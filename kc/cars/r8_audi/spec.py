# Audi R8 V10 (Type 4S facelift, 2019+) - front keychain, same design language as the user's G80 M3.
# Reference: Audi MediaCenter press photo A1812863 (R8 production, Boellinger Hoefe, 2018), cropped to the car
# (kc/cars/r8_audi/ref/front.jpg = original px 640..1880 x 480..1300 of the 2500x1667 web_2880 file).
# Traced on the RIGHT half of the photo (the left front wheel is being fitted and hides the left fender), mirrored.
# DRL signature read from the lit grey car (Audi press photo A1812864, ref/cand/audi69455.jpg).
# Revision 1: DRL comb (inner scythe + bar + outer scythe + curved outer leg), curved hood shut lines, sturdier white
# bridges (rings/slot, grille/splitter, air-curtain rails), blunted knife-edge tips.
# Revision 2 (line consistency / bulk print time): ONE honeycomb for grille and side intakes - regular flat-top hex,
# pitch 3.2 mm, rib 0.8 mm (the line's cell size; the photo's grille lattice autocorrelates to a 43 px = 3.3 mm row
# pitch). Built here as a 'custom' relief: a 1.0 mm rim rib lines every pocket wall (the real grille / intake frame is
# ~0.6-1.2 mm), and every part-cell against the rim smaller than FOLD_A mm2 or narrower than FOLD_W mm is folded into
# the rib, so no cut part-cell narrower than 0.9 mm is left at any wall. Grille lattice symmetric about the centreline
# and phased so the top and bottom walls cut one column parity exactly at half-cell; intake phase swept for the most
# full cells. Relief rib perimeter 985 -> 840 mm, production black 20m50s -> 17m10s.
import math, os, sys
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

_LIB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import geom as _g

CX = 614
FRAME = dict(units='px', px_left=95, px_right=1133, px_bottom=707, center_x=CX)
# body silhouette: windshield base -> fender crest -> body side -> splitter
OUTLINE = [(CX, 276), (800, 276), (960, 278), (1000, 283), (1040, 291), (1068, 302), (1088, 318),
           (1102, 340), (1112, 365), (1120, 395), (1127, 430), (1131, 470), (1133, 520), (1132, 580),
           (1128, 630), (1125, 660), (1120, 678), (1112, 690), (1095, 697), (1000, 701), (860, 704), (CX, 707)]
TAB = dict(y_mm=16.8)

GRILLE = [(600, 487), (838, 487), (921, 532), (915, 560), (867, 678), (600, 678)]
INTAKE = [(992, 533), (1086, 507), (1093, 507), (1095, 514), (1083, 600), (1076, 642), (940, 648)]

# ---- unified honeycomb (keychain mm) -------------------------------------------------------------------------------
HEX_P, HEX_RIB, RIM = 3.2, 0.8, 1.0     # cell pitch (flat to flat, centre spacing), wall, rim rib along the pocket wall
FOLD_A, FOLD_W = 1.0, 0.9               # part-cells smaller than this (mm2) or narrower than this (mm) become rib

_F = _g.Frame(FRAME)
_M0 = _g.build_maps(dict(FRAME, outline_half=OUTLINE, outline_smooth=1, prims=[], tab=TAB))
_DY, _K = _M0['place']


def _region(pts):
    """px polygon -> keychain mm exactly as the pipeline places it (incl. its width re-scale), clipped to the body."""
    g = affinity.translate(Polygon(_F.pts(pts)).buffer(0), 0, _DY)
    g = affinity.scale(g, _K, _K, origin=(0, 0)) if _K != 1.0 else g
    return _g.clean(g.intersection(_M0['outline']))


def hex_ribs(reg, x0=0.0, y0=0.0, pitch=HEX_P, rib=HEX_RIB, rim=RIM):
    """Rib geometry of a flat-top honeycomb inside `reg` (mm): cells only inside the wall inset by `rim`, small or
    thin part-cells folded into the rib, then made a fixed point of the pipeline's 0.64 mm regularize."""
    a = pitch / math.sqrt(3)
    dx = 1.5 * a
    minx, miny, maxx, maxy = reg.bounds
    cells = []
    for i in range(int((minx - x0) / dx) - 2, int((maxx - x0) / dx) + 3):
        for j in range(int((miny - y0) / pitch) - 2, int((maxy - y0) / pitch) + 3):
            x, y = x0 + i * dx, y0 + j * pitch + (pitch / 2 if i % 2 else 0)
            h = Polygon([(x + a * math.cos(math.radians(60 * q)), y + a * math.sin(math.radians(60 * q)))
                         for q in range(6)])
            cells.append(h.buffer(-rib / 2, join_style=2))
    holes = unary_union(cells).intersection(reg.buffer(-rim, join_style=2))
    keep = [h for h in _g.polys(holes) if h.area >= FOLD_A and not h.buffer(-FOLD_W / 2).is_empty]
    ribs = reg.difference(unary_union(keep))
    for _ in range(2):
        ribs = _g.regularize(reg, ribs, 0.64)
    return ribs


_GR = _region(GRILLE)
_GR = _g.clean(unary_union([_GR, _g.mirror_x(_GR)]))
GRILLE_RIBS = hex_ribs(_GR, x0=0.0, y0=1.65)                     # lattice symmetric about the centreline
_IN = _region(INTAKE)                                            # right intake; ribs mirrored to the left one
_IR = hex_ribs(_IN, x0=1.0, y0=0.8)
INTAKE_RIBS = _g.clean(unary_union([_IR, _g.mirror_x(_IR)]))

SPEC = dict(
    id='r8_audi', name='Audi R8 V10 (4S facelift)',
    ref='kc/cars/r8_audi/ref/front.jpg',
    **FRAME,
    outline_half=OUTLINE,
    outline_smooth=1,
    prims=[
        # ---- engraved hood shut lines (windshield corner -> headlight top, gently curved like the real panel gap);
        #      painted first so the headlight black clips the lower end
        dict(kind='stroke', color='groove', width=0.62, smooth=1,
             pts=[(995, 270), (972, 320), (957, 355), (945, 385), (932, 415), (918, 456)]),
        # ---- headlight unit (slim wedge, inner end squared off to a 0.6 mm flat instead of a knife edge)
        dict(kind='poly', color='black', pts=[(846, 462), (900, 450), (960, 434), (1020, 418), (1082, 401), (1092, 407),
                                              (1097, 425), (1097, 463), (1085, 471), (1060, 481), (1000, 496),
                                              (945, 508), (900, 491), (846, 470)]),
        # ---- DRL (4S facelift): top blade over the full lamp length that bends down at the outer end (reads as the
        #      outermost blade), with a comb hanging from it: outer scythe, straight vertical bar, inner scythe
        dict(kind='stroke', color='white', width=0.7, smooth=2, pts=[(886, 468), (1062, 422), (1076, 432), (1082, 454)]),
        dict(kind='stroke', color='white', width=0.78, smooth=2, pts=[(1028, 431), (1043, 443), (1052, 455), (1055, 468)]),
        dict(kind='stroke', color='white', width=0.7, pts=[(1008, 437), (1009, 470)]),
        dict(kind='stroke', color='white', width=0.78, smooth=2, pts=[(962, 448), (978, 458), (988, 470), (993, 483)]),
        # ---- facelift: three slim slots between the hood and the grille
        dict(kind='poly', color='black', pts=[(600, 463), (683, 463), (686, 469), (683, 475), (600, 475)]),
        dict(kind='poly', color='black', pts=[(703, 463), (825, 464), (825, 471), (809, 476), (703, 475), (700, 469)]),
        # ---- single-frame grille: unified honeycomb (pitch 3.2 / rib 0.8, rim rib on the frame, no small part-cells)
        dict(kind='poly', color='black', pts=GRILLE, relief=dict(type='custom', ribs=GRILLE_RIBS)),
        # ---- side intake (same honeycomb as the grille) and the slim outer air-curtain slot
        dict(kind='poly', color='black', pts=INTAKE, relief=dict(type='custom', ribs=INTAKE_RIBS)),
        dict(kind='poly', color='black', pts=[(1104, 524), (1113, 522), (1113, 650), (1095, 650)]),
        # ---- splitter (black lip, deeper at the corners)
        dict(kind='poly', color='black', pts=[(600, 694), (880, 693), (960, 684), (1040, 674), (1100, 668), (1118, 672),
                                              (1140, 690), (1140, 720), (600, 720)]),
    ],
    badge=dict(type='rings', c=(CX, 431), d=3.2, ring_r=1.45, w=0.6, colour='black'),
    tab=TAB,
)
