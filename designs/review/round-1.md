# Impeccable finish review — Inky usage design collection

## 1. Disposition: **fix** (targeted; no rebuild, no art recapture except one crop)

The collection is genuinely good — six materially different compositions, correct data everywhere, and the art earns its desk space. But the ink files (the exact pixels the panel would receive) carry a systematic text-edge fringing defect, plus three small factual-hygiene issues. All are cheap fixes in `designs/render.py`; the twelve artworks and all six layouts survive as-is.

## 2. Material findings

**F1 — Colour fringing on all text edges in every `-inks.png` (CONFIRMED, top priority).** `Sheet.finish()` (`designs/render.py:82-91`) LANCZOS-downsamples 2× then quantizes with nearest-RGB, no dither. Anti-aliased grey edge pixels land nearest to saturated inks, not black/white. Measured in pure-text regions: harbour-almanac-1-inks right column has 2,049 green/blue/orange pixels against 4,591 black text pixels (~31% as many stray colour pixels as ink pixels); mission-control rail and departure-board table show the same ~2% of region area. At the panel's ~105 PPI every glyph will shimmer green/blue. The `-paper.png` proofs mute these fringes, so the review deliverable under-represents an artefact the hardware will show. Fix: snap near-neutral RGB to black/white before `quantize` (or render text layers unantialiased at 1×); one function, re-render all 24 files.

**F2 — Balance: unattributed credits line (both editions).** `render.py:227` renders "Resets 2 banked / 0 applicable" with no provider, sitting directly under a block that talks about Claude 5h. Every other layout says "Codex". A glance could read these as Claude resets. Add the word Codex.

**F3 — Departure Board edition 2: bad art crop.** The 600×180 band crop of artwork 8 (`departure-board-2-paper.png` / `-inks.png`, top edge) beheads a green/yellow vehicle; it reads as an unidentifiable floating object behind the "NEXT DEPARTURES" box, clipped at the canvas top. Edition 1 crops cleanly. Re-crop (offset the `ImageOps.fit` focus) or swap the artwork for this slot.

**F4 — Footer date is hard-coded, violating the snapshot-derivation property.** `render.py:122` writes the literal string `28 OCT 2026` while `d["date"]` already derives the same date from `as_of`. Correct today, silently wrong on the first live re-render. Same latent class (fine for frozen mockups, must become conditional before deployment, no change needed now): "today"/"Today" (`render.py:142,198`), "CODEX ALLOWED" (`:166`), "5h not reported" (`:185,211`), and the advisory "More weekly room." (`:245` — the one hard-coded claim that's a comparison, not a label; it also blurs the observed-fact/advice separation PRODUCT.md asks for).

**Minor, no action required:** Mission Control's Codex reset is a bare "4 Nov 14:49" at the rail's foot (`render.py:159`) with no "Reset" prefix, far from its 95%; the Departure Board row chips reuse green for both Claude 5h and Codex, suggesting an encoding that doesn't exist.

## 3. Factual / data checks — all pass

- Claude weekly 20% left, Fable 58%, session 100%, Codex weekly 95%: match `snapshot.json` exactly in all twelve images.
- Reset times: session 17:50 today; weekly/Fable Fri 18:00 (30 Oct 2026 is indeed a Friday; 28 Oct is a Wednesday, matching "WED 28 OCT"); Codex 4 Nov 14:49. All correct, all labelled SGT or implicitly local.
- Credits: "2 banked / 0 applicable" present in all six layouts — the banked-vs-applicable distinction ANALYSIS.md requires is never collapsed into "redeemable".
- Codex 5h absence: never synthesized; Conservatory and Departure Board state "5h not reported" explicitly, the rest simply omit it. Honest either way.
- Weekly binding quota: every layout headlines the 20% weekly, not the flattering 100% session. Correct prioritisation.
- The seven-ink registration strip in the footer plus the render-time assertion (`render.py:264`) guarantee all seven palette slots reach every image. Good honesty device.
- One semantic observation, not a defect: the "next reset 17:50" being headlined (hugely, in Mission Control and Balance) is the session window that's already at 100% — a no-op replenishment. It complies with ANALYSIS.md's "earliest future deadline" rule, and Mission Control pairs it with "Claude 5h · 100% left", but MC may prefer "next reset that returns allowance you're missing" (here Fri 18:00) as the headline rule. Worth a one-line decision before implementation.

## 4. Comparative recommendation

**Mission Control** is the strongest fit for the stated priority: the 87px remaining figures and 49px next-reset read from across a room, and the dark rail makes the display unmistakably a different object from paper. Tradeoffs: the large black field is the biggest physical-contrast unknown (ANALYSIS already flags the on-device check), and its Codex reset labelling is the weakest (minor finding above). **Harbour Almanac** is the best all-rounder if the panel's black field disappoints — equal data completeness, warmer, with the clearest supporting block. **Departure Board** wins if MC values comparing all four windows in one scan; its next-reset is only a table row, so it trades the headline priority for completeness. Conservatory is the most beautiful but has the least prominent next-reset; Balance is the boldest object but the most sparse in labelling; Studio Companion is the most charming and would make a fine rotation member rather than the daily default. Given twelve reusable artworks, the practical answer is Mission Control's layout as default with Harbour as the light-mode alternate — but all six are legitimately presentable once F1 is fixed.

## 5. Scope and limitations

Reviewed: PRODUCT.md, ANALYSIS.md, snapshot.json, render.py, craft floor, all 12 `-paper.png` at native size, 3 `-inks.png` spot-checks plus a pixel-count verification over text regions, and manifest.json. Not done (out of scope or impossible here): no physical-panel viewing — the dark-field contrast and the real-world visibility of F1's fringing are inferred from pixel data, not optics; no review of the artwork prompts or the remaining 9 inks files individually (F1 is systematic, from shared `finish()` code, so it affects all 24 outputs); no live-data or scheduler assessment beyond what ANALYSIS documents. No files were modified. The craft floor's web-specific checks (motion, states, browser surfaces) don't apply to static panel images and were not forced onto the brief.
