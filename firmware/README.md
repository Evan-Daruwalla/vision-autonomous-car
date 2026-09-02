# firmware/ — Arduino Uno

The Uno owns everything real-time (Appendix BC, `.claude/codebase-memory/architecture.md`):
motor PWM, steering servo, the four light channels, encoder counting on D2/D3,
and a throttle watchdog. The Pi does vision and policy at 20 Hz and sends
commands over **USB serial**.

## Board facts, verified 2026-09-02 not assumed

- Uno R3 **clone**, 2 KB SRAM **measured** (`RAMEND 0x8FF`, 1705 B free with a
  small sketch, 1472 B obtainable by malloc)
- **Clock MEASURED at 16.0042 MHz (+0.026%)** by timestamping serial beacons on
  the host. `F_CPU` is a build constant and proves nothing — this had to be
  measured because avrdude's signature is shared with the LGT8F328P, which runs
  at 32 MHz (Appendix BE)
- ⚠️ **The signature is ambiguous and the two reads DISAGREE:** avrdude says
  `1E 95 0F` (328P), the silicon's own row says `1E 95 16` (**328PB**). optiboot
  hardcodes what it reports, so the in-app read is the more direct evidence.
  **Treat it as 328P-family; do not use PB-only peripherals**
- **FTDI FT232RL** USB bridge (`VID_0403 PID_6001`), enumerates as **COM3**
- Bootloader: STK500 v1, HW 3 / FW 4.4 — stock Uno bootloader, uploads fine
- **Opening the serial port RESETS the board.** Timing comparisons must
  timestamp on the HOST and use deltas; board uptime vs a host stopwatch gives
  nonsense (it produced a bogus 0.54x clock ratio before this was understood)
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
- ~~The FTDI latency timer (default 16 ms) is UNMEASURED~~ **MEASURED
  2026-09-02 (Appendix BF): it does NOT threaten the loop.** Registry
  `LatencyTimer` is indeed 16, but the real round trip at the actual control
  shape (4-byte command -> 4-byte reply, 20 Hz, 400 exchanges) is **p50 0.869 ms,
  p95 0.956 ms, p99 1.069 ms, max 5.753 ms, zero failures** — nothing above
  10 ms, so ~2% of the 50 ms budget at p99. `firmware/uno_echo` is the harness.
