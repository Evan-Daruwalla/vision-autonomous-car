// Servo mount v1 (2026-10-12): PLA plate that sits on the Lego 2x4 L-shaped
// liftarm and carries the MG90D-270 by its two ears. UNTESTED - not printed.
//
// FRAME: origin on the servo output shaft = the L liftarm's axle hole (stud 0);
// x along the L's long leg (studs 1, 2, 3 at x 8, 16, 24); z = 0 on the L's
// TOP face, z up. mm.
//
// Evan, 2026-10-12 (records GO, GP): case 22.88 x 12.44 x 22.60; ears 5.0 long,
// 2.65 thick, hole centres 2.5 from the case ends (27.88 apart); the FAR ear's
// hole is 2 studs + 1 mm (17.0) from the shaft; ear underside 15.3 above the
// L's bottom face (GB). "Leave it as open space": only the ears rest on
// plastic; the whole case footprint is cut through (shaft, boss, coupler free).
//
// PINS: Evan's black LEGO 2780 friction pins (decisions.md). Studs 0-2 are
// taken (axle hole / under the case / 1 mm from the far ear's screw), so the
// plate pins at stud 3, the L's corner: (24, 0) plus BOTH possible positions
// of the short leg, (24, +8) and (24, -8) - one of them stays empty.
// Placeholder: L_T_UNMEASURED (the L's thickness, assumed 8.0 so the plate is
// never too thick - a thinner real L leaves a gap the ear screws close).

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;

PITCH = 8.0;
L_T_UNMEASURED = 8.0;
EAR_ABOVE_L_BOTTOM = 15.3;                 // GB
EAR_Z = EAR_ABOVE_L_BOTTOM - L_T_UNMEASURED;   // plate top = ear underside (7.3)

CASE_L = 22.88;
CASE_W = 12.44;
CASE_H = 22.60;
EAR_L = 5.0;
EAR_T = 2.65;
EAR_HOLE_FROM_CASE = 2.5;
EAR_HOLE_SPACING = CASE_L + 2 * EAR_HOLE_FROM_CASE;   // 27.88
FAR_HOLE_X = 2 * PITCH + 1.0;                         // 17.0 (Evan)
NEAR_HOLE_X = FAR_HOLE_X - EAR_HOLE_SPACING;          // -10.88
CASE_CX = (FAR_HOLE_X + NEAR_HOLE_X) / 2;             // 3.06: case centre vs shaft

PILOT_D = 1.7;            // pick from the coupon's 1.5 / 1.7 / 1.9 row
PILOT_DEPTH = 6.0;        // screw 7.0 - ear 2.65 = 4.35 into the plate
OPEN_CLEAR = 0.5;         // around the case footprint

X0 = NEAR_HOLE_X - EAR_HOLE_FROM_CASE - 1.12;   // -14.5: past the near ear tip (-13.38)
X1 = 3 * PITCH + 4;                             // 28: covers the stud-3 holes
Y_STRIP = 9.0;                                  // 1 mm past the 8 mm-wide L each side
PAD_X0 = 20.0;                                  // pin pad x 20..28
PAD_Y = 12.0;

PIN_NODES = [[3 * PITCH, 0], [3 * PITCH, PITCH], [3 * PITCH, -PITCH]];

difference() {
  union() {
    translate([X0, -Y_STRIP, 0]) cube([X1 - X0, 2 * Y_STRIP, EAR_Z]);           // strip
    translate([PAD_X0, -PAD_Y, 0]) cube([X1 - PAD_X0, 2 * PAD_Y, EAR_Z]);       // pin pad
  }
  // open space under the whole servo body
  translate([CASE_CX - CASE_L / 2 - OPEN_CLEAR, -(CASE_W / 2 + OPEN_CLEAR), -EPS])
    cube([CASE_L + 2 * OPEN_CLEAR, CASE_W + 2 * OPEN_CLEAR, EAR_Z + 2 * EPS]);
  // ear-screw pilots
  for (x = [NEAR_HOLE_X, FAR_HOLE_X])
    translate([x, 0, EAR_Z - PILOT_DEPTH]) pilot_hole(PILOT_D, PILOT_DEPTH + EPS);
  // pin holes, Lego-beam shaped: collar recess at the bottom (meets the L), tip recess on top
  for (n = PIN_NODES)
    translate([n[0], n[1], 0]) technic_hole(d = 4.8, h = EAR_Z, cb_d = 6.2, cb_top = 0.8, cb_bot = 0.8);
}

// preview-only ghosts
ghost_box([CASE_L, CASE_W, CASE_H], [CASE_CX - CASE_L / 2, -CASE_W / 2, EAR_Z - 1.5]);    // case (face 1.5 below the ears, GB)
ghost_box([CASE_L + 2 * EAR_L, CASE_W, EAR_T], [CASE_CX - CASE_L / 2 - EAR_L, -CASE_W / 2, EAR_Z]);   // ears
ghost_box([3 * PITCH + 8, 8, L_T_UNMEASURED], [-4, -4, -L_T_UNMEASURED]);                // L long leg
