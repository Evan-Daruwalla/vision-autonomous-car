# Pi ↔ Uno serial protocol — DRAFT v0.1 (2026-09-02)

**Status: DESIGN ONLY. No firmware implements this yet.** Drafted after the link
was measured (Appendix BF: p50 0.869 ms, p99 1.069 ms round trip at 20 Hz), so
the sizing below is against real numbers rather than guesses.

The Uno owns everything real-time; the Pi sends a command every 50 ms and reads
back state. Rationale for the split: Appendix BC.

---

## 1. Pin map — CORRECTED

⚠️ **`docs/BOM.md`'s diagram (lines 153, 164) double-books D3**, assigning it to
both the encoder's second interrupt and motor PWM. Found while drafting this.
The map below is the corrected one.

| pin | use | why this pin |
|---|---|---|
| D2 | encoder A | INT0 — one of only two hardware interrupts |
| D3 | encoder B | INT1 — **the other one; nothing else may use D3** |
| D4 | left indicator | digital, on/off — blink is firmware |
| D5 | headlights (PWM) | Timer0 |
| D6 | tail lights (PWM) | Timer0 |
| D7 | right indicator | digital |
| D8 | motor DIR A | → TB6612 AIN1 |
| D9 | steering servo | Servo library, **claims Timer1** |
| D11 | motor PWM | **Timer2** — see below |
| D12 | motor DIR B | → TB6612 AIN2 |
| D13 | status LED | onboard; heartbeat + fault code |

**Motor PWM must be on Timer2 (D11), not Timer0 (D5/D6).** Timer0 also drives
`millis()`, so its frequency cannot be changed without breaking timekeeping —
and motor PWM is the one channel that may need its frequency raised above
~20 kHz to get the whine out of the audible band. Lights never need that, so
they take the frequency-locked Timer0 pins. This is the only pin assignment
here that is forced rather than convenient.

Free after this: A0–A5, D10, plus D0/D1 (the USB UART — **do not use**).

---

## 2. Frame format

Binary, fixed length, sync byte + CRC8. **Not ASCII**, and the reason is the
failure mode rather than speed: at 115200 with a 50 ms budget even 100 ASCII
bytes would cost 8.7 ms, so size is irrelevant. What matters is that a
desynchronised stream must not reach the actuators. A sync byte plus a checksum
lets the Uno *reject* a corrupt frame and fall to a safe state; a line-oriented
ASCII parser silently accepts a truncated number as a valid one.

### Command — Pi → Uno, 7 bytes

| byte | field | type | meaning |
|---|---|---|---|
| 0 | `SYNC` | `0xA5` | frame start |
| 1 | `seq` | uint8 | wraps; lets the Uno spot drops and the Pi match replies |
| 2 | `steer` | int8 | −100…+100, percent of full lock |
| 3 | `throttle` | int8 | −100…+100, percent; negative is reverse |
| 4 | `lights` | uint8 | bit0 head · bit1 tail · bit2 left · bit3 right · bit4 dim (daytime mode) |
| 5 | `flags` | uint8 | bit0 **ARMED** — actuators are inert unless set |
| 6 | `crc8` | uint8 | over bytes 0–5, poly 0x07 |

### Reply — Uno → Pi, 9 bytes

| byte | field | type | meaning |
|---|---|---|---|
| 0 | `SYNC` | `0x5A` | different from the command sync, so a loopback cannot be mistaken for a reply |
| 1 | `seq` | uint8 | echoed — the Pi measures round-trip latency from this |
| 2–5 | `ticks` | int32 LE | cumulative quadrature count, signed, wraps naturally |
| 6 | `status` | uint8 | bit0 armed · bit1 **watchdog tripped** · bit2 last CRC bad · bit3 frame dropped |
| 7 | `loop_dt` | uint8 | firmware loop time in units of 100 µs, saturating — cheap health signal |
| 8 | `crc8` | uint8 | over bytes 0–7 |

**int8 for steer/throttle is deliberate, not lazy.** 200 steps over the range;
the servo resolves maybe 60 discrete positions across its useful travel, so the
quantisation is already an order of magnitude finer than the actuator. *Upgrade
trigger: move to int16 only if a measurement shows steering quantisation is
visible in driving, which it should not be.*

---

## 3. Safety rules — the part that actually matters

1. **ARMED is opt-in every frame.** `flags` bit0 must be set in each command.
   Actuators are inert on boot, after a reset, and after any watchdog trip. Stray
   bytes on a serial port cannot start the car.
2. **Watchdog: 150 ms** (three missed frames at 20 Hz). On expiry the firmware
   **cuts throttle to zero, holds the last steering angle, and flashes both
   indicators as hazards.** Throttle-to-zero is the safety action; *holding*
   steering rather than centring it avoids a jerk at the moment control is lost,
   and hazards make the state visible from across the room.
3. **A bad CRC is a dropped frame, not a guessed one.** The Uno replies with
   `status` bit2 set and takes no actuator action. Two consecutive bad frames
   should be treated by the Pi as a link fault.
4. **The watchdog is SAFETY, not security.** It protects against a hung Pi or a
   diverging policy. It does nothing against something else writing valid frames
   to the port (`security.md`).

---

## 4. Budget check against measured numbers

| item | measured / computed | share of the 50 ms step |
|---|---|---|
| round trip, 4-byte exchange at 20 Hz | **p99 1.069 ms** (BF) | ~2% |
| 7 + 9 bytes at 115200 | 1.39 ms wire time | ~3% |
| worst single sample observed | 5.753 ms | ~12% |

Comfortable. **But the measurement is Windows-to-Uno on one cable**, and the
mechanism that produces 0.9 ms against a configured 16 ms FTDI latency timer is
**not understood** (BF.3). **Re-measure on the Pi before relying on it.**

RAM cost is negligible: two 16-byte frame buffers plus an int32 counter, against
**1705 bytes free** (BE.2).

---

## 5. Debuggability

One ASCII escape hatch: a lone `?` (0x3F) outside a frame makes the Uno print a
human-readable status line. Costs one branch, and means the board can be
inspected from any serial terminal without a decoder. `?` is not a valid sync
byte, so it cannot collide with a frame.

---

## 6. Open

- **Not implemented.** No firmware, no Pi-side client.
- Encoder counts-per-revolution unknown until the motor is in hand — `ticks` is
  raw counts, and conversion to distance is the Pi's job, not the Uno's.
- Whether `throttle` maps linearly to PWM duty or through a calibration curve is
  undecided and belongs in firmware, not in this protocol.
- No provision for streaming telemetry faster than the command rate; if the
  encoder ever needs finer sampling than 20 Hz, that is a v0.2 change.
