# Integrated artwork revision

Branch: `feat/usage-designs`. Updated: 2026-10-28.

## Acceptance criteria

- Use the actual project product photos as visual references: comic close-up, engraved octopus, saturated halftone colour.
- Make the information part of the picture, not an adjacent dashboard or small framed illustration.
- Use built-in ImageGen to produce complete artwork-and-type mockups, including the illustrative changing numbers.
- Deliver six original integrated compositions at exactly 600×448 plus higher-resolution masters and exact prompts.
- Preserve the first study as history. No Pi display or live scheduler changes in this review phase.

## Tasks

- [x] Inspect the four supplied reference photos and contrast with the first study.
- [x] Generate six integrated artwork-and-type mockups using the actual image references.
- [x] Inspect lettering, numeric accuracy, composition, and native-resolution legibility; export exact-size proofs.
- [x] Publish the revised comparison page and commit the new study.

## Verification

- Six high-resolution masters saved with exact prompts; twelve exact 600×448 concept/proof exports.
- Every indexed proof uses the seven colour slots; no claim of physical colour calibration.
- All six native concept PNGs visually inspected; supporting values checked against the frozen snapshot.
- All twelve concept/proof selections exercised at 728px and 360px; native image dimensions correct and no page overflow, including 1:1 mode.
- Ruff lint and formatting passed for the export script. Gallery hook warnings were fixed by using the documented font alias and palette fallbacks; no suppressions.
- No production renderer change, usage fetch, credential access, Pi update, or scheduler installation.

## Direction

- Prioritize a full-frame authored composition: pop-comic, engraved cephalopod, pulp space, neon street, botanical label, mechanical print.
- Baked-in numbers are authorized for the visual exploration. Preserve the distinction between a concept image and the later dynamic text renderer.
- Keep the frozen 17:43 snapshot for direct comparison: Claude weekly20% remaining, Codexweekly95%, Claude5h100%, Fable58%, sessionreset17:50SGT, weeklyresetFri18:00, Codexreset4Nov14:49, twoCodexresetsbanked/zeroapplicable.
