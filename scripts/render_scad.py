#!/usr/bin/env python
"""Render an OpenSCAD file to a CANONICAL binary STL, validated before it is written.

Stdlib + numpy only. Same discipline as gen_servo_lego_coupler.py: the mesh is
checked closed and consistently wound, probed at the places the design says
there is a hole or a wall, and NOTHING is written if any check fails.

WHY CANONICAL (2026-10-11)
--------------------------
scripts/check_artifacts.py regenerates every registered artifact and
byte-compares it with the committed file. OpenSCAD's own STL cannot take part
in that: it is ASCII text, in OpenSCAD's internal facet order and number
formatting, and neither of those is part of the geometry. So the render is
re-emitted in a form that depends on the geometry and on nothing else:

  - coordinates rounded to float32, negative zero removed
  - each triangle's vertices rotated (orientation kept) so its
    lexicographically smallest vertex comes first
  - triangles sorted lexicographically by their nine coordinates
  - normals recomputed from the vertices, fixed 80-byte header

Two renders of the same geometry are then byte-identical (self_check (e)).
Measured 2026-10-11 on the PLA coupon: two raw OpenSCAD renders of one file
were NOT byte-identical (4114 of 7880 facets differed in order or vertex
rotation); their canonical forms were.
The triangulation itself is NOT canonicalised: if OpenSCAD ever splits a face
along a different diagonal the bytes change and check_artifacts reports drift.
That is the right outcome; regenerate and re-inspect.

WHAT IT CHECKS (every failure is named; any failure writes nothing)
-------------------------------------------------------------------
  1. OpenSCAD exits 0 and prints no line starting WARNING: or ERROR:. A warning
     means the SCAD did not do what it says, so it is never ignored. It also
     gets 900 s: after that its whole process tree is killed and the run FAILs
     rather than hangs.
  2. Manifold: every directed edge occurs once and its reverse exists
     (vertices keyed at 5 decimals), and the signed volume is positive.
  3. With a probe file (below): the bounding box, every hole, every open point
     and every solid point.

PROBE FILE: the SCAD path with .scad replaced by .probe.json, or --probe PATH
  {"bbox": [[xmin,ymin,zmin],[xmax,ymax,zmax]],      equal within 0.01 mm
   "holes": [{"name": str, "center": [x,y,z], "axis": "x"|"y"|"z",
              "d": float, "ring": true}, ...],
   "open_points":  [[x,y,z], ...],                   must be empty space
   "solid_points": [[x,y,z], ...]}                   must be inside material
  A hole is probed at its centre and at 4 points d/2 - 0.05 from its axis (all
  must be open); with "ring": true also at 4 points d/2 + 0.30 from its axis
  (all must be solid). "Inside" is a ray-parity test: 3 skewed rays, majority
  vote. Every key is optional.

WHAT PASSING PROVES, AND WHAT IT DOES NOT
-----------------------------------------
It proves the mesh is a closed solid with the extents and holes the SCAD means
to have, at the probed points. It says nothing about how the part prints or
fits: that is measured on the printed part, never inferred here. --png writes
an OpenSCAD PREVIEW (ghost_box stand-ins visible), which is not the validated
mesh.

Usage:  python scripts/render_scad.py SCAD -o OUT.stl [--probe P.json]
                                      [-D NAME=VALUE ...] [--png PREVIEW.png]
Exit:   0 written (and the PNG made, if asked)
        1 render or validation failed (an OpenSCAD timeout counts) and NOTHING
          was written, or the PNG failed after a validated STL had already
          been written
OpenSCAD is found via $OPENSCAD, then ~/tools/openscad-2021.01, then PATH.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

# ---- tunables (mm unless noted) ---------------------------------------------
HEADER = b"render_scad.py canonical STL"
OPENSCAD_TIMEOUT = 900   # s, per OpenSCAD run; the PLA coupon takes ~25-40 s
KEY_SCALE = 1e5      # manifold check keys vertices at 5 decimals
BBOX_TOL = 0.01      # bbox must equal the probe's within this, per axis
BORE_MARGIN = 0.05   # hole-interior probes sit this far inside d/2
RING_MARGIN = 0.30   # hole-wall probes sit this far outside d/2
HIT_EPS = 1e-9       # ray hits at t <= this are the origin's own surface
# Skewed rays: an axis-aligned ray runs along coplanar faces and shared edges
# of a CAD mesh. Inside = at least two of the three see an odd hit count.
RAY_DIRS = ((1.0, 0.0013, 0.0017), (0.0011, 1.0, 0.0019), (0.0016, 0.0012, 1.0))
# In-plane unit vectors of a hole whose axis is x / y / z.
PLANE = {"x": ((0, 1, 0), (0, 0, 1)),
         "y": ((1, 0, 0), (0, 0, 1)),
         "z": ((1, 0, 0), (0, 1, 0))}
# One binary-STL facet: normal, 3 vertices, attribute word. Little-endian.
FACET = np.dtype([("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("a", "<u2")])
assert FACET.itemsize == 50


def find_openscad() -> Path:
    """OpenSCAD's console binary: $OPENSCAD, then ~/tools/openscad-2021.01, then PATH."""
    env = os.environ.get("OPENSCAD")
    if env and Path(env).exists():
        return Path(env)
    local = Path.home() / "tools" / "openscad-2021.01" / "openscad.com"
    if local.exists():
        return local
    found = shutil.which("openscad")
    if found:
        return Path(found)
    raise FileNotFoundError("OpenSCAD not found: set OPENSCAD or install to ~/tools/openscad-2021.01")


def parse_stl(data: bytes) -> np.ndarray:
    """ASCII or binary STL bytes -> float64 triangles, shape (n, 3, 3).

    Coordinates go through float32 and back (the precision the output file
    keeps) and `+ 0.0` turns -0.0 into 0.0, so the canonical form is exact.
    """
    n = struct.unpack_from("<I", data, 80)[0] if len(data) >= 84 else -1
    if len(data) == 84 + 50 * n:
        verts = np.frombuffer(data, dtype=FACET, count=n, offset=84)["v"].astype(np.float64)
    else:
        rows = [[float(w) for w in ln.split()[1:4]]
                for ln in data.decode("ascii", errors="replace").splitlines()
                if ln.split()[:1] == ["vertex"]]
        if len(rows) % 3:
            raise RuntimeError(f"STL has {len(rows)} vertex lines, not a multiple of 3")
        verts = np.array(rows, dtype=np.float64).reshape(-1, 3, 3)
    if len(verts) == 0:
        raise RuntimeError("OpenSCAD wrote an STL with no triangles")
    return verts.astype(np.float32).astype(np.float64) + 0.0


def _run_openscad(cmd: list[str], scad: Path,
                  timeout: float = OPENSCAD_TIMEOUT) -> subprocess.CompletedProcess:
    """Run one OpenSCAD command, capturing its text output, under a hard time limit.

    On expiry the whole process tree is killed and RuntimeError is raised, so a
    hung render is a reported FAIL, never a hang. subprocess.run(timeout=...)
    is not enough on Windows: openscad.com is a launcher whose child does the
    work and keeps the output pipes open, so run() kept waiting until OpenSCAD
    finished by itself (measured 2026-10-11: timeout=5 returned after 23.6 s).
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace")
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        if os.name == "nt":                     # /T = the whole tree, /F = force
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True)
        proc.kill()
        proc.wait()                             # not communicate(): a stray child may still hold the pipes
        raise RuntimeError(f"OpenSCAD timed out after {timeout:g} s: {scad}") from None
    return subprocess.CompletedProcess(cmd, proc.returncode, out, err)


def render(scad: Path, defines: list[str]) -> np.ndarray:
    """Run OpenSCAD on `scad`; return its triangles, shape (n, 3, 3).

    A non-zero exit, a timeout, or any stdout/stderr line starting WARNING: or
    ERROR: raises RuntimeError carrying OpenSCAD's own words.
    """
    exe = find_openscad()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "render.stl"
        cmd = [str(exe), "-o", str(tmp)]
        for d in defines:
            cmd += ["-D", d]
        cmd.append(str(scad))
        proc = _run_openscad(cmd, scad)
        lines = (proc.stdout + "\n" + proc.stderr).splitlines()
        bad = [ln for ln in lines if ln.startswith(("WARNING:", "ERROR:"))]
        if proc.returncode != 0 or bad:
            said = bad or [ln for ln in lines if ln.strip()][-10:]
            raise RuntimeError(f"OpenSCAD problem on {scad} (exit {proc.returncode}): "
                               + " | ".join(said))
        if not tmp.exists():
            raise RuntimeError(f"OpenSCAD exited 0 but wrote no STL for {scad}")
        return parse_stl(tmp.read_bytes())


def _lex_less(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Row-wise a < b, lexicographic over the last axis (length 3)."""
    lt, eq = a < b, a == b
    return lt[:, 0] | (eq[:, 0] & lt[:, 1]) | (eq[:, 0] & eq[:, 1] & lt[:, 2])


def canonical(tris: np.ndarray) -> np.ndarray:
    """Geometry-only ordering: rotate each triangle so its smallest vertex is
    first (orientation kept), then sort the triangles by their 9 coordinates."""
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    first = np.zeros(len(tris), dtype=np.int64)
    best = v0.copy()
    for k, v in ((1, v1), (2, v2)):
        less = _lex_less(v, best)
        first = np.where(less, k, first)
        best = np.where(less[:, None], v, best)
    idx = (first[:, None] + np.arange(3)[None, :]) % 3
    rolled = np.take_along_axis(tris, np.broadcast_to(idx[:, :, None], tris.shape), axis=1)
    flat = rolled.reshape(len(tris), 9)
    return rolled[np.lexsort(flat.T[::-1])]     # lexsort: LAST key is primary


def check_manifold(tris: np.ndarray) -> tuple[int, int]:
    """(dup, unmatched): directed edges used != once, and directed edges whose
    reverse is absent. Both 0 for a closed, consistently wound mesh. Vertices
    are keyed at 5 decimals, as in gen_servo_lego_coupler.py."""
    keys = np.rint(tris.reshape(-1, 3) * KEY_SCALE).astype(np.int64)
    _, vid = np.unique(keys, axis=0, return_inverse=True)
    vid = vid.reshape(-1).astype(np.int64).reshape(len(tris), 3)
    nv = int(vid.max()) + 1
    src = vid.reshape(-1)
    dst = np.roll(vid, -1, axis=1).reshape(-1)
    uniq, counts = np.unique(src * nv + dst, return_counts=True)
    dup = int(np.count_nonzero(counts != 1))
    rev = (uniq % nv) * nv + uniq // nv
    unmatched = int(np.count_nonzero(~np.isin(rev, uniq)))
    return dup, unmatched


def signed_volume(tris: np.ndarray) -> float:
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def inside(tris: np.ndarray, point) -> bool:
    """Is `point` inside the solid? Moller-Trumbore ray parity, vectorised over
    every triangle, 3 skewed rays, majority vote."""
    p = np.asarray(point, dtype=np.float64)
    v0 = tris[:, 0]
    e1, e2 = tris[:, 1] - v0, tris[:, 2] - v0
    t_vec = p - v0
    q_vec = np.cross(t_vec, e1)
    odd = 0
    for d in RAY_DIRS:
        d = np.asarray(d, dtype=np.float64)
        d = d / np.linalg.norm(d)
        p_vec = np.cross(d, e2)
        det = np.einsum("ij,ij->i", e1, p_vec)
        ok = np.abs(det) > 1e-12                      # else parallel to the ray
        inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
        u = np.einsum("ij,ij->i", t_vec, p_vec) * inv
        v = (q_vec @ d) * inv
        t = np.einsum("ij,ij->i", e2, q_vec) * inv
        # shortcut: edge and vertex hits count on both triangles (inclusive
        # bounds), so a ray through a shared edge counts twice. The skewed rays
        # make that vanishingly unlikely for these probes; upgrade to a
        # watertight test if a probe ever flakes.
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > HIT_EPS)
        odd += int(np.count_nonzero(hit)) % 2
    return odd >= 2


def probe_checks(probe: dict) -> list[tuple[str, str, tuple, bool]]:
    """Every point test a probe asks for: (label, kind, (x, y, z), expect_solid)."""
    checks = []
    for h in probe.get("holes", []):
        label = f"hole {h['name']}"
        r = float(h["d"]) / 2
        c = np.asarray(h["center"], dtype=np.float64)
        u, w = (np.asarray(v, dtype=np.float64) for v in PLANE[h["axis"]])
        checks.append((label, "center", tuple(c), False))
        for s in (u, w, -u, -w):
            checks.append((label, "bore", tuple(c + (r - BORE_MARGIN) * s), False))
        if h.get("ring"):
            for s in (u, w, -u, -w):
                checks.append((label, "ring", tuple(c + (r + RING_MARGIN) * s), True))
    for i, pt in enumerate(probe.get("open_points", [])):
        checks.append((f"open_points[{i}]", "", tuple(pt), False))
    for i, pt in enumerate(probe.get("solid_points", [])):
        checks.append((f"solid_points[{i}]", "", tuple(pt), True))
    return checks


def bbox_failures(tris: np.ndarray, probe: dict) -> list[str]:
    want = probe.get("bbox")
    if want is None:
        return []
    pts = tris.reshape(-1, 3)
    got = (pts.min(axis=0), pts.max(axis=0))
    fails = []
    for side, name in ((0, "min"), (1, "max")):
        for ax, axname in enumerate("xyz"):
            if abs(got[side][ax] - want[side][ax]) > BBOX_TOL:
                fails.append(f"bbox {name} {axname}: mesh {got[side][ax]:.3f} "
                             f"vs probe {want[side][ax]:g} (tolerance {BBOX_TOL} mm)")
    return fails


def validate(tris: np.ndarray, probe: dict | None) -> list[str]:
    """Failure strings; an empty list means every check passed."""
    fails = []
    dup, unmatched = check_manifold(tris)
    if dup or unmatched:
        fails.append(f"mesh is not a closed manifold: duplicate-directed-edges={dup} "
                     f"unmatched-edges={unmatched}")
    vol = signed_volume(tris)
    if not vol > 0:
        fails.append(f"signed volume {vol:.4f} mm^3 is not positive")
    if probe is not None:
        fails += bbox_failures(tris, probe)
        for label, kind, pt, solid in probe_checks(probe):
            if inside(tris, pt) != solid:
                x, y, z = pt
                note = ", ".join(s for s in (kind, "expected solid" if solid else "expected open") if s)
                fails.append(f"{label}: point ({x:g}, {y:g}, {z:g}) is "
                             f"{'open' if solid else 'solid'} ({note})")
    return fails


def write_binary_stl(tris: np.ndarray, path) -> None:
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    cross = np.cross(b - a, c - a)
    norm = np.sqrt(np.einsum("ij,ij->i", cross, cross))
    good = norm > 0
    normal = np.zeros_like(cross)
    normal[good] = cross[good] / norm[good][:, None]       # degenerate -> 0 vector
    rec = np.zeros(len(tris), dtype=FACET)
    rec["n"] = normal
    rec["v"] = tris
    with open(path, "wb") as f:
        f.write(HEADER.ljust(80, b"\0"))
        f.write(struct.pack("<I", len(tris)))
        f.write(rec.tobytes())


def render_png(scad: Path, defines: list[str], png: Path) -> None:
    """OpenSCAD PREVIEW image (the % ghost_box stand-ins are drawn in it)."""
    png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(find_openscad()), "--preview", "--viewall", "--autocenter",
           "--imgsize=1600,1200", "--colorscheme=Tomorrow", "-o", str(png)]
    for d in defines:
        cmd += ["-D", d]
    cmd.append(str(scad))
    proc = _run_openscad(cmd, scad)
    if proc.returncode != 0 or not png.exists():
        tail = [ln for ln in (proc.stdout + "\n" + proc.stderr).splitlines() if ln.strip()][-6:]
        raise RuntimeError(f"OpenSCAD PNG preview failed (exit {proc.returncode}): " + " | ".join(tail))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scad", type=Path, help="OpenSCAD source file")
    ap.add_argument("-o", "--out", type=Path, required=True, help="canonical binary STL to write")
    ap.add_argument("--probe", type=Path, default=None,
                    help="probe JSON (default: SCAD with .scad -> .probe.json, if it exists)")
    ap.add_argument("-D", dest="defines", action="append", default=[], metavar="NAME=VALUE",
                    help="passed to OpenSCAD as -D NAME=VALUE (repeatable)")
    ap.add_argument("--png", type=Path, default=None,
                    help="also write an OpenSCAD preview image after a successful STL")
    args = ap.parse_args(argv)

    if not args.scad.exists():
        ap.error(f"no such SCAD file: {args.scad}")
    probe_path = args.probe
    if probe_path is None:
        guess = args.scad.with_suffix(".probe.json")
        probe_path = guess if guess.exists() else None
    elif not probe_path.exists():
        ap.error(f"no such probe file: {probe_path}")
    probe = json.loads(probe_path.read_text(encoding="utf-8")) if probe_path else None

    out = args.out
    print(f"scad       : {args.scad}")
    try:
        tris = canonical(render(args.scad, args.defines))
    except (FileNotFoundError, RuntimeError) as e:
        print(f"render     : FAIL  {e}")
        print("OVERALL    : FAIL")
        print(f"NOT WRITTEN: {out}")
        print(f"render_scad: FAIL: {e}", file=sys.stderr)
        return 1

    dup, unmatched = check_manifold(tris)
    vol = signed_volume(tris)
    pts = tris.reshape(-1, 3)
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    print(f"triangles  : {len(tris)}")
    print(f"manifold   : duplicate-directed-edges={dup} unmatched-edges={unmatched}"
          f"  -> {'PASS' if dup == 0 and unmatched == 0 else 'FAIL'}")
    print(f"volume     : {vol:.4f} mm^3  -> {'PASS' if vol > 0 else 'FAIL'}")
    bbox_note = "not checked (no probe)"
    if probe is not None and probe.get("bbox") is not None:
        bbox_note = "PASS" if not bbox_failures(tris, probe) else "FAIL"
    print(f"bbox       : ({lo[0]:.3f}, {lo[1]:.3f}, {lo[2]:.3f}) .. "
          f"({hi[0]:.3f}, {hi[1]:.3f}, {hi[2]:.3f}) mm  -> {bbox_note}")
    print(f"probe : {probe_path if probe_path else 'none'}")

    fails = validate(tris, probe)
    if fails:
        for f in fails:
            print(f"FAIL       : {f}")
        print("OVERALL    : FAIL")
        print(f"NOT WRITTEN: {out}")
        print(f"render_scad: FAIL: {len(fails)} check(s) failed, first: {fails[0]}", file=sys.stderr)
        return 1

    if probe is not None:
        n = len(probe_checks(probe))
        print(f"probes : {n}/{n} PASS")
    out.parent.mkdir(parents=True, exist_ok=True)
    write_binary_stl(tris, out)                 # only ever reached with a clean mesh
    print("OVERALL    : PASS")
    print(f"wrote      : {out}  ({out.stat().st_size} bytes)")

    if args.png:
        try:
            render_png(args.scad, args.defines, args.png)
        except (FileNotFoundError, RuntimeError) as e:
            print(f"png        : FAIL  {e}")
            return 1
        print(f"png        : {args.png}  ({args.png.stat().st_size} bytes, OpenSCAD preview)")
    return 0


def self_check():
    """Plant bugs against a small rendered block and prove each one is caught."""
    find_openscad()               # FileNotFoundError here => run_checks reports SKIP
    lego = (REPO / "cad" / "scad" / "lib" / "lego.scad").as_posix()
    src = (f"use <{lego}>\n"
           "difference() {\n"
           "  cube([16, 8, 7.8]);\n"
           "  translate([4, 4, 0]) technic_hole(d=4.8, h=7.8);\n"
           "  translate([12, 4, 0]) technic_hole(d=4.8, h=7.8);\n"
           "}\n")
    good = {"bbox": [[0, 0, 0], [16, 8, 7.8]],
            "holes": [{"name": "T1", "center": [4, 4, 3.9], "axis": "z", "d": 4.8, "ring": True},
                      {"name": "T2", "center": [12, 4, 3.9], "axis": "z", "d": 4.8, "ring": True}]}
    with tempfile.TemporaryDirectory() as td:
        scad = Path(td) / "selfcheck.scad"
        scad.write_bytes(src.encode("utf-8"))
        first = canonical(render(scad, []))
        second = canonical(render(scad, []))

        fails = validate(first, good)
        assert not fails, f"(a) the correct probe must pass, got {fails}"
        print(f"self_check (a) correct probe passes on the rendered block ({len(first)} triangles): ok")

        moved = json.loads(json.dumps(good))
        moved["holes"][0]["center"] = [5, 4, 3.9]
        fails = validate(first, moved)
        assert fails, "(b) a hole moved 1 mm was NOT caught"
        print(f"self_check (b) hole moved 1 mm is caught ({len(fails)} failures): ok")

        fails = validate(first, dict(good, solid_points=[[4, 4, 3.9]]))
        assert fails, "(c) a solid_point inside a hole was NOT caught"
        print(f"self_check (c) solid_point placed in a hole is caught ({len(fails)} failures): ok")

        fails = validate(first, dict(good, bbox=[[0, 0, 0], [16.5, 8, 7.8]]))
        assert fails, "(d) a bbox wrong by 0.5 mm was NOT caught"
        print(f"self_check (d) bbox max x 16.5 vs 16.0 is caught ({len(fails)} failures): ok")

        p1, p2 = Path(td) / "one.stl", Path(td) / "two.stl"
        write_binary_stl(first, p1)
        write_binary_stl(second, p2)
        assert p1.read_bytes() == p2.read_bytes(), "(e) two renders gave different canonical bytes"
        print(f"self_check (e) two renders are byte-identical ({p1.stat().st_size} bytes): ok")

    # (f) A hung OpenSCAD must come back as a FAIL in bounded time even when a
    # grandchild keeps the output pipes open (the openscad.com launcher case).
    hang = [sys.executable, "-c",
            "import subprocess, sys, time\n"
            "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
            "time.sleep(60)\n"]
    t0 = time.monotonic()
    try:
        _run_openscad(hang, Path("hang.scad"), timeout=1)
    except RuntimeError as e:
        assert "timed out after 1 s: hang.scad" in str(e), f"(f) wrong timeout message: {e}"
    else:
        raise AssertionError("(f) a 60 s command with a 1 s timeout was not stopped")
    took = time.monotonic() - t0
    assert took < 20, f"(f) the timeout took {took:.1f} s: a grandchild held the pipes open"
    print(f"self_check (f) hung command plus a grandchild is killed and reported FAIL in {took:.1f} s: ok")


if __name__ == "__main__":
    sys.exit(main())
