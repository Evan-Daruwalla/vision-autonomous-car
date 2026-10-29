# Real-car data collection protocol (M3 behavioral cloning)

Written 2026-10-29 (record entry to follow). Nothing here has been run yet: it is the
plan for the first driving sessions, so the laps collected are usable on the first try.
Every rule below exists because the training side needs it; the reason is next to it.

## Before a session

1. **Bench checks passed** (pi/README.md checklist): banner + SELFTEST, steer sign, camera
   colour and orientation, ~20 fps on the page, deadman trips with the pad removed.
   Without them the data can be silently wrong (a flipped image or steer sign trains a
   model that steers the wrong way and every loss curve still looks normal).
2. **Pack charged** (>= 8.0 V at rest). Throttle response changes as the pack sags; write
   the start voltage in the session notes.
3. **Same camera mount and pitch as the last session.** A moved camera is a different
   input distribution; if it moved, note it and do not mix that session into the same
   training run without saying so.
4. **Lighting:** note it (daylight / lamps / time). Mixed lighting across sessions is
   fine and even helps, but only if it is written down.
5. **Throttle cap:** start with `--max-throttle 20` (raise only after the car has driven
   clean laps at that cap). The model learns throttle too; a cap that changes mid-session
   changes what "full trigger" means, so keep one cap per session.

## During a session

- **One episode = 20 to 90 s of driving** (X starts and stops it). Episodes under 2 s
  (40 frames) are dropped by the trainer (`REAL_MIN_STEPS`); very long ones cost RAM on
  the Pi (~70 MB per minute).
- **At least 7 episodes per session.** The trainer splits by episode WITHIN each session
  (session = folder) and always holds out at least one episode for validation and one for
  test, so a 3-episode session leaves only 1 episode to learn from.
- **Clean laps:** at least 5 in each direction around the track, smooth steering, staying
  centred. These are what the model imitates; a wobbly lap teaches wobble.
- **Recovery clips (the part beginners skip, and the reason most BC cars fail):** start
  the car off-centre or angled toward the edge, press X, steer back to the centre, press
  X to stop. Record only the recovery, never the drift out. 10-20 of these, both sides,
  both directions. Without them the model has never seen what to do once it is off the
  line, so one small error grows until it leaves the track.
- **Crashes:** if the car leaves the track or hits something, press **Y** (crash). That
  ends the episode as terminal, which tells training those last frames led nowhere good.
- **Never record with the car disarmed** (recording stops itself on any disarm).
- **Keep the pad in hand the whole time;** the deadman is the only thing between a
  dropped link and a car still moving.

## After a session

1. Copy the data back to the PC **outside the repo** (the repo is public and real camera
   frames must never be committed; `car_data/` is git-ignored as a backstop):
   `scp -r ed@ed-pi5.local:~/car_data/<session> <somewhere outside the repo>`
2. Run the checker (added with this protocol): `./.venv/Scripts/python.exe ml/verify_real.py
   <dir>`. It must exit 0. It reports dropped frames, steer saturation and short episodes.
3. Write a record entry: session id, date/time (from `date`), laps and recovery clips
   recorded, throttle cap, pack voltage start/end, lighting, camera mount state, anything
   odd (link drops, crashes), and the verify_real summary.
4. Only then train: `./.venv/Scripts/python.exe ml/bc_real.py --data <dir> --out <run dir>`.

## Autopilot sessions (once a model exists)

- Car on a stand first, then on the track at the lowest cap that moves it.
- Back/View toggles AUTO; any stick or trigger input takes control back instantly.
- Autopilot frames are recorded with `log_mode = 1`. Where the model went wrong, drive a
  correction while recording: those frames are the most valuable data there is (they are
  exactly the situations the model gets wrong), and they are how the next model improves.
