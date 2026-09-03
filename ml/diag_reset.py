"""Is the episode START STATE uncontrolled? (tests the Appendix AC hypothesis)

AC left the project with a harness it cannot trust: two closed-loop batches
that pass every available check -- expert 600/600 at 20 Hz, healthy mean|cte|
-- disagreed by 3x on the same controller checkpoints. The leading suspect is
the reset.

`DonkeyEnv.reset()` is SLEEP-synchronised, not state-synchronised:

    send_control(0, 0, handbrake) ; sleep(0.1) ; viewer.reset()
    send_control(0, 0, handbrake) ; sleep(0.1) ; observe()

Nothing waits for the simulator to confirm the reset landed. Under different
machine load the car's pose and speed at the first control step could differ.
A PID absorbs a varied start (the expert finishes 600/600 regardless); a
marginal learned policy would not -- which is exactly the pattern observed,
where the expert gate passes while controller numbers swing 3x.

**The `seed=` argument is a red herring** and this script does not use it: it
sets only `self.np_random`, which lives in the Python process. The simulator
is a separate Unity binary and never reads it.

WHAT IS MEASURED. Per episode, the car's state at two moments:
  post-reset   immediately after env.reset(), before any action
  post-warmup  after WARMUP_STEPS of straight throttle -- **this is the state
               the policy actually inherits**, so it is the one that matters

Spread ACROSS episodes within one sim launch, and (run this script twice)
across launches. If these are tight, the reset is exonerated and the 3x swing
has another cause; that is a useful answer too, and the script says so rather
than hunting for a culprit.

Usage:
  python ml/diag_reset.py --episodes 8
  python ml/diag_reset.py --episodes 8 --tag second_launch
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from collect_sim_data import SIM_EXE, THROTTLE, WARMUP_STEPS
from provenance import write_result
from sim_conf import base_sim_conf

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"


def snapshot(info: dict) -> dict:
    pos = info.get("pos", (0.0, 0.0, 0.0))
    return {"cte": float(info.get("cte", 0.0)),
            "speed": float(info.get("speed", 0.0)),
            "x": float(pos[0]), "y": float(pos[1]), "z": float(pos[2])}


def spread(rows, key) -> tuple:
    v = np.array([r[key] for r in rows], float)
    return float(v.mean()), float(v.std()), float(v.min()), float(v.max())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", default="donkey-generated-track-v0")
    ap.add_argument("--episodes", type=int, default=8)
    ap.add_argument("--port", type=int, default=9091)
    ap.add_argument("--tag", default="launch1")
    ap.add_argument("--out", default=str(RUNS / "diag_reset"))
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    import gym_donkeycar  # noqa: F401  registers the envs
    import gymnasium as gym

    conf = base_sim_conf(str(SIM_EXE), args.port, "diag", max_cte=4.0)
    env = gym.make(args.track, conf=conf)

    post_reset, post_warmup = [], []
    try:
        for ep in range(args.episodes):
            t0 = time.time()
            obs, info = env.reset()
            # env.reset() returns (obs, info); info comes straight from
            # observe(), so this is the state before ANY action is issued.
            r = snapshot(info if isinstance(info, dict) else {})
            r["episode"] = ep
            r["reset_seconds"] = round(time.time() - t0, 3)
            post_reset.append(r)

            # Replicate eval_in_sim.run_episode's warmup EXACTLY: the state the
            # policy inherits is the one after this loop, not after reset.
            last = {}
            for _ in range(WARMUP_STEPS):
                obs, _, term, trunc, last = env.step(
                    np.array([0.0, THROTTLE], np.float32))
                if term or trunc:
                    obs, _ = env.reset()
                    obs, _, term, trunc, last = env.step(
                        np.array([0.0, THROTTLE], np.float32))
            w = snapshot(last)
            w["episode"] = ep
            post_warmup.append(w)
            print(f"  ep {ep}: reset cte {r['cte']:+.4f} speed {r['speed']:.3f} "
                  f"pos ({r['x']:.2f},{r['z']:.2f}) [{r['reset_seconds']:.2f}s]"
                  f"  ->  warmup cte {w['cte']:+.4f} speed {w['speed']:.3f} "
                  f"pos ({w['x']:.2f},{w['z']:.2f})")
    finally:
        try:
            env.close()
        except Exception:                      # noqa: BLE001
            pass
        time.sleep(2.0)

    print(f"\n{'':<14}{'mean':>10}{'sd':>10}{'min':>10}{'max':>10}{'range':>10}")
    summary = {}
    for name, rows in (("post-reset", post_reset), ("post-warmup", post_warmup)):
        print(f"{name}")
        for key in ("cte", "speed", "x", "z"):
            m, s, lo, hi = spread(rows, key)
            summary[f"{name}_{key}"] = {"mean": m, "sd": s, "min": lo, "max": hi}
            print(f"  {key:<12}{m:>10.4f}{s:>10.4f}{lo:>10.4f}{hi:>10.4f}"
                  f"{hi-lo:>10.4f}")

    # The verdict rides on POST-WARMUP cte, because that is what the policy
    # inherits. Thresholds are deliberately loose: the question is whether the
    # spread is big enough to plausibly move a marginal policy, not whether it
    # is exactly zero.
    w_cte = summary["post-warmup_cte"]
    w_spd = summary["post-warmup_speed"]
    cte_range = w_cte["max"] - w_cte["min"]
    print()
    if cte_range < 0.05 and w_spd["sd"] < 0.05:
        verdict = (f"RESET IS CLEAN within this launch. Post-warmup cte varies "
                   f"by only {cte_range:.4f} across {args.episodes} episodes "
                   f"and speed sd is {w_spd['sd']:.4f}. **The start state is "
                   f"NOT the source of the 3x batch-to-batch swing** -- look "
                   f"elsewhere. Run this again as a separate launch and compare "
                   f"the two summaries before fully clearing it, since the "
                   f"swing was observed ACROSS launches.")
    else:
        verdict = (f"RESET IS NOT DETERMINISTIC. Post-warmup cte spans "
                   f"{cte_range:.4f} (min {w_cte['min']:+.4f}, max "
                   f"{w_cte['max']:+.4f}) and speed sd is {w_spd['sd']:.4f} "
                   f"across {args.episodes} episodes in ONE launch. The policy "
                   f"inherits a different starting condition each episode, "
                   f"which is a live explanation for the closed-loop variance "
                   f"in Appendix AC.")
    print(f"VERDICT: {verdict}")

    path = out / f"diag_reset_{args.tag}.json"
    write_result(path, 
        {"args": vars(args), "warmup_steps": WARMUP_STEPS,
         "post_reset": post_reset, "post_warmup": post_warmup,
         "summary": summary, "verdict": verdict})
    print(f"-> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
