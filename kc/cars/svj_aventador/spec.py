# Lamborghini Aventador SVJ (2018-2022) front keychain - revision round 3.
#
# Reference: the Lamborghini studio press front view (ref/front.jpg, 1280x853, perfectly symmetric, centreline
# x = 639.5). That photo is shot from high above the hood, so it is first converted to a front elevation by
# ref/elev.py (perspective sag removed, hood/lamp/nose bands compressed, forward-facing intake band stretched;
# proportions checked against the low street photo alt_red_monaco_1146.jpg). The warped photo is
# ref/front_elev.png and ALL coordinates below are pixels of that elevation image (left half, mirrored by the
# pipeline). overlay.png therefore lines up with front_elev.png. Three places are drawn deliberately away from the
# studio photo because its high camera distorts them (checked on the two street photos, which are near straight-on):
#   * top edge (cowl): straight and 9 px lower (the band above y~434 in the studio view is the cowl vent strip /
#     windscreen base seen from above); body ratio 80.5 : 30.3 mm = 2.66, as in the low street photo.
#   * lower corners: the studio view shows the plan-view curve of the bumper. Straight on, the SVJ stands on its
#     splitter (widest at the bottom, ~5 mm corner radius), so the side runs straight down to a tight corner.
#   * bottom edge: straight.
#
# Badge: the library 'shield' (a flat-topped pentagon with 0.6 mm bands) is not used. A Lamborghini crest (pointed
# top corners, slightly arched top, sides tapering continuously into the point) is built here and painted as the
# LAST prim, like the library badge. Switch it off with BADGE_ON = False (same convention as c8_corvette and
# s650_mustang; SPEC['badge'] is None so the library never draws a second one).
import os
import sys

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import geom as _geom                 # read-only use of the pipeline's own clean-up (regularize) for the custom ribs

BADGE_ON = True

CX = 639.5
PL, PR = 328, 2 * CX - 328          # widest body points (front fender sides)
YB = 669                             # lowest outline point (splitter bottom)
S = 80.5 / (PR - PL)                 # mm per px
YS = 1.0                             # no extra vertical scale: elev.py already gives the front elevation
G = 0.55                             # engraved line width (mm): G80 shut lines are 0.45, README asks 0.5-0.6


def mx(pts):
    """mirror px points about the centreline"""
    return [(2 * CX - x, y) for x, y in pts]


def _mm(p):
    x, y = p
    return ((x - CX) * S, (YB - y) * S * YS)


def _mmpoly(pts):
    return Polygon([_mm(p) for p in pts]).buffer(0)


def _both(g):
    """geometry (mm) + its mirror about the centreline"""
    from shapely import affinity
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])


def _ribs(lines, w):
    """relief ribs (mm) from px polylines, both halves"""
    g = []
    for pts in lines:
        for q in (pts, mx(pts)):
            g.append(LineString([_mm(p) for p in q]).buffer(w / 2, cap_style=2, join_style=1))
    return unary_union(g)


def _reg(region, ribs, w=0.64):
    """geom.regularize (the clean-up the built-in patterns get), retried on a snapped copy if GEOS trips"""
    try:
        return _geom.clean(_geom.regularize(region, ribs, w))
    except Exception:
        return _geom.clean(_geom.regularize(_geom.clean(region), _geom.clean(ribs), w))


def _groove(pts):
    return LineString([_mm(p) for p in pts]).buffer(G / 2, cap_style=2)


def _groove_to(pts, stop):
    """groove (mm geometry, one half) that ends exactly on the edge of the black `stop` polygon (px), so it
    neither nicks the black part nor leaves a white crumb in front of it"""
    return _groove(pts).difference(_mmpoly(stop).buffer(-0.01))


# ---------------------------------------------------------------- body outline (left half, elevation px)
# top = cowl: near-flat, centre 0.25 mm higher than the fender corners (G80-like slight crown, no crescent)
# side: straight down to the splitter; lower corner ~5.5 mm x 4 mm radius; bottom straight
SIDE_LOW = [(328.4, 566), (329, 585), (330, 605), (331.3, 622), (333.3, 636), (336.5, 648), (341.5, 657),
            (348.5, 663), (358, 666.9), (372, 668.6), (400, 669), (CX, 669)]
OUTLINE = [(CX, 434.5), (600, 434.7), (560, 435.1), (520, 435.5), (470, 436), (430, 436.3), (395, 436.5),
           (372, 436.5), (359, 436.4), (350, 437.6), (343, 441), (338, 446.5), (334.5, 453), (332, 461),
           (330, 472), (329, 486), (328.4, 502), (328.1, 516), (328, 530), (328.1, 548)] + SIDE_LOW

# ---------------------------------------------------------------- headlight: black lens (incl. bezel) + white Y DRL
HEADLIGHT = [(369.5, 475.5), (372.5, 473.2), (426, 493.1), (433, 493.2), (454, 503), (464, 518), (429, 539.5),
             (418, 543.5), (386, 533)]
DRL_W = 0.8                                       # G80 DRL strokes are 0.67-0.86 mm
DRL_MARGIN = 0.65                                 # black kept all round the white Y (min)
Y_J = (406, 519)                                  # junction of the Y
# long bar: runs from the lens's outer-top corner through the junction down to the lens bottom (drawn past both
# ends and trimmed by the lens inset, so it ends in a pointed tip in the corner and a clean cut at the bottom,
# exactly DRL_MARGIN inside the lens); short arm: ~36 deg up to the lens's inner top
DRL_BAR = [(369.2, 472.6), (384.1, 488.7), Y_J, (421.5, 543)]   # tip segment on the lens-corner bisector
DRL_SHORT = [(429, 502), Y_J]
_LENS_IN = _mmpoly(HEADLIGHT).buffer(-DRL_MARGIN, join_style=2)
DRL = unary_union([LineString([_mm(p) for p in DRL_BAR]).buffer(DRL_W / 2, cap_style=2, join_style=2),
                   LineString([_mm(p) for p in DRL_SHORT]).buffer(DRL_W / 2)]).intersection(_LENS_IN)
DRL = DRL.buffer(-0.25).buffer(0.25)              # corner tip ends 0.5 mm wide (rounded) instead of a hair point

# ---------------------------------------------------------------- nose: the slim vent slit (1 mm blunt ends)
NOSE_VENT = [(500, 539.8), (508, 539.5), (590, 546.5), (597, 547.3), (597, 555.0), (508, 548), (500, 547.0)]

# ---------------------------------------------------------------- lower front
# The whole black mouth (flat black = carbon): side intake above the body-colour blade + centre opening between
# the blade tips. Its bottom edge stops 1.1 mm above the splitter, leaving the body-colour lip that joins the
# two blade tips into one continuous 'U' frame.
MOUTH = [(366, 570), (383, 557), (400, 559), (420, 564), (440, 570), (470, 574), (500, 577), (560, 582),
         (620, 586), (CX, 587), (CX, 646.6), (630, 646.6), (560, 643.5), (500, 640.5),
         (493.5, 640.2), (492.4, 636.8),                  # blunted corner (no acute black wedge at the blade tip)
         (512.5, 620.2), (512, 614.9), (486, 618), (470, 624), (378, 600), (371, 583)]
# Only the real openings are recessed (relief pockets, 0.6 mm floor in production). The carbon blade in each side
# intake and the SVJ 'arrow' V between the two openings stay flat black (1.6 mm).
#   upper slot: the dark opening under the hood edge, from the outer intake corner to the centre
SLOT_BOT = [(369, 580), (400, 584.5), (440, 590.5), (500, 597.5), (548, 601), (600, 602.5), (CX, 605.5)]
UPPER_SLOT = [(366, 570), (383, 557), (400, 559), (420, 564), (440, 570), (470, 574), (500, 577), (560, 582),
              (620, 586), (CX, 587)] + SLOT_BOT[::-1]
#   lower centre opening: below the arrow V, down to the lip, between the blade tips
LOWER_OPEN = [(512, 614.9), (548, 610.5), (600, 614), (630, 616.3), (CX, 616.3), (CX, 646.6), (630, 646.6),
              (560, 643.5), (500, 640.5),
              (493.5, 640.2), (492.4, 636.8), (512.5, 620.2)]
# carbon standing up inside the openings: the centre bracket (full height, like the G80 grille bridge), one 1.0 mm
# carbon strake per side along the middle of the slot (0.8 mm gaps) that drops square into the carbon blade (so it
# also breaks the slot into short spans), and one 1.3 mm lower-grille slat (1.2-1.45 mm gaps). Cleaned with the
# pipeline's own regularize so no rib/gap sliver is left where a rib meets an angled wall.
_M = _both(_mmpoly(MOUTH))
_R_UP = _both(_mmpoly(UPPER_SLOT)).intersection(_M)
_R_LO = _both(_mmpoly(LOWER_OPEN)).intersection(_M)
_RIBS = unary_union([
    LineString([_mm((CX, 575)), _mm((CX, 655))]).buffer(1.6 / 2, cap_style=2),     # centre bracket
    _ribs([[(450, 581.5), (470, 584), (500, 587.2), (515, 588.4), (518, 601)]], 1.0),  # strake -> blade
    _ribs([[(520, 627.2), (548, 626.7), (600, 629.8), (CX, 632)]], 1.3),           # lower grille slat (free end
                                                                                    # 0.8 mm clear of the angled wall)
])
RIBS_UP = _reg(_R_UP, _RIBS.intersection(_R_UP))
RIBS_LO = _reg(_R_LO, _RIBS.intersection(_R_LO))
# splitter lip along the bottom, wrapping up the outer side to y 566 (1.5 mm flat top on the wrap). Its outer edge
# is the outline itself (no white sliver along the edge); the inner edge is the body-colour blade's outer edge,
# which sweeps round the corner so the carbon is ~3 mm along the side and the bottom and ~5 mm in the corner.
SPLITTER = SIDE_LOW[::-1] + [(340, 566), (344, 581), (348, 594), (354, 609), (363, 623), (376, 634), (396, 641.5),
                             (430, 646), (470, 648.5), (500, 649.8), (560, 652.5), (CX, 655.5)]

# ---------------------------------------------------------------- engraved body lines
FENDER_LINE = _groove_to([(388, 420), (444.5, 506.9)], HEADLIGHT)          # hood/fender shut line, ends on the lens
HOOD_EDGE = _groove_to([(456, 517), (463, 518), (505, 524), (545, 527), (580, 531), (609, 534), (626, 531),
                        (CX, 530)], HEADLIGHT)                                # hood front edge 'W' out of the lamp tip
CREASE = _groove([(544, 446), (507, 524.2)])       # hood panel crease: starts 1.5 mm below the cowl, ends on the W
# SVJ nose fins: the two sharp body-colour fins hanging from the W line at the ends of each vent slit
FINS = unary_union([_groove([(471, 519.1), (494, 568)]),                      # outer fin
                    _groove([(609, 534), (603, 577)])])                       # inner fin (beside the crest)

# ---------------------------------------------------------------- Lamborghini crest (custom badge, see top)
BC = (CX, 559.4)                     # crest centre (px)
BH, BW = 4.4, 3.8                    # crest height / width incl. the black rim (mm); real crest ~3.0 x 3.2 mm
RIM, BAND = 0.62, 0.62               # black rim, white inner outline (mm); the rest is the black field


def _crest():
    cx, cy = _mm(BC)
    a, h, arc = BW / 2, BH / 2, 0.22
    half = [(0, h + arc), (0.5 * a, h + 0.75 * arc), (a, h),                   # arched top, pointed corners
            (0.975 * a, 0.55 * h), (0.91 * a, 0.15 * h), (0.78 * a, -0.25 * h),    # sides taper continuously
            (0.56 * a, -0.6 * h), (0.28 * a, -0.86 * h), (0, -h)]                 # ... into the point
    pts = half + [(-x, y) for x, y in reversed(half[1:-1])]
    sh = Polygon([(cx + x, cy + y) for x, y in pts])
    return sh, sh.buffer(-RIM, join_style=2), sh.buffer(-(RIM + BAND), join_style=2)


CREST = _crest()

SPEC = dict(
    id='svj_aventador', name='Lamborghini Aventador SVJ',
    ref='kc/cars/svj_aventador/ref/front_elev.png',
    units='px', px_left=PL, px_right=PR, px_bottom=YB, center_x=CX, y_scale=YS,
    outline_half=OUTLINE,
    prims=[
        # headlights (black lens) + Y-shaped DRL (white)
        dict(kind='poly', color='black', pts=HEADLIGHT),
        dict(kind='geom', color='white', geom=DRL),
        # nose vent slits
        dict(kind='poly', color='black', pts=NOSE_VENT),
        # lower front: flat black mouth, then the two recessed openings with their carbon ribs
        dict(kind='poly', color='black', pts=MOUTH),
        dict(kind='poly', color='relief', pts=UPPER_SLOT, relief=dict(type='custom', ribs=RIBS_UP)),
        dict(kind='poly', color='relief', pts=LOWER_OPEN, relief=dict(type='custom', ribs=RIBS_LO)),
        # splitter + outer corners
        dict(kind='poly', color='black', pts=SPLITTER),
        # engraved body lines
        dict(kind='geom', color='groove', geom=FENDER_LINE),
        dict(kind='geom', color='groove', geom=HOOD_EDGE),
        dict(kind='geom', color='groove', geom=CREASE),
        dict(kind='geom', color='groove', geom=FINS),
    ] + ([
        # Lamborghini crest, painted last like the library badge: black crest, white inner outline, black field
        dict(kind='geom', color='black', geom=CREST[0], mirror=False),
        dict(kind='geom', color='white', geom=CREST[1], mirror=False),
        dict(kind='geom', color='black', geom=CREST[2], mirror=False),
    ] if BADGE_ON else []),
    badge=None,          # library 'shield' not used; the crest is the last three prims (BADGE_ON above)
    badge_note='custom Lamborghini crest prims (black / white outline / black field), on/off with BADGE_ON in spec.py',
    tab=dict(y_frac=0.62),   # at the widest point of the fender; its blend stays clear of the splitter wrap
)
