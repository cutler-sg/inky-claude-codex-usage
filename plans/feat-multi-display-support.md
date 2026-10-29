# Adapt the live gallery to additional Inky Impression displays

Status: approved by MC on 2026-10-29; completed and verified.
Branch: `feat/multi-display-support`.

## Outcome and acceptance criteria

- [x] Preserve the original 5.7-inch panel's rendered pixels, palette, button mapping,
  refresh serialization, selection persistence, and usage/staleness behavior.
- [x] Detect the original panel and the three current Spectra 6 sizes by EEPROM
  identity, with resolution and driver cross-checks. Reject unknown/mismatched boards.
- [x] Produce hardware-free previews for all six artworks at all four resolutions.
- [x] Use the appropriate seven- or six-colour palette and verify the vendor's
  image-to-buffer mapping, including blue/green and the absence of orange on Spectra 6.
- [x] Visually review all 24 normal-state previews, plus representative edge states,
  at native pixels; preserve information surfaces without cropping or distortion.
- [x] Exercise detection and display/gallery behavior with hardware doubles; retain
  the existing checks and test the real 5.7-inch device only after offline checks pass.
- [x] Document the new panels as experimentally supported and rendering-tested;
  physical colour, refresh, and button behavior remain unverified on those panels.

## Verified facts

The vendor product page identifies all three current models as **six-colour
Spectra 6**, rather than the original seven-colour technology. Resolution alone
cannot identify a driver: older seven-colour 7.3-inch boards also use 800×480.

The already-pinned `inky==2.6.0` supports these EEPROM variants. The ignored local
vendor checkout is also tagged v2.6.0. No library upgrade is needed for this scope.

| Proposed profile | Resolution | EEPROM variant(s) | Vendor driver | Button A/B/C/D (BCM) |
| --- | --- | --- | --- | --- |
| `impression-5.7` | 600×448 | 14 | `inky_uc8159` | 5 / 6 / 16 / 24 |
| `spectra6-4.0` | 600×400 | 25 | `inky_e640` | 5 / 6 / 16 / 24 |
| `spectra6-7.3` | 800×480 | 22, 26 (AC) | `inky_e673` | 5 / 6 / 16 / 24 |
| `spectra6-13.3` | 1600×1200 | 21, 27 (AC) | `inky_el133uf1` | 5 / 6 / 25 / 24 |

The 13.3-inch driver uses GPIO16 for a display chip-select. Keeping our existing
global button map would therefore conflict with display operation. The vendor's
Spectra button example explicitly specifies GPIO25 for button C on this model.

Current hard-coded assumptions are in:

- `inky_frame/__main__.py`: `read_display()` rejects everything except variant 14;
  image loading happens before display detection; skip hashes omit panel identity.
- `inky_frame/images.py`: preparation, margins, and the sample target 600×448.
- `inky_frame/live.py`: artwork coordinates use a 600×448 design space, plates are
  1200×896, rendering scale is 2, and `Canvas.finish()` uses seven indexed inks.
- `inky_frame/gallery.py`: `show_frame()` validates only the original dimensions
  and palette; `Player` renders without a target; buttons and refresh interval
  are fixed globally.
- `scripts/deploy.sh`: checks only the UC8159 import, and currently excludes master
  image files. Existing 1200×896 clean plates are sufficient for the initial scope.

## Proposed design

Use one small immutable display-profile structure, shared by hardware detection,
image preparation, rendering, frame validation, and button setup. It holds the
resolution, palette family, allowed EEPROM variants, expected driver, and buttons.
Keep this to four explicit profiles; do not introduce a plugin framework or add
every display supported by the vendor library.

Hardware operations select a profile from EEPROM, validate its dimensions, then
let `inky.auto.auto(ask_user=False)` select the vendor driver. Cross-check the
returned resolution/driver. The gallery reads metadata without owning display
GPIO; its existing isolated worker remains the only display owner, under the
refresh lock. Revalidate the worker's target before sending a frame. Unknown
hardware must fail with an actionable error rather than silently use 600×448.

Offline commands accept an explicit `--profile`; preserve the existing 5.7-inch
default when no hardware is involved. Add a hardware-free gallery rendering entry
point with an explicit sanitized fixture and fixed time. This is the same renderer
used on the Pi, rather than a separate simulation layout. Hardware writes always
use the detected identity; an offline profile cannot force an incompatible driver.

Keep the 600×448 composition coordinates as the artwork's logical space. For other
panels, uniformly scale the clean plate and its text surfaces together into a
centered content rectangle. Render text from fonts for the target raster before
final quantization. Do not stretch, crop, or enlarge an already-quantized 600×448
frame. The original profile must retain its current rendering operations exactly.

The initial fit policy is **contain**, preserving every integrated information
surface. Expected content areas, rounded to pixels:

| Panel | Approximate content rectangle | Remaining space |
| --- | --- | --- |
| 5.7-inch | 600×448 | None; existing output |
| 4.0-inch | 536×400 | About 32 px on each side |
| 7.3-inch | 643×480 | About 78–79 px on each side |
| 13.3-inch | 1600×1195 | About 2–3 px above/below |

Start with plain, palette-safe margins. Inspect readability before adding any
art-specific exceptions. If a composition needs one, change only that profile's
presentation; do not redesign the approved 5.7-inch art. The 13.3-inch version can
have sharp text but its source illustration still has 1200×896 detail; label this
limitation rather than claiming higher-resolution source art.

Keep the original seven-colour conversion unchanged. Add a separate six-colour
conversion using the driver's expected sequential image palette: black, white,
yellow, red, blue, green. Spectra drivers map those image indices to hardware
codes `[0, 1, 2, 3, 5, 6]`; our code must not apply that remapping twice. Orange
in the source illustration is quantized into available colours. Test the actual
v2.6.0 `set_image()` conversion without display I/O, using a colour-swatch fixture,
as well as validating our PNG palettes. Preserve no-dither live lettering.

Keep the conservative 40-second minimum between refresh starts and the vendor's
normal refresh mode for every profile initially. The existing worker serialization
already waits for completion if a refresh exceeds that interval. Do not infer
refresh duration from diagonal size or enable faster waveforms. Retain retry,
latest-selection coalescing, and debounce behavior. Make successful-frame hashes
include profile, dimensions, mode, palette, pixels, and relevant settings, so a
different panel cannot incorrectly inherit an unchanged-frame decision. Expect
one refresh when migrating the old hash schema; preserve state/selection data.

## Implementation sequence

1. [x] **Freeze the original behavior.** Create deterministic sanitized usage
   fixtures and a fixed timestamp. Capture all six legacy render outputs before
   refactoring, including palette data. Cover normal, stale/unavailable, long
   labels, missing credit/reset information, and allowance boundaries. Compare
   decoded pixels and palettes, not PNG compression bytes. Record Pillow version;
   run before/after comparisons in the same environment.
2. [x] **Add profiles and detection.** Implement the small profile table and pure
   identity resolver; test all supported EEPROM variants, wrong dimensions,
   absent/unknown identities, and 7.3-inch legacy/Spectra ambiguity. Keep hardware
   imports out of offline rendering. Test the 13.3-inch button map against its
   reserved display pins before GPIO requests.
3. [x] **Adapt rendering and image commands.** Thread the profile through
   `prepare`, `sample`, `Canvas`, and gallery rendering/validation. Preserve default
   call behavior for existing users. Implement aspect-preserving transforms and
   the Spectra palette. Add offline profile selection and deterministic preview
   generation, including photographs, rotation, transparency, and indexed input.
4. [x] **Integrate the gallery/display path.** Detect the profile at startup and
   again in the isolated display worker, select its buttons, check frame dimensions
   and palette, update hashes/status, and report detected hardware in `info`.
   Ensure the one-shot SSH image path prepares for the detected target too. Extend
   deployment's import checks without changing installed library versions.
5. [x] **Render, inspect, and correct.** Generate the 24 normal-state images and
   targeted edge-state images under ignored `state/` using synthetic data. Inspect
   a labelled comparison overview and native-pixel crops of headlines, reset
   labels, scope/credit text, and timestamps. Check contrast, legibility, correct
   colours, alignment with illustration surfaces, margins, and clipping. Fix all
   observed issues in one pass, then rerender and confirm. Keep findings and
   representative non-secret previews suitable for review.
6. [x] **Validate and document.** Require legacy pixel/palette equality, correct
   dimensions/allowed colours on all profiles, exact swatch-to-driver mapping, and
   existing lock/retry/coalescing tests to pass. Measure worst-case render time and
   peak memory for 1600×1200; bound intermediate canvases and avoid arbitrary 2×
   supersampling at that size. Update the README/support matrix and operations
   guide to distinguish physical testing from simulated rendering.
7. [x] **Controlled 5.7-inch rollout.** Only after the offline evidence passes,
   record the deployed version and back up selection/status, deploy to the existing
   Pi, verify EEPROM/profile, refresh success, unchanged-image skip, and continued
   collection/gallery operation. Preserve its selected artwork; use any temporary
   button/selection checks reversibly. Measure on-Pi render resources and have a
   rollback to the previous deployed source ready. Software success is not optical
   confirmation; record any physical observation separately. New-size hardware
   validation remains outstanding until someone has those devices.

## Scope boundaries

MC approved implementation and controlled deployment on 2026-10-29.
Credential handling, artwork regeneration, and website changes remain outside scope.

Initial implementation excludes other legacy 4.0-/7.3-inch seven-colour models,
new layouts that relocate information outside the illustrations, automatic
slideshows, per-panel waveform tuning, and claims of measured physical colour on
unowned hardware. Those can be separate follow-ups if justified by evidence.

## Sources inspected

- [Current product specification and revisions](https://shop.pimoroni.com/products/inky-impression?variant=56039376912763)
- [Pimoroni getting-started guide](https://learn.pimoroni.com/article/getting-started-with-inky-impression)
- [Inky v2.6.0 EEPROM/driver routing](https://github.com/pimoroni/inky/blob/v2.6.0/inky/auto.py)
- [Spectra 6 button example, including 13.3-inch exception](https://github.com/pimoroni/inky/blob/v2.6.0/examples/spectra6/buttons.py)
- [4.0-inch driver](https://github.com/pimoroni/inky/blob/v2.6.0/inky/inky_e640.py)
- [7.3-inch driver](https://github.com/pimoroni/inky/blob/v2.6.0/inky/inky_e673.py)
- [13.3-inch driver](https://github.com/pimoroni/inky/blob/v2.6.0/inky/inky_el133uf1.py)
- [Original UC8159 driver](https://github.com/pimoroni/inky/blob/v2.6.0/inky/inky_uc8159.py)

## Completed verification (2026-10-29)

- 125 tests pass. All 30 committed baseline pixel and palette hashes match on
  local Pillow 12.3.0. The same 30 before/after renders also match exactly on the
  Pi's Pillow 11.1.0, using an isolated candidate directory before deployment.
- Generated 120 synthetic images: six artworks × four profiles × five states.
  Inspected all 24 normal-state frames in comparison sheets, native small-panel
  images and large-panel text crops, plus stale/unavailable/missing/boundary views.
  Split unavailable provider headings on new profiles after the initial review;
  rerendered the affected previews and confirmed the smaller headings fit better.
  Normal previews retain aligned text surfaces and complete, uncropped artwork.
- The actual pinned vendor `set_image()` conversion passed colour-swatch checks
  for every profile on the Pi, with constructors bypassed and no GPIO/SPI I/O.
  Confirmed native mappings 0–6 for UC8159 and 0/1/2/3/5/6 for Spectra 6.
- Rendering every 1600×1200 artwork on the Pi took 14.06–17.47 seconds; peak process
  RSS was 88.7 MiB after all legacy and large-format renders. Local batch peak was
  137.1 MiB. No arbitrary 2× large-panel intermediate is allocated.
- Existing deployed source and selection/status were backed up under
  `/tmp/inky-profile-audit/` on the Pi. The candidate was tested separately, then
  the gallery was stopped gracefully before deployment and restarted afterward.
  Installed vendor dependencies remained at their existing versions.
- The detected live profile is `impression-5.7`, variant 14, with unchanged button
  GPIOs. Quota Moth remained selected and completed its refresh at
  2026-10-29 09:50:55 +08 in 34.43 seconds. Its saved pixels/palette and digest match
  an independent render of the latest on-device sanitized usage snapshot.
- Gallery and usage timer are active, both providers are healthy, and the unchanged
  frame check skips a second physical refresh. No new optical-verification claim
  is made; the three unowned physical sizes remain experimentally supported.
- README now links the original discontinued product and the exact product
  variants for each current size. Hardware, design, product, and plate notes
  describe profile-dependent behaviour and the limits of software-only evidence.
