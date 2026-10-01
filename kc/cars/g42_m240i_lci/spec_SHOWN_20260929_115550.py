# BMW M240i xDrive Coupe (G42, 2024 model update / LCI = latest front) keychain.
# Reference: BMW Group PressClub photo P90554907 "The new BMW M240i xDrive Coupe (06/2024)", Fire Red, straight-on
# front, 1200x1500 press download (https://www.press.bmwgroup.com/global/photo/detail/P90554907 ; (c) BMW AG, PressClub
# press material for editorial use). ref/front.jpg = unmodified copy. The photo is level and mirror-symmetric about
# x = 601 (checked with a mirror blend), so it is traced directly. Traced half = viewer's right (car's left, well lit).
# Cross-checked on the 2024 UK press set (P90601549, blue M Sport, DRL lit) for the DRL hook, the tow-hook side and
# the kidney grille (both photos: the two kidney frames are joined in the middle by a black camera housing, body
# colour shows only as a small notch under the badge and one above the lower bumper; wavy in-out-in fins).
#
# Badge switch: SHOW_BADGE below (or environment KC_BADGE=0 for a badge-free export without editing this file).
# With the roundel on, the hood front shut line stops ~1.1 mm short of it on both sides (the badge sits alone in
# white like on the G80); with the roundel off the line runs straight across the centre.
import sys, os
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import geom

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '1') == '0':
    SHOW_BADGE = False

CX = 601
PX_L, PX_R, PX_B = 2 * CX - 1080, 1080, 1088
S = 80.5 / (PX_R - PX_L)                           # mm per photo pixel
FRAME = geom.Frame(dict(units='px', px_left=PX_L, px_right=PX_R, px_bottom=PX_B, center_x=CX))


def ymm(y_px):
    return (PX_B - y_px) * S


def mm(p):
    return FRAME.pt(p)


def mirrored(g):
    return unary_union([g, affinity.scale(g, xfact=-1, yfact=1, origin=(0, 0))])


def fit_ribs(region, raw, w=0.64):
    """Regularised custom ribs (no rib/gap slivers < w inside the recess) that also run on past the recess wall, so
    the pipeline's own clip to the (grid-snapped) recess gives ribs that meet the wall exactly (no hairline gap)."""
    return geom.regularize(region, raw.intersection(region), w).union(raw.difference(region))


# ---------------------------------------------------------------------------------------------- traced shapes (px)
# right kidney. Inner side follows the body-colour notch under the badge (y 753-777) and the notch above the bumper
# (y 841-871); between them the kidneys are joined by the black camera housing (KID_JOIN).
KIDNEY = [(624, 753), (700, 751), (800, 752), (845, 756), (862, 766), (871, 785), (874, 810), (870, 838), (858, 856),
          (835, 866), (760, 871), (660, 871), (638, 869), (622, 864), (615, 855), (612, 843), (612, 810), (612, 775),
          (615, 762)]
KID_JOIN = [(585, 777), (617, 777), (617, 841), (585, 841)]          # symmetric about CX (mirror=False)

# ---------------------------------------------------------------------------------------------- kidney fins (mm)
# 8 fins per kidney on the photo's fin lines (x 641/667/693/719/745/771/797/823 px): pitch 2.2 / rib 1.1 / gap 1.1.
# Each fin is the 2024 wavy in-out-in blade: straight top (to y 783 px), a steep 0.6 mm step AWAY from the centreline
# (783-790), a straight middle section (790-808), a longer diagonal back (808-825) and a straight bottom. The outermost
# fin ends ~2 mm inside the outer wall like the photo (dark corner there), so nothing jams into the curved corner.
FIN_X0, FIN_P, FIN_R, FIN_OUT, FIN_N = 3.4, 2.2, 1.1, 0.6, 8
_ya, _yb, _yc, _yd = ymm(783), ymm(790), ymm(808), ymm(825)


def _fin(x):
    r, o = FIN_R / 2, FIN_OUT
    top = box(x - r, _ya, x + r, 45)
    d1 = Polygon([(x - r, _ya), (x + r, _ya), (x + o + r, _yb), (x + o - r, _yb)])
    mid = box(x + o - r, _yc, x + o + r, _yb)
    d2 = Polygon([(x + o - r, _yc), (x + o + r, _yc), (x + r, _yd), (x - r, _yd)])
    bot = box(x - r, -5, x + r, _yd)
    return unary_union([top, d1, mid, d2, bot])


_kreg = mirrored(geom.prim_geom(dict(kind='poly', pts=KIDNEY, smooth=1, offset=-0.7), FRAME))
_fins = mirrored(unary_union([_fin(FIN_X0 + i * FIN_P) for i in range(FIN_N)]))
KIDNEY_RIBS = fit_ribs(_kreg, _fins)

# ---------------------------------------------------------------------------------------------- centre lower grille
# M Sport lower grille: flush gloss band on top (radar panel behind the dropped plate), recessed grille below with
# 2 slats (3 even ~1.0 mm slots) in the two side sections and the two diagonal struts that frame the downward-
# narrowing centre trapezoid (photo: (531,968)->(561,1039) and mirror). The centre panel between the struts has no
# slats in the photo (dark radar/sensor box), so it stays a plain recess.
CI_RELIEF = [(560, 968), (852, 968), (852, 976), (840, 1000), (820, 1025), (808, 1039), (560, 1039)]   # 976: avoids a 0.004 mm2
# float hairline where the upper slat meets the outer wall after the pipeline's re-regularise (invisible 0.08 mm move)
_cireg = mirrored(geom.prim_geom(dict(kind='poly', pts=CI_RELIEF, offset=-0.5), FRAME))
_cy = (_cireg.bounds[1] + _cireg.bounds[3]) / 2
_slats = unary_union([box(-50, _cy + 1.0 + i * 2.0 - 0.5, 50, _cy + 1.0 + i * 2.0 + 0.5) for i in (-2, -1, 0, 1)])
STRUT_W = 0.8
_s0, _s1 = mm((531, 968)), mm((561, 1039))
_dx, _dy = _s1[0] - _s0[0], _s1[1] - _s0[1]
_strut = LineString([(_s0[0] - _dx, _s0[1] - _dy), (_s1[0] + _dx, _s1[1] + _dy)]).buffer(STRUT_W / 2, cap_style=2)
_centre = Polygon([(_s0[0] - _dx, _s0[1] - _dy), (_s1[0] + _dx, _s1[1] + _dy),
                   (-(_s1[0] + _dx), _s1[1] + _dy), (-(_s0[0] - _dx), _s0[1] - _dy)])   # between the strut lines
CI_RIBS = fit_ribs(_cireg, mirrored(_strut).union(_slats.difference(_centre)))

# ---------------------------------------------------------------------------------------------- outer intakes
# tall triangle next to the diagonal bumper blade; top-outer corner kept ~1 mm lower for a wider white neck under the
# keyring tab, bottom in line with the centre-intake bottom. M Sport insert: 0.6 mm flush gloss frame, recessed
# inside with the one slanted fin the photo shows ((950,972)->(1017,957)), attached to the inner diagonal wall.
OUTER_INTAKE = [(1043, 847), (1053, 856), (1062, 868), (1064, 1000), (900, 1040), (882, 1039), (878, 1031)]
_oireg = geom.prim_geom(dict(kind='poly', pts=OUTER_INTAKE, offset=-0.6), FRAME)
_f0, _f1 = mm((925, 978)), mm((1017, 957))
OI_RIBS = mirrored(fit_ribs(_oireg, LineString([(2 * _f0[0] - _f1[0], 2 * _f0[1] - _f1[1]), _f1]).buffer(0.4)))

# hood front shut line: stops short of the roundel when it is shown
HOOD_FRONT = [(638, 720), (750, 720), (880, 724), (925, 729), (948, 745)]
if not SHOW_BADGE:
    HOOD_FRONT = [(560, 719)] + HOOD_FRONT

prims = [
    # hood front shut line (engraved), drawn first so the headlights cover its ends; the last segment turns down so
    # it meets the rising headlight top edge at ~55 deg (no thin white wedge)
    dict(kind='stroke', color='groove', width=0.55, pts=HOOD_FRONT),
    # hood side shut lines: from under the headlight's outer-top corner up along the fender, turning up steeply to
    # leave through the top edge (no tangent run along the silhouette)
    dict(kind='stroke', color='groove', width=0.55, smooth=2,
         pts=[(1013, 719), (985, 695), (956, 676), (931, 665), (905, 659), (893, 655), (884, 632), (881, 624)]),
    # bumper blade creases (engraved): top edge + inner edge of the lit diagonal facet between the intakes. Both
    # round ends stop >= 0.75 mm (edge to edge) short of the intakes, so no thin white web is left next to the slot
    dict(kind='stroke', color='groove', width=0.55, pts=[(864, 955), (930, 860), (1018, 850)]),
    # headlight unit (black); outer-top edge kept ~0.85 mm inside the silhouette (solid white wall on the corner)
    dict(kind='poly', color='black', pts=[(885, 757), (905, 750), (940, 738), (975, 726), (1000, 717), (1012, 710),
                                          (1023, 722), (1037, 735), (1048, 752), (1054, 770), (1055, 790),
                                          (1051, 802), (1041, 808), (985, 808), (975, 806), (946, 786),
                                          (910, 786), (899, 779), (889, 767)]),
    # DRL: upper inner bar, step down, lower bar, then the tall outer upright (hockey stick / L) running up the outer
    # side into the lens corner like the lit 2024 photo; >= 0.6 mm black kept all round
    dict(kind='stroke', color='white', width=0.72, smooth=2,
         pts=[(903, 766), (948, 766), (980, 790), (1031, 791), (1038, 787), (1041, 772), (1037, 757), (1027, 744)]),
    # kidneys: gloss-black frame (flush) joined by the black camera housing, recessed pockets with wavy fins
    dict(kind='poly', color='black', smooth=1, pts=KIDNEY),
    dict(kind='poly', color='black', pts=KID_JOIN, mirror=False),
    dict(kind='poly', color='relief', smooth=1, offset=-0.7, pts=KIDNEY, relief=dict(type='custom', ribs=KIDNEY_RIBS)),
    # centre lower intake (symmetric trapezoid): flush gloss band on top, recessed grille below (slats + struts);
    # bottom at the real frame edge (y 1039) so ~1.5 mm of body-colour lip remains
    dict(kind='poly', color='black', pts=[(560, 933), (843, 933), (851, 941), (852, 975), (840, 1000),
                                          (820, 1025), (808, 1039), (560, 1039)]),
    dict(kind='poly', color='relief', pts=CI_RELIEF, offset=-0.5, relief=dict(type='custom', ribs=CI_RIBS)),
    # outer intakes with the M Sport insert fin
    dict(kind='poly', color='black', pts=OUTER_INTAKE),
    dict(kind='poly', color='relief', pts=OUTER_INTAKE, offset=-0.6, relief=dict(type='custom', ribs=OI_RIBS)),
    # splitter lip; its outer end is cut square to the silhouette (blunt ~1 mm end like the G80, no feathered tip)
    dict(kind='poly', color='black', pts=[(560, 1057), (900, 1057), (1000, 1058), (1030, 1058), (1040, 1075),
                                          (1040, 1120), (560, 1120)]),
    # tow-hook cover: BMW, exactly one, viewer's left (user rule; the photo shows it at (353,907))
    dict(kind='ring', color='black', c=(353, 907), r_mm=1.4, width=0.55, mirror=False),
]

SPEC = dict(
    id='g42_m240i_lci', name='BMW M240i (G42 LCI)',
    ref='kc/cars/g42_m240i_lci/ref/front.jpg',
    units='px', px_left=PX_L, px_right=PX_R, px_bottom=PX_B, center_x=CX,
    outline_half=[(601, 633), (700, 634), (800, 636), (870, 640), (903, 645), (935, 652), (962, 663), (992, 683),
                  (1022, 705), (1045, 728), (1060, 748), (1070, 770), (1077, 800), (1080, 840), (1080, 900),
                  (1079, 960), (1077, 1010), (1072, 1035), (1063, 1050), (1048, 1060), (1036, 1068), (1018, 1077),
                  (980, 1083), (900, 1086), (760, 1088), (601, 1088)],
    prims=prims,
    badge=dict(type='roundel', c=(601, 733), d=3.9),
    badge_on=SHOW_BADGE,
    tab=dict(y_frac=0.57),
)
