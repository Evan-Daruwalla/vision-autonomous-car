"""Generate the MG90S-spline -> female-Lego-axle steering coupler as a binary STL.

Zero dependencies, same discipline as gen_tolerance_coupon.py: the mesh is
checked closed and consistently wound, its signed volume is checked against an
independently-computed analytic volume, and NOTHING is written if either fails.

WHAT THIS PART IS, AND WHAT IT IS NOT
-------------------------------------
It is the servo-to-pinion coupling of PRD task 8c(ii) -- the highest-torque
joint on the car (Appendix BV). It is a printed STOPGAP to try before paying
$10 shipping for a $0.75 Adafruit #4252 (Evan, 2026-09-03), NOT a proven
replacement for it. Appendix BV's finding still stands and this design obeys
it: **a printed male cross-axle profile FAILS** (SF 0.57-0.96 at MG90S stall,
thin cruciform fins shearing along layer lines). This part prints NO cross
profile. It prints a thick-walled FEMALE SOCKET that receives a REAL Lego
axle, which is the geometry the docs already permit ("socket-style only",
`steering.md`).

THE SERVO END IS A PLAIN ROUND BORE, ON PURPOSE
-----------------------------------------------
The MG90S output is a 20-tooth spline of ~4.8-4.9 mm outer diameter
(TinyTronics/SkyStar datasheet; servodatabase). 20 teeth on a 4.85 mm circle
is a ~0.76 mm tooth pitch -- below what a 0.4 mm nozzle resolves, so a
"modelled spline" would print as a blurred round hole and lie about its own
fidelity. Instead the bore is deliberately UNDERSIZE and the servo's metal
spline cuts its own seat on first assembly.

⚠️ THAT INTERFACE IS THE WEAK POINT AND IT IS UNTESTED. Friction plus
spline-bite on a 4.65 mm bore is exactly the joint Appendix BV worried about,
just at a larger diameter with far more surrounding material than a printed
cross profile has. **No safety factor is claimed here** -- none can be
computed without a torque test. What actually protects this joint is the
existing rule that the servo must never reach stall (SERVO_US_SPAN limiting,
`uno_control.ino` / task 8c). If it slips under load, the upgrade is a
transverse M2 grub screw through the wall into the bore, not a bigger servo
(BOM row 7: the MG996R makes the coupling problem ~5x worse, not better).

NUMBERS THAT ARE NOT YET MEASURED -- caliper these and re-run
-------------------------------------------------------------
  SPLINE_DIA   4.85  datasheet range 4.8-4.9; measure the real servo
  AXLE_ARM     1.80  arm thickness of a Lego cross axle. Community value,
                     NOT confirmed against an authoritative source. The 4.8 mm
                     across-the-cross span IS confirmed (cailliau.org).
  SOCKET_CLEAR 0.20  provisional. The RIGHT source for this is the M1.3
                     tolerance coupon's axle row, which has not been printed.
  BORE_INTERF  0.20  press interference; pure guess, first print will say.

Usage:  python scripts/gen_servo_lego_coupler.py [-o out.stl]
"""

import argparse
import math
import struct
import sys
from collections import Counter
from pathlib import Path

# ---- geometry, all mm -------------------------------------------------------
OD = 10.0            # body outer diameter (v1/v2; v3 is 7.4 via --od)
MIN_WALL = 1.2       # refuse below this: three 0.4 mm-nozzle perimeters
TOTAL_LEN = 16.0     # matches Adafruit #4252's 16 mm so it drops into the same space

SPLINE_DIA = 4.85    # MG90S 20T spline OD (datasheet 4.8-4.9)
BORE_INTERF = 0.20   # bore is undersize by this; the spline cuts its own seat
BORE_DIA = SPLINE_DIA - BORE_INTERF
BORE_DEPTH = 8.0     # servo end, from z=0
BORE_FLAT = 0.0      # 0 = round bore. >0 = D-bore, this many mm across the
                     # flat (the drive motor's 3 mm D-shaft, 2026-10-10)

SCREW_DIA = 2.2      # axial access for the servo's OWN retaining screw (M2),
                     # so the coupler cannot walk off the shaft. Zero new parts.
WEB_TOP = 10.0       # web spans BORE_DEPTH -> WEB_TOP (2 mm of solid material)

AXLE_SPAN = 4.80     # Lego cross axle, across the cross -- confirmed
AXLE_ARM = 1.80      # arm thickness -- community value, UNVERIFIED
SOCKET_CLEAR = 0.20  # added to both, provisional until the M1.3 coupon prints
SOCKET_SPAN = AXLE_SPAN + SOCKET_CLEAR
SOCKET_ARM = AXLE_ARM + SOCKET_CLEAR
SOCKET_DEPTH = TOTAL_LEN - WEB_TOP   # 6.0 mm

FILL_ANGLES = 64     # fill points around the circles, before corner angles


def cross_radius(th, span, arm):
    """Exit distance of a ray at angle th from the centre of a Lego cross.

    The cross is the union of two boxes: (span x arm) and (arm x span). The
    centre is inside both, so the union's exit is the further of the two
    box exits. Exact -- no sampling error in the profile itself.
    """
    c, s = abs(math.cos(th)), abs(math.sin(th))
    inf = float("inf")
    e1 = min((span / 2) / c if c > 1e-12 else inf, (arm / 2) / s if s > 1e-12 else inf)
    e2 = min((arm / 2) / c if c > 1e-12 else inf, (span / 2) / s if s > 1e-12 else inf)
    return max(e1, e2)


def build_angles():
    """One angle list shared by EVERY ring in the model.

    Two reasons this is one global list rather than per-feature sampling:
    shared boundaries then have bit-identical vertices (the manifold check is
    unforgiving about T-junctions), and every annular face becomes a plain quad
    strip. The 12 exact corner angles of the cross are included, so the socket
    profile is geometrically exact rather than angularly rounded -- rounding
    the concave notches would tighten the corners and stop a real axle seating.
    """
    hs, ha = SOCKET_SPAN / 2, SOCKET_ARM / 2
    corners = []
    for sx in (1, -1):
        for sy in (1, -1):
            corners += [(sx * hs, sy * ha), (sx * ha, sy * ha), (sx * ha, sy * hs)]
    angs = {math.atan2(y, x) % (2 * math.pi) for x, y in corners}
    if BORE_FLAT > 0:   # the D's two flat-to-arc corners, exact (same reason)
        t = math.acos((BORE_FLAT - BORE_DIA / 2) / (BORE_DIA / 2))
        angs |= {t, 2 * math.pi - t}
    angs |= {2 * math.pi * k / FILL_ANGLES for k in range(FILL_ANGLES)}
    return sorted(angs)


ANGLES = build_angles()
N = len(ANGLES)


def gap_comp():
    """Per-vertex radial compensation so a bore is not printed undersize.

    A polygon through points ON the circle is inscribed, so it is smaller than
    the circle by (1 - cos(half-step)). For a HOLE that error subtracts from
    the fit. Push each vertex out by its own local half-gap; with a
    non-uniform angle list the gaps differ, so this is computed per vertex
    rather than assumed uniform (the coupon generator could assume it).
    """
    out = []
    for i, a in enumerate(ANGLES):
        prev = ANGLES[i - 1] - (2 * math.pi if i == 0 else 0)
        nxt = ANGLES[(i + 1) % N] + (2 * math.pi if i == N - 1 else 0)
        half = max(a - prev, nxt - a) / 2
        out.append(1.0 / math.cos(half))
    return out


COMP = gap_comp()


def ring_circle(dia, compensate):
    r = dia / 2
    return [(r * (COMP[i] if compensate else 1.0) * math.cos(a),
             r * (COMP[i] if compensate else 1.0) * math.sin(a))
            for i, a in enumerate(ANGLES)]


def ring_bore():
    """Round bore, or a D: the compensated circle cut by a flat at +x."""
    pts = ring_circle(BORE_DIA, compensate=True)
    if BORE_FLAT <= 0:
        return pts
    d = BORE_FLAT - BORE_DIA / 2          # flat's distance from the centre
    out = []
    for (x, y), a in zip(pts, ANGLES):
        c = math.cos(a)
        r = math.hypot(x, y)
        if c > 1e-12 and d / c < r:
            r = d / c
        out.append((r * math.cos(a), r * math.sin(a)))
    return out


def ring_cross():
    return [(cross_radius(a, SOCKET_SPAN, SOCKET_ARM) * math.cos(a),
             cross_radius(a, SOCKET_SPAN, SOCKET_ARM) * math.sin(a))
            for a in ANGLES]


def area(pts):
    """Shoelace. Positive for CCW."""
    s = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        s += x0 * y1 - x1 * y0
    return s / 2


def quad(tris, a, b, c, d):
    tris.append((a, b, c))
    tris.append((a, c, d))


def wall(tris, pts, z0, z1, outward):
    """Vertical wall between two z levels. outward=False for a bore."""
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        a = (p[0], p[1], z0)
        b = (q[0], q[1], z0)
        c = (q[0], q[1], z1)
        d = (p[0], p[1], z1)
        if outward:
            quad(tris, a, b, c, d)
        else:
            quad(tris, a, d, c, b)


def annulus(tris, outer, inner, z, up):
    """Flat ring between two same-length rings. up=True -> normal +z."""
    for i in range(len(outer)):
        o0, o1 = outer[i], outer[(i + 1) % len(outer)]
        i0, i1 = inner[i], inner[(i + 1) % len(inner)]
        a = (o0[0], o0[1], z)
        b = (o1[0], o1[1], z)
        c = (i1[0], i1[1], z)
        d = (i0[0], i0[1], z)
        if up:
            quad(tris, a, b, c, d)
        else:
            quad(tris, a, d, c, b)


def build():
    body = ring_circle(OD, compensate=False)      # outer surface: inscribed is fine
    bore = ring_bore()
    screw = ring_circle(SCREW_DIA, compensate=True)
    socket = ring_cross()
    tris = []

    wall(tris, body, 0.0, TOTAL_LEN, outward=True)
    annulus(tris, body, bore, 0.0, up=False)               # servo-end face
    wall(tris, bore, 0.0, BORE_DEPTH, outward=False)
    annulus(tris, bore, screw, BORE_DEPTH, up=False)       # roof of the servo bore
    wall(tris, screw, BORE_DEPTH, WEB_TOP, outward=False)  # screwdriver access
    annulus(tris, socket, screw, WEB_TOP, up=True)         # floor of the socket
    wall(tris, socket, WEB_TOP, TOTAL_LEN, outward=False)
    annulus(tris, body, socket, TOTAL_LEN, up=True)        # Lego-end face
    return tris


def check_manifold(tris):
    key = lambda p: (round(p[0], 5), round(p[1], 5), round(p[2], 5))
    edges = Counter()
    for t in tris:
        for i in range(3):
            edges[(key(t[i]), key(t[(i + 1) % 3]))] += 1
    dup = sum(1 for c in edges.values() if c != 1)
    unmatched = sum(1 for (a, b) in edges if (b, a) not in edges)
    return dup, unmatched


def signed_volume(tris):
    total = 0.0
    for a, b, c in tris:
        total += (a[0] * (b[1] * c[2] - b[2] * c[1])
                  - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return total / 6


def expected_volume():
    """Independent of the mesh: analytic areas of the actual generated polygons."""
    return (area(ring_circle(OD, False)) * TOTAL_LEN
            - area(ring_bore()) * BORE_DEPTH
            - area(ring_circle(SCREW_DIA, True)) * (WEB_TOP - BORE_DEPTH)
            - area(ring_cross()) * SOCKET_DEPTH)


def write_stl(tris, path):
    with open(path, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
            m = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(struct.pack("<12fH", nx / m, ny / m, nz / m, *a, *b, *c, 0))


def main():
    global SOCKET_CLEAR, SOCKET_SPAN, SOCKET_ARM, ANGLES, N, COMP
    global OD, BORE_DEPTH, WEB_TOP, SOCKET_DEPTH, TOTAL_LEN
    global BORE_DIA, BORE_FLAT, SCREW_DIA
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="cad/servo_lego_coupler_v1.stl")
    # Added 2026-10-04 after Evan printed v1: its socket (+0.20 = the coupon's
    # FREE-SPIN axle-bore offset) held the Lego axle too loosely. A grip wants
    # the coupon's PIN-row offset, which passed at 0.00 (4.80 modelled for a
    # 4.8 pin) -> v2. Default stays 0.20 so v1 regenerates byte-identically.
    # shortcut: one clearance for span and arm alike; if 0.00 is too tight in
    # ABS, re-run at 0.05 / 0.10 rather than modelling the arms separately.
    ap.add_argument("--socket-clear", type=float, default=SOCKET_CLEAR,
                    help="mm added to the Lego cross on span and arm "
                         "(v1 0.20 = too loose when printed; v2 0.00)")
    # Added 2026-10-10 for v3 (Evan, after fitting v2: "walls 1/2 as thick and a
    # bit shorter overall, other than that the dimensions are good"). Defaults
    # are v1/v2's, so both still regenerate byte-identically. The web between
    # bore and socket stays 2 mm; TOTAL_LEN follows from the two depths.
    ap.add_argument("--od", type=float, default=OD, help="body outer diameter, mm")
    ap.add_argument("--bore-depth", type=float, default=BORE_DEPTH,
                    help="servo-spline bore depth, mm")
    ap.add_argument("--socket-depth", type=float, default=SOCKET_DEPTH,
                    help="Lego-axle socket depth, mm")
    # Added 2026-10-10 for the DRIVE-motor coupler (Pololu #5159, 3 mm D-shaft).
    # Defaults are the servo coupler's, so v1-v3 regenerate byte-identically.
    ap.add_argument("--bore-dia", type=float, default=BORE_DIA,
                    help="motor/servo-end bore diameter, mm")
    ap.add_argument("--bore-flat", type=float, default=BORE_FLAT,
                    help="D-bore: mm across the flat (0 = round)")
    ap.add_argument("--screw-dia", type=float, default=SCREW_DIA,
                    help="through-hole in the web, mm")
    args = ap.parse_args()

    OD = args.od
    BORE_DEPTH = args.bore_depth
    WEB_TOP = BORE_DEPTH + 2.0
    SOCKET_DEPTH = args.socket_depth
    TOTAL_LEN = WEB_TOP + SOCKET_DEPTH
    BORE_DIA = args.bore_dia
    BORE_FLAT = args.bore_flat
    SCREW_DIA = args.screw_dia
    if BORE_FLAT and not BORE_DIA / 2 < BORE_FLAT < BORE_DIA:
        ap.error("--bore-flat must lie between the bore radius and diameter")

    SOCKET_CLEAR = args.socket_clear
    SOCKET_SPAN = AXLE_SPAN + SOCKET_CLEAR
    SOCKET_ARM = AXLE_ARM + SOCKET_CLEAR
    ANGLES = build_angles()     # the exact cross corners move with the socket
    N = len(ANGLES)
    COMP = gap_comp()

    tris = build()
    dup, unmatched = check_manifold(tris)
    vol, exp = signed_volume(tris), expected_volume()
    err = abs(vol - exp) / exp
    wall_bore = (OD - BORE_DIA) / 2
    wall_socket = (OD - SOCKET_SPAN) / 2
    # Appendix FD #6: `--socket-clear 6` produced wall -0.40 and still printed
    # OVERALL PASS -- the mesh checks prove a closed solid, not a printable
    # one. 1.2 mm = three 0.4 mm-nozzle perimeters; below that it is not a wall.
    walls_ok = min(wall_bore, wall_socket) >= MIN_WALL
    # The web's through-hole must sit strictly inside BOTH bores, at every
    # angle -- a 2.2 mm hole crosses a 3 mm D-shaft's flat (1.0 mm off centre)
    # and the annulus faces would fold through each other. Mesh checks miss it.
    screw_r = [math.hypot(x, y) for x, y in ring_circle(SCREW_DIA, True)]
    nested = all(s < math.hypot(*b) and s < math.hypot(*c)
                 for s, b, c in zip(screw_r, ring_bore(), ring_cross()))
    ok = dup == 0 and unmatched == 0 and vol > 0 and err < 1e-6 and walls_ok and nested

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if ok:                      # never leave a bad mesh on disk looking printable
        write_stl(tris, out)

    print(f"body       : OD {OD:.2f} x {TOTAL_LEN:.2f} mm")
    if BORE_FLAT > 0:
        print(f"D bore     : {BORE_DIA:.2f} mm dia, {BORE_FLAT:.2f} across the flat "
              f"x {BORE_DEPTH:.2f} deep (wall {wall_bore:.2f})")
    else:
        print(f"servo bore : {BORE_DIA:.2f} mm dia x {BORE_DEPTH:.2f} deep "
              f"({SPLINE_DIA - BORE_DIA:.2f} under the {SPLINE_DIA:.2f} spline; wall {wall_bore:.2f})")
    print(f"screw hole : {SCREW_DIA:.2f} mm dia, z {BORE_DEPTH:.1f}-{WEB_TOP:.1f}")
    print(f"axle socket: {SOCKET_SPAN:.2f} across x {SOCKET_ARM:.2f} arm "
          f"x {SOCKET_DEPTH:.2f} deep (clear {SOCKET_CLEAR:.2f}; wall {wall_socket:.2f})")
    print(f"ring points: {N} ({FILL_ANGLES} fill + exact cross corners)")
    print(f"triangles  : {len(tris)}")
    print(f"manifold   : duplicate-directed-edges={dup} unmatched-edges={unmatched}"
          f"  -> {'PASS' if dup == 0 and unmatched == 0 else 'FAIL'}")
    print(f"volume     : {vol:.4f} mm^3 (expected {exp:.4f}, rel.err {err:.2e})"
          f"  -> {'PASS' if vol > 0 and err < 1e-6 else 'FAIL'}")
    print(f"hole nested: inside bore and socket at every angle  -> {'PASS' if nested else 'FAIL'}")
    print(f"walls      : min {min(wall_bore, wall_socket):.2f} mm (need >= {MIN_WALL:.2f})"
          f"  -> {'PASS' if walls_ok else 'FAIL'}")
    print(f"OVERALL    : {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"NOT WRITTEN: {out} (geometry failed validation)")
        return 1
    print(f"wrote      : {out}  ({out.stat().st_size} bytes)")
    print()
    print("UNVERIFIED: no torque margin is claimed. The bore-to-spline grip is")
    print("friction + spline bite and has never been loaded. Print, fit, and")
    print("test against the servo's own stall before trusting it on the car.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
