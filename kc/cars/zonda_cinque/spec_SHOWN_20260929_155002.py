# Pagani Zonda Cinque (2009) front keychain.
# Reference: ref/front_press.jpg = Pagani studio press photo of the white/carbon Zonda Cinque (1600x1200, straight on,
# camera at headlight height, centred and level), via the caricos.com gallery. See ref/SOURCE.txt.
# Traced half = viewer's LEFT. Coordinates are photo pixels (1 mm = 15.96 px). Body 80.5 x 30.7 mm.
#
# Design (G80 language):
#  outline  - the two white clamshell fender humps standing above the cowl, the flat cowl/windscreen base between them,
#             straight fender sides, the carbon splitter as the bottom edge. Windscreen, roof scoop, mirrors and tyres
#             dropped.
#  white    - body paint: the two fenders (with the white "leg" that runs down between side intake and lower intake)
#             and the centre stripe (paint -> white), which runs from under the badge down the nose strut.
#  black    - the exposed-carbon hood panel between the fenders (the Cinque's two-tone; CARBON_HOOD), the two headlight
#             clusters (carbon "cat face" of two tilted lobes + the indicator pod), the curved canard on each fender
#             corner, side intakes, lower intake and splitter.
#  white on black (light signature) - per cluster: outer projector = white chrome ring around a dark lens pocket;
#             inner reflector = bright white dish with a small dark bulb-shield pit; indicator = small white ring;
#             fog lamps = white rings in the lower intake.
#  relief   - lower radiator intake and side intakes: the same diamond wire mesh (G80-scale pitch); one unrelieved
#             carbon strake per side in the lower mesh; lamp lenses: plain pockets; splitter top edge: a plain
#             0.7 mm pocket line (reads in both builds, a groove on black would only show in the classic one).
#  grooves  - lower fender crease (kept off the canard so each fender stays one piece); in the all-white variant
#             (CARBON_HOOD = False) also the two hood/fender shut lines.
#  tab      - viewer's left, y_frac 0.63, on the white fender beside the cluster, above the canard.
import os, sys
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

SHOW_BADGE = True
CARBON_HOOD = True          # False = all-white body with the hood shut lines as grooves ("painted hood" variant)
if os.environ.get('KC_CARBON', '').strip() in ('0', '1'):
    CARBON_HOOD = os.environ['KC_CARBON'].strip() == '1'

CX, YB, XL = 806.5, 977, 164
XR = 2 * CX - XL
S = 80.5 / (XR - XL)               # mm per px


def mm(p):
    return ((p[0] - CX) * S, (YB - p[1]) * S)


def P(pts, smooth=0):
    q = [mm(p) for p in pts]
    if smooth:
        q = geom.chaikin(q, smooth, closed=True)
    return Polygon(q).buffer(0)


def mirror(g):
    return affinity.scale(g, xfact=-1, yfact=1, origin=(0, 0))


# ------------------------------------------------------------------ outline
OUTLINE = [(CX, 524), (700, 523.5), (600, 523), (520, 522.5), (460, 522), (441, 521.5),
           (433, 516.5), (425, 509), (410, 497), (395, 490), (375, 487.5), (300, 487), (240, 488), (220, 490.5),
           (205, 496), (192, 505), (181, 519), (173, 534), (167.5, 551), (165, 570), (164, 600), (164, 700),
           (164, 800), (164, 900), (164, 935), (165.5, 950), (171, 961), (182, 968), (230, 972), (300, 974),
           (400, 975.5), (600, 976.5), (CX, 977)]

# ------------------------------------------------------------------ headlight cluster (carbon surround)
# pod shoulder left of the indicator pushed out (322,722)/(327,728) so the bigger indicator ring keeps >= 0.6 mm black
CLUSTER = [(355, 644), (347, 634), (339, 620), (326, 602), (314, 590), (300, 584), (288, 584), (276, 592),
           (266, 608), (260, 630), (259.5, 660), (264, 678), (272, 692), (284, 704), (298, 712), (312, 718),
           (322, 722), (324, 729), (328, 741), (338, 753), (354, 760), (368, 757), (377, 748), (384, 737),
           (387, 730), (394, 729.5), (410, 729.5), (424, 728), (438, 722), (448, 710), (454, 694), (455.5, 674),
           (452, 656), (446, 644), (438, 630), (428, 618), (416, 608), (404, 602), (392, 601), (380, 604),
           (368, 620), (362, 636)]
LAMP_OUT = (304, 658)       # outer projector: chrome ring, dark lens
LAMP_IN = (410, 671)        # inner reflector: bright dish, dark bulb shield
INDICATOR = (355, 721)
LAMP_R, LAMP_W = 1.75, 0.65          # mm, projector ring
DISH_R, BULB_R = 1.65, 0.35          # mm, reflector dish + bulb-shield pit
IND_R, IND_W = 1.25, 0.62

# ------------------------------------------------------------------ canard (upper dive plane on the fender corner)
# outer edge kept >= 1.2 mm inside the body edge (tab root / thin white wall), tip at (254,821)-(253,830) kept sharp
CANARD = [(184, 736), (191, 734), (196, 752), (205, 770), (215, 786), (227, 798), (241, 810), (254, 821),
          (253, 830), (245, 827), (235, 821), (217, 816), (203, 812), (193, 805), (187, 795), (185, 775),
          (184, 752)]

# ------------------------------------------------------------------ lower black: side intake, main intake, splitter
LOWER = [(150, 822), (167, 824), (200, 834), (235, 845), (251, 851), (247, 868), (240, 890), (234, 906),
         (229, 920), (236, 926), (252, 928), (262, 923), (271, 911), (282, 895), (294, 883), (310, 875),
         (340, 871), (400, 870), (490, 866), (600, 862), (CX + 30, 862), (CX + 200, 1200), (100, 1200), (100, 822)]
# side-intake mesh pocket: closed by a 0.8 mm black lip at the body edge, lower edge on LOWER's line
SIDE_INTAKE = [(177, 826), (200, 834), (235, 845), (251, 851), (247, 868), (240, 890), (234, 906),
               (229, 920), (177, 923)]
MESH_PAT = dict(type='diamond', pitch=2.4, rib=1.0, offset=0.9)    # G80-scale mesh: 1.4 mm holes
MESH_BOT = 930
MESH = [(400, 850), (CX + 30, 850), (CX + 30, MESH_BOT), (400, MESH_BOT)]     # top clipped by LOWER's edge
STRAKE_X, STRAKE_HW = 515, 6.5       # vertical carbon strake in the mesh (0.8 mm wide), unrelieved
FOG = (352, 906)
FOG_R, FOG_W = 1.1, 0.6
# splitter top edge (gloss edge at y~940-948 in the photo): plain pocket line across the full width
SPLIT_Y, SPLIT_W = 946, 0.7
SPLIT_LINE = [(182, SPLIT_Y), (300, SPLIT_Y), (500, SPLIT_Y), (CX + 30, SPLIT_Y)]

# ------------------------------------------------------------------ hood panel (carbon) / its shut lines
HOOD_LINE = [(446, 529), (455, 552), (463, 572), (470, 596), (476, 625), (482, 670), (486, 720), (488.5, 780),
             (489.5, 840), (490, 870)]
HOOD = [(420, 470), (441, 521.5)] + HOOD_LINE + [(490, 875), (CX + 30, 875), (CX + 30, 480)]
GW = 0.62
# lower fender crease (bright/grey fold measured at y 830-838): starts 2.6 mm clear of the canard tip, so the white
# fender stays one piece
CREASE = [(300, 827.5), (350, 830), (400, 832.5), (450, 835), (492, 837)]
STRIPE_HW = 18              # px half width of the centre stripe / nose strut (2.25 mm), one constant width
STRIPE_BOT = MESH_BOT       # stripe ends flush with the mesh bottom, 0.6 mm above the splitter line

# ------------------------------------------------------------------ Pagani badge (shield + oval)
BADGE_TOP = 535             # px, shield top corners (0.65 mm under the cowl edge at y=524)
BADGE_W, BADGE_H = 5.8, 5.0  # mm (real badge ~6.3 x 5.3)
BADGE_GAP = 0.7             # mm black gap between shield tip and stripe top


def ring_lamp(c, r, w):
    """white ring on the black cluster; the lens inside is a relief pocket (one step deeper)"""
    return [dict(kind='ring', color='white', c=c, r_mm=r, width=w),
            dict(kind='circle', color='relief', c=c, r_mm=r - w + 0.01, relief=dict(type='none'))]


def dish_lamp(c, r, dot):
    """bright reflector: solid white dish, dark bulb shield as a small pit (black + pocket, so it shows in face.png)"""
    return [dict(kind='circle', color='white', c=c, r_mm=r),
            dict(kind='circle', color='black', c=c, r_mm=dot),
            dict(kind='circle', color='relief', c=c, r_mm=dot, relief=dict(type='none'))]


def badge():
    """Pagani shield: raised top corners with a concave top edge, sides converging to a rounded tip; oval inside"""
    cx, top = mm((CX, BADGE_TOP))
    w, h = BADGE_W, BADGE_H
    half = [(0, -0.26), (w * 0.25, -0.21), (w * 0.42, -0.10), (w * 0.50, 0.06), (w * 0.51, -0.25),
            (w * 0.50, -h * 0.30), (w * 0.47, -h * 0.50), (w * 0.38, -h * 0.70), (w * 0.23, -h * 0.87),
            (w * 0.08, -h * 0.98), (0, -h)]
    pts = [(cx + x, top + y) for x, y in half] + [(cx - x, top + y) for x, y in reversed(half[1:-1])]
    sh = Polygon(geom.chaikin(pts, 1, closed=True)).buffer(0)
    oval = affinity.scale(Point(cx, top - h * 0.50).buffer(1.0, 64), 1.75, 0.58)
    return sh, oval


_sh, _ov = badge()
BADGE_BOTTOM_PX = YB - _sh.bounds[1] / S          # px y of the shield tip
_strake = P([(STRAKE_X - STRAKE_HW, 850), (STRAKE_X + STRAKE_HW, 850), (STRAKE_X + STRAKE_HW, MESH_BOT + 3),
             (STRAKE_X - STRAKE_HW, MESH_BOT + 3)]).intersection(P(LOWER, smooth=1))

prims = [dict(kind='poly', color='black', pts=CLUSTER, smooth=2)]
prims += ring_lamp(LAMP_OUT, LAMP_R, LAMP_W)
prims += dish_lamp(LAMP_IN, DISH_R, BULB_R)
prims += ring_lamp(INDICATOR, IND_R, IND_W)
prims += [
    dict(kind='poly', color='black', pts=CANARD, smooth=1),
    dict(kind='poly', color='black', pts=LOWER, smooth=1),
    dict(kind='poly', color='relief', pts=SIDE_INTAKE, relief=MESH_PAT),
    dict(kind='poly', color='relief', pts=MESH, relief=MESH_PAT),
    # strake: white then black repaint cuts it out of the mesh pocket (the mesh pattern stays one aligned grid)
    dict(kind='geom', color='white', geom=_strake),
    dict(kind='geom', color='black', geom=_strake),
]
if CARBON_HOOD:
    s_top = BADGE_BOTTOM_PX + BADGE_GAP / S         # stripe starts 0.7 mm below the badge tip (also with badge off)
    prims += [dict(kind='poly', color='black', pts=HOOD),
              dict(kind='poly', color='white', pts=[(CX - STRIPE_HW, s_top), (CX - STRIPE_HW, STRIPE_BOT),
                                                    (CX + 1, STRIPE_BOT), (CX + 1, s_top)])]
else:
    prims += [dict(kind='poly', color='white', pts=[(CX - STRIPE_HW, 850), (CX - STRIPE_HW, STRIPE_BOT),
                                                    (CX + 1, STRIPE_BOT), (CX + 1, 850)]),
              dict(kind='stroke', color='groove', width=GW, pts=HOOD_LINE, smooth=1)]
prims += ring_lamp(FOG, FOG_R, FOG_W)
prims += [dict(kind='stroke', color='relief', width=SPLIT_W, pts=SPLIT_LINE, relief=dict(type='none'))]
# crease groove only on the white fender: clipped at the (carbon) hood edge
_crease = LineString(geom.chaikin([mm(p) for p in CREASE], 1, closed=False)).buffer(GW / 2, cap_style=1, join_style=1)
if CARBON_HOOD:
    _crease = _crease.difference(P(HOOD))
prims += [dict(kind='geom', color='groove', geom=geom.clean(_crease))]

if SHOW_BADGE:
    if CARBON_HOOD:     # solid white shield on the carbon, black oval
        prims += [dict(kind='geom', color='white', geom=_sh, mirror=False),
                  dict(kind='geom', color='black', geom=_ov, mirror=False)]
    else:               # black shield on the white hood, white oval
        prims += [dict(kind='geom', color='black', geom=_sh, mirror=False),
                  dict(kind='geom', color='white', geom=_ov, mirror=False)]

SPEC = dict(
    id='zonda_cinque', name='Pagani Zonda Cinque',
    ref='kc/cars/zonda_cinque/ref/front_press.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.63),
    badge_on=SHOW_BADGE,
)
