# Kia Stinger GT (CK facelift, 2022-2023) front keychain.
# Reference: ref/front.png = crop (290,330)-(1090,720) of ref/kiamedia_17181_low.jpg, Kia America press photo
# "2022 Stinger Scorpion Special Edition" (kiamedia.com media id 17181, straight-on front). See ref/SOURCE.txt.
# NO LOGOS (user rule): the KIA badge spot on the nose stays plain body.
#
# Revision 1:
#  * upper 'tiger nose' grille: raised chrome-stud relief in staggered horizontal rows (the facelift's studded
#    mesh) instead of a generic honeycomb; only whole studs, kept >= 0.65 mm off the recess wall (no slivers).
#  * lower intake: flush black opening with a recessed honeycomb panel in the centre (stretched hex cells, whole
#    cells only so the panel rim forms a solid frame) - the real car's centre mesh; plain black beside the fangs.
#  * hood: vents moved down off the cowl edge, thinner; the two hood creases run from each vent forward/inward
#    (traced from a high-pass of the photo); shut line groove 0.65 mm.
#  * crisper headlight (sharper inner tip), longer inner DRL sweep, squarer side intakes, blunt fang tips with
#    near-vertical feet, flatter centre pinch on the grille, one sensor pair only.
import os, sys, math
from shapely.geometry import LineString, Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

CX = 382
PXL, PXR, PXB = 33, 731, 348
S = 80.5 / (PXR - PXL)          # mm per px


def mm(p):
    return ((p[0] - CX) * S, (PXB - p[1]) * S)


def region_mm(pts, smooth=0):
    q = [mm(p) for p in pts]
    if smooth:
        q = geom.chaikin(q, smooth, closed=True)
    g = Polygon(q).buffer(0)
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])


OUTLINE = [(382, 38), (300, 39), (220, 42), (160, 46), (125, 52), (112, 58), (100, 64), (82, 74), (66, 84), (53, 95),
           (44, 108), (38, 125), (35, 145), (33, 175), (33, 220), (33, 270), (34, 300), (36, 320), (40, 333),
           (50, 340), (80, 343), (150, 346), (250, 348), (382, 348)]

HEADLIGHT = [(58, 104), (75, 99), (100, 101), (130, 110), (155, 122), (174, 137), (166, 148), (135, 153),
             (112, 158), (88, 167), (68, 165), (55, 153), (51, 132)]
DRL_OUT = [(62, 126), (63, 135), (68, 140), (78, 142), (110, 142)]
DRL_IN = [(121, 129), (122, 136), (128, 140), (150, 141), (160, 139)]

GRILLE = [(420, 151), (382, 151), (360, 149), (340, 146), (310, 143), (280, 143), (250, 144), (220, 146), (195, 151), (178, 158),
          (167, 166), (166, 172), (172, 180), (185, 190), (205, 198), (240, 204), (280, 207), (310, 207), (330, 203),
          (342, 197), (355, 195), (382, 195), (420, 195)]

SIDE_INTAKE = [(66, 193), (90, 194), (108, 198), (113, 210), (114, 240), (113, 270), (108, 290), (97, 299), (85, 302),
               (72, 299), (66, 288), (64, 250), (64, 210)]
SIDE_BLADE = [(81, 212), (81, 286)]

LOWER = [(420, 250), (382, 250), (200, 251), (180, 255), (165, 265), (156, 280), (153, 296), (158, 305), (180, 312), (220, 316),
         (382, 318), (420, 318)]
PANEL = [(420, 264), (250, 264), (241, 268), (240, 300), (244, 308), (260, 311), (420, 311)]   # centre honeycomb
FANG = [(193, 262), (200, 260), (206, 267), (233, 326), (214, 326), (211, 312), (198, 280)]

LIP = [(400, 331), (200, 330), (100, 328), (55, 326), (30, 318), (20, 360), (400, 360)]

HOOD_VENT = [(192, 58), (205, 55), (240, 55), (252, 58), (250, 63), (230, 65), (205, 64)]
HOOD_CREASE = [(190, 66), (205, 78), (218, 89), (228, 99)]
HOOD_LINE = [(128, 64), (136, 73), (150, 86), (168, 99), (190, 107), (220, 111), (270, 114), (330, 115), (390, 116)]


# ---------------------------------------------------------------- relief geometry (keychain mm)
def _grille_studs():
    """Chrome studs of the facelift grille: horizontal capsules in staggered rows; whole studs only."""
    region = region_mm(GRILLE, 2)
    inner = region.buffer(-0.65)
    L, W, PX, PY = 0.65, 0.65, 2.2, 1.35              # capsule: 1.3 x 0.65 mm
    y0 = mm((0, 173))[1]                              # a row through the middle of the grille
    studs = []
    for j in range(-6, 7):
        y = y0 + j * PY
        sh = (PX / 2) if j % 2 else 0.0
        for i in range(-20, 21):
            x = i * PX + sh
            s = LineString([(x - L / 2, y), (x + L / 2, y)]).buffer(W / 2, 16)
            if s.within(inner):
                studs.append(s)
    return region, unary_union(studs)


def _panel_mesh():
    """Stretched honeycomb of the lower-intake centre panel: rows of wide pointed-end hex cells, staggered by half a
    cell; whole cells only, so the panel rim reads as a solid frame (no clipped cells / slivers)."""
    region = region_mm(PANEL, 1)
    hw, hh, tip = 1.15, 0.45, 0.45                     # cell half-width, half-height, length of the pointed ends
    PX, PY = 2.9, 1.5                                  # horizontal pitch, row pitch (rib >= 0.6 everywhere)
    yc = mm((0, 287.5))[1]
    cell = Polygon([(-hw, 0), (-hw + tip, hh), (hw - tip, hh), (hw, 0), (hw - tip, -hh), (-hw + tip, -hh)])
    inner = region.buffer(-0.6)
    holes = []
    for j in range(-3, 4):
        sh = PX / 2 if j % 2 else 0.0
        for i in range(-12, 13):
            h = affinity.translate(cell, i * PX + sh, yc + j * PY)
            if h.within(inner):
                holes.append(h)
    return region, region.difference(unary_union(holes))


GRILLE_REGION, GRILLE_RIBS = _grille_studs()
PANEL_REGION, PANEL_RIBS = _panel_mesh()

prims = [
    dict(kind='stroke', color='groove', width=0.65, pts=HOOD_LINE, smooth=2),
    dict(kind='stroke', color='groove', width=0.65, pts=HOOD_CREASE, smooth=1),
    dict(kind='poly', color='black', pts=HOOD_VENT, smooth=1),
    dict(kind='poly', color='black', pts=HEADLIGHT, smooth=1),
    dict(kind='stroke', color="white", width=0.75, pts=DRL_OUT, smooth=1),
    dict(kind='stroke', color="white", width=0.75, pts=DRL_IN, smooth=1),
    dict(kind='poly', color='black', pts=GRILLE, smooth=2, relief=dict(type='custom', ribs=GRILLE_RIBS)),
    dict(kind='poly', color='black', pts=SIDE_INTAKE, smooth=2),
    dict(kind='stroke', color='white', width=0.7, pts=SIDE_BLADE),
    dict(kind='poly', color='black', pts=LOWER, smooth=1),
    dict(kind='poly', color='white', pts=FANG),
    dict(kind='poly', color='relief', pts=PANEL, smooth=1, relief=dict(type='custom', ribs=PANEL_RIBS)),
    dict(kind='poly', color='black', pts=LIP),
    dict(kind='ring', color='black', c=(251, 222), r_mm=0.95, width=0.5),
]

SPEC = dict(
    id='kia_stinger', name='Kia Stinger GT (CK facelift)',
    ref='kc/cars/kia_stinger/ref/front.png',
    units='px', px_left=PXL, px_right=PXR, px_bottom=PXB, center_x=CX,
    outline_half=OUTLINE,
    outline_smooth=2,
    prims=prims,
    badge=None,
    tab=dict(y_frac=0.54),
)
