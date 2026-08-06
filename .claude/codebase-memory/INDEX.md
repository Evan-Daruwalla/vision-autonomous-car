# codebase-memory index — Autonomous Car Project

Core bins:
- security.md — empty, no attack surface yet; live at M2 teleop (updated 2026-07-23)
- performance.md — empty, no perf work yet; live at M3 inference loop (updated 2026-07-23)
- architecture.md — planned system shape + staged AI pipeline (updated 2026-07-23)
- features.md — empty, no code yet (updated 2026-07-23)
- conventions.md — empty, no code yet (updated 2026-07-23)
- gotchas.md — hardware/print/power traps from the research brief (updated 2026-07-23)

Standards bins (only those the codebase actually commits to):
- dependencies.md — planned stack (DonkeyCar 5.x plumbing + PyTorch models) (updated 2026-07-23)
- ui.md — N/A, no frontend planned; teleop UI TBD at M2 (updated 2026-07-23)
- testing.md — empty, no code yet (updated 2026-07-23)
- data.md — THE episode data contract: npz schema, t=0 rule, both alignment gates, split rule (updated 2026-08-06)
- tooling.md — Python 3.12.10 venv, machine facts, git -F quirk (updated 2026-08-06)

Cross-bin invariants:
- No hardware purchase without Evan's explicit go (BLOCKED-ON-EVAN).
- Absolute dates in every entry; nothing invented; desk research is tagged
  as untested until a build task verifies it on the real car.
