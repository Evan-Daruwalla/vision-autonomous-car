"""Deterministic episode-level splits, shared by every P3/P4 training script.

Three evaluation sets, because they answer three different questions and
conflating them is how a model gets called "generalising" when it isn't:

  fit          episodes actually trained on
  val_indomain held-out EPISODES of the SAME tracks -- unseen trajectories,
               seen visual domain. Answers "did it learn the dynamics, or
               memorise these particular runs?"
  holdout      an entirely unseen TRACK (waveshare). Answers "does it
               transfer to a new layout?"

**`holdout` turned out to be a harder question than intended, and the
distinction matters.** Measured 2026-08-06: the two training tracks are
outdoor (road, trees, sky) while waveshare is indoor (walls, pale floor). So
the holdout confounds *unseen layout* with *unseen visual domain*, and the
VAE fails it by hallucinating trees onto an indoor scene. That is a real and
interesting result, but it cannot also serve as the "do the dynamics work"
check -- hence val_indomain.

Splitting at EPISODE level, never frame level: frames t and t+1 are
near-duplicates, so a frame split leaks (record Appendix L).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
PROC = REPO / "ml" / "data" / "proc"

VAL_FRACTION = 0.15     # of training episodes, per track


def encoder_fingerprint(ckpt) -> str:
    """Short stable fingerprint of the VAE checkpoint behind a latent cache.

    Lives here because BOTH writers and readers of `{split}_mu.npy` need the
    same answer: train_mdnrnn.py writes the cache, rollout_eval.py decodes
    through it, and a mismatch between them is silent. One helper at the shared
    chokepoint beats two copies that can drift. (Cold audit finding 5.)
    """
    if ckpt is None or not Path(ckpt).exists():
        return "unknown"
    st = Path(ckpt).stat()
    return hashlib.sha1(
        f"{Path(ckpt).name}:{st.st_size}:{st.st_mtime_ns}".encode()
    ).hexdigest()[:12]


def cache_key_matches(split: str, want: str, proc: Path = PROC) -> bool:
    p = proc / f"{split}_latents.key"
    return p.exists() and p.read_text(encoding="utf-8").strip() == want


def write_cache_key(split: str, want: str, proc: Path = PROC) -> None:
    (proc / f"{split}_latents.key").write_text(want, encoding="utf-8")


def load_proc(split: str, proc: Path = PROC):
    imgs = np.load(proc / f"{split}_images.npy", mmap_mode="r")
    actions = np.load(proc / f"{split}_actions.npy")
    episodes = np.load(proc / f"{split}_episodes.npy")
    tracks = np.load(proc / f"{split}_tracks.npy")
    return imgs, actions, episodes, tracks


def fit_val_episodes(tracks: np.ndarray, seed: int = 0,
                     val_fraction: float = VAL_FRACTION):
    """Split episode INDICES into (fit, val), stratified by track.

    Stratified so every track stays represented in both halves -- an
    unstratified random split can drop a whole track out of training, which
    looks like overfitting in the curves and is actually a broken split.
    """
    rng = np.random.default_rng(seed)
    fit, val = [], []
    for name in sorted(np.unique(tracks)):
        idx = np.flatnonzero(tracks == name)
        rng.shuffle(idx)
        n_val = max(1, int(round(len(idx) * val_fraction)))
        val.extend(idx[:n_val].tolist())
        fit.extend(idx[n_val:].tolist())
    return np.array(sorted(fit)), np.array(sorted(val))


def frame_indices(episodes: np.ndarray, ep_idx: np.ndarray) -> np.ndarray:
    """Flat frame indices belonging to the given episodes."""
    if len(ep_idx) == 0:
        return np.array([], np.int64)
    return np.concatenate([np.arange(s, s + n) for s, n in episodes[ep_idx]])


def describe(tracks, episodes, fit, val) -> str:
    def summary(idx):
        if len(idx) == 0:
            return "none"
        frames = int(episodes[idx][:, 1].sum())
        uniq, cnt = np.unique(tracks[idx], return_counts=True)
        per = ", ".join(f"{u}:{c}" for u, c in zip(uniq.tolist(), cnt.tolist()))
        return f"{len(idx)} eps / {frames:,} frames ({per})"
    return f"fit          {summary(fit)}\nval_indomain {summary(val)}"


def self_check() -> None:
    """Runnable check: the split is disjoint, exhaustive, and reproducible."""
    tracks = np.array(["a"] * 10 + ["b"] * 6)
    fit, val = fit_val_episodes(tracks, seed=0)

    assert len(set(fit) & set(val)) == 0, "fit and val overlap"
    assert sorted(fit.tolist() + val.tolist()) == list(range(16)), "not exhaustive"
    # every track present on both sides
    assert set(tracks[fit]) == {"a", "b"}, tracks[fit]
    assert set(tracks[val]) == {"a", "b"}, tracks[val]
    # reproducible
    f2, v2 = fit_val_episodes(tracks, seed=0)
    assert np.array_equal(fit, f2) and np.array_equal(val, v2), "not deterministic"
    # a different seed gives a different split (otherwise the seed is ignored)
    f3, _ = fit_val_episodes(tracks, seed=1)
    assert not np.array_equal(fit, f3), "seed has no effect"

    eps = np.array([[0, 5], [5, 7], [12, 3]])
    fr = frame_indices(eps, np.array([0, 2]))
    assert fr.tolist() == [0, 1, 2, 3, 4, 12, 13, 14], fr.tolist()
    assert frame_indices(eps, np.array([], np.int64)).size == 0

    print(f"fit={fit.tolist()}")
    print(f"val={val.tolist()}")
    print("splits self_check: PASS")


if __name__ == "__main__":
    self_check()
