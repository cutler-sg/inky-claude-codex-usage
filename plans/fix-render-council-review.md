# Visual council review

Branch: `fix/render-council-review`

## Acceptance criteria

- [x] Independent council inspects all six artworks, four displays, and five fixture states using rendered images.
- [x] Findings identify affected images and actionable geometry, readability, or semantic defects; preferences and physical limitations are distinguished.
- [x] Remediate accepted findings, preserving the original artwork with deliberate corrections to demonstrated typography defects. Final conditions received a focused correction and acceptance pass.
- [x] Generate a fresh, reproducible set of all 120 validation images plus new regression scenarios: 312 total.
- [x] Run the council again against the updated images, record every finding's disposition and final judgments.
- [x] Tests, format/lint and secret scan pass; documentation and revision history reflect the result.

## Sequence

1. [x] Freeze current previews and run independent composition, typography, and data-state reviews.
2. [x] Synthesize findings, implement corrections and focused regression checks.
3. [x] Regenerate validation images and run independent final review.
4. [x] Record evidence and physical-test limitations in the review document and revision history.

The renderer and synthetic fixtures are the review target. No credentials or collector changes. Preserve the approved artwork and hardware behavior. Demonstrated defects on the original 5.7-inch panel may receive targeted corrections; retain explicit before/after evidence and the old golden hashes rather than silently replacing baselines.

## Council execution

At MC's explicit model restriction, the initial Claude tasks were interrupted before synthesis. Their artifacts are excluded. Both review rounds use only `gpt-6-astra` or `gpt-6.1-sol` independent subagents. Round 1 covers every normal image three ways, with the five-state matrix covered across the reviewers. Source PNGs and a frozen 120-frame manifest remain under `state/multi-display/previews/` and `state/council/round-1/manifest.json`.

## Completed evidence

- Three independent final PASS verdicts; the second round's residual alignment conditions were corrected and explicitly rechecked. See [review record](../docs/visual-council-review.md).
- All 312 final PNGs validated: 144 unchanged from the fully reviewed second round, 144 revised geometry frames rechecked across every state/profile, and 24 new fallback frames reviewed for semantics.
- 147 tests, Ruff check/format, and whitespace checks pass. Old golden hashes remain archived; 26 original-profile cases deliberately change, four retain exact pixels, all 30 retain identical palettes.
- Isolated Pi validation: 18 original-size frames and one large frame pass on Pillow 11.1.0, peak 75.4 MiB. Existing Night Market selection retained during controlled deployment; its 34.17-second refresh matches an independent render of current usage. Collector/timer and hardware/button code unchanged.
- Gitleaks scans the branch without suppressions. No credentials or protected configuration touched.
