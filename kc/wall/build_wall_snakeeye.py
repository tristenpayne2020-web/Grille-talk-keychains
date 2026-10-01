"""G80 wall key holder (user's G80_WallKeyholder_user.step), custom-colour snake-eye version.
3 filaments like the custom-colour keychains: 1 = black (back plate, sensor dots, tow-hook ring),
2 = body colour (body with the key hooks, hood), 3 = white (the snake-eye DRL bars).
Changes vs the user's STEP: stock DRL pieces replaced by the snake-eye bars (kc/cars/_snakeeye.py TEMPLATE, fitted
to these lamps); BMW roundel removed and its hole filled flush (no-logo rule).
usage (from anywhere):  python kc/wall/build_wall_snakeeye.py      -> kc/wall/out/"""
import os, sys
import numpy as np
import cadquery as cq
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__))
KC = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(KC, 'lib')); sys.path.insert(0, os.path.join(KC, 'cars'))
from geom import polys, clean
import _snakeeye

HOOD = 'body'           # user 2026-10-01: hood in the body colour ('black' = carbon hood)
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
BOOL = dict(engine='manifold')


def section(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1]); g = Polygon()
    if s is not None:
        for e in s.discrete:
            g = g.symmetric_difference(Polygon(e[:, :2]).buffer(0))
    return clean(g.buffer(0))


def brep_section(shape, z):
    """exact cross-section of a B-rep solid at height z, as shapely geometry"""
    faces = cq.Workplane().add(shape).section(z).faces().vals()
    tris = []
    for f in faces:
        v, t = f.tessellate(0.01)
        tris += [Polygon([(v[a].x, v[a].y), (v[b].x, v[b].y), (v[c].x, v[c].y)]) for a, b, c in t]
    return clean(unary_union([x.buffer(0) for x in tris]).buffer(0.001).buffer(-0.001)) if tris else Polygon()


def mesh_of(shape, tol=0.03):
    f = os.path.join(OUT, '_tmp.stl')
    cq.exporters.export(cq.Workplane().add(shape), f, tolerance=tol, angularTolerance=0.1)
    m = trimesh.load(f, force='mesh'); m.merge_vertices(); os.remove(f)
    if not m.is_volume:
        # a few hairline gaps in the STEP surfaces: rebuild the part as 0.2 mm slices of its exact (B-rep)
        # cross-sections; the printer lays it down in 0.2 mm layers anyway, so this is print-identical and watertight
        zb0, zb1 = m.bounds[:, 2]                          # exact heights (B-rep bounding boxes are loose)
        n = max(1, int(round((zb1 - zb0) / 0.2)))
        dz = (zb1 - zb0) / n
        slabs = []
        for k in range(n):
            g = brep_section(shape, zb0 + (k + 0.5) * dz)
            slabs += [trimesh.creation.extrude_polygon(p, dz).apply_translation([0, 0, zb0 + k * dz]) for p in polys(g) if p.area > 1e-3]
        slabs = [x for x in slabs if x.is_volume]
        if slabs:                      # (an empty, zero-volume artifact solid in the STEP has no slices)
            m = trimesh.boolean.union(slabs, **BOOL) if len(slabs) > 1 else slabs[0]
    return m


def prism(g, z0, z1):
    ps = [trimesh.creation.extrude_polygon(p, z1 - z0).apply_translation([0, 0, z0]) for p in polys(g) if p.area > 1e-3]
    return trimesh.boolean.union(ps, **BOOL) if len(ps) > 1 else ps[0]


sol = cq.importers.importStep(os.path.join(HERE, 'G80_WallKeyholder_user.step')).solids().vals()
M = [mesh_of(s) for s in sol]
info = [(i, s.BoundingBox(), s.Volume()) for i, s in enumerate(sol)]
# identify the parts by role (sizes from the user's file)
base = max((x for x in info if x[1].zmin < 0), key=lambda x: x[2])[0]                  # back plate below z = 0
body = max(info, key=lambda x: x[2] if x[1].zmax > 10 else 0)[0]                         # body with the key hooks
hood = max((x for x in info if x[0] not in (base, body)), key=lambda x: x[2])[0]
drls = [x[0] for x in info if 400 < x[2] < 700]                                           # the two stock DRL pieces
roundel = [x[0] for x in info if 20 < x[2] < 50 and abs((x[1].xmin + x[1].xmax) / 2) < 10]  # roundel quarters
tiny = [x[0] for x in info if x[2] < 1]
small = [x[0] for x in info if x[0] not in (base, body, hood, *drls, *roundel, *tiny)]  # sensor dots, tow-hook ring
z0, z1 = M[drls[0]].bounds[:, 2]                                                          # face layer heights

# ---------------------------------------------------------------- snake-eye DRLs
base_s = section(M[base], M[base].bounds[1][2] - 0.1)          # top of the back plate (what shows through the lamps)
face = unary_union([section(M[i], (z0 + z1) / 2) for i in (body, hood)])
bars = []
for d in drls:
    old = section(M[d], (z0 + z1) / 2)
    # the lamp = black back plate showing outside the body/hood around the old DRL piece
    # (limited to the stock DRL's surroundings: the black shows through all round the car's edge too)
    near = box(*old.bounds).buffer(3.0, join_style=2)
    cands = [Polygon(p.exterior) for p in polys(clean(base_s.difference(face.buffer(0.05)).intersection(near))) if p.intersects(old)]
    lamp = max(cands, key=lambda p: p.intersection(old).area).union(old).buffer(0)
    bars.append(_snakeeye._template_bars(lamp, lamp.centroid.x > 0))
white = prism(unary_union(bars), z0, z1)

# ---------------------------------------------------------------- roundel removed: fill its hole flush
body_s = section(M[body], (z0 + z1) / 2)
hood_s = section(M[hood], (z0 + z1) / 2)
r_c = unary_union([section(M[i], (z0 + z1) / 2) for i in roundel]).centroid
holes = [Polygon(h) for p in polys(body_s) for h in p.interiors] + [Polygon(h) for p in polys(hood_s) for h in p.interiors]
fill = unary_union([h for h in holes if h.contains(r_c) or h.distance(r_c) < 1.0])
# the roundel sits in the body-coloured nose (below the hood): its hole is filled flush in the body colour,
# except where it would overlap the hood piece itself
fill_body = fill.difference(hood_s.buffer(0.02))
fill_hood = fill.intersection(hood_s.buffer(0.02)).difference(body_s)

parts = {'black': [M[base]] + [M[i] for i in small], 'body': [M[body]]}
parts['black' if HOOD == 'black' else 'body'].append(M[hood])
if not fill_body.is_empty:
    parts['body'].append(prism(fill_body, z0, z1))
if not fill_hood.is_empty and fill_hood.area > 0.5:
    parts['black' if HOOD == 'black' else 'body'].append(prism(fill_hood, z0, z1))
mk = {k: trimesh.boolean.union(v, **BOOL) if len(v) > 1 else v[0] for k, v in parts.items()}
mk['body'] = trimesh.boolean.difference([mk['body'], mk['black']], **BOOL)     # no overlap between filaments
mk['white'] = trimesh.boolean.difference([white, trimesh.boolean.union([mk['black'], mk['body']], **BOOL)], **BOOL)
for k, m in mk.items():
    m.export(os.path.join(OUT, f'g80_wall_snakeeye_{k}.stl'))
print('parts', {k: round(m.volume) for k, m in mk.items()}, 'watertight', {k: m.is_watertight for k, m in mk.items()},
      'size', np.round(trimesh.util.concatenate(list(mk.values())).extents, 1))

# ---------------------------------------------------------------- Creality Print 3MF (3 filaments, master settings)
import k2config, write3mf, render, export3
r3d = os.path.join(OUT, 'g80_wall_snakeeye_render.png')
try:
    render.render3d([(mk['body'], (0.55, 0.57, 0.60)), (mk['black'], (0.10, 0.10, 0.11)), (mk['white'], (0.95, 0.95, 0.93))],
                    r3d, elev=60, azim=-10, zoom=1.3)
except Exception as e:
    print('render skipped:', e); r3d = None
prt = [dict(name='Base, hood, details (black)', mesh=mk['black'], extruder=1),
       dict(name='Body (custom colour)', mesh=mk['body'], extruder=2),
       dict(name='Snake-eye lights (white)', mesh=mk['white'], extruder=3)]
cfg = k2config.build_n(3, export3.COLOURS, export3.FLUSH3)
write3mf.write_3mf(os.path.join(OUT, 'g80_wall_snakeeye.3mf'), prt, cfg, object_name='G80 wall key holder (snake-eye, custom colour)',
                   app_version=k2config.VERSION, thumbnail_png=r3d, positions=[(130.0, 130.0)])
if os.name == 'nt':
    import shutil
    dl = os.path.join(os.path.expanduser('~'), 'Downloads', 'GrilleTalk_Extras', 'G80_Wall_Key_Holder_snake_eye')
    os.makedirs(dl, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(('.3mf', '.stl', '.png')):
            shutil.copy2(os.path.join(OUT, f), dl)
    print('copied to', dl)
