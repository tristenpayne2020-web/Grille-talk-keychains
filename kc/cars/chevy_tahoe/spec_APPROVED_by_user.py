# Chevrolet Tahoe (5th gen, GMT T1UC, 2021-2024 pre-facelift) front keychain - High Country trim.
# Reference: ref/front.jpg = crop (x 1200-2800, y 1100-2250) of Wikimedia Commons
# "Chevrolet Tahoe High Country GMTT1XX Avalon White Pearl (3).jpg" (Damian B Oh, CC BY-SA 4.0), see ref/SOURCE.txt.
# White car, nearly straight-on with a small yaw (the car's left side shows on the viewer's right), so the viewer's
# LEFT half (far side, its silhouette is the true body edge) is traced and mirrored; mirror check at x 785 is clean.
# The traced half is ~5 % narrower than the near half -> y_scale 0.95 restores the true face proportions.
# Scale: 1320 px = 80.5 mm (16.4 px/mm).
# NO LOGOS (user rule): the bowtie is NOT drawn; its spot is plain black grille + the plain white chrome bar. badge=None.
CX = 785

SPEC = dict(
    id='chevy_tahoe', name='Chevrolet Tahoe (2021-2024)',
    ref='kc/cars/chevy_tahoe/ref/front.jpg',
    units='px', px_left=2 * CX - 1445, px_right=1445, px_bottom=1000, center_x=CX, y_scale=0.95,
    outline_half=[(CX, 142), (600, 142), (420, 143), (335, 148), (290, 162), (248, 190), (212, 228), (186, 268),
                  (166, 312), (146, 362), (131, 420), (126, 480), (125, 600), (125, 800), (127, 860), (130, 950),
                  (142, 990), (200, 1000), (CX, 1002)],
    prims=[
        # ---- headlamp (top corner) + DRL housing below it + the big grille: one black band across the face
        dict(kind='poly', color='black', pts=[(174, 324), (260, 330), (356, 338), (CX, 336), (CX, 622), (450, 622),
                                              (372, 620), (342, 606), (322, 586), (316, 568), (300, 565),
                                              (178, 563), (160, 553), (154, 480), (156, 400), (163, 350)]),
        # ---- the full-width chrome bar = the DRL top light pipe continued across the grille (white)
        dict(kind='stroke', color='white', width=1.0, cap='flat', pts=[(140, 408), (CX, 408)]),
        # chrome bezel between headlamp and grille
        dict(kind='stroke', color='white', width=0.65, cap='flat', pts=[(355, 345), (355, 408)]),
        # DRL light pipe: inner vertical leg down the grille side, curling outward at the bottom ("]" shape)
        dict(kind='stroke', color='white', width=0.8, smooth=2,
             pts=[(290, 408), (292, 500), (284, 530), (262, 541), (172, 543)]),
        # ---- grille chrome bars (white), ends kept off the black frame
        dict(kind='stroke', color='white', width=0.6, cap='flat', pts=[(380, 367), (CX, 367)]),
        dict(kind='stroke', color='white', width=0.75, cap='flat', pts=[(338, 470), (CX, 470)]),
        dict(kind='stroke', color='white', width=0.75, cap='flat', pts=[(336, 512), (CX, 512)]),
        dict(kind='stroke', color='white', width=0.75, cap='flat', pts=[(338, 552), (CX, 552)]),
        dict(kind='stroke', color='white', width=0.75, cap='flat', pts=[(360, 592), (CX, 592)]),
        # ---- vertical air-curtain slot at the bumper corner
        dict(kind='poly', color='black', pts=[(148, 568), (180, 566), (182, 620), (180, 738), (162, 758), (148, 748)]),
        # ---- lower intake + valance/skid (black) with the chrome lip between them (white)
        dict(kind='poly', color='black', pts=[(CX, 783), (380, 784), (345, 795), (314, 818), (296, 846), (100, 846),
                                              (100, 1030), (CX, 1030)]),
        dict(kind='stroke', color='white', width=0.9, smooth=2, pts=[(296, 852), (330, 858), (500, 861), (CX, 862)]),
        dict(kind='poly', color='relief', pts=[(CX, 795), (372, 795), (372, 842), (CX, 842)],
             relief=dict(type='hbars', pitch=2.0, rib=0.9)),
        # parking sensor
        dict(kind='ring', color='black', c=(550, 725), r_mm=1.0, width=0.5),
        # ---- engraved lines: hood front fold, hood/fender shut line
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(335, 175), (400, 212), (490, 238), (CX, 242)]),
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(318, 160), (270, 192), (225, 240), (196, 290),
                                                                      (182, 320)]),
        # lower bumper step: from the air-curtain foot to the intake corner
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(170, 772), (225, 800), (282, 830)]),
    ],
    badge=None,
    tab=dict(y_frac=0.5),
)
