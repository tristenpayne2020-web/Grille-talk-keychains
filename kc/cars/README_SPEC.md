# Car-front keychain spec guide (read fully before tracing)

The goal: a keychain for a new car that looks like it belongs to the same product line as the user's own
**BMW M3 (G80)** keychain. Study these first, they ARE the style guide:

| file (in `kc/style/`) | what it shows |
|---|---|
| `g80_reference_photo_the_user_traced.png` | the straight-on front photo the user traced in Fusion 360 |
| `g80_user_keychain_fusion_screenshot.png` | the user's finished keychain (their render) |
| `g80_user_keychain_iso.png` | same, isometric |
| `g80_face_flat.png` | the G80 rebuilt by this pipeline, flat face view (same renderer your car's `face.png` uses) |
| `g80_production_render.png` / `g80_classic_render.png` | the two 3D builds of the G80 |

Compare the photo with the keychain to see how the user abstracts a car: **what is kept, what is simplified, what is dropped.**

## Design language (measured from the G80)
1. **View and crop**: straight-on front elevation, perfectly mirror-symmetric. The outline is the body only: top edge =
   the base of the windshield / cowl (hood fully included, windshield/roof/mirrors/antenna excluded), sides = the
   fenders/wheel-arch flares, bottom = the front splitter/lip. **Tyres are not part of the outline.**
2. **Size**: the car body is always scaled to exactly **80.5 mm wide**; height follows the car (G80 = 38 mm). A low
   supercar will be flatter, which is correct. 3.0 mm thick (handled by the pipeline).
3. **Two colours only.** White = body paint. Black = everything dark: headlight units (the whole lens outline),
   grille openings, air intakes, splitter/lip, side air curtains/vents, prominent hood vents.
4. **White on black** = the car's light signature (DRL graphics) drawn inside the black headlights. This is the most
   recognisable element of a modern car front - get its shape right (G80: the two hexagonal "L" strokes).
5. **Grille** = black region with a **relief pattern** matching the real car (G80: horizontal slats). Other patterns:
   vertical bars, honeycomb (`hex`), `grid`, `diamond`. Large intakes may also get a pattern if the real car has
   visible mesh/fins there.
6. **Engraved lines** (`groove`) for 2-6 key body lines only: hood shut line / hood edges / fender-to-A-pillar lines,
   creases (G80: hood outline + two fender lines). Width 0.5-0.6 mm.
7. **Small details**: parking sensors / washers as small rings (`ring`, outer r >= 0.9 mm, width 0.5 mm) - optional,
   max ~2 per side. Tow-hook covers, plates, text, wipers: dropped. Logos: dropped (see below).
8. **Keyring tab**: on the viewer's LEFT side, at a height where the car edge is white (fender), usually 50-65 % of
   the height. Set `tab: {'y_frac': 0.55}` (fraction of height from the bottom) or `{'y_mm': 21}`.
9. **Printability (0.4 mm nozzle, hard rule)**: every black feature, white feature (e.g. a DRL stroke), groove and
   every gap between two features must be **>= 0.5 mm wide (0.6 preferred)**. Relief ribs and the gaps between them
   >= 0.6 mm (0.8+ looks better). The checker lists violations with their mm position; fix them in the spec. An
   auto-repair widens leftovers, but aim for **0 errors before repair**.
10. Simplify: use a few clean straight/curved segments like the G80 does, not noisy traced pixels. The G80 headlights
   are ~8 points each; the outline is ~40 points per half.

## Coordinate frame
Trace directly on the reference photo in **photo pixels** (`units: 'px'`). Calibration keys:
- `px_left`, `px_right`: x pixel of the car body's widest points (left/right body edge, NOT mirrors, NOT tyres)
- `center_x`: car centreline x pixel (default = midpoint of px_left/px_right; set it explicitly if the photo is off)
- `px_bottom`: y pixel of the lowest point of the outline (bottom of the splitter/lip)
- `y_scale` (optional, default 1.0): stretch heights if the photo is foreshortened. Keep 1.0 unless clearly needed.
The pipeline maps px -> mm (80.5 mm between px_left and px_right, y up, 0 at px_bottom).

Symmetry: trace ONE half. `outline_half` runs from the top of the centreline, outward, down the side, back to the
bottom of the centreline (either half works - it is mirrored). Every primitive is mirrored by default
(`mirror: True`); centred features (grille bridge, badge, centre intake) use `mirror: False` and must themselves be
symmetric about `center_x` (easiest: trace one half and keep mirror True - a shape crossing the centreline is fine,
it is unioned with its mirror).

## Spec file (`kc/cars/<id>/spec.py`)
```python
SPEC = dict(
    id='g87_m2', name='BMW M2 (G87)',
    ref='kc/cars/g87_m2/ref/front.jpg',           # path used for overlay.png (relative to scratchpad or absolute)
    units='px', px_left=112, px_right=1188, px_bottom=640, center_x=650,
    outline_half=[(650,180),(760,176),(930,196),(1080,236),(1150,300),(1188,420),(1180,560),(1120,625),(900,640),(650,640)],
    outline_smooth=0,                              # optional Chaikin smoothing passes for the outline
    prims=[                                        # painted IN ORDER, later paints over earlier
        dict(kind='poly', color='black', pts=[(...), ...]),                     # headlight unit
        dict(kind='stroke', color='white', width=0.7, pts=[(...), ...]),        # DRL stroke (width in mm)
        dict(kind='poly', color='black', pts=[...], relief=dict(type='hbars', pitch=2.4, rib=1.1)),   # grille
        dict(kind='poly', color='black', pts=[...], mirror=False),             # centre lower intake (symmetric)
        dict(kind='stroke', color='groove', width=0.55, pts=[...]),            # hood shut line
        dict(kind='ring', color='black', c=(x, y), r_mm=1.1, width=0.5),        # parking sensor
    ],
    badge=dict(type='roundel', c=(650, 330), d=4.0),   # c in px, d = diameter in mm
    tab=dict(y_frac=0.56),
)
```
Primitive kinds (coordinates in px unless noted; all widths/sizes in **mm**):
- `poly` pts [, smooth=n Chaikin passes, offset=+/-mm grow/shrink]
- `stroke` pts, width [, cap='round'|'flat'|'square', smooth=n]
- `circle` c, r (px) or r_mm ; `ring` c, r or r_mm (outer), width ; `ellipse` c, rx/ry (px) or rx_mm/ry_mm, rot (deg)
- colours: `black`, `white` (paints white over black - DRLs, grille bridge), `groove` (engraved line), `relief`
  (adds a pattern to an already-black area without repainting it)
- `relief` dict (mm): `type` hbars|vbars|bars|hex|grid|diamond|none, `pitch` centre spacing, `rib` rib width,
  `angle` deg, `offset` shift, `margin` gap between ribs and the recess wall (0 = ribs touch the wall).
  Good starting values: slats pitch 2.2-2.8 / rib 1.0-1.3 ; honeycomb pitch 2.2-2.6 / rib 0.7 ; grid pitch 2.4 / rib 0.7.
- `badge` types: `roundel` (BMW), `star` (Mercedes/AMG), `rings` (Audi; `ring_r`, `w`, `colour`), `shield` (Porsche/
  Lamborghini crest), `flags` (Corvette), `pony` (Mustang), `bar`. `d` = size in mm (>= 3.2). Badges can be
  switched off (`badge_on=False`), so never paint the badge into other primitives.

## Commands (run from the scratchpad dir `.../scratchpad`)
- Trace helpers: `python kc/lib/trace_tools.py grid|edges|points|mirror|rotate ...` (see its docstring; grid/edge
  labels are ORIGINAL photo pixels even on crops/zooms: `--crop x0 y0 x1 y1 --scale 3 --step 10`).
- Fast 2D iteration (1-2 s): `python kc/lib/export.py kc/cars/<id>/spec.py kc/cars/<id>/out --design-only`
  -> prints size + printability errors; writes `out/face.png` (flat keychain face) and `out/overlay.png` (your design
  painted back on the photo: red = outline, cyan = black edges, yellow = white edges). LOOK at both every iteration.
- Full build (~30-90 s): `python kc/lib/export.py kc/cars/<id>/spec.py kc/cars/<id>/out`
  -> both constructions (STL, STEP, 3MF single + full plate), 3D renders `out/production/*_render.png`,
  `out/classic/*_render.png`, and a real-slicer check (`build_report.json` -> `slicecheck`: `n_lost` must be 0 and
  `top_layer_coverage` >= 0.9 for all four parts).

## NO LOGOS (user decision 2026-09-30, trademark reasons)
No car gets a badge, emblem, crest or brand lettering. New specs set `badge=None` and draw no logo prims; leave the
spot as plain body or plain grille. The pipeline enforces it for old specs too: `geom.py` sets `KC_BADGE=0` by
default, `build_maps` then skips the library `badge`, and specs with a custom `SHOW_BADGE` / `BADGE_ON` flag read
`KC_BADGE` and drop their logo prims. `KC_BADGE=1` brings the old logos back (internal use only).
The two sections below describe the old badge mechanisms; they stay only so the older specs make sense.

## Badges without a built-in type (legacy) (Nissan, McLaren, Dodge, Toyota, Cadillac, Chevrolet bowtie, Shelby...)
Draw a simplified badge as custom `geom`/`mm_poly` primitives (>= 0.5 mm strokes, 3.5-8 mm size) and put them behind a
module-level literal flag `SHOW_BADGE = True` (append them to `prims` only when True). Keep proportions faithful:
zoom in at print scale before accepting. See kc/cars/gt500_mustang/spec.py (COBRA_MM) for an example.
