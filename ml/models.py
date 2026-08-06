"""SIM-POC P3: the Ha & Schmidhuber world model (arXiv:1803.10122).

Two networks, trained separately:

  V (ConvVAE)  64x64x3 frame -> z in R^32
  M (MDN-RNN)  (z_t, a_t) + LSTM state -> a MIXTURE over z_{t+1}

The MDN part is the point. A plain regressor predicting z_{t+1} converges to
the conditional MEAN, and the mean of "the road bends left" and "the road
bends right" is "the road goes straight" -- a prediction that is never
correct. A mixture density head represents the branches separately instead of
averaging them. This is the same multimodality argument that makes plain
behavioural cloning unable to route (record Appendix O), showing up one level
down in the dynamics.

Architecture follows the paper exactly, including kernel sizes, so the VAE
parameter count reproduces the published **4,348,547**. That equality is
asserted in `self_check()` -- it is a free, precise test that the layers are
wired as specified rather than approximately.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

Z_DIM = 32
ACTION_DIM = 2      # (steer, throttle) -- the paper's CarRacing used 3
HIDDEN = 256
N_MIXTURES = 5


class ConvVAE(nn.Module):
    """64x64x3 -> z in R^32. Paper section A.1."""

    def __init__(self, z_dim: int = Z_DIM):
        super().__init__()
        self.z_dim = z_dim
        # 64 -> 31 -> 14 -> 6 -> 2
        self.enc = nn.Sequential(
            nn.Conv2d(3, 32, 4, stride=2), nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, 4, stride=2), nn.ReLU(inplace=True),
            nn.Conv2d(64, 128, 4, stride=2), nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, 4, stride=2), nn.ReLU(inplace=True),
        )
        self.fc_mu = nn.Linear(1024, z_dim)
        self.fc_logvar = nn.Linear(1024, z_dim)

        self.fc_dec = nn.Linear(z_dim, 1024)
        # 1 -> 5 -> 13 -> 30 -> 64
        self.dec = nn.Sequential(
            nn.ConvTranspose2d(1024, 128, 5, stride=2), nn.ReLU(inplace=True),
            nn.ConvTranspose2d(128, 64, 5, stride=2), nn.ReLU(inplace=True),
            nn.ConvTranspose2d(64, 32, 6, stride=2), nn.ReLU(inplace=True),
            nn.ConvTranspose2d(32, 3, 6, stride=2), nn.Sigmoid(),
        )

    def encode(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.enc(x).flatten(1)
        return self.fc_mu(h), self.fc_logvar(h)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        h = self.fc_dec(z).view(-1, 1024, 1, 1)
        return self.dec(h)

    def reparameterize(self, mu, logvar):
        # sampling during training is what stops the latent collapsing to a
        # lookup table; at eval time callers use mu directly
        std = torch.exp(0.5 * logvar)
        return mu + std * torch.randn_like(std)

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar


def vae_loss(recon, x, mu, logvar, beta: float = 1.0):
    """Summed-over-pixels L2 + KL, averaged over the batch.

    Summed (not mean) reconstruction is deliberate: with a per-pixel mean the
    KL term dwarfs reconstruction at this resolution and the decoder collapses
    to the dataset average image -- a grey blur that looks like a bug but is
    the loss doing exactly what it was told.
    """
    rec = F.mse_loss(recon, x, reduction="none").flatten(1).sum(1).mean()
    kl = (-0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).sum(1)).mean()
    return rec + beta * kl, rec.detach(), kl.detach()


class MDNRNN(nn.Module):
    """(z_t, a_t) -> LSTM -> mixture over z_{t+1}. Paper section A.2."""

    def __init__(self, z_dim: int = Z_DIM, action_dim: int = ACTION_DIM,
                 hidden: int = HIDDEN, n_mix: int = N_MIXTURES):
        super().__init__()
        self.z_dim, self.hidden, self.n_mix = z_dim, hidden, n_mix
        self.lstm = nn.LSTM(z_dim + action_dim, hidden, batch_first=True)
        # per mixture: 1 logit + z_dim means + z_dim log-sigmas
        self.head = nn.Linear(hidden, n_mix * (1 + 2 * z_dim))

    def forward(self, z, a, state=None):
        """z (B,T,Z), a (B,T,A) -> (logpi, mu, logsigma), each (B,T,K,...)."""
        out, state = self.lstm(torch.cat([z, a], dim=-1), state)
        p = self.head(out)
        B, T, _ = p.shape
        K, Zd = self.n_mix, self.z_dim
        logits = p[..., :K]
        mu = p[..., K:K + K * Zd].view(B, T, K, Zd)
        logsigma = p[..., K + K * Zd:].view(B, T, K, Zd)
        # clamp keeps sigma out of the region where exp() overflows or the
        # NLL divides by ~0; both show up as a sudden nan mid-epoch
        logsigma = logsigma.clamp(-7.0, 3.0)
        return F.log_softmax(logits, dim=-1), mu, logsigma, state


_LOG_SQRT_2PI = math.log(math.sqrt(2 * math.pi))


def mdn_loss(logpi, mu, logsigma, target):
    """Negative log-likelihood of `target` (B,T,Z) under the mixture.

    Per-dimension diagonal Gaussians, mixture weights shared across
    dimensions -- the paper's formulation.
    """
    t = target.unsqueeze(2)                       # (B,T,1,Z)
    log_prob = -0.5 * ((t - mu) / logsigma.exp()) ** 2 - logsigma - _LOG_SQRT_2PI
    log_prob = log_prob.sum(-1)                   # (B,T,K) diagonal covariance
    return -torch.logsumexp(logpi + log_prob, dim=-1).mean()


def mdn_sample(logpi, mu, logsigma, temperature: float = 1.0):
    """Sample z_{t+1} from the mixture. temperature<1 sharpens, >1 diversifies."""
    K = logpi.shape[-1]
    if temperature != 1.0:
        logpi = logpi / temperature
        logpi = logpi - torch.logsumexp(logpi, dim=-1, keepdim=True)
    idx = torch.distributions.Categorical(logits=logpi).sample()   # (B,T)
    idx_e = idx.unsqueeze(-1).unsqueeze(-1).expand(*idx.shape, 1, mu.shape[-1])
    m = mu.gather(2, idx_e).squeeze(2)
    s = logsigma.gather(2, idx_e).squeeze(2).exp() * math.sqrt(temperature)
    return m + s * torch.randn_like(s)


def count_params(m: nn.Module) -> int:
    return sum(p.numel() for p in m.parameters())


def self_check() -> None:
    """Runnable check: shapes flow, and the VAE matches the published count."""
    torch.manual_seed(0)
    vae, rnn = ConvVAE(), MDNRNN()

    n_vae = count_params(vae)
    # Ha & Schmidhuber report exactly 4,348,547 for the CarRacing ConvVAE.
    # Reproducing it to the parameter proves every kernel size and channel
    # width matches the paper, which eyeballing the code cannot.
    assert n_vae == 4_348_547, f"VAE has {n_vae:,} params, paper says 4,348,547"

    x = torch.rand(4, 3, 64, 64)
    recon, mu, logvar = vae(x)
    assert recon.shape == x.shape, recon.shape
    loss, rec, kl = vae_loss(recon, x, mu, logvar)
    assert torch.isfinite(loss), "VAE loss is not finite"

    B, T = 3, 7
    z = torch.randn(B, T, Z_DIM)
    a = torch.randn(B, T, ACTION_DIM)
    logpi, m, ls, _ = rnn(z, a)
    assert logpi.shape == (B, T, N_MIXTURES), logpi.shape
    assert m.shape == (B, T, N_MIXTURES, Z_DIM), m.shape
    nll = mdn_loss(logpi, m, ls, torch.randn(B, T, Z_DIM))
    assert torch.isfinite(nll), "MDN loss is not finite"
    s = mdn_sample(logpi, m, ls)
    assert s.shape == (B, T, Z_DIM), s.shape

    # mixture weights must be a distribution
    assert torch.allclose(logpi.exp().sum(-1), torch.ones(B, T), atol=1e-5)

    n_rnn = count_params(rnn)
    print(f"ConvVAE : {n_vae:,} params  (paper: 4,348,547 -- exact match)")
    print(f"MDN-RNN : {n_rnn:,} params  (paper reports 422,368 for CarRacing,")
    print(f"          which used a 3-dim action; this uses 2, so a smaller")
    print(f"          count is expected -- not claimed as a match)")
    print(f"total   : {n_vae + n_rnn:,} params")
    print("self_check: PASS")


if __name__ == "__main__":
    self_check()
