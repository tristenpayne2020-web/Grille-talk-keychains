# Cadillac Escalade (5th gen, GMT T1XX, 2021-2024 pre-facelift) front keychain.
# Reference: Wikimedia Commons "Cadillac Escalade Sport Platinum GMTT1UL Black Raven (14).jpg" (Damian B Oh,
# CC BY-SA 4.0), downloaded as the 3840 px Commons file and resized to 2000x1500 (ref/front.jpg). Dead-on front,
# level, mirror check passes at centre_x 1004. The car is black, so the colour semantics (what is body paint and what
# is black trim) were read from a white Escalade Sport: "Cadillac Escalade (GMTT1XX) IMG 0799.jpg" (Alexander-93,
# CC BY-SA 4.0, ref/img0799.jpg).
# NO LOGOS (user rule): no crest, no lettering; the grille mesh simply runs through the badge spot. badge=None.
CX = 1004

SPEC = dict(
    id='escalade', name='Cadillac Escalade (2021+)',
    ref='kc/cars/escalade/ref/front.jpg',
    units='px', px_left=2 * CX - 1758, px_right=1758, px_bottom=1338, center_x=CX,
    outline_half=[(CX, 456), (800, 456), (600, 457), (500, 459), (462, 464), (420, 474), (385, 500), (366, 527),
                  (345, 553), (325, 582), (309, 612), (297, 642), (287, 672), (277, 710), (268, 765), (259, 830),
                  (252, 900), (249, 1000), (249, 1100), (251, 1180), (255, 1240), (275, 1285), (295, 1310),
                  (318, 1325), (400, 1334), (600, 1337), (CX, 1338)],
    prims=[
        # slim horizontal headlight (black) joined to the thick black grille surround
        # (inner end stepped: a white gap separates the lamp from the grille surround below the top bar)
        dict(kind='poly', color='black', pts=[(320, 658), (400, 660), (505, 666), (514, 672), (514, 750),
                                              (470, 763), (330, 770), (318, 760), (309, 735), (309, 690)]),
        # headlight DRL: vertical light pipe at the outer end + thin line along the lens bottom (white L)
        dict(kind='stroke', color='white', width=0.7, pts=[(331, 678), (332, 738), (346, 748), (470, 743), (494, 737)]),
        # shield grille: wide top, sides tapering inward, shallow V at the bottom centre; diamond mesh relief
        dict(kind='poly', color='black', pts=[(CX, 660), (700, 660), (527, 664), (535, 770), (590, 1000),
                                              (800, 1018), (CX, 1036)],
             relief=dict(type='diamond', pitch=2.2, rib=0.75, margin=1.0, offset=0.2)),
        # thick black bar above the grille (hood front trim), notched down at its ends into the headlights
        dict(kind='poly', color='black', pts=[(CX, 645), (700, 645), (505, 648), (485, 662), (540, 682), (CX, 682)]),
        # vertical LED light blade (black housing + white light strip) at the bumper corner - THE Escalade signature
        dict(kind='poly', color='black', pts=[(288, 828), (322, 836), (348, 1178), (342, 1198), (296, 1196),
                                              (284, 1150)]),
        # tapered white light: slim at the top, widening toward the bottom (fills most of the housing)
        dict(kind='poly', color='white', pts=[(300, 850), (311, 850), (335, 1176), (309, 1176)]),
        # black trim band across the bumper (three horizontal slats) running inward from the blade foot
        dict(kind='poly', color='black', pts=[(340, 1130), (CX, 1130), (CX, 1196), (340, 1196)],
             relief=dict(type='hbars', pitch=1.8, rib=0.9, margin=0.0)),
        dict(kind='poly', color='black', pts=[(300, 1190), (600, 1190), (560, 1200), (470, 1214), (330, 1220)]),
        # lower valance: black from under the white lower wing to the bottom edge
        dict(kind='poly', color='black', pts=[(CX, 1250), (600, 1250), (558, 1298), (330, 1258), (262, 1250),
                                              (240, 1300), (300, 1360), (CX, 1360)]),
        dict(kind='poly', color='relief', pts=[(CX, 1262), (770, 1262), (760, 1312), (CX, 1312)],
             relief=dict(type='hbars', pitch=2.2, rib=1.0)),
        # engraved: hood / fender shut line, hood front edge, bumper crease under the grille
        dict(kind='stroke', color='groove', width=0.62, pts=[(405, 512), (374, 543), (360, 600), (362, 652)]),
        dict(kind='stroke', color='groove', width=0.62, pts=[(380, 533), (480, 530), (598, 526), (622, 508), (CX, 503)]),
        dict(kind='stroke', color='groove', width=0.62, pts=[(620, 1042), (800, 1052), (CX, 1062)]),
        # parking sensors
        # recess crease under the headlight, running down to the grille surround
        dict(kind='stroke', color='groove', width=0.62, pts=[(345, 792), (374, 880), (420, 972), (585, 996)]),
        # parking sensors (outer pair only; the inner pair crowded the bumper)
        dict(kind='ring', color='black', c=(425, 1078), r_mm=1.1, width=0.55),
    ],
    badge=None,
    tab=dict(y_frac=0.6),
)
