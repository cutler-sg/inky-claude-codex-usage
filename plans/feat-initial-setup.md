# Inky initial setup

Updated: 2026-10-28. Branch: `feat/initial-setup`.

## Requirements and acceptance criteria

- Document the actual Pi, display, GPIO connections, setup, and operating limits.
- Provide a repeatable command to send an arbitrary image over existing SSH.
- Use the vendor driver and serialize hardware access; no new network service.
- Install on `pi@inky.local`, identify the display, and complete a sample refresh.
- Preserve the supplied reference files and leave a committed, reproducible project.

## Tasks

- [x] Inspect local references, vendor documentation, and the Pi (completed: 2026-10-28).
- [x] Initialize Python project, image preparation, sample, and SSH scripts (completed: 2026-10-28).
- [x] Validate image fitting, transparency, EXIF/explicit rotation, corrupt inputs, lock contention, state on failure, and unchanged-image skipping: 10 tests passed (completed: 2026-10-28).
- [x] Enable SPI/I²C and SPI chip-select overlay; user rebooted, device nodes verified (completed: 2026-10-28).
- [x] Deploy, read EEPROM, refresh sample, and record measured results: PCB 1.2, variant 14, 34.4-second command (completed: 2026-10-28).
- [x] Confirm optical image on physical display: MC confirmed the sample displayed correctly, including with the driver's held-high busy fallback (completed: 2026-10-28).
- [ ] Finish README and commit verified setup.

## Verification

- `uv run pytest`: 10 passed; Ruff lint and formatting passed; shell syntax checks passed.
- Pi `info`: 600×448 UC8159, variant 14, PCB 1.2, EEPROM timestamp 2021-08-26 09:55:55.2.
- Sample: physical display confirmed by MC; command completed in 34.4 seconds.
- Repeated image: `unchanged`, no additional refresh. Pi image preparation also verified at 600×448 RGB.
- No power throttling reported before or after refresh. No daemon or open HTTP port added.
- Global `pip check` exposes pre-existing Debian stub dependency gaps; deployment instead verifies actual driver imports and package versions. No unrelated OS packages changed.
- Formatter briefly included a newly appeared vendor checkout. All 31 changed files were verified against exact formatter output and restored; vendor git status is clean. Project checks now exclude it.

## Decisions

- SSH is the transport and authentication boundary; a one-shot Python command drives the display.
- Keep Pillow/NumPy/GPIO from Raspberry Pi OS in a system-site-packages venv to avoid builds on a 512 MB Pi.
- Force IPv4 for this host: mDNS advertises unreachable link-local IPv6 addresses here.
- Driver selection must match the 600×448 UC8159 panel; EEPROM mismatch fails explicitly.
