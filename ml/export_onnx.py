"""Export a trained BC policy to ONNX and prove the export is faithful.

WHY THIS EXISTS. The Pi runs the autopilot on onnxruntime, not torch (torch is
too heavy for the Pi). An export that silently drifts from the torch model
would make the car drive differently than the policy that was evaluated, so
every export is gated on a numeric parity check against the torch outputs, and
the CPU latency is measured here because the control loop has a time budget.

The legacy TorchScript exporter (dynamo=False) is used: it is the stable path
for plain conv nets and needs no extra dependency.

BCNet lives in ml/models.py and is imported only inside the CLI branch, so
this module imports (and self-checks) without it.

    ./.venv/Scripts/python.exe ml/export_onnx.py --ckpt <run>/bc_best.pt --out <dir>/bc.onnx
    ./.venv/Scripts/python.exe ml/export_onnx.py --untrained --out <dir>/bcnet_untrained.onnx
--untrained exports a seed-0 BCNet with random weights: for timing on the Pi
(pi/autopilot.py --bench) only, never for driving.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import torch

OPSET = 17
PARITY_TOL = 1e-4


def export(model: torch.nn.Module, path, input_shape=(1, 3, 64, 64)) -> Path:
    """Export `model` to `path` with input "image", output "action", dynamic batch."""
    path = Path(path)
    model.eval()
    dummy = torch.zeros(*input_shape)
    torch.onnx.export(
        model, dummy, str(path),
        input_names=["image"], output_names=["action"],
        dynamic_axes={"image": {0: "batch"}, "action": {0: "batch"}},
        opset_version=OPSET, dynamo=False)
    return path


def _session(onnx_path):
    import onnxruntime as ort
    return ort.InferenceSession(str(onnx_path),
                                providers=["CPUExecutionProvider"])


def parity(model: torch.nn.Module, onnx_path, n: int = 32, seed: int = 0,
           input_shape=(1, 3, 64, 64)) -> float:
    """Max abs difference between torch and onnxruntime on n random inputs in [0,1]."""
    model.eval()
    rng = np.random.default_rng(seed)
    x = rng.random((n, *input_shape[1:]), dtype=np.float32)
    with torch.no_grad():
        ref = model(torch.from_numpy(x)).numpy()
    out = _session(onnx_path).run(None, {"image": x})[0]
    return float(np.max(np.abs(ref - out)))


def time_cpu(onnx_path, iters: int = 200, input_shape=(1, 3, 64, 64)) -> dict:
    """Batch-1 CPU inference timings in ms: mean_ms, p50_ms, p95_ms."""
    sess = _session(onnx_path)
    x = np.random.default_rng(0).random(input_shape, dtype=np.float32)
    for _ in range(5):                      # warmup
        sess.run(None, {"image": x})
    ts = []
    for _ in range(iters):
        t0 = time.perf_counter()
        sess.run(None, {"image": x})
        ts.append((time.perf_counter() - t0) * 1000.0)
    a = np.array(ts)
    return {"mean_ms": float(a.mean()), "p50_ms": float(np.percentile(a, 50)),
            "p95_ms": float(np.percentile(a, 95))}


def self_check() -> None:
    net = torch.nn.Sequential(
        torch.nn.Conv2d(3, 8, 5, stride=2), torch.nn.ReLU(),
        torch.nn.Conv2d(8, 16, 3, stride=2), torch.nn.ReLU(),
        torch.nn.AdaptiveAvgPool2d(1), torch.nn.Flatten(),
        torch.nn.Linear(16, 2), torch.nn.Tanh())
    torch.manual_seed(0)
    n = 32
    with tempfile.TemporaryDirectory() as d:
        p = export(net, Path(d) / "m.onnx")
        assert p.exists()
        err = parity(net, p, n=n)
        assert err < PARITY_TOL, err
        x = np.random.default_rng(1).random((n, 3, 64, 64), dtype=np.float32)
        out = _session(p).run(None, {"image": x})[0]
        assert out.shape == (n, 2), out.shape
        assert out.min() >= -1.0 and out.max() <= 1.0
        t = time_cpu(p, iters=20)
        assert t["mean_ms"] > 0, t
    print(f"self_check OK (parity {err:.2e}, mean {t['mean_ms']:.3f} ms)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--ckpt")
    ap.add_argument("--out")
    ap.add_argument("--untrained", action="store_true",
                    help="export a seed-0 UNTRAINED BCNet (latency measurement only; no --ckpt)")
    a = ap.parse_args()
    if a.self_check:
        self_check()
        return 0
    if a.ckpt and a.untrained:
        ap.error("--ckpt and --untrained are mutually exclusive")
    if not a.out or not (a.ckpt or a.untrained):
        ap.error("--out and one of --ckpt / --untrained are required (or use --self-check)")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from models import BCNet            # imported here, not at module top (see docstring)
    import provenance
    shape = (1, 3, 64, 64)
    if a.untrained:
        torch.manual_seed(0)
        model = BCNet()
    else:
        model = BCNet()
        ck = torch.load(a.ckpt, map_location="cpu")
        model.load_state_dict(ck["model"])
    out = Path(a.out)
    # Export beside the target and only os.replace() it into place once parity
    # passes, so a model that failed parity is never left at --out.
    tmp = out.with_suffix(".onnx.tmp")
    try:
        export(model, tmp, shape)
        err = parity(model, tmp, input_shape=shape)
        timing = time_cpu(tmp, input_shape=shape)
        if err <= PARITY_TOL:
            os.replace(tmp, out)
    finally:
        tmp.unlink(missing_ok=True)      # no-op after a successful replace
    prefix = "UNTRAINED (latency only): " if a.untrained else ""
    print(f"{prefix}parity max abs diff {err:.3e}; timing {timing}")
    provenance.write_result(
        str(out) + ".json",
        {"parity": err, "timing": timing, "opset": OPSET,
         "input_shape": list(shape),
         "ckpt": None if a.untrained else str(a.ckpt),
         "weights": "untrained (latency only)" if a.untrained else "trained",
         # Audit C2-5, record NQ: the checkpoint was picked on val MSE alone
         # and has never driven. pi/teleop.py warns on AUTO while this is
         # False; set it to true by hand only after a supervised stand pass.
         "selected_by": None if a.untrained else "val_mse (bc_real best checkpoint)",
         "stand_tested": False})
    if err > PARITY_TOL:
        print(f"FAIL: parity {err:.3e} > {PARITY_TOL}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
