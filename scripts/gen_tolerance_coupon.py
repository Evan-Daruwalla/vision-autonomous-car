"""Generate the Lego-fit tolerance test coupon (PRD M1.3) as a binary STL.

Zero dependencies. The coupon is a flat plate on an 8 mm grid -- the real Lego
beam pitch -- carrying three test features:

  PITCH row   5 holes at exactly 8.0 mm centres, all at PIN_REF diameter.
              Tests whether a real Lego pin pair / beam spans correctly, which
              catches printer dimensional scaling that a single hole cannot.
  PIN row     6 holes, 4.8 -> 5.3 mm. Target: a Lego pin pushes in and HOLDS.
  AXLE row    6 holes, 4.8 -> 5.3 mm. Target: a Lego axle spins FREELY.

Nominal Lego pin hole is 4.8 mm, but FDM holes print undersize, so the useful
answer is empirical -- hence the sweep. Community starting points are ~5.1 mm
(pin fit) and 5.3-5.6 mm (free-rotating bore); those are unverified on THIS
printer, which is the entire point of this part.

v2 (2026-09-05): AXLE_LO moved from 5.2 to 4.8, same as PIN_LO. v1 (Bambu
P1S, Bambu ABS Black, 99% shrinkage comp.) tested the axle row at 5.20-5.70
and Evan reported ALL SIX too loose ("spin very smooth... seems a bit big"
even at 5.20, the smallest). A round bore for a ROTATING cross-axle cannot
go below the axle's tip-to-tip diagonal (~4.8 mm, same figure as the pin
hole) without the corners binding, so 4.8 is the geometric floor, not a
guess below anything tested -- the same reasoning `gen_servo_lego_coupler.py`
uses for its `AXLE_ARM`/cross-socket sizing. v1's own pin-row sweep already
found 4.80 mm the best PIN fit at these settings, so this range asks whether
the same diameter that holds a pin also frees an axle, rather than assuming
they land in the same place. v1's plate is kept on disk (`tolerance_coupon_v1.stl`,
already measured) -- this is a new file, not an overwrite.

Row identification (no text -- embossed fonts need a font engine):
  PIN row  = ONE 3 mm marker hole at the left end.
  AXLE row = TWO 3 mm marker holes, one at each end.
  PITCH row = unmistakable, 5 tightly-spaced holes and no markers.

Plate is 8 mm thick so hole depth matches a real Lego beam -- hole shrinkage is
depth-dependent, so a thin coupon would report optimistic numbers.

Usage:  python scripts/gen_tolerance_coupon.py [-o out.stl]
"""

import argparse
import math
import struct
import sys
from collections import Counter
from pathlib import Path

CELL = 8.0          # Lego beam pitch, mm
NX, NY = 13, 7      # cells -> 104 x 56 mm plate
THICK = 8.0         # mm, matches a real Lego beam
SEGMENTS = 64       # circle facets; must be divisible by 4
PIN_REF = 5.1       # diameter used for the pitch row, mm
MARKER = 3.0        # row-identification hole diameter, mm
PIN_LO = 4.8        # pin-fit sweep low end, mm (unchanged since v1)
AXLE_LO = 4.8       # axle-bore sweep low end, mm -- WAS 5.2 in v1; moved down
                    # to the geometric floor (axle diagonal) after v1 found
                    # the entire 5.2-5.7 mm range too loose. See module docstring.

# (cell_x, cell_y) -> diameter in mm
HOLES = {}
for i, x in enumerate(range(4, 9)):                     # pitch row
    HOLES[(x, 1)] = PIN_REF
for i, x in enumerate(range(1, 12, 2)):                 # pin-fit sweep
    HOLES[(x, 3)] = round(PIN_LO + 0.1 * i, 4)
for i, x in enumerate(range(1, 12, 2)):                 # axle-bore sweep
    HOLES[(x, 5)] = round(AXLE_LO + 0.1 * i, 4)
HOLES[(0, 3)] = MARKER                                  # 1 marker  -> PIN row
HOLES[(0, 5)] = MARKER                                  # 2 markers -> AXLE row
HOLES[(12, 5)] = MARKER

W, H = NX * CELL, NY * CELL


def ring(cx, cy, dia, n=SEGMENTS):
    """Points of a regular n-gon whose INSCRIBED circle has the target diameter.

    A polygon inscribed in the circle would print undersize by (1 - cos(pi/n)).
    On a tolerance coupon that error is the measurement, so compensate it out.
    """
    r = (dia / 2.0) / math.cos(math.pi / n)
    return [(cx + r * math.cos(2 * math.pi * k / n),
             cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def quad(tris, a, b, c, d):
    tris.append((a, b, c))
    tris.append((a, c, d))


def cell_boundary(cx, cy):
    """The cell's square boundary subdivided into SEGMENTS points, CCW.

    EVERY cell is subdivided identically -- including cells with no hole --
    so shared edges between neighbouring cells have matching vertices. Emitting
    a hole-less cell as a single quad leaves T-junctions against its holed
    neighbours, which is non-manifold; the manifold check catches it.
    """
    h = CELL / 2.0
    corners = [(cx + h, cy - h), (cx + h, cy + h),
               (cx - h, cy + h), (cx - h, cy - h)]
    per = SEGMENTS // 4
    pts = []
    for side in range(4):
        s0, s1 = corners[side], corners[(side + 1) % 4]
        for j in range(per):
            t = j / per
            pts.append((s0[0] + (s1[0] - s0[0]) * t,
                        s0[1] + (s1[1] - s0[1]) * t))
    return pts


def cell_face(tris, cx, cy, dia, z, up):
    """Top or bottom face of one grid cell: a square, optionally minus a circle."""
    bnd = cell_boundary(cx, cy)
    n = len(bnd)

    if dia is None:
        ctr = (cx, cy, z)
        for k in range(n):
            a = (bnd[k][0], bnd[k][1], z)
            b = (bnd[(k + 1) % n][0], bnd[(k + 1) % n][1], z)
            tris.append((ctr, a, b) if up else (ctr, b, a))
        return

    pts = ring(cx, cy, dia)
    off = (SEGMENTS // 4) // 2   # align arc 0 with the middle of the right edge
    for k in range(n):
        sa = (bnd[k][0], bnd[k][1], z)
        sb = (bnd[(k + 1) % n][0], bnd[(k + 1) % n][1], z)
        pa = pts[(k - off) % SEGMENTS]
        pb = pts[(k + 1 - off) % SEGMENTS]
        ca, cb = (pa[0], pa[1], z), (pb[0], pb[1], z)
        if up:
            quad(tris, sa, sb, cb, ca)
        else:
            quad(tris, ca, cb, sb, sa)


def build():
    tris = []
    for gy in range(NY):
        for gx in range(NX):
            cx, cy = (gx + 0.5) * CELL, (gy + 0.5) * CELL
            dia = HOLES.get((gx, gy))
            cell_face(tris, cx, cy, dia, THICK, up=True)
            cell_face(tris, cx, cy, dia, 0.0, up=False)
            if dia is not None:
                pts = ring(cx, cy, dia)
                for k in range(SEGMENTS):
                    p, q = pts[k], pts[(k + 1) % SEGMENTS]
                    # Normal must point INTO the hole -- material is outside it.
                    # Traversed p-up-over-down so each rim edge runs opposite to
                    # the face triangulation that shares it.
                    quad(tris,
                         (p[0], p[1], 0.0), (p[0], p[1], THICK),
                         (q[0], q[1], THICK), (q[0], q[1], 0.0))

    # Outer walls, subdivided at the SAME pitch as the cell boundaries
    # (CELL/per) so the rim vertices coincide with the edge cells' faces.
    step = CELL / (SEGMENTS // 4)
    perim = []
    x = 0.0
    while x < W - 1e-9:
        perim.append((x, 0.0)); x += step
    y = 0.0
    while y < H - 1e-9:
        perim.append((W, y)); y += step
    x = W
    while x > 1e-9:
        perim.append((x, H)); x -= step
    y = H
    while y > 1e-9:
        perim.append((0.0, y)); y -= step

    for k in range(len(perim)):
        x0, y0 = perim[k]
        x1, y1 = perim[(k + 1) % len(perim)]
        quad(tris, (x0, y0, 0.0), (x1, y1, 0.0),
                   (x1, y1, THICK), (x0, y0, THICK))
    return tris


def check_manifold(tris):
    """Every directed edge must appear exactly once, and its reverse exactly once.

    Passing this proves the mesh is closed AND consistently wound (a flipped
    face would duplicate its neighbour's edge direction). It does NOT prove the
    normals point outward rather than inward -- signed volume covers that.
    """
    key = lambda p: (round(p[0], 4), round(p[1], 4), round(p[2], 4))
    edges = Counter()
    for t in tris:
        for i in range(3):
            edges[(key(t[i]), key(t[(i + 1) % 3]))] += 1
    dup = sum(1 for c in edges.values() if c != 1)
    unmatched = sum(1 for (a, b) in edges if (b, a) not in edges)
    return dup, unmatched


def signed_volume(tris):
    """Divergence-theorem volume. Positive iff normals face outward."""
    total = 0.0
    for a, b, c in tris:
        total += (a[0] * (b[1] * c[2] - b[2] * c[1])
                  - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return total / 6.0


def expected_volume():
    """Plate minus the n-gon holes actually generated (not ideal circles)."""
    v = W * H * THICK
    for dia in HOLES.values():
        r = (dia / 2.0) / math.cos(math.pi / SEGMENTS)
        area = SEGMENTS * r * r * math.sin(2 * math.pi / SEGMENTS) / 2.0
        v -= area * THICK
    return v


def write_stl(tris, path):
    with open(path, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            nx_, ny_, nz_ = (uy * vz - uz * vy,
                             uz * vx - ux * vz,
                             ux * vy - uy * vx)
            m = math.sqrt(nx_ * nx_ + ny_ * ny_ + nz_ * nz_) or 1.0
            f.write(struct.pack("<12fH", nx_ / m, ny_ / m, nz_ / m,
                                *a, *b, *c, 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="cad/tolerance_coupon_v2.stl")
    args = ap.parse_args()

    tris = build()
    dup, unmatched = check_manifold(tris)
    vol, exp = signed_volume(tris), expected_volume()
    err = abs(vol - exp) / exp
    ok = dup == 0 and unmatched == 0 and vol > 0 and err < 1e-6

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # **Write only if the geometry passed, and exit non-zero if it did not.**
    # This used to write unconditionally and then print "OVERALL: FAIL" while
    # returning 0 -- so a non-manifold or inside-out mesh landed on disk as a
    # printable-looking STL, and any caller checking the exit code saw success.
    # Both failure modes are real history here: the first two builds of this
    # coupon failed manifold and then signed-volume (record Appendix I).
    # README.md calls this artifact "geometrically self-validated", which was
    # only true if a human read the output. (Cold audit finding 6, 2026-08-06.)
    if ok:
        write_stl(tris, out)

    print(f"plate      : {W:.1f} x {H:.1f} x {THICK:.1f} mm")
    print(f"triangles  : {len(tris)}")
    print(f"holes      : {len(HOLES)}")
    print(f"manifold   : duplicate-directed-edges={dup} unmatched-edges={unmatched}"
          f"  -> {'PASS' if dup == 0 and unmatched == 0 else 'FAIL'}")
    print(f"volume     : {vol:.3f} mm^3 (expected {exp:.3f}, rel.err {err:.2e})"
          f"  -> {'PASS' if vol > 0 and err < 1e-6 else 'FAIL'}")
    print(f"OVERALL    : {'PASS' if ok else 'FAIL'}")
    if ok:
        print(f"wrote      : {out}  ({out.stat().st_size} bytes)")
    else:
        print(f"NOT WRITTEN: {out} (geometry failed validation)")
        return 1
    print()
    print("pitch row  : 5 holes @ 8.00 mm centres, all "
          f"{PIN_REF:.2f} mm  (no markers)")
    pin = sorted(d for (x, y), d in HOLES.items() if y == 3 and d != MARKER)
    axle = sorted(d for (x, y), d in HOLES.items() if y == 5 and d != MARKER)
    print(f"pin row    : {', '.join(f'{d:.2f}' for d in pin)} mm  (1 marker hole)")
    print(f"axle row   : {', '.join(f'{d:.2f}' for d in axle)} mm  (2 marker holes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
