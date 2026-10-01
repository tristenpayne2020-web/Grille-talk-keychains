# Ram 1500 TRX (DT, 2021+) front keychain
# Reference: ref/front.jpg = official FCA/Stellantis press photo (2021 Ram 1500 TRX Launch Edition), via caricos.com
# (see ref/SOURCE.txt). Straight-on, level. Traced half = viewer's LEFT, centreline x = 1284 px.
# NO LOGOS (user rule): the RAM grille lettering is NOT drawn, the grille is plain hex mesh. badge=None.
# Revision 1: square LED blocks instead of round rings, reshaped 0.8 mm DRL, sharper 0.9 mm grille frame that encloses
# the lower slot, black fender-flare ends, inset hex relief (black rim), simpler fog lamps, closed skid pads.
CX = 1284
HEX = dict(type='hex', pitch=2.2, rib=0.65)
PXMM = (2 * CX - 2 * 722) / 80.5                       # photo px per keychain mm

from shapely.geometry import Polygon as _Poly, LineString as _Line


def _full(half):
    """Close a viewer's-left half path (starting and ending on CX) into a symmetric polygon."""
    return _Poly(list(half) + [(2 * CX - x, y) for x, y in reversed(half)])


FRAME = [(CX, 630), (955, 630), (935, 672), (926, 712), (927, 745), (943, 770), (974, 787), (1035, 797), (CX, 801)]
BAR = [(1040, 793), (1078, 777), (1108, 755), (1138, 745), (CX, 741)]
_bar = _Line(BAR + [(2 * CX - x, y) for x, y in reversed(BAR[:-1])])
# grille relief = inside of the frame line, minus the cross bar, with a 0.75 mm solid black rim along every white edge
_grille = _full(FRAME).buffer(-(0.45 + 0.75) * PXMM).difference(_bar.buffer((0.75 + 0.75) * PXMM))
GRILLE_RELIEF = [list(g.exterior.coords) for g in getattr(_grille, 'geoms', [_grille]) if g.area > 50]

SPEC = dict(
    id='ram_trx', name='Ram 1500 TRX (2021+)',
    ref='kc/cars/ram_trx/ref/front.jpg',
    units='px', px_left=722, px_right=2 * CX - 722, px_bottom=1059, center_x=CX,
    outline_half=[(CX, 481), (1092, 481), (1080, 488), (1072, 496), (884, 497), (866, 510), (852, 536), (828, 552),
                  (800, 566), (774, 582), (752, 602), (737, 624), (727, 648), (722, 675), (721, 760), (733, 880), (740, 930), (754, 958), (788, 984), (848, 1004), (904, 1017), (914, 1030),
                  (919, 1046), (934, 1057), (970, 1059), (CX, 1059)],
    prims=[
        # ---- black face: hood-front header + headlight units + grille surround + lower bumper (all black on the TRX)
        dict(kind='poly', color='black', pts=[(CX, 582), (1100, 584), (1000, 590), (960, 597), (900, 604), (850, 607),
                                              (800, 612), (776, 618), (765, 628), (762, 640), (762, 816), (650, 816),
                                              (650, 1100), (CX, 1100)]),
        # red lower fascia corners under the headlights -> body (white), running into the grille frame
        dict(kind='poly', color='white', pts=[(762, 726), (800, 731), (860, 739), (896, 749), (912, 762), (930, 790),
                                              (948, 812), (945, 816), (740, 816), (740, 726)]),
        # black fender-flare ends: the wide-body flare runs down the side into the black bumper
        dict(kind='poly', color='black', pts=[(700, 752), (726, 754), (742, 772), (748, 816), (700, 816)]),
        # ---- headlight: C-shaped LED DRL (top bar, outer side, lower bar with the upward kick) + two square LED blocks
        dict(kind='stroke', color='white', width=0.8, pts=[(925, 646), (905, 642), (797, 642), (791, 650), (791, 694),
                                                            (797, 700), (880, 701), (895, 688)]),
        dict(kind='poly', color='white', smooth=1, pts=[(825, 660), (849, 660), (849, 677), (825, 677)]),
        dict(kind='poly', color='white', smooth=1, pts=[(870, 660), (894, 660), (894, 677), (870, 677)]),
        # ---- grille: one recess inside the frame (upper mesh + lower slot), hex relief inset to leave a black rim
        dict(kind='poly', color='black', pts=[(CX, 628), (955, 628), (933, 672), (923, 712), (924, 746), (940, 772),
                                              (972, 790), (1035, 800), (CX, 804)]),
        # grille frame (the chamfered TRX grille outline, white line) enclosing the lower slot + the thick cross bar
        dict(kind='stroke', color='white', width=0.9, pts=FRAME),
        dict(kind='stroke', color='white', width=1.5, pts=BAR),
        dict(kind='poly', color='white', pts=[(1030, 798), (1094, 799), (1078, 778), (1040, 790)]),   # bar-to-frame gusset
    ] + [dict(kind='poly', color='relief', pts=r, mirror=False, relief=HEX) for r in GRILLE_RELIEF] + [
        # ---- bumper: lower grille mesh, fog lamp lens, skid plate with tow hooks
        dict(kind='poly', color='relief', pts=[(CX, 893), (990, 893), (978, 900), (975, 915), (980, 930), (990, 936),
                                                 (CX, 936)], relief=HEX),
        dict(kind='poly', color='white', smooth=1, pts=[(803, 881), (858, 881), (864, 891), (858, 901), (803, 901),
                                                         (797, 891)]),
        dict(kind='poly', color='white', pts=[(CX, 937), (1000, 937), (960, 939), (935, 949), (921, 966), (917, 1000),
                                              (912, 1030), (905, 1070), (CX, 1070)]),
        dict(kind='poly', color='black', smooth=2, pts=[(973, 955), (1045, 958), (1053, 975), (1048, 995), (1030, 1013),
                                                         (990, 1020), (955, 1010), (943, 985), (950, 964)]),
        dict(kind='stroke', color='white', width=0.8, pts=[(963, 984), (1030, 990)]),
        # skid plate pads (engraved closed rounded outlines)
        dict(kind='stroke', color='groove', width=0.65, smooth=1, pts=[(1112, 982), (1195, 982), (1205, 994), (1205, 1030),
                                                                       (1195, 1040), (1112, 1040), (1102, 1030),
                                                                       (1102, 994), (1112, 982)]),
        dict(kind='stroke', color='groove', width=0.65, smooth=1, pts=[(CX + 4, 982), (1249, 982), (1239, 994), (1239, 1030),
                                                                       (1249, 1040), (CX + 4, 1040)]),
        # ---- hood: scoop opening with the three amber marker lights, cowl heat extractors
        dict(kind='poly', color='black', smooth=1, pts=[(1360, 502), (1160, 502), (1140, 506), (1132, 516), (1137, 535),
                                                         (1155, 550), (1185, 557), (1360, 559)]),
        dict(kind='stroke', color='white', width=0.9, pts=[(1188, 518), (1218, 518)]),
        dict(kind='stroke', color='white', width=0.9, pts=[(1269, 518), (1299, 518)], mirror=False),
        dict(kind='poly', color='black', smooth=1, pts=[(1078, 485), (1070, 500), (1062, 516), (1042, 525), (960, 526), (918, 518),
                                                        (896, 503), (886, 485)]),
        # hood / fender shut line (engraved), ends in white well before the black header
        dict(kind='stroke', color='groove', width=0.65, pts=[(846, 554), (838, 572), (842, 594)]),
    ],
    badge=None,
    tab=dict(y_frac=0.68),
)
