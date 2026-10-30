"""Pre-drive checks, run ON the Pi before teleop: PASS/FAIL per line, exit 1 on any FAIL.

WHY: a missing import, a dead camera or an Uno that fails its SELFTEST is
cheaper to find here than mid-session. --fake swaps the camera and Uno for
FakeCamera/FakeUno and drops the picamera2 and /dev/ttyACM* requirements so the
logic can be tested on a PC; a --fake pass says nothing about the real Pi.

    ~/car/venv/bin/python ~/car/pi/preflight.py [--port /dev/ttyACM0]
    ~/car/venv/bin/python ~/car/pi/preflight.py --no-uno     (Pi off the car)
    ./.venv/Scripts/python.exe pi/preflight.py --fake
    ./.venv/Scripts/python.exe pi/preflight.py --self-check
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import argparse
import contextlib
import glob
import io
import importlib
import shutil

MIN_FREE_GB = 2.0
MIN_PYTHON = (3, 9)


def check_python() -> tuple[str, str]:
    v = sys.version_info
    ok = (v.major, v.minor) >= MIN_PYTHON
    return ("PASS" if ok else "FAIL"), f"{v.major}.{v.minor}.{v.micro} (need >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]})"


def import_check(module: str, required: bool = True, why: str = ""):
    def run() -> tuple[str, str]:
        try:
            m = importlib.import_module(module)
        except Exception as e:
            if required:
                return "FAIL", f"import failed: {e!r}"
            return "WARN", f"import failed ({why}): {e!r}"
        return "PASS", getattr(m, "__version__", "")
    return run


def check_serial_device() -> tuple[str, str]:
    devs = sorted(glob.glob("/dev/ttyACM*"))
    return ("PASS", " ".join(devs)) if devs else ("FAIL", "no /dev/ttyACM* device")


def check_disk() -> tuple[str, str]:
    free = shutil.disk_usage(Path.home()).free / 1e9
    return ("PASS" if free >= MIN_FREE_GB else "FAIL"), f"{free:.1f} GB free under ~ (need >= {MIN_FREE_GB:g})"


def check_camera(fake: bool):
    def run() -> tuple[str, str]:
        from camera import FakeCamera, PiCamera
        cam = FakeCamera() if fake else PiCamera()
        try:
            cam.start()
            frame, _ = cam.read()
        except Exception as e:
            return "FAIL", f"camera failed: {e!r}"
        finally:
            try:
                cam.stop()
            except Exception:
                pass
        if tuple(frame.shape) != (120, 160, 3):
            return "FAIL", f"frame shape {tuple(frame.shape)}, want (120, 160, 3)"
        return "PASS", f"frame {tuple(frame.shape)}"
    return run


def check_uno(fake: bool, port: str):
    def run() -> tuple[str, str]:
        from uno_link import FakeUno, UnoLink
        link = FakeUno() if fake else UnoLink(port)
        try:
            banner = link.open()      # raises unless banner + SELFTEST PASS
        except Exception as e:
            return "FAIL", f"{e!r}"
        finally:
            try:
                link.close()
            except Exception:
                pass
        return "PASS", " | ".join(banner)
    return run


def skip_uno() -> tuple[str, str]:
    return "SKIP", "Uno not attached (--no-uno)"


def build_checks(fake: bool, port: str, no_uno: bool = False) -> list:
    checks = [
        ("python version", check_python),
        ("import numpy", import_check("numpy")),
        ("import serial", import_check("serial")),
        ("import websockets", import_check("websockets")),
        ("import PIL", import_check("PIL")),
        ("import picamera2", import_check("picamera2", required=not fake)),
        ("import onnxruntime", import_check("onnxruntime", required=False,
                                            why="autopilot unavailable")),
    ]
    if not fake:
        checks.append(("serial device", skip_uno if no_uno else check_serial_device))
    checks += [
        ("free disk", check_disk),
        ("camera frame", check_camera(fake)),
        ("uno banner + SELFTEST", skip_uno if no_uno else check_uno(fake, port)),
    ]
    return checks


def run_preflight(fake: bool, port: str = "/dev/ttyACM0", extra: list | None = None,
                  no_uno: bool = False) -> int:
    failed = 0
    for name, fn in build_checks(fake, port, no_uno) + (extra or []):
        try:
            status, detail = fn()
        except Exception as e:                # a check must never crash the run
            status, detail = "FAIL", f"check raised {e!r}"
        if status == "FAIL":
            failed += 1
        print(f"{status:4}  {name}: {detail}")
    print("preflight: " + ("FAIL" if failed else "PASS") + (f" ({failed} failed)" if failed else "")
          + (" (Uno not checked)" if no_uno and not failed else ""))
    return 1 if failed else 0


def self_check() -> None:
    assert run_preflight(fake=True) == 0
    bad = [("fake missing import", import_check("no_such_module_for_preflight_test"))]
    assert run_preflight(fake=True, extra=bad) == 1
    optional = [("fake optional import", import_check("no_such_module_for_preflight_test",
                                                      required=False, why="test"))]
    assert run_preflight(fake=True, extra=optional) == 0     # WARN is not a failure
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert run_preflight(fake=True, no_uno=True) == 0
    assert "SKIP  uno banner + SELFTEST" in buf.getvalue()
    assert "PASS (Uno not checked)" in buf.getvalue()
    print("preflight self_check: PASS")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--fake", action="store_true", help="FakeCamera + FakeUno (PC)")
    ap.add_argument("--no-uno", action="store_true",
                    help="skip the serial device and Uno banner checks (Pi off the car)")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0
    return run_preflight(args.fake, args.port, no_uno=args.no_uno)


if __name__ == "__main__":
    sys.exit(main())
