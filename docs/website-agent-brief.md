# Bootstrap prompt for the website agent

Copy the prompt below into the agent working on the personal website.

---

Prepare a project write-up for my personal website about **Inky Claude/Codex Usage
Display**. Start by inspecting the website's existing project pages, writing style,
asset pipeline, and publishing conventions. Then inspect the project repository:

**https://github.com/cutler-sg/inky-claude-codex-usage**

Read `README.md`, `docs/hardware-and-operations.md`, `PRODUCT.md`, and `DESIGN.md`
for the current implementation. The design studies and plans are historical;
distinguish their proposals from what the current code actually does. If you have
a local checkout, verify its location and update it before using it as evidence.

## Find the artwork first

All paths below are relative to the repository root. The six approved mockups are:

- `designs/integrated-v2/02-budget-kraken-concept.png`
- `designs/integrated-v2/01-pop-comic-concept.png`
- `designs/integrated-v2/03-reactor-room-concept.png`
- `designs/integrated-v2/04-night-market-concept.png`
- `designs/integrated-v2/05-quota-moth-concept.png`
- `designs/integrated-v2/06-cosmic-pinball-concept.png`

These are the images showcased near the top of the README. Each is exactly
600×448. The matching `*-master.png` files in the same directory are the original
higher-resolution compositions; prefer those for a large website hero. Matching
`*-inks.png` files are indexed seven-colour proofs. Inspect the images before
choosing crops. **Budget Kraken** and **Pop Comic** are strong hero candidates;
keep all six available for a gallery.

- `assets/live/*-plate.png`: clean 1200×896 artwork with the lettering removed;
  deterministic live numbers are projected into these surfaces by the Pi renderer.
- `assets/live/*-master.png`: original clean-plate generations.
- `designs/integrated-v2/prompts.json`: exact prompts and visual references for the
  six compositions.
- `assets/live/prompts.json`: exact clean-plate edit prompts and provenance.
- `designs/artwork/01-original.png` through `12-original.png`: the earlier artwork
  study. Its rendered layouts are in `designs/mockups/`, and its prompts are in
  `designs/prompts/artwork.json`. Use it only if explaining the design evolution.
- `pimoroni-inky-impression/`: manufacturer photos, drawings, and technical
  references. These are not photos of my finished project. Read `THIRD_PARTY.md`
  before considering their reuse; their redistribution rights are not established.

Reuse the existing artwork instead of generating replacements. Copy and optimize
selected images through the website's normal asset pipeline, retain their aspect
ratio and useful detail, and write descriptive alt text. Link to the GitHub repo.

## Tell the project accurately

This is a personal experiment: a Raspberry Pi Zero 2 W driving the original,
discontinued Pimoroni Inky Impression 5.7-inch seven-colour 600×448 display.
Claude and Codex remaining allowance and reset information become part of the
artwork itself: speech balloons, tentacle coils, reactor tanks, street signs,
moth wings, and a pinball playfield.

The current Pi collects directly from CLIProxyAPI over verified HTTPS; the owner's
installation reaches the private proxy through Tailscale. A systemd timer collects
every ten minutes. CLIProxyAPI holds and refreshes vendor OAuth tokens, while the
Pi holds a protected management credential and stores a sanitized usage snapshot.
The earlier Mac collection/sync architecture is historical, not a current dependency.

A separate Pi service renders the selected artwork and listens to physical buttons:
A previous, B next, C random, D Budget Kraken. A full refresh takes about 34 seconds;
the image remains visible without power. Presses during a refresh coalesce into
the latest selection. Failed/old observations are marked stale instead of implying
that allowance has replenished.

The illustrations were created with built-in ImageGen. The live figures are drawn
deterministically in code, with perspective transforms matching the original
information surfaces. Preserve that distinction when describing the build.

## Editorial boundaries

- The showcase mockups contain frozen example readings, not current account data.
- Digital mockups are not physical-panel photographs. Physical e-ink colours are
  more restrained than the RGB previews. Do not invent a finished-device photo.
- Usage percentages are subscription quota windows, not token counts or money.
- Do not publish credentials, private network endpoints, live account snapshots,
  account identifiers, or local machine paths. No secret access is needed for this article.
- Do not invent build duration, battery life, costs, performance claims, or a more
  elaborate backstory than the evidence supports.

Lead with the artwork and the useful desk object. Keep detailed installation and
protocol material behind a link to the repository's technical guide. Produce the
article/project page using the website's established conventions and verify its
layout and images before handing it back.
