---
name: Inky desk companion
description: Six exact-resolution usage-display studies on one seven-colour e-ink panel; no composition selected yet
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
  display:
    fontFamily: "DM Serif Display"
  headline-condensed:
    fontFamily: "Barlow Condensed SemiBold"
  bold:
    fontFamily: "Barlow SemiBold"
  body:
    fontFamily: "Barlow Medium"
  mono:
    fontFamily: "Space Mono"
---

# Design System: Inky desk companion

<!-- STUDY STAGE: six alternative compositions, deliberately unselected. Re-run this document once one is chosen for the live Pi build; at that point collapse this file to the single chosen identity. -->

## Overview

This is not a settled visual identity. MC asked for six materially different exact-resolution screen designs before any is chosen for the 600×448, seven-colour Inky Impression 5.7 on a Raspberry Pi Zero 2 W. All six share one fixed canvas, one physical palette, one data snapshot, and one semantic contract; what varies is composition, type voice, and how much of the frame goes to artwork versus numbers. Nothing here should be read as a brand decision — it is a controlled comparison.

**Key characteristics shared by all six:**
- Canvas is exactly 600×448px, rendered at 2× internally (`SCALE = 2` in `designs/render.py`) then quantized down — never drawn at native size.
- Every pixel reduces to one of seven fixed palette indexes (0–6); there is no eighth colour or alpha blending at render time.
- All six use the same frozen snapshot (`designs/data/snapshot.json`, `as_of` 2026-10-28T17:43:14+08:00) and the same stable data positions concept: a layout's number regions keep their job even if the artwork behind them changes.
- Each composition ships with two original artwork editions (12 originals total, one per `designs/artwork/NN-original.png`) and two palette proofs per edition: a "seven digital inks" proof and a muted "paper approximation" proof. The paper proof approximates the vendor's printed reference colours; it is not a calibrated photograph of the glass, and no composition has been visually confirmed under the desk's actual lighting.

## Colors

The palette is not six different palettes — it is one seven-slot indexed palette rendered two ways. `INKS` supplies the nominal RGB representation of each panel colour. `WORK` is a chosen reference palette used during quantization, so dark green artwork maps to the green slot rather than black. `PAPER` supplies the vendor's muted reference colours for the approximate paper proof. No table is a calibration of this particular physical display.

### Primary
- **Ink Black** (`#000000` ink / `#000000` on-screen): primary text, rules, and the dominant structural colour in every composition — Mission Control's instrument rail fills the full black at index 0.
- **Ink White** (`#ffffff` ink / `#ffffff` on-screen): the paper ground. Every layout starts from a full-white canvas (`Sheet.__init__`) and treats white as the resting state, not a colour choice per layout.

### Secondary
- **Ink Orange** (`#ff8c00` ink / `#eb821b` on-screen): the warmest accent, used sparingly as a single highlight element (e.g. Mission Control's reset-marker bar).
- **Ink Yellow** (`#ffff00` ink / `#f2cb19` working reference): used for emphasis against black (Mission Control's "WEEKLY ALLOWANCE LEFT"), artwork, and registration marks.

### Tertiary
- **Ink Red** (`#ff0000` ink / `#df3322` working reference): appears in artwork and registration marks, not body copy. A later live status system could give it an explicit warning role; none is installed now.
- **Ink Blue** (`#0000ff` ink / `#174992` on-screen) and **Ink Green** (`#00ff00` ink / `#16603d` on-screen): secondary row/marker accents in the same indicator role as red; none of the six compositions currently uses blue or green as a primary identity colour.

### Named Rules
**The Neutral-Text Rule.** Before quantization, any pixel whose RGB channels differ by ≤28 is snapped to pure black or pure white (`Sheet.finish()`, `designs/render.py:87-93`). Anti-aliased text and rules would otherwise pick up stray colour fringes at the seven-colour quantization boundary; this one function is what keeps body text and hairlines clean black/white across all twelve rendered mockups. It cannot neutralize text that is deliberately set in a colour ink (see Do's and Don'ts).

**The Seven-Slot Rule.** A render that doesn't use all seven palette indexes is treated as a bug, not a style choice (`assert used == set(range(7))` in `render.py:main`) — every composition must prove the full panel actually receives every ink, including via the footer's seven-chip registration mark (`footer()`, `render.py:130-136`).

## Typography

**Display font:** DM Serif Display — the editorial voice, used for headline numbers and titles in the warmer compositions (Harbour Almanac, Studio Companion, The Conservatory).
**Headline/condensed font:** Barlow Condensed SemiBold — the instrument voice, used for large tight numerals and all-caps labels in the colder compositions (Mission Control, Departure Board, The Balance).
**Body font:** Barlow Medium, with Barlow SemiBold for bold emphasis (section labels like "CLAUDE"/"CODEX").
**Label/mono font:** Space Mono — used for the `AS OF … SGT` footer timestamp in five layouts. Mission Control uses its condensed instrument font for that line instead.

**Character:** Headline numbers follow one axis per composition: serif-editorial (DM Serif Display + Barlow) or condensed-instrument (Barlow Condensed + Barlow). The observation timestamp remains a distinct, small data line in every layout.

### Hierarchy
- **Display** (DM Serif Display, 25–68px depending on role): provider names, remaining-percentage numbers, and editorial titles.
- **Headline-condensed** (Barlow Condensed SemiBold, 28–95px): the condensed alternative to Display for the colder compositions' headline numbers and all-caps section titles.
- **Bold** (Barlow SemiBold, 21–23px): capitalized provider labels in the numeral-led layouts. Conservatory uses serif title case; Departure Board uses condensed title case.
- **Body** (Barlow Medium, 13–20px): supporting facts — weekly-left captions, reset lines, scope and credit notes.
- **Mono** (Space Mono, 13px): the `AS OF {time} SGT  /  {date}` footer line only. Never reused for any other purpose — its presence is the freshness signal.

### Timestamp treatment
Keep observation time visible and separate from reset deadlines. The current study uses a 13px footer; the final live layout still needs an explicit stale-state treatment.

## Layout

There is no shared grid — each of the six studies is a distinct spatial argument for the same four facts (Claude weekly remaining, Codex weekly remaining, next reset, supporting session/scope/credit notes), tested against the same 600×448 frame:

1. **Harbour Almanac** (`harbour()`) — left artwork plate (20,73,300,224) beside a right-hand two-provider numeral column; supporting facts in a lower ledger strip; full-width footer rule.
2. **Mission Control** (`mission()`) — a full-height black instrument rail (0,0,238,448) against a right-hand artwork plate and numeral stack; the one composition with a filled black field rather than a white ground.
3. **The Conservatory** (`conservatory()`) — tall vertical artwork plate (20,83,200,294) with a wide right-hand typographic ledger split top/bottom by provider.
4. **Departure Board** (`departures()`) — full-width artwork banner (0,0,600,180) above a four-row ruled table, the only composition that lists every window (session, weekly, scoped, Codex weekly) as explicit rows rather than grouping by provider.
5. **The Balance** (`balance()`) — the boldest reduction: two very large numerals left, one artwork plate right (225,15,355,275), minimal supporting text.
6. **Studio Companion** (`studio()`) — artwork plate (20,82,277,235) beside a warm serif numeral column, closest in tone to Harbour Almanac but with session/scope notes folded into the lower-left instead of a ledger.

All six enforce hard canvas bounds: `Sheet.text()` raises if a string would print outside 600×448 or past a caller-declared `max_width`, so layout overflow is a render-time error, not a silent clip.

## Elevation & Depth

Not applicable. This is a reflective e-ink panel with seven flat indexed colours; there is no shadow, blur, or transparency primitive available to any composition, and none is simulated.

## Shapes

Every shape is an axis-aligned rectangle, line, or glyph — `Sheet.box()` and `Sheet.line()` are the only drawing primitives besides text and the artwork paste. No rounded corners, no diagonals, no decorative strokes beyond flat rules and solid colour chips (used as list markers in Departure Board and as a legend/registration strip in the footer).

## Do's and Don'ts

### Do:
- **Do** keep every layout's data region fixed and swap only the artwork behind/beside it — the point of the twelve-original collection is daily rotation without redesigning the screen (`designs/ANALYSIS.md`).
- **Do** run the Neutral-Text Rule's ΔRGB≤28 snap on any new text or rule before quantization; it is what keeps black text from fringing orange/green at the seven-colour boundary.
- **Do** treat the paper-approximation PNGs as vendor-reference proofs for comparing compositions on a laptop screen, not as a stand-in for the physical panel under desk lighting.
- **Do** calculate remaining allowance as `100 - used_percent` (or Claude's equivalent used percentage), label the limiting window explicitly, and keep session/weekly/scoped figures distinct (`PRODUCT.md`, `designs/ANALYSIS.md`).

### Don't:
- **Don't** treat any one of the six as the chosen production identity. MC has not picked one; round-2 review recommends Mission Control as a tentative default pending an on-device black-field contrast check, with Harbour Almanac as the light alternate — that is a recommendation on record, not a decision.
- **Don't** claim this file encodes verified physical colour or optical behaviour. All colour statements here are digital pixel values and vendor-reference approximations (`WORK`/`PAPER` tables in `designs/render.py`); the independent review's F1–F4 findings were resolved against pixel data, not glass. No composition has an optical/hardware claim attached.
- **Don't** set body or rule colour in anything but ink-black or ink-white. Only labels deliberately chosen as a colour accent (e.g. Mission Control's yellow "WEEKLY ALLOWANCE LEFT") should carry a non-neutral ink, and only with the understanding that the Neutral-Text Rule cannot clean up that label's own anti-aliased edges.
- **Don't** infer a workflow-default renderer, a scheduled push, or any live-refresh behaviour from this file. No periodic collection or render job is installed on the Pi; these are static study renders from a single frozen snapshot (`designs/data/snapshot.json`), not a running display.
