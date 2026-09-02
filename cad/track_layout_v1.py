"""Figure-8 track plan for a 3.0 x 3.0 m floor, with destinations and a bridge.

**NOTHING HERE IS COMMITTED GEOMETRY.** Corner radius is FROZEN until the B3
turning test (Appendix L, AM.2): the ~330 mm minimum turn radius is
`wheelbase / tan(max steer)` on an UNMEASURED 130 mm car width, and the
500-670 mm centreline figure derived from it is an estimate on an estimate.
This script parameterises the layout so the plan can be re-cut the day B3
produces a real number. Do not cut corner tiles from it.

WHY THIS SHAPE AND NOT A TWISTY ONE (Appendix AT)
  "Twisty" means many tight curves, and the tightest curve allowed here is
  already about half the room. At the frozen minimum radius only 1.75-2.33
  180-degree hairpins fit across the WHOLE 2.8 m of usable floor, and only
  1.04-1.40 full S-bends. At R = 670 mm even a plain figure-8 does not fit
  (3.01-3.07 m against 2.80 m usable). The figure-8 is therefore not a
  conservative choice, it is close to the only one -- and `gotchas.md` already
  mandates it over an oval, because an oval teaches "always steer left".

WHY THE BRIDGE IS FLAT (Appendix AT)
  A real overpass needs the car to climb over itself. Three constraints close
  on each other and leave no room:
    * torque caps the climbable grade near 9-15% for a 0.6-1.0 kg car, before
      rolling resistance and Lego diff losses are counted;
    * at 10% a 100 mm-tall car needs 2.77 m of ramp -- 92% of the floor, before
      a single corner;
    * a 10% grade moves the image horizon 6 px, which is 21 standard deviations
      outside the flat-ground training corpus (sd 0.284 px, Appendix AR).
  So the bridge here is a FLAT CAUSEWAY: a deck at floor level with parapets
  and a void either side. Zero grade, zero projection change, and the parapets
  add strong near-lane vertical features the open-desert corpus entirely lacks.

WHY THE DESTINATIONS ARE LANDMARKS, NOT ROUTING TARGETS (Appendix AT)
  A behaviourally-cloned lane-follower has no goal input, so it cannot CHOOSE
  at a junction. Spur roads to five destinations would create five junctions
  the policy is architecturally unable to handle. These five are landmarks
  BESIDE the loop -- visual diversity and localisation targets that cost the
  policy nothing. Goal-conditioned routing is a separate, later question.

Usage:
  python cad/track_layout_v1.py                 # verify + write the SVG plan
  python cad/track_layout_v1.py --self-check    # geometry checks only
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

# ---- inputs. Every one of these is an ESTIMATE except the floor. ----------
FLOOR = 3.000          # m   CONFIRMED by Evan 2026-09-01
WALL_MARGIN = 0.100    # m   keep the track off the skirting        EST
CAR_WIDTH = 0.130      # m   UNMEASURED -- set by the Lego rack + diff at B2
LANE = 2.0 * CAR_WIDTH  # m  lane width rule, SIM_TRANSFER_SPEC section 3
R_NOM = 0.550          # m   centreline corner radius, inside the frozen
                       #     500-670 mm band and chosen so the bbox fits
BRIDGE_LEN = 0.350     # m   deck long enough to read as a bridge next to a
                       #     ~130 mm car                              EST
BRIDGE_PARAPET = 0.025  # m  parapet thickness each side              EST


def place_bridge(pts: np.ndarray, lane: float, deck_len: float = BRIDGE_LEN):
    """Longest-clearance contiguous run of centreline that can carry the deck.

    The deck plus its parapets must not overlap ANY other part of the track.
    That rules out the crossing straights outright: the two of them meet at
    ~80 deg, so a deck on one sits on the other unless it starts 294 mm from
    the crossing, leaving only 171 mm of clear run against a 350 mm deck. The
    search finds a lobe arc instead -- a flat deck on a 550 mm curve, which is
    still a flat deck.
    """
    seglen = np.linalg.norm(np.diff(pts, axis=0, append=pts[:1]), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seglen)[:-1]])
    total = s[-1] + seglen[-1]
    n = len(pts)
    half_w = lane / 2 + BRIDGE_PARAPET
    need = half_w + lane / 2 + 0.02          # deck half + road half + margin
    span_i = max(2, int(round(deck_len / total * n)))
    best = None
    for i in range(0, n, max(1, n // 360)):
        idx = (np.arange(i, i + span_i)) % n
        deck = pts[idx]
        # distance from every deck point to every NON-adjacent track point
        keep = np.ones(n, bool)
        keep[(np.arange(i - span_i, i + 2 * span_i)) % n] = False
        if not keep.any():
            continue
        dmin = float(np.linalg.norm(
            deck[:, None, :] - pts[None, keep, :], axis=2).min())
        if dmin < need:
            continue
        if best is None or dmin > best[0]:
            best = (dmin, idx)
    if best is None:
        raise SystemExit(
            f"no {deck_len * 1000:.0f} mm run of track can carry a bridge deck "
            f"with {need * 1000:.0f} mm clearance. Shorten the deck or open the "
            f"layout out.")
    return best[1], best[0], total


def figure8(R: float, d: float, n: int = 2000):
    """Centreline of a figure-8: two circles of radius R, centres d apart on
    the y axis, joined by their two internal tangents (which cross at origin).

    Returns (points, curvature_sign, straight_spans). A tangent line through
    the origin at angle t to the x axis is distance (d/2)|cos t| from either
    centre, so tangency requires cos(t) = 2R/d -- and therefore d > 2R.
    """
    if d <= 2 * R:
        raise ValueError(f"d={d} must exceed 2R={2 * R} for the tangents to exist")
    t = math.acos(2 * R / d)
    C1, C2 = np.array([0.0, d / 2]), np.array([0.0, -d / 2])

    def tangent_point(C, ang):
        u = np.array([math.cos(ang), math.sin(ang)])
        return (C @ u) * u

    # the four tangent points, one per (circle, line) pair
    P1a, P1b = tangent_point(C1, t), tangent_point(C1, -t)
    P2a, P2b = tangent_point(C2, t), tangent_point(C2, -t)

    def arc(C, start, end, sign, m):
        a0 = math.atan2(*(start - C)[::-1])
        a1 = math.atan2(*(end - C)[::-1])
        if sign > 0:
            while a1 <= a0:
                a1 += 2 * math.pi
        else:
            while a1 >= a0:
                a1 -= 2 * math.pi
        a = np.linspace(a0, a1, m)
        return C + R * np.stack([np.cos(a), np.sin(a)], axis=1)

    def seg(A, B, m):
        s = np.linspace(0, 1, m)[:, None]
        return A + (B - A) * s

    def arc_matching(C, start, end, exit_dir, m):
        """The sweep direction whose EXIT tangent matches `exit_dir`.

        Choosing the sign by hand is how the first cut of this produced four
        cusps: the two tangent points of one straight must come from the SAME
        tangent line, and the arc between them must leave in the direction that
        straight departs. Picking it by measurement cannot get that backwards.
        """
        best = None
        for sign in (+1, -1):
            a = arc(C, start, end, sign, m)
            v = a[-1] - a[-2]
            v = v / max(np.linalg.norm(v), 1e-12)
            err = float(np.linalg.norm(v - exit_dir))
            if best is None or err < best[0]:
                best = (err, a)
        return best[1]

    def unit(v):
        return v / max(np.linalg.norm(v), 1e-12)

    # The +t line touches BOTH circles: C1 at P1a and C2 at P2a. Those two are
    # one straight. The -t line gives the other, P2b -> P1b.
    m_arc, m_seg = n // 3, n // 6
    top = arc_matching(C1, P1b, P1a, unit(P2a - P1a), m_arc)
    down = seg(P1a, P2a, m_seg)                 # straight, through the crossing
    bot = arc_matching(C2, P2a, P2b, unit(P1b - P2b), m_arc)
    up = seg(P2b, P1b, m_seg)
    pts = np.concatenate([top, down[1:], bot[1:], up[1:-1]])
    spans = [float(np.linalg.norm(P1a - P2a)), float(np.linalg.norm(P2b - P1b))]
    return pts, spans, (P1a, P2a, P2b, P1b)


def curvature(pts: np.ndarray) -> np.ndarray:
    """Signed curvature of a closed polyline, by circumscribed circle."""
    p0 = np.roll(pts, 1, axis=0)
    p2 = np.roll(pts, -1, axis=0)
    a = np.linalg.norm(pts - p0, axis=1)
    b = np.linalg.norm(p2 - pts, axis=1)
    c = np.linalg.norm(p2 - p0, axis=1)
    cross = ((pts - p0)[:, 0] * (p2 - pts)[:, 1]
             - (pts - p0)[:, 1] * (p2 - pts)[:, 0])
    area2 = cross
    denom = a * b * c
    return np.where(denom > 1e-12, 2 * area2 / np.maximum(denom, 1e-12), 0.0)


def pick_d(R: float, lane: float, usable: float) -> float:
    """Largest lobe separation whose bounding box still fits the floor.

    Bigger d means longer crossing straights (room for the bridge deck) and a
    taller bounding box, so this takes the biggest d the floor allows.
    """
    d = usable - 2 * R - lane
    if d <= 2 * R:
        raise SystemExit(
            f"no figure-8 fits: R={R * 1000:.0f} mm and lane={lane * 1000:.0f} mm "
            f"need d>{2 * R * 1000:.0f} mm but the floor allows only "
            f"{d * 1000:.0f} mm. Reduce R (frozen until B3) or the lane width.")
    return d


def build():
    usable = FLOOR - 2 * WALL_MARGIN
    d = pick_d(R_NOM, LANE, usable)
    pts, spans, tps = figure8(R_NOM, d)
    return pts, spans, tps, d, usable


# ---- destinations: LANDMARKS beside the loop, never spur junctions --------
DESTINATIONS = [
    ("D1  school",      0.06),
    ("D2  market",      0.19),
    ("D3  depot",       0.34),
    ("D4  station",     0.60),
    ("D5  park",        0.78),
]


def place_destinations(pts: np.ndarray, lane: float, offset: float = 0.16):
    """One landmark per fraction of arc length, set back from the road edge.

    The road already fills the usable floor, so the OUTWARD normal often leaves
    the room. Both sides are tried and the one that stays inside the floor with
    the most clearance from the road wins -- in practice that is usually the
    empty interior of a lobe.
    """
    seglen = np.linalg.norm(np.diff(pts, axis=0, append=pts[:1]), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seglen)[:-1]])
    total = s[-1] + seglen[-1]
    lim = FLOOR / 2 - 0.05          # keep the marker off the wall
    out = []
    for name, frac in DESTINATIONS:
        i = int(np.searchsorted(s, frac * total)) % len(pts)
        tang = pts[(i + 5) % len(pts)] - pts[(i - 5) % len(pts)]
        nrm = np.array([-tang[1], tang[0]])
        nrm = nrm / max(np.linalg.norm(nrm), 1e-9)
        best = None
        for sgn in (+1, -1):
            p = pts[i] + sgn * nrm * (lane / 2 + offset)
            if np.abs(p).max() > lim:
                continue                       # outside the room
            clear = float(np.linalg.norm(pts - p, axis=1).min()) - lane / 2
            if best is None or clear > best[0]:
                best = (clear, p)
        if best is None:
            raise SystemExit(
                f"{name}: neither side of the road at arc fraction {frac} fits "
                f"inside the {FLOOR:.1f} m floor. Reduce the landmark offset or "
                f"the lane width.")
        out.append((name, best[1], pts[i]))
    return out, total


def self_check() -> None:
    pts, spans, tps, d, usable = build()

    # 1. closed loop
    gap = float(np.linalg.norm(pts[0] - pts[-1]))
    assert gap < 0.02, f"path is not closed: {gap * 1000:.1f} mm gap"

    # 2. NO CUSPS. The car cannot drive a heading discontinuity, and a kink is
    #    invisible to a min-radius check that samples curvature pointwise --
    #    the first cut of this had four of them, one per tangent point.
    v = np.diff(pts, axis=0, append=pts[:1])
    ang = np.arctan2(v[:, 1], v[:, 0])
    dang = np.abs(np.diff(ang, append=ang[:1]))
    dang = np.minimum(dang, 2 * np.pi - dang)
    assert dang.max() < 0.05, (
        f"heading jumps {dang.max():.3f} rad at index {int(dang.argmax())} "
        f"-- the path has a cusp")

    # 3. minimum radius is respected everywhere (straights read as zero curvature)
    k = np.abs(curvature(pts))
    rmin = 1.0 / k[k > 1e-6].max()
    assert rmin > R_NOM * 0.95, f"min radius {rmin * 1000:.0f} mm < R {R_NOM * 1000:.0f} mm"

    # 3. BOTH turn directions present -- the whole reason for a figure-8
    ks = curvature(pts)
    left = (ks > 1e-6).sum()
    right = (ks < -1e-6).sum()
    assert left > 100 and right > 100, f"not both-handed: L={left} R={right}"

    # 4. the road, not just the centreline, fits inside the usable floor
    half = LANE / 2
    ext = np.abs(pts).max(axis=0) + half
    assert (2 * ext <= usable + 1e-9).all(), \
        f"road bbox {2 * ext * 1000} mm exceeds usable {usable * 1000:.0f} mm"

    # 5. the bridge deck actually fits somewhere, clear of every other part
    #    of the track. A deck on a crossing straight overlaps the OTHER
    #    straight -- the first cut of this drew exactly that.
    idx, clear, _ = place_bridge(pts, LANE)
    assert clear >= LANE / 2 + BRIDGE_PARAPET + LANE / 2, \
        f"bridge deck clears only {clear * 1000:.0f} mm"
    deck = pts[idx]
    run = float(np.linalg.norm(np.diff(deck, axis=0), axis=1).sum())
    assert run >= BRIDGE_LEN * 0.9, f"deck run only {run * 1000:.0f} mm"
    # and it must NOT have landed on a crossing straight: check it is curved
    kd = np.abs(curvature(deck))[2:-2]
    assert kd.mean() > 0.5 / R_NOM, "deck landed on a straight"

    # 6. five destinations, all inside the room
    dests, _ = place_destinations(pts, LANE)
    assert len(dests) == 5, len(dests)
    for name, p, _ in dests:
        assert np.abs(p).max() <= FLOOR / 2, f"{name} lands outside the room"
        # a landmark ON the road is an obstacle, not a landmark
        clear = float(np.linalg.norm(pts - p, axis=1).min()) - LANE / 2
        assert clear > 0.02, f"{name} sits {clear * 1000:.0f} mm from the road edge"

    # 7. the geometry helper refuses an impossible request rather than guessing
    try:
        figure8(0.6, 1.1)
    except ValueError:
        pass
    else:
        raise AssertionError("figure8 accepted d <= 2R")

    print("track_layout_v1 self_check: PASS")


def svg(pts, spans, tps, d, usable, out: Path) -> None:
    S = 300.0                      # px per metre
    pad = 40.0
    W = FLOOR * S + 2 * pad
    half = LANE / 2

    def X(x): return pad + (x + FLOOR / 2) * S
    def Y(y): return pad + (FLOOR / 2 - y) * S

    dests, total = place_destinations(pts, LANE)
    path = " ".join(f"{'M' if i == 0 else 'L'}{X(p[0]):.1f},{Y(p[1]):.1f}"
                    for i, p in enumerate(pts)) + " Z"
    bidx, bclear, _ = place_bridge(pts, LANE)
    bdeck = pts[bidx]
    A, B = bdeck[0], bdeck[-1]
    deck_path = " ".join(f"{'M' if i == 0 else 'L'}{X(q[0]):.1f},{Y(q[1]):.1f}"
                         for i, q in enumerate(bdeck))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{W:.0f}" '
        f'viewBox="0 0 {W:.0f} {W:.0f}">',
        f'<rect width="{W:.0f}" height="{W:.0f}" fill="#f7f6f3"/>',
        # floor + usable envelope
        f'<rect x="{X(-FLOOR/2):.1f}" y="{Y(FLOOR/2):.1f}" width="{FLOOR*S:.1f}" '
        f'height="{FLOOR*S:.1f}" fill="#fff" stroke="#333" stroke-width="2"/>',
        f'<rect x="{X(-usable/2):.1f}" y="{Y(usable/2):.1f}" width="{usable*S:.1f}" '
        f'height="{usable*S:.1f}" fill="none" stroke="#bbb" stroke-dasharray="6 5"/>',
        # road surface, then the centre line
        f'<path d="{path}" fill="none" stroke="#5a5a5a" '
        f'stroke-width="{LANE*S:.1f}" stroke-linecap="round"/>',
        f'<path d="{path}" fill="none" stroke="#f2c200" stroke-width="2.5" '
        f'stroke-dasharray="14 7"/>',
    ]
    # bridge deck
    parts.append(f'<path d="{deck_path}" fill="none" stroke="#8b5a2b" '
                 f'stroke-width="{(LANE+2*BRIDGE_PARAPET)*S:.1f}" '
                 f'stroke-linecap="butt" opacity="0.9"/>')
    parts.append(f'<path d="{deck_path}" fill="none" stroke="#f2c200" '
                 f'stroke-width="2.5" stroke-dasharray="14 7"/>')
    mid = bdeck[len(bdeck) // 2]
    parts.append(
        f'<text x="{X(mid[0]):.1f}" y="{Y(mid[1])-((LANE/2+0.055)*S):.1f}" '
        f'font-family="sans-serif" font-size="15" fill="#3d2b1f" '
        f'text-anchor="middle">BRIDGE &#8212; flat causeway, 0% grade</text>')
    # destinations
    for name, p, anchor in dests:
        parts.append(
            f'<line x1="{X(anchor[0]):.1f}" y1="{Y(anchor[1]):.1f}" '
            f'x2="{X(p[0]):.1f}" y2="{Y(p[1]):.1f}" stroke="#999" '
            f'stroke-width="1" stroke-dasharray="3 3"/>')
        parts.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="13" '
                     f'fill="#1f6feb" opacity="0.9"/>')
        parts.append(f'<text x="{X(p[0]):.1f}" y="{Y(p[1])+4.5:.1f}" fill="#fff" '
                     f'font-family="sans-serif" font-size="12" font-weight="bold" '
                     f'text-anchor="middle">{name.split()[0]}</text>')
        parts.append(f'<text x="{X(p[0])+18:.1f}" y="{Y(p[1])+4.5:.1f}" fill="#333" '
                     f'font-family="sans-serif" font-size="13">'
                     f'{name.split(maxsplit=1)[1]}</text>')
    # dimensions + the honesty banner
    parts.append(f'<text x="{X(0):.1f}" y="{Y(FLOOR/2)-12:.1f}" text-anchor="middle" '
                 f'font-family="sans-serif" font-size="17" font-weight="bold">'
                 f'Figure-8 track plan v1 &#8212; 3.00 &#215; 3.00 m floor</text>')
    lines = [
        f"lane width {LANE*1000:.0f} mm = 2.0 x car width {CAR_WIDTH*1000:.0f} mm (UNMEASURED)",
        f"centreline radius {R_NOM*1000:.0f} mm (FROZEN band 500-670, NOT COMMITTED until B3)",
        f"lobe separation d = {d*1000:.0f} mm   crossing straights {spans[0]*1000:.0f} / {spans[1]*1000:.0f} mm",
        f"centreline length {total:.2f} m   both turn directions   level crossing at centre",
    ]
    for i, ln in enumerate(lines):
        parts.append(f'<text x="{pad:.1f}" y="{W-pad+2+i*15:.1f}" '
                     f'font-family="sans-serif" font-size="12" fill="#444">{ln}</text>')
    parts.append("</svg>")
    out.write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--out", default=str(REPO / "cad"))
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0

    self_check()
    pts, spans, tps, d, usable = build()
    dests, total = place_destinations(pts, LANE)
    k = np.abs(curvature(pts))
    rmin = 1.0 / k[k > 1e-6].max()

    print(f"floor            {FLOOR:.3f} x {FLOOR:.3f} m  (usable {usable:.3f} m)")
    print(f"car width        {CAR_WIDTH*1000:.0f} mm   UNMEASURED, set at B2")
    print(f"lane width       {LANE*1000:.0f} mm   = 2.0 x car width")
    print(f"corner radius    {R_NOM*1000:.0f} mm nominal; measured min on path "
          f"{rmin*1000:.0f} mm   NOT COMMITTED until B3")
    print(f"lobe separation  {d*1000:.0f} mm")
    print(f"crossing straights {spans[0]*1000:.0f} / {spans[1]*1000:.0f} mm")
    print(f"centreline length {total:.3f} m")
    half = LANE / 2
    ext = 2 * (np.abs(pts).max(axis=0) + half)
    print(f"road bounding box {ext[0]*1000:.0f} x {ext[1]*1000:.0f} mm "
          f"inside {usable*1000:.0f} mm usable")
    print("destinations (landmarks beside the loop, NOT spur junctions):")
    for name, p, _ in dests:
        print(f"   {name:14s} at ({p[0]*1000:+7.0f}, {p[1]*1000:+7.0f}) mm")
    bidx, bclear, _ = place_bridge(pts, LANE)
    bdeck = pts[bidx]
    blen = float(np.linalg.norm(np.diff(bdeck, axis=0), axis=1).sum())
    print(f"bridge: FLAT causeway, 0% grade, {blen*1000:.0f} mm deck on a lobe "
          f"arc, {bclear*1000:.0f} mm clear of the rest of the track")

    out = Path(args.out)
    svg(pts, spans, tps, d, usable, out / "track_layout_v1.svg")
    (out / "track_layout_v1.json").write_text(json.dumps({
        "floor_m": FLOOR, "wall_margin_m": WALL_MARGIN,
        "car_width_m_ESTIMATE": CAR_WIDTH, "lane_width_m": LANE,
        "corner_radius_m_NOT_COMMITTED": R_NOM, "measured_min_radius_m": rmin,
        "lobe_separation_m": d, "crossing_straights_m": spans,
        "centreline_length_m": total,
        "road_bbox_m": [float(ext[0]), float(ext[1])],
        "bridge": {"type": "flat causeway", "grade": 0.0,
                   "deck_len_m": blen, "clearance_m": bclear,
                   "centre_xy_m": [float(bdeck[len(bdeck)//2][0]),
                                   float(bdeck[len(bdeck)//2][1])],
                   "reason": "overpass infeasible - see module docstring"},
        "destinations": [{"name": n, "xy_m": [float(p[0]), float(p[1])]}
                         for n, p, _ in dests],
    }, indent=2), encoding="utf-8")
    print(f"-> {out / 'track_layout_v1.svg'}")
    print(f"-> {out / 'track_layout_v1.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
