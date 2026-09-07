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


def build_xml(scale=1.0):
    geoms, g, R = geometries(scale)
    ms = _load("marking_specs.py")
    t = ms.table()
    # model dimension x scale. At scale=1 these are the 250 mm lane and the
    # 10.42 mm line; at full scale they return to the real 12 ft and 6 in
    # that marking_specs derived them from.
    lane_w = g["lane"] * scale
    mark_w = t["normal_line_mm"][1] / 1000.0 * scale
    total = sum(gm[3] for gm in geoms)

    root = ET.Element("OpenDRIVE")
    ET.SubElement(root, "header", revMajor="1", revMinor="4",
                  name="Autonomous Car Project figure-8",
                  vendor="cad/export_xodr.py")
    road = ET.SubElement(root, "road", name="figure-8 route",
                         length=f"{total:.10f}", id="0", junction="-1")
    link = ET.SubElement(road, "link")
    ET.SubElement(link, "predecessor", elementType="road", elementId="0",
                  contactPoint="end")
    ET.SubElement(link, "successor", elementType="road", elementId="0",
                  contactPoint="start")

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
        if side == "right":                     # centre lane sits between them
            c = ET.SubElement(sec, "center")
            cl = ET.SubElement(c, "lane", id="0", type="none", level="false")
            ET.SubElement(cl, "roadMark", sOffset="0", type=CENTRE_MARK[0],
                          color=CENTRE_MARK[1], laneChange="none", weight="",
                          width=f"{mark_w:.10f}")

    # LaneMaker refuses any map without this vendor block:
    #   "xodr map needs to contain custom LaneProfile!"
    # It is NOT standard OpenDRIVE -- it is a RoadRunner extension, and
    # LaneMaker reads it by XPath (strings `roadRunnerProfile`,
    # `LaneProfile::Apply` are in the binary). Decoded from its own SampleMaps:
    #   type_s    = section start, s in CENTIMETRES (road 0: 127.14 m -> 12714)
    #   4294967295 = UINT32_MAX, a terminator on the left list
    #   laneCount = DRIVING lanes on that side (medians are not counted)
    #   offsetX2  = laneOffset / laneWidth * 2 -- verified across all 272 roads
    # ⚠️ NOT verified: why <left> lists a length-cm section plus a UINT32_MAX
    # terminator while <right> lists a single type_s="0". No sample road has a
    # 1+1 layout without a median, so this mirrors road 0's SHAPE with our lane
    # counts. If LaneMaker still refuses, draw any road in it, save, and read
    # the profile it writes -- that is ground truth and ends the guessing.
    prof = ET.SubElement(road, "roadRunnerProfile")
    off_x2 = 0                                   # our laneOffset is 0
    left = ET.SubElement(prof, "left")
    ET.SubElement(left, "section", type_s=str(int(round(total * 100))),
                  laneCount="1", offsetX2=str(off_x2))
    ET.SubElement(left, "section", type_s="4294967295",
                  laneCount="1", offsetX2=str(off_x2))
    right = ET.SubElement(prof, "right")
    ET.SubElement(right, "section", type_s="0",
                  laneCount="1", offsetX2=str(off_x2))
    return root, geoms, g, R, total, lane_w


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
    assert len(reparsed.findall("road/planView/geometry")) == len(geoms)

    print("export_xodr self_check: PASS")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-scale", action="store_true",
                    help="write the 2.7 m model instead of full scale")
    ap.add_argument("--out", default=None)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0
    self_check()

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
