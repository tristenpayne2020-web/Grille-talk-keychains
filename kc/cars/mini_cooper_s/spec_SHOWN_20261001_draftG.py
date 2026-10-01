# MINI Cooper S (F56 hatch, pre-LCI 2014-2018) - front keychain, same product line as the user's G80.
# Reference: Wikimedia Commons "MINI F56 Hatch Cooper S Chili Red (1).jpg" by Damian B Oh, CC BY-SA 4.0
#   https://commons.wikimedia.org/wiki/File:MINI_F56_Hatch_Cooper_S_Chili_Red_(1).jpg
#   ref/front.jpg = original resized to 2000x1500 and cropped (150,200,1850,1400).
# The photo is slightly yawed (car's left side visible on the viewer's right), so the viewer's RIGHT half
# (the near half) is traced and mirrored.  centre = badge / grille centre (CX).
# Rev 1 - perspective correction: everything outboard of the grille (x > T) sits further back than the nose, so
# the yaw pushes it outward on the near side.  Near/far measurements (body edge 689/523 px, headlight 533/415 px
# from CX) give true half-widths ~606 / ~474 px, so outline points past the grille are pulled in with
# x' = T + (x - T) * K (see mx()); headlight and arch trim are placed directly in corrected coordinates.
# NO LOGOS: no MINI wings, no red "S" grille badge.
import math

CX = 673
T, K = 1100, 0.725          # perspective correction outboard of the grille edge


def mx(x):
    return x if x <= T else T + (x - T) * K


def M(pts):
    return [(mx(x), y) for x, y in pts]


def arc(cx, cy, r, a0, a1, n=48):
    """points on a circle (px), angles in degrees, 0 = right, 90 = UP (photo y grows down)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy - r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


HL_C, HL_R = (1145, 585), 106          # headlight (corrected), black unit incl. chrome bezel
FOG_C = (mx(1181), 888)
EDGE = mx(1364)                        # widest body point (wheel-arch flare)

# S bumper side intake (chrome frame = white poly, opening = same shape shrunk)
INTAKE = [(880, 946), (1026, 936), (1042, 946), (1044, 1016), (1032, 1026), (892, 1026), (879, 1016)]
# opening = frame shrunk 0.8 mm; a short black throat through the frame's inboard side joins it to the mesh band
# (C-shaped chrome bezel, and the black stays one connected region so face.png paints it correctly)
THROAT = [(860, 966), (905, 966), (905, 1004), (860, 1004)]

SPEC = dict(
    id='mini_cooper_s', name='MINI Cooper S (F56)',
    ref='kc/cars/mini_cooper_s/ref/front.jpg',
    units='px', px_left=2 * CX - EDGE, px_right=EDGE, px_bottom=1060, center_x=CX, y_scale=0.92,
    outline_half=M([(CX, 378), (900, 377), (1060, 376), (1160, 380), (1240, 394), (1294, 432), (1334, 486),
                    (1356, 556), (1364, 640), (1364, 780), (1358, 890), (1346, 960), (1320, 1010), (1275, 1040),
                    (1200, 1052), (1000, 1057), (CX, 1060)]),
    outline_smooth=2,
    prims=[
        # --- round headlight: black lens unit, white LED ring DRL hugging the rim, projector dot ---
        dict(kind='circle', color='black', c=HL_C, r=HL_R),
        # ring DRL (small flat-cut break at the bottom keeps the inner black connected to the lens - render.py)
        dict(kind='stroke', color='white', width=1.0, cap='flat',
             pts=arc(HL_C[0], HL_C[1], 87, -85.5, 265.5, 96)),
        dict(kind='circle', color='white', c=(HL_C[0] + 6, HL_C[1] - 10), r_mm=1.1),

        # --- hexagonal grille opening (black), chrome cross bar (white), hex mesh in the upper section ---
        dict(kind='poly', color='black', smooth=1,
             pts=[(CX - 60, 652), (CX, 652), (900, 654), (985, 662), (1040, 705), (1060, 770), (1062, 822),
                  (1048, 864), (1010, 889), (940, 896), (CX, 897), (CX - 60, 897)]),
        dict(kind='poly', color='relief',
             pts=[(CX - 60, 640), (1000, 640), (1050, 700), (1066, 734), (CX - 60, 734)],
             relief=dict(type='hex', pitch=2.6, rib=0.8, offset=0.7)),
        dict(kind='stroke', color='white', width=0.8, cap='flat', pts=[(CX - 5, 733), (1064, 733)]),

        # --- S bumper: continuous lower hex-mesh band, chrome-framed side intakes on top of it ---
        dict(kind='poly', color='black', smooth=2,
             pts=[(CX - 60, 928), (CX, 928), (1026, 921), (1058, 929), (1062, 1026), (1048, 1045), (CX, 1045),
                  (CX - 60, 1045)],
             relief=dict(type='hex', pitch=2.6, rib=0.8, margin=0.75)),
        dict(kind='poly', color='white', smooth=2, pts=INTAKE),
        dict(kind='poly', color='black', smooth=2, pts=INTAKE, offset=-0.8),
        dict(kind='poly', color='black', pts=THROAT),

        # --- round fog lamps (black surround, white lens) ---
        dict(kind='ring', color='black', c=FOG_C, r=60, width=1.0),

        # --- thin black wheel-arch trim at the lower bumper corners (blunt top, blunt bottom end) ---
        dict(kind='poly', color='black', smooth=1,
             pts=[(1277, 785), (1400, 785), (1400, 995), (1250, 995), (1265, 950), (1274, 885)]),

        # --- hood scoop (Cooper S): black slot + engraved scoop outline (~50 px above the headlight centre) ---
        dict(kind='poly', color='black', smooth=2,
             pts=[(CX - 60, 525), (CX, 525), (780, 525), (820, 528), (828, 536), (820, 545), (780, 547), (CX, 547),
                  (CX - 60, 547)]),
        dict(kind='stroke', color='groove', width=0.62, smooth=2,
             pts=[(CX - 60, 505), (CX, 505), (790, 507), (840, 513), (858, 535), (840, 560), (790, 566), (CX, 567),
                  (CX - 60, 567)]),

        # --- clamshell bonnet shut line: along the grille's chrome top, round its upper corner, out under the
        #     headlight; ends ~1 mm inside the silhouette ---
        dict(kind='stroke', color='groove', width=0.62, smooth=1,
             pts=M([(CX - 60, 628), (CX, 628), (900, 630), (990, 641), (1045, 674), (1072, 716), (1094, 730),
                    (1150, 724), (1260, 710), (1338, 700)])),
        # --- lower half of the hexagonal chrome grille surround (outer edge) ---
        dict(kind='stroke', color='groove', width=0.62, smooth=2,
             pts=[(1080, 722), (1094, 760), (1095, 800), (1090, 850), (1068, 892), (1012, 914), (940, 918),
                  (CX, 919), (CX - 60, 919)]),
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
