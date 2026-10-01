# Lexus LC 500 (URZ100, 2018+) front keychain.
# Reference: ref/sao9314.jpg = Wikimedia Commons "Lexus LC 500h SAO 2016 9314.jpg" (Mario Roberto Duran Ortiz,
# CC BY-SA 4.0, 1920 px thumbnail). LC 500h and LC 500 share the same front fascia. Near straight-on, camera a bit
# above the hood. Traced half = viewer's LEFT (the clearer, slightly wider one), on ref/front_enh.jpg (CLAHE copy).
# Coordinates below are ORIGINAL photo pixels; T() squeezes the hood (rows above Y0) by K because the raised camera
# shows the long LC hood ~2x taller than in a true front elevation. make_ref.py writes ref/front.jpg with the same
# squeeze so overlay.png still lines up.
#
# Design (G80 language, NO LOGOS - plain mesh where the badge sits):
#  black  = slim triangular headlamp units (triple-projector lens), the band around the arrowhead DRL, the huge
#           spindle grille, the vertical corner slots under the lamps, the lower lip under the grille's chrome bar.
#  white  = body; the body-colour wedge enclosed by the arrowhead (the LC's "L" lamp signature); the chrome bottom
#           bar of the spindle (white strip between grille and lip).
#  DRL    = one white arrowhead / check-mark: a tapering blade under the lens running inward-down into a solid tip,
#           with the upper arm coming back up along the lamp's inner edge.
#  relief = gradient diamond mesh: zig-zag rows whose spacing grows downwards (small flat diamonds at the top, tall
#           open V's at the bottom, as on the real LC grille) inside a 0.7 mm flat frame; flat lower band.
#  grooves= hood/fender shut lines, hood front edge (lamp -> spindle corner), hood character creases into the
#           spindle corners.
import math
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union

CX, YB, XL = 1036, 1202, 270           # centreline, lowest outline point, body edge (left, widest fender)
S = 80.5 / (2 * (CX - XL))              # mm per px
Y0, K = 520.0, 0.32                     # hood squeeze (rows above Y0)
YS = 0.90                               # mild overall vertical correction for the raised camera


def T(p):
    x, y = p
    return (x, y if y >= Y0 else Y0 - (Y0 - y) * K)


def TT(pts):
    return [T(p) for p in pts]


def mm(p):
    x, y = T(p)
    return ((x - CX) * S, (YB - y) * S * YS)


# low, gently arched cowl line dropping over rounded fender shoulders; sides bulge slightly toward the wheel arches
OUTLINE = [(1036, 290), (850, 292), (700, 296), (600, 302), (530, 312), (480, 328), (430, 356), (385, 392),
           (345, 432), (312, 470), (292, 505), (281, 540), (275, 600), (272, 700), (270, 800), (268, 900),
           (270, 960), (279, 1025), (297, 1070), (330, 1106), (385, 1133), (455, 1150), (520, 1165), (560, 1190),
           (640, 1200), (1036, 1202)]

# headlamp: lens triangle + the band that carries the check-mark DRL
LAMP = [(318, 500), (480, 637), (524, 664), (562, 684), (600, 712), (634, 746), (658, 788), (660, 814),
        (622, 813), (560, 794), (470, 767), (400, 748), (352, 739),
        # dark trim running down the bumper corner into the vertical slot (one black "fang" with the lamp)
        (338, 762), (343, 820), (350, 890), (342, 950), (326, 990), (308, 1000), (304, 950), (301, 850),
        (299, 760), (298, 714), (296, 640), (297, 560), (300, 528)]
# body-colour wedge enclosed by the check mark (between lens, blade and return arm)
WEDGE = [(426, 707), (470, 670), (497, 649), (528, 666), (542, 685), (538, 700), (543, 722), (548, 744),
         (520, 735), (470, 716)]
# check-mark DRL (one white poly): blade top edge -> inner corner -> arm inner edge -> arm top -> arm outer edge ->
# solid tip -> blade bottom edge (tapers from ~0.9 mm outboard to ~1.4 mm and a filled tip)
DRL = [(372, 679), (420, 697), (470, 716), (520, 735), (548, 744), (543, 722), (538, 700), (540, 691),
       (556, 692), (576, 716), (600, 746), (618, 768), (634, 790), (600, 791), (560, 779), (500, 754),
       (440, 728), (372, 699)]

GRILLE = [(1036, 680), (657, 680), (690, 730), (720, 780), (738, 815), (742, 838), (720, 858), (660, 905),
          (600, 958), (560, 1003), (532, 1048), (519, 1085), (525, 1122), (553, 1143), (620, 1150),
          (800, 1153), (1036, 1154)]
# relief zone: grille minus a blunted waist corner, down to just above the chrome bar
MESH_ZONE = [(1036, 680), (657, 680), (690, 730), (720, 780), (735, 818), (728, 845), (660, 905),
             (600, 958), (560, 1003), (532, 1048), (519, 1085), (525, 1122), (553, 1143), (620, 1150),
             (800, 1153), (1036, 1154)]
# lower lip under the chrome bar (white strip ~1.2 mm between, rising with the grille's rounded corners)
LIP = [(1036, 1180), (800, 1179), (620, 1176), (588, 1176), (572, 1186), (566, 1240), (1036, 1240)]

FENDER_LINE = [(486, 296), (455, 385), (425, 455), (400, 520), (386, 578)]
HOOD_EDGE = [(552, 657), (610, 670), (666, 692)]
PROJ = [(333, 566), (370, 598), (408, 630)]
CREASE = [(522, 425), (548, 482), (578, 545), (612, 608), (664, 692)]


# ---------------------------------------------------------------- gradient mesh (custom ribs, mm)
def lerp(a, b, f):
    return a + (b - a) * max(0.0, min(1.0, f))


def chevron_mesh(zone_px, y0=672, y1=1150, P=(3.2, 4.6), h=(1.0, 2.9), g=(1.0, 1.2), rib=(0.85, 1.0),
                 gap=0.9, margin=1.0, min_area=1.2, keep=0.55):
    """Rows of separate down-pointing V elements: small flat tabs at the top growing into tall open V's at the
    bottom (the LC 'gradient' grille). Rows alternate half a pitch; everything is clipped to the zone shrunk by
    `margin` and slivers below `min_area` are dropped."""
    half = [mm(p) for p in zone_px]
    zone = unary_union([Polygon(half), Polygon([(-x, y) for x, y in half])]).buffer(0.01).buffer(-margin, join_style=2)
    y_top, y_bot = mm((CX, y0))[1], mm((CX, y1))[1]
    parts, y, k = [], y_top, 0
    while y - lerp(*h, (y_top - y) / (y_top - y_bot)) > y_bot - 0.8:
        f = (y_top - y) / (y_top - y_bot)
        Pk, hk, gk, rk = lerp(*P, f), lerp(*h, f), lerp(*g, f), lerp(*rib, f)
        a = Pk / 2 - gap / 2 - rk * 0.45          # half width of a V (leaves `gap` between neighbours)
        ph = (k % 2) * Pk / 2
        n = int(45 / Pk) + 2
        for i in range(-n, n + 1):
            cx = i * Pk + ph
            v = LineString([(cx - a, y), (cx, y - hk), (cx + a, y)])
            el = v.buffer(rk / 2, cap_style=2, join_style=2, mitre_limit=2.5)
            cut = el.intersection(zone)
            if cut.area < el.area - 1e-6:            # clipped by the frame: round off slivers
                cut = cut.buffer(-0.33).buffer(0.33).simplify(0.02)
            if cut.area >= keep * el.area:           # drop elements the frame would chop to stubs
                parts.append(cut)
        y -= hk + gk
        k += 1
    ribs = unary_union(parts)
    geoms = getattr(ribs, 'geoms', [ribs])
    return unary_union([q for q in geoms if q.area >= min_area])


MESH = dict(type='custom', ribs=chevron_mesh(MESH_ZONE))
WEDGE_WHITE = True

prims = [
    dict(kind='stroke', color='groove', width=0.65, pts=TT(FENDER_LINE), smooth=1),
    dict(kind='stroke', color='groove', width=0.65, pts=TT(CREASE), smooth=1),
    dict(kind='stroke', color='groove', width=0.65, pts=TT(HOOD_EDGE), smooth=1),
    dict(kind='poly', color='black', pts=TT(LAMP)),
    *([dict(kind='poly', color='white', pts=TT(WEDGE), offset=-0.7)] if WEDGE_WHITE else []),
    dict(kind='poly', color='black', pts=TT(DRL), offset=0.7),     # 0.7 mm black halo round the DRL
    dict(kind='poly', color='white', pts=TT(DRL)),
    *[dict(kind='ring', color='white', c=T(c), r_mm=1.0, width=0.5) for c in PROJ],
    dict(kind='poly', color='black', pts=TT(GRILLE)),
    dict(kind='poly', color='relief', pts=TT(MESH_ZONE), relief=MESH),
    dict(kind='poly', color='black', pts=TT(LIP)),
]

SPEC = dict(
    id='lexus_lc500', name='Lexus LC 500 (URZ100)',
    ref='kc/cars/lexus_lc500/ref/front.jpg',
    units='px', px_left=XL, px_right=2 * CX - XL, px_bottom=YB, center_x=CX, y_scale=YS,
    outline_half=TT(OUTLINE), outline_smooth=1,
    prims=prims,
    badge=None,
    tab=dict(y_frac=0.57),
)
