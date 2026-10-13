// Electronics TRAY: PLA tray that pins onto the car's Lego frames and carries the
// battery bank, the battery holder, the charger / small parts, and the deck posts.
// UNTESTED - not printed.
// spec: record GW
// v2 (2026-10-12): encoder-cable notch in the -y rail (x 100..108, z 0..5) and floor slot
// (x 100..108, y -41.0..-38.5); see the record entry of that date.
// v3 (2026-10-13): print-friendly per docs/research/2026-10-12_print-friendly-cad-rules.md:
// ribs under the floor so every overhang is a bridge <= ~20 mm (Rule 7), zip-tie
// notches in the ribs, -y feet moved off the small-parts tie paths, holder lobe to
// y 85 (tie strip 0.6 -> 2.6 mm, Rule 8), 45 deg wedges under the four outer posts,
// pockets from fit class "pocket" (Rules 2, 11), 0.5 lead-in chamfers on the pocket
// tops (Rule 5). Print as modelled: z = 0 on the bed. See the record entry of 2026-10-13.
// v4 (2026-10-13): deck raised 2 mm (posts to z 32.0) - the 2S holder (20.5 tall, top
// z 30.3) hit the deck underside at 30.0. LAYOUT list = every layer-1 electronic part
// (preview ghosts + echoed for scripts/electronics_layout.py).
// v5 (2026-10-13): fences 4 -> 10 mm tall. The PETG pocket gauge showed the bank ~2 mm
// loose in a 4 mm fence: its edges are rounded and its sides are flat only from 7 mm
// above its bottom (Evan). Pocket width unchanged (70.55 + 0.25 per side). Zip slots 3.5.
//
// FRAME: x along the car, x = 0 at the REAR corner pin hole, +x toward the front;
// y across, the Lego pin rows at y = +/-24; z = 0 on the Lego frames' top face, z up. mm.
//
// Layout: two rails (pinned to the frames), a floor with a lightening window, a
// holder lobe (+y), a small-parts lobe (-y), a three-sided bank fence (no rear wall,
// for ports), a holder fence, four feet, ribs under the floor, and six deck posts (pinned, z up to 32.0).

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;
PIN_D = lego_pin_d();     // 4.95: lib/lego.scad fit class "friction_pin" (record GU, HG)

RAIL_H = 7.8;             // a Lego beam's height: a pin half fits fully
FLOOR_T = 2.0;
FLOOR_TOP = RAIL_H + FLOOR_T;   // 9.8
FENCE_T = 2.0;
FENCE_H = 10.0;           // v5: past the bank's rounded bottom edge (flat side from 7 mm up, Evan 2026-10-13)
FENCE_TOP = FLOOR_TOP + FENCE_H;   // 19.8
POST_TOP = 32.0;
POST_S = 8.0;
FOOT_S = 8.0;

RAIL_Y0 = 20;
RAIL_Y1 = 28;
RAIL_X0 = -4;
RAIL_X1 = 132;
PIN_ROW_Y = 24;
RAIL_PIN_X = [0, 32, 48, 80, 88, 120, 128];

// pockets: the bought part's footprint + fit class "pocket" (0.25 per side)
POCKET_C = fit_offset("pocket") / 2;
BANK_POS = [-4, -35.275];  BANK_SIZE = [151.5, 70.55];    // battery bank
HOLD_POS = [58.125, 37.85]; HOLD_SIZE = [75.75, 40.5];    // 2S holder
// bank fence interior
BANK_X0 = BANK_POS[0] - POCKET_C;
BANK_X1 = BANK_POS[0] + BANK_SIZE[0] + POCKET_C;
BANK_Y = BANK_SIZE[1] / 2 + POCKET_C;
// holder fence interior
HOLD_X0 = HOLD_POS[0] - POCKET_C;
HOLD_X1 = HOLD_POS[0] + HOLD_SIZE[0] + POCKET_C;
HOLD_Y0 = HOLD_POS[1] - POCKET_C;
HOLD_Y1 = HOLD_POS[1] + HOLD_SIZE[1] + POCKET_C;

FEET = [[64, 60], [124, 60], [78, -60], [106, -60]];   // -y feet clear of the small-parts tie paths (v3)
POSTS = [[10, 41.6], [10, -41.6], [150, 41.6], [150, -41.6], [60, -82], [128, -82]];

ZIP_BANK = [[35, 38.5], [35, -38.5], [140, 38.5], [140, -38.5]];
ZIP_HOLDER = [[75, 81.5], [117, 81.5]];
ZIP_SMALL = [[64, -48], [92, -48], [120, -48], [64, -72], [92, -72], [120, -72]];
ZIP_W = 3.5;              // PETG coupon: 3.5 x 1.8 passes the ties easily, no slop (2026-10-13)
ZIP_T = 1.8;
RIB_T = 2.0;              // ribs under the floor (Rule 7)
TIE_Z0 = 5.3;             // zip-tie passage under the floor: z TIE_Z0..RAIL_H
LEAD = 0.5;               // lead-in chamfer on pocket tops (Rule 5)

module box(x0, x1, y0, y1, z0, z1) {
  translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
}
module rib(x0, x1, y0, y1) { box(x0, x1, y0, y1, 0, RAIL_H + EPS); }
module tie_notch(x0, x1, y0, y1) { translate([x0, y0 - EPS, TIE_Z0]) cube([x1 - x0, y1 - y0 + 2 * EPS, RAIL_H - TIE_Z0]); }
module lead_in(x0, x1, y0, y1, ztop, c) {
  hull() {
    translate([x0, y0, ztop - c]) cube([x1 - x0, y1 - y0, EPS]);
    translate([x0 - 2 * c, y0 - 2 * c, ztop + c]) cube([x1 - x0 + 4 * c, y1 - y0 + 4 * c, EPS]);
  }
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
    box(55, 137, 42, 85, RAIL_H, FLOOR_TOP);
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
    // 8b ribs under the floor (Rule 7): edge ribs, rear skirt, rear cross, front cross, front skirt
    rib(-6, 156, 40, 42); rib(-6, 156, -42, -40);
    rib(-6, -4, -42, 42); rib(5, 7, -42, 42); rib(144, 146, -42, 42); rib(154, 156, -42, 42);
    // holder lobe: outer skirt, two sides, middle
    rib(55, 137, 83, 85); rib(55, 57, 42, 85); rib(135, 137, 42, 85); rib(55, 137, 61.5, 63.5);
    // small-parts lobe: outer skirt, two sides, middle
    rib(56, 132, -86, -84); rib(56, 58, -86, -42); rib(130, 132, -86, -42); rib(56, 132, -64, -62);
    // 8c 45 deg wedges under the four outer posts, which overhang the floor edge (|y| 42) by 3.6
    for (px = [10, 150], s = [1, -1]) {
      d = 41.6 + POST_S / 2 - 42;     // 3.6
      hull() {
        translate([px - POST_S / 2, s > 0 ? 42 - EPS : -42, FLOOR_TOP - d]) cube([POST_S, EPS, d + EPS]);
        translate([px - POST_S / 2, s > 0 ? 42 + d - EPS : -42 - d, FLOOR_TOP - EPS]) cube([POST_S, EPS, 2 * EPS]);
      }
    }
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
  // 15 encoder-cable notch through the -y edge rib, full height, under the floor slot
  translate([100, -42 - EPS, -EPS]) cube([8, 2 + 2 * EPS, RAIL_H + EPS]);
  // 16 zip-tie notches in the ribs (z TIE_Z0..RAIL_H): bank ties around the floor edge,
  // holder ties around the lobe edge, small-parts ties under the lobe between slot pairs
  for (x = [35, 140], s = [1, -1]) tie_notch(x - 3, x + 3, s > 0 ? 40 : -42, s > 0 ? 42 : -40);
  for (x = [75, 117]) tie_notch(x - 3, x + 3, 83, 85);
  for (x = [64, 92, 120]) tie_notch(x - 3, x + 3, -64, -62);
  // 17 lead-in chamfers on the pocket tops (Rule 5)
  lead_in(BANK_X0, BANK_X1, -BANK_Y, BANK_Y, FENCE_TOP, LEAD);
  lead_in(HOLD_X0, HOLD_X1, HOLD_Y0, HOLD_Y1, FENCE_TOP, LEAD);
}

// preview-only ghosts
// LAYOUT: [name, [sx, sy, sz], [x, y, z], kind, held by, ports]; kind part | zone | note.
// A zone reserves space for a part whose size is NOT measured.
LAYOUT = [
  ["battery bank (Pi power)", [151.5, 70.55, 18.0], [-4, -35.275, FLOOR_TOP], "part", "bank fence, open at the rear", "-x: USB-C + USB-A (20 / 45 mm from the left)"],
  ["2S holder + 2x Samsung 25R", [75.75, 40.5, 20.5], [58.125, 37.85, FLOOR_TOP], "part", "holder fence + 2 zip ties (slots x 75, 117)", "leads red / black + MB wire; exit end not measured"],
  ["USB-C 2S charger (Adeept p0374)", [38.43, 18.3, 6.3], [60, -69.5, FLOOR_TOP], "part", "zip ties at x 64 and 92", "pads BAT, GND, GND, VIN; USB-C side not stated"],
  ["2S BMS (ACEIRMC B08HLQQCQJ)", [41, 8, 2.2], [66, -83, FLOOR_TOP], "part", "double-sided tape", "pads B+ B- MB P+ P-"],
  ["XT30 pair, mated (25 x 10.5 x 5.3)", [25, 10.5, 5.3], [104, -66, FLOOR_TOP], "part", "zip tie at x 120", "BMS P+ / P- side; car side to the rocker"]
];
for (p = LAYOUT) if (p[3] != "note") ghost_box(p[1], p[2]);
echo(LAYOUT_PARTS = LAYOUT);
ghost_box([168, 56, 7.8], [-4, -28, -7.8]);                         // middle frames (approx)
