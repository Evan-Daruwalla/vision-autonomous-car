# ui.md — Autonomous Car Project

- N/A, no frontend planned; a minimal teleop UI may appear at M2 (2026-07-23).
- **Re-checked 2026-09-02: still N/A, no change.** The hardware lane started
  (`firmware/`) and vehicle LIGHTING got a spec (`docs/LIGHTING_SPEC.md`), but
  neither is a user interface — lighting is an actuator channel and a third
  policy head. No teleop UI exists or has been designed. This bin stays a stub
  until M2 teleop puts a human in front of a screen.
- **2026-10-29 (record LF): no longer N/A.** M2 teleop now has a web page, `pi/web/index.html` (record LD): video canvas, telemetry table, ARM/DISARM/REC/CRASH buttons, keyboard Space = disarm, and the Xbox pad read through the browser Gamepad API. It needs a secure context, so it is opened through an SSH tunnel at http://localhost:8000. Verified in a desktop browser against the fake car only; untested with a real pad.
- 2026-10-30 (record LQ): `pi/teleop.py --fake-uno` = FakeUno + the real Pi camera, for the Pi OFF the car (no Uno attached); `--fake` still fakes both. Use `--bench` with either (FakeUno reports pack FAULT, so arming is refused otherwise). Same page and pad mapping; episodes are flagged `fake_uno` and rejected by verify_real / bc_real. Untested on the Pi.
