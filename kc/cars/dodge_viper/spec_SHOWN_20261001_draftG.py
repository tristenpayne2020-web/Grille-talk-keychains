# Dodge Viper (5th gen VX, 2013-2017) - traced on a straight-on front photo of a 2014 SRT Viper GTS
# ref: https://commons.wikimedia.org/wiki/File:2014_Viper_(9526066709).jpg  (Patrick Corcoran, CC BY 2.0), cropped
# NO LOGOS: the fanged-viper badge spot on the nose is left plain body.
CX = 1390

SPEC = dict(
    id='dodge_viper', name='Dodge Viper (VX)',
    ref='kc/cars/dodge_viper/ref/front.jpg',
    units='px', px_left=100, px_right=2680, px_bottom=1312, center_x=CX,
    outline_half=[(CX, 382), (1200, 384), (1000, 389), (800, 394), (600, 397), (480, 400), (400, 405),
                  (320, 420), (240, 450), (178, 490), (140, 532), (115, 590), (102, 680), (98, 800), (99, 950),
                  (102, 1100), (108, 1170), (116, 1205), (128, 1245), (155, 1280), (210, 1300), (400, 1309),
                  (800, 1312), (CX, 1312)],
    outline_smooth=1,
    prims=[
        # snake-eye headlight (whole lens, black) - compact teardrop, blunt inner tip at the real lens tip
        dict(kind='poly', color='black', smooth=2, pts=[(232, 560), (250, 530), (290, 516), (350, 514), (420, 528),
             (490, 557), (545, 595), (585, 640), (612, 690), (630, 728), (634, 750), (610, 762), (540, 764),
             (440, 760), (350, 752), (285, 736), (250, 708), (234, 662), (228, 610)]),
        # LED DRL strip: down the outer edge and along the bottom, >= 0.6 mm black kept outside it
        dict(kind='stroke', color='white', width=0.7, smooth=2,
             pts=[(268, 562), (262, 620), (270, 672), (300, 706), (370, 722), (470, 730), (560, 730)]),
        # projector lens (on the real projector)
        dict(kind='ring', color='white', c=(374, 632), r_mm=1.7, width=0.55),
        # hood vents (stylised extractors either side of the power bulge), blunt ends
        dict(kind='poly', color='black', smooth=1, pts=[(700, 452), (790, 443), (950, 464), (948, 500), (780, 477), (700, 482)]),
        # central hood scoop on the power bulge
        dict(kind='poly', color='black', smooth=1, pts=[(CX + 40, 498), (1250, 498), (1218, 510), (1212, 530), (1225, 552),
             (1260, 565), (1340, 570), (CX + 40, 570)]),
        # wide mouth grille, honeycomb mesh (each half stops ~0.6 mm short of the centre U-frame)
        dict(kind='poly', color='black', smooth=2, pts=[(1289, 902), (1260, 894), (1000, 895), (800, 900), (690, 912), (610, 930),
             (555, 958), (520, 1000), (505, 1060), (515, 1115), (550, 1155), (620, 1180), (750, 1192), (1000, 1196),
             (1330, 1194), (1320, 1150), (1309, 1110), (1297, 1000)],
             relief=dict(type='hex', pitch=2.2, rib=0.7, margin=0.7, offset=1.1)),
        # centre V insert (flat black) incl. the border strip next to the mesh
        dict(kind='poly', color='black', pts=[(CX, 893), (1300, 893), (1286, 905), (1294, 1000), (1306, 1110), (1317, 1150),
             (1326, 1188), (CX, 1194)]),
        # U-frame around the centre insert (0.8 mm, stops above the V tip)
        dict(kind='stroke', color='white', width=0.8, pts=[(1322, 896), (1330, 1000), (1342, 1110), (1352, 1146), (CX, 1160)]),
        # outer side intakes
        dict(kind='poly', color='black', smooth=2, pts=[(190, 930), (240, 912), (300, 905), (318, 930), (305, 1000),
             (305, 1080), (320, 1130), (340, 1160), (260, 1165), (200, 1150), (175, 1100), (172, 1000)]),
        # front splitter (black lip, ~2 mm)
        dict(kind='poly', color='black', pts=[(CX, 1248), (800, 1246), (400, 1243), (220, 1236), (150, 1226), (110, 1222),
             (100, 1330), (CX, 1330)]),
        # engraved lines: hood shut line (starts inside the lens tip)
        dict(kind='stroke', color='groove', width=0.6, pts=[(618, 744), (680, 727), (800, 721), (1100, 717), (CX, 716)]),
        # power-bulge edges: gentle, nearly parallel, widening slightly to the nose
        dict(kind='stroke', color='groove', width=0.6, smooth=2, pts=[(1000, 400), (1010, 470), (1026, 560), (1044, 640), (1060, 714)]),
        # fender / bumper split (starts 1 mm inside the outline, clear of the tab neck)
        dict(kind='stroke', color='groove', width=0.6, pts=[(135, 727), (228, 730)]),
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
