# hardware.md — Autonomous Car Project

**Split out of `gotchas.md` on 2026-09-02** (Appendix BO), which had reached
423 lines, 2.8x the ~150 cap. Physical-build traps: printing and Lego fit,
power, motors and drivers, the Arduino Uno, and measured vehicle geometry.

Entries dated 2026-07-23 come from the research brief
(`docs/research/2026-07-23_sensor-compute-stack.md`) and are **DESK RESEARCH,
not yet verified on this car.** Mark them verified when a build task confirms.

Track and marking traps are in `track.md`; simulator and training-harness
traps in `sim-harness.md`.

- FDM tolerances don't match Lego injection molding — print test coupons for
  pin holes/axle bores and tune per-printer before any chassis print
  (2026-07-23). Community starting points: **~5.1mm pin fit, 5.3-5.6mm
  free-rotating axle bore** vs Ø4.8mm nominal; beam pitch 8mm. (inferred
  from published test boards, unverified on Evan's printer)
- **PETG (not PLA) for rotating bores** against Lego axles — PLA galls/wears
  (LDraw forum guidance, 2026-07-23). PLA fine for static holes.
- Plain Lego motors have no position feedback — never use one for steering;
  hobby servo drives the Lego steering rack (2026-07-23).
- **Never drive Powered Up / Control+ motors (88013/88014) from a raw
  H-bridge** — you lose their built-in 1° encoder and fight their thermistor
  current limiting. PF motors → TB6612FNG; PU motors → Pi Build HAT.
  Mutually exclusive per motor (2026-07-23).
- **L298N banned** on this project: 1.4-3V drop across its BJT output stage
  wastes ~20% of a 9V rail as heat. TB6612FNG (~0.5V drop) is the pick
  (2026-07-23).
- ~~**Pi 5 will not get 5V/5A from standard USB-PD** … Battery path is 2S
  LiPo → 5V/5A-class UBEC → 5V GPIO pins … Never a phone power bank.~~
  **(supersedes the 2026-07-23 ~16:17 entry — the CONSEQUENCE was wrong.)**
  Corrected 2026-07-23 ~17:59 (verified verbatim against official docs):
  the Pi 5 accepts **"5 V at 3 A (15 W) with a 600 mA peripheral limit"**.
  The 5 A rating is a **USB-peripheral budget, not a board requirement**,
  and the only documented consequence of a 3 A supply is that USB cap —
  **irrelevant here, since this build has no USB peripherals** (CSI camera
  only). Measured Pi 5 draw under CNN inference is **1.40 A**; all-core
  stress ~1.76 A. A USB power bank IS viable for the Pi.
- **The real Pi 5 power constraint is transient rail stiffness, not
  amperage.** A documented Pi 5 shut down at only ~1.5 A because of voltage
  drop in "5 A-rated" cables, and another got undervoltage warnings through
  a bench-tested 5 A buck due to transients a DC load never catches. Short
  thick cables; bulk capacitance at the Pi end if a regulator is ever in its
  path (2026-07-23).
- **NEVER put the Pi and the motor on one 5V/3A power bank.** Simultaneous
  Pi peak (2.32 A) + servo stall (0.70 A) + motor stall (1.6 A) = **4.62 A
  on a 3 A rail** → current limit, rail collapse, Pi hard-reset mid-run with
  the SD card mounted. Average draw (~2 A) is fine; the stall event is the
  killer. Split source is the design: bank → Pi only; 2S pack → motor +
  servo; **one shared ground**, star-grounded at the driver (2026-07-23).
- **Don't set `PSU_MAX_CURRENT=5000`** on this build — with no USB
  peripherals it enables nothing and only removes a brownout guardrail
  (2026-07-23).
- **MPU6050 is EOL** (TDK discontinued, counterfeit-prone modules). If an IMU
  enters at M4: ICM-20948 ($20, raw) or BNO055 ($35, on-chip fusion)
  (2026-07-23).
- DonkeyCar 5.x requires **64-bit Raspberry Pi OS Bookworm + Python 3.11**;
  its trainer is TensorFlow/Keras, not PyTorch (2026-07-23).
- Pi 5 prices are volatile (LPDDR4 shortage; two hikes in three months as of
  2026) — re-verify at purchase time, don't trust the brief's numbers blind.
- **Camera Module 3 ships with the WRONG cable for a Pi 5** (verified
  against Raspberry Pi docs 2026-07-23). The Pi 5 uses the **mini 22-pin**
  connector; the module includes a Standard-Standard cable. A **Standard-
  Mini** cable must be bought separately or the camera cannot be connected
  at all. It is in `docs/BOM.md`.
- **Evan owns NO Lego motors** (confirmed 2026-07-23). Any doc or reasoning
  that assumes a free reused Power Functions motor is stale — the drive
  motor must be bought (PRD M1.1b) and its dimensions gate the rear-module
  CAD.
- **Lego motors: rejected, but be precise about WHY — the bin used to overstate
  its own source.** (Corrected 2026-09-02, Appendix BR.)
  `docs/research/2026-07-23_drive-motor-selection.md` measures best-case Lego
  through any diff arrangement as **PF M 0.88 / PF L 0.84 / PF XL 0.50 m/s**,
  all under the 1.0 m/s floor. **But the same doc says a 20t->8t step-up
  layshaft brings PF M to 0.92-1.74 m/s and calls that "workable."** So after a
  step-up it is NOT rejected on physics — it is rejected on two extra gears, an
  extra layshaft, more rear-module volume, and used-part cost (PF M ~$19 used /
  ~$28 new, i.e. no cheaper than a new fully-spec'd N20). The old wording
  ("rejected on physics, not price" / "Don't helpfully re-propose a Lego motor")
  was stronger than the evidence.
- **THE BINDING CONSTRAINT IS NOW THE ENCODER, NOT SPEED** (2026-09-02, and this
  did not exist when the motor was chosen). `ticks` from #5159's 12 CPR encoder
  is the car's ONLY odometry: D2/D3 are spent on its interrupts, the protocol
  reply frame carries it in bytes 2-5, and `uno_control` decodes it. **No Lego PF
  motor has an encoder at all.** Powered Up motors do, but reaching them needs
  the Build HAT, rejected on four independent grounds (8V +/-10% vs a 6.4-8.4 V
  2S pack; takes GPIO 0/1/4/14/15/16/17 incl. the primary UART; no Trixie
  support; $65). **Switching to a Lego motor now also costs the odometry.**
- **Geekservo is the genuinely Lego-mountable motor, and it is far too slow.**
  70 rpm (standard) / 90 rpm at 3 V (2kg version), vs the N20's 1000 rpm and the
  already-rejected PF M's 400 rpm — roughly 4-6x slower than the slowest option
  already ruled out. Torque ~500 g.cm (~49 mN.m) is comparable to the N20's
  55.9 mN.m stall, but at a small fraction of the speed. No encoder either.
  (Checked 2026-09-02: RobotShop / Pimoroni / Kittenbot listings.)
- **Pololu #1011 is discontinued AND was never the right part**: it adapts 3mm
  HEXAGONAL shafts to LEGO WHEEL hubs, not to a Technic CROSS AXLE, so it could
  never have driven through the differential. Verified 2026-09-02.
- **Lego gears are metric module 1** ⇒ pitch diameter (mm) = tooth count.
  Mesh centres: 12t→28t = **20.0 mm (2.5 studs)**; 20t→28t = **24.0 mm
  (3.0 studs)**. Diff 62821 = 28-tooth ring; 6573 = 24/16. Lego tire part
  names state real OD × width in mm (44309 = 43.2 × 22; 32019 = 62.4 × 20)
  (2026-07-23).
- **Only the 30:1 N20 ratio works.** N20 speeds jump 1000 → 2000 rpm with
  nothing between; 15:1 and 10:1 fail the acceleration check (112% and
  132-153% of stall), 50:1 tops out below 0.9 m/s, and the low-current
  **30:1 MP variant fails at 101.8% of stall** — which is why the 1.6 A HP
  variant is forced (2026-07-23).
- **Parallel BOTH TB6612FNG channels** (AIN1+BIN1, AIN2+BIN2, AO1+BO1,
  AO2+BO2) for 2 A continuous — steering is a servo, so the second channel
  is free. Also **PWM-cap duty at ~71%** of a full 8.4V pack so the 6V motor
  sees ≤6V, and add a firmware stall-timeout (2026-07-23).
- **The printed motor coupler is the LOWEST-torque joint, not the highest**
  (corrects the 2026-07-23 ~16:17 brief's premise). It sits upstream of the
  reduction: motor stall 55.9 mN·m vs ~45.6 mN·m per half-shaft downstream
  of a 2.333:1 diff. Still, print it as a **socket gripping a real Lego
  axle, never as a printed axle cross-profile** — a printed cross stub is
  only SF 2-4 in torsion at stall, collapsing toward 1 with sparse infill
  (2026-07-23).
- **Raspberry Pi Build HAT is rejected** (2026-07-23, both facts verified
  directly): it needs **8V ±10% (7.2-8.8V) at 48W via a barrel jack** — a
  2S pack is below that for most of its discharge — and it reserves **GPIO
  0/1/4/14/15/16/17** including the primary UART. It is also **not
  supported on Raspberry Pi OS Trixie** (official docs say stay on
  Bookworm), and no rpm/torque data is published for Lego 88013/88014
  anywhere, so their gearing can't be designed on paper.
- **Evan owns NO battery and NO charger** (confirmed 2026-07-23 ~17:32 CDT).
  The 2S-LiPo plan assumed equipment that doesn't exist; the complete power
  system (cells + charger + connectors) is an unbudgeted purchase and is
  under research as PRD M1.1c. Budget is projected over the $200 ceiling as
  a result.
- **Steering is a SERVO, never a plain DC motor** (restated 2026-07-23
  ~17:32 CDT after the "2 motors" framing came up). A servo takes a
  commanded ANGLE; a bare DC motor only takes a direction, so steering
  position would be unknown. The M3 behavioral-cloning model and every M4
  policy emit a steering angle — a plain motor gives that output nothing to
  command. The car has two actuators: drive motor + MG90S servo.
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
- **Do not power the Uno from the 7.4V pack's VIN.** The pack sags under motor
  stall; if VIN falls below ~7V the AMS1117 regulator drops out and the Uno
  browns out MID-DRIVE, taking the servo and the watchdog with it. Feed its 5V
  pin from the LM2596 rail and use a **data-only USB cable** (5V wire cut) so
  the two supplies cannot back-feed each other.
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
- **The 2S pack has no HARDWARE over-discharge protection** (Appendix BI). BOM
  row 11's "BMS" documents over-voltage and short-circuit only, and the EVE
  cells are bare. `firmware/uno_packguard/` implements a latched firmware cutoff
  (warn 6.4 V, cut 6.0 V held 500 ms, fault outside 4.0-8.8 V, CLEAR needs
  6.8 V) - **but firmware cannot guard a pack while the firmware is off.** It
  supplements a protection board; it does not replace one.
- **Measure the pack against the internal 1.1 V band gap, never the 5 V rail.**
  The Uno's 5 V comes from the LM2596 - the same supply that sags when the pack
  sags - so a rail-referenced reading lies exactly when it matters.
- ⚠️ **CAR WIDTH SUPERSEDED 2026-09-03: rear track is now 148.25 mm** (Appendix CH) — Evan fitted NEW REAR WHEELS and measured outside-to-outside. **+33.5 mm, the third value in two days**, so treat it as provisional until the chassis exists. Lane 296.5 mm, track v2 spare 103.5 mm. **FRONT TRACK IS NOW UNKNOWN** — 107.75 mm was measured against the OLD wheels, and the governing width is the widest point. The 2026-09-02 entry below is kept for its reasoning:
- ~~**CAR WIDTH IS MEASURED: 114.75 mm.**~~ Evan built the Lego rack-and-pinion
  steering and measured tire track: **front 107.75 mm, rear 114.75 mm, both at
  the widest point.** This **supersedes the 130 mm ESTIMATE** that every track
  document has been drawn against since Appendix L. The car is **15.25 mm
  narrower than assumed (11.7%)**.
  - **Lane width follows the measured number**: `SIM_TRANSFER_SPEC` §3's rule is
    lane = 2.0 x measured car width, so **229.5 mm**, not 260 mm.
  - **Track v2 gains span: MEASURED 171 mm, not the ~201 mm first estimated.**
    Re-ran `cad/track_layout_v2.py` 2026-09-02 (Appendix BO): lane 260 -> 230 mm,
    span 2660 -> 2629 mm, **spare 140 -> 171 mm**, tiles 79 -> 73 (~902 g).
  - **The "40 mm of span per 10 mm of car width" rule of thumb is WRONG for
    this geometry - do not use it.** (From **Appendix AZ**, 2026-09-01; an
    earlier note here wrongly credited HANDOFF - corrected in Appendix BP.)
    `best_straight` is **capped at MAX_STRAIGHT = 200 mm**, and the uncapped
    value exceeds that cap at BOTH widths, so **pitch does not move at all**;
    span then changes by exactly the lane delta. **Real sensitivity is 2x the
    car-width change, not 4x**, while the straight stays capped. The runnable,
    self-checking generator is the authority; a rule of thumb is not.
  - **CAVEAT, not yet closed: this is TIRE track, not whole-vehicle width.**
    Lane width must key off the widest point of the assembled car including
    chassis, electronics stack and any camera mount. Confirm nothing exceeds
    114.75 mm before freezing lane width.
  - **Rear is 7.0 mm wider than front.** Normal cars cut the rear wheels
    *inside* the front path in a corner; a wider rear track partly cancels
    that, so swept corner width is set by front-outer and rear-outer together.
    A T2 detail, not a today detail - noted so it is not rediscovered.

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
  per channel independently. **Run the LEDs at 10 mA**: 20 mA/pin in spec,
  80 mA chip total. No MOSFETs needed.
- **Encoder `Vcc` (Pololu #5159) must come off the 5 V rail, NEVER the 7.4 V
  pack.** The encoder accepts 2.7-18 V, so the pack "works" - and then swings
  its outputs to 7.4 V into the Uno's 5 V-max inputs. Outputs already carry
  internal 10k pull-ups to `Vcc`; no external pull-ups.
- **`BOM.md` row 5 buys the WRONG MOTOR** as of 2026-09-02: it lists #1093
  ($23.95, no encoder) while the record has Evan choosing **#5159** ($29.95,
  12 CPR) on 2026-08-12, and D2/D3 are already spent on encoder interrupts.
  Unresolved - it moves the total, so it is Evan's call.

- **STEERING PINION IS 12 TEETH** (Evan, 2026-09-02). **LEGO gear pitch rule,
  verified not recalled: 16 teeth per stud of pitch radius, stud = 8 mm, so
  pitch radius = N/2 mm**; the same sources state the system is metric module 1,
  which says the same thing independently. So a 12t pinion has pitch radius
  6.00 mm, pitch diameter 12.00 mm, and **rack travel = 37.70 mm per full
  pinion revolution**. Cross-checked two ways: pi x 12.00 mm, and 12 teeth x
  the module-1 tooth pitch of 3.1416 mm. Both give 37.70 mm.
  - At a nominal MG90S 180 deg (1:1 to the pinion) that is **+/-9.42 mm** of
    rack travel from centre; at 120 deg, **+/-6.28 mm**. *Servo travel is a
    nominal spec and depends on the pulse range - bracketing, not an answer.*
  - **Confirms the protocol's int8 steering**: 200 steps over +/-9.42 mm is
    0.094 mm/step, far finer than the mechanism resolves. int16 stays unneeded.
  - **Does NOT give max steer angle** - that needs the steering arm length, and
    the LEGO hard stops may bind before the servo does. **Turn radius is still
    an estimate**, but it is now short exactly two bench-measurable numbers:
    **wheelbase** and **max road-wheel angle at the rack's hard stop**. That
    would be a GEOMETRIC radius; PRD **T2 still wants the EMPIRICAL** test on
    the rolling chassis.

## Vehicle width FULLY measured (2026-09-03, Appendix CI)

Three numbers, and the governing one is unchanged:

| | mm | note |
|---|---|---|
| front track | **107.5** | outside-to-outside. The new rear wheels did NOT change it (was 107.75) |
| **rear track** | **148.25** | **WIDEST — governs lane width** |
| body | **135.75** | narrower than the rear track |

- **148.25 mm is now a WHOLE-VEHICLE width, not just tire track.** The caveat
  every prior entry carried ("tire track, not whole-vehicle") is CLOSED: the body
  measures 135.75 mm, 12.5 mm narrower than the rear track, so **the rear wheels
  are the widest point and stand 6.25 mm proud of the body per side.**
- **Lane width, span and spare are UNCHANGED** — 296.5 mm / 2696.5 mm / 103.5 mm.
  The measurement confirmed the number rather than moving it.
- ⚠️ **The front track is only 72.5% of the rear — a 40.75 mm difference.** That
  is a large split and it was never a design decision anyone recorded; it fell
  out of which Lego parts were used. Two consequences to carry into T2:
  - **Swept width in a corner is set by the rear outer wheel**, not the front.
    The usual assumption that rear wheels cut INSIDE the front path does not
    hold when the rear track is 40 mm wider.
  - The front wheels sit **28.25 mm inside the body**, so the body — not the
    front tyres — is what a kerb or a track edge will contact at the front.
- **Nothing here is a chassis decision yet.** These are donor-part measurements;
  the printed frame does not exist.
