"""Road-marking dimensions for the physical track, scaled from the real MUTCD.

Requested by Evan 2026-09-06 ("can we start making street layouts?"). This is
the numeric input BOTH downstream consumers need: the printed marking strips
(PRD task T3) and any 3DStreet cross-section, which only speaks real-world
metres and therefore needs the full-scale side of every row.

WHY THIS FILE EXISTS: THE PROJECT'S MARKING TABLE HAS BEEN STALE SINCE
2026-08-05. `PRD_ROADMAP.md` says so in its own words -- "the marking table
below is stale and NOT yet recomputed". That table was scaled 1:14 from an
ESTIMATED 130 mm car width. The car has been measured four times since, the
governing width flipped from rear track to front track on 2026-09-05, and the
lane rule itself changed from a fixed scale to `lane = 2.0 x car width`
(`docs/SIM_TRANSFER_SPEC.md` section 3).

THE SCALE IS NOW DERIVED, NOT CHOSEN -- and that is the real finding here.
Once lane width follows the car, the model scale is no longer free: it is
whatever makes the model lane represent a real lane.

    scale = REAL_LANE_IN / model_lane        (model lane = 2.0 x car width)

At the 155 mm front track and the 1.613x lane rule that is 250 mm of lane and
a scale of **~1:14.63**.

HISTORY WORTH KEEPING, because the number went out and came back. The PRD
carried 1:14, CHOSEN in Appendix L against a 130 mm ESTIMATE. When the lane
rule replaced the fixed scale the derived scale became 1:11.80 (Appendix DT).
Then narrowing the lane to 250 mm for the two-lane switch (Appendix DX) moved
it to 1:14.63 -- almost exactly back on the original. **That is a coincidence,
not a vindication.** 1:14 was a round number against a wrong car width;
1:14.63 is derived from a measured one. They agree by accident and would
diverge again the moment either input moves.

WHAT IS MEASURED, WHAT IS A STANDARD, AND WHAT IS A JUDGEMENT CALL
  MEASURED   car width 155 mm (front track, Appendix DM)
  STANDARD   every full-scale figure below -- verified against the FHWA MUTCD
             (mutcd.fhwa.dot.gov Part 3B + Part 3 general, accessed
             2026-08-05, Appendix L). Not recalled from memory.
  DERIVED    the scale, and every model dimension
  JUDGEMENT  the dash compression. See DASH, below.

DASH -- THE ONE ROW THAT IS NOT A SCALING
  At true scale one dash cycle is 10 ft + 30 ft = 40 ft, which is 1033 mm at
  this scale. The whole driven route is 8.23 m, so the car would see about 8
  dash cycles in a full lap: almost no signal for a CNN that sees 64x64. The
  MUTCD's own text permits "dimensions in a similar ratio of line segments to
  gaps as appropriate", so the absolute size is compressed and the RATIO is
  the thing preserved.

  WHERE THE DASH GOES: the CENTRELINE, between the two directions of travel.
  Ordinary MUTCD placement -- yellow separates opposing directions. The track
  is TWO lanes as of 2026-09-06 (Appendix DX, Evan's call), 250 mm each.

  This took three tries and the trail is in the record, not repeated here:
  DV put the dash on the LANE EDGES because the track was then single-lane and
  had no centreline; DW corrected DV's claim that two lanes could not fit
  (they can -- span 2700 mm, spare 100 mm); DX switched to two lanes and so
  DELETED the dashed-edge deviation entirely. **Only the RATIO deviation below
  remains, and it is not claimed as MUTCD compliance.**

  RATIO RESOLVED 2026-09-06 BY EVAN (Appendix DU): dash:gap = 1:2. It had been ambiguous, and the
  ambiguity is worth keeping on the record because it survived a month in
  three documents. The project recorded the deviation as "Duckietown uses
  ~2:1" (Appendix L, HANDOFF, track.md) and NONE of the three said which way
  round. MUTCD's is dash:gap = 1:3 (10 ft dash, 30 ft gap). "2:1" could have
  meant gap:dash = 2:1 (dash 1 : gap 2, denser than MUTCD) or dash:gap = 2:1
  (dash LONGER than its gap, which no road marking does). Appendix L's own
  worked example -- "~60 mm dash / 180 mm gap" -- is 1:3, i.e. it kept MUTCD's
  ratio and never applied the 2:1 at all, so the appendix contradicted itself.
  Evan's call takes the gap:dash = 2:1 reading: denser than MUTCD, which was
  the entire point of the deviation. `--dash-to-gap` still re-runs the table
  at any other ratio.

Usage:
  python cad/marking_specs.py
  python cad/marking_specs.py --self-check
  python cad/marking_specs.py --car-width 0.155 --dash-to-gap 0.5
"""

from __future__ import annotations

import argparse

# ---- full scale: MUTCD, verified 2026-08-05 (Appendix L). Inches. ----------
MUTCD_LANE_IN = 12 * 12          # 12 ft standard travel lane
MUTCD_NORMAL_LINE_IN = (4, 6)    # normal longitudinal line
MUTCD_STOP_LINE_IN = (12, 24)    # stop line
MUTCD_DASH_IN = 10 * 12          # broken line: 10 ft segment ...
MUTCD_GAP_IN = 30 * 12           # ... 30 ft gap
MM_PER_IN = 25.4

# ---- the model side --------------------------------------------------------
CAR_WIDTH = 0.155        # m  MEASURED 2026-09-05, FRONT track (Appendix DM).
                         #    MIRRORS cad/track_layout_v2.py -- self_check
                         #    imports that file and fails if they drift.
LANE_TO_CAR = 250.0 / 155.0   # 1.613. ~~2.0x, SIM_TRANSFER_SPEC s3~~
                         #    CHANGED 2026-09-06 (Appendix DX, Evan): two
                         #    lanes at the 2.0x rule need a 620 mm road,
                         #    which fits the 3x3 grid ONLY at R=500 and so
                         #    commits frozen corner geometry before T2.
                         #    250 mm/lane also fits R=550. Inside
                         #    Duckietown's measured 1.4-1.6x band.
                         #    MIRRORS cad/track_layout_v2.py.
ROUTE_LEN_M = 7.51       # m  real output of cad/track_layout_v2.py 2026-09-06
                         #    at TWO lanes (was 8.23 single-lane, 8.31
                         #    before the floor-fit fix of Appendix DS)
DASH_TO_GAP = 0.5        #    dash length / gap length = 1:2. DECIDED by Evan
                         #    2026-09-06 (Appendix DU), resolving the "~2:1"
                         #    ambiguity the record carried in three places --
                         #    see the docstring. A deliberate deviation from
                         #    MUTCD's 1:3, not a scaling of it.
MIN_PRINTED_FEATURE_MM = 0.8   # PRD T3: printed marking strips are 0.8 mm min
TARGET_DASH_CYCLES = 40  #    dash cycles the car should see in one lap. The
                         #    whole reason the true-scale dash is rejected.
                         #                                              EST


def lane_width_m(car_width: float = CAR_WIDTH) -> float:
    """ONE lane, one direction. The road is LANES x this -- see
    track_layout_v2.py; the grid geometry consumes the ROAD, not this."""
    return LANE_TO_CAR * car_width


def scale(car_width: float = CAR_WIDTH) -> float:
    """Model scale, DERIVED. Returns N for a scale of 1:N."""
    return (MUTCD_LANE_IN * MM_PER_IN) / (lane_width_m(car_width) * 1000.0)


def to_model_mm(inches: float, car_width: float = CAR_WIDTH) -> float:
    return inches * MM_PER_IN / scale(car_width)


def dash_cycle(route_len_m: float = ROUTE_LEN_M,
               cycles: int = TARGET_DASH_CYCLES,
               dash_to_gap: float = DASH_TO_GAP):
    """Compressed dash, sized so one lap shows `cycles` of them.

    Returns (dash_mm, gap_mm, cycle_mm). The RATIO is the input; the absolute
    size falls out of how much training signal the lap has to carry.
    """
    cycle_mm = route_len_m * 1000.0 / cycles
    dash_mm = cycle_mm * dash_to_gap / (1.0 + dash_to_gap)
    return dash_mm, cycle_mm - dash_mm, cycle_mm


def table(car_width: float = CAR_WIDTH, dash_to_gap: float = DASH_TO_GAP):
    s = scale(car_width)
    d, g, cyc = dash_cycle(dash_to_gap=dash_to_gap)
    true_dash = to_model_mm(MUTCD_DASH_IN, car_width)
    true_gap = to_model_mm(MUTCD_GAP_IN, car_width)
    return {
        "car_width_mm": car_width * 1000.0,
        "scale": s,
        "lane_mm": lane_width_m(car_width) * 1000.0,
        "normal_line_mm": tuple(to_model_mm(i, car_width)
                                for i in MUTCD_NORMAL_LINE_IN),
        "stop_line_mm": tuple(to_model_mm(i, car_width)
                              for i in MUTCD_STOP_LINE_IN),
        "dash_true_mm": (true_dash, true_gap, true_dash + true_gap),
        "dash_used_mm": (d, g, cyc),
        "dash_cycles_true": ROUTE_LEN_M * 1000.0 / (true_dash + true_gap),
        "dash_cycles_used": ROUTE_LEN_M * 1000.0 / cyc,
    }


def self_check() -> None:
    # 1. the scale is DERIVED and round-trips: model lane x scale == 12 ft
    t = table()
    assert abs(t["lane_mm"] * t["scale"] - MUTCD_LANE_IN * MM_PER_IN) < 1e-6, t
    assert abs(t["lane_mm"] - 250.0) < 1e-9, t["lane_mm"]
    assert 14.5 < t["scale"] < 14.7, f"scale {t['scale']:.3f} is not ~1:14.6"

    # 2. REGRESSION against the six numbers Appendix L published at 1:14, which
    #    Appendix O.4's cold audit re-verified ("all six MUTCD 1:14 numbers
    #    reproduce exactly"). If this drifts, the SCALING ARITHMETIC changed.
    #
    #    NOTE THE DIRECTION, because it is the whole point of this file:
    #    Appendix L picked the SCALE (1:14) and derived the lane from it
    #    (12 ft / 14 = 261.3 mm). This file does the opposite -- lane comes
    #    from the car, scale falls out. So the regression must be driven by an
    #    explicit scale, not by a car width. (Feeding it the 130 mm car of the
    #    era gives lane 260.0 mm and scale 1:14.07 -- near-identical, which is
    #    WHY the swap went unnoticed. The two rules agreed at 130 mm and
    #    diverge as the car grows.)
    def at_14(inches):
        return inches * MM_PER_IN / 14.0
    assert abs(at_14(MUTCD_LANE_IN) - 261.0) < 0.5, at_14(MUTCD_LANE_IN)
    assert abs(at_14(MUTCD_NORMAL_LINE_IN[0]) - 7.3) < 0.1
    assert abs(at_14(MUTCD_STOP_LINE_IN[0]) - 22.0) < 0.5
    assert abs(at_14(MUTCD_STOP_LINE_IN[1]) - 44.0) < 1.0
    assert abs(at_14(MUTCD_DASH_IN) - 218.0) < 1.5
    assert abs(at_14(MUTCD_GAP_IN) - 653.0) < 2.0
    #    The old 2.0x rule happened to agree with 1:14 at the 130 mm car of
    #    the era (260.0 mm / 1:14.07 vs 261 mm / 1:14), which is why the
    #    direction reversal went unnoticed. That coincidence is GONE under
    #    the 1.613x rule -- no assert, because there is nothing left to pin.

    # 3. the dash compression does what it exists to do
    assert t["dash_cycles_true"] < 10, "true-scale dash was not actually sparse"
    assert t["dash_cycles_used"] >= 30, t["dash_cycles_used"]
    d, g, cyc = t["dash_used_mm"]
    assert abs(d + g - cyc) < 1e-9
    assert abs(d / g - DASH_TO_GAP) < 1e-9, "the compression lost its ratio"
    # ... and the ratio is the ONLY thing the MUTCD latitude preserves, so a
    #     dash longer than its gap is out of spec no matter how it is framed
    assert d < g, "dash must not be longer than its gap"

    # 4. every feature survives the printer. A 0.4 mm nozzle cannot lay a
    #    0.3 mm line, and a marking too thin to print is not a marking.
    assert t["normal_line_mm"][0] >= MIN_PRINTED_FEATURE_MM, t["normal_line_mm"]
    assert d >= MIN_PRINTED_FEATURE_MM, d

    # 5. ordering that must hold at any scale
    assert t["normal_line_mm"][0] < t["normal_line_mm"][1]
    assert t["stop_line_mm"][0] > t["normal_line_mm"][1], \
        "a stop line must be wider than the widest normal line"

    # 6. a wider car means a smaller scale number (less shrunk), not more
    assert scale(0.200) < scale(0.130), "scale must fall as the car grows"

    # 7. THE TWO SCRIPTS DESCRIBE ONE TRACK. Same guard as
    #    cad/vehicle_envelope.py (Appendix DS): a constant drifting in one
    #    file must FAIL here rather than diverge in silence. Imported INSIDE
    #    the check so a normal run of this file stays stdlib-only.
    import importlib.util
    from pathlib import Path
    _f = Path(__file__).with_name("track_layout_v2.py")
    _spec = importlib.util.spec_from_file_location("_track_layout_v2", _f)
    _t = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_t)
    assert _t.CAR_WIDTH == CAR_WIDTH, (
        f"CAR_WIDTH has drifted: {_f.name} says {_t.CAR_WIDTH}, this file says "
        f"{CAR_WIDTH}. One track, two scripts - they must agree.")
    assert abs(_t.LANE - lane_width_m()) < 1e-12, (
        f"lane has drifted: {_f.name} says {_t.LANE}, this file computes "
        f"{lane_width_m()}")

    print("marking_specs self_check: PASS")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--car-width", type=float, default=CAR_WIDTH)
    ap.add_argument("--dash-to-gap", type=float, default=DASH_TO_GAP)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0
    self_check()

    t = table(args.car_width, args.dash_to_gap)
    print("=" * 78)
    print("ROAD MARKING SPECS  (full scale = FHWA MUTCD, verified 2026-08-05)")
    print("=" * 78)
    print(f"car width   {t['car_width_mm']:.2f} mm  FRONT track, MEASURED (Appendix DM)")
    print(f"lane        {t['lane_mm']:.1f} mm per direction = {LANE_TO_CAR:.3f} x car "
          f"(road = 2 x this = {2*t['lane_mm']:.0f} mm)")
    print(f"SCALE       1:{t['scale']:.2f}  DERIVED from the lane rule, not chosen")
    print("            (PRD still says 1:14 -- overtaken, never re-derived)")
    print()
    print(f"{'feature':<22} {'full scale':>16} {'model':>18}   note")
    print("-" * 78)
    n0, n1 = t["normal_line_mm"]
    s0, s1 = t["stop_line_mm"]
    print(f"{'lane width':<22} {'12 ft':>16} {t['lane_mm']:>15.1f} mm   the input, not an output")
    print(f"{'normal line':<22} {'4-6 in':>16} {n0:>10.2f}-{n1:.2f} mm   white: same direction")
    print(f"{'stop line':<22} {'12-24 in':>16} {s0:>10.2f}-{s1:.2f} mm")
    td, tg, tc = t["dash_true_mm"]
    print(f"{'dash (TRUE scale)':<22} {'10 + 30 ft':>16} {td:>7.0f} + {tg:.0f} mm   "
          f"only {t['dash_cycles_true']:.1f} cycles per lap -- REJECTED")
    ud, ug, uc = t["dash_used_mm"]
    print(f"{'dash (USED)':<22} {'ratio only':>16} {ud:>7.1f} + {ug:.1f} mm   "
          f"{t['dash_cycles_used']:.0f} cycles per lap")
    print()
    print("  Yellow separates OPPOSING directions; white separates same-direction.")
    print(f"  Dash ratio: dash:gap = 1:{1/args.dash_to_gap:.0f}  (MUTCD is 1:3)")
    print("  DECIDED by Evan 2026-09-06, resolving the '~2:1 Duckietown' ambiguity")
    print("  the record carried in three places without ever saying which side was")
    print("  which. A deliberate deviation from MUTCD, not a scaling of it.")
    print()
    print("FOR 3DSTREET: feed it the FULL-SCALE column. It works in real-world")
    print(f"metres, so the street to build is a 12 ft ({MUTCD_LANE_IN*MM_PER_IN/1000:.4f} m) lane")
    print("with 4-6 in lines -- an ordinary US street. The model scale is ours, not its.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
