# Autonomous Car Project — Build & AI PRD & Roadmap

**Written 2026-07-23 by Claude (Fable), first session, from the 2026-07-23
research brief. Standing document — the executing model works through TASK
BREAKDOWN top to bottom, one task at a time, and checks off SUCCESS
CRITERIA.**

**HOW TO READ THIS FILE (added 2026-09-02 ~19:31 CDT, Appendix BY):** it has
accreted six weeks of dated amendments under the rule *ADD by appending ·
REMOVE by dated strikethrough · never delete*, so the current state is no
longer readable top to bottom. **`HANDOFF.md` is the live snapshot; this file
is the plan.** A task's most recent dated note is its current status. Where a
term in the original text is now wrong ("PF motor", "LiPo + UBEC",
"1.6 × 2.8 m") it is struck in place with the correction beside it — the
original stays so the reasoning trail survives. `/milestone-track` cannot
parse this file's numbered-prose tasks; **do not trust its percentage here.**

**GOAL:** Build a mini autonomous car — Lego Technic differential, steering
geometry, and wheels in a 3D-printed frame, Pi 5 + wide mono camera onboard —
that (1) drives under human teleop, (2) drives a track autonomously via a
behavioral-cloning CNN trained on Evan's own demonstrations, and (3) as the
capstone, runs a policy improved by a world model trained OFFLINE on the
car's own logged real driving; every stage verified on the physical car and
documented in the record as a college-portfolio engineering artifact.

**SCOPE GUARD (set 2026-07-23, RATIFIED by Evan 2026-07-23 ~17:21 CDT): no
hardware purchase without Evan's explicit go; no online RL training on the
physical car (safety + scope — offline only, per the research brief) unless
a future dated fork says otherwise; no SLAM/LiDAR work (deferred idea, mount
reserved only).**

---

## 1. OBJECTIVE

A working, self-driving mini car and the documented engineering process
behind it. The user is Evan (builder, portfolio) and any executing model.
Staging is deliberate: each milestone is independently demoable, so the
project has portfolio value even if a later stage stalls. The staging was
AMENDED from Evan's original "train world model in sim, then real life" idea
by the 2026-07-23 research: mandatory sim-RL was demoted (documented
F1TENTH/RoboRacer sim2real transfer failures); an offline world model on the
car's own logged data was promoted to the capstone (reuses BC data, no
sim2real gap, no verified hobbyist precedent — stronger story). **RATIFIED
by Evan 2026-07-23 ~17:21 CDT** (M1.1 gate item e).

## 2. CONTEXT

### What exists (verified 2026-07-23)
- Docs only, no code, no git repo, no hardware bought: `HANDOFF.md`,
  `docs/Project Record — Full Chronological History.md`,
  `docs/research/2026-07-23_sensor-compute-stack.md` (the evidence base for
  every stack choice below), `.claude/codebase-memory/` bins, this PRD.
- ~~Evan owns: Lego Technic sets incl. a working differential and a steering
  donor set (specific set/motor inventory NOT yet catalogued — M1.1), a 3D
  printer (model/filament stock not catalogued — M1.2), a desktop PC
  (GPU/VRAM not confirmed — M1.1).~~ (superseded 2026-07-23 ~17:21 CDT by
  the M1.1 gate answers below)
- **Evan owns (confirmed 2026-07-23 ~17:21 CDT, M1.1 gate):** Lego Technic
  sets incl. a working differential and a steering donor set (exact set
  numbers still uncatalogued — M1.2); a 3D printer (model/filament stock
  uncatalogued — M1.2); a desktop PC with an **RTX 3060 Ti, 8GB dedicated
  VRAM** (the "16GB shared" is host-RAM spillover, not usable VRAM).
  **He owns NO Lego motors** — this voids the earlier "reuse an owned PF
  motor" plan and makes the drive motor a purchase decision (M1.1b).
  *Open sub-question: "none" may mean none of the PF/Powered-Up families
  specifically; EV3/NXT/9V-Technic motors, if owned, would reopen the
  encoder path — confirm during M1.2 inventory.*
- **What exists (2026-09-02, Appendix BY) — supersedes "Docs only" above:**
  a git repo (github.com/Evan-Daruwalla/vision-autonomous-car) · `ml/` — 31
  scripts, **SIM-POC P1-P6 complete** (102,888-frame corpus, V+M+C and
  DreamerV3-S trained, the paired eval harness) · `firmware/` — four Uno
  sketches; **`uno_control` runs on the real board** (SELFTEST 39/39,
  `host_test.py` 11/11) · `cad/` — tolerance coupon STL (**unprinted**), track
  layouts v1/v2 (parametric, self-checking, **uncommitted geometry**) ·
  `docs/BOM.md`, `docs/WIRING_PROTOSHIELD.md`, `docs/SIM_TRANSFER_SPEC.md`,
  `docs/LIGHTING_SPEC.md`, `firmware/SERIAL_PROTOCOL.md` · a 77-appendix
  record. **Hardware in hand: an Arduino Uno R3 clone (owned) and a Lego
  rack-and-pinion Evan built and measured. Nothing purchased, nothing printed,
  nothing wired.**

### Must not break
- Record append-only discipline; absolute dates; no invented data.
- Physical honesty: untested prints are "untested"; sim-only or bench-only
  results never claimed as real-car results.
- ~~Budget: target ≈$165-195 total new spend (brief BOM); overshoot needs
  Evan's OK.~~ (revised 2026-07-23 ~17:21 CDT — the old figure assumed a
  free owned motor)
- ~~**Budget: ~$200 ceiling, approved by Evan 2026-07-23 ~17:21 CDT.**
  Committed so far: Pi 5 8GB $95 + Camera Module 3 Wide $35 + TB6612FNG $5
  + MG90S $5 + UBEC ~$8 + 2S LiPo ~$12 + SD card ~$10 + wire/caps/connectors
  ~$8 ≈ **$178**, leaving ~$22 for the drive motor (M1.1b). **Watch item:**
  a 2S LiPo needs a balance charger (~$25) — if Evan doesn't own one, the
  build exceeds $200 and needs his call (confirm in M1.2 inventory).~~
  (revised 2026-07-23 ~17:32 CDT — the watch item resolved badly: Evan owns
  no battery AND no charger, so the battery line was understated)
- **Budget: ~$200 ceiling (Evan, 2026-07-23 ~17:21 CDT). PROJECTED OVER
  CEILING as of 2026-07-23 ~17:32 CDT.** Committed: Pi 5 8GB $95 + Camera
  Module 3 Wide $35 + TB6612FNG $5 + MG90S servo $5 + UBEC ~$8 + SD card
  ~$10 + wire/caps/connectors ~$8 ≈ **$166**. **Drive motor priced
  2026-07-23 ~17:47: Pololu #1093 = $23.95** ⇒ running total **$189.95**.
  Still to price: **complete power system incl. charger (M1.1c, ~$25-40 —
  Evan owns no LiPo and no charger)** ⇒ realistic total **~$215-230**.
- **BUDGET RESOLVED 2026-07-23 ~17:59: the ceiling is breached; a cut is
  required.** The cheapest complete SAFE power system is **$25.89 alone**,
  leaving $0 for the motor. Full-build scenarios (motor $23.95 included):

  | Scenario | Total |
  |---|---|
  | Owns a power bank + **Pi 4GB** | **~$174** — comfortable ⇐ **CHOSEN** |
  | Owns a power bank + Pi 8GB | ~$199 — at the line; shipping breaks it |
  | No power bank + Pi 4GB | ~$194-202 — at the line |
  | No power bank + Pi 8GB | ~$219-227 — over |

- **BUDGET SETTLED 2026-07-23 ~20:46 CDT (Evan):** he **owns a USB power
  bank**, and takes the **Pi 5 8GB → 4GB downgrade** (supersedes the ~17:21
  gate answer (a), on his own instruction). ~~Final BOM ≈ **$176-179 +
  shipping**, inside the $200 ceiling.~~ *(Superseded 2026-09-01: re-priced
  2026-08-08 to $221.82-$224.82, then rows 17-20 (lighting + I/O, Appendix AY)
  took it to $232-249. **Revised again 2026-09-02 (Appendix BC): row 17's
  PCA9685 is superseded by an Arduino Uno Evan already OWNS ($0), giving
  ≈$226-234 + $15-25 shipping = ≈$241-259.** The $200 ceiling is still breached
  on the 4GB Pi; the **2GB path reaches ≈$196-214**, whose low end clears $200.
  Budget is NOT settled; it is Evan's open call.)* Itemised in `docs/BOM.md`. One part
  was missing from every earlier estimate and is now included: a **camera
  cable, Standard-Mini (~$2-5)** — Camera Module 3 ships with a
  Standard-Standard cable that does NOT fit the Pi 5's mini 22-pin
  connector (verified against Raspberry Pi docs 2026-07-23).

  Shipping across 3-4 vendors adds $15-25 unless consolidated. **The Pi 5
  8GB → 4GB downgrade (−$25) is now recommended by the power research
  independently of the earlier argument.** NOT applied — Evan chose 8GB at
  the M1.1 gate; only he revises it. **If the downgrade is refused there is
  no safe power system that fits** — and the gap must NOT be bridged by
  putting the Pi and motor on one bank (see M1.1c).
  Largest identified lever: **Pi 5 8GB → 4GB saves $25** (4GB is DonkeyCar's
  stated minimum and onboard work is inference-only). NOT applied — Evan
  chose 8GB at the gate; only he revises it.

## 3. SUCCESS CRITERIA

- [ ] M1: printed chassis integrates Lego diff + steering; steering sweeps
      lock-to-lock driven by the servo (bench, no wheels-on-ground needed);
      rear axle spins freely through the diff. Evidence: photos + measured
      tolerance table in the record.
- [ ] M2: car drives under teleop for a full battery session without
      brownout; ≥10 laps of camera+control data logged and readable.
- [ ] M3: car completes 3 consecutive autonomous laps of the training track
      with ≤1 human intervention total, on the custom PyTorch model.
      Evidence: video + eval log in the record.
- [ ] M4: a world model trained offline on the car's own logs produces
      (a) recognizable multi-step video/latent predictions of the track and
      (b) a policy that matches or beats the M3 BC model on the same
      3-lap eval. Evidence: prediction rollout video + eval comparison table.
- [ ] Every milestone has a record entry with real measurements/output at
      completion.

## 4. CONSTRAINTS

- ~~Stack (from the 2026-07-23 brief — change requires a dated PRD edit):
  Pi 5 (4GB or 8GB per M1.1) · Camera Module 3 Wide · owned PF L/XL drive
  motor + TB6612FNG · MG90S servo (MG996R fallback; mount takes both) ·
  2S LiPo + 5V/5A-class UBEC into GPIO, split rails, shared ground ·
  DonkeyCar 5.x (64-bit Bookworm, Py 3.11) for plumbing + custom PyTorch
  models · training on Evan's desktop GPU.~~ (amended 2026-07-23 ~17:21 CDT
  — Pi size resolved; owned-PF-motor assumption void, he owns no Lego
  motors)
- **Stack (amended 2026-07-23 ~17:21 CDT):** **Pi 5 8GB ($95, chosen by
  Evan)** · Camera Module 3 Wide · **drive motor TBD — M1.1b, must be
  purchased** + TB6612FNG (or DRV8871 if the chosen motor's stall current
  demands it) · MG90S servo (MG996R fallback; mount takes both) · **power
  system TBD — M1.1c** (the 2S LiPo + 5V UBEC plan assumed equipment Evan
  doesn't own; chemistry, charger and whether the Pi can run off a 5V/3A
  source are all under research as of 2026-07-23 ~17:32 CDT) · DonkeyCar 5.x
  (64-bit Bookworm, Py 3.11) for plumbing + custom PyTorch models ·
  training on **RTX 3060 Ti, 8GB VRAM** — a real constraint on M4, see
  below.
- **Stack (CURRENT, 2026-09-02 — supersedes both stack lines above; each
  item traces to a dated appendix):** Pi 5 — **BOM row 1 says 4GB ($110),
  the 2026-08-12 research recommends 2GB ($65), Evan has not decided** ·
  Camera Module 3 Wide (confirmed the correct part for the sim's `fov=90`
  VERTICAL, Appendix AR) + Standard-Mini cable · **Pololu #5159 N20 30:1 HP
  6V *with 12 CPR encoder*** (BOM row 5 corrected 2026-09-02 — it had listed
  the encoderless #1093 for three weeks after Evan chose the encoder) +
  TB6612FNG, both channels paralleled, duty capped 71% · MG90S servo — its
  180° is a **1:1 match to the measured 180° pinion sweep**; ⚠️ the MG996R
  fallback is now a **liability**, SF 0.12-0.19 at the steering coupler ·
  **Arduino Uno R3 clone (OWNED, $0) owns all real-time actuation**: motor
  PWM on Timer2, servo, 4 light channels, quadrature encoder on D2/D3, pack
  guard on A0, TB6612 `STBY` on D10 — **zero PWM spare, A1-A5 the only free
  pins**; Pi↔Uno over USB with the 5 V conductor cut, binary serial protocol
  v0.2 (7-byte command, 9-byte reply, CRC8, ARMED per frame, 150 ms
  watchdog) · power: USB bank → Pi ONLY; 2× EVE 25P 18650 + 2S BMS board →
  TB6612 VM and → LM2596 @ 5.2 V → servo, Uno 5V pin, LEDs, encoder; 3 A
  fuse at the pack, XT30, rocker; ⚠️ **the 2S BMS documents NO over-discharge
  cutoff — open safety item, guarded by firmware only while the firmware is
  on** · DonkeyCar 5.x for Pi-side plumbing **minus its actuator backend,
  which cannot drive the Uno** (task 11 amendment); `rpi-lgpio` not
  `RPi.GPIO` on the Pi 5 · custom PyTorch models · training on RTX 3060 Ti
  8 GB with Sysmem Fallback still ON (capped in code, not in the driver).
- **M4 VRAM constraint (recorded 2026-07-23 ~17:21 CDT):** 8GB is below the
  ~24GB figure the brief cited (single-source) for DreamerV3 on 64×64
  vision. M3 behavioral cloning is unaffected (tiny CNN). M4's exact
  architecture/config is therefore RESEARCH-GATED — see task 16a. Do not
  assume full-size DreamerV3 fits.
- Out of scope (do not start even if convenient): SLAM/LiDAR, online
  on-car RL, sim-RL as a gate (optional parallel track M5 only), Jetson,
  depth cameras, multi-car anything.
- Print rules: calibrate tolerances via coupons BEFORE chassis parts; PETG
  for rotating bores; PLA acceptable for static parts; embed real Lego
  beams/pins as load path where precision matters.
- Environment: Windows 11 + PowerShell 5.1 quirks per global CLAUDE.md; Pi
  work happens on the Pi over SSH once it exists.

## 5. MILESTONES

| # | Milestone | Goal |
|---|---|---|
| M1 | Chassis (CAD + print) | Rolling chassis: Lego diff + steering in printed frame, servo-steerable on the bench |
| M2 | Electronics + teleop | Wired, powered, human-drivable over WiFi; data logging works |
| M3 | Behavioral cloning | Autonomous laps on a custom PyTorch CNN; lane-seg experiment |
| M4 | Offline world model (capstone) | World model + improved policy from the car's own logs |
| M5 | (optional, parallel) Sim-RL track | gym-donkeycar/Wheeled Lab policy + honest transfer report |
| M6 | (stretch) Online Dreamer on car | Only after M4, only with a dated fork authorizing it |

Order rationale: hardware before data before learning; each learning stage
consumes the previous stage's artifacts (M3 consumes M2's logger; M4 consumes
M3's dataset + eval harness). M5 is parallel because its failure (documented
transfer gap) must not block the capstone.

## 6. TASK BREAKDOWN

### M1 — Chassis (CAD + print)

1. ~~**Decision gate — BLOCKED-ON-EVAN.** Evan answers: (a) Pi 5 8GB ($95,
   recommended) or 4GB ($70); (b) which Lego motors he owns (PF M/L/XL vs
   Powered Up 88013/88014 — decides drive+odometry path per brief §2);
   (c) desktop GPU model/VRAM; (d) budget ceiling OK at ~$200; (e) ratify
   the amended staging + scope guard. Done: answers recorded in the record +
   this PRD's constraints updated with dates.~~
   **DONE 2026-07-23 ~17:21 CDT.** Answers: (a) **8GB**; (b) **none owned**;
   (c) **RTX 3060 Ti, 8GB VRAM**; (d) **yes, ~$200**; (e) **ratified**.
   Consequences propagated into §2 and §4 above, and into new tasks 1b and
   16a below.

1b. **Drive motor selection (NEW, added 2026-07-23 ~17:21 CDT — replaces the
   void "reuse an owned PF motor" plan).** Blocks task 6 (rear drive module
   CAD) because the motor's dimensions define the cradle. Research launched
   2026-07-23 comparing: generic N20 gearmotor + printed Lego-axle adapter ·
   used PF motor from the secondary market · new Powered Up 88013/88014 +
   Pi Build HAT (buys 1° encoder odometry, costs ~$50-65 and a different
   control path) · small RC brushed motor. Must resolve gear ratio against
   the real Lego diff reduction and wheel diameter for a 1-2 m/s target, and
   confirm stall current fits the TB6612FNG. Done: motor chosen with Evan's
   go, dimensions recorded in `gotchas.md`/`architecture.md`, BOM updated.
   **RESEARCH RESOLVED 2026-07-23 ~17:47 CDT** —
   `docs/research/2026-07-23_drive-motor-selection.md`. Recommendation:
   **Pololu #1093, N20 30:1 HP 6V, $23.95.** Every Lego motor path is
   REJECTED ON PHYSICS (all PF motors top out at ≤0.88 m/s, below the
   1.0 m/s floor, through any diff configuration); Powered Up + Build HAT
   rejected on five grounds incl. its 8V ±10% supply requirement that a 2S
   pack cannot meet. **Still BLOCKED-ON-EVAN for the purchase go.**
   Drivetrain: config B (62.4 mm tire, 12t→28t, N=2.333, 20.0 mm centres,
   1.28 m/s) is the lower-risk build; config A (43.2 mm, 20t→28t, N=1.400,
   24.0 mm centres, 1.46 m/s) needs the in-plane mesh verified physically
   first. Parallel BOTH TB6612 channels (steering is a servo, so both are
   free) and PWM-cap duty at ~71% of a full 8.4V pack.

1c. **Power system selection (NEW, added 2026-07-23 ~17:32 CDT — Evan owns
   no LiPo battery and no charger, so the whole power path is a purchase).**
   Research launched 2026-07-23 across 2S LiPo + balance charger · 2S/3S
   18650 Li-ion · NiMH pack · split-source (USB power bank for the Pi +
   separate motor battery) · boost/buck arrangements · LiFePO4, compared on
   cost, safety, weight, runtime and complexity. **Pivotal sub-question:**
   whether the Pi 5 genuinely needs 5V/5A for THIS workload (CSI camera, no
   USB peripherals, CPU inference) or whether ~3A suffices — if 3A is
   adequate, cheap 5V/3A sources become viable and the architecture and cost
   both change. Safety is a first-class criterion, not a footnote: this is a
   17-year-old charging cells at home. Done: complete power kit chosen with
   Evan's go (cells + charger + connectors + switch/fusing), runtime
   estimate recorded, `architecture.md` + BOM updated.
   **RESEARCH RESOLVED 2026-07-23 ~17:59 CDT** —
   `docs/research/2026-07-23_power-system.md`. **Pivotal finding: the Pi 5
   does NOT need 5V/5A for this workload** — official docs allow 5V/3A with
   only a 600 mA USB-peripheral cap, and this build has no USB peripherals;
   measured CNN-inference draw is 1.40 A. **Recommended: SPLIT SOURCE** —
   USB power bank → Pi alone; 2× 18650 (7.4V) + USB-C 2S BMS board →
   TB6612FNG VM and → LM2596 @5.2V → servo; one shared ground star-grounded
   at the driver; inline 3A fuse + switch on the motor pack. Chosen on
   SAFETY first (only path where household lithium is a UL/ETL-listed
   consumer product charged from a phone charger) plus structural immunity
   to motor-stall brownout. **NEVER put the Pi and motor on one 5V/3A bank**
   (4.62 A demanded on a 3 A rail during a simultaneous stall).
   **STILL BLOCKED-ON-EVAN on two questions — see below.**

   **NOTE — actuator count (clarified 2026-07-23 ~17:32 CDT):** the car has
   TWO actuators — one drive motor + one steering **servo** (MG90S, already
   budgeted at $5). Steering must NOT be a plain DC motor: without position
   feedback there is no way to command a steering ANGLE, which is exactly
   what the M3 behavioral-cloning model and any M4 policy emit. See
   `gotchas.md`.
2. **Inventory + tooling note.** Catalogue donor Lego set (set number,
   diff type, steering parts), printer model, filament on hand; pick CAD
   tool (recommend Onshape free tier unless Evan prefers Fusion). Done:
   `tooling.md` bin + record entry updated. (Not blocked — can run before 1.)
   **STATUS 2026-09-02: OPEN.** CAD tool, printer model, filament stock and
   donor set numbers are all still uncatalogued. The desktop side of
   `tooling.md` is current (Python 3.12.10 venv, arduino-cli location).
3. **Print tolerance coupons.** ~~Print the Printables 660885 test board (or
   equivalent self-modeled coupon)~~ (changed 2026-07-23 ~20:46: a
   self-generated coupon replaces the third-party download — its contents
   couldn't be verified, the source page 403s, and a parametric generator can
   be re-run when the sweep needs widening). **Coupon generated and validated
   2026-07-23:** `scripts/gen_tolerance_coupon.py` →
   `cad/tolerance_coupon_v1.stl` (104×56×8 mm, 20 holes; generator's manifold
   and signed-volume self-checks both PASS). Bench procedure, print settings
   guidance, and the results table are in `cad/README.md`. **Print in BOTH
   PLA and PETG** using the exact settings intended for the chassis.
   Done: measured table (commanded Ø vs measured Ø vs fit verdict) + print
   settings in the record; chosen offsets written into `gotchas.md`,
   replacing the unverified community figures. **Runnable NOW — needs only
   Evan's printer and Lego, not the parts order.**
4. **Measure donor geometry.** Calipers on the donor steering assembly +
   diff: kingpin spacing, steering arm lengths, axle spans, wheel hub
   interfaces. Done: dimensioned sketch (photo or CAD screenshot) in
   `docs/` + record entry.
   **PARTIAL 2026-09-02 (Appendices BL/BQ/BU):** measured so far — front tire
   track **107.75 mm**, rear **114.75 mm** (the governing width), steering
   pinion **12 teeth**, pinion sweep **~180° lock-to-lock**, max steer **32°**
   (the wheel's DEVIATION from straight ahead — Evan measured with 90° =
   straight, angle = 90 − protractor reading; taking the raw 58° instead is a
   2.6× error in turn radius). **NOT yet measured:** wheelbase (Evan does not
   have the parts), kingpin spacing, steering-arm lengths, hub interfaces,
   and whether any part of the assembled car exceeds the 114.75 mm tire
   track. No dimensioned sketch exists yet.
5. **CAD: front steering module.** Printed frame holding the Lego steering
   geometry + servo mount accepting MG90S AND MG996R footprints + printed
   servo-horn→Lego-axle link (adapt Printables 61922/147626). Done: STL
   exported, printed, Lego parts seat without force.
   ⚠️ **HARD CONSTRAINT ADDED 2026-09-02 (Appendix BV): the "printed
   servo-horn→Lego-axle link" named above FAILS at MG90S stall.** The steering
   coupler is the HIGHEST-torque joint on the car — the exact inverse of the
   drive side, which the 2026-07-23 research carefully showed survivable. A
   printed cross-axle stub is SF **0.57-0.96** at ~216 mN·m; the MG996R the
   mount also accepts is SF **0.12-0.19**. The link must **grip a real Lego
   axle and never print the cross profile**, and the servo must never reach
   stall (task 8c). Printables 61922/147626 are acceptable only as
   socket-style adapters. Constraint: `docs/WIRING_PROTOSHIELD.md` §2.4a.
6. **CAD: rear drive module.** Diff mounts, ~~PF motor~~ **N20 #5159 motor**
   cradle (10 × 12 × 26 mm body, +3-4 mm on the connector side for the
   encoder board, 3 mm D-shaft; drive coupler is a socket gripping a real
   Lego axle — SF 2.26-3.77 at stall, the survivable side), axle bores at
   coupon-calibrated size (PETG). Done: printed; axle+diff spin freely by
   hand with motor engaged. *(Term corrected 2026-09-02 — "PF motor" has been
   wrong since 2026-07-23 ~17:21, when Evan confirmed he owns no Lego motors.)*
7. **CAD: chassis plate.** Bays for Pi, ~~LiPo (low, central), TB6612+UBEC~~
   **2× 18650 holder (low, central) · the Arduino Uno + proto shield (68.6 ×
   53.4 mm — 60% of the 114.75 mm car width, so it mounts lengthwise; stack
   height unbudgeted against the camera) · TB6612 + LM2596 living on that
   shield · the USB power bank for the Pi**, camera mast with adjustable
   pitch (**mount target: true horizon on row 42 of a 120-row frame at 90°
   vertical FOV** — `SIM_TRANSFER_SPEC`), reserved RPLIDAR C1 footprint,
   front/rear module attachment (real Lego pins/beams as load path where
   the coupons say printed holes are marginal). Done: full assembly
   printed + test-fit; M1 success criterion checked. *(Power terms corrected
   2026-09-02 — LiPo/UBEC was superseded by the split-source 18650 design on
   2026-07-23 ~17:59; the Uno bay is new since 2026-09-02, Appendix BC.)*

### M2 — Electronics + teleop

8. ~~**Purchase list — BLOCKED-ON-EVAN.** Final BOM from brief §Ranked
   options (+ SD card, PF 8886 sacrificial cable if not owned).~~
   (superseded 2026-07-23 ~20:46 — the BOM is now written and complete)
   **Purchase — BLOCKED-ON-EVAN.** ~~`docs/BOM.md` is final at ≈$176-179 +
   shipping.~~ Before ordering, Evan verifies the four items in that file's
   "Verify before ordering" section (power-bank output rating, which
   differential he owns, which tires, and current prices). Done: order
   placed by Evan; arrival + any price deltas noted in the record.
   - *(Price corrected 2026-09-01: ≈$176-179 is stale by ~$60. The BOM
     re-priced 2026-08-08 to **$221.82–$224.82** before shipping, and rows
     17–20 — lighting and I/O added 2026-09-01 (Appendix AY) — took it to
     $232–249. **Revised again 2026-09-02 (Appendix BC): row 17's PCA9685 is
     superseded by an Arduino Uno Evan already OWNS ($0), so the total is
     ≈$226–234 before shipping, ≈$241–259 with.** The $200 ceiling is still
     breached on the 4GB Pi; the **2GB path now reaches ≈$196–214**, whose low
     end clears $200 for the first time since lighting was added.)*
   - *(**Revised again 2026-09-02 (Appendix BO) to ≈$235-243 before shipping,
     ≈$250-268 with.** Two changes, both DRIFT REPAIR rather than new scope:
     **row 5 was buying the WRONG MOTOR** — #1093, which has no encoder — while
     Evan chose the **#5159 encoder motor on 2026-08-12** and the firmware pin
     map has spent D2/D3 on encoder interrupts ever since (+$6.00); and **new
     row 5b**, the **#4763 JST SH cable Pololu explicitly does not include**
     with #5159 (+$3.00), same defect class as row 3's camera cable.
     ⚠️ **The $200 ceiling is now breached on EVERY path, including the 2GB Pi**,
     which lands at ≈$205-223 with shipping. The 2GB path was the last one whose
     low end cleared it.)*
   - *(Amended 2026-09-01, again 2026-09-02: the "four items" are now **six** — check 5, which
     LEDs, sets every series-resistor value. And the **PWM-path question is
     RESOLVED** — ~~PCA9685~~ **an ARDUINO UNO (2026-09-02, Appendix BC)**,
     carrying motor PWM + servo + 4 light channels and adding encoder counting
     plus a throttle watchdog the PCA9685 could not. That was BLOCKED-ON-EVAN
     and no longer is. Pin map: `firmware/SERIAL_PROTOCOL.md`.)*
8b. ~~**Uno actuation firmware**~~ **DONE 2026-09-02 (Appendices BO/BU).**
    Appended retroactively: this work was not in the PRD because the Arduino
    only entered the design on 2026-09-02 (Appendix BC), superseding the
    PCA9685. **It needed NO parts**, which is why it ran ahead of task 8.
    `firmware/uno_control/` implements `firmware/SERIAL_PROTOCOL.md` v0.2 —
    7-byte command, 9-byte reply, CRC8, ARMED-per-frame, 150 ms watchdog,
    4x quadrature encoder, the pack-guard throttle inhibit, and D10 -> TB6612
    `STBY`. Done-check MET: **firmware SELFTEST 39/39 on the real board** and
    **`firmware/host_test.py` 11/11, exit 0**; 7232 B flash (22%), 312 B SRAM
    (15%), loop 2-3 ms of the 50 ms budget.
    ⚠️ **ACTUATORS UNWIRED.** The link and the state machine are verified; no
    motor, servo, encoder, LED or pack exists, so every actuator path is
    verified only as a DECISION the firmware made, never as something that
    physically moved.

8c. **Steering calibration + the servo-to-pinion coupling** (appended
    2026-09-02, Appendices BS/BU/BV). **OPEN, and 8c(ii) is a hard constraint
    on the mechanical design, not a preference.**
    (i) **One-shot centre calibration into EEPROM.** Evan proposed calibrating
        every startup by driving to both locks. **It cannot work as stated:** a
        hobby servo gives the Uno no position feedback, so the board cannot
        detect a stop; and **opening the serial port RESETS the board**, so
        "every startup" means "every Pi reconnect" and would slam the steering
        into both hard stops each time. Corrected shape: calibrate ONCE on an
        explicit command with an operator in the loop (zero new hardware),
        store both endpoints in EEPROM (1024 B available), reload on boot.
        Done: measured endpoints in EEPROM, centre derived not assumed, and a
        SELFTEST that fails if the stored span is absent or implausible.
    (ii) **Choose a coupling that survives.** ⚠️ **The steering coupler is the
        HIGHEST-torque joint on the car and a PRINTED cross-axle stub FAILS
        there** — SF **0.57-0.96** at MG90S stall (~216 mN·m), against SF
        2.26-3.77 for the N20 drive coupler it was modelled on. **The MG996R
        fallback named in BOM row 7 is SF 0.12-0.19**, i.e. choosing it makes
        the coupling problem ~5x worse rather than solving a stall. Must grip a
        real Lego axle; never print the cross profile. Constraint written to
        `docs/WIRING_PROTOSHIELD.md` §2.4a. Done: a coupling selected with its
        stall-torque margin stated.

9. **Bench bring-up.** Pi OS (64-bit Bookworm), SSH, camera test; TB6612 +
   ~~PF motor~~ **N20** on bench PSU; servo sweep test. Done: each
   subsystem's real output (photo/log) in record.
   **PARTIAL 2026-09-02 — the Uno half is done AHEAD of parts:** board proven
   (`uno_bringup`), SRAM and clock measured (`uno_memtest`: 2048 B, 16.0042
   MHz), link measured (`uno_echo`: p99 1.069 ms), pack guard and control
   firmware verified on the board (task 8b). **Everything that needs a part —
   Pi, camera, TB6612, motor, servo — is untouched.** For the servo sweep:
   use `uno_control`'s calibrated span, never a raw full-range sweep, or the
   first bench test drives the servo into the Lego hard stop (task 8c).
10. **Power integration.** ~~LiPo + UBEC + split rails~~ **2× 18650 + 2S BMS
    + LM2596 @ 5.2 V for the actuator side, USB bank for the Pi, one star
    ground** on the chassis; measure ~~5V rail~~ **both rails** under motor
    stall + Pi load. Done: no brownout/UV warning in `vcgencmd` during stall
    test; measurements recorded. *(Terms corrected 2026-09-02; the split-source
    architecture itself dates from 2026-07-23 ~17:59 and is unchanged. Net
    list and an 8-step build order: `docs/WIRING_PROTOSHIELD.md`.)*
    ⚠️ **GATE: BOM Verify item 6.** The 2S BMS board documents NO over-discharge
    cutoff, and firmware cannot guard a pack while the firmware is off. Close
    it (protection board that states over-discharge cutoff, or protected
    cells) before any pack is charged. **Evan's call.**
11. **Teleop + logging.** DonkeyCar install, web/gamepad teleop, tub
    recorder verified (images + steering/throttle synced). Done: M2 success
    criterion (full-session drive + ≥10 readable laps).
    - *(**AMENDED 2026-09-02 (Appendix BC): DonkeyCar cannot drive this car's
      actuators.** Its `pins.py` has three PWM backends — RPI_GPIO, PCA9685,
      PIGPIO — and the actuators sit behind an Arduino Uno speaking a binary
      serial protocol none of them knows. Task 11 is therefore: DonkeyCar for
      the camera, teleop UI and tub recorder, **plus a custom DonkeyCar part
      that speaks `firmware/SERIAL_PROTOCOL.md` v0.2** — sends the 7-byte
      command at 20 Hz with ARMED set, reads the 9-byte reply, and surfaces
      `ticks` (the car's only odometry) and pack state. `firmware/host_test.py`
      is the seed of that part. Also: `donkeycar[pi]` pulls in `RPi.GPIO`,
      which does not work on the Pi 5 — use `rpi-lgpio`.)*

11b. **Indicator state in the logger — GATES TASK 12** (appended 2026-09-01,
    Appendix AY / `docs/LIGHTING_SPEC.md` §5). Task 11's done-check names two
    logged channels, "images + steering/throttle synced". Evan's lighting
    request adds turn signals, and a turn signal is a **policy OUTPUT**, so it
    needs a per-frame label: extend the tub schema to a third field,
    `indicator ∈ {off, left, right}`, and give the teleop rig two buttons to
    set it.
    - **Why it is learnable at all, unlike the stop sign:** `gotchas.md` records
      that a stop sign is provably unlearnable by plain BC — stopped at the
      line, the image is identical whether to wait or go. An indicator on a
      MEMORISED route is the opposite: the correct state is a function of where
      the car is, which is visible in the frame.
    - **Why it gates task 12:** 10-20 laps recorded without indicator labels
      cannot be relabelled honestly. If this does not land before the
      collection run, drive the indicators from a rule on predicted steering
      and **say in the write-up that they are rule-driven, not learned.**
    - Done: a logged session whose tub carries all three fields, frame-synced,
      spot-checked against the recorded button presses; record entry.

### M3 — Behavioral cloning

12. **Track + dataset.** Define the training track (tape on floor);
    collect 10-20 clean laps. Done: dataset size + sample frames in record.
    - *(Amended 2026-09-01: "tape on floor" is superseded by the TRACK section
      below — printed markings on a board, layout in `cad/track_layout_v2.py`.
      Not struck, because the task's intent — define a track, collect clean
      laps — is unchanged.)*
    - *(Amended 2026-09-01: **gated by task 11b.** Collecting these laps before
      the logger records indicator state forfeits the multi-task head for this
      dataset. Check 11b's status before starting the run.)*
    - *(Amended 2026-09-02 from the P5 follow-up (Appendix W) and the paired
      eval (Appendix AJ): collect a **separate off-centre recovery set, exempt
      from the quality filter**. In sim the 69-110-step wall was perception
      going out of distribution — the clean corpus had no off-centre frames —
      and the same wall will appear on the physical car. **But Appendix AJ
      then found that recovery data mildly HURT closed-loop driving in sim**
      (negative in 4/4 launches, n.s.). So: collect it, and evaluate it as a
      separate arm. Do not assume it helps.)*
13. **Baseline train + deploy.** DonkeyCar's stock trainer as baseline;
    deploy; measure. Done: autonomous attempt logged (laps, interventions).
14. **Custom PyTorch model.** Swap PyTorch CNN into the inference path;
    train on same data; A/B against baseline. Done: eval table both models.
15. **Lane-segmentation experiment.** Train/apply a simple lane-mask
    preprocessor; A/B robustness (lighting changes). Done: comparison in
    record; M3 success criterion checked.

### M4 — Offline world model (capstone) — tasks to be REFINED after M3
(deliberately coarse now; detail them in a dated PRD append once M3's
dataset format and eval harness exist)

**STATUS 2026-09-02:** every M4 task below already has a working **SIM**
implementation from SIM-POC — `ml/episode_writer.py` + `verify_corpus.py`
(16), `train_vae.py` + `train_mdnrnn.py` (17), `run_dreamer_p4.py` + the 8 GB
fitting table (18), `train_controller.py` / `plan_cem.py` / `eval_paired.py`
(19). **All sim-only.** M4 proper needs real-car logs → M2 → parts. The sim
result to carry forward honestly: **no learned policy drove reliably in sim
across five attempts** (Appendix AJ); the causes are understood (perception
out of distribution; a track generator that regenerates per launch); and the
trustworthy results are the open-loop ones (aux-head probe AUC 0.673 → 1.000,
the copycat refutation, the readout improvement). **Held-out MSE ranks
policies backwards here — never select a controller on it.**

16a. ~~**Architecture + VRAM gate (NEW, added 2026-07-23 ~17:21 CDT).** Pick
    the world-model architecture that actually fits 8GB of VRAM on the
    3060 Ti and still constitutes a genuine world model. Research launched
    2026-07-23 covering DreamerV3 size presets and real 8-12GB training
    reports, offline model-based RL codebases, the much smaller Ha &
    Schmidhuber VAE+MDN-RNN architecture, 8GB mitigations (mixed precision,
    gradient checkpointing, batch/sequence sizing, WSL2 vs native Windows),
    required dataset size, and Colab/Kaggle escalation if 8GB genuinely
    blocks it. Done: architecture chosen with a cited VRAM basis, written
    into `dependencies.md` + a dated PRD append detailing tasks 16-19.~~
    **RESOLVED 2026-07-23 ~17:39 CDT** — see
    `docs/research/2026-07-23_world-model-8gb-vram.md`. Verdict: **feasible
    with constraints.** Two architectures, one dataset, one eval harness
    (tasks 16-19 restructured below). Note the research **RETRACTED** the
    earlier "~24GB VRAM" figure — it was unlocatable and does not
    generalise downward.

**M4 tasks (restructured 2026-07-23 ~17:39 CDT — supersedes the coarse
16-19 list below, which is struck in place):**

16. **Dataset consolidation + replay format.** All logged driving into one
    corpus in `dreamerv3-torch` episode format (so the same data feeds both
    architectures). Held-out split defined here, not later. Target 100k-200k
    frames @20Hz = 1.4-2.8 h driving = 1.2-2.5 GB. Done: corpus on disk,
    frame/action sync verified by spot-checking N random frames against
    their recorded actions, split documented.

17. **Build the SMALL world model first (Ha & Schmidhuber V+M+C, ~4.77M
    params).** Conv-VAE -> z in R^32; MDN-RNN over (z_t, a_t, h_t) ->
    p(z_{t+1}). This is the de-risking step: it exercises the entire data
    pipeline and eval protocol and cannot OOM. Done: multi-step latent
    rollouts on held-out data are recognisably track-like (qualitative,
    with saved rollout frames in the record).

18. **Attempt DreamerV3-S on the same corpus.** `NM512/dreamerv3-torch`
    (PyTorch — the JAX reference has NO offline mode and no native-Windows
    CUDA), repo-default S-scale config, `offline_traindir`, batch 16,
    length 50, **imag_horizon 5** (V-D4RL offline finding, not the default
    15), fp32 first. **Disable NVIDIA Sysmem Fallback first** or an OOM
    silently becomes a ~3x slowdown. Log
    `torch.cuda.max_memory_allocated()` every epoch. Done: either a trained
    model OR a documented OOM boundary with the measured number — **both
    outcomes are a pass**, because nobody has published this figure.

19. **Policy extraction + on-car eval.** From whichever model(s) trained:
    latent BC on (z,h)->action, or CEM/random-shooting planning through the
    learned dynamics. Evaluate on the SAME 3-lap protocol as M3. Done: M4
    success criterion — comparison table (M3 BC vs each world-model policy)
    in the record.

20. **Writeup** (portfolio artifact via /portfolio-case-study). Must state
    the scale honestly: comma.ai's driving world model is 250M-1B params on
    100k-400k minute-long segments; this is five orders of magnitude
    smaller. The novel part is the constraint and the measurement, not
    beating the state of the art.

~~16. **Dataset consolidation + replay format.** All logged driving into one
    training corpus. 17. **World model training offline** (architecture per
    16a; desktop GPU). 18. **Policy extraction + on-car eval** vs M3
    (M4 success criterion). 19. **Writeup** (portfolio artifact via
    /portfolio-case-study).~~ (superseded 2026-07-23 ~17:39 CDT by the
    restructured 16-20 above, once the VRAM research made the two-
    architecture sequencing the better plan)

### M5 — (optional, parallel, never blocks M4) Sim-RL track

20. **gym-donkeycar PPO baseline; honest transfer attempt + report.** The
    report's value is the measured transfer gap itself.
    **STATUS 2026-09-02: never started, and deliberately so.** *(Numbering
    note: this "20" collides with M4's task 20, the writeup. Pre-existing;
    not renumbered because record entries reference both by number.)*

### TRACK — the physical driving environment (ADDED 2026-08-05; needed before M2 data collection, i.e. by ~week 5)

**Decided 2026-08-05 (Evan): 1.6 × 2.8 m floor space available · 1:14 scale
kept · figure-8 layout · print MARKINGS, not the road surface.** Full
reasoning, MUTCD verification, and the rejected alternative are in record
Appendix L.

**SUPERSEDED IN PART, 2026-09-01/02 (Appendices AM/AX/BO/BX):** the floor is
**3.0 × 3.0 m** (Evan, 2026-09-01), not 1.6 × 2.8; the layout is
`cad/track_layout_v2.py` — a 3×3 city grid **driven as** a figure-8 through
the centre intersection, 8.31 m route, **171 mm spare at R = 500 mm** — not a
plain figure-8; the lane is **230 mm** on the measured 114.75 mm car, not
261 mm on an estimated 130. The figure-8 rule and print-markings-not-surface
both stand, the latter now as a **hybrid**: ~73 printed tiles for corner arcs
and intersection boxes (~902 g), tape for ~31.5 m of straights (Appendix AX).
**The marking table below is stale and NOT yet recomputed** (T1 is partial).

**The core decision and why:** printing the road surface costs ~6.4 kg of
filament and ~150-250 print-hours for a minimum two-lane loop; printing only
the markings costs ~0.15 kg and ~6 hours — **a 97% reduction for identical
camera input**, because at 120×160 the camera sees markings, not road. The
printer is also committed to chassis parts in weeks 1-3, and large thin
prints warp on the one surface that must be flat. **Substrate = dark matte
foam board / coroplast tiles (~$15 total); markings = printed strips glued
flush; printer is reserved for strips, signs, and stencils.**

**Layout = FIGURE-8, never a plain oval** — a one-handed loop teaches the BC
model "always steer left", which looks perfect on the training track and
fails everywhere else. The figure-8 also yields the intersection for the
stop sign / traffic light for free.

**Scaled marking specs (MUTCD-verified 2026-08-05; scale from an ESTIMATED
130 mm car width — recompute at T1):** lane 261 mm · normal line 7.3 mm ·
stop line 22-44 mm · **dash compressed to ~60/180 mm** (true scale is
218/653 mm, which shows only ~3.5 dashes on a 5 m loop — the MUTCD's own
"similar ratio of line segments to gaps" latitude permits the compression;
the deviation is deliberate and documented). Yellow separates opposing
directions; white separates same-direction.

T1. ~~**Confirm scale.** Recompute the marking table from the MEASURED car
    width (needs B2/B3). Done: table in the record with measured input.~~
    **DONE 2026-09-02 (Appendix BO).** Evan measured tire track: front
    107.75 mm, **rear 114.75 mm — the governing width**, superseding the
    130 mm ESTIMATE every track document had used since Appendix L.
    `cad/track_layout_v2.py` re-run on it (a `--car-width` flag was added to
    mirror the existing `--radius`): **lane 260 -> 230 mm, span 2660 ->
    2629 mm, spare 140 -> 171 mm, tiles 79 -> 73 (~902 g of filament).**
    ⚠️ **Two caveats carried forward:** it is TIRE TRACK, not whole-vehicle
    width — confirm nothing on the assembled car exceeds 114.75 mm — and the
    HANDOFF-era rule of thumb "40 mm of span per 10 mm of car width" is
    **WRONG for this geometry** (Appendix BP): `best_straight` is capped at
    MAX_STRAIGHT = 200 mm, so pitch never moves and span tracks the lane
    delta at **2x** the car-width change, not 4x. The marking table itself
    (line widths, dash pattern) is NOT yet recomputed.
T2. **Measure minimum turning radius empirically** on the rolling chassis
    (needs M1.7). Estimate is ~330 mm centerline (wheelbase ÷ tan(max
    steer)) ⇒ corners want 500-670 mm, but that is arithmetic on an
    estimate. **No corner tile is cut before this measurement.** Done:
    measured radius in the record.
    **UPDATE 2026-09-02 (Appendix BQ):** max steer is now MEASURED at **32°**,
    so the only unknown in `wheelbase ÷ tan(max steer)` is wheelbase:
    **R_min = 1.600 × wheelbase.** The ~330 mm estimate implies ~206 mm of
    wheelbase, which is plausible for a 114.75 mm-wide car, so the 500-670 mm
    band probably does not shrink. This is still not T2 — T2 is the empirical
    test — but once wheelbase is calipered the geometric radius can bound the
    corner tiles before the rolling chassis exists.
T3. **Design the figure-8** to fit ~~1.6 × 2.8 m~~ **3.0 × 3.0 m** at the
    confirmed scale; vector/CAD layout with tile boundaries chosen so **seams
    run parallel to travel** where possible (a perpendicular seam reads as a
    stop bar to the model). Done: layout drawing + tile cut list.
    **PARTIAL 2026-09-01/02:** two parametric, self-checking layouts exist —
    `cad/track_layout_v1.py` (figure-8 with a causeway bridge + 5 landmarks)
    and **`cad/track_layout_v2.py`** (3×3 grid, 9 intersections, figure-8
    route through the centre; `--radius` and `--car-width` flags). Both write
    an SVG plan. **Neither is committed geometry** (corner radius frozen until
    T2) and **no tile cut list exists.** A sim rehearsal of the track was
    investigated and is IMPOSSIBLE — gym-donkeycar has no road-definition
    message (Appendix AX).
T4. **Fabricate substrate** — dark matte tiles, cut to the T3 list. Done:
    tiles laid out flat, photographed.
T5. **Generate + print markings, sign, and stencils** — parametric generator
    in the style of `scripts/gen_tolerance_coupon.py` (self-validating,
    re-runnable when the scale changes), 0.8 mm strips + a scaled stop sign.
    Done: generator self-check passes, parts printed and fitted.
T6. **Assemble and define the layout configurations.** Build config A and B
    for training and hold out **config C entirely** for testing. Done: three
    configurations photographed and documented; C never driven for training
    data.

**Stop sign / traffic light — deferred to M4 by design, not by oversight.** A
traffic light is EASY to learn (red/green is visible in the current frame, so
a memoryless CNN suffices) but needs hardware. A stop sign is trivial to
build but **provably impossible for plain BC** — stopped at the line, the
image is identical whether to wait or go, so the correct action depends on
history, which π(action|image) cannot express. That makes the stop sign the
ideal M4 demonstration: same track, same dataset, **BC fails and the world
model succeeds** because the RSSM / MDN-RNN carries recurrent state. Build
the sign into the track from the start; exercise it at M4.

### SIM-POC — simulated proof of concept of the M4 pipeline (ADDED 2026-08-05, parallel track, runnable before any hardware exists)

**What this is (and is not).** Asked by Evan 2026-08-05: "can we train the
model in a simulated space first as a proof of concept?" Yes — as a POC of
the PIPELINE, not of transfer. The M4 world-model stack is trained on
simulated driving data and evaluated IN SIM, proving the code path end to
end while parts ship. This is NOT M5 (no online RL, no PPO, no sim2real
claim), and the scope guard stands: **the sim-trained policy is never
claimed as the real car's policy; M4's capstone remains offline training on
the car's own real logs.** What it retires early, from the 2026-07-23
research's own flagged unknowns: (a) whether dreamerv3-torch's
`offline_traindir` runs end-to-end with zero env instantiation; (b) the real
8GB OOM boundary on the actual 3060 Ti — the number nobody has published;
(c) the episode format / frame-action sync / held-out split / eval harness
that M3-M4 then inherit proven. Sim: **gym-donkeycar v25.10.06** — Windows
binary verified to exist 2026-08-05 (DonkeySimWin.zip, 236,059,289 bytes,
GitHub API).

P1. **ML environment.** ~~Pinned **Python 3.11 venv** (matches DonkeyCar
    5.x; system 3.14.4 is too new to assume ML wheels)~~ (amended
    2026-08-05 ~21:42: **3.11 is not installed on this machine; 3.12.10 is**,
    and it was the pre-declared fallback. Verified before switching: torch
    2.13.0 classifies 3.10-3.14, and gym-donkeycar needs only
    gymnasium>=0.29/numpy/pillow at python_requires>=3.7 — so 3.12 is
    covered and no 3.11 install is warranted.) **Python 3.12 venv at
    `.venv/`** + PyTorch CUDA + gym-donkeycar **installed from GitHub, NOT
    PyPI** (PyPI's gym-donkeycar is 1.0.13 from 2019-08-04 — six years
    stale; GitHub is v25.10.06) + the DonkeySimWin binary (~236 MB). Done:
    `torch.cuda.is_available()` prints True from the venv AND a
    gym-donkeycar env connects to the sim and returns a camera frame.
    **DONE 2026-08-05** (commit 83e966b; `ml/verify_env.py` is the runnable
    done-check and exits non-zero on failure).
P2. **Sim data corpus.** Drive the sim (scripted PID lane-follower or
    keyboard) and record camera + steering/throttle into the
    dreamerv3-torch episode format; ~100k frames; held-out split defined
    here. **Split by LAYOUT, never randomly by frame** (amended 2026-08-05):
    frame t and t+1 are near-duplicates, so a random split leaks and
    massively overstates accuracy. The 11 registered gym-donkeycar tracks
    are the sim analogue of the physical tile configurations — train on a
    subset, hold out whole tracks. Same rule carries to M3/M4 on real data.
    Done: corpus on disk + N random frames spot-checked against their
    recorded actions + the held-out track list documented.
    **AMENDED 2026-08-06 (Evan's decision, record Appendix P/Q):
    `mountain-track` and `roboracingleague-track` were QUARANTINED** - the
    tuned expert cannot drive them (13/13 episodes rejected, and 303-frame
    episodes against a 1200 request respectively); they supplied 7% of the
    corpus and 100% of its verification failures. Their 15 episodes moved to
    `ml/data/sim_quarantine/`, not deleted. **Consequence to state in any
    writeup: SIM-POC trains on TWO layouts, not four.** The held-out-layout
    design survives (2 train + 1 entirely unseen holdout) and remains far
    stronger than a random frame split, but the phrase "four tracks" must
    never be used. Layout diversity is properly an M3/M4 real-car concern.
    **DONE 2026-08-06 (Appendix R):** 102,888 frames, 88/88 episodes verified
    on BOTH alignment axes, split disjoint — `ml/verify_corpus.py` PASS;
    re-verified PASS 2026-09-01. Train is unbalanced 51:27 across the two
    surviving layouts.
P3. **Small world model first (Ha & Schmidhuber V+M+C).** Conv-VAE →
    z∈R^32; MDN-RNN over (z_t, a_t, h_t). Done: multi-step latent rollouts
    on held-out sim data are recognisably track-like; rollout frames saved.
    **DONE 2026-08-06 (Appendix S):** V+M+C trained (VAE 4,348,547 params —
    an exact match to the paper's count, asserted in code). 30-step
    imagination beats a frozen-frame baseline **30/30 steps in-domain, 0/30
    cross-domain**; `ml/rollout_eval.py` is the gate and exits 1 below 90%.
P4. **DreamerV3-S offline on the same corpus.** dreamerv3-torch repo
    defaults, `offline_traindir`, imag_horizon 5, fp32 first; **Sysmem
    Fallback disabled before the first run**; log
    `torch.cuda.max_memory_allocated()` every epoch. Done: a trained model
    OR a documented OOM boundary with the measured number — both pass.
    **AMENDED 2026-08-06 (record Appendix T) — TWO PREMISES IN THIS TASK
    WERE FALSE, and both are now measured facts:**
    (a) ~~`offline_traindir`~~ does NOT give an offline training run.
    `dreamer.main()` builds envs unconditionally (dreamer.py:238-241) and
    drives training from `tools.simulate()` env steps (dreamer.py:319) — the
    repo **has no offline training loop at all**; the flag only warm-starts
    the replay buffer. This retires the 2026-07-23 research's flagged
    unknown (a) with a NO. `ml/run_dreamer_p4.py` supplies hand-built gym
    spaces plus a real offline loop over the unmodified `Dreamer._train`,
    leaving `ml/vendor/` unpatched.
    (b) ~~Sysmem Fallback disabled before the first run~~ — it was **not**
    disabled, and it is **still ON** (measured: 10.0 GB allocated on the 8 GB
    card with no OOM). Changing a driver setting is BLOCKED-ON-EVAN, so the
    task is met instead with `torch.cuda.set_per_process_memory_fraction`
    (`--cap-gb`), verified to still raise OOM under active fallback. That is
    strictly better for this project: it lives in version control and is
    reproducible, where a control-panel checkbox is neither.
    **DONE 2026-08-06 ~13:36 CDT — BOTH halves, each verified (record
    Appendices T and U).**
    *Boundary half:* `ml/runs/dreamer_p4/sweep_summary.json` (regenerate with
    `python ml/sweep_dreamer_p4.py`). Headline: **batch size, not model size,
    is what breaks 8 GB** — a 69.7M-param model fits at batch 16 (5.238 GB)
    while the 19.1M model at batch 64 does not fit in 7.0 GB.
    *Trained half:* 2000 offline steps, no OOM, **image reconstruction loss
    588.31 → 61.39, a 9.6x reduction** (`ml/runs/dreamer_p4/S_b16_train2000/
    p4_result.json`). Peak VRAM held at **2.550-2.552 GB across all 20
    epochs** — a 0.002 GB spread, and identical to the 20-step sweep figure,
    so the boundary measurement is confirmed stable over a long run rather
    than a warm-up artifact.
P5. **Policy extraction + in-sim eval.** Latent BC and/or CEM planning
    through the learned dynamics; evaluate in sim against the P2 scripted
    driver. Done: eval table in the record + the explicit no-transfer-claim
    note.
    **DONE 2026-08-07 ~05:55 CDT (record Appendix V) — BOTH options built, and
    the result is an INSTRUMENTED NEGATIVE.** Latent BC (`train_controller.py`,
    linear and MLP) and CEM planning (`plan_cem.py`) were each evaluated over
    3 seeds x 3 episodes against the PID expert. **No learned policy completed
    a single episode; the expert completed 9/9.** Eval table in Appendix V.3.1;
    artifacts in `ml/runs/p5_eval/` and `ml/runs/p5_cem/`.
    Three findings the task did not anticipate:
    (a) **The paper's linear controller is structurally wrong for this task.**
    A linear probe recovers R^2 = 0.27 of cross-track error from z; an MLP
    probe recovers 0.97 — the latent encodes lane position NONLINEARLY, so a
    linear C cannot compute it. Swapping to an MLP cut in-sim lane error 2.4x
    to essentially expert level (0.435 vs 0.381) and still did not finish.
    (b) **Evan's "incentive" proposal required CEM, not BC** — behavioural
    cloning has no reward to attach an incentive to. Implemented as
    `W_CTE*mean(cte^2) + W_SMOOTH*mean(dsteer^2)`; the centring term gave the
    best survival of any learned policy (89.7 vs 69.3 steps), while the
    smoothness term proved UNDER-weighted (the planner is the jitteriest
    policy measured, 20.9 reversals/100 vs the expert's 9.87).
    (c) **The bottleneck is the representation, not the controller.** Three
    policy classes wall at 69-110 steps; only the expert, which never touches
    the latent, completes. Corner speed was tested and ruled out.
    **SIM-POC (P1-P5) is now COMPLETE.**
    **CAVEAT ADDED 2026-08-11 ~23:29 CDT (record Appendices AC/AD): every STEP COUNT above
    is from a harness now known to be unreliable, and none of them are
    certified.** The same controller checkpoint, same seed, evaluated across
    gate-valid sim launches, scores anywhere from 106.5 to 471.5 steps — a
    4.4x spread — while episodes WITHIN a launch agree to a few steps. Ruled
    out as causes: control rate, track identity, and episode start state
    (`ml/diag_reset.py`: post-RESET POSITION is near-deterministic — z and
    speed identical across all 16 episodes of two launches, x identical for 14
    of 16 with episode 0 of each launch differing by 2.8e-4 world units.
    Post-warmup *cte* is NOT four-decimal identical; it spans 0.0018-0.0075,
    which is ~0.6% of the ~0.87 cte the car actually operates at, i.e. far too
    small to explain a 4.4x swing). **The LAUNCH is the unit of variation and
    the cause is unknown.** The qualitative conclusions above survive — the expert
    completes and learned policies mostly do not, across every launch — but
    the specific numbers (69.3, 89.7, 187.2, 110) must not be quoted as
    measurements. Also note the flat claim "no learned policy completed a
    single episode" is now FALSE: completions have since been observed, just
    not reliably.

    **P5 FOLLOW-UP, 2026-08-08 (record Appendix W) — the wall is DIAGNOSED and
    it is a DATA problem, plus a new PRD-level risk:**
    (a) **The 69-110 step wall is PERCEPTION going out of distribution.** The
    probe's lane-position error is a function of POSITION, not policy or time:
    ~0.20 while |cte| < 1.0, rising to ~2.1 past 1.5, with corr 0.894 (learned
    policy) and 0.852 (PID expert) — the SAME curve under both drivers. Cause:
    `collect_sim_data.py` rejects episodes with `mean|cte| > 1.2` and the
    expert averaged 0.36, so the corpus has no off-centre frames and the
    encoder has never seen the states a recovering policy needs. Drift past
    ~1.0 and the car cannot see where it is. **No controller change fixes
    this** — it explains why three policy classes failed identically.
    **ACTION FOR M3: collect a SEPARATE off-centre recovery set, exempt from
    the quality filter.** The filter that keeps the imitation corpus clean is
    exactly what deletes the recovery data, and the same wall will appear on
    the physical car without it.
    (b) **RISK TO THE M4 STOP-SIGN SHOWCASE.** Both the ConvVAE and DreamerV3
    erase small objects entirely — **0 of 899 cone pixels survive in either
    reconstruction** (`ml/compare_encoders.py`). The showcase assumed the sign
    reaches the latent; at 64x64 with a reconstruction-dominated objective, an
    object at <1% of frame does not. A bigger world model is NOT the fix.
    ~~**DECISION NEEDED (not an implementation detail):** raise input
    resolution, add an auxiliary detection/segmentation head, or change the
    showcase task.~~ **RESOLVED 2026-08-10 18:44 CDT by Evan: auxiliary
    detection head + an oversized (non-scale) printed sign.** Rationale and
    the three measurements behind it are in record Appendix Y. In short:

      - **Raising resolution was rejected on an argument, not a measurement.**
        Reconstruction loss is a MEAN over pixels, so an object's share of the
        gradient is scale-invariant — 28/4096 at 64x64 is 112/16384 at 128x128,
        the same 0.68%. Higher resolution buys detection RANGE (a 2px distant
        sign becomes 8-12px and is at least representable); it does not make
        the objective care. It also costs the P3/P4 shared-tensor
        comparability and runs into the batch-size wall measured in P4.
      - **Oversized sign is the cheap half and attacks the real quantity.**
        Pixel SHARE is what governs whether the objective cares, and printing
        a larger sign raises it directly, for free. Deliberately off-scale;
        that is a documented modelling choice, not an oversight.
      - **NEW HARD REQUIREMENT — the sign must be RELOCATABLE / REMOVABLE.**
        This falls out of a measurement, not a preference. On a fixed track a
        sign at a fixed place is perfectly predicted by "where am I", and the
        latent already encodes track position (cte probe R^2 0.957). A policy
        could then pass the whole showcase by stopping at a LOCATION while
        being blind to the sign, and an auxiliary head could drive its loss to
        zero the same way. `ml/probe_cone.py` measured exactly this failure on
        the sim's cones: AUC 0.997 that collapsed to nothing under ablation.
        A sign that moves between runs is what makes the demonstration mean
        anything. Cost: none — a printed sign placed on the track.

    **STILL OPEN (tracked, not decided):** whether the aux head is sufficient.
    `ml/exp_aux_head.py` tests it against a position-decorrelated synthetic
    object; if a z=32 bottleneck cannot retain a <1%-of-frame object even
    under direct supervision, the escalation is a larger z or a detection path
    that bypasses the latent, and this item reopens.

- [x] **P6 (NEW, 2026-08-11, BLOCKING all future closed-loop claims; CAUSE
      FOUND 2026-08-13, Appendix AI; DONE 2026-08-13, Appendix AJ — checkbox
      ticked 2026-09-02, it had been left open for three weeks and made
      HANDOFF and /milestone-track both report the harness as still blocking.
      Precisely what closed it: the PAIRED design in `ml/eval_paired.py`. The
      done-check's clause "eval_in_sim.py refuses to emit a comparison the
      noise floor cannot support" is met by routing every comparison through
      `eval_paired.py` — `eval_in_sim.py` itself has only the expert-survival
      BATCH INVALID gate, not a noise-floor refusal): make the
      sim evaluation harness trustworthy, or characterise its noise well
      enough to design around.** This is not optional polish — it invalidated
      a headline result (Appendix AB, retracted in AC) and it gates every
      driving number the project will ever report, including M3/M4 on the
      physical car. Done when: the launch-to-launch spread on a fixed
      checkpoint is either eliminated, or quantified with enough launches that
      a claim can carry a real confidence interval; and `eval_in_sim.py`
      refuses to emit a comparison that the measured noise floor cannot
      support. Already built and reusable: the expert-survival batch gate
      (necessary, not sufficient), `control_hz` reporting, and
      `ml/diag_reset.py`.
      **Three concrete levers, cheapest first (added 2026-08-11 from the
      landing-check critique of Appendix AD):**
      **THE CAUSE IS NO LONGER UNKNOWN (2026-08-13, Appendix AI):
      `donkey-generated-track-v0` REGENERATES THE TRACK ON EVERY LAUNCH.**
      Three identical-config launches at an identical spawn pose differ by
      MAE 29-36 with 27-35% of pixels differing by >30, at stable brightness;
      the same test on the fixed `donkey-warehouse-v0` gives a 0.307 noise
      floor. The launch is the unit of variation because the TRACK is. This
      supersedes the caveat above listing track identity as "ruled out" -
      that was wrong, and tight expert cte across launches is exactly what a
      track generator produces.
      **The cheapest fix now dominates the others: EVALUATE ON A FIXED TRACK.**
      The paired design (a) is still correct and now has a mechanism - pairing
      arms within one launch holds the track constant. ~~Done when Z.3, AA.1,
      AB.2 and AC.1 have been re-run on a fixed track.~~ **DONE 2026-08-13
      (Appendix AJ), but NOT on a fixed track — a fixed track proved unusable:
      every one is far outside the corpus's visual distribution and the learned
      controllers collapse to 13-67 steps there (mean|cte| 2.2-3.8 vs the 0.317
      they trained at). The fix was the PAIRED design instead
      (`ml/eval_paired.py`): all arms inside ONE launch sharing that launch's
      generated track, differenced within-launch, verified on synthetic data to
      cancel a known per-launch offset exactly. RESULT: no arm beats the
      baseline. The most consistent signal is that recovery data mildly HURTS
      (cl_aug negative in 4/4 launches, mean -26.0, t=-1.84, n.s.; ~19 launches
      needed). Pairing cut variance for 2 of 3 arms but RAISED it for the
      third, so real arm x track interaction remains and is not removable by
      experimental design. Expert 600/600 in all four launches, so the batch is
      unambiguously valid — the first closed-loop comparison in this project
      that is a measurement rather than an anecdote.**
      (a) **PAIR THE DESIGN — probably the single biggest win.** The launch is
      the confounder, so run EVERY arm inside EACH launch and difference
      within-launch; the launch effect then cancels and the relevant variance
      collapses to the within-launch component, which is a few steps. Today
      `eval_in_sim.py` takes one `--ctrl-dir` per invocation and structurally
      cannot do this. Fixing that plausibly beats accepting ~120 launches for
      a 20% effect by an order of magnitude.
      (b) **STOP USING THE MEAN — the outcome is right-censored.** `steps` is
      capped at `--max-steps` (600) and completions sit exactly on the cap, so
      mean and sd are biased toward it and understate upper spread; if two
      arms differ in how often they hit the cap, the censored mean can move
      OPPOSITE to the true one. Report a completion RATE (binomial) plus
      MEDIAN steps instead.
      (c) **Quote the CV with its interval.** CV 0.553 comes from n=7
      (df=6): the chi-square 95% CI is CV ∈ [0.36, 1.22], so "~5 launches for
      a 2× effect" is really 2-23, "~19 for 50%" is 8-93, "~120 for 20%" is
      50-581. Use the table to choose between "a handful" and "a hundred",
      never to certify "we ran 5, therefore powered" — re-estimate CV from the
      actual launches first. **The conclusion that survives regardless: even
      at the optimistic end of the CV interval (0.36), n=1 resolves only
      2.43×, and every retracted difference was under 1.85× (342.4/185.6 =
      1.845).**

- [ ] **M1.4b (NEW, 2026-09-01): design the printable track layout.**
      Evan is drafting in 3dstreet.app (`.mcp.json` wires
      `3dstreet-mcp`). **Scope split, because the tool only covers
      half of it:** 3DStreet does street CROSS-SECTIONS — linear
      segments plus 90/T/dead-end intersections, no curved streets,
      real-world units — so use it for marking design, dash pattern,
      sign placement and the portfolio render. **Keep the figure-8
      plan-view geometry in a dimensioned plan**, where the corner
      radius is checkable. Done when: a dimensioned plan exists that
      fits the (still unstated) floor space at ~300 mm lanes with
      corner radii >= the MEASURED turn radius, and a marking sheet
      is ready to print. **Floor space ANSWERED 2026-09-01: 3.0 x 3.0 m**,
      which fits the full 500-670 mm corner range at either car width.
      Still BLOCKED on (b) the B3 turning test — corner geometry must not be
      committed before it** (Appendix L, AM.2).
      **UPDATE 2026-09-02:** car width is now MEASURED (T1) and **max steer is
      confirmed at 32°** (Appendix BQ), where 32° is the wheel's DEVIATION from
      straight ahead — Evan measured with 90° = straight, angle = 90 − protractor
      reading, and reading it as 58° instead is a **2.6× error**. That gives
      `R_min = wheelbase / tan(32°)` = **1.600 × wheelbase**, so **wheelbase is
      the single remaining input** — and it is blocked on parts. For reference the
      standing ~330 mm estimate implies a ~206 mm wheelbase, so the frozen
      500-670 mm corner band probably does NOT shrink. **This still does not
      close T2**, which asks for an EMPIRICAL turning test on the rolling
      chassis; a geometric radius is better than arithmetic-on-estimates but is
      not the measurement the task names.

## 6b. EXECUTION PLAN (dated 2026-08-05, approved by Evan — schedules the tasks above; adds no new milestones)

**Why this exists:** §6 says WHAT to build and in what order. This says WHEN,
against a real deadline, and who does which part. Approved 2026-08-05 after
Evan set the deadline and confirmed the portfolio context.

~~**THE DEADLINE (new constraint, 2026-08-05): EA/ED college applications,
~Nov 1 2026** — 12.5 weeks out.~~ **SUPERSEDED 2026-08-05 ~23:10 (Appendix
N): the hard deadline is REGULAR DECISION, ~Jan 1-15 2027; Nov 1 2026 is a
SOFT milestone.** **Nov 1 still targets SIM-POC + M3** (a real BC-driving car
+ a sim-trained world model is a complete application story), and
**M4-on-real-logs moves from STRETCH to comfortably in scope for RD** — it
lands as an application update or interview material if it slips past Nov 1.
Anything that threatens M3-by-mid-October is escalated to Evan, not absorbed
silently.

**PORTFOLIO CONTEXT (2026-08-05):** this is **1 of 5 concurrent portfolio
projects** (ServeLocal, two trading projects, this, a World Models research
project). Consequences that bind execution:
- Assume **~2-3 sittings/week here**, not full attention. One task per
  sitting, always ending at a done-check — nothing left half-open.
- **Evidence banks at milestone completion, not in October.** Photos, video,
  measured tables go into the record the day they happen; nothing is
  reconstructed from memory at application time.
- **C3-C5 and M4 double as World-Models-research substrate** — capture
  configs, measured numbers, and limitations in the record so that project
  consumes them without re-running anything.

**THREE PARALLEL LANES.** A = procurement (Evan) · B = physical/CAD (Evan's
hands, my CAD support) · C = software/SIM-POC (me; costs Evan no sittings).
Lane C is why the shipping window isn't dead time.

| Week | Dates | Targets |
|---|---|---|
| 0 | Aug 5-10 | A1 checklist + A2 orders · **B1 coupon printed+measured** · C1 venv+sim |
| 1 | Aug 10-17 | B2 inventory · B3 donor measured · B4 CAD starts · C2 corpus · C3 V+M+C |
| 2 | Aug 17-24 | Parts arrive · motor calipered → B5 · B4 printed+fitted · **C4 VRAM boundary measured** |
| 3 | Aug 24-31 | B6 assembly → **M1 done** · C5 → **SIM-POC done (portfolio piece banked)** |
| 4 | Aug 31-Sep 7 | B7 bench bring-up + power integration (school starts — weekend cadence) |
| 5-6 | Sep 7-21 | Teleop + logging → **M2 done**; track defined; first real laps |
| 7-9 | Sep 21-Oct 12 | M3 baseline + PyTorch BC + lane-seg + 3-lap eval → **M3 done = Nov-1 story complete** |
| 10-12 | Oct 12-Nov 1 | **M4 stretch window** (code already exists from lane C) |
| post | Nov-Jan | M4 for RD update · task 20 writeup · M5 optional |

**Float ≈1-2 weeks, in weeks 4-6, shared with four other projects.** The
design absorbs it: Nov 1 needs only weeks 0-9.

**SCHEDULE STATUS 2026-09-02 — week 4 of the table above — and this is the
ESCALATION the plan itself requires.** Lane C is AHEAD: SIM-POC P1-P6 complete
and banked 2026-08-13, and the Uno actuation firmware — not in this plan at
all — runs on the board. **Lanes A and B are ~4 weeks BEHIND:** nothing
ordered (A2 targeted Aug 7), the coupon not printed (B1 was week 0), the
donor only partly measured (B3), no CAD started (B4), M1 not done (was
week 3). The plan says "anything that threatens M3-by-mid-October is
escalated to Evan, not absorbed silently." **M3 by mid-October is now
threatened:** with parts unordered on Sep 2 and a ~1-2 week ship, M1 cannot
complete before ~late September, which pushes M2 into October and M3 past
the Nov 1 soft target. The hard RD deadline (~Jan 1-15 2027) is **not** yet
threatened. **The two moves that unstick the schedule are both Evan's and
both cheap in time: print the coupon (needs no parts) and place the order.**
The float has been spent.

**Lane A — procurement (Evan, ~45 min then waiting).** A1 pre-order checks
BEFORE checkout: power bank label reads 5V/3A · **count the diff ring teeth
(28 = 62821, 24+16 = 6573)** — sets CAD mesh centres · confirm a 12-tooth
bevel (ideally also a 20t double-bevel) is in the bin, else ~$3 add · which
tires · **ask dad re: soldering iron+solder, multimeter, SD reader**
(assumed owned 2026-08-05; any "no" is +$8-40 and is SHOP TOOLING, not car
BOM — Evan decides whether the $200 ceiling covers it) · re-check prices.
A2 consolidated orders (target Fri Aug 7), 4 vendors, $15-25 shipping. A3
log arrivals + price deltas.

**Lane B** = existing tasks 2-11, re-ordered so B1(=task 3, the coupon) runs
FIRST because it gates every printed dimension, and task 6's motor cradle
stays parametric until the real motor is calipered.

**Lane C** = SIM-POC P1-P5 below, then the same code serves M3 and M4.

**COMMIT AUTHORIZATION (granted by Evan with this plan, 2026-08-05):** commit
at each task's done-check, per-task, message naming the task ID and its
verification result. **Push still requires Evan's explicit say-so.**

## 7. HANDOFF NOTES

**Read first, in order:** `HANDOFF.md` → this file →
`docs/research/2026-07-23_sensor-compute-stack.md` → record front-matter.
**Work order:** M1 → M4 strictly (M5 parallel-optional). One task per
sitting; finish (done-check + record entry) before the next.
**Gotchas that will bite you:**
- ~~Pi 5 + battery: standard USB-PD won't give 5V/5A (PMIC PPS bug,
  rpi-eeprom #497) — UBEC into GPIO is the path; it bypasses the input
  fuse, so the buck must be clean. Never a phone power bank.~~
  **RETRACTED 2026-07-23 ~17:59, un-struck here until the 2026-08-06 cold
  audit caught it (F15).** The Pi 5 accepts **5V/3A with only a 600 mA USB
  peripheral cap**, and this build has no USB peripherals — so the chosen
  architecture is the OPPOSITE of this line: a **USB power bank feeds the Pi
  alone**, and a separate 2S pack feeds motor + servo, sharing only ground.
  See **`hardware.md`** (`gotchas.md` was SPLIT 2026-09-02 into
  `hardware.md` / `track.md` / `sim-harness.md` and is now only a router)
  and `docs/research/2026-07-23_power-system.md`.
- Lego pin holes print tight: ~5.1mm pin fit / 5.3-5.6mm rotating bore,
  but CALIBRATE ON THIS PRINTER (task 3) before cutting chassis parts.
- ~~Don't drive Powered Up motors from a raw H-bridge (loses encoder, fights
  thermistor). PF motors only on the TB6612; PU motors only via Build HAT.~~
  *(Stale since 2026-07-23: Evan owns no Lego motors, the drive is a Pololu
  N20 with its own encoder, and the Build HAT is rejected. Struck 2026-09-02,
  kept for history.)*
- L298N is banned (1.4-3V drop wastes the ~~9V~~ **7.4 V** rail). MPU6050 is
  EOL — if an IMU enters at M4, it's ICM-20948 or BNO055.
- **TB6612 `STBY` is pulled LOW internally** — unwired, the motor is dead,
  not degraded. It is D10. And `STBY` low is a COAST, not a stop: brake first,
  then drop it. (2026-09-02, `hardware.md`)
- **The steering coupler sees ~4× the drive coupler's torque, and a printed
  cross-axle stub FAILS there** (SF 0.57-0.96). Grip a real Lego axle.
  (2026-09-02, Appendix BV)
- **Opening the serial port RESETS the Uno.** Never auto-arm or auto-calibrate
  on boot — "every boot" means "every Pi reconnect". (2026-09-02)
- **A floating analog pin reads near FULL SCALE, not zero** (10,164-10,266 mV
  measured across runs). Any sensor guard needs an upper implausibility band.
  (2026-09-02)
- DonkeyCar needs 64-bit Bookworm + Python 3.11; its trainer is TF/Keras —
  the custom-model tasks exist because the portfolio story is PyTorch.
- Sim-RL policies that win in sim can lose on hardware
  (F1TENTH/RoboRacer) — that's WHY M5 is optional and M4 is offline-on-real-
  logs. Don't "helpfully" re-promote sim-RL.
- Prices in the brief are 2026-07-23 and volatile (Pi RAM shortage) —
  re-verify at purchase time.
