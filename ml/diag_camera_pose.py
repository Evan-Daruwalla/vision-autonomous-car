"""What HEIGHT, PITCH and OFFSET was the corpus captured at?

`diag_camera_fov.py` identified the sim's unrecorded FOV as 90 by sweeping
explicit values until one reproduced the default frame. **That trick does not
extend to the extrinsics**, and the reason is in gym_donkeycar's own docstring
for `send_cam_config`:

    set any field to Zero to get the default camera setting

FOV was identifiable because its default (90) is non-zero, so an explicit
sweep could hit it. For `offset_x/y/z` and `rot_x/y/z`, **0.0 means "use the
default"** -- asking whether `offset_y=0` reproduces the default is a
tautology, not a measurement. The fov=90 run sent all six extrinsic keys as
0.0, so it deliberately held the extrinsics at their defaults and learned
nothing about them.

So the extrinsics are measured GEOMETRICALLY instead, off frames already on
disk. Two things are identifiable and one is not:

  PITCH -- from the horizon row. For a camera pitched DOWN by theta the
    ground plane's vanishing line lands at row  cy - f*tan(theta), so
    theta = atan((cy - r_h) / f). Needs f, hence needs to know whether the
    sim's `fov` is vertical or horizontal. Measured VERTICAL (Appendix AR),
    so f = 60 px on a 120x160 frame.

  HEIGHT -- from the projection of a ground feature at known lateral offset.
    For a ground point at lateral X, u - cx = (X*cos(theta)/h)*(v - v_h), in
    which f CANCELS. Regressing the yellow centre line's column on the logged
    `cte` therefore gives h/cos(theta) in metres with no FOV assumption at all.
    **This is NOT yet working -- see LIMITATIONS.**

  offset_z (forward) -- NOT identifiable from a ground plane at all. Sliding
    the camera forward along its own axis leaves every ground-plane image
    relation unchanged; it is absorbed into the definition of `cte`.

LIMITATIONS (measured, not guessed; record Appendix AR)
  * The height regression fails on the corpus as collected. Three causes, all
    confirmed: the yellow line runs off the LEFT EDGE at close rows, censoring
    exactly the rows carrying the most signal; `cte` spans only +-0.17 m on the
    main corpus, so the lateral signal is tiny; and the PID couples heading
    error to `cte`, so the regression slope is not a pure lateral response.
  * `donkey-generated-track-v0` is tree-lined and has no clean sky boundary,
    so only `donkey-generated-roads-v0` (open desert, flat) yields a horizon.
  * `offset_x` is not separable from the road's own geometry using one line:
    the yellow line's lateral position is (track-reference offset) - cte, and
    only the sum is observable.

Usage:
  python ml/diag_camera_pose.py                 # horizon/pitch from the corpus
  python ml/diag_camera_pose.py --self-check    # runnable check, no data needed
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
SIM = REPO / "ml" / "data" / "sim"
RUNS = REPO / "ml" / "runs"

SKY_MIN_BLUE_EXCESS = 25.0   # B - R above this counts a pixel as sky
IMG_H, IMG_W = 120, 160


def horizon_rows(imgs: np.ndarray) -> np.ndarray:
    """Sub-pixel sky/ground boundary row per frame; NaN where undecidable.

    Scans down for the first row that is NOT predominantly sky, and interpolates
    the 50%-sky crossing. **Content, not gradient.** The obvious alternative --
    steepest vertical gradient of blue-minus-red -- locks onto the pink stripe
    on `donkey-avc-sparkfun-v0` and returns a "horizon" BELOW a ground stripe,
    which is geometrically impossible. That failure was deterministic, so it
    repeated to 0.000 px across launches and read as confirmation. Repeatability
    bounds noise, never correctness (Appendix AR).
    """
    f = np.asarray(imgs, dtype=np.float32)
    frac = ((f[..., 2] - f[..., 0]) > SKY_MIN_BLUE_EXCESS).mean(axis=2)
    out = np.full(len(f), np.nan, np.float64)
    for i, fr in enumerate(frac):
        below = np.where(fr < 0.5)[0]
        if len(below) == 0 or below[0] == 0:
            continue                      # all sky, or no sky at all
        r = int(below[0])
        f0, f1 = fr[r - 1], fr[r]
        t = (f0 - 0.5) / (f0 - f1) if f0 != f1 else 0.0
        out[i] = (r - 1) + float(np.clip(t, 0.0, 1.0))
    return out


def pitch_deg(horizon_row: float, height_px: int = IMG_H,
              width_px: int = IMG_W, fov_deg: float = 90.0,
              fov_is_vertical: bool = True) -> float:
    """Downward pitch, in degrees, from the horizon's row."""
    cy = (height_px - 1) / 2.0
    half = height_px / 2.0 if fov_is_vertical else width_px / 2.0
    f = half / np.tan(np.radians(fov_deg / 2.0))
    return float(np.degrees(np.arctan((cy - horizon_row) / f)))


def pink_stripe_row(img: np.ndarray) -> float:
    """Centroid row of the saturated pink ground stripe on `sparkfun_avc`.

    The second, independent vertical reference in the aspect test: the ratio of
    (stripe row - horizon row) between two image heights measures the vertical
    scale without relying on the horizon's absolute position.
    """
    f = np.asarray(img, np.float32)
    prof = (f[..., 0] - f[..., 1]).mean(axis=1)
    i = int(np.argmax(prof))
    lo, hi = max(0, i - 6), min(len(prof), i + 7)
    w = np.clip(prof[lo:hi] - prof[lo:hi].min(), 0, None)
    return float((np.arange(lo, hi) * w).sum() / max(w.sum(), 1e-9))


def aspect_ratios(run_dir: Path):
    """Recompute the fov-convention test from the frames saved by the run.

    Exists because the run's original JSON was written by the DEBUNKED gradient
    detector and reports an offset ratio of 0.0867 -- a number AR.3 explains as
    a detector failure, not a measurement. An artifact that contradicts the
    entry citing it will mislead the next reader, so the numbers are derived
    from the frames on demand rather than trusted from the file.
    """
    out = {}
    for tag in ("a_160x120", "b_160x160", "c_160x120_rep"):
        p = run_dir / f"{tag}.npy"
        if not p.exists():
            raise SystemExit(f"missing aspect frame {p}")
        img = np.load(p)
        h = float(horizon_rows(img[None])[0])
        cy = (img.shape[0] - 1) / 2.0
        out[tag] = {"shape": list(img.shape), "cy": cy, "horizon_row": h,
                    "offset_above_centre_px": cy - h,
                    "pink_stripe_row": pink_stripe_row(img)}
    a, b, c = out["a_160x120"], out["b_160x160"], out["c_160x120_rep"]
    sep_a = a["pink_stripe_row"] - a["horizon_row"]
    sep_b = b["pink_stripe_row"] - b["horizon_row"]
    res = {
        "frames": out,
        "repeatability_px": abs(a["offset_above_centre_px"]
                                - c["offset_above_centre_px"]),
        "offset_ratio_b_over_a": b["offset_above_centre_px"] / a["offset_above_centre_px"],
        "stripe_separation_ratio_b_over_a": sep_b / sep_a,
        "predicted_if_fov_vertical": 160 / 120,
        "predicted_if_fov_horizontal": 1.0,
        "note": ("Recomputed with the CONTENT-based horizon detector. The "
                 "original file was written by the gradient detector, which "
                 "locked onto sparkfun_avc's pink ground stripe and gave "
                 "0.0867 -- see Appendix AR.3."),
    }
    r = res["offset_ratio_b_over_a"]
    res["verdict"] = ("VERTICAL" if abs(r - 160 / 120) < abs(r - 1.0)
                      else "HORIZONTAL")
    return res


def corpus_horizon(track_prefix: str = "generated-roads", stride: int = 10):
    from episode_writer import load_episode
    rows = []
    for p in sorted((SIM / "train").iterdir()):
        if p.name.startswith(track_prefix):
            rows.append(horizon_rows(load_episode(p)["image"][::stride]))
    if not rows:
        raise SystemExit(f"no episodes matching {track_prefix!r} under {SIM / 'train'}")
    r = np.concatenate(rows)
    return r[np.isfinite(r)]


def self_check() -> None:
    """Synthetic frames with a KNOWN horizon: does the detector recover it?"""
    for true_r in (20, 41, 73):
        img = np.zeros((IMG_H, IMG_W, 3), np.uint8)
        img[:true_r] = (40, 90, 200)          # sky: strong blue excess
        img[true_r:] = (160, 140, 120)        # ground: red excess
        got = horizon_rows(img[None])[0]
        assert abs(got - (true_r - 0.5)) <= 1.0, (true_r, got)
    # a frame with no sky at all is undecidable, not silently zero
    assert np.isnan(horizon_rows(np.full((1, IMG_H, IMG_W, 3), 130, np.uint8))[0])
    # a bright ground stripe must NOT be mistaken for the horizon: put a
    # saturated red band BELOW the true boundary, the sparkfun failure mode.
    img = np.zeros((IMG_H, IMG_W, 3), np.uint8)
    img[:41] = (40, 90, 200)
    img[41:] = (160, 140, 120)
    img[70:78] = (255, 60, 60)
    assert abs(horizon_rows(img[None])[0] - 40.5) <= 1.0, horizon_rows(img[None])[0]
    # the pink-stripe reference finds a band it is given, and is what makes
    # the aspect test's SECOND ratio checkable rather than prose (AU finding 3)
    img = np.zeros((IMG_H, IMG_W, 3), np.uint8)
    img[:41] = (40, 90, 200)
    img[41:] = (160, 140, 120)
    img[70:78] = (255, 60, 60)
    assert abs(pink_stripe_row(img) - 73.5) <= 1.5, pink_stripe_row(img)

    # geometry: horizon above centre => pitched DOWN => positive
    assert pitch_deg(41.974) > 0
    assert abs(pitch_deg(59.5)) < 1e-9, "horizon at centre must be zero pitch"
    # f = 60 px vertical vs 80 px horizontal at 90 deg on a 120x160 frame
    assert abs(pitch_deg(41.974) - np.degrees(np.arctan(17.526 / 60))) < 1e-6
    assert abs(pitch_deg(41.974, fov_is_vertical=False)
               - np.degrees(np.arctan(17.526 / 80))) < 1e-6
    print("diag_camera_pose self_check: PASS")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", default="generated-roads",
                    help="episode-name prefix. Only donkey-generated-roads-v0 "
                         "has a clean sky boundary; generated-track is "
                         "tree-lined and yields nothing usable")
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--recompute-aspect", action="store_true",
                    help="rewrite ml/runs/camera_aspect/camera_aspect.json from "
                         "the saved frames using the content horizon detector")
    ap.add_argument("--out", default=str(RUNS / "camera_pose"))
    args = ap.parse_args()

    if args.self_check:
        self_check()
        return 0

    if args.recompute_aspect:
        run = RUNS / "camera_aspect"
        res = aspect_ratios(run)
        for tag, f in res["frames"].items():
            print(f"{tag:16s} H={f['shape'][0]:3d}  horizon {f['horizon_row']:7.3f}  "
                  f"pink {f['pink_stripe_row']:7.3f}  offset "
                  f"{f['offset_above_centre_px']:7.3f}")
        print()
        print(f"repeatability            {res['repeatability_px']:.3f} px")
        print(f"offset ratio b/a         {res['offset_ratio_b_over_a']:.4f}")
        print(f"stripe separation ratio  {res['stripe_separation_ratio_b_over_a']:.4f}")
        print(f"  predicted VERTICAL     {res['predicted_if_fov_vertical']:.4f}")
        print(f"  predicted HORIZONTAL   {res['predicted_if_fov_horizontal']:.4f}")
        print(f"VERDICT: fov is {res['verdict']}")
        (run / "camera_aspect.json").write_text(json.dumps(res, indent=2),
                                                encoding="utf-8")
        print(f"-> {run / 'camera_aspect.json'}")
        return 0

    r = corpus_horizon(args.track, args.stride)
    med = float(np.median(r))
    cy = (IMG_H - 1) / 2.0
    res = {
        "track_prefix": args.track, "n_frames": int(len(r)),
        "horizon_row_median": med, "horizon_row_sd": float(r.std()),
        "horizon_row_iqr": [float(np.percentile(r, 25)), float(np.percentile(r, 75))],
        "cy": cy, "offset_above_centre_px": cy - med,
        "pitch_deg_if_fov_vertical": pitch_deg(med),
        "pitch_deg_if_fov_horizontal": pitch_deg(med, fov_is_vertical=False),
    }
    print(f"{args.track}: n={len(r):,}  horizon row {med:.3f} "
          f"(sd {r.std():.3f}, IQR {res['horizon_row_iqr'][0]:.2f}-"
          f"{res['horizon_row_iqr'][1]:.2f})")
    print(f"  cy - r_h = {cy - med:.3f} px")
    print(f"  pitch DOWN = {res['pitch_deg_if_fov_vertical']:.2f} deg "
          f"(fov vertical, f=60 px -- the measured convention)")
    print(f"  pitch DOWN = {res['pitch_deg_if_fov_horizontal']:.2f} deg "
          f"(fov horizontal, f=80 px -- ruled out, kept for the record)")
    print("\nHEIGHT and offset_x are NOT identified. See the module docstring.")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "camera_pose.json").write_text(json.dumps(res, indent=2))
    print(f"-> {out / 'camera_pose.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
