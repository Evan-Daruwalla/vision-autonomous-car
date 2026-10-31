# Handoff

**Last updated: 2026-10-31 ~16:29 CDT** (records LO-MJ; MJ: shield layout / test card / guides / renders moved to the as-built direct-to-pin wiring, suite 34/34; meter checks A-D PASS per Evan (card version unconfirmed), E not done; MI: servo + strip data wired straight to Uno D7 / D6 / D5, J2 SIG path abandoned, C1 fixed, strip DIN resistors never built (Evan, final); MH: 2026-11-01 soft milestone (M3) NOT met - flagged; paste-ready prompt rewritten; MG: Uno re-flashed with the D7/D6/D5 build; MF: audit MB high + listed meds fixed, landing check caught a SIGTERM deadlock (fixed); ME: firmware + docs moved to the as-built pins servo D7 / strips D6, D5 - compiled, NOT flashed (item 0b); push state: run `git fetch` then `git status -sb`) — this file is the ONLY live snapshot.
History lives in `docs/Project Record — Full Chronological History.md`
(append-only, ~~312 appendices A–KZ~~ ~~323 appendices A-LK as of 2026-10-29~~ ~~327 appendices A-LO~~ ~~328 appendices A-LP~~ ~~329 appendices A-LQ~~ ~~330 appendices A-LR~~ ~~331 appendices A-LS~~ ~~332 appendices A-LT~~ ~~333 appendices A-LU~~ ~~334 appendices A-LV~~ ~~335 appendices A-LW~~ ~~336 appendices A-LX~~ ~~337 appendices A-LY~~ ~~338 appendices A-LZ~~ ~~339 appendices A-MA~~ ~~341 appendices A-MC~~ ~~342 appendices A-MD~~ ~~343 appendices A-ME~~ ~~344 appendices A-MF~~ ~~345 appendices A-MG~~ 346 appendices A-MH (MB = the 2026-10-31 scheduled audit) as of 2026-10-30; BM/BN/BP/BU/CT/CY/DB/DE/DN/EL/EN/EO/ET/EU are corrections to earlier entries). When this file and the record disagree about
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

**2026-10-25 UPDATE (LB-LD) wins over this paragraph where they differ: the proto shield is SOLDERED (untested), and the teleop/recording software is built in `pi/` (fake-hardware verified only) - see the next paragraph.** **CURRENT STATE 2026-10-20 (supersedes the older lines below wherever they disagree; fixes audit KA HIGH #2 / #3):** the Uno runs the current uno_control (SELFTEST PASS 86/86, re-flashed from the Pi 2026-10-16, JQ; host_test all ok from the Pi). The servo is wired and drives the rack; the 2S pack is built and charged (IU-JA); the Pi 5 runs Bookworm and the camera works (JK). NOT yet wired: motor, encoder, LED strips, rocker, proto shield - the shield's hole-by-hole layout is ready and checked (KG), nothing soldered. Tray v11 / deck v13 / camera mast v1 are designed and checked, UNPRINTED. **2026-10-20 evening (KI, KJ):** the shield, layout and pack diagrams are all-bold with zero text overlaps, enforced by `scripts/svg_text_overlap.py` (in run_checks, 19 pass); the shield map embeds a 3D render of the INTENDED finished board (`scripts/shield_render3d.py`, untested against a real build) and draws w3/w4/w5 as their step-6 L-routes from a `via` list in `docs/shield_layout.json`. **2026-10-21/22 (KK-KX):** shield SVG audited (4 of 8 socket arrows pointed to the wrong Uno header - fixed); C1 now stands UPRIGHT (build-step change, KQ); bench guides added - docs/SHIELD_SOLDER_GUIDE.md, docs/shield_build_guide.svg (LEGO-style), docs/shield_how_it_works.svg (current paths); strips named left (D4) / right (D7) like the firmware (KX). Still nothing soldered. The paste-ready prompt at the end is the short current summary.

**2026-10-30 (LQ, PC-side, nothing on the Pi yet):** off-car Pi session software ready: `teleop.py --fake-uno` (real camera, fake Uno), `preflight.py --no-uno`, `autopilot.py --bench` + `export_onnx.py --untrained` (Pi latency), and a guard so episodes recorded on fake hardware are FAILed by verify_real and skipped by bc_real. ~~Next: Evan runs pi/README.md "Off-car session" (HANDOFF item 0a-off).~~ **DONE same day on the real Pi (LR):** Pi re-flashed (key-only SSH), preflight --no-uno PASS after 2 fixes (pyserial, picamera2 fps=), camera 20 fps full FOV, autopilot p95 1.40 ms, pad/deadman OK by Evan, fake-guard FAILs a real Pi episode. OPEN: ~~get_throttled 0x50000 (check the Pi supply).~~ LS/LT: ~~the Anker A1275 bank~~ the Pi's current supply (NOT the bank, LT; a 'battery backup', LU) sags to 4.52 V under full load (4.535 V and 4/12 readings without the USB-C extension, LU). **RESOLVED for the bench (LV):** on a wall charger it holds 5.11-5.15 V, throttled 0x0 - the backup was the cause. NEW: 77.9 C under all-core load (throttle at 80 C) on a BARE board (LW) - fit the Vilros kit fan case (already owned) and re-test. ~~**LX: the Anker bank (car's planned Pi supply) also sags (5/12, low 4.539 V, 3 A mode)** - re-test it with a different cable; if it still sags, the car needs a stiffer 5 V source (Evan's call)~~ **LY: RESOLVED - with a new cable the bank holds 4.97-5.08 V, 0x0; the OLD cable caused all the sags.** Retire that cable; fan case required (79.6 C bare) - but the Vilros case slot is for PCIe, not the camera: case OR camera until Evan modifies it (LZ; bench runs bare - MA measured real teleop bare at 45-47 C, throttled 0x0, so that is fine); the 600 mA USB cap for Uno+servo is untested (under-voltage + throttling live) - re-test with a short 3 A+ USB-C cable; if it still sags, the car's Pi supply needs a decision. Suite 33/33.

**2026-10-29 (LF-LK, all PC-side, nothing on the Pi):** M3 software exists and is tested on synthetic data only: `ml/bc_real.py` (BC trainer for pi/recorder episodes; BCNet 134,552 params), `ml/export_onnx.py` (parity 1.8e-07), AUTO mode in teleop (`pi/autopilot.py`, pad override wins), `ml/verify_real.py` (run before training), `docs/DATA_COLLECTION.md` (session protocol), `pi/deploy.sh` + `pi/preflight.py` (first Pi session), protocol rule 3 + Uno reconnect. Stable train/val split by episode id (audit HJ HIGH closed in code; ~~re-run ml/preprocess.py to use it~~ 2026-10-30 drift fix: the re-run was done in LN and is byte-identical plus ids, but the *_ids.npy are NOT installed - existing checkpoints were trained on the legacy split, so install them only with a retrain or an evaluator legacy fallback). C1 upright clears the wiring space by only +1.2 mm (layout check). LM2596: measured 4.95 V (JE) vs 4.99 V restated (JF/JR) - meter it to settle. Suite ~~32/32~~ 33/33 (LN).

**2026-10-22..25 (LB-LD):** Evan SOLDERED the shield (all wiring done, UNTESTED - no meter checks or power yet): L2/9-L2/10 bridge added after photo review; C1 hangs on long bare legs (re-seat upright or sleeve + glue); servo signal path incomplete - the orange female-male jumper sits on J2's SIG pin, so either fit a pin at L1/-3 + the L1/-2-L1/-3 bridge, or (bench) wire the servo plug with 3 jumpers (signal male-male to D9, V and GND male-female to J2 middle/bottom; advice recorded in LF). **Teleop + recording stack BUILT (LD):** custom Python in `pi/` (DonkeyCar dropped), Xbox pad in the laptop browser via SSH tunnel, npz recorder in the ml/ format; suite 26 pass; verified on fake hardware + browser only - NOTHING run on the Pi yet (Pi was unreachable from the PC). Lights postponed until after 2026-11-01.

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

*(2026-10-30: the old ~140-line table was moved verbatim into the record (the HANDOFF-trim entry after LL). The ONE live list is NEXT ACTIONS in the paste-ready prompt at the end of this file.)*

Still-open rows carried over from the old table (needs Evan or parts):
- Pitch-row scale check + caliper the printed coupons (last open piece of M1.3).
- Confirm a 12-tooth bevel gear is in the parts bin.
- Bench-measure the real wheel angle with the servo attached; confirm the MG90D-270 fits its mount.
- Task 8e: flash and verify the WS2812B lighting firmware (postponed with lights until after 2026-11-01).

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

**Compute:** *(SUPERSEDED 2026-09-03: the Vilros 4 GB starter kit was bought, $179.99, BOM row 1; audit MB)* recommend the **Pi 5 2GB at $65**, not the 4GB at $110 — identical
silicon, and DonkeyCar's "4GB minimum" is an unjustified recommendation (its
`pi` extra installs tflite-runtime, not TensorFlow; a 512 MB Zero 2 W already
drives autonomously). Full brief:
`docs/research/2026-08-12_onboard-compute-selection.md`. Whole-landscape
follow-up (BeagleY-AI, x86, phone, off-board WiFi):
`docs/research/2026-08-12_pi5-alternatives.md`. **Evan's call.**

---

## Track layout — IN PROGRESS, and the geometry is frozen

Evan is designing the street layout in **3dstreet.app**; ~~`.mcp.json` wires the
`3dstreet-mcp` server (project scope).~~ (2026-10-31: entry removed from `.mcp.json` - audit MB, Evan.) ~~**The `claude` CLI is not on PATH
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
| Electronics + teleop | M2 | ~~**Not started**~~ **In progress (2026-10-31, audit MB)** | everything bought; shield soldered, UNTESTED; teleop stack built and run on the Pi off-car (LD, LR); firmware re-flash pending (ME) |
| Behavioral cloning | M3 | ~~**Not started**~~ **Software built, no real data (2026-10-31, audit MB)** | bc_real / export_onnx / autopilot exist, tested on synthetic data (LJ-LK); Pi latency p95 1.40 ms (LR); no laps recorded |
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

- Pi 5 **4GB, $70** *(bought 2026-09-03 as the Vilros 4 GB kit, $179.99, BOM row 1; audit MB)* (chosen 2026-07-23 ~20:46, down from 8GB for budget;
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
- Software: ~~DonkeyCar 5.3.0 (Pi 5 OK, 64-bit Bookworm, Py 3.11, TF/Keras
  trainer) for plumbing~~ (superseded 2026-10-25, LD: custom `pi/` stack); custom PyTorch models are the portfolio line.
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
  MEASURED** (rear tire track). *(SUPERSEDED 2026-09-05: the front track is 155 mm and governs - Appendix DM, cad/vehicle_envelope.py:68; audit MB)* Lane width follows at 229.5 mm; track v2 spare
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
1. D:\ClaudeCode\Autonomous Car Project\HANDOFF.md  (ONLY live snapshot; this prompt is its end)
2. PRD_ROADMAP.md (M2/M3 rows; tasks 9-12 carry dated notes)
3. Before ANY shield work: docs/shield_test_card.png (meter checks A-E, in order),
   docs/shield_layout.json (holes, pins, steps 0-8), docs/WIRING_PROTOSHIELD.md.
   Before ANY Pi work: pi/README.md ("Off-car session" + "On-Pi bench checklist").
   Before ANY tray/deck/mast work: docs/ELECTRONICS_LAYOUT.md.
4. .claude/project-memory/important.md, INDEX.md, then ONLY the bins your task
   touches (hardware-shield-wiring.md, firmware-traps.md, hardware-power.md,
   data.md, testing.md ...).

STATE (2026-10-31 ~15:43 CDT; record entries LO-MG cover 2026-10-30..31):
- UNO: re-flashed 2026-10-31 with uno_control at the AS-BUILT pin map - servo D7,
  left strip D6, right strip D5 (D4, D9 spare; NO spare PWM pin left). 11658 B,
  read-back verified, banner + SELFTEST PASS 86/86 (MG). Encoder D2/D3, motor
  D8/D10/D11/D12, pack sense A0 unchanged. Read the banner before trusting firmware.
- SHIELD: soldered, UNTESTED (no meter checks, never powered). ~~Two known fixes
  before any power (record LC): (1) the servo jumper's female end sits on J2's SIG
  pin, so the servo has nowhere to plug - fix the signal path; (2) C1 hangs on bare
  legs - re-seat it upright.~~ **MI (Evan, FINAL): C1 fixed (method + height not
  stated); servo signal goes STRAIGHT into Uno D7 (J2 SIG path abandoned; V+/GND
  assumed on J2 middle/bottom, JP1 top = Uno 5V - unconfirmed); strip DIN goes
  STRAIGHT into D6 (left) / D5 (right) when lights are wired. The 2 x 200 ohm DIN
  resistors were NEVER built - add 400 ohm in each DIN jumper before any strip
  is plugged in.** The shield should be OFF the Uno (the flash procedure took it off -
  confirm). ~~Wiring as built: shield->Uno Dupont wires on D7 / D6 / D5 (MD).~~
  ~~STALE vs as-built: test card section C rows D7->J2, L3/12->D6, L3/13->D5;
  shield_layout.json DIN note + step 7; SHIELD_SOLDER_GUIDE step 7.~~ MJ: all
  updated to as-built (only docs/shield_bottom_grid.jpg still shows old wires).
  **MJ: meter checks A-D PASS (Evan); which card version he used is unconfirmed
  (old section C rows cannot pass on MI wiring). Shield still never powered.**
- PI 5: re-flashed 2026-10-30 (old password lost): Raspberry Pi OS Lite Bookworm,
  Python 3.11.2, `ssh ed@ed-pi5.local` with PUBLIC-KEY ONLY (PC key
  ~/.ssh/id_ed25519). apt python3-picamera2 (0.3.31) + python3-venv installed;
  `bash pi/deploy.sh` done; onnxruntime 1.31.1 in ~/car/venv. A re-flash wipes all
  of that. MEASURED ON THE PI (LR-MA): preflight --no-uno PASS; camera 20 fps,
  full FOV (ScalerCrop 4608x2592); autopilot predict p95 1.40 ms (untrained BCNet,
  upper bound); pad, arm/disarm and deadman work (Evan, by eye); real teleop on the
  BARE board plateaus 45-47 C.
- POWER (LS-LY): every under-voltage seen was a bad USB-C cable, not the supplies.
  The Anker A1275 bank (the car's planned Pi supply, 3 A mode) holds 4.97-5.08 V
  under full load on a good cable. The old cable must never be used on the Pi.
  In 3 A mode the Pi caps USB peripherals at 600 mA total - the Uno + TB6612 logic
  + servo all draw through it (JF/JR); UNTESTED until the Uno is connected.
- COOLING: the Vilros kit fan case's ribbon slot fits the PCIe connector, not the
  camera - Evan will cut the case. Bench runs bare (fine, MA); the car needs cooling.
- SOFTWARE (all PC-side, synthetic data unless stated): teleop (fake/real camera,
  --fake-uno, auto port detect ttyACM*/ttyUSB*, disarms on ST_WATCHDOG, SIGTERM
  saves the episode), recorder, verify_real (FAILs fake-hardware episodes),
  bc_real, export_onnx, autopilot --bench. Audit MB's high + listed meds fixed
  (MF); the train/val split stays LEGACY until *_ids.npy is installed together
  with a retrain - check_corpus refuses mismatches.
- NOT WIRED / NOT DONE: motor, encoder, LED strips, rocker; no meter checks; no
  laps; no trained real-car model. M2 in progress, M3 software-only.
- DEADLINE: the 2026-11-01 soft milestone (SIM-POC + M3) is NOT met - M3 needs real
  laps. Hard deadline: Regular Decision ~2027-01-01..15.
- UNCOMMITTED BY CHOICE: docs/shield_bottom_grid.jpg (board photo with the ROW/COL
  grid + pin labels; Evan has not said public or local).
TEST SUITE: scripts/run_checks.py (34 on 2026-10-31) - re-run it, never quote it.
Push state: `git fetch` then `git status -sb`.

NEXT ACTIONS, highest value first (all need Evan at the bench):
1. ~~Fix the servo signal path + re-seat C1 (record LC).~~ DONE/REPLACED by MI
   (direct-to-pin wiring; C1 fixed). On the card, check D7 socket -> servo
   signal lead (BEEP) instead of D7 -> J2; skip the two ~400 ohm strip rows.
2. ~~Meter test card sections A-D (power OFF), then~~ A-D PASS (MJ). Next: wire
   the power path (step 2b, W8-W14; read the rocker's DC rating first; meter the
   LM2596 output alone before W14 reaches J5), then card section E (first
   power-up; write down the J3 voltage - settles LM2596 4.95 vs 4.99 V).
3. Power build checks: XT30 -> rocker -> VBAT (rocker OFF = 0 V; polarity +8.x V);
   charger board 2 no-load test (8.4 V OK, >= 8.6 V reject).
4. Shield back on the Uno, Uno on the Pi's USB, then the on-car session:
   deploy -> preflight (must PASS) -> pi/README.md bench checklist (servo sign,
   camera orientation, deadman with the real Uno; --bench, NO --max-throttle until
   the motor is wired and the car is on a stand). Watch the 600 mA USB cap.
5. Laps per docs/DATA_COLLECTION.md -> verify_real -> bc_real -> export_onnx ->
   AUTO on the stand (M3 done-check).
Alongside: print tray v11 + deck v13 (fit report + printer settings in the
record); cut the case slot (photo + slot size); 12-tooth bevel gear; USB-B plug
size. Claude, once unblocked: C1 height in scripts/electronics_layout.py; a 30 s+
episode for the long-run frame-gap %.

HARD CONSTRAINTS
- Start every reply with "Evan". Commit only when asked; push only when told;
  no Co-Authored-By lines.
- Corner geometry FROZEN until T2's empirical turning test. LaneMaker /
  OpenDRIVE CLOSED.
- No hardware purchase without Evan's explicit go.
- The record is append-only: run `date` first, append via
  ~/.claude/skills/project-memory/append-record-entry.js, never pre-cite a letter.
- Physical claims stay honest: unprinted/unfitted/unpowered = "untested".
- Never power the shield (USB or pack) before the meter checks pass; flash the Uno
  with the shield OFF.
- Plan-split rule for long tasks (Opus specs and decides, Sonnet codes, Opus
  re-runs checks and reads diffs).
- Every printed part passes render_scad.py + check_artifacts; every layout
  change passes scripts/electronics_layout.py; every shield change passes
  scripts/shield_holemap.py (then re-run scripts/shield_render3d.py); every
  diagram change passes scripts/svg_text_overlap.py (0 overlaps).
- Never use `sed -i` on files here (it silently changes CRLF/LF) - use a
  Python script or the Edit tool. Use ./.venv/Scripts/python.exe.
- Never `git add -A` / `git add .` - list every path. Leave
  .claude/pm-cadence.json, drift-check.stamp, the *.tmp files and
  firmware/uno_control/build/ out.
- Flash with `arduino-cli upload -t` (read-back verify); the plain upload does not verify.
- ASCII-only text in any .md you write.
```
