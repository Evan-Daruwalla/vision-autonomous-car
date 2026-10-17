# Electronics layout - where every part goes (2026-10-16, tray v10 / deck v11)

**Status: PLAN, UNTESTED.** Nothing here has been printed or fitted. Parts
and positions come from the `LAYOUT` lists in
`cad/scad/electronics_tray.scad` (layer 1) and `cad/scad/electronics_deck.scad`
(layer 2); `scripts/electronics_layout.py` reads them, checks them against
the rendered STLs and draws `docs/electronics_layout.svg`. Change a position
in the .scad, never here, then re-run the script. Records: the entry of
2026-10-13 that introduced this file; records JU (v9 / v10) and the 2026-10-16 entry for v10 / v11 (cable room).

![layout](electronics_layout.svg)

**Frame (mm):** x along the car, x = 0 at the rear corner pin hole of the
centre frames, **+x = front**; y across, +y = the car's left (up in the drawing);
z = 0 on the Lego frames' top face. Layer 1: the bank on the raised middle
floor (z 9.8); everything else on the two lobe plates, which sit on the frames
(z 0..3). Layer 2 on the deck (underside z 54.5, top z 57.0 - raised 8.5 mm on
2026-10-16 for the taller bank and the velcro under the fuse holder on it).
**Every part sits on ~4 mm velcro** (the `VELCRO` constant, assumed, not
measured): bank, holder, Pi case, fuse holder, BMS, charger, XT30 - all
removable without unsoldering. No zip ties anywhere.
Printed in Bambu PETG Translucent, supports OFF.

**Why v9 / v10 (2026-10-16):** Evan replaced the flaky bank with a 168 x 62.16
x 22.51 one (16.5 longer, 8.4 narrower, 4.5 taller). The servo mount starts at
x ~157, so the bank moved BACK (rear end x -14.25, ~10 mm past the frames - that
space is clear, Evan). The pack is soldered up to the XT30 male and is NOT to be
re-soldered, so the layout was fitted to the wires as built: 4 x 190 mm P+ / P-,
fuse wire B+ -> holder + 326 mm (Evan: 153 + 4 x 43.27), MB 55 mm from the
holder's brass rivet, encoder #4763 uncut (300 mm).

**Why v10 / v11 (2026-10-16, Evan: "leave space for wires and connectors ...
especially around the Arduino and Pi"):** v10 left 3.6 mm between the Pi's
USB-A / LAN end and the Uno (a straight USB-A plug needs ~40 mm), the Pi's front
USB-C plug + bend reached ~5 mm from the camera mast, the holder fence's end
walls blocked the lead exit and pressed on the MB joint, and the Pi brackets'
10 mm legs could block the outer plugs. Evan chose to grow the deck rearward
(no new cables). Plug estimates (Evan: use them): USB-A 40, USB-C 30, USB-B 35
mm. Every reserved space is a `clearance` box in the LAYOUT lists, so the
checker proves nothing printed or placed sits in it.

## Layer 1 - electronics tray (v9)

| # | Part | Box x .. / y .. / z .. | Held by | Ports / leads |
|---|---|---|---|---|
| 1 | Power bank (Pi only) 168 x 62.16 x 22.51 | -14.25..153.75 / -31.08..31.08 / 13.8..36.3 | velcro + bank fence 18 mm tall (top z 27.8), open rear; the -y wall starts at x 15 | REAR end (-x): USB-C at the -y corner, USB-A at the +y corner (Evan). Charge button on the -y side face ~10 mm forward of the rear end (Evan) - the fence is open there. Edges rounded (Evan; radius not measured). Keep this orientation so the charge level stays readable |
| 2 | 2S holder + 2x Samsung 25R, 75.75 x 40.5 x 20.5 | 58.1..133.9 / 44.3..84.8 / 7.0..27.5 | velcro + 14 mm side walls on its lobe plate (v10: end walls removed for the leads and the MB joint) | red / black leads leave the -x (short) end; MB wire 55 mm from the brass rivet on the +x (no-lead) end |
| 3 | Inline 3 A ATO fuse holder, 50 x 34.25 x 12 lying flat | 10..60 / -17.1..17.1 / 40.3..52.3 (on top of the bank) | velcro | in the CELL+ wire (326 mm total, coil the slack); x 10 keeps it out from under the deck's Pi vent window (x 65..137) |
| 4 | 2S BMS (ACEIRMC) 41 x 8 x 2.2 | 92..133 / 44.75..52.75 / 31.5..33.7 (on top of the holder, at its +x rivet end, inner edge) | velcro | pads toward +x - forced by the 55 mm MB wire (not stuck down yet, Evan). Inner edge = shortest P+ / P- run across the bank |
| 5 | USB-C 2S charger (Adeept p0374), turned: 18.3 x 38.43 x 6.3 | 104..122.3 / -85.5..-47.1 / 7.0..13.3 | velcro | USB-C faces -y, out the lobe's outer edge (charge without lifting the deck); BAT / GND pads at the +y end (Evan: opposite the USB-C) |
| 6 | XT30 pair, mated, 25 x 10.5 x 5.3 | 76..101 / -58..-47.5 / 7.0..12.3 | velcro (pack half) | pack half +x (BMS P+ / P-, soldered); car half -x toward the rocker |

## Layer 2 - electronics deck (v11)

Plate x -64..156 (was -6..156), rear posts at x -12 (were 10): the Uno sits on
a 52 mm cantilever behind them, stiffened by two 2 x 3 mm ribs under it.

| # | Part | Box x .. / y .. / z .. | Held by | Ports |
|---|---|---|---|---|
| 1 | Raspberry Pi 5 in Vilros case 91.8 x 64.4 x 27.2 | 40.0..131.8 / -32.2..32.2 / 61.0..88.2 | velcro + 4 corner brackets 10 mm tall (legs 10 mm on the sides, 4 mm on the port ends), +0.25 per side | FRONT (+x): camera connector + USB-C power; REAR (-x): USB-A + LAN (Evan, 2026-10-12); HDMI on a side (unused); fan on top |
| 2 | Arduino Uno R3 + proto shield, 53.7 x 70 x 24 | -58.2..-4.5 / -35..35 / 63.0..87.0 | 4 standoffs (6 mm) + pegs, 2 ribs under | -y end: USB-B (plug box below) and DC jack |
| 3 | LM2596 buck, 5.00 V, with display, 66 x 36 x 14 | 62..128 / -78..-42 / 60.0..74.0 | 4 standoffs + 3.2 pegs (57.5 x 31.5) | display up; terminals at the short ends (assumed) |
| 4 | Rocker switch, 21.0 hole at (42, -64) on the -y wing | body 30.55..53.45 / -75.45..-52.55 / 30.7..54.5 | snap-in | power slot x 38..46, y -49.5..-45.5 for VBAT / GND up to the shield |

## Reserved space (clearance boxes, both layers)

| Space | Box x .. / y .. / z .. | For |
|---|---|---|
| Pi USB-A / LAN plugs | -2..39.7 / -28.4..28.4 / 61..88.2 | 40 mm straight plug; the A-B cable then bends -y and loops to the Uno's USB-B (cable > 18 in, coil the spare) |
| Pi front USB-C + camera ribbon | 132.1..176.8 / -28.4..28.4 / 61..88.2 | 30 mm plug + 15 mm bend; ends ~5 mm short of the camera mast (x ~182 +/- 3, photo estimate - the mast is not in the checker) |
| Pi fan / top access | over the Pi, 15 mm | airflow, SD / cable access |
| Uno shield wiring | over the Uno, 20 mm | Dupont housings, servo / encoder / strip leads |
| Uno USB-B plug | -53..-37 / -72.3..-42.3 / 63.6..76.6 | allowance 16 x 30 x 13 (plug NOT measured) |
| LM2596 terminals | 52..62 and 128..138 / -78..-42 / 60..74 | screw terminals at both short ends (assumed) |
| Rocker terminals | below the body, z 20.7..30.7 | spade / solder tabs |
| Bank USB-C plug | -44.25..-14.25 / -30..-16 / 19..31 | plug at the bank's rear -y corner |
| Bank USB-C cable over the bank | -44..156 / -37..-29 / 37..43 | under the deck, beside the fuse holder |
| Bank USB-C cable rise | 156..166 / -37..-29 / 37..67 | up in front of the tray, outside the servo mount (y -37..-29 vs its |y| <= 20), then back into the Pi's plug |
| P+ / P- crossing | 110..132 / -45..44 / 44..50 | the four 190 mm pack wires over the bank |
| Charger USB-C plug | 108.15..118.15 / -116..-86 / 7..17 | out the car's -y side |
| XT30 unplug room | 56..76 / -58..-47.5 / 7..12.3 | pull the car half off |
| Holder lead exit / MB rivet end | 43.1..58.1 and 133.9..141.9 / 44.25..84.75 / 7..27.5 | leads and the MB joint |

## Every part you have, accounted for

Evan's 2026-10-10 arrival list (record FI; items 2, 10, 13, 14, 17 are row 16
of the order sheet, numbered in FI's order), plus what was already owned or
came later.

| Item | Piece | Goes |
|---|---|---|
| 1 | 2S BMS (8-pack; 1 used) | layer 1 #4 |
| 2 | 22 AWG wire | harness (all power and signal, BOM row 16) |
| 3 | Standard-Mini 200 mm camera cable | Pi front -> camera mast |
| 4 | Pololu #4763 6-pin JST SH cable | motor -> shield (motor power + encoder) |
| 5 | Vilros Pi 5 kit | Pi in its case = layer 2 #1 (SD card inside); PSU / HDMI adapter stay off the car |
| 6 | Fuse holder + fuses | layer 1 #5, on top of the bank |
| 7 | WS2812B reel | two short segments at the car's front and rear, fed from the shield |
| 8 | Rocker switch | deck -y wing (since tray v9 / deck v10; was the rear tab) |
| 9 | XT30 | layer 1 #6 |
| 10 | 470 uF caps | on the shield at the TB6612, and at the strip feed point |
| 11 | TB6612 carrier | on the shield (layer 2 #2) |
| 12 | LM2596 (2-pack; 1 used) | layer 2 #3 |
| 13 | 0.1 uF caps | on the shield at the TB6612 |
| 14 | Heat shrink | harness |
| 15 | MG90D-270 (4-pack; 1 used) | servo mount |
| 16 | Adeept charger | layer 1 #3 |
| 17 | Headers | on the shield (TB6612 socket) |
| 18 | Dupont jumpers | harness / servo lead extension if it is short |
| 19 | Proto shield | on the Uno (layer 2 #2) |
| 20 | Resistor kit | divider 100k + 12k on the shield; strip series resistor |
| 21 | 2S holder | layer 1 #2 |
| 22 | 18650 cells | in the holder |
| owned | Arduino Uno R3 clone | layer 2 #2 |
| owned | Power bank 5 V / 3 A, 168 x 62.16 x 22.51 (2026-10-16; replaced the flaky 151.5 x 70.55 x 18.0 bank) | layer 1 #1 |
| owned | Data-only USB cable | Pi USB-A -> Uno USB-B |
| later | Pololu #5159 motor | motor mount |
| arrived 2026-10-15 | Camera Module 3 Wide (+ a second one, spare) | camera mast |

Spares that stay off the car: 7 BMS boards, 1 LM2596, 3 servos, the rest of
the WS2812B reel and the fuses.

## Cable routes (estimates - nothing is routed on a printed tray yet)

Soldered wires (fixed lengths, Evan 2026-10-16) vs the v9 layout. Manhattan =
along the axes; diagonal = straight across the bank top. The BMS P pads are
taken at ~(131, 49, 33.7).

| Wire | Length (fixed) | Route | Needs (Manhattan / diagonal) | Slack |
|---|---|---|---|---|
| BMS P+ / P- -> charger BAT / GND (2 wires) | 190 | holder top -> over the bank top (z 36.3, under the deck) -> down the -y side at x ~110-131 (clear of the encoder rise at x 100..108) -> charger +y end | ~149 / ~135 | ~40-55 |
| BMS P+ / P- -> XT30 pack half (2 wires) | 190 | same, to the XT30's +x end | ~168 / ~146 | ~20-45 |
| MB: holder rivet (+x end) -> BMS MB | 55 | up the holder's +x end face onto its top | ~20-30 | ~25-35 |
| CELL+ -> fuse -> BMS B+ | 326 total | holder -x end -> fuse on the bank top (x 10..60) -> holder top | ~150-200 | coil the rest |
| Holder black -> BMS B- | NOT recorded | along the holder top, -x end -> +x end | ~90 | unknown - bench-check |
| Encoder #4763 | 300 (uncut) | motor socket below the frames (x ~110, y ~0) -> up through the frame opening there (Evan: there is one) -> along the frame top UNDER the tray floor -> -y rail notch + edge-rib notch (x 100..108) -> up the floor slot beside the bank fence (y -41..-38.5) -> deck slot right above -> along the deck to the shield at the rear | ~220-270 (v11: the Uno moved back 56 mm) | ~30-80; if short, splice Dupont leads at the shield end |

Unsoldered runs (cut to fit):

| From -> to | Route | ~Length |
|---|---|---|
| XT30 car half -> rocker | lobe (z ~10) up to the rocker terminals (z ~31) under the -y wing | ~80 |
| Rocker out (VBAT) + GND -> shield | up through the wing's power slot (x 38..46) -> shield; VBAT also to the LM2596 VIN next to it | ~60-100 |
| LM2596 VOUT -> shield `+5V2` | deck wing -> shield | short |
| Bank USB-C (-y rear corner) -> Pi USB-C (front) | under the deck over the bank (y -37..-29), up in front of the tray, back into the Pi's front plug | ~300-350 - Evan's cable is only known to be "> 25 cm": measure it; a longer or right-angle cable is a purchase (Evan's call) |
| Pi USB-A -> Uno USB-B | Pi rear -> 40 mm plug zone -> bend -y -> Uno's -y end | ~150-200 of > 457; coil the spare |
| Servo lead | servo (x ~170) -> along the deck -> shield at the rear | ~260-300 of ~250 - needs a Dupont extension (on hand) |
| Camera cable | Pi front -> camera mast | ~110-135 of 200 |
| Strip segments | shield -> car front / rear | per segment |

Wiring rules live in `docs/WIRING_PROTOSHIELD.md` (section 2.1: nothing but
the BMS touches B+ / MB / B-; star ground at the TB6612 GND pad).

## Verification (2026-10-16, tray v10 / deck v11)

- `render_scad.py`: tray 252/252 probes, deck 96/96, both manifold, exit 0
  (re-run by Opus: byte-identical to the agents' STLs).
- `./.venv/Scripts/python.exe scripts/electronics_layout.py`: 34 entries, 0
  checks failed - no part, zone or clearance box contains printed material, no
  two boxes overlap, every part rests on plastic or on another box.

What this does NOT prove: any fit (unprinted), the plug sizes (estimates), the
camera mast and servo mount clearances (not in the checker), the velcro's real
thickness, or that the cables reach.

## Still to measure / check (before printing)

- **Bench check (cheap, do first):** hold the BMS on the holder top at the rivet
  end (pads toward +x, inner edge) and confirm B-, MB and fuse -> B+ all reach;
  lay the 190 mm P wires across a 62 mm-wide stand-in for the bank to the
  charger / XT30 spots.
- The velcro pair's real thickness (4 mm assumed in both .scad files).
- The bank USB-C -> Pi cable length (needs ~300-350 mm by the reserved route).
- That the Pi's outer ports clear the 4 mm bracket legs on the port ends.
- Lay the encoder cable along its route (~220-270 of 300).
- The bank's charge LEDs: where they are, and whether the deck hides them.
- The USB-B plug body (16 x 30 x 13 allowance).
- The two Uno holes as a spot check of the peg pattern.
