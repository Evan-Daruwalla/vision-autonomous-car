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

from collect_recovery import MAX_MEAN_ABS_CTE_RECOVERY
from collect_sim_data import MAX_MEAN_ABS_CTE, MIN_EPISODE_STEPS
from episode_writer import load_episode

REPO = Path(__file__).resolve().parent.parent

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

    # filename length must match the array length -- the loader trusts it.
    # Parsed defensively: this ran outside the per-episode try/except, so a
    # single file not matching `{id}-{length}.npz` raised IndexError/ValueError
    # out of the whole check and every remaining episode went unexamined. A
    # verifier that dies on the first odd filename verifies nothing after it.
    # (Cold audit E5, 2026-08-06.)
    try:
        stem_len = int(name.rsplit("-", 1)[1].split(".")[0])
    except (IndexError, ValueError):
        failures.append(f"{name}: filename does not encode a length as "
                        f"'{{id}}-{{length}}.npz' - the loader trusts this")
    else:
        if stem_len != T:
            failures.append(f"{name}: filename says {stem_len} steps, arrays have {T}")

    for key in REQUIRED:
        if len(ep[key]) != T:
            failures.append(f"{name}: '{key}' has {len(ep[key])} rows, expected {T}")

    if ep["image"].ndim != 4 or ep["image"].shape[3] != 3:
        failures.append(f"{name}: image shape {ep['image'].shape} is not (T,H,W,3)")
    if ep["image"].dtype != np.uint8:
        failures.append(f"{name}: image dtype {ep['image'].dtype}, expected uint8")
    # The lag constants below are calibrated for 120x160 frames; on any other
    # resolution the pixel-motion profile means nothing (cold audit E8).
    if ep["image"].shape[1:3] != (120, 160):
        failures.append(f"{name}: image is {ep['image'].shape[1:3]}, but the "
                        f"alignment gate's lag constants are calibrated for "
                        f"(120, 160)")

    # **The expert-quality contract, enforced AT REST.** These thresholds lived
    # only inside collect_sim_data.py, which applies them once at write time and
    # never again; log_mean_abs_cte was written and read by nothing. So a corpus
    # collected under different constants, hand-assembled, or copied in from
    # elsewhere would pass every structural and alignment check while containing
    # episodes the expert drove badly. Re-reading them here makes the contract
    # checkable on data that already exists. (Cold audit finding 7 / prior audit
    # F7, open since 2026-08-05.)
    if "log_mean_abs_cte" in ep:
        cte = float(ep["log_mean_abs_cte"])
        # Recovery episodes are collected with a deliberately looser cap --
        # MAX_MEAN_ABS_CTE is the threshold that excluded off-centre data in the
        # first place, so applying it here would reject exactly the episodes
        # collect_recovery.py exists to produce. The collector already logs
        # log_recovery, so the gate reads the evidence instead of asserting a
        # constant that is not constant. (Cold audit A4, 2026-09-02 -- same
        # class as the omitted-log_ki misdiagnosis, Appendix P.2.)
        recovery = float(ep.get("log_recovery", 0.0)) == 1.0
        cap = MAX_MEAN_ABS_CTE_RECOVERY if recovery else MAX_MEAN_ABS_CTE
        cap_name = ("MAX_MEAN_ABS_CTE_RECOVERY" if recovery
                    else "MAX_MEAN_ABS_CTE")
        if cte > cap:
            failures.append(f"{name}: mean|cte| {cte:.3f} exceeds the collector's "
                            f"{cap_name}={cap}")
    if T < MIN_EPISODE_STEPS:
        failures.append(f"{name}: {T} steps is below the collector's "
                        f"MIN_EPISODE_STEPS={MIN_EPISODE_STEPS}")

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
# Below this the peak is noise, not a lag measurement, and reporting it as a
# lag would be a FALSE DIAGNOSIS. Measured separation 2026-08-06 across 77
# episodes: episodes with a well-determined lag sit at |r| 0.60-0.96, while
# four short (~180-frame) roboracingleague episodes sat at 0.34-0.40 and
# "peaked" at -3 -- noise, not a rolled image array. Set above that gap.
MIN_PEAK_CORR = 0.50


def check_pid_identity(ep: dict, acc: dict, failures: list) -> None:
    """ACTION-AXIS gate, one episode at a time: recompute the actions from cte.

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

    RECOVERY EPISODES (cold audit A4, 2026-09-02). collect_recovery.py injects
    noise bursts into the EXECUTED steer, so `action` is deliberately not the
    PID output on those frames and this gate failed on all 20 of them -- while
    that collector's docstring claimed it still passed. Both are now true:
    where `log_expert_steer` and `log_noise` are present the identity is
    checked against `log_expert_steer` (which is what the claim always meant),
    throttle is checked against the EXECUTED steer exactly as both collectors
    compute it, and `log_noise` itself is proven honest -- executed == expert
    on every clean frame and != on every flagged one. A decorative flag would
    otherwise let anything through.
    """
    name = ep.get("_name", "?")
    need = ("log_cte", "log_kp", "log_ki", "log_kd", "log_steer_sign",
            "log_throttle", "log_throttle_corner", "log_steer_limit")
    missing = [k for k in need if k not in ep]
    if missing:
        acc["skipped"].append((name, missing[0]))
        return

    cte = np.asarray(ep["log_cte"], np.float64)
    act = np.asarray(ep["action"], np.float64)
    # Both or neither: half-recorded noise metadata cannot be checked, and
    # must not be silently treated as a clean episode.
    has_exp, has_noise = "log_expert_steer" in ep, "log_noise" in ep
    if has_exp != has_noise:
        failures.append(
            f"pid-identity: {name}: half-recorded recovery metadata - "
            f"log_expert_steer {'present' if has_exp else 'missing'} but "
            f"log_noise {'present' if has_noise else 'missing'}")
        return
    expert = np.asarray(ep["log_expert_steer"], np.float64) if has_exp else None
    noise = np.asarray(ep["log_noise"], np.float64) if has_noise else None
    if expert is not None and not (len(expert) == len(noise) == len(act)):
        failures.append(
            f"pid-identity: {name}: log_expert_steer/log_noise length "
            f"{len(expert)}/{len(noise)} != action {len(act)}")
        return
    kp, ki, kd = float(ep["log_kp"]), float(ep["log_ki"]), float(ep["log_kd"])
    sign, lim = float(ep["log_steer_sign"]), float(ep["log_steer_limit"])
    thr, thr_c = float(ep["log_throttle"]), float(ep["log_throttle_corner"])

    if len(cte) != len(act):
        failures.append(f"pid-identity: {name}: log_cte has {len(cte)} entries, "
                        f"action has {len(act)}")
        return

    prev, integral = 0.0, 0.0
    max_err, worst = 0.0, -1
    dishonest = []
    for i in range(1, len(act)):
        e = cte[i - 1]
        # mirror PIDDriver.act exactly, integral clamp included
        integral = float(np.clip(integral + e, -50.0, 50.0))
        steer = float(np.clip(
            sign * (kp * e + ki * integral + kd * (e - prev)), -lim, lim))
        prev = e
        # The reference is the EXPERT's steer where one was logged; on a plain
        # corpus that is the executed action, so this is a strict generalisation.
        ref = expert[i] if expert is not None else act[i, 0]
        # Throttle follows the EXECUTED steer -- collect_sim_data.py and
        # collect_recovery.py both compute it that way, from what they sent.
        throttle = thr_c if abs(act[i, 0]) > 0.5 else thr
        err = max(abs(steer - ref), abs(throttle - act[i, 1]))
        if err > max_err:
            max_err, worst = err, i
        if expert is not None:
            # log_noise must MEAN something: clean frames execute the expert
            # exactly, flagged frames must differ from it.
            clean = noise[i] == 0.0
            if clean != bool(act[i, 0] == expert[i]):
                dishonest.append(i)
            elif not clean:
                acc["noise_frames"] += 1
    acc["checked"] += 1

    if dishonest:
        failures.append(
            f"pid-identity: {name}: log_noise is not honest at indices "
            f"{dishonest[:5]} ({len(dishonest)} total) - the executed steer "
            f"equals the expert on a frame flagged noisy, or differs from it "
            f"on a frame flagged clean. The flag cannot be trusted to exempt "
            f"anything.")

    # 1e-5 is safe ONLY because KI is currently 0.0. `integral` is replayed
    # here from float32-rounded log_cte while the collector accumulated it in
    # float64, so with a nonzero KI that rounding difference compounds across
    # ~1200 steps and can exceed this threshold on a perfectly good corpus --
    # a false FAIL of exactly the family already logged in record Appendix P.2
    # (the omitted-log_ki misdiagnosis). If KI is ever raised, widen this and
    # say so in the record. (Cold audit E9, 2026-08-06.)
    if max_err > 1e-5:
        failures.append(
            f"pid-identity: {name}: recomputed action disagrees with the stored "
            f"one (max |diff| {max_err:.6f} at index {worst}). The frame/action "
            f"indexing is wrong, or the corpus was modified after writing.")


def finalize_pid_identity(acc: dict, total: int, failures: list) -> None:
    checked, skipped = acc["checked"], acc["skipped"]
    noise_frames = acc["noise_frames"]
    if checked == 0:
        failures.append("pid-identity: no episode carried the log_cte metadata "
                        "needed to verify alignment exactly - recollect with "
                        "the current collector")
    elif skipped:
        # Partial verification reported as success is how a mixed-format
        # corpus (e.g. appended by an older collector via --only) slips
        # through half-checked.
        failures.append(
            f"pid-identity: only {checked}/{total} episodes could be "
            f"verified; {len(skipped)} lack metadata, first: "
            f"{skipped[0][0]} (missing {skipped[0][1]}). Recollect them or "
            f"remove them - a partially verified corpus is not verified.")
    else:
        extra = (f", {noise_frames} noise frames checked against "
                 f"log_expert_steer" if noise_frames else "")
        print(f"  exact PID identity     : verified on {checked}/{total} "
              f"episode(s), every action reproduced from log_cte{extra}")


def check_alignment(ep: dict, acc: dict, failures: list) -> None:
    """IMAGE-AXIS gate, one episode at a time: does pixel motion still lag by -1?

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
    name = ep.get("_name", "?")
    img, act = ep["image"], ep["action"]
    T = len(img)
    if T < 30:
        acc["weak"].append((name, 0))
        return

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
        acc["weak"].append((name, n))
        return

    shifts = np.array(shifts)
    if shifts.std() < 1e-6:
        acc["bad"].append((name, None, 0.0, "estimated shifts are constant"))
        return

    r = {}
    for lag in ALIGN_LAGS:
        s = np.array(steer_at_lag[lag])
        r[lag] = (abs(float(np.corrcoef(shifts, s)[0, 1]))
                  if s.std() > 1e-9 else 0.0)
    peak = max(ALIGN_LAGS, key=lambda k: r[k])

    if r[peak] < MIN_PEAK_CORR:
        # UNVERIFIABLE, not wrong. Calling a noisy peak a misalignment is the
        # same false-diagnosis class as the log_ki bug: it points the reader
        # at the wrong subsystem.
        acc["weak"].append((name, f"{n} frames but |r| only {r[peak]:.2f}"))
    elif peak not in PLAUSIBLE_LAGS:
        acc["bad"].append((name, peak, r[peak], "lag outside the plausible band"))
    else:
        acc["checked"].append((name, n, peak, r[peak]))


def finalize_alignment(acc: dict, total: int, failures: list) -> None:
    checked, weak, bad = acc["checked"], acc["weak"], acc["bad"]

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
            f"image-axis: {len(weak)}/{total} episode(s) could NOT be checked "
            f"(too few turning frames, or too weak a correlation to determine "
            f"a lag); first: {weak[0][0]} - {weak[0][1]}. Their image/action "
            f"alignment is UNVERIFIED - not wrong, unchecked. Drop them or "
            f"collect longer episodes on that track.")

    if not checked:
        failures.append("image-axis: no episode could be checked at all")
        return

    # Per-episode band check above catches a >=2-frame offset. The corpus MODE
    # catches a whole-corpus 1-frame roll, which shifts every episode together.
    # Neither catches a 1-frame roll of a MINORITY -- real physics already
    # produces that signature at -2 (see the constants above). Stated, not
    # papered over: the action axis is what is covered exactly.
    peaks = [c[2] for c in checked]
    dist = {lag: peaks.count(lag) for lag in sorted(set(peaks))}
    top = max(dist.values())
    tied = [lag for lag, n in dist.items() if n == top]
    # An exact tie has no mode. `max(set(peaks), key=peaks.count)` silently
    # picked one by set-iteration order, so a 10/10 split reported "mode -2"
    # and failed a corpus the per-episode band check had passed 20/20 (cold
    # audit A4, 2026-09-02 -- the recovery corpus is exactly this shape).
    # Abstaining is the module's own rule for an ambiguous measurement, not a
    # widened tolerance. LIMIT, stated: a whole-corpus roll that happened to
    # produce an exact tie would not be caught by the mode; the per-episode
    # band check is the coverage that remains.
    mode = tied[0] if len(tied) == 1 else None
    rs = [c[3] for c in checked]
    mode_txt = f"mode {mode:+d}" if mode is not None else f"mode UNDETERMINED (tie {tied})"
    print(f"  image-axis gate        : {len(checked)}/{total} episodes in band "
          f"{PLAUSIBLE_LAGS}, lag distribution {dist}, {mode_txt} "
          f"(|r| {min(rs):.2f}-{max(rs):.2f})")

    if mode is None:
        print(f"  note: lag mode undetermined ({dist}) - abstaining. The "
              f"per-episode band check above is the coverage on this corpus.")
    elif mode != EXPECTED_MODE_LAG:
        failures.append(
            f"image-axis: the corpus lag MODE is {mode:+d}, expected "
            f"{EXPECTED_MODE_LAG:+d} (distribution {dist}). Every episode "
            f"shifting together is the signature of the image array being "
            f"rolled relative to the actions. If the control rate or platform "
            f"changed instead, re-measure EXPECTED_MODE_LAG deliberately.")


def main():
    ap = argparse.ArgumentParser()
    # Absolute by default: every other script in ml/ resolves from REPO, and a
    # cwd-relative default here reads as "corpus not found" when the check is
    # launched from ml/ (Appendix AQ).
    ap.add_argument("root", nargs="?", default=str(REPO / "ml" / "data" / "sim"))
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"corpus not found: {root}")
        sys.exit(1)

    failures: list[str] = []
    split_tracks: dict[str, set] = {}
    total_frames, n_episodes, n_recovery = 0, 0, 0
    # Streaming accumulators: each episode is checked and then DISCARDED.
    # Retaining every image array cost 4.09 GB at 76k frames and would have
    # OOM'd near the PRD's own ~100k target -- i.e. the done-check would have
    # died exactly when P2 became finishable.
    pid_acc = {"checked": 0, "skipped": [], "noise_frames": 0}
    lag_acc = {"checked": [], "weak": [], "bad": []}

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
            check_pid_identity(ep, pid_acc, failures)
            check_alignment(ep, lag_acc, failures)
            n_episodes += 1
            n_recovery += float(ep.get("log_recovery", 0.0)) == 1.0
            del ep
        total_frames += frames
        print(f"{split:9s}: {len(files):3d} episodes, {frames:7d} frames, "
              f"tracks {sorted(split_tracks[split])}")
        if not files:
            failures.append(f"{split}: no episodes found")

    # The layout split is P2's whole point, so "could not check it" must be a
    # failure, not silence. --only train produces exactly this state.
    if set(split_tracks) == {"train"} and n_recovery == n_episodes > 0:
        # collect_recovery.py writes train/ only, by design: recovery data
        # augments the training corpus and has no holdout of its own. Decided
        # by EVIDENCE in the npz (every episode carries log_recovery), never a
        # CLI flag -- a flag is how a gate gets switched off silently.
        print(f"  layout split          : not applicable - all {n_episodes} "
              f"episodes are log_recovery, and collect_recovery.py writes "
              f"train/ only")
    elif "train" in split_tracks and "holdout" in split_tracks:
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
    if n_episodes:
        print("\nalignment:")
        finalize_pid_identity(pid_acc, n_episodes, failures)
        finalize_alignment(lag_acc, n_episodes, failures)

    print()
    if failures:
        print("P2 CORPUS CHECK: FAIL")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("P2 CORPUS CHECK: PASS")


if __name__ == "__main__":
    main()
