"""SIM-POC P4 step 0: lay the P2 corpus out the way dreamerv3-torch wants it.

dreamerv3-torch reads `offline_traindir` / `offline_evaldir` as DIRECTORIES OF
PER-EPISODE npz -- the same shape `episode_writer.py` already writes, which is
why P2 targeted that format in the first place. Two things still have to
change before Dreamer can consume it:

  1. **Resize 120x160 -> 64x64.** Dreamer's default `size: [64, 64]`, and its
     CNN encoder/decoder are built around minres=4 with stride-2 layers. More
     importantly this is the SAME tensor P3 consumed, so any P3-vs-P4
     comparison is about the model, not the input pipeline.
  2. **Materialise the fit/val split as directories.** Dreamer takes two paths,
     not a list of indices, so the split has to exist on disk.

**The split is computed by `splits.fit_val_episodes(..., seed=0)` -- byte for
byte the split P3 trained on.** Episode order comes from the same
`sorted(glob("*.npz"))` that `preprocess.py` uses, so the episode indices mean
the same thing in both scripts. Change either and P3/P4 stop being comparable.

`holdout` (waveshare) is deliberately NOT written here. P4's done-check is
about whether DreamerV3 trains inside 8 GB, and P3 already measured what the
cross-domain track does to a world model. Feeding it here would only add
memory pressure to a memory experiment.

Usage:  python ml/prep_dreamer_corpus.py
        python ml/prep_dreamer_corpus.py --limit 4      # smoke, 4 episodes
"""

from __future__ import annotations

import argparse
import io
import os
from pathlib import Path

import numpy as np
import torch

from episode_writer import load_episode
from preprocess import resize_batch, frames_in
from splits import fit_val_episodes

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "ml" / "data" / "sim" / "train"
OUT = REPO / "ml" / "data" / "dreamer"


def write_episode(src: Path, dst_dir: Path, device: str, chunk: int = 256) -> int:
    """Resize one episode to 64x64 and re-write it, keeping every other key.

    Written to a .tmp then os.replace()d, same as episode_writer.py: a reader
    scanning the directory must see a complete file or no file. Dreamer's
    load_episodes swallows a bad npz with a printed warning and CARRIES ON
    with fewer episodes, so a torn file here would silently shrink the corpus
    instead of failing.
    """
    ep = load_episode(src)
    n = len(ep["image"])
    if n != frames_in(src):
        raise SystemExit(f"{src.name}: filename says {frames_in(src)}, array has {n}")

    small = np.empty((n, 64, 64, 3), np.uint8)
    for s in range(0, n, chunk):
        e = min(s + chunk, n)
        small[s:e] = resize_batch(ep["image"][s:e], device)

    out = {k: v for k, v in ep.items() if k != "image"}
    out["image"] = small

    dst = dst_dir / src.name
    tmp = dst.with_suffix(".npz.tmp")
    try:
        with io.BytesIO() as buf:
            np.savez_compressed(buf, **out)
            buf.seek(0)
            tmp.write_bytes(buf.read())
        os.replace(tmp, dst)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError as e:
                print(f"  failed to clean up {tmp}: {e}")
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--limit", type=int, default=0,
                    help="cap episodes per split (smoke runs)")
    ap.add_argument("--seed", type=int, default=0,
                    help="split seed; 0 is the split P3/P4 were trained on. "
                         "The other three fit_val_episodes call sites take "
                         "this from --seed, so hardcoding it here made the "
                         "docstring's 'byte for byte' claim true only by "
                         "coincidence (cold audit finding 10)")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    files = sorted(SRC.glob("*.npz"))
    if not files:
        raise SystemExit(f"no episodes under {SRC}")

    # Identical derivation to preprocess.py, so episode index i means the same
    # episode in both -- that is what makes the seed-0 split reproducible here.
    tracks = np.array([f.stem.rsplit("-", 2)[0] for f in files], dtype="<U40")
    fit, val = fit_val_episodes(tracks, seed=args.seed)
    print(f"{len(files)} source episodes -> fit {len(fit)}, val_indomain {len(val)}")

    for name, idx in (("train", fit), ("eval", val)):
        dst = Path(args.out) / name
        dst.mkdir(parents=True, exist_ok=True)
        # **Clear the directory first.** Episode filenames encode the source
        # episode, not the split, so growing the corpus by even one episode
        # reshuffles which side of the fit/val line an episode falls on -- and
        # without this, its copy on the OLD side survives. Demonstrated on the
        # live corpus (cold audit E2, 2026-08-06): appending one
        # generated-track episode moves 4 episodes val->fit while their stale
        # eval copies remain, so the P4 eval set silently contains episodes the
        # model trained on. The corpus has already been topped up twice.
        stale = list(dst.glob("*.npz"))
        for p in stale:
            p.unlink()
        if stale:
            print(f"  {name:5s} cleared {len(stale)} stale episode(s)")
        sel = idx[: args.limit] if args.limit else idx
        total = 0
        for j, i in enumerate(sel):
            total += write_episode(files[i], dst, args.device)
            if (j + 1) % 10 == 0 or j + 1 == len(sel):
                print(f"  {name:5s} {j+1}/{len(sel)} episodes, {total:,} frames")
        print(f"  -> {dst}  ({len(sel)} episodes, {total:,} frames)")


if __name__ == "__main__":
    main()
