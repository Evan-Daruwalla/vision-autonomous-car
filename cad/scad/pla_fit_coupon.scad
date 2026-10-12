// PLA fit coupon (2026-10-11): one small print for the PLA fit questions behind
// the printed Lego-interface mounts.
//
// WHAT IT TESTS
//   - PLA pin-hole fit, plain (row A) and counterbored (row B), over six
//     diameters 4.75 .. 5.00 mm in 0.05 mm steps.
//   - Pitch (row C): six 4.90 mm holes at 8 mm spacing, to lay a real liftarm over.
//   - Horizontal pin holes (fin): axis along Y, 4.8 / 4.9 / 5.0 mm, through the
//     fin and out above the pilot block.
//   - Self-tapping servo-screw pilot holes: 1.5 / 1.7 / 1.9 mm.
//   - Zip-tie slots: 3.0 / 3.5 / 4.0 / 5.0 mm wide, 1.8 mm thick.
//
// ORIENTATION: the chamfered corner at x=0, y=0 marks the 4.75 end. Diameters
// grow along +X in rows A and B.
//
// MAP (mm; x right, y back, z up; 72 x 34 x 17 overall)
//   Region 1, plate x 0..48, y 0..24, z 0..7.8
//     row A  y=4   plain holes, x = 4, 12, 20, 28, 36, 44
//     row B  y=12  counterbored (top, 0.8 deep, 6.2 dia), same x and diameters
//     row C  y=20  pitch check, all 4.90 dia, same x
//   Region 2, fin x 48..72, y 0..7.8, z 0..17
//     horizontal holes along +Y at z=12.5, x = 52, 60, 68 (4.8 / 4.9 / 5.0);
//     they exit the fin's back face above the region 3 block (top z=7.8), so a
//     pin can pass through and take a beam on the far side
//   Region 3, block x 48..72, y 7.8..24, z 0..7.8
//     pilot holes at y=16, x = 52, 60, 68 (1.5 / 1.7 / 1.9)
//   Region 4, strip x 0..72, y 24..34, z 0..3
//     zip slots at y=29, x = 9, 27, 45, 63 (3.0 / 3.5 / 4.0 / 5.0 wide)
//
// Render with scripts/render_scad.py: it checks the mesh against
// pla_fit_coupon.probe.json before it writes cad/pla_fit_coupon.stl.

use <lib/lego.scad>
T = 7.8;
DIAS = [4.75, 4.80, 4.85, 4.90, 4.95, 5.00];
EPS = 0.01;
difference() {
  union() {
    cube([48, 24, T]);                          // region 1: rows A, B, C
    translate([48, 0, 0]) cube([24, T, 17]);    // region 2: horizontal-hole fin
    translate([48, T, 0]) cube([24, 24 - T, T]); // region 3: pilot holes
    translate([0, 24, 0]) cube([72, 10, 3]);    // region 4: zip-slot strip
  }
  for (i = [0 : 5]) translate([4 + 8 * i, 4, 0]) technic_hole(d = DIAS[i], h = T);               // row A plain
  for (i = [0 : 5]) translate([4 + 8 * i, 12, 0]) technic_hole(d = DIAS[i], h = T, cb_top = 0.8); // row B counterbored
  for (i = [0 : 5]) translate([4 + 8 * i, 20, 0]) technic_hole(d = 4.90, h = T);                  // row C pitch check
  for (i = [0 : 2]) translate([52 + 8 * i, 0, 12.5]) rotate([-90, 0, 0]) technic_hole(d = [4.8, 4.9, 5.0][i], h = T); // horizontal, along +Y
  for (i = [0 : 2]) translate([52 + 8 * i, 16, 0]) pilot_hole([1.5, 1.7, 1.9][i], T);
  for (i = [0 : 3]) translate([9 + 18 * i, 29, 0]) zip_slot(w = [3.0, 3.5, 4.0, 5.0][i], t = 1.8, h = 3);
  translate([0, 0, -EPS]) linear_extrude(T + 1) polygon([[-EPS, -EPS], [1.5, -EPS], [-EPS, 1.5]]); // orientation chamfer at the 4.75 corner
}
