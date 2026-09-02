# Pi ↔ Uno serial protocol — DRAFT v0.1 (2026-09-02)

**Status: IMPLEMENTED 2026-09-02 (Appendix BO) — `firmware/uno_control/`, with
`firmware/host_test.py` as the Pi-side exerciser. Verified ON THE REAL BOARD:
firmware SELFTEST 37/37, host_test 11/11, exit 0. ACTUATORS ARE UNWIRED — the
link and the state machine are tested; no motor, servo, encoder, LED or pack
exists. Bumped to v0.2 by the status-bit extension in §2.**
~~Status: DESIGN ONLY. No firmware implements this yet.~~ Drafted after the link
was measured (Appendix BF: p50 0.869 ms, p99 1.069 ms round trip at 20 Hz), so
the sizing below is against real numbers rather than guesses.

The Uno owns everything real-time; the Pi sends a command every 50 ms and reads
back state. Rationale for the split: Appendix BC.

---

## 1. Pin map — CORRECTED

The map below is the corrected one. **`docs/BOM.md`'s diagram used to double-book D3** — assigning it to both the encoder's second interrupt and motor PWM — which this draft caught; **both files were fixed in the same commit (590f765)**, so neither double-books it now. (The original wording here said BOM.md *currently* double-books D3, which was false the moment it was committed.)

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
| D10 | **TB6612 `STBY`** — master driver enable | added 2026-09-02, Appendix BL. Its PWM is already dead (Servo owns Timer1), so it is the cheapest free pin; spending it here keeps A1–A5 for future analog (motor current sense) |
| D11 | motor PWM | **Timer2** — see below |
| D12 | motor DIR B | → TB6612 AIN2 |
| D13 | status LED | onboard; heartbeat + fault code |

**Motor PWM must be on Timer2 (D11), not Timer0 (D5/D6).** Timer0 also drives
`millis()`, so its frequency cannot be changed without breaking timekeeping —
and motor PWM is the one channel that may need its frequency raised above
~20 kHz to get the whine out of the audible band. Lights never need that, so
they take the frequency-locked Timer0 pins. This is the only pin assignment
here that is forced rather than convenient.

Free after this: ~~A0–A5~~ **A1–A5** ~~and D10~~, plus D0/D1 (the USB UART — **do
not use**). **D10 became `STBY` on 2026-09-02**, so the only free pins left are
the five analog ones. **A0 is the pack-sense divider input** as of 2026-09-02
(`firmware/uno_packguard/`, Appendix BJ) — corrected in BK.

### 1a. `STBY` — the gap this map had until 2026-09-02

**The map above had no `STBY` line, and neither did `docs/BOM.md`. As written,
the car could not have moved.** Pololu's #713 page is explicit: *"The STBY pin is
pulled low internally, putting the TB6612FNG into a low-power sleep mode by
default, and must be driven high (2.7 V – 5.5 V) in order to enable the driver."*
An unwired `STBY` is not a degraded mode; it is a dead motor, and it would have
presented as a mystery bring-up failure with correct-looking PWM on a scope.

**It is on a GPIO rather than tied to 5 V, and that is the load-bearing choice.**
All three existing safety mechanisms — the per-frame ARMED bit, the 150 ms
watchdog, and `uno_packguard`'s latched cutoff — act through **one** code path:
writing D11. A stuck Timer2 register, a runaway `analogWrite`, or a firmware
hang after the timer is loaded defeats all three at once. `STBY` gives them a
second, *hardware* path that removes the bridge outputs no matter what the PWM
and DIR pins are doing. One pin for an independent shutdown path is cheap.

**Two behaviours that are easy to get backwards** (Toshiba truth table, via the
SparkFun hookup guide — the Pololu page does not reproduce it):

| IN1 | IN2 | PWM | mode |
|---|---|---|---|
| H | H | H/L | **short brake** |
| H | L | H | CW |
| H | L | **L** | **short brake** |
| L | H | H | CCW |
| L | H | **L** | **short brake** |
| L | L | H | **stop — outputs OFF (coast)** |

1. **`analogWrite(D11, 0)` with a direction set is a BRAKE, not a coast.** So
   "cut throttle to zero" already stops the car actively. That is the behaviour
   we want from the watchdog and the pack cutoff, and it happens to be what the
   current design does — but by accident, not by decision, so record it here.
2. **`STBY` LOW is a COAST, not a stop.** High-Z outputs; the car rolls on. So
   `STBY` is a *disable*, never the stop action. Order matters:
   **brake first (PWM 0 with DIR held), then drop `STBY`** once stopped.

**Fail-safe on reset is free, and it closes a known trap.** The Uno's pins are
high-Z until `setup()` runs, and the carrier's internal pull-down then holds
`STBY` low, so the driver is disabled through every reset. This matters because
**opening the serial port resets the board** (`gotchas.md`) — so the Pi
connecting can no longer leave an enabled bridge on an unattended car. Tying
`STBY` to 5 V would have thrown that away. Firmware must therefore drive D10
high only *after* the first valid ARMED frame, never in `setup()`.

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
| 6 | `status` | uint8 | bit0 armed · bit1 **watchdog tripped** · bit2 last CRC bad · bit3 frame dropped · **bits 4–5 pack state (v0.2)** |
| 7 | `loop_dt` | uint8 | firmware loop time in units of 100 µs, saturating — cheap health signal |
| 8 | `crc8` | uint8 | over bytes 0–7 |

**Status bits 4–5 are a v0.2 addition** (2026-09-02) carrying `PackState`
(0 OK · 1 WARN · 2 CUTOFF · 3 FAULT). Without them the Pi cannot tell *"throttle
is dead because the pack is flat"* from *"throttle is dead because I stopped
sending"* — identical symptom, opposite fix, and the operator debugs the wrong
one. Bits 6–7 remain free.

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
4. **`STBY` is dropped on every safe state, after the brake.** Disarm,
   watchdog trip, latched pack cutoff and boot all end with D10 LOW. Re-arming
   requires a valid ARMED frame; a latched cutoff cannot be re-armed at all
   without a power cycle. See §1a for why brake-then-coast and not coast alone.
5. **The watchdog is SAFETY, not security.** It protects against a hung Pi or a
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

- ~~**Not implemented.** No firmware, no Pi-side client.~~ **Both exist as of
  2026-09-02** — `firmware/uno_control/` and `firmware/host_test.py`.
- **Nothing is wired.** The link and state machine are verified on the board;
  every actuator path is verified only as a DECISION the firmware made.
- **The encoder SIGN is unresolved.** `ENCODER_SIGN` in `uno_control.ino` is a
  convention, not a measurement — flip it when the car rolls forward and
  `ticks` go down. A SELFTEST that asserted a direction was the bug that
  surfaced this.
- **`packguard.h` is a COPY** of the tested `uno_packguard` logic. Promote to a
  real library the moment either copy changes.
- Encoder counts-per-revolution unknown until the motor is in hand — `ticks` is
  raw counts, and conversion to distance is the Pi's job, not the Uno's.
- Whether `throttle` maps linearly to PWM duty or through a calibration curve is
  undecided and belongs in firmware, not in this protocol.
- No provision for streaming telemetry faster than the command rate; if the
  encoder ever needs finer sampling than 20 Hz, that is a v0.2 change.
