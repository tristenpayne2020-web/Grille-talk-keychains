# Koenigsegg Jesko (2019+) front keychain - traced on Wikimedia Commons photo
# "Koenigsegg Jesko Auto Zuerich 2023 1X7A1382.jpg" (CC BY-SA 4.0), downscaled to 2600 px.
# Photo is taken from above -> heights compressed with y_scale. NO LOGOS (badge=None).
C = 1240

def _mx(pts):
    """mirror a left-half point list to the right half (for non-mirrored, side-specific prims)"""
    return [(2 * C - x, y) for x, y in pts]

# side duct opening (recessed carbon duct between the outer intake wall and the vertical fin)
DUCT = [(285,1560),(330,1548),(352,1600),(380,1590),(420,1520),(560,1572),(660,1625),(720,1660),
        (745,1800),(300,1790),(270,1700)]

SPEC = dict(
    id='jesko', name='Koenigsegg Jesko',
    ref='kc/cars/jesko/ref/front.jpg',
    units='px', px_left=194, px_right=2*C-194, px_bottom=1982, center_x=C, y_scale=0.68,
    outline_half=[(C,803),(1000,782),(800,748),(680,705),(620,690),(560,708),(470,752),(390,795),(320,838),
                  (280,885),(258,960),(250,1060),(250,1140),(238,1172),(212,1192),(194,1200),
                  (190,1260),(192,1350),(198,1420),(214,1452),(232,1466),(226,1540),(226,1700),
                  (248,1775),(300,1812),(450,1872),(800,1935),(1080,1966),(C,1982)],
    outline_smooth=1,
    prims=[
        # headlight: long pointed hexagonal lens (black), straight facets
        dict(kind='poly', color='black', pts=[(380,872),(394,884),(422,955),(434,1020),(438,1110),(438,1192),
             (432,1224),(412,1250),(385,1256),(358,1252),(340,1234),(312,1174),(304,1130),(309,1100),
             (345,965),(368,886)]),
        # U-shaped DRL light guide hugging the lower rim of the lens (white)
        dict(kind='stroke', color='white', width=0.75, smooth=0, pts=[(345,1070),(338,1120),(342,1160),
             (364,1198),(386,1212),(400,1210),(411,1196),(412,1140)]),
        # carbon fender-top air vents (curved blade along the fender crest)
        dict(kind='poly', color='black', smooth=1, pts=[(450,808),(530,762),(614,728),(604,790),(594,870),
             (588,948),(548,918),(492,866)]),
        # hood louvre slot (carbon strip across the front of the hood), sharp upturned tips
        dict(kind='poly', color='black', smooth=1, pts=[(834,834),(848,858),(882,900),(920,950),(970,995),
             (1100,1022),(C,1026),(C+30,1026),(C+30,1058),(C,1058),(1100,1054),(960,1030),(900,987),(856,915)]),
        # front canard / dive plane: tall pointed blade forming the outer corner of the silhouette
        dict(kind='poly', color='black', pts=[(194,1198),(222,1212),(240,1240),(250,1300),(266,1370),
             (292,1428),(350,1484),(300,1496),(240,1478),(212,1450),(176,1410),(172,1330),(172,1260)]),
        # whole lower nose: splitter, side ducts and central intake (carbon). Top edge has the white
        # "fang" lobe hanging down between the canard and the dark scoop, then sweeps to the nose tip.
        dict(kind='poly', color='black', pts=[(150,1400),(200,1420),(240,1478),(300,1494),(352,1482),(356,1530),
             (370,1552),(386,1548),(396,1500),(404,1466),(440,1474),(500,1494),(570,1530),(650,1580),
             (730,1630),(800,1652),(870,1670),(936,1690),(1079,1719),(1180,1732),(C,1736),
             (C,1990),(1080,1975),(800,1945),(450,1880),(290,1820),(200,1790),(150,1600)]),
        # side duct: diagonal carbon-weave relief, chevron (left /, right \)
        dict(kind='poly', color='relief', mirror=False, pts=DUCT,
             relief=dict(type='hbars', pitch=1.5, rib=0.7, angle=-45, margin=0.5)),
        dict(kind='poly', color='relief', mirror=False, pts=_mx(DUCT),
             relief=dict(type='hbars', pitch=1.5, rib=0.7, angle=45, margin=0.5)),
        # vertical fin between side duct and central intake
        dict(kind='stroke', color='white', width=0.7, pts=[(752,1668),(768,1760),(784,1862)]),
        # splitter lip crease: shallow V to the centre
        dict(kind='stroke', color='white', width=0.7, pts=[(520,1846),(800,1876),(C,1904)]),
        # centre nose seam
        dict(kind='stroke', color='black', width=0.7, mirror=False, pts=[(C,1540),(C,1740)]),
        # hood / front clam shut line
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(590,960),(614,993),(640,1080),(662,1200),
             (690,1310),(730,1372),(829,1429),(1007,1493),(1186,1529),(C,1533)]),
    ],
    badge=None,
    tab=dict(y_mm=25.0),
)
