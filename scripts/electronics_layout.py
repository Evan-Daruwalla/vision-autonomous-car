#!/usr/bin/env python
"""Check the electronics tray + deck LAYOUT against the real STLs, and draw it.

Stdlib + numpy only. cad/scad/electronics_tray.scad (layer 1) and
cad/scad/electronics_deck.scad (layer 2) each carry a LAYOUT list and print it
with echo(LAYOUT_PARTS = LAYOUT); the deck also prints echo(LAYOUT_PEGS = ...).
One LAYOUT entry is
    [name, [sx, sy, sz], [x, y, z], kind, held_by, ports]
[x, y, z] is the MIN corner of the box (the ghost_box convention), mm; x is
along the car (+x = front), y across, z up. kind is "part", "zone" or "note"
(a note has no volume: it is only drawn). `ports` is a string whose
";"-separated segments may start with a side tag -x: +x: -y: +y:.
This script runs OpenSCAD on each .scad, reads those echo lines, loads the two
committed STLs (cad/electronics_tray.stl, cad/electronics_deck.stl) and checks
every part/zone box against them:

  a) material: a 5 x 5 x 3 grid inside the box (inset 0.3 mm from every face;
     the mid-plane only, if the box is under 0.9 mm tall) must be OPEN in both
     STLs. Samples within 2.5 mm (x, y) of a LAYOUT_PEGS point are skipped:
     the pegs are meant to go into the parts' holes.
  b) overlap: no two part/zone boxes (either layer) overlap in volume. Boxes
     that only touch at a face do not overlap.
  c) support: on a 2 mm grid over the footprint (inset 0.3 mm), at least one
     point 0.3 mm below the bottom face is solid in one of the STLs.
  d) report only: for each layer-1 part/zone whose footprint overlaps the deck
     STL's xy bounding box, its top z and the gap up to the deck underside.

and writes docs/electronics_layout.svg: one panel per layer, a height map of
the STL under the entries, a legend line per entry.

WHAT PASSING PROVES, AND WHAT IT DOES NOT
-----------------------------------------
It proves that the boxes the SCAD lists are free of printed material at the
sampled points, do not overlap each other, and sit on something at the sampled
points. It does not prove the boxes are the real part sizes (they are typed in
the SCAD from the datasheet or a caliper), that a cable fits, that the car
survives a crash, or that anything prints or fits: that is measured on the
printed parts, never inferred here. Sampling is a grid, so a feature thinner
than the grid pitch can slip between samples. The SVG is a drawing of the
same boxes, not a measurement.

Usage:  python scripts/electronics_layout.py [-o docs/electronics_layout.svg]
                                             [--no-svg] [--self-check]
Exit:   0 every check passed (and --self-check: both planted bugs were caught)
        1 a check failed, the LAYOUT could not be read, or OpenSCAD failed
OpenSCAD is found like scripts/render_scad.py does ($OPENSCAD, then
~/tools/openscad-2021.01, then PATH). --self-check needs the STLs only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_scad import _run_openscad, find_openscad, inside, parse_stl  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

# ---- inputs -----------------------------------------------------------------
TRAY_SCAD = REPO / "cad" / "scad" / "electronics_tray.scad"
DECK_SCAD = REPO / "cad" / "scad" / "electronics_deck.scad"
TRAY_STL = REPO / "cad" / "electronics_tray.stl"
DECK_STL = REPO / "cad" / "electronics_deck.stl"
DEFAULT_SVG = REPO / "docs" / "electronics_layout.svg"

# ---- tunables (mm unless noted) ---------------------------------------------
OPENSCAD_TIMEOUT = 120    # s
KINDS = ("part", "zone", "note")
INSET = 0.3               # samples sit this far inside every face
THIN = 0.9                # boxes thinner than this get one mid-plane z sample
GRID_XYZ = (5, 5, 3)      # material samples per axis
PEG_CLEAR = 2.5           # skip material samples this close (x, y) to a peg
SUPPORT_STEP = 2.0        # support grid pitch
SUPPORT_DROP = 0.3        # support point sits this far below the bottom face
OVERLAP_EPS = 1e-6        # overlap in an axis must exceed this to count
MAX_MATERIAL_REPORTS = 3  # per part

# ---- SVG layout --------------------------------------------------------------
SCALE = 2.0                          # px per mm
VIEW_X = (-32, 158)                  # mm, x range drawn
VIEW_Y = (-88, 87)                   # mm, y range drawn
NX = VIEW_X[1] - VIEW_X[0]           # 190 height-map columns
NY = VIEW_Y[1] - VIEW_Y[0]           # 175 height-map rows
CELL_OFF = (0.5 + 0.0137, 0.5 + 0.0291)   # ray offset inside a 1 mm cell
MARGIN = 20.0
TITLE_H = 16.0
PANEL_W = NX * SCALE + 2 * MARGIN
LEGEND_TOP = 56.0                    # below the drawing: caption, then legend
LEGEND_LINE = 12.0
LEGEND_WRAP = 68
HEIGHT_FILLS = ("#e6e6e6", "#c8c8c8", "#a0a0a0", "#787878")
PALETTE = ("#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#a65628")
PORT_SIZE = 6.0                      # px, triangle edge
SIDE_TAGS = ("-x:", "+x:", "-y:", "+y:")


# ---- reading the layout ------------------------------------------------------
def load_layout(scad: Path) -> tuple[list, list]:
    """(parts, pegs) printed by one SCAD file's echo lines.

    Runs OpenSCAD (output .csg in a temp dir, so no mesh is built), then
    json-parses the text after "ECHO: LAYOUT_PARTS = " and, if present,
    "ECHO: LAYOUT_PEGS = ". RuntimeError on a non-zero exit, a timeout, or a
    missing LAYOUT_PARTS.
    """
    with tempfile.TemporaryDirectory() as td:
        cmd = [str(find_openscad()), "-o", str(Path(td) / "layout.csg"), str(scad)]
        proc = _run_openscad(cmd, scad, timeout=OPENSCAD_TIMEOUT)
    lines = (proc.stdout + "\n" + proc.stderr).splitlines()
    if proc.returncode != 0:
        tail = [ln for ln in lines if ln.strip()][-6:]
        raise RuntimeError(f"OpenSCAD failed on {scad} (exit {proc.returncode}): " + " | ".join(tail))
    found = {}
    for key in ("LAYOUT_PARTS", "LAYOUT_PEGS"):
        prefix = f"ECHO: {key} = "
        for ln in lines:
            if ln.startswith(prefix):
                try:
                    found[key] = json.loads(ln[len(prefix):].strip())
                except ValueError as e:
                    raise RuntimeError(f"{scad}: cannot parse {key}: {e}") from None
    if "LAYOUT_PARTS" not in found:
        raise RuntimeError(f"no 'ECHO: LAYOUT_PARTS = ' line in the output of {scad}")
    return found["LAYOUT_PARTS"], found.get("LAYOUT_PEGS", [])


def make_entries(parts: list, layer: int, scad: Path) -> list[dict]:
    """LAYOUT lists -> dicts with the layer and the 1-based index within it."""
    out = []
    for i, p in enumerate(parts):
        if len(p) != 6 or p[3] not in KINDS:
            raise RuntimeError(f"{scad}: LAYOUT entry {i + 1} is not [name, size, pos, kind, held_by, ports]: {p!r}")
        out.append({"name": str(p[0]), "size": [float(v) for v in p[1]], "pos": [float(v) for v in p[2]],
                    "kind": p[3], "held_by": str(p[4]), "ports": str(p[5]),
                    "layer": layer, "idx": i + 1})
    return out


def bodies(entries: list[dict]) -> list[dict]:
    """Entries that occupy volume (kind part or zone)."""
    return [e for e in entries if e["kind"] in ("part", "zone")]


# ---- checks: each returns [(ok, text)] ---------------------------------------
def axis_samples(lo: float, size: float, n: int, thin: float) -> np.ndarray:
    """n points inside [lo, lo+size] inset INSET from both faces; the mid-plane
    only when the extent is under `thin` (or too small to inset)."""
    if size < thin or size <= 2 * INSET:
        return np.array([lo + size / 2.0])
    return np.linspace(lo + INSET, lo + size - INSET, n)


def check_material(entries: list[dict], stls: list[np.ndarray], pegs: list) -> list[tuple[bool, str]]:
    results = []
    for e in bodies(entries):
        (x0, y0, z0), (sx, sy, sz) = e["pos"], e["size"]
        xs = axis_samples(x0, sx, GRID_XYZ[0], 0.0)
        ys = axis_samples(y0, sy, GRID_XYZ[1], 0.0)
        zs = axis_samples(z0, sz, GRID_XYZ[2], THIN)
        bad = []
        for x in xs:
            for y in ys:
                if any((x - p[0]) ** 2 + (y - p[1]) ** 2 <= PEG_CLEAR ** 2 for p in pegs):
                    continue
                for z in zs:
                    if any(inside(t, (x, y, z)) for t in stls):
                        bad.append((x, y, z))
                        if len(bad) == MAX_MATERIAL_REPORTS:
                            break
                if len(bad) == MAX_MATERIAL_REPORTS:
                    break
            if len(bad) == MAX_MATERIAL_REPORTS:
                break
        if bad:
            for x, y, z in bad:
                results.append((False, f"{e['name']}: material inside at ({x:.2f}, {y:.2f}, {z:.2f})"))
        else:
            results.append((True, f"material {e['name']}"))
    return results


def check_overlap(entries: list[dict]) -> list[tuple[bool, str]]:
    body = bodies(entries)
    fails = []
    for i, a in enumerate(body):
        for b in body[i + 1:]:
            if all(min(a["pos"][k] + a["size"][k], b["pos"][k] + b["size"][k])
                   - max(a["pos"][k], b["pos"][k]) > OVERLAP_EPS for k in range(3)):
                fails.append((False, f"overlap: {a['name']} (layer {a['layer']}) overlaps {b['name']} (layer {b['layer']})"))
    return fails or [(True, f"overlap: no two of {len(body)} boxes overlap")]


def check_support(entries: list[dict], stls: list[np.ndarray]) -> list[tuple[bool, str]]:
    results = []
    for e in bodies(entries):
        (x0, y0, z0), (sx, sy, _) = e["pos"], e["size"]
        xs = np.arange(x0 + INSET, x0 + sx - INSET + 1e-9, SUPPORT_STEP)
        ys = np.arange(y0 + INSET, y0 + sy - INSET + 1e-9, SUPPORT_STEP)
        if len(xs) == 0:
            xs = np.array([x0 + sx / 2.0])
        if len(ys) == 0:
            ys = np.array([y0 + sy / 2.0])
        z = z0 - SUPPORT_DROP
        held = any(inside(t, (x, y, z)) for x in xs for y in ys for t in stls)
        results.append((True, f"support {e['name']}") if held
                       else (False, f"{e['name']}: nothing under it"))
    return results


def report_gaps(entries: list[dict], deck: np.ndarray) -> list[str]:
    """Layer-1 part/zone tops against the deck underside (information only)."""
    pts = deck.reshape(-1, 3)
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    out = []
    for e in bodies(entries):
        if e["layer"] != 1:
            continue
        if all(e["pos"][k] + e["size"][k] > lo[k] and e["pos"][k] < hi[k] for k in (0, 1)):
            top = e["pos"][2] + e["size"][2]
            out.append(f"report: {e['name']} top z={top:.1f} mm, gap to deck underside "
                       f"(z={lo[2]:.1f}) = {lo[2] - top:.1f} mm")
    return out


# ---- SVG ----------------------------------------------------------------------
def fmt(v: float) -> str:
    """Every number in the SVG: one decimal, no negative zero."""
    return "%.1f" % (round(float(v), 1) + 0.0)


def columns(tris: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> dict:
    """Vertical rays at every (xs[i], ys[j]); {(i, j): solid z intervals (n, 2)}.

    Adapted from the overhang scan: barycentric hit test per column, hits
    sorted by z and paired. Columns that miss the mesh are absent.
    """
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    txmin = np.minimum(np.minimum(a[:, 0], b[:, 0]), c[:, 0])
    txmax = np.maximum(np.maximum(a[:, 0], b[:, 0]), c[:, 0])
    tymin = np.minimum(np.minimum(a[:, 1], b[:, 1]), c[:, 1])
    tymax = np.maximum(np.maximum(a[:, 1], b[:, 1]), c[:, 1])
    out = {}
    for i, x in enumerate(xs):
        mx = (txmin <= x) & (txmax >= x)
        if not mx.any():
            continue
        tx = tris[mx]
        tymn, tymx = tymin[mx], tymax[mx]
        for j, y in enumerate(ys):
            m = (tymn <= y) & (tymx >= y)
            t = tx[m]
            if len(t) == 0:
                continue
            p0, p1, p2 = t[:, 0], t[:, 1], t[:, 2]
            d = (p1[:, 1] - p2[:, 1]) * (p0[:, 0] - p2[:, 0]) + (p2[:, 0] - p1[:, 0]) * (p0[:, 1] - p2[:, 1])
            ok = np.abs(d) > 1e-12
            d = np.where(ok, d, 1.0)
            l0 = ((p1[:, 1] - p2[:, 1]) * (x - p2[:, 0]) + (p2[:, 0] - p1[:, 0]) * (y - p2[:, 1])) / d
            l1 = ((p2[:, 1] - p0[:, 1]) * (x - p2[:, 0]) + (p0[:, 0] - p2[:, 0]) * (y - p2[:, 1])) / d
            l2 = 1 - l0 - l1
            hit = ok & (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
            if not hit.any():
                continue
            z = np.sort(l0[hit] * p0[hit, 2] + l1[hit] * p1[hit, 2] + l2[hit] * p2[hit, 2])
            if len(z) % 2:
                raise RuntimeError(f"odd ray crossings at x={x:.3f} y={y:.3f}: {z}")
            out[(i, j)] = z.reshape(-1, 2)
    return out


def height_rects(tris: np.ndarray, x0: float, y0: float) -> list[str]:
    """Height-map rects for one STL: 1 mm cells, 4 gray levels, runs merged per row."""
    xs = VIEW_X[0] + np.arange(NX) + CELL_OFF[0]
    ys = VIEW_Y[0] + np.arange(NY) + CELL_OFF[1]
    zs = tris.reshape(-1, 3)[:, 2]
    zmin, zmax = float(zs.min()), float(zs.max())
    cols = columns(tris, xs, ys)
    level = {k: min(3, int(4 * (float(iv[:, 1].max()) - zmin) / (zmax - zmin + 1e-9)))
             for k, iv in cols.items()}
    rects = []
    for j in range(NY - 1, -1, -1):                     # top of the drawing first
        i = 0
        while i < NX:
            lv = level.get((i, j))
            if lv is None:
                i += 1
                continue
            k = i
            while k + 1 < NX and level.get((k + 1, j)) == lv:
                k += 1
            rects.append(f'<rect x="{fmt(x0 + i * SCALE)}" y="{fmt(y0 + (NY - 1 - j) * SCALE)}" '
                         f'width="{fmt((k - i + 1) * SCALE)}" height="{fmt(SCALE)}" fill="{HEIGHT_FILLS[lv]}"/>')
            i = k + 1
    return rects


def port_sides(ports: str) -> list[str]:
    """Side tags in the ports string, first-seen order, no repeats."""
    seen = []
    for seg in ports.split(";"):
        seg = seg.strip()
        for tag in SIDE_TAGS:
            if seg.startswith(tag) and tag[:2] not in seen:
                seen.append(tag[:2])
    return seen


def port_triangle(side: str, bx0: float, by0: float, bx1: float, by1: float, colour: str) -> str:
    """6 px triangle on the middle of one box side, pointing outward (SVG px;
    by0 is the top edge = +y, by1 the bottom edge = -y)."""
    cx, cy = (bx0 + bx1) / 2.0, (by0 + by1) / 2.0
    h = PORT_SIZE / 2.0
    if side == "-x":
        pts = [(bx0, cy - h), (bx0, cy + h), (bx0 - PORT_SIZE, cy)]
    elif side == "+x":
        pts = [(bx1, cy - h), (bx1, cy + h), (bx1 + PORT_SIZE, cy)]
    elif side == "+y":
        pts = [(cx - h, by0), (cx + h, by0), (cx, by0 - PORT_SIZE)]
    else:  # "-y"
        pts = [(cx - h, by1), (cx + h, by1), (cx, by1 + PORT_SIZE)]
    return f'<polygon points="{" ".join(fmt(px) + "," + fmt(py) for px, py in pts)}" fill="{colour}"/>'


def panel_svg(title: str, tris: np.ndarray, entries: list[dict], left: float) -> tuple[list[str], int]:
    """(svg lines, legend line count) for one panel whose left edge is at `left` px."""
    x0, y0 = left + MARGIN, MARGIN + TITLE_H
    w, h = NX * SCALE, NY * SCALE
    sx_ = lambda x: x0 + (x - VIEW_X[0]) * SCALE          # noqa: E731  mm -> px
    sy_ = lambda y: y0 + (VIEW_Y[1] - y) * SCALE          # noqa: E731  mm -> px, flipped
    dark = "#333333"
    g = [f'<text x="{fmt(x0)}" y="{fmt(MARGIN + 8)}" font-size="{fmt(12)}" font-weight="bold">{escape(title)}</text>',
         f'<rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(w)}" height="{fmt(h)}" fill="#ffffff" '
         f'stroke="#999999" stroke-width="{fmt(1)}"/>',
         f'<g shape-rendering="crispEdges">']
    g += height_rects(tris, x0, y0)
    g.append("</g>")
    texts = []
    for e in entries:
        colour = PALETTE[(e["idx"] - 1) % len(PALETTE)]
        (px, py, _), (sx, sy, _) = e["pos"], e["size"]
        bx0, bx1 = sx_(px), sx_(px + sx)
        by0, by1 = sy_(py + sy), sy_(py)
        if e["kind"] == "part":
            g.append(f'<rect x="{fmt(bx0)}" y="{fmt(by0)}" width="{fmt(bx1 - bx0)}" height="{fmt(by1 - by0)}" '
                     f'fill="{colour}" fill-opacity="0.35" stroke="{colour}" stroke-width="{fmt(1)}"/>')
        elif e["kind"] == "zone":
            g.append(f'<rect x="{fmt(bx0)}" y="{fmt(by0)}" width="{fmt(bx1 - bx0)}" height="{fmt(by1 - by0)}" '
                     f'fill="none" stroke="{colour}" stroke-width="{fmt(1)}" stroke-dasharray="{fmt(4)} {fmt(3)}"/>')
        else:
            g.append(f'<circle cx="{fmt((bx0 + bx1) / 2)}" cy="{fmt((by0 + by1) / 2)}" r="{fmt(sx / 2 * SCALE)}" '
                     f'fill="none" stroke="{colour}" stroke-width="{fmt(1)}" stroke-dasharray="{fmt(4)} {fmt(3)}"/>')
        if e["kind"] != "note":
            for side in port_sides(e["ports"]):
                g.append(port_triangle(side, bx0, by0, bx1, by1, colour if e["kind"] == "part" else dark))
        texts.append(f'<text x="{fmt((bx0 + bx1) / 2)}" y="{fmt((by0 + by1) / 2 + 3)}" font-size="{fmt(9)}" '
                     f'text-anchor="middle" fill="{dark}">{e["idx"]}</text>')
    g += texts
    g.append(f'<text x="{fmt(x0)}" y="{fmt(y0 + h + 16)}" font-size="{fmt(10)}" fill="{dark}">front of car -&gt;</text>')
    n_lines = 0
    for e in entries:
        line = f"{e['idx']}. {e['name']} | held by: {e['held_by']} | ports: {e['ports']}"
        for k, part in enumerate(textwrap.wrap(line, LEGEND_WRAP, subsequent_indent="   ")):
            g.append(f'<text x="{fmt(x0)}" y="{fmt(y0 + h + LEGEND_TOP + n_lines * LEGEND_LINE)}" '
                     f'font-size="{fmt(9)}" font-family="monospace" xml:space="preserve">{escape(part)}</text>')
            n_lines += 1
    return g, n_lines


def build_svg(tray: np.ndarray, deck: np.ndarray, l1: list[dict], l2: list[dict]) -> str:
    a, n1 = panel_svg("Layer 1 - electronics tray", tray, l1, 0.0)
    b, n2 = panel_svg("Layer 2 - electronics deck", deck, l2, PANEL_W)
    width = 2 * PANEL_W
    height = MARGIN + TITLE_H + NY * SCALE + LEGEND_TOP + max(n1, n2) * LEGEND_LINE + MARGIN
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width)}" height="{fmt(height)}" '
            f'viewBox="0 0 {fmt(width)} {fmt(height)}" font-family="sans-serif">\n'
            f'<rect x="{fmt(0)}" y="{fmt(0)}" width="{fmt(width)}" height="{fmt(height)}" fill="#ffffff"/>')
    return head + "\n" + "\n".join(a + b) + "\n</svg>\n"


# ---- self-check -----------------------------------------------------------------
def self_check(stls: list[np.ndarray] | None = None) -> None:
    """Plant one bug per check and prove it is caught; raises AssertionError if one
    slips through. Takes no argument when scripts/run_checks.py calls it."""
    if stls is None:
        stls = [parse_stl(TRAY_STL.read_bytes()), parse_stl(DECK_STL.read_bytes())]
    solid = {"name": "fake solid", "size": [10.0, 10.0, 1.0], "pos": [0.0, 0.0, 8.0],
             "kind": "part", "held_by": "", "ports": "", "layer": 1, "idx": 1}
    res = check_material([solid], stls, [])
    caught_a = any(not ok for ok, _ in res)
    print(f"self-check (a) box planted inside the tray material is caught: {'ok' if caught_a else 'NOT CAUGHT'}")
    box1 = dict(solid, name="fake A", pos=[200.0, 0.0, 0.0], idx=1)
    box2 = dict(solid, name="fake B", pos=[205.0, 5.0, 0.5], idx=2)
    caught_b = any(not ok for ok, _ in check_overlap([box1, box2]))
    clean = all(ok for ok, _ in check_overlap([box1, dict(box2, pos=[210.0, 0.0, 0.0])]))
    print(f"self-check (b) two overlapping boxes are caught: {'ok' if caught_b else 'NOT CAUGHT'}")
    print(f"self-check (b) two boxes touching at a face are not flagged: {'ok' if clean else 'FALSE ALARM'}")
    assert caught_a and caught_b and clean, "a planted bug was not caught (see the lines above)"


# ---- main -----------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_SVG, help="SVG to write (default docs/electronics_layout.svg)")
    ap.add_argument("--no-svg", action="store_true", help="check only, write no SVG")
    ap.add_argument("--self-check", action="store_true", help="plant bugs and prove the checks catch them")
    args = ap.parse_args(argv)

    if args.self_check:
        try:
            self_check()
        except AssertionError as e:
            print(f"self-check: FAIL: {e}")
            return 1
        print("self-check: PASS")
        return 0

    try:
        parts1, _ = load_layout(TRAY_SCAD)
        parts2, pegs = load_layout(DECK_SCAD)
        l1, l2 = make_entries(parts1, 1, TRAY_SCAD), make_entries(parts2, 2, DECK_SCAD)
    except (FileNotFoundError, RuntimeError, subprocess.SubprocessError) as e:
        print(f"layout: FAIL: {e}", file=sys.stderr)
        print(f"layout: FAIL: {e}")
        return 1
    tray = parse_stl(TRAY_STL.read_bytes())
    deck = parse_stl(DECK_STL.read_bytes())
    entries = l1 + l2

    results = []
    for res in (check_material(entries, [tray, deck], pegs),
                check_overlap(entries),
                check_support(entries, [tray, deck])):
        for ok, text in res:
            results.append(ok)
            print(f"PASS {text}" if ok else f"FAIL {text}")
    for line in report_gaps(entries, deck):
        print(line)

    failed = results.count(False)
    if not args.no_svg:
        try:
            svg = build_svg(tray, deck, l1, l2)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_bytes(svg.encode("ascii", errors="xmlcharrefreplace"))
            print(f"svg: {args.out}  ({args.out.stat().st_size} bytes)")
        except RuntimeError as e:
            failed += 1
            print(f"FAIL svg: {e}")
    print(f"layout: {len(entries)} entries, {failed} checks failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
