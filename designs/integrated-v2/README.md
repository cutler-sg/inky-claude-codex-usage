# Integrated artwork revision

Six complete ImageGen compositions inspired directly by the project product photographs: the full-screen pop-comic portrait and the engraved octopus circuit-board illustration. The numbers are part of the illustration, as requested, rather than an adjacent dashboard.

## Concepts

- **Pop Comic:** weekly balances become thought balloons; reset and scope figures become comic captions.
- **Budget Kraken:** tentacle coils enclose balances, with engraved reset ribbons woven through the arms.
- **Reactor Room:** balances are painted onto reactor housings, with session and scoped allowance on mechanical gauge faces.
- **Night Market:** the city is the interface: shop signs, awnings, lanterns, and a shutter carry the figures.
- **Quota Moth:** balances are wing markings; smaller figures follow botanical specimen ribbons.
- **Cosmic Pinball:** balances occupy the playfield's scoring islands; rails, inserts, and the apron hold the reset details.

Each `*-master.png` is the original generated image. `*-concept.png` is an exact 600×448 export in the generated colours. `*-inks.png` is an indexed seven-slot print proof. `index.html` is a self-contained comparison page; `preview.html` uses absolute local image paths for T3's automatic image inlining. Exact prompts and reference paths are in `prompts.json`; prompts are also embedded in PNG metadata.

These are **concept mockups with baked-in numbers**, deliberately authorized for the artwork exploration. They use the earlier frozen snapshot, not current usage. No image has been displayed on the Pi and no scheduler installed. Digital colours are not a calibration of the physical display.

## Dynamic rendering after selection

Keep the composition's information-bearing surfaces: speech balloon interiors, tank paint, shop signs, wing markings, or playfield inserts. Produce a matching clean artwork plate with those areas blank, then draw live values into the same shapes, matching the lettering and applying perspective/curved baselines where required. Fixed lettering and scene detail remain in the artwork; changing numbers and reset times are deterministic overlays. This preserves the integration rather than reverting to a separate sidebar.

The readable headline values are 20% Claude weekly remaining and 95% Codex weekly remaining. Claude's already-full 5h session is 100%; Fable is 58% remaining; Codex has two banked reset credits and zero currently applicable. The 17:50 session reset does not replenish the binding weekly allowance, which resets Friday at 18:00.
