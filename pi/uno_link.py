"""Pi-side serial link to the Uno, plus a fake Uno for PC testing.

WHY: the Pi control loop needs one object that sends a command frame and gets
the matching reply, and that says honestly when the link is bad (link_ok).
FakeUno has the same interface but no serial port, and builds its replies
through the real encode/ReplyParser byte path, so loop logic can be tested on a
PC. A FakeUno pass is sim-only: it says nothing about a real board.

Opening the port RESETS the Uno (see host_test.py), which is how the boot
banner and the firmware SELFTEST are captured.

    ./.venv/Scripts/python.exe pi/uno_link.py --self-check
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import time

import protocol
from protocol import Reply, ReplyParser


def check_banner(lines: list[str]) -> None:
    st = next((l for l in lines if l.startswith("SELFTEST")), None)
    if not any("UNO CONTROL" in l for l in lines) or st is None or "PASS" not in st:
        raise RuntimeError(f"Uno banner check failed: {lines!r}")


class UnoLink:
    def __init__(self, port: str, baud: int = 115200, reply_timeout: float = 0.03) -> None:
        self.port = port
        self.baud = baud
        self.reply_timeout = reply_timeout
        self.banner: list[str] = []
        self.missed_in_row = 0
        self._seq = 0
        self._ser = None

    def open(self) -> list[str]:
        import serial  # here so the module imports without pyserial
        self._ser = serial.Serial(self.port, self.baud, timeout=0.2)
        time.sleep(2.2)                      # bootloader + setup()
        banner: list[str] = []
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            ln = self._ser.readline().decode("ascii", "replace").strip()
            if ln:
                banner.append(ln)
                if ln.startswith("SELFTEST"):
                    break
        self.banner = banner
        check_banner(banner)
        self._ser.reset_input_buffer()
        self._ser.timeout = 0.005
        return banner

    def exchange(self, steer: int, throttle: int, armed: bool) -> Reply | None:
        self._seq = (self._seq + 1) & 0xFF
        seq = self._seq
        self._ser.write(protocol.encode_command(seq, steer, throttle, armed))
        parser = ReplyParser()
        deadline = time.monotonic() + self.reply_timeout
        while time.monotonic() < deadline:
            n = self._ser.in_waiting
            data = self._ser.read(n if n else 1)
            for r in parser.feed(data):
                if r.seq == seq:
                    self.missed_in_row = 0
                    return r
        self.missed_in_row += 1
        return None

    @property
    def link_ok(self) -> bool:
        return self.missed_in_row < 3

    def close(self) -> None:
        if self._ser is not None:
            self._ser.close()
            self._ser = None


class FakeUno:
    """Same public interface as UnoLink, no serial. Sim-only."""

    def __init__(self, pack: int = protocol.PACK_FAULT, drop: set[int] | None = None) -> None:
        self.pack = pack
        self.drop = drop or set()
        self.banner: list[str] = []
        self.missed_in_row = 0
        self.sent: list[tuple[int, int, bool]] = []
        self._calls = 0
        self._seq = 0
        self._ticks = 0
        self._last: float | None = None

    def open(self) -> list[str]:
        self.banner = ["UNO CONTROL (fake)", "SELFTEST PASS 0/0 (fake)"]
        check_banner(self.banner)
        return self.banner

    def exchange(self, steer: int, throttle: int, armed: bool) -> Reply | None:
        self._calls += 1
        self.sent.append((steer, throttle, armed))
        now = time.monotonic()
        watchdog = self._last is not None and (now - self._last) > 0.150
        self._last = now
        if self._calls in self.drop:
            self.missed_in_row += 1
            return None
        self._seq = (self._seq + 1) & 0xFF
        if armed and throttle > 0:
            self._ticks += 2 * throttle
        status = ((protocol.ST_ARMED if armed else 0)
                  | (protocol.ST_WATCHDOG if watchdog else 0)
                  | (self.pack << 4))
        frame = protocol.encode_reply(self._seq, self._ticks, status, 12)
        (reply,) = ReplyParser().feed(frame)
        self.missed_in_row = 0
        return reply

    @property
    def link_ok(self) -> bool:
        return self.missed_in_row < 3

    def close(self) -> None:
        pass


def self_check() -> None:
    check_banner(["UNO CONTROL v0.2", "SELFTEST PASS 86/86"])
    for bad in ([], ["UNO CONTROL"], ["UNO CONTROL", "SELFTEST FAIL 85/86"]):
        try:
            check_banner(bad)
        except RuntimeError:
            pass
        else:
            raise AssertionError(f"accepted {bad!r}")

    f = FakeUno()
    f.open()
    r1 = f.exchange(0, 50, True)
    r2 = f.exchange(0, 0, True)
    r3 = f.exchange(0, 50, False)
    r4 = f.exchange(0, -50, True)
    r5 = f.exchange(0, 10, True)
    assert [r.seq for r in (r1, r2, r3, r4, r5)] == [1, 2, 3, 4, 5]
    assert [r.armed for r in (r1, r2, r3, r4, r5)] == [True, True, False, True, True]
    assert [r.ticks for r in (r1, r2, r3, r4, r5)] == [100, 100, 100, 100, 120]
    assert f.sent[0] == (0, 50, True)
    assert all(r.pack == protocol.PACK_FAULT for r in (r1, r2, r3, r4, r5))
    assert not r2.watchdog
    time.sleep(0.2)
    assert f.exchange(0, 0, True).watchdog is True
    assert f.exchange(0, 0, True).watchdog is False

    f = FakeUno(pack=protocol.PACK_OK, drop={2, 3, 4})
    assert f.exchange(0, 0, True).pack == protocol.PACK_OK and f.link_ok
    for _ in range(3):
        assert f.exchange(0, 0, True) is None
    assert not f.link_ok
    assert f.exchange(0, 0, True) is not None and f.link_ok

    link = UnoLink("COM_X")
    assert link._ser is None and link.link_ok
    print("uno_link self_check: PASS")


if __name__ == "__main__":
    self_check()
