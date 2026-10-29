# Visual council review

Branch: `fix/render-council-review`

## Acceptance criteria

- [ ] Independent council inspects all six artworks, four displays, and five fixture states using rendered images.
- [ ] Findings identify affected images and actionable geometry, readability, or semantic defects; preferences and physical limitations are distinguished.
- [ ] Remediate accepted findings in one batch, preserving the original normal artwork unless a demonstrated defect requires a deliberate correction.
- [ ] Generate a fresh, reproducible set of all 120 validation images plus any new regression scenarios required by findings.
- [ ] Run the council again against the updated images, record every finding's disposition and final judgments.
- [ ] Tests, format/lint and secret scan pass; documentation and revision history reflect the result.

## Sequence

1. [ ] Freeze current previews and run independent composition, typography, and data-state reviews.
2. [ ] Synthesize findings, implement corrections and focused regression checks.
3. [ ] Regenerate validation images and run independent final review.
4. [ ] Record evidence, publish revisions, and report remaining physical-test limitations.

The renderer and synthetic fixtures are the review target. No credentials or collector changes. Preserve the approved artwork and hardware behavior. Demonstrated defects on the original 5.7-inch panel may receive targeted corrections; retain explicit before/after evidence and the old golden hashes rather than silently replacing baselines.

## Council execution

At MC's explicit model restriction, the initial Claude tasks were interrupted before synthesis. Their artifacts are excluded. Both review rounds use only `gpt-6-astra` or `gpt-6.1-sol` independent subagents. Round 1 covers every normal image three ways, with the five-state matrix covered across the reviewers. Source PNGs and a frozen 120-frame manifest remain under `state/multi-display/previews/` and `state/council/round-1/manifest.json`.
