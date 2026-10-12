// Servo mount v3 (2026-10-12): PLA frame that sits on the TWO Lego 2x4 L-shaped
// liftarms either side of the MG90D-270 and carries the servo by its two ears.
// UNTESTED - not printed.
// v3 (record GV, Evan): ear supports 6 mm higher (13.3 above the Ls) and less
// material - two pinned rails along the Ls plus two bridges under the ears,
// open everywhere else.
//
// FRAME: origin on the servo output shaft. x along the servo's long axis = the
// L legs (stud 0 = the Ls' axle holes, studs 1, 2, 3 at x 8, 16, 24); y across;
// the two L long legs are centred at y +16 and -16 (photo IMG_0212: 4 studs
// apart, one each side of the servo, short legs pointing inward at x 24);
// z = 0 on the Ls' TOP faces, z up. mm.
//
// Evan, 2026-10-12 (records GO, GP, GQ, GS): case 22.88 x 12.44 x 22.60; ears
// 5.0 long, 2.65 thick, hole centres 2.5 from the case ends (27.88 apart); the
// FAR ear's hole is 2 studs + 1 mm (17.0) from the shaft; ear underside 15.3
// above the Ls' bottom face (GB). Only the ears rest on plastic; the case
// footprint is open. "Connect on both sides": pin holes at studs 1, 2 and 3 of
// BOTH Ls (all open per Evan; the short-leg ends are closed and unused).
//
// PINS: Evan's black LEGO 2780 friction pins (decisions.md), Lego-beam shaped
// holes. Pinning studs 1 and 3 on each side is enough; stud 2 is a spare.
// Placeholders: L_T_UNMEASURED (assumed 8.0 so the plate is never too thick)
// and L_SPACING_UNMEASURED (32.0 = 4 studs, read off the photo).

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;
PIN_D = 4.875;            // pin-hole bore: 4.80 + 0.075 (Evan, 2026-10-12, record GU)

PITCH = 8.0;
L_T_UNMEASURED = 8.0;
L_SPACING_UNMEASURED = 4 * PITCH;          // centre to centre of the two L legs
L_Y = L_SPACING_UNMEASURED / 2;            // 16
L_W = 8.0;                                 // a liftarm is one stud wide
EAR_ABOVE_L_BOTTOM = 15.3;                 // GB
RAISE = 6.0;                               // v3 (Evan): 6 mm higher than v2
EAR_Z = EAR_ABOVE_L_BOTTOM - L_T_UNMEASURED + RAISE;   // bridge top = ear underside (13.3)
RAIL_H = 7.8;                              // a Lego beam's height: a pin half fits fully

CASE_L = 22.88;
CASE_W = 12.44;
CASE_H = 22.60;
EAR_L = 5.0;
EAR_T = 2.65;
EAR_HOLE_FROM_CASE = 2.5;
EAR_HOLE_SPACING = CASE_L + 2 * EAR_HOLE_FROM_CASE;   // 27.88
FAR_HOLE_X = 2 * PITCH + 1.0;                         // 17.0 (Evan)
NEAR_HOLE_X = FAR_HOLE_X - EAR_HOLE_SPACING;          // -10.88
CASE_CX = (FAR_HOLE_X + NEAR_HOLE_X) / 2;             // 3.06

PILOT_D = 1.7;            // pick from the coupon's 1.5 / 1.7 / 1.9 row
PILOT_DEPTH = 6.0;        // screw 7.0 - ear 2.65 = 4.35 into the bridge
OPEN_CLEAR = 0.5;

X0 = NEAR_HOLE_X - EAR_HOLE_FROM_CASE - 1.12;   // -14.5: past the near ear tip (-13.38)
X1 = 3 * PITCH + L_W / 2;                       // 28: the Ls' far end
Y_OUT = L_Y + L_W / 2;                          // 20: outer faces of the Ls

PIN_X = [PITCH, 2 * PITCH, 3 * PITCH];          // studs 1, 2, 3
NEAR_BRIDGE = [X0, CASE_CX - CASE_L / 2 - OPEN_CLEAR];        // x -14.5 .. -8.88
FAR_BRIDGE = [CASE_CX + CASE_L / 2 + OPEN_CLEAR, FAR_HOLE_X + 3.5];   // x 15.0 .. 20.5

difference() {
  union() {
    // two rails along the Ls
    for (s = [1, -1]) translate([X0, s * L_Y - L_W / 2, 0]) cube([X1 - X0, L_W, RAIL_H]);
    // two bridges under the ears, rail to rail
    for (b = [NEAR_BRIDGE, FAR_BRIDGE]) translate([b[0], -Y_OUT, RAIL_H - EPS]) cube([b[1] - b[0], 2 * Y_OUT, EAR_Z - RAIL_H + EPS]);
  }
  // open space under the whole servo body
  translate([CASE_CX - CASE_L / 2 - OPEN_CLEAR, -(CASE_W / 2 + OPEN_CLEAR), -EPS])
    cube([CASE_L + 2 * OPEN_CLEAR, CASE_W + 2 * OPEN_CLEAR, EAR_Z + 2 * EPS]);
  // ear-screw pilots
  for (x = [NEAR_HOLE_X, FAR_HOLE_X])
    translate([x, 0, EAR_Z - PILOT_DEPTH]) pilot_hole(PILOT_D, PILOT_DEPTH + EPS);
  // pin holes over both Ls, Lego-beam shaped
  for (x = PIN_X, s = [1, -1])
    translate([x, s * L_Y, 0]) technic_hole(d = PIN_D, h = RAIL_H, cb_d = 6.2, cb_top = 0.8, cb_bot = 0.8);
}

// preview-only ghosts
ghost_box([CASE_L, CASE_W, CASE_H], [CASE_CX - CASE_L / 2, -CASE_W / 2, EAR_Z - 1.5]);   // case
ghost_box([CASE_L + 2 * EAR_L, CASE_W, EAR_T], [CASE_CX - CASE_L / 2 - EAR_L, -CASE_W / 2, EAR_Z]);   // ears
for (s = [1, -1]) ghost_box([X1 + L_W / 2, L_W, L_T_UNMEASURED], [-L_W / 2, s * L_Y - L_W / 2, -L_T_UNMEASURED]);   // L long legs
