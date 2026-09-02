# firmware/ — Arduino Uno

The Uno owns everything real-time (Appendix BC, `.claude/codebase-memory/architecture.md`):
motor PWM, steering servo, the four light channels, encoder counting on D2/D3,
and a throttle watchdog. The Pi does vision and policy at 20 Hz and sends
commands over **USB serial**.

## Board facts, verified 2026-09-02 not assumed

- Uno R3 **clone**: ATmega328P, device signature `1E 95 0F`, **F_CPU 16000000**
- **FTDI FT232RL** USB bridge (`VID_0403 PID_6001`), enumerates as **COM3**
- Bootloader: STK500 v1, HW 3 / FW 4.4 — stock Uno bootloader, uploads fine
- **5V logic — connect over USB, NEVER to the Pi's 3.3V GPIO** (`gotchas.md`)
- `arduino-cli` ships inside the IDE and does not need a separate install:
  `~/AppData/Local/Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe`

`arduino-cli board list` reports the board as **Unknown with no FQBN** — normal
for an FTDI clone, whose bridge carries no Arduino vendor ID. **Always pass
`--fqbn arduino:avr:uno` explicitly.**

## Build and upload

```
CLI="$HOME/AppData/Local/Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe"
"$CLI" compile --fqbn arduino:avr:uno firmware/uno_bringup
"$CLI" upload -p COM3 --fqbn arduino:avr:uno firmware/uno_bringup
```

## uno_bringup — why it is not stock Blink

Clones frequently ship with the factory Blink already flashed, so a 1 Hz LED
proves nothing about whether YOUR upload landed. This sketch is unambiguous two
ways: a **3-fast-blinks-then-pause** pattern, and a **serial banner + tick
counter** at 115200, so the result is READ rather than eyeballed.

Verified output 2026-09-02:

```
UNO-BRINGUP-OK build=2026-09-02 pattern=3fast+pause
F_CPU=16000000
tick 0
```

## Not done

- **No control firmware exists.** The serial protocol is designed on paper only.
- **The FTDI latency timer (default 16 ms) is UNMEASURED** and sits on the 20 Hz
  control path, whose whole budget is 50 ms per step. Measure before trusting
  the loop rate.
