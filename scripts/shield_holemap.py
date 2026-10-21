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
import json
import math
import re
import sys
import textwrap
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

HOLE_RE = re.compile(r"^([A-Z][A-Z0-9]*)/(-?\d+)$")
# A hole-looking token inside free text. The lookbehind stops "3V3/5" matching "V3/5".
TOKEN_RE = re.compile(r"(?<![A-Za-z0-9])[A-Z][A-Z0-9]*/-?\d+")

PITCH = 34
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
    for ref in pins:
        nn = root_nets.get(uf.find(ref))
        pin_color[ref] = net_color(nn[0]) if nn else NO_NET

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
            "pins": pins, "pin_color": pin_color, "net_color": net_color,
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


def render_svg(data: dict, A: dict) -> str:
    rows, row_idx, holeset, hole_rc = A["rows"], A["row_idx"], A["holeset"], A["hole_rc"]
    grid = data.get("grid", {})
    n = len(rows)
    rc = {h: hole_rc(h) for h in holeset}
    cols_with = sorted({c for (_, c) in rc.values()})
    cmin, cmax = (cols_with[0], cols_with[-1]) if cols_with else (0, 0)
    title = title_of(data, A["ok"])
    left = 90
    top = 110 + 18 * (len(title) - 1)

    def X(c):
        return left + (c - cmin) * PITCH

    def Y(r):
        return top + r * PITCH

    width = max(1400, X(cmax) + 90)
    ybot = Y(n - 1)
    kinds: list[str] = []
    for p in data.get("parts", []) + data.get("offboard_parts", []):
        if p.get("kind") not in kinds:
            kinds.append(p.get("kind"))

    def kind_color(k):
        return KIND_PALETTE[kinds.index(k) % len(KIND_PALETTE)] if k in kinds else "#888888"

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
            lx, ly = x0 + 3, y0 + 12
        else:
            out.append(f'<circle cx="{X(sh[2])}" cy="{Y(sh[1])}" r="{sh[3] * PITCH}" fill="{col}" '
                       f'fill-opacity="0.15" stroke="{col}" stroke-width="2"/>')
            lx, ly = X(sh[2]) - sh[3] * PITCH + 3, Y(sh[1]) - sh[3] * PITCH + 12
        out.append(f'<text x="{lx}" y="{ly}" font-size="11" font-weight="bold" fill="{col}">'
                   f'{esc(p["id"])}</text>')
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
        if a not in rc or b not in rc:
            continue
        col = A["net_color"](w["net"]) if w.get("net") else NO_NET
        x1, y1, x2, y2 = X(rc[a][1]), Y(rc[a][0]), X(rc[b][1]), Y(rc[b][0])
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" '
                   f'stroke-width="3" stroke-linecap="round" stroke-opacity="0.9">'
                   f'<title>{esc(w.get("id"))}: {esc(a)} to {esc(b)} {esc(w.get("note", ""))}'
                   f'</title></line>')
        out.append(f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 4}" font-size="10" '
                   f'text-anchor="middle" fill="#111" stroke="#fff" stroke-width="3" '
                   f'paint-order="stroke">{esc(w.get("id"))}</text>')
    # pins
    for p in data.get("parts", []):
        for pn, h in p.get("pins", {}).items():
            if h not in rc:
                continue
            x, y = X(rc[h][1]), Y(rc[h][0])
            pcol = A["pin_color"][p["id"] + "." + pn]
            out.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{pcol}" '
                       f'stroke="#222" stroke-width="1"><title>{esc(p["id"])}.{esc(pn)} in '
                       f'{esc(h)}</title></circle>')
            out.append(f'<text x="{x + 7}" y="{y + 13}" font-size="8" fill="#222" '
                       f'stroke="#fff" stroke-width="2" paint-order="stroke">{esc(pn)}</text>')
    # bridge hazards: small red x between the two holes of each pair
    for (h, _na), (n2, _nb) in A["hazards"]:
        mx = (X(rc[h][1]) + X(rc[n2][1])) / 2
        my = (Y(rc[h][0]) + Y(rc[n2][0])) / 2
        out.append(f'<path d="M{mx - 4},{my - 4} L{mx + 4},{my + 4} M{mx - 4},{my + 4} '
                   f'L{mx + 4},{my - 4}" stroke="#e00000" stroke-width="2" fill="none">'
                   f'<title>hazard: {esc(h)} next to {esc(n2)}</title></path>')
    # sockets: short arrow out toward the nearer edge
    for s in data.get("sockets", []):
        h = s.get("hole")
        if h not in rc:
            continue
        x, y = X(rc[h][1]), Y(rc[h][0])
        up = rc[h][0] < (n - 1) / 2
        y2 = y - 24 if up else y + 24
        out.append(f'<line x1="{x}" y1="{y + (-7 if up else 7)}" x2="{x}" y2="{y2}" '
                   f'stroke="#333" stroke-width="2" marker-end="url(#arr)"/>')
        out.append(f'<text x="{x}" y="{y2 - 4 if up else y2 + 12}" font-size="10" '
                   f'text-anchor="middle" fill="#333">-&gt; {esc(s.get("uno"))}</text>')
    # grid labels
    for lb in grid.get("labels", []):
        r, c = lb["at"]
        out.append(f'<text x="{X(c)}" y="{Y(r)}" font-size="11" fill="#444" '
                   f'text-anchor="middle">{esc(lb["text"])}</text>')
    # row names and col numbers
    for i, rn in enumerate(rows):
        out.append(f'<text x="{left - 48}" y="{Y(i) + 4}" font-size="12" text-anchor="end" '
                   f'fill="#222">{esc(rn)}</text>')
    for c in cols_with:
        for yy in (top - 52, ybot + 58):
            out.append(f'<text x="{X(c)}" y="{yy}" font-size="10" text-anchor="middle" '
                       f'fill="#555">{c}</text>')

    # legend
    ly = ybot + 90
    out.append(f'<text x="20" y="{ly}" font-size="13" font-weight="bold">Legend</text>')
    ly += 22
    items = []
    for k in kinds:
        items.append(("rect", kind_color(k), f"part: {k}"))
    for net in data.get("nets", {}):
        items.append(("line", A["net_color"](net), f"net {net}"))
    items += [("copper", "#dcdcdc", "copper strip / rail"),
              ("bridge", "#222", "bottom-side solder bridge"),
              ("wire", "#888", "top-side jumper wire (net colour)"),
              ("sock", "#333", "socket: Dupont to the Uno")]
    x = 20
    for kind, col, text in items:
        if x > width - 240:
            x, ly = 20, ly + 22
        if kind == "rect":
            out.append(f'<rect x="{x}" y="{ly - 10}" width="16" height="12" fill="{col}" '
                       f'fill-opacity="0.3" stroke="{col}" stroke-width="2"/>')
        elif kind == "copper":
            out.append(f'<rect x="{x}" y="{ly - 10}" width="16" height="12" fill="{col}"/>')
        elif kind == "bridge":
            out.append(f'<line x1="{x}" y1="{ly - 4}" x2="{x + 16}" y2="{ly - 4}" stroke="{col}" '
                       f'stroke-width="6" stroke-dasharray="4 2"/>')
        else:
            out.append(f'<line x1="{x}" y1="{ly - 4}" x2="{x + 16}" y2="{ly - 4}" stroke="{col}" '
                       f'stroke-width="3"/>')
        out.append(f'<text x="{x + 22}" y="{ly}" font-size="11" fill="#222">{esc(text)}</text>')
        x += 230
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
    height = ly + 20

    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="Arial, Helvetica, sans-serif">',
            '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" '
            'orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#333"/></marker></defs>',
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>']
    for i, t in enumerate(title):
        head.append(f'<text x="20" y="{30 + 18 * i}" font-size="{20 if i == 0 else 12}" '
                    f'font-weight="{"bold" if i == 0 else "normal"}" '
                    f'fill="{("#b00020" if not A["ok"] else "#111") if i == 0 else "#333"}">'
                    f'{esc(t)}</text>')
    return "\n".join(head + out + ["</svg>"]) + "\n"


# ---- Markdown ---------------------------------------------------------------------
def render_md(data: dict, A: dict) -> str:
    title = title_of(data, A["ok"])
    L = [f"# {title[0]}", ""]
    for t in title[1:]:
        L += [t, ""]
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
            L.append(f"- **{w.get('id')}**: {w.get('from')} -> {w.get('to')}" +
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
            write_ascii(args.svg, render_svg(data, A), True)
            print(f"svg: {args.svg}")
        if args.md:
            write_ascii(args.md, render_md(data, A), False)
            print(f"md: {args.md}")
    except (OSError, KeyError, TypeError, ValueError) as e:
        print(f"FAIL output: {type(e).__name__}: {e}")
        return 1
    failed = sum(1 for r in A["results"] if r["status"] == "FAIL")
    print(f"holemap: {failed} check(s) failed" if failed else "holemap: all checks passed")
    return 0 if A["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
