# Tesla Model 3 "Highland" (2024+) - front keychain artwork.
# Reference: ref/front_std.jpg (2560x1920) - Tesla press photo of the 2024 Model 3 as republished by NetCarShow
# (https://www.netcarshow.com/Tesla-Model_3-2024-Front.5b74ffa8.jpg, (c) Tesla, press image, used only as a tracing
# reference, never redistributed in the product). Viewer's-left half traced, mirrored about center_x.
# NO LOGOS (user rule): the T badge on the nose is left as plain body; badge=None.
SPEC = dict(
    id='tesla_model3', name='Tesla Model 3 (Highland, 2024+)',
    ref='kc/cars/tesla_model3/ref/front_std.jpg',
    units='px', px_left=578, px_right=2002, px_bottom=1482, center_x=1290,
    outline_half=[(1290, 886), (1000, 885), (800, 886), (752, 891), (712, 908), (670, 935), (630, 966), (600, 1000),
                  (584, 1036), (578, 1090), (578, 1250), (582, 1340), (586, 1410), (592, 1442), (606, 1462),
                  (650, 1470), (800, 1476), (1000, 1480), (1290, 1482)],
    outline_smooth=1,
    prims=[
        # headlight unit: slim, angular, sharp inner tip pointing at the nose
        dict(kind='poly', color='black', pts=[(624, 1046), (634, 1039), (700, 1050), (780, 1067), (850, 1089),
                                              (896, 1108), (920, 1159), (912, 1160), (870, 1156), (780, 1150), (700, 1142),
                                              (652, 1134), (630, 1124), (624, 1105)]),
        # LED DRL: the thin "L" - vertical at the outer edge, then the long bar along the bottom of the lens
        dict(kind='stroke', color='white', width=0.7, pts=[(647, 1056), (647, 1098), (659, 1112), (712, 1116),
                                                             (735, 1125), (888, 1136)]),
        # slim lower intake slot (one wide slot, mirrored -> spans the centre)
        dict(kind='poly', color='black', pts=[(1330, 1401), (920, 1401), (885, 1403), (858, 1410), (838, 1422),
                                              (822, 1438), (812, 1457), (1330, 1457)]),  # plain gloss-black slot, no slats (Highland has none)
        # hood shut line: from the cowl, down beside the headlight, then across the smooth nose
        dict(kind='stroke', color='groove', width=0.6, smooth=2,
             pts=[(760, 904), (800, 950), (845, 997), (885, 1050), (918, 1090), (950, 1118), (985, 1132),
                  (1050, 1140), (1150, 1143), (1290, 1144), (1330, 1144)]),
        # bumper character line under the headlights
        dict(kind='stroke', color='groove', width=0.6, smooth=2,
             pts=[(705, 1168), (800, 1176), (950, 1184), (1100, 1189), (1290, 1191), (1330, 1191)]),
        # lower-fascia sweep: lower edge of the sculpted bumper surface above the intake
        dict(kind='stroke', color='groove', width=0.6, smooth=2,
             pts=[(682, 1318), (740, 1336), (810, 1360), (900, 1375), (1050, 1381), (1290, 1382), (1330, 1382)]),
    ],
    badge=None,
    tab=dict(y_frac=0.53),
)
