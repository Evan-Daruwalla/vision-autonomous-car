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
- **`arduino-cli` ships INSIDE the Arduino IDE (found 2026-09-02)** — no separate
  install, and it is not on PATH:
  `~/AppData/Local/Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe`
  (v1.5.1, with core `arduino:avr 1.8.8` already present). Build/upload:
  `arduino-cli compile --fqbn arduino:avr:uno firmware/<sketch>` then
  `arduino-cli upload -p COM3 --fqbn arduino:avr:uno firmware/<sketch>`.
- **`--fqbn arduino:avr:uno` is MANDATORY on every command.** `arduino-cli board
  list` reports COM3 as `Unknown` with no FQBN, because the FT232RL is a generic
  bridge carrying no Arduino vendor ID (a genuine Uno announces itself through an
  ATmega16U2). The IDE's board dropdown will not auto-select either.
- **Reading the board's serial from the shell:** PowerShell
  `System.IO.Ports.SerialPort` works. **Opening the port RESETS the board**, so
  timestamp lines on the HOST and compare deltas — comparing board uptime against
  a host stopwatch started at a different moment produced a bogus 0.54x clock
  ratio before this was understood (Appendix BE).
