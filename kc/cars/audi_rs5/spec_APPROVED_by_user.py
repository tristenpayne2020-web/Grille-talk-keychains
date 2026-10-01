# Audi RS 5 Coupe (B9.5 facelift, 2020+) - traced on Audi MediaCenter photo A202345 (see ref/source.json).
# Right half (viewer's right, x >= center_x) is traced; everything is mirrored.
# NO LOGOS: the four rings / RS badge spot is left as plain honeycomb grille.
# Revision 1: crisp octagonal single frame, custom flat-top stretched honeycomb (grille + intakes) with a wall margin,
# intake vertical blade, subtle flush round lamp in the mesh, DRL hugging the lamp rim, grooves kept inside the outline.
import math
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

_PX = dict(px_left=50, px_right=1242, px_bottom=571, center_x=646)
_S = 80.5 / (_PX['px_right'] - _PX['px_left'])


def _mm(pts):
    return [((x - _PX['center_x']) * _S, (_PX['px_bottom'] - y) * _S) for x, y in pts]


def _honeycomb(regions_px, cut_mm=None, pitch=2.4, stretch=1.4, rib=0.8, margin=0.45, y0=0.0):
    """Flat-top hexagons (points left/right) stretched horizontally like the RS gloss-black honeycomb.
    Rib walls are a true `rib` mm wide (cells are shrunk after stretching). Ribs stop `margin` mm short of the
    recess wall so no sliver fragments are left along the slanted grille flanks."""
    reg = []
    for pts in regions_px:
        p = Polygon(_mm(pts)).buffer(0)
        q = Polygon([(-x, y) for x, y in p.exterior.coords])
        reg.append(unary_union([p, q]))
    reg = unary_union(reg)
    inner = reg.buffer(-margin, join_style=2)
    if cut_mm is not None:                       # keep ribs off white/flush features painted inside the region
        inner = inner.difference(cut_mm.buffer(margin, join_style=2))
    a = pitch / math.sqrt(3)
    dx, dy = 1.5 * a * stretch, pitch
    minx, miny, maxx, maxy = reg.bounds
    cells = []
    nx = int(max(abs(minx), abs(maxx)) / dx) + 2
    ny = int((maxy - miny) / dy) + 3
    for i in range(-nx, nx + 1):
        for j in range(-2, ny + 1):
            cx = i * dx
            cy = miny + y0 + j * dy + (dy / 2 if i % 2 else 0)
            h = Polygon([(cx + a * stretch * math.cos(math.radians(60 * k)), cy + a * math.sin(math.radians(60 * k)))
                         for k in range(6)])
            cells.append(h.buffer(-rib / 2, join_style=2))
    lattice = box(minx - 5, miny - 5, maxx + 5, maxy + 5).difference(unary_union(cells))
    return lattice.intersection(inner)


GRILLE = [(646, 246), (925, 246), (960, 262), (976, 300), (912, 452), (892, 470), (860, 474), (646, 474)]
INTAKE = [(1072, 377), (1120, 362), (1198, 346), (1212, 352), (1218, 372), (1218, 480), (1210, 494),
          (1150, 495), (1060, 491), (1003, 490)]
BLADE_X, LAMP_C, LAMP_R = 1180, (1114, 431), 33
_cut = []
for _sx in (1, -1):
    _bx = (BLADE_X - 646) * _S * _sx
    _cut.append(box(min(_bx - 0.35 * _sx, 50 * _sx), -1, max(_bx - 0.35 * _sx, 50 * _sx), 40))   # blade + outboard strip stay plain
    _c = _mm([LAMP_C])[0]
    _cut.append(Polygon([(_c[0] * _sx + LAMP_R * _S * math.cos(t / 32 * math.pi), _c[1] + LAMP_R * _S * math.sin(t / 32 * math.pi))
                         for t in range(64)]))
MESH = _honeycomb([GRILLE, INTAKE], cut_mm=unary_union(_cut))

SPEC = dict(
    id='audi_rs5', name='Audi RS 5 (B9.5)',
    ref='kc/cars/audi_rs5/ref/front.jpg',
    units='px', **_PX,
    outline_half=[(646, 61), (900, 60), (1060, 58), (1100, 64), (1150, 90), (1190, 120),
                  (1218, 150), (1234, 185), (1241, 240), (1243, 320), (1243, 420), (1241, 500),
                  (1237, 535), (1232, 556), (1212, 567), (1000, 570), (646, 571)],
    outline_smooth=1,
    prims=[
        # --- headlight unit (black) ---
        dict(kind='poly', color='black', pts=[(958, 236), (990, 220), (1051, 198), (1137, 175), (1176, 166),
                                              (1196, 172), (1207, 190), (1210, 250), (1200, 265), (1180, 272),
                                              (1109, 280), (1040, 278), (1006, 268), (975, 252)]),
        # --- DRL signature: segmented "digital" bar hugging the top rim, longer last bar hooking down ---
        dict(kind='stroke', color='white', width=0.7, cap='flat', pts=[(978, 241), (998, 232.5)]),
        dict(kind='stroke', color='white', width=0.7, cap='flat', pts=[(1007, 229.3), (1028, 221.7)]),
        dict(kind='stroke', color='white', width=0.7, cap='flat', pts=[(1037, 218.5), (1058, 211)]),
        dict(kind='stroke', color='white', width=0.7, cap='flat', pts=[(1067, 208.6), (1088, 203)]),
        dict(kind='stroke', color='white', width=0.7, cap='flat', pts=[(1097, 200.6), (1117, 195.3)]),
        dict(kind='stroke', color='white', width=0.7, pts=[(1127, 192.6), (1164, 184), (1166, 252)]),
        # --- three slim slots under the hood edge (Sport quattro homage) ---
        dict(kind='poly', color='black', pts=[(646, 216), (740, 216), (740, 230), (646, 230)]),
        dict(kind='poly', color='black', pts=[(758, 216), (880, 216), (895, 230), (758, 230)]),
        # --- single-frame grille (crisp octagon), gloss-black honeycomb ---
        dict(kind='poly', color='black', pts=GRILLE, relief=dict(type='custom', ribs=MESH)),
        # --- outer intake: diagonal inner slot + main intake with honeycomb ---
        dict(kind='poly', color='black', pts=[(982, 400), (1032, 395), (976, 481), (952, 482)]),
        dict(kind='poly', color='black', pts=INTAKE, relief=dict(type='custom', ribs=MESH)),
        # vertical blade near the outboard edge of the intake
        dict(kind='stroke', color='white', width=0.7, cap='flat', pts=[(BLADE_X, 336), (BLADE_X, 505)]),
        # round lamp: a flush plain-black disc sitting in the mesh (white first to cut the mesh, then black)
        dict(kind='circle', color='white', c=LAMP_C, r=LAMP_R),
        dict(kind='circle', color='black', c=LAMP_C, r=LAMP_R),
        # --- lower slot + splitter (black) with the lip edge ---
        dict(kind='poly', color='black', pts=[(646, 507), (905, 507), (940, 512), (1000, 522), (1070, 535),
                                              (1130, 545), (1185, 550), (1240, 547), (1260, 547), (1260, 600), (646, 600)]),
        dict(kind='stroke', color='white', width=0.7, cap='flat', smooth=2,
             pts=[(646, 541), (900, 541), (960, 542), (1030, 547), (1085, 553)]),
        # --- engraved lines: hood shut lines + hood creases (start inside the outline) ---
        dict(kind='stroke', color='groove', width=0.62, smooth=2,
             pts=[(905, 236), (940, 197), (990, 145), (1030, 106), (1065, 82), (1080, 74)]),
        dict(kind='stroke', color='groove', width=0.62, smooth=2, pts=[(832, 80), (815, 110), (795, 148), (781, 182), (776, 200)]),
    ],
    badge=None,
    tab=dict(y_frac=0.5),
)
