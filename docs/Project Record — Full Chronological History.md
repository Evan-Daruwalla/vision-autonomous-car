# Project Record — Full Chronological History

Written 2026-07-23. Every entry is grounded in one of:
- The live session transcript of 2026-07-23 (project conception — no git
  history, files, or artifacts existed before this date)
- Files created during a session, named explicitly in the entry

Sections where a timestamp can't be precisely verified are explicitly
marked. No fabricated metrics, dates, or file names.

---

# How this document is organized

This record has two parts plus this navigation front-matter:

- **Part I — Phases** (`##` headings): the original consolidation, written in
  one pass from real history at bootstrap time.
- **Part II — Appendices A–…** (`#` headings): chronological addenda appended
  one session at a time per the `CLAUDE.md` cadence rule. **Append-only** —
  prior appendices are never edited.

The two heading levels encode that distinction (Phases are sections of the
original record; Appendices are top-level addenda). Sub-sections use the
`Letter.Number` convention (e.g. `B.7`, `Q.2`).

The sections below are reading aids. The authoritative detail always lives in
the dated entry, not the digest.

---

# Table of Contents

**Part I — Original record (2026-07-23)**
- [Phase 0 — Conception and bootstrap](#phase-0--conception-and-bootstrap-2026-07-23) (~07-23)

**Part II — Appendices (chronological)**
- [A — Research workers report: sensors, AI pipeline, electronics](#appendix-a---research-workers-report-sensors-ai-pipeline-electronics-2026-07-23-1612-cdt) (07-23)
- [B — Compute verdict, spot-checks, brief compiled, PRD + HANDOFF written](#appendix-b---compute-verdict-spot-checks-brief-compiled-prd--handoff-written-2026-07-23-1617-cdt) (07-23)
- [C — M1.1 gate answered; owned-motor premise voided; 8GB VRAM constraint](#appendix-c---m11-gate-answered-owned-motor-premise-voided-8gb-vram-constraint-2026-07-23-1721-cdt) (07-23)
- [D — No battery/charger owned; budget over ceiling; servo-vs-motor clarified](#appendix-d---no-batterycharger-owned-budget-over-ceiling-servo-vs-motor-clarified-2026-07-23-1732-cdt) (07-23)
- [E — M4 VRAM gate resolved; "24GB" figure RETRACTED; M4 restructured](#appendix-e---m4-vram-gate-resolved-24gb-figure-retracted-m4-restructured-2026-07-23-1739-cdt) (07-23)
- [F — Drive motor resolved; Lego motors rejected on physics; coupler-torque premise corrected](#appendix-f---drive-motor-resolved-lego-motors-rejected-on-physics-coupler-torque-premise-corrected-2026-07-23-1747-cdt) (07-23)
- [G — Power system resolved; Pi 5A premise overturned; budget forces a cut](#appendix-g---power-system-resolved-pi-5a-premise-overturned-budget-forces-a-cut-2026-07-23-1759-cdt) (07-23)
- [H — Budget settled (4GB + owned bank); BOM final; missing camera cable caught](#appendix-h---budget-settled-4gb--owned-bank-bom-final-missing-camera-cable-caught-2026-07-23-2046-cdt) (07-23)

---

## Phase 0 — Conception and bootstrap (2026-07-23)

**2026-07-23 (afternoon, ~16:00 CDT).** Project conceived by Evan in the first
session, in an empty directory (`D:\ClaudeCode\Autonomous Car Project`). The
stated idea, in Evan's terms: design a mini autonomous car in CAD and 3D print
it, reusing Lego Technic parts (wheels, body parts, a working differential
from an owned set, and a copied Lego steering mechanism with motors added) to
keep cost low and guarantee mechanical fit; sensing "prob use tesla style
vision AI but LiDar or other sensor suites I'm open to ideas"; then train the
autonomous AI on computer using a world model, then train it in real life.

Claude's initial assessment (given before any files existed):
- **Main flaw flagged:** "train a world model, then real life" as a single
  step is research-grade scope. Proposed staging instead: behavioral cloning
  first (DonkeyCar-style camera→CNN imitation), then RL in simulator, world
  model as stretch — each stage independently portfolio-worthy.
- Steering should use a hobby servo (position feedback) driving the Lego
  steering rack, not a plain Lego motor.
- Camera-only sensing recommended for indoor mini scale; LiDAR deferred,
  chassis reserves a mount.
- Compute fork (Pi 5 vs Jetson Orin Nano vs offboard) identified as the first
  hardware decision, driving chassis size, battery, and budget.
- FDM-vs-Lego tolerance mismatch flagged: plan test coupons for pin/axle
  bores before committing chassis prints.

Evan approved option 3 — research brief first, then doc-system bootstrap with
a staged PRD — via `/project-memory then 3 using /opus-workers on high`.

Bootstrap actions this session (2026-07-23, from ~16:04 CDT):
- `.claude/pm-cadence.json` created with skill defaults (record every 3
  prompts; handoff/PRD/bins event-driven). Hand-created — the autoinit hook
  did not fire on a slash-command invocation.
- Four Opus research workers launched in parallel (compute platform, sensor
  suite, electronics/Lego integration, AI software pipeline), each with a
  pre-registered review rubric per the opus-workers skill.
- This record created (Part I written from the live session — the only
  ground truth that exists; nothing seeded from git because no git history
  exists yet).

**HONEST OPEN ITEM (at time of writing Phase 0):** research workers still
running; HANDOFF.md and PRD_ROADMAP.md not yet written (blocked on research
results). No git repository initialized yet. No hardware purchased; no CAD
started.

# Appendix A - Research workers report: sensors, AI pipeline, electronics (2026-07-23, ~16:12 CDT)

**WHAT:** Three of the four Opus research workers returned (sensors ~16:08,
AI pipeline ~16:10, electronics ~16:12 CDT); compute worker still running.
All three pass the pre-registered rubric on structure (multi-sourced claims,
2025-26 prices, honest gaps flagged). Spot-checks (rubric R4) deferred until
all four are in. Cadence note: this entry fires on the prompt-#3 cadence hit
(the counter counted background task notifications as prompts — noted, not
hidden).

**Key verdicts carried forward to the brief/PRD (full sourced detail will
live in docs/research/, this is the digest):**
- Sensors: Pi Camera Module 3 Wide ($35, 120° diag) for M2-M3 — every
  successful platform runs >=120° FOV; no evidence rolling shutter hurts at
  1-3 m/s (reasoned inference, tagged); depth/LiDAR deferred (RPLIDAR C1 $99
  mount reserved); MPU6050 is EOL — ICM-20948 $20 / BNO055 $35 are the 2026
  IMU parts; Powered Up motors carry free 1-degree encoders readable via Pi
  Build HAT.
- AI pipeline: DonkeyCar alive (5.3.0, 2026-03-29, Pi 5 fix; TF/Keras
  trainer) — use for plumbing, swap in own PyTorch model; JetRacer aging out.
  STAGING AMENDMENT recommended by evidence: sim-RL is the riskiest rung
  (F1TENTH/RoboRacer transfer failures) — promote offline RL / offline world
  model on own real driving logs as the M4-M5 spine; sim-RL (gym-donkeycar or
  Wheeled Lab/Isaac Lab, arXiv:2502.07380) becomes parallel/optional; thread
  lane-segmentation preprocessing from M3.
- Electronics: reuse owned PF L/XL motor through the Lego differential
  (native coupling, $0) + TB6612FNG driver ($4.95); L298N rejected (1.4-3V
  drop); MG90S servo likely adequate (flagged: sized by analogy, MG996R
  fallback); single 2S LiPo, split rails, 5V UBEC into GPIO (Pi 5 USB-PD
  PPS negotiation bug documented, rpi-eeprom #497); print pin holes ~5.1mm,
  rotating axle bores 5.3-5.6mm, PETG for bores.
- Cross-worker tension to resolve in synthesis: sensors worker's "free
  encoders" assumes Powered Up motors + Build HAT; electronics worker
  recommends PF motors + H-bridge, which has NO encoder. The fork changes
  the M4 odometry plan.

**HONEST OPEN ITEM:** compute worker (Pi 5 vs Jetson vs offboard) not yet
returned; no spot-checks run yet; brief not yet compiled; HANDOFF.md and
PRD_ROADMAP.md still not written.

# Appendix B - Compute verdict, spot-checks, brief compiled, PRD + HANDOFF written (2026-07-23, ~16:17 CDT)

**WHAT:** Fourth worker (compute) returned ~16:14 CDT. Reviewer ran the
rubric's spot-check requirement — one load-bearing claim per worker
re-verified against its primary source (WebFetch, 2026-07-23):

| Claim | Worker | Primary source checked | Result |
|---|---|---|---|
| Camera Module 3 Wide = 120 deg diagonal, from $25 | sensors | raspberrypi.com product page | MATCH (page confirms 75 deg std / 120 deg wide; per-variant price not broken out on page — the $25/$35 split is from the secondary source, tagged) |
| DonkeyCar 5.3.0 released 2026-03-29 w/ Pi5 fix | software | GitHub releases API | MATCH (exact date + "Disable camera alignment for Pi5 compatibility") |
| TB6612FNG $4.95, 4.5-13.5V, 1A cont / 3A peak | electronics | pololu.com/product/713 | MATCH on all four figures |
| Pi 5 prices 4GB $70 / 8GB $95, LPDDR4-driven | compute | raspberrypi.com news 2025-12-01 | MATCH incl. the stated cause |

All four survived. No worker needed a redo round.

**Compute verdict (H1 supported, H2 refuted-on-rationale, H3 mixed):** Pi 5.
BC-stage CNN runs ~41 FPS on Pi 5 CPU (MobileNetV2 proxy) against a 20 Hz
DonkeyCar loop cap, so no accelerator is needed. Jetson's "avoid
re-platforming" premise fails because ALL training (BC, offline RL, Dreamer)
lives on the desktop GPU and deployment is always a small encoder+actor net;
JetRacer targets the Jan-2026-EOL original Nano and was never ported to
Orin, so Jetson is less turnkey in 2026, not more. Offboard compute measured
at 100-250 ms round trip vs a 50 ms budget for 20 Hz — good for teleop and
data collection, wrong for the autonomous loop.

**WHY the staging changed:** the software worker surfaced RLJ-2025
F1TENTH/RoboRacer results where sim-winning RL policies swerve and
underperform classical control on real hardware. Making sim-RL a mandatory
gate risks burning the middle of the project on a documented failure mode.
Offline world model / offline RL on the car's own logs reuses the BC dataset,
has no sim2real gap, and has no verified hobbyist precedent found - so it is
both safer and a stronger portfolio claim. Sim-RL survives as optional M5.

**HOW:** brief compiled to docs/research/2026-07-23_sensor-compute-stack.md
(TL;DR + findings by theme + ranked options + what-would-change-this +
condensed sources with gaps preserved). PRD_ROADMAP.md written with GOAL
block, scope guard, 6 milestones, 20 numbered tasks with done-checks, and
HANDOFF NOTES gotchas. HANDOFF.md written as the live snapshot with the
workstream table.

**Cross-worker tension resolved into the PRD rather than papered over:** the
sensors worker's free-odometry finding (Powered Up motors carry 1-degree
encoders readable via Build HAT) conflicts with the electronics worker's
drive recommendation (PF motor + H-bridge, no encoder). Both paths are
documented; which one applies depends on Evan's actual motor inventory, so it
became decision-gate item (b) instead of a guess.

**HONEST OPEN ITEMS:** (1) The amended staging is Claude's recommendation
from evidence - Evan has NOT ratified it; the PRD says so in two places.
(2) Nothing physical has been built, printed, bought, or measured - every
"fits/works" statement in the brief and PRD is desk research, explicitly
untested on this car. (3) M4 tasks are deliberately coarse and must be
refined by a dated PRD append once M3 exists. (4) No git repository
initialized. (5) Cadence: this session ran record entries at Appendix A
(prompt-3 hook) and here; handoff written at session end per config.

# Appendix C - M1.1 gate answered; owned-motor premise voided; 8GB VRAM constraint (2026-07-23, ~17:21 CDT)

**WHAT:** Evan answered the M1.1 decision gate in full: (a) Pi 5 **8GB**;
(b) Lego motors owned: **none**; (c) training GPU: **RTX 3060 Ti, 8GB
dedicated VRAM, 16GB shared**; (d) budget ~$200 **approved**; (e) amended
staging + scope guard **ratified**. The gate is closed; two of the five
answers invalidated prior plan assumptions and both were escalated to
research rather than guessed around.

**WHY this mattered more than a routine gate:**

1. **The owned-motor premise is void.** Appendix A/B recorded the
   electronics worker's verdict "reuse an owned PF L/XL motor through the
   Lego differential — native coupling, $0 marginal cost." That verdict was
   entirely conditional on Evan already owning a Power Functions motor. He
   does not. The drive motor is now a PURCHASE decision, and — the part that
   actually blocks work — its physical dimensions define the rear-drive
   module's motor cradle, so PRD task 6 (rear drive module CAD) cannot start
   until the motor is chosen. Logged as new PRD task M1.1b.
   *Residual ambiguity, flagged not resolved:* "none" may mean none of the
   PF/Powered-Up families specifically. EV3/NXT/9V-Technic motors, if owned,
   would reopen the free-encoder odometry path. Routed to the M1.2 inventory
   task rather than assumed either way.

2. **8GB VRAM is below the figure the brief cited for the capstone.** The
   research brief carried a single-source practitioner claim that DreamerV3
   wants ~24GB for 64x64 vision (~12GB state-only). The 3060 Ti has 8GB. M3
   behavioral cloning is unaffected (small CNN, trains in minutes). M4 — the
   ratified capstone — is the exposure. The "16GB shared" figure is Windows
   host-RAM spillover, which thrashes rather than OOMs and is therefore not
   a mitigation. Logged as new PRD task 16a (architecture + VRAM gate)
   BEFORE the existing coarse M4 tasks 16-19.

**HOW:** Two Opus research workers launched in parallel ~17:22 CDT with
pre-registered rubrics: (i) drive-motor selection across four paths (N20
gearmotor + printed Lego-axle adapter · used PF motor from the secondary
market · new Powered Up 88013/88014 + Pi Build HAT for encoder odometry ·
small RC brushed motor), required to show gearing and torque math against
the real Lego differential reduction and wheel diameters for a 1-2 m/s
target, verify stall current against the TB6612FNG's 1A/3A limits, and
return CAD-grade dimensions; (ii) 8GB-VRAM feasibility for an offline world
model, covering DreamerV3 size presets and real 8-12GB training reports,
offline model-based RL codebases, the far smaller Ha & Schmidhuber
VAE+MDN-RNN architecture, 8GB mitigations, required dataset size, and
Colab/Kaggle escalation.

**Note on the opus-workers routing:** Evan switched the session model to
Opus 4.8 partway through this session (previously Fable). Opus workers are
therefore no longer a strictly-cheaper tier than the reviewer, so the
skill's cost rationale has lapsed; they were kept for parallelism and for
keeping high-volume research output out of the main context, which are real
but different justifications. Stated rather than quietly ignored.

**PRD edits applied under the mutability rules** (struck in place with dated
reasons, never deleted): the "What exists" inventory bullet, the stack
constraint line, and the budget line were each struck and superseded with
dated replacements; task 1 was struck and marked done with its answers; new
tasks 1b and 16a appended; scope guard and objective marked RATIFIED with
timestamp. Budget arithmetic recorded: ~$178 committed of the ~$200
ceiling, leaving ~$22 for the motor, with an unbudgeted LiPo balance charger
(~$25) flagged as a possible overrun pending the M1.2 inventory.

**HONEST OPEN ITEMS:** (1) Both research questions are unresolved at the
time of writing — workers still running. (2) Still nothing physical built,
printed, bought, or measured; every hardware claim remains desk research.
(3) M4 tasks 16-19 remain deliberately coarse pending 16a and M3. (4) No git
repository initialized. (5) Whether the ~$22 motor budget is realistic is
itself an output of the in-flight research, not a verified figure.

# Appendix D - No battery/charger owned; budget over ceiling; servo-vs-motor clarified (2026-07-23, ~17:32 CDT)

**WHAT:** Evan reported two things: (1) he owns **no LiPo battery and no LiPo
charger**; (2) "we'll need 2 motors, 1 for power and 1 for steering."

**WHY (1) matters — the budget now provably exceeds the ceiling.** The
Appendix C arithmetic carried a 2S LiPo at ~$12 and flagged a possible
~$25 charger as a WATCH item pending inventory. That watch item has now
resolved to the bad branch, and the battery is not a line item but a whole
subsystem (cells + charger + connectors + any safety equipment). Recomputed
against the ~$200 ceiling:

| Line | Cost |
|---|---|
| Pi 5 8GB | $95 |
| Camera Module 3 Wide | $35 |
| TB6612FNG | $5 |
| MG90S servo (steering) | $5 |
| UBEC | $8 |
| SD card | $10 |
| wire/caps/connectors | $8 |
| **Committed subtotal** | **$166** |
| Drive motor (M1.1b, in research) | ~$5-30 |
| Battery + charger (NEW, in research) | ~$25-40 |
| **Realistic total** | **~$196-236** |

So the build is at or over the ceiling depending on both in-flight research
answers. The largest single lever identified: **Pi 5 8GB -> 4GB saves $25**,
and 4GB is DonkeyCar's stated minimum with onboard work being
inference-only. Not applied — Evan chose 8GB at the M1.1 gate and only he
can revise it.

**WHY (2) needed a correction rather than an edit.** The steering actuator
in the plan is an **MG90S hobby servo, already in the BOM at $5** — it is
not a second bare DC motor. A servo is a motor plus a potentiometer and a
control loop, so it accepts a commanded ANGLE and holds it. A plain DC motor
has no position feedback: it can only be told "turn this way," so the
steering angle would be unknown and uncontrollable. That is fatal to the
whole project, because both the behavioral-cloning model (M3) and any
world-model policy (M4) emit a steering ANGLE as their output — there is
nothing for that output to command without position feedback. The
"two actuators" count is correct and was already budgeted; the "two motors"
framing is the part that would have been an error if implemented. Recorded
here because the correction is load-bearing, and the original 2026-07-23
~16:00 CDT assessment (Phase 0) had already flagged exactly this trap.

**HOW:** A third Opus research worker launched ~17:33 CDT on the power
system, with a pre-registered rubric. Its pivotal question is whether the Pi
5 actually needs 5V/5A for THIS workload (CSI camera, no USB peripherals,
CPU inference) or whether ~3A suffices — because if 3A is adequate, cheap
5V/3A sources including USB power banks become viable and the whole power
architecture (and its cost) changes. It also compares complete kits across
2S LiPo / 18650 Li-ion / NiMH / split-source power-bank / boost-buck /
LiFePO4 on cost, safety, weight, runtime and complexity, with runtime math
shown, and must answer directly whether anything safe fits the remaining
budget or what has to be cut.

**Effect on the in-flight drive-motor research (checked, not assumed):** its
prompt specified a 2S LiPo at 6.4-8.4V. Every alternative chemistry under
consideration lands near the same nominal voltage (2S 18650 7.4V, 6-cell
NiMH 7.2V), so the motor selection and its gearing/torque math remain valid.
The worker was left running rather than restarted.

**HONEST OPEN ITEMS:** (1) All three research questions — drive motor, 8GB
VRAM world-model architecture, power system — are unresolved at time of
writing. (2) The budget overrun is arithmetic from estimates, not quotes; it
will firm up when the motor and power research return. (3) Still nothing
physical built, printed, bought, or measured. (4) No git repository
initialized. (5) Cadence: this entry fires on the prompt-#6 hook.

# Appendix E - M4 VRAM gate resolved; "24GB" figure RETRACTED; M4 restructured (2026-07-23, ~17:39 CDT)

**WHAT:** The world-model VRAM worker returned (~16 min runtime, 86 tool
calls). PRD task 16a is resolved. Brief saved to
`docs/research/2026-07-23_world-model-8gb-vram.md`. M4 tasks restructured
from four coarse items into five concrete ones.

**CORRECTION TO A PRIOR ENTRY (this is the important part).** Appendix B and
the 2026-07-23 ~16:17 research brief carried the claim that DreamerV3 wants
"~24GB VRAM for 64x64 vision (single practitioner source)". That figure was
tagged single-source at the time, correctly. This pass **could not locate
that source at all**, and established that **no published VRAM-per-size
table for DreamerV3 exists anywhere**. The figure is **RETRACTED**. It was
also directionally misleading: it evidently described the XL/size200m end,
and does not generalise downward. Per the append-only rule this correction
is a new entry, not an edit to Appendix B; the research brief itself carries
an inline dated CORRECTION block pointing here.

Lesson recorded rather than glossed: the original claim entered the record
properly tagged, and the tag is what made it cheap to overturn. Untagged, it
would have silently shaped the M4 plan.

**VERDICT: feasible with constraints.** 8GB works at DreamerV3 **S-scale
(~18M params)** or below at 64x64. It does not work at L/XL - which is what
every default config in every repo hands you (danijar's default is
size200m). Load-bearing measurements, all single-user reports and tagged as
such: XL-scale crafter on an 8GB GTX 1080 thrashed at 0.025 Hz against ~11
Hz expected, while S-scale on the SAME card ran at a usable 1.4 Hz; XL at
batch 8 measured 13.37 GiB; size200m OOM'd even on a 24GB RTX 3090.

**Two verified implementation findings that change the plan:**
1. **Use `NM512/dreamerv3-torch`, not danijar's JAX reference.** Reviewer
   spot-checked both claims against primary sources (2026-07-23 ~17:39):
   the PyTorch port's `dreamer.py` contains `offline_traindir` /
   `offline_evaldir` and `if not config.offline_traindir: prefill = ...`,
   i.e. setting it skips environment prefill entirely - CONFIRMED verbatim.
   JAX's official install table lists Windows x86_64 NVIDIA GPU as "no" and
   WSL2 as "experimental" - CONFIRMED verbatim. The JAX reference also has
   no offline mode at all (issue #80, closed unanswered).
2. **NVIDIA Sysmem Fallback must be disabled before training.** Since driver
   536.40 the default spills VRAM overflow into shared system RAM, turning
   an OOM into a silent ~3x slowdown (measured 4.5 s/iter vs 1.5 s/iter).
   This is precisely the "16GB shared" in Evan's spec - host RAM over PCIe
   (~25 GB/s) vs 448 GB/s GDDR6. Also established: WSL2 does NOT give more
   VRAM (no evidence found); mixed precision is not a reliable rescue (the
   one PyTorch measurement had bf16 costing 10.5 GiB MORE); gradient
   checkpointing is unimplemented in all three candidate codebases.

**WHY M4 was restructured — the sequencing change.** The worker's strongest
recommendation was not a config but an ORDER: build the small architecture
FIRST. Ha & Schmidhuber's original World Models (VAE 4.35M + MDN-RNN 0.42M +
controller 867 = ~4.77M params; "<1 hour per model on a single GPU" on 2018
hardware) is guaranteed to fit, cannot OOM, and is still a genuine world
model - it is the paper that named the field. Building it first exercises
the whole data pipeline (recording format, frame/action sync, held-out
splits, on-car eval protocol) and guarantees M4 finishes with a real result
regardless of where the 8GB boundary falls. DreamerV3-S is then attempted on
the identical dataset with the identical eval harness. Output: two
architectures, one dataset, one protocol, an honest comparison table, and a
measured VRAM boundary nobody has published. Accepted - this is a better
plan than the single-architecture attempt it replaces, and it converts the
hardware constraint from a risk into a finding.

Task 18's done-check was written accordingly: **either a trained model OR a
documented OOM boundary with the measured number counts as a pass.**

**Offline training helps for one published reason:** V-D4RL's Offline
DreamerV2 uses imagination horizon 5 instead of the online 15, stating the
reduction "is required due to the lack of online 'remedial' sampling" -
roughly a 3x cut in actor-critic rollout memory that comes free with going
offline. Their batch increase 16->64 is a data-efficiency choice and is
explicitly NOT copied here.

**Dataset size is a non-problem** (the reassuring finding): DonkeyCar's own
guidance is ~10,000 images at 20 Hz; V-D4RL's offline visual standard is
100k transitions. Derived arithmetic (not sourced): 100k frames = 83 minutes
of driving = 1.23 GB at 64x64 uint8. One person, one afternoon, indoors.

**Scale honesty for the eventual writeup:** comma.ai's driving world model
is 250M-1B params over 100k-400k minute-long segments; Dreamer 4 used 2.5K
hours of video and 256-1024 TPU-v5p. This project is five orders of
magnitude smaller. The novelty is the constraint and the measurement, not
beating anyone. PRD task 20 now says this explicitly.

**HONEST OPEN ITEMS:** (1) The S-fits-8GB claim rests on ONE user's
throughput observation with **no VRAM number reported for the S run** -
nobody has published GB-for-S. (2) Direct counter-evidence stands: DreamerV3
on **CarRacing-v2**, the closest published analogue to this project, OOM'd
on 10.91 GiB - 36% more VRAM than Evan has; the config is unstated so it
cannot be dismissed. (3) The `dreamerv3-torch` offline path was verified to
EXIST in source but not verified to RUN end-to-end with zero environment
instantiation - test before committing. (4) No published
DreamerV3-offline-on-real-small-RC-car-logs result exists, so there is no
recipe to copy for M4 as specified. (5) Nothing has been run on Evan's
machine; every VRAM number here is someone else's measurement on someone
else's config. (6) Drive-motor and power-system workers still running. (7)
Still nothing physical built, printed, bought, or measured. (8) No git repo.

# Appendix F - Drive motor resolved; Lego motors rejected on physics; coupler-torque premise corrected (2026-07-23, ~17:47 CDT)

**WHAT:** The drive-motor worker returned (~24 min, 115 tool calls) - the
longest-running of the six workers this session. PRD task M1.1b is resolved
pending Evan's purchase go. Brief saved to
`docs/research/2026-07-23_drive-motor-selection.md`.

**RECOMMENDATION: Pololu #1093, N20 30:1 HP 6V, $23.95.**

**WHY the Lego-motor question closed differently than expected.** Appendix C
recorded that Evan owning no Lego motors "voided" the reuse plan and turned
the motor into a purchase decision. The math says the reuse plan was never
viable regardless: **every Power Functions motor is too slow.** Best case
through ANY differential arrangement is PF M at **0.88 m/s**, against the
1.0 m/s floor (PF L 0.84, PF XL 0.50). Since every diff option reduces speed
further, the only fix is an added step-up layshaft - two extra gears and
more rear-module volume than the N20 route it was meant to simplify. So the
Appendix A electronics verdict ("reuse an owned PF L/XL - native coupling,
$0") would have produced a car that could not hit its own speed target. Not
owning the motors turned out to be irrelevant. Secondary-market pricing also
undercut the premise: PF motors run $19-35, i.e. the same money as a new,
fully-spec'd N20 with a datasheet and a warranty.

**Why 30:1 specifically:** available N20 no-load speeds jump 1000 -> 2000
rpm with nothing between, and the requirement band is ~430-1550 rpm. 15:1
and 10:1 fail the acceleration check outright (112% and 132-153% of stall);
50:1 tops out below 0.9 m/s. Critically the low-current **30:1 MP variant
(0.67 A stall, which would fit a single TB6612 channel) fails at 101.8% of
stall** - which is what forces the 1.6 A HP variant and, in turn, forces
paralleling both driver channels. Both channels are free because steering is
a servo, so this costs nothing.

**REVIEWER VERIFICATION (rubric requirement, run in full):**

| Check | Source | Result |
|---|---|---|
| Pololu #1093: $23.95, 1000 rpm, 0.57 kg-cm stall, 1.6 A stall, 3 mm D-shaft 9 mm, 10x12 mm | pololu.com/product/1093 | MATCH on every figure |
| Build HAT: 8V +/-10%, 48W, DC 5521; reserves GPIO 0/1/4/14/15/16/17; Trixie unsupported | raspberrypi.com Build HAT docs | MATCH verbatim incl. the Trixie warning |
| **Entire gearing + torque calculation chain** | **re-derived independently by the reviewer** | **MATCH** - wheel rpm, reduction ratios, force/torque budget, top speeds, linear current model, acceleration-from-rest, printed-coupler stresses, and the traction margin all reproduce |

The full arithmetic re-derivation was done because the rubric demanded
correct math and because these numbers drive irreversible CAD. Nothing was
taken on trust.

**A PREMISE OF MINE WAS WRONG, and is corrected here.** The 2026-07-23
~16:17 brief - and the worker prompt I wrote from it - described the printed
motor coupling as "the drive (highest-torque) joint." That is backwards. The
coupler sits UPSTREAM of the reduction, so it is the LOWEST-torque joint in
the driveline: motor stall is 55.9 mN-m, while each half-shaft downstream of
a 2.333:1 diff sees ~45.6 mN-m and the wheel hubs more still. The practical
advice survives the correction but for a different reason than I gave: a
printed Lego cross-axle stub is only **SF 2-4 in torsion at stall (6.64 MPa
against ~15-25 MPa PLA interlayer shear)**, collapsing toward 1 with sparse
infill or bad orientation - so print the coupler as a SOCKET GRIPPING A REAL
LEGO AXLE, never as a printed axle cross-profile. Second correction of the
session (after the retracted 24GB VRAM figure), and worth noting that both
were caught by workers checking my framing rather than accepting it.

**Powered Up + Build HAT rejected on five independent grounds**, two of them
verified directly by the reviewer: it requires 8V +/-10% (7.2-8.8V) at 48W
via a barrel jack, which a 2S pack sits below for most of its discharge
curve; it reserves GPIO 0/1/4/14/15/16/17 including the primary UART; it is
not supported on Raspberry Pi OS Trixie; no rpm/torque data is published for
88013/88014 anywhere, so the gearing cannot be designed on paper; and the
full Build HAT + Camera Module 3 + on-device-inference stack on a Pi 5 is
undocumented. Cost was the least of it at $64.99 against ~$22 remaining.

**Drivetrain geometry now CAD-ready** (Lego gears are metric module 1, so
pitch diameter in mm = tooth count): **config B (lower risk)** = 62.4 mm
tire 32019 + 12t bevel -> 28t ring 62821, N=2.333, mesh centres 20.0 mm
(2.5 studs), top speed 1.28 m/s, cruise 0.23 A. **Config A (faster)** =
43.2 mm tire 44309 + 20t double-bevel in-plane -> 28t, N=1.400, centres
24.0 mm (3.0 studs), 1.46 m/s - but the in-plane mesh is standard practice
without a citable set instruction for this specific ring, so it must be
verified on the physical part first.

**Budget now: $189.95** committed-plus-motor, against the ~$200 ceiling,
with the power system (M1.1c, still in research) unpriced. Projected
~$215-230.

**HONEST OPEN ITEMS:** (1) Purchase still BLOCKED-ON-EVAN. (2) Two
dimensions unverified and flagged for calipers on arrival: N20 mounting-hole
spacing (10 +/- 0.2 mm, single-source) and D-flat depth (missing entirely).
(3) Lego cross-axle rib thickness must come from an LDraw/GrabCAD model, not
eyeballing. (4) Printables 897927's coupler outputs an 8-tooth gear/pulley,
not a plain axle - confirm the real STL geometry before committing the rear
module. (5) The 1.6 A stall exceeds one TB6612 channel; the design leans on
paralleling + a PWM duty cap + a firmware stall-timeout, and real operating
currents (0.23-0.25 A cruise, ~0.9-1.0 A accel) are comfortable. (6) Power
worker still running. (7) Nothing physical built, printed, bought, or
measured. (8) No git repository.

# Appendix G - Power system resolved; Pi 5A premise overturned; budget forces a cut (2026-07-23, ~17:59 CDT)

**WHAT:** The power worker returned (~26 min, 133 tool calls) - the last of
six workers this session. PRD task M1.1c is researched; the PURCHASE remains
blocked on Evan, and one factual question must be answered by him first.
Brief saved to `docs/research/2026-07-23_power-system.md`. Cadence: this
entry also satisfies the prompt-#9 hook.

**THE PIVOTAL FINDING OVERTURNS A PREMISE CARRIED SINCE APPENDIX A.** The
2026-07-23 ~16:17 brief treated the Pi 5's 5V/5A requirement as a hard
design constraint, and built the whole battery architecture (2S LiPo + 5V/5A
UBEC into GPIO) around defeating the USB-PD negotiation bug. That framing
was wrong in its consequence. Official Raspberry Pi documentation states the
Pi 5 accepts **"5 V at 3 A (15 W) with a 600 mA peripheral limit"**
(reviewer verified verbatim, 2026-07-23 ~17:59). The 5A rating is a USB
PERIPHERAL BUDGET, not a board requirement, and the ONLY documented
consequence of a 3A supply is that 600 mA cap on the USB ports. **This build
has zero USB peripherals** (CSI camera, no USB devices), so the cap costs
nothing. Measured draw during CNN inference on a Pi 5 is **1.40 A**
(arXiv 2506.09300, USB inline meter, with a display attached - headless will
be lower); all-core stress is ~1.76 A. Cheap 5V/3A sources, including USB
power banks, are therefore back on the table, which changes the architecture
and the cost.

Three under-spec behaviours were separated that forum lore conflates:
boot-warning-only (harmless here), undervoltage throttle (only when the rail
actually sags below ~4.64 V), and brownout shutdown (rail collapse). **The
real constraint is transient rail stiffness, not amperage** - a documented
case had a Pi 5 shutting down at only ~1.5 A because of voltage drop in the
cables.

**RECOMMENDATION: split source.** USB power bank -> Pi alone; separate 2S
18650 pack -> motor + servo; single shared ground at the driver. The
reasoning is primarily SAFETY, not cost: it is the only path where the
lithium in the house is a **UL/ETL-listed consumer product with an
integrated BMS, charged from a phone charger**. Every other lithium path
puts bare cells and a hobby charger in a teenager's bedroom, which
institutional guidance (NFPA consumer tip sheet, Illinois DRS, WMU EHS, AMA)
surrounds with rules - balance-charge only, never unattended, fireproof bag,
1C max. It also structurally eliminates motor-stall brownout of the Pi
(4tronix rates separate supplies "most safe"), and deletes the DIY regulator
from the Pi's path - which matters because the strongest evidence against
the battery+UBEC approach is a documented Pi 5 getting undervoltage warnings
and WiFi instability through a 5A-rated buck, attributed to transients a
bench load never catches.

**THE FINDING THAT KILLS THE CHEAPEST OPTION:** one 5V/3A power bank
powering everything demands, on simultaneous Pi peak + servo stall + motor
stall, **4.62 A on a 3 A rail** -> current limit, rail collapse, Pi
hard-reset mid-run with the SD card mounted. Average draw (~2 A) is fine;
the stall event is the killer. Recorded explicitly so no future session
"simplifies" the design into it.

**REVIEWER VERIFICATION (rubric, run in full):**

| Check | Source | Result |
|---|---|---|
| Pi 5 accepts 5V/3A with a 600 mA peripheral limit | raspberrypi.com hardware docs | MATCH verbatim - the pivotal claim holds |
| Runtime, energy, and peak-current arithmetic | re-derived independently | MATCH on every row checked |
| Worker's motor assumptions vs the ACTUAL selected motor | cross-worker integration | Worker assumed 0.6 A running / 2.0 A stall; the selected N20 #1093 is 0.25 A cruise / 1.6 A stall. **Worker was pessimistic**, so runtime estimates are conservative and system peak drops 4.32 A -> **3.92 A**. Conclusions unchanged; the single-bank rejection survives at 4.62 A. |

The cross-worker check was run because the power worker was launched BEFORE
the motor was selected and had to assume an envelope. Confirming the real
motor lands inside that envelope is what makes the two briefs composable.

**BUDGET: the ceiling is now provably breached, and a cut is required.** The
cheapest complete SAFE power system is **$25.89 on its own** - which leaves
$0 for the motor against the ~$22 that remained. Full-build scenarios with
the motor at $23.95:

| Scenario | Total |
|---|---|
| Owns a power bank + **Pi 4GB** | **~$174** (comfortable) |
| Owns a power bank + Pi 8GB | ~$199 (at the line; shipping breaks it) |
| No power bank + Pi 4GB | ~$194-202 (at the line) |
| No power bank + Pi 8GB | ~$219-227 (over) |

Shipping across 3-4 vendors adds $15-25 unless consolidated, which pushes
every "at the line" row over. **The Pi 5 8GB -> 4GB downgrade (-$25) is now
recommended by the power research independently of the earlier budget
argument.** Not applied - Evan chose 8GB at the M1.1 gate and only he
revises it.

**NEW BLOCKING QUESTION FOR EVAN:** does he already own a USB power bank?
The entire cost case for the recommended path turns on it - $15.42 if yes
(both safest AND cheapest), $33-41 if no. This is a fact only he has.

**HONEST OPEN ITEMS:** (1) Power purchase blocked on Evan's answer about the
power bank AND on the Pi 4GB/8GB budget decision. (2) No published Pi 5
measurement exists with a CSI camera + sustained CNN loop specifically - the
1.40 A figure is one workload-class removed (display attached, no CSI
camera); budget 0.3 A for the camera. (3) Camera Module 3's isolated current
draw is unpublished anywhere. (4) The recommended path is the HEAVIEST
(~320 g of battery vs 90 g for a LiPo) on a drivetrain whose torque margin
is calculated but untested - if the car turns out underpowered, this is the
first thing to revisit. (5) Two batteries means two charge rituals and a
confusing failure mode (flat motor pack, full Pi pack). (6) One source
claiming the Pi 5 preemptively throttles on a lower-rated PSU is
contradicted by official docs and RPi staff, and is NOT credited. (7) All
six research workers are now complete; nothing physical has been built,
printed, bought, or measured. (8) No git repository.

# Appendix H - Budget settled (4GB + owned bank); BOM final; missing camera cable caught (2026-07-23, ~20:46 CDT)

**WHAT:** Evan answered the two blocking questions from Appendix G: he
**owns a USB power bank**, and he **takes the Pi 5 8GB -> 4GB downgrade**
(this supersedes his own ~17:21 M1.1 gate answer (a), on his instruction).
That selects the cheapest AND safest scenario from the Appendix G table.
The BOM is now written and final at **~$176-179 + shipping**, inside the
~$200 ceiling: `docs/BOM.md`.

**A MISSING PART WAS CAUGHT BEFORE IT COULD BITE.** While assembling the
BOM the reviewer checked the camera connection and verified against the
official Raspberry Pi camera documentation (2026-07-23): **the Pi 5 uses the
mini 22-pin CSI connector, while Camera Module 3 ships with a
Standard-Standard (15-pin) cable.** A **Standard-Mini cable (~$2-5)** must be
bought separately or the camera physically cannot be connected. This part
was absent from every prior cost estimate in this session (Appendices A-G)
and would have stopped M2 bring-up with all other hardware already on the
bench. Added to the BOM and to `gotchas.md`. Cheap part, expensive omission -
recorded because the near-miss is the lesson: the BOM was assembled by
walking the physical connections, not by summing the research briefs, and
that is what surfaced it.

**Final BOM composition** (full table with sources in `docs/BOM.md`):
Pi 5 4GB $70 + Camera Module 3 Wide $35 + Standard-Mini cable ~$2-5 + microSD
~$10 + Pololu #1093 N20 motor $23.95 + Pololu #713 TB6612FNG $4.95 + MG90S
servo ~$5 + 2x EVE 25P 18650 $3.70 + 2-cell holder $1.25 + USB-C 2S BMS
charge board $7.99 + LM2596 buck (servo rail) $2.48 + XT30 pair $1.10 +
rocker switch $0.75 + inline fuse holder ~$2.15 + wire/caps/connectors ~$8.
Power bank $0 (owned). **Shipping across 3-4 vendors is the remaining cost
risk at $15-25** - the BOM advises consolidating vendors over shaving item
prices, since most small parts are generic.

**Deferred and explicitly NOT ordered:** IMU (ICM-20948 $20 / BNO055 $35,
only if M4's observation design needs velocity or yaw), RPLIDAR C1 $99
(mount reserved in the chassis only), MG996R servo (fallback), DRV8871
driver (unnecessary - the paralleled TB6612 covers the numbers).

**Charging caveat carried into the build:** the $7.99 BMS board's published
protection list covers overcharge, over-discharge and short circuit but does
NOT state per-cell balancing. Mitigation written into the BOM: buy both
cells in the same order (matched), check them with a multimeter
occasionally, never mix in an older cell. The alternative considered and not
taken - an XTAR FC2 at $6.99 charging cells individually - removes balancing
concerns entirely but requires pulling cells out to charge and leaves the
pack with no discharge protection.

**Pre-order verification checklist written into the BOM** (four items Evan
must confirm himself, none of which Claude can check): his power bank's
label actually reads 5V/3A; which differential he owns (62821 28-tooth vs
6573 24/16 - this sets the reduction and the CAD mesh centres); which tires
(the part name states the real diameter); and current prices, since Pi
pricing moved twice in three months this year.

**SESSION SUMMARY - the research phase is complete.** Six Opus research
workers ran (compute, sensors, electronics, AI pipeline, drive motor, power
system), producing four saved briefs in `docs/research/`. Every worker's
load-bearing claims were spot-checked against primary sources by the
reviewer, and two full calculation chains (the drivetrain gearing/torque
math and the power runtime/peak-current math) were re-derived independently
rather than trusted. **Three of Claude's own earlier claims were overturned
in the process and are recorded as dated corrections rather than silent
edits** - the "~24GB VRAM" DreamerV3 figure (retracted, source unlocatable,
Appendix E), the "printed coupler is the highest-torque joint" framing
(backwards - it is the lowest, Appendix F), and "the Pi 5 needs 5V/5A"
(that rating is a USB-peripheral budget, Appendix G). A future session must
not reintroduce any of the three.

**HONEST OPEN ITEMS:** (1) **Nothing has been bought, built, printed, or
measured.** Every hardware claim in every doc remains desk research until
parts arrive. (2) No git repository initialized. (3) M1 tasks 2-5 (inventory,
CAD tool choice, print tolerance coupons, donor-geometry measurement) need
only Evan's existing printer and Lego and can start before the order
arrives; task 6 (rear drive module) still waits on the motor's real measured
dimensions. (4) The M4 task list (16-20) is concrete but its detail should
be revisited once M3's dataset format and eval harness actually exist.
