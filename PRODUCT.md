# Inky desk companion

<!-- impeccable:product-schema 1 -->

## Platform

Embedded e-ink: Raspberry Pi Zero 2 W and 600×448 seven-colour Inky Impression 5.7. The design comparison gallery is web-based; the product itself is a static, reflective desk display.

## Users

MC, a software engineer in Singapore, checks the display throughout the day to plan use of Claude Code and Codex subscription allowance.

## Product Purpose

Make remaining allowance and the next reset readable at a glance, while keeping weekly and model-specific limits visible. Artwork should make the display worth keeping on the desk.

## Operating Context

Existing passwordless SSH at `pi@inky.local`; a full screen refresh takes about 34 seconds. Ten-minute data refreshes are sufficient. Existing usage collection runs through CLIProxyAPI on hwi. All display times use Asia/Singapore.

## Capabilities and Constraints

- Six materially different exact-resolution concepts must be reviewed before live deployment.
- Twelve original reusable artworks support a future rotation.
- Distinguish session, weekly, scoped-model, reset-credit, source-health, and freshness information.
- Subscription usage percentages are not token counts or currency budgets.
- Missing windows stay missing; stale readings cannot be presented as fresh.
- Keep credentials and API tokens away from the Pi.
- Static artwork and labels must survive the panel's seven-colour palette and small physical dimensions.

## Evidence on Hand

`claude_usage.py` in MC's scripts workspace contains the current collector. Its non-secret cache provides the frozen mockup snapshot. The first sample image has already been optically verified on the hardware.

## Product Principles

- Lead with allowance remaining and the next reset (confirmed by MC).
- Keep the most restrictive relevant quota visible.
- Separate observed facts from scheduling advice.
- Change artwork independently of data, with stable information positions.
- Never show stale or absent data as newly replenished allowance.

## Open Decisions

Which of the six compositions to deploy; which always-on host should own collection and scheduled pushes. This session delivers the alternatives and recommendation before deployment.
