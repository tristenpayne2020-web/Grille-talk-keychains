# Honda Civic Type R (FL5, 2023+) front keychain.  NO LOGOS (user rule): badge=None, the H-badge spot is plain honeycomb.
# Reference: ref/front.jpg (see ref/SOURCE.txt). Traced half = viewer's LEFT. Photo pixels of the 2560 x 1920 frame.
# The photo is taken from above (camera ~roof height), which makes the hood look much deeper than it is. Every point
# above y = HOOD_Y is pulled down towards HOOD_Y by HOOD_K (hood depth compressed), so the keychain gets the same
# proportions as the rest of the line; the bumper/lamp/grille zone below HOOD_Y is traced 1:1.
import os

CX = 1288
HOOD_Y, HOOD_K = 868, 0.3


def Y(y):
    return y if y >= HOOD_Y else HOOD_Y - (HOOD_Y - y) * HOOD_K


def P(pts):
    return [(x, Y(y)) for x, y in pts]


def M(pts):
    """mirror px points to the other half (for non-mirrored asymmetric relief)"""
    return [(2 * CX - x, y) for x, y in pts]


# top of the outline drawn directly in the compressed frame (cowl line + fender shoulders a touch higher than the hood)
# bottom = the nearly flat FL5 splitter with squarish corners
OUTLINE = [(CX, 778), (1000, 777), (800, 773), (660, 768), (560, 766), (480, 772), (420, 788), (375, 812),
           (352, 840), (340, 875), (330, 920), (325, 960), (322, 1050), (322, 1150), (328, 1210), (340, 1250),
           (343, 1350), (345, 1440), (350, 1500), (358, 1565), (375, 1608), (425, 1640), (520, 1676),
           (650, 1704), (800, 1722), (1000, 1735), (CX, 1742)]
# side air-curtain slit (kept below the keyring tab so the fender stays white there)
SLIT = [(300, 1305), (368, 1302), (385, 1318), (393, 1345), (395, 1432), (300, 1442)]

# black band: headlight unit + gloss trim + upper honeycomb grille (one piece on the car)
BAND = [(372, 870), (430, 886), (520, 928), (620, 974), (720, 1020), (800, 1060), (840, 1092), (870, 1126),
        (910, 1145), (1000, 1152), (CX, 1153), (CX, 1347), (1100, 1342), (1000, 1334), (930, 1318), (870, 1290),
        (830, 1265), (760, 1236), (660, 1196), (560, 1152), (470, 1112), (415, 1080), (388, 1056), (372, 960)]

# DRL light bar: an "L" hugging the lamp's outer end and running along the whole top edge to the inner tip
DRL = [(410, 1030), (399, 960), (401, 908), (440, 920), (520, 958), (620, 1004), (720, 1050), (790, 1084), (824, 1112)]

# honeycomb inset >= 0.8 mm inside the black band, plain gloss bar (~1 mm) left on top
UPPER_HEX = [(875, 1178), (CX + 5, 1178), (CX + 5, 1325), (1000, 1313), (935, 1296), (890, 1272)]

# lower black: centre intake + corner intake + splitter lip.  The white bumper corner ("fang" + canard) comes down
# to ~1615 and only a ~1.5 mm black lip runs under it.
LOWER = [(CX, 1412), (800, 1414), (730, 1420), (690, 1434), (655, 1452), (620, 1480), (590, 1525), (565, 1578),
         (556, 1612), (480, 1614), (420, 1600), (378, 1580), (330, 1552), (300, 1552), (300, 1800), (CX, 1800)]

# lower honeycomb and corner fins, separated by a solid ~2 mm black divider, both inset from the black edges
LOWER_HEX = [(752, 1438), (CX + 5, 1438), (CX + 5, 1700), (786, 1688)]
CORNER = [(700, 1458), (735, 1676), (600, 1662), (586, 1630), (595, 1582), (625, 1532), (660, 1488)]

HOOD_LINE = P([(CX, 972), (1100, 969), (900, 961), (700, 937), (580, 904), (510, 876), (472, 850), (462, 832)])
_sy = Y(800)                             # hood scoop: position compressed, thickness kept (~1.35 mm)
SCOOP = [(905, _sy - 2), (915, _sy - 12), (960, _sy - 15), (1050, _sy - 16), (CX, _sy - 16),
         (CX, _sy + 16), (1050, _sy + 15), (960, _sy + 12), (915, _sy + 9), (905, _sy + 4)]
# power-bulge crease rising from the scoop ends and running across behind it
BULGE = [(893, _sy + 6), (925, _sy - 24), (1000, _sy - 38), (1100, _sy - 41), (CX, _sy - 41)]

UOFF, LOFF, COFF = 0.5, 0.5333, 2.0     # relief phase (mm), tuned so few cells are clipped into slivers

SPEC = dict(
    id='civic_type_r_fl5', name='Honda Civic Type R (FL5)',
    ref=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ref', 'front.jpg'),
    units='px', px_left=322, px_right=2 * CX - 322, px_bottom=1742, center_x=CX,
    outline_half=OUTLINE,
    prims=[
        dict(kind='poly', color='black', pts=BAND),
        dict(kind='stroke', color='white', width=0.75, pts=DRL),
        dict(kind='poly', color='relief', pts=UPPER_HEX, relief=dict(type='hex', pitch=3.0, rib=0.9, margin=0.7, offset=UOFF)),
        dict(kind='poly', color='black', pts=LOWER),
        dict(kind='poly', color='black', pts=SLIT),
        dict(kind='poly', color='relief', pts=LOWER_HEX, relief=dict(type='hex', pitch=3.2, rib=0.9, margin=0.7, offset=LOFF)),
        dict(kind='poly', color='relief', pts=CORNER, mirror=False, relief=dict(type='vbars', pitch=2.4, rib=1.0, margin=0.0, angle=16, offset=COFF)),
        dict(kind='poly', color='relief', pts=M(CORNER), mirror=False, relief=dict(type='vbars', pitch=2.4, rib=1.0, margin=0.0, angle=-16, offset=-COFF)),
        dict(kind='poly', color='black', pts=SCOOP),
        dict(kind='stroke', color='groove', width=0.62, pts=HOOD_LINE, smooth=1),
        dict(kind='stroke', color='groove', width=0.62, pts=BULGE, smooth=1),
    ],
    badge=None,
    tab=dict(y_frac=0.65),
)
