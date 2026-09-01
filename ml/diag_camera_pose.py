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
    ap.add_argument("--out", default=str(RUNS / "camera_pose"))
    args = ap.parse_args()

    if args.self_check:
        self_check()
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
