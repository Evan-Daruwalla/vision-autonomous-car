# Handoff

**Last updated: 2026-09-01 ~15:12 CDT** — this file is the ONLY live snapshot.
History lives in `docs/Project Record — Full Chronological History.md`
(append-only, 39 appendices A–AM). When this file and the record disagree about
a historical fact, **the record wins**.

## Goal

Build a mini autonomous car — Lego Technic differential/steering/wheels in a
3D-printed frame, Pi 5 + wide mono camera — that drives teleop, then drives
autonomously via behavioral cloning trained on Evan's own demonstrations, then
(capstone) runs a policy improved by a world model trained offline on the car's
own logged real driving. **The process is the product:** every stage verified on
the physical car and documented as a college-portfolio engineering artifact.

---

## Where the project actually is

**The software lane is four milestones ahead of the hardware lane, and the
hardware lane has not started.** SIM-POC (P1–P5) is built and its findings are
banked. **Nothing has been printed and nothing has been ordered since
2026-07-23.**

The sim work ended in a **well-instrumented negative**: no learned policy
drives reliably, across five separate attempts to make one. That is a
defensible portfolio result — the cause is understood down to the simulator's
track generator — but it is a negative, and the write-up must say so.

### The four things a fresh session must not rediscover

1. **`donkey-generated-track-v0` REGENERATES the track on every launch**
   (Appendix AI). This caused a 4.4× launch-to-launch swing that three
   appendices failed to explain. **Never compare closed-loop numbers across
   launches.** Use `ml/eval_paired.py`, which runs every arm inside ONE launch
   and differences within-launch.
2. **No intervention improves closed-loop driving** (Appendix AJ, the first
   *valid* comparison in the project). Recovery data, DART relabelling,
   recovery loss weighting, and removing the history input have all failed. The
   most consistent signal is that recovery data mildly *hurts*.
3. **The project's trustworthy results are the open-loop ones** — the aux head
   (probe AUC 0.673 → 1.000), the `h`-dependence measurement (skill −0.120),
   the copycat refutation (18.2×), the cone probe, the 57% readout improvement.
   Everything that touched the simulator's closed loop is noisier than it looks.
4. **Held-out MSE ranks policies backwards here.** The best-driving arm had the
   worst val MSE by 16×. Do not select controllers on open-loop loss.

### Two defects that will bite the physical build

- **`donkeycar[pi]` installs `RPi.GPIO`, which does not work on the Pi 5** (RP1
  southbridge; fails with `Cannot determine SOC peripheral base address`). Use
  **`rpi-lgpio`**, a drop-in. This is a defect in the *current* plan, not a
  board comparison — it would surface as a mystery bench failure otherwise.
- **DonkeyCar's `pins.py` has only three PWM backends** (RPI_GPIO, PCA9685,
  PIGPIO). The BOM wires the servo and TB6612FNG **straight to GPIO**, which
  locks the project to a Pi. A **PCA9685 breakout** would make actuation
  board-agnostic. Decide before ordering. (Appendix AH.)

---

## Immediate next actions

| # | Action | Blocked on |
|---|---|---|
| 1 | **Give the floor-space number.** "More floor space" was chosen 2026-08-12 but never quantified. Every track dimension scales off it. | **Evan** |
| 2 | **Commit or discard the uncommitted AL audit fixes** — 19 files, 299 insertions, in the working tree. They compile and `splits.py` self-checks PASS, but **nothing was re-run end-to-end**. | review |
| 3 | **Print the tolerance coupon (M1.3).** Needs no parts — only the printer and Lego. Gates every chassis dimension. | **Evan** |
| 4 | **Pi 2GB ($65) vs 4GB ($110).** Purchase window is now; the 4GB has taken every DRAM hike and the 2GB none. | **Evan** |
| 5 | **Place the order** (`docs/BOM.md`). Nothing downstream of M1.5 moves until parts exist. | **Evan** |

---

## Physical build — decisions made, spec written

**`docs/SIM_TRANSFER_SPEC.md` is the contract the real car must meet** for any
of the sim work to transfer. Measured, not guessed: **20.00 Hz control loop**,
**1.401 m/s mean speed** (7.0 cm per control step), **120×160 → 64×64
anisotropic squash**, expert holds **|cte| 0.317 m** and **saturates steering at
the p95**.

**Evan decided 2026-08-12:** buy the encoder motor (#5159, +$6) · take **more
floor space** rather than compress to ~1:20 · research Pi alternatives before a
**~September** purchase.

**Camera resolved (Appendix AI):** the sim's camera was never configured, so
the whole corpus was captured at an unrecorded Unity default. Identified by
comparison as **`fov=90`** → ~106° H / ~118° diagonal. **The Camera Module 3
Wide (102° H / 120° D) matches within 2–4° and is the correct part**; the
standard module is ~40° off. BOM row 2 HOLD is lifted. Camera height, pitch and
offset remain unidentified — same method would find them.

**Compute:** recommend the **Pi 5 2GB at $65**, not the 4GB at $110 — identical
silicon, and DonkeyCar's "4GB minimum" is an unjustified recommendation (its
`pi` extra installs tflite-runtime, not TensorFlow; a 512 MB Zero 2 W already
drives autonomously). Full brief:
`docs/research/2026-08-12_onboard-compute-selection.md`. Whole-landscape
follow-up (BeagleY-AI, x86, phone, off-board WiFi):
`docs/research/2026-08-12_pi5-alternatives.md`. **Evan's call.**

---

## Track layout — IN PROGRESS, and the geometry is frozen

Evan is designing the street layout in **3dstreet.app**; `.mcp.json` wires the
`3dstreet-mcp` server (project scope, loads on restart). **The `claude` CLI is
not on PATH here**, so `claude mcp add` must be run by Evan.

**Fit caveat (Appendix AM):** 3DStreet is a street *cross-section* tool —
linear segments plus 90° / T / dead-end intersections, **no curved streets
found**, and real-world units (a real lane is 3–3.6 m; this track's is ~0.3 m).
It is good for **marking design, dash patterns, sign placement and a portfolio
render**. It is not a plan-view track-geometry tool, and the figure-8 is
plan-view geometry. Keep the layout itself in a dimensioned plan.

| constraint | value | source |
|---|---|---|
| floor space | **3.0 × 3.0 m — CONFIRMED by Evan 2026-09-01** (9 m², vs 4.48 m² for the old 1.6×2.8 plan) | Evan |
| lane width | **2.0 x the MEASURED car width** (200 mm @ 100 mm car, 260 mm @ 130 mm). Corrected 2026-09-01 — the old fixed-85 mm rule gave 2.31-2.70x, wider than real roads (1.98x) or Duckietown (1.4-1.6x) | `SIM_TRANSFER_SPEC` §3 |
| corner radius | **≥500–670 mm centreline** — *estimate on an estimate* | Appendix L |
| layout | **figure-8**, never an oval | `gotchas.md` |
| stop sign | **relocatable/removable** — a fixed sign is predictable from position | Appendix Y.3 |
| surface | print **MARKINGS**, not road (~0.15 kg vs ~6.4 kg) | `gotchas.md` |
| dashes | MUTCD 1:3 does not survive at scale; ~2:1, a documented deviation | Appendix L |

> **⚠️ CORNER GEOMETRY IS FROZEN until the B3 turning test.** The ~330 mm
> minimum turn radius is `wheelbase / tan(max steer)` on an **unmeasured**
> 130 mm car width. Appendix L already ruled that corner tiles must not be cut
> until an empirical turning test on the rolling chassis. Designing the *look*
> now is fine; committing corner geometry now risks a track the car cannot
> drive.

*(Superseded: the earlier "1.6 × 2.8 m, 1:14, lane 261 mm" spec assumed the
original floor and the pre-2026-08-12 scale decision.)*

---

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
| Harness trustworthiness | P6 | **DONE 2026-08-13** | Appendix AI/AJ. Cause found: `donkey-generated-track-v0` REGENERATES per launch, which is the 4.4x swing. Fix is the PAIRED design (`ml/eval_paired.py`), not a fixed track — every fixed track is far OOD and the controllers collapse to 13-67 steps there. Result: **no arm beats the baseline** |
| Track layout | M1.4 | **In progress** | 2026-09-01, Appendix AM. Evan designing in 3dstreet.app; `.mcp.json` wires `3dstreet-mcp`. **Corner geometry FROZEN until the B3 turning test**; floor-space number still needed from Evan |
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


## BLOCKED-ON-EVAN
- ~~**HOW MUCH FLOOR SPACE?**~~ **ANSWERED 2026-09-01: 3.0 × 3.0 m.**
  Comfortable — it fits the FULL estimated corner-radius range
  (500–670 mm) at either car width. A 130 mm car at 300 mm lanes gives
  a figure-8 bbox of 1.30 × 2.30 m (R=500) to 1.64 × 2.98 m (R=670).
- **Car width: measure, don't choose.** Evan asked about ~100 mm.
  Space does not require it — 3×3 m fits either. It would buy ~18% more
  clearance per side (100 mm vs 85 mm at a 300 mm lane), which targets
  the measured off-centre perception failure. **But width is set by the
  Lego steering rack and diff, fixed parts nobody has measured**, and
  the existing 130 mm is itself an estimate (Appendix L, unmeasured
  until B2/B3). Measure the assembled rack + diff at M1.2/B2 and let
  the car land where it lands; set lane width for ≥85 mm/side from the
  MEASURED width. Note a smaller car also lowers the camera, and the
  sim's camera height/pitch are still unidentified (AI.3).
- **Pi 5 2GB ($65) or 4GB ($110)?** Recommended 2GB — identical silicon, and the 4GB has absorbed every DRAM price rise while the 2GB has absorbed none. Purchase window is now.
- **PWM path: straight-to-GPIO or a PCA9685 breakout?** Straight-to-GPIO (as the BOM wires it) locks the project to a Pi. Decide before ordering.
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
