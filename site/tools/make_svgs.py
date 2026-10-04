"""SVG layers per launch car from the 2D design maps (geom.build_maps), KC_BADGE=0.

site/build/svg/<id>/outline.svg   body outline incl. tab and hole
site/build/svg/<id>/black.svg     black detail regions
site/build/svg/<id>/white.svg     white regions (body cap + light islands)
site/build/svg/<id>/lights.svg    white islands only (DRLs and lamps)
site/build/svg/<id>/drl.svg       the two largest light islands: the G80's drives the hero light-up
Coordinates are millimetres, y flipped to SVG (down). viewBox covers the outline with a 1 mm margin.
usage: python site/tools/make_svgs.py [id,id,...]
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
KC = os.path.join(ROOT, 'kc')
sys.path.insert(0, os.path.join(KC, 'lib'))
os.environ['KC_BADGE'] = '0'
import geom, export  # noqa: E402
from shapely.geometry import Polygon, MultiPolygon  # noqa: E402

OUT = os.path.join(ROOT, 'site', 'build', 'svg')


def polys(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon)]


def ring_d(coords, H):
    pts = [f'{x:.3f} {H - y:.3f}' for x, y in coords]
    return 'M' + ' L'.join(pts) + 'Z'


def path_d(g, H):
    d = []
    for p in polys(g):
        d.append(ring_d(p.exterior.coords, H))
        d += [ring_d(i.coords, H) for i in p.interiors]
    return ''.join(d)


def svg(d, vb, fill):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
            f'<path fill="{fill}" fill-rule="evenodd" d="{d}"/></svg>\n')


def lights_of(white):
    """White islands: every white polygon except the main body cap."""
    ps = sorted(polys(white), key=lambda p: p.area, reverse=True)
    return MultiPolygon(ps[1:]) if len(ps) > 1 else Polygon()


def build(car_id, spec_rel):
    spec = export.load_spec(os.path.join(KC, spec_rel))
    M = geom.build_maps(spec)
    x0, y0, x1, y1 = M['outline'].bounds
    H = y1                                        # flip: svg_y = H - y
    vb = f'{x0 - 1:.3f} {-1:.3f} {x1 - x0 + 2:.3f} {y1 - y0 + 2:.3f}'
    od = os.path.join(OUT, car_id)
    os.makedirs(od, exist_ok=True)
    outline = M['outline'].difference(M['hole'])
    lights = lights_of(M['white'])
    drl = MultiPolygon(sorted(polys(lights), key=lambda p: p.area, reverse=True)[:2])   # the two light signatures
    layers = dict(outline=outline, black=M['black'], white=M['white'], lights=lights, drl=drl)
    for name, g in layers.items():
        with open(os.path.join(od, f'{name}.svg'), 'w') as f:
            f.write(svg(path_d(g, H), vb, '#fff' if name != 'black' else '#000'))
    print(car_id, {k: len(polys(v)) for k, v in layers.items()})


if __name__ == '__main__':
    launch = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    pkg = {c['id']: c for c in json.load(open(os.path.join(KC, 'cars_pkg.json')))}
    ids = sys.argv[1].split(',') if len(sys.argv) > 1 else [c['id'] for c in launch['cars']]
    for i in ids:
        build(i, pkg[i]['spec'])
