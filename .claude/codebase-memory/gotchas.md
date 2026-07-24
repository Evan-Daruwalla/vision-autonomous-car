# gotchas.md — Autonomous Car Project

Hardware/integration traps. All entries 2026-07-23 are from the research
brief (`docs/research/2026-07-23_sensor-compute-stack.md`) — DESK RESEARCH,
not yet verified on this car. Mark them verified when a build task confirms.

- FDM tolerances don't match Lego injection molding — print test coupons for
  pin holes/axle bores and tune per-printer before any chassis print
  (2026-07-23). Community starting points: **~5.1mm pin fit, 5.3-5.6mm
  free-rotating axle bore** vs Ø4.8mm nominal; beam pitch 8mm. (inferred
  from published test boards, unverified on Evan's printer)
- **PETG (not PLA) for rotating bores** against Lego axles — PLA galls/wears
  (LDraw forum guidance, 2026-07-23). PLA fine for static holes.
- Plain Lego motors have no position feedback — never use one for steering;
  hobby servo drives the Lego steering rack (2026-07-23).
- **Never drive Powered Up / Control+ motors (88013/88014) from a raw
  H-bridge** — you lose their built-in 1° encoder and fight their thermistor
  current limiting. PF motors → TB6612FNG; PU motors → Pi Build HAT.
  Mutually exclusive per motor (2026-07-23).
- **L298N banned** on this project: 1.4-3V drop across its BJT output stage
  wastes ~20% of a 9V rail as heat. TB6612FNG (~0.5V drop) is the pick
  (2026-07-23).
- ~~**Pi 5 will not get 5V/5A from standard USB-PD** … Battery path is 2S
  LiPo → 5V/5A-class UBEC → 5V GPIO pins … Never a phone power bank.~~
  **(supersedes the 2026-07-23 ~16:17 entry — the CONSEQUENCE was wrong.)**
  Corrected 2026-07-23 ~17:59 (verified verbatim against official docs):
  the Pi 5 accepts **"5 V at 3 A (15 W) with a 600 mA peripheral limit"**.
  The 5 A rating is a **USB-peripheral budget, not a board requirement**,
  and the only documented consequence of a 3 A supply is that USB cap —
  **irrelevant here, since this build has no USB peripherals** (CSI camera
  only). Measured Pi 5 draw under CNN inference is **1.40 A**; all-core
  stress ~1.76 A. A USB power bank IS viable for the Pi.
- **The real Pi 5 power constraint is transient rail stiffness, not
  amperage.** A documented Pi 5 shut down at only ~1.5 A because of voltage
  drop in "5 A-rated" cables, and another got undervoltage warnings through
  a bench-tested 5 A buck due to transients a DC load never catches. Short
  thick cables; bulk capacitance at the Pi end if a regulator is ever in its
  path (2026-07-23).
- **NEVER put the Pi and the motor on one 5V/3A power bank.** Simultaneous
  Pi peak (2.32 A) + servo stall (0.70 A) + motor stall (1.6 A) = **4.62 A
  on a 3 A rail** → current limit, rail collapse, Pi hard-reset mid-run with
  the SD card mounted. Average draw (~2 A) is fine; the stall event is the
  killer. Split source is the design: bank → Pi only; 2S pack → motor +
  servo; **one shared ground**, star-grounded at the driver (2026-07-23).
- **Don't set `PSU_MAX_CURRENT=5000`** on this build — with no USB
  peripherals it enables nothing and only removes a brownout guardrail
  (2026-07-23).
- **MPU6050 is EOL** (TDK discontinued, counterfeit-prone modules). If an IMU
  enters at M4: ICM-20948 ($20, raw) or BNO055 ($35, on-chip fusion)
  (2026-07-23).
- DonkeyCar 5.x requires **64-bit Raspberry Pi OS Bookworm + Python 3.11**;
  its trainer is TensorFlow/Keras, not PyTorch (2026-07-23).
- Sim-trained RL policies that win in simulation can lose to classical
  control on real hardware (F1TENTH/RoboRacer, RLJ 2025) — this is why the
  PRD makes sim-RL optional (M5) and the capstone offline-on-real-logs (M4).
  Don't re-promote sim-RL without a dated PRD fork (2026-07-23).
- Pi 5 prices are volatile (LPDDR4 shortage; two hikes in three months as of
  2026) — re-verify at purchase time, don't trust the brief's numbers blind.
- **Camera Module 3 ships with the WRONG cable for a Pi 5** (verified
  against Raspberry Pi docs 2026-07-23). The Pi 5 uses the **mini 22-pin**
  connector; the module includes a Standard-Standard cable. A **Standard-
  Mini** cable must be bought separately or the camera cannot be connected
  at all. It is in `docs/BOM.md`.
- **Evan owns NO Lego motors** (confirmed 2026-07-23). Any doc or reasoning
  that assumes a free reused Power Functions motor is stale — the drive
  motor must be bought (PRD M1.1b) and its dimensions gate the rear-module
  CAD.
- **Every Lego motor is TOO SLOW for this car — rejected on physics, not
  price** (2026-07-23, math in
  `docs/research/2026-07-23_drive-motor-selection.md`). Through any
  differential arrangement the best case is PF M at **0.88 m/s**, below the
  1.0 m/s floor; PF L 0.84, PF XL 0.50. Every diff option *reduces* speed
  further, so the only fix is an added step-up layshaft. Don't
  "helpfully" re-propose a Lego motor.
- **Lego gears are metric module 1** ⇒ pitch diameter (mm) = tooth count.
  Mesh centres: 12t→28t = **20.0 mm (2.5 studs)**; 20t→28t = **24.0 mm
  (3.0 studs)**. Diff 62821 = 28-tooth ring; 6573 = 24/16. Lego tire part
  names state real OD × width in mm (44309 = 43.2 × 22; 32019 = 62.4 × 20)
  (2026-07-23).
- **Only the 30:1 N20 ratio works.** N20 speeds jump 1000 → 2000 rpm with
  nothing between; 15:1 and 10:1 fail the acceleration check (112% and
  132-153% of stall), 50:1 tops out below 0.9 m/s, and the low-current
  **30:1 MP variant fails at 101.8% of stall** — which is why the 1.6 A HP
  variant is forced (2026-07-23).
- **Parallel BOTH TB6612FNG channels** (AIN1+BIN1, AIN2+BIN2, AO1+BO1,
  AO2+BO2) for 2 A continuous — steering is a servo, so the second channel
  is free. Also **PWM-cap duty at ~71%** of a full 8.4V pack so the 6V motor
  sees ≤6V, and add a firmware stall-timeout (2026-07-23).
- **The printed motor coupler is the LOWEST-torque joint, not the highest**
  (corrects the 2026-07-23 ~16:17 brief's premise). It sits upstream of the
  reduction: motor stall 55.9 mN·m vs ~45.6 mN·m per half-shaft downstream
  of a 2.333:1 diff. Still, print it as a **socket gripping a real Lego
  axle, never as a printed axle cross-profile** — a printed cross stub is
  only SF 2-4 in torsion at stall, collapsing toward 1 with sparse infill
  (2026-07-23).
- **Raspberry Pi Build HAT is rejected** (2026-07-23, both facts verified
  directly): it needs **8V ±10% (7.2-8.8V) at 48W via a barrel jack** — a
  2S pack is below that for most of its discharge — and it reserves **GPIO
  0/1/4/14/15/16/17** including the primary UART. It is also **not
  supported on Raspberry Pi OS Trixie** (official docs say stay on
  Bookworm), and no rpm/torque data is published for Lego 88013/88014
  anywhere, so their gearing can't be designed on paper.
- **Evan owns NO battery and NO charger** (confirmed 2026-07-23 ~17:32 CDT).
  The 2S-LiPo plan assumed equipment that doesn't exist; the complete power
  system (cells + charger + connectors) is an unbudgeted purchase and is
  under research as PRD M1.1c. Budget is projected over the $200 ceiling as
  a result.
- **Steering is a SERVO, never a plain DC motor** (restated 2026-07-23
  ~17:32 CDT after the "2 motors" framing came up). A servo takes a
  commanded ANGLE; a bare DC motor only takes a direction, so steering
  position would be unknown. The M3 behavioral-cloning model and every M4
  policy emit a steering angle — a plain motor gives that output nothing to
  command. The car has two actuators: drive motor + MG90S servo.
- ~~**Training GPU is 8GB (RTX 3060 Ti)**, below the ~24GB the research
  cited for DreamerV3 on 64×64 vision.~~ **(supersedes 2026-07-23 ~17:21
  entry: the ~24GB figure is RETRACTED — a follow-up pass could not locate
  the source, and no published VRAM-per-size table for DreamerV3 exists.)**
  Corrected 2026-07-23 ~17:39: 8GB is **workable at DreamerV3 S-scale
  (~18M params) or below** at 64×64; XL-scale needs 13.4 GiB and even a
  24GB 3090 OOMs at size200m. Behavioral cloning (M3) is unaffected either
  way. Full detail: `docs/research/2026-07-23_world-model-8gb-vram.md`.
- **Every DreamerV3 repo's DEFAULT config is too big for 8GB.** danijar's
  default is `size200m`; `dreamerv3-torch`'s crafter/atari100k overrides
  jump to dyn_deter 4096 / cnn_depth 96. Use the **repo defaults** of
  `dreamerv3-torch` (dyn_deter 512, cnn_depth 32, units 512) and apply no
  task overrides (2026-07-23).
- **Use `NM512/dreamerv3-torch`, NOT danijar's JAX DreamerV3** (2026-07-23,
  both facts verified directly against source): the JAX reference has **no
  offline-training mode** (issue #80, closed unanswered) and **JAX has no
  native-Windows CUDA support** (official install table: Windows = "no",
  WSL2 = "experimental"). The PyTorch port has `offline_traindir` /
  `offline_evaldir`, and setting `offline_traindir` skips environment
  prefill entirely.
- **Disable NVIDIA "CUDA - Sysmem Fallback Policy" before any training run**
  (NVIDIA Control Panel → Manage 3D Settings → python.exe → "Prefer No
  Sysmem Fallback"). Since driver 536.40 the default spills VRAM overflow
  into shared system RAM, so an out-of-memory condition becomes a **silent
  ~3× slowdown** instead of a loud error. This is exactly what the "16GB
  shared" figure is — host RAM over PCIe (~25 GB/s) vs 448 GB/s GDDR6.
  Never count it as VRAM (2026-07-23).
- **Mixed precision is not a reliable 8GB rescue here** — the one available
  PyTorch DreamerV3 measurement had bf16 costing **10.5 GiB more** and
  running slower. Measure `torch.cuda.max_memory_allocated()`; revert if it
  rises. Gradient checkpointing isn't implemented in any of these codebases
  (2026-07-23).
- **WSL2 does not give more VRAM** — no evidence found; the GPU stays under
  the Windows WDDM driver. It buys compatibility (JAX, TF≥2.11) and clean
  OOM behaviour only (2026-07-23).
