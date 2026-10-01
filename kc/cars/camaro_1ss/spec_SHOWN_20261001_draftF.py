# Chevrolet Camaro SS / 1SS (6th gen, 2020-2024 revised SS front) keychain.
# Reference: ref/front.jpg = crop (x 300..3460, y 400..2200) of ref/cand_cleveland.jpg scaled 0.5
# (Wikimedia Commons "2023 Cleveland Auto Show (52790072809).jpg", Erik Drost, CC BY 2.0). See ref/SOURCE.txt.
# Traced half = viewer's LEFT, photo pixels of ref/front.jpg (1 mm = 17.96 px).
# NO LOGOS: no bowtie, no SS badge (badge=None, no SHOW_BADGE prims) - the upper grille is left plain grille.
#
# Revision 1: grille reliefs are generated here (custom ribs) inside a solid rim so no clipped hex/slat slivers
# reach the recess wall; lower = coarse honeycomb (3.0 / 0.8), upper = two slats that follow the band's curve.
import os, sys, math
import shapely
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

CX, YB = 797, 858                   # centreline / lowest outline point (splitter bottom), photo px
XL = 74                             # widest outline point (splitter winglet tip) -> 80.5 mm, so the pipeline's
XR = 2 * CX - XL                    # force-width scale is exactly 1 and the custom mm geometry lines up
S = 80.5 / (XR - XL)                # mm per px
GW = 0.65                           # groove width (mm)

plain = lambda g: shapely.from_wkb(shapely.to_wkb(shapely.set_precision(g.buffer(0), 0.001)))


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


def full(half):
    """left-half px trace starting and ending on the centreline -> symmetric polygon in mm"""
    h = mm(half)
    return Polygon(h + [(-x, y) for x, y in reversed(h)]).buffer(0)


def both(g):
    return unary_union([g, shapely.affinity.scale(g, -1, 1, origin=(0, 0))])


OUTLINE = [(797, 178), (600, 181), (420, 189), (300, 197), (238, 205), (192, 226), (152, 262), (120, 305),
           (99, 360), (86, 430), (79, 500), (77, 600), (79, 680), (86, 714),
           (76, 736), (74, 768), (82, 790), (150, 813), (300, 836), (450, 850), (620, 855), (797, 858)]
# headlamps + upper grille: one continuous black band (the 2020 SS look)
BAND = [(797, 388), (600, 380), (530, 370), (420, 362), (380, 355), (330, 343), (250, 330), (160, 319), (140, 322),
        (141, 352), (150, 388), (160, 411), (250, 430), (350, 450), (450, 461), (560, 471), (680, 477), (797, 482)]
# lower opening: outer C-shaped corner channel + bottom slot + lower grille (white tongue left inside)
LOWER = [(130, 505), (280, 516), (300, 575), (306, 596), (290, 600), (165, 566), (160, 585),
         (174, 611), (208, 632), (292, 648), (428, 668), (395, 601), (480, 592),
         (797, 597), (797, 782), (520, 772), (420, 780), (250, 750), (154, 734),
         (126, 716), (117, 680), (116, 600), (118, 520)]
# relief windows (overshoot the opening where the edge is the black wall; clipped to the black host)
LOWER_WIN = [(797, 580), (470, 578), (390, 590), (428, 668), (420, 800), (797, 800)]
UPPER_WIN = [(797, 360), (562, 356), (540, 404), (372, 412), (352, 470), (797, 500)]

RIM = 0.75           # solid rib frame along the recess wall (mm)
HOLE_MIN_W, HOLE_MIN_A = 0.8, 1.6


def finish(region, holes, rim=RIM):
    zone = region.buffer(-rim, join_style=2)
    holes = holes.intersection(zone)
    r = HOLE_MIN_W / 2
    holes = holes.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(holes)
    holes = unary_union([q for q in geom.polys(holes) if q.area >= HOLE_MIN_A])
    ribs = geom.clean(region.difference(holes))
    for _ in range(2):
        ribs = geom.regularize(region, ribs, 0.64)
    # overlap the wall slightly so the pipeline's own region clip leaves no zero-width gap slivers
    ribs = unary_union([ribs, region.buffer(0.3, join_style=2).difference(region.buffer(-0.3, join_style=2))])
    return ribs


def lower_relief(pitch=3.0, rib=0.8, off=1.5):
    region = full(LOWER_WIN).intersection(full(LOWER))
    minx, miny, maxx, maxy = region.bounds
    a = pitch / math.sqrt(3)
    cells = []
    for i in range(-20, 21):
        for j in range(-6, 7):
            x = i * 1.5 * a                       # column 0 on the centreline -> symmetric honeycomb
            y = (miny + maxy) / 2 + off + j * pitch + (pitch / 2 if i % 2 else 0)
            hexa = Polygon([(x + a * math.cos(math.radians(60 * k)), y + a * math.sin(math.radians(60 * k)))
                            for k in range(6)])
            cells.append(hexa.buffer(-rib / 2, join_style=2))
    return region, finish(region, unary_union(cells))


def upper_relief(rib=0.8):
    region = full(UPPER_WIN).intersection(full(BAND))
    # one slat along the middle of the band between the DRL tails: two stacked slots in the centre,
    # a single slot under each DRL tail
    mid = [(538, 402), (566, 416), (610, 425), (680, 430), (797, 435)]
    h = mm(geom.chaikin(mid, 2, closed=False))
    line = LineString(h + [(-x, y) for x, y in reversed(h[:-1])])
    slat = line.buffer(rib / 2, cap_style=2, join_style=1)
    return region, finish(region, region.difference(slat), rim=0.7)


_LREG, _LRIBS = lower_relief()
_UREG, _URIBS = upper_relief()

SPEC = dict(
    id='camaro_1ss', name='Chevrolet Camaro SS (6th gen, 2020+)',
    ref='kc/cars/camaro_1ss/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, center_x=CX, px_bottom=YB,
    outline_half=OUTLINE,
    prims=[
        dict(kind='poly', color='black', pts=BAND),
        # DRL light guide: down the outer lamp edge, along the bottom (raised off the lamp's lower edge),
        # kink up, long tail inward along the grille top
        dict(kind='stroke', color='white', width=0.8, pts=[(163, 336), (166, 368), (188, 390), (240, 397), (318, 400),
                                                           (340, 396), (366, 387), (400, 384), (508, 388)]),
        dict(kind='poly', color='black', pts=LOWER),
        # SS corner-intake LED bar (white)
        dict(kind='stroke', color='white', width=0.7, pts=[(150, 530), (282, 576)]),
        # lower grille honeycomb and upper grille slats (custom ribs inside a solid rim)
        dict(kind='geom', color='relief', geom=plain(_LREG), mirror=False, relief=dict(type='custom', ribs=plain(_LRIBS))),
        dict(kind='geom', color='relief', geom=plain(_UREG), mirror=False, relief=dict(type='custom', ribs=plain(_URIBS))),
        # splitter lip with small winglet tips that step out past the fascia
        dict(kind='poly', color='black', pts=[(797, 830), (600, 821), (440, 807), (250, 791), (120, 774), (98, 748),
                                              (88, 716), (86, 714), (76, 736), (74, 768), (82, 790), (150, 813), (300, 836),
                                              (450, 850), (620, 855), (797, 858)]),
        # hood extractor vent insert (thin tapered slot)
        dict(kind='poly', color='black', pts=[(797, 197), (640, 196), (604, 199), (618, 208), (660, 212), (797, 213)]),
        # grooves: hood leading edge, power-dome sides (both run off the outline / into the hood line),
        # fascia crease into the lower-grille corner, nose 'beak' crease under the band
        dict(kind='stroke', color='groove', width=GW, smooth=2,
             pts=[(226, 200), (265, 243), (310, 266), (400, 290), (520, 305), (650, 312), (797, 315)]),
        dict(kind='stroke', color='groove', width=GW, smooth=2, pts=[(566, 170), (578, 228), (606, 270), (638, 318)]),
        dict(kind='stroke', color='groove', width=GW, pts=[(300, 482), (355, 548), (392, 597), (401, 607)]),
        dict(kind='stroke', color='groove', width=GW, pts=[(316, 500), (500, 510), (797, 515)]),
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
