#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
host=${1:-pi@inky.local}
case "$host" in -*) echo 'Invalid SSH host' >&2; exit 1 ;; esac
ssh -4 -o BatchMode=yes -o ConnectTimeout=15 "$host" 'mkdir -p /home/pi/inky'
COPYFILE_DISABLE=1 tar --no-xattrs --exclude=__pycache__ -czf - \
    --exclude='*-master.png' \
    inky_frame scripts assets designs/fonts pyproject.toml requirements-pi.txt README.md uv.lock |
    ssh -4 -o BatchMode=yes "$host" 'cd /home/pi/inky && tar -xzf -'
ssh -4 -o BatchMode=yes "$host" '
    cd /home/pi/inky &&
    python3 -m venv --system-site-packages .venv &&
    .venv/bin/python -m pip install -r requirements-pi.txt &&
    .venv/bin/python -c "from importlib.metadata import version; from inky.inky_uc8159 import Inky; import gpiod, spidev, smbus2, numpy; from PIL import Image; print({name: version(name) for name in [\"inky\", \"gpiodevice\", \"pillow\", \"numpy\", \"gpiod\", \"spidev\", \"smbus2\"]})"
'
