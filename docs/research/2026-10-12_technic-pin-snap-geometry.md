# Technic friction pin snap geometry for printed parts

**Date:** 2026-10-12 (America/Chicago)
**Question:** What is the geometry of a Lego Technic pin hole and the black
friction pin (part 2780) that a 3D-printed part must reproduce so a real pin
seats and SNAPS (Evan: "the last maybe .1 mm of the circle has a wider
diameter so the connectors can snap into place")?
**For:** Evan and the motor-mount design (`cad/scad/motor_mount.scad`), whose
arms switch from printed stubs to real black pins. Decision: the hole, recess
and snap-cavity sizes in the arms.

## TL;DR

Evan's observation holds, with one correction of size: the wider part is not
the last 0.1 mm but the last **0.8 mm at each END of the pin**, a lip about
**5.2 mm** across against the 4.8 mm shaft (LDraw part geometry), and it
snaps into the **recess at the far face of the hole**, which is **6.2 mm
across and 0.8 mm deep** (measured, cailliau.org; LDraw models it as 6.4 x
0.8). The pin's centre collar seats in the recess at the near face. So a
printed part that takes half a pin must look like a Lego beam: 4.8 bore,
6.2 x 0.8 recess at the face the pin enters, and a 6.2 recess (or open cavity)
where the pin's tip ends, about 8 mm from the collar. Hypothesis H1 (a snap
lip + far-face recess) survived; H0 (friction only, no snap feature) is
weakened but NOT killed: the lip exists in the CAD model, but nothing here
shows it is what retains the pin. **Source concentration:** every geometric
number except the 6.2 x 0.8 recess comes from ONE community CAD library
(LDraw), built by modellers to fit itself; only the recess has an
independent (one-person, caliper) measurement. Evan's "last 0.1 mm" may
instead describe the friction ridges, which LDraw makes about 0.1 mm proud
of the shaft near the tip (finding 7). The motor-mount socket works for
either reading: bore + collar recess + an open cavity where the tip lands.

## Method

Primary geometry: the LDraw parts library (community CAD of LEGO parts, 1 LDU
= 0.4 mm), read as raw `.dat` text from the Debian mirror
(`browse.dgit.debian.org/ldraw-parts.git/plain/...`): `parts/2780.dat`,
`p/confric5.dat`, `p/confric.dat`, `p/peghole.dat`, `p/connhole.dat`,
`p/beamhole.dat`. Measured values: cailliau.org "More Dimensions" (raw HTML,
curl). Community print practice: web search; Printables was behind a
Cloudflare challenge (not bypassed). Limitation: no part was measured for this
brief; no official LEGO drawing exists publicly.

Hypotheses (stated before collection):
- H1: the pin has a wider tip lip and the hole a wider far-face recess; the
  lip snaps into that recess.
- H0 (rival): the hole recesses only seat the collar for flush stacking; the
  pin holds by friction ridges alone, with no snap feature.

Phase effects (2026-10-12):
  8.5 verify   - caught a NOT-FOUND-equivalent: the Printables "6.2 x 1.05"
                 figure came only from a search summary and could not be
                 read (UNREACHABLE); downgraded to unverified.
  10.5 assess  - downgraded 2 claims (H0 "died" -> weakened; LDraw rows
                 relabelled DERIVED, not verbatim), added a limitation
                 (single-library concentration, now in the TL;DR) and a
                 finding (friction ridges, finding 7).

## Findings

1. **Hole bore 4.8 mm nominal; real holes 4.9 mm.** LDraw `connhole.dat`: a
   cylinder of radius 6 LDU (4.8 mm) between the two ends. cailliau measures
   the bearing hole at 4.9 mm, derived from the knob, with axles at 4.8 mm.
2. **Recess at BOTH faces: 6.2 mm across, 0.8 mm deep (measured).** cailliau:
   "there is a counterbore at each side. That turns out to be 6.2mm in
   diameter and 0.8mm deep". LDraw `peghole.dat`: radius 8 LDU (6.4 mm), 2 LDU
   (0.8 mm) deep, at each end of `connhole.dat` / `beamhole.dat`.
3. **Pin half-length 8.0 mm from the collar's centre plane** (LDraw
   `confric5.dat` runs from y 0 to y -20 LDU; `2780.dat` is two of them
   mirrored), so a full pin is 16 mm, spanning two 8 mm beams.
4. **Collar: 6.4 mm across (LDraw), 0.8 mm per side, 1.6 mm total**, split by
   slots on 2780 ("Split Base Collar"). It sits half in each beam's recess,
   which is why two pinned beams sit flush. A forum measurement put the
   collar's "outer cylinder" at 0.9 mm (Eurobricks topic 75308; single
   source, ambiguous about which length).
5. **Snap lip: the last 0.8 mm of each end, radius 6.5 LDU = 5.2 mm across**
   (LDraw `confric5.dat`, cylinders at y -18..-20 with r = 6.5 LDU, against
   the shaft's r = 6.0). The slots (inner radius ~4 LDU) let the end squeeze
   through the 4.8 bore and spring out into the far recess.
6. **Printing practice:** community designs use about 6.2 mm recesses; one
   (Printables 779089) reportedly uses 6.2 x 1.05 (search summary only,
   UNREACHABLE). General guidance: test-print a hole series in 0.05-0.1 mm
   steps (the project's `cad/pla_fit_coupon.stl` already does this).
7. **Friction ridges** (from the cold assessor's reading of the same
   `confric5.dat`, not re-derived independently): ridges at about r 6.25 LDU,
   i.e. ~0.1 mm proud of the 4.8 shaft per side, at y -13..-18 (next to the
   tip) and y -2..-7 (next to the collar). These grip the bore along its
   length; they are a second candidate for what Evan felt.

## Design consequence for the motor-mount arm (half a pin below beam A/B)

With the beam's underside at B (33.13 mm above the floor) and the arm's top
face flush against it: recess 6.2 x 0.8 at the top (collar), bore 4.8 for
6.2 mm (as in a real 7.8 mm beam), then a 6.2 mm cavity where the tip lip
lands (tip at about B - 8.0 in LDraw's 8.0 mm module; a real beam is 7.8 mm,
so a real pin's tip may sit up to ~0.2 mm higher). The cavity is 2.0 mm tall,
not 0.8, so either length still lands inside it. The real tip is chamfered
(LDraw draws it flat), which only makes it enter more easily.

## Verification table (stage 8.5)

| Load-bearing claim | Source | Verdict |
|---|---|---|
| Counterbore at each side, 6.2 mm x 0.8 mm | cailliau.org More Dimensions, raw HTML | VERIFIED-VERBATIM |
| Recess r 8 LDU x 2 LDU at both hole ends | LDraw peghole.dat + connhole.dat, raw | VERIFIED-VERBATIM (geometry lines read) |
| Bore r 6 LDU (4.8 mm) | LDraw connhole.dat, raw | VERIFIED-VERBATIM |
| Pin half 20 LDU; lip r 6.5 LDU over y -18..-20 | LDraw confric5.dat, raw | DERIVED: geometry lines read verbatim, radii computed from their matrices (confirmed independently by the cold assessor) |
| Collar r 8 LDU, 2 LDU per side | LDraw confric5.dat, raw | DERIVED (as above) |
| Real hole 4.9 mm, axle 4.8 mm | cailliau.org, raw HTML | VERIFIED-VERBATIM |
| Printed design using 6.2 x 1.05 | Printables 779089 via search summary | UNREACHABLE (Cloudflare) |

## Numbers register

| Number | Claims | Source | Date read | Interest class | Verdict |
|---|---|---|---|---|---|
| 6.2 mm x 0.8 mm | hole recess, both faces | cailliau.org | 2026-10-12 | INDEPENDENT (measured by the author) | VERIFIED-VERBATIM |
| 4.9 mm | real bearing hole | cailliau.org | 2026-10-12 | INDEPENDENT | VERIFIED-VERBATIM |
| 6.4 mm (r 8 LDU) | recess / collar, CAD | LDraw | 2026-10-12 | INDEPENDENT (community CAD) | VERIFIED-VERBATIM |
| 5.2 mm (r 6.5 LDU) | pin tip lip | LDraw confric5.dat | 2026-10-12 | INDEPENDENT (community CAD) | VERIFIED-VERBATIM, but a model, not a measurement |
| 0.8 mm | lip length, recess depth | LDraw | 2026-10-12 | INDEPENDENT | VERIFIED-VERBATIM |
| 8.0 mm | pin half-length | LDraw | 2026-10-12 | INDEPENDENT | VERIFIED-VERBATIM |
| 0.9 mm | collar "outer cylinder" | Eurobricks 75308 | 2026-10-12 | UNVERIFIABLE (forum) | single source |
| 6.2 x 1.05 | printed recess | Printables 779089 | - | UNVERIFIABLE | UNREACHABLE |

No vendor numbers. But SOURCE concentration is high: all LDraw rows are one community library, internally consistent by construction, so they are one source, not several (stated in the TL;DR). Same-source note:
findings 2-5 all lean on LDraw except the 6.2 x 0.8 recess, which cailliau
measures independently.

## Cold assessment (stage 10.5, fresh agent, 2026-10-12)

It found: (1) findings 2-5 rest on one library; (2) the concentration was
buried at the bottom; (3) H1 was never exposed to killing evidence - no
caliper reading of Evan's pins/beams, no coupon with vs without the far
cavity, no source saying the lip retains; (4) the community-practice source
type (Printables) was never actually read; (5) missing for a print designer:
measured parts, FDM hole shrink and orientation, PLA brittleness and creep
at a snap wall, 7.8 vs 8.0 mm, the real tip chamfer, a retention-force
target, existing parametric Technic libraries; (6) "H0 died" and
"VERIFIED-VERBATIM (computed)" overstated. It confirmed the 5.2 mm lip is
really in confric5.dat. One revision round applied: TL;DR, verdict labels,
finding 7, the 7.8/8.0 note. Not done (needs Evan's hands, not a search):
caliper the pin tip and ridges; print the socket and feel the snap.

## Thin / missing

- **No measured lip diameter.** LDraw's 5.2 mm is a modeller's choice;
  searches for "technic friction pin 2780 dimensions collar diameter" and the
  Eurobricks pin-standard thread found no caliper value for the tip. A caliper
  on one black pin's tip (Evan has them) would settle it.
- **No official LEGO drawing** of the pin or the hole (searched; none public).
- **No published PLA recipe** for the far-face snap cavity specifically; the
  community designs found give recess sizes, not cavity heights.

## What would change this conclusion

- A caliper reading of the pin's tip below ~5.0 mm or a lip shorter than
  ~0.5 mm would make the snap weak in a 6.2 cavity (the friction ridges would
  then carry the joint).
- If the coupon's row B shows 6.2 x 0.8 does not let a pin sit flush in PLA,
  the recess grows (6.3-6.4).

## Sources (read 2026-10-12)

- LDraw parts library, Debian mirror, raw files:
  https://browse.dgit.debian.org/ldraw-parts.git/plain/parts/2780.dat ,
  .../p/confric5.dat , .../p/confric.dat , .../p/peghole.dat ,
  .../p/connhole.dat , .../p/beamhole.dat
- R. Cailliau, Lego Dimensions - More Dimensions:
  https://www.cailliau.org/en/Alphabetical/L/Lego/Dimensions/More%20Dimensions/
- Eurobricks, "Lego pin and axle standard" (topic 75308):
  https://www.eurobricks.com/forum/forums/topic/75308-lego-pin-and-axle-standard/
- Printables 779089 "LEGO-Technic-Compatible Frame" (unreachable):
  https://www.printables.com/model/779089-lego-technic-compatible-frame
