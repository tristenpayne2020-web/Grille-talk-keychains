# BMW M4 (F82, 2018+ LCI) front keychain - traced on BMW Group press photo P90244968 (M4 LCI, straight front)
# Coordinates = pixels of ref/front.jpg (crop 550,380 of the 3508x2683 original). Left half traced, mirrored.
# Revision 1: wider-spaced double kidney slats inside a surround, chunky side-intake blade, solid side intakes,
# coarser centre honeycomb, cleared pinch points (groove/roundel, eyebrow/tail, headlight/kidney wall).
# Revision 2: heavier kidney slats (0.8 rib / 0.8 gap, 4 pairs) to match the line weight of the rest of the set.
import math
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union

PX_L, PX_R, PX_B, CX = 141, 2245, 1290, 1193
S = 80.5 / (PX_R - PX_L)                        # mm per photo pixel


def mm_x(x):
    return (x - CX) * S


def mm_pt(p):
    return ((p[0] - CX) * S, (PX_B - p[1]) * S)


KIDNEY = [(686, 668), (722, 654), (796, 646), (903, 641), (1039, 643), (1128, 653), (1158, 672), (1170, 704),
          (1174, 770), (1166, 823), (1145, 848), (1105, 856), (1000, 859), (900, 857), (822, 848), (780, 836),
          (744, 816), (716, 790), (697, 755), (686, 712)]


def double_slats(centres_px, rib=0.65, gap=0.65, inset=0.8):
    """F82 kidney: pairs of vertical slats (mirrored), as relief ribs in keychain mm. Each slat is a square-ended bar
    that stops `inset` mm short of the kidney wall (the gloss-black surround then reads as a frame, and no slat ends in
    a thin diagonal sliver where it meets the rounded corners)."""
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


def honeycomb(a=1.45, b=0.8, h=0.72, rib=0.65, y0=0.0):
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


# Revision 2: 4 pairs per kidney at 0.8 rib / 0.8 gap (2 extrusion lines each on a 0.4 nozzle), pitch 110 px = 4.21 mm.
# Black between pairs 1.81 mm = black from the outer slats to the kidney edge (1.02 + 0.8 inset), pair ratio 2.26:1.
SLATS = double_slats([765, 875, 985, 1095], rib=0.8, gap=0.8)
HONEY = honeycomb(a=1.9, b=1.05, h=0.95, rib=0.75, y0=(PX_B - 1100) * S)

SPEC = dict(
    id='f82_m4', name='BMW M4 (F82)',
    ref='kc/cars/f82_m4/ref/front.jpg',
    units='px', px_left=PX_L, px_right=PX_R, px_bottom=PX_B, center_x=CX,
    outline_half=[(1193, 358), (1000, 361), (800, 369), (650, 380), (545, 393), (470, 406), (410, 426), (365, 472),
                  (320, 494), (270, 528), (230, 562), (186, 600), (167, 640), (158, 700), (150, 800), (143, 890),
                  (141, 1000), (143, 1100), (149, 1200), (155, 1240), (160, 1262), (172, 1280), (210, 1288),
                  (400, 1290), (1193, 1290)],
    prims=[
        # headlight unit (inner end pulled 12 px in, so a >= 1 mm white wall separates it from the kidney)
        dict(kind='poly', color='black', pts=[(208, 628), (222, 610), (260, 606), (330, 610), (420, 620), (520, 634),
                                              (620, 653), (656, 661), (659, 700), (656, 748), (600, 753), (584, 757),
                                              (566, 771), (548, 790), (515, 803), (450, 805), (380, 800), (300, 788), (255, 772),
                                              (225, 748), (208, 715), (203, 670)]),
        # eyebrow (0.7) + two hexagonal DRL rings (LCI, 0.8) sharing the middle leg; inner ring ends in the tail
        dict(kind='stroke', color='white', width=0.7, pts=[(244, 633), (330, 637), (420, 648), (520, 666), (612, 682)]),
        dict(kind='stroke', color='white', width=0.8, pts=[(262, 640), (259, 690), (268, 726), (288, 750), (380, 752),
                                                            (402, 740), (417, 700), (421, 650)]),
        dict(kind='stroke', color='white', width=0.8, pts=[(419, 695), (428, 737), (446, 763), (472, 771), (521, 771),
                                                            (539, 760), (559, 731), (588, 720), (626, 720)]),
        dict(kind='poly', color='white', pts=[(410, 722), (424, 722), (432, 744), (398, 748)]),   # merged shared stem
        # kidney grille (black surround + double vertical slats)
        dict(kind='poly', color='black', pts=KIDNEY, relief=dict(type='custom', ribs=SLATS)),
        # outer vertical slot (air curtain) + side intake (solid, like the G80) + centre intake (honeycomb)
        dict(kind='poly', color='black', pts=[(226, 992), (240, 970), (258, 972), (260, 1000), (258, 1226), (228, 1226)]),
        dict(kind='poly', color='black', pts=[(284, 1008), (318, 1012), (360, 1033), (420, 1050), (480, 1060),
                                              (540, 1072), (600, 1081), (652, 1094), (625, 1185), (600, 1212),
                                              (340, 1216), (300, 1204), (284, 1170)]),
        dict(kind='poly', color='black', pts=[(1193, 1046), (1000, 1049), (850, 1054), (748, 1064), (686, 1198),
                                              (700, 1214), (1193, 1214)],
             relief=dict(type='custom', ribs=HONEY)),
        # swept slot above the body-colour blade over each side intake (joins the air-curtain slot)
        dict(kind='stroke', color='black', width=0.65, pts=[(252, 968), (300, 968), (360, 977), (420, 987), (480, 993),
                                                             (540, 1003), (600, 1017), (650, 1030), (688, 1050)]),
        # lower lip (about 1.85 mm, ends bluntly on the body edge)
        dict(kind='poly', color='black', pts=[(1193, 1242), (900, 1242), (700, 1241), (420, 1241), (320, 1243),
                                              (260, 1246), (200, 1248), (140, 1249), (140, 1300), (1193, 1300)]),
        # grooves: hood front edge (arched a little over the roundel), power-dome crease, hood/fender shut line
        dict(kind='stroke', color='groove', width=0.55, pts=[(438, 622), (450, 611), (462, 604), (500, 599), (600, 590), (700, 581), (800, 574),
                                                             (900, 568), (1000, 562), (1100, 557), (1193, 554)]),
        dict(kind='stroke', color='groove', width=0.55, pts=[(412, 430), (479, 467), (590, 523), (700, 581)]),
        dict(kind='stroke', color='groove', width=0.55, pts=[(316, 490), (320, 550), (322, 606)]),
        # parking sensors
        dict(kind='ring', color='black', c=(222, 877), r_mm=1.0, width=0.55),
        dict(kind='ring', color='black', c=(782, 1006), r_mm=1.0, width=0.55, mirror=False),   # BMW: single tow-hook cover, viewer's left
    ],
    badge=dict(type='roundel', c=(1193, 622), d=3.3),
    tab=dict(y_frac=0.53),
)
