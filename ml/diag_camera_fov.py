"""What FOV was the entire corpus actually captured at?

Record AG.4: `donkey_sim.py` only sends a camera config when `cam_config` is
present in the conf dict, and **this project never put one there**. So the FOV,
lens distortion, camera height, pitch and forward offset of every frame the
ConvVAE ever saw are the Unity binary's defaults, and those defaults are not
recorded anywhere on the Python side. They cannot be read out of the code.

**They can be identified by comparison.** Capture one frame at the default,
then frames with `cam_config` set to a series of explicit FOVs from the same
pose. Whichever explicit value reproduces the default frame identifies it.

The pose is controlled for free: `ml/diag_reset.py` measured post-reset
position as deterministic across launches (z identical, x identical in 14 of
16 episodes), so a frame captured immediately after reset is comparable
between runs.

**Why this gates a purchase.** The Camera Module 3 Wide is 120 deg. If the sim
default is materially narrower, the encoder trained on a projection the real
camera will not produce, and the Wide is the wrong part. This is the cheapest
possible check: one sim run, no hardware.

Each FOV needs its own launch, because the camera config is sent once at
connect.

Usage:
  python ml/diag_camera_fov.py --fovs 60 75 90 105 120 150
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from provenance import write_result
from collect_sim_data import SIM_EXE, THROTTLE, WARMUP_STEPS

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"


def grab(track: str, port: int, fov: int | None, warmup: int) -> np.ndarray:
    """One frame from a fresh launch, at a controlled pose.

    `fov=None` means send NO cam_config at all — reproducing exactly what the
    corpus collector did, so the returned frame IS the unrecorded default.
    """
    import gym_donkeycar  # noqa: F401
    import gymnasium as gym

    conf = {"exe_path": str(SIM_EXE), "host": "127.0.0.1", "port": port,
            "start_delay": 10.0, "car_name": "fov", "max_cte": 4.0}
    if fov is not None:
        # Only the keys donkey_sim.extract_keys looks for are sent; anything
        # left at 0 means "sim default" per its own docstring, so this isolates
        # FOV and changes nothing else.
        conf["cam_config"] = {"img_w": 160, "img_h": 120, "img_d": 3,
                              "fov": int(fov), "fish_eye_x": 0.0,
                              "fish_eye_y": 0.0, "offset_x": 0.0,
                              "offset_y": 0.0, "offset_z": 0.0,
                              "rot_x": 0.0, "rot_y": 0.0, "rot_z": 0.0}
    env = gym.make(track, conf=conf)
    try:
        obs, _ = env.reset()
        for _ in range(warmup):
            obs, _, term, trunc, _ = env.step(
                np.array([0.0, THROTTLE], np.float32))
            if term or trunc:
                break
        return np.array(obs, copy=True)
    finally:
        try:
            env.close()
        except Exception:                      # noqa: BLE001
            pass
        time.sleep(3.0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", default="donkey-generated-track-v0")
    ap.add_argument("--fovs", type=int, nargs="+",
                    default=[60, 75, 90, 105, 120, 150])
    ap.add_argument("--warmup", type=int, default=WARMUP_STEPS,
                    help="steps after reset before capture; the corpus "
                         "collector used WARMUP_STEPS, so match it")
    ap.add_argument("--port", type=int, default=9091)
    ap.add_argument("--out", default=str(RUNS / "camera_fov"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print("capturing the DEFAULT frame (no cam_config, exactly as the corpus "
          "was collected) ...")
    ref = grab(args.track, args.port, None, args.warmup)
    print(f"  default frame {ref.shape}, mean {ref.mean():.2f}")

    # A second default capture bounds the noise floor: any explicit FOV whose
    # difference from the reference is at or below this is indistinguishable
    # from the default, and anything above it is a real difference.
    print("capturing a SECOND default frame to bound run-to-run noise ...")
    ref2 = grab(args.track, args.port, None, args.warmup)
    noise = float(np.abs(ref.astype(np.int16) - ref2.astype(np.int16)).mean())
    print(f"  default-vs-default MAE = {noise:.3f}  <- the noise floor\n")

    rows = []
    for fov in args.fovs:
        print(f"capturing at fov={fov} ...")
        f = grab(args.track, args.port, fov, args.warmup)
        mae = float(np.abs(ref.astype(np.int16) - f.astype(np.int16)).mean())
        rows.append({"fov": fov, "mae_vs_default": mae,
                     "distinguishable": bool(mae > 3 * max(noise, 0.1))})
        print(f"  MAE vs default {mae:.3f}"
              f"{'   <-- matches the default' if mae <= 3*max(noise,0.1) else ''}")
        np.save(out / f"frame_fov{fov}.npy", f)

    np.save(out / "frame_default.npy", ref)
    rows.sort(key=lambda r: r["mae_vs_default"])
    best = rows[0]

    print(f"\n{'fov':>6}{'MAE vs default':>18}{'distinguishable':>18}")
    for r in sorted(rows, key=lambda r: r["fov"]):
        print(f"{r['fov']:>6}{r['mae_vs_default']:>18.3f}"
              f"{str(r['distinguishable']):>18}")
    print(f"\nnoise floor (default vs default) = {noise:.3f}")

    matches = [r for r in rows if not r["distinguishable"]]
    if len(matches) == 1:
        verdict = (f"THE SIM DEFAULT FOV IS {matches[0]['fov']} DEGREES "
                   f"(MAE {matches[0]['mae_vs_default']:.3f} vs a noise floor "
                   f"of {noise:.3f}; every other tested FOV is clearly "
                   f"distinguishable). The corpus was captured at this FOV, so "
                   f"the physical camera must match it.")
    elif len(matches) > 1:
        verdict = (f"AMBIGUOUS: {len(matches)} tested FOVs are indistinguishable "
                   f"from the default ({[m['fov'] for m in matches]}). Either "
                   f"the sim ignored cam_config entirely, or the frames are "
                   f"insensitive to FOV at this pose. **Check whether the "
                   f"captured frames actually differ from each other before "
                   f"concluding anything** — if they are all identical, "
                   f"cam_config is not being applied and this method cannot "
                   f"answer the question.")
    else:
        verdict = (f"NO TESTED FOV MATCHES THE DEFAULT. Closest is "
                   f"{best['fov']} deg at MAE {best['mae_vs_default']:.3f} "
                   f"against a {noise:.3f} noise floor. The default lies "
                   f"outside the tested range, or differs in something other "
                   f"than FOV. Widen --fovs.")
    print(f"\nVERDICT: {verdict}")

    # A sanity check the verdict depends on: if the explicit-FOV frames are all
    # identical to each other, cam_config was silently ignored and every number
    # above is meaningless.
    spread = 0.0
    if len(rows) > 1:
        a = np.load(out / f"frame_fov{rows[0]['fov']}.npy").astype(np.int16)
        b = np.load(out / f"frame_fov{rows[-1]['fov']}.npy").astype(np.int16)
        spread = float(np.abs(a - b).mean())
    print(f"sanity: MAE between the two most-different explicit FOVs = "
          f"{spread:.3f}"
          f"{'   *** cam_config APPEARS TO BE IGNORED ***' if spread <= 3*max(noise,0.1) else ''}")

    write_result(out / "camera_fov.json", 
        {"args": vars(args), "noise_floor_mae": noise, "results": rows,
         "explicit_fov_spread": spread, "verdict": verdict})
    print(f"-> {out / 'camera_fov.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
