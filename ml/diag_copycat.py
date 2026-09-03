"""Is the controller a COPYCAT? (tests the hypothesis the research brief raised)

The brief surfaced Wen et al., "Fighting Copycat Agents in Behavioral Cloning
from Observation Histories" (NeurIPS 2020, arXiv:2010.14876): a BC policy given
observation HISTORIES learns to predict the PREVIOUS expert action, and
held-out likelihood improves while closed-loop reward falls -- explicitly not
overfitting. This controller consumes the MDN-RNN hidden state `h`, and every
arm through Appendix AA shows the signature: val MSE ~0.0018 and steadily
improving, driving flat and terrible at ~190 of 600 steps.

**This diagnoses it WITHOUT retraining**, because the decisive comparison is
already available in the corpus. Expert steering is temporally smooth, so the
previous action is a strong predictor of the current one for free. If a
trivial "repeat a[t-1]" predictor matches the controller's MSE, then the
controller's impressive held-out number is worth nothing: it is exploiting
temporal autocorrelation, not perceiving the road.

Four numbers on the SAME held-out frames:

  ctrl -> a[t]      the reported val MSE, i.e. what the model claims
  a[t-1] -> a[t]    the trivial copy baseline. **THE KEY COMPARISON.**
  ctrl -> a[t-1]    is the model literally predicting the PREVIOUS action?
                    Lower than `ctrl -> a[t]` is direct copycat evidence.
  ctrl(h=0) -> a[t] serve-time ablation of the history input. Crude (the model
                    was trained with h, so h=0 is off-distribution) but it
                    bounds how much work `h` is doing.

Reported as MSE and as skill = 1 - MSE/var(a[t]), so "beats the trivial
baseline" is legible without holding the units in your head.

Usage:
  python ml/diag_copycat.py
  python ml/diag_copycat.py --ctrl ml/runs/cl_aug/controller_mlp_seed0.pt \\
                            --proc ml/data/proc_aug
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from models import MDNRNN, ConvVAE, Z_DIM
from splits import (fit_val_episodes, load_cached_mu, load_proc,
                    split_seed_of)
from train_controller import Controller, rnn_states

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"


def mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(((a - b) ** 2).mean(axis=-1).mean())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proc", default=str(REPO / "ml" / "data" / "proc"))
    ap.add_argument("--ctrl", default=str(RUNS / "cl_base" / "controller_mlp_seed0.pt"))
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--rnn", default=str(RUNS / "mdnrnn" / "mdnrnn_best.pt"))
    ap.add_argument("--out", default=str(RUNS / "diag_copycat"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    proc = Path(args.proc)

    ck = torch.load(args.ctrl, map_location=args.device)
    arch = ck.get("args", {}).get("arch", "mlp")
    model = Controller(arch=arch).to(args.device)
    model.load_state_dict(ck["model"])
    model.eval()

    vae_ckpt = torch.load(args.vae, map_location=args.device)
    rnn = MDNRNN().to(args.device)
    rnn.load_state_dict(torch.load(args.rnn, map_location=args.device)["model"])
    rnn.eval()

    _, act, eps, tracks = load_proc("train", proc=proc)
    expert_path = proc / "train_actions_expert.npy"
    if expert_path.exists():
        act = np.load(expert_path)
    mu_path = proc / "train_mu.npy"
    # Cold audit finding 1: check the cache's encoder fingerprint before
    # reusing it, same as train_mdnrnn.py does when it writes the cache.
    mu = load_cached_mu("train", args.vae, proc=proc)
    if mu is None:
        imgs, _, _, _ = load_proc("train", proc=proc)
        vae = ConvVAE().to(args.device)
        vae.load_state_dict(vae_ckpt["model"])
        vae.eval()
        mu = np.zeros((len(imgs), Z_DIM), np.float32)
        with torch.no_grad():
            for s in range(0, len(imgs), 512):
                e = min(s + 512, len(imgs))
                x = torch.from_numpy(np.array(imgs[s:e])).to(args.device)
                mu[s:e] = vae.encode(
                    x.permute(0, 3, 1, 2).float().div_(255.0))[0].cpu().numpy()
        del imgs

    split_seed = split_seed_of(vae_ckpt)
    _, val_eps = fit_val_episodes(tracks, seed=split_seed)
    val_i, val_h = rnn_states(rnn, mu, act, eps, val_eps, args.device)

    # a[t-1], built per EPISODE so no frame is paired with the last action of
    # the previous episode -- that transition never happened.
    prev_of = np.full(len(act), -1, np.int64)
    for s0, n0 in eps:
        idx = np.arange(s0, s0 + n0)
        prev_of[idx[1:]] = idx[:-1]
    has_prev = prev_of[val_i] >= 0
    vi = val_i[has_prev]
    hh = val_h[has_prev]
    a_t = act[vi]
    a_prev = act[prev_of[vi]]
    print(f"held-out frames with a valid previous action: {len(vi):,} "
          f"(dropped {int((~has_prev).sum())} episode-start frames)")

    with torch.no_grad():
        z = torch.from_numpy(mu[vi]).to(args.device)
        h = torch.from_numpy(hh).to(args.device)
        pred = model(z, h).cpu().numpy()
        pred_h0 = model(z, torch.zeros_like(h)).cpu().numpy()

    var = float(act[vi].var(axis=0).mean())
    rows = [
        ("controller -> a[t]      (the reported val MSE)", mse(pred, a_t)),
        ("a[t-1]     -> a[t]      (TRIVIAL COPY BASELINE)", mse(a_prev, a_t)),
        ("controller -> a[t-1]    (is it predicting the PREVIOUS action?)",
         mse(pred, a_prev)),
        ("controller(h=0) -> a[t] (serve-time history ablation)",
         mse(pred_h0, a_t)),
    ]
    print(f"\n{'comparison':<62}{'MSE':>10}{'skill':>8}")
    for label, m in rows:
        print(f"{label:<62}{m:>10.6f}{1 - m / var:>8.3f}")
    print(f"\nvar(a[t]) = {var:.6f};  skill = 1 - MSE/var")

    m_ctrl, m_copy, m_prev, m_h0 = [m for _, m in rows]
    print()
    # A controller that cannot beat "repeat the last action" has learned
    # nothing about the road, however good its MSE looks in isolation.
    if m_ctrl >= m_copy:
        verdict = (f"COPYCAT CONFIRMED. The controller ({m_ctrl:.6f}) does NOT "
                   f"beat the trivial repeat-last-action baseline "
                   f"({m_copy:.6f}). Its held-out MSE is temporal "
                   f"autocorrelation, not perception. This is a rival "
                   f"explanation for the whole P5 wall and it does not involve "
                   f"the encoder at all.")
    elif m_prev < m_ctrl:
        verdict = (f"PARTIAL COPYCAT. The controller predicts a[t-1] "
                   f"({m_prev:.6f}) BETTER than a[t] ({m_ctrl:.6f}) -- it is "
                   f"tracking the previous action -- but still beats the "
                   f"trivial baseline ({m_copy:.6f}). The history input is "
                   f"doing harm; the z-only ablation is the next test.")
    else:
        ratio = m_copy / m_ctrl
        verdict = (f"NOT A COPYCAT on this evidence. The controller "
                   f"({m_ctrl:.6f}) beats repeat-last-action ({m_copy:.6f}) by "
                   f"{ratio:.2f}x and predicts a[t] better than a[t-1]. Its "
                   f"MSE reflects real signal, so the P5 wall needs a "
                   f"different explanation.")
    print(f"VERDICT: {verdict}")
    print(f"\nhistory contribution at serve time: MSE {m_ctrl:.6f} with h, "
          f"{m_h0:.6f} with h=0 ({100*(m_h0-m_ctrl)/m_ctrl:+.0f}%)")

    (out / "diag_copycat.json").write_text(json.dumps(
        {"args": vars(args), "n_frames": len(vi), "var_action": var,
         "mse_ctrl_vs_at": m_ctrl, "mse_prev_vs_at": m_copy,
         "mse_ctrl_vs_prev": m_prev, "mse_ctrl_h0_vs_at": m_h0,
         "verdict": verdict}, indent=2))
    print(f"-> {out / 'diag_copycat.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
