"""Paired closed-loop evaluation: every arm inside ONE launch, on ONE track.

**Why this exists.** Appendix AI established that
`donkey-generated-track-v0` REGENERATES the track on every launch, and that
this is the cause of the 4.4x launch-to-launch spread that made every
comparison in Appendices Z, AA, AB and AC unmeasurable. The launch is the unit
of variation because the TRACK is.

`eval_in_sim.py` takes one `--ctrl-dir` per invocation, so each arm of a
comparison necessarily got its own launch and therefore its own track. That is
an unpaired design against a confound with a 55% coefficient of variation.

**This runs every arm inside a single env session**, so they all drive the
SAME generated track, and reports the WITHIN-LAUNCH difference between arms.
The track effect cancels exactly, the way a paired t-test cancels
between-subject variance. Repeating over several launches then averages the
paired difference over the track distribution.

**Why not just use a fixed track.** Measured 2026-08-13: on the fixed
`donkey-avc-sparkfun-v0` and `donkey-mountain-track-v0` the learned
controllers die at 13-67 steps with mean|cte| 2.2-3.8, against the 0.317 the
expert holds in training. Every fixed track is far out of the corpus's visual
distribution, so the arms bunch at the floor and the comparison measures
nothing. The generated track is the only in-distribution option, and pairing is
what makes it usable.

Reads the same checkpoints as `eval_in_sim.py` and reuses its episode loop and
policy wrapper, so nothing about how a policy is driven changes.

Usage:
  python ml/eval_paired.py --ctrl-dirs cl_base cl_aug nh_base nh_aug \\
                           --launches 4 --episodes 2
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from collect_sim_data import PIDDriver, SIM_EXE
from eval_in_sim import LatentPolicy, run_episode
from provenance import write_result
from sim_conf import base_sim_conf
from splits import check_fingerprints
from models import MDNRNN, ConvVAE
from train_controller import Controller

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"


def parse_arm_rnns(specs: list[str], names: list[str], default: str) -> dict[str, str]:
    """Map every arm name to an MDN-RNN path: `default` unless a NAME=PATH spec overrides it."""
    out = {n: default for n in names}
    seen: set[str] = set()
    for spec in specs:
        if "=" not in spec:
            raise ValueError(f"{spec!r} is not NAME=PATH")
        name, path = spec.split("=", 1)
        if not name or not path:
            raise ValueError(f"{spec!r} has an empty name or path")
        if name not in names:
            raise ValueError(f"{name!r} is not an arm name; arms are {names}")
        if name in seen:
            raise ValueError(f"{name!r} given twice")
        seen.add(name)
        out[name] = path
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", default="donkey-generated-track-v0")
    ap.add_argument("--ctrl-dirs", nargs="+", required=True,
                    help="arm directories under ml/runs (or full paths)")
    ap.add_argument("--arch", default="mlp", choices=("linear", "mlp"))
    ap.add_argument("--launches", type=int, default=4,
                    help="independent sim launches; each gets its own "
                         "generated track, and all arms share it")
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--episodes", type=int, default=2)
    ap.add_argument("--max-steps", type=int, default=600)
    ap.add_argument("--port", type=int, default=9091)
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--rnn", default=str(RUNS / "mdnrnn" / "mdnrnn_best.pt"))
    ap.add_argument("--arm-rnn", action="append", default=[], metavar="NAME=PATH",
                    help="use this MDN-RNN checkpoint for arm NAME (repeatable); "
                         "other arms use --rnn")
    ap.add_argument("--out", default=str(RUNS / "eval_paired"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing eval_paired.json in --out")
    args = ap.parse_args()

    arms = [Path(d) if Path(d).is_absolute() else RUNS / d for d in args.ctrl_dirs]
    names = [d.name for d in arms]
    # Arms are keyed by directory NAME; two dirs with one name would silently
    # share a key in ctrls / per_launch and overwrite each other.
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        print(f"FAIL: --ctrl-dirs map to the same arm name {dupes}; arms are "
              f"keyed by directory name, so rename or pick distinct dirs.")
        return 1
    try:
        arm_rnn = parse_arm_rnns(args.arm_rnn, names, args.rnn)
    except ValueError as e:
        print(f"FAIL: --arm-rnn: {e}")
        return 1

    out = Path(args.out)
    if (out / "eval_paired.json").exists() and not args.force:
        print(f"REFUSING: {out / 'eval_paired.json'} already exists. "
              f"Pass --force to overwrite it.")
        return 1
    out.mkdir(parents=True, exist_ok=True)

    vae = ConvVAE().to(args.device)
    vae.load_state_dict(torch.load(args.vae, map_location=args.device)["model"])
    vae.eval()
    rnns: dict[str, MDNRNN] = {}
    pairing: dict[str, str] = {}
    for path in dict.fromkeys(arm_rnn.values()):
        rck = torch.load(path, map_location=args.device)
        m = MDNRNN().to(args.device)
        m.load_state_dict(rck["model"])
        m.eval()
        rnns[path] = m
        pairing[path] = rck.get("action_pairing", "legacy")
    for name in names:
        print(f"  {name}: rnn {arm_rnn[name]} "
              f"(action_pairing={pairing[arm_rnn[name]]})")

    # Load every arm's controllers up front so a missing checkpoint fails
    # before a sim is launched rather than half way through a 20-minute run.
    ctrls: dict[str, dict[int, tuple[Controller, bool]]] = {}
    bad_fp = []
    for d, name in zip(arms, names):
        ctrls[name] = {}
        for s in args.seeds:
            p = d / f"controller_{args.arch}_seed{s}.pt"
            if not p.exists():
                print(f"FAIL: {p} missing")
                return 1
            ck = torch.load(p, map_location=args.device)
            bad_fp += check_fingerprints(ck, args.vae, arm_rnn[name],
                                         name=f"{name}/{p.name}")
            c = Controller(arch=args.arch).to(args.device)
            c.load_state_dict(ck["model"])
            c.eval()
            ctrls[name][s] = (c, bool(ck.get("args", {}).get("no_history", False)))
    if bad_fp:
        print("REFUSING: controller/encoder fingerprint mismatch:")
        for m in bad_fp:
            print(f"  {m}")
        return 2
    print(f"{len(names)} arms x {len(args.seeds)} seeds loaded: {names}\n")

    import gym_donkeycar  # noqa: F401
    import gymnasium as gym

    records = []
    for L in range(args.launches):
        conf = base_sim_conf(str(SIM_EXE), args.port, "pair", max_cte=4.0)
        env = gym.make(args.track, conf=conf)
        print(f"=== launch {L+1}/{args.launches} "
              f"(one generated track, shared by every arm) ===")
        try:
            for s in args.seeds:
                torch.manual_seed(s)
                np.random.seed(s)
                # expert first, as the per-launch difficulty reference
                for ep in range(args.episodes):
                    r = run_episode(env, PIDDriver(), args.max_steps, True)
                    r.update(launch=L, seed=s, episode=ep, arm="expert")
                    records.append(r)
                for name in names:
                    c, nh = ctrls[name][s]
                    pol = LatentPolicy(vae, rnns[arm_rnn[name]], c, args.device,
                                       no_history=nh)
                    for ep in range(args.episodes):
                        r = run_episode(env, pol, args.max_steps, False)
                        r.update(launch=L, seed=s, episode=ep, arm=name)
                        records.append(r)
                got = {n: np.mean([x["steps"] for x in records
                                   if x["launch"] == L and x["seed"] == s
                                   and x["arm"] == n]) for n in ["expert"] + names}
                print("  seed %d: %s" % (s, "  ".join(
                    f"{k} {v:.0f}" for k, v in got.items())))
        finally:
            try:
                env.close()
            except Exception:                  # noqa: BLE001
                pass
            time.sleep(3.0)

    def mean_for(launch, arm):
        v = [r["steps"] for r in records
             if r["launch"] == launch and r["arm"] == arm]
        return float(np.mean(v)) if v else float("nan")

    print(f"\n{'launch':>7}" + "".join(f"{a:>12}" for a in ["expert"] + names))
    per_launch = {}
    for L in range(args.launches):
        row = {a: mean_for(L, a) for a in ["expert"] + names}
        per_launch[L] = row
        print(f"{L+1:>7}" + "".join(f"{row[a]:>12.1f}" for a in ["expert"] + names))

    # THE PAIRED STATISTIC. Differences are taken WITHIN a launch, so whatever
    # that launch's track difficulty was cancels. Averaging the differences
    # across launches then estimates the arm effect free of the track effect --
    # which the unpaired design in Z/AA/AB/AC could not do.
    base = names[0]
    print(f"\nPAIRED differences vs '{base}', computed WITHIN each launch:")
    print(f"{'arm':<12}{'mean diff':>12}{'sd':>10}{'n':>5}   per-launch")
    summary = {}
    for name in names[1:]:
        diffs = [per_launch[L][name] - per_launch[L][base]
                 for L in range(args.launches)
                 if np.isfinite(per_launch[L][name])
                 and np.isfinite(per_launch[L][base])]
        d = np.array(diffs, float)
        sd = float(d.std(ddof=1)) if len(d) > 1 else float("nan")
        summary[name] = {"mean_diff": float(d.mean()), "sd": sd, "n": len(d),
                         "per_launch": [round(x, 1) for x in diffs]}
        print(f"{name:<12}{d.mean():>12.1f}{sd:>10.1f}{len(d):>5}   "
              f"{[round(x) for x in diffs]}")
    print(f"\n('{base}' is the reference; a positive diff means the arm drove "
          f"FURTHER than {base} on the same track.)")

    # The unpaired spread, printed alongside, to show what pairing bought.
    print(f"\nfor contrast, the UNPAIRED spread of each arm across launches:")
    for a in ["expert"] + names:
        v = np.array([per_launch[L][a] for L in range(args.launches)], float)
        v = v[np.isfinite(v)]
        if len(v) > 1:
            print(f"  {a:<12} mean {v.mean():7.1f}  sd {v.std(ddof=1):6.1f}  "
                  f"range {v.min():.0f}-{v.max():.0f}")

    # **Batch validity gate**, same definition as eval_in_sim.py: the PID expert
    # is fixed code and must survive EVERY episode it ran (all seeds, all
    # launches); if it did not, the sim was degraded for this batch and every
    # arm number in it is untrustworthy.
    exp_rows = [r for r in records if r["arm"] == "expert"]
    exp_survived = sum(r["survived"] for r in exp_rows)
    batch_valid = bool(exp_rows and exp_survived == len(exp_rows))
    if exp_rows and not batch_valid:
        print(f"\n*** BATCH INVALID: the expert survived only "
              f"{exp_survived}/{len(exp_rows)}. The expert is fixed code "
              f"and completes 9/9 on a healthy sim, so the SIMULATOR was "
              f"degraded during this run. Do not compare these controller "
              f"numbers against another batch. Re-run. ***")
    write_result(out / "eval_paired.json",
        {"args": vars(args), "arm_rnn": arm_rnn, "per_episode": records,
         "per_launch": {str(k): v for k, v in per_launch.items()},
         "paired_vs_" + base: summary,
         "batch_valid": batch_valid})
    print(f"\n-> {out / 'eval_paired.json'}")
    print("NOTE: simulated only. No transfer claim is made or implied.")
    return 0 if batch_valid or not exp_rows else 2


def self_check() -> None:
    names = ["a", "b", "c"]
    assert parse_arm_rnns([], names, "D") == {"a": "D", "b": "D", "c": "D"}
    assert parse_arm_rnns(["b=X.pt"], names, "D") == {"a": "D", "b": "X.pt", "c": "D"}
    for bad in (["noequals"], ["=p"], ["a="], ["zzz=p"], ["a=p", "a=q"]):
        try:
            parse_arm_rnns(bad, names, "D")
        except ValueError:
            continue
        raise AssertionError(f"parse_arm_rnns accepted {bad}")
    print("eval_paired self_check: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
