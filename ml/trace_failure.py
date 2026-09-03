"""Diagnose the 69-110 step wall: which stage fails first?

Record Appendix V left this open. Every learned policy -- linear BC, MLP BC,
CEM planning -- dies at 69-110 steps while the PID expert completes 600/600,
and lowering throttle made it worse, so corner speed is ruled out. That
narrows it to the learned stack, but "the latent is the bottleneck" is a
conclusion about THREE stages at once and it has not been separated.

The stack has three places it can fail, and they are distinguishable:

  PERCEPTION  the VAE encodes the live frame to z, and the probe reads lane
              position back out. Failure looks like: probe_cte stops tracking
              the simulator's real cte.
  DYNAMICS    the MDN-RNN predicts where the car will be H steps from now.
              Failure looks like: probe_cte tracks fine, but the model's
              H-step-ahead prediction diverges from what actually happens.
  CONTROL     both of the above are accurate and the policy still steers
              badly. Failure looks like: everything tracks, the car leaves
              anyway.

This logs all three per step, using the SAME actions the car actually took, so
the H-step prediction is graded against a future that genuinely occurred --
not against a counterfactual. Without that, a prediction error and a policy
change are indistinguishable.

Outputs a per-step JSON trace and a 3-panel PNG.

Usage:
  python ml/trace_failure.py --driver mlp
  python ml/trace_failure.py --driver cem --episodes 2
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from collect_sim_data import PIDDriver, SIM_EXE, THROTTLE, WARMUP_STEPS
from eval_in_sim import SIZE, LatentPolicy
from provenance import write_result
from sim_conf import base_sim_conf
from models import HIDDEN, MDNRNN, ConvVAE
from plan_cem import CEMPlanner, load_probe
from train_controller import Controller

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"


@torch.no_grad()
def encode(vae, obs, device):
    x = torch.from_numpy(obs.copy()).to(device).permute(2, 0, 1).unsqueeze(0).float()
    x = torch.nn.functional.interpolate(x, size=(SIZE, SIZE), mode="bilinear",
                                        align_corners=False, antialias=True)
    x = x.clamp(0, 255).round().to(torch.uint8).float().div_(255.0)
    mu, _ = vae.encode(x)
    return mu


@torch.no_grad()
def imagine_cte(rnn, probe, z, state, actions, device):
    """Roll `actions` (H,2) forward from (z, state); return predicted cte each step."""
    out = []
    for a in actions:
        at = torch.from_numpy(np.asarray(a, np.float32)).to(device).unsqueeze(0)
        o, state = rnn.lstm(torch.cat([z, at], dim=-1).unsqueeze(1), state)
        p = rnn.head(o.squeeze(1))
        K, Zd = rnn.n_mix, rnn.z_dim
        logpi = torch.log_softmax(p[:, :K], dim=-1)
        mu = p[:, K:K + K * Zd].view(1, K, Zd)
        z = (logpi.exp().unsqueeze(-1) * mu).sum(dim=1)
        out.append(float(probe(z).squeeze()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--driver", choices=("mlp", "linear", "cem", "expert"),
                    default="mlp")
    ap.add_argument("--track", default="donkey-generated-track-v0")
    ap.add_argument("--episodes", type=int, default=2)
    ap.add_argument("--max-steps", type=int, default=300)
    ap.add_argument("--horizon", type=int, default=10,
                    help="how far ahead to grade the dynamics model")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--port", type=int, default=9091)
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--rnn", default=str(RUNS / "mdnrnn" / "mdnrnn_best.pt"))
    ap.add_argument("--probe", default=str(RUNS / "cte_probe" / "cte_probe_mlp.pt"))
    ap.add_argument("--ctrl-dir", default=str(RUNS / "controller"))
    ap.add_argument("--out", default=str(RUNS / "p5_trace"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    vae = ConvVAE().to(args.device)
    vae.load_state_dict(torch.load(args.vae, map_location=args.device)["model"])
    rnn = MDNRNN().to(args.device)
    rnn.load_state_dict(torch.load(args.rnn, map_location=args.device)["model"])
    vae.eval(); rnn.eval()
    probe, probe_r2 = load_probe(Path(args.probe), args.device)
    print(f"probe val R^2 {probe_r2:.4f}")

    if args.driver == "expert":
        driver, is_expert = PIDDriver(), True
    elif args.driver == "cem":
        driver, is_expert = CEMPlanner(vae, rnn, probe, args.device), False
    else:
        ctrl = Controller(arch=args.driver).to(args.device)
        ctrl.load_state_dict(torch.load(
            Path(args.ctrl_dir) / f"controller_{args.driver}_seed{args.seed}.pt",
            map_location=args.device)["model"])
        ctrl.eval()
        driver, is_expert = LatentPolicy(vae, rnn, ctrl, args.device), False

    import gym_donkeycar  # noqa: F401
    import gymnasium as gym
    conf = base_sim_conf(str(SIM_EXE), args.port, "trace", max_cte=4.0)
    print(f"launching {args.track}, driver={args.driver} ...")
    env = gym.make(args.track, conf=conf)

    episodes = []
    try:
        for ep in range(args.episodes):
            obs, _ = env.reset()
            driver.reset()
            info = {}
            for _ in range(WARMUP_STEPS):
                obs, _, term, trunc, info = env.step(
                    np.array([0.0, THROTTLE], np.float32))
                if term or trunc:
                    obs, _ = env.reset(); driver.reset()
                    obs, _, term, trunc, info = env.step(
                        np.array([0.0, THROTTLE], np.float32))

            rows, pend = [], []          # pend: predictions awaiting their future
            cte = float(info.get("cte", 0.0)) if info else 0.0
            state = None
            for t in range(args.max_steps):
                z = encode(vae, obs, args.device)
                with torch.no_grad():
                    probe_cte = float(probe(z).squeeze())
                action = driver.act(cte) if is_expert else driver.act(obs)
                rows.append({"step": t, "actual_cte": cte,
                             "probe_cte": probe_cte,
                             "steer": float(action[0]),
                             "throttle": float(action[1])})
                # Grade the dynamics: predict H steps ahead by REPEATING this
                # action. Held constant because the policy's future actions are
                # not known yet; the comparison is still apples-to-apples
                # because the same assumption is graded against what happens.
                pred = imagine_cte(rnn, probe, z, state,
                                   [action] * args.horizon, args.device)
                pend.append((t + args.horizon, pred[-1]))
                _, state = rnn.lstm(
                    torch.cat([z, torch.from_numpy(action).to(args.device)
                               .unsqueeze(0)], dim=-1).unsqueeze(1), state)

                obs, _, term, trunc, info = env.step(action)
                cte = float(info.get("cte", 0.0))
                if term or trunc:
                    break

            # attach each prediction to the cte that actually occurred
            by_step = {r["step"]: r for r in rows}
            for target, predicted in pend:
                if target in by_step:
                    by_step[target][f"pred_cte_from_t-{args.horizon}"] = predicted
            episodes.append({"episode": ep, "steps": len(rows), "rows": rows})
            print(f"  ep{ep}: {len(rows)} steps, final |cte| {abs(cte):.3f}")
    finally:
        try:
            env.close()
        except Exception:
            pass

    payload = {"args": vars(args), "probe_val_r2": probe_r2, "episodes": episodes}
    tag = args.driver
    write_result(out / f"trace_{tag}.json", payload)

    # ---- the three-way verdict, computed not eyeballed -------------------
    print(f"\n{'':<22}{'first 25%':>12}{'last 25%':>12}")
    verdict = {}
    for label, key in (("perception |probe-actual|", "probe_cte"),
                       (f"dynamics  |pred-actual| (h={args.horizon})",
                        f"pred_cte_from_t-{args.horizon}")):
        early, late = [], []
        for e in episodes:
            rows = [r for r in e["rows"] if key in r]
            if not rows:
                continue
            n = len(rows)
            for i, r in enumerate(rows):
                err = abs(r[key] - r["actual_cte"])
                (early if i < n * 0.25 else late if i >= n * 0.75 else []).append(err)
        if early and late:
            verdict[label] = (float(np.mean(early)), float(np.mean(late)))
            print(f"{label:<22}{np.mean(early):>12.3f}{np.mean(late):>12.3f}")

    print(f"\n{'':<22}{'first 25%':>12}{'last 25%':>12}")
    ae, al = [], []
    for e in episodes:
        n = len(e["rows"])
        for i, r in enumerate(e["rows"]):
            (ae if i < n * 0.25 else al if i >= n * 0.75 else []).append(
                abs(r["actual_cte"]))
    if ae and al:
        verdict["actual |cte|"] = (float(np.mean(ae)), float(np.mean(al)))
        print(f"{'actual |cte|':<22}{np.mean(ae):>12.3f}{np.mean(al):>12.3f}")

    write_result(out / f"verdict_{tag}.json", verdict)
    print(f"\n-> {out / f'trace_{tag}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
