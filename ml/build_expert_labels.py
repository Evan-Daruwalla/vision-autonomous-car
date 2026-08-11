"""Behavioural-cloning labels for the augmented corpus: what the EXPERT would
have done, not what was executed.

`collect_recovery.py` records the action ACTUALLY EXECUTED, including injected
noise, because the data contract in data.md is that action[i] produced
image[i] and verify_corpus's alignment gate depends on it. That is right for
the dynamics model, which has to learn what genuinely moved the car.

**It is wrong for the controller.** On a noise frame the executed steering is
deliberately incorrect -- the whole point is to shove the car off the centre
line -- so cloning it teaches the car to swerve. `collect_recovery.py`'s
docstring flags this; this script is the part that acts on it. That is also
the DART formulation (Laskey et al.): train on the EXPERT's action at the
visited state, which is exactly what `log_expert_steer` records.

The recovery frames AFTER a burst, where the PID is driving back to centre,
already agree with the executed action. Those are the valuable ones and are
untouched.

Throttle is recomputed from the expert steering with `collect_recovery.py`'s
own rule, so the label is the complete action the expert would have issued
rather than the expert's steering bolted onto the noise burst's throttle.

Episode order matches `preprocess.py --extra-src` exactly: originals sorted,
then recovery sorted. A mismatch would pair a frame with another frame's
label, so the length check at the end is load-bearing.

Usage:
  python ml/build_expert_labels.py                     # -> proc_aug
  python ml/build_expert_labels.py --out ml/data/proc_aug
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from collect_sim_data import THROTTLE, THROTTLE_CORNER
from episode_writer import load_episode

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "ml" / "data" / "sim" / "train"
REC = REPO / "ml" / "data" / "sim_recovery" / "train"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "ml" / "data" / "proc_aug"))
    args = ap.parse_args()
    out = Path(args.out)
    if not (out / "train_actions.npy").exists():
        raise SystemExit(f"no augmented corpus at {out}. Run preprocess.py "
                         f"--extra-src {REC} --out {out} first.")

    executed = np.load(out / "train_actions.npy")
    chunks, n_fixed, n_rec = [], 0, 0
    for f in sorted(SRC.glob("*.npz")) + sorted(REC.glob("*.npz")):
        ep = load_episode(f)
        act = np.asarray(ep["action"], np.float32).copy()
        if "log_expert_steer" in ep:
            es = np.asarray(ep["log_expert_steer"], np.float32)
            if len(es) != len(act):
                raise SystemExit(f"{f.name}: {len(es)} expert-steer entries "
                                 f"vs {len(act)} actions - misaligned log")
            n_fixed += int((np.abs(act[:, 0] - es) > 1e-6).sum())
            act[:, 0] = es
            # same rule collect_recovery.py used, applied to the expert's steer
            act[:, 1] = np.where(np.abs(es) > 0.5, THROTTLE_CORNER, THROTTLE)
            n_rec += 1
        chunks.append(act)
        del ep

    labels = np.concatenate(chunks)
    if len(labels) != len(executed):
        raise SystemExit(f"built {len(labels)} labels for {len(executed)} "
                         f"frames - episode ordering does not match "
                         f"preprocess.py")

    path = out / "train_actions_expert.npy"
    np.save(path, labels)
    changed = int((np.abs(labels[:, 0] - executed[:, 0]) > 1e-6).sum())
    print(f"{len(labels):,} labels from {len(chunks)} episodes "
          f"({n_rec} recovery)")
    print(f"  steering relabelled on {n_fixed:,} noise frames "
          f"({100*n_fixed/len(labels):.2f}% of corpus)")
    print(f"  differs from executed actions on {changed:,} frames")
    if n_rec and not n_fixed:
        print("WARNING: recovery episodes found but nothing was relabelled - "
              "check that log_expert_steer is populated.")
    print(f"-> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
