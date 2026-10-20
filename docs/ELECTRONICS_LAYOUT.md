# Electronics layout - where every part goes (2026-10-16, tray v11 / deck v12)

**Status: PLAN, UNTESTED.** Nothing here has been printed or fitted. Parts
and positions come from the `LAYOUT` lists in
`cad/scad/electronics_tray.scad` (layer 1) and `cad/scad/electronics_deck.scad`
(layer 2); `scripts/electronics_layout.py` reads them, checks them against
the rendered STLs and draws `docs/electronics_layout.svg`. Change a position
in the .scad, never here, then re-run the script. Records: the entry of
2026-10-13 that introduced this file; records JU (v9 / v10) and JV (v10 / v11, cable room) and the 2026-10-16 entry for v11 / v12 (Evan's bench results).

![layout](electronics_layout.svg)

**Frame (mm):** x along the car, x = 0 at the rear corner pin hole of the
centre frames, **+x = front**; y across, +y = the car's left (up in the drawing);
z = 0 on the Lego frames' top face. Layer 1: the bank on the raised middle
floor (z 9.8); everything else on the two lobe plates, which sit on the frames
(z 0..3). Layer 2 on the deck (underside z 54.5, top z 57.0 - raised 8.5 mm on
2026-10-16 for the taller bank and the velcro under the fuse holder on it).
**Every part sits on velcro: 15.5 mm dots, 3.5 mm per mated pair** (the
`VELCRO` constant; measured by Evan 2026-10-16): bank, holder, Pi case, fuse holder, BMS, charger, XT30 - all
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
| 1 | Power bank (Pi only) 168 x 62.16 x 22.51 | -14.25..153.75 / -31.08..31.08 / 13.3..35.8 | velcro + bank fence 18 mm tall (top z 27.8), open rear; the -y wall starts at x 15 | REAR end (-x): USB-C at the -y corner, USB-A at the +y corner (Evan). Charge button on the -y side face ~10 mm forward of the rear end (Evan) - the fence is open there. Edges rounded (Evan; radius not measured). Charge LEDs on the TOP near the -y side, ~10-40 mm from the rear end (x ~-4..26, Evan): read them from the car's -y side through the gap under the deck - nothing sits on or beside that strip |
| 2 | 2S holder + 2x Samsung 25R, 75.75 x 40.5 x 20.5 | 58.1..133.9 / 44.3..84.8 / 7.0..27.5 | velcro + 14 mm side walls on its lobe plate (v10: end walls removed for the leads and the MB joint) | red / black leads leave the -x (short) end; MB wire 55 mm from the brass rivet on the +x (no-lead) end |
| 3 | Inline 3 A ATO fuse holder, 50 x 34.25 x 12 lying flat | 30..80 / -17.1..17.1 / 39.3..51.3 (on top of the bank) | velcro | in the CELL+ wire (326 mm total, coil the slack); x 30 keeps it off the bank's charge LEDs; 3.2 mm under the deck |
| 4 | 2S BMS (ACEIRMC) 41 x 8 x 2.2 | 92..133 / 44.75..52.75 / 31.5..33.7 (on top of the holder, at its +x rivet end, inner edge) | velcro | pads toward +x - forced by the 55 mm MB wire (not stuck down yet, Evan). Inner edge = shortest P+ / P- run across the bank |
| 5 | USB-C 2S charger (Adeept p0374), turned: 18.3 x 38.43 x 6.3 | 104..122.3 / -85.5..-47.1 / 7.0..13.3 | velcro | USB-C faces -y, out the lobe's outer edge (charge without lifting the deck); BAT / GND pads at the +y end (Evan: opposite the USB-C) |
| 6 | XT30 pair, mated, 25 x 10.5 x 5.3 | 76..101 / -58..-47.5 / 7.0..12.3 | velcro (pack half) | pack half +x (BMS P+ / P-, soldered); car half -x toward the rocker |

## Layer 2 - electronics deck (v11)

Plate x -64..156 (was -6..156), rear posts at x -12 (were 10): the Uno sits on
a 52 mm cantilever behind them, stiffened by two 2 x 3 mm ribs under it.

| # | Part | Box x .. / y .. / z .. | Held by | Ports |
|---|---|---|---|---|
| 1 | Raspberry Pi 5 in Vilros case 91.8 x 64.4 x 27.2 | 40.0..131.8 / -32.2..32.2 / 60.5..87.7 | velcro + brackets 10 mm tall: +x end legs 4 mm, both +y side legs, the -y side leg at the -x corner (v12: the -x end legs and the -y leg at the +x corner removed so the plugs clear) | -x: USB-A + LAN, 4 mm from the case sides (Evan); -y SIDE: USB-C ~7 mm from the +x end (Evan 2026-10-16 - NOT the back end, as the 2026-10-12 note implied); +x: camera opening mid-face (Evan is modifying the case); fan on top |
| 2 | Arduino Uno R3 + proto shield, 53.7 x 70 x 24 | -58.2..-4.5 / -35..35 / 63.0..87.0 | 4 standoffs (6 mm) + pegs, 2 ribs under | -y end: USB-B (plug box below) and DC jack |
| 3 | LM2596 buck, 5.00 V, with display, 66 x 36 x 14 | 10..76 / -74..-38 / 60.0..74.0 (v13: +4 in y, 4 mm clear of the lobe boss at (60, -82)) | 4 standoffs + 3.2 pegs (57.5 x 31.5) | display up; terminals at the short ends (Evan confirmed) |
| 4 | Rocker switch, 21.0 hole at (100, -64) on the -y wing (WING_X 0..132) | body 88.55..111.45 / -75.45..-52.55 / 30.7..54.5 | snap-in | hangs over the XT30 / charger (terminals end z 20.7, charger top 13.3); power slot x 96..104, y -49.5..-45.5 for VBAT / GND up to the shield |

## Reserved space (clearance boxes, both layers)

| Space | Box x .. / y .. / z .. | For |
|---|---|---|
| Pi USB-A / LAN plugs | -2..39.7 / -32.2..32.2 / 60.5..87.7 | 40 mm straight plug; the A-B cable then bends -y and loops to the Uno's USB-B (cable > 18 in, coil the spare) |
| Pi front camera ribbon | 132.1..176.8 / -28.4..28.4 / 60.5..87.7 | camera opening mid-face; ends ~5 mm short of the camera mast (x ~182 +/- 3, photo estimate; the mast is unprinted and can move - Evan) |
| Pi USB-C plug (-y side) | 116.8..131.8 / -77.2..-32.2 / 60.5..87.7 | 30 mm plug + 15 mm bend, out the Pi's -y side over the wing's front end |
| Pi fan / top access | over the Pi, 15 mm | airflow, SD / cable access |
| Uno shield wiring | over the Uno, 20 mm | Dupont housings, servo / encoder / strip leads |
| Uno USB-B plug | -53..-37 / -72.3..-42.3 / 63.6..76.6 | allowance 16 x 30 x 13 (plug NOT measured) |
| LM2596 terminals | 0..10 and 76..86 / -74..-38 / 60..74 | screw terminals at both short ends (Evan confirmed) |
| Rocker terminals | below the body, z 20.7..30.7 | spade / solder tabs |
| Bank USB-C plug | -44.25..-14.25 / -30..-16 / 19..31 | plug at the bank's rear -y corner |
| Bank USB-C cable along the bank's -y side | -14..154 / -37.6..-33.6 / 28..34 | below the bank's top, so it never covers the charge LEDs |
| Bank USB-C cable rise | 133..141 / -50..-42 / 34..74 | up outside the deck edge just past the wing's front end, then into the Pi's -y side plug |
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
| CELL+ -> fuse -> BMS B+ | 326 total | holder -x end -> fuse on the bank top (x 30..80) -> holder top | ~150-200 | coil the rest |
| Holder black -> BMS B- | NOT recorded | along the holder top, -x end -> +x end | ~90 | unknown - bench-check |
| Encoder #4763 | 300 (uncut) | motor socket below the frames (x ~110, y ~0) -> up through the frame opening there (Evan: there is one) -> along the frame top UNDER the tray floor -> -y rail notch + edge-rib notch (x 100..108) -> up the floor slot beside the bank fence (y -41..-38.5) -> deck slot right above -> along the deck to the shield at the rear | ~220-270 (v11: the Uno moved back 56 mm) | ~30 by Evan's lay-out (2026-10-16; path hard to judge) - tight; if short, splice Dupont leads at the shield end |

Unsoldered runs (cut to fit):

| From -> to | Route | ~Length |
|---|---|---|
| XT30 car half -> rocker | XT30 (x 76) straight up to the rocker terminals right above it (x ~89-111, z ~21-31) | ~30-50 |
| Rocker out (VBAT) + GND -> shield | up through the wing's power slot (x 96..104) -> along the deck to the shield at the rear; VBAT also to the LM2596 VIN (its +x end, x 76) | ~150-200 to the shield, ~30 to the LM2596 |
| LM2596 VOUT -> shield `+5V2` | deck wing -> shield | short |
| Bank USB-C (-y rear corner) -> Pi USB-C (-y side) | along the bank's -y side below its top, up past the wing's front end, into the Pi's side plug | ~250-300; Evan's cable is "a lot longer than 320" (2026-10-16) - coil the spare |
| Pi USB-A -> Uno USB-B | Pi rear -> 40 mm plug zone -> bend -y -> Uno's -y end | ~150-200 of > 457; coil the spare |
| Servo lead | servo (x ~170) -> along the deck -> shield at the rear | ~260-300 of ~250 - needs a Dupont extension (on hand) |
| Camera cable | Pi front -> camera mast | ~110-135 of 200 |
| Strip segments | shield -> car front / rear | per segment |

Wiring rules live in `docs/WIRING_PROTOSHIELD.md` (section 2.1: nothing but
the BMS touches B+ / MB / B-; star ground at the TB6612 GND pad).

## Verification (2026-10-16, tray v11 / deck v12)

- `render_scad.py`: tray 252/252 probes (STL byte-identical to v10: LAYOUT-only
  change), deck 97/97, both manifold, exit 0 (re-run by Opus: identical to the
  agents' STLs).
- `./.venv/Scripts/python.exe scripts/electronics_layout.py`: 35 entries, 0
  checks failed. Since 2026-10-20 a part's sides must also be 0.2 mm clear of
  material (deck v12 put the LM2596 flush against a boss; Evan caught it). Fuse holder top z 51.3 -> 3.2 mm under the deck (two velcro
  pairs).
- Camera mast (2026-10-16): `cad/camera_mast.stl` is loaded into the tray frame
  (servo shaft taken at x 167, the near end of the photo's 170 +/- 3) and counts
  as material, so no box reaches into it. Nearest box behind it: the Pi front
  camera-ribbon zone, sampled gap 9.0 mm (+/- 0.5; ~12 at the nominal 170).

What this does NOT prove: any fit (unprinted), the plug sizes (estimates), the
servo mount clearance (not in the checker), the mast's real position (photo
estimate), or that the cables reach.

## Bench results (Evan, 2026-10-16, before printing)

| Check | Result |
|---|---|
| Bank USB-C -> Pi cable | "a lot longer than 320 mm" - OK |
| Encoder cable laid along the route | ~30 mm spare (path hard to judge) - tight but OK |
| 45 mm plug + bend allowance | right; the camera mast is unprinted and can change |
| Pi port positions | USB-A + LAN 4 mm from the case sides; USB-C on the -y SIDE ~7 mm from the +x end; camera opening mid +x face, ~5-6 mm (case being modified) |
| BMS at the rivet end, all pack wires | room to spare |
| Velcro | 15.5 mm dots, 3.5 mm per mated pair |
| Bank charge LEDs | top, near the -y (button) side, ~10-40 mm from the port end; read from the side |
| LM2596 terminals | on the short ends |

## Still to measure / check

- The camera mast's real position once printed (the checker assumes the servo
  shaft at x 167..170 from a photo); Evan's case modification for the camera
  opening.
- The encoder cable's real path once installed (~30 mm spare).
- The USB-B plug body (16 x 30 x 13 allowance).
- The two Uno holes as a spot check of the peg pattern.
