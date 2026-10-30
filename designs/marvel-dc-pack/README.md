# Marvel versus DC — artwork study

**Two completed mockups from six planned concepts.** The built-in image generator
rejected the other four outputs, including a second pass using calmer, fully
clothed portrait compositions. The six-image set is incomplete; blocked concepts
are preserved as briefs, not represented by placeholder artwork.

## Completed artwork

| 03 / Gods of Thunder | 04 / Fourth Wall |
| --- | --- |
| ![Thor and Wonder Woman above two inscribed balance panels](03-gods-of-thunder-mockup.png) | ![Deadpool and Harley Quinn with usage figures inside speech balloons](04-fourth-wall-mockup.png) |
| Thor × Wonder Woman: heroic portraiture, carved stone panels and gold/cobalt framing. | Deadpool × Harley Quinn: expressive comic banter and oversized speech balloons. |

Open [the local comparison gallery](index.html) to inspect both images at up to
600 CSS pixels wide. Native generated files are preserved; browser scaling is
not an exact 600 × 448 export or a physical-size simulation.

## Concepts still blocked

| Concept | Pairing | Intended integration |
| --- | --- | --- |
| 01 / Worlds Collide | Iron Man × Superman | Technology and shield-shaped comic caption plaques. |
| 02 / Rooftop Rivals | Spider-Man × Batman | Large city billboards framed by web lines and a cape. |
| 05 / Mystic Crossover | Doctor Strange × Zatanna | Clean text discs within ornate magic portals. |
| 06 / Cosmic Collision | Silver Surfer × Green Lantern | Cosmic ribbons and green energy constructs. |

The final failures reported output-moderation category `other`, without a more
specific explanation. The first Mystic Crossover attempt was flagged `sexual`;
its revised prompt specified waist-up, fully clothed magician portraits and was
also rejected, under `other`. No conclusion about the underlying cause is assumed.
Request identifiers and per-concept outcomes are recorded in [generation.json](generation.json).
No alternate backend was used.

## Sample data and production status

These are generated comic fan-art mockups with fixed example values from the
[28 October 2026 snapshot](../data/snapshot.json): Claude **20%** weekly allowance
remaining and Codex **95%**. The reset captions are Friday 18:00 and Wednesday
14:49 respectively, in Asia/Singapore. They are historical examples, not current
usage. `WEEK LEFT` means weekly allowance remaining.

Colours are RGB concept colours, not a validated seven-ink palette. Neither
image is installed on the Pi. Clean plates, dynamic text, additional usage and
freshness states, palette conversion and physical testing remain production work.

## Prompts and theme controls

All images were generated with the **built-in image_gen tool**. The original six
briefs and exact prompts are in [prompts.json](prompts.json). The safer second-pass
prompts are in [revised-prompts.json](revised-prompts.json). Gods of Thunder uses
the revised portrait brief; Fourth Wall uses its original comic-page brief.

The [theme-control direction](../../docs/artwork-themes.md) records the intended
D-button switch between Original, Street Fighter, and future themes. A/B/C and
automatic rotation must stay within the selected theme. The user chose to finish
the artwork mockups first and implement theme switching in the next round.
