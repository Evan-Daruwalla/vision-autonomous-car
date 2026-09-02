"""Write driving episodes in the NM512/dreamerv3-torch on-disk format.

Format matched to that repo's `tools.save_episodes` / `tools.load_episodes`
(read from source 2026-08-05):

  * one `np.savez_compressed` archive per episode
  * filename `{id}-{length}.npz`, where length == len(episode["reward"])
  * every key is a parallel array over timesteps

Keys written, matching what dreamerv3-torch's dataloader expects:

  image        (T, H, W, 3) uint8   camera frame
  action       (T, A)       float32 the action that LED TO this frame
  reward       (T,)         float32
  discount     (T,)         float32 1.0, or 0.0 on a true terminal
  is_first     (T,)         bool    True only at t=0
  is_last      (T,)         bool    True at the final step
  is_terminal  (T,)         bool    True only if the episode really ended
                                    (crash), False if merely truncated

**The t=0 convention is the part that is easy to get wrong.** At reset there
is no preceding action, so `action[0]` is zeros and `reward[0]` is 0.0. Every
later index i holds the action that produced `image[i]`. Getting this off by
one silently teaches the model to predict the PREVIOUS action -- it still
trains, it just learns the wrong thing, which is why `verify_corpus.py`
re-derives the alignment from an independent signal instead of trusting it.

Terminal vs truncated matters to a world model: a real crash means "no future
exists" (discount 0), while hitting a step limit means "the future exists, we
just stopped looking" (discount 1). Conflating them teaches the model that
time-limit boundaries are catastrophes.
"""

from __future__ import annotations

import io
import os
import uuid
from pathlib import Path

import numpy as np

# Keys whose dtype we pin, so a stray Python float can't silently widen an
# array to float64 and double the corpus size on disk.
_DTYPES = {
    "image": np.uint8,
    "action": np.float32,
    "reward": np.float32,
    "discount": np.float32,
    "is_first": bool,
    "is_last": bool,
    "is_terminal": bool,
}


# ---- turn-signal channel (PRD task 11b, docs/LIGHTING_SPEC.md section 5) ----
# A turn signal is a POLICY OUTPUT, so behavioural cloning needs a per-frame
# label for it, the same way it needs steering and throttle. Task 11's
# done-check names only "images + steering/throttle synced"; this is the third
# channel, and it MUST exist before the M3 collection run -- 10-20 laps
# recorded without indicator labels cannot be relabelled honestly.
#
# The `log_` prefix is deliberate and follows `log_cte`: dreamerv3-torch's
# dataloader filters keys containing "log_", so the world-model path (M4) is
# untouched, while this project's own scripts read the npz directly and can use
# it as a training target -- which is exactly how train_cte_probe.py already
# consumes `log_cte`.
#
# Unlike a stop sign, this IS learnable by plain BC: on a memorised route the
# correct indicator state is a function of where the car is, which is visible
# in the frame (gotchas.md's "traffic lights are memoryless-learnable").
INDICATOR_OFF, INDICATOR_LEFT, INDICATOR_RIGHT = 0, 1, 2
_PER_FRAME_LOG = ("log_indicator",)
INDICATOR_NAMES = {INDICATOR_OFF: "off", INDICATOR_LEFT: "left",
                   INDICATOR_RIGHT: "right"}


def _check_indicator(v) -> np.int8:
    """Reject anything that is not one of the three states, loudly.

    A silently-coerced label is worse than a crash: it trains the third head on
    garbage while every shape check still passes.
    """
    if isinstance(v, bool) or v not in INDICATOR_NAMES:
        raise ValueError(
            f"indicator must be one of {sorted(INDICATOR_NAMES)} "
            f"({', '.join(INDICATOR_NAMES.values())}), got {v!r}")
    return np.int8(v)


class EpisodeWriter:
    """Accumulate one episode's transitions, then write it as a single npz."""

    def __init__(self, directory: str | Path, prefix: str = ""):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix
        self._steps: list[dict] = []

    def add_reset(self, image: np.ndarray, action_dim: int,
                  indicator: int = INDICATOR_OFF) -> None:
        """Record the frame returned by env.reset(): no action caused it."""
        if self._steps:
            raise RuntimeError("add_reset() called on a non-empty episode")
        self._steps.append({
            "image": image,
            "action": np.zeros(action_dim, np.float32),
            "reward": 0.0,
            "discount": 1.0,
            "is_first": True,
            "is_last": False,
            "is_terminal": False,
            "log_indicator": _check_indicator(indicator),
        })

    def add_step(self, image, action, reward, terminated, truncated,
                 indicator: int = INDICATOR_OFF) -> None:
        """Record a post-step frame and the action that produced it.

        `indicator` is the TURN-SIGNAL STATE AT THIS FRAME (PRD task 11b). It
        is a third supervised channel, not telemetry: a turn signal is a policy
        OUTPUT, so behavioural cloning needs a per-frame label for it exactly
        as it needs steering and throttle. Defaults to OFF so every existing
        caller keeps working unchanged.
        """
        if not self._steps:
            raise RuntimeError("add_step() before add_reset()")
        self._steps.append({
            "log_indicator": _check_indicator(indicator),
            "image": image,
            "action": np.asarray(action, np.float32),
            "reward": float(reward),
            # a real terminal kills the future; a truncation does not
            "discount": 0.0 if terminated else 1.0,
            "is_first": False,
            "is_last": bool(terminated or truncated),
            "is_terminal": bool(terminated),
        })

    def __len__(self) -> int:
        return len(self._steps)

    def save(self, meta: dict | None = None) -> Path:
        """Write the episode. Returns the path. Resets the buffer."""
        if len(self._steps) < 2:
            raise RuntimeError(f"refusing to save a {len(self._steps)}-step episode")

        # Force is_last on the final frame even if the loop stopped early --
        # otherwise the episode has no boundary and the loader will run it
        # straight into the next one.
        self._steps[-1]["is_last"] = True

        episode = {}
        for key, dtype in _DTYPES.items():
            episode[key] = np.array([s[key] for s in self._steps], dtype=dtype)

        # Per-frame `log_` channels recorded alongside the dreamer keys. These
        # are PARALLEL ARRAYS over timesteps, unlike the `meta` block below,
        # which stores one constant per episode. The indicator label (task 11b)
        # is the first of these: it varies frame to frame and is a supervised
        # target, so it cannot ride in `meta`.
        for key in _PER_FRAME_LOG:
            if key in self._steps[0]:
                episode[key] = np.array([s[key] for s in self._steps], np.int8)

        if meta:
            for key, value in meta.items():
                # dreamerv3-torch filters keys containing "log_" out of the
                # training tensors, so provenance rides along harmlessly.
                episode[f"log_{key}"] = np.array(value)

        length = len(episode["reward"])
        stem = f"{self.prefix}{uuid.uuid4().hex}"
        path = self.directory / f"{stem}-{length}.npz"

        # Build in memory, write to a temp name, then rename. os.replace is
        # atomic within a filesystem, so a reader scanning this directory
        # only ever sees the complete file or no file -- never a half one.
        # (Building in a BytesIO alone does NOT give this: the write to disk
        # is still interruptible, and a verifier racing the collector then
        # hits a truncated npz. Observed 2026-08-06.)
        tmp = path.with_suffix(".npz.tmp")
        try:
            with io.BytesIO() as buf:
                np.savez_compressed(buf, **episode)
                buf.seek(0)
                tmp.write_bytes(buf.read())
            os.replace(tmp, path)
        finally:
            # Clear the buffer even if the write failed, or the next
            # add_reset() raises "non-empty episode" and kills the whole run
            # over one bad write.
            self._steps = []
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError as e:
                    print(f"episode_writer: failed to clean up {tmp}: {e}")
        return path


def load_episode(path: str | Path) -> dict:
    """Read one episode back. Mirrors dreamerv3-torch's load_episodes."""
    with Path(path).open("rb") as f:
        with np.load(f) as data:
            return {k: data[k] for k in data.files}


def self_check() -> None:
    """Round-trip an episode carrying indicator labels through a real npz."""
    import tempfile
    rng = np.random.default_rng(0)
    want = [INDICATOR_OFF, INDICATOR_LEFT, INDICATOR_LEFT,
            INDICATOR_RIGHT, INDICATOR_OFF]
    with tempfile.TemporaryDirectory() as td:
        w = EpisodeWriter(td, prefix="selfcheck")
        img = lambda: rng.integers(0, 255, (8, 10, 3), dtype=np.uint8)
        w.add_reset(img(), action_dim=2, indicator=want[0])
        for k in want[1:]:
            w.add_step(img(), np.zeros(2, np.float32), 0.0, False, False,
                       indicator=k)
        path = w.save()
        ep = load_episode(path)

    assert "log_indicator" in ep, "indicator channel missing after round-trip"
    got = ep["log_indicator"]
    assert got.shape == (len(want),), got.shape
    assert list(got) == want, (list(got), want)
    # parallel with every other channel -- an off-by-one here mislabels which
    # frame the driver was indicating on
    assert len(got) == len(ep["image"]) == len(ep["action"]) == len(ep["reward"])
    # t=0 convention preserved
    assert bool(ep["is_first"][0]) and not bool(ep["is_first"][1])

    # bad labels must RAISE, not coerce
    for bad in (3, -1, 1.5, "left", True, None):
        try:
            _check_indicator(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid indicator {bad!r}")
    # ... and the three valid ones must pass
    for good in (INDICATOR_OFF, INDICATOR_LEFT, INDICATOR_RIGHT):
        assert int(_check_indicator(good)) == good

    print("episode_writer self_check: PASS")


if __name__ == "__main__":
    self_check()
