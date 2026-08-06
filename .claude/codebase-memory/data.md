# data.md — Autonomous Car Project

**The driving-episode format is THE data contract of this project.** It is
written by `ml/episode_writer.py`, consumed by everything downstream
(SIM-POC P3/P4, then M3 behavioural cloning and M4 world models on real car
logs), and enforced by `ml/verify_corpus.py`. Established 2026-08-05,
verified on a 102,888-frame corpus 2026-08-06.

## On-disk format (matches NM512/dreamerv3-torch, read from its source)

- **One `np.savez_compressed` archive per episode**, filename
  `{id}-{length}.npz` where `length == len(episode["reward"])`. The loader
  TRUSTS the filename, so a mismatch is a verifier failure, not a warning.
- Written to a `.npz.tmp` then `os.replace()`d — **atomic**, so a reader
  scanning the directory sees a complete file or no file, never a partial
  one. A plain write is not enough: a verifier racing the collector hits a
  truncated npz (observed 2026-08-06).

| Key | Shape | dtype | Meaning |
|---|---|---|---|
| `image` | (T, H, W, 3) | uint8 | camera frame |
| `action` | (T, A) | float32 | the action that LED TO this frame |
| `reward` | (T,) | float32 | |
| `discount` | (T,) | float32 | 1.0, or 0.0 on a TRUE terminal |
| `is_first` | (T,) | bool | True at t=0 only |
| `is_last` | (T,) | bool | True at the final step only |
| `is_terminal` | (T,) | bool | True only on a real terminal, not a truncation |
| `log_*` | varies | varies | provenance; `log_`-prefixed keys are training-irrelevant |

## Invariants (each one is a verifier gate, not a convention)

- **`action[i]` is the action that produced `image[i]`.** At t=0 there is no
  preceding action, so `action[0]` is zeros and `reward[0]` is 0.0. An
  off-by-one here still trains happily and silently learns to predict the
  wrong action — which is why alignment has two independent gates (below).
- **`discount == 0` exactly where `is_terminal`.** A crash means "no future
  exists"; hitting a step limit means "the future exists, we stopped
  looking". Conflating them teaches the model that time-limit boundaries are
  catastrophes.
- No NaN/inf in `action`, `reward`, `discount`; steering within [-1, 1];
  images uint8 and 4-D.

## Alignment is verified on TWO axes, and one is only approximate

1. **Action axis — exact.** The expert is a deterministic function of
   cross-track error, so `verify_corpus.check_pid_identity` recomputes every
   action from `log_cte` (+ the PID params logged per-episode, so re-tuning
   the driver later cannot retroactively invalidate an old corpus). No
   thresholds; rolling the action array by one step breaks it immediately.
2. **Image axis — approximate, and the limit is documented.** Pixel motion
   trails the steering command because steering sets heading RATE. Measured:
   lag −1 for most episodes, −2 for the fastest (speed-dependent, so an
   exact-equality gate produces FALSE failures). Gate = per-episode peak in
   band {−2, −1} **plus** corpus mode == −1. **Catches** any ≥2-frame offset
   and a whole-corpus 1-frame roll; **cannot catch** a 1-frame roll of a
   minority, because physics already produces that signature at −2.
   `MIN_PEAK_CORR = 0.50` sits inside a measured gap (well-determined lags
   0.60-0.96; noise 0.34-0.40) — below it an episode is UNVERIFIABLE, never
   "wrong".

**All three of the above constants are simulator-calibrated. Re-measure them
for the real car** — they belong to the control rate and platform, not the
track.

## Splitting rule — THREE splits, not two (revised 2026-08-06)

**Never split randomly by frame.** Frames *t* and *t+1* are near-duplicates,
so a random split leaks and massively overstates accuracy.

`ml/splits.py` produces three sets, because two conflate two questions:

| Split | What it is | Question |
|---|---|---|
| `fit` | episodes trained on | did it fit |
| `val_indomain` | held-out EPISODES of the same tracks | did it learn, or memorise these runs |
| `holdout` | an entirely unseen TRACK | does it transfer |

**Why three.** Measured 2026-08-06 (record Appendix S): the training tracks
are outdoor and the holdout track is indoor, so "unseen track" was also
"unseen visual domain". With only fit-vs-holdout the VAE looked like it was
overfitting badly; adding `val_indomain` showed fit 56.11 vs val 56.72 — no
overfitting at all, just zero cross-domain transfer. **A random frame split
would have declared success; a two-way split declared failure; only the
three-way split is true.** `val_indomain` is stratified by track so no layout
can silently drop out of training.

Select checkpoints on `val_indomain`, not `holdout` — selecting on a domain
the model was never meant to cover picks an underfit model.

## Current corpus (SIM-POC P2, closed 2026-08-06)

| Split | Track | Episodes | Frames |
|---|---|---|---|
| train | generated-track | 51 | 60,051 |
| train | generated-roads | 27 | 31,627 |
| holdout | waveshare | 10 | 11,210 |
| | **total** | **88** | **102,888** (3.80 GB) |

**Two train layouts, not four** — `mountain-track` and
`roboracingleague-track` are quarantined in `ml/data/sim_quarantine/`
(the expert cannot drive them; see record Appendix P/Q). Train is still
unbalanced 51:27 in favour of `generated-track`.
