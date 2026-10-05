"""Wall key holders in the style of the user's G80 holder (G80_WallKeyholder_user.step), 1-SWAP construction.

What the user's holder is: the keychain face scaled 3x in every axis (body 241 mm wide; black back plate 4.8 mm,
coloured face 4.2 mm on top = 9.0 mm), no keyring tab, four J-hooks (15 mm wide, 30 mm apart) standing on the face
along the bottom edge, curling up at the tip.
What this builds for any car spec:
  * the car's own design scaled 3x, as the 1-swap build: black base 0 -> 4.8 mm, white cap 4.8 -> 9.0 mm
    (black details recessed, grooves cut to the black, relief grilles with ribs) -> exactly ONE filament change;
  * the user's hooks copied 1:1 from the STEP, white (they stand on the white cap), placed at the same spacing,
    all at one height just inside the bottom edge; under each hook the cap is made solid;
  * two countersunk wall-mounting holes (4.5 mm, 90-degree countersink 8.6 mm, flush #6/#8 screw), mirror-symmetric;
  * no back label (it would add filament changes) and no logos.
usage: python kc/wall/build_wall.py charger_srt mk5_supra gt500_mustang camaro_zl1 c8_corvette
"""
import os, sys, json
import numpy as np
import trimesh
import cadquery as cq
from shapely.geometry import Point, box, Polygon
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__)); KC = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(KC, 'lib'))
import geom, build3d, export, export3, k2config, write3mf, render
from geom import polys, clean

S = 3.0                                        # scale of the user's holder vs the keychain
HB, HF, T = 1.6 * S, 0.6 * S, 3.0 * S         # 4.8 / 1.8 / 9.0 mm, on the 0.2 mm layer grid
USER_FACE_TOP = 5.8                            # z of the face top in the user's STEP
MOUNT_D, CSK_D, MARGIN = 4.5, 8.6, 2.2
BOOL = dict(engine='manifold')
OUT = os.path.join(HERE, 'out')
NAMES = {c['id']: (c['folder'], c['name']) for c in json.load(open(os.path.join(KC, 'cars_pkg.json')))}


# ---------------------------------------------------------------- the user's hooks (once)
def _bsec(shape, z):
    """exact cross-section of a B-rep solid at height z (shapely)"""
    tris = []
    for f in cq.Workplane().add(shape).section(z).faces().vals():
        v, t = f.tessellate(0.01)
        tris += [Polygon([(v[a].x, v[a].y), (v[b].x, v[b].y), (v[c].x, v[c].y)]) for a, b, c in t]
    return clean(unary_union([x.buffer(0) for x in tris]).buffer(0.001).buffer(-0.001)) if tris else Polygon()


def user_hooks():
    """The user's hooks as exact 0.2 mm layers of their STEP (the STEP surfaces have hairline gaps, so this is the
    watertight, print-identical form). Returns [(geom, dz0, dz1)] with z relative to the face top, the user's car
    centre x, and the y of the hooks' root."""
    sol = cq.importers.importStep(os.path.join(HERE, 'G80_WallKeyholder_user.step')).solids().vals()
    body = max((s for s in sol if s.BoundingBox().zmax > 10), key=lambda s: s.Volume())
    bb = body.BoundingBox()
    top = bb.zmax
    n = int(round((top - USER_FACE_TOP) / 0.2))
    dz = (top - USER_FACE_TOP) / n
    layers = []
    for k in range(n):
        g = _bsec(body, USER_FACE_TOP + (k + 0.5) * dz)
        if not g.is_empty:
            layers.append((g, k * dz, (k + 1) * dz))
    foot = layers[0][0]
    return layers, (bb.xmin + bb.xmax) / 2, foot.bounds[1], foot


# ---------------------------------------------------------------- per car
def scaled_maps(spec):
    M = geom.build_maps(spec, tab=False); geom.repair_min_width(M); geom.split_white(M)
    keys = ('outline', 'white', 'black', 'relief_region', 'relief_ribs', 'grooves_white', 'grooves_black',
            'white_body', 'white_light')
    return {k: affinity.scale(M[k], S, S, origin=(0, 0)) for k in keys} | {'hole': Polygon()}


def stepped_countersink(cx, cy):
    """90-degree countersink as 0.2 mm steps (what the printer lays down anyway) + the through shaft."""
    out = [(Point(cx, cy).buffer(MOUNT_D / 2, 64), 0.0, T)]
    r_top, z = CSK_D / 2, T
    while r_top - (T - z) > MOUNT_D / 2:
        z0 = round(z - 0.2, 3)
        out.append((Point(cx, cy).buffer(r_top - (T - z0), 64), z0, z))
        z = z0
    return out


def write_all(stem, sl, cols, cfg, title):
    """STLs, coloured STEP (flat part, without the hooks), render and the Creality 3MF."""
    parts = build3d.parts_from(sl)
    meshes = {k: build3d.to_trimesh(parts[k]) for k, _, _ in cols}
    for k, m in meshes.items():
        m.export(f'{stem}_{k}.stl')
    try:
        # the hooks' 113 layers make the OCC fuse take hours: the STEP is the flat part only (hooks are in the STL/3MF)
        flat = {k: [(g, a, b) for g, a, b in v if b <= T + 1e-6] for k, v in sl.items()}
        export3.export_step3(flat, stem + '.step', title, {k: rgb for k, _, rgb in cols})
    except Exception as e:
        print('STEP skipped:', e)
    r3d = stem + '_render.png'
    try:
        render.render3d([(meshes[k], rgb) for k, _, rgb in reversed(cols)], r3d, elev=60, azim=-10, zoom=1.3)
    except Exception as e:
        print('render skipped:', e); r3d = None
    prt = [dict(name=label, mesh=meshes[k], extruder=i + 1) for i, (k, label, _) in enumerate(cols)]
    write3mf.write_3mf(stem + '.3mf', prt, cfg, object_name=title, app_version=k2config.VERSION,
                       thumbnail_png=r3d, positions=[(126.0, 110.0)])
    print(title, np.round(trimesh.util.concatenate(list(meshes.values())).extents, 1), 'mm',
          {k: round(m.volume / 1000, 1) for k, m in meshes.items()}, 'cm3')


def build(cid, hooks, ucx, uroot, ufoot):
    folder, name = NAMES[cid]
    spec = export.load_spec(os.path.join(KC, 'cars', cid, 'spec.py'))
    M = scaled_maps(spec)
    _, sl = build3d._production(M, HB, HF, T)
    O = M['outline']
    ob = O.bounds; cx = (ob[0] + ob[2]) / 2
    inner = O.buffer(-0.6)
    # hooks: same spacing as the user's, all at one height, footprint fully inside the outline
    dx = cx - ucx
    feet = [affinity.translate(p, dx, 0) for p in polys(ufoot)]
    # like the user's G80: hooks low on the bumper, all at one height, as low as the outline allows (keys hang below
    # the car). Where the face there is a recessed black area the hook root becomes a white column down to the black
    # base (still above the swap height, so still one filament change).
    shift = None
    for dy in np.arange(ob[1] - uroot, ob[1] - uroot + 0.5 * (ob[3] - ob[1]), 0.2):
        if all(inner.contains(affinity.translate(f, 0, dy).buffer(0.4)) for f in feet):
            shift = dy; break
    if shift is None:
        raise SystemExit(f'{cid}: no room for the hooks')
    pads = unary_union([affinity.translate(f, 0, shift).buffer(0.3) for f in feet]).intersection(O)
    # under the hooks: solid black base + solid white cap
    sl = {k: [(g.difference(pads), a, b) for g, a, b in v] for k, v in sl.items()}
    sl['black'].append((pads, 0.0, HB)); sl['white'].append((pads, HB, T))
    hook_sl = [(affinity.translate(g, dx, shift), T + a, T + b) for g, a, b in hooks]
    # mounting holes: outermost spot with solid white cap and black base all round, clear of the hooks
    white_face = unary_union([g for g, a, b in sl['white'] if b >= T - 1e-6]).difference(pads.buffer(3))
    solid = clean(white_face.buffer(-0.01))
    best = None
    for x in np.arange(ob[0] + 6, cx - (ob[2] - ob[0]) * 0.2, 0.5):
        for y in np.arange(ob[1] + 6, ob[3] - 6, 0.5):
            need = CSK_D / 2 + MARGIN
            if solid.contains(Point(x, y).buffer(need)) and solid.contains(Point(2 * cx - x, y).buffer(need)):
                sc = (x - ob[0]) + 0.35 * abs(y - (ob[1] + ob[3]) / 2)
                if best is None or sc < best[0]:
                    best = (sc, x, y)
    if best is None:
        raise SystemExit(f'{cid}: no room for the mounting holes')
    _, hx, hy = best
    cut = [c for x in (hx, 2 * cx - hx) for c in stepped_countersink(x, hy)]
    # cut every slab by the cutters that span it, height band by height band
    bands = sorted({0.0, T, HB, HF} | {z for _, a, b in cut for z in (a, b)} | {z for v in sl.values() for _, a, b in v for z in (a, b)})
    def cut_slabs(lst):
        res = []
        for g, a, b in lst:
            zs = [z for z in bands if a - 1e-6 <= z <= b + 1e-6]
            for z0, z1 in zip(zs[:-1], zs[1:]):
                if z1 - z0 < 1e-6: continue
                hole = unary_union([h for h, ha, hb in cut if ha <= z0 + 1e-6 and hb >= z1 - 1e-6])
                gg = clean(g.difference(hole)) if not hole.is_empty else g
                if not gg.is_empty: res.append((gg, z0, z1))
        return res
    sl = {k: cut_slabs(v) for k, v in sl.items()}
    sl['white'] += hook_sl
    d = os.path.join(OUT, folder); os.makedirs(d, exist_ok=True)
    # ---- 1-swap (black + white)
    stem = os.path.join(d, f'{folder}_wall_key_holder')
    write_all(stem, sl, [('black', 'Back plate + details (black)', (0.10, 0.10, 0.11)), ('white', 'Face + hooks (white)', (0.93, 0.92, 0.88))],
              k2config.build({'wipe_tower_x': ['216'], 'wipe_tower_y': ['222']}), f'{name} wall key holder')
    # ---- custom body colour (3 filaments like the custom-colour keychains): 1 black, 2 body colour (face + hooks),
    # 3 white lights (the light islands of the face, full cap height so they stay opaque)
    L = M['white_light'].difference(M['grooves_white']).difference(pads)
    sl3 = {'black': sl['black'],
           'body': [(g.difference(L) if b <= T + 1e-6 else g, a, b) for g, a, b in sl['white']],
           'light': [(g.intersection(L), a, b) for g, a, b in sl['white'] if b <= T + 1e-6]}
    sl3['light'] = [(g, a, b) for g, a, b in sl3['light'] if not g.is_empty]
    write_all(stem + '_custom_colour', sl3, [('black', 'Back plate + details (black)', (0.10, 0.10, 0.11)),
                                              ('body', 'Body + hooks (custom colour)', (0.78, 0.06, 0.18)),
                                              ('light', 'Lights (white)', (0.95, 0.95, 0.93))],
              k2config.build_n(3, export3.COLOURS, export3.FLUSH3, {'wipe_tower_x': ['216'], 'wipe_tower_y': ['222']}),
              f'{name} wall key holder (custom colour)')
    print(f'{cid}: holes at x={hx:.1f}/{2*cx-hx:.1f} y={hy:.1f}')
    if os.name == 'nt':                                   # deliver next to the other extras
        import shutil
        dl = os.path.join(os.path.expanduser('~'), 'Downloads', 'GrilleTalk_Extras', 'Wall_Key_Holders', folder)
        os.makedirs(dl, exist_ok=True)
        for f in os.listdir(d):
            shutil.copy2(os.path.join(d, f), dl)
    return stem


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    hooks, ucx, uroot, ufoot = user_hooks()
    print('user hooks:', len(polys(ufoot)), 'layers', len(hooks), [tuple(np.round(p.bounds, 1)) for p in polys(ufoot)])
    for cid in sys.argv[1:]:
        build(cid, hooks, ucx, uroot, ufoot)
