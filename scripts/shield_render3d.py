"""3D render of the FINISHED proto shield, built from docs/shield_layout.json.

Writes an OpenSCAD model of the board as SHIELD_BUILD.md says it ends up
(carrier, headers, divider, jumper wires, Dupont leads; bottom-side copper and
solder bridges) and renders two PNGs with OpenSCAD's preview renderer:
  docs/shield_3d_top.png     - from above, the USB end on the LEFT
  docs/shield_3d_bottom.png  - from below (mirror image), the bridges

It is a picture of the INTENDED build, not of a real one: part sizes are
typical catalogue sizes, the board outline is the hole field plus a margin
(not the real shield outline), and the Dupont leads stop above their hole
because the Uno header positions are not in the layout file.

Usage: python scripts/shield_render3d.py [--layout docs/shield_layout.json]
       [--outdir docs] [--scad-only]
Exit 0 = both PNGs written; 1 = a check failed (printed as FAIL ...).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_scad import find_openscad  # noqa: E402

P = 2.54            # mm, hole pitch
BOARD_T = 1.6       # mm
MARGIN = 3.0        # mm of board around the outermost holes
IMG = (1600, 1100)

# Top-side wire routes (corner holes) from SHIELD_BUILD.md step 6. The first and
# last entries must equal the wire's from/to in the layout file (checked).
WIRE_ROUTES = {
    "w1": ["L3/7", "L3/9"],
    "w2": ["L3/8", "B/8"],
    "w3": ["L3/2", "L3/0", "V/0"],
    "w4": ["P4/7", "P4/-1", "P3/-1"],
    "w5": ["B/2", "B/-2", "P3/-2"],
}
# Carrier-top bridges (step 1), drawn as flat nested U's lying on the carrier:
# (pin a, pin b) -> (how far the U reaches in from the pin row, mm; wire dia, mm).
# Outer pin pairs reach further in so no two U's cross.
JOIN_SHAPE = {
    ("PWMA", "PWMB"): (4.2, 0.8), ("AIN2", "BIN2"): (3.0, 0.8), ("AIN1", "BIN1"): (1.8, 0.8),
    ("AO1", "BO1"): (3.6, 1.6), ("AO2", "BO2"): (1.9, 1.6),
}
CAP_C1 = (8.0, 12.5)   # 470 uF 25 V can, dia x length, mm (measured, hardware.md 2026-10-20)
JP1_CAP = ("UNO5V", "SERVO_V")   # JR: servo V+ from the Uno 5V

C_BOARD, C_COPPER, C_SOLDER = "#2f6b3a", "#c8873a", "#c9c9c9"
C_PLASTIC, C_PIN, C_CARRIER, C_CHIP = "#1d1d1d", "#d4af37", "#2a4f9e", "#111111"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Geo:
    def __init__(self, data: dict):
        self.rows = data["grid"]["rows"]
        self.ri = {r: i for i, r in enumerate(self.rows)}

    def xy(self, hole: str) -> tuple[float, float]:
        r, c = hole.split("/")
        return int(c) * P, -self.ri[r] * P

    def rc(self, hole: str) -> tuple[int, int]:
        r, c = hole.split("/")
        return self.ri[r], int(c)


def all_holes(data: dict, g: Geo) -> list[str]:
    out = []
    for blk in data["grid"]["holes"]:
        c0, c1 = blk["cols"]
        for r in blk["rows"]:
            out += [f"{r}/{c}" for c in range(c0, c1 + 1)]
    return sorted(set(out), key=g.rc)


def f(v: float) -> str:
    return f"{v:.3f}"


def seg(a, b, d, col) -> str:
    """Cylinder of diameter d from point a to point b (hull of two spheres)."""
    return (f'color("{col}") hull() {{ translate([{f(a[0])},{f(a[1])},{f(a[2])}]) sphere(d={f(d)}, $fn=12); '
            f'translate([{f(b[0])},{f(b[1])},{f(b[2])}]) sphere(d={f(d)}, $fn=12); }}')


def poly(pts, d, col) -> list[str]:
    return [seg(a, b, d, col) for a, b in zip(pts, pts[1:])]


def box(x0, y0, z0, x1, y1, z1, col) -> str:
    return (f'color("{col}") translate([{f(min(x0, x1))},{f(min(y0, y1))},{f(min(z0, z1))}]) '
            f'cube([{f(abs(x1 - x0))},{f(abs(y1 - y0))},{f(abs(z1 - z0))}]);')


def cyl(x, y, z, h, d, col, fn=24) -> str:
    return f'color("{col}") translate([{f(x)},{f(y)},{f(z)}]) cylinder(h={f(h)}, d={f(d)}, $fn={fn});'


def build_scad(data: dict) -> tuple[str, list[str], tuple[float, float, float]]:
    g = Geo(data)
    errs: list[str] = []
    holes = all_holes(data, g)
    xs = [g.xy(h)[0] for h in holes]
    ys = [g.xy(h)[1] for h in holes]
    bx0, bx1, by0, by1 = min(xs) - MARGIN, max(xs) + MARGIN, min(ys) - MARGIN, max(ys) + MARGIN
    s: list[str] = []

    # board with drilled holes
    drills = " ".join(f"translate([{f(g.xy(h)[0])},{f(g.xy(h)[1])},-1]) cylinder(h={f(BOARD_T + 2)}, d=1.0, $fn=10);"
                      for h in holes)
    s.append(f'color("{C_BOARD}") difference() {{ translate([{f(bx0)},{f(by0)},{f(-BOARD_T)}]) '
             f'cube([{f(bx1 - bx0)},{f(by1 - by0)},{f(BOARD_T)}]); {drills} }}')

    # the drill holes seen from below (the preview renderer does not show the cut)
    for h in holes:
        x, y = g.xy(h)
        s.append(cyl(x, y, -BOARD_T - 0.12, 0.05, 1.0, "#0a0a0a", 10))
    # bottom copper: pads + bars between ADJACENT holes of one group
    for grp in data["grid"].get("copper", []):
        hs = [h for h in grp["holes"] if h in holes]
        for h in hs:
            x, y = g.xy(h)
            s.append(cyl(x, y, -BOARD_T - 0.05, 0.05, 2.0, C_COPPER))
        for a in hs:
            for b in hs:
                (ra, ca), (rb, cb) = g.rc(a), g.rc(b)
                if (ra == rb and cb == ca + 1) or (ca == cb and rb == ra + 1):
                    (xa, ya), (xb, yb) = g.xy(a), g.xy(b)
                    s.append(box(xa - (0 if ra == rb else 0.9), ya - (0.9 if ra == rb else 0), -BOARD_T - 0.05,
                                 xb + (0 if ra == rb else 0.9), yb + (0.9 if ra == rb else 0), -BOARD_T, C_COPPER))

    used: set[str] = set()
    parts = {p["id"]: p for p in data["parts"]}

    # ---- TB6612 carrier on two 8-pin headers (step 1-2)
    tb = parts["TB"]
    r0, r1, c0, c1 = tb["body"]["rect"]
    zc = 2.5            # header spacer height
    s.append(box(c0 * P, -r0 * P, zc, c1 * P, -r1 * P, zc + 1.6, C_CARRIER))
    for pn, h in tb["pins"].items():
        x, y = g.xy(h)
        used.add(h)
        s.append(box(x - 1.27, y - 1.27, 0, x + 1.27, y + 1.27, zc, C_PLASTIC))
        s.append(box(x - 0.32, y - 0.32, -BOARD_T - 1.5, x + 0.32, y + 0.32, zc + 1.6 + 1.2, C_PIN))
        s.append(cyl(x, y, zc + 1.6, 0.6, 1.6, C_SOLDER, 12))
    cx, cy = (c0 + c1) / 2 * P, -(r0 + r1) / 2 * P
    s.append(box(cx - 3.9, cy - 4.0, zc + 1.6, cx + 3.9, cy + 4.0, zc + 1.6 + 1.4, C_CHIP))
    # marker dot on PWMA (step 1)
    px, py = g.xy(tb["pins"]["PWMA"])
    s.append(cyl(px + 1.4, py - 2.0, zc + 1.6, 0.1, 1.2, "#ffffff", 16))
    top = zc + 1.6 + 1.2
    for j in data.get("joins", []):
        a, b = j["a"].split(".")[1], j["b"].split(".")[1]
        key = (a, b) if (a, b) in JOIN_SHAPE else (b, a)
        if key not in JOIN_SHAPE:
            errs.append(f"join {a}-{b} has no shape in JOIN_SHAPE")
            continue
        reach, d = JOIN_SHAPE[key]
        (xa, ya), (xb, yb) = g.xy(tb["pins"][a]), g.xy(tb["pins"][b])
        inward = -1.0 if ya > cy else 1.0          # top row reaches down, bottom row up
        zw = top + 0.2 + d / 2
        col = data["net_colors"].get(next((n for n, m in data["nets"].items() if f"TB.{a}" in m), ""), "#555555")
        s += poly([(xa, ya, top), (xa, ya + inward * reach, zw), (xb, yb + inward * reach, zw), (xb, yb, top)], d, col)
    # C1 lying flat on the carrier at the VMOT / GND2 end, C2 across the same tips (step 1)
    vx, vy = g.xy(tb["pins"]["VMOT"])
    gx, gy = g.xy(tb["pins"]["GND2"])
    mx = (vx + gx) / 2
    dia, ln = CAP_C1
    can_z = top + 1.8 + dia / 2                # resting on the pin tips and bridge wires
    s.append(f'color("#202a6a") translate([{f(mx)},{f(vy + 3.0)},{f(can_z)}]) rotate([-90,0,0]) cylinder(h={f(ln)}, d={f(dia)}, $fn=40);')
    s.append(f'color("#d0d0d0") translate([{f(mx)},{f(vy + 3.0)},{f(can_z)}]) rotate([-90,0,0]) '
             f'intersection() {{ cylinder(h={f(ln)}, d={f(dia + 0.1)}, $fn=40); translate([{f(dia / 2 - 1.6)},-5,0]) cube([3,10,{f(ln)}]); }}')  # (-) stripe, GND side
    s += poly([(vx, vy, top), (vx, vy, can_z), (vx, vy + 3.0, can_z)], 0.6, C_SOLDER)
    s += poly([(gx, gy, top), (gx, gy, can_z), (gx, gy + 3.0, can_z)], 0.6, C_SOLDER)
    s.append(f'color("#e0b040") translate([{f(mx)},{f(vy - 3.2)},{f(top + 3.0)}]) rotate([90,0,0]) cylinder(h=2.0, d=4.5, $fn=24);')
    s += poly([(vx, vy, top), (vx, vy - 2.2, top + 2.0)], 0.5, C_SOLDER)
    s += poly([(gx, gy, top), (gx, gy - 2.2, top + 2.0)], 0.5, C_SOLDER)

    # ---- pin headers (step 4)
    for pid, p in parts.items():
        if not pid.startswith("J"):
            continue
        for pn, h in p["pins"].items():
            x, y = g.xy(h)
            used.add(h)
            s.append(box(x - 1.27, y - 1.27, 0, x + 1.27, y + 1.27, 2.5, C_PLASTIC))
            if pn == "KEY":          # J5: the 2nd pin is pulled out as a polarity key
                continue
            s.append(box(x - 0.32, y - 0.32, -BOARD_T - 1.5, x + 0.32, y + 0.32, 8.5, C_PIN))
        if pid == "JP1":            # jumper cap over two pins
            (xa, ya), (xb, yb) = g.xy(p["pins"][JP1_CAP[0]]), g.xy(p["pins"][JP1_CAP[1]])
            s.append(box(min(xa, xb) - 1.25, min(ya, yb) - 1.25, 3.0, max(xa, xb) + 1.25, max(ya, yb) + 1.25, 9.0, "#1565c0"))

    # ---- divider (step 5)
    def resistor_flat(a, b, col):
        (xa, ya), (xb, yb) = g.xy(a), g.xy(b)
        mxr, myr = (xa + xb) / 2, (ya + yb) / 2
        L = ((xb - xa) ** 2 + (yb - ya) ** 2) ** 0.5
        ux, uy = (xb - xa) / L, (yb - ya) / L
        out = poly([(xa, ya, 0), (xa, ya, 1.4), (mxr - ux * 3.2, myr - uy * 3.2, 1.4)], 0.5, C_SOLDER)
        out += poly([(xb, yb, 0), (xb, yb, 1.4), (mxr + ux * 3.2, myr + uy * 3.2, 1.4)], 0.5, C_SOLDER)
        out.append(seg((mxr - ux * 3.1, myr - uy * 3.1, 1.4), (mxr + ux * 3.1, myr + uy * 3.1, 1.4), 2.4, col))
        return out

    def resistor_standing(body_hole, other, col):
        (xa, ya), (xb, yb) = g.xy(body_hole), g.xy(other)
        out = [cyl(xa, ya, 0.6, 6.3, 2.4, col, 20)]
        out += poly([(xb, yb, 0), (xb, yb, 8.2), (xa, ya, 8.2), (xa, ya, 6.9)], 0.5, C_SOLDER)
        return out

    s += resistor_flat(parts["R100k"]["pins"]["a"], parts["R100k"]["pins"]["b"], "#d9c08a")
    s += resistor_standing(parts["R10k"]["pins"]["a"], parts["R10k"]["pins"]["b"], "#7fb0d8")
    s += resistor_standing(parts["R2k"]["pins"]["b"], parts["R2k"]["pins"]["a"], "#7fb0d8")
    for pid in ("R100k", "R10k", "R2k"):
        used |= set(parts[pid]["pins"].values())

    # ---- top-side jumper wires (step 6)
    for w in data.get("wires", []):
        route = WIRE_ROUTES.get(w["id"])
        if not route or route[0] != w["from"] or route[-1] != w["to"]:
            errs.append(f"wire {w['id']} {w['from']}->{w['to']} does not match WIRE_ROUTES {route}")
            continue
        col = data["net_colors"].get(w.get("net"), "#999999")
        pts = [(*g.xy(route[0]), 0.0)] + [(*g.xy(h), 0.9) for h in route] + [(*g.xy(route[-1]), 0.0)]
        if w["id"] == "w1":     # hops over L3/8
            (xa, ya), (xb, yb) = g.xy(route[0]), g.xy(route[-1])
            pts = [(xa, ya, 0), (xa, ya, 2.4), (xb, yb, 2.4), (xb, yb, 0)]
        s += poly(pts, 1.5, col)
        used |= {route[0], route[-1]}

    # ---- Dupont leads to the Uno sockets (step 7): up, then off the board edge on
    # the side of the Uno header they plug into (digital = top edge, analog =
    # bottom edge), ending in the male Dupont housing. Header x positions are not
    # in the layout, so each lead leaves the board straight along its own column.
    for so in data.get("sockets", []):
        x, y = g.xy(so["hole"])
        used.add(so["hole"])
        analog = so["uno"].startswith("A")
        zl = 14.0 if analog else 7.0               # A0 crosses the divider and C1
        ye = (by0 - 1.0) if analog else (by1 + 1.0)
        sg = -1.0 if analog else 1.0
        s += poly([(x, y, 0), (x, y, zl), (x, ye, zl)], 1.5, "#8e44ad" if analog else "#e67e22")
        if so["uno"] in ("D4", "D7"):              # 200 + 200 ohm in the wire, heat-shrunk
            ym = (y + ye) / 2
            s.append(seg((x, ym - 5, zl), (x, ym + 5, zl), 3.0, "#111111"))
        s.append(box(x - 1.27, ye, zl - 1.27, x + 1.27, ye + sg * 14.0, zl + 1.27, C_PLASTIC))
        s.append(box(x - 0.32, ye + sg * 14.0, zl - 0.32, x + 0.32, ye + sg * 20.0, zl + 0.32, C_PIN))

    # ---- bottom: solder joints on every used hole + the solder bridges (step 3)
    for h in sorted(used):
        x, y = g.xy(h)
        s.append(f'color("{C_SOLDER}") translate([{f(x)},{f(y)},{f(-BOARD_T)}]) scale([1,1,0.6]) sphere(d=1.9, $fn=14);')
    for a, b in data.get("bridges", []):
        if a not in holes or b not in holes:
            errs.append(f"bridge {a}-{b} uses a hole not in the grid")
            continue
        (xa, ya), (xb, yb) = g.xy(a), g.xy(b)
        s.append(seg((xa, ya, -BOARD_T - 0.4), (xb, yb, -BOARD_T - 0.4), 1.4, C_SOLDER))

    return "\n".join(s) + "\n", errs, ((bx0 + bx1) / 2, (by0 + by1) / 2, 4.0)


def render(scad: Path, png: Path, centre: tuple[float, float, float], rot: tuple[float, float, float],
           dist: float, proj: str) -> None:
    cx, cy, cz = centre
    cmd = [str(find_openscad()), "-o", str(png), f"--imgsize={IMG[0]},{IMG[1]}",
           f"--camera={cx},{cy},{cz},{rot[0]},{rot[1]},{rot[2]},{dist}",
           f"--projection={proj}", "--colorscheme=Tomorrow", str(scad)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not png.exists():
        raise RuntimeError(f"openscad failed ({r.returncode}): {r.stderr[-800:]}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--layout", type=Path, default=ROOT / "docs" / "shield_layout.json")
    ap.add_argument("--outdir", type=Path, default=ROOT / "docs")
    ap.add_argument("--scad-only", action="store_true", help="build and check the model, render nothing")
    args = ap.parse_args(argv)
    scad_text, errs, centre = build_scad(load(args.layout))
    for e in errs:
        print(f"FAIL {e}")
    if errs:
        return 1
    print(f"PASS model: {scad_text.count(chr(10))} primitives, every wire/join/bridge placed")
    if args.scad_only:
        return 0
    with tempfile.TemporaryDirectory() as td:
        scad = Path(td) / "shield.scad"
        scad.write_text(scad_text, encoding="ascii")
        # top: perspective from the front-left; bottom: straight up from below,
        # orthographic, i.e. the board flipped top-over-bottom (USB end still left)
        for name, rot, dist, proj in (("top", (45, 0, 15), 185.0, "p"), ("bottom", (180, 0, 0), 150.0, "o")):
            png = args.outdir / f"shield_3d_{name}.png"
            render(scad, png, centre, rot, dist, proj)
            print(f"png: {png}  ({png.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
