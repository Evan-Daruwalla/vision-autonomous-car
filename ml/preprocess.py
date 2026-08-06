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


def process_split(split: str, out: Path, device: str, chunk: int = 256) -> None:
    files = sorted((SRC / split).glob("*.npz"))
    if not files:
        raise SystemExit(f"no episodes under {SRC / split}")

    lengths = [frames_in(f) for f in files]
    total = sum(lengths)
    print(f"{split:8s}: {len(files)} episodes, {total} frames")

    out.mkdir(parents=True, exist_ok=True)
    images = np.lib.format.open_memmap(
        out / f"{split}_images.npy", mode="w+", dtype=np.uint8,
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
    np.save(out / f"{split}_actions.npy", actions)
    np.save(out / f"{split}_episodes.npy", episodes)
    np.save(out / f"{split}_tracks.npy", tracks)
    uniq, cnt = np.unique(tracks, return_counts=True)
    print(f"    tracks: {dict(zip(uniq.tolist(), cnt.tolist()))}")

    mb = (images.nbytes + actions.nbytes) / 1e6
    print(f"    -> {out / f'{split}_images.npy'}  ({mb:.0f} MB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    print(f"resizing to {SIZE}x{SIZE} on {args.device}\n")
    for split in ("train", "holdout"):
        process_split(split, Path(args.out), args.device)
        print()


if __name__ == "__main__":
    main()
