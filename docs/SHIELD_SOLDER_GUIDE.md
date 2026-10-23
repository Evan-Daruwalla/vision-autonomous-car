# Proto shield - step-by-step soldering guide

Written 2026-10-21 for the bench. It follows the 9 build steps in
`docs/shield_layout.json` (the same steps as `docs/SHIELD_BUILD.md`, which is
generated from it) and adds the how: tools, order, technique, and the meter
check that closes each step. Hole names are ROW/COL as on
`docs/shield_holemap.svg`. If this guide and the layout file ever disagree,
the layout file wins - re-run `scripts/shield_holemap.py` and tell Claude.

**Picture version (LEGO-style, one panel per step, new parts in colour):
`docs/shield_build_guide.svg`** - generated from the same layout file by
`scripts/shield_guide_svg.py`, step renders by `scripts/shield_render3d.py --steps`.

**What every part does and how the current flows (animated):
`docs/shield_how_it_works.svg`**
(`scripts/shield_flow_svg.py`).

Pictures of the intended result: `docs/shield_3d_top.png` (labelled, from
above), `docs/shield_3d_iso.png` (3/4 view), `docs/shield_3d_bottom.png`
(underside, labelled). They show the INTENDED build, not a photo.

## Before you start

**Tools:** soldering iron with a fine conical or small chisel tip, solder
(0.5-0.8 mm with flux core), flux pen if you have one, flush cutters,
multimeter with a continuity beep, tweezers or helping hands, a scrap of bare
wire (resistor lead offcuts are ideal) for bridges, 22 AWG insulated wire,
heat-shrink, a marker.

**Iron temperature (typical values, check your solder's label):** about
330-350 C for leaded (63/37 or 60/40) solder, about 360-380 C for lead-free.

**Good joint, every time:** touch the iron to the pad AND the lead together,
count 1-2 s, feed solder into the joint (not onto the iron), pull the solder
away, then the iron. The joint should be a shiny little cone that wets both the
pad and the lead. A ball sitting on top of the pad is a cold joint - reheat it
with a touch of flux.

**Rules for this board:**
- **One lead per hole.** The layout never puts two parts in one hole.
- **Red x on the hole map = danger pair.** A bridge sits next to a hole on a
  different net. After soldering near it, meter those two holes: they must be
  SILENT.
- **Bridges are on the UNDERSIDE.** The hole map draws them as seen THROUGH the
  board from the top. Flip the board **top-over-bottom** (rotate it around its
  long edge) so the USB end stays on your LEFT - then
  `docs/shield_3d_bottom.png` matches what you see. Never flip it left-to-right:
  that mirrors every bridge.
- **Meter with the shield OFF the Uno and nothing powered**, continuity mode,
  until step 7.
- **If a check fails, STOP.** Do not solder past a failed check. Send the
  result (and a photo) first.

## Step 0 - two meter checks before any solder

Shield off the Uno, continuity mode.

- [ ] 0.1 U1/1 to U3/1: must **BEEP** (one strip, three holes).
- [ ] 0.2 V/12 to G/12, and V/12 to B/13: must be **SILENT**.

Already metered by Evan on 2026-10-20: T and V beep to 5V; G and B beep to
GND; G beeps to B; neighbouring strips silent.

**Check:** both match. If either differs, STOP and send the result.

## Step 1 - TB6612 carrier, off the shield

Work on the carrier alone; it is far easier than on the board.

1. **Headers:** push the two 8-pin headers through the carrier, SHORT ends up
   through the carrier, LONG ends down. Tip: plug the long ends into a
   breadboard (or into the shield's own holes, without soldering) to hold them
   straight. Solder one pin of each row, check both rows are square, then the
   rest.
2. **Mark PWMA** (label side) with a marker dot. This dot goes TOP-LEFT in
   step 2.
3. **Carrier-top bridges** (insulated wire, soldered to the pin tips on top of
   the carrier): PWMA-PWMB, AIN2-BIN2, AIN1-BIN1 (any thin wire), AO1-BO1 and
   AO2-BO2 (22 AWG - these carry motor current). Lay them as nested U's so no
   two cross: the outer pair (PWMA-PWMB, AO1-BO1) reaches furthest in.
4. **C1 (470 uF)**: + lead (NO stripe) to the VMOT tip, stripe (-) lead to the
   GND tip next to it - bottom row, right end. Stand the can UPRIGHT on the two
   tips, leads short. **Stripe to GND - a reversed electrolytic across ~8 V can
   fail violently.**
5. **C2 (0.1 uF, no polarity)** across the same VMOT and GND tips. Either bend
   its leads out past the carrier's bottom edge, low, so it sits beside the can,
   or solder it straight across C1's two legs right at the tips - both are the
   same circuit; keep C2's leads as short as you can. Heat each cap joint
   briefly (2-3 s): the electrolytic does not like a long soak.

**Check:** PWMA-PWMB, AIN1-BIN1, AIN2-BIN2, AO1-BO1, AO2-BO2 each BEEP;
VMOT-GND does NOT beep (C1 may chirp once while it charges from the meter).

## Step 2 - carrier onto the shield

1. Chip up, PWMA dot at the TOP-LEFT: the top row of pins goes into
   U2/1 ... U2/8, the bottom row into L2/1 ... L2/8.
2. Solder one corner pin, check the carrier sits flat and square, then the
   opposite corner, then all 16 on the underside.
3. Trim the leftover pin length flush.

**Check:** U1/1 beeps to the PWMA pin; L3/7 beeps to VMOT; L3/1 beeps to L3/8
(GND through the carrier).

**Send a photo here, before the bridges.**

## Step 3 - underside solder bridges

Each bridge joins exactly TWO neighbouring holes. Flip the board top-over-bottom
first (see the rules). Method: lay a short bare-wire offcut across the two pads
and solder both ends - more reliable than trying to blob solder across the gap.

- [ ] Motor outputs: L3/3-P3/3, L3/4-P3/4.
- [ ] J1 GND: P3/5-P4/5 and P4/5-B/5. J1 +5V2: P3/6-P4/6.
- [ ] +5V2 bus along row P4: P4/6-P4/7-P4/8-P4/9-P4/10-P4/11-P4/12-P4/13
      (one bare wire along the row, soldered at every hole, works well).
- [ ] VBAT strips: L2/9-L2/10.
- [ ] Strip data: L3/12-P3/12, L3/13-P3/13.
- [ ] Uno 5V to the left field: V/1-V/0, V/0-V/-1, V/-1-L1/-1.
- [ ] Servo block: L3/-1-P3/-1, L2/-2-L2/-1, L1/-2-L1/-3, L3/-2-P3/-2.

**DANGER pairs - they sit side by side and must NOT touch:**
- P4/5 (GND) and P4/6 (+5V2).
- P3/-1 (+5V2) and P3/-2 (GND).

**Check:** P4/5 to P4/6 SILENT; P3/-1 to P3/-2 SILENT; P4/6 beeps to P4/13;
V/12 beeps to L1/-1. Then meter every red-x pair on the hole map you soldered
near: all SILENT.

## Step 4 - headers

Headers sit on top, soldered underneath. Tack one pin, check it stands
straight, then the rest.

- [ ] J1 (4 pins) in P3/3, P3/4, P3/5, P3/6.
- [ ] J5 (4 pins, pull out the 2nd pin first - it is the polarity key) in
      L3/10, P3/10, P4/10, B/10. J6 (1 pin) in B/11.
- [ ] J3 in P3/12, P4/12, B/12. J4 in P3/13, P4/13, B/13.
- [ ] JP1 in L1/-1, L2/-1, L3/-1. J2 in L1/-2, L2/-2, L3/-2.

**Check:** J5 top pin (L3/10) beeps to L1/9 (the VBAT strip; VMOT joins it
only with w1 in step 6); J3 middle beeps to J4 middle
(+5V2); J3 bottom beeps to B/8.

## Step 5 - divider (pack-voltage sense for A0)

- [ ] R100k lying flat: leads into L1/9 and U3/9 only (the body lies over G/9
      and V/9 - its leads must NOT go into those holes).
- [ ] R10k standing: U2/9 and U2/10.
- [ ] R2k standing: U3/10 and G/10.

10k + 2k in series = the 12k bottom half (the kit has no 12k; never use the
10k alone - the firmware would under-read the pack by 15%).

**Check (meter on resistance):** L1/9 to U3/9 = ~100k; U3/9 to G/10 = ~12k.

## Step 6 - top-side jumper wires (insulated 22 AWG)

Strip ~3 mm at each end, push through, solder underneath. The wires are
insulated everywhere else, so they may cross over other holes (w1 hops over
L3/8).

- [ ] w1 L3/7 -> L3/9 (VMOT to the VBAT strip; hop over L3/8).
- [ ] w2 L3/8 -> B/8 (TB6612 GND to the star).
- [ ] w3 L3/2 -> L3/0 -> V/0 (TB6612 VCC to the Uno 5V): left along row L3,
      then up column 0 - never under the carrier.
- [ ] w4 P4/7 -> P4/-1 -> P3/-1 (+5V2 to JP1's bottom pin): left along row P4,
      then up.
- [ ] w5 B/2 -> B/-2 -> P3/-2 (servo GND to the star): left along row B, then
      up.

**Check:** J5 top pin (L3/10) now beeps to VMOT (through w1); VBAT (L3/10) to
B/10 SILENT; V/0 to B/2 SILENT; P4/7 to B/2 SILENT.

## Step 7 - Dupont wires to the Uno sockets

Cut a male-male jumper, strip the cut end, solder it in the hole; the male pin
plugs into the shield's own socket for that Uno pin. Digital pins are on the
top header, A0 on the bottom header.

- [ ] U1/1 -> D11, U1/2 -> D12, U1/3 -> D8, U1/4 -> D10.
- [ ] U1/9 -> A0. L1/-3 -> D9.
- [ ] L3/12 -> D4 and L3/13 -> D7, each with 200 + 200 ohm soldered in series
      IN the wire, then heat-shrunk.
- [ ] Encoder yellow -> D2 socket, white -> D3 socket (male pins on the cable,
      not through the shield).

Route the A0 wire around the upright C1, not over it at a stretch.

**Check (shield ON the Uno, still unpowered):** each socket pin beeps to its
hole; the Uno's 5V pin beeps to V/12.

## Step 8 - before the first power-up

1. Re-run every SILENT check from steps 0, 3 and 6.
2. Jumper cap on JP1's TOP two pins (UNO5V-SERVO_V: servo on the Uno 5V).
3. Pack OFF (rocker). Uno on the Pi's USB first. Then rocker ON with nothing
   else plugged in, and meter VBAT at J5 (~8 V) and +5V2 at J3's middle pin
   (~5.0 V).

**Check:** VBAT ~ pack voltage, +5V2 ~ 5.0 V, Uno 5V ~ 5 V and NOT tied to
+5V2 (V/12 to P4/13 SILENT with the power off).

## After the build

Record in the project record: solder type and iron temperature used, every
check result (beep / silent / ohms / volts), any joint you had to redo, and
photos. Everything above is untested until those results exist.
