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
  configured; real Python 3.14.4 (not the Store stub); ~~PrusaSlicer AND~~
  Bambu Studio installed (PrusaSlicer NOT found on 2026-10-11 - stale claim); ~~OpenSCAD NOT installed (the coupon generator is
  zero-dependency Python for this reason).~~ **OpenSCAD 2021.01 INSTALLED 2026-10-11** (see below). Printer model + filament stock
  still uncatalogued (M1.2).
- Multi-line git commit messages on this machine: write to a file and use
  `git commit -F <file>` — PowerShell here-strings mangle embedded quotes
  into pathspecs (hit 2026-07-23).
- ~~CAD tool choice still pending (M1.2; Onshape recommended, not decided).~~
  **2026-10-11 (Evan): printed mounts are OpenSCAD.** OpenSCAD 2021.01 (latest
  stable), the official portable zip `OpenSCAD-2021.01-x86-64.zip` from
  files.openscad.org, 21,884,613 bytes, SHA-256 verified against the published
  file, unpacked to `~/tools/openscad-2021.01/` (NOT on PATH). Use
  `openscad.com` for the CLI (it prints to the console; `openscad.exe` is the
  GUI). `scripts/render_scad.py` finds it there (or `$OPENSCAD`) and writes a
  canonical, validated STL. Only numpy is in the venv: no CSG library.
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

## Moved from gotchas.md 2026-09-02 (Appendix BO)

- **Quoted heredocs write backslash-u escapes LITERALLY.** `cat > f <<'EOF'` does
  no escape interpretation, so a `\u2014` written for an em dash lands as six
  characters. 21 such lines reached the append-only record on 2026-09-02 and
  **cannot be edited out**. Write real UTF-8 characters, or build the file in
  Python where the escapes are interpreted.


- **OpenSCAD 2021.01 asserts exit 0 (2026-10-13, record HL):** a failed `assert()` prints "ERROR: Assertion ... failed" but `openscad.com` still exits 0 (seen in echo mode). render_scad.py does not rely on the exit code - a failed assert leaves no valid mesh, so its manifold/probe gate fails.
- **COM3 "Access is denied" on upload (2026-10-13, record HT):** another program holds the Uno's port - usually the Arduino IDE Serial Monitor. Close it; `arduino-cli upload -p COM3 --fqbn arduino:avr:uno <sketch>` then works (HU). Reading the boot banner = open COM3 at 115200 with pyserial (opening resets the board).

- 2026-10-22 (KV, KW): headless Chrome (--screenshot / --dump-dom, even with --virtual-time-budget) does NOT advance CSS animations - every capture shows t=0, so it cannot verify an animated SVG. The desktop app's browser pane does animate, but only for files inside the project folder, and it refused to open the 728 KB docs/shield_how_it_works.svg; verify animation there on a smaller file or read the keyframes.
