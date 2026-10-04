"""Build one GLB per launch car from the production STLs (kc/cars/<id>/out/production/).

Scene (glTF units are metres, +Y up, face toward +Z):
  keychain            node, origin at the keyring hole centre (the pivot the chain hangs from)
    body              white cap mesh, material "body" (recoloured per variant on the site)
    details           black base mesh, material "details"
  link_0 .. link_4    short chain hanging down from the hole, separate nodes so the site can drive them
  ring                split ring at the end of the chain
    lights            white light signatures (material "lights"), never recoloured

The chain and ring are modelled once here with trimesh (no Blender needed). Output: site/build/glb_raw/<id>.glb.
Compression (meshopt) is a separate step: node tools/compress_glb.mjs.

usage: python site/tools/make_glb.py [id,id,...]
"""
import json, os, sys
import numpy as np
import trimesh
import shapely
from trimesh.visual.material import PBRMaterial

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
KC = os.path.join(ROOT, 'kc')
sys.path.insert(0, os.path.join(KC, 'lib'))
os.environ.setdefault('KC_BADGE', '0')
import geom, export  # noqa: E402

MM = 0.001
OUT = os.path.join(ROOT, 'site', 'build', 'glb_raw')

# chain geometry, mm
WIRE = 0.55          # link wire radius
LINK_R = 1.55        # radius of the link's end arcs (centre line)
LINK_S = 3.2         # straight part of the link (centre line)
PITCH = 2 * LINK_R + LINK_S - 2 * WIRE - 0.35   # centre-to-centre distance of interlocked links
N_LINKS = 5
RING_R = 8.0         # split ring centre-line radius (16 mm ring keeps the hanging length close to the body height)
RING_WIRE = 0.65


def stadium_tube(r, s, wire, n_path=72, n_tube=14):
    """Closed tube swept along a stadium (two arcs of radius r joined by straights of length s), long axis = Y."""
    pts = []
    per_arc = n_path // 2 - 4
    for k in range(per_arc + 1):                              # top arc
        a = np.pi * k / per_arc
        pts.append((r * np.cos(a), s / 2 + r * np.sin(a)))
    for k in range(1, 4):
        pts.append((-r, s / 2 - s * k / 4))
    for k in range(per_arc + 1):                              # bottom arc
        a = np.pi + np.pi * k / per_arc
        pts.append((r * np.cos(a), -s / 2 + r * np.sin(a)))
    for k in range(1, 4):
        pts.append((r, -s / 2 + s * k / 4))
    P = np.array([(x, y, 0.0) for x, y in pts])
    return sweep(P, wire, n_tube)


def sweep(P, wire, n_tube):
    n = len(P)
    T = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    T /= np.linalg.norm(T, axis=1)[:, None]
    Z = np.array([0, 0, 1.0])
    V, F = [], []
    for i in range(n):
        nrm = np.cross(T[i], Z); nrm /= np.linalg.norm(nrm)
        for j in range(n_tube):
            a = 2 * np.pi * j / n_tube
            V.append(P[i] + wire * (np.cos(a) * nrm + np.sin(a) * Z))
    for i in range(n):
        for j in range(n_tube):
            a, b = i * n_tube + j, i * n_tube + (j + 1) % n_tube
            c, d = ((i + 1) % n) * n_tube + j, ((i + 1) % n) * n_tube + (j + 1) % n_tube
            F += [(a, c, b), (b, c, d)]
    m = trimesh.Trimesh(np.array(V), np.array(F), process=True)
    m.fix_normals()
    return m


def split_ring():
    """Two coils of a flat split ring, slightly offset in Z, ring plane = XY."""
    n = 120
    parts = []
    for dz in (-RING_WIRE * 0.95, RING_WIRE * 0.95):
        a = np.linspace(0, 2 * np.pi, n, endpoint=False)
        P = np.stack([RING_R * np.cos(a), RING_R * np.sin(a), np.full(n, dz)], 1)
        parts.append(sweep(P, RING_WIRE, 12))
    return trimesh.util.concatenate(parts)


def mat(name, rgb, metal, rough):
    return PBRMaterial(name=name, baseColorFactor=list(rgb) + [1.0], metallicFactor=metal, roughnessFactor=rough,
                       doubleSided=False)


def shaded(m, material):
    m = m.copy()
    m.merge_vertices()
    m = trimesh.graph.smooth_shade(m, angle=np.radians(28))
    m.visual = trimesh.visual.TextureVisuals(material=material)
    return m


def spec_path(car_id):
    pkg = {c['id']: c for c in json.load(open(os.path.join(KC, 'cars_pkg.json')))}
    return os.path.join(KC, pkg[car_id]['spec'])


def build(car_id):
    prod = os.path.join(ROOT, 'site', 'build', 'geom', car_id, 'production')   # logo-free rebuild, build_geometry.py
    white = trimesh.load(os.path.join(prod, f'{car_id}_production_white.stl'))
    black = trimesh.load(os.path.join(prod, f'{car_id}_production_black.stl'))
    spec = export.load_spec(spec_path(car_id))
    M = geom.build_maps(spec)
    geom.repair_min_width(M)
    geom.split_white(M)                      # same body-paint vs white-light split as the custom-colour print
    tx, ty = M['tab_center']
    # white solids whose footprint sits in a light island stay white whatever the body colour
    light_zone = M['white_light'].buffer(0.3)
    body_parts, light_parts = [], []
    for part in white.split(only_watertight=False):
        v = part.vertices[:, :2]
        is_light = not light_zone.is_empty and shapely.contains_xy(light_zone, v[:, 0], v[:, 1]).mean() > 0.5
        (light_parts if is_light else body_parts).append(part)
    white_body = trimesh.util.concatenate(body_parts)
    # pivot at the hole centre, mid thickness
    shift = np.array([-tx, -ty, -1.5])
    meshes = [white_body, black] + light_parts
    for m in meshes:
        m.apply_translation(shift)
        m.apply_scale(MM)

    body = shaded(white_body, mat('body', (0.95, 0.95, 0.94), 0.0, 0.55))
    details = shaded(black, mat('details', (0.012, 0.012, 0.014), 0.0, 0.72))
    metal = mat('metal', (0.80, 0.81, 0.83), 1.0, 0.28)

    scene = trimesh.Scene()
    scene.graph.update(frame_to='keychain', frame_from='world', matrix=np.eye(4))
    scene.add_geometry(body, node_name='body', geom_name='body', parent_node_name='keychain')
    scene.add_geometry(details, node_name='details', geom_name='details', parent_node_name='keychain')
    if light_parts:
        lights = shaded(trimesh.util.concatenate(light_parts), mat('lights', (0.97, 0.97, 0.96), 0.0, 0.5))
        scene.add_geometry(lights, node_name='lights', geom_name='lights', parent_node_name='keychain')

    link = stadium_tube(LINK_R, LINK_S, WIRE)
    link.apply_scale(MM)
    link_len = (2 * LINK_R + LINK_S) * MM
    # link_0 threads the hole: its top arc passes through the hole, then the chain falls straight down
    y = -(link_len / 2 - (LINK_R - 0.2) * MM)
    for i in range(N_LINKS):
        T = np.eye(4)
        if i % 2 == 1:   # every other link turned 90 degrees about Y
            T[:3, :3] = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])[:3, :3]
        T[:3, 3] = (0, y, 0)
        scene.add_geometry(shaded(link, metal), node_name=f'link_{i}', geom_name=f'link_{i}', transform=T)
        y -= PITCH * MM
    ring = split_ring(); ring.apply_scale(MM)
    T = np.eye(4)
    T[:3, :3] = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])[:3, :3]   # ring plane at 90deg to last link
    last_bottom = y + PITCH * MM - link_len / 2 + LINK_R * MM
    T[:3, 3] = (0, last_bottom - (RING_R - 0.4) * MM, 0)
    scene.add_geometry(shaded(ring, metal), node_name='ring', geom_name='ring', transform=T)

    os.makedirs(OUT, exist_ok=True)
    extras = {'tab_center_mm': [tx, ty], 'body_width_mm': 80.5, 'pitch_m': PITCH * MM, 'links': N_LINKS}
    scene.metadata['grille_talk'] = extras
    path = os.path.join(OUT, f'{car_id}.glb')
    scene.export(path)
    bounds = M['outline'].bounds
    with open(os.path.join(OUT, f'{car_id}.json'), 'w') as f:
        json.dump(dict(extras, outline_bounds_mm=bounds), f)
    print(car_id, os.path.getsize(path) // 1024, 'KB', 'tris', len(body.faces) + len(details.faces))


if __name__ == '__main__':
    launch = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    ids = sys.argv[1].split(',') if len(sys.argv) > 1 else [c['id'] for c in launch['cars']]
    assert not geom.badges_on(), 'KC_BADGE must be 0: products are logo-free'
    for i in ids:
        build(i)
