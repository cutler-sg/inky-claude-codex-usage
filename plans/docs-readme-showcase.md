# README showcase

Branch: `docs/readme-showcase`. Updated: 2026-10-28.

## Acceptance criteria

- Show all six previously generated integrated mockups near the top of the public README.
- Explain the project, physical controls, live-data integration, and hardware briefly.
- Label digital mockups and frozen example values accurately.
- Move detailed hardware, installation, collector contract, operations, troubleshooting,
  development, and historical design notes into a linked technical guide.
- Preserve technical content and repair relative links and incoming README anchors.
- Reuse the committed images; validate Markdown rendering and image/link resolution.
- Commit and publish the documentation change to the existing public repository.

## Tasks

- [x] Read the current README, references, and six mockup images.
- [x] Build the showcase README and extract the technical guide.
- [x] Check rendering and links, commit, and publish.

## Verification

- README reduced from 248 to 74 lines, with all six original concept PNGs linked
  near the top in a two-column gallery; each opens the full 600×448 image.
- All nine original technical sections are preserved in the new technical guide,
  with relative links relocated and the incoming study README anchor repaired.
- GitHub Markdown API render inspected at 728px and 360px: six images loaded at
  the correct native size, no page overflow and no table overflow.
- All local Markdown links and anchors resolve. Original section text was checked
  against the prior README, allowing only link relocation and two navigation edits.
- Documentation-only change; no runtime code, new image assets, or dependencies.
