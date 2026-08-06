"""SIM-POC P2: collect a driving corpus from the Donkey simulator.

A scripted PID lane-follower drives; camera frames and the actions that
produced them are written as dreamerv3-torch episodes.

**The split is by TRACK, never by frame.** Frame t and t+1 in a driving log
are near-duplicates, so a random frame split leaks between train and test and
massively overstates accuracy. Whole tracks are held out instead, so the test
set is genuinely unseen geometry. The 11 registered Donkey tracks are the
simulator's analogue of the physical tile layouts (record Appendix L), and
the same rule carries forward to M3/M4 on real driving data.

**The driver is an EXPERT, not a model.** It steers on `cte` (cross-track
error) read from the simulator's privileged state -- it is standing in for a
human demonstrator, exactly as Evan will later drive the real car by hand.
Nothing downstream ever sees `cte`; the learned models get pixels only.

Usage:
  python ml/collect_sim_data.py --smoke          # 2 tracks, tiny, validates
  python ml/collect_sim_data.py                  # full corpus
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from episode_writer import EpisodeWriter

REPO = Path(__file__).resolve().parent.parent
SIM_EXE = REPO / "sim" / "DonkeySimWin" / "donkey_sim.exe"
DATA = REPO / "ml" / "data" / "sim"

# --- the layout split -------------------------------------------------------
# Held-out tracks are NEVER used for training. Chosen before any data was
# collected, so the split cannot be tuned to flatter a result.
TRAIN_TRACKS = [
    "donkey-generated-track-v0",
    "donkey-generated-roads-v0",
    "donkey-mountain-track-v0",
    "donkey-roboracingleague-track-v0",
]
HOLDOUT_TRACKS = [
    "donkey-waveshare-v0",
]

# --- expert driver ----------------------------------------------------------
# Gains and throttle were swept on donkey-generated-track-v0, 2026-08-05, not
# guessed. Full results in record Appendix M. Two findings from that sweep:
#
#   * STEER_SIGN: an open-loop probe held steer +0.35 and watched cte run
#     +0.005 -> +4.224, so positive steer INCREASES cte and the correction
#     must be negative. Measured, not assumed.
#   * THROTTLE dominates the gains. At 0.32 the car left the road in 191-218
#     steps under every gain setting tried; at 0.20 every setting survived
#     400/400. The PID simply cannot track the line at the higher speed.
#     Tuning gains without dropping throttle would have chased the wrong knob.
#
# Chosen: survived 400/400 with mean|cte| 0.36 (best of six configurations).
KP, KI, KD = 2.4, 0.0, 1.2     # on cross-track error, metres
STEER_SIGN = -1.0
THROTTLE = 0.20
THROTTLE_CORNER = 0.14         # ease off when steering hard
STEER_LIMIT = 1.0

# --- episode shaping --------------------------------------------------------
WARMUP_STEPS = 12              # car settles after reset; frames are garbage
MAX_EPISODE_STEPS = 1200
# An episode is expert data only if the driver actually stayed on the road.
# Anything worse is discarded rather than quietly poisoning the corpus.
MAX_MEAN_ABS_CTE = 1.2
MIN_EPISODE_STEPS = 150


class PIDDriver:
    def __init__(self):
        self.reset()

    def reset(self):
        self._prev_err = 0.0
        self._integral = 0.0

    def act(self, cte: float) -> np.ndarray:
        err = cte
        self._integral = float(np.clip(self._integral + err, -50.0, 50.0))
        derivative = err - self._prev_err
        self._prev_err = err

        steer = STEER_SIGN * (KP * err + KI * self._integral + KD * derivative)
        steer = float(np.clip(steer, -STEER_LIMIT, STEER_LIMIT))

        # slow down in corners so the PID can actually track the line
        throttle = THROTTLE_CORNER if abs(steer) > 0.5 else THROTTLE
        return np.array([steer, throttle], dtype=np.float32)


def collect_track(track: str, out_dir: Path, n_episodes: int,
                  max_steps: int, port: int) -> dict:
    import gym_donkeycar  # noqa: F401  registers the envs
    import gymnasium as gym

    conf = {
        "exe_path": str(SIM_EXE),
        "host": "127.0.0.1",
        "port": port,
        "start_delay": 10.0,
        "car_name": "poc",
        "max_cte": 4.0,          # terminate sooner than the 8.0 default:
                                 # past this the car is off-road and the
                                 # frames are not expert data
    }
    env = gym.make(track, conf=conf)
    driver = PIDDriver()
    writer = EpisodeWriter(out_dir, prefix=f"{track.replace('donkey-', '').replace('-v0', '')}-")

    stats = {"track": track, "saved": 0, "rejected": 0, "frames": 0,
             "cte": [], "reject_reasons": []}

    try:
        for ep in range(n_episodes):
            obs, _ = env.reset()
            driver.reset()

            # burn the settling frames without recording them
            for _ in range(WARMUP_STEPS):
                obs, _, term, trunc, info = env.step(np.array([0.0, THROTTLE], np.float32))
                if term or trunc:
                    obs, info = env.reset()[0], {}
                    driver.reset()

            writer.add_reset(obs, action_dim=2)
            # cte_log[i] is the cross-track error AT THE SAME INSTANT as
            # image[i]. Because the expert is a deterministic function of cte,
            # this lets verify_corpus.py recompute every action exactly and
            # prove the frame/action indexing is right -- see the note there.
            cte_log = [float(info.get("cte", 0.0)) if info else 0.0]
            ctes, terminated, truncated = [], False, False

            for _ in range(max_steps):
                action = driver.act(cte_log[-1])
                obs, reward, terminated, truncated, info = env.step(action)
                writer.add_step(obs, action, reward, terminated, truncated)
                cte_log.append(float(info.get("cte", 0.0)))
                ctes.append(abs(cte_log[-1]))
                if terminated or truncated:
                    break

            n = len(writer)
            mean_cte = float(np.mean(ctes)) if ctes else 99.0
            reason = None
            if n < MIN_EPISODE_STEPS:
                reason = f"too short ({n} steps)"
            elif mean_cte > MAX_MEAN_ABS_CTE:
                reason = f"poor driving (mean|cte| {mean_cte:.2f})"

            if reason:
                stats["rejected"] += 1
                stats["reject_reasons"].append(reason)
                writer._steps = []          # drop it, do not save
                print(f"    ep {ep+1}/{n_episodes}: REJECTED - {reason}")
            else:
                path = writer.save(meta={
                    "track": track,
                    "mean_abs_cte": mean_cte,
                    "cte": np.array(cte_log, np.float32),
                    # the expert's parameters, so the verifier recomputes the
                    # actions from what was actually used, not from constants
                    # that may have since been re-tuned
                    "kp": KP, "kd": KD, "ki": KI, "steer_sign": STEER_SIGN,
                    "throttle": THROTTLE, "throttle_corner": THROTTLE_CORNER,
                    "steer_limit": STEER_LIMIT,
                })
                stats["saved"] += 1
                stats["frames"] += n
                stats["cte"].append(mean_cte)
                print(f"    ep {ep+1}/{n_episodes}: saved {n:5d} frames "
                      f"mean|cte| {mean_cte:.2f}  {path.name}")
    finally:
        try:
            env.close()
        except Exception:                    # noqa: BLE001
            pass
        time.sleep(2.0)                      # let the sim process exit

    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="tiny run to validate the pipeline before the real one")
    ap.add_argument("--episodes", type=int, default=6,
                    help="episodes per track")
    ap.add_argument("--max-steps", type=int, default=MAX_EPISODE_STEPS)
    ap.add_argument("--port", type=int, default=9091)
    args = ap.parse_args()

    if args.smoke:
        train_tracks = TRAIN_TRACKS[:1]
        holdout_tracks = HOLDOUT_TRACKS[:1]
        episodes, max_steps = 1, 300
        root = DATA.parent / "sim_smoke"
    else:
        train_tracks, holdout_tracks = TRAIN_TRACKS, HOLDOUT_TRACKS
        episodes, max_steps = args.episodes, args.max_steps
        root = DATA

    print(f"corpus root : {root}")
    print(f"train tracks: {train_tracks}")
    print(f"holdout     : {holdout_tracks}  (never trained on)")
    print()

    all_stats = []
    for split, tracks in (("train", train_tracks), ("holdout", holdout_tracks)):
        for track in tracks:
            print(f"[{split}] {track}")
            st = collect_track(track, root / split, episodes, max_steps, args.port)
            st["split"] = split
            all_stats.append(st)

    print("\n--- summary ---")
    total = 0
    for st in all_stats:
        cte = f"{np.mean(st['cte']):.2f}" if st["cte"] else "n/a"
        print(f"{st['split']:8s} {st['track']:34s} "
              f"saved {st['saved']:3d}  rejected {st['rejected']:3d}  "
              f"frames {st['frames']:7d}  mean|cte| {cte}")
        total += st["frames"]
    print(f"{'':8s} {'TOTAL':34s} {'':22s} frames {total:7d}")

    rejected = sum(s["rejected"] for s in all_stats)
    if rejected:
        print(f"\n{rejected} episode(s) rejected and NOT written:")
        for st in all_stats:
            for r in st["reject_reasons"]:
                print(f"  {st['track']}: {r}")


if __name__ == "__main__":
    main()
