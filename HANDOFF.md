# Handoff

## Goal

Build a mini autonomous car — Lego Technic differential/steering/wheels in a
3D-printed frame, Pi 5 + wide mono camera — that drives teleop, then drives
autonomously via behavioral cloning trained on Evan's own demonstrations,
then (capstone) runs a policy improved by a world model trained offline on
the car's own logged real driving. The process is the product: every stage
verified on the physical car and documented as a college-portfolio
engineering artifact.

## Current state — BOM final + SIM-POC track added; waiting on Evan's order, coupon print, and SIM-POC go

**Last updated: 2026-08-05** — this file is the only live snapshot; history
lives in the record.

> **2026-08-05 — SIM-POC added (record Appendix J).** Evan asked to train in
> sim first as a proof of concept — yes, as a POC of the M4 PIPELINE, not of
> transfer (scope guard intact; the sim policy is never the car's policy).
> PRD tasks P1-P5: Py3.11 venv → sim corpus → V+M+C → DreamerV3-S with the
> measured 8GB boundary → in-sim eval. **Coupon-print and order status
> after 2026-07-23 are unknown to the docs — Evan asked to report.**

> **2026-07-23 — Research brief + PRD written, then M1.1 gate answered
> (record Phase 0, Appendix A-C).** Four-worker research settled the stack:
> Pi 5 8GB + Camera Module 3 Wide + TB6612FNG + MG90S + 2S LiPo/UBEC;
> DonkeyCar plumbing + custom PyTorch. Evan RATIFIED the amended staging
> (sim-RL demoted to optional M5; offline world model on the car's own logs
> is the M4 capstone).
>
> **2026-07-23 ~20:46 — all six research workers complete; BOM final.**
> Evan chose **Pi 5 4GB** (down from 8GB) and **owns a USB power bank**, so
> the build lands at **≈$176-179 + shipping**, inside the $200 ceiling.
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
| BOM | M2.8 | **Final; BLOCKED-ON-EVAN** | `docs/BOM.md`, ≈$176-179 + shipping |
| Chassis CAD + print | M1 | **Started** | M1.3 coupon generated + validated 2026-07-23; awaiting Evan's print + measurements |
| Tolerance coupon | M1.3 | **Ready to print** | `cad/tolerance_coupon_v1.stl` + `cad/README.md`; gates every chassis dimension |
| Electronics + teleop | M2 | **Not started** | purchase list is task 8 |
| Behavioral cloning | M3 | **Not started** | |
| M4 architecture gate | M4.16a | **Done** | 2026-07-23: feasible w/ constraints; docs/research/2026-07-23_world-model-8gb-vram.md |
| Offline world model | M4 | **Not started** | tasks 16-20 now concrete (two architectures, one dataset) |
| Sim-RL (optional) | M5 | **Not started** | never blocks M4 |
| SIM-POC (M4 pipeline in sim) | P1-P5 | **Added 2026-08-05** | proves the pipeline + measures the 8GB boundary before hardware; P1 needs Evan's go (~236 MB sim download) |

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
- Budget: **SETTLED at ≈$176-179 + shipping**, inside the ~$200 ceiling
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
- `.claude/codebase-memory/` — bins (mostly stubs until code exists).
  `gotchas.md` is the dense one — read it before any hardware or M4 work.
- `.claude/pm-cadence.json` — record entry every 3 prompts; handoff at
  session end.

## BLOCKED-ON-EVAN
- ~~M1.1 decision gate~~ — **answered 2026-07-23** (see Current state).
- ~~M1.1b drive-motor purchase — research in flight~~ — **resolved
  2026-07-23**; the motor is in the BOM below.
- **THE ORDER (`docs/BOM.md`, ≈$176-179).** Nothing is bought. Everything
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
- **Open question for Evan:** does "no Lego motors" mean none at all, or
  none of the PF/Powered-Up families? EV3/NXT/9V-Technic motors, if owned,
  would reopen the free-encoder odometry path. Confirm at M1.2 inventory.
