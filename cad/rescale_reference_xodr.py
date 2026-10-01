"""Rescale Evan's own working LaneMaker export (1122.xodr) to fit our floor,
touching ONLY dimensioned numeric values -- never structure.

**Why this exists (2026-09-07, Appendix EM).** Appendices EK/EL spent two
timeboxed attempts trying to DERIVE `cad/export_xodr.py`'s missing
`<junction><boundary>` block (the `side` attribute and the turn-connector
trim ratio) from `1122.xodr` and came up empty -- `side` does not follow any
simple positional rule, even between same-arm-count junctions inside that
one file. Evan's instruction that ends the derivation attempt: **the file
already works. Recreate it 1:1** -- i.e. stop trying to reverse-engineer the
boundary semantics and instead reuse the reference file's own topology
UNCHANGED, only rescaled to our project's physical size.

**What "1:1" means here, precisely.** Every junction, connection, laneLink,
boundary segment and its `side`/`type` stay BYTE-IDENTICAL in structure and
ORDER. Only dimensioned numeric quantities are scaled by one constant `k` so
the whole file's footprint fits our floor. This is a mechanical, documented
transform (OpenDRIVE's own geometry schema), not a guess: if `k` is applied
correctly everywhere a length/coordinate appears, the file describes the
exact same road network at a different physical size, and nothing that made
the original load and simulate is touched.

WHAT SCALES (all dimensioned quantities), and how:
  - <geometry s x y length>          all four *= k         (hdg UNCHANGED --
                                                              it's an angle)
  - <arc curvature>                  curvature /= k         (radius *= k)
  - <spiral curvStart curvEnd>       both /= k              (same reason)
  - <paramPoly3 aU..dV pRange=normalized>
                                      all 8 coefficients *= k
                                      (p is dimensionless in [0,1] under
                                      "normalized" range, so every physical
                                      offset coefficient scales uniformly --
                                      this file uses ONLY pRange=normalized,
                                      asserted below; "arcLength" range would
                                      need the s-polynomial rule instead and
                                      is refused rather than silently wrong)
  - <elevation s a b c d>            s *= k; a *= k; b unchanged;
  - <laneOffset s a b c d>           c /= k; d /= k^2
  - <width sOffset a b c d>          (a cubic in s has dimension length; s
                                      itself scales by k, so a and s share
                                      k, and each extra power of s in the
                                      denominator needs an extra 1/k)
  - <roadMark sOffset width>         both *= k
  - <road length>                    *= k
  - <segment sStart sEnd>            *= k        (boundary; a plain s-value,
                                                    not a polynomial coeff)
  - roadRunnerProfile <section type_s>
                                      *= k, EXCEPT the literal sentinel
                                      4294967295 (UINT32_MAX terminator,
                                      Appendix EA) which is never a distance
                                      and must pass through unchanged
  - offsetX2, every id/type/enum/contactPoint attribute
                                      UNCHANGED (offsetX2 is a ratio of two
                                      lengths, invariant under uniform scale;
                                      everything else here is not a length)

Usage:
  python cad/rescale_reference_xodr.py                # picks k automatically
  python cad/rescale_reference_xodr.py --scale 0.05    # explicit k
  python cad/rescale_reference_xodr.py --target 2.7    # target footprint (m)
  python cad/rescale_reference_xodr.py --self-check
"""

from __future__ import annotations

import argparse
import math
import xml.etree.ElementTree as ET
from pathlib import Path

# Vendored 2026-09-09. This used to be `Path.home() / "Downloads" / "1122.xodr"`,
# which made the whole script dead on any machine but Evan's: main() calls
# self_check() unconditionally and self_check() asserts REF.exists(), so a bare
# clone could not run it at all -- and Appendix EN's experiment could not be
# reproduced from the repo. The file is Evan's own LaneMaker export; it is now
# tracked at cad/reference/. See .claude/project-memory/track.md for the SHA256
# and provenance of both reference files.
REF = Path(__file__).with_name("reference") / "1122.xodr"
OUT = Path(__file__).with_name("track_1122_rescaled.xodr")

SENTINEL_TYPE_S = 4294967295  # UINT32_MAX terminator, never a distance


def estimate_footprint(root: ET.Element) -> tuple[float, float, float, float]:
    """Conservative bbox from every <geometry s x y hdg length>: start point
    plus a `length`-sized pad in every direction. Safe (never too small) --
    no arc/spiral/paramPoly3 curve evaluation needed, because no geometry
    can extend farther from its own start than its own length.
    """
    xs, ys = [], []
    for g in root.iter("geometry"):
        x = float(g.get("x")); y = float(g.get("y")); length = float(g.get("length"))
        xs += [x - length, x + length]
        ys += [y - length, y + length]
    return min(xs), max(xs), min(ys), max(ys)


def _scale_attr(el: ET.Element, name: str, k: float) -> None:
    v = el.get(name)
    if v is not None:
        el.set(name, repr(float(v) * k))


def _scale_poly_coeffs(el: ET.Element, k: float, prefix: str = "") -> None:
    """a/b/c/d (or aU/bU/cU/dU + aV/bV/cV/dV) of a cubic-in-s polynomial
    whose OUTPUT has dimension length: a*=k, b unchanged, c/=k, d/=k**2.
    """
    for letter, factor in (("a", k), ("b", 1.0), ("c", 1.0 / k), ("d", 1.0 / (k * k))):
        name = prefix + letter
        v = el.get(name)
        if v is not None:
            el.set(name, repr(float(v) * factor))


def rescale(root: ET.Element, k: float) -> None:
    for g in root.iter("geometry"):
        for attr in ("s", "x", "y", "length"):
            _scale_attr(g, attr, k)
        # hdg is an angle -- NEVER scaled.

    for a in root.iter("arc"):
        _scale_attr(a, "curvature", 1.0 / k)

    for sp in root.iter("spiral"):
        _scale_attr(sp, "curvStart", 1.0 / k)
        _scale_attr(sp, "curvEnd", 1.0 / k)

    for pp in root.iter("paramPoly3"):
        assert pp.get("pRange", "normalized") == "normalized", (
            "this file was assumed pRange=normalized everywhere -- found "
            "arcLength, which needs the s-polynomial rule instead, not the "
            "uniform-coefficient one. Refusing rather than silently "
            "mis-scaling.")
        for letter in ("aU", "bU", "cU", "dU", "aV", "bV", "cV", "dV"):
            _scale_attr(pp, letter, k)

    for el in root.iter("elevation"):
        _scale_attr(el, "s", k)
        _scale_poly_coeffs(el, k)

    for lo in root.iter("laneOffset"):
        _scale_attr(lo, "s", k)
        _scale_poly_coeffs(lo, k)

    for w in root.iter("width"):
        _scale_attr(w, "sOffset", k)
        _scale_poly_coeffs(w, k)

    for rm in root.iter("roadMark"):
        _scale_attr(rm, "sOffset", k)
        _scale_attr(rm, "width", k)

    for ls in root.iter("laneSection"):
        _scale_attr(ls, "s", k)

    # ROAD OBJECTS -- the turn arrows and stopping lines. Missed on the first
    # cut (2026-09-07), and the symptom named the bug: at k=0.5 the arrows
    # rendered OFF TO THE SIDE of the road, because `t` (lateral offset from
    # the reference line, +/-3.25 = one lane width) stayed at full size while
    # the lane it belongs on halved. `s` past a shortened road's end and a
    # 2 m-wide arrow glyph on a 1.625 m lane are the same defect.
    for ob in root.iter("object"):
        for attr in ("s", "t", "zOffset", "length", "width", "height",
                     "radius", "validLength"):
            _scale_attr(ob, attr, k)
        # hdg / pitch / roll / orientation are angles -- NEVER scaled.

    for r in root.iter("road"):
        _scale_attr(r, "length", k)

    for seg in root.iter("segment"):
        _scale_attr(seg, "sStart", k)
        _scale_attr(seg, "sEnd", k)

    for sec in root.iter("section"):
        v = sec.get("type_s")
        if v is not None and int(float(v)) != SENTINEL_TYPE_S:
            sec.set("type_s", repr(float(v) * k))
        # offsetX2 untouched -- a ratio, invariant under uniform scale.


# EVERY (tag, attribute) pair this file format can carry, and what it is.
# The completeness guard below refuses to run on a file containing a pair
# that is not listed here -- because the ONE defect this script has had was
# an unlisted element passing through unscaled (`<object>` and
# `<laneSection s>`, 2026-09-07: the arrows rendered off to the side of the
# road because `t` kept its full-size lateral offset on a halved lane).
# Silence is the failure mode, so an unknown attribute must be loud.
ATTR_CLASS: dict[tuple[str, str], str] = {}
for _tag, _attrs, _cls in (
    ("arc", ("curvature",), "inverse"),
    ("elevation", ("s",), "length"),
    ("elevation", ("a", "b", "c", "d"), "poly"),
    ("geometry", ("length", "s", "x", "y"), "length"),
    ("geometry", ("hdg",), "angle"),
    ("laneOffset", ("s",), "length"),
    ("laneOffset", ("a", "b", "c", "d"), "poly"),
    ("laneSection", ("s",), "length"),
    ("object", ("s", "t", "zOffset", "length", "width", "height", "radius",
                "validLength"), "length"),
    ("object", ("hdg", "pitch", "roll", "orientation"), "angle"),
    ("object", ("dynamic", "id", "name", "subtype", "type"), "opaque"),
    ("paramPoly3", ("aU", "aV", "bU", "bV", "cU", "cV", "dU", "dV"), "length"),
    ("paramPoly3", ("pRange",), "opaque"),
    ("road", ("length",), "length"),
    ("road", ("id", "junction", "name"), "opaque"),
    ("roadMark", ("sOffset", "width"), "length"),
    ("roadMark", ("color", "laneChange", "type", "weight"), "opaque"),
    ("section", ("type_s",), "length"),
    ("section", ("laneCount", "offsetX2"), "opaque"),
    ("segment", ("sEnd", "sStart"), "length"),
    ("segment", ("roadID", "side", "type"), "opaque"),
    ("spiral", ("curvEnd", "curvStart"), "inverse"),
    ("width", ("sOffset",), "length"),
    ("width", ("a", "b", "c", "d"), "poly"),
    ("connection", ("connectingRoad", "contactPoint", "id", "incomingRoad"), "opaque"),
    ("header", ("revMajor", "revMinor"), "opaque"),
    ("junction", ("id", "name"), "opaque"),
    ("lane", ("id", "level", "type"), "opaque"),
    ("laneLink", ("from", "to"), "opaque"),
    ("predecessor", ("contactPoint", "elementId", "elementType", "id"), "opaque"),
    ("successor", ("contactPoint", "elementId", "elementType", "id"), "opaque"),
    ("signalPhase", ("id",), "opaque"),
):
    for _a in _attrs:
        ATTR_CLASS[(_tag, _a)] = _cls


def check_coverage(root: ET.Element) -> None:
    """Refuse to scale a file carrying an attribute we have not classified."""
    unknown = set()
    for el in root.iter():
        for a in el.keys():
            if (el.tag, a) not in ATTR_CLASS:
                unknown.add((el.tag, a))
    if unknown:
        raise SystemExit(
            "UNCLASSIFIED attributes -- refusing to scale, because an "
            "unhandled length passes through silently and lands as a "
            "misplaced feature, not an error:\n  " +
            "\n  ".join(f"<{t} {a}=...>" for t, a in sorted(unknown)))


def self_check() -> None:
    assert REF.exists(), f"reference file not found: {REF}"
    tree = ET.parse(REF)
    root = tree.getroot()
    check_coverage(root)
    x0, x1, y0, y1 = estimate_footprint(root)
    span_before = max(x1 - x0, y1 - y0)
    # every 'length'-class value in the file, before scaling
    def _lengths(r):
        out = []
        for el in r.iter():
            for a in el.keys():
                if ATTR_CLASS.get((el.tag, a)) == "length":
                    v = float(el.get(a))
                    if el.tag == "section" and int(v) == SENTINEL_TYPE_S:
                        continue
                    out.append(v)
        return out
    before = _lengths(root)
    k = 0.1
    rescale(root, k)
    after = _lengths(root)
    x0b, x1b, y0b, y1b = estimate_footprint(root)
    span_after = max(x1b - x0b, y1b - y0b)
    assert abs(span_after - span_before * k) < 1e-6 * span_before, (
        f"footprint did not scale linearly: before {span_before:.4f}, "
        f"after {span_after:.4f}, expected {span_before*k:.4f}")
    # EVERY length-class value must have moved by exactly k -- this is the
    # check that fails if a new element is added and left out of rescale().
    assert len(before) == len(after), "attribute count changed during scaling"
    bad = [(b, a) for b, a in zip(before, after)
           if abs(b) > 1e-12 and abs(a - b * k) > 1e-9 * abs(b)]
    assert not bad, f"{len(bad)} length-class values did not scale by k: {bad[:3]}"
    print(f"self_check: PASS (footprint {span_before:.3f} m -> "
          f"{span_after:.3f} m at k={k}; {len(before)} length-class values "
          f"all scaled, {sum(1 for _ in root.iter('road'))} roads)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=None,
                    help="explicit scale factor k (overrides --target)")
    ap.add_argument("--target", type=float, default=2.7,
                    help="target footprint in metres (default 2.7, our "
                         "project's model-scale convention)")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0
    self_check()

    if not REF.exists():
        raise SystemExit(f"reference file not found: {REF}")
    tree = ET.parse(REF)
    root = tree.getroot()

    x0, x1, y0, y1 = estimate_footprint(root)
    span = max(x1 - x0, y1 - y0)
    k = args.scale if args.scale is not None else args.target / span

    n_roads = sum(1 for _ in root.iter("road"))
    n_junctions = sum(1 for _ in root.iter("junction"))
    n_boundaries = sum(1 for _ in root.iter("boundary"))
    total_len_before = sum(float(r.get("length")) for r in root.iter("road"))

    rescale(root, k)

    total_len_after = sum(float(r.get("length")) for r in root.iter("road"))
    x0b, x1b, y0b, y1b = estimate_footprint(root)
    span_after = max(x1b - x0b, y1b - y0b)

    ET.indent(tree, space="\t")
    out = Path(args.out)
    out.write_bytes(b'<?xml version="1.0" standalone="yes"?>\n' +
                    ET.tostring(root, encoding="utf-8"))

    print("=" * 74)
    print("RESCALED COPY OF 1122.xodr -- SAME TOPOLOGY, DIFFERENT SIZE")
    print("=" * 74)
    print(f"reference       {REF}")
    print(f"scale factor k  {k:.6f}  ({'explicit' if args.scale is not None else f'target {args.target} m'})")
    print(f"roads           {n_roads}  (unchanged count)")
    print(f"junctions       {n_junctions}  (unchanged count)")
    print(f"boundary blocks {n_boundaries}  (unchanged count, side/type/order untouched)")
    print(f"footprint (est) {span:.3f} m -> {span_after:.3f} m")
    print(f"total road len  {total_len_before:.3f} m -> {total_len_after:.3f} m")
    print()
    print("NOT a claim this matches our own 3x3 figure-8 track shape -- it")
    print("is Evan's own test map, resized. Structure (junctions, connections,")
    print("boundary, side) is byte-identical to the file that already loads")
    print("and simulates; only lengths/coordinates/widths changed. If this")
    print("crashes, the cause is size-dependent (unlikely for a format this")
    print("literal) rather than the boundary/side semantics EK/EL could not")
    print("derive.")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
