"""Snake-eye DRL variant (user request 2026-10-01, from their G80/G87 photos): the stock DRL is removed and each
headlight gets two short, near-vertical white bars, one near the outer end of the lamp and one past its middle.
make(base_spec, drl_index) returns a new spec dict; the original approved spec is never modified."""
import copy, os, sys
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import geom

BAR_W = 0.85        # mm, bar width (G80 DRL strokes are ~0.75-0.8)
MARGIN = 0.6        # mm of black kept around each bar
FRACS = (0.20, 0.58)  # bar positions along the lamp, from its outer end
LEAN = 0.35         # mm the bar top leans outward (photos: bars tilt slightly with the lamp)


def _bars(lamp, outer_is_left):
    x0, y0, x1, y1 = lamp.bounds
    inner = lamp.buffer(-MARGIN - BAR_W / 2)
    out = []
    for f in FRACS:
        x = x0 + f * (x1 - x0) if outer_is_left else x1 - f * (x1 - x0)
        lean = -LEAN if outer_is_left else LEAN
        seg = LineString([(x - lean, y0 - 5), (x + lean, y1 + 5)]).intersection(inner)
        if seg.is_empty:
            continue
        out.append(seg.buffer(BAR_W / 2, cap_style=2))
    return unary_union(out)


def make(base, drl_index, new_id, new_name):
    spec = copy.deepcopy(base)
    old = spec['prims'].pop(drl_index)
    M = geom.build_maps(spec)
    dy, k = M['place']
    # the lamps: black polygons (holes filled - in the STEP-based G80 the DRL is a hole in the lamp) that cover the
    # old DRL; each lamp is repainted solid black, then the bars go on top
    F = geom.Frame(base)
    g = geom.sym(geom.prim_geom(old, F), old.get('mirror', True))
    g = affinity.scale(affinity.translate(g, 0, dy), k, k, origin=(0, 0))
    old_drl = geom.polys(g)
    lamps = []
    for p in geom.polys(M['black']):
        solid = Polygon(p.exterior)
        if any(solid.contains(d.representative_point()) and d.area < 0.5 * solid.area for d in old_drl):
            lamps.append(solid)
    bars = unary_union([_bars(p, p.centroid.x < 0) for p in lamps])
    lamps_u = unary_union(lamps)
    # back into the pre-placement mm frame ('geom' prims are mm in every spec ; build_maps applies translate(dy) then scale(k))
    pre = affinity.translate(affinity.scale(bars, 1 / k, 1 / k, origin=(0, 0)), 0, -dy)
    unplace = lambda g: affinity.translate(affinity.scale(g, 1 / k, 1 / k, origin=(0, 0)), 0, -dy)
    spec['prims'].append(dict(kind='geom', color='black', geom=unplace(lamps_u), mirror=False))
    spec['prims'].append(dict(kind='geom', color='white', geom=pre, mirror=False))
    spec['id'], spec['name'] = new_id, new_name
    spec['_lamps'] = len(lamps)
    return spec
