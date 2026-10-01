# Lamborghini Huracan EVO (2019-2024) front keychain.
#
# Reference: ref/front.jpg = Flickr 54124826722 "Lamborghini Huracan EVO" (Monaco street photo, 2048x1365),
# levelled by +1.5 deg -> ref/front_lvl.jpg (all coordinates below are pixels of front_lvl.jpg).
# The car is very slightly yawed (its left flank is visible), so ONE half is traced: the viewer's RIGHT half,
# which shows the true silhouette without flank. That half is a little foreshortened horizontally (compared
# with the opposite half and a second near-frontal photo, ~8 %), so y_scale 0.92 restores the aspect ratio.
# NO LOGOS: badge=None, the shield spot on the nose is left as plain body.

CX = 1097

SPEC = dict(
    id='huracan_evo', name='Lamborghini Huracan EVO',
    ref='kc/cars/huracan_evo/ref/front_lvl.jpg',
    units='px', px_left=2 * CX - 1615, px_right=1615, px_bottom=1172, center_x=CX, y_scale=0.92,
    outline_half=[(CX, 716), (1250, 715), (1400, 707), (1480, 699),
                  (1522, 707), (1560, 724), (1590, 750), (1607, 780), (1615, 812), (1619, 860), (1620, 920),
                  (1618, 1000), (1614, 1060), (1613, 1108), (1620, 1124), (1612, 1146), (1594, 1164),
                  (1560, 1172), (CX, 1172)],
    prims=[
        # ---- lower front: everything below the nose lip is black (centre intake, side intakes, splitter)
        dict(kind='poly', color='black',
             pts=[(1085, 1028), (1160, 1026), (1240, 1022), (1300, 1014), (1330, 1007), (1400, 998), (1480, 992),
                  (1520, 987), (1545, 982), (1566, 981), (1580, 997), (1592, 1032), (1597, 1080), (1598, 1104),
                  (1630, 1110), (1640, 1200), (1085, 1200)]),
        # centre lower grille: horizontal slats
        dict(kind='poly', color='relief', mirror=True,
             pts=[(1085, 1034), (1160, 1032), (1240, 1028), (1300, 1020), (1322, 1015), (1336, 1098), (1085, 1100)],
             relief=dict(type='hbars', pitch=1.6, rib=0.7, margin=0.6, offset=0.5)),
        # side intake mesh (honeycomb) between the centre grille and the blade
        dict(kind='poly', color='relief',
             pts=[(1340, 1012), (1400, 1004), (1480, 998), (1512, 994), (1504, 1090), (1352, 1094)],
             relief=dict(type='hex', pitch=2.5, rib=0.75, margin=0.6, min_w=0.7, offset=1.2)),
        # outer corner vent: plain black (the slanted fins only left slivers in such a narrow box)
        # body-coloured intake divider: tapered, slightly leaning blade forking into the lower wing (EVO intake)
        dict(kind='poly', color='white',
             pts=[(1523, 984), (1546, 982), (1531, 1090), (1546, 1104), (1580, 1106), (1630, 1102), (1630, 1126),
                  (1590, 1128), (1550, 1128), (1520, 1115), (1350, 1117), (1340, 1109), (1352, 1099),
                  (1505, 1097), (1513, 1090)]),

        # ---- headlight unit (black) + Y-shaped DRL signature (white)
        dict(kind='poly', color='black',
             pts=[(1390, 901), (1553, 820), (1559, 826), (1549, 876), (1542, 900), (1533, 910), (1442, 936),
                  (1428, 936), (1410, 921)]),
        dict(kind='stroke', color='white', width=0.8, pts=[(1414, 905), (1432, 921)]),               # inner dash
        dict(kind='stroke', color='white', width=0.8, pts=[(1473, 875), (1469, 891), (1457, 916)]),  # Y stem
        dict(kind='stroke', color='white', width=0.8, pts=[(1469, 891), (1484, 896), (1496, 906)]),  # Y branch
        dict(kind='stroke', color='white', width=0.8, pts=[(1542, 838), (1537, 862), (1524, 886), (1518, 896)]),

        # ---- engraved body lines
        dict(kind='stroke', color='groove', width=0.62,              # hood / fender shut line -> lamp inner tip
             pts=[(1480, 700), (1464, 744), (1440, 800), (1416, 848), (1398, 884), (1390, 901)]),
        dict(kind='stroke', color='groove', width=0.62,              # hood front edge with the centre bump
             pts=[(1390, 901), (1320, 912), (1260, 921), (1200, 927), (1174, 929), (1156, 922), (1132, 916),
                  (1085, 914)]),
        dict(kind='stroke', color='groove', width=0.62, pts=[(1238, 712), (1252, 738), (1336, 880)]),  # hood ridge
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
