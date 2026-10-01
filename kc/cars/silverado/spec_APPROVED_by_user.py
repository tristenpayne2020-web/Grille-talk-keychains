# Chevrolet Silverado 1500 (2022+ refresh, T1 "GMTT1XX" facelift) front keychain - RST trim (body-colour grille bar)
# Reference: ref/front.jpg = horizontally rectified + mirrored copy of ref/gma_rst_009.jpg (GM Authority spy/real-world
# photo of a 2022 Silverado RST, see ref/SOURCE.txt). The photo has a small yaw, so the near (viewer's right) half was
# remapped with landmark-averaged widths (both halves + the straight-on press night shot ref/press_drl_night.jpg)
# and mirrored. Traced half = viewer's RIGHT, centreline x = 700 px.  Scale: 1272 px = 80.5 mm (15.8 px/mm).
# NO LOGOS (user rule): the bowtie is NOT drawn; its spot is plain black upper grille / plain white bar.
# Revision 1: chunky filled white C light pipe with a uniform ~0.62 mm black outline, 0.55 mm grooves, fewer hood
# lines, G80-scale slats (3 heavy blades + segment dividers on the lower grille), 3 LED fog bars, tab on the C notch.

CX = 700

SLATS_VENT = dict(type='hbars', pitch=2.0, rib=0.9)       # corner vents + lower centre intake
SLAT_UPPER = dict(type='hbars', pitch=10.0, rib=0.9)      # upper slot: one centre bar
SLATS_BIG = dict(type='hbars', pitch=2.6, rib=1.3)        # lower grille: 3 heavy blades
DIVIDER = dict(type='hbars', pitch=50.0, rib=40.0)        # fills its (thin) strip = a vertical relief divider

SPEC = dict(
    id='silverado', name='Chevrolet Silverado 1500 (2022+)',
    ref='kc/cars/silverado/ref/front.jpg',
    units='px', px_left=2 * CX - 1336, px_right=1336, px_bottom=836, center_x=CX,
    outline_half=[(CX, 42), (1000, 44), (1180, 50), (1270, 60), (1305, 75), (1322, 100), (1330, 150), (1334, 220),
                  (1336, 400), (1336, 600), (1330, 624), (1314, 640), (1308, 700), (1302, 762), (1296, 800),
                  (1270, 822), (1100, 833), (CX, 836)],
    prims=[
        # ---- slim headlamp + C-shaped DRL housing + corner vent (one black lamp graphic per side).
        # The body-colour notch inside the C is cut out and stays open to the white fender.
        dict(kind='poly', color='black', pts=[(1098, 248), (1150, 243), (1282, 226), (1298, 214), (1302, 226),
                                              (1302, 315), (1206, 329), (1198, 337), (1198, 355), (1206, 364),
                                              (1302, 367), (1300, 526), (1246, 528), (1185, 452), (1138, 452),
                                              (1138, 304), (1100, 304)]),
        # corner vent slats (relief only, below the C)
        dict(kind='poly', color='relief', pts=[(1150, 412), (1300, 412), (1300, 526), (1246, 528), (1185, 452), (1150, 452)],
             relief=SLATS_VENT),
        # C-shaped LED DRL light pipe (filled white): wide inner arm, top arm sloping up along the lamp's lower edge,
        # bottom arm out toward the fender; black end caps keep it separate from the fender paint
        dict(kind='poly', color='white', pts=[(1149, 314), (1160, 304), (1288, 289), (1288, 305), (1196, 318),
                                              (1188, 326), (1188, 367), (1196, 374), (1288, 377), (1288, 396),
                                              (1157, 398), (1149, 390)]),
        # ---- grille: upper slot (bowtie spot left plain), thick body-colour bar (white gap), tall lower grille
        dict(kind='poly', color='black', pts=[(CX - 2, 248), (1110, 248), (1110, 304), (CX - 2, 304)], relief=SLAT_UPPER),
        dict(kind='poly', color='black', pts=[(CX - 2, 360), (1145, 360), (1145, 455),
                                              (1120, 480), (1102, 497), (CX - 2, 497)], relief=SLATS_BIG),
        # segment dividers in the lower grille (vertical relief ribs)
        dict(kind='poly', color='relief', pts=[(814, 360), (827, 360), (827, 497), (814, 497)], relief=DIVIDER),
        dict(kind='poly', color='relief', pts=[(994, 360), (1007, 360), (1007, 497), (994, 497)], relief=DIVIDER),
        # ---- lower bumper: centre intake + fog pockets + air dam (one black band)
        dict(kind='poly', color='black', pts=[(CX - 2, 628), (1062, 628), (1088, 636), (1104, 655), (1142, 735),
                                              (1158, 766), (1304, 766), (1300, 800), (1272, 824), (1100, 840),
                                              (CX - 2, 842)]),
        dict(kind='poly', color='relief', pts=[(CX - 2, 642), (885, 642), (885, 690), (CX - 2, 690)], relief=SLATS_VENT),
        # three stacked LED fog bars
        dict(kind='stroke', color='white', width=0.65, cap='flat', pts=[(988, 708), (1088, 708)]),
        dict(kind='stroke', color='white', width=0.65, cap='flat', pts=[(988, 728), (1088, 728)]),
        dict(kind='stroke', color='white', width=0.65, cap='flat', pts=[(988, 748), (1088, 748)]),
        # ---- engraved lines (0.55 mm like the G80): hood shut line, power-dome crease, hood/fender edge, bumper line
        dict(kind='stroke', color='groove', width=0.55, pts=[(CX, 213), (1000, 207), (1100, 200), (1270, 196)]),
        dict(kind='stroke', color='groove', width=0.55, smooth=3, pts=[(1040, 64), (1000, 82), (960, 98), (935, 115), (915, 132)]),
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(1272, 194), (1270, 140), (1284, 112), (1300, 98)]),
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(CX, 541), (1100, 545), (1140, 570), (1178, 606),
                                                                      (1205, 612), (1336, 612)]),
    ],
    badge=None,
    tab=dict(y_frac=0.62),
)
