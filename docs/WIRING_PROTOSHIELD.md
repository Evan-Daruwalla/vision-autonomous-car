# Proto-shield wiring — the buildable schematic

**Status: DESIGN, nothing is built and nothing is ordered.** Written
2026-09-02 ~17:30 CDT. This is the point-to-point net list for an **Arduino
proto shield** carrying every connection between the Uno, the TB6612, the
motor/encoder, the servo, the lights and the pack.

**It is deliberately not a PCB.** Not one component in this document has ever
been in Evan's hands — no TB6612, no LM2596, no MG90S, no N20, no encoder. A
board laid out now is a board laid out against datasheet drawings. Writing the
net list first cost nothing and **found four defects** (§4), any one of which
would have shipped into a PCB rev-1 and cost a two-week respin. When this
document has been built and driven, it becomes the verified schematic a PCB
gets spun from — see §7 for exactly what changes at that point.

Companion docs: pin map + protocol `firmware/SERIAL_PROTOCOL.md` · parts and
prices `docs/BOM.md` · light channels `docs/LIGHTING_SPEC.md` · power
architecture `docs/research/2026-07-23_power-system.md`.

---

## 1. What sits on the shield

| # | On the shield | Notes |
|---|---|---|
| 1 | Pololu #713 TB6612FNG carrier | soldered on 0.1" header, **not** flying leads |
| 2 | LM2596 buck module @ 5.2 V | module, wired in — has its own trim pot, set it BEFORE connecting anything |
| 3 | SPST rocker switch (or its leads to a panel mount) | switches the pack, not the Pi |
| 4 | 470–1000 µF electrolytic + 0.1 µF ceramic | across VM/GND, physically at the TB6612 |
| 5 | 8 × LED series resistors | one **per LED**, never one per channel — see §4.2 |
| 6 | Pack-sense divider: 100 kΩ + 12 kΩ | ratio 0.10714, per `firmware/uno_packguard/` |
| 7 | Screw terminals or JST for every off-board lead | motor+encoder, servo, 8 LEDs, pack |

**Zero flying Dupont jumpers is the point of the exercise.** Dupont crimps back
out under vibration, and this vehicle vibrates. Every off-board connection
lands in a screw terminal or a latching connector.

---

## 2. Net list

Signal wire ~26 AWG; motor and pack wire ~22 AWG (`BOM.md` row 16).

### 2.1 Pack and power distribution

| Net | From | To | Wire | Notes |
|---|---|---|---|---|
| `PACK+` | 2S holder + | 3 A ATO fuse holder | 22 | **Fuse at the pack terminal, before anything else** — it protects the harness, so it goes at the source |
| `PACK+F` | fuse out | XT30 male | 22 | disconnect point |
| `PACK+SW` | XT30 female | rocker switch | 22 | on the shield |
| `VBAT` | rocker out | TB6612 `VMOT`, LM2596 `VIN+`, divider top | 22 | the switched 7.4 V rail |
| `+5V2` | LM2596 `VOUT+` | Uno `5V` pin, servo V+, LED resistor commons, encoder `Vcc` | 22 | **set the trim pot to 5.20 V with the module unloaded before connecting anything** |
| `GND` | see §3 | — | 22 | single star point |

> ⚠️ **The Uno is fed at its `5V` pin, which BYPASSES the onboard regulator and
> its reverse-protection.** 5.2 V is inside spec; anything above ~5.5 V kills
> the ATmega. Meter the LM2596 output before it ever touches that pin. Do not
> connect the LM2596 to `VIN`.

> ⚠️ **The USB cable to the Pi must have its 5 V conductor cut** (`BOM.md`
> row 20). With the shield feeding the Uno's 5V pin, an intact USB 5 V wire
> back-feeds the Pi's bank into the LM2596 rail — two supplies fighting.

### 2.2 Motor — TB6612, both channels paralleled

| Net | Uno pin | TB6612 | Notes |
|---|---|---|---|
| `M_PWM` | **D11** | `PWMA` **and** `PWMB` bridged | Timer2. One pin drives both channels |
| `M_DIR1` | **D8** | `AIN1` **and** `BIN1` bridged | |
| `M_DIR2` | **D12** | `AIN2` **and** `BIN2` bridged | |
| `M_STBY` | **D10** | `STBY` | **§4.1 — this net did not exist until 2026-09-02** |
| `VCC` | Uno `5V` | `VCC` | logic supply, 2.7–5.5 V |
| — | — | `AO1` + `BO1` bridged → motor M1 | output side of the parallel |
| — | — | `AO2` + `BO2` bridged → motor M2 | |

**Paralleling is forced, not tidy.** There is zero spare PWM on this Uno
(`SERIAL_PROTOCOL.md` §1), so the B channel *cannot* be driven independently —
the inputs must be bridged. Pololu states the 2 A paralleled rating but **does
not document the pin pairing**; the pairing above is standard practice and is
**unverified against the Toshiba datasheet — confirm before soldering.**

Motor: Pololu #1093 stall 1.6 A vs 2 A paralleled continuous, duty capped
~71 % of a full 8.4 V pack. Add **0.1 µF across the motor terminals** for brush
noise; it is not in `BOM.md` row 16 and should be.

### 2.3 Encoder — Pololu #5159, 6-pin JST SH

Verified against pololu.com/product/5159 on 2026-09-02.

| JST pin | Colour | Function | Goes to |
|---|---|---|---|
| 6 | red | motor M1 | TB6612 `AO1`+`BO1` |
| 5 | black | motor M2 | TB6612 `AO2`+`BO2` |
| 4 | blue | encoder `Vcc` | **`+5V2` — see the warning below** |
| 1 | green | encoder `GND` | star ground |
| 3 | yellow | channel A | Uno **D2** (INT0) |
| 2 | white | channel B | Uno **D3** (INT1) |

> ⚠️ **Encoder `Vcc` MUST come from the 5.2 V rail, never from `VBAT`.** The
> encoder accepts 2.7–18 V, so 7.4 V would work *for the encoder* — and would
> then swing its outputs to 7.4 V into the Uno's 5 V-max input pins. This is a
> silent way to destroy the board. The outputs are pulled to `Vcc` through
> internal 10 kΩ resistors, so **no external pull-ups are needed.**

12 CPR at the motor shaft × 29.86:1 ≈ **358 counts per output-shaft
revolution.** JST SH is 1.0 mm pitch and not hand-solderable to 0.1"
protoboard — buy Pololu's mating cable and solder its far end to the shield.

### 2.4 Steering servo (MG90S)

| Wire | To |
|---|---|
| signal (orange/white) | Uno **D9** |
| V+ (red) | `+5V2` |
| GND (brown/black) | star ground |

Servo peak ~700 mA. Its return current must not share a conductor with the
encoder return (§3).

### 2.5 Lights

Each channel drives **two** LEDs in parallel, each through **its own**
resistor, sourcing from the pin to the LED anode; cathodes to star ground.

| Net | Uno pin | Load | Type |
|---|---|---|---|
| `L_HEAD` | **D5** | 2 × white | PWM (Timer0) — dimmable for daytime mode |
| `L_TAIL` | **D6** | 2 × red | PWM (Timer0) |
| `L_IND_L` | **D4** | 2 × amber | digital, blink in firmware |
| `L_IND_R` | **D7** | 2 × amber | digital |

**Resistor sizing, at 10 mA per LED — not 20 (see §4.2):**
`R = (5.0 − Vf) / 0.010`

| LED | Vf assumed | R computed | nearest E12 |
|---|---|---|---|
| white | 3.1 V | 190 Ω | **200 Ω** |
| red | 2.0 V | 300 Ω | **300 Ω** |
| amber | 2.1 V | 290 Ω | **300 Ω** |

⚠️ **These `Vf` figures are placeholders.** `BOM.md` Verify item 5 — *which
LEDs* — is still open and unanswered, and `Vf` is the only input to this table.
**Recompute from the real datasheet before buying resistors.**

### 2.6 Pack sense

| Net | From | To |
|---|---|---|
| divider top | `VBAT` (**after** the switch) | 100 kΩ |
| `A0` | 100 kΩ / 12 kΩ junction | Uno **A0** |
| divider bottom | 12 kΩ | star ground |

Tapping **after** the rocker means the divider stops drawing (≈75 µA at 8.4 V)
when the car is off, and a blown fuse reads 0 V → `FAULT`, which
`uno_packguard` already handles correctly and distinctly from `CUTOFF`.

---

## 3. Ground

**One star point, at the TB6612's `GND` pad.** Everything returns there
individually: pack negative, LM2596 `VOUT−`, Uno `GND`, servo GND, encoder GND,
all 8 LED cathodes.

The rule that matters: **the encoder return must not share a conductor with the
motor, servo, or LED returns.** Motor current is the noisiest thing on the
vehicle and the encoder is the one signal whose corruption is invisible —
counts are just wrong, and `ticks` is the car's only odometry. Give the encoder
its own return leg to the star point.

---

## 4. Four defects this exercise found

Written out because they are the entire justification for doing the net list
before the board.

**4.1 `STBY` was missing from every document.** The pin map and `BOM.md` both
omitted it. Pololu: *"The STBY pin is pulled low internally … must be driven
high (2.7 V – 5.5 V) in order to enable the driver."* As specified, the car
could not have moved, and it would have presented as a mystery bring-up
failure with correct-looking PWM on a scope. Fixed 2026-09-02 → **D10**.
Rationale for a GPIO rather than a 5 V tie is in `SERIAL_PROTOCOL.md` §1a: it
gives the three existing safety mechanisms a hardware path independent of D11.

**4.2 The LED current budget is wrong per-pin, and nobody noticed because the
chip-total was right.** `LIGHTING_SPEC.md` computes 8 × 20 mA = 160 mA against
the ATmega328P's 200 mA all-pin limit and calls it 80 % — true, but it is the
wrong limit. There are **4 channels driving 2 LEDs each**, so at 20 mA per LED
each *pin* sources **40 mA** — the ATmega328P's *absolute maximum* per I/O pin,
with a 20 mA recommended figure. The spec inherited its per-channel reasoning
from the PCA9685, which sank 25 mA per channel independently, and was only
partly rewritten for the Uno. **Fix: run the LEDs at 10 mA** (20 mA/pin, in
spec; 80 mA chip total, 40 % of the limit). 3 mm LEDs at 10 mA are plainly
bright. No MOSFETs needed — `BOM.md` row 19's transistor fallback stays unbuilt.

**4.3 `BOM.md` row 5 contradicts a decision Evan made on 2026-08-12.** The
record (Appendix O, and again at three later points) has him choosing the
**encoder** motor, **#5159 at $29.95**. Row 5 still lists **#1093 at $23.95**,
a motor with no encoder — while the pin map has spent D2 and D3 on encoder
interrupts and this net list wires six encoder conductors. **The BOM buys a
motor that cannot feed the firmware that has been designed around it.** Not
changed here: it moves the total (+$6) and purchases are Evan's call.

**4.4 The motor/encoder connector is not hand-solderable.** 6-pin JST SH at
1.0 mm pitch does not mate with 0.1" protoboard. Needs Pololu's cable, which is
not a `BOM.md` line item.

---

## 5. Build order, with the check that gates each step

Nothing proceeds to the next row until the check passes.

| # | Do | Check before continuing |
|---|---|---|
| 1 | Set LM2596 to 5.2 V, **unloaded, nothing else connected** | meter reads 5.15–5.25 V |
| 2 | Solder pack path: fuse, XT30, rocker, star ground | continuity; **switch off = 0 V downstream** |
| 3 | Fit divider, wire A0, flash `uno_packguard` | `SELFTEST` 27/27, then `REAL` reports pack voltage within 0.1 V of the meter |
| 4 | Solder TB6612 + caps, including `STBY` to D10 | with D10 low, motor terminals high-Z; with D10 high and PWM 0, they short-brake |
| 5 | Motor + encoder | drive at 20 % duty both directions; `ticks` counts up one way, down the other, ≈358 per output rev by hand |
| 6 | Servo | sweeps full travel without buzzing at the ends; check the 5.2 V rail does not sag below 4.8 V at peak |
| 7 | LEDs | all 8 light; measure one channel's pin current ≤ 20 mA |
| 8 | Full-load rail check | motor stalled + servo moving + all lights on: 5.2 V rail holds, Uno does not reset |

Step 8 is the one that finds the LM2596 undersized if it is. Record the
measurements — this table is portfolio material, not ceremony.

---

## 6. Open

- **Which LEDs** (`BOM.md` Verify item 5) — gates every resistor in §2.5.
- **Row 5 motor**, §4.3 — gates whether §2.3 is wired at all.
- **TB6612 parallel pin pairing** unverified against Toshiba, §2.2.
- **LM2596 module current rating** unverified for the specific Addicore part;
  §2 loads sum to ≈840 mA peak.
- **`STBY` in firmware.** `SERIAL_PROTOCOL.md` §1a and rule 4 specify the
  behaviour; nothing implements it, because nothing implements the protocol.
- Shield footprint is 68.6 × 53.4 mm against a **measured 114.75 mm car
  width** — it fits, but it is 60 % of the width and the stack height is
  unbudgeted against the camera mount.

---

## 7. What changes if this becomes a PCB

Everything above is footprints and nets already. A rev-1 would add: the TB6612
as a bare IC rather than a carrier (saves ~15 mm of height), proper 2 oz copper
pours for the motor path, the star ground as an actual plane stitch point, and
polarised connectors that cannot be inserted backwards — which is the one real
safety gain a board buys over a shield.

**Spin it after §5 step 8 passes, not before.** The defect list in §4 is four
items long and this design has never been powered; the honest expectation is
that building it finds more. Those belong in rev-1, not in rev-2.
