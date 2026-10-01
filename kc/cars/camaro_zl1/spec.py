# Chevrolet Camaro ZL1 (6th gen, 2017-2024 nose; the 2019 refresh left the ZL1 front unchanged) front keychain.
# Reference: ref/front.jpg = crop (x 300..3070, y 400..2200) of Wikimedia Commons "2017 Camaro ZL1.jpg"
# (Yahya S., CC BY 2.0), straight-on auto-show photo, camera about headlight height, DRLs lit. See ref/SOURCE.txt.
# Traced half = viewer's LEFT. Coordinates are photo pixels of ref/front.jpg (1 mm = 32.6 px).
#
# Design (G80 language): white = body paint. Black = the carbon hood extractor (top centre, reaching back to the
# windshield base, with its carbon side fins and shallow V front edge), ONE continuous band of headlamps + slim upper
# grille strip (the ZL1 lamps flow into the strip), the huge lower grille, the two slanted corner brake-duct intakes,
# the full-width splitter with its wrapped-up corner end plates. White on black = the light signature: the J-shaped
# DRL light guide (0.75 mm down the lamp's outer end from its sharp top corner, swelling to 1.0 mm along its lower
# edge, ending in a blunt diagonal cut at the chrome turn-signal piece), the vertical LED blade at the outer end of
# each corner intake, and the hollow ZL1 "flowtie" as a white bowtie outline on the strip (SHOW_BADGE). Relief = the
# ZL1's lower grille as 4 wavy bars (V at the centreline, flatter run, kink down, outer rise), measured on the photo.
# Grooves = the hood shut line, the two edges of the raised painted hood panel in front of the extractor, and the
# fascia cheek creases.
#
# Photo perspective: the close, elevated-ish show photo stretches the hood's top surface (everything above the hood
# front edge, y < 557 px). That zone is compressed in px space by warp() BEFORE anything else (KA for the painted
# panel, KB for the extractor), so the fascia below the hood edge keeps the photo's fit. Set KC_NOWARP=1 to get an
# unwarped overlay for checking the trace against the photo.
import os, sys, math
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):
    SHOW_BADGE = False

CX, YB, XL = 1383.5, 1670, 70          # centreline, splitter bottom, fender (widest body) left edge
XR = 2 * CX - XL
S = 80.5 / (XR - XL)                    # mm per px

# ------------------------------------------------------------------------------------------------ hood-zone warp
YH, YE = 557.0, 292.0      # hood front edge at the centre / extractor front edge (photo px)
KA, KB = 0.42, 0.58        # vertical compression of the painted hood panel (YE..YH) and of the extractor (< YE)
if os.environ.get('KC_NOWARP', '').strip() in ('1', 'true', 'yes'):
    KA = KB = 1.0


def wy(y):
    if y >= YH:
        return y
    if y >= YE:
        return YH - KA * (YH - y)
    return YH - KA * (YH - YE) - KB * (YE - y)


def W(pts):
    return [(x, wy(y)) for x, y in pts]


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


def full(half):
    """left-half px trace starting and ending on the centreline -> symmetric polygon in mm"""
    h = mm(half)
    return Polygon(h + [(-x, y) for x, y in reversed(h)]).buffer(0)


def var_stroke(pts, widths, n=2, step=0.08):
    """polyline (mm) with a width (mm) given per vertex, linearly interpolated -> round-capped polygon"""
    P = np.array(pts, float)
    Wd = np.array(widths, float)
    if n:
        for _ in range(n):                           # Chaikin on points and widths together
            q, w = [P[0]], [Wd[0]]
            for i in range(len(P) - 1):
                q += [0.75 * P[i] + 0.25 * P[i + 1], 0.25 * P[i] + 0.75 * P[i + 1]]
                w += [0.75 * Wd[i] + 0.25 * Wd[i + 1], 0.25 * Wd[i] + 0.75 * Wd[i + 1]]
            q.append(P[-1]); w.append(Wd[-1])
            P, Wd = np.array(q), np.array(w)
    parts = []
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        k = max(1, int(np.hypot(*(b - a)) / step))
        for t0 in range(k):
            t1 = t0 + 1
            p0, p1 = a + (b - a) * t0 / k, a + (b - a) * t1 / k
            r0 = (Wd[i] + (Wd[i + 1] - Wd[i]) * t0 / k) / 2
            r1 = (Wd[i] + (Wd[i + 1] - Wd[i]) * t1 / k) / 2
            parts.append(unary_union([Point(p0).buffer(r0, 24), Point(p1).buffer(r1, 24)]).convex_hull)
    return unary_union(parts).buffer(0)


plain = lambda g: shapely.from_wkb(shapely.to_wkb(g))

# ------------------------------------------------------------------------------------------------ outline
# top edge = windshield base: across the extractor (which reaches back to the cowl), the fin corner, the fender /
# cowl tops beside it (mirror base excluded), then down the fender.
OUTLINE = W([
    (CX, 147), (1200, 147), (1050, 148), (975, 152), (935, 158), (900, 165), (860, 171),
    (780, 175), (700, 175), (620, 177), (560, 184), (500, 196), (450, 213), (400, 237),
    (350, 263), (310, 292), (270, 338), (225, 398), (185, 455), (150, 510), (122, 560),
    (100, 620), (88, 700), (76, 755),
    (70, 800), (72, 860), (80, 930), (92, 1000), (104, 1070), (113, 1130),
    (117, 1200), (121, 1240),                                                    # fender foot
    (106, 1285), (88, 1340), (76, 1390), (72, 1425), (76, 1452), (94, 1471),     # splitter end plate
    (130, 1487), (190, 1508), (250, 1535), (350, 1566), (440, 1600), (500, 1618),
    (650, 1628), (800, 1638), (1000, 1651), (1200, 1664), (CX, 1670)])

# ------------------------------------------------------------------------------------------------ black parts
# carbon hood extractor: top clipped by the outline (windshield base), outer side = the carbon fin, front edge =
# the shallow V measured on the photo (268 at the fin, 296 on the centreline)
HOOD_INSERT = W([(CX, 100), (916, 100), (915, 150), (903, 165), (898, 196), (888, 222), (881, 250), (889, 259),
                 (940, 268), (1000, 275), (1100, 282), (1200, 287), (1300, 292), (CX, 296)])
TOP_RIM = 0.0              # mm of white kept between the extractor and the windshield-base edge (0 = on the edge)
# raised painted centre panel in front of the extractor: its two side edges (grooves)
RAISED_PANEL = W([(979, 276), (990, 320), (1003, 370), (1018, 425), (1031, 480), (1041, 530), (1045, 552)])
# headlamp + upper grille strip: one continuous black band (the lamps flow into the slim upper grille); the strip's
# lower edge dips under the bowtie like the real badge frame
LAMP_BAND = [(CX, 738), (1200, 734), (1000, 723), (859, 712), (677, 690), (467, 647), (300, 601), (245, 578),
             (222, 557), (192, 552), (179, 571), (177, 592), (181, 632), (194, 668), (209, 695), (236, 721),
             (262, 745), (330, 764), (400, 780), (463, 801), (520, 806), (600, 798), (679, 786), (933, 820),
             (1200, 857), (1300, 874), (CX, 877)]
# DRL light guide (centreline measured from the lit guide): down the lamp's outer end, then along its lower edge,
# getting bolder, to a point
DRL = [(207, 585), (208, 598), (211, 615), (216, 632), (222, 648), (229, 664), (241, 681), (265, 699), (297, 711),
       (340, 725), (380, 736), (420, 742), (460, 744), (500, 744), (540, 745), (580, 746)]
DRL_WIDTHS = [0.62, 0.7, 0.74, 0.75, 0.77, 0.8, 0.85, 0.9, 0.95, 0.98, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
DRL_CUT = [(542, 729), (566, 762)]   # blunt diagonal end where the chrome turn-signal piece cuts the lit guide
LAMP_MARGIN = 0.62          # mm of black kept around the light guide inside the lamp
LOWER_GRILLE = [(CX, 999), (1180, 993), (900, 982), (607, 951), (580, 958), (556, 975), (541, 1010),
                (538, 1040), (542, 1065), (556, 1170), (626, 1344), (648, 1384), (672, 1403), (705, 1411),
                (1219, 1468), (CX, 1479)]
CORNER_INTAKE = [(118, 950), (106, 972), (138, 1165), (150, 1192), (170, 1201), (200, 1200), (336, 1285),
                 (461, 1347), (492, 1356), (470, 1285), (446, 1205), (425, 1152), (402, 1112), (372, 1086),
                 (145, 954)]
LED_BLADE = [(150, 982), (183, 1156)]    # centreline of the lit blade (photo y ~967..1170)
BLADE_W, BLADE_MARGIN, FENDER_RIM = 0.95, 0.6, 0.75   # mm: blade width, black around it, white fender rim
SPLITTER = [(CX, 1579), (931, 1530), (771, 1509), (700, 1503), (600, 1525), (454, 1472), (248, 1376),
            (200, 1335), (160, 1300), (125, 1262), (100, 1245), (40, 1245), (40, 1720), (CX, 1720)]
HOOD_LINE = W([(334, 262), (346, 280), (372, 312), (403, 363), (444, 406), (506, 446), (587, 474), (700, 500), (850, 528),
               (1000, 548), (1200, 555), (CX, 557), (CX + 20, 557)])
# fascia cheek crease: from the fender side under the lamp, inward and down toward the grille's top-outer corner
CHEEK = [(190, 812), (200, 815), (300, 845), (400, 868), (500, 887), (590, 902)]

GROOVE_W = 0.62
OUTLINE_MM = full(OUTLINE)
INSERT_MM = Polygon(mm(HOOD_INSERT)).buffer(0).intersection(OUTLINE_MM.buffer(-TOP_RIM) if TOP_RIM else OUTLINE_MM)
PANEL_MM = LineString(geom.chaikin(mm(RAISED_PANEL), 2, closed=False)).buffer(GROOVE_W / 2).difference(INSERT_MM)
def _keep_right_of(pts_px):
    (x0, y0), (x1, y1) = mm(pts_px)
    dx, dy = x1 - x0, y1 - y0
    L = 200.0 / math.hypot(dx, dy)
    a, b = (x0 - dx * L, y0 - dy * L), (x1 + dx * L, y1 + dy * L)
    nx, ny = dy * L, -dx * L          # right-hand normal (mm frame, y up) = the lamp side of the cut
    return Polygon([a, b, (b[0] + nx, b[1] + ny), (a[0] + nx, a[1] + ny)])


DRL_MM = var_stroke(mm(DRL), DRL_WIDTHS).intersection(_keep_right_of(DRL_CUT))
# lamp band grown so the DRL always has LAMP_MARGIN of black around it (the real bezel is hair-thin), then closed
LAMP_MM = unary_union([full(LAMP_BAND), DRL_MM.buffer(LAMP_MARGIN)]).buffer(0.3).buffer(-0.3)
BLADE_MM = LineString(mm(LED_BLADE)).buffer(BLADE_W / 2)
# corner intake grown around the LED blade, then trimmed to keep a FENDER_RIM of white along the body edge
INTAKE_MM = unary_union([Polygon(mm(CORNER_INTAKE)), BLADE_MM.buffer(BLADE_MARGIN)]).intersection(
    OUTLINE_MM.buffer(-FENDER_RIM))

prims = [
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, pts=HOOD_LINE),
    dict(kind='geom', color='groove', geom=plain(PANEL_MM)),
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, pts=CHEEK),
    dict(kind='geom', color='black', geom=plain(INSERT_MM)),
    dict(kind='geom', color='black', geom=plain(LAMP_MM)),
    dict(kind='geom', color='white', geom=plain(DRL_MM)),
    dict(kind='poly', color='black', pts=LOWER_GRILLE),
    dict(kind='geom', color='black', geom=plain(INTAKE_MM)),
    dict(kind='geom', color='white', geom=plain(BLADE_MM)),
    dict(kind='poly', color='black', pts=SPLITTER),
]

# ------------------------------------------------------------------------------------------------ bowtie badge
# The ZL1 wears the hollow "flowtie": a black bowtie with a bright chrome edge. Drawn as a white bowtie OUTLINE
# (BOW_LINE mm) with a black interior on the black strip; BOW_STYLE = 'solid' gives the plain white bowtie instead.
# Point-symmetric Chevrolet shape: centre block + two arms, all side edges leaning "/". Photo: 9.1 x 2.7 mm, arms
# ~1.35 mm, centre block ~2.5 mm wide, centred at y ~807 px; the outline version is a touch taller (arms 1.7 mm) so
# the black inside the arms stays >= 0.6 mm.
BOW_STYLE = 'outline'
BOW_W, BOW_H, BOW_ARM, BOW_CW = 8.3, 3.0, 1.86, 2.8    # mm: arm-end width at mid-height, centre height, arm height,
                                                       # centre block width (overall ~9.3 x 3.0 mm)
BOW_LINE = 0.62                      # mm, white outline width (inner arm black = BOW_ARM - 2 * BOW_LINE)
END_LEAN, MID_LEAN = 0.55, 0.12    # "/" lean (dx per mm of height) of the arm ends and of the centre block sides
BOW_Y_PX = 807.5                     # badge centre (photo px)
if BOW_STYLE == 'solid':
    BOW_W, BOW_H, BOW_ARM, BOW_CW = 8.25, 2.6, 1.42, 2.65


def bowtie():
    Wb, H, A, Cw = BOW_W / 2, BOW_H / 2, BOW_ARM / 2, BOW_CW / 2
    e = lambda x, y: (x + END_LEAN * y, y)
    m = lambda x, y: (x + MID_LEAN * y, y)
    pts = [e(-Wb, -A), m(-Cw, -A), m(-Cw, -H), m(Cw, -H), m(Cw, -A), e(Wb, -A),
           e(Wb, A), m(Cw, A), m(Cw, H), m(-Cw, H), m(-Cw, A), e(-Wb, A)]
    return Polygon(pts).buffer(0)


if SHOW_BADGE:
    BOW = affinity.translate(bowtie(), 0, (YB - BOW_Y_PX) * S)
    if BOW_STYLE == 'outline':
        BOW_IN = BOW.buffer(-BOW_LINE, join_style=2)
        prims.append(dict(kind='geom', color='white', geom=plain(BOW.difference(BOW_IN)), mirror=False))
        # hollow like the real flowtie: the black inside is a plain relief pocket (no ribs), so it also stays black
        # in the flat previews (a black island inside a white ring)
        prims.append(dict(kind='geom', color='relief', geom=plain(BOW_IN), mirror=False, relief=dict(type='none')))
    else:
        prims.append(dict(kind='geom', color='white', geom=plain(BOW), mirror=False))


# ------------------------------------------------------------------------------------------------ grille relief
# The ZL1 lower grille = stacked glossy wavy bars, all with the same profile (measured on the photo, round 3):
# lowest at the centreline (a V following the grille's V lower edge, rounded at the bottom), rising 0.27 mm/mm to
# |x| ~8.2 mm, a flatter run (0.14), a sharp kink DOWN of ~1.25 mm over ~2.2 mm, then rising 0.27 mm/mm again to the
# frame. The kinks sit on a slanted line parallel to the grille's side walls (higher bars kink further out).
# Custom relief: one 1.0 mm rib per bar (PITCH apart), a RIM-wide frame rib along the recess wall; the black gaps
# are opened by CLIP_MIN_W so the bar/frame wedges never leave slivers, and scraps smaller than CLIP_MIN_AREA mm2
# are filled.
PITCH, RIB, RIM = 2.8, 0.95, 0.7
BAR_Y0, N_BARS = 7.85, 4   # centreline height (mm) of the lowest bar (it hugs the V lower edge, as on the car) and
                           # the number of bars (photo: 4 V bars at 6.9 / 9.65 / 12.5 / 15.9 mm; no bar in the top V)
V_SLOPE, V_X, PLAT_SLOPE, OUT_SLOPE = 0.27, 8.2, 0.10, 0.27
KINK_X0, KINK_SH, KINK_W, KINK_D = 12.5, 0.21, 2.2, 1.25   # kink start |x| at y=12.5 mm, its shift per mm of height
V_ROUND = 1.3              # half-width (mm) of the rounded bottom of the V
CLIP_MIN_W, CLIP_MIN_AREA = 0.7, 0.6


def bar_profile(yk):
    """(|x|, dy) vertices of one bar's half profile (dy up, 0 at the centreline)"""
    xk = KINK_X0 + KINK_SH * (yk - 12.5)
    pk = V_SLOPE * V_X + PLAT_SLOPE * (xk - V_X)
    pts = [(0.0, 0.0), (V_ROUND, 0.25 * V_SLOPE * V_ROUND), (V_X, V_SLOPE * V_X), (xk, pk),
           (xk + KINK_W, pk - KINK_D), (45.0, pk - KINK_D + OUT_SLOPE * (45.0 - xk - KINK_W))]
    return pts


def bar_line(yk):
    half = bar_profile(yk)
    pts = [(-x, yk + d) for x, d in reversed(half[1:])] + [(x, yk + d) for x, d in half]
    return LineString(geom.chaikin(pts, 1, closed=False))


def grille_relief(y0=None):
    y0 = BAR_Y0 if y0 is None else y0
    region = full(LOWER_GRILLE)
    zone = region.buffer(-RIM, join_style=2)
    b = region.bounds
    bars = unary_union([bar_line(y0 + k * PITCH).buffer(RIB / 2, cap_style=2, join_style=1)
                        for k in range(-2, N_BARS)])
    holes = zone.difference(bars)
    r = CLIP_MIN_W / 2
    holes = holes.buffer(-r, join_style=1).buffer(r, join_style=1).intersection(holes)
    holes = unary_union([q for q in geom.polys(holes) if q.area >= CLIP_MIN_AREA])
    ribs = geom.clean(region.difference(holes))
    for _ in range(2):
        ribs = geom.regularize(region, ribs, 0.64)
    # overlap the recess wall by 0.05 mm so the pipeline's own (snapped) region clip leaves no zero-width gap slivers
    ribs = unary_union([ribs, region.buffer(0.05, join_style=2).difference(region.buffer(-0.2, join_style=2))])
    return region, ribs


_REG, _RIBS = grille_relief()
prims.append(dict(kind='geom', color='relief', geom=plain(_REG), mirror=False,
                  relief=dict(type='custom', ribs=plain(_RIBS))))

# keyring tab: centred on the white fender side between the lamp's outer end and the corner intake
TAB_Y_PX = 785
SPEC = dict(
    id='camaro_zl1', name='Chevrolet Camaro ZL1 (6th gen)',
    ref='kc/cars/camaro_zl1/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_mm=round((YB - TAB_Y_PX) * S, 2)),
    badge_on=SHOW_BADGE,
)
