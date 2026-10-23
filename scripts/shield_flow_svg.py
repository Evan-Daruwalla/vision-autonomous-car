#!/usr/bin/env python
"""Build the animated 'how it works' page (docs/shield_how_it_works.svg).

Same visual system as scripts/shield_guide_svg.py (reuses its helpers). Six
panels, one per current path; each shows the top-side and underside renders
(<pngdir>/flow_{k}_top.png, flow_{k}_bottom.png, k = 1..6, made by
scripts/shield_render3d.py --flow) plus an explanation. The panels light up one
after another (CSS, 30 s loop).

Every phase names the nets it shows; the script FAILS if docs/shield_layout.json
lacks those nets or their key members, so the page cannot describe a wire the
layout does not have.

Usage: python scripts/shield_flow_svg.py [--pngdir DIR] [--layout FILE] [-o OUT]
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shield_guide_svg import (CW, GUTTER, LAYOUT, MARGIN, PAD, PAGE_W, PANEL_W, ROOT,  # noqa: E402
                              Out, read_png_size, wrap)

PHASE_S, N_PHASE = 5, 6
TOTAL_S = PHASE_S * N_PHASE
IMG_W = (PANEL_W - 30) / 2

# (title, nets, involved lines, text)
PHASES = [
    ("Battery power (VBAT)", ["VBAT"],
     ["2S pack via J5's VBAT pin", "w1 (VMOT to the VBAT strip)", "C1 470 uF + C2 0.1 uF",
      "TB6612 VM pin", "R100k (top of the divider)"],
     "The 2S pack (7.2-8.4 V) arrives through the fuse, BMS and rocker at J5's VBAT pin and the "
     "VBAT strip; w1 carries it to the TB6612's motor-power pin VM, where C1 and C2 hold it steady. "
     "The divider's top resistor (R100k) also taps it, so the Uno can measure the pack."),
    ("+5V2 (from the LM2596)", ["5V2"],
     ["J5's +5V2 pin", "bridge bus along row P4", "J1 +5V2 (encoder)", "J3 / J4 +5V2 (LED strips)",
      "w4 -> JP1's bottom pin"],
     "The LM2596 on the deck makes about 5 V from VBAT and brings it in on J5's +5V2 pin. A bridge "
     "bus along row P4 spreads it to the encoder (J1), both LED strips (J3, J4) and, through w4, "
     "JP1's bottom pin - used only if the servo jumper is moved down."),
    ("Logic 5V (the Uno, from the Pi's USB)", ["UNO5V", "SERVO_V"],
     ["rail V (the Uno's 5V)", "w3 -> TB6612 VCC", "JP1 top two pins + the jumper cap",
      "J2 servo V+"],
     "The Pi's USB powers the Uno; the Uno's 5V pin is rail V. w3 takes it to the TB6612's logic "
     "supply (VCC), and JP1's cap on the top two pins passes it to the servo's V+ on J2."),
    ("Signals (the Uno's pins)",
     ["PWM", "DIR1", "DIR2", "STBY", "SERVO_SIG", "DIN_L", "DIN_R", "A0", "DIV_MID"],
     ["D11 PWM, D8 + D12 direction, D10 enable -> TB6612", "D9 -> servo signal (J2)",
      "D4 / D7 -> LED data (J3, J4), 400 ohm in each wire",
      "A0 <- divider (R100k over R10k + R2k)", "D2 / D3 <- encoder (straight to the Uno)"],
     "The Uno runs the firmware: it reads the Pi's commands and drives the pins. Dupont leads carry "
     "its signals: speed, direction and enable to the TB6612, the servo angle, the LED data. It "
     "reads the pack voltage on A0 (VBAT / 9.33 from the divider) and the encoder on D2 / D3, "
     "which plug straight into the Uno."),
    ("Motor current", ["M1", "M2"],
     ["TB6612 AO1+BO1 and AO2+BO2 (paralleled on the carrier)", "bridges L3/3-P3/3 and L3/4-P3/4",
      "J1 M1 / M2 -> N20 motor"],
     "The TB6612 switches VBAT into the motor. Its A and B channels are paralleled on the carrier "
     "for more current, and two bridges take M1 / M2 to J1 and on to the N20 motor. Speed comes "
     "from PWM, direction from the DIR pins."),
    ("Ground return (the star)", ["GND"],
     ["rail B = the star", "rail G (joined to B)", "w2 (TB6612 GND -> B)", "w5 (servo GND -> B)",
      "GND pins of J1-J6", "R2k (bottom of the divider)"],
     "Every current comes back to ground, and all grounds meet at one point: rail B, the star. The "
     "TB6612 returns through w2, the servo through w5, the headers' GND pins through their "
     "bridges; the LM2596's ground arrives on J6 (wire W13)."),
]

# members that must be present in each net of the layout
REQUIRED = {
    "VBAT": ["TB.VMOT", "C1.+", "J5.VBAT", "R100k.a"],
    "5V2": ["J1.5V2", "J3.5V2", "J4.5V2", "JP1.5V2", "J5.5V2"],
    "UNO5V": ["TB.VCC", "JP1.UNO5V"],
    "SERVO_V": ["J2.V"],
    "PWM": ["uno:D11"],
    "SERVO_SIG": ["uno:D9"],
    "DIN_L": ["uno:D4"],
    "DIN_R": ["uno:D7"],
    "A0": ["uno:A0", "R100k.b"],
    "M1": ["TB.AO1", "J1.M1"],
    "M2": ["TB.AO2", "J1.M2"],
    "GND": ["TB.GND1", "J1.GND", "J2.GND", "J5.GND", "J6.GND", "R2k.b"],
}


def check_against_layout(data: dict) -> list[str]:
    nets = data["nets"]
    errs = []
    for k, (_t, plist, _i, _x) in enumerate(PHASES, 1):
        for net in plist:
            if net not in nets:
                errs.append(f"phase {k}: net {net} not in the layout")
    for net, members in REQUIRED.items():
        if net not in nets:
            continue   # already reported above
        for m in members:
            if m not in nets[net]:
                errs.append(f"net {net}: {m} is not a member in the layout")
    if {d.get("uno") for d in data.get("direct_uno", [])} != {"D2", "D3"}:
        errs.append("encoder: layout direct_uno is not D2 + D3")
    return errs


def css_block() -> str:
    css = []
    for k in range(1, N_PHASE + 1):
        a, b = (k - 1) / N_PHASE * 100, k / N_PHASE * 100
        hl = ([(0, 0)] if a == 0 else [(0, 0), (a, 0)]) + [(a + 0.8, 1), (b - 0.8, 1), (b, 0)]
        bd = ([(0, "#1f4e79")] if a == 0 else [(0, "#1f4e79"), (a, "#1f4e79")]) + \
            [(a + 0.8, "#f2b600"), (b - 0.8, "#f2b600"), (b, "#1f4e79")]
        if b < 100:
            hl.append((100, 0))
            bd.append((100, "#1f4e79"))
        css.append(f"@keyframes hl{k}k{{" + "".join(f"{p:.2f}%{{opacity:{v}}}" for p, v in hl) + "}")
        css.append(f"@keyframes bd{k}k{{" + "".join(f"{p:.2f}%{{fill:{v}}}" for p, v in bd) + "}")
        css.append(f".hl{k}{{opacity:0;animation:hl{k}k {TOTAL_S}s linear infinite}}")
        css.append(f".bd{k}{{animation:bd{k}k {TOTAL_S}s linear infinite}}")
    sel = ",".join(f".hl{k},.bd{k}" for k in range(1, N_PHASE + 1))
    hid = ",".join(f".hl{k}" for k in range(1, N_PHASE + 1))
    css.append(f"@media (prefers-reduced-motion: reduce){{{sel}{{animation:none}}{hid}{{opacity:0}}}}")
    return "".join(css)


def draw_panel(o: Out, x0: float, y0: float, h: float, k: int, imgs, measure: bool = False) -> float:
    title, _nets, involved, text = PHASES[k - 1]
    inner = PANEL_W - 2 * PAD
    y = PAD
    body: list[str] = []
    rec: list[tuple[str, float, float]] = []

    def T(x, yy, s, fs, limit, fill=None, dx=0):
        rec.append((s, fs, limit))
        f = f' fill="{fill}"' if fill else ""
        body.append(f'<text x="{x0 + x + dx:.1f}" y="{y0 + yy:.1f}" font-size="{fs}"{f}>{escape(s)}</text>')

    # 1. badge + title
    tx = PAD + 52 + 12
    tw = PANEL_W - tx - PAD
    tl = wrap(title, tw, 14)
    head_h = max(52, len(tl) * 17 + 4)
    cy = y + 26
    body.append(f'<circle class="bd{k}" cx="{x0 + PAD + 26}" cy="{y0 + cy}" r="26" fill="#1f4e79"/>')
    body.append(f'<text x="{x0 + PAD + 26}" y="{y0 + cy + 10.5}" font-size="30" fill="#fff" '
                f'text-anchor="middle">{k}</text>')
    ty = y + (head_h - len(tl) * 17) / 2 + 13
    for ln in tl:
        T(tx, ty, ln, 14, tw)
        ty += 17
    y += head_h + 10

    # 2. involved box
    lines = []
    for it in involved:
        lines.extend(wrap(it, inner - 16, 11))
    pbh = 8 + 14 + 14 * len(lines) + 4
    body.append(f'<rect x="{x0 + PAD}" y="{y0 + y}" width="{inner}" height="{pbh}" rx="6" '
                f'fill="#fffbe6" stroke="#e0c060"/>')
    T(PAD + 8, y + 8 + 11, "Involved", 11, inner - 16)
    py = y + 8 + 14 + 11
    for ln in lines:
        T(PAD + 8, py, ln, 11, inner - 16)
        py += 14
    y += pbh + 10

    # 3. images two per row (3/4 view, straight down; then the underside, centred)
    for r in range(0, len(imgs), 2):
        row = imgs[r:r + 2]
        x_first = PAD if len(row) == 2 else PAD + (IMG_W + 10) / 2
        row_h = 0.0
        for j, (png, size) in enumerate(row):
            ih = IMG_W * size[1] / size[0]
            b64 = base64.b64encode(png.read_bytes()).decode("ascii")
            ix = x_first + j * (IMG_W + 10)
            body.append(f'<image x="{x0 + ix:.1f}" y="{y0 + y:.1f}" width="{IMG_W:.1f}" height="{ih:.1f}" '
                        f'href="data:image/png;base64,{b64}"/>')
            row_h = max(row_h, ih)
        y += row_h + 10

    # 4. explanation
    for ln in wrap(text, inner, 12):
        T(PAD, y + 12, ln, 12, inner)
        y += 16
    y += PAD

    if not measure:
        o.raw(f'<g class="pnl{k}">')
        o.raw(f'<rect x="{x0}" y="{y0}" width="{PANEL_W}" height="{h:.1f}" rx="10" '
              f'fill="#f4f6f8" stroke="#c9d1d9"/>')
        o.raw(f'<rect class="hl{k}" x="{x0}" y="{y0}" width="{PANEL_W}" height="{h:.1f}" rx="10" '
              f'fill="none" stroke="#f2b600" stroke-width="5"/>')
        o.parts.extend(body)
        o.raw('</g>')
        o.lines.extend(rec)
    return y


def build(pngdir: Path) -> tuple[str, list[tuple[str, float, float]]]:
    pngs = []
    for k in range(1, N_PHASE + 1):
        pair = []
        for side in ("top", "plan", "bottom"):
            p = pngdir / f"flow_{k}_{side}.png"
            if not p.exists():
                raise FileNotFoundError(f"missing {p} - run scripts/shield_render3d.py --flow")
            pair.append((p, read_png_size(p)))
        pngs.append(pair)

    o = Out()
    o.text(MARGIN, 20 + 24, "Proto shield - what each part does, and how the current flows", 24,
           PAGE_W - 2 * MARGIN)
    intro = ("Six panels, one per path the current takes. In each picture only that path's parts "
             "and wires are in colour; everything else is grey. Top row: a 3/4 view and the view "
             "straight down; below: the underside (flipped top-over-bottom, USB end still left). The panels light up one "
             "after another (30 s loop). Pictures are renders of the INTENDED build, not photos.")
    y = 20 + 24 + 22
    for ln in wrap(intro, PAGE_W - 2 * MARGIN, 12):
        o.text(MARGIN, y, ln, 12, PAGE_W - 2 * MARGIN)
        y += 16
    y += 6

    dummy = Out()
    for r in range(1, N_PHASE + 1, 2):
        idx = [k for k in (r, r + 1) if k <= N_PHASE]
        h = max(draw_panel(dummy, 0, 0, 0, k, pngs[k - 1], measure=True) for k in idx)
        for c, k in enumerate(idx):
            draw_panel(o, MARGIN + c * (PANEL_W + GUTTER), y, h, k, pngs[k - 1])
        y += h + GUTTER

    o.text(MARGIN, y + 6, "Generated by scripts/shield_flow_svg.py from docs/shield_layout.json; "
           "renders by scripts/shield_render3d.py --flow.", 11, PAGE_W - 2 * MARGIN)
    H = y + 6 + 16
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}" height="{H:.0f}" '
           f'viewBox="0 0 {PAGE_W} {H:.0f}" font-family="Arial, sans-serif" font-weight="bold">\n'
           f'<style>{css_block()}</style>\n'
           f'<rect width="{PAGE_W}" height="{H:.0f}" fill="#fff"/>\n'
           + "\n".join(o.parts) + "\n</svg>\n")
    return svg, o.lines


def self_check() -> None:
    data = json.loads(LAYOUT.read_text(encoding="utf-8"))
    assert check_against_layout(data) == [], check_against_layout(data)
    bad = json.loads(json.dumps(data))
    bad["nets"]["VBAT"].remove("TB.VMOT")             # planted: VM no longer on VBAT
    assert any("TB.VMOT" in e for e in check_against_layout(bad)), "planted net error not caught"
    svg, lines = build(ROOT / "docs" / "guide")       # FileNotFoundError -> SKIP in run_checks
    assert svg.count("<circle ") == N_PHASE, f"{svg.count('<circle ')} circles, want {N_PHASE}"
    assert svg.count('class="pnl') == N_PHASE, "panel count"
    for k in range(1, N_PHASE + 1):
        assert f'class="hl{k}"' in svg, f"hl{k} missing"
    joined = " ".join(escape(s) for s, _, _ in lines)
    for t, *_ in PHASES:
        assert escape(t) in joined, f"title missing: {t}"
    for s, fs, limit in lines:
        assert len(s) * CW * fs <= limit + 0.5, f"line too wide ({limit}px): {s[:40]}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pngdir", default=str(ROOT / "docs" / "guide"))
    ap.add_argument("--layout", type=Path, default=LAYOUT)
    ap.add_argument("-o", default=str(ROOT / "docs" / "shield_how_it_works.svg"))
    a = ap.parse_args(argv)
    data = json.loads(a.layout.read_text(encoding="utf-8"))
    errs = check_against_layout(data)
    for e in errs:
        print(f"FAIL {e}")
    if errs:
        return 1
    try:
        svg, _ = build(Path(a.pngdir))
    except FileNotFoundError as e:
        print(f"FAIL {e}")
        return 1
    Path(a.o).write_text(svg, encoding="utf-8", newline="\n")
    print(f"PASS layout check ok; wrote {a.o} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
