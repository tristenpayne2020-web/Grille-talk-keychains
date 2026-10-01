# Subaru BRZ (2nd gen, ZD8, 2022+) front keychain.
# Reference: ref/front.jpg = Subaru of America media-site studio photo "2024_Subaru_BRZ_tS_14.jpg" (straight-on,
# camera at about headlight height, DRLs lit), cropped (1700,1300)-(6300,4500) of the 8010 px original and halved.
# The tS shares the standard ZD8 front (only the small "BRZ tS" grille badge differs, which is dropped).
# See ref/SOURCE.txt. Traced half = viewer's LEFT. Coordinates = photo px of ref/front.jpg (1 mm = 25.9 px).
#
# Design (G80 language):
#  white  = body paint: the long flat hood (outline top = cowl / windshield base), fenders, the plain nose (NO LOGOS: the badge spot stays plain body),
#           the thin body-colour lip between grille and lower intake, and the body-colour lower bumper corners.
#  black  = headlight units (whole lens), the slim vertical corner vents with their horizontal blade (the BRZ
#           "fangs"), the wide hexagonal grille, the lower intake + splitter lip between the body-colour corners.
#  white on black = the light signature: the C-shaped DRL light guide that runs down the lamp's outer side and along
#           its lower edge to the inner tip (0.80 mm, >= 0.55 mm black bezel), exactly as it lights up in the photo.
#  relief = horizontal slats in the grille (pitch 2.32 = the real fin spacing, phased onto the real fins) and finer
#           slats inside the corner vents (the real vents show horizontal fins behind a flat trim frame, kept flat).
#  grooves (0.62 mm) = hood front shut line across the nose (headlight to headlight), the hood/fender shut lines
#           rising from the lamps' top-outer corners to the cowl, the bumper/fender seams from the lamps' lower-outer
#           corners to the body edge, the stepped grille-surround crease (from under the vent blade, round the
#           grille's outer corner to the lower intake) that gives the face its hexagonal frame.
#  dropped = Subaru badge + all lettering (user rule: no logos), plate recess, front camera, "BRZ tS" grille badge, side markers, tow-hook cover, projector lenses
#           (tried as rings: they turn the lamps into cartoon eyes and hide the DRL signature).
import os, sys, math
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom


CX, YB, XL = 1146, 1382, 106          # centreline, splitter bottom, fender (body) left edge (px)
XR = 2 * CX - XL
S = 80.5 / (XR - XL)                  # mm per px


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


# ------------------------------------------------------------------------------------------------ outline
OUTLINE = [(1146, 492), (900, 492), (700, 493), (500, 495), (400, 497), (340, 500), (300, 507), (272, 521),
           (250, 537), (232, 556), (215, 578), (198, 598), (177, 620), (157, 640), (139, 660), (126, 680),
           (118, 700), (112, 730), (109, 770), (107, 810), (106, 860), (106, 920), (108, 980), (111, 1030),
           (115, 1080), (119, 1140), (124, 1190), (131, 1240), (138, 1280), (145, 1310), (154, 1331),
           (170, 1344), (200, 1351), (300, 1358), (390, 1364), (500, 1372), (650, 1378), (800, 1381), (1146, 1382)]

# ------------------------------------------------------------------------------------------------ parts (px)
HEADLIGHT = [(250, 603), (300, 613), (350, 628), (400, 648), (450, 674), (500, 708), (540, 740), (568, 770),
             (584, 800), (592, 830), (590, 855), (578, 870), (550, 873), (500, 868), (440, 861), (380, 853),
             (320, 843), (282, 832), (255, 812), (236, 790), (222, 760), (214, 725), (212, 690), (214, 655),
             (220, 628), (233, 610)]
# lens outer side + bottom (the DRL light guide runs inside it: the BRZ "C" signature)
LAMP_EDGE = [(236, 606), (220, 628), (214, 655), (212, 690), (214, 725), (222, 760), (236, 790), (255, 812),
             (282, 832), (320, 843), (380, 853), (440, 861), (500, 868), (550, 873), (578, 870), (590, 855)]
DRL_W, DRL_IN, DRL_BEZEL = 0.80, 0.95, 0.55     # mm: stroke width, centreline inset, min black around it
DRL_TOP, DRL_END = 630, 572                    # px: top end (y) of the outer run, inner end (x) of the bottom run

VENT = [(215, 925), (260, 921), (320, 927), (380, 934), (430, 940), (452, 946), (440, 954), (400, 960),
        (340, 965), (295, 968), (272, 976), (262, 992), (266, 1020), (280, 1062), (300, 1110), (318, 1155),
        (330, 1190), (329, 1220), (316, 1246), (290, 1262), (240, 1266), (200, 1259), (180, 1240), (172, 1200),
        (170, 1150), (172, 1080), (178, 1020), (188, 970), (200, 940)]
GRILLE = [(1250, 1018), (1200, 1018), (800, 1017), (600, 1012), (520, 1012), (496, 1016), (483, 1026), (478, 1042), (486, 1064),
          (505, 1102), (526, 1142), (548, 1180), (572, 1212), (598, 1234), (640, 1242), (800, 1243), (1200, 1243), (1250, 1243)]
LOWER = [(1146, 1263), (700, 1263), (575, 1261), (550, 1268), (505, 1293), (465, 1322), (430, 1348), (398, 1363),
         (398, 1420), (1146, 1420)]
HOOD_LINE = [(490, 702), (535, 711), (585, 718), (630, 715), (680, 709), (800, 710), (1000, 713), (1146, 715),
             (1200, 715)]
# body crease of the stepped grille surround: from under the vent blade tip, round the grille's outer corner
SURROUND_LINE = [(548, 962), (480, 984), (446, 1012), (440, 1046), (456, 1090), (488, 1148), (522, 1205), (548, 1246)]
FENDER_LINE = [(266, 608), (262, 572), (264, 542), (271, 512)]
SEAM_LINE = [(214, 748), (160, 782), (100, 820)]
GROOVE_W = 0.62


def drl():
    lens = Polygon(mm(HEADLIGHT)).buffer(0)
    edge = LineString(geom.chaikin(mm(LAMP_EDGE), 2, closed=False))
    line = edge.offset_curve(DRL_IN, join_style=1)
    keep = box((0 - CX) * S, -50, (DRL_END - CX) * S, (YB - DRL_TOP) * S)
    line = line.intersection(keep)
    g = line.buffer(DRL_W / 2, 32)
    return g.intersection(lens.buffer(-DRL_BEZEL))


def vent_opening():
    v = Polygon(geom.chaikin(mm(VENT), 1, closed=True)).buffer(0)
    top = (YB - VENT_OPEN_TOP) * S
    return v.buffer(-VENT_TRIM).intersection(box(-60, -5, 0, top))


VENT_TRIM, VENT_OPEN_TOP = 0.7, 1000         # mm trim left flat, px top of the recessed opening
VENT_BARS = dict(type='hbars', pitch=1.9, rib=0.8, offset=0.5)
GRILLE_BARS = dict(type='hbars', pitch=2.32, rib=1.0, offset=0.68)

prims = [
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, pts=HOOD_LINE),
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=1, pts=FENDER_LINE),
    dict(kind='stroke', color='groove', width=GROOVE_W, pts=SEAM_LINE),
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, pts=SURROUND_LINE),
    dict(kind='poly', color='black', pts=HEADLIGHT, smooth=1),
    dict(kind='geom', color='white', geom=drl()),
    dict(kind='poly', color='black', pts=VENT, smooth=1),
    dict(kind='geom', color='relief', geom=vent_opening(), relief=VENT_BARS),
    dict(kind='poly', color='black', pts=GRILLE, smooth=1, relief=GRILLE_BARS),
    dict(kind='poly', color='black', pts=LOWER),
]


SPEC = dict(
    id='brz_zd8', name='Subaru BRZ (ZD8)',
    ref='kc/cars/brz_zd8/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    badge=None,
    tab=dict(y_frac=0.44),
)
