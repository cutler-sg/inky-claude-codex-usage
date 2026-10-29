# Inky desk companion

<!-- impeccable:product-schema 1 -->

## Platform

Embedded e-ink: tested on Raspberry Pi Zero 2 W and 600×448 seven-colour Inky Impression 5.7; experimental profiles for Spectra 6 at 600×400, 800×480, and 1600×1200. The design comparison gallery is web-based; the product itself is a static, reflective desk display.

## Users

MC, a software engineer in Singapore, checks the display throughout the day to plan use of Claude Code and Codex subscription allowance.

## Product Purpose

Make remaining allowance and the next reset readable at a glance, while keeping weekly and model-specific limits visible. Artwork should make the display worth keeping on the desk.

## Operating Context

The Pi at `pi@inky.local` collects directly from CLIProxyAPI over verified HTTPS through `inky-usage.service`, scheduled every ten minutes by `inky-usage.timer`. `inky-gallery.service` renders locally from its sanitized snapshot and handles the buttons. Collection and navigation are independent of the Mac. The previous Mac launch job is superseded. All display times use Asia/Singapore.

A full panel refresh takes about 34 seconds. A/B select previous/next artwork, C selects another random artwork, and D returns to Budget Kraken. Selection persists across restarts. The listener debounces presses for 200ms, settles changes for 0.8 seconds, runs one display child at a time, and retains the latest pending selection. Refresh starts are at least 40 seconds apart.

## Capabilities and Constraints

- MC approved all six integrated-v2 compositions and authorized unattended live implementation. All six are available through the physical buttons; Budget Kraken is home.
- Six clean, text-free ImageGen plates preserve the approved artwork and its information-bearing surfaces. Deterministic projective typography inserts live values into those original surfaces.
- Display frames match the detected profile: the original 600×448 output uses indexes 0–6; Spectra 6 profiles use indexes 0–5 in their required palette order. Artwork remains integrated with the data at native panel resolution.
- Distinguish session, weekly, scoped-model, reset-credit, source-health, and freshness information.
- Subscription usage percentages are not token counts or currency budgets.
- Missing windows stay missing. Each provider becomes stale after 20 minutes or a collection error, and unavailable after 24 hours; stale state appears in that provider's header. The shared observation time uses the oldest provider observation.
- Passed reset deadlines show `UPDATE PENDING`; the renderer never assumes replenishment without a new observation.
- Vendor OAuth tokens remain on CLIProxyAPI. Only its management credential is
  installed on the Pi, in root-owned mode-0600 configuration outside the repository.
- Static artwork and labels must survive the detected panel's limited colour palette and physical dimensions.
- MC rejected the first study's understated artwork and separated data/illustration treatment. The approved direction integrates numbers into balloons, tentacle coils, instruments, signs, wing markings, and pinball inserts, inspired by the supplied full-screen comic and engraved octopus photographs.

## Evidence on Hand

The existing SwiftBar `claude_usage.py` supplied the request and normalization
contract. `inky_frame/proxy.py` now implements that contract without Keychain or
an external source module at runtime. It discovers enabled provider accounts and
requests usage through CLIProxyAPI with literal `$TOKEN$` substitution. It does
not redeem credits or fetch unrelated OpenRouter data. `inky_frame/collect.py`
retains independent provider failure handling and emits only validated usage fields.

The first live Budget Kraken refresh completed on 2026-10-28 at 20:48:44 +08:00 in 34.18 seconds. This confirms the hardware refresh completed; optical verification of live text and colour remains MC's task. The earlier sample image was optically verified separately.

The original twelve-artwork study and frozen snapshot remain in `designs/`; the approved generated compositions and prompts remain in `designs/integrated-v2/`. Live clean plates and edit provenance are in `assets/live/`. These historical frozen proofs do not represent current usage.

## Product Principles

- Lead with allowance remaining and the next reset (confirmed by MC).
- Keep the most restrictive relevant quota visible.
- Separate observed facts from scheduling advice.
- Integrate information into the artwork's own balloons, signs, markings, or instruments; preserve those positions when live values change.
- Never show stale or absent data as newly replenished allowance.

## Remaining Verification

MC's optical check of the live compositions under desk lighting remains outstanding. Composition approval and collection ownership are settled.

The three Spectra 6 sizes have synthetic render and vendor-buffer validation, but
physical colour, refresh, and button verification require those devices. The
13.3-inch button C uses GPIO25; other profiles use GPIO16.
