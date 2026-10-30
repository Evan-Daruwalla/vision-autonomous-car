"""Check a directory of REAL-car episodes before any training touches them.

WHY a separate checker: ml/verify_corpus.py's two alignment gates are SIM-ONLY
(they re-derive actions from the sim's logged cross-track error), and its
150-step minimum is the sim collector's rule. Real episodes come from
pi/recorder.py and carry their own evidence: the command actually sent after
each frame (log_cmd_next) and sensor timestamps (log_t_frame_ns). This file
checks those, so a broken recording is caught at the bench, not after an
afternoon of training on it.

Checks, per episode (contract = .claude/project-memory/data.md, "Real-car
episodes"):
  FAIL  verify_corpus.check_structure problems (keys, lengths, filename, image
        shape/dtype) other than the sim length rule
  FAIL  missing log_cmd_next, or action[k] != log_cmd_next[k-1]/100 (the shift)
  FAIL  steer/throttle commands outside -100..100
  FAIL  recorded with fake hardware (log_fake or log_fake_uno true in meta)
  WARN  shorter than REAL_MIN_STEPS (the trainer skips these)
  WARN  frame gaps > GAP_MS in log_t_frame_ns (dropped frames), reported as %
  WARN  steer saturated (|cmd| >= 95) on more than SAT_WARN of frames
Exit 1 if any FAIL. Prints one summary line per session (parent directory).

    ./.venv/Scripts/python.exe ml/verify_real.py <dir of npz>
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from episode_writer import load_episode  # noqa: E402

from bc_real import REAL_MIN_STEPS  # noqa: E402  single source: the trainer's skip rule
GAP_MS = 75.0                # 1.5 frame periods at 20 Hz
SAT_WARN = 0.30


def _structure(ep: dict, path: Path) -> list[str]:
    """verify_corpus.check_structure minus its sim-only minimum-length rule."""
    from verify_corpus import check_structure
    out: list[str] = []
    check_structure(ep, path, out)
    return [f for f in out if "MIN_EPISODE_STEPS" not in f]


def check_episode(ep: dict, path: Path) -> tuple[list[str], list[str], dict]:
    fails = _structure(ep, path)
    warns: list[str] = []
    T = len(ep.get("reward", []))
    stats = {"T": T, "gap_pct": 0.0, "sat_pct": 0.0}
    name = path.name
    if (bool(np.asarray(ep.get("log_fake", False)))
            or bool(np.asarray(ep.get("log_fake_uno", False)))):
        fails.append(f"{name}: recorded with fake hardware (log_fake/log_fake_uno) "
                     "- never train on it")
    if "log_cmd_next" not in ep:
        fails.append(f"{name}: no log_cmd_next - not a pi/recorder.py episode")
        return fails, warns, stats
    cmd = ep["log_cmd_next"].astype(np.int32)
    if cmd.shape != (T, 2):
        fails.append(f"{name}: log_cmd_next shape {cmd.shape}, expected ({T}, 2)")
        return fails, warns, stats
    if np.abs(cmd).max(initial=0) > 100:
        fails.append(f"{name}: a command is outside -100..100")
    act = ep["action"]
    if T and not np.allclose(act[0], 0.0):
        fails.append(f"{name}: action[0] is not zeros")
    if T > 1 and not np.allclose(act[1:], cmd[:-1] / 100.0, atol=1e-6):
        bad = int(np.flatnonzero(~np.isclose(act[1:], cmd[:-1] / 100.0,
                                             atol=1e-6).all(axis=1))[0]) + 1
        fails.append(f"{name}: action[k] != log_cmd_next[k-1]/100 first at k={bad}")
    if T < REAL_MIN_STEPS:
        warns.append(f"{name}: {T} steps < REAL_MIN_STEPS={REAL_MIN_STEPS} (trainer skips it)")
    if "log_t_frame_ns" in ep and T > 1:
        gaps = np.diff(ep["log_t_frame_ns"].astype(np.int64)) / 1e6
        if (gaps <= 0).any():
            fails.append(f"{name}: frame timestamps not strictly increasing")
        stats["gap_pct"] = float((gaps > GAP_MS).mean() * 100)
        if stats["gap_pct"] > 0:
            warns.append(f"{name}: {stats['gap_pct']:.1f}% of frame gaps > {GAP_MS:.0f} ms")
    if T:
        stats["sat_pct"] = float((np.abs(cmd[:, 0]) >= 95).mean() * 100)
        if stats["sat_pct"] > SAT_WARN * 100:
            warns.append(f"{name}: steer saturated on {stats['sat_pct']:.0f}% of frames")
    return fails, warns, stats


def verify_dir(root: Path) -> int:
    if not str(root).strip() or not root.is_dir():
        print(f"verify_real: error: {str(root)!r} is not an existing directory")
        return 2
    files = sorted(root.rglob("*.npz"))
    if not files:
        print(f"verify_real: no .npz under {root}")
        return 1
    fails_all: list[str] = []
    per_session: dict = collections.defaultdict(lambda: {"eps": 0, "frames": 0, "warn": 0})
    for f in files:
        try:
            ep = load_episode(f)
        except Exception as e:  # unreadable file is a contract failure, not a crash
            fails_all.append(f"{f.name}: cannot load ({e})")
            continue
        fails, warns, st = check_episode(ep, f)
        fails_all += fails
        s = per_session[f.parent.name]
        s["eps"] += 1
        s["frames"] += st["T"]
        s["warn"] += len(warns)
        for w in warns:
            print("  WARN " + w)
    for f in fails_all:
        print("  FAIL " + f)
    for name, s in sorted(per_session.items()):
        print(f"session {name}: {s['eps']} episodes, {s['frames']} frames "
              f"({s['frames'] / 20 / 60:.1f} min at 20 Hz), {s['warn']} warnings")
    print(f"verify_real: {len(files)} files, {len(fails_all)} failures")
    return 1 if fails_all else 0


def self_check() -> None:
    import tempfile
    from episode_writer import EpisodeWriter

    def write(d: Path, n: int, shift_ok: bool = True, gaps_ms: float = 50.0,
              meta: dict | None = None) -> Path:
        w = EpisodeWriter(d)
        rng = np.random.default_rng(n)
        cmds = np.stack([rng.integers(-60, 61, n), np.full(n, 20)], 1).astype(np.int8)
        img = lambda: rng.integers(0, 255, (120, 160, 3), dtype=np.uint8)
        w.add_reset(img(), action_dim=2)
        for k in range(1, n):
            a = cmds[k - 1] / 100.0 if shift_ok else cmds[k] / 100.0
            w.add_step(img(), a, 0.0, False, k == n - 1)
        t = (np.arange(n) * gaps_ms * 1e6).astype(np.int64)
        return w.save(meta=meta, frame_logs={"log_cmd_next": cmds, "log_t_frame_ns": t})

    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "s1"
        write(good, 60)
        assert verify_dir(good) == 0, "a correct episode failed"
        bad = Path(td) / "s2"
        p = write(bad, 60, shift_ok=False)            # off-by-one: must FAIL
        f, _, _ = check_episode(load_episode(p), p)
        assert any("log_cmd_next[k-1]" in x for x in f), f
        assert verify_dir(bad) == 1
        short = Path(td) / "s3"
        p = write(short, 20)                          # short: WARN, not FAIL
        f, w, _ = check_episode(load_episode(p), p)
        assert not f and any("REAL_MIN_STEPS" in x for x in w), (f, w)
        slow = Path(td) / "s4"
        p = write(slow, 60, gaps_ms=100.0)            # every gap 100 ms: dropped frames
        _, w, st = check_episode(load_episode(p), p)
        assert st["gap_pct"] == 100.0 and any("frame gaps" in x for x in w), (st, w)
        p = write(Path(td) / "s5", 60, meta={"fake_uno": True})   # fake hardware: FAIL
        f, _, _ = check_episode(load_episode(p), p)
        assert any("fake hardware" in x for x in f), f
        assert verify_dir(Path(td) / "s5") == 1
        write(Path(td) / "s6", 60, meta={"fake": False, "fake_uno": False})
        assert verify_dir(Path(td) / "s6") == 0, "real-hardware flags falsely failed"
        assert verify_dir(Path(td) / "does_not_exist") == 2, "missing root must exit 2"
        assert main([""]) == 2, "empty root arg must exit 2"
    print("verify_real self_check: PASS")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)
    if a.root == "":
        print("verify_real: error: empty root path")
        return 2
    if a.self_check or a.root is None:
        self_check()
        return 0
    return verify_dir(Path(a.root))


if __name__ == "__main__":
    sys.exit(main())
