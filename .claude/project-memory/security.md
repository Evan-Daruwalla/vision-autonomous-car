# security.md — Autonomous Car Project

- empty, no attack surface yet (2026-07-23). Becomes live at M2 (teleop over
  WiFi: auth on the control endpoint).

- **A serial actuator surface appears with the Arduino (2026-09-02).** Anything
  able to write to COM3 can command the motor and steering directly, bypassing
  the policy. On a tethered bench car that is acceptable; it is worth stating
  because it is a real surface that did not exist when actuation was GPIO from
  the Pi itself.
- **The watchdog is a SAFETY feature, not a security one, and the distinction
  matters.** Firmware cutting throttle after a command timeout protects against
  a hung Pi or a diverging policy. It does not protect against a hostile writer
  on the port, which would simply keep sending valid commands.
- Still no network attack surface. Teleop over WiFi (M2) remains the first real
  one, and the note above about auth on the control endpoint still stands.
