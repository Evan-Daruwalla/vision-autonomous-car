# Electronics layout - where every part goes (2026-10-13)

**Status: PLAN, UNTESTED.** Nothing here has been printed or fitted. Parts
and positions come from the `LAYOUT` lists in
`cad/scad/electronics_tray.scad` (layer 1) and `cad/scad/electronics_deck.scad`
(layer 2); `scripts/electronics_layout.py` reads them, checks them against
the rendered STLs and draws `docs/electronics_layout.svg`. Change a position
in the .scad, never here, then re-run the script. Record: the entry of
2026-10-13 that introduced this file.

![layout](electronics_layout.svg)

**Frame (mm):** x along the car, x = 0 at the rear corner pin hole of the
centre frames, **+x = front**; y across, +y = the car's left (up in the drawing);
z = 0 on the Lego frames' top face. Layer 1: the bank on the raised middle
floor (z 9.8); everything else on the two lobe plates, which sit on the frames
(z 0..3, tray v8);
layer 2 on the deck (underside z 46.0, top z 48.5: raised on 2026-10-13 for
the 2S holder, the fuse holder on the bank, and the 4 mm velcro under the bank).
The bank, holder and Pi case sit on ~4 mm velcro (removable; Evan); the
charger, BMS and XT30 on tape or velcro. No zip ties anywhere - every tie slot
was removed (tray v8, deck v9).
Printed in Bambu PETG Translucent.

## Layer 1 - electronics tray

| # | Part | Box x .. / y .. / z .. | Held by | Ports / leads |
|---|---|---|---|---|
| 1 | Power bank (Pi only) 151.5 x 70.55 x 18.0 | -4..147.5 / -35.3..35.3 / 13.8..31.8 | ~4 mm velcro + bank fence 14 mm tall (holds the flat sides; edges rounded below 7 mm), open rear | USB-C + USB-A on the REAR end (-x), 20 / 45 mm from the left |
| 2 | 2S holder + 2x Samsung 25R, 75.75 x 40.5 x 20.5 (measured 20.30 tall) | 58.1..133.9 / 44.3..84.8 / 7.0..27.5 | ~4 mm velcro + 4-sided 14 mm fence on its lobe plate | red / black leads leave the SAME SHORT end (Evan 2026-10-14), 160 mm; + the MB wire soldered to the series strap. Seat the holder with that end at -x (x 58), the end nearest the fuse and the BMS |
| 3 | USB-C 2S charger (Adeept p0374) 38.43 x 18.30 x 6.30 | 60..98.4 / -69.5..-51.2 / 3.0..9.3 | double-sided tape or velcro | pads BAT (-> BMS P+), GND (-> P-), GND, VIN; USB-C on a SHORT end (Evan 2026-10-14) -> faces -x, 4 mm from the open lobe edge (x 56); the plug sticks out past that edge |
| 4 | 2S BMS (ACEIRMC) 41 x 8 x 2.2 | 66..107 / -83..-75 / 3.0..5.2 | double-sided tape | pads B+ B- MB P+ P- |
| 5 | Inline 3 A ATO fuse holder, 50 x 34.25 x 12 lying flat | 40..90 / 0..34.3 / 31.8..43.8 (ON TOP of the bank) | tape or velcro | in the CELL+ wire, before the BMS |
| 6 | XT30 pair, mated, 25 x 10.5 x 5.3 | 104..129 / -66..-55.5 / 3.0..8.3 | double-sided tape or velcro (pack half) | BMS P+/P- side; car side goes to the rocker |

## Layer 2 - electronics deck

| # | Part | Box x .. / y .. / z .. | Held by | Ports |
|---|---|---|---|---|
| 1 | Raspberry Pi 5 in Vilros case 91.8 x 64.4 x 27.2 (confirmed) | 55.1..146.9 / -32.2..32.2 / 52.5..79.7 | ~4 mm velcro + 4 corner brackets 10 mm tall, +0.25 per side | FRONT (+x): camera connector + USB-C power; REAR (-x): 2x USB-A + LAN |
| 2 | Arduino Uno R3 + proto shield (TB6612 on headers, 470 uF + 0.1 uF, 100k/12k divider), 53.7 x 70 x 24 | -2.2..51.5 / -35..35 / 54.5..78.5 | 4 standoffs (6 mm, so the USB plug clears the pin boss) + pegs | -y end: USB-B (centre 13 mm from the left edge, sticks out 7.3) and DC jack (43 mm, 4.1) |
| - | USB-B plug clearance (allowance 16 x 30 x 13; plug NOT measured) | 3..19 / -72.3..-42.3 / 55.1..68.1 | hangs from the jack | must stay empty: passes over the pin boss at (10, -41.6), top z 53.8 |
| 3 | LM2596 buck, 5.00 V, with display, 66 x 36 x 14 | 62..128 / -78..-42 / 51.5..65.5 | 4 standoffs + 3.2 pegs on 57.5 x 31.5 hole centres (measured) | display up; trim pot set to 5.00 V unloaded, then locked |
| - | Rocker switch: body 20.50 dia (22.90 over the clips), 23.8 deep | 21.0 hole at (-18, -32) on the rear tab | snap-in | body hangs ~24 mm below the tab, behind the tray (space clear - Evan) |

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
| 8 | Rocker switch | deck rear tab |
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
| owned | Power bank 5 V / 3 A | layer 1 #1 |
| owned | Data-only USB cable | Pi USB-A -> Uno USB-B |
| later | Pololu #5159 motor | motor mount |
| in shipping | Camera Module 3 Wide | camera mast |

Spares that stay off the car: 7 BMS boards, 1 LM2596, 3 servos, the rest of
the WS2812B reel and the fuses.

## Cable routes (planned, lengths are estimates)

| From -> to | Route | ~Length |
|---|---|---|
| Holder red -> fuse -> BMS B+; black -> B-; MB -> MB | out of the holder's lead end, up onto the bank top (fuse there), across under the deck (14.2 mm over the bank), down into the -y lobe | black to B- ~155-175 mm straight-line estimate from the -x end (2026-10-14: 33 up onto the bank + 70 across + 53 down to the BMS, before slack) vs 160 mm leads - likely short; plan a 22 AWG extension. Red only has to reach the fuse (~45 mm) |
| Charger BAT+/BAT- -> BMS P+/P- | inside the -y lobe | short |
| BMS P+/P- -> XT30 (pack side) | inside the -y lobe | short |
| XT30 (car side) -> rocker -> VBAT | up the -y lobe's outer edge onto the deck wing, back along the deck to the rear tab; VBAT then to the shield (TB6612 VMOT, LM2596 VIN, divider top) | ~190 mm |
| LM2596 VOUT -> shield `+5V2` | deck wing -> shield | short |
| Bank USB-C -> Pi USB-C | from the bank's REAR end, up behind the deck, forward along the deck's +y side to the Pi's front | ~230 mm - Evan has a USB-C cable > 25 cm |
| Pi USB-A -> Uno USB-B | Pi rear end -> Uno's -y end, on the deck | short; Evan's A-B cable is > 18 in - coil the spare |
| Motor + encoder (#4763) | motor below the frames -> -y rail notch (x 100..108) -> under the tray floor -> up the floor + deck slot (x 100..108, y -41..-38.5) -> shield | ~165 mm of 300 (record HE) |
| Servo lead | servo (tray x ~170) -> along the deck -> shield | ~150-200 mm; the lead is ~25 cm (measured) |
| Camera cable | Pi front -> camera mast | 85-110 mm of 200 (record HE) |
| Strip segments | shield -> car front / rear | per segment |

Wiring rules live in `docs/WIRING_PROTOSHIELD.md` (section 2.1: nothing but
the BMS touches B+ / MB / B-; star ground at the TB6612 GND pad).

## Verification (2026-10-13, tray v8 / deck v9)

`./.venv/Scripts/python.exe scripts/electronics_layout.py`: 14 entries, 0
checks failed - no part, zone or clearance box contains printed material
(tray or deck), no two boxes overlap, every part rests on printed material
or on another box (velcro on the floor, the bank on velcro, the fuse holder
on the bank), and the gap from each layer-1 top to the deck underside (z
46.0) is 2.2 mm (fuse holder on the bank), 14.2 (bank), 18.5 (holder),
36.7 (charger), 37.7 (XT30), 40.8 (BMS). The USB-B plug allowance starts 1.3 mm
above the pin boss it crosses; with 4 mm Uno standoffs it would hit it.

What this does NOT prove: any fit (unprinted), the USB-B plug's real size
(an allowance), that the space past the -y lobe's -x edge is clear for the charger's USB-C plug, or that the cables reach.

## Still to measure / check

- The USB-B plug body (the 16 x 30 x 13 allowance is a guess).
- What on the car sits past the -y lobe's -x edge (x < 56, y -70..-51, z 3..10): the charger's USB-C plug and cable need ~30 mm there (USB-C on a short end, Evan 2026-10-14).
- Whether the holder's 160 mm leads reach the BMS once routed.
- The velcro's real thickness (4 mm assumed; it is the `VELCRO` constant in both .scad files).
- The two Uno holes as a spot check of the peg pattern (not measured).
