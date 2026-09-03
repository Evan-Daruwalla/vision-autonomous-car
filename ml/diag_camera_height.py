"""Camera HEIGHT in the sim, by a purpose-built lateral sweep.

Appendix AR.5 established the method and then failed to execute it on the
corpus as collected. The method is right and needs no FOV assumption: for a
camera at height h pitched down by theta, a ground point at lateral offset X
projects to

    u - cx = (X * cos(theta) / h) * (v - v_h)

in which the focal length CANCELS. The yellow centre line sits at X = C - cte
with `cte` logged per frame in metres, so regressing its column on cte at a
fixed row gives slope(v) = -(cos(theta)/h) * (v - v_h): the RATE at which that
slope grows with row yields h/cos(theta) in metres, and the zero crossing
yields the horizon independently.

WHY IT FAILED ON THE EXISTING CORPUS, AND WHAT THIS CHANGES

  1. `cte` spanned only +-0.17 m (sd 0.053) because the PID holds the car
     centred, so the lateral excitation was tiny.
     -> FIX: drive the PID against a SLOWLY-VARYING SETPOINT. `PIDDriver.act`
        takes the error, and its setpoint is implicitly zero, so passing
        `act(cte - target(t))` sweeps the car laterally with no change to the
        driver itself.

  2. The PID couples heading error to cte -- it steers FROM cte -- so the
     regression slope was not a pure lateral response.
     -> FIX: make the sweep SLOW (default 30 s per cycle at 20 Hz). A slowly
        tracked setpoint keeps heading error small while cte varies over a wide
        range, which is exactly the decoupling the fixed-setpoint corpus could
        not provide.

  3. The yellow line runs off the LEFT EDGE at close rows, and truncation
     compresses the measured centroid, flattening the slope at the rows that
     carry the most signal.
     -> FIX: reject any row whose line centroid sits within EDGE_REJECT px of
        either border, and require the mask to not touch the border at all.

Track is `donkey-generated-roads-v0`: flat open desert, unobstructed horizon,
one clean yellow centre line. `donkey-generated-track-v0` is tree-shadowed with
an occluded horizon and is NOT usable for this.

Usage:
  python ml/diag_camera_height.py --collect      # one sim launch
  python ml/diag_camera_height.py --fit          # regress what was collected
  python ml/diag_camera_height.py --self-check
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
from provenance import write_result

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"
OUT = RUNS / "camera_height"

ROWS = np.arange(64, 112)      # below the horizon (row ~42), above the bumper
EDGE_REJECT = 8                # px: a centroid this close to a border is censored
HORIZON_ROW = 41.974           # measured directly from the sky boundary,
                               # sd 0.284 px over 3,187 frames (Appendix AR)
MIN_MASK = 3                   # px of yellow needed to trust a row
SWEEP_AMPLITUDE = 0.60         # m of lateral offset either side          EST
SWEEP_PERIOD_S = 30.0          # s per full cycle -- SLOW, to decouple heading
CONTROL_HZ = 20.0              # matches SIM_TRANSFER_SPEC


def sweep_target(step: int, amplitude: float = SWEEP_AMPLITUDE,
                 period_s: float = SWEEP_PERIOD_S, hz: float = CONTROL_HZ) -> float:
    """Lateral setpoint in metres: a slow sine, so heading error stays small."""
    return amplitude * math.sin(2 * math.pi * step / (period_s * hz))


def yellow_centroids(imgs: np.ndarray, rows: np.ndarray = ROWS):
    """Column of the yellow centre line per (frame, row); NaN where unusable.

    Yellow is isolated by requiring BLUE TO BE DEPRESSED, not merely by
    brightness -- the warm-tinted white edge line is bright in R and G too, and
    a plain `R+G-2B` rule leaks onto it (measured while building AR).
    """
    f = np.asarray(imgs, np.float32)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    bright = np.minimum(R, G)
    m = (bright > 110) & ((bright - B) > 45)
    m = m[:, rows, :]
    W = m.shape[2]
    cols = np.arange(W, dtype=np.float32)
    n = m.sum(axis=2)
    cen = (m * cols).sum(axis=2) / np.maximum(n, 1)
    touches_edge = m[:, :, 0] | m[:, :, -1]
    ok = (n >= MIN_MASK) & ~touches_edge \
        & (cen > EDGE_REJECT) & (cen < W - 1 - EDGE_REJECT)
    return np.where(ok, cen, np.nan)


def fit_height(cen: np.ndarray, cte: np.ndarray, rows: np.ndarray = ROWS):
    """slope(v) = -(cos t / h)(v - v_h)  ->  h/cos(t) and the horizon row."""
    rows_ok, slopes, weights, rs = [], [], [], []
    for j, r in enumerate(rows):
        u = cen[:, j]
        ok = np.isfinite(u)
        if ok.sum() < 200:
            continue
        x, y = cte[ok].astype(np.float64), u[ok].astype(np.float64)
        if x.std() < 1e-6:
            continue
        s, _ = np.polyfit(x, y, 1)
        rows_ok.append(r); slopes.append(s); weights.append(ok.sum())
        rs.append(float(np.corrcoef(x, y)[0, 1]))
    if len(rows_ok) < 5:
        raise SystemExit(f"only {len(rows_ok)} usable rows - not enough to fit")
    rows_ok = np.asarray(rows_ok, float)
    slopes = np.asarray(slopes)
    w = np.sqrt(np.asarray(weights, float))
    a, c = np.polyfit(rows_ok, slopes, 1, w=w)
    resid = slopes - np.polyval([a, c], rows_ok)

    # ONE-PARAMETER FIT, and this is the estimate to trust.
    #
    # The free two-parameter fit above finds the horizon by extrapolating the
    # slope line to zero -- but the usable rows are 64-112 and the horizon is
    # near row 42, so it extrapolates ~100 rows past its own data and a 3-4%
    # slope error swings the intercept by tens of rows. The first run of this
    # returned a horizon of -13.6, outside the image entirely.
    #
    # The horizon does not need to be inferred here: AR measured it directly
    # from the sky boundary at 41.97 +- 0.28 px over 3,187 frames. Pinning it
    # leaves a single unknown, the scale, fit through the origin:
    #     slope = -(cos t / h) * (v - v_h)
    dv = rows_ok - HORIZON_ROW
    k = float(np.sum(w * dv * slopes) / np.sum(w * dv * dv))   # k = -(cos t)/h
    pred = k * dv
    resid1 = slopes - pred
    ss = float(np.sum(w * (slopes - np.average(slopes, weights=w)) ** 2))
    return {
        "h_over_cos_pitch_m": -1.0 / k if k != 0 else float("nan"),
        "horizon_row_ASSUMED": HORIZON_ROW,
        "one_param_resid_rms": float(resid1.std()),
        "one_param_r2": float(1 - np.sum(w * resid1 ** 2) / ss) if ss else float("nan"),
        "free_fit_h_over_cos_pitch_m": -1.0 / a if a != 0 else float("nan"),
        "free_fit_horizon_row": -c / a if a != 0 else float("nan"),
        "free_fit_resid_rms": float(resid.std()),
        "slope_per_row": float(a), "intercept": float(c),
        "n_rows": len(rows_ok), "mean_abs_r": float(np.mean(np.abs(rs))),
        "rows": rows_ok.tolist(), "slopes": slopes.tolist(),
    }


def collect(track: str, episodes: int, steps: int, port: int):
    import gym_donkeycar  # noqa: F401
    import gymnasium as gym
    from collect_sim_data import PIDDriver, SIM_EXE, WARMUP_STEPS
    from sim_conf import base_sim_conf

    # base_sim_conf pins cam_config (fov=90) so this run matches the corpus's
    # projection -- the whole point is to measure THAT camera, not another one.
    conf = base_sim_conf(str(SIM_EXE), port, "height", max_cte=4.0)
    env = gym.make(track, conf=conf)
    imgs, ctes = [], []
    try:
        for ep in range(episodes):
            obs, _ = env.reset()
            drv = PIDDriver()
            # Warm up against the ZERO setpoint: centre the car first, so the
            # sweep starts from a known lateral position rather than wherever
            # reset dropped it. (Reading `info` here before the first step is
            # what the first cut did -- undefined on episode 0, stale on 1.)
            info = {"cte": 0.0}
            for _ in range(WARMUP_STEPS):
                obs, _, te, tr, info = env.step(drv.act(float(info["cte"])))
                if te or tr:
                    break
            for k in range(steps):
                cte = float(info["cte"])
                # THE ONE CHANGE THAT MATTERS: a moving setpoint. PIDDriver's
                # setpoint is implicitly zero, so subtracting the target here
                # sweeps the car laterally without touching the driver.
                action = drv.act(cte - sweep_target(k))
                obs, _, te, tr, info = env.step(action)
                imgs.append(np.array(obs, copy=True))
                ctes.append(float(info["cte"]))
                if te or tr:
                    print(f"  ep{ep}: terminated at step {k}")
                    break
            print(f"  ep{ep}: {len(ctes)} frames so far, "
                  f"cte range [{min(ctes):.2f}, {max(ctes):.2f}]")
    finally:
        try: env.close()
        except Exception: pass
        time.sleep(3.0)
    return np.asarray(imgs), np.asarray(ctes, np.float32)


def self_check() -> None:
    """Synthetic ground truth: build frames from a KNOWN h, recover it."""
    H, W = 120, 160
    h_true, v_h, cos_t = 0.85, 42.0, 1.0
    rng = np.random.default_rng(0)
    cte = rng.uniform(-0.6, 0.6, 800).astype(np.float32)
    C = 0.0                                   # line at the track reference
    imgs = np.zeros((len(cte), H, W, 3), np.uint8)
    imgs[:, :, :] = (120, 120, 120)           # grey road, no yellow anywhere
    for i, c in enumerate(cte):
        for r in ROWS:
            u = W / 2 + ((C - c) * cos_t / h_true) * (r - v_h)
            j = int(round(u))
            if EDGE_REJECT + 2 < j < W - EDGE_REJECT - 3:
                imgs[i, r, j - 1:j + 2] = (255, 240, 30)   # yellow: B depressed
    cen = yellow_centroids(imgs)
    res = fit_height(cen, cte)
    got_h, got_vh = res["h_over_cos_pitch_m"], res["free_fit_horizon_row"]
    assert abs(got_h - h_true) < 0.03, f"h {got_h:.4f} != {h_true}"
    assert abs(got_vh - v_h) < 1.5, f"horizon {got_vh:.2f} != {v_h}"

    # the sweep must actually sweep, and slowly
    t = [sweep_target(k) for k in range(int(SWEEP_PERIOD_S * CONTROL_HZ))]
    assert abs(max(t) - SWEEP_AMPLITUDE) < 0.01 and abs(min(t) + SWEEP_AMPLITUDE) < 0.01
    assert max(abs(t[k + 1] - t[k]) for k in range(len(t) - 1)) < 0.01, \
        "setpoint steps too fast - heading error will not stay small"

    # border censoring must REJECT, not silently bias: a line pinned to the
    # left edge is exactly the failure that flattened AR.5's slopes
    edge = np.zeros((4, H, W, 3), np.uint8); edge[:, :, :] = (120, 120, 120)
    edge[:, ROWS, 0:3] = (255, 240, 30)
    assert np.isnan(yellow_centroids(edge)).all(), "edge-pinned line not rejected"
    print("diag_camera_height self_check: PASS")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--track", default="donkey-generated-roads-v0")
    ap.add_argument("--episodes", type=int, default=2)
    ap.add_argument("--steps", type=int, default=900)
    ap.add_argument("--port", type=int, default=9091)
    args = ap.parse_args()

    if args.self_check:
        self_check()
        return 0
    self_check()
    OUT.mkdir(parents=True, exist_ok=True)

    if args.collect:
        print(f"collecting a lateral sweep on {args.track} "
              f"(+-{SWEEP_AMPLITUDE} m, {SWEEP_PERIOD_S:.0f} s/cycle) ...")
        imgs, cte = collect(args.track, args.episodes, args.steps, args.port)
        np.save(OUT / "images.npy", imgs)
        np.save(OUT / "cte.npy", cte)
        print(f"-> {len(imgs):,} frames, cte range "
              f"[{cte.min():.3f}, {cte.max():.3f}] m, sd {cte.std():.3f}")

    if args.fit or not args.collect:
        imgs = np.load(OUT / "images.npy", mmap_mode="r")
        cte = np.load(OUT / "cte.npy")
        cen = yellow_centroids(np.asarray(imgs))
        usable = np.isfinite(cen).sum()
        print(f"{len(imgs):,} frames, cte sd {cte.std():.3f} m, "
              f"{usable:,} usable (frame,row) samples")
        res = fit_height(cen, cte)
        res["cte_sd"] = float(cte.std())
        res["cte_range"] = [float(cte.min()), float(cte.max())]
        res["n_frames"] = int(len(imgs))
        print()
        print(f"{res['n_rows']} usable rows, mean |r| {res['mean_abs_r']:.3f}")
        print(f"  ONE-PARAM (horizon PINNED at {res['horizon_row_ASSUMED']:.2f},"
              f" the trusted direct measurement):")
        print(f"    h / cos(pitch) = {res['h_over_cos_pitch_m']:.4f} sim units")
        print(f"    resid rms {res['one_param_resid_rms']:.4f}, "
              f"R^2 {res['one_param_r2']:.4f}")
        print("  FREE 2-PARAM (extrapolates ~100 rows past its data - fragile):")
        print(f"    h / cos(pitch) = {res['free_fit_h_over_cos_pitch_m']:.4f}, "
              f"horizon {res['free_fit_horizon_row']:.2f} (vs 41.97 measured)")
        write_result(OUT / "camera_height.json", res)
        print(f"-> {OUT / 'camera_height.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
