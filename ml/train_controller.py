"""SIM-POC P5 step 1: train the controller (C) by latent behavioural cloning.

The third component of Ha & Schmidhuber's V-M-C. V (ConvVAE) compresses a
frame to z; M (MDN-RNN) carries history in its LSTM state h; C maps [z_t, h_t]
to an action. The paper's C is a single linear layer: all representational
work is supposed to live in V and M, and a linear C is what demonstrates it.

**That premise failed here, and the failure is measured (2026-08-07).** A
linear probe recovers R^2 = 0.27 of cross-track error from z; an MLP probe
recovers 0.97. The latent carries lane position, but NONLINEARLY -- so a
linear C cannot compute the one quantity lane-following depends on. `--arch
mlp` is the controlled test of that diagnosis; `--arch linear` remains the
default so the paper-faithful result stays reproducible.

**Why [z, h] and not just z.** A policy on z alone is memoryless: it can only
see the current frame. Feeding it h is what makes P5 exercise the world model
this project spent P3 building rather than just the encoder. It is also the
mechanism that would eventually let a stop sign work (record Appendix L: a
memoryless policy provably cannot represent "I already stopped here").

**The paper trains C with CMA-ES on cumulative reward. This trains it by
behavioural cloning on the expert's actions**, per the PRD's "latent BC"
wording. That is a deliberate scope choice, not an oversight: evolution
strategies need thousands of live rollouts through the simulator, and SIM-POC
is a proof of the offline pipeline. Consequence to state plainly: this policy
can at best match the PID expert, never beat it. It is imitating, not
optimising.

THE CAUSAL INDEXING, stated because this project has caught this bug before:
`h_t` must be the LSTM state BEFORE the RNN consumes (z_t, a_t). nn.LSTM's
`out[t]` is the state AFTER consuming input t, so out[t] already depends on
a_t -- the action the controller is being asked to predict. Using it directly
would leak the label and produce a policy that looks excellent offline and
cannot drive. h is therefore shifted by one: h_0 = 0, h_t = out[t-1].

Usage:
  python ml/train_controller.py                 # 30 epochs
  python ml/train_controller.py --seed 1        # a different init
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from models import ACTION_DIM, HIDDEN, MDNRNN, Z_DIM, ConvVAE, count_params
from splits import fit_val_episodes, load_cached_mu, load_proc

REPO = Path(__file__).resolve().parent.parent
PROC = REPO / "ml" / "data" / "proc"
RUNS = REPO / "ml" / "runs"


class Controller(nn.Module):
    """Policy on [z, h]. `linear` is the paper's C; `mlp` is one hidden layer.

    **Why `mlp` exists, measured 2026-08-07.** A linear probe recovers only
    R^2 = 0.27 of cross-track error from z, while an MLP probe recovers 0.97
    -- so the latent DOES carry lane position, encoded nonlinearly. A linear
    policy therefore cannot compute "how far off centre am I" from z at all;
    it can only fit a local approximation near the centre and degrade as it
    drifts. That matches the measured failure exactly: the linear controller
    steers LESS than the expert (6.57 vs 7.67 reversals/100) yet sits 2.9x
    further off centre, i.e. it drifts out without recovering rather than
    oscillating. `mlp` is the smallest change that tests this diagnosis.
    """

    def __init__(self, z_dim: int = Z_DIM, hidden: int = HIDDEN,
                 action_dim: int = ACTION_DIM, arch: str = "linear",
                 width: int = 256):
        super().__init__()
        self.arch = arch
        d = z_dim + hidden
        if arch == "linear":
            self.net = nn.Linear(d, action_dim)
        elif arch == "mlp":
            self.net = nn.Sequential(
                nn.Linear(d, width), nn.ReLU(inplace=True),
                nn.Linear(width, action_dim))
        else:
            raise ValueError(f"unknown arch {arch!r}")

    def forward(self, z: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
        # tanh bounds steering to [-1, 1], which is the simulator's own range;
        # an unbounded head learns to emit values the env silently clips, and
        # the clipping hides the error from the loss.
        return torch.tanh(self.net(torch.cat([z, h], dim=-1)))


@torch.no_grad()
def rnn_states(rnn: MDNRNN, mu: np.ndarray, act: np.ndarray,
               episodes: np.ndarray, ep_idx: np.ndarray, device: str):
    """h_t for every frame of the given episodes, causally shifted.

    Returns (flat_indices, h) so callers can index the shared mu/act arrays.
    """
    idx_all, h_all = [], []
    for i in ep_idx:
        s, n = episodes[i]
        z = torch.from_numpy(mu[s:s + n]).to(device).unsqueeze(0)
        a = torch.from_numpy(act[s:s + n]).to(device).unsqueeze(0)
        # Only the LSTM output is needed -- the mixture head predicts z_{t+1}
        # and is irrelevant to the controller, so it is not run.
        out, _ = rnn.lstm(torch.cat([z, a], dim=-1))     # (1, n, HIDDEN)
        out = out.squeeze(0)
        # h_t = state BEFORE consuming (z_t, a_t). See the module docstring.
        h = torch.cat([torch.zeros(1, out.shape[1], device=device), out[:-1]], 0)
        idx_all.append(np.arange(s, s + n))
        h_all.append(h.cpu().numpy())
    return np.concatenate(idx_all), np.concatenate(h_all)


def evaluate(model, z, h, a, device, batch=4096, w=None):
    """Mean per-frame MSE. `w` gives a weighted mean over the same frames.

    Both are reported: the WEIGHTED one is what checkpoint selection uses when
    `--recovery-weight` is set, because selecting on the unweighted metric
    would quietly pull the chosen epoch back toward the centred-frame optimum
    the weighting exists to escape. The UNWEIGHTED one is the only number
    comparable across different weights.
    """
    model.eval()
    tot, n = 0.0, 0.0
    with torch.no_grad():
        for s in range(0, len(z), batch):
            e = min(s + batch, len(z))
            zb = torch.from_numpy(z[s:e]).to(device)
            hb = torch.from_numpy(h[s:e]).to(device)
            ab = torch.from_numpy(a[s:e]).to(device)
            err = ((model(zb, hb) - ab) ** 2).mean(dim=-1)
            if w is None:
                tot += float(err.sum())
                n += e - s
            else:
                wb = torch.from_numpy(w[s:e]).to(device)
                tot += float((err * wb).sum())
                n += float(wb.sum())
    model.train()
    return tot / n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--vae", default=str(RUNS / "vae" / "vae_best.pt"))
    ap.add_argument("--rnn", default=str(RUNS / "mdnrnn" / "mdnrnn_best.pt"))
    ap.add_argument("--arch", choices=("linear", "mlp"), default="linear")
    ap.add_argument("--proc", default=str(PROC),
                    help="processed corpus to train on. Point at "
                         "ml/data/proc_aug to include the off-centre recovery "
                         "episodes; V and M stay frozen on the original.")
    ap.add_argument("--no-history", action="store_true",
                    help="zero the MDN-RNN hidden state, training C on z "
                         "alone. Tests whether the controller's near-total "
                         "dependence on h is what kills it in closed loop: h "
                         "is teacher-forced on LOGGED expert actions during "
                         "training but built from the POLICY's own actions at "
                         "serve time, so it drifts. eval_in_sim.py reads this "
                         "flag back out of the checkpoint and zeroes h to "
                         "match (see diag_copycat.py)")
    ap.add_argument("--recovery-weight", type=float, default=1.0,
                    help="loss weight on frames from '-rec' (off-centre "
                         "recovery) episodes. 1.0 = unweighted, the Appendix "
                         "Z.3 arm that did NOT improve driving. Requires a "
                         "--proc containing recovery episodes")
    ap.add_argument("--out", default=str(RUNS / "controller"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    rng = np.random.default_rng(args.seed)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    vae_ckpt = torch.load(args.vae, map_location=args.device)
    vae = ConvVAE().to(args.device)
    vae.load_state_dict(vae_ckpt["model"])
    rnn = MDNRNN().to(args.device)
    rnn.load_state_dict(torch.load(args.rnn, map_location=args.device)["model"])
    vae.eval(); rnn.eval()

    proc = Path(args.proc)
    _, act, eps, tracks = load_proc("train", proc=proc)

    # **Expert labels, not executed actions, when the corpus has recovery
    # episodes.** collect_recovery.py records the action actually executed
    # (including injected noise) to keep the data contract; cloning that
    # teaches the car to swerve. build_expert_labels.py writes what the expert
    # would have done at each visited state -- the DART target.
    expert_path = proc / "train_actions_expert.npy"
    if expert_path.exists():
        act = np.load(expert_path)
        print(f"labels: {expert_path.name} (expert actions)")

    mu_path = proc / "train_mu.npy"
    # Cold audit finding 1: check the cache's encoder fingerprint before
    # reusing it, same as train_mdnrnn.py does when it writes the cache.
    mu = load_cached_mu("train", args.vae, proc=proc)
    if mu is None:
        # Missing (alternate corpus) or stale (different VAE than loaded
        # above) cache. Encode with the SAME frozen VAE loaded above rather
        # than writing a cache here: the cache carries an encoder fingerprint
        # (cold audit finding 5) and only train_mdnrnn.py is set up to stamp
        # one.
        print(f"no usable latent cache at {mu_path.name} - encoding with the frozen VAE...")
        imgs, _, _, _ = load_proc("train", proc=proc)
        mu = np.zeros((len(imgs), Z_DIM), np.float32)
        with torch.no_grad():
            for s in range(0, len(imgs), 512):
                e = min(s + 512, len(imgs))
                x = torch.from_numpy(np.array(imgs[s:e])).to(args.device)
                mu[s:e] = vae.encode(
                    x.permute(0, 3, 1, 2).float().div_(255.0))[0].cpu().numpy()
        del imgs
    assert len(mu) == len(act), f"{len(mu)} latents vs {len(act)} actions"

    # Same rule as rollout_eval.py: the SPLIT seed comes from the checkpoint,
    # never from --seed. --seed varies this controller's init and batch order
    # so P5 can report >=3 seeds, and must not move the data split underneath.
    split_seed = vae_ckpt.get("args", {}).get("seed", 0)
    fit_eps, val_eps = fit_val_episodes(tracks, seed=split_seed)
    assert not (set(fit_eps.tolist()) & set(val_eps.tolist())), "fit/val overlap"

    print(f"building RNN states for {len(fit_eps)} fit + {len(val_eps)} val episodes...")
    t0 = time.time()
    fit_i, fit_h = rnn_states(rnn, mu, act, eps, fit_eps, args.device)
    val_i, val_h = rnn_states(rnn, mu, act, eps, val_eps, args.device)
    print(f"  fit {len(fit_i):,} frames, val {len(val_i):,} frames "
          f"({time.time()-t0:.0f}s)")

    fit_z, fit_a = mu[fit_i], act[fit_i]
    val_z, val_a = mu[val_i], act[val_i]

    if args.no_history:
        # Zeroed rather than removed so the Controller architecture, parameter
        # count and checkpoint format stay identical to every banked arm --
        # the only thing that changes is the information available.
        fit_h = np.zeros_like(fit_h)
        val_h = np.zeros_like(val_h)
        print("--no-history: MDN-RNN hidden state ZEROED, C sees z only")

    # **Recovery-frame sample weight.** Appendix Z.3: adding 6.67% off-centre
    # recovery data left the controller's val MSE essentially unchanged
    # (0.001754 -> 0.001788) and did not make the car drive further, because
    # the objective is a mean over frames and 93% of them are centred -- the
    # minimiser is nearly the same policy. Weighting recovery frames by W
    # moves their share of the gradient from 6.67% to 6.67W/(93.33+6.67W).
    # Directly analogous to the aux-head weight sweep in Z.1, where weight 10
    # (~4% of loss) bought nothing and 100 saturated.
    is_rec_ep = np.array([t.endswith("-rec") for t in tracks])
    is_rec_frame = np.zeros(len(mu), bool)
    for e_i in np.flatnonzero(is_rec_ep):
        s0, n0 = eps[e_i]
        is_rec_frame[s0:s0 + n0] = True
    fit_w = np.where(is_rec_frame[fit_i], args.recovery_weight, 1.0).astype(np.float32)
    val_w = np.where(is_rec_frame[val_i], args.recovery_weight, 1.0).astype(np.float32)
    n_rec_fit = int(is_rec_frame[fit_i].sum())
    share = (args.recovery_weight * n_rec_fit
             / (args.recovery_weight * n_rec_fit + (len(fit_i) - n_rec_fit)))
    if n_rec_fit:
        print(f"recovery frames: {n_rec_fit:,}/{len(fit_i):,} "
              f"({100*n_rec_fit/len(fit_i):.2f}%), weight {args.recovery_weight:g} "
              f"-> {100*share:.1f}% of the objective")
    elif args.recovery_weight != 1.0:
        raise SystemExit(f"--recovery-weight {args.recovery_weight:g} given but "
                         f"this corpus has NO '-rec' episodes. Point --proc at "
                         f"ml/data/proc_aug, or the flag silently does nothing.")

    model = Controller(arch=args.arch).to(args.device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    print(f"controller: {count_params(model):,} params "
          f"(linear on z{Z_DIM} + h{HIDDEN})\n")

    history, best = [], float("inf")
    steps = max(1, len(fit_z) // args.batch)
    for epoch in range(1, args.epochs + 1):
        t0, run = time.time(), 0.0
        for _ in range(steps):
            sel = rng.choice(len(fit_z), size=args.batch, replace=False)
            zb = torch.from_numpy(fit_z[sel]).to(args.device)
            hb = torch.from_numpy(fit_h[sel]).to(args.device)
            ab = torch.from_numpy(fit_a[sel]).to(args.device)
            wb = torch.from_numpy(fit_w[sel]).to(args.device)
            err = ((model(zb, hb) - ab) ** 2).mean(dim=-1)
            # weighted MEAN, not sum: keeps the loss scale (and so the
            # effective learning rate) comparable across weights
            loss = (err * wb).sum() / wb.sum()
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            run += float(loss)
        tr = run / steps
        # selection on the weighted metric (matches the objective); the
        # unweighted one is the only cross-weight-comparable number
        va = evaluate(model, val_z, val_h, val_a, args.device, w=val_w)
        va_plain = evaluate(model, val_z, val_h, val_a, args.device)
        history.append({"epoch": epoch, "fit_mse": tr, "val_mse": va,
                        "val_mse_unweighted": va_plain,
                        "seconds": round(time.time() - t0, 1)})
        if epoch % 5 == 0 or epoch == 1:
            print(f"  epoch {epoch:3d}  fit {tr:.5f}  val_indomain {va:.5f} "
                  f"(unweighted {va_plain:.5f})")
        if va < best:
            best = va
            torch.save({"model": model.state_dict(), "epoch": epoch,
                        "val_mse": va, "val_mse_unweighted": va_plain,
                        "args": vars(args)},
                       out / f"controller_{args.arch}_seed{args.seed}.pt")

    (out / f"history_{args.arch}_seed{args.seed}.json").write_text(
        json.dumps({"args": vars(args), "history": history}, indent=2))
    print(f"\nbest val_indomain MSE {best:.5f} -> "
          f"{out / f'controller_{args.arch}_seed{args.seed}.pt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
