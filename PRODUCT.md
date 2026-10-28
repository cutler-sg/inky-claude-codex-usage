# Inky desk companion

<!-- impeccable:product-schema 1 -->

## Platform

Embedded e-ink: Raspberry Pi Zero 2 W and 600×448 seven-colour Inky Impression 5.7. The design comparison gallery is web-based; the product itself is a static, reflective desk display.

## Users

MC, a software engineer in Singapore, checks the display throughout the day to plan use of Claude Code and Codex subscription allowance.

## Product Purpose

Make remaining allowance and the next reset readable at a glance, while keeping weekly and model-specific limits visible. Artwork should make the display worth keeping on the desk.

## Operating Context

The Pi at `pi@inky.local` runs `inky-gallery.service` and renders locally from its latest credential-free usage snapshot. The Mac reuses the existing `claude_usage.py` collector functions, CLIProxyAPI, and Keychain access; launchd job `com.cotdp.inky-usage` collects and sends a sanitized snapshot every 600 seconds and at login. Button navigation works without the Mac being awake. All display times use Asia/Singapore.

A full panel refresh takes about 34 seconds. A/B select previous/next artwork, C selects another random artwork, and D returns to Budget Kraken. Selection persists across restarts. The listener debounces presses for 200ms, settles changes for 0.8 seconds, runs one display child at a time, and retains the latest pending selection. Refresh starts are at least 40 seconds apart.

## Capabilities and Constraints

- MC approved all six integrated-v2 compositions and authorized unattended live implementation. All six are available through the physical buttons; Budget Kraken is home.
- Six clean, text-free ImageGen plates preserve the approved artwork and its information-bearing surfaces. Deterministic projective typography inserts live values into those original surfaces.
- Every display frame is exactly 600×448, indexed 0–6 with the exact vendor palette. Artwork remains integrated with the data at native panel resolution.
- Distinguish session, weekly, scoped-model, reset-credit, source-health, and freshness information.
- Subscription usage percentages are not token counts or currency budgets.
- Missing windows stay missing. Each provider becomes stale after 20 minutes or a collection error, and unavailable after 24 hours; stale state appears in that provider's header. The shared observation time uses the oldest provider observation.
- Passed reset deadlines show `UPDATE PENDING`; the renderer never assumes replenishment without a new observation.
- Keep credentials and API tokens away from the Pi.
- Static artwork and labels must survive the panel's seven-colour palette and small physical dimensions.
- MC rejected the first study's understated artwork and separated data/illustration treatment. The approved direction integrates numbers into balloons, tentacle coils, instruments, signs, wing markings, and pinball inserts, inspired by the supplied full-screen comic and engraved octopus photographs.

## Evidence on Hand

`claude_usage.py` in MC's scripts workspace supplies the trusted collector functions; its authentication code is unchanged and its unrelated OpenRouter path is not invoked. `inky_frame/collect.py` exports only validated usage fields; the Pi receives no credentials.

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
