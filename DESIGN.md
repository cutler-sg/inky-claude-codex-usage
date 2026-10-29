---
name: Inky desk companion
description: Six approved illustrated usage displays with live text integrated into the artwork
colors:
  ink-black: "#000000"
  ink-white: "#ffffff"
  ink-green: "#00ff00"
  ink-blue: "#0000ff"
  ink-red: "#ff0000"
  ink-yellow: "#ffff00"
  ink-orange: "#ff8c00"
  work-black: "#000000"
  work-white: "#ffffff"
  work-green: "#16603d"
  work-blue: "#174992"
  work-red: "#df3322"
  work-yellow: "#f2cb19"
  work-orange: "#eb821b"
typography:
  display-comic:
    fontFamily: "Bangers"
  display-engraved:
    fontFamily: "DM Serif Display"
  label:
    fontFamily: "Barlow Condensed SemiBold"
---

# Design System: Inky desk companion

## Overview

MC approved all six [integrated-v2 compositions](designs/integrated-v2/index.html) and authorized unattended live implementation. The screen is a full-frame illustration whose own balloons, tentacle coils, machinery, signs, wing markings, or pinball inserts carry usage information. MC rejected the first study's understated artwork and separation between picture and statistics.

The live system preserves these compositions using six clean, text-free ImageGen plates in `assets/live/`. The edit prompts and original source paths are recorded in [prompts.json](assets/live/prompts.json). `inky_frame/live.py` renders deterministic typography into the original surfaces using projective transforms; no generated frozen numbers remain in the live text layer.

**Key characteristics:**

- The original profile is exactly 600×448 with seven palette indexes (0–6). Spectra 6 profiles use six indexes (0–5) at their detected resolution.
- Full-frame artwork with fixed information-bearing surfaces; text adapts within each surface.
- Large provider allowance figures, supporting quota/reset information, and visible observation time.
- Six approved identities in one button-controlled gallery; Budget Kraken is home.

**Historical provenance.** The earlier twelve-artwork comparison remains in `designs/artwork/`, `designs/mockups/`, [ANALYSIS.md](designs/ANALYSIS.md), and `designs/review/`; its deterministic sidebar/plate renderer is `designs/render.py`. It used the frozen snapshot `designs/data/snapshot.json` (2026-10-28T17:43:14+08:00), DM Serif Display/Barlow/Space Mono, and seven-ink plus approximate-paper proofs. Its six layouts were Harbour Almanac, Mission Control, The Conservatory, Departure Board, The Balance, and Studio Companion. The later `designs/integrated-v2/` masters, prompts, proofs, and overlay proposal record the approved composition study. Both studies remain historical references; the live renderer and `assets/live/` define current output.

## Colors

On the original panel, one seven-slot indexed palette serves every composition. The `ink-*` tokens are the exact vendor RGB palette in index order: black, white, green, blue, red, yellow, orange. The `work-*` tokens are the quantization references used to map artwork to those physical slots. They do not describe calibrated physical colour under desk lighting.

### Primary

- **Ink Red** and **Ink Blue** distinguish large allowance figures in most compositions. Night Market uses yellow and red against dark signs; Cosmic Pinball uses red for both allowance figures and blue for reset details. Provider names always supply identification independently of colour.
- **Ink Yellow** and **Ink Orange** carry the illustrated print character, signs, and highlights.

### Neutral

- **Ink Black** supplies the engraving, outlines, and most text.
- **Ink White** supplies balloons, ribbons, labels, and other light text-bearing surfaces. Night Market and Cosmic Pinball also use white lettering on dark surfaces.

### Named Rules

**The Panel-Palette Rule.** The original output remains a 600×448 `P` image using indexes 0–6. Spectra 6 profiles use black/white/yellow/red/blue/green (0–5) at 600×400, 800×480, or 1600×1200. `gallery.show_frame()` validates the detected profile's dimensions, indexes, and palette before display. The vendor performs Spectra's native index remapping; do not apply it twice. Orange source art is mapped into the available six inks.

**The Neutral-Text Rule.** Before quantization, pixels whose RGB channels differ by at most 28 snap to black or white. This prevents neutral anti-aliasing from becoming coloured fringes. Coloured text has a black stroke before the final palette conversion.

## Typography

**Comic display:** Bangers for Pop Comic, Reactor Room, Night Market, and Cosmic Pinball. Its compact, emphatic lettering belongs to the illustrated signs and instruments.

**Engraved display:** DM Serif Display for Budget Kraken and Quota Moth, matching their engraved character.

**Supporting labels:** Barlow Condensed SemiBold for session, scope, reset, credit, and observation text across all six.

`Canvas.panel()` renders each original-profile text patch at 2×, fits each line to its allocated surface, then projects it into the composition's quadrilateral. Font sizes are fitted per surface rather than governed by a global size scale. The final frame is downsampled and quantized without dithering.

### Hierarchy

- Provider name, remaining percentage, and window label form each main information surface.
- Weekly remaining leads when reported; otherwise the most-used reported window supplies the headline.
- Claude session and scoped-model allowance, provider reset deadlines, and Codex reset credits occupy supporting surfaces.
- Observation time remains distinct from reset time. All six compositions use the oldest provider observation; Pop Comic splits its date, time, and SGT label across the starburst.

## Layout

Artwork coordinates retain one 600×448 logical canvas. The original profile preserves its existing pixels. Other profiles uniformly fit the complete plate and its text surfaces into the target, with white margins and no cropping. Small targets retain bounded supersampling; 1600×1200 renders at native size to limit memory. Text is drawn from fonts at the target scale, rather than enlarging a quantized proof. Preserve each approved plate's artwork and surface positions. `render()` in `inky_frame/live.py` owns the exact quadrilaterals:

| Composition | Information surfaces |
| --- | --- |
| Pop Comic | Thought balloons, caption ribbons, bottom strip, and timestamp starburst |
| Budget Kraken | Two tentacle-enclosed ovals and ribbons woven through the arms |
| Reactor Room | Curved tank labels, gauge faces, lower plaques, and metal placards |
| Night Market | Shop signs, awnings, lantern, shutter, and lower sign |
| Quota Moth | Pale wing markings and botanical ribbons |
| Cosmic Pinball | Planet scoring islands, name headers, inserts, plaques, and apron strips |

The original surfaces establish the layout; adding a detached statistics rail would repeat the treatment MC rejected. No automatic slideshow is installed.

## Elevation & Depth

Depth comes from the artwork's engraving, perspective, halftone, and overlapping forms. Dynamic text conforms to those surfaces. The physical output has seven flat colours on the original panel, or six on Spectra 6; the renderer adds no interface shadows, blur, or translucent panels.

## Shapes

Preserve the plate's organic coils, curved labels, ribbons, signs, and illustrated borders. Text patches are transparent during composition and project into four-point surfaces; their patch rectangles must not become visible containers. Do not replace the original surfaces with generic cards.

## Components

### Allowance and source state

Each provider has an independent observation and health state. Its header gains `/ STALE` after 20 minutes or a collection error, and `/ UNAVAILABLE` after 24 hours without a valid observation. On the new profiles, unavailable provider headings split into two lines to avoid excessively small labels. Unavailable values display `--` or `NOT REPORTED`; missing windows never become zero usage or full allowance. Passed reset deadlines display `UPDATE PENDING` until a new observation arrives.

### Physical navigation

A selects previous, B next, C another random composition, and D Budget Kraken. Selection persists. The Pi's `inky-gallery.service` debounces presses for 200ms and settles changes for 0.8 seconds. One child performs each refresh; presses during a refresh coalesce into the latest pending selection. Refresh starts remain at least 40 seconds apart, so visible selection changes wait for the panel's slow refresh.

## Do's and Don'ts

### Do:

- **Do** preserve the approved artwork and draw live values within its original surfaces.
- **Do** keep session, weekly, scoped-model, credits, source health, observation time, and reset deadlines semantically distinct.
- **Do** retain the detected profile's indexed palette through the display path.
- **Do** treat digital and approximate-paper proofs as references rather than calibrated photographs of the panel.

### Don't:

- **Don't** use frozen ImageGen lettering as live usage, or infer replenishment from a passed reset deadline.
- **Don't** hide a provider failure behind the other provider's fresh timestamp.
- **Don't** treat historical first-study fonts, sidebar layouts, or Mission Control recommendations as current authority.
- **Don't** claim optical verification of the live compositions. The first live Budget Kraken refresh completed at 20:48:44 +08:00 on 2026-10-28 (34.18 seconds); MC's visual check under desk lighting remains outstanding.
