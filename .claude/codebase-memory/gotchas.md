# gotchas.md — SPLIT 2026-09-02. This file is now a router.

It reached **423 lines, 2.8x the ~150 cap**, and had become four unrelated
subjects in one file. Split into the bins below (Appendix BO). **No fact was
lost** — the split was done mechanically with a no-loss invariant (68 entry
blocks parsed, 68 placed), and the one entry that was NOT carried over is
named at the bottom.

**This file is kept rather than deleted** because `CLAUDE.md`, `HANDOFF.md` and
several record appendices reference `gotchas.md` by name. Follow the pointer.

| looking for | read |
|---|---|
| printing, Lego fit, power, motors, drivers, the Uno, vehicle geometry | **`hardware.md`** |
| track layout, markings, surface, what the camera sees of the environment | **`track.md`** |
| the simulator, the eval harness, training-time GPU limits | **`sim-harness.md`** |
| shell, encoding and build-tool traps | **`tooling.md`** |

**One entry was deliberately not carried over:** *"NEVER split a driving dataset
randomly by frame"*. It duplicated `data.md`'s **"Splitting rule — THREE splits,
not two"**, which covers the same rule with the measured evidence behind it
(fit 56.11 vs val 56.72). Keeping both is exactly the scattering the bins
exist to prevent. **The rule itself is unchanged and still enforced** — it lives
in `data.md`.
