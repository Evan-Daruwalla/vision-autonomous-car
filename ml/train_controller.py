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
  python ml/train_controller.py --self-check    # invariants only, CPU, no data
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
from provenance import write_result
from splits import (encoder_fingerprint, fit_val_episodes, load_cached_mu,
                    load_proc, split_seed_of)

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


def select_actions(executed: np.ndarray, expert: np.ndarray | None):
    """Return (lstm_input, bc_target). THE DART INVARIANT, as one function.

    The LSTM input is ALWAYS the executed sequence -- it is what produced the
    observed latents, and the frozen MDN-RNN was only ever trained on executed
    actions. Only the BC target takes the expert relabel. Extracted from main()
    2026-09-10 so self_check() can pin it: the 2026-09-07 defect (Appendix EJ)
    lived in main()'s choice of array, and main() cannot run without the corpus.
    """
    if expert is None:
        return executed, executed
    assert len(expert) == len(executed), (
        f"{len(expert)} expert labels vs {len(executed)} executed actions")
    return executed, expert


def build_training_arrays(rnn, mu, act, expert, eps, fit_eps, val_eps, device):
    """main()'s whole DART data-prep path: (i, z, h, a) for fit and for val.

    Moved out of main() 2026-10-10 (daily audit, Appendix FD #2). With only
    select_actions() under test, putting the 2026-09-07 bug back INSIDE main()
    -- handing the expert array to rnn_states() -- still passed self_check.
    main() now does nothing on this path but call this function, and
    self_check() runs it end to end.
    """
    lstm_in, target = select_actions(act, expert)
    out = []
    for ep_idx in (fit_eps, val_eps):
        idx, h = rnn_states(rnn, mu, lstm_in, eps, ep_idx, device)
        out.append((idx, mu[idx], h, target[idx]))
    return out[0], out[1]


def check_labels(tracks, expert, allow_noisy: bool) -> None:
    """Refuse to clone noise-injected actions by accident (Appendix FD #7).

    Recovery episodes (track names ending '-rec', the same rule main() uses
    for --recovery-weight) record the action actually EXECUTED, injected
    noise included. Without train_actions_expert.npy the BC target falls back
    to those actions, and the car learns to swerve. That used to happen
    silently; now it needs an explicit flag.
    """
    n_rec = sum(str(t).endswith("-rec") for t in tracks)
    if n_rec and expert is None and not allow_noisy:
        raise SystemExit(
            f"{n_rec} recovery episode(s) but no train_actions_expert.npy: the "
            f"BC target would be the noise-injected executed actions. Run "
            f"ml/build_expert_labels.py, or pass --allow-noisy-labels to train "
            f"on them deliberately.")


def self_check() -> None:
    """Pins the DART invariant, proves it is not vacuous, and pins causality.

    CPU only, a randomly initialised MDN-RNN, no corpus or checkpoint -- so it
    runs on a bare clone. fork_rng keeps it from reseeding the global RNG,
    because scripts/run_checks.py runs every self-check in one process.
    """
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(0)
        rng = np.random.default_rng(0)
        executed = rng.standard_normal((11, ACTION_DIM)).astype(np.float32)
        expert = executed.copy()
        expert[3:6] += 0.8          # "recovery frames": where the arrays differ

        # 1. The invariant, at the function that decides it. Check 5 below
        #    runs main()'s whole data-prep path, so the pre-bfa953e bug (the
        #    expert array into the LSTM) cannot hide in main() either --
        #    before 2026-10-10 it could (Appendix FD #2).
        lstm_in, target = select_actions(executed, expert)
        assert lstm_in is executed, (
            "rnn_states() must replay the EXECUTED actions, never the expert "
            "relabel -- the 2026-09-07 DART contamination (Appendix EJ)")
        assert target is expert, "the BC target must be the expert relabel"
        lstm_in, target = select_actions(executed, None)
        assert lstm_in is executed and target is executed
        refused = False
        try:
            select_actions(executed, expert[:-1])
        except AssertionError:
            refused = True
        assert refused, "a label/action length mismatch must be refused"

        # 2. The invariant is not vacuous: which array goes in changes h.
        #    Two episodes: frames 0-5 (actions 3-5 differ) and 6-10 (identical).
        rnn = MDNRNN().eval()
        mu = rng.standard_normal((11, Z_DIM)).astype(np.float32)
        eps = np.array([[0, 6], [6, 5]])
        ep_idx = np.array([0, 1])
        idx, h_exec = rnn_states(rnn, mu, executed, eps, ep_idx, "cpu")
        _, h_exp = rnn_states(rnn, mu, expert, eps, ep_idx, "cpu")
        assert idx.tolist() == list(range(11)), idx
        assert h_exec.shape == (11, HIDDEN), h_exec.shape
        assert not np.allclose(h_exec[4], h_exp[4]), (
            "feeding expert vs executed actions left h unchanged -- then the "
            "DART invariant above would be guarding nothing")

        # 3. Causality (THE CAUSAL INDEXING in the module docstring): h_t is
        #    the state BEFORE consuming (z_t, a_t). Frame 3's own action
        #    differs between the two runs, so h_3 matching proves h_t does not
        #    see a_t -- the label leak that makes a policy look perfect offline
        #    and unable to drive.
        assert np.allclose(h_exec[:4], h_exp[:4]), (
            "h_t depends on a_t: the one-step causal shift is broken and the "
            "label leaks into the controller's input")
        assert np.all(h_exec[0] == 0) and np.all(h_exec[6] == 0), (
            "h must start at zero in every episode")
        assert np.allclose(h_exec[6:], h_exp[6:]), (
            "state leaked across an episode boundary")

        # 4. The controller's output is bounded to the simulator's range.
        for arch in ("linear", "mlp"):
            out = Controller(arch=arch)(torch.randn(5, Z_DIM) * 50,
                                        torch.randn(5, HIDDEN) * 50)
            assert out.shape == (5, ACTION_DIM), out.shape
            assert out.abs().max() <= 1.0, f"{arch} escaped tanh's [-1, 1]"
        refused = False
        try:
            Controller(arch="transformer")
        except ValueError:
            refused = True
        assert refused, "an unknown arch must be refused"

        # 5. main()'s data-prep path end to end. fit = episode 0 (frames 0-5,
        #    where the arrays differ at 3-5); val = episode 1 (identical).
        (fit_i, fit_z, fit_h, fit_a), (val_i, _, val_h, val_a) = build_training_arrays(
            rnn, mu, executed, expert, eps, np.array([0]), np.array([1]), "cpu")
        assert fit_i.tolist() == list(range(6)) and val_i.tolist() == list(range(6, 11))
        assert np.array_equal(fit_a, expert[fit_i]), "BC target must be the expert relabel"
        assert np.array_equal(fit_z, mu[fit_i])
        assert np.allclose(fit_h, h_exec[fit_i]) and np.allclose(val_h, h_exec[val_i]), (
            "the LSTM was fed something other than the EXECUTED actions -- the "
            "2026-09-07 DART contamination, now inside main()'s path")
        assert not np.allclose(fit_h[4], h_exp[4])

        # 6. Noisy-label guard (Appendix FD #7).
        recov = ["generated-track", "generated-track-rec"]
        refused = False
        try:
            check_labels(recov, None, allow_noisy=False)
        except SystemExit:
            refused = True
        assert refused, "recovery episodes with no expert labels must be refused"
        check_labels(recov, None, allow_noisy=True)      # deliberate: allowed
        check_labels(recov, expert, allow_noisy=False)   # labelled: fine
        check_labels(["generated-track"], None, allow_noisy=False)  # no recovery: fine
    print("train_controller self_check: PASS")


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
    ap.add_argument("--allow-noisy-labels", action="store_true",
                    help="train on recovery episodes WITHOUT expert labels, i.e. "
                         "clone the noise-injected executed actions on purpose")
    ap.add_argument("--self-check", action="store_true",
                    help="run the DART/causality invariants on CPU and exit; "
                         "needs no corpus or checkpoint")
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0

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

    # **Expert labels, not executed actions, for the BC loss TARGET when the
    # corpus has recovery episodes.** collect_recovery.py records the action
    # actually executed (including injected noise) to keep the data contract;
    # cloning that teaches the car to swerve. build_expert_labels.py writes
    # what the expert would have done at each visited state -- the DART
    # target. `act` itself stays the EXECUTED sequence everywhere else in
    # this file: it is what actually produced the observed latents `mu`, so
    # it is what rnn_states() below must replay into the frozen MDN-RNN's
    # LSTM (see THE CAUSAL INDEXING in the module docstring). Only the BC
    # target gets the DART relabel - build_training_arrays() below decides
    # that, and self_check() runs it. Cold audit finding, Appendix EI
    # (2026-09-07): this used to overwrite `act` itself, so h_t was built from
    # a counterfactual action sequence that never produced the observed z's
    # -- worst exactly on the recovery frames where the two arrays differ.
    expert_path = proc / "train_actions_expert.npy"
    expert = np.load(expert_path) if expert_path.exists() else None
    check_labels(tracks, expert, args.allow_noisy_labels)
    if expert is not None:
        print(f"labels: {expert_path.name} (expert actions; "
              f"LSTM input stays the executed sequence)")

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
    split_seed = split_seed_of(vae_ckpt)
    fit_eps, val_eps = fit_val_episodes(tracks, seed=split_seed)
    assert not (set(fit_eps.tolist()) & set(val_eps.tolist())), "fit/val overlap"

    print(f"building RNN states for {len(fit_eps)} fit + {len(val_eps)} val episodes...")
    t0 = time.time()
    (fit_i, fit_z, fit_h, fit_a), (val_i, val_z, val_h, val_a) = build_training_arrays(
        rnn, mu, act, expert, eps, fit_eps, val_eps, args.device)
    print(f"  fit {len(fit_i):,} frames, val {len(val_i):,} frames "
          f"({time.time()-t0:.0f}s)")

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
                        "args": vars(args),
                        # Appendix FD #7: which frozen V and M this C was
                        # trained against. encoder_fingerprint() is a plain
                        # file-stat hash, so it serves the RNN too. Nothing
                        # CHECKS these yet - eval_in_sim / eval_paired /
                        # plan_cem verifying them is the open follow-up.
                        "vae_fingerprint": encoder_fingerprint(args.vae),
                        "rnn_fingerprint": encoder_fingerprint(args.rnn)},
                       out / f"controller_{args.arch}_seed{args.seed}.pt")

    write_result(out / f"history_{args.arch}_seed{args.seed}.json", {"args": vars(args), "history": history})
    print(f"\nbest val_indomain MSE {best:.5f} -> "
          f"{out / f'controller_{args.arch}_seed{args.seed}.pt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
