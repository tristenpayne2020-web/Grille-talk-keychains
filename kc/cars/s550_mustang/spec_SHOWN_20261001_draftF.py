# Ford Mustang GT (S550 facelift, 2018-2023) - front keychain.
# Reference: ref/front.jpg = crop (x 2200-5500, y 1000-3400) of ref/front_raw.jpg scaled to 2200x1600 px.
# front_raw.jpg: 2022 Ford Mustang GT California Special press photo (Car and Driver gallery), dead-centred and level,
# camera above the hood. See ref/SOURCE.txt. Traced half = viewer's LEFT. Centreline x = 1100.
# The camera is high, so the hood is seen from above: y_scale 0.88 squeezes the (stretched) fascia and the hood band
# above the headlights is drawn as it reads in a level elevation (cross-checked with the level S550 GT500 photo and a
# near-level 2022 GT, ref/wm_grey22a.jpg), not traced from this photo.
# NO LOGOS (user rule): no pony, no GT/CS script - the grille is plain mesh. badge=None.

CX = 1100
YB = 1492          # bottom of the splitter

OUTLINE = [(1100, 476), (800, 482), (560, 494), (400, 503), (300, 503), (240, 505), (196, 518), (160, 546),
           (136, 600), (122, 668), (116, 745), (118, 810), (124, 880), (128, 940), (131, 1000), (137, 1100),
           (145, 1200), (150, 1240), (158, 1285), (172, 1330), (196, 1395), (226, 1439), (300, 1452), (435, 1464),
           (604, 1473), (747, 1482), (1100, 1492)]

# lamp: level-view outline, blunt rounded outer end, sharp arrowhead inner tip (the 'angry' S550 lamp)
HEADLIGHT = [(150, 744), (162, 731), (184, 726), (215, 734), (300, 760), (400, 790), (466, 806), (424, 860),
             (376, 896), (300, 900), (226, 886), (174, 860), (154, 826), (149, 785)]

UPPER_GRILLE = [(1100, 904), (800, 903), (560, 903), (538, 912), (404, 1034), (406, 1048), (460, 1101),
                (600, 1125), (747, 1139), (950, 1150), (1100, 1156)]

LOWER_GRILLE = [(1100, 1262), (685, 1251), (497, 1245), (360, 1240), (330, 1250), (300, 1288), (345, 1322),
                (497, 1360), (747, 1383), (1100, 1392)]

SPLITTER = [(1100, 1425), (685, 1415), (497, 1400), (247, 1318), (204, 1300), (150, 1240), (100, 1240),
            (100, 1530), (1100, 1530)]

# corner: short slanted lamp strip joined to the black triangular vent under it (vent dominates)
CORNER = [(162, 996), (178, 1006), (366, 1096), (368, 1126), (250, 1110), (212, 1204), (194, 1206), (178, 1160),
          (164, 1085)]

# tri-bar DRL: three slanted bars "///" in the inner end of the lens, parallel to the lamp's inner edge
BARS = [[(328, 800), (302, 866)], [(366, 806), (340, 872)], [(404, 818), (380, 866)]]

VENT = [(582, 596), (601, 568), (790, 561), (808, 577), (792, 606), (601, 614)]

LO_OFF = 1.0
HEX = dict(type='hex', pitch=2.0, rib=0.65, margin=0.6)

prims = [
    # hood leading edge (shut line above the grille), from the headlight tip to the centre
    dict(kind='stroke', color='groove', width=0.62, smooth=2, pts=[(436, 816), (470, 803), (530, 795), (747, 787), (1100, 783)]),
    # hood / fender shut line from the headlight top up through the cowl edge
    dict(kind='stroke', color='groove', width=0.62, smooth=1, pts=[(212, 745), (230, 630), (262, 470)]),
    # GT hood: the two bulge strakes running back from each heat extractor
    dict(kind='stroke', color='groove', width=0.62, pts=[(586, 590), (560, 470)]),
    dict(kind='stroke', color='groove', width=0.62, pts=[(804, 572), (822, 470)]),
    dict(kind='poly', color='black', pts=HEADLIGHT),
    dict(kind='poly', color='black', pts=UPPER_GRILLE, relief=HEX),
    dict(kind='poly', color='black', pts=LOWER_GRILLE, relief=dict(HEX, offset=LO_OFF)),
    dict(kind='poly', color='black', pts=SPLITTER),
    dict(kind='poly', color='black', pts=CORNER),
    dict(kind='poly', color='black', pts=VENT),
] + [dict(kind='stroke', color='white', width=0.78, cap='round', pts=b) for b in BARS]

SPEC = dict(
    id='s550_mustang', name='Ford Mustang GT (S550 facelift)',
    ref='kc/cars/s550_mustang/ref/front.jpg',
    units='px', px_left=116, px_right=2084, px_bottom=YB, center_x=CX, y_scale=0.88,
    outline_half=OUTLINE, outline_smooth=1,
    prims=prims,
    badge=None,
    tab=dict(y_frac=0.55),
)
