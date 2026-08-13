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

## The latent encodes lane position NONLINEARLY (P5, 2026-08-07)

**Measured, and it invalidates a design the paper hands you for free.** Probing
cross-track error from the ConvVAE latent z:

| probe | val R² |
|---|---|
| linear | **0.27** |
| MLP (256-256) | **0.97** |

The information is there — the encoding is not linear. Consequences:

- **Ha & Schmidhuber's linear controller C cannot lane-follow on this latent.**
  It structurally cannot compute the one quantity the task depends on. Swapping
  to one hidden layer cut offline action MSE 4.9× and in-sim lane error 2.4×
  (0.435 vs 0.435 expert-level 0.381). Do not assume the paper's C transfers.
- **Anything that scores imagined latents needs a nonlinear readout.** The CEM
  planner uses the MLP probe; the linear one would optimise a proxy explaining
  a quarter of the target.
- Expect the same for any future readout (heading, distance-to-stop-line). Probe
  it linearly first — the linear R² is a statement about the LATENT, and the
  linear-vs-MLP gap is the finding worth recording.

**No learned policy completed a lap** (linear BC, MLP BC, CEM planning; 3 seeds
× 3 episodes each) while the PID expert completed 9/9. All three wall at 69-110
steps. **CAVEAT (2026-08-12): true AS SCOPED to those three arms and that one
batch, but do not generalise it — completions have since been observed on other
arms, and every step count here came from a harness later measured at CV 55%
where n=1 resolves only ~3×. See the retraction section above.** Corner speed was tested and ruled out (lowering throttle made it worse).
**The bottleneck is the representation and dynamics, not the controller** — the
expert is the only policy that never touches the latent. Full table: record
Appendix V.3.1.

## THE WALL IS PERCEPTION GOING OUT OF DISTRIBUTION (measured 2026-08-07)

Appendix V left "why does every learned policy die at 69-110 steps" open.
`ml/trace_failure.py` separates the three stages that could be at fault --
perception (does the probe still read lane position correctly?), dynamics
(does the RNN's H-step prediction match what happens?), and control -- by
logging all three per step against the actions actually taken.

**Perception error is a function of POSITION, not of policy or elapsed time:**

| \|actual cte\| | perception err, MLP policy | perception err, PID expert |
|---|---|---|
| 0.0 - 0.3 | 0.202 | 0.198 |
| 0.3 - 0.6 | 0.267 | 0.315 |
| 0.6 - 1.0 | 0.307 | 0.447 |
| 1.0 - 1.5 | 0.625 | 0.665 |
| 1.5 + | **2.104** | **1.734** |

corr(|cte|, perception error) = **0.894** (MLP) and **0.852** (expert). Two
completely different drivers, one learned and one hand-tuned, produce the same
curve — so it is where the car IS, not what is steering.

**Root cause: the corpus has no off-centre frames.** `collect_sim_data.py`
rejects any episode with `mean|cte| > MAX_MEAN_ABS_CTE = 1.2`, and the expert
averaged 0.36. The VAE and the probe were therefore never shown what far-off-
centre looks like, and perception collapses in exactly the region a recovering
policy must operate in. **The failure is unrecoverable by construction:** drift
past ~1.0 and the policy can no longer see where it is, so it cannot steer back.

**Consequences, and these carry to the real car:**

- **This is a DATA problem, not a controller problem.** No amount of policy
  architecture fixes it — confirmed by three policy classes failing identically
  (Appendix V.3.1). The fix is recovery data: DAgger-style relabelling, or
  deliberately starting episodes off-centre and recording the expert's
  correction.
- **M3/M4 must collect off-centre recovery demonstrations on the physical
  car**, or the same wall appears on hardware. A corpus of only clean expert
  driving teaches a policy that cannot recover from its own mistakes.
- **A quality filter that rejects bad episodes also deletes the recovery
  data.** `MAX_MEAN_ABS_CTE` was added to keep the corpus clean and it does —
  at the cost of the only frames that teach recovery. Keep the filter for the
  imitation set; collect a SEPARATE recovery set that is deliberately exempt.
- The trace tool adds an encode plus an H-step imagination per control step,
  which slows the loop enough to degrade even the expert (its last-25%
  mean|cte| rose to 1.213 vs 0.367 in the uninstrumented eval). Within-run
  correlations are unaffected; absolute survival numbers from a traced run
  are not comparable to `eval_in_sim.py`.

## BOTH encoders erase small objects (measured 2026-08-08)

The ConvVAE drops orange traffic cones; the open question was whether
DreamerV3's much larger RSSM keeps them. It does not. 32 held-out frames,
28 cone px each (0.69% of frame), `ml/compare_encoders.py`:

| model | cone err | bg err | ratio | cone px surviving |
|---|---|---|---|---|
| ConvVAE | 0.2200 | 0.0500 | 4.40x | **0 / 899** |
| DreamerV3 | 0.1982 | 0.0640 | 3.10x | **0 / 899** |

**Zero surviving cone pixels in either.** Road, lane lines and treeline are
preserved. A bigger world model is NOT the mitigation — the options are higher
input resolution, an auxiliary detection/segmentation head, or a reward the
object actually moves. **This threatens the M4 stop-sign showcase**, which
assumed the sign reaches the latent. Caveat: the DreamerV3 checkpoint had
2,000 steps vs the VAE's 40 epochs and its worse background error is
consistent with undertraining — but 0/899 is an absence, not a blur.

**Method warning attached to this result.** The first version of that script
reported only cone-error / background-error RATIO and auto-concluded
"DreamerV3 preserves cones better, the showcase is not threatened". Wrong:
the ratio improved because DreamerV3's BACKGROUND error is 28% worse, not
because it kept the cone. **A derived ratio can improve for the wrong reason.**
Prefer a metric that asks directly whether the thing is still there — here,
re-running the colour detector on the reconstruction. Render the artifact and
LOOK at it; the panel showed both erasures instantly.

## Recovery data fixes off-centre perception with a FROZEN encoder (2026-08-08)

The direct test of the W.1 diagnosis. `ml/collect_recovery.py` adds off-centre
states by DART-style noise injection (burst of steering noise every 60 steps
for 8 steps, then the PID drives home). 18 episodes, 5,961 frames,
**mean|cte| 0.95 vs the original corpus's 0.36** — 6.7% of the augmented set.

`ml/exp_recovery.py` trains two probes against the **same frozen ConvVAE**:

| \|cte\| bucket | baseline | + recovery | change |
|---|---|---|---|
| 0.0 - 0.3 | 0.057 | 0.069 | +21% |
| 1.0 - 1.5 | 0.268 | **0.159** | **-41%** |
| 1.5 + | 0.591 | **0.214** | **-64%** |
| off-centre (>=1.0) | 0.429 | **0.186** | **-57%** |

**The latent already contained off-centre lane position; only the readout was
starved.** No VAE retrain needed — the cheap branch. Tradeoff: centred buckets
get ~20% worse as the probe spreads capacity over a wider range; overall error
still improves (0.093 -> 0.086).

**This narrows the case against the ConvVAE.** The encoder was never the
problem for LANE POSITION. It is still the problem for small OBJECTS (0/899
cone pixels, above) — do not conflate the two failures.

**Use DART, not DAgger, for the real car.** DAgger needs an expert relabelling
states the learner visits, i.e. a human riding along with a controller every
run. Noise injection needs only the scripted expert, so the same procedure
transfers to hardware. That is why M3's recovery set is collectable at all.

**Still untested:** whether this makes the car drive further. The probe result
proves perception is cheaply fixable, not that the wall is beaten.

## Steering smoothness: real knob, wrong target (2026-08-08)

The CEM planner oscillates at **20.90 reversals/100 vs the expert's 9.84**
(2.13x); the BC controllers do NOT (8.50 linear, 9.28 MLP). Sweeping
`--w-smooth` (1 seed x 2 episodes, so directional only):

| `w_smooth` | rev/100 | mean\|cte\| | steps |
|---|---|---|---|
| 0.05 | 21.4 | 0.346 | 82 |
| 0.5 | 9.8 | 0.675 | 86 |
| 1.0 | 6.4 | 1.049 | 97 |

- Jitter falls monotonically, 3.3x. `w_smooth = 0.5` matches expert smoothness.
- **Survival does NOT improve** (flat/noisy) — so jitter was never what killed
  the car. Independent corroboration that the wall is perception.
- Lane-holding is the cost: mean|cte| triples. At 0.05 the planner tracks the
  lane BETTER than the expert (0.346 vs 0.367) — precise but jittery.
- **Penalise the RATE of steering change, never the ANGLE.** A corner needs a
  large sustained angle, so an angle penalty causes understeer; on straights it
  is redundant because the cte term already charges for off-line steering.

## The latent does NOT contain small objects, and the obvious probe lies (2026-08-10)

`ml/probe_cone.py`, frozen ConvVAE, cone labels from the W.2 colour detector.

- Held-out **AUC 0.997** for "is a cone visible". Reads as a total success.
- **It is meaningless.** Paint the cone out (verified 0 cone px left) and the
  probe's score moves from 0.946 to 0.938 — **1% of the pos/neg gap**. It was
  reading TRACK POSITION, not the object.
- Cones sit at fixed track locations and the latent encodes position well
  (cte probe R² 0.957), so position alone predicts cone presence.

**So the aux head is the EXPENSIVE branch.** The hoped-for X.1-style result
(signal already in `mu`, readout just needs data) is refuted for objects. The
aux loss has to reshape the ENCODER → VAE retrain.

**Two consequences that generalise beyond cones:**
- **Never measure small-object perception on a FIXED-position object.** Any
  such measurement is confounded by position. `exp_aux_head.py` injects a
  synthetic object at uniform random position for exactly this reason.
- **The M4 stop sign must be RELOCATABLE.** On a fixed track a policy passes
  the showcase by stopping at a location while blind to the sign. Recorded as
  a hard requirement in PRD 6(b), not a preference.

**Control design rule, learned the hard way twice (W.3, then this):** a
control that varies the LABEL (shuffled labels) tests the architecture; a
control that varies the INPUT (ablate the thing you claim to detect) tests the
claim. Here the shuffled control read 0.427 and would NOT have caught it —
only the counterfactual did.

## Recovery data: executed actions are the WRONG BC label (2026-08-10)

`collect_recovery.py` stores the action ACTUALLY EXECUTED including injected
noise, because the data contract is action[i] produced image[i]. Cloning that
teaches the car to swerve.

- `ml/build_expert_labels.py` writes `train_actions_expert.npy` into the proc
  dir: `log_expert_steer` substituted on noise frames, throttle recomputed by
  the collector's own rule. **805 frames, 0.82% of the augmented corpus.**
- `train_controller.py` auto-prefers that file when present, and gained
  `--proc` so it can train on `ml/data/proc_aug` with V and M frozen.
- Corpus ground truth: **98 episodes / 98,230 frames = 78 original (91,678) +
  20 recovery (6,552)**. Recovery mean|cte| 0.971 vs original 0.322.
  (Record Appendix X said 18 episodes / 5,961 frames — wrong, corrected in
  Appendix Y.4. It came from one collection run's stdout; the directory
  already held 2 episodes from an earlier run.)

## RETRACTION (2026-08-11): the "first completions" result did not replicate

The 342.4-steps / 3-of-9 headline below is **withdrawn**. Ten seeds across two
independent gate-valid batches give **107.2 ± 16.0, 0/20 completions**; the
same three checkpoints that scored [78,600,600] / [600,469,448] / [96,96,95]
re-ran at [100,113] / [108,108] / [107,107]. The re-runs are tight (all 10
seeds 85–147) where the original was chaotic (sd 230), so the original batch
is the anomaly. ~~**No learned policy has completed an episode.**~~ **That
flat claim is FALSE — an overcorrection, caught by landing-check 2026-08-11.**
3 completions exist in `ev3_nh_aug` and 1 in `ev2_nh_aug`. The true statement:
**no learned policy completes RELIABLY.** Pooled over **47** gate-valid
`nh_aug` episodes the distribution is **bimodal** — **30 under 150 steps, 6 at
450-601**, almost nothing between — with **4 completions**, and every one of
them from a single launch.

**The lesson is bigger than the result: the expert-survival gate is NECESSARY
BUT NOT SUFFICIENT.** Both batches pass it (expert 600/600) and disagree 3×.
**Never rest a closed-loop claim on one batch — replicate in an independent
one.**

**THE LAUNCH IS THE UNIT OF VARIATION (measured 2026-08-11).** Same checkpoint,
same seed, **seven** gate-valid launches: **106.5, 118.5, 179.5, 205.5,
232.0, 353.5, 471.5 steps — a 4.4× spread, CV 55%**, while episodes WITHIN a
launch agree to a few steps. Eliminated as causes: control rate (matched
~20 Hz), track identity (expert cte 0.323-0.381 over 12 launches), and
**episode start state** — `ml/diag_reset.py` shows post-RESET POSITION
near-deterministic (z identical; x identical for 14 of 16 episodes, episode 0
of each launch differing by 2.8e-4 world units). **NOT "deterministic to four
decimals"** — post-warmup cte spans 0.0018-0.0075, which is ~0.6% of the ~0.87
cte the car operates at, i.e. far too small to explain a 4.4× swing. Cause
still unknown.

**The 2×2 table below is NOT a matched comparison** (landing-check). The arms
do not share batch sets. Restricted to the two batches common to all four arms
(ev3, ev4): cl_base 190.3, cl_aug 167.8, nh_base 109.25, **nh_aug 232.8** —
the ranking flips and nh_aug is top. **Only the "removing `h` hurts" leg
survives matched-batch restriction** (109.25 vs 190.3); "the plain baseline is
best" does not.

## The controller ignored `z` and rode the RNN state (2026-08-11; closed-loop half RETRACTED, open-loop half stands)

`ml/diag_copycat.py`, held-out, skill = 1 − MSE/var:

| comparison | MSE | skill |
|---|---|---|
| controller → a[t] | 0.001755 | 0.993 |
| a[t−1] → a[t] (trivial copy) | 0.031997 | 0.873 |
| **controller with h=0 → a[t]** | **0.282040** | **−0.120** |

- **Copycat (Wen et al. NeurIPS 2020) is REFUTED** — beats repeat-last-action
  by 18.2× and predicts a[t] better than a[t−1].
- **But it depends almost entirely on `h`.** Zero it and the model is worse
  than predicting the mean. **`h` is teacher-forced on LOGGED expert actions
  in training and built from the POLICY's own actions at serve time**, so the
  one input it uses is the one that drifts. Compounding error through the
  recurrent state — not the same failure as perception OOD.

**The 2×2 — ONE BATCH (ev3), and its `nh_aug` cell did NOT replicate. Kept for
the record; do not cite the bottom-right number:**

| | with `h` | `z` only (`--no-history`) |
|---|---|---|
| original | 185.6 (0/9) | 109.3 (0/9) |
| + recovery | 196.6 (0/9) | ~~342.4, 3/9~~ **RETRACTED — see above** |

- **Neither change works alone; the interaction is the result.** z-only alone
  is *worse*. Recovery data alone does nothing. A one-variable-at-a-time
  search rejects both.
- **This vindicates the 57% probe finding** — it was necessary but could not
  express itself while the controller ignored `z`. It also means the
  `--recovery-weight` null had a cause I got wrong (not "drowned out in the
  objective" — no weighting helps when the model ignores the input).
- **Variance is high: per-seed [426, 506, 96].** Not a solved task.

**DO NOT SELECT CONTROLLERS ON OPEN-LOOP MSE.** It ranks these arms backwards:
the best-driving arm has the worst val MSE by **16×** (0.02846 vs 0.00177).
Exactly Codevilla et al. (ECCV 2018), measured on this stack.

## The paired closed-loop comparison: no intervention helps (2026-08-13, AJ)

**First closed-loop comparison in this project that is a measurement rather
than an anecdote.** `ml/eval_paired.py` runs every arm inside ONE launch so
all share that launch's generated track, and differences are taken
within-launch, cancelling track difficulty. Verified on synthetic data with a
known +40 effect and per-launch offsets of +0/+300/-100: paired diff recovered
+40 at **sd 0.0**, unpaired sds 208.

4 launches x 3 seeds x 2 episodes, expert 600/600 in every launch:

| arm vs cl_base | mean diff | sd | t (df=3) | signs |
|---|---|---|---|---|
| cl_aug (+recovery) | **-26.0** | 28.4 | -1.84 | **4/4 negative** |
| nh_base (z-only) | -15.7 | 58.8 | -0.53 | 2/4 |
| nh_aug (z-only +rec) | +49.3 | 121.2 | 0.81 | 1/4 |

- **NO ARM BEATS THE BASELINE.** Five attempts have now failed to transfer
  X.1's 57% probe improvement to driving.
- **The most consistent signal says recovery data mildly HURTS** with `h`
  present (4/4 negative). Not significant; ~19 launches needed.
- **`nh_aug`'s advantage is ONE launch (+221) for the second time** — the first
  was the retracted Appendix AB. **High-variance and occasionally lucky, not
  better.** Assume any future headline from this arm is that launch again.
- **A FIXED TRACK DOES NOT WORK as the fix.** `donkey-avc-sparkfun-v0` (MAE
  0.367) and `donkey-mountain-track-v0` (0.481) are genuinely fixed, but the
  controllers collapse to 13-67 steps at mean|cte| 2.2-3.8 there — far OOD.
  `donkey-generated-roads-v0` (3.504) is ALSO regenerated.
- **Pairing helped 2 of 3 arms and RAISED variance for `nh_base`** — so real
  arm x track interaction exists and cannot be designed away.

**Gate defect, unfixed:** the expert-survival batch gate fires BATCH INVALID on
a harder track (expert 425/549 of 600 on the fixed tracks) because it cannot
distinguish "simulator degraded" from "track harder than the expert's tuning".

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
