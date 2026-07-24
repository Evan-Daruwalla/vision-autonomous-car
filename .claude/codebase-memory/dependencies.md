# dependencies.md — Autonomous Car Project

No code exists yet (2026-07-23). Planned stack, chosen in the 2026-07-23
research brief — pin real versions here when first installed:

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
- Optional/later: gym-donkeycar (v25.10.06, 2025-10-06) or Isaac Lab /
  Wheeled Lab (arXiv:2502.07380) if the optional M5 sim-RL track runs.
