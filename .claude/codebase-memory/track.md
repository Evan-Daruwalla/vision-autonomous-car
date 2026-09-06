# track.md — Autonomous Car Project

**Split out of `gotchas.md` on 2026-09-02** (Appendix BO). Traps belonging to
the physical track: layout, markings, surface, and what the camera sees of the
environment.

The track's dimensions are driven by the car's MEASURED width — that fact lives
in `hardware.md` (114.75 mm, 2026-09-02), and the generator that consumes it is
`cad/track_layout_v2.py`.

- **3DStreet is a street CROSS-SECTION tool, not a track-geometry tool**
  (assessed 2026-09-01, Appendix AM). It does linear segments plus 90-deg /
  T / dead-end intersections; **no curved streets found**, and it works in
  real-world units (a real lane is 3-3.6 m, this track's is ~0.3 m, roughly
  1/11). **Good for** marking design, dash patterns, sign placement and a
  portfolio render. **Bad for** the figure-8 plan-view geometry, which is
  the actual hard part. Keep the layout in a dimensioned plan. The
  `3dstreet-mcp` server (`.mcp.json`) is a bridge to a LIVE browser tab over
  WebSocket - alpha, no auth token, piggybacks on whichever tab is signed
  in - not a headless generator.
- **CORNER GEOMETRY IS FROZEN until the T2 turning test** (Appendix L, AM.2)
  — **still true 2026-09-05 even though every input to the formula below is
  now measured or estimated from real numbers, and those numbers keep
  moving.** Minimum turn radius = wheelbase / tan(max steer). ~~330 mm
  ESTIMATE, width/wheelbase/steer all unmeasured~~ superseded piece by
  piece: wheelbase estimated 185.95 mm (`steering.md`, Appendix DD/DE), max
  steer 58° on the current 13-stud rack, hand-measured with the servo
  DISCONNECTED (Appendix DL) — ~~capped 45° for planning margin (Appendix
  DM)~~ **CORRECTED same day (Appendix DN): the MG90S is fixed at 90° each
  way and is now out-travelled by the rack (135° each way), so 58° is the
  rack's limit, not the servo's, and 45° may not be achievable at all.
  Servo-achievable ESTIMATE (unverified): ~38.7°.** Giving bare-linkage
  **R_min ~ 116.2 mm**, servo-estimate **R_min ~ 232.4 mm**. Both
  comfortably under the 330 mm estimate on TURN RADIUS. **But car width
  ALSO changed the same day** — ~~148.25 mm rear track governs~~ **front
  track is now 155 mm and governs instead (Appendix DM)** — and that pushes
  lane width to 310 mm, which makes the FLOOR-FIT tight: `cad/
  track_layout_v2.py`'s own 100 mm safety-margin self-check now FAILS at
  R=500 (only 90 mm spare). Turn radius has slack; floor space does not.
  **None of this unfreezes corner geometry.** A geometric estimate from real
  measurements is still not the same claim as T2's empirical test on the
  rolling chassis, and both the steering number and the car width have now
  changed while the mechanism was still being built out — cutting or
  printing corner tiles before T2 still risks a track sized for numbers
  that move again before the car is done.
- **Track: print MARKINGS, not the road surface** (2026-08-05). Full-surface
  printing is ~6.4 kg / ~150-250 h for a minimum loop vs ~0.15 kg / ~6 h for
  markings — 97% less for identical camera input, because at 120×160 the
  camera sees markings, not road. Substrate is dark matte foam board /
  coroplast. Don't let a future session "improve" this back to printed tiles.
- **Track layout must be a FIGURE-8, not an oval** (2026-08-05). A one-handed
  loop teaches the BC model "always steer left" — perfect on the training
  track, useless elsewhere. The figure-8 also provides the intersection for
  the stop sign.
- **A seam running perpendicular to travel reads as a stop bar** to the
  model. Run tile seams parallel to travel where possible (2026-08-05).
- **Lock the camera pitch before data collection and record the angle** —
  changing it mid-dataset silently splits the data into two incompatible
  distributions. Vary LIGHTING across sessions on purpose (real-world domain
  randomization); never vary the camera geometry (2026-08-05).
- **Glare:** glossy plastic under room lighting produces specular highlights
  that wash out markings. Matte everything; if printing surface pieces, print
  face-down on a textured plate (2026-08-05).
- **A stop sign is provably unlearnable by plain BC** (2026-08-05). Stopped
  at the line the image is identical whether to wait or go, so the action
  depends on history, which π(action|image) cannot express (frame-stacking
  gives ~0.2 s at 20 Hz; a stop is 2-3 s). This is a FEATURE of the plan —
  it is the M4 world-model showcase, since the RSSM/MDN-RNN has recurrent
  state. Traffic lights are the opposite: memoryless-learnable (state is
  visible in the frame) but need hardware.
