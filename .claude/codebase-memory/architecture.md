# architecture.md — Autonomous Car Project

- **Planned system shape** (decided 2026-07-23 from the research brief;
  supersede as reality lands — nothing below is built yet):
  - Mechanical: Lego Technic differential + copied Lego steering geometry +
    Lego wheels, held in a 3D-printed FDM frame; real Lego beams/pins as the
    load path where print precision is marginal.
  - Actuation: hobby servo (MG90S, MG996R fallback) on the steering rack;
    a drive motor turning the rear axle through the Lego diff via a
    TB6612FNG H-bridge (**both channels paralleled** — steering is a servo,
    so the second channel is free).
  - **Drive motor selected 2026-07-23 ~17:47 (pending Evan's purchase go):
    Pololu #1093 N20 30:1 HP 6V, $23.95** — 1000 rpm no-load, 55.9 mN·m
    stall, 1.6 A stall, body 10 × 12 × 25-26 mm, 3 mm D-shaft 9 mm long,
    2 × M1.6 mounting holes. Supersedes both the 2026-07-23 ~16:17 "reuse
    an owned PF motor" plan and the ~17:21 "undecided" entry. Lego motors
    were rejected on physics (too slow), not availability. Full math:
    `docs/research/2026-07-23_drive-motor-selection.md`.
  - **Drivetrain geometry:** config B (lower risk) = 62.4 mm tire (32019) +
    12t bevel → 28t diff ring (62821), N = 2.333, mesh centres 20.0 mm,
    top speed 1.28 m/s. Config A (faster, needs physical verification of an
    in-plane 20t double-bevel mesh) = 43.2 mm tire (44309) + 20t → 28t,
    N = 1.400, centres 24.0 mm, 1.46 m/s.
  - **Power: SPLIT SOURCE** (chosen 2026-07-23 ~17:59, supersedes the
    ~16:17 "single 2S LiPo + 5V UBEC" plan). **Battery A** = USB power bank
    (5V/3A) → Pi 5 only, short thick cable, nothing else on it. **Battery B**
    = 2× 18650 in series (7.4V) + USB-C 2S BMS/charge board → TB6612FNG VM
    (motor) and → LM2596 @5.2V → MG90S servo. **One shared node only:** Pi
    GND ↔ TB6612 GND, star-grounded at the driver. Inline 3A fuse + rocker
    switch on Battery B. Rationale is safety-first (the only path where the
    household lithium is a UL/ETL-listed consumer product on a phone
    charger) plus structural immunity to motor-stall brownout of the Pi.
    Full evidence: `docs/research/2026-07-23_power-system.md`.
  - Sensing: single wide mono camera (Pi Camera Module 3 Wide, 120° diag).
    No depth, no LiDAR (chassis reserves an RPLIDAR C1 footprint only).
  - Compute: **Raspberry Pi 5 4GB** onboard (chosen 2026-07-23 ~20:46;
    supersedes the ~17:21 8GB choice — downgraded for budget, and 4GB is
    DonkeyCar's stated minimum), running inference only. All training happens on Evan's desktop — **RTX 3060 Ti,
    8GB VRAM** (confirmed 2026-07-23; the "16GB shared" is host-RAM
    spillover, not usable VRAM). This holds for every AI stage, including
    the world model (deployment is always a small encoder+actor policy).
  - Software: DonkeyCar 5.x supplies teleop, the data recorder, and the
    drive loop (20 Hz cap); custom PyTorch models replace its Keras models
    at the inference/training boundary.
- **Staged AI pipeline** (amended 2026-07-23, pending Evan's ratification):
  teleop → behavioral cloning (+ lane-segmentation experiment) → offline
  world model / offline RL on the car's own logs (capstone) → optional
  parallel sim-RL. Rationale and evidence: PRD_ROADMAP.md §1 and the brief.
- **ACTUATION MOVES TO AN ARDUINO UNO (decided 2026-09-02 ~15:17, supersedes
  the PCA9685 decision of 2026-09-01 ~21:06, Appendix AY).** Evan has an
  **Uno R3 clone** on hand: ATmega328P (TQFP), **5V logic**, FTDI FT232RL USB
  bridge, enumerating as **COM3** with the driver already working. Cost **$0**.
  - **The split:** Pi does vision and policy at 20 Hz and sends commands over
    **USB serial**; the Uno owns everything real-time — motor PWM, steering
    servo, the four light channels, encoder counting, and a throttle watchdog.
    This is the conventional robotics division of labour, and it is the first
    time this project has had one.
  - **Why it beats the PCA9685 it replaces:** the PCA9685 is a PWM expander and
    nothing else. The Uno additionally does (a) **quadrature encoder counting**
    on hardware interrupts D2/D3 — exactly one encoder's worth, which is what
    the chosen encoder motor needs, and which a Pi does badly because Linux
    guarantees no interrupt latency and silently drops counts at speed; and
    (b) a **failsafe** — firmware cuts throttle if no command arrives within a
    timeout, so a hung Pi or a diverging policy stops the car instead of
    driving it into a wall. Neither is possible on an I2C PWM chip.
  - **Channel budget, checked:** the Servo library claims Timer1, killing PWM
    on pins 9/10 and leaving PWM on **3, 5, 6, 11**. Needed: motor + headlights
    + tail = 3 PWM, servo on its own library, and the two indicators are on/off
    so plain digital pins serve. **Fits with one PWM pin spare.**
  - **The cost, stated plainly:** DonkeyCar's `pins.py` has a PCA9685 backend
    and **no Arduino backend**, so the actuator path in PRD task 11 becomes
    custom firmware plus a serial protocol this project writes and debugs.
    Consistent with a project whose differentiator is already custom PyTorch,
    but it is real work that the $6-15 part would have avoided.
  - **Power, and it is not free:** `docs/research/2026-07-23_power-system.md`
    states "This build has zero USB peripherals, so the [600mA] cap is
    irrelevant." **A USB-connected Uno makes that false.** The board alone is
    ~50mA; the danger is it sourcing LED current from its pins, which would put
    up to 160mA back on the Pi's 5V/3A bank — precisely what LIGHTING_SPEC §3
    was written to prevent. **The Uno supplies LOGIC; LED current comes off the
    LM2596 rail.** Powering the Uno from the 7.4V pack instead has its own
    failure: the pack sags under motor stall and the AMS1117 drops out,
    browning out the Uno mid-drive. Preferred: feed its 5V pin from the LM2596
    rail and use a **data-only USB cable** so nothing back-feeds.
- gotchas.md holds the hardware traps; this bin stays about system shape.
