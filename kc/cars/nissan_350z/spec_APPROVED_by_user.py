# Nissan 350Z (Z33, 2006-2009) front keychain.
# Reference: ref/front.jpg (see ref/SOURCE.txt). Straight-on, level, centreline x = 828 px. Traced half = viewer's LEFT.
# NO LOGOS (user rule): badge=None, the Nissan emblem spot on the nose is left as plain body.
#
# Design (G80 language): white = body paint (the long plain Z33 nose stays white - that bare nose IS the car).
# Black = the tall swept-back headlamp units, the wide low mouth, the vertical bumper-corner ducts and the lip band.
# White on black = the projector bezel (C-arc, open towards the lamp's lower inner tip; the opening also keeps the lens
# tied to the lamp so no black island floats inside a white ring) and the two round fog lamps at the ends of the mouth bar.
# Relief = horizontal slats above and below a flush black centre bar in the mouth (stock Z33 slat grille; the
# photographed car has aftermarket mesh). Grooves = hood front shut line, the two hood-bulge creases and the
# hood/fender shut lines that run from the lamp tops up to the cowl (the fender peaks).
import math


def _arc(c, r, a0, a1, n=24):
    """points on a circle arc in photo px (angles in degrees, 0 = +x, counter-clockwise on screen)"""
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] - r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


SPEC = dict(
    id='nissan_350z', name='Nissan 350Z (Z33)',
    ref='kc/cars/nissan_350z/ref/front.jpg',
    units='px', px_left=95, px_right=1561, px_bottom=1047, center_x=828,
    # top = cowl (hood slightly lower in the middle so the fender peaks over the lamps stand up), convex fender shoulder
    outline_half=[(828, 356), (700, 355), (560, 352), (430, 348), (355, 346), (320, 348), (290, 355), (256, 376),
                  (218, 403), (182, 431), (150, 461), (124, 497), (104, 546), (97, 610), (95, 700), (95, 800),
                  (97, 880), (100, 935), (106, 968), (118, 992), (140, 1012), (220, 1028), (400, 1040),
                  (600, 1045), (828, 1047)],
    prims=[
        # headlight unit (whole lens, black)
        dict(kind='poly', color='black', smooth=1, pts=[(224, 450), (334, 451), (348, 472), (372, 548), (396, 626),
                                                        (400, 646), (378, 647), (262, 633), (201, 622), (193, 598),
                                                        (193, 522), (200, 482), (212, 458)]),
        # projector ring (white, 0.8 mm), near-full circle with a small flat-cut gap at the lower OUTER side
        # (the gap keeps the black lens inside the ring joined to the rest of the lamp)
        dict(kind='stroke', color='white', width=0.8, cap='flat', pts=_arc((282, 560), 44, 239, 571, n=40)),
        # lower mouth (black)
        dict(kind='poly', color='black', pts=[(870, 800), (432, 800), (414, 805), (406, 818), (404, 950),
                                              (410, 968), (430, 977), (870, 980)]),
        # slats above / below the bar; they start 0.8 mm clear of the fog lamp so each lamp sits on a flat black pad
        dict(kind='poly', color='relief', pts=[(870, 790), (492, 790), (492, 889), (870, 889)],
             relief=dict(type='hbars', pitch=1.8, rib=1.0, offset=0.9)),
        dict(kind='poly', color='relief', pts=[(870, 889), (492, 889), (492, 990), (870, 990)],
             relief=dict(type='hbars', pitch=1.8, rib=1.0, offset=0.9)),
        # the Z33 horizontal mouth bar (body colour) running between the two fog lamps
        dict(kind='stroke', color='white', width=1.1, cap='flat', pts=[(468, 889), (828, 889)]),
        # round fog lamps at the ends of the bar: white ring with a black lamp centre
        dict(kind='ring', color='white', c=(447, 889), r_mm=1.6, width=1.0),
        # vertical side ducts in the bumper corners
        dict(kind='poly', color='black', pts=[(192, 742), (220, 746), (256, 932), (222, 934)]),
        # lower lip (about the same thickness across the whole width)
        dict(kind='poly', color='black', pts=[(104, 972), (180, 988), (300, 993), (450, 998), (828, 1003),
                                              (828, 1060), (80, 1060)]),
        # engraved: hood front shut line, fender shut lines (lamp top -> cowl), hood bulge creases,
        # bumper/fender split line from the lamp's lower outer corner down to the side duct
        dict(kind='stroke', color='groove', width=0.65, smooth=2, pts=[(402, 588), (600, 596), (828, 598)]),
        dict(kind='stroke', color='groove', width=0.65, smooth=1, pts=[(282, 449), (292, 410), (310, 376), (336, 350)]),
        dict(kind='stroke', color='groove', width=0.65, smooth=1, pts=[(668, 372), (676, 470), (694, 588)]),
        dict(kind='stroke', color='groove', width=0.65, smooth=1, pts=[(204, 629), (214, 686), (208, 744)]),
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
