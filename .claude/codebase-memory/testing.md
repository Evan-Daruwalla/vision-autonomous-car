# testing.md — Autonomous Car Project

No test framework is installed (verified 2026-08-06: no pytest, no linter, no
CI config). Verification is done by **runnable self-checks and done-checks
that exit non-zero on failure** — the project's actual gates. Adding `ruff`
and a `tests/` directory before M3 is an open audit item (F20).

## The gates that exist, and what each one actually proves

| Command | Proves | Notes |
|---|---|---|
| `python ml/verify_env.py` | CUDA is live and the simulator returns a camera frame | SIM-POC P1 done-check. Launches the sim — don't run it while collecting |
| `python ml/verify_corpus.py ml/data/sim` | the driving corpus is structurally valid, frame/action aligned on BOTH axes, at 120×160, within the collector's quality thresholds, and the layout split is disjoint | SIM-POC P2 done-check. O(1) memory. **PASS 88/88, 102,888 frames, mode -1 (re-run 2026-09-02 after A4)** |
| `python ml/verify_corpus.py ml/data/sim_recovery` | the same, on the noise-injected recovery corpus: PID identity against `log_expert_steer`, throttle against the EXECUTED steer, and **`log_noise` proven honest** — executed == expert on clean frames, != on flagged ones | **Added 2026-09-02 (A4, Appendix CD): this had NEVER been run, and failed four gates when it was.** A flag that exempts frames must itself be checked, or it exempts anything. **PASS 20/20, 805 noise frames verified.** The corpus is train-only by design, so the layout gate reports not-applicable from `log_recovery` in the npz, never a CLI flag |
| `python ml/models.py` | the world model's layers are wired to the paper — asserts the VAE has **exactly 4,348,547** params | reproducing a published count to the digit is a stronger wiring check than reading the code. **The assert now lives in `ConvVAE.__init__`**, so every training/eval run re-checks it, not just this command |
| `python ml/splits.py` | the fit/val split is disjoint, exhaustive, stratified, and reproducible; a different seed gives a different split | catches a seed being silently ignored |
| `python ml/rollout_eval.py` | 30-step imagination beats a frozen-frame baseline on ≥90% of steps **(exits 1 if not)** | SIM-POC P3 done-check. Gated on `val_indomain` only — holdout is *expected* to lose (0/30), so gating on it would fail a correct model |
| `python ml/probe_vram.py` | whether an OOM can actually happen on this machine | exit 1 means Sysmem Fallback is ON — a finding about the machine, not a broken check |
| `python ml/eval_in_sim.py ...` (every run) | **batch validity.** The PID expert is fixed code with no learned part and completes 9/9 on a healthy sim. Below that, the SIMULATOR was degraded and every controller number in the batch is untrustworthy — prints a BATCH INVALID banner, writes `batch_valid: false`, **exits 2** | added 2026-08-11 after a whole 2×2 batch had to be thrown away (expert fell to 4/9 then 0/9 at a normal ~20 Hz having been 9/9 all evening). Verified by replaying it against artifacts already on disk: passes the healthy batches, fails the degraded one. Pair with the `ctrl Hz` column — a step count is only comparable to one taken at the same rate |
| `python ml/exp_aux_head.py --self-check` | the synthetic-object pipeline is sound: injected mask area matches the plan, the colour detector fires **exactly** on the injected pixels (so the survival metric counts the right ones), the un-injected frame is a clean counterfactual, the 8×8 aux target matches the object's cells, injection is deterministic per frame index, and object position is genuinely spread | guards the three things every conclusion in that experiment rests on and none of which are visible in its result table. Position spread is the load-bearing one — a fixed-position object is predictable from track position and would prove nothing (Appendix Y.2/Y.3) |

**Cold audit 2026-08-06 fixed four gates that could not fail.** Before it:
`rollout_eval.py` printed its win count and discarded it (0/30 exited exactly
like 30/30); `gen_tolerance_coupon.py` wrote the STL *before* validating and
always exited 0; `sweep_dreamer_p4.py` inferred success from a file existing
rather than the child's exit code; and `models.py`'s param assert never ran
outside `__main__`. **A gate that cannot fire is not a gate** — and all four
were documented, here and in the README, as if they were.

## Rules learned the hard way

- **A checker that misdiagnoses is worse than one that abstains.** Three
  false-diagnosis bugs were found in `verify_corpus.py` alone (gating on
  peak-lag zero; omitting `log_ki`; reporting weak correlation as
  misalignment). Every one asserted a constant that was not constant. When a
  measurement is too noisy to judge, report UNVERIFIABLE, never WRONG.
- **Every claim needs a baseline.** "The rollout looks track-like" is
  unfalsifiable — every frame of a driving corpus looks track-like. Compare
  against a do-nothing predictor (freeze the last real frame) or the claim
  means nothing.
- **Seed everything and record the seed.** All training scripts take `--seed`
  and seed torch, numpy and CUDA. Evaluation subsets use a *fixed* separate
  seed so epoch-to-epoch numbers are comparable.
- **One seed is not a measurement** for any comparative claim — the routing
  research found seed variance in driving policies reaching tens of points.
  P3 used one seed because it is a pipeline proof, not a comparison; P4/P5
  comparisons need ≥3.
- Adversarial self-testing works: deliberately corrupting a corpus (rolling
  the image axis, emptying a split, removing the holdout) is what exposed
  that the P2 gate did not check what its docstring claimed.
- **Verify a gate by making it FAIL, not by watching it pass.** Every fix in
  the 2026-08-06 audit pass was checked in both directions — the coupon was
  fed impossible geometry, `rollout_eval` an unreachable threshold,
  `preprocess` a simulated Ctrl-C, `verify_corpus` a malformed filename. A
  green run proves nothing about a check that has no red path.
- **A cache keyed on less than what produced it is a silent-corruption
  machine.** `{split}_mu.npy` was keyed on the split name alone, so retraining
  the VAE meant the MDN-RNN learned dynamics in one latent space while
  rollouts decoded through another. Latent caches now carry a
  `{split}_latents.key` fingerprint of the encoder; a missing key is
  UNVERIFIABLE (warn), a different key is WRONG (exit 1).
- **Exit codes, not artifacts, are the success signal for a subprocess.**
  Committed result files make "the output exists" indistinguishable from "the
  run worked" — and republishing a stored number as a fresh measurement is
  the worst failure this project can have.

## Firmware gates (added 2026-09-02, hardware lane)

No test framework here either. The Uno sketches in `firmware/` verify
themselves over the serial console; there is no host-side runner.

| Command | Proves | Notes |
|---|---|---|
| `SELFTEST` on `firmware/uno_packguard` | the pack low-voltage state machine is correct: OK→WARN→CUTOFF thresholds, the 500 ms hold that ignores stall dips, that CUTOFF **latches** (a recovered or even full pack stays cut), that FAULT is distinct from CUTOFF and does NOT latch, and that both CUTOFF and FAULT inhibit throttle | **27/27 PASS on the real board 2026-09-02** (Appendix BJ). Runs automatically in `setup()` as well as on demand |
| `SIM <mv>` / `REAL` / `CLEAR` / `STATUS` on the same sketch | lets every state transition be driven without discharging a real pack | The divider itself and the ADC path are NOT covered by SELFTEST — only the logic downstream of a millivolt reading is |

**The gate is testable because the transition is a pure function.** `step(mv,
now)` takes voltage and time and returns a state, so SELFTEST exercises
*exactly* the shipping logic rather than a copy of it. Any firmware state
machine added later (the serial protocol's ARMED/watchdog logic is the next
one) should be factored the same way — the alternative is a state machine only
testable by driving the car.

**Two guards here exist because a naive check would have been backwards:**
- A **floating analog pin reads near full scale, not zero** — measured 10248 mV
  on the first build with nothing wired to A0. So the sensor guard needs an
  *upper* implausibility band (>8.8 V ⇒ FAULT), not just a lower one. A
  lower-only guard would have read an unwired divider as a healthy pack.
- CUTOFF **latches** deliberately. An unlatched cutoff would re-enable as the
  pack relaxed a few hundred mV above threshold, sag under load, and oscillate.

**`uno_bringup`, `uno_memtest`, `uno_echo` are MEASUREMENTS, not gates** — they
have no pass/fail and exit nothing. They produced the board facts in
`gotchas.md` (2048 B SRAM / 1705 B free, 16.0042 MHz measured, link p50
0.869 / p99 1.069 ms). Do not cite them as verification of anything else.

## Control firmware gates (added 2026-09-02, Appendix BO)

| Command | Proves | Notes |
|---|---|---|
| firmware SELFTEST on `firmware/uno_control` (runs in `setup()`, or send `T`) | CRC8 against the 123456789=0xF4 reference vector, whole-frame CRC, steering/throttle clamping, the duty cap, the **whole four-input safety decision** (`outputModeFor`), the pack transitions, and the quadrature table's antisymmetry | **PASS 39/39 on the real board 2026-09-02.** Same discipline as `uno_packguard`: the safety decision is a PURE function, so the test drives shipping logic, not a copy |
| `.venv/Scripts/python.exe firmware/host_test.py --port COM3` | the protocol end-to-end on hardware: reply framing and CRC, seq echo, a 20 Hz stream, bad-CRC rejection, the 150 ms watchdog, the `?` escape hatch, and that **STBY stays LOW with no pack sensor** | **PASS 13/13, exit 0, 2026-09-02 ~19:55 CDT** (two checks added for the watchdog defect, CA). Exits non-zero on any failure, so it is a gate. Needs `pyserial` (installed into `.venv` 2026-09-02) |

**Compiling is not running, and this is the evidence.** `uno_control` compiled
clean (7134 B flash, 312 B SRAM) while carrying **three wrong assertions**. Only
flashing it and reading the board surfaced them: one asserted the pack latch
outranked a fault reading when the firmware — correctly, matching the tested
`uno_packguard` — does the reverse, and two asserted an encoder direction that
**is not knowable until the encoder is on a motor.** A green compile said
nothing about any of them.

**The lesson generalises: do not assert a sign, a direction, or a polarity that
no measurement has established.** Test the property that survives the
convention instead — here, that the two directions are exact opposites and that
`QTAB` is antisymmetric across all 16 entries, which is true either way.

## The watchdog defect, and the test that looked right but could not see it (2026-09-02, Appendices BY/CA)

**The scheduled daily-audit found a CRIT in firmware this bin had just called
"verified on the board".** `loop()` sampled `millis()` at the top, burned ~2 ms
in the pack guard's 16 `analogRead`s, then handed `handleFrame()` a SECOND,
later `millis()` which became `lastFrameMs`. The watchdog then subtracted the
fresher stamp from the stale sample — unsigned — and wrapped past 150 ms on
every iteration that handled a good frame. **"SELFTEST 39/39, host_test 11/11"
was true and was not evidence for this path**: SELFTEST tests `outputModeFor()`
as a pure function, never the loop's clock handling, and host_test read `seq`.

**The obvious test is blind, and that is the lesson.** The audit suggested
asserting `ST_WATCHDOG` stays clear on healthy frames. Implemented, run on the
unfixed build: **it passed** (`[False, False, False, False]`). The reply is
sent from *inside* `handleFrame`, *before* the same iteration's watchdog block,
and the previous iteration had already cleared the bit — so the false trip
lives only in the ~2 ms after each reply and can never reach a status byte.
What the trip *does* do is clear `armed`, and nothing re-arms until the next
frame 50 ms later. The observable is therefore **`armed` probed via `?` inside
the 150 ms window after an ARMED frame**: `armed=0` on the broken build,
`armed=1` after the one-line fix (pass the loop-scope `now`). Red, then green,
on the board — both runs pasted in Appendix CA.

**Generalisation, added to the rules above:** when a defect's effect is on
state the reply is built *before*, test the state, not the reply. And a bit
that was visible in the script's own printed output (`status=0x33` in the
very first run, bit 1 set) went unread for hours because the assertion next to
it was about a different bit. **Read the whole status line, not the bit the
assertion names.**
