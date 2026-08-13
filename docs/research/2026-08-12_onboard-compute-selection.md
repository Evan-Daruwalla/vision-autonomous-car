# Research Brief — Onboard compute: which board, given a breached budget?

**Date:** 2026-08-12
**Question:** The $200 ceiling is breached at ≈$222–225 (verified 2026-08-12).
The Pi is the largest single line and the main lever. Which board should Evan
buy in ~September 2026?
**For:** Evan, spending real money. And any executing model working M1.
**Method:** One collection agent, hypotheses pre-registered before collection,
each hunted for its own falsifier. Every price fetched live 2026-08-12; every
claim dated. Desk research — **nothing was benchmarked on Evan's hardware.**

---

## VERDICT

**Raspberry Pi 5 2GB — $65.00 (pishop.us, in stock, verified 2026-08-12).**
Same 2.4 GHz Cortex-A76 silicon as the 4GB, saves **$45**, and it is the only
Pi variant Raspberry Pi has held flat through all three 2025–26 DRAM price
hikes.

**BOM impact:** fixed rows $219.82 → **$174.82**; + cable $2–5 →
$176.82–$179.82; + shipping $15–25 → **≈$192–205 all-in.** The ceiling is met
on the low-shipping path and missed by ≤$5 on the high one; vendor
consolidation (already flagged in the BOM) closes the rest.

---

## Hypotheses, as pre-registered

- **H1** — Pi 5 2GB is sufficient for inference-only at 20 Hz; the "4GB
  minimum" is DonkeyCar's convenience figure, not a hard requirement.
- **H2** — an older/cheaper Pi (4, 3B+, Zero 2 W) is sufficient and cheaper.
- **H3** — a non-Pi SBC beats Pi on price/performance; CSI + software cost is
  acceptable.
- **H4 (null)** — pay the $110; every alternative costs more in integration
  time and sim2real risk than it saves.

## H1 — SURVIVES, strongly

1. **It is not a minimum and never was.** DonkeyCar's own page: *"In general,
   we recommend the RPi 4 or 5 with 4GB of ram."* A hedged recommendation with
   **no stated justification anywhere in the docs.**
2. **The heavyweight framework never lands on the Pi.** From `setup.cfg` on
   `main` (fetched 2026-08-12), the `pi` extra installs **`tflite-runtime`,
   not TensorFlow**; `tensorflow==2.15.*` appears only in the `pc` and `macos`
   extras. The folk belief that a Pi running DonkeyCar hosts a full TF runtime
   is false. What the `pi` extra *does* drag in (kivy, matplotlib, plotly,
   pandas, opencv-contrib) is **install-time and disk bloat, not drive-loop
   RSS** — and is the most plausible origin of the 4GB folklore.
3. **A 512MB board already does the job.** DIYRobocars (2026-01-06) runs a
   full end-to-end NN driving autonomously on a **Pi Zero 2 W — 512 MB** — on
   Bookworm Lite 64-bit. 2GB is 4× the headroom of a config that demonstrably
   works.

**Falsifier hunt:** every reported 2GB Pi 5 failure found is a *desktop*
workload (Chromium at 40 tabs hitting 1685 of 2048 MB). **Nothing about
headless camera + inference.** The falsifier does not exist in the literature.

## H2 — DIES on the Pi 4 branch; survives weakly as a Zero 2 W fallback

Pi 4 is economically dead: **Pi 4 4GB $100 vs Pi 5 4GB $110; Pi 4 2GB $55 vs
Pi 5 2GB $65** (pishop.us, 2026-08-12). **$10 to give up a full CPU
generation** (A72 → A76, ~2–3×) on a build whose binding constraint is loop
rate. Never take that trade.

Zero 2 W ($17.25) is a different project: the DIYRobocars build is
**steering-only with manual throttle**, on an "optimized" DonkeyCar fork, and
512MB needs swap just to `pip install` — swap on an SD card inside a 20 Hz
loop is a latency hazard. Keep as the $17 emergency fallback.

## H3 — DIES, exactly where predicted: the camera

The **IMX708 (Camera Module 3) driver lives only in Raspberry Pi's kernel
fork** (`raspberrypi/linux`, `rpi-6.6.y`). Mainline integration is incomplete —
metadata support was never merged, and IMX708's PDAF and HDR depend on it.
Rockchip has an open *port request*, not a port. This is not theoretical:

- Radxa Zero 3E cannot drive the older, better-supported **IMX219** — "Error
  −5 setting default controls", **unresolved** as of 2025-02-28, with Radxa
  staff unsure of the cause.
- `ubuntu-rockchip`, the main community distro carrying camera-driver work for
  these boards, was **archived 2026-04-29**.

Compounding it: DonkeyCar's `pi` extra depends on `picamera2` **and**
`RPi.GPIO` — switching boards re-plumbs the camera path *and* the actuation
path. A USB-camera fallback adds $15–25 and discards the $38.50 Camera Module
3 already in the BOM, so the "cheaper" board is not cheaper.

## H4 — DIES, on a primary source

Raspberry Pi's official 2026-04-01 announcement: *"We've been able to hold the
price of Raspberry Pi 400 with 4GB of memory at $60, and the 1GB and 2GB
variants of Raspberry Pi 4 and Raspberry Pi 5 at between $35 and $65."* The
same post raises 4GB by $25, 8GB by $50, 16GB by $100, citing "a seven-fold
increase over the last year in the price of LPDDR4 DRAM."

| variant | Dec 2025 | Feb 2026 | Apr 2026 | pishop 2026-08-12 |
|---|---|---|---|---|
| Pi 5 2GB | $55 | $65 | **held** | **$65.00** |
| Pi 5 4GB | $70 | $85 | +$25 → $110 | **$110.00** |

**The 4GB has taken every hike; the 2GB none.** pishop's $110 *is* the
official price, not a retail markup — this closes the BOM's open note that the
official 4GB price was unverified. **The September purchase carries real price
risk on the 4GB and essentially none on the 2GB.**

## Ranked options

| # | Board | Price (pishop.us, 2026-08-12) | RAM | 20 Hz? | Camera | Tradeoff |
|---|---|---|---|---|---|---|
| **1** | **Pi 5 2GB** | **$65.00**, in stock | 2GB | Yes, large margin | Native mini 22-pin — **BOM row 3 cable unchanged** | Identical compute to the 4GB for $45 less |
| 2 | Pi 5 4GB | $110.00, in stock | 4GB | Yes | identical | Buys headroom with no demonstrated use; keeps ceiling breached |
| 3 | Pi Zero 2 W | $17.25 | 512MB | Unproven | Native mini | $17 emergency fallback; proof is steering-only |
| 4 | Pi 4 4GB | $100.00 | 4GB | Marginal | **standard 15-pin — different cable** | $10 off for a CPU generation. No. |
| 6 | Rockchip/Allwinner | not quoted | 1–4GB | Probably | **broken for IMX708** | Cheapest board, most expensive project |
| — | + Hailo-8L AI Kit | $109.90 (adafruit) | — | — | — | Costs more than the board; a 4.3M-param model at 64×64 has nothing to offload |

## What actually determines the RAM

1. **Your inference runtime — the largest lever, and it is yours to choose.**
   The `torch` extra pulls `torch==2.1.*`; the ONNX Runtime aarch64 wheel is
   ~17 MB against PyTorch's ~65–67 MB with a correspondingly smaller arena.
   **Export ConvVAE + MDN-RNN + controller to ONNX and this stops being
   close.** Recommended regardless of board.
2. Model weights — <100 MB fp32, ~17 MB as fp32 ONNX without the training
   graph. Not a factor.
3. Camera buffers — from **CMA**, and Pi 5's 3D block has an **IOMMU**, so it
   avoids the contiguous low-memory pool that constrained Pi 4.
4. OS — Bookworm Lite 64-bit, headless. Do not install the desktop.
5. **`pip install donkeycar[pi]` — the actual 2GB risk**, where opencv-contrib
   + kivy resolution can OOM. **Mitigation costs $0: swap file for the
   install, then remove it.**

**Note the shape of that risk: 2GB fails at INSTALL time, where a swap file
and ten minutes fix it — not at RUN time, where it would be fatal.**

## Falsifier evidence — what argues against the verdict

- **Nobody has benchmarked this actual model.** Every fps figure is a bracket,
  not a measurement of a ConvVAE + MDN-RNN.
- **The real 20 Hz threat is per-frame Python overhead, not FLOPs.** An
  MDN-RNN steps sequentially every frame inside the DonkeyCar vehicle loop —
  interpreter-bound and **RAM-invariant**. A 2GB purchase does not de-risk
  loop rate. **Measure the loop, not the model.**
- **No measured RSS figure for a DonkeyCar drive loop exists on any board.**
  The H1 case is architectural + existence-proof, not a memory measurement.
- **If 2GB does block you, you pay twice:** $65 + $110 = $175, and weeks lost
  in September. This is the strongest argument for H4 and it belongs on the
  record.

Partly offsetting: the 4GB is in stock now, and the 2GB's failure mode is loud
and immediate (OOM at install), not a subtle mid-project degradation.

**Bonus finding:** the 2GB Pi 5 uses the **BCM2712 D0 stepping** — 33% smaller
die with unused dark silicon physically removed, CPU/clock/ISP functionally
identical to the C1, and **~30% idle power savings**. On a USB-power-bank
build the 2GB is not a compromise part; on power it is the better one.

## Could not find

- **Any measured RSS figure** for a DonkeyCar drive loop, on any board or
  version. The 4GB recommendation appears to rest on nothing published.
- **Any stated justification** by DonkeyCar for the 4GB figure.
- **Any report of a Pi 5 2GB failing** at headless camera + inference.
- **Reliable used/refurbished pricing.** eBay aggregators returned
  $7.99–$457.72 — noise. A search summary attributed "$30–40 for a used Pi 4
  4GB" to a HowToGeek article; **the article was fetched and contains no such
  figures.** Not passed on. Structural risk stands: no warranty, counterfeits
  common, a dead board in September costs weeks.
- Pi 5 2GB stock at a **second US vendor** — only pishop verified. Worth a
  second source before ordering.

## Sources

Prices, all fetched 2026-08-12 — pishop.us product pages for Pi 5 2GB /
4GB / Pi 4 4GB / Pi 4 2GB / Zero 2 W; adafruit.com for the AI Kit.
Official pricing history: raspberrypi.com news posts 2025-12-01, 2026-02-02,
2026-04-01. DonkeyCar: docs.donkeycar.com setup_raspberry_pi, and `setup.cfg`
on `main`. Benchmarks: pytorch.org realtime_rpi tutorial;
docs.ultralytics.com raspberry-pi guide. Camera drivers: raspberrypi/linux
`imx708.c`, rockchip-linux/kernel #330, forum.radxa.com IMX219 thread
(2025-02-27/28). Community: diyrobocars.com 2026-01-06 Zero 2 W build.
D0 stepping: hackaday.com 2024-08-19, jeffgeerling.com 2024 (403, title only).
