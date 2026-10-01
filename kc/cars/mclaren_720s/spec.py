# McLaren 720S (2017-2023) front keychain.  (revision 1)
# Reference: ref/front.jpg = McLaren Automotive studio press photo (silver 720S, doors up, straight-on, camera at
# headlight height, perfectly centred and level), 1600x1062, via supercars.net gallery. See ref/SOURCE.txt.
# Traced half = viewer's LEFT. Coordinates are photo pixels of ref/front.jpg (1 mm = 10.43 px). Body 80.5 x 28.4 mm.
#
# Design (G80 language):
#  outline  - cowl/windscreen base (flat, y 510) to the splitter bottom; soft clamshell shoulder at the top corners,
#             fender sides straight down; tyres, doors and mirrors dropped. The lower bumper corners stay white, the
#             black splitter runs the full width.
#  black    - the two "eye sockets" (short fat teardrops wrapping lamp + duct, traced on the hard rim), the two hood
#             nostrils (short comma-shaped slots = the real dark openings only), the lower mouth (two outer voids +
#             carbon centre section), the splitter, the McLaren speedmark.
#  white on black (light signature) - inside each socket: the headlamp lens as a 0.65 mm outline following the
#             socket top and closing into a blunt tip, and below it the LED DRL blade that droops ~7 deg into the
#             socket tip (0.9 -> 0.58 mm taper); the two white fins ("whiskers", 0.9 mm) that split the mouth into
#             outer voids and the carbon centre, and a 0.8 mm white lip between mouth and splitter (silver bezel).
#  relief   - no rib patterns (the 720S has no grille/mesh at the front); the real openings are one step deeper:
#             the socket duct below the DRL and the two outer mouth voids are plain relief pockets (type 'none'),
#             both inside a 0.7 mm black rim.
#  grooves  - 0.62 mm: the front-clamshell shut line (fender edge -> over the socket -> across the nose, one big U
#             when mirrored). The hood crease is switched off (see CREASE).
#  tab      - viewer's left, y_frac 0.60 (white fender beside the socket).
import os, sys
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):   # badge-free export, no edit
    SHOW_BADGE = False

CX, YB, XL = 800, 806, 380
XR = 2 * CX - XL
S = 80.5 / (XR - XL)               # mm per px


def mm(p):
    return ((p[0] - CX) * S, (YB - p[1]) * S)


def P(pts, smooth=0):
    q = [mm(p) for p in pts]
    if smooth:
        q = geom.chaikin(q, smooth, closed=True)
    return Polygon(q).buffer(0)


def L(pts, w, smooth=0, cap=1):
    q = [mm(p) for p in pts]
    if smooth:
        q = geom.chaikin(q, smooth, closed=False)
    return LineString(q).buffer(w / 2, cap_style=cap, join_style=1)


def taper_q(q, widths, smooth=0):
    """stroke whose width (mm) varies along a centreline given in mm; round ends"""
    import numpy as np
    w = list(widths)
    if smooth:
        n0 = len(q)
        q = geom.chaikin(q, smooth, closed=False)
        t0 = np.linspace(0, 1, n0); t1 = np.linspace(0, 1, len(q))
        w = list(np.interp(t1, t0, w))
    parts = []
    for (a, ra), (b, rb) in zip(zip(q, w), zip(q[1:], w[1:])):
        parts.append(unary_union([Point(a).buffer(ra / 2, 32), Point(b).buffer(rb / 2, 32)]).convex_hull)
    return unary_union(parts)


def taper(pts, widths, smooth=0):
    """taper_q with the centreline in photo px"""
    return taper_q([mm(p) for p in pts], widths, smooth)


def opened(g, r):
    """remove every part of g narrower than 2r (mitre-free round opening), keep the rest exactly"""
    return geom.clean(g.buffer(-r).buffer(r).intersection(g))


# ------------------------------------------------------------------ outline
# top corner = the soft clamshell shoulder measured on the photo (y 511 @ x420, 518 @ 410, 527 @ 400, 535 @ 390,
# 549 @ 385); bottom edge = one smooth splitter line (no kink)
OUTLINE = [(800, 510), (600, 510), (470, 511), (435, 511), (421, 511.5), (413, 515), (406, 520.5), (400, 526.5),
           (394, 532.5), (389, 539.5), (385.5, 548), (383.5, 557), (381.5, 569), (380, 585), (380, 700), (380, 770),
           (380, 786), (380, 795), (382, 797.6), (386, 798.6), (392, 799), (470, 799.8), (530, 802), (600, 804.5),
           (680, 805.7), (800, 806)]

# ------------------------------------------------------------------ eye socket (headlamp + intake duct)
# traced on the hard socket rim (not the soft shadow on the paint above it); inner apex on the rim at ~(583,640)
SOCKET = [(405, 605), (406, 585), (410, 568), (419, 559), (433, 554.5), (452, 555), (476, 562.5), (500, 574.5),
          (524, 587), (548, 602.5), (565, 615.5), (578, 628.5), (589, 641), (580, 646), (566, 650.5), (540, 657),
          (500, 668), (465, 673), (442, 673), (425, 666), (413, 652), (407, 632)]
LENS_INSET = 0.75          # mm of black socket rim above / beside the headlamp lens
LENS_RING = 0.65           # mm white lens outline
LENS_BOTTOM = [(380, 601), (560, 601)]       # lens lower edge (px), cut line
# LED DRL blade, measured centreline (420,620)-(468,626)-(500,630)-(518,632): droops ~7 deg into the socket tip
DRL = [(415, 615), (470, 621), (500, 625), (521.5, 627.8), (518.5, 634), (500, 632.2), (470, 629.2), (415, 624.5)]
LED_DOTS = []             # lit LED projector modules (white dots) - off: one dot reads as a pupil, two do not fit
LED_R = 0.5                # mm

# ------------------------------------------------------------------ hood vent (nostril): the dark opening only
VENT_C = [(551, 525), (572, 533), (590, 542), (605, 551), (620, 561)]     # vent centreline (px)
VENT_W = [0.6, 0.95, 1.2, 1.15, 0.65]                                  # width along it (mm)

# ------------------------------------------------------------------ lower intake (mouth) + fin + splitter
MOUTH = [(478, 778), (467, 766), (463, 752), (470, 738), (486, 724), (507, 713), (535, 706), (565, 704),
         (605, 707), (650, 712), (700, 717), (760, 720), (800, 721), (860, 721), (860, 774), (800, 774),
         (700, 774), (600, 775), (540, 776)]
FIN = [(538, 697), (570, 707.5), (608, 717), (643, 732), (668, 751), (684, 767), (689, 778)]
FIN_W = 0.9
VOID_ROUND = 1.0           # mm: corner rounding of the outer voids (smooth flow from mouth top into the fin)
SPLITTER = [(830, 783.5), (700, 782.5), (600, 783.5), (560, 784.5), (520, 786.5), (480, 788.5), (440, 789.5),
            (400, 790), (376, 790), (376, 815), (830, 815)]

# ------------------------------------------------------------------ engraved lines
GW = 0.62
# front-clamshell shut line: from the fender edge over the socket, down past the socket tip, across the nose
HOOD_LINE = [(378, 552), (400, 543), (430, 538), (470, 543), (520, 557), (560, 571), (600, 584), (640, 603),
             (680, 619), (720, 625), (760, 626.6), (800, 627), (840, 626.6)]
# hood crease (lower edge of the nostril channel): OFF. With the nostril cut back to the real dark opening, any
# crease that stays clear of the shut line (>= 0.8 mm) is only a short dash parallel to the vent and reads as a
# second vent; the one-line U (as sparse as the G80's hood lines) reads cleaner. Set e.g.
# [(526, 535), (540, 543.5), (554, 552.5)] to bring a short one back.
CREASE = []


def groove_group():
    out = [dict(kind='geom', color='groove', geom=L(HOOD_LINE, GW, smooth=2))]
    if CREASE:
        out.append(dict(kind='geom', color='groove', geom=L(CREASE, GW, smooth=1)))
    return out


def socket_group():
    sock = P(SOCKET, smooth=2)
    lens = sock.buffer(-LENS_INSET)
    ybot = mm(LENS_BOTTOM[0])[1]
    lens = opened(geom.clean(lens.intersection(box(-60, ybot, 0, 60))), 0.4)   # blunt inner tip
    inner = opened(lens.buffer(-LENS_RING), 0.4)
    drl = opened(P(DRL), 0.26)                                  # round the bevelled inner end (no wedge tip)
    out = [dict(kind='geom', color='black', geom=sock),
           dict(kind='geom', color='white', geom=lens),
           dict(kind='geom', color='black', geom=inner),
           dict(kind='geom', color='white', geom=drl)]
    for c in LED_DOTS:
        out.append(dict(kind='geom', color='white', geom=Point(mm(c)).buffer(LED_R, 48)))
    if DUCT_POCKET:
        # the socket below the DRL is the air duct: one step deeper than the lamp, inside a DUCT_RIM carbon rim,
        # and at least DUCT_RIM below the DRL blade
        (ax, ay), (bx, by) = mm(DUCT_TOP[0]), mm(DUCT_TOP[1])
        below = Polygon([(ax, ay), (bx, by), (bx, -5), (ax, -5)])
        duct = geom.clean(sock.buffer(-DUCT_RIM).intersection(below).difference(drl.buffer(DUCT_RIM)))
        duct = opened(duct, 0.4)
        out.append(dict(kind='geom', color='relief', geom=duct, relief=dict(type='none')))
    return out


DUCT_POCKET = True
DUCT_RIM = 0.7                                # mm
DUCT_TOP = [(380, 628.5), (620, 650)]         # px: pocket top edge, parallel to the DRL's lower edge


def mouth_group():
    m = P(MOUTH, smooth=1)
    fin = L(FIN, FIN_W, smooth=2)
    pieces = geom.polys(opened(m.difference(fin), 0.32))
    xf = mm(FIN[2])[0]
    void = opened(unary_union([q for q in pieces if q.centroid.x < xf]), VOID_ROUND)
    # smooth the crest where the mouth top flows into the fin (no peak): simplify + Chaikin, never grows the void
    v = void.simplify(0.25)
    void = geom.clean(Polygon(geom.chaikin(list(v.exterior.coords)[:-1], 3, closed=True)).buffer(0).intersection(void))
    centre = opened(unary_union([q for q in pieces if q.centroid.x >= xf]), 0.35)
    out = [dict(kind='geom', color='black', geom=unary_union([void, centre]))]
    if VOID_POCKET:
        # the outer voids are real openings (to the low-temperature radiators): one step deeper than the carbon
        # centre section -> plain relief pocket inside the same 0.7 mm black rim as the socket duct
        pocket = opened(geom.clean(void.buffer(-VOID_RIM)), 0.4)
        out.append(dict(kind='geom', color='relief', geom=pocket, relief=dict(type='none')))
    return out


VOID_POCKET = True
VOID_RIM = 0.7

prims = groove_group() + \
        [dict(kind='geom', color='black', geom=taper(VENT_C, VENT_W, smooth=2))] + socket_group() + mouth_group() + \
        [dict(kind='poly', color='black', pts=SPLITTER)]

# ------------------------------------------------------------------ McLaren speedmark
# outline of the official speedmark (work/speedmark.png, Wikimedia Commons "McLaren Speedmark.svg") normalised to
# width 1 (y up); drawn black on the nose just above the shut line where the 720S wears its badge
SPEEDMARK = [(0.9979, 0.4792), (0.9896, 0.5), (0.9646, 0.524), (0.9302, 0.5385), (0.8885, 0.5469), (0.8135, 0.549),
             (0.7698, 0.5458), (0.626, 0.5208), (0.4812, 0.4802), (0.3125, 0.4167), (0.1594, 0.3448), (0.001, 0.2531),
             (0.0729, 0.2771), (0.1552, 0.2979), (0.3125, 0.3219), (0.4365, 0.324), (0.501, 0.3146), (0.5427, 0.301),
             (0.5771, 0.2802), (0.6, 0.2542), (0.6115, 0.224), (0.6125, 0.1865), (0.601, 0.1406), (0.5802, 0.0948),
             (0.5188, 0.001), (0.7302, 0.15), (0.8719, 0.2698), (0.926, 0.326), (0.9698, 0.3833), (0.9948, 0.4365),
             (0.999, 0.4573)]
# the two needle tails are too thin to print at 1:1: redraw them as tapered strokes along their true centrelines
# that end in a 0.56 mm round tip (normalised centreline, width in mm)
TAIL_UP = ([(0.44, 0.394), (0.3125, 0.369), (0.155, 0.320), (0.05, 0.2755)], [1.0, 0.78, 0.64, 0.6])
TAIL_LO = ([(0.655, 0.165), (0.618, 0.10), (0.568, 0.045)], [0.9, 0.68, 0.6])
BADGE_W = 7.5                 # mm
BADGE_GROW = 0.06             # mm
BADGE_GAP = 0.75              # mm of white between the badge and the shut-line groove below it


def speedmark():
    W = BADGE_W
    body = Polygon([(x * W, y * W) for x, y in SPEEDMARK]).buffer(0)
    core = opened(body.buffer(BADGE_GROW), 0.28)
    tails = [taper_q([(x * W, y * W) for x, y in c], w) for c, w in (TAIL_UP, TAIL_LO)]
    sw = geom.clean(unary_union([core] + tails))
    b = sw.bounds
    groove_top = mm((CX, 627))[1] + GW / 2
    return affinity.translate(sw, -(b[0] + b[2]) / 2, groove_top + BADGE_GAP - b[1])


if SHOW_BADGE:
    prims.append(dict(kind='geom', color='black', geom=speedmark(), mirror=False))

SPEC = dict(
    id='mclaren_720s', name='McLaren 720S',
    ref='kc/cars/mclaren_720s/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.60),
    badge_on=SHOW_BADGE,
)
