"""SIM-POC P2 done-check: prove the corpus is correct, not merely present.

Structural checks are cheap and catch format errors. The one that matters is
ALIGNMENT, and it needs TWO gates, because each covers an axis the other
cannot:

    An off-by-one still trains happily. The loss goes down, the curves look
    fine, and the model learns to predict the wrong action from the current
    frame. Nothing downstream complains.

  1. `check_pid_identity` -- recomputes every action from the logged
     cross-track error. Exact algebra, no thresholds. Covers the ACTION axis.
  2. `check_alignment`    -- measures how far pixel motion lags the steering
     command and requires it to match the measured baseline. Covers the
     IMAGE axis.

Gate 1 alone is not enough, and that was a real defect here, not a
hypothetical: verified 2026-08-06 by rolling the image array +1 and +3 on a
good corpus -- both printed PASS, exit 0, because gate 1 never opens an
image. Only gate 2 catches that. Corrected the same day; see EXPECTED_PEAK_LAG.

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
MIN_PAIRS_PER_EPISODE = 120   # turning frames needed to measure one episode's lag


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
# Pixel motion trails the steering command, because steering sets heading
# RATE, not heading. Measured across 49 episodes 2026-08-06: the lag is -1
# for most episodes and -2 for the fastest ones (mean |dx| 4.23 px vs 3.40,
# mean |steer| 0.655 vs 0.614; the slow holdout track is -1 throughout). So
# the lag is speed-dependent and an exact-equality gate produces FALSE
# FAILURES on legitimately fast driving -- measured, after trying it.
#
# What this gate can therefore prove, and what it cannot:
#   CAN  - any episode outside the plausible band (a >=2-frame offset)
#   CAN  - a whole-corpus roll of 1 frame (the MODE moves off baseline)
#   CANNOT - a 1-frame roll of a MINORITY of episodes, because real physics
#            already produces that exact signature at -2
# The action axis is covered exactly by check_pid_identity; this covers the
# image axis approximately, and the limit is stated rather than papered over.
#
# Re-measure both constants for the real car -- they belong to the control
# rate and platform, not the track.
PLAUSIBLE_LAGS = (-2, -1)
EXPECTED_MODE_LAG = -1
MIN_PEAK_CORR = 0.30   # below this the peak is noise, not a lag measurement


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
    checked, skipped = 0, []
    for idx, ep in enumerate(episodes):
        need = ("log_cte", "log_kp", "log_ki", "log_kd", "log_steer_sign",
                "log_throttle", "log_throttle_corner", "log_steer_limit")
        missing = [k for k in need if k not in ep]
        if missing:
            skipped.append((ep.get("_name", f"episode #{idx}"), missing[0]))
            continue

        cte = np.asarray(ep["log_cte"], np.float64)
        act = np.asarray(ep["action"], np.float64)
        kp, ki, kd = float(ep["log_kp"]), float(ep["log_ki"]), float(ep["log_kd"])
        sign, lim = float(ep["log_steer_sign"]), float(ep["log_steer_limit"])
        thr, thr_c = float(ep["log_throttle"]), float(ep["log_throttle_corner"])

        if len(cte) != len(act):
            failures.append(f"pid-identity: log_cte has {len(cte)} entries, "
                            f"action has {len(act)}")
            continue

        prev, integral = 0.0, 0.0
        max_err = 0.0
        worst = -1
        for i in range(1, len(act)):
            e = cte[i - 1]
            # mirror PIDDriver.act exactly, integral clamp included
            integral = float(np.clip(integral + e, -50.0, 50.0))
            steer = float(np.clip(
                sign * (kp * e + ki * integral + kd * (e - prev)), -lim, lim))
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
    elif skipped:
        # Partial verification reported as success is how a mixed-format
        # corpus (e.g. appended by an older collector via --only) slips
        # through half-checked.
        failures.append(
            f"pid-identity: only {checked}/{len(episodes)} episodes could be "
            f"verified; {len(skipped)} lack metadata, first: "
            f"{skipped[0][0]} (missing {skipped[0][1]}). Recollect them or "
            f"remove them - a partially verified corpus is not verified.")
    else:
        print(f"  exact PID identity     : verified on {checked}/{len(episodes)} "
              f"episode(s), every action reproduced from log_cte")


def check_alignment(episodes: list[dict], failures: list) -> None:
    """THE IMAGE-AXIS GATE: does pixel motion still lag the steering by -1?

    `check_pid_identity` proves action[i] matches log_cte[i-1], but it never
    opens an image -- so it passes a corpus whose IMAGE array has been rolled.
    Verified 2026-08-06: images rolled +1 and +3 both passed it; only a rolled
    ACTION array failed. That is the exact bug the module docstring claims to
    catch, so the image axis needs a gate of its own, and this is it.

    The earlier mistake was gating on peak lag == 0. Steering commands a
    heading RATE, so the visible scene shift genuinely trails the command --
    measured peak is -1 on every known-good corpus collected so far. The fix
    is not to abandon the check but to gate on the MEASURED baseline: rolling
    the image array shifts the peak by exactly the roll (+1 -> -2), so
    equality with EXPECTED_PEAK_LAG is a real test of the image axis.

    The baseline is a property of the CONTROL RATE and platform, not the
    track. If either changes -- notably when this pipeline moves to the real
    car -- re-measure it and update EXPECTED_PEAK_LAG rather than deleting
    the gate.
    """
    checked, weak, bad = [], [], []

    for idx, ep in enumerate(episodes):
        name = ep.get("_name", f"episode #{idx}")
        img, act = ep["image"], ep["action"]
        T = len(img)
        if T < 30:
            weak.append((name, 0))
            continue

        profs = [column_profile(img[t]) for t in range(T)]
        shifts = []
        steer_at_lag = {lag: [] for lag in ALIGN_LAGS}
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
        if n < MIN_PAIRS_PER_EPISODE:
            weak.append((name, n))
            continue

        shifts = np.array(shifts)
        if shifts.std() < 1e-6:
            bad.append((name, None, 0.0, "estimated shifts are constant"))
            continue

        r = {}
        for lag in ALIGN_LAGS:
            s = np.array(steer_at_lag[lag])
            r[lag] = (abs(float(np.corrcoef(shifts, s)[0, 1]))
                      if s.std() > 1e-9 else 0.0)
        peak = max(ALIGN_LAGS, key=lambda k: r[k])

        if r[peak] < MIN_PEAK_CORR:
            bad.append((name, peak, r[peak], "steering barely explains motion"))
        elif peak not in PLAUSIBLE_LAGS:
            bad.append((name, peak, r[peak], "lag outside the plausible band"))
        else:
            checked.append((name, n, peak, r[peak]))

    total = len(episodes)

    for name, peak, rp, why in bad[:5]:
        shown = "n/a" if peak is None else f"{peak:+d}"
        failures.append(
            f"image-axis: {name} peaks at lag {shown} (|r| {rp:.3f}) - {why}. "
            f"Plausible band is {PLAUSIBLE_LAGS}; outside it the image array "
            f"is offset from the actions and the model would learn to predict "
            f"the wrong action.")
    if len(bad) > 5:
        failures.append(f"image-axis: ...and {len(bad) - 5} more episode(s) outside the band")

    if weak:
        failures.append(
            f"image-axis: {len(weak)}/{total} episode(s) had too few turning "
            f"frames to check (need {MIN_PAIRS_PER_EPISODE}); first: "
            f"{weak[0][0]} with {weak[0][1]}. Their image/action alignment is "
            f"UNVERIFIED.")

    if not checked:
        failures.append("image-axis: no episode could be checked at all")
        return

    # Per-episode band check above catches a >=2-frame offset. The corpus MODE
    # catches a whole-corpus 1-frame roll, which shifts every episode together.
    # Neither catches a 1-frame roll of a MINORITY -- real physics already
    # produces that signature at -2 (see the constants above). Stated, not
    # papered over: the action axis is what is covered exactly.
    peaks = [c[2] for c in checked]
    mode = max(set(peaks), key=peaks.count)
    dist = {lag: peaks.count(lag) for lag in sorted(set(peaks))}
    rs = [c[3] for c in checked]
    print(f"  image-axis gate        : {len(checked)}/{total} episodes in band "
          f"{PLAUSIBLE_LAGS}, lag distribution {dist}, mode {mode:+d} "
          f"(|r| {min(rs):.2f}-{max(rs):.2f})")

    if mode != EXPECTED_MODE_LAG:
        failures.append(
            f"image-axis: the corpus lag MODE is {mode:+d}, expected "
            f"{EXPECTED_MODE_LAG:+d} (distribution {dist}). Every episode "
            f"shifting together is the signature of the image array being "
            f"rolled relative to the actions. If the control rate or platform "
            f"changed instead, re-measure EXPECTED_MODE_LAG deliberately.")


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
            try:
                ep = load_episode(f)
            except Exception as exc:                       # noqa: BLE001
                # A half-written npz (collector interrupted, or a reader
                # racing a writer) must not abort the run -- that would leave
                # every remaining episode silently unexamined.
                failures.append(f"{f.name}: could not be read ({type(exc).__name__}: {exc})")
                continue
            ep["_name"] = f.name
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

    # The layout split is P2's whole point, so "could not check it" must be a
    # failure, not silence. --only train produces exactly this state.
    if "train" in split_tracks and "holdout" in split_tracks:
        overlap = split_tracks["train"] & split_tracks["holdout"]
        if overlap:
            failures.append(f"LEAKAGE: track(s) in both train and holdout: {sorted(overlap)}")
        else:
            print(f"  split is disjoint      : no track appears on both sides")
    else:
        failures.append(
            f"split check did NOT run - needs both train/ and holdout/, found "
            f"{sorted(split_tracks) or 'no split directories'}. Passing here "
            f"would imply a layout-split guarantee that was never tested.")

    print(f"\ntotal frames: {total_frames}")
    # An empty corpus must never pass: a done-check that reports success on
    # nothing is how a task gets marked done on nothing.
    if total_frames == 0:
        failures.append("corpus is empty - 0 frames found under " + str(root))
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
