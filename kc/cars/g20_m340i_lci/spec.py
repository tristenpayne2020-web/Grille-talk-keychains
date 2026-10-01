# BMW M340i (G20 LCI, 2023+) front keychain.
# Reference: BMW Group PressClub photo P90479608 "The new BMW M340i xDrive (09/2022)" (Skyscraper Grey, straight front),
# https://www.press.bmwgroup.com/global/photo/detail/P90479608 - (c) BMW AG, press/editorial image.
# ref/front.jpg = crop (1000,1200)-(3950,2900) of the 4961x3309 HighRes original, scaled 0.5 (1475x850).
# The photo is level and centred (mirror blend at x=739 matches). Traced half = viewer's left (car's right).
import sys, os
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import geom

PX_L, PX_R, PX_B, CX = 78, 1400, 716, 739
KID_XPH, KID_REG = -2.56, 0.64
IM_A, IM_B, IM_H, IM_RIB, IM_XPH, IM_REG = 2.9, 2.1, 1.1, 0.75, -2.4, 0.7
RADAR_RING = 0.75
S = 80.5 / (PX_R - PX_L)                         # mm per photo pixel


def mm(p):
    return ((p[0] - CX) * S, (PX_B - p[1]) * S)


def hexmesh(a, b, h, rib, x_phase, y_phase, x_lo=-45, x_hi=45, y_lo=-2, y_hi=45):
    """Stretched honeycomb (pointy left/right cells, flat top/bottom) as rib geometry in keychain mm.
    Cell: vertices (+-a, 0), (+-b, +-h); column step a+b; odd columns shifted by h."""
    cells = []
    step = a + b
    i0, i1 = int(x_lo / step) - 2, int(x_hi / step) + 2
    for i in range(i0, i1 + 1):
        x = x_phase + i * step
        for j in range(int(y_lo / (2 * h)) - 3, int(y_hi / (2 * h)) + 3):
            y = y_phase + j * 2 * h + (h if i % 2 else 0)
            hexa = Polygon([(x + a, y), (x + b, y + h), (x - b, y + h), (x - a, y), (x - b, y - h), (x + b, y - h)])
            cells.append(hexa.buffer(-rib / 2, join_style=2))
    return box(x_lo, y_lo, x_hi, y_hi).difference(unary_union(cells))


def mirrored(g):
    return unary_union([g, affinity.scale(g, xfact=-1, yfact=1, origin=(0, 0))])


# ---------------------------------------------------------------------------------------------- traced shapes (px)
OUTLINE = [(739, 116), (600, 116), (450, 117), (330, 119), (262, 122), (246, 130), (236, 140), (224, 150),
           (211, 160), (197, 170), (187, 180), (178, 191), (170, 202), (160, 213), (148, 224), (133, 236),
           (117, 250), (104, 263), (95, 276), (89, 292), (84, 316), (80, 345), (78, 380), (78, 420), (79, 480),
           (80, 560), (81, 630), (84, 662), (90, 678), (100, 686), (130, 689), (224, 691), (240, 704), (262, 707),
           (330, 711), (500, 715), (739, 716)]

HEADLIGHT = [(131, 265), (150, 260), (180, 262), (220, 267), (260, 273), (300, 281), (340, 289), (375, 296),
             (388, 300), (390, 340), (388, 377), (360, 377), (300, 373), (250, 368), (200, 362), (160, 356),
             (135, 348), (120, 337), (112, 322), (109, 300), (115, 282), (121, 270)]

KIDNEY = [(739, 284), (715, 277), (690, 272), (640, 267), (580, 264), (520, 264), (470, 268), (445, 275),
          (425, 284), (412, 294), (406, 306), (404, 325), (406, 345), (409, 365), (416, 380), (430, 395),
          (451, 409), (481, 419), (530, 425), (600, 427), (660, 426), (700, 423), (725, 418), (739, 415)]

KIDNEY_MESH = [(726, 300), (722, 292), (710, 287), (680, 285), (600, 283), (520, 283), (476, 285), (452, 291),
               (435, 300), (425, 314), (421, 335), (423, 358), (431, 378), (447, 393), (468, 403), (500, 410),
               (600, 414), (680, 413), (712, 409), (724, 400), (727, 380), (727, 320)]

# LCI daytime running lights: two inverted-L elements per side. Leg ~0.8 mm (slanted, thicker), top bar ~0.65 mm
# with an angled inner end, small rounded outer corner. Legs stop ~0.7 mm above the lens bottom (printable black).
DRL_OUTER = [(145, 339), (128, 301), (128, 292), (133, 284), (141, 279), (235, 288), (228, 298), (152, 291),
             (147, 294), (145, 302), (159, 337)]
DRL_INNER = [(247, 355), (231, 320), (232, 311), (238, 303), (250, 297), (377, 312), (372, 323), (270, 310),
             (257, 310), (250, 315), (249, 323), (262, 353)]

INTAKE = [(739, 443), (600, 443), (450, 443), (352, 444), (332, 446), (302, 466), (280, 504),
          (283, 520), (292, 552), (305, 580), (318, 607), (332, 632), (345, 648), (362, 657), (400, 660),
          (500, 661), (600, 662), (739, 663)]

INTAKE_POCKET = [(436, 453), (352, 453), (334, 457), (315, 470), (299, 490), (292, 506), (296, 525), (306, 550),
                 (318, 577), (330, 603), (339, 621), (436, 590)]

# mesh only below the plate panel (y 545-654 px); the band above (plate + PDC sensors) stays plain flush black
INTAKE_MESH = [(739, 545), (452, 545), (452, 603), (348, 637), (356, 648), (370, 652), (500, 653), (739, 654)]

CURTAIN = [(116, 442), (138, 442), (147, 450), (150, 468), (150, 582), (296, 645), (298, 651), (290, 657),
           (250, 661), (170, 660), (135, 654), (117, 640), (109, 622), (106, 600), (106, 470), (108, 452)]

# black textured lower lip: top = the real bumper bottom edge (~683 px at the centre), ~2.0 mm tall at the centre,
# chamfered ends where the outline steps down (no thin taper)
LIP = [(224, 690), (300, 684), (400, 678), (500, 680), (600, 682), (739, 683), (739, 760), (224, 760)]

# ACC radar housing in the middle of the lower mesh: U-shaped frame hanging from the plate panel (traced half, px).
# Its top is drawn above the mesh top so the frame ring only runs down the sides and along the bottom.
RADAR = [(739, 530), (672, 530), (672, 545), (664, 558), (660, 575), (660, 600), (664, 617), (672, 632), (684, 644),
         (700, 651), (715, 654), (739, 654)]

# the gloss radar cover inside the frame, raised to rib level (reads as the real radar panel)
RADAR_COVER = [(739, 558), (701, 558), (693, 564), (689, 585), (692, 608), (700, 614), (739, 614)]

# ---------------------------------------------------------------------------------------------- relief patterns (mm)
# kidney: M-Sport LCI mesh = large stretched hexagons (flats ~2.4 mm, point-to-point ~3.7 mm, rows 2.0 mm),
# columns at x = -(2.56 + 3.05 k) mm: the pointed vertex of the innermost column sits on the centre wall
_k = hexmesh(a=1.83, b=1.22, h=1.0, rib=0.7, x_phase=KID_XPH, y_phase=(PX_B - 350) * S, x_lo=-45, x_hi=-0.05)
_kreg = mirrored(Polygon([mm(p) for p in KIDNEY_MESH]))
KIDNEY_RIBS = geom.regularize(_kreg, mirrored(_k).intersection(_kreg), KID_REG)   # no slivers along the pocket walls
# lower centre intake (below the plate panel only): flat, wide hexagons, columns 5.0 mm apart at x = -(2.4 + 5k) mm
# (measured: column centres at -7.4 / -12.4 / -17.4 mm, so the blade cuts the outer column through its middle as on
# the car); the columns next to the plate panel have their flat rib on the panel edge. Mirrored: the centreline seam
# is hidden behind the radar housing.
_ireg = mirrored(Polygon([mm(p) for p in INTAKE_MESH]))
_im = mirrored(hexmesh(a=IM_A, b=IM_B, h=IM_H, rib=IM_RIB, x_phase=IM_XPH, y_phase=(PX_B - 545) * S, x_lo=-45, x_hi=0.0))
_rad = mirrored(Polygon([mm(p) for p in RADAR]))
_rad_in = _rad.buffer(-RADAR_RING, join_style=1)
_cover = mirrored(Polygon([mm(p) for p in RADAR_COVER]))
INTAKE_RIBS = geom.regularize(_ireg, unary_union([_im.difference(_rad), _rad.difference(_rad_in), _cover]).intersection(_ireg),
                              IM_REG)

SPEC = dict(
    id='g20_m340i_lci', name='BMW M340i (G20 LCI)',
    ref='kc/cars/g20_m340i_lci/ref/front.jpg',
    units='px', px_left=PX_L, px_right=PX_R, px_bottom=PX_B, center_x=CX,
    outline_half=OUTLINE,
    prims=[
        # grooves first (black parts painted later cover their ends)
        dict(kind='stroke', color='groove', width=0.62, smooth=2,
             pts=[(182, 268), (182, 236), (189, 212), (202, 192), (221, 175), (245, 158), (270, 139), (294, 119)]),
        dict(kind='stroke', color='groove', width=0.62, smooth=1,
             pts=[(437, 112), (441, 150), (450, 200), (459, 240), (466, 272)]),
        # M-Sport bumper crease: from the air-curtain top down to the outer vertex of the big intake
        dict(kind='stroke', color='groove', width=0.62, pts=[(140, 445), (280, 504)]),
        # headlight unit + LCI DRL: two inverted-L elements (thin top bar, slanted thicker leg, rounded corner)
        dict(kind='poly', color='black', pts=HEADLIGHT),
        dict(kind='poly', color='white', pts=DRL_OUTER),
        dict(kind='poly', color='white', pts=DRL_INNER),
        # kidneys: gloss-black frame (flush) + recessed M mesh
        dict(kind='poly', color='black', pts=KIDNEY),
        dict(kind='poly', color='black', pts=KIDNEY_MESH, relief=dict(type='custom', ribs=KIDNEY_RIBS)),
        # lower intake: black frame + blades (flush), corner pockets (recessed, plain), centre mesh (recessed hex)
        dict(kind='poly', color='black', pts=INTAKE),
        dict(kind='poly', color='black', pts=INTAKE_POCKET, relief=dict(type='none')),
        dict(kind='poly', color='black', pts=INTAKE_MESH, relief=dict(type='custom', ribs=INTAKE_RIBS)),
        # air curtain slot running into the black lower corner wedge
        dict(kind='poly', color='black', pts=CURTAIN),
        # black lower lip
        dict(kind='poly', color='black', pts=LIP),
    ],
    badge=dict(type='roundel', c=(739, 241), d=3.8),
    tab=dict(y_frac=0.53),
)
