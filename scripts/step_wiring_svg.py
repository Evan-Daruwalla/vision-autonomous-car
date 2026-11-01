#!/usr/bin/env python
"""Draw the two bench-step wiring sheets from WIRING_PROTOSHIELD.md section 5.

  docs/step2b_power_wiring.svg   - build step 2b: everything after the rocker (W8-W14)
  docs/step5_motor_encoder.svg   - build step 5: motor + encoder cable (W16)

Stdlib only. Header pins (J5, J6, J1) and the encoder's D2 / D3 come from
docs/shield_layout.json; wire cut lengths come from scripts/pack_wiring_svg.py's
cut list. self_check() fails if either source drifts from what is drawn.

Usage: python scripts/step_wiring_svg.py [--check]
"""
from __future__ import annotations

import json
import re
import sys
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
LAYOUT = ROOT / "docs" / "shield_layout.json"
PACK = ROOT / "scripts" / "pack_wiring_svg.py"
OUT_2B = ROOT / "docs" / "step2b_power_wiring.svg"
OUT_5 = ROOT / "docs" / "step5_motor_encoder.svg"
W = 1400
CW = 0.62          # glyph width estimate, as a fraction of font size
PITCH = 60         # close-up hole pitch, px

RED, BLK, ORG, GRY = "#C62828", "#222222", "#E65100", "#9E9E9E"
BLU, GRN, YEL, WHT, MOT = "#1565C0", "#2E7D32", "#F9A825", "#FFFFFF", "#6A1B9A"

CUTS = {"W8": 80, "W9": 250, "W10": 100, "W12": 260, "W13": 220, "W14": 120}


class Svg:
    def __init__(self):
        self.parts: list[str] = []

    def t(self, x, y, s, fs=12, fill=BLK, anchor="start", bold=True):
        w = ' font-weight="bold"' if bold else ' font-weight="normal"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{fill}" '
                          f'text-anchor="{anchor}"{w}>{escape(s)}</text>')

    def box(self, x, y, w, h, title, lines=(), fill="#F4F6F8", stroke="#5F5E5A"):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="2"/>')
        self.t(x + 10, y + 20, title, 14)
        for i, ln in enumerate(lines):
            self.t(x + 10, y + 40 + 16 * i, ln, 11, "#4A4A46", bold=False)

    def wire(self, pts, col, width=4, dashed=False, outline=False):
        d = " ".join(f"{x},{y}" for x, y in pts)
        if outline:   # white / yellow wires need a dark edge to show on white
            self.parts.append(f'<polyline points="{d}" fill="none" stroke="#555" '
                              f'stroke-width="{width + 2}" stroke-linejoin="round"/>')
        dash = ' stroke-dasharray="10 6"' if dashed else ""
        self.parts.append(f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="{width}" '
                          f'stroke-linejoin="round"{dash}/>')

    def label(self, x, y, s, col, fs=11):
        w = len(s) * CW * fs + 8
        self.parts.append(f'<rect x="{x - w / 2:.1f}" y="{y - fs:.1f}" width="{w:.1f}" height="{fs + 5}" '
                          f'rx="3" fill="#FFFFFF" stroke="{col}"/>')
        self.t(x, y, s, fs, col, anchor="middle")

    def dot(self, x, y, col=BLK, r=5):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>')

    def pin(self, x, y, name, side="left", col=BLK):
        self.parts.append(f'<rect x="{x - 5}" y="{y - 5}" width="10" height="10" fill="{col}"/>')
        if side == "left":
            self.t(x + 10, y + 4, name, 11)
        else:
            self.t(x - 10, y + 4, name, 11, anchor="end")

    def panel(self, x, y, w, title, lines, fill, stroke, fs=12):
        n = max(10, int((w - 24) / (CW * fs)))
        wrapped = []
        for ln in lines:
            sub = textwrap.wrap(ln, n, subsequent_indent="   ", break_on_hyphens=False) or [""]
            wrapped.extend(sub)
        h = 34 + 17 * len(wrapped) + 6
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="2"/>')
        self.t(x + 12, y + 22, title, 14)
        for i, ln in enumerate(wrapped):
            self.t(x + 12, y + 44 + 17 * i, ln, fs, bold=False)
        return h

    def doc(self, h):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
                f'font-family="Arial, sans-serif">\n<rect width="{W}" height="{h}" fill="#FFFFFF"/>\n'
                + "\n".join(self.parts) + "\n</svg>\n")


def closeup(s: Svg, x0, y0, rows, cols, grid_rows, pins, note, labels_right=False):
    """Draw a patch of shield holes; pins = {hole: (label, colour)}. Returns hole -> (x, y)."""
    xy = {}
    w = (len(cols) - 1) * PITCH + 80
    h = (len(rows) - 1) * PITCH + 90
    s.parts.append(f'<rect x="{x0 - 50}" y="{y0 - 55}" width="{w + 20}" height="{h + 10}" rx="8" '
                   f'fill="#E8F5E9" stroke="#6AA86F" stroke-width="2"/>')
    s.t(x0 - 40, y0 - 36, note, 11, "#2E5E33")
    for c in cols:
        s.t(x0 + (c - cols[0]) * PITCH, y0 - 14, str(c), 10, "#4A4A46", anchor="middle", bold=False)
    for ri, r in enumerate(rows):
        assert r in grid_rows
        y = y0 + ri * PITCH
        if labels_right:
            s.t(x0 + (len(cols) - 1) * PITCH + 24, y + 4, r, 10, "#4A4A46", bold=False)
        else:
            s.t(x0 - 24, y + 4, r, 10, "#4A4A46", anchor="end", bold=False)
        for c in cols:
            x = x0 + (c - cols[0]) * PITCH
            hole = f"{r}/{c}"
            xy[hole] = (x, y)
            if hole in pins:
                lab, col = pins[hole]
                s.parts.append(f'<rect x="{x - 9}" y="{y - 9}" width="18" height="18" fill="{col}" '
                               f'stroke="#111" stroke-width="1.5"/>')
            else:
                s.parts.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#FFFFFF" stroke="#8A8A86"/>')
    return xy


def header(s: Svg, title, sub):
    s.t(30, 40, title, 24)
    for i, ln in enumerate(textwrap.wrap(sub, int((W - 60) / (CW * 12)))):
        s.t(30, 64 + 16 * i, ln, 12, "#4A4A46", bold=False)


def footer(s: Svg, y):
    s.t(30, y, "Generated by scripts/step_wiring_svg.py from docs/shield_layout.json and the "
               "scripts/pack_wiring_svg.py cut list. A plan drawing, not a photo: nothing here has been powered.",
        11, "#4A4A46", bold=False)


def build_2b(d: dict) -> str:
    j5 = next(p for p in d["parts"] if p["id"] == "J5")["pins"]
    j6 = next(p for p in d["parts"] if p["id"] == "J6")["pins"]
    j3 = next(p for p in d["parts"] if p["id"] == "J3")["pins"]
    j4 = next(p for p in d["parts"] if p["id"] == "J4")["pins"]
    s = Svg()
    header(s, "Build step 2b - power wiring after the rocker (W8-W14)",
           "All 22 AWG. The pack side (cells, fuse, BMS, charger, XT30 pack half: W1-W7) is already done. "
           "Shield stays OFF the Uno for this whole step. Do the steps in the order of the list below: W8 and its "
           "polarity check come BEFORE any other wire, so nothing is loaded when the polarity is first measured.")

    # XT30 car half
    s.box(40, 140, 190, 170, "XT30 car half", ["female, on the car", "", "pack side (W1-W7)", "is already done"],
          fill="#FDE8E8", stroke=RED)
    s.pin(230, 190, "+", "right"); s.pin(230, 270, "-", "right")
    # rocker
    s.box(340, 110, 170, 100, "Rocker (SPST)", ["6A 250V AC marking,", "no DC rating (MK)"],
          fill="#FDE8E8", stroke=RED)
    s.pin(340, 175, "pin 1"); s.pin(510, 175, "pin 2", "right")
    # LM2596
    s.box(600, 260, 230, 220, "LM2596 buck", ["set 4.95 V unloaded (JE)", "pot locked", "", "IN- and OUT- are joined",
                                               "inside: wire only IN-"], fill="#FFF3E0", stroke=ORG)
    s.pin(600, 400, "IN+"); s.pin(600, 450, "IN-")
    s.pin(830, 400, "OUT+", "right"); s.pin(830, 450, "OUT- (no wire)", "right", col=GRY)

    # shield close-up: J5 col 10, J6 B/11, J3 / J4 for orientation
    pins = {j5["VBAT"]: ("VBAT", RED), j5["KEY"]: ("KEY", "#FFFFFF"), j5["5V2"]: ("+5V2", ORG),
            j5["GND"]: ("GND", BLK), j6["GND"]: ("GND", BLK)}
    for p in list(j3.values()) + list(j4.values()):
        pins[p] = ("", GRY)
    xy = closeup(s, 1110, 210, ["L3", "P3", "P4", "B"], [10, 11, 12, 13], d["grid"]["rows"], pins,
                 "Top view (part), as shield_holemap.svg", labels_right=True)
    x10 = xy[j5["VBAT"]][0]
    s.t(x10, 455, "J5", 13, anchor="middle")
    s.t(xy[j6["GND"]][0] + 14, 455, "J6", 13)
    s.t(xy[j3["GND"]][0], 455, "J3", 11, GRY, anchor="middle")
    s.t(xy[j4["GND"]][0], 455, "J4", 11, GRY, anchor="middle")
    s.t(xy[j5["KEY"]][0] - 16, xy[j5["KEY"]][1] + 4, "KEY", 10, "#4A4A46", anchor="end")

    # wires
    s.wire([(230, 190), (290, 190), (290, 175), (340, 175)], RED)
    s.label(290, 232, f"W8 red {CUTS['W8']}", RED)
    vb = xy[j5["VBAT"]]
    s.wire([(510, 175), (900, 175), (900, vb[1]), vb], RED)
    s.label(720, 168, f"W9 red {CUTS['W9']} (twist with W12)", RED)
    s.wire([(545, 175), (545, 400), (600, 400)], RED)
    s.dot(545, 175, RED, 6)
    s.label(545, 262, f"W10 red {CUTS['W10']}", RED)
    gnd = xy[j5["GND"]]
    s.wire([(230, 270), (270, 270), (270, 530), (920, 530), (920, gnd[1]), gnd], BLK)
    s.label(420, 534, f"W12 black {CUTS['W12']}", BLK)
    j6xy = xy[j6["GND"]]
    s.wire([(600, 450), (570, 450), (570, 565), (j6xy[0], 565), j6xy], BLK)
    s.label(760, 569, f"W13 black {CUTS['W13']}", BLK)
    p5 = xy[j5["5V2"]]
    s.wire([(830, 400), (880, 400), (880, p5[1]), p5], ORG, dashed=True)
    s.label(990, p5[1] - 8, f"W14 orange {CUTS['W14']}, LAST", ORG)


    y = 615
    do = [f"1. Rocker OFF, pack unplugged at the XT30, shield OFF the Uno.",
          f"2. W8 red, cut {CUTS['W8']} mm: XT30 car half + -> rocker pin 1. (Either rocker pin works as pin 1.)",
          "3. Polarity check now (see the right-hand box, first two lines). Unplug the pack again.",
          f"4. W9 red, cut {CUTS['W9']}: rocker pin 2 -> J5 VBAT ({j5['VBAT']}). Twist it with W12.",
          f"5. W10 red, cut {CUTS['W10']}: rocker pin 2 -> LM2596 IN+. Pin 2 now carries W9 and W10.",
          f"6. W12 black, cut {CUTS['W12']}: XT30 car half - -> J5 GND ({j5['GND']}, the star rail).",
          f"7. W13 black, cut {CUTS['W13']}: LM2596 IN- -> J6 ({j6['GND']}). OUT- gets no wire.",
          f"8. W14 orange, cut {CUTS['W14']}: LM2596 OUT+ -> J5 +5V2 ({j5['5V2']}).",
          "9. Ends for J5 / J6 (no crimper): cut 4 female-female jumpers about 30 mm from the housing, "
          "solder W9 / W14 / W12 / W13 to the stubs, heat-shrink each joint. Superglue the W9, W14, W12 "
          "housings side by side with one EMPTY housing (lift the latch, slide the contact out) in the J5 order "
          "VBAT, KEY, +5V2, GND - the empty KEY means the block cannot go on shifted. W13 keeps its own housing "
          "for J6. Do NOT push either onto the shield yet."]
    chk = ["- After step 2, pack in: rocker OFF -> rocker pin 2 to XT30 - reads 0 V.",
           "- Rocker ON -> pin 2 reads +8.x V (+ on pin 2). A minus sign = reversed XT30: STOP.",
           "- After step 9, J5 housing OFF the shield, rocker ON: LM2596 OUT+ to OUT- reads about 5.0 V "
           "(4.95 V in JE). Over 5.2 V: STOP, do not plug in.",
           "- Rocker OFF. Push J5 + J6 on. Then test card section E: Uno on the Pi's USB first, then rocker ON. "
           "Write down the J3 middle-pin voltage.",
           "- Wire lengths are cut-list estimates: lay each wire on the car before cutting.",
           "- Later, build step 8 (motor stalled): touch the J5 block after 60 s. Warm = the jumper contacts "
           "(no published amp rating) are the limit: solder W9 and W12 straight to the board."]
    h1 = s.panel(30, y, 800, "Do, in this order", do, "#F4F6F8", "#C9D1D9")
    h2 = s.panel(850, y, 520, "Check before going on", chk, "#E8F4EA", "#6AA86F")
    yy = y + max(h1, h2) + 24
    footer(s, yy)
    return s.doc(yy + 14)


def build_5(d: dict) -> str:
    j1 = next(p for p in d["parts"] if p["id"] == "J1")["pins"]
    j5 = next(p for p in d["parts"] if p["id"] == "J5")["pins"]
    enc = {e["from"].split()[1]: e["uno"] for e in d["direct_uno"] if e["from"].startswith("encoder")}
    s = Svg()
    header(s, "Build step 5 - motor + encoder (W16)",
           "Cable: Pololu #4763 6-wire, 300 mm, still UNCUT (route about 220-270 mm). Colours and JST pins from "
           "WIRING_PROTOSHIELD.md section 2.3 (Pololu #5159). Four conductors go into one 4-way housing on J1; "
           "yellow and white get male Dupont pins and plug straight into the Uno.")

    # motor box; pins listed in an order that lets the wires run without crossing
    rows = [("red", RED, "6", "motor M1", False), ("black", BLK, "5", "motor M2", False),
            ("green", GRN, "1", "encoder GND", False), ("blue", BLU, "4", "encoder Vcc", False),
            ("yellow", YEL, "3", "channel A", True), ("white", WHT, "2", "channel B", True)]
    s.box(40, 130, 270, 380, "N20 motor + encoder", ["Pololu #5159, 12 CPR", "JST SH 6-pin, 1.0 mm"],
          fill="#F3E5F5", stroke=MOT)
    ys = [200 + 50 * i for i in range(len(rows))]
    for (name, col, jst, fn, _), y in zip(rows, ys):
        s.parts.append(f'<rect x="300" y="{y - 6}" width="20" height="12" fill="{col}" stroke="#555"/>')
        s.t(290, y + 4, f"{jst} {name} - {fn}", 12, anchor="end")

    # shield close-up: J1 on row P3, cols 3-6
    pins = {j1["M1"]: ("M1", RED), j1["M2"]: ("M2", BLK), j1["GND"]: ("GND", GRN), j1["5V2"]: ("+5V2", BLU)}
    xy = closeup(s, 820, 190, ["L3", "P3"], [1, 2, 3, 4, 5, 6, 7, 8], d["grid"]["rows"], pins,
                 "Top view (part), as shield_holemap.svg; J5 / VBAT is col 10, off right")
    for key, lab in (("M1", "M1"), ("M2", "M2"), ("GND", "GND"), ("5V2", "+5V2")):
        x, y = xy[j1[key]]
        s.t(x, y - 18, lab, 11, anchor="middle")
    s.t(xy[j1["M2"]][0] + 30, 284, "J1", 13, anchor="middle")

    # Uno digital header, D7 .. D0 left to right (USB jack on the left)
    socks = {}
    for i, name in enumerate(["D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0"]):
        x = 820 + 55 * i
        socks[name] = (x, 600)
        hot = name in enc.values()
        s.parts.append(f'<rect x="{x - 10}" y="590" width="20" height="20" fill="{"#111" if hot else "#555"}" '
                       f'stroke="#111"/>')
        s.t(x, 632, name, 11, BLK if hot else GRY, anchor="middle")
    s.t(800, 600 + 5, "Uno", 13, anchor="end")
    s.t(800, 620, "sockets", 11, "#4A4A46", anchor="end", bold=False)
    s.t(820 - 10, 655, "D7 servo, D6 / D5 strips: leads of their own (record MI)", 10, GRY, bold=False)

    # wires: lanes step left and levels step down so nothing crosses
    targets = [xy[j1["M1"]], xy[j1["M2"]], xy[j1["GND"]], xy[j1["5V2"]], socks[enc["yellow"]], socks[enc["white"]]]
    lanes = [640, 620, 600, 580, 560, 540]
    levels = [330, 360, 390, 420, 520, 550]
    for (name, col, _, _, to_uno), y, tgt, lx, lv in zip(rows, ys, targets, lanes, levels):
        if to_uno:
            pts = [(320, y), (lx, y), (lx, lv), (tgt[0], lv), (tgt[0], tgt[1] - 10)]
        else:
            pts = [(320, y), (lx, y), (lx, lv), (tgt[0], lv), (tgt[0], tgt[1] + 9)]
        s.wire(pts, col, outline=name in ("white", "yellow"))
    s.label(700, 314, f"red -> J1 M1 ({j1['M1']})", RED)
    s.label(720, 434, f"blue -> J1 +5V2 ({j1['5V2']}), NEVER VBAT", BLU)
    s.label(720, 506, f"yellow -> {enc['yellow']}", "#8D6E00")
    s.label(720, 566, f"white -> {enc['white']}", "#555555")

    y = 690
    do = ["1. Rocker OFF, XT30 unplugged.",
          f"2. Cut 4 female-female jumpers about 30 mm from the housing; solder red, black, green, blue to "
          f"the stubs, heat-shrink. Superglue the housings side by side in the J1 order red M1 ({j1['M1']}), "
          f"black M2 ({j1['M2']}), green GND ({j1['GND']}), blue +5V2 ({j1['5V2']}).",
          "3. Yellow and white: the same with the male end of 2 jumpers (male pin to plug into the Uno).",
          f"4. Push the housing onto J1. Look: blue sits on the pin nearest J5 ({j1['5V2']}). A one-pin shift "
          "puts motor voltage on the encoder.",
          f"5. Yellow into {enc['yellow']}, white into {enc['white']}.",
          "6. Car on a stand, wheels off the ground. Uno on the Pi's USB, then rocker ON.",
          "7. Run host_test.py --wired at 20 % duty, both directions."]
    chk = [f"- Before step 6, power off: J1 +5V2 ({j1['5V2']}) to J5 VBAT ({j5['VBAT']}) is SILENT. A beep = STOP.",
           "- ticks count up one way and down the other.",
           "- About 358 counts per output-shaft turn by hand (12 CPR x 29.86:1).",
           "- Wheels turn backwards for 'forward'? Swap red and black at J1 and tell Claude (a wiring fact for "
           "the record; or keep the wires and flip it in firmware).",
           "- Encoder Vcc on VBAT would drive 7.4 V into the Uno's 5 V-max pins: silent board damage."]
    h1 = s.panel(30, y, 800, "Do, in this order", do, "#F4F6F8", "#C9D1D9")
    h2 = s.panel(850, y, 520, "Check before going on", chk, "#E8F4EA", "#6AA86F")
    yy = y + max(h1, h2) + 24
    footer(s, yy)
    return s.doc(yy + 14)


def self_check() -> None:
    d = json.loads(LAYOUT.read_text(encoding="utf-8"))
    nets = d["nets"]
    for part, pin, net in (("J5", "VBAT", "VBAT"), ("J5", "5V2", "5V2"), ("J5", "GND", "GND"),
                           ("J6", "GND", "GND"), ("J1", "M1", "M1"), ("J1", "M2", "M2"),
                           ("J1", "GND", "GND"), ("J1", "5V2", "5V2")):
        assert f"{part}.{pin}" in nets[net], f"{part}.{pin} not on net {net} in shield_layout.json"
    enc = {e["from"]: e["uno"] for e in d["direct_uno"] if e["from"].startswith("encoder")}
    assert enc == {"encoder yellow (A)": "D2", "encoder white (B)": "D3"}, enc
    src = PACK.read_text(encoding="utf-8")
    for wid, mm in CUTS.items():
        m = re.search(rf'\("{wid}",.*?"cut (\d+)', src)
        assert m and int(m.group(1)) == mm, f"{wid}: drawn cut {mm}, pack_wiring_svg.py says {m and m.group(1)}"
    for svg in (build_2b(d), build_5(d)):
        assert svg.count("<polyline") >= 6


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    self_check()
    if "--check" in argv:
        print("step_wiring_svg self_check: PASS")
        return 0
    d = json.loads(LAYOUT.read_text(encoding="utf-8"))
    for path, svg in ((OUT_2B, build_2b(d)), (OUT_5, build_5(d))):
        path.write_text(svg, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(ROOT)} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
