"""Does DreamerV3's RSSM keep the small objects the ConvVAE throws away?

Record Appendix V.2 flagged this as a live risk to the M4 plan. Two extraction
agents, working on different artifacts without seeing each other, both found
that the ConvVAE's reconstructions DROP orange traffic cones entirely -- and
since every downstream stage consumes only the latent, anything built on that
encoder is blind to small high-contrast objects. The PRD makes a STOP SIGN the
M4 world-model showcase. A stop sign is exactly such an object.

The open question was whether DreamerV3 shares the defect. It plausibly does
not: its RSSM carries a far larger latent (dyn_deter 512 plus a 32x32 discrete
stochastic state, against the ConvVAE's z=32 continuous), so there is more room
to encode detail that contributes little to pixel loss.

**This measures it instead of arguing it.** Cone pixels are detected by colour
in the ORIGINAL frame, and reconstruction error is reported separately for
cone pixels and everything else, for both models on the same frames. The ratio
(cone error / background error) is the number that matters: a model that
reconstructs the road well and the cone badly has a high ratio, and that is
precisely the failure mode.

Reporting per-pixel error rather than a whole-image score is the point. Cones
occupy well under 1% of the frame, so an image-level MSE is dominated by road
and sky and would show nothing.

Usage:
  python ml/compare_encoders.py
  python ml/compare_encoders.py --n-frames 24 --out ml/runs/encoder_cmp
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from pathlib import Path

import numpy as np
import torch

from models import ConvVAE
from splits import fit_val_episodes, load_proc

REPO = Path(__file__).resolve().parent.parent
PROC = REPO / "ml" / "data" / "proc"
RUNS = REPO / "ml" / "runs"
VENDOR = REPO / "ml" / "vendor" / "dreamerv3-torch"


def cone_mask(img: np.ndarray) -> np.ndarray:
    """Orange-cone pixels in a (H,W,3) uint8 frame.

    **Thresholds derived from the data and checked by eye, not guessed.** A
    first attempt at `(r-g) > 40` fired on 62% of frames with mean masked
    colour [209,164,85] -- that is the tan dirt road, not a cone, and it would
    have measured road fidelity while claiming to measure cone fidelity.
    Percentiles of (R-G) across held-out frames put the 99.9th at 62 and the
    99.99th at 95, so `> 80` sits in the genuine tail: masked pixels average
    [169,78,73] and appear in ~3.6% of frames. Rendering those frames beside
    their masks confirmed the mask lands on the cone body and excludes both
    the yellow centre line (where R ~= G) and the road.
    """
    r, g = img[..., 0].astype(int), img[..., 1].astype(int)
    return (r > 120) & ((r - g) > 80)


def load_dreamer_wm(ckpt_path: Path, device: str):
    """Rebuild the vendored WorldModel and load the P4 checkpoint into it."""
    if not VENDOR.exists():
        raise SystemExit(f"vendored dreamerv3-torch missing at {VENDOR}")
    import argparse as _ap
    import importlib.util

    import gym  # noqa: F401

    # **Name collision, and it is not cosmetic.** This project has its OWN
    # ml/models.py, already imported above and therefore cached in
    # sys.modules['models']. A plain `import models` after adding the vendor
    # directory to sys.path returns OUR module, and the failure surfaces as a
    # baffling `module 'models' has no attribute 'WorldModel'`. Load the
    # vendored file by explicit path, register it as 'models' so the vendor's
    # own internal `import models` resolves to itself, then put ours back.
    sys.path.insert(0, str(VENDOR))
    ours = sys.modules.pop("models", None)
    try:
        spec = importlib.util.spec_from_file_location("models", VENDOR / "models.py")
        dv3_models = importlib.util.module_from_spec(spec)
        sys.modules["models"] = dv3_models
        spec.loader.exec_module(dv3_models)
    finally:
        if ours is not None:
            sys.modules["models"] = ours

    ck = torch.load(ckpt_path, map_location=device)
    config = _ap.Namespace(**ck["config"])
    obs_space = gym.spaces.Dict({
        "image": gym.spaces.Box(0, 255, (64, 64, 3), dtype=np.uint8),
        "is_first": gym.spaces.Box(0, 1, (), dtype=bool),
        "is_terminal": gym.spaces.Box(0, 1, (), dtype=bool),
    })
    act_space = gym.spaces.Box(-1.0, 1.0, (config.num_actions,), dtype=np.float32)
    wm = dv3_models.WorldModel(obs_space, act_space, 0, config).to(device)
    wm.load_state_dict(ck["wm"])
    wm.eval()
    return wm, config


@torch.no_grad()
def dreamer_reconstruct(wm, imgs: np.ndarray, acts: np.ndarray, device: str):
    """(T,64,64,3) uint8 -> reconstructed (T,64,64,3) float in [0,1]."""
    T = len(imgs)
    data = {
        "image": torch.from_numpy(imgs).to(device).unsqueeze(0).float(),
        "action": torch.from_numpy(acts).to(device).unsqueeze(0).float(),
        "is_first": torch.zeros(1, T, device=device),
        "is_terminal": torch.zeros(1, T, device=device),
    }
    data["is_first"][0, 0] = 1.0
    data = wm.preprocess(data)
    embed = wm.encoder(data)
    post, _ = wm.dynamics.observe(embed, data["action"], data["is_first"])
    feat = wm.dynamics.get_feat(post)
    recon = wm.heads["decoder"](feat)["image"].mode().squeeze(0)
    # **No +0.5 here, and that is deliberate.** Upstream DreamerV3 preprocesses
    # images to [-0.5, 0.5] and its ConvDecoder ends with `mean += 0.5`, so the
    # instinct is to undo an offset. But THIS repo's preprocess does
    # `obs["image"] / 255.0` (models.py:182), i.e. targets are [0, 1], and the
    # decoder's +0.5 is therefore just a bias init that lands it in the SAME
    # [0,1] space. Adding another 0.5 would brighten every reconstruction and
    # manufacture a "DreamerV3 is worse" result out of a units error.
    lo, hi = float(recon.min()), float(recon.max())
    if not (-0.2 < lo < 1.2 and -0.2 < hi < 1.2):
        print(f"WARNING: decoder output range [{lo:.2f}, {hi:.2f}] is not [0,1] "
              f"- the scaling assumption above may be wrong for this "
              f"checkpoint; do not trust the comparison.")
    return recon.clamp(0, 1).cpu().numpy()


@torch.no_grad()
def vae_reconstruct(vae, imgs: np.ndarray, device: str):
    x = torch.from_numpy(imgs).to(device).permute(0, 3, 1, 2).float().div_(255.0)
    recon, _, _ = vae(x)
    return recon.permute(0, 2, 3, 1).clamp(0, 1).cpu().numpy()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-frames", type=int, default=32)
    ap.add_argument("--min-cone-px", type=int, default=12,
                    help="a frame must have at least this many cone pixels")
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--dreamer",
                    default=str(RUNS / "dreamer_p4" / "S_b16_saved" / "world_model.pt"))
    ap.add_argument("--out", default=str(RUNS / "encoder_cmp"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    imgs_all, acts_all, eps, tracks = load_proc("train")
    _, val_eps = fit_val_episodes(tracks, seed=0)
    # Held-out episodes only: reconstructing training frames would flatter both
    # models and say nothing about what either one generalises.
    pool = np.concatenate([np.arange(s, s + n) for s, n in eps[val_eps]])

    print(f"scanning {len(pool):,} held-out frames for cones...")
    picked = []
    for i in pool:
        m = cone_mask(imgs_all[i])
        if m.sum() >= args.min_cone_px:
            picked.append((int(i), int(m.sum())))
        if len(picked) >= args.n_frames:
            break
    if not picked:
        print(f"FAIL: no held-out frame has >= {args.min_cone_px} cone pixels. "
              f"Either the detector is wrong or this split has no cones - "
              f"check before concluding anything about either encoder.")
        return 1
    idx = np.array([i for i, _ in picked])
    print(f"  {len(idx)} frames, {np.mean([c for _, c in picked]):.0f} cone px each "
          f"({100*np.mean([c for _,c in picked])/(64*64):.2f}% of frame)")

    imgs = np.ascontiguousarray(imgs_all[idx])
    acts = np.ascontiguousarray(acts_all[idx])

    vae = ConvVAE().to(args.device)
    vae.load_state_dict(torch.load(args.vae, map_location=args.device)["model"])
    vae.eval()
    rec_vae = vae_reconstruct(vae, imgs, args.device)

    dreamer_path = Path(args.dreamer)
    if not dreamer_path.exists():
        print(f"FAIL: no DreamerV3 checkpoint at {dreamer_path}. Run "
              f"`python ml/run_dreamer_p4.py --tag S_b16_saved` first.")
        return 1
    wm, _ = load_dreamer_wm(dreamer_path, args.device)
    rec_dv3 = dreamer_reconstruct(wm, imgs, acts, args.device)

    truth = imgs.astype(np.float32) / 255.0
    masks = np.stack([cone_mask(im) for im in imgs])

    # **`survival` is the decisive column, not `ratio`.** A ratio can improve
    # because the numerator fell OR because the denominator rose, and a model
    # that reconstructs the background worse scores a better ratio while
    # erasing the object just as completely. Measured 2026-08-09: DreamerV3's
    # ratio beat the ConvVAE's 3.12x to 4.38x purely because its background
    # error was 28% worse -- both erased the cone outright, which the rendered
    # panel showed at a glance and the ratio hid. So: re-run the SAME colour
    # detector on the RECONSTRUCTION. If the cone is there, some cone-coloured
    # pixels survive; if it is erased, the count is ~0 regardless of MSE.
    n_true = int(masks.sum())
    print(f"\n{'model':<12}{'cone err':>10}{'bg err':>10}{'ratio':>9}{'cone px kept':>14}")
    summary = {}
    for name, rec in (("ConvVAE", rec_vae), ("DreamerV3", rec_dv3)):
        err = np.abs(rec - truth).mean(axis=-1)          # (T,64,64) per-pixel
        cone = float(err[masks].mean())
        bg = float(err[~masks].mean())
        rec_u8 = (rec * 255).astype(np.uint8)
        kept = int(np.stack([cone_mask(im) for im in rec_u8]).sum())
        summary[name] = {"cone_err": cone, "bg_err": bg, "ratio": cone / bg,
                         "cone_px_in_recon": kept, "cone_px_in_truth": n_true,
                         "survival": kept / max(1, n_true)}
        print(f"{name:<12}{cone:>10.4f}{bg:>10.4f}{cone/bg:>9.2f}x"
              f"{kept:>8}/{n_true:<5}")

    print()
    print("ratio    = per-pixel error on cones / error elsewhere (direction only)")
    print("cone px kept = cone-coloured pixels surviving in the reconstruction")
    print()
    # Survival gates the verdict. Ratio only breaks ties among models that
    # actually keep the object.
    s_vae = summary["ConvVAE"]["survival"]
    s_dv3 = summary["DreamerV3"]["survival"]
    ERASED = 0.05          # under 5% of cone pixels surviving is "erased"
    if s_vae < ERASED and s_dv3 < ERASED:
        print(f"VERDICT: BOTH encoders ERASE the cone (survival "
              f"{s_vae:.1%} and {s_dv3:.1%}). The blindness is NOT specific to "
              f"the ConvVAE, so a bigger/better-trained world model does not "
              f"fix it. **The M4 stop-sign showcase IS threatened** and needs a "
              f"different mitigation: higher input resolution, an auxiliary "
              f"detection/segmentation head, or a reward the object actually "
              f"moves. Note the ratio column would have implied otherwise -- a "
              f"model with worse BACKGROUND error scores a better ratio while "
              f"erasing the object just as completely.")
    elif s_dv3 > max(ERASED, s_vae * 2):
        print(f"VERDICT: DreamerV3 KEEPS the cone where the ConvVAE loses it "
              f"({s_dv3:.1%} vs {s_vae:.1%} survival). The M4 showcase is "
              f"viable on the RSSM but not on the ConvVAE.")
    else:
        print(f"VERDICT: comparable survival ({s_vae:.1%} vs {s_dv3:.1%}) - "
              f"switching encoder is not the mitigation.")

    # panel: original / VAE / DreamerV3, first 8 frames
    n = min(8, len(imgs))
    rows = [np.concatenate(list(truth[:n]), axis=1),
            np.concatenate(list(rec_vae[:n]), axis=1),
            np.concatenate(list(rec_dv3[:n]), axis=1)]
    panel = (np.concatenate(rows, axis=0) * 255).astype(np.uint8)
    try:
        from PIL import Image
        Image.fromarray(panel).resize((panel.shape[1] * 3, panel.shape[0] * 3),
                                      Image.NEAREST).save(out / "cone_recon.png")
        print(f"\npanel (rows: original / ConvVAE / DreamerV3) -> "
              f"{out / 'cone_recon.png'}")
    except Exception as e:
        print(f"panel not written: {e}")

    (out / "encoder_cmp.json").write_text(json.dumps(
        {"args": vars(args), "n_frames": len(idx),
         "mean_cone_px": float(np.mean([c for _, c in picked])),
         "summary": summary}, indent=2))
    print(f"-> {out / 'encoder_cmp.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
