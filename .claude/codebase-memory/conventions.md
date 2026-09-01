# conventions.md — Autonomous Car Project

General code conventions actually observed across the 31 files under `ml/`
(verified 2026-08-25 by grep; counts below are exact, not estimated). This
bin is general coding style — data schema/format conventions live in
data.md, verification/gate conventions in testing.md, environment/build in
tooling.md; don't duplicate those here.

- **`from __future__ import annotations`** at the top of 29/31 files.
- **`pathlib.Path`** for all filesystem paths in 28/31 files — no bare
  string paths in new code.
- **Every file (31/31) opens with a module docstring**, usually stating what
  the script measures/proves and why, several with a `Usage:` block showing
  example invocations (e.g. `train_vae.py`).
- **argparse-based CLI** in 25/31 files — scripts are run standalone with
  flags, not imported as a library API.
- **`--seed` flag in 15/31 files** — every training/eval script seeds torch,
  numpy and CUDA explicitly (testing.md's "seed everything" rule; this is
  the convention that rule is implemented as).
- **`print()`, not `logging`** — 30/31 files print directly; zero files
  import the `logging` module. No structured logging in this codebase.
- **Self-check mode**: 3 files (`exp_aux_head.py` among them) ship a
  `--self-check`/`self_check` flag that validates the script's own pipeline
  assumptions before trusting its results (testing.md's gate philosophy).
- Type hints on function signatures are present in 30/31 files.
