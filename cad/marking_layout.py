"""WHERE the markings go and HOW the board is tiled -- the layer on top of the grid.

Requested by Evan 2026-09-06 ("plan out a street layout"). `track_layout_v2.py`
says where the streets are; `marking_specs.py` says how wide a line is. Neither
says where a line STOPS, and nothing at all said where the board gets cut.

THIS FILE OWNS NO DIMENSIONS. Geometry comes from `track_layout_v2.build()`,
dimensions from `marking_specs.table()`. A third copy of any constant is the
defect class Appendix DX exists to end, so `self_check` imports both and fails
if they drift.

THE TWO TILINGS, which no document had ever distinguished
  SUBSTRATE PANELS -- dark matte foam board / coroplast, the road surface.
  MARKING STRIPS   -- printed 2 mm tiles glued flush on top.
  `gotchas.md`'s rule -- "a seam running perpendicular to travel reads as a STOP
  BAR to the model" -- constrains the SUBSTRATE. The only tiling ever computed
  before this file (`print_plan`'s `ceil(printed_len / 0.200)`) counts STRIPS,
  so the constraint was enforced by nothing.

  Handled here by construction: substrate panels are long strips running ALONG
  each street's travel axis, so every seam is parallel to travel. With a 500 mm
  road and PANEL_MAX_W = 250 mm that is exactly two strips per street, and
  **the single longitudinal seam lands on the centreline, where the centreline
  marking covers it.** Straight streets end up with no visible seam at all.
  Intersections are single uncut panels -- a seam inside a box would cross
  travel on one of the two streets no matter how it were oriented.

WHY THE CENTRELINE BREAKS AT INTERSECTIONS
  MUTCD drops the centreline through an intersection. Kept, because it is free
  realism and because a line running straight through a junction is the visual
  the model would use to decide it may proceed.

WHY STOP LINES GO ON EVERY DRIVEN APPROACH, OR NONE
  Appendix Y.3 requires the stop SIGN be relocatable so the policy cannot
  memorise its position. **A painted stop line is exactly as much of a
  positional giveaway as a fixed sign.** Painting a subset would reintroduce the
  leak Y.3 exists to close. So: all four approaches of all seven DRIVEN
  intersections, 28 lines, and the line then says nothing about where the sign
  is on any given run.

WHAT IS DELIBERATELY NOT MARKED
  The route uses 7 of the 9 intersections. (-1.1, -1.1) and (+1.1, +1.1) are
  never driven -- they are the ends of the diagonal the figure-8 does not touch.
  Their boxes are not painted and get no stop lines.
  ⚠️ Honest cost: the streets still physically cross there, so an unmarked
  crossing may be visible in peripheral frames. At 64x64 that is small, but it
  is a real domain gap and is recorded as one rather than assumed away.

Usage:
  python cad/marking_layout.py
  python cad/marking_layout.py --self-check
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

PANEL_MAX_W = 0.250    # m  widest substrate strip that is practical to cut and
                       #    lay flat. 250 mm x 2 = the 500 mm road exactly, so
                       #    the one seam hides under the centreline.      EST


def _load(name):
    """Load a sibling CAD module by path. Lazy for the same reason
    track_layout_v2._marking_specs is: these files import each other's
    self-checks and a module-level import would be a cycle."""
    f = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(f"_{f.stem}", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _subtract(interval, holes):
    """interval minus a list of holes -> list of surviving sub-intervals."""
    out = [interval]
    for h0, h1 in holes:
        nxt = []
        for a, b in out:
            if h1 <= a or h0 >= b:          # no overlap
                nxt.append((a, b))
                continue
            if a < h0:
                nxt.append((a, h0))
            if h1 < b:
                nxt.append((h1, b))
        out = nxt
    return [(a, b) for a, b in out if b - a > 1e-9]


def layout(g=None, t=None):
    """Full marking + substrate layout. `g` from track_layout_v2.build(),
    `t` from marking_specs.table()."""
    tl = _load("track_layout_v2.py")
    ms = _load("marking_specs.py")
    g = g or tl.build()
    t = t or ms.table()

    road, pitch = g["road"], g["pitch"]
    half = road / 2.0
    coords = list(g["street_coords"])          # -pitch, 0, +pitch
    end = max(coords) + half                   # street runs -end .. +end
    boxes = [(c - half, c + half) for c in coords]

    driven = {(round(x, 6), round(y, 6)) for x, y in g["verts"]}
    all_ix = [(round(x, 6), round(y, 6)) for x, y in g["intersections"]]
    undriven = [p for p in all_ix if p not in driven]

    dash, gap, cycle = t["dash_used_mm"]
    dash, gap, cycle = dash / 1000.0, gap / 1000.0, cycle / 1000.0

    # ---- centreline runs: the street, minus every intersection box on it ----
    centre_runs = []       # (axis, street_coord, start, end)
    for axis in ("NS", "EW"):
        for c in coords:
            for a, b in _subtract((-end, end), boxes):
                centre_runs.append((axis, c, a, b))
    centre_len = sum(b - a for _, _, a, b in centre_runs)

    # dashes that actually fit in those runs -- NOT route length / cycle
    dashes = sum(int((b - a) // cycle) for _, _, a, b in centre_runs)

    # ---- stop lines: 4 approaches x every DRIVEN intersection ----------------
    stop_lines = []        # (x, y, approach, length)
    for (x, y) in sorted(driven):
        for approach in ("N", "S", "E", "W"):
            stop_lines.append((x, y, approach, road / 2.0))   # spans one lane

    # ---- substrate panels ---------------------------------------------------
    # strips ALONG each street's travel axis; intersections are single pieces.
    strips_per_road = max(1, round(road / PANEL_MAX_W))
    panels = []            # (kind, axis, seam_axis, length, width)
    for axis in ("NS", "EW"):
        for c in coords:
            for a, b in _subtract((-end, end), boxes):
                for _ in range(strips_per_road):
                    panels.append((f"street-{axis}", axis, axis,
                                   b - a, road / strips_per_road))
    for (x, y) in all_ix:
        panels.append(("intersection", "both", "none", road, road))

    return {
        "road": road, "pitch": pitch, "street_end": end, "boxes": boxes,
        "driven": sorted(driven), "undriven": sorted(undriven),
        "centre_runs": centre_runs, "centre_len_m": centre_len,
        "dash_m": dash, "gap_m": gap, "cycle_m": cycle, "dashes": dashes,
        "stop_lines": stop_lines,
        "stop_line_w_mm": t["stop_line_mm"],
        "edge_line_w_mm": t["normal_line_mm"],
        "panels": panels, "strips_per_road": strips_per_road,
        "route_len_m": g_route_len(g),
    }


def g_route_len(g):
    import math
    r = g["route"]
    return float(sum(math.dist(r[i], r[i + 1]) for i in range(len(r) - 1)))


def route_centreline_fraction(g, road):
    """How much of the DRIVEN route carries a centreline at all.

    The route crosses an intersection box 8 times (7 intersections, the centre
    one twice), and each crossing is `road` long with no centreline in it.
    """
    crossings = len(g["verts"])          # 8 vertices = 8 box traversals
    return crossings * road


def self_check() -> None:
    tl = _load("track_layout_v2.py")
    ms = _load("marking_specs.py")
    g, t = tl.build(), ms.table()
    L = layout(g, t)

    # 1. THE SEAM RULE -- the one physical constraint, previously unenforced.
    for kind, axis, seam, _len, _w in L["panels"]:
        if kind.startswith("street-"):
            assert seam == axis, f"{kind}: seam {seam} is not parallel to travel {axis}"
        else:
            assert seam == "none", "an intersection panel must be uncut"

    # 1b. two strips per road, so the seam lands ON the centreline and is
    #     covered by it. If PANEL_MAX_W ever stops dividing the road evenly the
    #     seam moves off-centre and becomes visible -- fail loudly then.
    assert L["strips_per_road"] == 2, L["strips_per_road"]
    assert abs(L["road"] / L["strips_per_road"] - L["road"] / 2) < 1e-12

    # 2. NO CENTRELINE INSIDE ANY INTERSECTION BOX
    for _axis, _c, a, b in L["centre_runs"]:
        for h0, h1 in L["boxes"]:
            assert b <= h0 + 1e-9 or a >= h1 - 1e-9, \
                f"centreline run ({a:.3f},{b:.3f}) overlaps box ({h0:.3f},{h1:.3f})"

    # 3. LENGTH CONSERVATION -- runs plus boxes must reconstruct every street,
    #    so a break inserted at an intersection cannot silently delete road.
    n_streets = 2 * len(g["street_coords"])
    full = n_streets * (2 * L["street_end"])
    boxed = n_streets * sum(h1 - h0 for h0, h1 in L["boxes"])
    assert abs(L["centre_len_m"] + boxed - full) < 1e-9, \
        (L["centre_len_m"], boxed, full)

    # 4. STOP LINES: 4 per DRIVEN intersection, and none on an undriven one
    assert len(L["driven"]) == 7, L["driven"]
    assert len(L["undriven"]) == 2, L["undriven"]
    assert len(L["stop_lines"]) == 4 * 7, len(L["stop_lines"])
    undriven = set(L["undriven"])
    for x, y, _a, _l in L["stop_lines"]:
        assert (x, y) not in undriven, f"stop line on undriven intersection {(x, y)}"
    # the two undriven ones are the untouched diagonal, not an arbitrary pair.
    # Tolerance, not equality: intersection coords are rounded to 6 dp while
    # g["pitch"] is 1.0999999999999999.
    want = [(-g["pitch"], -g["pitch"]), (g["pitch"], g["pitch"])]
    for (gx, gy), (wx, wy) in zip(L["undriven"], want):
        assert abs(gx - wx) < 1e-6 and abs(gy - wy) < 1e-6, (L["undriven"], want)

    # 5. a stop line must be wider than an edge line or it reads as one
    assert L["stop_line_w_mm"][0] > L["edge_line_w_mm"][1], \
        (L["stop_line_w_mm"], L["edge_line_w_mm"])

    # 6. DRIFT GUARD -- this file owns no dimensions; prove it still agrees.
    assert abs(L["road"] - tl.ROAD) < 1e-12
    assert abs(L["dash_m"] * 1000 - t["dash_used_mm"][0]) < 1e-9
    assert abs(ms.lane_width_m() - tl.LANE) < 1e-12, "lane rule drifted"

    print("marking_layout self_check: PASS")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0
    self_check()

    tl = _load("track_layout_v2.py")
    g = tl.build()
    L = layout(g)
    road = L["road"]

    print("=" * 76)
    print("MARKING + SUBSTRATE LAYOUT  (geometry: track_layout_v2 / dims: marking_specs)")
    print("=" * 76)
    print(f"road {road*1000:.0f} mm, {len(g['street_coords'])} streets per axis, "
          f"street runs +/-{L['street_end']*1000:.0f} mm")
    print()
    print("CENTRELINE (dashed yellow, broken at every intersection)")
    print(f"  runs            {len(L['centre_runs'])} segments, "
          f"{L['centre_len_m']*1000:.0f} mm total")
    print(f"  dash / gap      {L['dash_m']*1000:.1f} / {L['gap_m']*1000:.1f} mm "
          f"(cycle {L['cycle_m']*1000:.1f} mm)")
    print(f"  dashes laid     {L['dashes']}")
    print()
    print("STOP LINES (all 4 approaches of all 7 DRIVEN intersections)")
    print(f"  count           {len(L['stop_lines'])}")
    print(f"  width           {L['stop_line_w_mm'][0]:.2f}-{L['stop_line_w_mm'][1]:.2f} mm")
    print(f"  NOT marked      {L['undriven']}  (never driven)")
    print()
    print("SUBSTRATE PANELS (seams parallel to travel -- gotchas.md)")
    street_p = [p for p in L["panels"] if p[0].startswith("street-")]
    ix_p = [p for p in L["panels"] if p[0] == "intersection"]
    print(f"  street strips   {len(street_p)}, {L['strips_per_road']} per road at "
          f"{road/L['strips_per_road']*1000:.0f} mm wide")
    print(f"  intersections   {len(ix_p)} single uncut {road*1000:.0f} mm squares")
    print("  the one longitudinal seam lands ON the centreline and is covered by it")
    print()
    lost = route_centreline_fraction(g, road)
    carries = L["route_len_m"] - lost
    # ASCII only in printed output: Windows stdout is cp1252 and an emoji here
    # raises UnicodeEncodeError. Comments and docstrings can carry them; prints
    # cannot. The other three CAD scripts already follow this.
    print("!! DASH DENSITY ON THE DRIVEN ROUTE -- not what the spec assumed")
    print(f"  route            {L['route_len_m']*1000:.0f} mm")
    print(f"  inside boxes     {lost*1000:.0f} mm ({lost/L['route_len_m']*100:.0f}%) "
          f"-- 8 box traversals, no centreline in any of them")
    print(f"  carries a dash   {carries*1000:.0f} mm")
    print(f"  cycles per lap   {carries/L['cycle_m']:.1f}   "
          f"vs marking_specs' TARGET_DASH_CYCLES = 40")
    print("  The target was computed on the FULL route length, which assumed the")
    print("  centreline runs through intersections. It does not. Either accept the")
    print("  lower density or shrink the cycle -- Evan's call, not decided here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
