# Button-controlled artwork gallery

Branch: `feat/button-gallery`. Updated: 2026-10-28.

## Acceptance criteria

- All six approved integrated designs are installed on the Pi at native resolution with real usage.
- Display the live renderer's indexed frames directly, preserving the seven physical colour indexes.
- A/B select previous/next, C selects another random design, D selects Budget Kraken.
- Debounce presses, serialize refreshes, and coalesce presses during a refresh into the latest selection.
- Persist the selection, start the listener on boot, and leave existing SSH image pushes available.
- Complete a hardware refresh and verify service health, GPIO ownership, and software selection paths.
- Fetch real Claude/Codex usage through the existing trusted collector, with per-provider freshness.
- Replace all frozen numbers with deterministic integrated overlays on clean ImageGen plates.
- Install a ten-minute Mac launch agent; transmit sanitized data only, with no credentials on the Pi.

## Tasks

- [x] Inspect the existing frame code, Pi, driver, and vendor GPIO example.
- [x] Generate six clean plates; implement live collection, integrated rendering, and tests.
- [x] Implement the gallery controller, focused tests, service, and deployment.
- [x] Run checks, install all six plates, and verify actual refreshes and persistence.
- [x] Document controls, operational limits, verification, and commit the changes.

## Design

Use the installed libgpiod v2 API and vendor button pins; no new dependencies.
One small service owns only button GPIO. A child process performs each display update
through the existing hardware lock, releasing the panel pins on exit. Keep at most
one pending selection and a short settling delay after button presses. Persist the
desired selection atomically; write runtime status separately. No automatic slideshow
or new network endpoint. The listener remains responsive during the slow panel refresh.
The user confirmed unattended operation and expanded scope to real usage. Reuse the
Mac's existing collector functions and Keychain integration without changing its auth
code or invoking its unrelated OpenRouter path. Normalize only allowlisted usage
fields. The Pi renders locally from the latest sanitized snapshot, so button cycling
does not depend on the Mac being awake. Mark old/failed observations stale locally.

## Verification

- Thirty tests pass, including independent provider failure, field allowlisting,
  invalid usage rejection, stale/expired/missing data, live pixel changes in all
  six artworks, persistent/wrapping selection, coalesced presses, and refresh retry.
- Ruff lint/format, shell syntax, systemd unit verification, and PNG prompt scan pass.
- All six 1200×896 plates and required fonts are installed on the Pi. GPIO 5, 6,
  16, and 24 are owned by the gallery with pull-ups and falling-edge events.
- Pi service is enabled and active; no automatic restarts, throttling 0x0.
- Launch agent is loaded, interval 600 seconds; its first run fetched both providers
  successfully, sent the sanitized snapshot, and exited 0.
- First live Kraken refresh completed 20:48:44 +08 in 34.18 seconds. Later service
  restarts preserved the selection and restored the listener.
- Independent Impeccable review found a Kraken ribbon collision and undersized
  timestamp. Both visual fixes were scored resolved; Codex date ambiguity and
  current product/design documentation were also corrected.
- All six sequential on-device refreshes completed and their successful-state hashes
  matched independently rendered expected frames: Pop Comic 20:54:06, Budget Kraken
  20:54:53, Reactor Room 20:55:40, Night Market 20:56:27, Quota Moth 20:57:13,
  Cosmic Pinball 20:57:59 (+08). Selected Budget Kraken again after the pass.
- Optical verification and physical switch actuation remain MC's on-device check;
  software completion cannot prove the final glass appearance.
- No git remote is configured; revision history is committed locally on the feature branch.
