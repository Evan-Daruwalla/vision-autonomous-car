// Servo mount plate (2026-10-11): LAYOUT DRAFT - NOT PRINTABLE - placeholders
// marked _UNMEASURED. UNTESTED.
//
// PURPOSE: a plate that sits on top of the Lego L piece and holds the steering
// servo by its ears, with a pocket for the servo case and a clearance hole for
// the output-shaft boss. Pin holes on the 8 mm Technic grid tie it to the L piece.
//
// FRAME: origin on the servo output shaft axis; x along the servo's long side
// (case centre at +x); z=0 at the L piece's TOP face (the plate sits on it),
// z up. mm.
//
// Measured: EAR_ABOVE_L_BOTTOM 15.3, CASE_FACE_ABOVE_L_BOTTOM 13.8 (record GB).
// Everything named *_UNMEASURED is a placeholder until measured on the real
// servo and L piece. Preview ghosts (%) stay out of the STL.

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;

L_T_UNMEASURED = 8.0;
EAR_ABOVE_L_BOTTOM = 15.3;
CASE_FACE_ABOVE_L_BOTTOM = 13.8;
EAR_Z = EAR_ABOVE_L_BOTTOM - L_T_UNMEASURED;             // 7.3
CASE_FACE_Z = CASE_FACE_ABOVE_L_BOTTOM - L_T_UNMEASURED; // 5.8
CASE_L_UNMEASURED = 22.8;
CASE_W_UNMEASURED = 12.2;
CASE_H_UNMEASURED = 22.6;
SHAFT_OFFSET_UNMEASURED = 5.5;
EAR_SPAN_UNMEASURED = 32.0;
EAR_HOLE_SPACING_UNMEASURED = 27.5;
EAR_T_UNMEASURED = 2.5;
PILOT_D = 1.7;
PILOT_DEPTH = 6.0;
BOSS_CLEAR_D_UNMEASURED = 12.0;
POCKET_CLEAR = 0.5;

SO = SHAFT_OFFSET_UNMEASURED;
CL = CASE_L_UNMEASURED;
CW = CASE_W_UNMEASURED;
EHS = EAR_HOLE_SPACING_UNMEASURED;
ES = EAR_SPAN_UNMEASURED;

difference() {
  translate([-20, -20, 0]) cube([48, 40, EAR_Z]);   // plate

  // 1 servo case pocket
  translate([SO - CL / 2 - POCKET_CLEAR, -(CW / 2 + POCKET_CLEAR), CASE_FACE_Z - 0.5])
    cube([CL + 2 * POCKET_CLEAR, CW + 2 * POCKET_CLEAR, EAR_Z - (CASE_FACE_Z - 0.5) + EPS]);

  // 2 output-shaft boss clearance
  translate([0, 0, -EPS]) hole_cyl(BOSS_CLEAR_D_UNMEASURED, EAR_Z + 2 * EPS);

  // 3 ear-screw pilots
  for (x = [SO - EHS / 2, SO + EHS / 2])
    translate([x, 0, EAR_Z - PILOT_DEPTH]) pilot_hole(PILOT_D, PILOT_DEPTH + EPS);

  // 4 pin holes on the 8 mm grid (18 nodes)
  for (x = [-16, -8, 0, 8, 16, 24], y = [-16, 16])
    translate([x, y, 0]) technic_hole(d = 4.8, h = EAR_Z, cb_d = 6.2, cb_bot = 0.8);
  for (x = [-16, 24], y = [-8, 0, 8])
    translate([x, y, 0]) technic_hole(d = 4.8, h = EAR_Z, cb_d = 6.2, cb_bot = 0.8);
}

// preview-only ghosts
ghost_box([CL, CW, CASE_H_UNMEASURED], [SO - CL / 2, -CW / 2, CASE_FACE_Z]);   // servo case
ghost_box([ES, CW, EAR_T_UNMEASURED], [SO - ES / 2, -CW / 2, EAR_Z]);          // ears
ghost_box([6, 6, 4.0], [-3, -3, 1.8]);                                         // output boss
ghost_box([48, 8, L_T_UNMEASURED], [-20, -4, -L_T_UNMEASURED]);                // L piece (shape unknown)
