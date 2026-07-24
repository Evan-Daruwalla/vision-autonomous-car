# Research Brief — Drive Motor Selection

**Date:** 2026-07-23
**Question:** What motor drives the rear axle through the owned Lego
differential, and how does it physically couple to a Lego axle? Its
dimensions block the rear-drive-module CAD (PRD task 6).
**For:** Evan (purchase decision) and any model executing PRD M1.1b / M1.6.
**Method:** One Opus research worker with a pre-registered rubric, required
to show its gearing and torque math. Reviewer independently re-derived the
entire calculation chain and spot-checked two primary sources 2026-07-23
~17:47 CDT — see Verification. **Nothing has been built or measured on the
real parts;** every dimension below still needs calipers on arrival.

---

## TL;DR (verdict first)

1. **Buy the Pololu #1093 — N20 30:1 HP 6V, $23.95.** It is the *only*
   candidate whose available gear ratio lands in the required motor-speed
   band, and it has a full published spec sheet and CAD envelope.
2. **The Lego motor path is rejected on physics, not on price.** Every
   Power Functions motor is too slow: the best case through any
   differential configuration is **0.88 m/s**, below the 1.0 m/s floor.
   Not owning them turns out to be irrelevant — they wouldn't have worked
   without adding a step-up layshaft.
3. **Powered Up + Build HAT is rejected on five independent grounds**, the
   hardest being that the HAT needs **8V ±10%** and a 2S battery sits below
   that for most of its discharge curve.
4. **Both TB6612FNG channels are free** (steering is a servo, not a motor),
   so parallel them for 2A continuous — free headroom already owned.
5. **A premise in the earlier brief was wrong and is corrected here:** the
   printed motor coupler is the **lowest**-torque joint in the driveline,
   not the highest. It sits upstream of the reduction.
6. Budget impact: **$23.95**, slightly over the ~$22 that was left.

---

## The drivetrain math

### The differential, and what actually meshes with it

The owned differential is almost certainly one of two parts, both driven by
a 12-tooth bevel at 90°: **62821** (28-tooth ring, current generation) or
**6573** (24/16-tooth, 1994 generation). Lego gears are **metric module 1**,
so pitch diameter in mm equals tooth count — which makes mesh centre
distances exact and CAD-ready.

| Drive arrangement | Reduction | Mesh centre distance |
|---|---|---|
| 12t bevel → 28t ring (62821), 90° | **2.333:1** | 20.0 mm (2.5 studs) |
| 20t double-bevel → 28t ring (62821), in-plane | **1.400:1** | 24.0 mm (3.0 studs) |
| 12t bevel → 24t large end (6573), 90° | 2.000:1 | 18.0 mm (2.25 studs) |

*The in-plane 20t option depends on double-bevel gears meshing both linearly
and at 90°, which is documented general behaviour but was not confirmable
against a set instruction for this specific ring — **verify physically
before committing CAD.***

### Required motor speed (the requested table, at 1.5 m/s)

Tire diameters are exact: Lego tire part names state OD × width in mm
(44309 = 43.2 × 22; 32019 = 62.4 × 20).

| Tire OD | 12t→28t (2.333) | 20t→28t (1.400) | 12t→24t (2.000) |
|---|---|---|---|
| 43.2 mm | 1547 rpm | **928 rpm** | 1326 rpm |
| 56.0 mm | 1194 | 716 | 1023 |
| 62.4 mm | **1071 rpm** | 643 | 918 |
| 81.6 mm | 819 | 492 | 702 |

Across the 1.0–1.5 m/s target band the requirement spans roughly
**430–1550 rpm**.

### Why 30:1 is the only ratio that works

Available N20 no-load speeds at 6V: 10:1 = 3100, 15:1 = 2000, **30:1 =
1000**, 50:1 = 590, 75:1 = 410, 100:1 = 310. **There is a hard gap between
1000 and 2000 rpm** — no ratio exists in between, which decides the design.

Assumptions for the torque budget (all challengeable): m = 1.25 kg,
C_rr = 0.020 (pessimistic for small hard tires indoors), target accel
1.0 m/s², driveline efficiency 0.70 (three lossy interfaces at ~0.9),
linear motor torque-speed model, rotating inertia ignored.

```
F_roll = 0.020 × 1.25 × 9.81 = 0.2453 N
F_acc  = 1.25 × 1.0          = 1.2500 N
F_tot                         = 1.4953 N
```

**Traction sanity check:** rear normal force ≈ 6.13 N; measured Lego-tire μ
on wood is 1.15–1.38 ⇒ traction limit ≈ 7.05 N against 1.50 N required.
**Not traction-limited — 4.7× margin.**

Two configurations work, both with the 30:1 HP motor (stall 55.9 mN·m,
1000 rpm no-load, 1.6 A stall, 0.10 A no-load):

| Config | Cruise torque (% stall) | Top speed | Cruise current | Accel current | Accel from rest |
|---|---|---|---|---|---|
| **A — 43.2 mm tire, N=1.400** | 5.41 mN·m (9.7%) | **1.46 m/s** | 0.25 A | 0.98 A | 1.83 m/s² |
| **B — 62.4 mm tire, N=2.333** | 4.68 mN·m (8.4%) | **1.28 m/s** | 0.23 A | 0.87 A | 2.14 m/s² |
| C — 43.2 mm, N=2.333 | 3.24 mN·m (5.8%) | 0.91 m/s ✗ | 0.19 A | 0.63 A | 3.19 m/s² |
| D — 81.6 mm, N=2.333 | 6.13 mN·m (11.0%) | 1.63 m/s | 0.26 A | 1.10 A | 1.59 m/s² |

**Rejected ratios, with the numbers that reject them:**
- **15:1** (2000 rpm, 29.4 mN·m stall): config A's acceleration demand is
  **112% of stall — physically impossible.**
- **10:1**: 132–153% of stall. Impossible.
- **50:1**: tops out at 0.78–0.89 m/s. Too slow.
- **30:1 MP** (720 rpm, 32.4 mN·m, 0.67 A — the variant that would fit one
  TB6612 channel): config A needs **101.8% of stall**. *This is why the HP
  variant, and therefore the >1 A stall current, is forced.*

### Why every Lego motor fails

| Motor | Best configuration | Top speed |
|---|---|---|
| PF M 8883 (400 rpm, 0.15 N·m) | 62.4 mm + N=1.400 | **0.88 m/s** |
| PF L 88003 (375 rpm, 0.22 N·m) | 62.4 mm + N=1.400 | 0.84 m/s |
| PF XL 8882 (220 rpm, 0.40 N·m) | 62.4 mm + N=1.400 | 0.50 m/s |

None reaches 1.0 m/s. Every differential arrangement *reduces* speed
further, so the only fix is an added step-up stage (e.g. 20t → 8t layshaft
= 2.5× up, netting 1.071× overall), which brings PF M to 0.92–1.74 m/s
depending on tire — workable, but two extra gears, an extra layshaft, and
more rear-module volume than the N20 route it was meant to simplify.

Secondary-market pricing also isn't the bargain assumed: PF M ≈ $19 used /
$28 new, PF L ≈ $14 / $27, PF XL ≈ $28 / $39 (Brickset, 2026-07-23), with
one US reseller at $34.99 and sold out. **Buying a used, undocumented,
warranty-less part for the same money as a new fully-spec'd one is a bad
trade on a project where the process is the deliverable.**

### Why Powered Up + Build HAT is rejected

1. **$64.99 minimum** ($39.99 motor + $25.00 HAT) against ~$22 remaining.
2. **The battery can't feed it.** The HAT requires **8V ±10% (7.2–8.8V) at
   up to 48W** via a barrel jack (verified directly). A 2S pack is
   6.4–8.4V — below the window for most of its discharge. Fixing that needs
   a boost converter, and the HAT then back-powers the Pi through the GPIO
   header, colliding with the chosen 5V UBEC rail.
3. **It takes GPIO 0/1/4/14/15/16/17** — including the primary UART
   (verified directly).
4. **Not supported on Raspberry Pi OS Trixie** (verified directly: *"install
   or stay on Raspberry Pi OS Bookworm for now"*). A May 2026 forum thread
   reports the Bookworm package is a 2023-vintage v0.6.0 that won't load
   current firmware; workarounds are `pip --break-system-packages` or a
   force-installed cross-release deb.
5. **No published rpm/torque data exists for 88013/88014 anywhere the worker
   could find** — so the gearing could not be designed on paper. You would
   be spending $65 to find out.
6. Build HAT + Camera Module 3 + on-device inference on a Pi 5 is
   **undocumented** — Build HAT + camera CV robots exist, but not that stack.

### Why RC can motors are rejected

An RS-380 draws **~18 A stalled** — 6× the TB6612's 3 A peak and beyond the
DRV8871's 3.6 A, so it would invalidate the already-chosen driver. A
130-class motor is driver-compatible (0.70 A) but ungeared at 8,100 rpm,
needing ~15:1 of added Lego reduction — three gear stages inside a module
that must fit behind the differential. Strictly more work for strictly
worse control.

---

## The printed coupler — correcting an earlier premise

The earlier brief (and the worker prompt) called the motor coupling *"the
drive (highest-torque) joint."* **That is backwards.** The coupler sits
upstream of the reduction, so it is the **lowest**-torque joint in the
driveline. Torque at the N20 output peaks at stall = 55.9 mN·m; downstream
of a 2.333:1 diff the half-shafts see ~91.3 mN·m total / 45.6 mN·m per side,
and the wheel hubs see more still.

Stress at full motor stall (worst case):

| Feature | Stress | Margin |
|---|---|---|
| D-flat bearing (44.7 N over 12.5 mm²) | 3.6 MPa | vs ~50–70 MPa PLA compressive ⇒ **SF ≈ 15** |
| Printed Lego cross-axle stub in torsion (J_t ≈ 15.16 mm⁴) | 6.64 MPa | vs ~15–25 MPa PLA interlayer shear ⇒ **SF ≈ 2–4** |

The torsion figure is the one to respect, and it degrades toward SF ≈ 1 with
sparse infill or poor print orientation.

**Mitigations:** print the coupler as a *socket that grips a real Lego
axle*, never as a printed axle cross-profile; 100% infill and 5 perimeters
if printed; and add firmware stall detection so 55.9 mN·m is never held. A
metal alternative exists — a stainless grub-screw 3.2 mm-shaft-to-Technic-
axle coupler, £4.50, ~7.5 mm OD × 16 mm (single-source, UK, US shipping
unknown). Note Pololu's own #1011 Lego adapter is **discontinued** and is
for 3 mm *hex* shafts anyway — not a solution.

Two verified printed-adapter families exist (Printables 897927 "N20 LEGO
Adapter", Thingiverse thing:3322834), plus at least five more. This is a
well-trodden path. **Caveat:** 897927's coupler outputs an 8-tooth gear /
pulley, not a plain axle — confirm the actual interface against the
downloaded STL before committing the rear module.

---

## CAD-relevant dimensions (Pololu #1093)

| Feature | Value | Confidence |
|---|---|---|
| Body envelope excl. shaft | **10.0 (H) × 12.0 (W) × 25–26 (L) mm** | 2 sources, 1 mm disagreement — **model 26 mm + 0.5 mm clearance** |
| Overall length incl. shaft | ~35–36 mm | Pololu |
| Output shaft | **3.0 mm dia, D-shaped, 9.0 mm long** | Pololu, verified |
| D-flat depth | **MISSING** (one retailer says 2.5 mm — single-source) | **measure with calipers** |
| Mounting | 2 × **M1.6** threaded holes | M1.6 = 2 sources |
| Mounting hole spacing | **10 ± 0.2 mm** | **single-source — verify before drilling CAD holes** |
| Weight | 9.5 g | Pololu (spec'd on same-family sibling) |
| Encoder variant #5159 adds | 3–4 mm on connector side, 358 counts/output rev, +$6 | Pololu |
| Lego cross-axle profile | 4.8 mm across; **rib thickness NOT VERIFIED** | **pull from LDraw/GrabCAD, do not eyeball** |

**Load cases for the mount:** it must react **55.9 mN·m** about the motor
axis (stall), the harness must carry **1.6 A at 6V** (2.24 A if ever driven
unlimited at 8.4V).

**Electrical:** parallel both TB6612FNG channels (AIN1+BIN1, AIN2+BIN2,
AO1+BO1, AO2+BO2) for 2 A continuous, and **PWM-cap duty at ~71% of a full
8.4V pack** so the 6V motor sees ≤6V nominal.

## Weakest points of the recommendation (stated plainly)

1. **The 1.6 A stall exceeds one TB6612 channel's 1 A continuous rating**,
   and even paralleled (2 A) a stall at 8.4V draws 2.24 A. The design leans
   on paralleling + a firmware PWM cap + the fact that real operating
   currents are 0.23–0.25 A cruising and ~0.9–1.0 A accelerating. The right
   fix for more margin is a firmware stall-timeout, not a new driver.
2. **The printed adapter is the single mechanical point of failure**, and
   the exact interface geometry of the published STL is unconfirmed.
3. **Two dimensions are unverified** — hole spacing (single-source) and
   D-flat depth (missing). Both must be measured on arrival.
4. **The in-plane 20t mesh (config A) is unconfirmed** for this specific
   ring. Config B is the lower-risk build.
5. Pololu's $23.95 is ~3× a generic N20 of the same form factor — but
   generic listings publish untrustworthy stall data (Adafruit's own N20
   listing claims 200 mA stall, contradicting every other N20 source).

## Verification (reviewer, 2026-07-23 ~17:47 CDT)

| Check | Source | Result |
|---|---|---|
| Pololu #1093: $23.95, 1000 rpm, 0.57 kg·cm stall, 1.6 A stall, 3 mm D-shaft 9 mm, 10×12 mm | pololu.com/product/1093 | **MATCH** on every figure |
| Build HAT: 8V ±10%, 48W, DC 5521 barrel; reserves GPIO 0/1/4/14/15/16/17; Trixie unsupported | raspberrypi.com Build HAT docs | **MATCH** verbatim, incl. the Trixie warning |
| Entire gearing + torque calculation chain | re-derived independently by reviewer | **MATCH** — wheel rpm, reductions, force/torque budget, top speeds, current model, accel-from-rest, coupler stresses, traction margin all reproduce |

## Sources

Primary: pololu.com product pages #1093/#1101/#4784/#5159/#2364/#1089/#1599/
#1011/#713 · raspberrypi.com Build HAT documentation · adafruit.com #3190/
#4638/#5287 · technicopedia.com/fundamentals.html · rebrickable.com parts
6573/62821b/44309/32019/56145/32269 · brickarchitect.com/parts/44309 ·
bricknerd.com LEGO gears guide · bdml.stanford.edu CrawlerNotes (module 1) ·
brickexperimentchannel.wordpress.com (measured motor + wheel + friction
data) · brickset.com sets 8883/88003/8882/88013/88014 · printables.com
897927 · thingiverse.com thing:3322834 · metal-technic-parts.com coupler ·
forums.raspberrypi.com t=397987 (Build HAT/Trixie, 2026-05) ·
mabuchi-motor.com knowledge base. All accessed 2026-07-23.

**Reported missing, not fabricated:** N20 D-flat depth; verified N20
mounting-hole spacing (single-source); rpm/torque for Lego 88013/88014
(absent everywhere); Lego cross-axle rib thickness; confirmation that a 20t
double-bevel meshes in-plane with this specific diff ring; generic-N20
pricing (Amazon pages unfetchable). Sources that returned no data —
BrickLink price guide, BrickEconomy, lego.com, Amazon, Thingiverse and
Printables item pages, and all PDFs — are listed in the worker output so a
future session doesn't retry them.
