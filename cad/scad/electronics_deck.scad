// Electronics DECK v1 (2026-10-12): PLA plate that sits on the six posts of the
// electronics tray and carries the Raspberry Pi 5 case (corner brackets), the
// Arduino Uno (4 standoffs + pegs) and one LM2596 buck board (66 x 36, holes 61 x 31; record FZ) on 4 standoffs + pegs.
// UNTESTED - not printed.
// spec: record GW
// v2 (2026-10-12): encoder-cable slot (x 100..108, y -41.0..-38.5), above the tray's; see the record entry of that date.
// v3 (2026-10-13): print-friendly per docs/research/2026-10-12_print-friendly-cad-rules.md:
// Pi case pocket from fit class "pocket" (was zero clearance; Rules 2, 11), 0.5 lead-in
// chamfer on the Pi bracket tops (Rule 5), 0.4 chamfers on both faces of the rocker hole
// (Rules 5, 6), 0.4 lead-in on the Uno / LM2596 peg tops. Print as modelled: the
// underside (z = 46.0) on the bed. See the record entry of 2026-10-13.
// v4 (2026-10-13): raised 2 mm (underside z 32.0) to clear the tray's 2S holder; LAYOUT
// list = every layer-2 electronic part (preview ghosts + echoed for scripts/electronics_layout.py).
// v6 (2026-10-13): rocker hole 21.0 (body 20.50), LM2596 pegs 57.5 x 31.5, Uno + shield 53.7 x 70 x 24.
// v7 (2026-10-13): underside 32 -> 42 (deck +10 mm for the fuse holder); Uno standoffs 4 -> 6 so
// the USB-B plug (jack centre 13 mm from the Uno's left edge, Evan) clears the boss at (10, -41.6).
// v8 (2026-10-13): underside 42 -> 46 (tray posts follow the velcro-lifted bank); the Pi case
// sits on ~4 mm velcro (Evan; removable), so its brackets go 6 -> 10 mm.
VELCRO = 4.0;             // velcro pair thickness under the Pi case (Evan: roughly 4)
// v9 (2026-10-13): the (unused) Pi zip slots removed - the Pi is held by velcro.
//
// FRAME: x along the car, x = 0 at the REAR corner pin hole, +x toward the front;
// y across, pin rows at y = +/-24; z = 0 on the Lego frames' top face. The deck's
// underside is z = 46.0 (the top of the tray's posts). mm.

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;
PIN_D = lego_pin_d();     // 4.95: lib/lego.scad fit class "friction_pin" (record GU, HG)

// deck levels
DECK_BOT = 46.0;          // top of the tray posts
PLATE_T = 2.5;
DECK_TOP = DECK_BOT + PLATE_T;    // 48.5
BOSS = 8.0;               // pin boss footprint, square
BOSS_H = 7.8;             // a Lego beam's height
BOSS_TOP = DECK_BOT + BOSS_H;     // 53.8

// plate, wing, rocker tab
PLATE_X = [-6, 156];
PLATE_Y = [-42, 42];
WING_X = [56, 132];
WING_Y = [-86, -42];
TAB_X = [-30, -6];
TAB_Y = [-46, -6];

BOSS_XY = [[10, 41.6], [10, -41.6], [150, 41.6], [150, -41.6], [60, -82], [128, -82]];

// Raspberry Pi case and its corner brackets
POCKET_C = fit_offset("pocket") / 2;   // 0.25 per side
PI_X0 = 55.1 - POCKET_C;  // case 55.1..146.9 x -32.2..32.2 (91.8 x 64.4) + pocket clearance
PI_X1 = 146.9 + POCKET_C;
PI_Y0 = -32.2 - POCKET_C;
PI_Y1 = 32.2 + POCKET_C;
BR_T = 1.5;               // bracket wall thickness
BR_LEG = 10.0;            // free leg length beyond the case corner
BR_H = 10.0;              // bracket height above the deck (z 48.5..58.5); 6 -> 10 for the 4 mm velcro
LEAD = 0.5;               // lead-in chamfer on the Pi bracket tops (Rule 5)

// Arduino Uno standoffs and pegs
UNO_XY = [[0.54, -19.05], [15.78, 31.75], [43.72, 31.75], [48.8, -20.32]];
UNO_SO_D = 6.0;
UNO_SO_H = 6.0;           // z 48.5..54.5; was 4: the USB-B plug crosses the boss at (10, -41.6)
UNO_PEG_D = 3.0;
UNO_PEG_H = 3.0;          // z 54.5..57.5

// LM2596 standoffs and pegs
// Evan 2026-10-13: holes 3.5 dia, 61 outer edge to outer edge -> 57.5 centre to centre, 31.5 the other way
LM_XY = [[66.25, -44.25], [123.75, -44.25], [66.25, -75.75], [123.75, -75.75]];
LM_SO_D = 6.0;
LM_SO_H = 3.0;            // z 48.5..51.5
LM_PEG_D = 3.5 - fit_offset("slide");   // 3.2 in the 3.5 holes
LM_PEG_H = 3.0;           // z 51.5..54.5

// cut-outs
VENT_X = [65, 137];
VENT_Y = [-22, 22];
ROCKER_XY = [-18, -32];
ROCKER_D = 20.5 + fit_offset("pocket");   // 21.0: body measured 20.50 (clips 22.90), Evan 2026-10-13
ROCK_CH = 0.4;            // rocker hole chamfer, both faces (Rules 5, 6)
PEG_CH = 0.4;             // lead-in on peg tops

module box(x, y, z) { translate([x[0], y[0], z[0]]) cube([x[1] - x[0], y[1] - y[0], z[1] - z[0]]); }
module lead_in(x0, x1, y0, y1, ztop, c) {
  hull() {
    translate([x0, y0, ztop - c]) cube([x1 - x0, y1 - y0, EPS]);
    translate([x0 - 2 * c, y0 - 2 * c, ztop + c]) cube([x1 - x0 + 4 * c, y1 - y0 + 4 * c, EPS]);
  }
}
// circumscribed cone (flats at the given radii), same polygon as hole_cyl
module chamfer_cone(r_bot, r_top, h) { cylinder(r1 = r_bot / cos(180 / 64), r2 = r_top / cos(180 / 64), h = h, $fn = 64); }
// peg with a PEG_CH lead-in at the top; total height h
module peg(d, h) {
  cylinder(d = d, h = h - PEG_CH + EPS);
  translate([0, 0, h - PEG_CH]) cylinder(d1 = d, d2 = d - 2 * PEG_CH, h = PEG_CH);
}

difference() {
  union() {
    // plate, wing, rocker tab
    box(PLATE_X, PLATE_Y, [DECK_BOT, DECK_TOP]);
    box(WING_X, WING_Y, [DECK_BOT, DECK_TOP]);
    box(TAB_X, TAB_Y, [DECK_BOT, DECK_TOP]);
    // pin bosses
    for (p = BOSS_XY) translate([p[0] - BOSS / 2, p[1] - BOSS / 2, DECK_BOT]) cube([BOSS, BOSS, BOSS_H]);
    // Pi corner brackets, outside the case, two legs per corner
    box([PI_X0 - BR_T, PI_X0 + BR_LEG], [PI_Y0 - BR_T, PI_Y0], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X0 - BR_T, PI_X0], [PI_Y0 - BR_T, PI_Y0 + BR_LEG], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X0 - BR_T, PI_X0 + BR_LEG], [PI_Y1, PI_Y1 + BR_T], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X0 - BR_T, PI_X0], [PI_Y1 - BR_LEG, PI_Y1 + BR_T], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X1 - BR_LEG, PI_X1 + BR_T], [PI_Y0 - BR_T, PI_Y0], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X1, PI_X1 + BR_T], [PI_Y0 - BR_T, PI_Y0 + BR_LEG], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X1 - BR_LEG, PI_X1 + BR_T], [PI_Y1, PI_Y1 + BR_T], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X1, PI_X1 + BR_T], [PI_Y1 - BR_LEG, PI_Y1 + BR_T], [DECK_TOP, DECK_TOP + BR_H]);
    // Uno standoffs + pegs
    for (p = UNO_XY) {
      translate([p[0], p[1], DECK_TOP]) cylinder(d = UNO_SO_D, h = UNO_SO_H);
      translate([p[0], p[1], DECK_TOP + UNO_SO_H]) peg(UNO_PEG_D, UNO_PEG_H);
    }
    // LM2596 standoffs + pegs
    for (p = LM_XY) {
      translate([p[0], p[1], DECK_TOP]) cylinder(d = LM_SO_D, h = LM_SO_H);
      translate([p[0], p[1], DECK_TOP + LM_SO_H]) peg(LM_PEG_D, LM_PEG_H);
    }
  }
  // boss pin holes, Lego-beam shaped
  for (p = BOSS_XY)
    translate([p[0], p[1], DECK_BOT]) technic_hole(d = PIN_D, h = BOSS_H, cb_d = 6.2, cb_top = 0.8, cb_bot = 0.8);
  // Pi vent window
  box(VENT_X, VENT_Y, [DECK_BOT - EPS, DECK_TOP + EPS]);
  // rocker hole
  translate([ROCKER_XY[0], ROCKER_XY[1], DECK_BOT - EPS]) hole_cyl(ROCKER_D, PLATE_T + 2 * EPS);
  // rocker hole chamfers: bed face and top face, 45 deg, ROCK_CH at each face
  translate([ROCKER_XY[0], ROCKER_XY[1], DECK_BOT - ROCK_CH]) chamfer_cone(ROCKER_D / 2 + 2 * ROCK_CH, ROCKER_D / 2 - EPS, 2 * ROCK_CH);
  translate([ROCKER_XY[0], ROCKER_XY[1], DECK_TOP - ROCK_CH]) chamfer_cone(ROCKER_D / 2 - EPS, ROCKER_D / 2 + 2 * ROCK_CH, 2 * ROCK_CH);
  // lead-in on the Pi bracket tops (Rule 5)
  lead_in(PI_X0, PI_X1, PI_Y0, PI_Y1, DECK_TOP + BR_H, LEAD);
  // encoder-cable slot (x 100..108, y -41.0..-38.5), above the tray's
  translate([100, -41.0, DECK_BOT - EPS]) cube([8, 2.5, 2.5 + 2 * EPS]);
}

// preview-only ghosts
// LAYOUT: [name, [sx, sy, sz], [x, y, z], kind, held by, ports]; kind part | zone | note.
LAYOUT = [
  ["velcro under the Pi case (~4 mm)", [91.8, 64.4, VELCRO], [55.1, -32.2, DECK_TOP], "zone", "adhesive both sides", ""],
  ["Raspberry Pi 5 in Vilros case", [91.8, 64.4, 27.2], [55.1, -32.2, DECK_TOP + VELCRO], "part", "velcro + 4 corner brackets (10 mm), pocket +0.25 per side", "+x: camera + USB-C power; -x: 2x USB-A + LAN"],
  ["Arduino Uno R3 + proto shield (TB6612, caps, divider)", [53.7, 70, 24], [-2.18, -35, DECK_TOP + UNO_SO_H], "part", "4 standoffs + pegs", "-y: USB-B (overhangs 7.3) + DC jack (4.1); jack positions NOT measured"],
  ["USB-B plug clearance (16 x 30 x 13 allowance, plug NOT measured)", [16, 30, 13], [3, -72.3, DECK_TOP + UNO_SO_H + 1.6 - 1.0], "clearance", "hangs from the Uno jack", "-y: to the Pi"],
  ["LM2596 buck, 5.00 V (display)", [66, 36, 14], [62, -78, DECK_TOP + LM_SO_H], "part", "4 standoffs + pegs", "display up; trim pot locked"],
  ["rocker switch (20 mm round)", [20, 20, 0], [-28, -42, DECK_TOP], "note", "snap-in 20 mm hole", "body hangs below the tab; depth NOT measured"]
];
for (p = LAYOUT) if (p[3] != "note") ghost_box(p[1], p[2]);
echo(LAYOUT_PARTS = LAYOUT);
echo(LAYOUT_PEGS = concat(UNO_XY, LM_XY));
