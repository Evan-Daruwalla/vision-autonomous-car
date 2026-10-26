"""Teleop server for the car's Pi: browser pad input in, Uno commands out, video + data back.

WHY the split: `Controller` is pure logic (no IO, no clock reads; time is passed
in) so every safety rule - deadman, pack gate, throttle cap, steer hold - is
unit-tested on a PC. `TeleopApp` is the IO shell: a 20 Hz control thread paced
by the camera, a websocket server for pad input + telemetry + JPEG video, and
a stdlib HTTP server for the page. Shared state sits under one Lock.

Safety summary (decisions D7/D8 in the teleop plan): input older than the
deadman window disarms and zeroes throttle while steer is HELD (the Uno
watchdog also holds steer); arm is refused on a CUTOFF/FAULT pack unless
--bench, and bench forces throttle 0; a disarm of any kind truncates the
recording. A FakeUno/FakeCamera pass is sim-only: it proves nothing about the
real car, servo sign, camera colour or the browser Gamepad API.

    ./.venv/Scripts/python.exe pi/teleop.py --fake
    ./.venv/Scripts/python.exe pi/teleop.py --self-check
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import argparse
import asyncio
import collections
import functools
import json
import math
import socket
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import websockets

import protocol
from camera import FakeCamera, PiCamera, encode_jpeg
from recorder import Recorder
from uno_link import FakeUno, UnoLink

BAD_PACK = (protocol.PACK_CUTOFF, protocol.PACK_FAULT)
DISARM_EVENTS = ("deadman", "link_lost")


def _is_disarm_event(ev: str) -> bool:
    return ev in DISARM_EVENTS or ev.startswith("pack_")


class Controller:
    """Pure teleop logic: pad input + commands -> (steer, throttle, armed)."""

    def __init__(self, max_throttle: int, bench: bool, steer_invert: bool,
                 deadman_s: float = 0.25, deadzone: float = 0.08) -> None:
        if not 0 <= max_throttle <= 100:
            raise ValueError(f"max_throttle must be 0..100, got {max_throttle}")
        self.max_throttle = max_throttle
        self.bench = bench
        self.steer_invert = steer_invert
        self.deadman_s = deadman_s
        self.deadzone = deadzone
        self.armed = False
        self.last_steer_cmd = 0
        self.input: tuple[float, float, float | None] = (0.0, 0.0, None)
        self._now = 0.0                       # latest time seen (set_input / tick)

    def set_input(self, steer: float, throttle: float, now: float) -> None:
        clip = lambda v: max(-1.0, min(1.0, float(v)))
        self.input = (clip(steer), clip(throttle), now)
        self._now = max(self._now, now)

    def _fresh(self, now: float) -> bool:
        t = self.input[2]
        return t is not None and now - t <= self.deadman_s

    def command(self, name: str, pack: int | None) -> list[str]:
        if name == "arm":
            # pack None = no reply seen yet: unknown is refused like a bad pack
            if (pack is None or pack in BAD_PACK) and not self.bench:
                return ["arm_refused_pack"]
            if not self._fresh(self._now):
                return ["arm_refused_no_input"]
            if abs(self.input[1]) > 0.05:     # trigger held: arming would lurch
                return ["arm_refused_throttle"]
            self.armed = True
            return ["armed"]
        if name == "disarm":
            self.armed = False
            return ["disarmed"]
        if name == "rec_toggle":
            return ["rec_toggle"]
        if name == "crash":
            self.armed = False
            return ["crash", "disarmed"]
        raise ValueError(f"unknown command {name!r}")

    def _steer(self) -> int:
        s = self.input[0]
        dz = self.deadzone
        s = 0.0 if abs(s) <= dz else math.copysign((abs(s) - dz) / (1.0 - dz), s)
        if self.steer_invert:
            s = -s
        return max(-100, min(100, int(round(s * 100))))

    def tick(self, now: float, pack: int | None,
             link_ok: bool) -> tuple[int, int, bool, list[str]]:
        self._now = max(self._now, now)
        events: list[str] = []
        fresh = self._fresh(now)
        if self.armed and not fresh:
            self.armed = False
            events.append("deadman")
        if self.armed and not link_ok:
            self.armed = False
            events.append("link_lost")
        if self.armed and pack in BAD_PACK and not self.bench:
            self.armed = False
            events.append("pack_" + protocol.PACK_NAMES[pack])
        if fresh:
            self.last_steer_cmd = self._steer()
        steer_cmd = self.last_steer_cmd       # stale: HELD, like the firmware watchdog
        if self.armed and fresh and not self.bench:
            thr_cmd = int(round(self.input[1] * self.max_throttle))
        else:
            thr_cmd = 0
        return steer_cmd, thr_cmd, self.armed, events


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass


class TeleopApp:
    def __init__(self, uno, cam, recorder: Recorder, controller: Controller,
                 http_port: int, ws_port: int, web_dir: str | Path,
                 host: str = "0.0.0.0") -> None:
        self.uno = uno
        self.cam = cam
        self.recorder = recorder
        self.controller = controller
        self.http_port = http_port
        self.ws_port = ws_port
        self.web_dir = str(web_dir)
        self.host = host
        self.lock = threading.Lock()
        self._stop = threading.Event()
        self._shut = False
        self._ctl_thread: threading.Thread | None = None
        self._http: ThreadingHTTPServer | None = None
        self._http_thread: threading.Thread | None = None
        self._ws_thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._ws_stop: asyncio.Event | None = None
        self._ws_ready = threading.Event()
        self._ws_error: BaseException | None = None
        self._clients: set = set()
        self.malformed = 0
        self._save_threads: list[threading.Thread] = []
        # shared state (under lock)
        self.last_pack: int | None = None
        self.last_ticks = 0
        self.last_saved: str | None = None
        self.latest_jpeg: bytes | None = None
        self.jpeg_seq = 0
        self.events: collections.deque[str] = collections.deque(maxlen=5)
        self._frame_times: collections.deque[float] = collections.deque(maxlen=20)
        self._frame_n = 0
        self.telem: dict = {}

    # ---- recording helpers (call with lock held) ----
    def _stop_recording(self, crash: bool) -> None:
        """Recording off now; the npz is written on a worker thread (never blocks 20 Hz)."""
        def on_saved(path: Path | None) -> None:
            with self.lock:
                self.last_saved = str(path) if path else None
                self.events.append("saved " + (path.name if path else "none (too short)"))
        self._save_threads.append(
            self.recorder.stop_background(crash=crash, on_saved=on_saved))

    # ---- control thread ----
    def _control_loop(self) -> None:
        while not self._stop.is_set():
            try:
                frame, t_frame = self.cam.read()
            except Exception as e:  # camera died: stop safely, do not spin
                with self.lock:
                    self.controller.armed = False
                    self.events.append(f"camera_error {e}")
                self._stop.set()
                break
            now = time.monotonic()
            with self.lock:
                steer, thr, armed, ev = self.controller.tick(
                    now, self.last_pack, self.uno.link_ok)
                t_cmd = time.monotonic_ns()
                reply = self.uno.exchange(steer, thr, armed)
                if reply is not None:
                    self.last_pack = reply.pack
                    self.last_ticks = reply.ticks
                if self.recorder.recording:
                    self.recorder.add(frame, (steer, thr), {
                        "ticks": self.last_ticks,
                        "status": reply.status if reply else 0,
                        "t_frame_ns": t_frame, "t_cmd_ns": t_cmd,
                        "loop_dt": reply.dt if reply else 0})
                if any(_is_disarm_event(e) for e in ev) and self.recorder.recording:
                    self._stop_recording(crash=False)
                self.events.extend(ev)
                self._frame_n += 1
                if self._frame_n % 2 == 0:
                    self.latest_jpeg = encode_jpeg(frame)
                    self.jpeg_seq += 1
                self._frame_times.append(now)
                ft = self._frame_times
                fps = (len(ft) - 1) / (ft[-1] - ft[0]) if len(ft) > 1 and ft[-1] > ft[0] else 0.0
                st = reply.status if reply else 0
                self.telem = {
                    "armed": armed,
                    "recording": self.recorder.recording,
                    "steps": self.recorder.steps,
                    "steer_cmd": steer, "thr_cmd": thr,
                    "ticks": self.last_ticks,
                    "status": st,
                    "watchdog": bool(st & protocol.ST_WATCHDOG),
                    "crc_bad": bool(st & protocol.ST_CRC_BAD),
                    "dropped": bool(st & protocol.ST_DROPPED),
                    "pack_name": (protocol.PACK_NAMES[self.last_pack]
                                  if self.last_pack is not None else "?"),
                    "link_ok": self.uno.link_ok,
                    "loop_dt_ms": (reply.dt / 10.0) if reply else 0.0,
                    "fps": round(fps, 1),
                    "last_saved": self.last_saved,
                    "events": list(self.events),
                    "max_throttle": self.controller.max_throttle,
                    "bench": self.controller.bench,
                }

    # ---- commands ----
    def handle_command(self, name: str) -> None:
        with self.lock:
            events = self.controller.command(name, self.last_pack)
            self.events.extend(events)
            if name == "rec_toggle":
                if self.recorder.recording:
                    self._stop_recording(crash=False)
                elif self.controller.armed:
                    self.recorder.start()
                else:
                    self.events.append("rec_refused_not_armed")
            elif name == "crash":
                if self.recorder.recording:
                    self._stop_recording(crash=True)
            elif name == "disarm" and self.recorder.recording:
                self._stop_recording(crash=False)

    def _on_message(self, raw: str | bytes) -> None:
        try:
            msg = json.loads(raw)
            kind = msg["type"]
            if kind == "input":
                steer, thr = float(msg["steer"]), float(msg["throttle"])
                if not (math.isfinite(steer) and math.isfinite(thr)):
                    raise ValueError("non-finite input")
                with self.lock:
                    self.controller.set_input(steer, thr, time.monotonic())
            elif kind == "cmd":
                name = msg["name"]
                if not isinstance(name, str):
                    raise ValueError("bad cmd name")
                self.handle_command(name)
            else:
                raise ValueError(f"unknown type {kind!r}")
        except (ValueError, KeyError, TypeError):
            self.malformed += 1

    # ---- websocket ----
    async def _handler(self, ws) -> None:
        self._clients.add(ws)
        try:
            async for raw in ws:
                self._on_message(raw)
        except websockets.ConnectionClosed:
            pass
        finally:
            self._clients.discard(ws)

    async def _broadcaster(self) -> None:
        last_seq = -1
        while True:
            await asyncio.sleep(0.1)
            if not self._clients:
                continue
            with self.lock:
                telem = dict(self.telem)
                jpeg = self.latest_jpeg
                seq = self.jpeg_seq
            if telem:
                telem["type"] = "telem"
                websockets.broadcast(self._clients, json.dumps(telem))
            if jpeg is not None and seq != last_seq:
                last_seq = seq
                websockets.broadcast(self._clients, jpeg)

    async def _ws_main(self) -> None:
        self._ws_stop = asyncio.Event()
        try:
            server = await websockets.serve(self._handler, self.host, self.ws_port)
        except BaseException as e:
            self._ws_error = e
            self._ws_ready.set()
            return
        task = asyncio.ensure_future(self._broadcaster())
        self._ws_ready.set()
        await self._ws_stop.wait()
        task.cancel()
        server.close()
        await server.wait_closed()

    def _ws_thread_main(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._ws_main())
        self._loop.close()

    # ---- lifecycle ----
    def start_background(self) -> None:
        self.cam.start()
        self._http = ThreadingHTTPServer(
            (self.host, self.http_port),
            functools.partial(_QuietHandler, directory=self.web_dir))
        self._http.daemon_threads = True
        self._http_thread = threading.Thread(
            target=self._http.serve_forever, daemon=True)
        self._http_thread.start()
        self._ws_thread = threading.Thread(target=self._ws_thread_main, daemon=True)
        self._ws_thread.start()
        if not self._ws_ready.wait(10.0):
            raise RuntimeError("websocket server did not start")
        if self._ws_error is not None:
            raise RuntimeError(f"websocket server failed: {self._ws_error!r}")
        self._ctl_thread = threading.Thread(target=self._control_loop, daemon=True)
        self._ctl_thread.start()

    def run(self) -> None:
        self.start_background()
        try:
            while not self._stop.is_set():
                time.sleep(0.2)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        if self._shut:
            return
        self._shut = True
        self._stop.set()
        if self._ctl_thread is not None:
            self._ctl_thread.join(timeout=2.0)
        with self.lock:
            self.controller.armed = False
            for _ in range(5):                # disarmed frames, steer held, thr 0
                try:
                    self.uno.exchange(self.controller.last_steer_cmd, 0, False)
                except Exception:
                    break
            if self.recorder.recording:
                try:
                    self._stop_recording(crash=False)
                except Exception as e:
                    print(f"recording save failed on shutdown: {e}")
        for t in list(self._save_threads):   # outside the lock: on_saved takes it
            t.join(timeout=30.0)
        for closer in (self.cam.stop, self.uno.close):
            try:
                closer()
            except Exception as e:
                print(f"shutdown: {e}")
        if self._loop is not None and self._ws_stop is not None:
            self._loop.call_soon_threadsafe(self._ws_stop.set)
        if self._ws_thread is not None:
            self._ws_thread.join(timeout=3.0)
        if self._http is not None:
            self._http.shutdown()
            self._http.server_close()


# ---------------------------------------------------------------- self check

def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _check_controller() -> None:
    def ctl(**kw) -> Controller:
        args = dict(max_throttle=0, bench=False, steer_invert=False)
        args.update(kw)
        return Controller(**args)

    def steer_of(c: Controller, s: float) -> int:
        c.set_input(s, 0.0, 0.0)
        return c.tick(0.0, 0, True)[0]

    c = ctl()
    assert steer_of(c, 1.0) == 100
    assert steer_of(c, 0.05) == 0
    assert steer_of(c, -0.5) == round(-100 * (0.42 / 0.92))
    assert steer_of(ctl(steer_invert=True), 1.0) == -100
    assert steer_of(ctl(steer_invert=True), -0.5) == -round(-100 * (0.42 / 0.92))

    c = ctl(max_throttle=30)
    c.set_input(0.0, 1.0, 0.0)
    assert c.command("arm", protocol.PACK_OK) == ["arm_refused_throttle"]
    assert c.command("arm", None) == ["arm_refused_pack"]   # no reply seen yet
    c.set_input(0.0, 0.0, 0.0)
    assert c.command("arm", protocol.PACK_OK) == ["armed"]
    c.set_input(0.0, 1.0, 0.0)
    assert c.tick(0.0, protocol.PACK_OK, True)[:3] == (0, 30, True)
    c = ctl(max_throttle=0)
    c.set_input(0.0, 0.0, 0.0)
    c.command("arm", protocol.PACK_OK)
    c.set_input(0.0, 1.0, 0.0)
    assert c.tick(0.0, protocol.PACK_OK, True)[1] == 0
    c = ctl(max_throttle=30)
    c.set_input(0.0, 1.0, 0.0)
    assert c.tick(0.0, protocol.PACK_OK, True)[1:3] == (0, False)

    c = ctl(max_throttle=30)
    c.set_input(0.0, 1.0, 0.0)
    assert c.command("arm", protocol.PACK_FAULT) == ["arm_refused_pack"] and not c.armed
    c = ctl(max_throttle=30, bench=True)
    c.set_input(0.0, 0.0, 0.0)
    assert c.command("arm", protocol.PACK_FAULT) == ["armed"]
    c.set_input(0.0, 1.0, 0.0)
    assert c.tick(0.0, protocol.PACK_FAULT, True)[1:3] == (0, True)
    c = ctl(max_throttle=30)                  # no input yet -> refused
    assert c.command("arm", protocol.PACK_OK) == ["arm_refused_no_input"]

    c = ctl(max_throttle=30)                  # pack goes bad while armed
    c.set_input(0.0, 0.0, 0.0)
    c.command("arm", protocol.PACK_OK)
    c.set_input(0.0, 1.0, 0.0)
    s, t, a, ev = c.tick(0.0, protocol.PACK_CUTOFF, True)
    assert (a, t, ev) == (False, 0, ["pack_CUTOFF"])

    c = ctl(max_throttle=30)                  # deadman: steer held
    c.set_input(0.5, 0.0, 0.0)
    c.command("arm", protocol.PACK_OK)
    c.set_input(0.5, 0.5, 0.0)
    s0, _, _, _ = c.tick(0.05, protocol.PACK_OK, True)
    assert s0 == round(100 * (0.42 / 0.92))
    s, t, a, ev = c.tick(0.26, protocol.PACK_OK, True)
    assert (s, t, a) == (s0, 0, False) and "deadman" in ev, (s, t, a, ev)

    c = ctl(max_throttle=30)
    c.set_input(0.0, 0.0, 0.0)
    c.command("arm", protocol.PACK_OK)
    c.set_input(0.0, 0.5, 0.0)
    s, t, a, ev = c.tick(0.05, protocol.PACK_OK, False)
    assert not a and "link_lost" in ev

    c = ctl(max_throttle=30)
    c.set_input(0.0, 0.0, 0.0)
    c.command("arm", protocol.PACK_OK)
    c.set_input(0.0, 0.5, 0.0)
    ev = c.command("crash", protocol.PACK_OK)
    assert "crash" in ev and "disarmed" in ev and not c.armed
    try:
        c.command("nope", None)
    except ValueError:
        pass
    else:
        raise AssertionError("unknown command accepted")


async def _client_session(ws_port: int) -> tuple[list[dict], list[bytes]]:
    telems: list[dict] = []
    blobs: list[bytes] = []
    async with websockets.connect(f"ws://127.0.0.1:{ws_port}") as ws:
        sending = True
        thr = 0.0                              # trigger released until armed

        async def reader() -> None:
            async for m in ws:
                if isinstance(m, bytes):
                    blobs.append(m)
                else:
                    telems.append(json.loads(m))

        async def sender() -> None:
            while sending:
                await ws.send(json.dumps({"type": "input", "steer": 0.5,
                                          "throttle": thr}))
                await asyncio.sleep(0.02)

        rtask = asyncio.ensure_future(reader())
        stask = asyncio.ensure_future(sender())
        await asyncio.sleep(0.1)
        await ws.send(json.dumps({"type": "cmd", "name": "arm"}))
        await ws.send(json.dumps({"type": "cmd", "name": "rec_toggle"}))
        thr = 0.5
        await ws.send("not json")             # must be ignored, not fatal
        await asyncio.sleep(2.0)
        await ws.send(json.dumps({"type": "cmd", "name": "rec_toggle"}))
        sending = False
        await stask
        await asyncio.sleep(0.5)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if telems and not telems[-1]["armed"] and "deadman" in telems[-1]["events"]:
                break
            await asyncio.sleep(0.05)
        rtask.cancel()
    return telems, blobs


def _check_end_to_end() -> None:
    import tempfile
    import numpy as np
    from episode_writer import load_episode

    with tempfile.TemporaryDirectory() as td:
        rec = Recorder(td, session="sc", meta={"fake": True})
        ctl = Controller(max_throttle=30, bench=False, steer_invert=False)
        app = TeleopApp(FakeUno(pack=protocol.PACK_OK), FakeCamera(), rec, ctl,
                        _free_port(), _free_port(),
                        Path(__file__).resolve().parent / "web", host="127.0.0.1")
        app.start_background()
        try:
            telems, blobs = asyncio.run(_client_session(app.ws_port))
        finally:
            app.shutdown()
        assert telems, "no telemetry received"
        last = telems[-1]
        assert last["armed"] is False and "deadman" in last["events"], last
        assert blobs and blobs[0][:2] == b"\xff\xd8", "no JPEG received"
        assert app.malformed >= 1
        npzs = list(Path(td).rglob("*.npz"))
        assert len(npzs) == 1, npzs
        ep = load_episode(npzs[0])
        T = len(ep["action"])
        assert T >= 20, T
        want = [round(100 * (0.42 / 0.92)) / 100, 0.15]
        assert np.allclose(ep["action"][-1], want, atol=1e-6), ep["action"][-1]
        cmd = ep["log_cmd_next"]
        for i in range(1, T):
            assert np.allclose(ep["action"][i], cmd[i - 1] / 100.0, atol=1e-6), i
        assert not ep["is_terminal"].any()


def self_check() -> None:
    t0 = time.monotonic()
    _check_controller()
    _check_end_to_end()
    assert time.monotonic() - t0 < 20.0
    print("teleop self_check: PASS")


# ---------------------------------------------------------------------- main

def _max_throttle(v: str) -> int:
    n = int(v)
    if not 0 <= n <= 100:
        raise argparse.ArgumentTypeError("must be 0..100")
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--fake", action="store_true", help="FakeUno + FakeCamera")
    ap.add_argument("--max-throttle", type=_max_throttle, default=0)
    ap.add_argument("--bench", action="store_true")
    ap.add_argument("--steer-invert", action="store_true")
    ap.add_argument("--rotate180", action="store_true")
    ap.add_argument("--data-dir", default="~/car_data")
    ap.add_argument("--http-port", type=int, default=8000)
    ap.add_argument("--ws-port", type=int, default=8765)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()

    if args.self_check:
        self_check()
        return 0

    try:
        uno = FakeUno() if args.fake else UnoLink(args.port)
        banner = uno.open()
    except Exception as e:
        print(f"Uno open failed: {e!r}")
        return 2
    print("Uno banner:", " | ".join(banner))
    cam = FakeCamera() if args.fake else PiCamera(rotate180=args.rotate180)

    meta = {"max_throttle": args.max_throttle, "bench": args.bench,
            "steer_invert": args.steer_invert, "camera": cam.config,
            "banner": " | ".join(banner), "protocol": "v0.2", "fake": args.fake}
    rec = Recorder(args.data_dir, meta=meta)
    ctl = Controller(args.max_throttle, args.bench, args.steer_invert)
    app = TeleopApp(uno, cam, rec, ctl, args.http_port, args.ws_port,
                    Path(__file__).resolve().parent / "web")
    if args.max_throttle > 0 and args.bench:
        print("NOTE: --bench forces throttle 0 (max-throttle ignored).")
    print(f"Data dir: {rec.directory}")
    print(f"HTTP :{args.http_port}  WS :{args.ws_port}")
    print(f"From the laptop: ssh -L {args.http_port}:localhost:{args.http_port} "
          f"-L {args.ws_port}:localhost:{args.ws_port} ed@ed-pi5.local")
    print(f"then open http://localhost:{args.http_port}")
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
