# Handoff

## Goal

Build a mini autonomous car — Lego Technic differential/steering/wheels in a
3D-printed frame, Pi 5 + wide mono camera — that drives teleop, then drives
autonomously via behavioral cloning trained on Evan's own demonstrations,
then (capstone) runs a policy improved by a world model trained offline on
the car's own logged real driving. The process is the product: every stage
verified on the physical car and documented as a college-portfolio
engineering artifact.

## Current state — SIM-POC P1–P5 built but its closed-loop NUMBERS are uncertified (P6 open); stop-sign decision made and validated; still waiting on Evan's order and coupon print

**Last updated: 2026-08-12 ~12:34 CDT** — this file is the only live snapshot;
history lives in the record.

> **2026-08-10 (Appendices Y, Z) — read these four before touching the ML
> stack:**
>
> 1. **The M4 stop-sign decision is MADE and VALIDATED IN SIM.** Evan chose an
>    auxiliary detection head + an oversized printed sign (PRD 6(b), resolved
>    in place). Measured: an aux head at loss weight 100 puts a
>    sub-1%-of-frame object into the z=32 latent at **essentially zero
>    reconstruction cost** (probe AUC 0.673 → 1.000, val rec 60.88 → 60.48).
>    **Weight matters enormously** — at weight 10 (~4% of loss) it buys
>    nothing.
> 2. **NEW HARD REQUIREMENT: the printed sign must be RELOCATABLE.** On a
>    fixed track a sign at a fixed place is perfectly predicted by "where am
>    I", so a policy can pass the whole showcase while blind to the sign. This
>    is measured, not stylistic: a cone probe scored **AUC 0.997 and collapsed
>    to nothing when the cone was painted out** — it was reading track
>    position. Never measure small-object perception on a fixed-position
>    object.
> 3. **The closed-loop recovery test came back NEGATIVE.** Recovery data cut
>    off-centre *probe* error 57% (Appendix X) but does **not** make the car
>    drive further: 187.2 → 199.9 steps, error bars overlapping, **0/9
>    survived in every arm**. The obvious escape hatch — that recovery frames
>    were drowned out at 6.67% of a mean objective — was tested with a
>    `--recovery-weight` sweep and **closed** (Appendix AA): pushing them to
>    **78.9% of the objective changes survival not at all** (172.6–221.0
>    steps across the sweep, per-seed sd 27–81, every spread covering every
>    other mean, 0/9 everywhere). The weighting was not a no-op — unweighted
>    val MSE degrades 0.00177 → 0.00331 and lane error rises to 1.029 — so a
>    genuinely different policy was learned; it just does not drive better.
>    **…and Appendix AB found why: the controller was barely reading `z` at
>    all.** Zeroing the MDN-RNN hidden state at serve time makes it worse than
>    predicting the mean (skill −0.120), so it rode almost entirely on `h` —
>    which is teacher-forced on logged expert actions in training but built
>    from the policy's own actions in closed loop, and therefore drifts.
>    ~~**Remove `h` AND add recovery data and the car finally drives: 342.4
>    steps, 3/9 episodes COMPLETED.**~~ **RETRACTED 2026-08-11 — DID NOT
>    REPLICATE.** Ten seeds across two independent gate-valid batches give
>    **107.2 ± 16.0 steps and 0/20 completions**, with every seed between 85
>    and 147 and episodes within a seed near-identical. The same three
>    checkpoints that scored [78,600,600] / [600,469,448] / [96,96,95] scored
>    [100,113] / [108,108] / [107,107] on re-run. **Treat the 342.4 batch as
>    the anomaly, not these.** **Correction (2026-08-11 ~23:29 CDT): the flat claim "no
>    learned policy has completed an episode" is FALSE and was itself an
>    overcorrection — 3 completions exist in `ev3_nh_aug` and 1 in
>    `ev2_nh_aug`. The true statement is that **no learned policy completes
>    RELIABLY**: pooled over **47** gate-valid `nh_aug` episodes the
>    distribution is bimodal — **30 die under 150 steps, 6 reach 450-601** —
>    with **4 completions**, all from one launch.
>    **The whole 2×2 reverses on re-run** (Appendix AC) — the plain baseline
>    is the best and by far the most stable arm:
>
>    | arm | valid batches | mean | sd |
>    |---|---|---|---|
>    | cl_base (h, original) | 4 | **189.4** | **4.1** |
>    | cl_aug (h, +recovery) | 4 | 189.1 | 35.1 |
>    | nh_base (z-only) | 2 | 109.2 | 0.1 |
>    | nh_aug (z-only, +recovery) | 4 | 170.0 | 115.4 |
>
>    **No intervention tried on 2026-08-10/11 improves closed-loop driving.**
>    Recovery data does nothing (189.4 → 189.1); removing `h` actively hurts.
> 4. **THE HARNESS NOISE FLOOR IS MEASURED, AND IT INVALIDATES THE PRECISION
>    OF EVERY CLOSED-LOOP COMPARISON IN THIS PROJECT (Appendix AD).** Same
>    checkpoint, same seed, **7 gate-valid launches: 106.5 / 118.5 / 179.5 /
>    205.5 / 232.0 / 353.5 / 471.5 — mean 238.1, sd 131.6, CV 55%, a 4.4×
>    spread.** Episodes *within* a launch agree to a few steps; launches do
>    not. **The launch is the unit of variation.**
>
>    At CV 55%, launches needed per arm at 80% power: ~5 for a 2× effect, ~19
>    for 50%, ~120 for 20% — **but quote these with their interval or not at
>    all** (Appendix AE): CV is estimated from n=7, 95% CI [0.36, 1.22], so
>    those are really **2–23 / 8–93 / 50–581**. Use them to choose between "a
>    handful" and "a hundred", never to certify "we ran 5, therefore powered".
>    Two things matter more than sample size: **the outcome is right-censored**
>    at 600 steps, so report a completion RATE and MEDIAN, not a mean; and
>    **pairing the design** (all arms inside each launch, differenced
>    within-launch) cancels the launch effect and is likely worth an order of
>    magnitude. Every comparison in Appendices Z,
>    AA, AB and AC used **n = 1**. So this harness could only ever have
>    resolved ~3× differences, and the 7–28% differences those entries
>    discuss were never measurable. **Z.3 and AA's nulls are not "no effect" —
>    they are "no measurement".** The one comparison that may survive is
>    nh_base 109.2 vs cl_base 189.4 (1.7×, and nh_base is the most stable arm
>    seen) — suggestive, still under the resolution bar.
>
>    Eliminated as causes, each by measurement: control rate, track identity,
>    and **episode start state** (`ml/diag_reset.py` — post-RESET POSITION is
>    near-deterministic: z identical across all 16 episodes of two launches, x
>    identical for 14 of 16. NOT "deterministic to four decimals" — post-warmup
>    cte spans 0.0018-0.0075, ~0.6% of the ~0.87 cte the car operates at, far
>    too small to explain a 4.4× swing. Refutes the leading hypothesis in AC).
>    Cause unknown; remaining suspects are inside the Unity process.
>
>    **Consequence: do not rank policies on closed-loop steps until PRD P6 is
>    done.** The project's trustworthy results are precisely the ones that
>    never touched the sim (aux head, `h`-dependence, copycat refutation, cone
>    probe, the 57% readout finding) — worth remembering for M3/M4, where the
>    sim becomes a physical car and this noise gets worse, not better.
> 5. **Held-out MSE ranks these arms almost exactly backwards.** The
>    best-driving policy has the WORST val MSE by 16× (0.02846 vs 0.00177).
>    Do not select controllers on open-loop loss in this project.
> 6. **`eval_in_sim.py` step counts are NOT comparable across runs** unless
>    the reported `control_hz` agrees. The same checkpoint scored 69.3 steps
>    at 13.2 Hz and 187.2 at 16.7 Hz. **The banked P5 headline of 69.3
>    understates that controller by 2.7×.** Do NOT use `--control-hz` to
>    equalise arms — throttling by sleeping desynchronises the loop from the
>    sim and is a cliff (the expert dies at a 2% throttle). Run arms
>    back-to-back unthrottled and check the rate matched.
>
> **Also new:** a full research brief on AI methods
> (`docs/research/2026-08-10_ai-methods-for-the-autonomy-stack.md`). Headline:
> **do not build offline RL on this corpus** (H3 dies — the closest published
> match reports BC 91.5 vs offline DreamerV2 4.8). And an untested rival
> explanation for the P5 wall: **copycat agents** — a BC policy given
> observation histories learns to predict the previous expert action, with
> held-out loss improving while closed-loop reward drops. This controller
> consumes the MDN-RNN hidden state and shows exactly that signature. One
> training run tests it (`z` alone, `h` zeroed).

> **2026-08-07 — SIM-POC IS COMPLETE, P1 through P5 (Appendices R, S, T, U,
> V).** A 102,888-frame corpus verified 88/88 on both alignment axes; a Ha &
> Schmidhuber world model beating a frozen-frame baseline 30/30 in-domain;
> DreamerV3-S trained offline with the 8 GB boundary measured; and a full
> policy-extraction pass.
>
> **P5 is an honest negative and should be read as one.** Latent BC (linear
> and MLP) and CEM planning were each evaluated over 3 seeds × 3 episodes:
> **no learned policy completed an episode; the PID expert completed 9/9.**
> The diagnostic is the valuable part — the paper's linear controller is
> structurally wrong for this task (z encodes cross-track error nonlinearly:
> probe R² 0.27 linear vs 0.97 MLP), and the bottleneck is the learned
> representation, not the controller. Corner speed was tested and ruled out.
>
> **A cold audit (2026-08-06, Appendix V.1) found four gates that could not
> fail** — including one where the README's advertised "Reproduce with"
> command would republish committed numbers as fresh measurements on any
> clone without a GPU. All fixed, each verified by being made to fail.
>
> **2026-08-08 — the wall is diagnosed, and it changes what M3 must collect
> (Appendix W).** The 69-110 step failure is **perception going out of
> distribution**: probe error is a function of POSITION (corr 0.894 learned,
> 0.852 expert — the same curve under both), because the collector rejects
> episodes with `mean|cte| > 1.2` so the corpus has no off-centre frames.
> **No controller change fixes it.** M3 needs a SEPARATE off-centre recovery
> set exempt from the quality filter, or the same wall appears on hardware.
>
> **NEW RISK, needs Evan's decision:** both the ConvVAE *and* DreamerV3 erase
> small objects — **0 of 899 cone pixels survive in either**. The M4
> stop-sign showcase assumed the sign reaches the latent. A bigger world model
> is not the fix; the options are higher input resolution, an auxiliary
> detection head, or a different showcase task.
>
> Software is now five SIM-POC tasks ahead of hardware: **nothing has been
> printed and nothing ordered since 2026-07-23**, and the two decisions below
> still block all physical progress.

> **2026-08-05 ~23:10 — DEADLINE MOVED (Appendix N).** **The hard deadline
> is now REGULAR DECISION, ~Jan 1-15 2027** (~5 months); Nov 1 2026 is now a
> SOFT milestone — whatever is done by then strengthens the EA application,
> the rest lands as an RD update. The Appendix K schedule already assumed
> Nov 1 needed only SIM-POC + M3, so nothing has to be cut and **M4 moves
> from stretch to comfortably in scope.** This is 1 of 5 concurrent
> portfolio projects (~2-3 sittings/week here). PRD §6b holds the schedule.
>
> **A SCOPE EXPANSION IS UNDER EVALUATION, NOT ADOPTED:** destinations,
> parking, and routing on a bigger grid. Two blockers before it enters the
> PRD — (1) end-to-end BC likely **cannot route** (identical intersection
> images, different destinations ⇒ needs goal-conditioning, an architecture
> change to every model in the plan); (2) **a 4-intersection grid does not
> fit 1.6 m at 1:14** (needs ~2.04 m; a single intersection needs 1.52 m and
> does fit). Research in flight. **Live BOM consequence: the encoder motor
> (#5159, +$6) is decidable now at zero cost and expensive after ordering.** **Nothing printed and nothing ordered as of 2026-08-05** — those
> are Evan's two actions this week.
>
> **2026-08-05 ~23:10 — track design settled + P2 code done (Appendices L,
> M).** Track: **print MARKINGS, not the road surface** (97% less filament
> for identical camera input), **figure-8 not an oval** (an oval teaches
> "always steer left"), 1:14 scale in the confirmed 1.6 × 2.8 m space,
> MUTCD-verified markings. **A stop sign is provably unlearnable by plain
> BC** — that makes it the M4 world-model showcase, not an M3 feature.
> P2's expert driver was tuned by measurement (throttle, not gains, was the
> binding constraint) and its alignment gate is an exact algebraic identity
> after the first pixel-based gate proved to be a false alarm on good data.
>
> **Per-task commits are authorized** (plan approval, 2026-08-05). Push
> still requires Evan's explicit say-so.

> **2026-07-23 — Research brief + PRD written, then M1.1 gate answered
> (record Phase 0, Appendix A-C).** Four-worker research settled the stack:
> Pi 5 8GB + Camera Module 3 Wide + TB6612FNG + MG90S + 2S LiPo/UBEC;
> DonkeyCar plumbing + custom PyTorch. Evan RATIFIED the amended staging
> (sim-RL demoted to optional M5; offline world model on the car's own logs
> is the M4 capstone).
>
> **2026-07-23 ~20:46 — all six research workers complete; BOM final.**
> Evan chose **Pi 5 4GB** (down from 8GB) and **owns a USB power bank**, so
> the build lands at **≈$178-181 + shipping**, inside the $200 ceiling.
> `docs/BOM.md` is the order list. **Nothing is bought yet.**
>
> **Three claims were overturned during research and are recorded as dated
> corrections** (Appendices E, F, G) — a future session must not
> reintroduce them: the "~24GB VRAM for DreamerV3" figure is **retracted**
> (unlocatable source); the printed motor coupler is the **lowest**-torque
> joint, not the highest; and the **Pi 5 does not need 5V/5A** for this
> workload (that rating is a USB-peripheral budget).

### Workstreams (mapped to PRD milestones)

| Workstream | PRD | Status | Notes |
|---|---|---|---|
| Doc system bootstrap | — | **Done** | 2026-07-23, this session |
| Research brief | — | **Done** | docs/research/2026-07-23_sensor-compute-stack.md, 4 workers, spot-checked |
| Decision gate | M1.1 | **Done** | 2026-07-23: 8GB · no Lego motors · 3060 Ti 8GB · ~$200 · ratified |
| Drive motor selection | M1.1b | **Done (purchase pending)** | 2026-07-23: Pololu #1093 N20 30:1 HP 6V, $23.95; docs/research/2026-07-23_drive-motor-selection.md |
| Power system selection | M1.1c | **Done (purchase pending)** | 2026-07-23: split source, power bank owned; docs/research/2026-07-23_power-system.md |
| BOM | M2.8 | **Final; BLOCKED-ON-EVAN** | `docs/BOM.md`, ≈$178-181 + shipping |
| Chassis CAD + print | M1 | **Started** | M1.3 coupon generated + validated 2026-07-23; awaiting Evan's print + measurements |
| Tolerance coupon | M1.3 | **Ready to print** | `cad/tolerance_coupon_v1.stl` + `cad/README.md`; gates every chassis dimension |
| Electronics + teleop | M2 | **Not started** | purchase list is task 8 |
| Behavioral cloning | M3 | **Not started** | |
| M4 architecture gate | M4.16a | **Done** | 2026-07-23: feasible w/ constraints; docs/research/2026-07-23_world-model-8gb-vram.md |
| Offline world model | M4 | **Not started** | tasks 16-20 now concrete (two architectures, one dataset) |
| Sim-RL (optional) | M5 | **Not started** | never blocks M4 |
| SIM-POC P1 environment | P1 | **Done** | 2026-08-05, commit 83e966b — CUDA True + sim camera frame, `ml/verify_env.py` |
| SIM-POC P2 corpus | P2 | **DONE** | 2026-08-06, Appendix R: **102,888 frames**, 88/88 episodes verified on BOTH axes, split disjoint, PASS. Target met, not redefined. **2 train layouts, not 4** (Appendix Q), unbalanced 51:27 |
| SIM-POC P3 world model | P3 | **DONE** | 2026-08-06, Appendix S: V+M+C trained (VAE 4,348,547 params = exact paper match). 30-step imagination **beats a frozen-frame baseline 30/30 steps in-domain**, 0/30 cross-domain. Done-check PASS. ~6 min total training |
| SIM-POC P4 DreamerV3 | P4 | **DONE** | 2026-08-06, Appendices T+U: **both** halves. Trained 2000 steps (image loss 588.31→61.39, 9.6x) AND the 8GB fitting table measured. **Batch size, not model size, breaks 8GB**: 69.7M params fit at b16 (5.238 GB), 19.1M at b64 does not fit in 7.0 GB. Two task premises proved false — see T.2 |
| SIM-POC P5 policy | P5 | **DONE — but its NUMBERS are uncertified** | 2026-08-07, Appendix V. Latent BC (linear + MLP) **and** CEM planning, 3 seeds × 3 episodes. Key finding (stands, open-loop): the paper's linear C is structurally wrong here — z encodes cross-track error nonlinearly (probe R² 0.27 linear vs 0.97 MLP). **CAVEAT 2026-08-11 (Appendix AD): every step count from this task came from a harness later measured at CV 55%, where n=1 launch resolves only ~3×. The qualitative result holds — the expert completes, learned policies mostly do not — but 69.3/89.7/187.2/110 are not measurements. "No learned policy finished" was also later shown FALSE in the strict sense: completions occur, just not reliably.** |
| **Harness trustworthiness** | **P6** | **OPEN — BLOCKING all closed-loop claims** | 2026-08-11, Appendix AD. Same checkpoint across 7 gate-valid launches: 106.5–471.5 steps, CV 55%. Rate, track and start state ruled out; cause unknown. Nothing may be ranked on closed-loop steps until this is fixed or quantified |
| Track fabrication | T1-T6 | **Designed, not built** | figure-8, 1.6×2.8 m, 1:14, print markings not surface; T2 blocked on measured turning radius |

## Hardware & stack facts (from the 2026-07-23 brief — re-verify prices at purchase)

- Pi 5 **4GB, $70** (chosen 2026-07-23 ~20:46, down from 8GB for budget;
  4GB is DonkeyCar's minimum and the board only ever runs inference).
- Camera Module 3 Wide $35 (120° diagonal, rolling shutter — fine at 1-3 m/s)
  **+ a Standard-Mini camera cable (~$2-5)** — the module ships with a
  Standard-Standard cable that does NOT fit the Pi 5's mini 22-pin port.
- Drive: **Pololu #1093 N20 30:1 HP 6V, $23.95** (chosen 2026-07-23,
  purchase pending). 1000 rpm, 55.9 mN·m stall, 1.6 A stall, 10×12×26 mm,
  3 mm D-shaft. Into the Lego diff via TB6612FNG with **both channels
  paralleled** (2 A cont.) and duty PWM-capped at ~71% of a full 8.4 V pack.
  **All Lego motors were rejected on physics — too slow (≤0.88 m/s).**
  Build HAT rejected (needs 8 V ±10 %, takes the UART, no Trixie support).
  L298N banned. Drivetrain config B: 62.4 mm tire + 12t→28t, 20.0 mm
  centres, 1.28 m/s.
- Steering: MG90S (MG996R fallback; mount takes both).
- Print: calibrate coupons first; ~5.1mm pin / 5.3-5.6mm rotating bore;
  PETG for bores. Real Lego beams as load path where precision matters.
- Software: DonkeyCar 5.3.0 (Pi 5 OK, 64-bit Bookworm, Py 3.11, TF/Keras
  trainer) for plumbing; custom PyTorch models are the portfolio line.
- Training: **RTX 3060 Ti, 8GB VRAM** (16GB "shared" is host-RAM spillover,
  not usable VRAM — and **disable NVIDIA Sysmem Fallback** or an OOM becomes
  a silent ~3× slowdown). Fine for M3. M4 resolved 2026-07-23: **feasible at
  DreamerV3 S-scale (~18M) or below**; the earlier "~24GB needed" figure is
  **RETRACTED** (unlocatable source). Use `NM512/dreamerv3-torch` — the JAX
  reference has no offline mode and no native-Windows CUDA. Build Ha &
  Schmidhuber V+M+C (~4.77M) FIRST as the guaranteed result.
- Power: **SPLIT SOURCE** (chosen 2026-07-23, purchase pending). USB power
  bank → Pi ONLY; 2× 18650 (7.4 V) + USB-C 2S BMS board → TB6612FNG VM and
  → LM2596 @5.2 V → servo; **one shared ground**, star-grounded at the
  driver; inline 3 A fuse + switch on the motor pack. **The Pi 5 does NOT
  need 5 V/5 A** — official docs allow 5 V/3 A with only a 600 mA USB
  peripheral cap, and this build has no USB peripherals (measured CNN draw
  1.40 A). **Never put the Pi and motor on one 5 V/3 A bank** — 4.62 A on a
  3 A rail during a stall resets the Pi.
- **Actuators: TWO — one drive motor + one MG90S steering SERVO.** Steering
  is never a plain DC motor (no position feedback ⇒ no commandable angle;
  see `gotchas.md`).
- Budget: **SETTLED at ≈$178-181 + shipping**, inside the ~$200 ceiling
  (Evan took the 4GB downgrade and owns the power bank, 2026-07-23 ~20:46).
  Shipping across 3-4 vendors could add $15-25 — **consolidate vendors**;
  most small parts are generic. Full list: `docs/BOM.md`.

## Documentation
- `docs/Project Record — Full Chronological History.md` — append-only
  chronological record (Appendix headings + TOC line each entry). No HTML
  twin — don't create one.
- `PRD_ROADMAP.md` — the standing plan. Source of truth for what to build
  and in what order.
- `docs/research/2026-07-23_sensor-compute-stack.md` — evidence base for
  every stack choice; read before challenging a hardware decision. **Carries
  a dated CORRECTION block: its "~24GB VRAM" claim is retracted.**
- `docs/research/2026-07-23_world-model-8gb-vram.md` — M4 feasibility,
  the recommended config, and the fallback ladder. Read before any M4 work.
- `docs/research/2026-07-23_drive-motor-selection.md` — motor choice with
  the full gearing/torque math and CAD dimensions. Read before M1.6.
- `docs/research/2026-07-23_power-system.md` — split-source architecture,
  real Pi 5 current data, runtime/peak math, battery safety. Read before
  M1.1c or any wiring.
- `docs/BOM.md` — the order list, with wiring architecture and the
  pre-order verification checklist.
- `.claude/codebase-memory/` — bins. `gotchas.md` is the dense one — read it
  before any hardware, track, or ML work.
- `ml/` — SIM-POC code. `requirements.txt` rebuilds the environment;
  `verify_env.py` and `verify_corpus.py` are the P1/P2 done-checks and both
  exit non-zero on failure.

## Track (decided 2026-08-05, record Appendix L)
Figure-8 (never an oval — a one-handed loop teaches "always steer left"),
1.6 × 2.8 m, **1:14 scale**: lane 261 mm, line 7.3 mm, stop line 22-44 mm,
dash compressed to ~60/180 mm. **Print MARKINGS, not the road surface** —
full-surface printing is ~6.4 kg and 150-250 h versus ~0.15 kg and ~6 h for
markings, for identical camera input. Substrate is dark matte foam board.
Stop sign goes in from the start but is exercised at M4, because plain BC
provably cannot learn it and the world model can.
- `.claude/pm-cadence.json` — record entry every 3 prompts; handoff at
  session end.

## BLOCKED-ON-EVAN
- ~~M1.1 decision gate~~ — **answered 2026-07-23** (see Current state).
- ~~M1.1b drive-motor purchase — research in flight~~ — **resolved
  2026-07-23**; the motor is in the BOM below.
- **THE ORDER (`docs/BOM.md`, ≈$178-181).** Nothing is bought. Everything
  downstream of M1.5 waits on parts. Before ordering Evan should check the
  four items in the BOM's "Verify before ordering" section — most
  importantly that his power bank's label reads **5V/3A**.
- **PRINT THE COUPON (M1.3)** — needs NO parts, only his printer and Lego.
  `cad/tolerance_coupon_v1.stl`, once in PLA and once in PETG, using the
  settings he intends for the chassis. Every chassis dimension in M1.5–M1.7
  waits on these measurements, so this is the critical path while the order
  ships. Procedure + results table: `cad/README.md`.
- **Which printer?** PrusaSlicer and Bambu Studio are both installed on this
  machine, but the actual printer model and filament stock are uncatalogued
  (M1.2). The coupon's print settings must be recorded with its measurements.
- **Ask dad: soldering iron + solder, multimeter, USB SD reader.** Assumed
  owned 2026-08-05 (calipers confirmed). Any "no" is +$8-40 and counts as
  shop tooling, not car BOM — Evan decides whether the $200 ceiling covers it.
- **A1 pre-order checks** (PRD §6b): power-bank label reads 5V/3A · **count
  the diff ring teeth** (28 = 62821, 24+16 = 6573 — sets the CAD mesh
  centres) · confirm a 12-tooth bevel is in the parts bin · which tires ·
  re-check prices.
- **Open question for Evan:** does "no Lego motors" mean none at all, or
  none of the PF/Powered-Up families? EV3/NXT/9V-Technic motors, if owned,
  would reopen the free-encoder odometry path. Confirm at M1.2 inventory.
