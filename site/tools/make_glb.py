"""Build one GLB per launch car from the production STLs (kc/cars/<id>/out/production/).

Scene (glTF units are metres, +Y up, face toward +Z):
  keychain            node, origin at the keyring hole centre (the pivot the chain hangs from)
    body              white cap mesh, material "body" (recoloured per variant on the site)
    details           black base mesh, material "details"
  link_0              jump ring threaded through the keyring hole (plane holds the hole axis)
  link_1 .. link_4    short chain hanging from the jump ring, separate nodes so the site can drive them
  ring                split ring at the end of the chain
    back              carbon-fibre back face (material "back", tiled twill texture): the textured build plate finish
    lettering         'GRILLE TALK' in white sans across the back, mirrored to read from behind
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
JUMP_R = 3.4         # jump ring centre-line radius: threads the 4.5 mm hole and wraps the 2 mm wall under it
JUMP_WIRE = 0.6
N_LINKS = 4          # chain links below the jump ring (link_1..link_4; link_0 is the jump ring)
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


def jump_ring():
    """Closed round ring, plane XY. Rotated into the YZ plane it passes through the keyring hole."""
    a = np.linspace(0, 2 * np.pi, 96, endpoint=False)
    P = np.stack([JUMP_R * np.cos(a), JUMP_R * np.sin(a), np.zeros_like(a)], 1)
    return sweep(P, JUMP_WIRE, 12)


def split_ring():
    """Two coils of a flat split ring, slightly offset in Z, ring plane = XY."""
    n = 120
    parts = []
    for dz in (-RING_WIRE * 0.95, RING_WIRE * 0.95):
        a = np.linspace(0, 2 * np.pi, n, endpoint=False)
        P = np.stack([RING_R * np.cos(a), RING_R * np.sin(a), np.full(n, dz)], 1)
        parts.append(sweep(P, RING_WIRE, 12))
    return trimesh.util.concatenate(parts)


def carbon_texture(px=256, cells=6):
    """2x2 twill carbon-fibre weave, as the textured build plate leaves it on the black base. Tileable."""
    from PIL import Image, ImageFilter
    c = px // cells
    y, x = np.mgrid[0:px, 0:px].astype(float)
    i, j = (x // c).astype(int), (y // c).astype(int)
    u, v = (x % c) / c, (y % c) / c
    horizontal = ((i + j) // 2) % 2 == 0                 # 2x2 twill: tows switch direction every two cells, stepped
    across = np.where(horizontal, v, u)                  # position across the tow
    along = np.where(horizontal, u, v)
    tow = 0.55 + 0.45 * np.sin(np.pi * across) ** 0.8    # rounded tow profile catches the light in the middle
    fibres = 0.92 + 0.08 * np.sin(2 * np.pi * across * 9 + along * 0.6)
    edge = np.clip(np.minimum(across, 1 - across) * 9, 0.35, 1)
    shade = np.where(horizontal, 1.0, 0.78)              # the two tow directions reflect differently
    g = 12 + 62 * tow * fibres * edge * shade
    img = Image.fromarray(np.clip(np.stack([g, g, g * 1.04], -1), 0, 255).astype(np.uint8))
    return img.filter(ImageFilter.GaussianBlur(0.5))


def face_away(m):
    """Flip a flat mesh so every face points to -Z (seen from behind), whatever the triangulator's winding."""
    flip = m.face_normals[:, 2] > 0
    if flip.any():
        f = m.faces.copy()
        f[flip] = f[flip][:, ::-1]
        m = trimesh.Trimesh(m.vertices, f, process=False)
    return m


def back_and_lettering(M, tab_center):
    """Carbon-fibre back face (UV-mapped, z just behind the black base) and 'GRILLE TALK' in white sans across the
    back, mirrored so it reads correctly from behind. Coordinates in map mm, before the pivot shift."""
    from shapely.geometry import Polygon as P, Point as Pt
    from shapely import affinity as aff
    from shapely.ops import unary_union
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    face = M['outline'].difference(M['hole']).buffer(-0.05)
    v2, f = trimesh.creation.triangulate_polygon(face, engine='earcut')
    V = np.column_stack([v2, np.full(len(v2), -0.08)])   # clear of the base after quantization
    back = face_away(trimesh.Trimesh(V, f, process=False))        # faces point to -Z (away from the front)
    uv = v2 / 10.0                                                # one texture tile per 10 mm, about 1.7 mm tows
    tex = carbon_texture()
    back.visual = trimesh.visual.TextureVisuals(uv=uv, material=PBRMaterial(
        name='back', baseColorTexture=tex, baseColorFactor=[1.0, 1.0, 1.0, 1.0], metallicFactor=0.0, roughnessFactor=0.32))
    # lettering
    tp = TextPath((0, 0), 'GRILLE TALK', size=1.0, prop=FontProperties(family='DejaVu Sans', weight='bold'))
    rings = [P(r) for r in tp.to_polygons() if len(r) > 2]
    text = None
    for r in rings:
        r = r.buffer(0)
        text = r if text is None else text.symmetric_difference(r)
    body = M['outline'].difference(Pt(tab_center).buffer(9))     # centre on the body, not the keyring tab
    bx0, by0, bx1, by1 = body.bounds
    tx0, ty0, tx1, ty1 = text.bounds
    k = min(0.6 * (bx1 - bx0) / (tx1 - tx0), 0.16 * (by1 - by0) / (ty1 - ty0))
    text = aff.scale(text, -k, k, origin=(0, 0))                 # mirrored: read from behind
    tx0, ty0, tx1, ty1 = text.bounds
    text = aff.translate(text, (bx0 + bx1) / 2 - (tx0 + tx1) / 2, (by0 + by1) / 2 - (ty0 + ty1) / 2)
    text = text.intersection(M['outline'].buffer(-1.0))
    parts = []
    for poly in (text.geoms if hasattr(text, 'geoms') else [text]):
        if poly.is_empty or poly.area < 0.01:
            continue
        lv, lf = trimesh.creation.triangulate_polygon(poly, engine='earcut')
        parts.append(face_away(trimesh.Trimesh(np.column_stack([lv, np.full(len(lv), -0.12)]), lf, process=False)))
    letters = trimesh.util.concatenate(parts)
    letters.visual = trimesh.visual.TextureVisuals(material=mat('lettering', (0.96, 0.96, 0.95), 0.0, 0.5))
    return back, letters


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
    if car_id in pkg:
        return os.path.join(KC, pkg[car_id]['spec'])
    launch = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    return os.path.join(KC, next(c['spec'] for c in launch['cars'] if c['id'] == car_id))


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
    back, letters = back_and_lettering(M, (tx, ty))
    meshes = [white_body, black, back, letters] + light_parts
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
    scene.add_geometry(back, node_name='back', geom_name='back', parent_node_name='keychain')
    scene.add_geometry(letters, node_name='lettering', geom_name='lettering', parent_node_name='keychain')
    if light_parts:
        lights = shaded(trimesh.util.concatenate(light_parts), mat('lights', (0.97, 0.97, 0.96), 0.0, 0.5))
        scene.add_geometry(lights, node_name='lights', geom_name='lights', parent_node_name='keychain')

    rot_y = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])[:3, :3]   # XY plane -> YZ plane
    # link_0: jump ring through the hole. Its plane holds the hole axis (Z), its top wire runs through the hole and
    # the ring wraps the tab wall below it, so it reads as looped through, not floating in front of the plate.
    jr = jump_ring(); jr.apply_scale(MM)
    T = np.eye(4); T[:3, :3] = rot_y; T[:3, 3] = (0, -JUMP_R * MM, 0)
    scene.add_geometry(shaded(jr, metal), node_name='link_0', geom_name='link_0', transform=T)
    # chain links hang from the bottom of the jump ring, each turned 90 degrees to the one above
    link = stadium_tube(LINK_R, LINK_S, WIRE)
    link.apply_scale(MM)
    half = (LINK_R + LINK_S / 2) * MM                     # centre to top of the link centre line
    hook_top = (-2 * JUMP_R + JUMP_WIRE + WIRE + 0.15) * MM   # first link's top centre line sits just above the ring's bottom wire
    y = hook_top - half
    for i in range(1, N_LINKS + 1):
        T = np.eye(4)
        if i % 2 == 0:
            T[:3, :3] = rot_y
        T[:3, 3] = (0, y, 0)
        scene.add_geometry(shaded(link, metal), node_name=f'link_{i}', geom_name=f'link_{i}', transform=T)
        y -= PITCH * MM
    last_y = y + PITCH * MM
    ring = split_ring(); ring.apply_scale(MM)
    T = np.eye(4)
    if N_LINKS % 2 == 0:                                   # split ring perpendicular to the last link
        pass
    else:
        T[:3, :3] = rot_y
    last_bottom = last_y - half
    T[:3, 3] = (0, last_bottom + (WIRE + RING_WIRE + 0.15) * MM - RING_R * MM, 0)
    scene.add_geometry(shaded(ring, metal), node_name='ring', geom_name='ring', transform=T)

    os.makedirs(OUT, exist_ok=True)
    extras = {'tab_center_mm': [tx, ty], 'body_width_mm': 80.5, 'pitch_m': PITCH * MM, 'links': N_LINKS + 1, 'jump_ring_mm': JUMP_R}
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
