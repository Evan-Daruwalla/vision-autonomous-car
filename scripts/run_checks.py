#!/usr/bin/env python
"""The test suite. Runs every self_check() in the repo and reports honestly.

WHY THIS EXISTS (2026-09-09, daily-audit Appendix ES finding 4)
--------------------------------------------------------------
CLAUDE.md's definition of done requires "the test suite ran with real output
pasted" -- but there was no test suite. `git ls-files | grep -cE
'(^|/)(test_|tests?/)'` returned 0. What this repo has instead is a self_check()
convention: 14 modules carry one, most wired to a --self-check flag. Nothing
ever ran them together, so "the suite passed" could not be said truthfully.

This runs all of them, in one process, and prints a result for each.

DISCOVERY IS A WALK, NOT A LIST. A hardcoded registry would go stale the first
time someone adds a module -- which is the exact failure mode this session
spent its day fixing. The walk finds `def self_check` under cad/, ml/ and
scripts/, skipping .venv/ and ml/vendor/ (third-party, not ours to test).

THE THREE STATES, and why SKIP is not a pass
--------------------------------------------
  PASS  self_check() returned without raising, and returned nothing or 0.
  FAIL  it raised AssertionError (a violated invariant), raised anything else
        unexpected, or returned a non-zero int. Exit code 1.
  SKIP  it could not run because this machine lacks a resource -- a GPU, the
        gitignored driving corpus under ml/data/, an absent file. The reason is
        ALWAYS printed. A SKIP is never counted as a pass and never silent,
        because a silently-skipped check is indistinguishable from a passing
        one, which is how a suite starts lying.

  A missing dependency is a SKIP; a violated invariant is a FAIL. That is the
  whole classification rule. Its known weakness: a genuine bug that surfaces as
  ImportError would be reported as a SKIP. Use --strict in CI to make any SKIP
  fatal.

USAGE
  python scripts/run_checks.py             # exit 0 unless something FAILED
  python scripts/run_checks.py --strict    # exit 1 if anything was SKIPPED too
  python scripts/run_checks.py --verbose   # show each check's own stdout
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import contextlib
import sys
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SEARCH_DIRS = ("cad", "ml", "scripts")
EXCLUDE_PARTS = {".venv", "vendor", "__pycache__", "site-packages"}

# Exceptions that mean "this machine cannot run the check", not "the code is
# wrong". Anything else is a real failure.
MISSING_RESOURCE = (ImportError, ModuleNotFoundError, FileNotFoundError)


def find_modules() -> list[Path]:
    """Every .py under SEARCH_DIRS that defines a self_check, sorted."""
    found = []
    me = Path(__file__).resolve()
    for d in SEARCH_DIRS:
        for p in sorted((REPO / d).rglob("*.py")):
            if EXCLUDE_PARTS.intersection(p.parts):
                continue
            # This file documents the convention, so its own docstring contains
            # the search string. Without this it discovers, imports and fails
            # on itself.
            if p.resolve() == me:
                continue
            try:
                if "def self_check" in p.read_text(encoding="utf-8", errors="ignore"):
                    found.append(p)
            except OSError:
                continue
    return found


def run_one(path: Path, verbose: bool) -> tuple[str, str, str]:
    """Import the module and call self_check(). Returns (state, reason, output)."""
    name = "_check_" + path.stem
    buf = io.StringIO()
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        # Import and call both run with stdout captured: a self_check that
        # prints its own banner should not shred this report's formatting.
        with contextlib.redirect_stdout(buf):
            spec.loader.exec_module(module)
            if not callable(getattr(module, "self_check", None)):
                # The text "def self_check" appeared (a docstring, a comment)
                # but no callable exists. Reported, never silently dropped.
                return ("SKIP", "matched 'def self_check' as text but the module "
                                "defines no callable of that name", buf.getvalue())
            result = module.self_check()
    except AssertionError as e:
        return "FAIL", f"AssertionError: {e}".strip(), buf.getvalue()
    except MISSING_RESOURCE as e:
        return "SKIP", f"{type(e).__name__}: {e}", buf.getvalue()
    except Exception:
        return "FAIL", traceback.format_exc(limit=3).strip(), buf.getvalue()

    # ml/exp_aux_head.py's self_check returns an int exit code rather than None.
    if isinstance(result, int) and result != 0:
        return "FAIL", f"self_check() returned {result}", buf.getvalue()
    return "PASS", "", buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true",
                    help="treat SKIP as failure (for CI, where every resource "
                         "is supposed to be present)")
    ap.add_argument("--verbose", action="store_true",
                    help="print each check's own stdout, not just the verdict")
    args = ap.parse_args()

    modules = find_modules()
    if not modules:
        print("run_checks: found no module defining self_check -- that is itself wrong")
        return 1

    # cad/ modules import each other by filename; ml/ ones expect the repo root.
    for extra in (REPO, REPO / "cad", REPO / "ml"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))

    passed, failed, skipped = [], [], []
    print(f"running {len(modules)} self-checks\n")
    for path in modules:
        rel = path.relative_to(REPO).as_posix()
        state, reason, output = run_one(path, args.verbose)
        print(f"  {state:5} {rel}")
        if reason:
            for line in reason.splitlines():
                print(f"        {line}")
        if args.verbose and output.strip():
            for line in output.strip().splitlines():
                print(f"        | {line}")
        {"PASS": passed, "FAIL": failed, "SKIP": skipped}[state].append(rel)

    print(f"\n{len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped"
          f"  (of {len(modules)})")
    if skipped:
        print("SKIPPED checks did NOT run and are not evidence of anything:")
        for s in skipped:
            print(f"  - {s}")
    if failed:
        print("FAILED:")
        for f in failed:
            print(f"  - {f}")
        return 1
    if skipped and args.strict:
        print("--strict: a skipped check is a failure here.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
