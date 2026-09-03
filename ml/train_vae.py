"""SIM-POC P3 step 1: train the ConvVAE (V) on the sim corpus.

Reports THREE numbers every epoch, because they answer three questions:

  fit          episodes trained on
  val_indomain held-out EPISODES of the same tracks -- unseen trajectories,
               seen visual domain. "Did it learn, or memorise these runs?"
  holdout      an entirely unseen TRACK. "Does it transfer to a new layout?"

The third turned out to be a domain shift, not just a layout change (the
training tracks are outdoor, the holdout indoor), so it is reported as the
harder question it actually is rather than as the headline metric. See
splits.py.

Seeded end to end so a rerun reproduces: any claim made from this run has to
survive someone re-running it.

Usage:
  python ml/train_vae.py                 # defaults: 20 epochs, batch 256
  python ml/train_vae.py --epochs 5      # quick pass
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from models import ConvVAE, count_params, vae_loss
from provenance import write_result
from splits import describe, fit_val_episodes, frame_indices, load_proc

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"


def to_tensor(batch: np.ndarray, device: str) -> torch.Tensor:
    """(B,64,64,3) uint8 -> (B,3,64,64) float in [0,1]."""
    t = torch.from_numpy(np.ascontiguousarray(batch)).to(device)
    return t.permute(0, 3, 1, 2).float().div_(255.0)


@torch.no_grad()
def evaluate(model, imgs, pool, device, batch: int, rng: np.random.Generator,
             n_frames: int = 8192):
    """Mean per-frame reconstruction + KL over a fixed random subset of `pool`."""
    model.eval()
    idx = np.sort(rng.choice(pool, size=min(n_frames, len(pool)), replace=False))
    rec_sum, kl_sum, n = 0.0, 0.0, 0
    for s in range(0, len(idx), batch):
        sel = idx[s:s + batch]
        x = to_tensor(imgs[sel], device)
        recon, mu, logvar = model(x)
        _, rec, kl = vae_loss(recon, x, mu, logvar)
        rec_sum += float(rec) * len(sel)
        kl_sum += float(kl) * len(sel)
        n += len(sel)
    model.train()
    return rec_sum / n, kl_sum / n


@torch.no_grad()
def save_reconstructions(model, imgs, pool, device, path: Path, rng, n: int = 8):
    """Top row: real frames. Bottom row: the VAE's reconstruction."""
    model.eval()
    idx = np.sort(rng.choice(pool, size=n, replace=False))
    x = to_tensor(imgs[idx], device)
    mu, _ = model.encode(x)
    recon = model.decode(mu)          # mu, not a sample: this is a fidelity
                                      # check, not a generation demo
    grid = torch.cat([x, recon], dim=0).clamp(0, 1)
    grid = (grid.permute(0, 2, 3, 1).cpu().numpy() * 255).astype(np.uint8)
    rows = [np.concatenate(list(grid[i * n:(i + 1) * n]), axis=1) for i in range(2)]
    Image.fromarray(np.concatenate(rows, axis=0)).save(path)
    model.train()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--beta", type=float, default=1.0, help="KL weight")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=str(RUNS / "vae"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    rng = np.random.default_rng(args.seed)
    eval_rng_seed = args.seed + 1        # fixed eval subset across epochs

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    train_imgs, _, train_eps, train_tracks = load_proc("train")
    hold_imgs, _, hold_eps, hold_tracks = load_proc("holdout")

    fit_eps, val_eps = fit_val_episodes(train_tracks, seed=args.seed)
    fit_frames = frame_indices(train_eps, fit_eps)
    val_frames = frame_indices(train_eps, val_eps)
    hold_frames = np.arange(len(hold_imgs))

    print(describe(train_tracks, train_eps, fit_eps, val_eps))
    print(f"holdout      {len(hold_eps)} eps / {len(hold_imgs):,} frames "
          f"({sorted(set(hold_tracks.tolist()))[0]}) - UNSEEN TRACK *and* an "
          f"unseen visual domain")
    # Guard the thing the whole evaluation rests on.
    assert len(set(fit_frames) & set(val_frames)) == 0, "fit/val frames overlap"

    model = ConvVAE().to(args.device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    print(f"\nmodel  : {count_params(model):,} params on {args.device}\n")

    steps = len(fit_frames) // args.batch
    history = []
    best = float("inf")

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        perm = rng.permutation(fit_frames)
        run_rec, run_kl = 0.0, 0.0

        for i in range(steps):
            # sorted indices keep the memmap read mostly sequential
            sel = np.sort(perm[i * args.batch:(i + 1) * args.batch])
            x = to_tensor(train_imgs[sel], args.device)
            recon, mu, logvar = model(x)
            loss, rec, kl = vae_loss(recon, x, mu, logvar, beta=args.beta)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            run_rec += float(rec)
            run_kl += float(kl)

        tr_rec, tr_kl = run_rec / steps, run_kl / steps
        va_rec, va_kl = evaluate(model, train_imgs, val_frames, args.device,
                                 args.batch, np.random.default_rng(eval_rng_seed))
        ho_rec, ho_kl = evaluate(model, hold_imgs, hold_frames, args.device,
                                 args.batch, np.random.default_rng(eval_rng_seed))
        dt = time.time() - t0
        print(f"epoch {epoch:3d}/{args.epochs}  fit rec {tr_rec:7.2f}  |  "
              f"val_indomain rec {va_rec:7.2f} kl {va_kl:5.2f}  |  "
              f"holdout rec {ho_rec:7.2f}   ({dt:.0f}s)")

        history.append({"epoch": epoch, "fit_rec": tr_rec, "fit_kl": tr_kl,
                        "val_indomain_rec": va_rec, "val_indomain_kl": va_kl,
                        "holdout_rec": ho_rec, "holdout_kl": ho_kl,
                        "seconds": round(dt, 1)})

        # Select on val_indomain: it is the question P3 exists to answer
        # ("did it learn the dynamics"). Selecting on the cross-domain holdout
        # would be tuning against a distribution the model was never meant to
        # cover, and would pick an underfit model.
        if va_rec < best:
            best = va_rec
            torch.save({"model": model.state_dict(), "epoch": epoch,
                        "val_indomain_rec": va_rec, "holdout_rec": ho_rec,
                        "args": vars(args)}, out / "vae_best.pt")

    torch.save({"model": model.state_dict(), "epoch": args.epochs,
                "args": vars(args)}, out / "vae_last.pt")

    # reload the selected checkpoint so the saved images match the checkpoint
    model.load_state_dict(torch.load(out / "vae_best.pt")["model"])
    for tag, imgs, pool in (("fit", train_imgs, fit_frames),
                            ("val_indomain", train_imgs, val_frames),
                            ("holdout", hold_imgs, hold_frames)):
        save_reconstructions(model, imgs, pool, args.device,
                             out / f"recon_{tag}.png",
                             np.random.default_rng(eval_rng_seed))
    write_result(out / "history.json", {"args": vars(args), "history": history})

    print(f"\nbest val_indomain rec: {best:.2f}  ({out / 'vae_best.pt'})")
    print(f"reconstructions      : {out}/recon_{{fit,val_indomain,holdout}}.png")


if __name__ == "__main__":
    main()
