# track.md — Autonomous Car Project

**Split out of `gotchas.md` on 2026-09-02** (Appendix BO). Traps belonging to
the physical track: layout, markings, surface, and what the camera sees of the
environment.

The track's dimensions are driven by the car's MEASURED width — that fact lives
in `hardware.md`. ~~114.75 mm, 2026-09-02~~ — **superseded 2026-09-05 (Appendix DM): the generator uses the 155.00 mm FRONT track**, which governs since the 13-stud rack rebuild (rear 148.25 and body 135.75 are both narrower). The generator that consumes it is `cad/track_layout_v2.py`. (Corrected 2026-09-09, Appendix ET.)

- **3DStreet is a street CROSS-SECTION tool, not a track-geometry tool**
  (assessed 2026-09-01, Appendix AM). It does linear segments plus 90-deg /
  T / dead-end intersections; **no curved streets found**, and it works in
  real-world units (a real lane is 3-3.6 m, this track's is ~0.3 m, roughly
  1/15 — ~~confirmed exactly 2026-09-06: the derived scale is 1:11.80~~ **struck 2026-09-09 (Appendix ET): `marking_specs.scale()` returns 14.6304, i.e. 1:14.63**,
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
  ~~Scale is 1:11.80 either way.~~ **Scale is 1:14.63 either way (struck 2026-09-09, ET).** **Run the generator before claiming a
  layout does or does not fit — it is the authority (Appendix DS).**
- **STOP SIGN placed in the 3DStreet scene 2026-09-06 (Appendix DW):**
  `stop_sign` mixin as a STANDALONE entity (that is what makes it
  relocatable, vs baked into street-generated content), 0.6 m off the lane
  edge, `rotation "0 -90 0"` faces traffic travelling +X. **Relocation
  PROVEN**: one `entityUpdate` moved it 25 m, read back clean, no street
  rebuild. Satisfies Y.3's relocatable requirement IN THE MODEL only —
  the physical mount is unbuilt. ⚠️ **Do NOT size the printed sign from
  the ~~1:11.80~~ **1:14.63** scale** — Evan decided 2026-08-10 (Appendix Y) on a
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
  - ❌ ~~a median lane may be required~~ ~~**NO** — probes 1-4 load with a
    1+1 no-median layout.~~ **RE-TESTED AND STILL NO, but the old reason
    was too weak (2026-09-07, Appendix EP).** Probes 1-4 tested LOADING;
    simulating is a different gate. `--lanemaker-lanes` gives street
    roads LaneMaker's exact authored layout — median lane id 1, driving
    id 2, `laneOffset=-lane/2`, `offsetX2=+1/-1`, centre `type=""`,
    junction `laneLink from="2"` — and simulation fails IDENTICALLY
    ("No roads to spawn on!" then the crash). **The median is not the
    gate. Do not re-open this a third time.**
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
  - ⚠️ **THE BOUNDARY TRIM CANNOT BE DERIVED IN FULL, so it is NOT built —
    but one piece of it now IS derived (2026-09-07, Appendix EK).**
    Structure is known (2 segments per arm; `type="lane"` on a connecting
    road + zero-length `type="joint"` on the incoming street).
    **`trim = connector_length / 24`, confirmed to 10-12 significant
    figures on 5/5 STRAIGHT-THROUGH connectors** (roads 4, 2, 20, 25, 49 —
    each a `<line/>` geometry linking one street directly to another; the
    old "0.949 m, unexplained" note was this same number seen without the
    `/24` relationship). ⚠️ Confirmed for ONE trim family only — the other
    10 sampled segments (turn-arc connectors) cluster 1.0-1.55 m and do
    NOT fit `length/24`; no formula found for them. And **our own grid
    mostly can't use even the confirmed half**: 8 of 9 junctions are
    corner/edge (2-3 arms, no opposite-arm pair), so no straight-through
    connector exists there to trim by `/24` at all — only the 1 interior
    4-arm junction has one. `side` and the arm-selection rule (which
    connecting road represents an arm when several exist) are still
    undecoded. **Not implemented** — would still mean guessing on most
    arms. Next real step needs a SECOND reference export from LaneMaker
    (different lane width) to test whether `/24` is a real constant or an
    artifact of this one file — Evan's own LaneMaker session, not
    derivable from data already on disk.
  - ✅ **THE JUNCTIONS HAVE NO PAVED AREA, AND IT IS VISIBLE (2026-09-07,
    Appendix EP).** In a screenshot of our own grid, **8 of 9 junctions
    render as EMPTY background**; only the hovered one shows anything,
    and that is hover-highlighted connector curves, not a surface.
    **`<junction><boundary>` IS the junction's paved-area polygon** —
    ours has 0 of 9, the reference 5 of 5. That single gap explains all
    three symptoms as ONE chain: no polygon → nothing to draw (the
    "renders only on HOVER" symptom recorded since EE) → no drivable
    area ("No roads to spawn on!") → empty result dereferenced
    (`0xC0000409`). ⚠️ Coherent, NOT proven — nobody has built a
    boundary on our geometry and watched it work.
  - ⚠️ **Appendix EO's spawn threshold (1.463, 2.553] m does NOT apply
    to our file.** It was measured only on rescaled copies of
    `1122.xodr`. At 5.000 m street segments (`--sim-min-road 5`, scale
    x50) our grid fails identically. Length is not our gate; EO's
    inference was over-generalised.
  - 🔴 **THREAD CLOSED AS A NEGATIVE, 2026-09-07 (Appendix ER). SEVEN
    hypotheses, seven wrong**: self-link (EC), self-intersection (EC),
    median required (EC, re-killed vs SIMULATION in EP), U-turns (EH),
    roads-too-short (EO/EP), missing `<junction><boundary>` (built and
    verified, EQ), missing `<signalPhase>` (added 68/68, ER). The ONE
    correct finding ever — connecting roads must be one-way (EF) — came
    from diffing Evan's own export. **Do not re-open without new evidence;
    continuing means bisecting `figure 8.xodr` toward our file over ~6-10
    more manual LaneMaker sessions against a closed-source Qt binary.**
  - ✅ **RESOLUTION: use `~/Downloads/figure 8.xodr` if a simulation visual
    is ever wanted.** It is a working figure-8 through a 4-way junction,
    authored by LaneMaker itself — our track's exact topology, already
    simulating. Nothing needs generating for that purpose.
  - ✅ **FOUR PIECES OF THE VENDOR FORMAT ARE NOW DERIVED AND VERIFIED**
    (reusable if this is ever revisited):
    **`side`** — joint at a road's START → `"right"`, at its END → `"left"`;
    every `type="lane"` segment → `"right"`. 38/38 segments, both reference
    files (EQ). ⚠️ Appendix EL called this underivable by hunting POSITIONAL
    patterns; the rule is per-segment semantic.
    **The boundary walk** — a COUNTERCLOCKWISE cycle of joint→lane, where
    each lane segment is the RIGHT-TURN connector between adjacent arms
    (the kerb return); every lane segment's predecessor/successor match its
    neighbouring joints (EQ).
    **`signalPhase`** — one id per ARM, 0-based, keyed on the arm not the
    road (ER).
    **Straight-through trim = `connector_length / 24`**, machine-precision
    5/5 (EK). ⚠️ TURN trims are 0.37-0.49 × lane, never symmetric, no
    formula found — `export_xodr.py` uses 0.45 × lane as a marked shortcut.
  - **STATUS: everything LOADS and RENDERS; simulation unsupported.**
    NOT on the critical path — the physical track is
    `track_layout_v2.py` + `marking_layout.py`. Recommend banking it.
  - **`side` tested against ALL 5 reference junctions (2026-09-07, Appendix
    EL) — no simple positional rule survives**: not "first joint is left"
    (junction 2 breaks it), not "one left per junction" (junction 3 has
    two). Confirms EK's caveat rather than closing it.
  - **`cad/rescale_reference_xodr.py` (2026-09-07, Appendix EM) — Evan's
    call after EK/EL: stop deriving, reuse 1122.xodr's own topology
    UNCHANGED, only rescaled.** Scales every dimensioned OpenDRIVE
    attribute by one factor `k` (geometry x/y/s/length, arc/spiral
    curvature inversely, paramPoly3 coefficients, width/laneOffset/
    elevation polynomials by the correct s-power rule, boundary
    sStart/sEnd) while leaving junctions/connections/boundary/`side`
    byte-identical. Output `cad/track_1122_rescaled.xodr` at 2.7 m
    footprint (k=0.020876) — element-tag counts, `hdg`, and `offsetX2`
    verified identical to the reference; the UINT32_MAX `type_s` sentinel
    verified untouched. **This is EVAN'S test map resized, NOT our 3x3
    figure-8 track** — a positive LaneMaker result would validate the rest
    of the pipeline on a real closed network, not answer the boundary
    question. **Untested — needs Evan's LaneMaker session**, same
    limitation as everything else on this thread: no GUI-automation tool
    exists in this environment to click Start Simulation.
  - ✅ **THE CRASH DID NOT HAPPEN ON A BOUNDARY-CARRYING FILE (2026-09-07,
    Appendix EN) — the single most informative result on this thread.**
    The rescaled copy of `1122.xodr` LOADED AND SIMULATED WITHOUT
    `0xC0000409`. It failed instead on a readable warning
    (`No roads to spawn on! Try creating longer roads.`). Four appendices
    (EE–EH) chased that crash; a file with a complete `<junction><boundary>`
    walked straight past it to spawn logic. **Strong evidence the boundary
    WAS the cause** — but the boundary here was COPIED, not derived, so this
    confirms the diagnosis without supplying the fix. EK/EL's derivation
    problem is untouched.
  - ⚠️ **LANEMAKER REFUSES ROADS THAT ARE TOO SHORT, AND THIS THREATENS OUR
    OWN GEOMETRY — now CONFIRMED, Appendix EO.** Measured in LaneMaker:
    0.213 m, 1.021 m and **1.4630 m all FAIL to spawn**; 2.553 m, 5.105 m
    and 10.210 m all spawn. **Threshold ∈ (1.463 m, 2.553 m], and our
    street segments are exactly 1.4630 m — below it.** The 1.4630 m probe
    (`cad/probe_spawn_kours.xodr`, k=0.143292) was built to match our own
    segment exactly, so this is a direct measurement, not extrapolation.
    ⚠️ **"One long road is enough" is RULED OUT** — that probe carried
    roads up to 7.571 m and still failed. Whether the gate is shortest-road
    length or overall network scale is NOT separable from 3 points; don't
    assert either.
    ⚠️ **IT IS A RATIO PROBLEM, so no uniform scale fixes it**: ours is
    shortest-road/lane = 1.463/3.6576 = **0.40x**; the reference is
    10.210/3.25 = **3.14x**. Same 91%-junction/9%-street fact this file
    already recorded. Options (Appendix EO, neither adopted): **A** export
    the .xodr at ≳x25.5 instead of x14.6304 (lanes render unrealistically
    wide, physical track untouched — RECOMMENDED, LaneMaker is off the
    critical path); **B** raise pitch 1100 → ≥1174.5 mm (span 2700 → 2849,
    spare 151 mm, still fits the 3.0 m floor, but re-derives
    `grid_pitch()`/`best_straight()` and changes the real track for a
    non-critical-path tool).
    **Our street segments are
    `pitch - 2*Rt` = 1100 - 2×500 = 100 mm model = 1.463 m at full scale**,
    far under 10.210 m. **A car may be unspawnable on our grid regardless of
    the boundary** — a blocker invisible until now because every earlier
    attempt crashed before reaching spawn. If confirmed, the fix is
    GEOMETRIC (raise pitch relative to the 500 mm kerb return radius to
    lengthen street segments), not structural.
  - **`No route find form <road>/<laneSectionS>/<lane> @<s> to ...` is
    NORMAL on the reference map, not a defect** (2026-09-07). Seen on a
    k=1.0 round-trip. Cause: `1122.xodr` road 0 has a `predecessor`
    (junction 3) and NO `successor` — a dead-end stub — and no junction
    connection consumes its lane −1, so a route starting there has nowhere
    to go. Logged at `[info]`. **Our 3×3 grid has no stubs** (every street
    joins two junctions), so this specific failure should not appear on our
    geometry.
  - ⚠️ **`rescale_reference_xodr.py` HAD A SILENT DEFECT worth remembering as
    a class**: it scaled no `<object>` element (31 in the reference —
    `subtype="arrow"` / `"stopping-line"`), so at k=0.5 the arrows rendered
    OFF TO THE SIDE, because `t` (lateral offset, ±3.25 = one lane width)
    kept full size on a halved lane — exactly 2× too far out. A full
    element/attribute census found a second miss, `<laneSection s>`. **The
    failure mode was SILENCE**: an unhandled length passes through and lands
    as a misplaced feature, never an error. Now guarded — `ATTR_CLASS`
    classifies every (tag, attribute) pair and `check_coverage()` REFUSES to
    scale a file containing an unclassified one; `self_check()` verifies all
    1202 length-class values moved by exactly k. Guard proven to fire on a
    synthetic `<road superelevation="0.02">`.
  - ⚠️ **NEVER put a period inside an .xodr filename.** `probe_spawn_k0.5.xodr`
    was rejected by LaneMaker's file dialog as an invalid path — Qt splits the
    extension at the FIRST dot, reads `.5.xodr`, and fails the `*.xodr`
    filter. Use `k050` / `k025` style tags.
  - **A k=1.0 round-trip through `rescale_reference_xodr.py` is NUMERICALLY
    IDENTICAL to the reference** — 0 numeric differences across all 4354
    attributes; 1504 differ in float formatting only (`"0"` vs `"0.0"`).
    The transform is proven neutral, so any LaneMaker behaviour seen on a
    rescaled file is the file's own, not the rescaler's.
  - ❌ **U-TURNS DID NOT FIX SIMULATION (2026-09-07, Appendix EH).** Crash
    unchanged: `0xC0000409 FAST_FAIL p=7 @0x7FF888D4527E` — byte-identical
    exception code, parameter AND fault address before and after. Same throw.
  - ⚠️ **FOUR HYPOTHESES, FOUR WRONG:** self-link (killed by probe 4),
    self-intersection (probe 3), median required (probes 1-4), U-turns
    required (EH). The ONE correct finding — connecting roads must be
    one-way — came from diffing the reference file, not from reasoning.
    **Method rule: on this tool, only evidence has ever been right.**
  - `<junction><boundary>` is the only structural difference LEFT, but that
    does **not** make it the cause — it is the last thing VISIBLE in a
    structural diff. Treat building it as one timeboxed EXPERIMENT that may
    not be the fix, never as "the fix".
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
