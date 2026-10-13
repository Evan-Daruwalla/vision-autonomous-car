// Lego Technic interface primitives for printed mounts (2026-10-11).
//
// Every module marked "Negative volume" is meant to be SUBTRACTED with
// difference().
//
// PIN_D 4.80 is the ABS-coupon value (the nominal Lego pin hole). Parts do NOT
// use it directly: they take lego_pin_d() below, which adds the calibrated
// friction-pin fit offset. Re-check the offsets once the pla_fit_coupon print
// (cad/scad/pla_fit_coupon.scad) has been fitted.
// CB_D 6.2 / CB_DEPTH 0.8 are community values for the counterbore of a
// Technic pin hole. UNVERIFIED until measured on a real liftarm.
//
// Include with `use <lib/lego.scad>`. `use` exposes the modules but not the
// constants below, so each module carries its own defaults.

PITCH = 8.0;
PIN_D = 4.80;
CB_D = 6.2;
CB_DEPTH = 0.8;
FN = 64;
EPS = 0.01;

// Fit classes: ONE place for every printed-fit clearance (docs/research/
// 2026-10-12_print-friendly-cad-rules.md, Rule 2). Diametral offset in mm over
// the nominal size, PLA on the Bambu P1S, slicer X-Y hole compensation 0
// (Evan, record HK). Calibrated per filament - change a value here, never in a part.
//   "friction_pin": Lego friction pin in a printed hole. +0.15 -> 4.95 (HG).
//                   UNTESTED; +0.075 printed too tight (HH).
//   "press_shaft" : motor D-shaft into a printed bore. +0.15 FITS (GF).
//   "slide"       : printed-to-printed sliding fit. 0.3 = Prusa's starting
//                   value, UNTESTED here.
//   "rotate"      : Lego axle spinning in a printed bore - NOT calibrated in
//                   PLA (ABS coupon: 5.00 bore); asking for it stops the render.
function fit_offset(fit) =
  fit == "friction_pin" ? 0.15 :
  fit == "press_shaft"  ? 0.15 :
  fit == "slide"        ? 0.30 :
  fit == "rotate"       ? assert(false, "fit 'rotate' is not calibrated in PLA - print the coupon first") 0 :
  assert(false, str("unknown fit class: ", fit)) 0;

// nominal + offset, rounded to 0.0001 mm so a value written as a literal before
// (e.g. 4.95) comes out bit-identical and the STL does not change.
function fit_d(nominal, fit) = round((nominal + fit_offset(fit)) * 10000) / 10000;

// The printed Lego pin-hole bore every part uses.
function lego_pin_d() = fit_d(4.80, "friction_pin");

// Circumscribed polygon: flats at d/2, so a printed HOLE is never smaller than d.
module hole_cyl(d, h, fn=FN) { cylinder(r = d / 2 / cos(180 / fn), h = h, $fn = fn); }

// Negative volume: a pin hole along +Z from z=0 to z=h, centred on x=y=0,
// with optional counterbores (diameter cb_d) cb_bot deep at z=0 and cb_top deep at z=h.
module technic_hole(d=PIN_D, h=7.8, cb_d=CB_D, cb_top=0, cb_bot=0) {
  translate([0, 0, -EPS]) hole_cyl(d, h + 2 * EPS);
  if (cb_bot > 0) translate([0, 0, -EPS]) hole_cyl(cb_d, cb_bot + EPS);
  if (cb_top > 0) translate([0, 0, h - cb_top]) hole_cyl(cb_d, cb_top + EPS);
}

// Negative volume: nx * ny technic holes on the 8 mm grid, node (0,0) at the origin.
// skip = list of [i, j] nodes to leave solid.
module pin_grid(nx, ny, pitch=PITCH, d=PIN_D, h=7.8, cb_top=0, cb_bot=0, skip=[]) {
  for (i = [0 : nx - 1], j = [0 : ny - 1])
    if (len([for (s = skip) if (s[0] == i && s[1] == j) 1]) == 0)
      translate([i * pitch, j * pitch, 0]) technic_hole(d, h, CB_D, cb_top, cb_bot);
}

// Negative volume: a self-tapping-screw pilot hole from z=0 up to z=depth.
module pilot_hole(d, depth) { translate([0, 0, -EPS]) hole_cyl(d, depth + EPS); }

// Negative volume: one zip-tie slot, w along X by t along Y, through z = 0..h, centred on x=y=0.
module zip_slot(w, t, h) { translate([-w / 2, -t / 2, -EPS]) cube([w, t, h + 2 * EPS]); }

// Preview-only stand-in for a component (the % modifier keeps it OUT of the STL).
module ghost_box(size, pos=[0, 0, 0]) { % translate(pos) cube(size); }
