"""Keychain finger spinners with a topology-optimised look, around a 6804 bearing (20 x 32 x 7 mm).

2D layout (this script): a bearing ring, a keyring lug and a truss of tapered struts between them, filleted at the
joints. The ring and lug are full thickness (7.4 mm, the bearing sits flush); the struts are thinner (5.2 mm, centred),
so the voxel remesh + smoothing in Blender (spinner_blender.py) blends them into organic, generative-design forms.
The bearing pocket (32.25 mm, a light press in PETG-CF) and the keyring hole are cut after smoothing, so they stay exact.

usage: python spinner/make_spinners.py      (writes spinner/out/*_raw.stl, then runs Blender for print STLs + renders)
"""
import os, json, math, subprocess, sys
import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
BEARING = dict(name='6804', id=20.0, od=32.0, w=7.0)
POCKET_D = 32.25                       # PETG-CF light press fit; print a test ring first
T_FULL, T_STRUT = 7.4, 5.2
RING_R = POCKET_D / 2 + 4.0            # 4 mm wall round the bearing
LUG_HOLE_D = 4.6
BLENDER = os.environ.get('BLENDER', r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')


def strut(a, b, ra, rb, n=24):
    """tapered capsule from a (radius ra) to b (radius rb)"""
    return unary_union([Point(a).buffer(ra, n), Point(b).buffer(rb, n)]).convex_hull


def arc_strut(pts, r0, r1):
    """a curved strut through pts, tapering from r0 to r1"""
    k = len(pts) - 1
    return unary_union([strut(pts[i], pts[i + 1], r0 + (r1 - r0) * i / k, r0 + (r1 - r0) * (i + 1) / k) for i in range(k)])


def smooth(g, r=1.6):
    return g.buffer(r, 32).buffer(-r, 32).buffer(-0.4, 32).buffer(0.4, 32)


def ring_and_lug(lug):
    return Point(0, 0).buffer(RING_R, 96), Point(lug).buffer(6.6, 64)


def web(envelope, keep, seed, spacing=11.0, w=(0.95, 1.55)):
    """Topology-optimised look: Voronoi cells inside the envelope, shrunk to leave struts of varying width
    (thicker near the bearing, where the load path is), with filleted corners. Returns the solid web."""
    from shapely.ops import voronoi_diagram
    from shapely.geometry import MultiPoint
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = envelope.bounds
    pts = []
    for _ in range(4000):                           # rejection-sampled seeds (Poisson-disc-ish)
        p = (rng.uniform(x0, x1), rng.uniform(y0, y1))
        if envelope.contains(Point(p)) and all(math.dist(p, q) > spacing for q in pts):
            pts.append(p)
    voids = []
    for cell in voronoi_diagram(MultiPoint(pts), envelope=envelope.buffer(20)).geoms:
        c = cell.intersection(envelope.buffer(-1.5)).difference(keep)
        d = c.centroid.distance(Point(0, 0)) if not c.is_empty else 0
        half = w[1] - (w[1] - w[0]) * min(1, d / 45)    # struts thin out away from the bearing
        v = c.buffer(-half, 16).buffer(-1.2, 16).buffer(1.2, 16)   # rounded voids
        if v.area > 6:
            voids.append(v)
    return envelope.difference(unary_union(voids))


def design_talon():
    """'Talon': a teardrop lattice web from the bearing to the keyring (owner: no hook, only the optimised web)."""
    L = (47.0, -7.0)
    env = unary_union([Point(0, 0).buffer(RING_R), Point(L).buffer(7), Point(24, 16).buffer(6),
                       Point(42, 8).buffer(5)]).convex_hull
    return L, env, 11


def design_karambit():
    """'Karambit': a hooked blade curving up and over from the bearing, the blade itself filled with the lattice."""
    L = (-2.0, -30.0)
    spine = [(14, 9, 13), (26, 22, 12.5), (40, 31, 11), (54, 32, 9), (65, 26, 6.5), (71, 16, 4), (73, 6, 2.6)]
    blade = unary_union([strut(a[:2], b[:2], a[2], b[2]) for a, b in zip(spine, spine[1:])])
    blade = blade.difference(Point(54, 6).buffer(15, 64))          # the hook's inner curve
    env = unary_union([Point(0, 0).buffer(RING_R), blade, unary_union([Point(0, -8).buffer(12), Point(L).buffer(7)]).convex_hull])
    return L, env.buffer(2.5, 32).buffer(-2.5, 32), 23


def design_shield():
    """'Shield': an oval frame, bearing at the top, keyring at the bottom, a lattice web between (owner's reference)."""
    L = (0.0, -47.0)
    env = unary_union([Point(0, 0).buffer(RING_R + 1.5), Point(0, -36).buffer(15), Point(L).buffer(7)]).convex_hull
    return L, env, 5


DESIGNS = {'talon': design_talon, 'karambit': design_karambit, 'shield': design_shield}


def build(name):
    L, env, seed = DESIGNS[name]()
    ring, lug = ring_and_lug(L)
    keep = unary_union([ring.buffer(1.5), lug.buffer(1.5)])
    full = smooth(unary_union([ring, lug]))
    web_ = smooth(web(env, keep, seed).difference(Point(0, 0).buffer(POCKET_D / 2 + 0.5)), 0.5)
    # extrude: full-thickness ring + lug, thinner centred struts
    parts = []
    for g, t in ((full, T_FULL), (web_, T_STRUT)):
        for p in getattr(g, 'geoms', [g]):
            m = trimesh.creation.extrude_polygon(p, t)
            m.apply_translation((0, 0, -t / 2))
            parts.append(m)
    raw = trimesh.util.concatenate(parts)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f'{name}_raw.stl')
    raw.export(path)
    b = unary_union([full, web_]).bounds
    return dict(name=name, raw=path, lug=L, size=[round(b[2] - b[0], 1), round(b[3] - b[1], 1), T_FULL])


def main():
    jobs = [build(n) for n in DESIGNS]
    job = dict(designs=jobs, out=OUT, pocket_d=POCKET_D, t_full=T_FULL, lug_hole_d=LUG_HOLE_D, bearing=BEARING)
    jp = os.path.join(OUT, 'job.json')
    json.dump(job, open(jp, 'w'), indent=1)
    for j in jobs:
        print(j['name'], j['size'], 'mm')
    r = subprocess.run([BLENDER, '--background', '--factory-startup', '--python', os.path.join(HERE, 'spinner_blender.py'), '--', jp],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(r.stdout[-1500:] if 'SPINNERS_DONE' not in r.stdout else 'blender ok')
    if 'SPINNERS_DONE' not in r.stdout:
        print(r.stderr[-1500:]); sys.exit(1)


if __name__ == '__main__':
    main()
