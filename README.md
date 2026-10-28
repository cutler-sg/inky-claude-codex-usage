# Inky

An SSH-controlled e-ink frame: Raspberry Pi Zero 2 W + discontinued **Pimoroni Inky Impression 5.7-inch, seven-colour, 600 × 448** display.

Images are streamed over the existing SSH connection, fitted with Pillow, quantized by Pimoroni's driver, and sent to the panel. No daemon or HTTP endpoint is needed. E-ink retains the last image without power or a running process.

## Usage display design study

[Open the revised integrated artwork gallery](designs/integrated-v2/index.html): six full-screen ImageGen compositions with numbers built into the artwork itself—comic balloons, tentacle coils, reactor housings, street signs, moth wings, and pinball inserts. This is the current direction after review of the initial study. Each has a higher-resolution master, an exact 600×448 colour concept, and an indexed seven-colour proof. [Prompts](designs/integrated-v2/prompts.json) and [implementation notes](designs/integrated-v2/README.md) are preserved alongside the files.

[Open the comparison gallery](designs/usage-gallery.html) for six 600×448 screen layouts, each with two original artwork editions. It is self-contained and works directly from disk. Controls compare both editions, seven digital inks versus a muted paper approximation, and fit versus 1:1 pixel viewing.

[Research and refresh proposal](designs/ANALYSIS.md) traces the existing Claude/Codex collector, defines remaining/reset/credit/freshness semantics, and proposes a ten-minute collection/render/SSH-push job. The mockups use a clearly dated frozen cache snapshot. No periodic usage job is installed yet; the Pi still shows the verified sample.

All twelve artwork originals are in `designs/artwork/`; [exact prompts and provenance](designs/prompts/artwork.json) record built-in ImageGen generation. Fonts are bundled with their OFL licenses. Final screen PNGs are in `designs/mockups/` (600×448, indexed, exactly seven colour slots).

```sh
uv run python designs/render.py
uv run python designs/gallery.py
open designs/usage-gallery.html

# Revised integrated artwork study
uv run python designs/integrated-v2/build.py
open designs/integrated-v2/index.html
```

The design renderer intentionally targets this frozen study snapshot. It is not the live collector or a generalized dashboard renderer. `usage-gallery-preview.html` is the T3 preview variant that references local PNG paths; use the self-contained `usage-gallery.html` when sharing or opening independently.

## Update the image

From this directory on your Mac:

```sh
uv run python scripts/push.py assets/hello.png
uv run python scripts/push.py /path/to/photo.jpg --fit cover
uv run python scripts/push.py /path/to/photo.png --rotate 180 --saturation 0.7
```

The default `contain` preserves the entire image with white margins; `cover` crops centrally to fill the screen. EXIF orientation is applied, and transparency is composited onto white. Saturation is the vendor's palette adjustment (0–1, default 0.5). Identical prepared images/settings are skipped; add `--force` to refresh again. Concurrent updates fail immediately rather than competing for GPIO.

Expect roughly 30 seconds of flashing during a full refresh. Wait for `refresh_completed`. The driver cannot verify the final optical image: check the physical display after initial setup. Avoid frequent refresh loops; this panel suits occasional artwork/dashboard updates. A successful update stores `state/current.png` (prepared RGB source, not a simulation of the panel's colours) and `state/status.json` on the Pi.

```sh
# Local preparation and preview, without hardware
uv run python -m inky_frame prepare /path/to/photo.jpg /tmp/preview.png --fit cover
uv run python -m inky_frame sample assets/hello.png

# Inspect identity and last successful update
ssh -4 pi@inky.local 'cd /home/pi/inky && .venv/bin/python -m inky_frame info'
ssh -4 pi@inky.local 'cat /home/pi/inky/state/status.json'
```

## Hardware inventory

Observed over SSH on **2026-10-28**, unless marked as a specification:

| Component | Configuration |
| --- | --- |
| Computer | Raspberry Pi Zero 2 W Rev 1.0 (`/proc/device-tree/model`) |
| CPU / RAM (specification) | Broadcom BCM2710A1, quad-core Cortex-A53 at 1 GHz; 512 MB RAM |
| Wireless (specification) | 2.4 GHz 802.11 b/g/n Wi-Fi; Bluetooth 4.2 / BLE |
| OS | Raspberry Pi OS desktop image dated 2026-10-06; Debian 13 Trixie, `/etc/os-release` reported 13.7; aarch64 |
| Kernel | `6.18.50+rpt-rpi-v8` |
| Python | 3.13.5 |
| Storage | User-supplied 64 GB microSD; kernel reports 59.5 GiB; 512 MiB boot partition, ~59 GiB root partition |
| Root filesystem | `df -h`: 58 GiB total, 5.1 GiB used, 51 GiB available at initial inspection |
| Memory | OS exposes ~415 MiB RAM; ~414 MiB zram swap at initial inspection |
| Host / user | `inky.local` / `pi`; IPv4 was `192.168.1.80` (DHCP address can change) |
| Access | Existing passwordless SSH; user enabled passwordless sudo during setup (verified with `sudo -n true`) |
| Permissions | `pi` already belongs to `gpio`, `i2c`, `spi`, and `sudo` |
| Time | `Asia/Singapore` (UTC+8), NTP synchronized; no hardware RTC reported |
| Power health | `vcgencmd get_throttled` returned `0x0` at initial inspection |
| Initial interfaces | SPI and I²C disabled; only `/dev/i2c-2` existed |
| Display identity | EEPROM: 600 × 448, `7-Colour (UC8159)`, PCB revision 1.2, written `2021-08-26 09:55:55.2` |
| Configured interfaces | `/dev/i2c-1`, `/dev/spidev0.0`; `dtoverlay=spi0-0cs` active after reboot |

The Pi is compatible with the panel's 40-pin header. Its limited RAM favours one-shot updates and OS-provided binary packages over compiling NumPy/Pillow or running a desktop browser.

## Display details

This is the original **5.7-inch ACeP seven-colour panel**, not a newer Spectra 6 or 7.3-inch model. The vendor driver is `inky.inky_uc8159.Inky`; EEPROM variant **14** maps to **600 × 448**. The project checks that identity before driving GPIO and fails on an absent or mismatched EEPROM.

- Palette: black, white, green, blue, red, yellow, orange. Photos are dithered into these colours.
- Reflective E Ink Gallery Palette 4000; no backlight. Readable in sunlight, with a >170° viewing angle.
- Approximate refresh: 30 seconds. Best colour at room temperature.
- Board: 125.4 × 99.5 × 9 mm including display/header; visible area: 114.9 × 85.8 mm; pixel pitch: 0.1915 mm.
- Four side-mounted buttons, available for future controls; no button behaviour is installed.
- Glass panel: handle the PCB edges; do not press the glass or use overlong mounting screws. Power down before changing the header connection.

### GPIO wiring

BCM numbers are GPIO identities; physical numbers refer to the 40-pin header. The HAT supplies these connections directly.

| Signal | BCM GPIO | Physical pin |
| --- | --- | --- |
| SPI MOSI | 10 | 19 |
| SPI clock | 11 | 23 |
| Software chip select | 8 | 24 |
| Data / command | 22 | 15 |
| Reset | 27 | 13 |
| Busy | 17 | 11 |
| I²C SDA / SCL (identity EEPROM, address `0x50`) | 2 / 3 | 3 / 5 |
| Button A / B / C / D | 5 / 6 / 16 / 24 | 29 / 31 / 36 / 18 |
| EEPROM write protect (reserved; do not repurpose) | 12 | 32 |
| Power | 3.3 V / 5 V | 1, 17 / 2, 4 |
| Ground | — | 6, 9, 14, 20, 25, 30, 34, 39 |

The SPI bus is used for pixels; I²C identifies the display. MISO (GPIO9/pin21), CE1 (GPIO7/pin26), and other pins are exposed on the board; they are not required by this project's panel driver. The schematic's write-protect connection is why GPIO12 is reserved here. Buttons are normally pulled up and close to ground when pressed.

## Reproduce the setup

The current Pi already has `python3-venv`, `python3-pil`, `python3-numpy`, `python3-spidev`, `python3-libgpiod`, and `i2c-tools`. On a fresh Raspberry Pi OS installation, install them first:

```sh
sudo apt update
sudo apt install -y python3-venv python3-pip python3-pil python3-numpy python3-spidev python3-libgpiod i2c-tools
```

Enable interfaces using the included script (first copy it to the Pi, or deploy below). It preserves the original config as `/boot/firmware/config.txt.inky-backup`, enables I²C/SPI through `raspi-config`, and adds `dtoverlay=spi0-0cs` so the kernel does not claim GPIO8. It does not reboot itself.

```sh
ssh -4 pi@inky.local 'mkdir -p /home/pi/inky/scripts'
scp -4 scripts/bootstrap-system.sh pi@inky.local:/home/pi/inky/scripts/
ssh -4 -t pi@inky.local 'sudo sh /home/pi/inky/scripts/bootstrap-system.sh && sudo reboot'
```

After the Pi returns, deploy without root:

```sh
bash scripts/deploy.sh
ssh -4 pi@inky.local 'cd /home/pi/inky && .venv/bin/python -m inky_frame info'
uv run python scripts/push.py assets/hello.png
```

Deployment installs the project at `/home/pi/inky`, creates a `--system-site-packages` virtual environment, and installs `inky==2.6.0` and `gpiodevice==0.1.0`. It preserves `state/`. Pillow, NumPy, SPI, and libgpiod come from the OS. `uv.lock` locks local development dependencies; the Pi uses `requirements-pi.txt` plus OS packages. Updating the system packages is an independent OS maintenance task.

Verified Pi Python dependencies: Pillow 11.1.0, NumPy 2.2.4, gpiod 2.2.0, spidev 3.6, smbus2 0.4.3. Deployment verifies imports and records installed versions. A global `pip check` on this system also reports unrelated Debian type-stub packages missing optional applications; those are outside the display dependency chain.

The first sample command returned successfully at **2026-10-28 17:29:52 +08**, taking **34.4 seconds**, and **MC confirmed the sample displayed correctly**. The vendor driver reported the busy line held high and used its timed waits, including the full 32-second refresh wait; this fallback worked on this particular unit. Sending the same image again returned `unchanged` without refreshing.

For scheduling or generated dashboards, render a PNG locally and invoke `scripts/push.py` from the generating job. Alternatively, run `.venv/bin/python -m inky_frame show /path/to/image.png` on the Pi. No refresh-on-boot service is necessary: the panel retains its image.

## Troubleshooting

- **No route to host:** this Mac resolved `inky.local` to unreachable IPv6 link-local addresses. The scripts force `ssh -4`; IPv4 works.
- **No EEPROM:** check `/dev/i2c-1`, enabled I²C, power, and HAT seating. Do not rewrite the EEPROM. This setup deliberately does not guess another panel model.
- **GPIO8 claimed by SPI:** check `dtoverlay=spi0-0cs` in `/boot/firmware/config.txt` and reboot. The vendor driver manages CS itself.
- **Permission denied on GPIO/SPI/I²C:** verify `id` lists `gpio`, `spi`, `i2c`. Group membership changes require a new login.
- **Another update is running:** wait for it. The `flock` is released when the process exits; the persistent lock file does not mean it is held. Do not delete it to bypass locking.
- **Busy warnings or no visible change:** inspect the physical panel and header connection. Vendor busy timeouts may warn and return; software completion alone is not proof the glass changed.
- **Wrong orientation:** pass `--rotate 180` (or 90/270) rather than changing wiring.
- **Force a recovery refresh:** resend a known image with `--force`. Inspect power with `vcgencmd get_throttled` if refreshes fail.

## Development

```sh
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The Python package is `inky_frame` to avoid shadowing the vendor's `inky` package. Hardware modules are imported only for `info` / `show`, so image preparation and tests work on macOS. JSON refresh events go to stdout; driver diagnostics go to stderr. Original reference files are preserved in the repository root. The optional `python-library-inky/` vendor checkout is ignored by git and excluded from project checks; runtime code uses the installed pinned package.

## References

- [Pimoroni product specification and handling notes](https://shop.pimoroni.com/products/inky-impression-5-7)
- [Pimoroni driver and installation instructions](https://github.com/pimoroni/inky)
- [UC8159 driver at v2.6.0](https://github.com/pimoroni/inky/blob/v2.6.0/inky/inky_uc8159.py)
- [EEPROM-to-driver mapping](https://github.com/pimoroni/inky/blob/v2.6.0/inky/auto.py)
- [Inky 2.6.0 package](https://pypi.org/project/inky/2.6.0/)
- [Raspberry Pi Zero 2 W specification](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
- [GPIO pinout](https://pinout.xyz/pinout/inky_impression); local copies: [HTML](inky_impression_pinout.html), [PNG](inky_impression_pinout.png)
- Supplied vendor references: [schematic](inky_impression_5_7_schematic.pdf), [dimensional drawing](inky-impression-5.7-drawing.png), and archived product page `inky_impression_5_7_product.pdf`; product photos are preserved alongside them.
