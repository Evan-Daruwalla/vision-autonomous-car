"""The ONE frame -> model-input function, shared by training (ml/) and the Pi.

WHY one function: any difference between train-time and drive-time resizing is
a silent accuracy loss. PIL's BILINEAR downscale is antialiased, so 160x120 ->
64x64 is not plain point sampling. Do not reimplement this elsewhere.

    ./.venv/Scripts/python.exe pi/preprocess_frame.py --self-check
"""
from __future__ import annotations

import sys

import numpy as np
from PIL import Image


def to_model_input(frame_rgb: np.ndarray) -> np.ndarray:
    """uint8 (120,160,3) RGB -> float32 (1,3,64,64) in [0,1]."""
    if (not isinstance(frame_rgb, np.ndarray) or frame_rgb.dtype != np.uint8
            or frame_rgb.shape != (120, 160, 3)):
        raise ValueError(
            f"frame must be uint8 (120, 160, 3), got "
            f"{getattr(frame_rgb, 'dtype', None)} {getattr(frame_rgb, 'shape', None)}")
    img = Image.fromarray(frame_rgb).resize((64, 64), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return np.ascontiguousarray(arr.transpose(2, 0, 1)[None])


def self_check() -> None:
    rng = np.random.default_rng(0)
    f = rng.integers(0, 256, (120, 160, 3), dtype=np.uint8)
    out = to_model_input(f)
    assert out.shape == (1, 3, 64, 64) and out.dtype == np.float32
    assert out.min() >= 0.0 and out.max() <= 1.0
    assert np.array_equal(out, to_model_input(f.copy()))      # deterministic
    half = np.zeros((120, 160, 3), np.uint8)
    half[:, :80] = 255
    o = to_model_input(half)
    means = o[0].mean(axis=(1, 2))
    assert np.allclose(means, 0.5, atol=0.02), means
    assert o[0, :, :, 0].mean() > o[0, :, :, 63].mean()
    for bad in (np.zeros((64, 64, 3), np.uint8), np.zeros((120, 160, 3), np.float32),
                [1, 2, 3]):
        try:
            to_model_input(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("bad input accepted")
    print("preprocess_frame self_check: PASS")


if __name__ == "__main__":
    if "--self-check" in sys.argv[1:]:
        self_check()
    else:
        print(__doc__)
