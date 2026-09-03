"""SIM-POC P3 step 0: decode the episode corpus once into compact arrays.

Training a VAE for many epochs over 3.8 GB of compressed npz means decoding
the same frames hundreds of times. This decodes once to 64x64 and writes flat
memmap-able arrays:

    <out>/{split}_images.npy    (N, 64, 64, 3) uint8
    <out>/{split}_actions.npy   (N, 2)         float32
    <out>/{split}_episodes.npy  (E, 2)         int64   [start, length] per episode
    <out>/{split}_tracks.npy    (E,)           <U40    track name per episode

64x64 because that is what Ha & Schmidhuber used and what DreamerV3 expects,
so P3 and P4 consume the identical tensor and any comparison between them is
about the MODEL, not the input pipeline.

**The resize squashes 120x160 to 64x64 rather than cropping.** Cropping to
square would throw away peripheral vision, which is where the lane edge lives
during a turn -- exactly the signal the model needs. A fixed anisotropic
squash is a consistent, invertible-in-spirit distortion that the CNN absorbs;
losing the road edge is not.

Episode boundaries are kept because the MDN-RNN trains on SEQUENCES: a window
must never straddle two episodes, or the model learns a transition that never
happened.

Usage:  python ml/preprocess.py
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from episode_writer import load_episode

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "ml" / "data" / "sim"
OUT = REPO / "ml" / "data" / "proc"
SIZE = 64


def frames_in(path: Path) -> int:
    """Episode length is encoded in the filename; the writer guarantees it
    and verify_corpus.py enforces it, so trust it for preallocation."""
    return int(path.stem.rsplit("-", 1)[1])


def resize_batch(img: np.ndarray, device: str) -> np.ndarray:
    """(T,H,W,3) uint8 -> (T,64,64,3) uint8, antialiased bilinear."""
    t = torch.from_numpy(img).to(device).permute(0, 3, 1, 2).float()
    # antialias matters when downsampling 160->64: without it, thin lane
    # markings alias in and out between frames and the VAE learns flicker.
    t = F.interpolate(t, size=(SIZE, SIZE), mode="bilinear",
                      align_corners=False, antialias=True)
    t = t.clamp(0, 255).round().to(torch.uint8)
    return t.permute(0, 2, 3, 1).cpu().numpy()


def process_split(split: str, out: Path, device: str, chunk: int = 256,
                  extra_src: Path | None = None) -> None:
    files = sorted((SRC / split).glob("*.npz"))
    # `extra_src` appends a second corpus to the TRAIN split only -- used to
    # fold in off-centre recovery episodes (ml/collect_recovery.py) without
    # touching ml/data/sim, so every P2-P5 result stays reproducible from the
    # original corpus. Appended AFTER the sorted originals so the first N
    # episode indices keep their meaning and the seed-0 split of the original
    # episodes is unchanged.
    if extra_src is not None and split == "train":
        extra = sorted(Path(extra_src).glob("*.npz"))
        print(f"  + {len(extra)} recovery episodes from {extra_src}")
        files = files + extra
    if not files:
        raise SystemExit(f"no episodes under {SRC / split}")

    lengths = [frames_in(f) for f in files]
    total = sum(lengths)
    print(f"{split:8s}: {len(files)} episodes, {total} frames")

    out.mkdir(parents=True, exist_ok=True)
    # **All four outputs are written to .tmp, then renamed ONE AT A TIME.**
    # NOT an atomic four-file swap -- this comment claimed one until
    # 2026-09-03 (PRD task A3) and four sequential os.replace calls cannot
    # give one. A kill between renames is still possible; what changed is
    # that splits.load_proc() now REFUSES the torn result instead of
    # mmapping it silently. A true swap needs a versioned directory and one
    # pointer rename.
    # shortcut: guard on read, not atomicity on write. CEILING: a torn
    # write still happens, it just cannot be consumed. UPGRADE TRIGGER: if
    # a torn write is ever hit in practice, move to a versioned dir.
    # open_memmap(mode="w+") allocates the FULL-SIZE images file up front and
    # fills it progressively, while the three index arrays are only written
    # after the loop. Interrupt the loop on a re-run and the old index files
    # survive next to a half-real, zero-padded image array -- load_proc() then
    # mmaps a consistent-looking pair and train_vae.py trains on black frames
    # with no error at all. This is the project's normal workflow (the corpus
    # has been topped up twice), so it is a live path, not a hypothetical.
    # (Cold audit E1, 2026-08-06; mirrors episode_writer.py's tmp+os.replace.)
    tmp = {k: out / f"{split}_{k}.npy.tmp"
           for k in ("images", "actions", "episodes", "tracks")}
    images = np.lib.format.open_memmap(
        tmp["images"], mode="w+", dtype=np.uint8,
        shape=(total, SIZE, SIZE, 3))
    actions = np.zeros((total, 2), np.float32)
    episodes = np.zeros((len(files), 2), np.int64)
    # Track label per episode. Needed so a fit/val split can be stratified by
    # track: without it, holding out episodes could silently remove an entire
    # layout from training and the loss curve would look like overfitting.
    tracks = np.array([f.stem.rsplit("-", 2)[0] for f in files], dtype="<U40")

    pos = 0
    for i, f in enumerate(files):
        ep = load_episode(f)
        img, act = ep["image"], ep["action"]
        n = len(img)
        if n != lengths[i]:
            raise SystemExit(f"{f.name}: filename says {lengths[i]}, array has {n}")

        for s in range(0, n, chunk):
            e = min(s + chunk, n)
            images[pos + s: pos + e] = resize_batch(img[s:e], device)

        actions[pos: pos + n] = act
        episodes[i] = (pos, n)
        pos += n
        del ep
        if (i + 1) % 10 == 0 or i + 1 == len(files):
            print(f"    {i+1}/{len(files)} episodes, {pos}/{total} frames")

    assert pos == total, f"wrote {pos} frames, expected {total}"
    images.flush()
    img_bytes = images.nbytes
    del images                      # release the mmap so Windows can rename it
    # Written through a file object, not a path: np.save appends ".npy" to any
    # path that does not already end in it, so np.save(".../x.npy.tmp") would
    # silently create ".../x.npy.tmp.npy" and the rename below would fail.
    for key in ("actions", "episodes", "tracks"):
        with open(tmp[key], "wb") as f:
            np.save(f, {"actions": actions, "episodes": episodes,
                        "tracks": tracks}[key])
    # Only now does any of it become visible under its real name.
    for k, src in tmp.items():
        os.replace(src, out / f"{split}_{k}.npy")
    uniq, cnt = np.unique(tracks, return_counts=True)
    print(f"    tracks: {dict(zip(uniq.tolist(), cnt.tolist()))}")

    mb = (img_bytes + actions.nbytes) / 1e6
    print(f"    -> {out / f'{split}_images.npy'}  ({mb:.0f} MB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--extra-src", default=None,
                    help="append a second episode dir to the TRAIN split "
                         "(e.g. ml/data/sim_recovery/train). Use with a "
                         "different --out so the original proc arrays survive")
    args = ap.parse_args()

    print(f"resizing to {SIZE}x{SIZE} on {args.device}\n")
    extra = Path(args.extra_src) if args.extra_src else None
    for split in ("train", "holdout"):
        process_split(split, Path(args.out), args.device, extra_src=extra)
        print()


if __name__ == "__main__":
    main()
