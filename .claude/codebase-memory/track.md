# track.md — Autonomous Car Project

**Split out of `gotchas.md` on 2026-09-02** (Appendix BO). Traps belonging to
the physical track: layout, markings, surface, and what the camera sees of the
environment.

The track's dimensions are driven by the car's MEASURED width — that fact lives
in `hardware.md` (114.75 mm, 2026-09-02), and the generator that consumes it is
`cad/track_layout_v2.py`.

- **3DStreet is a street CROSS-SECTION tool, not a track-geometry tool**
  (assessed 2026-09-01, Appendix AM). It does linear segments plus 90-deg /
  T / dead-end intersections; **no curved streets found**, and it works in
  real-world units (a real lane is 3-3.6 m, this track's is ~0.3 m, roughly
  1/11 — **confirmed exactly 2026-09-06: the derived scale is 1:11.80**,
  see the marking section below). **Good for** marking design, dash
  patterns, sign placement and a
  portfolio render. **Bad for** the figure-8 plan-view geometry, which is
  the actual hard part. Keep the layout in a dimensioned plan. The
  `3dstreet-mcp` server (`.mcp.json`) is a bridge to a LIVE browser tab over
  WebSocket - alpha, no auth token, piggybacks on whichever tab is signed
  in - not a headless generator.
- ⚠️ **THE TAB MUST BE PAIRED BEFORE THE SESSION STARTS. Pairing mid-session
  does NOT work and cannot be recovered from inside the session**
  (2026-09-06, Appendix DT). ✅ **CONFIRMED THE OTHER WAY 2026-09-06
  (Appendix DV): Evan restarted with the tab already paired and all 26
  tools registered on the FIRST ToolSearch.** The rule is now tested in
  both directions, not observed once. Proven, not guessed: Evan paired the tab, the
  page's own feed showed `MCP relay paired` plus four `tools/list:
  Completed`, the MCP server even disconnected and RECONNECTED mid-session —
  and the session still had zero `mcp__3dstreet__*` tools across six
  `ToolSearch` queries. Confirms Appendix DQ (a session's MCP tool registry
  is fixed at startup) from a second direction.
- ⚠️ **The page's `WebMCP active (26 tools)` banner is NOT about Claude
  Code.** WebMCP is the page's primary transport for *agentic browsers*
  (ChatGPT desktop browser, Gemini in Chrome, Chrome 149+). Claude Code uses
  the MCP relay, which the page itself calls the fallback. Do not read '26
  tools' as 'the session has 26 tools'.
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
  Scale is 1:11.80 either way. **Run the generator before claiming a
  layout does or does not fit — it is the authority (Appendix DS).**
- **STOP SIGN placed in the 3DStreet scene 2026-09-06 (Appendix DW):**
  `stop_sign` mixin as a STANDALONE entity (that is what makes it
  relocatable, vs baked into street-generated content), 0.6 m off the lane
  edge, `rotation "0 -90 0"` faces traffic travelling +X. **Relocation
  PROVEN**: one `entityUpdate` moved it 25 m, read back clean, no street
  rebuild. Satisfies Y.3's relocatable requirement IN THE MODEL only —
  the physical mount is unbuilt. ⚠️ **Do NOT size the printed sign from
  the 1:11.80 scale** — Evan decided 2026-08-10 (Appendix Y) on a
  deliberately OVERSIZED, off-scale sign, because pixel share is what the
  training objective responds to. Scale-correct would be 64.6 mm; the
  standing decision is larger on purpose.
- ✅ **OPENDRIVE IS THE WAY AROUND 3DSTREET'S MISSING CURVES (2026-09-06,
  Appendix EA).** LaneMaker (`~/Downloads/LaneMaker_0.9_Win64`) is a Qt5
  GUI whose SampleMaps are `.xodr` — **OpenDRIVE**, plain XML, the ASAM
  standard CARLA/esmini/SUMO read. Its `<planView>` takes `<line>`,
  **`<arc>`**, **`<spiral>`** (clothoid) and `<paramPoly3>`; the samples use
  356 arcs and 286 spirals. So the R=500 corner geometry that 3DStreet
  structurally cannot hold is a NATIVE primitive here.
  - **`cad/export_xodr.py`** emits the driven route as one closed road:
    14 geometries (8 line, 6 arc), full scale by default (x14.6304 → lane
    3.6576 m, R 7.3152 m, route 109.9 m); `--model-scale` for the 2.7 m
    track. Outputs `cad/track_figure8.xodr` + `_model.xodr`.
  - **THE ROUTE HAS 6 CORNERS, NOT 8** — derived in EA, never before.
    Two of its 8 vertices are both `(0,0)`, and the heading does NOT change
    at either: the route runs STRAIGHT THROUGH the centre intersection on
    both passes. Those merge into 2.2 m straights. 3 lefts + 3 rights.
  - ⚠️ **NOT exported: the grid, the 9 intersections, junction records.**
    The road crosses itself with no junction declared — valid OpenDRIVE,
    minimum test of whether LaneMaker loads our geometry.
  - ✅ **LANEMAKER DOES IMPORT .xodr — tested 2026-09-06 (Appendix EB).**
    It parsed the file and named its own blocker:
    `xodr map needs to contain custom LaneProfile!`
  - ⚠️ **EVERY .xodr FOR LANEMAKER NEEDS A `<roadRunnerProfile>` BLOCK** —
    a RoadRunner (MathWorks) vendor extension, NOT standard OpenDRIVE, as
    the LAST child of `<road>`. Grepping the samples for "LaneProfile"
    returns ZERO — the element is named `roadRunnerProfile` (544 hits in
    traffic_test.xodr). Schema: `type_s` = section start with **s in
    CENTIMETRES**; `4294967295` = UINT32_MAX terminator on the `<left>`
    list; `laneCount` = DRIVING lanes only (medians not counted);
    **`offsetX2` = laneOffset / laneWidth * 2**, verified across all 272
    roads. `export_xodr.py` emits it and self-checks the cm unit.
  - ✅ **THE EXPORTER IS VALIDATED AGAINST LANEMAKER (2026-09-06, Appendix
    EC).** `export_xodr.py --probe` writes a 4-rung bisection ladder
    (straight / +arc / +figure-8 / +self-link). **ALL FOUR LOAD.** So
    straights, arcs, a SELF-INTERSECTING road with no junction declared,
    and a road that LINKS TO ITSELF are all accepted — both hypotheses for
    the crash were wrong. Probes 3 and 4 render identically because the
    self-link is topology metadata, not geometry.
  - ⚠️ **The crash was NOT the file content.** `probe_4_closed8.xodr` and
    `track_figure8.xodr` differ only in two `name` attributes; everything
    else hashes identically. Probe 4 loads. Most likely a stale PRE-PROFILE
    chat attachment was opened. **Unconfirmed** — the only untested
    variable is the `name` string containing spaces and a hyphen.
  - **Diagnosed from Windows minidumps**, not guessed:
    `%LOCALAPPDATA%\CrashDumps\LaneMaker.exe.*.dmp`, exception
    **0xC0000409 param 7 = FAST_FAIL_FATAL_APP_EXIT** (MSVC
    `std::terminate`/abort — an unhandled C++ exception, NOT memory
    corruption), identical fault address both times. Parse the
    MINIDUMP_EXCEPTION_STREAM directly; no debugger needed.
  - **THE 3x3 GRID IS EXPORTED TOO (2026-09-07, Appendix ED):**
    `export_xodr.py --grid` -> `cad/track_grid3x3.xodr`. 6 roads, 39.5021 m
    each, pitch 16.0934 m, road 7.3152 m, **9 crossings that are GEOMETRIC
    ONLY** — no junction records, licensed by EC (probe 3 self-intersects
    with no junction and loads). Same pitch/length as the 3DStreet scene,
    so the two representations agree.
  - **PROPER JUNCTIONS EXIST (2026-09-07, Appendix EE):** `--junctions` ->
    `cad/track_grid3x3_junctions.xodr`. 56 roads (12 street segments + 44
    connecting roads), 9 junctions, 32 turn arcs, 44 laneLinks.
  - ✅ **THE KERB RETURN RADIUS RECONCILES THE FIGURE-8 WITH THE GRID.**
    A turn confined to the bare box has R = road/2 - lane/2 = **125 mm**,
    needing **56.1 deg of lock** — past the 38.7 deg the servo reaches, so
    **the car could not turn right**. With junction radius Rt the arcs are
    Rt -/+ lane/2. At **Rt = 500 mm: right 375, left 625, street segments
    100 mm** — which is exactly the "straight between corners"
    `track_layout_v2` reports. **The figure-8's R=500 corners ARE the
    junction turns.** A self-check asserts every radius >= 232.4 mm.
  - ⚠️ **The grid is 91% junction, 9% street** (1000 mm of junction in
    every 1100 mm pitch) — a direct consequence of Rt=500 vs pitch 1100.
  - ✅ **GROUND TRUTH EXISTS: `~/Downloads/1122.xodr`**, a 3x3 grid Evan
    exported FROM LaneMaker (2026-09-07, Appendix EF). Diff against it
    instead of inferring from the SampleMaps.
  - ⚠️ **CONNECTING ROADS MUST BE ONE-WAY.** All 47 of LaneMaker's have
    `<right>` lane -1 + `<center>` lane 0, **NO `<left>` element**,
    `laneOffset = +lane/2`, a **LANE-level `<link>`** inside the lane, and a
    profile with only `<right>`. Mine were two-way — that was the
    ACCESS_VIOLATION. Fixed via `_add_oneway_road()`; **the file now LOADS**
    and connections appear. Pinned by self-check 8e.
  - ❌ ~~a median lane may be required~~ **NO** — probes 1-4 load with a
    1+1 no-median layout. LaneMaker writes a median; it does not demand one.
  - ✅ **`offsetX2 = 0` IS correct for our roads** — it is
    `laneOffset/laneWidth*2`, and ours have `laneOffset = 0`. The
    reference's +/-1 come from ITS reference lines sitting half a lane off
    centre. Do not "fix" this.
  - ⚠️ **STILL BROKEN: connections render only on HOVER, and starting the
    SIMULATION crashes** (`0xC0000409 FAST_FAIL p=7`, an unhandled C++
    exception — a DIFFERENT fault from the load crash, which is fixed).
    Prime suspect: **`<junction><boundary>`, which mine lacks entirely**
    (0 of 9; reference has 5 of 5). Format: **2 segments per ARM**,
    alternating `type="lane"` (a stretch along a CONNECTING road's outer
    edge) with ZERO-LENGTH `type="joint"` on the incoming street.
    Second gap: **LaneMaker INCLUDES U-turns** (its 4-arm junction has
    16 = 4x4 connections); mine excludes them.
  - ✅ **TESTED 2026-09-07 (Appendix EG): simulation WORKS on 1122.xodr.**
    So the fault is OURS, not the tool's.
  - **U-turns added:** LaneMaker emits k arms -> k*k movements. Now **80
    roads, 68 connections** (4x4 + 4x3^2 + 4x2^2). ⚠️ The 24 U-turns are
    **UNDRIVABLE** (radius = lane/2 = 125 mm, under R_min 232.4) — emitted
    for format conformance only; check 8b skips them BY DESIGN.
  - ⚠️ **THE BOUNDARY TRIM CANNOT BE DERIVED, so it is NOT built.**
    Structure is known (2 segments per arm; `type="lane"` on a connecting
    road + zero-length `type="joint"` on the incoming street). But
    junction 0's lane segments run s = 0.948..21.814 on a 22.763 m
    connector — trimmed 0.949 m at each end, and **nothing in the file
    explains 0.949** (not the 3.25 lane, not its half). `side` and
    ordering would also be guessed.
  - **STATUS: everything LOADS and RENDERS; simulation unsupported.**
    NOT on the critical path — the physical track is
    `track_layout_v2.py` + `marking_layout.py`. Recommend banking it.
  - The reference's geometry is **21 line, 21 spiral, 18 arc, 6
    paramPoly3** — spirals are clothoid transitions, which
    `export_xodr.py` does not model at all.
  - ⚠️ **EVERY OpenDRIVE ROAD NEEDS A `<link>`.** The first junction cut
    had 0 of 56 and crashed LaneMaker with `0xC0000005 ACCESS_VIOLATION` at
    an address in the EXE's OWN range (the EB/EC crashes were 0xC0000409 in
    a system DLL — different bug). Junctions pointed at roads; no road
    pointed back. **Connecting roads link to ROADS; street roads link to
    JUNCTIONS.** Also `laneLink from` is -1 or +1 depending on WHICH END of
    the street meets the junction — hardcoding -1 mislabels half of them
    (post-fix split is 22/22). Self-check 8d now pins all of this and is
    proven to fire.
  - ✅ **The R=500 route stays ON the roadway** — measured max offset
    139.4 mm vs the 250 mm half-width, 0 of 780 points off. Near a corner
    the path is carried by the CROSSING street's pavement.
  - ⚠️ **NEITHER xodr FILE SHOWS THE WHOLE TRACK.**
    `track_grid3x3.xodr` = the street NETWORK, square crossings, no corner
    arcs. `track_figure8.xodr` = the driven PATH, with the R=500 corners,
    but no grid. The 3DStreet scene has the same split. Do not call either
    one "the track".
  - `_add_road()` is the ONE road builder for all three callers (figure-8,
    probes, grid). Extracted 2026-09-07 from two near-duplicates; the
    extraction is proven faithful because regenerating every previously
    committed .xodr after it produced BYTE-IDENTICAL files.
  - ⚠️ **STILL NOT UNDERSTOOD:** why `<left>` needs a length-cm section
    PLUS a UINT32_MAX terminator while `<right>` needs one `type_s="0"`.
    No sample road has a 1+1 layout without a median, so ours mirrors road
    0's SHAPE, not a true analogue. **If LaneMaker still refuses: draw any
    road in it, save, and read the profile it writes — ground truth.**
  - LaneMaker internals, from its binary: CGAL (`vcpkg/.../CGAL/
    Intersections_2/`), roads+junctions with overlap resolution, XPath
    parsing (`.//lanes//laneOffset`, `.//lane`).
  - `path_len` CLOSES the loop (`append=p[:1]`); an open `i..i+1` sum misses
    a 5.042 mm closing chord. Compare against `path_len`, never a
    reimplementation of it.
- **3DStreet scene holds the 3x3 grid as of 2026-09-06 (Appendix DZ):**
  6 managed streets, pitch **16.0934 m**, length **39.5 m**, road
  **7.3152 m** — the 1:14.63 full-scale equivalent of `track_layout_v2`.
  ⚠️ **STREET NETWORK ONLY — no corner arcs and no figure-8 route.**
  3DStreet has no curved streets, so the junctions are SQUARE and the
  geometry the car actually follows is absent. Caption it as a network
  diagram, never as the track.
  ⚠️ **IT CONTRADICTS `marking_layout.py` AT EVERY INTERSECTION.** DY says
  the centreline BREAKS at a junction; in the scene the dashes run straight
  through all nine, and there are no stop lines — managed streets are
  independent entities with no intersection-aware marking logic. **Never
  check marking placement against the scene.**
  - `managedStreetCreate` has NO rotation parameter; `entityUpdate` with
    `rotation "0 90 0"` afterwards works and does not move the street.
  - An unrotated street runs its LENGTH along Z (segment children sit at
    +/-1.8288 on X). The plan view suggests the opposite — trust the child
    positions.
  - ⚠️ **After a plan snapshot the camera sticks top-down**: `focus`,
    `birdseye`, `closeup` then all return a byte-identical frame. `closeup`
    worked earlier the same session. Take angled shots BEFORE a plan one.
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
  `PRD_ROADMAP.md`. **The model scale is DERIVED, not chosen: 1:11.80.**
  Appendix L picked the scale (1:14) and derived the lane from it; the lane
  rule that replaced it (`lane = 2.0 x car width`) derives the lane from the
  car, so the scale falls out as `12 ft / 310 mm`. The two agreed at the old
  130 mm car (260.0 mm / 1:14.07 vs the published 261 mm / 1:14), which is
  why the reversal went unnoticed. At 155 mm: normal line 8.61-12.92 mm,
  stop line 25.83-51.67 mm, lane 310 mm.
- **DASH RATIO DECIDED 2026-09-06 (Evan, Appendix DU): `dash:gap = 1:2`** —
  gap twice the dash. At 1:11.80 on the 8.23 m lap that is **68.6 mm dash /
  137.2 mm gap, 40 cycles per lap.** ~~UNRESOLVED — this file, `HANDOFF.md`
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
