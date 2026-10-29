# Live artwork plates

Six non-destructive ImageGen edits of `designs/integrated-v2/*-concept.png` remove
all frozen lettering while preserving each scene and its information surfaces.
`*-master.png` preserves the generated output; `*-plate.png` is the 1200×896
reusable RGB plate. Exact prompts and repository-relative source paths are in `prompts.json` and the
PNG `impeccable:prompt` metadata. Generated with the built-in ImageGen tool.

`inky_frame/live.py` projects deterministic current text into these surfaces and
exports an indexed image for the detected display profile. The original 600×448
UC8159 output retains its seven colour indexes; experimental Spectra 6 profiles
use six indexes at 600×400, 800×480, or 1600×1200, with proportional fitting.
Text is rasterized for the target; the original illustration detail is 1200×896. The Pi
receives plates and fonts, not the larger masters. No usage figures are baked
into these plates. Fresh snapshots and rendered display state are ignored by git.

Live typography uses Bangers, DM Serif Display, and Barlow Condensed SemiBold;
the fonts and OFL licences are preserved in `designs/fonts/`.
