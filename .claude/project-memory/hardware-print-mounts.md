# hardware-print-mounts.md - printing, Lego fit, motors/gearing/couplers, printed mounts, measured vehicle geometry (split from hardware.md on 2026-10-29)
Moved verbatim from hardware.md, original relative order; router is hardware.md. Entries dated 2026-07-23 are desk research unless marked verified.
Cross-topic facts live in the file that fit best; check the sibling hardware-*.md files too.

- FDM tolerances don't match Lego injection molding — print test coupons for
  pin holes/axle bores and tune per-printer before any chassis print
  (2026-07-23). Community starting points: **~5.1mm pin fit, 5.3-5.6mm
  free-rotating axle bore** vs Ø4.8mm nominal; beam pitch 8mm. (inferred
  from published test boards, unverified on Evan's printer) **MEASURED
  2026-09-05, Bambu P1S/ABS (Appendices DI/DK) — BOTH numbers now closed:
  pin holes 4.80mm (v1; community's 5.1mm guess was too big here), rotating
  axle bores 5.00mm (v2; v1's 5.20-5.70 sweep was entirely too loose).**
  No calipers used on either coupon; verdicts are fit-by-feel against the
  coupon's own pass criteria, not measured offsets. Pitch-row dimensional-
  scaling check (beam across holes 1-2, then 1-5) never run — scale factor
  vs the nominal 32.00mm span is still unknown.
- ~~**PETG (not PLA) for rotating bores** against Lego axles — PLA galls/wears
  (LDraw forum guidance, 2026-07-23). PLA fine for static holes.~~
  **SUPERSEDED 2026-09-05: ABS is the standing chassis material now, not
  PLA or PETG** (Evan's call, replacing the PLA/PETG plan entirely). Real
  Lego parts are ABS, so an ABS print rubbing an ABS axle is a same-family
  pair — untested here whether that galls worse than the PLA-vs-ABS case
  this guidance was written for, or whether the 20-30 cycle spin-test isn't
  even needed because the v1 axle row failed on FIT (too loose) before
  galling could be assessed at all.
- Plain Lego motors have no position feedback — never use one for steering;
  hobby servo drives the Lego steering rack (2026-07-23).
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
- **Actual differential gearing is 20t→28t (N=1.400), confirmed by Evan
  2026-09-03 — the July research doc's Config A, not the "lower-risk"
  Config B (12t→28t, N=2.333) both `PRD_ROADMAP.md` and `HANDOFF.md`
  assumed.** The doc's own caveat on the in-plane 20t mesh ("verify
  physically before committing CAD") is now closed: it's the real part.
  But his measured tire is 55.75 mm, not either modeled diameter
  (43.2/62.4 mm). Re-derived with the July doc's own formulas
  (`docs/research/2026-07-23_drive-motor-selection.md`, reproduced and
  checked 2026-09-03): **top speed 1.83 m/s loaded, 2.09 m/s no-load
  (≈4.1–4.7 mph) — OVER the 1.0–1.5 m/s target band**, not under it.
  Cruise torque 12.5% of stall (was 9.7% for Config A). Accel current
  1.24 A at **76% of stall TORQUE** (not of stall current — 1.24/1.6 A is
  77.5%; the "76%" is 42.53/55.9 mN·m. Gloss corrected 2026-09-03, Appendix
  DB) — real headroom loss,
  still under the TB6612's 2 A paralleled rating. Accel-from-rest drops to
  1.38 m/s² (was 1.83). Traction margin unaffected: 4.7x, a vehicle-level
  check independent of drivetrain ratio. See Appendix CS.
- **The printed motor coupler is the LOWEST-torque joint, not the highest**
  (corrects the 2026-07-23 ~16:17 brief's premise). It sits upstream of the
  reduction: motor stall 55.9 mN·m vs ~45.6 mN·m per half-shaft downstream
  of a 2.333:1 diff. Still, print it as a **socket gripping a real Lego
  axle, never as a printed axle cross-profile** — a printed cross stub is
  only SF 2-4 in torsion at stall, collapsing toward 1 with sparse infill
  (2026-07-23).
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
    ~~`best_straight` is **capped at MAX_STRAIGHT = 200 mm**~~ **190 mm as of
    2026-09-06** (and mirrored in `cad/vehicle_envelope.py`, whose self-check
    now imports the other file and FAILS if the two copies drift). The
    uncapped value exceeds that cap at BOTH widths, so **pitch does not move
    at all**; span then changes by exactly the lane delta. **Real sensitivity
    is 2x the car-width change, not 4x**, while the straight stays capped.
    ⚠️ **That 'pitch does not move' shortcut only holds while the CAP binds.**
    Since 2026-09-06 `best_straight` also reserves `SPARE_MIN = 100 mm` of
    wall spare, so once a car gets wide enough the RESERVE binds instead and
    the straight (and therefore the pitch) shrinks to protect the spare —
    already true at R=550 (straight 95 mm) and R=600 (0 mm). The runnable,
    self-checking generator is the authority; a rule of thumb is not.
  - **CAVEAT, not yet closed: this is TIRE track, not whole-vehicle width.**
    Lane width must key off the widest point of the assembled car including
    chassis, electronics stack and any camera mount. Confirm nothing exceeds
    114.75 mm before freezing lane width.
  - **Rear is 7.0 mm wider than front.** Normal cars cut the rear wheels
    *inside* the front path in a corner; a wider rear track partly cancels
    that, so swept corner width is set by front-outer and rear-outer together.
    A T2 detail, not a today detail - noted so it is not rediscovered.

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

Three numbers — ~~and the governing one is unchanged~~ **the governing one
FLIPPED 2026-09-05 (Appendix DM), see below:**

| | mm | note |
|---|---|---|
| front track | ~~**107.5**~~ **155 as of 2026-09-05** | outside-to-outside. Changed by the steering rebuild (13-stud rack, Appendix DL) |
| rear track | **148.25** | outside-to-outside, unaffected by the steering rebuild |
| body | **135.75** | narrower than either track |

- ~~**148.25 mm is now a WHOLE-VEHICLE width... the rear wheels are the widest
  point**~~ **SUPERSEDED 2026-09-05: front (155) now exceeds rear (148.25) by
  6.75 mm. The front is the widest point and governs lane width.** This was
  true when written (2026-09-03) for the hardware that existed then.
- ~~**Lane width, span and spare are UNCHANGED** — 296.5 mm / 2696.5 mm /
  103.5 mm.~~ **CHANGED: lane 310 mm** (2.0 x 155 mm). ~~at R=500 span is
  now **2710 mm, spare only 90 mm** — UNDER the script's own 100 mm
  safety-margin self-check, which now FAILS~~ **CLOSED 2026-09-06: span
  2690 mm, spare 110 mm, self-check PASSES.**
  **The cause was NOT that the car outgrew the floor.** Two functions in
  `cad/track_layout_v2.py` held different definitions of usable width:
  `best_straight()` sized the straight against the whole 2800 mm, while the
  self-check demanded 100 mm of that 2800 be left unused. They had never
  agreed; the 200 mm straight cap bound first and hid it while lane was
  229.5 mm (171 mm spare). Lane going to 310 mm ate exactly the 80.5 mm of
  slack that was masking it. Fix: a `SPARE_MIN = 0.100` constant that
  `best_straight` now RESERVES and the self-check asserts, plus
  `MAX_STRAIGHT` 200 -> 190 mm. **The layout now self-corrects** — a future
  width increase shrinks the straight instead of failing the check, and it
  only fails when the straight hits 0 and the span still does not fit.
  ⚠️ **What the fix does NOT solve: at R=600 the straight is already 0 and
  spare is 90 mm — under SPARE_MIN with nothing left to shrink.** A T2
  result near 600 mm reopens the floor-fit as a real problem. The check
  only asserts the R=500 case, so it will not catch that on its own.
  ⚠️ **The print plan grew with the lane**: intersection boxes 10.67 -> 11.16 m,
  tiles 85 -> 88, filament ~1051 -> ~1081 g. Route 8.31 -> 8.23 m.
- ~~**The front track is only 72.5% of the rear**~~ **REVERSED: front is now
  104.5% of rear** (155/148.25). The two T2 consequences below are from the
  OLD geometry and no longer describe the car — kept for the trail, not as
  current guidance:
  - ~~Swept width in a corner is set by the rear outer wheel, not the
    front.~~ **Now the FRONT outer wheel governs**, the usual assumption for
    most cars (rear cuts inside the front path in a turn).
  - ~~The front wheels sit 28.25 mm inside the body~~ **no longer true** —
    front track (155) now exceeds body width (135.75) by 19.25 mm, so the
    front TYRES, not the body, are now the forward contact risk at a kerb
    or track edge.
- **Nothing here is a chassis decision yet.** These are donor-part
  measurements; the printed frame does not exist. Both tracks should be
  re-confirmed together on the same assembly before freezing anything —
  they were measured on two different dates against two different states
  of the steering.

## Drive-motor coupler v1 generated (2026-10-10, Appendix FN)

- `cad/motor_lego_coupler_v1.stl`: #5159 3 mm D-shaft bore (2.50 across the
  flat, 8 deep) to a 0.00-clearance real-Lego-axle socket, OD 7.4 x 15 mm.
  The 2.50 flat is UNMEASURED (single retailer) - caliper the shaft first.
- Generator now refuses a web hole that crosses the D flat (a 2.2 mm hole
  does; 1.5 mm used).
- 2026-10-11 (Appendix FP): motor coupler v2 = D-bore +0.075 mm (3.075 /
  2.575 across flat), 8 mm deep. v1 CONFIRMED too tight (Evan, Appendix FQ).
- 2026-10-11 (Appendix GF): motor coupler v3 (3.15 / 2.65 across flat) FITS the #5159
  shaft and is installed on the diff input axle. Fit only, NOT load-tested.
- 2026-10-11 (Appendix FY): the PLA pin-hole fit is UNKNOWN - the 4.80 mm figure is
  from the ABS coupons. `cad/pla_fit_coupon.stl` (untested) tests 4.75-5.00 pin
  holes, a counterbore, pitch, horizontal holes, servo-screw pilots and zip slots.
  The printed mounts are OpenSCAD (`cad/scad/`), gated on it and the measurements.
- 2026-10-11 (Appendix FS): motor coupler v3 = D-bore +0.150 over v1 (3.150 /
  2.650 across flat). v2 inferred still too tight. Shaft still unmeasured.
- 2026-10-12 (record GX) OPEN DESIGN REQUIREMENTS for the printed mounts: (1) the
  #5159 encoder cable comes up from BELOW the frames (motor under the centre
  frame, connector up) - the electronics tray needs a cable channel up to the
  Uno; (2) a mount for a STURDY camera mast (camera in shipping; the Pi's
  camera connector faces forward on the deck).
- 2026-10-12 (record HD) CAMERA MAST figures: lens 109 mm above the floor (+/-3; up to ~6 lower if the 250 mm lane is edge-to-edge), pitch 28-30 deg, over/just ahead of the front axle, centred; software rotation+lens remap to the sim view. Module 3 Wide V-FOV 67 deg (sim 90) - no pose matches without the remap. Mast: pinned pitch 20-35 deg, +/-0.3 deg, resonance >= 35-50 Hz (rule of thumb), focus locked. docs/research/2026-10-12_camera-mast-pose.md.
- 2026-10-12 (record HE) CAMERA MAST v1 + cable channel built (UNTESTED): mast pins to the two front "+" holes (axle-pins 43093) and servo-mount stud 2 (3L pins 6558); L tops 62.09 above floor (Evan); tray x 0 = rear-left centre-frame corner hole (photo matches RAIL_PIN_X); front axle tray x ~201, encoder socket x ~110 (photo, +/-3).
- 2026-10-13 (record IA) ELECTRONICS TRAY + DECK v3 (UNTESTED): print-friendly redo. Tray prints z 0 on the bed with NO supports: 2 mm ribs from the bed under the floor (edge ribs |y| 40..42, cross ribs x 5..7 / 144..146, skirts, a middle rib per lobe) - they rest on / hang just above the frame top, relying on "nothing sticks up under the tray" (HE). Tie notches z 5.3..7.8; -y feet now x 78 / 106; holder lobe to y 85; pockets = part footprint + fit class "pocket" (0.25/side). Deck: Pi pocket 92.3 x 64.9, chamfered rocker hole and peg tops.
- 2026-10-13 (record IB) ELECTRONICS LAYOUT: positions live ONLY in the LAYOUT lists of cad/scad/electronics_tray.scad and electronics_deck.scad; scripts/electronics_layout.py checks them against the STLs and draws docs/electronics_layout.svg (see docs/ELECTRONICS_LAYOUT.md). Side lobes are flat 3 mm plates on the frames, holder moved out to y 44.25, no zip slots (record IK). Deck underside now z 46.0 (record IJ: bank, holder, Pi on ~4 mm velcro, fences 14, Pi brackets 10; record II: +10 mm so the 50 x 34.25 x 12 fuse holder lies on the bank; was 32.0 in IB for the holder top 30.3); Uno standoffs 6 mm (USB-B plug over the pin boss at (10, -41.6)). Bank 151.5 x 70.55 x 18.0 is the right size (Evan; FZ 69.7 x 18.5 superseded). BMS + fuse + XT30 + charger in the -y lobe. ONE LM2596 on the deck (66 x 36, holes 61 x 31). Unmeasured: fuse holder body, XT30 mated length, Uno + shield height, rocker depth, charger port edge, holder lead end, servo lead length.
- 2026-10-14 (records IN, IO): supersedes parts of the line above - the BMS is ON TOP of the 2S holder (not the -y lobe) so the unfused B- / MB leads stay short; the fuse stays on the bank, charger + XT30 stay on the -y lobe. Now known (Evan): the charger's USB-C is on a short end, facing -x out the -y lobe's open edge; the holder's leads leave a short end - seat it at -x. Wiring picture: docs/bms_wiring.svg.
- 2026-10-13 (record IC) FILAMENT: every car part is Bambu PETG Translucent (Evan), nozzle 250 C, bed 70 C, P1S 0.4, 0.15 mm layers, 2 walls, 15 % cubic, X-Y hole/contour comp 0, elephant foot 0.25. PETG coupon row D (mount hole, recess both faces) = good at 4.90 / 4.95 / 5.00 / 5.05 -> friction_pin 4.95 kept. Rows A/B (plain / top recess) read looser at the same sizes - unexplained. press_shaft +0.15 is PLA-calibrated only. Best zip slot: 3.5 x 1.8.
- 2026-10-16 (record JU): NEW POWER BANK 168 x 62.16 x 22.51 (Evan; the 151.5 x 70.55 x 18.0 bank was flaky and is retired from the car). Ports on its rear end: USB-C at the -y corner, USB-A at the +y corner; charge button on the -y side ~10 mm forward of the rear end; rounded edges (radius not measured). Soldered pack wire lengths (Evan): P+ / P- 4 x 190 mm, fuse wire B+ -> holder + 326 mm (153 + 4 x 43.27), MB 55 mm from the holder's +x brass rivet, B- NOT recorded; encoder #4763 uncut 300 mm. Rear wheels peak 11 mm above the frame top (Evan). Layout: deck underside z 54.5, rocker on the -y wing, BMS at the holder's rivet end, charger USB-C out the -y side - see docs/ELECTRONICS_LAYOUT.md. pla_pocket_gauge.scad still gauges the OLD bank.
- 2026-10-16 (record JV): layout rule - every plug, cable run and terminal gets a LAYOUT clearance box so electronics_layout.py proves the space stays empty (JU passed with zero cable room). Plug estimates (Evan): USB-A 40, USB-C 30, USB-B 35 mm. Vilros case: LAN + USB-A one end, USB-C + camera the other, HDMI a side, fan on top. Encoder cable rises through a frame opening above the motor socket (Evan).
- 2026-10-16 (record JW): Evan's bench results - velcro = 15.5 mm dots, 3.5 mm per mated pair (VELCRO = 3.5); the Pi 5's USB-C is on the Vilros case's SIDE (car -y), ~7 mm from the camera (+x) end - NOT the back end (corrects the 2026-10-12 case note); USB-A + LAN sit 4 mm from the case sides; camera opening mid +x face (Evan modifying the case); bank charge LEDs on top near the -y side, ~10-40 mm from the port end; LM2596 terminals on the short ends; encoder cable ~30 mm spare on its route; bank USB-C cable > 320 mm.
- 2026-10-30 (record LZ, Evan): the Vilros case's ribbon slot lines up with the Pi 5's PCIe FPC connector, NOT the camera connectors - the camera cannot be attached with the case closed. Evan will modify the case (cut not decided). The JV layout assumption 'camera the other end' holds only after the mod; add the cut + ribbon route to the layout clearance boxes once it exists. Until then: bench = bare board.
