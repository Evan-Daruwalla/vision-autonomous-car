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
- [I — Repo initialized; M1.3 tolerance coupon generated and validated](#appendix-i---repo-initialized-m13-tolerance-coupon-generated-and-validated-2026-07-23-2110-cdt) (07-23)
- [J — Sim-first POC question; SIM-POC track added to the PRD](#appendix-j---sim-first-poc-question-sim-poc-track-added-to-the-prd-2026-08-05-2127-cdt) (08-05)
- [K — Nov-1 deadline set; execution plan approved; C1 environment started](#appendix-k---nov-1-deadline-set-execution-plan-approved-c1-environment-started-2026-08-05-2142-cdt) (08-05)
- [L — Track design settled: print markings not roads; figure-8; stop signs reframed as the M4 showcase](#appendix-l---track-design-settled-print-markings-not-roads-figure-8-stop-signs-reframed-as-the-m4-showcase-2026-08-05-2218-cdt) (08-05)
- [M — SIM-POC P2: expert driver tuned by measurement; alignment gate rebuilt after the first one proved wrong](#appendix-m---sim-poc-p2-expert-driver-tuned-by-measurement-alignment-gate-rebuilt-after-the-first-one-proved-wrong-2026-08-05-2310-cdt) (08-05)
- [N — Deadline moved to Regular Decision; grid/routing scope proposed; collection interrupted at 30k frames](#appendix-n---deadline-moved-to-regular-decision-gridrouting-scope-proposed-collection-interrupted-at-30k-frames-2026-08-05-2310-cdt) (08-05)
- [O — Cold audit finds the alignment gate was a fake; both the audit's fix and mine were wrong; routing research lands](#appendix-o---cold-audit-finds-the-alignment-gate-was-a-fake-both-the-audits-fix-and-mine-were-wrong-routing-research-lands-2026-08-05-2354-cdt) (08-05)
- [P — Verifier streamed (4.09 GB → 0.10 GB measured); a second false diagnosis caught; two sim tracks are unusable](#appendix-p---verifier-streamed-409-gb---010-gb-measured-a-second-false-diagnosis-caught-two-sim-tracks-are-unusable-2026-08-06-0020-cdt) (08-06)
- [Q — Two sim tracks quarantined by Evan's decision; corpus verifies clean on both axes](#appendix-q---two-sim-tracks-quarantined-by-evans-decision-corpus-verifies-clean-on-both-axes-2026-08-06-0011-cdt) (08-06)
- [R — SIM-POC P2 CLOSED: 102,888 frames, 88/88 verified on both axes](#appendix-r---sim-poc-p2-closed-102888-frames-8888-verified-on-both-axes-2026-08-06-0040-cdt) (08-06)
- [S — SIM-POC P3 DONE: a working world model, and the domain gap it exposed](#appendix-s---sim-poc-p3-done-a-working-world-model-and-the-domain-gap-it-exposed-2026-08-06-0118-cdt) (08-06)

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

# Appendix I - Repo initialized; M1.3 tolerance coupon generated and validated (2026-07-23, ~21:10 CDT)

**WHAT:** Two tasks at Evan's instruction ("2 then 3"): git repository
initialized with the doc scaffold committed, then PRD task M1.3 (print
tolerance coupons) prepared to the point where only Evan's printer is needed.

**GIT.** `git init` in the project root; minimal `.gitignore` (OS junk +
slicer gcode output only - no speculative language ignores, since no code
existed yet). 23 files staged, initial commit **6829d51**, working tree clean.
NOT pushed - Evan did not ask, and there is no remote. Note for future
sessions: the commit message was written to a file and passed with
`git commit -F` after a PowerShell here-string mangled the embedded double
quotes into pathspec arguments (`error: pathspec 'VRAM' did not match...`).
Use `-F` with a message file for any multi-line commit message on this
machine.

**M1.3 - DEVIATION FROM THE PRD, dated and justified.** The task as written
said to print "the Printables 660885 test board (or equivalent self-modeled
coupon)". A self-generated coupon was built instead. Reasons: the Printables
page 403s to automated fetch so its actual contents could never be verified
(the drive-motor research hit the same wall on Printables/Thingiverse), a
downloaded STL cannot be re-parameterized when the sweep turns out to bracket
nothing, and a generator script is a better portfolio artifact than a
download. The PRD task text was struck in place with this reason rather than
rewritten.

**Environment discovered** (feeds M1.2 inventory): git 2.53.0 with Evan's
identity configured; **real Python 3.14.4** (not the Microsoft Store stub);
**OpenSCAD NOT installed**; **both PrusaSlicer and Bambu Studio installed** -
the actual printer model and filament stock are still uncatalogued. Python
being real is what made a zero-dependency generator the right call over an
OpenSCAD file Evan would have had to install a tool to open.

**The artifact:** `scripts/gen_tolerance_coupon.py` ->
`cad/tolerance_coupon_v1.stl`. A 104 x 56 x 8 mm plate on the real 8 mm Lego
beam pitch, 20 holes, 18,048 triangles. Three test features: a PITCH row of 5
holes at exactly 8.00 mm centres (catches printer dimensional scaling, which
a single hole cannot), a PIN-fit sweep 4.80-5.30 mm, and an AXLE-bore sweep
5.20-5.70 mm. Rows are identified by marker-hole count (1 = pin, 2 = axle,
none = pitch) because embossed text would need a font engine. Plate thickness
is 8 mm deliberately - it matches a real Lego beam, and hole shrinkage is
depth-dependent, so a thin coupon would report optimistic numbers. Circle
facets use a circumscribed polygon (radius / cos(pi/n)) so the polygonal
approximation does not itself bias a tolerance measurement.

**TWO REAL DEFECTS WERE CAUGHT BY THE GENERATOR'S OWN CHECKS, not by
inspection.** This is the part worth recording:

1. **First run: `manifold FAIL`, 2560 duplicate + 4880 unmatched directed
   edges.** Cause: cells containing a hole subdivided their square boundary
   into 64 segments, while hole-less cells emitted a single quad - leaving
   T-junctions along every shared edge, and the outer walls did not match
   either. Fix: subdivide EVERY cell boundary identically and generate the
   perimeter walls at the same pitch.
2. **Second run: `manifold FAIL` (2560 unmatched) and `volume FAIL` -
   47616 mm3 against an expected 43519.** The volume number is what localized
   it: the mesh measured LARGER than a solid plate, so the holes were adding
   material instead of removing it. The hole walls were wound inside-out, and
   2560 = 20 holes x 64 segments x 2 rims pinned it exactly. Fix: reverse the
   wall traversal so each rim edge runs opposite to the face triangulation
   sharing it.
3. **Third run: `manifold PASS` (0 duplicate, 0 unmatched), `volume PASS`
   at 6.69e-16 relative error, `OVERALL PASS`.**

The signed-volume check was added specifically because edge-pairing proves
topology and winding consistency but would still pass a fully inverted mesh -
and it is what turned "something is wrong" into "the hole walls are
backwards" in one step. Neither defect would have been visible in a slicer
preview; both would have produced a subtly wrong physical part, on the one
artifact whose entire job is dimensional accuracy.

**Bench documentation:** `cad/README.md` carries the print guidance (same
settings as the eventual chassis, or the numbers do not transfer; no supports;
print BOTH PLA and PETG since the research calls for PETG on rotating bores
and PLA is fine for static holes), the pass criteria for each row (pin = seats
with firm thumb pressure and HOLDS; axle = spins FREELY with no radial slop;
pitch = a real Lego beam spans all 5 holes, else measure the 32.00 mm nominal
span and derive the printer's scale factor), and an empty results table for
the measurements.

**HONEST OPEN ITEMS:** (1) **The coupon has NOT been printed** - it is
validated geometry only, and no dimension in it has touched a real Lego part.
Every tolerance figure in the docs remains the unverified community starting
point until Evan prints and measures. (2) The printer model and filament stock
are still uncatalogued (M1.2). (3) Nothing has been ordered. (4) Not pushed -
no remote exists. (5) If the sweep brackets nothing at either end, the
generator constants need widening and a re-print, which is exactly why the
generator exists rather than a downloaded STL.

# Appendix J - Sim-first POC question; SIM-POC track added to the PRD (2026-08-05, ~21:27 CDT)

**WHAT:** Evan asked: "can we train the model in a simulated space first as a
proof of concept?" Answered yes, with a scope clarification that keeps the
ratified staging intact, and a new parallel SIM-POC task block appended to
the PRD (dated 2026-08-05). Cadence: this entry fires on the prompt-#12 hook.

**THE 13-DAY GAP, stated honestly:** the previous entry (Appendix I) is
2026-07-23; today is 2026-08-05. Whether the tolerance coupon was printed or
the BOM order was placed in between is UNKNOWN to this session - Evan has not
reported either, and nothing in the repo records it. Both remain open items;
if either happened, the results belong in the record and Evan has been asked.

**THE DISTINCTION THAT MAKES THE ANSWER YES.** The 2026-07-23 research
demoted sim-RL because sim-trained policies transfer badly to real hardware
(F1TENTH/RoboRacer, Appendix B/E) - that is a claim about TRANSFER. Evan's
question is about a PROOF OF CONCEPT - a claim about the PIPELINE. Training
the M4 world-model stack on simulated driving data proves the code path
(data format -> VAE+MDN-RNN -> DreamerV3-S -> policy extraction -> eval)
without touching the transfer bet at all, and evaluation in sim is free and
safe. The ratified scope guard is untouched: the sim-trained policy is NEVER
claimed as the real car's policy, and M4's capstone remains offline training
on the car's OWN real logs. SIM-POC de-risks M4; it does not replace it.

**Why now is exactly the right time:** nothing physical exists yet (order
status unknown, coupon unprinted), so the software pipeline is the only
workable critical path from this chair. The POC retires three explicitly
flagged unknowns from the 2026-07-23 research while hardware waits:
1. Whether `NM512/dreamerv3-torch`'s offline_traindir path actually runs
   end-to-end with zero environment instantiation (Appendix E flagged this
   verified-in-source but never verified-to-run).
2. WHERE THE REAL 8GB OOM BOUNDARY IS on Evan's actual 3060 Ti - the number
   the VRAM research said nobody has published. Sim data makes this
   measurable today (task P4's done-check: a trained model OR a documented
   OOM boundary, both pass).
3. Whether the episode format, frame/action sync, held-out split, and eval
   harness hold together - so M3/M4 on real data inherit a proven pipeline.

**Sim choice:** gym-donkeycar (already the research's low-friction pick for
M5). Reviewer verified 2026-08-05 via the GitHub API that the current
release v25.10.06 ships a Windows simulator binary - DonkeySimWin.zip,
236,059,289 bytes - so the POC runs on this machine. (The releases HTML page
failed to render its asset list; the API answered.)

**Environment caveat recorded to tooling.md:** system Python is 3.14.4 -
bleeding-edge for the ML ecosystem; PyTorch/gym wheel availability is
unverified there. All ML work runs in a PINNED PYTHON 3.11 VENV, matching
DonkeyCar 5.x's own requirement so the machine carries one toolchain
convention. Wheel availability is P1's done-check, not an assumption.

**PRD change under the mutability rules:** SIM-POC P1-P5 APPENDED as a
parallel track (environment/venv -> sim data corpus in dreamerv3-torch
episode format -> VAE+MDN-RNN small world model -> DreamerV3-S + measured
VRAM boundary -> policy extraction + in-sim eval vs a scripted baseline).
Nothing struck, nothing re-ordered; M1-M5 stand as ratified. Explicitly
noted in the PRD: SIM-POC is not M5 (no online RL, no PPO, no transfer
claim) - it is the M4 pipeline rehearsed on free data.

**Model-routing note:** session model switched back to Fable 5 this prompt
(was Opus 4.8 since ~17:21 on 07-23), so the opus-workers cheaper-tier
rationale applies again to any future worker spawns.

**HONEST OPEN ITEMS:** (1) Coupon print status and order status unknown -
asked. (2) The sim binary is NOT downloaded and no venv exists; SIM-POC P1
needs Evan's go (a ~236 MB download). (3) Python 3.11 wheel availability for
torch/gym-donkeycar is assumed-reasonable, verified only when P1 runs.
(4) Docs updated this entry: PRD SIM-POC block, tooling.md first real fact,
dependencies.md gym-donkeycar moved from "optional M5" to "SIM-POC + M5",
HANDOFF workstream row. Not committed - Evan has not asked for a commit.

# Appendix K - Nov-1 deadline set; execution plan approved; C1 environment started (2026-08-05, ~21:42 CDT)

**WHAT:** Evan reported nothing printed and nothing ordered, and asked for a
full thought-out plan before any execution. Planning session produced a
three-lane execution plan, approved, then appended to the PRD as section 6b.
Lane C (software) started immediately.

**THREE NEW CONSTRAINTS Evan supplied that reshaped the plan:**

1. **HARD DEADLINE: EA/ED college applications ~Nov 1 2026** - 12.5 weeks
   out. This is the first real deadline the project has had; every prior doc
   was dependency-ordered only.
2. **CAD tool: Onshape** (free public docs, browser-based, built-in version
   control matching the documentation-trail ethos). Resolves the M1.2 open
   question.
3. **PORTFOLIO CONTEXT, volunteered on plan review: this is 1 of 5
   concurrent portfolio projects** (ServeLocal, two trading projects, this,
   and a World Models research project), all documenting process for the
   same applications. This materially changed the plan rather than being a
   footnote - see below.

**Tools:** calipers confirmed owned; soldering iron+solder, multimeter, and
USB SD reader ASSUMED owned pending Evan asking his dad. Recorded as an
assumption with a $8-40 contingency, and flagged as SHOP TOOLING rather than
car BOM so it does not silently breach the $200 ceiling.

**HOW THE PORTFOLIO CONTEXT CHANGED THE PLAN (the substantive edit):** the
first draft implicitly assumed this project had Evan's full attention and
scheduled M4-on-real-logs to land Oct 19-26, before Nov 1. Five concurrent
projects makes that schedule dishonest. Revised:
- Bandwidth assumption stated explicitly: **~2-3 sittings/week here**, and
  the one-task-per-sitting design is what makes five-way juggling survivable
  (every sitting ends at a done-check; nothing left half-open).
- **Nov 1 now requires only SIM-POC + M3** - a real BC-driving car plus a
  sim-trained world model is a complete application story. **M4-on-real is
  reframed as STRETCH for Nov 1 and COMMITTED for RD (Jan 2027)**, landing
  as an application update or interview material if it slips. Pre-declaring
  this beats discovering it in late October.
- **Evidence banks at milestone completion, never at application season** -
  photos, video, measured tables into the record the day they happen. This
  was already the record discipline; it is now also a portfolio requirement.
- **C3-C5 and M4 double as substrate for the World Models research
  project** - the two-architecture comparison on one dataset, the
  unpublished 8GB DreamerV3-S boundary, and any honest negative results get
  captured with configs and limitations so that project consumes them
  without re-running anything. One build, two portfolio entries.

**Three lanes** so the shipping window is not dead time: A procurement
(Evan, ~45 min then waiting) - B physical/CAD (Evan's hands, my CAD support,
gated by the coupon then by parts) - C software/SIM-POC (me, costs Evan zero
sittings, starts now). Float is ~1-2 weeks concentrated in weeks 4-6 and is
shared with four other projects, which the design absorbs because Nov 1
needs only weeks 0-9.

**PRD updated under the mutability rules:** new **section 6b EXECUTION PLAN**
appended (schedule table, lane definitions, the A1 pre-order checklist,
deadline and portfolio constraints). No milestone was struck or re-ordered;
M1-M5 and SIM-POC P1-P5 stand as ratified. **Per-task commit authorization
granted by Evan with the plan approval** - commit at each done-check, naming
the task ID and its verification result; push still requires his explicit
say-so.

**C1 STARTED - two findings already, both recorded:**

1. **Python 3.11 is NOT installed on this machine** (`py -0p` shows 3.14.4
   and 3.12.10 only). 3.12 was the pre-declared fallback, and it was
   verified BEFORE switching rather than assumed: torch 2.13.0 classifies
   Python 3.10-3.14, and gym-donkeycar's GitHub setup.py needs only
   gymnasium>=0.29.0 / numpy / pillow at python_requires>=3.7. So 3.12 is
   covered and installing 3.11 would have been unjustified work. **Venv
   created at `.venv/` on Python 3.12.10**, pip 26.2.1.
2. **PyPI's `gym-donkeycar` is SIX YEARS STALE - 1.0.13, released
   2019-08-04** - while the GitHub repo ships v25.10.06 (2025-10-06). A
   naive `pip install gym-donkeycar` would have silently installed a 2019
   package against a 2025 simulator binary. **Install source is GitHub, not
   PyPI**, now written into the PRD's P1 task text and the dependencies bin.

**Hardware confirmed for the record:** `nvidia-smi` reports **NVIDIA GeForce
RTX 3060 Ti, 8192 MiB, driver 610.62** - the 8GB figure Evan gave on 07-23
is now machine-verified rather than reported. PyTorch cu126 wheel install
running at time of writing.

**HONEST OPEN ITEMS:** (1) PyTorch install not finished;
`cuda.is_available()` NOT yet verified - C1's done-check is unmet until it
prints True. (2) The DonkeySimWin binary (~236 MB) is not downloaded yet.
(3) Coupon still unprinted and order still unplaced - both are Evan's
actions this week, and both were confirmed outstanding at the top of this
session. (4) The soldering-iron/multimeter/SD-reader assumption is
unconfirmed until Evan asks his dad. (5) Nothing committed yet this session.


# Appendix L - Track design settled: print markings not roads; figure-8; stop signs reframed as the M4 showcase (2026-08-05, ~22:18 CDT)

**WHAT:** Evan described the intended real-world driving environment for the
first time: **modular sectioned plastic tiles, 3D printed with American road
markings and stop lines already in the surface, turns, with stop signs and
traffic lights possibly later** ("I don't know how hard they will be to make,
set up, and program yet"). Asked for suggestions. Analysis produced one hard
pushback, one reversed assumption, and a set of specs. Evan then decided:
**1.6 x 2.8 m floor space confirmed available; keep the 1:14 scale for the
turns; encode into the PRD; start SIM-POC P2 with the layout-based split.**

**THE PUSHBACK: printing the road SURFACE does not pencil out.** Estimated
for a minimum two-lane loop, ~5 m path x 0.52 m wide = ~2.6 m2 of road:

| Approach | Filament | Print time |
|---|---|---|
| Full surface, 220 mm tiles @ 2 mm | **~6.4 kg** (~$130-160) | **~150-250 h** (~100 on a fast Bambu) |
| Markings only, 0.8 mm strips | **~0.15 kg** | **~6 h** |

A **97% material reduction for identical camera input.** Three supporting
reasons: the printer is committed to chassis parts in weeks 1-3 while the
track is needed by ~week 5 for M2 data collection, so 150+ hours does not
fit; large thin prints warp, and this is the one surface that must be flat;
and warped tiles mean bumps, camera shake, and possible wheel lift.

**The framing that decided it: the camera sees MARKINGS, not roads.** The
road surface's entire job is to be flat, matte, and dark. At 120x160
resolution, filament spent on road surface buys nothing visible. Filament
spent on markings, signs, and stencils buys precision obtainable no other
way. **Recommendation adopted: dark matte foam board / coroplast tiles
(~$15 for the whole track) + printed marking strips glued flush + printed
signs and stencils.** Keeps modularity, precision, and the printed-markings
aesthetic; drops 6 kg of filament and ~5 days of printing.

**LAYOUT: figure-8, not an oval.** A simple loop turns one direction only,
and a behavioral-cloning model will learn "always steer left" - it would
look excellent on the training track and fail on anything else. A figure-8
gives both handednesses, a natural intersection for the stop sign / traffic
light, and a comparable footprint. (Driving the loop in both directions is
the cheap fix; the figure-8 is better and yields the intersection for free.)

**REVERSED ASSUMPTION - traffic lights are EASIER to learn than stop signs,
which is the opposite of the order Evan assumed:**
- **Traffic light: easy to learn, harder to build.** The correct action is a
  function of the CURRENT image (red visible -> stop, green -> go). A
  memoryless CNN handles it. Hardware ~$5-10 (LEDs + any microcontroller);
  for prototyping, a tablet displaying a red/green image needs no build at
  all.
- **Stop sign: trivial to build, PROVABLY impossible for plain BC.** Stopped
  at the line, the image is identical whether the car should keep waiting or
  go. The correct action depends on how long it has been stopped - history,
  not the current observation. A feedforward policy pi(action|image) cannot
  express it. Frame-stacking buys ~0.2 s of memory at 20 Hz; a stop is 2-3 s.

**WHY THAT IS GOOD NEWS, and the strongest argument in the project so far:**
DreamerV3's RSSM and the Ha & Schmidhuber MDN-RNN both carry recurrent latent
state - real memory. So the stop sign yields a clean, principled experiment
on one track and one dataset: **BC fails, the world model succeeds, for an
explainable reason.** That is the sharpest available justification for M4
existing at all, and it hands the separate World Models research project a
genuine result. **Decision: build the stop sign into the track from the
start, exercise it at M4, not M3.**

**MARKING SPECS - verified against the FHWA MUTCD** (mutcd.fhwa.dot.gov
Part 3B + MUTCD Part 3 general, accessed 2026-08-05), not recalled: normal
longitudinal lines **4-6 in**; stop lines **12-24 in**; broken lines **10 ft
segment / 30 ft gap**; **yellow separates opposing directions of travel,
white separates same-direction**. Scaled at **1:14** (from an ESTIMATED
130 mm car width - must be recomputed once the car is measured at B2/B3):

| Feature | Full scale | At 1:14 |
|---|---|---|
| Lane width | 12 ft | 261 mm |
| Normal line | 4 in | 7.3 mm |
| Stop line | 12-24 in | 22-44 mm |
| Dash cycle | 10 ft + 30 ft | 218 + 653 mm - PROBLEM |

**The dash finding:** at true scale one dash cycle is ~871 mm, so a ~5 m loop
shows only about 3.5 dashes - almost no signal for the CNN. The MUTCD itself
permits "dimensions in a similar ratio of line segments to gaps as
appropriate," so the 1:3 ratio is kept and the absolute size compressed to
~60 mm dash / 180 mm gap. Faithful in spirit, far denser training signal,
and the deviation is documented rather than silent.

**FOUR PHYSICAL GOTCHAS recorded to gotchas.md:** (1) glare - glossy plastic
under room lighting produces specular highlights that wash out markings;
matte everything, print face-down on a textured plate if printing surface
pieces. (2) **A seam running perpendicular to travel looks like a stop bar**
to the model; run seams parallel to travel where possible and keep them
tight. (3) Lock the camera pitch before data collection and record the
angle - changing it mid-dataset silently splits the data into two
incompatible distributions. (4) Vary lighting deliberately ACROSS sessions -
the real-world analogue of the domain randomization that made DeepRacer
transfer.

**METHODOLOGY FINDING that applies to SIM-POC P2 and M3 alike: never split a
driving dataset randomly by frame.** Frame t and t+1 are near-duplicates, so
a random split leaks and massively overstates accuracy. Split by lap at
minimum. Best: **split by LAYOUT** - train on configurations A+B, hold out
configuration C entirely. The modular tile system makes that free, and it
converts the fabrication choice into a scientific asset: a genuine
generalization result rather than a memorization score. Adopted for P2 in
sim (11 gym-donkeycar tracks are the sim analogue of tile layouts) and
carried forward to M3/M4 on the real car.

**Space:** Evan confirmed **1.6 x 2.8 m** available, which is what a
1:14 figure-8 wants. Scale is therefore kept as-is rather than compressed.

**HONEST OPEN ITEMS:** (1) The 1:14 scale rests on an ESTIMATED 130 mm car
width - unmeasured until B2/B3, and the whole marking table shifts if the
real car differs. (2) **Corner radius is still blocked on measuring the
steering geometry** (min radius ~ wheelbase / tan(max steer) - estimated
~330 mm, so corners want 500-670 mm centerline, but that is arithmetic on an
estimate, not a measurement). Corner tiles must not be cut until B3 and an
empirical turning-radius test on the rolling chassis. (3) Stop-sign and
traffic-light hardware are unbuilt and unpriced beyond a ~$5-10 estimate.
(4) The gym-donkeycar sim tracks look nothing like a 1:14 American-marked
road - irrelevant for SIM-POC, which proves the pipeline and makes no
transfer claim, but it does mean sim and real data can never be pooled.


# Appendix M - SIM-POC P2: expert driver tuned by measurement; alignment gate rebuilt after the first one proved wrong (2026-08-05, ~23:10 CDT)

**WHAT:** SIM-POC P2 built and validated: `ml/episode_writer.py` (writes the
NM512/dreamerv3-torch on-disk episode format), `ml/collect_sim_data.py`
(scripted PID expert driving the Donkey simulator, layout-split corpus),
`ml/verify_corpus.py` (the P2 done-check). Committed as 6d6bd8f. Corpus
collection to the ~100k-frame target launched 2026-08-05 ~23:12 CDT.

**THE LAYOUT SPLIT IS IN THE CODE, NOT THE INTENTIONS.** Per Appendix L,
`TRAIN_TRACKS` (generated-track, generated-roads, mountain-track,
roboracingleague-track) and `HOLDOUT_TRACKS` (waveshare) are module
constants, fixed BEFORE any data was collected so the split cannot later be
tuned to flatter a result. The verifier reads `log_track` back out of every
saved episode and fails on any track appearing in both splits, so leakage is
a test failure rather than a thing to remember. The 11 registered Donkey
tracks are the simulator's analogue of the physical tile configurations.

**FIRST SMOKE RUN FAILED, AND THE QUALITY FILTER IS WHY THAT WAS VISIBLE.**
Both smoke episodes were REJECTED and not written - "too short (65 steps)"
and "(99 steps)" against a 300-step request - because the car left the road
almost immediately. Had the collector saved whatever it produced, the corpus
would have silently filled with off-road frames labelled as expert
demonstration. The filter (min 150 steps, mean|cte| <= 1.2) turned a data-
poisoning bug into a loud rejection.

**DIAGNOSED, NOT GUESSED.** An open-loop probe held steer at +0.35 for 40
steps and logged cte: **+0.005 -> +4.224**. So positive steering INCREASES
cross-track error on this simulator, and the correction must be negative -
`STEER_SIGN = -1.0` is now a measurement, not a coin flip. A gain sweep on
donkey-generated-track-v0 then produced the finding that actually mattered:

| throttle | kp / kd | survived | mean abs cte |
|---|---|---|---|
| 0.32 | 0.32 / 0.28 | 191/400 | off-road |
| 0.32 | 0.6 / 0.4 | 218/400 | off-road |
| 0.32 | 1.0 / 0.6 | 203/400 | off-road |
| 0.20 | 1.2 / 0.6 | **400/400** | 0.53 |
| 0.20 | 1.8 / 0.9 | **400/400** | 0.41 |
| 0.20 | **2.4 / 1.2** | **400/400** | **0.36** |

**THROTTLE dominated the gains.** At 0.32 the car left the road in 191-218
steps under every gain setting tried; at 0.20 every setting survived the full
400. Tuning gains at the original throttle would have been chasing the wrong
knob indefinitely. Adopted: KP 2.4, KD 1.2, KI 0.0, THROTTLE 0.20,
THROTTLE_CORNER 0.14.

**THE PART WORTH RECORDING: THE FIRST ALIGNMENT CHECK WAS WRONG, AND THE
CORPUS IT WOULD HAVE FAILED WAS FINE.** An off-by-one between frames and
actions is the failure mode that does not announce itself - training still
converges, the curves still look healthy, and the model quietly learns to
predict the PREVIOUS action from the current frame. So `verify_corpus.py`
was built to re-derive alignment from pixels: estimate the horizontal scene
shift between consecutive frames by cross-correlating a band of road ahead,
then check that `action[i]` correlates with that shift better than
`action[i+1]` does.

It ran on a known-good corpus and reported the correlation peaking at **lag
-1**, not 0. Taken at face value that says the data is misaligned. It is not
- **it is vehicle physics.** Steering commands a heading RATE, not a heading,
so the scene shift produced by a steering input necessarily appears a step
or so after the command. Peak-correlation-at-lag-zero was simply the wrong
test, and shipping it would have meant a permanent false alarm on correct
data - or worse, "fixing" a correct writer to satisfy a broken check.

**Replaced with an exact algebraic identity.** The expert driver is a
deterministic function of cross-track error, so the collector now logs
`log_cte` (recorded at the same instant as each frame) plus the PID
parameters actually in force. The verifier recomputes every action from
scratch:

    action[i] == clip(sign * (kp*e + kd*(e - e_prev)), -limit, +limit)
    where e = cte[i-1], e_prev = cte[i-2]

No thresholds, no assumptions about dynamics, and rolling the action array by
a single step breaks it immediately. The pixel-motion check was kept but
DEMOTED to informational, printing the whole lag profile - it is genuinely
useful for spotting a dead or frozen camera feed, it is just not an alignment
gate. Logging the PID parameters per-episode rather than reading module
constants also means re-tuning the driver later cannot retroactively
invalidate an older corpus.

**Verifier output on the corpus as it stood (2026-08-05 ~23:08 CDT), real
output pasted:**

    holdout  :   1 episodes,     401 frames, tracks ['donkey-waveshare-v0']
    train    :   6 episodes,    3381 frames, tracks ['donkey-generated-roads-v0',
                 'donkey-generated-track-v0', 'donkey-mountain-track-v0',
                 'donkey-roboracingleague-track-v0']
      split is disjoint      : no track appears on both sides
    total frames: 3782
    alignment:
      exact PID identity     : verified on 7 episode(s), every action reproduced from log_cte
      pixel-motion profile   : -3:0.57 -2:0.67 -1:0.72 +0:0.66 +1:0.51 +2:0.34  (n=3388, peak -1)
    P2 CORPUS CHECK: PASS

**Structural checks the verifier also enforces** (each one a bug that would
otherwise surface much later): filename step-count must match the array
length, since dreamerv3-torch's loader trusts the filename; `is_first` true
only at t=0 and `is_last` only at the end; `action[0]` all zeros and
`reward[0]` zero, because no action caused the reset frame; `discount == 0`
exactly where `is_terminal` is true, so a time-limit truncation is never
encoded as "the future ceased to exist"; no NaN or inf; steering within
[-1, 1]; image arrays uint8 and (T, H, W, 3).

**A `--holdout-episodes` flag was added 2026-08-05 ~23:12** so the held-out
track is not over-sampled at the training track's episode count - the holdout
sizes an evaluation, not a training set.

**HONEST OPEN ITEMS:** (1) The corpus at time of writing is **3,782 frames
against a ~100k target** - the full run is in flight and P2 is NOT done until
it lands and re-verifies. (2) roboracingleague-track yielded only a 176-frame
episode, so the expert may be marginal on that geometry; if it keeps
under-producing it should be dropped from TRAIN_TRACKS with a dated note
rather than left to quietly skew the corpus toward the easy tracks. (3) The
expert drives on privileged simulator state (`cte`); this is deliberate and
matches Evan later hand-driving the real car, and nothing downstream ever
sees `cte` - the models get pixels only. (4) Episode lengths in the existing
corpus are inconsistent (176/401/1001) because they span runs made with
different `--max-steps`; harmless for training, but the final corpus summary
should report the distribution rather than an average that hides it.
(5) Still nothing physical printed, ordered, or built.


# Appendix N - Deadline moved to Regular Decision; grid/routing scope proposed; collection interrupted at 30k frames (2026-08-05, ~23:10 CDT)

**CADENCE NOTE, logged not hidden:** this entry covers cadence hits at prompt
#18 AND #21. The #18 entry was never written - the session was interrupted
mid-turn (the tool layer became briefly unavailable, then the process exited)
before it could be. Caught up here rather than silently skipped.

**WHAT (1) - THE DEADLINE MOVED.** Evan: *"This may also go past the Nov 1
deadline so the final deadline is now regular decision but I want to get as
much done as possible before then."* So **the hard deadline is now Regular
Decision, ~Jan 1-15 2027** (~5 months), with **Nov 1 2026 retained as a soft
milestone** - whatever is finished by then strengthens the EA application,
and the rest lands as an RD update or interview material. This RELAXES the
Appendix K schedule, which had already been designed so Nov 1 needed only
SIM-POC + M3, with M4 pre-declared an RD-safe stretch. That design now pays
off: nothing has to be cut, and the M4 capstone moves from "stretch" to
"comfortably in scope."

**WHAT (2) - A SCOPE EXPANSION IS PROPOSED, NOT YET DECIDED.** Evan is
considering scaling the grid up to support **real destinations, parking, and
routing** - i.e. "drive from A to B, then park," rather than lane-following a
loop. This is a genuine change in system CLASS, not a bigger version of the
same thing, and it is under evaluation rather than adopted. Two reasons it
needs care before it enters the PRD:

**(a) End-to-end behavioural cloning cannot route - reasoning, pending
verification.** At an intersection, two IDENTICAL camera images require
different actions depending on the destination. A policy pi(action|image)
has no term for the destination, so it cannot represent the difference. This
is the same partial-observability class as the stop-sign finding in Appendix
L, but strictly worse: the stop sign is resolvable by MEMORY (recurrent
state), whereas routing additionally requires CONDITIONING ON A GOAL. The
expected fix is a goal-conditioned policy pi(action|image, command) -
conditional imitation learning - which is well-established in the literature
but is an architecture change to every model in the plan, not a bolt-on. A
research worker was launched 2026-08-05 ~23:12 to verify this and pin the
canonical architecture; **nothing is being built against it until that
returns.**

**(b) THE GRID DOES NOT FIT THE CONFIRMED SPACE at 1:14 - arithmetic, done
here, to be re-checked against the measured car width.** Using the Appendix
L scale (lane 261 mm, two-lane road 522 mm) in the confirmed 1.6 x 2.8 m:

| Layout | Required span | Fits 1.6 m? |
|---|---|---|
| Single 4-way intersection, 500 mm arms | 500 + 522 + 500 = **1522 mm** | YES |
| 2x2 grid (4 intersections), 400 mm blocks, 300 mm stubs | 522 + 400 + 522 + 600 = **2044 mm** | **NO** |
| Same grid, ONE-WAY single-lane roads (261 mm) | 261 + 400 + 261 + 600 = **1522 mm** | YES, but loses the yellow centreline |
| 4-bay parking lot (196 x 392 mm bays + 522 mm aisle) | **784 x 914 mm** | fits alongside, in the 2.8 m axis |

So there is a real tension: **American two-lane markings AND a
multi-intersection grid cannot both fit 1.6 m at 1:14.** A single
intersection plus a parking lot does fit - and a single 4-way intersection is
already enough to demonstrate routing, since routing only requires that a
CHOICE exists with more than one destination. The figure-8 already has a
crossing. Levers if a true grid is wanted: one-way single-lane roads, a
smaller scale (1:20 is still marginal at 1732 mm), or more floor space.
Presented to Evan as options; not decided.

**A LIVE, TIME-SENSITIVE BOM CONSEQUENCE.** Routing requires localization,
and the chosen drive motor **Pololu #1093 has NO encoder**. The same motor
with a 12 CPR magnetic encoder is **#5159 at $29.95 (+$6)**. **The order has
not been placed**, so this is decidable now at zero cost and expensive later
- retrofitting an encoder means replacing the motor and re-cutting the
cradle. Flagged to the research worker as an explicit question rather than
guessed at.

**WHAT (3) - SIM-POC P2 COLLECTION WAS INTERRUPTED.** The ~100k-frame run
launched 2026-08-05 ~23:12 was killed when the session process exited. It is
NOT a code failure - the log shows clean laps (18.1-21.6 s) right up to the
cut. Survived, verified on disk:

| Split | Episodes | Frames |
|---|---|---|
| train | 28 | **29,803** |
| holdout | 1 | **401** |

**The holdout is the problem, and it is a structural one, not bad luck:** the
collector runs all train tracks first and the holdout last, so an
interruption takes out the evaluation split specifically. 401 frames cannot
support a generalization claim. A `--only {train,holdout}` resume flag was
added (episodes carry uuid filenames, so a repeat run APPENDS rather than
restarting) and holdout collection relaunched at 9 episodes.

**Honest note on the target:** the PRD says ~100k frames, from V-D4RL's
offline-visual benchmark standard. 29,803 train frames is already above
DonkeyCar's stated 10-20k guidance for behavioural cloning and above Ha &
Schmidhuber's 10,000 rollouts, so P3 is not blocked. If the corpus is
declared done below 100k, that is a DEVIATION FROM THE PRD and must be
recorded as one - not quietly redefined as sufficient.

**WHAT (4) - A COLD AUDIT WAS LAUNCHED.** Evan invoked `/audit`. Per the
skill's step 0, a session that built the thing inherits its author's belief
("that module is fine, I wrote it" is not a finding it can make), so a fresh
auditor was spawned with the project path, the scope, and the docs handed to
it **as claims under test** - and deliberately WITHOUT this conversation's
history or any "this part is known-good". Findings-only; it is forbidden to
change anything. Weighted toward ML-pipeline correctness and doc-vs-reality
drift, because this project's portfolio value depends on its measured claims
being true. It will specifically re-test the record's own numbers (the PID
sweep table, "97% filament reduction", the coupon's manifold/volume PASS,
the MUTCD scaling, the ~$176-179 budget).

**HONEST OPEN ITEMS:** (1) Routing architecture UNVERIFIED - the claim that
BC cannot route is reasoning, not yet sourced; the worker may refute it.
(2) The grid arithmetic above uses an ESTIMATED 130 mm car width; the whole
table shifts when the real car is measured (task T1). (3) The encoder-motor
decision is open and blocks nothing yet, but closes cheaply only until the
order is placed. (4) Holdout collection in flight; P2 is NOT done until it
lands and re-verifies. (5) **Still nothing printed and nothing ordered** -
unchanged since 2026-07-23, now the longest-standing open item in the
project. (6) The audit had not returned at time of writing; its findings are
not represented here.


# Appendix O - Cold audit finds the alignment gate was a fake; both the audit's fix and mine were wrong; routing research lands (2026-08-05, ~23:54 CDT)

**WHAT:** The cold audit (launched ~23:12, findings-only, no conversation
history, docs handed to it as claims under test) returned **22 findings and
12 edge cases**. Separately the routing/scope research returned. Both are
summarised here; the audit's fixes 1-6 are APPLIED and re-verified.

## O.1 - The headline finding, and it is mine to own

**The alignment gate did not gate what its own docstring claimed.**
`check_pid_identity` relates `action[i]` to `log_cte[i-1]` and **never opens
an image**. So a corpus whose IMAGE array is rolled passes cleanly - which is
exactly the bug Appendix M says the check exists to catch.

Reviewer-verified independently before accepting the finding (sandbox copies,
real verifier, 2026-08-06 ~23:30 CDT):

| Manipulation | Result |
|---|---|
| baseline, untouched | PASS |
| **images rolled +1** | **PASS** <- should fail |
| **images rolled +3** | **PASS** <- should fail |
| actions rolled +1 (control) | FAIL |

**How it happened, stated plainly:** Appendix M records replacing the
pixel-motion check with the PID identity after the pixel check reported peak
correlation at lag -1 on good data. Diagnosing that -1 as physics was
correct. **Demoting the check was not.** The right move was to gate on the
measured baseline; instead the only check that could see the image axis was
removed, and Appendix M went on to describe the remaining check in language
that implied it covered both axes. The docs overclaimed relative to the code,
which is precisely the class of drift the audit was commissioned to find.

## O.2 - The audit's recommended fix was ALSO wrong, and the data says so

The audit proposed re-promoting the pixel check with a gate on **peak lag ==
-1**. Implemented, then measured across all 49 episodes - and it produced
**false failures on 11 legitimate episodes**. Diagnosis run
(`scratchpad/diag_lag.py`, per-episode lag vs pixel speed):

| Group | n | mean abs pixel shift | mean abs steer |
|---|---|---|---|
| peak **-2** | 11 | **4.23 px** | 0.655 |
| peak **-1** | 38 | **3.40 px** | 0.614 |

The -2 episodes are **interleaved through every collection run** (22:37,
22:45, 22:49, 22:59, 23:01, 23:04, 23:06, 23:24, 23:26, 23:30, 23:32) - not
clustered, so not a collector-version artifact - and they are systematically
the **faster-moving** ones. Every holdout episode on the slower waveshare
track (mean shift 2.15 px) sits at -1. **The visual lag is speed-dependent:
faster scene motion pushes the apparent lag from -1 to -2.** Physics plus
discrete sampling, not misalignment.

So an exact-equality gate is wrong for the same underlying reason the
original peak-at-zero gate was wrong: **it assumes a constant that is not
constant.** Two different people (the auditor, and me) reached for the same
wrong shape of fix; only measuring across the whole corpus exposed it.

**What shipped instead - and what it can and cannot prove:**
- per-episode peak must lie in the **plausible band {-2, -1}** -> catches any
  offset of >=2 frames
- the corpus **MODE** must equal -1 -> catches a whole-corpus 1-frame roll,
  since that shifts every episode together
- **CANNOT** catch a 1-frame roll of a *minority* of already-at--1 episodes,
  because real physics produces that exact signature at -2. **Documented in
  the constants block rather than papered over.** The action axis remains
  covered exactly by the PID identity; the image axis is now covered
  approximately, with the limit stated.

## O.3 - Fixes applied and re-verified

| # | Fix | Verification |
|---|---|---|
| 1 | Image-axis gate restored (band + mode, per-episode not pooled) | images rolled +1 -> FAIL, +3 -> FAIL, baseline -> PASS |
| 2 | Empty corpus fails (`total_frames == 0`, and a bare dir with no split subdirs) | both -> FAIL |
| 3 | Missing-split fails instead of silently skipping the leakage check | train-only -> FAIL |
| 4 | Partial verification fails (`checked != len(episodes)`) | a mixed-format corpus can no longer report success |
| 5 | `log_ki` added to the PID identity, integral clamp mirrored | a non-zero KI would have failed a CORRECT corpus with the actively misleading message "the frame/action indexing is wrong" |
| 6 | Atomic episode write (`os.replace`) + guarded load + `_steps` cleared in `finally` | a reader racing the collector can no longer hit a truncated npz and abort the whole run |

**Per-episode, not pooled, matters:** the first attempt pooled all episodes
and passed a sandbox corpus with 2 of 3 episodes rolled by +1 - the clean
minority averaged out the corrupted majority.

**Full corpus after fixes (real output, ~23:52 CDT):**

    holdout  :  10 episodes,   11210 frames, tracks ['donkey-waveshare-v0']
    train    :  41 episodes,   45416 frames, tracks [4 tracks]
      split is disjoint      : no track appears on both sides
    total frames: 56626
      exact PID identity     : verified on 51/51 episode(s)
      image-axis gate        : 51/51 in band (-2, -1), distribution {-2: 11, -1: 40}, mode -1 (|r| 0.39-0.95)
    P2 CORPUS CHECK: PASS

## O.4 - The rest of the audit, not yet actioned

Verified-clean by the auditor re-running them: the coupon generator
reproduces `manifold PASS` / `volume PASS at 6.69e-16` / 18,048 triangles and
rewrites the STL byte-identically; **all six MUTCD 1:14 numbers reproduce
exactly**; "97% filament reduction" is 97.66%, correctly and conservatively
rounded; no secrets; `.gitignore` has no malformed `{`/`}` globs, so empty
searches are trustworthy.

Outstanding, by class:
- **Doc drift (F4, F15-F17):** HANDOFF and PRD still carried the Nov-1
  deadline and "~100k-frame run in progress"; the PRD still carries the
  **retracted** "never a phone power bank" gotcha un-struck in a "read first"
  section, still says Pi 5 **8GB**, and three docs claim a **Python 3.11**
  venv when it is **3.12.10**.
- **Data quality (F7, F8):** the quality gate (mean|cte| <= 1.2, >= 150
  steps) is enforced only in the collector and is **unenforceable at rest** -
  `log_mean_abs_cte` is written and never read. One train episode sits at
  mean|cte| 1.13 (94% of the reject limit) with **69.6% of frames at full
  steering lock**, labelled expert data. Separately, the train split is
  **41 episodes but heavily skewed to one track** - the interrupt hit
  mid-run, so `generated-track` dominates. That undercuts "train on a subset
  of layouts" and needs round-robin collection.
- **Scaling (F9/E7):** `verify_corpus` holds every episode's images in RAM -
  **2.57 GB at 44.6k frames, ~5.8 GB at the PRD's own 100k target.** The
  done-check will OOM exactly when P2 becomes finishable.
- **Bins (F18):** `data.md` is still "empty, no code yet" while the npz
  schema IS the ML data contract.
- Minor: BOM total is light by $2.32 (excludes the camera cable it
  celebrates catching); two record timestamps are misattributed against file
  mtimes; Appendix L's "3.5 dashes" should be 5.7.

## O.5 - Routing research: the scope expansion is real but must shrink

**BC cannot route - CONFIRMED, with a refinement.** Codevilla et al. (ICRA
2018) state it directly: *"when a car approaches an intersection, the camera
input is not sufficient... the mapping from the image to the control command
is no longer a function."* Refinement worth keeping honest: what fails is
**direction, not representation** - a multimodal head can represent both
branches, it just cannot *select* one. Frame history does not help; the
destination was never in any pixel. **Conditioning is necessary.**

**Architecture: branched conditional imitation learning.** Shared conv trunk,
one head per discrete command, command as a one-hot switch. Measured:
CARLA 88% vs 78% (branched vs command-as-input), 64% vs 52% on an unseen
town; on a 1/5-scale physical truck over a **14-intersection route, 0% vs
11.1% missed turns** - trained on **2 hours of teleop**. That 2-hour figure
is what makes this scope plausible at all.

**Three findings that change the plan:**
1. **Modern target-point conditioning has a pathology the 2018 discrete-
   command form does not** (ICCV 2023): TP-conditioned models extrapolate
   toward a point behind a turn and cut into the oncoming lane. A one-hot
   "turn left" carries no geometry to over-extrapolate. **The older, simpler
   formulation is the safer one here.**
2. **The inertia problem is guaranteed to bite**, because stop lines are
   being added: stopped frames dominate, producing *"excessive stopping and
   difficult restarting."* Mitigation is known - a speed-prediction auxiliary
   head, and classifying target speed rather than regressing it.
3. **More data can make it worse** - CILRS found 10 h beat 100 h on dense
   traffic. Coverage of rare events, not volume, is the lever. Also: **seed
   variance up to 42 points**, so one trained model is not a measurement -
   >=3 seeds or the numbers are noise.

**GEOMETRY: the current track spec is over-constrained and cannot be built.**
- Duckietown tiles are **61 cm**; its minimum loop with intersections is
  **3x3 = 1.84 m**, which **fails the 1.6 m width**. The largest
  Duckietown-spec layout fitting 1.6 x 2.8 m is a **2x4 plain loop with zero
  possible intersections.**
- At **1:14**, a two-lane road is 522 mm and 1.6 m holds **3.07 lane-widths**
  - one road plus margin. **A grid with two parallel roads is impossible at
  1:14**, confirming the Appendix N arithmetic from a second direction.
- To fit a **3x5 grid**: tile <= 533 mm, lane 182 mm, effective scale
  **~1:20, not 1:14**. Car at 130 mm then occupies 71% of the lane - **26 mm
  clearance per side, about half a Duckiebot's margin.**
- **True MUTCD dash proportions (1:3) do not survive tiling at any scale that
  fits.** Duckietown uses ~2:1. This must be recorded as a deliberate
  deviation, not claimed as MUTCD compliance.

**BOM: buy the encoder motor (#5159, +$6). Not close.** The decisive argument
is not odometry in general but **the intersection blind zone**: inside an
intersection there are no lane markings, the camera provides nothing for
40-60 cm, and **that is the piece that broke in all four prior attempts**
found (2018 Unicorn, 2019 proj-goto-n, 2023 student writeup, 2024 GOTO-1) -
two of them resorted to open-loop hardcoded timing. Calibrated encoder drift
over 0.6 m is ~1-6 mm. Secondary wins: ground-truth speed labels (PWM->speed
drifts with battery voltage, making the action space non-stationary), and
closed-loop restart from stop lines. **Order the 6-pin JST SH cable in the
same purchase - it is sold separately.** Honest arguments against, recorded:
the encoder adds 3-4 mm on the connector side of a 10x12 mm gearbox, and it
counts the MOTOR shaft, upstream of a backlash-heavy Lego differential.
Also flagged: **pigpio does not work on Pi 5** (RP1 south bridge) - use lgpio
/ libgpiod.

**Parking: forward pull-in ONLY.** Reverse perpendicular and parallel both
need rear sensing this car does not have, and **nobody has published either
on a sub-1/10 car with a single forward camera.** The one quantitative prior
record is a **failure**: Duckietown's 2017 parking project planned fine
(Dubins in <0.2 s, localization +/-0.5 mm within 0.3 m) but *"was unable to
park"* because AprilTag detection ran at ~0.34 Hz. That specific number is
Pi-2/3-era lore and is obsolete - a Pi 5 does ~20 FPS - but the architectural
lesson (tag-in-the-control-loop is latency-critical) stands.

**AprilTag sizing - the single most actionable derived number.** With a 120
deg lens the pixels spread thin: at 640 px wide, a 40 mm tag36h11 is
**unreadable beyond 26 cm**. Switching to **tag41h12** buys ~60% range free,
and detection should run on a **1280-wide crop**. At 60 mm / 1280 px that is
1.24 m of range instead of 0.52 m.

**Scope verdict: the full "lane following + routing + parking" is NOT
realistic** at ~2-3 sittings/week as 1 of 5 projects; a staged subset is.
Recommended order, each stage shipping a measurable artifact: **Stage 0 track
re-spec (BLOCKING, before any printing)** -> lane-following BC -> stop-line
detection -> topological localization (AprilTag + encoder) -> branched
command-conditioned BC + Dijkstra routing -> forward pull-in parking ->
world model kept OFF the control path as an offline prediction artifact.
**Cut line: drop parking before dropping routing** - routing is the
distinctive claim nobody has published at this scale; parking would be a weak
version of a solved problem.

**HONEST OPEN ITEMS:** (1) Audit findings F4, F7-F9, F15-F18 and edge cases
E7-E12 are NOT fixed - only fixes 1-6 are. (2) The track geometry is now
known-unbuildable as specified and Stage 0 blocks all printing; **this is
good news only because nothing has been printed.** (3) The scope expansion is
still Evan's decision - nothing was adopted into the PRD beyond this record.
(4) The encoder-motor recommendation is not an order; nothing is bought.
(5) `verify_corpus` will OOM near the 100k target and must be streamed first.
(6) Corpus is 56,626 frames and still collecting.


# Appendix P - Verifier streamed (4.09 GB -> 0.10 GB measured); a second false diagnosis caught; two sim tracks are unusable (2026-08-06, ~00:20 CDT)

**WHAT:** The P2 top-up collection finished. Corpus is **76,299 frames**
(67 train episodes / 65,089 frames; 10 holdout / 11,210). Two audit items
fixed and re-verified; two data-quality findings surfaced that need Evan's
decision. **P2 currently FAILS its own done-check** - honestly, and for a
good reason.

## P.1 - Streaming fix (audit F9/E7), with a measured result

`verify_corpus.py` retained every episode's image array so two later passes
could iterate. The audit predicted **~5.8 GB at the PRD's own 100k-frame
target** - i.e. the done-check would OOM exactly when P2 became finishable.
At 76,299 frames the retained-images estimate was **4.09 GB**.

Refactored so each episode is checked and immediately discarded: both gates
became per-episode functions writing into small accumulators, with separate
finalizers. **Measured peak Python RSS after the change: 0.10 GB** - roughly
40x lower, and now O(1) in corpus size rather than O(n). All four adversarial
tests still behave correctly after the refactor (baseline PASS; images rolled
+1 FAIL; rolled +3 FAIL; actions rolled +1 FAIL).

## P.2 - A SECOND false diagnosis, same class as the log_ki one

With the band gate live, four short roboracingleague episodes reported
*"the image array is offset from the actions"* - peaks at lag -3. That
diagnosis was **wrong**, and it was wrong in the same way the `log_ki` bug
was wrong: it pointed a reader at the wrong subsystem.

The tell is the correlation strength. Measured separation across 77 episodes:

| Group | \|r\| at peak |
|---|---|
| episodes with a well-determined lag | **0.60 - 0.96** |
| the four "peaking at -3" (~180 frames each) | **0.34 - 0.40** |

At \|r\| ~0.35 on ~180 frames the peak is **noise, not a lag measurement** -
the correlation is far too weak to distinguish -3 from -1. `MIN_PEAK_CORR`
was 0.30, permissive enough to let noise be reported as misalignment. Raised
to **0.50** (set inside the measured gap, not tuned to make a failure
disappear), and weak-correlation episodes are now routed to **UNVERIFIABLE**
rather than **WRONG**, with the message saying so explicitly: *"not wrong,
unchecked."*

Lesson worth keeping: **a checker that misdiagnoses is worse than one that
abstains.** Three separate instances of this class have now been found in
this one file (peak-at-zero, log_ki, weak-correlation-as-misalignment). The
common cause each time was asserting a constant that was not constant.

## P.3 - Two of the four sim tracks are unusable by the expert

Per-track breakdown of the finished corpus:

| Split | Track | Episodes | Frames | Avg length |
|---|---|---|---|---|
| train | generated-track | 38 | 44,438 | 1169 |
| train | generated-roads | 14 | 16,014 | 1144 |
| train | **roboracingleague** | 14 | **4,236** | **303** |
| train | **mountain-track** | **1** | **401** | 401 |
| holdout | waveshare | 10 | 11,210 | 1121 |

- **mountain-track: 13 of 13 episodes REJECTED** in the top-up run. The
  quality filter (min 150 steps, mean\|cte\| <= 1.2) caught every one - the
  expert cannot drive that geometry at the tuned gains.
- **roboracingleague: episodes average 303 frames against a 1200 request**,
  i.e. the car leaves the road in about a quarter of an episode, and its
  mean\|cte\| of 0.68 is the worst of any saved track. **All 12 currently-
  unverifiable episodes come from these two tracks.**

Together they contribute **4,637 frames - 7% of the corpus** - while
supplying 100% of its failures. The two healthy tracks supply **60,452
frames**.

**This undercuts a load-bearing claim.** The layout split (Appendix L/M) is
premised on training across *several* layouts and holding one out. In
practice the corpus is two healthy layouts plus two that barely produced
data. That is still a valid layout split - two train layouts, one unseen
holdout - but it is thinner than the PRD implies, and saying "trained on
four tracks" would be false.

**Not decided here - escalated to Evan**, because narrowing the training
distribution is an experiment-design change, not a cleanup:
- **(a)** Quarantine the two tracks' episodes and strike them from
  `TRAIN_TRACKS` with a dated reason -> 60,452 frames, 2 train layouts,
  clean PASS.
- **(b)** Re-tune the expert per-track (lower throttle, per-track gains) so
  they produce usable data -> more layout diversity, real work, no benefit
  to the M4 pipeline P2 exists to prove.

Recommendation: **(a)**, with the reduced diversity stated plainly in the
PRD and any writeup. P2's purpose is proving the pipeline end to end, not
maximising track variety; layout diversity is a *real-car* concern (M3/M4),
where the physical tile configurations are the layouts that matter.

## P.4 - Current state, stated honestly

    total frames: 76,299
      exact PID identity     : verified on 77/77 episode(s)
      image-axis gate        : 65/77 in band (-2,-1), distribution {-2: 16, -1: 49}, mode -1 (|r| 0.64-0.96)
    P2 CORPUS CHECK: FAIL
      - image-axis: 12/77 episode(s) could NOT be checked ... UNVERIFIED - not wrong, unchecked.

**P2 is NOT done.** The action axis verifies on every episode; 65 of 77 also
verify on the image axis; the remaining 12 are unverifiable short episodes
from the two bad tracks. The failure is the done-check working as intended -
it is refusing to certify episodes nothing actually checked.

**HONEST OPEN ITEMS:** (1) The track decision above is unmade. (2) Audit
items still outstanding: quality thresholds unenforceable at rest (F7),
per-track collection imbalance (F8 - now measured and worse than the audit
saw: 38 of 67 train episodes are one track), the empty `data.md` bin (F18),
and edge cases E8-E12. (3) `MIN_PEAK_CORR = 0.50` is calibrated on 77
episodes from one simulator; it must be re-measured for the real car along
with the lag constants. (4) Nothing printed, nothing ordered - unchanged.


# Appendix Q - Two sim tracks quarantined by Evan's decision; corpus verifies clean on both axes (2026-08-06, ~00:11 CDT)

**WHAT:** Evan chose option (a) from Appendix P.3: **quarantine the two
tracks the expert cannot drive**, rather than re-tuning the expert per-track.
Applied, verified, and the consequence recorded rather than buried.

**Action taken - MOVED, not deleted.** 15 episodes / 4,637 frames
(`mountain-track` x1, `roboracingleague-track` x14) were moved from
`ml/data/sim/train/` to **`ml/data/sim_quarantine/train/`**. Nothing was
deleted, so the decision is reversible if the expert is ever re-tuned. Both
tracks were struck from `TRAIN_TRACKS` in `collect_sim_data.py` with the
reason, the numbers, and the quarantine path written into the code comment -
so a future session cannot silently re-add them without reading why they
went.

**Corpus after quarantine, real output:**

    holdout  :  10 episodes,   11210 frames, tracks ['donkey-waveshare-v0']
    train    :  52 episodes,   60452 frames, tracks ['donkey-generated-roads-v0', 'donkey-generated-track-v0']
      split is disjoint      : no track appears on both sides
    total frames: 71662
    alignment:
      exact PID identity     : verified on 62/62 episode(s), every action reproduced from log_cte
      image-axis gate        : 62/62 episodes in band (-2, -1), lag distribution {-2: 16, -1: 46}, mode -1 (|r| 0.74-0.96)
    P2 CORPUS CHECK: PASS

**Every episode now verifies on BOTH axes** - 62/62 on the action axis and
62/62 on the image axis, against 77/77 and 65/77 before. The correlation
floor also moved: the weakest surviving episode is **|r| 0.74**, where the
previous corpus reached down to 0.35. Removing the two tracks did not just
silence failures, it removed the only episodes whose alignment was
genuinely indeterminate.

**THE COST, stated plainly and to be repeated in any writeup: SIM-POC now
trains on TWO layouts, not four.** The layout-split premise (Appendix L/M)
survives - two training layouts and one entirely unseen holdout is a valid
held-out-layout design, and far stronger than a random frame split - but it
is thinner than "four tracks" and that phrase must never be used. Layout
diversity is properly a REAL-CAR concern (M3/M4), where the physical tile
configurations are the layouts that matter and where Evan controls how many
exist.

**Corpus-size deviation being closed rather than argued.** At 71,662 frames
the corpus sat at 72% of the PRD's ~100k target (a figure inherited from
V-D4RL's offline-visual benchmark standard). Rather than redefine the target
as satisfied - the failure mode this record exists to prevent - a further
13 episodes per healthy track were launched at ~00:11 CDT, projected to land
near 101k. **P2 remains NOT done until that lands and re-verifies.** If it
finishes below target for any reason, the shortfall gets recorded as a
deviation, not absorbed.

**HONEST OPEN ITEMS:** (1) Top-up collection in flight; P2 not closed.
(2) Audit items still outstanding: quality thresholds unenforceable at rest
(F7), the empty `data.md` bin (F18), edge cases E8-E12. (3) Per-track
imbalance persists within the surviving two - `generated-track` supplies 38
of 52 train episodes - so even the two-layout claim is unbalanced, and the
top-up collects both tracks equally to narrow that. (4) The lag constants and
`MIN_PEAK_CORR = 0.50` are calibrated on this simulator only and must be
re-measured for the real car. (5) **Nothing printed, nothing ordered** - and
two decisions remain open from Appendix O: the encoder motor (#5159, +$6,
which unblocks ordering) and the ~1:20 track re-spec (which unblocks
printing).


# Appendix R - SIM-POC P2 CLOSED: 102,888 frames, 88/88 verified on both axes (2026-08-06, ~00:40 CDT)

**WHAT:** The top-up collection landed and **P2 is done, above its own
target, with no deviation to record.** 26 of 26 episodes saved, zero
rejected. Final verification, real output:

    holdout  :  10 episodes,   11210 frames, tracks ['donkey-waveshare-v0']
    train    :  78 episodes,   91678 frames, tracks ['donkey-generated-roads-v0', 'donkey-generated-track-v0']
      split is disjoint      : no track appears on both sides
    total frames: 102888
    alignment:
      exact PID identity     : verified on 88/88 episode(s), every action reproduced from log_cte
      image-axis gate        : 88/88 episodes in band (-2, -1), lag distribution {-2: 29, -1: 59}, mode -1 (|r| 0.74-0.96)
    P2 CORPUS CHECK: PASS

**Against the PRD's ~100k-frame target: 102,888. Met, not redefined.** At
the point the two bad tracks were quarantined the corpus sat at 71,662 (72%
of target), and the tempting move was to declare that sufficient. Collecting
the remainder cost ~30 minutes of unattended wall-clock and removed the need
to argue about it at all.

**Final composition:**

| Split | Track | Episodes | Frames |
|---|---|---|---|
| train | generated-track | 51 | 60,051 |
| train | generated-roads | 27 | 31,627 |
| holdout | waveshare (never trained on) | 10 | 11,210 |
| | **total** | **88** | **102,888** (3.80 GB) |

**What P2 actually established** - the point of the milestone was never the
data, it was proving the pipeline and retiring flagged unknowns:
- The dreamerv3-torch episode format round-trips, and its `offline_traindir`
  path exists in source (Appendix E flagged it as verified-in-source but
  never verified-to-run; **that remains true - P3/P4 will exercise it**).
- The layout split is enforced mechanically, not by intention: the verifier
  reads `log_track` back out of every episode and fails on any track
  appearing on both sides.
- Frame/action alignment is gated on **two independent axes**, with the
  approximate one's limits documented rather than overclaimed.
- The done-check runs in **O(1) memory** (0.10 GB measured at 76k frames),
  so it will not die as the corpus grows toward M4's 200k.

**Data contract now recorded where a future session will find it.** The
audit's F18 (the `data.md` bin still said "empty, no code yet" while the npz
schema WAS the project's data contract) is fixed: `data.md` now carries the
on-disk format, all seven required keys, the t=0 convention, the
terminal-vs-truncation distinction, both alignment gates with their measured
constants, the split rule, and an explicit warning that **every constant is
simulator-calibrated and must be re-measured for the real car.**

**HONEST OPEN ITEMS:** (1) Train remains **unbalanced 51:27** toward
`generated-track`, and it is **two layouts, not four** - both stated in the
PRD, the bin, and the code comment so no writeup can claim otherwise.
(2) Audit items still outstanding: quality thresholds unenforceable at rest
(F7), edge cases E8-E12, no linter or test suite (F20). (3) P3 (Ha &
Schmidhuber V+M+C) is the next PRD task and has not started. (4) **Nothing
printed, nothing ordered** - and the two decisions that unblock physical
progress are still open: the encoder motor (#5159, +$6) and the ~1:20 track
re-spec. The software lane has now run three milestones ahead of the
hardware lane, which was the plan's intent while parts shipped - but no
parts have been ordered to ship.


# Appendix S - SIM-POC P3 DONE: a working world model, and the domain gap it exposed (2026-08-06, ~01:18 CDT)

**WHAT:** P3 complete. The Ha & Schmidhuber V+M+C world model
(arXiv:1803.10122) trains on the P2 corpus and produces **30-step imagination
rollouts that are recognisably track-like and measurably better than a
do-nothing baseline** - the PRD's done-check, met with a number rather than a
vibe. Total training time on the RTX 3060 Ti: **VAE 198 s + MDN-RNN 140 s =
under 6 minutes**, nowhere near the 8 GB ceiling.

New files: `ml/preprocess.py`, `ml/splits.py`, `ml/models.py`,
`ml/train_vae.py`, `ml/train_mdnrnn.py`, `ml/rollout_eval.py`.

## S.1 - Architecture reproduces the paper exactly

| Component | Params | Note |
|---|---|---|
| ConvVAE (V) | **4,348,547** | **exact match to the paper's published figure** |
| MDN-RNN (M) | 382,533 | paper reports 422,368 for CarRacing, which used a 3-dim action; this uses 2, so smaller is expected and NOT claimed as a match |
| total | 4,731,080 | |

The VAE count is asserted in `models.self_check()`. Reproducing a published
parameter count to the digit proves every kernel size and channel width is
wired as specified - something reading the code cannot establish.

## S.2 - THE METHODOLOGICAL CORRECTION (the most important part of P3)

**A first VAE run reported what looked like textbook overfitting** - train
reconstruction falling 221 -> 55 while holdout error bottomed at ~390 and
then ROSE to ~415. That reading was WRONG, and it was wrong because the
evaluation had only two splits.

The holdout track (`waveshare`) is **indoor** - pale walls, a ladder, orange
lane lines on a light floor - while both surviving training tracks are
**outdoor** road scenes with trees and sky. So "unseen track" was silently
also "unseen visual domain", and the two questions were confounded.

Added a **third split** (`ml/splits.py`): `val_indomain`, held-out whole
EPISODES of the training tracks - unseen trajectories, seen domain,
stratified by track so no layout drops out of training. Re-run:

| Split | epoch 1 | epoch 40 | question it answers |
|---|---|---|---|
| fit | 236.6 | **56.11** | did it fit |
| val_indomain | 138.3 | **56.72** | did it learn, or memorise these runs |
| holdout | 426.3 | **412.0** (flat) | does it transfer to a new domain |

**val_indomain tracks fit almost exactly - a gap of 0.6.** There is no
overfitting. The model generalises fine to unseen trajectories and simply
cannot render a visual domain it has never seen. That is a domain gap, and
the earlier entry's implied "overfitting" reading is corrected here.

Worth stating plainly: **a random frame split would have shown fit == val and
declared success; a two-way layout split showed what looked like a broken
model; only the three-way split gives the true answer.** Both wrong readings
were available and I published the second one before catching it.

## S.3 - Rollout results: the done-check, with a baseline

Protocol: warm the LSTM on 32 real frames (teacher forcing), then cut the
frames off and imagine 30 steps, feeding predicted z back in **while
following the real recorded actions** - so any divergence is the dynamics
model failing, not a policy disagreeing. 8 episodes per split.

**The baseline is what makes this a claim.** Every frame of a driving corpus
looks vaguely road-like, so "the rollout looks like a track" proves nothing
alone. Error is therefore reported against a *freeze the last real frame*
predictor.

| | step 1 | 5 | 10 | 15 | 30 | beats baseline |
|---|---|---|---|---|---|---|
| **val_indomain** image MSE | 0.0047 | 0.0057 | 0.0071 | 0.0066 | 0.0068 | **30/30 steps** |
| val_indomain frozen baseline | 0.0102 | 0.0229 | 0.0281 | 0.0314 | 0.0313 | |
| val_indomain latent L2 | 4.22 | 4.66 | 4.53 | 4.64 | 5.14 | |
| **holdout** image MSE | 0.0416 | 0.0522 | 0.0645 | 0.0834 | 0.1052 | **0/30 steps** |
| holdout frozen baseline | 0.0115 | 0.0349 | 0.0493 | 0.0520 | 0.0592 | |

**In-domain: a real world model.** Image error is essentially FLAT across 30
imagined steps (0.0047 -> 0.0068) while the frozen baseline degrades 3x. The
latent trajectory grows slowly and does not diverge. Saved panels
(`rollout_val_indomain.png`) show road geometry, the yellow centre line, the
tree line and the horizon all surviving 30 steps of pure imagination -
blurry, as a 32-dim latent must be, but structurally correct.

**Cross-domain: actively worse than doing nothing.** On the holdout the model
loses to the frozen-frame baseline at every single step, and the panel shows
why - it hallucinates green trees and blue sky onto an indoor scene. The
world model does not merely fail to transfer; it confidently predicts the
wrong world.

**P3 DONE-CHECK: PASS on val_indomain** ("multi-step latent rollouts on
held-out data are recognisably track-like"), with the cross-domain failure
recorded as the honest limit rather than omitted.

## S.4 - A measurement inconsistency, flagged not hidden

MDN-RNN final: fit NLL **27.52**, val_indomain **12.85**, holdout **64.24**
(rising). Validation NLL being LOWER than training NLL is not a miracle - it
is an artifact: training samples z ~ N(mu, sigma) for both input and target
(a noisier target, hence higher NLL), while evaluation uses the posterior
mean for both. **fit and val_indomain NLL are therefore not comparable to
each other.** The val-vs-holdout comparison IS valid, since both use the
mean. Fixing this would mean evaluating on sampled targets too; left as-is
and documented, because the comparison P3 needs is val-vs-holdout.

## S.5 - What this buys P4 and M4

- The pipeline is proven end to end on real data: corpus -> 64x64 tensors ->
  latents -> dynamics -> imagination -> decoded pictures -> a metric.
- **Portfolio artifact #1 is banked** and it is independent of whether
  DreamerV3-S fits in 8 GB at P4 - which was the entire point of building the
  small model first.
- The three-way split, the frozen-frame baseline, and the seeded determinism
  are all reusable for P4 and for M3/M4 on the real car.
- Headroom is enormous: under 6 minutes of training and a small fraction of
  8 GB. P4 has room.
- **The domain-gap result transfers as a warning to the real car:** two
  training layouts were not enough to cover a third that merely looked
  different. On the physical track, tile configurations that change the
  *appearance* (lighting, surroundings) - not just the geometry - will need
  to be in the training set, or the same failure recurs.

**HONEST OPEN ITEMS:** (1) Rollouts are blurry - inherent to a 32-dim latent
plus an L2 VAE, not a bug, but it caps how much fine road detail the model
can represent. (2) Only ONE seed was trained. The routing research recorded
that seed variance in driving policies can reach tens of points, so any
comparison at P4/P5 needs >=3 seeds; P3 as a pipeline proof does not.
(3) The MDN-RNN NLL inconsistency above. (4) `testing.md` bin still not
populated. (5) Nothing printed, nothing ordered - the encoder-motor and
~1:20 track re-spec decisions remain open and continue to block all physical
progress.

