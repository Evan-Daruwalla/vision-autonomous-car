# decisions - Autonomous Car Project

STATUS: started 2026-10-12. Older dated decisions still live in HANDOFF.md
(2026-07-23, 2026-08-12, 2026-09-09); move them here when next touched.

## 2026-10-12 - printed parts attach to the Lego body with REAL black friction pins (Evan)
**What:** every printed mount pins to the Technic frame with Evan's black
friction pins (LEGO 2780: a ring in the middle and a wider lip at each end).
No more printed pin stubs (motor mount v1 used them; v2 replaced them).
**How to apply:** a through hole gets the Lego hole shape: a 4.95 bore (PIN_D; was 4.875 until 2026-10-12 record HG,
2026-10-12 record GU: 4.80 + 0.075; since 2026-10-13 every part sets PIN_D = lego_pin_d(),
the "friction_pin" fit class in lib/lego.scad - change fits THERE, never in a part) with a
6.2 x 0.8 recess at both faces (`technic_hole(..., cb_top=0.8, cb_bot=0.8)`
in `cad/scad/lib/lego.scad`). A BLIND socket that takes half a pin from a
beam above (a mount coming in from below) needs the `pin_socket()` shape in
`cad/scad/motor_mount.scad`: 6.2 x 0.8 recess at the face, 4.8 bore 6.2 long,
then a 6.2 pocket 2.0 tall where the tip lip snaps.
**Why:** real pins are a known part with a proven grip; printed stubs are
weak across layers and their fit is untested.
**Source:** record GL and GM; docs/research/2026-10-12_technic-pin-snap-geometry.md.
Recess and pocket sizes are still UNTESTED in PLA (coupon row B, first v2 print).

## 2026-10-13 - steering gate stays coupled to the pack check until the pack is wired (Evan)
**What:** the servo keeps moving only in OUT_DRIVE (armed + pack OK + link
alive). No bench bypass. Frame -> servo through uno_control is first tested
end to end after the pack is wired (cells metered, BMS in).
**Why:** keeps the audit-HJ gate unchanged before the pack exists; the
compensator math (SELFTEST 86/86) and constants (1525 / 75 us, measured by
hand) are already verified separately.
**Rejected:** A (steer on armed + link alive, ignoring the pack - Claude's
recommendation; revisit when the car first runs on the pack), B (disarmed
bench command).
**Source:** records HW, HX, HY, HZ.

## 2026-10-13 - every car part is printed in Bambu PETG Translucent (Evan)
**What:** all printed car parts use Bambu PETG Translucent (250 C nozzle, 70 C
bed, P1S 0.4, 0.15 mm layers, 2 walls, X-Y hole compensation 0). Fit classes
in cad/scad/lib/lego.scad are calibrated for it; press_shaft (+0.15) is
PLA-only until re-tested.
**Why:** "I have the most of it."
**Source:** record IC.

## 2026-10-13 - bank, holder and Pi case held by velcro, not zip ties (Evan)
**What:** ~4 mm velcro under the bank, the 2S holder and the Pi case
(removable); fences 14 mm and Pi brackets 10 mm so the lifted parts are still
held at their flat sides; no zip slots anywhere on the tray or deck.
**Why:** the old edge tie slots could never close a loop (no return path
under the part), and the needed loops (~135-195 mm) exceed a 200 mm tie for
the bank and Pi. Velcro over chained ties: removable.
**Rejected:** chaining two 200 mm ties (Claude's recommendation).
**Source:** records IJ, IK. Velcro thickness is assumed, not measured.

## 2026-10-13 - tray side lobes sit ON the Lego frames (Evan)
**What:** only the middle floor is raised (the bank spans the 7.8 mm pin
rails); both side lobes are flat 3 mm plates on the frames, printed on the
bed with no bridges; the holder moved out to sit wholly on its lobe.
**Why:** the lobes were raised only because v2 carried the middle floor's
level outward; Evan confirmed the frames under them are level.
**Source:** record IK.

## 2026-10-16 - the Uno is powered by the Pi's USB, not the LM2596 (Evan)
**What:** plain USB cable Pi -> Uno for power + data; the LM2596 `+5V2` rail feeds only the servo, both strips and the encoder; `+5V2` never touches the Uno 5V pin; servo V+ on `+5V2`, never the Uno 5V header.
**Why:** no cut-5V cable (and no FT232RL risk); the Uno survives a dead pack / blown fuse / rocker OFF and reports PACK_FAULT instead of going dark.
**Rejected:** the 2026-09/10 design (Uno 5V pin on `+5V2`, USB 5 V conductor cut).
**Source:** record JF.

## 2026-10-14 - the BMS sits on top of the 2S holder (Evan)
**What:** BMS taped on the holder top near its -x lead end; only the fused, BMS-protected P+ / P- cross the bank to the charger and XT30 on the -y lobe.
**Why:** with the BMS on the -y lobe the two UNFUSED leads (B-, MB) were the longest pack wires (~160-200 mm); a short between them shorts cell 2 with no fuse or BMS in the path.
**Cost:** peel the BMS off to swap cells.
**Source:** record IO.

## 2026-10-16 - the steering servo is powered from the Uno's 5V header (Evan)
**What:** servo V+ on the Uno 5V pin (USB 5 V from the Pi); signal D9; GND to the star. `+5V2` keeps the strips and encoder.
**Why:** ease of setup and repair - three pins into the shield on the Uno; it drove the rack (incl. the left stop) on PC USB (HM-HQ) and on Pi USB with no reset or USB over-current (JN-JO).
**Known cost / rejected:** Claude recommended `+5V2`: with the servo on the Uno 5V, 2 of 3 large swings lost serial bytes Uno -> Pi (JP). Mitigation: a 3-pin jumper (Uno 5V | servo + | `+5V2`) on the shield; re-measure CRC-reject rate while steering once the pack is on the shield.
**Source:** records JN-JP, JR.

## 2026-10-16 - tray v9 / deck v10 for the new 168 x 62.16 x 22.51 bank (Evan + Claude)
**What:** bank pocket moved back (bank x -14.25..153.75, floor to x -16); bank fence 18 mm, -y wall open at the rear for the charge button; deck +8.5 (underside 54.5); ~4 mm velcro under EVERY part (bank, holder, Pi, fuse holder, BMS, charger, XT30); rocker moved from the rear tab to the deck's -y wing at (42, -64) with a power slot; BMS at the holder's +x rivet end; charger turned so its USB-C faces out the -y side; XT30 at the -y lobe's inner edge; fuse holder on the bank at x 10..60.
**Why:** the old bank was flaky; the new one is 16.5 longer (servo mount at x ~157 forces it backward), 4.5 taller (fuse holder on velcro needs the deck at 54.5). The pack is soldered up to the XT30 male and Evan will NOT re-solder it, so the layout fits the wires as built (P+ / P- 4 x 190, fuse wire 326, MB 55, encoder 300 uncut). Evan chose deck +8.5 over thin tape under the fuse; Claude chose the -y wing for the rocker (the rear tab sits in the bank's port / cable exit; the rear wheels peak at z 11, Evan, so both were clear).
**Rejected:** P+ / P- under the tray floor (would mean re-threading the soldered pack); fuse holder on thin tape with the deck at +4.5.
**Source:** record JU; docs/ELECTRONICS_LAYOUT.md.

## 2026-10-16 - reserve space for plugs and cables; deck grows rearward (Evan)
**What:** tray v10 / deck v11: deck plate x -64..156, Uno behind a 40 mm USB-A plug zone, Pi x 40..131.8, rear posts x -12, holder fence end walls removed, Pi bracket end legs 4 mm, 15 LAYOUT clearance boxes (plugs, cable runs, terminals).
**Why:** JU's layout passed the checker with no cable room (Pi USB-A 3.6 mm from the Uno, Pi USB-C plug near the mast, fence walls on the holder leads / MB joint). Evan chose rearward growth over right-angle cables (purchase) or a wider -y wing (car already 173 mm wide vs 155 track).
**Cost:** car ~58 mm longer at deck height; 52 mm deck cantilever; servo lead needs a Dupont extension; bank->Pi USB-C ~300-350 mm.
**Source:** record JV.
## 2026-10-16 - deck -y wing order and Pi brackets follow the real ports (Evan's bench results)
**What:** LM2596 x 10..76, rocker at (100, -64) over the XT30 / charger, Pi USB-C plug zone on the -y side at the wing's front end; Pi bracket legs removed at the USB/LAN end and at the USB-C side corner; fuse holder x 30 and the bank USB-C cable below the bank top so the charge LEDs stay readable from the side.
**Why:** ports 4 mm from the case sides and a side-facing USB-C (Evan) collided with the brackets / LM2596; Evan prefers reading the LEDs from the side over a deck window (window weakens the plate near the rear posts and the USB cable crosses it).
**Source:** record JW.
