"""SIM-POC P5 step 3: CEM planning through the learned dynamics.

Evan's proposal, 2026-08-07: "give the AI a large incentive to stay in the
middle of the track and a smaller incentive to keep sideways acceleration low."

Behavioural cloning cannot take an incentive -- it minimises distance to the
expert's recorded actions and has no notion of good or bad. This file is where
an incentive becomes expressible: the planner IMAGINES candidate futures
through the MDN-RNN and picks the action sequence that scores best under a
cost function we write down.

HOW IT WORKS, each control step (model-predictive control):
  1. encode the live frame -> z, carry the LSTM state h
  2. sample N candidate steering sequences of length H
  3. roll all N through the MDN-RNN in parallel -> imagined z trajectories
  4. score each with the cost below, using the z->cte probe
  5. keep the best `elite` fraction, refit the sampling distribution, repeat
  6. execute only the FIRST action of the winner, then replan next step

THE COST FUNCTION, and the honest weighting:
    cost = W_CTE * mean(cte^2) + W_SMOOTH * mean(dsteer^2)

`W_CTE >> W_SMOOTH` deliberately. Evan asked for a small lateral-acceleration
term, and it is here -- but the measurement that prompted it did not hold up.
The linear controller was NOT swerving: measured 6.57 steering reversals per
100 steps against the expert's 7.67, with a SMALLER mean |dsteer| (0.107 vs
0.129). It was drifting off-centre and failing to recover, not overcorrecting.
So a heavy smoothness penalty would suppress exactly the corrections the car
needs. It is kept small, and `--w-smooth` makes its real cost measurable
rather than assumed.

WHY THIS SHOULD BEAT BC, AND THE PREDICTION IT MAKES: the MLP controller died
at step 69.3 +- 1.2 across nine episodes and three independently trained
seeds -- a deterministic wall, almost certainly the first hard corner, while
holding the lane well (mean|cte| 0.435 vs expert 0.381) everywhere before it.
A reactive policy cannot see a corner coming; a planner rolling H steps ahead
can. If planning does NOT clear that wall, the world model's forward
predictions are not accurate enough to plan through, which is a real and
reportable result about the model rather than about the controller.

Usage:
  python ml/plan_cem.py --smoke
  python ml/plan_cem.py --seeds 0 1 2 --episodes 3
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from collect_sim_data import (PIDDriver, SIM_EXE, STEER_LIMIT, THROTTLE,
                              THROTTLE_CORNER, WARMUP_STEPS)
from eval_in_sim import SIZE, run_episode
from sim_conf import base_sim_conf
from models import HIDDEN, MDNRNN, Z_DIM, ConvVAE

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"


def load_probe(path: Path, device: str):
    ck = torch.load(path, map_location=device)
    arch = ck.get("arch", "mlp")
    w = ck.get("width", 256)
    if arch == "linear":
        m = nn.Linear(Z_DIM, 1)
    else:
        m = nn.Sequential(nn.Linear(Z_DIM, w), nn.ReLU(inplace=True),
                          nn.Linear(w, w), nn.ReLU(inplace=True),
                          nn.Linear(w, 1))
    m.load_state_dict(ck["model"])
    m.to(device).eval()
    return m, ck.get("val_r2", float("nan"))


class CEMPlanner:
    """Model-predictive control over the MDN-RNN's imagined latents."""

    def __init__(self, vae, rnn, probe, device, *, horizon=12, candidates=256,
                 iters=3, elite_frac=0.125, w_cte=1.0, w_smooth=0.05,
                 init_std=0.4, min_std=0.05,
                 throttle=THROTTLE, throttle_corner=THROTTLE_CORNER):
        self.vae, self.rnn, self.probe, self.device = vae, rnn, probe, device
        self.H, self.N, self.iters = horizon, candidates, iters
        self.n_elite = max(2, int(candidates * elite_frac))
        self.w_cte, self.w_smooth = w_cte, w_smooth
        self.init_std, self.min_std = init_std, min_std
        self.throttle, self.throttle_corner = throttle, throttle_corner
        self.reset()

    def reset(self):
        self._state = None
        self._h = torch.zeros(1, HIDDEN, device=self.device)
        self._prev_steer = 0.0
        self._mean = None            # warm-started plan, shifted each step

    @torch.no_grad()
    def _rollout_cost(self, z0, h0, c0, steers):
        """Imagine `steers` (N,H) forward and return each candidate's cost."""
        N, H = steers.shape
        z = z0.expand(N, -1).contiguous()
        state = (h0.expand(N, -1).contiguous().unsqueeze(0),
                 c0.expand(N, -1).contiguous().unsqueeze(0))
        cte_sq = torch.zeros(N, device=self.device)
        for t in range(H):
            s = steers[:, t:t + 1]
            # Throttle follows the expert's own rule rather than being planned:
            # it keeps the search 1-D (steering is what lane-following needs)
            # and matches the action distribution the dynamics were trained on.
            thr = torch.where(s.abs() > 0.5,
                              torch.full_like(s, self.throttle_corner),
                              torch.full_like(s, self.throttle))
            a = torch.cat([s, thr], dim=-1)
            out, state = self.rnn.lstm(
                torch.cat([z, a], dim=-1).unsqueeze(1), state)
            p = self.rnn.head(out.squeeze(1))
            K, Zd = self.rnn.n_mix, self.rnn.z_dim
            logpi = torch.log_softmax(p[:, :K], dim=-1)
            mu = p[:, K:K + K * Zd].view(N, K, Zd)
            # Mixture MEAN, not a sample: planning on sampled futures makes the
            # cost stochastic and CEM then chases noise instead of the signal.
            z = (logpi.exp().unsqueeze(-1) * mu).sum(dim=1)
            cte_sq += self.probe(z).squeeze(-1) ** 2
        d = torch.diff(steers, dim=1, prepend=steers.new_full((N, 1), self._prev_steer))
        return self.w_cte * (cte_sq / H) + self.w_smooth * (d ** 2).mean(dim=1)

    @torch.no_grad()
    def act(self, obs: np.ndarray) -> np.ndarray:
        x = torch.from_numpy(obs.copy()).to(self.device)
        x = x.permute(2, 0, 1).unsqueeze(0).float()
        x = torch.nn.functional.interpolate(
            x, size=(SIZE, SIZE), mode="bilinear", align_corners=False,
            antialias=True)
        x = x.clamp(0, 255).round().to(torch.uint8).float().div_(255.0)
        z, _ = self.vae.encode(x)

        c0 = (self._state[1][-1] if self._state is not None
              else torch.zeros(1, HIDDEN, device=self.device))
        mean = (self._mean if self._mean is not None
                else torch.zeros(self.H, device=self.device))
        std = torch.full((self.H,), self.init_std, device=self.device)

        for _ in range(self.iters):
            cand = (mean.unsqueeze(0)
                    + std.unsqueeze(0) * torch.randn(self.N, self.H, device=self.device))
            cand = cand.clamp(-STEER_LIMIT, STEER_LIMIT)
            cost = self._rollout_cost(z, self._h, c0, cand)
            elite = cand[cost.topk(self.n_elite, largest=False).indices]
            mean = elite.mean(dim=0)
            std = elite.std(dim=0).clamp_min(self.min_std)

        steer = float(mean[0].clamp(-STEER_LIMIT, STEER_LIMIT))
        thr = self.throttle_corner if abs(steer) > 0.5 else self.throttle
        action = np.array([steer, thr], dtype=np.float32)

        # Warm start: shift the plan forward one step. Re-solving from scratch
        # every step throws away a good solution and makes the policy jittery.
        self._mean = torch.cat([mean[1:], mean[-1:]])
        self._prev_steer = steer
        _, self._state = self.rnn.lstm(
            torch.cat([z, torch.from_numpy(action).to(self.device).unsqueeze(0)],
                      dim=-1).unsqueeze(1), self._state)
        self._h = self._state[0][-1]
        return action


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", default="donkey-generated-track-v0")
    ap.add_argument("--episodes", type=int, default=3)
    ap.add_argument("--max-steps", type=int, default=600)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--port", type=int, default=9091)
    ap.add_argument("--horizon", type=int, default=12)
    ap.add_argument("--candidates", type=int, default=256)
    ap.add_argument("--iters", type=int, default=3)
    ap.add_argument("--w-cte", type=float, default=1.0)
    ap.add_argument("--w-smooth", type=float, default=0.05)
    ap.add_argument("--throttle", type=float, default=THROTTLE,
                    help="straight-line throttle. The expert's own tuning "
                         "found throttle dominates gains (record Appendix M): "
                         "at 0.32 it left the road under EVERY gain setting. "
                         "Lowering this tests whether the learned policies' "
                         "wall is corner speed rather than representation.")
    ap.add_argument("--throttle-corner", type=float, default=THROTTLE_CORNER)
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--rnn", default=str(RUNS / "mdnrnn" / "mdnrnn_best.pt"))
    ap.add_argument("--probe", default=str(RUNS / "cte_probe" / "cte_probe_mlp.pt"))
    ap.add_argument("--out", default=str(RUNS / "p5_cem"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--with-expert", action="store_true",
                    help="also run the PID expert for a same-session baseline")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.seeds, args.episodes, args.max_steps = [0], 1, 200

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    vae = ConvVAE().to(args.device)
    vae.load_state_dict(torch.load(args.vae, map_location=args.device)["model"])
    rnn = MDNRNN().to(args.device)
    rnn.load_state_dict(torch.load(args.rnn, map_location=args.device)["model"])
    vae.eval(); rnn.eval()
    probe, probe_r2 = load_probe(Path(args.probe), args.device)
    print(f"probe: {Path(args.probe).name}  val R^2 {probe_r2:.4f}")
    if probe_r2 < 0.5:
        print("WARNING: planning on a probe this weak optimises noise.")

    import gym_donkeycar  # noqa: F401
    import gymnasium as gym
    conf = base_sim_conf(str(SIM_EXE), args.port, "p5cem", max_cte=4.0)
    print(f"launching {args.track} (H={args.horizon}, N={args.candidates}, "
          f"w_cte={args.w_cte}, w_smooth={args.w_smooth}) ...")
    env = gym.make(args.track, conf=conf)

    results = {"cem": []}
    if args.with_expert:
        results["expert"] = []
    try:
        for seed in args.seeds:
            torch.manual_seed(seed)
            np.random.seed(seed)
            drivers = [("cem", CEMPlanner(
                vae, rnn, probe, args.device, horizon=args.horizon,
                candidates=args.candidates, iters=args.iters,
                w_cte=args.w_cte, w_smooth=args.w_smooth,
                throttle=args.throttle,
                throttle_corner=args.throttle_corner), False)]
            if args.with_expert:
                drivers.append(("expert", PIDDriver(), True))
            for name, driver, is_expert in drivers:
                for ep in range(args.episodes):
                    t0 = time.time()
                    r = run_episode(env, driver, args.max_steps, is_expert)
                    r.update(seed=seed, episode=ep,
                             seconds=round(time.time() - t0, 1))
                    results[name].append(r)
                    print(f"  seed {seed} {name:7s} ep{ep}: {r['steps']:4d} steps, "
                          f"mean|cte| {r['mean_abs_cte']:.3f}, "
                          f"rev/100 {r['reversals_per_100']:.2f}, "
                          f"{r['seconds']:.0f}s"
                          f"{'  (survived)' if r['survived'] else ''}")
    finally:
        try:
            env.close()
        except Exception:
            pass

    print(f"\n{'driver':<8} {'eps':>4} {'steps (mean+-sd)':>20} {'mean|cte|':>10} "
          f"{'rev/100':>9} {'survived':>10}")
    summary = {}
    for name, rows in results.items():
        steps = np.array([r["steps"] for r in rows], float)
        ctes = np.array([r["mean_abs_cte"] for r in rows], float)
        rev = np.array([r["reversals_per_100"] for r in rows], float)
        surv = sum(r["survived"] for r in rows)
        summary[name] = {"episodes": len(rows), "steps_mean": float(steps.mean()),
                         "steps_sd": float(steps.std()),
                         "cte_mean": float(np.nanmean(ctes)),
                         "reversals_per_100": float(rev.mean()),
                         "survived": int(surv)}
        print(f"{name:<8} {len(rows):>4} {steps.mean():>12.1f} +-{steps.std():<5.1f} "
              f"{np.nanmean(ctes):>10.3f} {rev.mean():>9.2f} {surv:>7}/{len(rows)}")

    (out / "p5_cem.json").write_text(json.dumps(
        {"args": vars(args), "probe_val_r2": probe_r2,
         "per_episode": results, "summary": summary,
         "no_transfer_claim": (
             "Simulated only. Nothing here is evidence about the physical "
             "car.")}, indent=2))
    print(f"\n-> {out / 'p5_cem.json'}")
    print("NOTE: simulated only. No transfer claim is made or implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
