# Camera mast pose - height, pitch, fore-aft and stiffness from the sim training data

**Date:** 2026-10-12 (~21:34 CDT). **For:** Evan, designing the camera mast mount
(tray/deck v2, record GX open requirement). **Question:** where should the
Camera Module 3 Wide sit (height, pitch, fore-aft) and what must the mast
provide, so the real images reproduce what the sim-trained models saw?

## TL;DR

1. **No mount pose reproduces the sim's images directly (null H3 survived).**
   The sim camera has a 90 deg VERTICAL FOV; the Module 3 Wide has 67 deg
   (vendor spec, read verbatim; not yet measured on our unit). The best direct fit (pitch 22.65 deg, lens
   104 mm) still misses by 9.2 px RMS on a 160x120 frame; matching the
   horizon row instead (the old SIM_TRANSFER_SPEC mount target) is worse,
   13-17 px.
2. **The exact route: put the lens at the sim camera's SCALED HEIGHT, then
   remap in software.** With the same camera centre, real-to-sim is a pure
   rotation + lens remap, exact at the matched height for every point
   (road, and cones/signs IF they are lane-scaled too); each mm of height
   error costs ~0.2 px at the bottom row. Scaled height = 0.435 x lane width
   = **109 mm lens centre above the floor** (108-109 from the corpus; up to
   ~6 mm LOWER if the 250 mm lane is measured edge-to-edge of the markings -
   undefined in the repo, see Thin / missing).
3. **Pitch 28-30 deg down** (plateau 27.9-30.0): the real frame then covers
   92-96% of the sim's road pixels (rows >= 42); the uncovered part is the
   far lateral corners (real H FOV 99-102 deg vs sim 106).
4. **Fore-aft: lens at or slightly ahead of the front axle**, centred, so no
   wheel or body part enters the frame (the sim frames show none). This
   cannot also match the sim's camera-to-rear-axle lever (0.33-0.36 lane
   widths); a known, accepted mismatch.
5. **Mast:** pinned (not friction) pitch with 20-35 deg range, repeatable to
   about +/-0.3 deg; first natural frequency well above the <= 11 Hz
   drivetrain excitation (rule of thumb >= 35-50 Hz); exposure capped near
   1 ms (forward-motion blur ~1.2 px per ms at the bottom row; the sim has
   none); autofocus LOCKED (motorised lens, focus range ~5 cm to infinity).

## Method

Desk + computation. Project evidence first (SIM_TRANSFER_SPEC sections 4-5,
record AI/AR, `ml/diag_camera_pose.py`); a NEW measurement on the existing
corpus (lane-width-vs-row profile, below); primary sources read as raw text:
the simulator's Unity source (tawnkramer/sdsandbox master, ec04c400, raw
GitHub files) and the Raspberry Pi documentation repo (raw asciidoc). Pose
fits are pinhole geometry in a scratch script (not committed). Limitations:
no real camera exists yet (in shipping), so no real frame, no lens-distortion
calibration, no vibration measurement; the lane-line positions inside the
sim's road texture were not read.

Hypotheses fixed BEFORE collection:
- H1: the corpus lane-width profile is linear in row with its zero at the
  horizon row (42 +/- 2), so lane-width / camera-height is measurable.
  Dies if non-linear or the zero sits far from row 42.
- H2: the Module 3 Wide vertical FOV is ~67 deg, so a horizon-row match means
  ~11 deg pitch, not 16.3. Dies if an official mode has V FOV >= 85 deg.
- H3 (null): no pose reproduces the full ground-to-image map. Dies if a
  numeric search finds a pose with near-zero error.

Phase effects (2026-10-12):
  8.5 verify   - caught a sign error in my own coverage computation (max on
                 the search boundary; fixed, self-check added: horizon row
                 41.95 as predicted); verified the agent's sim-prefab lines
                 and the FOV verbatim; downgraded the lane-width-definition
                 claim to an open uncertainty.
  10.5 assess  - downgraded 3 claims (F2 "partly independent" -> consistency
                 only; "official spec, verified" -> vendor, unmeasured;
                 "exact for every point" -> exact at the matched height,
                 lane-scaled props); added 4 limitations; corrected 2
                 numbers (wheel 8.0 Hz -> 4.0-8.0 Hz range; height range
                 now carries the lane-definition caveat); one collection
                 round run (filter sensitivity, focus range). See the
                 section at the end.

## Findings

### F1. The sim lane is 2.30 camera-heights wide (H1 survived)

New measurement, `donkey-generated-roads-v0` corpus (27 episodes, every 10th
frame, 3,187 frames). Per frame and per row 55-115: column of the yellow
centre line and of the nearest white line to its right (the car drives the
right lane; frames show yellow left, white right). For flat ground the
lateral offset cancels and the lane's pixel width is linear in row:
du(r) = (W/h) cos(pitch) (f_h/f_v) (r - r_horizon).

- 100 frames passed (>= 30 rows detected, fit RMS < 1.5 px); slope p50
  2.2244 px/row (p10-p90 2.181-2.281).
- Zero crossing of the free fit: p50 row **42.36** (p25-p75 41.91-43.02),
  against the sky-boundary horizon **41.97** (record AR). Two independent
  observables agree within 0.4 row: H1 survives, and 16.3 deg is the
  effective in-world pitch.
- With the zero fixed at 41.97: **W/h = 2.2971** (IQR 2.2906-2.3107), i.e.
  **h_sim = 0.4353 x lane** (free fit: 0.4315).
- Biases: yaw makes each row read W/cos(yaw) (small, overestimates W);
  only 205 of 3,187 frames had >= 30 rows with both lines detected
  (selected toward clean straights).
- Filter sensitivity (run after the cold assessment): dropping the fit-RMS
  cut entirely (all 205 profiles) gives W/h 2.3216 (vs 2.3175) and zero row
  42.39 (vs 42.36). The 1.5 px cut did not shape the answer.

### F2. The sim's own source is consistent (NOT an independent check)

Read from raw `sdsim/Assets/Prefabs/Objects/Donkey_new_phys.prefab` (the car
`_controllers.prefab` line 82 instantiates in the generated-roads scene):
- `CameraSensor` line 3222: `m_LocalPosition: {x: 0, y: 1.1203952, z: 0.5528488}`;
  line 3221: `m_LocalRotation: {x: 0.13052624, ...}` = 15.0 deg pitch
  (2 x asin 0.1305); line 3254: `field of view: 90`.
- Wheels: `m_Radius: 0.32`, collider centres y -0.171 (line 2102), so the
  camera sits **1.61-1.73 units** above the ground contact (agent's
  derivation; bracket from suspension travel 0.1).
- Road: `RoadBuilder.cs` line 12 `roadWidth` is a HALF width (lines
  196-197); `_controllers.prefab` line 145 `roadWidth: 5` -> 10 units full.
- Consistency only: the lane of 3.70-3.97 units is this height TIMES F1's
  W/h, so it restates F1; all it shows is that F1 does not put the lane
  outside the 10-unit road. An independent check needs the line positions
  in the road texture (not read).
- **Discrepancy kept, not averaged:** prefab pitch 15.0 deg vs measured
  in-world 16.3 deg. Likely car-body pitch on its suspension (unverified).
  The images were taken at the measured 16.3, so that is the value used.

### F3. The Module 3 Wide cannot match the sim's FOV (H2 survived)

Raspberry Pi documentation, `hardware_specification.adoc` (raw): Camera
Module 3 Wide - focal length 2.75 mm, sensor image area 6.45 x 3.63 mm
(16:9, 4608 x 2592), horizontal FoV 102 deg, **vertical FoV 67 deg**. The
sim's 90 is vertical (record AR). Full-FOV capture resized to 160x120 gives
pinhole f_h 68.2 / f_v 90.9 px (sim: 60 / 60). The record's earlier "matches
within 2-4 deg" (AI) compared horizontal and diagonal only. Pinhole check:
2 atan(1.815/2.75) = 66.8 deg matches the vertical 67; the horizontal gives
99.0 vs the spec's 102, which suggests mild distortion along the long axis
(calibrate; not measured). Focus: motorised, "Approx 5 cm to inf" (same
page) - the nearest ground in frame is ~123 mm away, inside range.

Consequence for the old mount target ("horizon on row 42"): with f_v 90.9
that is a **10.9 deg** pitch, not 16.3, and it is a poor match (F4).

### F4. Direct-match poses all miss (H3 survived)

Every sim pixel in rows 50-119 back-projected to the ground (h_sim = 1),
re-projected through the real intrinsics at candidate poses; RMS pixel
error, 160x120 frame; real height scaled by the lane (h_sim -> 108.8 mm):

| target | pitch | lens height | RMS error |
|---|---|---|---|
| least squares, all ground pixels | 22.65 deg | 104 mm | 9.2 px |
| keep sim pitch 16.3 | 16.3 deg | 82 mm | 10.5 px |
| horizon row 42, best height | 10.9 deg | 65 mm | 13.0 px |
| horizon row + lateral scale | 10.9 deg | 84 mm | 17.4 px |

Algebra says why: a ground-plane image map has three free scale conditions
(horizon row, lateral scale, longitudinal scale) and a mount has two knobs
(height, pitch); with f_h/f_v fixed by the lens, all three cannot hold.

### F5. The exact route: same camera centre + rotation remap

If the real lens sits where the scaled sim camera sat (109 mm, lane-scaled),
the real-to-sim image map is K_sim R K_real^-1 (after undistorting the real
lens) - exact for every 3D point, independent of depth. Pitch is then free
and only sets coverage of the sim view (sim rows >= 42 = ground):

| real pitch | coverage, rows >= 42 | rows >= 60 |
|---|---|---|
| 16.3 | 64-69% | 57-62% |
| 22.0 | 77-81% | 74-78% |
| 25.0 | 84-88% | 84-88% |
| **27.9-30.0** | **92-96%** | **95-98%** |

(Ranges: pinhole-from-focal vs spec-FOV intrinsics.) The sky above sim row
~35 is not covered at these pitches; it carries no road.

### F6. Fore-aft and body visibility

At 109 mm and ~29 deg, the frame's bottom edge looks 62 deg down and its
top edge ~5 deg above level. The front tyre tops (84.5 mm, front tyre radius
42.25) are ~24 mm below the lens; they stay out of frame only if the lens
is within ~13 mm (24.3 / tan 62.2) behind their highest forward point, or
they fall outside the ~+/-50 deg horizontal half-angle. So: **lens over or
just ahead of the front axle**, and EVERYTHING ahead of the lens (steering
parts, frame, deck, the mast's own bracket) must stay below a 62 deg line
down from the lens. A mast cantilevered forward to get there fights the
stiffness target (F7): brace it back to the frame. The sim camera sits
0.5528 + 0.765 = 1.318 units ahead of the rear axle (prefab, F2); divided by
the lane 3.70-3.97 units that is 0.33-0.36 lane widths = 83-89 mm on this
car - mid-car, where the front tyres would very likely show. The real mount
will be ~0.74 lane widths ahead (186 mm wheelbase / 250 mm lane). This changes how steering
moves the image relative to the sim; real-lap BC training absorbs it.

### F7. Blur and stiffness budget (derived, unsourced rules flagged)

- Forward-motion blur at 1.401 m/s, bottom row: **1.2 px per ms** of
  exposure (120-row frame). The sim renders none. Cap exposure near 1 ms
  (more light or gain indoors).
- Pitch error moves rows by f_v x angle: 1 px (120 rows) = 0.63 deg; one row
  of the 64x64 model input = 1.18 deg. Budget **+/-0.3 deg**, static and
  under vibration, and calibrate the real pitch from a photo, never from
  the CAD angle.
- Height error: moving the lens 3 mm changes the bottom-row ground angle by
  58 x 3 / (58^2 + 109^2) = 0.65 deg ~ 1 px (less higher up). Hence the
  +/-3 mm tolerance in the recommendation.
- Excitation at 1.401 m/s: the repo's 55.75 mm rear tyre figure is used as a
  RADIUS in HANDOFF's wheelbase arithmetic but called "the tire measures"
  elsewhere, so rear wheel 4.0 Hz (radius) to 8.0 Hz (diameter); front
  (radius 42.25) 5.3 Hz; diff input x1.4 = 5.6-11.2 Hz. Rule of thumb
  (unsourced): first mast resonance >= 3-5x the top of that, i.e. >= 35-50
  Hz: short, triangulated, pinned at two or more points.
- Focus: lock it (manual lens position). A motorised lens hunting during a
  run changes the focal length the remap assumes.

## Recommendation (ranked)

1. **Lens 109 mm above the floor (+/-3 mm), pitch 28-30 deg down, over or
   just ahead of the front axle, on the centreline; software remap to the
   sim view.** Exact for all points; 92-96% coverage. Costs a calibration
   (lens distortion + measured pitch) and a remap step in the pipeline.
2. **No remap: lens 104 mm, pitch 22.65 deg.** Best direct match, still
   9.2 px RMS; nothing to calibrate.
3. **Re-collect the sim at the real camera's intrinsics** (cam_config fov 67
   vertical, a 16:9 image squashed to 160x120, rot_x set to the real pitch).
   Exact by construction; invalidates the corpus and every trained model.

Option 1 and 2 share the hardware: a mast at ~104-109 mm with 20-35 deg of
pinned pitch serves both, so the mount does not need to wait for the
software choice.

## Verification table (load-bearing claims)

| claim | source | verdict |
|---|---|---|
| Module 3 Wide V FoV 67, H 102, f 2.75, area 6.45 x 3.63 | RPi docs raw adoc | VERIFIED-VERBATIM |
| sim camera y 1.1203952, rot x 0.13052624, fov 90 | sdsandbox raw prefab lines 3221-3254 | VERIFIED-VERBATIM (re-fetched by me after the agent) |
| wheel radius 0.32, collider y -0.171 | same prefab, lines 2116, 2102 | VERIFIED-VERBATIM |
| roadWidth half-width; 5 in the scene car prefab | RoadBuilder.cs 12, 196-197; _controllers.prefab 145 | VERIFIED-VERBATIM |
| generated-roads uses Donkey_new_phys (carPrefab guid) | _controllers.prefab line 82 + agent's guid lookup | CLOSE-PARAPHRASE (guid -> file mapping agent-reported, not re-checked) |
| sim fov is vertical, horizon row 41.97 | record AR (project measurement) | project evidence |
| W/h 2.2971 | this brief, F1 (new measurement) | computed, single method |
| real lane 250 mm per direction | cad/track_layout_v2.py stdout | project evidence |
| Module 3 Wide focus motorised, ~5 cm to infinity | RPi docs raw adoc (Focus, Focus range rows) | VERIFIED-VERBATIM |

## Numbers register

| number | claims | source | date | interest class | verdict |
|---|---|---|---|---|---|
| 67 deg / 102 deg | Module 3 Wide V / H FoV | Raspberry Pi docs | read 2026-10-12 | VENDOR-SELF-REPORTED | verbatim |
| 2.75 mm, 6.45 x 3.63 mm | focal, sensor area | Raspberry Pi docs | read 2026-10-12 | VENDOR-SELF-REPORTED | verbatim |
| 1.1203952 / 15.0 deg / 90 | sim camera y / pitch / fov | sdsandbox source | master ec04c400 (2025-10-06) | INDEPENDENT (the sim itself) | verbatim |
| 1.61-1.73 units | sim camera height over ground | derived from prefab | 2026-10-12 | derived | arithmetic |
| 2.2971 (IQR 2.2906-2.3107) | sim lane / camera height | corpus, this brief | 2026-10-12 | INDEPENDENT (own data) | computed |
| 42.36 vs 41.97 | lane-zero row vs horizon row | corpus / AR | 2026-10-12 / 2026-09-01 | INDEPENDENT | computed |
| 109 mm | scaled lens height | 0.4353 x 250 | 2026-10-12 | derived | arithmetic |
| 27.9-30.0 deg, 92-96% | pitch plateau, coverage | scratch geometry | 2026-10-12 | derived | computed (sign self-checked) |
| 9.2 px @ 22.65 deg / 104 mm | best direct match | scratch geometry | 2026-10-12 | derived | computed |
| 1.2 px/ms | bottom-row blur at 1.401 m/s | scratch geometry | 2026-10-12 | derived | computed |
| 35-50 Hz | mast resonance target | rule of thumb | - | UNVERIFIABLE | unsourced |

Structural checks: the headline height (F1) and its cross-check (F2) come
from different sources (own corpus vs sim source) but F2 can only bound the
sim lane, not pin it - so the height rests on one measurement. Vendor
numbers are 2 of the load-bearing set (the FOV), not a majority.

## Thin / missing

- **Real lane width definition.** `cad/marking_specs.py` and
  `track_layout_v2.py` give "250 mm per direction" with no statement of
  centre-to-centre vs edge-to-edge of the markings. F1 measured line
  CENTRES. The height scales 1:1 with this: a 15 mm line would move it by
  up to ~6% (about 6 mm). Searched: grep for line width / centre-to-centre
  / edge line in both files (only "2 edge lines" in a length count).
- **Sim lane lines in the texture.** Not read; would turn F2 into a fully
  independent height check. Searched by the agent: lane / laneWidth /
  marker in RoadBuilder, PathManager, CarPath, RoadPrefab, scene,
  _controllers - none.
- **Real lens distortion.** H FoV from the focal length is 99.0 deg vs the
  spec's 102, so the lens is not pinhole; a checkerboard calibration is
  needed for the remap. Nothing measured (camera in shipping).
- **Why prefab 15.0 vs in-world 16.3.** Not traced (suspension pitch is a
  guess).
- **Sim binary version vs source commit.** Prefab values are stable from
  2021-12 to master (agent's history check), but no 22.x tag was mapped.
- **Minimum exposure / readout time of the IMX708** - not looked up.
- **Mast stiffness numbers** - no measurement, no source; rule of thumb only.
- **H2 had a weak falsifier.** "An official mode with V FoV >= 85" cannot
  happen (modes only crop a 3.63 mm-tall sensor behind a 2.75 mm lens). The
  real test is measuring the FoV of our unit when it arrives.
- **Model tolerance never measured.** Nobody warped corpus frames by known
  pitch/height errors to see how much the trained encoder/controller cares;
  the +/-0.3 deg and +/-3 mm budgets are geometric (about 1 px), not
  model-derived.
- **Colour, exposure, texture gap** (real floor, tape, lighting vs Unity) -
  out of scope here, and likely larger than any geometry residual.
- **Tyre size definition** (radius vs diameter of the 55.75 mm figure) -
  ambiguous in the repo; only affects the excitation estimate.

## What would change this

- A real-lane-width definition that is edge-to-edge (height drops up to ~6%).
- A real frame showing the front tyres at the recommended fore-aft spot
  (move forward or mask).
- Evan choosing option 3 (re-collect the sim): then any sensible pose works
  and height/pitch become free design choices.
- A measured sim lane in texture units that disagrees with 3.70-3.97.

## Sources

- Raspberry Pi documentation, `documentation/asciidoc/accessories/camera/hardware_specification.adoc`,
  github.com/raspberrypi/documentation (master), raw text read 2026-10-12.
- tawnkramer/sdsandbox, master ec04c400f045222375ec82e649bb051fb17aad41 (2025-10-06):
  `sdsim/Assets/Prefabs/Objects/Donkey_new_phys.prefab`,
  `sdsim/Assets/Scripts/RoadBuilder.cs`, `sdsim/Assets/Prefabs/Scripts/_controllers.prefab`,
  `sdsim/Assets/Scripts/camera/CameraSensor.cs`; raw text read 2026-10-12.
- Project: `docs/SIM_TRANSFER_SPEC.md` sections 4-5; record Appendices AI, AR;
  `ml/diag_camera_pose.py`; `cad/track_layout_v2.py` stdout (2026-10-12);
  `donkey-generated-roads-v0` corpus under the SIM-POC data directory.

## Cold assessment (stage 10.5, fresh agent, brief-only input)

The reviewer saw only this draft. Its findings and what was done:

1. F2 restated F1 (lane = prefab height x F1's W/h) - ACCEPTED, F2
   retitled "consistency, not independent". The horizon (AR) and the lane
   zero crossing (F1) are different observables from the same corpus.
2. Optics all from one vendor page, disclosed only in the register -
   ACCEPTED, TL;DR now says "vendor spec, not yet measured on our unit".
3. H2's falsifier could not fire; H1 might be selected by the fit filter -
   H2 ACCEPTED (Thin / missing). H1 TESTED in the one extra round: no
   filter -> W/h 2.3216, zero row 42.39; the result stands.
4. No real-camera measurement, no texture read - ACCEPTED (limitations;
   the camera is in shipping).
5. Missing items: scaled props, height parallax, focus lock / minimum focus,
   colour gap, model tolerance, parts other than tyres ahead of the lens,
   wheel frequency, 0.33-0.36 derivation - all ADDED or CORRECTED.
   One correction to the reviewer: its 3 mm parallax figure (~1.4 deg,
   ~2 px) is about 2x too large; 58 x 3 / (58^2 + 109^2) = 0.65 deg ~ 1 px.
6. Over-confidence in "exact for every point" and "+/-3 mm" next to a 6 mm
   lane-definition swing - ACCEPTED, both reworded.
