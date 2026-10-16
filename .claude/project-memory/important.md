# important - Autonomous Car Project

> Critical facts: getting one wrong is irreversible or expensive, invalidates
> results, or breaks a live external constraint. Numbered, dated, newest last.
> CLAUDE.md wins on conflict. Never remove an entry without telling Evan.
> Keep entries short; detail lives in the topic bin. ASCII only.
> Created 2026-09-30 from CLAUDE.md, HANDOFF.md, PRD_ROADMAP.md and the bins (Skills record EA follow-up).

## 1. No hardware purchase without Evan's explicit go (2026-09-30)
**What:** the BOM (`docs/BOM.md`) stands at $422.25 before shipping (2026-10-04 cart review, was $411.45; shipping not re-estimated), ~~UNBOUGHT, BLOCKED-ON-EVAN~~ **ORDERED; 23 of 24 items ARRIVED 2026-10-10 (Appendices FI-FL) - Camera Module 3 Wide not arrived (separate order); motor confirmed #5159.** **2026-10-12: the camera is IN SHIPPING (PiShop; record GX).** **2026-10-15: the camera ARRIVED (record IX) - all 24 items in.** Any NEW purchase still needs his explicit go. The BMS is confirmed: `B08HLQQCQJ` (2026-10-04). Purchase tasks are worked against specs and stubs until he acts.
**Constrains:** never place, start or "prepare to submit" an order; re-verify prices before he buys.
**Why:** money, and the BOM has been re-priced four times.
**Source:** CLAUDE.md:18-19; HANDOFF.md:39, :191, :495; detail in budget.md / hardware.md.

## 2. Physical-world claims stay honest (2026-09-30)
**What:** an unprinted or untested part is "untested"; a sim-only result is "sim-only". On any test print, record printer settings, filament and measured fit in the record.
**Constrains:** every result, README line and portfolio claim.
**Why:** the experiment trail is the portfolio; an overclaim is a credibility failure.
**Source:** CLAUDE.md:20-25.

## 3. The flashed Uno build and the repo source DIVERGE (2026-09-30)
**What:** ~~the board runs the 2026-09-02 build (SELFTEST 49/49, 7888 B)~~ ~~**2026-10-10: the board runs `firmware/servo_bench` (Appendix FT); the 2026-09-02 build is gone from it.** The current uno_control source (WS2812B path, EU, FH) has never been flashed; no SELFTEST count exists for it. Actuators are unwired.~~ ~~**2026-10-13 (record HU): the board runs the current uno_control source (backlash compensation HS + steering gate HT), boot banner "SELFTEST PASS 86/86".**~~ ~~**2026-10-13 ~14:00 CDT (record HW): the board runs `firmware/servo_bench` again (for the backlash test).**~~ **2026-10-13 ~14:09 CDT (record HY): the board runs the current uno_control source (backlash 75 us, HX), banner "SERVO WIRED; MOTOR, ENCODER, LEDS, PACK UNWIRED" + "SELFTEST PASS 86/86".** The servo is on the car; motor, encoder, strip and pack are still unwired. Any later source edit re-opens the divergence - read the banner. **2026-10-16 ~17:06 CDT (record JM): STALE AGAIN - host_test on the Pi read the `== SERVO BENCH ==` banner: the board runs `firmware/servo_bench`. Re-flash uno_control before trusting any protocol test.** **2026-10-16 ~17:22 CDT (record JQ): CURRENT AGAIN - uno_control re-flashed, banner + SELFTEST PASS 86/86, host_test all ok run from the Pi.**
**Constrains:** read the boot banner before trusting any firmware claim; never assume the repo is what runs.
**Why:** a test against the wrong build verifies nothing.
**Source:** HANDOFF.md:27-34; detail in firmware-traps.md.

## 4. Battery safety: a charger is not a BMS (2026-09-30)
**What:** a 2S 18650 pack needs a board that DOCUMENTS over-discharge cutoff, or protected cells; BOM row 11's "BMS" documents over-voltage and short-circuit only. Firmware cannot guard a pack while it is off. 2026-10-04: the chosen BMS (row 11b, `B08HLQQCQJ`, 2.9 V set point re-verified live) must actually be IN the circuit - `docs/WIRING_PROTOSHIELD.md`'s net list omitted it until 2026-10-10 (now section 2.1: cells -> fuse -> B+/MB/B-, everything else on P+/P-), and anything wired to B+/B- instead of P+/P- bypasses it. **2026-10-14/15 (records IU-JA): the BMS IS in the circuit - P+ to P- 7.21 V; charger and XT30 on P+ / P-; first pack charge done (stopped at 8.29 V). Its 2.9 V cutoff and short trip remain UNTESTED. A charger wired reversed (IY) likely ruined one board - check BAT -> P+, GND -> P- twice.**
**Constrains:** no pack is specified or bought without a documented over-discharge cutoff.
**Why:** an over-discharged lithium pack is a fire and safety risk.
**Source:** HANDOFF.md:474-483; hardware.md (power section).

## 5. Steering coupler: a printed CROSS-AXLE STUB fails; nothing is load-tested (2026-09-30, sharpened 2026-10-04)
**What:** the highest-torque joint. A printed cross-axle STUB gives SF 0.57-0.96 at MG90S stall (~216 mN-m, Appendix BV) - never print one. The old wording here ("the printed one FAILS", "no coupling is chosen yet") conflated that stub with the socket-style `cad/servo_lego_coupler_v1.stl` (Appendix DG, prints no cross) and ignored BOM row 22's 2026-09-03 choice of Adafruit #4252. 2026-10-04, Evan: ~~PRINT v1 instead of buying #4252 - unless #4252 is already in the parts bin.~~ PRINT `cad/servo_lego_coupler_v2.stl` (2026-10-04: no #4252 was ever on hand; the 2026-09-03 build was a print of v1, whose axle socket was too loose). No SF is claimed or computable for either; PETG not PLA, and ~~Evan's prints so far are ABS, which nothing here analyses~~ **the couplers are printed in PLA (Bambu P1S, 0.1 mm, 2 walls, solid - Appendix FR, 2026-10-11); only the coupons were ABS**. 2026-10-10/11: servo v2 FITTED, v3 generated; motor coupler v1 too tight, v2 generated; 2026-10-11 motor coupler v3 FITS the shaft (Appendix GF). None load-tested. Fit on the MG90D-270 is not bench-verified.
**Constrains:** never print a cross-axle stub; never CLAIM any coupler works until it survives a load test; BOM row 22 is not retired until one does.
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
