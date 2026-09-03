"""Host-side exerciser for firmware/uno_control — the Pi side of SERIAL_PROTOCOL.md.

Runs the protocol against a real Uno and asserts on the replies. Exits non-zero
on any failure, so it is a GATE, not a demo (testing.md's rule).

    .venv/Scripts/python.exe firmware/host_test.py --port COM3

WHAT IT CANNOT TELL YOU. Nothing is wired to the board: no motor, servo,
encoder, LED or pack exists. This verifies the LINK and the STATE MACHINE only.
Every actuator assertion here is about what the firmware DECIDED, never about
anything physically moving.

Opening the port RESETS the board (gotchas), which is how the boot banner and
the firmware's own SELFTEST are captured.
"""
from __future__ import annotations

import argparse
import sys
import time

import serial

SYNC_CMD, SYNC_RPL = 0xA5, 0x5A
CMD_LEN, RPL_LEN = 7, 9
ST_ARMED, ST_WATCHDOG, ST_CRC_BAD, ST_DROPPED = 0x01, 0x02, 0x04, 0x08
PACK_NAMES = {0: "OK", 1: "WARN", 2: "CUTOFF", 3: "FAULT"}

_fail: list[str] = []


def check(cond: bool, desc: str) -> None:
    print(("  ok   " if cond else "  FAIL ") + desc)
    if not cond:
        _fail.append(desc)


def crc8(data: bytes) -> int:
    """CRC-8/ATM, poly 0x07, init 0 — must match the firmware's crc8()."""
    c = 0
    for b in data:
        c ^= b
        for _ in range(8):
            c = ((c << 1) ^ 0x07) & 0xFF if c & 0x80 else (c << 1) & 0xFF
    return c


def command(seq: int, steer: int, throttle: int, lights: int, armed: bool) -> bytes:
    body = bytes([SYNC_CMD, seq & 0xFF, steer & 0xFF, throttle & 0xFF,
                  lights & 0xFF, 0x01 if armed else 0x00])
    return body + bytes([crc8(body)])


def read_reply(ser: serial.Serial, timeout: float = 0.5):
    """Resynchronise on SYNC_RPL, then read a whole frame. Returns None on timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        b = ser.read(1)
        if not b:
            continue
        if b[0] != SYNC_RPL:
            continue
        rest = ser.read(RPL_LEN - 1)
        if len(rest) != RPL_LEN - 1:
            return None
        f = b + rest
        if crc8(f) != 0:
            return None
        ticks = int.from_bytes(f[2:6], "little", signed=True)
        return {"seq": f[1], "ticks": ticks, "status": f[6], "dt": f[7]}
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM3")
    ap.add_argument("--baud", type=int, default=115200)
    args = ap.parse_args()

    print(f"opening {args.port} at {args.baud} (this RESETS the board)")
    ser = serial.Serial(args.port, args.baud, timeout=0.2)
    time.sleep(2.2)                      # bootloader + setup()

    print("\n-- boot output (firmware's own SELFTEST) --")
    banner, deadline = [], time.time() + 3.0
    while time.time() < deadline:
        ln = ser.readline().decode("ascii", "replace").strip()
        if ln:
            print("   " + ln)
            banner.append(ln)
            if ln.startswith("SELFTEST"):
                break
    st = [l for l in banner if l.startswith("SELFTEST")]

    print("\n-- assertions --")
    check(any("UNO CONTROL" in l for l in banner), "board booted uno_control")
    check(bool(st) and "PASS" in st[0], f"firmware SELFTEST passed ({st[0] if st else 'no output'})")

    ser.reset_input_buffer()

    # 1. a valid armed frame gets a well-formed reply with the seq echoed
    ser.write(command(1, 0, 0, 0, armed=True))
    r = read_reply(ser)
    check(r is not None, "valid frame -> a CRC-valid 9-byte reply")
    if r:
        check(r["seq"] == 1, f"seq echoed (got {r['seq']})")
        check(bool(r["status"] & ST_ARMED), "ARMED bit reflected in status")
        pack = (r["status"] >> 4) & 0x03
        print(f"       pack={PACK_NAMES[pack]} ticks={r['ticks']} dt={r['dt']} "
              f"status=0x{r['status']:02X}")
        # A0 is floating: the guard MUST call that a fault, not a healthy pack.
        check(pack == 3, "floating pack sense reads FAULT, not a healthy pack")

    # 2. seq increments cleanly across a short stream
    ok = True
    wd_mid = []                          # ST_WATCHDOG on each mid-stream reply
    for s in range(2, 8):
        ser.write(command(s, 20, 30, 0x01, armed=True))
        rr = read_reply(ser)
        if rr is None or rr["seq"] != s:
            ok = False
            break
        if s >= 4:
            wd_mid.append(bool(rr["status"] & ST_WATCHDOG))
        time.sleep(0.05)                 # the protocol's 20 Hz
    check(ok, "20 Hz stream: every frame answered with a matching seq")
    # Appendix BY (scheduled daily-audit, 2026-09-02) found the watchdog tripping
    # on EVERY good frame: loop() sampled millis() before ~2 ms of analogRead,
    # handleFrame() stamped lastFrameMs from a LATER sample, and the unsigned
    # subtraction wrapped past 150 ms. The stream check above read seq only and
    # could not see it -- and the bit was visible in this script's own printed
    # status (0x33) all along. Frames 4-7 give the boot-state bit two frames to
    # clear; on the buggy firmware every one of them is set.
    check(bool(wd_mid) and not any(wd_mid),
          f"20 Hz stream: WATCHDOG stays CLEAR on healthy frames (got {wd_mid})")
    # ^ That check PASSES on the buggy firmware (verified on the board
    # 2026-09-02) and is therefore not the observable for the BY defect. The
    # reply is sent from INSIDE handleFrame, BEFORE the same iteration's
    # watchdog block runs, and the previous iteration already cleared the bit,
    # so a false trip can never reach a status byte. What it DOES do is clear
    # `armed` ~2 ms after every good frame, and nothing re-arms until the next
    # frame 50 ms later: drive ~2 ms, brake ~48 ms, repeat. So probe `armed`
    # well inside the 150 ms window after an ARMED frame.
    ser.write(command(8, 0, 0, 0, armed=True))
    read_reply(ser)
    time.sleep(0.02)                     # 20 ms: << WATCHDOG_MS, >> one loop
    ser.reset_input_buffer()
    ser.write(b"?")
    time.sleep(0.15)
    probe = ser.read(300).decode("ascii", "replace").strip().split("\r\n")[0]
    check("armed=1" in probe,
          "armed stays 1 inside the watchdog window after an ARMED frame "
          f"(a false trip clears it) -- got: {probe[:70]}")

    # 3. a corrupted frame must be REJECTED, not acted on
    bad = bytearray(command(8, 0, 0, 0, armed=True))
    bad[3] ^= 0xFF                       # flip throttle, leave the CRC stale
    ser.write(bytes(bad))
    r = read_reply(ser)
    check(r is not None and bool(r["status"] & ST_CRC_BAD),
          "bad CRC sets the CRC_BAD status bit")

    # 4. the watchdog trips when the stream stops
    ser.reset_input_buffer()
    time.sleep(0.4)                      # > WATCHDOG_MS (150)
    ser.write(command(9, 0, 0, 0, armed=True))
    r = read_reply(ser)
    check(r is not None and bool(r["status"] & ST_WATCHDOG),
          "silence past 150 ms sets the WATCHDOG status bit")

    # 5. the ASCII escape hatch still works and is not mistaken for a frame
    ser.reset_input_buffer()
    ser.write(b"?")
    time.sleep(0.3)
    line = ser.read(300).decode("ascii", "replace")
    check("everArmed=" in line, "'?' prints a human-readable status line")
    check("stby=0" in line,
          "STBY still LOW: no pack sensor means the driver is never enabled")
    print("       " + line.strip().replace("\r\n", " | ")[:160])

    ser.close()
    print(f"\nhost_test: {'FAIL' if _fail else 'PASS'} "
          f"({len(_fail)} failed)")
    for f in _fail:
        print("  - " + f)
    return 1 if _fail else 0


if __name__ == "__main__":
    sys.exit(main())
