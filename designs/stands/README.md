# Minimal desk stand concepts

See the [illustrated stand guide](../../docs/3d-stands.md) for the design directions,
how we built the models in OpenSCAD, and the remaining physical fit checks.

Thirteen editable OpenSCAD studies for MC's original **5.7-inch Inky Impression** and
rear-mounted Pi Zero 2 W. Open `stand-concepts.scad` in OpenSCAD and select
`concept` 1–13 in the Customizer. The default remains the rounded half-drum (6).
`index.html` compares the original four; `rounded.html` compares the three rounded
alternatives requested after that first study. `explorations.html` compares six
further shapes. Each has front, rear and stand-only views.

| Concept | Footprint (W × D) | Character |
|---|---|---|
| 1. Wedge | 112 × 72 mm | Broad, solid base; most material and visual weight. |
| 2. Twin fins | 100 × 76 mm | Two triangular feet joined at the rear; best starting point. |
| 3. Open triangle | 94 × 76 mm | Slim triangular frames; lighter visual profile, thinner members. |
| 4. Pebble cradle | 116 × 66 mm | Rounded low plinth; shallowest footprint and lowest rear support. |
| 5. Half-moon feet | ~100 × 68 mm | Semicircular side supports and a rounded rear bridge. |
| 6. Half-drum | ~112 × 56 mm | Semicircular footprint with a continuous domed back; preferred rounded direction. |
| 7. Crescent | ~112 × 68 mm | Open semicircular rear rail with half-moon side supports. |
| 8. Soft delta | ~102 × 62 mm | Rounded triangular feet; compact and straightforward. |
| 9. Loops | ~100 × 62 mm | Rounded triangular frames with windows behind the slot supports. |
| 10. Capsule | 116 × 58 mm | Low racetrack plinth with small rear saddles. |
| 11. Arch | ~104 × 76 mm | A broad curved bridge with an open underside. |
| 12. Teardrop | ~108 × 77 mm | Rounded triangular footprint tapering to a single rear tip. |
| 13. Pebbles | ~114 × 66 mm | Two domed oval feet linked by a low rear bar. |

All lean back 12 degrees, seat the board approximately 9 mm above the desk, and
leave its side buttons exposed. A provisional 36 mm centre relief avoids the
bottom ribbon area. The cable illustration drops into a top opening, then follows
an 8 mm wide, 4 mm high underside channel to the back. These are routing spaces,
not a strain-relief clamp. Add non-slip feet when developing a printable version.

## Verified references and assumptions

The [vendor dimensional drawing](../../pimoroni-inky-impression/inky-impression-5.7-drawing.png)
gives a **125.4 × 99.5 mm** outline. The
[original product page](https://shop.pimoroni.com/products/inky-impression-5-7)
gives **114.9 × 85.8 mm** active area and **9 mm** total depth including display
and header. That 9 mm is neither the lower edge thickness nor the assembled
Pi-plus-display depth. The saved rear product photo shows the central flex ribbon,
rear electronics and downward-facing Pi USB sockets.

**Concepts, not print-ready fit models.** The following remain illustrative:

- 5.2 mm slot width, board/display thickness and active-area placement.
- Pi/header/USB placement and cable bend radius; the green board is a clearance proxy.
- Ribbon relief, lower breakout-header clearance and all contact points.
- Stability under button presses and cable pull; no physical load testing performed.

Before printing a complete stand, measure the assembled unit's lower edge,
rear protrusions, USB plug body and accessible PCB contact locations. Refine the
saddles to bear on the PCB, with compliant liners and clearance to the glass,
flex ribbon, pins and components. Print a small slot coupon first. The vendor
warns that the glass display is fragile; a tight interference fit is unsuitable.

The abstract screen graphic and simplified rear hardware are orientation aids.
The stand geometry is real OpenSCAD CSG, not an AI-generated product photograph.

## Reproduce

```sh
uv run python designs/stands/render.py
uv run python designs/stands/render.py --rounded
uv run python designs/stands/render.py --explorations
```

The script uses `openscad` on PATH or the standard macOS application location.
Front, rear and stand-only renders use identical cameras across all thirteen concepts.
The models have also been evaluated through OpenSCAD's full CGAL STL exporter;
all thirteen report a simple solid. Temporary STLs live in ignored `state/stands/`;
do not treat successful mesh export as a mechanical fit check.

## Source and downloads

- [Editable OpenSCAD source](stand-concepts.scad)
- [06 / Half-drum STL](stl/06-half-drum.stl) — 111.97 × 55.82 × 27.82 mm
- [12 / Teardrop STL](stl/12-teardrop.stl) — 108.00 × 77.00 × 31.58 mm

Both exports contain the stand only and were checked as closed, connected meshes.
Import them as millimetres. Their geometry is unchanged by the later studies.

Use `show_display=false` and `show_cable=false` for stand-only export. The original
5.7-inch outline is the only supported reference here; the newer panel sizes have
different mechanical layouts.
