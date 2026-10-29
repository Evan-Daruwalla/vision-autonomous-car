# track.md — Autonomous Car Project

**Split out of `gotchas.md` on 2026-09-02** (Appendix BO). Traps belonging to
the physical track: layout, markings, surface, and what the camera sees of the
environment.

The track's dimensions are driven by the car's MEASURED width — that fact lives
in `hardware.md`. ~~114.75 mm, 2026-09-02~~ — **superseded 2026-09-05 (Appendix DM): the generator uses the 155.00 mm FRONT track**, which governs since the 13-stud rack rebuild (rear 148.25 and body 135.75 are both narrower). The generator that consumes it is `cad/track_layout_v2.py`. (Corrected 2026-09-09, Appendix ET.)

- 3DStreet / OpenDRIVE / LaneMaker material (thread CLOSED as a negative, moved 2026-10-29) lives in `track-xodr-closed.md`.

- ✅ **DECIDED 2026-09-06 (Evan, Appendix DX): TWO LANES, 250 mm each,
  road 500 mm, `LANE_TO_CAR = 1.613`.** Deliberately under
  `SIM_TRANSFER_SPEC` s3's 2.0x rule: at 2.0x the road is 620 mm and the
  3x3 grid fits ONLY at R=500, committing frozen corner geometry before
  T2. At 250 mm/lane **R=550 fits too**. 1.613x is inside Duckietown's
  measured 1.4-1.6x band. Real output: span 2700 mm, spare 100 mm,
  straight 100 mm, lap **7.51 m** (was 8.23 single-lane), `self_check:
  PASS`. **R=600 now REFUSES** — it fitted at one lane; that is the second
  lane's price, and the self-check pins it.
  ⚠️ **CORNERING CLEARANCE IS NOW 29.6 mm/side, BELOW the 50 mm
  `MIN_SIDE_CLEARANCE` EST** (off-tracking eats 35.9 mm at the measured
  185.95 mm wheelbase at R=500). It was 59.6 mm at a 310 mm lane. Nothing
  asserts against that constant so no check fails — `vehicle_envelope.py`
  just prints TOO LONG on every wheelbase row. **Open for Evan to
  revisit.**
  ⚠️ **`lane` and `road` are now SEPARATE everywhere** (`LANE` = one
  direction, `ROAD = LANES * LANE` = what the grid geometry consumes).
  One variable meaning both is what caused the DV misreading and the DW
  arithmetic error. Do not re-merge them.
  ⚠️ **Model scale moved 1:11.80 -> 1:14.63** — near the PRD's original
  1:14 **by coincidence, not vindication**; 1:14 was chosen against a
  130 mm estimate, 1:14.63 is derived from a measured 155 mm car.
  ⚠️ **The dashed-EDGE deviation from DV is DELETED** — two lanes give a
  real centreline, so only DU's ratio deviation remains.
- ~~**ONE LANE OR TWO IS AN OPEN CHOICE, not a constraint (2026-09-06,
  Appendix DW — CORRECTS DV).**~~ **CLOSED by DX above.** The track is BUILT single-lane (310 mm
  road; `SIM_TRANSFER_SPEC` s3's lane:vehicle = 2.0x makes 310 mm ONE lane,
  and `track_layout_v2.py` uses `lane` as the road's TOTAL width). DV
  claimed two lanes "would not fit at all" — **wrong.** Real output of
  `track_layout_v2.py --car-width 0.310`: **span 2700 mm, spare 100 mm,
  self_check PASS.** The error was holding PITCH fixed; `best_straight`
  shrinks the straight (190 -> 40 mm) to protect SPARE_MIN. Two lanes cost
  a **14% shorter lap (8.23 -> 7.03 m)** and nearly all remaining straight,
  but buy back a real centreline and delete the dashed-edge deviation.
  ~~Scale is 1:11.80 either way.~~ **Scale is 1:14.63 either way (struck 2026-09-09, ET).** **Run the generator before claiming a
  layout does or does not fit — it is the authority (Appendix DS).**
- **MARKING + SUBSTRATE LAYOUT: `cad/marking_layout.py`** (2026-09-06,
  Appendix DY). Owns no dimensions — geometry from `track_layout_v2`, dims
  from `marking_specs`, drift-guarded against both.
  - **THERE ARE TWO TILINGS and only one was ever counted.** Substrate
    panels (foam board) vs printed marking strips. **The seam rule
    constrains the SUBSTRATE**; `print_plan`'s 122 counts STRIPS — so the
    rule was enforced by nothing until now. Now satisfied by construction:
    strips run ALONG travel, 2 per 500 mm road, and **the one longitudinal
    seam lands on the centreline and is covered by it**. Intersections are
    single uncut 500 mm squares.
  - Centreline BREAKS at every intersection (MUTCD). 12 runs, 7200 mm,
    36 dashes.
  - **Stop lines on EVERY approach of every driven intersection (28), or
    none** — a painted stop line is as much a positional giveaway as a
    fixed sign, so a subset would reintroduce the leak Y.3 closes.
  - The 2 undriven intersections `(-1.1,-1.1)` and `(1.1,1.1)` are NOT
    painted. ⚠️ The streets still cross there — small peripheral domain gap.
- ⚠️ **THE DASH TARGET IS BASED ON A FALSE ASSUMPTION (Appendix DY, OPEN).**
  `TARGET_DASH_CYCLES = 40` divided the full 7.51 m route by the cycle,
  assuming the centreline runs through intersections. It does not.
  **53% of the route (4000 mm) is inside a box**, so a lap delivers **18.7
  cycles, not 40** — under half the target that justified deviating from
  MUTCD's ratio at all. Accept 18.7, or shrink the cycle to ~87.5 mm
  (dash 29.2 / gap 58.3). **Evan's call, not decided.**
- ⚠️ **`MARK_W` WAS 25 mm, 2.4-3.6x the DERIVED 6.94-10.42 mm** — deleted
  2026-09-06, now sourced from `marking_specs`. **Filament 1506 g -> 627 g.**
  Every filament figure quoted before Appendix DY used the 25 mm estimate;
  the hybrid-vs-225-panels conclusion is unaffected (627 g vs ~12,600 g).
- **MARKING SPECS ARE NOW A RUNNABLE SCRIPT: `cad/marking_specs.py`**
  (2026-09-06, Appendix DT), replacing the stale hand table in
  `PRD_ROADMAP.md`. **The model scale is DERIVED, not chosen: ~~1:11.80~~ 1:14.63** (struck 2026-09-09, Appendix ET — `marking_specs.scale()` returns 14.6304 and the dash table below was computed from the stale figure).
  Appendix L picked the scale (1:14) and derived the lane from it; the lane
  rule that replaced it (`lane = 2.0 x car width`) derives the lane from the
  car, so the scale falls out as `12 ft / 310 mm`. The two agreed at the old
  130 mm car (260.0 mm / 1:14.07 vs the published 261 mm / 1:14), which is
  why the reversal went unnoticed. ~~At 155 mm: normal line 8.61-12.92 mm, stop line 25.83-51.67 mm, lane 310 mm.~~ **STRUCK 2026-09-09 (Appendix ET) — those are the old single-lane 1:11.80 values. Live `cad/marking_specs.py` gives: lane 250.0 mm per direction (road 500 mm, 1.613 × the 155 mm car, deliberately under the 2.0× rule), normal line 6.94-10.42 mm, stop line 20.83-41.67 mm, scale 1:14.63.**
- **DASH RATIO DECIDED 2026-09-06 (Evan, Appendix DU): `dash:gap = 1:2`** —
  gap twice the dash. ~~At 1:11.80 on the 8.23 m lap that is 68.6 mm dash / 137.2 mm gap, 40 cycles per lap.~~ **RE-DERIVED 2026-09-09 (Appendix ET) from live output: at 1:14.63 the dash is 62.6 mm / gap 125.2 mm (cycle 187.8 mm), 36 dashes over 12 runs / 7200 mm. And the cycle count is NOT 40 — `marking_layout.py` computes 18.7 per lap, because 4000 mm of the 7507 mm route (53%) is inside intersection boxes that carry no centreline. ~~`marking_specs.py:274` still PRINTS '40 cycles per lap' as fact; that string is false and the decision is OPEN.~~ **CLOSED 2026-09-09 (Appendix EU): Evan ACCEPTED 18.7. `TARGET_DASH_CYCLES` is retired for a max-blind-gap criterion -- 1.8 control steps against a 2.0 limit -- which `marking_specs.py` now ASSERTS at both ends. No script prints '40 cycles per lap' any more; dash geometry is unchanged.** ~~UNRESOLVED — this file, `HANDOFF.md`
  and Appendix L all said "Duckietown uses ~2:1" and none said which side
  was which~~ closed. Keep the reason on the record: MUTCD's is dash:gap =
  1:3, and **Appendix L's own worked example (60/180 mm) is 1:3** — it never
  applied the 2:1 it had just introduced, so the appendix contradicted
  itself and the contradiction propagated into two live docs for a month.
  1:2 is the reading that makes the deviation do its job: MUTCD's 1:3 was
  rejected for giving too FEW dashes at this scale, so the replacement had
  to be denser. **Documented deviation, not MUTCD compliance.**
- **CORNER GEOMETRY IS FROZEN until the T2 turning test** (Appendix L, AM.2)
  — **still true 2026-09-05 even though every input to the formula below is
  now measured or estimated from real numbers, and those numbers keep
  moving.** Minimum turn radius = wheelbase / tan(max steer). ~~330 mm
  ESTIMATE, width/wheelbase/steer all unmeasured~~ superseded piece by
  piece: wheelbase estimated 185.95 mm (`steering.md`, Appendix DD/DE), max
  steer 58° on the current 13-stud rack, hand-measured with the servo
  DISCONNECTED (Appendix DL) — ~~capped 45° for planning margin (Appendix
  DM)~~ **CORRECTED same day (Appendix DN): the MG90S is fixed at 90° each
  way and is now out-travelled by the rack (135° each way), so 58° is the
  rack's limit, not the servo's, and 45° may not be achievable at all.
  Servo-achievable ESTIMATE (unverified): ~38.7°.** Giving bare-linkage
  **R_min ~ 116.2 mm**, servo-estimate **R_min ~ 232.4 mm**. Both
  comfortably under the 330 mm estimate on TURN RADIUS. **But car width
  ALSO changed the same day** — ~~148.25 mm rear track governs~~ **front
  track is now 155 mm and governs instead (Appendix DM)** — and that pushes
  lane width to 310 mm. ~~which makes the FLOOR-FIT tight: `cad/
  track_layout_v2.py`'s own 100 mm safety-margin self-check now FAILS at
  R=500 (only 90 mm spare)~~ **CLOSED 2026-09-06 — span 2690 mm, spare
  110 mm, self-check PASSES.** The failure was two functions in that file
  disagreeing about usable width, not the car outgrowing the floor; see
  `hardware.md` for the mechanism. ⚠️ **Still true at the other end of the
  frozen band: at R=600 the straight is already 0 mm and spare is 90 mm,
  under the 100 mm reserve with nothing left to shrink.** Turn radius has
  slack; floor space does not.
  **None of this unfreezes corner geometry.** A geometric estimate from real
  measurements is still not the same claim as T2's empirical test on the
  rolling chassis, and both the steering number and the car width have now
  changed while the mechanism was still being built out — cutting or
  printing corner tiles before T2 still risks a track sized for numbers
  that move again before the car is done.
- **Track: print MARKINGS, not the road surface** (2026-08-05). Full-surface
  printing is ~6.4 kg / ~150-250 h for a minimum loop vs ~0.15 kg / ~6 h for
  markings — 97% less for identical camera input, because at 120×160 the
  camera sees markings, not road. Substrate is dark matte foam board /
  coroplast. Don't let a future session "improve" this back to printed tiles.
- **Track layout must be a FIGURE-8, not an oval** (2026-08-05). A one-handed
  loop teaches the BC model "always steer left" — perfect on the training
  track, useless elsewhere. The figure-8 also provides the intersection for
  the stop sign.
- **A seam running perpendicular to travel reads as a stop bar** to the
  model. Run tile seams parallel to travel where possible (2026-08-05).
- **Lock the camera pitch before data collection and record the angle** —
  changing it mid-dataset silently splits the data into two incompatible
  distributions. Vary LIGHTING across sessions on purpose (real-world domain
  randomization); never vary the camera geometry (2026-08-05).
- **Glare:** glossy plastic under room lighting produces specular highlights
  that wash out markings. Matte everything; if printing surface pieces, print
  face-down on a textured plate (2026-08-05).
- **A stop sign is provably unlearnable by plain BC** (2026-08-05). Stopped
  at the line the image is identical whether to wait or go, so the action
  depends on history, which π(action|image) cannot express (frame-stacking
  gives ~0.2 s at 20 Hz; a stop is 2-3 s). This is a FEATURE of the plan —
  it is the M4 world-model showcase, since the RSSM/MDN-RNN has recurrent
  state. Traffic lights are the opposite: memoryless-learnable (state is
  visible in the frame) but need hardware.
