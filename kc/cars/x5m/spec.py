# BMW X5 M Competition (F95 LCI, 2024+) - traced on the BMW press photo (Isle of Man Green, studio front view).
# Left half traced (viewer's left), mirrored about x=960. NO LOGOS (user rule): no roundel, no grille badge.
# Revision 1: sparse lower-intake bars (no waffle), no chrome bar, no LED dashes, angular kidneys with 4 slim slats,
# straight power-dome creases, thicker/longer-upper-leg DRL chevrons, hexagon closes on the intake edge, splitter step fillet.
SPEC = dict(
    id='x5m', name='BMW X5 M Competition (F95 LCI)',
    ref='kc/cars/x5m/ref/front.jpg',
    units='px', px_left=345, px_right=1575, center_x=960, px_bottom=1140,
    outline_half=[(960, 517), (700, 518), (556, 520), (505, 532), (462, 550), (425, 575), (395, 607), (375, 640),
                  (362, 672), (352, 710), (347, 760), (345, 840), (345, 940), (348, 1010), (356, 1055), (370, 1085),
                  (392, 1102), (420, 1107), (566, 1106), (578, 1128), (600, 1138), (620, 1140), (960, 1140)],
    prims=[
        # ---- headlight unit (black) - slim LCI lens with pointed inner end
        dict(kind='poly', color='black', smooth=1, pts=[(378, 692), (383, 664), (395, 649), (445, 648), (500, 656), (555, 671),
             (605, 684), (636, 692), (628, 704), (604, 735), (588, 743), (500, 744), (420, 741), (394, 732), (380, 715)]),
        # ---- DRL: two outward-pointing arrow chevrons (white, ~0.95 mm), longer upper leg, vertex ~55% down the lens
        dict(kind='stroke', color='white', width=1.1, cap='flat', pts=[(428, 662), (402, 700), (418, 723)]),
        dict(kind='stroke', color='white', width=1.1, cap='flat', pts=[(524, 682), (499, 712), (512, 727)]),
        # ---- grille frame + central lower intake: one black X-shaped mass (flush black)
        dict(kind='poly', color='black', pts=[(960, 698), (948, 690), (935, 676), (915, 664), (860, 659), (760, 659), (712, 661),
             (686, 671), (662, 694), (643, 730), (633, 770), (637, 792), (690, 888), (562, 1046), (558, 1060), (612, 1110),
             (960, 1110)]),
        # ---- splitter / lower apron (black)
        dict(kind='poly', color='black', pts=[(960, 1100), (562, 1100), (578, 1150), (960, 1150)]),
        # ---- kidney openings: angular octagon, recessed, 4 slim horizontal slats (photo y ~712/747/788/822)
        dict(kind='poly', color='relief', pts=[(940, 700), (926, 683), (720, 681), (690, 693), (664, 740), (661, 795),
             (672, 812), (735, 860), (940, 860)],
             relief=dict(type='hbars', pitch=2.4, rib=0.75, offset=1.55)),
        # ---- lower centre intake: open recess (no ribs) ...
        dict(kind='poly', color='relief', pts=[(960, 903), (703, 903), (592, 1046), (590, 1058), (628, 1093), (960, 1093)],
             relief=dict(type='none')),
        # ... with sparse flush bars like the real car: one full-width bar under the plate zone, one lower bar, 2 struts/side
        dict(kind='stroke', color='white', width=0.9, cap='flat', pts=[(640, 972), (960, 972)]),
        dict(kind='stroke', color='black', width=0.9, cap='flat', pts=[(640, 972), (960, 972)]),
        dict(kind='stroke', color='white', width=0.9, cap='flat', pts=[(590, 1035), (872, 1035)]),
        dict(kind='stroke', color='black', width=0.9, cap='flat', pts=[(590, 1035), (872, 1035)]),
        dict(kind='stroke', color='white', width=0.9, cap='flat', pts=[(668, 972), (668, 1100)]),
        dict(kind='stroke', color='black', width=0.9, cap='flat', pts=[(668, 972), (668, 1100)]),
        dict(kind='stroke', color='white', width=0.9, cap='flat', pts=[(752, 972), (752, 1100)]),
        dict(kind='stroke', color='black', width=0.9, cap='flat', pts=[(752, 972), (752, 1100)]),
        # radar sensor hexagon (flush black, sharp corners, closes on the intake bottom edge)
        dict(kind='poly', color='white', pts=[(960, 990), (896, 990), (870, 1013), (863, 1040), (870, 1067), (896, 1093), (960, 1093)]),
        dict(kind='poly', color='black', pts=[(960, 990), (896, 990), (870, 1013), (863, 1040), (870, 1067), (896, 1093), (960, 1093)]),
        # ---- outer intakes (black): huge vertical zig-zag openings
        dict(kind='poly', color='black', pts=[(372, 812), (385, 803), (603, 875), (612, 887), (482, 1036), (468, 1042),
             (382, 1040), (372, 1030)]),
        # opening below the gloss-black flap: recessed (no ribs) so the flap stands proud
        dict(kind='poly', color='relief', pts=[(380, 838), (535, 905), (548, 912), (472, 1028), (382, 1030)],
             relief=dict(type='none')),
        # ---- hood: fender shut lines + straight power-dome creases converging on the kidney frame corners (grooves)
        dict(kind='stroke', color='groove', width=0.62, smooth=2, pts=[(488, 556), (464, 585), (453, 612), (450, 632)]),
        dict(kind='stroke', color='groove', width=0.62, pts=[(648, 534), (668, 582), (686, 627), (694, 644)]),
    ],
    badge=None,
    tab=dict(y_frac=0.58),
)
