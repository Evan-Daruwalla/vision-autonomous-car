# tooling.md — Autonomous Car Project

- ~~All ML work runs in a pinned Python **3.11** venv (decided 2026-08-05);
  DonkeyCar 5.x requires 3.11 so one version serves desktop and Pi.~~
  **CORRECTED 2026-08-06 (cold audit F17): the venv is Python 3.12.10** —
  `.venv/pyvenv.cfg` says so, and 3.11 is not installed on this machine. The
  intent was 3.11; what got built is 3.12.10, and it works. The
  "one version serves desktop and Pi" reasoning is therefore VOID: the Pi
  will run 3.11 for DonkeyCar and the desktop runs 3.12.10, so anything
  shared between them must not depend on version parity.
- System Python is 3.14.4 — too new to assume PyTorch/gym wheel coverage, so
  ML work stays in the venv. Wheel availability was verified by SIM-POC P1's
  done-check, not assumed.
- Machine facts (verified 2026-07-23): git 2.53.0 with Evan's identity
  configured; real Python 3.14.4 (not the Store stub); PrusaSlicer AND
  Bambu Studio installed; OpenSCAD NOT installed (the coupon generator is
  zero-dependency Python for this reason). Printer model + filament stock
  still uncatalogued (M1.2).
- Multi-line git commit messages on this machine: write to a file and use
  `git commit -F <file>` — PowerShell here-strings mangle embedded quotes
  into pathspecs (hit 2026-07-23).
- CAD tool choice still pending (M1.2; Onshape recommended, not decided).
