# Chevrolet Corvette C5 (1997-2004) - front keychain artwork, pop-up headlights CLOSED.
# Reference: ref/front.jpg (= ref/cs_silver.jpg), silver C5 convertible, straight-on, level, centred (axis x=521),
# from the CorvSport.com 2000 C5 image gallery (user-submitted photo, reference use only; see ref/SOURCE.txt).
# ref/cs_red.jpg (red C5, same gallery) confirms the fine square mesh in the intakes / brake ducts.
# NO LOGOS (user rule): the crossed-flags emblem on the nose and the plate/CORVETTE panel lettering are left out.
#
# Design (G80 language):
#   black : short outboard parking/turn lamp housings, the long main intakes (fine mesh relief) with the round fog
#           lamp at their outer end, the lower brake-duct slots, the black chin spoiler under the bumper
#   white : parking/turn lamp lens (stubby rounded oblong inside the black housing), fog lamp as a white ring
#   groove: closed pop-up headlight lids (the signature smooth C5 nose), clamshell hood shut line across the nose,
#           hood side shut lines up towards the cowl, the rounded bumper pocket in the centre (plain, no plate/lettering)
#   tab   : viewer's left, on the white front fender (~55 % height)
INTAKE = [(264, 584), (300, 585), (350, 589), (400, 595), (425, 602), (435, 615), (430, 630), (410, 637), (350, 633),
          (300, 624), (272, 614), (263, 600)]

SPEC = dict(
    id='c5_corvette', name='Chevrolet Corvette C5',
    ref='kc/cars/c5_corvette/ref/front.jpg',
    units='px', px_left=167, px_right=875, px_bottom=688, center_x=521,
    outline_half=[(521, 371), (420, 371), (330, 371), (292, 369), (266, 370), (250, 378), (225, 390), (202, 406),
                  (185, 426), (175, 450), (169, 480), (167, 520), (168, 565), (171, 605), (176, 635), (184, 656),
                  (196, 672), (214, 684), (300, 687), (400, 688), (521, 688)],
    outline_smooth=2,
    prims=[
        # black chin spoiler below the bumper (blunt outer ends, a touch deeper at the centre)
        dict(kind='poly', color='black', pts=[(521, 668), (420, 667), (320, 665), (240, 663), (205, 661),
                                              (190, 660), (172, 662), (194, 682), (212, 694), (521, 696)]),
        # parking / turn lamp: short black housing + stubby white lens
        dict(kind='poly', color='black', smooth=2, pts=[(175, 566), (205, 564), (238, 569), (253, 580), (254, 598),
                                                         (244, 609), (210, 608), (184, 602), (174, 586)]),
        dict(kind='poly', color='white', smooth=2, pts=[(188, 575), (220, 574), (236, 578), (242, 588), (239, 598),
                                                         (214, 599), (194, 596), (186, 586)]),
        # main intake (fine slats following the intake's slope) + round fog lamp at its outer end.
        # Painted per side (mirror=False) so each side's slats can lean with its own intake and stay mirror-symmetric.
        *[dict(kind='poly', color='black', smooth=2, mirror=False,
               pts=[(521 + sx * (x - 521), y) for x, y in INTAKE],
               relief=dict(type='hbars', pitch=1.5, rib=0.75, margin=0.4, offset=0.5, angle=-5.5 * sx))
          for sx in (1, -1)],
        dict(kind='ring', color='white', c=(296, 602), r_mm=1.2, width=0.6),
        # lower brake-duct slot
        dict(kind='poly', color='black', smooth=2, pts=[(206, 630), (250, 632), (280, 635), (288, 644), (281, 654),
                                                         (240, 655), (214, 653), (203, 642)]),
        # closed pop-up headlight lid
        dict(kind='stroke', color='groove', width=0.65, smooth=2,
             pts=[(212, 436), (265, 434), (316, 437), (324, 446), (325, 484), (317, 494), (262, 496), (212, 493),
                  (204, 484), (204, 445), (212, 436)]),
        # hood front shut line (leaves the lid's outboard side, runs across the nose)
        dict(kind='stroke', color='groove', width=0.65, smooth=1, pts=[(322, 482), (340, 488), (450, 496), (521, 499)]),
        # hood side shut line up towards the cowl (stops >1 mm inside the outline)
        dict(kind='stroke', color='groove', width=0.65, smooth=2, pts=[(230, 436), (231, 410), (238, 396)]),
        # rounded bumper pocket (plain)
        dict(kind='stroke', color='groove', width=0.65, smooth=2,
             pts=[(521, 571), (472, 572), (457, 578), (451, 597), (452, 622), (459, 636), (478, 642), (521, 643)]),
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
