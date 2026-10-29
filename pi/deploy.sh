#!/usr/bin/env bash
# Copy the Pi-side code from the PC to the car's Pi. Run from the repo root.
#
#   bash pi/deploy.sh [--dry-run] [user@host]     (default ed@ed-pi5.local)
#
# --dry-run only echoes the commands. Nothing is deleted on the Pi: mkdir -p,
# scp (overwrites same-named files) and a venv create-if-missing + pip install.
#
# ml/ files copied: ml/verify_corpus.py imports collect_recovery and
# collect_sim_data (which import sim_conf and episode_writer). gym_donkeycar /
# gymnasium are imported lazily INSIDE functions there, and sim_conf imports
# nothing, so all of them import cleanly on the Pi without gym. sim_conf.py is
# therefore copied too (the spec list did not name it; the imports need it).
# If a future change makes any of these import gym at module level, drop it
# here: the recorder self_check then SKIPs, which is acceptable.
set -euo pipefail

DRY=0
HOST="ed@ed-pi5.local"
for a in "$@"; do
    case "$a" in
        --dry-run) DRY=1 ;;
        *) HOST="$a" ;;
    esac
done

run() {
    if [ "$DRY" -eq 1 ]; then
        echo "+ $*"
    else
        echo "+ $*"
        "$@"
    fi
}

run ssh "$HOST" 'mkdir -p ~/car/pi ~/car/ml ~/car/firmware'
run scp -r pi/*.py pi/web pi/requirements*.txt "$HOST:~/car/pi/"
run scp ml/episode_writer.py ml/verify_corpus.py ml/collect_sim_data.py \
    ml/collect_recovery.py ml/sim_conf.py "$HOST:~/car/ml/"
run scp firmware/host_test.py "$HOST:~/car/firmware/"
run ssh "$HOST" '[ -d ~/car/venv ] || python3 -m venv --system-site-packages ~/car/venv; ~/car/venv/bin/pip install -r ~/car/pi/requirements.txt'

if [ "$DRY" -eq 1 ]; then echo; echo "DRY RUN: nothing was copied or run."; fi
cat <<EOF

Target $HOST:~/car. Next, on the Pi:
  ssh $HOST
  ~/car/venv/bin/python ~/car/pi/preflight.py
  ~/car/venv/bin/python ~/car/pi/teleop.py --bench
EOF
