"""SIM-POC P3 step 2: train the MDN-RNN (M) on VAE latents.

Learns p(z_{t+1} | z_t, a_t, h_t) as a mixture of Gaussians -- the dynamics
half of the world model.

Two things this script is careful about:

**Latents are cached, and cached as (mu, logvar) rather than as sampled z.**
Encoding 91k frames every epoch would dominate runtime, but caching a single
sampled z would freeze one draw from the posterior and hand the RNN a
falsely-deterministic world. Caching the distribution lets a fresh z be
sampled each epoch, which is what the paper does and what stops the RNN
memorising encoder noise.

**Sequences never straddle an episode boundary.** A window spanning the join
between two episodes contains a transition that never physically happened --
a teleport. The model would dutifully learn it.

Usage:
  python ml/train_mdnrnn.py                # 60 epochs, seq 64
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from models import MDNRNN, ConvVAE, count_params, mdn_loss
from splits import (cache_key_matches, encoder_fingerprint,
                    fit_val_episodes, load_proc, write_cache_key)

REPO = Path(__file__).resolve().parent.parent
PROC = REPO / "ml" / "data" / "proc"
RUNS = REPO / "ml" / "runs"


@torch.no_grad()
def encode_split(split: str, vae: ConvVAE, device: str, batch: int = 512,
                 vae_ckpt: Path | None = None):
    """Cache (mu, logvar) for every frame. Recomputed if missing OR STALE.

    **Staleness is what this guards.** Keyed on the split name alone, retraining
    the VAE with any different --epochs/--beta/--seed silently reused latents
    from the PREVIOUS encoder: the MDN-RNN would learn dynamics in one latent
    space while rollout_eval.py decoded them through another, with nothing
    anywhere reporting a mismatch. The filename stays stable (rollout_eval.py
    loads the same path) and a `.key` sidecar carries the encoder fingerprint.
    (Cold audit finding 5, 2026-08-06.)
    """
    mu_path = PROC / f"{split}_mu.npy"
    lv_path = PROC / f"{split}_logvar.npy"
    want = encoder_fingerprint(vae_ckpt)
    if mu_path.exists() and lv_path.exists() and cache_key_matches(split, want):
        return np.load(mu_path), np.load(lv_path)
    if mu_path.exists() and not cache_key_matches(split, want):
        print(f"  {split}: cached latents are from a different VAE checkpoint "
              f"- re-encoding")

    imgs, _, _, _ = load_proc(split)
    n = len(imgs)
    mus = np.zeros((n, vae.z_dim), np.float32)
    lvs = np.zeros((n, vae.z_dim), np.float32)
    vae.eval()
    for s in range(0, n, batch):
        e = min(s + batch, n)
        # np.array() (not ascontiguousarray) so the memmap slice is copied into
        # a writable buffer -- torch warns and gives undefined behaviour on
        # read-only arrays
        x = torch.from_numpy(np.array(imgs[s:e])).to(device)
        x = x.permute(0, 3, 1, 2).float().div_(255.0)
        mu, lv = vae.encode(x)
        mus[s:e] = mu.cpu().numpy()
        lvs[s:e] = lv.cpu().numpy()
    np.save(mu_path, mus)
    np.save(lv_path, lvs)
    # Stamp WHICH encoder produced these, so a later run cannot silently
    # reuse them under a different VAE (cold audit finding 5).
    write_cache_key(split, want)
    print(f"  encoded {split}: {n:,} frames -> {mu_path.name}")
    return mus, lvs


def make_windows(episodes: np.ndarray, ep_idx: np.ndarray, seq: int) -> np.ndarray:
    """Start offsets for every valid window, clipped to episode boundaries.

    A window needs seq+1 frames: seq inputs and the target z_{t+1} for the
    last one.
    """
    starts = []
    for s, n in episodes[ep_idx]:
        if n >= seq + 1:
            starts.append(np.arange(s, s + n - seq))
    if not starts:
        raise SystemExit(f"no episode is longer than seq+1={seq+1} frames")
    return np.concatenate(starts)


def batch_from(starts, mus, lvs, actions, seq, device, rng, sample=True):
    """Assemble (z_in, a_in, z_target) for a batch of window starts."""
    idx = starts[:, None] + np.arange(seq + 1)[None, :]      # (B, seq+1)
    mu = torch.from_numpy(mus[idx]).to(device)
    if sample:
        lv = torch.from_numpy(lvs[idx]).to(device)
        z = mu + torch.exp(0.5 * lv) * torch.randn_like(mu)
    else:
        z = mu
    a = torch.from_numpy(actions[idx]).to(device)
    return z[:, :-1], a[:, :-1], z[:, 1:]


@torch.no_grad()
def evaluate(model, starts, mus, lvs, actions, seq, device, batch, rng,
             n_windows: int = 4096):
    model.eval()
    sel = rng.choice(starts, size=min(n_windows, len(starts)), replace=False)
    total, n = 0.0, 0
    for s in range(0, len(sel), batch):
        chunk = np.sort(sel[s:s + batch])
        # eval on the posterior mean: a fixed target makes epochs comparable
        z_in, a_in, z_tgt = batch_from(chunk, mus, lvs, actions, seq, device,
                                       rng, sample=False)
        logpi, mu, ls, _ = model(z_in, a_in)
        total += float(mdn_loss(logpi, mu, ls, z_tgt)) * len(chunk)
        n += len(chunk)
    model.train()
    return total / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--seq", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--out", default=str(RUNS / "mdnrnn"))
    ap.add_argument("--steps-per-epoch", type=int, default=300)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    rng = np.random.default_rng(args.seed)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    vae = ConvVAE().to(args.device)
    vae.load_state_dict(torch.load(args.vae, map_location=args.device)["model"])
    print(f"VAE loaded from {args.vae}")

    print("encoding latents (cached after the first run)...")
    tr_mu, tr_lv = encode_split("train", vae, args.device, vae_ckpt=args.vae)
    ho_mu, ho_lv = encode_split("holdout", vae, args.device, vae_ckpt=args.vae)

    _, tr_act, tr_eps, tr_tracks = load_proc("train")
    _, ho_act, ho_eps, _ = load_proc("holdout")
    fit_eps, val_eps = fit_val_episodes(tr_tracks, seed=args.seed)

    fit_w = make_windows(tr_eps, fit_eps, args.seq)
    val_w = make_windows(tr_eps, val_eps, args.seq)
    ho_w = make_windows(ho_eps, np.arange(len(ho_eps)), args.seq)
    print(f"windows: fit {len(fit_w):,}  val_indomain {len(val_w):,}  "
          f"holdout {len(ho_w):,}  (seq={args.seq})")

    model = MDNRNN().to(args.device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    print(f"model  : {count_params(model):,} params on {args.device}\n")

    history, best = [], float("inf")
    for epoch in range(1, args.epochs + 1):
        t0, run = time.time(), 0.0
        for _ in range(args.steps_per_epoch):
            sel = np.sort(rng.choice(fit_w, size=args.batch, replace=False))
            z_in, a_in, z_tgt = batch_from(sel, tr_mu, tr_lv, tr_act,
                                           args.seq, args.device, rng)
            logpi, mu, ls, _ = model(z_in, a_in)
            loss = mdn_loss(logpi, mu, ls, z_tgt)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            run += loss.item()

        tr_nll = run / args.steps_per_epoch
        va_nll = evaluate(model, val_w, tr_mu, tr_lv, tr_act, args.seq,
                          args.device, args.batch, np.random.default_rng(args.seed + 1))
        ho_nll = evaluate(model, ho_w, ho_mu, ho_lv, ho_act, args.seq,
                          args.device, args.batch, np.random.default_rng(args.seed + 1))
        dt = time.time() - t0
        print(f"epoch {epoch:3d}/{args.epochs}  fit nll {tr_nll:9.2f}  |  "
              f"val_indomain {va_nll:9.2f}  |  holdout {ho_nll:9.2f}   ({dt:.0f}s)")
        history.append({"epoch": epoch, "fit_nll": tr_nll,
                        "val_indomain_nll": va_nll, "holdout_nll": ho_nll,
                        "seconds": round(dt, 1)})

        if va_nll < best:
            best = va_nll
            torch.save({"model": model.state_dict(), "epoch": epoch,
                        "val_indomain_nll": va_nll, "args": vars(args)},
                       out / "mdnrnn_best.pt")

    (out / "history.json").write_text(json.dumps(history, indent=2))
    print(f"\nbest val_indomain nll: {best:.2f}  ({out / 'mdnrnn_best.pt'})")


if __name__ == "__main__":
    main()
