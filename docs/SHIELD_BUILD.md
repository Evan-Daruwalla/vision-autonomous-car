# Proto shield v.5 - hole-by-hole layout (2026-10-20)  [PASS]

Top view, the Uno's USB end on the LEFT, digital headers at the top. Hole = ROW/COL.

## Notes

- Grid read off Evan's photos (2026-10-20). Rows: T top rail; P1 P2 plain; U1-U3 upper 3-hole strips (cols 1-10); G GND rail; V 5V rail (= the Uno 5V = the Pi's USB); L1-L3 lower strips; P3 P4 plain; B bottom GND rail = the STAR (Evan's choice).
- Cols 1-10 = the ten short strips counted from the USB end; 11-13 = plain holes right of them; 0 and negative = the plain field left of the strips.
- MEASURED by Evan 2026-10-20 (shield off the Uno): T, V = 5V header pin (beep); G, B = GND header pin (beep); G-B beep; neighbouring strips silent; the Uno pins reach the shield only through their own sockets. Step 0 re-checks the two items not yet metered: U1/1-U3/1 beep (one strip) and V-G / V-B silent.
- Uno connections are Dupont male pins plugged into the shield's own sockets (Evan). Off-board cables use 0.1 in male headers (Evan).
- The 470 uF for the LED strips goes AT each strip's input pads (+5V / GND), not on the shield - that is where the WS2812B guidance puts it.
- The TB6612 VM bulk cap C1 (470 uF) and C2 (0.1 uF) are soldered across the carrier's VMOT and GND pin tips on top of the carrier.
- DIN_F / DIN_R: the D4 / D7 Dupont wires each carry 200 + 200 ohm soldered in series inside the wire (heat-shrunk). KEY = J5's pulled pin, no connection.

## Parts

- **TB** (TB6612 carrier, chip up): PWMA = U2/1, AIN2 = U2/2, AIN1 = U2/3, STBY = U2/4, BIN1 = U2/5, BIN2 = U2/6, PWMB = U2/7, GND3 = U2/8, GND1 = L2/1, VCC = L2/2, AO1 = L2/3, AO2 = L2/4, BO2 = L2/5, BO1 = L2/6, VMOT = L2/7, GND2 = L2/8 - Orientation: put a marker dot on the PWMA pad (label side), flip chip-up, dot at the TOP-LEFT. Top row = control, bottom row = power.
- **J1** (4-pin header: motor): M1 = P3/3, M2 = P3/4, GND = P3/5, 5V2 = P3/6 - Encoder yellow (A) and white (B) do NOT go here: give them male Dupont pins and plug them straight into the D2 / D3 sockets.
- **J5** (4-pin header: power in): VBAT = L3/10, KEY = P3/10, 5V2 = P4/10, GND = B/10 - W9 VBAT, (key), W14 +5V2, W12 pack - (motor return).
- **J6** (1-pin header: W13): GND = B/11 - W13: LM2596 IN- / OUT-.
- **J3** (3-pin header: front strip): DIN = P3/12, 5V2 = P4/12, GND = B/12 - Cable order: DIN, +5V, GND.
- **J4** (3-pin header: rear strip): DIN = P3/13, 5V2 = P4/13, GND = B/13 - Cable order: DIN, +5V, GND.
- **JP1** (3-pin header: servo-power jumper): UNO5V = L1/-1, SERVO_V = L2/-1, 5V2 = L3/-1 - Put the Dupont female-female jumper (or a jumper cap) on the TOP two pins (UNO5V + SERVO_V) = servo on the Uno 5V (Evan, JR). Move it to the bottom two = servo on +5V2 (fallback).
- **J2** (3-pin header: servo): SIG = L1/-2, V = L2/-2, GND = L3/-2 - Servo plug: orange/white = SIG at the top, red in the middle, brown/black = GND at the bottom.
- **R100k** (100k, lying flat): a = L1/9, b = U3/9 - Body lies over G/9 and V/9 - leads go ONLY into L1/9 and U3/9.
- **R10k** (10k, standing): a = U2/9, b = U2/10
- **R2k** (2k, standing): a = U3/10, b = G/10
- **C1** (470 uF on the carrier, off-board): + -> TB.VMOT, - -> TB.GND2 - + lead (no stripe) to the VMOT pin tip, - lead (stripe side) to the GND pin tip next to it, at the right end of the carrier's bottom row.
- **C2** (0.1 uF on the carrier, off-board): a -> TB.VMOT, b -> TB.GND2 - Same two pin tips as C1; no polarity.

## Wires (top side)

- **w1**: L3/7 -> L3/9 [VBAT] - VMOT to the VBAT strip, insulated, hops over L3/8
- **w2**: L3/8 -> B/8 [GND] - TB6612 GND to the star rail, hops over P3/8 and P4/8
- **w3**: L3/2 -> V/0 [UNO5V] - TB6612 VCC to the Uno 5V - ROUTE: left along row L3, then up column 0 (never under the carrier)
- **w4**: P4/7 -> P3/-1 [5V2] - +5V2 to JP1's bottom pin - ROUTE: left along row P4 under the J1 pins, then up to P3/-1
- **w5**: B/2 -> P3/-2 [GND] - servo GND to the star - ROUTE: left along row B, then up to P3/-2

## Solder bridges (bottom side)

- L3/3 - P3/3
- L3/4 - P3/4
- P3/5 - P4/5
- P4/5 - B/5
- P3/6 - P4/6
- P4/6 - P4/7
- P4/7 - P4/8
- P4/8 - P4/9
- P4/9 - P4/10
- P4/10 - P4/11
- P4/11 - P4/12
- P4/12 - P4/13
- L2/9 - L2/10
- L3/12 - P3/12
- L3/13 - P3/13
- V/1 - V/0
- V/0 - V/-1
- V/-1 - L1/-1
- L3/-1 - P3/-1
- L2/-2 - L2/-1
- L1/-2 - L1/-3
- L3/-2 - P3/-2

## Uno sockets and joins

- Dupont U1/1 -> Uno D11
- Dupont U1/2 -> Uno D12
- Dupont U1/3 -> Uno D8
- Dupont U1/4 -> Uno D10
- Dupont U1/9 -> Uno A0
- Dupont L1/-3 -> Uno D9
- Dupont L3/12 -> Uno D4
- Dupont L3/13 -> Uno D7
- direct: encoder yellow (A) -> Uno D2 - male Dupont pin on the cable end, straight into the D2 socket
- direct: encoder white (B) -> Uno D3 - male Dupont pin on the cable end, straight into the D3 socket
- join TB.PWMA <-> TB.PWMB - carrier-top wire bridge (logic)
- join TB.AIN2 <-> TB.BIN2 - carrier-top wire bridge (logic)
- join TB.AIN1 <-> TB.BIN1 - carrier-top wire bridge (logic)
- join TB.AO1 <-> TB.BO1 - carrier-top wire bridge, 22 AWG (motor current)
- join TB.AO2 <-> TB.BO2 - carrier-top wire bridge, 22 AWG (motor current)

## Steps

1. **0. Remaining meter checks BEFORE any solder (shield OFF the Uno, continuity mode)**
   - Already done by Evan 2026-10-20: T and V beep to 5V; G and B beep to GND; G beeps to B; neighbouring strips silent.
   - 0.1 U1/1 to U3/1: must BEEP (one strip, three holes)
   - 0.2 V/12 to G/12 and V/12 to B/13: must be SILENT
   - If either differs, STOP and send me the result.
   - Check: both match
2. **1. TB6612 headers and carrier-top work (off the shield)**
   - Solder the two 8-pin headers to the carrier: SHORT ends up through the carrier, LONG ends down.
   - Mark PWMA (label side) with a dot.
   - On the carrier's top, solder insulated wire bridges between the pin tips: PWMA-PWMB, AIN2-BIN2, AIN1-BIN1 (any thin wire), AO1-BO1 and AO2-BO2 (22 AWG).
   - Solder C1 (470 uF): + lead to the VMOT tip, stripe (-) lead to the GND tip next to it (bottom row, right end); lay the can flat on the carrier.
   - Solder C2 (0.1 uF) across the same VMOT and GND tips.
   - Check: meter: PWMA-PWMB, AIN1-BIN1, AIN2-BIN2, AO1-BO1, AO2-BO2 each BEEP; VMOT-GND does NOT beep (C1 may chirp once)
3. **2. Carrier onto the shield**
   - Chip up, dot at the top-left: top row pins into U2/1 ... U2/8, bottom row pins into L2/1 ... L2/8.
   - Solder all 16 on the underside; trim the leftover pin length.
   - Check: U1/1 beeps to the PWMA pin; L3/7 beeps to VMOT; L3/1 beeps to L3/8 (GND through the carrier)
4. **3. Bottom-side solder bridges (each joins exactly two neighbouring holes)**
   - Motor outputs: L3/3-P3/3, L3/4-P3/4.
   - J1 GND: P3/5-P4/5 and P4/5-B/5.  J1 +5V2: P3/6-P4/6.
   - +5V2 bus along row P4: P4/6-P4/7-P4/8-P4/9-P4/10-P4/11-P4/12-P4/13.
   - DANGER: P4/5 (GND) and P4/6 (+5V2) are neighbours - they must NOT touch.
   - VBAT strips: L2/9-L2/10.  Strip data: L3/12-P3/12, L3/13-P3/13.
   - Uno 5V to the left field: V/1-V/0, V/0-V/-1, V/-1-L1/-1.
   - Servo block: L3/-1-P3/-1, L2/-2-L2/-1, L1/-2-L1/-3, L3/-2-P3/-2.
   - DANGER: P3/-1 (+5V2) and P3/-2 (GND) are neighbours - must NOT touch.
   - Check: P4/5 to P4/6 SILENT; P3/-1 to P3/-2 SILENT; P4/6 beeps to P4/13; V/12 beeps to L1/-1
5. **4. Headers**
   - J1 (4 pins) in P3/3, P3/4, P3/5, P3/6.
   - J5 (4 pins, pull out the 2nd pin) in L3/10, P3/10, P4/10, B/10.  J6 (1 pin) in B/11.
   - J3 in P3/12, P4/12, B/12.  J4 in P3/13, P4/13, B/13.
   - JP1 in L1/-1, L2/-1, L3/-1.  J2 in L1/-2, L2/-2, L3/-2.
   - Check: J5 top pin (L3/10) beeps to VMOT; J3 middle beeps to J4 middle (+5V2); J3 bottom beeps to B/8
6. **5. Divider**
   - R100k lying flat: leads into L1/9 and U3/9 only (body over G/9, V/9).
   - R10k standing: U2/9 and U2/10.  R2k standing: U3/10 and G/10.
   - Check: L1/9 to U3/9 = ~100k; U3/9 to G/10 = ~12k
7. **6. Top-side jumper wires (insulated 22 AWG)**
   - w1 L3/7 -> L3/9 (VMOT to the VBAT strip).
   - w2 L3/8 -> B/8 (TB6612 GND to the star).
   - w3 L3/2 -> V/0 (TB6612 VCC to the Uno 5V).
   - w4 P4/7 -> P3/-1 (+5V2 to JP1's bottom pin).
   - w5 B/2 -> P3/-2 (servo GND to the star).
   - Check: VBAT (L3/10) to B/10 SILENT; V/0 to B/2 SILENT; P4/7 to B/2 SILENT
8. **7. Dupont wires to the Uno sockets (cut a male-male jumper, solder the cut end in the hole)**
   - U1/1 -> D11, U1/2 -> D12, U1/3 -> D8, U1/4 -> D10.
   - U1/9 -> A0.  L1/-3 -> D9.
   - L3/12 -> D4 and L3/13 -> D7, each with 200 + 200 ohm soldered in series IN the wire, heat-shrunk.
   - Encoder yellow -> D2 socket, white -> D3 socket (male pins on the cable, not through the shield).
   - Check: with the shield on the Uno: each socket pin beeps to its hole; the Uno's 5V pin beeps to V/12
9. **8. Before the first power-up**
   - Re-run every SILENT check from steps 0, 3 and 6.
   - Jumper on JP1's TOP two pins (servo on the Uno 5V).
   - Pack OFF (rocker), Uno on the Pi's USB first; then rocker ON with nothing else plugged in and meter VBAT at J5 (~8 V) and +5V2 at J3 middle (~5.0 V).
   - Check: VBAT ~ pack voltage, +5V2 ~ 5.0 V, Uno 5V ~ 5 V and NOT tied to +5V2 (V/12 to P4/13 silent with the power off)

## Solder-bridge hazards - meter each pair SILENT after the bridges

- [ ] B/10 (GND) - P4/10 (5V2): silent
- [ ] B/11 (GND) - P4/11 (5V2): silent
- [ ] B/12 (GND) - P4/12 (5V2): silent
- [ ] B/13 (GND) - P4/13 (5V2): silent
- [ ] B/6 (GND) - P4/6 (5V2): silent
- [ ] B/7 (GND) - P4/7 (5V2): silent
- [ ] B/8 (GND) - P4/8 (5V2): silent
- [ ] B/9 (GND) - P4/9 (5V2): silent
- [ ] G/1 (GND) - V/1 (UNO5V): silent
- [ ] L1/-1 (UNO5V) - L1/-2 (SERVO_SIG): silent
- [ ] L1/-1 (UNO5V) - L2/-1 (SERVO_V): silent
- [ ] L1/-2 (SERVO_SIG) - L2/-2 (SERVO_V): silent
- [ ] L1/1 (GND) - V/1 (UNO5V): silent
- [ ] L2/-1 (SERVO_V) - L3/-1 (5V2): silent
- [ ] L2/-2 (SERVO_V) - L3/-2 (GND): silent
- [ ] L2/8 (GND) - L2/9 (VBAT): silent
- [ ] L3/-1 (5V2) - L3/-2 (GND): silent
- [ ] L3/12 (DIN_F) - L3/13 (DIN_R): silent
- [ ] L3/2 (UNO5V) - L3/3 (M1): silent
- [ ] L3/3 (M1) - L3/4 (M2): silent
- [ ] L3/5 (M2) - P3/5 (GND): silent
- [ ] L3/6 (M1) - P3/6 (5V2): silent
- [ ] P3/-1 (5V2) - P3/-2 (GND): silent
- [ ] P3/10 (KEY) - P4/10 (5V2): silent
- [ ] P3/12 (DIN_F) - P3/13 (DIN_R): silent
- [ ] P3/12 (DIN_F) - P4/12 (5V2): silent
- [ ] P3/13 (DIN_R) - P4/13 (5V2): silent
- [ ] P3/3 (M1) - P3/4 (M2): silent
- [ ] P3/4 (M2) - P3/5 (GND): silent
- [ ] P3/5 (GND) - P3/6 (5V2): silent
- [ ] P4/5 (GND) - P4/6 (5V2): silent

## Check results

- PASS 1 refs: every hole and PART.PIN reference exists
- PASS 2 one-lead: 61 lead-used holes, none shared
- PASS 3 bridges: 22 bridge(s), all adjacent and unique
- PASS 4 bodies: 11 body(ies), no foreign lead inside, no overlap
- PASS 5 connectivity: 17 net(s) each in one component, none shorted
- PASS 6 steps: 9 step(s), every hole token exists
