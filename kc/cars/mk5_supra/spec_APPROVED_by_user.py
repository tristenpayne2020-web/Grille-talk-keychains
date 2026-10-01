# Toyota GR Supra (A90 / MK5, 2020+) front keychain.
# Reference: ref/front.jpg = Toyota USA Newsroom press photo (2020 GR Supra Launch Edition, Absolute Zero white),
# camera at headlight height, levelled +2.74 deg and cropped (see ref/SOURCE.txt). Traced half = viewer's LEFT (the
# right half shows a little more of the car's side through a slight yaw). Coordinates = photo px (1 mm = 18.98 px).
#
# Design (G80 language):
#  white  = body paint (hood, fenders, the nose cone with the badge, the two "fang" pillars between the intakes and the
#           body-colour blades under the outer intakes, the lower corner legs).
#  black  = headlight units (whole lens), the vertical side vents behind the lamps, the two outer intakes (with their
#           flat black upper inserts), the big central lower intake, and one full-width splitter that wraps up the
#           outer corners as the canards and joins the central intake and the outer intakes' lower corners, like the
#           photo; the parking sensors (rings on the pillars); the Toyota badge (SHOW_BADGE).
#  white on black = the light signature: the LED DRL light guide that runs up the lamp's outer side and along its
#           lower edge into the tail (0.70 mm, 0.65 mm of bezel outside it), and the three LED projector cells
#           ("six-lens" lamps) as small rounded squares along the lamp top.
#  relief = the product line honeycomb (pitch 2.4, rib 0.8) in all three intakes (the real car has the same mesh in
#           all of them); the outer intakes' upper inserts are left flat black (rib height).
#  grooves (0.55 mm) = the hood's front shut line running across the nose between the lamps, and the nose-cone crease
#           that leaves each lamp's inner corner and sweeps down under the badge (the Supra's protruding centre nose).
import os, sys, math
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):   # badge-free export, no edit
    SHOW_BADGE = False

CX, YB = 899, 1023                    # centreline, splitter bottom (px)

# ------------------------------------------------------------------------------------------------ outline
OUTLINE = [(899, 312), (800, 313), (700, 315), (600, 318), (530, 323), (480, 330), (445, 337), (420, 341),
           (380, 349), (340, 360), (310, 372), (285, 388), (262, 405), (240, 427), (220, 450), (200, 475),
           (185, 497), (172, 518), (160, 540), (150, 565), (144, 590), (140, 620), (138, 660), (138, 700),
           (139, 740), (141, 780), (141, 820), (137, 840), (135, 870), (135, 930), (136, 965), (140, 988),
           (150, 998), (200, 1003), (300, 1007), (450, 1012), (600, 1016), (700, 1019), (800, 1022), (899, 1023)]
XL = min(x for x, y in OUTLINE)
XR = 2 * CX - XL
S = 80.5 / (XR - XL)                  # mm per px


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


def sym(g):
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])


# ------------------------------------------------------------------------------------------------ parts (px)
HEADLIGHT = [(186, 540), (190, 518), (198, 503), (210, 494), (228, 489), (255, 487), (290, 488), (330, 492),
             (365, 498), (392, 503), (406, 508), (418, 518), (432, 533), (448, 553), (463, 574), (478, 596),
             (492, 612), (505, 622), (525, 628), (555, 634), (585, 642), (610, 654), (627, 670), (632, 681),
             (622, 684), (600, 681), (560, 673), (500, 661), (440, 649), (380, 638), (320, 627), (265, 616),
             (228, 607), (208, 600), (195, 590), (188, 572), (185, 555)]
# DRL light guide: runs up the lamp's outer side and along its lower edge into the tail; drawn as the lamp's
# outer+lower edge offset DRL_IN into the lens (-> exactly DRL_IN - DRL_W/2 of black bezel outside it), ending at DRL_END
LAMP_EDGE = [(185, 534), (185, 555), (188, 572), (195, 590), (208, 600), (228, 607), (265, 616), (320, 627),
             (380, 638), (440, 649), (500, 661), (560, 673), (600, 681), (622, 684)]
DRL_IN, DRL_END = 1.0, 565          # mm, px
LED_CELLS = [(262, 524), (320, 535), (377, 544)]          # the three LED projector cells (centres, px)
LED_W, LED_H, LED_R = 1.85, 1.55, 0.4                     # mm
SIDE_VENT = [(184, 606), (195, 615), (207, 636), (215, 665), (218, 700), (216, 730), (209, 752), (198, 762),
             (189, 756), (183, 735), (180, 700), (179, 660), (180, 630)]
OUTER_INTAKE = [(305, 748), (400, 752), (500, 764), (580, 776), (622, 785), (628, 792), (624, 830), (615, 870),
                (603, 905), (594, 922), (580, 926), (300, 922), (288, 930), (292, 955), (305, 968), (330, 978),
                (330, 1000), (250, 1000), (256, 960), (258, 900), (260, 850), (266, 810), (276, 782), (290, 760)]
MESH_OUTER = [(305, 748), (400, 752), (500, 764), (580, 776), (622, 785), (628, 792), (624, 830), (615, 870),
              (603, 905), (594, 922), (580, 926), (300, 922), (270, 922), (258, 900), (260, 850), (266, 810),
              (276, 782), (290, 760)]
INSERT = [(330, 735), (500, 745), (515, 770), (535, 795), (538, 822), (526, 842), (500, 849), (345, 849),
          (325, 838), (320, 810), (322, 760)]
CENTER_INTAKE = [(899, 783), (716, 783), (704, 791), (698, 810), (690, 860), (682, 910), (674, 960), (665, 995),
                 (657, 1010), (657, 1040), (899, 1040)]
CENTER_MESH = [(899, 783), (716, 783), (704, 791), (698, 810), (690, 860), (682, 910), (677, 962), (899, 962)]
SPLITTER = [(899, 1004), (660, 1004), (640, 1003), (500, 990), (360, 977), (330, 976), (256, 935), (240, 950),
            (210, 958), (185, 948), (175, 930), (168, 900), (160, 860), (148, 832), (137, 828), (120, 830),
            (120, 1040), (899, 1040)]
SENSOR = (655, 833)
HOOD_LINE = [(404, 507), (480, 507), (560, 506), (650, 502), (750, 498), (899, 496), (912, 496)]
NOSE_ARC = [(438, 530), (500, 553), (560, 576), (620, 599), (680, 620), (740, 637), (800, 647), (860, 652),
            (899, 653), (912, 653)]
BADGE_C = (900, 582)

GROOVE_W = 0.55
DRL_W = 0.70


def rrect(c, w, h, r):
    x, y = mm([c])[0]
    return box(x - w / 2 + r, y - h / 2 + r, x + w / 2 - r, y + h / 2 - r).buffer(r, 32)


def drl():
    line = LineString(geom.chaikin(mm(LAMP_EDGE), 2, closed=False)).offset_curve(DRL_IN, join_style=1)
    line = line.intersection(box(-60, -10, (DRL_END - CX) * S, 60))
    return line.buffer(DRL_W / 2, 32)


prims = [
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, pts=HOOD_LINE),
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, pts=NOSE_ARC),
    dict(kind='poly', color='black', pts=HEADLIGHT),
    dict(kind='geom', color='white', geom=drl()),
] + [dict(kind='geom', color='white', geom=rrect(c, LED_W, LED_H, LED_R)) for c in LED_CELLS] + [
    dict(kind='poly', color='black', pts=SIDE_VENT, smooth=2),
    dict(kind='poly', color='black', pts=OUTER_INTAKE),
    dict(kind='poly', color='black', pts=CENTER_INTAKE, mirror=True),
    dict(kind='poly', color='black', pts=SPLITTER),
    dict(kind='ring', color='black', c=SENSOR, r_mm=0.95, width=0.5),
]

# honeycomb mesh (product line cell: pitch 2.4, rib 0.8) in the three intakes; the outer intakes' upper inserts
# stay flat black
HEX = dict(type='hex', pitch=2.4, rib=0.8)
_outer = sym(Polygon(mm(MESH_OUTER)).buffer(0)).difference(sym(Polygon(mm(INSERT)).buffer(0)))
prims += [dict(kind='geom', color='relief', geom=_outer, mirror=False, relief=HEX),
          dict(kind='poly', color='relief', pts=CENTER_MESH, relief=HEX)]


# ------------------------------------------------------------------------------------------------ Toyota badge
# Simplified three-oval emblem, 7.0 x 3.44 mm (photo: 6.5 x 3.2 mm, same 2.03:1 aspect as seen on the sloping nose).
# Black ellipse = the badge; white 0.5 mm strokes = the vertical oval + the horizontal oval (both share their top,
# like the real "T"). The chrome outer ring is the black/white edge itself, and the horizontal oval's lower arc inside
# the vertical oval is dropped: at 3.4 mm there is no room for either with >= 0.5 mm black gaps.
BADGE_A, BADGE_B, BADGE_W = 3.5, 1.72, 0.5          # black ellipse semi-axes, stroke width (mm)
BADGE_GTOP, BADGE_GBOT = 0.55, 0.5                  # black above / below the ovals
BADGE_AH, BADGE_BH, BADGE_AV = 2.45, 0.78, 0.66     # horizontal oval semi-axes, vertical oval semi-width (centrelines)
BADGE_ROUND = 0.12                                  # the small black cells inside the ovals get round ends (r mm)


def _ell(a, b, y=0.0):
    return affinity.translate(affinity.scale(Point(0, 0).buffer(1, 128), a, b), 0, y)


def toyota_badge():
    w = BADGE_W
    top = BADGE_B - BADGE_GTOP - w / 2               # shared top of both ovals (centreline)
    bot = -(BADGE_B - BADGE_GBOT - w / 2)            # bottom of the vertical oval (centreline)
    bv, yv = (top - bot) / 2, (top + bot) / 2
    yh = top - BADGE_BH
    base = _ell(BADGE_A, BADGE_B)
    vert = _ell(BADGE_AV, bv, yv).exterior.buffer(w / 2, 32)
    horz = _ell(BADGE_AH, BADGE_BH, yh).exterior.buffer(w / 2, 32).difference(_ell(BADGE_AV - w / 2, bv - w / 2, yv))
    white = unary_union([vert, horz]).intersection(base)
    # the two black cells inside the horizontal oval end in hair-thin tips where the ovals meet: a local opening turns
    # them into round-ended cells (~0.8 mm across, 0.83 mm2) that a 0.4 mm nozzle fills in the classic inlay
    black = unary_union([q.buffer(-BADGE_ROUND, 32).buffer(BADGE_ROUND, 32) if q.area < 1.5 else q
                         for q in geom.polys(base.difference(white))])
    white = base.difference(black)
    x, y = mm([BADGE_C])[0]
    return affinity.translate(base, 0, y), affinity.translate(white, 0, y)


if SHOW_BADGE:
    _bb, _bw = toyota_badge()
    prims += [dict(kind='geom', color='black', geom=_bb, mirror=False),
              dict(kind='geom', color='white', geom=_bw, mirror=False)]

SPEC = dict(
    id='mk5_supra', name='Toyota GR Supra (A90 / MK5)',
    ref='kc/cars/mk5_supra/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.52),
    badge_on=SHOW_BADGE,
)
