#!/usr/bin/env python
"""Prove every committed generated artifact still matches its generator.

WHY THIS EXISTS (2026-09-09, daily-audit Appendix ES finding 1/2)
----------------------------------------------------------------
Every generator in this repo defaults its --out INTO a tracked path, so an
artifact is correct only if a human remembers to regenerate it, and nothing
ever checked. Two files had silently drifted for days:

  cad/track_grid3x3_junctions.xodr   0 <signalPhase> committed, 68 generated
  cad/track_1122_rescaled.xodr       31 <object> elements at unscaled values

The docs then described files that were not on disk. Appendix ER even claimed
the default export was "byte-identical", which was false.

This is the ROOT fix the audit asked for: ONE registry, not a --check flag
bolted onto each of five generators. Regenerate into a temp dir, diff, report.

USAGE
  python scripts/check_artifacts.py            # every registered artifact
  python scripts/check_artifacts.py --staged   # only what THIS commit stages
  python scripts/check_artifacts.py --list     # registry, no regeneration

EXIT CODES
  0  every artifact that could be checked is byte-identical to a fresh run
  1  at least one artifact has DRIFTED, or a generator failed to run

UNCHECKABLE artifacts are printed with their reason and do NOT fail the run --
but they are never silently skipped, because a silent skip is how this class of
bug survives. See the UNCHECKABLE list at the bottom of ARTIFACTS.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = REPO / ".venv" / "Scripts" / "python.exe"
if not PY.exists():                      # POSIX clone, or a venv-less runner
    PY = Path(sys.executable)

# --------------------------------------------------------------------------
# THE REGISTRY
#
# kind="file": cmd writes ONE file; {out} is a temp FILE path.
# kind="dir" : cmd writes into a DIRECTORY; {out} is a temp DIR, and `files`
#              lists the basenames it drops there. This exists because
#              track_layout_*.py and export_xodr.py --probe emit several
#              artifacts per run and take a directory, not a file.
# kind="uncheckable": cannot be regenerated here. `reason` is mandatory and is
#              always printed -- an artifact nobody can verify is a standing
#              risk, and hiding it is the failure mode this script prevents.
# --------------------------------------------------------------------------
ARTIFACTS = [
    # --- cad/export_xodr.py: one generator, five flag combinations ----------
    dict(kind="file", artifact="cad/track_figure8.xodr",
         cmd=["cad/export_xodr.py", "--out", "{out}"]),
    dict(kind="file", artifact="cad/track_figure8_model.xodr",
         cmd=["cad/export_xodr.py", "--model-scale", "--out", "{out}"]),
    dict(kind="file", artifact="cad/track_grid3x3.xodr",
         cmd=["cad/export_xodr.py", "--grid", "--out", "{out}"]),
    dict(kind="file", artifact="cad/track_grid3x3_model.xodr",
         cmd=["cad/export_xodr.py", "--grid", "--model-scale", "--out", "{out}"]),
    dict(kind="file", artifact="cad/track_grid3x3_junctions.xodr",
         cmd=["cad/export_xodr.py", "--junctions", "--out", "{out}"]),
    dict(kind="file", artifact="cad/track_grid3x3_junctions_model.xodr",
         cmd=["cad/export_xodr.py", "--junctions", "--model-scale", "--out", "{out}"]),
    # NOT a plain --boundary run. The filename cascade at export_xodr.py:990
    # puts "_bnd" first, so this file is the COMBINED Appendix EQ/ER experiment:
    # boundary + LaneMaker lane convention + 5 m roads. Recovered 2026-09-09 by
    # diffing (roads are 5.0 m, laneOffset -6.25, lane width 12.5) -- the
    # provenance existed nowhere until this registry recorded it.
    dict(kind="file", artifact="cad/track_grid3x3_junctions_bnd.xodr",
         cmd=["cad/export_xodr.py", "--junctions", "--boundary",
              "--lanemaker-lanes", "--sim-min-road", "5", "--out", "{out}"]),
    # Also a combined run (Appendix EP): the LaneMaker lane convention on 5 m
    # roads. Same provenance recovery as _bnd above.
    dict(kind="file", artifact="cad/track_grid3x3_junctions_lmlanes.xodr",
         cmd=["cad/export_xodr.py", "--junctions", "--lanemaker-lanes",
              "--sim-min-road", "5", "--out", "{out}"]),
    # --sim-min-road 5 is not a guess: the committed file's shortest road
    # measures exactly 5.000000 m, and Appendix EP records that run.
    dict(kind="file", artifact="cad/track_grid3x3_junctions_sim.xodr",
         cmd=["cad/export_xodr.py", "--junctions", "--sim-min-road", "5", "--out", "{out}"]),
    dict(kind="dir", artifact="cad", files=["probe_1_straight.xodr",
                                            "probe_2_arc.xodr",
                                            "probe_3_open8.xodr",
                                            "probe_4_closed8.xodr"],
         cmd=["cad/export_xodr.py", "--probe", "--out", "{out}"]),

    # --- cad/rescale_reference_xodr.py -------------------------------------
    # Default target 2.7 m derives k=0.020876167519805887.
    dict(kind="file", artifact="cad/track_1122_rescaled.xodr",
         cmd=["cad/rescale_reference_xodr.py", "--out", "{out}"]),
    # The spawn-threshold ladder from Appendix EO. Each k verified 2026-09-09
    # to reproduce its committed file byte-for-byte.
    dict(kind="file", artifact="cad/probe_spawn_k010.xodr",
         cmd=["cad/rescale_reference_xodr.py", "--scale", "0.10", "--out", "{out}"]),
    dict(kind="file", artifact="cad/probe_spawn_k025.xodr",
         cmd=["cad/rescale_reference_xodr.py", "--scale", "0.25", "--out", "{out}"]),
    dict(kind="file", artifact="cad/probe_spawn_k050.xodr",
         cmd=["cad/rescale_reference_xodr.py", "--scale", "0.50", "--out", "{out}"]),
    dict(kind="file", artifact="cad/probe_spawn_k100.xodr",
         cmd=["cad/rescale_reference_xodr.py", "--scale", "1.00", "--out", "{out}"]),
    # k chosen so the reference's shortest road matches OUR 1.463 m street.
    dict(kind="file", artifact="cad/probe_spawn_kours.xodr",
         cmd=["cad/rescale_reference_xodr.py", "--scale", "0.143292", "--out", "{out}"]),

    # --- track layouts: --out is a DIRECTORY, two artifacts each -----------
    dict(kind="dir", artifact="cad", files=["track_layout_v1.json",
                                            "track_layout_v1.svg"],
         cmd=["cad/track_layout_v1.py", "--out", "{out}"]),
    dict(kind="dir", artifact="cad", files=["track_layout_v2.json",
                                            "track_layout_v2.svg"],
         cmd=["cad/track_layout_v2.py", "--out", "{out}"]),

    # --- printed parts ------------------------------------------------------
    dict(kind="file", artifact="cad/servo_lego_coupler_v1.stl",
         cmd=["scripts/gen_servo_lego_coupler.py", "-o", "{out}"]),
    # v2 (2026-10-04): v1's +0.20 socket printed too loose on a Lego axle.
    dict(kind="file", artifact="cad/servo_lego_coupler_v2.stl",
         cmd=["scripts/gen_servo_lego_coupler.py", "--socket-clear", "0.00",
              "-o", "{out}"]),
    # v3 (2026-10-10): Evan fitted v2 - half the wall, a bit shorter, same fits.
    dict(kind="file", artifact="cad/servo_lego_coupler_v3.stl",
         cmd=["scripts/gen_servo_lego_coupler.py", "--socket-clear", "0.00",
              "--od", "7.4", "--bore-depth", "7", "--socket-depth", "5",
              "-o", "{out}"]),
    # Drive motor (Pololu #5159, 3 mm D-shaft) to a real Lego axle, 2026-10-10.
    dict(kind="file", artifact="cad/motor_lego_coupler_v1.stl",
         cmd=["scripts/gen_servo_lego_coupler.py", "--socket-clear", "0.00",
              "--od", "7.4", "--bore-dia", "3.0", "--bore-flat", "2.5",
              "--screw-dia", "1.5", "--bore-depth", "8", "--socket-depth", "5",
              "-o", "{out}"]),
    # Motor v2 (2026-10-11, Evan): +0.075 mm on the D-bore only.
    dict(kind="file", artifact="cad/motor_lego_coupler_v2.stl",
         cmd=["scripts/gen_servo_lego_coupler.py", "--socket-clear", "0.00",
              "--od", "7.4", "--bore-dia", "3.075", "--bore-flat", "2.575",
              "--screw-dia", "1.5", "--bore-depth", "8", "--socket-depth", "5",
              "-o", "{out}"]),
    # Motor v3 (2026-10-11, Evan): another +0.075 mm on the D-bore.
    dict(kind="file", artifact="cad/motor_lego_coupler_v3.stl",
         cmd=["scripts/gen_servo_lego_coupler.py", "--socket-clear", "0.00",
              "--od", "7.4", "--bore-dia", "3.15", "--bore-flat", "2.65",
              "--screw-dia", "1.5", "--bore-depth", "8", "--socket-depth", "5",
              "-o", "{out}"]),
    # PLA fit coupon (2026-10-11): pin holes, pitch, pilot holes, zip slots - OpenSCAD via render_scad.py.
    dict(kind="file", artifact="cad/pla_fit_coupon.stl",
         cmd=["scripts/render_scad.py", "cad/scad/pla_fit_coupon.scad", "-o", "{out}"]),
    dict(kind="file", artifact="cad/motor_mount.stl",
         cmd=["scripts/render_scad.py", "cad/scad/motor_mount.scad", "-o", "{out}"]),
    dict(kind="file", artifact="cad/servo_mount.stl",
         cmd=["scripts/render_scad.py", "cad/scad/servo_mount.scad", "-o", "{out}"]),
    dict(kind="file", artifact="cad/tolerance_coupon_v2.stl",
         cmd=["scripts/gen_tolerance_coupon.py", "-o", "{out}"]),

    # --- CANNOT BE CHECKED HERE, and said out loud rather than omitted ------
    dict(kind="uncheckable", artifact="ml/artifacts/p1_first_frame.png",
         reason="ml/verify_env.py needs the Unity simulator (~236 MB, gitignored "
                "under sim/) and an NVIDIA GPU. It also has no argparse at all -- "
                "the output path is the constant at ml/verify_env.py:22."),
    dict(kind="uncheckable", artifact="cad/tolerance_coupon_v1.stl",
         reason="Superseded design. scripts/gen_tolerance_coupon.py now emits the "
                "v2 geometry (axle sweep 4.80-5.30 mm); v1's axle row failed and "
                "was replaced 2026-09-05. Kept as the printed-and-tested artifact "
                "behind Appendix DI, not as regenerable output."),
]


def _run(cmd_tpl: list[str], out: Path) -> subprocess.CompletedProcess:
    cmd = [str(PY)] + [str(REPO / c) if c.endswith(".py") else c.format(out=out)
                       for c in cmd_tpl]
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)


def check_one(entry: dict, tmp: Path) -> tuple[str, str]:
    """Return (verdict, detail). Verdict is OK | DRIFT | ERROR | UNCHECKABLE."""
    if entry["kind"] == "uncheckable":
        return "UNCHECKABLE", entry["reason"]

    if entry["kind"] == "file":
        fresh = tmp / Path(entry["artifact"]).name
        proc = _run(entry["cmd"], fresh)
        if proc.returncode != 0:
            return "ERROR", f"generator exited {proc.returncode}: {proc.stderr.strip()[:300]}"
        if not fresh.exists():
            return "ERROR", "generator ran but wrote nothing to the temp path"
        committed = REPO / entry["artifact"]
        if not committed.exists():
            return "ERROR", "tracked artifact is missing from the working tree"
        same = filecmp.cmp(fresh, committed, shallow=False)
        return ("OK", "") if same else ("DRIFT", _regen_hint(entry))

    # kind == "dir"
    outdir = tmp / "d"
    outdir.mkdir(parents=True, exist_ok=True)
    proc = _run(entry["cmd"], outdir)
    if proc.returncode != 0:
        return "ERROR", f"generator exited {proc.returncode}: {proc.stderr.strip()[:300]}"
    drifted = []
    for name in entry["files"]:
        fresh, committed = outdir / name, REPO / entry["artifact"] / name
        if not fresh.exists():
            return "ERROR", f"generator did not write {name}"
        if not committed.exists() or not filecmp.cmp(fresh, committed, shallow=False):
            drifted.append(name)
    if drifted:
        return "DRIFT", f"{', '.join(drifted)} -- {_regen_hint(entry)}"
    return "OK", ""


def _regen_hint(entry: dict) -> str:
    """The exact command that fixes it, with the temp path swapped for the real
    destination -- so a blocked commit tells you what to run, not just what broke."""
    dest = entry["artifact"] if entry["kind"] == "dir" else entry["artifact"]
    parts = [c for c in entry["cmd"]]
    for i, c in enumerate(parts):
        if c == "{out}":
            parts[i] = dest
    return "regenerate: .venv/Scripts/python.exe " + " ".join(parts)


def entry_paths(entry: dict) -> list[str]:
    if entry["kind"] == "dir":
        return [f"{entry['artifact']}/{n}" for n in entry["files"]]
    return [entry["artifact"]]


def staged_paths() -> set[str]:
    proc = subprocess.run(["git", "diff", "--cached", "--name-only"],
                          cwd=REPO, capture_output=True, text=True)
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--staged", action="store_true",
                    help="only check artifacts staged in the current commit "
                         "(what the pre-commit hook uses)")
    ap.add_argument("--list", action="store_true",
                    help="print the registry and exit; regenerates nothing")
    args = ap.parse_args()

    if args.list:
        for e in ARTIFACTS:
            for p in entry_paths(e):
                print(f"  {e['kind']:12} {p}")
        print(f"\n{sum(len(entry_paths(e)) for e in ARTIFACTS)} artifacts registered")
        return 0

    entries = ARTIFACTS
    if args.staged:
        staged = staged_paths()
        entries = [e for e in ARTIFACTS
                   if staged.intersection(entry_paths(e))]
        if not entries:
            print("check_artifacts: no registered artifact is staged -- nothing to do")
            return 0

    drift, errors, unchecked = [], [], []
    with tempfile.TemporaryDirectory(prefix="artifact_check_") as td:
        for e in ARTIFACTS if not args.staged else entries:
            tmp = Path(td) / str(ARTIFACTS.index(e))
            tmp.mkdir(parents=True, exist_ok=True)
            verdict, detail = check_one(e, tmp)
            label = ", ".join(entry_paths(e))
            if verdict == "OK":
                print(f"  OK           {label}")
            elif verdict == "UNCHECKABLE":
                print(f"  UNCHECKABLE  {label}")
                print(f"               {detail}")
                unchecked.append(label)
            elif verdict == "DRIFT":
                print(f"  DRIFT        {label}")
                print(f"               {detail}")
                drift.append(label)
            else:
                print(f"  ERROR        {label}")
                print(f"               {detail}")
                errors.append(label)

    total = sum(len(entry_paths(e)) for e in (entries if args.staged else ARTIFACTS))
    print(f"\n{total} artifacts checked, {len(drift)} drifted, "
          f"{len(errors)} errored, {len(unchecked)} uncheckable")

    if drift or errors:
        print("\nA committed artifact no longer matches its generator. Regenerate it")
        print("with the command above and stage the result, or -- if you are")
        print("deliberately committing a stale artifact -- bypass with:")
        print("    git commit --no-verify")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
