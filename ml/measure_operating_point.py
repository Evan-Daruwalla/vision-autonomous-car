"""What operating point did every sim result actually assume?

Everything trained and measured so far — the corpus, the world model, the
controllers, the recovery data — is tied to a specific speed, control rate,
camera geometry and lane scale. **The physical car only inherits those results
if it is built to the same operating point**, and most of that point was never
written down: `THROTTLE = 0.20` is a normalised command, not a speed, and the
corpus logs cte but not velocity.

This drives the scripted expert and records what the numbers mean in physical
units, so the real-car spec can be derived rather than guessed.

Reported:
  speed at THROTTLE 0.20 / 0.14   the corpus's cruise and corner speeds, m/s
  cte distribution                 what "mean|cte| 0.36" is in metres
  control rate                     the loop the PID gains were tuned at
  frames                           120x160 native, squashed to 64x64

Usage:
  python ml/measure_operating_point.py --steps 400
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from collect_sim_data import (KD, KI, KP, PIDDriver, SIM_EXE, STEER_LIMIT,
                              STEER_SIGN, THROTTLE, THROTTLE_CORNER,
                              WARMUP_STEPS)
from sim_conf import base_sim_conf

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", default="donkey-generated-track-v0")
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--port", type=int, default=9091)
    ap.add_argument("--out", default=str(RUNS / "operating_point"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    import gym_donkeycar  # noqa: F401
    import gymnasium as gym

    conf = base_sim_conf(str(SIM_EXE), args.port, "op", max_cte=4.0)
    env = gym.make(args.track, conf=conf)
    driver = PIDDriver()

    rows = []
    try:
        obs, info = env.reset()
        driver.reset()
        for _ in range(WARMUP_STEPS):
            obs, _, term, trunc, info = env.step(
                np.array([0.0, THROTTLE], np.float32))
        cte = float(info.get("cte", 0.0))
        t0 = time.time()
        for i in range(args.steps):
            a = driver.act(cte)
            obs, _, term, trunc, info = env.step(a)
            cte = float(info.get("cte", 0.0))
            rows.append({"i": i, "cte": cte,
                         "speed": float(info.get("speed", 0.0)),
                         "fwd": float(info.get("forward_vel", 0.0)),
                         "steer": float(a[0]), "throttle": float(a[1])})
            if term or trunc:
                break
        elapsed = time.time() - t0
    finally:
        try:
            env.close()
        except Exception:                      # noqa: BLE001
            pass
        time.sleep(2.0)

    n = len(rows)
    sp = np.array([r["speed"] for r in rows])
    ct = np.abs([r["cte"] for r in rows])
    thr = np.array([r["throttle"] for r in rows])
    st = np.abs([r["steer"] for r in rows])
    # Discard the first 50 steps for the steady-state figure: the car is still
    # accelerating out of the reset and would drag the cruise speed down.
    ss = sp[50:] if n > 100 else sp
    # np.isclose, NOT ==: throttle round-trips through float32 and comes back
    # as 0.20000000298023224, so exact equality never matches. Measured
    # 2026-08-12: the == form silently reported frac_steps_cornering 0.0 when
    # the true value was 0.605, and left both speeds null.
    cruise = sp[np.isclose(thr, THROTTLE)]
    corner = sp[np.isclose(thr, THROTTLE_CORNER)]
    hz = n / elapsed if elapsed > 0 else 0.0
    img = obs.shape if hasattr(obs, "shape") else None

    res = {
        "steps": n, "control_hz": round(hz, 2),
        "frame_shape": list(img) if img else None,
        "speed_steady_mean": float(ss.mean()), "speed_steady_max": float(ss.max()),
        "speed_cruise_mean": float(cruise.mean()) if len(cruise) else None,
        "speed_corner_mean": float(corner.mean()) if len(corner) else None,
        "frac_steps_cornering": float(np.isclose(thr, THROTTLE_CORNER).mean()),
        "cte_mean_abs": float(ct.mean()), "cte_p95": float(np.percentile(ct, 95)),
        "cte_max": float(ct.max()),
        "steer_mean_abs": float(st.mean()), "steer_p95": float(np.percentile(st, 95)),
        "gains": {"kp": KP, "ki": KI, "kd": KD, "steer_sign": STEER_SIGN,
                  "steer_limit": STEER_LIMIT, "throttle": THROTTLE,
                  "throttle_corner": THROTTLE_CORNER},
    }
    print(f"\nsteps {n}  control {hz:.2f} Hz  frame {img}")
    print(f"speed  steady mean {ss.mean():.3f} m/s  max {ss.max():.3f}")
    if len(cruise):
        print(f"       cruise (thr {THROTTLE})       {cruise.mean():.3f} m/s")
    if len(corner):
        print(f"       corner (thr {THROTTLE_CORNER})       {corner.mean():.3f} m/s"
              f"   ({100*np.isclose(thr,THROTTLE_CORNER).mean():.0f}% of steps)")
    print(f"|cte|  mean {ct.mean():.3f} m  p95 {np.percentile(ct,95):.3f}  "
          f"max {ct.max():.3f}")
    print(f"|steer| mean {st.mean():.3f}  p95 {np.percentile(st,95):.3f} "
          f"(of limit {STEER_LIMIT})")
    (out / "operating_point.json").write_text(json.dumps(
        {"args": vars(args), "result": res, "per_step": rows}, indent=2))
    print(f"-> {out / 'operating_point.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
