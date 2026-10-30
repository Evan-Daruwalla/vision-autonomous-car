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

- **2026-10-30 (records LD, LL, LN): the network surface now EXISTS - pi/teleop.py.**
  It serves an HTTP page + a websocket that can arm the car and send steer/throttle,
  with NO login. Mitigations in code: binds 127.0.0.1 by default (reach it only
  through `ssh -L 8000:localhost:8000 -L 8765:localhost:8765 ed@ed-pi5.local`, so
  SSH is the auth); the websocket accepts only Origin
  http://localhost:<http-port>, http://127.0.0.1:<http-port>, or NO Origin header
  (non-browser clients - so the Origin check stops a hostile web page, not a
  local script); `--host 0.0.0.0` prints a WARNING that anyone on
  the network can drive the car. The 0.0.0.0 default was audit LL's top HIGH,
  fixed in LN. The "auth on the control endpoint" note above is answered by the
  tunnel, not by an in-app login - do not add a LAN-facing mode without one.
- The serial actuator surface moved from the PC's COM3 to the Pi's /dev/ttyACM0
  (anything on the Pi that can open it can drive the car; same reasoning as above).
- 2026-10-30 (record LR): the Pi's SSH is now public-key only (no password login over SSH); the private key lives only on the PC (`~/.ssh/id_ed25519`, no passphrase - anyone with that file can log in to the Pi).
