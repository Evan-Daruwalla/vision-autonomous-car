# important - Autonomous Car Project

> Critical facts: getting one wrong is irreversible or expensive, invalidates
> results, or breaks a live external constraint. Numbered, dated, newest last.
> CLAUDE.md wins on conflict. Never remove an entry without telling Evan.
> Keep entries short; detail lives in the topic bin. ASCII only.
> Created 2026-09-30 from CLAUDE.md, HANDOFF.md, PRD_ROADMAP.md and the bins (Skills record EA follow-up).

## 1. No hardware purchase without Evan's explicit go (2026-09-30)
**What:** the BOM (`docs/BOM.md`) stands at $411.45 + shipping (~$424-439), UNBOUGHT, BLOCKED-ON-EVAN. Purchase tasks are worked against specs and stubs until he acts.
**Constrains:** never place, start or "prepare to submit" an order; re-verify prices before he buys.
**Why:** money, and the BOM has been re-priced four times.
**Source:** CLAUDE.md:18-19; HANDOFF.md:39, :191, :495; detail in budget.md / hardware.md.

## 2. Physical-world claims stay honest (2026-09-30)
**What:** an unprinted or untested part is "untested"; a sim-only result is "sim-only". On any test print, record printer settings, filament and measured fit in the record.
**Constrains:** every result, README line and portfolio claim.
**Why:** the experiment trail is the portfolio; an overclaim is a credibility failure.
**Source:** CLAUDE.md:20-25.

## 3. The flashed Uno build and the repo source DIVERGE (2026-09-30)
**What:** the board runs the 2026-09-02 build (SELFTEST 49/49, 7888 B); newer source (incl. the WS2812B path) was never flashed. Actuators are unwired.
**Constrains:** read the boot banner before trusting any firmware claim; never assume the repo is what runs.
**Why:** a test against the wrong build verifies nothing.
**Source:** HANDOFF.md:27-34; detail in firmware-traps.md.

## 4. Battery safety: a charger is not a BMS (2026-09-30)
**What:** a 2S 18650 pack needs a board that DOCUMENTS over-discharge cutoff, or protected cells; BOM row 11's "BMS" documents over-voltage and short-circuit only. Firmware cannot guard a pack while it is off.
**Constrains:** no pack is specified or bought without a documented over-discharge cutoff.
**Why:** an over-discharged lithium pack is a fire and safety risk.
**Source:** HANDOFF.md:474-483; hardware.md (power section).

## 5. Steering coupler: the printed one FAILS (2026-09-30)
**What:** the highest-torque joint; MG90S stall ~216 mN-m gives SF 0.57-0.96 for the printed coupler. Grip a real Lego axle; no coupling is chosen yet.
**Constrains:** never ship or claim a printed steering coupler.
**Why:** the joint breaks under stall torque.
**Source:** HANDOFF.md:485-489; detail in steering.md.

## 6. Frozen and closed decisions - do not reopen (2026-09-30)
**What:** corner geometry is FROZEN until the T2 turning test on the rolling chassis. The LaneMaker / OpenDRIVE thread is CLOSED as a negative - DO NOT RE-OPEN.
**Constrains:** no geometry changes and no LaneMaker work without Evan reopening it.
**Why:** both were settled with evidence; reopening burns sittings.
**Source:** HANDOFF.md:148, :317; detail in decisions.md (when migrated).

## 7. ML evaluation discipline (2026-09-30)
**What:** never compare closed-loop sim numbers across launches (`donkey-generated-track-v0` regenerates the track) - use `ml/eval_paired.py`; never select controllers on open-loop MSE; never split episodes randomly by frame (three splits; seed from the checkpoint); every result JSON goes through `provenance.write_result`.
**Constrains:** every ML result reported.
**Why:** each of these produced a wrong conclusion before.
**Source:** HANDOFF.md:61-75; data.md:83-106; conventions.md:29-39.

## 8. Deadlines (2026-09-30)
**What:** the hard deadline is Regular Decision, ~2027-01-01..15; 2026-11-01 is a SOFT milestone that still targets SIM-POC + M3. Anything that threatens M3-by-mid-October is escalated to Evan, not absorbed.
**Constrains:** scope choices this month.
**Why:** the car is a college-application piece.
**Source:** PRD_ROADMAP.md:1323-1329; detail in timeline.md (when migrated).

## 9. Public repo; git hygiene (2026-09-30)
**What:** the repo is public (github.com/Evan-Daruwalla/vision-autonomous-car). Never `git add -A` / `git add .` (hard-denied); list files explicitly; never push unprompted; no Co-Authored-By.
**Constrains:** every commit.
**Why:** public history is permanent; 2 occurrences of a home path remain in committed record history (a rewrite is Evan's call).
**Source:** HANDOFF.md:569-573, :586-587, :598-599.
