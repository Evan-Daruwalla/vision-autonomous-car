"""Episode recorder for the Pi control loop: buffer frames + commands, save one npz.

WHY the shift: at control tick k the loop captures image_k and THEN sends
cmd_k. The episode contract (.claude/project-memory/data.md) needs
action[i] = the action that produced image[i], so action[0] = zeros and
action[k] = cmd_{k-1}/100 for k >= 1. The unshifted commands are kept as
`log_cmd_next` so the alignment can be re-derived later.

Everything is buffered in Python lists and written once in stop() through
`ml/episode_writer.py`, so the control loop never does disk I/O per tick.
# shortcut: frames are held in RAM, ~1.15 MB/s at 160x120x3 and 20 Hz (~70 MB
# per minute); fine for lap-length episodes on a 4 GB Pi 5. Upgrade trigger:
# episodes longer than ~10 min -> write chunks as they fill.
Units: action = [steer/100, throttle/100] float32 from int8 percentages.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import json
import threading
import time

import numpy as np

EP = Path(__file__).resolve().parent.parent / "ml"
if str(EP) not in sys.path:
    sys.path.insert(0, str(EP))

from episode_writer import EpisodeWriter  # noqa: E402

_TELEM_KEYS = ("ticks", "status", "t_frame_ns", "t_cmd_ns", "loop_dt")
# optional per-frame keys and their default: mode 0 = manual, 1 = autopilot
# (added 2026-10-29 so autopilot laps can be relabelled later, DAgger-style)
_OPTIONAL_KEYS = {"mode": 0}


class Recorder:
    """Buffer one episode at a time; write it on stop()."""

    def __init__(self, root: str | Path, session: str | None = None,
                 meta: dict | None = None):
        self.session = session or time.strftime("%Y%m%d-%H%M%S")
        self.directory = Path(root).expanduser() / self.session
        self.meta = dict(meta or {})
        self._recording = False
        self._clear()

    def _clear(self) -> None:
        self._images: list[np.ndarray] = []
        self._cmds: list[tuple[int, int]] = []
        self._telem: list[dict] = []

    @property
    def recording(self) -> bool:
        return self._recording

    @property
    def steps(self) -> int:
        return len(self._images)

    def start(self) -> None:
        if self._recording:
            raise RuntimeError("already recording")
        self._clear()
        self._recording = True

    def add(self, image: np.ndarray, cmd_sent: tuple[int, int],
            telem: dict) -> None:
        if not self._recording:
            raise RuntimeError("add() while not recording")
        if (not isinstance(image, np.ndarray) or image.dtype != np.uint8
                or image.shape != (120, 160, 3)):
            raise ValueError(
                f"image must be uint8 (120, 160, 3), got "
                f"{getattr(image, 'dtype', None)} {getattr(image, 'shape', None)}")
        missing = [k for k in _TELEM_KEYS if k not in telem]
        if missing:
            raise ValueError(f"telem missing keys: {missing}")
        self._images.append(image)
        self._cmds.append((int(cmd_sent[0]), int(cmd_sent[1])))
        row = {k: int(telem[k]) for k in _TELEM_KEYS}
        row.update({k: int(telem.get(k, d)) for k, d in _OPTIONAL_KEYS.items()})
        self._telem.append(row)

    def stop(self, crash: bool = False) -> Path | None:
        if not self._recording:
            raise RuntimeError("stop() while not recording")
        self._recording = False
        try:
            T = len(self._images)
            if T < 2:
                return None
            w = EpisodeWriter(self.directory)
            w.add_reset(self._images[0], action_dim=2)
            for k in range(1, T):
                last = k == T - 1
                steer, thr = self._cmds[k - 1]
                w.add_step(self._images[k],
                           action=[steer / 100.0, thr / 100.0],
                           reward=0.0,
                           terminated=bool(crash and last),
                           truncated=bool((not crash) and last))
            meta = {}
            for key, value in {**self.meta, "session": self.session}.items():
                meta[key] = (json.dumps(value)
                             if isinstance(value, (dict, list, tuple)) else value)
            col = lambda k, dt: np.array([t[k] for t in self._telem], dt)
            frame_logs = {
                "log_cmd_next": np.array(self._cmds, np.int8).reshape(T, 2),
                "log_ticks": col("ticks", np.int32),
                "log_status": col("status", np.uint8),
                "log_t_frame_ns": col("t_frame_ns", np.int64),
                "log_t_cmd_ns": col("t_cmd_ns", np.int64),
                "log_loop_dt": col("loop_dt", np.uint8),
                "log_mode": col("mode", np.uint8),
            }
            return w.save(meta=meta, frame_logs=frame_logs)
        finally:
            self._clear()

    def stop_background(self, crash: bool = False, on_saved=None) -> threading.Thread:
        """End the episode NOW, write it on a worker thread.

        WHY: savez_compressed of a few-minute episode takes seconds; done on the
        20 Hz control thread (or under teleop's lock) it stalls the command
        stream past the Uno's 150 ms watchdog. The buffers are handed to a
        detached Recorder, so this one can start() again at once.
        on_saved(path_or_None) is called from the worker thread.
        """
        if not self._recording:
            raise RuntimeError("stop() while not recording")
        job = Recorder(self.directory.parent, session=self.session, meta=self.meta)
        job._images, job._cmds, job._telem = self._images, self._cmds, self._telem
        job._recording = True
        self._recording = False
        self._images, self._cmds, self._telem = [], [], []

        def work() -> None:
            path = job.stop(crash=crash)
            if on_saved is not None:
                on_saved(path)

        t = threading.Thread(target=work, daemon=False)
        t.start()
        return t


def self_check() -> None:
    import tempfile
    from camera import fake_frame
    from episode_writer import load_episode
    import verify_corpus

    with tempfile.TemporaryDirectory() as td:
        rec = Recorder(td, session="sc", meta={"car": "test", "cfg": {"a": 1}})
        try:
            rec.add(np.zeros((120, 160, 3), np.uint8), (0, 0), {})
        except RuntimeError:
            pass
        else:
            raise AssertionError("add() accepted while not recording")

        def run(n: int, crash: bool) -> Path | None:
            rec.start()
            assert rec.recording
            for k in range(n):
                t = k * 50_000_000
                rec.add(fake_frame(k), (k % 201 - 100, (k * 7) % 201 - 100),
                        {"ticks": k, "status": 1, "t_frame_ns": t,
                         "t_cmd_ns": t + 1000, "loop_dt": 50})
            assert rec.steps == n
            return rec.stop(crash=crash)

        path = run(150, False)
        assert path is not None and path.exists()
        ep = load_episode(path)
        assert len(ep["reward"]) == 150
        assert np.allclose(ep["action"][0], [0, 0])
        cmd = ep["log_cmd_next"]
        for i in range(1, 150):
            assert np.allclose(ep["action"][i], cmd[i - 1] / 100.0), i
        assert ep["is_first"].tolist() == [True] + [False] * 149
        assert ep["is_last"].tolist() == [False] * 149 + [True]
        assert not ep["is_terminal"].any()
        assert np.all(ep["discount"] == 1.0)
        assert ep["log_ticks"].dtype == np.int32
        assert ep["log_mode"].dtype == np.uint8 and not ep["log_mode"].any()  # default manual
        failures: list = []
        verify_corpus.check_structure(ep, path, failures)
        assert failures == [], failures

        path2 = run(10, True)
        ep2 = load_episode(path2)
        assert bool(ep2["is_terminal"][-1])
        assert float(ep2["discount"][-1]) == 0.0
        assert not ep2["is_terminal"][:-1].any()

        before = sorted(rec.directory.glob("*.npz"))
        assert run(1, False) is None
        assert sorted(rec.directory.glob("*.npz")) == before

        # background save: recording is off at once, the file lands later,
        # and the recorder can start a new episode while the old one writes
        rec.start()
        for k in range(150):
            rec.add(fake_frame(k), (k % 201 - 100, 0),
                    {"ticks": k, "status": 1, "t_frame_ns": k,
                     "t_cmd_ns": k, "loop_dt": 50})
        got: list = []
        th = rec.stop_background(on_saved=got.append)
        assert not rec.recording and rec.steps == 0
        rec.start()
        rec.add(fake_frame(0), (0, 0), {"ticks": 0, "status": 1, "t_frame_ns": 0,
                                        "t_cmd_ns": 0, "loop_dt": 50})
        th.join(timeout=30)
        assert len(got) == 1 and got[0] is not None and got[0].exists(), got
        assert len(load_episode(got[0])["reward"]) == 150
        assert rec.steps == 1
    print("recorder self_check: PASS")


if __name__ == "__main__":
    self_check()
