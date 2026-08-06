"""SIM-POC P4: DreamerV3-S trained OFFLINE on the P2 corpus, with the 8 GB
boundary measured rather than assumed.

WHY THIS FILE EXISTS INSTEAD OF `python dreamer.py --offline_traindir ...`
--------------------------------------------------------------------------
The 2026-07-23 research brief flagged an unknown: "does dreamerv3-torch's
`offline_traindir` run end-to-end with zero environment instantiation?"
Reading the vendored source (commit 6ef8646) answers it: **no.**

  * `dreamer.main()` builds `train_envs`/`eval_envs` UNCONDITIONALLY
    (dreamer.py:238-241). `offline_traindir` only changes which directory
    seeds the replay buffer; it does not gate env creation.
  * Worse, the training LOOP is `tools.simulate(agent, train_envs, ...)`
    (dreamer.py:319). Training steps are driven by ENV steps -- the agent
    trains inside `Dreamer.__call__`, which `simulate` invokes once per
    environment transition. There is no offline loop in the repo.

So `offline_traindir` means "warm-start the buffer from disk", not "train
offline". Running it as the PRD originally specified would either need the
Unity sim live (not offline, and it would dominate the memory measurement) or
a fake env feeding garbage transitions into the buffer alongside the real
corpus (silently poisoning the data).

`Dreamer._train(data)` itself needs NO environment -- it takes a batch and
does the world-model update plus the imagination actor-critic update. So this
file supplies the two things `main()` was providing and nothing else:

  1. observation/action spaces, built from the real corpus (the only thing the
     envs were ever consulted for -- dreamer.py:245, 288-290), and
  2. an honest offline training loop that pulls batches and calls `_train`.

Everything that does the actual learning is the unmodified vendored code. The
vendored tree is NOT patched, so it can be re-pulled without losing this.

MEASURING THE MEMORY CEILING
----------------------------
`ml/probe_vram.py` established on 2026-08-06 that NVIDIA Sysmem Fallback is ON
for this machine: a 10 GB allocation succeeded on an 8 GB card without raising
OutOfMemoryError. An OOM boundary measured in that state is meaningless -- an
over-budget run silently spills to host RAM over PCIe and merely gets slower.

Rather than require a driver setting (Evan's call, and invisible to version
control), `--cap-gb` uses `torch.cuda.set_per_process_memory_fraction` to cap
PyTorch's own allocator. probe_vram.py verified that this cap still raises OOM
with fallback active, so the boundary becomes reproducible and in-code.

Usage:
    python ml/run_dreamer_p4.py --smoke
    python ml/run_dreamer_p4.py --steps 2000
    python ml/run_dreamer_p4.py --steps 200 --cap-gb 4.0   # force the ceiling
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

import numpy as np
import torch

VENDOR = pathlib.Path(__file__).resolve().parent / "vendor" / "dreamerv3-torch"
if not VENDOR.exists():
    raise SystemExit(
        f"vendored dreamerv3-torch not found at {VENDOR}\n"
        "  git clone --depth 1 https://github.com/NM512/dreamerv3-torch.git "
        f"{VENDOR}"
    )
sys.path.insert(0, str(VENDOR))

import gym  # noqa: E402  (dreamer's wrappers import it; spaces come from here)
import ruamel.yaml as yaml  # noqa: E402

import dreamer as dv3  # noqa: E402
import tools as dv3_tools  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / "ml" / "data" / "dreamer"
RUNS = REPO / "ml" / "runs" / "dreamer_p4"

# Model-size presets.
#
# **Only "S" is verified.** It is exactly the vendored repo's `defaults` block
# (dyn_deter 512, units 512, cnn_depth 32), which the 2026-07-23 research
# identified as the DreamerV3-S-scale config to target on 8 GB, and whose
# ~18M trainable params match that brief's estimate.
#
# XS/M/L are scaling steps DEFINED HERE by raising the same three knobs. They
# are NOT claimed to reproduce the published size table -- that has not been
# checked against the paper. They exist to answer "how does memory scale with
# model size on this card", which does not require them to be canonical. Cite
# the measured parameter counts, never these letters, as the size.
SIZES = {
    "XS": dict(dyn_deter=256, units=256, cnn_depth=24),
    "S": dict(dyn_deter=512, units=512, cnn_depth=32),   # = repo defaults
    "M": dict(dyn_deter=1024, units=640, cnn_depth=48),
    "L": dict(dyn_deter=2048, units=768, cnn_depth=64),
}


def build_config(overrides: dict) -> argparse.Namespace:
    """configs.yaml `defaults`, recursively updated -- same merge main() does.

    Uses the modern ruamel API: `yaml.safe_load` was REMOVED in ruamel.yaml
    0.19, so the vendored `dreamer.py`'s own `__main__` block cannot run under
    the installed version. Not patched there -- this file is the entry point.
    """
    loader = yaml.YAML(typ="safe", pure=True)
    raw = loader.load((VENDOR / "configs.yaml").read_text())
    cfg = {}

    def recursive_update(base, update):
        for key, value in update.items():
            if isinstance(value, dict) and key in base:
                recursive_update(base[key], value)
            else:
                base[key] = value

    recursive_update(cfg, raw["defaults"])
    recursive_update(cfg, overrides)
    return argparse.Namespace(**cfg)


def spaces_from_corpus(episode: dict, size: int):
    """The obs/action spaces `main()` would have asked an environment for.

    Derived from a real episode rather than hardcoded, so a corpus whose shape
    drifts fails loudly here instead of at the first matmul.
    """
    img = episode["image"]
    if img.shape[1:] != (size, size, 3):
        raise SystemExit(
            f"corpus images are {img.shape[1:]}, expected ({size}, {size}, 3). "
            "Run ml/prep_dreamer_corpus.py first."
        )
    n_act = episode["action"].shape[1]

    obs_space = gym.spaces.Dict({
        "image": gym.spaces.Box(0, 255, (size, size, 3), dtype=np.uint8),
        # is_first/is_terminal are consumed directly by WorldModel.preprocess;
        # they stay out of the encoder because mlp_keys is '$^' (matches
        # nothing), so declaring them costs no parameters.
        "is_first": gym.spaces.Box(0, 1, (), dtype=bool),
        "is_terminal": gym.spaces.Box(0, 1, (), dtype=bool),
    })
    act_space = gym.spaces.Box(-1.0, 1.0, (n_act,), dtype=np.float32)
    return obs_space, act_space, n_act


def count_params(*modules) -> int:
    """Unique parameter tensors across the given modules.

    Deduplicated by id because `ImagBehavior` keeps a REFERENCE to the world
    model, so a naive sum over `agent._task_behavior.parameters()` re-counts
    all 15.7M world-model params and reports a model roughly twice its real
    size. Verified against the repo's own optimizer lines, which print
    15,685,763 + 1,052,676 + 1,181,439 = 17,919,878.
    """
    seen = {}
    for m in modules:
        for p in m.parameters():
            seen[id(p)] = p.numel()
    return sum(seen.values())


def gb(n_bytes: float) -> float:
    return n_bytes / 1024**3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=2000, help="offline train steps")
    ap.add_argument("--epoch-steps", type=int, default=100,
                    help="steps per memory-logging epoch")
    ap.add_argument("--size", choices=sorted(SIZES), default="S")
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--batch-length", type=int, default=64)
    ap.add_argument("--imag-horizon", type=int, default=5)
    ap.add_argument("--precision", type=int, choices=(16, 32), default=32)
    ap.add_argument("--cap-gb", type=float, default=0.0,
                    help="cap the torch allocator (0 = uncapped)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dataset-size", type=int, default=0,
                    help="cap frames loaded into host RAM (0 = whole corpus). "
                         "VRAM holds only the batch, so a sweep can load less "
                         "without changing the memory measurement")
    ap.add_argument("--smoke", action="store_true",
                    help="20 steps, tiny batch -- proves the path, not the ceiling")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.epoch_steps, args.batch_size = 20, 10, 4

    if not torch.cuda.is_available():
        print("FAIL: no CUDA device")
        return 1

    total_b = torch.cuda.get_device_properties(0).total_memory
    if args.cap_gb > 0:
        fraction = min(1.0, args.cap_gb * 1024**3 / total_b)
        torch.cuda.set_per_process_memory_fraction(fraction, 0)
        print(f"allocator capped at {args.cap_gb:.2f} GB "
              f"({fraction:.1%} of {gb(total_b):.2f} GB)")

    overrides = dict(
        SIZES[args.size],
        logdir=str(RUNS / (args.tag or f"{args.size}_b{args.batch_size}")),
        offline_traindir=str(DATA / "train"),
        offline_evaldir=str(DATA / "eval"),
        batch_size=args.batch_size,
        batch_length=args.batch_length,
        imag_horizon=args.imag_horizon,
        precision=args.precision,
        seed=args.seed,
        compile=False,          # vendored code already skips compile on Windows
        video_pred_log=False,   # writes videos, not memory-relevant
        device="cuda:0",
    )
    # cnn_depth lives inside the encoder/decoder sub-dicts too; the size preset
    # sets the top-level key, so mirror it or the CNN stays at the default.
    overrides["encoder"] = {"cnn_depth": SIZES[args.size]["cnn_depth"]}
    overrides["decoder"] = {"cnn_depth": SIZES[args.size]["cnn_depth"]}

    if args.dataset_size:
        overrides["dataset_size"] = args.dataset_size

    config = build_config(overrides)
    dv3_tools.set_seed_everywhere(config.seed)

    logdir = pathlib.Path(config.logdir)
    logdir.mkdir(parents=True, exist_ok=True)
    print(f"logdir {logdir}")

    print(f"loading episodes from {DATA / 'train'} ...")
    t0 = time.time()
    train_eps = dv3_tools.load_episodes(DATA / "train", limit=config.dataset_size)
    if not train_eps:
        raise SystemExit(f"no episodes under {DATA / 'train'} -- run "
                         "ml/prep_dreamer_corpus.py first")
    frames = sum(len(e["reward"]) for e in train_eps.values())
    host_gb = gb(sum(e["image"].nbytes for e in train_eps.values()))
    print(f"  {len(train_eps)} episodes, {frames:,} frames, "
          f"{host_gb:.2f} GB of images in HOST RAM ({time.time()-t0:.0f}s)")

    sample = next(iter(train_eps.values()))
    obs_space, act_space, n_act = spaces_from_corpus(sample, config.size[0])
    config.num_actions = n_act
    print(f"  obs image {sample['image'].shape[1:]}, {n_act} actions")

    dataset = dv3.make_dataset(train_eps, config)
    logger = dv3_tools.Logger(logdir, 0)

    print(f"\nbuilding DreamerV3-{args.size} "
          f"(deter={config.dyn_deter}, units={config.units}, "
          f"cnn_depth={config.encoder['cnn_depth']}, "
          f"imag_horizon={config.imag_horizon}, fp{config.precision}) ...")
    agent = dv3.Dreamer(obs_space, act_space, config, logger, dataset).to(config.device)
    agent.requires_grad_(requires_grad=False)

    n_wm = count_params(agent._wm)
    n_total = count_params(agent._wm, agent._task_behavior)
    n_beh = n_total - n_wm
    print(f"  world model      {n_wm:>12,} params")
    print(f"  actor + critic   {n_beh:>12,} params  (incl. the slow-target copy)")
    print(f"  TOTAL unique     {n_total:>12,} params")

    torch.cuda.reset_peak_memory_stats()
    print(f"\ntraining {args.steps} offline steps "
          f"(batch {config.batch_size} x {config.batch_length})\n")
    print(f"{'epoch':>6} {'step':>7} {'peak GB':>9} {'image_loss':>11} "
          f"{'kl':>9} {'s/epoch':>9}")

    history = []
    oom_at = None
    global_peak = 0.0
    t_epoch = time.time()
    try:
        for step in range(1, args.steps + 1):
            agent._train(next(dataset))
            if step % args.epoch_steps == 0:
                peak = gb(torch.cuda.max_memory_allocated())
                global_peak = max(global_peak, peak)
                # Dreamer accumulates metrics into lists and only drains them
                # inside __call__, which the offline loop never runs -- so
                # average and clear them here, or they grow without bound and
                # every "epoch" reports the mean since step 1.
                means = {k: float(np.mean(v)) for k, v in agent._metrics.items() if v}
                agent._metrics = {}
                row = dict(
                    epoch=step // args.epoch_steps,
                    step=step,
                    peak_gb=round(peak, 3),
                    alloc_gb=round(gb(torch.cuda.memory_allocated()), 3),
                    reserved_gb=round(gb(torch.cuda.memory_reserved()), 3),
                    image_loss=round(means.get("image_loss", float("nan")), 2),
                    kl=round(means.get("kl", float("nan")), 3),
                    seconds=round(time.time() - t_epoch, 1),
                )
                history.append(row)
                print(f"{row['epoch']:>6} {row['step']:>7} {row['peak_gb']:>9.3f} "
                      f"{row['image_loss']:>11.2f} {row['kl']:>9.3f} "
                      f"{row['seconds']:>9.1f}")
                torch.cuda.reset_peak_memory_stats()
                t_epoch = time.time()
    except torch.cuda.OutOfMemoryError as e:
        oom_at = step
        print(f"\nOOM at step {step}: {str(e).splitlines()[0]}")

    result = dict(
        size=args.size,
        batch_size=config.batch_size,
        batch_length=config.batch_length,
        imag_horizon=config.imag_horizon,
        precision=config.precision,
        cap_gb=args.cap_gb or None,
        params_world_model=n_wm,
        params_actor_critic=n_beh,
        params_total=n_total,
        steps_requested=args.steps,
        steps_completed=(oom_at - 1) if oom_at else args.steps,
        oom_at_step=oom_at,
        peak_gb=round(global_peak, 3),
        total_vram_gb=round(gb(total_b), 3),
        episodes=len(train_eps),
        frames=frames,
        history=history,
    )
    out = logdir / "p4_result.json"
    out.write_text(json.dumps(result, indent=2))

    print()
    if oom_at:
        print(f"RESULT: OOM at step {oom_at}, peak {global_peak:.3f} GB"
              + (f" under a {args.cap_gb:.2f} GB cap" if args.cap_gb else ""))
        print("        This is a MEASURED boundary -- P4 done-check accepts it.")
    else:
        print(f"RESULT: trained {args.steps} steps, peak {global_peak:.3f} GB "
              f"of {gb(total_b):.2f} GB")
        print("        P4 done-check: a trained model.")
    print(f"        -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
