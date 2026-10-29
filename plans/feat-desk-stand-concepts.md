# Desk stand concept study

- [x] Inspect vendor drawing, product dimensions, rear electronics and local OpenSCAD.
- [x] Create four editable stand concepts for the original 5.7-inch display.
- [x] Render assembled, rear and stand-only views; inspect geometry.
- [x] Present a comparison with verified dimensions and explicit fit assumptions.

Acceptance: four distinct concepts rendered from actual OpenSCAD geometry; preserve
bottom-centre ribbon clearance, expose side buttons, illustrate rear cable routing.
These are concept models, not fit-validated print files. No runtime changes.

Completed four concepts and twelve 1200 × 1000 OpenSCAD previews. Inspected front,
rear and stand-only views; lowered lips below the active image and added a vertical
cable entry into the underside channel. All four final stand-only CGAL exports
report `Simple: yes`, `Volumes: 2` (one solid plus the exterior). Renderer lint and
format checks pass. Inline gallery checked at desktop/mobile widths, including
view switching. Measured fit, cushioning, component clearance and physical
stability remain deliberately outside this concept study.

## Rounded direction

- [x] Add three studies: half-moon side supports, a domed semicircular back, and an open crescent.
- [x] Render and inspect all views, including full geometry exports.
- [x] Present the rounded alternatives and retain the original studies.

Acceptance: visibly curved silhouettes, low front lips, rear cable routing and
explicitly provisional mechanical fit, using the same display reference.

Completed concepts 5–7 and nine additional renders. Full CGAL exports each report
`Simple: yes`, `Volumes: 2`. Inspected all nine views and desktop/mobile gallery
previews, including rear-view switching. Half-drum (6) is the new default; original
concepts and renders remain available. No physical fit validation is claimed.

## Six focused alternatives

- [x] Model concepts 8–13: soft delta, loops, capsule, arch, teardrop, and pebbles.
- [x] Render all views, check full geometry, and correct visual or structural defects.
- [x] Publish a comparison and document reproducible renders.

Acceptance: six distinct minimalist silhouettes with the same provisional display
fit; include rounded triangles, solid forms and open forms. Retain concepts 1–7.

Completed eighteen renders and six full CGAL exports, all simple solids. Binary
STL checks confirmed closed connected meshes and positive volumes. Moved the
loop windows aft to preserve the support behind each slot; regenerated that
model and its views. Raised extrusion preview convexity to correctly display
the hollow shapes without missing faces (no mesh geometry change). Desktop and
mobile comparisons pass, including rear-view switching and no horizontal overflow.
Python lint/format pass. The existing half-drum STL is unchanged.

## Public release

- [x] Write a dedicated illustrated stand guide explaining the design directions and OpenSCAD workflow.
- [x] Add only stand-page links to the root README and document both downloadable STLs.
- [ ] Validate documentation/assets, scan the branch, and push all stand work.
- [ ] Create and link the PR, with validation recorded for the authorized merge.

Acceptance: all thirteen designs, 39 previews, editable source, two requested
STLs and the guide are on GitHub main. The main README stays concise. User has
explicitly authorized commit, push, PR and merge for this release.

Pre-publication checks: 53 local Markdown links/anchors resolve, all 39 PNGs have
the expected dimensions and decode successfully, all HTML gallery image targets
exist, both binary STLs have valid lengths and triangle counts, and renderer
lint/format and diff whitespace checks pass. No display runtime code changed.
