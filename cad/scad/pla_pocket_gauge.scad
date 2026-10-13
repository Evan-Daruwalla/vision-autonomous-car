// PLA pocket gauge - UNTESTED, not printed (2026-10-13).
// See docs/research/2026-10-12_print-friendly-cad-rules.md Rules 3, 11.
//
// Drop-in width gauges for the three bought parts that sit in printed pockets on
// the electronics tray/deck. Lower each part onto the three gauges of its column;
// the tightest gauge it still drops into without force is the clearance to use.
//
// COLUMNS (nominal part width W): battery bank 70.55, Pi 5 Vilros case 64.4,
// 2S holder 40.5. Per column three segments with clearance per side
// 0.15 / 0.25 / 0.35 (0.25 = fit class "pocket"); the chamfered corner marks the
// 0.15 end (y = 0).
//
// PRINT: flat, floor on the bed, no supports.

use <lib/lego.scad>
EPS = 0.01;
FLOOR_T = 1.2;
WALL_T = 2.0;
WALL_TOP = 5.2;           // floor 1.2 + 4.0 wall, the tray fence height
SEG_L = 10;               // gauge segment length (y)
SEG_Y = [0, 14, 28];      // segment starts
COL_L = 38;               // column floor length (y)
LEAD = 0.5;               // lead-in, as on the tray fences (Rule 5)
P = fit_offset("pocket") / 2;          // 0.25 per side
C = [P - 0.10, P, P + 0.10];           // 0.15 / 0.25 / 0.35 per side
// [label, nominal width W, column x0]
COLS = [["battery bank", 70.55, 0], ["Pi 5 case", 64.4, 81.25], ["2S holder", 40.5, 156.35]];
function col_w(W) = W + 2 * max(C) + 2 * WALL_T;

module lead_in(x0, x1, y0, y1, ztop, c) {
  hull() {
    translate([x0, y0, ztop - c]) cube([x1 - x0, y1 - y0, EPS]);
    translate([x0 - 2 * c, y0 - 2 * c, ztop + c]) cube([x1 - x0 + 4 * c, y1 - y0 + 4 * c, EPS]);
  }
}

difference() {
  union() {
    for (col = COLS) {
      W = col[1]; x0 = col[2]; cx = x0 + col_w(W) / 2;
      translate([x0, 0, 0]) cube([col_w(W), COL_L, FLOOR_T]);
      for (i = [0 : 2]) for (s = [-1, 1]) {
        f = W / 2 + C[i];                         // inner face offset from cx
        translate([s > 0 ? cx + f : cx - f - WALL_T, SEG_Y[i], 0]) cube([WALL_T, SEG_L, WALL_TOP]);
      }
    }
  }
  for (col = COLS) {
    W = col[1]; x0 = col[2]; cx = x0 + col_w(W) / 2;
    for (i = [0 : 2]) lead_in(cx - (W / 2 + C[i]), cx + (W / 2 + C[i]), SEG_Y[i] - 1, SEG_Y[i] + SEG_L + 1, WALL_TOP, LEAD);
    // orientation chamfer at the column's (x0, 0) corner = the 0.15 end
    translate([x0, 0, -EPS]) linear_extrude(WALL_TOP + 2 * EPS) polygon([[-EPS, -EPS], [3, -EPS], [-EPS, 3]]);
  }
}
