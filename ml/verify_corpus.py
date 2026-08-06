"""SIM-POC P2 done-check: prove the corpus is correct, not merely present.

Structural checks are cheap and catch format errors. The one that matters is
ALIGNMENT, and it is deliberately not a structural check:

    An off-by-one between frames and actions still trains happily. The loss
    goes down, the curves look fine, and the model learns to predict the
    PREVIOUS action from the current frame. Nothing downstream complains.

So alignment is re-derived from the pixels themselves. When the car steers,
the scene shifts horizontally between consecutive frames; that shift is
estimated by cross-correlating a band of road ahead, independently of
anything the writer recorded. If `action[i]` really is the action that
produced `image[i]`, it must correlate with the shift from `image[i-1]` to
`image[i]` MORE strongly than `action[i+1]` does. That comparison is the
test, and it can fail -- which is the point.

Usage:  python ml/verify_corpus.py ml/data/sim_smoke
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from episode_writer import load_episode

REQUIRED = ["image", "action", "reward", "discount",
            "is_first", "is_last", "is_terminal"]

BAND = (60, 95)        # image rows to profile: road ahead, above the bumper
MAX_SHIFT = 14         # px of horizontal search either way
MIN_PAIRS = 200        # need enough samples for the correlation to mean anything


def column_profile(img: np.ndarray) -> np.ndarray:
    """1-D horizontal intensity profile of the road band, mean-centred."""
    band = img[BAND[0]:BAND[1], :, :].astype(np.float32).mean(axis=2)
    prof = band.mean(axis=0)
    return prof - prof.mean()


def estimate_shift(prev: np.ndarray, cur: np.ndarray) -> float:
    """Horizontal shift (px) that best maps prev onto cur, by NCC."""
    best_dx, best_score = 0, -np.inf
    n = prev.shape[0]
    for dx in range(-MAX_SHIFT, MAX_SHIFT + 1):
        # overlap region after shifting prev by dx
        if dx >= 0:
            a, b = prev[: n - dx], cur[dx:]
        else:
            a, b = prev[-dx:], cur[: n + dx]
        if a.size < n // 2:
            continue
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom < 1e-6:
            continue
        score = float(np.dot(a, b) / denom)
        if score > best_score:
            best_score, best_dx = score, dx
    return float(best_dx)


def check_structure(ep: dict, path: Path, failures: list) -> None:
    name = path.name
    for key in REQUIRED:
        if key not in ep:
            failures.append(f"{name}: missing key '{key}'")
            return

    T = len(ep["reward"])

    # filename length must match the array length -- the loader trusts it
    stem_len = int(name.rsplit("-", 1)[1].split(".")[0])
    if stem_len != T:
        failures.append(f"{name}: filename says {stem_len} steps, arrays have {T}")

    for key in REQUIRED:
        if len(ep[key]) != T:
            failures.append(f"{name}: '{key}' has {len(ep[key])} rows, expected {T}")

    if ep["image"].ndim != 4 or ep["image"].shape[3] != 3:
        failures.append(f"{name}: image shape {ep['image'].shape} is not (T,H,W,3)")
    if ep["image"].dtype != np.uint8:
        failures.append(f"{name}: image dtype {ep['image'].dtype}, expected uint8")

    # episode boundary flags
    if not ep["is_first"][0] or ep["is_first"][1:].any():
        failures.append(f"{name}: is_first must be True at t=0 only")
    if not ep["is_last"][-1] or ep["is_last"][:-1].any():
        failures.append(f"{name}: is_last must be True at the final step only")

    # t=0 has no preceding action
    if np.abs(ep["action"][0]).sum() != 0:
        failures.append(f"{name}: action[0] must be zeros (no action caused the reset frame)")
    if ep["reward"][0] != 0:
        failures.append(f"{name}: reward[0] must be 0")

    # discount encodes "does a future exist", not "did we stop looking"
    bad = np.where((ep["discount"] == 0) != ep["is_terminal"])[0]
    if bad.size:
        failures.append(f"{name}: discount==0 and is_terminal disagree at {bad[:5].tolist()}")

    for key in ("action", "reward", "discount"):
        if not np.isfinite(ep[key]).all():
            failures.append(f"{name}: '{key}' contains NaN or inf")

    steer = ep["action"][:, 0]
    if np.abs(steer).max() > 1.0 + 1e-6:
        failures.append(f"{name}: steering out of [-1,1]: max |s| = {np.abs(steer).max():.3f}")


ALIGN_LAGS = (-3, -2, -1, 0, 1, 2)


def check_pid_identity(episodes: list[dict], failures: list) -> None:
    """THE alignment gate: recompute every action from the logged cte.

    The expert driver is a deterministic function of cross-track error, and
    `log_cte[i]` was recorded at the same instant as `image[i]`. So

        action[i] == clip(sign * (kp*e + kd*(e - e_prev)))
        where e = cte[i-1], e_prev = cte[i-2]

    is an exact algebraic identity, with no thresholds and no assumptions
    about vehicle dynamics. Rolling the action array by even one step breaks
    it immediately, which is precisely the bug class this exists to catch.

    (The pixel-motion check below cannot do this job: steering sets heading
    RATE, so the visible scene shift genuinely lags the command by about a
    step. Measured 2026-08-05 -- on a known-good corpus the shift correlates
    better with action[i-1] than action[i]. That is physics, not a bug, and
    it makes peak-correlation-at-lag-zero the wrong test.)
    """
    checked = 0
    for ep in episodes:
        need = ("log_cte", "log_kp", "log_kd", "log_steer_sign",
                "log_throttle", "log_throttle_corner", "log_steer_limit")
        if any(k not in ep for k in need):
            continue

        cte = np.asarray(ep["log_cte"], np.float64)
        act = np.asarray(ep["action"], np.float64)
        kp, kd = float(ep["log_kp"]), float(ep["log_kd"])
        sign, lim = float(ep["log_steer_sign"]), float(ep["log_steer_limit"])
        thr, thr_c = float(ep["log_throttle"]), float(ep["log_throttle_corner"])

        if len(cte) != len(act):
            failures.append(f"pid-identity: log_cte has {len(cte)} entries, "
                            f"action has {len(act)}")
            continue

        prev = 0.0
        max_err = 0.0
        worst = -1
        for i in range(1, len(act)):
            e = cte[i - 1]
            steer = float(np.clip(sign * (kp * e + kd * (e - prev)), -lim, lim))
            prev = e
            throttle = thr_c if abs(steer) > 0.5 else thr
            err = max(abs(steer - act[i, 0]), abs(throttle - act[i, 1]))
            if err > max_err:
                max_err, worst = err, i
        checked += 1

        if max_err > 1e-5:
            failures.append(
                f"pid-identity: recomputed action disagrees with the stored one "
                f"(max |diff| {max_err:.6f} at index {worst}). The frame/action "
                f"indexing is wrong, or the corpus was modified after writing.")

    if checked == 0:
        failures.append("pid-identity: no episode carried the log_cte metadata "
                        "needed to verify alignment exactly - recollect with "
                        "the current collector")
    else:
        print(f"  exact PID identity     : verified on {checked} episode(s), "
              f"every action reproduced from log_cte")


def check_alignment(episodes: list[dict], failures: list) -> None:
    """INFORMATIONAL: pixel-motion lag profile. Not a gate -- see above."""
    shifts = []
    steer_at_lag = {lag: [] for lag in ALIGN_LAGS}

    for ep in episodes:
        img, act = ep["image"], ep["action"]
        T = len(img)
        if T < 30:
            continue
        profs = [column_profile(img[t]) for t in range(T)]
        lo, hi = 1 - min(ALIGN_LAGS), T - 1 - max(ALIGN_LAGS)
        for t in range(lo, hi):
            # only sample frames where the car is actually turning; straight
            # driving carries no alignment information either way
            if abs(act[t, 0]) < 0.06:
                continue
            shifts.append(estimate_shift(profs[t - 1], profs[t]))
            for lag in ALIGN_LAGS:
                steer_at_lag[lag].append(act[t + lag, 0])

    n = len(shifts)
    if n < MIN_PAIRS:
        print(f"  pixel-motion profile   : skipped, only {n} turning frames")
        return

    shifts = np.array(shifts)
    if shifts.std() < 1e-6:
        failures.append("pixel-motion: estimated shifts are constant - "
                        "the shift estimator found no motion, check BAND rows")
        return

    r = {}
    for lag in ALIGN_LAGS:
        s = np.array(steer_at_lag[lag])
        r[lag] = abs(float(np.corrcoef(shifts, s)[0, 1])) if s.std() > 1e-9 else 0.0

    best = max(ALIGN_LAGS, key=lambda k: r[k])
    profile = "  ".join(f"{lag:+d}:{r[lag]:.2f}" for lag in ALIGN_LAGS)
    print(f"  pixel-motion profile   : {profile}   (n={n}, peak {best:+d})")

    # Not a pass/fail gate -- a peak at -1 is the expected physical lag.
    # It IS worth shouting about if steering barely explains motion at all,
    # because that means the corpus has no usable steering signal in it.
    if max(r.values()) < 0.15:
        failures.append(
            f"pixel-motion: steering explains almost no image motion "
            f"(best |r| = {max(r.values()):.3f} at lag {best:+d}). The corpus "
            "may be static, or the shift estimator is reading the wrong rows.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="ml/data/sim")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"corpus not found: {root}")
        sys.exit(1)

    failures: list[str] = []
    split_tracks: dict[str, set] = {}
    loaded, total_frames = [], 0

    for split_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        files = sorted(split_dir.glob("*.npz"))
        split = split_dir.name
        split_tracks[split] = set()
        frames = 0
        for f in files:
            ep = load_episode(f)
            check_structure(ep, f, failures)
            frames += len(ep["reward"])
            if "log_track" in ep:
                split_tracks[split].add(str(ep["log_track"]))
            loaded.append(ep)
        total_frames += frames
        print(f"{split:9s}: {len(files):3d} episodes, {frames:7d} frames, "
              f"tracks {sorted(split_tracks[split])}")
        if not files:
            failures.append(f"{split}: no episodes found")

    # the whole point of the split: no track may appear on both sides
    if "train" in split_tracks and "holdout" in split_tracks:
        overlap = split_tracks["train"] & split_tracks["holdout"]
        if overlap:
            failures.append(f"LEAKAGE: track(s) in both train and holdout: {sorted(overlap)}")
        else:
            print(f"  split is disjoint      : no track appears on both sides")

    print(f"\ntotal frames: {total_frames}")
    if loaded:
        print("\nalignment:")
        check_pid_identity(loaded, failures)
        check_alignment(loaded, failures)

    print()
    if failures:
        print("P2 CORPUS CHECK: FAIL")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("P2 CORPUS CHECK: PASS")


if __name__ == "__main__":
    main()
