#!/usr/bin/env python
"""Build the LEGO-style proto-shield build guide (docs/shield_build_guide.svg).

Stdlib only. Reads docs/shield_layout.json (steps, bridges, wires, sockets) and
nine step renders <pngdir>/step_0.png .. step_8.png (made by
scripts/shield_render3d.py --steps). One panel per step, two columns.

Usage: python scripts/shield_guide_svg.py [--pngdir DIR] [-o OUT]
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
LAYOUT = ROOT / "docs" / "shield_layout.json"
PAGE_W = 1400
MARGIN = 20
GUTTER = 20
PANEL_W = 670
PAD = 10
CW = 0.62   # glyph width estimate, as a fraction of font size
NSTEPS = 9


def read_png_size(p: Path) -> tuple[int, int]:
    raw = p.read_bytes()[16:24]
    return int.from_bytes(raw[:4], "big"), int.from_bytes(raw[4:], "big")


def wrap(text: str, width_px: float, fs: float, bullet: bool = False) -> list[str]:
    n = max(10, int(width_px / (CW * fs)))
    kw = dict(break_on_hyphens=False, break_long_words=False)
    if bullet:
        kw.update(initial_indent="- ", subsequent_indent="  ")
    return textwrap.wrap(text, n, **kw) or [""]


def parts_for(i: int, d: dict) -> list[str]:
    nb, nw, ns = len(d["bridges"]), len(d["wires"]), len(d["sockets"])
    table = {
        0: ["multimeter (continuity mode)"],
        1: ["1x TB6612 carrier (Pololu md08a)", "2x 8-pin male header",
            "5x short insulated wire (AO/BO pair: 22 AWG)",
            "1x 470 uF 25 V electrolytic (C1)", "1x 0.1 uF ceramic (C2)"],
        2: ["the carrier from step 1", "16 solder joints"],
        3: [f"{nb} bridges: bare-wire offcuts + solder"],
        4: ["1x 4-pin header (J1)", "1x 4-pin header, 2nd pin pulled (J5)",
            "1x 1-pin header (J6)", "4x 3-pin header (J3, J4, JP1, J2)"],
        5: ["1x 100k", "1x 10k", "1x 2k"],
        6: [f"{nw}x insulated 22 AWG wire (w1-w5)"],
        7: [f"{ns}x male Dupont jumper, cut",
            "4x 200 ohm (2 in series per strip wire)", "heat-shrink"],
        8: ["1x jumper cap (JP1)", "multimeter"],
    }
    return table[i]


class Out:
    """SVG body plus a record of every text line (text, font size, limit px)."""

    def __init__(self):
        self.parts: list[str] = []
        self.lines: list[tuple[str, float, float]] = []

    def text(self, x, y, s, fs, limit, fill=None, dx=0):
        self.lines.append((s, fs, limit))
        f = f' fill="{fill}"' if fill else ""
        self.parts.append(f'<text x="{x + dx:.1f}" y="{y:.1f}" font-size="{fs}"{f}>{escape(s)}</text>')

    def raw(self, s):
        self.parts.append(s)


def draw_panel(o: Out, x0: float, y0: float, h: float, i: int, step: dict, d: dict,
               png: Path, size: tuple[int, int], measure: bool = False) -> float:
    """Lay out one panel at (x0, y0). Returns its content height."""
    inner = PANEL_W - 2 * PAD
    y = PAD
    body: list[str] = []
    rec: list[tuple[str, float, float]] = []

    def T(x, yy, s, fs, limit, fill=None, dx=0):
        rec.append((s, fs, limit))
        f = f' fill="{fill}"' if fill else ""
        body.append(f'<text x="{x0 + x + dx:.1f}" y="{y0 + yy:.1f}" font-size="{fs}"{f}>{escape(s)}</text>')

    # 1. number circle + title
    title = step["title"]
    k = title.find(". ")
    if k > 0 and title[:k].isdigit():
        title = title[k + 2:]
    tx = PAD + 52 + 12
    tw = PANEL_W - tx - PAD
    tl = wrap(title, tw, 14)
    head_h = max(52, len(tl) * 17 + 4)
    cy = y + 26
    body.append(f'<circle cx="{x0 + PAD + 26}" cy="{y0 + cy}" r="26" fill="#1f4e79"/>')
    body.append(f'<text x="{x0 + PAD + 26}" y="{y0 + cy + 10.5}" font-size="30" fill="#fff" '
                f'text-anchor="middle">{i}</text>')
    ty = y + (head_h - len(tl) * 17) / 2 + 13
    for ln in tl:
        T(tx, ty, ln, 14, tw)
        ty += 17
    y += head_h + 10

    # 2. parts box
    items = parts_for(i, d)
    pbh = 8 + 14 + 14 * len(items) + 4
    body.append(f'<rect x="{x0 + PAD}" y="{y0 + y}" width="{inner}" height="{pbh}" rx="6" '
                f'fill="#fffbe6" stroke="#e0c060"/>')
    T(PAD + 8, y + 8 + 11, "Parts", 11, inner - 16)
    py = y + 8 + 14 + 11
    for it in items:
        T(PAD + 8, py, it, 11, inner - 16)
        py += 14
    y += pbh + 10

    # 3. image
    ih = inner * size[1] / size[0]
    b64 = base64.b64encode(png.read_bytes()).decode("ascii")
    body.append(f'<image x="{x0 + PAD}" y="{y0 + y:.1f}" width="{inner}" height="{ih:.1f}" '
                f'href="data:image/png;base64,{b64}"/>')
    y += ih + 10

    # 4. do bullets
    for line in step["do"]:
        wl = wrap(line, inner, 12, bullet=True)
        for j, ln in enumerate(wl):
            if j == 0:
                T(PAD, y + 12, ln, 12, inner)
            else:
                T(PAD, y + 12, ln.lstrip(), 12, inner - 9, dx=9)
            y += 16
        y += 2
    y += 6

    # 5. check box
    cl = wrap("CHECK: " + step["check"], inner - 16, 12)
    cbh = 16 + 16 * len(cl)
    body.append(f'<rect x="{x0 + PAD}" y="{y0 + y}" width="{inner}" height="{cbh}" rx="6" '
                f'fill="#e8f4ea" stroke="#6aa86f"/>')
    cyy = y + 8 + 12
    for ln in cl:
        T(PAD + 8, cyy, ln, 12, inner - 16)
        cyy += 16
    y += cbh + PAD

    if not measure:
        o.raw(f'<rect x="{x0}" y="{y0}" width="{PANEL_W}" height="{h:.1f}" rx="10" '
              f'fill="#f4f6f8" stroke="#c9d1d9"/>')
        o.parts.extend(body)
        o.lines.extend(rec)
    return y


def build(pngdir: Path) -> tuple[str, list[tuple[str, float, float]]]:
    data = json.loads(LAYOUT.read_text(encoding="utf-8"))
    steps = data["steps"]
    assert len(steps) == NSTEPS, f"expected {NSTEPS} steps, got {len(steps)}"
    pngs = []
    for i in range(NSTEPS):
        p = pngdir / f"step_{i}.png"
        if not p.exists():
            raise FileNotFoundError(f"missing {p} - run scripts/shield_render3d.py --steps")
        pngs.append((p, read_png_size(p)))

    o = Out()
    # header
    o.text(MARGIN, 20 + 24, "Proto shield v.5 - build guide", 24, PAGE_W - 2 * MARGIN)
    intro = ("One panel per step. New parts in each picture are in colour; parts from earlier "
             "steps are grey. Hole = ROW/COL, as on docs/shield_holemap.svg. Pictures are "
             "renders of the INTENDED build, not photos. Rails: BLACK band = GND (G, and B = the "
             "ground star), RED band = 5V (V and T = the Uno's 5V, from the Pi's USB); the bands "
             "are drawn on to show the rails - the real board's rail copper is on the underside.")
    y = 20 + 24 + 22
    for ln in wrap(intro, PAGE_W - 2 * MARGIN, 12):
        o.text(MARGIN, y, ln, 12, PAGE_W - 2 * MARGIN)
        y += 16
    y += 2
    o.text(MARGIN, y, "If a CHECK fails, STOP - do not solder past it.", 13, PAGE_W - 2 * MARGIN,
           fill="#b00020")
    y += 18

    # panels
    dummy = Out()
    for r in range(0, NSTEPS, 2):
        idx = [i for i in (r, r + 1) if i < NSTEPS]
        hs = []
        for c, i in enumerate(idx):
            hs.append(draw_panel(dummy, 0, 0, 0, i, steps[i], data, pngs[i][0], pngs[i][1],
                                 measure=True))
        h = max(hs)
        for c, i in enumerate(idx):
            x0 = MARGIN + c * (PANEL_W + GUTTER)
            draw_panel(o, x0, y, h, i, steps[i], data, pngs[i][0], pngs[i][1])
        y += h + GUTTER

    o.text(MARGIN, y + 6, "Generated by scripts/shield_guide_svg.py from docs/shield_layout.json; "
           "renders by scripts/shield_render3d.py --steps.", 11, PAGE_W - 2 * MARGIN)
    H = y + 6 + 16
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}" height="{H:.0f}" '
           f'viewBox="0 0 {PAGE_W} {H:.0f}" font-family="Arial, sans-serif" font-weight="bold">\n'
           f'<rect width="{PAGE_W}" height="{H:.0f}" fill="#fff"/>\n'
           + "\n".join(o.parts) + "\n</svg>\n")
    return svg, o.lines


def self_check():
    svg, lines = build(ROOT / "docs" / "guide")   # FileNotFoundError -> SKIP in run_checks
    data = json.loads(LAYOUT.read_text(encoding="utf-8"))
    assert svg.count("<circle ") == NSTEPS, f"{svg.count('<circle ')} circles, want {NSTEPS}"
    joined = " ".join(escape(s) for s, _, _ in lines)
    for st in data["steps"]:
        t = st["title"]
        k = t.find(". ")
        if k > 0 and t[:k].isdigit():
            t = t[k + 2:]
        assert escape(t) in joined, f"title missing: {t}"
        assert escape("CHECK: " + st["check"]) in joined, f"check missing: {st['check'][:30]}"
    for s, fs, limit in lines:
        assert len(s) * CW * fs <= limit + 0.5, f"line too wide ({limit}px): {s[:40]}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pngdir", default=str(ROOT / "docs" / "guide"))
    ap.add_argument("-o", default=str(ROOT / "docs" / "shield_build_guide.svg"))
    a = ap.parse_args(argv)
    try:
        svg, _ = build(Path(a.pngdir))
    except FileNotFoundError as e:
        print(f"FAIL {e}")
        return 1
    Path(a.o).write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {a.o} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
