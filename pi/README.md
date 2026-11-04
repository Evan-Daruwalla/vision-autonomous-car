# pi/ - teleop + recording on the Raspberry Pi

Status: ~~sim-only (FakeUno/FakeCamera) until the on-Pi checklist below is done.~~ (2026-11-04 audit fix) Run on the Pi off-car (record LR) and on the car with the Uno on /dev/ttyUSB0: host_test --wired passed (NC), teleop drove the motor on the stand (NE).

## Files
- `protocol.py` - byte codec for firmware/SERIAL_PROTOCOL.md v0.2.
- `uno_link.py` - serial link to the Uno (banner + SELFTEST gate) and `FakeUno`.
- `motor_sweep.py` - motor diagnosis on the stand (added 2026-11-01, records NG-NI): interleaved +/- throttle steps with braked rests, encoder ticks/s per step, a verdict and a JSON log in `~/car_data/`. Flags: `--levels --repeats --hold --rest --out`, or `--steady THR --seconds N` to hold one throttle; `--self-check`.
- `camera.py` - `PiCamera` (picamera2), `FakeCamera`, JPEG encode.
- `recorder.py` - buffers one episode, writes an npz via `ml/episode_writer.py`.
- `preprocess_frame.py` - the one frame -> model-input function (64x64 float32 CHW), shared with training.
- `autopilot.py` - `Autopilot` (ONNX via onnxruntime) and `StubAutopilot`.
- `teleop.py` - control loop (20 Hz), websocket (8765), page server (8000).
- `web/index.html` - video, telemetry, pad input (browser Gamepad API).

## Deploy (from the laptop, repo root)
    bash pi/deploy.sh --dry-run           # prints the commands, runs nothing
    bash pi/deploy.sh [user@host]         # default ed@ed-pi5.local

It does `mkdir -p`, `scp` of `pi/*.py pi/web pi/requirements*.txt` plus the `ml/`
files the recorder and `verify_corpus.py` import (`episode_writer`, `verify_corpus`,
`collect_sim_data`, `collect_recovery`, `sim_conf`; gym is imported lazily there so
none needs it on the Pi) and `firmware/host_test.py`, then creates `~/car/venv`
(`--system-site-packages`) if missing and `pip install -r requirements.txt`.
It deletes nothing on the Pi. It prints the next commands when done.

## Preflight (on the Pi, before teleop)
    ~/car/venv/bin/python ~/car/pi/preflight.py

One PASS/FAIL/WARN line per check, exit 1 on any FAIL: python version; numpy,
serial, websockets, PIL, picamera2 imports (onnxruntime optional: WARN means
autopilot unavailable); a `/dev/ttyACM*` or `/dev/ttyUSB*` device; >= 2 GB free under `~`; one
120x160x3 camera frame; Uno banner + SELFTEST PASS (opening the port resets the
Uno). `--fake` swaps in FakeCamera/FakeUno and drops the picamera2 and device
requirements so it runs on the PC (sim-only: proves nothing about the Pi).

## Link faults and reconnect
`link_ok` goes False on 3 missed replies in a row OR 2 consecutive replies with
the CRC-bad status bit (SERIAL_PROTOCOL rule 3). Only replies whose seq matches
the command are counted; a bad-CRC reply with a garbled seq shows up as a miss.
While the link is down the car is disarmed (`link_lost`) and `arm` is refused
(`arm_refused_link`). The control loop then calls `UnoLink.reopen()` at most once
every 2.0 s, after the tick that disarmed, with the app lock released; opening
the port resets the Uno (~2.2 s plus banner), so no commands go out meanwhile.
Events `reconnect_ok` / `reconnect_failed`. A successful reconnect does NOT
re-arm: a new arm command is needed. A background save that raises surfaces as
event `save_failed <error>` (the traceback also prints on the Pi console).
A reply with the watchdog status bit while armed disarms (`watchdog_disarm`; the firmware itself resumes on the next ARMED frame): press A to re-arm.
Tested with FakeUno only (`disconnect()`, `corrupt`); not tried on a real cable pull.

## Run
Bench mode (servo only, throttle forced 0; the pack reads FAULT while unwired):

    ~/car/venv/bin/python ~/car/pi/teleop.py --bench

On the laptop (the Gamepad API needs a secure context; localhost via the tunnel is one):

    ssh -L 8000:localhost:8000 -L 8765:localhost:8765 ed@ed-pi5.local

then open http://localhost:8000 and press a pad button.

The server binds `127.0.0.1` by default (`--host`), so only the SSH tunnel can reach it; there is
NO login. `--host 0.0.0.0` prints a warning because anyone on the network could then drive the car.
The websocket also rejects any browser Origin other than `http://localhost:<http-port>` /
`http://127.0.0.1:<http-port>`, so the tunnel's local port must equal `--http-port`.

Other flags: `--steer-invert`, `--rotate180`, `--max-throttle N` (0..100, default 0),
`--host` (bind address, default 127.0.0.1), `--data-dir`, `--port` (default: auto-detect, first `/dev/ttyACM*` then `/dev/ttyUSB*`), `--http-port N` (page, default 8000), `--ws-port N` (websocket, default 8765;
if you change either, change the ssh tunnel and the page URL to match), `--model <path.onnx>`,
`--fake` (no hardware; pack reads FAULT, so use `--bench` to arm; uses a stub autopilot unless `--model` is given),
`--fake-uno` (FakeUno + real PiCamera, for the Pi off the car; episodes are flagged `fake_uno` and rejected by verify_real/bc_real).

## Pad mapping (browser "standard" mapping)
| Control | Action |
|---|---|
| Left stick X (axes[0]) | steer (deadzone 0.08) |
| RT / LT (buttons 7 / 6) | throttle = RT - LT, scaled by --max-throttle |
| A | arm |
| B | disarm |
| X | toggle recording (only while armed) |
| Y | end episode as crash + disarm |
| Back/View (buttons[8]) | toggle AUTO |

Keyboard: Space = disarm, Enter = arm, R = rec toggle, A = auto toggle.

## AUTO mode (model drives)
Start with `--model <path.onnx>` (needs `requirements-autopilot.txt`; input tensor named `image`,
64x64 float32 via `preprocess_frame.py`). Without `--model` AUTO is unavailable
(`auto_unavailable`); with `--fake` and no model a stub that outputs steer 0.3, throttle 0.5 is used.
- Back/View or the A key (or the AUTO button) toggles AUTO. Manual -> auto only while armed
  (else `auto_refused_not_armed`); auto -> manual always. The page shows MODE large.
- Override: in AUTO, pad steer beyond 0.15 or pad throttle beyond 0.05 drops to MANUAL at once
  (`auto_override`) and that tick uses the pad. Any disarm (deadman, link, pack, button) also returns to MANUAL.
- Pad input must stay fresh in AUTO: the deadman still applies. steer = model steer x 100
  (`--steer-invert` affects the pad only); throttle = round(model throttle x 100), clipped to +/-`--max-throttle` (training labels are cmd/100 and
  already include the cap, so it is not scaled again); `--bench` forces 0. A non-finite model output raises
  `autopilot_error` and disarms.
- Recorded episodes carry `log_mode` (0 manual, 1 auto) per frame.
- Never pass `--max-throttle` with a model until the motor is wired and the car is on a stand.

## Data
Episodes land in `~/car_data/<session>/` (session = start time). Copy back:

    scp -r ed@ed-pi5.local:~/car_data .

## Off-car session (Pi on the desk, Uno NOT attached)
1. PC: `bash pi/deploy.sh`, then on the Pi `~/car/venv/bin/python ~/car/pi/preflight.py --no-uno` - must
   end "preflight: PASS (Uno not checked)". Proves deploy, venv, imports and the real camera.
2. Full fake: Pi `~/car/venv/bin/python ~/car/pi/teleop.py --fake --bench --data-dir ~/car_data_test`;
   PC `ssh -L 8000:localhost:8000 -L 8765:localhost:8765 ed@ed-pi5.local`, open http://localhost:8000,
   plug in the Xbox pad. Check: A arms, B disarms, sticks move the steer readout, unplug the pad ->
   armed false within ~0.3 s, X records ~30 s.
3. Real camera, fake Uno: same but `--fake-uno` instead of `--fake`. Check: a red object looks red, fps
   ~20, note the first-frame ScalerCrop line printed in the Pi terminal. Do NOT judge orientation here
   (it depends on the camera mount on the car).
4. PC: `scp -r ed@ed-pi5.local:~/car_data_test <a folder OUTSIDE the repo>` then
   `./.venv/Scripts/python.exe ml/verify_real.py <that folder>` - expect exit 1 with only "recorded with
   fake hardware" FAILs (that proves the guard works); read the frame-gap % (real Pi timing).
5. Autopilot latency: Pi `~/car/venv/bin/pip install -r ~/car/pi/requirements-autopilot.txt` (if pip
   finds no wheel for the Pi's Python, stop - do not build from source); PC
   `./.venv/Scripts/python.exe ml/export_onnx.py --untrained --out bcnet_untrained.onnx`,
   `scp bcnet_untrained.onnx ed@ed-pi5.local:~/car/`; Pi
   `~/car/venv/bin/python ~/car/pi/autopilot.py --bench ~/car/bcnet_untrained.onnx`. The weights are
   random: the timing is real, the outputs mean nothing. Budget: 50 ms per 20 Hz tick.

Never plug the car's Uno into the Pi until the shield fixes (record LC) and meter checks are done (done: MI, MJ, MO); never
pass --max-throttle off the car.

## On-Pi bench checklist (UNVERIFIED until done)
- [ ] Banner printed and SELFTEST PASS gate holds (teleop exits 2 otherwise).
- [ ] Stick right -> wheels turn right (else add `--steer-invert`).
- [ ] Camera colour: hold a red object, it must look red on the page.
- [ ] Camera orientation correct (else add `--rotate180`).
- [ ] fps shown on the page is ~20.
- [ ] Deadman: unplug the pad or close the laptop lid -> armed false within ~0.3 s and the servo holds.
- [ ] Record 30 s, `scp` the npz back, load it:
      `./.venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'ml'); from episode_writer import load_episode as L; e=L(sys.argv[1]); print({k:v.shape for k,v in e.items() if hasattr(v,'shape')})" <file.npz>`

~~The motor is unwired:~~ (2026-11-01: the motor is wired, record NB.) Never pass `--max-throttle` unless the car is on a stand.
