# A small stand for Inky

Thirteen minimalist desk-stand concepts, built in OpenSCAD for the original
**Pimoroni Inky Impression 5.7-inch** and a rear-mounted Raspberry Pi Zero 2 W.
The brief was simple: let the screen rest in a slot, lean it back a little, and
lead the USB cable towards the back of the desk.

We explored three directions: triangular supports, semicircular backs, then a
broader set of rounded and open shapes. Every image below comes from the actual
CAD geometry. The screen graphic and rear electronics are simplified references.

| Half-drum: a continuous rounded back | Teardrop: a tapered footprint |
| --- | --- |
| ![Half-drum with the screen, rear Pi and USB route](../designs/stands/renders/06-rear.png) | ![Teardrop with the screen, rear Pi and USB route](../designs/stands/renders/12-rear.png) |
| [Download Half-drum STL](../designs/stands/stl/06-half-drum.stl) | [Download Teardrop STL](../designs/stands/stl/12-teardrop.stl) |

**These are concept models, not physically validated prints.** Both downloadable
STLs are closed, connected meshes, but the slot, PCB contact points and component
clearances still need checking against the assembled device. The stand models
target the original 5.7-inch panel only; the application's support for other
display sizes does not make these stands compatible with those boards.

## What stayed consistent

The [saved manufacturer drawing](../pimoroni-inky-impression/inky-impression-5.7-drawing.png)
gives a **125.4 × 99.5 mm** board outline. The quoted **9 mm** product depth includes
the display and header, so we did not use it as the thickness of the lower edge
that sits in the slot. The rear product photos also show a flex ribbon near the
bottom centre and USB sockets facing down from the Pi.

To compare shapes fairly, we kept the same reference screen, camera positions,
12° backward lean and approximately 9 mm seat height throughout. Each concept has:

- A provisional **5.2 mm slot**, with low front lips below the reference image.
- Space around the bottom-centre ribbon, rather than a continuous clamping edge.
- Access to the side buttons and rear-mounted Pi.
- A rear cable route with an **8 mm wide, 4 mm high underside channel**. The cable
  can be laid into the channel without threading its connector through a hole.

Those are design allowances, not measured fit guarantees. In particular, the
channel is not a strain-relief clamp, and the cable bend shown is illustrative.

## Direction 1: triangles and low bases

We started with the simplest structural shapes: a wedge, two fins, an open frame
and a shallow plinth. This established how much of the stand should be visible
from the front and how much access to leave behind the screen.

| 01 / Wedge | 02 / Twin fins |
| --- | --- |
| ![Wedge stand](../designs/stands/renders/01-stand.png) | ![Twin fins stand](../designs/stands/renders/02-stand.png) |
| Broad, solid base with the most visual mass. | Two triangular feet connected by one rear bar. |
| **03 / Open triangle** | **04 / Pebble cradle** |
| ![Open triangle stand](../designs/stands/renders/03-stand.png) | ![Pebble cradle stand](../designs/stands/renders/04-stand.png) |
| Triangular frames reduce material and expose the space beneath the screen. | A rounded low plinth with small rear supports. |

The first renders showed that a tall retaining lip would obscure the bottom of
the image. We lowered it and kept the taller support behind the screen. The
centre relief also became a shared feature, preserving room for the ribbon.

## Direction 2: semicircular backs

The next request was for something rounder, particularly a semicircular back.
We tried the curve in two planes: a half-moon side profile and a semicircle in
the footprint viewed from above.

| 05 / Half-moon feet | 06 / Half-drum |
| --- | --- |
| ![Half-moon feet stand](../designs/stands/renders/05-stand.png) | ![Half-drum stand](../designs/stands/renders/06-stand.png) |
| Semicircular side supports joined by a low rear bridge. | A continuous domed back over a semicircular footprint. |

![Crescent stand with an open semicircular rear rail](../designs/stands/renders/07-stand.png)

**07 / Crescent** combines half-moon supports with an open semicircular rear rail.
It keeps the curved outline while leaving more of the middle empty.

The **Half-drum** became the default model and the first requested STL export.
Its continuous back makes the shape read as one object. The cable drops through
an opening into the underside channel instead of passing through the solid dome.

## Direction 3: six focused alternatives

The final exploration mixed rounded triangles, open frames and simple solid
forms. The screen placement stayed fixed so we could judge each silhouette
without changing the viewing angle or scale.

| 08 / Soft delta | 09 / Loops |
| --- | --- |
| ![Soft delta stand](../designs/stands/renders/08-stand.png) | ![Loops stand](../designs/stands/renders/09-stand.png) |
| Compact triangular feet with softened corners. | The same direction opened into frames, with full supports behind the slots. |
| **10 / Capsule** | **11 / Arch** |
| ![Capsule stand](../designs/stands/renders/10-stand.png) | ![Arch stand](../designs/stands/renders/11-stand.png) |
| A low racetrack plinth with two shallow saddles. | A broad curved bridge with an open underside. |
| **12 / Teardrop** | **13 / Pebbles** |
| ![Teardrop stand](../designs/stands/renders/12-stand.png) | ![Pebbles stand](../designs/stands/renders/13-stand.png) |
| Wide at the screen, tapering to a single rounded rear tip. | Two smooth oval feet joined by a low rear bar. |

Soft delta is the most straightforward option in this set. Pebbles gives the
most organic outline. Teardrop was selected for the second STL export: it keeps
a broad front support while narrowing the base behind the display.

During review, we moved the Loops windows farther back so they would not cut
through the supports behind the screen slots. This is why the openings are
smaller than the initial frame study.

## How we built them in OpenSCAD

All thirteen concepts live in one [parametric source file](../designs/stands/stand-concepts.scad).
The models use constructive solid geometry: combine simple solids, then subtract
the shared slot, ribbon clearance and cable route.

| Shape family | Construction |
| --- | --- |
| Wedges and fins | Extruded side-profile polygons. |
| Rounded triangles and loops | Paired 2D offsets soften the corners; an inner profile forms the windows. |
| Rounded bases and Capsule | Hulls of circles form the footprint, then a linear extrusion gives it thickness. |
| Half-moon feet and Arch | Clipped circular or elliptical profiles, extruded across the stand. Arch subtracts an inner opening. |
| Half-drum and Pebbles | Scaled spheres clipped to flat soles. |
| Teardrop | A hull of three circles forms the footprint; an intersection with a side profile creates the sloping top. |

The `panel_space()` transform places the reference board and the slot at the
same angle. `stand()` trims the front lip; the individual models subtract the
shared clearance shapes. Keeping those operations common made it possible to
explore silhouettes without rebuilding the cradle each time.

The main controls are at the top of the file:

| Control | Default | Purpose |
| --- | --- | --- |
| `concept` | `6` | Selects one of the thirteen models. |
| `show_display` | `true` | Shows the reference screen and rear hardware. |
| `show_cable` | `true` | Shows the illustrative cable path. |
| `lean` | `12` | Backward lean in degrees. |
| `slot_width` | `5.2` | Provisional slot width in millimetres. |
| `seat_height` | `9` | Reference seat height in millimetres. |
| `cable_width` | `8` | Cable-channel width in millimetres. |

Changing a parameter does not automatically prove a new configuration fits:
the support spacing, ribbon relief and surrounding body geometry must still be
checked. The green Pi board is a visual clearance proxy, not a detailed assembly model.

### Open and export a model

1. Open `designs/stands/stand-concepts.scad` in OpenSCAD.
2. Set `concept` to the desired number in the Customizer and preview it with F5.
3. Set **both** `show_display` and `show_cable` to `false` for a stand-only export.
4. Render the solid with F6, then use **File → Export → Export as STL**.

The same export can run from the repository root using the CLI:

```sh
openscad --export-format binstl --hardwarnings \
  -D concept=12 -D show_display=false -D show_cable=false \
  -o /tmp/12-teardrop.stl designs/stands/stand-concepts.scad
```

On macOS, if `openscad` is not on PATH, use
`/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD` instead. The models use
millimetres; STL itself carries no unit metadata, so import them as millimetres
in a slicer. Exporting the assembly reference would also export the screen and
cable, which is why both visibility flags must be off.

### Reproduce the previews

The [render script](../designs/stands/render.py) uses the installed OpenSCAD CLI.
It exports front, rear and stand-only views at 1200 × 1000 pixels, using the same
cameras for every concept:

```sh
uv run python designs/stands/render.py                 # concepts 1–4
uv run python designs/stands/render.py --rounded       # concepts 5–7
uv run python designs/stands/render.py --explorations  # concepts 8–13
```

The three local comparison pages let you switch views across a whole collection:

- [Original four](../designs/stands/index.html)
- [Rounded backs](../designs/stands/rounded.html)
- [Six further alternatives](../designs/stands/explorations.html)

GitHub shows these HTML files as source. Clone or download the repository and
open them locally with their sibling `renders/` directory intact. This Markdown
guide is the gallery that renders directly on GitHub.

## Validation and the next physical step

All thirteen stand bodies were evaluated through OpenSCAD's full CGAL exporter
and reported simple solids. The two published STLs were also checked for closed
edges, a single connected mesh and positive volume. We inspected all 39 preview
images; increasing extrusion preview convexity corrected missing faces in the
hollow-model previews without changing the exported geometry.

| Export | Mesh dimensions (W × D × H) | Triangles |
| --- | --- | --- |
| [06 / Half-drum](../designs/stands/stl/06-half-drum.stl) | 111.97 × 55.82 × 27.82 mm | 3,008 |
| [12 / Teardrop](../designs/stands/stl/12-teardrop.stl) | 108.00 × 77.00 × 31.58 mm | 452 |

Mesh validity is only the digital check. Before a complete print, measure the
assembled lower edge, USB plug body, rear protrusions and accessible PCB contact
locations. A small slot coupon is the next useful test. Refine the saddles to
bear on the PCB with compliant liners, clear of the glass, ribbon, pins and
components. Non-slip feet and stability under button presses and cable pull
also need a physical trial. No print settings or material have yet been validated.

See the [source and asset index](../designs/stands/README.md) for the complete
footprint table and files.
