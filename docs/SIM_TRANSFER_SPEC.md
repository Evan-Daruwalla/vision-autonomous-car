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
| **Cruise speed** | **1.401 m/s** steady mean, 1.586 max | The speed all the data was collected at. |
| **Distance per control step** | **7.0 cm** | 1.401 ÷ 20. The car commits to an action for 7 cm. |
| **Camera frame** | **120 × 160 × 3** native | Then squashed to 64×64 (see §3). |
| **\|cte\| held by the expert** | **mean 0.317 m**, p95 0.789, max 1.122 | The distribution the encoder saw. Off-centre perception collapses past ~1.0. |
| **Corpus quality filter** | rejected mean\|cte\| > 1.2 m | Why the corpus had no recovery data. |
| **Episode termination** | \|cte\| > 4.0 m | Sim's off-track bound. |
| **\|steer\| used** | **mean 0.598**, **p95 1.000 (saturating)** | The expert saturates its steering ≥5% of the time. |
| **PID gains** | Kp 2.4, Ki 0.0, Kd 1.2, steer_sign −1 | **Per CALL, not per second — see §4.** |

---

## 2. The four things that MUST match, in priority order

### 2.1 Control rate: 20 Hz, sustained
Not "about 20". Rate is the single most sensitive parameter measured: a **2%**
sleep-throttle collapsed the expert from 9/9 to 0/2 (record Z.2), and the same
checkpoint scored 69 vs 187 steps at 13.2 vs 16.7 Hz. **The Pi must sustain
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
- **Quantise to uint8 BEFORE dividing by 255.** This exact skew has already
  cost this project once — the serve path skipped the round trip and the car
  went from 39 to 61 steps when it was fixed.

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

With **more floor space** chosen (2026-08-12), the lane is no longer forced to
182 mm by a 3×5 grid. Pick the lane first, then the speed follows.

Preserve the sim's **error-to-clearance ratio**, which is the quantity that
actually governs whether the car stays on the road:

- Sim: the expert held mean |cte| **0.317 m** and the corpus filter cut at
  **1.2 m** — so the working band is roughly **±0.32 m typical, ±1.2 m worst**.
- Real: the same *shape* must fit inside `(lane_width − car_width) / 2`.

With a **130 mm car**:

| lane width | clearance per side | verdict |
|---|---|---|
| 182 mm (3×5 grid, now abandoned) | 26 mm | **~half a Duckiebot's margin.** Every perception error you measured in sim gets amplified. |
| 250 mm | 60 mm | workable |
| **300 mm** | **85 mm** | **recommended** — comparable to Duckietown's relative margin |
| 350 mm+ | 110 mm | most forgiving; costs floor area per tile |

**Recommendation: target ~300 mm lanes.** That gives 85 mm per side, roughly
2.6× the 3×5 grid's margin, and it is the cheapest possible insurance against
the one failure this project has measured repeatedly — perception degrading as
the car goes off-centre.

**Then set the speed empirically**, not from the formula: start at **0.3–0.5
m/s** on the real car and raise it only while the PID still holds the lane.
At 20 Hz, 0.4 m/s is **2 cm per control step** — about 7% of a 300 mm lane per
decision, against the sim's 7 cm per step. Slower relative motion than the sim
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
2. **Sim camera FOV — investigated 2026-08-12, and the finding is bigger than
   the question.** `donkey_sim.py` only sends a camera config **if
   `cam_config` is present in the conf dict**, and this project's conf
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
