"""One-page meter test card for the soldered proto shield -> docs/shield_test_card.svg.

WHY: the checks live as prose inside docs/shield_layout.json steps 0-8, spread
across the build order. After the build, Evan needs them as ONE sheet in test
order: shorts first (a short can destroy parts at power-up), then the
connections, then the divider, then the first power-up. Every probe point on
the card is checked against shield_layout.json by self_check, so a typo in a
hole name fails here instead of on the bench.

    ./.venv/Scripts/python.exe scripts/shield_test_card_svg.py            # write the SVG
    ./.venv/Scripts/python.exe scripts/shield_test_card_svg.py --self-check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYOUT = ROOT / "docs" / "shield_layout.json"
OUT = ROOT / "docs" / "shield_test_card.svg"

# (probe A, probe B, expect, why) - wording and holes from shield_layout.json steps 0-8
SECTIONS = [
    ("A. SHORTS - power OFF, continuity mode. Do these FIRST. Any steady beep = STOP, send it to me.", "#c62828", [
        ("V/12", "G/12", "SILENT", "Uno 5V vs GND (step 0.2)"),
        ("V/12", "B/13", "SILENT", "Uno 5V vs GND (step 0.2)"),
        ("P4/5", "P4/6", "SILENT", "GND vs +5V2 - neighbours (step 3)"),
        ("P3/-1", "P3/-2", "SILENT", "+5V2 vs GND - neighbours (step 3)"),
        ("L3/10", "B/10", "SILENT", "VBAT vs GND (step 6)"),
        ("V/0", "B/2", "SILENT", "Uno 5V vs GND (step 6)"),
        ("P4/7", "B/2", "SILENT", "+5V2 vs GND (step 6)"),
        ("V/12", "P4/13", "SILENT", "Uno 5V must NOT be tied to +5V2 (step 8)"),
        ("L3/7", "L3/8", "no steady beep", "VMOT vs GND - C1 may chirp once (step 1)"),
    ]),
    ("B. CONNECTIONS - power OFF, continuity mode. Each must BEEP.", "#2e7d32", [
        ("U1/1", "U3/1", "BEEP", "one strip (step 0.1)"),
        ("U1/1", "PWMA pin", "BEEP", "carrier seated (step 2)"),
        ("L3/7", "VMOT pin", "BEEP", "carrier seated (step 2)"),
        ("L3/1", "L3/8", "BEEP", "GND through the carrier (step 2)"),
        ("P4/6", "P4/13", "BEEP", "+5V2 bus (step 3)"),
        ("V/12", "L1/-1", "BEEP", "Uno 5V to the left field (step 3)"),
        ("L3/10", "VMOT pin", "BEEP", "J5 top pin, through w1 (step 6)"),
        ("J3 middle", "J4 middle", "BEEP", "+5V2 (step 4)"),
        ("J3 bottom", "B/8", "BEEP", "GND star (step 4)"),
    ]),
    ("C. TO THE UNO - shield ON the Uno, power OFF.", "#1565c0", [
        ("U1/1", "D11", "BEEP", "(step 7)"),
        ("U1/2", "D12", "BEEP", "(step 7)"),
        ("U1/3", "D8", "BEEP", "(step 7)"),
        ("U1/4", "D10", "BEEP", "(step 7)"),
        ("U1/9", "A0", "BEEP", "battery divider (step 7)"),
        ("D7", "J2 top pin (L1/-2)", "BEEP", "servo signal - after the record LC fix"),
        ("L3/12", "D6", "~400 ohm", "200 + 200 in the wire - use ohms mode (step 7)"),
        ("L3/13", "D5", "~400 ohm", "200 + 200 in the wire - use ohms mode (step 7)"),
        ("Uno 5V pin", "V/12", "BEEP", "(step 7)"),
    ]),
    ("D. DIVIDER - ohms mode, power OFF.", "#6a1b9a", [
        ("L1/9", "U3/9", "~100k", "R100k (step 5)"),
        ("U3/9", "G/10", "~12k", "R10k + R2k (step 5)"),
    ]),
    ("E. FIRST POWER-UP - only after A-D all pass. DC volts mode.", "#e65100", [
        ("JP1", "top two pins", "jumper ON", "servo on the Uno 5V (step 8)"),
        ("Pack", "rocker OFF", "then Uno on Pi USB", "Uno first, nothing else plugged (step 8)"),
        ("J5 top pin", "GND", "~8 V (pack)", "VBAT - rocker ON now (step 8)"),
        ("J3 middle", "GND", "~5.0 V", "+5V2 from the LM2596 - WRITE IT DOWN (4.95 vs 4.99, JE/JF)"),
        ("Uno 5V pin", "GND", "~5 V", "from the Pi's USB (step 8)"),
    ]),
]

W, ROW, HEAD, PAD = 1100, 30, 38, 24
COLS = (PAD, 210, 460, 640)          # x of probe A, probe B, expect, why


def build_svg() -> str:
    rows = sum(len(r) for _, _, r in SECTIONS)
    h = 120 + len(SECTIONS) * (HEAD + 28) + rows * ROW + 70
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
         'font-family="Segoe UI, Arial, sans-serif">',
         f'<rect width="{W}" height="{h}" fill="#ffffff"/>',
         f'<text x="{PAD}" y="44" font-size="26" font-weight="700" fill="#111">Proto shield meter test card</text>',
         f'<text x="{PAD}" y="74" font-size="15" fill="#444">Source: docs/shield_layout.json steps 0-8. '
         'Do A to E in order; tick each box. Hole names = row/column on the shield grid.</text>']
    y = 104
    for title, color, rows_ in SECTIONS:
        o.append(f'<rect x="{PAD - 8}" y="{y}" width="{W - 2 * PAD + 16}" height="{HEAD - 6}" rx="6" fill="{color}"/>')
        o.append(f'<text x="{PAD}" y="{y + 22}" font-size="16" font-weight="700" fill="#fff">{escape(title)}</text>')
        y += HEAD + 18          # first row band (y - 20) must start below the header box
        for i, (a, b, exp, why) in enumerate(rows_):
            if i % 2 == 0:
                o.append(f'<rect x="{PAD - 8}" y="{y - 20}" width="{W - 2 * PAD + 16}" height="{ROW}" fill="#f3f3f3"/>')
            o.append(f'<rect x="{PAD - 2}" y="{y - 13}" width="13" height="13" fill="none" stroke="#333" stroke-width="1.5"/>')
            o.append(f'<text x="{COLS[0] + 22}" y="{y}" font-size="15" font-weight="600" fill="#111">{escape(a)}</text>')
            o.append(f'<text x="{COLS[1]}" y="{y}" font-size="15" font-weight="600" fill="#111">{escape(b)}</text>')
            o.append(f'<text x="{COLS[2]}" y="{y}" font-size="15" font-weight="700" fill="{color}">{escape(exp)}</text>')
            o.append(f'<text x="{COLS[3]}" y="{y}" font-size="13" fill="#555">{escape(why)}</text>')
            y += ROW
        y += 14
    o.append(f'<text x="{PAD}" y="{y + 14}" font-size="13" fill="#444">Any result that differs: STOP and send it. '
             'Untested until every box is ticked (no power before A-D pass).</text>')
    o.append("</svg>")
    return "\n".join(o)


HOLE = re.compile(r"\b(?:[A-Z]|[A-Z]\d)/-?\d+\b")


def self_check() -> None:
    layout = LAYOUT.read_text(encoding="utf-8")
    holes = {h for _, _, rows in SECTIONS for r in rows for h in HOLE.findall(" ".join(r[:2]))}
    missing = sorted(h for h in holes if h not in layout)
    assert not missing, f"card cites holes not in shield_layout.json: {missing}"
    assert len(holes) >= 25, len(holes)
    for pin in ("D11", "D12", "D8", "D10", "A0", "D7", "D6", "D5", "PWMA", "VMOT", "JP1", "J5"):
        assert pin in layout, pin
    svg = build_svg()
    assert svg.count('stroke-width="1.5"') == sum(len(r) for _, _, r in SECTIONS)   # one tick box per row
    assert all(ord(c) < 128 for c in svg), "non-ASCII in the card"
    bad = [h for h in ("L1/-3",) if h in svg]   # D7 goes to J2's SIG pin, not the old L1/-3 route
    assert not bad, bad
    print(f"shield_test_card self_check: PASS ({len(holes)} holes cross-checked)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)
    if a.self_check:
        self_check()
        return 0
    OUT.write_text(build_svg(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
