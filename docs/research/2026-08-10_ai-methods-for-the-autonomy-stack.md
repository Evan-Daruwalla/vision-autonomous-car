# Research Brief — Which AI method should drive this car?

**Date:** 2026-08-10
**Question:** Given four milestones of measured failure — no learned policy
completes a lap, perception goes out of distribution off-centre, recovery data
fixes the readout 57% with a frozen encoder, and both encoders erase
sub-1%-of-frame objects — what is the right AI method for this car's autonomy
stack: behavioural cloning, an offline world model, offline RL, or classical
CV plus control?

> **CAVEAT ADDED 2026-08-11 (record Appendix AD) — one of the four framing
> premises above has since weakened.** "No learned policy completes a lap" is
> now known to be false in the strict sense (completions occur, just not
> reliably), and every closed-loop number that supported it came from a
> harness later measured at **CV 55%**, where a single launch per arm resolves
> only ~3× differences. **The other three premises are unaffected** — they are
> open-loop measurements that never touched the simulator, and they are what
> the brief's conclusions actually rest on. The findings below (H3 dies; the
> convergent answer is hybrid; DreamerV2's own single-pixel-ball quote) are
> unchanged.
**For:** Evan, and any executing model working PRD M3/M4. This brief is
supposed to settle which branch gets built, so it is written to be
disagreed with — every hypothesis was pre-registered and every arm was
assigned to hunt its own falsifier.
**Method:** Four parallel collection agents, one per pre-registered
hypothesis, each instructed to search for the evidence that would KILL its own
hypothesis rather than support it. Primary sources (arXiv, official docs,
competition results) preferred over commentary; every claim carries a URL and
a date. **Desk research only — nothing in the Findings section was run on
Evan's machine.** Where a claim rests on one source it is tagged
single-source. Where a search came up empty it is recorded as missing rather
than filled in.

**Pre-registration.** H1–H4 were written into record Appendix W.5 on
2026-08-08, BEFORE any collection, as the anti-confirmation-bias gate. The
first collection attempt died on API limits and recorded nothing; this is the
re-run against the identical hypotheses. They were not retrofitted to the
findings.

---

## The four hypotheses, as pre-registered (Appendix W.5)

- **H1** — the binding constraint is DATA COVERAGE, not model class
- **H2** — the binding constraint is the REPRESENTATION (reconstruction is the
  wrong objective)
- **H3** — OFFLINE RL on the reward already in the corpus beats cloning
- **H4 (null)** — classical CV + control is the right answer at this scale and
  the learned stack is portfolio decoration

---

## TL;DR (verdict first)

**No hypothesis wins outright. One dies cleanly, and the survivors converge on
an answer none of them stated: hybrid, with coverage first.**

1. **H3 DIES — the cleanest kill in the brief. Do not build offline RL on this
   corpus.** Every published condition under which offline RL beats cloning —
   sparse reward, noisy or suboptimal data, diverse coverage — is *absent*
   here. The closest-matching published experiment (pixels, 100k transitions,
   continuous control, narrow expert data) reports BC 91.5 and offline
   DreamerV2 **4.8**. The dense centredness reward being "already there and
   unused" is not evidence it is useful.
2. **H1 MIXED — right now, wrong soon.** Coverage is almost certainly what is
   binding at the current wall, and the closest analogue (CIL 2018: 10%
   noise-injected data, 56% → 88%) says the recovery experiment should move the
   number. But "coverage, not model class" is not defensible as a general
   claim: a controlled CARLA ablation bought +17 DS from an architecture change
   and +2 DS from tripling the data.
3. **H2 MIXED — the mechanism is real and cited; the strong form dies.**
   DreamerV2's own authors write that reconstruction loss fails *"because the
   most important object in the game, the ball, occupies only a single pixel."*
   That is this project's 0-of-899-pixels result, named in a primary source.
   But every strongest published fix **keeps** reconstruction and re-aims it,
   and deleting it measurably hurts. "Reconstruction is the wrong objective" is
   too strong; "reconstruction is aimed at the wrong thing" survives.
4. **H4 MIXED — survives narrowly; "learned = decoration" dies.** Classical
   dominates F1TENTH, but that is LiDAR with a prior map. In this project's
   actual regime — camera-only, printed markings, 1/10 scale — the AI Driving
   Olympics winner class **flipped from classical (2018) to learned
   (2019–2021)**.

**The convergent answer, which no single hypothesis proposed:** every recent
result that beats the classical state of the art at this scale is a **hybrid** —
learned residual on a classical controller, learned tuning of pure pursuit,
learned perception feeding a classical controller. Not an end-to-end
replacement. That reframes the PID not as the thing to beat but as the thing to
build on.

**The one finding this brief went looking for and did not expect.** The
controller consumes the MDN-RNN hidden state, and *copycat agents* — BC
policies given observation histories — are documented to learn to predict the
*previous* expert action, with held-out likelihood improving while closed-loop
reward **decreases**. That is exactly the observed signature here: val MSE
~0.005, closed-loop 110/600. **It is a rival explanation for the P5 wall that
is independent of perception and has never been tested.** The test costs one
training run.

---

## H3 — Offline RL on the corpus reward: **DIES**

The corpus carries a dense per-step reward (mean 1.393, ~849 distinct values)
that essentially measures centredness, logged since P2 and used by nothing.
H3 asked whether that free signal beats cloning.

**The direct treatment does not say what H3 needs.** Kumar et al. claim
offline RL's advantage "under specific but common conditions such as **sparse
rewards or noisy data sources**" — neither holds here. Their Practical
Observation 4.1, verbatim: *"When no assumptions are made on the environment
structure, both offline RL and BC perform equally poorly with trajectories
from an expert demonstrator."* Their own caveat is that **naïve** CQL performs
comparably or worse than BC and only wins after a dedicated offline-tuning
workflow.
([arXiv:2204.05618](https://arxiv.org/abs/2204.05618), 2022-04-12, ICLR 2022;
[BAIR blog](https://bair.berkeley.edu/blog/2022/04/25/rl-or-bc/), 2022-04-25)

**The near-exact regime match falsifies H3 outright.** V-D4RL benchmarks
pixel-observation continuous control at **100,000 transitions** — verbatim:
*"By default, each dataset consists of 100,000 total transitions (often 10×
less than in d4rl)"* — against this project's ~92k frames. Its finding,
verbatim: *"pure BC outperforms on the high-quality narrowly-distributed
expert data"*, and *"Offline DV2 is considerably weaker on the expert datasets
that have narrow data distributions."*

| walker-walk (expert) | score | | cheetah-run (expert) | score |
|---|---|---|---|---|
| **BC** | **91.5** | | **BC** | **67.4** |
| CQL | 89.6 | | CQL | 61.5 |
| DrQ+BC | 68.4 | | DrQ+BC | 34.5 |
| Offline DreamerV2 | **4.8** | | Offline DreamerV2 | **10.9** |

([arXiv:2206.04779](https://arxiv.org/abs/2206.04779), 2022-06-09, rev.
2023-07-06, TMLR 2023. Exact table values single-extraction except BC
walker-walk 91.5, independently corroborated.)

This is not an analogy. It is the same cell: pixels, ~100k transitions,
continuous control, narrow near-expert data. And the discarded DreamerV3
actor-critic from P4 belongs to precisely the family that scores 4.8/100 there.

**Three further independent strikes:**

- **Dense reward removes BC's theoretical handicap.** BC's O(H²) compounding
  error is the thing offline RL is supposed to beat; under dense rewards
  offline IL achieves *linear* horizon dependence.
  ([arXiv:2407.15007](https://arxiv.org/abs/2407.15007), 2024-07-20, NeurIPS
  2024)
- **Offline RL generalises WORSE than BC**, which is this project's actual
  failure mode. Verbatim: *"Behavioral cloning is a strong baseline,
  outperforming state-of-the-art offline RL and sequence modeling approaches
  when trained on data from multiple environments and tested on new ones."*
  Also: *"increasing the diversity of the data, rather than its size, improves
  performance on new environments"* — and this corpus was deliberately
  filtered to *reduce* diversity (rejecting mean|cte| > 1.2).
  ([arXiv:2312.05742](https://arxiv.org/abs/2312.05742), 2023-12-10, ICLR 2024)
- **Decision Transformer is contraindicated by its own paper**: it wins in
  *"sparse-reward and low-quality data settings"* and needs *more* data than
  CQL — the complement of this project's profile.
  ([arXiv:2305.14550](https://arxiv.org/abs/2305.14550), 2023-05-23)

**The honest counterweight, because it is the one condition this project does
meet.** Kumar's Practical Observation 4.2 names a second win condition:
*"when the initial state distribution changes during deployment."* A BC policy
that drifts off-centre and never recovers IS a deployment-distribution-shift
failure. But the same logic points at the fix: distribution shift is cured by
**state coverage**, and this project has already measured a 57% perception-error
reduction from recovery data. That is in-project evidence that coverage, not
the objective, is the live lever — consistent with the "diversity, not size"
finding above, and it feeds H1 rather than rescuing H3.

**One genuine caveat on the framing.** The tuning objection that usually sinks
offline RL — you cannot select a policy without online evaluation — does *not*
apply here, because gym_donkeycar makes online rollouts cheap. But that fact
argues *against* H3, not for it: if online interaction is available, the dense
reward is far more valuable driving **online** RL or offline-pretrain →
online-finetune than pure offline RL. On the DonkeyCar platform specifically,
L2D reports online RL learning to drive from scratch "in less than five
minutes of interaction" and driving "faster than imitation learning and a
human operator" ([arXiv:2008.00715](https://arxiv.org/abs/2008.00715),
2020-08-03) — the only platform-matched result that beats imitation, and it
beats it by *interacting*, not by mining a fixed corpus.

**Missing, and reported as missing:** no published offline-RL result on
donkeycar / gym-donkeycar exists at all; no IQL result on pixels at ~100k
transitions (V-D4RL does not benchmark IQL); Kumar et al.'s per-task tables
could not be reliably extracted (two extractions disagreed), so only its
verbatim Practical Observations are treated as reliable here.

---

## H2 — The representation is the constraint: **MIXED**

The mechanism is real and the primary sources are unusually direct about it.
H2's *strong* form does not survive.

**The architecture in use self-reports the failure.** Ha & Schmidhuber,
*World Models*, Discussion, verbatim: *"The choice of implementing V as a VAE
and training it as a standalone model also has its limitations, since it may
encode parts of the observations that are not relevant to a task. After all,
unsupervised learning cannot, by definition, know what will be useful for the
task at hand."* They report the VAE reproducing wall tile patterns while
failing to reproduce task-relevant road tiles.
([worldmodels.github.io](https://worldmodels.github.io/),
[arXiv:1803.10122](https://arxiv.org/abs/1803.10122), 2018-03-27)

**DreamerV2's own paper states this project's exact finding.** Verbatim:
*"We hypothesize that the reconstruction loss of the world model does not
encourage learning a meaningful latent representation because the most
important object in the game, the ball, occupies only a single pixel."*
([arXiv:2010.02193](https://arxiv.org/abs/2010.02193), 2020-10-05, ICLR 2021)
Stated earlier as a loss-share argument: *"Since the ball is very small, it is
mostly ignored by the reconstruction loss of a VAE. The contribution of one
pixel to the overall loss is negligible."*
([arXiv:1904.01318](https://arxiv.org/abs/1904.01318), 2019-04-02)

**This is the citation for W.2's 0-of-899-pixels result.** The measurement was
not a bug and is not exotic; it is a documented, named failure mode of
reconstruction-trained latents, replicated across five modern world models
(DreamerV3, DIAMOND, TWISTER, Simulus, STORM) in Pong, where *"Many of these
rollout failures involve the ball and its interactions, despite the ball
occupying only a few pixels."*
([arXiv:2607.15142](https://arxiv.org/abs/2607.15142), 2026-07-16, preprint,
not peer-reviewed)

**But the strong form dies — and this directly shapes the M4 fix.**

- **The best published fixes KEEP reconstruction and re-aim it.** CGSReg adds
  *more* pixel reconstruction, weighted onto segmented concept regions, and
  moves frozen-world-model Pong returns from −21.00 to −11.90 (DreamerV3) and
  −21.00 to −1.90 (TWISTER). Segmentation Dreamer, SEM2 and MILE all
  reconstruct a *different target* (masks, BEV semantics) rather than dropping
  reconstruction. MILE reports +31% driving score on a held-out CARLA
  town/weather ([arXiv:2210.07729](https://arxiv.org/abs/2210.07729), NeurIPS
  2022).
- **Masked World Models keeps pixel reconstruction entirely** and fixes only
  the architecture — masking convolutional features instead of pixel patches —
  reaching RLBench Reach Target >80% vs DreamerV2's <20%, a task defined by a
  small target. This is the sharpest single falsifier of "reconstruction is
  the wrong objective."
  ([arXiv:2206.14244](https://arxiv.org/abs/2206.14244), 2022-06-28, CoRL 2022)
- **Deleting reconstruction measurably hurts.** HarmonyDream's ablation shows
  observation modelling *improves* reward modelling (reward loss 0.379 with it
  on vs 0.416 with it off). TD-MPC2 is decoder-free and beats DreamerV3 on
  hard continuous control but is reported to fail on sparse-reward and
  precision tasks.
  ([arXiv:2310.00344](https://arxiv.org/abs/2310.00344), ICML 2024;
  [arXiv:2310.16828](https://arxiv.org/abs/2310.16828), ICLR 2024)

**Loss balance is the cheap lever, with a number attached.** HarmonyDream
finds observation loss dominating reward loss "at two orders of magnitude
greater scale", and simply raising the reward coefficient from 1 to 100
sharply improves sample efficiency. That is direct support for sweeping the
aux weight across 10/100/1000 rather than picking one — a weight that is 4% of
total loss cannot reshape an encoder.

**An unexcluded confound this brief will not paper over: z=32 capacity.**
Emu reports that a 4-channel autoencoder loses detail *"especially noticeable
in small objects"*, with 16 channels improving SSIM, PSNR and FID across the
board ([arXiv:2309.15807](https://arxiv.org/abs/2309.15807), 2023-09-27).
This project's ConvVAE is z=32 continuous. That the DreamerV3 RSSM (32×32
discrete) *also* erased the cone argues against pure capacity being the whole
story, but does not close it — the two encoders differ in more than capacity.
**"H2-capacity" remains a live rival to "H2-objective" and is not settled by
anything measured so far.**

**The counter-cite to expect.** One 2026 single-author preprint reports
IRIS/DIAMOND latents carrying *linearly* decodable object positions with
causal interventions confirming use
([arXiv:2603.21546](https://arxiv.org/abs/2603.21546), 2026-03-23). Different
architecture family (transformer/diffusion, Atari) from this ConvVAE, but it
is the paper that would be cited against Appendix Y.2's probe result.

**Two things this project appears to have measured that the literature has
not:**

1. **The scale-invariance corollary is unsourced.** No paper states that
   because reconstruction loss is a *mean* over pixels, an object's gradient
   share equals its area fraction and is therefore invariant to input
   resolution. The nearest published statements give the *magnitude* claim
   without the resolution corollary. **This must be presented as Evan's own
   derivation, not a citation** — which is how PRD 6(b) and Appendix Y.1
   already label it. No experiment testing "does raising resolution alone
   restore small objects in a world-model latent" was found either; CGSReg
   explicitly did not test it.
2. **The paint-out probe appears novel as a measurement.** No published
   cone- or sign-scale object-retention measurement for a ConvVAE latent on a
   1/10–1/14 scale car was found, and no driving paper isolates sign retention
   in a world-model latent with a causal ablation of the kind in Appendix Y.2.

---

## H1 — Data coverage is the binding constraint: **MIXED**

Best one-line summary: **H1 is right now and will be wrong soon.** Coverage is
almost certainly what is binding at the current wall, but "coverage, not model
class" is not defensible as a general claim, and the falsifiers say so with
controlled ablations.

**The closest published analogue strongly supports the recovery experiment.**
Conditional Imitation Learning collected 2 hours of driving of which *"only
10% (roughly 12 minutes) contain demonstrations with injected noise."*
Ablation, success rate (km between infractions):

| | with noise data | without |
|---|---|---|
| Town 1 (seen) | **88%** (2.34) | 56% (1.31) |
| Town 2 (unseen) | **64%** (1.18) | 22% (0.54) |

On the physical car, removing the noise data raised interventions from 0.67 to
8.67 and missed turns from 0% to 24.4%. Verbatim: *"a relatively small amount
of such data proved very effective in stabilizing the learned policy."*
([arXiv:1710.02410](https://arxiv.org/abs/1710.02410), 2017-10-06, ICRA 2018)

**This project's recovery set is 6.67% of corpus against CIL's 10% — the same
order.** That is the single best reason to expect the closed-loop test to move,
and it is the right comparison to put in the record.

**What DART actually reports, since this project chose it.** Up to 3× faster in
computation and only 5% cumulative-reward loss during training vs DAgger's 80%;
79% vs 49% success on robot grasping in clutter.
([arXiv:1703.09327](https://arxiv.org/abs/1703.09327), CoRL 2017) Two caveats
that matter here:

- **DART has never been evaluated on driving or lane-keeping.** MuJoCo
  locomotion plus one grasping task. There is no published DART-on-driving
  number to compare against.
- **On the one axis where the comparison was fair — an *algorithmic* supervisor
  — DART only reaches "parity with DAgger."** Its wins came from human-
  supervisor cost. This project's expert is a scripted PID, so all three of
  DART's stated advantages over DAgger (tedium, danger, retraining burden)
  largely collapse in sim. The DART choice is still right, but **for a
  different reason than the paper's**: it is the one that transfers to the
  physical car, where querying an expert means a human riding along. That
  reasoning should be stated as the justification, not the paper's headline.
- DART's own authors concede it is a data-insufficiency patch: *"noise
  injection will offer no improvement if the robot can represent the supervisor
  perfectly and collect sufficient data."*

**The falsifiers, and they are strong:**

- **F1 — architecture beat data 8:1 in a controlled CARLA ablation.** Jaeger et
  al.'s cumulative Longest6 table: adding a transformer decoder = **+17 DS**;
  tripling the dataset 185k→555k frames = **+2 DS**; shift/rotation
  augmentation = +9 DS.
  ([arXiv:2306.07957](https://arxiv.org/abs/2306.07957), 2023-06-13, ICCV 2023)
- **F3 — closed-loop performance plateaus with data while capacity keeps
  paying.** NVIDIA, 16h → 8192h: *"the MDBF results improved only up to the
  256-hour mark, beyond which they plateaued around 1 km"*, while a ResNet-50
  reached the same error with 63% less data than a ResNet-18.
  ([arXiv:2504.04338](https://arxiv.org/abs/2504.04338), 2025-04-06)
- **F4 — the World Models authors prescribe a model-class fix for exactly this
  symptom.** Their VAE "failed to reproduce task-relevant tiles on the road",
  and their proposed remedy is *"training together with an M that predicts
  rewards"* so the VAE learns to focus on task-relevant areas. That is the
  auxiliary-supervision direction PRD 6(b) just committed to, arriving from a
  completely independent line of evidence.
- **F5 — the frozen encoder may itself be the ceiling.** Frozen representations
  *"fare better in the very low-data regime but overall performance is
  bottlenecked by policy learning"* and suffer a domain gap *"which is
  alleviated by finetuning."*
  ([arXiv:2212.05749](https://arxiv.org/abs/2212.05749), ICML 2023) Appendix
  X.1's 57% improvement was obtained **with the encoder frozen**, so it is
  plausibly leaving performance on the table.

**F8 is a direct warning about how X.1 must be reported.** *"offline prediction
error is not necessarily correlated with driving quality, and two models with
identical prediction error can differ dramatically in their driving
performance."*
([arXiv:1809.04843](https://arxiv.org/abs/1809.04843), ECCV 2018) **A 57% cut
in an offline probe is not evidence of a closed-loop fix. Only a lap count
is.** Appendix X.1 already refused to make that claim; this is the citation for
why that refusal was correct.

**F7 is the finding this brief did not go looking for, and it is a live risk in
the current stack.** Copycat agents: with observation *histories*, a BC policy
learns to predict the *previous* expert action; held-out likelihood improves
while environment reward **decreases**, and the paper is explicit that this is
not overfitting.
([arXiv:2010.14876](https://arxiv.org/abs/2010.14876), NeurIPS 2020)

**This controller consumes the MDN-RNN hidden state `h`.** And the observed
pattern is exactly the copycat signature: excellent held-out MSE (~0.005) with
catastrophic closed-loop failure. **This is a rival explanation for the P5 wall
that is independent of perception, and it has never been tested.** The test is
cheap: train a controller on `z` alone with `h` zeroed and compare closed-loop
survival. If the z-only controller drives *further*, the history input is
hurting, and no amount of recovery data will fix that.

### A correction to this arm's own recommendation

The H1 agent named target-point conditioning as "the single most actionable
falsifier", on the basis that *"gym_donkeycar exposes track waypoints."*
**It does not.** Verified directly against
`.venv/Lib/site-packages/gym_donkeycar/envs/donkey_sim.py` on 2026-08-10: the
info dict returns `pos, cte, speed, forward_vel, hit, gyro, accel, vel, lidar,
car(roll/pitch/yaw), last_lap_time, lap_count` and the sim's message table has
no waypoint or path message. A target point could be *constructed* by logging
expert `pos` into a centreline and looking ahead, but that needs `pos` at
inference time — **privileged localization the physical car will not have.**
So TP conditioning is a sim-only shortcut that does not transfer, which is the
opposite of why DART was chosen. Recorded here because the underlying finding
(Jaeger's TP mechanism *is* how SOTA CARLA methods recover laterally) is real
and useful, while the proposed action for this project is not available.

---

## H4 (null) — Classical CV + control is the right answer: **MIXED**

H4 survives narrowly. Its **strong form — "the learned stack is portfolio
decoration" — dies.**

**The competition record backs classical, but mostly in a different regime.**
F1TENTH winners are overwhelmingly classical: ICRA 2024 GP won by VAUL with
SLAM → particle filter → offline optimal trajectory → **Pure Pursuit** (MPC
explicitly rejected as too expensive onboard); ForzaETH won German GP 2022 and
ICRA GP 2023 with a classical modular stack; Penn won the 12th GP in 2023 with
planning and control. The benchmark survey is blunt — lap times in seconds:

| method | AUT | ESP | GBR | MCO |
|---|---|---|---|---|
| Optimisation & tracking (classical, mapped) | **16.79** | **35.92** | **31.24** | **28.08** |
| MPCC (classical) | 16.87 | 39.13 | 35.40 | 31.53 |
| Follow-the-Gap (classical, **mapless**) | 19.10 | 45.78 | 39.34 | 34.99 |
| End-to-end DRL | 19.94 | 46.37 | 40.22 | 34.93 |

End-to-end agents are *"significantly slower"*, and note the mapless classical
baseline also beats end-to-end DRL — so the classical edge is not purely "it
got a map." ([arXiv:2402.18558](https://arxiv.org/abs/2402.18558), 2024-02-28)

**But F1TENTH is 2D LiDAR with a prior SLAM map. This car is camera-only.**
That is the Duckietown/DonkeyCar regime — **and there the winner class flipped**:

| AI Driving Olympics, lane following | winner method |
|---|---|
| AI-DO 1 (NeurIPS 2018) | **classical** — top 3 all classical, RL placed 4th and 5th |
| AI-DO 3 (2019/20) & AI-DO 5 (NeurIPS 2020) | **imitation learning** (sim + real jointly) |
| AI-DO 6 (NeurIPS 2021) | **PPO + domain randomization**, sim-only training |

The AI-DO 2018 organizers also noted most real-world entries were *"not
surviving for more than 3 seconds"* — sim-to-real, not algorithm class, was
the binding constraint. ([Duckietown results pages;
arXiv:1903.02503](https://arxiv.org/abs/1903.02503), 2019-03-06;
[arXiv:2007.03514](https://arxiv.org/abs/2007.03514), 2020-07-07)

**The cleanest camera-only head-to-head found, and it favours classical.**
PIX Moving hackathon, Guiyang, May 2019, fastest single lap on a real track:
best deep-learning car **9.75 s**, best optimal-control (classical) car
**~8 s** — roughly an 18% classical advantage. Notably, what fixed the CNN
was a *classical* front-end: HSV colour thresholding to mask glare, after
saliency maps showed the network attending to *"background objects and
sunlight reflections, anything but not the track lanes."*

**Falsifiers, and they are specific:**

- **Residual learning on top of a classical controller beats the classical
  SotA** — by the same ETH group that holds it: up to **11.5% faster laps with
  20 minutes of on-car training**, no sim pre-training.
  ([arXiv:2505.07321](https://arxiv.org/abs/2505.07321), 2025-05-12)
- **Model-based RL beat a tuned MPPI planner on a real 1/10 car** — the closest
  published analogue to this project's CEM-planner failure, with MPPI given the
  *same* predictive model and *same* reward. TD-MPC2 surpassed it; PPO and SAC
  did not. ([arXiv:2604.07672](https://arxiv.org/abs/2604.07672), 2026-04-09,
  single-source, very recent)
- **The world-model family works at this scale** — Dreamer-style latent
  imagination on an F1TENTH robot *"substantially outperform[s] model-free
  agents"* and generalizes from one map to unseen tracks. Caveat: baselines are
  model-free RL, **not classical**, and it is LiDAR.
  ([arXiv:2103.04909](https://arxiv.org/abs/2103.04909), ICRA 2022)
- **The stop sign is the weakest part of H4, but weaker than expected.** GTSRB:
  CNN with spatial transformers **99.71%**, human 98.84%, best hand-crafted
  classical (COSFIRE colour-blob filters) **98.97%**. The learned advantage is
  real but it is not a chasm — and GTSRB is *classification of pre-cropped
  signs*, not detection at range in a cluttered frame, which is the actual
  task. Do not oversell this one.

**Where the evidence actually converges: hybrid.** Every recent result that
beats the classical state of the art at this scale is a hybrid, not an
end-to-end replacement — learned residual on a classical controller, learned
*tuning* of pure pursuit, learned perception feeding a classical Stanley
controller (MIND-Stack, IEEE IV 2025), classically-computed racing line
injected into the RL reward. Even ForzaETH's flagship classical stack is going
hybrid at the edges.

**On portfolio credibility, this arm refused to speculate and that refusal
stands.** No real evidence was found about how college-admissions reviewers
weigh a working classical baseline plus an honest negative result. The
adjacent ML-peer-review evidence cuts the *other* way: ICML 2024's position
paper on negative results argues the field currently **under**-rewards them —
*"if a new method or algorithm is not able to beat the state-of-the-art on a
typical benchmark dataset, researchers might quickly abandon their work"* —
i.e. a negative result is a harder sell, not an easier one. The ICBINB
workshop series exists precisely because that class of work needs its own
venue. **Nobody should put a number on the admissions question, and this brief
does not.**
([arXiv:2406.03980](https://arxiv.org/abs/2406.03980), ICML 2024;
[icbinb.cc](https://icbinb.cc/))

**The most useful single line from this arm:** no apples-to-apples comparison
of classical CV+PID versus a learned policy on the *same* camera-only
1/10-scale car, same track, with published numbers, appears to exist. **This
project's PID 9/9 vs learned 110/600 is a comparison nobody has published** —
which argues for documenting it carefully rather than treating it as an
embarrassment.

---

## Ranked: what to actually build next

Ranked by evidence strength ÷ cost. One-line tradeoff each.

1. **Finish the closed-loop recovery test.** Already in flight. CIL 2018 says
   10% recovery data flipped 56% → 88%; this corpus is at 6.67%. *Tradeoff:
   none — it is the cheapest decisive experiment available, and Codevilla
   (ECCV 2018) says the 57% probe improvement is not evidence without it.*
2. **Test the copycat hypothesis: train a controller on `z` alone, `h` zeroed.**
   One training run against checkpoints that already exist. *Tradeoff: if the
   z-only controller drives further, a chunk of the P5 narrative needs
   rewriting — which is a reason to run it, not to avoid it.*
3. **Aux head / joint encoder training** (in flight). Ha & Schmidhuber
   prescribe exactly this for exactly this symptom, arriving independently of
   the PRD decision. *Tradeoff: needs a VAE retrain (Appendix Y.2), and the
   z=32 capacity confound stays unexcluded either way.*
4. **Unfreeze / finetune the encoder.** Frozen representations are documented
   to be bottlenecked by policy learning, and X.1's 57% was measured frozen.
   *Tradeoff: breaks the frozen-encoder comparability that P3–P5 results rest
   on; do it as a new arm, not a replacement.*
5. **Hybrid: a classical CV front-end feeding the learned stack.** The PIX
   Moving fix for a camera-only 1/10 car was HSV glare masking in front of the
   CNN. *Tradeoff: less "pure" as a portfolio story, but it is what the
   evidence actually supports and it is honest about why.*
6. **DO NOT build offline RL on this corpus.** H3, decisively. *If the dense
   reward is to be used at all, use it for online or offline-pretrain →
   online-finetune, where the platform-matched L2D result lives.*
7. **DO NOT raise input resolution as the small-object fix.** No published
   experiment tests it, and the scale-invariance argument against it is
   unsourced — meaning there is no evidence either way, which is a reason not
   to spend the P3/P4 comparability on it.

## What would change these conclusions

- **A lap count.** If the closed-loop test shows no improvement, H1's "coverage
  is binding *now*" weakens sharply and attention should move to the copycat
  test and the encoder.
- **The z-only controller beating z+h.** Would make copycat, not perception,
  the primary P5 explanation and would partially invalidate the framing in
  Appendices V–X.
- **The aux head failing at every swept weight.** Would mean a z=32 bottleneck
  cannot retain a sub-1%-of-frame object even under direct supervision,
  reopening PRD 6(b) toward larger z or a detection path outside the latent.
- **A resolution ablation.** Nobody has published one. Running it would settle
  an argument this project currently makes on reasoning alone.

## Limitations of this brief

- **Desk research only.** Nothing in Findings was run on Evan's machine. Every
  number is someone else's measurement on someone else's setup.
- **Table values were extracted by agents from HTML/PDF and are not all
  independently line-checked.** Where an extraction was inconsistent it is
  flagged in the section (Kumar et al.'s per-task tables; Codevilla 2019's
  per-dataset-size cells) and the verbatim quotes are treated as the reliable
  part.
- **One agent claim was checked and found wrong** — gym_donkeycar does not
  expose waypoints (see the correction under H1). Others were not
  independently re-verified at that depth.
- Several primary PDFs defeated text extraction (Prakash CVPR 2020, DAgger,
  MIND-Stack, Learning-to-Tune-Pure-Pursuit); those are cited at abstract level
  and marked.
- **No competition evidence later than May 2024** could be retrieved for
  F1TENTH/Roboracer; if the winner class has flipped since, this brief cannot
  see it.

## Sources

Consolidated; every entry dated. Grouped by the arm that surfaced it. Full
per-claim URLs are inline in the sections above.

**Imitation learning, covariate shift, recovery data (H1)** — DART
(arXiv:1703.09327, 2017-03-27, CoRL 2017) · Conditional Imitation Learning
(arXiv:1710.02410, 2017-10-06, ICRA 2018) · PilotNet (arXiv:1604.07316,
2016-04-25) · ChauffeurNet (arXiv:1812.03079, 2018-12-07) · Limitations of
Behavior Cloning (arXiv:1904.08980, 2019-04-18, ICCV 2019) · Offline Evaluation
of Driving Models (arXiv:1809.04843, 2018-09-13, ECCV 2018) · Learning by
Cheating (arXiv:1912.12294, 2019-12-27) · Hidden Biases of End-to-End Driving
Models (arXiv:2306.07957, 2023-06-13, ICCV 2023) · Hidden Biases of End-to-End
Driving Datasets (arXiv:2412.09602, 2024-12-12) · Data Scaling Laws for
End-to-End AD (arXiv:2504.04338, 2025-04-06) · Pre-Training for Visuo-Motor
Control (arXiv:2212.05749, 2022-12-12, ICML 2023) · Causal Confusion in
Imitation Learning (arXiv:1905.11979, 2019-05-28) · **Copycat Agents
(arXiv:2010.14876, 2020-10-28, NeurIPS 2020)** · SafeDAgger (arXiv:1605.06450,
2016-05-20) · Data Scaling Laws in Robotic Manipulation (arXiv:2410.18647,
ICLR 2025) · DAgger (arXiv:1011.0686, 2010-11-02)

**Representation / world models (H2)** — World Models (arXiv:1803.10122,
2018-03-27) · **DreamerV2 (arXiv:2010.02193, 2020-10-05, ICLR 2021)** ·
Weaknesses of Deep RL Agents (arXiv:1904.01318, 2019-04-02) · CGSReg
(arXiv:2607.15142, 2026-07-16, preprint) · OC-STORM (arXiv:2501.16443,
2025-01-27) · Masked World Models (arXiv:2206.14244, 2022-06-28, CoRL 2022) ·
HarmonyDream (arXiv:2310.00344, ICML 2024) · MuDreamer (arXiv:2405.15083,
2024-05-23) · Value Equivalence Principle (arXiv:2011.03506, 2020-11-06) ·
What model does MuZero learn? (arXiv:2306.00840, 2023-06-01) · SEM2
(arXiv:2210.04017, 2022-10-08) · MILE (arXiv:2210.07729, 2022-10-14) ·
Segmentation Dreamer (arXiv:2410.09972, 2024-10-13) · TD-MPC2
(arXiv:2310.16828, 2023-10-25) · CURL (arXiv:2004.04136) / RAD
(arXiv:2004.14990) / SPR (arXiv:2007.05929) · DINO-WM (arXiv:2411.04983,
2024-11-07) · Emu (arXiv:2309.15807, 2023-09-27) · Probing Latent
Representations (arXiv:2603.21546, 2026-03-23, counter-cite)

**Offline RL (H3)** — **Kumar et al., Offline RL vs BC (arXiv:2204.05618,
2022-04-12, ICLR 2022)** + BAIR blog 2022-04-25 · **V-D4RL (arXiv:2206.04779,
2022-06-09, TMLR 2023)** · Generalization Gap in Offline RL (arXiv:2312.05742,
2023-12-10, ICLR 2024) · Is Behavior Cloning All You Need? (arXiv:2407.15007,
2024-07-20, NeurIPS 2024) · When to prefer Decision Transformers
(arXiv:2305.14550, 2023-05-23) · RCSL limits (arXiv:2206.01079, 2022-06-02) ·
DreamerV3 (arXiv:2301.04104, 2023-01-10) · IQL (arXiv:2110.06169) · Optimistic
Perspective on Offline RL (arXiv:1907.04543, ICML 2020) · **L2D on real
DonkeyCar (arXiv:2008.00715, 2020-08-03)** · Offline Tutorial
(arXiv:2005.01643, 2020-05-04)

**Small-scale platforms, classical vs learned (H4)** — F1TENTH benchmark survey
(arXiv:2402.18558, 2024-02-28) · ForzaETH Race Stack (arXiv:2403.11784,
2024-03-18) · VAUL ICRA 2024 GP writeup (Foxglove) · Penn 12th GP, 2023-05-09 ·
AI-DO 1 results (Duckietown, 2018-12-08) · AI-DO 3 winners (Duckietown,
2020-01-14) · AI-DO 6 (SmartLab AI, Dec 2021) · AI-DO at NeurIPS 2018
(arXiv:1903.02503, 2019-03-06) · AI-DO imitation-learning winner
(arXiv:2007.03514, 2020-07-07) · DIY Robocars post-race analysis (2017-01-24)
and standings (2018-03-20) · PIX Moving hackathon (Felix Yu, 2019-06-04) ·
**Drive Fast, Learn Faster (arXiv:2505.07321, 2025-05-12)** · Reset-Free RL for
Agile Driving (arXiv:2604.07672, 2026-04-09) · Latent Imagination in Racing
(arXiv:2103.04909, 2021-03-08, ICRA 2022) · TinyLidarNet (arXiv:2410.07447,
2024-10-09) · OC vs RL, Science Robotics 8(82) (arXiv:2310.10943, 2023-10-17) ·
Trajectory-aided DRL (arXiv:2306.07003, 2023-06-12) · MIND-Stack
(arXiv:2505.21734, 2025-05-27) · Learning to Tune Pure Pursuit
(arXiv:2602.18386, 2026-02-23) · Small-Scale Cars survey (arXiv:2404.06229,
2024-04) · Hough lane-detection limits (Int. J. Adv. Robotic Systems,
2021-04-15) · LanEvil (arXiv:2406.00934, 2024-06) · GTSRB results table ·
AWS DeepRacer (product page; league finale writeup 2025-02-28) · Embracing
Negative Results in ML (arXiv:2406.03980, ICML 2024) · ICBINB workshop series
