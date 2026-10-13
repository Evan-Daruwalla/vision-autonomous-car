# Print-friendly CAD rules for the printed Lego-Technic mounts

**Date:** 2026-10-12 (~23:14 CDT). **For:** Evan, and every `cad/scad/*.scad`
part plus `cad/scad/lib/lego.scad`. **Question:** which design rules make
these OpenSCAD parts print right on a Bambu P1S in PLA (0.4 mm nozzle) the
first time - hole and pin clearances, hole orientation, overhangs, walls,
first layer, strength orientation and mesh hygiene - so that fits stop being
found one reprint at a time? **Trigger:** servo mount v6 printed with pin
holes too tight at 4.875 mm (record HH); HG moved every part to 4.95.

## TL;DR

1. **Printed holes come out undersized, by an amount that belongs to the
   printer + filament + slicer settings, so the fix is a CALIBRATED
   clearance per fit type, not a universal number.** H1 is supported for
   VERTICAL holes in the literature; its rival (first-layer flare) was argued
   away from geometry, never measured on our parts. Vertical
   PLA holes in a peer-reviewed study were 0.12-0.20 mm under at 0.2 mm
   layers (6-10 mm holes) and 0.15-0.36 mm under for 4.5 mm holes at small
   inclines. This project's two PLA fits on this P1S (motor coupler fits at
   +0.15; pin holes too tight at +0.075) are ONE confounded source - same
   printer, filament and unknown slicer profile, tuned in sequence, and a 3 mm
   D-bore is not a 4.95 round bore. **4.95 (+0.15) is consistent with them
   but NOT established - UNTESTED.**
2. **Compensate in ONE place.** Bambu Studio's X-Y hole compensation grows
   holes by 2x the entered value. If it is non-zero in Evan's profile, every
   fit number in this repo is confounded. **His setting is not known -
   that is the first thing to check.**
3. The first-layer flare (elephant's foot) "directly affects fit" (Bambu);
   the P-series profile sets 0.15 mm compensation (Bambu release notes). Our
   Lego-shaped holes already dodge it: a 6.2 x 0.8 recess sits at the bed
   face, so the 4.95 bore never touches layer 1.
4. Layers are the weak direction: upright PLA tensile bars were 36% weaker
   than flat ones (55.49 vs 35.52 MPa). Keep pin loads in the layer plane
   (vertical pin holes do that); the camera mast's uprights bend across
   layers and are the part to watch.
5. **Source concentration:** most rule-of-thumb numbers (0.3 mm sliding
   clearance, 45 deg overhangs, wall widths, elephant-foot values) are
   Bambu/Prusa vendor guidance; the 0.4-0.5 mm chamfer is Opus's judgment
   with no source.
6. Thirteen concrete rules follow (section "Rules"), ranked by how much rework
   each prevents.

## Method

Desk research, read at source. Two parallel agents (Sonnet) searched (1)
official Bambu / OrcaSlicer / Prusa documentation and (2) peer-reviewed
studies plus the OpenSCAD manual and nophead's polyholes post; every quote
they returned was taken from page text they fetched themselves. Opus then
re-fetched each load-bearing claim by a different call (curl + HTML strip,
Crossref API, PDF text, and the browser pane for MDPI) - see the
verification table. Project evidence: cad/README.md (ABS coupons),
hardware.md (motor coupler fits), records GF/FQ/FS/HH/HE. Limitations: no
new print or measurement was made; the settings of the MOUNT prints are not
recorded (record FR holds the couplers' profile: P1S, PLA, 0.1 mm, 2 walls,
solid - not confirmed for the mounts); no PLA data exists in the sources for
horizontal holes near 5 mm. UPDATE 2026-10-13 (record HK): Evan's X-Y hole
compensation is 0 mm, so the slicer does not resize holes.

Hypotheses fixed BEFORE collection:
- H1: FDM holes print undersized by a printer/material-specific amount ->
  calibrate a clearance per fit type. Rival: the tightness is mainly the
  first-layer flare / hole mouth, fixed by a chamfer or elephant-foot
  compensation instead of a bigger bore.
- H2: vertical holes (axis along Z) are more accurate and rounder than
  horizontal ones; horizontal holes need a teardrop / flat roof.
- H3: parts are weakest across layers -> carry load in the layer plane.

Phase effects (2026-10-12):
  8.5 verify   - 18 load-bearing claims in the verification table: 16
                 re-read by Opus at source and present, 2 agent-read only
                 (marked CLOSE-PARAPHRASE); 2 more numbers in the register
                 (Prusa 0.2 mm elephant foot, Prusa wall widths) are also
                 agent-read only - 4 in all (count corrected 2026-10-13
                 after the daily audit, record HJ);
                 the Popescu table numbers needed the browser (MDPI blocks
                 curl) and were found in the page's own table DOM; added a
                 caveat (the paper's inclined-hole angle convention is not
                 stated). No claim downgraded, none killed.
  10.5 assess  - downgraded 4 claims (H1 "survived" -> supported, rival
                 untested; project evidence "two features" -> one
                 confounded source; rival "weakened" -> argued, not
                 measured; chamfer number -> unsourced judgment); added 6
                 limitations and 1 rule (13); moved the vendor-concentration
                 disclosure into the TL;DR; one collection round (Bambu seam /
                 flow / moisture lines verified verbatim; precise-wall page
                 not found).

## Findings

### F1. Holes print undersized; the amount is local (H1 survived)

- PLA, vertical holes, caliper-measured, Prusa Replica / PrusaSlicer:
  Table 4 of Popescu et al. 2022 - 0.2 mm layers, 2 shells: 9.866 / 7.873
  / 5.876 mm for 10 / 8 / 6 mm holes (0.124-0.134 under); 3 shells: 9.800 /
  7.803 / 5.816 (0.18-0.20 under). "the layer thickness is the most relevant
  influence factor for the diameter accuracy, followed by the number of
  shells around the holes."
- Same paper, experiment 2: 4.5 mm holes at 5-15 deg hole-axis angles
  measured 4.141-4.350 mm before decontamination (0.15-0.36 under); "The
  inclined holes are built undersized". Closest size to our 4.8-4.95 pins
  in any source found.
- PLA, Grgic et al. 2023: a 45 mm hole measured 44.80; the authors adopted a
  slicer hole expansion of 0.13 mm ("the Hole Horizontal Expansion parameter
  should be 0.13 mm"). The paper's body text once writes -0.13; the
  abstract and its table say 0.13.
- nophead (2011): "When Reprap machines print holes they tend to come out
  undersized, even if the linear dimensions of an object are spot on."
- Bambu wiki lists the causes: material shrinkage, elephant's foot, moist
  filament, flow dynamics, holes near nozzle size, "Lack of chamfers or
  lead-in features on holes", and the seam - and states "This calibration is
  specific to each filament".
- **Project evidence (this P1S, PLA):** motor coupler D-bore - nominal too
  tight (FQ), +0.075 inferred still tight, +0.15 FITS (GF); servo mount v6
  pin holes at 4.80 + 0.075 = 4.875 too tight (HH). Consistent with about
  +0.15, but: one printer, filament and unknown slicer profile (one
  confounded source); +0.075 "too tight" is qualitative; and the D-bore is
  a different shape and size from a 4.95 round bore. The ABS coupons (4.80 pin
  "best fit") do not transfer: different material, and they were printed
  with 99% shrinkage compensation (cad/README.md).
- Rival hypothesis: ARGUED, NOT MEASURED. A Lego-shaped hole has a 6.2 mm
  recess at the bed face, so the first layer should flare into the recess,
  not the bore - but nobody calipered the v6 bore vs the recess, and the
  D-bore has no recess, so for that fit the rival is untouched.
- Scale and walls: Grgic's 0.20 mm is a 45 mm hole and does not transfer to
  5 mm. Wall count matters: in Popescu, 2 -> 3 shells added about 0.06 mm
  of undersize - half of the whole +0.15 correction.

### F2. Where to compensate: CAD or slicer, never both

- Bambu Studio "X-Y hole compensation": "The hole diameter will increase by
  twice the compensation value"; symptoms it fixes include "Pins or shafts
  feel too tight"; only applies to closed paths. No recommended value - you
  calibrate it ("Set XY Hole Compensation to 0 mm , and print the model").
- Bambu's "Shrinkage" setting scales outer XY only and "does not affect the
  size of internal features (such as holes and contours)".
- OrcaSlicer has native polyholes and a tolerance-test model (holes at 0.0,
  0.05, 0.1, 0.2, 0.3, 0.4 mm); Bambu Studio and PrusaSlicer have no
  polyhole option, so on the P1S any polyhole must be modelled in OpenSCAD.
- Recommendation: compensate in the CAD (version-controlled, survives
  slicer/profile changes, visible in the record) and keep Bambu's X-Y hole
  compensation at 0 - but first READ Evan's current value.

### F3. Polygon resolution (already handled)

- OpenSCAD: "Using cylinder() with difference() to place holes in objects
  results in undersized holes ... polygons inscribed within in a circle." With
  the defaults ($fa 12, $fs 2) a 4.8 mm hole becomes an octagon, 4.435 mm
  across the flats (arithmetic).
- `lib/lego.scad` `hole_cyl()` already circumscribes (r / cos(180/fn), fn 64):
  measured in this session's meshes, the flats sit exactly at d/2.
- Polyholes (nophead): `n = max(round(2 * d),3)`, "the maximum number of
  vertices you can have before the hole shrinks is twice the hole size in
  mm" - evidence is the author's own drill-gauge tests only. Not adopted.

### F4. First layer and chamfers

- Bambu: elephant's foot "On tolerance-critical parts such as assemblies,
  snaps, rails, and shaft holes, the flared base directly affects fit."
  Release notes: "Set the "elephant foot compensation" to 0.15 for X series
  and P series" (not checked against the shipped P1S profile file).
- Prusa: "Values around 0.2 mm usually work well for the default 0.4 mm
  nozzle"; "use chamfer instead" of a fillet on bed-facing edges; "Using a
  chamfer on the edges of two parts that slot together can save you a lot of
  effort when assembling."

### F5. Orientation and strength (H3 survived; H2 partly)

- Eryildiz 2021 (PLA): "For upright build orientation, 36% less tensile
  strength was obtained compared to the flat ones"; Table 2 flat 55.49,
  on-edge 48.18, upright 35.52 MPa (ratio 0.64).
- ORNL/SAMPE 2019: FFF "commonly demonstrate a 50-75 % decrease in
  mechanical strength in the build direction (z-axis)" (general, not PLA-only).
- H3 is textbook and was not tested hard here (one PLA tensile study).
- H2: vertical holes are more accurate in size but less round in the two
  studies that compared (Sawad 2026, 0.8 mm PLA hole: dimensional error
  0.3095 mm at 90 deg vs 0.5000 at 0 deg, roundness the reverse - a 0.8 mm
  hole, so direction only; Knoop &
  Schoeppner 2017, ABS). No PLA data near 5 mm. Teardrop / flat-roof
  horizontal holes: NOT in any official doc found - community practice only.

### F6. Overhangs, bridges, walls

- Bambu: "when the overhang tilt angle is smaller than 45 deg, it is
  recommended to add supports" (angle measured from the bed). Prusa: 45-60
  deg cleanly, depending on nozzle and settings.
- Bridges: no numeric limit in any official doc; "Shorter bridge spans are
  usually more stable and sag less" (Bambu).
- Prusa: "Walls thinner than one nozzle perimeter are not printable"; table
  for 0.4 mm: 1 perimeter 0.45 mm, 2 = 0.9, 3 = 1.35, 4 = 1.8 (approx).
- Prusa: no "universal" clearance; "An initial good measurement for movable
  parts is at least 0.3 mm."

### F7. Mesh hygiene

- OpenSCAD manual: "It is mandatory for all unions, explicit or implicit,
  that external faces to be merged not be coincident"; failure "can result
  in a render which is not manifold". Same rule for difference(): the cutter
  must extend fully through. Record HE hit exactly this (faces 0.0001 mm
  apart from 4-decimal rounding) and render_scad.py's manifold gate caught it.

## Rules (ranked by rework prevented)

1. **Read and pin the slicer settings first.** Record Evan's Bambu Studio
   X-Y hole compensation, X-Y contour compensation, elephant-foot value,
   layer height, wall count, wall generator (Arachne/classic), seam
   position, flow calibration and filament (and whether it was dried) for
   every printed part. Target: hole compensation 0 so the CAD owns all
   clearance. Bambu lists "Seam , this feature can affect hole precision",
   "Flow dynamics not properly tuned" and moist filament as causes.
2. **Fit classes in `lib/lego.scad`, calibrated per filament.** One named
   diametral offset per fit, used everywhere: FRICTION_PIN (Lego pin: now
   +0.15 -> 4.95, untested), PRESS_SHAFT (D-shaft: +0.15, fits, GF),
   ROTATE (Lego axle: ABS 5.00, PLA unknown), SLIDE (printed-to-printed:
   start at 0.3 per Prusa). Never hand-edit a number in one part.
3. **Print the coupon before any large part.** `cad/pla_fit_coupon.stl`
   exists and is unprinted; a 10-20 minute ladder print replaces a 2-hour
   failed mount. Extend it with a 4.90 / 4.95 / 5.00 / 5.05 pin row.
4. **Pin and shaft holes vertical (along Z) in the print orientation.** All
   current parts do this; keep it a rule.
5. **Lead-in on every mating hole.** A 45 deg chamfer (0.4-0.5 mm is
   Opus's judgment - no source gives a number) at the
   entry face that is not already a Lego recess (Bambu lists missing
   chamfers as a cause; Prusa recommends them).
6. **Recess or chamfer the bed face of any fit-critical hole** (the Lego
   6.2 x 0.8 recess does this for pin holes).
7. **No unsupported overhang below 45 deg from the bed**; if one is
   unavoidable (camera mast holder bottom, 29 deg), say so in the part
   header and plan supports.
8. **Walls >= 3 perimeters (~1.35 mm) for anything that takes load or
   holds a pin;** nothing below 2 perimeters (0.9 mm). More walls make
   holes SMALLER (Popescu), so calibrate fits with the same wall count the
   parts use.
9. **Load in the layer plane.** Pins shear across vertical holes (good);
   tall uprights and cantilevers (camera mast) bend across layers - make
   them thicker or brace them.
10. **Overlap, never touch.** Unions overlap by EPS; never place a vertex on
    another solid's face computed separately (HE); keep the manifold gate.
11. **Static clearances between printed parts and Lego faces:** 0.2-0.3 mm
    (as used in the mast); 0.3+ for anything that moves.
12. **Measure what the probes cannot see.** Probes check topology, not 0.05
    mm sizes; a bore measurement (as done for HG) should be part of the
    render check for every fit-critical hole.
13. **One fixed print profile for fit-critical parts,** and the coupon is
    printed with that same profile (layer height is the strongest factor
    in Popescu); a profile change means a re-calibration.

## Verification table

| claim | source | verdict |
|---|---|---|
| hole comp grows diameter by 2x the value | Bambu wiki XY hole/contour comp | VERIFIED-VERBATIM (curl) |
| "Pins or shafts feel too tight" symptom | same | VERIFIED-VERBATIM |
| calibration "specific to each filament" | same | VERIFIED-VERBATIM |
| missing chamfers listed as a cause | same | VERIFIED-VERBATIM |
| elephant foot 0.15 for X and P series | Bambu Studio release v01.08.03.89 | VERIFIED-VERBATIM (release text; shipped profile not checked) |
| flare "directly affects fit" | Bambu wiki elephant foot | VERIFIED-VERBATIM |
| 0.3 mm for movable parts; 45-60 deg; walls; chamfer; anisotropy | Prusa KB "Modeling with 3D printing in mind" | VERIFIED-VERBATIM |
| supports below 45 deg | Bambu wiki overhang | VERIFIED-VERBATIM |
| Table 4 values 9.866/7.873/5.876 and 9.800/7.803/5.816 | Popescu et al. 2022 (MDPI) | VERIFIED-VERBATIM (browser, table DOM) |
| 4.5 mm holes 4.141-4.350 "before" | same, experiment-2 table | VERIFIED-VERBATIM; angle convention unstated |
| layer thickness most relevant factor | same | VERIFIED-VERBATIM |
| hole expansion 0.13 mm | Grgic et al. 2023 abstract (Crossref) | VERIFIED-VERBATIM |
| inscribed polygons -> undersized holes | OpenSCAD manual | VERIFIED-VERBATIM |
| no coincident faces in unions | OpenSCAD manual CSG Modelling | VERIFIED-VERBATIM |
| polyhole rule and formula | nophead 2011 | VERIFIED-VERBATIM |
| 36% weaker upright; 55.49/48.18/35.52 MPa | Eryildiz 2021 PDF | VERIFIED-VERBATIM |
| 50-75% decrease in z | ORNL/SAMPE 2019 abstract | CLOSE-PARAPHRASE (agent read; not re-fetched by Opus) |
| Sawad 0.3095 vs 0.5000 mm | IEOM 2026 PDF | CLOSE-PARAPHRASE (agent read; not re-fetched) |

## Numbers register

| number | claims | source | date | interest class | verdict |
|---|---|---|---|---|---|
| 0.124-0.134 / 0.18-0.20 mm | PLA vertical hole undersize, 6-10 mm, 0.2 layers, 2 / 3 shells | Popescu et al. | 2022 | INDEPENDENT | verbatim |
| 0.15-0.36 mm | PLA 4.5 mm inclined hole undersize | Popescu et al. | 2022 | INDEPENDENT | verbatim (angle ref unstated) |
| 0.20 mm / 0.13 mm | 45 mm hole undersize / adopted hole expansion | Grgic et al. | 2023 | INDEPENDENT | verbatim (abstract) |
| 2x | diameter change per unit of hole compensation | Bambu wiki | undated | VENDOR-SELF-REPORTED | verbatim |
| 0.15 mm | P-series elephant-foot setting | Bambu release notes | undated in text | VENDOR-SELF-REPORTED | verbatim |
| 0.2 mm | elephant foot "usually work well" | Prusa KB | undated | VENDOR-SELF-REPORTED | close-paraphrase (agent) |
| 0.3 mm | starting clearance for movable parts | Prusa KB | undated | VENDOR-SELF-REPORTED | verbatim |
| 45 / 45-60 deg | supportless overhang | Bambu / Prusa | undated | VENDOR-SELF-REPORTED | verbatim |
| 0.45 / 0.9 / 1.35 / 1.8 mm | 1-4 perimeter wall widths, 0.4 nozzle | Prusa KB | undated | VENDOR-SELF-REPORTED | close-paraphrase (agent) |
| 36%; 55.49 / 35.52 MPa | PLA upright vs flat tensile | Eryildiz | 2021 | INDEPENDENT | verbatim |
| 50-75% | FFF z-strength decrease | ORNL/SAMPE | 2019 | INDEPENDENT | close-paraphrase |
| +0.15 mm | fit offset that worked here (D-bore) | project GF | 2026-10-11 | INDEPENDENT (own print) | record |
| +0.075 too tight | pin holes, v6 | project HH | 2026-10-12 | INDEPENDENT (own print) | record (qualitative) |

Structural checks: H1 rests on two independent published studies
(Popescu, Grgic - both vertical holes, neither near 5 mm) plus ONE
confounded project source (two fits from one printer/profile, tuned in
sequence). Vendor numbers are 7 of 13 rows and they DO set several rules
(sliding clearance, overhangs, walls, elephant foot) - now stated in the
TL;DR.

## Thin / missing

- **Evan's slicer settings for every PLA print so far** - unknown. Biggest
  gap: a non-zero X-Y hole compensation would make all project fit numbers
  slicer-dependent.
- **PLA horizontal-hole data near 5 mm** - none found. Searches: "FDM hole
  diameter dimensional accuracy undersize PLA orientation layer height";
  "dimensional accuracy of holes FDM PLA internal diameter horizontal vs
  vertical"; "FDM accuracy circular holes build orientation horizontal axis
  vertical axis".
- **Peer-reviewed clearance-vs-fit table for small FDM PLA pins** - none.
  Searches: "3D printed press fit clearance fit tolerance study FDM"; "FDM
  clearance fit press fit hole shaft tolerance experimental study PLA";
  "minimum clearance print-in-place FDM PLA experimental". Vendor blogs give
  0.1-0.5 mm ranges without saying per-side or diametral; not used.
- **Teardrop holes in official docs** - none (Bambu, Orca, Prusa searched).
- **Shipped P1S profile elephant-foot value** - release notes only.
- **PrusaSlicer XY size compensation** - no official article (n/a for the P1S).
- **Seam placement, flow calibration, moisture, Arachne vs classic walls,
  "precise wall"** - Bambu names seam, flow and moisture as causes but gives
  no design rule; a Bambu "precise wall" wiki page was not found at
  .../parameter/precise-wall.
- **PLA friction-fit creep/relaxation over time** - not researched.
- **Fit of the 6.2 mm collar recess itself** - untested in PLA.
- **Caliper data on any printed bore in this project** - none.

## What would change this

- Evan's slicer showing non-zero hole compensation -> re-derive every fit
  offset with it at 0.
- The 4.95 holes coming out loose -> FRICTION_PIN offset between +0.075 and
  +0.15; the coupon's ladder decides.
- A different filament (brand, colour) -> re-calibrate (Bambu: per filament).

## Sources (read 2026-10-12)

- Bambu Lab Wiki: "XY Hole / Contour compensation" (wiki.bambulab.com/en/software/bambu-studio/xy-hole-contour-compensation); "3d prints shrinkage"; "Elephant foot compensation" (.../parameter/elephant-foot); "How to Print Overhangs" (.../print-quality/overhang); "How to Improve Bridge Quality". Bambu Studio GitHub release v01.08.03.89 notes.
- OrcaSlicer Wiki: "Precision" (quality_settings_precision); "Filament Tolerance Calibration" (calibration/tolerance_calib).
- Prusa Knowledge Base: "Modeling with 3D printing in mind" (article 164135); "Elephant foot compensation" (114492); "Support material"; "Poor bridging".
- Popescu, Amza, Marinescu, Iacob, Carutasu, "Investigations on Factors Affecting 3D-Printed Holes Dimensional Accuracy and Repeatability", Applied Sciences 13(1):41, 2022, doi 10.3390/app13010041.
- Grgic, Karakasic, Glavas, Konjatic, "Accuracy of FDM PLA Polymer 3D Printing Technology Based on Tolerance Fields", Processes 11(10):2810, 2023, doi 10.3390/pr11102810.
- Sawad et al., "Accuracy Assessment of Micro-Holes in FDM 3D Printing", IEOM Ankara 2026, doi 10.46254/AN16.20260055.
- Knoop, Schoeppner, "Geometrical Accuracy of Holes and Cylinders Manufactured with Fused Deposition Modeling", SFF Symposium 2017.
- Eryildiz, "Effect of Build Orientation on Mechanical Behaviour and Build Time of FDM 3D-Printed PLA Parts", European Mechanical Science 5(3):116-120, 2021, doi 10.26701/ems.881254.
- ORNL / SAMPE 2019, "Z-pinning approach for improving interlayer strength of 3D printed parts" (abstract).
- OpenSCAD User Manual: "Other Language Features" (circle resolution), "undersized circular objects", "CSG Modelling".
- C. Palmer (nophead), "Polyholes", HydraRaptor blog, 2011-02-05.
- Project: cad/README.md; .claude/project-memory/hardware.md; record Appendices FQ, FS, GF, GU, HE, HG, HH.

## Cold assessment (stage 10.5, fresh agent, brief-only input)

1. The two project fits were counted as independent - ACCEPTED (one
   confounded source). 2. Vendor concentration disclosed only at the bottom
   - ACCEPTED, moved to the TL;DR; the chamfer number had no source -
   ACCEPTED. 3. The H1 rival was never measured; H3 was a softball -
   ACCEPTED, both stated. 4. The never-run source type is the project's own
   measurement (coupon unprinted, slicer profile unread) - ACCEPTED, it is
   Rule 1 and Rule 3. 5. Missing: seam, flow, walls vs hole size, Arachne,
   precise wall, layer-height rule, recess fit, moisture, creep, D-bore vs
   round-bore extrapolation, Grgic's 45 mm scale, Sawad's 0.8 mm relevance -
   ADDED. Its arithmetic check found no errors. 6. "H1 survived" and "two
   features point to +0.15" overstated - ACCEPTED, reworded.
