"""SIM-POC P3 done-check: multi-step imagination rollouts.

Warms the LSTM on `--warmup` real frames (teacher forcing), then cuts the
frames off and lets the model hallucinate forward, feeding its OWN predicted
z_{t+1} back in while following the REAL recorded actions. Decoding those
imagined latents through the VAE turns the world model's internal state into
pictures a human can judge.

Using the real action sequence is deliberate: it isolates the DYNAMICS model.
If the car's imagined future diverges, that is the world model failing to
predict, not a policy choosing differently.

Two outputs:
  rollout_<split>.png   ground truth vs imagined, over the horizon
  rollout_metrics.json  latent L2 and decoded-image MSE vs horizon step,
                        with a same-frame baseline for scale

**The baseline matters.** An imagined rollout that looks vaguely road-like
proves nothing on its own -- every frame of a driving corpus looks vaguely
road-like. So error is reported against a "freeze the last real frame"
predictor: beating it means the model is genuinely predicting motion, not
just reproducing the average road scene.

Usage:  python ml/rollout_eval.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from models import ConvVAE, MDNRNN, mdn_sample
from splits import (cache_key_matches, encoder_fingerprint,
                    fit_val_episodes, load_proc)

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs"

# Fraction of imagined steps on which val_indomain must beat the frozen-frame
# baseline for the P3 done-check to pass. Observed 30/30; 0.9 leaves three
# steps of headroom so seed variance does not fail a correct model.
MIN_BEAT_FRACTION = 0.9


@torch.no_grad()
def rollout(vae, rnn, mu_all, act_all, start, warmup, horizon, device,
            temperature=1.0, seed=0):
    """Imagine `horizon` steps after `warmup` teacher-forced steps.

    Returns (imagined_z, true_z, actions_used).
    """
    # Determinism comes from the global seed below. A local torch.Generator was
    # created here and never passed to anything -- it read as a per-rollout
    # determinism guarantee that did not exist (cold audit finding 12).
    torch.manual_seed(seed)

    total = warmup + horizon
    z_true = torch.from_numpy(mu_all[start:start + total + 1]).to(device)
    a = torch.from_numpy(act_all[start:start + total]).to(device)

    # teacher forcing: real latents in, LSTM state carried forward
    state = None
    if warmup > 0:
        _, _, _, state = rnn(z_true[:warmup].unsqueeze(0),
                             a[:warmup].unsqueeze(0))

    z = z_true[warmup].unsqueeze(0).unsqueeze(0)     # (1,1,Z) last real latent
    imagined = []
    for t in range(horizon):
        logpi, mu, ls, state = rnn(z, a[warmup + t].view(1, 1, -1), state)
        z = mdn_sample(logpi, mu, ls, temperature=temperature)
        imagined.append(z.squeeze(0).squeeze(0))
    return torch.stack(imagined), z_true[warmup + 1: warmup + 1 + horizon], a


@torch.no_grad()
def decode(vae, z, device):
    img = vae.decode(z.to(device))
    return (img.clamp(0, 1).permute(0, 2, 3, 1).cpu().numpy() * 255).astype(np.uint8)


def strip(frames: np.ndarray, every: int) -> np.ndarray:
    return np.concatenate(list(frames[::every]), axis=1)


@torch.no_grad()
def run_split(tag, imgs, mu_all, act_all, episodes, ep_idx, vae, rnn, args, out):
    device = args.device
    rng = np.random.default_rng(args.seed)

    # pick episodes long enough to hold warmup + horizon.
    # Strictly GREATER than `need`, not >=: line 108 draws a start offset with
    # rng.integers(0, n - need), and an episode of exactly `need` frames makes
    # that rng.integers(0, 0) -> ValueError after the models are already loaded.
    # Reachable today with --warmup 369 --horizon 30 against the 401-frame
    # episodes in this corpus. (Cold audit E6, 2026-08-06.)
    need = args.warmup + args.horizon + 2
    usable = [i for i in ep_idx if episodes[i][1] > need]
    if not usable:
        raise SystemExit(f"{tag}: no episode has {need} frames")
    chosen = rng.choice(usable, size=min(args.n_episodes, len(usable)),
                        replace=False)

    lat_err, img_err, base_err = [], [], []
    panels = []

    for k, ep in enumerate(chosen):
        s, n = episodes[ep]
        start = int(s) + int(rng.integers(0, n - need))
        imag, true, _ = rollout(vae, rnn, mu_all, act_all, start,
                                args.warmup, args.horizon, device,
                                args.temperature, seed=args.seed + k)

        lat_err.append(torch.linalg.norm(imag - true, dim=-1).cpu().numpy())

        gt_frames = np.array(imgs[start + args.warmup + 1:
                                  start + args.warmup + 1 + args.horizon])
        pred = decode(vae, imag, device)
        # baseline: freeze the last REAL frame for the whole horizon
        frozen = np.array(imgs[start + args.warmup])[None].repeat(args.horizon, 0)

        gt_f = gt_frames.astype(np.float32) / 255.0
        img_err.append(((pred.astype(np.float32) / 255.0 - gt_f) ** 2)
                       .reshape(args.horizon, -1).mean(1))
        base_err.append(((frozen.astype(np.float32) / 255.0 - gt_f) ** 2)
                        .reshape(args.horizon, -1).mean(1))

        if k < args.n_panels:
            every = max(1, args.horizon // args.n_shown)
            panels.append(np.concatenate([strip(gt_frames, every),
                                          strip(pred, every)], axis=0))

    if panels:
        # 2-pixel white rule between episodes so the pairs are readable
        sep = np.full((4, panels[0].shape[1], 3), 255, np.uint8)
        stacked = panels[0]
        for p in panels[1:]:
            stacked = np.concatenate([stacked, sep, p], axis=0)
        Image.fromarray(stacked).save(out / f"rollout_{tag}.png")

    return {
        "episodes": len(chosen),
        "latent_l2_by_step": np.mean(lat_err, axis=0).round(3).tolist(),
        "image_mse_by_step": np.mean(img_err, axis=0).round(5).tolist(),
        "frozen_baseline_mse_by_step": np.mean(base_err, axis=0).round(5).tolist(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warmup", type=int, default=32)
    ap.add_argument("--horizon", type=int, default=30)
    ap.add_argument("--n-episodes", type=int, default=8)
    ap.add_argument("--n-panels", type=int, default=3)
    ap.add_argument("--n-shown", type=int, default=10, help="frames per strip")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--rnn", default=str(RUNS / "mdnrnn" / "mdnrnn_best.pt"))
    ap.add_argument("--out", default=str(RUNS / "rollout"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(args.seed)

    vae_ckpt = torch.load(args.vae, map_location=args.device)
    vae = ConvVAE().to(args.device)
    vae.load_state_dict(vae_ckpt["model"])
    vae.eval()
    rnn = MDNRNN().to(args.device)
    rnn.load_state_dict(torch.load(args.rnn, map_location=args.device)["model"])
    rnn.eval()

    tr_imgs, tr_act, tr_eps, tr_tracks = load_proc("train")
    ho_imgs, ho_act, ho_eps, _ = load_proc("holdout")
    tr_mu = np.load(REPO / "ml" / "data" / "proc" / "train_mu.npy")
    ho_mu = np.load(REPO / "ml" / "data" / "proc" / "holdout_mu.npy")

    # These latents were produced by train_mdnrnn.py under SOME VAE. If that
    # was a different checkpoint than the one loaded above, this script decodes
    # dynamics from one latent space through another and reports the resulting
    # nonsense as a result. Missing sidecar => UNVERIFIABLE (caches predating
    # this guard have none); present-and-different => WRONG, and we stop.
    want = encoder_fingerprint(args.vae)
    for split in ("train", "holdout"):
        keyfile = REPO / "ml" / "data" / "proc" / f"{split}_latents.key"
        if not keyfile.exists():
            print(f"note: {split} latent cache has no encoder fingerprint - "
                  f"cannot verify it matches {Path(args.vae).name}; re-run "
                  f"train_mdnrnn.py to stamp it")
        elif not cache_key_matches(split, want):
            print(f"FAIL: {split} latents were encoded by a DIFFERENT VAE than "
                  f"{Path(args.vae).name}. Delete "
                  f"ml/data/proc/{split}_mu.npy and re-run train_mdnrnn.py.")
            return 1

    # **The SPLIT seed comes from the CHECKPOINT, never from --seed.**
    # --seed varies the episode sampling and the MDN-RNN temperature draw; it
    # must NOT re-derive the data split, because the checkpoint was selected
    # against the split its own training run used. Measured before this fix
    # (cold audit, 2026-08-06): `--seed 3` reported 12 of 12 "val_indomain"
    # episodes that were in the seed-0 FIT set -- a held-out metric computed
    # entirely on training data, recorded to json with no warning. P5 needs
    # >=3 seeds for its comparative claim, so this was one flag away from
    # publishing train-on-test numbers.
    split_seed = vae_ckpt.get("args", {}).get("seed", 0)
    fit_eps, val_eps = fit_val_episodes(tr_tracks, seed=split_seed)
    if split_seed != args.seed:
        print(f"note: sampling seed {args.seed}, but the split is rebuilt with "
              f"seed {split_seed} (the checkpoint's) so val_indomain stays "
              f"genuinely held out")
    # The guard train_vae.py:115 has and this file did not.
    assert not (set(fit_eps.tolist()) & set(val_eps.tolist())), \
        "fit/val episodes overlap - the rollout split is not held out"

    print(f"warmup {args.warmup} frames, then {args.horizon} imagined steps "
          f"following the real actions\n")

    results = {}
    results["val_indomain"] = run_split(
        "val_indomain", tr_imgs, tr_mu, tr_act, tr_eps, val_eps,
        vae, rnn, args, out)
    results["holdout"] = run_split(
        "holdout", ho_imgs, ho_mu, ho_act, ho_eps, np.arange(len(ho_eps)),
        vae, rnn, args, out)

    beats = {}
    for tag, r in results.items():
        mse = r["image_mse_by_step"]
        base = r["frozen_baseline_mse_by_step"]
        lat = r["latent_l2_by_step"]
        print(f"{tag}  ({r['episodes']} episodes)")
        print(f"  step        {'1':>8} {'5':>8} {'10':>8} "
              f"{f'{len(mse)//2}':>8} {f'{len(mse)}':>8}")
        pick = [0, 4, 9, len(mse) // 2 - 1, len(mse) - 1]
        print(f"  latent L2   " + "".join(f"{lat[i]:8.2f}" for i in pick))
        print(f"  image MSE   " + "".join(f"{mse[i]:8.4f}" for i in pick))
        print(f"  frozen base " + "".join(f"{base[i]:8.4f}" for i in pick))
        better = sum(m < b for m, b in zip(mse, base))
        beats[tag] = (better, len(mse))
        print(f"  beats the frozen-frame baseline on {better}/{len(mse)} steps\n")

    (out / "rollout_metrics.json").write_text(json.dumps(
        {"args": vars(args), "results": results}, indent=2))
    print(f"panels : {out}/rollout_{{val_indomain,holdout}}.png")
    print(f"metrics: {out / 'rollout_metrics.json'}")

    # **The done-check has to be able to FAIL.** Before this, `better` was
    # printed and discarded and main() returned None, so 0/30 exited 0 exactly
    # like 30/30 -- while testing.md listed this file in a table of gates that
    # "exit non-zero on failure". A gate that cannot fire is not a gate.
    # (Cold audit finding 3, 2026-08-06.)
    #
    # Gated on val_indomain ONLY. Holdout is an unseen visual domain and is
    # EXPECTED to lose to the baseline (measured 0/30, record Appendix S) --
    # gating on it would fail a correct model.
    #
    # 0.9, not 1.0: the published result is 30/30, so the threshold sits three
    # steps below the observed value. A gate pinned to a perfect score turns
    # ordinary seed variance into a red build, which is how gates get disabled.
    won, total = beats["val_indomain"]
    need = int(MIN_BEAT_FRACTION * total)
    print(f"\nP3 DONE-CHECK: val_indomain beat the baseline on {won}/{total} "
          f"steps (need >= {need})")
    if won < need:
        print("P3 DONE-CHECK: FAIL")
        return 1
    print("P3 DONE-CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
