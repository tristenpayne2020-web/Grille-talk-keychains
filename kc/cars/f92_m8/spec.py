# BMW M8 Competition Coupe (F92, 2020+) front keychain
# Traced on BMW Group PressClub photo P90348785 ("The all-new BMW M8 Competition Coupe (06/2019)"), straight front:
#   https://www.press.bmwgroup.com/global/photo/detail/P90348785/the-all-new-bmw-m8-competition-coupe-06/2019
#   (BMW AG press image, (c) BMW AG, free for editorial use; used only as a tracing reference).
# ref/front_level.jpg = crop (600,750) of the 4500x3002 original, brightened, levelled +0.2 deg.
# Left half traced (viewer's left), mirrored about the centreline x=1647.
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union

PX_L, PX_R, PX_B, CX = 241, 3053, 1634, 1647
S = 80.5 / (PX_R - PX_L)                         # mm per photo pixel


def mm_x(x):
    return (x - CX) * S


def mm_pt(p):
    return ((p[0] - CX) * S, (PX_B - p[1]) * S)


# ------------------------------------------------------------------------------------------------ shapes (px)
KIDNEY = [(1619, 752), (1604, 727), (1580, 712), (1540, 703), (1460, 692), (1340, 688), (1180, 687), (1044, 691),
          (988, 697), (940, 713), (900, 737), (860, 772), (828, 812), (804, 846), (789, 892), (792, 928),
          (812, 964), (830, 988), (860, 1012), (900, 1032), (980, 1048), (1100, 1056), (1260, 1058), (1420, 1056),
          (1540, 1050), (1590, 1042), (1612, 1028), (1619, 1005)]

SIDE_INTAKE = [(322, 983), (384, 977), (538, 987), (692, 1014), (768, 1033), (815, 1048), (838, 1068), (842, 1091),
               (822, 1137), (799, 1191), (768, 1252), (730, 1322), (699, 1375), (676, 1398), (645, 1405), (461, 1406),
               (345, 1402), (322, 1391), (311, 1345), (303, 1229), (299, 1114), (303, 1014), (307, 995)]
MESH_SIDE = [(384, 1133), (615, 1160), (800, 1190), (820, 1190), (820, 1420), (384, 1420)]   # honeycomb below the flap

CENTRE_INTAKE = [(1647, 1200), (963, 1200), (937, 1232), (902, 1284), (880, 1354), (876, 1397), (885, 1420),
                 (911, 1440), (1000, 1448), (1200, 1454), (1400, 1460), (1647, 1462)]
RADAR = [(1647, 1238), (1560, 1240), (1515, 1248), (1500, 1270), (1498, 1462), (1647, 1462)]


def double_slats(centres_px, rib=0.7, gap=0.7, inset=1.0):
    """F92 kidney: pairs of vertical slats (mirrored), relief ribs in keychain mm, stopping `inset` mm short of the
    kidney wall so the gloss-black surround reads as a frame."""
    inner = Polygon([mm_pt(p) for p in KIDNEY]).buffer(-inset)
    bars = []
    for c in centres_px:
        xc = mm_x(c)
        for dx in (-(gap + rib) / 2, (gap + rib) / 2):
            x0, x1 = xc + dx - rib / 2, xc + dx + rib / 2
            spans = []
            for x in (x0, x1):
                seg = inner.intersection(LineString([(x, -1), (x, 60)]))
                spans.append(seg.bounds[1::2] if not seg.is_empty else None)
            if None in spans:
                continue
            y0, y1 = max(spans[0][0], spans[1][0]), min(spans[0][1], spans[1][1])
            if y1 - y0 > 1.0:
                bars.append(box(x0, y0, x1, y1))
                bars.append(box(-x1, y0, -x0, y1))
    return unary_union(bars)


def honeycomb(a=1.7, b=0.95, h=0.8, rib=0.65, y0=0.0):
    """M-style horizontally stretched honeycomb (pointy left/right cells), symmetric about x=0, keychain mm."""
    cells = []
    step_x = a + b
    for i in range(-30, 31):
        x = i * step_x
        for j in range(-5, 40):
            y = y0 + j * 2 * h + (h if i % 2 else 0)
            hexa = Polygon([(x + a, y), (x + b, y + h), (x - b, y + h), (x - a, y), (x - b, y - h), (x + b, y - h)])
            cells.append(hexa.buffer(-rib / 2, join_style=2))
    return box(-60, -5, 60, 60).difference(unary_union(cells))


def full_poly(half_px):
    """Half shape traced from the centreline (px) -> full symmetric polygon in keychain mm."""
    g = Polygon([mm_pt(p) for p in half_px]).buffer(0)
    return unary_union([g, Polygon([(-x, y) for x, y in g.exterior.coords])]).buffer(0)


# centre intake mesh = intake minus the ACC radar housing (the housing stays flush black, like a plate in the mesh)
RADAR_G = full_poly(RADAR).buffer(-1.0, join_style=1).buffer(1.0, join_style=1).union(
    full_poly(RADAR).intersection(box(-20, -1, 20, (PX_B - 1440) * S)))       # rounded top corners, square foot
CENTRE_MESH = full_poly(CENTRE_INTAKE).difference(RADAR_G)

SLATS = double_slats([946, 1064, 1184, 1304, 1424, 1544], rib=0.7, gap=0.7)
HONEY = honeycomb(y0=(PX_B - 1300) * S)

SPEC = dict(
    id='f92_m8', name='BMW M8 Competition (F92)',
    ref='kc/cars/f92_m8/ref/front_level.jpg',
    units='px', px_left=PX_L, px_right=PX_R, px_bottom=PX_B, center_x=CX,
    outline_half=[(1647, 236), (1300, 236), (1000, 237), (800, 239), (720, 245), (660, 260), (610, 282), (568, 305),
                  (530, 333), (497, 360), (472, 384), (448, 406), (420, 428), (392, 447), (362, 466), (335, 485),
                  (315, 503), (300, 523), (289, 545), (279, 570), (270, 595), (263, 620), (257, 655), (252, 700), (247, 750), (243, 800), (241, 850),
                  (244, 900), (252, 940), (260, 980), (263, 1040), (263, 1150), (264, 1250), (266, 1310), (274, 1350),
                  (287, 1392), (302, 1428), (322, 1458), (350, 1487), (385, 1515), (420, 1555), (465, 1586),
                  (600, 1600), (800, 1611), (1000, 1619), (1200, 1627), (1400, 1632), (1647, 1634)],
    prims=[
        # headlight unit
        dict(kind='poly', color='black', pts=[(290, 572), (360, 574), (420, 583), (520, 606), (620, 640), (720, 678),
                                              (842, 724), (822, 748), (782, 792), (750, 826), (722, 846), (650, 852),
                                              (560, 848), (470, 842), (400, 832), (345, 818), (300, 795), (275, 770),
                                              (258, 740), (240, 700), (240, 640), (252, 608), (270, 585)]),
        # DRL: the two hexagonal "L" light guides (outer + inner), white strokes; the outer one tucks into the inner one
        dict(kind='stroke', color='white', width=0.8, pts=[(312, 622), (305, 680), (310, 735), (330, 765), (352, 781),
                                                             (478, 787), (505, 776), (527, 766)]),
        dict(kind='stroke', color='white', width=0.8, pts=[(530, 690), (522, 740), (532, 778), (552, 803), (595, 812),
                                                             (695, 812), (718, 801)]),
        # kidney grille: black surround + double vertical slats
        dict(kind='poly', color='black', pts=KIDNEY, relief=dict(type='custom', ribs=SLATS)),
        # outer intake: black (carbon flap + air curtain flush), honeycomb in the mesh part
        dict(kind='poly', color='black', pts=SIDE_INTAKE),
        dict(kind='poly', color='relief', pts=MESH_SIDE, relief=dict(type='custom', ribs=HONEY)),
        # centre intake with honeycomb, radar housing flush black in the middle
        dict(kind='poly', color='black', pts=CENTRE_INTAKE),
        dict(kind='geom', color='relief', geom=CENTRE_MESH, relief=dict(type='custom', ribs=HONEY)),
        # lower lip / splitter (carbon wings + black lip)
        dict(kind='poly', color='black', pts=[(1647, 1534), (1400, 1530), (1100, 1521), (950, 1506), (850, 1480),
                                              (600, 1466), (450, 1466), (420, 1480), (390, 1515), (380, 1540),
                                              (380, 1700), (1647, 1700)]),
        # grooves: hood/fender shut line, power-dome creases
        dict(kind='stroke', color='groove', width=0.62, pts=[(397, 576), (388, 530), (383, 485), (386, 455), (398, 430)]),
        dict(kind='stroke', color='groove', width=0.62, pts=[(952, 268), (1030, 430), (1108, 592)]),
        # parking sensor + ONE tow-hook cover (viewer's left only)
        dict(kind='ring', color='black', c=(1137, 1112), r_mm=0.95, width=0.55),
        dict(kind='ring', color='black', c=(929, 1110), r_mm=1.3, width=0.55, mirror=False),
    ],
    badge=dict(type='roundel', c=(1647, 625), d=4.0),
    tab=dict(y_frac=0.50),
)
