"""Snake-eye DRL variant (user request 2026-10-01, from their G80/G87 photos): the stock DRL is removed and each
headlight gets two short, near-vertical white bars, one near the outer end of the lamp and one past its middle.
make(base_spec, drl_index) returns a new spec dict; the original approved spec is never modified."""
import copy, os, sys
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union, substring
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import geom

BAR_W = 0.85        # mm, bar width (G80 DRL strokes are ~0.75-0.8)
MARGIN = 0.6        # mm of black kept around each bar
FRACS = (0.20, 0.58)  # bar positions along the lamp, from its outer end
LEAN = 0.35         # mm the bar top leans outward (photos: bars tilt slightly with the lamp)


def _bars(lamp, outer_is_left, length=1.0, lean_mm=LEAN):
    x0, y0, x1, y1 = lamp.bounds
    inner = lamp.buffer(-MARGIN - BAR_W / 2)
    out = []
    for f in FRACS:
        x = x0 + f * (x1 - x0) if outer_is_left else x1 - f * (x1 - x0)
        lean = -lean_mm if outer_is_left else lean_mm
        seg = LineString([(x - lean, y0 - 5), (x + lean, y1 + 5)]).intersection(inner)
        if seg.is_empty:
            continue
        if length < 1.0:                                   # shorten about the bar's middle
            L = seg.length
            seg = substring(seg, L * (1 - length) / 2, L * (1 + length) / 2)
        out.append(seg.buffer(BAR_W / 2, cap_style=2))
    return unary_union(out)


# The user's own snake-eye DRL design (BMW_M3_G80_snake_eye_new.step, 2026-10-01): the two '7'-shaped light bars of
# the viewer's RIGHT headlight of the G80, in the G80 spec frame (mm), and that headlight's bounding box. Every
# snake-eye variant uses these: copied 1:1 on the G80, fitted to other cars' lamps by lamp size and position.
TEMPLATE = [[(25.644, 27.061), (25.644, 27.424), (27.944, 27.412), (28.317, 26.923), (27.556, 24.02), (26.707, 24.054), (26.821, 26.851)], [(33.554, 28.331), (32.03, 28.6), (32.03, 28.971), (34.93, 28.971), (35.298, 28.489), (34.256, 24.673), (33.406, 24.707)]]
TEMPLATE_LAMP = (19.857, 22.879, 37.417, 30.149)


def _template_bars(lamp, right_side):
    """Fit the template bars into one lamp: each bar keeps its position as a fraction of the lamp's bounding box
    and is scaled by the lamp-height ratio (shape kept, not stretched). Left lamps get the mirror image."""
    tx0, ty0, tx1, ty1 = TEMPLATE_LAMP
    x0, y0, x1, y1 = lamp.bounds
    k = (y1 - y0) / (ty1 - ty0)
    out = []
    for pts in TEMPLATE:
        bar = Polygon(pts)
        c = bar.centroid
        fx, fy = (c.x - tx0) / (tx1 - tx0), (c.y - ty0) / (ty1 - ty0)
        if not right_side:
            bar, fx = affinity.scale(bar, -1, 1, origin=(c.x, c.y)), 1 - fx
        bar = affinity.scale(bar, k, k, origin=(c.x, c.y))
        bar = affinity.translate(bar, x0 + fx * (x1 - x0) - c.x, y0 + fy * (y1 - y0) - c.y)
        out.append(bar)
    return unary_union(out).intersection(lamp.buffer(-0.5))


def make(base, drl_index, new_id, new_name, length=1.0, lean=LEAN, style='template'):
    """style 'template' (default): the user's 7-shaped bars from TEMPLATE. style 'bars': the first, plain straight
    bars (length: fraction of the in-lamp length kept; lean: mm the bar top leans outward)."""
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
    if style == 'template':
        bars = unary_union([_template_bars(p, p.centroid.x > 0) for p in lamps])
    else:
        bars = unary_union([_bars(p, p.centroid.x < 0, length, lean) for p in lamps])
    lamps_u = unary_union(lamps)
    # back into the pre-placement mm frame ('geom' prims are mm in every spec ; build_maps applies translate(dy) then scale(k))
    pre = affinity.translate(affinity.scale(bars, 1 / k, 1 / k, origin=(0, 0)), 0, -dy)
    unplace = lambda g: affinity.translate(affinity.scale(g, 1 / k, 1 / k, origin=(0, 0)), 0, -dy)
    spec['prims'].append(dict(kind='geom', color='black', geom=unplace(lamps_u), mirror=False))
    spec['prims'].append(dict(kind='geom', color='white', geom=pre, mirror=False))
    spec['id'], spec['name'] = new_id, new_name
    spec['_lamps'] = len(lamps)
    return spec
