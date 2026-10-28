#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
host=${1:-pi@inky.local}
bash scripts/deploy.sh "$host"
ssh -4 -o BatchMode=yes "$host" '
    sudo -n install -m 644 /home/pi/inky/scripts/inky-gallery.service /etc/systemd/system/inky-gallery.service &&
    sudo -n systemctl daemon-reload &&
    sudo -n systemctl enable inky-gallery.service &&
    sudo -n systemctl restart inky-gallery.service
'
