"""Motor sweep on the stand: fixed throttle steps both ways, encoder ticks/s for each.

WHY: hand-driven pad tests on 2026-11-01 (records NE, NF) gave a different story
every run - forward dead, reverse half, both fast after the car was moved. This
takes the human and the pad out: the same throttle steps, in the same order,
repeated, with the speed measured by the encoder instead of by eye. A repeat that
disagrees with itself points at a loose contact or drag; a direction that never
moves at any level points at the drive path for that direction.

It cannot tell an electrical fault from a mechanical one on its own: zero ticks
means "the output shaft did not turn", for either reason. The verdict says which
meter reading separates them.

Car ON A STAND, wheels free. teleop.py must be stopped (the port is exclusive).

    ~/car/venv/bin/python ~/car/pi/motor_sweep.py                  (auto port, levels 20 40 60 80)
    ~/car/venv/bin/python ~/car/pi/motor_sweep.py --levels 30 60 --repeats 3
    ./.venv/Scripts/python.exe pi/motor_sweep.py --self-check
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import argparse
import json
import statistics
import time

import protocol
from uno_link import UnoLink, find_port

RATE_HZ = 20                 # the protocol's command rate
SETTLE_S = 0.4               # skip spin-up before measuring a step
MOVING_TPS = 20.0            # |ticks/s| above this = the shaft turned (358 counts/rev -> ~3 rpm)
ASYM_RATIO = 0.7             # slower/faster direction below this at the same level = asymmetric
SPREAD = 0.3                 # (max-min)/max across repeats above this = unstable
BAD_PACK = (protocol.PACK_CUTOFF, protocol.PACK_FAULT)


class Abort(Exception):
    pass


def hold(link, throttle: int, seconds: float, clock, sleep) -> tuple[list, dict]:
    """Stream (steer 0, throttle) armed at RATE_HZ for `seconds`. Returns the
    (t, ticks) samples and flag counts. Raises Abort on a lost link or a bad pack."""
    samples, flags = [], {"missed": 0, "watchdog": 0, "crc_bad": 0}
    t0 = clock()
    while clock() - t0 < seconds:
        r = link.exchange(0, throttle, True)
        if r is None:
            flags["missed"] += 1
            if not link.link_ok:
                raise Abort("link lost (3 missed replies)")
        else:
            flags["watchdog"] += int(r.watchdog)
            flags["crc_bad"] += int(r.crc_bad)
            pack = (r.status >> 4) & 0x03
            if pack in BAD_PACK:
                raise Abort(f"pack {protocol.PACK_NAMES[pack]} - the Uno inhibits the motor")
            samples.append((clock() - t0, r.ticks))
        sleep(1.0 / RATE_HZ)
    return samples, flags


def rate(samples: list) -> float | None:
    """ticks/s over the part of a hold after SETTLE_S."""
    s = [p for p in samples if p[0] >= SETTLE_S]
    if len(s) < 2 or s[-1][0] <= s[0][0]:
        return None
    return (s[-1][1] - s[0][1]) / (s[-1][0] - s[0][0])


def sweep(link, levels: list[int], repeats: int, hold_s: float, rest_s: float,
          clock=time.monotonic, sleep=time.sleep, log=print) -> dict:
    """Interleaved steps (+L, rest, -L, rest) for each level, `repeats` times.
    Every rest is armed throttle 0 = the firmware's short brake."""
    runs = []                          # {"thr", "rep", "tps", flags...}
    rest_drift = []                    # ticks/s while braked: the shaft should be still
    for rep in range(repeats):
        for lvl in levels:
            for thr in (lvl, -lvl):
                samples, flags = hold(link, thr, hold_s, clock, sleep)
                tps = rate(samples)
                runs.append({"thr": thr, "rep": rep, "tps": tps, **flags})
                log(f"  rep {rep + 1}  thr {thr:+4d}  ticks/s {'-' if tps is None else f'{tps:+8.1f}'}"
                    f"  missed {flags['missed']} wd {flags['watchdog']} crc {flags['crc_bad']}")
                rs, _ = hold(link, 0, rest_s, clock, sleep)
                d = rate(rs)
                if d is not None:
                    rest_drift.append(d)
    return {"levels": levels, "repeats": repeats, "hold_s": hold_s, "rest_s": rest_s,
            "runs": runs, "rest_drift_tps": rest_drift}


def verdict(res: dict) -> list[str]:
    """Plain findings from the sweep numbers. Each fault names the next measurement."""
    out, notes = [], []                # faults; notes (start levels) do not count as faults
    by = {}
    for r in res["runs"]:
        if r["tps"] is not None:
            by.setdefault(r["thr"], []).append(r["tps"])
    med = {t: statistics.median(v) for t, v in by.items()}
    fwd_moves = [l for l in res["levels"] if abs(med.get(l, 0)) > MOVING_TPS]
    rev_moves = [l for l in res["levels"] if abs(med.get(-l, 0)) > MOVING_TPS]

    if not fwd_moves and not rev_moves:
        out.append("NO MOTION either way at any level. Shaft never turned, or the encoder never counted. "
                   "Look: did the wheels turn? Yes -> encoder (D2/D3, +5V2 on J1 P3/6). "
                   "No -> meter J1 M1-M2 (P3/3-P3/4) at full throttle.")
        return out
    for name, moves, other, sign in (("FORWARD", fwd_moves, rev_moves, 1), ("REVERSE", rev_moves, fwd_moves, -1)):
        if not moves and other:
            out.append(f"{name} DEAD: no motion at any level while the other way moves "
                       f"(from {min(other)} %). Meter J1 M1-M2 while holding {name.lower()}: "
                       f"~0 V -> the {name.lower()} drive path (TB6612 inputs U2/2, U2/3, U2/5, U2/6); "
                       f"several volts -> mechanical (the drivetrain blocks this way).")
        elif moves:
            notes.append(f"{name} starts moving at {min(moves)} %.")
    for l in res["levels"]:
        f, r = med.get(l), med.get(-l)
        if f is None or r is None or max(abs(f), abs(r)) <= MOVING_TPS:
            continue
        ratio = min(abs(f), abs(r)) / max(abs(f), abs(r))
        if ratio < ASYM_RATIO:
            slow = "forward" if abs(f) < abs(r) else "reverse"
            out.append(f"ASYMMETRIC at {l} %: forward {f:+.0f}, reverse {r:+.0f} ticks/s "
                       f"({slow} {ratio:.0%} of the other). Same throttle should give the same speed. "
                       f"Meter M1-M2 both ways: equal volts -> drag in the drivetrain; "
                       f"lower volts {slow} -> one TB6612 channel is fighting or off.")
        if f * r > 0:
            out.append(f"SAME SIGN at {l} %: forward and reverse both count {'+' if f > 0 else '-'}. "
                       f"The shaft cannot turn the same way for opposite commands: check the motor really "
                       f"reverses by eye; if it does, the encoder channels are miswired.")
    for t, v in sorted(by.items()):
        hi = max(abs(x) for x in v)
        if len(v) > 1 and hi > MOVING_TPS and (hi - min(abs(x) for x in v)) / hi > SPREAD:
            out.append(f"UNSTABLE at {t:+d} %: repeats gave {', '.join(f'{x:+.0f}' for x in v)} ticks/s. "
                       f"The same command gave different speeds: a loose contact (Uno sockets, J1 housing, "
                       f"carrier pins) or something rubbing. Wiggle-test while it runs.")
    if res["rest_drift_tps"] and max(abs(d) for d in res["rest_drift_tps"]) > MOVING_TPS:
        out.append(f"COASTS WHILE BRAKED: up to {max(abs(d) for d in res['rest_drift_tps']):.0f} ticks/s "
                   f"after the {res['rest_s']} s rest began - the short brake may not be applied.")
    flags = {k: sum(r[k] for r in res["runs"]) for k in ("missed", "watchdog", "crc_bad")}
    if any(flags.values()):
        out.append(f"LINK: {flags} over the sweep - serial trouble can also stall the motor (watchdog brakes it).")
    if not out:
        out.append("No fault pattern found: both ways move, similar speed, repeats agree.")
    return out + notes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", default=None, help="serial device (default: auto, as teleop.py)")
    ap.add_argument("--levels", type=int, nargs="+", default=[20, 40, 60, 80])
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--hold", type=float, default=1.5, help="seconds per step")
    ap.add_argument("--rest", type=float, default=0.8, help="seconds braked between steps")
    ap.add_argument("--out", default=None, help="JSON result path (default ~/car_data/motor_sweep_<time>.json)")
    ap.add_argument("--steady", type=int, default=None, metavar="THR",
                    help="instead of the sweep: hold this one throttle (-100..100) for --seconds, "
                         "printing ticks/s each second - time to put a meter on the pins")
    ap.add_argument("--seconds", type=float, default=8.0)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)
    if args.self_check:
        self_check()
        print("motor_sweep self_check: PASS")
        return 0
    if any(not 0 < l <= 100 for l in args.levels):
        ap.error("levels must be 1..100")
    if args.steady is not None and not (-100 <= args.steady <= 100 and 0 < args.seconds <= 30):
        ap.error("--steady must be -100..100 and --seconds 0..30")

    port = args.port or find_port()
    if port is None:
        print("no /dev/ttyACM* or /dev/ttyUSB* device")
        return 2
    print(f"port {port} (opening resets the Uno)")
    print("CAR ON A STAND, wheels free. Ctrl+C stops (the Uno brakes within 150 ms).")
    link = UnoLink(port)
    banner = link.open()
    print("banner: " + " | ".join(banner))
    try:
        if args.steady is not None:
            print(f"holding throttle {args.steady:+d} for {args.seconds:.0f} s")
            for k in range(int(args.seconds)):
                samples, flags = hold(link, args.steady, 1.0, time.monotonic, time.sleep)
                d = samples[-1][1] - samples[0][1] if len(samples) > 1 else 0
                print(f"  t {k + 1:2d} s  ticks {samples[-1][1] if samples else '-'}  +{d} in the last second"
                      f"  wd {flags['watchdog']} missed {flags['missed']}")
            return 0
        res = sweep(link, args.levels, args.repeats, args.hold, args.rest)
    except Abort as e:
        print(f"ABORTED: {e}")
        return 1
    except KeyboardInterrupt:
        print("stopped by Ctrl+C")
        return 1
    finally:
        for _ in range(5):                 # explicit disarmed zero frames, then let go
            link.exchange(0, 0, False)
            time.sleep(1.0 / RATE_HZ)
        link.close()
    res["banner"] = banner
    res["time"] = time.strftime("%Y-%m-%d %H:%M:%S %z")
    res["findings"] = verdict(res)
    print("\nfindings:")
    for f in res["findings"]:
        print("  - " + f)
    out = Path(args.out or f"~/car_data/motor_sweep_{time.strftime('%Y%m%d-%H%M%S')}.json").expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\nwrote {out}")
    return 0


class _ModelUno:
    """Fake link with a per-direction speed model, on a fake clock. Sim-only."""

    def __init__(self, gain_fwd: float, gain_rev: float, clock, factor=None) -> None:
        self.gain = {1: gain_fwd, -1: gain_rev}
        self.clock = clock
        self.factor = factor or (lambda now: 1.0)   # speed multiplier as a function of time
        self.ticks = 0.0
        self.last = None
        self.seq = 0
        self.link_ok = True

    def exchange(self, steer: int, throttle: int, armed: bool):
        now = self.clock()
        if self.last is not None and armed and throttle:
            self.ticks += self.gain[1 if throttle > 0 else -1] * throttle * (now - self.last) * self.factor(now)
        self.last = now
        self.seq = (self.seq + 1) & 0xFF
        return protocol.Reply(self.seq, int(self.ticks), protocol.ST_ARMED if armed else 0, 12)


def self_check() -> None:
    t = [0.0]
    clock = lambda: t[0]
    def sleep(s):
        t[0] += s
    quiet = lambda *a, **k: None

    def run(gf, gr, factor=None):
        t[0] = 0.0
        link = _ModelUno(gf, gr, clock, factor)
        res = sweep(link, [20, 60], 2, 1.5, 0.5, clock=clock, sleep=sleep, log=quiet)
        return res, verdict(res)

    # healthy: equal and opposite -> no fault, both start at 20
    res, v = run(10.0, 10.0)
    assert any(x.startswith("No fault") for x in v), v
    r60 = [r["tps"] for r in res["runs"] if r["thr"] == 60]
    assert all(abs(x - 600) < 30 for x in r60), r60          # 10 ticks/s per % x 60 %
    # forward dead (today's symptom) -> FORWARD DEAD, names the meter check
    _, v = run(0.0, 10.0)
    assert any(x.startswith("FORWARD DEAD") and "M1-M2" in x for x in v), v
    # reverse at half speed -> ASYMMETRIC, reverse named slow
    _, v = run(10.0, 5.0)
    assert any(x.startswith("ASYMMETRIC") and "reverse 50%" in x for x in v), v
    # encoder counting the same way both directions -> SAME SIGN
    _, v = run(10.0, -10.0)
    assert any(x.startswith("SAME SIGN") for x in v), v
    # repeat 1 full speed, repeat 2 at 20 % (a contact that came loose) -> UNSTABLE.
    # One repeat = 2 levels x 2 directions x (1.5 hold + 0.5 rest) = 8 s of fake time.
    _, v = run(10.0, 10.0, factor=lambda now: 1.0 if now < 8.0 else 0.2)
    assert any(x.startswith("UNSTABLE") for x in v), v
    # nothing moves -> NO MOTION
    _, v = run(0.0, 0.0)
    assert v[0].startswith("NO MOTION"), v
    # a CUTOFF pack aborts instead of driving
    class _Cut(_ModelUno):
        def exchange(self, s, th, a):
            r = super().exchange(s, th, a)
            return protocol.Reply(r.seq, r.ticks, r.status | (protocol.PACK_CUTOFF << 4), 12)
    try:
        sweep(_Cut(10, 10, clock), [20], 1, 1.0, 0.5, clock=clock, sleep=sleep, log=quiet)
        raise AssertionError("CUTOFF pack did not abort")
    except Abort:
        pass


if __name__ == "__main__":
    sys.exit(main())
