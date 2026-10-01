# Audi RS 7 Sportback (C8, 2020+) - traced on Audi MediaCenter press photo A233048 (RS 7 Sportback performance,
# straight-on front view; see ref/source.json). Right half (viewer's right, x >= center_x) is traced; all mirrored.
# NO LOGOS: the four-rings spot is left as plain honeycomb grille, badge=None.
import math
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

_PX = dict(px_left=145, px_right=1158, px_bottom=756, center_x=651.5)
_S = 80.5 / (_PX['px_right'] - _PX['px_left'])


def _mm(pts):
    return [((x - _PX['center_x']) * _S, (_PX['px_bottom'] - y) * _S) for x, y in pts]


def _sym(pts):
    p = Polygon(_mm(pts)).buffer(0)
    return unary_union([p, Polygon([(-x, y) for x, y in p.exterior.coords])])


def _honeycomb(region, pitch=2.7, stretch=1.5, rib=0.8, margin=0.6, y0=0.0):
    """Gloss-black RS honeycomb: hexagons pointed left/right, stretched wide, true `rib` mm walls, symmetric about
    x=0; ribs stop `margin` mm short of the recess wall so no slivers form along the slanted flanks."""
    a = pitch / math.sqrt(3)
    dx, dy = 1.5 * a * stretch, pitch
    minx, miny, maxx, maxy = region.bounds
    nx = int(max(abs(minx), abs(maxx)) / dx) + 2
    ny = int((maxy - miny) / dy) + 3
    cells = []
    for i in range(-nx, nx + 1):
        for j in range(-2, ny + 1):
            cx, cy = i * dx, miny + y0 + j * dy + (dy / 2 if i % 2 else 0)
            h = Polygon([(cx + a * stretch * math.cos(math.radians(60 * k)), cy + a * math.sin(math.radians(60 * k)))
                         for k in range(6)])
            cells.append(h.buffer(-rib / 2, join_style=2))
    inner = region.buffer(-margin, join_style=2)
    lattice = box(minx - 5, miny - 5, maxx + 5, maxy + 5).difference(unary_union(cells)).intersection(inner)
    # fold open slivers (< 0.6 mm) between a clipped rib and the wall into the rib, then drop rib slivers/crumbs
    gaps = inner.difference(lattice)
    lattice = unary_union([lattice, gaps.difference(gaps.buffer(-0.31).buffer(0.31, join_style=2))])
    lattice = lattice.buffer(-0.31).buffer(0.31, join_style=2).intersection(inner)
    parts = getattr(lattice, 'geoms', [lattice])
    return unary_union([g for g in parts if g.area >= 0.5])


GRILLE = [(640, 462), (880, 462), (903, 467), (963, 527), (963, 536), (905, 650), (890, 670), (870, 677), (640, 678)]
INTAKE = [(972, 668), (1045, 588), (1092, 528), (1092, 706), (1060, 700), (990, 680)]
GRILLE_MESH = _honeycomb(_sym(GRILLE), y0=0.55)
INTAKE_MESH = _honeycomb(_sym(INTAKE), y0=0.3)

# --- slim HD Matrix headlight: black wedge, sharp inner tip, lower edge tapering into a thin blade ---
LAMP = [(903, 447), (930, 440), (1000, 428), (1060, 416), (1100, 408), (1112, 410), (1119, 422), (1120, 472),
        (1114, 483), (1060, 487), (1000, 486), (965, 477), (936, 464)]
_LAMP = Polygon(LAMP)


def _lamp_bottom(x):
    return max(y for _, y in _LAMP.intersection(Polygon([(x - .01, 0), (x + .01, 0), (x + .01, 999), (x - .01, 999)])).exterior.coords)


# --- laser-light DRL: a thin light bar with a row of short slanted segments hanging from it; outer two step up ---
DRL_W = 0.65
_BAR = ((948, 450.5), (1098, 438.0))            # bar centre line (px): dashes hang from it


def _bar_y(x):
    (x0, y0), (x1, y1) = _BAR
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


DRL = [dict(kind='stroke', color='white', width=DRL_W, pts=list(_BAR))]
for _i, _x in enumerate(range(953, 1098, 16)):          # 10 segments, 16 px (1.27 mm) pitch
    _top = _bar_y(_x) - (14 if _i >= 8 else 0)        # outer two stepped up toward the lamp's top edge
    _bot = min(_bar_y(_x) + 13, _lamp_bottom(_x) - 11.5)
    DRL.append(dict(kind='stroke', color='white', width=DRL_W, pts=[(_x - 2, _bot), (_x + 1, _top)]))

SPEC = dict(
    id='audi_rs7', name='Audi RS 7 Sportback (C8)',
    ref='kc/cars/audi_rs7/ref/front.png',
    units='px', **_PX,
    outline_half=[(651.5, 322), (800, 322), (920, 323), (990, 325), (1010, 331), (1050, 346), (1090, 368),
                  (1125, 389), (1147, 413), (1156, 445), (1159, 490), (1160, 570), (1160, 640), (1157, 690),
                  (1151, 714), (1141, 731), (1120, 745), (1000, 754), (651.5, 756)],
    outline_smooth=1,
    prims=[
        dict(kind='poly', color='black', pts=LAMP),
        *DRL,
        # --- wide low single-frame grille, honeycomb ---
        dict(kind='poly', color='black', pts=GRILLE, relief=dict(type='custom', ribs=GRILLE_MESH)),
        # --- outer intakes (same honeycomb) ---
        dict(kind='poly', color='black', pts=INTAKE, relief=dict(type='custom', ribs=INTAKE_MESH)),
        # outboard air-curtain channel (plain black), separated by a ~1 mm white vertical blade
        dict(kind='poly', color='black', pts=[(1105, 524), (1113, 529), (1120, 580), (1121, 640), (1116, 685),
                                              (1111, 704), (1105, 704)]),
        # --- lower slot under the grille ---
        dict(kind='poly', color='black', pts=[(640, 690), (880, 690), (920, 697), (900, 707), (640, 707)]),
        # --- splitter ---
        dict(kind='poly', color='black', pts=[(640, 722), (1000, 722), (1080, 724), (1118, 724), (1140, 714),
                                              (1175, 700), (1175, 770), (640, 770)]),
        # --- engraved lines: hood front shut line (tip to tip) + two soft hood creases branching off it ---
        dict(kind='stroke', color='groove', width=0.65, pts=[(640, 445), (902, 445)]),
        dict(kind='stroke', color='groove', width=0.65, pts=[(897, 444), (950, 375)]),
    ],
    badge=None,
    tab=dict(y_frac=0.6),
)
