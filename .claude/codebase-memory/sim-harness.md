# sim-harness.md — Autonomous Car Project

**Split out of `gotchas.md` on 2026-09-02** (Appendix BO). Traps in the
simulator, the evaluation harness, and training-time GPU limits — the things
that made closed-loop numbers untrustworthy.

**The load-bearing one is the first sim entry below: the generated track is
regenerated per launch, so closed-loop numbers are NOT comparable across
launches.** Use `ml/eval_paired.py`.

Related bins: `ml-training.md` (world-model training facts measured on this
3060 Ti), `data.md` (the episode contract and the three-way split rule).

- Sim-trained RL policies that win in simulation can lose to classical
  control on real hardware (F1TENTH/RoboRacer, RLJ 2025) — this is why the
  PRD makes sim-RL optional (M5) and the capstone offline-on-real-logs (M4).
  Don't re-promote sim-RL without a dated PRD fork (2026-07-23).
- ~~**Training GPU is 8GB (RTX 3060 Ti)**, below the ~24GB the research
  cited for DreamerV3 on 64×64 vision.~~ **(supersedes 2026-07-23 ~17:21
  entry: the ~24GB figure is RETRACTED — a follow-up pass could not locate
  the source, and no published VRAM-per-size table for DreamerV3 exists.)**
  Corrected 2026-07-23 ~17:39: 8GB is **workable at DreamerV3 S-scale
  (~18M params) or below** at 64×64; XL-scale needs 13.4 GiB and even a
  24GB 3090 OOMs at size200m. Behavioral cloning (M3) is unaffected either
  way. Full detail: `docs/research/2026-07-23_world-model-8gb-vram.md`.
- **Every DreamerV3 repo's DEFAULT config is too big for 8GB.** danijar's
  default is `size200m`; `dreamerv3-torch`'s crafter/atari100k overrides
  jump to dyn_deter 4096 / cnn_depth 96. Use the **repo defaults** of
  `dreamerv3-torch` (dyn_deter 512, cnn_depth 32, units 512) and apply no
  task overrides (2026-07-23).
- **Use `NM512/dreamerv3-torch`, NOT danijar's JAX DreamerV3** (2026-07-23,
  both facts verified directly against source): the JAX reference has **no
  offline-training mode** (issue #80, closed unanswered) and **JAX has no
  native-Windows CUDA support** (official install table: Windows = "no",
  WSL2 = "experimental"). The PyTorch port has `offline_traindir` /
  `offline_evaldir`, and setting `offline_traindir` skips environment
  prefill entirely. ~~*(the last clause read as "so it runs without an
  environment" — see the correction below)*~~
- **`offline_traindir` does NOT make dreamerv3-torch run without an
  environment, and the repo has NO offline training loop** (measured
  2026-08-06 against commit 6ef8646, record Appendix T — **partially
  supersedes the 2026-07-23 entry above**, whose "skips environment prefill"
  was true but was being read as "runs offline"). `dreamer.main()` builds
  `train_envs`/`eval_envs` unconditionally (dreamer.py:238-241), and the
  training loop is `tools.simulate(agent, train_envs, ...)` — train steps are
  driven by ENV steps. The flag only warm-starts the replay buffer.
  `Dreamer._train(batch)` itself needs no env, so `ml/run_dreamer_p4.py`
  supplies hand-built obs/action spaces plus a real offline loop and leaves
  the vendored tree unpatched. **Any future session planning "just run their
  offline mode" is planning something that does not exist.** Full detail:
  `.claude/codebase-memory/ml-training.md`.
- **Disable NVIDIA "CUDA - Sysmem Fallback Policy" before any training run**
  (NVIDIA Control Panel → Manage 3D Settings → python.exe → "Prefer No
  Sysmem Fallback"). Since driver 536.40 the default spills VRAM overflow
  into shared system RAM, so an out-of-memory condition becomes a **silent
  ~3× slowdown** instead of a loud error. This is exactly what the "16GB
  shared" figure is — host RAM over PCIe (~25 GB/s) vs 448 GB/s GDDR6.
  Never count it as VRAM (2026-07-23). **CONFIRMED STILL ENABLED and no
  longer desk research (measured 2026-08-06, driver 610.62):
  `ml/probe_vram.py` allocated 10.0 GB on the 8 GB card without raising
  OutOfMemoryError.** Any OOM-boundary claim made while it is on is
  worthless. Changing it is Evan's call; until then use
  `torch.cuda.set_per_process_memory_fraction`, which was measured to still
  raise OOM under fallback (OOM at 1.750 GB under a 2.0 GB cap) and is
  reproducible because it lives in code, not a control panel.
- **Mixed precision is not a reliable 8GB rescue here** — the one available
  PyTorch DreamerV3 measurement had bf16 costing **10.5 GiB more** and
  running slower. Measure `torch.cuda.max_memory_allocated()`; revert if it
  rises. Gradient checkpointing isn't implemented in any of these codebases
  (2026-07-23).
- **WSL2 does not give more VRAM** — no evidence found; the GPU stays under
  the Windows WDDM driver. It buys compatibility (JAX, TF≥2.11) and clean
  OOM behaviour only (2026-07-23).
- **`donkey-generated-track-v0` REGENERATES THE TRACK ON EVERY LAUNCH**
  (measured 2026-08-13, Appendix AI). Three identical-config launches at an
  identical spawn pose gave pairwise MAE 29-36 with **27-35%% of pixels
  differing by >30**, at stable mean brightness (spread 6.6) - so the
  structure changes, not the lighting. The same test on the fixed
  `donkey-warehouse-v0` gives a **0.307** noise floor, 158x smaller.
  **This is the cause of the 4.4x launch-to-launch closed-loop variance** that
  AD/AE/AF could not explain: the launch is the unit of variation because the
  TRACK is. **Any frame-comparison experiment (FOV, encoder, reconstruction)
  is meaningless on the generated track - use a fixed one.** And any
  closed-loop A/B must either run on a fixed track or pair arms within one
  launch. Note AD.2 wrongly listed track identity as ruled out: tight expert
  mean|cte| across launches is what a track GENERATOR produces, not evidence
  of one track.
- **The sim camera FOV is 90** (`cam_config` was never sent, so it was the
  Unity default; identified 2026-08-13 by comparison on a fixed track). At
  160x120 with Unity's vertical-FOV convention that is ~106 deg horizontal /
  ~118 deg diagonal. **Camera Module 3 Wide (102 H / 120 D) is the right
  part**; the standard module (66 H) is ~40 deg off. Camera height, pitch and
  offset are still unidentified - same method would find them.
- **`eval_in_sim.py` step counts are NOT comparable across runs unless
  `--control-hz` is pinned** (measured 2026-08-10). The identical MLP
  checkpoint (byte-identical val_mse 0.001754), through the identical script,
  scored **69.3 steps at a 13.2 Hz control loop and 187.2 at 16.7 Hz** — a
  2.7× swing from nothing but how fast the machine ran inference that day.
  The rate is flat within a run (no warmup artifact) and the PID expert, which
  does no neural forward pass, sat at the sim's own 18.87 Hz in both runs and
  was perfectly reproducible. `control_hz` is now always reported per episode
  and in the summary — **a step count without its rate is uninterpretable**,
  and the banked P5 headline of 69.3 steps understates that controller.
  **To compare two policies: run them back-to-back unthrottled on an idle
  machine and check the reported `control_hz` agrees.**
- **Do NOT use `--control-hz` to equalise two arms** (measured 2026-08-10, the
  same day it was added). Throttling by SLEEPING is not the same manipulation
  as "the same loop, slower." The loop normally runs flat out and stays in
  lockstep with the sim's frame production because `observe()` blocks for the
  next frame; any sleep breaks that lockstep and the two clocks beat against
  each other. It is a **cliff, not a slope** — the PID expert:

  | throttle | steps | mean\|cte\| |
  |---|---|---|
  | none (18.87 Hz natural) | **600 (9/9)** | 0.361 |
  | 18.5 Hz (−2%) | 196.5 | 0.988 |
  | 18.0 Hz | 136.0 | 0.745 |
  | 17.0 Hz | 133.0 | 0.806 |
  | 16.0 Hz | 124.9 | 0.797 |

  A 2% throttle costs two thirds of the performance and further slowing barely
  matters — that is desynchronisation, not control-rate sensitivity. The flag
  is kept as a DIAGNOSTIC that measures the artifact.
- **`PIDDriver` is not dt-normalised** (`collect_sim_data.py`). `integral +=
  err` and `derivative = err - prev_err` are both per-CALL, not per-second, so
  the effective Ki and Kd change with loop rate. Harmless while the loop rate
  is constant, but it means **the gains are tied to the rate they were tuned
  at** — a real portability trap for the physical car, whose loop will not run
  at the sim's 18.87 Hz. Also means any throttled-expert number confounds rate
  with silent gain re-tuning.

