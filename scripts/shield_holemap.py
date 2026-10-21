#!/usr/bin/env python
"""Check a proto-shield hole map (JSON) and draw it as an SVG + a build MD.

Stdlib only. The layout lives in a JSON file (see docs/shield_layout.json): a grid
of named holes ("ROW/COL", e.g. "U2/1", "L2/-2"), copper groups, parts with pins
in holes, jumper wires (top side), solder bridges (bottom side), Dupont sockets to
the Uno, and the nets that must (and must not) end up connected. This script
checks that data and renders it. It owns no layout data itself.

Checks (each prints a PASS/FAIL line, details indented under a FAIL):
  1 refs          every hole / PART.PIN referenced anywhere exists
  2 one-lead      each hole carries at most one lead (part pin, wire end, socket)
  3 bridges       each bridge joins two ADJACENT holes, none listed twice
  4 bodies        no part body covers a foreign lead; no two bodies overlap
  5 connectivity  union-find over copper, bridges, wires, sockets, joins, part
                  internals: every net in ONE component, no two nets in one
                  component (short); WARN for a lead-used component with no net
  6 steps         every hole-looking token in the build steps names a real hole

WHAT PASSING PROVES, AND WHAT IT DOES NOT
-----------------------------------------
It proves the JSON is self-consistent: the holes named exist, no hole takes two
leads, the bridges are physically possible, and the copper/wire/bridge graph
joins exactly the nets the JSON declares. It does not prove the JSON matches the
real shield (the copper groups are typed from a photo or a continuity test), that
a part fits its body rectangle, or that anything is soldered correctly. Those are
measured on the board, never inferred here.

Usage:  python scripts/shield_holemap.py LAYOUT.json [--svg OUT.svg] [--md OUT.md]
        python scripts/shield_holemap.py --self-check
Exit:   0 every check passed (--self-check: all planted bugs were caught)
        1 any FAIL, an unreadable layout, or a failed self-check
On FAIL the outputs are still written, with FAILED in the title.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import re
import sys
import textwrap
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

LEGEND_COL = 340   # px per legend column (4 across at the 1400 px page)

# 3D renders of the finished board (scripts/shield_render3d.py); embedded when present
RENDER_FILES = ("shield_3d_top.png", "shield_3d_bottom.png")
RENDER_CAPTION = [
    "Top: straight down on the finished top side. Bottom: straight up from below, the board flipped top-over-bottom (USB end still on the "
    "left, the digital-header edge now at the bottom) - the solder bridges; the top-side parts show as cyan "
    "ghost outlines and the top-side wires as pink lines, labelled (a thin line leads from a label pushed "
    "off its part).",
    "The INTENDED build, not a photo: catalogue part sizes, board outline = hole field + 3 mm, board colour "
    "guessed; Dupont leads leave straight along their column (Uno header positions are not in the layout).",
]

HOLE_RE = re.compile(r"^([A-Z][A-Z0-9]*)/(-?\d+)$")
# A hole-looking token inside free text. The lookbehind stops "3V3/5" matching "V3/5".
TOKEN_RE = re.compile(r"(?<![A-Za-z0-9])[A-Z][A-Z0-9]*/-?\d+")

PITCH = 48
EPS = 1e-9
NET_PALETTE = ["#d62728", "#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b",
               "#e377c2", "#17becf", "#bcbd22", "#7f7f7f"]
KIND_PALETTE = ["#4e79a7", "#f28e2b", "#59a14f", "#b07aa1", "#edc948", "#76b7b2",
                "#e15759", "#9c755f", "#bab0ac", "#ff9da7"]
NO_NET = "#999999"


def esc(s) -> str:
    return escape(str(s), {'"': "&quot;"})


# ---- union-find -------------------------------------------------------------------
class UF:
    def __init__(self):
        self.p: dict[str, str] = {}

    def find(self, a: str) -> str:
        self.p.setdefault(a, a)
        root = a
        while self.p[root] != root:
            root = self.p[root]
        while self.p[a] != root:
            self.p[a], a = root, self.p[a]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


# ---- geometry ---------------------------------------------------------------------
def wire_path(w: dict) -> list:
    """Holes a top-side wire visits: from, its optional "via" corners, to."""
    return [w.get("from")] + list(w.get("via", [])) + [w.get("to")]


def body_shape(body):
    """('rect', r0, r1, c0, c1) | ('circle', r, c, rad) | None."""
    if not body:
        return None
    if "rect" in body:
        r0, r1, c0, c1 = (float(v) for v in body["rect"])
        return ("rect", min(r0, r1), max(r0, r1), min(c0, c1), max(c0, c1))
    if "circle" in body:
        r, c, rad = (float(v) for v in body["circle"])
        return ("circle", r, c, rad)
    return None


def shape_contains(sh, row: float, col: float) -> bool:
    if sh[0] == "rect":
        return sh[1] - EPS <= row <= sh[2] + EPS and sh[3] - EPS <= col <= sh[4] + EPS
    return math.hypot(row - sh[1], col - sh[2]) <= sh[3] + EPS


def _rect_circle_overlap(rect, circ) -> bool:
    dr = max(rect[1] - circ[1], 0.0, circ[1] - rect[2])
    dc = max(rect[3] - circ[2], 0.0, circ[2] - rect[4])
    return math.hypot(dr, dc) < circ[3] - EPS


def shapes_overlap(a, b) -> bool:
    """Positive-area overlap; touching edges do not count."""
    if a[0] == "rect" and b[0] == "rect":
        return (min(a[2], b[2]) - max(a[1], b[1]) > EPS
                and min(a[4], b[4]) - max(a[3], b[3]) > EPS)
    if a[0] == "circle" and b[0] == "circle":
        return math.hypot(a[1] - b[1], a[2] - b[2]) < a[3] + b[3] - EPS
    return _rect_circle_overlap(a, b) if a[0] == "rect" else _rect_circle_overlap(b, a)


# ---- analysis ---------------------------------------------------------------------
def analyze(data: dict) -> dict:
    """Run the six checks. Raises ValueError if the grid itself is unusable."""
    grid = data.get("grid") or {}
    rows = grid.get("rows")
    if not rows:
        raise ValueError("grid.rows is missing or empty")
    row_idx = {r: i for i, r in enumerate(rows)}

    # -- hole set --
    grid_errs: list[str] = []
    holeset: set[str] = set()
    for k, ent in enumerate(grid.get("holes", [])):
        c0, c1 = ent["cols"]
        for rn in ent["rows"]:
            if rn not in row_idx:
                grid_errs.append(f"grid.holes[{k}]: row {rn!r} is not in grid.rows")
                continue
            for c in range(int(c0), int(c1) + 1):
                holeset.add(f"{rn}/{c}")

    def hole_rc(h: str):
        m = HOLE_RE.match(h)
        return (row_idx[m.group(1)], int(m.group(2))) if m and m.group(1) in row_idx else None

    parts = data.get("parts", [])
    offb = data.get("offboard_parts", [])
    wires = data.get("wires", [])
    sockets = data.get("sockets", [])
    bridges = data.get("bridges", [])
    joins = data.get("joins", [])
    directs = data.get("direct_uno", [])
    nets = data.get("nets", {})
    net_colors = data.get("net_colors", {})

    # -- pin table: "ID.pin" -> hole (parts) or None (off-board parts) --
    pins: dict[str, str | None] = {}
    offb_target: dict[str, str] = {}
    ids_seen: set[str] = set()
    ref_errs = list(grid_errs)
    for p in parts:
        if p["id"] in ids_seen:
            ref_errs.append(f"duplicate part id {p['id']}")
        ids_seen.add(p["id"])
        for pn, h in p.get("pins", {}).items():
            pins[f"{p['id']}.{pn}"] = h
    for p in offb:
        if p["id"] in ids_seen:
            ref_errs.append(f"duplicate part id {p['id']}")
        ids_seen.add(p["id"])
        for pn, target in p.get("pins", {}).items():
            pins[f"{p['id']}.{pn}"] = None
            offb_target[f"{p['id']}.{pn}"] = target

    # -- 1 refs --
    def need_hole(h, where):
        if not isinstance(h, str) or h not in holeset:
            ref_errs.append(f"{where}: no such hole {h!r}")

    def need_pin(ref, where):
        if ref not in pins:
            ref_errs.append(f"{where}: no such pin {ref!r}")

    for p in parts:
        for pn, h in p.get("pins", {}).items():
            need_hole(h, f"part {p['id']} pin {pn}")
        for grp in p.get("internal", []):
            for pn in grp:
                need_pin(f"{p['id']}.{pn}", f"part {p['id']} internal")
    for ref, target in offb_target.items():
        need_pin(target, f"off-board pin {ref}")
    for i, b in enumerate(bridges):
        if len(b) != 2:
            ref_errs.append(f"bridge #{i}: needs exactly 2 holes, got {b!r}")
            continue
        for h in b:
            need_hole(h, f"bridge #{i}")
    for w in wires:
        need_hole(w.get("from"), f"wire {w.get('id')} from")
        need_hole(w.get("to"), f"wire {w.get('id')} to")
        for v in w.get("via", []):
            need_hole(v, f"wire {w.get('id')} via")
        path = wire_path(w)
        if len(path) > 2:   # a routed wire runs straight between corners
            for a, b in zip(path, path[1:]):
                ra, rb = hole_rc(a) if isinstance(a, str) else None, hole_rc(b) if isinstance(b, str) else None
                if ra and rb and ra[0] != rb[0] and ra[1] != rb[1]:
                    ref_errs.append(f"wire {w.get('id')}: leg {a} -> {b} is not straight (same row or column)")
        wn = w.get("net")
        if wn and wn not in nets and wn not in net_colors:
            ref_errs.append(f"wire {w.get('id')}: net {wn!r} is in neither nets nor net_colors")
    for s in sockets:
        need_hole(s.get("hole"), f"socket {s.get('uno')}")
    for j in joins:
        need_pin(j.get("a"), "join a")
        need_pin(j.get("b"), "join b")
    # direct_uno "from" may be free text, so it is never a ref failure
    for net, members in nets.items():
        for m in members:
            if m.startswith("uno:"):
                continue
            if HOLE_RE.match(m):
                need_hole(m, f"net {net}")
            else:
                need_pin(m, f"net {net}")

    results: list[dict] = []

    def add(n, name, details, ok_text):
        results.append({"n": n, "name": name, "status": "FAIL" if details else "PASS",
                        "summary": (f"{len(details)} problem(s)" if details else ok_text),
                        "details": details})

    add(1, "refs", ref_errs, "every hole and PART.PIN reference exists")

    # -- 2 one lead per hole --
    users: dict[str, list[str]] = defaultdict(list)
    for p in parts:
        for pn, h in p.get("pins", {}).items():
            users[h].append(f"{p['id']}.{pn}")
    for w in wires:
        users[w.get("from")].append(f"wire {w.get('id')} (from)")
        users[w.get("to")].append(f"wire {w.get('id')} (to)")
    for s in sockets:
        users[s.get("hole")].append(f"socket {s.get('uno')}")
    lead2 = [f"{h} carries {len(u)} leads: {', '.join(u)}" for h, u in users.items() if len(u) > 1]
    add(2, "one-lead", lead2, f"{len(users)} lead-used holes, none shared")

    # -- 3 bridges --
    br_errs = []
    seen_br: set[frozenset] = set()
    for b in bridges:
        if len(b) != 2:
            continue
        key = frozenset(b)
        if key in seen_br:
            br_errs.append(f"bridge {b[0]} - {b[1]} is listed twice")
        seen_br.add(key)
        ra, rb = hole_rc(b[0]), hole_rc(b[1])
        if ra is None or rb is None:
            continue  # reported by refs
        if abs(ra[0] - rb[0]) + abs(ra[1] - rb[1]) != 1:
            br_errs.append(f"bridge {b[0]} - {b[1]} is not between adjacent holes")
    add(3, "bridges", br_errs, f"{len(bridges)} bridge(s), all adjacent and unique")

    # -- 4 bodies --
    body_errs = []
    shapes = []
    for p in parts:
        sh = body_shape(p.get("body"))
        if sh is None:
            continue
        shapes.append((p["id"], sh))
        own = {h for h in p.get("pins", {}).values()}
        for h in users:
            rc = hole_rc(h) if isinstance(h, str) else None
            if rc is None or h in own:
                continue
            if shape_contains(sh, rc[0], rc[1]):
                body_errs.append(f"body of {p['id']} covers {h}, used by {', '.join(users[h])}")
    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            if shapes_overlap(shapes[i][1], shapes[j][1]):
                body_errs.append(f"bodies of {shapes[i][0]} and {shapes[j][0]} overlap")
    add(4, "bodies", body_errs, f"{len(shapes)} body(ies), no foreign lead inside, no overlap")

    # -- 5 connectivity --
    uf = UF()
    for p in parts:
        for pn, h in p.get("pins", {}).items():
            uf.union(f"{p['id']}.{pn}", h)
        for grp in p.get("internal", []):
            for a, b in zip(grp, grp[1:]):
                uf.union(f"{p['id']}.{a}", f"{p['id']}.{b}")
    for ref, target in offb_target.items():
        uf.union(ref, target)
    for c in grid.get("copper", []):
        hs = c.get("holes", [])
        for a, b in zip(hs, hs[1:]):
            uf.union(a, b)
    for b in bridges:
        if len(b) == 2:
            uf.union(b[0], b[1])
    for w in wires:
        uf.union(w.get("from"), w.get("to"))
    for s in sockets:
        uf.union(s.get("hole"), "uno:" + str(s.get("uno")))
    for j in joins:
        uf.union(j.get("a"), j.get("b"))
    for d in directs:
        src = d.get("from")
        if src in pins:
            uf.union(src, "uno:" + str(d.get("uno")))

    con_errs: list[str] = []
    root_nets: dict[str, list[str]] = defaultdict(list)
    for net, members in nets.items():
        groups: dict[str, list[str]] = defaultdict(list)
        for m in members:
            groups[uf.find(m)].append(m)
            if net not in root_nets[uf.find(m)]:
                root_nets[uf.find(m)].append(net)
        if len(groups) > 1:
            parts_txt = " | ".join(", ".join(g) for g in groups.values())
            con_errs.append(f"net {net} is split into {len(groups)} groups: {parts_txt}")
    for root, nn in root_nets.items():
        if len(nn) > 1:
            txt = "; ".join(f"{n}: {', '.join(nets[n])}" for n in nn)
            con_errs.append(f"nets {' + '.join(nn)} are SHORTED together ({txt})")
    warns: list[str] = []
    float_seen: set[str] = set()
    for h, u in users.items():
        if not isinstance(h, str) or h not in holeset:
            continue
        root = uf.find(h)
        if root not in root_nets and root not in float_seen:
            float_seen.add(root)
            members = sorted(x for x, uh in users.items() if isinstance(x, str) and uf.find(x) == root)
            warns.append(f"floating component with no net member: lead holes {', '.join(members)}")
    add(5, "connectivity", con_errs, f"{len(nets)} net(s) each in one component, none shorted")
    results[-1]["warns"] = warns

    # -- 6 steps --
    step_errs = []
    for i, st in enumerate(data.get("steps", []), 1):
        texts = [("title", st.get("title", ""))]
        texts += [("do", t) for t in st.get("do", [])]
        texts.append(("check", st.get("check", "")))
        for where, t in texts:
            for tok in TOKEN_RE.findall(str(t)):
                if tok not in holeset:
                    step_errs.append(f"step {i} ({where}): {tok} is not a hole")
    add(6, "steps", step_errs, f"{len(data.get('steps', []))} step(s), every hole token exists")

    # -- colours (net of each pin) --
    net_list = list(nets)

    def net_color(net: str) -> str:
        if net in net_colors:
            return net_colors[net]
        return NET_PALETTE[net_list.index(net) % len(NET_PALETTE)] if net in net_list else NO_NET

    pin_color = {}
    pin_net = {}
    for ref in pins:
        nn = root_nets.get(uf.find(ref))
        pin_color[ref] = net_color(nn[0]) if nn else NO_NET
        pin_net[ref] = nn[0] if nn else None

    # -- 7 bridge hazards (WARN only, never changes ok) --
    def hole_net(h: str):
        nn = root_nets.get(uf.find(h))
        return nn[0] if nn else None

    br_ends = {h for b in bridges if len(b) == 2 for h in b if h in holeset}
    pairs: set[tuple[str, str]] = set()
    for h in br_ends | {h for h in users if isinstance(h, str) and h in holeset}:
        ri, c = hole_rc(h)
        na = hole_net(h)
        if na is None:
            continue
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            if not 0 <= ri + dr < len(rows):
                continue
            nb_hole = f"{rows[ri + dr]}/{c + dc}"
            if nb_hole not in holeset:
                continue
            nb = hole_net(nb_hole)
            if nb is None or nb == na or (h not in br_ends and nb_hole not in br_ends):
                continue
            pairs.add(tuple(sorted(((h, na), (nb_hole, nb)))))
    hazards = sorted(pairs)

    return {"rows": rows, "row_idx": row_idx, "holeset": holeset, "hole_rc": hole_rc,
            "hazards": hazards,
            "results": results, "ok": all(r["status"] != "FAIL" for r in results),
            "pins": pins, "pin_color": pin_color, "pin_net": pin_net, "net_color": net_color,
            "users": users}


def print_results(A: dict) -> None:
    for r in A["results"]:
        print(f"{r['status']} {r['n']} {r['name']}: {r['summary']}")
        for d in r["details"]:
            print(f"  - {d}")
        for w in r.get("warns", []):
            print(f"WARN {r['n']} {r['name']}: {w}")
    hz = A["hazards"]
    if hz:
        print(f"WARN 7 hazards: {len(hz)} adjacent pairs of different nets next to a solder bridge")
        for (h, na), (n2, nb) in hz:
            print(f"WARN 7 hazards: {h} ({na}) next to {n2} ({nb})")
    else:
        print("PASS 7 hazards: no adjacent different-net pair next to a solder bridge")


# ---- SVG --------------------------------------------------------------------------
def title_of(data: dict, ok: bool) -> list[str]:
    t = data.get("title") or ["Shield hole map"]
    t = [t] if isinstance(t, str) else list(t)
    t[0] = f"{t[0]}  [{'PASS' if ok else 'FAILED'}]"
    return t


def _seg_hits_box(x1, y1, x2, y2, b) -> bool:
    """Liang-Barsky: does segment (x1,y1)-(x2,y2) touch box b = (x0,y0,x1,y1)?"""
    t0, t1 = 0.0, 1.0
    for p, q in ((x1 - x2, x1 - b[0]), (x2 - x1, b[2] - x1),
                 (y1 - y2, y1 - b[1]), (y2 - y1, b[3] - y1)):
        if p == 0:
            if q < 0:
                return False
        elif p < 0:
            t0 = max(t0, q / p)
        else:
            t1 = min(t1, q / p)
        if t0 > t1:
            return False
    return True


def _leader_seg(text, fs, cx, cy, hx, hy):
    """Leader from a hole edge to the label box edge, or None if the label is close."""
    if math.hypot(cx - hx, cy - hy) <= 0.75 * PITCH:
        return None
    w_, h_ = Placer.size(text, fs)
    qx = min(max(hx, cx - w_ / 2), cx + w_ / 2)
    qy = min(max(hy, cy - h_ / 2), cy + h_ / 2)
    dd = math.hypot(qx - hx, qy - hy)
    if dd <= 6:
        return None
    return hx + (qx - hx) * 6 / dd, hy + (qy - hy) * 6 / dd, qx, qy


class Placer:
    """Greedy text-label placer. Boxes and segments are obstacles; a label is a box
    centred on a candidate point. Width estimate: 0.62 * font size * chars (bold Arial)."""

    def __init__(self, xmin, xmax, ymin, ymax):
        self.boxes: list[tuple] = []
        self.segs: list[tuple] = []  # (x1, y1, x2, y2, half-width incl. margin)
        self.lim = (xmin, xmax, ymin, ymax)
        self.right = 0.0

    def box(self, x0, y0, x1, y1) -> None:
        self.boxes.append((x0, y0, x1, y1))

    def seg(self, x1, y1, x2, y2, hw) -> None:
        self.segs.append((x1, y1, x2, y2, hw))

    def ring(self, cx, cy, r) -> None:
        pts = [(cx + r * math.cos(k * math.pi / 16), cy + r * math.sin(k * math.pi / 16))
               for k in range(33)]
        for a, b in zip(pts, pts[1:]):
            self.seg(a[0], a[1], b[0], b[1], 2)

    @staticmethod
    def size(text, fs):
        return 0.62 * fs * len(text) + 6, fs  # +6: capitals in bold run wider than 0.62 em

    def free(self, b) -> bool:
        xmin, xmax, ymin, ymax = self.lim
        if b[0] < xmin or b[2] > xmax or b[1] < ymin or b[3] > ymax:
            return False
        for o in self.boxes:
            if b[0] < o[2] and o[0] < b[2] and b[1] < o[3] and o[1] < b[3]:
                return False
        for x1, y1, x2, y2, hw in self.segs:
            if _seg_hits_box(x1, y1, x2, y2, (b[0] - hw, b[1] - hw, b[2] + hw, b[3] + hw)):
                return False
        return True

    def leader_clear(self, seg) -> bool:
        """A leader may not cross a placed label box (hole/pin/dot obstacle boxes are
        <= 14 px square and ignored; the box holding the leader's start is ignored)."""
        sx, sy, qx, qy = seg
        for o in self.boxes:
            if o[2] - o[0] <= 14 and o[3] - o[1] <= 14:
                continue
            if o[0] <= sx <= o[2] and o[1] <= sy <= o[3]:
                continue
            if _seg_hits_box(sx, sy, qx, qy, o):
                return False
        return True

    def place(self, text, fs, cands, what, src=None):
        """First free candidate centre wins; returns (cx, cy). Raises if none is free.
        src=(hx, hy): also require the label's leader line to be clear of other labels."""
        w, h = self.size(text, fs)
        for cx, cy in cands:
            b = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            if self.free(b):
                if src is not None:
                    ld = _leader_seg(text, fs, cx, cy, src[0], src[1])
                    if ld is not None and not self.leader_clear(ld):
                        continue
                self.boxes.append(b)
                self.right = max(self.right, b[2])
                return cx, cy
        raise ValueError(f"no free spot for label {what}: {text}")

    def fixed(self, text, fs, cx, cy):
        w, h = self.size(text, fs)
        self.boxes.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
        self.right = max(self.right, cx + w / 2)


def _rings(cx, cy, start=8, stop=240, step=8):
    """Fallback candidates: 16 compass points on growing rings around (cx, cy)."""
    for r in range(start, stop, step):
        for k in range(16):
            a = k * math.pi / 8
            yield cx + r * math.cos(a), cy + r * math.sin(a)


def find_renders(folder: Path) -> list[tuple[Path, tuple[int, int]]]:
    """The 3D renders next to an output file, with their pixel sizes (PNG IHDR)."""
    out = []
    for name in RENDER_FILES:
        p = folder / name
        if p.exists():
            raw = p.read_bytes()[16:24]
            out.append((p, (int.from_bytes(raw[:4], "big"), int.from_bytes(raw[4:], "big"))))
    return out


def render_svg(data: dict, A: dict, renders=()) -> str:
    rows, row_idx, holeset, hole_rc = A["rows"], A["row_idx"], A["holeset"], A["hole_rc"]
    grid = data.get("grid", {})
    n = len(rows)
    rc = {h: hole_rc(h) for h in holeset}
    cols_with = sorted({c for (_, c) in rc.values()})
    cmin, cmax = (cols_with[0], cols_with[-1]) if cols_with else (0, 0)
    title = title_of(data, A["ok"])
    left = 90
    top = 110 + 18 * (len(title) - 1) + 18   # +18: underside note line
    NOTE = ("Black dashed bars = solder bridges on the UNDERSIDE, drawn as seen through the board "
            "from the top. Flip the board top-over-bottom (USB end stays LEFT) - the bottom 3D "
            "render below shows that view.")

    def X(c):
        return left + (c - cmin) * PITCH

    def Y(r):
        return top + r * PITCH

    width = max(1400, X(cmax) + 90, math.ceil(0.62 * 12 * len(NOTE)) + 40)
    ybot = Y(n - 1)
    kinds: list[str] = []
    for p in data.get("parts", []) + data.get("offboard_parts", []):
        if p.get("kind") not in kinds:
            kinds.append(p.get("kind"))

    def kind_color(k):
        return KIND_PALETTE[kinds.index(k) % len(KIND_PALETTE)] if k in kinds else "#888888"

    # ---- label placement: obstacles first, then fixed texts, then the rest ----
    pl = Placer(10, max(width, 10 ** 4), top - 44, ybot + 44)
    SOCK = 30
    for (r_, c_) in rc.values():
        pl.box(X(c_) - 5, Y(r_) - 5, X(c_) + 5, Y(r_) + 5)
    parts_pl = data.get("parts", [])
    for p in parts_pl:
        for h in p.get("pins", {}).values():
            if h in rc:
                pl.box(X(rc[h][1]) - 7, Y(rc[h][0]) - 7, X(rc[h][1]) + 7, Y(rc[h][0]) + 7)
        sh = body_shape(p.get("body"))
        if sh is None:
            continue
        if sh[0] == "rect":
            x0, y0, x1, y1 = X(sh[3]), Y(sh[1]), X(sh[4]), Y(sh[2])
            for e in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
                pl.seg(*e, 2)
        else:
            pl.ring(X(sh[2]), Y(sh[1]), sh[3] * PITCH)
    for b in data.get("bridges", []):
        if len(b) == 2 and b[0] in rc and b[1] in rc:
            pl.seg(X(rc[b[0]][1]), Y(rc[b[0]][0]), X(rc[b[1]][1]), Y(rc[b[1]][0]), 4.5)
    wires_pl = [w for w in data.get("wires", []) if all(h in rc for h in wire_path(w))]
    for w in wires_pl:
        path = wire_path(w)
        for a, b in zip(path, path[1:]):
            pl.seg(X(rc[a][1]), Y(rc[a][0]), X(rc[b][1]), Y(rc[b][0]), 2.5)
    for w in wires_pl:
        for h in (w.get("from"), w.get("to")):
            if h in rc:
                pl.box(X(rc[h][1]) - 5, Y(rc[h][0]) - 5, X(rc[h][1]) + 5, Y(rc[h][0]) + 5)
    for (h, _na), (n2, _nb) in A["hazards"]:
        mx = (X(rc[h][1]) + X(rc[n2][1])) / 2
        my = (Y(rc[h][0]) + Y(rc[n2][0])) / 2
        pl.box(mx - 5, my - 5, mx + 5, my + 5)
    socks_pl = [s_ for s_ in data.get("sockets", []) if s_.get("hole") in rc]
    for s_ in socks_pl:
        x, y = X(rc[s_["hole"]][1]), Y(rc[s_["hole"]][0])
        up = str(s_.get("uno", "")).startswith("D")
        pl.seg(x, y + (-7 if up else 7), x, y - SOCK if up else y + SOCK, 3)
    labels: list[str] = []
    leaders: list[str] = []

    def leader(text, fs, cx, cy, hx, hy):
        """Thin line hole edge -> label box edge when the label sits far from its hole."""
        ld = _leader_seg(text, fs, cx, cy, hx, hy)
        if ld is None:
            return
        sx, sy, qx, qy = ld
        leaders.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{qx:.1f}" y2="{qy:.1f}" '
                       f'stroke="#888" stroke-width="0.75"/>')
        pl.seg(sx, sy, qx, qy, 1.5)

    def emit(text, fs, cx, cy, extra, anchor="middle"):
        labels.append(f'<text x="{cx:.1f}" y="{cy + 0.35 * fs:.1f}" font-size="{fs}" '
                      f'text-anchor="{anchor}" {extra}>{esc(text)}</text>')

    # fixed texts: grid labels, row names, column numbers
    for lb in grid.get("labels", []):
        r, c = lb["at"]
        cx, cy = pl.place(lb["text"], 11, [(X(c), Y(r) - 4)] + list(_rings(X(c), Y(r) - 4, 6)),
                          "grid label")
        emit(lb["text"], 11, cx, cy, 'fill="#444"')
    for i, rn in enumerate(rows):
        w_, h_ = Placer.size(rn, 12)
        pl.fixed(rn, 12, left - 48 - w_ / 2, Y(i))
        emit(rn, 12, left - 48, Y(i), 'fill="#222"', "end")
    for c in cols_with:
        for yy in (top - 52, ybot + 58):
            pl.fixed(str(c), 10, X(c), yy - 3.5)
            emit(str(c), 10, X(c), yy - 3.5, 'fill="#555"')
    # part ids
    for p in parts_pl:
        sh = body_shape(p.get("body"))
        if sh is None:
            continue
        col = kind_color(p.get("kind"))
        # label text at 55% of the outline colour so pale kinds stay readable on white
        col = "#" + "".join(f"{int(int(col[i:i + 2], 16) * 0.55):02x}" for i in (1, 3, 5))
        if sh[0] == "rect":
            x0, y0, x1, y1 = X(sh[3]), Y(sh[1]), X(sh[4]), Y(sh[2])
        else:
            x0, y0 = X(sh[2]) - sh[3] * PITCH, Y(sh[1]) - sh[3] * PITCH
            x1, y1 = X(sh[2]) + sh[3] * PITCH, Y(sh[1]) + sh[3] * PITCH
        w_, h_ = Placer.size(p["id"], 11)
        cands = [(x0 + w_ / 2, y0 - h_ / 2 - 3), (x1 - w_ / 2, y0 - h_ / 2 - 3),
                 (x0 + w_ / 2, y1 + h_ / 2 + 3), (x1 - w_ / 2, y1 + h_ / 2 + 3),
                 (x0 - w_ / 2 - 3, (y0 + y1) / 2), (x1 + w_ / 2 + 3, (y0 + y1) / 2)]
        cands += list(_rings((x0 + x1) / 2, (y0 + y1) / 2, 8))
        cx, cy = pl.place(p["id"], 11, cands, "part id")
        emit(p["id"], 11, cx, cy, f'fill="{col}"')
    # socket labels
    for s_ in socks_pl:
        h = s_["hole"]
        x, y = X(rc[h][1]), Y(rc[h][0])
        up = str(s_.get("uno", "")).startswith("D")
        # an analog socket's arrow points DOWN across the board; say where it goes
        t = f'{s_.get("uno")}' if up else f'{s_.get("uno")} (bottom header)'
        w_, h_ = Placer.size(t, 10)
        ty = (y - SOCK - h_ / 2 - 2) if up else (y + SOCK + h_ / 2 + 2)
        cands = [(x, ty), (x - PITCH / 2, ty), (x + PITCH / 2, ty)] + list(_rings(x, ty, 6))
        cx, cy = pl.place(t, 10, cands, "socket", (x, y))
        emit(t, 10, cx, cy, 'fill="#333"')
        leader(t, 10, cx, cy, x, y)
    # pin labels
    for p in parts_pl:
        for pn, h in p.get("pins", {}).items():
            if h not in rc:
                continue
            x, y = X(rc[h][1]), Y(rc[h][0])
            lt = pn
            if pn == "KEY":
                lt = "KEY"   # the hollow ring + legend say "no pin"; a long label lands far away
            elif len(pn) == 1 and A["pin_net"].get(p["id"] + "." + pn):
                lt = A["pin_net"][p["id"] + "." + pn]
            w_, h_ = Placer.size(lt, 9)
            hp = PITCH / 2
            cands = [(x, y + hp), (x, y - hp), (x + 8 + w_ / 2, y), (x - 8 - w_ / 2, y),
                     (x + hp, y + hp), (x - hp, y + hp), (x + hp, y - hp), (x - hp, y - hp)]
            cands += list(_rings(x, y, 14))
            cx, cy = pl.place(lt, 9, cands, f'pin {p["id"]}.{pn}', (x, y))
            leader(lt, 9, cx, cy, x, y)
            emit(lt, 9, cx, cy, 'fill="#222" stroke="#fff" stroke-width="2" paint-order="stroke"')
    # wire ids
    for w in wires_pl:
        path = wire_path(w)   # the id goes beside the longest leg
        a, b = max(zip(path, path[1:]), key=lambda ab: math.hypot(rc[ab[1]][0] - rc[ab[0]][0],
                                                                  rc[ab[1]][1] - rc[ab[0]][1]))
        x1, y1, x2, y2 = X(rc[a][1]), Y(rc[a][0]), X(rc[b][1]), Y(rc[b][0])
        L = math.hypot(x2 - x1, y2 - y1) or 1.0
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        t = str(w.get("id"))
        w_, h_ = Placer.size(t, 10)
        off = abs(nx) * w_ / 2 + abs(ny) * h_ / 2 + 4
        cands = []
        for f in (0.5, 0.35, 0.65, 0.2, 0.8):
            px, py = x1 + (x2 - x1) * f, y1 + (y2 - y1) * f
            cands += [(px + nx * off, py + ny * off), (px - nx * off, py - ny * off)]
        cands += list(_rings((x1 + x2) / 2, (y1 + y2) / 2, 8))
        cx, cy = pl.place(t, 10, cands, "wire id")
        emit(t, 10, cx, cy, 'fill="#111" stroke="#fff" stroke-width="3" paint-order="stroke"')
    width = max(width, math.ceil(pl.right) + 10)

    out: list[str] = []
    # copper bars under the holes
    for cg in grid.get("copper", []):
        hs = [h for h in cg.get("holes", []) if h in rc]
        out.append(f'<g class="copper"><title>{esc(cg.get("name", ""))}</title>')
        for h in hs:
            out.append(f'<circle cx="{X(rc[h][1])}" cy="{Y(rc[h][0])}" r="10" fill="#dcdcdc"/>')
        byrow: dict[int, list[str]] = defaultdict(list)
        bycol: dict[int, list[str]] = defaultdict(list)
        for h in hs:
            byrow[rc[h][0]].append(h)
            bycol[rc[h][1]].append(h)
        for grp in list(byrow.values()) + list(bycol.values()):
            grp = sorted(grp, key=lambda h: rc[h])
            for a, b in zip(grp, grp[1:]):
                out.append(f'<line x1="{X(rc[a][1])}" y1="{Y(rc[a][0])}" x2="{X(rc[b][1])}" '
                           f'y2="{Y(rc[b][0])}" stroke="#dcdcdc" stroke-width="20" '
                           f'stroke-linecap="round"/>')
        out.append("</g>")
    # holes
    for h in sorted(rc):
        out.append(f'<circle cx="{X(rc[h][1])}" cy="{Y(rc[h][0])}" r="4" fill="#fff" '
                   f'stroke="#777" stroke-width="1"><title>{esc(h)}</title></circle>')
    # bodies
    for p in data.get("parts", []):
        sh = body_shape(p.get("body"))
        if sh is None:
            continue
        col = kind_color(p.get("kind"))
        if sh[0] == "rect":
            x0, y0 = X(sh[3]), Y(sh[1])
            out.append(f'<rect x="{x0}" y="{y0}" width="{(sh[4] - sh[3]) * PITCH}" '
                       f'height="{(sh[2] - sh[1]) * PITCH}" fill="{col}" fill-opacity="0.15" '
                       f'stroke="{col}" stroke-width="2"/>')
        else:
            out.append(f'<circle cx="{X(sh[2])}" cy="{Y(sh[1])}" r="{sh[3] * PITCH}" fill="{col}" '
                       f'fill-opacity="0.15" stroke="{col}" stroke-width="2"/>')
    # bridges
    for b in data.get("bridges", []):
        if len(b) == 2 and b[0] in rc and b[1] in rc:
            out.append(f'<line x1="{X(rc[b[0]][1])}" y1="{Y(rc[b[0]][0])}" x2="{X(rc[b[1]][1])}" '
                       f'y2="{Y(rc[b[1]][0])}" stroke="#222" stroke-width="7" '
                       f'stroke-dasharray="5 3"><title>bottom-side solder bridge {esc(b[0])} - '
                       f'{esc(b[1])}</title></line>')
    # wires
    for w in data.get("wires", []):
        a, b = w.get("from"), w.get("to")
        path = wire_path(w)
        if not all(h in rc for h in path):
            continue
        col = A["net_color"](w["net"]) if w.get("net") else NO_NET
        pts = " ".join(f"{X(rc[h][1])},{Y(rc[h][0])}" for h in path)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" '
                   f'stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.9">'
                   f'<title>{esc(w.get("id"))}: {esc(a)} to {esc(b)} {esc(w.get("note", ""))}'
                   f'</title></polyline>')
    # wire endpoint dots (from / to, not via corners)
    for w in wires_pl:
        col = A["net_color"](w["net"]) if w.get("net") else NO_NET
        for h in (w.get("from"), w.get("to")):
            if h in rc:
                out.append(f'<circle cx="{X(rc[h][1])}" cy="{Y(rc[h][0])}" r="4" fill="{col}" '
                           f'stroke="#222" stroke-width="1"/>')
    # pins
    for p in data.get("parts", []):
        for pn, h in p.get("pins", {}).items():
            if h not in rc:
                continue
            x, y = X(rc[h][1]), Y(rc[h][0])
            pcol = A["pin_color"][p["id"] + "." + pn]
            if pn == "KEY":
                out.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#fff" stroke="#999" '
                           f'stroke-width="1.5"><title>{esc(p["id"])}.KEY (no pin) in {esc(h)}'
                           f'</title></circle>')
                continue
            out.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{pcol}" '
                       f'stroke="#222" stroke-width="1"><title>{esc(p["id"])}.{esc(pn)} in '
                       f'{esc(h)}</title></circle>')
    # bridge hazards: small red x between the two holes of each pair
    for (h, _na), (n2, _nb) in A["hazards"]:
        mx = (X(rc[h][1]) + X(rc[n2][1])) / 2
        my = (Y(rc[h][0]) + Y(rc[n2][0])) / 2
        out.append(f'<path d="M{mx - 4},{my - 4} L{mx + 4},{my + 4} M{mx - 4},{my + 4} '
                   f'L{mx + 4},{my - 4}" stroke="#e00000" stroke-width="2" fill="none">'
                   f'<title>hazard: {esc(h)} next to {esc(n2)}</title></path>')
    # sockets: short arrow out (D* up, A* down)
    for s in data.get("sockets", []):
        h = s.get("hole")
        if h not in rc:
            continue
        x, y = X(rc[h][1]), Y(rc[h][0])
        up = str(s.get("uno", "")).startswith("D")
        y2 = y - SOCK if up else y + SOCK
        out.append(f'<line x1="{x}" y1="{y + (-7 if up else 7)}" x2="{x}" y2="{y2}" '
                   f'stroke="#333" stroke-width="2" marker-end="url(#arr)"/>')
    out.extend(leaders)
    # all placed text labels (grid labels, row names, col numbers, part ids, sockets,
    # pins, wire ids) go on top
    out.extend(labels)

    # legend
    ly = ybot + 90
    out.append(f'<text x="20" y="{ly}" font-size="13" font-weight="bold">Legend</text>')
    ly += 22
    items = []
    for k in kinds:
        items.append(("rect", kind_color(k), f"part: {k}"))
    by_col: dict[str, list[str]] = {}
    for net in data.get("nets", {}):
        by_col.setdefault(A["net_color"](net), []).append(net)
    for col_, names in by_col.items():
        items.append(("line", col_, "net " + " / ".join(names)))
    items += [("copper", "#dcdcdc", "copper strip / rail"),
              ("bridge", "#222", "bottom-side solder bridge"),
              ("wire", "#888", "top-side jumper wire (net colour)"),
              ("sock", "#333", "socket: Dupont to the Uno"),
              ("hazard", "#e00000", "red x: a bridge sits next to another net - meter these two "
                                    "holes, must be SILENT"),
              ("dot", "#888", "dot at a wire end: soldered there (wires are insulated everywhere else)"),
              ("ring", "#999", "hollow ring: no pin (polarity key)")]
    x = 20
    for kind, col, text in items:
        wide = 0.62 * 11 * len(text) + 6 > LEGEND_COL - 25
        if wide:
            if x > 20:
                x, ly = 20, ly + 22
        elif x > width - LEGEND_COL:
            x, ly = 20, ly + 22
        if kind == "rect":
            out.append(f'<rect x="{x}" y="{ly - 10}" width="16" height="12" fill="{col}" '
                       f'fill-opacity="0.3" stroke="{col}" stroke-width="2"/>')
        elif kind == "copper":
            out.append(f'<rect x="{x}" y="{ly - 10}" width="16" height="12" fill="{col}"/>')
        elif kind == "hazard":
            out.append(f'<path d="M{x + 4},{ly - 8} L{x + 12},{ly} M{x + 4},{ly} L{x + 12},{ly - 8}" '
                       f'stroke="{col}" stroke-width="2" fill="none"/>')
        elif kind == "dot":
            out.append(f'<circle cx="{x + 8}" cy="{ly - 4}" r="4" fill="{col}" stroke="#222" '
                       f'stroke-width="1"/>')
        elif kind == "ring":
            out.append(f'<circle cx="{x + 8}" cy="{ly - 4}" r="6" fill="#fff" stroke="{col}" '
                       f'stroke-width="1.5"/>')
        elif kind == "bridge":
            out.append(f'<line x1="{x}" y1="{ly - 4}" x2="{x + 16}" y2="{ly - 4}" stroke="{col}" '
                       f'stroke-width="6" stroke-dasharray="4 2"/>')
        else:
            out.append(f'<line x1="{x}" y1="{ly - 4}" x2="{x + 16}" y2="{ly - 4}" stroke="{col}" '
                       f'stroke-width="3"/>')
        out.append(f'<text x="{x + 22}" y="{ly}" font-size="11" fill="#222">{esc(text)}</text>')
        x += width if wide else LEGEND_COL
    ly += 28
    notes = []
    for d in data.get("direct_uno", []):
        notes.append(f"direct to Uno {d.get('uno')}: {d.get('from')} {d.get('note', '')}".strip())
    for p in data.get("offboard_parts", []):
        pn = ", ".join(f"{k}->{v}" for k, v in p.get("pins", {}).items())
        notes.append(f"off-board {p['id']} ({p.get('kind', '')}): {pn} {p.get('note', '')}".strip())
    for j in data.get("joins", []):
        notes.append(f"join {j.get('a')} <-> {j.get('b')} {j.get('note', '')}".strip())
    for t in notes:
        for line in textwrap.wrap(t, 190) or [""]:
            out.append(f'<text x="20" y="{ly}" font-size="11" fill="#333">{esc(line)}</text>')
            ly += 15
    # finished-build 3D renders (scripts/shield_render3d.py), embedded side by side
    if renders:
        ly += 20
        out.append(f'<text x="20" y="{ly}" font-size="13">Finished build - 3D render of this layout '
                   f'(scripts/shield_render3d.py)</text>')
        for line in (w for c in RENDER_CAPTION for w in textwrap.wrap(c, 180)):
            ly += 16
            out.append(f'<text x="20" y="{ly}" font-size="11" fill="#333">{esc(line)}</text>')
        ly += 10
        iw = width - 40          # one render per row, full width, so the labels stay legible
        ih = 0
        for i, (png, (pw, ph)) in enumerate(renders):
            h = round(iw * ph / pw)
            ih = max(ih, h)
            b64 = base64.b64encode(png.read_bytes()).decode("ascii")
            out.append(f'<image x="20" y="{ly + i * (h + 10)}" width="{iw}" height="{h}" '
                       f'href="data:image/png;base64,{b64}"/>')
        ly += len(renders) * (ih + 10)
    height = ly + 20

    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="Arial, Helvetica, sans-serif" font-weight="bold">',
            '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" '
            'orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#333"/></marker></defs>',
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>']
    for i, t in enumerate(title):
        head.append(f'<text x="20" y="{30 + 18 * i}" font-size="{20 if i == 0 else 12}" '
                    f'font-weight="bold" '
                    f'fill="{("#b00020" if not A["ok"] else "#111") if i == 0 else "#333"}">'
                    f'{esc(t)}</text>')
    head.append(f'<text x="20" y="{30 + 18 * len(title)}" font-size="12" font-weight="bold" '
                f'fill="#b00020">{esc(NOTE)}</text>')
    return "\n".join(head + out + ["</svg>"]) + "\n"


# ---- Markdown ---------------------------------------------------------------------
def render_md(data: dict, A: dict, renders=()) -> str:
    title = title_of(data, A["ok"])
    L = [f"# {title[0]}", ""]
    for t in title[1:]:
        L += [t, ""]
    if renders:
        L += ["## Finished build (3D render, scripts/shield_render3d.py)", ""]
        L += [" ".join(RENDER_CAPTION), ""]
        L += [f"![{p.stem}]({p.name})" for p, _ in renders] + [""]
    if data.get("notes"):
        L += ["## Notes", ""] + [f"- {t}" for t in data["notes"]] + [""]
    L += ["## Parts", ""]
    for p in data.get("parts", []):
        pn = ", ".join(f"{k} = {v}" for k, v in p.get("pins", {}).items())
        L.append(f"- **{p['id']}** ({p.get('kind', '')}): {pn}" +
                 (f" - {p['note']}" if p.get("note") else ""))
    for p in data.get("offboard_parts", []):
        pn = ", ".join(f"{k} -> {v}" for k, v in p.get("pins", {}).items())
        L.append(f"- **{p['id']}** ({p.get('kind', '')}, off-board): {pn}" +
                 (f" - {p['note']}" if p.get("note") else ""))
    L.append("")
    if data.get("wires"):
        L += ["## Wires (top side)", ""]
        for w in data["wires"]:
            L.append(f"- **{w.get('id')}**: {' -> '.join(str(h) for h in wire_path(w))}" +
                     (f" [{w['net']}]" if w.get("net") else "") +
                     (f" - {w['note']}" if w.get("note") else ""))
        L.append("")
    if data.get("bridges"):
        L += ["## Solder bridges (bottom side)", ""]
        L += [f"- {b[0]} - {b[1]}" for b in data["bridges"] if len(b) == 2] + [""]
    if data.get("sockets") or data.get("direct_uno") or data.get("joins"):
        L += ["## Uno sockets and joins", ""]
        for s in data.get("sockets", []):
            L.append(f"- Dupont {s.get('hole')} -> Uno {s.get('uno')}")
        for d in data.get("direct_uno", []):
            L.append(f"- direct: {d.get('from')} -> Uno {d.get('uno')}" +
                     (f" - {d['note']}" if d.get("note") else ""))
        for j in data.get("joins", []):
            L.append(f"- join {j.get('a')} <-> {j.get('b')}" +
                     (f" - {j['note']}" if j.get("note") else ""))
        L.append("")
    L += ["## Steps", ""]
    for i, st in enumerate(data.get("steps", []), 1):
        L.append(f"{i}. **{st.get('title', '')}**")
        for d in st.get("do", []):
            L.append(f"   - {d}")
        if st.get("check"):
            L.append(f"   - Check: {st['check']}")
    if A["hazards"]:
        L += ["", "## Solder-bridge hazards - meter each pair SILENT after the bridges", ""]
        for (h, na), (n2, nb) in A["hazards"]:
            L.append(f"- [ ] {h} ({na}) - {n2} ({nb}): silent")
    L += ["", "## Check results", ""]
    for r in A["results"]:
        L.append(f"- {r['status']} {r['n']} {r['name']}: {r['summary']}")
        for d in r["details"]:
            L.append(f"  - {d}")
        for w in r.get("warns", []):
            L.append(f"  - WARN: {w}")
    L.append("")
    return "\n".join(L)


def write_ascii(path: Path, text: str, svg: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("ascii", errors="xmlcharrefreplace" if svg else "replace"))


# ---- self-check -------------------------------------------------------------------
def _clean_layout() -> dict:
    return {
        "title": ["tiny clean layout"],
        "grid": {"rows": ["A", "B", "C"],
                 "holes": [{"rows": ["A", "B", "C"], "cols": [1, 3]}],
                 "copper": [{"name": "rail", "holes": ["A/1", "A/2", "A/3"]}],
                 "labels": [{"text": "rail", "at": [0, 2]}]},
        "parts": [{"id": "R1", "kind": "resistor", "pins": {"1": "B/1", "2": "B/3"},
                   "body": {"rect": [1, 1, 1, 3]}, "note": "test part"}],
        "bridges": [["A/1", "B/1"], ["B/3", "C/3"]],
        "wires": [{"id": "W1", "from": "A/3", "to": "C/1", "net": "GND", "note": ""}],
        "sockets": [{"hole": "C/3", "uno": "D2"}],
        "nets": {"GND": ["A/1", "R1.1", "C/1"], "SIG": ["R1.2", "uno:D2"]},
        "net_colors": {"GND": "#222222", "SIG": "#d62728"},
        "steps": [{"title": "Place R1", "do": ["R1 pin 1 in B/1, pin 2 in B/3"],
                   "check": "A/1 and B/1 bridged"}],
    }


def _status(data: dict) -> dict[int, str]:
    return {r["n"]: r["status"] for r in analyze(data)["results"]}


def self_check() -> None:
    """Plant one bug per check and prove it is caught; raises AssertionError if one
    slips through. Takes no argument when scripts/run_checks.py calls it."""
    import copy

    clean = _clean_layout()
    A = analyze(clean)
    assert A["ok"], "clean layout should pass: " + str([r for r in A["results"] if r["details"]])
    print("self-check clean layout passes all six checks: ok")

    # smoke test: both renderers run, are pure ASCII, and carry the status in the title
    svg, md = render_svg(clean, A), render_md(clean, A)
    for name, txt in (("svg", svg), ("md", md)):
        txt.encode("ascii")
        assert "[PASS]" in txt, f"{name} title lacks PASS"
    assert svg.startswith("<svg") and "</svg>" in svg
    print("self-check renderers produce ASCII svg and md: ok")

    def must_fail(label: str, n: int, mutate, needle: str = "") -> None:
        d = copy.deepcopy(clean)
        mutate(d)
        res = {r["n"]: r for r in analyze(d)["results"]}
        caught = res[n]["status"] == "FAIL" and (not needle or any(needle in x for x in res[n]["details"]))
        print(f"self-check ({n}) {label}: {'ok' if caught else 'NOT CAUGHT'}")
        assert caught, f"planted bug not caught by check {n}: {label}"
        # the failing layout must still render, with FAILED in the title
        assert "[FAILED]" in render_svg(d, analyze(d)) and "[FAILED]" in render_md(d, analyze(d))

    must_fail("a hole used by two leads", 2,
              lambda d: d["wires"].append({"id": "W3", "from": "C/1", "to": "C/2", "net": "GND"}),
              "C/1")
    must_fail("a bridge between non-adjacent holes", 3,
              lambda d: d["bridges"].append(["A/2", "C/2"]), "not between adjacent")
    must_fail("a bridge listed twice", 3, lambda d: d["bridges"].append(["B/1", "A/1"]), "twice")
    must_fail("a part body covering a foreign lead", 4,
              lambda d: d["wires"].append({"id": "W4", "from": "B/2", "to": "C/2", "net": "GND"}),
              "B/2")
    must_fail("two overlapping bodies", 4,
              lambda d: d["parts"].append({"id": "R2", "kind": "resistor", "pins": {"1": "C/1"},
                                           "body": {"circle": [1, 2, 0.8]}}), "overlap")
    must_fail("a bridge shorting two nets", 5,
              lambda d: d["bridges"].append(["A/3", "B/3"]), "SHORTED")
    must_fail("a net split in two", 5,
              lambda d: d["bridges"].remove(["B/3", "C/3"]), "split")
    must_fail("a missing hole", 1, lambda d: d["wires"][0].update(to="Z/9"), "Z/9")
    must_fail("a wire via that leaves a diagonal leg", 1,
              lambda d: d["wires"][0].update(via=["B/2"]), "not straight")
    must_fail("a step naming a missing hole", 6,
              lambda d: d["steps"][0]["do"].append("solder at A/9"), "A/9")

    # (7) bridge hazards: the clean layout has bridge endpoint B/3 (SIG) next to A/3 (GND)
    assert A["hazards"] == [(("A/3", "GND"), ("B/3", "SIG"))], f"hazards: {A['hazards']}"
    nobr = copy.deepcopy(clean)
    nobr["bridges"] = []
    assert analyze(nobr)["hazards"] == [], "no bridge, so no hazard"
    assert A["ok"], "hazards must not change ok"
    print("self-check (7) a bridge next to another net gives exactly one hazard (warn only): ok")

    # a floating lead-used component is a WARN, not a FAIL
    d = copy.deepcopy(clean)
    d["wires"].append({"id": "W5", "from": "B/2", "to": "C/2"})
    d["parts"][0]["body"] = {"rect": [0.5, 0.5, 1, 3]}
    r5 = {r["n"]: r for r in analyze(d)["results"]}[5]
    assert r5["status"] == "PASS" and r5["warns"], "floating component should WARN only"
    print("self-check (5) a floating component warns without failing: ok")


# ---- main -------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("layout", nargs="?", type=Path, help="layout JSON (e.g. docs/shield_layout.json)")
    ap.add_argument("--svg", type=Path, help="SVG to write")
    ap.add_argument("--md", type=Path, help="build-steps Markdown to write")
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
    if args.layout is None:
        ap.error("a layout JSON is required unless --self-check is given")

    try:
        data = json.loads(args.layout.read_text(encoding="utf-8"))
        A = analyze(data)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        print(f"layout: FAIL: {type(e).__name__}: {e}")
        return 1

    print_results(A)
    try:
        if args.svg:
            write_ascii(args.svg, render_svg(data, A, find_renders(args.svg.parent)), True)
            print(f"svg: {args.svg}")
        if args.md:
            write_ascii(args.md, render_md(data, A, find_renders(args.md.parent)), False)
            print(f"md: {args.md}")
    except (OSError, KeyError, TypeError, ValueError) as e:
        print(f"FAIL output: {type(e).__name__}: {e}")
        return 1
    failed = sum(1 for r in A["results"] if r["status"] == "FAIL")
    print(f"holemap: {failed} check(s) failed" if failed else "holemap: all checks passed")
    return 0 if A["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
