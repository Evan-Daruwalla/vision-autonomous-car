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
- [T — SIM-POC P4: the 8GB DreamerV3 boundary measured; two task premises proved false; repo goes public](#appendix-t---sim-poc-p4-the-8gb-dreamerv3-boundary-measured-two-task-premises-proved-false-repo-goes-public-2026-08-06-1329-cdt) (08-06)
- [U — SIM-POC P4 CLOSED: the model trains; the memory boundary holds over a long run](#appendix-u---sim-poc-p4-closed-the-model-trains-the-memory-boundary-holds-over-a-long-run-2026-08-06-1336-cdt) (08-06)
- [V — Cold audit fixed; knowledge graph built; SIM-POC P5 CLOSED as an instrumented negative result](#appendix-v---cold-audit-fixed-4-gates-that-could-not-fail-knowledge-graph-built-sim-poc-p5-closed-as-an-instrumented-negative-result-2026-08-07-0555-cdt) (08-07)
- [W — The wall diagnosed (perception goes OOD); both encoders erase small objects, threatening the M4 stop-sign showcase](#appendix-w---the-wall-diagnosed-perception-goes-ood-both-encoders-erase-small-objects-so-the-m4-stop-sign-showcase-is-threatened-2026-08-08-2252-cdt) (08-08)
- [X — Recovery data fixes off-centre perception 57% with a frozen encoder; steering smoothness works but does not fix the wall](#appendix-x---recovery-data-fixes-off-centre-perception-by-57-with-a-frozen-encoder-the-steering-smoothness-knob-works-but-does-not-fix-the-wall-2026-08-08-2311-cdt) (08-08)
- [Y — The stop-sign decision, and an AUC of 0.997 that meant nothing](#appendix-y---the-stop-sign-decision-and-an-auc-of-0997-that-meant-nothing-2026-08-10-1853-cdt) (08-10)
- [Z — The aux head works; the research brief kills H3; the closed-loop metric was never reproducible](#appendix-z---the-aux-head-works-the-research-brief-kills-h3-and-the-closed-loop-metric-was-never-reproducible-2026-08-10-1924-cdt) (08-10)
- [AA — Recovery data is not the fix, and the loss weight is not either: the wall is upstream](#appendix-aa---recovery-data-is-not-the-fix-and-the-loss-weight-is-not-either-the-wall-is-upstream-2026-08-10-2007-cdt) (08-10)
- [AB — ~~FIRST COMPLETED EPISODES~~ **[RETRACTED — see AC]**: the controller was ignoring z, and recovery data only pays once the crutch is removed](#appendix-ab---first-completed-episodes-the-controller-was-ignoring-z-and-recovery-data-only-pays-once-the-crutch-is-removed-2026-08-11-0021-cdt) (08-11)
- [AC — **RETRACTION of AB**: the "first completed episodes" result did not replicate; the closed-loop harness is not trustworthy](#appendix-ac---retraction-of-ab-the-first-completed-episodes-result-did-not-replicate-and-the-closed-loop-harness-is-not-trustworthy-2026-08-11-1821-cdt) (08-11)
- [AD — Harness noise floor MEASURED (CV 55%): the reset is exonerated and every comparison this session was underpowered](#appendix-ad---the-harness-noise-floor-measured-cv-55-and-every-comparison-this-session-was-underpowered-2026-08-11-2329-cdt) (08-11)
- [AE — Corrections to AD, and a better harness fix than AD proposed: pair the design, the outcome is censored, and the CV needs its interval](#appendix-ae---corrections-to-ad-and-a-better-fix-for-the-harness-than-the-one-ad-proposed-2026-08-12-0724-cdt) (08-12)
- [AF — AE corrected the record and forgot the live docs, which is the error AE was correcting](#appendix-af---ae-corrected-the-record-and-forgot-the-live-docs-which-is-the-error-ae-was-correcting-2026-08-12-0735-cdt) (08-12)
- [AG — Evan's build decisions, the operating point measured, and the camera nobody configured](#appendix-ag---evans-build-decisions-the-operating-point-measured-and-the-camera-nobody-configured-2026-08-12-2048-cdt) (08-13)
- [AH — The camera was never the constraint; the PWM pin was, and it breaks the Pi 5 too](#appendix-ah---the-camera-was-never-the-constraint-the-pwm-pin-was-and-it-breaks-the-pi-5-too-2026-08-12-2148-cdt) (08-12)
- [AI — The track regenerates every launch (the harness mystery, solved), and the sim FOV is 90](#appendix-ai---the-track-regenerates-every-launch-that-is-the-harness-mystery-solved-and-the-sim-fov-is-90-2026-08-13-0056-cdt) (08-13)
- [AJ — The closed-loop comparison, re-run PAIRED and finally valid: no intervention helps](#appendix-aj---the-closed-loop-comparison-re-run-paired-and-finally-valid-no-intervention-helps-2026-08-13-1547-cdt) (08-13)
- [AK — Scheduled daily-audit: the sim FOV that AI identified by comparison is now pinned in code, and a secret gate is wired](#appendix-ak---scheduled-daily-audit-the-sim-fov-that-ai-identified-by-comparison-is-now-pinned-in-code-and-a-secret-gate-is-wired-2026-08-16-1328-cdt) (08-16)
- [AL — Scheduled daily-audit: 23 findings; three cache readers skip the encoder fingerprint, and the record guard's missing-file branch fails OPEN under a "Fails CLOSED" comment](#appendix-al---scheduled-daily-audit-23-findings-three-cache-readers-skip-the-encoder-fingerprint-and-the-record-guards-missing-file-branch-fails-open-under-a-fails-closed-comment-2026-08-25-0721-cdt) (08-25)
- [AM — 3DStreet wired for the track layout, and the AL audit fixes found sitting uncommitted](#appendix-am---3dstreet-wired-for-the-track-layout-and-the-al-audit-fixes-found-sitting-uncommitted-2026-09-01-1512-cdt) (09-01)
- [AN — Floor space is 3x3 m; car width must be measured not chosen; and the lane-width rule was over-provisioned](#appendix-an---floor-space-is-3x3-m-car-width-must-be-measured-not-chosen-and-the-lane-width-rule-was-over-provisioned-2026-09-01-1531-cdt) (09-01)
- [AO — The AL audit fixes, run: the encoder-fingerprint guard is a false negative and breaks train_cte_probe.py](#appendix-ao---the-al-audit-fixes-run-the-encoder-fingerprint-guard-is-a-false-negative-and-breaks-train_cte_probepy-2026-09-01-1546-cdt) (09-01)
- [AP — Option 1 applied: load_cached_mu resolves three states, and every runnable AL-touched reader re-run](#appendix-ap---option-1-applied-load_cached_mu-resolves-three-states-and-every-runnable-al-touched-reader-re-run-2026-09-01-1550-cdt) (09-01)
- [AQ — CORRECTION to AP.5: ml/data/sim was never missing - verify_corpus.py's cwd-relative default was, and P2 re-verified PASS](#appendix-aq---correction-to-ap5-mldatasim-was-never-missing---verify_corpuspys-cwd-relative-default-was-and-p2-re-verified-pass-2026-09-01-1555-cdt) (09-01)
- [AR — Sim camera pose: the FOV trick does not extend to extrinsics; fov proved VERTICAL, pitch measured 16.3 deg down, height NOT identified](#appendix-ar---sim-camera-pose-the-fov-trick-does-not-extend-to-extrinsics-fov-proved-vertical-pitch-measured-163-deg-down-height-not-identified-2026-09-01-1610-cdt) (09-01)
- [AS — Reference lookup: LEGO Technic rack-and-pinion steering, set 42111 as the donor precedent](#appendix-as---reference-lookup-lego-technic-rack-and-pinion-steering-set-42111-as-the-donor-precedent-2026-09-01-1725-cdt) (09-01)
- [AT — Track layout v1: twisty is geometrically impossible at 3x3 m, the bridge cannot be an overpass, and the destinations are landmarks not junctions](#appendix-at---track-layout-v1-twisty-is-geometrically-impossible-at-3x3-m-the-bridge-cannot-be-an-overpass-and-the-destinations-are-landmarks-not-junctions-2026-09-01-2012-cdt) (09-01)
- [AU — Scheduled daily-audit: AP/AQ/AR/AS re-verified against disk, 3 findings, and a stale artifact that would mislead the next auditor](#appendix-au---scheduled-daily-audit-apaqaras-re-verified-against-disk-3-findings-and-a-stale-artifact-that-would-mislead-the-next-auditor-2026-09-01-2014-cdt) (09-01)
- [AV — Record letter-collision race repaired, and the AU audit's two findings against AR's artifacts fixed](#appendix-av---record-letter-collision-race-repaired-and-the-au-audits-two-findings-against-ars-artifacts-fixed-2026-09-01-2018-cdt) (09-01)
- [AW — CORRECTION to AV.1: the append script was never the race; the daily-audit prompt never named it. Prompt fixed and a write-time guard added](#appendix-aw---correction-to-av1-the-append-script-was-never-the-race-the-daily-audit-prompt-never-named-it-prompt-fixed-and-a-write-time-guard-added-2026-09-01-2036-cdt) (09-01)
- [AX — Track v2: a 3x3 city grid that fits only at R=500mm, the sim cannot rehearse it, and the 225-panel floor is refused (my filament figure was 2.7x too high)](#appendix-ax---track-v2-a-3x3-city-grid-that-fits-only-at-r500mm-the-sim-cannot-rehearse-it-and-the-225-panel-floor-is-refused-my-filament-figure-was-27x-too-high-2026-09-01-2100-cdt) (09-01)
- [AY — CORRECTION to AX.2: the street pitch never needed a lane term, so the city fits at R=500/550/600; v2 shrunk; lighting spec settles the PCA9685](#appendix-ay---correction-to-ax2-the-street-pitch-never-needed-a-lane-term-so-the-city-fits-at-r500550600-v2-shrunk-lighting-spec-settles-the-pca9685-2026-09-01-2106-cdt) (09-01)
- [AZ — PCA9685 and lighting added to the BOM: the $200 ceiling is breached on every path, and the wiring rule was already self-contradictory](#appendix-az---pca9685-and-lighting-added-to-the-bom-the-200-ceiling-is-breached-on-every-path-and-the-wiring-rule-was-already-self-contradictory-2026-09-01-2139-cdt) (09-01)
- [BA — Vehicle envelope derived (height provably blocked); camera height attempt 2 is a second negative and the curvature hypothesis is refuted; indicator logging lands](#appendix-ba---vehicle-envelope-derived-height-provably-blocked-camera-height-attempt-2-is-a-second-negative-and-the-curvature-hypothesis-is-refuted-indicator-logging-lands-2026-09-01-2204-cdt) (09-01)
- [BB — claude CLI verified installed, and the 3dstreet MCP blocker was pending APPROVAL all along - not a restart and not the browser tab](#appendix-bb---claude-cli-verified-installed-and-the-3dstreet-mcp-blocker-was-pending-approval-all-along---not-a-restart-and-not-the-browser-tab-2026-09-01-2214-cdt) (09-01)
- [BC — Arduino Uno supersedes the PCA9685 one day old: encoder counting and a watchdog for $0, the $200 ceiling is reachable again, and the record write-guard is confirmed firing](#appendix-bc---arduino-uno-supersedes-the-pca9685-one-day-old-encoder-counting-and-a-watchdog-for-0-the-200-ceiling-is-reachable-again-and-the-record-write-guard-is-confirmed-firing-2026-09-02-1520-cdt) (09-02)
- [BD — First verified hardware: the Uno runs our firmware (signature 1E 95 0F, F_CPU 16 MHz), and an FTDI clone needs an explicit --fqbn forever](#appendix-bd---first-verified-hardware-the-uno-runs-our-firmware-signature-1e-95-0f-f_cpu-16-mhz-and-an-ftdi-clone-needs-an-explicit---fqbn-forever-2026-09-02-1526-cdt) (09-02)
- [BE — SRAM measured at 2048 B and the clock at 16.0042 MHz; CORRECTION to BD (F_CPU was never measured), and the silicon's signature says 328PB while avrdude says 328P](#appendix-be---sram-measured-at-2048-b-and-the-clock-at-160042-mhz-correction-to-bd-f_cpu-was-never-measured-and-the-silicons-signature-says-328pb-while-avrdude-says-328p-2026-09-02-1541-cdt) (09-02)
- [BF — FTDI latency timer measured: configured at 16 ms but costs ~0.9 ms on the wire, so the risk flagged in BD and BE was wrong](#appendix-bf---ftdi-latency-timer-measured-configured-at-16-ms-but-costs-09-ms-on-the-wire-so-the-risk-flagged-in-bd-and-be-was-wrong-2026-09-02-1550-cdt) (09-02)
- [BG — Serial protocol v0.1 drafted, and drafting it caught D3 double-booked between the encoder interrupt and motor PWM in yesterday's diagram](#appendix-bg---serial-protocol-v01-drafted-and-drafting-it-caught-d3-double-booked-between-the-encoder-interrupt-and-motor-pwm-in-yesterdays-diagram-2026-09-02-1558-cdt) (09-02)
- [BH — landing-check returned FIX FIRST: nine items closed, including a wrong PWM budget the D3 fix silently created and a stale price in the public README](#appendix-bh---landing-check-returned-fix-first-nine-items-closed-including-a-wrong-pwm-budget-the-d3-fix-silently-created-and-a-stale-price-in-the-public-readme-2026-09-02-1611-cdt) (09-02)
- [BI — Rows 11/13/14 linked, and row 11's board does NOT document the over-discharge protection the BOM credited it with - the 2S pack has no low-voltage cutoff](#appendix-bi---rows-111314-linked-and-row-11s-board-does-not-document-the-over-discharge-protection-the-bom-credited-it-with---the-2s-pack-has-no-low-voltage-cutoff-2026-09-02-1634-cdt) (09-02)
- [BJ — Pack low-voltage cutoff implemented on the Uno: 27/27 on hardware, and the hardware test caught a floating-pin fault the design reasoning had missed](#appendix-bj---pack-low-voltage-cutoff-implemented-on-the-uno-2727-on-hardware-and-the-hardware-test-caught-a-floating-pin-fault-the-design-reasoning-had-missed-2026-09-02-1647-cdt) (09-02)

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


---

# Appendix T - SIM-POC P4: the 8GB DreamerV3 boundary measured; two task premises proved false; repo goes public (2026-08-06, ~13:29 CDT)

**WHAT:** SIM-POC P4 executed. The measured-boundary half of its done-check is
met and verified; the trained-model half was still running when this entry was
written and is explicitly NOT claimed. The project also got its first public
GitHub repo. Commit `1b1b790`; repo
https://github.com/Evan-Daruwalla/vision-autonomous-car (public, default
branch `main`).

New files: `README.md`, `ml/probe_vram.py`, `ml/prep_dreamer_corpus.py`,
`ml/run_dreamer_p4.py`, `ml/sweep_dreamer_p4.py`, and a new codebase-memory
bin `.claude/codebase-memory/ml-training.md`.

## T.1 The number the 2026-07-23 research said nobody had published

RTX 3060 Ti, 8.0 GB, driver 610.62, 64x64 input, fp32, 20 warm steps,
PyTorch allocator capped at 7.0 GB. Source of truth:
`ml/runs/dreamer_p4/sweep_summary.json`; regenerate with
`python ml/sweep_dreamer_p4.py`.

| config | params (unique) | peak VRAM | % of 8 GB | status |
|---|---|---|---|---|
| S, batch 16, horizon 5 | 19,101,317 | **2.552 GB** | 31.9% | fits |
| S, batch 32, horizon 5 | 19,101,317 | 4.793 GB | 59.9% | fits |
| S, batch 64, horizon 5 | 19,101,317 | - | - | **OOM >7.0 GB** |
| S, batch 16, horizon 15 | 19,101,317 | 3.873 GB | 48.4% | fits |
| M, batch 16, horizon 5 | 35,299,397 | 3.729 GB | 46.6% | fits |
| L, batch 16, horizon 5 | 69,654,533 | 5.238 GB | 65.5% | fits |

**Headline: batch size, not model size, is what breaks 8 GB.** A 69.7M-param
model fits in 5.238 GB while the 19.1M model at batch 64 does not fit in 7.0.
Tripling the imagination horizon (5 -> 15) costs 1.3 GB, MORE than nearly
doubling the parameter count (S -> M costs 1.2 GB). Activations dominate;
weights are close to free at this scale. **8 GB holds roughly 3.6x the model
the retracted "~24 GB" figure implied** (that retraction is Appendix E).

**Scope limit stated honestly:** only "S" is a verified size. It is the
vendored repo's `defaults` block verbatim, and its 17,919,878 trainable params
match the 2026-07-23 brief's "~18M" for DreamerV3-S. **XS/M/L are scaling
steps defined in `run_dreamer_p4.py` and were NOT checked against the paper's
published size table.** The code, the bin, and the README all say so. Cite the
measured parameter counts, never the letters. This entry does not claim a
reproduction of the paper's size ladder.

## T.2 Two premises written into the P4 task were false

Both are now measured facts, and `PRD_ROADMAP.md` was amended in place per the
append-mostly rule rather than rewritten.

**(a) `offline_traindir` does not run dreamerv3-torch without an environment,
and the repo has no offline training loop at all.** Verified by reading the
vendored source at commit `6ef8646d807cd10ce0c88e10a7e943211e7fc44c`:
`dreamer.main()` builds `train_envs`/`eval_envs` **unconditionally**
(dreamer.py:238-241), and the training loop is
`tools.simulate(agent, train_envs, ...)` (dreamer.py:319) - train steps are
driven by ENV steps, because the agent trains inside `Dreamer.__call__`, which
`simulate` invokes once per environment transition. The flag only warm-starts
the replay buffer from disk.

This **retires the 2026-07-23 research's flagged unknown (a) with a NO** -
that unknown was one of the three things SIM-POC existed to settle early
(Appendix J). Running P4 as originally specified would have required either
the Unity sim live (not offline, and it would have dominated the memory
measurement) or a fake env feeding garbage transitions into the buffer
alongside the real corpus.

`Dreamer._train(batch)` needs no environment, so `ml/run_dreamer_p4.py`
supplies the two things `main()` was using the envs for - hand-built gym
observation/action spaces - plus a genuine offline loop, and **leaves
`ml/vendor/` unpatched** so it can be re-pulled.

**(b) "Sysmem Fallback disabled before the first run" never happened, and it
is still ON.** `ml/probe_vram.py` allocated **10.0 GB on the 8 GB card without
raising OutOfMemoryError**. The 2026-07-23 research predicted this as a risk
(gotchas.md); it is now confirmed as the live state on this machine. **Any
OOM-boundary claim measured in that state is worthless** - an over-budget run
does not crash, it spills to host RAM over PCIe and gets slower.

Changing a driver setting is Evan's call and is not something this repo does,
so the requirement was met differently: `torch.cuda.set_per_process_memory_
fraction` caps PyTorch's own allocator, and was **measured to still raise OOM
under active fallback** (OOM at 1.750 GB under a 2.0 GB cap). This is
strictly better for the project than the control-panel fix - it lives in
version control and is reproducible on any machine, where a checkbox is
neither. Exposed as `--cap-gb`.

## T.3 The mistake: I ran the wrong experiment first and had to kill it

**Symptom:** the first sweep hung. **Root cause:** it was run UNCAPPED, so the
batch-64 config never failed - it pinned the card at ~7.93 GB / 100%
utilization for **over twenty minutes** without finishing the 20 steps that
batch 32 finished in 71 s. **Fix:** cap every sweep run, which turns the hang
into an immediate deterministic OOM; the full 6-config sweep then finishes in
about two minutes.

That is the documented "silent ~3x slowdown" gotcha demonstrating itself on
real hardware rather than in a research note. The lesson now recorded in the
bin: **a config that spills is worse than one that OOMs, because it looks like
it is working.** `sweep_dreamer_p4.py` no longer has an uncapped mode by
default.

## T.4 Three smaller corrections caught before they hardened

1. **Parameter double-count.** `ImagBehavior` holds a *reference* to the world
   model, so a naive sum over `agent._task_behavior.parameters()` re-counted
   all 15.7M world-model params and reported the model at roughly double its
   real size (34,787,080 instead of 19,101,317). Caught by checking against
   the repo's own printed optimizer sizes (15,685,763 + 1,052,676 +
   1,181,439 = 17,919,878 trainable). Fixed by deduplicating on `id(p)`.
2. **Timings are warm-run only.** The identical config measured **63.0 s cold
   and 11.1 s warm** for 20 steps (CUDA kernel autotuning on first execution).
   Peak memory was byte-identical across both runs, so **memory is stable and
   time is not** - the sweep's seconds column must never be quoted as absolute
   throughput.
3. **A fabricated commit hash, reported to Evan.** In a chat summary the P4
   commit was cited as `a1b1247`. That hash was never read from git; the real
   one is `1b1b790`. Nothing downstream depended on it, but it is logged here
   because inventing an identifier is exactly the failure the standing "DO NOT
   MAKE ANYTHING UP" rule exists to catch, and a correction that only lives in
   chat does not exist.

## T.5 Verified rather than assumed: P4 trains on P3's exact split

`ml/prep_dreamer_corpus.py` re-derives the split from the raw corpus, so there
was a real risk of it silently differing from the arrays P3 consumed. Asserted
directly: episode ORDER identical across both derivations (78 episodes), the
seed-0 fit/val split identical (66 fit / 12 val), the on-disk dreamer
directories exactly match that split, and train/eval are disjoint. **PASS.**
Any P3-vs-P4 comparison is therefore about the model and not the data.

Corpus written for Dreamer: 66 fit episodes / 77,266 frames + 12 val episodes
/ 14,412 frames. With the untouched 11,210-frame holdout that reconciles to
the P2 total of 102,888.

## T.6 First public repo

https://github.com/Evan-Daruwalla/vision-autonomous-car - **public**, default
branch `main` (renamed from `master` at Evan's request after creation).

Pre-publication checks, in this order: the secret scanner's own canary
self-test (**PASS**, 7 real secrets caught, 0 false positives - an unverified
scanner reporting "clean" is theater), then a full-history scan (**clean, 0
findings**), then a staged-diff scan (**clean**). The tracked file list was
also read by eye: no `.env`, no keys, no data dumps; largest tracked file is
the 884 KB coupon STL.

`README.md` leads with the honest status - *"the software is real and
measured. The car is not built."* It carries the P3 rollout table, the T.1
memory table, and a section on the three findings that cost a wrong answer
first (the two-way split, the fake verification gate, the retracted 24 GB
figure). Reviewed for AI texture before publishing since it is outward-facing
prose; four flags fixed.

`.gitignore` gained `*.tfevents.*` - TensorBoard files are regenerable, binary,
and written incrementally, so a commit taken mid-run captures a truncated one.
The json/png artifacts beside them are the evidence.

## T.7 Bin reorganization

`gotchas.md` was past its ~150-line cap and had become two domains, so GPU and
world-model training facts moved to a new **`ml-training.md`** bin (the bin
protocol allows a new specifically-named bin, never a catch-all). `gotchas.md`
keeps dated corrections that point at it: the `offline_traindir` entry is now
partially superseded, and the Sysmem Fallback entry is upgraded from desk
research to measured-and-still-enabled. `INDEX.md` updated.

## T.8 Open items, stated as open

1. **The 2000-step training run was still in flight when this entry was
   written** (started 12:53:15 CDT, ~36 min elapsed, GPU busy). P4's
   done-check already passes on the boundary half, which the PRD accepts
   alone - but **"a trained model" is not claimed anywhere** until its loss
   curve is read. The PRD says so explicitly rather than leaving it implied.
2. Sysmem Fallback remains ON. Every future memory measurement must use
   `--cap-gb` or repeat T.2(b)'s mistake.
3. XS/M/L size labels remain unverified against the paper.
4. Cadence: this entry covers prompts through #33. The P3 entry (Appendix S)
   already covered the prior block, so no cadence was missed.
5. **Nothing printed, nothing ordered** - unchanged since 2026-07-23. The
   encoder-motor decision and the ~1:20 track re-spec still block all physical
   progress, and the public README now says so where anyone can read it.


---

# Appendix U - SIM-POC P4 CLOSED: the model trains; the memory boundary holds over a long run (2026-08-06, ~13:36 CDT)

**WHAT:** Closes the one open item Appendix T left explicitly unresolved
(T.8 item 1). The 2000-step DreamerV3-S offline run finished, exit 0.
**P4's done-check now passes on BOTH halves, each verified.** Artifact:
`ml/runs/dreamer_p4/S_b16_train2000/p4_result.json`.

**Appendix T deliberately refused to write "a trained model" while that run
was in flight.** This entry is what earns the word.

## U.1 It trains

DreamerV3-S, batch 16 x 64, imagination horizon 5, fp32, 7.0 GB allocator cap,
on the full 66-episode / 77,266-frame fit split.

| | epoch 1 | epoch 4 | epoch 10 | epoch 20 |
|---|---|---|---|---|
| image reconstruction loss | 588.31 | 123.73 | 83.18 | **61.39** |
| kl | 8.996 | 5.681 | 9.134 | 9.485 |
| peak VRAM (GB) | 2.552 | 2.550 | 2.551 | 2.551 |

**Image reconstruction loss fell 588.31 -> 61.39, a 9.6x reduction**, and fell
monotonically after the first epoch. The hand-written offline loop in
`ml/run_dreamer_p4.py` - built because the vendored repo has none at all
(Appendix T.2a) - genuinely trains the model rather than merely allocating
memory on it. Total 2000 gradient steps, no OOM.

**Not diagnosed, and stated as such:** `kl` fell to 5.68 by epoch 4, then rose
and plateaued near 9.5 while reconstruction kept improving. That is consistent
with the posterior encoding more information as the decoder sharpens
(`kl_free` is 1.0, so the loss term itself is clamped), but no check was run.
It must not be cited as evidence of healthy training without one.

## U.2 The control that matters more than the loss curve

**Peak VRAM held at 2.550-2.552 GB across all twenty epochs - a spread of
0.002 GB - and is identical to the figure the 20-step sweep reported.**

This is the result that hardens Appendix T.1's fitting table. A 20-step
measurement could plausibly have been a warm-up artifact that crept upward
once training ran for real; fragmentation and cache growth are exactly the
kind of thing that makes short memory probes lie. It did not creep. The table
is a steady-state measurement, and M4 can be planned against it.

## U.3 Wall-clock from this run is unusable, and why that is recorded anyway

Per-epoch time ran **119-527 s for the first seven epochs, then settled at
46-52 s for the remaining thirteen** - a 10x swing within one run at constant
configuration.

**Suspected cause, not proven:** an orphaned child process left over from the
sweep killed in Appendix T.3. `subprocess.run` children can outlive the shell
task that spawned them, so the killed batch-64 run may have still been holding
the GPU during this run's early epochs. No attempt was made to prove it after
the fact, and it is not worth re-running to find out.

The reason this is in the record rather than quietly dropped: it is a second,
independent demonstration of the same lesson as T.3 and the warm/cold finding
- **memory measurements survive GPU contention, timings do not.** Every
throughput number this project publishes needs an otherwise-idle card and an
`nvidia-smi` check first. Peak-allocated needs neither.

## U.4 SIM-POC status after P4

| task | state |
|---|---|
| P1 environment | DONE (2026-08-05) |
| P2 corpus | DONE - 102,888 frames, 88/88 verified both axes (Appendix R) |
| P3 Ha & Schmidhuber V+M+C | DONE - beats frozen-frame baseline 30/30 in-domain (Appendix S) |
| P4 DreamerV3-S offline | **DONE - both halves (Appendices T, U)** |
| P5 policy extraction + in-sim eval | not started |

**P5 is the only remaining SIM-POC task.** Note the standing constraint from
`testing.md`: P5 is a COMPARATIVE claim (learned policy vs the P2 scripted
driver), so it needs **>=3 seeds**, not the single seed P3 and P4 used as
pipeline proofs.

## U.5 Open items

1. `kl` behaviour undiagnosed (U.1).
2. Wall-clock unmeasured on an idle card (U.3).
3. XS/M/L size labels still unverified against the paper (T.1).
4. Sysmem Fallback still ON; every future memory measurement needs `--cap-gb`.
5. **Nothing printed, nothing ordered** - unchanged since 2026-07-23. The
   encoder-motor decision and the ~1:20 track re-spec still block all physical
   progress. Software is now four SIM-POC tasks ahead of hardware.


---

# Appendix V - Cold audit fixed (4 gates that could not fail); knowledge graph built; SIM-POC P5 CLOSED as an instrumented negative result (2026-08-07, ~05:55 CDT)

**CADENCE NOTE, stated rather than hidden:** the hook fired at prompts #36,
#39, #42, #45, #48 and #51 with no entry written. This entry covers all of it.
The miss was real: a long autonomous run was allowed to continue past six
cadence marks. Logged per the rule that misses are recorded, not smoothed.

**WHAT:** three blocks of work. (1) The cold audit's 15 findings and 10 edge
cases were fixed and verified. (2) A knowledge graph was built over the whole
project and then incrementally updated. (3) SIM-POC P5 was executed and closed
-- the pipeline works end to end and **no learned policy completes the track**,
which is the honest result and is recorded as such.

Commits: `f8a3c03` (audit fixes). P5 code is uncommitted at time of writing.

## V.1 The audit fixes, and the class of bug they all shared

Four P1s, every one a **gate that could not fail** while being documented as a
gate that could. Full detail in the commit message; the pattern is the point:

| what it claimed | what it did |
|---|---|
| `sweep_dreamer_p4.py` reports measured VRAM | inferred success from a committed file EXISTING, never reading the child's exit code |
| `rollout_eval.py` "exits non-zero on failure" (testing.md) | printed its win count and discarded it; 0/30 exited exactly like 30/30 |
| `gen_tolerance_coupon.py` output is "geometrically self-validated" (README) | wrote the STL *before* validating, always exited 0 |
| `models.py` "asserts it on every run" (README) | the assert lived in `self_check()`, which no training or eval run ever calls |

Plus the split-seed leak: `rollout_eval.py --seed 3` reported **12 of 12
"held-out" episodes that were training episodes** (`--seed 1`/`2`: 10 of 12),
because the split was re-derived from `--seed` while the checkpoints were
selected against seed 0. P5 needs >=3 seeds, so this was one flag away from
publishing train-on-test numbers as the SIM-POC finale.

**Every fix was verified by making it FAIL**, not by watching it pass: the
coupon was fed impossible geometry (refused to write, exit 1), `rollout_eval`
an unreachable threshold (exit 1), `preprocess` a simulated Ctrl-C (all four
outputs byte-identical afterwards), `verify_corpus` a malformed filename
(clean FAIL, not a traceback), the latent cache a wrong fingerprint (exit 1).

Also closed **F7, open since the 2026-08-05 audit**: the expert-quality
thresholds now enforce at rest in `verify_corpus.py`, not only at collection.

## V.2 Knowledge graph

`graphify-out/` (gitignored): **635 nodes, 930 edges, 54 communities** over 60
files. Full build cost 853,476 extraction tokens; the incremental `--update`
after the audit fixes cost 104,453 -- 8x cheaper for 15 changed files.

Two findings came out of the extraction agents rather than the graph:

1. **The VAE drops small salient objects.** Independently observed in two
   different artifacts by two agents that could not see each other's work:
   orange traffic cones vanish entirely from the FIT-split reconstruction
   grid, and a cone in the rollout panel survives only as a smudge. Since
   every downstream stage consumes only the latent, **anything built on this
   encoder is blind to small high-contrast objects.** That is a direct risk to
   the PRD's plan to make a stop sign the M4 world-model showcase -- a stop
   sign is exactly such an object. Not a verdict: DreamerV3's RSSM trains its
   encoder against reward and continuation rather than reconstruction alone,
   so it may not share the defect. Cheap to test before M4 depends on it.
2. **`val_indomain` holds out RUNS, not TRACKS.** On a closed circuit a
   held-out lap sees nearly the same views as a training lap, so parity with
   the fit split is a weak generalisation claim. **This qualifies Appendix S**,
   which said "the model generalises fine to unseen trajectories" -- the split
   is a valid CONTROL against the holdout (it proves the 7.3x holdout gap is a
   domain gap and not memorisation) but is not independent evidence of
   generalisation.

## V.3 SIM-POC P5 - policy extraction and in-sim evaluation

New: `ml/train_controller.py`, `ml/train_cte_probe.py`, `ml/eval_in_sim.py`,
`ml/plan_cem.py`. Artifacts in `ml/runs/controller/`, `ml/runs/cte_probe/`,
`ml/runs/p5_eval/`, `ml/runs/p5_cem/`.

### V.3.1 The eval table (P5's done-check)

`donkey-generated-track-v0`, 3 seeds x 3 episodes = 9 episodes each, 600-step
cap. Expert = the same PID lane-follower that produced the training corpus.

| driver | steps (mean+-sd) | mean\|cte\| | reversals/100 | completed |
|---|---|---|---|---|
| expert (PID) | **600.0 +- 0.0** | **0.367** | 9.87 | **9/9** |
| BC, linear C (paper-faithful) | 104.1 +- 66.5 | 1.043 | 8.50 | 0/9 |
| BC, MLP C | 69.3 +- 1.2 | 0.435 | 9.28 | 0/9 |
| CEM planning (Evan's cost) | 89.7 +- 3.3 | 0.551 | 20.90 | 0/9 |

**No learned policy completed a single episode. The expert completed all
nine.** That is the result. It is not dressed up.

### V.3.2 Three hypotheses tested; two falsified

**Falsified - "it swerves and overcompensates"** (Evan's read of the sim
window, 2026-08-07). Measured instead: the linear controller made **6.57
steering reversals per 100 steps against the expert's 7.67**, with a SMALLER
mean |dsteer| (0.107 vs 0.129). It steers less and more gently than the
expert while sitting 2.9x further off centre -- it drifts out and fails to
recover, the opposite of overcorrection. The observation was real; the
mechanism behind it was not what it looked like.

**Confirmed - the linear controller's failure is ARCHITECTURAL.** A linear
probe recovers only **R^2 = 0.27** of cross-track error from z; an MLP probe
recovers **0.97**. The latent carries lane position almost perfectly, but
NONLINEARLY -- so the paper's linear C structurally cannot compute the one
quantity lane-following depends on. Swapping to a one-hidden-layer MLP cut
offline action MSE 4.9x (0.00857 -> 0.00175) and **cut in-sim lane error 2.4x
to 0.435, essentially expert-level (0.381)**. It still did not finish.

**Falsified - "the wall is corner speed."** The MLP died at **69.3 +- 1.2
steps across nine episodes and three independently trained seeds** -- a
deterministic wall, not a stochastic drift. The project's own record
(Appendix M) established that throttle dominated the expert's tuning, so
lowering it was the obvious test. It does not help: at throttle 0.12 the
planner got *worse* (75, 63 steps), at 0.08 it was 111 and 74. Speed is not
the binding constraint.

### V.3.3 Evan's incentive proposal, and what it did

Asked 2026-08-07: "give the AI a large incentive to stay in the middle of the
track and a smaller incentive to keep sideways acceleration low."

**Behavioural cloning cannot take an incentive** -- it minimises distance to
recorded expert actions and has no notion of good or bad. Implementing the
idea therefore meant the PRD's other P5 option: **CEM planning through the
learned dynamics** (`plan_cem.py`), where the cost function is exactly
`W_CTE * mean(cte^2) + W_SMOOTH * mean(dsteer^2)`, scored on latents imagined
forward through the MDN-RNN and read out by the z->cte probe.

Result: **planning gave the best survival of any learned policy** (89.7 vs
69.3 steps) -- the centring incentive worked. The smoothness term is the part
that needs revisiting: the planner is the *jitteriest* policy measured
(20.90 reversals/100 against the expert's 9.87), so at `w_smooth = 0.05` it is
under-weighted, not over-weighted as the original swerving diagnosis implied.

### V.3.4 What P5 actually establishes

The pipeline is proven end to end: live frame -> VAE encode -> MDN-RNN state
-> policy or planner -> simulator, at ~15 planning steps/second. Every stage
runs, and the failure is measured rather than assumed.

**The bottleneck is the learned representation and dynamics, not the
controller.** Three policy classes spanning linear, nonlinear, and planning
all wall at 69-110 steps while the expert -- which reads the simulator's cte
directly and never touches the latent -- completes 9/9. The common factor is
the VAE latent and the MDN-RNN.

**NO TRANSFER CLAIM.** Everything here is simulated. None of it is evidence
about the physical car, and the capstone remains M4 offline training on the
car's own real logs.

## V.4 Open items

1. **The 69-110 step wall is undiagnosed.** Speed is ruled out; the leading
   remaining hypothesis is compounding latent error at a specific track
   feature. A cte-vs-step trace of a failing episode is the next cheap test.
2. `w_smooth` is under-weighted for the planner (V.3.3) -- untested at higher
   values.
3. The VAE's blindness to small salient objects (V.2) is unverified against
   DreamerV3's RSSM, and the M4 stop-sign showcase depends on the answer.
4. Appendix S's "generalises to unseen trajectories" is qualified by V.2.
5. **Nothing printed, nothing ordered** - unchanged since 2026-07-23. The
   encoder-motor decision and the ~1:20 track re-spec still block all physical
   progress. Software is now five SIM-POC tasks ahead of hardware.


---

# Appendix W - The wall diagnosed (perception goes OOD); both encoders erase small objects, so the M4 stop-sign showcase is threatened (2026-08-08, ~22:52 CDT)

**CADENCE NOTE:** hooks fired at prompts #54, #57, #60 and #63 before this
entry. Second consecutive multi-mark slip, both during long autonomous runs.
Recorded, not smoothed. The pattern is now clear enough to act on: cadence
fails specifically when a task chains many tool calls without a natural
reporting break.

**WHAT:** the two open items Appendix V.4 left as "undiagnosed" are now
measured and closed. New: `ml/trace_failure.py`, `ml/compare_encoders.py`,
plus checkpoint saving in `ml/run_dreamer_p4.py`. Artifacts in
`ml/runs/p5_trace/` and `ml/runs/encoder_cmp/`.

## W.1 The 69-110 step wall is PERCEPTION going out of distribution

Appendix V.3.2 ruled out corner speed but left the cause open, and "the latent
is the bottleneck" was a conclusion about three stages at once. `trace_failure.py`
separates them by logging, per step: the probe's read of lane position
(perception), the RNN's H-step-ahead prediction graded against what actually
happened (dynamics), and the true cte.

**Perception error is a function of POSITION, not of policy or elapsed time:**

| \|actual cte\| | perception err, MLP policy | perception err, PID expert |
|---|---|---|
| 0.0 - 0.3 | 0.202 | 0.198 |
| 0.3 - 0.6 | 0.267 | 0.315 |
| 0.6 - 1.0 | 0.307 | 0.447 |
| 1.0 - 1.5 | 0.625 | 0.665 |
| 1.5 + | **2.104** | **1.734** |

corr(|cte|, perception error) = **0.894** (MLP) and **0.852** (expert), n=263
and n=600. Two drivers with nothing in common -- one learned, one hand-tuned
PID -- trace the same curve. It is where the car IS, not what is steering it,
and not how long it has been running.

**Root cause, and it is in this project's own collector.**
`collect_sim_data.py` rejects any episode with `mean|cte| > MAX_MEAN_ABS_CTE
= 1.2`; the expert averaged 0.36. The corpus therefore contains essentially no
off-centre frames, so the VAE and the probe were never shown the states a
recovering policy must operate in. **The failure is unrecoverable by
construction:** drift past ~1.0 and the car can no longer see where it is, so
it cannot steer back. Every policy class fails identically because none of
them is the problem.

**This is a DATA problem, and it transfers to hardware.** M3/M4 on the real
car need deliberate off-centre recovery demonstrations, or the same wall
appears there. Note the irony worth keeping: the quality filter that keeps the
imitation corpus clean is exactly what deletes the recovery data. The fix is a
SEPARATE recovery set exempt from the filter, not a loosened threshold.

**Instrumentation caveat, stated because it affects one number.** The trace
adds an encode plus an H-step imagination per control step, slowing the loop
enough to degrade even the expert (its last-25% mean|cte| rose to 1.213 versus
0.367 in the uninstrumented eval). Within-run correlations are unaffected --
that is the whole finding -- but absolute survival from a traced run is not
comparable to `eval_in_sim.py`.

## W.2 Both encoders erase small objects. The M4 stop-sign plan is threatened.

Appendix V.2 flagged that the ConvVAE drops orange traffic cones, and asked
whether DreamerV3's RSSM (dyn_deter 512 plus a 32x32 discrete stochastic
state, against z=32 continuous) would keep them. `compare_encoders.py` answers
it on 32 held-out frames averaging 28 cone pixels each (0.69% of frame):

| model | cone err | bg err | ratio | cone px surviving |
|---|---|---|---|---|
| ConvVAE | 0.2200 | 0.0500 | 4.40x | **0 / 899** |
| DreamerV3 | 0.1982 | 0.0640 | 3.10x | **0 / 899** |

**Zero cone pixels survive in either reconstruction.** Road, lane lines and
tree line are all preserved; the cone is simply gone. A bigger, differently-
trained world model does not fix it.

**Consequence for the PRD.** The stop sign was chosen as the M4 world-model
showcase precisely because a memoryless BC policy provably cannot learn it
while a recurrent world model can (Appendix L). That reasoning is still sound
-- but it assumes the sign reaches the latent, and at 64x64 with a
reconstruction-dominated objective an object at <1% of frame does not.
Mitigations are OUTSIDE the choice of world model: higher input resolution, an
auxiliary detection/segmentation head, or a reward the object actually moves.

**Caveat, stated:** the DreamerV3 checkpoint saw 2,000 training steps against
the ConvVAE's 40 epochs, and its worse BACKGROUND error (0.0640 vs 0.0500) is
consistent with being undertrained. That weakens any claim about relative
quality -- but not the conclusion, because 0/899 is an absence, not a blur.

## W.3 A metric that graded its own answer wrong

Worth recording as a method failure, not just a result.

`compare_encoders.py` first reported only the RATIO of cone error to
background error, and printed an automated verdict: *"DreamerV3 preserves
cones BETTER (3.12x vs 4.38x). The M4 stop-sign showcase is not threatened."*

That verdict was **wrong**, and the rendered panel showed it wrong at a
glance: both rows have no cone at all. The ratio improved because DreamerV3's
BACKGROUND error is 28% worse, shrinking the denominator -- a model can score
a better ratio by getting worse everywhere else while erasing the object just
as completely. Absolute cone error differed by only 9%.

Fixed by adding a metric that cannot be gamed that way: re-run the same colour
detector on the RECONSTRUCTION and count surviving cone pixels. Survival now
gates the verdict; ratio only breaks ties among models that keep the object.

The general lesson, which belongs with the audit's "a gate that cannot fire is
not a gate": **a derived ratio can improve for the wrong reason. Prefer a
metric that asks directly whether the thing you care about is still there.**
The panel was rendered and LOOKED AT; that is what caught it.

## W.4 Method failures this session

1. **A cone detector that measured the road.** The first colour threshold
   (`R-G > 40`) fired on 62% of frames with mean masked colour [209,164,85] --
   tan dirt, not cone. It would have measured road fidelity and called it cone
   fidelity. Fixed by deriving the threshold from the actual R-G distribution
   (99.9th percentile 62, 99.99th 95, so `> 80` is the real tail) and then
   RENDERING frames beside their masks to confirm the mask lands on the cone
   and excludes the yellow centre line.
2. **A decoder rescaling bug that would have faked the headline.** Upstream
   DreamerV3 preprocesses images to [-0.5, 0.5] and its ConvDecoder ends with
   `mean += 0.5`, so undoing an offset looks correct. This fork preprocesses to
   [0, 1] (`models.py:182`), making that `+0.5` a bias init in the same space.
   Adding another 0.5 would have brightened every DreamerV3 reconstruction and
   manufactured a "DreamerV3 is worse" result out of a units error. Caught by
   reading the vendored source before running; a range assertion now guards it.
3. **`&` inside a `run_in_background` call.** The wrapper returned "exit 0"
   immediately while the real training died. Cost one silent ~20-minute
   no-op. Do not background a command that is already backgrounded.
4. **A module-name collision with the vendored library.** `import models`
   after adding `ml/vendor/` to sys.path returns THIS project's `ml/models.py`
   (already cached in sys.modules), surfacing as
   `module 'models' has no attribute 'WorldModel'`. Fixed by loading the
   vendored file by explicit path via importlib, registering it as `models` so
   the vendor's internal imports resolve, then restoring ours.

## W.5 Research brief: BLOCKED, not abandoned

`/research-brief` was started on "best AI method for this project's autonomy
stack". Stages 1-5 completed and the hypotheses were pre-registered BEFORE
collection (the anti-confirmation-bias gate):

- **H1** the binding constraint is DATA COVERAGE, not model class
- **H2** the binding constraint is the REPRESENTATION (reconstruction is the
  wrong objective)
- **H3** OFFLINE RL on the reward already in the corpus beats cloning
- **H4 (null)** classical CV + control is the right answer at this scale and
  the learned stack is portfolio decoration

Four parallel collection agents were dispatched, one per hypothesis, each
instructed to hunt its own falsifier. **All four terminated on an API session
limit** partway through collection, returning only mid-work notes rather than
findings. No brief was written and none of those fragments are recorded here
as evidence -- an agent's note that a source "is a direct hit" is not a
finding. Re-run collection after the limit resets.

**Relevant discovery made while answering a question, not by the agents:** the
corpus already carries a dense reward (mean 1.393, ~849 distinct values, range
0-1.9) that essentially measures how centred the car is -- the exact incentive
Evan proposed on 2026-08-07. It has been present in every episode since P2 and
is used by nothing except the DreamerV3 actor-critic, whose policy P4 trained
and discarded. That is directly relevant to H3.

**Also clarified for the record:** no component that has ever driven the car
uses reinforcement learning. V is unsupervised, M is supervised next-latent
prediction, C is behavioural cloning, the probe is supervised regression, and
CEM is planning against a hand-written cost with no learning from outcomes.
The single exception is P4's DreamerV3 run, which does train an actor-critic
on imagined rollouts (`dreamer.py:125`) -- genuine model-based RL -- but its
policy was never extracted or driven.

## W.6 Open items

1. **Research brief incomplete** (W.5). Blocked on API limits, not on anything
   technical.
2. **The M4 stop-sign showcase needs a decision** (W.2): raise input
   resolution, add an auxiliary detection head, or change the showcase. This
   is a PRD-level choice, not an implementation detail.
3. Untested: whether recovery data actually fixes the wall (W.1). It is the
   obvious next experiment and it is cheap in sim -- collect episodes started
   deliberately off-centre and re-train.
4. `w_smooth` still under-weighted for the CEM planner (Appendix V.3.3).
5. **Nothing printed, nothing ordered** - unchanged since 2026-07-23. The
   encoder-motor decision and the ~1:20 track re-spec remain the only things
   blocking physical progress.


---

# Appendix X - Recovery data fixes off-centre perception by 57% with a FROZEN encoder; the steering-smoothness knob works but does not fix the wall (2026-08-08, ~23:11 CDT)

**CADENCE NOTE:** hook fired at #66 before this entry. Third consecutive slip.

**WHAT:** two experiments, both prompted by Evan. (1) The recovery-data test
that Appendix W.6 listed as the obvious next experiment. (2) A steering-
smoothness sweep, after Evan observed the car overcompensating a second time.
New: `ml/collect_recovery.py`, `ml/exp_recovery.py`, `--extra-src` on
`ml/preprocess.py`. Artifacts in `ml/runs/exp_recovery/`.

## X.1 Recovery data: the cheap branch wins

W.1 diagnosed the wall as perception going out of distribution, because the
collector rejects `mean|cte| > 1.2` and the expert averaged 0.36, so no
off-centre frames exist. `collect_recovery.py` supplies them by DART-style
noise injection (Laskey et al.): drive the expert, inject a burst of steering
noise every 60 steps for 8 steps, then hand back control and let the PID drive
home. The frames in between are the missing states.

**DART was chosen over DAgger deliberately.** DAgger needs an expert to
relabel states the learner visits, which on a physical car means a human with
a controller riding along every run. Noise injection needs only the scripted
expert, so the identical procedure works on the real car — which is the point,
since this experiment exists to de-risk M3's data plan.

Collected: **18 episodes, 5,961 frames, mean|cte| 0.95** against the original
corpus's 0.36; ~6.7% of the augmented corpus. Two episodes were rejected for
never recovering (the loose 2.5 cap, deliberately NOT the 1.2 filter that
caused the problem).

**THE DECOMPOSITION, which is why the experiment was built this way.**
"Perception failed" is two claims with very different price tags:
(a) the LATENT does not contain off-centre lane position — expensive, needs a
VAE retrain or a new representation; (b) the READOUT was never trained to
decode it — cheap. `exp_recovery.py` separates them by training two probes
against the **same frozen ConvVAE** and evaluating on the same held-out
episodes drawn from both corpora.

| \|cte\| bucket | n | baseline probe | augmented probe | change |
|---|---|---|---|---|
| 0.0 - 0.3 | 11,546 | 0.057 | 0.069 | +21% |
| 0.3 - 0.6 | 5,906 | 0.071 | 0.085 | +20% |
| 0.6 - 1.0 | 1,474 | 0.131 | 0.128 | -3% |
| **1.0 - 1.5** | 478 | 0.268 | **0.159** | **-41%** |
| **1.5 +** | 825 | 0.591 | **0.214** | **-64%** |
| overall | 20,229 | 0.093 | 0.086 | -8% |

**Off-centre (|cte| >= 1.0): 0.429 -> 0.186, a 57% reduction, with the encoder
frozen.** Hypothesis (b) wins. The ConvVAE's latent carried off-centre lane
position all along; the probe had simply never been shown it.

**This corrects the emphasis of Appendix W.1.** W.1's diagnosis (coverage, not
controller) holds and is confirmed. But its framing invited the reading that
the *representation* was inadequate — and V/W together had been building a
case against the ConvVAE. That case is now weaker: the encoder was never the
problem for lane position. It remains true that the encoder erases small
OBJECTS (W.2, 0/899 cone pixels) — those are different failures and should not
be conflated.

**Tradeoff, stated:** the centred buckets got ~20% WORSE. The probe now spends
capacity across a wider range instead of overfitting a narrow one. Overall
error still improved, and the trade is obviously right — 0.012 worse where the
car was already fine, 0.38 better where it was dying — but it is a real cost
and a reason to keep an eye on centred-lane precision.

**NOT YET ESTABLISHED, and this matters:** this measures the PROBE, not the
car. It proves perception is cheaply fixable; it does not prove the car drives
further. A controller retrained on the augmented corpus and re-evaluated in
sim is the outstanding test, and no claim about the wall being beaten should
be made until it runs.

## X.2 Steering smoothness: the knob works, and it does not fix anything

Evan, 2026-08-08: "the car likes to overcompensate on turns and straights,
would it be advantageous to punish the bot for excessive steering angle?"

**He was right this time, and a previous entry argued the opposite for a
different policy.** Appendix V.3.2 measured the LINEAR BC controller and found
it does NOT oscillate (8.50 reversals/100 vs the expert's 9.84). But the CEM
planner does: **20.90, or 2.13x the expert.** Same symptom, different policy,
opposite diagnosis. V.3.3 had already flagged `w_smooth` as under-weighted and
left it as an open item; Evan spotted it before it was acted on.

**The correction to his framing is narrow but real: penalise the RATE of
steering change, not the ANGLE.** A corner needs a large *sustained* angle, so
an angle penalty causes understeer and running wide. On straights an angle
penalty is redundant anyway — the centring term already charges for any
steering that moves the car off-line. The cost function already had the rate
term; only its weight was wrong.

Sweep (1 seed, 2 episodes per setting, 600-step cap):

| `w_smooth` | rev/100 | mean\|cte\| | steps |
|---|---|---|---|
| 0.05 (as shipped) | 21.4 | **0.346** | 82 |
| 0.2 | 12.2 | 0.524 | 74 |
| 0.5 | **9.8** | 0.675 | 86 |
| 1.0 | 6.4 | 1.049 | 97 |
| *expert* | *9.84* | *0.367* | *600* |

**A PREDICTION WAS FALSIFIED, and the way it failed is the finding.** The
prediction (logged before running) was that jitter would fall monotonically
while survival peaked and then declined, because damping the planner also
damps the recovery corrections it needs. Jitter did fall monotonically, 3.3x.
**Survival did not decline — it is flat-to-noisy (74-97, overlapping).**
Smoothing the steering does not make the car drive meaningfully further, so
**the jitter was never what was killing it.** That independently corroborates
W.1: the wall is perception, not steering behaviour.

The real cost is lane-holding: mean|cte| triples, 0.346 -> 1.049. Note that at
`w_smooth = 0.05` the planner holds the lane BETTER than the expert (0.346 vs
0.367) — it is precise and jittery, and smoothing trades the precision away.

**Recommendation:** `w_smooth = 0.5` for expert-matched smoothness (9.8 vs
9.84) at roughly 2x lane error, but only if smoothness is wanted for its own
sake. It does not improve survival.

**UNDERPOWERED, and labelled as such.** One seed, two episodes per setting.
`testing.md` requires >=3 seeds for a comparative claim. The jitter and
lane-error trends are large and monotonic enough to trust directionally; the
survival column is NOT distinguishable at n=2 and no conclusion rests on it
beyond "no large effect".

## X.3 Open items

1. **The closed-loop test of X.1** — retrain the controller (and probe) on the
   augmented corpus, re-run `eval_in_sim.py`, 3 seeds. This is the experiment
   that decides whether recovery data beats the wall. Everything needed exists.
2. Research brief still BLOCKED on API session limits (Appendix W.5).
   Hypotheses remain pre-registered; collection has not been re-run.
3. M4 stop-sign showcase decision still open (W.2).
4. **Nothing printed, nothing ordered** — unchanged since 2026-07-23.


---

# Appendix Y - The stop-sign decision, and an AUC of 0.997 that meant nothing (2026-08-10, ~18:53 CDT)

**CADENCE NOTE:** hook fired at #69. Fourth consecutive slip; entry written
mid-work rather than after, so the experiments still running at the time of
writing are marked IN FLIGHT and their results belong to the next entry.

**WHAT:** Evan asked "what is the stop sign decision", then chose. Enacting
the choice turned up (a) a measurement that inverts how expensive the choice
is, (b) a hard new requirement on the physical track that falls out of that
measurement, and (c) a factual error in Appendix X. New:
`ml/probe_cone.py`, `ml/exp_aux_head.py`, `ml/build_expert_labels.py`,
`--proc` on `ml/train_controller.py`.

## Y.1 The decision (Evan, 2026-08-10 18:44 CDT)

W.2 left PRD 6(b) open with three options. Evan chose **auxiliary detection
head + an oversized (non-scale) printed sign** -- options 2 and 4 of the four
put to him. PRD 6(b) amended in place, the old DECISION NEEDED struck through
rather than deleted.

**Raising input resolution was rejected on an ARGUMENT, and the argument is
recorded because it is not a measurement.** Reconstruction loss is a MEAN over
pixels, so an object's share of the gradient is scale-invariant: 28/4096 at
64x64 is 112/16384 at 128x128, the same 0.68%. Higher resolution buys
detection RANGE -- a 2px distant sign becomes 8-12px and is at least
representable -- but it does not make the objective care. It also costs the
P3/P4 shared-tensor comparability and meets the batch-size wall measured in
P4. **This has not been tested and could be wrong**; it is reasoning from how
the loss is defined, not a result.

**The oversized sign attacks the quantity that actually governs the problem.**
Pixel SHARE decides whether the objective cares, and printing the sign larger
raises it for free. Deliberately off-scale -- a documented modelling choice,
not an oversight.

## Y.2 A probe scored AUC 0.997 and was blind. The ablation arm is the finding.

Before building the aux head, the cheap question: **does the frozen latent
already contain the object, and only the DECODER drop it?** Reconstruction
loss is a mean over pixels, so a 28-pixel object contributes ~0.7% of the
gradient -- the decoder has almost no reason to paint it even if `mu` encodes
it perfectly. Same latent-vs-readout split that paid off in X.1.

`ml/probe_cone.py`, frozen ConvVAE, cone labels from the W.2 colour detector:

| measurement | value |
|---|---|
| cone frames (>=12 px) | 3,687 / 91,678 (4.02%), mean 49 px |
| held-out AUC, cone present | **0.997** |
| shuffled-label control | 0.427 |

An AUC of 0.997 reads as a total success. **It is worth nothing, and the
experiment was built to find that out.**

Cones sit at FIXED track locations, and the latent demonstrably encodes track
position (cte probe R^2 0.957). So a probe can score near-perfectly by
learning "cones live near here" while being completely blind to cone pixels.
The ablation arm separates the two: paint the cone out, re-encode, re-score.

| | mean probe score |
|---|---|
| cone frames, as-is | 0.946 |
| **same frames, cone erased** (0 cone px left, verified) | **0.938** |
| true no-cone frames | 0.011 |

**Erasing the object moved the score by 1% of the pos/neg gap.** The probe was
reading position. The latent does not contain the cone.

**Consequence: the aux head is the EXPENSIVE branch, not the cheap one.** The
hoped-for result was X.1's -- signal already in `mu`, aux head only has to read
it, no VAE retrain. That is refuted. The aux loss has to reshape the ENCODER,
which means retraining the VAE.

**Method note.** W.3 recorded a metric that graded its own answer wrong and was
caught by rendering the frames. This time the check was designed in before the
run, and it fired. Without the ablation arm this entry would report "AUC 0.997,
the latent carries the object, the M4 mitigation is cheap" -- confident,
quantified, and wrong. **The shuffled-label control alone would NOT have caught
it** (it read 0.427, comfortably below the real 0.997); only the counterfactual
did. Worth keeping as a pattern: a control that varies the LABEL tests the
architecture, a control that varies the INPUT tests the claim.

Small honesty note: the shuffled control at 0.427 sits a few standard errors
BELOW chance rather than at it. A probe trained on destroyed labels learns an
arbitrary function of z, which can land either side of 0.5; it is not evidence
of leakage, which would show as AUC well above 0.5. Not investigated further.

## Y.3 NEW HARD REQUIREMENT: the sign must be relocatable. This is not a preference.

Y.2's confound is not confined to the probe. **On a fixed track, a sign at a
fixed place is perfectly predicted by "where am I".** Three consequences, all
following from the same fact:

1. A policy could pass the entire M4 showcase by stopping at a LOCATION while
   being blind to the sign. The demonstration would prove nothing.
2. An auxiliary head trained against a fixed-position sign can drive its loss
   to zero the same way, leaving the encoder blind while the metric goes green.
3. Any measurement taken on the sim's fixed cones is uninterpretable for the
   same reason -- which is why `exp_aux_head.py` uses a synthetic object at a
   uniformly random position instead.

**So the printed sign must be RELOCATABLE / REMOVABLE between runs.** Cost:
none -- it is a printed sign placed on a track. Recorded in PRD 6(b) as a hard
requirement rather than a nice-to-have, because the showcase is worthless
without it and that is a measured claim, not a stylistic one.

## Y.4 CORRECTION to Appendix X: the recovery corpus is 20 episodes, not 18

Appendix X.1 states "18 episodes, 5,961 frames". **That is wrong.** Ground
truth, from `ml/data/proc_aug/` and from X.1's own saved artifact:

| | Appendix X said | actual |
|---|---|---|
| recovery episodes | 18 | **20** |
| recovery frames | 5,961 | **6,552** |
| recovery mean\|cte\| | 0.95 | **0.971** |
| share of augmented corpus | ~6.7% | 6.67% (correct) |

`exp_recovery/exp_recovery.json` records `n_recovery_episodes: 20`, and
`train_episodes.npy` sums to 98,230 frames over 98 episodes (78 original +
20 recovery). The stale pair came from one `collect_recovery.py` run's stdout
summary ("saved 18 ... rejected 2") while the output directory already held 2
episodes from an earlier run; the experiment consumed all 20.

**The headline result is unaffected.** Off-centre probe error 0.42949 ->
0.18616 is -56.7%, matching the artifact exactly, and the ~6.7% corpus share
was computed from the arrays and was already right. Only the corpus
description was wrong. Per the append-only rule Appendix X is left as written
and stands corrected here.

Also corrected: X.1 compares recovery mean|cte| against "the original corpus's
0.36". 0.36 is the expert's mean PER-EPISODE value from the collection filter;
the frame-level mean over the original 91,678 frames is **0.322**. Both are
real numbers measuring different things, and X.1 compared across them without
saying so.

## Y.5 IN FLIGHT at time of writing (results belong to the next entry)

1. **`ml/exp_aux_head.py`** -- does an aux head make the encoder keep the
   object? Four arms (plain, aux weight 10/100/1000), 40 epochs each, on a
   POSITION-DECORRELATED synthetic object (~50% of frames, uniform position,
   real-cone frames dropped) precisely so Y.2's confound cannot recur. The
   un-injected frame is an exact counterfactual, so the ablation control is
   free. Weight is swept because at 10 the aux term is ~4% of total loss and a
   null result there could not distinguish a failed idea from a small knob.
2. **The closed-loop recovery test** (X.3 item 1) -- MLP controller, 3 seeds,
   trained on the original vs augmented corpus with V and M frozen, then
   `eval_in_sim.py`. Linear arm skipped: P5 established it is structurally
   wrong (probe R^2 0.27 linear vs 0.957 MLP).
   Required a real fix first: `build_expert_labels.py`. The corpus stores the
   action EXECUTED including injected noise (the data contract), so cloning it
   directly would teach the car to swerve -- exactly what
   `collect_recovery.py`'s docstring warned. 805 noise frames (0.82% of the
   corpus) are relabelled to `log_expert_steer`, with throttle recomputed by
   the collector's own rule. This is the DART target.
3. **Research brief** -- four collection agents dispatched, one per
   pre-registered hypothesis (W.5 H1-H4), each tasked to hunt its own
   falsifier. Previous attempt died on API limits and recorded nothing.

## Y.6 Open items

1. Whether the aux head is SUFFICIENT. If a z=32 bottleneck cannot retain a
   <1%-of-frame object under direct supervision, PRD 6(b) reopens and the
   escalation is a larger z or a detection path that bypasses the latent.
2. `docs/BOM.md` is modified in the working tree by an author other than this
   session (mtime 2026-08-08 23:05). It re-prices the Pi 5 4GB $70 -> $110 and
   puts the total at ~$222-225, **breaching the $200 ceiling**. Unstaged,
   uncommitted, unverified, and flagged to Evan rather than absorbed.
3. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.


---

# Appendix Z - The aux head works; the research brief kills H3; and the closed-loop metric was never reproducible (2026-08-10, ~19:24 CDT)

**WHAT:** the three things Evan asked for in one sitting — enact the stop-sign
decision (Y.1), run the research brief, run the closed-loop recovery test.
All three landed. The third one found a measurement problem that invalidates a
banked number.

## Z.1 The auxiliary head works, and the weight had to be 100x

Y.2 established the aux head is the EXPENSIVE branch: the frozen latent does
not contain the object, so the aux loss has to reshape the encoder.
`ml/exp_aux_head.py` retrains it and measures whether that works.

**The experiment could not be run on the sim's real cones**, because Y.2/Y.3
showed cone presence is predictable from track position, so an aux head could
satisfy its loss from position alone and the metric would go green on a blind
encoder. Instead a synthetic object is INJECTED — a 4-7px square in cone
colour, present in ~50% of frames at a uniformly random position, seeded from
the frame index. Presence and position are independent of the track by
construction, real-cone frames are dropped (10.1% of the corpus), and the
un-injected frame is an EXACT counterfactual, so the ablation control is free.

Four arms, identical seed/data/budget, 40 epochs each, ~69.7k fit frames:

| arm | val rec | object survival | pixel survival | probe AUC | ablation |
|---|---|---|---|---|---|
| plain | 60.88 | 0.0% | 0.0% | 0.673 | 97% |
| aux, weight 10 | 60.41 | **0.0%** | 0.0% | **0.985** | 100% |
| aux, weight 100 | 60.48 | 35.4% | 14.6% | **1.000** | 100% |
| aux, weight 1000 | 65.04 | **79.4%** | 34.6% | 1.000 | 100% |

**Headline: an auxiliary detection head puts the object in the latent, and at
weight 100 it is essentially free** (val rec 60.88 -> 60.48, a 0.7%
*improvement*, within noise). PRD 6(b)'s chosen mitigation is validated in sim.

**The `aux10` row is the most informative and was not predicted.** AUC 0.985
with **zero object survival**: the encoder learned the object while the decoder
still refuses to draw it. That is a clean dissociation of *in the latent* from
*in the reconstruction* — and it is the latent that M4 needs, since every
downstream stage consumes only `mu`. It also means **W.2's reconstruction-based
survival test systematically understates what an encoder knows.** W.2's
conclusion still stands for the plain ConvVAE (AUC 0.673 here, and the real-cone
probe collapsed under ablation in Y.2), but the METHOD needs the caveat.

**The weight sweep was load-bearing, and the pre-registered reason was right.**
At weight 10 the aux term is ~4% of total loss and buys no survival at all. A
single-weight experiment at 10 would have produced "the aux head does not work"
— confidently, and wrongly. Independent corroboration arrived the same day from
the research brief: HarmonyDream (ICML 2024) finds observation loss dominating
reward loss "at two orders of magnitude greater scale" and fixes it by raising
the coefficient from 1 to 100 — the same order as the jump from a dead arm to a
working one here.

**Cost, stated:** weight 1000 more than doubles object survival (35.4% ->
79.4%) but degrades reconstruction 60.48 -> 65.04 (+7.5%). Weight 100 is
selected as the cheapest arm that saturates AUC; the tie-break is now explicit
in code (`min` weight within 0.005 AUC of the best) rather than an accident of
`max()` argument order.

**Limits, stated plainly.** This is a SYNTHETIC object, not a stop sign: a
flat-colour square with a perfect colour detector for a label. It proves the
mechanism (an aux loss can force a <1%-of-frame object into a z=32 latent); it
does not prove a printed sign under real lighting will work. One seed. And the
z=32 capacity confound raised by the brief is untouched — this says an aux head
is SUFFICIENT at z=32, not that capacity was never a factor.

## Z.2 The closed-loop metric was never reproducible, and a banked number is wrong

Running the closed-loop test surfaced this before it produced a result.

**The identical MLP checkpoint, through the identical script, scored 69.3 steps
in the banked P5 run and 187.2 today — a 2.7x swing.** Ruled out, in order:
the checkpoints are byte-identical on val_mse (0.001754), epoch (30) and args;
`eval_in_sim.py` has one commit and was not modified between the runs; the
per-episode variance inside each run is tiny (+-1.2 and +-8.9), so neither run
is noisy.

**What differed is the control-loop rate: 13.2 Hz then, 16.7 Hz today.** The
PID expert, which does no neural forward pass, ran at the sim's own 18.87 Hz in
BOTH runs and returned 600/600 identically — perfectly reproducible. The rate
is flat across episodes within a run, so it is not a CUDA-warmup artifact
(checked explicitly; the first episode matches the last).

**The obvious mechanism is that gym_donkeycar advances in real time and
`observe()` blocks for the next frame, so a policy that cannot keep up drives
on a stale action.** `eval_in_sim.py` gained `--control-hz` to test that by
throttling the loop, and now always reports `control_hz` per episode and in the
summary.

**The throttle then falsified the tool it was built to be.** Sleeping out the
remainder of an iteration is NOT the same manipulation as "the same loop,
slower" — it breaks the lockstep between the control loop and frame
production, and the two clocks beat against each other. The PID expert,
throttled:

| throttle | steps | mean\|cte\| |
|---|---|---|
| none (18.87 Hz natural) | **600.0 (9/9)** | 0.361 |
| 18.5 Hz (a 2% reduction) | 196.5 +- 0.5 | 0.988 |
| 18.0 Hz | 136.0 +- 0.0 | 0.745 |
| 17.0 Hz | 133.0 +- 1.0 | 0.806 |
| 16.0 Hz | 124.9 +- 1.3 | 0.797 |

**A 2% throttle costs two thirds of the performance, and slowing four times
further barely matters.** That is a cliff, not a slope, and smooth control-rate
sensitivity does not behave that way. So `--control-hz` is demoted to a
DIAGNOSTIC that measures the artifact, explicitly documented as unusable for
equalising two arms of a comparison. **This was caught after the pinned A/B had
already been run** — the numbers exist in Z.3 and are reported, but they
describe the desynchronised regime.

**A second confound found while interpreting this, and it is a real bug for
the physical car.** `PIDDriver` is not dt-normalised: `integral += err` and
`derivative = err - prev_err` are per-CALL, not per-second. Changing the loop
rate therefore silently re-tunes the effective Ki and Kd. Harmless at a
constant rate, but **the expert's gains are tied to the rate they were tuned
at**, and the Pi 5 will not run at the sim's 18.87 Hz. It also means every
throttled-expert row above confounds rate with silent gain change.

**What survives, and it is the operationally important part:**
1. **The banked P5 headline of 69.3 steps understates that controller by
   2.7x.** Appendix V's P5 numbers were measured at whatever rate the machine
   ran that day. The QUALITATIVE conclusion is untouched — 0/9 survived at
   both rates and the expert finishes 9/9 — but the step count is not a stable
   quantity and must not be cited as one.
2. **Comparisons require matched achieved `control_hz`**, obtained by running
   both arms back-to-back unthrottled on an idle machine and checking the
   reported rate agrees — not by throttling.
3. **Inference latency is a first-class design constraint for M3/M4**, both
   because loop rate demonstrably moves the result and because the PID's gains
   are silently rate-coupled.

## Z.3 The closed-loop recovery test: NO CLEAR IMPROVEMENT

X.3 item 1, the experiment that was supposed to decide whether recovery data
beats the wall. **It does not, on this evidence.**

Setup: MLP controller (P5 established the linear one is structurally wrong),
3 seeds, V and M FROZEN on the original corpus, trained on `ml/data/proc`
vs `ml/data/proc_aug`, code-identical. Run at two operating points because of
Z.2.

| arm | steps | mean\|cte\| | ctrl Hz | survived |
|---|---|---|---|---|
| expert (reference) | 600.0 +- 0.0 | 0.361 | 18.87 | **9/9** |
| baseline, unpinned | 187.2 +- 8.9 | 0.528 | 16.73 | 0/9 |
| augmented, unpinned | 199.9 +- 24.6 | 0.774 | 16.88 | 0/9 |
| baseline, throttled 16 Hz † | 81.2 +- 18.0 | 0.679 | 15.93 | 0/9 |
| augmented, throttled 16 Hz † | 95.1 +- 9.0 | 0.626 | 15.90 | 0/9 |

† **The throttled rows are in the desynchronised regime described in Z.2 and
should not be read as a second operating point.** They were run before the
throttle was understood, and are kept because both arms sat in the same broken
regime, so the comparison between them is still internally matched — but the
absolute numbers describe the artifact. **The unpinned pair is the real
comparison**, and it is valid precisely because both arms happened to achieve
almost identical rates (16.73 vs 16.88 Hz, 0.9% apart).

Augmented is ahead at both operating points (+6.8% unpinned, +17.1%
throttled) and the SIGN is consistent, which is weak positive evidence. **But
no claim of improvement is made, for three reasons:**

1. **0/9 survived in every single arm.** Nothing finishes. Whatever the effect
   is, it is not the difference between failing and driving.
2. **The error bars overlap** at both operating points.
3. **The control arm moved.** The PID expert is IDENTICAL between the two
   pinned runs — same code, same gains, no learned component — yet scored
   124.9 +- 1.3 in one and 132.9 +- 19.6 in the other, a 6.4% swing with
   wildly different variance. That is the between-run noise floor of this
   harness, measured on a fixed reference, and it is the same order as the
   effect being claimed. **Including the expert in every run is what made this
   visible; a base-vs-aug comparison alone would have reported a 17% win.**

**Why it probably did not work, and this is testable.** The augmented
controller's held-out MSE is essentially unchanged: **0.001754 -> 0.001788**
(slightly worse). Recovery frames are 6.67% of the corpus and the BC objective
is a mean squared error dominated by the 93% of centred frames, so the policy
that minimises it is nearly the same policy. The probe in X.1 improved 57%
because it was trained with cross-track error as its TARGET; the controller's
target is the action, and the recovery frames are drowned out.

**That is the same failure mode Z.1 just measured in the aux head**, where
weight 10 (~4% of loss) bought nothing and weight 100 saturated. **The obvious
next experiment is a sample-weight sweep on the recovery frames in the
controller loss** — and it is cheap, since controller training takes ~1 minute.
Noted as the top open item rather than run tonight.

**A second confound that the frozen design cannot rule out.** V and M were
frozen deliberately, to test X.1's claim that the encoder needs no retraining.
But the controller consumes `h` from an MDN-RNN trained ONLY on centred data,
so on exactly the off-centre frames that matter, the hidden state is itself out
of distribution. The test isolates the CONTROLLER's exposure to recovery data
and leaves the dynamics model unexposed. Retraining M on the augmented corpus
is the fuller version.

**What this does NOT overturn.** X.1's measurement stands — recovery data
really does cut off-centre probe error 57% with a frozen encoder. What fails is
the inference from that to driving. **Appendix X.1 explicitly refused to make
that inference** ("this measures the PROBE, not the car... no claim about the
wall being beaten should be made until it runs"), and the research brief
supplies the citation for why that refusal was right: offline prediction error
is not necessarily correlated with driving quality, and two models with
identical prediction error can differ dramatically in closed-loop performance
(Codevilla et al., ECCV 2018).

## Z.4 Research brief: H3 dies, nothing else wins outright

`docs/research/2026-08-10_ai-methods-for-the-autonomy-stack.md`. Four
collection agents, one per hypothesis pre-registered in W.5, each instructed to
hunt its OWN falsifier. The W.5 attempt died on API limits and recorded
nothing; this is the completed re-run against the identical hypotheses.

- **H3 (offline RL beats cloning) DIES.** Every published win condition for
  offline RL — sparse reward, noisy data, diverse coverage — is absent here.
  V-D4RL benchmarks the same cell of the design space (pixels, 100k
  transitions, continuous control, narrow expert data) and reports BC 91.5 vs
  **offline DreamerV2 4.8** on walker-walk expert. The dense centredness reward
  being free and unused is not evidence it is useful. **Do not build offline RL
  on this corpus.**
- **H1 (coverage) MIXED** — right now, wrong soon. CIL 2018 is the closest
  analogue: 10% noise-injected data took success 56% -> 88% (and 22% -> 64% on
  an unseen town). This corpus is at 6.67%, the same order. But Jaeger's
  controlled CARLA ablation bought +17 DS from an architecture change and +2 DS
  from tripling the data, so "coverage, not model class" is not defensible as a
  general claim.
- **H2 (representation) MIXED** — the mechanism is real and cited in primary
  sources, including DreamerV2's own paper: the reconstruction loss fails
  "because the most important object in the game, the ball, occupies only a
  single pixel." **That is W.2's 0-of-899-pixels result, named by the authors
  of one of the two encoders measured.** But the strong form dies: the best
  published fixes KEEP reconstruction and re-aim it (Masked World Models,
  Segmentation Dreamer, SEM2, MILE), and deleting it measurably hurts.
- **H4 (classical is the answer) MIXED** — survives narrowly; "learned =
  decoration" dies. Classical dominates F1TENTH, but that is LiDAR with a prior
  map. In this project's actual regime — camera-only, printed markings, 1/10
  scale — the AI Driving Olympics lane-following winner flipped from classical
  (2018) to imitation learning (2019/20) to PPO (2021).

**The convergent answer no single hypothesis proposed: hybrid.** Every recent
result beating the classical state of the art at this scale is a learned
component ON a classical one — residual RL on a classical controller (+11.5%
lap time, 20 min on-car training), learned tuning of pure pursuit, learned
perception feeding a classical Stanley controller. That reframes the PID as the
thing to build on, not the thing to beat.

**Two things this project appears to have measured that the literature has
not**, both flagged so they are never cited as borrowed: (a) the
scale-invariance argument against raising resolution is **Evan's own
derivation** — no source states it, and no published experiment tests whether
resolution alone restores small objects; (b) no cone- or sign-scale
object-retention measurement for a ConvVAE latent on a 1/10-1/14 car was found,
and no driving paper isolates sign retention with a causal paint-out test of
the kind in Y.2.

**One agent claim was checked and found FALSE.** The H1 arm named target-point
conditioning as its most actionable recommendation, on the basis that
"gym_donkeycar exposes track waypoints." It does not — verified directly
against `donkey_sim.py`: the info dict is `pos, cte, speed, forward_vel, hit,
gyro, accel, vel, lidar, car, last_lap_time, lap_count`, and there is no
waypoint message type. A target point could be constructed from logged expert
`pos`, but that needs localization at inference the physical car will not have,
so it is a sim-only shortcut that does not transfer. Recorded because the
underlying mechanism is real and the proposed action is not available.

**A finding the brief was not looking for, and it is a live risk in this
stack.** Copycat agents (NeurIPS 2020): a BC policy given observation HISTORIES
learns to predict the *previous* expert action, with held-out likelihood
improving while closed-loop reward decreases — explicitly not overfitting. This
controller consumes the MDN-RNN hidden state, and the observed signature
matches exactly: val MSE ~0.0018, closed-loop failure. **It is a rival
explanation for the P5 wall, independent of perception, and it has never been
tested.** The test is one training run: controller on `z` alone with `h` zeroed.

## Z.5 Open items

1. **The copycat test** (Z.4) — one training run, could partially rewrite the
   P5 narrative. Highest value-per-cost item on the board.
2. **A resolution ablation.** Nobody has published one, and PRD 6(b) currently
   rejects resolution on an argument alone.
3. The aux head on a REAL sign under real lighting, not a synthetic square.
4. **`docs/BOM.md` still modified by another session** (mtime 2026-08-08
   23:05), unstaged and unverified, claiming the $200 ceiling is breached.
   Flagged to Evan, not absorbed.
5. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.


---

# Appendix AA - Recovery data is not the fix, and the loss weight is not either: the wall is upstream (2026-08-10, ~20:07 CDT)

**WHAT:** Z.3's negative result had one obvious escape hatch — recovery frames
are 6.67% of a mean-squared objective, so maybe they were simply drowned out.
`--recovery-weight` on `ml/train_controller.py` tests it by upweighting them.
**The escape hatch is closed.**

## AA.1 A 12x change in the objective moves survival not at all

MLP controller, 3 seeds per arm, V and M frozen, all five arms evaluated
**back-to-back on an idle machine** so the Z.2 rate confound cannot apply —
achieved `control_hz` was 19.96-20.00 across every arm, and the PID expert
returned 600/600 (9/9) in all five with mean|cte| 0.328-0.364.

| arm | recovery share of objective | val MSE (unweighted) | steps, per-seed mean | mean\|cte\| |
|---|---|---|---|---|
| cl_base (original corpus) | 0% | 0.00177 | 189.7 +- 32.1 | 0.757 |
| cl_aug (weight 1) | 6.6% | 0.00181 | **221.0 +- 27.2** | 0.977 |
| rw5 | 27.3% | 0.00207 | 209.9 +- 32.7 | 0.640 |
| rw15 | 52.9% | 0.00245 | **172.6 +- 80.7** | 0.907 |
| rw50 | 78.9% | 0.00331 | 190.2 +- 37.6 | 1.029 |

**0/9 survived in every arm.** Means span 172.6 to 221.0 with per-seed standard
deviations of 27-81, so every arm's spread covers every other arm's mean.
Nothing here is significant and nothing is monotonic.

**The unit of analysis is the SEED, not the episode.** Three episodes share one
controller, so they are not independent; quoting the 9-episode sd (as low as
+-22) would overstate precision roughly 1.7x. n=3 per arm.

**The weighting was NOT a no-op — that is what makes this decisive.** Unweighted
val MSE degrades monotonically 0.00177 -> 0.00331 as recovery frames take over
the objective, and lane error drifts up across the swept arms (0.640 -> 0.907
-> 1.029). The optimiser genuinely learned a different policy. **It just did not
learn a better-driving one.** So "the recovery frames were drowned out by the
93% centred majority" is refuted: at weight 50 they dominate 78.9% of the
gradient and the car still dies at ~190 steps.

**A prediction was logged before the run and half of it held.** Predicted:
(a) weight 50 would HURT via worse lane-holding rather than fewer steps —
**held**, mean|cte| rises across the sweep to 1.029, the worst of any arm;
(b) survival flat all the way to weight 50 would mean the problem is upstream
of the loss weighting — **that is what happened.**

## AA.2 What this closes, and what it leaves

**Closed:** recovery data does not beat the P5 wall, at any loss weight. X.1's
57% off-centre PROBE improvement was real and remains real; it simply does not
transfer to driving, and three separate attempts to make it transfer (add the
data, relabel with DART expert actions, upweight the frames to 79% of the
objective) all failed. Codevilla et al. (ECCV 2018) is the citation for why
that is a known trap: offline prediction error is not correlated with driving
quality.

**Still standing, untested, and now the leading hypothesis: COPYCAT.** The
research brief (Z.4) surfaced that a BC policy given observation HISTORIES
learns to predict the PREVIOUS expert action, with held-out likelihood
improving while closed-loop reward falls — explicitly not overfitting
(arXiv:2010.14876, NeurIPS 2020). This controller consumes the MDN-RNN hidden
state `h`, and every arm above shows the signature: excellent and steadily
*improving* held-out MSE alongside flat, terrible driving. **Nothing in AA.1
touches the `h` input, which is the one thing common to every failed arm.**
The test is one training run with `h` zeroed.

**Second candidate, also untouched:** M was frozen on centred data throughout,
so on off-centre frames the hidden state itself is out of distribution.
Retraining M on the augmented corpus separates that from copycat.

## AA.3 Method note: the control arm earned its keep again

The expert was run inside every one of the five eval batches rather than once.
That is what makes "all arms at 19.96-20.00 Hz, expert 9/9 at cte 0.328-0.364"
a checkable statement instead of an assumption — and after Z.2, an eval batch
without its own control arm is not worth running. Note also that the sim ran at
**20.00 Hz this session against 18.87 Hz earlier the same evening**, which is
further evidence that only within-batch comparisons mean anything here.


---

# Appendix AB - FIRST COMPLETED EPISODES: the controller was ignoring z, and recovery data only pays once the crutch is removed (2026-08-11, ~00:21 CDT)

**WHAT:** the copycat test from AA.2. Copycat is refuted, but the ablation
built to test it found the actual failure, and fixing it produced **the first
learned policy in this project to finish an episode.** New:
`ml/diag_copycat.py`, `--no-history` on `train_controller.py` (honoured at
serve time by `eval_in_sim.py`), and a batch-validity gate.

## AB.1 Copycat: refuted, cheaply, without retraining

Expert steering is temporally smooth, so "repeat the previous action" is a
strong predictor for free. If the controller cannot beat it, its held-out MSE
is autocorrelation rather than perception. Held-out, 14,400 frames, skill =
1 - MSE/var:

| comparison | MSE | skill |
|---|---|---|
| controller -> a[t] (the reported val MSE) | 0.001755 | 0.993 |
| a[t-1] -> a[t] (trivial copy baseline) | 0.031997 | 0.873 |
| controller -> a[t-1] | 0.030699 | 0.878 |
| **controller with h=0 -> a[t]** | **0.282040** | **-0.120** |

The controller beats repeat-last-action by **18.2x** and predicts a[t] far
better than a[t-1]. **Wen et al.'s copycat mechanism does not apply here** —
recorded as a refuted hypothesis, not quietly dropped.

**The fourth row is the finding.** Zero the MDN-RNN hidden state at serve time
and the controller is *worse than predicting the mean* (skill -0.120). It is
riding almost entirely on `h` and barely reading `z`.

**Why that is fatal, and it is a train/serve asymmetry:** during training `h`
is teacher-forced on the **logged expert actions**; in closed loop it is built
from the **policy's own actions**, fed back step by step. The single input the
controller depends on is the one that drifts the moment the policy deviates.
That is compounding error through the RECURRENT STATE, a different failure from
the perception-OOD story in W.1.

## AB.2 The 2x2, and the interaction that neither change produces alone

MLP controller, 3 seeds, V and M frozen, all four arms in one back-to-back
batch. `--no-history` zeroes `h` at training AND serve (read back out of the
checkpoint, so the two can never disagree).

| | with `h` | `z` only |
|---|---|---|
| original corpus | 185.6 +- 15.4 (0/9) | 109.3 +- 27.8 (0/9) |
| **+ recovery data** | 196.6 +- 7.0 (0/9) | **342.4 +- 230.6 (3/9)** |

**Three of nine episodes completed the full 600 steps. No learned policy in
this project had ever finished one.** Per-seed means [426, 506, 96].

**Neither intervention works alone, and that is the point.** Removing `h` by
itself makes things WORSE (185.6 -> 109.3): the controller is forced onto `z`,
whose off-centre readout is poor. Recovery data by itself does almost nothing
(185.6 -> 196.6), reproducing Z.3/AA. Together: 1.85x the baseline and the
first completions. **A one-variable-at-a-time search would have rejected both.**

**This retroactively vindicates X.1 and explains AA.** The 57% off-centre probe
improvement was real AND necessary — it just could not express itself while the
controller was routing around `z` entirely. It also means **AA's null had a
cause I got wrong**: I attributed it to recovery frames being drowned out at
6.67% of the objective, and the `--recovery-weight` sweep to 78.9% duly
disproved that. The real reason is that no loss weighting helps when the model
ignores the input the data improves. Upweighting merely fit those frames'
actions better *through `h`*.

**The open-loop metric is actively misleading, which is the transferable
lesson.** Held-out MSE ranks these arms in almost exactly the wrong order:

| arm | val MSE (unweighted) | steps |
|---|---|---|
| cl_base | **0.00177** (best) | 185.6 |
| cl_aug | 0.00181 | 196.6 |
| nh_base | 0.02614 | 109.3 |
| **nh_aug** | **0.02846** (worst, 16x) | **342.4 (3/9)** |

**The best-driving policy has the worst held-out loss by a factor of 16.** This
was pre-registered as the signature to look for before the run, and it is
exactly Codevilla et al. (ECCV 2018) — "two models with identical prediction
error can differ dramatically in their driving performance" — arriving as a
measurement on this project's own stack rather than as a citation.

## AB.3 Honest limits

- **High variance: per-seed [426, 506, 96].** One seed in three collapses.
  `nh_aug`'s +-230.6 is by far the widest of any arm. This is a promising
  configuration, **not a solved task**, and 3/9 is not "it drives".
- **The expert still wins outright**: 600/600, 9/9, mean|cte| 0.32-0.37 in
  every arm. The learned policy has not caught the scripted one.
- **Jitter roughly doubles without `h`** (rev/100 13.2 vs 6.6). Appendix X
  measured that jitter does not drive survival, so nothing here rests on it,
  but it is a real behavioural change and the z-only car visibly saws.
- Sim only. Nothing has touched hardware.

## AB.4 A batch was thrown away, and the control arm is why

The first run of this 2x2 was **discarded**: the PID expert — fixed code, no
learned component, 9/9 all evening — fell to 4/9 and then 0/9 across four
consecutive arms at a normal ~20 Hz. The simulator itself had degraded, so
every controller number in that batch was untrustworthy.

**The order was then reversed** to rule out an ordering artifact, since
`nh_aug` had run last. It won from first position too (342.4/3-of-9 valid,
362.0/1-of-9 degraded), and the two batches agree on the ordering while
disagreeing on the absolute numbers — which is the expected signature of a
degraded run.

`eval_in_sim.py` now **gates on this automatically**: expert survival below
9/9 prints a BATCH INVALID banner, records `batch_valid: false` in the
artifact, and exits 2. Verified by replaying it against the artifacts already
on disk — it passes the healthy batches and fails the degraded one. Combined
with Z.2's rate warning, an eval result in this project now has to declare both
the rate it ran at and whether its own control arm held.

## AB.5 Open items

1. **More seeds on `nh_aug`.** One-in-three collapse needs explaining before
   this is called a result; n=3 cannot distinguish a bad seed from a bimodal
   policy.
2. **Retrain M on the augmented corpus.** `h` was never useless in principle —
   it was trained only on centred data. A dynamics model that has seen
   off-centre states might beat z-only rather than lose to it.
3. **Revisit the `--recovery-weight` sweep with `h` zeroed.** AA swept it with
   the crutch in place, where it could not have worked.
4. Aux head on a real sign, not a synthetic square (Z.1).
5. **`docs/BOM.md` still modified by another session**, unverified, claiming
   the $200 ceiling is breached. Deliberately excluded from commit 2cbb84e.
6. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.


---

# Appendix AC - RETRACTION of AB: the "first completed episodes" result did not replicate, and the closed-loop harness is not trustworthy (2026-08-11, ~18:21 CDT)

**Appendix AB's headline is withdrawn.** It claimed 342.4 steps and 3/9
completed episodes for the z-only + recovery-data controller, called it the
first learned policy in this project to finish an episode, and built a 2x2
interaction story on it. **None of that survives replication.** AB is left as
written per the append-only rule and stands corrected here.

## AC.1 What replication actually shows

Same checkpoints, independent gate-valid batches:

| seed | AB's batch (expert 9/9) | re-run (expert 10/10) |
|---|---|---|
| 0 | 78, **600**, **600** | 100, 113 |
| 1 | **600**, 469, 448 | 108, 108 |
| 2 | 96, 96, 95 | 107, 107 |

Extended to **10 seeds over two independent valid batches: 107.2 +- 16.0,
0 of 20 completions**, every seed between 85 and 147. **No learned policy in
this project has ever completed an episode.**

Every arm re-run in the short-batch regime, all gate-valid:

| arm | valid batches | mean | sd | range |
|---|---|---|---|---|
| cl_base (h, original) | 4 | **189.4** | **4.1** | 185.6-195.0 |
| cl_aug (h, +recovery) | 4 | 189.1 | 35.1 | 139.0-221.0 |
| nh_base (z-only, original) | 2 | 109.2 | 0.1 | 109.2-109.3 |
| nh_aug (z-only, +recovery) | 4 | 170.0 | 115.4 | 98.3-342.4 |

**The 2x2 does not merely weaken — it reverses.** The plain baseline is the
best and by far the most stable arm (189.4 +- 4.1 across four batches).
Recovery data does nothing (189.4 -> 189.1, means indistinguishable). Removing
`h` is actively harmful (189.4 -> 109.2, and that one is rock-stable across
batches). `nh_aug`'s apparent advantage rests entirely on the single anomalous
batch; drop it and the arm sits at ~110-123.

**Honest conclusion: no intervention attempted on 2026-08-10/11 improves
closed-loop driving.** Recovery data, DART expert relabelling, recovery loss
weighting, and removing the history input have all now failed.

## AC.2 How the error was made, because that is the reusable part

The gate added hours earlier (expert survival 9/9) fired correctly on genuinely
degraded batches and gave false confidence on this one. **AB's batch passes
every check that existed**: expert 600/600 at 20.00 Hz, healthy mean|cte| 0.369,
reproduced in a second batch with the arm order reversed.

**The tell was present and I read it backwards.** AB's winning arm had
sd 230.6 while every other arm in the same batch had sd 7-45. I recorded that
as "high variance, not a solved task" and reported the mean as a result
anyway. **A 20x variance blow-up confined to the arm that wins is evidence the
measurement broke, not evidence of a promising policy.** The re-runs make this
unmistakable: the stable arms (cl_base sd 4.1, nh_base sd 0.1) reproduce to the
step, and only the arms with large sd move between batches.

**Second error: I treated agreement on ORDERING between two batches as
replication.** Both batches that ranked `nh_aug` first (ev2, ev3) were the
high-variance ones; ev2 was already known degraded. Two correlated
observations are not two independent ones.

## AC.3 The harness problem, which now outranks every ML question

**Two batches that both pass every available check disagree by 3x.** Until that
is understood, no closed-loop number from this project is trustworthy —
including those in Appendices Z and AA, which used the same harness. Those
were comparative and mostly null, so their conclusions are less exposed, but
they are not certified either.

**Leading hypothesis, not yet tested: the episode start state is
uncontrolled.** `DonkeyEnv.reset()` is sleep-synchronised, not
state-synchronised — `send_control(handbrake)`, `sleep(0.1)`, `viewer.reset()`,
`sleep(0.1)`, `observe()` — with nothing waiting for the simulator to confirm
the reset landed. Under different machine load the car's pose and speed at the
first control step will differ. The `seed=` parameter is a red herring: it sets
only `self.np_random`, which the Unity process never reads.

This fits the signature. A PID absorbs a varied start (600/600 regardless);
a marginal learned policy does not — which is exactly why the expert gate
passes while controller numbers swing 3x. It also explains the within-batch
pattern: consistent resets give near-identical episodes (107/107, 108/108),
inconsistent ones give 78 vs 600 within one controller.

**Test:** log cte, speed and pose at the first control step of every episode
and compare across batches. Cheap, and it either confirms the mechanism or
eliminates it.

**What is NOT affected**, because it never touched the simulator:
- The `h`-dependence measurement (AB.1). Open-loop, deterministic: zeroing the
  hidden state still gives skill -0.120, and copycat is still refuted at 18.2x
  over repeat-last-action.
- The aux-head sweep (Z.1) and the cone probe (Y.2). Open-loop, four arms,
  tight numbers.
- The research brief (Z.4).

**What IS affected:** every survival/step number in Z.3, AA.1, AB.2 and this
entry. The comparative nulls are probably safe — a harness this noisy makes
false NEGATIVES likely and false positives like AB's the real hazard — but
"probably safe" is not certified.

## AC.4 Rules adopted

1. **A closed-loop claim requires replication in an INDEPENDENT batch**, not a
   second arm within the same run. Ordering agreement is not replication.
2. **Variance is a validity signal, not just an error bar.** An arm whose sd is
   an order of magnitude above its neighbours in the same batch is suspect
   regardless of its mean.
3. The expert-survival gate stays, but is documented as **necessary and not
   sufficient**.
4. Prefer short batches. Every degraded batch tonight was a long one; every
   tight batch was short. Correlational, cause unknown.

## AC.5 Open items

1. **Fix or characterise the reset.** Highest priority in the project; every
   driving number depends on it.
2. Re-certify Z.3 and AA.1 once the harness is trustworthy.
3. Retrain M on the augmented corpus (AB.5) — still untested, and now the
   only live ML hypothesis for the wall.
4. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.
5. `docs/BOM.md` still modified by another session and unverified.


---

# Appendix AD - The harness noise floor MEASURED: CV 55%, and every comparison this session was underpowered (2026-08-11, ~23:29 CDT)

**WHAT:** AC named "fix or characterise the reset" the project's top priority
and the reset as the leading suspect. The reset is **exonerated**. The real
answer is worse and more useful: the harness has a measured 55% coefficient of
variation at the LAUNCH level, which means **no comparison run this session
had the statistical power to detect the effects it claimed.** New:
`ml/diag_reset.py`. Also folds in three errors caught by `/landing-check` on
commit 0bf4264.

## AD.1 The reset is not the cause (AC.3's hypothesis, refuted)

`ml/diag_reset.py` replicates `eval_in_sim.run_episode`'s reset + warmup
exactly and records the car's state at the moment the policy inherits it.

| | post-warmup cte | speed | pos x | pos z |
|---|---|---|---|---|
| launch 1, 8 episodes | mean 0.0066, range 0.0055 | sd 0.0031 | sd 0.0002 | sd 0.0018 |
| launch 2, 8 episodes | mean 0.0069, range 0.0046 | sd 0.0047 | sd 0.0002 | sd 0.0028 |

Post-reset position is identical to four decimals in all 16 episodes across
both launches (x 6.2116, z 5.9797), speed exactly 0.000, and `reset_seconds`
1.201-1.202 throughout. **The start state is deterministic within AND across
launches.** AC.3's leading hypothesis is dead. Recorded as a refuted
hypothesis, not quietly dropped.

## AD.2 The launch is the unit of variation, and the spread is 4.4x

Same checkpoint (`nh_aug` seed 0), same seed, seven independent **gate-valid**
sim launches (expert 600/600 in every one):

| launch | episodes | mean | completions |
|---|---|---|---|
| sd_01234 | 100, 113 | 106.5 | 0/2 |
| lc_3 | 115, 122 | 118.5 | 0/2 |
| lc_5 | 175, 184 | 179.5 | 0/2 |
| lc_1 | 200, 211 | 205.5 | 0/2 |
| lc_2 | 197, 267 | 232.0 | 0/2 |
| lc_6 | 183, 524 | 353.5 | 0/2 |
| lc_4 | **600**, 343 | 471.5 | **1/2** |

**mean 238.1, sd 131.6, min 106.5, max 471.5 — a 4.4x spread on one
unchanged policy.** Episodes *within* a launch frequently agree to a few steps
(100/113, 115/122, 175/184, 200/211); launches disagree enormously. The
variance lives between launches, not between episodes.

**Eliminated as causes, each by measurement:** control rate (matched
19.5-20.0 Hz in all seven), track identity (expert mean|cte| 0.323-0.381 over
12 launches — a regenerated track could not produce a +-5% band from a fixed
PID), and episode start state (AD.1). **The cause remains unknown.**

## AD.3 The number that matters: CV 55%, and what it costs

Coefficient of variation **131.6 / 238.1 = 0.553**.

Launches per ARM needed to detect a relative difference at 80% power,
alpha 0.05 (`n = 2(1.96+0.84)^2 CV^2 / d^2`):

| effect size | launches needed per arm |
|---|---|
| 10% | ~479 |
| 20% | ~120 |
| 30% | ~53 |
| 50% | ~19 |
| 100% (2x) | ~5 |
| 200% (3x) | ~1.2 |

**Every arm comparison in Appendices Z, AA, AB and AC used n = 1 launch per
arm.** At n=1 this harness can only resolve differences around 3x. Therefore:

- **Z.3** (recovery data, 187.2 vs 199.9, a 7% difference) — **uninterpretable.**
  Correctly reported as null, but for the wrong reason: it was not a
  measurement of "no effect", it was no measurement at all.
- **AA.1** (recovery-weight sweep, 172.6-221.0 across arms, ~28% spread) —
  **uninterpretable.** The conclusion "a 12x change in the objective moves
  survival not at all" is not supported; the instrument could not have seen a
  move smaller than 3x.
- **AB.2** (the 2x2, nh_aug 342.4 vs cl_base 185.6, 1.85x) — **below
  resolution at n=1.** The retraction in AC was right, but AC's own
  replacement table has exactly the same defect.
- **AC.1** (the reversed 2x2, cl_base 189.4 vs cl_aug 189.1) — **also
  uninterpretable at n=1 per batch.**
- **The one comparison that may survive**: `nh_base` 109.2 vs `cl_base` 189.4,
  a 1.7x difference, and `nh_base` is the most stable arm measured
  (109.33 / 109.17 across two launches). Still under the ~2x resolution bar,
  so **suggestive, not established.**

**This supersedes the framing of both AB and AC.** AB claimed a result the
instrument could not support; AC retracted it and asserted a replacement the
instrument could not support either. The correct statement is that **the
project does not currently possess a closed-loop measurement capable of
ranking these policies.**

## AD.4 Three errors caught by /landing-check on commit 0bf4264

Run by a fresh agent against artifacts only. All arithmetic in AC re-derived
exactly from the JSON; three substantive findings:

1. **A FALSE UNIVERSAL was committed.** AC, the commit message and
   `ml-training.md` all state "no learned policy has completed an episode" —
   contradicted by artifacts *in the same commit*: `ev3_nh_aug` has
   `survived: 3`, `ev2_nh_aug` has `survived: 1`. This was an overcorrection
   after the retraction. **True statement: no learned policy completes
   RELIABLY.** Pooled over 35 gate-valid `nh_aug` episodes the distribution is
   bimodal — 28 under 150 steps, 4 at 450-601 — with completions clustering by
   launch. Corrected in HANDOFF and the bin.
2. **AC's 2x2 table was not a matched comparison.** The four arms did not
   share batch sets: `cl_base`/`cl_aug` each carried two pre-session batches
   never re-run, and `nh_aug` had two batches no other arm had. Restricted to
   the two batches common to all four (ev3, ev4): cl_base 190.3, cl_aug 167.8,
   nh_base 109.25, **nh_aug 232.8** — the stated ranking flips. Only the
   "removing `h` hurts" leg survives restriction. **The table was printed as
   like-for-like and was not.**
3. **`PRD_ROADMAP.md` was untouched** and still banked uncertified harness
   numbers (69.3, 89.7, 187.2) while the harness problem was not a roadmap
   item at all. Now carries a caveat and **P6, blocking all future closed-loop
   claims.**

Also noted: `ml/runs/ev3_nh_aug/p5_eval.json` predates the gate and so has NO
`batch_valid` field — absent is not the same as `false`, and the one artifact
holding 3 completions is the one an automated filter would read as unmarked.

## AD.5 What survives all of this

Untouched by the harness problem, because none of it involves the simulator:

- **`h`-dependence** (AB.1): zeroing the RNN state gives skill **-0.120**,
  worse than predicting the mean. Deterministic, open-loop.
- **Copycat refuted** (AB.1): 18.2x better than repeat-last-action.
- **The aux head works** (Z.1): probe AUC 0.673 -> 1.000 at loss weight 100,
  ~zero reconstruction cost, ablation-clean.
- **Small objects are absent from the frozen latent** (Y.2): AUC 0.997 that
  collapsed to 1% of the pos/neg gap under paint-out.
- **Recovery data fixes the off-centre readout 57%** (X.1), frozen encoder.
- **The research brief** (Z.4), including H3's death.

Every one of these is an open-loop measurement. **The project's reliable
results are the ones that never touched the sim** — which is itself the
finding to carry into M3/M4, where the "simulator" becomes a physical car and
the equivalent noise will be worse, not better.

## AD.6 Open items

1. **P6: make the harness trustworthy or quantify it well enough to design
   around.** Now a PRD item and blocking. Cheapest useful version: fix the
   number of launches per arm by the effect size worth detecting, and have
   `eval_in_sim.py` refuse comparisons the noise floor cannot support.
2. Find the launch-level cause. Rate, track and start state are eliminated;
   remaining suspects are inside the Unity process (physics/frame pacing,
   GPU context) and were not reachable from the telemetry available.
3. Re-run the Z.3/AA/AB/AC comparisons at adequate n once (1) exists. Until
   then no ranking of those policies is claimed.
4. Retrain M on the augmented corpus (AB.5) — still the only untested ML
   hypothesis, and still worth doing, but not measurable until (1).
5. **`docs/BOM.md` still modified by another session**, unverified, claiming
   the $200 ceiling is breached. Excluded from commits 2cbb84e and 0bf4264.
6. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.


---

# Appendix AE - Corrections to AD, and a better fix for the harness than the one AD proposed (2026-08-12, ~07:24 CDT)

`/landing-check` on commit e5dceed, run cold against artifacts. Every headline
number in AD re-derived exactly. Six corrections, and one methodological
critique that is more useful than anything AD itself proposed.

## AE.1 Corrections to Appendix AD

1. **"Post-reset position identical to four decimals across 16 episodes" is
   OVERSTATED.** z, speed and `reset_seconds` are identical throughout, but
   **x is not**: episode 0 of *each* launch reads 6.2114 against 6.2116 for
   the other 14. The conclusion is unaffected — the difference is 2.8e-4 world
   units — but the claim as written is false.
2. **The episode pool was stale: 35, not 47.** The `lc_*` launches were added
   by the very commit that quoted the 35-episode pool. Re-derived over all
   gate-valid `nh_aug` episodes at HEAD: **n=47, 30 under 150 steps, 6 at
   450-601, 4 completions.** Still bimodal; conclusion unchanged.
3. **The matched-batch table did not state its estimator.** cl_base 190.3 /
   cl_aug 167.8 / nh_base 109.25 / nh_aug 232.8 are **unweighted
   mean-of-batch-means**. Episode-pooled gives 189.3 / 173.5 / 109.3 /
   **254.7** — nh_aug moves 22 steps, because ev3 (n=9) and ev4 (n=6) disagree
   most on that arm. Unweighted is the defensible choice given the batch is
   the unit of variation, but it should have been said.
4. **Date stamps were wrong in four places.** `ml-training.md`,
   `PRD_ROADMAP.md` (x2) and `HANDOFF.md` stamped edits **2026-08-12** while
   the commit landed 2026-08-11 23:31 CDT — i.e. ~29 minutes in the future.
   Cause: I took the date from a system notice (UTC) instead of the `date`
   call I had already run (2026-08-11 23:29 -0500). The standing rule is to
   run `date` and label by the reported offset; I ran it and then ignored it.
   All four corrected to 2026-08-11.
5. **`PRD_ROADMAP.md` misdescribed the diagnostic it cited.** It said
   "post-warmup **cte** deterministic to four decimals". False — post-warmup
   cte spans 0.0018-0.0075. It is post-**reset position** that is
   near-deterministic. AD's own wording was right; the PRD paraphrase was not.
   Corrected, and the cte spread is now given in context (~0.6% of the ~0.87
   cte the car actually operates at, far too small to explain a 4.4x swing).
6. **The research brief still carried a retracted premise.** Its framing
   question opens with "no learned policy completes a lap". AD said the false
   universal was "corrected in HANDOFF and the bin" and never mentioned the
   brief — while the same commit message listed the brief under "what
   survives". Now caveated in place, noting that the other three framing
   premises are open-loop and unaffected.

Also fixed: `HANDOFF.md` had duplicate item numbers (two 5s and an out-of-order
4) from successive edits, and its status table still showed P5 as
"DONE — SIM-POC COMPLETE" with no caveat and no P6 row, so a fresh session
reading the table got the pre-correction picture. Both repaired.

## AE.2 The power table is a good argument and a bad number

AD's CV-55% table is arithmetically correct and the formula is the right one.
It is also **far softer than AD presented it**, and the reason is not the one
AD flagged.

**The sd is barely estimated, and this is the real defect.** n=7, df=6. The
chi-square 95% CI on sigma gives **CV in [0.36, 1.22]**. Since n scales with
CV^2:

| effect | AD stated | actual 95% interval |
|---|---|---|
| 2x | ~5 | **2 - 23** |
| 50% | ~19 | **8 - 93** |
| 20% | ~120 | **50 - 581** |

**Three lines after establishing that n=1 cannot support a claim, AD committed
the same error one level up** — a single n=7 sample quoted to two significant
figures with no interval. Recorded because it is the same mistake in a new
costume.

**Bimodality matters LESS than AD claimed, and the label was on the wrong
pool.** Normality is assumed of the sampling distribution of the mean
difference, not the raw data, and the CLT absorbs most of it. More to the
point: the bimodality evidence comes from the 35/47-EPISODE pool mixing four
batches, whereas **the 7 launch means the CV was computed from are not
bimodal** — they are right-skewed (skew +1.02), and near-symmetric on a log
scale (log-sd 0.540). The launch process looks multiplicative, which is
exactly the regime where CV is the right scale-free summary. The shape
argument mostly *supports* the parameterisation. What skew does cost is that
nominal 80% power will not be true power at n~5, usually against you — so
treat the n's as floors.

**The unmodelled defect nobody named: the outcome is RIGHT-CENSORED.**
`eval_in_sim.py` defines `survived = steps >= max_steps`, steps caps at 600,
and completions sit exactly on the cap. Mean and sd of a censored variable are
biased toward the cap and understate upper spread; **if two arms differ in how
often they hit it, the censored mean can move opposite to the true one.** This
is a worse problem than bimodality and it silently affects every step-count
comparison in Z, AA, AB, AC and AD. The fix is a completion RATE plus MEDIAN
steps, not a mean.

**And the biggest lever is a design change, not a sample size.** The formula
prices an UNPAIRED design. The launch is the confounder, so run every arm
INSIDE each launch and difference within-launch: the launch effect cancels and
the relevant variance collapses to the within-launch component, which
`diag_reset` and the `lc_*` episodes both put at a few steps. `eval_in_sim.py`
takes one `--ctrl-dir` per invocation and structurally cannot do this today.
**That plausibly beats accepting ~120 launches for a 20% effect by an order of
magnitude**, and AD never considered it. All three are now PRD P6 sub-items.

**What survives intact** is the conclusion AD actually needs: *one launch per
arm resolves only ~3x, so every n=1 comparison in Z/AA/AB/AC was
unmeasurable.* That holds at the optimistic end of the CV interval too — at
CV 0.36, n=1 still resolves only 2.4x, and every retracted difference was
under 1.85x.

## AE.3 A lead AD closed too early

Episode 0 of each launch differs from episodes 1-7 on **both** x (6.2114 vs
6.2116) and post-warmup cte (0.0018/0.0028 vs 0.0073/0.0075), reproducibly, in
both launches. In a session whose thesis is "the launch is the unit of
variation", **a systematic first-episode-after-launch difference is exactly
the signal worth chasing.** The magnitudes are physically tiny and the
conclusion is almost certainly right, but AD closed the hypothesis as "the
start state is deterministic", which the data do not quite say. Left open
rather than quietly dropped.

## AE.4 Open items

1. **P6, now with three concrete levers** (paired design, censoring-aware
   endpoints, CV with interval) rather than the vague "characterise it".
   Paired design first.
2. The first-episode effect (AE.3).
3. Everything still blocked on Evan: `docs/BOM.md` (unverified, claims the
   $200 ceiling is breached, excluded from three commits now), the encoder
   motor (#5159, +$6) and the ~1:20 track re-spec.
4. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.


---

# Appendix AF - AE corrected the record and forgot the live docs, which is the error AE was correcting (2026-08-12, ~07:35 CDT)

Third `/landing-check`, on commit 35fd453. It confirmed every number in AE
re-derives exactly, and then found that **two of AE's six corrections were
written into the append-only record and never applied to the two LIVE
documents carrying the same errors.** That is precisely the failure AE was
correcting AD for, committed one layer up. Recorded because the pattern is now
three deep and clearly systematic rather than incidental.

## AF.1 The pattern

| layer | error | caught by |
|---|---|---|
| AB | reported a result the instrument could not support | replication |
| AC | retracted it, asserted a replacement with the same defect | AD |
| AD | quoted CV 0.553 off n=7 to three figures, three lines after establishing n=1 proves nothing | landing-check 2 |
| AE | corrected AD in the RECORD, left HANDOFF and the bin stating the old numbers | landing-check 3 |

**The common shape: the correction is written where it is easiest to write —
the newest entry — rather than everywhere the claim actually lives.** The
append-only record makes this especially seductive, because appending *feels*
like fixing. It is not. `HANDOFF.md` is the only live snapshot and the bins are
what a fresh session reads; a correction that lands only in the record is a
correction nobody will see.

## AF.2 What was still stale, now fixed

1. **`ml-training.md` and `HANDOFF.md` both still said "35 gate-valid episodes,
   28 under 150, 4 at 450-601".** Corrected everywhere to the re-derived
   **47 / 30 / 6, with 4 completions.**
2. **Both still said the start state was "deterministic to four decimals"** —
   the exact phrasing AE had just corrected in the PRD, and self-refuting where
   the bin quoted "0.0066 vs 0.0069" in the same sentence. Replaced with the
   accurate statement: post-RESET POSITION is near-deterministic; post-warmup
   *cte* spans 0.0018-0.0075.
3. **`ml-training.md` still described "four gate-valid launches ... 2.2x
   spread"** from the intermediate measurement, against the final seven
   launches / 4.4x / CV 55%.
4. **`HANDOFF.md` still read "Last updated: 2026-08-10 ~19:24 CDT"** after two
   commits had rewritten it — in a commit whose stated theme was date-stamp
   correctness. Now 2026-08-12.
5. **`ml-training.md:172`'s "No learned policy completed a lap"** was true as
   scoped to Appendix V's three arms but unmarked, 190 lines above its own
   retraction. Now carries the scope caveat.
6. **PRD P6(c) understated its own bound** (~2x where the arithmetic gives
   2.43x at CV 0.36).

## AF.3 A correction to AE itself

AE.1 §1 states that in `diag_reset`, "z, speed and `reset_seconds` are
identical throughout". **Two thirds of that is wrong**, though harmlessly:

- `z` — genuinely identical across all 16 episodes.
- `speed` — **not identical**: it ranges 1.02e-7 to 4.19e-7. Equal only when
  rounded, and at that magnitude the claim is vacuous rather than true.
- `reset_seconds` — **not identical**: 1.201 and 1.202 both occur.

The conclusion is untouched (a 3e-7 speed difference cannot move a car), but
"identical" was the wrong word and this is the second time in two entries that
an over-strong determinism claim has had to be walked back. **Rule adopted:
write the measured range, never the word "identical", unless the values are
bit-equal.**

## AF.4 What the three landing-checks cost and returned

Three fresh-agent sweeps across commits 0bf4264, e5dceed and 35fd453. Between
them they caught: a false universal committed to a public repo, an unmatched
comparison table presented as like-for-like, four wrong date stamps, a PRD that
misdescribed the diagnostic it cited, a stale episode pool, an unstated
estimator, an untouched roadmap, and this entry's stale live docs. **None of
these were code bugs** — `/code-review` and `code-check` would have passed all
three commits. Every one was a claim that did not match disk, or a correction
that did not propagate.

They also produced the single best idea of the session, which was not mine:
**pair the design** — run every arm inside each launch and difference
within-launch, cancelling the launch effect entirely — rather than accepting
~120 launches per arm to detect a 20% effect. Now PRD P6(a).

## AF.5 Open items

Unchanged from AE, minus the fixed items:
1. **P6**, with its three levers — paired design first.
2. The first-episode-after-launch effect (AE.3), still unchased.
3. **Blocked on Evan:** `docs/BOM.md` (excluded from four commits now,
   unverified, claims the $200 ceiling is breached); the encoder motor
   (#5159, +$6); the ~1:20 track re-spec.
4. **Nothing printed, nothing ordered** - unchanged since 2026-07-23, now
   three weeks.

---

# Appendix AG - Evan's build decisions, the operating point measured, and the camera nobody configured (2026-08-12, ~20:48 CDT)

**WHAT:** Evan made three build calls, the BOM was verified, the sim's physical
operating point was measured for the first time, and a Pi brief ran. A fourth
`/landing-check` then found a false value I had committed as measured data.

## AG.1 Evan's decisions (2026-08-12)

1. **Buy the encoder motor #5159 (+$6).** The decisive argument was never
   odometry in general but the **intersection blind zone** — no lane markings
   for 40-60 cm, the piece that broke all four prior attempts found in the
   2026-07-23 research, two of which fell back to hardcoded timing.
2. **More floor space**, rather than accept the ~1:20 re-spec's 26 mm
   clearance. This retires the 3x5-grid constraint.
3. **Research Pi alternatives**, purchase ~September.

## AG.2 The BOM re-pricing is accurate; the ceiling is genuinely breached

The unattributed re-pricing had been held out of four commits. All six prices
re-checked against live vendor pages and **every one confirmed exactly**: Pi 5
4GB $110.00 pishop / $130.00 Adafruit; Camera Module 3 Wide $38.50; Pololu
#1093 $23.95; #713 $4.95; Pi 5 2GB $65.00. Total ~$222-225 before shipping.
Committed at 9f9af08.

## AG.3 The operating point, measured for the first time

`ml/measure_operating_point.py` (new, 400 steps). **None of this had ever been
written down** — `THROTTLE = 0.20` is a normalised command and the corpus logs
cte but not velocity, so every sim result was tied to an operating point nobody
had recorded.

| quantity | measured |
|---|---|
| control rate | **20.00 Hz** |
| mean operating speed | **1.401 m/s** (max 1.586) -> **7.0 cm per control step** |
| frame | 120x160x3 native |
| \|cte\| held by the expert | mean **0.317 m**, p95 0.789, max 1.122 |
| \|steer\| | mean 0.598, **p95 1.000 — saturating** |

`docs/SIM_TRANSFER_SPEC.md` turns this into the contract the physical car must
meet: 20 Hz sustained, a byte-identical image pipeline, steering authority at
least what the sim uses, and **speed scaled to the lane rather than copied**.
Recommends ~300 mm lanes (85 mm clearance for a 130 mm car) and starting at
0.3-0.5 m/s empirically.

## AG.4 THE CAMERA WAS NEVER CONFIGURED

Chasing one of the spec's own "known unknowns" produced the largest finding of
the day. `donkey_sim.py` sends a camera config only via three paths, all keyed
on `cam_config` / `cam_config_b` being present — and **`cam_config` is absent
from every conf dict in `ml/*.py`.**

**So the FOV, lens distortion, camera height, pitch and forward offset were
never set.** The entire corpus was captured through the Unity binary's default
projection, which is **not recorded anywhere on the Python side.** Camera
Module 3 Wide is 120 deg. If the default differs materially, every learned
component trained on a different lens than the physical car will have — a
first-order sim2real risk that had been invisible.

**Identifying it costs one short sim run and no hardware:** capture at the
default, then at several explicit FOVs from the same pose, and compare. **Do it
before buying a camera** — `docs/BOM.md` row 2 is now flagged HOLD.

## AG.5 Pi: the 2GB, and the "4GB minimum" is folklore

`docs/research/2026-08-12_onboard-compute-selection.md`. Verdict: **Pi 5 2GB,
$65** — same 2.4 GHz Cortex-A76, saves $45, **returns the build to ~$192-205
all-in.**

- **H1 survives.** DonkeyCar's page says "in general, we recommend ... 4GB"
  with **no stated justification**, its `pi` extra installs **tflite-runtime,
  not TensorFlow**, and a **512MB Zero 2 W already drives autonomously**.
- **H4 dies on a primary source.** Raspberry Pi's 2026-04-01 post held the
  1GB/2GB variants flat while raising 4GB by $25. The 4GB has taken every hike
  since Dec 2025 ($70 -> $85 -> $110); the 2GB none. **September price risk is
  concentrated entirely on the 4GB.**
- **H3 dies on camera drivers** — IMX708 lives only in Raspberry Pi's kernel
  fork; Radxa cannot drive even the older IMX219.
- **Honest counterweight:** nobody has benchmarked this actual model, no
  measured RSS figure exists for a DonkeyCar loop on any board, and if 2GB
  blocks you it costs $175 and weeks. The 2GB's failure mode is at `pip
  install` (fixable with swap), not runtime.
- Free lever regardless of board: **export to ONNX** rather than shipping
  PyTorch (~17 MB vs ~65 MB runtime).

## AG.6 A false value was committed as measured data

`/landing-check` #4. `measure_operating_point.py` compared `thr == THROTTLE`,
but throttle round-trips through float32 as `0.20000000298023224`, so **exact
equality never matched.** Consequences:

- `frac_steps_cornering` was written to the committed JSON as **0.0 when the
  true value is 0.605** — a false number presented as a measurement.
- Both conditional prints never fired; `speed_cruise_mean` and
  `speed_corner_mean` were stored as **null**.
- **60.5% of the run was at corner throttle**, so labelling 1.401 m/s "cruise
  speed" was wrong. Fixed to "mean operating speed", with the note that the
  split is not meaningful anyway — corner-throttle mean (1.397) *exceeds*
  cruise-throttle mean (1.209) because speed lags the command. The 7.0 cm/step
  figure survives; it was always the overall mean.

Fixed with `np.isclose`; the JSON was re-derived from the recorded per-step
data and carries a `CORRECTION` field.

**Three further spec defects the same check caught:**
- **An unsourced number: "the car went from 39 to 61 steps".** It appears
  nowhere in the record or codebase. **Withdrawn.** The uint8-before-/255
  practice is real and documented in `eval_in_sim.py`; the quantified gain was
  not. This is the standing no-invented-data rule, broken.
- **"2.6x the grid's margin" is wrong** — 85/26 = **3.27x**. And "comparable to
  Duckietown's relative margin" cited no Duckietown figure; withdrawn.
- **§2.1's rate evidence contradicts the project's own AD.3.** 69 -> 187 steps
  is 2.7x, below the ~3x that a CV-55% harness can resolve at n=1. Direction
  real, magnitude unestablished — now stated that way.

## AG.8 The date error, a third time

This entry was first written stamped **2026-08-13 ~01:52 CDT**. That is wrong;
`date` reported **2026-08-12 20:48 -0500**. I took the date from a UTC system
notice instead of the clock call I had already made — **the identical error AE
corrected in four places and AF recorded as a pattern**, committed again inside
the entry documenting it.

The standing rule is to run `date` and label by the reported offset. Running it
is not the failing step; **using it is.** Hardening the habit: the timestamp is
copied from the `date` output verbatim, and any date that arrives from a hook,
a system notice or a task banner is treated as UTC and never written down.

## AG.7 Open items

1. **Identify the sim camera FOV and mount geometry** (AG.4). Highest-value
   work available with no hardware, and it gates the camera purchase.
2. **PRD P6** — harness trustworthiness, paired design first. Still blocking
   every closed-loop claim.
3. Sim lane width in metres — blocks the clean speed-scaling formula.
4. Evan's call on the Pi 2GB vs 4GB.
5. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.

---

# Appendix AH - The camera was never the constraint; the PWM pin was, and it breaks the Pi 5 too (2026-08-12, ~21:48 CDT)

**WHAT:** `/research-brief` on alternatives to the Raspberry Pi 5 *as a whole*.
Four agents, one per pre-registered hypothesis, each hunting its own falsifier.
The verdict keeps the incumbent, but **both of the reasons the previous brief
gave were wrong**, and the brief surfaced a live defect in the current build
plan. Saved: `docs/research/2026-08-12_pi5-alternatives.md`.

## AH.1 The prior brief's central argument does not hold

The 2026-08-12 compute brief rejected every non-Pi board because DonkeyCar
depends on `picamera2` and IMX708 drivers are Pi-only. **Verified false in
DonkeyCar `main` source:**

- `picamera2` and `RPi.GPIO` are **only in the `pi` extra**, not
  `install_requires`.
- `PiCamera` imports picamera2 **inside `__init__`** — with `CAMERA_TYPE=CVCAM`
  it never executes.
- `templates/complete.py` dispatches PICAM / WEBCAM / CVCAM / CSIC / V4L /
  IMAGE_LIST / LEOPARD / MOCK, all lazily.
- **The `nano` extra is the existence proof**: `Jetson.GPIO` instead of
  `RPi.GPIO`, and no `picamera2` at all. Upstream already ships a non-Pi build.

That the prior brief's own H3 rested on this is worth recording: **the
conclusion (stay with the Pi) survived, the argument did not.** A correct
answer reached through a wrong argument is not a validated answer.

## AH.2 The real constraint, and it bites the incumbent

`parts/pins.py` has **exactly three PWM backends: RPI_GPIO, PCA9685, PIGPIO.**
No libgpiod, no periphery, no vendor GPIO. **Two of three are Pi-only**; the
third needs a PCA9685 breakout that is **not in the BOM** (checked absent, and
absent from the deferred list). Evan's wiring drives the servo and TB6612FNG
straight off GPIO.

**And `RPi.GPIO` does not work on the Raspberry Pi 5 at all.** Verified against
the Raspberry Pi forum directly (thread 361834): *"RPi.GPIO is not compatible
on PI5"*, failing with `Cannot determine SOC peripheral base address` because
Pi 5 moved GPIO behind the **RP1 southbridge** while RPi.GPIO poked registers
through `/dev/mem`. Replacements: **`rpi-lgpio`** (drop-in), `gpiozero`,
`libgpiod`.

**`donkeycar[pi]` installs `RPi.GPIO`.** So this is not a comparison point
between boards — **it is a defect in the current plan**, and it would have
surfaced as a mystery failure on the bench in September.

## AH.3 H3 dies on a number that was measured, not argued

The onboard path was benchmarked locally (4 CPU threads to mimic the Pi's four
cores, 300 iterations after warmup, real `ConvVAE.encode` + `Controller` +
`MDNRNN.lstm`):

| | |
|---|---|
| ConvVAE | 4,348,547 = **encoder 755,744** + decoder 3,592,803 |
| MDN-RNN / Controller | 382,533 / 74,498 |
| **onboard path** | **1,212,775 params — 28% of the headline 4.35M** |
| **full step** | **0.903 ms -> 1108 Hz** |
| **vs the 50 ms budget** | **55x headroom** |

**The decoder never runs on the car.** `models.py` notes callers use `mu`
directly at eval; a Ha & Schmidhuber controller is `a = W[z,h]+b`; and even M4's
latent imagination needs no decoder. **Every prior discussion of "the 4.3M-param
model" overstated the onboard workload by 3.6x.**

Also against accelerators: Hailo's compiler reportedly rejects LSTM/GRU
outright ("not supported layers", community thread 2025-07-13), and its
documented fallback is **unrolling to a fixed sequence length**, which is not
the stateful single-step RNN a driving MDN-RNN needs. **Coral is archived**
(`google-coral/edgetpu`, 2026-04-19, flagship complaint unanswered).

**Caveat kept prominent:** this is a desktop x86 CPU, not a Cortex-A76, and it
measures the MODEL ONLY — not capture, resize, or DonkeyCar's vehicle loop.
The agents' own warning stands: the 20 Hz risk is per-frame Python overhead,
not FLOPs.

## AH.4 The rest of the field

- **BeagleY-AI is the only board that partially falsifies "only Pi has working
  software"** — first-party Debian 13.6 images dated **2026-07-24**. But it is
  **$70 against the Pi 5 2GB's $65**: the reason to leave the Pi is money, and
  the one board with real software costs more.
- **US stock has collapsed for Radxa** (Rock 5A/5B, Zero 3W, X2L all out of
  stock 2026-08-12; 5C and Zero 3E unlisted). `ubuntu-rockchip` **archived
  2026-04-29**, narrowly replaced.
- **Off-board compute over WiFi fails on measurement**: best figure 200 ms
  (WebRTC, 720p30, glass-to-glass) against a 50 ms budget. The honest
  counter — a raw 64x64 frame is 12,288 bytes and skips the encode/jitter/decode
  stages that dominate that 200 ms — **has no measured figure behind it**, and
  jitter rather than mean latency is what kills a steering loop.
- **Android/OpenBot** is the only left-field option not dismissed: proven
  architecture, ~$0 if a phone exists, GPIO sidestepped via Arduino over USB
  OTG. Costs a full Kotlin rewrite, abandons DonkeyCar, and NNAPI was
  deprecated in Android 15. A cheaper project and a worse one.
- **Used market: no usable prices, second consecutive brief.** Treat "used is
  cheaper" as unverified. Meanwhile **RAM prices are up ~7x** and drove the Pi
  increases — September is likelier worse than better.

## AH.5 Method note: all four arms returned PARTIAL

The previous process died mid-run. The agents were **resumed from transcript**
rather than restarted, and instructed to deliver only what they had actually
sourced with a NOT-YET-COLLECTED section. That preserved real work — but the
brief has genuine holes, the largest being **Libre Computer, entirely
unsourced**, which was one of the two best shots at falsifying the Pi's
software advantage. Recorded as a limitation rather than papered over.

One agent also flagged a DigiKey price ($72.54) that came from a search
snippet rather than a fetched page. **Not entered anywhere.**

## AH.6 Actions this forces regardless of board

1. **Plan on `rpi-lgpio`** — `donkeycar[pi]`'s `RPi.GPIO` is broken on Pi 5.
2. **Decide the PWM path before ordering.** Straight-to-GPIO locks the project
   to a Pi; a PCA9685 breakout makes actuation pure I2C and board-agnostic, at
   a cost not yet collected.
3. **Measure the real loop rate on hardware** before trusting the 55x headroom.

## AH.7 Open items

1. Libre Computer — the unsourced gap.
2. The sim camera FOV/mount identification (AG.4) — still the top no-hardware
   item, and still gating the camera purchase.
3. PRD P6 — harness trustworthiness, paired design first.
4. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.


---

# Appendix AI - The track regenerates every launch (that is the harness mystery, solved), and the sim FOV is 90 (2026-08-13, ~00:56 CDT)

**WHAT:** the camera-FOV identification from AG.4, which was the top
no-hardware item. It answered its own question **and** solved the harness
variance that AD/AE/AF spent three entries failing to explain — by failing
first, loudly, in a way that pointed at the cause. New: `ml/diag_camera_fov.py`.

## AI.1 The generated track is regenerated EVERY LAUNCH

The FOV test compares a default frame against frames captured at explicit
FOVs. On `donkey-generated-track-v0` it returned garbage: the
**default-vs-default noise floor was 23.9 MAE**, and on a second attempt with
a fully-controlled pose (no warmup, car stationary at spawn) it got *worse* at
**48.4** — swamping a real signal of ~50.

Three identical-config launches, captured at the identical spawn pose:

| pair | MAE | median | pixels differing >30 |
|---|---|---|---|
| 1 vs 2 | 30.02 | 10.0 | **31.4%** |
| 1 vs 3 | 36.45 | 17.0 | **35.1%** |
| 2 vs 3 | 29.32 | 14.0 | **27.3%** |

Mean brightness across the three: 121.3 / 123.1 / 127.9 — **spread 6.65, i.e.
stable.** So this is not lighting or time-of-day. **A third of the pixels
differ structurally between launches: the scene itself is different.** The
"generated" in `donkey-generated-track-v0` is literal.

**Confirmed by contrast:** the identical test on the FIXED `donkey-warehouse-v0`
gives a default-vs-default noise floor of **0.307** — 158x smaller.

## AI.2 This is the harness mystery from AD, and I got that one wrong

**AD.2 listed "track identity" as ELIMINATED**, on this reasoning: the expert's
mean|cte| spans only 0.323-0.381 over 12 launches, and "a regenerated track
could not produce a +-5% band from a fixed PID."

**That reasoning is wrong.** A PID tracking a centreline produces similar
mean|cte| on *any* track whose curvature statistics are similar — which is
exactly what a track *generator* produces. Tight cte was never evidence of an
identical track, and I treated a weak proxy as a measurement.

**It explains every observation AD/AE/AF could not:**
- **The 4.4x launch-to-launch spread on a fixed checkpoint** (106.5 to 471.5) —
  each launch is a *different track*, so a marginal policy meets a different
  difficulty each time.
- **Episodes WITHIN a launch agreeing to a few steps** (107/107, 108/108) —
  same track for the whole launch.
- **The expert being unaffected** (600/600 everywhere) — a PID on cte does not
  care about track shape, which is precisely why it made such a poor control.
- **The bimodality** (28 of 35 episodes under 150 steps, 4 at 450-601) — some
  generated tracks are easy and most are not.
- **Why start state, control rate and reset determinism all came back clean** —
  they were all fine; the variable was never inside the episode.

**The launch is the unit of variation because the TRACK is the unit of
variation.** Not a bug — the sim doing what its name says, unnoticed for the
whole project.

**Consequences that need acting on:**
1. **PRD P6's "cause unknown" is closed.** The fix is now concrete: evaluate on
   a FIXED track, or deliberately average over many launches and report the
   spread as track difficulty. The paired-design lever from AE.2 is still right
   and now has a mechanism: pairing arms *within* a launch holds the track
   constant.
2. **The corpus spans many generated tracks.** 88 episodes collected across
   multiple launches means the training data covers many layouts. That is
   *good* for generalisation and it means "the track" was never one track — the
   fit/val split by episode was never a within-track split either.
3. **Every closed-loop comparison in Z, AA, AB, AC, AD remains uncertified**,
   but the reason is now understood rather than mysterious.

## AI.3 The sim FOV is 90, and the Camera Module 3 Wide is the right part

Re-run on the fixed track, noise floor 0.307:

| fov | MAE vs default |
|---|---|
| 60 | 47.369 |
| **90** | **0.192 <- matches** |
| 120 | 42.950 |
| 150 | 50.025 |

**The sim default is `fov=90`**, unambiguous at a 0.307 noise floor with every
other tested value 140x further away.

**What that means for the purchase.** Unity's `Camera.fieldOfView` is VERTICAL
by default. At 160x120:

| | horizontal | diagonal |
|---|---|---|
| sim (fov=90 vertical) | **106.3 deg** | **118.1 deg** |
| Camera Module 3 **Wide** | 102 deg | 120 deg |
| Camera Module 3 standard | 66 deg | 75 deg |

**The Wide is within 4.3 deg horizontal and 1.9 deg diagonal.** Even under the
alternative reading (fov=90 as horizontal) the Wide is 12 deg wide, while the
standard module is ~40 deg off under *either* reading. **The Wide is correct
under both interpretations and the standard module is definitively wrong.**

**`docs/BOM.md` row 2 HOLD is LIFTED.** The camera specced back on 2026-07-23
turns out to match the projection the corpus was captured through — by luck,
not by design, since nobody had set or checked it.

**Stated as an assumption, not a measurement:** the vertical-FOV reading rests
on Unity's documented default, not on anything measured here. It does not
change the decision (the Wide wins either way), but the exact horizontal FOV is
+-12 deg depending on the convention.

**Still unmeasured: camera height, pitch and forward offset.** `offset_x/y/z`
and `rot_x/y/z` were never set either, and the same comparison method would
identify them — but each needs a scan over a continuous parameter rather than
four discrete guesses, so it is a larger job than the FOV was.

## AI.4 Method note: the failure was more informative than a success

The first two runs of this experiment produced no answer. What made them
useful was the **sanity check written into the script before it ran** — "if
the explicit-FOV frames are all identical to each other, cam_config is being
ignored and this method cannot answer the question." That check fired, proved
cam_config *was* working (MAE 70 between fov=60 and fov=150), and forced the
question "then why is default-vs-default so noisy?" — which is the entire
finding in AI.1.

Without it the honest conclusion would have been "cam_config appears to be
ignored", which is false, and the track regeneration would still be undiscovered.

## AI.5 Open items

1. **Re-run the closed-loop comparisons on a FIXED track.** Z.3, AA.1, AB.2,
   AC.1 are all re-runnable now that the confound is known and controllable.
   This is the highest-value ML work available.
2. Camera height/pitch/offset identification (AI.3).
3. Libre Computer, still unsourced (AH).
4. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.


---

# Appendix AJ - The closed-loop comparison, re-run PAIRED and finally valid: no intervention helps (2026-08-13, ~15:47 CDT)

**WHAT:** AI.5's top item — re-run Z.3 / AA.1 / AB.2 / AC.1 now that the
confound (track regeneration per launch) is known and controllable. New:
`ml/eval_paired.py`. **This is the first closed-loop comparison in the project
that is a measurement rather than an anecdote**, and the answer is a clean
negative.

## AJ.1 A fixed track does not work, and that is itself a finding

The obvious fix — evaluate on a track that does not regenerate — was tried
first and **fails for a reason worth recording.** Two fixed outdoor tracks were
confirmed genuinely fixed by launch-to-launch frame comparison:

| track | launch-to-launch MAE | |
|---|---|---|
| `donkey-avc-sparkfun-v0` | 0.367 | FIXED |
| `donkey-mountain-track-v0` | 0.481 | FIXED |
| `donkey-generated-roads-v0` | 3.504 | **also REGENERATED** |
| `donkey-generated-track-v0` | 29-36 | REGENERATED (AI.1) |

But on both fixed tracks the learned controllers **collapse to 13-67 steps at
mean|cte| 2.2-3.8**, against the 0.317 the expert holds in training. Every
fixed track is far outside the corpus's visual distribution, so all arms bunch
at the floor and the comparison measures nothing. **The generated track is the
only in-distribution option**, which is why pairing — not track substitution —
is the fix.

**A defect in my own batch-validity gate surfaced here.** It fired BATCH
INVALID on both fixed tracks because the expert did not survive (425 and 549 of
600). But that is not sim degradation — it is PID gains tuned at 20 Hz on the
generated track failing to complete a tighter course. **The gate conflates
"simulator degraded" with "track harder than the expert's tuning"**, and would
silently invalidate any legitimate new-track experiment. Recorded; not yet
fixed.

## AJ.2 The paired design, and what it bought

`eval_paired.py` runs **every arm inside ONE launch**, so all four share that
launch's generated track, and reports the **within-launch difference**. Track
difficulty cancels exactly. Verified before running on synthetic data with a
known +40 effect and per-launch offsets of +0/+300/-100: the paired difference
recovered +40 with **sd 0.0** while the unpaired sds were 208.

4 launches x 3 seeds x 2 episodes. **The expert completed 600/600 in every
launch** — so for once the batch is unambiguously valid.

| launch | expert | cl_base | cl_aug | nh_base | nh_aug |
|---|---|---|---|---|---|
| 1 | 600.0 | 122.5 | 119.0 | 151.7 | 132.5 |
| 2 | 600.0 | 215.7 | 158.2 | 121.3 | 152.3 |
| 3 | 600.0 | 65.0 | 64.3 | 94.5 | 94.5 |
| 4 | 600.0 | 215.2 | 172.7 | 188.2 | 436.0 |

**Paired differences vs `cl_base`, n=4, df=3, t_crit 3.182:**

| arm | mean diff | sd | t | signs | verdict |
|---|---|---|---|---|---|
| cl_aug (+recovery) | **-26.0** | 28.4 | -1.84 | **4/4 negative** | n.s. |
| nh_base (z-only) | -15.7 | 58.8 | -0.53 | 2/4 negative | n.s. |
| nh_aug (z-only +rec) | +49.3 | 121.2 | 0.81 | 1/4 negative | n.s. |

**NO ARM BEATS THE BASELINE.** Same conclusion as AA and AC — but this time it
is a measurement rather than an absence of one.

## AJ.3 Three things the numbers say that the verdict line does not

1. **Pairing helped, but did NOT fully solve it.** Variance of the difference
   vs the arm's own unpaired spread: cl_aug 48.4 -> **28.4 (helped)**,
   nh_aug 156.6 -> **121.2 (helped)**, nh_base 40.3 -> **58.8 (did NOT help)**.
   If the track were the only confound, pairing would reduce variance for every
   arm. It did not. **There is real arm x track interaction** — different
   policies genuinely suit different layouts — which is behaviour, not noise,
   and it is not removable by better experimental design.

2. **The most consistent signal points AGAINST recovery data.** `cl_aug` is
   negative in **4 of 4** launches. Not significant (t=-1.84; ~19 launches
   needed at 80% power), but a sign that is consistent across every paired
   comparison is the strongest evidence in the table, and it says recovery data
   mildly **hurts** when `h` is present. That is a stronger statement than
   AA's "no effect", and it is the opposite of what X.1 predicted.

3. **`nh_aug` produced a large positive from ONE launch again** (+221 in launch
   4; 1/4 negative overall). **This is the second time this exact configuration
   has generated a headline from a single launch** — the first was Appendix AB,
   retracted in AC. Recorded as a behavioural signature: **`nh_aug` is
   high-variance and occasionally lucky, not better.** Any future result from
   this arm should be assumed to be launch 4 again until shown otherwise across
   many launches.

## AJ.4 What this settles, and what it costs

**Settled:** recovery data, DART expert relabelling, recovery loss weighting,
and removing the history input have now all been tested with a design that
matches the confound, and **none of them improves closed-loop driving.** The
X.1 finding (57% better off-centre probe readout with a frozen encoder) remains
true and remains untransferred — five attempts.

**Not settled, and not cheap:** at n=4 launches this design resolves roughly a
2x effect. Detecting the ~17% `cl_aug` effect would take ~19 launches, about
2.5 hours of sim. That is affordable if the question is worth it; it probably
is not, since the interesting hypotheses are exhausted.

**The honest position for the portfolio:** the SIM-POC produced a working world
model, a measured 8 GB DreamerV3 boundary, a validated auxiliary-head fix for
small-object blindness, and **a well-instrumented negative on policy
extraction** whose cause is now understood down to the simulator's track
generator. That is a stronger engineering story than a policy that half-works
for reasons nobody checked.

## AJ.5 Open items

1. **Fix the batch-validity gate's semantics** (AJ.1) — it cannot distinguish a
   degraded sim from a harder track.
2. Camera height/pitch/offset identification (AI.3) — same method as the FOV,
   but a continuous scan.
3. Sim lane width in metres — still blocks the clean speed-scaling formula in
   `SIM_TRANSFER_SPEC` §2.4.
4. Libre Computer, still unsourced (AH).
5. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.

# Appendix AK - Scheduled daily-audit: the sim FOV that AI identified by comparison is now pinned in code, and a secret gate is wired (2026-08-16, ~13:28 CDT)

## AK.1 What ran

The `daily-audit` scheduled task ran a cross-project cold audit; Evan
replied "do all." Two fixes here (AC-1, AC-2).

## AK.2 AC-1 - cam_config chokepoint

AI (2026-08-13) identified the sim's default FOV as 90 degrees by
comparison - `diag_camera_fov.py` sweeping explicit values against the
unrecorded default. That identification was never asserted anywhere in the
code that actually launches the sim: `cam_config` appeared in exactly one
file (the diagnostic itself); the 9 modules that build the corpus, measure
the operating point, and run every closed-loop eval (`collect_sim_data.py`,
`measure_operating_point.py`, `eval_paired.py`, `verify_env.py`,
`collect_recovery.py`, `diag_reset.py`, `eval_in_sim.py`, `plan_cem.py`,
`trace_failure.py`) each hand-built a conf dict with no camera geometry at
all. A gym-donkeycar or DonkeySimWin version bump could move every measured
number in `docs/SIM_TRANSFER_SPEC.md` with nothing to notice.

Added `ml/sim_conf.py`: one `base_sim_conf()` builder carrying the pinned
`fov=90` cam_config, callers keep only `port`/`car_name`/overrides.
Migrated all 9 launch sites to it. `diag_camera_fov.py` deliberately left
untouched - its whole job is sweeping FOV values including "none sent" to
IDENTIFY this constant, so it must not import the thing it discovered.

## AK.3 AC-2 - secret gate wired

No `core.hooksPath`, no native `.git/hooks/pre-commit` - same gap as Swing
Trading. Added `scripts/git-hooks/pre-commit` (secret-gate delegation only;
this repo has no HTML-twin record per CLAUDE.md) and set
`core.hooksPath scripts/git-hooks`.

## AK.4 Verification

- **P1 done-check re-run for real, post-migration:** `ml\verify_env.py` ->
  `torch 2.13.0+cu126`, `cuda.is_available: True`,
  `device: NVIDIA GeForce RTX 3060 Ti`, sim launched, `reset ok: obs (120,
  160, 3) uint8`, `step ok`, frame saved, **`P1 DONE-CHECK: PASS`**.
- Confirmed exactly the 9 intended call sites now import `sim_conf`
  (`grep -rl "from sim_conf import"`) and exactly one hand-rolled conf dict
  remains, in `diag_camera_fov.py` (the deliberate exception).
- AC-2: staged content, ran the hook directly - clean, exit 0.

## AK.5 Status

- AC-1, AC-2: closed.
- Not pushed - Evan has not authorized a push.

# Appendix AL - Scheduled daily-audit: 23 findings; three cache readers skip the encoder fingerprint, and the record guard's missing-file branch fails OPEN under a "Fails CLOSED" comment (2026-08-25, ~07:21 CDT)
Audit run - 23 findings (2 high, 6 med, 10 low, 5 edge cases), findings only, nothing changed.

**Top:** `ml/train_cte_probe.py:85`, `ml/train_controller.py:207-209` and
`ml/diag_copycat.py:87-89` load the cached latents `ml/data/proc/train_mu.npy`
with no encoder-fingerprint check, while `ml/train_mdnrnn.py:57-60` and
`ml/rollout_eval.py:192-203` do check. Retrain the VAE without deleting the
cache and the probe trains on the old encoder's latents silently. Second high:
three `fit_val_episodes()` call sites take the split seed from the checkpoint
and three do not (`compare_encoders.py:163`, `probe_cone.py:173`,
`train_cte_probe.py:91`), the same class as the bug `rollout_eval.py:205-213`
already documents.

**Cross-project:** `scripts/git-hooks/pre-commit`'s record-invariant block
carries the comment "Fails CLOSED" directly above an `else` branch that fails
OPEN. The enforcement path itself is sound - `append-record-entry.js --canary`
prints `CANARY PASS 45/45` - but when the guard FILE is absent the commit
proceeds: with `HOME` pointed at an empty directory the live hook printed both
skip warnings and exited **0**. The same branch is in all **six** repos carrying
the block - Autonomous Car Project, ServeLocal, Skills, Swing Trading, Trading
and World Models Research - so a fresh clone or a second machine commits
unverified. (Corrected before this entry was committed: the count first
written here was "five", which omitted Trading, where the block is present
on disk but uncommitted. Found by the 2026-08-25 landing-check, F5.)

**Docs:** the record's cadence rule and HANDOFF's session-end sync were both
missed for the three commits after Appendix AK (`e8b464b`, `3e5f6bf`,
`fc4c75f`) - the LF pin and the record-guard delegation are in no entry.

Full report in the scheduled daily-audit session output for 2026-08-25.

# Appendix AM - 3DStreet wired for the track layout, and the AL audit fixes found sitting uncommitted (2026-09-01, ~15:12 CDT)
**CADENCE NOTE:** first entry since AL (2026-08-25). AL itself recorded that
the cadence rule and the HANDOFF session-end sync were both missed for three
commits; that gap is closed in AM.4 rather than left implicit.

**WHAT:** Evan is building the physical street layout in 3dstreet.app and
supplied the `3dstreet-mcp` server config. Wired it up, assessed the fit
against the track this project actually needs, and — while surveying state for
a handoff — found the Appendix AL audit fixes complete but uncommitted in the
working tree.

## AM.1 3DStreet MCP: wired, with a fit caveat that matters more than the wiring

`.mcp.json` written at the project root (project scope). `npx` 11.9.0 is
present. **The `claude` CLI is not on PATH in this environment**, so the
`claude mcp add` form Evan supplied has to be run by him; the JSON file is the
equivalent and loads on restart.

**What the server actually is:** a bridge to a LIVE 3DStreet browser tab over
WebSocket — not a headless generator. Tools: `getScene`, `getEntity`,
`entityCreate/Update/Remove/Clone/Reparent`, `componentAdd/Remove`,
`segmentAdd/Update/Remove`, `selectEntity`, `focusCamera`, `undo/redo`. It is
**alpha, protocol subject to change**, and carries no auth token — it
piggybacks on whichever tab is already signed in.

**The fit problem, stated before any time is spent on it.** 3DStreet is
Streetmix-lineage: its competence is the street CROSS-SECTION (what sits in
the street left-to-right) extruded along a line. Its own materials describe
drag-and-drop **linear** streets plus **4-way 90-degree, T and dead-end**
intersections; **no evidence of curved streets was found**.

**This project's track is a FIGURE-8**, and its hard part is plan-view
geometry — corner radii, closing the loop, fitting the floor. That is exactly
what the tool does not do. What it IS good for: lane widths, dash patterns,
sign placement, and a presentable 3D render for the portfolio.

Second mismatch: 3DStreet works in **real-world street units** (a real lane is
3-3.6 m; this track's is ~0.3 m, roughly 1/11). Designing at 1:1 and scaling
on export is workable, but typing 0.3 into a lane-width field is not.

**Recommendation recorded:** use it for the marking design and the render;
keep the figure-8 geometry in a plain dimensioned plan where the radius
constraint is checkable.

## AM.2 The constraint that gates the layout, and it is still an estimate

Consolidated from the record so the layout work has one place to read:

| constraint | value | source |
|---|---|---|
| floor space | was **1.6 x 2.8 m**; Evan chose "more floor space" 2026-08-12, amount **not yet specified** | Appendix L; AG.1 |
| lane width | **~300 mm** (85 mm clearance for a 130 mm car) | `SIM_TRANSFER_SPEC` §3 |
| corner radius | **>=500-670 mm centreline**, from an estimated ~330 mm min turn radius | Appendix L |
| layout | **figure-8**, never an oval (an oval teaches "always steer left") | `gotchas.md` |
| stop sign | **relocatable/removable** — a fixed sign is predictable from position | Appendix Y.3 |
| surface | print MARKINGS, not road (~0.15 kg vs ~6.4 kg) | `gotchas.md` |
| dashes | MUTCD 1:3 does not survive at scale; Duckietown ~2:1, a documented deviation | Appendix L |

**The corner radius is arithmetic on an estimate, not a measurement.** Min
radius ~ wheelbase / tan(max steer) ~ 330 mm assumes a 130 mm car width that
is itself unmeasured until B2/B3. Appendix L already ruled that corner tiles
must not be cut until B3 and an empirical turning test on the rolling chassis.
**Designing the look now is fine; committing corner geometry now risks a track
the car physically cannot drive.**

**Blocked on Evan:** how much floor space there actually is. Every dimension
scales off it and "more" is not a number.

## AM.3 The AL fixes are done, verified to compile, and were never committed

Surveying state for the handoff turned up **19 modified files, 299 insertions,
uncommitted** — including Appendix AL itself. AL's own text says "findings
only, nothing changed", which was true when written; the fixes landed
afterwards and then stalled before commit.

**Both AL high findings are addressed:**

- **Finding 1 (stale latent cache).** `ml/splits.py` gains
  `load_cached_mu(split, vae_ckpt, proc)` — a chokepoint that returns the
  cached `{split}_mu.npy` **only if** its encoder fingerprint matches, else
  `None`, letting each caller decide between re-encoding and failing loudly.
  The three readers that previously skipped the check
  (`train_cte_probe.py`, `train_controller.py`, `diag_copycat.py`) now use it.
  `train_cte_probe.py` has no encoder loaded to re-encode with, so it treats a
  stale cache as a **hard stop**, which is the right call for that script.
- **Finding 2 (split seed).** The three `fit_val_episodes()` call sites that
  used a hardcoded default now take the seed from the VAE checkpoint, matching
  the convention `rollout_eval.py` already documented.

**Verified this session:** all 11 changed modules compile, and `splits.py`'s
own gate prints `splits self_check: PASS`. **NOT verified:** that any of the
affected scripts still produce correct results end-to-end — no training or
eval was re-run. **Do not treat these as validated fixes; treat them as
complete-looking and unrun.**

## AM.4 Closing AL's documentation gap

AL flagged that three commits after Appendix AK carry no record entry. Named
here so the record is continuous:

| commit | date | subject |
|---|---|---|
| `e8b464b` | 2026-08-20 23:46 | Delegate record-invariant checking in the pre-commit hook |
| `3e5f6bf` | 2026-08-21 16:25 | Restore the missing TOC line for Appendix AK |
| `fc4c75f` | 2026-08-21 16:29 | Pin shell scripts and git hooks to LF |

The substance of each is in its commit message; this entry does not restate
work it did not do, it only makes the gap navigable.

**Still open from AL, unfixed:** the pre-commit record-guard's missing-file
branch **fails OPEN** under a comment reading "Fails CLOSED" — verified live by
pointing `HOME` at an empty directory, where the hook printed both skip
warnings and exited 0. The same branch is in **six** repos. Cross-project, so
it is not this project's to fix alone, but it means a fresh clone or a second
machine commits unverified.

## AM.5 Open items

1. **Floor space number** — blocks every track dimension.
2. **Commit or discard the uncommitted AL fixes.** They compile; they are unrun.
3. Corner geometry stays frozen until the B3 turning test.
4. Pre-commit guard fails OPEN (cross-project, from AL).
5. Pi 2GB vs 4GB — Evan's call, purchase window is now.
6. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.

# Appendix AN - Floor space is 3x3 m; car width must be measured not chosen; and the lane-width rule was over-provisioned (2026-09-01, ~15:31 CDT)
**WHAT:** Evan answered the floor-space question (3.0 x 3.0 m), asked whether
the car could shrink to ~100 mm, and then **caught a real over-provisioning in
the lane-width rule I wrote in `SIM_TRANSFER_SPEC` §3**. The rule is corrected
here from a fixed clearance to a proportional one.

## AN.1 Floor space: 3.0 x 3.0 m, and it is generous

The number that had been blocking M1.4b. **9 m2 against the 4.48 m2 the
original 1.6 x 2.8 m plan assumed** — so the "more floor space" decision of
2026-08-12 more than doubled the area, and space is no longer the binding
constraint on anything.

Figure-8 as two tangent loops, bounding box `(2R + W) x (4R + W)`:

| car | lane | clearance/side | max corner R that fits in 3 m |
|---|---|---|---|
| 100 mm | 270 mm | 85 mm | 682 mm |
| 100 mm | 300 mm | 100 mm | 675 mm |
| 130 mm | 300 mm | 85 mm | 675 mm |
| 130 mm | 330 mm | 100 mm | 668 mm |

**Every combination fits the full estimated 500-670 mm corner range.** At
R=500 the figure-8 is 1.30 x 2.30 m; at R=670 it is 1.64 x 2.98 m — the tight
end just fits, the comfortable end leaves most of a metre.

## AN.2 Car width: measure it, do not choose it

Evan asked about ~100 mm. **Space does not require it** (AN.1), and neither
does turn radius: `R_min ~ wheelbase / tan(max steer)` gives **157-322 mm**
across plausible wheelbases (110-150 mm) and steer angles (25-35 deg), all far
below the 500-670 mm corners the track would actually use. **Shrinking the car
to buy a tighter turning circle solves a problem this project does not have.**

What it would buy is clearance — ~18% more per side at a given lane width,
aimed at the measured off-centre perception failure.

**What blocks it: car width is not a free parameter.** It is track width,
outer wheel face to outer wheel face, set by the Lego steering rack and diff —
fixed parts. Working back from 100 mm: two wheels at 20-22 mm each (44309 is
22 mm wide, 32019 is 20 mm) consume 40-44 mm, leaving ~56-60 mm between the
inner faces for the differential (62821 is a 28-tooth module-1 ring, ~28 mm
pitch diameter, plus housing) and the front knuckles. Plausible and tight.

**And the existing 130 mm was itself never measured** — Appendix L flags it
unmeasured until B2/B3. Choosing 100 mm now trades one estimate for another.
**Decision: build to the parts, measure the assembled rack + diff at M1.2/B2,
and set lane width from the MEASURED result.** Also noted: a smaller car sits
the camera lower, and the sim's camera height and pitch are still unidentified
(AI.3) — only `fov=90` was pinned.

## AN.3 The lane-width rule was wrong, and Evan caught it

He observed that real lanes are only ~1.8-2x vehicle width. **He is right, and
the spec was well outside that.** Sourced:

| reference | lane : vehicle |
|---|---|
| US highway lane (12 ft = 3658 mm) / typical car body (~1850 mm) | **1.98x** |
| Duckietown: 210 mm lane / Duckiebot DB21 (~150 mm) | **1.40x** |
| Duckietown, if the chassis is nearer 130 mm | **1.62x** |
| **previous spec: 300 mm / 130 mm** | **2.31x** |
| **previous spec: 270 mm / 100 mm** | **2.70x** |

**The old rule was wider than every real reference — up to 93% wider than
Duckietown.** Worse, its justification does not survive scrutiny: I wrote that
85 mm/side was "the cheapest insurance against the measured off-centre
perception failure", but **widening a lane does not fix perception, it only
delays the consequence**. And Duckietown demonstrably runs learned policies at
**30-40 mm per side**, under half what I specced.

**Corrected rule: lane width = 2.0 x the MEASURED car width.**
200 mm for a 100 mm car (50 mm/side), 260 mm for a 130 mm car (65 mm/side).

**Why 2.0x rather than Duckietown's 1.4-1.6x**, stated so it is not mistaken
for splitting the difference: Duckiebots are **differential-drive and can pivot
in place**; this car is **Ackermann-steered with a real minimum turn radius**
and cannot recover from a bad line the same way. 2.0x matches real-road
proportion, still leaves more margin than Duckietown, and **costs essentially
nothing here** — maximum corner radius moves only 675 mm to 685-700 mm.

**Caveat kept in the spec:** the 150 mm Duckiebot width comes from a
"13x6x9 in / 34x15x23 cm" product listing that may describe the shipping box
rather than the chassis, so the 1.40x figure is soft. Either reading puts
Duckietown tighter than real roads, which is the point that matters. **This is
the second Duckietown comparison in this project; the first was withdrawn as
uncited in Appendix AE, so this one was sourced before use.**

## AN.4 Open items

1. **Measure the assembled steering rack + diff** (M1.2/B2) — sets car width,
   which now sets lane width by rule.
2. Corner geometry still frozen until the B3 turning test.
3. Camera height / pitch / offset still unidentified (AI.3) — same comparison
   method that found `fov=90` would find them, no hardware needed.
4. Pi 2GB vs 4GB — Evan's call, purchase window is now.
5. The AL audit fixes remain uncommitted and unrun (AM.3).
6. **Nothing printed, nothing ordered** - unchanged since 2026-07-23.

# Appendix AO - The AL audit fixes, run: the encoder-fingerprint guard is a false negative and breaks train_cte_probe.py (2026-09-01, ~15:46 CDT)
The AL audit fixes had been sitting uncommitted since 2026-08-25, described in
AM as "compile, splits.py self-checks PASS, nothing re-run end-to-end". Ran
them. **The central fix is wrong and breaks a working script.**

## AO.1 What the fix does

Cold-audit finding 1 said three readers of the latent cache
(`ml/data/proc/train_mu.npy`) load it without checking which VAE produced it.
The fix adds `splits.load_cached_mu()` as a shared chokepoint: it returns the
cached array iff `{split}_latents.key` matches `encoder_fingerprint(vae_ckpt)`,
otherwise `None`. `train_cte_probe.py` treats `None` as a hard stop;
`train_controller.py` and `diag_copycat.py` treat it as "re-encode in memory".

## AO.2 The regression, run

`ml/data/proc/` contains **no `.key` file at all** — the fingerprint scheme
postdates the cache, and nothing but `train_mdnrnn.py` can stamp one.
`cache_key_matches` therefore returns False for every split, and
`load_cached_mu` returns `None` on a corpus that has not changed:

```
$ python train_cte_probe.py --out runs/_verify_cte_probe
  train: cached latents at train_mu.npy are from a different VAE checkpoint
  than ...\runs\vae\vae_best.pt - treating as stale
ml/data/proc/train_mu.npy is missing or was encoded by a different VAE
checkpoint than ...\runs\vae\vae_best.pt -- run train_mdnrnn.py first to
refresh the cache.
```

`train_cte_probe.py` **worked before this change and refuses to run after it.**
`train_controller.py` survives only because its `None` branch re-encodes — it
now does 91,678 VAE forward passes on every run that the cache already answers:

```
$ python train_controller.py --epochs 2 --out runs/_verify_ctrl
  train: cached latents at train_mu.npy are from a different VAE checkpoint ...
no usable latent cache at train_mu.npy - encoding with the frozen VAE...
building RNN states for 66 fit + 12 val episodes...
  fit 77,266 frames, val 14,412 frames (1s)
controller: 578 params (linear on z32 + h256)
  epoch   1  fit 0.08711  val_indomain 0.03229 (unweighted 0.03229)
best val_indomain MSE 0.01926 -> runs\_verify_ctrl\controller_linear_seed0.pt
```

## AO.3 The cache is fine — measured, not assumed

Re-encoded a 4,096-frame random sample of the train split with
`runs/vae/vae_best.pt` and differenced it against the cache. Control arm:
the same VAE with every weight multiplied by 1.01, i.e. the smallest
"different checkpoint" worth worrying about.

| arm | max abs diff | mean abs diff | mean/scale |
|---|---|---|---|
| cuda TF32=on | 2.85e-03 | 2.84e-04 | 7.46e-04 |
| cuda TF32=off | 2.09e-03 | 1.99e-04 | 5.22e-04 |
| cpu fp32 | 2.09e-03 | 1.99e-04 | 5.22e-04 |
| **+1% weights (control)** | 2.42e-01 | 1.95e-02 | **5.12e-02** |

Cached mu scale (mean |mu|) 0.3813. The cache-vs-checkpoint residual is
**100x smaller than a 1% weight change**, and is bit-identical between CPU
fp32 and TF32-off CUDA — so it is float32 accumulation-order noise from the
chunk size used when the cache was written, not a different encoder.
**`train_mu.npy` is the output of `vae_best.pt`. The guard is a false
negative.**

## AO.4 Root cause: the fix does not mirror the thing it cites

`load_cached_mu`'s docstring says it "mirrors the check half of
train_mdnrnn.py:encode_split", and the call-site comments cite
`rollout_eval.py`. `rollout_eval.py:190-203` distinguishes **three** states,
and says why in a comment:

> Missing sidecar => UNVERIFIABLE (caches predating this guard have none);
> present-and-different => WRONG, and we stop.

Missing key warns and continues; mismatched key returns 1. `load_cached_mu`
collapses missing and mismatched into one `None` — deleting exactly the
carve-out `rollout_eval.py` wrote for this corpus. The fix contradicts the
precedent it cites rather than mirroring it.

## AO.5 The other changes in the working tree

Ran or read the rest; none is broken.

- **Split seed from the checkpoint** (`compare_encoders.py`, `probe_cone.py`,
  `train_cte_probe.py`): correct hardening, and a **no-op today** —
  `vae_best.pt`'s `args` is a plain dict with `seed: 0`, the same value the
  removed hardcodes used. It buys nothing now and prevents a silent wrong
  split after any VAE retrain at another seed. `.get` is safe: `args` is a
  dict, not an argparse Namespace.
- **`verify_corpus.py` importing `MAX_MEAN_ABS_CTE`/`MIN_EPISODE_STEPS` from
  `collect_sim_data`** instead of re-declaring them: good — kills a
  keep-in-sync comment. Import resolves; the script then exits 1 on
  `corpus not found: ml\data\sim`, because **the raw episode corpus is not on
  disk** (only `ml/data/proc/`). Pre-existing, unrelated to this change, and
  it means the P2 done-check cannot currently be re-run at all.
- **`eval_in_sim.py`**: `SIZE` now imported from `preprocess` rather than
  re-declared; `--force` guard against silently overwriting `p5_eval.json`;
  `batch_valid` now requires `episodes > 0` (an empty batch used to read as
  valid). All three are right. Not exercised — needs a sim launch.
- **`plan_cem.py`**: CEM candidates clamped to `STEER_LIMIT` instead of
  hardcoded +-1.0. Right, and it changes CEM behaviour if `STEER_LIMIT < 1`.
  Not exercised — needs a sim launch.
- **`episode_writer.py` / `prep_dreamer_corpus.py`**: silent `except OSError:
  pass` on temp-file cleanup now prints. Fine.

## AO.6 Status

Nothing committed. `runs/_verify_cte_probe` and `runs/_verify_ctrl` are
throwaway verification outputs. `ml/runs/controller/history_linear_seed0.json`
is also modified in the tree and is a **result artifact**, not a code fix — it
does not belong in a commit labelled "audit fixes" and needs its own account
of which run produced it before it goes anywhere.

Also corrected: HANDOFF's "19 files, 299 insertions" is stale — the tree holds
**13 files, 161 insertions** (12 of them tracked work plus `.claude/
pm-cadence.json`, a counter file).

# Appendix AP - Option 1 applied: load_cached_mu resolves three states, and every runnable AL-touched reader re-run (2026-09-01, ~15:50 CDT)
Evan picked option 1 from AO. Repaired `splits.load_cached_mu` and re-ran every
reader the AL fixes touched that can run without the simulator.

## AP.1 The repair

`load_cached_mu` now resolves the same THREE states `rollout_eval.py:190`
already decides, instead of collapsing two of them:

| state | before | after |
|---|---|---|
| no `{split}_mu.npy` | `None` | `None` |
| cache, **no sidecar key** | `None` ("stale") | **warn UNVERIFIABLE, return the array** |
| sidecar present, matches | array | array |
| sidecar present, differs | `None` ("stale") | `None` ("stale") |

One file changed (`ml/splits.py`); the three callers are untouched, because
what changed is only *when* `None` is produced, not what `None` means. The
docstring now states the three states and names AO as the reason.

## AP.2 The self-check

`self_check()` gains a four-state assertion over a `tempfile` scratch dir --
no corpus and no real VAE needed, since `encoder_fingerprint` only stats the
file. It asserts missing-cache => None, keyless-cache => usable, matching-key
=> usable, mismatched-key => None.

```
$ python splits.py
  note: train latent cache has no encoder fingerprint - cannot verify it
  matches vae_best.pt; using it anyway. Re-run train_mdnrnn.py to stamp one.
  train: cached latents at train_mu.npy are from a different VAE checkpoint
  than ...\tmpgadg1yti\vae_best.pt - treating as stale
fit=[0, 1, 2, 3, 5, 7, 8, 9, 10, 11, 12, 14, 15]
val=[4, 6, 13]
splits self_check: PASS
```

## AP.3 Every runnable reader, re-run

**`train_cte_probe.py` -- the script AO found broken. Now runs.** R^2 0.957
matches the 0.97 MLP probe of Appendix V.

```
  note: train latent cache has no encoder fingerprint - ... using it anyway.
  epoch  40  val MSE 0.0100  R^2 0.9572
mlp z->cte probe: val MSE 0.0100, R^2 0.9572
```

**`train_controller.py` --epochs 2.** This is the strongest evidence in the
whole exercise: the run now reads the cache, and produces **numbers identical
to the AO run that re-encoded all 91,678 frames from `vae_best.pt`** --
fit 0.08711, val_indomain 0.03229, best 0.01926, to five decimals. Cache and
fresh encode are interchangeable downstream, which is what AO's 100x margin
predicted.

```
  note: train latent cache has no encoder fingerprint - ... using it anyway.
building RNN states for 66 fit + 12 val episodes...
  fit 77,266 frames, val 14,412 frames (1s)
controller: 578 params (linear on z32 + h256)
  epoch   1  fit 0.08711  val_indomain 0.03229 (unweighted 0.03229)
best val_indomain MSE 0.01926 -> runs\_v_ctrl\controller_linear_seed0.pt
```

**`diag_copycat.py`.** Reproduces the banked copycat refutation exactly --
18.23x (Appendix recorded 18.2x) and the h=0 skill of -0.120.

```
controller -> a[t]      (the reported val MSE)                  0.001755   0.993
a[t-1]     -> a[t]      (TRIVIAL COPY BASELINE)                 0.031997   0.873
controller -> a[t-1]    (is it predicting the PREVIOUS action?)  0.030699   0.878
controller(h=0) -> a[t] (serve-time history ablation)           0.282040  -0.120
VERDICT: NOT A COPYCAT on this evidence. ... beats repeat-last-action by 18.23x
```

**`probe_cone.py`** (split seed now from the checkpoint). AUC 0.997, and the
paint-out ablation still returns the CONFOUNDED verdict -- 1% of the pos/neg
gap recovered. The negative stands.

**`compare_encoders.py`** (same change). Both encoders erase the cone, 0/899
cone pixels surviving in each. ConvVAE ratio 4.42x, DreamerV3 3.22x. The M4
stop-sign threat stands.

## AP.4 Two changes that are no-ops today -- stated, not glossed

Measured, not assumed:

- **Split-seed-from-checkpoint** (`compare_encoders.py`, `probe_cone.py`,
  `train_cte_probe.py`): `vae_best.pt`'s `args` is `{'epochs': 40, 'batch':
  256, 'lr': 0.0001, 'beta': 1.0, 'seed': 0, ...}`. `seed: 0` is the value the
  removed hardcodes used, so **behaviour is unchanged today**. It is insurance
  against a silent wrong split after any VAE retrain at another seed.
- **`plan_cem.py` clamping to `STEER_LIMIT`** instead of +-1.0:
  `collect_sim_data.STEER_LIMIT == 1.0`, so **this too changes nothing today**.
  It stops the clamp drifting away from the collector's limit later.

Neither is wrong; neither has yet been shown to do anything. Recorded that way
so a future reader does not mistake them for tested behaviour changes.

## AP.5 What is still NOT verified

- **`eval_in_sim.py` and `plan_cem.py` need a simulator launch.** Not run.
  `eval_in_sim.py --smoke` was attempted and the new `--force` guard **stopped
  it, correctly** -- the default `--out` is `runs/p5_eval`, so the smoke run
  would have overwritten the banked Appendix V artifact. The guard did the job
  it was added for on its first real contact. Its refusal path is therefore
  exercised; its success path is not.
- **`verify_corpus.py` cannot run at all**: the raw episode corpus
  `ml/data/sim` **is not on disk** (only `ml/data/proc/`). The new
  `from collect_sim_data import MAX_MEAN_ABS_CTE, MIN_EPISODE_STEPS` import
  resolves -- the script reaches its own `corpus not found: ml\data\sim` and
  exits 1 -- but the P2 done-check is unrunnable until the raw corpus is
  restored or regenerated. Pre-existing, unrelated to the AL fixes, and it
  means P2's DONE status currently rests on the 2026-08-06 record alone.
- Throwaway verification outputs `runs/_v_cte`, `runs/_v_ctrl`,
  `runs/_v_copycat`, `runs/_v_cone`, `runs/_v_enc` were deleted.

# Appendix AQ - CORRECTION to AP.5: ml/data/sim was never missing - verify_corpus.py's cwd-relative default was, and P2 re-verified PASS (2026-09-01, ~15:55 CDT)
**CORRECTION to AP.5.** AP.5 states "the raw episode corpus `ml/data/sim` **is
not on disk**" and concludes "the P2 done-check is unrunnable until the raw
corpus is restored or regenerated" and "P2's DONE status currently rests on the
2026-08-06 record alone". **All three statements are wrong.** AP is committed
(3f58804) and append-only, so the correction lives here rather than as an edit
to it.

## AQ.1 The corpus was never missing

```
ml/data/sim/train     78 episodes
ml/data/sim/holdout   10 episodes
3.9G  ml/data/sim
```

88 episodes, matching the P2 figure recorded 2026-08-06 exactly. `ml/data/` is
gitignored (`.gitignore:32`, "large and regenerable"), which is why `git
ls-files ml/data` is empty -- that is by design and is not evidence of absence.

## AQ.2 What actually happened

`verify_corpus.py`'s positional default was the **cwd-relative string**
`"ml/data/sim"`:

```python
ap.add_argument("root", nargs="?", default="ml/data/sim")
```

Every reader in AP.3 was run with `cd ml` first, so the default resolved to
`ml/ml/data/sim`, and the script printed its own honest `corpus not found:
ml\data\sim` and exited 1. **I read a path error as a missing 3.9 GB corpus and
wrote it into the record as fact.** The script was right; the invocation and
the inference were both mine.

The general lesson, worth more than the specific bug: `corpus not found` is a
claim about a *path*, not about *disk*. It needed one `ls` before it became a
record entry. It got none.

## AQ.3 P2 re-verified, and it PASSES

Run against the real corpus. This is the first time the P2 done-check has been
executed since 2026-08-06, so P2's DONE status is now independently
re-confirmed rather than record-only -- the opposite of what AP.5 claimed.

```
$ python ml/verify_corpus.py ml/data/sim
holdout  :  10 episodes,   11210 frames, tracks ['donkey-waveshare-v0']
train    :  78 episodes,   91678 frames, tracks ['donkey-generated-roads-v0', 'donkey-generated-track-v0']
  split is disjoint      : no track appears on both sides

total frames: 102888

alignment:
  exact PID identity     : verified on 88/88 episode(s), every action reproduced from log_cte
  image-axis gate        : 88/88 episodes in band (-2, -1), lag distribution {-2: 29, -1: 59}, mode -1 (|r| 0.74-0.96)

P2 CORPUS CHECK: PASS
```

Both gates hold: the ACTION axis (every action reproduced from `log_cte` by
exact PID algebra) and the IMAGE axis (88/88 episodes with pixel-motion lag in
the expected `(-2, -1)` band). Gate 2 is the one that catches an off-by-one
image roll, which gate 1 cannot see -- see the module docstring.

## AQ.4 The one-line defect, fixed

`verify_corpus.py` was the only script in `ml/` whose default path was
cwd-relative; `collect_sim_data.py`, `preprocess.py`, `train_vae.py` and the
rest all resolve from `REPO = Path(__file__).resolve().parent.parent`. Added
`REPO` and made the default absolute, so the P2 done-check no longer depends
on the directory it is launched from.

Verified by running it from `ml/` -- the exact cwd that produced the false
"corpus not found" -- and getting `P2 CORPUS CHECK: PASS`, RC=0.

## AQ.5 Also corrected

AP.5's bullet claiming `verify_corpus.py` "cannot run at all" is void.
The new `from collect_sim_data import MAX_MEAN_ABS_CTE, MIN_EPISODE_STEPS`
import (committed in 3f58804) is now exercised for real, not merely
import-resolved: the thresholds it pulls are what gate the 88-episode
expert-quality check above.

# Appendix AR - Sim camera pose: the FOV trick does not extend to extrinsics; fov proved VERTICAL, pitch measured 16.3 deg down, height NOT identified (2026-09-01, ~16:10 CDT)
HANDOFF's next-action 2 was "identify the sim camera height/pitch/offset by the
same comparison method that pinned fov=90". **The method does not transfer.**
Pitch is now measured; the FOV convention it depends on is now settled
empirically; height and lateral offset are NOT identified, and this entry says
why rather than supplying a number.

## AR.1 Why the FOV trick cannot be reused

`diag_camera_fov.py` worked by sweeping explicit FOVs until one reproduced the
un-configured default frame. Applying that to the extrinsics is blocked by
gym_donkeycar's own contract, `donkey_sim.py:738`:

    set any field to Zero to get the default camera setting

FOV was identifiable because its default (90) is **non-zero**, so an explicit
sweep could land on it. For `offset_x/y/z` and `rot_x/y/z`, **0.0 means "use
the default"** -- asking whether `offset_y=0` reproduces the default is a
tautology, not a measurement. Worse, the fov=90 run itself sent all six
extrinsic keys as 0.0, so it explicitly *held the extrinsics at default* and
yielded no information about them at all.

So the extrinsics had to be attacked geometrically, off frames already on disk.

## AR.2 The FOV convention, settled: it is VERTICAL

The pitch calculation needs the focal length `f`, and `f` depends on whether
the sim's `fov` is the vertical or the horizontal field of view -- a ~30%
difference in `f` (60 px vs 80 px on a 120x160 frame) and therefore a ~4 deg
difference in pitch. Appendix AI **assumed** vertical (that is where its
"~106 deg H / ~118 deg diagonal" came from). It had not been tested.

Decisive test, 3 launches on `donkey-avc-sparkfun-v0` (fixed track, so the
pose is reproducible; `donkey-generated-*` regenerates per launch): hold pose
and `fov=90`, change only `img_h`.

| hypothesis | prediction for the horizon's offset from centre, 160x160 vs 160x120 |
|---|---|
| fov VERTICAL (f tracks height: 60 -> 80 px) | ratio 1.3333 |
| fov HORIZONTAL (f = 80 px either way) | ratio 1.0000 |

Measured, from two independent references in the same frames:

| measure | value | vertical predicts | horizontal predicts |
|---|---|---|---|
| horizon offset ratio | **1.3460** | 1.3333 | 1.0000 |
| horizon->pink-stripe separation ratio | **1.2713** | 1.3333 | 1.0000 |

Both land near 1.33 and nowhere near 1.00. **`fov` is the VERTICAL field of
view**, so f = 60 px at the native 120x160, and AI's 106 deg H / 118 deg
diagonal -- and with them the Camera Module 3 Wide purchase decision -- are
confirmed rather than assumed. Frames in `ml/runs/camera_aspect/`.

## AR.3 A false confirmation, and what it cost

The first pass at AR.2 returned an offset ratio of **0.0867**, matching neither
hypothesis, and the script's own tie-break still printed
`VERDICT: fov is HORIZONTAL` because 0.0867 is nearer 1.0 than 1.333. It was
wrong, and the reason is worth recording.

The horizon detector took the steepest vertical gradient of blue-minus-red.
On `sparkfun_avc` that locks onto a **saturated pink stripe painted on the
ground**, which is a stronger B-R edge than the sky boundary. The giveaway was
geometric: the reported "horizon" (row 77.5) sat **below** a ground stripe
(row 75.5), which is impossible.

**The repeatability check said 0.000 px.** Two independent launches of the same
configuration returned bit-identical horizon rows. That read as confirmation
and was nothing of the sort: the detector failed *deterministically*, so its
failure repeated perfectly. **Repeatability bounds noise; it says nothing about
correctness.** This is the same shape of error as the AO cache guard -- a check
that looked like evidence and was not.

Replacing the rule with a **content** test -- the last row that is still
predominantly sky, requiring pixels to actually BE sky rather than merely to
sit on a strong edge -- fixed it, on the already-saved frames, with no extra
launches. That correction is what produced the AR.2 table.

## AR.4 Pitch, measured

`ml/data/sim/train`, `donkey-generated-roads-v0` only, every 10th frame:

```
$ python ml/diag_camera_pose.py
generated-roads: n=3,187  horizon row 41.974 (sd 0.284, IQR 41.73-42.19)
  cy - r_h = 17.526 px
  pitch DOWN = 16.28 deg (fov vertical, f=60 px -- the measured convention)
  pitch DOWN = 12.36 deg (fov horizontal, f=80 px -- ruled out, kept for the record)
```

**Camera pitch: 16.3 deg DOWN.** The horizon sits at row 41.97 of 120, with a
standard deviation of **0.284 px** across 3,187 frames -- tight, because that
track is an open flat desert with an unobstructed true horizon.

`donkey-generated-track-v0` gives horizon 10.5 with sd 9.34 and is unusable:
it is tree-lined, so no row is ever predominantly sky. Only one of the two
training tracks can answer this question, and the corpus is 51:27 weighted
toward the *other* one.

Two supporting facts that make the number trustworthy:

- **The image centre row is 59.5, confirmed empirically to 0.2 px.** Refitting
  the old `camera_fov_fixed` sweep (warehouse, the run that produced the fov=90
  verdict) to `r_h = cy - k/tan(fov/2)` gives an intercept of **59.295** against
  a geometric prediction of 59.5, with a max residual of **0.351 px** across
  four FOVs. That also proves the sim genuinely applies `fov` as a perspective
  FOV rather than ignoring it.
- That same warehouse run **cannot** give pitch, despite the excellent fit:
  warehouse is indoor and has no horizon, so the feature it locked onto is a
  wall/floor edge at some fixed unknown angle.

## AR.5 Height: NOT identified, and the failure is diagnosed

The intended method is sound on paper and needs no FOV assumption at all. For a
camera at height h pitched down by theta, a ground point at lateral offset X
projects to

    u - cx = (X * cos(theta) / h) * (v - v_h)

in which **f cancels**. The yellow centre line sits at X = C - cte with `cte`
logged per frame in metres, so regressing its column on `cte` at each row gives
`slope(v) = -(cos(theta)/h) * (v - v_h)`: the rate yields h/cos(theta) in
metres, and the zero crossing yields the horizon independently.

It does not work on the corpus as collected. Run on 2,077 near-straight frames
(|steer| < 0.05) of `generated-roads`:

```
weighted fit  slope(v) = 1.39483*v + -317.8315   (resid rms 8.7026, n rows 45)
  -> h / cos(pitch)      = -0.7169  sim length units
  -> horizon row v_h     = 227.864   (sky-boundary measurement: 43.02)
```

A negative height and a horizon 108 rows outside a 120-row image. The model is
being violated, by three confirmed causes:

1. **Left-edge censoring.** The yellow line exits the frame at close rows --
   measured centroids fall to column 13.0 at row 96 and 4.0 at row 104. Those
   are exactly the rows carrying the most signal, and truncation at the border
   compresses their centroid, flattening the slope. Observed slope magnitude
   *decreases* from 216 to 154 across rows 68->108; the model requires it to
   *increase* by a factor of ~2.6.
2. **`cte` barely varies.** Range [-0.160, 0.176] m, sd 0.053 m. The PID holds
   the car centred, so the lateral excitation is tiny.
3. **Heading is coupled to `cte`.** The PID steers *from* `cte`, so heading
   error is a lagged function of it. Heading rotates the line's image position
   in a row-dependent way, and the regression cannot separate the two.

`ml/data/sim_recovery` has cte spanning +-4.2 m (sd 1.474, 28x wider) and would
fix cause 2 -- but it is on `generated-track-v0`, which is tree-shadowed with
dappled light and an occluded horizon, and at cte=4.14 the car is off the road
entirely with no line in frame. Trading cause 2 for a much harder extraction is
not obviously a win, and was not attempted.

**No height number is being reported.** The honest state is that the method is
correct, the data as collected cannot support it, and fixing it means either a
purpose-built collection run (a slow lateral sweep on the clean desert track,
steering decoupled from cte) or a different observable.

## AR.6 What is not identifiable at all

- **`offset_z` (forward)** cannot be recovered from a ground plane by any
  amount of analysis. Sliding the camera along its own optical axis leaves
  every ground-plane image relation unchanged; the shift is absorbed into the
  definition of `cte`.
- **`offset_x` (lateral)** is not separable from the road's own geometry with a
  single line: the yellow line's observed lateral position is (its offset from
  the track reference) minus `cte`, and only the sum is observable. A second
  line does not fix this -- it adds the lane width as another unknown.

## AR.7 What transfers to the physical car

The convention-free, directly actionable spec is **the horizon's image row**,
not an angle. If the real camera is mounted so that the true horizon lands on
**row 42 of a 120-row frame (35% down)** at the matched 90 deg vertical FOV,
the real projection reproduces the training projection in pitch, whatever the
mounting hardware ends up looking like. That is a mount target that can be
checked with a spirit level and one test photo, and it needs no trigonometry
at the bench.

Height remains open, and it is the parameter that most constrains where the
camera can sit on a chassis nobody has built yet -- so this is not currently on
anyone's critical path. It should be settled before the camera mount is
designed, not after.

## AR.8 Artifacts

- `ml/diag_camera_pose.py` -- new. Carries the horizon detector, the pitch
  calculation, the full LIMITATIONS section above, and a `--self-check` that
  runs with no corpus: three synthetic frames with known horizons, an
  all-grey frame that must return NaN rather than 0, **a frame with a bright
  red ground stripe below the true boundary (the sparkfun failure mode, which
  the old gradient rule fails)**, and the two f-convention identities.
  `diag_camera_pose self_check: PASS`.
- `ml/runs/camera_aspect/` -- the three aspect-test frames and their JSON.
- `ml/runs/camera_pose/camera_pose.json` -- the pitch measurement.

---

# Appendix AS - Reference lookup: LEGO Technic rack-and-pinion steering, set 42111 as the donor precedent (2026-09-01, ~17:25 CDT)

No code, CAD, or sim change this entry. Evan asked for a Technic steering
mechanism modelled on Dom Toretto's Dodge Charger, with part numbers, so this
records what was *verified* versus what is still assumption, since the numbers
will be used to order parts later.

## AS.1 What was verified

Official set **42111 Dom's Dodge Charger** (2020, 1,076-1,077 parts) exists and
uses rack-and-pinion steering. Steering-relevant inventory pulled from the
BrickOwl inventory page for 42111 (Rebrickable and Bricker both refused the
fetch, HTTP 403 / menu-only):

- Steering wheel 2741 x1
- Gear Rack 7 - 65127 / 87761 x1
- Technic Hole with 3 Ball Joints - 15460 / 67325 (the modern steering
  knuckle) - quantity was truncated in the fetch, NOT confirmed
- Beam 4 with Ball Joint Socket - 15459 / 31794 x4
- Pin with Ball - 6628 / 66906 x8
- Bevel Gear 12t - 32270 x2; Bevel 20t reinforced - 18575 x3;
  Gear 16t reinforced - 94925 x3; Bevel half 12t - 6589 x5
- Differential casing 62821 x1
- Small shock absorber, extra hard spring - 76537 x4

## AS.2 What is NOT verified

- Which gear meshes the rack (the pinion). Inventory alone cannot say; it needs
  the official instruction PDF or a physical build.
- Whether 42111's front geometry implements true Ackermann. Expectation is that
  it does not - LEGO ball-jointed knuckles with a straight tie rod give
  near-parallel steer unless the steering arms are deliberately angled - but
  that is an expectation, not a measurement.

Both belong in the same bucket as every other untested physical claim in this
project: unverified until built or read off the instructions.

# Appendix AT - Track layout v1: twisty is geometrically impossible at 3x3 m, the bridge cannot be an overpass, and the destinations are landmarks not junctions (2026-09-01, ~20:12 CDT)
Evan asked for the track layout "using the mcp to make a twisty road layout,
at least 5 destinations and 1 bridge". **Three of those four cannot be done as
asked**, each for a measured reason. The layout was built anyway, to the
closest thing the constraints allow, and is verified.

## AT.1 The MCP is not usable, and would not have helped

`3dstreet-mcp` is configured in `.mcp.json` but **no tab is paired**, so the
server exposes zero tools this session. Pairing needs Evan to open
`https://3dstreet.app/#mcp` -- it cannot be done from here.

That is the smaller problem. **Appendix AM already recorded that 3DStreet
cannot draw this track**: it is Streetmix-lineage, its competence is the street
CROSS-SECTION extruded along a line, and its own materials describe linear
streets plus 4-way/T/dead-end intersections with **no curved streets found**.
A twisty road is precisely the thing it does not do. AM's recommendation --
markings and render in 3DStreet, geometry in a dimensioned plan -- is what this
entry follows.

## AT.2 "Twisty" is geometrically impossible at this scale

Twisty means many tight curves. The tightest curve permitted is the frozen
minimum corner radius, so the question is how many minimum-radius features fit
across the floor at all.

| car / lane | R | one 180 deg hairpin spans | fit across 2.80 m | one S-bend spans | fit |
|---|---|---|---|---|---|
| 100 / 200 mm | 500 mm | 1200 mm | 2.33 | 2000 mm | 1.40 |
| 100 / 200 mm | 670 mm | 1540 mm | 1.82 | 2680 mm | 1.04 |
| 130 / 260 mm | 500 mm | 1260 mm | 2.22 | 2000 mm | 1.40 |
| 130 / 260 mm | 670 mm | 1600 mm | 1.75 | 2680 mm | 1.04 |

**Barely two hairpins, or one S-bend, fit across the WHOLE room.** The tightest
legal curve is already about half the floor. There is no arrangement of a 3.0 x
3.0 m space at this radius that reads as twisty.

Worse, the figure-8 itself is near the edge. Bounding box is
(2R + lane) x (d + 2R + lane) with d > 2R required for the crossing tangents to
exist:

| R | lane | bbox | fits 2.80 m? |
|---|---|---|---|
| 500 mm | 260 mm | 1260 x 2360 mm | yes |
| 550 mm | 260 mm | 1360 x 2570 mm | yes |
| 600 mm | 260 mm | 1460 x 2780 mm | yes |
| **670 mm** | **260 mm** | **1600 x 3074 mm** | **NO** |

**At the top of the frozen 500-670 mm band, the mandated figure-8 does not fit
in the room.** That is a live risk on the B3 turning test, not a hypothetical:
if B3 lands at the pessimistic end, either the lane width or the floor has to
give. Worth knowing before B3, not after.

## AT.3 The bridge cannot be an overpass -- three constraints, all binding

An overpass needs the car to climb over itself. Every input below marked EST is
unmeasured, and the car's height and mass are among them.

**Ramp footprint.** Rise = car height + 6 mm deck + 15 mm margin; total bridge
length = 2 x (rise / grade) + a 350 mm clear span over the road below.

| car height | rise | 8% | 10% | 15% | 20% | 25% |
|---|---|---|---|---|---|---|
| 80 mm | 101 mm | 2.88 m | 2.37 m | 1.70 m | 1.36 m | 1.16 m |
| 100 mm | 121 mm | **3.38 m X** | 2.77 m | 1.96 m | 1.56 m | 1.32 m |
| 120 mm | 141 mm | **3.88 m X** | **3.17 m X** | 2.23 m | 1.76 m | 1.48 m |
| 150 mm | 171 mm | **4.62 m X** | **3.77 m X** | 2.63 m | 2.06 m | 1.72 m |

X = does not fit in the 3.0 m floor dimension at all, before one corner is
drawn.

**Torque caps the grade.** Pololu #1093 at 55.9 mN.m stall, 12t->28t, 71% duty
cap, 30% of stall usable = 27.8 mN.m at the wheel = 0.89 N of tractive force:

| mass | max grade (rolling resistance IGNORED) |
|---|---|
| 0.4 kg | 23% |
| 0.6 kg | 15% |
| 0.8 kg | 11% |
| 1.0 kg | 9% |

**The two close on each other.** A realistic 0.6-1.0 kg car is limited to
9-15%, and at 10% a 100 mm car needs 2.77 m of ramp -- 92% of the floor. The
feasible window is a sliver, and the bridge would consume the entire room it is
supposed to sit inside.

**And a grade breaks the projection measured this same day.** The corpus was
collected entirely on flat ground; that is why its horizon row has sd 0.284 px
(Appendix AR). A ramp rotates the car and the camera with it, moving the
horizon by f*tan(grade):

| grade | angle | horizon shift | in training sd |
|---|---|---|---|
| 5% | 2.86 deg | 3.00 px | **11 sd** |
| 10% | 5.71 deg | 6.00 px | **21 sd** |
| 15% | 8.53 deg | 9.00 px | **32 sd** |
| 25% | 14.04 deg | 15.00 px | **53 sd** |

The encoder has never seen a horizon more than about 1 px off row 41.97. Every
frame on a ramp would be far out of distribution in exactly the dimension the
projection is most sensitive to.

**Resolution: a FLAT CAUSEWAY.** Deck at floor level, parapets, a void either
side. It reads unmistakably as a bridge, has zero grade and zero projection
cost, and the parapets add strong near-lane vertical features that the
open-desert training corpus completely lacks -- so it is a perception asset
rather than merely a decoration.

## AT.4 Five destinations, as landmarks and not as routing targets

A behaviourally-cloned lane-follower **has no goal input**. It cannot choose at
a junction. Five spur roads to five destinations would create five junctions
the policy is architecturally unable to handle, and would silently turn M3 from
lane-following into goal-conditioned navigation.

So the five are **landmarks beside the loop**: D1 school, D2 market, D3 depot,
D4 station, D5 park. They cost the policy nothing, give the visual diversity
the corpus lacks, and are localisation targets later. Goal-conditioned routing
is a real and interesting extension, but it is a different task and should be
chosen deliberately, not acquired by accident from a track drawing.

## AT.5 The layout, verified

`cad/track_layout_v1.py` -- parametric, self-checking, writes an SVG plan and a
JSON of every dimension.

```
$ python cad/track_layout_v1.py
track_layout_v1 self_check: PASS
floor            3.000 x 3.000 m  (usable 2.800 m)
car width        130 mm   UNMEASURED, set at B2
lane width       260 mm   = 2.0 x car width
corner radius    550 mm nominal; measured min on path 550 mm   NOT COMMITTED until B3
lobe separation  1440 mm
crossing straights 929 / 929 mm
centreline length 7.227 m
road bounding box 1360 x 2800 mm inside 2800 mm usable
destinations (landmarks beside the loop, NOT spur junctions):
   D1  school     at (   -838,    +656) mm
   D2  market     at (    +16,    +979) mm
   D3  depot      at (   +753,    +348) mm
   D4  station    at (   -234,    -833) mm
   D5  park       at (   +246,    -803) mm
bridge: FLAT causeway, 0% grade, 387 mm deck on a lobe arc, 387 mm clear of the rest of the track
```

The road bbox fills the usable floor exactly in one dimension (2800 of 2800),
because the generator takes the largest lobe separation the floor allows --
longer crossing straights, at the cost of no slack in height.

## AT.6 Two design errors the self-check caught

Both were caught by assertions, not by looking at the picture, and both are now
permanent checks.

1. **Four cusps.** The first cut paired tangent points from *different* tangent
   lines, producing external tangents at x = +-355 mm rather than the internal
   ones through the origin. The path had a heading discontinuity at all four
   tangent points -- jumps of 2.271 and 0.866 rad -- which a pointwise
   minimum-radius check reports as "min radius 1 mm" without saying why. Fixed
   by choosing each arc's sweep direction **by measuring which one exits along
   the departing straight**, rather than hardcoding a sign. `self_check` now
   asserts max heading jump < 0.05 rad directly.
2. **The bridge sat on the crossing.** A deck placed on a crossing straight
   covers the OTHER straight, because the two meet at 80.4 deg. Measured: the
   deck must start 294 mm from the crossing to clear the other road, and the
   tangent point is only 465 mm out, leaving **171 mm of clear run against a
   350 mm deck**. It does not fit. `place_bridge` now searches the whole
   centreline for a run with real clearance and refuses rather than guessing;
   it selects a lobe arc, 387 mm deck with 387 mm clearance. A flat deck on a
   550 mm curve is still a flat deck.

## AT.7 Standing caveat

**No corner geometry is committed.** R = 550 mm is a parameter chosen to fit
the room, inside a frozen band that is arithmetic on an unmeasured 130 mm car
width. Appendix L already ruled that corner tiles must not be cut until B3.
Re-run the generator with the measured numbers the day B2 gives a car width and
B3 gives a turning radius; if B3 lands near 670 mm, AT.2 says the layout has to
change, not just rescale.

## AT.8 A record-invariant repair, made before this entry could be appended

The append refused: `TOC lines (45) != appendix headings (46)`. Cause was NOT
this session. **Appendix AS (LEGO Technic rack-and-pinion steering, 42111),
written at ~17:25 CDT by another session, landed as a heading with no TOC
line** and was still uncommitted in the working tree. That imbalance blocks
every subsequent append, so it had to be repaired first.

Repaired additively: the missing TOC line was generated by calling the tool's
OWN `slugify()` on the existing heading rather than hand-deriving the anchor,
then inserted after AR's line. The AS entry's content was not touched. The
tool then reported the next free letter as AT, so this entry is AT and no
letter was consumed or reused.

# Appendix AU - Scheduled daily-audit: AP/AQ/AR/AS re-verified against disk, 3 findings, and a stale artifact that would mislead the next auditor (2026-09-01, ~20:14 CDT)

**Audit run — 3 findings, top: `ml/runs/camera_aspect/camera_aspect.json` still holds the debunked
pre-fix horizon measurement (offset ratio 0.0867) rather than the corrected 1.3460 that AR.2 reports.**

Cold, read-only, budget-constrained (single agent, no fan-out — the unconstrained fan-out
exhausted the session quota earlier this evening; see the report for why).

## AU.1 Findings
1. `ml/runs/camera_aspect/camera_aspect.json:1` — stale artifact from the debunked gradient
   detector that locked onto the pink stripe; recomputing with the content-based
   `horizon_rows()` (`ml/diag_camera_pose.py:69`) over `a_160x120.npy`/`b_160x160.npy`
   reproduces 1.34597 ≈ 1.3460. **AR.2's claim is TRUE; only the saved JSON is wrong.**
   Fix: regenerate and overwrite that JSON.
2. `docs/Project Record — Full Chronological History.md:5245` — Appendix AS has no TOC line
   (TOC ends at AR) and the entry is uncommitted (39 inserted lines). Fix: add the AS TOC line
   and commit. Also dirty, pre-existing: `.claude/pm-cadence.json`,
   `ml/runs/controller/history_linear_seed0.json`.
3. AR.2's secondary number (horizon→pink-stripe separation ratio 1.2713) has NO artifact on
   disk anywhere and is not listed in AR.8 — prose-only, unverifiable. Not shown false.
   Fix: persist it alongside the primary ratio or strike it.

## AU.2 Verified HEALTHY by re-running, not reading
- `python splits.py` → `splits self_check: PASS`; `load_cached_mu` (`ml/splits.py:63-92`)
  really does resolve the same three states `rollout_eval.py:190` decides.
- `train_cte_probe.py` re-run to a throwaway out-dir → `val MSE 0.0100, R^2 0.9572`,
  matching AP.3 to four decimals. A real re-run, not a copy of prose.
- AQ confirmed: `ml/verify_corpus.py:392` default is now absolute (`REPO/ml/data/sim`).
  Re-run from inside `ml/` — the exact cwd that caused the original false failure — gives
  `total frames: 102888` / `P2 CORPUS CHECK: PASS`, RC=0.
- `python diag_camera_pose.py --self-check` → PASS. `camera_pose.json` matches AR.4 exactly
  (pitch 16.28°, n=3187, sd 0.2835); `fov_is_vertical=True` at `diag_camera_pose.py:96`.
- **Height: no artifact and no committed code produces a height number.** "NOT identified"
  holds — nothing was smuggled in.
- AS's LEGO 42111 citation is real, including part numbers 65127/87761 and 62821. The entry
  honestly admits its failed fetches. **0 fabrications detected across all four appendices.**

## AU.3 Not checked
Three of AP.3's five claimed reader re-runs (`diag_copycat`, `probe_cone`,
`compare_encoders`/`train_controller`) were not re-executed — GPU/VAE-heavy, dropped under the
tool budget after 2/5 reproduced exactly. AR.3's HTTP 403 claim is third-party history,
unverifiable from here.

# Appendix AV - Record letter-collision race repaired, and the AU audit's two findings against AR's artifacts fixed (2026-09-01, ~20:18 CDT)
Two things happened while AT was being written: a **letter collision** with a
concurrent writer, and an **audit (AU) that found a real defect in AR's
artifacts**. Both are resolved here.

## AV.1 The record has a concurrent-write race, and it is not a one-off

Appending AT was refused with `TOC lines (45) != appendix headings (46)`.
Then, after that was repaired and AT landed, the commit was refused again with
`duplicate Appendix AT`. Two separate collisions in six minutes:

| entry | writer | time | defect |
|---|---|---|---|
| AS | another session (LEGO Technic 42111 steering lookup) | ~17:25 CDT | heading written, **no TOC line** |
| AT | this session (track layout) | ~20:12 CDT | fine |
| AT (dup) | scheduled daily-audit | ~20:14 CDT | heading written, **no TOC line**, **letter already taken** |

**Both foreign writers omitted the TOC line, and one of them also read the same
"next free letter" this session had just taken.** The `--next-letter` lookup and
the append are not atomic, so two writers two minutes apart can both be told
"AT". The pre-commit hook catches it, which is why nothing corrupt was
committed -- but it catches it at commit time, after the work is done.

**Repairs, both additive, neither touching a foreign entry's content:**

- AS's missing TOC line was regenerated by calling the tool's own `slugify()`
  on the existing heading rather than hand-deriving an anchor, and inserted
  after AR's.
- The audit's entry was renumbered **AT -> AU**, because its 20:14 timestamp
  is later than this session's 20:12, and its `## AT.x` subsection headings
  were renumbered to match. Its TOC line was generated the same way. Its prose
  is untouched.

This is worth fixing at the source rather than repairing after the fact: a
scheduled task that writes the record needs to take the same lock an
interactive session does, or to write its TOC line in the same commit as its
heading. Flagged, not fixed -- the scheduled task's code was not touched.

## AV.2 The audit was right about AR's artifacts

Appendix AU raised three findings. Two are against work committed earlier
today, and both are real.

**AU finding 1 -- a stale artifact that contradicts the entry citing it.**
`ml/runs/camera_aspect/camera_aspect.json` still held the **debunked 0.0867**
offset ratio, because it was written by the gradient horizon detector before
AR.3 established that detector fails on `sparkfun_avc`'s pink stripe. AR.2
reports 1.3460 in prose; the committed JSON said 0.0867. The audit
independently recomputed 1.34597 from the saved frames and confirmed **AR.2's
claim is true and only the file was wrong** -- but a file that contradicts the
record is exactly what misleads the next reader, and it was committed in
410dd62 as supporting evidence.

**AU finding 3 -- a prose-only number.** AR.2's second, independent ratio
(horizon-to-pink-stripe separation, 1.2713) had **no artifact anywhere on
disk** and was not listed in AR.8. Not shown false, but unverifiable from the
repo. That is the weaker half of the fov-convention argument being
unreproducible.

**Both fixed by making the measurement reproducible rather than by editing the
JSON.** `ml/diag_camera_pose.py` gains `pink_stripe_row()`, `aspect_ratios()`
and a `--recompute-aspect` mode that re-derives every number from the saved
frames with the content-based detector and rewrites the file:

```
$ python ml/diag_camera_pose.py --recompute-aspect
a_160x120        H=120  horizon  35.643  pink  57.763  offset  23.857
b_160x160        H=160  horizon  47.389  pink  75.510  offset  32.111
c_160x120_rep    H=120  horizon  35.643  pink  57.763  offset  23.857

repeatability            0.000 px
offset ratio b/a         1.3460
stripe separation ratio  1.2713
  predicted VERTICAL     1.3333
  predicted HORIZONTAL   1.0000
VERDICT: fov is VERTICAL
```

Both ratios now live in `camera_aspect.json`, both are regenerable from the
frames by one command, and the file carries a note saying why it was rewritten.
`self_check` gains an assertion on `pink_stripe_row` against a synthetic band,
so the second reference cannot silently rot either.

**AU finding 2** (AS's missing TOC line, entry uncommitted) is resolved by
AV.1. The two dirty files it also lists -- `.claude/pm-cadence.json` and
`ml/runs/controller/history_linear_seed0.json` -- are known: the first is a
counter, and the second is deliberately held out of every commit this session
because it is a result artifact with no account of which run produced it
(AO.6).

## AV.3 What this says about the day's work

AR.3 already recorded that a repeatability check of 0.000 px was a false
confirmation of a broken detector. AU then found that the same broken
detector's output had been **committed as an artifact** alongside the entry
that debunks it. The lesson generalises past this one file: **fixing the
measurement in prose does not fix the artifacts the earlier measurement
already wrote.** When a method is retracted, every file that method produced
has to be regenerated or deleted, and neither AR.8's artifact list nor the
commit caught it. The cold audit did.

# Appendix AW - CORRECTION to AV.1: the append script was never the race; the daily-audit prompt never named it. Prompt fixed and a write-time guard added (2026-09-01, ~20:36 CDT)
AV flagged the record-corruption race and explicitly left it unfixed
("Flagged, not fixed -- the scheduled task's code was not touched"). Evan asked
for the source fix. Investigating it showed **AV named the wrong cause**, so
that correction comes first.

## AW.1 CORRECTION to AV.1: the append script was never at fault

AV.1 states:

> "The `--next-letter` lookup and the append are not atomic, so two writers two
> minutes apart can both be told 'AT'."

**That is wrong.** `append-record-entry.js:278-296` already takes an **O_EXCL
lockfile** around the whole read-modify-write and publishes by **temp-file +
rename**. Its own header comment records why, and it is not theoretical: the
previous `writeFileSync -> verify -> roll back` shape was measured destroying
records, "3 of 5 trials at 433KB losing up to 146 of 164 appendices, 10/10 at
1MB", and the rollback itself "WAS the corruption". The tool is sound, and its
canary passes 45/45 untouched.

**The real cause: neither incident used the script at all.** The tool always
writes the heading and the TOC line together, so an entry with a heading and no
TOC line is proof it was hand-spliced. Both AS and AU were hand-spliced, and a
hand-splice takes no lock and derives its own letter — which is how AU landed
on a letter this session had already taken two minutes earlier.

AV's diagnosis pointed at the one component that had already been hardened
against exactly this, and away from the instruction gap that actually caused
it. Recorded here rather than edited into AV, which is committed and
append-only.

## AW.2 The instruction gap, found

`~/.claude/scheduled-tasks/daily-audit/SKILL.md:74-76`, verbatim before this
change:

> CONSTRAINTS — READ-ONLY: no code edits, no fixes applied, no commits, no
> HANDOFF edits. ONE exception: after each project's audit, append one dated
> record entry ("Audit run — N findings, top: <item>") so future sweeps can
> detect it ran.

"Append one dated record entry" and nothing else. It never names the script,
the TOC line, or the lock. The "APPEND WITH THE SCRIPT, never by hand" rule
lives in `~/.claude/skills/project-memory/SKILL.md:128-147`, and the audit run
has no reason to load it -- its prompt invokes `/audit` and `/landing-check`,
never `/project-memory`. Worse, the task's own STEP 1 tells it to READ the
record, so it sees `# Appendix X` headings and imitates them. Heading only.

The audit skills themselves (`audit/`, `audit-code/`, `audit-docs/`) contain no
record-writing instruction at all, so nothing else could have redirected it.

**And the project's own `CLAUDE.md:9-11` does not close the gap either** -- it
says entries are "`# Appendix <X>` headings + TOC line", which describes the
FORMAT and still points at no tool. A model following it faithfully still
hand-writes.

## AW.3 Why fixing only the prompt was not enough

Appendix AS came from an **ordinary interactive session** doing a LEGO Technic
lookup, not from the audit. Fixing the daily-audit prompt would not have
prevented it, and would not prevent the next skill or task that grows a reason
to append. Evan chose prompt + guard.

## AW.4 What was changed

Three files, all under `C:\Users\evan.EVANFREDY\.claude\` -- **outside this
repo, and `~/.claude` is not a git repository, so none of this is versioned.**
Only this entry is committed here.

1. **`scheduled-tasks/daily-audit/SKILL.md`** -- the bare instruction now
   carries the full script invocation, plus why: that an entry is a heading AND
   a TOC line written together, that writing the heading alone blocks every
   later append until a human repairs it, and that picking the letter yourself
   races other sessions. It names both 2026-09-01 incidents.

2. **`skills/project-memory/hooks/pretooluse-record-guard.js`** -- NEW. A
   PreToolUse hook on `Edit|Write` that DENIES a direct write to any
   `...Full Chronological History.md`, with a message naming the exact script
   invocation. Mirrors `pretooluse-commit-gate.js`'s contract exactly: reads
   the event from fd 0, **always exits 0**, expresses the block as
   `permissionDecision:"deny"` in JSON rather than by crashing.

   Deliberate carve-outs, each because denying would be worse than allowing:
   a record that does not exist yet (BOOTSTRAP legitimately creates it with
   `Write`); `record_<date>.md` of the `## YYYY-MM-DD` convention, which the
   script explicitly REFUSES to handle, so a deny would leave no legal path;
   and unparseable/absent input, which allows LOUDLY because denying there
   would wedge every Edit and Write in the session. Once the target is KNOWN
   to be a record, every error path denies -- a false block is recoverable, a
   false allow re-opens the corruption.

   Repair hatch `PM_RECORD_UNLOCK=1`, which matters because repairing an
   already-broken record needs a hand edit. It must be set in the environment
   that LAUNCHED Claude Code; a model running `export` in a Bash call cannot
   reach the hook's process, so the model cannot unlock itself.

3. **`settings.json`** -- registered as a new `PreToolUse` element with matcher
   `Edit|Write` (there was none before; the existing `Edit|Write` entry is
   PostToolUse).

## AW.5 Verified

```
$ node ~/.claude/skills/project-memory/hooks/pretooluse-record-guard.js --canary
CANARY PASS 23/23
```

23 cases: deny on Edit and Write, on backslash / lowercase / quoted / `/d/...`
Git-Bash spellings and on `notebook_path`; the deny text contains the script,
all four flags, the hand-splice line and the hatch; allow for another `.md`, a
code file, the `.html` twin, a `.bak`, and a not-yet-existing record; warn for
`record_<date>.md`, `PM_RECORD_UNLOCK=1`, malformed stdin and empty stdin; and
every path exits 0.

Against the real record and a real non-record:

```
$ ... | node pretooluse-record-guard.js      # the project's own record
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny",...}}
exit=0
$ ... | node pretooluse-record-guard.js      # HANDOFF.md
exit=0   (empty stdout - allowed)
```

`append-record-entry.js --canary` still **PASS 45/45**: the script was not
touched, and it is spawned via Bash so the `Edit|Write` matcher never fires on
it. This entry was appended with that script, which is itself the end-to-end
proof that the sanctioned path still works.

## AW.6 The canary caught a bug in the guard

First run was **22/23**. The failing case was `quoted/padded path -> deny`, and
the cause was real rather than cosmetic: the name match ran on a cleaned path
(trimmed, quotes stripped) while `existsSync` ran on the RAW string with its
quotes still attached. So the guard's matcher said "this is a record" and its
stat said "this file does not exist", and the not-yet-exists carve-out let the
write through. **A guard whose two halves disagree about which file they are
looking at fails open on exactly the input designed to slip past it.** Fixed by
routing both through one `cleanPath()`; the comment in the source says why they
must never diverge again.

## AW.7 Not fixed, and stated

- **The guard cannot be confirmed live this session.** Hooks are read at
  startup, so it will not fire until Claude Code is restarted. What is proven
  is the hook's own behaviour against real payloads, not that the harness is
  calling it.
- **Delete-then-Write defeats the `existsSync` carve-out.** `pre-commit-record`
  still fails closed at commit time, which is the remaining net.
- **A record under a different filename is not matched** -- the same blind spot
  `pre-commit-record` already has, since both key on the naming convention.
- **Editing a typo inside a prior entry is now blocked.** That enforces what
  `project-memory/SKILL.md` already stated ("APPEND ONLY - corrections are NEW
  entries"), but it is new friction people will feel.
- **`~/.claude` is not a git repository.** The prompt fix, the hook and the
  settings change are unversioned; if that directory is lost they go with it.

# Appendix AX - Track v2: a 3x3 city grid that fits only at R=500mm, the sim cannot rehearse it, and the 225-panel floor is refused (my filament figure was 2.7x too high) (2026-09-01, ~21:00 CDT)
Evan asked three things: can the sim run the generated landscapes, make track
v2 more like a real city, and is a 225-panel 3D-printed floor a good idea. One
"no", one built, one refused with numbers -- and Evan caught an error in mine.

## AX.1 The sim CANNOT rehearse a custom track. No road-definition message exists

`gym_donkeycar/envs/donkey_sim.py` sends exactly ten message types:
`cam_config`, `cam_config_b`, `car_config`, `control`, `exit_scene`,
`get_scene_names`, `lidar_config`, `load_scene`, `racer_info`, `reset_car`.
**There is no way to send a road.** `load_scene` selects from 11 prebuilt Unity
scenes:

    avc-sparkfun, circuit-launch-track, generated-roads, generated-track,
    minimonaco-track, mountain-track, roboracingleague-track,
    thunderhill-track, warehouse, warren-track, waveshare

A custom track means authoring a Unity scene and rebuilding the sim binary --
its own project. And the two "generated" scenes are not authorable either: they
regenerate randomly per launch, which is the 4.4x measurement swing of AI.

**This costs less than it first appears.** `PRD_ROADMAP.md:306-310` has M3
collecting **10-20 laps on the real track**, and M4 consuming the car's own
logs. The sim corpus was never the training set for the physical car. What must
still match is the CONTROL LOOP and CAMERA -- 20.00 Hz, 1.401 m/s,
120x160 -> 64x64, fov=90 VERTICAL, horizon on row 42 (AR) -- not the scenery.
What is genuinely lost: no sim rehearsal of the city, and M5 (sim-RL) stays on
stock tracks. M5 is already marked optional and parallel.

## AX.2 A city grid fits at exactly ONE point in the frozen radius band

Streets must be spaced at least `2R + lane` so consecutive 90-degree turns do
not overlap, and `span = (S-1) * pitch + lane` must fit 2800 mm of usable floor:

| R | pitch | 3x3 span | fits? |
|---|---|---|---|
| **500 mm** | **1260 mm** | **2780 mm** | **yes -- 20 mm spare** |
| 550 mm | 1360 mm | 2980 mm | no |
| 600 mm | 1460 mm | 3180 mm | no |
| 670 mm | 1600 mm | 3460 mm | no |

Identical at 100 mm and 130 mm car width -- the radius dominates, not the lane.

**And there is no smaller-city fallback.** A 2x2 grid has the SPACE at those
radii but cannot carry the route at all: a figure-8 needs a centre street to
cross on plus outer streets both sides, so three per axis. Two streets admit
only a perimeter loop -- every turn the same way, the oval `gotchas.md` bans
because it teaches "always steer left". **So B3 above 500 mm does not shrink the
city, it deletes it**, and the fallback is v1's non-grid figure-8. The generator
refuses rather than emitting something undrivable.

## AX.3 The route: a figure-8 THROUGH the centre intersection

Three LEFT turns round the top-left block, straight through the centre, three
RIGHT turns round the bottom-right block, straight through again. One closed
circuit, 8.79 m, balanced turns, and a genuine level crossing. It drives 7 of
the 9 intersections; the other two are city dressing.

**Behavioural cloning can drive intersections, and the honest caveat matters.**
A cloned lane-follower has no goal input and cannot CHOOSE at a junction. It
does not have to: M3 collects 10-20 laps of the SAME route, so the policy learns
"turn right here" from the visuals. That is **route memorisation, not
navigation** -- a different route means retraining. It is still a better result
than an oval, and the write-up must say which of the two it is.

## AX.4 The 225-panel floor: refused, and my first numbers were WRONG

Proposal was 15x15 = 225 panels of 200 mm with dovetails, on a 256 mm bed.

**Evan caught the error.** My first table said 33.5 kg / $670 at 3 mm. That
assumed **100% infill**. A real panel -- ~0.8 mm of solid skins plus ~15% sparse
-- is about 56 g, not 149 g, so **~12.6 kg**, which is what Evan said ("even if
I make them only 3mm thick its 12kg"). My figure was **2.7x too high**. The
corrected cost is roughly $250, not $670. Still the wrong trade, but the
argument has to rest on the right number.

What stands after the correction:

- **~12.6 kg** of filament at 3 mm, against a whole-project BOM of ~$180.
- **169-900 hours** of printing at 45-240 min/panel: 7 to 37 days nonstop.
- **225 separate print jobs.** The bed is 256 mm, so one 200 mm panel fits but
  two do not (400 > 256) -- every panel is its own job with a hand bed-clear,
  before dovetails add to the footprint.
- **28 seam lines** (14 each way) across the floor. At 120x160 the camera reads
  high-contrast straight edges in exactly the region the lane-follower uses,
  and the corpus is seamless.
- **Warping.** 200 x 200 mm at 2-3 mm is the textbook PLA warp case: large
  area, almost no height to resist it. Any panel-to-panel lip is both a bump
  and a visual edge.
- **Tolerance stack** across 15 dovetails: 0.77 mm random-walk, 3.0 mm worst
  case at +-0.2 mm per joint.

`gotchas.md:79-83` had already settled this on 2026-08-05 -- markings not
surface -- and explicitly warns "Don't let a future session 'improve' this back
to printed tiles."

**Evan's call: HYBRID.** Print only the geometry that must be exact.

## AX.5 The hybrid print plan

| element | length | disposition |
|---|---|---|
| corner arcs (6 turns) | 6.28 m | **printed tiles** |
| intersection boxes (9) | 9.36 m | **printed tiles** |
| straight street lines | 33.36 m | tape or paint on the board |

**79 tiles at 200 mm, ~970 g of filament.** For contrast: printing every line
would be ~3,038 g, and the 225-panel floor ~12,600 g.

Note that `gotchas.md`'s "~0.15 kg for markings" does NOT carry over -- that
figure was for a MINIMUM LOOP, not 50 m of city-grid lines. The honest hybrid
number is ~1 kg, not 0.15 kg.

## AX.6 Three real errors the self-check caught

All three were caught by assertions, not by looking at the render.

1. **Phantom cusps.** Zero-length segments at every arc/straight junction: the
   straight's endpoints duplicated the neighbouring arcs' vertices, and
   `arctan2(0, 0)` fabricates a heading of 0 there, which reads as a **pi jump**
   in a path that is actually smooth. Slice both ends, not just the leading one.
2. **The two lobes never touched.** The first design was two rounded rectangles
   on diagonally opposite blocks, assumed to meet at the shared block corner.
   They do not -- rounding pulls each path `R*(sqrt(2)-1)` = **207 mm** clear of
   the corner. It was **two separate loops with no way to drive between them**,
   and it looked plausible in the summary line. Fixed by building the route as
   a rounded polyline that passes STRAIGHT THROUGH the centre intersection;
   self-check 6 now asserts the route reaches the origin on two perpendicular
   headings.
3. **An off-grid fallback.** With `--streets 2` the route still ran to
   `+-pitch` while the grid only had streets at `-pitch` and `0` -- a path not
   on any street, which printed a clean-looking summary. Self-check 6b now
   asserts every route vertex lies on a real street, and 6c asserts a 2x2 grid
   refuses outright.

## AX.7 Status and what is still not committed

`cad/track_layout_v2.py` (parametric, self-checking), `track_layout_v2.svg`,
`track_layout_v2.json`. v1 is NOT superseded -- it is the documented fallback if
B3 puts the radius above 500 mm.

**No geometry is committed.** R = 500 mm is a parameter at the optimistic end of
a frozen band that is itself arithmetic on an unmeasured 130 mm car width.
Appendix L still rules that corner tiles must not be cut until B3. The 20 mm of
spare floor is the whole margin, so B2's measured car width can also break it:
every 10 mm of extra car width costs 20 mm of lane and 40 mm of span.

# Appendix AY - CORRECTION to AX.2: the street pitch never needed a lane term, so the city fits at R=500/550/600; v2 shrunk; lighting spec settles the PCA9685 (2026-09-01, ~21:06 CDT)
Evan: the loop can be smaller; the bridge and 5 destinations belong to the FINAL
track version, not v2; stop signs only, never traffic lights; and the car should
have headlights, tail lights, daytime running lights and turn signals.

## AY.1 CORRECTION to AX.2: the street pitch was over-constrained by one lane width

AX.2 claimed a 3x3 city grid "fits at exactly ONE point in the frozen radius
band". **That is wrong, and it was my arithmetic, not the geometry.**

`track_layout_v2.py` used `pitch = 2R + lane`. Deriving it instead of assuming
it: driving east and turning north, the arc is tangent to both street
centrelines and consumes R **before** the corner and R **after** it, so two
consecutive corners a pitch apart need only

    pitch >= 2R

The lane width is **not** part of that constraint. Parallel streets need
`pitch >= lane` merely so their surfaces do not overlap, and 2R (>= 1000 mm)
already dwarfs lane (260 mm). The `+ lane` term inflated every pitch by 260 mm
and every 3x3 span by 520 mm.

Corrected, with `pitch = 2R + straight`:

| R | max straight that fits | pitch | span | vs AX.2's claim |
|---|---|---|---|---|
| 500 mm | 200 mm (capped) | 1200 mm | **2660 mm, 140 mm spare** | AX.2 said 2780 mm |
| 550 mm | 100 mm | 1200 mm | **2800 mm, fits** | AX.2 said **NO** |
| 600 mm | 70 mm | 1270 mm | **2800 mm, fits** | AX.2 said **NO** |
| 670 mm | — | 1340 mm | 2940 mm, does not fit | AX.2 said NO (correct) |

**So B3 only deletes the city at the very top of the frozen band, not across
three quarters of it.** The layout is far less at-risk than AX.2 recorded. The
"no smaller-city fallback" finding still stands: a 2x2 grid cannot carry a
figure-8, so R = 670 mm still means falling back to v1.

## AY.2 Smaller, as asked

Evan: "the loop can be smaller, smaller is probably better." Implemented as
`best_straight()`: take the largest straight run between corners that fits, up
to a 200 mm cap, rather than spending the whole floor. At R = 500 mm that leaves
**140 mm spare** instead of 20 mm.

That margin is the defence against the TWO unmeasured numbers, not one. B3 sets
the radius; **B2 sets the car width, and every 10 mm of measured car width costs
20 mm of lane and 40 mm of span.** A layout with 20 mm of slack was one
measurement away from dead in either direction.

```
$ python cad/track_layout_v2.py
street pitch    1200 mm  (straight between corners 200 mm)
grid            3x3 streets, 4 blocks, 9 intersections
span            2660 mm of 2800 usable -> 140 mm SPARE
driven route    figure-8 through the centre intersection, 8.31 m, 3 lefts + 3 rights (balanced)
```

A self-check that asserted `span > 2.7` had to be **inverted**: it encoded the
over-constrained pitch and was asserting the loop was BIG. It is replaced by a
geometric floor (the grid must not collapse below tangent corners) plus a check
that R = 500 mm leaves >= 100 mm spare. A second new check pins the pitch
formula directly -- `grid_pitch` must be unchanged by the lane argument, which
is the exact error above.

Also corrected in passing: a "smaller is better" assertion I wrote claiming a
bigger radius must not give a bigger loop. **That is false physics** -- a bigger
turning circle forces a bigger loop, and at R = 600 mm the straight is already
squeezed to 70 mm. The real property, now asserted, is that the cap binds at the
small end so margin is left rather than spent.

## AY.3 Bridge and destinations move to the final version

Evan scoped these to the final track. v2 carries neither, which is why it is
just streets. **v1's work is not wasted** -- `cad/track_layout_v1.py` holds the
verified flat-causeway bridge (387 mm deck, 387 mm clearance) and the 5-landmark
placement, and both are parametric, so they port to the final layout once the
radius is measured. The reasoning behind them stands unchanged: the bridge
cannot be an overpass (torque caps the grade at 9-15%, a 10% ramp eats 2.77 m of
a 3 m floor, and a 10% grade moves the horizon 21 sd out of distribution --
AT.3), and destinations are landmarks rather than spur junctions.

## AY.4 Stop signs only, no traffic lights -- already the plan, and for a reason

Confirmed correct against `gotchas.md:97-103`, which records it as a FEATURE:

> A stop sign is provably unlearnable by plain BC. Stopped at the line the image
> is identical whether to wait or go, so the action depends on history, which
> pi(action|image) cannot express (frame-stacking gives ~0.2 s at 20 Hz; a stop
> is 2-3 s). This is a FEATURE of the plan -- it is the M4 world-model showcase,
> since the RSSM/MDN-RNN has recurrent state. **Traffic lights are the opposite:
> memoryless-learnable (state is visible in the frame) but need hardware.**

So a traffic light would be both more hardware AND a weaker demonstration. The
sign must also stay relocatable (Appendix Y.3) or position alone predicts it.

## AY.5 Lighting: `docs/LIGHTING_SPEC.md`, and it settles an open purchase decision

Written as a spec; nothing ordered, nothing wired.

**What the camera sees is what decides the risk.** The camera faces forward, so
tail lights and rear indicators are never in frame -- pure realism, zero ML
cost, build them freely. **Only the headlight beam matters**, because it lands on
the road ahead.

**The PCA9685 decision is now settled.** Lights need 4 more channels (headlight,
tail, left, right), two of them PWM for the dimmed daytime running mode, on top
of the existing 1 servo PWM + 2 motor PWM/DIR. A PCA9685 is a 16-channel I2C LED
controller costing 2 pins, designed for exactly this. Straight-to-GPIO needs 4
more pins and has no hardware PWM to spare. The portability argument (DonkeyCar's
`pins.py` has only three PWM backends; straight-to-GPIO locks the project to a
Pi) already leaned this way; capacity settles it. **This closes a
BLOCKED-ON-EVAN item rather than adding one.**

Power: ~8 LEDs x 20 mA = ~160 mA EST, off the **LM2596 5 V rail** that already
feeds the servo -- never off the Pi, whose 5 V/3 A bank has a 600 mA peripheral
cap against a measured 1.40 A CNN draw.

**The headlight trap.** `gotchas.md` says to vary lighting across sessions on
purpose. A headlight beam is NOT that kind of variation: ambient light is
uncorrelated with the car's state, but the beam is fixed to the car and lands in
the same image region every frame. Switching between full beam and the dimmed
daytime mode creates **two visual domains the policy cannot tell apart**, because
nothing in the input says which is active. Collecting some laps in each does the
opposite of domain randomisation -- it injects a hidden variable correlated with
nothing. **Rule: lock ONE lighting mode across the whole dataset and deployment,
exactly as the camera pitch is locked**, or log the mode as an input and say so.

**Turn signals are a policy OUTPUT, and this is the genuinely interesting part.**
The policy gains a third head: a 3-state indicator (off/left/right); the blink
cadence is firmware. Unlike the stop sign, this **is** learnable by plain BC --
on a memorised fixed route the correct state is a function of where the car is,
which is visible in the frame, the same reason `gotchas.md` calls traffic lights
memoryless-learnable.

The prerequisite is real and has a deadline: **M2's logger must record indicator
state per frame before the M3 collection run.** 10-20 laps recorded without
indicator labels cannot be relabelled honestly. If that change does not land in
time, drive the indicators from a rule on predicted steering and **say in the
write-up that they are rule-driven, not learned.** Both are defensible; passing
a rule off as learned is not.

## AY.6 Open

- The PCA9685, LEDs, resistors and wire are **not in `docs/BOM.md`**, and adding
  them moves the ~$178-181 total. BLOCKED-ON-EVAN with the rest of the order.
- Whether indicators are a learned head depends on the M2 logger change landing
  before M3 data collection.
- Headlight position relative to the camera decides where the beam falls in
  frame, which per AY.5 is a dataset-defining choice, not styling -- and it is
  downstream of a chassis nobody has built.
- Still no committed geometry. R = 500 mm remains a parameter; B2 and B3 both
  still gate it.

# Appendix AZ - PCA9685 and lighting added to the BOM: the $200 ceiling is breached on every path, and the wiring rule was already self-contradictory (2026-09-01, ~21:39 CDT)
Evan: add the PCA9685 and LEDs to the BOM, then plan the next steps. Two
decisions taken with him first: **all PWM moves to the PCA9685** (lights, servo
AND motor), and **one order** rather than a deferred phase two.

## AZ.1 BOM rows 17-20, and the ceiling is now breached on every path

New `**Lighting + I/O**` category, matching the file's existing format (bold
prices, bare vendor domains, quantity folded into the item name, status markers
inline):

| # | item | price |
|---|---|---|
| 17 | PCA9685 16-ch I2C PWM/LED driver | ~$6-15 |
| 18 | 8x 3mm LEDs (2 white, 2 red, 4 amber) | ~$1.50-3 |
| 19 | LED series resistors | ~$1-2 |
| 20 | JST/Dupont jumpers + I2C wire | ~$2-4 |

**Totals recomputed from the rows, not carried forward.** Rows 1-16 sum to
**$221.82-$224.82**, which matches the file's own prose exactly -- so the
apparent conflict between the `TOTAL` row (≈$222-225) and the "≈$237-250"
elsewhere was never a conflict: **the TOTAL row is pre-shipping and the other
figure was with-shipping.** I had flagged that as an inconsistency while
planning; it was not one, and the correction note in the BOM says so.

New total: **$232.32-$248.82 before shipping, ≈$247-274 with the $15-25
estimate.**

**The finding that matters: the $200 ceiling is breached on EVERY path now.**
Swapping the Pi 5 4GB for the 2GB at $65 was the move that previously restored
it; with lighting it lands at **$187-204 before shipping, ≈$202-229 with**. So
the ceiling is no longer recoverable by that swap. Evan decides whether the
ceiling moves or the lighting waits. Nothing is ordered.

## AZ.2 The wiring rule was already self-contradictory, and this says so

`docs/BOM.md` carried a paragraph headed **"The one rule that matters"** stating
that the Pi and motor pack share *"ground only ... Nothing else crosses between
them"* -- and then, in the same paragraph, that the ground *"reference is
required for the PWM/direction logic"*. Those cannot both be true: PWM and
direction wires were crossing all along.

So adding I2C did not break a clean rule. **It exposed a loose one.** The
amended rule states the invariant that was always actually meant:

> **No power path crosses between the Pi and the motor pack.** What crosses is
> signal and reference only -- ground, SDA, SCL, the PCA9685's 3.3V logic
> supply, and the TB6612's two direction lines.

The old wording is quoted in place with a dated note rather than deleted, per
this file's own convention (it already flags its own wrong date at lines 42-44
instead of fixing it).

The diagram now shows the PCA9685 with its **V+ on the LM2596 rail** (so ~160 mA
of LEDs never touches the Pi's 5V/3A bank and its 600 mA peripheral cap) and its
**VCC referenced to the Pi at 3.3V** so I2C levels match -- two different pins
that must not be bridged -- plus a channel map: ch0 motor PWM, ch1 servo, ch2-5
lights. **6 of 16 channels.**

**The TB6612's two direction pins stay on GPIO.** DonkeyCar's PCA9685 backend
drives PWM, not direction logic, so moving them needs custom code. Recorded
rather than implying actuation became 100% I2C.

## AZ.3 Power headroom: comfortable, and explicitly unproven

`docs/research/2026-07-23_power-system.md` justifies the LM2596 **solely by the
servo's 700 mA peak**, and elsewhere says a bare LM2596 "won't honestly deliver
3 A". Lights add ~160 mA EST, giving **~860 mA peak** on that rail. That is
comfortable against the 700 mA precedent but **the brief states no measured
module ceiling**, so it is recorded as unverified above ~1 A rather than as
proven headroom. Pack side gains ~110 mA against a documented 3.92 A total --
untroubling. The power brief is closed-world ("Nothing has been built or
measured") and never anticipated additional 5V loads.

## AZ.4 PRD: appended, never rewritten

Per the roadmap's mutability rule (ADD by appending, REMOVE by dated
strikethrough, PIVOT by forking):

- **New task 11b -- indicator state in the logger, GATES TASK 12.** Task 11's
  done-check names two logged channels, "images + steering/throttle synced". A
  turn signal is a **policy output**, so it needs a third per-frame field
  (`indicator in {off, left, right}`) and two buttons on the teleop rig. No
  existing task owned this; `1b`, `1c`, `16a`, `M1.4b` are the precedent for
  suffixed appends.
- **Task 12 amended** with the gate, and with a note that "tape on floor" is
  superseded by the TRACK section -- not struck, because the task's intent is
  unchanged.
- **Task 8 amended**: the price is stale by ~$60, the "four items" to verify are
  now **five**, and the **PWM-path question is resolved**.
- Tasks 6, 9 and 10 still say "PF motor" and "LiPo + UBEC", both superseded by
  1b/1c. **Left as-is and flagged here**, not silently rewritten.

## AZ.5 HANDOFF drift, closed

It claimed **"44 appendices A-AR"** while the record stood at **AY (51)** --
appendices AS-AY had no HANDOFF row at all. Fixed, and four workstream rows
added: track layout v1+v2, the sim-rehearsal impossibility, the hybrid track
surface, and vehicle lighting. The PWM-path blocker moved from open to resolved.
Budget line struck and replaced.

**Naming collision flagged, not silently resolved.** "B3" means two different
tasks: ~10 record appendices use "the B3 turning test", which is PRD **T2** and
needs the whole rolling chassis (M1.7); but `PRD_ROADMAP.md` §6b's own B-lane
maps **B3 = task 4, measure donor geometry**, which needs only calipers and is
doable today. The freeze banner now says **T2** and carries a note explaining
the collision. Both readings are left visible; neither was redefined.

## AZ.6 Next steps

**Evan only -- the critical path runs entirely through these:**

1. **Print the tolerance coupon** (task 3), PLA *and* PETG, with the settings
   intended for the chassis. Needs **no parts**, and gates every chassis
   dimension in tasks 5-7. Highest-value action available while an order ships.
2. **Measure the assembled Lego steering rack + diff** (tasks 2/4). This sets
   car width, which sets lane width, which decides whether track v2 fits at all
   -- every 10 mm of car width costs 40 mm of grid span against 140 mm of spare.
3. **Count the diff ring teeth** (62821 = 28 vs 6573 = 24+16) and confirm the
   power bank reads **5V/3A**.
4. **Decide Pi 2GB vs 4GB** -- a $45 swing that no longer restores the ceiling
   either way, so it is now a value call rather than a budget fix.
5. **Pick the LEDs** (new BOM verify item 5) -- forward voltage sets every
   resistor value.
6. **Place the order.**

**Available without hardware:** parametric CAD for tasks 5-7 written to consume
the coupon's numbers when they exist (task 6's motor cradle is explicitly meant
to stay parametric); the M2 logger's indicator-field design ahead of task 11b;
and further doc reconciliation.

**Blocked on measurement, not on time:** track v2's corner geometry (T2), the
final track version's bridge and 5 destinations, and any lane-width number.

## AZ.7 Verified

- BOM table renders: every data row has 5 columns, every category separator has
  1, matching rows 17/22/26/32; no markdown links introduced (the file uses bare
  domains throughout).
- Totals recomputed from the row values themselves.
- `grep` for the stale `$178-181` / `$176-179` anchors across the live docs
  returns only struck or dated-corrected hits; record appendices are append-only
  and left untouched.
- `python cad/track_layout_v2.py --self-check` still **PASS** -- nothing here
  touches geometry, so a change would have meant something went wrong.

# Appendix BA - Vehicle envelope derived (height provably blocked); camera height attempt 2 is a second negative and the curvature hypothesis is refuted; indicator logging lands (2026-09-01, ~22:04 CDT)
Evan asked for three things: dimensional requirements (height/width/length/
steering angle), the camera-height measurement (A), and indicator logging (B).
Two delivered. **A is a SECOND negative, and this entry does not dress it up.**

## BA.1 Vehicle envelope: three of four derived, height provably blocked

`cad/vehicle_envelope.py`. This inverts the project's usual direction --
everywhere else the Lego parts are measured and the car "lands where it lands";
here the track is held fixed and the envelope is solved for, so the measurement
at B2 has a pass/fail to meet.

**WIDTH** -- hard ceiling from the grid fitting the floor. The straight run
between corners trades directly against width:

| corner R | max car width @ straight=0 | @ straight=200mm | verdict for 130 mm |
|---|---|---|---|
| 500 mm | 400 mm | 200 mm | fits, with proper straights |
| 550 mm | 300 mm | 100 mm | fits only with tangent corners |
| 600 mm | 200 mm | none | fits only with tangent corners |
| 670 mm | 60 mm | none | **does not fit** |

**STEERING ANGLE** -- the minimum max-lock, `atan(wheelbase / R)`. At the R=500
corner track v2 uses: **11.3 deg** at a 100 mm wheelbase, **13.5** at 120,
**15.6** at 140, **17.7** at 160, **19.8** at 180. The recorded ~330 mm
minimum-radius estimate implies **21.5 deg at a 130 mm wheelbase**, which is
where that estimate came from.

Every one of these is a **FLOOR** from a bicycle model that ignores tyre slip,
Ackermann error and roll -- all of which make the real radius LARGER. Build
margin over them. `gotchas.md` already records that LEGO ball-jointed knuckles
with a straight tie rod give near-parallel steer, not true Ackermann.

**LENGTH** -- bounded by off-tracking, which the project had not accounted for
anywhere. A turning car sweeps WIDER than its own width because the rear axle
cuts inside the front. At R=500 mm, off-track is 10.1 mm at a 100 mm wheelbase
rising to **41.7 mm at 200 mm**, and lane clearance per side falls from 59.9 mm
to 44.1 mm. Past a ~160 mm wheelbase it breaches a 50 mm/side working minimum.

**HEIGHT -- CANNOT BE DERIVED, and that is a result rather than an omission.**
Camera height does not set the horizon row; PITCH does (AR). The horizon sits
at row 41.97 because the camera is pitched 16.3 deg down, and that is true at
ANY height. What height changes is SCALE. So the only thing that pins the real
camera's height is matching the SIM's -- which is exactly what BA.2 failed to
measure. Any number would have been invented.

**A contradiction found and fixed while writing this:** the first cut held the
straight run fixed at 200 mm and concluded R=550 and R=600 do not fit -- while
`track_layout_v2.py` reports both fitting, because it SHRINKS the straight as
the radius grows (`best_straight`). Two scripts describing one track disagreed.
`max_car_width` now takes the straight as an argument and the table shows both
ends of the trade; a self-check pins the two together.

## BA.2 Camera height, attempt 2: the sweep worked, the fit did NOT

AR.5 listed three causes for the first failure and this attack fixed all three.
`ml/diag_camera_height.py`.

**The instrument worked.** `PIDDriver.act` takes the error and its setpoint is
implicitly zero, so passing `act(cte - target(t))` sweeps the car laterally
with **no change to the driver** -- one line at the call site. With a slow
30 s/cycle sine at +-0.6 m:

```
1,800 frames, cte range [-1.044, 1.621] m, sd 0.476
```

against the original corpus's sd **0.053** -- **9x the lateral excitation**,
which was cause 2. Border censoring (cause 1) is enforced by rejecting any row
whose centroid sits within 8 px of a border or whose mask touches one. The slow
sweep addresses cause 3.

**The fit still fails, and worse than before.** Pinning the horizon at its
trusted direct measurement (41.974, sd 0.284 over 3,187 frames) leaves one
unknown, the scale:

```
45 usable rows, mean |r| 0.509
  ONE-PARAM (horizon PINNED at 41.97): h/cos(pitch) = 2.1027, R^2 = -0.3232
  FREE 2-PARAM: h/cos(pitch) = 4.5130, horizon = -13.59 (vs 41.97 measured)
```

**R^2 is NEGATIVE.** The model fits worse than a constant. The per-row
correlation between the line's column and `cte` is only 0.509. The geometry
`slope(v) = -(cos t / h)(v - v_h)` does not describe this data, so **no height
is being reported.** The 2.10 figure is what the arithmetic returns, not a
measurement.

The free 2-parameter fit is separately untrustworthy for a reason worth
recording: the usable rows are 64-112 and the horizon is near row 42, so it
extrapolates ~100 rows past its own data and a 3-4% slope error swings the
intercept by tens of rows -- which is how it produced a horizon of -13.59,
outside the image entirely.

## BA.3 The curvature hypothesis, tested and REFUTED

The obvious explanation was that `generated-roads` CURVES, so the line's
lateral offset varies with forward distance and the model's constant-X premise
breaks. The synthetic self-check passes precisely because it builds a straight
road.

Tested by scoring each frame's straightness (residual of a line fit to the
line's column-vs-row trace) and keeping only the straightest:

| kept | frames | h | R^2 | free-fit horizon |
|---|---|---|---|---|
| 100% | 1,346 | 2.192 | **0.858** | 28.01 |
| straightest 50% | 673 | 1.969 | **-0.188** | -9.45 |
| straightest 25% | 337 | 1.646 | **-1.867** | -36.75 |

**Filtering out curvature makes the fit monotonically WORSE.** If curvature
were the confound, removing it would improve the fit. It does the opposite, and
h drifts 2.19 -> 1.97 -> 1.65 as the filter tightens, which is the signature of
an estimate with no stable value. The apparent R^2 = 0.858 on the unfiltered
set is therefore driven BY the curved frames -- the confound was carrying the
fit, not spoiling it.

**So the hypothesis is dead and the cause is still unknown.** Something other
than lateral offset moves the line's column, and it is not road curvature.

## BA.4 What a third attempt needs, concretely

`gym_donkeycar`'s per-step `info` carries more than `cte`
(`donkey_sim.py:444-455`): **`pos` (x, y, z)**, **`car` (roll, pitch, yaw)**,
`vel`, `gyro`, `accel`, `forward_vel`. None of it was logged here.

The next attempt should log `pos` and `car`, compute heading error against the
road direction, and either regress with heading as a second covariate or filter
on it directly. That tests the one cause AR named and this run could not
isolate: heading error still dominating despite the slow sweep. It is bounded --
the collection script already exists and needs two more logged fields.

**Two designed experiments, two negatives.** That is the honest state, and the
method is not yet vindicated.

## BA.5 Indicator logging (PRD task 11b) -- done and round-tripped

`ml/episode_writer.py` gains `INDICATOR_OFF/LEFT/RIGHT`, an `indicator=`
argument on `add_reset`/`add_step` defaulting to OFF so **every existing caller
is unchanged**, and a `log_indicator` (T,) int8 channel.

**Why the `log_` prefix:** dreamerv3-torch's dataloader filters keys containing
`log_`, so the M4 world-model path is untouched, while this project's own
scripts read the npz directly and can use it as a target -- exactly how
`train_cte_probe.py` already consumes `log_cte`. Precedent, not invention.

`_check_indicator` **raises** on anything outside the three states, including
`True` (which would otherwise coerce to 1 = LEFT). A silently-coerced label is
worse than a crash: it trains the third head on garbage while every shape check
still passes.

**The self-check caught a real gap.** `save()` builds the archive from a fixed
`_DTYPES` whitelist, so the first version wrote episodes with **no indicator
channel at all** -- the round-trip assertion failed on `"log_indicator" in ep`.
Fixed with a `_PER_FRAME_LOG` tuple, kept distinct from the `meta` block
because meta stores ONE constant per episode while this varies frame to frame.

```
$ python ml/episode_writer.py
episode_writer self_check: PASS
```

Regression: the P2 done-check still passes on the untouched 88-episode corpus
(102,888 frames, 88/88 on both axes), so the format change is backward
compatible -- old episodes simply carry no indicator key.

## BA.6 Still open

- **Camera height: unknown after two attempts.** Third attempt scoped in BA.4.
- The height requirement in `vehicle_envelope.py` stays blocked on it.
- Nothing ordered; every hardware item remains BLOCKED-ON-EVAN.
- The indicator channel exists in the writer but **nothing writes it yet** --
  the teleop rig that would set it is task 11, which needs hardware.

# Appendix BB - claude CLI verified installed, and the 3dstreet MCP blocker was pending APPROVAL all along - not a restart and not the browser tab (2026-09-01, ~22:14 CDT)
Evan reported the `claude` CLI should now be available. Verified, and checking
what it unlocks answered a question that had been wrong in two previous entries.

## BB.1 The CLI is installed

```
$ which claude
/c/users/evan.evanfredy/.local/bin/claude
$ claude --version
2.1.258 (Claude Code)
```

`claude.exe`, 218 MB, installed 2026-09-01 21:40. **`ANTHROPIC_API_KEY` is
still NOT set** — the CLI authenticates by OAuth, so the half of the standing
environment note about the API key stands and only the CLI half is falsified.

The global `~/.claude/CLAUDE.md` had **already** been corrected at lines 73-74
before this session looked; the stale copy was the session-start snapshot in
context. `HANDOFF.md:129-130` still claimed the CLI was absent and is now
struck and replaced.

## BB.2 The 3dstreet MCP blocker was neither the CLI nor the browser tab

This is the correction that matters. Across AT.1 and the exchange that followed
I reported that `3dstreet-mcp` exposed zero tools and inferred, twice, that the
cause was the server not being loaded into the session and needing a restart,
and separately that pairing the browser tab was the missing step. **Both were
wrong.** `claude mcp list` gives the actual state:

```
3dstreet: npx -y 3dstreet-mcp - ⏸ Pending approval (run `claude` to approve)
```

A **project-scoped** server declared in `.mcp.json` requires the user's
explicit approval the first time it is seen. Until that happens it is not
loaded at all — which is exactly why the server never appeared in the session's
server list, not even as a failure, and why pairing the 3dstreet tab did
nothing: there was no relay client to pair with.

**Evan must run `claude` interactively in this project directory and approve
it.** A model cannot and should not approve a server that will execute
`npx -y 3dstreet-mcp` under his account.

Note this does not change the design conclusion in AT.1: even once approved,
3DStreet is a street **cross-section** tool with no curved streets, so the
figure-8 and the city grid still live in `cad/track_layout_v*.py`. Approval buys
the marking design and a portfolio render, nothing about plan-view geometry.

## BB.3 Other MCP state, for the record

`claude mcp list` also reports, unprompted:

- `claude.ai Google Drive`, `Gmail`, `Google Calendar` — connected
- `context7` — connected
- `plugin:github:github` — **failed**, HTTP 400 "Authorization header is badly
  formatted" (the same failure this session's tool listing reported)
- `plugin:railway:railway`, `plugin:stripe:stripe` — need authentication

None of these are project blockers; recorded so a future session does not
re-diagnose the GitHub failure as new.

## BB.4 What the CLI actually unlocks

- `claude mcp add` / `list` / `remove` — MCP management without Evan hand-editing
  JSON.
- Any skill that shells out to `claude`. **Still gated by the missing
  `ANTHROPIC_API_KEY`** for anything that needs raw API access rather than the
  CLI's OAuth session, so the standing caveat is narrowed, not removed.

Nothing in the project's build, sim or CAD path depended on the CLI, so no
blocked work becomes unblocked by this alone.

# Appendix BC - Arduino Uno supersedes the PCA9685 one day old: encoder counting and a watchdog for $0, the $200 ceiling is reachable again, and the record write-guard is confirmed firing (2026-09-02, ~15:20 CDT)
Evan produced an Arduino he had lying around. Identified it, verified it works,
and it turns out to beat the part chosen 18 hours earlier — so the PCA9685
decision of Appendix AY is superseded one day old. Also: the record write-guard
added yesterday is now confirmed FIRING.

## BC.1 The board, identified from the USB IDs and not from the photo

**Arduino Uno R3 clone: ATmega328P (TQFP), 5V logic, FTDI FT232RL, COM3.**

```
USB Serial Converter   USB\VID_0403&PID_6001\A5069RR4     Status: OK
USB Serial Port (COM3) FTDIBUS\VID_0403+PID_6001+A5069RR4A\0000
```

**I guessed CH340G from the photo and was WRONG.** The chip beside the USB jack
is an FT232RL in SSOP-28, not a CH340G in SOIC-16; I read a nearby crystal as
evidence for CH340 (which needs one) when FT232RL has an internal oscillator.
The lesson is not "look harder at the photo" -- it is that **the USB vendor and
product ID is authoritative and a package outline is not.** Driver already
installed; nothing to install. Arduino IDE is already present at
`~/AppData/Local/Programs/Arduino IDE`.

A separate Windows prompt to install "Adafruit Industries LLC" port software
appeared and is unrelated: no `VID_239A` device is connected, and every device
in a non-OK state is `CM_PROB_PHANTOM` (ghost entries for unplugged hardware),
not a driver failure. Almost certainly the Arduino IDE installing its bundled
driver bundle. Not needed for this board.

## BC.2 The decision: actuation moves to the Uno, PCA9685 dropped

The PCA9685 is a PWM expander and nothing else. The Uno does everything it would
have done **plus two things it cannot**:

1. **Quadrature encoder counting** on hardware interrupts D2/D3 -- exactly one
   encoder's worth, which is what the chosen encoder motor needs. A Pi does this
   badly because Linux guarantees no interrupt latency, so it silently
   undercounts at speed, and the symptom reads as "the model is bad" rather than
   "the odometry is wrong".
2. **A throttle watchdog.** Firmware cuts throttle if no command arrives inside a
   timeout, so a hung Pi or a diverging policy stops the car instead of driving
   it into a wall. Not possible on an I2C PWM chip.

**Channel budget, checked rather than assumed.** The Servo library claims
Timer1, killing PWM on pins 9/10 and leaving PWM on **3, 5, 6, 11**. Needed:
motor + headlights + tail = 3 PWM, servo on its own library, and the two
indicators are on/off so plain digital pins serve. **Fits with one PWM spare.**

**The cost, stated and not buried:** DonkeyCar's `pins.py` has a PCA9685 backend
and **no Arduino backend**, so PRD task 11's actuator path becomes custom
firmware plus a serial protocol this project writes and debugs. Consistent with
a project whose differentiator is already custom PyTorch, but it is real work the
$6-15 part would have avoided.

## BC.3 The budget moves, and the $200 ceiling is reachable again

Recomputed from the rows, not carried forward. Rows 17-20 fall from
**$10.50-$24.00** to **$4.50-$9.00** because row 17 is now $0 (owned).

| | before shipping | with $15-25 shipping |
|---|---|---|
| TOTAL (4GB Pi) | $232-249 -> **$226-234** | $247-274 -> **~$241-259** |
| with the 2GB Pi | $187-204 | $202-229 -> **~$196-214** |

**The 2GB path's low end now clears $200 for the first time since lighting was
added.** The top does not, and on the 4GB Pi every path is still over. So the
ceiling is reachable rather than restored -- a real change from 2026-09-01, when
every path was over. Nothing is ordered.

## BC.4 The wiring rule finally becomes true

`docs/BOM.md`'s "one rule that matters" has now been wrong twice and is right
once. It originally claimed the Pi and motor pack share "ground only ... Nothing
else crosses between them" while the same paragraph required the ground as a
reference "for the PWM/direction logic" -- so PWM and direction wires crossed all
along. AY amended the wording to cover I2C. **The Arduino swap makes the strong
version true for the first time:** every actuator signal now originates on the
Uno, on the motor-pack side, and the only Pi link is **USB with its 5V conductor
cut**. Two data wires and a ground reference, no power path.

## BC.5 Power, and two ways to get it wrong

- **An Uno on USB makes the power brief's "zero USB peripherals" claim FALSE.**
  The board is ~50 mA, but if it sourced LED current from its pins that is up to
  160 mA onto the Pi's 5V/3A bank with its 600 mA peripheral cap -- exactly what
  `LIGHTING_SPEC` section 3 exists to prevent. **The Uno's 5V pin is fed from the
  LM2596 rail**, so LED current stays on the motor pack.
- **Do NOT power it from VIN off the 7.4V pack.** The pack sags under motor
  stall; below ~7V the on-board AMS1117 drops out and the Uno browns out
  MID-DRIVE, taking the servo and the watchdog with it. Feeding the 5V pin
  bypasses that regulator entirely.
- **The USB 5V wire must be cut.** With the Uno on the LM2596 rail and USB
  plugged in, two 5V supplies meet and back-feed. A data-only cable removes the
  conflict rather than trusting a clone's unverified power-select circuit.

**A current limit tighter than the PCA9685's**, and easy to miss: an ATmega328P
pin sources 20 mA, but the absolute maximum across ALL I/O together is **200 mA**
-- a shared budget, where the PCA9685's 25 mA was per channel and independent.
8 LEDs at 20 mA is 160 mA, 80% of the hard limit; realistically ~120 mA peak
(4 lamps steady, 2 indicators blinking). Workable; brighter LEDs need MOSFETs.

## BC.6 The counterfeit-FTDI trap

FTDI has twice shipped Windows drivers that deliberately disabled **counterfeit**
FT232RL chips -- the 2014 driver bricked them by zeroing the USB PID, a later one
made them transmit `NON GENUINE DEVICE FOUND` in place of data. Clone Unos are
where counterfeit FT232RLs live, and genuine-versus-fake is not determinable from
here. **If COM3 dies or the board starts sending garbage after a Windows update,
that is the cause -- not the wiring and not the firmware.** The fix is rolling
back the FTDI driver. In `gotchas.md` so nobody debugs their own code for a day.

## BC.7 Bins updated -- and three deliberately not

The pm-cadence hook had flagged the codebase-memory bins three times.

- **`architecture.md`** -- the actuation decision above, superseding the PCA9685
  entry. This bin had been 40 days stale and the staleness was real.
- **`gotchas.md`** -- a new Arduino section: the 3.3V/5V hazard, FT232RL
  identification, the counterfeit-driver trap, Timer1 stealing pins 9/10,
  pins 5/6 sharing Timer0 with `millis()`, the USB-peripheral cap, the VIN
  brownout, and 2KB of SRAM meaning nothing ML goes there.
- **`performance.md`** -- was a dated stub. Now real: real-time actuation moves
  off the Pi, and **the FTDI latency timer (default 16 ms) is now on the control
  path against a 50 ms budget at 20 Hz, and is UNMEASURED.**
- **`security.md`** -- was a dated stub. Now real: a serial actuator surface
  exists that did not before, and the watchdog is a SAFETY feature, not a
  security one -- it does nothing against a hostile writer on the port.
- **`ui.md`, `conventions.md`, `dependencies.md` NOT touched.** Nothing about
  them changed. `ui.md`'s "N/A, no frontend planned" is still true, so its
  40-day staleness is CORRECT rather than drift. Writing something there to
  satisfy a hook would be padding.

## BC.8 The record write-guard is confirmed firing

Yesterday's `pretooluse-record-guard.js` (Appendix AW) could not be verified in
the session that wrote it, because hooks load at startup. Tested today on a
**decoy** file named to match the guard's pattern, so the real record was never
at risk. The Edit was DENIED with the full remediation text naming
`append-record-entry.js` and all four flags. **The guard works, and the hook
config from yesterday loaded.** Decoy deleted; `git status` confirms the real
record was untouched by the test.

## BC.9 Not done

- **No firmware exists.** The serial protocol is designed on paper only; nothing
  has been uploaded to the board, and the board has not been proven to run code
  at all. Blink on COM3 is the next five-minute step and would rule out a dead
  bootloader, which clones sometimes ship with.
- **The FTDI latency timer is unmeasured** and sits on the 20 Hz control path.
- Everything else remains BLOCKED-ON-EVAN: coupon print, rack-and-diff
  measurement, diff teeth, Pi 2GB vs 4GB, which LEDs, and the order.

# Appendix BD - First verified hardware: the Uno runs our firmware (signature 1E 95 0F, F_CPU 16 MHz), and an FTDI clone needs an explicit --fqbn forever (2026-09-02, ~15:26 CDT)
**The first piece of hardware in this project is verified working.** Everything
until now has been "nothing built, nothing printed, nothing ordered". The Uno
adopted in BC now runs firmware this project wrote.

## BD.1 Bring-up, and why it is not stock Blink

Clones very often ship with the factory Blink already flashed, so a 1 Hz LED
proves **nothing** about whether an upload landed. The test sketch is therefore
unambiguous two ways: a **3-fast-blinks-then-pause** pattern, and a **serial
banner plus tick counter** at 115200 so the result is READ, not eyeballed.

Toolchain: `arduino-cli` **ships inside the Arduino IDE** and needed no separate
install --
`~/AppData/Local/Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe`,
version 1.5.1, with `arduino:avr 1.8.8` already present.

```
$ arduino-cli compile --fqbn arduino:avr:uno firmware/uno_bringup
Sketch uses 2430 bytes (7%) of program storage space. Maximum is 32256 bytes.
Global variables use 192 bytes (9%) of dynamic memory, leaving 1856 bytes...

$ arduino-cli upload -p COM3 --fqbn arduino:avr:uno firmware/uno_bringup -v
Programmer type       : Arduino
Description           : Arduino bootloader using STK500 v1 protocol
HW Version            : 3
FW Version            : 4.4
Device signature = 1E 95 0F (ATmega328P, ATA6614Q, LGT8F328P)
Writing 2430 bytes to flash
Writing | ################################################## | 100% 0.30s
2430 bytes of flash written
```

Read back off COM3 at 115200:

```
UNO-BRINGUP-OK build=2026-09-02 pattern=3fast+pause
F_CPU=16000000
tick 0
```

**That is our exact compiled string, so the board is running OUR code and not a
factory image.** Device signature `1E 95 0F` confirms a real ATmega328P, and
`F_CPU=16000000` is the chip reporting its own clock. Upload path, bootloader,
and serial in both directions all work.

## BD.2 One thing that will bite every future upload

`arduino-cli board list` reports COM3 as **`Unknown`, with no FQBN**:

```
Port Protocol Type              Board Name FQBN Core
COM3 serial   Serial Port (USB) Unknown
```

That is **normal for an FTDI clone** and not a fault. A genuine Uno R3 announces
itself through an ATmega16U2 carrying Arduino's USB vendor ID; an FT232RL is a
generic serial bridge and carries none. **Every compile and upload must pass
`--fqbn arduino:avr:uno` explicitly**, and the Arduino IDE's board dropdown will
not auto-select either. Recorded in `firmware/README.md` so it is not
rediscovered as a bug.

## BD.3 Artifacts

- `firmware/uno_bringup/uno_bringup.ino` -- the bring-up sketch, out of scratch
  and into the repo, because it is the reference for "the board works".
- `firmware/README.md` -- verified board facts (signature, F_CPU, bootloader
  version, FTDI IDs, COM3), the exact build/upload commands, the FQBN trap
  above, and what is NOT done.

## BD.4 Still not done, stated plainly

- **No control firmware exists.** The serial protocol is on paper only. Blink
  proves the board and the toolchain, nothing about the actuation design.
- **The FTDI latency timer (default 16 ms) is UNMEASURED** and sits on the 20 Hz
  control path whose entire budget is 50 ms per step. It is now the most
  concrete unmeasured number in the hardware lane. The tick cadence in the
  capture above cannot serve as the measurement -- those ticks had accumulated
  in the FTDI buffer since the upload reset, so they time the buffer, not the
  loop.
- Nothing is ordered. Coupon, rack-and-diff measurement, diff teeth, Pi RAM,
  LED choice and the order itself all remain BLOCKED-ON-EVAN.

## BD.5 3dstreet: still absent after a fifth check

Checked again this session; no `mcp__3dstreet__*` tool exists. The CLI reports
the server `Connected` and Evan has both approved it and paired the tab. The
remaining untested variable is ORDER: the relay publishes its tool list from the
paired tab, so the tab must be paired **before** the session starts, not after.
That sequence has not yet been tried. Recorded so the next session tries it
rather than re-diagnosing from scratch.

# Appendix BE - SRAM measured at 2048 B and the clock at 16.0042 MHz; CORRECTION to BD (F_CPU was never measured), and the silicon's signature says 328PB while avrdude says 328P (2026-09-02, ~15:41 CDT)
Evan asked how much RAM the board has. The answer is 2048 bytes, but getting
there **corrected an error in BD, produced a real clock measurement, and turned
up a signature conflict that says the chip may not be what avrdude claims.**

## BE.1 CORRECTION to BD: "F_CPU is the chip reporting its own clock" is WRONG

BD.1 states the bring-up output proved the clock because `F_CPU=16000000` came
back over serial. **It proves nothing.** `F_CPU` is a macro the BUILD supplies
from the board definition; the chip never reported it, and printing a constant
you compiled in is circular. The same commit message repeats the claim.

This mattered, because the signature avrdude read is shared with a part that
runs at a different speed (BE.3), so the clock was exactly the thing that needed
independent measurement rather than assertion.

## BE.2 SRAM: 2048 bytes, measured

`firmware/uno_memtest`. Three numbers rather than one, because each can fail
differently:

```
RAMEND (compile-time) = 0x8FF
SRAM total implied by RAMEND = 2048
MEASURED malloc'd = 1472 B in 46 x 32B
MEASURED freeRam before/after = 1705/1705
```

- **2048 B total**, consistent with an ATmega328P/PB.
- **1705 B free** with a small sketch loaded (338 B of globals).
- **1472 B obtainable through malloc** in 32 B blocks. The gap to 1705 is
  allocator overhead plus the static block table, which is expected, not a leak
  -- `freeRam` returns to exactly 1705 after freeing, so nothing was lost.

Confirms rather than assumes the "2 KB, nothing ML goes here" note already in
`gotchas.md`. For the control firmware 1.7 KB is ample: serial buffers and a
couple of encoder counters.

## BE.3 The clock: 16.0042 MHz, measured -- and why it had to be

avrdude's own output names three candidate parts for the signature it read:

```
Device signature = 1E 95 0F (ATmega328P, ATA6614Q, LGT8F328P)
```

The **LGT8F328P** is a Chinese clone with a different core that commonly runs at
**32 MHz**. On a knockoff board that is a live question, and `F_CPU` cannot
settle it.

Measured by timestamping serial beacons on the HOST and regressing board time
against wall time:

```
host  delta = 19022 ms
board delta = 19027 ms
ratio board/host = 1.00026   (+0.026% error)
implied real clock = 16.0042 MHz
```

**16 MHz, to 0.026%.** An LGT8F328P at 32 MHz on a 16 MHz build would read ~2.0;
the internal 8 MHz RC oscillator would read ~0.5. Both excluded.

**A false alarm on the way, worth recording because the method was the fault.**
An earlier capture gave a ratio of **0.54**, which would have meant an ~8.7 MHz
part. It was wrong: **opening the serial port RESETS the board**, so board
uptime restarts while the host stopwatch does not, and comparing the two
absolute values is meaningless. The fix is to timestamp each line on the host
and use DELTAS, which is immune to when either clock started. The 0.54 also
contradicted evidence already in hand -- serial at 115200 was clean, which a
2x clock error would have made impossible -- and that contradiction is what
prompted re-measuring instead of reporting it.

## BE.4 The signature conflict: the chip may be a 328PB, not a 328P

Two ways of reading the signature **disagree**:

| method | result | part |
|---|---|---|
| avrdude over STK500 | `1E 95 0F` | ATmega328P |
| in-app `boot_signature_byte_get(0,2,4)` | **`1E 95 16`** | **ATmega328PB** |

**The in-app read is the more direct evidence.** avrdude talks to the
**bootloader**, and optiboot **hardcodes** the signature bytes it reports as
build-time constants -- so avrdude is quoting what the bootloader was compiled
to say, not what the silicon is. The in-app read goes to the signature row.

Consistent with everything else measured: a 328PB has 32 KB flash, **2 KB SRAM**
and runs at 16 MHz here. Nothing observed contradicts it.

**Not treated as settled.** One in-app read is not a cross-check, and the
practical rule either way is the same: **treat the part as 328P-family and do
not rely on PB-only peripherals** (the PB adds a third timer, a second UART and
extra I2C, none of which the plan uses). Recorded so a future session does not
"discover" the discrepancy and assume the board is broken.

## BE.5 Bins updated

- **`gotchas.md`** -- the signature ambiguity and why optiboot's answer is the
  weaker one; `F_CPU` is a build constant; the port-open reset and the timing
  method it forces; the measured 2048 B.
- **`tooling.md`** -- `arduino-cli` lives inside the IDE and is not on PATH;
  `--fqbn arduino:avr:uno` is mandatory on every command because an FTDI clone
  reports no board identity; how to read the port from PowerShell and the reset
  caveat.
- **`dependencies.md`** -- the Arduino toolchain, and the fact that firmware uses
  **only** bundled `Servo` and AVR headers, so there is no third-party Arduino
  dependency to vendor or pin.
- **`ui.md` deliberately still untouched** -- still no frontend, so its staleness
  remains correct rather than drift.

## BE.6 Still not done

- No control firmware; the serial protocol remains paper only.
- **The FTDI latency timer is still UNMEASURED.** Note this is a DIFFERENT
  quantity from the clock measured above: the clock is the chip's timebase, the
  latency timer is how long the USB bridge sits on bytes before delivering them,
  and only the latter eats the 50 ms control budget.

# Appendix BF - FTDI latency timer measured: configured at 16 ms but costs ~0.9 ms on the wire, so the risk flagged in BD and BE was wrong (2026-09-02, ~15:50 CDT)
The FTDI latency timer was the most concrete unmeasured number in the hardware
lane, flagged in BD and BE as sitting on the 20 Hz control path. **Measured. It
does not threaten the loop, which means the risk I flagged twice was wrong.**

## BF.1 The configured value really is 16 ms

```
HKLM\SYSTEM\CurrentControlSet\Enum\FTDIBUS\VID_0403+PID_6001+A5069RR4A\0000\Device Parameters
LatencyTimer    : 16
MinReadTimeout  : 0
MinWriteTimeout : 0
```

So the premise of the concern was correct: the FT232RL is configured with the
16 ms default, and a control reply is a SHORT packet, which is precisely the
case the timer governs.

## BF.2 The measured round trip is ~0.9 ms, not 16 ms

`firmware/uno_echo` echoes a byte with no delay, no formatting and no flush, so
what remains is USB out + microseconds of AVR + USB back.

First pass, 200 single-byte exchanges: p50 **0.508 ms**, p95 0.634, p99 0.764,
max 7.277, 0 failures.

Then at the shape that actually matters -- a 4-byte command and 4-byte reply,
paced at 20 Hz for 400 exchanges:

```
n=400 fails=0   (4-byte cmd -> 4-byte reply, 20 Hz)
p50=0.869  p95=0.956  p99=1.069  max=5.753 ms
over 5ms : 1
over 10ms: 0
over 16ms: 0
over 50ms: 0  <- would break the control loop
```

**About 2% of the 50 ms budget at p99, ~12% in the single worst sample, and
nothing above 10 ms across 400 exchanges.** The serial link is not a constraint
on the 20 Hz loop.

## BF.3 The mechanism is NOT established, and I am not going to invent one

The registry says 16 ms. The wire says 0.9 ms. Those are both facts and I
cannot presently reconcile them. The plausible stories -- that the timer bounds
a MAXIMUM wait rather than imposing a fixed delay, that the host driver drains
more eagerly than the datasheet model suggests, or that a counterfeit FT232RL
(BC.6 flags that risk) does not implement the timer faithfully -- are
speculation, and none was tested.

What follows from that honestly:

- **Do not budget 16 ms.** It was measured, repeatedly, and it is not there.
- **Do not budget 0.9 ms on a different host either.** This is one machine, one
  driver, one cable. The number is not portable and the mechanism that produces
  it is unknown, so it could differ on the Pi, which is where it will actually
  run.
- The firmware watchdog already covers the failure mode regardless, and if the
  timer ever does bite, the registry `LatencyTimer` value is the known lever.

**Re-measure on the Pi before relying on this.** The measurement that matters is
Pi-to-Uno, and every number above is Windows-to-Uno.

## BF.4 What this corrects

BD.4 and BE.6 both list the latency timer as an open risk on the control path,
and BE.6 goes further, calling it "the most concrete unmeasured number in the
hardware lane". That framing was right to measure and wrong in its expectation:
the concern was reasoned from the datasheet default rather than from the wire.
Two entries carried it as a live risk; it was ~2% of the budget the whole time.

Updated in place: `firmware/README.md` and `.claude/codebase-memory/performance.md`
both had it as UNMEASURED and now carry the numbers plus the caveat that the
mechanism is unexplained.

## BF.5 Artifacts

- `firmware/uno_echo/uno_echo.ino` -- the harness. Deliberately minimal so the
  measurement is of the link and not of the sketch.
- The measurement scripts were scratch PowerShell and are not committed; the
  method is described above precisely enough to repeat: discard the input
  buffer, timestamp with a Stopwatch around write-then-blocking-read, pace the
  loop to 20 Hz, and report percentiles rather than a mean.

## BF.6 Still open

- No control firmware; the serial protocol is still paper only. Echo proves the
  link, not the design.
- The Pi-side measurement above.
- Everything physical remains BLOCKED-ON-EVAN.

# Appendix BG - Serial protocol v0.1 drafted, and drafting it caught D3 double-booked between the encoder interrupt and motor PWM in yesterday's diagram (2026-09-02, ~15:58 CDT)
Serial protocol drafted (`firmware/SERIAL_PROTOCOL.md`, v0.1, DESIGN ONLY).
Drafting it **found a pin conflict in the diagram committed yesterday**.

## BG.1 D3 was double-booked, and it would have failed on the bench

`docs/BOM.md` line 153 assigned D3 to the encoder's second interrupt; line 164
assigned D3 to motor PWM. **Both, in the same diagram, in commit 5ee14a9.**

The conflict is not cosmetic. The ATmega328P has exactly **two** external
interrupts, INT0 on D2 and INT1 on D3, so a quadrature encoder consumes both and
D3 cannot also carry PWM. Wired as drawn, the encoder would have lost a channel
and the motor would have fought it -- and the symptom would have been erratic
counts, i.e. the exact failure mode BC.2 says the Arduino was adopted to avoid.

**Corrected pin map**, now in both the BOM diagram and the protocol doc:

| pin | use | |
|---|---|---|
| D2 / D3 | encoder A / B | INT0 / INT1, the only two |
| D5 / D6 | headlights / tail lights | PWM, Timer0 |
| D4 / D7 | left / right indicator | digital |
| D8 / D12 | motor DIR | |
| D9 | steering servo | Servo lib claims Timer1 |
| D11 | motor PWM | **Timer2** |
| D13 | status LED | |

**Motor PWM is forced onto Timer2 and this is the one non-arbitrary assignment.**
Timer0 also drives `millis()`, so its frequency cannot be changed; motor PWM is
the only channel that may need raising above ~20 kHz to move the whine out of
the audible band. Lights never need that, so they take the frequency-locked
Timer0 pins.

## BG.2 The protocol, and why binary

Fixed-length binary frames, sync byte plus CRC8. **7-byte command, 9-byte
reply.** Full field tables in the doc.

**Binary was chosen for the failure mode, not for speed.** At 115200 with a
50 ms budget even 100 ASCII bytes costs 8.7 ms, so size is irrelevant here --
the measurement in BF already showed the link is ~2% of the budget. What matters
is that a desynchronised stream must not reach the actuators: a sync byte plus a
checksum lets the Uno REJECT a corrupt frame and fall to a safe state, whereas a
line-oriented ASCII parser silently accepts a truncated number as a valid one.

One ASCII escape hatch is kept: a lone `?` outside a frame prints human-readable
status, so the board is inspectable from any terminal without a decoder. `?` is
not a valid sync byte, so it cannot collide.

`int8` for steer and throttle is deliberate: 200 steps against a servo that
resolves perhaps 60 positions across its useful travel, so quantisation is an
order of magnitude finer than the actuator. Upgrade trigger recorded in the doc.

## BG.3 Safety rules

1. **ARMED is opt-in in every frame.** Actuators inert on boot, after reset, and
   after any watchdog trip. Stray bytes cannot start the car.
2. **Watchdog 150 ms** = three missed frames at 20 Hz. On expiry: **throttle to
   zero, HOLD last steering, flash both indicators as hazards.** Throttle-zero
   is the safety action; holding steering rather than centring avoids a jerk at
   the moment control is lost; hazards make the state visible across the room.
3. **A bad CRC is a dropped frame, never a guessed one** -- reply with the bad-CRC
   status bit and take no actuator action.
4. The watchdog is **SAFETY, not security**: it does nothing against something
   else writing valid frames to the port.

## BG.4 Budget, against measured numbers rather than guesses

Round trip p99 **1.069 ms** (BF) plus 1.39 ms of wire time for 16 bytes at
115200 = roughly **5% of the 50 ms step**; worst observed sample 5.753 ms = 12%.
RAM cost is two 16-byte buffers and an int32 against **1705 bytes free** (BE.2).

**Carried caveat, not resolved:** the BF numbers are Windows-to-Uno on one
cable, and the mechanism producing 0.9 ms against a configured 16 ms FTDI
latency timer is still unexplained. **Re-measure on the Pi before relying on
this.**

## BG.5 Not done

- **Nothing implements this.** No firmware, no Pi-side client. It is a design
  document, and the pin conflict it caught is the argument for writing such
  documents before wiring rather than after.
- Encoder counts-per-revolution unknown until the motor exists, so `ticks` is
  raw counts and conversion is the Pi's job.
- Throttle-to-duty mapping (linear vs calibrated) deliberately left to firmware.

# Appendix BH - landing-check returned FIX FIRST: nine items closed, including a wrong PWM budget the D3 fix silently created and a stale price in the public README (2026-09-02, ~16:11 CDT)
`/landing-check` swept commits `397c46a..590f765` cold, from artifacts only. It
returned **FIX FIRST** with eight findings; a ninth turned up while fixing them.
All are now closed. **One was an engineering error I introduced, not a doc slip.**

## BH.1 The one that mattered: "one PWM pin spare" was FALSE

Stated in BC and repeated in three live docs. The D3 pin fix (BG) falsified it
and nothing noticed.

Arithmetic: the Servo library claims Timer1, killing PWM on D9/D10, leaving
`{3, 5, 6, 11}`. **The encoder then takes D3 (INT1)**, leaving `{5, 6, 11}` --
exactly three, all consumed by motor + headlights + tail. **Zero spare, not
one.**

Why it matters beyond tidiness: **there is no PWM headroom at all.** Any future
PWM channel needs a pin freed or a timer reconfigured, and `gotchas.md` was
still telling a future reader "usable PWM after that: 3, 5, 6, 11" -- four pins,
one of which is spoken for. That is the kind of line trusted at the bench with a
soldering iron in hand.

Corrected in `docs/BOM.md`, `docs/LIGHTING_SPEC.md`,
`.claude/codebase-memory/architecture.md`, plus a new `gotchas.md` entry naming
D3 explicitly. The BC/BG record entries keep the wrong claim -- append-only --
and this entry is the correction.

## BH.2 A document that contradicted itself on arrival

`firmware/SERIAL_PROTOCOL.md:14` warned that `docs/BOM.md` **currently**
double-books D3 -- in the same commit (`590f765`) that fixed it, citing line
numbers that no longer pointed at it. The two files ended up pointing at each
other, each saying the other was wrong. Rewritten to past tense with the fixing
commit named.

## BH.3 A stale budget in the PUBLIC repo

`README.md:128` read "**Budget: ~$178-181, under a $200 ceiling**", unstruck.
The repo is public (`github.com/Evan-Daruwalla/vision-autonomous-car`), the real
figure is **$226-234 before shipping / $241-259 with**, and the ceiling is
breached on the 4GB path. This also falsifies AZ.7's claim that a grep for stale
anchors "returns only struck or dated-corrected hits" -- **a false universal**,
and the second one this project has produced in a public file.

## BH.4 The PCA9685 supersession reached 3 of 6 docs

BC replaced the PCA9685 with the Uno. It propagated to `BOM.md`,
`architecture.md` and `gotchas.md`, and NOT to:

- `HANDOFF.md` -- three live assertions (rows 215, 232, 326) plus two stale
  totals (215, 330), including "RESOLVED ... PCA9685, BOM row 17"
- `PRD_ROADMAP.md` -- two blocks (the task-8 amendment and the ~line-96 budget
  note), both still stating $232-249 / "$200 breached on every path"
- `docs/LIGHTING_SPEC.md` section 7 -- the only section with no supersession
  banner, carrying "**Order the PCA9685**" as a live imperative, plus a ceiling
  claim `BOM.md:59-62` had already struck

All closed, and the imperative at section 2's end now reads **DO NOT ORDER IT**.

## BH.5 The rest

- `docs/BOM.md:224` still said the total was "\u2248$237-250"; struck, now \u2248$241-259.
- `dependencies.md` claimed firmware uses "the bundled `Servo` library". **No
  `.ino` includes `Servo.h`.** Corrected to what is actually included
  (`avr/io.h`, `avr/boot.h`, `stdlib.h`), with a note that Servo is PLANNED and
  matters because it claims Timer1 and thereby sets the whole PWM budget.
- `docs/research/2026-07-23_power-system.md:22` still read "This build has zero
  USB peripherals, so the cap is irrelevant." Two bins had flagged it as false
  since BC; **neither propagated to the brief itself.** Now corrected in place
  with the conclusion preserved (~50 mA is still far inside the 600 mA cap).
- `HANDOFF.md:5` said "55 appendices A-BC"; the record held **59, A-BG**, and it
  was already wrong when set in `084d271`.
- **Ninth, found while fixing:** `PRD_ROADMAP.md` ~line 96 carried a SECOND copy
  of the superseded budget block. The sweep named one; there were two.

## BH.6 What the sweep confirmed, which matters as much

Load-bearing negatives, all re-derived by the agent and spot-checked by hand:

- **BOM arithmetic reproduces 13/13 to the cent**, including every historical
  and struck figure. No invented precision anywhere.
- **The D3 fix genuinely landed in both files** -- full 11-pin enumeration, no
  pin assigned twice.
- **The FTDI numbers are byte-identical across all four copies**, and neither
  `firmware/README.md` nor `performance.md` still says UNMEASURED.
- Every re-derivable measurement exact: 2048 B, 1472 B, 1.00026, 16.0042 MHz,
  1.389 ms, 8.68 ms, 4.9%, 80%, 120 mA.
- **The record write-guard fired on a planted positive and stayed silent on a
  negative**, canary 23/23, tested on a decoy so the real record was never at
  risk. No mislanding, one live hook, no dead copy.

## BH.7 Two process notes worth keeping

1. **The sweep's findings held; its citations did not.** It cited
   `HANDOFF.md:330` as a PCA9685 mention -- `grep -n PCA9685 HANDOFF.md` returns
   55, 56, 215, 232, 326 and not 330. Line 330 IS stale (a superseded total) but
   for a different reason. Re-deriving every cited line before acting was worth
   it, exactly as the skill says.
2. **A doc-only finding was an engineering error in disguise.** "One PWM spare"
   reads like prose drift and is actually a wrong pin budget. The cheap tell was
   that a *fix* (BG) silently invalidated a *claim* made two entries earlier;
   nothing in the workflow connects those, which is why the cold sweep found it
   and the author did not.

## BH.8 Not swept

Appendices BA/BB and commit `d2527a1` -- `cad/vehicle_envelope.py`,
`ml/diag_camera_height.py`, `ml/episode_writer.py` -- were outside the sweep and
remain unverified. Handoffs the sweep raised: `/code-review` for the three
`.ino` files and that Python; and the latency percentiles came from **scratch
PowerShell that was never committed**, so those headline numbers are not
reproducible from the repo by anyone but this session.

# Appendix BI - Rows 11/13/14 linked, and row 11's board does NOT document the over-discharge protection the BOM credited it with - the 2S pack has no low-voltage cutoff (2026-09-02, ~16:34 CDT)
Found the three missing BOM links (rows 11, 13, 14). **Row 11 turned up a safety
gap, not just a URL** \u2014 the board the BOM calls a "BMS" does not document the
protection the BOM credits it with.

## BI.1 The safety finding: the 2S pack has no low-voltage cutoff

`docs/BOM.md` row 11 claimed the Adeept USB-C 2S board "provides overcharge,
**over-discharge** and short protection." Adeept's own product page lists:

> "Battery charger board has strong adaptability to input power and **over
> voltage protection** for battery"
> "Boost lithium battery module preserves the battery voltage below the input
> voltage and battery **short circuit**"

**Over-discharge protection is not listed.** The board is a charger with a boost
converter and over-voltage/short protection, sold under a "BMS" title.

**And the cells are bare.** Row 9's EVE 25P are unprotected cells. So as the BOM
is written today, **nothing stops the pack being run flat under motor load** \u2014
which is exactly what a driving robot does to a battery.

Why this is worth stopping for rather than noting: below ~2.5 V/cell, lithium
takes permanent capacity loss, and in the worst case grows internal copper
shunts that become a **fire risk on the NEXT charge**. Short-circuit is already
covered independently by the mandatory inline fuse (row 15). This is
specifically the low-voltage end, and it is uncovered.

**Three ways to close it, added as Verify item 6:**
(a) a 2S protection board that explicitly states over-discharge cutoff;
(b) protected cells;
(c) **firmware cutoff on the Arduino** \u2014 A0-A5 are free
(`firmware/SERIAL_PROTOCOL.md` \u00a71), so a resistor divider on the pack lets the
Uno cut throttle at a voltage threshold, reusing the watchdog path already
designed. **(c) costs two resistors and is the only option that also LOGS the
event**, which matters for a project whose point is the evidence trail.

Not decided here. It is Evan's call and it is BLOCKED-ON-EVAN with the order.

**Honest limit on this finding:** a vendor page not mentioning a feature is not
proof the hardware lacks it. What is certain is that **the BOM asserted a safety
property the vendor does not document**, and on a lithium pack that gap has to
be closed deliberately rather than assumed away.

## BI.2 The three links

| row | part | link | verified |
|---|---|---|---|
| 11 | USB-C 2S BMS | `adeept.com/li-ion-battery-charger-m-2s2a_p0374.html` | **$7.99** (list $9.99). \u26a0\ufe0f **http only, no TLS** |
| 13 | XT30 pair | `alofthobbies.com/products/xt30-plugs` | **$1.10**, ONE male+female pair, genuine Amass, in stock |
| 14 | SPST rocker | `sparkfun.com/products/11138` | **$0.75**, SPST round, **10A @ 125VAC**, in stock |

**Row 14 vindicates the caution recorded in BH.5.** The previous pass refused to
link `COM-08837` because it looked like a right-angle variant rather than the
10 A part specified. Correct: the right part is **COM-11138 (round)**, and
guessing would have put the wrong SKU in an order.

Row 13 confirms a quantity assumption that had never been checked: one unit is
**one male + one female**, which is what the build needs.

## BI.3 Prices now stand at 12 of 20 rows verified

Combined with BH's pass: Pi 5 4GB $110 \u00b7 Pi 5 2GB $65 \u00b7 Camera Wide $38.50 \u00b7
Pololu #1093 $23.95 \u00b7 Pololu #713 $4.95 \u00b7 BMS $7.99 \u00b7 XT30 $1.10 \u00b7 rocker $0.75
\u2014 **all matching the figures already in the BOM.** The total is live, not stale.

Still unverified prices: rows 9, 10, 12, 15. Still `any` by design: 4, 7, 16,
18-20. Row 15 keeps its warning that BC Robotics' 14AWG and 18AWG fuse-holder
listings have inconsistent titles.

## BI.4 A numbering slip, caught and fixed

Inserting the new Verify item produced the order `1,2,3,4,6,5`. Item 5 could not
simply be renumbered because `docs/BOM.md` row 19 cross-references "Verify item
5" for the LED question, so the new item was moved after it instead. Also
removed a dangling clause left in item 5 by an earlier edit ("or needs a
transistor per channel", orphaned mid-sentence).

# Appendix BJ - Pack low-voltage cutoff implemented on the Uno: 27/27 on hardware, and the hardware test caught a floating-pin fault the design reasoning had missed (2026-09-02, ~16:47 CDT)
Evan chose option (c) from BI: firmware low-voltage cutoff on the Arduino.
Implemented, uploaded, **SELFTEST PASS 27/27 on the real board** \u2014 and testing
it on hardware caught a defect that the design reasoning had missed.

## BJ.1 The defect the hardware test found

The design already argued that a guard must distinguish "broken" from
"triggered", and the first build had a FAULT band for **implausibly LOW**
readings (< 4.0 V), on the reasoning that an unwired A0 would read near zero.

**It does not.** With nothing connected, the real board reported:

```
PACK OK mv=10248 latched=0 throttle=allowed mode=REAL
```

A floating A0 sits near **full scale** \u2014 1.1 V / 0.10714 = 10.27 V maximum
readable, and it measured 10248-10266 mV across runs. That is **above** a full
2S pack (8.4 V), so it sailed past a low-only check and read as a **healthy
battery with throttle ALLOWED**. The guard would have permitted driving with no
sensor attached at all, which is the precise failure it exists to prevent.

Fixed with an upper band: **fault outside 4.0-8.8 V**. Re-verified on hardware:

| input | before | after |
|---|---|---|
| unwired A0, 10266 mV | `OK`, throttle **allowed** | **`FAULT`, INHIBITED** |
| 8400 mV (full 2S) | \u2014 | `OK`, allowed |
| 8900 mV (above any 2S) | \u2014 | **`FAULT`, INHIBITED** |

**The reasoning was right and the constant was wrong**, and only running it on
the board showed which. Recorded in the source header as found-by-testing.

## BJ.2 Design decisions that are load-bearing

**The internal 1.1 V band gap reference, not the 5 V rail.** The Uno's 5 V comes
from the LM2596, which is the same supply that sags when the pack sags.
Measuring the pack against a reference that moves with it produces a meter that
lies precisely when it matters. `analogReference(INTERNAL)` is
supply-independent.

**Divider 100k / 12k**, chosen against tolerance rather than for round numbers.
The obvious 100k/15k puts 8.4 V at 1.096 V against a 1.1 V ceiling \u2014 **0.4%
margin**, which 5% resistors would clip (worst case 1.195 V), silently pinning
the reading at full scale. 100k/12k gives 0.900 V, **18% margin**, worst case
0.984 V, and still resolves 10.0 mV of pack per count against thresholds 400 mV
apart. Divider drain 75 uA = 1.8 mAh/day against a 2500 mAh cell.

**WARN does not cut.** Voltage sags hard under motor stall. Cutting on a
transient makes the car undriveable for no safety gain, so cutoff requires
**6.0 V sustained for 500 ms**, and a dip that recovers **restarts** the timer
rather than resuming it (self-test covers that specific case).

**The latch never clears itself.** With throttle cut the pack recovers a few
hundred mV, would cross back over, re-enable, sag, and oscillate \u2014 cycling the
motor on a pack already too flat. `CLEAR` is explicit AND requires \u2265 6.8 V. The
board refused it correctly under test: `REFUSED: need >= 6800 mV, have 5900`.

## BJ.3 How it is tested with no battery

Nothing is ordered; no pack exists. The state machine is a **pure function** of
(millivolts, now), so `SIM <mv>` injects readings over serial and `SELFTEST`
drives **27 checks through the shipping code path** on real silicon \u2014 not a
host-side mock of it. Every transition is covered: warn without latching, a dip
too brief to cut, a sustained dip that latches, a restarted timer, refusal to
auto-recover, both fault bands, and that WARN/OK do NOT inhibit while
CUTOFF/FAULT do.

Live transitions confirmed on the board beyond the self-test: 7400 OK -> 6300
WARN -> 5900 WARN then CUTOFF latched with throttle INHIBITED -> CLEAR refused
-> 3000 FAULT -> 0 FAULT -> back to 7400 still CUTOFF (latch survives).

**What is NOT verified: the divider and the ADC's real behaviour.** Both need
hardware that does not exist. The resistor values are arithmetic; the 10 mV/count
figure is arithmetic; the only measured ADC number so far is the floating-pin
reading that produced BJ.1.

## BJ.4 The honest limit on this fix

**Firmware cannot protect a pack while the firmware is off.** If the Arduino is
unpowered, disconnected, or mid-reset, the guard does not exist \u2014 and the pack
is still bare cells behind a board that does not document over-discharge
protection. This is a **supplement** to Verify item 6's options (a) a protection
board or (b) protected cells, not a replacement for them. `docs/BOM.md` now says
so at the point of decision rather than only here.

## BJ.5 Artifacts

- `firmware/uno_packguard/uno_packguard.ino` \u2014 6004 bytes flash (18%), 289 bytes
  SRAM (14%), well inside the 1705 bytes measured free in BE.
- `docs/BOM.md` \u2014 Verify item 6 marks (c) implemented with its thresholds, and
  row 19 now carries the two divider resistors (1x 100k, 1x 12k).
- `firmware/README.md` \u2014 the sketch, its limits, and the "firmware off means no
  guard" caveat.
