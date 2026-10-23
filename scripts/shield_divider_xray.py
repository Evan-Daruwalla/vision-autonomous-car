"""X-ray close-up of the pack-voltage divider on the proto shield: the board is
drawn see-through so the resistor leads, the copper strips under the board, the
solder joints and the bridge that join them are all visible at once.

Writes docs/guide/divider_xray.png (3/4 view through the board), divider_xray_plan.png
(straight down through it) and docs/shield_divider_xray.svg (both + a numbered legend).
Holes and parts come from docs/shield_layout.json (R100k, R10k, R2k, the A0
socket, J5's VBAT pin, w1's end, the L2/9-L2/10 bridge); the script fails if
any of them moved. Geometry helpers are shared with scripts/shield_render3d.py.

Usage: python scripts/shield_divider_xray.py
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shield_render3d import (BOARD_T, C_COPPER, C_SOLDER, C_PIN, C_PLASTIC, P, Geo,  # noqa: E402
                             _crop_to_content, box, cyl, f, poly, render, seg)

ROOT = Path(__file__).resolve().parent.parent
# what this picture claims, checked against the layout file
EXPECT = {"R100k": {"a": "L1/9", "b": "U3/9"}, "R10k": {"a": "U2/9", "b": "U2/10"},
          "R2k": {"a": "U3/10", "b": "G/10"}}
C_VBAT = "#C62828"


# (hole, dx, dy, z) for badges 1..9 - the order of LEGEND below
BADGES = [("L3/9", -3.5, 0, 3.0), ("L3/10", 2.2, -1.5, 9.5), ("L2/10", 2.5, 0, 0.5),
          ("V/9", -3.0, 0, 3.5), ("U1/9", 2.4, 2.2, 4.5), ("U2/9", -3.0, 0, 9.0),
          ("U2/10", 2.8, -0.6, 10.5), ("G/10", 2.8, 0, 8.0), ("G/11", 2.5, 0, 0.6)]
# the straight-down view has its own spots, off the parts (dx, dy in mm from the hole)
BADGES_PLAN = [("L3/8", 0, 1.3), ("L3/11", 0, 0), ("L2/11", 0, 0), ("V/8", 0, 0), ("U1/8", 0, 0),
               ("U2/8", 0, 0), ("U2/11", 0, 0), ("U3/11", 0, 0), ("G/11", 1.3, 0)]
LEGEND = [
    "VBAT comes in on w1, at L3/9 (lower strip 9).",
    "J5's VBAT pin at L3/10 (lower strip 10).",
    "Bridge L2/9-L2/10 on the underside joins lower strips 9 and 10 - one VBAT island.",
    "R100k lies flat from L1/9 (VBAT) to U3/9, over the G and V rails without touching them.",
    "Upper strip 9 = the A0 node: U1/9 (Dupont lead to the Uno's A0), U2/9 (R10k), U3/9 (R100k).",
    "R10k stands on U2/9 and loops over to U2/10.",
    "Upper strip 10 = the middle of the 12k bottom half: U2/10 (R10k) and U3/10 (R2k).",
    "R2k stands on G/10 and loops over to U3/10.",
    "Rail G = GND (joined to rail B, the star): the bottom of the divider.",
]


def badge(x, y, z, n, plan=False, d=2.6, size=1.5):
    # a white disc with the number, both turned to face the (55, 0, 25) camera
    turn = "" if plan else "rotate([0,0,25]) rotate([55,0,0])"   # flat for the straight-down view
    return (f'translate([{f(x)},{f(y)},{f(z)}]) {turn} {{ color("#ffffff") cylinder(h=0.1, d={d}, $fn=24); '
            f'color("#1f4e79") translate([0,0,0.12]) linear_extrude(0.1) text("{n}", size={size}, '
            f'font="Liberation Sans:style=Bold", halign="center", valign="center"); }}')


def build(data: dict, plan: bool = False) -> str:
    parts = {p["id"]: p for p in data["parts"]}
    for pid, pins in EXPECT.items():
        if parts.get(pid, {}).get("pins") != pins:
            raise SystemExit(f"FAIL {pid} pins in the layout are {parts.get(pid, {}).get('pins')}, expected {pins}")
    if not any(s["hole"] == "U1/9" and s["uno"] == "A0" for s in data["sockets"]):
        raise SystemExit("FAIL the A0 socket is no longer at U1/9")
    if ["L2/9", "L2/10"] not in data["bridges"]:
        raise SystemExit("FAIL the L2/9-L2/10 bridge is gone")
    g = Geo(data)
    xy = g.xy
    s: list[str] = []
    cols = (8, 9, 10, 11)
    rows = ["U1", "U2", "U3", "G", "V", "L1", "L2", "L3"]
    holes = [f"{r}/{c}" for r in rows for c in cols]
    # copper under the board: strips 9 and 10 (upper and lower), and the G and V rails
    for grp in data["grid"]["copper"]:
        hs = [h for h in grp["holes"] if h in holes]
        if len(hs) < 2:
            continue
        xs = [xy(h)[0] for h in hs]
        ys = [xy(h)[1] for h in hs]
        s.append(box(min(xs) - 0.9, min(ys) - 0.9, -BOARD_T - 0.06, max(xs) + 0.9, max(ys) + 0.9, -BOARD_T, C_COPPER))
    for h in holes:
        x, y = xy(h)
        s.append(cyl(x, y, -BOARD_T - 0.12, 0.06, 1.0, "#0a0a0a", 12))
        s.append(cyl(x, y, 0.0, 0.05, 1.0, "#0a0a0a", 12))

    def through(h, col):              # a lead through the board, its joint underneath
        x, y = xy(h)
        return [seg((x, y, 0.4), (x, y, -BOARD_T - 0.6), 0.55, col),
                f'color("{C_SOLDER}") translate([{f(x)},{f(y)},{f(-BOARD_T - 0.2)}]) scale([1,1,0.6]) sphere(d=1.9, $fn=16);']

    # R100k lying flat L1/9 -> U3/9 (VBAT -> A0)
    (xa, ya), (xb, yb) = xy("L1/9"), xy("U3/9")
    s += poly([(xa, ya, 0.4), (xa, ya, 1.4), (xa, ya + 1.2, 1.4)], 0.55, C_SOLDER)
    s += poly([(xb, yb, 0.4), (xb, yb, 1.4), (xb, yb - 1.2, 1.4)], 0.55, C_SOLDER)
    s.append(seg((xa, ya + 1.2, 1.4), (xb, yb - 1.2, 1.4), 2.4, "#d9c08a"))
    s += through("L1/9", C_SOLDER) + through("U3/9", C_SOLDER)
    # R10k standing on U2/9, lead looping to U2/10 (A0 -> DIV_MID)
    for body, other, col in (("U2/9", "U2/10", "#7fb0d8"), ("G/10", "U3/10", "#7fb0d8")):
        (xa, ya), (xb, yb) = xy(body), xy(other)
        s.append(cyl(xa, ya, 0.6, 6.3, 2.4, col, 24))
        s += poly([(xb, yb, 0.4), (xb, yb, 8.2), (xa, ya, 8.2), (xa, ya, 6.9)], 0.5, C_SOLDER)
        s += through(body, C_SOLDER) + through(other, C_SOLDER)
    # A0 Dupont lead going up from U1/9
    x, y = xy("U1/9")
    s += poly([(x, y, 0.4), (x, y, 9.0)], 1.4, "#8e44ad")
    s += through("U1/9", "#8e44ad")
    # J5's VBAT pin at L3/10, w1's end at L3/9
    x, y = xy("L3/10")
    s.append(box(x - 1.27, y - 1.27, 0, x + 1.27, y + 1.27, 2.5, C_PLASTIC))
    s.append(box(x - 0.32, y - 0.32, -BOARD_T - 1.0, x + 0.32, y + 0.32, 8.5, C_PIN))
    s.append(f'color("{C_SOLDER}") translate([{f(x)},{f(y)},{f(-BOARD_T - 0.2)}]) scale([1,1,0.6]) sphere(d=1.9, $fn=16);')
    x, y = xy("L3/9")
    s += poly([(x - 2 * P, y, 0.9), (x, y, 0.9), (x, y, 0.0)], 1.4, C_VBAT)
    s += through("L3/9", C_VBAT)
    # the L2/9 - L2/10 bridge (underside)
    (xa, ya), (xb, yb) = xy("L2/9"), xy("L2/10")
    s.append(seg((xa, ya, -BOARD_T - 0.4), (xb, yb, -BOARD_T - 0.4), 1.4, C_SOLDER))
    # numbered badges (the legend in the SVG says what each number is)
    spots = [(h, dx, dy, 12.0) for h, dx, dy in BADGES_PLAN] if plan else BADGES
    for n, (h, dx, dy, dz) in enumerate(spots, 1):
        x, y = xy(h)
        s.append(badge(x + dx, y + dy, dz, n, plan, *((2.0, 1.2) if plan else (2.6, 1.5))))
    # the board LAST and see-through, so everything under it shows
    x0, x1 = min(cols) * P - 2.0, max(cols) * P + 2.0
    y0, y1 = xy("L3/8")[1] - 2.0, xy("U1/8")[1] + 2.0
    s.append(f'color("#2f6b3a", 0.30) translate([{f(x0)},{f(y0)},{f(-BOARD_T)}]) cube([{f(x1 - x0)},{f(y1 - y0)},{f(BOARD_T)}]);')
    return "\n".join(s) + "\n", ((x0 + x1) / 2, (y0 + y1) / 2, 2.0)


def page(imgs) -> str:
    """The two renders side by side with the numbered legend and the circuit, as an SVG."""
    import base64
    from xml.sax.saxutils import escape
    W, M = 1400, 20
    iw = (W - 3 * M) / 2
    o, y = [], 44
    o.append(f'<text x="{M}" y="{y}" font-size="24">Proto shield - how the pack-voltage divider connects (board see-through)</text>')
    y += 22
    o.append(f'<text x="{M}" y="{y}" font-size="12" fill="#444">Left: 3/4 view; right: straight down. The board is drawn '
             f'see-through, so the copper strips and solder underneath show. Render of the INTENDED build, not a photo.</text>')
    y += 16
    hmax = 0
    for j, (png, (pw, ph)) in enumerate(imgs):
        h = iw * ph / pw
        b64 = base64.b64encode(png.read_bytes()).decode("ascii")
        o.append(f'<image x="{M + j * (iw + M):.1f}" y="{y}" width="{iw:.1f}" height="{h:.1f}" href="data:image/png;base64,{b64}"/>')
        hmax = max(hmax, h)
    y += hmax + 24
    for n, line in enumerate(LEGEND, 1):
        o.append(f'<circle cx="{M + 11}" cy="{y - 4}" r="10" fill="#1f4e79"/>')
        o.append(f'<text x="{M + 11}" y="{y + 1}" font-size="13" fill="#fff" text-anchor="middle">{n}</text>')
        o.append(f'<text x="{M + 30}" y="{y}" font-size="13" fill="#222">{escape(line)}</text>')
        y += 24
    y += 6
    for line in ("The circuit: VBAT -> R100k -> A0 node -> R10k -> R2k -> GND. A0 = VBAT x 12k / 112k = VBAT / 9.33,",
                 "so a full 8.4 V pack reads 0.90 V on A0 and the 7.2 V low end reads 0.77 V - well inside the Uno's 0-5 V."):
        o.append(f'<text x="{M}" y="{y}" font-size="13" fill="#1a56b0">{escape(line)}</text>')
        y += 18
    H = y + 14
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" '
            f'font-family="Arial, sans-serif" font-weight="bold">\n<rect width="{W}" height="{H:.0f}" fill="#fff"/>\n'
            + "\n".join(o) + "\n</svg>\n")


def main(argv=None) -> int:
    from shield_guide_svg import read_png_size
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)
    data = json.loads((ROOT / "docs" / "shield_layout.json").read_text(encoding="utf-8"))
    gdir = ROOT / "docs" / "guide"
    outs = [(gdir / "divider_xray.png", (55, 0, 25), 75.0, "p"), (gdir / "divider_xray_plan.png", (0, 0, 0), 60.0, "o")]
    with tempfile.TemporaryDirectory() as td:
        for png, rot, dist, proj in outs:
            scad_text, centre = build(data, plan=rot == (0, 0, 0))
            scad = Path(td) / "divider.scad"
            scad.write_text(scad_text, encoding="ascii")
            render(scad, png, centre, rot, dist, proj)
            _crop_to_content(png)
    svg_out = ROOT / "docs" / "shield_divider_xray.svg"
    svg_out.write_text(page([(p, read_png_size(p)) for p, *_ in outs]), encoding="ascii", newline="\n")
    print(f"PASS divider holes match the layout; wrote {', '.join(str(p) for p, *_ in outs)}, {svg_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
