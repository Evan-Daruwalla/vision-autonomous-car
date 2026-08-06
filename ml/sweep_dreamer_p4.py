"""SIM-POC P4 done-check: where is the real 8 GB boundary on this 3060 Ti?

The PRD asks for "a trained model OR a documented OOM boundary with the
measured number". DreamerV3-S at the repo's default batch fits easily
(2.55 GB), so the useful artifact is not a single pass/fail -- it is the TABLE
saying which configurations fit and which do not, because M4 will train a
world model on the real car's logs on this same card.

**Each configuration runs in a SEPARATE PROCESS.** Building several agents in
one process leaves the caching allocator fragmented and every measurement
after the first is contaminated by the ones before it. Slower, but a memory
measurement taken in a dirty process is not a measurement.

**Every run is capped with `--cap-gb`, and that is not optional.** With Sysmem
Fallback ON (confirmed by ml/probe_vram.py on 2026-08-06) an over-budget config
does not crash -- it spills to host RAM and merely gets slower. Measured
2026-08-06: an uncapped batch-64 run pinned the card at ~7.93 GB / 100% for
over TWENTY MINUTES without finishing 20 steps that batch 32 finished in 71 s,
and had to be killed. A sweep that waits for configs like that to "fail" never
terminates.

The cap turns that hang into an immediate, deterministic OOM. probe_vram.py
verified the allocator cap still raises OutOfMemoryError with fallback active,
so the boundary is real and reproducible in code rather than dependent on a
control-panel setting.

**The cap defaults to 7.0 GB, not 8.0.** The card is never entirely yours --
1.0-2.7 GB was in use by the Windows desktop across measurements on
2026-08-06. A config that only fits when nothing else is running does not fit.

Two numbers come out, and they answer different questions:
  peak_gb  -- how much the config actually needed (only meaningful if it fit)
  OOM      -- it needs more than the cap; the cap IS the reported boundary

Usage:  python ml/sweep_dreamer_p4.py
        python ml/sweep_dreamer_p4.py --cap-gb 7.5 --steps 30
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
RUNS = REPO / "ml" / "runs" / "dreamer_p4"
PY = REPO / ".venv" / "Scripts" / "python.exe"
RUNNER = REPO / "ml" / "run_dreamer_p4.py"

# (label, extra args). Walks two axes off the DreamerV3-S default: batch size,
# then model size. imag_horizon 15 is the paper's default -- the PRD pinned 5
# to be safe, and this measures what that caution actually bought.
CONFIGS = [
    ("S  b16 h5",  ["--size", "S", "--batch-size", "16", "--imag-horizon", "5"]),
    ("S  b32 h5",  ["--size", "S", "--batch-size", "32", "--imag-horizon", "5"]),
    ("S  b64 h5",  ["--size", "S", "--batch-size", "64", "--imag-horizon", "5"]),
    ("S  b16 h15", ["--size", "S", "--batch-size", "16", "--imag-horizon", "15"]),
    ("M  b16 h5",  ["--size", "M", "--batch-size", "16", "--imag-horizon", "5"]),
    ("L  b16 h5",  ["--size", "L", "--batch-size", "16", "--imag-horizon", "5"]),
]

CARD_GB = 8.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--cap-gb", type=float, default=7.0,
                    help="allocator cap per run; the reported OOM boundary")
    ap.add_argument("--dataset-size", type=int, default=20000,
                    help="frames loaded per run; VRAM holds only the batch")
    args = ap.parse_args()

    rows = []
    for label, extra in CONFIGS:
        tag = "sweep_" + label.replace(" ", "")
        print(f"\n=== {label} ===", flush=True)
        cmd = [str(PY), str(RUNNER), "--steps", str(args.steps),
               "--epoch-steps", str(args.steps), "--tag", tag,
               "--cap-gb", str(args.cap_gb),
               "--dataset-size", str(args.dataset_size)] + extra
        proc = subprocess.run(cmd, cwd=str(REPO / "ml"),
                              capture_output=True, text=True)
        result_path = RUNS / tag / "p4_result.json"
        # **Check the EXIT CODE, not just the file.** `p4_result.json` from a
        # previous run is committed to this repo, so "the file exists" is not
        # evidence this run produced it. On a fresh clone with no GPU, no
        # corpus, and no vendored library, the runner exits non-zero writing
        # nothing -- and a file-existence check would then read the committed
        # result and report it as freshly measured. That is a fabricated
        # fitting table presented as a measurement, in the one command the
        # README advertises as "Reproduce with". (Cold audit, 2026-08-06.)
        #
        # The runner catches OOM itself and still writes its json with exit 0,
        # so a non-zero exit always means the config genuinely never ran.
        if proc.returncode != 0 or not result_path.exists():
            why = (f"exit {proc.returncode}" if proc.returncode != 0
                   else "no result written")
            tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
            rows.append(dict(label=label, status="ERROR",
                             note=f"{why}: " + " | ".join(tail)))
            print(f"  ERROR ({why}): {' | '.join(tail)}")
            continue

        r = json.loads(result_path.read_text())
        peak = r["peak_gb"]
        status = f"OOM >{args.cap_gb:.1f}GB" if r["oom_at_step"] else "fits"
        rows.append(dict(label=label, status=status,
                         peak_gb=None if r["oom_at_step"] else peak,
                         params=r["params_total"],
                         # Recorded so a capped row is distinguishable from an
                         # uncapped one; without it the summary cannot say
                         # whether a number is a ceiling or a spill (finding 11).
                         cap_gb=r.get("cap_gb"),
                         seconds=r["history"][-1]["seconds"] if r["history"] else None))
        print(f"  {status}" + ("" if r["oom_at_step"] else f": peak {peak:.3f} GB"))

    print(f"\n{'config':<12} {'params':>12} {'peak GB':>9} {'% of 8GB':>9} "
          f"{'s/{} steps'.format(args.steps):>12}  status")
    for r in rows:
        if r["status"] == "ERROR":
            print(f"{r['label']:<12} {'-':>12} {'-':>9} {'-':>9} {'-':>12}  "
                  f"ERROR {r['note'][:60]}")
            continue
        secs = f"{r['seconds']:.1f}" if r["seconds"] is not None else "-"
        # peak is meaningless for an OOM'd run -- it reports how far it got,
        # not what it needed. Printing it as if it were a requirement would
        # understate the config, so it is left blank.
        peak = f"{r['peak_gb']:.3f}" if r["peak_gb"] is not None else "-"
        pct = (f"{100 * r['peak_gb'] / CARD_GB:.1f}%"
               if r["peak_gb"] is not None else "-")
        print(f"{r['label']:<12} {r['params']:>12,} {peak:>9} "
              f"{pct:>9} {secs:>12}  {r['status']}")

    out = RUNS / "sweep_summary.json"
    out.write_text(json.dumps(rows, indent=2))
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
