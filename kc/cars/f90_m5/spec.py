# BMW M5 Competition (F90 LCI, 2021+) front keychain.
# PROVISIONAL DESIGN WITHOUT A REFERENCE PHOTO: the cloud container's egress proxy refused every image host tried
# (Wikimedia Commons/upload, BMW PressClub + mediapool, motor1, hearstapps, edmunds, netcarshow, caricos, unsplash,
# flickr, imgur, pexels, pixabay ...), so - like g90_m5 - this is drawn directly in keychain millimetres
# (units='mm', x = 0 at the centreline, y up, 0 at the bottom of the lip), with BMW proportions of the same era
# calibrated on the photo-traced f92_m8 and f82_m4 specs. Elements drawn (F90 LCI M5 Competition):
#   * wide twin kidneys joined by a slim centre bar, gloss-black surround + double vertical slats (custom relief)
#   * slim LCI laser headlights, deeper outer part with the step in the lower edge, inner tip toward the kidney;
#     DRL = the two L-shaped light guides (outer leg + bottom leg) per lamp, white strokes
#   * M bumper: three big intakes (wide centre + two side) with honeycomb mesh, white pillars between them,
#     black lower lip
#   * hood: shut line over kidneys/lamps, fender shut lines to the cowl, two power-dome creases
#   * ONE tow-hook cover ring (viewer's left only, mirror=False), one parking sensor per side
# NO LOGOS (user rule): no roundel / lettering; the spot above the kidneys stays plain body (badge=None).
# The user should check this against a real straight-on photo before printing a sale batch.
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union

OUTLINE = [(0, 39.3), (10, 39.25), (17, 39.0), (23, 38.55), (27.5, 37.9), (30.5, 37.2), (32.0, 36.6),
           (34.6, 35.0), (36.9, 33.6), (38.6, 32.0), (39.7, 30.0), (40.15, 27.5), (40.25, 24), (40.2, 18),
           (40.0, 12.5), (39.7, 8.5), (39.5, 6.2), (39.2, 4.4), (38.4, 2.6), (37.0, 1.5), (34.5, 0.9),
           (26, 0.4), (14, 0.1), (0, 0)]

# right kidney (viewer's right, mirrored); inner edge 0.8 mm off the centreline -> 1.6 mm white centre bar
KIDNEY = [(0.8, 17.8), (0.8, 29.0), (1.4, 29.9), (4.5, 30.2), (8.5, 30.25), (11.6, 30.0), (13.4, 29.4),
          (14.3, 28.2), (14.9, 25.0), (15.45, 21.0), (15.6, 19.2), (15.0, 17.9), (13.6, 17.3), (10, 17.1),
          (4, 17.0), (1.5, 17.1)]


def double_slats(centres, rib=0.8, gap=0.8, inset=1.0):
    """F90 kidney: pairs of vertical slats (mirrored), keychain mm, stopping `inset` mm short of the kidney wall so
    the gloss-black surround reads as a frame (same construction as f92_m8 / f82_m4)."""
    inner = Polygon(KIDNEY).buffer(-inset)
    bars = []
    for xc in centres:
        for dx in (-(gap + rib) / 2, (gap + rib) / 2):
            x0, x1 = xc + dx - rib / 2, xc + dx + rib / 2
            spans = []
            for x in (x0, x1):
                seg = inner.intersection(LineString([(x, -1), (x, 60)]))
                spans.append(seg.bounds[1::2] if not seg.is_empty else None)
            if None in spans:
                continue
            y0, y1 = max(spans[0][0], spans[1][0]), min(spans[0][1], spans[1][1])
            if y1 - y0 > 1.0:
                bars.append(box(x0, y0, x1, y1))
                bars.append(box(-x1, y0, -x0, y1))
    return unary_union(bars)


SLATS = double_slats([3.65, 7.35, 11.05], rib=0.7, gap=0.6, inset=1.1)

HEADLIGHT = [(16.0, 28.6), (16.3, 29.5), (17.2, 29.9), (24, 30.7), (30, 31.4), (35, 32.1), (37.0, 32.2),
             (38.2, 31.4), (38.6, 29.8), (38.3, 28.0), (37.6, 27.0), (34, 26.4), (29, 26.1), (25.2, 26.1),
             (23.6, 26.7), (22.6, 27.4), (18.5, 27.7), (16.6, 27.9)]

CENTRE_INTAKE = [(0, 14.3), (12.4, 14.3), (13.6, 13.9), (14.2, 13.0), (16.6, 5.9), (16.1, 5.1), (0, 5.0)]
SIDE_INTAKE = [(17.1, 15.0), (17.9, 15.9), (27, 17.6), (35.6, 19.2), (36.9, 19.0), (37.7, 17.6), (38.2, 12),
               (38.0, 7.6), (37.3, 5.9), (35.8, 5.3), (20.0, 5.2), (19.3, 5.7)]
LIP = [(-1, -1), (-1, 3.1), (14, 3.15), (26, 3.4), (33.5, 3.75), (37.0, 4.3), (38.6, 5.4), (39.6, 6.6), (41, 6.6),
       (41, -1)]

SPEC = dict(
    id='f90_m5', name='BMW M5 Competition (F90 LCI)',
    ref=None,
    units='mm',
    outline_half=OUTLINE,
    outline_smooth=1,
    prims=[
        # headlight unit (black)
        dict(kind='poly', color='black', smooth=1, pts=HEADLIGHT),
        # DRL: the two L-shaped light guides (outer leg + bottom leg)
        dict(kind='stroke', color='white', width=0.75, pts=[(36.8, 30.9), (36.7, 28.6), (36.2, 27.95), (32.0, 27.45)]),
        dict(kind='stroke', color='white', width=0.75, pts=[(30.4, 30.6), (30.3, 28.2), (29.7, 27.35), (25.6, 27.15)]),
        # kidney grille: black surround + double vertical slats
        dict(kind='poly', color='black', smooth=1, pts=KIDNEY, relief=dict(type='custom', ribs=SLATS)),
        # three big lower intakes with honeycomb mesh
        dict(kind='poly', color='black', pts=CENTRE_INTAKE, relief=dict(type='hex', pitch=2.7, rib=0.72)),
        dict(kind='poly', color='black', smooth=1, pts=SIDE_INTAKE, relief=dict(type='hex', pitch=2.7, rib=0.72)),
        # lower lip (full width)
        dict(kind='poly', color='black', pts=LIP),
        # grooves: hood shut line over kidneys + lamps, fender shut lines to the cowl, two power-dome creases
        dict(kind='stroke', color='groove', width=0.55, smooth=1,
             pts=[(0, 31.2), (9, 31.3), (14.6, 31.0), (17, 30.9), (24, 31.75), (30, 32.45), (34.0, 32.95)]),
        dict(kind='stroke', color='groove', width=0.55, pts=[(34.0, 32.95), (32.6, 35.0), (31.3, 37.3)]),
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(13.0, 31.9), (11.2, 35.0), (9.6, 39.4)]),
        # parking sensor + ONE tow-hook cover (viewer's left only)
        dict(kind='ring', color='black', c=(29.5, 22.2), r_mm=0.95, width=0.55),
        dict(kind='ring', color='black', c=(-19.8, 19.6), r_mm=1.3, width=0.55, mirror=False),
    ],
    badge=None,
    tab=dict(y_mm=23.0),
)
