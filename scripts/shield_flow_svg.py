"""Animated 'how it works' diagram of the proto shield: what every part does and
how current flows, as docs/shield_how_it_works.svg.

Block diagram (not hole-level). Current is drawn as dashes moving along each
wire, coloured by net; six phases light up in turn (30 s loop, CSS animation,
so it plays in a browser and on GitHub): 1 battery power (VBAT), 2 +5V2,
3 logic 5V from the Pi's USB, 4 signals, 5 motor current, 6 ground return.
With animation off, every path shows at reduced strength and all captions stay
readable.

Every drawn connection names the net and the members it joins; the script
FAILS if docs/shield_layout.json does not have that net with those members, so
the picture cannot show a wire the layout does not have.

Usage: python scripts/shield_flow_svg.py [--layout docs/shield_layout.json] [-o docs/shield_how_it_works.svg]
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
W = 1400
CAP_CHARS = int((W - 70) / (0.62 * 11))   # caption wrap width at 11 px bold
PHASE_S, N_PHASE = 5, 6           # seconds per phase, phases

# (x, y, w, h, title, lines, border colour)
BLOCKS = {
    "pack":  (30, 70, 230, 110, "Battery pack (2S 18650)", ["7.2-8.4 V", "3 A fuse + BMS cutoff", "rocker switch, XT30"], "#C62828"),
    "lm":    (30, 250, 230, 80, "LM2596 buck (on the deck)", ["VBAT -> +5V2 (~5 V)"], "#E07B00"),
    "pi":    (30, 560, 230, 80, "Raspberry Pi 5", ["USB: powers the Uno and", "sends drive commands"], "#AD1457"),
    "j5":    (320, 90, 170, 90, "J5 power in", ["VBAT, +5V2, GND", "(KEY pin pulled out)"], "#2E7D32"),
    "caps":  (320, 220, 170, 70, "C1 470 uF + C2 0.1 uF", ["steady VBAT at VM"], "#6A1B9A"),
    "div":   (320, 330, 170, 90, "Divider 100k / 12k", ["VBAT / 9.33 -> A0", "(pack voltage)"], "#1A56B0"),
    "tb":    (560, 90, 230, 180, "TB6612 motor driver", ["VM = VBAT (motor power)", "VCC = Uno 5V (logic)",
                                                         "PWM D11, DIR D8 + D12,", "enable STBY D10;",
                                                         "A + B channels paralleled"], "#1f4e79"),
    "j1":    (850, 90, 200, 90, "J1 motor + encoder", ["M1, M2 (motor)", "+5V2, GND (encoder)"], "#6A1B9A"),
    "jp1":   (850, 230, 200, 90, "JP1 servo-power jumper", ["cap on TOP pins = Uno 5V", "cap on BOTTOM = +5V2"], "#2E7D32"),
    "j2":    (850, 360, 200, 80, "J2 servo", ["SIG = D9, V+, GND"], "#2E7D32"),
    "j34":   (850, 480, 200, 90, "J3 / J4 LED strips", ["DIN = D4 / D7 via 400 ohm", "+5V2, GND"], "#B59F00"),
    "uno":   (420, 520, 370, 150, "Arduino Uno (under the shield)", ["runs uno_control: reads the Pi's commands,",
                                                                     "drives the pins, guards the pack (A0),",
                                                                     "5V pin = rail V, fed by the Pi's USB"], "#00838F"),
    "motor": (1120, 90, 250, 90, "N20 motor + encoder", ["Pololu #5159", "encoder A/B -> D2/D3"], "#6A1B9A"),
    "servo": (1120, 360, 250, 80, "Servo (MG90D)", ["steers the rack"], "#2E7D32"),
    "strips": (1120, 480, 250, 90, "WS2812B strips", ["front + rear lights"], "#B59F00"),
}

NET_COL = {"VBAT": "#C62828", "5V2": "#E07B00", "UNO5V": "#AD1457", "PWM": "#555555",
           "SERVO_SIG": "#2E7D32", "SERVO_V": "#2E7D32", "DIN_F": "#B59F00", "A0": "#1A56B0",
           "M1": "#6A1B9A", "GND": "#222222", "ENC": "#00838F"}

# (phase, net, members it must contain in the layout file, points, label or None, label xy)
# net "ENC" is the encoder going straight to the Uno (direct_uno in the layout).
FLOWS = [
    (1, "VBAT", ["J5.VBAT"], [(260, 120), (320, 120)], "VBAT", (270, 112)),
    (1, "VBAT", ["J5.VBAT", "TB.VMOT"], [(490, 120), (560, 120)], "VM", (512, 112)),
    (1, "VBAT", ["J5.VBAT", "C1.+"], [(405, 180), (405, 220)], None, None),
    (1, "VBAT", ["J5.VBAT", "R100k.a"], [(405, 290), (405, 330)], None, None),
    (1, "VBAT", [], [(145, 180), (145, 250)], "VBAT", (152, 220)),
    (2, "5V2", ["J5.5V2"], [(260, 300), (300, 300), (300, 165), (320, 165)], "+5V2", (266, 292)),
    (2, "5V2", ["J5.5V2", "J1.5V2"], [(490, 165), (530, 165), (530, 70), (950, 70), (950, 90)], "+5V2", (826, 205)),
    (2, "5V2", ["J5.5V2", "J3.5V2", "J4.5V2"], [(820, 70), (820, 525), (850, 525)], None, None),
    (2, "5V2", ["J5.5V2", "JP1.5V2"], [(820, 300), (850, 300)], None, None),
    (3, "UNO5V", [], [(260, 600), (420, 600)], "USB 5 V", (300, 592)),
    (3, "UNO5V", ["TB.VCC", "JP1.UNO5V"], [(600, 520), (600, 270)], "VCC", (607, 300)),
    (3, "UNO5V", ["JP1.UNO5V"], [(790, 545), (805, 545), (805, 255), (850, 255)], None, None),
    (3, "SERVO_V", ["JP1.SERVO_V", "J2.V"], [(950, 320), (950, 360)], "servo V+", (957, 334)),
    (4, "PWM", ["TB.PWMA", "uno:D11"], [(700, 520), (700, 270)], "D11 D8 D12 D10", (707, 470)),
    (4, "SERVO_SIG", ["J2.SIG", "uno:D9"], [(790, 610), (835, 610), (835, 410), (850, 410)], "D9", (842, 432)),
    (4, "SERVO_SIG", ["J2.SIG"], [(1050, 400), (1120, 400)], None, None),
    (4, "DIN_F", ["J3.DIN", "uno:D4"], [(790, 640), (843, 640), (843, 555), (850, 555)], "D4 D7", (800, 632)),
    (4, "DIN_F", ["J3.DIN"], [(1050, 525), (1120, 525)], "data", (1062, 517)),
    (4, "A0", ["R100k.b", "uno:A0"], [(405, 420), (405, 645), (420, 645)], "A0", (412, 500)),
    (4, "ENC", [], [(1245, 180), (1245, 720), (700, 720), (700, 670)], "encoder A/B -> D2, D3 (straight to the Uno)", (870, 712)),
    (5, "M1", ["TB.AO1", "J1.M1"], [(790, 135), (850, 135)], "M1 M2", (800, 127)),
    (5, "M1", ["J1.M1"], [(1050, 135), (1120, 135)], "motor", (1062, 127)),
    (6, "GND", ["J5.GND"], [(320, 175), (310, 175), (310, 806)], None, None),
    (6, "GND", [], [(260, 325), (310, 325)], None, None),
    (6, "GND", ["R2k.b"], [(320, 410), (310, 410)], None, None),
    (6, "GND", ["TB.GND1"], [(760, 270), (760, 350), (1065, 350)], None, None),
    (6, "GND", ["J1.GND"], [(1050, 170), (1065, 170), (1065, 806)], None, None),
    (6, "GND", ["J2.GND"], [(1050, 430), (1065, 430)], None, None),
    (6, "GND", ["J3.GND", "J4.GND"], [(1050, 560), (1065, 560)], None, None),
    (6, "GND", [], [(790, 660), (1065, 660)], None, None),
    (6, "GND", [], [(310, 806), (1065, 806)], None, None),
]

CAPTIONS = [
    "1  Battery power: the 2S pack (7.2-8.4 V) feeds VBAT through the fuse, BMS and rocker into J5. VBAT powers the motor "
    "driver (VM; C1 + C2 steady it), the divider, and the LM2596.",
    "2  +5V2: the LM2596 steps VBAT down to ~5 V for the LED strips and the encoder - and for the servo only if JP1's cap "
    "is moved to the bottom pins.",
    "3  Logic 5V: the Pi's USB powers the Uno; the Uno's 5V (rail V) feeds the TB6612's logic (VCC) and, through JP1's "
    "top two pins (the current setting), the servo.",
    "4  Signals: the Uno sends speed (PWM D11), direction (D8, D12) and enable (D10) to the TB6612, the servo angle on D9 "
    "and LED data on D4 / D7; it reads the encoder (D2, D3) and the pack voltage (A0, via the divider).",
    "5  Motor current: the TB6612 switches VBAT through its paralleled A + B outputs into J1's M1 / M2 and the N20 motor.",
    "6  Ground return: every ground meets at one point, rail B (the star), by design - the drawing's black lines.",
]


def check_against_layout(data: dict) -> list[str]:
    nets = data["nets"]
    errs = []
    for ph, net, members, *_ in FLOWS:
        if net == "ENC":
            if {d.get("uno") for d in data.get("direct_uno", [])} != {"D2", "D3"}:
                errs.append("encoder: layout direct_uno is not D2 + D3")
            continue
        if net not in nets:
            errs.append(f"net {net} not in the layout")
            continue
        for m in members:
            if m not in nets[net]:
                errs.append(f"net {net}: {m} is not a member in the layout")
    for extra in ("DIN_R", "DIR1", "DIR2", "STBY", "M2"):     # drawn as shared lines; must exist
        if extra not in nets:
            errs.append(f"net {extra} not in the layout")
    return errs


def build(data: dict) -> str:
    caps = [textwrap.wrap(c, CAP_CHARS, subsequent_indent="   ") for c in CAPTIONS]
    H = 880 + sum(len(c) for c in caps) * 16 + len(caps) * 4 + 20
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Arial, Helvetica, sans-serif" font-weight="bold">']
    total = PHASE_S * N_PHASE
    css = [".flow{fill:none;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:10 8;"
           "animation:dash 0.9s linear infinite}", "@keyframes dash{to{stroke-dashoffset:-18}}"]
    for k in range(1, N_PHASE + 1):
        a, b = (k - 1) / N_PHASE * 100, k / N_PHASE * 100
        css.append(f".p{k}{{opacity:.18;animation:dash 0.9s linear infinite,ph{k} {total}s linear infinite}}")
        css.append(f".c{k}{{opacity:0;animation:ph{k}c {total}s linear infinite}}")
        css.append(f"@keyframes ph{k}{{0%,{max(a - 0.01, 0):.2f}%{{opacity:.18}}{a:.2f}%,{b - 0.5:.2f}%{{opacity:1}}"
                   f"{b:.2f}%,100%{{opacity:.18}}}}")
        css.append(f"@keyframes ph{k}c{{0%,{max(a - 0.01, 0):.2f}%{{opacity:0}}{a:.2f}%,{b - 0.5:.2f}%{{opacity:1}}"
                   f"{b:.2f}%,100%{{opacity:0}}}}")
    css.append("@media (prefers-reduced-motion: reduce){.flow,.p1,.p2,.p3,.p4,.p5,.p6{animation:none;opacity:1}}")
    o.append("<style>" + "".join(css) + "</style>")
    o.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    o.append('<text x="30" y="34" font-size="22" fill="#111">Proto shield - what each part does, and how the current flows</text>')
    o.append('<text x="30" y="54" font-size="12" fill="#444">Block diagram (not hole-level). Moving dashes = current, '
             'coloured by net; the six phases below light up in turn (30 s loop). Built from docs/shield_layout.json.</text>')
    # shield frame
    o.append('<rect x="290" y="78" width="790" height="760" rx="12" fill="none" stroke="#9aa5b1" stroke-width="1.5" '
             'stroke-dasharray="6 4"/>')
    o.append('<text x="300" y="854" font-size="12" fill="#5c6b7a">PROTO SHIELD (sits on the Uno)</text>')
    # flows first (under the blocks' edges)
    for ph, net, _m, pts, label, lxy in FLOWS:
        col = NET_COL[net]
        d = " ".join(f"{x},{y}" for x, y in pts)
        o.append(f'<polyline class="flow p{ph}" points="{d}" stroke="{col}"/>')
    # star bar
    o.append('<rect x="306" y="801" width="764" height="10" rx="3" fill="#222222"/>')
    o.append('<text x="700" y="828" font-size="12" fill="#222" text-anchor="middle">Rail B = GND star - every ground meets here</text>')
    # blocks
    for key, (x, y, w, h, title, lines, col) in BLOCKS.items():
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#ffffff" stroke="{col}" stroke-width="2.5"/>')
        o.append(f'<text x="{x + 10}" y="{y + 20}" font-size="13" fill="{col}">{escape(title)}</text>')
        for i, ln in enumerate(lines):
            o.append(f'<text x="{x + 10}" y="{y + 40 + i * 16}" font-size="11" fill="#333">{escape(ln)}</text>')
    # flow labels on white tags
    for ph, net, _m, pts, label, lxy in FLOWS:
        if not label:
            continue
        tw = 0.62 * 11 * len(label) + 8
        o.append(f'<rect x="{lxy[0] - 3}" y="{lxy[1] - 11}" width="{tw:.0f}" height="15" rx="3" fill="#ffffff"/>')
        o.append(f'<text x="{lxy[0]}" y="{lxy[1]}" font-size="11" fill="{NET_COL[net]}">{escape(label)}</text>')
    # caption list: all lines readable; the active phase gets a highlight bar
    y = 880
    for k, lines in enumerate(caps, 1):
        o.append(f'<rect class="c{k}" x="24" y="{y - 13}" width="{W - 48}" height="{16 * len(lines) + 1}" rx="4" '
                 f'fill="#fff3c4"/>')
        for ln in lines:
            o.append(f'<text x="30" y="{y}" font-size="11" fill="#222">{escape(ln)}</text>')
            y += 16
        y += 4
    o.append("</svg>")
    return "\n".join(o) + "\n"


def self_check() -> None:
    data = json.loads((ROOT / "docs" / "shield_layout.json").read_text(encoding="utf-8"))
    assert check_against_layout(data) == [], check_against_layout(data)
    bad = json.loads(json.dumps(data))
    bad["nets"]["VBAT"].remove("TB.VMOT")             # planted: VM no longer on VBAT
    assert any("TB.VMOT" in e for e in check_against_layout(bad)), "planted net error not caught"
    svg = build(data)
    assert svg.count('class="flow p') == len(FLOWS) and all(f".p{k}{{" in svg for k in range(1, 7))
    assert all(len(ln) * 0.62 * 11 < W - 60 for c in CAPTIONS for ln in textwrap.wrap(c, CAP_CHARS)), \
        "a caption line is wider than the page"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--layout", type=Path, default=ROOT / "docs" / "shield_layout.json")
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "docs" / "shield_how_it_works.svg")
    args = ap.parse_args(argv)
    data = json.loads(args.layout.read_text(encoding="utf-8"))
    errs = check_against_layout(data)
    for e in errs:
        print(f"FAIL {e}")
    if errs:
        return 1
    args.out.write_text(build(data), encoding="ascii", newline="\n")
    print(f"PASS every drawn connection is in the layout ({len(FLOWS)} paths); wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
