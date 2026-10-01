# Chevrolet Corvette C6 (2005-2013) - front keychain artwork (Z06 front).
# Reference: ref/front_raw.jpg = "2007 Chevrolet Corvette Z06 front view" (GM studio press photo, Velocity Yellow/orange),
# Flickr photo 6912329178 by "zorly" (https://www.flickr.com/photos/zorly/6912329178/), 2048x1365, licence: All Rights
# Reserved (used only as a private tracing reference, see ref/SOURCE.txt). Camera dead centre on the car, headlight
# height, level: mirror symmetric about x = 1024 (checked with trace_tools mirror), so no levelling/warp is needed.
#
# Design (G80 language), NO LOGOS (badge=None, the crossed-flags spot on the nose is plain body):
#   black : whole teardrop headlight lenses (exposed, non pop-up C6 lamps), wide low mouth grille (incl. the shadowed
#           outer pockets), Z06 hood-front air scoop, fog lamps, splitter/lip
#   white : the three round lamp elements inside each lens as rings (outer big turn/high-beam reflector + two projector
#           lenses) - the C6 light signature - plus the ribbed park-lamp band along the lens bottom as a 0.62 mm stroke
#   relief: grille = diagonal wire mesh ('diamond', like the real Z06 mesh)
#   groove: hood shut line (fender seams from the cowl down to the headlight tips + hood front edge across the nose)
#           and the sharp central nose crease from below the (omitted) emblem down to the grille
#   tab   : viewer's left, 55 % height, on the white fender between headlight and fog lamp
C = 1024
GRILLE_PITCH = 1.8
GRILLE_OFF = 0.0


def _sym(half):
    """half outline from the top centre point outward and back to the bottom centre point -> full symmetric ring."""
    return list(half) + [(2 * C - x, y) for x, y in reversed(half[1:-1])]

SPEC = dict(
    id='c6_corvette', name='Chevrolet Corvette C6',
    ref='kc/cars/c6_corvette/ref/front_raw.jpg',
    units='px', px_left=184, px_right=2 * C - 184, px_bottom=1192, center_x=C,
    outline_half=[(C, 517), (800, 516), (600, 513), (480, 510), (420, 511), (370, 518), (330, 530), (295, 546),
                  (265, 568), (238, 592), (218, 620), (203, 652), (193, 700), (186, 760), (184, 805), (187, 860),
                  (192, 920), (197, 970), (202, 1020), (208, 1060), (215, 1085), (226, 1103), (242, 1136), (292, 1164),
                  (420, 1170), (600, 1186), (C, 1192)],
    outline_smooth=1,
    prims=[
        # teardrop headlight lens (black)
        dict(kind='poly', color='black', smooth=2, pts=[
            (267, 688), (272, 660), (284, 620), (304, 592), (328, 576), (360, 572), (400, 578), (440, 594),
            (480, 620), (520, 652), (556, 684), (574, 712), (572, 732), (556, 740), (500, 740), (440, 735),
            (380, 728), (320, 716), (280, 706)]),
        # round lamp elements (white rings with dark centres): turn/high-beam reflector + 2 projectors
        dict(kind='ring', color='white', c=(330, 634), r_mm=1.6, width=0.6),
        dict(kind='ring', color='white', c=(408, 662), r_mm=1.25, width=0.5),
        dict(kind='ring', color='white', c=(486, 672), r_mm=1.25, width=0.5),
        # park-lamp band along the lens bottom
        dict(kind='stroke', color='white', width=0.64, smooth=1, pts=[(338, 699), (372, 706), (430, 712), (464, 714)]),
        # Z06 hood-front air scoop (black, flush)
        dict(kind='poly', color='black', pts=[(888, 683), (C + 30, 681), (C + 30, 713), (938, 714), (914, 707), (898, 696)]),
        # mouth grille with the wire mesh: ONE symmetric polygon (mirror=False) so the mesh is generated once, centred
        dict(kind='poly', color='black', smooth=1, mirror=False, pts=_sym([(C, 950), (760, 950), (480, 948), (466, 960),
                                                                         (478, 990), (520, 1030), (575, 1058), (650, 1068), (C, 1078)]),
             relief=dict(type='diamond', pitch=GRILLE_PITCH, rib=0.7, offset=GRILLE_OFF)),
        # the three bright vertical mesh dividers (C6/Z06 cue)
        dict(kind='stroke', color='white', width=0.66, cap='flat', mirror=False, pts=[(C, 945), (C, 1085)]),
        dict(kind='stroke', color='white', width=0.66, cap='flat', pts=[(735, 945), (737, 1075)]),
        # fog lamp
        dict(kind='poly', color='black', smooth=2, pts=[(262, 935), (300, 937), (382, 945), (392, 953), (395, 1012),
                                                        (386, 1022), (300, 1014), (260, 1007), (253, 998), (253, 944)]),
        # splitter / lip
        dict(kind='poly', color='black', pts=[(C, 1146), (800, 1140), (600, 1128), (400, 1123), (300, 1115),
                                              (250, 1108), (200, 1092), (205, 1150), (280, 1215), (C, 1215)]),
        # hood shut line + fender seams (engraved); the hood front edge stops where the bulge edges cross it, so no
        # groove runs right above the recessed scoop
        dict(kind='stroke', color='groove', width=0.62, smooth=1,
             pts=[(492, 518), (540, 560), (578, 606), (602, 645), (618, 663), (700, 664), (842, 664)]),
        # sharp-hood bulge edges: from the cowl, across the shut line, down the beak to the nose point (one clean 'V')
        dict(kind='stroke', color='groove', width=0.62,
             pts=[(772, 522), (842, 664), (940, 760), (C, 792)]),
        # central nose crease from the V point down to the grille: V + crease form one continuous 'Y'
        dict(kind='stroke', color='groove', width=0.62, mirror=False, pts=[(C, 792), (C, 950)]),
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
