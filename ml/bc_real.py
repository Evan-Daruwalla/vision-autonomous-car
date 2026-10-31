"""Behavioural cloning on REAL-car episodes (pi/recorder.py output).

    ./.venv/Scripts/python.exe ml/bc_real.py --data DIR --out DIR [--epochs 50] [--seed 0] [--cpu]
    ./.venv/Scripts/python.exe ml/bc_real.py --self-check

Inputs come from pi/preprocess_frame.to_model_input -- the SAME function the Pi
runs at drive time, so training and the car see identical pixels. Target for
image_k is log_cmd_next[k] / 100 (the command sent right after that frame),
(steer, throttle) with +steer = right. Splits are by EPISODE (splits.py), never
by frame. Flip augmentation always negates the steer target.
"""
from __future__ import annotations

import argparse
import copy
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ml"))
sys.path.insert(0, str(REPO / "pi"))

import provenance                               # noqa: E402
import splits                                   # noqa: E402
from episode_writer import EpisodeWriter, load_episode   # noqa: E402
from models import BCNet                        # noqa: E402
from preprocess_frame import to_model_input     # noqa: E402

REAL_MIN_STEPS = 40
VAL_FRACTION = 0.15
LR = 1e-3
BATCH = 128
PATIENCE = 5
W_STEER, W_THROTTLE = 1.0, 0.5
ACTION_UNITS = "cmd/100, +steer = right"
CRASH_TRIM = 10        # frames dropped before a crash (is_terminal[-1]); not imitated


def load_real(data_dir) -> tuple[list[dict], list[dict]]:
    """Every *.npz under data_dir -> (episodes, skipped).

    episode = {id, track, x (K,3,64,64) f32, y (K,2) f32, n_auto, n_crash};
    skipped = [{path, reason}]. track = parent directory name (the session).

    Which frames are imitated: frames with log_mode == 1 (autopilot) are
    dropped -- they are the model's own actions, not demonstrations; and in
    an episode that ends in a crash (is_terminal[-1]) the last CRASH_TRIM
    frames are dropped -- the lead-in to a crash is what not to imitate.
    n_auto / n_crash count the dropped frames (disjoint). Episodes without
    log_mode keep every frame. Episodes recorded with fake hardware are skipped.
    """
    eps, skipped = [], []
    for p in sorted(Path(data_dir).rglob("*.npz")):
        try:
            ep = load_episode(p)
        except Exception as e:                  # corrupt / not an npz episode
            skipped.append({"path": str(p), "reason": f"unreadable: {e}"})
            continue
        if "log_cmd_next" not in ep or "image" not in ep:
            skipped.append({"path": str(p),
                            "reason": "no log_cmd_next/image (not a real-car episode)"})
            continue
        if (bool(np.asarray(ep.get("log_fake", False)))
                or bool(np.asarray(ep.get("log_fake_uno", False)))):
            skipped.append({"path": str(p),
                            "reason": "fake hardware (log_fake/log_fake_uno)"})
            continue
        T = len(ep["image"])
        if T < REAL_MIN_STEPS:
            skipped.append({"path": str(p),
                            "reason": f"too short ({T} < {REAL_MIN_STEPS})"})
            continue
        cmd = np.asarray(ep["log_cmd_next"])
        if cmd.shape != (T, 2):
            skipped.append({"path": str(p),
                            "reason": f"log_cmd_next shape {cmd.shape}, expected ({T}, 2)"})
            continue
        keep = np.ones(T, bool)
        n_auto = n_crash = 0
        if "log_mode" in ep:
            auto = np.asarray(ep["log_mode"]).reshape(-1) == 1
            if auto.shape != (T,):
                skipped.append({"path": str(p),
                                "reason": f"log_mode shape {auto.shape}, expected ({T},)"})
                continue
            keep &= ~auto
            n_auto = int(auto.sum())
        term = np.asarray(ep.get("is_terminal", []))
        if len(term) == T and bool(term[-1]):
            tail = np.zeros(T, bool)
            tail[-CRASH_TRIM:] = True
            n_crash = int((tail & keep).sum())
            keep &= ~tail
        idx = np.flatnonzero(keep)
        x = np.concatenate([to_model_input(ep["image"][i]) for i in idx], axis=0) \
            if len(idx) else np.zeros((0, 3, 64, 64), np.float32)
        y = (cmd[idx].astype(np.float32) / 100.0).astype(np.float32)
        eps.append({"id": p.stem, "track": p.parent.name, "x": x, "y": y,
                    "n_auto": n_auto, "n_crash": n_crash})
    return eps, skipped


def augment(x: torch.Tensor, y: torch.Tensor, gen: torch.Generator,
            p_flip: float = 0.5, max_shift: int = 4):
    """Training-batch augmentation. x (N,3,64,64) in [0,1], y (N,2).

    brightness x U(0.75,1.25) clipped; translation up to max_shift px (edge
    padding); horizontal flip with prob p_flip, which ALWAYS negates steer.
    Returns new tensors; inputs are untouched.
    """
    n = x.shape[0]
    x = x * (0.75 + 0.5 * torch.rand(n, 1, 1, 1, generator=gen))
    x = x.clamp(0.0, 1.0)
    if max_shift > 0:
        s = max_shift
        pad = F.pad(x, (s, s, s, s), mode="replicate")
        off = torch.randint(0, 2 * s + 1, (n, 2), generator=gen)
        h, w = x.shape[2], x.shape[3]
        x = torch.stack([pad[i, :, off[i, 0]:off[i, 0] + h, off[i, 1]:off[i, 1] + w]
                         for i in range(n)])
    y = y.clone()
    flip = torch.rand(n, generator=gen) < p_flip
    if flip.any():
        x = torch.where(flip.view(-1, 1, 1, 1), x.flip(-1), x)
        y[flip, 0] = -y[flip, 0]
    return x, y


def _loss(pred: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    return (W_STEER * F.mse_loss(pred[:, 0], y[:, 0])
            + W_THROTTLE * F.mse_loss(pred[:, 1], y[:, 1]))


@torch.no_grad()
def evaluate(model, x, y, dev, bs: int = 512) -> dict:
    model.eval()
    if len(x) == 0:
        return {"n_frames": 0, "loss": None, "steer_mae": None}
    preds = torch.cat([model(x[i:i + bs].to(dev)).cpu() for i in range(0, len(x), bs)])
    return {"n_frames": int(len(x)), "loss": float(_loss(preds, y)),
            "steer_mae": float((preds[:, 0] - y[:, 0]).abs().mean())}


def _cat(eps, idx):
    x = torch.from_numpy(np.concatenate([eps[i]["x"] for i in idx]))
    y = torch.from_numpy(np.concatenate([eps[i]["y"] for i in idx]))
    return x, y


def run(data, out, epochs: int = 50, seed: int = 0, cpu: bool = False,
        batch: int = BATCH, patience: int = PATIENCE) -> dict:
    eps, skipped = load_real(data)
    for s in skipped:
        print(f"  skipped {s['path']}: {s['reason']}")
    if len(eps) < 3:
        raise SystemExit(f"need >= 3 usable episodes for fit/val/test, got {len(eps)}")
    tracks = np.array([e["track"] for e in eps])
    ids = np.array([e["id"] for e in eps])
    fit_i, val_i = splits.fit_val_episodes(tracks, seed, VAL_FRACTION, ids=ids)
    sub_fit, sub_test = splits.fit_val_episodes(tracks[fit_i], seed + 1,
                                                VAL_FRACTION, ids=ids[fit_i])
    test_i, fit_i = fit_i[sub_test], fit_i[sub_fit]
    if len(fit_i) == 0:
        raise SystemExit("fit split is empty; collect more episodes per session")
    print(f"episodes: {len(eps)} (fit {len(fit_i)}, val {len(val_i)}, test {len(test_i)})")

    dev = torch.device("cpu" if cpu or not torch.cuda.is_available() else "cuda")
    torch.manual_seed(seed)
    np.random.seed(seed)
    gen = torch.Generator().manual_seed(seed)
    xf, yf = _cat(eps, fit_i)
    xv, yv = _cat(eps, val_i)
    xt, yt = _cat(eps, test_i)
    if len(xf) == 0:
        raise SystemExit("no trainable frames: every fit-episode frame was "
                         "dropped (autopilot log_mode=1 or crash trim)")

    model = BCNet().to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    best, best_val, bad, hist = None, float("inf"), 0, []
    for ep in range(1, epochs + 1):
        model.train()
        perm = torch.randperm(len(xf), generator=gen)
        tot, cnt = 0.0, 0
        for i in range(0, len(xf), batch):
            b = perm[i:i + batch]
            xb, yb = augment(xf[b], yf[b], gen)
            xb, yb = xb.to(dev), yb.to(dev)
            loss = _loss(model(xb), yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += float(loss) * len(b)
            cnt += len(b)
        v = evaluate(model, xv, yv, dev)
        hist.append({"epoch": ep, "train_loss": tot / cnt, "val_loss": v["loss"],
                     "val_steer_mae": v["steer_mae"]})
        print(f"  epoch {ep:3d} train {tot / cnt:.4f} val {v['loss']:.4f} "
              f"val_steer_mae {v['steer_mae']:.4f}")
        if v["loss"] < best_val:
            best_val, bad = v["loss"], 0
            best = copy.deepcopy(model.state_dict())
        else:
            bad += 1
            if bad >= patience:
                print(f"  early stop (no val improvement for {patience} epochs)")
                break
    model.load_state_dict(best)

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    used_ids = [eps[i]["id"] for i in range(len(eps))]
    cid = splits.corpus_id(used_ids)
    cpu_state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
    torch.save({"model": cpu_state, "input_size": [64, 64],
                "action_units": ACTION_UNITS, "split_seed": seed,
                "corpus_id": cid, "n_episodes": len(eps),
                "real_min_steps": REAL_MIN_STEPS}, out / "bc_best.pt")
    results = {
        "fit": evaluate(model, xf, yf, dev),
        "val": evaluate(model, xv, yv, dev),
        "test": evaluate(model, xt, yt, dev),
        "epochs_run": len(hist), "best_val_loss": best_val,
        "history": hist, "skipped": skipped,
        "frames_excluded": {
            "autopilot_log_mode_1": int(sum(e["n_auto"] for e in eps)),
            "crash_lead_in": int(sum(e["n_crash"] for e in eps)),
            "crash_trim_frames": CRASH_TRIM},
        "split": {"seed": seed, "test_seed": seed + 1, "val_fraction": VAL_FRACTION,
                  "n_fit": int(len(fit_i)), "n_val": int(len(val_i)),
                  "n_test": int(len(test_i)), "corpus_id": cid},
        "config": {"lr": LR, "batch": batch, "patience": patience,
                   "loss": "MSE(steer)*1.0 + MSE(throttle)*0.5",
                   "device": str(dev), "action_units": ACTION_UNITS},
    }
    provenance.write_result(out / "bc_results.json", results)
    print(f"  val {results['val']}  test {results['test']}")
    return results


# --------------------------------------------------------------- self-check

def _write_synth(root: Path, rng: np.random.Generator, extras: bool = False,
                 all_auto: bool = False) -> None:
    """4 sessions x 3 episodes x 60 frames, plus one 30-frame episode."""
    def episode(session: str, T: int, auto_half: bool = False,
                crash: bool = False, meta: dict | None = None,
                auto_all: bool = False) -> None:
        w = EpisodeWriter(root / session)
        ps = rng.integers(0, 160, T)
        steer = np.rint(((ps / 159.0) * 2 - 1) * 100).astype(np.int8)
        cmd = np.stack([steer, np.full(T, 30, np.int8)], axis=1)

        def img(p):
            im = np.full((120, 160, 3), 10, np.uint8)
            im[:, max(0, p - 3):min(160, p + 4)] = 255
            return im
        w.add_reset(img(int(ps[0])), action_dim=2)
        for k in range(1, T):
            w.add_step(img(int(ps[k])), np.zeros(2, np.float32), 0.0,
                       crash and k == T - 1, False)
        logs = {"log_cmd_next": cmd}
        if auto_half:
            logs["log_mode"] = (np.arange(T) >= T // 2).astype(np.uint8)
        if auto_all:
            logs["log_mode"] = np.ones(T, np.uint8)
        w.save(meta=meta, frame_logs=logs)
    for s in range(4):
        for _ in range(3):
            episode(f"sess{s}", 60, auto_all=all_auto)
    episode("short", 30)
    if extras:
        episode("auto", 60, auto_half=True)
        episode("crash", 60, crash=True)
        episode("fake", 60, meta={"fake_uno": True})


def self_check() -> None:
    t0 = time.time()
    # augment: flip must negate steer (and only steer), and mirror the image
    x = torch.zeros(6, 3, 64, 64)
    x[:, :, :, 10] = 1.0
    y = torch.tensor([[0.5, 0.3]] * 6)
    g = torch.Generator().manual_seed(0)
    xa, ya = augment(x, y, g, p_flip=1.0, max_shift=0)
    assert torch.allclose(ya[:, 0], torch.full((6,), -0.5)), ya
    assert torch.allclose(ya[:, 1], torch.full((6,), 0.3)), ya
    assert (xa[:, 0].argmax(-1) == 63 - 10).all(), "image not mirrored"
    xa, ya = augment(x, y, g, p_flip=0.0, max_shift=0)
    assert torch.allclose(ya, y) and (xa[:, 0].argmax(-1) == 10).all()
    assert y[0, 0] == 0.5, "augment mutated its input"
    xa, ya = augment(x, y, g)                    # defaults: shape/range intact
    assert xa.shape == x.shape and xa.min() >= 0 and xa.max() <= 1

    rng = np.random.default_rng(0)
    with tempfile.TemporaryDirectory() as td:
        data = Path(td) / "data"
        _write_synth(data, rng)
        eps, skipped = load_real(data)
        assert len(eps) == 12, len(eps)
        assert len(skipped) == 1 and "too short" in skipped[0]["reason"], skipped
        assert {e["track"] for e in eps} == {f"sess{s}" for s in range(4)}

        out = Path(td) / "out"
        res = run(data, out, epochs=60, seed=0, cpu=True, batch=32, patience=60)
        h = res["history"]
        first, last = h[0]["train_loss"], h[-1]["train_loss"]
        assert last < 0.5 * first, f"train loss fell only {first:.4f} -> {last:.4f}"
        assert res["val"]["steer_mae"] < 0.15, res["val"]
        assert res["skipped"] and "too short" in res["skipped"][0]["reason"]
        assert (out / "bc_results.json").exists()
        ck = torch.load(out / "bc_best.pt", map_location="cpu")
        for k in ("input_size", "action_units", "split_seed", "corpus_id",
                  "n_episodes", "real_min_steps"):
            assert k in ck, k
        BCNet().load_state_dict(ck["model"])
        assert res["frames_excluded"] == {"autopilot_log_mode_1": 0,
                                          "crash_lead_in": 0,
                                          "crash_trim_frames": CRASH_TRIM}, res
        keep_path = os.environ.get("BC_KEEP_PATH")
        if keep_path:
            shutil.copy(out / "bc_best.pt", keep_path)
            print(f"  kept checkpoint at {keep_path}")

        # frame selection: autopilot frames and the crash lead-in are not imitated
        d2 = Path(td) / "data2"
        _write_synth(d2, np.random.default_rng(1), extras=True)
        e2, sk2 = load_real(d2)
        by = {e["track"]: e for e in e2}
        assert "fake" not in by, "fake-hardware episode was loaded"
        assert any("fake hardware" in s["reason"] and "fake" in Path(s["path"]).parent.name
                   for s in sk2), sk2
        assert len(by["auto"]["x"]) == 30 and by["auto"]["n_auto"] == 30, by["auto"]["n_auto"]
        assert len(by["crash"]["x"]) == 60 - CRASH_TRIM and by["crash"]["n_crash"] == CRASH_TRIM
        assert len(by["sess0"]["x"]) == 60 and by["sess0"]["n_auto"] == 0
        # every frame autopilot (log_mode=1): clear SystemExit, not ZeroDivisionError
        d3 = Path(td) / "data3"
        _write_synth(d3, np.random.default_rng(2), all_auto=True)
        try:
            run(d3, Path(td) / "out3", epochs=1, seed=0, cpu=True)
        except SystemExit as e:
            assert "no trainable frames" in str(e), e
        else:
            raise AssertionError("empty fit set did not raise SystemExit")
    dt = time.time() - t0
    assert dt < 90, f"self_check took {dt:.1f}s"
    print(f"bc_real self_check: PASS (train loss {first:.4f} -> {last:.4f}, "
          f"val steer MAE {res['val']['steer_mae']:.4f}, {dt:.1f}s)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--data")
    ap.add_argument("--out")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        self_check()
        return 0
    if not (a.data and a.out):
        ap.error("--data and --out are required (or use --self-check)")
    run(a.data, a.out, a.epochs, a.seed, a.cpu)
    return 0


if __name__ == "__main__":
    sys.exit(main())
