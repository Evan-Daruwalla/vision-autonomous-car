# Research Brief — Power System

**Date:** 2026-07-23
**Question:** What complete power solution — battery, charger, regulation,
wiring — should the car use, given that Evan owns no battery and no charger,
a tight budget, and that a 17-year-old will be charging cells at home?
**For:** Evan (purchase decision) and any model executing PRD M1.1c.
**Method:** One Opus research worker with a pre-registered rubric. Reviewer
verified the pivotal claim against the official Raspberry Pi documentation,
re-derived the entire runtime and peak-current calculation chain, and
cross-checked the worker's motor assumptions against the now-selected motor
(see Verification). **Nothing has been built or measured** — every figure is
someone else's measurement or a stated assumption.

---

## TL;DR (verdict first)

1. **The Pi 5 does not need 5 A for this workload.** Official docs allow
   "5 V at 3 A with a 600 mA peripheral limit," and the *only* documented
   consequence of a 3 A supply is that USB-port current cap. **This build
   has zero USB peripherals**, so the cap is irrelevant. Measured draw
   during CNN inference on a Pi 5 is **1.40 A**; all-core stress is ~1.76 A.
   This reopens cheap 5 V/3 A sources, including USB power banks.
2. **Recommended: split source.** A USB power bank feeds the Pi alone; a
   separate 2S pack feeds the motor and servo. The single shared connection
   is ground.
3. **The safety argument is the main reason, not cost.** This is the only
   path where the lithium in the house is a **UL/ETL-listed consumer
   product with an integrated BMS, charged from a phone charger** — no
   hobby balance charger, no fireproof bag, no attended-charging rule.
4. **One power bank for everything does NOT work.** A simultaneous Pi peak
   + servo stall + motor stall demands **~4.6 A on a 3 A rail** — the bank
   current-limits, the rail collapses, and the Pi hard-resets mid-run with
   the SD card mounted. Do not let anyone "simplify" the design this way.
5. **Budget verdict: nothing safe fits the ~$22 that was left.** The
   cheapest complete, safe power system is **~$26 on its own**, before the
   motor. **The Pi 5 8GB → 4GB downgrade (−$25) is now recommended by the
   power research as well.**
6. **Everything hinges on one unknown: does Evan already own a USB power
   bank?** If yes, the recommended path costs **$15.42** and is both the
   safest and the cheapest available. If no, it is $33–41.

---

## The pivotal answer: real Pi 5 current draw

**No, this workload does not need 5 A.** Measured evidence, all accessed
2026-07-23:

| Source | Workload | Method | Result |
|---|---|---|---|
| arXiv 2506.09300 | **YOLOv4-Tiny FP32 CNN inference on Pi 5** | USB inline meter | **5.09 V × 1.40 A = 7.13 W** |
| arXiv 2506.09300 | Same, INT8 quantized | USB inline meter | 5.13 V × 0.78 A = 4.00 W |
| CNX Software | `stress -c 4` (all cores) | wall meter | 8.8 W (≈1.76 A) |
| CNX Software | headless, WiFi, idle | wall meter | 3.0 W |
| RPi forum t=371450 | `stress --cpu 4` | inline | ~1.5 A @ 5.1 V |
| bret.dk | idle / typical / Ollama / Linpack peak | wall meter | 4.84 / 6.5 / 10.8 / **11.6 W** |

The closest published match to this project's workload is the arXiv paper —
Pi 5 running CNN inference, **1.40 A measured**, *with a display attached*.
Headless with a CSI camera it will be at or below that.

**Data-quality flag:** that paper's *abstract* claims 13.85 W average, which
its own Section IV-B measurement (4.00 W) contradicts. Use the section
figures, not the abstract.

**Three distinct under-spec behaviours, which get conflated in forum lore:**
1. **Boot warning only** (3 A supply, voltage adequate): "Power to
   peripherals will be restricted", USB capped at 600 mA, **CPU
   unaffected**. Harmless here.
2. **Undervoltage → throttle**: only when the rail actually sags below
   ~4.64 V. Triggered by *measured* voltage, not by the PSU's negotiated
   rating.
3. **Brownout → hard shutdown**: rail collapses (cable resistance, or a
   motor stall on a shared rail). Red LED, instant power-off, SD-corruption
   exposure.

**Design consequence: the constraint moves from amperage to transient rail
stiffness.** A documented case had a Pi 5 shutting down at only ~1.5 A
because of voltage drop in "5 A-rated" USB-C cables — the delivery path
mattered more than the supply label.

## Runtime and peak current

**Assumptions** (all challengeable): Pi + camera 7.0 W average; Pi peak
11.6 W = 2.32 A; MG90S 30% moving at 200 mA / 70% holding at 10 mA, 700 mA
stall (ProtoSupplies *measured*); 5 V regulator 88% efficient; usable pack
fraction 0.85.

```
System average (battery + buck path):
  5V-side load  = 7.0 (Pi+cam) + 0.35 (servo)          = 7.35 W
  from pack     = 7.35 / 0.88                          = 8.35 W
  + motor                                              ≈ 0.8–2.4 W
  SYSTEM AVERAGE                                       ≈ 9–11 W

Energy needed:  30 min ≈ 6.5 Wh installed · 60 min ≈ 13 Wh installed
```

**13 Wh is two 18650 cells.** Energy is not the binding constraint:

| Pack | Runtime @11 W |
|---|---|
| 2S 1500 mAh LiPo | 51 min |
| 2S 2200 mAh LiPo | 75 min |
| 2× 18650 2500 mAh | **83 min** |
| 6× AA NiMH 2000 | 67 min nominal, **~57–60 min derated** |
| 6× AA NiMH 2800 | ~85 min derated |
| 2S LiFePO4 1800 | 53 min |
| 10,000 mAh bank (Pi + servo only) | **4.3 h** |

**Peak current is what actually decides the architecture:**

```
Pi peak 2.32 A + servo stall 0.70 A            = 3.02 A on the 5 V rail
  ...through an 88% buck from 7.4 V            = 2.32 A from the pack
  + motor stall (N20 #1093, 1.6 A)             = 3.92 A total from a 2S pack   ✅ fine

SINGLE 5 V/3 A power bank feeding everything:
  2.32 + 0.70 + 1.60                           = 4.62 A on a 3 A rail          ❌ collapses
```

That second line is the finding that kills the cheapest-imaginable option.
Average draw (~2 A) is comfortable; the **stall event** is the killer, and
on a demo day a mid-run Pi reset is the worst possible failure.

## Path verdicts

| Path | Kit cost | Runtime | Verdict |
|---|---|---|---|
| **a. 2S LiPo + balance charger + bag** | $37.92 | 51 min | **Reject** — worst safety profile *and* not cheapest |
| **b. 2S 18650 + per-cell charger + UBEC** | $21.89–28.17 | 83 min | Best pure-engineering answer; second overall |
| **c. NiMH AA** | $32–38 (or $85.73 retail pack) | 57–85 min | Safest chemistry, but heaviest (~200 g) and no cheaper |
| **d. Split: power bank + motor pack** | **$15.42 if bank owned**, else $33–41 | 4.3 h (Pi side) | ⭐ **RECOMMENDED** |
| e. Single battery + cheap buck | $15.42–22.89 | 83 min | **Reject** — a bare LM2596 won't honestly deliver 3 A |
| f. LiFePO4 | $47–59 | 53 min | **Reject on cost** — safest chemistry, but dearest and shortest |

### Why the split source wins

1. **It is the only path where the lithium in the bedroom is a UL/ETL-listed
   consumer product**, charged from a phone charger, exactly as NFPA's
   consumer guidance contemplates. Every other lithium path puts bare cells
   and a hobby charger in a teenager's room, which institutional guidance
   (Illinois DRS, WMU EHS, AMA) surrounds with rules: balance-charge only,
   never charge unattended, use a fireproof bag, 1C max.
2. **It structurally eliminates the failure mode that kills hobby robots** —
   a motor stall sagging the rail and resetting the Pi. 4tronix rates
   separate supplies as the "most safe" configuration and documents the
   shared-supply failures (motor-start glitches killing the network
   interface; abrupt stops risking SD corruption).
3. **It deletes the DIY regulator from the Pi's power path entirely.** That
   matters because of the single strongest piece of evidence against the
   battery+UBEC approach: a user running a Pi 5 from a 7.4 V pack through a
   5.1 V/5 A buck *still* got undervoltage warnings and WiFi instability,
   attributed to transient dips too brief for a bench load to catch. The Pi
   sees a purpose-built, regulated, current-limited USB source instead.
4. Power-bank auto-shutoff is a non-issue: banks cut off below ~50–100 mA,
   and a Pi 5 idles at 450–640 mA — 5–10× above it.

**Configuration:**
- **Battery A** — 10,000 mAh USB-C bank, 5 V/3 A → Pi 5 only, via a short
  thick cable. Nothing else on it.
- **Battery B** — 2× 18650 in series (7.4 V) with a USB-C 2S BMS/charge
  board → TB6612FNG VM (motor) **and** → LM2596 at 5.2 V → MG90S servo.
  The LM2596 is fine *here*: 700 mA peak, not 3 A.
- **One shared node only:** Pi GND ↔ TB6612 GND, single fat wire,
  star-grounded at the driver. Required so the PWM/direction logic has a
  reference.
- Inline 3 A fuse + rocker switch on Battery B; Battery A uses its own button.

**Weakest points, stated plainly:** it is the **heaviest** option (~320 g of
battery vs 90 g for a LiPo) on a Lego drivetrain whose torque margin is
calculated but untested; it needs **two charge rituals** and two states of
charge to track, and a flat motor pack with a full Pi pack is a confusing
failure to debug; and **the entire cost case depends on whether Evan already
owns a power bank.**

**Evidence against it, from the sources:** a Pi 5 running `ollama` on an
Anker Prime bank produced undervoltage warnings and crashes. Caveat: LLM
inference is a far heavier sustained load than a 20 Hz CNN, and that bank
doesn't advertise a 5 V/5 A profile. The same thread contains a claim that
"the Pi 5 can draw close to 5 A when CPU-bound" — contradicted by every
measurement found here, and treated as folklore.

## Budget verdict

**Nothing safe and adequate fits the ~$22 that was left.**

```
Cheapest complete, SAFE power system found (path b):
  2× EVE 25P 18650 cells                    $3.70
  2-cell series holder                      $1.25
  XTAR FC2 charger (per-cell, no balancing) $6.99
  Adafruit UBEC 5V/3A                       $9.95
  XT30 pair + switch + fuse holder          $4.00
  ------------------------------------------------
  POWER SYSTEM MINIMUM                     $25.89   ...leaving $0 for a motor
```

Full build totals (motor now priced at $23.95):

| Scenario | Total | Verdict |
|---|---|---|
| Owns a power bank + **Pi 4GB** | **~$174** | ✅ comfortable |
| Owns a power bank + Pi 8GB | ~$199 | ⚠️ at the line; shipping breaks it |
| No power bank + **Pi 4GB** | ~$194–202 | ⚠️ at the line |
| No power bank + Pi 8GB | ~$219–227 | ❌ over |

Shipping across three or four vendors adds **$15–25** unless orders are
consolidated — which pushes every "at the line" row over it.

**Recommendation: take the Pi 5 8GB → 4GB downgrade.** It is a free $25 on
power grounds too (no measurable idle-power difference was found between
4GB and 8GB — though that source published no numbers, so it is reported as
missing rather than proven), and a small CNN at 20 Hz is not a RAM-bound
workload.

**If the downgrade is refused, there is no safe power system that fits.** Do
not bridge the gap by putting the Pi and motor on one 5 V/3 A bank — the
peak-current math above says that configuration resets the Pi on the first
stall.

## Verification (reviewer, 2026-07-23 ~17:59 CDT)

| Check | Source | Result |
|---|---|---|
| Pi 5 supports "5 V at 3 A (15 W) with a 600 mA peripheral limit" | raspberrypi.com hardware docs | **MATCH** verbatim — the pivotal claim holds |
| Runtime + energy + peak-current arithmetic | re-derived independently | **MATCH** on every row checked |
| Worker's motor assumptions (0.6 A running / 2.0 A stall) vs the selected N20 #1093 (0.25 A cruise / 1.6 A stall) | cross-worker | **Worker was pessimistic** — real motor is lighter, so runtimes are conservative and the peak figure drops from 4.32 A to **3.92 A**. Conclusions unchanged; the single-bank rejection survives at 4.62 A on a 3 A rail. |

## Sources

Primary: raspberrypi.com hardware + getting-started documentation ·
arXiv 2506.09300 (measured Pi 5 CNN inference power) · Toshiba TB6612FNG
datasheet · NFPA lithium-ion consumer tip sheet + Fire Prevention Week 2025
release · University of Illinois DRS battery safety · WMU EHS lithium
guidance · AMA LiPo basics · Battery University BU-304a · 4tronix robot
power blog · cnx-software Pi 5 review · bret.dk Pi 5 power guide ·
raspberry.tips 2026 power comparison · ProtoSupplies MG90S (measured
currents) · Raspberry Pi forum threads t=358916, t=360658, t=371450,
t=373841, t=381080, t=338502, t=347469, t=359911 · vendor pricing from
Adafruit, Pololu, SparkFun, 18650BatteryStore, Addicore, Anker, EBL,
Tenergy, Palm Beach Bots, Aloft Hobbies, BC Robotics, Jameco, BatterySpace.
All accessed 2026-07-23.

**Reported missing, not fabricated:** any published Pi 5 measurement with a
CSI camera + sustained CNN loop specifically (closest is the arXiv figure
with a display attached); isolated Camera Module 3 current draw from any
primary source (budget 0.3 A and you are safe); exact 2026 price of an EBL
8×AA + charger bundle (Amazon and Walmart block automated fetch); a verified
2026 price for a 5 V buck-boost module for the LiFePO4 path; and any
measured 4GB-vs-8GB Pi 5 power delta. One source (Repetier-Server) claiming
the Pi 5 preemptively throttles on a lower-rated PSU is contradicted by
official docs and Raspberry Pi staff, and is **not** credited.
