# Porsche 911 GT3 RS (992) front keychain - traced on a straight-on photo (viewer's left half, mirrored).
# Reference: Wikimedia Commons "Porsche 911 GT3 RS (992.1) Washington DC Metro Area, USA (1.1).jpg" (CC BY 4.0)
# Revision 2: sloping fender shoulder that peaks inboard next to the lid (no round "ear" over the lamp), fender
# louvre band forms the silhouette edge itself, DRL blades close into the 992 broken ring, nostrils are open ducts
# (plain deep pocket, no BMW slats), radiator honeycomb at pitch 2.4 with every panel edge on a clean half-cell,
# bumper light raised with a white fang under it, black arch flank raised to just under the keyring neck.
import math
from shapely.geometry import Polygon, LineString, Point, box

PX_L, PX_R = 170, 1776
CX = 973
PX_BOT = 1331
S = 80.5 / (PX_R - PX_L)          # nominal mm per px


# ---------------------------------------------------------------------------------------------- outline
# Top edge: the front lid sits low between the two wings (the 911 twin-hump). Each wing rises from the side in a
# long convex shoulder (the photo's louvre/brick boundary), peaks just outboard of the lid shut line and drops into
# a small V where the shut line meets the top edge.
OUTLINE = [(973, 601), (880, 601), (780, 602), (680, 603), (600, 604), (530, 605), (496, 606), (480, 607),
           (446, 607), (443, 599), (439, 591), (434, 584), (427, 579), (418, 577), (405, 580), (390, 584),
           (372, 590), (354, 597), (334, 607), (313, 618), (292, 631), (272, 644), (256, 656), (242, 669), (230, 685),
           (219, 705), (209, 730), (201, 756), (194, 785), (189, 810), (184, 840), (179, 870), (177, 950),
           (176, 1100), (173, 1238), (168, 1255), (172, 1271), (300, 1290), (450, 1305), (600, 1316),
           (800, 1326), (973, 1331)]

# effective mm per px after the pipeline forces the body to exactly 80.5 mm wide
KS = 80.5 / (2 * max(CX - x for x, _ in OUTLINE))


def X(mm):                         # keychain mm (x, +right) -> photo px
    return CX + mm / KS


def Y(mm):                         # keychain mm (y, up from the bottom) -> photo px
    return PX_BOT - mm / KS


HL_C = (368.5, 764.5)             # left headlight centre (px)
HL_ROT = -21                      # visual tilt of the lamp ellipse (deg, y-up)


def blade(c, bx, by, half, ang_deg, sx, sy):
    """Porsche DRL blade: centre (sx*bx, sy*by) mm from lamp centre c, length 2*half, symmetric about the lamp
    axes. Tangential tilt: the outer end sits closer to the horizontal axis, so the four blades form a broken ring
    around the projector (the 992 four-point light)."""
    a = math.radians(ang_deg)
    inner = (sx * (bx - half * math.cos(a)), sy * (by + half * math.sin(a)))
    outer = (sx * (bx + half * math.cos(a)), sy * (by - half * math.sin(a)))
    return [(c[0] + x / S, c[1] - y / S) for x, y in (inner, outer)]


DRL = [blade(HL_C, 2.35, 2.05, 1.05, 28, sx, sy) for sx in (-1, 1) for sy in (-1, 1)]


def louvre_band(width_px=27, fc=(433, 815), a_lo=208, a_hi=250):
    """RS fender-top louvres: a dark strip that IS the silhouette on the car (brick meets louvres). Outer edge =
    outline, inner edge = outline offset by width_px. Both ends are cut square to the strip along rays from fc, the
    centre of curvature of the shoulder (image degrees, y down), so no acute corners are left at the edge."""
    full = OUTLINE + [(2 * CX - x, y) for x, y in reversed(OUTLINE)]
    P = Polygon(full)
    band = P.buffer(12, join_style=1).difference(P.buffer(-width_px, join_style=1))
    fan = [fc] + [(fc[0] + 700 * math.cos(math.radians(a)), fc[1] + 700 * math.sin(math.radians(a)))
                  for a in range(a_lo, a_hi + 1, 2)]
    band = band.intersection(Polygon(fan))
    if band.geom_type != 'Polygon':
        band = max(band.geoms, key=lambda g: g.area)
    return [(round(x, 1), round(y, 1)) for x, y in band.exterior.coords[:-1]]


NOSTRIL = [(634, 702), (786, 700), (791, 664), (872, 634),
           (880, 700), (895, 744), (897, 778), (888, 786), (672, 786), (655, 772), (632, 712)]

# ---------------------------------------------------------------------------------------------- radiator mesh
# Honeycomb pitch 2.4 / rib 0.8, pointy-top cells (angle 90), so the cells have vertical flat sides next to the
# vertical dividers. Each panel is its own pattern centred on the panel. Every vertical panel edge sits CUT mm past
# the centre of the cells of one row (a clean cut cell, >= 1.15 mm wide) while the other row(s) end in full cells
# behind a 0.85 mm rib: centre panel = top/bottom rows cut, outer panels = middle row cut, so it reads as one
# continuous honeycomb behind the two 0.9 mm dividers (at the photo's divider position). Top/bottom edges leave a
# 0.72 mm rib over the cell tips. No clipped slivers or open slots (CUT > 0.31 keeps regularize() from growing the
# cut cells).
HEX_P, HEX_R, OFF = 2.4, 0.8, 0.5
ROW = 1.5 * HEX_P / math.sqrt(3)               # row spacing of the pointy-top honeycomb (mm)
TIP = (HEX_P - HEX_R) / math.sqrt(3)           # centre-to-tip of a cell hole (mm)
Y_C = 6.25                                     # mesh centre height (mm)
H_HALF = ROW + TIP + 0.72                      # final half height (3 rows + 0.72 mm rib over the tips)
CUT = 0.35                                     # wall sits this far past the centre of the cut cells
XC_EDGE = 2.5 * HEX_P + CUT                    # centre panel edge +/-6.35 mm (top/bottom rows cut)
DIV = 0.9                                      # black divider width (mm)
XO_IN = XC_EDGE + DIV                          # outer panel inner edge 7.25 mm
XO_OUT = XO_IN + 2 * (3 * HEX_P + CUT)         # outer panel 15.1 mm wide (middle row cut at both ends)


def panel_px(x0, x1, rtl=0.0, rbl=0.0):
    """Rectangle x0..x1 (mm, x0 < x1) before the -OFF shrink, optional rounded LEFT corners (top/bottom radius mm)."""
    y0, y1 = Y_C - H_HALF - OFF, Y_C + H_HALF + OFF
    g = box(x0 - OFF, y0, x1 + OFF, y1)
    for r, cy in ((rtl, y1), (rbl, y0)):
        if r > 0:
            sgn = -1 if cy == y1 else 1
            cut = box(x0 - OFF, min(cy, cy + sgn * r), x0 - OFF + r, max(cy, cy + sgn * r))
            keep = Point(x0 - OFF + r, cy + sgn * r).buffer(r, 64)
            g = g.difference(cut.difference(keep))
    return [(round(X(x), 2), round(Y(y), 2)) for x, y in g.exterior.coords[:-1]]


OUTER_L = panel_px(-XO_OUT, -XO_IN, rtl=1.6, rbl=1.6)
OUTER_R = [(2 * CX - x, y) for x, y in OUTER_L]
CENTRE = panel_px(-XC_EDGE, XC_EDGE)
MESH = dict(type='hex', pitch=HEX_P, rib=HEX_R, angle=90)

prims = [
    # --- headlight (whole lens black) + Porsche four-point DRL (four slim, square-ended white blades on a ring)
    dict(kind='ellipse', color='black', c=HL_C, rx=103.5, ry=115.5, rot=HL_ROT),
]
for pts in DRL:
    prims.append(dict(kind='stroke', color='white', width=0.85, cap='flat', pts=pts))

prims += [
    # --- fender-top louvre band = the silhouette edge over the outer shoulder
    dict(kind='poly', color='black', pts=louvre_band()),
    # --- hood nostril vent: open duct (plain deep pocket) + the tall inner fin standing in it (flush black)
    dict(kind='poly', color='black', pts=NOSTRIL),
    dict(kind='poly', color='relief', pts=[(630, 690), (786, 690), (786, 790), (630, 790)],
         relief=dict(type='none')),
    # --- lower bumper: side intakes + centre radiator intake + splitter (one black mass like the real car)
    dict(kind='poly', color='black', pts=[(973, 1117), (800, 1114), (700, 1107), (620, 1099), (548, 1094),
                                         (547, 1072), (540, 1054), (528, 1042), (430, 1031), (342, 1027),
                                         (326, 1035), (310, 1056), (298, 1088), (291, 1140), (286, 1200), (281, 1252),
                                         (240, 1250), (196, 1246), (120, 1244), (120, 1300), (973, 1340)]),
    # bumper LED light blade (white on black) at the top of the housing
    dict(kind='stroke', color='white', width=0.9, pts=[(352, 1049), (428, 1053), (498, 1061)]),
    # white bumper fang under the light housing (separates the light blade from the intake below)
    dict(kind='poly', color='white', pts=[(442, 1085), (500, 1085), (548, 1088), (590, 1097), (560, 1100),
                                         (500, 1100), (442, 1098)]),
    # centre radiator mesh, three panels split by the two black dividers
    dict(kind='poly', color='relief', offset=-OFF, mirror=False, pts=OUTER_L, relief=MESH),
    dict(kind='poly', color='relief', offset=-OFF, mirror=False, pts=OUTER_R, relief=MESH),
    dict(kind='poly', color='relief', offset=-OFF, mirror=False, pts=CENTRE, relief=MESH),
    # side blade (black flank of the front wheel arch), starts just under the keyring neck
    dict(kind='poly', color='black', pts=[(120, 980), (197, 980), (198, 1252), (240, 1256), (240, 1300), (120, 1300)]),
    # --- engraved lines: front-lid shut line (straight, wide trapezoid) + bumper/wing line that becomes the
    #     lid's front edge. The shut line starts above the silhouette so it cuts the top edge in the V.
    dict(kind='stroke', color='groove', width=0.6,
         pts=[(461.4, 591.1), (470, 610), (490, 654), (515, 707), (541, 762), (566, 814), (589, 862), (604, 893),
              (612, 907), (619, 915), (630, 920)], smooth=1),
    dict(kind='stroke', color='groove', width=0.6,
         pts=[(245, 880), (300, 893), (370, 901), (450, 907), (540, 912), (620, 918), (700, 921), (820, 923),
              (973, 924)], smooth=1),
]

SPEC = dict(
    id='gt3rs_992', name='Porsche 911 GT3 RS (992)',
    ref='kc/cars/gt3rs_992/ref/front.jpg',
    units='px', px_left=PX_L, px_right=PX_R, px_bottom=PX_BOT, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    badge=dict(type='shield', c=(973, 862), d=3.8),
    tab=dict(y_frac=0.62),
)
