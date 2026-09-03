# conventions.md — Autonomous Car Project

General code conventions actually observed across the **34** files under
`ml/` (**re-derived 2026-09-03** by running the greps, not by incrementing the
old ones; the previous "31" was already stale at 33 before `provenance.py`).
Counts are exact. This
bin is general coding style — data schema/format conventions live in
data.md, verification/gate conventions in testing.md, environment/build in
tooling.md; don't duplicate those here.

- **`from __future__ import annotations`** at the top of **32/34** files.
- **`pathlib.Path`** for all filesystem paths in **31/34** files — no bare
  string paths in new code.
- **Every file (34/34) opens with a module docstring**, usually stating what
  the script measures/proves and why, several with a `Usage:` block showing
  example invocations (e.g. `train_vae.py`).
- **argparse-based CLI** in **27/34** files — scripts are run standalone with
  flags, not imported as a library API.
- **`--seed` flag in **16/34** files** — every training/eval script seeds torch,
  numpy and CUDA explicitly (testing.md's "seed everything" rule; this is
  the convention that rule is implemented as).
- **`print()`, not `logging`** — **33/34** files print directly; zero files
  import the `logging` module. No structured logging in this codebase.
- **Self-check mode**: 3 files (`exp_aux_head.py` among them) ship a
  `--self-check`/`self_check` flag that validates the script's own pipeline
  assumptions before trusting its results (testing.md's gate philosophy).
- Type hints on function signatures are present in **33/34** files.

- **Every result JSON UNDER `ml/` goes through `provenance.write_result(path,
  obj)`** (added 2026-09-03, PRD task A1). ⚠️ **Scope corrected 2026-09-03: the
  first wording said "every result JSON" and that was false** — `cad/track_layout_v1.py:438`
  and `v2.py:472` still write tracked `cad/track_layout_v*.json` with bare
  `json.dumps`. They are geometry artifacts, not experiment results, so they are
  out of A1's scope; but the universal as written was wrong (Appendix CG). Never `write_text(json.dumps(...))` for a result --
  it stamps `commit`, `dirty`, `dirty_files`, `ts_utc` and the python/torch/numpy
  versions, and **REFUSES to write when it cannot determine the commit**. The
  payload must be a dict; three call sites used to write bare lists and are now
  `{"history": ...}` / `{"rows": ...}`. The 108 result files written before this
  carry no commit and **cannot be retrofitted** -- say so when citing them.
