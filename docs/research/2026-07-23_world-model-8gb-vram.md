# Research Brief — Offline World Model on 8GB VRAM (RTX 3060 Ti)

**Date:** 2026-07-23
**Question:** Is PRD milestone M4 — a world model trained offline on the
car's own logged real driving, then a policy extracted from it and evaluated
on the physical car — actually feasible on an RTX 3060 Ti with 8GB VRAM? If
so, in what configuration; if not, what is the honest fallback?
**For:** Evan, and any executing model working PRD M4 (tasks 16a, 16-19).
**Method:** One Opus research worker with a pre-registered rubric, reading
primary artifacts directly (config files, papers, issue threads) rather than
summaries. Reviewer spot-checked the two pivotal claims against primary
sources 2026-07-23 ~17:39 CDT — both confirmed verbatim (see Verification).
Desk research only: **nothing here has been run on Evan's machine.** Every
VRAM number below is someone else's measurement on someone else's config.

---

## TL;DR (verdict first)

1. **Feasible with constraints.** 8GB is enough if the model stays at the
   DreamerV3 paper's **S scale (~18M params)** or below, at 64×64, with a
   short imagination horizon. It is not enough for L/XL — **which is what
   every default config in every repo gives you.** The single most useful
   data point: S-scale ran at a usable 1.4 Hz on an 8GB GTX 1080, while
   XL-scale on the same card thrashed at 0.025 Hz against ~11 Hz expected.
2. **The "~24GB comfortable" figure from the first research pass is
   RETRACTED** — the source could not be located, and no published
   VRAM-per-size table for DreamerV3 exists at all. The measured evidence
   says it was describing XL/size200m, and it does not generalise downward.
3. **Use `NM512/dreamerv3-torch`, not danijar's JAX reference.** The JAX
   version has no offline mode and JAX does not support native Windows CUDA
   at all. The PyTorch port has first-class `offline_traindir` support that
   skips environment prefill entirely, and runs on native Windows.
4. **Disable NVIDIA's Sysmem Fallback before training.** Otherwise the
   "16GB shared" memory silently absorbs an out-of-memory condition and
   turns it into a ~3× slowdown instead of a loud error.
5. **Build the small architecture first.** Ha & Schmidhuber's original
   World Models (VAE + MDN-RNN + controller, **~4.77M params total**, under
   an hour per component on 2018 hardware) is guaranteed to fit and is
   still a genuine world model — it is the paper that named the field.
   Building it first de-risks the whole data pipeline and guarantees M4
   finishes with a real result regardless of where the 8GB boundary lands.
6. **Dataset size is a non-problem.** 100k frames at 20 Hz is 83 minutes of
   driving and 1.23 GB at 64×64 — an afternoon's work, and small enough to
   upload anywhere.

---

## Findings by theme

### The size presets, and why the published numbers don't line up

Read directly from `danijar/dreamerv3/dreamerv3/configs.yaml` @ main
(2026-07-23), there are exactly seven presets: `size1m`, `size12m`,
`size25m`, `size50m`, `size100m`, `size200m`, `size400m`. Repo defaults:
`batch_size 16`, `batch_length 64`, `imag_length 15`,
`compute_dtype bfloat16`, 64×64 images, **default config `size200m`**.

The paper (arXiv 2301.04104, Appendix B) uses different names — XS/S/M/L/XL
at **8M / 18M / 37M / 77M / 200M** params. The two namings do not
correspond (the repo's `size12m` uses deter 2048; the paper has no 12M row),
and open issue #131 reports the same mismatch. **No verified parameter
counts exist for the current repo's presets** — treat the names as labels.

The paper states one V100 per agent but never says which V100 SKU (16GB or
32GB), and the README's entire memory guidance is *"Try `--batch_size 1` to
rule out an out of memory error."*

### What actually fits in 8GB — the measured evidence

Every row here is a single-user report; tagged as such.

| Config | Measured | Source |
|---|---|---|
| XL/size200m crafter 64×64, GTX 1080 8GB | **7.8/8.0 GB, 0.025 Hz** vs ~11 Hz expected (~400× slow) | SheepRL #227 |
| **S-scale ms_pacman 64×64, GTX 1080 8GB** | **ran at 1.4 Hz**, "more reasonable" (VRAM not reported) | SheepRL #227 |
| XL MsPacman, batch 8, seq 98 | fp32 **13.37 GiB**; bf16 **23.83 GiB** | SheepRL #240 |
| DreamerV3 on **CarRacing-v2** (config unstated) | **OOM at 10.91 GiB** (GTX 1080 Ti) | SheepRL #207 |
| size200m Tetris, RTX 3090 24GB | **OOM** after ~12 h | dreamerv3 #152 |
| TD-MPC2 single-task (5M params, state or pixels) | author states **≥8 GB** | repo README |
| Ha & Schmidhuber World Models (CarRacing) | **4.77M params total**, <1 h/component on 2018 GPU | arXiv 1803.10122 |

The S-scale row is the load-bearing one, and its weakness is stated plainly
below.

### Offline training helps — for one specific, published reason

V-D4RL (Lu et al., TMLR 2023) built Offline DreamerV2 for exactly this
workload. Their offline hyperparameters: batch 64, sequence length 50,
**imagination horizon 5 (vs online 15)**, 64×64, 100k transitions. Their
stated rationale for the shorter horizon: *"reduction in horizon is required
due to the lack of online 'remedial' sampling."* Horizon 15→5 cuts the
actor-critic imagination rollout roughly 3× — a real memory saving that
comes free with going offline. (Their batch 16→64 increase is a
data-efficiency choice, not a memory one — do **not** copy that on 8GB.)
Reported compute: 10 hours on a V100 for 100k transitions.

### Why PyTorch, not the JAX reference

- **JAX does not support native Windows CUDA.** Its official install table
  lists Windows x86_64 NVIDIA GPU as "No" and WSL2 as "Experimental"
  (verified directly, 2026-07-23).
- **The JAX reference has no offline mode.** Issue #80 asks how to train on
  a gathered dataset; closed without a documented answer.
- **`NM512/dreamerv3-torch` has offline support built in** (verified
  directly, 2026-07-23): `offline_traindir` / `offline_evaldir` load
  episodes from a directory, and `if not config.offline_traindir: prefill =
  ...` means setting it **skips environment prefill entirely**. Its defaults
  are already S-scale (dyn_deter 512, cnn_depth 32, units 512, batch 16,
  length 64, 64×64, precision 32). **Do not apply its crafter/atari100k
  overrides** — those jump to XL (dyn_deter 4096, cnn_depth 96).
  *Unverified caveat from the worker: whether the loop runs end-to-end with
  zero environment instantiation was not tested. Test before committing.*
- V-D4RL's own codebase is TensorFlow 2 (DreamerV2 derivative), and TF
  dropped native-Windows GPU support after 2.10 — so it is WSL2-only too.

### The Windows trap that would waste a day

NVIDIA driver 536.40 (June 2023) introduced **CUDA Sysmem Fallback**: when
VRAM runs out, the driver spills into shared system memory instead of
failing. A measured consequence on the PyTorch forums: 4.5 s/iteration using
shared memory versus 1.5 s/iteration restricted to dedicated — **3× slower,
silently.** This is precisely the "16GB shared" in Evan's spec. It is host
RAM over PCIe (~25 GB/s) against 448 GB/s of GDDR6 on the 3060 Ti. **Set
NVIDIA Control Panel → Manage 3D Settings → CUDA - Sysmem Fallback Policy →
"Prefer No Sysmem Fallback"** (global or per-app on `python.exe`) so
out-of-memory fails loudly instead of degrading invisibly.

Related: **WSL2 does not give more VRAM.** No evidence was found for that
claim; the GPU is still owned by the Windows WDDM driver. WSL2 buys
*compatibility* (JAX, TF≥2.11) and clean OOM behaviour, nothing more.

### Mitigations that turn out not to be levers

- **Mixed precision:** already baseline in the JAX version
  (`compute_dtype: bfloat16`), so that saving is spent. In PyTorch it is
  available (default is fp32) — but the one available measurement shows
  bf16 *costing* 10.5 GiB more and running slower. The 3060 Ti (GA104, CC
  8.6) does support bf16 tensor cores, so the hardware is fine; the software
  behaviour is the uncertainty. **Measure, don't assume.**
- **Gradient checkpointing:** no DreamerV3-specific benchmark exists, and
  none of the three codebases ships a documented RSSM checkpointing flag.
  Unimplemented last resort, not a lever.

### Dataset size — the reassuring finding

DonkeyCar's own guidance: *"We want about 10,000 of these"* and *"Donkeycar
records data 20 times per second"*; a second source says 10–20 laps / 5–20k
images. V-D4RL's offline visual standard is 100k transitions.

Derived (arithmetic, not sourced): at 20 Hz, 5–20k frames = **4–17 minutes**
of driving; 100k frames = **83 minutes**; 200k = **2.8 hours**. At 64×64×3
uint8 = 12,288 B/frame, 100k frames = **1.23 GB**, 200k = **2.46 GB** —
RAM-resident and trivially uploadable to Kaggle or Colab.

### Scale calibration, so the writeup doesn't overclaim

comma.ai's *Learning to Drive from a World Model* (CVPRW 2025) uses a
250M/500M/1B-param diffusion transformer on 100k–400k one-minute segments.
Dreamer 4 reached Minecraft diamonds purely offline using 2.5K hours of
video and 256–1024 TPU-v5p. Both are the right *concept* at five orders of
magnitude the wrong *scale*. Say so explicitly in any portfolio writeup.

---

## Recommended config (primary attempt)

```
Implementation:  NM512/dreamerv3-torch   (PyTorch, native Windows CUDA, offline support)
Mode:            --offline_traindir <logdir>/episodes  --offline_evaldir <logdir>/eval
Model:           repo DEFAULTS (≈ paper "S", ~18M) — do NOT apply crafter/atari overrides
                 dyn_deter 512   dyn_hidden 512   units 512   cnn_depth 32
Observation:     [64, 64] RGB
    batch_size      16    → fallback 8 → 4
    batch_length    50    (V-D4RL offline value; keep ≥32 — temporal context is the point)
    imag_horizon    5     (V-D4RL offline finding, NOT the default 15)
    precision       32    first run — measure, then try 16 and measure again
Dataset:         100k–200k frames @20Hz = 1.4–2.8 h driving = 1.2–2.5 GB
Driver:          Sysmem Fallback Policy = "Prefer No Sysmem Fallback" on python.exe
Instrument:      log torch.cuda.max_memory_allocated() every epoch
OS:              native Windows (WSL2 buys no VRAM; only switch for a JAX/TF codebase)
```

## Fallback ladder

1. Primary config above.
2. **Shrink the batch, keep the model:** 16 → 8 → 4. Keep `batch_length` ≥32.
3. **Try precision 16, then measure.** If `max_memory_allocated` goes *up*,
   revert immediately (see the bf16 counter-measurement).
4. **Shrink the model below S:** dyn_deter 512→384→256, cnn_depth 32→24→16.
   *Unsourced territory* — the paper's smallest published size is XS at 8M
   and no published result uses the repo's `size1m`. Below XS you must
   demonstrate it still learns useful dynamics yourself (held-out
   reconstruction/rollout quality is the check).
5. **Drop resolution** (56×56, 48×48). Costs comparability with every
   published number — do this only after 2–4.
6. **Escalate to Kaggle Notebooks:** ~30 GPU-hours/week free, T4/P100,
   **16 GB** VRAM, 12-hour sessions. Doubles the VRAM for free and the
   dataset uploads with no friction. *Figures corroborated but not from a
   single fetchable authoritative Kaggle page — verify in-product.*
7. **Colab.** 12 h max runtime; Google explicitly does not publish limits.
   Less predictable than Kaggle for this workload.
8. **Architecture fallback — the guaranteed result:** Ha & Schmidhuber
   V+M+C on the same logs. Conv-VAE (~4.3M) → z∈ℝ³²; MDN-RNN (~0.4M) over
   (z_t, a_t, h_t) → p(z_{t+1}); policy from the latent, extracted either by
   latent behavioural cloning on (z,h)→action or by CEM/random-shooting
   planning through the learned dynamics. Minutes-to-an-hour on a 3060 Ti;
   will never OOM.

## Recommended sequencing (this is the actual plan change)

**Build rung 8 first, before attempting rung 1**, on the same logged
dataset. It costs about a day, de-risks the entire data pipeline (recording
format, frame/action synchronisation, held-out splits, the on-car evaluation
protocol), and guarantees M4 finishes with a real world-model result no
matter where the 8GB boundary falls. Then attempt DreamerV3-S with the
identical dataset and identical eval harness.

The output is two architectures, one dataset, one evaluation protocol, an
honest comparison table, and a documented VRAM boundary that nobody has
published. That is a stronger artifact than a single successful DreamerV3
run, and it converts the hardware constraint from a risk into a finding.

## What would change this conclusion

- **The S-scale claim rests on one user's throughput observation with no
  VRAM number reported for the S run.** Nobody has published GB-for-S.
- **SheepRL #207: DreamerV3 on CarRacing-v2 — the closest published
  analogue to this project — OOM'd on 10.91 GiB**, 36% more VRAM than Evan
  has. The config is unstated; if it was default-XL that explains it, but
  that cannot be verified, so it stands as a live counter-example on the
  exact task family.
- Mixed precision, the standard 8GB rescue, backfired in the one PyTorch
  measurement available.
- Gradient checkpointing is not implemented in any of these codebases.
- Windows desktop/browser holds several hundred MB to ~1.5 GB of the 8 GB
  (worker's estimate, unsourced) — the real budget is nearer 6.5–7.5 GB.
- The `dreamerv3-torch` offline path was verified to exist in source but
  **not** verified to run end-to-end with zero environment instantiation.

**Bottom line: the primary config is a well-reasoned bet, not a guarantee.**
Budget one sitting to find the OOM boundary empirically and record the
number — that measurement is itself a portfolio artifact.

## Verification (reviewer, 2026-07-23 ~17:39 CDT)

| Claim | Primary source | Result |
|---|---|---|
| `dreamerv3-torch` supports `offline_traindir`/`offline_evaldir` and skips prefill | raw `dreamer.py` @ main | **MATCH** — all three lines present; prefill runs only when `offline_traindir` is unset |
| JAX: no native-Windows CUDA; WSL2 experimental | docs.jax.dev install table | **MATCH** — Windows x86_64 NVIDIA = "no"; WSL2 = "experimental" |

## Sources

Primary artifacts read directly: `danijar/dreamerv3` configs.yaml + README +
issues #80/#131/#152 · `NM512/dreamerv3-torch` dreamer.py + configs.yaml ·
SheepRL configs (`dreamer_v3_S.yaml`, `dreamer_v3.yaml`,
`dreamer_v3_100k_ms_pacman.yaml`, `dreamer_v3_XL_crafter.yaml`) + issues
#207/#227/#240 · `nicklashansen/tdmpc2` README ·
`m-barker/somniloquy-dreamer-v3` README · arXiv 2301.04104 (DreamerV3,
ar5iv) · arXiv 1803.10122 (Ha & Schmidhuber, ar5iv) · arXiv 2206.04779
(V-D4RL) + `conglu1997/v-d4rl` · arXiv 2504.19077 (comma.ai) ·
docs.jax.dev installation · tensorflow.org/install/pip ·
docs.nvidia.com Ampere Tuning Guide · Colab FAQ · docs.donkeycar.com +
docs.robocarstore.com train_autopilot · PyTorch Forums sysmem-fallback
thread · videocardz + NVIDIA KB 5490 (sysmem fallback, secondary) ·
Kaggle product-feedback/docs (verify in-product) · emergentmind Dreamer 4
summary (secondary). All accessed 2026-07-23.

**Explicitly could not be found — reported as missing, not fabricated:**
any published VRAM-per-size table for DreamerV3 at 64×64; verified param
counts for the current repo presets; the retracted "~24GB" practitioner
guide; any published DreamerV3-offline-on-real-small-RC-car-logs result
(i.e. **no recipe exists to copy for M4 as specified**); any RSSM
gradient-checkpointing benchmark; any quantitative WSL2-vs-native usable-VRAM
comparison.
