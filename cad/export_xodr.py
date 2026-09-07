"""Export the figure-8 route as OpenDRIVE (.xodr) -- the format LaneMaker reads.

Written 2026-09-06 after Evan installed LaneMaker
(`~/Downloads/LaneMaker_0.9_Win64`) and its SampleMaps turned out to be
OpenDRIVE. This matters because of what 3DStreet could NOT do: a managed street
there is a cross-section extruded along a STRAIGHT line, so the R=500 mm corner
arcs -- the geometry that makes this a track rather than a street plan -- have
nowhere to live (Appendix DZ). OpenDRIVE has `<arc>` as a first-class primitive.
The sample maps use 356 arcs and 286 spirals, so this is not a theoretical
capability.

WHAT THIS EXPORTS, AND WHAT IT DOES NOT
  Exports: the DRIVEN ROUTE as one closed road -- 8 straights and 6 arcs.
  Does NOT export: the 3x3 grid, the 9 intersections, junction records, or
  lane links between roads. A figure-8 self-intersects, and OpenDRIVE models
  that with a junction plus connecting roads. This file emits the route as a
  single road that simply crosses itself geometrically, which is valid
  OpenDRIVE and is the smallest thing that answers "does LaneMaker load our
  geometry at all". Escalate to junctions only once that is known.

THE DECOMPOSITION, and why it is trustworthy
  `round_polyline` in track_layout_v2 rounds each 90-degree corner at radius R.
  For a 90-degree turn the tangent length is R*tan(45) = R, so each corner eats
  R from both adjacent edges and contributes an arc of R*pi/2.

  THE ROUTE HAS 6 CORNERS, NOT 8. Its 8 vertices include (0,0) twice, and at
  BOTH of those the heading does not change -- the route runs straight through
  the centre intersection on each pass. Those two vertex pairs merge into
  straights of 2.2 m. 3 lefts + 3 rights remain, which is exactly what
  track_layout_v2's docstring claims and what its self-check 4 tests.

  Arithmetic, all of it checkable:
      2 merged straights   2 * (2.2 - 2R) = 2 * 1.2  = 2.4 m
      4 single straights   4 * (1.1 - 2R) = 4 * 0.1  = 0.4 m
      6 arcs               6 * R*pi/2     = 6*0.7854 = 4.7124 m
      total                                           7.5124 m
  against `path_len(build()["route"])`'s 7.51207 m. The 0.32 mm gap is the
  polyline's discretization -- 240 chords across 6 arcs, each fractionally
  shorter than its arc, plus a 5.042 mm closing chord that `path_len` adds and
  an open sum would miss. The exact figures here are the MORE accurate ones;
  self_check pins the agreement at 1 mm.

SCALE
  OpenDRIVE is real-world metres and so is LaneMaker. Exports at FULL scale by
  default (x14.6304, from marking_specs) so lane widths are 3.6576 m rather
  than an absurd 0.25 m. `--model-scale` writes the 2.7 m model instead.
  ⚠️ At full scale the corner radius is 7.3152 m -- a parking-lot corner, not a
  road corner. Geometrically valid; it may look wrong to a tool that assumes
  highway alignments.

Usage:
  python cad/export_xodr.py                 # writes cad/track_figure8.xodr
  python cad/export_xodr.py --self-check
  python cad/export_xodr.py --model-scale
"""

from __future__ import annotations

import argparse
import importlib.util
import math
import xml.etree.ElementTree as ET
from pathlib import Path

XML_DECL = '<?xml version="1.0"?>' + chr(10)
LANE_TYPE = "driving"
EDGE_MARK = ("solid", "white")    # outer edge line, both sides
CENTRE_MARK = ("broken", "yellow")  # separates opposing directions (Appendix DU/DX)


def _load(name):
    f = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(f"_{f.stem}", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def arc_end(x, y, hdg, curv, length):
    """Endpoint and heading after an OpenDRIVE line (curv=0) or arc."""
    if abs(curv) < 1e-12:
        return x + length * math.cos(hdg), y + length * math.sin(hdg), hdg
    r = 1.0 / curv
    dh = curv * length
    cx, cy = x - r * math.sin(hdg), y + r * math.cos(hdg)
    return (cx + r * math.sin(hdg + dh),
            cy - r * math.cos(hdg + dh),
            hdg + dh)


def geometries(scale=1.0):
    """The route as an ordered list of (x, y, hdg, length, curvature).

    curvature 0 = straight; +ve = left turn, -ve = right (OpenDRIVE convention).
    """
    tl = _load("track_layout_v2.py")
    g = tl.build()
    R = g["R"] * scale
    verts = [(x * scale, y * scale) for x, y in g["verts"]]
    n = len(verts)

    def hdg_of(i):
        ax, ay = verts[i]
        bx, by = verts[(i + 1) % n]
        return math.atan2(by - ay, bx - ax)

    def wrap(a):
        return (a + math.pi) % (2 * math.pi) - math.pi

    # turn angle at each vertex i, between edge (i-1 -> i) and edge (i -> i+1)
    turn = [wrap(hdg_of(i) - hdg_of((i - 1) % n)) for i in range(n)]

    out = []
    for i in range(n):
        ax, ay = verts[i]
        bx, by = verts[(i + 1) % n]
        h = hdg_of(i)
        edge = math.hypot(bx - ax, by - ay)
        # this edge loses R at each END that is a real corner
        cut_start = R if abs(turn[i]) > 1e-9 else 0.0
        cut_end = R if abs(turn[(i + 1) % n]) > 1e-9 else 0.0
        straight = edge - cut_start - cut_end
        sx = ax + cut_start * math.cos(h)
        sy = ay + cut_start * math.sin(h)
        if straight > 1e-9:
            out.append((sx, sy, h, straight, 0.0))
        elif straight < -1e-9:
            raise SystemExit(
                f"edge {i} is {edge:.4f} m but two {R:.4f} m corner cuts need "
                f"{cut_start + cut_end:.4f} m -- corners overlap. Raise the "
                f"pitch or lower R in track_layout_v2.py.")
        t = turn[(i + 1) % n]
        if abs(t) > 1e-9:                      # arc at the far vertex
            ex, ey, eh = arc_end(sx, sy, h, 0.0, max(straight, 0.0))
            curv = (1.0 if t > 0 else -1.0) / R
            out.append((ex, ey, eh, abs(t) * R, curv))
    return out, g, R


# Counterclockwise order of compass arms, E first. The reference files' own
# boundary walk is counterclockwise -- derived from `figure 8.xodr` by taking
# each arm's outward heading (N/W/S/E) and reading the order its boundary
# visits them.
CCW_ARMS = ("E", "N", "W", "S")

# Trim applied to a boundary lane segment at EACH end, as a fraction of lane
# width, for a TURN connector. The reference's own turn trims are 0.37-0.49 x
# lane (8 samples, `1122.xodr` + `figure 8.xodr`), never symmetric and with no
# formula recovered -- they are where the connector's edge meets the incoming
# street's edge, which varies with the approach angle.
# shortcut: one representative value instead of the true intersection.
# Ceiling: the paved polygon is a few cm off the real kerb line. Upgrade
# trigger: LaneMaker renders a visibly wrong junction surface.
TURN_TRIM_LANE_FRAC = 0.45


def _boundary_side(contact):
    """`side` for a type="joint" segment. DERIVED and verified on 38 of 38
    boundary segments across all 6 junctions of `1122.xodr` and
    `figure 8.xodr` (2026-09-07, Appendix EQ):

        junction at the road's START (s=0)      -> "right"
        junction at the road's END   (s=length) -> "left"
        every type="lane" segment               -> "right", always

    Appendix EL called this underivable because it hunted POSITIONAL patterns
    (is the first joint left? one left per junction?). The rule is per-segment
    semantic; the L/R sequences EL tabulated are just each junction's arms in
    whatever order they happen to be written.
    """
    return "right" if contact == "start" else "left"


def _add_road(root, rid, name, geoms, scale, self_link=False,
              lanemaker_convention=False):
    """Append one <road> built from `geoms` and return it.

    ONE builder for all three callers -- the figure-8 export, the probe ladder
    and the 3x3 grid. build_xml and _probe_xml were near-duplicates when the
    probes were added (2026-09-06); a third copy for the grid would have made
    the lane block and the roadRunnerProfile three places to keep in step.
    """
    tl = _load("track_layout_v2.py")
    ms = _load("marking_specs.py")
    g, t = tl.build(), ms.table()
    # model dimension x scale. At scale=1 these are the 250 mm lane and the
    # 10.42 mm line; at full scale they return to the real 12 ft and 6 in
    # that marking_specs derived them from.
    lane_w = g["lane"] * scale
    mark_w = t["normal_line_mm"][1] / 1000.0 * scale
    total = sum(gm[3] for gm in geoms)

    road = ET.SubElement(root, "road", name=name, length=f"{total:.10f}",
                         id=str(rid), junction="-1")
    if self_link:
        link = ET.SubElement(road, "link")
        ET.SubElement(link, "predecessor", elementType="road",
                      elementId=str(rid), contactPoint="end")
        ET.SubElement(link, "successor", elementType="road",
                      elementId=str(rid), contactPoint="start")

    pv = ET.SubElement(road, "planView")
    s = 0.0
    for x, y, hdg, length, curv in geoms:
        gel = ET.SubElement(pv, "geometry", s=f"{s:.10f}", x=f"{x:.10f}",
                            y=f"{y:.10f}", hdg=f"{hdg:.10f}",
                            length=f"{length:.10f}")
        if abs(curv) < 1e-12:
            ET.SubElement(gel, "line")
        else:
            ET.SubElement(gel, "arc", curvature=f"{curv:.10f}")
        s += length

    ep = ET.SubElement(road, "elevationProfile")
    ET.SubElement(ep, "elevation", s="0", a="0", b="0", c="0", d="0")

    lanes = ET.SubElement(road, "lanes")
    if lanemaker_convention:
        # ⚠️ EXPERIMENT (2026-09-07): mirror the EXACT lane layout LaneMaker
        # itself authors for a two-way street, because our 1+1 no-median
        # layout is unlike ANY road in the reference file and the simulator
        # reports "No roads to spawn on!" then crashes on our grid even at
        # 5 m street segments -- i.e. length is not the gate (Appendix EO's
        # threshold was measured only on rescaled copies of the reference and
        # does NOT transfer to our file).
        # `track.md` cleared the median on probes 1-4, but those tested
        # LOADING; simulating is a different gate, and its own note already
        # warned "no sample road has a 1+1 layout without a median".
        # Reference road 0: laneOffset -lane/2; right -1 driving; centre 0
        # with type=""; left 1 MEDIAN + 2 driving; profile offsetX2 +1/-1.
        ET.SubElement(lanes, "laneOffset", s="0", a=f"{-lane_w / 2.0:.10f}",
                      b="0", c="0", d="0")
        sec = ET.SubElement(lanes, "laneSection", s="0")
        grp = ET.SubElement(sec, "right")
        ln = ET.SubElement(grp, "lane", id="-1", type=LANE_TYPE, level="false")
        ET.SubElement(ln, "width", sOffset="0", a=f"{lane_w:.10f}",
                      b="0", c="0", d="0")
        ET.SubElement(ln, "roadMark", sOffset="0", type=EDGE_MARK[0],
                      color=EDGE_MARK[1], laneChange="none", weight="",
                      width=f"{mark_w:.10f}")
        c = ET.SubElement(sec, "center")
        cl = ET.SubElement(c, "lane", id="0", type="", level="false")
        ET.SubElement(cl, "roadMark", sOffset="0", type=CENTRE_MARK[0],
                      color=CENTRE_MARK[1], laneChange="none", weight="",
                      width=f"{mark_w:.10f}")
        grp = ET.SubElement(sec, "left")
        med = ET.SubElement(grp, "lane", id="1", type="median", level="false")
        ET.SubElement(med, "width", sOffset="0", a=f"{lane_w:.10f}",
                      b="0", c="0", d="0")
        ln = ET.SubElement(grp, "lane", id="2", type=LANE_TYPE, level="false")
        ET.SubElement(ln, "width", sOffset="0", a=f"{lane_w:.10f}",
                      b="0", c="0", d="0")
        ET.SubElement(ln, "roadMark", sOffset="0", type=EDGE_MARK[0],
                      color=EDGE_MARK[1], laneChange="none", weight="",
                      width=f"{mark_w:.10f}")
    else:
        ET.SubElement(lanes, "laneOffset", s="0", a="0", b="0", c="0", d="0")
        sec = ET.SubElement(lanes, "laneSection", s="0")
        for side, lane_id in (("right", "-1"), ("left", "1")):
            grp = ET.SubElement(sec, side)
            ln = ET.SubElement(grp, "lane", id=lane_id, type=LANE_TYPE, level="false")
            ET.SubElement(ln, "width", sOffset="0", a=f"{lane_w:.10f}",
                          b="0", c="0", d="0")
            ET.SubElement(ln, "roadMark", sOffset="0", type=EDGE_MARK[0],
                          color=EDGE_MARK[1], laneChange="none", weight="",
                          width=f"{mark_w:.10f}")
            if side == "right":                 # centre lane sits between them
                c = ET.SubElement(sec, "center")
                cl = ET.SubElement(c, "lane", id="0", type="none", level="false")
                ET.SubElement(cl, "roadMark", sOffset="0", type=CENTRE_MARK[0],
                              color=CENTRE_MARK[1], laneChange="none", weight="",
                              width=f"{mark_w:.10f}")

    # LaneMaker refuses any map without this vendor block:
    #   "xodr map needs to contain custom LaneProfile!"
    # NOT standard OpenDRIVE -- a RoadRunner extension read by XPath (strings
    # `roadRunnerProfile`, `LaneProfile::Apply` are in the binary). Decoded
    # from its own SampleMaps (Appendix EB):
    #   type_s     = section start, s in CENTIMETRES (road 0: 127.14 m -> 12714)
    #   4294967295 = UINT32_MAX, a terminator on the left list
    #   laneCount  = DRIVING lanes on that side (medians are not counted)
    #   offsetX2   = laneOffset / laneWidth * 2 -- verified on all 272 roads
    # ⚠️ Still unexplained: why <left> needs a length-cm section PLUS the
    # terminator while <right> needs a single type_s="0". No sample road has a
    # 1+1 layout without a median, so this mirrors road 0's SHAPE.
    # offsetX2 = laneOffset / laneWidth * 2. With the LaneMaker convention
    # the reference line sits half a lane off centre, so it is -/+1 exactly as
    # every reference road writes it; our own centred layout gives 0.
    ox_l, ox_r = ("1", "-1") if lanemaker_convention else ("0", "0")
    prof = ET.SubElement(road, "roadRunnerProfile")
    left = ET.SubElement(prof, "left")
    ET.SubElement(left, "section", type_s=str(int(round(total * 100))),
                  laneCount="1", offsetX2=ox_l)
    ET.SubElement(left, "section", type_s="4294967295",
                  laneCount="1", offsetX2=ox_l)
    right = ET.SubElement(prof, "right")
    ET.SubElement(right, "section", type_s="0", laneCount="1", offsetX2=ox_r)
    return road


def _new_root(title):
    root = ET.Element("OpenDRIVE")
    ET.SubElement(root, "header", revMajor="1", revMinor="4", name=title,
                  vendor="cad/export_xodr.py")
    return root


def build_xml(scale=1.0):
    geoms, g, R = geometries(scale)
    root = _new_root("Autonomous Car Project figure-8")
    _add_road(root, 0, "figure-8 route", geoms, scale, self_link=True)
    total = sum(gm[3] for gm in geoms)
    return root, geoms, g, R, total, g["lane"] * scale


def grid_roads(scale=1.0):
    """The 3x3 grid as 6 straight roads: 3 along Z, 3 along X.

    NO junctions and no links. Appendix EC established that LaneMaker loads a
    self-intersecting road with no junction declared, so crossing roads need
    none either -- this is the cheap version, and proper junction records are
    the follow-up if the topology is wanted.
    """
    tl = _load("track_layout_v2.py")
    g = tl.build()
    coords = [c * scale for c in g["street_coords"]]
    half = g["road"] / 2.0 * scale
    end = max(coords) + half              # street runs -end .. +end
    span = 2 * end
    out = []
    for c in coords:                      # along +Y (hdg = pi/2)
        out.append((f"N-S street x={c/scale:+.3f} m model",
                    [(c, -end, math.pi / 2, span, 0.0)]))
    for c in coords:                      # along +X (hdg = 0)
        out.append((f"E-W street y={c/scale:+.3f} m model",
                    [(-end, c, 0.0, span, 0.0)]))
    return out, g, span


def build_grid_xml(scale=1.0):
    roads, g, span = grid_roads(scale)
    root = _new_root("Autonomous Car Project 3x3 grid")
    for rid, (name, geoms) in enumerate(roads):
        _add_road(root, rid, name, geoms, scale)
    return root, roads, g, span



def self_check() -> None:
    tl = _load("track_layout_v2.py")
    geoms, g, R = geometries(1.0)

    # 1. 6 arcs, 3 left + 3 right -- balanced, matching track_layout_v2's own
    #    self-check 4. The route's 8 vertices include (0,0) twice and the
    #    heading does not change at either, so 2 of them are NOT corners.
    arcs = [gm for gm in geoms if abs(gm[4]) > 1e-12]
    assert len(arcs) == 6, f"{len(arcs)} arcs, expected 6"
    assert sum(1 for a in arcs if a[4] > 0) == 3, "expected 3 left turns"
    assert sum(1 for a in arcs if a[4] < 0) == 3, "expected 3 right turns"

    # 2. LENGTH agrees with the generator's own measured route. This is the
    #    check that proves the decomposition, not just that it is self-consistent.
    # Use track_layout_v2's OWN path_len: it closes the loop (`append=p[:1]`),
    # and an open sum would omit that 5.042 mm closing chord. Tolerance 1 mm
    # because the polyline is 780 points -- 240 chords across 6 arcs, each
    # fractionally shorter than the arc it approximates, plus that closing
    # chord. The exact decomposition here is the MORE accurate number:
    # 7.512389 vs 7.512070, a 0.32 mm / 0.004% discretization artifact.
    total = sum(gm[3] for gm in geoms)
    measured = tl.path_len(g["route"])
    assert abs(total - measured) < 1e-3, (total, measured)

    # 3. CONTINUITY -- every geometry must start where the previous one ended,
    #    in position AND heading. A gap here is a road that teleports.
    for i, (x, y, hdg, length, curv) in enumerate(geoms):
        ex, ey, eh = arc_end(x, y, hdg, curv, length)
        nx, ny, nh, _, _ = geoms[(i + 1) % len(geoms)]
        assert abs(ex - nx) < 1e-9 and abs(ey - ny) < 1e-9, \
            f"geometry {i} ends at ({ex:.6f},{ey:.6f}), next starts at ({nx:.6f},{ny:.6f})"
        d = (eh - nh + math.pi) % (2 * math.pi) - math.pi
        assert abs(d) < 1e-9, f"geometry {i} heading jump {d:.2e} rad"

    # 4. total turning must be exactly zero -- 3 lefts and 3 rights cancel, so
    #    the loop closes without a net rotation. An oval would total 2*pi.
    net = sum(a[4] * a[3] for a in arcs)
    assert abs(net) < 1e-12, f"net turn {net:.3e} rad -- not a balanced figure-8"

    # 5. the XML is well formed and carries what a reader needs
    root, *_ = build_xml(1.0)
    xml = ET.tostring(root, encoding="unicode")
    reparsed = ET.fromstring(xml)
    assert reparsed.find("road/planView/geometry/arc") is not None
    assert reparsed.find("road/lanes/laneSection/center/lane/roadMark") is not None
    # 6. LaneMaker's required vendor block, and type_s in CENTIMETRES
    prof = reparsed.find("road/roadRunnerProfile")
    assert prof is not None, "no roadRunnerProfile -- LaneMaker will refuse the map"
    assert prof.find("left/section") is not None and prof.find("right/section") is not None
    total_m = float(reparsed.find("road").get("length"))
    assert int(prof.find("left/section").get("type_s")) == int(round(total_m * 100)),         "left section type_s must be the road length in centimetres"

    # 7. THE 3x3 GRID: 6 roads, unique ids, every one straight and profiled.
    groot, roads, gg, span = build_grid_xml(1.0)
    assert len(roads) == 6, len(roads)
    rs = groot.findall("road")
    assert len(rs) == 6 and len({r.get("id") for r in rs}) == 6, "duplicate road id"
    for r in rs:
        assert r.find("planView/line") is None      # <line> is under <geometry>
        assert len(r.findall("planView/geometry")) == 1
        assert r.find("planView/geometry/line") is not None, "grid roads are straight"
        assert r.find("roadRunnerProfile/right/section") is not None
        assert abs(float(r.get("length")) - span) < 1e-9
    # the 6 streets must sit on the grid coordinates, 3 per axis
    xs = sorted({round(float(r.find("planView/geometry").get("x")), 6) for r in rs})
    zs = sorted({round(float(r.find("planView/geometry").get("y")), 6) for r in rs})
    assert len(xs) == 4 and len(zs) == 4, (xs, zs)   # 3 street coords + 1 end
    # span must cover the whole grid: 2*pitch + road
    assert abs(span - (2 * gg["pitch"] + gg["road"])) < 1e-9, (span, gg["pitch"])
    assert len(reparsed.findall("road/planView/geometry")) == len(geoms)

    # 8. THE JUNCTION GRID. The check that matters is CONTINUITY THROUGH THE
    #    JUNCTION: every connecting road's arc must LAND on the outgoing lane,
    #    in position and heading. An arc that ends anywhere else is a turn the
    #    car drives off the road.
    streets, junctions, connectors, m = junction_layout(1.0)
    assert len(streets) == 12, len(streets)
    assert len(junctions) == 9, len(junctions)
    # 68 = 4x4 (centre) + 4 x 3x3 (edges) + 4 x 2x2 (corners), U-turns
    # included per LaneMaker's convention (Appendix EF).
    assert len(connectors) == 68, len(connectors)
    from collections import Counter
    assert Counter(len(j["arms"]) for j in junctions) == Counter({2: 4, 3: 4, 4: 1})
    assert sum(len(j["connections"]) for j in junctions) == 68
    assert sum(len(j["arms"]) ** 2 for j in junctions) == 68, "k arms -> k*k moves"

    for j in junctions:
        C = j["centre"]
        for cid in j["connections"]:
            c = connectors[cid]
            x, y, hdg, length, curv = c["geoms"][0]
            ex, ey, eh = arc_end(x, y, hdg, curv, length)
            arm_out = c["name"].split("->")[1]
            v = DIRS[arm_out]
            rv = _right_of(v)
            px = C[0] + v[0] * m["Rt"] + rv[0] * m["o"]
            py = C[1] + v[1] * m["Rt"] + rv[1] * m["o"]
            assert abs(ex - px) < 1e-9 and abs(ey - py) < 1e-9, (
                c["name"], (ex, ey), (px, py))
            d = (eh - math.atan2(v[1], v[0]) + math.pi) % (2 * math.pi) - math.pi
            assert abs(d) < 1e-9, (c["name"], "heading off by", d)

    # 8b. EVERY TURN MUST BE DRIVABLE. A turn tighter than the car's own
    #     minimum radius is a road it cannot use. 232.4 mm is the
    #     servo-achievable R_min estimate (steering.md, Appendix DN) -- an
    #     estimate, so this asserts against it deliberately rather than against
    #     the 116.2 mm bare-linkage figure, which no servo can deliver.
    R_MIN_SERVO_EST = 0.2324
    radii = {c["r_arc"] for c in connectors
             if c["r_arc"] is not None and not c["uturn"]}
    assert radii == {m["r_right"], m["r_left"]}, radii
    for r in sorted(radii):
        assert r >= R_MIN_SERVO_EST, (
            "turn radius {:.3f} m is tighter than the car's estimated R_min "
            "{:.3f} m -- raise the junction radius".format(r, R_MIN_SERVO_EST))

    # 8c. junctions must not eat the streets between them
    assert m["seg"] > 0, m["seg"]

    # 8d. TOPOLOGY, not just geometry. The first cut of the junction export
    #     passed every check above and still crashed LaneMaker with an
    #     ACCESS_VIOLATION inside its own code, because NONE of its 56 roads
    #     had a <link>: the junction blocks pointed at roads, and no road
    #     pointed back. Geometry checks cannot see a missing graph edge.
    jroot, jstreets, jjs, jconns, _m = build_junction_xml(1.0)
    jroads = jroot.findall("road")
    ids = {r.get("id") for r in jroads}
    jids = {j.get("id") for j in jroot.findall("junction")}
    assert len(jroads) == len(jstreets) + len(jconns) == 80, len(jroads)

    for r in jroads:
        lk = r.find("link")
        assert lk is not None and len(lk), "road {} has no <link>".format(r.get("id"))
        for e in lk:
            et, eid = e.get("elementType"), e.get("elementId")
            if et == "road":
                assert eid in ids, "road {} links to missing road {}".format(r.get("id"), eid)
            elif et == "junction":
                assert eid in jids, "road {} links to missing junction {}".format(r.get("id"), eid)
            else:
                raise AssertionError("unknown elementType " + str(et))
        # a connecting road links to ROADS; a street links to JUNCTIONS
        want = "road" if r.get("junction") != "-1" else "junction"
        for e in lk:
            assert e.get("elementType") == want, (
                "road {} (junction={}) has a {} link, expected {}".format(
                    r.get("id"), r.get("junction"), e.get("elementType"), want))

    for con in jroot.findall("junction/connection"):
        assert con.get("incomingRoad") in ids, con.get("incomingRoad")
        assert con.get("connectingRoad") in ids, con.get("connectingRoad")
        ll = con.find("laneLink")
        assert ll is not None and ll.get("to") == "-1", ET.tostring(con)
        assert ll.get("from") in ("-1", "1"), ll.get("from")
    # both approach directions must actually occur -- hardcoding from="-1"
    # mislabels every street whose START touches the junction
    froms = {ll.get("from") for ll in jroot.findall("junction/connection/laneLink")}
    assert froms == {"-1", "1"}, froms

    # 8e. CONNECTING ROADS MUST BE ONE-WAY. A turn movement runs one way;
    #     the first cut made them two-way, which is the leading suspect for
    #     the ACCESS_VIOLATION of Appendix EE. Shape taken from Evan's own
    #     LaneMaker export (1122.xodr): no <left> lane group, no <left> in the
    #     roadRunnerProfile, laneOffset = +lane/2, and a LANE-level <link>.
    for r in jroot.findall("road"):
        if r.get("junction") == "-1":
            continue
        assert r.find("lanes/laneSection/left") is None, (
            "connecting road {} is two-way".format(r.get("id")))
        assert r.find("roadRunnerProfile/left") is None, r.get("id")
        ln = r.find("lanes/laneSection/right/lane")
        assert ln is not None and ln.find("link") is not None, (
            "connecting road {} has no lane-level link".format(r.get("id")))
        off = float(r.find("lanes/laneOffset").get("a"))
        assert off > 0, (r.get("id"), off)

    print("export_xodr self_check: PASS")


def write_probe(out_dir: Path):
    """A bisection ladder for LaneMaker's crash (Appendix EB follow-up).

    It aborts with 0xC0000409 param 7 (FAST_FAIL_FATAL_APP_EXIT = std::terminate
    on an unhandled C++ exception), deterministically, at the same address both
    times. That is a thrown invariant, not malformed XML -- so the question is
    WHICH property of our road it objects to. Four files, increasing in the
    three ways ours differs from every sample road:

      1 straight   one straight road, no links, no self-crossing
      2 arc        adds one arc -- tests the curve path
      3 open8      the full figure-8 geometry, still NO self-link
      4 closed8    adds the self-link (== cad/track_figure8.xodr)

    First one that crashes names the cause. No sample road self-links or
    self-intersects, so 3 and 4 are the anomalies; 1 and 2 should load if the
    roadRunnerProfile shape is right.
    """
    ms = _load("marking_specs.py")
    scale = ms.scale()
    ladder = [
        ("1_straight", [(0.0, 0.0, 0.0, 40.0, 0.0)], False),
        ("2_arc", None, False),
        ("3_open8", None, False),
        ("4_closed8", None, True),
    ]
    R = 7.3152
    quarter = abs(math.pi / 2) * R
    ladder[1] = ("2_arc", [(0.0, 0.0, 0.0, 20.0, 0.0),
                           (20.0, 0.0, 0.0, quarter, 1.0 / R),
                           (20.0 + R, R, math.pi / 2, 20.0, 0.0)], False)
    written = []
    for name, geoms, self_link in ladder:
        if geoms is None:
            geoms, _g, _R = geometries(scale)
        root = _new_root('probe')
        _add_road(root, 0, 'probe', geoms, scale, self_link=self_link)
        f = out_dir / f"probe_{name}.xodr"
        ET.indent(root, space="  ")
        f.write_text(XML_DECL + ET.tostring(root, encoding="unicode"),
                     encoding="utf-8")
        written.append((f.name, len(geoms), self_link))
    return written


DIRS = {"N": (0.0, 1.0), "S": (0.0, -1.0), "E": (1.0, 0.0), "W": (-1.0, 0.0)}


def _right_of(u):
    """Unit vector 90 degrees clockwise from u -- the right-hand side of travel."""
    return (u[1], -u[0])


def junction_layout(scale=1.0, turn_r=None):
    """The 3x3 grid as street segments + junctions + connecting roads.

    THE JUNCTION RADIUS IS THE KERB RETURN RADIUS, and it is the whole design
    lever here. A turn confined to the bare intersection box (half-width
    road/2 = 250 mm) would have radius road/2 - lane/2 = 125 mm, needing 56.1
    degrees of steer at the measured 185.95 mm wheelbase -- far past the 38.7
    degree servo-achievable estimate (steering.md / Appendix DN). The car could
    not make a right turn.

    With a kerb return radius Rt the arcs become Rt -/+ lane/2:

        Rt      right    left    street segment   drivable (R_min 232.4 mm)
        250mm   125mm    375mm      600mm         left only
        375mm   250mm    500mm      350mm         both
        500mm   375mm    625mm      100mm         both
        625mm   500mm    750mm     -150mm         junctions would overlap

    Default Rt = the figure-8's own R (500 mm), which is not a coincidence:
    it yields 100 mm street segments, exactly the "straight between corners"
    track_layout_v2 already reports. The route's sweeping corners ARE the
    junction turns.

    Returns (streets, junctions, connectors, meta) where each road is
    (name, geoms) and connectors carry their junction id and lane links.
    """
    tl = _load("track_layout_v2.py")
    g = tl.build()
    Rt = (g["R"] if turn_r is None else turn_r) * scale
    o = g["lane"] / 2.0 * scale
    coords = [c * scale for c in g["street_coords"]]
    pitch = g["pitch"] * scale

    if pitch - 2 * Rt <= 0:
        raise SystemExit(
            "junction radius {:.3f} m leaves no street between junctions at "
            "pitch {:.3f} m -- adjacent junctions would overlap".format(Rt, pitch))

    # ---- which arms each junction actually has -----------------------------
    # A junction has an arm in a direction only if a street continues there.
    arms = {}
    for cx in coords:
        for cy in coords:
            a = []
            if cy < max(coords) - 1e-9: a.append("N")
            if cy > min(coords) + 1e-9: a.append("S")
            if cx < max(coords) - 1e-9: a.append("E")
            if cx > min(coords) + 1e-9: a.append("W")
            arms[(cx, cy)] = a

    # ---- street segments between consecutive junctions ---------------------
    # Each carries an id and remembers which (junction, arm) each end touches,
    # so the connecting roads below can be linked without guessing.
    streets = []
    for c in coords:                                   # N-S streets at x = c
        for a, b in zip(coords, coords[1:]):
            streets.append(dict(
                name="street x={:+.3f} y={:+.3f}..{:+.3f}".format(c, a, b),
                geoms=[(c, a + Rt, math.pi / 2, pitch - 2 * Rt, 0.0)],
                start=((c, a), "N"), end=((c, b), "S")))
    for c in coords:                                   # E-W streets at y = c
        for a, b in zip(coords, coords[1:]):
            streets.append(dict(
                name="street y={:+.3f} x={:+.3f}..{:+.3f}".format(c, a, b),
                geoms=[(a + Rt, c, 0.0, pitch - 2 * Rt, 0.0)],
                start=((a, c), "E"), end=((b, c), "W")))

    end_road = {}                                      # (junction, arm) -> (idx, contact)
    for i, s in enumerate(streets):
        end_road[s["start"]] = (i, "start")
        end_road[s["end"]] = (i, "end")

    # ---- connecting roads: every legal movement at every junction ----------
    connectors = []
    junctions = []
    for jid, (C, a_list) in enumerate(sorted(arms.items())):
        conns = []
        for arm_in in a_list:
            for arm_out in a_list:
                # U-TURNS ARE INCLUDED, matching LaneMaker's own export
                # (1122.xodr, Appendix EF): its 4-arm junction has 16 = 4x4
                # connections and its 3-arm ones 9 = 3x3. Mine excluded
                # arm-to-same-arm and had 44 where its convention gives 68.
                # NOTE the U-turn is NOT drivable by this car: it swings
                # between two lane centres `lane` apart, so its radius is
                # lane/2 = 125 mm, under the 232.4 mm servo estimate. It is
                # emitted for FORMAT CONFORMANCE, and check 8b skips it.
                u = tuple(-v for v in DIRS[arm_in])     # travel direction in
                v = DIRS[arm_out]                       # travel direction out
                ru, rv = _right_of(u), _right_of(v)
                p_in = (C[0] + DIRS[arm_in][0] * Rt + ru[0] * o,
                        C[1] + DIRS[arm_in][1] * Rt + ru[1] * o)
                cross = u[0] * v[1] - u[1] * v[0]
                if arm_in == arm_out:                   # U-turn: 180 degrees
                    r_arc = o
                    geoms = [(p_in[0], p_in[1], math.atan2(u[1], u[0]),
                              r_arc * math.pi, 1.0 / r_arc)]
                elif abs(cross) < 1e-9:                 # straight through
                    geoms = [(p_in[0], p_in[1], math.atan2(u[1], u[0]),
                              2 * Rt, 0.0)]
                    r_arc = None
                else:
                    left = cross > 0
                    r_arc = Rt + o if left else Rt - o
                    geoms = [(p_in[0], p_in[1], math.atan2(u[1], u[0]),
                              r_arc * math.pi / 2,
                              (1.0 if left else -1.0) / r_arc)]
                cid = len(connectors)
                connectors.append(dict(
                    name="j{} {}->{}".format(jid, arm_in, arm_out),
                    uturn=(arm_in == arm_out),
                    arm_in=arm_in, arm_out=arm_out,
                    geoms=geoms, junction=jid, r_arc=r_arc,
                    incoming=end_road.get((C, arm_in)),
                    outgoing=end_road.get((C, arm_out))))
                conns.append(cid)
        junctions.append(dict(id=jid, centre=C, arms=a_list, connections=conns))

    meta = dict(Rt=Rt, o=o, pitch=pitch, seg=pitch - 2 * Rt,
                r_right=Rt - o, r_left=Rt + o, g=g, end_road=end_road)
    return streets, junctions, connectors, meta


def _add_oneway_road(root, rid, name, geoms, scale, lane_link=None):
    """A ONE-WAY single-lane road -- the shape LaneMaker itself writes for a
    connecting road inside a junction.

    Copied from Evan's own LaneMaker export (Downloads/1122.xodr, 2026-09-07),
    which is ground truth rather than inference. Every one of its 47 connecting
    roads has exactly this shape:

        <laneOffset a="+lane/2">        reference line on the lane's left edge
        <right><lane id="-1" driving>   the only travel lane
          <link><predecessor id=..><successor id=..>   LANE-level links
        <center><lane id="0">           carries the centreline roadMark
        (NO <left> element at all)
        <roadRunnerProfile><right><section type_s="0" laneCount="1"
                                           offsetX2="1"/></right>
        (NO <left> element in the profile either)

    My first cut made connecting roads TWO-WAY, which is semantically wrong --
    a turn movement runs one way -- and is the leading suspect for the
    ACCESS_VIOLATION of Appendix EE.

    `lane_link` is (predecessor_lane_id, successor_lane_id) or None.
    """
    tl = _load("track_layout_v2.py")
    ms = _load("marking_specs.py")
    g, t = tl.build(), ms.table()
    lane_w = g["lane"] * scale
    mark_w = t["normal_line_mm"][1] / 1000.0 * scale
    total = sum(gm[3] for gm in geoms)

    road = ET.SubElement(root, "road", name=name, length="{:.10f}".format(total),
                         id=str(rid), junction="-1")
    pv = ET.SubElement(road, "planView")
    s = 0.0
    for x, y, hdg, length, curv in geoms:
        gel = ET.SubElement(pv, "geometry", s="{:.10f}".format(s),
                            x="{:.10f}".format(x), y="{:.10f}".format(y),
                            hdg="{:.10f}".format(hdg),
                            length="{:.10f}".format(length))
        if abs(curv) < 1e-12:
            ET.SubElement(gel, "line")
        else:
            ET.SubElement(gel, "arc", curvature="{:.10f}".format(curv))
        s += length

    ep = ET.SubElement(road, "elevationProfile")
    ET.SubElement(ep, "elevation", s="0", a="0", b="0", c="0", d="0")

    lanes = ET.SubElement(road, "lanes")
    # reference line sits on the LEFT edge of the single lane, as LaneMaker does
    ET.SubElement(lanes, "laneOffset", s="0", a="{:.10f}".format(lane_w / 2.0),
                  b="0", c="0", d="0")
    sec = ET.SubElement(lanes, "laneSection", s="0")
    grp = ET.SubElement(sec, "right")
    ln = ET.SubElement(grp, "lane", id="-1", type=LANE_TYPE, level="false")
    if lane_link is not None:
        lk = ET.SubElement(ln, "link")
        ET.SubElement(lk, "predecessor", id=str(lane_link[0]))
        ET.SubElement(lk, "successor", id=str(lane_link[1]))
    ET.SubElement(ln, "width", sOffset="0", a="{:.10f}".format(lane_w),
                  b="0", c="0", d="0")
    ET.SubElement(ln, "roadMark", sOffset="0", type=EDGE_MARK[0],
                  color=EDGE_MARK[1], laneChange="none", weight="",
                  width="{:.10f}".format(mark_w))
    c = ET.SubElement(sec, "center")
    cl = ET.SubElement(c, "lane", id="0", type="", level="false")
    ET.SubElement(cl, "roadMark", sOffset="0", type=CENTRE_MARK[0],
                  color=CENTRE_MARK[1], laneChange="none", weight="",
                  width="{:.10f}".format(mark_w))

    prof = ET.SubElement(road, "roadRunnerProfile")
    right = ET.SubElement(prof, "right")
    ET.SubElement(right, "section", type_s="0", laneCount="1", offsetX2="1")
    return road


def _set_link(road, pred=None, succ=None):
    """Insert a <link> as the FIRST child of <road> (OpenDRIVE child order).

    Each of pred/succ is (elementType, elementId, contactPoint) or None.
    Roads without links are what crashed LaneMaker on 2026-09-07: it walks
    road -> junction -> connecting road and dereferences links that are not
    there (ACCESS_VIOLATION inside its own code, not the runtime's abort path).
    Every road in its SampleMaps carries one.
    """
    link = ET.Element("link")
    for tag, spec in (("predecessor", pred), ("successor", succ)):
        if spec is None:
            continue
        et, eid, cp = spec
        ET.SubElement(link, tag, elementType=et, elementId=str(eid),
                      contactPoint=cp)
    if len(link):
        road.insert(0, link)


def build_junction_xml(scale=1.0, turn_r=None, lanemaker_convention=False,
                       boundary=False):
    streets, junctions, connectors, meta = junction_layout(scale, turn_r)
    lane_w = meta["g"]["lane"] * scale
    root = _new_root("Autonomous Car Project 3x3 grid with junctions")
    jid_of = {tuple(j["centre"]): j["id"] for j in junctions}

    street_els = []
    for i, s in enumerate(streets):
        r = _add_road(root, i, s["name"], s["geoms"], scale,
                      lanemaker_convention=lanemaker_convention)
        # a street runs between two junctions; each end declares which.
        _set_link(r,
                  pred=("junction", jid_of[s["start"][0]], ""),
                  succ=("junction", jid_of[s["end"][0]], ""))
        street_els.append(r)

    base = len(streets)
    for k, c in enumerate(connectors):
        # LANE-LEVEL link ids: on a two-way street lane -1 runs in +s, so a car
        # reaching the road's END is in -1 and one reaching its START is in +1.
        pl = "-1" if (c["incoming"] and c["incoming"][1] == "end") else "1"
        sl = "-1" if (c["outgoing"] and c["outgoing"][1] == "start") else "1"
        r = _add_oneway_road(root, base + k, c["name"], c["geoms"], scale,
                             lane_link=(pl, sl))
        r.set("junction", str(c["junction"]))
        # a connecting road links to ROADS, not junctions, and names the end
        # of each street it meets.
        pred = succ = None
        if c["incoming"] is not None:
            idx, contact = c["incoming"]
            pred = ("road", idx, contact)
        if c["outgoing"] is not None:
            idx, contact = c["outgoing"]
            succ = ("road", idx, contact)
        _set_link(r, pred=pred, succ=succ)

    for j in junctions:
        jel = ET.SubElement(root, "junction", id=str(j["id"]),
                            name="junction {:+.3f},{:+.3f}".format(*j["centre"]))
        n = 0
        for cid in j["connections"]:
            c = connectors[cid]
            if c["incoming"] is None:
                continue
            inc, contact = c["incoming"]
            con = ET.SubElement(jel, "connection", id=str(n),
                                incomingRoad=str(inc),
                                connectingRoad=str(base + cid),
                                contactPoint="start")
            # ONE SIGNAL PHASE PER ARM, 0-based. 63 of 63 connections in both
            # reference files carry this; ours carried 0 of 68 (2026-09-07).
            # The rule is visible in `figure 8.xodr`, whose two roads each meet
            # the junction at BOTH ends: (road 0, lane -1)->2, (road 0, lane 2)
            # ->3, (road 13, lane -1)->0, (road 13, lane 2)->1 -- i.e. keyed on
            # the ARM, not the road.
            ET.SubElement(con, "signalPhase",
                          id=str(j["arms"].index(c["arm_in"])))
            # WHICH LANE ARRIVES depends on which END of the street touches
            # this junction. Lane -1 runs in +s, so a car reaching the road's
            # END is in -1; one reaching its START came the other way and is
            # in +1. Hardcoding -1 (as the first cut did) mislabels half the
            # approaches. The sample does the same thing -- its first
            # connection is laneLink from="2".
            # With LaneMaker's own layout the left side is lane 1 (MEDIAN)
            # + lane 2 (driving), so the left-hand approach arrives in lane 2
            # -- which is exactly what every reference connection writes
            # (from="2"). Our centred layout has the driving lane at 1.
            left_id = "2" if lanemaker_convention else "1"
            frm = "-1" if contact == "end" else left_id
            ET.SubElement(con, "laneLink", **{"from": frm, "to": "-1"})
            n += 1

        if not boundary:
            continue
        # THE BOUNDARY IS THE JUNCTION'S PAVED-AREA POLYGON, and its absence is
        # why our junctions render as empty space (Appendix EP). It is a CYCLIC
        # WALK: for each pair of arms adjacent in counterclockwise order, emit
        #   <segment type="joint">  zero-length, on the INCOMING STREET at arm i
        #   <segment type="lane">   a stretch of the connector arm i -> arm i+1
        # That connector is the RIGHT TURN between them, i.e. literally the kerb
        # return -- verified on both reference files, where every lane segment's
        # predecessor/successor are exactly its neighbouring joints (Appendix EQ).
        arm_of = {(c["arm_in"], c["arm_out"]): (base + cid, c)
                  for cid in j["connections"] for c in [connectors[cid]]}
        order = [a for a in CCW_ARMS if a in j["arms"]]
        bel = ET.SubElement(jel, "boundary")
        for i, arm in enumerate(order):
            nxt = order[(i + 1) % len(order)]
            street = meta["end_road"].get((tuple(j["centre"]), arm))
            pair = arm_of.get((arm, nxt))
            if street is None or pair is None:
                raise SystemExit(
                    f"junction {j['id']}: no street or connector for arm "
                    f"{arm}->{nxt}; the boundary walk cannot close.")
            sidx, contact = street
            slen = sum(gm[3] for gm in streets[sidx]["geoms"])
            at = 0.0 if contact == "start" else slen
            ET.SubElement(bel, "segment", roadID=str(sidx),
                          sStart=f"{at:.10f}", sEnd=f"{at:.10f}",
                          side=_boundary_side(contact), type="joint")
            crid, c = pair
            clen = sum(gm[3] for gm in c["geoms"])
            # straight-through connectors trim by length/24 -- machine-precision
            # on 5/5 reference samples (Appendix EK); turns use the fraction of
            # lane width above, which is an approximation, not a derivation.
            trim = clen / 24.0 if c["r_arc"] is None else lane_w * TURN_TRIM_LANE_FRAC
            trim = min(trim, clen * 0.45)         # never invert on a short arc
            ET.SubElement(bel, "segment", roadID=str(crid),
                          sStart=f"{trim:.10f}", sEnd=f"{clen - trim:.10f}",
                          side="right", type="lane")
    return root, streets, junctions, connectors, meta

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-scale", action="store_true",
                    help="write the 2.7 m model instead of full scale")
    ap.add_argument("--out", default=None)
    ap.add_argument("--probe", action="store_true",
                    help="write the LaneMaker bisection ladder")
    ap.add_argument("--junctions", action="store_true",
                    help="3x3 grid WITH junction records and turn arcs")
    ap.add_argument("--grid", action="store_true",
                    help="write the 3x3 street grid instead of the route")
    ap.add_argument("--sim-min-road", type=float, default=None,
                    metavar="METRES",
                    help="LANEMAKER ONLY. Scale the export so the SHORTEST "
                         "road is at least this long, instead of using the "
                         "true full scale. LaneMaker refuses to spawn a car "
                         "on short roads: measured 2026-09-07 (Appendix EO), "
                         "1.463 m FAILS and 2.553 m works, and our street "
                         "segments are exactly 1.463 m at true full scale, so "
                         "the honest export cannot be simulated. This is a "
                         "VIEWING scale for a tool that is off the critical "
                         "path -- it does NOT change the physical track, and "
                         "the lane renders unrealistically wide as the price. "
                         "5 matches the comfortably-spawning probe.")
    ap.add_argument("--lanemaker-lanes", action="store_true",
                    help="EXPERIMENT (2026-09-07). Give street roads the EXACT "
                         "lane layout LaneMaker authors for a two-way street: "
                         "a MEDIAN lane, reference line half a lane off centre, "
                         "offsetX2 -/+1, left driving lane id 2. Our 1+1 "
                         "centred layout matches no road in the reference file, "
                         "and the simulator reports 'No roads to spawn on!' "
                         "then crashes on our grid even at 5 m streets, so "
                         "length is not the gate. track.md cleared the median "
                         "on probes 1-4 -- but those tested LOADING, and "
                         "simulating is a different gate.")
    ap.add_argument("--boundary", action="store_true",
                    help="emit <junction><boundary>, the junction's paved-area "
                         "polygon. Its absence is why our junctions render as "
                         "empty space and the simulator finds no drivable area "
                         "(Appendix EP). `side` and the segment order are "
                         "DERIVED and verified on 38/38 reference segments "
                         "(EQ); the trim on turn connectors is approximate.")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0
    self_check()

    if args.junctions:
        ms = _load("marking_specs.py")
        scale = 1.0 if args.model_scale else ms.scale()
        if args.sim_min_road is not None:
            if args.model_scale:
                raise SystemExit("--sim-min-road and --model-scale both set "
                                 "a scale; pick one.")
            # The shortest road in this network is the street segment between
            # two junctions, `pitch - 2*Rt` -- 100 mm at model scale, because
            # Rt=500 against pitch=1100 leaves the grid 91% junction. Derive
            # the scale from IT, not from the lane, since it is what the spawn
            # threshold acts on.
            g = _load("track_layout_v2.py").build()
            seg_model = g["pitch"] - 2 * g["R"]
            scale = args.sim_min_road / seg_model
        root, streets, junctions, connectors, m = build_junction_xml(
            scale, lanemaker_convention=args.lanemaker_lanes,
            boundary=args.boundary)
        if args.sim_min_road is not None:
            # Appendix EO measured the spawn threshold in (1.463, 2.553] m.
            # Refuse to write a file that lands under the known-good end --
            # the failure mode in LaneMaker is a silent no-spawn, not an
            # error, so it has to be caught here.
            shortest = min(float(r.get("length")) for r in root.iter("road"))
            assert shortest >= 2.553, (
                f"shortest road {shortest:.4f} m is under 2.553 m, the "
                f"shortest length measured to actually spawn (Appendix EO; "
                f"1.463 m is measured to FAIL). Raise --sim-min-road.")
        out = Path(args.out) if args.out else Path(__file__).with_name(
            "track_grid3x3_junctions_model.xodr" if args.model_scale
            else "track_grid3x3_junctions_bnd.xodr" if args.boundary
            else "track_grid3x3_junctions_lmlanes.xodr" if args.lanemaker_lanes
            else "track_grid3x3_junctions_sim.xodr" if args.sim_min_road is not None
            else "track_grid3x3_junctions.xodr")
        ET.indent(root, space="  ")
        out.write_text(XML_DECL + ET.tostring(root, encoding="unicode"),
                       encoding="utf-8")
        from collections import Counter
        arm_hist = Counter(len(j["arms"]) for j in junctions)
        print("=" * 74)
        print("OPENDRIVE EXPORT -- 3x3 GRID WITH PROPER JUNCTIONS")
        print("=" * 74)
        print("scale           " + ("FULL, x{:.4f}".format(scale) if scale != 1.0
                                    else "MODEL, 1:1"))
        print("street segments {:d}  ({:.3f} m each)".format(len(streets), m["seg"]))
        print("junctions       {:d}  arms: {:d}x4-way, {:d}x3-way, {:d}x2-way".format(
            len(junctions), arm_hist[4], arm_hist[3], arm_hist[2]))
        nu = sum(1 for c in connectors if c["uturn"])
        print("connecting rds  {:d}  (k arms -> k*k movements, U-turns "
              "INCLUDED per LaneMaker's convention)".format(len(connectors)))
        print("  of which U-turn {:d}  radius {:.3f} m -- UNDRIVABLE by this car "
              "(under R_min),".format(nu, m["o"]))
        print("                     emitted for format conformance only")
        print()
        print("TURN GEOMETRY -- the junction radius IS the kerb return radius")
        print("  junction Rt   {:8.3f} m   (= the figure-8's own corner radius)".format(m["Rt"]))
        print("  right turns   {:8.3f} m   arc {:.3f} m".format(
            m["r_right"], m["r_right"] * math.pi / 2))
        print("  left turns    {:8.3f} m   arc {:.3f} m".format(
            m["r_left"], m["r_left"] * math.pi / 2))
        print("  car R_min est {:8.3f} m   servo-achievable (Appendix DN)".format(
            0.2324 * scale))
        print()
        print("Confining turns to the bare {:.3f} m box instead would force".format(
            m["g"]["road"] * scale))
        print("R = {:.3f} m for a right turn -- 56.1 deg of lock, past the".format(
            (m["g"]["road"] / 2 - m["g"]["lane"] / 2) * scale))
        print("38.7 deg the servo can reach. The kerb radius is what makes the")
        print("grid drivable at all.")
        print()
        print("-> {}".format(out))
        return 0

    if args.grid:
        ms = _load("marking_specs.py")
        scale = 1.0 if args.model_scale else ms.scale()
        root, roads, g, span = build_grid_xml(scale)
        out = Path(args.out) if args.out else Path(__file__).with_name(
            "track_grid3x3_model.xodr" if args.model_scale else "track_grid3x3.xodr")
        ET.indent(root, space="  ")
        out.write_text(XML_DECL + ET.tostring(root, encoding="unicode"),
                       encoding="utf-8")
        print("=" * 74)
        print("OPENDRIVE EXPORT -- 3x3 STREET GRID")
        print("=" * 74)
        print("scale           " + (f"FULL, x{scale:.4f}" if scale != 1.0
                                    else "MODEL, 1:1"))
        print(f"roads           {len(roads)}  (3 along Z, 3 along X)")
        print(f"street length   {span:.4f} m each")
        print(f"street pitch    {g['pitch'] * scale:.4f} m")
        print(f"road width      {g['road'] * scale:.4f} m, 2 lanes")
        print(f"crossings       {len(g['intersections'])} (geometric only)")
        print()
        print("NO junction records and no links. Appendix EC established that")
        print("LaneMaker loads a self-intersecting road with no junction, so")
        print("crossing roads need none either. Proper junction topology is the")
        print("follow-up, not this file.")
        print()
        print(f"-> {out}")
        return 0

    if args.probe:
        for name, n, sl in write_probe(Path(__file__).parent):
            print(f"  {name:26} {n:2} geometries  self-link={sl}")
        print()
        print("Open them in order. The FIRST that crashes names the cause.")
        return 0

    ms = _load("marking_specs.py")
    scale = 1.0 if args.model_scale else ms.scale()
    root, geoms, g, R, total, lane_w = build_xml(scale)

    out = Path(args.out) if args.out else Path(__file__).with_name(
        "track_figure8_model.xodr" if args.model_scale else "track_figure8.xodr")
    ET.indent(root, space="  ")
    out.write_text('<?xml version="1.0"?>\n' + ET.tostring(root, encoding="unicode"),
                   encoding="utf-8")

    arcs = [gm for gm in geoms if abs(gm[4]) > 1e-12]
    print("=" * 74)
    print("OPENDRIVE EXPORT  (the format LaneMaker's SampleMaps use)")
    print("=" * 74)
    print("scale           " + (f"FULL, x{scale:.4f} (the 1:{ms.scale():.2f} "
          f"model rendered at real-world size)" if scale != 1.0
          else "MODEL, 1:1 -- the physical 2.7 m track"))
    print(f"geometries      {len(geoms)}  ({len(geoms)-len(arcs)} line, {len(arcs)} arc)")
    print(f"corner radius   {R:.4f} m  -> curvature {1/R:.6f}")
    print(f"lane width      {lane_w:.4f} m each, 2 lanes")
    print(f"route length    {total:.4f} m")
    print(f"turns           3 left + 3 right, net turn 0 (balanced figure-8)")
    print()
    print("NOT exported: the 3x3 grid, the 9 intersections, junction records.")
    print("The route crosses itself geometrically with no junction declared --")
    print("valid OpenDRIVE, and the smallest thing that answers whether")
    print("LaneMaker loads our geometry at all.")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
