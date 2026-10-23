"""Draw docs/shield_wiring.svg: the proto shield (v.5, Evan's photo 2026-10-20) - where each
part goes on the board (left) and every net on it (right), plus the meter checks before
power. Hand-placed layout: positions are literals, so check the render after any edit.
Board landmarks are read off the photo (approximate). Nets: docs/WIRING_PROTOSHIELD.md
section 2; wire numbers W9-W17 match docs/pack_wiring_full.svg.

Usage: python scripts/shield_wiring_svg.py docs/shield_wiring.svg
"""
import sys
from xml.sax.saxutils import escape

W, H = 1500, 1230
RED, BLK, ORG, MAG, MOT, SIG, BLU = "#C62828", "#333333", "#E07B00", "#AD1457", "#6A1B9A", "#555555", "#1A56B0"
out = []


def t(x, y, s, size=12, color="#2C2C2A", bold=False, anchor="start"):
    w = ' font-weight="bold"' if bold else ""
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{w}>{escape(s)}</text>')


def rect(x, y, w, h, fill, stroke, rx=4, dash=False, sw=1, op=1.0):
    d = ' stroke-dasharray="5 4"' if dash else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def box(x, y, w, h, title, lines=(), fill="#F5F5F2", stroke="#5F5E5A"):
    rect(x, y, w, h, fill, stroke, 6)
    t(x + 8, y + 17, title, 12, bold=True)
    for i, s in enumerate(lines):
        t(x + 8, y + 33 + 14 * i, s, 10.5, "#4A4A46")


def line(pts, color, width=2, dashed=False):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    dash = ' stroke-dasharray="7 4"' if dashed else ""
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash}/>')


def dot(x, y, color="#2C2C2A", r=3):
    out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')


def tag(x, y, s, color):
    w = 6.6 * len(s) + 10
    rect(x - w / 2, y - 11, w, 15, "#FFFFFF", color, 7)
    t(x, y, s, 10.5, color, bold=True, anchor="middle")


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">')
out.append("<title>Proto shield wiring (2026-10-20)</title>")
out.append("<desc>Arduino proto shield v.5 for the autonomous car: suggested placement of the TB6612 carrier, caps, divider, strip resistors, pads and connectors (left, landmarks read off Evan's photo) and every net on the shield (right), with the meter checks to do before power. Source: docs/WIRING_PROTOSHIELD.md section 2.</desc>")
rect(0, 0, W, H, "#FFFFFF", "#FFFFFF", 0)
t(24, 32, "Proto shield (v.5) - what goes where, and every connection on it (2026-10-20)", 18, bold=True)
t(24, 54, "Left: the board as in your photo (USB end of the Uno on the LEFT, digital headers at the top). Shaded boxes = suggested spots. Board landmarks are read off the photo - approximate.", 12, "#4A4A46")
t(24, 72, "Right: every net. Wire numbers W9-W17 match docs/pack_wiring_full.svg. Lines that cross WITHOUT a dot are not connected. All wire 22 AWG.", 12, "#4A4A46")
t(24, 90, "SUPERSEDED for placement (2026-10-20): use docs/shield_holemap.svg + docs/SHIELD_BUILD.md. Since then: STAR = the printed rail B; C3 470 uF moved onto each strip's input pads.", 12, "#B00020", bold=True)

# ================= LEFT: physical top view =================
S = 9.3                       # px per mm
BX, BY = 40, 150              # board top-left
BW, BH = 68.6 * S, 53.3 * S   # 638 x 496


def P(mx, my):
    return BX + mx * S, BY + my * S


rect(BX, BY, BW, BH, "#DCE8F7", BLU, 8, sw=1.5)
t(BX, 112, "PROTO SHIELD v.5 - top view (68.6 x 53.3 mm); digital I/O pins used are in red", 12, BLU, bold=True)
# hole grid hint
for gx in range(14, 56, 3):
    for gy in range(6, 44, 3):
        x, y = P(gx, gy)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="#9DB5D8"/>')
# digital headers (top edge): AREF GND 13..8 | 7..0  (8 + 8, pre-R3 layout as photographed)
dl = ["REF", "GND", "13", "12", "11", "10", "9", "8"]
dr = ["7", "6", "5", "4", "3", "2", "1", "0"]
used = {"12", "11", "10", "9", "8", "7", "4", "3", "2"}
for blk, x0 in ((dl, 21.8), (dr, 42.4)):
    xa, ya = P(x0, 0.8)
    rect(xa - 4, ya, 2.54 * S * 8, 2.3 * S, "#222222", "#222222", 2)
    for i, name in enumerate(blk):
        x = xa + 2.54 * S * i + 8
        dot(x, ya + 10, "#FFD54F" if name in used else "#BBBBBB", 3)
        t(x, ya - 6, name, 9.5, RED if name in used else "#777777", bold=name in used, anchor="middle")
# power + analog headers (bottom edge)
pw = ["RST", "3V3", "5V", "GND", "GND", "Vin"]
an = ["A0", "A1", "A2", "A3", "A4", "A5"]
for blk, x0, cols in ((pw, 32.2, {"5V": MAG, "GND": BLK, "Vin": "#B00020"}), (an, 50.1, {"A0": RED})):
    xa, ya = P(x0, 50.6)
    rect(xa - 4, ya, 2.54 * S * 6, 2.3 * S, "#222222", "#222222", 2)
    for i, name in enumerate(blk):
        x = xa + 2.54 * S * i + 8
        c = cols.get(name)
        dot(x, ya + 10, "#FFD54F" if c else "#BBBBBB", 3)
        t(x, ya + 36, name, 9, c or "#777777", bold=bool(c), anchor="middle")
t(P(32.2, 0)[0], BY + BH + 50, "Vin: leave EMPTY (never VBAT)", 10, "#B00020", bold=True)
# printed buses
for my, label, col in ((23.2, "printed GND bus = Uno GND", BLK), (26.1, "printed 5V bus = Uno 5V (Pi USB)", MAG), (42.5, "printed GND strip = Uno GND", BLK)):
    xa, ya = P(26.9, my)
    rect(xa, ya - 3, 28 * S, 6, col, col, 2)
    t(xa - 6, ya + 4, label, 9.5, col, bold=True, anchor="end")
# other landmarks
for (mx, my, w, h, label) in ((10.5, 8.5, 6, 10, "DIP-14"), (1.5, 1.5, 6, 5, "ICSP"), (2.5, 45.5, 6, 5.5, "RESET"), (21, 45.5, 5.5, 5.5, "S1")):
    xa, ya = P(mx, my)
    rect(xa, ya, w * S, h * S, "#FFFFFF", "#7A8CA8", 2, op=0.7)
    t(xa + 3, ya + 13, label, 9.5, "#5A6A84")
t(P(14, 1.2)[0], P(14, 1.2)[1] + 4, "LED1", 9, "#5A6A84")
t(P(12, 47.5)[0], P(12, 47.5)[1] + 4, "LED2", 9, "#5A6A84")
t(BX + 6, BY + BH - 6, "<- USB end (Uno USB-B: faces the car's -y side)", 9.5, "#5A6A84", bold=True)

# suggested placement zones (mm on the board)
zones = [
    (27, 5.5, 20, 15.5, "#1A56B0", "TB6612 carrier", ["Pololu #713, on headers", "control pins toward", "D8-D12 (top)"]),
    (47.5, 5.5, 9.5, 15.5, RED, "C1 C2", ["470-1000uF", "+ 0.1uF", "VM-GND", "at the carrier"]),
    (22, 5.5, 4.5, 15.5, BLK, "STAR", ["strip", "soldered", "to TB6612", "GND pin"]),
    (27, 28.5, 13, 9.5, "#6B5B00", "R1-R4", ["2 x 200 per strip", "DIN (D4, D7)"]),
    (40.5, 28.5, 6, 9.5, ORG, "+5V2", ["own strip", "NOT the", "5V bus"]),
    (47, 28.5, 6, 9.5, ORG, "C3", ["470uF", "+5V2-GND"]),
    (53.5, 34, 11.5, 13, RED, "Divider", ["100k", "10k + 2k", "mid -> A0", "(near A0)"]),
    (57.5, 5.5, 9.5, 27, "#3E7D32", "Connectors", ["J1 motor+enc", " (6)", "J2 servo (3)", "JP1 jumper (3)", "J3 J4 strips", " (3 each)", "J5 power in", " (4)"]),
]
for (mx, my, w, h, col, title, lines) in zones:
    xa, ya = P(mx, my)
    rect(xa, ya, w * S, h * S, col, col, 4, op=0.13, sw=1.5)
    t(xa + 4, ya + 13, title, 10.5, col, bold=True)
    for i, s in enumerate(lines):
        t(xa + 4, ya + 26 + 11.5 * i, s, 9, col)
t(BX, BY + BH + 72, "On the car the USB end faces the car's -y side (the USB-B plug), so the digital-header edge faces the deck's REAR and the", 10.5, "#4A4A46")
t(BX, BY + BH + 86, "power/analog edge faces the Pi. The pack wires (W9, W12, W13, W14), motor/encoder and servo arrive from the front: put the", 10.5, "#4A4A46")
t(BX, BY + BH + 100, "connectors where their leads have the shortest run. The zones are suggestions - any free strip works if the nets match.", 10.5, "#4A4A46")

# ================= RIGHT: net map =================
X0 = 730
rect(X0 - 10, 92, W - X0 - 10, 584, "none", "#9E9E9E", 10, dash=True)
t(X0, 110, "EVERY NET ON THE SHIELD", 12, "#6B6B66", bold=True)
# incoming from the pack side
box(X0, 124, 120, 92, "From the pack", ["W9  VBAT (rocker)", "W12 GND (XT30 -)", "W13 LM2596 -", "W14 +5V2 (LM2596)"], fill="#FDE8E8", stroke=RED)
t(X0, 232, "W12, W13 -> STAR", 10, BLK, bold=True)
# VBAT pad
box(X0 + 140, 124, 100, 40, "VBAT pad", [], fill="#FFFFFF", stroke=RED)
dot(X0 + 140, 152, RED)
line([(X0 + 120, 152), (X0 + 140, 152)], RED, 2.2, dashed=True)
# TB6612
TX = X0 + 280
box(TX, 124, 215, 206, "TB6612FNG (Pololu #713)", ["", "", "", "", "", "", "", "", "C1 470-1000 uF + C2 0.1 uF:", "  VM to GND, at the carrier", "pin order: follow the silkscreen;", "A/B paralleled (bridge each pair)"], fill="#E8F0FE", stroke=BLU)
dot(TX, 150, RED); t(TX + 8, 154, "VM", 11, RED, bold=True)
dot(TX, 176, MAG); t(TX + 8, 180, "VCC <- Uno 5V bus", 10.5, MAG, bold=True)
line([(X0 + 240, 150), (TX, 150)], RED, 2.2)
pins_r = [("PWMA + PWMB", 150, "D11"), ("AIN1 + BIN1", 172, "D8"), ("AIN2 + BIN2", 194, "D12"), ("STBY", 216, "D10")]
for name, y, net in pins_r:
    dot(TX + 215, y, SIG)
    t(TX + 207, y + 4, name, 10.5, SIG, anchor="end")
    line([(TX + 215, y), (TX + 238, y)], SIG, 1.5)
    t(TX + 241, y + 4, net, 11, RED, bold=True)
for name, y in (("AO1 + BO1", 240, ), ("AO2 + BO2", 262)):
    dot(TX + 215, y, MOT)
    t(TX + 207, y + 4, name, 10.5, MOT, anchor="end")
dot(TX + 40, 330, BLK)
t(TX + 48, 326, "GND", 11, BLK, bold=True)
# STAR box under the TB6612
line([(TX + 40, 330), (TX + 40, 356)], BLK, 4)
box(TX, 356, 215, 180, "STAR (TB6612 GND pin + star strip)", ["every ground lands here on its OWN wire:", "  W12 pack - (XT30 car half)", "  W13 LM2596 IN- / OUT-", "  W15 jumper from the printed GND bus", "      (the Uno's ground, ONE point)",
                                                        "  C1 / C2 -, divider bottom, C3 -", "  J1 green (encoder GND)", "  J3 / J4 strip GND (one each)", "  J2 servo GND", "  NEVER the 5V bus, NEVER B-"], fill="#ECECEC", stroke=BLK)
# divider (W11 from the VBAT pad)
box(X0 + 140, 214, 120, 98, "Divider", ["top 100k (from VBAT)", "mid -> A0", "bottom 10k + 2k", "  = 12k -> STAR", ""], fill="#F4F4F0")
line([(X0 + 190, 164), (X0 + 190, 214)], RED, 2, dashed=True)
tag(X0 + 214, 194, "W11", RED)
line([(X0 + 260, 250), (X0 + 272, 250)], SIG, 1.5)
t(X0 + 262, 244, "A0", 11, RED, bold=True)
# +5V2 pad + C3
box(X0 + 140, 336, 120, 52, "+5V2 pad", ["own strip - NEVER", "the printed 5V bus"], fill="#FFF3E0", stroke=ORG)
line([(X0 + 120, 205), (X0 + 128, 205), (X0 + 128, 362), (X0 + 140, 362)], ORG, 2.2, dashed=True)
tag(X0 + 128, 300, "W14", ORG)
box(X0 + 140, 400, 120, 56, "C3 470 uF", ["+5V2 to GND", "at the feed; - -> STAR"], fill="#FFFFFF", stroke=ORG)
line([(X0 + 200, 388), (X0 + 200, 400)], ORG, 2)
# Uno 5V bus + JP1
box(X0, 560, 150, 70, "Uno 5V bus", ["printed 5V strip = Uno 5V", "pin = the Pi's USB 5 V", "feeds: TB6612 VCC, JP1"], fill="#FCE4EC", stroke=MAG)
box(X0 + 175, 548, 200, 92, "JP1 servo-power jumper", ["3 pins: [Uno 5V] [servo V+] [+5V2]", "cap on the LEFT pair = servo on", "the Uno 5V (Evan, JR - default)", "move it RIGHT = servo on +5V2", "(fallback if serial bytes drop)"], fill="#FFFFFF", stroke=MAG)
line([(X0 + 150, 590), (X0 + 175, 590)], MAG, 2)
line([(X0 + 260, 388), (X0 + 268, 388), (X0 + 268, 540), (X0 + 365, 540), (X0 + 365, 548)], ORG, 1.6)
t(X0 + 372, 545, "+5V2 to JP1 right pin", 9.5, ORG)
t(X0, 648, "W15: ONE jumper, printed GND bus -> STAR (the Uno's ground joins the star at one point)", 10, BLK, bold=True)

# ---- connectors (right) ----
CX = X0 + 560
box(CX, 124, 180, 150, "J1 motor + encoder (W16)", ["Pololu #4763 6-wire, 300 mm"], fill="#F3E5F5", stroke=MOT)
j1 = [("6 red  M1", 168, MOT, "AO1+BO1"), ("5 black M2", 186, MOT, "AO2+BO2"), ("4 blue Vcc", 204, ORG, "+5V2"),
      ("1 green GND", 222, BLK, "STAR"), ("3 yellow A", 240, RED, "D2"), ("2 white B", 258, RED, "D3")]
for name, y, c, net in j1:
    dot(CX, y, c)
    t(CX + 8, y + 4, name, 10.5, c)
    t(CX + 176, y + 4, net, 10.5, c, bold=True, anchor="end")
line([(TX + 215, 240), (TX + 262, 240), (TX + 262, 168), (CX, 168)], MOT, 2)
line([(TX + 215, 262), (TX + 270, 262), (TX + 270, 186), (CX, 186)], MOT, 2)
box(CX, 290, 180, 100, "J3 / J4 strips (W17)", ["3 pins each (left, right):", "  +5V2  <- +5V2 pad", "  DIN   <- D4 (J3) / D7 (J4)", "        via 200 + 200 ohm", "  GND   -> STAR, own wire each"], fill="#FFFDE7", stroke="#B59F00")
line([(X0 + 260, 352), (CX - 20, 352), (CX - 20, 320), (CX, 320)], ORG, 2)
box(CX, 404, 180, 70, "J2 servo (MG90D-270)", ["signal <- D9", "V+ (red) <- JP1 middle", "GND -> STAR"], fill="#E8F5E9", stroke="#3E7D32")
line([(X0 + 375, 604), (CX - 30, 604), (CX - 30, 440), (CX, 440)], MAG, 2)
t(X0 + 384, 598, "JP1 middle -> servo V+", 9.5, MAG)
box(CX, 488, 180, 70, "J5 power in", ["VBAT (W9) -> VBAT pad", "W12 + W13 -> STAR", "+5V2 (W14) -> +5V2 pad"], fill="#FDE8E8", stroke=RED)

# ================= BOTTOM: checks + parts =================
y = 790
t(24, y, "METER CHECKS - Uno OFF the shield, nothing plugged in, continuity (beep) mode", 14, bold=True)
checks = [
    ("1", "printed 5V bus  <->  the header's 5V pin", "BEEP", "proves the 5V bus IS the Uno's 5V (Pi USB) - so nothing from the pack may touch it"),
    ("2", "+5V2 pad  <->  printed 5V bus", "NO beep", "if it beeps, the LM2596 and the Pi's USB 5 V would fight on the Uno 5V pin - find the bridge first"),
    ("3", "VBAT pad  <->  STAR, and VBAT pad  <->  5V bus", "NO beep", "a beep is a short across the pack or onto the Uno"),
    ("4", "header Vin pin  <->  anything", "NO beep", "Vin stays empty - VBAT on Vin would run the Uno's regulator off the pack"),
    ("5", "STAR  <->  printed GND bus (after W15)", "BEEP", "the Uno's ground joins the star at ONE point"),
    ("6", "TB6612 VM  <->  STAR", "NO beep (slow rise ok)", "C1 charging can chirp briefly; a steady beep is a short"),
]
cols = (24, 50, 420, 560)
for i, h in enumerate(("#", "Probe between", "Expect", "Why")):
    t(cols[i], y + 26, h, 12, bold=True)
yy = y + 26
for c in checks:
    yy += 24
    for i, s in enumerate(c):
        t(cols[i], yy, s, 11.5, ("#0F6E56" if "BEEP" == s or s.startswith("BEEP") else "#B00020") if i == 2 else "#2C2C2A", bold=(i == 2))
yy += 40
t(24, yy, "PARTS ON THE SHIELD", 14, bold=True)
parts = [
    "TB6612FNG carrier, Pololu #713, on 0.1 in headers (not flying leads)",
    "C1 470-1000 uF electrolytic (mind + / -) and C2 0.1 uF ceramic, VM to GND, right at the carrier",
    "C3 470 uF across +5V2 / GND at the strip feed point",
    "R1-R4: 4 x 200 ohm - two in series in each strip's DIN line (400 ohm each)",
    "Divider: 100k (top), 10k + 2k in series (bottom = 12k) - NOT 10k alone",
    "J1 6-pin (motor + encoder), J2 3-pin (servo), JP1 3-pin + jumper cap, J3 / J4 3-pin (strips), J5 4-pin (power in): screw terminals or JST",
    "OFF the shield: the LM2596 and the rocker (deck -y wing), the 0.1 uF across the motor (at the motor)",
]
for s in parts:
    yy += 20
    t(36, yy, "- " + s, 11.5)
out.append("</svg>")
svg = "\n".join(out) + "\n"
assert all(ord(c) < 128 for c in svg)
open(sys.argv[1], "w", encoding="ascii", newline="\n").write(svg)
print("wrote", sys.argv[1], len(svg), "bytes, last y", yy)
