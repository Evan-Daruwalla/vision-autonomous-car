"""Does an auxiliary detection head make the encoder KEEP small objects?

The M4 showcase (PRD 6(b)) needs a stop sign to reach the latent. W.2 measured
that it does not: 0 of 899 cone pixels survive either encoder's reconstruction.
Evan chose the auxiliary-head mitigation on 2026-08-10. `probe_cone.py` then
measured that the frozen ConvVAE's latent does NOT contain the object either --
a probe hit AUC 0.997, but painting the cone out moved its score by 1% of the
pos/neg gap, so it was reading track position. So the aux loss has to reshape
the ENCODER, and this trains one to find out whether that works.

**WHY A SYNTHETIC OBJECT AND NOT THE REAL CONES.** This is the whole design.
Real cones sit at fixed track locations, so "is a cone visible" is almost
perfectly predicted by "where am I" -- which is exactly how the probe scored
0.997 while being blind. Train an aux head against that target and the encoder
can satisfy it from position alone, the aux loss goes to zero, and the metric
turns green while the car stays blind. Any result on the real cones would be
uninterpretable in the same way.

So the object is INJECTED: a small high-contrast square, present in ~50% of
frames at a uniformly random position, drawn from a seed derived from the frame
index. Presence and position are independent of the track by construction, so
the encoder cannot cheat, and the un-injected frame is an EXACT counterfactual
for the ablation control (no inpainting needed).

Frames containing real cones are dropped, so the detector only ever sees the
injected object.

Two ConvVAEs, identical seed, identical data, identical budget:
  plain  standard VAE loss                     -- the W.2 baseline, reproduced
  aux    + aux_weight * BCE(Linear(mu) -> 8x8 occupancy grid)

A LINEAR aux head on purpose: if a linear map off `mu` can place the object,
`mu` genuinely encodes it, and no capacity is hiding in the head.

Three measurements on held-out episodes:
  survival    object-coloured pixels kept in the reconstruction (the W.2 metric)
  probe AUC   + the paint-out ablation, the check probe_cone.py failed
  val rec     what the aux loss COSTS in ordinary pixel fidelity

Usage:
  python ml/exp_aux_head.py
  python ml/exp_aux_head.py --epochs 10 --aux-weight 5.0
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from compare_encoders import cone_mask
from models import Z_DIM, ConvVAE, vae_loss
from probe_cone import auc, scan_cones
from splits import fit_val_episodes, frame_indices, load_proc

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"

GRID = 8                  # aux target is an 8x8 occupancy grid over the frame
OBJ_RGB = (235, 96, 40)   # fires cone_mask: r=235>120, r-g=139>80
OBJ_MIN, OBJ_MAX = 4, 7   # side length px -> 16..49 px, matching real cones
Y_LO, Y_HI = 16, 52       # keep it on the road/horizon band, off the edges
X_LO, X_HI = 3, 61


def injection_plan(n: int, seed: int):
    """Per-frame object: (present, x, y, size). Independent of frame content."""
    rng = np.random.default_rng(seed)
    present = rng.random(n) < 0.5
    size = rng.integers(OBJ_MIN, OBJ_MAX + 1, n)
    x = rng.integers(X_LO, X_HI - OBJ_MAX, n)
    y = rng.integers(Y_LO, Y_HI - OBJ_MAX, n)
    return present, x.astype(np.int32), y.astype(np.int32), size.astype(np.int32)


def inject(batch: np.ndarray, plan, idx: np.ndarray):
    """Paste the planned object into a copy of `batch`; return (imgs, masks)."""
    present, px, py, ps = plan
    out = np.array(batch, copy=True)
    masks = np.zeros(out.shape[:3], bool)
    for j, i in enumerate(idx):
        if not present[i]:
            continue
        x, y, s = int(px[i]), int(py[i]), int(ps[i])
        out[j, y:y + s, x:x + s] = OBJ_RGB
        masks[j, y:y + s, x:x + s] = True
    return out, masks


def grid_target(masks: np.ndarray) -> np.ndarray:
    """(B,64,64) bool -> (B,GRID*GRID) float: 1 where the cell holds object."""
    b = masks.shape[0]
    c = 64 // GRID
    return masks.reshape(b, GRID, c, GRID, c).any(axis=(2, 4)).reshape(b, -1).astype(np.float32)


def to_tensor(batch: np.ndarray, device: str) -> torch.Tensor:
    t = torch.from_numpy(np.ascontiguousarray(batch)).to(device)
    return t.permute(0, 3, 1, 2).float().div_(255.0)


def train_one(tag, use_aux, imgs, fit_i, val_i, plan, args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    rng = np.random.default_rng(args.seed)

    model = ConvVAE().to(args.device)
    head = nn.Linear(Z_DIM, GRID * GRID).to(args.device)
    params = list(model.parameters()) + (list(head.parameters()) if use_aux else [])
    opt = torch.optim.Adam(params, lr=args.lr)
    # The grid is ~97% empty; without pos_weight the head predicts all-zero and
    # no gradient about the object ever reaches the encoder.
    auxf = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([30.0], device=args.device))

    steps = len(fit_i) // args.batch
    hist = []
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        perm = rng.permutation(fit_i)
        run_rec = run_aux = 0.0
        for i in range(steps):
            sel = np.sort(perm[i * args.batch:(i + 1) * args.batch])
            raw, masks = inject(imgs[sel], plan, sel)
            x = to_tensor(raw, args.device)
            recon, mu, logvar = model(x)
            loss, rec, _ = vae_loss(recon, x, mu, logvar, beta=args.beta)
            if use_aux:
                tgt = torch.from_numpy(grid_target(masks)).to(args.device)
                a = auxf(head(mu), tgt)
                loss = loss + args.aux_weight * a
                run_aux += float(a)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            run_rec += float(rec)
        va = eval_rec(model, imgs, val_i, plan, args)
        hist.append({"epoch": epoch, "fit_rec": run_rec / steps,
                     "aux": run_aux / steps, "val_rec": va,
                     "seconds": round(time.time() - t0, 1)})
        if epoch % 5 == 0 or epoch == args.epochs:
            print(f"  [{tag}] epoch {epoch:3d}/{args.epochs}  fit rec "
                  f"{run_rec/steps:7.2f}  aux {run_aux/max(1,steps):6.4f}  "
                  f"val rec {va:7.2f}  ({time.time()-t0:.0f}s)")
    model.eval()
    head.eval()
    return model, head, hist


@torch.no_grad()
def eval_rec(model, imgs, val_i, plan, args, n=4096):
    model.eval()
    idx = np.sort(val_i[np.linspace(0, len(val_i) - 1, min(n, len(val_i))).astype(int)])
    tot, cnt = 0.0, 0
    for s in range(0, len(idx), args.batch):
        sel = idx[s:s + args.batch]
        raw, _ = inject(imgs[sel], plan, sel)
        x = to_tensor(raw, args.device)
        recon, mu, logvar = model(x)
        _, rec, _ = vae_loss(recon, x, mu, logvar)
        tot += float(rec) * len(sel)
        cnt += len(sel)
    model.train()
    return tot / cnt


@torch.no_grad()
def encode_injected(model, imgs, idx, plan, args, injected=True):
    """Encode frames WITH (or deliberately WITHOUT) the planned object."""
    mu = np.zeros((len(idx), Z_DIM), np.float32)
    for s in range(0, len(idx), args.batch):
        sel = idx[s:s + args.batch]
        raw = inject(imgs[sel], plan, sel)[0] if injected else np.array(imgs[sel])
        mu[s:s + len(sel)] = model.encode(to_tensor(raw, args.device))[0].cpu().numpy()
    return mu


@torch.no_grad()
def survival(model, imgs, idx, plan, args):
    """Object-coloured pixels kept in the reconstruction (the W.2 metric)."""
    kept = true = 0
    obj_hit = obj_n = 0
    for s in range(0, len(idx), args.batch):
        sel = idx[s:s + args.batch]
        raw, masks = inject(imgs[sel], plan, sel)
        recon, _, _ = model(to_tensor(raw, args.device))
        rec_u8 = (recon.permute(0, 2, 3, 1).clamp(0, 1).cpu().numpy() * 255).astype(np.uint8)
        det = np.stack([cone_mask(im) for im in rec_u8])
        kept += int((det & masks).sum())
        true += int(masks.sum())
        for j in range(len(sel)):
            if masks[j].any():
                obj_n += 1
                obj_hit += int((det[j] & masks[j]).any())
    return {"px_kept": kept, "px_true": true, "px_survival": kept / max(1, true),
            "objects": obj_n, "objects_detected": obj_hit,
            "object_survival": obj_hit / max(1, obj_n)}


def train_probe(z, y, device, epochs=60, batch=4096, seed=0):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    m = nn.Sequential(nn.Linear(Z_DIM, 256), nn.ReLU(inplace=True),
                      nn.Linear(256, 256), nn.ReLU(inplace=True),
                      nn.Linear(256, 1)).to(device)
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    zt = torch.from_numpy(z).to(device)
    yt = torch.from_numpy(y.astype(np.float32)).to(device).unsqueeze(-1)
    pw = torch.tensor([(len(y) - y.sum()) / max(1.0, y.sum())], device=device)
    lossf = nn.BCEWithLogitsLoss(pos_weight=pw)
    for _ in range(epochs):
        for _ in range(max(1, len(z) // batch)):
            sel = torch.from_numpy(rng.choice(len(z), min(batch, len(z)),
                                              replace=False)).to(device)
            loss = lossf(m(zt[sel]), yt[sel])
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
    m.eval()
    return m


@torch.no_grad()
def pscore(m, z, device):
    return torch.sigmoid(m(torch.from_numpy(z).to(device))).squeeze(-1).cpu().numpy()


def self_check() -> int:
    """Prove the injection pipeline does what the experiment claims.

    Every conclusion here rests on three things being true: the object is
    really in the frame, the aux target really describes it, and the
    un-injected frame is really a clean counterfactual. None of that is
    visible in the result table, so it is asserted instead.
    """
    plan = injection_plan(50, 7)
    present, _, _, ps = plan
    base = np.zeros((6, 64, 64, 3), np.uint8)
    base[:] = (60, 110, 60)                      # flat non-object background
    idx = np.arange(6)
    imgs, masks = inject(base, plan, idx)

    for j, i in enumerate(idx):
        want = int(ps[i]) ** 2 if present[i] else 0
        assert masks[j].sum() == want, f"frame {j}: mask {masks[j].sum()} != {want}"
        # the survival metric detects by COLOUR, so the detector must agree
        # with the injected mask exactly or survival measures the wrong pixels
        assert (cone_mask(imgs[j]) == masks[j]).all(), f"frame {j}: detector != mask"
    assert cone_mask(base[0]).sum() == 0, "background trips the detector"

    g = grid_target(masks).reshape(-1, GRID, GRID)
    for j, i in enumerate(idx):
        if not present[i]:
            assert g[j].sum() == 0, f"frame {j}: grid marks an absent object"
            continue
        ys, xs = np.where(masks[j])
        want = np.zeros((GRID, GRID))
        want[ys.min() // 8:ys.max() // 8 + 1, xs.min() // 8:xs.max() // 8 + 1] = 1
        assert (g[j] == want).all(), f"frame {j}: grid does not match the object"

    assert (inject(base, plan, idx)[0] == imgs).all(), "injection is not deterministic"
    assert (inject(base, injection_plan(50, 7), idx)[1] == masks).all(), \
        "same seed gives a different plan"

    # The decorrelation IS the experiment (Appendix Y.2): a fixed-position
    # object would be predictable from track position and prove nothing.
    p = injection_plan(4000, 7)
    xs, ys = p[1][p[0]], p[2][p[0]]
    assert xs.std() > 10 and ys.std() > 5, \
        f"object position is not spread (std {xs.std():.1f}, {ys.std():.1f})"
    print(f"self-check PASSED (x std {xs.std():.1f}, y std {ys.std():.1f}, "
          f"{100*p[0].mean():.0f}% of frames carry the object)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-check", action="store_true",
                    help="assert the injection pipeline is correct, then exit")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--beta", type=float, default=1.0)
    # Swept, not guessed. At weight 10 the aux term is ~4% of total loss, so a
    # null result there cannot tell "the idea fails" from "the knob was too
    # small". The sweep makes a negative result mean something.
    ap.add_argument("--aux-weights", default="10,100,1000",
                    help="comma-separated aux loss weights to train")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=str(RUNS / "exp_aux_head"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    if args.self_check:
        return self_check()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    imgs, _, eps, tracks = load_proc("train")
    fit_eps, val_eps = fit_val_episodes(tracks, seed=args.seed)
    fit_i, val_i = frame_indices(eps, fit_eps), frame_indices(eps, val_eps)

    print(f"dropping frames that contain REAL cones (they would leak track "
          f"position into the label) ...")
    real = scan_cones(imgs) > 0
    fit_i = fit_i[~real[fit_i]]
    val_i = val_i[~real[val_i]]
    print(f"  dropped {int(real.sum()):,} of {len(imgs):,} frames "
          f"({100*real.mean():.1f}%)")

    plan = injection_plan(len(imgs), args.seed + 77)
    print(f"injected object: {OBJ_MIN}-{OBJ_MAX}px square, RGB {OBJ_RGB}, "
          f"present in {100*plan[0].mean():.0f}% of frames, uniform position")
    print(f"fit {len(fit_i):,} frames, val {len(val_i):,} frames\n")

    weights = [float(w) for w in args.aux_weights.split(",")]
    arms = [("plain", 0.0)] + [(f"aux{w:g}", w) for w in weights]

    results = {}
    for tag, w in arms:
        use_aux = w > 0
        args.aux_weight = w
        print(f"training [{tag}] "
              f"({'VAE loss + ' + str(w) + '*aux' if use_aux else 'VAE loss only'}) ...")
        model, _, hist = train_one(tag, use_aux, imgs, fit_i, val_i, plan, args)

        surv = survival(model, imgs, val_i[:4096], plan, args)
        mu_fit = encode_injected(model, imgs, fit_i[:40000], plan, args)
        mu_val = encode_injected(model, imgs, val_i, plan, args)
        mu_abl = encode_injected(model, imgs, val_i, plan, args, injected=False)
        y_fit = plan[0][fit_i[:40000]]
        y_val = plan[0][val_i]

        probe = train_probe(mu_fit, y_fit, args.device, seed=args.seed)
        a = auc(pscore(probe, mu_val, args.device), y_val)
        s_pos = float(pscore(probe, mu_val[y_val], args.device).mean())
        s_abl = float(pscore(probe, mu_abl[y_val], args.device).mean())
        s_neg = float(pscore(probe, mu_val[~y_val], args.device).mean())
        span = s_pos - s_neg
        drop = (s_pos - s_abl) / span if abs(span) > 1e-6 else float("nan")

        results[tag] = {"val_rec": hist[-1]["val_rec"], "survival": surv,
                        "auc": a, "score_pos": s_pos, "score_ablated": s_abl,
                        "score_neg": s_neg, "ablation_gap_recovered": drop,
                        "history": hist}
        torch.save({"model": model.state_dict(), "args": vars(args)},
                   out / f"vae_{tag}.pt")
        print(f"  [{tag}] val rec {hist[-1]['val_rec']:.2f}  "
              f"object survival {surv['object_survival']:.1%}  "
              f"AUC {a:.3f}  ablation {100*drop:.0f}%\n")

    tags = [t for t, _ in arms]
    print(f"\n{'':<26}" + "".join(f"{t:>12}" for t in tags))
    print(f"{'val rec loss':<26}"
          + "".join(f"{results[t]['val_rec']:>12.2f}" for t in tags))
    print(f"{'object survival':<26}"
          + "".join(f"{results[t]['survival']['object_survival']:>11.1%}" for t in tags))
    print(f"{'pixel survival':<26}"
          + "".join(f"{results[t]['survival']['px_survival']:>11.1%}" for t in tags))
    print(f"{'probe AUC':<26}"
          + "".join(f"{results[t]['auc']:>12.3f}" for t in tags))
    print(f"{'ablation gap recovered':<26}"
          + "".join(f"{100*results[t]['ablation_gap_recovered']:>11.0f}%" for t in tags))

    p = results["plain"]
    # Best aux arm = highest AUC among those whose ablation control passes. An
    # arm with a high AUC and a failed ablation is the probe_cone.py failure
    # mode and must never be selected as the winner.
    # AUC saturates at 1.000 once the aux loss bites, so "highest AUC" is a
    # coin flip between arms. Tie-break on the CHEAPEST sufficient
    # intervention: the lowest weight within 0.005 AUC of the best, because
    # weight buys latent content at the cost of reconstruction quality
    # (measured: aux1000 gets 79.4% object survival for +6.8% val rec loss,
    # while aux100 already reaches AUC 1.000 for +0.0%).
    clean = [(t, w) for t, w in arms[1:]
             if results[t]["ablation_gap_recovered"] >= 0.5]
    if clean:
        top = max(results[t]["auc"] for t, _ in clean)
        best = min((tw for tw in clean if results[tw[0]]["auc"] >= top - 0.005),
                   key=lambda tw: tw[1])[0]
    else:
        best = arms[1][0]
    x = results[best]
    print(f"\nbest aux arm: {best}")

    # The aux head's job is to put the object in `mu`. The ablation gate is what
    # separates that from the position-reading failure probe_cone.py exposed:
    # a high AUC whose score does not move when the object is removed is not
    # evidence of anything.
    print()
    ok = x["auc"] >= 0.80 and x["ablation_gap_recovered"] >= 0.5
    base = p["auc"] >= 0.80 and p["ablation_gap_recovered"] >= 0.5
    if ok and not base:
        verdict = (f"AUX HEAD WORKS. With the aux loss the latent carries the "
                   f"object (AUC {x['auc']:.3f}, ablation "
                   f"{100*x['ablation_gap_recovered']:.0f}%) and without it it "
                   f"does not (AUC {p['auc']:.3f}, ablation "
                   f"{100*p['ablation_gap_recovered']:.0f}%). Cost: val rec "
                   f"{p['val_rec']:.2f} -> {x['val_rec']:.2f}. The M4 "
                   f"mitigation is a VAE retrain with this head, and it is "
                   f"validated in sim.")
    elif ok and base:
        verdict = (f"BOTH latents carry the object (aux AUC {x['auc']:.3f}, "
                   f"plain {p['auc']:.3f}, both ablation-clean). The plain VAE "
                   f"encodes an object it does not RECONSTRUCT, so W.2's "
                   f"reconstruction test understated the encoder. The aux head "
                   f"is then optional, not required.")
    else:
        verdict = (f"AUX HEAD DOES NOT FIX IT (AUC {x['auc']:.3f}, ablation "
                   f"{100*x['ablation_gap_recovered']:.0f}%). A z={Z_DIM} "
                   f"bottleneck trained mostly for reconstruction does not "
                   f"retain a <1%-of-frame object even under direct "
                   f"supervision. Escalate: larger z, higher input resolution, "
                   f"or a detection path that bypasses the latent.")
    print(f"VERDICT: {verdict}")

    (out / "exp_aux_head.json").write_text(json.dumps(
        {"args": vars(args), "n_fit": len(fit_i), "n_val": len(val_i),
         "arms": tags, "best_aux_arm": best,
         "results": results, "verdict": verdict}, indent=2))
    print(f"-> {out / 'exp_aux_head.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
