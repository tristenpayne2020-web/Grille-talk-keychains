# Chevrolet Corvette C8 Stingray (2020+) - front keychain artwork, traced on a straight-on GM press photo.
# Reference: ref/front.jpg (1280x960, GM/Chevrolet press image as republished by NetCarShow). Left half traced
# (viewer's left), mirrored about center_x.
# Revision 1: louvres (intakes + lower grille band only), solid upper grille panel, split intake (upper slot +
# vane), joined DRL hook with a longer blade, raised splitter bottom (no ground/tyre shadow), frunk spine grooves,
# crease kept off the tab root, badge centred on the mirror axis.
# Revision 2: C8 honeycomb mesh (the chevron cells of the real intakes / grille eyes) instead of BMW slats, fender-top
# slit + frunk shut line re-traced lower and flatter (no longer notches the top edge), lighter 0.55 mm grooves,
# crease start and tab moved off each other, wider DRL gaps (fuller lens tip), thicker headlight rim.
# Revision 3: crossed-flags emblem drawn here as the C7/C8 winged V (the library 'flags' shape is an X of two poles,
# which reads as crossed hammers); DRL = one clean hook with a swept apex and a tapered blade that runs on towards the
# lens tip; spine grooves start 1 mm inside the top edge and run on across the shut line towards the badge; tapered
# fender slot; shut line re-traced on the photo's dark line and smoothed; grille eyes run wall to wall (no flush black
# wedge / sliver beside the mesh); wider, flatter chevron cells with no cut part-cells; splitter corner with real
# thickness; 0.6 mm grooves.
#
# Two things are generated here instead of by the library (kc/lib is read-only):
#   * the badge: SPEC['badge'] is None and badge_on False so the library 'flags' X is never drawn; the winged V is a
#     centred black prim painted last (like the library badge). Switch it off with BADGE_ON = False (the same
#     convention as s650_mustang's pony).
#   * the honeycomb: relief type 'custom' (see c8_mesh).
import math
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

BADGE_ON = True
GROOVE_W = 0.62

# ---- px <-> mm (same frame as the pipeline: 80.5 mm between px 173 and 1123, y up from px 722; the outline spans
# exactly that, so the pipeline applies no re-scale / shift) ----------------------------------------------------------
_PXL, _PXR, _CX, _YB = 173, 1123, 648, 722
_S = 80.5 / (_PXR - _PXL)


def _mm(p):
    return ((p[0] - _CX) * _S, (_YB - p[1]) * _S)


def _mir(g):
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])


def _to_mm(g):
    return affinity.affine_transform(g, [_S, 0, 0, -_S, -_CX * _S, _YB * _S])


def _regularize(region, ribs, w=0.64):                 # same rule as geom.regularize: no rib / gap under w
    r = w / 2 - 0.01
    ribs = ribs.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(region)
    gaps = region.difference(ribs).buffer(-r, join_style=2).buffer(r, join_style=2).intersection(region)
    ribs = region.difference(gaps)
    return ribs.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(region)


def _parts(g):
    return list(g.geoms) if hasattr(g, 'geoms') else ([g] if not g.is_empty else [])


def _slanted_walls(region_px):
    """Edges of a (left-half, px) region that are neither horizontal nor vertical, and not on the centreline."""
    walls = []
    for p in _parts(region_px):
        c = list(p.exterior.coords)
        for a, b in zip(c[:-1], c[1:]):
            if abs(a[0] - b[0]) > 0.05 and abs(a[1] - b[1]) > 0.05:
                walls.append([a, b])
    return walls


# ---- C8 honeycomb mesh (relief type 'custom', ribs in keychain mm) -------------------------------------------------
# The real C8 intakes and grille eyes carry wide, flat chevron/hex cells. Built here: a stretched honeycomb plus a
# 0.8 mm rim rib straddling every SLANTED recess wall, so after the pipeline clips the ribs to the recess their outer
# edge is exactly the wall (rib ends never sit on a slanted edge -> no degenerate shells in the production STL;
# axis-aligned walls clip the cells exactly). Part-cells smaller than min_cell after the clip are folded into the ribs
# so no ragged fragments are left along the walls.
def c8_mesh(region_px, pitch=2.4, stretch=1.55, rib=0.8, rim=0.8, x0=0.0, y0=0.0, min_cell=1.0, symmetric=True):
    """region_px: recess region (shapely, px, left half). symmetric=True: one lattice symmetric about the
    centreline (regions that cross it); False: lattice shifted by x0 mm, built for the left half and mirrored."""
    reg_l = _to_mm(region_px)
    region = _mir(reg_l)
    a = pitch / math.sqrt(3)
    dx = 1.5 * a * stretch
    minx, miny, maxx, maxy = region.bounds
    nx = int(max(abs(minx), abs(maxx)) / dx) + 3
    cells = []
    for i in range(-nx, nx + 1):
        for j in range(int((miny - y0) / pitch) - 2, int((maxy - y0) / pitch) + 3):
            x, y = x0 + i * dx, y0 + j * pitch + (pitch / 2 if i % 2 else 0)
            h = Polygon([(x + a * stretch * math.cos(math.radians(60 * k)), y + a * math.sin(math.radians(60 * k)))
                         for k in range(6)])
            cells.append(h.buffer(-rib / 2, join_style=2))
    cells = unary_union(cells)
    rim_l = unary_union([LineString([_mm(p) for p in w]).buffer(rim, join_style=2) for w in _slanted_walls(region_px)])
    if symmetric:
        reg, rimg = region, _mir(rim_l)
    else:
        reg, rimg = reg_l, rim_l
    ribs = unary_union([reg.difference(cells), rimg.intersection(reg)])
    ribs = _regularize(reg, ribs)
    small = [g for g in _parts(reg.difference(ribs)) if g.area < min_cell]
    ribs = unary_union([ribs] + [g.buffer(0.01) for g in small]).intersection(reg)
    ribs = _regularize(reg, ribs)
    ribs = unary_union([ribs, rimg])                   # rim straddles the wall -> clipped exactly by the pipeline
    return ribs if symmetric else _mir(ribs)


# ---- traced shapes (px, left half) ---------------------------------------------------------------------------------
_LENS = [(225, 398), (243, 391), (300, 413), (350, 441), (390, 469), (416, 499), (384, 496), (340, 481), (290, 474),
         (240, 470), (216, 465), (205, 456), (201, 440), (205, 421), (214, 407)]
_INTAKE = [(186, 543), (260, 549), (372, 559), (358, 590), (342, 622), (325, 650), (302, 673), (290, 677), (200, 677),
           (186, 668)]
_GRILLE = [(648, 570), (550, 566), (422, 562), (410, 580), (397, 605), (386, 630), (378, 650), (373, 666), (378, 679),
           (440, 692), (452, 694), (648, 694)]
_INTAKE_SLOT = Polygon(_INTAKE).intersection(Polygon([(178, 536), (380, 552), (380, 573), (178, 573)]))
_INTAKE_MESH = Polygon(_INTAKE).intersection(box(178, 585, 380, 700))
# open meshed band of the lower grille: outboard 'eyes' + the low centre slot. It is drawn past the grille wall so the
# pipeline clips it exactly to the wall (mesh wall to wall, no flush wedge), and its lower-left edge runs parallel to
# the lip, 0.65 mm above it (uniform flush frame instead of a sliver tapering to nothing).
_L0, _L1 = (378, 679), (440, 692)                             # lip edge of the grille wall
_ln = math.hypot(_L1[0] - _L0[0], _L1[1] - _L0[1])
_nx, _ny = (_L1[1] - _L0[1]) / _ln, -(_L1[0] - _L0[0]) / _ln   # unit normal pointing up (image y down)
_lo = [(_L0[0] + _nx * 0.65 / _S, _L0[1] + _ny * 0.65 / _S), (_L1[0] + _nx * 0.65 / _S, _L1[1] + _ny * 0.65 / _S)]
_k = (_lo[1][1] - _lo[0][1]) / (_lo[1][0] - _lo[0][0])
_x684 = _lo[0][0] + (684 - _lo[0][1]) / _k
_BAND_RAW = [(362, 611), (511, 611), (548, 652), (648, 652), (648, 684), (_x684, 684),
             (362, _lo[0][1] - (_lo[0][0] - 362) * _k)]
_BAND = Polygon(_BAND_RAW).intersection(Polygon(_GRILLE))

INTAKE_RIBS = c8_mesh(_INTAKE_MESH, y0=1.2, x0=0.8, symmetric=False)   # offsets chosen so no ragged part-cells
BAND_RIBS = c8_mesh(_BAND, y0=0.3)


def _taper(*pr, n=24):
    """Tapered capsule chain through (px point, radius mm) pairs, returned as a px polygon point list."""
    c = [Point(p).buffer(r / _S, n) for p, r in pr]
    g = unary_union([unary_union([a, b]).convex_hull for a, b in zip(c[:-1], c[1:])]).simplify(0.05)
    return [(round(x, 2), round(y, 2)) for x, y in list(g.exterior.coords)[:-1]]


# crossed-flags emblem, C7/C8 winged V (photo: 58 x 26 px = 4.9 x 2.2 mm, flags fly outward, top edges drop to a
# wide V notch, one point at the bottom centre). Left half incl. the centreline; mirrored.
_BADGE = [(648, 521), (641, 515), (621, 503.5), (618.5, 493.5), (632, 499), (648, 506)]

SPEC = dict(
    id='c8_corvette', name='Chevrolet Corvette C8 Stingray',
    ref='kc/cars/c8_corvette/ref/front.jpg',
    units='px', px_left=173, px_right=1123, px_bottom=722, center_x=648,
    outline_half=[(648, 384), (520, 384), (400, 383), (330, 382), (285, 380), (258, 378), (238, 380), (219, 386),
                  (203, 396), (191, 411), (183, 430), (177, 452), (174, 478), (173, 510), (173, 560), (173, 620),
                  (174, 670), (177, 690), (183, 704), (198, 714), (235, 720), (320, 722), (648, 722)],
    prims=[
        # headlight unit: long sharp wedge, tall at the fender, pointed at the inner-lower tip
        dict(kind='poly', color='black', pts=_LENS),
        # DRL signature: one hook - near-vertical outer bar swept into a sharp apex at the top-outer corner of the
        # lens, then the long diagonal blade, which tapers (0.8 -> 0.5 mm) as it runs on towards the lens tip
        dict(kind='stroke', color='white', width=0.78,
             pts=[(236.5, 455.5), (236, 417), (240, 407.5), (262, 419), (300, 436.5), (345, 458), (376, 474.5)]),
        dict(kind='poly', color='white', pts=_taper(((376, 474.5), 0.39), ((388, 485), 0.25))),
        # side air intake (corner)
        dict(kind='poly', color='black', pts=_INTAKE),
        # intake: narrow upper slot (plain pocket), flush black vane, main opening with the C8 honeycomb mesh
        dict(kind='poly', color='relief', pts=list(_INTAKE_SLOT.exterior.coords)[:-1], relief=dict(type='none')),
        dict(kind='poly', color='relief', pts=list(_INTAKE_MESH.exterior.coords)[:-1],
             relief=dict(type='custom', ribs=INTAKE_RIBS)),
        # central lower grille (trapezoid): solid gloss-black upper panel (flush)
        dict(kind='poly', color='black', pts=_GRILLE),
        # open meshed band: the outboard 'eyes' plus the low centre slot
        dict(kind='poly', color='relief', pts=_BAND_RAW, relief=dict(type='custom', ribs=BAND_RIBS)),
        # splitter (full width under the lip); the outer corner meets the body side with real thickness
        dict(kind='poly', color='black', pts=[(648, 693), (452, 693), (446, 700), (436, 707), (400, 710), (300, 706),
                                              (200, 699), (176, 693), (160, 690), (150, 760), (648, 760)]),
        # engraved lines: frunk (front trunk) lid shut line (continues the fender slot), frunk centre-spine edges
        # (running on across the shut line towards the badge, as the ridge does on the car), nose crease
        dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2,
             pts=[(343, 410.5), (360, 419.5), (380, 433), (400, 447.5), (420, 459), (440, 465.5), (470, 470),
                  (510, 472.5), (570, 474), (648, 475)]),
        dict(kind='stroke', color='groove', width=GROOVE_W, pts=[(550, 397), (571.5, 500)]),
        dict(kind='stroke', color='groove', width=GROOVE_W, pts=[(225, 512.5), (300, 521), (450, 536), (648, 552)]),
        # fender-top slot (dark hood/fender gap just inboard of the headlight) where the frunk shut line starts;
        # painted after the grooves so the groove's end cap does not sit on it
        dict(kind='poly', color='black', pts=_taper(((307, 393.8), 0.26), ((316, 396.3), 0.37), ((325, 400), 0.43), ((336, 405.8), 0.40),
                                              ((350, 414.2), 0.31))),
    ] + ([dict(kind='poly', color='black', pts=_BADGE)] if BADGE_ON else []),
    badge=None,          # library 'flags' (an X) not used; the winged-V emblem is the last prim (BADGE_ON above)
    badge_note='custom black winged-V crossed-flags prim, on/off with BADGE_ON in spec.py',
    badge_on=False,
    tab=dict(y_frac=0.66),
)
