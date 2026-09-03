# steering.md — Autonomous Car Project

**Split out of `hardware.md` on 2026-09-03** (Appendix CH). Everything about
getting a commanded angle to the road wheels: the servo choice, the measured
rack-and-pinion geometry, the coupler that has to survive it, and calibration.

⚠️ **The two facts most easily got wrong are both here**: max steer is the
wheel's DEVIATION from straight ahead (32°, not a 58° protractor reading — a
2.6× error in turn radius), and a PRINTED cross-axle stub FAILS as the
servo-to-pinion coupler.

## Steering actuator + the servo-to-pinion coupling (added 2026-09-02, Appendix BS)

- **THE SERVO-TO-PINION COUPLING IS SPECIFIED NOWHERE.** `BOM.md` row 7 is
  "MG90S metal-gear servo | Steering"; `WIRING_PROTOSHIELD.md` §2.4 covers only
  its three wires. **Nothing says how a splined servo horn reaches the 12-tooth
  Lego pinion.** Same defect class as the missing TB6612 `STBY` (Appendix BL),
  on the mechanical side: an unclosed interface that stops the build dead.
- **For STEERING, "Lego-mountable" is worth far more than it is for drive** —
  the speed objection that kills Geekservo as a drive motor (70-90 rpm) does not
  apply, because a steering servo needs position accuracy and torque, not rpm.
  **Do not carry the drive-motor rejection across to steering; it does not
  transfer.**
- **Geekservo 270° (Kittenbot) vs MG90S**, checked 2026-09-02:

  | | MG90S | Geekservo 270° |
  |---|---|---|
  | stall torque | ~2.2 kg.cm @4.8V | **0.9 kg.cm @4.8V, 1.0 @6.0V** |
  | rack force via the 6.0 mm pitch radius | **36.0 N** | **14.7-16.4 N** |
  | travel at 1:1 to the pinion | 180° = **+/-9.42 mm** | 270° = **+/-14.14 mm** |
  | speed | 60°/0.10s | 60°/0.12s |
  | Lego mount + cross axle | **no — needs an adapter** | **yes, native** |
  | clutch | no | **built in** |
  | gears | metal (the reason it was chosen) | **NOT STATED in any listing seen** |

  So Geekservo trades **2.4x less torque** for a native Lego cross axle, **50%
  more rack travel**, and a clutch. **Whether 14.7 N of rack force is enough is
  NOT computable here** — it needs the car's mass and front axle load, neither
  measured. Do not treat it as a drop-in swap; treat it as a candidate to test.
- **The clutch matters more than it looks.** `uno_control` warns that driving
  into the Lego rack's hard stop stalls and cooks the servo; the MG90S has no
  protection and `SERVO_US_SPAN` is deliberately narrowed to 300 us because of
  it. A built-in clutch is a mechanical answer to a problem currently handled
  by a guessed software limit.
- **Manufactured servo-to-Lego adapter, if the MG90S is kept: Adafruit #4252,
  $0.75**, micro-servo spline to a 16 mm Lego cross axle. ⚠️ Adafruit's own
  wording: *"fits our Micro Servo only! Not guaranteed to fit with any other
  kind of servo splines."* Their micro servo is SG90-class; the MG90S usually
  shares that spline but the vendor will not guarantee it. **It is also plastic,
  sitting at the highest-torque point of the steering path.** Verify the spline
  before buying. Printed alternatives already known: Printables 61922 / 147626
  (`docs/research/2026-07-23_sensor-compute-stack.md` lines 132, 255).
- **Firmware impact of a 270° servo:** `SERVO_US_CENTRE`/`SERVO_US_SPAN` in
  `uno_control.ino` are calibrated for a 180° part and are already marked
  provisional. A 270° servo needs them re-derived, not just re-tuned.

## Steering geometry MEASURED, and it inverts the 270-degree argument (2026-09-02, Appendix BU)

- **THE PINION SWEEPS ~180 DEGREES FULL-LEFT TO FULL-RIGHT** (Evan, 2026-09-02).
  Centre-to-full-lock is therefore **90 degrees**.
- **An MG90S at 180 degrees is an EXACT 1:1 match to this rack — no gearing, no
  reduction, nothing.** That is a strong point in its favour that was not known
  when the servo was chosen.
- **A 270-degree servo now OVERTRAVELS by 90 degrees.** `track.md`/Appendix BS
  listed "50% more rack travel" as a Geekservo ADVANTAGE. **That was wrong** —
  travel beyond what the mechanism has is not headroom, it is a way to drive
  into the Lego hard stops. Its built-in clutch mitigates the damage, but you
  would use only the middle 180 of its 270 degrees, **throwing away a third of
  the positional resolution** across the steering range. Corrected in BU.
- **Standard hobby servo scaling: 1000-2000 us over 180 degrees = 500 us per
  90 degrees.** So centre-to-lock = **500 us**, the geometric maximum span.
  ⚠️ **MG90S pulse range varies by unit** — some are 500-2400 us for 180 degrees,
  not 1000-2000. **Confirm the real endpoints on the bench before commanding
  full lock.**
- **`SERVO_US_SPAN = 300` was a REAL DEFECT, shipped and flashed 2026-09-02
  before this measurement existed.** It reached 54 of the 90 available degrees
  (**60% of lock**), giving ~19.2 degrees at the road wheel against the measured
  32 — a **turn radius 1.79x LARGER than the mechanism can achieve**. The car
  would have failed corners it is geometrically capable of, with nothing
  indicating why. **Now 450** (81 of 90 degrees, ~28.8 degrees road wheel,
  R = 1.819 x wheelbase), holding 10% margin per side because servo centre and
  rack centre are aligned by hand and that alignment is unmeasured.
- **Two SELFTEST checks now pin this** (`uno_control`, 39/39 on the board): the
  span may not exceed the mechanical lock, and it must reach **>=85% of it**.
  A future narrowing that silently costs turning circle now fails the gate.

| span | pinion from centre | road wheel | R |
|---|---|---|---|
| 300 (old, defective) | 54 deg (60%) | 19.2 deg | 2.872 x wheelbase |
| **450 (current)** | **81 deg (90%)** | **28.8 deg** | **1.819 x wheelbase** |
| 500 (geometric max) | 90 deg (100%) | 32.0 deg | 1.600 x wheelbase |

## Steering coupler + servo calibration (added 2026-09-02, Appendix BV)

- **THE STEERING COUPLER IS THE HIGHEST-TORQUE JOINT ON THE CAR, and a printed
  cross-axle stub FAILS THERE.** Exact inverse of the drive coupler. Scaling the
  drive research's own figure (6.64 MPa at the N20's 55.9 mN.m stall, vs
  ~15-25 MPa PLA interlayer shear):

  | joint | stall torque | stress | SF |
  |---|---|---|---|
  | N20 drive coupler | 55.9 mN.m | 6.64 MPa | 2.26-3.77 |
  | **MG90S steering coupler** | **~216 mN.m** | **26.1 MPa** | **0.57-0.96 FAILS** |
  | MG996R fallback (BOM row 7) | ~1079 mN.m | 128.3 MPa | 0.12-0.19 |

  **Grip a real Lego axle; never print the cross profile here.** And note the
  MG996R fallback is ~5x worse — choosing it makes the coupling problem harder,
  not just the servo stronger.
- **Limiting servo travel is what keeps the COUPLER alive, not just the servo.**
  All the numbers above are STALL. At working torque the coupler is fine. So
  `SERVO_US_SPAN` and any centre calibration are structural, not comfort.
- **A HOBBY SERVO GIVES THE UNO NO POSITION FEEDBACK.** The MG90S's internal pot
  serves its own loop and is not exposed. **The board cannot detect a hard stop**
  — it can only command a pulse width. Any "drive to both locks and find the
  centre" scheme needs a SENSOR (servo current sense on a free analog pin
  A1-A5 + a shunt) or an operator in the loop. It cannot be done with what is
  on the board today.
- **NEVER auto-calibrate on boot.** Opening the serial port RESETS the board, so
  "every boot" means "every time the Pi connects" — the steering would slam into
  both hard stops on every reconnect, at the stall torque that the table above
  shows breaks the coupler. **Calibrate once on an explicit command, store in
  EEPROM (ATmega328P has 1024 B), reload on boot.**
- **MG996R is ~11 kg.cm / ~1079 mN.m** for reference; MG90S ~2.2 kg.cm /
  ~216 mN.m. (Nominal spec figures, not measured on a real unit.)

- **MAX STEER ANGLE = 32 degrees, confirmed by Evan 2026-09-02** (Appendix BQ).
  Reported first as ~45 (eyeball), then 30, then measured at 32. Use 32.
- **THE MEASUREMENT CONVENTION IS LOAD-BEARING — record it or it WILL be
  misread.** Evan measured with **90 degrees = straight ahead on the protractor,
  steering angle = 90 - (protractor reading)**. So 32 is the wheel's DEVIATION
  from straight ahead, which is exactly the delta in `R = wheelbase / tan(delta)`.
  **Getting this backwards is a 2.6x error, not a rounding error:**
  `R = L/tan(32) = 1.600 L` versus `R = L/tan(58) = 0.625 L`. Anyone re-deriving
  the turn radius must confirm which number they are holding.
- **Turn radius is now ONE measurement away.** `R_min = 1.600 x wheelbase`, and
  **wheelbase is unmeasured because the parts do not exist**. For reference the
  standing ~330 mm estimate implies a ~206 mm wheelbase, which is plausible for
  a 114.75 mm-wide car — so the frozen 500-670 mm corner band probably does NOT
  shrink. **Corner geometry stays frozen until T2 measures it empirically on the
  rolling chassis; a geometric radius from wheelbase + 32 degrees would be
  better than today's arithmetic-on-estimates but is still not T2.**
