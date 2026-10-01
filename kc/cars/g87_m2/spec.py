# BMW M2 (G87, 2023+) front keychain - traced on a straight-on photo of a Sao Paulo Yellow M2 in BMW Welt.
# Reference: "Front vom BMW M2 Coupe in der BMW Welt Bild 2 2024-08-03.jpg" by Strubbl, Wikimedia Commons, CC BY-SA 4.0
# (1920 px copy, shadows brightened for tracing). Traced half = viewer's left (car's right). Centreline x = 937.
# Perspective correction: the photo was shot from eye level, so the (nearly horizontal) hood and fender tops look
# much taller than in the user's G80 photo (camera near bonnet height). Everything above the headlight tips
# (y < Y0) is compressed toward Y0 by F (see ref/make_warped.py, which applies the same mapping to the photo used
# for overlay.png). Coordinates below are the ORIGINAL photo pixels; _c() maps them.
from shapely.geometry import LineString

CX, YB, S = 937, 1075, 80.5 / (1583 - 291)          # same px -> mm mapping the pipeline uses
Y0, F = 515.0, 0.62                                 # hood / fender-top foreshortening (see header)


def _c(pts):
    return [(x, y if y >= Y0 else Y0 - (Y0 - y) * F) for x, y in pts]


# outline: cowl -> fender -> bumper side -> lip. The lip's lower edge is lost in the black floor shadow of the photo;
# it is placed ~0.4 mm below the visible lip reflection (a second, well-lit photo shows a thick carbon lip), and the
# total height is kept <= 40.8 mm so 12 keychains fit on one K2 plate next to the prime tower.
OUTLINE = _c([(937, 368), (760, 369), (640, 373), (590, 379), (560, 392), (525, 410), (490, 432), (455, 455),
              (420, 474), (385, 492), (358, 510), (338, 530), (322, 555), (312, 585), (305, 620), (299, 660),
              (294, 700), (292, 760), (291, 830), (291, 900), (292, 955), (296, 985), (304, 1004), (318, 1022),
              (345, 1036), (400, 1047), (450, 1055), (600, 1066), (800, 1073), (937, 1075)])


def _hood_side_line(d=22.0):
    """hood/fender shut line: runs parallel to the fender silhouette d px inside it, from the headlight tip up to
    the cowl, then turns up and leaves through the top edge (steep exit, no thin white sliver)"""
    sil = LineString(_c([(385, 492), (420, 474), (455, 455), (490, 432), (525, 410), (560, 392)]))
    a, b = sil.offset_curve(d), sil.offset_curve(-d)
    inner = a if a.centroid.y > b.centroid.y else b          # image y grows downward -> inside = larger y
    pts = list(inner.coords)
    if pts[0][0] > pts[-1][0]:
        pts = pts[::-1]
    top = Y0 - (Y0 - 379) * F                                # top edge height near the cowl corner
    return [(388, 522)] + pts + [(pts[-1][0] + 26, top + 9), (pts[-1][0] + 36, top - 12)]


SPEC = dict(
    id='g87_m2', name='BMW M2 (G87)',
    ref='kc/cars/g87_m2/ref/front_warped.png',
    units='px', px_left=291, px_right=1583, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=[
        # hood outline (engraved): front shut line + side shut lines up to the cowl (drawn first, headlight covers ends)
        dict(kind='stroke', color='groove', width=0.62, pts=[(455, 562), (937, 562)]),
        dict(kind='stroke', color='groove', width=0.62, smooth=2, pts=_hood_side_line()),
        # headlight unit (black)
        dict(kind='poly', color='black', pts=[(388, 515), (420, 535), (455, 558), (490, 582), (512, 600), (522, 615),
                                              (524, 650), (522, 700), (500, 700), (470, 693), (430, 683), (390, 670),
                                              (360, 660), (340, 648), (328, 628), (325, 600), (329, 575), (340, 553),
                                              (358, 535), (375, 522)]),
        # DRL: outer vertical light + lower light with the upward step (hockey stick)
        dict(kind='stroke', color='white', width=0.75, smooth=2,
             pts=[(357, 563), (355, 600), (358, 630), (368, 644), (386, 649), (430, 649), (460, 631), (478, 623), (504, 622)]),
        # kidney grille (left kidney), frameless, horizontal slats
        dict(kind='poly', color='black', smooth=1,
             pts=[(600, 640), (885, 640), (906, 644), (912, 660), (912, 782), (906, 796), (660, 797), (630, 787),
                  (600, 768), (578, 747), (570, 725), (570, 662), (578, 647)],
             relief=dict(type='hbars', pitch=2.3, rib=1.1, offset=1.15)),
        # outer lower intake (big box)
        dict(kind='poly', color='black', pts=[(309, 802), (360, 815), (420, 835), (462, 852), (484, 864), (493, 880),
                                              (495, 995), (489, 1010), (440, 1003), (385, 990), (342, 976), (320, 963),
                                              (310, 948)]),
        # centre lower intake, sits directly on the splitter. Behind the (dropped) display plate and its V-shaped
        # holder legs the photo shows a radiator with horizontal fins -> regular horizontal slats matching the kidneys
        # (5 slats, offset centres them between the sloping lip top (2.43 mm at the sides) and the pocket top, so no
        # clipped wedge rib forms along the lip; ribs meet the side walls like the G80 kidneys; ~45 % rib coverage)
        dict(kind='poly', color='black', pts=[(550, 1036), (550, 862), (555, 851), (566, 847), (960, 847), (960, 1047),
                                              (700, 1042)],
             relief=dict(type='hbars', pitch=2.3, rib=1.1, offset=0.34)),
        # splitter lip
        dict(kind='poly', color='black', pts=[(285, 985), (330, 1008), (400, 1020), (480, 1030), (550, 1036), (700, 1042),
                                              (960, 1047), (960, 1100), (280, 1100)]),
        # tow-hook cover
        dict(kind='ring', color='black', c=(592, 815), r_mm=1.1, width=0.5, mirror=False),   # BMW: single tow-hook cover, viewer's left
    ],
    badge=dict(type='roundel', c=(937, 603), d=3.4),
    tab=dict(y_frac=0.52),
)
