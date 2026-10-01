# Ferrari F40 (1987-1992) front keychain.
# Reference: ref/front.jpg = 2000 px copy of Wikimedia Commons
#   "Paris - Bonhams 2016 - Ferrari F40 Berlinetta - 1990 - 005.jpg" (Thesupermat, CC BY-SA 4.0), see ref/SOURCE.txt.
# The photo has a slight yaw (the viewer's-left flank shows), so the viewer's RIGHT half is traced and mirrored about
# the true centreline (prancing-horse badge / centre of the radiator mouth, x = 1158).
# NO LOGOS: badge=None, the badge spot on the nose stays plain white body.
SPEC = dict(
    id='ferrari_f40', name='Ferrari F40',
    ref='kc/cars/ferrari_f40/ref/front.jpg',
    units='px', px_left=428, px_right=1888, px_bottom=1158, center_x=1158, y_scale=0.85,
    outline_half=[(1158, 480), (1350, 481), (1480, 485), (1560, 489), (1640, 491), (1710, 496), (1765, 505),
                  (1805, 522), (1835, 543), (1856, 574), (1869, 612), (1878, 660), (1884, 720), (1888, 790),
                  (1890, 870), (1890, 940), (1888, 1020), (1884, 1090), (1874, 1130), (1856, 1150), (1800, 1156),
                  (1500, 1158), (1158, 1158)],
    prims=[
        # fixed lamp unit behind its clear cover (black), slanted inboard edge, rounded outboard-bottom corner
        dict(kind='poly', color='black', pts=[(1590, 757), (1826, 757), (1829, 762), (1829, 872), (1825, 884),
                                              (1812, 890), (1620, 902), (1614, 897)]),
        # round driving lamp (white disc) inboard + amber indicator (two white bars) outboard - the F40's lamp signature
        dict(kind='circle', color='white', c=(1663, 840), r_mm=1.5),
        dict(kind='stroke', color='white', width=0.65, cap='round', pts=[(1714, 826), (1808, 826)]),
        dict(kind='stroke', color='white', width=0.65, cap='round', pts=[(1714, 854), (1808, 854)]),
        # radiator mouth (black, diamond mesh)
        dict(kind='poly', color='black', pts=[(1100, 985), (1528, 985), (1545, 988), (1554, 997), (1556, 1010),
                                              (1556, 1050), (1553, 1062), (1543, 1070), (1526, 1073), (1100, 1073)],
             relief=dict(type='diamond', pitch=2.5, rib=0.8, margin=0)),
        # side intakes (black, mesh)
        dict(kind='poly', color='black', pts=[(1676, 974), (1792, 974), (1798, 980), (1796, 1058), (1790, 1064),
                                              (1678, 1064), (1671, 1058), (1670, 980)],
             relief=dict(type='diamond', pitch=2.5, rib=0.8, margin=0)),
        # NACA hood ducts: wide trapezoid mouth tapering into the narrow NACA tail running down the hood (black)
        dict(kind='poly', color='black', smooth=1,
             pts=[(1276, 583), (1368, 581), (1352, 606), (1340, 630), (1335, 652), (1321, 652), (1316, 630),
                  (1304, 606)]),
        # black rubbing strip across the nose
        dict(kind='stroke', color='black', width=1.0, smooth=2,
             pts=[(1100, 951), (1500, 949), (1700, 944), (1800, 937), (1845, 929), (1868, 919), (1904, 896)]),
        # black chin lip
        dict(kind='poly', color='black', pts=[(1100, 1120), (1600, 1120), (1840, 1116), (1882, 1106),
                                              (1874, 1140), (1856, 1152), (1800, 1160), (1100, 1160)]),
        # engraved: hood shut lines, closed pop-up headlight covers
        dict(kind='stroke', color='groove', width=0.7, cap='round', pts=[(1478, 503), (1525, 632), (1558, 750), (1578, 872)]),
        dict(kind='stroke', color='groove', width=0.7, cap='round',
             pts=[(1572, 628), (1808, 636), (1817, 640), (1826, 723), (1820, 730), (1590, 720), (1583, 714),
                  (1567, 636), (1572, 628)]),
    ],
    badge=None,
    tab=dict(y_frac=0.58),
)
