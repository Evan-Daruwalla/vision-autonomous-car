"""SIM-POC P5 step 2: a probe from latent z to cross-track error.

CEM planning needs to SCORE an imagined future, but the world model predicts
the next latent z, not "how far from the centre line am I". This probe closes
that gap: z -> cte, trained on the corpus, where every frame already carries
the simulator's own `log_cte` as a label.

**Why this is legitimate and not cheating.** The probe is trained offline on
recorded data, exactly like V and M. At planning time it never sees the
simulator's cte -- it reads only the latent the world model imagined. If the
probe cannot recover cte from z, that is itself a finding: it would mean the
encoder discarded the one quantity the task depends on, and no planner built
on those latents could work.

**Both architectures are kept, and the GAP between them is the finding.**
Measured 2026-08-07: linear R^2 = 0.27, MLP R^2 = 0.97. The latent carries
lane position almost perfectly, but NONLINEARLY. That single comparison
explains why the paper-faithful linear controller cannot lane-follow here, and
it is why the planner uses the MLP probe: scoring imagined latents through the
linear one would be optimising a proxy that explains a quarter of the target.

Usage:  python ml/train_cte_probe.py              # mlp (used by the planner)
        python ml/train_cte_probe.py --arch linear
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from episode_writer import load_episode
from models import Z_DIM
from splits import (fit_val_episodes, load_cached_mu, load_proc,
                    split_seed_of)

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "ml" / "data" / "sim" / "train"
PROC = REPO / "ml" / "data" / "proc"
RUNS = REPO / "ml" / "runs"


def build_cte_array() -> np.ndarray:
    """Concatenate log_cte across episodes in preprocess.py's exact order.

    Order matters: the result is indexed by the same flat frame index as
    train_mu.npy, so it MUST use the same `sorted(glob)` the preprocessor used.
    """
    cached = PROC / "train_cte.npy"
    if cached.exists():
        return np.load(cached)
    files = sorted(SRC.glob("*.npz"))
    out = []
    for f in files:
        ep = load_episode(f)
        out.append(np.asarray(ep["log_cte"], np.float32))
        del ep
    cte = np.concatenate(out)
    np.save(cached, cte)
    print(f"built {cached.name}: {len(cte):,} frames")
    return cte


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=1e-2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--arch", choices=("linear", "mlp"), default="mlp")
    ap.add_argument("--width", type=int, default=256)
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--out", default=str(RUNS / "cte_probe"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    _, _, eps, tracks = load_proc("train")
    vae_ckpt = torch.load(args.vae, map_location=args.device)
    # Cold audit finding 1: don't silently reuse a latent cache from a
    # retrained VAE. This script has no encoder loaded to re-encode with, so
    # a stale/missing cache is a hard stop, not a silent reuse.
    mu = load_cached_mu("train", args.vae, proc=PROC)
    if mu is None:
        raise SystemExit(
            f"ml/data/proc/train_mu.npy is missing or was encoded by a "
            f"different VAE checkpoint than {args.vae} -- run "
            f"train_mdnrnn.py first to refresh the cache.")
    cte = build_cte_array()
    if len(cte) != len(mu):
        raise SystemExit(f"cte has {len(cte)} frames, mu has {len(mu)} - "
                         f"the episode ordering does not match preprocess.py")

    # Cold audit finding 2: the split seed comes from the VAE checkpoint that
    # produced these latents, never a hardcoded default -- see
    # rollout_eval.py's split_seed comment for why.
    split_seed = split_seed_of(vae_ckpt)
    fit_eps, val_eps = fit_val_episodes(tracks, seed=split_seed)
    fit_i = np.concatenate([np.arange(s, s + n) for s, n in eps[fit_eps]])
    val_i = np.concatenate([np.arange(s, s + n) for s, n in eps[val_eps]])

    if args.arch == "linear":
        model = nn.Linear(Z_DIM, 1).to(args.device)
    else:
        model = nn.Sequential(
            nn.Linear(Z_DIM, args.width), nn.ReLU(inplace=True),
            nn.Linear(args.width, args.width), nn.ReLU(inplace=True),
            nn.Linear(args.width, 1)).to(args.device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)

    zf = torch.from_numpy(mu[fit_i]).to(args.device)
    cf = torch.from_numpy(cte[fit_i]).to(args.device).unsqueeze(-1)
    zv = torch.from_numpy(mu[val_i]).to(args.device)
    cv = torch.from_numpy(cte[val_i]).to(args.device).unsqueeze(-1)

    steps = max(1, len(fit_i) // args.batch)
    for epoch in range(1, args.epochs + 1):
        for _ in range(steps):
            sel = torch.from_numpy(
                rng.choice(len(fit_i), size=args.batch, replace=False)).to(args.device)
            loss = ((model(zf[sel]) - cf[sel]) ** 2).mean()
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
        if epoch % 10 == 0 or epoch == 1:
            with torch.no_grad():
                vp = model(zv)
                mse = float(((vp - cv) ** 2).mean())
                ss_res = float(((vp - cv) ** 2).sum())
                ss_tot = float(((cv - cv.mean()) ** 2).sum())
                print(f"  epoch {epoch:3d}  val MSE {mse:.4f}  R^2 {1 - ss_res/ss_tot:.4f}")

    with torch.no_grad():
        vp = model(zv)
        mse = float(((vp - cv) ** 2).mean())
        ss_res = float(((vp - cv) ** 2).sum())
        ss_tot = float(((cv - cv.mean()) ** 2).sum())
        r2 = 1 - ss_res / ss_tot
    torch.save({"model": model.state_dict(), "val_mse": mse, "val_r2": r2,
                "arch": args.arch, "width": args.width,
                "args": vars(args)}, out / f"cte_probe_{args.arch}.pt")
    (out / f"probe_{args.arch}.json").write_text(json.dumps(
        {"val_mse": mse, "val_r2": r2, "args": vars(args)}, indent=2))
    print(f"\n{args.arch} z->cte probe: val MSE {mse:.4f}, R^2 {r2:.4f}")
    print(f"-> {out / f'cte_probe_{args.arch}.pt'}")
    # A planner scoring imagined latents through a probe this weak would be
    # optimising noise, so say so loudly rather than letting CEM fail opaquely.
    if r2 < 0.5:
        print("WARNING: R^2 below 0.5 - z carries little lane information and "
              "CEM planning on these latents is unlikely to work.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
