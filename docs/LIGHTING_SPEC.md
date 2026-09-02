# Vehicle lighting — spec and consequences

**Status: SPEC ONLY. Nothing ordered, nothing wired, nothing built.**
Requested by Evan 2026-09-01: headlights, tail lights, daytime running lights
(headlights + tail lights at reduced brightness), and turn signals.

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

> **SUPERSEDED 2026-09-02 (Appendix BC): the driver is an ARDUINO UNO, not a
> PCA9685.** Evan has an Uno R3 clone on hand, so the part costs $0 and also
> brings encoder counting and a throttle watchdog, neither of which a PCA9685
> can do. The channel reasoning below still holds — four light channels, two
> needing PWM — and it is what proved a dedicated driver was necessary at all.
> What changed is which driver. On the Uno the Servo library claims Timer1,
> leaving PWM on pins 3, 5, 6, 11: motor + headlights + tail = 3 PWM, servo on
> its library, indicators on plain digital pins. **Fits with one PWM spare.**
> Series-resistor sizing changes too: an Uno pin sources 20 mA and the chip's
> absolute max across ALL pins is **200 mA**, where the PCA9685 sank 25 mA per
> channel independently. See `docs/BOM.md` rows 17-20 and `gotchas.md`.
> The section below is left as written for the reasoning trail.

Minimum channel count:

| channel | needs PWM? | why |
|---|---|---|
| headlights | **yes** | full beam vs dimmed daytime running light |
| tail lights | **yes** | same, dimmed with the DRL |
| left indicator | no (on/off) | blink is generated in firmware, not by varying duty |
| right indicator | no (on/off) | " |

Four new channels, two of them PWM, on top of the existing **1 servo PWM + 2
motor PWM/DIR**.

**This resolves the open BLOCKED-ON-EVAN item "straight-to-GPIO or a PCA9685?"
in favour of the PCA9685.** The reasoning was previously about portability
(DonkeyCar's `pins.py` has only three PWM backends, and straight-to-GPIO locks
the project to a Pi). Lighting makes it a capacity question as well: a PCA9685
is a **16-channel I2C LED controller** that costs **2 pins** total and is
literally designed to drive LEDs at constant current with per-channel 12-bit
dimming. Straight-to-GPIO would need four more pins and has no hardware PWM to
spare for dimming.

Order the PCA9685. It is the same part either way, so this does not add a
decision — it removes one.

---

## 3. Power — off the motor rail, never off the Pi

8 LEDs (2 head, 2 tail, 4 indicator) at ~20 mA each = **~160 mA peak**  EST

Feed from the **LM2596 5 V rail** that already supplies the servo, not from the
Pi. The Pi 5 runs on a 5 V/3 A bank with a **600 mA cap on USB peripherals** and
a measured CNN draw of 1.40 A (`docs/research/2026-07-23_power-system.md`).
160 mA is small, but it belongs on the rail that already exists for actuators,
and it keeps the one-shared-ground star topology unchanged.

Series resistor per LED. ~~The PCA9685 sinks up to 25 mA per channel, which
covers a 20 mA LED directly; anything brighter needs a transistor per channel.~~
**AMENDED 2026-09-02 (Appendix BC), and the limit is tighter than the PCA9685's
was:** an ATmega328P pin sources 20 mA, but the chip's absolute maximum across
**ALL** I/O together is **200 mA** — a shared budget, where the PCA9685's 25 mA
was per channel and independent. 8 LEDs at 20 mA = 160 mA, 80% of the hard
limit; realistically ~120 mA peak (4 lamps steady + 2 indicators blinking).
Workable, but brighter LEDs need MOSFETs off the LM2596 rail rather than pins.

**The rail argument is unchanged and now easier to satisfy:** the Uno's 5 V pin
is fed from the LM2596, so LED current comes off the motor pack either way — and
the USB link to the Pi is data-only with its 5 V conductor cut, so no LED
current can reach the Pi's bank even by accident.

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

- ~~**Nothing is ordered.** The PCA9685, LEDs, resistors and wire are not in
  `docs/BOM.md` yet, and adding them changes the ~$178-181 total.~~
  **CLOSED 2026-09-01 ~21:20 CDT: added as BOM rows 17-20** (PCA9685, 8 LEDs,
  resistors, I2C wire), **~$10.50-24.00**. The "~$178-181" anchor was itself
  stale by ~$60 — the BOM had re-priced to $221.82-$224.82 on 2026-08-08. New
  total **$232-249 before shipping, ≈$247-274 with**. **Nothing is ordered**,
  and the $200 ceiling is now breached on every path including the 2GB Pi
  (≈$202-229 with shipping). BLOCKED-ON-EVAN with the rest of the order.
- **Scope widened 2026-09-01 (Evan):** the PCA9685 carries **motor PWM and the
  servo as well as the four light channels** — 6 of 16 used. That was Appendix
  AH's original argument (DonkeyCar's `pins.py` has a PCA9685 backend, so
  actuation stops being Pi-locked); lighting only made the channel count decide
  it too. The TB6612's two direction pins stay on GPIO — the backend drives PWM,
  not direction logic.
- LED count, colour and forward voltage are unchosen; the 160 mA figure is EST
  at 20 mA per LED.
- Whether indicators become a learned head depends on the M2 logger change
  (§5.2) landing before M3 data collection.
- Mounting the lamps is downstream of a chassis nobody has built, and the
  headlight position relative to the camera decides where the beam lands in
  frame — which per §4 is a dataset-defining choice, not a styling one.
