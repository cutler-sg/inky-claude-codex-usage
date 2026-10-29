# Hardware and operations

[Back to the project showcase](../README.md)

Detailed setup and operating notes for the Raspberry Pi Zero 2 W and original
600 × 448 seven-colour Inky Impression 5.7, with experimental support for current
Spectra 6 displays. Commands run from the repository
root unless they explicitly change directory. The inventory records the tested
device; it is not a list of minimum storage or OS requirements.

[Hardware](#hardware-inventory) · [Installation](#reproduce-the-setup) · [Gallery and buttons](#live-gallery-and-buttons) · [Usage integration](#bring-your-own-usage-data) · [Troubleshooting](#troubleshooting) · [Development](#development)

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
| Host / user | `inky.local` / `pi`; address assigned by DHCP |
| Access | Existing passwordless SSH; user enabled passwordless sudo during setup (verified with `sudo -n true`) |
| Permissions | `pi` already belongs to `gpio`, `i2c`, `spi`, and `sudo` |
| Time | `Asia/Singapore` (UTC+8), NTP synchronized; no hardware RTC reported |
| Power health | `vcgencmd get_throttled` returned `0x0` at initial inspection |
| Initial interfaces | SPI and I²C disabled; only `/dev/i2c-2` existed |
| Display identity | EEPROM: 600 × 448, `7-Colour (UC8159)`, PCB revision 1.2, written `2021-08-26 09:55:55.2` |
| Configured interfaces | `/dev/i2c-1`, `/dev/spidev0.0`; `dtoverlay=spi0-0cs` active after reboot |

The Pi is compatible with the panel's 40-pin header. Its limited RAM favours one-shot updates and OS-provided binary packages over compiling NumPy/Pillow or running a desktop browser.

## Display details

This is the original **5.7-inch ACeP seven-colour panel**, not a newer Spectra 6 or 7.3-inch model. The vendor driver is `inky.inky_uc8159.Inky`; EEPROM variant **14** maps to **600 × 448**. The project checks the detected identity against its supported profiles before driving GPIO and fails on an absent, unknown, or mismatched EEPROM.

- Palette: black, white, green, blue, red, yellow, orange. Photos are dithered into these colours.
- Reflective E Ink Gallery Palette 4000; no backlight. Readable in sunlight, with a >170° viewing angle.
- Approximate refresh: 30 seconds. Best colour at room temperature.
- Board: 125.4 × 99.5 × 9 mm including display/header; visible area: 114.9 × 85.8 mm; pixel pitch: 0.1915 mm.
- Four side-mounted buttons, used by the [live gallery](#live-gallery-and-buttons).
- Glass panel: handle the PCB edges; do not press the glass or use overlong mounting screws. Power down before changing the header connection.

### Additional display profiles

The [current Inky Impression range](https://shop.pimoroni.com/products/inky-impression)
uses six-colour Spectra 6 panels. These profiles are rendering-tested and their
image conversion is checked against Inky 2.6.0, but they have not been tested on
physical panels in this project. The inventory above describes the original unit.

| Profile | Resolution | EEPROM variant(s) | Driver | Button C |
| --- | --- | --- | --- | --- |
| `impression-5.7` | 600×448 | 14 | UC8159 | GPIO16 |
| `spectra6-4.0` | 600×400 | 25 | E640 | GPIO16 |
| `spectra6-7.3` | 800×480 | 22, 26 (AC) | E673 | GPIO16 |
| `spectra6-13.3` | 1600×1200 | 21, 27 (AC) | EL133UF1 | GPIO25 |

Hardware operations automatically detect the profile from EEPROM and cross-check
the driver/resolution. A resolution alone is insufficient: the older seven-colour
800×480 display is a different driver and is deliberately rejected. Preview flags
cannot force hardware to use a different profile.

The 13.3-inch driver uses GPIO16 and GPIO26 for chip-select signals, so the button
listener uses GPIO25 for C on that board. Do not copy the original GPIO table to
other boards. Driver-specific wiring is handled by the pinned vendor library;
A/B/D remain GPIO5/6/24. Normal vendor refresh mode and the conservative 40-second
minimum between refresh starts are retained for every size.

The renderer preserves the complete composition with proportional scaling and
white margins. Text is rendered from fonts into the scaled artwork surfaces.
The 4.0-/7.3-inch screens have side margins; the 13.3-inch ratio is nearly the
original ratio. Illustrations still originate from 1200×896 plates, so larger
output does not invent additional illustration detail. Unavailable provider
headings use two lines on the new profiles for readability. The original profile
retains the existing pixels and seven-colour conversion.

Spectra image indices are black/white/yellow/red/blue/green (0–5). The driver
remaps these to native codes 0/1/2/3/5/6; the project must not remap them twice.
There is no orange ink on these panels. Digital previews are not calibrated
predictions of physical colour. Photos use the vendor's normal quantization;
live gallery lettering uses the project's deterministic indexed conversion.

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

For independent generated images, invoke `scripts/push.py` or run `.venv/bin/python -m inky_frame show /path/to/image.png` on the Pi. These share the gallery's refresh lock. A one-shot image remains until the next gallery selection, usage update, or freshness transition; stop `inky-gallery.service` if the independent image should remain indefinitely. The gallery service starts on boot to restore button control; it skips an identical prepared frame.

## Live gallery and buttons

All six approved compositions are installed: Pop Comic, Budget Kraken, Reactor Room, Night Market, Quota Moth, and Cosmic Pinball. The [clean plates and exact ImageGen prompts](../assets/live) preserve their original illustrations; `inky_frame/live.py` draws changing values into their balloons, ribbons, tanks, signs, wings and playfield. These live images replace every frozen usage value. Original concept studies remain below as history.

| Button | Action |
| --- | --- |
| A (GPIO 5) | Previous artwork, wrapping at the beginning |
| B (GPIO 6) | Next artwork, wrapping at the end |
| C (GPIO 16) | Another random artwork |
| D (GPIO 24) | Budget Kraken |

A complete panel refresh takes about 34 seconds. Presses settle for 0.8 seconds, and switch bounce is filtered for 200 ms. During a refresh, buttons select what appears next; only the latest selection is kept. Refresh starts are at least 40 seconds apart. Selection survives a service restart or reboot. No slideshow runs automatically.

**Live data:** the built-in Pi collector calls CLIProxyAPI directly over verified
HTTPS. It discovers enabled Claude/Codex accounts through the management API and
requests vendor usage with literal `$TOKEN$` substitution. Vendor OAuth tokens
remain on the proxy; the Pi needs its management credential. Raw provider responses
are reduced to validated usage fields before writing the local snapshot. A failed
provider retains its last successful values and observation time while the other
provider can update normally. No reset credits are redeemed.

The timestamp is the oldest provider observation in the snapshot, in Singapore time. A provider header says `STALE` after a fetch error or 20 minutes without a new observation. After 24 hours, its values become unavailable. Passed reset deadlines say `UPDATE PENDING`; they never imply replenishment. Collection and freshness checks run independently on the Pi; new usage requires the Pi to reach CLIProxyAPI. Scoped limits retain their reported model names; missing windows and credit counts stay missing.

### Configure direct Pi collection

First ensure the Pi can reach your proxy's HTTPS URL. If the proxy is served only
on a Tailscale hostname, install Tailscale on the Pi using its [Linux guide](https://tailscale.com/docs/install/linux)
and authenticate the device. Keep TLS verification enabled.

The configuration file is `/etc/inky/usage.env`, owned by root with mode `0600`,
inside a root-owned mode-`0700` directory. It contains these two variables:

| Variable | Purpose |
| --- | --- |
| `CLI_PROXY_API_BASE_URL` | Your CLIProxyAPI HTTPS base URL |
| `CLI_PROXY_API_MANAGEMENT_KEY` | Your existing proxy management credential |

If the credential is already in macOS Keychain, the helper transfers it over SSH
directly into that protected file. It never prints the credential, puts it in
process arguments, or writes a local copy. On another setup, provision the same
root-owned configuration using your own secret-management process.

```sh
# Reinstall the Pi gallery and boot service
bash scripts/install-gallery.sh

# One-time configuration from the Mac's existing Keychain entry
uv run python scripts/configure-pi-usage.py --proxy-url https://proxy.example.net:9443

# Install the Pi collection service and ten-minute timer; fetch immediately
bash scripts/install-pi-usage.sh

# Fetch again and inspect the timer/logs
ssh -4 pi@inky.local 'sudo systemctl start inky-usage.service'
ssh -4 pi@inky.local 'systemctl list-timers inky-usage.timer --all --no-pager'
ssh -4 pi@inky.local 'journalctl -u inky-usage.service -n 20 --no-pager'

# The same actions used by the physical buttons
ssh -4 pi@inky.local 'cd /home/pi/inky && .venv/bin/python -m inky_frame.gallery select next'
ssh -4 pi@inky.local 'cd /home/pi/inky && .venv/bin/python -m inky_frame.gallery select home'
ssh -4 pi@inky.local 'cd /home/pi/inky && .venv/bin/python -m inky_frame.gallery status'
ssh -4 pi@inky.local 'journalctl -u inky-gallery.service -n 30 --no-pager'
```

Pi collection: `inky-usage.timer` is enabled for boot, triggers after 30 seconds,
and schedules `inky-usage.service` every ten minutes. The one-shot collector runs
as `pi`; systemd reads its protected environment as root. A provider error writes
last-good data with its error state and causes a nonzero service exit; the next
timer run retries. HTTP requests have timeouts and size limits, and authenticated
management requests do not follow redirects.

Pi gallery: `inky-gallery.service`, running as `pi`, enabled for boot. The latest
sanitized data is `state/usage.json`. Selection/runtime status lives in
`state/gallery/`; successful display state is `state/status.json` and
`state/current.png`. Configuration is outside the deployed directory and survives
deployments. Do not put its values in Git or paste them into logs or issues.

Indexed gallery frames pass colour slots 0–6 directly to the UC8159 driver, preserving the proof's palette instead of quantizing it twice. Each refresh runs in a separate child process through the existing hardware lock. The listener owns only the four button pins, so the original one-shot SSH pushes below remain available. Stop the gallery before using a separate persistent GPIO button program.

The first live Budget Kraken refresh completed at **2026-10-28 20:48:44 +08** in **34.18 seconds**, with both provider fetches successful. Software completion does not optically verify the new screen; MC can now inspect it and test physical button presses.

### Bring your own usage data

The renderer only needs the credential-free contract in `inky_frame/usage.py`.
[An empty example](usage-snapshot.example.json) documents the accepted JSON
shape without publishing a live account snapshot. A compatible producer can send
validated JSON over SSH to `.venv/bin/python -m inky_frame.gallery receive` from
`/home/pi/inky`; collection does not have to run on the Pi.

The supplied Mac adapter expects an external Python module with these functions:

- `get_management_key()` returns an in-memory credential or `None`.
- `list_auth_indexes(key)` returns `(provider_indexes, error_or_none)`.
- `fetch_usage(key, indexes, provider, url, headers)` returns `(payload, error_or_none)`.
- `normalize_claude(payload)` and `normalize_codex(payload)` return windows with
  `label`, `percent` (used), and `reset_epoch` fields.
- `CLAUDE_USAGE_URL`, `CODEX_USAGE_URL`, `CLAUDE_HEADERS`, and `CODEX_HEADERS` provide
  the existing collector's request configuration.

The adapter imports functions without calling the external module's `main()`.
Its authentication code and credentials remain outside this repository. A fresh
checkout can prepare images and run tests without this integration or any account.

The external Mac adapter remains an optional alternative to direct Pi collection:

```sh
uv run python scripts/sync-usage.py --collector /absolute/path/to/claude_usage.py
```

Use one scheduled writer. When migrating an existing Mac installation, stop its
old launch job after verifying the Pi collector, so an older Mac snapshot cannot
overwrite newer on-device data:

```sh
launchctl bootout gui/$(id -u)/com.cotdp.inky-usage
launchctl disable gui/$(id -u)/com.cotdp.inky-usage
```

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

## Troubleshooting

- **No route to host:** this Mac resolved `inky.local` to unreachable IPv6 link-local addresses. The scripts force `ssh -4`; IPv4 works.
- **No EEPROM:** check `/dev/i2c-1`, enabled I²C, power, and HAT seating. Do not rewrite the EEPROM. This setup deliberately does not guess another panel model.
- **GPIO8 claimed by SPI:** check `dtoverlay=spi0-0cs` in `/boot/firmware/config.txt` and reboot. The vendor driver manages CS itself.
- **Permission denied on GPIO/SPI/I²C:** verify `id` lists `gpio`, `spi`, `i2c`. Group membership changes require a new login.
- **Another update is running:** wait for it. The `flock` is released when the process exits; the persistent lock file does not mean it is held. Do not delete it to bypass locking.
- **Busy warnings or no visible change:** inspect the physical panel and header connection. Vendor busy timeouts may warn and return; software completion alone is not proof the glass changed.
- **Wrong orientation:** pass `--rotate 180` (or 90/270) rather than changing wiring.
- **Force a recovery refresh:** resend a known image with `--force`. Inspect power with `vcgencmd get_throttled` if refreshes fail.

## Usage display design study

[Open the revised integrated artwork gallery](../designs/integrated-v2/index.html): six full-screen ImageGen compositions with numbers built into the artwork itself—comic balloons, tentacle coils, reactor housings, street signs, moth wings, and pinball inserts. This is the current direction after review of the initial study. Each has a higher-resolution master, an exact 600×448 colour concept, and an indexed seven-colour proof. [Prompts](../designs/integrated-v2/prompts.json) and [implementation notes](../designs/integrated-v2/README.md) are preserved alongside the files.

[Open the comparison gallery](../designs/usage-gallery.html) for six 600×448 screen layouts, each with two original artwork editions. It is self-contained and works directly from disk. Controls compare both editions, seven digital inks versus a muted paper approximation, and fit versus 1:1 pixel viewing.

[Research and refresh proposal](../designs/ANALYSIS.md) records the original collector investigation and remaining/reset/credit/freshness semantics. Its frozen-snapshot studies and proposed deployment are historical; the live gallery above is now installed.

All twelve artwork originals are in `designs/artwork/`; [exact prompts and provenance](../designs/prompts/artwork.json) record built-in ImageGen generation. Fonts are bundled with their OFL licenses. Final screen PNGs are in `designs/mockups/` (600×448, indexed, exactly seven colour slots).

```sh
uv run python designs/render.py
uv run python designs/gallery.py
open designs/usage-gallery.html

# Revised integrated artwork study
uv run python designs/integrated-v2/build.py
open designs/integrated-v2/index.html
```

The design renderer intentionally targets this frozen study snapshot. It is not the live collector or a generalized dashboard renderer. `usage-gallery-preview.html` is a generated, ignored T3 preview with local PNG paths; use the committed self-contained `usage-gallery.html` when sharing or opening independently.

## Preview and validate other sizes without hardware

Run from the repository root; no credentials or connected screen are needed:

```sh
uv run python -m scripts.render_previews
# Include stale, unavailable, missing-data and long-label/boundary fixtures:
uv run python -m scripts.render_previews --all-states
open state/multi-display/previews/index.html

uv run python -m inky_frame sample /tmp/spectra.png --profile spectra6-4.0
uv run python -m inky_frame prepare photo.jpg /tmp/prepared.png --profile spectra6-13.3
```

The preview command generates a gallery, native PNGs, timings, and peak process
memory under ignored `state/multi-display/previews/`. Its synthetic snapshots and
fixed time are in `tests/fixtures/render-snapshots.json`. The ordinary offline
commands default to the original 5.7-inch profile. One-shot image pushes always
prepare for the detected physical panel instead.

For one artwork and a sanitized usage snapshot:

```sh
uv run python -m inky_frame.gallery render 02-budget-kraken snapshot.json /tmp/kraken.png \
  --profile spectra6-7.3 --now 1793221200
```

On a Pi with the pinned vendor dependencies, verify all four drivers' indexed
image conversion **without constructing GPIO/SPI drivers or refreshing**:

```sh
.venv/bin/python -m scripts.check_driver_palettes
```

Legacy regression fixtures compare decoded pixels and palettes for 30 renders.
The committed golden hashes specify their Pillow version; when another Pillow
version is used, compare before/after in that environment separately. This was
also done on the actual Pi's Pillow 11.1.0 before deployment. Successful-frame
hashes now include profile, dimensions, mode, and palette, so the migration causes
one refresh even if the image has not otherwise changed. Selection and snapshots
retain their existing formats.

## Development

```sh
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The Python package is `inky_frame` to avoid shadowing the vendor's `inky` package. Hardware modules are imported only for hardware operations, so image preparation and tests work on macOS. JSON refresh events go to stdout; driver diagnostics go to stderr. Original reference files are preserved in `pimoroni-inky-impression/`. The optional `python-library-inky/` vendor checkout is ignored by git and excluded from project checks; runtime code uses the installed pinned package.

Project code uses the [MIT license](../LICENSE). Bundled fonts keep their OFL licenses;
manufacturer references retain their original rights. See [third-party notices](../THIRD_PARTY.md).
Keep credentials and local account state out of commits; `state/`, environment
files, keys, and generated previews are ignored. Before publication, run
`gitleaks git --redact=100 --log-opts=--all .` to check the full local history.

## References

- [Pimoroni product specification and handling notes](https://shop.pimoroni.com/products/inky-impression-5-7)
- [Pimoroni driver and installation instructions](https://github.com/pimoroni/inky)
- [UC8159 driver at v2.6.0](https://github.com/pimoroni/inky/blob/v2.6.0/inky/inky_uc8159.py)
- [EEPROM-to-driver mapping](https://github.com/pimoroni/inky/blob/v2.6.0/inky/auto.py)
- [Inky 2.6.0 package](https://pypi.org/project/inky/2.6.0/)
- [Raspberry Pi Zero 2 W specification](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
- [GPIO pinout](https://pinout.xyz/pinout/inky_impression); local copies: [HTML](../pimoroni-inky-impression/inky_impression_pinout.html), [PNG](../pimoroni-inky-impression/inky_impression_pinout.png)
- Supplied vendor references: [schematic](../pimoroni-inky-impression/inky_impression_5_7_schematic.pdf), [dimensional drawing](../pimoroni-inky-impression/inky-impression-5.7-drawing.png), and [archived product page](../pimoroni-inky-impression/inky_impression_5_7_product.pdf); product photos are preserved alongside them.
