# Handoff

**Last updated: 2026-09-01 ~16:12 CDT** — this file is the ONLY live snapshot.
History lives in `docs/Project Record — Full Chronological History.md`
(append-only, 51 appendices A–AY). When this file and the record disagree about
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
| 2 | ~~Commit or discard the uncommitted AL audit fixes~~ **DONE 2026-09-01** (AO/AP, commit `3f58804`). The central fix was WRONG and broke `train_cte_probe.py`; repaired and every runnable reader re-run. | — |
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
standard module is ~40° off. BOM row 2 HOLD is lifted.

**Camera POSE, 2026-09-01 (Appendix AR) — pitch measured, height still open.**
The FOV sweep method **does not extend to the extrinsics**: `send_cam_config`'s
contract is "set any field to Zero to get the default camera setting", and for
`offset_x/y/z` / `rot_x/y/z` **0.0 means "keep the default"**, so no sweep can
reproduce a default it cannot express. Measured geometrically instead
(`ml/diag_camera_pose.py`):

- **`fov` is the VERTICAL FOV — measured, not assumed.** Changing only `img_h`
  at fixed pose moved the horizon offset by **1.346** (2nd reference 1.271) vs
  1.3333 predicted for vertical and 1.0000 for horizontal. So **f = 60 px** at
  120×160, and AI's 106° H / 118° D — the basis of the camera purchase — is
  now confirmed rather than assumed.
- **Pitch = 16.3° DOWN.** Horizon at row **41.97 of 120**, sd 0.284 px,
  n=3,187 (`generated-roads`; `generated-track` is tree-lined, no horizon).
- **Height NOT identified, no number reported.** The cte-regression method is
  right (f cancels) but fails on this corpus — the yellow line runs off the
  left edge at close rows, `cte` spans only ±0.17 m, and the PID couples
  heading to `cte`. Needs a purpose-built lateral-sweep run.
- **`offset_z` is not identifiable at all** from a ground plane; **`offset_x`**
  is not separable from the road's own geometry.
- **Mount target:** match the observable, not the angle — mount so the true
  horizon lands on **row 42 of a 120-row frame (35% down)** at 90° vertical
  FOV. Spirit level plus one test photo.

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
`3dstreet-mcp` server (project scope). ~~**The `claude` CLI is not on PATH
here**, so `claude mcp add` must be run by Evan.~~ **CLI INSTALLED 2026-09-01**
(`~/.local/bin/claude.exe`, 2.1.258, OAuth; still no `ANTHROPIC_API_KEY`).

**The 3dstreet blocker was never the CLI, and never the browser tab.**
`claude mcp list` reports:

> `3dstreet: npx -y 3dstreet-mcp - ⏸ Pending approval (run `claude` to approve)`

A **project-scoped** `.mcp.json` server requires Evan's explicit approval on
first load, which is why the server was absent from the session's tool list
entirely rather than failing — and why pairing the 3dstreet browser tab changed
nothing on its own.

**STATUS 2026-09-01 ~22:20 — approved and paired; the NEXT session gets the
tools.** Evan approved it (`claude mcp list` → `3dstreet: npx -y 3dstreet-mcp -
✔ Connected`) and paired the tab. The session that made those changes still saw
zero `mcp__3dstreet__*` tools after three checks, because **a session's MCP
registry is fixed at startup**. Nothing is broken; it just needs a fresh
session with the tab left open.

**THREE conditions, all now met except the restart:** server approved (done) ·
browser tab paired at `https://3dstreet.app/#mcp`, kept open in the background
(done) · session started AFTER the approval (**pending**).

**What to actually use it for — do not re-litigate this.** 3DStreet cannot draw
this track: cross-section tool, no curved streets, real-world units (a real
lane is 3–3.6 m, this track's is 260 mm). Plan-view geometry stays in
`cad/track_layout_v2.py`. Use the MCP for **markings and a portfolio render**,
which maps onto real open work:
- dash ratio — MUTCD's 1:3 does not survive at this scale; ~2:1 is the
  documented deviation (`gotchas.md`)
- the hybrid print plan's **6.28 m of corner arcs and 9.36 m of intersection
  boxes** (Appendix AX), which become ~79 printed tiles
- stop-sign placement — must stay **relocatable** (Appendix Y.3), since a fixed
  sign is predictable from position and defeats the M4 showcase

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

> **⚠️ CORNER GEOMETRY IS FROZEN until the T2 turning test.**
>
> *(Naming collision, flagged 2026-09-01: "B3" is used across ~10 record
> appendices to mean the TURNING TEST, which is PRD **T2** and needs the whole
> rolling chassis (M1.7). But `PRD_ROADMAP.md` §6b's own B-lane maps **B3 =
> task 4, measure donor geometry**, which needs only calipers and is doable
> today. Two different tasks with wildly different prerequisites. Say **T2**
> when the turning test is meant.)* The ~330 mm
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
| BOM | M2.8 | **BLOCKED-ON-EVAN; re-priced twice** | `docs/BOM.md`, **≈$232-249 + $15-25 shipping**. Rows 17-20 (PCA9685, LEDs, resistors, I2C wire) added 2026-09-01 |
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
| Track layout | M1.4 | **v1 + v2 drawn, NOT committed** | 2026-09-01, Appendices AM/AT/AX/AY. `cad/track_layout_v1.py` = figure-8 with a flat causeway bridge + 5 landmarks; `cad/track_layout_v2.py` = 3x3 city grid, 9 intersections, figure-8 route through the centre, 8.31 m, 140 mm spare at R=500. Both parametric and self-checking. **Corner geometry FROZEN until the T2 turning test** |
| Track: sim rehearsal | — | **IMPOSSIBLE, settled** | 2026-09-01, Appendix AX. gym-donkeycar's protocol has ten message types and none defines a road; `load_scene` picks from 11 prebuilt Unity scenes. A custom track needs a Unity build. Costs little: M3 trains on real laps, not the sim corpus |
| Track surface | T3 | **Decided: hybrid** | 2026-09-01, Appendix AX. NOT 225 printed panels (~12.6 kg, 169-900 h, 225 bed clears, 28 camera-visible seams). Print the 6.28 m of corner arcs + 9.36 m of intersection boxes as ~79 tiles (~970 g); tape the 31.9 m of straight street lines |
| Vehicle lighting | — | **Spec written, nothing wired** | 2026-09-01, Appendix AY. `docs/LIGHTING_SPEC.md`. Headlights/tail/DRL/indicators. Only the headlight beam is in the camera's view. Settles the PCA9685. Turn signals are a THIRD policy head and gate the M3 collection run via PRD task 11b |
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
- Budget: ~~SETTLED at ≈$178-181 + shipping, inside the ~$200 ceiling~~
  **NOT settled and the ceiling is breached on EVERY path (2026-09-01).**
  Re-priced 2026-08-08 to $221.82-$224.82; rows 17-20 (lighting + I2C, Appendix
  AY) take it to **$232-249 before shipping, ≈$247-274 with**. The 2GB Pi swap
  no longer restores the ceiling either — it lands at **≈$202-229 with
  shipping**. Evan decides whether the ceiling moves or the lighting waits.
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
  exit non-zero on failure. **P2 re-verified PASS 2026-09-01** (102,888
  frames, 88/88 on both axes) — first run since 2026-08-06.
  `diag_camera_pose.py` measures the sim's camera pitch from the corpus.


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
- ~~**PWM path: straight-to-GPIO or a PCA9685 breakout?**~~ **RESOLVED 2026-09-01 (Appendix AY): PCA9685**, carrying motor PWM + servo + 4 light channels, 6 of 16 used. Lighting made the channel count decide what Appendix AH had already argued on portability grounds. BOM row 17.
- ~~M1.1 decision gate~~ — **answered 2026-07-23** (see Current state).
- ~~M1.1b drive-motor purchase — research in flight~~ — **resolved
  2026-07-23**; the motor is in the BOM below.
- **THE ORDER (`docs/BOM.md`, ≈$232-249 + shipping).** Nothing is bought.
  Everything downstream of M1.5 waits on parts. Before ordering Evan should
  check the **five** items in the BOM's "Verify before ordering" section — most
  importantly that his power bank's label reads **5V/3A**, and now also **which
  LEDs** (item 5), whose forward voltage sets every series-resistor value.
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
