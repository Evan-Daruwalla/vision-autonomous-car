"""SIM-POC P5 done-check: drive the learned controller in the simulator and
compare it against the P2 scripted expert on the same tracks.

This is the only script in the project that closes the loop: every earlier
evaluation measured the world model against RECORDED data, where the actions
were the expert's and a bad prediction cost nothing. Here the policy's own
output determines the next observation, so errors compound and a model that
looked fine offline can drive straight off the road.

WHAT IS BEING COMPARED
  expert      the PID lane-follower from collect_sim_data.py -- the same code
              that produced the training corpus, so it is both the baseline
              AND the thing the controller was cloned from
  controller  linear policy on [z, h]: ConvVAE encodes the live frame to z,
              the MDN-RNN carries h forward online, C emits (steer, throttle)

**The controller is trained by behavioural cloning, so the expert is a
CEILING, not a rival.** A result at or slightly below expert performance is
the expected outcome and still proves the pipeline. Beating it would be
surprising and would need explaining, not celebrating.

>=3 SEEDS, because this is a comparative claim. Single-seed comparisons of
driving policies are unreliable (record: routing research found seed variance
reaching tens of points), and testing.md makes >=3 the standing rule for P5.
The expert is deterministic given a track, but the simulator's reset pose is
not, so the expert is re-run per seed too rather than measured once.

METRICS
  steps       how long the car stayed on the road before max_cte terminated
              it, capped at --max-steps. The primary metric: it is what
              "did it drive" actually means.
  mean|cte|   average absolute cross-track error over the episode -- how
              well it held the lane while it survived. Lower is better, and
              it is only meaningful alongside `steps` (a car that dies
              immediately can post an excellent mean|cte|).

NO TRANSFER CLAIM. Everything here is simulated. Nothing in this file says
anything about the physical car, and a policy that drives well in the Donkey
simulator is not evidence that it will drive on Evan's track -- that is what
M3/M4 on real logs are for. Sim-trained policies losing to classical control
on real hardware is documented (F1TENTH/RoboRacer), and is exactly why the
PRD keeps sim-RL optional and the capstone on the car's own data.

Usage:
  python ml/eval_in_sim.py --episodes 3 --seeds 0 1 2
  python ml/eval_in_sim.py --smoke        # 1 seed, 1 episode, 200 steps
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from collect_sim_data import (MAX_EPISODE_STEPS, PIDDriver, SIM_EXE,
                              THROTTLE, WARMUP_STEPS)
from models import HIDDEN, MDNRNN, ConvVAE
from train_controller import Controller

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"
SIZE = 64


class LatentPolicy:
    """V -> M -> C, driven online. Maintains the LSTM state across steps."""

    def __init__(self, vae: ConvVAE, rnn: MDNRNN, ctrl: Controller, device: str):
        self.vae, self.rnn, self.ctrl, self.device = vae, rnn, ctrl, device
        self.reset()

    def reset(self):
        self._state = None
        self._h = torch.zeros(1, HIDDEN, device=self.device)

    @torch.no_grad()
    def act(self, obs: np.ndarray) -> np.ndarray:
        # Same preprocessing as ml/preprocess.py: anisotropic squash to 64x64,
        # antialiased. Any mismatch here and the encoder sees a distribution it
        # was never trained on -- the classic silent train/serve skew.
        x = torch.from_numpy(obs.copy()).to(self.device)
        x = x.permute(2, 0, 1).unsqueeze(0).float()
        x = torch.nn.functional.interpolate(
            x, size=(SIZE, SIZE), mode="bilinear", align_corners=False,
            antialias=True)
        # **Quantise to uint8 before scaling, exactly as preprocess.py did.**
        # The corpus was written as uint8 and only divided by 255 at load, so
        # skipping the round trip here feeds the encoder continuous values it
        # never saw in training. A small skew, but it is a train/serve
        # mismatch in the one place that matters -- the live observation.
        x = x.clamp(0, 255).round().to(torch.uint8).float().div_(255.0)
        mu, _ = self.vae.encode(x)                      # (1, Z)

        # C sees h BEFORE the RNN consumes this step -- the same causal
        # convention train_controller.py used. Getting this backwards here
        # would silently change the policy's input distribution at serve time.
        action = self.ctrl(mu, self._h).squeeze(0).cpu().numpy()

        _, self._state = self.rnn.lstm(
            torch.cat([mu, torch.from_numpy(action).to(self.device).unsqueeze(0)],
                      dim=-1).unsqueeze(1), self._state)
        self._h = self._state[0][-1]                    # (1, HIDDEN)
        return action.astype(np.float32)


def run_episode(env, driver, max_steps: int, is_expert: bool,
                min_step_s: float = 0.0) -> dict:
    """One episode. Returns steps survived and mean |cte|.

    **The reproducibility problem this was built for is real.** Measured
    2026-08-10: the same MLP checkpoint, through this same script, scored 69.3
    steps at a 13.2 Hz loop and 187.2 at 16.7 Hz -- a 2.7x swing driven by how
    fast the machine ran inference that day. The PID expert, which does no
    neural forward pass, sat at the sim's own 18.87 Hz in both runs and
    returned 600/600 identically. So step counts are only comparable between
    runs whose achieved `control_hz` is close.

    **`min_step_s` DOES NOT FIX IT, and must not be used to equalise two arms.**
    Sleeping out the remainder of an iteration is NOT the same manipulation as
    "the same loop, slower". The loop normally runs flat out and stays in
    lockstep with the sim's frame production, because `observe()` blocks for
    the next frame. Adding any sleep breaks that lockstep: the sim produces a
    frame while the loop idles, the next `observe()` returns an already-stale
    one, and the two clocks beat against each other.

    Measured, and it is a cliff rather than a slope: the expert throttled to
    **18.5 Hz -- a 2% reduction from its natural 18.87 -- collapses from 9/9
    survived to 0/2, with mean|cte| 0.361 -> 0.988.** Smooth control-rate
    sensitivity does not do that. Numbers taken under a throttle describe the
    desynchronised regime, not a slower controller.

    Kept because it MEASURES the artifact and guards against assuming the
    harness is rate-robust. To compare two policies fairly, run them
    back-to-back unthrottled on an idle machine and check the reported
    `control_hz` agrees between them.
    """
    obs, _ = env.reset()
    driver.reset()
    info = {}
    for _ in range(WARMUP_STEPS):
        obs, _, term, trunc, info = env.step(np.array([0.0, THROTTLE], np.float32))
        if term or trunc:
            obs, _ = env.reset()
            driver.reset()
            obs, _, term, trunc, info = env.step(
                np.array([0.0, THROTTLE], np.float32))

    ctes, steers, steps = [], [], 0
    cte = float(info.get("cte", 0.0)) if info else 0.0
    t_start = time.time()
    for _ in range(max_steps):
        t_iter = time.time()
        action = driver.act(cte) if is_expert else driver.act(obs)
        obs, _, term, trunc, info = env.step(action)
        cte = float(info.get("cte", 0.0))
        ctes.append(abs(cte))
        steers.append(float(action[0]))
        steps += 1
        if term or trunc:
            break
        if min_step_s > 0.0:
            slack = min_step_s - (time.time() - t_iter)
            if slack > 0:
                time.sleep(slack)
    elapsed = time.time() - t_start
    # Steering smoothness, so "it swerves" is a measured number rather than an
    # impression. reversals = sign changes per 100 steps (oscillation);
    # mean_abs_dsteer = average step-to-step steering change (control effort).
    s = np.asarray(steers, float)
    reversals = int((np.diff(np.sign(s)) != 0).sum()) if len(s) > 1 else 0
    return {"steps": steps,
            "mean_abs_cte": float(np.mean(ctes)) if ctes else float("nan"),
            "reversals_per_100": round(100.0 * reversals / max(1, len(s)), 2),
            "mean_abs_dsteer": float(np.abs(np.diff(s)).mean()) if len(s) > 1 else 0.0,
            # Always reported, never optional: a step count is uninterpretable
            # without the rate it was produced at (see the docstring).
            "control_hz": round(steps / elapsed, 2) if elapsed > 0 else 0.0,
            "survived": steps >= max_steps}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", default="donkey-generated-track-v0")
    ap.add_argument("--episodes", type=int, default=3)
    ap.add_argument("--max-steps", type=int, default=600)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--port", type=int, default=9091)
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--rnn", default=str(RUNS / "mdnrnn" / "mdnrnn_best.pt"))
    ap.add_argument("--ctrl-dir", default=str(RUNS / "controller"))
    ap.add_argument("--control-hz", type=float, default=0.0,
                    help="DIAGNOSTIC ONLY. Throttle the control loop to this "
                         "rate by sleeping. Do NOT use it to equalise two arms "
                         "of a comparison: sleeping desynchronises the loop "
                         "from the sim's frame production and is a cliff, not "
                         "a slope (the expert dies at a 2%% throttle). See "
                         "run_episode's docstring. 0 = normal.")
    ap.add_argument("--archs", nargs="+", default=["linear", "mlp"],
                    choices=("linear", "mlp"),
                    help="controller architectures to evaluate alongside the "
                         "expert. linear is the paper's C; mlp tests whether "
                         "its failure is architectural (see train_controller)")
    ap.add_argument("--out", default=str(RUNS / "p5_eval"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.seeds, args.episodes, args.max_steps = [0], 1, 200

    min_step_s = 1.0 / args.control_hz if args.control_hz > 0 else 0.0
    if min_step_s:
        print(f"WARNING: --control-hz {args.control_hz:g} throttles by SLEEPING, "
              f"which desynchronises the loop from the sim's frame production. "
              f"These numbers describe that regime, NOT a slower controller, "
              f"and are not comparable to unthrottled runs.")
    print("NOTE: step counts are only comparable between runs whose achieved "
          "control_hz agrees (a 2.7x swing across 13.2 vs 16.7 Hz was measured "
          "2026-08-10). Check the ctrl Hz column before comparing anything.")

    if len(args.seeds) < 3 and not args.smoke:
        print(f"WARNING: {len(args.seeds)} seed(s). P5 is a COMPARATIVE claim "
              f"and testing.md requires >=3; this result is not publishable "
              f"as a comparison.")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    vae = ConvVAE().to(args.device)
    vae.load_state_dict(torch.load(args.vae, map_location=args.device)["model"])
    rnn = MDNRNN().to(args.device)
    rnn.load_state_dict(torch.load(args.rnn, map_location=args.device)["model"])
    vae.eval(); rnn.eval()

    import gym_donkeycar  # noqa: F401  registers the envs
    import gymnasium as gym

    conf = {"exe_path": str(SIM_EXE), "host": "127.0.0.1", "port": args.port,
            "start_delay": 10.0, "car_name": "p5", "max_cte": 4.0}
    print(f"launching {args.track} ...")
    env = gym.make(args.track, conf=conf)

    results = {"expert": []}
    for a in args.archs:
        results[f"controller_{a}"] = []
    try:
        for seed in args.seeds:
            torch.manual_seed(seed)
            np.random.seed(seed)

            drivers = [("expert", PIDDriver(), True)]
            for arch in args.archs:
                ctrl_path = Path(args.ctrl_dir) / f"controller_{arch}_seed{seed}.pt"
                if not ctrl_path.exists():
                    print(f"FAIL: no {arch} controller for seed {seed} at {ctrl_path}")
                    return 1
                ctrl = Controller(arch=arch).to(args.device)
                ctrl.load_state_dict(torch.load(
                    ctrl_path, map_location=args.device)["model"])
                ctrl.eval()
                drivers.append((f"controller_{arch}",
                                LatentPolicy(vae, rnn, ctrl, args.device), False))

            for name, driver, is_expert in drivers:
                for ep in range(args.episodes):
                    t0 = time.time()
                    r = run_episode(env, driver, args.max_steps, is_expert,
                                    min_step_s=min_step_s)
                    r.update(seed=seed, episode=ep,
                             seconds=round(time.time() - t0, 1))
                    results[name].append(r)
                    print(f"  seed {seed} {name:10s} ep{ep}: "
                          f"{r['steps']:4d} steps, mean|cte| "
                          f"{r['mean_abs_cte']:.3f}"
                          f"{'  (survived)' if r['survived'] else ''}")
    finally:
        try:
            env.close()
        except Exception:
            pass

    print(f"\n{'driver':<18} {'eps':>4} {'steps (mean+-sd)':>19} "
          f"{'mean|cte|':>10} {'rev/100':>9} {'ctrl Hz':>8} {'survived':>8}")
    summary = {}
    for name, rows in results.items():
        steps = np.array([r["steps"] for r in rows], float)
        ctes = np.array([r["mean_abs_cte"] for r in rows], float)
        surv = sum(r["survived"] for r in rows)
        rev = np.array([r["reversals_per_100"] for r in rows], float)
        hz = np.array([r.get("control_hz", 0.0) for r in rows], float)
        summary[name] = {"episodes": len(rows), "steps_mean": float(steps.mean()),
                         "steps_sd": float(steps.std()),
                         "cte_mean": float(np.nanmean(ctes)),
                         "reversals_per_100": float(rev.mean()),
                         "control_hz": float(hz.mean()),
                         "survived": int(surv)}
        print(f"{name:<18} {len(rows):>4} "
              f"{steps.mean():>12.1f} +-{steps.std():<5.1f} "
              f"{np.nanmean(ctes):>10.3f} {rev.mean():>9.2f} "
              f"{hz.mean():>8.2f} {surv:>7}/{len(rows)}")

    payload = {"args": vars(args), "per_episode": results, "summary": summary,
               "no_transfer_claim": (
                   "Simulated only. These numbers say nothing about the "
                   "physical car; the controller has never seen real hardware. "
                   "The expert is a behavioural-cloning CEILING, not a rival.")}
    (out / "p5_eval.json").write_text(json.dumps(payload, indent=2))
    print(f"\n-> {out / 'p5_eval.json'}")
    print("NOTE: simulated only. No transfer claim is made or implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
