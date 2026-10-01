# BMW M5 (G90, 2025+) front keychain - traced in photo pixels from a real straight-on photo:
#   ref/front.jpg = Wikimedia Commons "File:BMW G90 M5 Brooklyn Grey Metallic (2).jpg" by Damian B Oh (CC BY-SA 4.0,
#   taken 2025-09-04: a Korean-registered Brooklyn Grey M5 in an underground car park), downscaled to 2000x1500.
#   See ref/SOURCE.txt.
# The viewer's RIGHT half is traced (mirrored by the pipeline). NO LOGOS: no roundel, no M5 lettering (badge=None).
from shapely.geometry import Polygon, box


def _chaikin(pts, n=2):
    p = list(pts)
    for _ in range(n):
        q = []
        for i in range(len(p)):
            a, b = p[i], p[(i + 1) % len(p)]
            q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]),
                  (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        p = q
    return p


def _inset(pts, d):
    g = Polygon(pts).buffer(-d, join_style=1)
    return [(round(x, 1), round(y, 1)) for x, y in g.exterior.coords]


CX = 1000
# right kidney (crosses the centreline -> merged with its mirror at the top centre; white V notch at the bottom centre)
KIDNEY_RAW = [(985, 718), (1000, 717), (1020, 711), (1034, 701), (1050, 692), (1110, 690), (1355, 690), (1398, 701), (1424, 720),
              (1438, 750), (1442, 793), (1437, 833), (1414, 867), (1375, 906), (1338, 940), (1305, 951), (1075, 952),
              (1042, 944), (1020, 924), (1008, 910), (1000, 903), (985, 903)]
KIDNEY = _chaikin(KIDNEY_RAW, 2)
_KC = Polygon(KIDNEY).intersection(box(1000, 0, 3000, 3000))      # this kidney only (centre side = x 1000)
KIDNEY_ONE = list(_KC.exterior.coords)
GLOW = _inset(KIDNEY_ONE, 22)          # the "Iconic Glow" contour line, ~1.1 mm inside the black frame
SLATS = _inset(KIDNEY_ONE, 44)         # slatted interior

SPEC = dict(
    id='g90_m5', name='BMW M5 (G90)',
    ref='kc/cars/g90_m5/ref/front.jpg',
    units='px', px_left=211, px_right=1789, px_bottom=1260, center_x=CX,
    outline_half=[(1000, 514), (1300, 515), (1460, 517), (1522, 519), (1548, 524), (1600, 565), (1636, 603),
                  (1668, 646), (1709, 697), (1745, 744), (1768, 798), (1782, 853), (1788, 920), (1789, 1000),
                  (1786, 1080), (1781, 1140), (1772, 1185), (1760, 1214), (1744, 1238), (1712, 1252), (1500, 1258),
                  (1000, 1260)],
    outline_smooth=1,
    prims=[
        # headlight unit (whole lens black) - slim, inner tip pointing at the kidney top corner
        dict(kind='poly', color='black', pts=[(1460, 731), (1550, 706), (1640, 681), (1664, 668), (1680, 681),
                                              (1700, 708), (1718, 733), (1721, 768), (1713, 781), (1505, 803),
                                              (1491, 798)]),
        # DRL signature: two near-vertical LED elements
        # (full lamp-height bars; the outer one turns inward along the top edge)
        dict(kind='stroke', color='white', width=0.9, pts=[(1576, 722), (1572, 771)]),
        dict(kind='stroke', color='white', width=0.9, pts=[(1654, 706), (1676, 708), (1685, 758)]),
        # kidney: black frame, white glow contour, slatted interior
        dict(kind='poly', color='black', pts=KIDNEY),
        dict(kind='stroke', color='white', width=0.85, pts=GLOW),
        dict(kind='poly', color='relief', pts=SLATS, relief=dict(type='hbars', pitch=2.4, rib=1.1, offset=0.4)),
        # wide centre intake (the M "X" bumper) - merges with the black splitter
        dict(kind='poly', color='black', pts=[(1000, 985), (1200, 981), (1446, 980), (1586, 1157),
                                              (1537, 1224), (1000, 1230)]),
        # intake structure engraved into the black (mostly open gloss black on the car): centre divider,
        # one vertical fin each side, lower frame line separating the intake from the splitter
        dict(kind='stroke', color='groove', width=0.7, mirror=False, pts=[(1000, 1110), (1000, 1218)]),
        dict(kind='stroke', color='groove', width=0.7, pts=[(1334, 1050), (1338, 1200)]),
        dict(kind='stroke', color='groove', width=0.7, pts=[(1000, 1216), (1500, 1212)]),
        # splitter / lip
        dict(kind='poly', color='black', pts=[(1000, 1226), (1536, 1223), (1575, 1219), (1752, 1201), (1810, 1190),
                                              (1810, 1300), (1000, 1300)]),
        # corner air curtain
        dict(kind='poly', color='black', pts=[(1733, 998), (1757, 1150), (1675, 1137)]),
        # hood: dome crease, crease above the lamp, hood-to-fender seam
        dict(kind='stroke', color='groove', width=0.7, smooth=2, pts=[(1060, 655), (1075, 620), (1086, 575), (1091, 542)]),
        # hood shut line: one continuous line from the windscreen corner, turning along the top of the lamp
        dict(kind='stroke', color='groove', width=0.7, smooth=2,
             pts=[(1534, 548), (1572, 567), (1612, 602), (1642, 645), (1625, 662), (1550, 652), (1452, 646)]),
        # parking sensor: small solid dot so it cannot be mistaken for the tow-hook cover ring
        dict(kind='circle', color='black', c=(1673, 1021), r_mm=0.5),
        # single front tow-hook cover (viewer's left only, as on the car)
        dict(kind='ring', color='black', c=(600, 949), r_mm=1.1, width=0.55, mirror=False),
    ],
    badge=None,
    tab=dict(y_frac=0.52),
)
