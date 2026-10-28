# Usage on the desk: requirements and implementation research

## What this display must do

MC's confirmed priority is **allowance remaining and the next reset**, with weekly and model-specific limits kept visible. The device is a 600×448 seven-colour Inky Impression on a Pi Zero 2 W. It should feel like a small artwork that happens to be useful throughout the working day. Ten-minute updates are sufficient; the measured full refresh takes 34.4 seconds.

The first deliverable is six complete alternatives, not a deployment selected without review. This collection includes twelve original artworks, two per direction. The data positions stay stable when the illustration changes. All six use the same frozen, non-secret cache snapshot, timestamped in `data/snapshot.json`.

## How the existing scripts actually work

Source: the external `claude_usage.py` collector module (not bundled), read in full. It is a SwiftBar presentation script plus collector; it does not export a clean JSON document from its CLI.

1. `get_management_key()` (line 53) asks macOS Keychain for service `cliproxyapi-management`. This is a management credential, not either vendor's OAuth token.
2. `list_auth_indexes()` (line 78) calls the proxy's `/v0/management/auth-files`, choosing the first enabled auth entry per provider. Multiple enabled accounts are therefore not aggregated; account identity needs an explicit choice if that changes.
3. `api_call()` (line 96) posts a GET request description to `/v0/management/api-call`. A literal `$TOKEN$` in the vendor Authorization header is substituted by CLIProxyAPI. The proxy owns token refresh.
4. Claude's endpoint is `https://api.anthropic.com/api/oauth/usage`, with the script's OAuth beta header. Codex uses `https://chatgpt.com/backend-api/wham/usage`, with its configured CLI User-Agent.
5. `normalize_claude()` (line 193) prefers non-empty `limits[]`: session, weekly-all, and dynamic weekly-scoped model limits. It falls back to `five_hour`/`seven_day` and their `utilization` fields. The fallback currently does not enumerate legacy model-specific top-level keys.
6. `normalize_codex()` (line 228) reads primary/secondary windows from the main `rate_limit`. It labels windows from their actual duration, so this account's primary window is weekly. `reset_at` is epoch seconds; `reset_after_seconds` is a fallback. Additional model quotas are deliberately omitted by the current script.
7. `codex_reset_credits()` (line 254) distinguishes `available_count` from `applicable_available_count`. Two banked credits are not two automatically usable resets. The display must never redeem them.
8. `resolve()` (line 285) caches successful raw responses per provider for up to 24 hours. A fetch failure returns recent data with an error/cache-age note. The disk cache contains the last successful payload and timestamp, but does not retain the latest fetch error; cache-only consumers cannot know whether a recent refresh failed.
9. `main()` (line 335) prints SwiftBar markup and also reads an unrelated OpenRouter key from a protected local file. I did not run `main()`, read credential files, or fetch management credentials. The design snapshot uses only the non-secret cache and existing pure normalization functions.

The adjacent `USAGE-WATCH.md` is older. It describes direct local OAuth reads and the superseded Codex `/backend-api/codex/usage` route; it is not the source of truth for this collector. Its early-reset detection is still a useful design idea: compare a meaningful drop in usage before the previous reset deadline. That requires successive fresh observations, not a single snapshot.

These are subscription allowance windows, not API billing totals. Neither the normalized data nor the cache establishes a count of remaining tokens, a currency budget, or how many coding tasks remain. No such conversion belongs on the screen.

## Information model and exact semantics

| Screen item | Source or calculation | Rule |
| --- | --- | --- |
| Remaining | `100 - percent` / `100 - used_percent` | Preserve reported value; clamp only the drawing, flag out-of-range payloads. |
| Headline allowance | Minimum remaining across the relevant current limits | Label the limiting window, usually weekly here. Never average windows. |
| Session | Claude session or duration-labelled Codex window | If absent, show `not reported`; never synthesize 100%. |
| Weekly all | Claude `weekly_all`, Codex duration near seven days | Always visible even when session has reset. |
| Model scope | Claude scoped `display_name` and percentage | Keep the scope name; extra scopes need overflow/detail policy. |
| Next reset | Earliest future deadline among reported windows | Label provider/window. A passed deadline means refresh pending, not proven replenishment. |
| Reset credits | Available count and currently applicable count | `2 banked; 0 applicable` is different from `redeemable now`. |
| Allowed / reached | Codex `rate_limit.allowed` / `limit_reached` | They are usage availability flags, not provider-wide service health. |
| Freshness | Separate `observed_at` per provider and latest fetch result | A successful screen push is not a successful provider fetch. |
| Plans | Codex `plan_type`; Claude label is hard-coded in SwiftBar | Do not present `Max 20x` as a newly verified account entitlement. |
| Suggested next provider | Headroom comparison, explicitly advisory | More headroom does not establish model suitability or equal task cost. |

The snapshot shows Claude 100% session remaining, 20% weekly-all remaining, and Fable 58% scoped weekly remaining. Codex reports only a weekly window, 95% remaining, `allowed=true`, `limit_reached=false`, two banked reset credits and zero applicable. The Claude weekly limit constrains the otherwise full session. See `data/snapshot.json` for exact times; all display dates are Asia/Singapore.

In these mockups, “next reset” means the next reported scheduled deadline: Claude's 17:50 session reset. That session is already full, so it does **not** restore the binding weekly allowance. The first useful Claude weekly replenishment is Friday at 18:00. For the live implementation, I recommend distinguishing “next scheduled reset” from “binding allowance returns” rather than implying that the 17:50 event solves the weekly constraint.

## Refresh proposal

**Recommended:** extend collection on the existing trusted always-on host, normalize a small credential-free snapshot, render a 600×448 PNG there, and push it over the existing SSH path every ten minutes. A systemd timer on that host is the smallest durable scheduler if it already runs Linux. The Pi continues to do just palette handling and a one-shot refresh. The implementation should be one scheduled command with a lock, not a new web service.

This requires first checking where the current proxy-management credential is available. The inspected SwiftBar path is macOS Keychain-specific; it cannot simply be copied to Linux. No credentials were moved or auth changes made in this design session. If hwi has no supported local management credential, a launchd job on this Mac can reuse the existing collector, but updates would stop while the Mac is asleep or away. That is a real reliability tradeoff, not something the Pi can solve by refreshing its old image.

The scheduled collector should return structured JSON directly rather than scrape SwiftBar's text. Preserve provider/window identity, duration, reset deadline, observed timestamp, last fetch result, and credit applicability. Fail providers independently, validate boundary shapes, use request timeouts, and write snapshots atomically. Existing normalization can be factored into a shared module after selection; do not fork the OAuth handling into this repo.

### Refresh and failure policy

- Poll every ten minutes. Render stable absolute reset times and the observation timestamp; avoid a seconds countdown that is wrong for most of the interval.
- Schedule a daily artwork change on Singapore calendar date. Twelve pieces form a twelve-day collection. More frequent art rotation can be a later preference; it does not need more API calls.
- Keep last-good values on temporary errors with a prominent `STALE` mark and provider-specific observation time. Suggested thresholds: stale after 20 minutes, unavailable after 24 hours. These are proposed product thresholds, not provider limits.
- A successful push updates the screen timestamp separately from provider observation time. The dashboard must include an absolute `as of` time so a completely offline Pi remains visibly old to a human; it cannot repaint its own stale badge without a local timer.
- If autonomous offline badging is wanted, add a local ten-minute Pi timer that checks age and renders a stale overlay from the last sanitized snapshot. This is a separate, justified capability, not needed merely to show new images.
- Skip identical rendered frames and serialize hardware access. With absolute timestamps, a fresh observation normally changes the image every ten minutes; failures can skip a duplicate stale frame.
- Do not interpret a forecast reset as successful replenishment until the next fresh sample confirms it. Do not auto-redeem reset credits. Do not auto-switch the user's models.
- The existing vendor busy-held-high fallback worked on the physical unit. Exact digital pixels and seven colour indexes are verifiable; physical colour rendering needs an on-device comparison in the desk's lighting.

## Design collection

1. **Harbour Almanac** — an illustrated journal spread, with large weekly balances beside the print and a clear lower ledger. Best overall balance of art and quick reading.
2. **Mission Control** — a black instrument rail paired with a space print and a prominent next-reset callout. Strongest distance readability; the dark area needs a physical contrast check.
3. **The Conservatory** — an airy botanical specimen page, with the two providers in a typographic ledger and a vertical artwork plate. Quiet, precise, and comfortable for long desk use.
4. **Departure Board** — a travel poster above a ruled timetable of allowances and reset destinations. Best comparison of all windows in one place.
5. **The Balance** — a museum-like abstract composition with two exceptionally large balances and compact supporting notes. The boldest graphic object.
6. **Studio Companion** — a cat print beside a friendly, complete working-day receipt. Warmest personality while retaining explicit weekly and scoped limits.

Each has two artwork editions, a nominal seven-ink PNG, and a muted palette approximation. The approximation uses the vendor's reference palette, not a calibrated photograph. Art originals are not claimed to contain exactly seven RGB values; final screen PNGs are indexed to precisely the seven supported colour slots, including black/white text.

## What stays open after this deliverable

Choose the composition (or combine a layout with another artwork), confirm the scheduler host/credential route, then implement one ten-minute collection/render/push job and inspect the chosen result on the physical display. No periodic job or usage image has been installed on the Pi during this mockup-first stage.
