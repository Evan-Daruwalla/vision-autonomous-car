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
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import websockets

import protocol
from camera import FakeCamera, PiCamera, encode_jpeg
from recorder import Recorder
from uno_link import FakeUno, UnoLink

BAD_PACK = (protocol.PACK_CUTOFF, protocol.PACK_FAULT)
DISARM_EVENTS = ("deadman", "link_lost")
AUTO_STEER_OVERRIDE = 0.15      # pad steer magnitude that hands control back
AUTO_THROTTLE_OVERRIDE = 0.05   # pad throttle magnitude that hands control back
REOPEN_INTERVAL_S = 2.0         # min gap between serial reopen attempts


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
        self.mode = "manual"                  # "manual" | "auto"
        self.autopilot_output: tuple[float, float] | None = None
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

    def command(self, name: str, pack: int | None, link_ok: bool = True) -> list[str]:
        if name == "arm":
            if not link_ok:                   # only "arm" looks at it
                return ["arm_refused_link"]
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
            return ["disarmed"] + self._leave_auto()
        if name == "rec_toggle":
            return ["rec_toggle"]
        if name == "crash":
            self.armed = False
            return ["crash", "disarmed"] + self._leave_auto()
        if name == "auto_toggle":
            if self.mode == "auto":
                self.mode = "manual"
                return ["auto_off"]
            if not self.armed:
                return ["auto_refused_not_armed"]
            self.mode = "auto"
            return ["auto_on"]
        raise ValueError(f"unknown command {name!r}")

    def _leave_auto(self) -> list[str]:
        if self.mode == "auto":
            self.mode = "manual"
            return ["auto_off"]
        return []

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
        if not self.armed:
            events.extend(self._leave_auto())
        if self.mode == "auto" and fresh and (
                abs(self.input[0]) > AUTO_STEER_OVERRIDE
                or abs(self.input[1]) > AUTO_THROTTLE_OVERRIDE):
            self.mode = "manual"              # pad touched: the human wins this tick
            events.append("auto_override")
        if self.mode == "auto" and fresh:
            m_steer, m_thr = self.autopilot_output or (None, None)
            if m_steer is not None:
                self.last_steer_cmd = max(-100, min(100, int(round(m_steer * 100))))
            steer_cmd = self.last_steer_cmd
            if m_thr is not None and not self.bench:
                # labels are cmd/100 and cmd already includes the cap, so the
                # model output is a raw percent; the cap only bounds it
                cap = self.max_throttle
                thr_cmd = max(-cap, min(cap, int(round(m_thr * 100))))
            else:
                thr_cmd = 0
            return steer_cmd, thr_cmd, self.armed, events
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
                 host: str = "127.0.0.1", autopilot=None) -> None:
        self.autopilot = autopilot            # None = AUTO feature off
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
        self._last_reopen = -1e9              # monotonic time of the last reopen attempt
        self._reopen_lock = threading.Lock()  # held while the port is being reopened
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

        def on_error(exc: BaseException) -> None:
            msg = f"save_failed {exc!r}"
            print(msg)
            with self.lock:
                self.events.append(msg)
        t = self.recorder.stop_background(crash=crash, on_saved=on_saved,
                                          on_error=on_error)
        self._save_threads.append(t)

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
            try:
                self._control_step(frame, t_frame)
            except Exception:                 # keep the loop alive: disarm and say so
                tb = traceback.format_exc()
                print(tb)
                with self.lock:
                    self.controller.armed = False
                    self.controller._leave_auto()
                    self.events.append(
                        "control_error " + tb.strip().splitlines()[-1])
                    if self.recorder.recording:
                        self._stop_recording(crash=False)
                time.sleep(0.5)

    def _control_step(self, frame, t_frame) -> None:
        now = time.monotonic()
        with self.lock:
            want_auto = self.autopilot is not None and self.controller.mode == "auto"
        ap_out = None
        ap_err = None
        if want_auto:                     # inference outside the lock
            try:
                ap_out = self.autopilot.predict(frame)
            except Exception as e:
                ap_err = e
        with self.lock:
            if (ap_out is None and ap_err is None and self.autopilot is not None
                    and self.controller.mode == "auto"):
                try:                      # AUTO engaged since the check above
                    ap_out = self.autopilot.predict(frame)
                except Exception as e:
                    ap_err = e
            if ap_err is not None:        # no model output -> stop safely
                self.controller.armed = False
                self.events.append(f"autopilot_error {ap_err}")
                if self.recorder.recording:
                    self._stop_recording(crash=False)
            self.controller.autopilot_output = ap_out
            link_ok_tick = self.uno.link_ok
            steer, thr, armed, ev = self.controller.tick(
                now, self.last_pack, link_ok_tick)
            mode = self.controller.mode
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
                    "loop_dt": reply.dt if reply else 0,
                    "mode": 1 if mode == "auto" else 0})
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
                "mode": mode,
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
        # Reopen only AFTER a tick has seen the link down (so link_lost has
        # already disarmed), outside the lock, at most once per 2.0 s.
        # Opening the real port resets the Uno (2.2 s + banner), so no
        # exchange happens meanwhile; re-arming needs a new arm command.
        if (not link_ok_tick and not self._stop.is_set()
                and time.monotonic() - self._last_reopen >= REOPEN_INTERVAL_S):
            with self._reopen_lock:
                try:
                    ok = bool(self.uno.reopen())
                except Exception:
                    ok = False
            self._last_reopen = time.monotonic()
            with self.lock:
                self.events.append("reconnect_ok" if ok else "reconnect_failed")

    # ---- commands ----
    def handle_command(self, name: str) -> None:
        with self.lock:
            if name == "auto_toggle" and self.autopilot is None:
                self.events.append("auto_unavailable")
                return
            events = self.controller.command(name, self.last_pack, self.uno.link_ok)
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
            # browsers send Origin; None keeps non-browser clients (self-check) working
            origins = [None, f"http://localhost:{self.http_port}",
                       f"http://127.0.0.1:{self.http_port}"]
            server = await websockets.serve(self._handler, self.host, self.ws_port,
                                            origins=origins)
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
        if self._reopen_lock.acquire(timeout=5.0):   # let a reopen in progress finish
            self._reopen_lock.release()
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


def _check_auto(ctl) -> None:
    ok = protocol.PACK_OK

    def armed_auto(**kw) -> Controller:
        c = ctl(max_throttle=30, **kw)
        c.set_input(0.0, 0.0, 0.0)
        pack = protocol.PACK_FAULT if kw.get("bench") else ok
        assert c.command("arm", pack) == ["armed"]
        assert c.command("auto_toggle", pack) == ["auto_on"] and c.mode == "auto"
        c.autopilot_output = (0.3, 0.15)
        return c

    c = ctl(max_throttle=30)                  # refused while disarmed
    c.set_input(0.0, 0.0, 0.0)
    assert c.command("auto_toggle", ok) == ["auto_refused_not_armed"]
    assert c.mode == "manual"

    c = armed_auto()                          # engages, uses model output
    assert c.tick(0.05, ok, True)[:3] == (30, 15, True) and c.mode == "auto"
    c.set_input(0.0, 0.0, 0.06)               # steer_invert never touches the model
    assert c.tick(0.07, ok, True)[:2] == (30, 15)
    assert c.command("auto_toggle", ok) == ["auto_off"] and c.mode == "manual"
    c.set_input(0.0, 0.0, 0.08)
    assert c.tick(0.09, ok, True)[:3] == (0, 0, True)   # manual again, pad at rest
    c = armed_auto(steer_invert=True)
    assert c.tick(0.05, ok, True)[0] == 30

    c = armed_auto()                          # pad steer 0.2 overrides
    c.set_input(0.2, 0.0, 0.05)
    s, t, a, ev = c.tick(0.06, ok, True)
    assert c.mode == "manual" and "auto_override" in ev and a
    assert s == round(100 * (0.12 / 0.92)) and t == 0, (s, t)
    c = armed_auto()                          # small steer / throttle noise below limits
    c.set_input(0.1, 0.04, 0.05)
    assert c.tick(0.06, ok, True)[:2] == (30, 15) and c.mode == "auto"
    c.set_input(0.0, 0.2, 0.07)               # pad throttle overrides
    s, t, a, ev = c.tick(0.08, ok, True)
    assert c.mode == "manual" and "auto_override" in ev and t == round(0.2 * 30)

    c = armed_auto()                          # model throttle is a raw percent, cap bounds it
    c.autopilot_output = (0.3, 0.5)
    assert c.tick(0.05, ok, True)[:2] == (30, 30)
    c.autopilot_output = (0.3, -0.9)
    assert c.tick(0.06, ok, True)[:2] == (30, -30)
    c = armed_auto()
    c.max_throttle = 0
    assert c.tick(0.05, ok, True)[:2] == (30, 0)

    c = armed_auto(bench=True)                # bench forces throttle 0
    assert c.tick(0.05, protocol.PACK_FAULT, True)[:3] == (30, 0, True)

    c = armed_auto()                          # deadman in auto: disarm + manual
    s, t, a, ev = c.tick(0.5, ok, True)
    assert (s, t, a) == (0, 0, False), (s, t, a)
    assert c.mode == "manual" and "deadman" in ev and "auto_off" in ev, ev
    c = armed_auto()
    c.tick(0.05, ok, True)
    assert c.command("disarm", ok) == ["disarmed", "auto_off"] and c.mode == "manual"
    c = armed_auto()
    ev = c.tick(0.05, protocol.PACK_CUTOFF, True)[3]
    assert c.mode == "manual" and "auto_off" in ev, ev


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

    _check_auto(ctl)

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


async def _auto_session(ws_port: int) -> tuple[list[dict], dict]:
    """Arm, record, go AUTO, record a second, override with the pad."""
    telems: list[dict] = []
    marks: dict = {}
    async with websockets.connect(f"ws://127.0.0.1:{ws_port}") as ws:
        sending = True
        steer = 0.0                            # pad at rest: no override

        async def reader() -> None:
            async for m in ws:
                if not isinstance(m, bytes):
                    telems.append(json.loads(m))

        async def sender() -> None:
            while sending:
                await ws.send(json.dumps({"type": "input", "steer": steer,
                                          "throttle": 0.0}))
                await asyncio.sleep(0.02)

        async def cmd(name: str) -> None:
            await ws.send(json.dumps({"type": "cmd", "name": name}))

        rtask = asyncio.ensure_future(reader())
        stask = asyncio.ensure_future(sender())
        await asyncio.sleep(0.1)
        await cmd("auto_toggle")               # disarmed: refused
        await asyncio.sleep(0.3)
        marks["refused"] = list(telems[-1]["events"]) if telems else []
        await cmd("arm")
        await cmd("rec_toggle")
        await asyncio.sleep(0.5)               # some manual frames
        await cmd("auto_toggle")
        await asyncio.sleep(1.5)
        marks["auto"] = dict(telems[-1])
        await cmd("rec_toggle")
        await asyncio.sleep(0.5)
        steer = 0.5                            # pad override
        await asyncio.sleep(0.5)
        marks["manual"] = dict(telems[-1])
        sending = False
        await stask
        await asyncio.sleep(0.5)
        rtask.cancel()
    return telems, marks


def _check_auto_end_to_end() -> None:
    import tempfile
    import numpy as np
    from autopilot import StubAutopilot
    from episode_writer import load_episode

    with tempfile.TemporaryDirectory() as td:
        rec = Recorder(td, session="sc", meta={"fake": True})
        ctl = Controller(max_throttle=30, bench=False, steer_invert=False)
        app = TeleopApp(FakeUno(pack=protocol.PACK_OK), FakeCamera(), rec, ctl,
                        _free_port(), _free_port(),
                        Path(__file__).resolve().parent / "web", host="127.0.0.1",
                        autopilot=StubAutopilot(throttle=0.15))
        app.start_background()
        try:
            telems, marks = asyncio.run(_auto_session(app.ws_port))
        finally:
            app.shutdown()
        assert "auto_refused_not_armed" in marks["refused"], marks["refused"]
        a = marks["auto"]
        assert a["mode"] == "auto" and a["steer_cmd"] == 30 and a["thr_cmd"] == 15, a
        m = marks["manual"]
        assert m["mode"] == "manual" and m["steer_cmd"] == 46, m
        assert any("auto_override" in t["events"] for t in telems)
        npzs = list(Path(td).rglob("*.npz"))
        assert len(npzs) == 1, npzs
        ep = load_episode(npzs[0])
        lm = ep["log_mode"]
        assert lm.dtype == np.uint8 and lm[0] == 0 and (lm == 1).sum() >= 10, lm
        assert (lm == 0).sum() >= 5, lm
        assert not (np.diff(lm.astype(int)) < 0).any(), lm   # manual -> auto, once
        assert (ep["log_cmd_next"][lm == 1] == [30, 15]).all()

    app2 = TeleopApp(FakeUno(), FakeCamera(), Recorder("unused"),     # feature off
                     Controller(30, False, False), 0, 0, ".")
    app2.handle_command("auto_toggle")
    assert "auto_unavailable" in app2.events and app2.controller.mode == "manual"


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


def _check_link_robustness() -> None:
    import tempfile

    c = Controller(max_throttle=30, bench=False, steer_invert=False)
    c.set_input(0.0, 0.0, 0.0)
    assert c.command("arm", protocol.PACK_OK, False) == ["arm_refused_link"]
    assert not c.armed
    assert c.command("arm", protocol.PACK_OK, True) == ["armed"]

    web = Path(__file__).resolve().parent / "web"
    with tempfile.TemporaryDirectory() as td:
        uno = FakeUno(pack=protocol.PACK_OK)
        app = TeleopApp(uno, FakeCamera(), Recorder(td, session="lk", meta={}),
                        Controller(30, False, False), _free_port(), _free_port(),
                        web, host="127.0.0.1")
        seen: set[str] = set()
        run = threading.Event()
        run.set()

        def feeder() -> None:              # pad input + event log (deque keeps only 5)
            while run.is_set():
                with app.lock:
                    app.controller.set_input(0.0, 0.0, time.monotonic())
                    seen.update(app.events)
                time.sleep(0.01)

        def wait(cond, what: str, timeout: float = 5.0) -> None:
            end = time.monotonic() + timeout
            while time.monotonic() < end:
                with app.lock:
                    if cond():
                        return
                time.sleep(0.01)
            raise AssertionError(f"timeout waiting for {what}; seen={sorted(seen)}")

        ft = threading.Thread(target=feeder, daemon=True)
        app.start_background()
        ft.start()
        real_stop = Recorder.stop
        try:
            wait(lambda: app.last_pack is not None, "first reply")
            app.handle_command("arm")
            wait(lambda: app.controller.armed, "armed")
            # unplug -> link_lost + disarm -> reopen -> reconnect_ok, still disarmed
            uno.disconnect()
            wait(lambda: "reconnect_ok" in seen, "reconnect_ok")
            assert "link_lost" in seen and not app.controller.armed
            assert uno.link_ok
            app.handle_command("arm")
            wait(lambda: app.controller.armed, "re-armed after reconnect")
            app.handle_command("disarm")

            # reopen keeps failing: arm refused, retries rate-limited to 1 / 2 s
            calls: list[float] = []

            def bad_reopen() -> bool:
                calls.append(time.monotonic())
                return False
            uno.reopen = bad_reopen
            uno.disconnect()
            wait(lambda: "reconnect_failed" in seen, "reconnect_failed")
            time.sleep(0.5)
            assert len(calls) == 1, calls
            app.handle_command("arm")
            assert "arm_refused_link" in app.events and not app.controller.armed
            del uno.reopen
            wait(lambda: uno.connected and uno.link_ok, "reconnect after failure", 4.0)

            # a failing background save is surfaced as an event
            def boom(self, crash=False):
                raise OSError("disk full")
            app.handle_command("arm")
            wait(lambda: app.controller.armed, "armed for save test")
            app.handle_command("rec_toggle")
            time.sleep(0.3)
            Recorder.stop = boom
            app.handle_command("rec_toggle")
            wait(lambda: any(e.startswith("save_failed") for e in seen | set(app.events)),
                 "save_failed")
        finally:
            Recorder.stop = real_stop
            run.clear()
            app.shutdown()
        assert any("disk full" in e for e in seen | set(app.events)), sorted(seen)


def _wait_helpers(app, seen):
    def feeder_loop(run) -> None:
        while run.is_set():
            with app.lock:
                app.controller.set_input(0.0, 0.0, time.monotonic())
                seen.update(app.events)
            time.sleep(0.01)

    def wait(cond, what: str, timeout: float = 5.0) -> None:
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            with app.lock:
                if cond():
                    return
            time.sleep(0.01)
        raise AssertionError(f"timeout waiting for {what}; seen={sorted(seen)}")
    return feeder_loop, wait


def _check_autopilot_nan() -> None:
    import tempfile
    from autopilot import StubAutopilot

    with tempfile.TemporaryDirectory() as td:
        ap = StubAutopilot()
        app = TeleopApp(FakeUno(pack=protocol.PACK_OK), FakeCamera(),
                        Recorder(td, session="nan", meta={}),
                        Controller(30, False, False), _free_port(), _free_port(),
                        Path(__file__).resolve().parent / "web", autopilot=ap)
        seen: set[str] = set()
        run = threading.Event()
        run.set()
        feeder_loop, wait = _wait_helpers(app, seen)
        app.start_background()
        threading.Thread(target=feeder_loop, args=(run,), daemon=True).start()
        try:
            wait(lambda: app.last_pack is not None, "first reply")
            app.handle_command("arm")
            wait(lambda: app.controller.armed, "armed")
            app.handle_command("auto_toggle")
            wait(lambda: app.telem.get("mode") == "auto" and app.telem.get("steer_cmd") == 30,
                 "auto engaged")
            ap.steer = float("nan")           # model goes bad
            wait(lambda: any(e.startswith("autopilot_error") for e in seen),
                 "autopilot_error")
            assert any("non-finite" in e for e in seen), sorted(seen)
            wait(lambda: not app.controller.armed and app.controller.mode == "manual",
                 "disarmed + manual")
            wait(lambda: app.telem["armed"] is False, "telemetry shows disarmed")
            assert app.telem["steer_cmd"] != 100, app.telem
        finally:
            run.clear()
            app.shutdown()


def _check_control_error() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        uno = FakeUno(pack=protocol.PACK_OK)
        app = TeleopApp(uno, FakeCamera(), Recorder(td, session="ce", meta={}),
                        Controller(30, False, False), _free_port(), _free_port(),
                        Path(__file__).resolve().parent / "web")
        seen: set[str] = set()
        run = threading.Event()
        run.set()
        real_exchange = uno.exchange
        boom = threading.Event()

        def flaky(*a, **kw):
            if boom.is_set():
                boom.clear()
                raise RuntimeError("injected exchange failure")
            return real_exchange(*a, **kw)
        uno.exchange = flaky
        feeder_loop, wait = _wait_helpers(app, seen)
        app.start_background()
        threading.Thread(target=feeder_loop, args=(run,), daemon=True).start()
        try:
            wait(lambda: app.last_pack is not None, "first reply")
            app.handle_command("arm")
            wait(lambda: app.controller.armed, "armed")
            boom.set()
            wait(lambda: any(e.startswith("control_error") for e in seen), "control_error")
            assert any("injected exchange failure" in e for e in seen), sorted(seen)
            assert not app.controller.armed
            n0 = app._frame_n
            wait(lambda: app._frame_n > n0 + 3, "loop still running", 5.0)
            assert app._ctl_thread.is_alive()
        finally:
            run.clear()
            app.shutdown()


async def _origin_check(http_port: int, ws_port: int) -> None:
    url = f"ws://127.0.0.1:{ws_port}"
    for origin in (f"http://localhost:{http_port}", f"http://127.0.0.1:{http_port}"):
        async with websockets.connect(url, origin=origin):
            pass
    for origin in ("http://evil.example", f"http://localhost:{http_port + 1}"):
        try:
            async with websockets.connect(url, origin=origin):
                pass
        except (websockets.InvalidStatus, websockets.InvalidStatusCode,
                websockets.InvalidHandshake):
            pass
        else:
            raise AssertionError(f"origin {origin} accepted")


def _check_origin_and_host() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        app = TeleopApp(FakeUno(), FakeCamera(), Recorder(td, session="or", meta={}),
                        Controller(30, False, False), _free_port(), _free_port(),
                        Path(__file__).resolve().parent / "web")
        assert app.host == "127.0.0.1"
        app.start_background()
        try:
            asyncio.run(_origin_check(app.http_port, app.ws_port))
            assert app._http.server_address[0] == "127.0.0.1"
        finally:
            app.shutdown()


def self_check() -> None:
    t0 = time.monotonic()
    _check_controller()
    _check_link_robustness()
    _check_end_to_end()
    _check_auto_end_to_end()
    _check_autopilot_nan()
    _check_control_error()
    _check_origin_and_host()
    assert time.monotonic() - t0 < 40.0
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
    ap.add_argument("--host", default="127.0.0.1",
                    help="bind address for HTTP + websocket (default 127.0.0.1; "
                         "reach it through the SSH tunnel). There is NO login: "
                         "0.0.0.0 lets anyone on the network drive the car.")
    ap.add_argument("--http-port", type=int, default=8000)
    ap.add_argument("--ws-port", type=int, default=8765)
    ap.add_argument("--model", default=None,
                    help="ONNX policy file; enables AUTO mode (Back/View or A key)")
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
            "banner": " | ".join(banner), "protocol": "v0.2", "fake": args.fake,
            "model": args.model or ""}
    rec = Recorder(args.data_dir, meta=meta)
    ctl = Controller(args.max_throttle, args.bench, args.steer_invert)
    autopilot = None
    if args.model:
        from autopilot import Autopilot
        autopilot = Autopilot(args.model)
    elif args.fake:
        from autopilot import StubAutopilot
        autopilot = StubAutopilot()
    app = TeleopApp(uno, cam, rec, ctl, args.http_port, args.ws_port,
                    Path(__file__).resolve().parent / "web", host=args.host,
                    autopilot=autopilot)
    if args.max_throttle > 0 and args.bench:
        print("NOTE: --bench forces throttle 0 (max-throttle ignored).")
    print(f"Data dir: {rec.directory}")
    print(f"HTTP {args.host}:{args.http_port}  WS {args.host}:{args.ws_port}")
    if args.host in ("0.0.0.0", "::", ""):
        print(f"WARNING: --host {args.host!r} exposes an UNAUTHENTICATED drive "
              "endpoint: anyone on the network can drive the car. "
              "Use the SSH tunnel with the default 127.0.0.1 instead.")
    print(f"From the laptop: ssh -L {args.http_port}:localhost:{args.http_port} "
          f"-L {args.ws_port}:localhost:{args.ws_port} ed@ed-pi5.local")
    print(f"then open http://localhost:{args.http_port} (the tunnel's local port "
          f"must equal --http-port: the websocket only accepts that Origin)")
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
