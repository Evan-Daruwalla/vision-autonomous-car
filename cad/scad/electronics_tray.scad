// Electronics TRAY: PLA tray that pins onto the car's Lego frames and carries the
// battery bank, the battery holder, the charger / small parts, and the deck posts.
// UNTESTED - not printed.
// spec: record GW
// v2 (2026-10-12): encoder-cable notch in the -y rail (x 100..108, z 0..5) and floor slot
// (x 100..108, y -41.0..-38.5); see the record entry of that date.
//
// FRAME: x along the car, x = 0 at the REAR corner pin hole, +x toward the front;
// y across, the Lego pin rows at y = +/-24; z = 0 on the Lego frames' top face, z up. mm.
//
// Layout: two rails (pinned to the frames), a floor with a lightening window, a
// holder lobe (+y), a small-parts lobe (-y), a three-sided bank fence (no rear wall,
// for ports), a holder fence, four feet, and six deck posts (pinned, z up to 30.0).

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;
PIN_D = 4.875;            // pin-hole bore: 4.80 + 0.075 (Evan, 2026-10-12, record GU)

RAIL_H = 7.8;             // a Lego beam's height: a pin half fits fully
FLOOR_T = 2.0;
FLOOR_TOP = RAIL_H + FLOOR_T;   // 9.8
FENCE_T = 2.0;
FENCE_H = 4.0;
FENCE_TOP = FLOOR_TOP + FENCE_H;   // 13.8
POST_TOP = 30.0;
POST_S = 8.0;
FOOT_S = 8.0;

RAIL_Y0 = 20;
RAIL_Y1 = 28;
RAIL_X0 = -4;
RAIL_X1 = 132;
PIN_ROW_Y = 24;
RAIL_PIN_X = [0, 32, 48, 80, 88, 120, 128];

// bank fence interior
BANK_X0 = -4.25;
BANK_X1 = 147.75;
BANK_Y = 35.53;
// holder fence interior
HOLD_X0 = 57.875;
HOLD_X1 = 134.125;
HOLD_Y0 = 37.6;
HOLD_Y1 = 78.6;

FEET = [[64, 60], [124, 60], [64, -60], [124, -60]];
POSTS = [[10, 41.6], [10, -41.6], [150, 41.6], [150, -41.6], [60, -82], [128, -82]];

ZIP_BANK = [[35, 38.5], [35, -38.5], [140, 38.5], [140, -38.5]];
ZIP_HOLDER = [[75, 81.5], [117, 81.5]];
ZIP_SMALL = [[64, -48], [92, -48], [120, -48], [64, -72], [92, -72], [120, -72]];
ZIP_W = 4.0;
ZIP_T = 1.8;

module box(x0, x1, y0, y1, z0, z1) {
  translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
}

difference() {
  union() {
    // 1 rails
    for (s = [1, -1])
      if (s > 0) box(RAIL_X0, RAIL_X1, RAIL_Y0, RAIL_Y1, 0, RAIL_H);
      else box(RAIL_X0, RAIL_X1, -RAIL_Y1, -RAIL_Y0, 0, RAIL_H);
    // 2 floor
    box(-6, 156, -42, 42, RAIL_H, FLOOR_TOP);
    // 3 holder lobe floor
    box(55, 137, 42, 83, RAIL_H, FLOOR_TOP);
    // 4 small-parts lobe floor
    box(56, 132, -86, -42, RAIL_H, FLOOR_TOP);
    // 5 bank fence: front wall and two side walls, no rear wall
    box(BANK_X1, BANK_X1 + FENCE_T, -(BANK_Y + FENCE_T), BANK_Y + FENCE_T, FLOOR_TOP, FENCE_TOP);
    box(BANK_X0, BANK_X1 + FENCE_T, BANK_Y, BANK_Y + FENCE_T, FLOOR_TOP, FENCE_TOP);
    box(BANK_X0, BANK_X1 + FENCE_T, -(BANK_Y + FENCE_T), -BANK_Y, FLOOR_TOP, FENCE_TOP);
    // 6 holder fence: two side walls and the outer wall
    box(HOLD_X0 - FENCE_T, HOLD_X0, HOLD_Y0, HOLD_Y1 + FENCE_T, FLOOR_TOP, FENCE_TOP);
    box(HOLD_X1, HOLD_X1 + FENCE_T, HOLD_Y0, HOLD_Y1 + FENCE_T, FLOOR_TOP, FENCE_TOP);
    box(HOLD_X0 - FENCE_T, HOLD_X1 + FENCE_T, HOLD_Y1, HOLD_Y1 + FENCE_T, FLOOR_TOP, FENCE_TOP);
    // 7 feet
    for (p = FEET) box(p[0] - FOOT_S / 2, p[0] + FOOT_S / 2, p[1] - FOOT_S / 2, p[1] + FOOT_S / 2, 0, RAIL_H);
    // 8 deck posts
    for (p = POSTS) box(p[0] - POST_S / 2, p[0] + POST_S / 2, p[1] - POST_S / 2, p[1] + POST_S / 2, FLOOR_TOP, POST_TOP);
  }
  // 9 lightening window through the floor
  box(8, 140, -18, 18, RAIL_H - EPS, FLOOR_TOP + EPS);
  // 10 rail pin holes, Lego-beam shaped
  for (x = RAIL_PIN_X, s = [1, -1])
    translate([x, s * PIN_ROW_Y, 0]) technic_hole(d = PIN_D, h = RAIL_H, cb_d = 6.2, cb_top = 0.8, cb_bot = 0.8);
  // 11 post pin holes (open at the top, deck pins in)
  for (p = POSTS)
    translate([p[0], p[1], POST_TOP - RAIL_H]) technic_hole(d = PIN_D, h = RAIL_H, cb_d = 6.2, cb_top = 0.8, cb_bot = 0.8);
  // 12 zip slots
  for (p = concat(ZIP_BANK, ZIP_HOLDER, ZIP_SMALL))
    translate([p[0], p[1], RAIL_H - EPS]) zip_slot(ZIP_W, ZIP_T, FLOOR_T + 2 * EPS);
  // 13 encoder-cable notch in the -y rail (x 100..108, between pins 88/120)
  translate([100, -28 - EPS, -EPS]) cube([8, 8 + 2 * EPS, 5.0 + EPS]);
  // 14 encoder-cable floor slot just outside the bank fence (y -41.0..-38.5)
  translate([100, -41.0, RAIL_H - EPS]) cube([8, 2.5, 2.0 + 2 * EPS]);
}

// preview-only ghosts
ghost_box([151.5, 70.55, 18.0], [-4, -35.275, FLOOR_TOP]);          // battery bank
ghost_box([75.75, 40.5, 20.5], [58.125, 37.85, FLOOR_TOP]);         // battery holder
ghost_box([38.5, 18.5, 6.3], [70, -66, FLOOR_TOP]);                 // charger
ghost_box([168, 56, 7.8], [-4, -28, -7.8]);                         // middle frames (approx)
