// Electronics TRAY (2026-10-11) - LAYOUT DRAFT - NOT PRINTABLE - placeholders marked _UNMEASURED
//
// PURPOSE: lower plate of the two-level electronics stack. Holds the battery bank
// (open at +x) and the battery-holder pocket, carries four posts that the deck sits
// on, and four frame-pin bosses for the Lego chassis. UNTESTED: no part of this
// layout has been printed or fitted.
//
// FRAME: x along the car (+x = rear), y lateral, origin at the tray centre;
// z = 0 at the tray underside. The deck underside sits on the post tops at z = DECK_Z.
//
// MAP (mm)
//   plate x -78..78, y -62.5..62.5, z 0..2
//   bank interior x -76..76 (open at +x), y -52.5..17.7, walls z 2..12
//   holder interior x -38.25..38.25, y 19.7..60.2, walls z 2..12
//   posts 8x8 at (+/-72, +/-58.5), z 0..23, top pin hole 4.8 dia (0.8 counterbore)
//   frame-pin bosses 8x8 at FRAME_PIN_NODES_UNMEASURED, z 0..7.8
//
// Render with scripts/render_scad.py: it checks the mesh against
// electronics_tray_draft.probe.json.

use <lib/lego.scad>
EPS = 0.01;
$fn = 64;

PLATE_T = 2.0;
WALL_T = 2.0;
WALL_H = 10.0;                       // above the plate top
BANK_L = 151.5;                      // measured (Evan)
BANK_W = 69.7;                       // measured (Evan)
BANK_H = 18.5;                       // measured (Evan)
BANK_CLEAR = 0.5;
HOLDER_L_UNMEASURED = 76;
HOLDER_W_UNMEASURED = 40;
HOLDER_H_UNMEASURED = 19;
DECK_Z = 23.0;
FRAME_PIN_NODES_UNMEASURED = [[-48, 32], [-48, 48], [48, 32], [48, 48]];
CHARGER_SIZE_UNMEASURED = [18, 25, 6];   // unattributed size

POSTS = [[-72, -58.5], [72, -58.5], [-72, 58.5], [72, 58.5]];
ZIPS = [[-50, -55.4], [50, -55.4], [-50, 20.6], [50, 20.6], [-66, 30], [66, 30], [-66, 46], [66, 46]];

module box(p0, p1) { translate(p0) cube([p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]); }

difference() {
  union() {
    box([-78, -62.5, 0], [78, 62.5, PLATE_T]);                       // 1 plate
    // 2 bank walls (z 2..12)
    box([-78, -54.5, PLATE_T], [-76, 19.7, PLATE_T + WALL_H]);       //   front end
    box([-78, -54.5, PLATE_T], [78, -52.5, PLATE_T + WALL_H]);       //   long wall
    box([-78, 17.7, PLATE_T], [78, 19.7, PLATE_T + WALL_H]);         //   shared wall
    // 3 holder walls (z 2..12)
    box([-40.25, 19.7, PLATE_T], [-38.25, 62.2, PLATE_T + WALL_H]);
    box([38.25, 19.7, PLATE_T], [40.25, 62.2, PLATE_T + WALL_H]);
    box([-40.25, 60.2, PLATE_T], [40.25, 62.2, PLATE_T + WALL_H]);
    // 4 posts 8x8, z 0..DECK_Z
    for (p = POSTS) box([p[0] - 4, p[1] - 4, 0], [p[0] + 4, p[1] + 4, DECK_Z]);
    // 5 frame-pin bosses 8x8, z 0..7.8
    for (n = FRAME_PIN_NODES_UNMEASURED) box([n[0] - 4, n[1] - 4, 0], [n[0] + 4, n[1] + 4, 7.8]);
  }
  // 6 post top pin holes
  for (p = POSTS) translate([p[0], p[1], DECK_Z - 7.8]) technic_hole(d = 4.8, h = 7.8, cb_d = 6.2, cb_top = 0.8);
  // 7 frame-pin holes
  for (n = FRAME_PIN_NODES_UNMEASURED) translate([n[0], n[1], 0]) technic_hole(d = 4.8, h = 7.8, cb_d = 6.2, cb_bot = 0.8);
  // 8 zip slots
  for (z = ZIPS) translate([z[0], z[1], 0]) zip_slot(4.0, 1.8, PLATE_T);
}

// Ghosts (preview only, not in the STL)
ghost_box([BANK_L, BANK_W, BANK_H], [-75.75, -52.25, 2]);
ghost_box([76, 40, 19], [-38, 20, 2]);
ghost_box([8, 41, 2.2], [56, 38, 2]);                                // BMS
ghost_box(CHARGER_SIZE_UNMEASURED, [-70, 36, 2]);                    // charger
