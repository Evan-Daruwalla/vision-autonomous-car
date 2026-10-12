// Electronics DECK (2026-10-11) - LAYOUT DRAFT - NOT PRINTABLE - placeholders marked _UNMEASURED
//
// PURPOSE: upper plate of the two-level electronics stack. Sits on the four tray posts
// and carries the Raspberry Pi case (fenced), the Arduino Uno (standoffs + pegs), the
// LM2596 buck converter (standoffs + pegs) and the rocker-switch hole. UNTESTED: no part
// of this layout has been printed or fitted.
//
// FRAME: x along the car (+x = rear), y lateral, origin at the tray centre;
// z = 0 at the deck underside (the deck sits on the tray posts, tray z 23.0).
//
// MAP (mm)
//   plate x -78..78, y -62.5..62.5, z 0..2.5
//   post bosses 8x8 at (+/-72, +/-58.5), z 0..7.8, pin holes 4.8 dia (0.8 counterbore at z 0)
//   Pi fence z 2.5..5.5, interior x -76.2..14.5, y -52.5..10.2
//   Uno standoffs z 2.5..6.5 + pegs to 9.5; LM2596 standoffs z 2.5..5.5 + pegs to 8.5
//   rocker hole 20 dia at (40, 40)
//
// Render with scripts/render_scad.py: it checks the mesh against
// electronics_deck_draft.probe.json.

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;

PLATE_T = 2.5;
PI_CASE_L_UNMEASURED = 90.2;
PI_CASE_W_UNMEASURED = 62.2;
PI_CASE_H_UNMEASURED = 26.7;
FENCE_T = 1.5;
FENCE_H = 3.0;                       // above the plate top
UNO_STANDOFF_D = 6.0;
UNO_STANDOFF_H = 4.0;
UNO_PEG_D = 3.0;
UNO_PEG_H = 3.0;
LM_STANDOFF_D = 6.0;
LM_STANDOFF_H = 3.0;
LM_PEG_D = 2.8;
LM_PEG_H = 3.0;
ROCKER_HOLE_D = 20.0;

POSTS = [[-72, -58.5], [72, -58.5], [-72, 58.5], [72, 58.5]];
// Uno hole pattern from the community library (board at x 20..73.34, y -53..15.58)
UNO_HOLES_UNMEASURED = [[22.54, -37.76], [37.78, 13.04], [65.72, 13.04], [70.8, -39.03]];
LM_HOLES_UNMEASURED = [[-67.5, 16.5], [-6.5, 16.5], [-67.5, 47.5], [-6.5, 47.5]];
ZIPS = [[-55, -54.9], [-10, -54.9], [-55, 12.6], [-10, 12.6]];

FENCE_X0 = -76.2; FENCE_X1 = 14.5;   // fence interior
FENCE_Y0 = -52.5; FENCE_Y1 = 10.2;

module box(p0, p1) { translate(p0) cube([p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]); }

difference() {
  union() {
    box([-78, -62.5, 0], [78, 62.5, PLATE_T]);                       // 1 plate
    for (p = POSTS) box([p[0] - 4, p[1] - 4, 0], [p[0] + 4, p[1] + 4, 7.8]);   // 2 post bosses
    // 3 Pi fence z 2.5..5.5: ring of thickness FENCE_T outside the interior
    difference() {
      box([FENCE_X0 - FENCE_T, FENCE_Y0 - FENCE_T, PLATE_T], [FENCE_X1 + FENCE_T, FENCE_Y1 + FENCE_T, PLATE_T + FENCE_H]);
      box([FENCE_X0, FENCE_Y0, PLATE_T - EPS], [FENCE_X1, FENCE_Y1, PLATE_T + FENCE_H + EPS]);
    }
    // 4 Uno standoffs + pegs (pegs are plain cylinders)
    for (h = UNO_HOLES_UNMEASURED) {
      translate([h[0], h[1], PLATE_T]) cylinder(d = UNO_STANDOFF_D, h = UNO_STANDOFF_H);
      translate([h[0], h[1], PLATE_T + UNO_STANDOFF_H]) cylinder(d = UNO_PEG_D, h = UNO_PEG_H);
    }
    // 5 LM2596 standoffs + pegs
    for (h = LM_HOLES_UNMEASURED) {
      translate([h[0], h[1], PLATE_T]) cylinder(d = LM_STANDOFF_D, h = LM_STANDOFF_H);
      translate([h[0], h[1], PLATE_T + LM_STANDOFF_H]) cylinder(d = LM_PEG_D, h = LM_PEG_H);
    }
  }
  // 6 post pin holes
  for (p = POSTS) translate([p[0], p[1], 0]) technic_hole(d = 4.8, h = 7.8, cb_d = 6.2, cb_bot = 0.8);
  // 7 rocker
  translate([40, 40, -EPS]) hole_cyl(ROCKER_HOLE_D, PLATE_T + 2 * EPS);
  // 8 zip slots
  for (z = ZIPS) translate([z[0], z[1], 0]) zip_slot(4.0, 1.8, PLATE_T);
}

// Ghosts (preview only, not in the STL)
ghost_box([PI_CASE_L_UNMEASURED, PI_CASE_W_UNMEASURED, PI_CASE_H_UNMEASURED], [-75.95, -52.25, 2.5]);
ghost_box([53.34, 68.58, 15], [20, -53, 9.5]);                       // Uno
ghost_box([66, 36, 12], [-70, 14, 8.5]);                             // LM2596
