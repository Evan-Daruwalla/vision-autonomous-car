"""What the car's dimensions MUST satisfy, derived from the track, not chosen.

Requested by Evan 2026-09-01: "give requirements on height/width/length and
steering angle minimum".

This inverts the usual direction. Everywhere else the project measures the Lego
donor parts and lets the car "land where it lands" (HANDOFF, car-width note).
Here the track geometry is treated as fixed and the vehicle envelope is solved
for, so that when the rack and diff ARE measured there is a pass/fail to check
them against instead of a shrug.

THREE OF THE FOUR ARE DERIVABLE. HEIGHT IS NOT, AND THAT IS A REAL RESULT.
Camera height does not set the horizon row -- PITCH does (Appendix AR). So the
only thing that pins the real camera's height is matching the SIM's camera
height, and AR left that "NOT identified" with three diagnosed causes. Until
that measurement exists, any height number here would be invented. It is
reported as blocked, not guessed.

MODEL AND ITS LIMITS
  Bicycle (single-track) model, R = wheelbase / tan(steer). It ignores tyre
  slip, Ackermann error and body roll, all of which make the real radius LARGER
  than predicted -- so every steering-angle requirement below is a FLOOR, and a
  real car needs margin over it. `gotchas.md` already records that LEGO
  ball-jointed knuckles with a straight tie rod give near-parallel steer rather
  than true Ackermann, which costs radius on the inside wheel.

Usage:
  python cad/vehicle_envelope.py
  python cad/vehicle_envelope.py --self-check
"""

from __future__ import annotations

import argparse
import math

FLOOR = 3.000          # m   CONFIRMED by Evan 2026-09-01
WALL_MARGIN = 0.100    # m                                              EST
USABLE = FLOOR - 2 * WALL_MARGIN
STREETS = 3            # per axis, track v2
LANES = 2              #     lanes per street, one per direction (2026-09-06)
LANE_TO_CAR = 250.0 / 155.0   # 1.613 -- MIRRORS track_layout_v2.py
ROAD_TO_CAR = LANES * LANE_TO_CAR   # 3.226: total paved width per car width
MAX_STRAIGHT = 0.190   # m   cap on the straight run between corners    EST
                       #     MIRRORS track_layout_v2.py, which is the
                       #     authority. 200 -> 190 on 2026-09-06. Do not
                       #     edit one file's copy alone -- self_check below
                       #     imports the other file and fails if they drift.
MIN_SIDE_CLEARANCE = 0.050   # m  clearance per side IN A CORNER        EST
                       #     RE-POINTED 2026-09-09 (Evan's call, daily-audit
                       #     finding 11). It used to be checked against the
                       #     LANE edge, where the real margin is 29.6 mm/side
                       #     -- so the report printed TOO LONG at all six
                       #     wheelbases and exited 0 anyway, because NOTHING
                       #     asserted on it. A stated requirement that nothing
                       #     enforces is not a requirement.
                       #     It now measures to the ROAD edge, which is what
                       #     actually ends a run: crossing the centreline on a
                       #     two-lane track with no oncoming traffic is a paint
                       #     violation, leaving the road is a failure. Margin
                       #     there is 154.6 mm/side at the measured wheelbase,
                       #     3x this constant, and self_check now ASSERTS it.
                       #     Accepted cost: 29.6 mm is 24% of the half-lane, so
                       #     the policy will clip the centreline in corners.
WHEELBASE_MEASURED = 0.18595   # m  Appendix DD/DE. The wheelbase the assertion
                       #     below is stated at -- not a swept range, the real
                       #     car. steering.md:166 is the authority.
CAR_WIDTH = 0.155      # m   MEASURED front track (Appendix DM). The report
                       #     below used a hardcoded 0.130 ESTIMATE until
                       #     2026-09-06; its caption went stale the moment the
                       #     lane rule changed, which is what exposed it.


def steer_floor_deg(wheelbase: float, radius: float) -> float:
    """Smallest max-steer that can hold `radius` at `wheelbase`. A FLOOR."""
    return math.degrees(math.atan(wheelbase / radius))


def offtrack(wheelbase: float, radius: float) -> float:
    """How much wider than the car the swept path is, mid-corner.

    The rear axle cuts inside the front, so a turning car occupies more lateral
    space than its own width. Ignoring this is how a car that "fits the lane"
    on paper clips the line on every corner.
    """
    if radius <= wheelbase:
        return float("nan")
    return radius - math.sqrt(radius * radius - wheelbase * wheelbase)


def max_car_width(radius: float, straight: float = MAX_STRAIGHT,
                  streets: int = STREETS, usable: float = USABLE) -> float:
    """Widest car the track v2 grid can carry at this corner radius.

    Track v2: road = ROAD_TO_CAR x car width (2 lanes x 1.613), street pitch
    = 2R + straight, and span = (streets-1)*pitch + road must fit the usable
    floor. Solving for the car width:
        W <= (usable - (streets-1)*(2R + straight)) / ROAD_TO_CAR
    The divisor was 2 until 2026-09-06 (one lane at 2.0x); it is now 3.226.

    `straight` MATTERS, and holding it fixed is a bug: `track_layout_v2.py`
    shrinks it as the radius grows (`best_straight`), which is why v2 reports
    R=550 and R=600 fitting while a fixed 200 mm straight says they do not.
    Two scripts describing one track have to agree, so this takes the straight
    as an argument and the report below shows BOTH ends of the trade.
    """
    return (usable - (streets - 1) * (2 * radius + straight)) / ROAD_TO_CAR


def corner_clearance(car_width: float, wheelbase: float, radius: float) -> float:
    """LANE clearance per side while cornering, after off-tracking.

    Crossing this is a paint violation, not a failure -- the track is two-lane
    with no oncoming traffic. Kept because it is what the policy's cross-track
    error is judged against; it is NOT what MIN_SIDE_CLEARANCE now measures.
    """
    lane = LANE_TO_CAR * car_width
    return (lane - car_width - offtrack(wheelbase, radius)) / 2.0


def road_clearance(car_width: float, wheelbase: float, radius: float) -> float:
    """ROAD clearance per side while cornering -- margin to leaving the track.

    This is the one that ends a run, and as of 2026-09-09 it is what
    MIN_SIDE_CLEARANCE is checked against (see the constant's note).
    """
    road = ROAD_TO_CAR * car_width
    return (road - car_width - offtrack(wheelbase, radius)) / 2.0


def self_check() -> None:
    # steering floor: a longer car needs MORE lock for the same radius
    assert steer_floor_deg(0.15, 0.5) > steer_floor_deg(0.12, 0.5)
    # ... and a tighter corner needs more lock than a wide one
    assert steer_floor_deg(0.13, 0.4) > steer_floor_deg(0.13, 0.6)
    # a 45-degree lock turns at exactly one wheelbase of radius
    assert abs(steer_floor_deg(0.5, 0.5) - 45.0) < 1e-9

    # off-tracking is positive, grows with wheelbase, shrinks with radius
    assert offtrack(0.15, 0.5) > offtrack(0.12, 0.5) > 0
    assert offtrack(0.13, 0.4) > offtrack(0.13, 0.8)
    # and it is NaN, not a silent lie, when the geometry is impossible
    assert math.isnan(offtrack(0.6, 0.5))

    # width budget shrinks as the corner radius grows -- the whole reason
    # track v2 dies at R=670
    assert max_car_width(0.500) > max_car_width(0.600) > max_car_width(0.670)
    # ~~at TANGENT corners R=600 still carries a 130 mm car~~ NOT ANY MORE:
    # two lanes tripled the road-per-car divisor (2 -> 3.226) on 2026-09-06,
    # so R=600 now tops out at 124 mm. track_layout_v2.py agrees -- its
    # self_check asserts R=600 REFUSES at the two-lane road width.
    assert max_car_width(0.600, straight=0.0) < 0.130, (
        "R=600 should no longer carry a 130 mm car at two lanes")
    assert max_car_width(0.550, straight=0.0) >= 0.155, (
        "R=550 must still carry the MEASURED 155 mm car -- that is the whole "
        "reason the lane was narrowed to 1.613x instead of 2.0x")
    assert max_car_width(0.670, straight=0.0) < 0.130, "R=670 must not fit 130 mm"

    # HISTORICAL reproduction, kept as a regression on the SPAN formula only:
    # at R=500, 200 mm straights and the OLD single-lane 2x rule, a 130 mm car
    # spanned 2660 mm leaving 140 mm spare. The 2x is deliberately literal --
    # this pins the arithmetic of that era, not today's road rule.
    span = 2 * (2 * 0.500 + 0.200) + 2 * 0.130
    assert abs(span - 2.660) < 1e-9, span
    assert abs((USABLE - span) - 0.140) < 1e-9

    # corner clearance falls as the car lengthens
    assert corner_clearance(0.130, 0.100, 0.5) > corner_clearance(0.130, 0.180, 0.5)

    # MIN_SIDE_CLEARANCE IS NOW ENFORCED. Added 2026-09-09 (daily-audit finding
    # 11): the constant was documented as a requirement and checked nowhere, so
    # the report printed TOO LONG at every wheelbase in its own table and still
    # exited 0. Stated at the real car, not a swept range.
    _road_cl = road_clearance(CAR_WIDTH, WHEELBASE_MEASURED, 0.500)
    assert _road_cl >= MIN_SIDE_CLEARANCE, (
        f"road clearance {_road_cl*1000:.1f} mm/side at the measured "
        f"{WHEELBASE_MEASURED*1000:.2f} mm wheelbase is under the required "
        f"{MIN_SIDE_CLEARANCE*1000:.0f} mm. Either the car grew, the road "
        f"narrowed, or the corner tightened -- none of which may pass silently.")
    # ...and the lane figure is the one we KNOWINGLY accept, so pin it too: if
    # it ever climbs back over MIN_SIDE_CLEARANCE the road-edge rule stops being
    # the binding one and this file's framing needs revisiting.
    assert corner_clearance(CAR_WIDTH, WHEELBASE_MEASURED, 0.500) < MIN_SIDE_CLEARANCE

    # THE TWO SCRIPTS DESCRIBE ONE TRACK (see max_car_width's docstring), so a
    # constant drifting in one file must FAIL here rather than diverge in
    # silence. Added 2026-09-06 after MAX_STRAIGHT went 200 -> 190 in
    # track_layout_v2.py and this file's copy would otherwise have kept
    # printing 200 as 'the cap track_layout_v2.py uses'. Imported INSIDE the
    # check so a normal run of this file stays stdlib-only (that file needs
    # numpy; this one does not).
    import importlib.util
    from pathlib import Path
    _f = Path(__file__).with_name('track_layout_v2.py')
    _spec = importlib.util.spec_from_file_location('_track_layout_v2', _f)
    _t = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_t)
    # CAR_WIDTH added to the tuple 2026-09-09 (daily-audit finding 11): it is
    # duplicated at :50 here and track_layout_v2.py:92, and marking_specs.py
    # already guards its own copy -- this file was the one hole in that fence.
    for _name in ('FLOOR', 'WALL_MARGIN', 'STREETS', 'MAX_STRAIGHT',
                  'LANES', 'LANE_TO_CAR', 'CAR_WIDTH'):
        assert getattr(_t, _name) == globals()[_name], (
            f'{_name} has drifted: {_f.name} says {getattr(_t, _name)}, '
            f'this file says {globals()[_name]}. One track, two scripts - '
            f'they must agree.')
    assert _t.SPARE_MIN > 0, 'track_layout_v2 lost its wall-spare reserve'

    print("vehicle_envelope self_check: PASS")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0
    self_check()

    print("=" * 74)
    print("VEHICLE ENVELOPE REQUIREMENTS  (derived from track v2, not chosen)")
    print("=" * 74)
    print(f"floor {FLOOR:.2f} m, usable {USABLE:.2f} m, {STREETS}x{STREETS} street grid")
    print("Every requirement is a FLOOR from a bicycle model that ignores tyre")
    print("slip, Ackermann error and roll -- all of which enlarge the real")
    print("radius. Budget margin over these, do not build to them.\n")

    print("-" * 74)
    print("1. WIDTH  -- hard ceiling, set by the grid fitting the floor")
    print("-" * 74)
    print("  The straight run between corners trades directly against width.")
    print("  At straight=0 the corners are tangent (no straight street at all);")
    print(f"  {MAX_STRAIGHT*1000:.0f} mm is the cap track_layout_v2.py uses when the floor allows.")
    print()
    print(f"{'corner R':>9} {'W max @ s=0':>13} {'W max @ s=200':>15}   "
          f"verdict for a 130 mm car")
    for R in (0.500, 0.550, 0.600, 0.670):
        w0 = max_car_width(R, straight=0.0)
        w2 = max_car_width(R, straight=MAX_STRAIGHT)
        f0 = f"{w0*1000:12.0f}mm" if w0 > 0 else f"{'none':>14}"
        f2 = f"{w2*1000:14.0f}mm" if w2 > 0 else f"{'none':>16}"
        if w0 >= 0.130 and w2 >= 0.130:
            v = "fits, with proper straights"
        elif w0 >= 0.130:
            v = "fits ONLY with tangent corners (no straight street)"
        else:
            v = "DOES NOT FIT a 130 mm car"
        print(f"{R*1000:8.0f}mm {f0} {f2}   {v}")
    print("\n  The 130 mm working estimate is UNMEASURED (Appendix L). Width is")
    print("  set by the Lego steering rack + diff, which nobody has measured.")
    print("  Lower bound: whatever those parts are. Upper bound: the table above.")

    print()
    print("-" * 74)
    print("2. STEERING ANGLE  -- minimum max-lock, by wheelbase and corner")
    print("-" * 74)
    print("  (all angles in DEGREES; 'd' suffix)")
    print(f"{'wheelbase':>10}" + "".join(f"{int(r*1000):>10}mm" for r in
                                         (0.400, 0.500, 0.600, 0.670)))
    print(f"{'':>10}" + "".join(f"{'corner R':>12}" for _ in range(1)))
    for wb in (0.100, 0.120, 0.140, 0.160, 0.180):
        row = "".join(f"{steer_floor_deg(wb, r):>10.1f}d"
                      for r in (0.400, 0.500, 0.600, 0.670))
        print(f"{wb*1000:9.0f}mm{row}")
    print("\n  Read the R=500 column: that is the tightest corner track v2 uses.")
    print("  The recorded ~330 mm minimum-radius estimate (Appendix L) implies")
    print(f"  {steer_floor_deg(0.130, 0.330):.1f} deg at a 130 mm wheelbase -- which is where")
    print("  that estimate came from, and it is arithmetic on an unmeasured car.")

    print()
    print("-" * 74)
    print("3. LENGTH  -- bounded by off-tracking eating lane clearance")
    print("-" * 74)
    print("  A turning car sweeps WIDER than its own width: the rear axle cuts")
    print("  inside the front. Clearance per side, cornering at R=500 mm:\n")
    print(f"{'wheelbase':>10} {'off-track':>10} {'to lane edge':>13} "
          f"{'to ROAD edge':>13}   verdict")
    for wb in (0.100, 0.120, 0.140, 0.160, 0.180, 0.200):
        ot = offtrack(wb, 0.500)
        cl = corner_clearance(CAR_WIDTH, wb, 0.500)
        rc = road_clearance(CAR_WIDTH, wb, 0.500)
        ok = "OK" if rc >= MIN_SIDE_CLEARANCE else "TOO LONG"
        print(f"{wb*1000:9.0f}mm {ot*1000:9.1f}mm {cl*1000:12.1f}mm "
              f"{rc*1000:12.1f}mm   {ok}")
    print(f"\n  (at the MEASURED {CAR_WIDTH*1000:.0f} mm car, lane "
          f"{LANE_TO_CAR*CAR_WIDTH*1000:.0f} mm, road "
          f"{ROAD_TO_CAR*CAR_WIDTH*1000:.0f} mm, needing "
          f">={MIN_SIDE_CLEARANCE*1000:.0f} mm/side TO THE ROAD EDGE)")
    print("  The verdict is judged on the ROAD column (Evan, 2026-09-09): the")
    print("  lane column is the paint, the road column is what ends a run.")
    print(f"  At the measured {WHEELBASE_MEASURED*1000:.2f} mm wheelbase the lane")
    print(f"  margin is {corner_clearance(CAR_WIDTH, WHEELBASE_MEASURED, 0.5)*1000:.1f}"
          f" mm/side -- KNOWINGLY under the {MIN_SIDE_CLEARANCE*1000:.0f} mm figure,")
    print("  so expect the policy to clip the centreline in corners.")
    print("  Overall LENGTH is wheelbase plus overhangs; overhangs do not")
    print("  off-track but do decide whether the car fits an intersection box")
    print(f"  ({ROAD_TO_CAR*CAR_WIDTH*1000:.0f} mm square -- the ROAD width, "
          f"at the measured {CAR_WIDTH*1000:.0f} mm car).")

    print()
    print("-" * 74)
    print("4. HEIGHT  -- CANNOT BE DERIVED YET. Not an oversight.")
    print("-" * 74)
    print("  Camera height does NOT set the horizon row; pitch does (AR). The")
    print("  horizon sits at row 41.97 of 120 because the camera is pitched")
    print("  16.3 deg down, and that is true at ANY height.")
    print()
    print("  What height DOES change is scale: how much ground area a pixel")
    print("  covers, and therefore how far ahead the lane is resolvable. To")
    print("  reproduce the sim's projection the real camera must sit at the")
    print("  SIM's height -- and Appendix AR.5 left that NOT IDENTIFIED, with")
    print("  three diagnosed causes (left-edge censoring, cte spanning only")
    print("  +-0.17 m, and the PID coupling heading to cte).")
    print()
    print("  So: no height requirement can be stated until that sim measurement")
    print("  is made. Any number here would be invented. BLOCKED on AR.5.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
