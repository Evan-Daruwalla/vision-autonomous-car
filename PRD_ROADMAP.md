# Autonomous Car Project — Build & AI PRD & Roadmap

**Written 2026-07-23 by Claude (Fable), first session, from the 2026-07-23
research brief. Standing document — the executing model works through TASK
BREAKDOWN top to bottom, one task at a time, and checks off SUCCESS
CRITERIA.**

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
  gate answer (a), on his own instruction). Final BOM ≈ **$176-179 +
  shipping**, inside the $200 ceiling. Itemised in `docs/BOM.md`. One part
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
5. **CAD: front steering module.** Printed frame holding the Lego steering
   geometry + servo mount accepting MG90S AND MG996R footprints + printed
   servo-horn→Lego-axle link (adapt Printables 61922/147626). Done: STL
   exported, printed, Lego parts seat without force.
6. **CAD: rear drive module.** Diff mounts, PF motor cradle, axle bores at
   coupon-calibrated size (PETG). Done: printed; axle+diff spin freely by
   hand with motor engaged.
7. **CAD: chassis plate.** Bays for Pi, LiPo (low, central), TB6612+UBEC,
   camera mast with adjustable pitch, reserved RPLIDAR C1 footprint,
   front/rear module attachment (real Lego pins/beams as load path where
   the coupons say printed holes are marginal). Done: full assembly
   printed + test-fit; M1 success criterion checked.

### M2 — Electronics + teleop

8. ~~**Purchase list — BLOCKED-ON-EVAN.** Final BOM from brief §Ranked
   options (+ SD card, PF 8886 sacrificial cable if not owned).~~
   (superseded 2026-07-23 ~20:46 — the BOM is now written and complete)
   **Purchase — BLOCKED-ON-EVAN.** `docs/BOM.md` is final at ≈$176-179 +
   shipping. Before ordering, Evan verifies the four items in that file's
   "Verify before ordering" section (power-bank output rating, which
   differential he owns, which tires, and current prices). Done: order
   placed by Evan; arrival + any price deltas noted in the record.
9. **Bench bring-up.** Pi OS (64-bit Bookworm), SSH, camera test; TB6612 +
   PF motor on bench PSU; servo sweep test. Done: each subsystem's real
   output (photo/log) in record.
10. **Power integration.** LiPo + UBEC + split rails on the chassis;
    measure 5V rail under motor stall + Pi load. Done: no brownout/UV
    warning in `vcgencmd` during stall test; measurements recorded.
11. **Teleop + logging.** DonkeyCar install, web/gamepad teleop, tub
    recorder verified (images + steering/throttle synced). Done: M2 success
    criterion (full-session drive + ≥10 readable laps).

### M3 — Behavioral cloning

12. **Track + dataset.** Define the training track (tape on floor);
    collect 10-20 clean laps. Done: dataset size + sample frames in record.
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

## 7. HANDOFF NOTES

**Read first, in order:** `HANDOFF.md` → this file →
`docs/research/2026-07-23_sensor-compute-stack.md` → record front-matter.
**Work order:** M1 → M4 strictly (M5 parallel-optional). One task per
sitting; finish (done-check + record entry) before the next.
**Gotchas that will bite you:**
- Pi 5 + battery: standard USB-PD won't give 5V/5A (PMIC PPS bug,
  rpi-eeprom #497) — UBEC into GPIO is the path; it bypasses the input
  fuse, so the buck must be clean. Never a phone power bank.
- Lego pin holes print tight: ~5.1mm pin fit / 5.3-5.6mm rotating bore,
  but CALIBRATE ON THIS PRINTER (task 3) before cutting chassis parts.
- Don't drive Powered Up motors from a raw H-bridge (loses encoder, fights
  thermistor). PF motors only on the TB6612; PU motors only via Build HAT.
- L298N is banned (1.4-3V drop wastes the 9V rail). MPU6050 is EOL — if an
  IMU enters at M4, it's ICM-20948 or BNO055.
- DonkeyCar needs 64-bit Bookworm + Python 3.11; its trainer is TF/Keras —
  the custom-model tasks exist because the portfolio story is PyTorch.
- Sim-RL policies that win in sim can lose on hardware
  (F1TENTH/RoboRacer) — that's WHY M5 is optional and M4 is offline-on-real-
  logs. Don't "helpfully" re-promote sim-RL.
- Prices in the brief are 2026-07-23 and volatile (Pi RAM shortage) —
  re-verify at purchase time.
