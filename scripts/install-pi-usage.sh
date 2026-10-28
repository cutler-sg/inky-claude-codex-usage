#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
host=${1:-pi@inky.local}
bash scripts/deploy.sh "$host"
ssh -4 -o BatchMode=yes "$host" '
    test -d /home/pi/inky/state &&
    sudo -n test -s /etc/inky/usage.env &&
    sudo -n install -m 644 /home/pi/inky/scripts/inky-usage.service /etc/systemd/system/inky-usage.service &&
    sudo -n install -m 644 /home/pi/inky/scripts/inky-usage.timer /etc/systemd/system/inky-usage.timer &&
    sudo -n systemctl daemon-reload &&
    sudo -n systemctl enable --now inky-usage.timer &&
    sudo -n systemctl start inky-usage.service
'
