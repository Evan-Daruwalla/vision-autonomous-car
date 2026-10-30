"""Autopilot: camera frame -> (steer, throttle) in [-1, 1] via an ONNX model.

`Autopilot` needs onnxruntime (imported in the constructor only, so this module
imports on a PC without it). `StubAutopilot` returns fixed values for tests and
`teleop.py --fake`.

    ./.venv/Scripts/python.exe pi/autopilot.py --self-check
    ./.venv/Scripts/python.exe pi/autopilot.py --bench MODEL.onnx [--iters 200]
"""
from __future__ import annotations

import argparse
import math
import sys
import time
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


def bench(model_path, iters: int = 200, warmup: int = 5) -> dict:
    """Time Autopilot.predict on synthetic frames. END-TO-END (preprocess +
    inference), which is what the 50 ms control tick pays."""
    import numpy as np
    from camera import fake_frame
    ap = Autopilot(model_path)
    for i in range(warmup):
        ap.predict(fake_frame(i))
    ts = []
    for i in range(iters):
        f = fake_frame(i % 50)
        t0 = time.perf_counter()
        ap.predict(f)
        ts.append((time.perf_counter() - t0) * 1000.0)
    a = np.array(ts)
    return {"mean_ms": float(a.mean()), "p50_ms": float(np.percentile(a, 50)),
            "p95_ms": float(np.percentile(a, 95)), "max_ms": float(a.max()),
            "iters": iters}


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


BUDGET_MS = 50.0      # 20 Hz control tick

if __name__ == "__main__":
    _ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    _ap.add_argument("--self-check", action="store_true")
    _ap.add_argument("--bench", metavar="MODEL")
    _ap.add_argument("--iters", type=int, default=200)
    _a = _ap.parse_args()
    if _a.self_check:
        self_check()
    elif _a.bench:
        r = bench(_a.bench, _a.iters)
        ok = r["p95_ms"] < BUDGET_MS
        print(f"autopilot bench: mean {r['mean_ms']:.2f} ms, p50 {r['p50_ms']:.2f}, "
              f"p95 {r['p95_ms']:.2f}, max {r['max_ms']:.2f} over {r['iters']} iters "
              f"(end-to-end predict: preprocess + onnxruntime); "
              f"budget {BUDGET_MS:.0f} ms (20 Hz tick)")
        print("PASS" if ok else "OVER BUDGET")
        sys.exit(0 if ok else 1)
    else:
        print(__doc__)
