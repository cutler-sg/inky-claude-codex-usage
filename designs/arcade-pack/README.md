# Arcade artwork pack — concept study

Six generated fan-art mockups inspired by Capcom's early Street Fighter games.
The balances are part of the arcade composition: versus lettering, health bars,
shop signs, aircraft stencils, selection cards and continue-screen windows.

**Retained as the second theme.** See the [planned theme controls](../../docs/artwork-themes.md).
Live overlays and button D theme switching will follow the artwork studies.

Open [the comparison gallery](index.html) locally to browse all six or switch to
a 600 CSS-pixel-wide view. The original generated PNGs are preserved at their
native dimensions; browser scaling is a readability preview, not an exact
600 × 448 render or a physical size simulation.

| Concept | Direction | Selected artwork |
| --- | --- | --- |
| 01 / Versus | Ryu and Ken portraits, diagonal energy and oversized fighter-name plaques. | [Mockup](01-versus-mockup.png) |
| 02 / Rooftop Round | Pixel-art rooftop duel; weekly allowance replaces health in the fight HUD. | [Mockup](02-rooftop-mockup.png) |
| 03 / Market Kick | Chun-Li in a market street; the shop signs carry the balances. | [Mockup](03-market-mockup.png) |
| 04 / Sonic Reserve | Guile at an airbase; aircraft panels and fuel motifs carry the figures. | [Revised mockup](04-airbase-mockup-v2.png) |
| 05 / Select Your Fighter | Roster portraits and two large selection cards. | [Mockup](05-select-mockup.png) |
| 06 / Continue? | Expressive portraits and oversized arcade score windows. | [Mockup](06-continue-mockup.png) |

## Data and status

These are **mockups with baked-in sample readings**, not live usage. They reuse
the weekly values from the [frozen 28 October 2026 design snapshot](../data/snapshot.json):
Claude **20% remaining**, resetting Friday at 18:00; Codex **95% remaining**,
resetting Wednesday at 14:49. Reset times use Asia/Singapore. The values do not
describe current account status. Each `WEEK LEFT` label means weekly allowance
remaining, rather than elapsed or remaining time.

The study focuses on the two headline balances. Session/scoped limits, freshness,
missing-data states, timestamps and reset credits are not represented yet. These
must be designed into a live pack rather than silently dropped from the display.

The colours are RGB concept colours. The prompts request a restrained seven-ink
direction, but the generated images contain more than seven actual colours and
have not been quantized or tested on the physical panel. Fine textures and dark
stage detail, especially in Rooftop Round, may need simplification for e-ink.

## Generation and review

Generated with the **built-in image_gen tool**. Exact initial prompts are in
[prompts.json](prompts.json); tool artifact identifiers are in
[generation.json](generation.json). The targeted airbase edit is recorded in
[revisions.json](revisions.json). Its first version is retained for comparison.

All six selected images were inspected for composition and the main provider
labels and percentages. The airbase revision makes the left gauge visibly lower
than the right, but its drawn arc proportions remain approximate; they must be
rebuilt deterministically for live use. Generated bars and gauges are artwork,
not calibrated data renderers.

Versus is the boldest portrait-led direction. Rooftop Round is closest to the
fighting-game screen structure. Market Kick integrates the figures most naturally
into its stage. Select Your Fighter offers the clearest reusable text surfaces.

## After choosing a direction

Generate matching clean plates with changing text and gauges removed, then draw
live values into those surfaces in code. Keep provider labels and allowance
semantics clear, and make bars/gauges follow the actual remaining percentage.
Test the result at 600 × 448 with the original display palette before adapting
it to other profiles. Market and aircraft panels will need perspective-aware
text placement; the straight HUD and selection cards are simpler overlay targets.

This study does not change the installed artwork rotation or deploy to the Pi.
