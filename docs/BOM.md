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
| 1 | Raspberry Pi 5 **4GB** | DonkeyCar's stated minimum; onboard work is inference-only, all training is on the 3060 Ti | **$70.00** | raspberrypi.com / any reseller |
| 2 | Camera Module 3 **Wide** | ≥120° FOV is the consensus lever for track following; rolling shutter is fine at 1–3 m/s | **$35.00** | raspberrypi.com |
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
| | | **TOTAL** | **≈ $176–179** | |

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
4. **Prices at checkout** — Pi pricing moved twice in three months this year.

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
