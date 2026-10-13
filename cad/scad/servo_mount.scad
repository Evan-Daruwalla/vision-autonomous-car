// Servo mount v3 (2026-10-12): PLA frame that sits on the TWO Lego 2x4 L-shaped
// liftarms either side of the MG90D-270 and carries the servo by its two ears.
// UNTESTED - not printed.
// v3 (record GV, Evan): ear supports 6 mm higher (13.3 above the Ls) and less
// material - two pinned rails along the Ls plus two bridges under the ears,
// open everywhere else.
// v4 (Evan, 2026-10-12): the ear bridges start at z 0, the same level as the
// rails (they used to hang between the rails from z 7.8). Solid down to the Ls'
// top face; assumes nothing sits between the Ls just outside the servo case.
// v5 (Evan, 2026-10-12): the bridges no longer overlap the rails - they span
// only y -12..12, between the rails' inner faces. In v3/v4 the far bridge
// (x 15..20.5) sat on top of both rails and capped the stud-2 pin holes.
// v7 (Evan, 2026-10-12): servo 1.6 mm further forward (+x) and 0.5 mm higher:
// pilots, case opening, bridges and gussets move with SERVO_DX; bridge tops
// 13.3 -> 13.8. Rails and peg holes stay on the Ls; the rail rear end follows
// the near ear (x -14.5 -> -12.9).
// v6 (Evan, 2026-10-12): 4 mm triangular gussets where each bridge meets each
// rail's inner face, z 0..7.8, inside y -12..12 - a bigger bridge-to-rail joint
// with the rail tops and peg holes still clear.
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
RAISE = 6.5;                               // v3 (Evan): 6 mm higher than v2; v7 (Evan): +0.5
EAR_Z = EAR_ABOVE_L_BOTTOM - L_T_UNMEASURED + RAISE;   // bridge top = ear underside (13.8)
RAIL_H = 7.8;                              // a Lego beam's height: a pin half fits fully

CASE_L = 22.88;
CASE_W = 12.44;
CASE_H = 22.60;
EAR_L = 5.0;
EAR_T = 2.65;
EAR_HOLE_FROM_CASE = 2.5;
EAR_HOLE_SPACING = CASE_L + 2 * EAR_HOLE_FROM_CASE;   // 27.88
SERVO_DX = 1.6;                                       // v7 (Evan): servo 1.6 mm further forward (+x)
FAR_HOLE_X = 2 * PITCH + 1.0 + SERVO_DX;              // 18.6 (17.0 Evan, + v7 shift)
NEAR_HOLE_X = FAR_HOLE_X - EAR_HOLE_SPACING;          // -9.28 (v6: -10.88)
CASE_CX = (FAR_HOLE_X + NEAR_HOLE_X) / 2;             // 4.66 (v6: 3.06)

PILOT_D = 1.7;            // pick from the coupon's 1.5 / 1.7 / 1.9 row
PILOT_DEPTH = 6.0;        // screw 7.0 - ear 2.65 = 4.35 into the bridge
OPEN_CLEAR = 0.5;

X0 = NEAR_HOLE_X - EAR_HOLE_FROM_CASE - 1.12;   // -12.9: past the near ear tip (-11.78)
X1 = 3 * PITCH + L_W / 2;                       // 28: the Ls' far end
Y_OUT = L_Y + L_W / 2;                          // 20: outer faces of the Ls
Y_IN = L_Y - L_W / 2;                           // 12: inner faces of the rails (v5 bridge edge)

PIN_X = [PITCH, 2 * PITCH, 3 * PITCH];          // studs 1, 2, 3
NEAR_BRIDGE = [X0, CASE_CX - CASE_L / 2 - OPEN_CLEAR];        // x -12.9 .. -7.28
FAR_BRIDGE = [CASE_CX + CASE_L / 2 + OPEN_CLEAR, FAR_HOLE_X + 3.5];   // x 16.6 .. 22.1

GUSSET = 4.0;             // v6: gusset leg length, along x and along y

// Right-triangle gusset at the corner (x0, Y_IN): one leg on the rail's inner
// face running dir * GUSSET along x, the other on the bridge face running
// GUSSET inward (-y). Overlaps rail and bridge by EPS so the union is one body.
module gusset(x0, dir) {
  linear_extrude(height = RAIL_H)
    polygon([[x0 - dir * EPS, Y_IN + EPS], [x0 + dir * GUSSET, Y_IN + EPS], [x0 - dir * EPS, Y_IN - GUSSET]]);
}

difference() {
  union() {
    // two rails along the Ls
    for (s = [1, -1]) translate([X0, s * L_Y - L_W / 2, 0]) cube([X1 - X0, L_W, RAIL_H]);
    // two bridges under the ears, from the Ls' top face (z 0) like the rails (v4),
    // only BETWEEN the rails (v5): nothing on top of a rail, so no pin hole is capped
    for (b = [NEAR_BRIDGE, FAR_BRIDGE]) translate([b[0], -Y_IN - EPS, 0]) cube([b[1] - b[0], 2 * (Y_IN + EPS), EAR_Z]);
    // v6 gussets: triangles in the corners where a bridge meets a rail's inner face,
    // rail height only, inside y -12..12 (never on a rail top, never near the case cut)
    for (m = [0, 1]) mirror([0, m, 0]) {
      gusset(NEAR_BRIDGE[1], 1);    // near bridge, case side
      gusset(FAR_BRIDGE[0], -1);    // far bridge, case side
      gusset(FAR_BRIDGE[1], 1);     // far bridge, outer side
    }
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
