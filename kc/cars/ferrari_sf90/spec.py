# Ferrari SF90 Stradale (2019+) front keychain - traced from a real straight-on photo.
# Reference: ref/p1.jpg = Pexels photo 12801137 "Front View of a Red Ferrari SF90 Stradale"
#   https://www.pexels.com/photo/front-view-of-a-red-ferrari-sf90-stradale-12801137/  (Pexels licence, free use)
#   downloaded at 2400x1600. Traced half = viewer's LEFT. Centreline x=1193 (checked with trace_tools mirror).
#
# Design (G80 language):
#  black    - the "C": slim headlight slit at the upper outer corner, wrapping round its outer end and running back
#             inboard as the slim vent slot under the lamp (one black C around the red blade); full-width lower
#             mouth; carbon splitter under the lip.
#  white on black - the LED signature: 0.7 mm stroke along the top of the lens, round the outer clear block and
#             back inboard (a small C inside the big C).
#  relief   - honeycomb mesh in the two side halves of the mouth (the real car's mesh); centre left plain black
#             (the open central diffuser/blade area).
#  grooves  - hood shut lines (cowl down to the lamps), hood front edge across the nose, and the diagonal hood
#             creases that form the sculpted central channel.
#  badge    - none (user rule: no logos); the nose stays plain body.
SPEC = dict(
    id='ferrari_sf90', name='Ferrari SF90 Stradale',
    ref='kc/cars/ferrari_sf90/ref/p1.jpg',
    units='px', px_left=132, px_right=2254, px_bottom=1393, center_x=1193,
    outline_half=[(1193, 604), (900, 602), (600, 596), (480, 590), (400, 586), (320, 576), (250, 590), (190, 618),
                  (155, 650), (140, 700), (133, 780), (130, 900), (129, 1020), (131, 1120), (137, 1200),
                  (147, 1262), (165, 1312), (200, 1350), (260, 1374), (500, 1385), (900, 1391), (1193, 1393)],
    outline_smooth=2,
    prims=[
        # carbon splitter under the red lip (full width)
        dict(kind='poly', color='black', pts=[(1250, 1376), (1000, 1367), (700, 1353), (420, 1334), (260, 1314),
                                              (175, 1292), (140, 1280), (120, 1420), (1250, 1420)]),
        # lower mouth (crosses the centreline -> unioned with its mirror)
        dict(kind='poly', color='black', smooth=1,
             pts=[(1250, 1158), (1050, 1152), (950, 1138), (800, 1120), (600, 1104), (400, 1094), (240, 1090),
                  (200, 1106), (178, 1150), (168, 1200), (164, 1238), (200, 1250), (300, 1264), (500, 1275),
                  (800, 1289), (955, 1298), (1005, 1328), (1045, 1350), (1250, 1352)]),
        # honeycomb mesh in the side part of the mouth
        dict(kind='poly', color='relief', pts=[(940, 1139), (800, 1122), (600, 1106), (400, 1096), (240, 1092),
                                               (200, 1108), (178, 1150), (168, 1200), (164, 1238), (200, 1250),
                                               (300, 1264), (500, 1275), (800, 1289), (970, 1299)],
             relief=dict(type='hex', pitch=2.6, rib=0.8, margin=0.9, min_w=0.8)),
        # headlight slit + outer wrap + vent slot under the lamp = the black "C"
        dict(kind='poly', color='black', smooth=1,
             pts=[(178, 778), (300, 796), (420, 829), (505, 847), (545, 864), (566, 895), (570, 918),
                  (522, 912), (420, 898), (300, 880), (308, 922), (325, 948),
                  (420, 985), (520, 1018), (585, 1040), (606, 1049), (606, 1068),
                  (560, 1063), (440, 1036), (320, 1013), (235, 992), (190, 966), (168, 912), (165, 840), (170, 785)]),
        # LED signature: along the lens top, round the outer clear block, back inboard
        dict(kind='stroke', color='white', width=0.8, smooth=2,
             pts=[(478, 870), (420, 857), (330, 834), (250, 816), (212, 819), (203, 860), (208, 922), (240, 945), (292, 953)]),
        # grooves: hood shut line (cowl -> lamp), hood front edge across the nose, diagonal hood crease
        dict(kind='stroke', color='groove', width=0.65, smooth=2,
             pts=[(398, 596), (399, 660), (405, 730), (414, 790), (424, 828)]),
        dict(kind='stroke', color='groove', width=0.65, smooth=1,
             pts=[(566, 878), (700, 887), (900, 898), (1050, 902), (1193, 903)]),
        dict(kind='stroke', color='groove', width=0.65, smooth=2,
             pts=[(600, 700), (700, 772), (790, 830), (850, 856)]),
        # parking sensor
        dict(kind='ring', color='black', c=(765, 1080), r_mm=0.95, width=0.5),
    ],
    badge=None,
    tab=dict(y_frac=0.47),
)
