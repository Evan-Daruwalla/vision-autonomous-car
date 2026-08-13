# Research Brief — Alternatives to the Raspberry Pi 5, whole-landscape

**Date:** 2026-08-12, ~21:48 CDT
**Question:** Across the *entire* compute landscape — not just Pi variants —
is there a better onboard board than the Raspberry Pi 5 for this car?
**For:** Evan, purchasing ~September 2026, on a $200 build already breached.
**Method:** Four collection agents, one per pre-registered hypothesis, each
told to hunt its OWN falsifier. **All four returned PARTIAL** — the previous
process died mid-run and they were resumed from transcript and told to deliver
what they had actually sourced rather than pad. Gaps are marked, not filled.
One number was measured locally rather than researched.

---

## TL;DR

**Keep the Pi — but the reason everyone assumed was wrong, and a real defect
was found in the current plan.**

1. **The camera was never the constraint.** `picamera2` is a *lazy import
   inside `PiCamera.__init__`* — with `CAMERA_TYPE=CVCAM` it never executes.
   The prior brief's central argument for rejecting non-Pi boards does not
   hold.
2. **The PWM pin is the constraint** — and **it breaks the Pi 5 too.**
   `RPi.GPIO` does not work on Pi 5 at all (RP1 southbridge), and
   `donkeycar[pi]` installs it. **This is a live defect in the current BOM,
   independent of which board is chosen.**
3. **H3 (accelerators) dies on arithmetic**, now measured: the onboard path is
   **1,212,775 params** — 28% of the headline 4.35M, because the 3.59M decoder
   never runs on the car — and a full step takes **0.903 ms**, i.e. **55× under
   the 50 ms budget.**
4. **No alternative board is cheaper AND better.** The only one with defensible
   software (BeagleY-AI, $70) costs *more* than the Pi 5 2GB ($65).
5. **Off-board compute over WiFi fails on measured latency** — best figure
   found is 200 ms, 4× the budget.

---

## The measured number that settles H3

Run locally 2026-08-12, `torch.set_num_threads(4)` to mimic the Pi's 4 cores,
300 iterations after warmup, on the real `ConvVAE.encode` + `Controller` +
`MDNRNN.lstm` step:

| | |
|---|---|
| ConvVAE total | 4,348,547 = **encoder 755,744** + decoder 3,592,803 |
| MDN-RNN | 382,533 |
| Controller (MLP) | 74,498 |
| **Onboard path** | **1,212,775 params (28% of the headline)** |
| **Full step latency** | **0.903 ms → 1108 Hz** |
| **Against the 50 ms budget** | **55× headroom** |

**The decoder is inference-dead** — `models.py` notes callers use `mu`
directly at eval time, and a Ha & Schmidhuber controller is `a = W[z,h]+b`.
Even latent-space imagination for M4 needs no decoder.

**Caveat, stated:** this is a desktop x86 CPU, not a Cortex-A76. A Pi 5 will be
slower — plausibly 5–20×, which is 4.5–18 ms, still inside 50 ms. **And it
measures the MODEL ONLY**, not camera capture, resize, or DonkeyCar's vehicle
loop. The agents' own warning stands: **the 20 Hz risk is per-frame Python
overhead, not FLOPs.** Measure the loop on real hardware before trusting it.

---

## H1 vs H2 — the camera constraint: **SPLIT, and both prior positions were wrong**

**H2 wins on the camera.** Verified in DonkeyCar `main` source, 2026-08-12:

- `setup.cfg` — `picamera2` and `RPi.GPIO` are **both only in the `pi` extra**,
  not `install_requires`.
- `parts/camera.py` — `PiCamera` does `from picamera2 import Picamera2`
  **inside `__init__`**. Never imported with a different `CAMERA_TYPE`.
- `templates/complete.py` — supports PICAM, **WEBCAM, CVCAM, CSIC, V4L**,
  IMAGE_LIST, LEOPARD, MOCK. All camera imports lazy, none top-level.
- **The `nano` extra is the existence proof**: `Jetson.GPIO` instead of
  `RPi.GPIO`, and **no `picamera2` at all**. Upstream already ships a non-Pi
  configuration.

**H1 wins on actuation, which nobody checked.** `parts/pins.py` has **exactly
three PWM backends: `RPI_GPIO`, `PCA9685`, `PIGPIO`.** No libgpiod, no
python-periphery, no vendor GPIO library. **Two of three are Pi-only**, and
the third (PCA9685, I2C) needs a breakout **not in the BOM** — checked, absent,
and not in the deferred list either. Evan's wiring drives the servo and
TB6612FNG **straight off GPIO**.

### The live defect: RPi.GPIO is broken on the Pi 5

Independently verified against the Raspberry Pi forum (thread 361834, fetched
2026-08-12): *"RPi.GPIO is not compatible on PI5"*, error `Cannot determine SOC
peripheral base address`. Pi 5 moved GPIO behind the **RP1 southbridge**;
RPi.GPIO pokes registers via `/dev/mem`. Recommended replacements:
**`rpi-lgpio`** (drop-in, no code changes), `gpiozero`, `libgpiod`.

**`donkeycar[pi]` installs `RPi.GPIO`.** So the GPIO path needs work on *every*
candidate board including the incumbent. The Pi's advantage shrinks to "the fix
is a pip drop-in" versus "write a new `pins.py` backend" — real, bounded, and
arguably portfolio-legible work on a non-Pi board.

**Latency evidence is absent, and the vendor numbers are marketing.** No
apples-to-apples measured USB-vs-CSI *capture* latency comparison exists. USB
figures found (105 ms, 115–130 ms, 75 ms) are glass-to-glass including monitor
latency, from 2016-era cameras. The widely-quoted "USB 5–20 ms vs MIPI
0.5–2 ms" comes from camera-vendor blog pages with **no stated method** —
recorded here only so it is recognised and discounted.

---

## H3 — accelerators: **DIES**

Beyond the 55× headroom above:

- **The recurrent core may be uncompilable.** Hailo Community thread 16189
  (2025-07-13): the Dataflow Compiler told a user **"LSTM and GRU are not
  supported layers"**; a Hailo moderator replied without contradicting it. The
  DFC v3.27.0 guide reportedly supports RNN/LSTM only by **unrolling to a fixed
  sequence length** — which is not a stateful single-step RNN, and a driving
  MDN-RNN must carry `(h,c)` across every step. *(That changelog line is
  search-summary only; the primary PDF would not parse. Flagged.)*
- **Coral is abandonware.** `google-coral/edgetpu` **archived 2026-04-19**;
  issue #896 (opened 2025-04-18, "Brilliant Hardware, Broken Toolchain")
  reports Python support ending at 3.9 and **no maintainer response**.
- **Price.** Hailo-8L AI Kit **$109.90** — more than the $65 board, on a budget
  already $22–25 over.
- Jetson Orin Nano Super: only an **unverified $249 MSRP from 2024-12-17** was
  obtained. Even taken at face value it exceeds the entire build ceiling.

---

## The non-Pi SBC landscape

**One board partially falsifies "only Pi has working software": BeagleY-AI.**
Official Debian 13.6 images dated **2026-07-24** — three weeks old — on a
current kernel line, plus an Armbian board page. That is a genuinely different
posture from a vendor that dumped an Ubuntu image in 2023.

**But it costs $70 (Seeed, in stock, 2026-08-12) against the Pi 5 2GB's $65.**
The reason to leave the Pi is money, and the only board with defensible
software is *more expensive*. Its camera path also needs manual device-tree +
`media-ctl` work; **IMX219 works, IMX708 (Camera Module 3) is unconfirmed**;
and TI staff initially called IMX219 incompatible (thread 39098, 2024) with a
community recipe only landing in 2025.

**The rest of the field is worse, and much of it is unbuyable.** At ameriDroid
on 2026-08-12, Radxa Rock 5A/5B, Zero 3W and X2L are **out of stock**; Rock 5C
and Zero 3E are not listed. ODROID-C4 out of stock; M1S variants sold out.
Rock 5T is $249.95. **`ubuntu-rockchip` was archived 2026-04-29** and only
narrowly replaced by a fork covering the Orange Pi 5B specifically — so for
every RK3588/RK3566 board the main third-party Ubuntu source is dead.

**Biggest gap: Libre Computer was NOT SOURCED.** Its own product page returned
only a title and Amazon pages are JS-rendered. Its mainline-kernel claim —
the other best shot at falsifying the Pi's software advantage — remains
**entirely unverified**.

---

## Left-field options

**Off-board compute over WiFi — fails on every measured number.** A 20 Hz loop
gives 50 ms. Best measured (Pi 5 + Camera Module V3, 720p30, glass-to-glass,
2024-04-15): **WebRTC 200 ms**, TCP native 500 ms, RTSP 1,300 ms, UDP native
3,400 ms. The winner is **four control periods of dead time, one way, before
inference.** Teleoperation literature: MQTT control latency averaged 128.4 ms;
direct teleoperation breaks down above 500 ms.

*Honest caveat:* those figures are 720p H.264, and a raw 64×64×3 frame is
**12,288 bytes** — one or two UDP datagrams, no encoder, no jitter buffer. The
three stages that dominate 200 ms are exactly the ones that pipeline skips.
**But no measured figure for that pipeline exists**, and jitter — not mean
latency — is what kills a steering loop. This project has already learned how
badly control-rate variance hurts.

**Android phone (OpenBot)** — the only left-field option not dismissed
outright. Proven architecture (`ob-f/OpenBot`, active into 2026: PR 2026-03-12),
phone as brain, **Arduino Nano over USB OTG serial** owning the servo and motor
driver, so GPIO is sidestepped entirely. **~$0 if a phone already exists.**
Against it: a full Kotlin/ONNX-Runtime-Mobile rewrite, DonkeyCar abandoned,
and **NNAPI was deprecated in Android 15**. It is a cheaper project and a
*worse* one.

**Disqualified on hard numbers:** LattePanda 3 Delta $279 (12 V, 125 mm wide);
LattePanda Mu $218 minimum as a 3-part stack, 9–20 V; N100 mini PCs $240–270,
6–12 W idle, 12 V barrel. **ESP32-S3** (512 KB SRAM + ≤8 MB PSRAM, routine
TinyML 200–500 kB) and **RP2350** (520 KB SRAM total) miss on RAM by roughly
8–10× against 4.3 MB int8 — and that is before the camera buffer and WiFi
stack.

**Used market: no usable price data, for the second consecutive brief.** The Pi
forum thread (2026-04-12/14) confirms a market exists and quotes **zero
prices**; eBay returns unresolvable listing links. Treat "used is cheaper" as
unverified.

**And the market is moving against waiting:** the same thread reports **RAM
prices up ~7×**, which is what drove the Pi increases. September is more likely
worse than better.

---

## Verdict and ranking

| # | Option | Price (dated) | Verdict |
|---|---|---|---|
| **1** | **Pi 5 2GB** | **$65.00** pishop 2026-08-12 | **Buy.** Cheapest, fits power/size, DonkeyCar-native, camera decision stays cheap and reversible |
| 2 | BeagleY-AI | $70.00 Seeed 2026-08-12 | Real software, *more* expensive, forced camera change, unverified `picamera2` substitute |
| 3 | Pi 5 4GB | $110.00 | Only if 2GB demonstrably fails at install |
| 4 | Android phone / OpenBot | ~$0 if owned | Cheaper project, worse project — full rewrite, DonkeyCar abandoned |
| 5 | Off-board WiFi | $0 | Measured 200 ms vs a 50 ms budget; also stops being autonomous |
| — | Hailo-8L / Coral / Jetson | $109.90 / — / ~$249 | 55× headroom already; recurrent core may not compile; Coral archived |
| — | x86, ESP32-S3, RP2350, Radxa/ODROID | see above | Price, power, size, RAM, or stock |

## What would change this conclusion

1. **Libre Computer being sourced** and genuinely mainline — the one unchecked
   shot at a cheaper board with real software.
2. **A measured loop rate on real Pi hardware** below 20 Hz — the 0.903 ms
   figure covers the model, not capture + preprocess + vehicle loop.
3. **A measured sub-50 ms round trip for a raw 64×64 stream** — would reopen
   off-board compute.
4. **2GB failing at `pip install`** — the documented risk, fixable with a
   temporary swap file.

## Actions this brief forces regardless of board choice

- **`donkeycar[pi]` installs `RPi.GPIO`, which does not work on Pi 5.** Plan on
  `rpi-lgpio`. This is a defect in the current plan, not a comparison point.
- **Decide the PWM path before ordering.** Straight-to-GPIO (as the BOM wires
  it) locks the project to a Pi; a **PCA9685 breakout makes actuation pure I2C
  and board-agnostic**, at a cost not yet collected.

## Method limitations

All four agents returned **partial** after a process restart. Not collected:
USB camera prices and FOV options; board-native MIPI camera reports for
Radxa/Orange Pi/Khadas/Odroid; Libre Computer anything; Orange Pi, Khadas,
Banana Pi, Milk-V, RISC-V pricing; verified Jetson pricing/power; RKNN
toolchain state; aarch64 wheel availability; power draw for all boards but
ODROID-M1S. One DigiKey price ($72.54 BeagleY-AI) came from a search snippet,
not a fetched page — **do not enter it in a BOM unverified.**
