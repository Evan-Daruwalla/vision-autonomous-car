# dependencies.md — Autonomous Car Project

**VERIFIED WORKING 2026-08-05 (PRD P1)** — exact pins in
`ml/requirements.txt`, rebuild instructions in its header:
- **Python 3.12.10** venv at `.venv/`. 3.11 is NOT installed on this machine
  and was not worth installing: torch classifies 3.10-3.14 and gym-donkeycar
  needs only gymnasium/numpy/pillow at python_requires>=3.7.
- **torch 2.13.0+cu126** — `cuda.is_available()` True on the RTX 3060 Ti,
  8.00 GiB. **The cu126 index-url is mandatory**; plain `pip install torch`
  gets a CPU-only wheel on Windows.
- **gym_donkeycar from GitHub, pinned to commit a1f4ca69** (release
  v25.10.06). ⚠️ **NEVER `pip install gym-donkeycar` from PyPI** — that
  package is 1.0.13 from **2019-08-04**, six years stale, and would pair a
  2019 client with a 2025 simulator.
- gymnasium 1.3.0 · numpy 2.5.1 · pillow 12.3.0. torch does NOT pull numpy;
  install it explicitly or torch warns and degrades.
- **Simulator: DonkeySimWin.zip** (236,059,289 bytes, sha256 75BAD63A…) from
  the v25.10.06 GitHub release → `sim/` (gitignored). Sim camera is
  **(120, 160, 3) uint8** — already the DonkeyCar standard resolution.

Remaining planned stack from the 2026-07-23 research brief:

- **DonkeyCar 5.x** (latest 5.3.0, 2026-03-29) — teleop, tub data recorder,
  drive loop. Requires 64-bit Raspberry Pi OS Bookworm + Python 3.11.
  Chosen for plumbing only; its TF/Keras trainer is NOT the model path.
- **PyTorch** (desktop training + on-Pi inference) — the custom BC model and
  everything downstream. Portfolio reason: the project's ML story is
  PyTorch, not Keras.
- **M4 world model (chosen 2026-07-23 ~17:39, evidence in
  `docs/research/2026-07-23_world-model-8gb-vram.md`):**
  - **`NM512/dreamerv3-torch`** — PyTorch DreamerV3 port. Chosen over
    danijar's JAX reference for two verified reasons: it has
    `offline_traindir` (skips env prefill), and JAX has no native-Windows
    CUDA. Use REPO DEFAULTS (≈ paper S, ~18M params); never the
    crafter/atari task overrides.
  - **Own implementation of Ha & Schmidhuber V+M+C** (conv-VAE + MDN-RNN +
    controller, ~4.77M params) — built FIRST as the de-risking architecture
    and the guaranteed M4 result.
- Deliberately NOT adding: JetRacer (targets EOL Jetson Nano), CARLA
  (wrong car class), depth-camera SDKs, any SLAM stack, danijar/dreamerv3
  (JAX; no offline mode, no native-Windows CUDA), conglu1997/v-d4rl
  (TF2 — WSL2-only on Windows). Adding one requires a dated PRD entry.
- **gym-donkeycar v25.10.06** (2025-10-06) — promoted from "optional M5"
  to the SIM-POC track 2026-08-05: supplies the simulated driving data for
  the M4-pipeline proof of concept. Windows sim binary verified to exist
  (DonkeySimWin.zip, 236,059,289 bytes, GitHub API 2026-08-05). Also serves
  M5 if that track ever runs. Isaac Lab / Wheeled Lab (arXiv:2502.07380)
  remains optional-M5-only.
- Environment rule: everything ML installs into the pinned Python 3.12.10
  venv, never system 3.14 — see tooling.md (2026-08-05).

- **Arduino toolchain (added 2026-09-02):** Arduino IDE 2.x at
  `~/AppData/Local/Programs/Arduino IDE`, bundling `arduino-cli` 1.5.1 and core
  `arduino:avr` 1.8.8. Firmware includes `Arduino.h`, `avr/io.h`, `avr/boot.h`
  and `stdlib.h` *(`Arduino.h` added by `uno_packguard` 2026-09-02; the earlier
  "only" list was a universal falsified three commits later — Appendix BK)* — **no third-party Arduino libraries**, so there is nothing to
  vendor or pin beyond the core version above. *(Corrected 2026-09-02, Appendix
  BH: the earlier wording claimed the bundled `Servo` library was in use. It is
  NOT — no `.ino` includes `Servo.h` yet. `Servo` is PLANNED for the steering
  servo on D9 per `firmware/SERIAL_PROTOCOL.md`, and it matters because Servo
  claims Timer1 and thereby sets the whole PWM budget.)*
- The firmware toolchain is entirely separate from the Python venv; nothing in
  `ml/requirements.txt` touches the board.
