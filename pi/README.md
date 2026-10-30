# pi/ - teleop + recording on the Raspberry Pi

Status: sim-only (FakeUno/FakeCamera) until the on-Pi checklist below is done.

## Files
- `protocol.py` - byte codec for firmware/SERIAL_PROTOCOL.md v0.2.
- `uno_link.py` - serial link to the Uno (banner + SELFTEST gate) and `FakeUno`.
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
autopilot unavailable); a `/dev/ttyACM*` device; >= 2 GB free under `~`; one
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
`--host` (bind address, default 127.0.0.1), `--data-dir`, `--port`, `--http-port N` (page, default 8000), `--ws-port N` (websocket, default 8765;
if you change either, change the ssh tunnel and the page URL to match), `--model <path.onnx>`,
`--fake` (no hardware; pack reads FAULT, so use `--bench` to arm; uses a stub autopilot unless `--model` is given).

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

## On-Pi bench checklist (UNVERIFIED until done)
- [ ] Banner printed and SELFTEST PASS gate holds (teleop exits 2 otherwise).
- [ ] Stick right -> wheels turn right (else add `--steer-invert`).
- [ ] Camera colour: hold a red object, it must look red on the page.
- [ ] Camera orientation correct (else add `--rotate180`).
- [ ] fps shown on the page is ~20.
- [ ] Deadman: unplug the pad or close the laptop lid -> armed false within ~0.3 s and the servo holds.
- [ ] Record 30 s, `scp` the npz back, load it:
      `./.venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'ml'); from episode_writer import load_episode as L; e=L(sys.argv[1]); print({k:v.shape for k,v in e.items() if hasattr(v,'shape')})" <file.npz>`

The motor is unwired: never pass `--max-throttle` until the motor is wired and the car is on a stand.
