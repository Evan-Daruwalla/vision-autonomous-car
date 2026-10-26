"""Pi-side byte-level codec for firmware/SERIAL_PROTOCOL.md (no serial import).

WHY a separate pure module: the frame layout is the one thing the Pi and the
Uno must agree on byte for byte, so it lives where it can be tested on a PC
with no board. self_check() pins it against firmware/host_test.py, the
already-verified exerciser, so the two Pi-side encoders cannot drift apart.

The reply parser resyncs one byte at a time after a bad frame: a real sync byte
can hide inside a corrupt frame, and skipping the whole frame would lose it.

    ./.venv/Scripts/python.exe pi/protocol.py --self-check
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import importlib.util
import random
from dataclasses import dataclass

SYNC_CMD, SYNC_RPL = 0xA5, 0x5A
CMD_LEN, RPL_LEN = 7, 9
ST_ARMED, ST_WATCHDOG, ST_CRC_BAD, ST_DROPPED = 0x01, 0x02, 0x04, 0x08
PACK_OK, PACK_WARN, PACK_CUTOFF, PACK_FAULT = 0, 1, 2, 3
PACK_NAMES = {0: "OK", 1: "WARN", 2: "CUTOFF", 3: "FAULT"}


def crc8(data: bytes) -> int:
    """CRC-8, poly 0x07, init 0, no reflection (matches the firmware)."""
    c = 0
    for b in data:
        c ^= b
        for _ in range(8):
            c = ((c << 1) ^ 0x07) & 0xFF if c & 0x80 else (c << 1) & 0xFF
    return c


def _valid_axis(v: object) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and -100 <= v <= 100


def encode_command(seq: int, steer: int, throttle: int, armed: bool,
                   lights: int = 0) -> bytes:
    if not _valid_axis(steer) or not _valid_axis(throttle):
        raise ValueError(f"steer/throttle must be ints in -100..100, got {steer!r}, {throttle!r}")
    body = bytes([SYNC_CMD, seq & 0xFF, steer & 0xFF, throttle & 0xFF,
                  lights & 0xFF, 0x01 if armed else 0x00])
    return body + bytes([crc8(body)])


def encode_reply(seq: int, ticks: int, status: int, dt: int) -> bytes:
    body = (bytes([SYNC_RPL, seq & 0xFF]) + int(ticks).to_bytes(4, "little", signed=True)
            + bytes([status & 0xFF, dt & 0xFF]))
    return body + bytes([crc8(body)])


@dataclass(frozen=True)
class Reply:
    seq: int
    ticks: int
    status: int
    dt: int

    @property
    def armed(self) -> bool:
        return bool(self.status & ST_ARMED)

    @property
    def watchdog(self) -> bool:
        return bool(self.status & ST_WATCHDOG)

    @property
    def crc_bad(self) -> bool:
        return bool(self.status & ST_CRC_BAD)

    @property
    def dropped(self) -> bool:
        return bool(self.status & ST_DROPPED)

    @property
    def pack(self) -> int:
        return (self.status >> 4) & 0x03

    @property
    def pack_name(self) -> str:
        return PACK_NAMES[self.pack]


class ReplyParser:
    """Incremental reply-frame parser; feed() returns the good Replies found."""

    def __init__(self) -> None:
        self._buf = bytearray()
        self.bad_frames = 0

    def feed(self, data: bytes) -> list[Reply]:
        self._buf.extend(data)
        out: list[Reply] = []
        buf = self._buf
        while True:
            i = buf.find(bytes([SYNC_RPL]))
            if i < 0:
                buf.clear()
                break
            if i:
                del buf[:i]
            if len(buf) < RPL_LEN:
                break                      # partial frame: keep for next feed
            frame = bytes(buf[:RPL_LEN])
            if crc8(frame) == 0:
                out.append(Reply(frame[1], int.from_bytes(frame[2:6], "little", signed=True),
                                 frame[6], frame[7]))
                del buf[:RPL_LEN]
            else:
                self.bad_frames += 1
                del buf[:1]                # advance one byte, rescan
        return out


def self_check() -> None:
    assert crc8(b"123456789") == 0xF4

    path = Path(__file__).resolve().parent.parent / "firmware" / "host_test.py"
    spec = importlib.util.spec_from_file_location("host_test", path)
    ht = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ht)
    rng = random.Random(0)
    for _ in range(500):
        data = bytes(rng.randrange(256) for _ in range(rng.randrange(13)))
        assert crc8(data) == ht.crc8(data)
    for _ in range(500):
        seq = rng.randrange(256)
        steer, thr = rng.randint(-100, 100), rng.randint(-100, 100)
        lights, armed = rng.randrange(256), rng.random() < 0.5
        assert encode_command(seq, steer, thr, armed, lights) == \
            ht.command(seq, steer, thr, lights, armed)

    for bad in (101, -101, 3.0, True):
        for args in ((bad, 0), (0, bad)):
            try:
                encode_command(1, args[0], args[1], True)
            except ValueError:
                pass
            else:
                raise AssertionError(f"accepted {bad!r}")

    r1 = encode_reply(1, -123456, 0x31, 12)
    r2 = bytearray(encode_reply(2, 77, 0x01, 12))
    r2[3] ^= 0xFF
    r3 = encode_reply(3, 2**31 - 1, 0x01, 12)
    r4 = encode_reply(4, 5, 0x31, 12)
    stream = b"\x00\x5a\x13" + r1 + bytes(r2) + r3 + r4
    want = [(1, -123456), (3, 2**31 - 1), (4, 5)]

    p = ReplyParser()
    got = p.feed(stream[:-4]) + p.feed(stream[-4:])
    assert [(r.seq, r.ticks) for r in got] == want, got
    assert p.bad_frames >= 1
    p = ReplyParser()
    got = []
    for b in stream:
        got += p.feed(bytes([b]))
    assert [(r.seq, r.ticks) for r in got] == want, got
    assert p.bad_frames >= 1

    r = Reply(1, 0, 0x31, 12)
    assert r.armed is True and r.pack == 3 and r.pack_name == "FAULT"
    assert not r.watchdog and not r.crc_bad and not r.dropped
    print("protocol self_check: PASS")


if __name__ == "__main__":
    self_check()
