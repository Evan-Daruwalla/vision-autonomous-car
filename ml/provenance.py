"""Stamp every result file with the code that produced it.

WHY THIS EXISTS. On 2026-09-02 a cold audit counted **0 of 108** tracked
`ml/runs/**/*.json` carrying the commit that produced them, while 82 carried a
seed. A seed makes a run repeatable only if you also know WHICH CODE it ran
under, and this project has already been bitten by exactly that gap:
`ml/runs/controller/history_linear_seed0.json` was silently rewritten on
2026-08-25 by a re-run under newer code, and the only surviving evidence of
which code is a filesystem mtime -- which any `git checkout` or file copy
destroys. Recorded as PRD task A1 (Appendix CB); this is the fix.

THE 108 EXISTING FILES CANNOT BE RETROFITTED. Anything citing them must say so.

WHY A MODULE AND NOT A ONE-LINER. The audit suggested "stamp `git rev-parse
HEAD` in the shared result writer". There was no shared writer -- 23 ad hoc
`write_text(json.dumps(...))` sites across 21 files. This creates the
chokepoint the suggestion assumed, which is also why the fix is one import per
file rather than one line in one file. Same reasoning as
`splits.split_seed_of`: one helper at the shared chokepoint beats N copies that
drift (cold audit A2, and the six-copy drift that produced it).

REFUSE ON NO COMMIT, RECORD ON DIRTY -- and the asymmetry is deliberate.
A missing commit means the stamp cannot do its job at all, so `write_result`
raises; PRD A1's own done-check says the writer "refuses to write without one".
A dirty tree is different: it is the NORMAL state while iterating, refusing
would block real work, and it hides nothing because `dirty` and `dirty_files`
are written into the file. A reader can then see that a result came from an
edited tree -- which is strictly more than the 108 files say today.

Stdlib only, on purpose: this is imported by the camera diagnostics, which have
no torch dependency of their own and should not gain one for a version string.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Cap the dirty-file list so a wildly dirty tree cannot bloat every result
# file. The COUNT is always exact; only the listing is truncated.
MAX_DIRTY_LISTED = 20


def _git(args: list[str], repo: Path) -> str | None:
    """Run a git command, returning stripped stdout or None if it cannot."""
    try:
        p = subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                           text=True, timeout=10)
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return None          # no git on PATH, or it failed to launch
    if p.returncode != 0:
        return None          # not a repo, or the command is not valid here
    # rstrip a trailing newline and NOT .strip(): porcelain's first line begins
    # with a SIGNIFICANT space (" M path"), and stripping the whole output ate
    # it, so _parse_porcelain's 3-char slice took one character too many off the
    # FIRST entry only -- ".claude/..." was recorded as "claude/...". Found by
    # reading the first real result file this module wrote, 2026-09-03.
    return p.stdout.rstrip("\n")


def _parse_porcelain(text: str) -> list[str]:
    """Paths from `git status --porcelain` output.

    Format is XY<space>path: two status columns then one space, so the path
    starts at index 3 -- and column 1 is a SPACE for anything modified in the
    worktree but not staged, which is most of them. Whitespace here is data.
    """
    out = []
    for ln in text.split("\n"):
        if len(ln) > 3:
            out.append(ln[3:])
    return out


def _version(pkg: str) -> str | None:
    try:
        from importlib.metadata import version
        return version(pkg)
    except Exception:        # noqa: BLE001 - a missing package is not an error here
        return None


def stamp(repo: Path = REPO) -> dict:
    """Provenance for a result produced right now.

    `commit` is None outside a git repo or when git is unavailable -- callers
    decide what that means. `dirty` is True when the working tree has ANY
    modification, tracked results included: this project commits `ml/runs/`,
    so an unrelated result file left dirty makes the tree dirty, and that is
    honest rather than noise.
    """
    commit = _git(["rev-parse", "HEAD"], repo)
    porcelain = _git(["status", "--porcelain"], repo)
    if porcelain is None:
        dirty, dirty_files = None, None
    else:
        lines = _parse_porcelain(porcelain)
        dirty, dirty_files = bool(lines), sorted(lines)[:MAX_DIRTY_LISTED]
    return {
        "commit": commit,
        "dirty": dirty,
        "dirty_files": dirty_files,
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "torch": _version("torch"),
        "numpy": _version("numpy"),
    }


def write_result(path, obj: dict, repo: Path = REPO, _stamp=stamp) -> Path:
    """Write `obj` as JSON with a `provenance` block. THE result writer.

    Refuses a non-dict payload: `{"provenance": ...}` has nowhere to go in a
    list, and three call sites used to write bare lists.
    """
    path = Path(path)
    if not isinstance(obj, dict):
        raise TypeError(
            f"write_result needs a dict so provenance has somewhere to live; "
            f"got {type(obj).__name__}. Wrap it, e.g. {{'history': ...}}.")
    if "provenance" in obj:
        raise ValueError("payload already has a 'provenance' key")
    st = _stamp(repo)
    if st["commit"] is None:
        raise RuntimeError(
            f"refusing to write {path.name}: cannot determine the git commit "
            f"({repo}). A result that cannot name the code that produced it is "
            f"what PRD task A1 exists to stop. Run inside the repo with git on "
            f"PATH.")
    if st["dirty"]:
        n = len(st["dirty_files"])
        print(f"  note: tree is dirty ({n}{'+' if n == MAX_DIRTY_LISTED else ''} "
              f"file(s)); recorded in provenance.dirty_files")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({**obj, "provenance": st}, indent=2),
                    encoding="utf-8")
    return path


def self_check() -> None:
    import re
    import tempfile

    # Whitespace in porcelain is DATA. This is the regression test for the bug
    # this module shipped with: _git stripped the whole output, eating the
    # leading space of the FIRST line, so the first path lost its first
    # character (".claude/x" -> "claude/x"). Pure, no filesystem.
    got = _parse_porcelain(" M .claude/a.md\nMM docs/b.md\n?? c.txt")
    assert got == [".claude/a.md", "docs/b.md", "c.txt"], got
    assert _parse_porcelain("") == []

    st = stamp()
    head = _git(["rev-parse", "HEAD"], REPO)
    assert st["commit"] == head, f"commit {st['commit']} != rev-parse {head}"
    assert re.fullmatch(r"[0-9a-f]{40}", st["commit"] or ""), \
        f"not a 40-hex sha: {st['commit']}"
    assert isinstance(st["dirty"], bool), f"dirty is {type(st['dirty'])}"
    assert isinstance(st["dirty_files"], list)
    assert len(st["dirty_files"]) <= MAX_DIRTY_LISTED
    datetime.fromisoformat(st["ts_utc"])          # raises if malformed
    assert st["python"].startswith("3."), st["python"]
    # Live cross-check against the real tree: a truncated path is not a path
    # any git command would ever emit, so ask git directly whether it knows it.
    # A path git emitted is either on disk (modified, or a new untracked file)
    # or tracked-but-deleted. A TRUNCATED path is neither, which is exactly how
    # the 2026-09-03 bug would have been caught on its first run.
    known = set(_git(["ls-files"], REPO).split("\n"))
    for f in st["dirty_files"]:
        assert (REPO / f).exists() or f in known, (
            f"dirty_files holds {f!r}, which is not on disk and not tracked -- "
            f"the porcelain parse truncated it")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        # Outside a repo there is no commit, and the writer must REFUSE.
        # (Checked here rather than trusted: a stamp that silently returned a
        # commit from some enclosing repo would defeat the whole module.)
        assert stamp(repo=tmp)["commit"] is None, \
            "a non-repo directory must not yield a commit"
        try:
            write_result(tmp / "x.json", {"a": 1}, repo=tmp)
            raise AssertionError("write_result must refuse without a commit")
        except RuntimeError:
            pass

        # round trip
        p = write_result(tmp / "sub" / "r.json", {"a": 1})
        got = json.loads(p.read_text(encoding="utf-8"))
        assert got["a"] == 1 and got["provenance"]["commit"] == head
        assert set(got) == {"a", "provenance"}

        # a list payload is the shape three call sites used to write
        for bad in ([1, 2], "s"):
            try:
                write_result(tmp / "bad.json", bad)
                raise AssertionError(f"must refuse {type(bad).__name__}")
            except TypeError:
                pass

        # a payload already carrying provenance must not be silently merged
        try:
            write_result(tmp / "dup.json", {"provenance": {}})
            raise AssertionError("must refuse a duplicate provenance key")
        except ValueError:
            pass

    print("provenance self_check: PASS")


if __name__ == "__main__":
    self_check()
