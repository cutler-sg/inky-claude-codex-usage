# Autonomous Pi usage collection

Branch: `feat/pi-usage-collector`. Updated: 2026-10-28.

## Acceptance criteria

- Mirror the current SwiftBar CLIProxyAPI management requests and usage normalization.
- Collect on the Pi every ten minutes, with no Mac dependency for normal operation.
- Establish verified-TLS connectivity to the owner's existing proxy.
- Transfer only the required management credential directly over SSH; never print it,
  include it in command arguments, or store it in the repository or public docs.
- Preserve per-provider last-good data, observation timestamps, stale semantics,
  and the existing local rendering/button service.
- Verify fresh upstream data and an automatic display refresh before disabling Mac sync.
- Test error handling and request shape; update docs and publish the tested code.

## Tasks

- [x] Read the actual SwiftBar collector and existing Pi/Mac deployment.
- [x] Establish Pi connectivity to the private proxy.
- [x] Implement the portable built-in proxy adapter, collection command, and timer.
- [x] Transfer protected configuration and verify fresh data and display refresh.
- [x] Disable the superseded Mac launch job, document, validate, and publish.

## Findings

The source uses a Keychain management credential and two authenticated management
routes: auth-file discovery and proxy API calls with a literal vendor-token placeholder.
The Pi currently has no Tailscale client or private DNS route. Owner-specific endpoint
and credential values remain outside tracked files. The user's explicit request
authorizes this credential transfer and on-device collection configuration.

## Verification

- Tailscale installed through the official Debian repository; MC approved device
  enrollment. Pi private DNS and verified HTTPS access work, with no TLS bypass.
- Configuration transferred directly from Keychain over SSH to root:root mode0600
  `/etc/inky/usage.env`, inside a mode0700 directory. No local secret copy, printed
  key, secret command argument, or repository credential file was created.
- First Pi service fetch succeeded at22:23:49+08 for both providers (three Claude
  windows and one Codex window), preserving banked/applicable credit semantics.
- The old Mac job was unloaded and disabled. The natural Pi timer fired again at
  22:33:49 and fetched both providers fresh at22:33:51 without Mac synchronization.
- Quota Moth refreshed at22:34:33 in34.16seconds; successful frame hash matched an
  independent render of the latest on-device snapshot. The user's selection was retained.
- 46 tests pass, including request/envelope shape, token substitution, disabled
  account filtering, redirect refusal, response bounds, malformed payload handling,
  per-provider fallback, and snapshot persistence before an error exit.
- Ruff lint/format, shell syntax, systemd unit verification, and local doc links pass.
  Staged Gitleaks scan found no leaks. Owner-specific URL and credential remain
  outside tracked source and documentation.
- Added `docs/website-agent-brief.md` in response to the follow-up: exact mockup,
  master, clean-plate, proof, and prompt paths; accurate current architecture;
  explicit distinction between digital concepts and physical device photographs.

## Decisions

- Keep the external collector adapter and Mac sync scripts as optional alternatives;
  only the installed Mac schedule is disabled. Normal operation is entirely on the Pi.
- A oneshot service and monotonic ten-minute timer avoid a new long-running network
  daemon. Failed providers preserve their own last-good timestamp; the next timer
  retries. The gallery continues to mark stale data independently.
- OnUnitActiveSec preserves the last service activation when the timer is restarted;
  verification therefore waited for the natural interval instead of shortening it.
