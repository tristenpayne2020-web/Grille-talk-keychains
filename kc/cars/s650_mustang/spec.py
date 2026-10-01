# Ford Mustang GT (S650, 2024+) front keychain - revision 6.
# Traced on ref/front.jpg = straight-on, level, headlight-height photo of a Race Red 2024 Mustang GT (Car and Driver,
# https://hips.hearstapps.com/hmg-prod/images/2024-ford-mustang-gt-155-64b982586091f.jpg - editorial photo, used only
# as a private tracing reference). Coordinates are ORIGINAL photo pixels; the viewer's LEFT half is traced and the
# pipeline mirrors it about the centreline x = CX.  1 mm on the keychain = 14.34 px.
#
# Two things are generated here instead of by the library (the library is read-only):
#   * the running pony: the library 'pony' badge faces the wrong way, is black and too crude, so a left-galloping
#     white pony is painted as a centred prim (switch it off with BADGE_ON = False; SPEC['badge_on'] stays False so
#     the library pony is never drawn on top of it)
#   * the honeycomb: the real S650 mesh is horizontally elongated hexes; the library 'hex' relief only does regular
#     hexes, so the rib geometry is built here (mm) and handed over as a 'custom' relief: rows registered to the
#     horizontal pocket walls, slanted / curved walls lined with a solid rib band, cleaned with the pipeline's own
#     geom.regularize (0 relief warnings, no rib or gap under 0.64 mm).
# Corner intakes and (by default) the lower grille are flat black, like the G80's lower openings: bulk print time.
# Revision 2: new pony silhouette (arched neck, tucked head, mane + tail streaming back, galloping legs, none planted),
# square-ended 1.0 mm DRL bars + small square projectors, 2.2 mm fang blades with the J hook (rounded nostril floor),
# coarser honeycomb (2.6 mm pitch), lower grille flat + continuous (no plate), 0.6 mm grooves cut exactly at the black
# they land on (no nubs), rib band on slanted pocket walls (black STL non-manifold edges 22 -> 7).
# Revision 3: pony redrawn at its final ~2.1 : 1 proportions (extended gallop, smooth crest + mane step at the withers,
# tapered legs and a rising tail plume, 0.72 mm notch closing), sitting low in the mesh with its hooves on the gloss
# band and cells above it; tapered, slightly bowed fang blades (1.1 -> 2.4 mm) built as solid ribs of ONE upper pocket
# (with the J hook), which with a simplified pony hole and a shared 0.001 mm grid gives watertight single-body STLs
# (0 non-manifold edges); S650-style elongated honeycomb (stretch 1.5, 0.70 mm ribs); projectors as 1.6 x 0.9 mm
# rectangles 1.0 mm below the bars; the raised power dome steps down onto the fender tops in the top edge.
# Revision 5: the pony is redrawn as a HORSE (pricked ear, long face angled down with a round jowl, near-vertical neck
# with two mane flames, deep barrel with a tuck-up, legs 1.1 -> 0.65 mm with hooves, a broad wavy tail plume), 10.3 x
# 6.0 mm, on a flush mount under its middle hooves like the car's badge stalk, halo closed at 1.2 mm; the honeycomb is
# finer and more elongated (pitch 2.2, stretch 1.75, 0.66 mm ribs: ~4 rows centre / 3 nostril, the mesh band keeps the
# photo's 7.43 mm for any pitch), the nostril lattice is offset half a column against the centre mesh; the fang blades
# are 2.2 -> 2.6 mm wide on the photo's blade line and the nostril floor (J rim) sits 1.3 mm above the gloss band; DRL =
# the three bars only (PROJ_ON False) with 0.9 mm between them; groove ends stop clear of the black (no fillet nubs);
# the hood-vent divider is 0.66 mm. The honeycomb hand-over also checks the exact pipeline path for gap specks.
# Revision 6: the pony is rebuilt from a skeleton so it also reads as a horse in the 3D renders (one ear and no mane
# flames, a smaller head hanging from a high ~60 deg neck, legs ~1.5 x the body depth, a narrow-rooted tail falling away
# back and down), 10.6 x 6.9 mm, lower in the mesh (hooves on the gloss band, cells over its head and back, halo closed
# at 0.7 mm instead of 1.2); the fang blades get an edge of their own: a continuous 0.7 mm recessed moat along both blade
# edges and the J rim, a rib band behind it on the centre side, and the outer nostrils become 3 horizontal louvres (the
# photo's nostrils read as horizontal dashes) so the J bracket outlines a different pocket; J radius 3.0 -> 1.2 mm;
# part-cells under 1.0 mm2 are filled (r5 0.5); the hood vent is one continuous slot with a short 0.66 mm tab from its
# top edge (photo); the intake crease hook is 0.68 mm clear of the intake (r5 0.45); fender lines cross the cowl edge
# and the lamp top ~square.
import math
import os
import sys
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom as _geom                # read-only use of the pipeline's own clean-up, see hex_ribs

CX = 1108
PX_BOTTOM = 1072
PX_PER_MM = (1685 - 531) / 80.5
MM = 1.0 / PX_PER_MM
FRAME = 0.65 * PX_PER_MM          # gloss-black surround left flush around every honeycomb pocket (mm -> px)
BAND = 0.66                       # mm: solid rib band lining every slanted / curved pocket wall (see hex_ribs)
FRAME_SIDE = 0.14 * PX_PER_MM     # flush margin kept on slanted walls; + the rib band = a ~0.8 mm surround (r3: 0.1 -> 0.14,
                                  # the 0.1 margin left a float hairline along the left nostril wall)
BADGE_ON = True                   # the centred white running pony (custom prim, see above)
LOWER_MESH = False                # honeycomb in the lower grille (see the lower grille section)


def _pts(g):
    """largest polygon of a shapely geometry -> point list (px) for a spec 'poly'"""
    if g.geom_type != 'Polygon':
        g = max(g.geoms, key=lambda p: p.area)
    g = g.simplify(0.4)
    return [(round(x, 2), round(y, 2)) for x, y in list(g.exterior.coords)[:-1]]


def _half(pts):
    """close a left-half trace against the centreline and add its mirror image (for shapely work only)"""
    return Polygon(pts + [(2 * CX - x, y) for x, y in reversed(pts)]).buffer(0)


def _mm(g):
    """px geometry -> keychain mm (same mapping as the pipeline: x from the centreline, y up from px_bottom)"""
    return affinity.affine_transform(g, [MM, 0, 0, -MM, -CX * MM, PX_BOTTOM * MM])


def _mirror_mm(g):
    return unary_union([g, affinity.scale(g, xfact=-1, yfact=1, origin=(0, 0))])


# ---------------------------------------------------------------- honeycomb (elongated hexes, pointed left/right)
# the photo's cells are ~2.3 x 1.2 mm (26 x 16.5 px lattice, ~2:1 elongated), too fine for >= 0.64 mm ribs AND gaps.
# r5: pitch 2.6 -> 2.2 (README lower bound), stretch 1.5 -> 1.75, rib 0.70 -> 0.66. Tried finer: at 1.8 the pipeline's
# regularize drops whole 1.1 mm cells (not a fixed point any more), at 2.0 the part-cells by the pony / fangs fill in.
HEX_PITCH = 2.2      # row pitch (mm): 1.54 mm clear cell height
HEX_STRETCH = 1.75   # horizontal stretch -> ~3.4 x 1.54 mm clear cells (the photo's ~2:1)
HEX_RIB = 0.66       # wall width (mm) (>= the pipeline's 0.64 mm rib limit)
NOS_SHIFT = 0.75     # x offset of the nostril lattice (x a = half a column): cells do not line up across the fang
MIN_CELL = 1.0       # mm2: smaller part-cells are filled (r5 0.5: stray specks along the mesh floor / by the pony)


def _polys(g):
    return [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']


def _reg(region, ribs):
    """geom.regularize, retried on a snapped copy if GEOS trips over a near-degenerate vertex"""
    for grid in (None, 0.001, 0.002):
        try:
            g = ribs if grid is None else shapely.set_precision(shapely.make_valid(ribs), grid)
            return _geom.clean(_geom.regularize(region, g, 0.64))
        except shapely.errors.GEOSException:
            continue
    return ribs


def _cells(region, y0, pitch, stretch, rib, x0=0.0):
    """the clear cells of the stretched honeycomb over region's bounds (column 0 at x = x0)"""
    a = pitch / math.sqrt(3) * stretch
    colp = 1.5 * a
    minx, miny, maxx, maxy = region.bounds
    cells = []
    for i in range(int(math.floor((minx - x0) / colp)) - 1, int(math.ceil((maxx - x0) / colp)) + 2):
        x = x0 + i * colp
        yo = y0 + (pitch / 2 if i % 2 else 0.0)
        for j in range(int(math.floor((miny - yo) / pitch)) - 1, int(math.ceil((maxy - yo) / pitch)) + 2):
            y = yo + j * pitch
            h = Polygon([(x + a, y), (x + a / 2, y + pitch / 2), (x - a / 2, y + pitch / 2), (x - a, y),
                         (x - a / 2, y - pitch / 2), (x + a / 2, y - pitch / 2)])
            cells.append(h.buffer(-rib / 2, join_style=2))
    return unary_union(cells)


def hex_ribs(region, y0=0.0, pitch=HEX_PITCH, stretch=HEX_STRETCH, rib=HEX_RIB, min_hole=0.5, band=BAND, skip=None,
             noded=False, solid=None, nos_zone=None, nos_holes=None, moat=None, mband=None):
    """Rib geometry (mm) of a stretched honeycomb inside `region` (mm). The lattice is symmetric about x = 0 (column 0
    on the centreline), y0 shifts it vertically. Cleaned with the pipeline's own geom.regularize (ribs / gaps under
    0.64 mm go) until it is a fixed point of it, and part-cells smaller than min_hole mm2 against the pocket wall are
    filled, so every rib and every hole is printable and the build-time clean-up pass changes nothing.
    The slanted / curved pocket walls (grille sides, nostril 'J', pony halo) are lined with a solid rib band (`band`
    mm; ribs stand flush with the black face, so in the print it is simply part of the gloss-black surround): no cell
    is cut by those walls. Cells cut by a slanted wall leave float-noise micro-slivers after the pipeline's 0.001 mm
    snap, which became non-manifold edges in the STL (22 -> 7). Walls inside `skip` keep cut cells (r3: not used any
    more - the fang blades are `solid` ribs inside the pocket, so no slanted wall has cut cells); horizontal walls
    (where the rows are registered) are exact anyway and keep their clean part-cells. `solid` (mm) = extra solid rib
    areas (the fangs + J hooks); noded=True returns (region, ribs) on one shared grid, see _noded."""
    region = _geom.clean(region)                      # the pipeline works on the same snapped (0.001 mm) region
    holes = _cells(region, y0, pitch, stretch, rib)
    if nos_zone is not None:
        # r5: the outer nostrils (left of the left fang's centre line, and its mirror) get their own lattice, offset
        # NOS_SHIFT * a in x, so the cells do not line up across the blade and it reads as a separate element
        a = pitch / math.sqrt(3) * stretch
        if nos_holes is not None:                     # r6: the nostril gets its own texture (horizontal louvres)
            hl = nos_holes.intersection(nos_zone)
        else:
            hl = _cells(nos_zone, y0, pitch, stretch, rib, x0=-NOS_SHIFT * a).intersection(nos_zone)
        holes = unary_union([holes.difference(_mirror_mm(nos_zone)), _mirror_mm(hl)])
    ribs = _geom.clean(region.difference(holes))
    segs = []
    for pg in _polys(region):
        for ring in [pg.exterior] + list(pg.interiors):
            cs = list(ring.coords)
            for a, b in zip(cs[:-1], cs[1:]):
                if abs(a[1] - b[1]) > 1e-6 and abs(a[0] - b[0]) > 1e-6:      # slanted / curved wall segment
                    ln = LineString([a, b])
                    if skip is None or not skip.contains(ln):
                        segs.append(ln)
    if segs and band:
        ribs = _geom.clean(unary_union([ribs, unary_union(segs).buffer(band, join_style=1).intersection(region)]))
    if solid is not None:                             # solid rib areas inside the pocket (the fang blades + J hooks)
        ribs = _geom.clean(unary_union([ribs, solid.intersection(region)]))
    if mband is not None:                             # r6: solid rib band beyond the fang moat (centre-mesh side)
        ribs = _geom.clean(unary_union([ribs, mband.intersection(region)]))
    if moat is not None:                              # r6: recessed moat round the fang blade + J rim; it stops at the
        if segs and band:                             # slanted-wall rib band (reaching the wall it ended in a hairline
            moat = moat.difference(unary_union(segs).buffer(band, join_style=1))   # point along the wall)
        ribs = _geom.clean(ribs.difference(moat))
    for _ in range(10):
        # what the pipeline will make of it: clip the handed-over ribs to the region, then its regularize pass
        sim = _reg(region, _geom.clean(_handover(region, ribs).intersection(region)))
        gaps = region.difference(sim)
        fill = [p for p in _polys(gaps) if p.area < min_hole] + [p.buffer(0.03, join_style=2) for p in _geom.thin_strips(gaps, 0.62)]
        cut = [p.buffer(0.03, join_style=2) for p in _geom.thin_strips(sim, 0.62)]
        # single-point contacts (a cell corner or a rib tip just touching the pocket wall, or two cells touching) give
        # non-manifold pinch edges in the STL: close them with a speck of rib / open them with a speck of gap
        fill += [pt.buffer(0.12, cap_style=3) for pt in _point_contacts(gaps, region.exterior if region.geom_type == 'Polygon' else region.boundary)]
        fill += [pt.buffer(0.12, cap_style=3) for pt in _point_contacts_between(gaps)]
        cut += [pt.buffer(0.12, cap_style=3) for pt in _point_contacts(sim, region.boundary)]
        # r3: thin acute rib spurs / cell spikes (where cells are cut by the curved band edge at a shallow angle) - too
        # fine for the nozzle, and they show as 'antennae' in the face view
        # (a spur is re-grown by the pipeline's mitre regularize from its acute corner, so the cell corners either side
        # of it are filled instead: the spur becomes a blunt bump of the rib)
        if noded:                                     # the exact pipeline path of the handed-over pair
            _rn, _xn = _noded(region, sim)
            _xp = _reg(_rn, _geom.clean(_xn.intersection(_rn)))
            fill += [p.buffer(0.15, join_style=1) for p in _spurs(_xp)]
            # r5: degenerate gap specks / hairline gap strips that the pipeline's regularize leaves along a cut edge
            _gp = _rn.difference(_xp)
            fill += [p.buffer(0.2, join_style=1) for p in _polys(_gp) if p.area < 0.05]   # r6: 0.06 -> 0.2 (a 0.06 plug was undone by the regularize)
            fill += [p.buffer(0.06, join_style=2) for p in _geom.thin_strips(_gp, 0.62, min_len=0.3)]
        fill += [p.buffer(0.15, join_style=1) for p in _spurs(sim)]
        fill += [p.buffer(0.02, join_style=2) for p in _spurs(gaps)]
        if not fill and not cut:
            ribs = sim
            break
        # fill part-cells that are too small and the thin acute tips of part-cells cut by a pocket wall (the same test
        # the pipeline's checker uses); cut thin rib wedges
        fill = [q for f in fill for q in _polys(f)]
        ribs = _geom.clean(unary_union([sim] + fill).intersection(region).difference(unary_union(cut) if cut else Polygon()))
    if noded:
        return _noded(region, ribs)
    return _handover(region, ribs)


def _noded(region, ribs, grid=0.001):
    """Revision 3: region and ribs on ONE shared, noded 0.001 mm grid (the pipeline's own snap grid). Every point where a
    rib meets the pocket wall becomes a vertex of the wall itself, so when the pipeline clips the ribs to the region
    and snaps both, nothing moves: no hairline rib / gap slivers along slanted walls where cells are cut (the fang-blade
    edges), which were the STL's non-manifold edges. Returns (region, ribs); the region is handed over as a 'geom'
    relief prim so its inserted vertices survive (a px 'poly' would be simplified / re-rounded)."""
    region = shapely.set_precision(region, grid)
    ribs = shapely.intersection(shapely.make_valid(ribs), region, grid_size=grid)
    ribs = unary_union(_polys(ribs))
    gaps = unary_union(_polys(shapely.difference(region, ribs, grid_size=grid)))
    return shapely.union(ribs, gaps, grid_size=grid), ribs


def _spurs(g, r=0.2):
    """thin, elongated spikes of g (lost to a round opening of radius r, longer than ~3x their width)"""
    out = []
    for p in _polys(g.difference(g.buffer(-r, join_style=1).buffer(r, join_style=1))):
        if p.area < 0.004:
            continue
        mrr = p.minimum_rotated_rectangle
        cs = list(mrr.exterior.coords)
        e1 = math.dist(cs[0], cs[1]); e2 = math.dist(cs[1], cs[2])
        if max(e1, e2) > 3 * max(min(e1, e2), 1e-6) and max(e1, e2) > 0.3:
            out.append(p)
    return out


def _points(x):
    out = []
    for g in getattr(x, 'geoms', [x]):
        if g.geom_type == 'Point':
            out.append(g)
        elif g.geom_type == 'MultiPoint':
            out += list(g.geoms)
    return out


def _point_contacts(g, line):
    """isolated points where the outline of g touches `line` (a boundary) without sharing a segment"""
    g = unary_union(_polys(g))
    if g.is_empty:
        return []
    return _points(g.boundary.intersection(line))


def _point_contacts_between(g):
    ps = _polys(g)
    out = []
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            if ps[i].distance(ps[j]) < 1e-7:
                out += _points(ps[i].boundary.intersection(ps[j].boundary))
    return out


def _handover(region, ribs):
    """ribs that reach a little PAST the pocket wall (and holes that do the same): the pipeline clips them to its own
    copy of the region, so float noise cannot leave hairline slivers of rib or gap along the wall"""
    holes = region.difference(ribs)
    wall = region.buffer(0.03).difference(region.buffer(-0.03))
    holes_ext = unary_union([holes, holes.buffer(0.03, join_style=2).intersection(wall)])
    return shapely.set_precision(region.buffer(0.03).difference(holes_ext), 1e-4)


# ---------------------------------------------------------------- running pony (gallops to the viewer's LEFT)
# Revision 6: rebuilt from a skeleton so it reads as a HORSE in the flat view AND in the 3D renders (the r5 outline read
# as a fox / dog in 3D: a mane flame behind the ear looked like a second ear, legs shorter than the body was deep, a
# thick upswept brush tail, an oversized head sitting on the chest). Local units, x right / y up, head LEFT
# (1 unit ~ 0.115 mm). Horse cues, every stroke >= 0.65 mm so it survives the nozzle:
#   * ONE pricked ear on the poll; no mane flames (nothing else pokes up above the head)
#   * a smaller head (poll -> nose ~0.45 of the body length, r5 ~0.6) hanging down-forward from the poll, with a round
#     jowl and a throat-latch angle, carried HIGH (poll ~19 units above the withers) on a ~60 deg neck that is clearly
#     visible between head and chest
#   * a deep barrel (depth ~0.41 of its length) with a tuck-up and round quarters
#   * long thin legs, 1.45-1.55 x the body depth (r5 ~0.78): lead foreleg reaching forward-down, the other foreleg
#     folded (knee forward, hoof back), a hind leg under the belly with a hock angle, one trailing - 0.85-1.0 mm at the
#     body tapering to 0.64 mm, 0.7 mm hoof caps
#   * the tail: a narrow dock (0.7 mm) off the top of the croup, widening to ~1.1 mm and falling away back and DOWN to a
#     point well below the croup (r5: an even, upswept plume = a fox's brush)
# The outline is then closed + opened at 0.72 / 0.52 mm, so no notch or tip is finer than the nozzle can print.
_PONY_HNB = [(30, 61), (25, 58.5), (19.5, 54.5), (15.5, 51), (14, 48.5), (15, 46.3), (18, 46), (22, 47.5),   # poll, face, nose, jaw
             (25.5, 49.5), (29, 53.5), (29.5, 50.5), (30, 46), (30.5, 41), (31, 35),                          # jowl, throat latch, neck front
             (32.5, 29), (37, 24.5), (48, 23.5), (58, 25), (64, 27), (70, 29.5), (74.5, 34),                  # breast, girth, belly, tuck-up
             (74, 39), (68.5, 42), (58, 40.5), (49, 42.5), (45, 48), (40, 54), (35, 58.5)]                    # quarters, croup, back, crest
_PONY_EAR = [(27.5, 60), (33.5, 61.5), (31.5, 68)]
_PONY_LEGS = [([(33.5, 29), (23.5, 22), (15, 15.5), (10, 14.5)], [8.5, 6.6, 6.4, 7]),    # lead foreleg reaching forward
              ([(38.5, 26), (34.5, 15), (40.5, 9.5), (44, 9)], [8.5, 6.6, 6.4, 7]),       # folded foreleg: knee fwd, hoof back
              ([(65, 29), (60, 18), (62, 12.5), (57, 5)], [10, 7.2, 6.8, 7]),             # hind leg under the belly (hock)
              ([(72, 31), (79.5, 22), (86, 15), (93.5, 9)], [10, 7.2, 6.8, 7])]           # trailing hind leg (steeper than the tail)
_PONY_TAIL = ([(74, 40), (80, 42.5), (87, 42.5), (93, 39.5), (98, 34), (101, 29)], [6.2, 8.5, 10, 9.5, 6.5, 3])  # falls away
PONY_W_MM = 10.6                  # -> 10.6 x 6.9 mm (r5 10.3 x 6.0); the photo badge is ~10 mm wide
PONY_ROT = 0.0                    # deg, negative = nose up
PONY_TOP = 764                    # px, bbox top (the blunted ear tip lands at ~770 = the photo pony's head, 2.3 mm under the
                                  # grille top): cells run over the head and back, the hooves land ~1 mm into the gloss band
PONY_CX = CX + 13                 # bbox centre x (px): the photo pony sits right of the centreline (CX+10..17); +13 is a
                                  # lattice phase where every halo wall passes the STL check (0 non-manifold, no lost cell)
PONY_HALO = 0.84                  # black clearance around the pony (mm): 0.18 flush + the 0.66 rib band
MOUNT_M = 0.84                    # mm: the badge mount (flush column under the lowest hooves down to the gloss band, like
MOUNT_R = 1.2                     #     the car's badge stalk) = hooves + MOUNT_M on the head side / MOUNT_R on the tail side
PONY_HALO_FLUSH = False           # True: the whole 0.84 halo is flush and cells are cut by it directly (no rib band). It
                                  # looks tidier in face.png, but the cut cells along the curved halo left 20-30 near-zero
                                  # slivers / non-manifold edges in the black STLs, so the r3 band construction is kept
PONY_HOLE_CLOSE = 0.7             # mm: the flush part of the halo is closed (fills the leg crotches); r6: 1.2 -> 0.6 so the
                                  # halo hugs the back / croup / tail with the same width as round the head (r5 left a flush
                                  # 'cloud' over the back)
PONY_HOLE_SIMPLIFY = 1.2          # px: simplified to few, long wall segments - every short curved wall segment touched by
                                  # the rib band became a hairline sliver after the pipeline's regularize + 0.001 mm snap


def _taper(pts, ws):
    """stroke along pts whose width (units) runs linearly between the per-vertex widths ws, round ends"""
    d = [0.0]
    for a, b in zip(pts[:-1], pts[1:]):
        d.append(d[-1] + math.dist(a, b))
    ln = LineString(pts)
    n = max(2, int(d[-1] * 2))
    cs = []
    for i in range(n + 1):
        t = d[-1] * i / n
        k = min(max(j for j in range(len(d)) if d[j] <= t + 1e-9), len(d) - 2)
        f = (t - d[k]) / max(d[k + 1] - d[k], 1e-9)
        cs.append((ln.interpolate(t), (ws[k] + (ws[k + 1] - ws[k]) * f) / 2))
    return unary_union([unary_union([a.buffer(ra, 24), b.buffer(rb, 24)]).convex_hull
                        for (a, ra), (b, rb) in zip(cs[:-1], cs[1:])])


def pony_px():
    parts = [Polygon(_PONY_HNB).buffer(0), Polygon(_PONY_EAR).buffer(0), _taper(*_PONY_TAIL)]
    parts += [_taper(*leg) for leg in _PONY_LEGS]
    g = unary_union(parts).buffer(0.6, join_style=1).buffer(-0.6, join_style=1)
    if PONY_ROT:
        g = affinity.rotate(g, PONY_ROT, origin=g.centroid)  # in y-up units: negative = clockwise = nose up
    b = g.bounds
    k = PONY_W_MM * PX_PER_MM / (b[2] - b[0])               # units -> px, y flipped (photo y runs down)
    g = affinity.translate(g, -(b[0] + b[2]) / 2, -b[3])     # bbox top-centre at the origin
    g = affinity.scale(g, k, -k, origin=(0, 0))
    g = affinity.translate(g, PONY_CX, PONY_TOP)
    # print-honest: close the notches narrower than 0.72 mm (every black notch left is >= 0.72 mm, so the classic inlay
    # has no black sliver in it) and blunt the tips narrower than 0.52 mm - what the 0.4 mm nozzle would do anyway
    rc, ro = 0.36 * PX_PER_MM, 0.26 * PX_PER_MM
    g = g.buffer(rc, join_style=1).buffer(-rc, join_style=1)
    g = g.buffer(-ro, join_style=1).buffer(ro, join_style=1)
    return g.simplify(0.3)


PONY = pony_px()

# ---------------------------------------------------------------- upper grille (hexagonal opening)
GRILLE = [(CX, 737), (790, 737), (782, 741), (760, 777), (741, 815), (729, 848), (728, 860), (736, 873), (765, 897),
          (800, 916), (840, 925), (CX, 926)]
G = _half(GRILLE)
G_IN = G.buffer(-FRAME_SIDE, join_style=2).intersection(box(0, 737 + FRAME, 2 * CX, 2000))   # + BAND of ribs on the slanted sides
# gloss-black 'fang' blades splitting the grille into centre mesh + outer nostrils. Revision 3: tapered like the real
# fangs, 1.1 mm wide at the top widening to 2.4 mm at the foot, centreline bowing slightly (photo). On the S650 the fang
# hooks OUTWARD along the nostril floor (a 'J'): the nostril pocket ends above the centre mesh and its inner-bottom
# corner is rounded (R 3 mm), so the flush band visibly turns outward under the nostril mesh at the wide foot.
# r5: re-centred on the photo's blade face (x 862-893 at the top, 840-868 at the foot) and widened (r3: 1.1 -> 2.4 mm,
# barely wider than a rib at the top): the photo blade is ~2.1 mm, so it is clearly wider than two lattice ribs throughout
BLADE_PTS = [(880, 736), (873, 790), (863, 835), (852, 866)]
BLADE_W = (2.2, 2.6)            # mm, top -> foot


def _blade(pts):
    ln = LineString(pts)
    n = int(ln.length / 3)
    w0, w1 = BLADE_W[0] * PX_PER_MM, BLADE_W[1] * PX_PER_MM
    cs = [(ln.interpolate(i / n, normalized=True), (w0 + (w1 - w0) * i / n) / 2) for i in range(n + 1)]
    g = unary_union([unary_union([a.buffer(ra, 32), b.buffer(rb, 32)]).convex_hull
                     for (a, ra), (b, rb) in zip(cs[:-1], cs[1:])])
    return g.simplify(0.2)


BLADE = _blade(BLADE_PTS)
BLADES = BLADE.union(_blade([(2 * CX - x, y) for x, y in BLADE_PTS]))
# Honeycomb rows are registered to the pocket walls: every horizontal pocket wall gets a full rib above / below one
# cell column and clean part-cells in the other, instead of random slivers. That fixes the pocket heights:
# H = pitch + rib + 2 * extra + k * pitch / 2 (k = whole number); the wall ribs are rib + extra.
# r5: the mesh band keeps the photo's height (~7.43 mm, UP_TOP -> gloss band) for any pitch: k = whole half-rows that
# fit, the rest goes into the top / bottom wall ribs (WALL_EXTRA)
MESH_H = 7.43
K_UP = int(math.floor((MESH_H - HEX_PITCH - HEX_RIB - 0.1) / (HEX_PITCH / 2)))
WALL_EXTRA = min(0.45, max(0.05, (MESH_H - HEX_PITCH - HEX_RIB - K_UP * HEX_PITCH / 2) / 2))


def _wall_h(k):
    return (HEX_PITCH + HEX_RIB + 2 * WALL_EXTRA + k * HEX_PITCH / 2) * PX_PER_MM


UP_TOP = 737 + FRAME                                              # top wall of the upper mesh (px)
UP_BOT = UP_TOP + _wall_h(K_UP)                                   # centre mesh bottom (~853 px)
NOS_RISE = 1                      # half-rows the nostril floor sits above the centre mesh floor (2 left only 2 rows of nostril cells)
NOS_BOT = UP_TOP + _wall_h(K_UP - NOS_RISE) - 0.2 * PX_PER_MM     # nostril mesh bottom: the J rim below it is 1.3 mm
# ONE upper honeycomb pocket across the whole grille opening, down to the smooth gloss band, with a hole round the pony.
# Revision 3: the gloss-black fang blades and their J hook are SOLID RIBS inside this pocket instead of flush walls
# between three pockets. Ribs stand flush with the black face, so in the print they are the same gloss-black blades as
# before; but the pocket now has no slanted wall with cut cells (the pipeline's 0.001 mm snap turned every cell cut by a
# slanted blade wall into hairline slivers = the STL's non-manifold edges), and the tapered blade keeps its true width
# with the cells running right up to it on both sides.
UPPER = G_IN.intersection(box(0, 700, 2 * CX, UP_BOT))
UPPER = max(UPPER.geoms, key=lambda p: p.area) if UPPER.geom_type != 'Polygon' else UPPER
if BADGE_ON:
    _c = PONY_HOLE_CLOSE * PX_PER_MM
    PONY_HOLE = PONY.buffer((PONY_HALO - (0 if PONY_HALO_FLUSH else BAND)) * PX_PER_MM).buffer(_c).buffer(-_c).simplify(PONY_HOLE_SIMPLIFY)
    # the badge's mount: a narrow flush column under the lowest hooves down to the gloss band - the car's pony stands on
    # one; it also avoids hairline necks of pocket between the hoof halos and the band (r6: the hooves already reach the
    # gloss band, so it only matters if the pony is moved up)
    _hb = PONY.bounds[3]
    _hx = PONY.intersection(box(0, _hb - 0.45 * PX_PER_MM, 2 * CX, 2000)).bounds
    _hr = MOUNT_M * PX_PER_MM                                     # mount = the two hooves + MOUNT_M each side
    PONY_HOLE = unary_union([PONY_HOLE, box(_hx[0] - _hr, _hb - 0.3 * PX_PER_MM, _hx[2] + MOUNT_R * PX_PER_MM, UP_BOT + 30)])
    # where the halo comes within 1.6 mm of the mesh top wall the strip of pocket between them (too thin for a cell, it
    # only left a hairline rib) is flush too; r6: with the pony lower this is only a short piece above the ear
    _T = box(0, 600, 2 * CX, UP_TOP + 0.5)
    _t = 0.8 * PX_PER_MM
    PONY_HOLE = unary_union([PONY_HOLE, _T]).buffer(_t).buffer(-_t).difference(_T.buffer(-0.5)).simplify(PONY_HOLE_SIMPLIFY)
    PONY_HOLE = max(_polys(PONY_HOLE), key=lambda q: q.area)
    UPPER = UPPER.difference(PONY_HOLE)
UPPER = UPPER.buffer(-0.36 * PX_PER_MM, join_style=2).buffer(0.36 * PX_PER_MM, join_style=2)   # no pinched channels
# (mitre joins: the pocket's corners stay sharp - short arcs lined by the rib band gave slivers, see PONY_HOLE_SIMPLIFY)
UPPER = unary_union([p for p in _polys(UPPER) if p.area > 400])
# the fang + its J: the blade turns outward along the nostril floor (NOS_BOT, above the centre mesh floor UP_BOT); the
# inner corner between blade and floor is filleted (R 3 mm), so the black band visibly hooks outward under the nostril
NOS_R = 1.2 * PX_PER_MM          # r6: 3.0 -> 1.2 mm, the photo's J turns outward on a ~1 mm radius
# r6: the blade is extended straight up through the grille top (it is clipped to the pocket anyway), so the moat along
# its edges runs straight into the top wall: the blade's rounded top corner left an acute rib wedge there that the
# clean-up loop grew into a plug across the moat
_BLADE_EXT = _blade([(BLADE_PTS[0][0] + (BLADE_PTS[0][0] - BLADE_PTS[1][0]) * 36 / 54, 700)] + BLADE_PTS)
# r6: below the nostril floor the blade's centre-side edge drops vertically to the mesh floor, so the moat along it
# meets the floor square (at the blade's 19 deg slant the moat end left an acute rib corner / a V point on the floor)
_xr = _BLADE_EXT.intersection(box(0, NOS_BOT - 0.5, 2 * CX, NOS_BOT + 0.5)).bounds[2]
_J = unary_union([_BLADE_EXT.intersection(box(0, 0, 2 * CX, NOS_BOT + 1)), box(0, NOS_BOT, _xr, 2000)]
                 ).buffer(NOS_R, join_style=1).buffer(-NOS_R, join_style=1)
FANGS = unary_union([_J, affinity.scale(_J, xfact=-1, yfact=1, origin=(CX, 0))]).intersection(UPPER)

# ---------------------------------------------------------------- corner intake: flat black, like the G80's lower intakes
# (a honeycomb here cost +1 min per keychain in production for ~16 tiny cells - dropped for bulk printing)
INTAKE = [(570, 868), (582, 858), (622, 860), (700, 928), (750, 950), (700, 996), (688, 1004), (592, 1004),
          (578, 997), (570, 980)]

# ---------------------------------------------------------------- lower grille: flat black by default (bulk printing).
# The honeycomb here costs +1:37 per keychain in production (+2:57 classic) for a band only 4 mm tall; the upper grille
# carries the honeycomb identity, and the G80 keeps its lower openings flat too. LOWER_MESH = True puts it back as one
# continuous honeycomb (the plate blank is dropped either way, as the style guide drops plates).
LOW_TOP = 948 + FRAME
LOW_BOT = 1026                                                   # outer bottom edge (px): >= 1.0 mm body band above the splitter
LOWER = [(CX, 948), (832, 948), (826, 953), (788.5, LOW_BOT - 4), (792, LOW_BOT), (CX, LOW_BOT)]
L = _half(LOWER)
LOWER_HEX = L.buffer(-FRAME, join_style=2)

# ---------------------------------------------------------------- relief regions (px pts) + their ribs (mm)
# the upper pocket surrounds the pony (it has a hole), which a spec 'poly' cannot carry, and its walls get the rib
# crossing points inserted as vertices (see _noded): it is handed over as the pipeline's own 'geom' primitive (mm, the
# same px -> mm mapping as the pipeline), exactly the geometry the honeycomb is built on
UPPER_MM0 = _geom.clean(_mm(UPPER.simplify(0.4)))
LOWER_PTS = _pts(LOWER_HEX)


def _y0_top(y_px):
    """lattice phase putting a full rib along a horizontal pocket TOP wall at y_px"""
    return ((PX_BOTTOM - y_px) * MM - (HEX_PITCH + HEX_RIB) / 2 - WALL_EXTRA) % HEX_PITCH


HEX_Y0 = dict(upper=_y0_top(UP_TOP), lower=_y0_top(LOW_TOP))
# the left outer nostril = everything left of the left fang's centre line (extended up / down); mirrored inside hex_ribs
_bx = [(x, y) for x, y in BLADE_PTS]
_ext = lambda p, q, y: (p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1]), y)
NOS_ZONE = _mm(Polygon([(0, 600), _ext(_bx[0], _bx[1], 600)] + _bx + [_ext(_bx[-2], _bx[-1], 1000), (0, 1000)]))
# r6: the fang blades get an edge of their own. In r5 they were plain solid ribs, the exact tone of the lattice ribs, so
# they read as a missing column of cells and the J hook vanished in the renders. Now:
#   * a continuous recessed MOAT (FANG_MOAT mm) runs along both long edges of each blade and along the top of the J rim:
#     blade + J stand as one clean raised plank with straight parallel edges, whatever the cell phase
#   * on the centre side the moat is backed by a solid rib band (FANG_BAND), then the honeycomb
#   * the outer nostrils get their own texture: NOS_SLATS horizontal louvres (the photo's nostrils read as horizontal
#     dashes) that open into the moat, so the J bracket outlines a visibly different pocket beside the centre honeycomb
FANG_MOAT = 0.7                   # mm (>= 0.64)
FANG_BAND = 0.66                  # mm
FANG_MOAT_END = 0.8               # mm: rib left under the round end of the centre-side moat, above the mesh floor
NOS_SLATS = 3                     # louvre gaps above the moat (0 = nostril keeps the offset honeycomb)
NOS_SLAT_GAP = 0.8                # mm; the ribs between them share the rest of the nostril height (~0.76 mm)
_F_MM = _geom.clean(_mm(FANGS))
_J_MM = _mirror_mm(_mm(_J))                           # the whole J (not clipped to the pocket): moat / band are built on it
_NOS2 = _mirror_mm(NOS_ZONE)
# the centre-side moat ends in a round cap FANG_MOAT_END above the mesh floor: run into the floor, its square corners
# were eaten by the clean-up (hairline plugs / a V point touching the floor = STL pinch)
_FLOOR_MM = (PX_BOTTOM - UP_BOT) * MM
if FANG_MOAT:
    _yc = _FLOOR_MM + FANG_MOAT_END + FANG_MOAT / 2
    _xc = (_xr - CX) * MM + FANG_MOAT / 2                 # the moat runs vertically here (left fang; mirrored)
    FANG_MOAT_G = unary_union([_J_MM.buffer(FANG_MOAT, join_style=1).difference(_J_MM).difference(box(-60, -10, 60, _yc)),
                               _mirror_mm(Point(_xc, _yc).buffer(FANG_MOAT / 2, 32))])
else:
    FANG_MOAT_G = None
FANG_BAND_G = (_J_MM.buffer(FANG_MOAT + FANG_BAND, join_style=1).difference(_J_MM.buffer(FANG_MOAT, join_style=1))
               .difference(_NOS2) if FANG_MOAT and FANG_BAND else None)
if NOS_SLATS:
    _yj = (PX_BOTTOM - NOS_BOT) * MM + FANG_MOAT          # top of the moat over the J rim (mm)
    _yt = (PX_BOTTOM - UP_TOP) * MM                       # pocket top (mm)
    _sr = (_yt - _yj - NOS_SLATS * NOS_SLAT_GAP) / (NOS_SLATS + 1)
    NOS_HOLES = unary_union([box(-60, _yj + _sr * (i + 1) + NOS_SLAT_GAP * i, 60, _yj + (_sr + NOS_SLAT_GAP) * (i + 1))
                             for i in range(NOS_SLATS)])
else:
    NOS_HOLES = None
UPPER_MM, RIBS_UPPER = hex_ribs(UPPER_MM0, HEX_Y0['upper'], solid=_F_MM, noded=True, min_hole=MIN_CELL,
                                nos_zone=NOS_ZONE if (NOS_SHIFT or NOS_SLATS) else None, nos_holes=NOS_HOLES,
                                moat=FANG_MOAT_G, mband=FANG_BAND_G,
                                skip=_mm(PONY_HOLE.buffer(3)) if BADGE_ON and PONY_HALO_FLUSH else None)

REL_UPPER = dict(type='custom', ribs=RIBS_UPPER)
if LOWER_MESH:
    LOWER_MM, RIBS_LOWER = hex_ribs(_geom.clean(_mm(Polygon(LOWER_PTS))), HEX_Y0['lower'], noded=True)
    REL_LOWER = dict(type='custom', ribs=RIBS_LOWER)

# ---------------------------------------------------------------- headlight + S650 light signature
# lamp top edge 1.5-2 px above the trace so the square-ended 1.0 mm bars keep >= 0.62 mm of black above them
LAMP = [(549, 714.5), (600, 716.5), (690, 719.5), (745, 734), (752, 740), (738, 768), (724, 791), (650, 784),
        (580, 777), (564, 770), (554, 750)]
LAMP_P = Polygon(LAMP)
DRL_W = 1.0                     # bar height (mm)
DRL_CLEAR = 0.62                # min black between a bar and the lamp edge (mm)
# the three horizontal light bars, square-ended, stepping down along the lamp top like the photo; bar 3 is clipped
# parallel to the sloping inboard lamp edge instead of being shortened
# r5: 0.9 mm black between the bars (r3: 0.63), so they read as three separate lights at a glance
DRL_BARS = [((572, 732.5), (615, 734)), ((628, 736), (671, 738)), ((684, 739.6), (729, 742.5))]
# the three projector modules under the bars: flat 1.6 x 0.9 mm rectangles (photo: wide, low lit lenses), placed
# PROJ_GAP of black below their bar so the bar and the projector read as two lights, not a 'T', also in the recessed
# production lamp; PROJ_ON = False leaves the DRL bars alone (house style: DRL graphic only)
PROJ_ON = False                 # r5: bars only (house style 'DRL graphic only'; 7 white islands per keychain, not 13)
PROJ_SIZE = (1.6, 0.9)          # mm, width x height
PROJ_GAP = 1.0                  # mm of black between a bar and its projector
PROJ_X = [596, 653, 709]        # px, lens centres (photo)


def _bar(p0, p1, w_mm):
    g = LineString([p0, p1]).buffer(w_mm / 2 * PX_PER_MM, cap_style=2, join_style=2)
    return _pts(g.intersection(LAMP_P.buffer(-DRL_CLEAR * PX_PER_MM, join_style=2)))


def _proj(i):
    hw, h = PROJ_SIZE[0] / 2 * PX_PER_MM, PROJ_SIZE[1] * PX_PER_MM
    x = PROJ_X[i]
    bar = Polygon(_bar(*DRL_BARS[i], DRL_W)).intersection(box(x - hw, 0, x + hw, 2000))
    y = bar.bounds[3] + PROJ_GAP * PX_PER_MM
    return [(x - hw, y), (x + hw, y), (x + hw, y + h), (x - hw, y + h)]


VENT_TAB_W = 0.66 * PX_PER_MM    # hood-vent tab width (px)

# ---------------------------------------------------------------- engraved lines
GROOVE_W = 0.62                 # 0.6 mm nominal (+0.02 so the polygonised round joins never dip under 0.6)


def _groove(pts, stop=None, fillet=True):
    """round-capped groove stroke; `stop` = black polygon (px) it runs into: the groove is cut exactly at its edge, so
    it lands on the black without a nub inside it. The acute white wedge left where it meets the black at an angle
    (< 0.5 mm wide, the nozzle could not print it anyway) is filled black as a small fillet of the black part.
    Returns a list of prims."""
    g = LineString(pts).buffer(GROOVE_W / 2 * PX_PER_MM, cap_style=1, join_style=1)
    if stop is None:
        return [dict(kind='poly', color='groove', pts=_pts(g))]
    S = Polygon(stop)
    g = g.difference(S)
    r = 0.26 * PX_PER_MM
    u = g.union(S)
    fil = u.buffer(r, join_style=1).buffer(-r, join_style=1).difference(u).intersection(g.buffer(2 * r))
    out = [dict(kind='poly', color='groove', pts=_pts(g))]
    for f in (_polys(fil) if fillet else []):
        if f.area > 0.5:
            out.append(dict(kind='poly', color='black', pts=_pts(f.buffer(0.3, join_style=2).difference(g))))
    return out


SPEC = dict(
    id='s650_mustang', name='Ford Mustang GT (S650)',
    ref='ref/front.jpg',
    units='px', px_left=531, px_right=1685, px_bottom=PX_BOTTOM, center_x=CX,
    # body outline: cowl/hood rear edge -> fender shoulder -> flat fender side -> splitter end -> splitter bottom
    # r3: the raised power dome steps down onto the fender tops at x ~850 px (photo), with the small V where the dome's
    #     edge meets the fender - a hood / fender step in the top edge like the G80's
    outline_half=[(CX, 564), (1000, 565), (885, 566), (866, 569), (850, 580.5), (836, 579), (790, 577.5), (730, 577),
                  (690, 578), (650, 582), (615, 590), (598, 598),
                  (578, 612), (560, 633), (546, 660), (537, 695), (532, 740), (531, 800), (531, 1000),
                  (533, 1036), (541, 1050), (570, 1057), (700, 1062), (760, 1068), (860, 1071), (CX, 1072)],
    prims=[
        # ---- headlight unit (black) + S650 light signature: three separate square-ended horizontal LED bars along
        #      the top of the three lamp modules, a small square projector under each
        dict(kind='poly', color='black', pts=LAMP),
        *[dict(kind='poly', color='white', pts=_bar(a, b, DRL_W)) for a, b in DRL_BARS],
        *([dict(kind='poly', color='white', pts=_proj(i)) for i in range(3)] if PROJ_ON else []),
        # ---- upper grille: black opening; honeycomb pockets = centre section + outer nostrils, separated by the
        #      flush black blades; the frame and the smooth gloss band along the bottom stay flush black
        dict(kind='poly', color='black', pts=GRILLE),
        dict(kind='geom', color='relief', geom=UPPER_MM, relief=REL_UPPER, mirror=False),   # centre + both nostrils
        # ---- hood vent (power-dome opening)
        dict(kind='poly', color='black', pts=[(912, 602), (918, 599), (960, 598), (1040, 596), (CX, 595), (CX, 629.5),
                                               (945, 630), (934, 628)]),
        # r6: the photo's power-dome opening is ONE continuous slot with a short tab hanging from its top edge at the
        #     centre (r5: a full-height divider split it into two slots) -> white tab 0.66 mm wide, ~40 % of the slot deep
        dict(kind='poly', color='white', mirror=False, pts=[(CX - VENT_TAB_W / 2, 588), (CX + VENT_TAB_W / 2, 588),
                                                           (CX + VENT_TAB_W / 2, 609), (CX - VENT_TAB_W / 2, 609)]),
        # ---- corner intake
        dict(kind='poly', color='black', pts=INTAKE),
        # ---- lower grille
        dict(kind='poly', color='black', pts=LOWER),
        *([dict(kind='geom', color='relief', geom=LOWER_MM, relief=REL_LOWER, mirror=False)] if LOWER_MESH else []),
        # ---- splitter lip
        #      (top edge 3 px lower at the centre than traced, so the body-colour band above it is >= 1.0 mm)
        #      (outer end kept pointed like the G80's splitter: measured, only a 0.05 mm2 tip is under 0.5 mm; a blunt
        #      end leaves a white 'foot' + a white wedge at the corner instead)
        dict(kind='poly', color='black', pts=[(CX, 1044), (800, 1044), (650, 1043.5), (560, 1044), (545, 1040),
                                               (520, 1038), (520, 1090), (CX, 1090)]),
        # ---- engraved body lines (0.6 mm): hood leading edge ('brow') landing on the lamp's top-edge kink, hood/fender
        #      shut lines (run out through the cowl edge like the G80's fender lines, land on the lamp top), corner-intake
        #      crease wrapping down onto the intake's top corner. Each is cut exactly at the black it runs into.
        #      r5: the brow and the intake crease end with a round cap clear of the black (no acute wedge, no fillet nub).
        #      r6: the crease hook ends 0.68 mm from the intake (r5: 0.45, under the 0.5 mm rule - measured with shapely);
        #      the fender lines leave the cowl edge and meet the lamp top ~at right angles (smaller sub-nozzle wedges)
        *_groove([(CX, 697), (900, 697), (780, 700), (742, 706)]),
        *_groove([(593, 588), (600, 603), (603, 640), (607, 680), (605.3, 730)], LAMP, fillet=False),   # r6: both ends ~normal to the edge they cross
        *_groove([(665, 836), (620, 832), (585, 835), (578, 848)]),
    ],
    badge=None,          # the library pony is not used (see the note at the top); the pony is the prim below
    badge_note='custom white left-galloping pony prim, on/off with BADGE_ON in spec.py',
    badge_on=False,
    tab=dict(y_mm=18.8),
)

if BADGE_ON:
    SPEC['prims'].append(dict(kind='poly', color='white', mirror=False, pts=_pts(PONY)))
