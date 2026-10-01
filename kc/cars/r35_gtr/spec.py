# Nissan GT-R (R35, 2017+ facelift) front keychain - revision 1.
# Reference: ref/front.jpg = Wikimedia Commons "Nissan GT-R MY2017 (2).jpg" (Tokumeigakarinoao, CC BY-SA 4.0),
# straight-on, level, symmetric about x 995 (checked with a left/right mirror blend). See ref/SOURCE.txt.
# Traced half = viewer's LEFT (car's right). Coordinates are photo pixels (1 mm = 18.31 px).
#
# Design (G80 language): white = body paint. Black = headlamp units, the one big hexagonal grille opening, the corner
# intakes, the two hood vents and the dark corner splitter blades (the MY17 lower lip is body colour in the centre).
# White on black = light signature + chrome: the 'lightning bolt' LED light guide (0.9 mm stroke that splits the lamp
# edge to edge: down the outer lens edge, across the lamp, down the inner edge to the lower inner tip), the LED lamps
# on top of the corner intakes, and the V-motion chrome 'U' (thin side strips from the grille's top corners + its broad
# flat bottom) that is THE MY17+ grille signature.
# Relief = expanded-metal diamond mesh (built here, symmetric, framed by a 0.7 mm rim, rounded hole tips so the preview
# matches the print) in the upper grille above the U and in the lower half of the lower grille (the smooth sensor band
# above it stays plain black, licence plate dropped); three vertical fin slots in each corner intake under the lamp.
# Grooves (0.6 mm) = hood/fender shut lines (inside the body -> lamp top), hood front shut line, hood bulge creases,
# lower bumper corner creases.
# Badge = the R35's real grille emblem (framed 'R', sitting on the chrome U) - the R35 carries no Nissan roundel on the
# front; BADGE_STYLE = 'nissan' gives a simplified circle-with-bar Nissan emblem instead. SHOW_BADGE / KC_BADGE=0
# switch it off (the mesh then fills the emblem's place).
# HOOD_K: the photo is taken from above hood height (the seats are visible) so the hood is over-long; everything above
# the hood front line (y 645 px) is compressed vertically by HOOD_K to get the G80's front-elevation proportions.
import os, sys, math
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

SHOW_BADGE = True
BADGE_STYLE = 'gtr'          # 'gtr' = the R emblem the R35 really wears on its grille; 'nissan' = circle-with-bar
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):
    SHOW_BADGE = False

CX, YB, XL = 995, 1172, 258   # centreline, bottom of the bumper lip, widest body point (fender) - photo px
XR = 2 * CX - XL
S = 80.5 / (XR - XL)          # mm per px (outline extremes == XL/XR -> the pipeline applies no extra scaling)

HOOD_Y, HOOD_K = 645, 0.85    # compress the (camera-lengthened) hood above the hood front line
if os.environ.get('KC_HOOD_K'):
    HOOD_K = float(os.environ['KC_HOOD_K'])


def hk(pts):
    """photo px -> design px: vertical compression of everything above the hood front line"""
    return [(x, y if y >= HOOD_Y else HOOD_Y - (HOOD_Y - y) * HOOD_K) for x, y in pts]


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in hk(pts)]


def full(half):
    """left-half px trace that starts and ends on the centreline -> symmetric polygon in mm"""
    h = mm(half)
    return Polygon(h + [(-x, y) for x, y in reversed(h)]).buffer(0)


mirror_x = lambda g: affinity.scale(g, -1, 1, origin=(0, 0))
plain = lambda g: shapely.from_wkb(shapely.to_wkb(g))

# ------------------------------------------------------------------ outline (top centre -> out -> down -> bottom centre)
OUTLINE = [(995, 410), (900, 410), (800, 411), (700, 413), (600, 416), (540, 418), (508, 421),
           (490, 432), (462, 450), (430, 468), (395, 489), (360, 510), (332, 532), (308, 560), (290, 592),
           (276, 630), (266, 670), (261, 710), (259, 760), (258, 850), (259, 950), (261, 1010), (262, 1045),
           (264, 1100), (269, 1140), (280, 1150), (330, 1156), (400, 1163), (470, 1170),
           (560, 1172), (700, 1172), (995, 1172)]

HEADLIGHT = [(363, 526), (418, 521), (453, 600), (480, 660), (499, 698), (502, 718), (496, 738), (482, 750),
             (320, 738), (313, 728), (313, 700), (318, 660), (326, 620), (331, 580), (342, 548)]
# lightning-bolt LED light guide: outer leg along the lens edge, knee, across the lamp, inner leg to the lower tip
DRL = [(370, 552), (349, 606), (436, 618), (463, 668), (480, 724)]
DRL_W = 0.9

GRILLE = [(995, 722), (660, 722), (648, 731), (600, 778), (560, 822), (548, 840), (536, 862), (527, 890),
          (523, 930), (521, 1000), (521, 1050), (524, 1072), (533, 1085), (548, 1093), (580, 1097), (700, 1099),
          (995, 1100)]
# V-motion chrome: thin side strips from the grille's top corners + the broad flat bottom of the chrome 'U'
VBAR = [(668, 710), (700, 758), (735, 803), (757, 830), (775, 843), (800, 848), (995, 849), (1005, 849)]
U_TOP = 807                   # px, top edge of the chrome U's flat bottom part (photo ~800-805)
U_FLAT = [(995, U_TOP), (768, U_TOP), (755, 810), (746, 816), (757, 830), (775, 843), (800, 848), (995, 849)]
UPPER_MESH = [(995, 722), (676, 722), (700, 758), (735, 803), (757, 830), (775, 843), (800, 848), (995, 849)]
# lower grille mesh: only below the smooth sensor band (photo: plain dark panel y 850-950, mesh below)
LOWER_MESH = [(995, 952), (534, 950), (534, 1050), (537, 1068), (545, 1077), (560, 1082), (590, 1085), (995, 1087)]

INTAKE = [(298, 812), (330, 818), (402, 836), (411, 846), (405, 900), (397, 960), (387, 1000), (377, 1020),
          (362, 1031), (330, 1035), (298, 1036)]
INTAKE_LAMP = [(314, 832), (396, 850), (394, 878), (314, 862)]
INTAKE_MESH = [(298, 877), (408, 897), (397, 960), (387, 1000), (377, 1020), (362, 1031), (330, 1035), (298, 1036)]

CANARD = [(250, 1046), (285, 1050), (300, 1062), (301, 1098), (340, 1114), (400, 1135), (445, 1151), (470, 1158),
          (470, 1185), (250, 1185)]

VENT = [(672, 452), (688, 446), (746, 447), (752, 454), (724, 478), (710, 483), (696, 479), (678, 464)]   # crisp shield

GW = 0.62

# ------------------------------------------------------------------ badge


def rrect(w, h, r):
    return box(-w / 2 + r, -h / 2 + r, w / 2 - r, h / 2 - r).buffer(r, 32)


def r_glyph(h=2.2, w=2.0, s=0.6, t=0.55, c=0.55, leg_x=1.12, leg_w=0.7):
    """block 'R' (mm), centred on its bbox: stem s, bowl (bars t, counter c tall), straight diagonal leg whose notch
    to the stem is >= leg_x - s wide"""
    bh = 2 * t + c                                       # bowl height
    by0 = h - bh                                         # bowl bottom
    ro = bh / 2
    xc, yc = w - ro, by0 + ro
    bowl_o = unary_union([box(0, by0, xc, h), Point(xc, yc).buffer(ro, 48)])
    bowl_i = unary_union([box(s, by0 + t, xc, h - t), Point(xc, yc).buffer(c / 2, 48)])
    stem = box(0, 0, s, h)
    leg = Polygon([(leg_x, by0 + 0.05), (leg_x + leg_w, by0 + 0.05), (w, 0), (w - leg_w, 0)])
    g = unary_union([stem, bowl_o.difference(bowl_i), leg])
    return affinity.translate(g, -w / 2, -h / 2)


def badge_geoms():
    """GT-R emblem sitting on the chrome U: white frame + white 'R' in a black window whose floor is the U's top edge.
    Returns (white geometry, mesh exclusion zone) in mm."""
    u = (YB - U_TOP) * S                                 # U top edge (mm)
    if BADGE_STYLE == 'nissan':
        cy = (u + (YB - GRILLE[0][1]) * S) / 2
        ring = Point(0, cy).buffer(1.75, 64).difference(Point(0, cy).buffer(1.2, 64))
        bar = affinity.translate(rrect(4.6, 1.05, 0.2), 0, cy)
        arcs = ring.difference(bar.buffer(0.55)).buffer(-0.27).buffer(0.27)     # no tapered arc tips
        white = unary_union([arcs, bar])
        zone = unary_union([Point(0, cy).buffer(1.75), bar]).buffer(0.7)
        return plain(white), zone
    W, F, R, M, RH = 4.5, 0.55, 0.9, 0.58, 2.2           # ~4.5 x 3.9 mm above the U (real emblem is wider than tall)
    win_top = u + M + RH + M
    top = win_top + F
    outer = affinity.translate(rrect(W, top - (u - 1.0), R), 0, (top + u - 1.0) / 2)
    win_h = win_top - u
    # window: top corners concentric with the frame's outer corners (uniform frame), square floor on the U
    window = affinity.translate(rrect(W - 2 * F, win_h + 2 * (R - F), R - F), 0, u + win_h / 2 - (R - F))
    window = window.intersection(box(-W, u, W, win_top))
    glyph = affinity.translate(r_glyph(h=RH), 0, u + M + RH / 2)
    white = unary_union([outer.difference(window), glyph])
    zone = outer.buffer(0.7)
    return plain(white), zone


# ------------------------------------------------------------------ paint (without the relief meshes)
P = lambda pts: hk(pts)
prims = [
    # engraved lines first (black parts painted later cover their ends)
    dict(kind='stroke', color='groove', width=GW, smooth=1,
         pts=P([(452, 482), (434, 502), (424, 522), (416, 540)])),                              # hood/fender shut line
    dict(kind='stroke', color='groove', width=GW, smooth=1,
         pts=P([(470, 678), (520, 662), (560, 652), (650, 648), (800, 646), (995, 645), (1005, 645)])),  # hood front edge
    dict(kind='stroke', color='groove', width=GW,
         pts=P([(525, 454), (631.6, 649)])),                                               # hood bulge crease (ends on
    #                                                                                        the front line's centre)
    dict(kind='stroke', color='groove', width=GW,
         pts=P([(549, 1110), (562, 1131), (574, 1151)])),                                  # lower bumper corner crease

    dict(kind='poly', color='black', pts=P(VENT)),                                           # hood vents
    dict(kind='poly', color='black', pts=P(HEADLIGHT), smooth=1),                            # headlight unit
    dict(kind='stroke', color='white', width=DRL_W, pts=P(DRL)),                             # lightning-bolt DRL

    dict(kind='poly', color='black', pts=GRILLE),                                            # the big grille opening
    dict(kind='stroke', color='white', width=0.85, pts=VBAR),                                # V-motion chrome U
    dict(kind='poly', color='white', pts=U_FLAT),

    dict(kind='poly', color='black', pts=INTAKE),                                            # corner intakes
    dict(kind='poly', color='white', pts=INTAKE_LAMP),                                       # LED lamp

    dict(kind='poly', color='black', pts=CANARD),                                            # corner splitter blades
]
if SHOW_BADGE:
    BADGE_W, BADGE_ZONE = badge_geoms()
    prims.append(dict(kind='geom', color='white', geom=BADGE_W, mirror=False, badge=True))
else:
    BADGE_ZONE = Polygon()

SPEC = dict(
    id='r35_gtr', name='Nissan GT-R (R35, MY17+)',
    ref=('kc/cars/r35_gtr/ref/front_hood085.jpg' if abs(HOOD_K - 0.85) < 1e-9 else 'kc/cars/r35_gtr/ref/front.jpg'),
    # (front_hood085.jpg = the photo with the same hood compression, work/warp_ref.py, so overlay.png lines up)
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=hk(OUTLINE),
    prims=prims,
    tab=dict(y_frac=0.52),
    badge_on=SHOW_BADGE,
)

# ------------------------------------------------------------------ relief (recessed meshes), built here so they are
# exactly symmetric and framed by a rim rib like a real mesh behind its surround
MESH_PITCH, MESH_RIB, MESH_ANG = 2.2, 0.8, 26.5      # expanded-metal diamonds ~3.1 x 1.6 mm holes, 0.8 mm ribs
TIP_R = 0.3                                           # hole tips rounded like the printed result
RIM = 0.7                                             # rim rib along the pocket wall (meshes)
SLOT_RIM = 0.7
HOLE_MIN_W = 0.75
HOLE_MIN_FRAC = dict(upper=0.6, lower=0.5, slots=0.3)  # upper band: drop part-cells rather than print slivers
SLOT_PITCH, SLOT_RIB = 1.53, 0.73                      # corner intake vertical fins


def _keep_holes(cells, full_area, frac, min_w=None, join=2):
    keep = []
    r = (min_w or HOLE_MIN_W) / 2
    for c in geom.polys(cells):
        q = c.buffer(-r, join_style=join).buffer(r, join_style=join).intersection(c)
        for p in geom.polys(q):
            if p.area >= frac * full_area:
                keep.append(p)
    return unary_union(keep) if keep else Polygon()


def diamond_holes(region, y0, frac):
    """holes of two mirror-symmetric crossing bar families (angle +-MESH_ANG, perpendicular pitch MESH_PITCH)"""
    th = math.radians(MESH_ANG)
    minx, miny, maxx, maxy = region.bounds
    D = max(abs(minx), abs(maxx)) + 5
    dv = MESH_PITCH / math.cos(th)
    t = math.tan(th)
    bars = []
    k0 = int(math.floor((miny - D * t - y0) / dv)) - 1
    k1 = int(math.ceil((maxy + D * t - y0) / dv)) + 1
    for k in range(k0, k1 + 1):
        c = y0 + k * dv
        for sgn in (1, -1):
            bars.append(LineString([(-D, c - sgn * D * t), (D, c + sgn * D * t)]).buffer(MESH_RIB / 2, cap_style=2))
    lat = unary_union(bars)
    zone = region.buffer(-RIM, join_style=2)
    cells = zone.difference(lat)
    hw = (MESH_PITCH - MESH_RIB) / math.sin(th)
    hh = (MESH_PITCH - MESH_RIB) / math.cos(th)
    holes = _keep_holes(cells, hw * hh / 2, frac)
    return holes.buffer(-TIP_R, join_style=1).buffer(TIP_R, join_style=1)   # round the acute tips


SLOT_X_PX = (319, 347, 375)                           # fin slot centres (photo px), after the photo's dot columns


def slot_holes(region):
    """vertical fin slots; the outer wall tapers in, so the inner slot runs shorter like the photo's fin columns"""
    minx, miny, maxx, maxy = region.bounds
    zone = region.buffer(-SLOT_RIM, join_style=2)
    w = SLOT_PITCH - SLOT_RIB
    xs = [x for x, _ in mm([(px, 0) for px in SLOT_X_PX])]
    cells = zone.intersection(unary_union([box(x - w / 2, miny - 1, x + w / 2, maxy + 1) for x in xs]))
    return _keep_holes(cells, w * (maxy - miny) * 0.3, HOLE_MIN_FRAC['slots'], min_w=w - 0.04, join=1)


def relief_prim(region, holes):
    ribs = geom.regularize(region, geom.clean(region.difference(holes)), 0.64)
    return dict(kind='geom', color='relief', geom=plain(region), mirror=False,
                relief=dict(type='custom', ribs=plain(ribs)))


def n_holes(M_or_region, ribs=None):
    if ribs is None:
        M = M_or_region
        g = M['relief_region'].difference(M['relief_ribs'])
    else:
        g = M_or_region.difference(ribs)
    return sum(1 for q in geom.polys(g) if q.area > 0.25)


MESH_Y0 = dict(upper=0.75, lower=0.375)      # phases: whole cells (2 staggered rows up, 4 rows low)
BLACK0 = geom.build_maps(SPEC)['black']
_reg = lambda g: geom.clean(geom.clean(g.intersection(BLACK0)).buffer(-0.3).buffer(0.3))
R_UP = _reg(full(UPPER_MESH).difference(BADGE_ZONE))
R_LO = _reg(full(LOWER_MESH))
R_IN_L = _reg(Polygon(mm(INTAKE_MESH)).buffer(0))


def build_relief(dy):
    """relief prims for a (tiny, invisible) vertical phase nudge dy (mm); returns (prims, designed hole count)"""
    h_up = diamond_holes(R_UP, MESH_Y0['upper'] + dy, HOLE_MIN_FRAC['upper'])
    h_lo = diamond_holes(R_LO, MESH_Y0['lower'] + dy, HOLE_MIN_FRAC['lower'])
    h_in = slot_holes(R_IN_L)
    h_in = unary_union([h_in, mirror_x(h_in)])
    R_IN = unary_union([R_IN_L, mirror_x(R_IN_L)])
    out = [relief_prim(R_UP, h_up), relief_prim(R_LO, h_lo), relief_prim(R_IN, h_in)]
    return out, sum(len(geom.polys(h)) for h in (h_up, h_lo, h_in))


# GEOS' mitred buffers in geom.regularize occasionally swallow a whole row of cells; probe the pipeline's own map build
# + min-width repair and nudge the rows by 0.011 mm steps (invisible) until every designed cell survives
for _k in (0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5):
    RELIEF, N_DESIGNED = build_relief(0.011 * _k)
    _M = geom.build_maps(dict(SPEC, prims=prims + RELIEF))
    geom.repair_min_width(_M)
    N_BUILT = n_holes(_M)
    if N_BUILT == N_DESIGNED:
        break
RELIEF_NUDGE = 0.011 * _k
SPEC['prims'] = prims + RELIEF
