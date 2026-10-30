"""Autopilot: camera frame -> (steer, throttle) in [-1, 1] via an ONNX model.

`Autopilot` needs onnxruntime (imported in the constructor only, so this module
imports on a PC without it). `StubAutopilot` returns fixed values for tests and
`teleop.py --fake`.

    ./.venv/Scripts/python.exe pi/autopilot.py --self-check
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import preprocess_frame


def _clip(v: float) -> float:
    return max(-1.0, min(1.0, float(v)))


def _clip_pair(a: float, b: float) -> tuple[float, float]:
    # NaN survives max/min clipping and would round() to a full-lock command
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError("non-finite model output")
    return _clip(a), _clip(b)


class Autopilot:
    def __init__(self, model_path: str | Path) -> None:
        import onnxruntime as ort
        self.session = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"])
        self.input_name = "image"

    def predict(self, frame_rgb) -> tuple[float, float]:
        x = preprocess_frame.to_model_input(frame_rgb)
        out = self.session.run(None, {self.input_name: x})[0]
        flat = out.reshape(-1)
        return _clip_pair(flat[0], flat[1])


class StubAutopilot:
    def __init__(self, steer: float = 0.3, throttle: float = 0.5) -> None:
        self.steer = steer
        self.throttle = throttle

    def predict(self, frame_rgb=None) -> tuple[float, float]:
        return _clip_pair(self.steer, self.throttle)


def self_check() -> None:
    assert StubAutopilot().predict() == (0.3, 0.5)
    assert StubAutopilot(2.0, -3.0).predict() == (1.0, -1.0)
    for bad in (float("nan"), float("inf"), float("-inf")):
        for args in ((bad, 0.1), (0.1, bad)):
            try:
                StubAutopilot(*args).predict()
            except ValueError as e:
                assert "non-finite" in str(e)
            else:
                raise AssertionError(f"non-finite {args} accepted")
    assert callable(Autopilot.predict)        # importable, constructor not called
    print("autopilot self_check: PASS")


if __name__ == "__main__":
    if "--self-check" in sys.argv[1:]:
        self_check()
    else:
        print(__doc__)
