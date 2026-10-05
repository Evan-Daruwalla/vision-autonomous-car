# steering.md — Autonomous Car Project

**Split out of `hardware.md` on 2026-09-03** (Appendix CH). Everything about
getting a commanded angle to the road wheels: the servo choice, the measured
rack-and-pinion geometry, the coupler that has to survive it, and calibration.

⚠️ **The two facts most easily got wrong are both here.** (1) Max steer is
the wheel's DEVIATION from straight ahead, never a raw protractor reading —
and this number has now changed TWICE, for two different reasons: a
units/convention mixup (2026-09-02, resolved as 32°) and a REAL mechanical
change (2026-09-05: a 13-stud rack replaced the old 7-stud one, genuinely
**58°** now — see the dated section below). **Always confirm which rack a
given number in this file was measured against; do not reuse pre-2026-09-05
figures (32°, the SERVO_US_SPAN table, the pinion-sweep measurement) without
re-checking them against the new rack first.** (2) A PRINTED cross-axle stub
FAILS as the servo-to-pinion coupler.

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
- **Two SELFTEST checks now pin this** (`uno_control`; ~~39/39 on the board~~ -- stale count struck 2026-09-09, SELFTEST count: **read the board's boot banner** -- `uno_control.ino` prints `SELFTEST PASS <pass>/<total>` at runtime and the file's own header forbids quoting a count without having just run it. Last OBSERVED on the board: **49/49, 2026-09-02** (Appendix CA). Current source carries 63 `CHECK()` invocations and **has never been flashed** (Appendix DC, plus the 2026-09-09 ST_DROPPED fix).): the
  span may not exceed the mechanical lock, and it must reach **>=85% of it**.
  A future narrowing that silently costs turning circle now fails the gate.

| span | pinion from centre | road wheel | R |
|---|---|---|---|
| 300 (old, defective) | 54 deg (60%) | 19.2 deg | 2.872 x wheelbase |
| **450 (current)** | **81 deg (90%)** | **28.8 deg** | **1.819 x wheelbase** |
| 500 (geometric max) | 90 deg (100%) | 32.0 deg | 1.600 x wheelbase |

⚠️ **TABLE ABOVE IS SPECIFIC TO THE OLD 7-STUD RACK (measured 2026-09-02) —
NOT re-verified against the 13-stud rack installed 2026-09-05.** Two things
are unknown with the new rack, not just one: whether the pinion still sweeps
~180 deg lock-to-lock (the old rack may have been what stopped it, not the
pinion/servo itself), and whether the wheel-angle-per-pinion-degree ratio
(0.3556 = 32/90 above) still holds. **Do not compute a "new 58 deg row" for
this table by extrapolating the old ratio** — that assumes linearity and an
unchanged pinion range, neither confirmed. `SERVO_US_SPAN = 450`'s 10%
safety margin (`uno_control.ino`) was sized against the OLD rack's hard
stops; it is UNVALIDATED against the new one until the pinion sweep is
re-measured on the bench. Driving anywhere near the old span on the new rack
before that measurement risks the exact stall/cook failure this margin
exists to prevent.

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

- ~~**MAX STEER ANGLE = 32 degrees, confirmed by Evan 2026-09-02** (Appendix BQ).~~
  **SUPERSEDED 2026-09-05 (see dated section below): 58 degrees, on a 13-stud
  rack.** 32° was correct for the 7-stud rack this bullet was measured on; it
  is not a stale/wrong number, it describes different hardware. Reported
  first as ~45 (eyeball), then 30, then measured at 32 (old rack); now 58
  (new rack). **Always state which rack a steering-angle number refers to.**
- **THE MEASUREMENT CONVENTION IS LOAD-BEARING — record it or it WILL be
  misread, and this project has now needed it applied correctly TWICE.**
  Evan measures with **90 degrees = straight ahead on the protractor,
  steering angle = 90 - (protractor reading)**. Old rack: reading 58 -> 32°
  deviation. New rack: reading 32 -> **58° deviation** — note these two
  measurements' raw readings and deviations are each other's complement
  (32+58=90), which is a genuine coincidence of this particular remeasurement,
  not a sign either one is the old convention error repeating. **Getting the
  reading-vs-deviation direction backwards is a 2.6x error either way:**
  `R = L/tan(32) = 1.600 L` versus `R = L/tan(58) = 0.625 L`. Anyone
  re-deriving the turn radius must confirm which number they are holding AND
  which rack it was measured on.
- **Turn radius, 13-stud rack (2026-09-05): `R_min = 0.625 x wheelbase`** —
  ~~`R_min = 1.600 x wheelbase`~~, the 7-stud-rack figure, superseded. Using
  the confirmed wheelbase (185.95 mm, Appendix DD/DE): **R_min = 0.625 x
  185.95 = 116.2 mm** — see the dated section below for the full derivation
  and what is and is not re-verified for the new rack.

## Geekservo 270 CLOSED, wheelbase geometric estimate, coupling status (2026-09-03, Appendix DD)

- **Geekservo 270 REJECTED — Evan keeps the MG90S** ("do the more powerful
  servo"). Closes the comparison table above in the MG90S's favour: 36.0 N
  rack force vs Geekservo's 14.7-16.4 N, at the cost of the native Lego mount
  and clutch. This also closes `HANDOFF.md`'s BLOCKED item 3a (weigh the car
  to arithmetic-check whether 14.7 N is enough) — **moot by decision, not
  answered by measurement**: the car was never weighed, the question no
  longer applies because Geekservo is out.
- **Wheelbase: a GEOMETRIC ESTIMATE, not a direct axle-to-axle measurement.**
  Evan measured **9.25 in (234.95 mm) from the back of the rear wheel to the
  front of the front wheel** — overall wheel-to-wheel length, not wheelbase.
  Wheelbase = overall length − (front radius + rear radius). ~~Same-diameter
  assumption, corrected 2026-09-03 (Appendix DE): front and rear tires do
  NOT match~~ — **front tire 42.25 mm diameter, rear (drive) tire 55.75 mm
  (Appendix CS)**:

      front radius 21.125 + rear radius 27.875 = 49.0 mm
      wheelbase (est.) = 234.95 - 49.0 = 185.95 mm (7.32 in)
      ~~R_min = 1.600 x 185.95 = 297.5 mm~~  -- 7-stud-rack figure, see below

  (Superseded the same-diameter estimate of 179.25 mm / R_min 286.8 mm from
  earlier the same day — that assumption is now known wrong, not just
  unconfirmed. The 297.5 mm R_min above is in turn superseded 2026-09-05 by
  the 13-stud rack, NOT by a wheelbase correction — wheelbase itself is
  unchanged at 185.95 mm.) Still does not unfreeze corner geometry
  (`gotchas.md`/Appendix L): **T2's empirical test on the rolling chassis is
  still the gate.**

## Rack length changed 7-stud to 13-stud: max steer 32° -> 58°, R_min 297.5mm -> 116.2mm (2026-09-05)

- **Evan replaced the 7-stud gear rack with a 13-stud one.** Re-measured
  steering angle with the same protractor convention as before (90° =
  straight ahead): new full-turn reading is 32° (was 58° on the old rack),
  giving deviation **58°** (was 32°). Confirmed genuine, not a repeat of the
  2026-09-02 convention mixup — the rack physically changed, and 32/58
  happening to be each other's complement here is coincidence, checked
  directly with Evan before recording it as real.
- **New turn radius**, wheelbase unchanged at 185.95 mm (Appendix DD/DE):

      R_min = wheelbase / tan(58°) = 185.95 / 1.6003 = 116.2 mm
      (equivalently R_min = 0.625 x wheelbase, since tan(58°) = 1/tan(32°)
      exactly — 58 and 32 are complementary angles)

  Comfortably inside the frozen 500-670 mm corner-radius band with room to
  spare — favourable, and still not a substitute for T2's empirical test.
- ⚠️ **What this does NOT tell us, and must not be assumed:** whether the
  pinion still sweeps ~180° lock-to-lock on the new rack (the OLD rack may
  have been the actual travel limit, not the pinion or servo), and whether
  the wheel-angle-per-pinion-degree relationship is still the same linear
  ratio the old SERVO_US_SPAN table assumed. **Both need a fresh bench
  measurement on the new rack before `SERVO_US_SPAN` is retuned or trusted
  near its old value** — see the warning after the old span table above.
  Until then, the safe assumption is that the servo's safe travel range is
  UNKNOWN on the new rack, not that it scales from the old numbers.

## Design margin: PLANNING max steer capped at 45° (2026-09-05, Appendix DM — CORRECTED by DN below, see that section first)

- ~~**Evan: "add some margin so make the max curve be only 45 degrees."**
  Same pattern as `SERVO_US_SPAN=450`... 45° is a DESIGN CHOICE... Keep
  both: mechanical capability vs. planning target are two different
  questions from here on.~~ **CORRECTED SAME DAY, Appendix DN: 45° is not a
  safe cutback from 58° — it may not be ACHIEVABLE at all.** See below.
- ~~**Planning R_min = wheelbase / tan(45°) = wheelbase exactly**... 185.95mm
  is comfortably inside the frozen 500-670mm corner band~~ **superseded —
  see DN.1 below before using any of these three numbers (58°, 116.2mm,
  45°/185.95mm).**

## The 58°/270° figures were measured with NO SERVO attached — the real ceiling may be ~39°, not 58° (2026-09-05, Appendix DN)

- **Both the 58° wheel-deviation (Appendix DL) and the ~270° pinion sweep
  (this section, above) were hand-measured on the bare linkage, servo
  disconnected** — confirmed directly with Evan. That means both describe
  what the RACK's own mechanical ends allow, not what the actual MG90S can
  reach. **The MG90S is a fixed-spec 180° servo (90° each way) — that
  number is independent of the rack** and does not grow when the rack does.
- **The pinion/rack now travels further (135° each way) than the servo can
  ever drive it (90° each way).** Assuming the same linear pinion-to-wheel
  ratio this project has used throughout (58°/135° = 0.4296, itself
  unverified — see the warning after the old SERVO_US_SPAN table):

      servo-achievable wheel deviation ~= 90 x (58/135) = 38.7 deg
      R_min at 38.7 deg = 185.95 / tan(38.7) = 232.4 mm

  **38.7° is an ESTIMATE from an unverified linear assumption, not a
  measurement** — flagged the same way the old table's ratio always was.
  But even as an estimate it settles the immediate question: **Evan's 45°
  planning target is likely ABOVE what the servo can physically deliver
  (reaching a true 45° wheel angle would need ~104.7° of pinion rotation,
  and the servo only has 90°), not a safe margin below a 58° mechanical
  max.** The rack is no longer the constraint on this build; the servo is.
- **The only way to get a real number is to bench-measure the wheel angle
  with the actual MG90S attached and driven to its own limit** — the same
  re-calibration Appendix DL already called for, now sharpened: measure the
  WHEEL angle directly at the servo's real safe span, don't compute it from
  the bare-linkage figures via the assumed ratio. Until that measurement
  exists, treat 38.7° (or whatever margin Evan wants below it) as
  provisional, and do not build to 45° as if it were a confirmed
  achievable target.
- **This does not undo the favourable part of Appendix DM**: the rack's own
  hard stop is still further away than the servo can reach, so the
  stall/cook risk from driving into the rack's end is reduced, not
  worsened, by the longer rack — the open question is only how MUCH wheel
  angle the servo itself yields, not whether the rack will bind first.

## Servo candidate found matching the full 135° range: HOOYIJ MG90D, 270° (2026-09-05, Appendix DO)

- **Evan asked directly for a servo covering the full 135° each way.**
  Found: **HOOYIJ MG90D-270, $16.99/4-pack** (Amazon B0D5YBL2JX). Same 20T
  spline, ~4.9 mm dia as the MG90S — the existing coupler design (Adafruit
  #4252 and `servo_lego_coupler_v1.stl`, both sized for this exact spline)
  should not need redesign. Same torque class (2.2 kg-cm @6V vs MG90S's
  ~2.2 kg-cm @4.8V) — does NOT worsen the coupler SF problem the way the
  MG996R fallback does (BOM row 7's warning still applies to that part, not
  this one).
- **The pulse-width table is the actual find**: 500-2500us = 270° full
  range; HALF that pulse range (500-1500us or 1500-2500us, split at the
  1500us neutral) = 135°±3°. In this project's firmware terms
  (`SERVO_US_CENTRE=1500`, `SERVO_US_SPAN` = "+/- from centre"), the
  geometric max span for this part is **1000 us**, driving the pinion
  through ±135° — matching the new rack's own measured travel (Appendix
  DN) with no wasted range on either side, if centering is good. This
  removes the servo-vs-rack mismatch DN found, rather than just estimating
  around it.
- ⚠️ **Not ordered, not bench-tested, not confirmed to fit the existing
  mount** — one dimension (22.4×12.1×22.8 mm vs the MG90S's usual
  ~22.8×12.2×31 mm) differs; check against `docs/WIRING_PROTOSHIELD.md`'s
  mount before assuming a drop-in fit. One review on the listing reports
  3-of-4 units dead on arrival (26 ratings, 4.2/5 avg) — the 4-pack's
  built-in spares partly cover that risk. The bench measurement of real
  wheel angle is still needed regardless of which servo is used.
- ~~**This is a candidate, not a BOM change** — `docs/BOM.md` row 7 still
  names the MG90S per this project's no-purchase-without-Evan's-go rule.~~
  **STALE since 2026-09-05, struck 2026-10-04:** BOM row 7 was swapped to the
  MG90D-270 that day (Appendix DP); Evan's 2026-10-04 cart holds it at $16.14
  (same ASIN `B0D5YBL2JX`).
- **Servo-to-pinion coupling CHOSEN: Adafruit #4252** (Evan, 2026-09-03) —
  the manufactured candidate this file and `docs/BOM.md` row 22 already
  named, $0.75, micro-servo spline → 16 mm Lego cross axle. Evan reports it
  already built and "strong," which is real information: it **empirically
  confirms the spline fit** on his actual MG90S — the open question in the
  first section of this file ("Adafruit's own wording... not guaranteed to
  fit with any other kind of servo splines... verify the spline before
  buying") is answered by his own build, not by the vendor's guarantee.
  **PRD task 8c(ii)'s done-check ("a coupling selected with its stall-torque
  margin stated") is only PARTIALLY met.** A part is selected. A numeric
  margin is not, and cannot be computed the way the printed-PLA case was
  (Appendix BV's SF 0.57-0.96 came from PLA's known interlayer shear
  strength) — **Adafruit publishes no torque rating for this injection-
  moulded part.** The honest ceiling without a published spec or a
  destructive test is Evan's own field assessment ("strong"), which is real
  evidence for a hobby-scale build but not a stated SF. Recommend treating
  that as sufficient for now rather than blocking on a number the vendor
  does not publish; flagged, not silently closed.
- **A PRINTED alternative now exists as a stopgap: `cad/servo_lego_coupler_v1.stl`**
  (2026-09-03, Appendix DG), from `scripts/gen_servo_lego_coupler.py`. Evan did
  not want ~$10 Adafruit shipping for a $0.75 part; a search of Amazon, eBay and
  AliExpress found **no other commercial source**, confirming BOM row 22 rather
  than overturning it. Ø10 × 16 mm: Ø4.65 mm round bore on the servo end (0.20
  under the spline — the metal spline cuts its own seat), Ø2.2 mm axial access
  to the servo's own retaining screw, and a 5.00 × 2.00 mm **female** cross
  socket 6 mm deep for a REAL Lego axle.
  ⚠️ **It obeys Appendix BV rather than relitigating it** — no printed cross
  profile anywhere; the printed part is a 2.50 mm-walled socket.
  ⚠️ **The 20T spline is deliberately NOT modelled**: ~0.76 mm tooth pitch is
  below 0.4 mm-nozzle resolution, so a modelled spline prints as a blurred round
  hole while claiming fidelity it lacks.
  ⚠️ **No safety factor is claimed and none can be computed** — friction plus
  spline bite, never loaded. Print PETG, not PLA. **Neither option has a real
  margin**, so this does not retire the #4252 purchase until one survives a test.
- **2026-10-04 (Evan): PRINT v1 INSTEAD of buying #4252** (BOM row 22 -> $0.00,
  NOT retired). Conditions that travel with it: print the socket-style
  `cad/servo_lego_coupler_v1.stl`, never a cross-axle stub (SF 0.57-0.96,
  Appendix BV). PETG, not PLA - and Evan's only prints so far are Bambu ABS,
  which neither the PLA SF math nor anything else here covers, so **ABS is
  UNANALYSED for this part**. No SF is claimed or computable. Never claim it
  works until it survives a load test (`important.md` #5).
  **FIRST check the parts bin:** the entry above records #4252 as "already
  built" and "strong" on 2026-09-03 - if it is on hand, nothing needs printing.
  **Coupler fit on the MG90D-270 is NOT bench-verified:** the #4252 fit was
  confirmed on the MG90S. The candidate entry above records the same 20T spline,
  but the body differs (22.8 mm vs ~31 mm), and v1's 4.65 mm bore was sized
  against the MG90S's ~4.8-4.9 mm spline. Test-fit ONE before printing several.
- **MG90S output shaft: 20-tooth spline, ~4.8-4.9 mm OD** (SkyStar/TinyTronics
  datasheet, servodatabase; 2026-09-03). Splined, not round — an adapter must
  grip the spline pattern, not a plain bore diameter.
