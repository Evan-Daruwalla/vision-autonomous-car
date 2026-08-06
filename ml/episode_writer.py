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


class EpisodeWriter:
    """Accumulate one episode's transitions, then write it as a single npz."""

    def __init__(self, directory: str | Path, prefix: str = ""):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix
        self._steps: list[dict] = []

    def add_reset(self, image: np.ndarray, action_dim: int) -> None:
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
        })

    def add_step(self, image, action, reward, terminated, truncated) -> None:
        """Record a post-step frame and the action that produced it."""
        if not self._steps:
            raise RuntimeError("add_step() before add_reset()")
        self._steps.append({
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
                except OSError:
                    pass
        return path


def load_episode(path: str | Path) -> dict:
    """Read one episode back. Mirrors dreamerv3-torch's load_episodes."""
    with Path(path).open("rb") as f:
        with np.load(f) as data:
            return {k: data[k] for k in data.files}
