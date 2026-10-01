# Honda Civic Si (11th gen FE, 2022+, pre-facelift) front keychain.
# Reference: ref/front.jpg = Motor1 review photo (1920 x 1080), straight-on, level, camera ~hood height. See ref/SOURCE.txt.
# Traced half = viewer's LEFT (car's right). Photo pixels, 1 mm = 12.41 px.
# Revision 1: lit DRL end cap + tapered top strip, flat wide honeycomb (custom relief) with a solid grille surround,
# taller Honda H in a sturdier frame, steep hood-line exit, slimmer lamp, slats 2.0/1.0 without slivers, rounded pocket corner.
# Revision 2: classic-build honeycomb symmetric again (simple DRL ring -> build3d's buffer(0) keeps every band hole),
# Honda H with the V upper notch (taller than wide), thicker DRL light bar, tapered lower corner wing, bolder 1.2 mm
# slats (5 bars, G80-style chamfered tops in classic), whole honeycomb cells only, recessed fog-pocket insert,
# thicker white walls at the hood-line hook and the lamp's outer end.
import math
import os
import sys
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom  # noqa: E402  (read-only use: regularize() for the custom honeycomb)

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):
    SHOW_BADGE = False

CX, YB, XL = 962.5, 842, 463
S = 80.5 / (2 * (CX - XL))              # mm per px
PX = 1.0 / S                            # px per mm (12.41)


def mm(p):
    return ((p[0] - CX) * S, (YB - p[1]) * S)


def mm_geom(g):
    """px-space shapely geometry -> keychain mm (x right, y up)."""
    return affinity.scale(affinity.translate(g, -CX, -YB), S, -S, origin=(0, 0))


def mirror(g):
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])


OUTLINE = [(962.5, 392), (800, 392), (640, 393), (598, 394), (578, 397), (556, 405), (536, 420), (520, 440),
           (509, 460), (496, 480), (480, 500), (470, 520), (465, 540), (463, 565), (463, 680), (465, 760), (468, 800), (472, 816), (480, 828), (495, 833), (640, 831), (660, 836), (760, 842), (962.5, 842)]

# black band: headlight lens + gloss trim under it + honeycomb upper grille (one continuous piece, like the car).
# Lamp top edge follows the lens top (2 px higher than r0), lower edge lifted 3-5 px mid-lamp so the lamp reads slimmer.
BAND = [(496, 498), (520, 500), (560, 507), (600, 515), (640, 524), (680, 533), (708, 538), (740, 547), (770, 555),
        (800, 559), (962.5, 559), (962.5, 638), (800, 638), (784, 635), (760, 626), (720, 611), (680, 599),
        (640, 592), (600, 586), (560, 581), (520, 578), (498, 576), (486, 572), (481, 562), (479, 541), (483, 522),
        (487, 508)]

# ------------------------------------------------------------------ DRL: lit outer end cap + top light strip
M_DRL = 0.63 * PX                        # black kept between the DRL and every band edge (px)
_band_px = Polygon(BAND)
_inner_px = _band_px.buffer(-M_DRL, join_style=1)


def _band_top(x):
    top = [p for p in BAND[:10]]
    for (x0, y0), (x1, y1) in zip(top, top[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return top[-1][1]


def _taper(pts, r0, r1):
    """tapered round-ended stroke (px): radius r0 at the first point -> r1 at the last"""
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.dist(a, b))
    rs = [r0 + (r1 - r0) * l / L[-1] for l in L]
    parts = [unary_union([Point(a).buffer(ra, 32), Point(b).buffer(rb, 32)]).convex_hull
             for a, b, ra, rb in zip(pts, pts[1:], rs, rs[1:])]
    return unary_union(parts)


R0, R1 = 1.15 * PX / 2, 0.72 * PX / 2    # light bar 1.15 mm at the cap -> 0.72 mm at the inner tip (photo: 1.1-1.2 mm)
_X0, _X1 = 500, 705                      # strip runs to the lens's inner top corner
_xs = [500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 705]
_strip_c = [(x, _band_top(x) + M_DRL + 0.4 + R0 + (R1 - R0) * (x - _X0) / (_X1 - _X0)) for x in _xs]
_strip = _taper(_strip_c, R0, R1)
_cap = Polygon([(470, 498), (510, 504), (508, 530), (503, 555), (497, 578), (470, 590)])   # lit outer end of the lens
# open (r 2.5 px ~ 0.2 mm) to round the cap's lower inner spike, close to fill the strip/cap seam, then simplify:
# a lean ring matters - the dense round-cap ring made build3d's buffer(0) drop the right honeycomb hole (classic build)
DRL_PX = (unary_union([_strip, _cap]).intersection(_inner_px)
          .buffer(-2.5, join_style=1).buffer(2.5, join_style=1).buffer(0.3).buffer(-0.3).simplify(0.2))
DRL_PTS = [(round(x, 2), round(y, 2)) for x, y in DRL_PX.exterior.coords][:-1]

# ------------------------------------------------------------------ lower: corner pocket + lip line + lower grille + lip
LOWER = [(962.5, 677), (740, 677), (718, 679), (703, 685), (688, 697), (674, 714), (662, 732), (651, 752),
         (642, 772), (636, 788), (610, 787), (590, 785), (574, 782), (565, 776), (563, 762), (575, 733), (588, 703),
         (602, 675), (560, 673), (500, 673), (489, 676), (483, 686), (482, 700), (482, 782), (485, 786), (520, 792),
         (560, 798), (620, 805), (656, 811), (662, 824), (668, 860), (962.5, 860)]
# white lower wing (under the pocket): top edge follows the photo (785 px at the fender -> 810 px at the lip), so it
# tapers from ~3.8 mm at the fender to ~1.3 mm at its inner tip, sweeping down with the black trim line.
SLAT_BOT = 814                           # recess bottom: 5 ribs with a gap at both walls (photo: lip edge ~805-810 px)
SLAT_ZONE = [(962.5, 677), (740, 677), (718, 679), (703, 685), (688, 697), (674, 714), (662, 732), (651, 752),
             (642, 772), (637, SLAT_BOT), (962.5, SLAT_BOT)]
SLATS = dict(type='hbars', pitch=2.0, rib=1.2, offset=-0.2)   # 5 ribs, gaps 1.1 top / 0.8 / 0.7 bottom (swept: 0 slivers)
# recessed inner insert of the fog-light pocket (black bezel ~0.8 mm stays flush), a small depth cue like the grilles
POCKET_INSERT = [(494, 686), (560, 686), (548, 772), (494, 772)]

# hood outline; at the top it hooks in and runs out of the top edge steeply (no knife-edge against the chamfer)
HOOD = [(962.5, 479), (800, 479), (620, 479), (549, 478), (533, 475), (526, 466), (532, 452), (545, 437),
        (557, 424), (568, 414), (574, 386)]     # hook 3-4 px further in: >= 1 mm white wall to the body edge

# ------------------------------------------------------------------ Honda 'H' badge: white frame, black field, white H
BW_TOP, BW_BOT, BH, BR, RING = 6.2, 5.8, 5.36, 0.85, 0.62
BADGE_C = (0.0, mm((962.5, 559))[1] + RING - BH / 2)   # black field top = band top line (559 px); frame top meets the nose
BADGE_PLATE = 0      # >0 = black outline round the frame top (face.png preview mis-paints nested islands, so off)


def badge_frame():
    cx, cy = BADGE_C
    tr = Polygon([(cx - BW_TOP / 2 + BR, cy + BH / 2 - BR), (cx + BW_TOP / 2 - BR, cy + BH / 2 - BR),
                  (cx + BW_BOT / 2 - BR, cy - BH / 2 + BR), (cx - BW_BOT / 2 + BR, cy - BH / 2 + BR)])
    return tr.buffer(BR, 64)


def honda_badge():
    cx, cy = BADGE_C
    rounded = badge_frame()
    inner = rounded.buffer(-RING, 64)
    out = []
    if BADGE_PLATE:     # thin black outline round the frame top where it overlaps the nose, so the whole frame reads
        out.append(dict(kind='geom', color='black', geom=rounded.buffer(BADGE_PLATE, 64), mirror=False))
        outer = rounded
    else:               # frame top merges into the nose; square top corners avoid tiny black cusps at the nose edge
        b = rounded.bounds
        outer = unary_union([rounded, rounded.intersection(box(b[0] - 1, cy + BH / 2 - BR, b[2] + 1, b[3] + 1)).envelope])
    # Honda H (photo: 3.2 w x 3.6 h, fills the field height): taller than wide, slightly wider at the top, slim legs
    # at the top that thicken downwards because the upper notch is a V (1.7 mm at the top -> 0.8 mm at the bar),
    # crossbar set low, short narrow lower notch.
    top, bot = cy + 1.46, cy - 1.46                      # 2.92 mm tall, 0.6 mm black to the field top/bottom
    b0, b1 = bot + 0.72, bot + 1.36                      # crossbar 0.64 mm
    legL = Polygon([(cx - 1.48, top), (cx - 0.84, top), (cx - 0.40, b1), (cx - 0.40, b0), (cx - 0.42, bot),
                    (cx - 1.30, bot)])
    legR = affinity.scale(legL, -1, 1, origin=(cx, cy))
    bar = box(cx - 0.8, b0, cx + 0.8, b1)
    H = unary_union([legL, legR, bar])
    return out + [dict(kind='geom', color='white', geom=outer, mirror=False),
                  dict(kind='geom', color='black', geom=inner, mirror=False),
                  dict(kind='geom', color='white', geom=H, mirror=False)]


# ------------------------------------------------------------------ Si honeycomb: wide flat cells (custom relief)
# photo: cells ~45 x 17 px (3.6 x 1.4 mm), columns ~40 px apart, alternate columns half a cell lower, ~3 cells per column;
# solid black surround (~0.65 mm) on top and bottom like the grille frame, solid ring around the badge.
HEX_ZONE = [(755, 568), (962.5, 568), (962.5, 700), (806, 700)]        # slanted side = grille side frame
HX_PC, HX_HP, HX_TIP, HX_RIB, HX_Y0 = 3.3, 1.85, 0.62, 0.70, 1.4
HX_X0 = 2.0 if SHOW_BADGE else 0.0     # column phase (mm), swept: most whole cells between badge and lamp
HX_KEEP = 0.5        # keep only cells with >= 50 % of their area inside the region (partials become solid rib)


def honeycomb():
    zone = mirror(mm_geom(Polygon(HEX_ZONE)))
    region = zone.intersection(mirror(mm_geom(_band_px)).buffer(-0.65, join_style=1))
    if SHOW_BADGE:                                   # one plain box: solid black round the badge and below it
        cx, cy = BADGE_C
        hw = BW_TOP / 2 + 0.62
        region = region.difference(box(cx - hw, cy - BH / 2 - 5.62, cx + hw, cy + BH / 2 + 0.62))
    region = region.buffer(0.01, join_style=2).buffer(-0.01, join_style=2)
    minx, miny, maxx, maxy = zone.bounds
    W = HX_PC + HX_TIP
    Wf = HX_PC - HX_TIP
    cy0 = mm((0, 568))[1] - HX_Y0
    kept = []
    n = int((maxx + W) / HX_PC) + 2
    for i in range(-n, n + 1):
        x = HX_X0 + i * HX_PC
        yoff = (HX_HP / 2) if i % 2 else 0.0
        for j in range(-2, 8):
            y = cy0 - j * HX_HP - yoff
            hexa = Polygon([(x - W / 2, y), (x - Wf / 2, y + HX_HP / 2), (x + Wf / 2, y + HX_HP / 2),
                            (x + W / 2, y), (x + Wf / 2, y - HX_HP / 2), (x - Wf / 2, y - HX_HP / 2)])
            cell = hexa.buffer(-HX_RIB / 2, join_style=2)
            if x < -1e-6 or (x < 1e-6 and SHOW_BADGE):  # build the right half only, mirror it below
                continue
            if cell.intersection(region).area >= HX_KEEP * cell.area:
                kept.append(cell)
    holes = mirror(unary_union(kept))                # exact mirror symmetry
    ribs = region.difference(holes)
    return region, geom.regularize(region, ribs, 0.62)


HEX_REGION, HEX_RIBS = honeycomb()


prims = [
    dict(kind='poly', color='black', pts=BAND),
    dict(kind='poly', color='white', pts=DRL_PTS),
    dict(kind='geom', color='relief', geom=HEX_REGION, mirror=False, relief=dict(type='custom', ribs=HEX_RIBS)),
    dict(kind='poly', color='black', pts=LOWER),
    dict(kind='poly', color='relief', pts=SLAT_ZONE, relief=SLATS),
    dict(kind='geom', color='relief', geom=mm_geom(Polygon(POCKET_INSERT)).buffer(-0.5, join_style=1).buffer(0.5, join_style=1),
         relief=dict(type='none')),
    dict(kind='stroke', color='groove', width=0.55, pts=HOOD, smooth=1),
]

if SHOW_BADGE:
    prims += honda_badge()

SPEC = dict(
    id='civic_11th', name='Honda Civic Si (11th gen)',
    ref='kc/cars/civic_11th/ref/front.jpg',
    units='px', px_left=XL, px_right=2 * CX - XL, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.49),
)
