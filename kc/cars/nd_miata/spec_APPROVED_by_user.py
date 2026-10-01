# Mazda MX-5 Miata (ND, 2016+) - traced on a straight-on front photo (viewer's LEFT half, mirrored).
# Reference: Wikimedia Commons, "2015 Mazda MX-5 ND 2.0 SKYACTIV-G 160 i-ELOOP Rubinrot-Metallic Frontalansicht
# LED-Scheinwerfer.jpg", CC BY-SA 4.0 (1920 px thumbnail).
# NO LOGOS (user rule): the Mazda wing badge spot above the mouth stays plain body. badge=None.
SPEC = dict(
    id='nd_miata', name='Mazda MX-5 Miata (ND)',
    ref='kc/cars/nd_miata/ref/front.jpg',
    units='px', px_left=482, px_right=1435, px_bottom=947, center_x=958.5,
    outline_half=[(958.5, 564), (850, 563), (740, 560), (650, 554), (608, 551), (588, 549), (572, 551), (556, 560),
                  (532, 577), (510, 600), (494, 627), (485, 658), (482, 700), (482, 800), (484, 858), (489, 889),
                  (498, 912), (511, 931), (528, 943), (600, 946), (760, 947), (958.5, 947)],
    outline_smooth=1,
    prims=[
        # headlight lens (black): slim squint, straight top edge, blunt angled outer end, inner tip
        dict(kind='poly', color='black', smooth=1, pts=[
            (537, 663), (552, 658), (580, 657), (600, 658), (636, 667), (677, 684), (711, 697), (723, 703),
            (712, 711), (690, 715), (660, 718), (636, 720), (600, 722), (575, 720), (557, 714), (546, 705),
            (539, 691)]),
        # projector ring + DRL light guide: one J from the ring's lower edge along the lens bottom to the tip
        dict(kind='ring', color='white', c=(609, 689), r_mm=1.7, width=0.8),
        dict(kind='stroke', color='white', width=0.8, smooth=2, pts=[
            (606, 709), (635, 708), (662, 705), (686, 701)]),
        # the smiling mouth (black): flat top, sharp outer-upper corners, flanks running down/in to a flat bottom
        dict(kind='poly', color='black', pts=[
            (958.5, 762), (806, 762), (740, 765), (700, 771), (679, 780), (681, 795), (687, 815),
            (696, 836), (707, 855), (721, 872), (740, 889), (765, 899), (800, 904), (850, 905), (958.5, 906)],
            relief=dict(type='hbars', pitch=2.6, rib=0.9, offset=1.3, margin=0.7)),
        # small slanted side intakes: narrow slits with parallel long sides and blunt ends
        dict(kind='poly', color='black', pts=[
            (537, 879), (588, 821), (607, 813), (604, 827), (557, 878)]),
        # black under-lip, deepest in the middle, tapering to the corners
        dict(kind='poly', color='black', pts=[
            (500, 918), (530, 925), (600, 927), (760, 926), (958.5, 925), (958.5, 960), (490, 960)]),
        # engraved lines: hood/fender split (fender peak down into the lamp), hood front shut line,
        # raised surround under the mouth (its lower flanks and bottom)
        dict(kind='stroke', color='groove', width=0.65, pts=[(576, 572), (578, 610), (583, 664)]),
        dict(kind='stroke', color='groove', width=0.65, smooth=2, pts=[
            (716, 700), (748, 684), (780, 673), (840, 666), (900, 663), (958.5, 662)]),
        dict(kind='stroke', color='groove', width=0.65, smooth=2, pts=[
            (668, 812), (676, 838), (692, 866), (714, 891), (745, 910), (800, 918), (958.5, 919)]),
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
