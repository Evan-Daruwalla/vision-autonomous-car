# Research Brief — Sensor + Compute + Software Stack for the Mini Autonomous Car

**Date:** 2026-07-23
**Question:** What sensor suite, compute platform, electronics, and AI-software
pipeline should the Lego-Technic + 3D-print hybrid mini autonomous car use,
staged by milestone — and is the proposed BC → sim-RL → world-model staging
right?
**For:** Evan + any executing model working PRD_ROADMAP.md. Feeds the PRD's
milestone structure and the M2 purchase list.
**Method:** Four parallel Opus research workers (compute / sensors /
electronics-Lego integration / AI pipeline), each with pre-registered rubric
(≥2 independent sources per load-bearing claim, 2025-26 prices, evidence
against each hypothesis). Reviewer spot-checked one load-bearing claim per
worker against primary sources 2026-07-23 (all four matched). Desk research
only — no physical testing yet; all "fits/works" claims about THIS car are
untested until M1-M2.

---

## TL;DR (verdict first)

1. **Pi 5 wins the compute fork.** A bare Pi 5 runs the BC-stage CNN above
   the 20 Hz control-loop cap on CPU alone; DonkeyCar 5.x officially supports
   it; Jetson's "avoid re-platforming later" rationale collapses because
   training always lives on the desktop GPU and even a world-model agent
   deploys only a small policy net onboard. Jetson Orin Nano Super ($249) is
   justified only as a CUDA/TensorRT skills-signal, not by the pipeline.
2. **Camera: Pi Camera Module 3 Wide ($35, 120° diagonal), mono, rolling
   shutter.** Every successful platform runs ≥120° FOV; no evidence rolling
   shutter hurts at 1-3 m/s. Depth and LiDAR don't earn their cost for
   BC/lane-RL — reserve a chassis mount for a $99 RPLIDAR C1, defer the buy.
3. **Electronics: reuse an owned PF L/XL motor** through the Lego
   differential + TB6612FNG driver ($4.95) + MG90S steering servo + single
   2S LiPo with split rails and a 5V/5A-class UBEC into the Pi's GPIO
   (the Pi 5's USB-PD quirk makes battery banks unreliable).
4. **The staging needs one amendment.** BC-first is right, but mandatory
   sim-RL is the riskiest rung (documented F1TENTH transfer failures).
   Promote **offline world-model / offline RL trained on the car's own
   logged real driving** to the M4-M5 spine; sim-RL becomes a parallel
   optional track. This also reads better as a portfolio story.
5. **Rough BOM to a driving, learning car: ~$165-195** (Pi 5 $70-95, camera
   $35, electronics ~$40-45, SD/misc ~$15), assuming owned Lego motors and
   printer filament.

---

## Findings by theme

### 1. Compute (worker: compute; spot-check passed on Pi 5 pricing)

- **Pi 5 prices rose 2025-12-01** (LPDDR4 cost, AI infra demand): 4GB **$70**,
  8GB **$95**, 16GB $145 (and a further 2026 hike on 16GB to ~$205,
  single-source). Old $60/$80 budget math is stale.
  [raspberrypi.com/news, Adafruit, TechPowerUp; verified 2026-07-23]
- **BC inference is easy on Pi 5 CPU:** MobileNetV2 224² int8 ≈ 41 FPS
  (PyTorch official tutorial) — and the DonkeyCar model is smaller, with the
  whole drive loop capped at 20 Hz anyway. No accelerator needed for M3.
- **Accelerator path exists if ever needed:** AI HAT+ 13 TOPS $70 / 26 TOPS
  $110 (YOLOv8s ≈ 80-120 FPS streaming; requires the PCIe Gen3 config flag).
  Optional, later.
- **Jetson Orin Nano Super ($249, 67 TOPS):** ~263 FPS INT8 on YOLO26n via
  TensorRT — real but unneeded headroom for one small policy net. JetRacer
  (the turnkey Jetson car) targets the original Jetson Nano, **EOL Jan 2026**,
  never ported to Orin — so Jetson is LESS turnkey in 2026, not more.
  H2's re-platforming argument: **refuted** — training (BC, offline RL,
  Dreamer) all happens on the desktop GPU; deployment is always a small
  encoder+actor net comparable to the M3 CNN.
- **Offboard compute (H3): mixed.** WebRTC-class camera-up/control-down round
  trips measure 100-250 ms (camera+USB dominates ~100 ms — a faster PC can't
  fix it), vs a 50 ms budget for a 20 Hz loop. Fine for teleop + data
  collection (DonkeyCar's own host-server mode does exactly this); wrong for
  the autonomous loop. DonkeyCar keeps autonomous inference onboard for this
  reason.
- **Power:** Pi 5 wants 5V/5A; standard USB-PD sources won't negotiate 5A at
  5V (documented PMIC/PPS quirk, rpi-eeprom #497) — a 5V/3A source triggers
  USB current caps. Design consequence in §3.

### 2. Sensors (worker: sensors; spot-check passed on Camera Module 3 Wide FOV)

- **FOV beats sensor generation.** DonkeyCar docs: ≥120° recommended, 160°
  preferred. JetRacer ships 160°; AWS DeepRacer races on a 120° camera
  downsampled to 160×120 greyscale @15 fps. Resolution is nearly irrelevant
  for this task.
- **Pick: Camera Module 3 Wide, $35, 102°H/120°D** (verified on
  raspberrypi.com). The $50 Global Shutter camera ships without a lens
  (real cost ~$75-100, 1.6MP) and buys nothing at 1-3 m/s: no study shows
  rolling-shutter harm at small-car speeds (the scary numbers in the
  literature are adversarial LED attacks at speed) and every mainstream
  platform runs rolling shutter. *Tagged reasoned-inference, not directly
  studied.*
- **Depth doesn't pay for lane-following:** UCSD MAE148 found mono sufficient
  and RealSense depth too slow on a Pi; DeepRacer only adds stereo+lidar for
  object-avoidance/head-to-head racing. OAK-D Lite ~$120-150 and tightening
  availability (SparkFun retired it).
- **LiDAR deferred, mount reserved:** RPLIDAR C1 ($99, DTOF) supersedes the
  A1 at the same price. Only needed if a SLAM milestone is added.
- **IMU 2026 state: MPU6050 is EOL** (counterfeit-prone modules) — spec
  ICM-20948 ($19.95) or BNO055 ($34.95, on-chip fusion) when M4 wants
  velocity/yaw. Purchase is M4-gated and design-dependent, not automatic.
- **Odometry fork (cross-worker synthesis):** Lego **Powered Up/Control+
  motors (88013 L / 88014 XL) carry built-in 1° encoders** readable via a Pi
  Build HAT — free odometry. BUT the electronics worker's recommended drive
  path (PF motor + H-bridge) has **no encoder**, and driving a PU motor raw
  from an H-bridge loses its encoder + fights its thermistor. The paths are
  mutually exclusive per motor:
  - **PF L/XL + TB6612** (recommended): simplest, $0 marginal, no odometry —
    add IMU or a cheap encoder at M4 if the observation design needs speed.
  - **PU 88013/88014 + Build HAT**: encoder odometry from day one, but
    different (fiddlier) control path and depends on owning those motors.
  - Which motors Evan actually owns decides this — **unresolved, needs his
    parts inventory.**
- **What each stage needs:** M2-M3 camera only. M4 (offline RL/world model):
  velocity/yaw helpful, design-dependent. M5: richer proprioception helps
  dynamics prediction; no sourced small-car world-model BOM exists (gap
  reported, reasoned from first principles).

### 3. Electronics + Lego/print integration (worker: electronics; spot-check passed on TB6612FNG)

- **Lego motor measured specs** (Philo + Brick Experiment Channel, agreeing
  within method differences): PF M 0.15 N·m / stall ≤0.85 A; PF L ~0.2 N·m /
  ≤1.3 A; PF XL 0.40 N·m / ≤1.8 A (worst-case at held 9V — size drivers to
  Philo's numbers). PF connector: two inner wires (C1/C2) are the switched
  motor lines — splice a sacrificial 8886 extension cable to the H-bridge.
- **Driver: TB6612FNG ($4.95, 4.5-13.5V, 1A cont/3A peak per channel,
  ~0.5V drop, verified on Pololu).** L298N rejected: 1.4-3V drop burns ~20%
  of a 9V rail as heat. DRV8871 ($7.50, 3.6A, current-limit) is the step-up
  if running two drive motors or wanting per-motor current limiting.
- **Steering servo: MG90S** (metal gear, 1.8-2.2 kg·cm, ~$5) — likely
  adequate for a ~1 kg car steering while rolling, but this is sized by
  RC-class analogy (the 8-15 kg·cm RC rule assumes heavier cars scrubbing
  grippy tires). **Fallback MG996R** (9.4-11 kg·cm, ~$8-12) if it stalls.
  Metal gears non-negotiable. Printed servo-horn→Lego-axle adapters exist
  (Printables 61922, 147626).
- **Powered Up motors are NOT a better PF for hacking:** encoders +
  thermistor current-limiting make them worse on a raw H-bridge (see §2
  odometry fork).
- **PF is discontinued** — secondary market only, prices variable and rising.
  Reusing owned motors is smart precisely because buying replacements is a
  gamble.
- **Print tolerances (Lego-compatible FDM):** beam pitch 8mm; pin hole
  nominal Ø4.8mm prints TIGHT — community test boards land at **~5.1mm for
  pin fit, 5.3-5.6mm for a free-rotating axle bore**, printer-dependent:
  calibrate with a test coupon first. **PETG over PLA for rotating bores**
  (PLA galls/wears against Lego axles — LDraw forum guidance; PLA fine for
  static holes). Where precision matters, embedding real Lego beams/pins in
  the printed frame as the load path sidesteps tolerance+wear entirely
  (synthesis, not a cited head-to-head — gap reported).
- **Power architecture:** single 2S LiPo → (a) motor rail direct to TB6612
  VMOT + bulk cap, (b) separate 5V/5A-class UBEC into the Pi 5's 5V GPIO
  pins (bypasses the broken PD negotiation; mind that this bypasses the
  input fuse — clean buck required), (c) servo on 5V, own BEC if it
  disturbs the Pi rail. Shared ground. This mirrors the DonkeyCar reference
  build. **Avoid USB-PD power banks for the Pi 5.**
- **Electronics BOM (excl. compute/camera): ≈$40-45** (TB6612 $5 + MG90S $5
  + UBEC ~$8 + 2S LiPo ~$12 + caps/wires/connectors ~$8, owned PF motor $0).

### 4. AI software pipeline (worker: software; spot-check passed on DonkeyCar 5.3.0)

- **DonkeyCar is alive but slow-cadence:** 5.3.0 released **2026-03-29** with
  an explicit Pi 5 compatibility fix (verified via GitHub API); needs 64-bit
  Bookworm + Python 3.11. Trainer is still TF/Keras, not PyTorch.
  **Recommended shape: DonkeyCar for plumbing (teleop web UI, tub recorder,
  deploy loop), custom PyTorch model swapped into inference** — the model +
  training loop is ~1 evening of work; the plumbing is the real 90%.
- **JetRacer: avoid** (built on EOL Jetson Nano, no Orin port, weak 2025-26
  maintenance signal).
- **Sim options for RL:** gym-donkeycar is current (v25.10.06, 2025-10-06)
  and drops into SB3/PPO — lowest friction. **Wheeled Lab (arXiv:2502.07380,
  2025)** integrates 1/10-scale RC cars with Isaac Lab and demonstrates
  zero-shot sim2real incl. figure-8 visual navigation — the modern
  heavyweight path. CARLA is overkill (full-scale AV dynamics, wrong car
  class — analytic judgment, flagged).
- **Sim2real evidence cuts both ways:** DeepRacer transferred with domain
  randomization as the single most effective lever (grayscale 160×120,
  ~1.6 m/s real). But F1TENTH/RoboRacer RLJ-2025 results show sim-winning RL
  policies swerving and underperforming classical control on real hardware.
  **This is the evidence that demotes mandatory sim-RL.**
- **Lane-segmentation preprocessing** shrinks the sim2real image gap AND
  robustifies BC against lighting (arXiv:2306.10491 + others) — cheap, high
  leverage, thread it in from M3.
- **World models:** DayDreamer trained Dreamer directly on 4 physical robots
  (quadruped walking in 1 hour real time; on-robot GPU unstated — gap).
  DreamerV3 (Nature 2025) runs one agent per GPU. **No verified
  solo-hobbyist world-model car exists — building one offline, on the car's
  own logged driving data, is both the safest variant (no online RL on
  moving hardware) and a genuinely novel-ish portfolio claim.**

  > **CORRECTION 2026-07-23 ~17:39 CDT.** This section originally read
  > "~24GB VRAM comfortable for vision (single practitioner source)." A
  > follow-up research pass could not locate that source at all, and no
  > published VRAM-per-size table for DreamerV3 at 64×64 exists anywhere.
  > **Treat the 24GB figure as RETRACTED.** It does not generalise downward
  > in any case: the measured evidence is that XL-scale DreamerV3 needs
  > 13.4 GiB (batch 8) and OOMs even on a 24GB RTX 3090 at size200m, while
  > S-scale (~18M params) at 64×64 ran on an 8GB GTX 1080. Verdict on
  > Evan's RTX 3060 Ti 8GB: **feasible with constraints** at S-scale or
  > below. Full detail, the recommended config, and the fallback ladder are
  > in `2026-07-23_world-model-8gb-vram.md`.
- **Teleop for data collection (2026):** DonkeyCar WebUI (phone touch or
  HTML5 gamepad) or a Bluetooth pad on the car; collect 10-20 laps / 5-20k
  images before first training.

---

## Ranked options

**Compute:** 1) **Pi 5 8GB $95** (recommended — $25 over 4GB for headroom;
4GB is the DonkeyCar minimum and fine if budget-tight) · 2) Pi 5 4GB $70 ·
3) Jetson Orin Nano Super $249 only if the CUDA/TensorRT résumé line is worth
+$150 and extra setup friction · offboard = teleop/data-collection tool, not
an autonomy platform.

**Sensors (M2-M3 buy):** Camera Module 3 Wide $35. Nothing else. (M4-gated:
ICM-20948 $20 or BNO055 $35. Deferred indefinitely: RPLIDAR C1 $99 — mount
reserved.)

**Drive:** owned PF L or XL + TB6612FNG. (Check inventory: if Evan owns PU
88013/88014, the Build-HAT-encoder path becomes a live alternative.)

**Steering:** MG90S, MG996R fallback.

**Software spine:** DonkeyCar plumbing + custom PyTorch BC model →
lane-segmentation experiment → offline world model / offline RL on logged
real data → (parallel, optional) gym-donkeycar or Wheeled Lab sim-RL →
(stretch) online Dreamer on the car.

## What would change this conclusion

- **Rolling-shutter verdict** is inference from platform practice, not a
  controlled study — if M3 shows smear-correlated failures, revisit Global
  Shutter.
- **MG90S sizing** is by analogy; a stall on real Lego steering geometry
  flips it to MG996R (design the mount to take both — different sizes).
- **Pi prices are volatile** ("temporary" per the Foundation) — re-check at
  purchase time; a drop changes the 4GB/8GB call.
- **DonkeyCar's TF/Keras trainer** aging badly, or its Pi-5 path breaking,
  would push the plumbing custom too (raising M2-M3 effort materially).
- **Evan's actual motor inventory** (PF vs PU) decides the odometry fork.
- **Desktop GPU VRAM** < 12GB would squeeze M4-M5 vision world-model
  training; confirm the card.

## Sources

Condensed to the load-bearing set; each worker's full dated list (~100 URLs,
all accessed 2026-07-23) is preserved in the session record of this date and
recoverable from the worker outputs. Key primary sources:

- raspberrypi.com — Camera Module 3 specs; Pi 5 price-rise announcement
  (2025-12-01); AI HAT+ pages; USB-PD white paper (RP-009856-WP)
- github.com/autorope/donkeycar — releases (5.3.0, 2026-03-29); docs.donkeycar.com
- pololu.com/product/713 — TB6612FNG; ti.com DRV8871 datasheet
- philohome.com/motors/motorcomp.htm + brickexperimentchannel.wordpress.com —
  measured Lego motor specs
- printables.com models 660885/660833 (Lego FDM tolerance test boards),
  61922/147626 (servo→Lego adapters), 897927 (N20 adapter)
- github.com/raspberrypi/rpi-eeprom/issues/497 — Pi 5 PD/PPS 5A bug
- nvidia.com Jetson Orin Nano Super; docs.ultralytics.com/guides/nvidia-jetson
- docs.pytorch.org/tutorials/intermediate/realtime_rpi.html — Pi CPU CNN FPS
- arXiv:2502.07380 (Wheeled Lab) · arXiv:1911.01562 (DeepRacer sim2real) ·
  RLJ_RLC_2025_90 (F1TENTH transfer failures) · arXiv:2306.10491
  (segmentation sim2real) · arXiv:2206.14176 (DayDreamer) · arXiv:2301.04104
  / Nature 640:647-653 (DreamerV3)
- lego.com 88013/88014 + buildhat.readthedocs.io — PU motor encoders via
  Build HAT

**Honest gaps carried from workers:** no rolling-shutter study at 1-3 m/s
(inference); no Ackermann torque formula for this chassis (servo sized by
analogy); DayDreamer's on-robot GPU unstated; DreamerV3 VRAM guidance
single-source; no beams-vs-printed-holes strength head-to-head; PF exact
discontinuation year unresolved; L298N/UBEC street prices approximate.
