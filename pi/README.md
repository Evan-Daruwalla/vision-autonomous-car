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

## Deploy (from the laptop)
    ssh ed@ed-pi5.local 'mkdir -p ~/car/ml'
    scp -r pi ed@ed-pi5.local:~/car/
    scp ml/episode_writer.py ed@ed-pi5.local:~/car/ml/

On the Pi, once:

    python3 -m venv --system-site-packages ~/car/venv
    ~/car/venv/bin/pip install -r ~/car/pi/requirements.txt

## Run
Bench mode (servo only, throttle forced 0; the pack reads FAULT while unwired):

    ~/car/venv/bin/python ~/car/pi/teleop.py --bench

On the laptop (the Gamepad API needs a secure context; localhost via the tunnel is one):

    ssh -L 8000:localhost:8000 -L 8765:localhost:8765 ed@ed-pi5.local

then open http://localhost:8000 and press a pad button.

Other flags: `--steer-invert`, `--rotate180`, `--max-throttle N` (0..100, default 0),
`--data-dir`, `--port`, `--http-port N` (page, default 8000), `--ws-port N` (websocket, default 8765;
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
  (`--steer-invert` affects the pad only); throttle = model throttle x `--max-throttle`; `--bench` forces 0.
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
