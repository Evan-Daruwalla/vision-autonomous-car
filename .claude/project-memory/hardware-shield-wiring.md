# hardware-shield-wiring.md - proto shield, wiring, pins, Uno pin budget, connectors, driver wiring, lighting strips (split from hardware.md on 2026-10-29)
Moved verbatim from hardware.md, original relative order; router is hardware.md. Entries dated 2026-07-23 are desk research unless marked verified.
Cross-topic facts live in the file that fit best; check the sibling hardware-*.md files too.

- **Never drive Powered Up / Control+ motors (88013/88014) from a raw
  H-bridge** — you lose their built-in 1° encoder and fight their thermistor
  current limiting. PF motors → TB6612FNG; PU motors → Pi Build HAT.
  Mutually exclusive per motor (2026-07-23).
- **L298N banned** on this project: 1.4-3V drop across its BJT output stage
  wastes ~20% of a 9V rail as heat. TB6612FNG (~0.5V drop) is the pick
  (2026-07-23).
- **Steering is a SERVO, never a plain DC motor** (restated 2026-07-23
  ~17:32 CDT after the "2 motors" framing came up). A servo takes a
  commanded ANGLE; a bare DC motor only takes a direction, so steering
  position would be unknown. The M3 behavioral-cloning model and every M4
  policy emit a steering angle — a plain motor gives that output nothing to
  command. The car has two actuators: drive motor + ~~MG90S~~ MG90D-270 servo (swapped 2026-09-05, Appendix DP).
- **The Pi 5's GPIO is 3.3V and NOT 5V tolerant; this Uno clone is a 5V board.**
  Wiring its TX straight to a Pi RX pin can damage the Pi. **Connect over USB**,
  which sidesteps level shifting entirely. This is the single hardware-
  destroying mistake available in this build.
- **It is an FTDI FT232RL board, not a CH340** (verified 2026-09-02 from the USB
  IDs: `VID_0403&PID_6001`, serial `A5069RR4`, enumerating OK as COM3). The
  driver is already installed; nothing to install. Identifying it from the chip
  package in a photo gave the WRONG answer — the USB vendor/product ID is
  authoritative, the silkscreen and package outline are not.
- **FTDI has twice shipped Windows drivers that disable COUNTERFEIT FT232RL
  chips** — the 2014 driver bricked them by zeroing the USB PID, a later one
  made them transmit `NON GENUINE DEVICE FOUND` instead of data. Clone Unos are
  where counterfeit FT232RLs live, and genuine-vs-fake is not determinable from
  here. **If COM3 dies or the board starts sending garbage after a Windows
  update, that is the cause — not your wiring or firmware.** The fix is rolling
  back the FTDI driver.
- **The Servo library claims Timer1**, which kills `analogWrite` on pins 9 and
  10. Usable PWM after that: 3, 5, 6, 11. Discovering this after wiring the
  board is how a "dead" LED channel gets misdiagnosed as a bad solder joint.
- **And D3 is NOT available either** (2026-09-02): the quadrature encoder needs both external interrupts, INT0 on D2 and INT1 on D3. So usable PWM is **{5, 6, 11}, not {3, 5, 6, 11}** — three pins for motor + headlights + tail, **zero spare**. The earlier "3, 5, 6, 11" line above is the pre-encoder count.
- **Pins 5 and 6 share Timer0 with `millis()`.** `analogWrite` works there, but
  changing their PWM frequency breaks timekeeping — so the watchdog and the
  dimming cannot both be tuned freely on those pins.
- **An Uno on USB makes the power brief's "zero USB peripherals" claim FALSE**
  (`docs/research/2026-07-23_power-system.md`). The board is ~50mA, but if it
  sources LED current from its pins that is up to 160mA on the Pi's 5V/3A bank
  with its 600mA peripheral cap — the exact thing `LIGHTING_SPEC` §3 avoids.
  **The Uno supplies logic; LED current comes off the LM2596 rail.**
- **LIGHTING ARCHITECTURE CHANGED 2026-09-03: WS2812B addressable RGB strip,
  not 8 discrete 3mm LEDs.** Evan's call — "much easier to wire and mount" —
  and it is, plus a real bonus: the old scheme spent the car's last 3 free
  PWM pins with zero spare (`docs/PRD_ROADMAP.md` line ~415); WS2812B needs
  no PWM hardware at all, freeing 2 of those 3. ⚠️ **CORRECTED same day
  (Evan): "the led strip only moves data 1 way."** DIN→DOUT only — cutting
  one reel into 2 segments does NOT let them share a data feed; each cut
  end needs its own pin. **Two digital pins, one per segment** (not one),
  still non-PWM so the 2-freed-pins count is unchanged either way.
  Daisy-chaining (a jumper from segment A's DOUT to segment B's DIN) would
  get to one pin but adds a chassis-spanning wire and a DIN/DOUT mix-up
  risk — two independent pins is simpler. LM2596 headroom
  checked: module rated 3A (Addicore listing, closing a gap
  `WIRING_PROTOSHIELD.md` had flagged as unverified), existing peak load
  840mA. **Both open figures quantified 2026-09-03** (were qualitative —
  "well under that" / "can drop ticks"), under stated assumptions (3
  pixels/segment: 1 white front + 1 red rear + 1 amber indicator per
  side; indicators blink at the firmware's existing `BLINK_MS`=340ms;
  brightness scaled to the old scheme's established "plainly bright"
  10mA/LED target — Appendix BO):
  - **Current draw: ~80mA realistic, 360mA absolute worst case** (6
    pixels, full white, 100% brightness, never actually commanded).
    Either way the LM2596's 3A rating keeps **1.8–2.1A of margin**.
    **2026-10-04: that 3 A was the Addicore part, which was backordered. Its
    substitute (EPLZON `B09R49R76K`, BOM row 12) is rated 2 A, so the margin
    at the same 0.92-1.20 A peak is 0.80-1.08 A - still positive, smaller.**
  - **Encoder tick loss: ~0.027% of ticks, ~1 in 3800, ~1.1 ticks/sec**
    — worst case, continuous indicator blink at the no-load top speed
    (Appendix CS), for ONE segment write. `applyLights()` writes both
    strips per call, so the real worst case is roughly double this —
    stated in Appendix DC, not yet corrected here in the source figure.
  ⚠️ **PIXEL LAYOUT AND FIRMWARE DECISIONS NOW RESOLVED (Evan, 2026-09-03,
  Appendix DC) — the "still open" language below is HISTORICAL.** 3
  pixels/segment was already settled by Appendix DA's cut-spacing math, not
  just assumed; DRL folds into the HEAD pixel only, never the tail.
  `firmware/uno_control/uno_control.ino`'s `applyLights()` is rewritten for
  two `Adafruit_NeoPixel` objects on D4/D7, compiled clean (9680 B flash /
  371 B SRAM) — **compiled only, NOT flashed, NOT run on real hardware; no
  strip is owned.** The do-not-flash banner from Appendix DB is gone (the
  stale code it warned about no longer exists), but "compiled" and
  "hardware-verified" are still two different claims. `docs/LIGHTING_SPEC.md`
  was brought current in the same pass — no longer the stale doc.
- **2KB of SRAM.** Fine for a command loop and encoder counters; it will hold no
  model, no buffer of frames, and no meaningful history. Nothing ML goes here.
- **The device signature is AMBIGUOUS and the two ways of reading it DISAGREE
  (measured 2026-09-02).** avrdude reports `1E 95 0F` and itself names three
  candidate parts: `ATmega328P, ATA6614Q, LGT8F328P`. But reading the silicon's
  own signature row in-app (`boot_signature_byte_get`) returns **`1E 95 16`,
  which is ATmega328PB.** The in-app read is the more direct evidence:
  **optiboot HARDCODES the signature it reports over STK500**, so avrdude is
  quoting the bootloader's build-time constant, not the chip. Treat the part as
  "328P-family, probably a PB" and do not rely on PB-only peripherals.
- **`F_CPU` is a BUILD constant, not a measurement.** It proves nothing about
  the silicon. The clock was measured separately at **16.0042 MHz (+0.026%)** by
  timestamping serial beacons on the host — which rules out an LGT8F328P at
  32 MHz (would read ~2.0x) and the internal 8 MHz RC (~0.5x).
- **Opening the serial port RESETS the board.** Any timing comparison must
  timestamp on the host and use DELTAS; comparing board uptime to a host
  stopwatch started later gives a nonsense ratio (0.54x was measured this way
  before the reset was understood).
- **SRAM measured at 2048 bytes** (`RAMEND 0x8FF`; 1472 B obtained by malloc in
  46x32 B blocks; 1705 B free with a small sketch loaded). Confirms the 2KB
  figure rather than assuming it — and confirms nothing ML fits.
- **A floating analog pin reads NEAR FULL SCALE, not zero** (measured 2026-09-02:
  10238-10266 mV on a 100k/12k divider input with nothing connected, against a
  10.27 V ceiling). A sensor guard that only rejects implausibly LOW readings
  therefore treats an **unwired sensor as a healthy one**. `uno_packguard`'s
  first build did exactly that and would have allowed throttle with no divider
  attached. **Any analog guard needs an upper implausibility band too.**
- **`STBY` is pulled LOW internally - an unwired `STBY` is a DEAD MOTOR, not a
  degraded one.** Pololu #713: *"pulled low internally ... must be driven high
  (2.7 V - 5.5 V) in order to enable the driver."* It was missing from BOTH the
  pin map and `BOM.md` until 2026-09-02; now **D10**. Presents as a mystery
  bring-up failure with perfectly correct PWM on a scope.
- **`analogWrite(pin, 0)` on the TB6612 with a direction set is a SHORT BRAKE,
  not a coast** (Toshiba truth table: DIR set + PWM low = short brake). So "cut
  throttle to zero" already stops the car actively. **`STBY` low is the coast**
  - high-Z outputs, car keeps rolling. `STBY` is a *disable*, never the stop
  action: brake first, then drop `STBY`.
- **ATmega328P has TWO current limits and the per-pin one is the binding one
  here.** 200 mA is the all-I/O absolute max; **40 mA is the per-pin absolute
  max, 20 mA the recommended figure.** `LIGHTING_SPEC.md` checked only the
  chip total (8 x 20 mA = 160 mA, "80% of the limit") and missed that its 4
  channels each drive **2** LEDs, i.e. **40 mA per pin** - the absolute maximum.
  The per-channel reasoning was inherited from the PCA9685, which sank 25 mA
  per channel independently. ~~**Run the LEDs at 10 mA**~~ (SUPERSEDED 2026-09-03: no LED current passes through a pin since the WS2812B swap, Appendix CX - the reasoning lesson stands): 20 mA/pin in spec,
  80 mA chip total. No MOSFETs needed.
- **Encoder `Vcc` (Pololu #5159) must come off the 5 V rail, NEVER the 7.4 V
  pack.** The encoder accepts 2.7-18 V, so the pack "works" - and then swings
  its outputs to 7.4 V into the Uno's 5 V-max inputs. Outputs already carry
  internal 10k pull-ups to `Vcc`; no external pull-ups.
- ~~**`BOM.md` row 5 buys the WRONG MOTOR** as of 2026-09-02: it lists #1093
  ($23.95, no encoder) while the record has Evan choosing **#5159** ($29.95,
  12 CPR) on 2026-08-12, and D2/D3 are already spent on encoder interrupts.
  Unresolved - it moves the total, so it is Evan's call.~~
  **RESOLVED THE SAME DAY (2026-09-02, Appendix BO)** - row 5 now reads #5159
  and a new row 5b adds the #4763 JST SH cable Pololu does not include. Struck
  2026-09-09 (daily-audit finding 10): it had sat here reading like a live
  defect for a week after being fixed.

- 2026-10-16 (records JM-JS): the Uno is flashed FROM THE PI: IDE "Export Compiled Binary" on the PC -> scp the .ino.hex -> `avrdude -p atmega328p -c arduino -P /dev/ttyUSB0 -b 115200 -D -U flash:w:<hex>:i` (clone FT232R = /dev/ttyUSB0; python3-serial + avrdude from apt). Servo V+ DECIDED on the Uno 5V header (Evan, JR; JP: serial bytes lost on 2 of 3 big swings) with a 3-pin jumper fallback to `+5V2`. `+5V2` stays 5.0 V (strips + encoder Vcc level with the Uno's USB 5 V).
- 2026-10-20 (records KB-KG): PROTO SHIELD v.5 (silkscreen 2012/7/23), metered by Evan: top rail T and rail V = the 5V header pin; rails G and B = GND, G-B joined; neighbouring short strips separate; NO breakout holes for the Uno pins (wires plug into the shield's own sockets). TB6612 carrier = Pololu md08a: label-side left column PWMA, AIN2, AIN1, STBY, BIN1, BIN2, PWMB, GND; right column GND, VCC, AO1, AO2, BO2, BO1, VMOT, GND; rows 0.5 in apart (fits U2 / L2 of the strip field). 470 uF caps = 25 V, 8 mm x 12.5 mm; 0.1 uF ceramics; NO 1000 uF on hand. Rocker = 2-pin SPST (KC). Deck v13: LM2596 moved +4 mm clear of the lobe boss at (60, -82) that Evan spotted (KB). Hole map: docs/shield_layout.json -> scripts/shield_holemap.py -> docs/shield_holemap.svg + docs/SHIELD_BUILD.md.
- 2026-10-21/22 (records KK-KX): proto shield doc facts. C1 (470 uF 25 V, 8 x 12.5 mm) now STANDS UPRIGHT on the carrier's VMOT/GND2 tips (Evan; build step 1 changed, KQ), top ~18.8 mm above the shield - headroom over the Uno NOT checked; C2 0.1 uF on the same tips, may be soldered across C1's legs at the tips. Strips are named by SIDE like the firmware: J3 = LEFT strip (D4), J4 = RIGHT strip (D7), nets DIN_L / DIN_R (KX; was front/rear). JP1 cap on the TOP two pins = servo on the Uno 5V; on the bottom two = +5V2. Socket arrows: digital pins go to the TOP header, A0 to the bottom (4 of 8 arrows were drawn wrong until KK). Underside bridges are drawn as seen through the board - flip top-over-bottom (USB stays left). Isolated pads (left field, rows P1-P4, cols 11-13) do not conduct to each other (Evan confirmed); only the strips and rails T, G, V, B do.
- 2026-10-22..24 (records LB, LC): proto shield SOLDERED by Evan, UNTESTED (no meter checks, no power). Photo review vs shield_layout.json: every bridge present except L1/-2-L1/-3; L2/9-L2/10 was missing and has been added. C1 is attached at the VMOT/GND2 tips but hangs off the board edge on ~25 mm bare legs (re-seat upright or sleeve + glue; stripe to GND2). Servo signal: the D9 jumper (female-male) sits on J2's SIG pin, so the servo plug has no home - fix = pin at L1/-3 + bridge, or bench: 3 jumpers from the servo plug (signal male-male to D9; V, GND male-female to J2 middle/bottom). Extra solder on unused holes (P2/9, U2/11) is harmless only while nothing else is in them; a blob at the bottom of strip col 10 may touch U3/11 (unused) - meter it if U3/11 is ever used.
- **2026-10-31 (record MC; CORRECTED in MD: as built = servo D7, left strip D6, right strip D5 - no clashes, only firmware pin constants differ; re-plug to D9/D4/D7 recommended):** ~~servo L1/-2 -> D6 (design D9; works, needs wire move or PIN_SERVO=6), left strip L3/12 -> D2 (design D4; CLASH with encoder A / INT0), right strip L3/13 -> D1 (design D7; CLASH with serial TX to the Pi). Recommended: move strips to D4/D7, servo to D9.~~ Test card section C and docs/shield_bottom_grid.jpg show the DESIGN pins. Also: the board has more holes in cols -9..-4 than the layout grid lists (unused).
