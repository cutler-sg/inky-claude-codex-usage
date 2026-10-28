# Usage display concepts

Updated: 2026-10-28. Branch: `feat/usage-designs`, based on the verified initial setup.

## Acceptance criteria

- Explain the actual Claude/Codex collector and discrepancies with older documentation.
- Define quota, reset, credit, freshness, and error semantics without inventing remaining tokens or money.
- Deliver six substantially different 600×448 compositions using the seven panel colours.
- Produce twelve reusable ImageGen artworks and preserve prompts/provenance.
- Show exact-pixel PNGs and an interactive comparison gallery before changing the live screen.
- Propose a ten-minute update architecture with safe offline behaviour.

## Tasks

- [x] Read the collector, watcher documentation, display renderer, and safe usage cache.
- [x] Write requirements, data mapping, refresh proposal, and explicit open decisions.
- [x] Generate twelve artwork assets using the built-in image tool; preserve originals and embedded prompts.
- [x] Render six exact-size, seven-colour mockups with deterministic text: two art editions and two palette proofs per design.
- [ ] Inspect all variants, verify dimensions/palette, and publish comparison gallery.
- [ ] Commit artifacts and leave deployment deferred until the mockups are reviewed.

## Constraints and decisions

- No credential files read and no collector main() invocation: it also reads an unrelated OpenRouter secret.
- Use only the non-secret cached usage for examples; label the frozen capture time.
- The existing sample remains on the Pi until design selection.
- A snapshot with no Codex session window must show that absence, never invent a 5h value.
- Artwork can rotate independently of the information grid. Labels and numbers stay deterministic.

## Verification

- Twenty-four PNGs verified at 600×448, indexed to the seven supported slots.
- Neutral text pixels snap to black/white before palette conversion to prevent coloured fringes.
- All 24 design/edition/palette selections exercised in browser previews at 728px and 360px; no page overflow, including the 1:1 scroll mode.
- Ten existing display/image tests passed; Ruff lint and format checks passed.
- Embedded-prompt provenance scan: 36 artwork/screen rasters, zero missing.
- Independent Fable review and a separate verdict round recorded under `designs/review/`.
- No collector main() execution, credential access, new network service, or Pi screen update in this phase.
