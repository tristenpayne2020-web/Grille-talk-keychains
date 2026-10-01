# Porsche Cayenne (E3.2 / PO536 facelift, 2024+) front keychain.
#
# Reference: caricos.com gallery "2024 Porsche Cayenne E-Hybrid" #2 (Porsche AG press photo), studio, straight-on,
# camera at about headlight height, Matrix LED four-point DRL lit. ref/front.jpg (2560x1440), see ref/source.json.
# All coordinates are pixels of ref/front.jpg; the viewer's LEFT half is traced and mirrored. Centreline x = 1292.
#
# NO LOGOS (user rule): the hood crest is not drawn, badge=None.
import os
import sys

from shapely.geometry import LineString, Point
from shapely.ops import unary_union

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import geom as _geom

CX = 1292.0
PL, PR = 712.0, 2 * CX - 712.0
YB = 1080.0
_F = _geom.Frame(dict(units='px', px_left=PL, px_right=PR, px_bottom=YB, center_x=CX))


def _mx(pts):
    return [(2 * CX - x, y) for x, y in pts]


def _ribs(lines, w):
    """custom relief ribs (mm) from px polylines of the left half, mirrored"""
    g = []
    for pts in lines:
        for q in (pts, _mx(pts)):
            g.append(LineString(_F.pts(q)).buffer(w / 2, cap_style=2, join_style=2))
    return unary_union(g)


# ------------------------------------------------------------------ outline (left half)
# top = hood rear edge at the windscreen base, A-pillar foot, round fender shoulder, near-vertical side,
# bumper corner, dark lower skid band (tyres excluded)
OUTLINE = [(CX, 538), (1150, 537), (1000, 535), (920, 532), (885, 538), (850, 556), (820, 568), (795, 582),
           (776, 597), (757, 613), (744, 634), (735, 657), (726, 684), (720, 715), (716, 750), (713, 800),
           (712, 850), (713, 920), (716, 980), (721, 1015), (729, 1037), (742, 1056), (757, 1071), (775, 1080),
           (CX, 1080)]

# ------------------------------------------------------------------ headlight + four-point DRL
HEADLIGHT = [(764, 620), (772, 610), (795, 603), (840, 603), (880, 608), (905, 619), (925, 638), (945, 663),
             (962, 688), (975, 705), (952, 715), (915, 721), (865, 721), (802, 716), (768, 706), (760, 695),
             (757, 675), (758, 640)]
DRL_W = 1.1
DRL = [[(795, 633), (832, 633)], [(856, 633), (897, 633)],
       [(798, 671), (834, 671)], [(856, 671), (900, 671)]]

# ------------------------------------------------------------------ lower front
# one black mouth: side intakes + centre grille, joined by the black band above the body-colour posts
MOUTH = [(CX, 779), (1004, 779), (1000, 768), (772, 767), (758, 771), (751, 782), (750, 795), (750, 935), (755, 950),
         (770, 960), (898, 968), (915, 961), (945, 934), (958, 916), (CX, 912)]
# body-colour post between side intake and grille
POST = [(938, 786), (1001, 786), (1003, 906), (930, 900), (936, 888)]
# horizontal body-colour slat through the side intake, running on under the grille
SLAT = [(745, 888), (775, 886), (850, 890), (940, 898), (1010, 904), (CX, 905), (CX, 921), (1010, 921),
        (940, 915), (850, 907), (775, 902), (745, 902)]
# lit DRL strip in the side intake
INTAKE_DRL = [(770, 815), (922, 818)]
# arrow-shaped black notch in the post that the DRL strip points into
NOTCH = [(930, 801), (975, 812), (975, 824), (930, 835)]
# lower part of the side intake (under the slat): vertical fins
LOWER_INTAKE = [(745, 900), (962, 900), (962, 975), (745, 975)]
# centre grille: two horizontal bars + vertical dividers (custom relief)
GRILLE = [(CX, 779), (1004, 779), (1002, 908), (CX, 908)]
GR_H = 1.05   # horizontal bars dominate, as on the car
GR_V = 0.65   # few, light vertical dividers; centre column left open (camera pod)
GRILLE_RIBS_H = [[(1000, 822), (CX, 822)], [(1000, 870), (CX, 870)]]
GRILLE_RIBS_V = [[(CX - 130, 775), (CX - 130, 905)], [(CX - 230, 775), (CX - 230, 905)]]
# lower black slot under the bumper and the dark lower skid band
SLOT = [(916, 1027), (957, 993), (985, 987), (CX, 987), (CX, 1028), (1140, 1028), (960, 1027)]
SKID = [(738, 1049), (765, 1056), (CX, 1056), (CX, 1090), (700, 1090)]

SPEC = dict(
    id='cayenne', name='Porsche Cayenne (E3.2)',
    ref='ref/front.jpg',
    units='px', px_left=PL, px_right=PR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=[
        dict(kind='poly', color='black', pts=HEADLIGHT),
        *[dict(kind='stroke', color='white', width=DRL_W, cap='flat', pts=p) for p in DRL],
        dict(kind='poly', color='black', pts=MOUTH),
        dict(kind='poly', color='white', pts=POST),
        dict(kind='poly', color='white', pts=SLAT),
        dict(kind='poly', color='black', pts=NOTCH),
        dict(kind='stroke', color='white', width=0.8, cap='flat', pts=INTAKE_DRL),
        dict(kind='poly', color='relief', pts=LOWER_INTAKE, relief=dict(type='vbars', pitch=1.7, rib=0.75)),
        dict(kind='poly', color='relief', pts=GRILLE, relief=dict(type='custom', ribs=_ribs(GRILLE_RIBS_H, GR_H).union(_ribs(GRILLE_RIBS_V, GR_V)))),
        dict(kind='poly', color='black', pts=SLOT),
        dict(kind='poly', color='black', pts=SKID),
        # hood: diagonal shut lines from the A-pillar foot down to the hood front edge, which runs between the lamps
        dict(kind='stroke', color='groove', width=0.62, pts=[(893, 556), (1008, 702), (CX, 704)]),
        # hood power-dome creases
        dict(kind='stroke', color='groove', width=0.62, smooth=1, pts=[(1145, 600), (1150, 645), (1154, 688)]),
        # parking sensors
        dict(kind='ring', color='black', c=(820, 990), r_mm=1.1, width=0.5),
        dict(kind='ring', color='black', c=(1088, 957), r_mm=1.1, width=0.5),
    ],
    badge=None,
    tab=dict(y_frac=0.58),
)
