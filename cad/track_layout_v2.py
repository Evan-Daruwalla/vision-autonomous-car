"""Track v2: a 3x3 city street grid on a 3.0 x 3.0 m floor, driven as a figure-8.

**NOTHING HERE IS COMMITTED GEOMETRY, AND THIS ONE IS AT RISK.** v1's caveat
applies (corner radius FROZEN until the B3 turning test), but v2 is worse: the
3x3 grid fits ONLY at R = 500 mm, the OPTIMISTIC end of the frozen 500-670 mm
band, with 20 mm of margin on 2800 mm of usable floor. Measured:

    R = 500 mm -> 3x3 streets, 4 blocks, 9 intersections, span 2780 mm  FITS
    R = 550 mm -> span 2980 mm                                          NO
    R = 600 mm -> span 3180 mm                                          NO
    R = 670 mm -> span 3460 mm                                          NO

And there is NO smaller-city fallback. A 2x2 grid has the space at those radii
but cannot carry this route at all: the figure-8 needs a centre street to cross
on plus outer streets both sides, and two streets admit only a perimeter loop --
the oval `gotchas.md` bans. So B3 above 500 mm does not shrink the city, it
DELETES it, and the fallback is v1's non-grid figure-8.

The generator is parametric for exactly that reason: re-run it with the measured
radius and it either regenerates or refuses. Do not cut anything from it first.

WHY A FIGURE-8 ROUTE ON A GRID (not a perimeter loop)
  `gotchas.md` bans an oval: it teaches "always steer left". A perimeter lap of
  a city grid is an oval with square corners -- every turn the same way. The
  driven route here is ONE closed circuit that PASSES THROUGH the centre
  intersection twice on perpendicular headings: three LEFT turns round the
  top-left block, straight through the centre, three RIGHT turns round the
  bottom-right block, straight through again. Balanced turns, genuine level
  crossing.

  It must pass THROUGH the centre, not meet at a block corner. Two rounded
  loops on diagonally opposite blocks do not touch -- rounding pulls each
  R*(sqrt(2)-1) ~ 207 mm clear of the shared corner, giving two separate loops
  with no way to drive between them. That was the first cut of this file, and
  self-check 6 now tests for it directly.

  The route needs 3 streets per axis (a centre to cross on, outer streets both
  sides). A 2x2 grid cannot host it at all -- see build().

WHY INTERSECTIONS ARE FINE FOR BEHAVIOURAL CLONING, AND WHAT IT COSTS
  A cloned lane-follower has no goal input, so it cannot CHOOSE at a junction.
  It does not have to: M3 (`PRD_ROADMAP.md:306-310`) collects 10-20 laps of the
  SAME route, so the policy learns "turn right at this intersection" from the
  visuals. That is route memorisation, not navigation -- a different route means
  retraining, and the honest write-up must say so. It is still a better result
  than an oval.

WHY THE SIM CANNOT REHEARSE THIS
  gym-donkeycar's protocol has no road-definition message. Its whole vocabulary
  is load_scene / car_config / cam_config / cam_config_b / lidar_config /
  control / reset_car / racer_info / get_scene_names / exit_scene, and
  load_scene picks from 11 prebuilt Unity scenes. A custom track needs a Unity
  build. This costs less than it sounds: M3 trains on real laps, not the sim
  corpus. What must still match the sim is the CONTROL LOOP and CAMERA (20 Hz,
  1.401 m/s, 120x160 -> 64x64, fov 90 VERTICAL, horizon on row 42 --
  `docs/SIM_TRANSFER_SPEC.md`), not the scenery.

Usage:
  python cad/track_layout_v2.py                 # verify + write the SVG plan
  python cad/track_layout_v2.py --self-check
  python cad/track_layout_v2.py --radius 0.55   # what B3 might do to it
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

FLOOR = 3.000          # m   CONFIRMED by Evan 2026-09-01
WALL_MARGIN = 0.100    # m                                          EST
CAR_WIDTH = 0.11475    # m   MEASURED 2026-09-02 (Appendix BL): rear tire track,
                       #     the widest point. Front is 107.75 mm. Supersedes the
                       #     0.130 ESTIMATE this file used until then.
                       #     CAVEAT: tire track, not whole-vehicle width -- the
                       #     assembled car (chassis, electronics stack, camera
                       #     mount) has never been measured and may be wider.
LANE = 2.0 * CAR_WIDTH  # m  lane width rule, SIM_TRANSFER_SPEC section 3
R_NOM = 0.500          # m   FROZEN band 500-670; only 500 fits a 3x3 grid
STREETS = 3            # per axis


MAX_STRAIGHT = 0.200   # m  cap on the straight run between corners     EST


def grid_pitch(R: float, lane: float, straight: float) -> float:
    """Street spacing: two arcs plus whatever straight street runs between.

    Driving east and turning north, the arc is tangent to both centrelines and
    consumes R BEFORE the corner and R AFTER it. Two consecutive corners a
    pitch apart therefore need `pitch - 2R >= 0`.

    **The lane width is NOT part of this** -- parallel streets only need
    `pitch >= lane` so their surfaces do not overlap, and 2R (>= 1000 mm) already
    dwarfs lane (260 mm). v1 of this file used `2R + lane`, over-constraining
    the pitch by a full 260 mm, which is what produced the false claim that a
    3x3 grid fits ONLY at R = 500 mm. It fits at 500, 550 and 600 (Appendix AY).
    """
    return 2 * R + straight


def best_straight(R: float, lane: float, streets: int) -> float:
    """Largest straight run between corners that still fits the floor, capped.

    Evan 2026-09-01: "the loop can be smaller, smaller is probably better."
    Smaller buys margin against BOTH unmeasured numbers -- B3's turning radius
    and B2's car width -- so this takes the largest straight up to a cap rather
    than the largest that fits, and returns 0 when even tangent corners are too
    big.
    """
    usable = FLOOR - 2 * WALL_MARGIN
    s = (usable - lane) / (streets - 1) - 2 * R
    return max(0.0, min(MAX_STRAIGHT, s))


def check_fits(R: float, lane: float, streets: int, straight: float = None):
    if straight is None:
        straight = best_straight(R, lane, streets)
    pitch = grid_pitch(R, lane, straight)
    span = (streets - 1) * pitch + lane
    return pitch, span, span <= FLOOR - 2 * WALL_MARGIN + 1e-9


def round_polyline(verts, R: float, per: int = 40):
    """Close a polyline of axis-aligned moves, rounding each 90-degree turn.

    A vertex whose incoming and outgoing headings MATCH is passed straight
    through and gets no arc -- that is what lets the route cross itself at an
    intersection. The first cut of this instead built two rounded rectangles on
    diagonally opposite blocks and assumed they met at the shared corner. They
    do not: rounding pulls each path R*(sqrt(2)-1) ~ 207 mm clear of the corner,
    so it produced two SEPARATE loops with no way to drive between them.
    """
    V = [np.asarray(v, float) for v in verts]
    n = len(V)
    out = []
    for i in range(n):
        prev, cur, nxt = V[(i - 1) % n], V[i], V[(i + 1) % n]
        din = cur - prev
        dout = nxt - cur
        din = din / max(np.linalg.norm(din), 1e-12)
        dout = dout / max(np.linalg.norm(dout), 1e-12)
        cross = din[0] * dout[1] - din[1] * dout[0]
        if abs(cross) < 1e-9:                     # straight through
            out.append(cur[None, :])
            continue
        if min(np.linalg.norm(cur - prev), np.linalg.norm(nxt - cur)) < R - 1e-9:
            raise ValueError(
                f"corner radius {R * 1000:.0f} mm does not fit the "
                f"{min(np.linalg.norm(cur - prev), np.linalg.norm(nxt - cur)) * 1000:.0f} mm leg")
        start = cur - din * R                      # tangent points
        end = cur + dout * R
        centre = start + np.array([-din[1], din[0]]) * R * np.sign(cross)
        a0 = math.atan2(*(start - centre)[::-1])
        a1 = math.atan2(*(end - centre)[::-1])
        if cross > 0:
            while a1 <= a0: a1 += 2 * math.pi
        else:
            while a1 >= a0: a1 -= 2 * math.pi
        a = np.linspace(a0, a1, per)
        out.append(centre + R * np.stack([np.cos(a), np.sin(a)], axis=1))
    # stitch: straight run from each piece's end to the next piece's start
    pts = []
    for i, piece in enumerate(out):
        pts.append(piece)
        nxt = out[(i + 1) % len(out)][0]
        seg = nxt - piece[-1]
        L = float(np.linalg.norm(seg))
        if L > 1e-9:
            m = max(2, int(L / 0.005))
            # [1:-1]: both endpoints duplicate a neighbouring piece's vertex,
            # and a zero-length segment makes arctan2(0, 0) fabricate a heading
            # that reads as a pi cusp in an otherwise smooth path.
            pts.append(np.stack([np.linspace(piece[-1][0], nxt[0], m),
                                 np.linspace(piece[-1][1], nxt[1], m)],
                                axis=1)[1:-1])
    return np.concatenate(pts)


def build(R: float = R_NOM, lane: float = LANE, streets: int = STREETS,
          straight: float = None):
    if straight is None:
        straight = best_straight(R, lane, streets)
    pitch, span, ok = check_fits(R, lane, streets, straight)
    if not ok:
        raise SystemExit(
            f"a {streets}x{streets} street grid does NOT fit: pitch "
            f"{pitch * 1000:.0f} mm gives a span of {span * 1000:.0f} mm against "
            f"{(FLOOR - 2 * WALL_MARGIN) * 1000:.0f} mm usable. This is the "
            f"documented failure mode: even TANGENT corners (no straight street "
            f"between them) do not fit at this radius. There is no smaller-city "
            f"fallback -- a 2x2 grid cannot carry a figure-8 -- so the fallback "
            f"is v1's non-grid figure-8 (cad/track_layout_v1.py).")
    if streets < 3:
        raise SystemExit(
            f"a {streets}x{streets} grid cannot carry this route. The figure-8 "
            f"needs a CENTRE street to cross on plus outer streets on BOTH "
            f"sides, i.e. 3 per axis. With 2 streets the only closed circuit is "
            f"a single perimeter loop -- every turn the same way, which is the "
            f"oval `gotchas.md` bans because it teaches 'always steer left'. "
            f"So if B3 puts the radius above 500 mm you do not get a smaller "
            f"city: you get no grid route at all, and the fallback is v1's "
            f"non-grid figure-8 (cad/track_layout_v1.py).")
    p = pitch
    # ONE closed route that crosses itself at the centre intersection. Read it
    # as: loop the top-left block with three LEFTS, pass STRAIGHT through the
    # centre, loop the bottom-right block with three RIGHTS, pass straight
    # through again. Balanced turns, and a genuine level crossing.
    verts = [(0, 0), (0, p), (-p, p), (-p, 0),      # 3 lefts
             (0, 0), (p, 0), (p, -p), (0, -p)]      # 3 rights
    route = round_polyline(verts, R)
    streets_xy = [(-pitch + i * pitch) for i in range(streets)]
    return {"pitch": pitch, "span": span, "R": R, "lane": lane,
            "straight": straight,
            "route": route, "verts": verts, "street_coords": streets_xy,
            "intersections": [(x, y) for x in streets_xy for y in streets_xy]}


def curvature(pts: np.ndarray) -> np.ndarray:
    p0, p2 = np.roll(pts, 1, axis=0), np.roll(pts, -1, axis=0)
    a = np.linalg.norm(pts - p0, axis=1)
    b = np.linalg.norm(p2 - pts, axis=1)
    c = np.linalg.norm(p2 - p0, axis=1)
    cross = ((pts - p0)[:, 0] * (p2 - pts)[:, 1]
             - (pts - p0)[:, 1] * (p2 - pts)[:, 0])
    den = a * b * c
    return np.where(den > 1e-12, 2 * cross / np.maximum(den, 1e-12), 0.0)


def path_len(p: np.ndarray) -> float:
    return float(np.linalg.norm(np.diff(p, axis=0, append=p[:1]), axis=1).sum())


# ---- the hybrid print plan ------------------------------------------------
# Evan's call 2026-09-01: NOT 225 full panels (12-13 kg at 3 mm with real
# infill, 169-900 h, 225 bed clears, 28 camera-visible seams). Print only the
# geometry that must be exact -- the corner arcs and the intersection boxes --
# as MARKING tiles, and lay them on a flat board.
MARK_W = 0.025         # m   painted/printed line width                EST
MARK_T = 0.002         # m   tile thickness                            EST
PLA_DENSITY = 1.24     # g/cm^3
INFILL_SOLID_FRAC = 1.0  # a 2 mm marking tile is all skin -- no sparse middle


def print_plan(g):
    R, lane, pitch = g["R"], g["lane"], g["pitch"]
    # corner arcs actually driven: 4 per lobe, 2 lobes
    arc_len = 2 * 4 * (math.pi / 2 * R)
    # intersection boxes: outline of a lane x lane square, 9 of them
    box_len = 9 * 4 * lane
    # street edge + centre lines for the whole grid, both axes
    street_len = 2 * len(g["street_coords"]) * g["span"] * 2   # 2 edge lines
    # ONLY the arcs and the intersection boxes are printed. The straight street
    # lines are tape or paint on the board -- billing filament for them is what
    # the first cut did, and it turned a 0.5 kg hybrid into a 3.0 kg one on
    # paper. (It also shows why gotchas.md's 0.15 kg figure does not carry over:
    # that was a MINIMUM LOOP, not 50 m of city grid lines.)
    def grams_for(metres):
        vol_mm3 = metres * 1000 * (MARK_W * 1000) * (MARK_T * 1000)
        return vol_mm3 / 1000.0 * PLA_DENSITY * INFILL_SOLID_FRAC

    printed_len = arc_len + box_len
    tiles = math.ceil(printed_len / 0.200)
    return {"arc_len_m": arc_len, "box_len_m": box_len,
            "street_line_len_m": street_len,
            "total_line_m": arc_len + box_len + street_len,
            "filament_g": grams_for(printed_len),
            "filament_g_if_all_lines_printed": grams_for(
                arc_len + box_len + street_len),
            "printed_tiles_200mm": tiles, "printed_len_m": printed_len}


def self_check() -> None:
    g = build()
    # 1. the grid fits, and only just
    assert g["span"] <= FLOOR - 2 * WALL_MARGIN, g["span"]
    # NOT "span > 2.7": that encoded the over-constrained pitch and asserted the
    # loop was BIG. Smaller is the goal (Evan, 2026-09-01). The real floor is
    # geometric -- the grid must not collapse below tangent corners.
    assert g["span"] >= 2 * (2 * g["R"]) + g["lane"] - 1e-9, \
        f"span {g['span']:.3f} is below tangent corners - grid is degenerate"
    assert g["straight"] >= 0.0, g["straight"]

    # 2. the CORRECTED pitch (2R, not 2R+lane) fits most of the frozen band.
    #    500/550/600 build; only 670 is out of reach even with tangent corners.
    for ok_R in (0.500, 0.550, 0.600):
        gg = build(R=ok_R)
        assert gg["span"] <= FLOOR - 2 * WALL_MARGIN + 1e-9, (ok_R, gg["span"])
    try:
        build(R=0.670)
    except SystemExit:
        pass
    else:
        raise AssertionError("R=670 should not fit a 3x3 grid")
    # "Smaller is better" cannot mean "a bigger radius gives a smaller loop" --
    # a bigger turning circle FORCES a bigger loop, and at R=600 the straight is
    # already squeezed to 70 mm. What it does mean: at the small end the cap
    # binds, so the layout leaves real margin instead of spending the whole
    # floor. That margin is the defence against B2 and B3 both landing badly.
    assert build(R=0.500)["span"] <= FLOOR - 2 * WALL_MARGIN - 0.100, \
        "at R=500 the layout should leave >=100 mm spare, not fill the floor"
    assert grid_pitch(0.6, LANE, 0.0) > grid_pitch(0.5, LANE, 0.0), \
        "pitch must grow with radius"

    # 2b. the pitch formula itself: 2R + straight, with NO lane term. Getting
    #     this wrong by one lane width is what produced the false "fits only at
    #     R=500" claim (Appendix AY).
    assert abs(grid_pitch(0.5, 0.26, 0.1) - 1.1) < 1e-9, grid_pitch(0.5, 0.26, 0.1)
    assert abs(grid_pitch(0.5, 0.99, 0.1) - 1.1) < 1e-9, "lane must not affect pitch"

    # 3. ONE closed route, min radius respected, NO cusps
    r = g["route"]
    assert np.linalg.norm(r[0] - r[-1]) < 0.05, "route not closed"
    k = np.abs(curvature(r))
    rmin = 1.0 / k[k > 1e-6].max()
    assert rmin > g["R"] * 0.9, f"min radius {rmin:.3f} < R {g['R']}"
    v = np.diff(r, axis=0, append=r[:1])
    ang = np.arctan2(v[:, 1], v[:, 0])
    d = np.abs(np.diff(ang, append=ang[:1]))
    d = np.minimum(d, 2 * np.pi - d)
    assert d.max() < 0.25, f"cusp: heading jumps {d.max():.3f} rad"

    # 4. BOTH turn directions, and BALANCED -- an oval teaches "always left"
    ks = curvature(r)
    left = float(ks[ks > 1e-6].sum())
    right = float(-ks[ks < -1e-6].sum())
    assert left > 0 and right > 0, f"not both-handed: L={left:.1f} R={right:.1f}"
    assert abs(left - right) / max(left, right) < 0.05,         f"turn directions unbalanced: L={left:.1f} R={right:.1f}"

    # 5. the road, not the centreline, stays inside the usable floor
    ext = np.abs(r).max() + g["lane"] / 2
    assert 2 * ext <= FLOOR - 2 * WALL_MARGIN + 1e-9, f"road bbox {2 * ext:.3f} m"

    # 6. the route really does CROSS at the centre intersection -- it must pass
    #    through the origin twice, on perpendicular headings. Two loops that
    #    merely touch a shared block corner are not a figure-8 (and rounding
    #    means they do not even touch).
    near = np.where(np.linalg.norm(r, axis=1) < 0.03)[0]
    assert len(near) > 0, "route never reaches the centre intersection"
    hd = v[near] / np.linalg.norm(v[near], axis=1, keepdims=True)
    assert float(np.abs(hd @ hd[0]).min()) < 0.1,         "route passes the centre only on one heading - no crossing"

    # 6b. every route vertex sits on a real street of the grid. The 2x2
    #     fallback silently emitted a route at +-pitch when the grid only had
    #     streets at -pitch and 0 -- an off-grid path that looked fine in the
    #     summary line.
    sc = [round(c, 6) for c in g["street_coords"]]
    for vx, vy in g["verts"]:
        assert round(vx, 6) in sc and round(vy, 6) in sc,             f"route vertex ({vx}, {vy}) is not on a street of {sc}"

    # 6c. a 2x2 grid must REFUSE, not emit an oval or an off-grid path
    try:
        build(R=0.550, streets=2)
    except SystemExit:
        pass
    else:
        raise AssertionError("a 2x2 grid should refuse this route")

    # 7. straights survive between corners: pitch - 2R must stay positive
    assert g["pitch"] - 2 * g["R"] > 0, "corners would overlap"

    # 8. the print plan is a real reduction, not a relabelling
    pp = print_plan(g)
    assert pp["filament_g"] < 2000, f"{pp['filament_g']:.0f} g is not a hybrid"
    print("track_layout_v2 self_check: PASS")


def svg(g, out: Path) -> None:
    S, pad = 300.0, 40.0
    W = FLOOR * S + 2 * pad
    X = lambda x: pad + (x + FLOOR / 2) * S
    Y = lambda y: pad + (FLOOR / 2 - y) * S
    usable = FLOOR - 2 * WALL_MARGIN
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{W:.0f}" '
         f'viewBox="0 0 {W:.0f} {W:.0f}">',
         f'<rect width="{W:.0f}" height="{W:.0f}" fill="#f7f6f3"/>',
         f'<rect x="{X(-FLOOR/2):.1f}" y="{Y(FLOOR/2):.1f}" width="{FLOOR*S:.1f}" '
         f'height="{FLOOR*S:.1f}" fill="#fff" stroke="#333" stroke-width="2"/>',
         f'<rect x="{X(-usable/2):.1f}" y="{Y(usable/2):.1f}" width="{usable*S:.1f}" '
         f'height="{usable*S:.1f}" fill="none" stroke="#ccc" stroke-dasharray="6 5"/>']
    # every street of the grid, in pale grey: the CITY
    for c in g["street_coords"]:
        p.append(f'<line x1="{X(-g["span"]/2):.1f}" y1="{Y(c):.1f}" '
                 f'x2="{X(g["span"]/2):.1f}" y2="{Y(c):.1f}" stroke="#d8d5d0" '
                 f'stroke-width="{g["lane"]*S:.1f}" stroke-linecap="butt"/>')
        p.append(f'<line x1="{X(c):.1f}" y1="{Y(-g["span"]/2):.1f}" '
                 f'x2="{X(c):.1f}" y2="{Y(g["span"]/2):.1f}" stroke="#d8d5d0" '
                 f'stroke-width="{g["lane"]*S:.1f}" stroke-linecap="butt"/>')
    # the DRIVEN route on top
    d = " ".join(f"{'M' if i == 0 else 'L'}{X(q[0]):.1f},{Y(q[1]):.1f}"
                 for i, q in enumerate(g["route"])) + " Z"
    p.append(f'<path d="{d}" fill="none" stroke="#5a5a5a" '
             f'stroke-width="{g["lane"]*S:.1f}" stroke-linecap="round"/>')
    p.append(f'<path d="{d}" fill="none" stroke="#f2c200" stroke-width="2.5" '
             f'stroke-dasharray="14 7"/>')
    for (ix, iy) in g["intersections"]:
        p.append(f'<rect x="{X(ix-g["lane"]/2):.1f}" y="{Y(iy+g["lane"]/2):.1f}" '
                 f'width="{g["lane"]*S:.1f}" height="{g["lane"]*S:.1f}" '
                 f'fill="none" stroke="#1f6feb" stroke-width="1.5" '
                 f'stroke-dasharray="4 3"/>')
    p.append(f'<text x="{X(0):.1f}" y="{Y(FLOOR/2)-14:.1f}" text-anchor="middle" '
             f'font-family="sans-serif" font-size="17" font-weight="bold">'
             f'Track v2 &#8212; 3&#215;3 city grid, figure-8 route, 3.00 &#215; 3.00 m</text>')
    pp = print_plan(g)
    for i, ln in enumerate([
        f'street pitch {g["pitch"]*1000:.0f} mm, span {g["span"]*1000:.0f} mm of '
        f'{usable*1000:.0f} usable &#8212; {(usable-g["span"])*1000:.0f} mm SPARE',
        f'corner radius {g["R"]*1000:.0f} mm &#8212; ONLY 500 mm fits a 3&#215;3 grid; '
        f'B3 above 500 leaves a 2&#215;2 plus sign',
        f'9 intersections, 4 blocks, driven as a figure-8 (both turn directions, '
        f'level crossing at centre)',
        f'HYBRID print: {pp["printed_tiles_200mm"]} marking tiles for arcs + '
        f'intersection boxes, ~{pp["filament_g"]:.0f} g &#8212; NOT 225 panels',
    ]):
        p.append(f'<text x="{pad:.1f}" y="{W-pad+4+i*15:.1f}" '
                 f'font-family="sans-serif" font-size="12" fill="#444">{ln}</text>')
    p.append("</svg>")
    out.write_text("\n".join(p), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--radius", type=float, default=R_NOM)
    ap.add_argument("--car-width", type=float, default=CAR_WIDTH,
                    help="metres; lane = 2x this. --radius already existed for "
                         "the frozen number, this is the other one")
    ap.add_argument("--streets", type=int, default=STREETS)
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--out", default=str(REPO / "cad"))
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0
    self_check()

    g = build(R=args.radius, lane=2.0 * args.car_width, streets=args.streets)
    pp = print_plan(g)
    usable = FLOOR - 2 * WALL_MARGIN
    route = path_len(g["route"])
    print(f"floor           {FLOOR:.3f} x {FLOOR:.3f} m (usable {usable:.3f})")
    print(f"car width       {args.car_width*1000:.2f} mm  MEASURED 2026-09-02 "
          f"(tire track, not whole-vehicle)")
    print(f"lane width      {g['lane']*1000:.0f} mm")
    print(f"corner radius   {g['R']*1000:.0f} mm  NOT COMMITTED until B3")
    print(f"street pitch    {g['pitch']*1000:.0f} mm  "
          f"(straight between corners {(g['pitch']-2*g['R'])*1000:.0f} mm)")
    print(f"grid            {args.streets}x{args.streets} streets, "
          f"{(args.streets-1)**2} blocks, {args.streets**2} intersections")
    print(f"span            {g['span']*1000:.0f} mm of {usable*1000:.0f} usable "
          f"-> {(usable-g['span'])*1000:.0f} mm SPARE")
    print(f"driven route    figure-8 through the centre intersection, "
          f"{route:.2f} m, 3 lefts + 3 rights (balanced)")
    print(f"\nHYBRID PRINT PLAN (Evan's call: not 225 panels)")
    print(f"  corner arcs        {pp['arc_len_m']:.2f} m")
    print(f"  intersection boxes {pp['box_len_m']:.2f} m")
    print(f"  -> printed tiles   {pp['printed_tiles_200mm']} at 200 mm, "
          f"~{pp['filament_g']:.0f} g of filament")
    print(f"  street lines       {pp['street_line_len_m']:.2f} m -> TAPE or paint "
          f"on the board, not printed")
    print(f"  (printing every line instead would be "
          f"~{pp['filament_g_if_all_lines_printed']:.0f} g; printing 225 solid "
          f"panels was ~12,600 g)")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    svg(g, out / "track_layout_v2.svg")
    (out / "track_layout_v2.json").write_text(json.dumps({
        "floor_m": FLOOR, "car_width_m_ESTIMATE": CAR_WIDTH,
        "lane_width_m": g["lane"], "corner_radius_m_NOT_COMMITTED": g["R"],
        "street_pitch_m": g["pitch"], "span_m": g["span"],
        "streets_per_axis": args.streets,
        "blocks": (args.streets - 1) ** 2, "intersections": args.streets ** 2,
        "route_len_m": route, "route": "figure-8: 3 lefts round the top-left block, straight through the centre, 3 rights round the bottom-right block",
        "print_plan": pp,
        "RISK": "3x3 fits ONLY at R=500mm, the optimistic end of the frozen "
                "500-670mm band. B3 above 500mm leaves a 2x2 grid.",
    }, indent=2), encoding="utf-8")
    print(f"-> {out / 'track_layout_v2.svg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
