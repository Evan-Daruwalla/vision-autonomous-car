# ml-training.md — Autonomous Car Project

GPU-memory and world-model training facts, measured on **this** machine.
Split out of `gotchas.md` on 2026-08-06: that bin was past its ~150-line cap
and ML/GPU facts had become their own domain. Hardware/print/track traps stay
in `gotchas.md`; anything about training a model lives here.

**Machine under test:** RTX 3060 Ti, 8.0 GB VRAM (7.999 GiB reported), driver
610.62, torch 2.13.0+cu126, Python 3.12.10, Windows 11.

## Sysmem Fallback is ON, and it invalidates any OOM claim

Measured 2026-08-06 by `ml/probe_vram.py`: **a 10.0 GB allocation succeeded on
the 8 GB card without raising OutOfMemoryError.** The 2026-07-23 research
predicted this; it is now confirmed as the live state, not a risk.

Consequences, in order of how badly they bite:

- **An over-budget training run does not crash. It silently spills to host RAM
  over PCIe and gets slower.** Observed on 2026-08-06: DreamerV3-S at batch 64
  pinned the card at ~7.94 GB / 100% utilization and ran more than **10x**
  slower than batch 32, which completed the same 20 steps in 71 s.
- Therefore **"it trained without OOM" proves nothing about fitting in 8 GB.**
  Always report `torch.cuda.max_memory_allocated()`, never just success.
- Changing the driver setting is Evan's call (NVIDIA Control Panel → Manage 3D
  Settings → CUDA - Sysmem Fallback Policy → "Prefer No Sysmem Fallback").
  **Nothing in this repo changes it.**

**The workaround that does not need the driver setting:**
`torch.cuda.set_per_process_memory_fraction(f, 0)` caps PyTorch's own
allocator and was measured to **still raise OOM under active fallback** (OOM
at 1.750 GB under a 2.0 GB cap). Prefer it — it lives in version control and
is reproducible on any machine, unlike a control-panel checkbox. Exposed as
`--cap-gb` on `ml/run_dreamer_p4.py`.

**Peak-allocated is a better instrument than an OOM anyway.** It says how much
a config *needs*, so "fits in 8 GB" becomes a comparison instead of a coin
flip that depends on what else is on the GPU. Note the card is never fully
yours: **1.0-2.7 GB was in use by the desktop** across measurements on
2026-08-06, and it drifts.

## dreamerv3-torch has no offline training loop (verified against source)

Commit `6ef8646d807cd10ce0c88e10a7e943211e7fc44c` (2026-03-08), vendored at
`ml/vendor/dreamerv3-torch/` (gitignored — re-clone per `ml/requirements.txt`).

The 2026-07-23 research flagged an unknown: does `offline_traindir` run
end-to-end with zero environment instantiation? **Answered 2026-08-06: no.**

- `dreamer.main()` builds `train_envs`/`eval_envs` **unconditionally**
  (dreamer.py:238-241). `offline_traindir` only selects which directory seeds
  the replay buffer.
- The envs are consulted for exactly two things: `action_space` /
  `observation_space` (dreamer.py:245, 288-290).
- The training loop is `tools.simulate(agent, train_envs, ...)`
  (dreamer.py:319) — **train steps are driven by ENV steps**, because the
  agent trains inside `Dreamer.__call__`, invoked once per env transition.

So the flag means "warm-start the buffer from disk", not "train offline".
`Dreamer._train(batch)` needs no environment at all, so `ml/run_dreamer_p4.py`
supplies hand-built gym spaces plus a genuine offline loop and **leaves the
vendored tree unpatched** so it can be re-pulled. Do not plan work around
"their offline mode" — it does not exist.

Other traps in the same repo:

- **`ruamel.yaml >= 0.19 removed `yaml.safe_load`**, which the vendored
  `dreamer.py.__main__` calls — so `python dreamer.py ...` cannot run under
  the installed version regardless of anything else. Use the
  `YAML(typ="safe", pure=True)` API.
- **Never `pip install -r ml/vendor/dreamerv3-torch/requirements.txt`** — it
  pins `torch==2.4.1` (CPU-only from PyPI) and would clobber the cu126 build.
  Only `gym`, `ruamel.yaml`, `tensorboard` are needed, and only at import.
- The repo **already skips `torch.compile` on Windows** (`config.compile and
  os.name != "nt"`, dreamer.py:47-50). Don't "fix" compile here.
- `ImagBehavior` holds a **reference** to the world model, so
  `sum(p.numel() for p in agent._task_behavior.parameters())` re-counts all
  15.7M world-model params and reports the model at roughly double its real
  size. Deduplicate by `id(p)`.
- `tools.load_episodes` reads **every episode into host RAM decompressed**,
  and silently skips a file it cannot parse (printed warning, then carries
  on with a smaller corpus). Write episodes atomically or the corpus quietly
  shrinks.
- `tools.sample_episodes` drops any key containing `log_` — which is exactly
  why `episode_writer.py` prefixes provenance fields that way. Keep the
  prefix.

## THE MEASURED TABLE — DreamerV3 on a 3060 Ti (2026-08-06, record Appendix T)

**This is the number the 2026-07-23 research said nobody had published.**
P2 sim corpus at 64x64, fp32, 20 warm steps, allocator capped at 7.0 GB.
Reproduce: `python ml/sweep_dreamer_p4.py`. Raw:
`ml/runs/dreamer_p4/sweep_summary.json`.

| config | params (unique) | peak VRAM | % of 8 GB | status |
|---|---|---|---|---|
| S, batch 16, horizon 5  | 19,101,317 | **2.552 GB** | 31.9% | fits |
| S, batch 32, horizon 5  | 19,101,317 | 4.793 GB | 59.9% | fits |
| S, batch 64, horizon 5  | 19,101,317 | — | — | **OOM >7.0 GB** |
| S, batch 16, horizon 15 | 19,101,317 | 3.873 GB | 48.4% | fits |
| M, batch 16, horizon 5  | 35,299,397 | 3.729 GB | 46.6% | fits |
| L, batch 16, horizon 5  | 69,654,533 | 5.238 GB | 65.5% | fits |

**Only "S" is a verified size** — it is the vendored repo's `defaults` block
verbatim, and its 17,919,878 trainable params (the table counts unique
tensors, which additionally includes the frozen slow-target critic) match the
research brief's "~18M" for DreamerV3-S. **XS/M/L are scaling steps defined in
`run_dreamer_p4.py`, NOT verified against the paper's published size table.**
Cite the measured parameter counts, never the letters.

**The headline finding: batch size, not model size, is what breaks 8 GB.**
A 69.7M-param model at batch 16 fits in 5.238 GB, while the 19.1M model at
batch 64 does not fit in 7.0 GB. Tripling the imagination horizon (5 -> 15)
costs 1.3 GB — more than tripling the parameter count (S -> M costs 1.2 GB).
Activations dominate; weights are close to free at this scale.

**Timings from that sweep are warm-run only.** The identical config measured
63.0 s cold and 11.1 s warm for 20 steps (CUDA kernel autotuning on first
execution). Peak memory was byte-identical across both runs. Never quote
absolute throughput from a first run; memory is stable, time is not.

### The long run confirms the boundary, and that it learns

2000 offline steps, DreamerV3-S, batch 16, horizon 5, fp32, 7.0 GB cap, on the
full 66-episode / 77,266-frame fit split
(`ml/runs/dreamer_p4/S_b16_train2000/p4_result.json`):

- **Image reconstruction loss 588.31 -> 61.39, a 9.6x reduction**, falling
  monotonically after the first epoch. The offline loop in
  `run_dreamer_p4.py` genuinely trains — it is not just allocating memory.
- **Peak VRAM 2.550-2.552 GB across all 20 epochs — a 0.002 GB spread**, and
  identical to the 20-step sweep number. **This is the important control:** it
  proves the fitting table above is a stable steady-state measurement, not a
  warm-up artifact that would creep upward over a real training run.
- The reported `kl` fell 8.996 -> 5.68 by epoch 4 then rose and plateaued near
  9.5 while reconstruction kept improving. Consistent with the posterior
  encoding more information as the decoder sharpens (`kl_free` is 1.0, so the
  loss term is clamped), but **this was not diagnosed** — do not cite it as a
  healthy-training indicator without checking.
- **Wall-clock from this run is unusable.** Per-epoch time ran 119-527 s for
  the first seven epochs, then settled at 46-52 s for the remaining thirteen.
  Suspected cause: an orphaned child process from a `TaskStop`-ed sweep still
  holding the GPU (`subprocess.run` children can outlive the parent shell).
  Not proven, and not worth re-running to prove. Memory was unaffected, which
  is the point — **memory measurements survive GPU contention; timings do
  not.** If throughput ever matters, measure it on an otherwise idle card and
  confirm with `nvidia-smi` first.

## Rules carried forward to M4 (real-car logs)

- **Measure, never estimate, VRAM.** The retracted "~24 GB for DreamerV3"
  figure cost this project a milestone restructure on desk research alone.
  8 GB turned out to hold ~3.6x the model that research feared.
- **Batch size is the cheapest memory lever**, and peak scales close to
  linearly with it (S: 2.552 GB at b16 -> 4.793 GB at b32). Reduce it before
  reducing model size — reducing the model buys far less than it costs.
- **A config that spills is worse than one that OOMs** — it wastes hours
  looking like it works. Always run with `--cap-gb` so over-budget configs
  fail in seconds instead of hanging for 20+ minutes.
