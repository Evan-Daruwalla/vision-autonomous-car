# Vehicle lighting — spec and consequences

**Status: SPEC ONLY. Nothing ordered, nothing wired, nothing built.**
Requested by Evan 2026-09-01: headlights, tail lights, daytime running lights,
and turn signals.

⚠️ **REWRITTEN 2026-09-03 for the WS2812B architecture (Appendices CX/CY/CZ/DA)
and PRD task 8e's firmware rewrite.** This doc was the last place in the repo
still describing the superseded 4-channel discrete-LED scheme (8 LEDs across
D4-D7, per-LED series resistors) — flagged stale in Appendices DA/DB, fixed
here. The car now uses **two WS2812B strip segments, 3 pixels each** (white
front / red rear / amber indicator, one per side), driven from D4 (left) and
D7 (right) with no PWM and no series resistor per LED. **DRL folds into the
HEAD pixel only, at reduced brightness — never the tail** (Evan, 2026-09-03);
the "headlights + tail lights at reduced brightness" framing above is the
ORIGINAL request and is superseded by that decision. `firmware/uno_control/`
implements this as of 2026-09-03 — compiled clean, **not yet run on real
hardware** (no strip owned).

Every number below marked EST is unmeasured.

---

## 1. What the camera can and cannot see

This is the axis that decides which of these are ML features and which are
decoration. The camera is forward-facing.

| light | in the camera's view? | ML consequence |
|---|---|---|
| **Headlights** | **the BEAM is, on the road ahead** | **changes the input distribution — see §4** |
| Tail lights | no | none. Pure realism |
| Rear turn signals | no | none. Pure realism |
| Front turn signals | the lamps themselves, no; stray amber on the road, marginally | negligible as input; significant as an OUTPUT — see §5 |

**Only the headlights materially affect perception.** Tail lights and rear
indicators are free from the model's point of view — build them for realism and
the portfolio, they cost nothing in risk.

---

## 2. Channels

**SUPERSEDED 2026-09-03 (Appendices CX/CY/DA): two WS2812B strip segments on
plain digital pins, no PWM at all.** The section below (channel-count table,
PCA9685-vs-Uno reasoning) described two earlier architectures in sequence —
a PCA9685, then 4 discrete LEDs on Uno GPIO — both retired the same day
Evan proposed addressable strips ("much easier to wire and mount," Appendix
CX). Kept for the reasoning trail; nothing in it is current.

**Current architecture:**

| segment | pin | pixels | zones |
|---|---|---|---|
| left strip | D4 (`DIN`) | 3 | white front (head+DRL) · red rear (tail) · amber (left indicator) |
| right strip | D7 (`DIN`) | 3 | white front (head+DRL) · red rear (tail) · amber (right indicator) |

Cut **to pixel count, not to length** (Appendix DA) — 3 pixels at the chosen
144 LED/m density spans 21 mm, a plausible headlight cluster on this car.
WS2812B bit-bangs its own timing on a plain digital pin; **no PWM hardware
and no per-LED series resistor are needed** (each pixel has a built-in
constant-current driver). This is why the swap frees 2 of the car's 3
previously-maxed-out PWM pins (D5/D6) rather than adding channels — the
opposite of the table this section used to carry.

**DRL is head-only, not head+tail.** The original request (top of this doc)
asked for "headlights + tail lights at reduced brightness." Evan decided
2026-09-03 to fold DRL into the HEAD pixel alone: the `lights` byte's bit4
(`dim`, `SERIAL_PROTOCOL.md` §2) now scales only the white front pixel; the
red rear pixel is unaffected by that bit. Implemented in
`firmware/uno_control/uno_control.ino`'s `headColor()`/`tailColor()`.

**Retired reasoning, kept for the trail only — PCA9685, then 4-channel Uno
GPIO, both superseded before purchase:** ~~the driver is an ARDUINO UNO, not
a PCA9685 (Appendix BC)~~ — Evan has an Uno R3 clone on hand, $0, also brings
encoder counting and a throttle watchdog. On the Uno the Servo library claims
Timer1, leaving PWM on pins 3, 5, 6, 11: motor + headlights + tail = 3 PWM,
servo on its library, indicators on plain digital pins — **fit with ZERO PWM
spare (Appendix BH)**. Superseded in turn 2026-09-03 by the WS2812B swap
above, which needs no PWM at all. Original PCA9685 reasoning: DonkeyCar's
`pins.py` has only three PWM backends and straight-to-GPIO locks the project
to a Pi; a PCA9685 is a 16-channel I2C LED controller, 2 pins total, built-in
per-channel 12-bit dimming.

---

## 3. Power — off the motor rail, never off the Pi

⚠️ **REWRITTEN 2026-09-03 for WS2812B (Appendix CZ).** The per-pin-current
derivation this section used to carry (8 discrete LEDs, 20 mA vs 10 mA per
pin, provisional series resistors) is moot: WS2812B pixels have a built-in
constant-current driver and draw off the strip's power pin directly, not
through an ATmega I/O pin, so the 200 mA all-I/O / 40 mA per-pin limits that
drove that analysis do not apply here at all.

**Current draw, computed under stated assumptions (Appendix CZ), no strip
owned, nothing bench-verified:**

| case | draw |
|---|---|
| realistic (6 pixels lit, both sides, brightness per §2's provisional levels) | **~80 mA** |
| absolute worst case (6 pixels, full white, 100% brightness — never commanded) | **~360 mA** |
| existing peak (motor stalled + servo) | 840 mA |
| + realistic strip | 920 mA — **2.08 A margin** to the LM2596's 3 A rating |
| + worst-case strip | 1200 mA — **1.8 A margin** |

Either figure leaves comfortable headroom. Feed from the **LM2596 5 V rail**
that already supplies the servo, not from the Pi — unchanged reasoning: the
Pi 5 runs on a 5 V/3 A bank with a 600 mA cap on USB peripherals and a
measured CNN draw of 1.40 A (`docs/research/2026-07-23_power-system.md`), so
strip current belongs on the actuator rail regardless of how small it is,
and it keeps the one-shared-ground star topology unchanged. The USB link to
the Pi is data-only with its 5 V conductor cut, so no strip current can reach
the Pi's bank even by accident.

**No per-LED series resistor.** One data-line resistor (~330-470 Ω) protects
the first pixel's `DIN` from spikes — standard practice, not a current
limiter — added to `docs/WIRING_PROTOSHIELD.md` §2.5 in Appendix DA. Two
things the strip swap adds that the discrete-LED scheme never needed: **bulk
capacitance at the strip feed** (a second 470 µF across the `+5V2`/GND pair
the strip draws from — pixel drivers switch in step, and without local bulk
that step lands on the rail the Uno itself runs from) and a **separate star-
ground leg** for the strip returns, kept off the encoder's return conductor
(both Appendix DA.4).

---

## 4. The headlight trap: a hidden variable in the dataset

`gotchas.md` already says **"Vary LIGHTING across sessions on purpose (real-world
domain randomization); never vary the camera geometry."** Headlights are not
that kind of lighting variation, and the distinction matters:

- **Ambient light varies with the room** and is uncorrelated with the car's
  state. Varying it teaches robustness.
- **The headlight beam is fixed to the car**, so it lands in the same image
  region every frame. Switching between full beam and DRL creates **two visual
  domains that the policy cannot tell apart**, because nothing in the input says
  which mode is active.

Collecting some laps on DRL and some on full beam therefore does the opposite of
domain randomisation: it injects a hidden variable correlated with nothing.

**Rule: pick ONE lighting mode and hold it for the entire dataset AND for
deployment**, exactly as the camera pitch is locked. If both modes are wanted as
a demo, either
  (a) treat the mode as a **logged input** to the policy, or
  (b) collect and train a separate dataset per mode,
and say which was done. Do not mix silently.

Second-order: the beam adds a bright pool in the near field that the sim corpus
does not have. That is fine — M3 trains on real laps, not the sim corpus
(`PRD_ROADMAP.md:306-310`) — but it is one more reason the sim's images and the
car's images are not interchangeable.

---

## 5. Turn signals are a policy OUTPUT, and that is the interesting part

A behavioural-cloning policy predicts `(steer, throttle)`. Turn signals add a
third output: a 3-state indicator (`off` / `left` / `right`). The blink cadence
is firmware; the policy only chooses the state.

**Unlike the stop sign, this IS learnable by plain BC.** `gotchas.md:97` records
that a stop sign is provably unlearnable by plain BC because, stopped at the
line, the image is identical whether to wait or go — the action depends on
history the policy cannot express. An indicator on a **memorised fixed route** is
the opposite: the correct state is a function of *where the car is*, which is
visible in the frame. It is memoryless-learnable for the same reason
`gotchas.md` says traffic lights are.

**What it costs, and this is a real prerequisite:**

1. The teleop rig needs indicator controls (two buttons).
2. **M2's logger must record the indicator state per frame**, alongside steering
   and throttle. Without labels there is no third head. This is a change to the
   M2 dataset schema and must land BEFORE the M3 collection run, not after —
   10-20 laps recorded without indicator labels cannot be relabelled honestly.
3. Evan must indicate consistently while driving, or the labels are noise.

**Recommended framing:** ship indicators as a **multi-task BC head** (steer,
throttle, indicator) if the logger change lands in time; otherwise drive them
from a rule (`indicate when |predicted steer| exceeds a threshold`) and **say
plainly in the write-up that they are rule-driven, not learned**. Both are
defensible. Passing a rule off as a learned behaviour is not.

---

## 6. Track interaction

- **Stop signs, no traffic lights** — confirmed correct, and already the plan's
  design. A stop sign is the M4 world-model showcase precisely because plain BC
  cannot do it; a traffic light would be memoryless-learnable and therefore a
  weaker demonstration, and needs hardware on the track
  (`gotchas.md:97-103`).
- The stop sign must stay **relocatable/removable** — a fixed sign is
  predictable from position alone (Appendix Y.3), which would let the policy
  cheat the very thing the sign is there to test.
- With 9 intersections in track v2, signs are placed on the route's turning
  intersections, and moved between sessions.

---

## 7. Open items

- ~~PCA9685/discrete-LED procurement and channel-fit history~~ **all
  superseded 2026-09-03 by the WS2812B swap (Appendices CX/CY/DA)** — kept
  in §2/§3 for the trail, not repeated here.
- **Nothing is ordered.** BOM row 18: BTF-LIGHTING WS2812B, 1m/144px,
  $11.99, part of the **$402.45** total (`docs/BOM.md`). BLOCKED-ON-EVAN
  with the rest of the order.
- **Firmware: written, not hardware-verified.** `firmware/uno_control/`
  implements the 3-pixel-per-segment layout and the head-only DRL decision
  (PRD task 8e, 2026-09-03) — compiled clean with `arduino-cli`, flash 9680 B
  / SRAM 371 B. **Not flashed, not run on a real board**; no strip is owned.
  SELFTEST has 9 new checks (58 total) whose pass/fail is unknown until Evan
  flashes it.
- **The Appendix CZ interrupt estimate (~0.03% encoder tick loss per pixel
  write, worst case) is still unmeasured on hardware.** The firmware answers
  the "update only between control-loop ticks" half by rate-limiting
  `NeoPixel::show()` to 20 ms in `applyLights()` — see that function's
  comment. First real test is wiring a strip and watching `ticks` count
  cleanly while the indicators blink (`SERIAL_PROTOCOL.md` build order step
  8, per Appendix DA.7).
- Whether indicators become a learned head depends on the M2 logger change
  (§5.2) landing before M3 data collection — unaffected by the strip swap.
- Mounting the lamps is downstream of a chassis nobody has built, and the
  headlight position relative to the camera decides where the beam lands in
  frame — which per §4 is a dataset-defining choice, not a styling one.
  Unaffected by the strip swap: still open.
