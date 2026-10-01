# features.md — Autonomous Car Project

**34 Python files under `ml/`** (was 31; re-derived 2026-09-03) (verified 2026-08-25: `git ls-files ml/ |
grep -c '\.py$'`) plus `scripts/gen_tolerance_coupon.py` (CAD tolerance-coupon
STL generator, zero-dependency — see tooling.md). Built over 2026-08-05 to
2026-08-13 for SIM-POC P1-P5. This bin lists WHAT EXISTS; schema/format is
data.md, gates/verification is testing.md, physical system shape is
architecture.md — cross-reference rather than duplicate.

## Data collection & format
- `collect_sim_data.py`, `collect_recovery.py` — drive the sim (PID expert)
  and log episodes; recovery variant collects off-centre frames exempt from
  the quality filter (Appendix W finding).
- `build_expert_labels.py`, `episode_writer.py` — expert action labelling and
  the episode `.npz` writer (format = data.md).
- `sim_conf.py` — sim launch configuration (camera FOV etc.; the missing
  `cam_config` bug is Appendix AI).

## Preprocessing & splits
- `preprocess.py` — builds the four aligned arrays (`_images/_actions/
  _episodes/_tracks`) from raw episodes, atomic tmp+replace (data.md).
- `splits.py` — fit/val/holdout split, stratified, seeded, disjoint
  (testing.md done-check).

## World model (Ha & Schmidhuber V+M+C, SIM-POC P3)
- `models.py` — ConvVAE + MDN-RNN + controller definitions; asserts the VAE's
  param count against the paper (4,348,547) on import.
- `train_vae.py`, `train_mdnrnn.py` — training scripts, both seeded.
- `compare_encoders.py` — encoder comparison utility.

## DreamerV3 (SIM-POC P4)
- `prep_dreamer_corpus.py` — reformats the corpus for `NM512/dreamerv3-torch`.
- `run_dreamer_p4.py` — training entry point.
- `sweep_dreamer_p4.py` — batch-size/VRAM sweep (the 8GB fitting table).

## Controller / policy
- `train_controller.py` — latent BC controller training (linear + MLP).
- `plan_cem.py` — CEM planning over the world model.
- `train_cte_probe.py` — linear/MLP probe of cross-track-error readout from
  latent `z` (P5's structural finding: R² 0.27 linear vs 0.97 MLP).

## Evaluation
- `eval_in_sim.py` — single-arm closed-loop eval; enforces the PID-expert
  batch-validity gate (testing.md), exits 2 on a degraded batch.
- `eval_paired.py` — the PAIRED design (all arms inside one sim launch,
  differenced within-launch) that answers the P6 harness-noise problem
  (Appendix AJ).
- `rollout_eval.py` — SIM-POC P3 done-check (30-step imagination vs a
  frozen-frame baseline).

## Diagnostics (harness / failure-mode investigation, Appendices AD-AJ)
- `diag_camera_fov.py` — measured sim FOV vs candidate real cameras
  (identified the Camera Module 3 Wide match, Appendix AI).
- `diag_copycat.py` — tests the copycat-agent explanation for the P5 wall
  (BC riding on `h` instead of `z`).
- `diag_reset.py` — episode start-state determinism check (ruled out as the
  4.4x variance cause, Appendix AD).
- `trace_failure.py` — per-episode failure-mode tracing.
- `measure_operating_point.py` — control-rate / operating-point measurement
  (ruled out control rate as the variance cause).

## Probes & experiments
- `probe_cone.py` — small-object (cone/sign) latent-survival probe; found
  0/899 cone pixels survive the VAE or DreamerV3 encoder.
- `probe_vram.py` — OOM/Sysmem-Fallback check (testing.md done-check).
- `exp_aux_head.py` — auxiliary detection-head experiment for the M4
  stop-sign showcase; ships a `--self-check` mode (testing.md).
- `exp_recovery.py` — recovery-data closed-loop experiment (the tested-and-
  closed "recovery helps" hypothesis, Appendices X/AA).

## Environment verification
- `verify_env.py` — SIM-POC P1 done-check (CUDA + sim camera frame).
- `verify_corpus.py` — SIM-POC P2 done-check (corpus structural/alignment
  validity).
