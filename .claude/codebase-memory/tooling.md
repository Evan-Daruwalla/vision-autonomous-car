# tooling.md — Autonomous Car Project

- **All ML work runs in a pinned Python 3.11 venv** (decided 2026-08-05).
  System Python is 3.14.4 — too new to assume PyTorch/gym wheel coverage —
  and DonkeyCar 5.x itself requires 3.11, so one version serves desktop and
  Pi. Wheel availability is verified by SIM-POC P1's done-check, not
  assumed.
- Machine facts (verified 2026-07-23): git 2.53.0 with Evan's identity
  configured; real Python 3.14.4 (not the Store stub); PrusaSlicer AND
  Bambu Studio installed; OpenSCAD NOT installed (the coupon generator is
  zero-dependency Python for this reason). Printer model + filament stock
  still uncatalogued (M1.2).
- Multi-line git commit messages on this machine: write to a file and use
  `git commit -F <file>` — PowerShell here-strings mangle embedded quotes
  into pathspecs (hit 2026-07-23).
- CAD tool choice still pending (M1.2; Onshape recommended, not decided).
