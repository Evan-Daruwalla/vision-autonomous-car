# testing.md — Autonomous Car Project

No test framework is installed (verified 2026-08-06: no pytest, no linter, no
CI config). Verification is done by **runnable self-checks and done-checks
that exit non-zero on failure** — the project's actual gates. Adding `ruff`
and a `tests/` directory before M3 is an open audit item (F20).

## The gates that exist, and what each one actually proves

| Command | Proves | Notes |
|---|---|---|
| `python ml/verify_env.py` | CUDA is live and the simulator returns a camera frame | SIM-POC P1 done-check. Launches the sim — don't run it while collecting |
| `python ml/verify_corpus.py ml/data/sim` | the driving corpus is structurally valid, frame/action aligned on BOTH axes, at 120×160, within the collector's quality thresholds, and the layout split is disjoint | SIM-POC P2 done-check. O(1) memory |
| `python ml/models.py` | the world model's layers are wired to the paper — asserts the VAE has **exactly 4,348,547** params | reproducing a published count to the digit is a stronger wiring check than reading the code. **The assert now lives in `ConvVAE.__init__`**, so every training/eval run re-checks it, not just this command |
| `python ml/splits.py` | the fit/val split is disjoint, exhaustive, stratified, and reproducible; a different seed gives a different split | catches a seed being silently ignored |
| `python ml/rollout_eval.py` | 30-step imagination beats a frozen-frame baseline on ≥90% of steps **(exits 1 if not)** | SIM-POC P3 done-check. Gated on `val_indomain` only — holdout is *expected* to lose (0/30), so gating on it would fail a correct model |
| `python ml/probe_vram.py` | whether an OOM can actually happen on this machine | exit 1 means Sysmem Fallback is ON — a finding about the machine, not a broken check |

**Cold audit 2026-08-06 fixed four gates that could not fail.** Before it:
`rollout_eval.py` printed its win count and discarded it (0/30 exited exactly
like 30/30); `gen_tolerance_coupon.py` wrote the STL *before* validating and
always exited 0; `sweep_dreamer_p4.py` inferred success from a file existing
rather than the child's exit code; and `models.py`'s param assert never ran
outside `__main__`. **A gate that cannot fire is not a gate** — and all four
were documented, here and in the README, as if they were.

## Rules learned the hard way

- **A checker that misdiagnoses is worse than one that abstains.** Three
  false-diagnosis bugs were found in `verify_corpus.py` alone (gating on
  peak-lag zero; omitting `log_ki`; reporting weak correlation as
  misalignment). Every one asserted a constant that was not constant. When a
  measurement is too noisy to judge, report UNVERIFIABLE, never WRONG.
- **Every claim needs a baseline.** "The rollout looks track-like" is
  unfalsifiable — every frame of a driving corpus looks track-like. Compare
  against a do-nothing predictor (freeze the last real frame) or the claim
  means nothing.
- **Seed everything and record the seed.** All training scripts take `--seed`
  and seed torch, numpy and CUDA. Evaluation subsets use a *fixed* separate
  seed so epoch-to-epoch numbers are comparable.
- **One seed is not a measurement** for any comparative claim — the routing
  research found seed variance in driving policies reaching tens of points.
  P3 used one seed because it is a pipeline proof, not a comparison; P4/P5
  comparisons need ≥3.
- Adversarial self-testing works: deliberately corrupting a corpus (rolling
  the image axis, emptying a split, removing the holdout) is what exposed
  that the P2 gate did not check what its docstring claimed.
- **Verify a gate by making it FAIL, not by watching it pass.** Every fix in
  the 2026-08-06 audit pass was checked in both directions — the coupon was
  fed impossible geometry, `rollout_eval` an unreachable threshold,
  `preprocess` a simulated Ctrl-C, `verify_corpus` a malformed filename. A
  green run proves nothing about a check that has no red path.
- **A cache keyed on less than what produced it is a silent-corruption
  machine.** `{split}_mu.npy` was keyed on the split name alone, so retraining
  the VAE meant the MDN-RNN learned dynamics in one latent space while
  rollouts decoded through another. Latent caches now carry a
  `{split}_latents.key` fingerprint of the encoder; a missing key is
  UNVERIFIABLE (warn), a different key is WRONG (exit 1).
- **Exit codes, not artifacts, are the success signal for a subprocess.**
  Committed result files make "the output exists" indistinguishable from "the
  run worked" — and republishing a stored number as a fresh measurement is
  the worst failure this project can have.
