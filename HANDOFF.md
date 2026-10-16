# Handoff

**Last updated: 2026-10-16 ~13:02 CDT** — this file is the ONLY live snapshot.
History lives in `docs/Project Record — Full Chronological History.md`
(append-only, 246 appendices A–IL; BM/BN/BP/BU/CT/CY/DB/DE/DN/EL/EN/EO/ET/EU are corrections to earlier entries). When this file and the record disagree about
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

**The software lane is four milestones ahead of the hardware lane. The hardware
lane has now STARTED — and as of 2026-09-02 the ACTUATION FIRMWARE RUNS ON THE
BOARD** (`firmware/uno_control/`, host_test 13/13, Appendices BO/CA/CE).
⚠️ **A watchdog defect that would have braked a wired car ~96% of the
time was found by the 2026-09-02 daily-audit (BY) and fixed the same evening
(CA); "verified on the board" before CA covered the link, not this path.**
⚠️ **The flashed build and the repo source now DIVERGE** (2026-09-03, Appendix
DC): ~~the board still runs the 2026-09-02 build (SELFTEST 49/49, 7888 B)~~ **2026-10-10: Evan uploaded `firmware/servo_bench` over it (Appendix FT) - the board runs servo_bench until uno_control is re-flashed** ~~(superseded)~~ ~~**2026-10-13 (HU): uno_control re-flashed, SELFTEST PASS 86/86 on the board**~~ ~~**2026-10-13 ~14:00 (HW): servo_bench flashed again for the backlash test - re-flash uno_control after it**~~ **2026-10-13 ~14:09 (HY): uno_control re-flashed (backlash 75 us), SELFTEST PASS 86/86**, while
`uno_control.ino`'s lighting path was rewritten for WS2812B afterwards —
compiled clean (58 checks, 9680 B) but **never flashed**. Read the boot banner,
never a doc, for what the board is actually running.
**Actuators are still unwired**: the link and state machine are verified, but no
motor, servo, encoder, LED or pack exists, so every actuator path is verified
only as a DECISION the firmware made. SIM-POC (P1–P5) is built and its findings are
banked. ~~Nothing has been printed and nothing has been ordered since
2026-07-23.~~ **PRINTING STARTED 2026-09-05** — two tolerance coupons (v1 and
v2) printed on a Bambu P1S in Bambu ABS, giving M1.3's two headline numbers
(pin holes 4.80 mm, rotating axle bores 5.00 mm, Appendices DI/DK). **Still
nothing ORDERED** — the BOM stands at ~~$411.45~~ **$422.25 before shipping (2026-10-04 cart review)**, ~~unbought~~ **ORDERED; 23 of 24 items ARRIVED 2026-10-10 (Appendices FI/FJ/FK). ~~NOT arrived: Camera Module 3 Wide (a separate order from the cable) - IN SHIPPING as of 2026-10-12 (GX).~~ **2026-10-15: the camera has ARRIVED (Evan; record IX) - all 24 items in. Not yet connected or tested.** Motor confirmed #5159 by its label (FL).**

**2026-09-07: a REAL DEFECT was found and fixed in the controller** (commit
`bfa953e`, Appendix EJ). `ml/train_controller.py` overwrote `act` with the
DART expert relabels and fed that same array to `rnn_states()`, so the frozen
MDN-RNN's hidden state `h_t` was built from a counterfactual action sequence
that never produced the observed latents — worst exactly on the recovery
frames. `ml/diag_copycat.py` imported the same function and inherited it.
Fixed by splitting `act` (executed, feeds the LSTM) from `act_target` (expert
relabel, feeds only the BC loss). **Re-running Appendix Z.3's recovery-data
comparison: the conclusion SURVIVES and sharpens** — held-out MSE for the
augmented arm was understated by the leak (pre-fix +2.2% vs baseline, post-fix
**+17.6%**), and the paired closed-loop result is unchanged at **0/9 survived
in both arms**. Found by the scheduled daily-audit (Appendix EI).

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
- ~~**DonkeyCar's `pins.py` has only three PWM backends** (RPI_GPIO, PCA9685,
  PIGPIO) ... A **PCA9685 breakout** would make actuation board-agnostic.~~
  **RESOLVED 2026-09-02 (Appendix BC): an ARDUINO UNO Evan already owns takes
  all actuation**, so `pins.py` is out of the path entirely. The Uno also brings
  encoder counting (D2/D3 interrupts) and a throttle watchdog, which no PWM
  backend can. Cost: no DonkeyCar backend exists for it, so the actuator path is
  custom firmware + a serial protocol. **It is bring-up tested and running our
  code** — `firmware/`.

---

## Immediate next actions

*(Rewritten 2026-09-06. The old table had become a graveyard of closed rows —
every one of them is in the record, Appendices DI–DQ. This lists only what is
actually open, cheapest-first.)*

**Runnable NOW — no parts, no purchase:**

*(Table rewritten 2026-09-07. Rows closed since the 2026-09-06 rewrite are in
the record — DS the floor-fit, DV/DZ the 3DStreet scene, DU the dash ratio.
This lists only what is actually open, cheapest first.)*

| # | Action | Why it matters |
|---|---|---|
| ~~1~~ | ~~**Decide the dash density**~~ **DECIDED 2026-09-09 (Evan): ACCEPT 18.7.** `TARGET_DASH_CYCLES` is retired; `cad/marking_specs.py` now asserts a max-blind-gap criterion instead (1.8 control steps against a 2.0 limit at 1.401 m/s / 20 Hz). Dash geometry unchanged at 62.6 / 125.2 mm. Appendix EU | ~~One word.~~ Closed. The cycle count was never the quantity that mattered |
| ~~2~~ | ~~**Decide the cornering clearance**~~ **DECIDED 2026-09-09 (Evan): ACCEPT 29.6 mm/side.** `MIN_SIDE_CLEARANCE` re-pointed at the ROAD edge (154.6 mm/side at the measured 185.95 mm wheelbase) and now genuinely ASSERTED in `vehicle_envelope.py`'s self_check. Appendix EU | ~~One word.~~ Closed. **Accepted cost: 29.6 mm is 24% of the half-lane, so the policy will clip the centreline in corners** |
| 3 | **Pitch-row scale check on the printed coupons.** Lego beam across holes 1–2, then 1–5 (nominal 32.00 mm span). If it binds across 5 but not 2, caliper the real span — that ratio is the printer's dimensional scaling error and it applies to every chassis part. | Last unclosed piece of M1.3. Needs only the coupons already printed + real Lego |
| 4 | **Caliper the coupons.** Every fit verdict so far (pin 4.80 mm, axle 5.00 mm) is fit-by-feel, not a measured diameter. | Turns two working numbers into a measured offset that transfers to CAD |
| 5 | **Confirm a 12-tooth bevel gear is in the parts bin.** Evan: "prob have one and if not i can print one" — not a confirmation. A bevel's meshing tooth profile is a harder print than a coupon. | Last unconfirmed pre-order check (PRD A1) |

**2026-10-04 CART REVIEW (side chat; Appendices EZ, FA, FB, FC) - nothing bought:**

- ~~**BLOCKER - the BMS.**~~ **RESOLVED 2026-10-04: Evan is ordering the vetted
  `B08HLQQCQJ`** (8PCS, $9.59), re-verified live - the description still states
  "Overdischarge detection voltage: 2.9V+/-0.05V." The `B08CV2VS8G` in his cart
  documented no set point. Read the DESCRIPTION, not the bullets: both parts'
  bullets say only "Over-discharge protection".
- **NEW SAFETY GAP: `docs/WIRING_PROTOSHIELD.md` never included the BMS.** Its
  net list still runs `PACK+` holder -> fuse, so wiring from it bypasses the
  over-discharge cutoff. Pack -> B+/B-/MB, everything else (charger too) ->
  P+/P-. MB needs the cell midpoint, which the 2-lead holder does not expose.
  A dated warning sits in that doc; ~~the net redraw is OPEN~~ **REDRAWN
  2026-10-10:** cells -> 3 A fuse -> BMS B+ / MB / B-, charger and everything
  else on P+ / P-, plus three Mermaid diagrams (power, signals, ground) in
  section 2.0, every Uno pin checked against `uno_control.ino`.
- **DIANN holder: SERIES per its listing** ("Output Voltage: 7.4V", Evan pasted
  it 2026-10-04). Meter it on arrival - ~7.4-8.4 V across red/black is series;
  ~3.7-4.2 V means parallel, reject it.
- **Resistor kit (KSOPUERT), checked 2026-10-04:** 100k present; NO 12k - build
  it as 10k + 2k in series (12.0k, same 0.10714 ratio; never 10k alone, which
  under-reads the pack 15%); nothing in 330-470 ohm - 2 x 200 ohm in series
  (400 ohm) per strip segment.
- **Coupler (2026-10-04):** no #4252 was ever on hand - the 2026-09-03 build
  was a PRINT of v1, whose axle socket was too loose. ~~Print v2~~ v2 fitted
  2026-10-10; print v3 (`cad/servo_lego_coupler_v3.stl`, Appendix FM). Untested.
- **UNVERIFIED, Evan's hands:** the Vilros kit's 120 mm camera cable pin count; coupler fit on
  the MG90D-270.
- **Decided by Evan:** 22 AWG for every net (26 AWG dropped); PRINT
  `cad/servo_lego_coupler_v2.stl` (v1 printed too loose) instead of buying #4252 (row 22 not retired
  until a coupler survives a load test).
- **In NO cart yet:** 2x Samsung 25R $9.98 at imrbatteries (row 9 - sales
  FINAL, USPS caps 8 cells/package); Adeept p0374 charger $7.99 (row 11).
- **Low stock when reviewed:** resistor kit 3 left, 0.1 uF caps 6, LM2596 6,
  470 uF caps 13, Pi kit 19.
- **Total $422.25 before shipping**, re-derived two ways (row table and order
  sheet agree). The review's own "approx $423" omitted row 22's -$0.75.

**OPEN FROM THE 2026-09-09 DAILY-AUDIT (Appendix ES) — not worked, Evan
cancelled the sweep; the doc half was repaired 2026-09-09 in Appendix ET:**

✅ **RESOLVED 2026-09-09 (Appendix EU).** The dirty artifacts were the
CORRECT freshly-generated output; the committed versions were the stale ones.
Regenerated and committed. **The guard that stops this recurring now exists:**
`scripts/check_artifacts.py` regenerates all 27 tracked artifacts into a temp
dir and diffs them, and `scripts/git-hooks/pre-commit` runs it with `--staged`.
Its FIRST run found **four more** stale files the audit had missed.

**`scripts/run_checks.py` is now the test suite** `CLAUDE.md` requires:
`15 passed, 0 failed, 0 skipped (of 15)`, exit 0 — the 15th added 2026-09-10,
`ml/train_controller.py`, which now pins the DART invariant (Appendix EV).

| sev | finding | one-line fix |
|---|---|---|
| ~~CRIT~~ **DONE** | regenerated. The guard then found the same drift in `_model`, `_lmlanes` and `_sim` too — four files, not one |
| ~~CRIT~~ **DONE** | regenerated, and `1122.xodr` vendored into `cad/reference/` so it is reproducible on any clone |
| ~~CRIT~~ **DONE** | status block rewritten to 2026-09-09, scale corrected to ~1:14.63, MG90S → MG90D-270. Voice-checked, in band on all 4 metrics |
| ~~HIGH~~ **DONE** | `scripts/check_artifacts.py` + pre-commit `--staged`. Blocking PROVEN by staging a staled file: commit refused, HEAD unchanged |
| ~~HIGH~~ **DONE** | `scripts/run_checks.py`, 14/14 pass, exit 0. (Audit's 28-of-43 was wrong: 37 argparse modules, 14 define one.) ~~`train_controller.py` still has none — open~~ **closed 2026-09-10 (Appendix EV)**: its self_check pins the DART invariant and kills a replay of the 2026-09-07 bug. `diag_copycat.py` still makes the same choice inline, unguarded |
| ~~HIGH~~ **DONE** | now **100755** |
| ~~HIGH~~ **DONE 2026-09-09** | SELFTEST was pinned at a stale **39/39** in ~~four~~ **three** unstruck places (the fourth, `PRD_ROADMAP.md:477`, had already been struck by Appendix ET -- the audit miscounted). All three now point at the board banner rather than carrying a number | struck; `uno_control.ino:10-16` remains the rule |
| ~~MED~~ **DONE** | `TARGET_DASH_CYCLES` retired for a max-blind-gap criterion (1.8 steps vs a 2.0 limit), asserted. Dash geometry unchanged |
| ~~MED~~ **DONE** | re-pointed at the ROAD edge (154.6 mm/side) and now ASSERTED; the accepted 29.6 mm lane shortfall is pinned by a second assert |
| ~~MED~~ **DONE, source only** | cleared at the true top, BEFORE `:529` sets it — the audit's "mirroring :532" would have wiped the bit just set. Compiles 9694 B. **NOT FLASHED** |
| ~~MED~~ **DONE** | now at `.gitignore:57` |

~~Two load-bearing files live OUTSIDE the repo with nothing preserving them.~~
**DONE 2026-09-09: both vendored into `cad/reference/`** as `1122.xodr` and
`figure8.xodr` (space dropped — LaneMaker's Qt dialogs choke on it), with
SHA256s in the record. `rescale_reference_xodr.py:72` repointed, so that
script now runs on a bare clone instead of only on Evan's machine.

**LaneMaker / OpenDRIVE — CLOSED AS A NEGATIVE, DO NOT RE-OPEN
(2026-09-07, Appendices EK–ER):**

`cad/export_xodr.py` emits the figure-8 (`--`), the grid (`--grid`), the grid
with junctions (`--junctions`) and a crash-bisection ladder (`--probe`).
**Everything LOADS and RENDERS. Simulation crashes, and seven hypotheses have
now failed to fix it:** self-link (EC), self-intersection (EC), median
required (EC, re-killed against SIMULATION in EP), U-turns (EH),
roads-too-short (EO/EP), missing `<junction><boundary>` — built, verified and
still crashing (EQ) — and missing `<signalPhase>` — added to 68 of 68
connections, still crashing (ER).

**RESOLUTION: use `~/Downloads/figure 8.xodr` if a simulation visual is ever
wanted.** It is a working figure-8 through a 4-way junction, authored by
LaneMaker itself — our track's exact topology, already simulating. Nothing
needs to be generated for that purpose.

**Continuing would mean** bisecting `figure 8.xodr` toward our generated file
one element at a time, ~6–10 more manual LaneMaker sessions, against a
closed-source Qt binary, for a tool that is off the critical path. **Not
recommended.** The physical track is defined by `cad/track_layout_v2.py` and
`cad/marking_layout.py`, both complete and self-checked, and neither depends
on any of this.

**What the thread DID produce — four pieces of an undocumented vendor format,
derived and verified, reusable if this is ever revisited** (details in
`.claude/project-memory/track.md`): the `side` rule (38/38 segments across
both reference files); the counterclockwise joint→lane boundary walk where
each lane segment is the right-turn kerb return between adjacent arms;
`signalPhase` = one id per arm, 0-based; and straight-through trim =
`connector_length / 24`, machine-precision on 5/5. ⚠️ Turn-connector trims
(0.37–0.49 × lane, never symmetric) were never solved — the exporter uses
0.45 × lane as a marked shortcut.

⚠️ **Appendix EL's "side is underivable" and Appendix EN's "the boundary is
the cause" are both RETRACTED** (EQ). EL hunted positional patterns when the
rule is per-segment semantic; EN read a rescaled copy of Evan's own working
file clearing the crash as isolating the boundary, which it does not.

**Blocked on the order:**

| # | Action | Blocked on |
|---|---|---|
| 6 | **Place the order** (`docs/BOM.md`, ~~**$411.45 + shipping ≈ $424-439**~~ **$422.25 before shipping (2026-10-04 cart review); shipping not re-estimated. BMS confirmed 2026-10-04 (B08HLQQCQJ, re-verified live)**). All six BOM Verify items closed; only #3 above is unconfirmed. | **Evan** |
| 7 | **Bench-measure the real wheel angle with a servo attached** — the sharpened task from Appendices DL/DN/DO. Measure the WHEEL directly at the servo's own limit; do not compute it from the bare-linkage 58°/270° figures. Then re-derive `SERVO_US_SPAN`, whose 10% margin was sized against the OLD rack's hard stops. | parts (servo) |
| 8 | **Confirm the MG90D-270° physically fits the MG90S-sized mount** — one body dimension differs (22.4×12.1×22.8 vs ~22.8×12.2×31 mm). | parts (servo) |
| 9 | **Task 8e: flash and verify the WS2812B firmware.** `uno_control.ino` compiles clean (9680 B, 58 SELFTEST checks) but has never run. Done-check needs both strip segments addressing independently, the LAST pixel of each lit, and `ticks` counting cleanly with indicators blinking. | parts (strip) |

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

✅ **RESOLVED 2026-09-06 (Appendix DQ): the tools are LIVE and verified.**
`mcp__3dstreet__getSessionInfo` returned a real response — build
`2026.8.0+70fef93c`, scene ~~`87740b35-811b-4c80-a384-7adb7ad4742e`~~ **`ac08e443-9733-47aa-bb53-62a032a0d712` as of 2026-09-06 (Appendix DV) — different scene**,
`saved: true`, `isAuthor: true`. All three conditions finally lined up
(server approved · tab paired · session started after both). 26 tools
available (`entityCreate`, `managedStreetCreate`, `takeSnapshot`, `undo`,
etc.).
⚠️ **`saved: true` + `isAuthor: true` means AUTOSAVE IS ON — every mutation
persists to Evan's real cloud scene immediately.** There is no sandbox.
`undo`/`redo` exist; the page's Read-only toggle blocks mutations entirely
if wanted. **The scene is currently EMPTY** — just the three default
containers (`street-container`, `environment`, `reference-layers`),
untitled, no geometry.
*(Original 2026-09-01 diagnosis, kept because it was right and cost three
sessions to find: Evan approved the server and paired the tab, but that
session still saw zero `mcp__3dstreet__*` tools, because **a session's MCP
registry is fixed at startup** — it needed a fresh session with the tab
left open, which is exactly what finally happened.)*

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
| **car width** | ~~**148.25 mm — rear track, WIDEST, governs**~~ **GOVERNANCE FLIPPED 2026-09-05 (Appendix DM): front track is now 155 mm** (up from 107.5, after the steering rebuild — 13-stud rack, Appendix DL) **— exceeds rear (148.25) by 6.75 mm. Front now governs.** Body 135.75 mm is narrower than both. ⚠️ **Real consequence, not just a number**: lane width follows the governing width (2.0×), so lane is now 310 mm. ~~`cad/track_layout_v2.py`'s own self-check FAILS at R=500 — only 90 mm spare against the required 100 mm. Flagged, not patched — see Appendix DM.~~ **FIXED 2026-09-06: spare 110 mm, check PASSES** (root cause was two functions in that file disagreeing about usable width, not the width itself). Both tracks were measured on different dates against different steering states; re-confirm together before freezing anything | Evan, Appendices CI/DM |
| **max steer** | ~~**Mechanical: 58°** ... **Planning/design: capped at 45° for margin**~~ **CORRECTED 2026-09-05 (Appendix DN): 58° (and the ~270° pinion sweep) were BOTH hand-measured with the servo disconnected — they describe the rack's own limit, not what the MG90S (fixed 180° spec, 90° each way) can actually drive.** The rack (135° each way) now out-travels the servo (90° each way) — opposite of the old setup, where both were ~180°. Assuming the same linear ratio this project has always used (unverified): **servo-achievable wheel deviation ≈ 90×(58/135) ≈ 38.7°**, giving `R_min ≈ 232.4 mm`. **45° may not be achievable by this servo at all** — reaching a true 45° needs ~104.7° of pinion rotation, more than the servo's 90° max. 38.7° is an ESTIMATE, not a measurement; the real number needs the actual servo bench-tested at its own limit, not computed from the bare-linkage figures. Both 116.2mm (58° bare-linkage) and 232.4mm (38.7° estimate) stay comfortably inside the frozen 500-670mm corner band. **CANDIDATE SERVO FOUND 2026-09-05 (Appendix DO): HOOYIJ MG90D-270°, $16.99/4-pack, same 20T/4.9mm spline + torque class as MG90S, 135° each way exactly matches the new rack.** Not ordered, not a BOM change yet — `docs/BOM.md` row 7 still names the MG90S | Evan, Appendices BQ/BU/DL/DM/DN/DO |
| lane width | ~~**296.5 mm** = 2.0 x the measured 148.25 mm~~ **310 mm = 2.0 x 155 mm as of 2026-09-05** (front track now governs, Appendix DM). Rule corrected 2026-09-01 — the old fixed-85 mm rule gave 2.31-2.70x, wider than real roads (1.98x) or Duckietown (1.4-1.6x) | `SIM_TRANSFER_SPEC` §3 |
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
> when the turning test is meant.)* ~~The ~330 mm minimum turn radius is
> `wheelbase / tan(max steer)` on an unmeasured 130 mm car width.~~ **STALE
> — car width is 148.25 mm (Appendix CI) and `R_min` is now an ARITHMETIC
> estimate of ~116.2 mm (58° max steer, 13-stud rack, `steering.md`
> Appendix DL), not the old 330 mm placeholder.** Appendix L already ruled
> that corner tiles must not be cut
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
| Drive motor selection | M1.1b | **Done (purchase pending)** | 2026-07-23: ~~Pololu #1093, $23.95~~ **#5159, $29.95** (encoder variant — corrected 2026-09-02 Appendix BO, propagated here 2026-09-03); docs/research/2026-07-23_drive-motor-selection.md |
| Power system selection | M1.1c | **Done (purchase pending)** | 2026-07-23: split source, power bank owned; docs/research/2026-07-23_power-system.md |
| BOM | M2.8 | **BLOCKED-ON-EVAN; re-priced four times** | `docs/BOM.md`, ~~≈$238-248 + $15-25 shipping (≈$253-273 all-in)~~ ~~**$411.45 + shipping ≈ $424-439**~~ **$422.25 before shipping (2026-10-04 cart review): rows 2-3 moved to PiShop, LM2596 + holder substitutes for the Addicore backorders, 26 AWG dropped, XT30 swapped, coupler printed instead of bought** (row 7's servo swapped to the MG90D-270° 2026-09-05, Appendix DP, +$9.00 over the interim $402.45 — the rack now needs 135° each way, past the MG90S's reach, Appendix DN). Row 17 is an **Arduino Uno Evan already owns, $0**. **Row 5 corrected 2026-09-02 to the #5159 ENCODER motor** Evan chose on 2026-08-12 (+$6) and **new row 5b, the #4763 JST SH cable Pololu does not include** (+$3) — Appendix BO. **$200 ceiling breached on every path** |
| Chassis CAD + print | M1 | **Started** | M1.3's two headline numbers closed 2026-09-05 (Appendices DI/DK): pin 4.80mm, axle 5.00mm — pitch-row scale check still open |
| Tolerance coupon | M1.3 | **Pin + axle offsets both closed; pitch check open** | `cad/tolerance_coupon_v1.stl` (pin row PASS @ 4.80mm; axle row FAIL, all 6 too loose) + `cad/tolerance_coupon_v2.stl` (axle sweep 4.80-5.30mm, PASS @ 5.00mm — "3rd smallest is best") + `cad/README.md`. No caliper data on either coupon (fit-by-feel only), pitch-row scale check (beam across holes 1-2, then 1-5) never run |
| Steering coupler (printed) | 8c(ii) | ~~**STL generated, never printed**~~ **v1 PRINTED (by 2026-09-03), axle socket TOO LOOSE (Evan, 2026-10-04); v2 generated, untested** | 2026-09-03, Appendix DG. `cad/servo_lego_coupler_v1.stl` + `scripts/gen_servo_lego_coupler.py` (manifold PASS, volume PASS 1.05e-14, 1152 tris, Ø10 × 16 mm). MG90S Ø4.65 bore → female 5.00 × 2.00 Lego cross socket. Prints NO cross profile (obeys Appendix BV); 20T spline deliberately not modelled (sub-nozzle pitch). ⚠️ **No torque margin claimed** — friction + spline bite, never loaded. Four constants unmeasured; `SOCKET_CLEAR` wanted the M1.3 coupon's data, now printed (2026-09-05) — but the coupon's AXLE row is a free-SPIN fit and the coupler's socket wants a firm GRIP, closer to the coupon's PIN row (4.80mm) in spirit; not yet reconciled, flagged rather than silently reused. PETG not PLA |
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
| Track layout | M1.4 | **v1 + v2 drawn, NOT committed** | 2026-09-01, Appendices AM/AT/AX/AY. `cad/track_layout_v1.py` = figure-8 with a flat causeway bridge + 5 landmarks; `cad/track_layout_v2.py` = 3x3 city grid, 9 intersections, figure-8 route through the centre. ~~8.31 m, 103.5 mm spare at R=500~~ ~~RE-RUN 2026-09-05 ... span 2710 mm, spare only 90 mm at R=500 — UNDER the script's own 100 mm self-check, which now FAILS~~ ~~**CURRENT, real output 2026-09-06 at lane 310 mm: route 8.23 m, pitch 1190 mm, span 2690 mm, spare 110 mm at R=500**~~ (struck 2026-09-09, Appendix ET: wrong in every number — the lane had already moved 310 → 250 mm and nothing propagated it). **CURRENT, real `cad/track_layout_v2.py` stdout 2026-09-09: lane 250 mm (1.613 × the 155 mm car, DELIBERATELY under the 2.0× rule), route 7.51 m, pitch 1100 mm, span 2700 mm of 2800 usable, spare 100 mm at R=500, `self_check: PASS`.** The SVG and JSON had been silently frozen since 2026-09-05 — `main()` runs `self_check()` before it writes, so the failing assert meant no regeneration; the committed JSON still read the old 148.25 mm car. Both regenerated. Print plan, live 2026-09-09: corner arcs 6.28 m, intersection boxes 18.00 m, **122 tiles at 200 mm, ~627 g** of filament, street lines 32.40 m taped not printed (~~10.67 → 11.16 m / 85 → 88 tiles / ~1051 → ~1081 g~~ struck same date, same cause). Corner geometry stays FROZEN until T2 regardless |
| Track: sim rehearsal | — | **IMPOSSIBLE, settled** | 2026-09-01, Appendix AX. gym-donkeycar's protocol has ten message types and none defines a road; `load_scene` picks from 11 prebuilt Unity scenes. A custom track needs a Unity build. Costs little: M3 trains on real laps, not the sim corpus |
| Track surface | T3 | **Decided: hybrid** | 2026-09-01, Appendix AX. NOT 225 printed panels (~12.6 kg, 169-900 h, 225 bed clears, 28 camera-visible seams). Print the 6.28 m of corner arcs + 9.36 m of intersection boxes as ~79 tiles (~970 g); tape the 31.9 m of straight street lines |
| Uno firmware | — | ~~**CONTROL FIRMWARE RUNS ON THE BOARD (2026-09-02)**~~ ~~**2026-10-10: board runs `servo_bench` (FT); uno_control to be re-flashed**~~ ~~**2026-10-13 (HU): uno_control re-flashed - SELFTEST PASS 86/86; backlash compensation (HS) + steering gate (HT).**~~ ~~**2026-10-13 ~14:00 (HW): board runs `servo_bench` for the backlash test.**~~ **2026-10-13 ~14:09 (HY): uno_control re-flashed - backlash 75 us MEASURED (HX), new banner, SELFTEST PASS 86/86. The rest of this row describes older builds.** | Appendices BD/BJ/BO. `firmware/` — `uno_bringup` (board proven), `uno_memtest` (2048 B SRAM, 16.0042 MHz), `uno_echo` (link p99 1.069 ms), `uno_packguard` (SELFTEST 27/27), **`uno_control` (implements `SERIAL_PROTOCOL.md` v0.2: **SELFTEST 49/49, `host_test.py` 13/13 exit 0**, 7888 B flash / 313 B SRAM, loop 2-3 ms; the status LED is quiet on a bench board and loud once a real pack has ever been seen — Appendix CE)** — **CURRENTLY FLASHED, fixed build, as of 2026-09-02 ~19:55 CDT.** Evan had put `uno_packguard` back on it in between, so **read the boot banner, never this line, for what the board is running.** ⚠️ **Watchdog defect found by the daily-audit (BY), fixed (CA): two `millis()` samples per loop iteration made the watchdog trip in the same iteration as every good frame — after the reply was sent, so no status byte ever showed it; a wired car would drive ~2 ms then brake ~48 ms, repeating.** The probe that catches it reads `armed` inside the window; the status-bit check the audit suggested passes on the broken build. `SERIAL_PROTOCOL.md` is no longer design-only. **ACTUATORS UNWIRED** — link + state machine only. ⚠️ **The repo source no longer matches what's flashed, as of 2026-09-03 (Appendix DC): `uno_control.ino`'s lighting path was rewritten for WS2812B (task 8e) after this row's "CURRENTLY FLASHED" build. That rewrite is compiled, not flashed** — the board still runs the 2026-09-02 build described in the rest of this row; SELFTEST 49/49 and 7888 B flash refer to THAT build, not the current source (58 checks, 9680 B, per Appendix DC) |
| Vehicle lighting | — | **Spec written, nothing wired** | 2026-09-01, Appendix AY. `docs/LIGHTING_SPEC.md`. Headlights/tail/DRL/indicators. Only the headlight beam is in the camera's view. ~~Settles the PCA9685.~~ Superseded 2026-09-02 (BC): an **Arduino Uno** takes actuation instead. Turn signals are a THIRD policy head and gate the M3 collection run via PRD task 11b |
| ~~Harness trustworthiness~~ | ~~P6~~ | ~~**OPEN — BLOCKING all closed-loop claims**~~ **STALE ROW, STRUCK 2026-09-02** | ⚠️ **This row contradicted the P6 row above it and was two days out of date.** It is dated 2026-08-11 (Appendix AD, cause unknown); the row above is dated **2026-08-13 (Appendix AI/AJ) and found the cause** — `donkey-generated-track-v0` regenerates the track per launch. **P6 is DONE.** The live rule that survives is narrower: never compare closed-loop numbers ACROSS launches; use `ml/eval_paired.py` |
| Track fabrication | T1-T6 | **Designed, not built** | figure-8; print markings not surface. ~~1.6×2.8 m, 1:14~~ **SUPERSEDED — floor is 3.0 × 3.0 m (Evan, 2026-09-01) and the layout is `cad/track_layout_v2.py` at lane 230 mm / 171 mm spare on the MEASURED 114.75 mm car (2026-09-02, Appendix BO).** T1 scale is CLOSED except its marking table; **T2 still blocks every corner tile** — it needs an empirical turning test on the rolling chassis. `R_min = 0.625 × wheelbase ≈ 116.2 mm` as of 2026-09-05 (58° max steer, 13-stud rack; was `1.600 × wheelbase ≈ 297.5 mm` on the old rack) |

## Hardware & stack facts (from the 2026-07-23 brief — re-verify prices at purchase)

- Pi 5 **4GB, $70** (chosen 2026-07-23 ~20:46, down from 8GB for budget;
  4GB is DonkeyCar's minimum and the board only ever runs inference).
- Camera Module 3 Wide $35 (120° diagonal, rolling shutter — fine at 1-3 m/s)
  **+ a Standard-Mini camera cable (~$2-5)** — the module ships with a
  Standard-Standard cable that does NOT fit the Pi 5's mini 22-pin port.
- Drive: **Pololu ~~#1093~~ #5159 N20 30:1 HP 6V, ~~$23.95~~ $29.95** (encoder variant; chosen 2026-07-23,
  purchase pending). 1000 rpm, 55.9 mN·m stall, 1.6 A stall, 10×12×26 mm,
  3 mm D-shaft. Into the Lego diff via TB6612FNG with **both channels
  paralleled** (2 A cont.) and duty PWM-capped at ~71% of a full 8.4 V pack.
  **All Lego motors were rejected on physics — too slow (≤0.88 m/s).**
  Build HAT rejected (needs 8 V ±10 %, takes the UART, no Trixie support).
  L298N banned. **Drivetrain corrected 2026-09-03 (Appendix CS): Evan's
  actual differential is 20t→28t (N=1.400), not config B's 12t→28t — and
  his tire measures 55.75 mm, not 43.2/62.4 mm.** Real top speed 1.83 m/s
  loaded / 2.09 m/s no-load (≈4.1-4.7 mph) — OVER the 1.0-1.5 m/s target
  band. Accel current 1.24 A (**76% of stall TORQUE**, not of stall current — 1.24/1.6 A is 77.5%; gloss corrected 2026-09-03, Appendix DB); traction
  margin unchanged at 4.7x.
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
- `.claude/project-memory/` — bins. **`gotchas.md` was SPLIT 2026-09-02** (it
  hit 423 lines) and is now a 24-line ROUTER. Read `hardware.md` before any
  build work, `track.md` before track work, `sim-harness.md` before touching the
  simulator or eval harness.
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
- ~~**Car width: measure, don't choose.**~~ **ANSWERED 2026-09-02: 114.75 mm
  MEASURED** (rear tire track). Lane width follows at 229.5 mm; track v2 spare
  went 140 → 171 mm. ~~**Still open: WHEELBASE**~~ **A geometric estimate exists
  2026-09-03: ≈185.95 mm, from Evan's 9.25 in overall wheel-to-wheel length
  minus the front (42.25 mm) and rear (55.75 mm) tire radii — not a direct
  axle-to-axle measurement, see action-table row 3b above.** Still open:
  confirming no part of the assembled car exceeds the tire track. Original
  note kept below.
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
- ✅ ~~**THE 2S PACK HAS NO HARDWARE LOW-VOLTAGE CUTOFF — open safety item**~~ **CLOSED 2026-09-03 (Appendix CK): it was a CATEGORY ERROR, not a sourcing gap.** A charger IC terminates CHARGE and has no discharge-path FET; over-discharge cutoff needs a series FET on the pack OUTPUT, which is a BMS job. Fix is TWO boards: Adeept p0374 stays the USB-C charger, plus **ACEIRMC 2S 8A BMS $9.59, documented cutoff 2.9 V ±0.05 V**, wired between charger and pack. +$9.59. **Caveat (Appendices FA, FE): the wiring doc never actually included the BMS until it was redrawn 2026-10-10, so this "closed" held only on paper for a month.** Original note follows: ⚠️ **THE 2S PACK HAS NO HARDWARE LOW-VOLTAGE CUTOFF**
  (2026-09-02, Appendix BI). BOM row 11's board is titled "BMS" but Adeept
  documents **over-voltage and short-circuit protection only**; over-discharge
  is not listed, and the EVE 25P cells are bare. Below ~2.5 V/cell lithium takes
  permanent capacity loss and can grow internal shorts that become a fire risk
  on the NEXT charge. **A firmware cutoff is implemented and tested**
  (`firmware/uno_packguard/`, SELFTEST 27/27 on hardware) — **but firmware
  cannot guard a pack while the firmware is off.** Close it with a protection
  board that states over-discharge cutoff, or protected cells. BOM Verify
  item 6 has the options. **Evan's call.**
- ⚠️ **THE STEERING COUPLER IS THE HIGHEST-TORQUE JOINT ON THE CAR AND A PRINTED
  ONE FAILS** (2026-09-02, Appendix BV). MG90S stall ~216 mN·m gives SF 0.57–0.96
  against PLA interlayer shear; the MG996R fallback in BOM row 7 is SF 0.12–0.19.
  The drive coupler was carefully shown survivable at SF 2.26–3.77 and **nobody
  ran the same check on the steering side, which sees ~4× the torque.** Grip a
  real Lego axle, never a printed cross profile. **No coupling is chosen.**
- ~~**Pi 5 2GB ($65) or 4GB ($110)?**~~ ✅ **DECIDED 2026-09-03: 4 GB — the 2 GB is SOLD OUT.** It was a $45 PRICE argument, never a capability one; 4 GB is comfortably sufficient and always was. Original reasoning kept: Recommended 2GB — identical silicon, and the 4GB has absorbed every DRAM price rise while the 2GB has absorbed none. Purchase window is now.
- ~~**PWM path: straight-to-GPIO or a PCA9685 breakout?**~~ ~~RESOLVED 2026-09-01 (AY): PCA9685~~ **SUPERSEDED 2026-09-02 (Appendix BC): an ARDUINO UNO Evan already owns** takes motor PWM + servo + 4 light channels, and adds encoder counting and a throttle watchdog the PCA9685 cannot do. $0. BOM row 17; pin map in `firmware/SERIAL_PROTOCOL.md`.
- ~~M1.1 decision gate~~ — **answered 2026-07-23** (see Current state).
- ~~M1.1b drive-motor purchase — research in flight~~ — **resolved
  2026-07-23**; the motor is in the BOM below.
- **THE ORDER (`docs/BOM.md`, ~~$411.45 + shipping = ≈$424-439~~ $422.25 before shipping as of 2026-10-04 — after the Vilros kit, Amazon consolidation, right-sizing bulk items, swapping 8 discrete LEDs for a WS2812B strip, Evan choosing the 144 LED/m density over 60/m (+$4.00), choosing the Adafruit #4252 steering coupling over the free-but-rejected printed option (+$0.75, Appendix DF), and swapping the steering servo to the MG90D-270° once the rack outgrew the MG90S's 90°-each-way reach (+$9.00, Appendix DP)).** Nothing is bought. **Lighting**: WS2812B strip, 2 segments on **D4 and D7** (data is one-way, cut halves cannot share a feed), freeing **D5/D6 — the first spare PWM this design has had**. Encoder-interrupt risk quantified at ~0.027% tick loss for 3 px/segment (Appendix CZ); it scales with pixels per segment, so **cut to pixel count, not length**. **`docs/WIRING_PROTOSHIELD.md` and `firmware/SERIAL_PROTOCOL.md` are now current (Appendix DA)** — the vet found §2.2 naming the wrong motor (#1093) and no strip pins assigned at all. ~~⚠️ **`docs/LIGHTING_SPEC.md` still describes the superseded 8-LED scheme.**~~ **CLOSED same day (Appendix DC): rewritten for WS2812B, 3px/segment, DRL folded into the head pixel only (Evan's calls).** `firmware/uno_control/uno_control.ino`'s `applyLights()` is rewritten too — compiled clean (9680 B flash / 371 B SRAM via `arduino-cli`), **not hardware-verified**, no strip owned. PRD task 8e is now blocked on hardware only, not decisions.
  ⚠️ **TWO NEW SOURCING PROBLEMS, 2026-09-03:** the **EVE 25P cells are SOLD OUT** —
  but do NOT hunt for another 20 A cell, that rating was never load-driven (worst-case
  pack draw ~2.5 A against a 3 A fuse; **real spec is flat-top unprotected 18650,
  ~2500 mAh, ≥5 A continuous**, which is nearly every cell in the class). And **vendor
  consolidation is RESOLVED (Appendix CJ): **NO SINGLE VENDOR EXISTS** — Adafruit 10/22,
  SparkFun 13/22, Pololu 5/22, and the gaps are CATALOG gaps not stock gaps. **Plan for
  three vendors.** ⚠️ **The Pi 5 4 GB is OUT OF STOCK at pishop, SparkFun AND Adafruit-2GB;
  only Adafruit ($130) and CanaKit ($110) have a 4 GB, while pishop has the 2 GB at $65.** **DigiKey confirms it out too (SC1431, 0 in stock) and publishes the only restock date: 180 due 2026-10-05** — which lands AFTER the ~late-September M1 completion that CF's escalation assumed. **DigiKey is cheapest for the camera ($35.00), the cable ($1.00 — a third of pishop) and the Active Cooler ($5.00).**
  ⚠️ **A 2S BMS documenting over-discharge protection exists at NONE of the three** — BOM
  Verify item 6 is now the hardest item to source, not just the most overlooked.
- **COOLING — raised 2026-09-03 and never considered before in this project.**
  Pi 5 soft-throttles at 80 °C, hard at 85 °C, and sits above 85 °C under sustained
  load with no cooling. **The consequence is the 20.00 Hz CONTROL RATE, not a hot
  chip.** Active Cooler $10.95, in stock at pishop.us, **flagged in the BOM but NOT
  added to the total — Evan's call.** `vcgencmd get_throttled` already covers thermal
  in the same bitfield task 10 checks for brownout.
  Everything downstream of M1.5 waits on parts. ✅ **ALL SIX BOM "Verify before
  ordering" items are now CLOSED (2026-09-05, Appendix DJ)** — the last one,
  power bank rating, is **confirmed 5V/3A, 10,000 mAh** (matches the power
  research's own working assumption exactly). Nothing on that checklist
  blocks placing the order anymore.
- ~~**PRINT THE COUPON (M1.3)**~~ **BOTH v1 AND v2 PRINTED AND TESTED, 2026-09-05
  (Appendices DI/DK)** — Bambu P1S, Bambu ABS Black (replaces the PLA/PETG plan
  entirely, Evan's call), 0.4mm nozzle, 0.2mm layers, 2 walls, 10% gyroid, 99%
  shrinkage comp. **Pin holes model at 4.80mm** (v1, bottom of tested range,
  not bracketed). **Rotating axle bores model at 5.00mm** (v2, "3rd smallest
  hole is best" — v1's 5.20-5.70 sweep was entirely too loose). **Both of
  M1.3's headline numbers are closed.** Still open: the pitch-row scale check
  (beam across holes 1-2, then 1-5) has never been run, and no caliper
  measurements exist for either coupon — every verdict is fit-by-feel, not a
  measured offset. Procedure + both result tables: `cad/README.md`.
- ~~**Which printer?**~~ **ANSWERED 2026-09-05: Bambu P1S, Bambu ABS Black.**
- **Ask dad: soldering iron + solder, multimeter, USB SD reader.** Assumed
  owned 2026-08-05 (calipers confirmed). Any "no" is +$8-40 and counts as
  shop tooling, not car BOM — Evan decides whether the $200 ceiling covers it.
- **A1 pre-order checks** (PRD §6b): ~~power-bank label reads 5V/3A~~ ✅ done
  2026-09-05 (Appendix DJ) · ~~count the diff ring teeth~~ ✅ done via
  Appendix CS (20t→28t) · confirm a 12-tooth bevel is in the parts bin —
  **STILL NOT CONFIRMED 2026-09-05: Evan "probably" has one, prints a
  replacement if not.** Not the same difficulty as the coupon/coupler
  prints — a bevel gear's meshing tooth profile is real geometry to get
  right, not a round hole or a socket, so don't assume it's a quick
  `gen_*.py` job if it comes to that ·
  ~~which tires~~ ✅ done via Appendix CS (55.75mm) · re-check prices ✅ done
  2026-08-08, total since moved to ~~$411.45~~ $422.25 (2026-10-04). **Bevel-gear bin check is the
  only item still open, and it's a "probably," not a confirmation.**
- **Open question for Evan:** does "no Lego motors" mean none at all, or
  none of the PF/Powered-Up families? EV3/NXT/9V-Technic motors, if owned,
  would reopen the free-encoder odometry path. Confirm at M1.2 inventory.

---

## Paste-ready prompt for the next session

```
Read, in order:
1. D:\ClaudeCode\Autonomous Car Project\HANDOFF.md  (ONLY live snapshot)
2. PRD_ROADMAP.md (tasks 5-7 carry dated notes from 2026-10-13)
   and docs/ELECTRONICS_LAYOUT.md before ANY tray/deck/wiring work
3. .claude/project-memory/INDEX.md, then ONLY the bins your task touches
   (steering.md before ANY servo/steering work; hardware.md + decisions.md
   before ANY printed-mount work; track.md before track work)

STATE (2026-10-15 ~11:45 CDT). Parts ORDERED; 23 of 24 arrived 2026-10-10
(FI-FL); the camera ARRIVED 2026-10-15 (IX) - all in; PRD task 8 done.
Not yet connected or tested. Paid ~$430 (Evan's recollection, FU).
FIRMWARE: the Uno runs the CURRENT uno_control source - flashed 2026-10-13
~14:09 (HY), boot banner "SERVO WIRED; MOTOR, ENCODER, LEDS, PACK UNWIRED" +
"SELFTEST PASS 86/86". Steering backlash compensation holds the servo 75 us
past each target in the direction of the last move, centre 1525 - both
MEASURED by hand in servo_bench (HX: straight at 1600 from the left, 1450
from the right). The steering gate (HT) moves the servo only in OUT_DRIVE
(armed + pack OK + link alive); with no pack wired the pack reads FAULT, so
ARMED frames CANNOT move the servo on the bench (HW). Evan (HZ): leave the
gate; the frame -> servo test waits for the pack wiring. host_test.py has NOT
been run on this build. Only the servo is wired.
STEERING (HM-HQ): left lock ~450 us is the RACK STOP (first-contact pulse not
measured; firmware safe limit 550); right lock ~2600 us is the servo's end.
PRINTING: EVERY car part is Bambu PETG Translucent, 250 C / 70 C, P1S 0.4,
0.15 mm layers, 2 walls, X-Y hole comp 0 (IC). PETG coupon (IC-IE): row D (the
mounts' exact hole) good at 4.90-5.05 -> pins stay 4.95; collar sits half in
the recess (correct); rows A/B read looser at the same sizes (unexplained);
zip slot 3.5 x 1.8 best. Pocket gauge (IF): holder snug (0.25/side OK), bank
loose only because its edges are rounded (flat from 7 mm up). Servo pilot
1.7 mm confirmed good; Evan has mounted the servo (mount version not stated,
ID). press_shaft (+0.15) is PLA-calibrated only.
PARTS (OpenSCAD in cad/scad/, render_scad.py + probes, check_artifacts):
electronics tray v8 + deck v9 (IA-IK) - side lobes are flat 3 mm plates ON
the frames; bank, holder and Pi on ~4 mm velcro (VELCRO constant, assumed);
14 mm fences; deck at z 46 with the 50 x 34.25 x 12 fuse holder lying on the
bank; Pi brackets 10 mm; Uno standoffs 6 mm (USB-B plug over a pin boss);
rocker hole 21.0; LM2596 pegs 57.5 x 31.5; NO zip ties anywhere. Servo mount
v7, motor mount v6, camera mast v1, fit coupon + pocket gauge. All UNTESTED
at these versions except the coupon and gauge (printed, IC-IF). Slice the
tray and deck with supports OFF (Evan's profile supports bridges).
ELECTRONICS LAYOUT: docs/ELECTRONICS_LAYOUT.md + docs/electronics_layout.svg,
generated and checked by scripts/electronics_layout.py from the LAYOUT lists
in the tray/deck .scad files (14 entries, 0 checks failed); every part Evan
has is accounted for; measured sizes from IH.
RESEARCH this cycle: docs/research/2026-10-12_camera-mast-pose.md and
docs/research/2026-10-12_print-friendly-cad-rules.md (13 ranked rules).
The sim lane ended in a well-instrumented NEGATIVE; LaneMaker/OpenDRIVE is
CLOSED - do not re-open. THE TEST SUITE is scripts/run_checks.py (17/17 on
2026-10-13 - re-run it, never quote it). Push state: run `git fetch` then
`git status -sb`; this file does not record it.

AUDIT BACKLOG: HJ (2026-10-13, 61 findings; its HIGH: ml/splits.py re-draws
the train/val split on any corpus top-up and checkpoints store no corpus id;
its steering-on-DISARMED-frames MED is FIXED in HT). EW (9) and EX (60) are
still unworked; FG's 35-row table has rows 11, 13, 16-35 open and row 14 half
done (checkpoint fingerprints written, never checked).

NEXT ACTIONS, highest value first:
1. PRINT tray v8 + deck v9 (supports OFF) after measuring the velcro pair
   (change VELCRO in both .scad files if it is not ~4 mm). Fit report: rails
   pin onto the frames; lobes sit flat on the frames; bank and holder seat in
   their fences on velcro; deck pins onto the 46 mm posts; Pi brackets, Uno /
   LM2596 pegs, rocker hole; anything rubbing. Record settings + fit.
2. Print / fit what is not yet confirmed: servo mount v7 (if not the mounted
   one), motor mount v6, camera mast v1. Record each.
3. PACK WIRING (unblocks the motor AND the frame -> servo test, HZ):
   DONE 2026-10-14 (IP-IV): MB tapped at the holder's brass rivet (strap not
   reachable), BMS wired B- / MB / fuse -> B+, P+ to P- = 7.21 V. NEXT (IW):
   4 x 190 mm 22 AWG - charger BAT/GND and XT30 both on P+ / P- (two wires
   per pad) - DONE 2026-10-15; charger was wired reversed, fixed (IY); first
   charge stopped early at 3.83 V/cell (IZ), second stopped itself at 8.29 V
   (JA). Charger no-load output test still NOT done - attend every charge.
   Charger board 1 RETIRED (likely damaged by the reversal, JC/JD); board 2
   installed. BMS sits ON the holder (IO). Step 1 DONE: LM2596 4.99 V
   unloaded (JE + hardware.md). POWER ENTRY CHANGED 2026-10-16 (JF): the Uno
   runs on the Pi's USB (plain cable, NOT cut); `+5V2` feeds only servo, strips,
   encoder - never the Uno 5V pin; servo V+ on `+5V2`. NEXT: 1b (plain-cable
   host_test.py), then 2b.
4. Audit HJ's HIGH: ml/splits.py split stability + a corpus id in checkpoints.
5. Couplers: print in PETG and re-test the fit (press_shaft is PLA-only);
   servo coupler v3 untested; none load-tested.
6. Small backlog: firmware/host_test.py docstring and SERIAL_PROTOCOL.md:9
   still say nothing is wired (the servo is); servo_bench prompt says
   "400-2600" (US_MAX is 2800); diag_copycat.py:96-99 DART choice through
   select_actions(); confirm the 12-tooth bevel gear; measure the USB-B plug
   (the layout uses a 16 x 30 x 13 allowance).
7. Evan's call: 98 tracked files carry the local path D:\ClaudeCode\... on the
   PUBLIC remote (95 provenance JSONs; ml/provenance.write_result stores cwd);
   2 HOME-path occurrences in the record. Stop the source and/or rewrite history.

HARD CONSTRAINTS
- Corner geometry FROZEN until T2's empirical turning test.
- No hardware purchase without Evan's explicit go.
- The record is append-only: run `date`, append via
  ~/.claude/skills/project-memory/append-record-entry.js, never pre-cite a letter.
- Physical claims stay honest: unprinted/unfitted = "untested", sim-only = "sim-only".
- Plan-split rule for long tasks (Opus specs, Sonnet codes, Opus re-renders and
  byte-compares); every printed part must pass render_scad.py + check_artifacts.
- Pin/fit sizes live ONLY in cad/scad/lib/lego.scad fit classes.
- Do NOT type a backslash inside a heredoc'd script; heredocs also break on
  quotes - write scripts with the Write tool.
- Use ./.venv/Scripts/python.exe -- bare `python` has no numpy.
- Never `git add -A` / `git add .` - list every path (the settings deny rule is
  GONE per audit HJ, so this is discipline, not enforcement). Leave
  .claude/pm-cadence.json, drift-check.stamp and the *.tmp files out.
- ASCII-only text in any .md you write.
```
