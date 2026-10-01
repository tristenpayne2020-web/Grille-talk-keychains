# Dodge Charger SRT Hellcat Widebody (7th gen LD, 2020-2023) front keychain.
# Reference: ref/front.jpg = FCA US press photo DG020_186CH (2020 Charger SRT Hellcat Widebody, Indigo Blue, straight-on,
# telephoto, camera ~bumper/headlight height), via moparinsiders.com. Level already (L/R DRL heights within 2 px),
# centreline x 1493. Traced half = viewer's LEFT (the lit side). Coordinates = photo pixels (1 mm = 26.2 px).
import os, sys, math
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):
    SHOW_BADGE = False

CX, YB, XL = 1493, 1414, 440          # centreline, splitter bottom, flare (widest body) left edge
XR = 2 * CX - XL
S = 80.5 / (XR - XL)                  # mm per px


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


def full(pts):
    """left-half px polygon (may cross / touch the centreline) -> union with its mirror (mm)"""
    p = Polygon(mm(pts)).buffer(0)
    return unary_union([p, affinity.scale(p, -1, 1, origin=(0, 0))]).buffer(0)


plain = lambda g: shapely.from_wkb(shapely.to_wkb(g))
mirror_x = lambda g: affinity.scale(g, -1, 1, origin=(0, 0))

# ------------------------------------------------------------------------------------------------ outline
OUTLINE = [(1493, 491), (1300, 494), (1200, 499), (1150, 505), (1000, 518), (850, 532), (750, 543), (700, 550),
           (650, 560), (612, 572), (596, 581), (583, 594), (570, 612), (558, 634), (548, 654), (541, 668),
           # widebody flare
           (524, 675), (502, 687), (480, 702), (463, 720), (451, 742), (444, 767), (441, 795), (440, 830),
           (440, 910), (442, 985), (447, 1050), (455, 1110), (461, 1180), (467, 1240), (473, 1290), (479, 1330),
           (484, 1352), (490, 1366), (499, 1378), (506, 1392), (517, 1405), (540, 1410), (700, 1413), (1493, 1414)]

# ------------------------------------------------------------------------------------------------ black band
# headlamp unit + upper grille = one dark band across the face (the Charger's signature look)
BAND = [(1493, 771), (1100, 771), (1000, 769), (940, 763), (900, 760), (850, 756), (800, 751), (750, 747), (700, 742),
        (650, 737), (600, 734), (578, 735), (559, 742), (545, 758), (536, 783), (534, 815), (538, 850), (547, 873),
        (563, 889), (590, 897), (650, 902), (700, 908), (800, 917), (850, 922), (900, 928), (948, 937),
        (962, 929), (990, 912), (1020, 895), (1060, 881), (1100, 873), (1140, 871), (1493, 871)]
# DRL: the C-shaped LED light pipe framing the lens (top bar, round outer end, bottom bar), open towards the grille
DRL = [(882, 786), (800, 778), (700, 769), (640, 765), (605, 764), (583, 768), (569, 779), (563, 797), (562, 820),
       (564, 842), (571, 858), (585, 867), (605, 872), (650, 876), (700, 881), (750, 886), (800, 890), (850, 895),
       (900, 900), (924, 902)]
DRL_W = 0.7
# upper grille relief zone (right of the slanted grille frame bar between lamp and mesh)
UPPER_ZONE = [(924, 755), (1493, 755), (1493, 886), (1100, 886), (962, 960), (953, 928), (945, 885), (937, 840), (930, 800)]

# mail slot in the body-colour brow under the upper grille
SLOT = [(1493, 901), (1150, 902), (1126, 906), (1110, 915), (1099, 928), (1096, 937), (1115, 935), (1493, 934)]

# hood: central scoop (power bulge inlet) + heat extractors seen edge-on beside it
SCOOP = [(1493, 529), (1400, 530), (1300, 535), (1266, 540), (1249, 547), (1262, 560), (1290, 576), (1320, 589),
         (1345, 596), (1400, 598), (1493, 597)]
# extractors: the slim dark slits under the raised hood shoulders either side of the power bulge (outer end higher)
EXTRACTOR = [(856, 566), (1000, 569), (1140, 565), (1163, 568), (1158, 591), (1000, 592), (862, 584)]

# lower fascia
INTAKE = [(612, 1070), (870, 1070), (882, 1076), (876, 1095), (862, 1150), (842, 1200), (820, 1250), (792, 1300),
          (778, 1318), (762, 1325), (650, 1328), (605, 1328), (588, 1318), (581, 1290), (580, 1110), (588, 1082)]
INTAKE_MESH = [(570, 1186), (802, 1186), (758, 1340), (570, 1340)]
LOWER = [(1493, 1108), (1100, 1109), (1030, 1111), (1000, 1113), (975, 1122), (958, 1136), (944, 1162), (934, 1200),
         (930, 1240), (932, 1280), (940, 1310), (955, 1328), (975, 1337), (1493, 1337)]
SPLITTER = [(1493, 1359), (1000, 1357), (930, 1362), (880, 1367), (800, 1377), (560, 1378), (520, 1379), (499, 1378),
            (470, 1378), (470, 1440), (1493, 1440)]

GROOVE_W = 0.6
prims = [
    # ---- engraved lines
    # hood front edge (shut line above the headlamps/grille), from the hood/fender shut line to the centre
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2,
         pts=[(697, 645), (740, 650), (790, 657), (840, 665), (880, 669), (950, 671), (1050, 668), (1200, 663),
              (1493, 658), (1510, 658)]),
    # hood / fender shut line from the cowl (A-pillar base) down to the hood front corner
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=1, pts=[(680, 552), (688, 598), (697, 645)]),

    # widebody flare: its inner seam against the fascia (from the notch where flare meets fender) and its top crease
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2,
         pts=[(536, 668), (527, 705), (522, 760), (520, 900), (521, 1050), (525, 1150), (531, 1250), (536, 1295)]),
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=1, pts=[(436, 809), (470, 786), (500, 766), (522, 752)]),

    # ---- hood vents
    dict(kind='poly', color='black', pts=SCOOP),
    dict(kind='poly', color='black', pts=EXTRACTOR),

    # ---- headlamps + upper grille band, DRL
    dict(kind='poly', color='black', pts=BAND),
    dict(kind='stroke', color='white', width=DRL_W, smooth=2, pts=DRL),
    # ---- mail slot
    dict(kind='poly', color='black', pts=SLOT),
    # ---- outer intakes, lower grille, splitter
    dict(kind='poly', color='black', pts=INTAKE),
    dict(kind='poly', color='black', pts=LOWER),
    dict(kind='poly', color='black', pts=SPLITTER),
]

SPEC = dict(
    id='charger_srt', name='Dodge Charger SRT Hellcat Widebody',
    ref='kc/cars/charger_srt/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.47),
    badge_on=SHOW_BADGE,
)

# ------------------------------------------------------------------------------------------------ SRT badge
# The real badge sits off-centre on the driver's side of the upper grille (viewer's right): an italic "SRT" wordmark
# (grey on the black mesh). Drawn as white 0.5 mm strokes, 2.6 mm tall (the real one is 1.7 mm - enlarged just enough
# for 0.5 mm strokes and 0.55 mm counters), centred where the photo badge is.
BADGE_H, BADGE_W, BADGE_SLANT = 2.62, 0.52, 13.0          # mm, mm, deg (italic)
BADGE_C = ((1893 - CX) * S, (YB - 821) * S)               # photo badge centre x, grille band centre y


def _rrect(x0, y0, x1, y1, r_right):
    """rectangle with its two right-hand corners rounded (radius r_right)"""
    g = box(x0, y0, x1 - r_right, y1)
    core = box(x0, y0 + r_right, x1, y1 - r_right)
    cs = [Point(x1 - r_right, y0 + r_right).buffer(r_right, 32), Point(x1 - r_right, y1 - r_right).buffer(r_right, 32)]
    return unary_union([g, core] + cs)


def _letters():
    h, w = BADGE_H, BADGE_W
    a, m, b = w / 2, h / 2, h - w / 2                     # centre-lines: bottom, middle, top bar
    L = 1.75                                              # letter width
    gap = 0.62
    # S: one stroke, round outer joins
    S_ = LineString([(L, b), (a, b), (a, m), (L - a, m), (L - a, a), (0.0, a)]).buffer(w / 2, cap_style=2, join_style=1)
    # R: stem + D-shaped bowl + diagonal leg
    x = L + gap
    bowl = _rrect(x, m - w / 2, x + L, h, 0.5).difference(_rrect(x + w, m + w / 2, x + L - w, h - w, 0.12))
    stem = box(x, 0, x + w, h)
    leg = LineString([(x + L - 0.95, m), (x + L - a, 0.0)]).buffer(w / 2, cap_style=2)
    R_ = unary_union([bowl, stem, leg])
    # T
    x = 2 * (L + gap)
    T_ = unary_union([box(x, h - w, x + L, h), box(x + L / 2 - w / 2, 0, x + L / 2 + w / 2, h)])
    g = unary_union([S_, R_, T_]).intersection(box(-1, 0, 20, h))
    g = affinity.skew(g, xs=BADGE_SLANT, origin=(0, 0))
    bx = g.bounds
    return affinity.translate(g, BADGE_C[0] - (bx[0] + bx[2]) / 2, BADGE_C[1] - (bx[1] + bx[3]) / 2)


BADGE_GEOM = plain(shapely.set_precision(_letters(), 0.001)) if SHOW_BADGE else Polygon()
BADGE_CLEAR = 0.5                    # flat black between the letters and the mesh holes

# ------------------------------------------------------------------------------------------------ mesh relief
# The Charger's grilles are a stretched honeycomb: flat-topped cells ~2.7x wider than tall, rows staggered by half a
# cell per column. Real cells are ~3.1 x 1.15 mm at keychain scale (too fine for a 0.4 mm nozzle), so the same
# shape is drawn 1.6x: row pitch HX_RP, column spacing HX_CS, tip length HX_T, walls HX_RIB.
HX_RP, HX_CS, HX_T, HX_RIB = 1.9, 3.8, 1.25, 0.75
RIM = 0.75                           # flat rib lining each recess wall
MIN_HOLE = 0.62                      # every hole (whole or cut at the rim) >= this wide
MIN_CUT = 0.50                       # a cell cut by the rim is kept only if >= this fraction of a whole hole
CUT_MIN_W = 0.85                     # ... and at least this wide somewhere (no thin capsules along the rim)


def hex_holes(zone, x0, y0):
    if zone.is_empty:
        return Polygon()
    minx, miny, maxx, maxy = zone.bounds
    W = HX_CS + HX_T
    cells = []
    for i in range(int(math.floor((minx - x0) / HX_CS)) - 1, int(math.ceil((maxx - x0) / HX_CS)) + 2):
        x = x0 + i * HX_CS
        sh = HX_RP / 2 if i % 2 else 0.0
        for j in range(int(math.floor((miny - y0) / HX_RP)) - 1, int(math.ceil((maxy - y0) / HX_RP)) + 2):
            y = y0 + sh + j * HX_RP
            c = Polygon([(x - W / 2, y), (x - W / 2 + HX_T, y - HX_RP / 2), (x + W / 2 - HX_T, y - HX_RP / 2),
                         (x + W / 2, y), (x + W / 2 - HX_T, y + HX_RP / 2), (x - W / 2 + HX_T, y + HX_RP / 2)])
            cells.append(c.buffer(-HX_RIB / 2, join_style=2))
    full_a = max(c.area for c in cells)
    keep = []
    r = MIN_HOLE / 2
    for c in cells:
        if not c.intersects(zone):
            continue
        if c.within(zone):
            keep.append(c)
            continue
        p = c.intersection(zone)
        if p.area >= 0.95 * c.area:                         # grazes the rim: keep as a whole cell (tiny flat cut)
            keep.append(p)
            continue
        # cut cell: round opening (no wedge tips / slivers)
        near = zone.boundary.buffer(0.7)                    # only round the cut side, keep the far tip sharp
        p = unary_union([p.buffer(-r, join_style=1).buffer(r, join_style=1), p.difference(near)]).intersection(p)
        p = p.buffer(-0.05, join_style=2).buffer(0.05, join_style=2)
        for q in geom.polys(p):
            if q.area >= MIN_CUT * full_a and not q.buffer(-CUT_MIN_W / 2).is_empty:
                keep.append(q)
    return unary_union(keep) if keep else Polygon()


def relief_prim(region, x0, y0, rim=RIM, keepout=None):
    zone = region.buffer(-rim, join_style=2)
    if y0 == 'top':                                           # even-column cells hang whole from the top of the zone
        y0 = zone.bounds[3] - (HX_RP - HX_RIB) / 2 - 0.02
    elif y0 == 'mid':                                         # even and odd rows straddle the zone's mid-height
        y0 = (zone.bounds[1] + zone.bounds[3]) / 2 + HX_RP / 4
    if keepout is not None and not keepout.is_empty:          # flat black ring round the badge, no extra rim there
        zone = geom.clean(zone.difference(keepout))
        region = geom.clean(region.difference(keepout))
    region = geom.clean(region.buffer(-0.36).buffer(0.36).intersection(region))   # no relief strips < 0.72 mm
    holes = hex_holes(zone, x0, y0)
    ribs = geom.clean(region.difference(holes))
    for _ in range(2):
        ribs = geom.regularize(region, ribs, 0.64)
    return dict(kind='geom', color='relief', geom=plain(region), mirror=False,
                relief=dict(type='custom', ribs=plain(ribs)))


BLACK0 = geom.build_maps(SPEC)['black']
_upper = geom.clean(full(UPPER_ZONE).intersection(BLACK0))
_lower = geom.clean(full(LOWER).intersection(BLACK0))
_im = geom.clean(Polygon(mm(INTAKE)).intersection(Polygon(mm(INTAKE_MESH))).intersection(BLACK0))
# the badge sits on a plain black plate at the outer end of the mesh (the mesh stops BADGE_CLEAR short of the letters)
_keep = box(BADGE_GEOM.bounds[0] - BADGE_CLEAR, -1, 60, 60) if SHOW_BADGE else None
prims.append(relief_prim(_upper, 0.0, (YB - 821) * S + 0.45, keepout=_keep))
prims.append(relief_prim(_lower, 0.0, 'top'))
_imh = relief_prim(_im, -32.6, 'mid')
_imh['geom'] = plain(unary_union([_imh['geom'], mirror_x(_imh['geom'])]))
_imh['relief']['ribs'] = plain(unary_union([_imh['relief']['ribs'], mirror_x(_imh['relief']['ribs'])]))
prims.append(_imh)
if SHOW_BADGE:
    prims.append(dict(kind='geom', color='white', geom=BADGE_GEOM, mirror=False, badge=True))
