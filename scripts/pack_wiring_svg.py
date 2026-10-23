"""Draw docs/pack_wiring_full.svg: every pack-side wire numbered W1-W17 with its length
(solid = soldered as built, measured by Evan; dashed = still to cut, CAD estimate + cut
length). Hand-placed layout: positions are literals, so check the render after any edit.
The wire facts come from docs/WIRING_PROTOSHIELD.md section 2 and docs/ELECTRONICS_LAYOUT.md.

Usage: python scripts/pack_wiring_svg.py docs/pack_wiring_full.svg
"""
import sys
from xml.sax.saxutils import escape

W, H = 1500, 1290
RED, BLK, ORG, MOT, SIG, GRP = "#C62828", "#333333", "#E07B00", "#6A1B9A", "#757575", "#9E9E9E"
out = []


def t(x, y, s, size=12, color="#2C2C2A", bold=False, anchor="start"):
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="bold">{escape(s)}</text>')


def box(x, y, w, h, title, lines=(), fill="#F5F5F2", stroke="#5F5E5A", tsize=13):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
    t(x + 8, y + 18, title, tsize, bold=True)
    for i, s in enumerate(lines):
        t(x + 8, y + 36 + 15 * i, s, 11, "#4A4A46")


def group(x, y, w, h, label):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="{GRP}" stroke-width="1" stroke-dasharray="5 4"/>')
    t(x + 10, y + 16, label, 11, "#6B6B66", bold=True)


def wire(pts, color, tag=None, at=0, dashed=False, width=2.2, dx=0, dy=-6):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    dash = ' stroke-dasharray="7 4"' if dashed else ""
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash}/>')
    if tag:
        (x0, y0), (x1, y1) = pts[at], pts[at + 1]
        mx, my = (x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy
        wtxt = 7.0 * len(tag) + 10
        out.append(f'<rect x="{mx - wtxt / 2}" y="{my - 11}" width="{wtxt}" height="15" rx="7" fill="#FFFFFF" stroke="{color}" stroke-width="1"/>')
        t(mx, my, tag, 11, color, bold=True, anchor="middle")


def pin(x, y, label, side="left", ly=4):
    out.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#2C2C2A"/>')
    if side == "left":
        t(x + 7, y + ly, label, 11)
    else:
        t(x - 7, y + ly, label, 11, anchor="end")


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">')
out.append("<title>18650 pack - every wire, with lengths (2026-10-20)</title>")
out.append("<desc>Pack-side wiring of the autonomous car: 2S pack, BMS, fuse, charger, XT30, rocker, LM2596, TB6612, divider, motor + encoder, strips. "
           "Every wire is numbered W1-W17; the cut list gives its length. Solid = soldered as built; dashed = still to cut (estimates from the CAD, trim at the dry fit). "
           "Source: docs/WIRING_PROTOSHIELD.md section 2, docs/ELECTRONICS_LAYOUT.md, records IO-IW, JU-JW, KC.</desc>")
out.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>')
t(24, 32, "18650 pack - every wire, with lengths (2026-10-20, tray v11 / deck v13)", 18, bold=True)
t(24, 54, "Solid = soldered as built (length measured by Evan). Dashed = still to cut: estimate from the CAD, cut length in the list, trim at the dry fit. All wire 22 AWG.", 12, "#4A4A46")
t(24, 72, "Every ground wire lands on the STAR = the TB6612 GND pad on the shield (drawn as a bar: one pad, many wires). Grounds are never switched. Source: docs/WIRING_PROTOSHIELD.md section 2.", 12, "#4A4A46")

# ---- groups (where things sit on the car) ----
group(18, 92, 330, 380, "PACK (holder on the +y lobe)")
group(362, 92, 222, 380, "TRAY -y LOBE")
group(598, 92, 224, 380, "DECK -y WING (rocker hangs below it)")
group(828, 92, 360, 548, "PROTO SHIELD on the Uno (deck, rear)")
group(1202, 92, 280, 300, "UNDER THE FRAMES")
group(1202, 406, 280, 234, "CAR LIGHTS (L + R)")

# ---- pack ----
box(40, 130, 130, 52, "Cell 1 (25R)", ["+ end at the lead end"])
box(40, 255, 130, 52, "Cell 2 (25R)", ["- end at the lead end"])
out.append('<line x1="105" y1="182" x2="105" y2="255" stroke="#444441" stroke-width="3"/>')
out.append('<circle cx="105" cy="218" r="5" fill="#BA7517"/>')
t(109, 236, "brass rivet = series node", 9, "#854F0B")
t(109, 248, "(no-lead end, MB tap)", 9, "#854F0B")
box(40, 392, 130, 44, "3 A fuse (violet ATO)", ["lies on the bank top"], fill="#FAEEDA", stroke="#854F0B", tsize=12)
box(222, 120, 110, 330, "BMS", ["", "B08HLQQCQJ", "on the holder top,", "rivet end", "", "2.9 V cutoff", "(untested)"], fill="#E1F5EE", stroke="#0F6E56")
pin(222, 218, "MB"); pin(222, 300, "B-"); pin(222, 414, "B+")
pin(332, 150, "P+", "right"); pin(332, 430, "P-", "right")
# W1 CELL+ -> fuse -> B+
wire([(40, 150), (28, 150), (28, 414), (40, 414)], RED, "W1 326", at=1, dx=40, dy=-66)
wire([(170, 414), (222, 414)], RED)
wire([(105, 218), (222, 218)], "#BA7517", "W3 55", at=0, dx=22)
wire([(170, 281), (196, 281), (196, 300), (222, 300)], BLK, "W2 ?", at=0, dx=6, dy=-10)

# ---- tray -y lobe: charger between the two XT30 rails ----
box(382, 205, 86, 150, "Charger", ["", "", "Adeept p0374", "USB-C out", "the -y side", "VIN unused"], fill="#EEEDFE", stroke="#534AB7")
pin(382, 235, "BAT"); pin(382, 340, "GND")
box(478, 120, 96, 330, "XT30", ["", "", "pack | car", "pack half:", "male, soldered"], fill="#F1EFE8")
out.append('<line x1="526" y1="160" x2="526" y2="172" stroke="#9A9A94" stroke-width="1" stroke-dasharray="3 3"/>')
out.append('<line x1="526" y1="224" x2="526" y2="440" stroke="#9A9A94" stroke-width="1" stroke-dasharray="3 3"/>')
pin(478, 150, "+"); pin(478, 430, "-")
pin(574, 150, "+", "right"); pin(574, 430, "-", "right")
wire([(332, 150), (478, 150)], RED, "W5 190", at=0, dx=30)
wire([(332, 158), (352, 158), (352, 235), (382, 235)], RED, "W4 190", at=1, dx=-2, dy=12)
wire([(332, 430), (478, 430)], BLK, "W7 190", at=0, dx=30)
wire([(332, 422), (352, 422), (352, 340), (382, 340)], BLK, "W6 190", at=1, dx=-2, dy=-8)
t(372, 466, "W4+W5 share the P+ pad, W6+W7 the P- pad", 10, "#6B6B66")

# ---- deck wing: rocker + LM2596 ----
box(612, 120, 100, 70, "Rocker", ["", "2 pins, SPST", "either way round"], fill="#FDE8E8", stroke=RED)
pin(612, 150, "1"); pin(712, 150, "2", "right")
wire([(574, 150), (612, 150)], RED, "W8 80", at=0, dy=-8, dashed=True)
box(640, 262, 170, 150, "LM2596 buck", ["", "set 4.99 V unloaded (JE)", "turn it so IN faces the", "rocker (+x end)", "IN- and OUT- are common"], fill="#FFF3E0", stroke=ORG)
pin(640, 292, "IN+"); pin(640, 392, "IN-")
pin(810, 292, "OUT+", "right")
out.append('<rect x="736" y="212" width="40" height="12" rx="2" fill="#FFFFFF" stroke="#5F5E5A"/>')
t(736, 208, "power slot", 10, "#4A4A46")
t(732, 236, "(W9 + W12 go up)", 10, "#4A4A46")
wire([(712, 162), (726, 162), (726, 245), (624, 245), (624, 292), (640, 292)], RED, "W10 100", at=2, dashed=True, dy=-6)

# ---- shield: TB6612, star bar, divider, Uno ----
box(882, 128, 172, 262, "TB6612FNG", ["", "VCC <- Uno 5V", "PWMA+B <- D11", "AIN1+BIN1 <- D8", "AIN2+BIN2 <- D12", "STBY <- D10",
                                       "470-1000 uF", " VM-GND, at board", "AO1+BO1 bridged", "AO2+BO2 bridged"], fill="#E8F0FE", stroke="#1A56B0")
pin(882, 150, "VM", ly=14)
out.append('<circle cx="1054" cy="200" r="3" fill="#2C2C2A"/><circle cx="1054" cy="240" r="3" fill="#2C2C2A"/>')
t(1060, 196, "AO1+BO1", 10, MOT); t(1060, 236, "AO2+BO2", 10, MOT)
out.append('<circle cx="868" cy="150" r="4" fill="#C62828"/>')
t(876, 124, "VBAT pad", 10, RED)
wire([(712, 142), (868, 142), (868, 150), (882, 150)], RED, "W9 250", at=0, dashed=True, dx=-10)
# W11 VBAT pad -> divider top, over the TB6612
box(1086, 250, 92, 120, "Divider", ["top 100k", "bottom 12k", "(10k + 2k)", "mid -> A0"], fill="#F4F4F0")
wire([(868, 150), (868, 112), (1132, 112), (1132, 250)], RED, "W11 40", at=2, dashed=True, dx=0, dy=-20)
out.append('<line x1="1178" y1="320" x2="1192" y2="320" stroke="#757575" stroke-width="1.5"/>')
t(1174, 316, "A0", 11, SIG, bold=True, anchor="end")
# star bar
out.append('<rect x="898" y="452" width="160" height="9" rx="3" fill="#111111"/>')
t(982, 508, "STAR = TB6612 GND pad", 11, BLK, bold=True)
t(982, 522, "one pad, every ground wire", 10, BLK)
wire([(968, 390), (968, 452)], BLK, width=3)
t(962, 412, "TB6612 GND", 10, BLK, anchor="end")
wire([(574, 430), (590, 430), (590, 440), (906, 440), (906, 452)], BLK, "W12 260", at=2, dashed=True, dx=60, dy=14)
wire([(640, 392), (626, 392), (626, 428), (926, 428), (926, 452)], BLK, "W13 220", at=2, dashed=True, dx=-100)
wire([(1132, 370), (1132, 382), (992, 382), (992, 452)], BLK, "div. bottom", at=1, dx=0, dy=-4, width=1.6)
# Uno
box(882, 530, 296, 106, "Uno R3 (shield sits on it)", ["powered by the Pi's USB (JF), NOT the pack", "D11 D8 D12 D10 -> TB6612, D2 D3 <- encoder",
                                                     "D4 D7 -> strips (via 400 ohm), A0 <- divider", "5V -> TB6612 VCC + servo V+ (JR, NOT the pack)", "+5V2 must NEVER touch the Uno 5V pin"])
wire([(946, 530), (946, 510), (946, 461)], BLK, "W15 40", at=0, dashed=True, dx=0, dy=6)
# +5V2
out.append(f'<circle cx="868" cy="292" r="4" fill="{ORG}"/>')
t(878, 312, "+5V2 pad", 10, ORG, anchor="end")
wire([(810, 292), (868, 292)], ORG, "W14 120", at=0, dashed=True, dy=-8)

# ---- motor + encoder ----
box(1226, 128, 236, 246, "N20 motor + encoder", ["Pololu #5159, 12 CPR", "", "", "", "", "", "",
                                                  "blue  (enc Vcc) -> +5V2", "yellow (A) -> D2", "white (B) -> D3",
                                                  "0.1 uF across M1-M2", "cable W16: #4763, 300 UNCUT"], fill="#F3E5F5", stroke=MOT)
pin(1226, 200, "M1 red"); pin(1226, 240, "M2 black")
wire([(1054, 200), (1226, 200)], MOT, "W16", at=0, dashed=True, dx=0)
wire([(1054, 240), (1226, 240)], MOT)
pin(1226, 362, "green (enc GND) -> STAR", "left")
wire([(1226, 362), (1196, 362), (1196, 444), (1012, 444), (1012, 452)], BLK, "W16 green", at=2, dx=40, width=1.6)

# ---- strips ----
box(1226, 430, 236, 196, "WS2812B strips x2", ["left + right strip, each:", "+5V2 <- +5V2 pad (W17)", "DIN <- D4 (left) / D7 (right)",
                                               "  via 400 ohm (2 x 200)", "GND -> STAR, own wire (W17)", "470 uF +5V2-GND at the feed", "",
                                               "W17 lengths: measure on the car", "(strip positions not designed)"], fill="#FFFDE7", stroke="#B59F00")
pin(1226, 600, "GND x2")
wire([(1226, 600), (1196, 600), (1196, 492), (1034, 492), (1034, 461)], BLK, "W17", at=2, dashed=True, dx=40, width=1.6)

# ---- legend / rules (left bottom) ----
group(18, 486, 800, 154, "HOW TO READ IT")
y0 = 510
for color, dash, label in ((RED, False, "pack + / VBAT, soldered"), (RED, True, "VBAT, still to cut"), (BLK, False, "ground (P- side)"), (ORG, True, "+5V2 (LM2596 out, 5.0 V)"), (MOT, True, "motor (driver -> motor)")):
    wire([(32, y0), (72, y0)], color, dashed=dash)
    t(80, y0 + 4, label, 11)
    y0 += 18
t(300, 512, "Tag = wire number + length in mm (cut length for dashed).", 11)
t(300, 530, "W2 ? = soldered, length never recorded.", 11)
t(300, 548, "Nothing but the BMS touches B+ / MB / B- (unfused).", 11)
t(300, 566, "Encoder Vcc from +5V2 only, never VBAT.", 11)
t(300, 584, "Switch OFF = 0 V on VBAT; meter XT30 polarity (+8.x V) before any load.", 11)
t(300, 602, "The servo and the Uno are NOT on the pack (Pi USB, records JF / JR).", 11)
t(300, 620, "Lengths for dashed wires are CAD estimates - cut long, trim at the dry fit.", 11)

# ---- cut list ----
ty = 664
t(24, ty, "CUT LIST", 15, bold=True)
cols = (24, 78, 520, 640, 900)
heads = ("Wire", "From -> to", "Colour", "Length (mm)", "Route / note")
rows = [
    ("W1", "Holder red (CELL+) -> 3 A fuse -> BMS B+", "red", "326 total, SOLDERED", "measured by Evan (153 + 4 x 43.27); coil slack on the bank top"),
    ("W2", "Holder black (cell 2 -) -> BMS B-", "black", "SOLDERED, not recorded", "unfused - keep short, sleeve it"),
    ("W3", "Holder brass rivet (series node) -> BMS MB", "-", "55, SOLDERED", "unfused - BMS sits at the rivet end of the holder top"),
    ("W4", "BMS P+ -> charger BAT", "red", "190, SOLDERED", "over the bank top to the -y lobe"),
    ("W5", "BMS P+ -> XT30 pack half +", "red", "190, SOLDERED", "same route; tightest pack wire (~20-45 spare)"),
    ("W6", "BMS P- -> charger GND (the one next to BAT)", "black", "190, SOLDERED", "over the bank top to the -y lobe"),
    ("W7", "BMS P- -> XT30 pack half -", "black", "190, SOLDERED", "same route"),
    ("W8", "XT30 car half + -> rocker pin 1", "red", "cut 80 (est 30-50)", "straight up to the rocker hanging under the wing"),
    ("W9", "Rocker pin 2 -> shield VBAT pad -> TB6612 VM", "red", "cut 250 (est ~230)", "up the power slot, along the deck, twisted with W12"),
    ("W10", "Rocker pin 2 -> LM2596 IN+", "red", "cut 100 (est ~80)", "LM2596 IN end facing +x (else ~150)"),
    ("W11", "Shield VBAT pad -> divider top (100k)", "red", "jumper 30-50", "on the shield; keeps the rocker tab to 2 wires"),
    ("W12", "XT30 car half - -> STAR", "black", "cut 260 (est ~250)", "with W9 through the power slot"),
    ("W13", "LM2596 IN- (= OUT-) -> STAR", "black", "cut 220 (est 150-200)", "one leg for both; along the deck to the shield"),
    ("W14", "LM2596 OUT+ -> shield +5V2 pad", "orange", "cut 120 (est 80-100)", "+5V2 = 4.99 V; never to the Uno 5V pin"),
    ("W15", "Uno GND (shield header) -> STAR", "black", "jumper 30-50", "on the shield"),
    ("W16", "Motor + encoder: Pololu #4763 6-wire cable", "6 cores", "300, UNCUT", "route ~220-270, ~30 spare (Evan); Dupont splice at the shield if short"),
    ("W17", "+5V2 / DIN / GND to each strip segment", "3 per seg.", "measure on the car", "strip positions not designed yet"),
]
y = ty + 26
for i, h in enumerate(heads):
    t(cols[i], y, h, 12, bold=True)
out.append(f'<line x1="24" y1="{y + 6}" x2="{W - 24}" y2="{y + 6}" stroke="#BDBDB8" stroke-width="1"/>')
for r in rows:
    y += 30
    soldered = "SOLDERED" in r[3] or "UNCUT" in r[3]
    for i, c in enumerate(r):
        t(cols[i], y, c, 12, "#2C2C2A" if i != 3 else ("#0F6E56" if soldered else "#8A4B00"), bold=(i == 0))
    out.append(f'<line x1="24" y1="{y + 10}" x2="{W - 24}" y2="{y + 10}" stroke="#EEEEEA" stroke-width="1"/>')
y += 30
t(24, y, "To buy / cut for step 2b and later (22 AWG): red ~480 mm (W8-W11), black ~560 mm (W12, W13, W15), orange ~120 mm (W14). Built so far: W1-W7 (pack), LM2596 set.", 12, "#4A4A46", bold=True)
out.append("</svg>")
s = "\n".join(out) + "\n"
assert all(ord(c) < 128 for c in s)
open(sys.argv[1], "w", encoding="ascii", newline="\n").write(s)
print("wrote", sys.argv[1], len(s), "bytes, height used", y)
