"""Is the small object IN the latent, or only missing from the reconstruction?

Appendix W.2 measured that **0 of 899 cone pixels survive** the ConvVAE's or
DreamerV3's reconstruction. That killed the assumption behind the M4 stop-sign
showcase and forced a decision (PRD 6(b)). Evan chose the auxiliary detection
head. This measures how expensive that head has to be.

**Erasing an object from the OUTPUT does not prove the encoder discarded it.**
Reconstruction loss is a mean over pixels, so a 28-pixel object contributes
~0.7% of the gradient: the decoder has almost no incentive to paint it even if
`mu` encodes it perfectly. Same latent-vs-readout split that `exp_recovery.py`
used for lane position, where the answer turned out to be the cheap one.

  probe works   -> the frozen latent already carries the object. The aux head
                   only has to READ it, so no VAE retrain: cheap.
  probe fails   -> the encoder genuinely throws it away. The aux loss has to
                   reshape the encoder, which means retraining the VAE: dear.

**THE CONFOUND, and why the ablation arm exists.** Cones sit at fixed track
locations. The latent demonstrably encodes track position (the cte probe
reaches R^2 0.957), so a probe could score a perfect AUC by learning "cones
live near here" while being completely blind to cone pixels. That would look
exactly like success and would be worthless.

So every positive frame is scored twice: as-is, and with the cone PAINTED OUT
and re-encoded. If the probe still cries cone on a frame with no cone in it,
it was reading position. If its score collapses toward the negatives, it is
reading the object. The ablation is the result; the AUC alone is not.

Labels are free: `cone_mask()` from compare_encoders.py, the colour detector
already validated in W.2 (thresholds derived from the R-G tail and confirmed
by rendering masks, after a first attempt measured the tan road instead).

Usage:
  python ml/probe_cone.py
  python ml/probe_cone.py --arch linear
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from compare_encoders import cone_mask
from models import Z_DIM, ConvVAE
from provenance import write_result
from splits import fit_val_episodes, load_proc, split_seed_of

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"
MIN_CONE_PX = 12          # same threshold compare_encoders.py used in W.2


def scan_cones(imgs, chunk: int = 4096):
    """Per-frame cone pixel count. Chunked: the full boolean mask over ~100k
    frames at 64x64 does not want to exist in memory all at once."""
    n = len(imgs)
    counts = np.zeros(n, np.int32)
    for s in range(0, n, chunk):
        e = min(s + chunk, n)
        block = np.array(imgs[s:e])
        r = block[..., 0].astype(np.int16)
        g = block[..., 1].astype(np.int16)
        counts[s:e] = ((r > 120) & ((r - g) > 80)).sum(axis=(1, 2))
    return counts


def paint_out(img: np.ndarray) -> np.ndarray:
    """Remove the cone from a frame by overwriting it with its surroundings.

    Per masked ROW, substitute the median colour of that row's UNmasked pixels.
    Row-wise rather than whole-frame because the background is strongly
    banded (sky above, road below); a single frame-wide median would paint a
    grey smear that is itself an anomaly, and the probe could then fire on the
    smear instead of on the cone -- which would confound the confound check.
    """
    out = img.copy()
    m = cone_mask(img)
    rows = np.flatnonzero(m.any(axis=1))
    for y in rows:
        keep = ~m[y]
        if keep.sum() < 4:                      # whole row masked: use frame
            fill = np.median(img[~m], axis=0)
        else:
            fill = np.median(img[y][keep], axis=0)
        out[y][m[y]] = fill.astype(np.uint8)
    return out


@torch.no_grad()
def encode(vae, imgs, device, batch=512):
    mu = np.zeros((len(imgs), Z_DIM), np.float32)
    for s in range(0, len(imgs), batch):
        e = min(s + batch, len(imgs))
        x = torch.from_numpy(np.ascontiguousarray(imgs[s:e])).to(device)
        x = x.permute(0, 3, 1, 2).float().div_(255.0)
        mu[s:e] = vae.encode(x)[0].cpu().numpy()
    return mu


def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """Mann-Whitney U / (n_pos * n_neg). Ties get average ranks."""
    pos, neg = int(labels.sum()), int((~labels.astype(bool)).sum())
    if pos == 0 or neg == 0:
        return float("nan")
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores), np.float64)
    ranks[order] = np.arange(1, len(scores) + 1)
    s = np.sort(scores)
    i = 0
    while i < len(s):                            # average ranks within ties
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = ranks[order[i:j + 1]].mean()
        i = j + 1
    return (ranks[labels.astype(bool)].sum() - pos * (pos + 1) / 2) / (pos * neg)


def train_probe(z, y, device, arch="mlp", epochs=60, batch=4096, seed=0):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    if arch == "linear":
        m = nn.Linear(Z_DIM, 1).to(device)
    else:
        m = nn.Sequential(nn.Linear(Z_DIM, 256), nn.ReLU(inplace=True),
                          nn.Linear(256, 256), nn.ReLU(inplace=True),
                          nn.Linear(256, 1)).to(device)
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    zt = torch.from_numpy(z).to(device)
    yt = torch.from_numpy(y.astype(np.float32)).to(device).unsqueeze(-1)
    # Cones are ~4% of frames. Without pos_weight the probe scores 96% by
    # always answering no, and the loss looks fine while it learns nothing.
    pw = torch.tensor([(len(y) - y.sum()) / max(1.0, y.sum())], device=device)
    lossf = nn.BCEWithLogitsLoss(pos_weight=pw)
    for _ in range(epochs):
        for _ in range(max(1, len(z) // batch)):
            sel = torch.from_numpy(
                rng.choice(len(z), min(batch, len(z)), replace=False)).to(device)
            loss = lossf(m(zt[sel]), yt[sel])
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
    m.eval()
    return m


@torch.no_grad()
def score(m, z, device):
    return torch.sigmoid(
        m(torch.from_numpy(z).to(device))).squeeze(-1).cpu().numpy()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--out", default=str(RUNS / "probe_cone"))
    ap.add_argument("--arch", default="mlp", choices=["linear", "mlp"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device",
                    default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    imgs, _, eps, tracks = load_proc("train")
    # Cold audit finding 2: the split seed comes from the VAE checkpoint,
    # never from --seed (which is the probe's own init/training seed) --
    # same rule as rollout_eval.py/train_controller.py.
    vae_ckpt = torch.load(args.vae, map_location=args.device)
    split_seed = split_seed_of(vae_ckpt)
    fit_eps, val_eps = fit_val_episodes(tracks, seed=split_seed)

    print(f"scanning {len(imgs):,} frames for cones ...")
    counts = scan_cones(imgs)
    y = (counts >= MIN_CONE_PX)
    print(f"  {y.sum():,} frames with >={MIN_CONE_PX} cone px "
          f"({100*y.mean():.2f}% of corpus), "
          f"mean {counts[y].mean():.0f} px when present")
    if y.sum() < 100:
        print("FAIL: too few cone frames to probe. Check the detector.")
        return 1

    def frames(sel):
        return np.concatenate([np.arange(s, s + n) for s, n in eps[sel]])

    fit_i, val_i = frames(fit_eps), frames(val_eps)
    print(f"  fit {len(fit_i):,} frames ({y[fit_i].sum():,} cone), "
          f"val {len(val_i):,} frames ({y[val_i].sum():,} cone)\n")

    vae = ConvVAE().to(args.device)
    vae.load_state_dict(vae_ckpt["model"])
    vae.eval()
    print("encoding with the FROZEN ConvVAE ...")
    mu = encode(vae, imgs, args.device)

    probe = train_probe(mu[fit_i], y[fit_i], args.device, arch=args.arch,
                        seed=args.seed)
    s_val = score(probe, mu[val_i], args.device)
    a = auc(s_val, y[val_i])

    # Permutation control: the same probe trained on SHUFFLED labels. Anything
    # the architecture can score from label frequency alone shows up here.
    rng = np.random.default_rng(args.seed + 1)
    y_shuf = y[fit_i].copy()
    rng.shuffle(y_shuf)
    ctrl = train_probe(mu[fit_i], y_shuf, args.device, arch=args.arch,
                       seed=args.seed)
    a_ctrl = auc(score(ctrl, mu[val_i], args.device), y[val_i])

    print(f"\nheld-out AUC (cone present):  {a:.3f}")
    print(f"  shuffled-label control:     {a_ctrl:.3f}   (chance = 0.500)")

    # ---- the ablation arm: is it reading the CONE or the LOCATION? ----
    pos_val = val_i[y[val_i]]
    neg_val = val_i[~y[val_i]]
    n_ab = min(400, len(pos_val))
    sel = pos_val[np.linspace(0, len(pos_val) - 1, n_ab).astype(int)]
    print(f"\npainting the cone out of {n_ab} held-out cone frames ...")
    painted = np.stack([paint_out(np.array(imgs[i])) for i in sel])
    left = int(np.stack([cone_mask(im) for im in painted]).sum())
    print(f"  cone px remaining after paint-out: {left} "
          f"(was {int(counts[sel].sum())})")
    mu_ab = encode(vae, painted, args.device)

    s_pos = float(score(probe, mu[sel], args.device).mean())
    s_ab = float(score(probe, mu_ab, args.device).mean())
    s_neg = float(score(probe, mu[neg_val], args.device).mean())
    print(f"\nmean probe score")
    print(f"  cone frames, as-is        {s_pos:.3f}")
    print(f"  same frames, cone erased  {s_ab:.3f}")
    print(f"  true no-cone frames       {s_neg:.3f}")

    # How far the ablated score falls from positive toward negative. 1.0 means
    # erasing the cone fully explains the probe's output; 0.0 means the cone
    # pixels were irrelevant and the probe was reading track position.
    span = s_pos - s_neg
    drop = (s_pos - s_ab) / span if abs(span) > 1e-6 else float("nan")
    print(f"  -> ablation recovers {100*drop:.0f}% of the pos/neg gap")

    print()
    GOOD_AUC, GOOD_DROP = 0.80, 0.5
    if a >= GOOD_AUC and drop >= GOOD_DROP:
        verdict = ("LATENT CARRIES THE OBJECT. The frozen ConvVAE encodes cone "
                   "presence (AUC {:.3f}) and the signal is genuinely the cone: "
                   "erasing its pixels collapses the probe. The reconstruction "
                   "drops it, the latent does not. **An auxiliary head only has "
                   "to READ mu -- no VAE retrain**, so the M4 mitigation is "
                   "cheap.").format(a)
    elif a >= GOOD_AUC:
        verdict = ("CONFOUNDED - DO NOT BUILD ON THIS. The probe scores AUC "
                   "{:.3f}, but painting the cone out barely moves it "
                   "({:.0f}% of the gap), so it is reading TRACK POSITION, not "
                   "the object. The latent has not been shown to contain the "
                   "cone. Treat this as the aux loss needing to reshape the "
                   "ENCODER.").format(a, 100 * drop)
    else:
        verdict = ("LATENT DISCARDS THE OBJECT (AUC {:.3f}). The encoder, not "
                   "just the decoder, throws small objects away. The auxiliary "
                   "head cannot be a read-only addition: the aux loss has to "
                   "train the ENCODER, which means retraining the VAE. That is "
                   "the expensive branch of PRD 6(b).").format(a)
    print(f"VERDICT: {verdict}")

    write_result(out / "probe_cone.json", 
        {"args": vars(args), "min_cone_px": MIN_CONE_PX,
         "n_cone_frames": int(y.sum()), "base_rate": float(y.mean()),
         "auc": a, "auc_shuffled_control": a_ctrl,
         "score_pos": s_pos, "score_ablated": s_ab, "score_neg": s_neg,
         "ablation_gap_recovered": drop, "n_ablated": n_ab,
         "cone_px_after_paint": left, "verdict": verdict})
    print(f"-> {out / 'probe_cone.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
