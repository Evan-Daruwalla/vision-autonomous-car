"""Does recovery data actually fix the perception wall? (tests Appendix W.1)

W.1 measured that perception degrades as a function of how far off-centre the
car is -- probe error ~0.20 while |cte| < 1.0, ~2.1 past 1.5 -- and attributed
it to coverage: the corpus contains no off-centre frames because the collector
rejects `mean|cte| > 1.2`. `collect_recovery.py` now supplies those frames.
This measures whether they help, and decomposes WHERE the fix has to happen.

THE DECOMPOSITION, which is the point of running it this way. "Perception" is
two things, and they fail for different reasons and cost different amounts to
fix:

  A. the LATENT. Does the frozen ConvVAE's z even CONTAIN lane position for an
     off-centre frame? The VAE trained on centred data only.
  B. the READOUT. Does the probe know how to decode it? The probe also trained
     on centred data only.

So three probes are trained against the SAME frozen encoder and evaluated on
the SAME held-out frames:

  baseline   probe trained on ORIGINAL (centred) frames only  <- today's state
  augmented  probe trained on original + recovery frames
  and the gap between them isolates (B) from (A).

**If `augmented` fixes the high-|cte| buckets, the latent was fine all along
and only the readout was starved** -- a cheap fix that needs no VAE retrain.
**If it does not, the encoder itself is discarding off-centre information**
and the VAE must be retrained (or replaced), which is the expensive branch.
Either answer is worth having before committing M3's data-collection plan.

Both probes are evaluated on held-out episodes drawn from BOTH corpora, so the
evaluation set actually contains the off-centre states in question. Scoring a
centred-only probe on centred-only data is how this bug survived in the first
place.

Prerequisites:
  python ml/collect_recovery.py --episodes 20 --max-steps 600
  python ml/preprocess.py --extra-src ml/data/sim_recovery/train \\
                          --out ml/data/proc_aug

Usage:
  python ml/exp_recovery.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from episode_writer import load_episode
from models import Z_DIM, ConvVAE
from provenance import write_result
from splits import load_proc

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "ml" / "data" / "sim" / "train"
REC = REPO / "ml" / "data" / "sim_recovery" / "train"
RUNS = REPO / "ml" / "runs"
BUCKETS = [(0.0, 0.3), (0.3, 0.6), (0.6, 1.0), (1.0, 1.5), (1.5, 99.0)]


def build_cte(proc: Path) -> np.ndarray:
    """log_cte for the augmented corpus, in preprocess.py's episode order.

    Order is originals (sorted) then recovery (sorted) -- the exact order
    `process_split` uses when `--extra-src` is given. Any mismatch here
    silently pairs a frame with another frame's label, so the length check
    below is not decoration.
    """
    cached = proc / "train_cte.npy"
    if cached.exists():
        return np.load(cached)
    out = []
    for f in sorted(SRC.glob("*.npz")) + sorted(REC.glob("*.npz")):
        ep = load_episode(f)
        out.append(np.asarray(ep["log_cte"], np.float32))
        del ep
    cte = np.concatenate(out)
    np.save(cached, cte)
    return cte


@torch.no_grad()
def encode_all(vae, imgs, device, batch=512):
    mu = np.zeros((len(imgs), Z_DIM), np.float32)
    for s in range(0, len(imgs), batch):
        e = min(s + batch, len(imgs))
        x = torch.from_numpy(np.array(imgs[s:e])).to(device)
        x = x.permute(0, 3, 1, 2).float().div_(255.0)
        mu[s:e] = vae.encode(x)[0].cpu().numpy()
    return mu


def train_probe(z, c, device, epochs=40, batch=4096, width=256, seed=0):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    m = nn.Sequential(nn.Linear(Z_DIM, width), nn.ReLU(inplace=True),
                      nn.Linear(width, width), nn.ReLU(inplace=True),
                      nn.Linear(width, 1)).to(device)
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    zt = torch.from_numpy(z).to(device)
    ct = torch.from_numpy(c).to(device).unsqueeze(-1)
    for _ in range(epochs):
        for _ in range(max(1, len(z) // batch)):
            sel = torch.from_numpy(
                rng.choice(len(z), min(batch, len(z)), replace=False)).to(device)
            loss = ((m(zt[sel]) - ct[sel]) ** 2).mean()
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
    m.eval()
    return m


@torch.no_grad()
def bucket_err(m, z, c, device):
    p = m(torch.from_numpy(z).to(device)).squeeze(-1).cpu().numpy()
    err = np.abs(p - c)
    rows = []
    for lo, hi in BUCKETS:
        k = (np.abs(c) >= lo) & (np.abs(c) < hi)
        rows.append((lo, hi, int(k.sum()),
                     float(err[k].mean()) if k.any() else float("nan")))
    return rows, float(err.mean())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proc", default=str(REPO / "ml" / "data" / "proc_aug"))
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--out", default=str(RUNS / "exp_recovery"))
    ap.add_argument("--val-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    proc = Path(args.proc)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if not (proc / "train_images.npy").exists():
        raise SystemExit(f"no augmented corpus at {proc}. Run:\n"
                         f"  python ml/preprocess.py --extra-src {REC} "
                         f"--out {proc}")

    imgs, _, eps, tracks = load_proc("train", proc=proc)
    cte = build_cte(proc)
    if len(cte) != len(imgs):
        raise SystemExit(f"cte has {len(cte)} frames, images have {len(imgs)} "
                         f"- episode ordering does not match preprocess.py")

    is_rec = np.array([t.endswith("-rec") for t in tracks])
    print(f"corpus: {len(eps)} episodes ({int(is_rec.sum())} recovery), "
          f"{len(imgs):,} frames")

    rng = np.random.default_rng(args.seed)
    # Hold out whole EPISODES from both corpora, so the eval set contains real
    # off-centre states and no frame leaks between train and eval.
    val_eps = []
    for grp in (np.flatnonzero(~is_rec), np.flatnonzero(is_rec)):
        k = max(1, int(round(len(grp) * args.val_frac)))
        val_eps.extend(rng.permutation(grp)[:k].tolist())
    val_eps = np.array(sorted(val_eps))
    fit_eps = np.array([i for i in range(len(eps)) if i not in set(val_eps.tolist())])

    def frames(sel):
        return np.concatenate([np.arange(s, s + n) for s, n in eps[sel]])

    fit_orig = frames(np.array([i for i in fit_eps if not is_rec[i]]))
    fit_aug = frames(fit_eps)
    val_i = frames(val_eps)
    print(f"  fit baseline  {len(fit_orig):,} frames (original only)")
    print(f"  fit augmented {len(fit_aug):,} frames (+{len(fit_aug)-len(fit_orig):,} recovery)")
    print(f"  eval          {len(val_i):,} frames, "
          f"{100*np.mean(np.abs(cte[val_i])>1.0):.1f}% off-centre\n")

    vae = ConvVAE().to(args.device)
    vae.load_state_dict(torch.load(args.vae, map_location=args.device)["model"])
    vae.eval()
    print("encoding with the FROZEN original VAE ...")
    mu = encode_all(vae, imgs, args.device)

    results = {}
    for name, sel in (("baseline", fit_orig), ("augmented", fit_aug)):
        m = train_probe(mu[sel], cte[sel], args.device, seed=args.seed)
        rows, overall = bucket_err(m, mu[val_i], cte[val_i], args.device)
        results[name] = {"overall": overall,
                         "buckets": [{"lo": lo, "hi": hi, "n": n, "err": e}
                                     for lo, hi, n, e in rows]}

    print(f"{'|cte| bucket':<16}{'n':>7}{'baseline':>11}{'augmented':>11}{'change':>10}")
    for base, aug in zip(results["baseline"]["buckets"],
                         results["augmented"]["buckets"]):
        if base["n"] == 0:
            continue
        b, a = base["err"], aug["err"]
        chg = "" if not np.isfinite(b) or b == 0 else f"{100*(a-b)/b:+.0f}%"
        print(f"  {base['lo']:.1f} - {base['hi']:<9.1f}{base['n']:>7}"
              f"{b:>11.3f}{a:>11.3f}{chg:>10}")
    print(f"  {'OVERALL':<14}{len(val_i):>7}"
          f"{results['baseline']['overall']:>11.3f}"
          f"{results['augmented']['overall']:>11.3f}")

    # The verdict rides on the OFF-CENTRE buckets, not the overall mean: the
    # eval set is still mostly centred frames, so an overall average would be
    # dominated by the region that already worked.
    hi_b = [x["err"] for x in results["baseline"]["buckets"]
            if x["lo"] >= 1.0 and x["n"] > 0]
    hi_a = [x["err"] for x in results["augmented"]["buckets"]
            if x["lo"] >= 1.0 and x["n"] > 0]
    print()
    if hi_b and hi_a:
        b, a = float(np.mean(hi_b)), float(np.mean(hi_a))
        results["off_centre_mean"] = {"baseline": b, "augmented": a}
        print(f"off-centre (|cte| >= 1.0): {b:.3f} -> {a:.3f}  "
              f"({100*(a-b)/b:+.0f}%)")
        if a < b * 0.7:
            print("VERDICT: recovery data FIXES the readout. The frozen VAE's "
                  "latent already contained off-centre lane position; the probe "
                  "was simply never trained on it. No VAE retrain needed.")
        elif a < b * 0.95:
            print("VERDICT: recovery data helps the readout but does not close "
                  "the gap. Part of the loss is in the ENCODER - retraining the "
                  "VAE on the augmented corpus is the next test.")
        else:
            print("VERDICT: recovery data does NOT fix the readout against a "
                  "frozen encoder. The ConvVAE itself discards off-centre "
                  "information, so the fix is a VAE retrain (or a different "
                  "representation), not more probe data.")
    write_result(out / "exp_recovery.json", 
        {"args": vars(args), "n_recovery_episodes": int(is_rec.sum()),
         "results": results})
    print(f"\n-> {out / 'exp_recovery.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
