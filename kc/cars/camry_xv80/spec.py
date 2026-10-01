# Toyota Camry (XV80, 9th gen, 2025+, SE) front keychain.
# Reference: ref/front.jpg = Toyota USA Newsroom press photo 2025_Camry_SE_AWD_SupersonicRed_012 (4000 x 2667,
# straight-on, camera at headlight height, long lens, level; the mirror check about x=2015 is clean, so no rotation).
# See ref/SOURCE.txt. DRL graphic confirmed on the lit XLE press photo (ref/cand/xle_009_full.jpg).
# Traced half = viewer's LEFT (car's right). Coordinates = photo px (1 mm ~ 27.7 px).
#
# Design (G80 language):
#  white  = body paint: hood, fenders, the nose with the badge, the body-colour notch that cuts into each lamp between
#           its upper blade and its lower tail, the band between the "hammerhead" opening and the grille, the fangs
#           between grille and corner vents, the lower bumper band.
#  black  = head lamp + its thin upper blade + the black upper opening that joins both lamps across the nose (one
#           "hammerhead" shape), the wide trapezoid lower grille, the C-shaped corner vents with their blades that
#           reach towards the grille, the lower lip / valance with its corner canards, the Toyota badge.
#  white on black = the light signature: the "<" / C-shaped LED light guide - upper arm along the blade, lower arm
#           down the lamp tail - hugging the white notch (0.66 mm strokes, 0.62 mm black each side).
#  relief = the SE's stretched flat-top hexagon mesh in the grille (4.4 x 2.2 mm cells, 0.7 ribs, 0.7 rim), holes
#           shrinking towards the grille corners like the real mesh turning into solid 3D blocks; horizontal louvres
#           (pitch 1.7, rib 0.8) in the corner vents, the inner C-frame of each vent left solid.
#  grooves (0.58 mm) = hood front shut line (blade tip to blade tip), the two hood creases from the cowl to the
#           blade tips, the hood/fender shut lines from the A-pillar base to the lamp tops.
#  badge  = simplified three-oval Toyota emblem, 6.8 x 3.6 mm (SHOW_BADGE / KC_BADGE=0 to drop it); cells sized so the
#           classic 0.4 mm inlay fills them (slice-tested).
#  tab    = viewer's left at 55 % height, on the white fender between the lamp and the corner vent.
# Full build: python kc/cars/camry_xv80/build_cli73.py kc/cars/camry_xv80/spec.py kc/cars/camry_xv80/out
# (the pipeline's slicecheck CLI call needs this wrapper since Creality Print auto-updated to 7.3).
import os, sys, math
import shapely
from shapely.geometry import Polygon, LineString, Point, box, MultiLineString
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):   # badge-free export, no edit
    SHOW_BADGE = False

CX, YB = 2015, 2127                   # centreline, bottom of the lower lip (px)

# ------------------------------------------------------------------------------------------------ outline
OUTLINE = [(2015, 1146), (1800, 1147), (1600, 1148), (1400, 1150), (1250, 1153), (1150, 1157), (1098, 1163),
           (1060, 1180), (1025, 1206), (995, 1236), (968, 1270), (945, 1307), (926, 1347), (912, 1390),
           (903, 1435), (899, 1480), (898, 1560), (898, 1700), (898, 1850), (899, 1960), (902, 2020),
           (910, 2065), (926, 2096), (952, 2114), (1000, 2123), (1100, 2126), (1400, 2127), (2015, 2127)]
XL = min(x for x, y in OUTLINE)
XR = 2 * CX - XL
S = 80.5 / (XR - XL)                  # mm per px


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


def mmp(p):
    return mm([p])[0]


def sym(g):
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])


# ------------------------------------------------------------------------------------------------ head lamp
# The lamp, its thin upper blade and the black upper opening ("hammerhead" band) that joins both lamps across the nose
# are one black shape. The body-colour notch between the blade and the lamp's lower tail stays white; the C-shaped
# LED light guide ("<": upper arm in the blade, lower arm along the tail) is a white stroke inside the black.
LAMP_TOP = [(985, 1343), (1050, 1356), (1100, 1363), (1150, 1370), (1200, 1377), (1250, 1383), (1300, 1389),
            (1350, 1394), (1400, 1399), (1428, 1404)]                # lamp + blade top edge (outer corner -> tip)
LAMP_OUTER = [(972, 1356), (963, 1380), (958, 1420), (961, 1452), (972, 1478)]
LAMP_BOTTOM = [(990, 1487), (1050, 1497), (1150, 1511), (1225, 1523), (1300, 1545)]
BAND_TOP = [(1300, 1488), (1350, 1493), (1400, 1498), (1500, 1509), (1600, 1516), (1700, 1521), (1800, 1524),
            (1900, 1526), (2015, 1527)]
BAND_BOT = [(2015, 1597), (1900, 1596), (1800, 1594), (1700, 1590), (1600, 1585), (1500, 1575), (1400, 1562),
            (1300, 1545)]
DIAG = [(1133, 1395), (1160, 1412), (1200, 1437), (1240, 1462), (1270, 1477), (1300, 1488)]   # notch lower edge

DRL_W = 0.66              # light guide width (mm)
RIM_TOP = 0.62            # black between the blade top edge and the upper arm (mm)
GAP = 0.62                # black between a light guide and the white notch (mm)
VERTEX = (1122, 1389)     # px, outer point of the "<"
UP_END_X = 1382           # px, inner end of the upper arm
LOW_END = (1318, 1521)    # px, inner end of the lower arm
BLADE_TIP = (1432, 1404)  # px, inner tip of the blade
TAPER_X = 1398            # px, blade keeps its full depth up to here, then tapers to the tip


def _below(line, d):
    """offset of a left->right polyline by d mm downwards (keychain frame, y up)"""
    a = line.offset_curve(d)
    b = line.offset_curve(-d)
    return a if a.centroid.y < b.centroid.y else b


def lamp_parts():
    top = LineString(mm(LAMP_TOP))
    up_c = _below(top, RIM_TOP + DRL_W / 2)                  # upper-arm centreline below the top edge
    vx, vy = mmp(VERTEX)
    xe = (UP_END_X - CX) * S
    up_c = up_c.intersection(box(vx, -50, xe, 60))
    up_pts = [(vx, vy)] + [p for p in up_c.coords if p[0] > vx + 0.3]
    # lower arm: follows the notch lower edge DIAG, GAP + DRL_W/2 below it, then eases into the tail end
    lo_c = _below(LineString(mm(DIAG)), GAP + DRL_W / 2)
    le = mmp(LOW_END)
    lo_pts = [p for p in lo_c.coords if vx + 0.6 < p[0] < le[0] - 0.6] + [le]
    drl_line = LineString(list(reversed(up_pts)) + lo_pts)
    drl = drl_line.buffer(DRL_W / 2, 32, join_style=1)
    # black lamp (+ blade + band): top edge, blade tip, down to the band, band to the centre and back, lamp bottom
    outline = LAMP_TOP + [BLADE_TIP, (1440, 1420), (1420, 1480)] + BAND_TOP[2:] + BAND_BOT + LAMP_BOTTOM[::-1] + LAMP_OUTER[::-1]
    black = Polygon(mm(outline)).buffer(0)
    # white notch = body colour between the blade and the lamp tail / band top. Its top is the blade's lower edge
    # (the upper arm's centreline + DRL_W/2 + GAP), which runs on to TAPER_X and then rises to the blade tip.
    bb = _below(top, RIM_TOP + DRL_W + GAP)
    xt = (TAPER_X - CX) * S
    bb_pts = [p for p in bb.coords if p[0] < xt]
    bb_y = float(bb.intersection(box(xt - 0.01, -50, xt + 0.01, 60)).centroid.y)
    tip = mmp(BLADE_TIP)
    xf = (1480 - CX) * S
    U = bb_pts + [(xt, bb_y), tip, (xf, tip[1])]
    below_u = Polygon(U + [(xf, -10), (U[0][0], -10)]).buffer(0)
    L = mm(DIAG + BAND_TOP[1:4])
    above_l = Polygon(L + [(L[-1][0], 60), (L[0][0], 60)]).buffer(0)
    sector = below_u.intersection(above_l).intersection(box(L[0][0], -10, xf, 60))
    notch = sector.difference(drl.buffer(GAP, 32))
    notch = max(geom.polys(notch), key=lambda q: q.area) if not notch.is_empty else notch
    r = 0.32
    notch = notch.buffer(-r, 32).buffer(r, 32)
    return black, drl, notch


LAMP_BLACK, DRL, NOTCH = lamp_parts()

# ------------------------------------------------------------------------------------------------ grille etc (px)
GRILLE = [(2015, 1695), (1700, 1696), (1450, 1697), (1375, 1699), (1340, 1706), (1300, 1720), (1265, 1742),
          (1232, 1775), (1207, 1815), (1188, 1860), (1174, 1910), (1164, 1955), (1157, 1995), (1154, 2008),
          (1200, 2015), (1300, 2025), (1417, 2035), (1600, 2042), (1800, 2045), (2015, 2046)]
VENT = [(1206, 1662), (1130, 1671), (1067, 1683), (1005, 1699), (978, 1715), (963, 1740), (955, 1790),
        (948, 1880), (941, 1975), (936, 2030), (1030, 2052), (1025, 1990), (1027, 1940), (1030, 1880),
        (1036, 1817), (1044, 1774), (1058, 1738), (1080, 1716), (1117, 1698), (1160, 1686), (1200, 1678), (1212, 1670)]
LIP = [(2015, 2080), (1700, 2078), (1500, 2077), (1300, 2082), (1238, 2087), (1130, 2063), (1025, 2035),
       (942, 2012), (918, 1994), (903, 1972), (880, 1945), (880, 2150), (2015, 2150)]
HOOD_LINE = [(1410, 1404), (1480, 1396), (1560, 1391), (1700, 1389), (1850, 1388), (2030, 1388)]
HOOD_CREASE = [(1318, 1192), (1336, 1228), (1356, 1268), (1378, 1312), (1398, 1352), (1418, 1394), (1426, 1403)]
FENDER_LINE = [(1076, 1176), (1063, 1218), (1053, 1262), (1047, 1306), (1043, 1348)]
GROOVE_W = 0.58


# ------------------------------------------------------------------------------------------------ grille mesh
# Stretched flat-top hexagons like the real SE grille (cells ~2.3:1 wide), scaled up ~1.5x for a 0.4 mm nozzle.
# Towards the grille's outer corners the real mesh turns into solid faceted 3D blocks: here the holes shrink
# (GRAD_*) and finally close, so the sides read as a denser texture like the photo.
HEX_PX, HEX_PY, HEX_F, HEX_RIB = 4.4, 2.2, 3.0, 0.7    # column pitch, row pitch, flat bar length, rib width (mm)
HEX_Y0 = 0.35                                           # row phase below the grille top (mm)
RIM = 0.7                                               # rib along the recess wall (mm)
GRAD_D0, GRAD_D1, GRAD_S0 = 1.5, 9.0, 0.45              # dist from the side edge (mm): hole scale GRAD_S0 -> 1
HOLE_MIN_W, HOLE_MIN_A = 0.62, 0.45                     # smaller holes are closed (mm, mm2)


def hex_holes(region, side_edge):
    minx, miny, maxx, maxy = region.bounds
    inner = region.buffer(-RIM, join_style=1)
    D = HEX_PX - HEX_F
    holes = []
    ncol = int(max(abs(minx), abs(maxx)) / HEX_PX) + 3
    nrow = int((maxy - miny) / HEX_PY) + 4
    for c in range(-ncol, ncol + 1):
        xc = c * HEX_PX
        off = HEX_PY / 2 if c % 2 else 0.0
        for r in range(-2, nrow):
            y = maxy - HEX_Y0 - r * HEX_PY - off               # top bar of this cell
            cell = Polygon([(xc - HEX_F / 2, y), (xc + HEX_F / 2, y), (xc + HEX_F / 2 + D, y - HEX_PY / 2),
                            (xc + HEX_F / 2, y - HEX_PY), (xc - HEX_F / 2, y - HEX_PY),
                            (xc - HEX_F / 2 - D, y - HEX_PY / 2)])
            h = cell.buffer(-HEX_RIB / 2, join_style=2)
            cc = cell.centroid
            if not inner.buffer(1.0).contains(cc):
                continue
            d = side_edge.distance(cc)
            t = min(1.0, max(0.0, (d - GRAD_D0) / (GRAD_D1 - GRAD_D0)))
            k = GRAD_S0 + (1 - GRAD_S0) * t
            h = affinity.scale(h, k, k, origin=cc)
            h = h.intersection(inner)
            for q in geom.polys(h):
                qo = q.buffer(-HOLE_MIN_W / 2 + 0.01, join_style=1).buffer(HOLE_MIN_W / 2 - 0.01, join_style=1)
                for q2 in geom.polys(qo):
                    if q2.area >= HOLE_MIN_A:
                        holes.append(q2)
    return unary_union(holes)


_ghalf = Polygon(mm(GRILLE)).buffer(0)
_grille = sym(_ghalf)
_side = LineString(mm(GRILLE[3:14]))                            # left outer edge of the grille (px pts 3..13)
_side = unary_union([_side, affinity.scale(_side, -1, 1, origin=(0, 0))])
_holes = hex_holes(_grille, _side)
_hl = _holes.intersection(box(-60, -10, 0, 60))                 # left-half holes, mirrored -> exactly symmetric
_holes = unary_union([_hl, affinity.scale(_hl, -1, 1, origin=(0, 0)), _holes.intersection(box(-HEX_PX / 2, -10, HEX_PX / 2, 60))])
_ribs = geom.regularize(_grille, _grille.difference(_holes), 0.64)

prims = [
    dict(kind='geom', color='black', geom=LAMP_BLACK),
    dict(kind='geom', color='white', geom=NOTCH),
    dict(kind='geom', color='white', geom=DRL),
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, pts=HOOD_LINE),
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, pts=HOOD_CREASE),
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, pts=FENDER_LINE),
    dict(kind='geom', color='black', geom=_grille, mirror=False, relief=dict(type='custom', ribs=_ribs)),
    dict(kind='poly', color='black', pts=VENT, smooth=1),
    dict(kind='poly', color='black', pts=LIP),
    # corner-vent louvres (relief slats) in the vertical part of the vent, below its blade
    dict(kind='poly', color='relief', pts=[(925, 1738), (1012, 1738), (1006, 2004), (925, 2004)],
         relief=dict(type='hbars', pitch=1.7, rib=0.8, offset=0.0)),
]

# ------------------------------------------------------------------------------------------------ Toyota badge
BADGE_C = (2015, 1461)
BADGE_A, BADGE_B, BADGE_W = 3.4, 1.8, 0.5
BADGE_GTOP, BADGE_GBOT = 0.5, 0.58
BADGE_N = 2.3                                       # outer ring: slight superellipse (room at the shoulders)
BADGE_AH, BADGE_BH, BADGE_AV = 2.5, 0.76, 0.7
BADGE_ROUND = 0.2


def _ell(a, b, y=0.0):
    return affinity.translate(affinity.scale(Point(0, 0).buffer(1, 128), a, b), 0, y)


def toyota_badge():
    w = BADGE_W
    top = BADGE_B - BADGE_GTOP - w / 2
    bot = -(BADGE_B - BADGE_GBOT - w / 2)
    bv, yv = (top - bot) / 2, (top + bot) / 2
    yh = top - BADGE_BH
    n = BADGE_N
    base = Polygon([(BADGE_A * math.copysign(abs(math.cos(t)) ** (2 / n), math.cos(t)),
                     BADGE_B * math.copysign(abs(math.sin(t)) ** (2 / n), math.sin(t)))
                    for t in [2 * math.pi * i / 256 for i in range(256)]])
    vert = _ell(BADGE_AV, bv, yv).exterior.buffer(w / 2, 32)
    horz = _ell(BADGE_AH, BADGE_BH, yh).exterior.buffer(w / 2, 32).difference(_ell(BADGE_AV - w / 2, bv - w / 2, yv))
    white = unary_union([vert, horz]).intersection(base)
    black = unary_union([q.buffer(-BADGE_ROUND, 32).buffer(BADGE_ROUND, 32) if q.area < 1.5 else q
                         for q in geom.polys(base.difference(white))])
    white = base.difference(black)
    x, y = mmp(BADGE_C)
    return affinity.translate(base, 0, y), affinity.translate(white, 0, y)


if SHOW_BADGE:
    _bb, _bw = toyota_badge()
    # painted first: nothing overlaps the badge, and this keeps its black cells after the ring in the black map's
    # polygon order, which the flat preview renderer (holes painted per polygon) needs to show them
    prims = [dict(kind='geom', color='black', geom=_bb, mirror=False),
             dict(kind='geom', color='white', geom=_bw, mirror=False)] + prims

SPEC = dict(
    id='camry_xv80', name='Toyota Camry (XV80) SE',
    ref='kc/cars/camry_xv80/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.55),
    badge_on=SHOW_BADGE,
)
