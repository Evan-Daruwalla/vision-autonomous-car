# codebase-memory index — Autonomous Car Project

Core bins:
- security.md — empty, no attack surface yet; live at M2 teleop (updated 2026-07-23)
- performance.md — empty, no perf work yet; live at M3 inference loop (updated 2026-07-23)
- architecture.md — planned system shape + staged AI pipeline (updated 2026-07-23)
- features.md — inventory of the 31 ml/ scripts by pipeline stage (updated 2026-08-25)
- conventions.md — general code style observed across ml/ (argparse, seeding, no logging) (updated 2026-08-25)
- gotchas.md — **SPLIT 2026-09-02, now a 24-line ROUTER only.** Kept because CLAUDE.md/HANDOFF reference it by name; follow its pointers
- hardware.md — printing + Lego fit, power, motors/drivers, the Uno, Arduino build traps, measured vehicle geometry (new 2026-09-02; 328 lines, over the ~150 cap but one coherent domain)
- track.md — track layout, markings, surface, what the camera sees of the environment (new 2026-09-02; 54 lines)
- sim-harness.md — the simulator, the eval harness, training-time GPU limits (new 2026-09-02; 131 lines)
- ml-training.md — GPU memory + world-model training facts MEASURED on this
  3060 Ti: the DreamerV3 fitting table, Sysmem Fallback confirmed ON,
  dreamerv3-torch's missing offline loop (updated 2026-08-06)

Standards bins (only those the codebase actually commits to):
- dependencies.md — planned stack (DonkeyCar 5.x plumbing + PyTorch models) (updated 2026-07-23)
- ui.md — N/A, no frontend planned; teleop UI TBD at M2 (re-checked 2026-09-02, still N/A)
- testing.md — the runnable done-checks + verification rules, ml AND firmware (updated 2026-09-02)
- data.md — THE episode data contract: npz schema, t=0 rule, both alignment gates, 3-way split rule, + the Pi/Uno serial frame contract, DESIGN ONLY (updated 2026-09-02; 158 lines, at the cap)
- tooling.md — Python 3.12.10 venv, machine facts, git -F quirk, shell/encoding traps from the gotchas split (updated 2026-09-02)

Cross-bin invariants:
- No hardware purchase without Evan's explicit go (BLOCKED-ON-EVAN).
- Absolute dates in every entry; nothing invented; desk research is tagged
  as untested until a build task verifies it on the real car.
- NEVER rewrite a UTF-8 file with PowerShell `Set-Content`/`-replace` — it
  mangles em-dashes to mojibake. Use the Edit/Write tools. (Hit 2026-08-06 on
  this very file; the global CLAUDE.md warns about it for JSON, and it
  applies to markdown just as hard.)
