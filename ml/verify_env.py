"""SIM-POC P1 done-check: prove the ML environment actually works.

Two assertions, both required by the PRD's P1 task:
  1. torch.cuda.is_available() is True on the RTX 3060 Ti
  2. a gym-donkeycar env connects to the simulator and returns a camera frame

Run:  .venv\\Scripts\\python.exe ml\\verify_env.py

Launches the Unity simulator itself (a window will open), drives a few
steps, saves the first frame, and exits non-zero if anything fails. Nothing
here is training -- it is the environment smoke test.
"""

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SIM_EXE = REPO / "sim" / "DonkeySimWin" / "donkey_sim.exe"
OUT = REPO / "ml" / "artifacts"
TRACK = "donkey-generated-track-v0"   # the standard training track

# The sim needs a moment between launch and accepting a socket connection.
# gym-donkeycar handles the wait internally, but a cold Unity start on a
# spinning disk can exceed its default -- give it room.
START_DELAY = 10.0


def main():
    failures = []

    # --- check 1: CUDA -----------------------------------------------------
    import torch
    cuda = torch.cuda.is_available()
    print(f"torch            : {torch.__version__}")
    print(f"cuda.is_available: {cuda}")
    if cuda:
        props = torch.cuda.get_device_properties(0)
        print(f"device           : {props.name}")
        print(f"total VRAM       : {props.total_memory / 1024**3:.2f} GiB")
    else:
        failures.append("torch.cuda.is_available() is False")

    # --- check 2: simulator connection + camera frame ----------------------
    if not SIM_EXE.exists():
        failures.append(f"simulator not found at {SIM_EXE}")
        report(failures)
        return

    import gym_donkeycar  # noqa: F401  (registers the gymnasium envs)
    import gymnasium as gym
    import numpy as np
    from PIL import Image

    conf = {
        "exe_path": str(SIM_EXE),
        "host": "127.0.0.1",
        "port": 9091,
        "start_delay": START_DELAY,
        "car_name": "poc",
        "font_size": 40,
    }

    print(f"\nlaunching simulator: {SIM_EXE.name}  (track {TRACK})")
    env = gym.make(TRACK, conf=conf)
    try:
        obs, _info = env.reset()
        print(f"reset ok         : obs {obs.shape} {obs.dtype}")

        # a few steps with a mild right turn so the frame isn't the spawn shot
        for _ in range(20):
            obs, reward, terminated, truncated, info = env.step(
                np.array([0.15, 0.35], dtype=np.float32))
            if terminated or truncated:
                obs, _info = env.reset()

        print(f"step ok          : obs {obs.shape}, reward {reward:.3f}")
        print(f"info keys        : {sorted(info.keys())}")

        if obs.ndim != 3 or obs.shape[2] != 3:
            failures.append(f"unexpected observation shape {obs.shape}")
        if int(obs.max()) == 0:
            failures.append("camera frame is entirely black")

        OUT.mkdir(parents=True, exist_ok=True)
        frame = OUT / "p1_first_frame.png"
        Image.fromarray(obs).save(frame)
        print(f"saved frame      : {frame.relative_to(REPO)}"
              f"  (min {obs.min()} max {obs.max()} mean {obs.mean():.1f})")
    except Exception as exc:                      # noqa: BLE001
        failures.append(f"simulator interaction failed: {exc!r}")
    finally:
        try:
            env.close()
        except Exception:                          # noqa: BLE001
            pass
        time.sleep(1.0)

    report(failures)


def report(failures):
    print()
    if failures:
        print("P1 DONE-CHECK: FAIL")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("P1 DONE-CHECK: PASS  (cuda available + sim returned a camera frame)")


if __name__ == "__main__":
    main()
