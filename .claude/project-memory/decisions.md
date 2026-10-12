# decisions - Autonomous Car Project

STATUS: started 2026-10-12. Older dated decisions still live in HANDOFF.md
(2026-07-23, 2026-08-12, 2026-09-09); move them here when next touched.

## 2026-10-12 - printed parts attach to the Lego body with REAL black friction pins (Evan)
**What:** every printed mount pins to the Technic frame with Evan's black
friction pins (LEGO 2780: a ring in the middle and a wider lip at each end).
No more printed pin stubs (motor mount v1 used them; v2 replaced them).
**How to apply:** a through hole gets the Lego hole shape: a 4.875 bore (PIN_D,
2026-10-12 record GU: 4.80 + 0.075; set it in each part - the lib default is 4.80) with a
6.2 x 0.8 recess at both faces (`technic_hole(..., cb_top=0.8, cb_bot=0.8)`
in `cad/scad/lib/lego.scad`). A BLIND socket that takes half a pin from a
beam above (a mount coming in from below) needs the `pin_socket()` shape in
`cad/scad/motor_mount.scad`: 6.2 x 0.8 recess at the face, 4.8 bore 6.2 long,
then a 6.2 pocket 2.0 tall where the tip lip snaps.
**Why:** real pins are a known part with a proven grip; printed stubs are
weak across layers and their fit is untested.
**Source:** record GL and GM; docs/research/2026-10-12_technic-pin-snap-geometry.md.
Recess and pocket sizes are still UNTESTED in PLA (coupon row B, first v2 print).
