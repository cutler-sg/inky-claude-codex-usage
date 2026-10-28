#!/bin/sh
# Run as root on Raspberry Pi OS. Does not reboot automatically.
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo 'Run: sudo sh /home/pi/inky/scripts/bootstrap-system.sh' >&2
    exit 1
fi

config=/boot/firmware/config.txt
if [ ! -f "$config.inky-backup" ]; then
    cp -p "$config" "$config.inky-backup"
fi
raspi-config nonint do_i2c 0
raspi-config nonint do_spi 0
if ! grep -qxF 'dtoverlay=spi0-0cs' "$config"; then
    printf '\n[all]\n# Inky uses GPIO8 as software chip select.\ndtoverlay=spi0-0cs\n' >> "$config"
fi
echo 'Inky interfaces configured. Reboot with: sudo reboot'
