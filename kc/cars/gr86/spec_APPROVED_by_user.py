# Toyota GR86 (2nd gen, ZN8, 2022+) front keychain.
# Reference: ref/front.jpg = Toyota USA Newsroom studio press photo 2023_GR-86_SpecialEdition_SolarShift_004
# (straight-on front, camera centred, slightly above headlight height; front end identical to every 2022+ GR86),
# WordPress 2560 px copy, cropped (440,250)-(2130,1320). See ref/SOURCE.txt.
# Coordinates = photo px of ref/front.jpg. Body 61..1617 px (centre 839) -> 1 mm = 19.33 px.
import os, sys, math
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

# NO LOGOS (user rule): no badge / emblem / lettering anywhere; the nose spot stays plain body.

CX = 839                               # centreline (px)

# ------------------------------------------------------------------------------------------------ outline (left half)
OUTLINE = [(839, 311), (700, 310), (560, 306), (470, 302), (400, 300), (318, 300), (292, 302), (266, 308), (244, 316),
           (224, 326), (207, 337), (192, 348), (178, 360), (166, 372), (156, 385), (147, 398), (140, 410),
           (132, 423), (122, 437), (110, 450), (98, 461), (88, 474), (80, 490), (75, 508), (71, 527), (68, 546),
           (65, 570), (63, 600), (62, 630), (61, 670), (61, 705), (62, 722), (65, 745), (69, 775), (73, 805),
           (78, 835), (83, 865), (88, 893), (92, 920), (96, 947), (99, 962), (108, 969), (126, 972), (146, 976),
           (166, 984), (200, 995), (240, 1004), (280, 1010), (320, 1015), (360, 1018), (420, 1019), (500, 1022),
           (600, 1024), (700, 1025), (839, 1025)]
XL = min(x for x, y in OUTLINE)
XR = 2 * CX - XL
YB = max(y for x, y in OUTLINE)
S = 80.5 / (XR - XL)                   # mm per px


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


def sym(g):
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])


# ------------------------------------------------------------------------------------------------ parts (px)
HEADLIGHT = [(163, 424), (178, 423), (200, 428), (240, 442), (280, 462), (320, 485), (350, 506), (375, 527),
             (393, 548), (404, 570), (410, 594), (411, 614), (406, 626), (395, 630), (370, 627), (330, 621),
             (290, 614), (250, 606), (215, 596), (188, 584), (170, 570), (158, 553), (151, 532), (148, 505),
             (148, 475), (151, 450), (156, 433)]
# DRL light guide: the "L" that runs down the lamp's outer edge and along its lower edge to the inner tip
LAMP_EDGE = [(166, 423), (156, 433), (151, 450), (148, 475), (148, 505), (151, 532), (158, 553), (170, 570),
             (188, 584), (215, 596), (250, 606), (290, 614), (330, 621), (370, 627), (395, 630)]
DRL_IN, DRL_W0, DRL_W1, DRL_END = 1.17, 0.68, 0.9, 392     # inset, width at top / at inner end (mm), end x (px)

GRILLE = [(845, 710), (700, 709), (560, 707), (455, 706), (438, 707), (420, 711), (404, 720), (390, 731),
          (379, 743), (370, 758), (363, 775), (357, 800), (352, 830), (347, 865), (343, 895), (340, 918),
          (342, 931), (354, 941), (395, 950), (480, 959), (570, 966), (700, 969), (845, 970)]
GRILLE_BAR = 729                        # px: the flat black upper frame of the grille ends here, mesh below

# corner air duct: black "fang" blade + the vertical duct opening + its frame down to the bumper corner
FANG = [(118, 680), (140, 678), (165, 684), (195, 693), (230, 704), (268, 716), (296, 726), (304, 728),
        (304, 741), (296, 742), (262, 733), (222, 725), (190, 719), (175, 721), (165, 735), (160, 760), (159, 780),
        (165, 800), (169, 822), (168, 842), (163, 862), (155, 882), (146, 902), (137, 924), (129, 946),
        (123, 966), (118, 990), (40, 990), (40, 888), (107, 872), (106, 850), (104, 800), (105, 750),
        (108, 712), (112, 690)]

FENDER_LINE = [(178, 426), (178, 405), (180, 390), (185, 375), (193, 361), (205, 348), (220, 337), (240, 326),
               (252, 320)]
HOOD_CREASE = [(386, 372), (392, 410), (401, 460), (411, 512)]
HOOD_LINE = [(345, 502), (380, 510), (400, 514), (420, 516), (470, 514), (560, 513), (700, 515), (845, 516)]

GROOVE_W = 0.6
# bumper seam that wraps the grille's upper corners ('nostril'), and the lower-lip crease under the grille
NOSTRIL = [(438, 699), (428, 686), (414, 681), (397, 686), (379, 698), (362, 716), (348, 740), (339, 765), (337, 786)]
LIP_LINE = [(160, 982), (230, 992), (320, 997), (450, 999), (600, 1000), (845, 1001)]


def drl():
    lamp = Polygon(mm(HEADLIGHT)).buffer(0)
    line = LineString(geom.chaikin(mm(LAMP_EDGE), 2, closed=False)).offset_curve(DRL_IN, join_style=1)
    line = line.intersection(box(-60, -10, (DRL_END - CX) * S, 60))
    if line.geom_type != 'LineString':
        line = max(line.geoms, key=lambda q: q.length)
    n = 60
    L = line.length
    segs = []
    for i in range(n):
        a, b = line.interpolate(L * i / n), line.interpolate(L * (i + 1) / n)
        w = DRL_W0 + (DRL_W1 - DRL_W0) * ((i + 0.5) / n) ** 1.5
        segs.append(LineString([a, b]).buffer(w / 2, 24))
    g = unary_union(segs)
    return g.intersection(lamp.buffer(-0.72))


# ------------------------------------------------------------------------------------------------ G-mesh relief
# The real grille is a staggered mesh of horizontally stretched hexagons (pointed left/right ends). Built as a
# tessellation of elongated hexes: column step DX, row pitch P, tip half-width A (flat half-width B = DX - A).
MESH_DX, MESH_P, MESH_A, MESH_RIB = 3.8, 2.4, 2.1, 0.85
MESH_RIM, MESH_MINFRAC = 0.8, 0.6


def g_mesh(region):
    # holes live inside a continuous 0.7 mm black rim (no hole ever opens onto the white grille wall); rows are
    # anchored on the grille bottom so the lower edge shows whole cells and cut cells hide under the top frame.
    inner = region.buffer(-MESH_RIM, join_style=2)
    minx, miny, maxx, maxy = inner.bounds
    A, B, P = MESH_A, MESH_DX - MESH_A, MESH_P
    cells = []
    nx = int((maxx - minx) / MESH_DX) + 4
    ny = int((maxy - miny) / P) + 4
    for i in range(-nx, nx + 1):
        for j in range(-2, ny + 1):
            x = i * MESH_DX
            y = miny + P / 2 - MESH_RIB / 2 + j * P + (P / 2 if i % 2 else 0)
            h = Polygon([(x - A, y), (x - B, y - P / 2), (x + B, y - P / 2), (x + A, y), (x + B, y + P / 2), (x - B, y + P / 2)])
            cells.append(h.buffer(-MESH_RIB / 2, join_style=2))
    full = max(c.area for c in cells)
    keep = []
    for c in cells:
        if c.centroid.x > 1e-6:                         # build the left half + centre column, mirror it below
            continue
        q = c.intersection(inner)
        if q.is_empty or q.area < 0.995 * full and q.area < MESH_MINFRAC * full:
            continue
        if q.area < 0.995 * full:                       # cut cell: open it so no point is narrower than 0.8 mm
            q = q.buffer(-0.4, join_style=1).buffer(0.4, join_style=1)
        keep += [g for g in geom.polys(q) if g.area > 0.5]
    holes = sym(unary_union(keep))
    return box(minx - 2, miny - 2, maxx + 2, maxy + 2).difference(holes)


_grille = sym(Polygon(mm(GRILLE)).buffer(0))
_mesh_zone = _grille.intersection(box(-60, -10, 60, (YB - GRILLE_BAR) * S))

_outline = sym(Polygon(mm(OUTLINE)).buffer(0))


def groove(pts, smooth=1, lamp_gap=0.6, wall=None, avoid=None, gap=0.65):
    """Engraved line; where it runs into the headlight it stops lamp_gap (mm) short of the black lens, so no
    half-covered groove slivers are left at the shallow crossing. wall: keep >= wall mm of white between the
    groove and the outline. avoid: a black area the groove must stay >= gap mm away from."""
    line = LineString(geom.chaikin(mm(pts), smooth, closed=False) if smooth else mm(pts))
    lamp = Polygon(mm(HEADLIGHT)).buffer(0)
    line = line.difference(lamp.buffer(lamp_gap + GROOVE_W / 2))
    if wall is not None:
        line = line.intersection(_outline.buffer(-(wall + GROOVE_W / 2)))
    if avoid is not None:
        line = line.difference(avoid.buffer(gap + GROOVE_W / 2))
    return line.buffer(GROOVE_W / 2, 24)


prims = [
    dict(kind='geom', color='groove', geom=groove(HOOD_CREASE)),
    dict(kind='geom', color='groove', geom=groove(HOOD_LINE, lamp_gap=-0.3)),
    dict(kind='geom', color='groove', geom=groove(NOSTRIL, 2, avoid=_grille)),
    dict(kind='poly', color='black', pts=HEADLIGHT, smooth=1),
    dict(kind='geom', color='white', geom=drl()),
    dict(kind='geom', color='black', geom=_grille, mirror=False),
    dict(kind='geom', color='relief', geom=_mesh_zone, mirror=False,
         relief=dict(type='custom', ribs=g_mesh(_mesh_zone))),
    dict(kind='poly', color='black', pts=FANG, smooth=1),
]


SPEC = dict(
    id='gr86', name='Toyota GR86 (ZN8)',
    ref='kc/cars/gr86/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.55),
    badge=None,
)
