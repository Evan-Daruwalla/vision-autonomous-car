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
| | | **TOTAL** | **≈ $222–225** | |

*(Total corrected 2026-08-06 from "≈$176–179" — the cold audit found it
excluded row 3, the camera cable, i.e. the very item this BOM was written to
catch. Fixed rows sum to $176.32; + $2–5 cable = $178.32–$181.32.)*
*(⚠️ That "2026-08-06" is wrong: this file's mtime is **2026-08-05 23:57 CDT**.
23:57 CDT = 04:57 UTC on 08-06 — the date was stamped in UTC, against the
Central-time rule. Left in place as written; flagged here, not silently edited.)*

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
                                          |  GND (single fat wire, star point at driver)
                                          |  + GPIO: PWM/DIR to driver, PWM to servo
                                          v
[2x 18650 = 7.4V] --fuse--switch--+--> [TB6612FNG VM] --> [N20 motor] --> Lego diff
   + USB-C BMS board             |          (both channels PARALLELED)
                                 +--> [LM2596 @ 5.2V] --> [MG90S servo]
```

**The one rule that matters:** the Pi and the motor pack share **ground
only** — one wire, star-grounded at the driver. That reference is required
for the PWM/direction logic. Nothing else crosses between them.

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
