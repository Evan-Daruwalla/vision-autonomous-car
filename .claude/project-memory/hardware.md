# hardware.md — Autonomous Car Project

**Split out of `gotchas.md` on 2026-09-02** (Appendix BO), which had reached
423 lines, 2.8x the ~150 cap. Physical-build traps: printing and Lego fit,
power, motors and drivers, the Arduino Uno, and measured vehicle geometry.

Entries dated 2026-07-23 come from the research brief
(`docs/research/2026-07-23_sensor-compute-stack.md`) and are **DESK RESEARCH,
not yet verified on this car.** Mark them verified when a build task confirms.

Track and marking traps are in `track.md`; simulator and training-harness
traps in `sim-harness.md`.

## Router (split 2026-10-29) - this file is now the index

- hardware-power.md - pack, BMS, charger, LM2596, power distribution, fuse, current limits, Pi 5 power, Uno VIN, charger-vs-BMS and search-snippet traps
- hardware-shield-wiring.md - proto shield, wiring, Uno pins and pin budget, FTDI board, TB6612 wiring traps, encoder wiring, WS2812B lighting, shield build records
- hardware-print-mounts.md - FDM/Lego fit, motors and gearing, couplers, printed mounts, camera mast, tray/deck layout, filament, measured vehicle width
- track.md - track and marking traps; sim-harness.md - simulator and training-harness traps

Facts that fit none of the three topics stay below.

- **MPU6050 is EOL** (TDK discontinued, counterfeit-prone modules). If an IMU
  enters at M4: ICM-20948 ($20, raw) or BNO055 ($35, on-chip fusion)
  (2026-07-23).
- DonkeyCar 5.x requires **64-bit Raspberry Pi OS Bookworm + Python 3.11** **[superseded 2026-10-25, record LD: DonkeyCar dropped; custom `pi/` stack]**;
  its trainer is TensorFlow/Keras, not PyTorch (2026-07-23).
- Pi 5 prices are volatile (LPDDR4 shortage; two hikes in three months as of
  2026) — re-verify at purchase time, don't trust the brief's numbers blind.
- **Camera Module 3 ships with the WRONG cable for a Pi 5** (verified
  against Raspberry Pi docs 2026-07-23). The Pi 5 uses the **mini 22-pin**
  connector; the module includes a Standard-Standard cable. A **Standard-
  Mini** cable must be bought separately or the camera cannot be connected
  at all. It is in `docs/BOM.md`.
- 2026-10-16 (records JF-JH): Pi 5 bring-up - SSH from PowerShell works; first flash was Trixie / Python 3.13, being re-flashed to Raspberry Pi OS Lite (Legacy, 64-bit) = Bookworm; hostname `ed-pi5`, user `ed`. Camera Module 3 Wide arrived 2026-10-15 (IX), not yet tested. Power entry: Uno on the Pi's USB (plain cable), `+5V2` only for servo/strips/encoder (JF); servo supply (Uno 5V vs `+5V2`) pending a test on Pi USB.
- 2026-10-16 (Evan): TWO Camera Module 3 Wide are on hand (identical). Plan: one camera through M3; the second is a spare and a later measured experiment (stereo depth or front + rear) - not in the current mast or data pipeline.
- 2026-10-30 (record LR): Pi RE-FLASHED (the old password was lost): Raspberry Pi OS Lite (Legacy, 64-bit) = Debian 12 bookworm, Python 3.11.2, Pi 5 Rev 1.1 4 GB; hostname `ed-pi5`, user `ed`, SSH PUBLIC-KEY ONLY (key `~/.ssh/id_ed25519` on the PC, comment `pc-to-ed-pi5`); passwordless sudo. A re-flash wipes the apt packages - redo `sudo apt install python3-picamera2 python3-venv`, then `bash pi/deploy.sh`. Boot LED 7 short = kernel image not found (seen on one bad flash). `vcgencmd get_throttled` read 0x50000 (under-voltage + throttling occurred since boot) - the Pi's supply is unrecorded and must be checked (Pi 5 wants 5 V / 5 A).
