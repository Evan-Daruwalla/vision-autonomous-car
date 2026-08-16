"""Collect OFF-CENTRE RECOVERY data — the direct test of Appendix W.1.

W.1 measured that every learned policy fails because PERCEPTION goes out of
distribution: the probe reads lane position accurately while |cte| < 1.0 and
degrades to ~2.1 error past 1.5, with the same curve under a learned policy
(corr 0.894) and the PID expert (0.852). The cause is coverage --
`collect_sim_data.py` rejects any episode with `mean|cte| > 1.2` and the expert
averaged 0.36, so the encoder has never seen an off-centre frame.

This collects the missing states by DART-style noise injection (Laskey et al.,
"DART: Noise Injection for Robust Imitation Learning"): drive the expert, but
periodically inject a burst of steering noise that pushes the car off the
centre line, then hand control back and let the PID drive home. The frames in
between are exactly the off-centre states the corpus lacks.

**Chosen over DAgger deliberately.** DAgger needs an expert to relabel states
the learner visits, which on a physical car means a human with a controller
riding along every run. Noise injection needs only the scripted expert, so the
same procedure works on the real car later — which is the point, since this
experiment exists to de-risk M3.

WHAT IS RECORDED, and why it keeps the data contract intact:
  `action`      the action ACTUALLY EXECUTED, including noise. The contract in
                data.md is that action[i] produced image[i], and
                verify_corpus's alignment gate depends on it. Recording the
                expert's counterfactual action here instead would break both.
  `log_noise`   1.0 on frames where noise was injected, 0.0 otherwise.
  `log_expert_steer`
                what the expert WOULD have commanded in that state. This is
                the behavioural-cloning label for noise frames, where the
                executed action is deliberately wrong.

So downstream consumers split cleanly:
  VAE / cte probe  -> train on EVERY frame. They need the off-centre pixels,
                      and they do not care what action was taken. **This is
                      the part W.1 says is actually broken.**
  dynamics (M)     -> train on every frame using `action` (executed), which is
                      what genuinely produced the transition.
  controller (C)   -> use `log_expert_steer`, or drop noise frames entirely.
                      Cloning the noise would teach the car to swerve.

**The PID identity gate still passes**, because `log_cte` and the logged gains
still reproduce `log_expert_steer` exactly; the executed action differs by the
recorded noise, which is itself logged. Nothing about the verifier is relaxed.

Episodes are written to a SEPARATE directory. The P2-P5 corpus is untouched
and every result in the record remains reproducible from it.

Usage:
  python ml/collect_recovery.py --smoke
  python ml/collect_recovery.py --episodes 12
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from collect_sim_data import (KD, KI, KP, MAX_EPISODE_STEPS, MIN_EPISODE_STEPS,
                              PIDDriver, SIM_EXE, STEER_LIMIT, STEER_SIGN,
                              THROTTLE, THROTTLE_CORNER, WARMUP_STEPS)
from episode_writer import EpisodeWriter
from sim_conf import base_sim_conf

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "ml" / "data" / "sim_recovery" / "train"

# Noise schedule. A burst has to be long enough to actually leave the centre
# lane -- a single noisy step is corrected before the car moves -- and the gap
# long enough for the expert to finish recovering and re-centre, so the corpus
# gets the whole return trajectory rather than a series of half-recoveries.
BURST_EVERY = 60          # steps between bursts
BURST_LEN = 8             # steps of injected noise
BURST_STEER = 0.55        # magnitude; sign alternates so both sides are covered

# Deliberately NOT MAX_MEAN_ABS_CTE = 1.2. That threshold is what excluded
# off-centre data in the first place; applying it here would reject exactly the
# episodes this script exists to collect. A loose cap is still needed so a run
# that simply drove off the road and died is not kept as "recovery data".
MAX_MEAN_ABS_CTE_RECOVERY = 2.5


def collect(track: str, out_dir: Path, n_episodes: int, max_steps: int,
            port: int, seed: int) -> dict:
    import gym_donkeycar  # noqa: F401  registers the envs
    import gymnasium as gym

    conf = base_sim_conf(str(SIM_EXE), port, "rec", max_cte=4.0)
    env = gym.make(track, conf=conf)
    driver = PIDDriver()
    writer = EpisodeWriter(
        out_dir, prefix=f"{track.replace('donkey-', '').replace('-v0', '')}-rec-")
    rng = np.random.default_rng(seed)
    stats = {"track": track, "saved": 0, "rejected": 0, "frames": 0,
             "noise_frames": 0, "cte": [], "reject_reasons": []}

    try:
        for ep in range(n_episodes):
            obs, _ = env.reset()
            driver.reset()
            info = {}
            for _ in range(WARMUP_STEPS):
                obs, _, term, trunc, info = env.step(
                    np.array([0.0, THROTTLE], np.float32))
                if term or trunc:
                    obs, _ = env.reset(); driver.reset()
                    obs, _, term, trunc, info = env.step(
                        np.array([0.0, THROTTLE], np.float32))

            writer.add_reset(obs, action_dim=2)
            cte_log = [float(info.get("cte", 0.0)) if info else 0.0]
            noise_log, expert_log = [0.0], [0.0]
            ctes = []
            burst_left, burst_sign = 0, 1.0

            for t in range(max_steps):
                expert = driver.act(cte_log[-1])
                expert_steer = float(expert[0])

                if t > 0 and t % BURST_EVERY == 0 and burst_left == 0:
                    burst_left = BURST_LEN
                    # alternate sides, with a little jitter so the corpus does
                    # not contain one stereotyped perturbation repeated
                    burst_sign = -burst_sign
                if burst_left > 0:
                    mag = BURST_STEER * float(rng.uniform(0.7, 1.3))
                    steer = float(np.clip(burst_sign * mag,
                                          -STEER_LIMIT, STEER_LIMIT))
                    burst_left -= 1
                    noisy = 1.0
                else:
                    steer = expert_steer
                    noisy = 0.0

                thr = THROTTLE_CORNER if abs(steer) > 0.5 else THROTTLE
                action = np.array([steer, thr], np.float32)

                obs, reward, terminated, truncated, info = env.step(action)
                writer.add_step(obs, action, reward, terminated, truncated)
                cte_log.append(float(info.get("cte", 0.0)))
                noise_log.append(noisy)
                expert_log.append(expert_steer)
                ctes.append(abs(cte_log[-1]))
                if terminated or truncated:
                    break

            n = len(writer)
            mean_cte = float(np.mean(ctes)) if ctes else 99.0
            reason = None
            if n < MIN_EPISODE_STEPS:
                reason = f"too short ({n} steps)"
            elif mean_cte > MAX_MEAN_ABS_CTE_RECOVERY:
                reason = f"never recovered (mean|cte| {mean_cte:.2f})"

            if reason:
                stats["rejected"] += 1
                stats["reject_reasons"].append(reason)
                writer._steps = []
                print(f"    ep {ep+1}/{n_episodes}: REJECTED - {reason}")
                continue

            nz = int(sum(noise_log))
            off = float(np.mean(np.asarray(ctes) > 1.0))
            path = writer.save(meta={
                "track": track,
                "mean_abs_cte": mean_cte,
                "cte": np.array(cte_log, np.float32),
                "noise": np.array(noise_log, np.float32),
                "expert_steer": np.array(expert_log, np.float32),
                "recovery": 1.0,
                "kp": KP, "kd": KD, "ki": KI, "steer_sign": STEER_SIGN,
                "throttle": THROTTLE, "throttle_corner": THROTTLE_CORNER,
                "steer_limit": STEER_LIMIT,
            })
            stats["saved"] += 1
            stats["frames"] += n
            stats["noise_frames"] += nz
            stats["cte"].append(mean_cte)
            print(f"    ep {ep+1}/{n_episodes}: saved {n:5d} frames "
                  f"mean|cte| {mean_cte:.2f}  {100*off:4.1f}% off-centre "
                  f"(|cte|>1.0)  {nz} noise  {path.name}")
    finally:
        try:
            env.close()
        except Exception:                    # noqa: BLE001
            pass
        time.sleep(2.0)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", default="donkey-generated-track-v0")
    ap.add_argument("--episodes", type=int, default=12)
    ap.add_argument("--max-steps", type=int, default=MAX_EPISODE_STEPS)
    ap.add_argument("--port", type=int, default=9091)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.episodes, args.max_steps = 2, 300

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    print(f"collecting recovery data -> {out}")
    print(f"  burst every {BURST_EVERY} steps, {BURST_LEN} steps long, "
          f"steer {BURST_STEER}\n")
    s = collect(args.track, out, args.episodes, args.max_steps, args.port,
                args.seed)
    print(f"\nsaved {s['saved']} episodes, {s['frames']:,} frames "
          f"({s['noise_frames']:,} noise-injected), "
          f"rejected {s['rejected']}")
    if s["cte"]:
        print(f"  mean|cte| across episodes: {np.mean(s['cte']):.2f} "
              f"(the ORIGINAL corpus averaged 0.36)")
    return 0 if s["saved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
