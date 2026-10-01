# Autonomous Car Project — project rules

Mini autonomous car: Lego Technic (differential, steering geometry, wheels) +
3D-printed FDM frame; camera-first sensing; staged AI (teleop → behavioral
cloning → sim RL → world model stretch). Fresh session: read `HANDOFF.md`
FIRST, then `PRD_ROADMAP.md`.

## Doc cadence (project-memory system, defaults set 2026-07-23)
- **Record entry** (`docs/Project Record — Full Chronological History.md`):
  every 3 prompts of real work. Append-only, `# Appendix <X>` headings +
  TOC line. No HTML twin (none exists — don't create one).
- **Handoff** (`HANDOFF.md`): session end.
- **PRD next-task**: on request ("next task", "go").
- **Project-memory bins** (`.claude/project-memory/`): same session as any
  change that alters a stored fact.

## Hard rules
- No hardware purchase without Evan's explicit go — purchase tasks are
  BLOCKED-ON-EVAN, worked against specs/stubs until he acts.
- Physical-world claims stay honest: a print that hasn't been test-fitted is
  "untested", a policy that hasn't driven the real car is "sim-only". Never
  claim real-world verification that didn't happen.
- CAD/STL/print artifacts: record printer settings + filament + measured fit
  results in the record when a test print happens (the experiment trail is
  portfolio material).
- Definition of done for code tasks: task's own done-check passes + real
  output pasted + record entry exists (global standard applies).

Never include "Co-Authored-By: Claude Opus 5.5 (or any other model) <noreply@anthropic.com>" in any commits or pushes

Long tasks on Opus 5.5 follow the plan-split rule in the workspace-root CLAUDE.md (Opus plans and reasons; up to 3 Sonnet 5.5 agents run the code part; not for scheduled runs).
