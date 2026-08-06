# vision-autonomous-car

A 1/14-scale autonomous car: Lego Technic drivetrain in a 3D-printed frame,
one camera, no LiDAR. The goal is a car that learns to drive from
demonstrations I record, then improves using a world model trained offline on
its own driving logs.

**Status as of 2026-08-06: the software is real and measured. The car is not
built.** Nothing has been 3D-printed and no parts have been ordered. Every
result below is in simulation, and this README says so everywhere it matters.

---

## What actually works right now

A full world-model training pipeline, end to end, on a 102,888-frame driving
corpus collected in simulation.

**A reproduction of Ha & Schmidhuber's World Models** (arXiv:1803.10122),
ConvVAE plus MDN-RNN. The VAE has **4,348,547 parameters, matching the
published figure exactly**, and the assertion runs inside `ConvVAE.__init__`,
so every training and evaluation run re-checks it.
Matching a parameter count to the digit proves every kernel size and channel
width is wired as specified. Reading the code proves nothing of the kind.

Given 32 real frames to warm up its recurrent state, the model then imagines
30 steps forward from its own predictions:

| | step 1 | step 10 | step 30 | beats baseline |
|---|---|---|---|---|
| **seen track, unseen run** | 0.0047 | 0.0071 | 0.0068 | **30 of 30 steps** |
| frozen-frame baseline | 0.0102 | 0.0281 | 0.0313 | |
| **unseen track** | 0.0416 | 0.0645 | 0.1052 | **0 of 30 steps** |

Image MSE. On familiar ground the error stays essentially flat across 30
imagined steps while the baseline degrades threefold. On a track it has never
seen, it loses to simply freezing the last frame, painting trees and sky onto
an indoor scene (`ml/runs/rollout/rollout_holdout.png`).

That baseline is doing the real work in this table. Every frame of a driving
corpus looks vaguely road-like, so "the rollout looks like a track" cannot be
falsified on its own. Measured against a predictor that does nothing, it
becomes a claim.

### DreamerV3 memory on an 8 GB card

The research phase could not find a published VRAM-per-size table for
DreamerV3, so I measured one. RTX 3060 Ti, 8 GB, 64×64 input, fp32,
allocator capped at 7.0 GB:

| config | parameters | peak VRAM | status |
|---|---|---|---|
| S, batch 16, horizon 5 | 19,101,317 | **2.552 GB** | fits |
| S, batch 32, horizon 5 | 19,101,317 | 4.793 GB | fits |
| S, batch 64, horizon 5 | 19,101,317 | — | **OOM above 7.0 GB** |
| S, batch 16, horizon 15 | 19,101,317 | 3.873 GB | fits |
| M, batch 16, horizon 5 | 35,299,397 | 3.729 GB | fits |
| L, batch 16, horizon 5 | 69,654,533 | 5.238 GB | fits |

**Batch size, not model size, is what breaks 8 GB.** A 69.7M-parameter model
fits in 5.24 GB while the 19.1M model at batch 64 does not fit in 7.0 GB.
Activations dominate; weights are nearly free at this scale.

Only "S" is a verified size — it is the reference repo's default config.
M and L are scaling steps I defined and have not checked against the paper's
published size table, so cite the measured parameter counts, not the letters.

A 2000-step run at the top config trained cleanly: image reconstruction loss
fell **588.31 to 61.39**, and peak memory held between 2.550 and 2.552 GB
across all twenty epochs. That 0.002 GB spread is the part that matters — it
means the table above is a steady-state measurement rather than a warm-up
number that would creep once training ran for real.

Reproduce with `python ml/sweep_dreamer_p4.py`.

The reference implementation ships no offline training loop, despite having an
`offline_traindir` flag. The flag only warm-starts the replay buffer; training
steps are still driven by environment steps. `ml/run_dreamer_p4.py` supplies a
real offline loop over the unmodified library code.

---

## Three findings that cost me a wrong answer first

These are in the repo because the mistakes are the useful part.

**A two-way data split told me the model was overfitting. It wasn't.** Both
training tracks are outdoor and the held-out track is indoor, so "unseen
track" was silently also "unseen visual domain", two different questions
wearing one label. Adding a third split (held-out *runs* of the *training*
tracks) showed a train/validation gap of 0.6, meaning no overfitting at all,
just zero cross-domain transfer. A random frame split would have declared
success. A two-way split declared failure. Only the three-way split is true,
and I published the second reading before catching it.

**A verification gate that checked less than its docstring claimed.** The
corpus verifier was supposed to confirm camera frames and steering commands
were aligned on both axes. It only ever checked one. Deliberately corrupting
the corpus — rolling the image array by one and three frames — is what
exposed it: both corruptions passed. Adversarial self-testing found what
reading the code did not.

**A retracted number that had reshaped the plan.** An early research pass
cited "~24 GB VRAM" for DreamerV3, which pushed the world-model milestone to
a stretch goal. A later pass could not locate the source, so the figure was
retracted rather than quietly kept. The measurements above show 8 GB holds
roughly 3.6× the model that number implied.

Corrections are logged as new dated entries that reference the old ones. The
record is append-only; earlier entries are never edited to look smarter.

---

## The hardware, which does not exist yet

Design decisions are settled and costed; nothing is bought.

- **Compute:** Raspberry Pi 5 (4 GB), Camera Module 3 Wide. Inference only.
- **Drive:** Pololu N20 30:1 HP through a Lego differential. Every Lego motor
  was rejected on physics, not price — the fastest option tops out at
  0.88 m/s against a 1.0 m/s floor.
- **Steering:** MG90S servo. Never a plain DC motor: no position feedback
  means no commandable angle, and every model in this project emits a
  steering angle.
- **Power:** split source. USB power bank to the Pi, separate 2S pack to the
  motor and servo, one shared ground. Combining them puts 4.62 A on a 3 A
  rail during a stall and resets the Pi mid-run.
- **Budget:** ≈$178–181, under a $200 ceiling. `docs/BOM.md` is the order list.

A parametric Lego-fit tolerance coupon is generated and geometrically
self-validated (manifold and signed-volume checks pass), but **it has not been
printed**, so every tolerance in it is a prediction, not a measurement.

---

## Layout

```
ml/            world-model pipeline: collection, verification, training, eval
cad/           tolerance coupon (generated, unprinted)
scripts/       parametric STL generation
docs/          research briefs, BOM, and the append-only project record
PRD_ROADMAP.md the standing plan, amended by strike-through, never deletion
HANDOFF.md     current state in one file
```

Runnable checks, each exiting non-zero on failure. The first two run on a bare
clone; the rest need things this repo deliberately does not ship:

```bash
python ml/models.py    # asserts the VAE matches the published param count
python ml/splits.py    # asserts the data split is disjoint and reproducible

# needs the driving corpus (gitignored — regenerate with ml/collect_sim_data.py)
python ml/verify_corpus.py ml/data/sim
python ml/rollout_eval.py

# needs an NVIDIA GPU. Exit 1 here means Sysmem Fallback is ON, which is a
# real finding about the machine, not a broken check.
python ml/probe_vram.py
```

Setup is in `ml/requirements.txt`. The simulator binary and the DreamerV3
reference implementation are fetched separately and not vendored here.

---

## What this is not

It is not a self-driving car. It is not a claim that anything transfers to
hardware — the models have only ever seen a simulator, and sim-trained driving
policies losing to classical control on real hardware is well documented,
which is why training on the physical car's own logs is the actual goal rather
than deploying these weights.

Built as a college-application engineering portfolio project. The
documentation trail is deliberate: `docs/Project Record — Full Chronological
History.md` is append-only, and it keeps the wrong turns.
