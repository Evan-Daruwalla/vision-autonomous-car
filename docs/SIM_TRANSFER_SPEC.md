# Sim-Transfer Spec — what the physical car must match

**Written 2026-08-12 ~08:05 CDT. Live doc; supersede by dated edit.**

Everything trained and measured in SIM-POC is tied to one operating point. The
physical car inherits that work **only where it matches this point** — and most
of it had never been written down, because `THROTTLE = 0.20` is a normalised
command rather than a speed and the corpus logs cross-track error but not
velocity.

**All figures measured 2026-08-12 by `ml/measure_operating_point.py`** (400
steps, scripted PID expert, `donkey-generated-track-v0`), not estimated.

---

## 1. The measured sim operating point

| quantity | measured | why it matters |
|---|---|---|
| **Control rate** | **20.00 Hz** | The PID gains and every learned policy were tuned here. Rate changes behaviour sharply (record Z.2). |
| **Mean operating speed** | **1.401 m/s** steady mean, 1.586 max | The speed all the data was collected at. **Not a "cruise" speed: 60.5% of steps ran at THROTTLE_CORNER (0.14) because the expert steers hard, and speed lags the command — corner-throttle mean 1.397 vs cruise-throttle mean 1.209. There is no clean cruise regime; use the overall mean.** |
| **Distance per control step** | **7.0 cm** | 1.401 ÷ 20, on the overall mean. The car commits to an action for 7 cm. |
| **Camera frame** | **120 × 160 × 3** native | Then squashed to 64×64 (see §3). |
| **\|cte\| held by the expert** | **mean 0.317 m**, p95 0.789, max 1.122 | The distribution the encoder saw. Off-centre perception collapses past ~1.0. |
| **Corpus quality filter** | rejected mean\|cte\| > 1.2 m | Why the corpus had no recovery data. |
| **Episode termination** | \|cte\| > 4.0 m | Sim's off-track bound. |
| **\|steer\| used** | **mean 0.598**, **p95 1.000 (saturating)** | The expert saturates its steering ≥5% of the time. |
| **PID gains** | Kp 2.4, Ki 0.0, Kd 1.2, steer_sign −1 | **Per CALL, not per second — see §4.** |

---

## 2. The four things that MUST match, in priority order

### 2.1 Control rate: 20 Hz, sustained
Not "about 20". Rate is the most sensitive parameter measured: a **2%**
sleep-throttle dropped the expert from 600/600 to **196.5 +- 0.5 steps**
(record Z.2 — and Z.2 itself demotes `--control-hz` to a diagnostic that
measures a desynchronisation artifact, so read it as "the harness is
rate-fragile", not as a clean rate law). The same checkpoint also scored 69 vs
187 steps at 13.2 vs 16.7 Hz — **but note AD.3 measured the harness at CV 55%,
where n=1 resolves only ~3x, and 69->187 is 2.7x. Treat the direction as real
and the magnitude as unestablished.** **The Pi must sustain
camera capture + preprocess + VAE + MDN-RNN + controller inside 50 ms, with
headroom.** If it can't, the sim-tuned gains and policies do not transfer and
must be re-tuned at whatever rate the Pi actually achieves — which is a real
cost, so measure it before committing to the board.

### 2.2 Image pipeline: byte-identical to `ml/preprocess.py`
- Capture **120 × 160 RGB**.
- Resize to **64 × 64 by anisotropic squash** — *not* a crop. Cropping to
  square discards peripheral vision, which is where the lane edge lives in a
  turn.
- **Antialiased bilinear.** Without it, thin lane markings alias between frames
  and the encoder sees flicker it never trained on.
- **Quantise to uint8 BEFORE dividing by 255.** The corpus was written as
  uint8 and only divided by 255 at load, so skipping the round trip feeds the
  encoder continuous values it never saw. `ml/eval_in_sim.py` does this
  correctly and documents why; match it exactly. *(An earlier draft of this
  spec attached a "39 → 61 steps" improvement to this fix. **That number is
  not in the record or the codebase and should not be relied on** — the
  practice is right, the quantified gain is unsourced.)*

### 2.3 Steering authority: at least as much as the sim uses
The expert's steering **saturates (|steer| = 1.0) at the p95**, and averages
0.598 of full lock. A real car whose lock-to-lock gives a larger turn radius
than the sim's will be unable to execute the corrections the policies learned.
**Measure the real turn radius during M1 bench testing and compare it against
the track's tightest corner** before printing a final frame.

### 2.4 Speed scaled to the lane, not copied
Do **not** copy 1.401 m/s. What transfers is *lane widths travelled per control
step*, and the real track's lane is far narrower than the sim's. Rule:

```
real_speed  =  1.401 m/s  ×  (real_lane_width / sim_lane_width)
```

**`sim_lane_width` is NOT MEASURED and this is the biggest open number in this
spec.** The sim's `max_cte = 4.0 m` is a termination bound, not a lane edge,
and the visual lane width was never measured. Until it is, treat the
right-hand factor as unknown and derive the real speed from the real track
instead (§3).

---

## 3. Deriving the real car's speed from the track

**Floor space CONFIRMED 2026-09-01: 3.0 × 3.0 m** (9 m²). That fits the full
estimated 500-670 mm corner-radius range at either candidate car width, so
space no longer constrains the layout. Pick the lane from the car, then the
speed from the lane.

Preserve the sim's **error-to-clearance ratio**, which is the quantity that
actually governs whether the car stays on the road:

- Sim: the expert held mean |cte| **0.317 m** and the corpus filter cut at
  **1.2 m** — so the working band is roughly **±0.32 m typical, ±1.2 m worst**.
- Real: the same *shape* must fit inside `(lane_width − car_width) / 2`.

| ratio | 100 mm car | 130 mm car | clearance/side |
|---|---|---|---|
| 1.8x | 180 mm | 234 mm | 40 / 52 mm |
| **2.0x (recommended)** | **200 mm** | **260 mm** | **50 / 65 mm** |
| 2.2x | 220 mm | 286 mm | 60 / 78 mm |

**RULE: lane width = 2.0 x the MEASURED car width.** Corrected 2026-09-01
after Evan pointed out that the previous fixed-clearance rule produced
unrealistic proportions. Sourced references:

| reference | lane : vehicle |
|---|---|
| US highway lane (12 ft = 3658 mm) / typical car body (~1850 mm) | **1.98x** |
| Duckietown: 210 mm lane / Duckiebot DB21 (~150 mm) | **1.40x** |
| Duckietown, if the chassis is nearer 130 mm | **1.62x** |
| ~~previous spec: 300 mm / 130 mm~~ | ~~2.31x~~ |
| ~~previous spec: 270 mm / 100 mm~~ | ~~2.70x~~ |

**The old rule was wider than every real reference**, and its justification —
"insurance against the measured off-centre perception failure" — does not hold
up: widening the lane does not fix perception, it only delays the consequence.
**Duckietown demonstrably runs learned policies at 30-40 mm per side**, well
under the 85 mm previously specced.

**Why 2.0x and not Duckietown's 1.4-1.6x:** Duckiebots are differential-drive
and can pivot in place; this car is Ackermann-steered with a real minimum turn
radius, so it is less able to recover from a bad line. 2.0x matches real-road
proportion, still leaves 50-65 mm per side (more than Duckietown), and costs
essentially nothing in the 3 x 3 m space — maximum corner radius moves only
675 mm -> 685-700 mm.

*(Caveat on the Duckiebot figure: 150 mm comes from a "13x6x9 in / 34x15x23 cm"
product listing that may describe the shipping box rather than the chassis, so
the 1.40x is soft. Either reading puts Duckietown TIGHTER than real roads,
which is the point that matters.)*

**Then set the speed empirically**, not from the formula: start at **0.3–0.5
m/s** on the real car and raise it only while the PID still holds the lane.
At 20 Hz, 0.4 m/s is **2 cm per control step** — 10% of a 200 mm lane or 7.7% of
a 260 mm lane per decision, against the sim's 7 cm per step. Slower relative motion than the sim
is the safe direction to err.

---

## 4. Carried-over defects the real build must not inherit

- **`PIDDriver` is not dt-normalised.** `integral += err` and
  `derivative = err − prev_err` are **per call, not per second**, so the
  effective Ki and Kd change with loop rate. The gains 2.4/0.0/1.2 are
  therefore **bound to 20 Hz**. Either normalise by dt before porting, or
  re-tune on the real car and record the rate alongside the gains.
- **`pigpio` does not work on Pi 5** (RP1 south bridge). Use `lgpio` /
  `libgpiod`.
- **Encoder counts the MOTOR shaft**, upstream of a backlash-heavy Lego
  differential. Odometry will be better than nothing and worse than the
  1–6 mm/0.6 m figure the datasheet maths implies. Calibrate against measured
  ground distance, don't trust the count.

## 5. Known unknowns — measure these, do not assume

1. **Sim lane width in metres.** Blocks the clean speed-scaling formula (§2.4).
2. **RESOLVED 2026-08-13 (Appendix AI): the sim default is `fov=90`**, i.e.
   ~106° horizontal / ~118° diagonal at 160x120 under Unity's vertical-FOV
   convention. **The Camera Module 3 Wide (102° H / 120° D) matches within
   2-4° and is the correct part**; the standard module is ~40° off. Identified
   by capturing a default frame and comparing against explicit FOVs on a FIXED
   track (`ml/diag_camera_fov.py`) - the test is meaningless on
   `donkey-generated-track-v0`, which regenerates the scene every launch.
   Original finding, retained because the mechanism still matters: `donkey_sim.py` sends a camera config only via
   **three paths** (two keyed on `cam_config`/`cam_config_b`, one deprecated
   top-level), and **all three are skipped** when those keys are absent, and this project's conf
   (`collect_sim_data.py`, `eval_in_sim.py`) contains only `exe_path, host,
   port, start_delay, car_name, max_cte`. **So the FOV, the lens distortion,
   and the camera's offset_x/y/z and rot_x/y/z were NEVER SET** — every frame
   in the corpus was captured at the Unity binary's built-in default, and that
   default is not recorded anywhere on the Python side. It cannot be read from
   the code; it lives in the sim binary.

   **This is a free parameter the project didn't know it had.** The Camera
   Module 3 Wide is 120°. If the sim default differs materially, the encoder
   trained on a different projection than the real camera will produce — which
   is the most likely single cause of sim2real failure in this build.

   **Three options, and the cheapest is decisive:**
   - **(a) Identify the default empirically — do this first.** Capture one
     frame at the default, then frames with `cam_config` set to fov 60 / 90 /
     120 from the same pose, and compare. Whichever matches identifies the
     default. Costs one short sim run, needs no hardware, and turns the
     project's largest sim2real unknown into a number.
   - **(b) Set the sim to match the real camera** (`cam_config: {"fov": 120,
     ...}`) and re-collect + retrain. Correct, and expensive — it invalidates
     the corpus and every trained component.
   - **(c) Choose a real lens matching the sim default.** Only possible after
     (a).

   **Do (a) before spending money on a camera.** It is the highest-value work
   available with no hardware, and it may make the Camera Module 3 Wide the
   wrong purchase.
3. **Camera height, pitch and forward offset in sim.** Same root cause as (2)
   — `offset_x/y/z` and `rot_x/y/z` were never set either, so the mount
   geometry the encoder trained on is also the Unity default and also
   unrecorded. Recover it in the same experiment as (a), then replicate it on
   the physical mount. **A camera at the wrong height or pitch changes the
   projection as surely as the wrong FOV does.**
4. **Achievable control rate on the target board.** Determines whether §2.1
   holds at all.

**Items 2 and 3 are the highest-value cheap work available before hardware
arrives**, and neither needs a purchase — both are recoverable from the sim's
own config and a tape measure.
