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
MAX_STRAIGHT = 0.200   # m   cap on the straight run between corners    EST
MIN_SIDE_CLEARANCE = 0.050   # m  clearance per side IN A CORNER        EST


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

    Track v2: lane = 2.0 x car width, street pitch = 2R + straight, and
    span = (streets-1)*pitch + lane must fit the usable floor. Solving for the
    car width:  W <= (usable - (streets-1)*(2R + straight)) / 2

    `straight` MATTERS, and holding it fixed is a bug: `track_layout_v2.py`
    shrinks it as the radius grows (`best_straight`), which is why v2 reports
    R=550 and R=600 fitting while a fixed 200 mm straight says they do not.
    Two scripts describing one track have to agree, so this takes the straight
    as an argument and the report below shows BOTH ends of the trade.
    """
    return (usable - (streets - 1) * (2 * radius + straight)) / 2.0


def corner_clearance(car_width: float, wheelbase: float, radius: float) -> float:
    """Lane clearance per side while cornering, after off-tracking."""
    lane = 2.0 * car_width
    return (lane - car_width - offtrack(wheelbase, radius)) / 2.0


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
    # at TANGENT corners R=600 still carries a 130 mm car -- this is the case a
    # fixed 200 mm straight got wrong, and track_layout_v2.py agrees it fits
    assert max_car_width(0.600, straight=0.0) >= 0.130
    assert max_car_width(0.670, straight=0.0) < 0.130, "R=670 must not fit 130 mm"
    # and the two scripts must agree on the same input
    assert abs(max_car_width(0.500, straight=0.200) - 0.200) < 1e-9

    # the v2 numbers reproduce: at R=500 with 200 mm straights the grid spans
    # 2660 mm for a 130 mm car, leaving 140 mm spare
    span = 2 * (2 * 0.500 + 0.200) + 2 * 0.130
    assert abs(span - 2.660) < 1e-9, span
    assert abs((USABLE - span) - 0.140) < 1e-9

    # corner clearance falls as the car lengthens
    assert corner_clearance(0.130, 0.100, 0.5) > corner_clearance(0.130, 0.180, 0.5)
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
    print("  200 mm is the cap track_layout_v2.py uses when the floor allows.")
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
    print(f"{'wheelbase':>10} {'off-track':>10} {'clearance/side':>15}   verdict")
    for wb in (0.100, 0.120, 0.140, 0.160, 0.180, 0.200):
        ot = offtrack(wb, 0.500)
        cl = corner_clearance(0.130, wb, 0.500)
        ok = "OK" if cl >= MIN_SIDE_CLEARANCE else "TOO LONG"
        print(f"{wb*1000:9.0f}mm {ot*1000:9.1f}mm {cl*1000:14.1f}mm   {ok}")
    print(f"\n  (at the 130 mm working car width, lane 260 mm, "
          f"needing >={MIN_SIDE_CLEARANCE*1000:.0f} mm/side)")
    print("  Overall LENGTH is wheelbase plus overhangs; overhangs do not")
    print("  off-track but do decide whether the car fits an intersection box")
    print(f"  ({2*0.130*1000:.0f} mm square at a 130 mm car).")

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
