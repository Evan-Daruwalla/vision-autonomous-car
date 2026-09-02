# Bill of Materials — v1 (2026-07-23)

**Status: FINAL pending Evan's order.** Every choice traces to a dated
research brief in `docs/research/`. Prices are 2026-07-23 and were volatile
this year (Pi RAM shortage) — **re-verify at checkout.**

**Decisions this BOM encodes** (Evan, 2026-07-23 ~20:46 CDT):
Pi 5 **4GB** (down from 8GB, −$25) · **owns a USB power bank**, so the
split-source power path costs almost nothing.

---

## The list

| # | Item | Why this one | Price | Source |
|---|---|---|---|---|
| **Compute + sensing** |
| 1 | Raspberry Pi 5 **4GB** | DonkeyCar's stated minimum; onboard work is inference-only, all training is on the 3060 Ti | **$110.00** ⚠️ *(was $70.00 — see re-pricing note)* | pishop.us $110 / adafruit.com $130 |
| 2 | Camera Module 3 **Wide** | ✅ **HOLD LIFTED 2026-08-13 (Appendix AI): the sim FOV was identified as `fov=90`, i.e. ~106° H / ~118° diagonal, and the Wide (102° H / 120° D) matches within 2-4°. The standard module is ~40° off and would be wrong. Correct part — by luck, since nobody set or checked it.** Superseded warning: The sim's camera FOV/offset/rotation were NEVER SET (`cam_config` absent from every conf dict), so the whole corpus was captured at an unrecorded Unity default. If it differs from this camera's 120°, the encoder trained on a different projection than this part will produce. One short sim run settles it — see `docs/SIM_TRANSFER_SPEC.md` §5.2. Original rationale: ≥120° FOV is the consensus lever for track following; rolling shutter is fine at 1–3 m/s | **$38.50** *(was $35.00)* | pishop.us |
| 3 | **Camera cable, Standard-Mini** | ⚠️ **Camera Module 3 ships with a Standard-Standard cable, which does NOT fit the Pi 5's mini 22-pin connector.** Verified against Raspberry Pi docs 2026-07-23. Without this, nothing works. | **~$2–5** | raspberrypi.com |
| 4 | microSD card, 32GB+, A2/U3 | OS + driving logs | **~$10.00** | any |
| **Drive + steering** |
| 5 | Pololu **#1093** N20 30:1 HP 6V | The only gear ratio that lands in the required 430–1550 rpm band; full spec sheet + CAD envelope | **$23.95** | pololu.com |
| 6 | Pololu **#713** TB6612FNG carrier | MOSFET bridge, ~0.5V drop, 4.5–13.5V. **Parallel both channels** for 2A continuous | **$4.95** | pololu.com |
| 7 | MG90S metal-gear servo | Steering. Metal gears non-negotiable; MG996R is the fallback if it stalls | **~$5.00** | any |
| **Power (split source — bank owned)** |
| 8 | USB power bank, **5V/3A** | → Pi ONLY. **You own this — check the label says 5V/3A** (see Verify below) | **$0.00** | owned |
| 9 | 2× EVE 25P 18650 cells | → motor + servo pack (7.4V). **Buy both from the same order** (matched cells — see caveat) | **$3.70** | 18650batterystore.com |
| 10 | 2-cell 18650 series holder | | **$1.25** | addicore.com |
| 11 | USB-C 2S BMS / charge board | Charges the pack in place from USB-C; provides overcharge, over-discharge and short protection. **No hobby balance charger needed** | **$7.99** | adeept.com |
| 12 | LM2596 buck module | 7.4V → 5.2V for the servo only (700mA peak — well within it). **Not for the Pi** | **$2.48** | addicore.com |
| **Wiring + protection** |
| 13 | XT30 connector pair | | **$1.10** | alofthobbies.com |
| 14 | SPST rocker switch, 10A | Main switch on the motor pack | **$0.75** | sparkfun.com |
| 15 | Inline ATO/ATC fuse holder + 3A fuse | **Mandatory** — unprotected 18650s can deliver enormous short-circuit current | **~$2.15** | bc-robotics.com |
| 16 | Wire, heat-shrink, bulk caps, headers | ~22AWG for motor, ~26AWG signal; 470–1000µF across the motor rail | **~$8.00** | any |
| **Lighting + I/O** |
| 17 | ~~**PCA9685** 16-ch I2C PWM/LED driver~~ **Arduino Uno R3 clone — OWNED** | ✅ **SUPERSEDES the PCA9685 2026-09-02 (Appendix BC).** Evan has an Uno R3 clone on hand: ATmega328P, 5V logic, FTDI FT232RL, working on COM3. It does everything the PCA9685 would (motor PWM + servo + 4 light channels, fits with one PWM pin spare after the Servo library takes Timer1) **plus two things the PCA9685 cannot**: quadrature **encoder counting** on hardware interrupts D2/D3, and a **throttle watchdog** that stops the car if the Pi hangs. ⚠️ **5V logic — connect over USB, NEVER to Pi GPIO** (`gotchas.md`). Cost of the swap: no DonkeyCar backend exists, so the actuator path becomes custom firmware + a serial protocol | **$0.00** | owned |
| 18 | 8× 3mm LEDs (2 white, 2 red, 4 amber) | Headlights, tail lights, 4 indicators. Amber for indicators; rear lamps are never in the forward camera's view, so they are realism at zero ML cost (`docs/LIGHTING_SPEC.md` §1) | **~$1.50–3** | any |
| 19 | LED series resistors | One per LED; value set by the chosen LEDs' forward voltage — see Verify item 5. ⚠️ **Current budget is tight on an Uno:** an ATmega328P pin sources 20mA (one LED) but the chip's ABSOLUTE MAX across all I/O is **200mA**. 8 LEDs at 20mA = 160mA, i.e. 80% of the hard limit. In practice only 4 are on continuously (2 head + 2 tail = 80mA) with 2 indicators blinking (+40mA) = **~120mA peak**, which is fine. If brighter LEDs are chosen, switch them with small N-channel MOSFETs off the LM2596 rail instead of driving pins directly — not currently in this BOM | **~$1–2** | any |
| 20 | Dupont jumpers + **data-only USB cable** | Pi→Uno is **USB, not GPIO** (5V logic would damage the Pi's 3.3V pins). The USB 5V wire must be **cut or omitted**: the Uno's 5V pin is fed from the LM2596 rail so LED current stays off the Pi's bank, and two supplies must not back-feed each other. Plus LED and servo leads | **~$2–4** | any |
| | | **TOTAL** | **≈ $226–234** | |

*(Total corrected 2026-08-06 from "≈$176–179" — the cold audit found it
excluded row 3, the camera cable, i.e. the very item this BOM was written to
catch. Fixed rows sum to $176.32; + $2–5 cable = $178.32–$181.32.)*
*(⚠️ That "2026-08-06" is wrong: this file's mtime is **2026-08-05 23:57 CDT**.
23:57 CDT = 04:57 UTC on 08-06 — the date was stamped in UTC, against the
Central-time rule. Left in place as written; flagged here, not silently edited.)*

*(**TOTAL raised 2026-09-01 ~21:20 CDT from ≈$222–225 to ≈$232–249** by rows
17–20, the lighting and I2C hardware (Appendix AY, `docs/LIGHTING_SPEC.md`).
Recomputed from the rows, not carried forward: rows 1–16 sum to
**$221.82–$224.82**, rows 17–20 add **$10.50–$24.00**, giving
**$232.32–$248.82 before shipping** and **≈$247–274 with the $15–25 shipping
estimate**. The earlier "≈$237–250" figure was the WITH-shipping number for the
old row set — the TOTAL row has always been pre-shipping, so the two were never
in conflict.*
*(~~**The $200 ceiling is now breached on every path, including the 2GB Pi.**
Swapping the Pi 5 4GB for the 2GB at $65 takes the build to **$187–204 before
shipping, ≈$202–229 with**. That was the swap that previously restored the
ceiling; with lighting it no longer does.~~ **SUPERSEDED 2026-09-02.**)*
*(**TOTAL lowered 2026-09-02 ~15:17 from ≈$232–249 to ≈$226–234** (Appendix BC):
row 17's PCA9685 is superseded by an **Arduino Uno R3 clone Evan already owns**,
taking rows 17–20 from $10.50–$24.00 to **$4.50–$9.00**. Recomputed from the
rows, not carried forward: **$226.32–$233.82 before shipping**, **≈$241–259
with** the $15–25 shipping estimate.)*
*(**The $200 ceiling is REACHABLE again at the low end — but only with the 2GB
Pi**, which now lands at **$181–189 before shipping, ≈$196–214 with**. The
bottom of that range clears $200; the top does not. On the 4GB Pi every path is
still over. Evan's call, and nothing is ordered.)*

**⚠️ RE-PRICED 2026-08-08 ~23:03 CDT against live vendor pages — the total rose
≈$44 and the BOM's Pi price was already stale when this file was written.**

| Row | BOM price (dated 2026-07-23) | Live 2026-08-08 | Δ |
|---|---|---|---|
| 1 Pi 5 4GB | $70.00 | **$110.00** (pishop.us) · $130.00 (adafruit.com) | **+$40 to +$60** |
| 2 Camera Module 3 Wide | $35.00 | **$38.50** (pishop.us) | +$3.50 |
| 5 Pololu #1093 | $23.95 | **$23.95** — unchanged, confirmed on pololu.com | $0 |
| 6 Pololu #713 | $4.95 | **$4.95** — unchanged, confirmed on pololu.com | $0 |

Rows 3, 4, 7, 9–16 were **not** re-quoted: they are generic parts with "~"
estimates, and inventing two-decimal precision for them would be false
confidence. Assume they still hold.

**Revised fixed-row sum $219.82; + $2–5 cable = $221.82–$224.82; + $15–25
shipping = ≈$237–250** at pishop pricing, **≈$257–270** if the Pi comes from
Adafruit. The **$200 ceiling in the 2026-07-23 decision gate is now breached**
on the cheapest path.

**The $70 was never a 2026-07-23 price.** Raspberry Pi's own posts:
4GB was **$70 on 2025-12-01**, then **+$15 on 2026-02-02** → $85. So the figure
this BOM recorded as current on 2026-07-23 was **the December 2025 price, ~5½
months superseded at write time.** At least one further rise has happened since
(raspberrypi.com's own buy page now shows 16GB at **$305**, against $205 in
February) — I could not locate that announcement, so the exact current *official*
4GB price is **unverified**; the $110/$130 above are live retail, which is what
checkout actually costs.

**Cheaper Pi variants, live 2026-08-08 (pishop.us): 2GB $65.00 · 1GB $45.00.**
Dropping to 2GB returns the build to ≈$192–205 all-in — but 2GB is **below the
4GB DonkeyCar minimum** this BOM's row 1 cites. That is a real engineering
trade, not a free saving, and it is **Evan's call, not made here.**

**PI RECOMMENDATION 2026-08-12 (`docs/research/2026-08-12_onboard-compute-selection.md`):
switch row 1 to the Pi 5 **2GB at $65.00** (pishop.us, in stock). Same 2.4 GHz
Cortex-A76 silicon, saves **$45**, and it is the only variant Raspberry Pi has
held flat through all three 2025-26 DRAM hikes while the 4GB took every one
(official posts 2025-12-01 / 2026-02-02 / 2026-04-01). **Returns the build to
≈$192-205 all-in.** DonkeyCar's "4GB minimum" is an unjustified recommendation
— its `pi` extra installs tflite-runtime, not TensorFlow, and a 512MB Zero 2 W
already drives autonomously. The 2GB's risk is at `pip install`, fixable with a
temporary swap file, not at runtime. **Evan's call; not applied to row 1.**

**INDEPENDENTLY VERIFIED 2026-08-12 ~07:40 CDT** against live vendor pages by
a second session, because the re-pricing above was authored outside the session
that found it and a breached budget ceiling should not rest on an unattributed
edit. **All six prices confirmed exactly:** Pi 5 4GB $110.00 pishop (in stock)
and $130.00 Adafruit; Camera Module 3 Wide $38.50 pishop (in stock); Pololu
#1093 $23.95; Pololu #713 $4.95; Pi 5 2GB $65.00 pishop (in stock). **The
re-pricing is accurate and the $200 ceiling is genuinely breached.**

**Plus shipping**, which is the real risk: spread across Pololu, Adafruit /
Raspberry Pi, 18650BatteryStore, Addicore, Adeept, Aloft, SparkFun and BC
Robotics this could add **$15–25+**. Consolidating vendors matters more than
shaving item prices — most of the small parts (holder, buck, connectors,
switch, fuse, wire) are generic and can come from whichever single vendor
carries the most of them.

**Already owned, not purchased:** Lego Technic differential, steering
geometry donor parts, wheels/tires, 3D printer + filament, desktop PC
(RTX 3060 Ti), USB power bank, USB-C cable.

**Deliberately deferred, not in this BOM:** IMU (ICM-20948 $20 or BNO055
$35 — only if M4's observation design needs velocity/yaw) · RPLIDAR C1 $99
(chassis reserves the mount; only for a future SLAM milestone) · MG996R
servo (fallback only) · DRV8871 driver (not needed — the numbers say
paralleled TB6612 is enough).

---

## Wiring architecture

```
[USB POWER BANK 5V/3A] --USB-C--> [Raspberry Pi 5 4GB]  ... and nothing else
                                          |
                                          |  USB (DATA ONLY - 5V wire cut)
                                          v
                                    [ARDUINO UNO]  5V logic, FTDI, COM3
                                          |
                    +---------------------+----------------+
                    |  D9 servo    D3/5/6/11 PWM+digital   |  D2/D3 INT
                    |  D7/D8 DIR   -> lights               |  <- encoder
                    v                                      v
[2x 18650 = 7.4V] --fuse--switch--+--> [TB6612FNG] --> [N20 motor] --> Lego diff
   + USB-C BMS board             |       (both channels PARALLELED)
                                 +--> [LM2596 @ 5.2V] --+--> [MG90S servo]
                                                        +--> [UNO 5V pin]
                                                        +--> LED commons

                    [UNO] pin budget, 6 of ~14 usable:
                       D9  servo (Servo lib -> Timer1, kills PWM on 9/10)
                       D3  motor PWM -> TB6612        D5  headlights (PWM)
                       D7/D8 motor DIR -> TB6612      D6  tail lights (PWM)
                       D2  encoder A (INT0)           D11 indicators (digital)
```

**The one rule that matters (amended again 2026-09-02):** **no power path
crosses between the Pi and the motor pack.** As of the Arduino swap, what
crosses is **USB data only** — the 5V conductor is cut, so even the data link
carries no power. Every actuator signal (PWM, direction, servo, lights) now
originates on the Uno, on the motor-pack side. **This is the cleanest the
separation has ever been:** the previous PCA9685 design had ground, SDA, SCL,
a 3.3V logic supply and two direction lines crossing; the Uno design has two
data wires and a shared ground reference.

*(History, kept because the rule was wrong twice. It originally read "they
share **ground only** … Nothing else crosses between them", which was already
self-contradictory — the same paragraph required the ground as a reference "for
the PWM/direction logic", so PWM and direction wires crossed all along. The
2026-09-01 amendment fixed the wording for I2C. The 2026-09-02 Arduino swap
then made the strong version true for the first time.)*

**Why the Uno sits on the motor rail, not on USB power:** its **5V pin** is fed
from the LM2596, so LED current (~120mA peak, see row 19) never touches the
Pi's 5V/3A bank with its 600mA peripheral cap. **Do NOT power it from VIN off
the 7.4V pack** — the pack sags under motor stall, and below ~7V the on-board
AMS1117 drops out and browns the Uno out mid-drive, taking the servo and the
watchdog with it. Feeding the 5V pin bypasses that regulator entirely.

**Why the USB 5V wire must be cut:** with the Uno powered from the LM2596 and
USB plugged in, two 5V supplies meet on one rail and back-feed. A data-only
cable removes the conflict rather than relying on the board's power-select
circuit, which is unverified on a clone.

**Why not one battery:** a simultaneous Pi peak + servo stall + motor stall
draws **4.62A**, which collapses a 3A rail and hard-resets the Pi mid-run
with the SD card mounted. The split is structural, not stylistic.

---

## Verify before ordering

1. **Your power bank's output rating** — the label or spec must say **5V/3A**
   (or 15W). Measured Pi 5 draw under CNN inference is 1.40A, so even a 2.4A
   bank very likely works, but confirm before relying on it. It must also be
   a plain 5V USB-A/C output; you do not need and should not rely on PD.
2. **Which Lego differential you actually have** — 62821 (28-tooth ring) or
   6573 (24/16). This sets the reduction and therefore the mesh centres in
   CAD. Count the teeth.
3. **Which tires** — the part name states the real diameter (44309 = 43.2mm,
   32019 = 62.4mm). Config B (62.4mm + 12t→28t) is the lower-risk drivetrain.
4. ~~**Prices at checkout** — Pi pricing moved twice in three months this year.~~
   **DONE 2026-08-08 ~23:03 CDT** — see the re-pricing table above. Total is
   **≈$237–250**, not ≈$195. Checks 1–3 remain open and are all physical
   inspection; this was the only one of the four that did not need Evan's hands.
   *(Amended 2026-09-01: that "≈$237–250" was the with-shipping figure for the
   pre-lighting row set; it is now **≈$247–274**. And "Checks 1–3 remain open"
   is superseded by the addition of check 5 below — the open set is **1–3 and
   5**. Prices need re-checking again anyway, since rows 17–20 are estimates.)*
5. **Which LEDs** — forward voltage and current set every series-resistor value
   in row 19, and decide whether the Uno can drive them directly (20mA/pin,
   **200mA absolute max across ALL pins** — 8 LEDs at 20mA is 160mA, 80% of
   that hard limit) or whether they need MOSFETs off the LM2596 rail
   or needs a transistor per channel. The **~160mA total is an ESTIMATE** at
   20mA × 8 LEDs (`docs/LIGHTING_SPEC.md` §3); nothing has been measured. Pick
   the LEDs before ordering resistors, not after.

## Caveats carried into the build

- **Matched cells:** the $7.99 BMS board's published protection list covers
  overcharge, over-discharge and short circuit but **does not state per-cell
  balancing**. With two new cells from the same order this is tolerable;
  check them with a multimeter occasionally, and never mix in an older cell.
  (The alternative — an XTAR FC2 at $6.99 charging cells individually —
  eliminates balancing entirely but means pulling cells out to charge and
  leaves the pack with no discharge protection.)
- **Two unverified motor dimensions** — mounting-hole spacing (10 ± 0.2mm,
  single-source) and D-flat depth (unpublished). **Measure both with
  calipers on arrival, before the rear module is committed to CAD.**
- **The printed coupler** must be a socket gripping a *real* Lego axle, never
  a printed axle cross-profile (SF 2–4 in torsion at stall).
- **Weight:** this is the heaviest power option (~320g of battery). If the
  car turns out underpowered, the battery is the first thing to revisit.
