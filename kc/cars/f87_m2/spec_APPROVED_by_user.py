# BMW M2 Competition (F87, 2019-2021) front keychain.
# Traced on BMW Group PressClub photo P90299387 "The new BMW M2 Competition (04/2018)" (studio, straight-on front).
# ref/front.jpg = crop x640..2860, y1000..2080 of the 3508x2480 original. Left half traced (viewer's left), mirrored.
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union

PX_L, PX_R, PX_B, CX = 134, 2084, 975, 1109
S = 80.5 / (PX_R - PX_L)                        # mm per photo pixel


def mm_x(x):
    return (x - CX) * S


def mm_pt(p):
    return ((p[0] - CX) * S, (PX_B - p[1]) * S)


# left kidney (black surround + slats); inner edge kept 15 px off the centreline -> ~1.2 mm white bridge
KIDNEY = [(665, 400), (676, 386), (700, 376), (760, 369), (820, 366), (932, 368), (1000, 372), (1045, 378),
          (1072, 387), (1087, 400), (1094, 420), (1094, 560), (1089, 581), (1074, 594), (1050, 599), (932, 601),
          (810, 598), (775, 591), (750, 573), (726, 540), (706, 505), (688, 470), (673, 435)]


def double_slats(centres_px, rib=0.65, gap=0.7, inset=0.75):
    """F87 Competition kidney: pairs of vertical slats (mirrored) as relief ribs in keychain mm, square-ended bars
    stopping `inset` mm short of the kidney wall."""
    inner = Polygon([mm_pt(p) for p in KIDNEY]).buffer(-inset)
    bars = []
    for c in centres_px:
        xc = mm_x(c)
        for dx in (-(gap + rib) / 2, (gap + rib) / 2):
            x0, x1 = xc + dx - rib / 2, xc + dx + rib / 2
            spans = []
            for x in (x0, x1):
                seg = inner.intersection(LineString([(x, -1), (x, 60)]))
                spans.append(seg.bounds[1::2] if not seg.is_empty else None)
            if None in spans:
                continue
            y0, y1 = max(spans[0][0], spans[1][0]), min(spans[0][1], spans[1][1])
            if y1 - y0 > 1.0:
                bars.append(box(x0, y0, x1, y1))
                bars.append(box(-x1, y0, -x0, y1))
    return unary_union(bars)


def honeycomb(a=1.9, b=1.05, h=0.95, rib=0.75, y0=0.0):
    """M-style horizontally stretched honeycomb (pointy left/right cells), symmetric about x=0, in keychain mm."""
    cells = []
    step_x = a + b
    for i in range(-30, 31):
        x = i * step_x
        for j in range(-5, 40):
            y = y0 + j * 2 * h + (h if i % 2 else 0)
            hexa = Polygon([(x + a, y), (x + b, y + h), (x - b, y + h), (x - a, y), (x - b, y - h), (x + b, y - h)])
            cells.append(hexa.buffer(-rib / 2, join_style=2))
    return box(-60, -5, 60, 60).difference(unary_union(cells))


# 4 pairs per kidney (0.72 rib / 0.72 gap): the real car has 5 thinner pairs, but at keychain scale 5 printable
# pairs merge into evenly spaced bars; 4 pairs keep the unmistakable "double slat" rhythm.
SLATS = double_slats([770, 858, 946, 1034], rib=0.72, gap=0.72)
# centre intake mesh, one row of cells centred in the opening (intake spans y 746..907 px)
HONEY = honeycomb(a=1.9, b=1.05, h=0.95, rib=0.75, y0=(PX_B - 826) * S)

SPEC = dict(
    id='f87_m2', name='BMW M2 Competition (F87)',
    ref='kc/cars/f87_m2/ref/front.jpg',
    units='px', px_left=PX_L, px_right=PX_R, px_bottom=PX_B, center_x=CX,
    outline_half=[(1109, 64), (1000, 65), (900, 66), (800, 68), (700, 71), (600, 73), (500, 76), (440, 79), (402, 84),
                  (382, 96), (362, 114), (345, 132), (325, 150), (300, 170), (268, 200), (238, 230), (208, 260),
                  (186, 290), (165, 318), (150, 345), (142, 380), (138, 420), (135, 470), (134, 520), (135, 570),
                  (137, 620), (141, 680), (146, 740), (152, 800), (160, 845), (173, 882), (200, 918), (238, 945),
                  (275, 958), (340, 964), (400, 968), (465, 975), (515, 972), (560, 962), (620, 954), (700, 956),
                  (1109, 958)],
    prims=[
        # headlight unit (whole lens outline)
        dict(kind='poly', color='black', pts=[(214, 320), (228, 305), (252, 299), (300, 301), (340, 309), (400, 325),
                                              (463, 342), (505, 349), (547, 357), (578, 369), (606, 394), (632, 436),
                                              (655, 474), (640, 478), (588, 478), (547, 489), (505, 497), (463, 498),
                                              (400, 493), (338, 485), (297, 477), (262, 462), (236, 437), (221, 405),
                                              (216, 370)]),
        # twin hexagonal corona DRLs: outer U, inner U, the outer ring's right arm runs into the inner ring's left leg
        dict(kind='stroke', color='white', width=0.75, join=2, pts=[(323, 358), (304, 388), (305, 415), (322, 441), (346, 449),
                                                             (402, 449), (423, 438), (441, 413)]),
        dict(kind='stroke', color='white', width=0.75, join=2, pts=[(458, 378), (444, 406), (446, 432), (463, 456), (492, 467),
                                                             (532, 467), (554, 458), (567, 437)]),
        # kidney grille (black surround + double vertical slats)
        dict(kind='poly', color='black', pts=KIDNEY, relief=dict(type='custom', ribs=SLATS)),
        # outer air-curtain slot + side intake (one black area, the white fin splits them at the top)
        dict(kind='poly', color='black', pts=[(251, 598), (262, 590), (275, 596), (271, 640), (265, 690), (257, 740),
                                              (250, 780), (246, 806), (258, 802), (278, 784), (302, 758), (332, 729),
                                              (365, 706), (420, 710), (480, 716), (540, 722), (592, 729), (575, 755),
                                              (550, 785), (520, 820), (490, 850), (462, 872), (400, 870), (330, 866),
                                              (260, 862), (226, 860), (216, 835), (217, 790), (222, 735), (234, 660),
                                              (244, 620)]),
        # large centre intake (honeycomb)
        dict(kind='poly', color='black', pts=[(1115, 746), (683, 746), (655, 772), (628, 802), (606, 832), (601, 848),
                                              (612, 862), (640, 878), (675, 895), (705, 905), (760, 907), (1115, 907)],
             relief=dict(type='custom', ribs=HONEY)),
        # grooves: hood front edge (arched over the roundel), hood/fender shut line
        dict(kind='stroke', color='groove', width=0.55, pts=[(500, 346), (506, 330), (522, 318), (600, 308), (700, 300),
                                                             (800, 293), (900, 286), (980, 280), (1050, 277), (1109, 276)]),
        dict(kind='stroke', color='groove', width=0.55, pts=[(426, 70), (402, 99), (377, 125), (352, 151), (332, 176),
                                                             (320, 206), (318, 245), (329, 282), (342, 306)]),
        # the three small slots in the Competition's lower lip
        dict(kind='stroke', color='black', width=0.65, pts=[(708, 933), (870, 933)]),
        dict(kind='stroke', color='black', width=0.65, pts=[(992, 935), (1109, 935)]),
        # parking sensors + the single tow-hook cover (BMW: viewer's left only)
        dict(kind='ring', color='black', c=(324, 686), r_mm=0.95, width=0.6),
        dict(kind='ring', color='black', c=(763, 650), r_mm=0.95, width=0.6),
        dict(kind='ring', color='black', c=(652, 645), r_mm=1.6, width=0.6, mirror=False),
    ],
    badge=dict(type='roundel', c=(1109, 340), d=3.4),
    tab=dict(y_frac=0.55),
)
