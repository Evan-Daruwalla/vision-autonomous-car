# firmware-traps.md — Autonomous Car Project

**Split out of `hardware.md` on 2026-09-03** (Appendix CH), which had reached
481 lines. Traps in the Arduino toolchain and in the firmware's own logic:
building and flashing, clock handling, and what the status LED means.

Board/electrical facts (pin budget, current limits, the pack) stay in
`hardware.md`; steering geometry and the coupler are in `steering.md`.

## Arduino build + firmware traps (added 2026-09-02, Appendix BO)

- **The Arduino preprocessor hoists function prototypes ABOVE your mid-file
  declarations.** A function taking or returning an `enum`/`struct` declared
  partway down a `.ino` fails with `'OutMode' does not name a type; did you mean
  'pinMode'?` — which points at the function, not at the enum. **Declare any type
  used in a signature before the first function, or put it in a header.** Cost
  2026-09-02: one compile cycle.
- **The Servo library was NOT installed** in this Arduino environment (hit
  2026-09-02). `arduino-cli lib install Servo` fixed it (1.3.0). Worth knowing
  before assuming a bare IDE install can build anything.
- **arduino-cli lives at**
  `~/AppData/Local/Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe`
  (v1.5.1). Not on PATH. `--fqbn arduino:avr:uno` stays mandatory: `board list`
  reports COM3 as **"Unknown"** because the FTDI clone carries no board identity.
- **A green compile proves almost nothing about firmware logic.** `uno_control`
  compiled clean while carrying three wrong SELFTEST assertions; only flashing it
  and reading the board found them. Budget an upload+read cycle, not a compile.
- **Do not assert a SIGN, direction or polarity that no measurement has
  established.** A SELFTEST asserted an encoder direction as "+4 forward"; which
  way is forward is unknowable until the encoder is on a motor in a drivetrain
  that does not exist. **Test the property that survives the convention** — that
  the two directions are exact opposites, and that the quadrature table is
  antisymmetric across all 16 entries. `ENCODER_SIGN` in `uno_control.ino` is the
  knob to flip once the car rolls.
- **Measured on the board 2026-09-02** (`uno_control`, nothing wired): flash
  **7134 B of 32256 (22%)**, SRAM **312 B of 2048 (15%)**, 1736 B free; firmware
  loop period **2.0-3.0 ms** (`loop_dt` 20-30 in 100 us units) against the 50 ms
  control budget, dominated by the pack guard's 16x `analogRead`.
- **A floating A0 read 10164-10248 mV across two runs**, consistent with the
  10248 mV measured in Appendix BJ. The upper fault band catches it every time.

## Firmware clock-sampling trap (added 2026-09-02, Appendices BY/CA)

- **Take ONE `millis()` per loop iteration and pass it everywhere.** A second
  sample taken after any blocking work (here ~2 ms of `analogRead`) is LATER
  than the first; any `first - second` on `uint32_t` wraps to ~4.29e9 and
  blows through every threshold. In `uno_control` this made the watchdog trip in
  the same iteration as every good frame. **Symptom with a motor wired: drive
  ~2 ms, brake ~48 ms, repeat** — a car that judders instead of driving, with
  nothing in the telemetry saying why.
- **The reply is built BEFORE the watchdog block runs**, so watchdog effects
  never appear in the reply that triggered them. Probe `armed` via `?` inside
  the window instead. See `testing.md` for the red/green evidence.
- **A scheduled cold audit found this; the author's own tests did not.** The
  audit's suggested test was also blind to it. Both facts are recorded so the
  next "verified on the board" claim names what was and was not exercised.

## Status-LED semantics: quiet on a bench, loud on a car (added 2026-09-02, Appendix CE)

- **A floating analog pin and a sense wire that FELL OFF read identically**
  (~10,248 mV). In the instant they are indistinguishable — which is why the
  upper fault band exists at all. **So no fault indicator may go quiet by
  inferring "probably just unwired".** It would also go quiet on the car.
- **They differ in HISTORY, and history is one bool.** `PackGuard::everPlausible`
  is set the first time a reading lands inside the fault band and never cleared.
  A board that has NEVER seen a plausible pack was never wired. The status LED
  silences `PACK_FAULT` only in that case — automatically, every power cycle.
  **The moment a real divider reads sane, every later fault is loud again.**
- **The watchdog blink follows the same rule**: `wd && everArmed`. A watchdog
  trip before anything has ever armed is "no Pi connected yet", not a fault.
  Missing this is what made the first attempt still blink after flashing.
- **A light that always cries wolf is not read when it means something** — that
  is the reason, not tidiness.
- **What is never silenced**: a latched `PACK_CUTOFF` (a genuinely flat pack).
  And silencing is LED-only — throttle inhibit, `STBY` and `outputModeFor()`
  are untouched, with SELFTEST assertions saying so, including that a watchdog
  trip still brakes when its blink is suppressed.
- `B` over serial toggles a manual override for the one case history cannot
  cover: a board that HAS seen a real pack and is deliberately benched. Not
  persisted; any reset clears it, and opening the serial port resets the board.
