# Lamborghini Urus front keychain - revision round 2.
# Generation: the ORIGINAL (pre-facelift) Urus, 2018-2022 - no bonnet vents, body-colour intake blades, three
# body-colour posts in the lower intake. NOT the Urus S / Performante (revised bumper, vented bonnet): do not add
# their cues.
#
# Reference: Wikimedia Commons "Lamborghini Urus front view dllu.jpg" (Dllu, CC BY-SA 4.0), downloaded as the
# 3840 px Commons thumbnail (ref/dllu_3000.jpg) and cropped to the car (ref/front.jpg = crop 700,1000,3140,2350).
# Straight-on, level (splitter / hood edge level to ~1 px), camera a little above headlight height.
# All coordinates below are pixels of ref/front.jpg; the viewer's LEFT half is traced and mirrored.
# Centreline x = 1217 (badge tip + hood chevron peak).
# The DRLs are off in that photo; the Y light signature (long bar along the lower lens + an upper arm to the
# outer top corner + a lower fork to the outer bottom corner) follows the unlit light guide visible in it, and its
# proportions were checked against a lit Urus S press view (ref/thumbs/cw_hl.png, used for the DRL shape only).
#
# Badge: the library 'shield' is not used (badge=None). A Lamborghini crest (black shield, white inner outline for
# the gold rim, black field) is drawn here as the LAST prims. Switch it off with SHOW_BADGE = False.
import os
import sys

from shapely import affinity
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import geom as _geom                 # read-only use of the pipeline's own helpers (polys / clean)

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):   # badge-free export, no edit
    SHOW_BADGE = False

CX = 1217.0
HALF = 1113.0                       # centreline -> widest body point (left fender side at x = 104)
PL, PR = CX - HALF, CX + HALF
YB = 1222.0                         # splitter bottom (lowest outline point)
S = 80.5 / (PR - PL)                # mm per px (outline is exactly 80.5 mm wide -> pipeline scale k = 1)


def _mm(p):
    x, y = p
    return ((x - CX) * S, (YB - y) * S)


def _mmp(pts):
    return [_mm(p) for p in pts]


def _mx(pts):
    return [(2 * CX - x, y) for x, y in pts]


def _ribs(lines, w):
    """custom relief ribs (mm, final keychain frame) from px polylines, both halves"""
    g = []
    for pts in lines:
        for q in (pts, _mx(pts)):
            g.append(LineString([_mm(p) for p in q]).buffer(w / 2, cap_style=1, join_style=1))
    return unary_union(g)


def _stroke(pts, w, cap=1, join=1):
    return LineString(_mmp(pts)).buffer(w / 2, cap_style=cap, join_style=join)


def _sym(g):
    return unary_union([g, affinity.scale(g, xfact=-1, yfact=1, origin=(0, 0))])


# ------------------------------------------------------------------ body outline (left half)
# top = hood rear edge at the windscreen base (slight crown), A-pillar corner, round fender down to the side,
# near-vertical side, bumper corner chamfered into the black lower bumper / splitter (tyres excluded)
OUTLINE = [(CX, 87), (1100, 88), (1000, 89), (900, 90), (800, 92), (700, 94), (600, 98), (500, 104), (400, 110),
           (335, 115), (308, 121), (284, 139), (258, 165), (233, 196), (210, 224), (190, 250), (172, 275),
           (156, 302), (140, 332), (127, 365), (118, 402), (111, 440), (106, 480), (104, 530), (104, 640),
           (106, 720), (108, 800), (110, 870), (109, 940), (106, 1000), (106, 1040), (108, 1078), (115, 1108),
           (130, 1133), (155, 1150), (180, 1170), (202, 1196), (224, 1215), (252, 1222), (CX, 1222)]
OUTLINE_MM = Polygon(_mmp(OUTLINE) + [(-x, y) for x, y in reversed(_mmp(OUTLINE))]).buffer(0)

# ------------------------------------------------------------------ headlight + Y DRL
# lower outer corner pushed ~5 px out (inside the thick dark bezel of the photo) so the Y fork keeps >= 0.6 mm black
HEADLIGHT = [(238, 313), (300, 320), (400, 337), (500, 357), (600, 379), (671, 399), (642, 432), (603, 472),
             (588, 485), (392, 479), (346, 487), (290, 483), (250, 478), (222, 464), (213, 437), (213, 400),
             (219, 360), (228, 332)]
DRL_W = 0.7
Y_J = (276, 422)                                   # junction of the Y (outer end of the long bar)
# upper arm + long bar as ONE stroke with a mitred corner (sharp outer point of the Y), flat-cut ends like the
# real light guides; the fork runs down/outward to the lens's outer bottom corner (~1.4 mm, 45 deg)
DRL_L = [(254, 340), Y_J, (420, 445), (570, 457)]
DRL_TAIL = [Y_J, (248, 449)]

# ------------------------------------------------------------------ lower front
# one black mouth: side intakes + upper grille + lower centre intake + corner pods + black lower bumper
MOUTH = [(1230, 563), (765, 563), (683, 612), (600, 601), (500, 591), (380, 581), (262, 575), (240, 579),
         (218, 592), (208, 612), (198, 650), (188, 700), (178, 760), (168, 820), (160, 870), (154, 910),
         (156, 945), (166, 972), (173, 1003), (152, 1044), (100, 1040), (60, 1050), (60, 1300), (1230, 1300)]
# body-colour "Y" frame: horizontal bar across the nose, 45 deg legs down to the lower corners
FRAME = [(1230, 756), (620, 756), (602, 766), (398, 952), (384, 956), (140, 956), (140, 1001), (402, 1000),
         (414, 994), (620, 791), (636, 790), (1230, 790)]
BLADE_W = 0.62
BLADE_TOP = [(242, 641), (560, 660), (686, 604)]   # eyebrow blade, rises into the body tooth
Y1 = [[(214, 730), (390, 746), (412, 762)], [(206, 777), (372, 784), (412, 762)], [(412, 762), (615, 768)]]
Y2 = [[(196, 830), (328, 843), (345, 857)], [(190, 877), (300, 882), (345, 857)], [(345, 857), (508, 860)]]


def _junction_fills(r=0.32, win=(-41.0, 9.0, -18.5, 24.5), min_ext=0.25):
    """White fillets where the intake blades meet each other / the frame / the body: black wedges narrower than
    2r (fork crotches, blade-to-leg and blade-to-tooth junctions) become body colour, so every black slot ends
    bluntly at >= 0.6 mm instead of tapering to nothing (like the solid junction pieces of the real blades).
    Morphological closing of the body-colour parts, kept only inside the side-intake window (left half, mm)."""
    white = [OUTLINE_MM.difference(Polygon(_mmp(MOUTH)).buffer(0)), Polygon(_mmp(FRAME)).buffer(0),
             _stroke(BLADE_TOP, BLADE_W)] + [_stroke(a, BLADE_W) for a in Y1 + Y2]
    w = unary_union(white)
    closed = w.buffer(r, join_style=1).buffer(-r, join_style=1)
    add = closed.difference(w).intersection(box(*win))
    keep = []
    for p in _geom.polys(add):
        b = p.bounds
        if max(b[2] - b[0], b[3] - b[1]) >= min_ext and p.area > 0.004:
            keep.append(p)
    return unary_union(keep)


JUNCTION_FILLS = _junction_fills()

# lower centre intake: body-colour bottom bar with three posts (posts ~1.1 mm like the photo, flared feet)
LOW_BAR = [(485, 1086), (1230, 1086)]
POST = [(837, 970), (867, 970), (869, 1060), (884, 1086), (820, 1086), (835, 1060)]
POST_C = [(1202, 970), (1230, 970), (1230, 1086), (1188, 1086), (1201, 1060)]

# radiator windows behind the posts: plain deeper pockets (the real radiator mesh is too fine to print)
RADIATOR = [(800, 970), (1230, 970), (1230, 1080), (800, 1080)]
# upper grille: large elongated hexagon frames (custom relief ribs, px polylines of the left half)
GRILLE = [(1230, 560), (768, 560), (690, 610), (598, 682), (610, 745), (620, 760), (1230, 760)]
RIB_W = 0.9
GRILLE_RIBS = [
    [(925, 560), (958, 624)],                                  # cell 1 upper-right edge
    [(698, 604), (722, 662), (890, 667), (958, 624), (1125, 628)],   # cell 1 left/bottom, cell 2 top
    [(600, 700), (722, 662)],                                  # cell 4 upper-left edge
    [(890, 667), (910, 713), (1129, 713)],                     # cell 2 lower-left + bottom
    [(910, 713), (846, 760)],                                  # cell 4 lower-right edge
    # centre camera housing: big camera hexagon over a smaller sensor hexagon, pinched waist between them
    [(1152, 560), (1125, 628), (1148, 683), (1127, 716), (1146, 760)],
    [(1148, 683), (CX, 683)],                                  # waist divider (camera / sensor)
]


def _grille_ribs():
    """The hex-frame ribs, cleaned like the library patterns (geom.regularize): rib slivers and gap wedges narrower
    than 0.64 mm where a rib meets the recess wall at a shallow angle are merged away."""
    region = _sym(Polygon(_mmp(GRILLE)).buffer(0).intersection(Polygon(_mmp(MOUTH)).buffer(0)))
    region = region.intersection(OUTLINE_MM).difference(_sym(unary_union([
        Polygon(_mmp(FRAME)).buffer(0), _stroke(BLADE_TOP, BLADE_W), JUNCTION_FILLS])))
    ribs = _geom.regularize(region, _ribs(GRILLE_RIBS, RIB_W).intersection(region), 0.64)
    gaps = region.difference(ribs)                     # cell tips still narrower than 0.64 mm become rib
    r = 0.32
    wide = gaps.buffer(-r, join_style=1).buffer(r, join_style=1)
    return _geom.clean(unary_union([ribs, region.difference(wide.buffer(0.01)).intersection(region)]))

# ------------------------------------------------------------------ engraved lines
G = 0.62
CHEVRON = [(668, 400), (1095, 405), (CX, 368)]                   # hood front edge (V at the centre)
# hood / fender shut line: up from the lamp corner, curving towards the A-pillar but kept >= 0.6 mm of body colour
# away from the chamfered outline corner and ending ~1 mm below the cowl edge (no knife-edge sliver, no notch)
HOOD_SIDE = [(262, 318), (258, 285), (258, 245), (263, 210), (277, 188), (300, 168), (330, 150)]
# hood crease (stops ~1 mm below the cowl edge) -> lamp tip -> nose facet line down to the grille's top corner:
# with the chevron it frames the hexagonal centre nose panel around the badge
CREASE = [(762, 558), (716, 478), (668, 402), (645, 330), (630, 280), (618, 230), (607, 170), (600, 128)]


def _groove_fills(r=0.3, wins=((-21.5, 28.0, -18.5, 31.5),), min_ext=0.15):
    """Groove-coloured nodes where grooves meet the lamp tip at acute angles: white-cap wedges narrower than 2r
    (between the crease, the chevron and the lens) are engraved too, so the production cap has no knife edges."""
    black = unary_union([Polygon(_mmp(HEADLIGHT)).buffer(0), Polygon(_mmp(MOUTH)).buffer(0)])
    grooves = unary_union([_stroke(CHEVRON, G), _stroke(CREASE, G), _stroke(HOOD_SIDE, G)])
    cap = OUTLINE_MM.difference(black).difference(grooves)
    opened = cap.buffer(-r, join_style=1).buffer(r, join_style=1)
    thin = cap.difference(opened.buffer(0.005))
    keep = []
    for wb in wins:
        for p in _geom.polys(thin.intersection(box(*wb))):
            b = p.bounds
            if max(b[2] - b[0], b[3] - b[1]) >= min_ext and p.area > 0.002:
                keep.append(p.buffer(0.01))
    return unary_union(keep)


GROOVE_FILLS = _groove_fills()

# ------------------------------------------------------------------ Lamborghini crest (custom badge, see top)
# photo crest: 2.75 x 2.4 mm, top corners y 428, tip y 492 (the nose surface slopes back, so it looks squat).
# Drawn 3.7 x 3.8 mm (between the squat photo view and the true, slightly tall crest) so the gold rim (white) and
# a ~1.5 x 1.2 mm black field survive printing; top corners 1.0 mm below the chevron groove, tip 1.5 mm above the
# grille. Full heater-shield sides (the photo crest stays wide to ~60 % of its height, then runs into the point).
BADGE_TOP = 420.0                    # px, y of the crest's top corners
BW, BH, BARC = 3.7, 3.7, 0.12        # mm: width, corner-to-tip height, arch of the top edge
RIM, BAND = 0.55, 0.55               # mm: black rim, white inner outline (the gold rim); the rest is the black field
# side profile, (x / half width, depth / height), top corner -> tip
CREST_PROFILE = [(1.0, 0.0), (1.0, 0.2), (0.97, 0.42), (0.86, 0.6), (0.64, 0.77), (0.34, 0.91), (0.0, 1.0)]


def _crest():
    cx, cy = _mm((CX, BADGE_TOP))
    a = BW / 2
    right = [(cx + a * u, cy - BH * v) for u, v in CREST_PROFILE]
    left = [(2 * cx - x, y) for x, y in reversed(right[:-1])]
    top = [(cx - 0.5 * a, cy + 0.75 * BARC), (cx, cy + BARC), (cx + 0.5 * a, cy + 0.75 * BARC)]
    sh = Polygon(top[1:] + right + left + top[:1]).buffer(0)
    return sh, sh.buffer(-RIM, join_style=2), sh.buffer(-(RIM + BAND), join_style=2)


CREST = _crest()

prims = [
    dict(kind='poly', color='black', pts=HEADLIGHT),
    dict(kind='stroke', color='white', width=DRL_W, pts=DRL_L, cap='flat', join=2),
    dict(kind='stroke', color='white', width=DRL_W, pts=DRL_TAIL, cap='flat'),
    dict(kind='poly', color='black', pts=MOUTH),
    dict(kind='poly', color='relief', pts=GRILLE, relief=dict(type='custom', ribs=_grille_ribs())),
    dict(kind='poly', color='white', pts=FRAME),
    dict(kind='stroke', color='white', width=BLADE_W, pts=BLADE_TOP),
]
for arm in Y1 + Y2:
    prims.append(dict(kind='stroke', color='white', width=BLADE_W, pts=arm))
prims += [
    dict(kind='geom', color='white', geom=JUNCTION_FILLS),
    dict(kind='poly', color='relief', pts=RADIATOR, relief=dict(type='none')),
    dict(kind='stroke', color='white', width=0.75, pts=LOW_BAR),
    dict(kind='poly', color='white', pts=POST),
    dict(kind='poly', color='white', pts=POST_C),
    dict(kind='stroke', color='groove', width=G, pts=CHEVRON),
    dict(kind='stroke', color='groove', width=G, pts=HOOD_SIDE),
    dict(kind='stroke', color='groove', width=G, pts=CREASE),
    dict(kind='geom', color='groove', geom=GROOVE_FILLS),
]
if SHOW_BADGE:
    # painted last like the library badge: black crest, white inner outline (gold rim), black field
    prims += [
        dict(kind='geom', color='black', geom=CREST[0], mirror=False),
        dict(kind='geom', color='white', geom=CREST[1], mirror=False),
        dict(kind='geom', color='black', geom=CREST[2], mirror=False),
    ]

SPEC = dict(
    id='lambo_urus', name='Lamborghini Urus',
    ref='kc/cars/lambo_urus/ref/front.jpg',
    units='px', px_left=PL, px_right=PR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    outline_smooth=0,
    prims=prims,
    badge=None,          # library 'shield' not used; the crest is the last three prims (SHOW_BADGE above)
    badge_on=False,
    tab=dict(y_frac=0.60),
)
