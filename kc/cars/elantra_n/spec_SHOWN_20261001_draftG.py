# Hyundai Elantra N (CN7 N, 2022-2023, pre-facelift) front keychain.  NO LOGOS (user rule): badge=None, the
# Hyundai "H" on the bonnet nose and the "N" badge in the grille are left out (plain body / plain grille mesh).
# Reference: ref/front.jpg (Hyundai USA press photo, see ref/SOURCE.txt). 3000 x 2001 px, camera dead centre at
# headlight height. Traced half = viewer's LEFT.
# Revision 1: separate pointed headlight eye (white underline), white grille flank, larger centred jewel diamonds,
# triangular intake mesh, white bumper corner strakes, separate black lip band, crowned / tapered outline.
import math
import os

from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity

CX = 1500


def M(pts):
    """mirror px points to the other half"""
    return [(2 * CX - x, y) for x, y in pts]


# body outline: crowned cowl -> crisp fender shoulder (behind the mirror) -> fender side -> tapered splitter
OUTLINE = [(CX, 930), (1300, 933), (1100, 939), (980, 943), (915, 948), (895, 955), (872, 970), (848, 1005),
           (832, 1040), (816, 1080), (808, 1120), (803, 1180), (802, 1300), (802, 1420), (804, 1470),
           (810, 1505), (830, 1524), (900, 1527), (1000, 1528), (1200, 1529), (CX, 1529)]

# black fascia (headlight lens + dark bumper panel + grille + intakes); outer edge pulled in to leave a white
# bumper-corner strake beside the intakes like the real car
FASCIA = [(874, 1054), (884, 1054), (895, 1080), (912, 1100), (960, 1116), (1010, 1131), (1065, 1145),
          (1150, 1160), (1300, 1168), (CX, 1170),
          (CX, 1406), (1300, 1406), (1140, 1406), (1075, 1411), (1020, 1438), (965, 1460), (900, 1466),
          (850, 1468), (850, 1300), (846, 1200), (842, 1140), (843, 1100), (856, 1070)]

# DRL: short vertical hook at the lamp's outer end + the long slim sweep converging on the grille corner
DRL = [(864, 1102), (867, 1124), (958, 1141), (1060, 1163)]

# white underline of the pointed headlight eye (lower lens edge) and the white grille flank running from the
# lamp's inner tip down to the bumper blade -> lamp, grille and intake read as separate pieces
LAMP_LOW = [(851, 1190), (880, 1206), (940, 1214), (1000, 1206), (1040, 1194)]
FLANK = [(1040, 1194), (1070, 1236), (1110, 1310), (1165, 1404)]

# parametric-jewel grille relief region (right of the flank), mid-height ~1290 so a diamond centres there
GRILLE = [(1060, 1174), (1300, 1174), (CX + 5, 1174), (CX + 5, 1406), (1300, 1406), (1172, 1406), (1135, 1330),
          (1095, 1255)]

# side intake pocket (leans inward) with a triangular mesh
INTAKE = [(874, 1282), (1010, 1295), (1080, 1378), (1040, 1402), (960, 1442), (874, 1450)]

# lower radiator intake under the white blade (ends above a thin white band)
LOWER = [(CX, 1424), (1300, 1424), (1140, 1426), (1080, 1444), (1040, 1462), (1020, 1480), (CX, 1480)]
RAD = [(1230, 1420), (CX + 5, 1420), (CX + 5, 1484), (1230, 1484)]

# red lip + splitter (drawn black, per the brief) as a full-width band with a small kick at the corners
LIP = [(CX, 1494), (1200, 1494), (1000, 1494), (870, 1494), (835, 1492), (812, 1488), (790, 1488), (790, 1600),
       (CX, 1600)]

HOOD_LINE = [(CX, 1086), (1330, 1087), (1100, 1090), (1000, 1093), (915, 1098)]
CREASE = [(1150, 958), (1240, 1010), (1290, 1055), (1325, 1084)]
FENDER = [(914, 960), (900, 992), (888, 1028), (879, 1058)]

# ---------------------------------------------------------------- explicit lattice cells (mm, keychain frame)
# The jewel diamonds and the intake triangles are built as whole cells and passed as 'custom' relief ribs
# (ribs = everything that is not a cell). Whole/clean cells avoid the 22-deg rib tips a clipped bar pattern
# leaves at the grille edge (those were the sub-0.6 mm rib/gap slivers). The frame maps px -> mm exactly
# (outline width is 80.5 mm, bottom at px_bottom), so these mm coordinates line up with the painted regions.
S = 80.5 / (2 * (CX - 802))


def mm(pts):
    return [((x - CX) * S, (1529 - y) * S) for x, y in pts]


def _cells(cells, region_px, margin, rib, keep=0.4):
    half = Polygon(mm(region_px)).buffer(0)
    inner = unary_union([half, affinity.scale(half, -1, 1, origin=(0, 0))]).buffer(-margin, join_style=2)
    out = []
    for c in cells:
        shrunk = c.buffer(-rib / 2, join_style=2)
        g = shrunk.intersection(inner)
        if g.is_empty or g.area < keep * shrunk.area:
            continue
        g = g.buffer(-0.33, join_style=1).buffer(0.33, join_style=1)      # round off any acute clipped tip
        if not g.is_empty:
            out.append(g)
    half = unary_union(out)
    return unary_union([half, affinity.scale(half, -1, 1, origin=(0, 0))])


def jewel_ribs(region_px, H=5.4, ang=24.0, rib=0.9, margin=0.8):
    W = H / math.tan(math.radians(ang))
    ys = [y for _, y in mm(region_px)]
    cy = (min(ys) + max(ys)) / 2
    cells = []
    for k in range(-3, 4):
        for j in range(-6, 2):
            x0, y0 = j * W + (W / 2 if k % 2 else 0), cy + k * H / 2
            cells.append(Polygon([(x0 - W / 2, y0), (x0, y0 + H / 2), (x0 + W / 2, y0), (x0, y0 - H / 2)]))
    return box(-45, -5, 45, 45).difference(_cells(cells, region_px, margin, rib))


def tri_ribs(region_px, p=3.1, rib=0.8, margin=0.8):
    L = 2 * p / math.sqrt(3)
    xs, ys = zip(*mm(region_px))
    x0, y0 = min(xs), (min(ys) + max(ys)) / 2 - p / 2
    cells = []
    for r in range(-5, 6):
        yb = y0 + r * p
        sh = (r % 2) * L / 2
        for i in range(-2, 12):
            xa = x0 + sh + i * L
            cells.append(Polygon([(xa, yb), (xa + L, yb), (xa + L / 2, yb + p)]))           # up triangle
            cells.append(Polygon([(xa + L / 2, yb + p), (xa + L * 1.5, yb + p), (xa + L, yb)]))  # down triangle
    return box(-45, -5, 45, 45).difference(_cells(cells, region_px, margin, rib, keep=0.55))


SPEC = dict(
    id='elantra_n', name='Hyundai Elantra N (2022-2023)',
    ref=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ref', 'front.jpg'),
    units='px', px_left=802, px_right=2 * CX - 802, px_bottom=1529, center_x=CX,
    outline_half=OUTLINE, outline_smooth=1,
    prims=[
        dict(kind='poly', color='black', pts=FASCIA),
        dict(kind='stroke', color='white', width=0.95, pts=DRL, cap='round'),
        dict(kind='stroke', color='white', width=0.9, pts=LAMP_LOW, smooth=1, cap='round'),
        dict(kind='stroke', color='white', width=0.85, pts=FLANK, smooth=1, cap='round'),
        # jewel grille: two crossing rib sets phased so a full diamond sits on the centreline at mid-height
        dict(kind='poly', color='relief', pts=GRILLE, relief=dict(type='custom', ribs=jewel_ribs(GRILLE))),
        # side intake: triangular mesh = three rib sets 60 deg apart through common nodes
        dict(kind='poly', color='relief', pts=INTAKE, relief=dict(type='custom', ribs=tri_ribs(INTAKE))),
        dict(kind='poly', color='black', pts=LOWER),
        dict(kind='poly', color='relief', pts=RAD, relief=dict(type='hbars', pitch=1.6, rib=0.8, offset=0.8, margin=0.0)),
        dict(kind='poly', color='black', pts=LIP),
        dict(kind='stroke', color='groove', width=0.65, pts=HOOD_LINE, cap='round'),
        dict(kind='stroke', color='groove', width=0.65, pts=CREASE, smooth=1, cap='round'),
        dict(kind='stroke', color='groove', width=0.65, pts=FENDER, smooth=1, cap='round'),
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
