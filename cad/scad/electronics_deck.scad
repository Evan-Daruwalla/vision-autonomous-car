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
VELCRO = 3.5;             // velcro pair thickness under the Pi case (Evan 2026-10-16: measured 3.5 per mated pair, 15.5 mm dots)
// v9 (2026-10-13): the (unused) Pi zip slots removed - the Pi is held by velcro.
// v10 (2026-10-16): underside 46 -> 54.5 (deck +8.5, Evan): the new 168 x 62.16 x 22.51 power bank is 4.5 taller and the fuse holder on it now sits on ~4 mm velcro. Rear rocker tab deleted (the longer bank and its rear USB cables sit there); the rocker moves to the -y wing (WING_X 56 -> 24), hole at (42, -64), body hangs to z 30.7, clear of the rear wheels (peak z 11, Evan). New 8 x 4 power slot (x 38..46, y -49.5..-45.5) for VBAT / GND from the rocker up to the shield.
// v11 (2026-10-16): room for wires and connectors (Evan). Plate rear edge -6 -> -64; rear bosses x 10 -> -12; Pi case 55.1 -> 40.0 (front USB-C plug + bend clear of the camera mast); Uno moved back 56 mm behind a 40 mm USB-A plug zone, two 3 mm ribs under it stiffen the 52 mm cantilever; Pi bracket legs on the port ends 10 -> 4 mm (BR_LEG_END) so they don't block the outer plugs; vent window follows the Pi. LAYOUT: clearance boxes reserve plug, cable and access space.
// v12 (2026-10-16): Evan's bench results - velcro 3.5 per mated pair (15.5 mm dots); Pi USB/LAN ports sit 4 mm from the case sides, so both -x end bracket legs are removed; the Pi's USB-C is on its -y SIDE 7 mm from the +x end (not the back), so the -y side leg at the +x corner is removed and the -y wing is re-ordered: LM2596 x 10..76, rocker at (100, -64) over the XT30 / charger, power slot x 96..104; WING_X 24 -> 0.
// v13 (2026-10-20): LM2596 moved +4 in y (y -74..-38, pegs y -40.25 / -71.75): Evan saw the board
// flush against the lobe boss at (60, -82), which rises 2.3 mm above the board's underside. The layout
// checker now also fails a part whose side touches material (SIDE_CLEAR 0.2).
//
// FRAME: x along the car, x = 0 at the REAR corner pin hole, +x toward the front;
// y across, pin rows at y = +/-24; z = 0 on the Lego frames' top face. The deck's
// underside is z = 54.5 (the top of the tray's posts). mm.

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;
PIN_D = lego_pin_d();     // 4.95: lib/lego.scad fit class "friction_pin" (record GU, HG)

// deck levels
DECK_BOT = 54.5;          // top of the tray posts (v10: 46 -> 54.5)
PLATE_T = 2.5;
DECK_TOP = DECK_BOT + PLATE_T;    // 48.5
BOSS = 8.0;               // pin boss footprint, square
BOSS_H = 7.8;             // a Lego beam's height
BOSS_TOP = DECK_BOT + BOSS_H;     // 53.8

// plate, wing
PLATE_X = [-64, 156];
PLATE_Y = [-42, 42];
WING_X = [0, 132];
WING_Y = [-86, -42];

BOSS_XY = [[-12, 41.6], [-12, -41.6], [150, 41.6], [150, -41.6], [60, -82], [128, -82]];

// Raspberry Pi case and its corner brackets
POCKET_C = fit_offset("pocket") / 2;   // 0.25 per side
PI_X0 = 40.0 - POCKET_C;  // case 40.0..131.8 x -32.2..32.2 (91.8 x 64.4) + pocket clearance
PI_X1 = 131.8 + POCKET_C;
PI_Y0 = -32.2 - POCKET_C;
PI_Y1 = 32.2 + POCKET_C;
BR_T = 1.5;               // bracket wall thickness
BR_LEG = 10.0;            // free leg length beyond the case corner
BR_LEG_END = 4.0;         // v11: leg length on the port ends (the y-running legs), so they don't block the outer plugs
BR_H = 10.0;              // bracket height above the deck (z 48.5..58.5); 6 -> 10 for the 4 mm velcro
LEAD = 0.5;               // lead-in chamfer on the Pi bracket tops (Rule 5)

// Arduino Uno standoffs and pegs
UNO_XY = [[-55.46, -19.05], [-40.22, 31.75], [-12.28, 31.75], [-7.2, -20.32]];
UNO_SO_D = 6.0;
UNO_SO_H = 6.0;           // z 48.5..54.5; was 4: the USB-B plug crosses the boss at (10, -41.6)
UNO_PEG_D = 3.0;
UNO_PEG_H = 3.0;          // z 54.5..57.5

// LM2596 standoffs and pegs
// Evan 2026-10-13: holes 3.5 dia, 61 outer edge to outer edge -> 57.5 centre to centre, 31.5 the other way
LM_XY = [[14.25, -40.25], [71.75, -40.25], [14.25, -71.75], [71.75, -71.75]];   // v13: +4 in y, 4 mm clear of the boss at (60, -82)
LM_SO_D = 6.0;
LM_SO_H = 3.0;            // z 48.5..51.5
LM_PEG_D = 3.5 - fit_offset("slide");   // 3.2 in the 3.5 holes
LM_PEG_H = 3.0;           // z 51.5..54.5

// cut-outs
VENT_X = [50, 122];
VENT_Y = [-22, 22];
ROCKER_XY = [100, -64];
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
    // plate, wing
    box(PLATE_X, PLATE_Y, [DECK_BOT, DECK_TOP]);
    box(WING_X, WING_Y, [DECK_BOT, DECK_TOP]);
    // pin bosses
    for (p = BOSS_XY) translate([p[0] - BOSS / 2, p[1] - BOSS / 2, DECK_BOT]) cube([BOSS, BOSS, BOSS_H]);
    // Pi corner brackets, outside the case, two legs per corner
    box([PI_X0 - BR_T, PI_X0 + BR_LEG], [PI_Y0 - BR_T, PI_Y0], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X0 - BR_T, PI_X0 + BR_LEG], [PI_Y1, PI_Y1 + BR_T], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X1, PI_X1 + BR_T], [PI_Y0 - BR_T, PI_Y0 + BR_LEG_END], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X1 - BR_LEG, PI_X1 + BR_T], [PI_Y1, PI_Y1 + BR_T], [DECK_TOP, DECK_TOP + BR_H]);
    box([PI_X1, PI_X1 + BR_T], [PI_Y1 - BR_LEG_END, PI_Y1 + BR_T], [DECK_TOP, DECK_TOP + BR_H]);
    // Uno standoffs + pegs
    for (p = UNO_XY) {
      translate([p[0], p[1], DECK_TOP]) cylinder(d = UNO_SO_D, h = UNO_SO_H);
      translate([p[0], p[1], DECK_TOP + UNO_SO_H]) peg(UNO_PEG_D, UNO_PEG_H);
    }
    // v11: stiffening ribs under the Uno (cantilever past the rear posts)
    for (ry = [-12, 12]) box([-60, -6], [ry - 1, ry + 1], [DECK_TOP - EPS, DECK_TOP + 3]);
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
  // power slot: VBAT / GND from the rocker (below the wing) up to the shield
  box([96, 104], [-49.5, -45.5], [DECK_BOT - EPS, DECK_TOP + EPS]);
  // lead-in on the Pi bracket tops (Rule 5)
  lead_in(PI_X0, PI_X1, PI_Y0, PI_Y1, DECK_TOP + BR_H, LEAD);
  // encoder-cable slot (x 100..108, y -41.0..-38.5), above the tray's
  translate([100, -41.0, DECK_BOT - EPS]) cube([8, 2.5, 2.5 + 2 * EPS]);
}

// preview-only ghosts
// LAYOUT: [name, [sx, sy, sz], [x, y, z], kind, held by, ports]; kind part | zone | note.
LAYOUT = [
  ["velcro under the Pi case (3.5 mm pair)", [91.8, 64.4, VELCRO], [40.0, -32.2, DECK_TOP], "zone", "adhesive both sides", ""],
  ["Raspberry Pi 5 in Vilros case", [91.8, 64.4, 27.2], [40.0, -32.2, DECK_TOP + VELCRO], "part", "velcro + brackets: +x end legs 4 mm, +y side legs, -y side leg at the -x corner (ports clear)", "+x: camera opening (mid-face); -y side: USB-C 7 mm from the +x end; -x: USB-A + LAN (4 mm from the sides)"],
  ["Arduino Uno R3 + proto shield (TB6612, caps, divider)", [53.7, 70, 24], [-58.18, -35, DECK_TOP + UNO_SO_H], "part", "4 standoffs + pegs", "-y: USB-B (overhangs 7.3) + DC jack (4.1); jack positions NOT measured"],
  ["USB-B plug clearance (16 x 30 x 13 allowance, plug NOT measured)", [16, 30, 13], [-53, -72.3, DECK_TOP + UNO_SO_H + 1.6 - 1.0], "clearance", "hangs from the Uno jack", "-y: to the Pi"],
  ["LM2596 buck, 5.00 V (display)", [66, 36, 14], [10, -74, DECK_TOP + LM_SO_H], "part", "4 standoffs + pegs", "display up; trim pot locked"],
  ["rocker switch (20 mm round)", [20, 20, 0], [90, -74, DECK_TOP], "note", "snap-in 21 mm hole on the -y wing", "body hangs 23.8 below the wing (to z 30.7)"],
  ["rocker body below the -y wing (clips 22.9, depth 23.8)", [22.9, 22.9, 23.8], [88.55, -75.45, DECK_BOT - 23.8], "clearance", "snap-in 21 mm hole", ""],
  ["Pi USB-A / LAN plugs", [41.7, 64.4, 27.2], [-2, -32.2, DECK_TOP + VELCRO], "clearance", "keep clear", ""],
  ["Pi front camera ribbon", [44.7, 56.8, 27.2], [132.1, -28.4, DECK_TOP + VELCRO], "clearance", "keep clear", ""],
  ["Pi USB-C plug (-y side, 7 mm from the +x end)", [15, 45, 27.2], [116.8, -77.2, DECK_TOP + VELCRO], "clearance", "keep clear", ""],
  ["Pi fan / top access", [91.8, 64.4, 15], [40.0, -32.2, DECK_TOP + VELCRO + 27.2], "clearance", "keep clear", ""],
  ["Uno shield wiring", [53.7, 70, 20], [-58.18, -35, DECK_TOP + UNO_SO_H + 24], "clearance", "keep clear", ""],
  ["LM2596 terminals -x", [10, 36, 14], [0, -74, DECK_TOP + LM_SO_H], "clearance", "keep clear", ""],
  ["LM2596 terminals +x", [10, 36, 14], [76, -74, DECK_TOP + LM_SO_H], "clearance", "keep clear", ""],
  ["rocker terminals", [22.9, 22.9, 10], [88.55, -75.45, DECK_BOT - 23.8 - 10], "clearance", "keep clear", ""]
];
for (p = LAYOUT) if (p[3] != "note") ghost_box(p[1], p[2]);
echo(LAYOUT_PARTS = LAYOUT);
echo(LAYOUT_PEGS = concat(UNO_XY, LM_XY));
