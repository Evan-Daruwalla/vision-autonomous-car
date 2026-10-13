// Camera mast v1 (2026-10-12): slide-in camera holder on a mast that anchors to
// the servo-mount rails. UNTESTED - not printed.
// spec: see the record entry of 2026-10-12.
//
// Anchors: rear = 3L friction pins (6558) through mast + servo-mount rail
// stud-2 + L; front = blue axle-pins (43093) in the two free "+" holes.
// Anchor face = L top = 62.09 mm above the floor. Lens target 109 mm abs
// (record HD), pitch 29 deg, lens x 35 (photo, +/-3).
//
// ASSEMBLY ORDER: 3L pins' long side down through servo-mount rail + L (collar
// in the rail's top recess, short side up); axle-pins' axle end down into the
// "+" holes; then the mast drops on over all four from above.
//
// PRINT: print base-down; enable supports for the holder's 29-deg bottom.
//
// FRAME = the servo-mount frame: origin on the servo shaft axis, x forward
// (studs 1-3 at x 8, 16, 24), y across (L rows at y +/-16), z = 0 on the L
// tops (62.09 mm above the floor). mm.

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;
PIN_D = 4.95;              // 4.80 + 0.075 (record GU) + 0.075 (Evan, 2026-10-12)
PITCH = 29.0;
LENS_X = 35.0;
LENS_Z = 46.91;   // 109.0 - 62.09
O_X = 28.4503;    // board centre on the PCB back face (Opus, from LENS_X/Z, pitch,
O_Z = 47.7176;    // 5.0 lens-ahead + 1.12 PCB, lens 2.469 above board centre)

// Holder transform (local X = world y, local Y = board up, local Z = board normal, forward).
module board_frame() multmatrix([[0, sin(PITCH), cos(PITCH), O_X], [1, 0, 0, 0],
                                 [0, cos(PITCH), -sin(PITCH), O_Z], [0, 0, 0, 1]]) children();

// a = min corner, b = max corner
module box(a, b) translate(a) cube(b - a);

UPRIGHT_PTS = [[12, 15.59], [36, 15.59], [38.3968, 60.3606], [31.12, 64.3942], [17.1289, 38.6379]];
RIB_PTS = [[28.3, 7.79], [32, 7.79], [19.666, 41.154], [17.1289, 38.6379]];

difference() {
  union() {
    // 1 base
    box([28.3, -20, 0], [36, 20, 7.8 + EPS]);
    // 2 side members
    box([12, 12.3, 7.8], [36, 20, 15.6]);
    box([12, -20, 7.8], [36, -12.3, 15.6]);
    // 3 uprights
    for (Y1 = [16.3, -12.7])
      translate([0, Y1, 0]) rotate([90, 0, 0]) linear_extrude(height = 3.6) polygon(UPRIGHT_PTS);
    // 4 ribs
    for (Y1 = [11.0, -9.0])
      translate([0, Y1, 0]) rotate([90, 0, 0]) linear_extrude(height = 2.0) polygon(RIB_PTS);
    // 5 holder, in the board frame
    board_frame() {
      // H1 back plate
      box([-14.5, -13.93, -6.0], [14.5, 11.93, -3.0]);
      // H2 side walls
      box([12.7, -13.93, -6.0], [14.5, 16.13, 2.82]);
      box([-14.5, -13.93, -6.0], [-12.7, 16.13, 2.82]);
      // H3 back ledges
      box([11.0, -11.93, -3.0], [12.7, 11.93, 0.0]);
      box([-12.7, -11.93, -3.0], [-11.0, 11.93, 0.0]);
      // H4 front lips
      box([11.3, -13.93, 1.32], [12.7, 11.93, 2.82]);
      box([-12.7, -13.93, 1.32], [-11.3, 11.93, 2.82]);
      // H5 bottom stops
      box([10.0, -13.93, -3.0], [12.7, -12.13, 1.32]);
      box([-12.7, -13.93, -3.0], [-10.0, -12.13, 1.32]);
    }
  }
  // 6 front pin holes
  for (s = [1, -1])
    translate([32, s * 16, 0]) technic_hole(d = PIN_D, h = 15.6, cb_d = 6.2, cb_top = 0.8, cb_bot = 0.8);
  // 7 rear pin holes
  for (s = [1, -1])
    translate([16, s * 16, 7.8]) technic_hole(d = PIN_D, h = 7.8, cb_d = 6.2, cb_top = 0.8, cb_bot = 0.8);
  // 8 stud-3 relief
  for (s = [1, -1])
    translate([24, s * 16, 7.8 - EPS]) hole_cyl(6.6, 0.6 + EPS);
  // 9 retaining-pin hole (a 1.75 mm filament rod across the top of the board)
  translate([35.3057, -17.5, 58.9299]) rotate([-90, 0, 0]) hole_cyl(2.0, 35);
}

// preview-only ghosts
% board_frame() box([-12.5, -11.931, 0], [12.5, 11.931, 1.12]);
% board_frame() translate([-5.4, 2.469 - 5.4, 1.12]) cube([10.8, 10.8, 8.3]);   // lens block
% box([-6.78, -6.22, 12.3], [16.1, 6.22, 34.9]);                                // servo case (servo mount v7 position)
% box([-14.5, 12, 0], [28, 20, 7.8]);                                           // servo-mount rails
% mirror([0, 1, 0]) box([-14.5, 12, 0], [28, 20, 7.8]);
