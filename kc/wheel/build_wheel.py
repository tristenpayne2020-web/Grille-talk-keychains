"""Steering-wheel keychain from the user's WheelKeychain_user.step (2026-10-01).
Two filaments: 1 = black, 2 = gray (the parts that are silver on the real wheel: paddle shifters, spoke button
panels, 12 o'clock stripe). Perforated dimples on the leather grips. Scaled to keychain size, paddles thickened.
usage (from kc/):  python wheel/build_wheel.py [--size 60]   -> wheel/out/"""
import os, sys, math
import numpy as np
import cadquery as cq
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from geom import polys, clean

SIZE = float(sys.argv[sys.argv.index('--size') + 1]) if '--size' in sys.argv else 60.0   # mm, wheel height
PAD_T = 1.2          # mm, paddle thickness after thickening (0.66 mm at scale is too fragile)
PERF_D, PERF_P, PERF_DEPTH = 0.9, 1.6, 0.6       # mm, dimple diameter / spacing along a row / depth
PERF_ROW = 1.35                                   # mm between staggered rows; rows fill the whole grip width
PERF_EDGE = 0.55                                  # mm of plain surface kept along every grip edge
STRIPE_W, STRIPE_T = 1.2, 0.6                                     # mm, 12 o'clock stripe width / inlay depth
# leather grips: between the carbon/leather joints the user modelled as notches in the rim outline, measured in the
# keychain frame (angle from +X, wheel centre): upper joints at +-22.8 deg from horizontal, lower ones at -53.3 deg
LEATHER = [(-53.3, 22.8), (157.2, 233.3)]
GRIP_W = 5.5         # mm in from the outer edge: the whole grip width, stopping short of the spokes
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- load: STEP frame x = wheel up, z = right, y = depth
solids = cq.importers.importStep(os.path.join(HERE, 'WheelKeychain_user.step')).solids().vals()
bb = max(solids, key=lambda s: s.Volume()).BoundingBox()
S = SIZE / (bb.xmax - bb.xmin)          # wheel height runs along x
Y0 = bb.ymin
# keychain frame: X = z, Y = x (wheel up = +Y), Z = y - Y0 (print up), all scaled by S
TF = np.array([[0, 0, S, 0], [S, 0, 0, 0], [0, S, 0, -Y0 * S], [0, 0, 0, 1]], float)
BOOL = dict(engine='manifold')


def mesh_of(shape, tol=0.02):
    """watertight mesh of a B-rep solid (via the STL exporter, which stitches shared edges)."""
    f = os.path.join(OUT, '_tmp.stl')
    cq.exporters.export(cq.Workplane().add(shape), f, tolerance=tol, angularTolerance=0.1)
    m = trimesh.load(f, force='mesh'); m.merge_vertices(); os.remove(f)
    if not m.is_volume:              # close the few hairline gaps of the STEP surfaces
        import manifold3d
        mm = manifold3d.Mesh(m.vertices.astype('float32'), m.faces.astype('uint32'))
        mm.merge()
        out = manifold3d.Manifold(mm).to_mesh()
        m = trimesh.Trimesh(out.vert_properties[:, :3], out.tri_verts)
    return m


body = trimesh.boolean.union([mesh_of(s).apply_transform(TF) for s in solids], **BOOL)


def section(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    g = Polygon()
    if s is not None:
        for e in s.discrete:
            g = g.symmetric_difference(Polygon(e[:, :2]).buffer(0))
    return clean(g.buffer(0))


def prism(g, z0, z1):
    parts = [trimesh.creation.extrude_polygon(p, z1 - z0).apply_translation([0, 0, z0]) for p in polys(g) if p.area > 1e-3]
    return trimesh.boolean.union(parts, **BOOL) if len(parts) > 1 else parts[0]


ztop = body.bounds[1][2]
lv = lambda y: (y - Y0) * S          # STEP depth y -> keychain Z
pads = clean(section(body, lv(3.5)).difference(section(body, lv(5.0)).buffer(0.03)))

# 1. paddles: thickened to PAD_T (gray)
body = trimesh.boolean.union([body, prism(pads, 0.0, PAD_T)], **BOOL)
gray = [prism(pads, -0.1, PAD_T)]

# 2. spoke button panels: everything above the face, minus the centre (badge) disc (gray)
face_z = lv(8.0)
front = unary_union([p for p in polys(section(body, face_z + 0.15)) if not p.contains(Point(0, 0))])
gray.append(prism(front.buffer(0.02), face_z, ztop + 0.5))

# 3. rim: leather grips (perforated) and the 12 o'clock stripe
top = section(body, lv(7.3))
outer = Polygon(max(polys(top), key=lambda p: p.area).exterior)
holes = [Polygon(h) for p in polys(top) for h in p.interiors]
rim_w = min(outer.exterior.distance(h) for h in holes)
rim = clean(outer.difference(outer.buffer(-rim_w * 0.98)).intersection(top))


def sector(a0, a1, r=200):
    return Polygon([(0, 0)] + [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 64)])


grip = clean(top.intersection(outer.difference(outer.buffer(-GRIP_W)))
             .intersection(unary_union([sector(a, b) for a, b in LEATHER])))
zone = grip.buffer(-PERF_EDGE - PERF_D / 2)
# staggered rows parallel to the outer edge, from just inside the edge across the whole grip
centres = []
k = 0
while PERF_EDGE + PERF_D / 2 + k * PERF_ROW < GRIP_W:
    ring = outer.buffer(-(PERF_EDGE + PERF_D / 2 + k * PERF_ROW)).exterior
    part = ring.intersection(zone)
    for line in getattr(part, 'geoms', [part]):
        if line.is_empty or line.geom_type != 'LineString' or line.length < PERF_D:
            continue
        for d in np.arange((PERF_P / 2 if k % 2 else 0) + PERF_D / 2, line.length - PERF_D / 2 + 1e-6, PERF_P):
            pt = line.interpolate(d)
            centres.append((pt.x, pt.y))
    k += 1
from scipy.spatial import cKDTree
V = body.vertices
kd = cKDTree(V[:, :2])
dimples = []
for x, y in centres:
    near = kd.query_ball_point([x, y], PERF_D / 2)  # local top surface under the dimple (the grip is domed)
    zt = np.median(V[near, 2]) if near else ztop
    dimples.append(trimesh.creation.cylinder(radius=PERF_D / 2, height=PERF_DEPTH + 2, sections=24)
                   .apply_translation([x, y, zt - PERF_DEPTH + (PERF_DEPTH + 2) / 2]))
if dimples:
    body = trimesh.boolean.difference([body, trimesh.boolean.union(dimples, **BOOL)], **BOOL)

stripe = rim.intersection(box(-STRIPE_W / 2, 0, STRIPE_W / 2, SIZE))
gray.append(prism(stripe, ztop - STRIPE_T, ztop + 0.5))

# ---------------------------------------------------------------- split into the two filaments
G = trimesh.boolean.union(gray, **BOOL)
mg = trimesh.boolean.intersection([body, G], **BOOL)
mb = trimesh.boolean.difference([body, G], **BOOL)
mb.export(os.path.join(OUT, 'wheel_black.stl')); mg.export(os.path.join(OUT, 'wheel_gray.stl'))
np.save(os.path.join(OUT, 'outline_xy.npy'), np.asarray(outer.exterior.coords))
print(f'scale {S:.3f}  size {body.extents.round(2)} mm  rim width {rim_w:.2f} mm  dimples {len(centres)}  '
      f'black {mb.volume:.0f} mm3  gray {mg.volume:.0f} mm3  watertight {mb.is_watertight}/{mg.is_watertight}')

# ---------------------------------------------------------------- Creality Print 3MFs (same master settings as the cars)
import k2config, write3mf, plate, render
r3d = os.path.join(OUT, 'wheel_render.png')
try:
    render.render3d([(mb, (0.12, 0.12, 0.13)), (mg, (0.62, 0.63, 0.65))], r3d, elev=55, azim=-10, zoom=1.3)
except Exception as e:          # needs a display (on Linux: Xvfb + DISPLAY); the 3MF still gets written
    print('render skipped:', e); r3d = None
parts = [dict(name='Wheel (black)', mesh=mb, extruder=1), dict(name='Silver parts (gray)', mesh=mg, extruder=2)]
name = 'Steering wheel keychain'
write3mf.write_3mf(os.path.join(OUT, 'wheel_single.3mf'), parts, k2config.build(), object_name=name,
                   app_version=k2config.VERSION, thumbnail_png=r3d, positions=[(130.0, 130.0)])
placed, tower_xy, how = plate.best_layout(outer)
cfgp = k2config.build({'wipe_tower_x': [f'{tower_xy[0]:.1f}'], 'wipe_tower_y': [f'{tower_xy[1]:.1f}']})
write3mf.write_3mf(os.path.join(OUT, f'wheel_PLATE_{len(placed)}x.3mf'), parts, cfgp, object_name=name,
                   app_version=k2config.VERSION, thumbnail_png=r3d, positions=placed)
plate.layout_png(outer, placed, tower_xy, (40, 25), os.path.join(OUT, 'wheel_plate_layout.png'))
print('plate', len(placed), how)

# on the user's PC: copy the print files next to the car keychains (a separate folder, so finalize.py never wipes it)
dl = os.path.join(os.path.expanduser('~'), 'Downloads', 'GrilleTalk_Extras', 'Steering_Wheel')
if os.name == 'nt':
    import shutil
    os.makedirs(dl, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(('.3mf', '.stl', '.png')):
            shutil.copy2(os.path.join(OUT, f), dl)
    print('copied to', dl)
