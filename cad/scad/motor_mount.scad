// Motor mount, 2026-10-11 (v2, v3 2026-10-12): printable PLA mount for the drive
// motor on the Lego Technic frame.
//
// v3 (record GT): floor 2.5 mm higher, back wall 2 mm closer to the motor.
// v4 (record GW): walls + floor 11 mm longer at the front, walls 0.2 mm in,
// a 1.5 x 1.5 front lip on each wall. Evan accepted the risk that the longer
// floor runs under the coupler.
// STATUS: UNTESTED as v4. v1 (printed pin stubs, full-length side walls) was
// printed by Evan: dimensions "alright", but the back third of the side walls
// hit the encoder housing (record GL). v2: those wall sections removed, a back
// wall added, and REAL black friction pins instead of printed stubs.
//
// FRAME: x along the axle (+x toward the coupler/diff), x=0 on the A/B pin line;
// y lateral (A at +16, B at -16); z = height above the floor, car upright.
//
// PIN SOCKETS follow the Technic pin geometry in
// docs/research/2026-10-12_technic-pin-snap-geometry.md: each arm's top 7.8 mm
// is shaped like a Lego beam (6.2 x 0.8 recess for the pin's collar, 4.875 bore),
// with a 6.2 cavity below it where the pin's 5.2 mm tip lip snaps in.
// The pin goes into beam A/B from below; the arm then pushes up onto its lower half.
//
// Render with scripts/render_scad.py: it checks the mesh against
// motor_mount.probe.json before it writes cad/motor_mount.stl.

use <lib/lego.scad>

EPS = 0.01;

FLOOR_Z0 = 21.0;         // v3 (2026-10-12, Evan): floor up 2.5 mm (was 18.5)
FLOOR_Z1 = 23.4;         // was 20.9
WALL_TOP = 26.2;
WALL_IN = 6.2;             // v4 (Evan): walls closed in 0.2 mm each (was 6.4)
WALL_OUT = 8.4;
WALL_X0 = 3;              // v2: walls start here; the back third (to the encoder) is gone
WALL_X1 = 26;             // v4 (Evan): walls and floor 11 mm longer at the front (was 15)
LIP_T = 1.5;              // v4: front lip, 1.5 thick (x 26..27.5) ...
LIP_IN = 1.5;             // ... sticking 1.5 inward from each wall; sides only, no floor lip
ARM_Y0 = 11.6;
ARM_Y1 = 19.9;            // room for the 6.2 recess/cavity around a pin at y 16
PIN_Y = 16;
BEAM_UNDER = 33.13;       // underside of the short beams holding A/B (record GI)
ARM_TOP = BEAM_UNDER;     // flush, like two pinned Lego beams
PIN_D = 4.875;            // 4.80 + 0.075 (Evan, 2026-10-12, record GU)
RECESS_D = 6.2;           // cailliau, measured; coupon row B tests it in PLA
RECESS_DEPTH = 0.8;
BORE_L = 6.2;             // as in a real 7.8 mm beam (7.8 - 2 x 0.8)
SNAP_CAV_H = 2.0;         // tip lip is 0.8 long; extra height tolerates pin length
ZIP_W = 4.0;
ZIP_T = 1.8;
ZIP_Y = 9.35;
ZIP_X = [3, 11];
GROOVE_DEPTH = 1.4;

// Back wall behind the encoder end (2026-10-11, Evan: "there needs to be a back"):
// stops the motor backing out of the coupler. The encoder's back end at x -7.85
// is a PHOTO estimate (IMG_0212); BACK_GAP leaves it free to sit fully in the coupler.
ENCODER_END_X_UNMEASURED = -7.85;
BACK_GAP = 0.5;
BACK_T = 2.0;
BACK_TOP = 28.0;          // below the connector (z 31.45 up)
BACK_RELIEF_D = 7.0;      // the wall bears on the rim of the encoder cap, not its centre
BACK_SHIFT = 2.0;         // v3 (Evan): back wall 2 mm toward the motor's front
BACK_X = ENCODER_END_X_UNMEASURED - BACK_GAP + BACK_SHIFT;   // inner face of the back wall (-6.35)
AXLE_Z = 26.2;

// Negative volume: one pin socket, top face at z = ARM_TOP.
module pin_socket() {
  z_bore0 = ARM_TOP - RECESS_DEPTH - BORE_L;
  translate([0, 0, ARM_TOP - RECESS_DEPTH]) hole_cyl(RECESS_D, RECESS_DEPTH + EPS);   // collar recess
  translate([0, 0, z_bore0 - EPS]) hole_cyl(PIN_D, BORE_L + 2 * EPS);              // bore
  translate([0, 0, z_bore0 - SNAP_CAV_H]) hole_cyl(RECESS_D, SNAP_CAV_H);         // snap cavity
}

difference() {
  union() {
    // 1 floor
    translate([-4, -18.2, FLOOR_Z0]) cube([19, 36.4, FLOOR_Z1 - FLOOR_Z0]);
    // 1b floor tongue out to the back wall
    translate([BACK_X - BACK_T, -WALL_OUT, FLOOR_Z0]) cube([-4 - (BACK_X - BACK_T) + EPS, 2 * WALL_OUT, FLOOR_Z1 - FLOOR_Z0]);
    // 1c v4 floor extension under the longer walls and the lip
    translate([15 - EPS, -WALL_OUT, FLOOR_Z0]) cube([WALL_X1 + LIP_T - 15 + EPS, 2 * WALL_OUT, FLOOR_Z1 - FLOOR_Z0]);
    // 2 side walls and their y-mirror
    translate([WALL_X0, WALL_IN, FLOOR_Z1]) cube([WALL_X1 - WALL_X0, WALL_OUT - WALL_IN, WALL_TOP - FLOOR_Z1]);
    translate([WALL_X0, -WALL_OUT, FLOOR_Z1]) cube([WALL_X1 - WALL_X0, WALL_OUT - WALL_IN, WALL_TOP - FLOOR_Z1]);
    // 2c v4 front lip: parallel to the back wall, catches the gearbox front plate
    translate([WALL_X1, WALL_IN - LIP_IN, FLOOR_Z1]) cube([LIP_T, WALL_OUT - WALL_IN + LIP_IN, WALL_TOP - FLOOR_Z1]);
    translate([WALL_X1, -WALL_OUT, FLOOR_Z1]) cube([LIP_T, WALL_OUT - WALL_IN + LIP_IN, WALL_TOP - FLOOR_Z1]);
    // 2b back wall
    translate([BACK_X - BACK_T, -WALL_OUT, FLOOR_Z1]) cube([BACK_T, 2 * WALL_OUT, BACK_TOP - FLOOR_Z1]);
    // 3 arms and their y-mirror
    translate([-4, ARM_Y0, FLOOR_Z0]) cube([8, ARM_Y1 - ARM_Y0, ARM_TOP - FLOOR_Z0]);
    translate([-4, -ARM_Y1, FLOOR_Z0]) cube([8, ARM_Y1 - ARM_Y0, ARM_TOP - FLOOR_Z0]);
  }
  // 4 pin sockets
  for (s = [1, -1]) translate([0, s * PIN_Y, 0]) pin_socket();
  // 5 zip slots through the floor
  for (x = ZIP_X, y = [ZIP_Y, -ZIP_Y])
    translate([x, y, FLOOR_Z0]) zip_slot(ZIP_W, ZIP_T, FLOOR_Z1 - FLOOR_Z0);
  // 6 underside grooves joining each slot pair
  for (x = ZIP_X)
    translate([x - ZIP_W / 2, -(ZIP_Y + 0.9), FLOOR_Z0 - EPS])
      cube([ZIP_W, 2 * (ZIP_Y + 0.9), GROOVE_DEPTH + EPS]);
  // 7 relief through the back wall on the axle line
  translate([BACK_X - BACK_T - EPS, 0, AXLE_Z]) rotate([0, 90, 0])
    cylinder(d = BACK_RELIEF_D, h = BACK_T + 2 * EPS, $fn = 64);
}

// Ghosts (preview only)
ghost_box([24, 12, 10], [0, -6, 21.2]);            // gearbox + can
ghost_box([8, 12.5, 10.5], [-8, -6.25, 20.95]);    // encoder
ghost_box([6, 9.6, 3.75], [-7, -4.8, 31.45]);      // connector
ghost_box([24, 8, 8], [-12, 12, 33.13]);           // beam A
ghost_box([24, 8, 8], [-12, -20, 33.13]);          // beam B
ghost_box([32, 8, 8], [-8, 18.75, 22.5]);          // white beam (assumed)
ghost_box([32, 8, 8], [-8, -26.75, 22.5]);         // white beam (assumed)
