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
// v6 (2026-10-13): posts 32 -> 42 (deck +10 mm, Evan's option A): the inline fuse holder
// (50 x 34.25 x 12, measured) lies flat on top of the bank, and the holder leads get room.
// v7 (2026-10-13): bank and holder sit on VELCRO (Evan, ~4 mm; removable) instead of zip
// ties - their edge slots could never close a loop (no return path under the part). Fences
// 10 -> 14 so the lifted bank's flat band (7 mm up) is still held; posts 42 -> 46 so the
// fuse holder on the lifted bank still clears the deck. The bank/holder slots stay, unused.
// v8 (2026-10-13): both side lobes DROPPED onto the Lego frames (Evan: frames level) -
// flat LOBE_T plates at z 0, printed on the bed: no ribs, feet or bridges under them. Only
// the middle floor stays raised (the bank spans the 7.8 mm pin rails). Holder moved out
// 6.4 mm to sit wholly on its lobe, in a 4-sided fence. Charger / BMS / XT30 on tape or
// velcro. Every zip slot and tie notch removed (nothing is tied any more).
VELCRO = 4.0;             // velcro pair thickness under the bank and holder (Evan: roughly 4)
//
// FRAME: x along the car, x = 0 at the REAR corner pin hole, +x toward the front;
// y across, the Lego pin rows at y = +/-24; z = 0 on the Lego frames' top face, z up. mm.
//
// Layout: two rails (pinned to the frames), a raised middle floor with a lightening
// window and ribs under it, a three-sided bank fence (no rear wall, for ports), two flat
// lobe plates on the frames (holder +y, small parts -y), a four-sided holder fence, and
// six deck posts (pinned, z up to 46.0).

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;
PIN_D = lego_pin_d();     // 4.95: lib/lego.scad fit class "friction_pin" (record GU, HG)

RAIL_H = 7.8;             // a Lego beam's height: a pin half fits fully
FLOOR_T = 2.0;
FLOOR_TOP = RAIL_H + FLOOR_T;   // 9.8
FENCE_T = 2.0;
FENCE_H = 14.0;           // v5: past the bank's rounded bottom edge (flat side from 7 mm up, Evan 2026-10-13)
FENCE_TOP = FLOOR_TOP + FENCE_H;   // 23.8
LOBE_T = 3.0;             // v8: lobe plates sit on the frames, z 0..3
HFENCE_TOP = LOBE_T + FENCE_H;     // 17.0: holder fence on its lobe
POST_TOP = 46.0;
POST_S = 8.0;

RAIL_Y0 = 20;
RAIL_Y1 = 28;
RAIL_X0 = -4;
RAIL_X1 = 132;
PIN_ROW_Y = 24;
RAIL_PIN_X = [0, 32, 48, 80, 88, 120, 128];

// pockets: the bought part's footprint + fit class "pocket" (0.25 per side)
POCKET_C = fit_offset("pocket") / 2;
BANK_POS = [-4, -35.275];  BANK_SIZE = [151.5, 70.55];    // battery bank
HOLD_POS = [58.125, 44.25]; HOLD_SIZE = [75.75, 40.5];    // 2S holder (v8: wholly on its lobe)
// bank fence interior
BANK_X0 = BANK_POS[0] - POCKET_C;
BANK_X1 = BANK_POS[0] + BANK_SIZE[0] + POCKET_C;
BANK_Y = BANK_SIZE[1] / 2 + POCKET_C;
// holder fence interior
HOLD_X0 = HOLD_POS[0] - POCKET_C;
HOLD_X1 = HOLD_POS[0] + HOLD_SIZE[0] + POCKET_C;
HOLD_Y0 = HOLD_POS[1] - POCKET_C;
HOLD_Y1 = HOLD_POS[1] + HOLD_SIZE[1] + POCKET_C;

POSTS = [[10, 41.6], [10, -41.6], [150, 41.6], [150, -41.6], [60, -82], [128, -82]];

RIB_T = 2.0;              // ribs under the floor (Rule 7)
LEAD = 0.5;               // lead-in chamfer on pocket tops (Rule 5)

module box(x0, x1, y0, y1, z0, z1) {
  translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
}
module rib(x0, x1, y0, y1) { box(x0, x1, y0, y1, 0, RAIL_H + EPS); }
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
    // 3 holder lobe plate, on the frames (overlaps the +y edge rib by 1 mm)
    box(55, 137, 41, 87, 0, LOBE_T);
    // 4 small-parts lobe plate, on the frames
    box(56, 132, -86, -41, 0, LOBE_T);
    // 5 bank fence: front wall and two side walls, no rear wall
    box(BANK_X1, BANK_X1 + FENCE_T, -(BANK_Y + FENCE_T), BANK_Y + FENCE_T, FLOOR_TOP, FENCE_TOP);
    box(BANK_X0, BANK_X1 + FENCE_T, BANK_Y, BANK_Y + FENCE_T, FLOOR_TOP, FENCE_TOP);
    box(BANK_X0, BANK_X1 + FENCE_T, -(BANK_Y + FENCE_T), -BANK_Y, FLOOR_TOP, FENCE_TOP);
    // 6 holder fence on its lobe plate: inner, outer and two end walls
    box(HOLD_X0 - FENCE_T, HOLD_X1 + FENCE_T, HOLD_Y0 - FENCE_T - 0.5, HOLD_Y0, LOBE_T - EPS, HFENCE_TOP);
    box(HOLD_X0 - FENCE_T, HOLD_X1 + FENCE_T, HOLD_Y1, HOLD_Y1 + FENCE_T, LOBE_T - EPS, HFENCE_TOP);
    box(HOLD_X0 - FENCE_T, HOLD_X0, HOLD_Y0, HOLD_Y1, LOBE_T - EPS, HFENCE_TOP);
    box(HOLD_X1, HOLD_X1 + FENCE_T, HOLD_Y0, HOLD_Y1, LOBE_T - EPS, HFENCE_TOP);
    // 8 deck posts: the two lobe posts stand on the bed (their lobe is at z 0)
    for (p = POSTS) box(p[0] - POST_S / 2, p[0] + POST_S / 2, p[1] - POST_S / 2, p[1] + POST_S / 2,
                        abs(p[1]) > 60 ? 0 : FLOOR_TOP, POST_TOP);
    // 8b ribs under the floor (Rule 7): edge ribs, rear skirt, rear cross, front cross, front skirt
    rib(-6, 156, 40, 42); rib(-6, 156, -42, -40);
    rib(-6, -4, -42, 42); rib(5, 7, -42, 42); rib(144, 146, -42, 42); rib(154, 156, -42, 42);
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
  // 13 encoder-cable notch in the -y rail (x 100..108, between pins 88/120)
  translate([100, -28 - EPS, -EPS]) cube([8, 8 + 2 * EPS, 5.0 + EPS]);
  // 14 encoder-cable floor slot just outside the bank fence (y -41.0..-38.5)
  translate([100, -41.0, RAIL_H - EPS]) cube([8, 2.5, 2.0 + 2 * EPS]);
  // 15 encoder-cable notch through the -y edge rib, full height, under the floor slot
  translate([100, -42 - EPS, -EPS]) cube([8, 2 + 2 * EPS, RAIL_H + EPS]);
  // 17 lead-in chamfers on the pocket tops (Rule 5)
  lead_in(BANK_X0, BANK_X1, -BANK_Y, BANK_Y, FENCE_TOP, LEAD);
  lead_in(HOLD_X0, HOLD_X1, HOLD_Y0, HOLD_Y1, HFENCE_TOP, LEAD);
}

// preview-only ghosts
// LAYOUT: [name, [sx, sy, sz], [x, y, z], kind, held by, ports]; kind part | zone | note.
// A zone reserves space for a part whose size is NOT measured.
LAYOUT = [
  ["velcro under the bank (~4 mm)", [151.5, 70.55, VELCRO], [-4, -35.275, FLOOR_TOP], "zone", "adhesive both sides", ""],
  ["velcro under the holder (~4 mm)", [75.75, 40.5, VELCRO], [58.125, 44.25, LOBE_T], "zone", "adhesive both sides", ""],
  ["battery bank (Pi power)", [151.5, 70.55, 18.0], [-4, -35.275, FLOOR_TOP + VELCRO], "part", "velcro + 14 mm bank fence, open at the rear", "-x: USB-C + USB-A (20 / 45 mm from the left)"],
  ["2S holder + 2x Samsung 25R", [75.75, 40.5, 20.5], [58.125, 44.25, LOBE_T + VELCRO], "part", "velcro + 4-sided 14 mm fence on its lobe", "-x: red / black leads + MB wire, 160 mm, from a SHORT end (Evan 2026-10-14) - seat that end at -x"],
  ["USB-C 2S charger (Adeept p0374)", [38.43, 18.3, 6.3], [60, -69.5, LOBE_T], "part", "double-sided tape or velcro", "-x: USB-C on a SHORT end (Evan 2026-10-14), out the open lobe edge at x 56; pads BAT, GND, GND, VIN"],
  ["2S BMS (ACEIRMC B08HLQQCQJ)", [41, 8, 2.2], [66, -83, LOBE_T], "part", "double-sided tape", "pads B+ B- MB P+ P-"],
  ["inline fuse holder, 3 A ATO (50 x 34.25 x 12, lying flat)", [50, 34.25, 12], [40, 0, FLOOR_TOP + VELCRO + 18.0], "part", "on top of the bank; tape or velcro", "in the CELL+ wire, before the BMS"],
  ["XT30 pair, mated (25 x 10.5 x 5.3)", [25, 10.5, 5.3], [104, -66, LOBE_T], "part", "double-sided tape or velcro (pack half)", "BMS P+ / P- side; car side to the rocker"]
];
for (p = LAYOUT) if (p[3] != "note") ghost_box(p[1], p[2]);
echo(LAYOUT_PARTS = LAYOUT);
ghost_box([168, 56, 7.8], [-4, -28, -7.8]);                         // middle frames (approx)
