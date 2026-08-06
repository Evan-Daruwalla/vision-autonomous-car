# codebase-memory index — Autonomous Car Project

Core bins:
- security.md — empty, no attack surface yet; live at M2 teleop (updated 2026-07-23)
- performance.md — empty, no perf work yet; live at M3 inference loop (updated 2026-07-23)
- architecture.md — planned system shape + staged AI pipeline (updated 2026-07-23)
- features.md — empty, no code yet (updated 2026-07-23)
- conventions.md — empty, no code yet (updated 2026-07-23)
- gotchas.md — hardware/print/power/track traps (updated 2026-08-06)
- ml-training.md — GPU memory + world-model training facts MEASURED on this
  3060 Ti: the DreamerV3 fitting table, Sysmem Fallback confirmed ON,
  dreamerv3-torch's missing offline loop (updated 2026-08-06)

Standards bins (only those the codebase actually commits to):
- dependencies.md — planned stack (DonkeyCar 5.x plumbing + PyTorch models) (updated 2026-07-23)
- ui.md — N/A, no frontend planned; teleop UI TBD at M2 (updated 2026-07-23)
- testing.md — the runnable done-checks + verification rules (updated 2026-08-06)
- data.md — THE episode data contract: npz schema, t=0 rule, both alignment gates, 3-way split rule (updated 2026-08-06)
- tooling.md — Python 3.12.10 venv, machine facts, git -F quirk (updated 2026-08-06)

Cross-bin invariants:
- No hardware purchase without Evan's explicit go (BLOCKED-ON-EVAN).
- Absolute dates in every entry; nothing invented; desk research is tagged
  as untested until a build task verifies it on the real car.
- NEVER rewrite a UTF-8 file with PowerShell `Set-Content`/`-replace` — it
  mangles em-dashes to mojibake. Use the Edit/Write tools. (Hit 2026-08-06 on
  this very file; the global CLAUDE.md warns about it for JSON, and it
  applies to markdown just as hard.)
