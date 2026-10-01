"""Sampler plates: one of each car (1-swap build), black + white Generic PLA, split over as many K2 plates as needed.
usage: python make_sampler.py <dest_dir>   -> All_Cars_Sampler_plate<k>of<n>_<m>x.3mf + previews"""
import sys, os, json, glob
sys.path.insert(0, 'lib')
import numpy as np
import export, geom, build3d, render, k2config
from write3mf_multi import write_3mf_multi
k2config.FILAMENT = 'Generic PLA @Creality K2 0.4 nozzle'
dest = sys.argv[1]
cars = json.load(open('cars_pkg.json'))
items = []
for c in cars:
    try:
        spec = export.load_spec(c['spec'] if c['id'] != 'g80_m3' else 'cars/g80_m3/spec_from_step.pkl')
        M = geom.build_maps(spec); geom.repair_min_width(M)
    except Exception as e:                      # a spec being edited right now: skip rather than fail the plates
        print('SKIPPED', c['id'], e); continue
    parts, _ = build3d.build_production(M)
    b, w = build3d.to_trimesh(parts['black']), build3d.to_trimesh(parts['white'])
    bb = M['outline'].bounds
    items.append(dict(name=c['name'], black=b, white=w, W=bb[2] - bb[0], H=bb[3] - bb[1]))

MARGIN, GAP, BED = 6.0, 5.0, 260.0
Wmax = max(it['W'] for it in items)
col_x = [MARGIN + Wmax / 2, MARGIN + Wmax + GAP + Wmax / 2]      # two columns; the prime tower uses the free strip on the right
col_h = BED - 2 * MARGIN
# first-fit-decreasing into plates of two columns
items.sort(key=lambda d: -d['H'])
plates = []                                                        # each plate: [col0 list, col1 list, heights]
for it in items:
    placed = False
    for p in plates:
        for k in (0, 1):
            if p[2][k] + it['H'] <= col_h + 1e-6:
                p[k].append(it); p[2][k] += it['H'] + GAP; placed = True; break
        if placed:
            break
    if not placed:
        plates.append([[it], [], [it['H'] + GAP, 0.0]])
for old in glob.glob(os.path.join(dest, 'All_Cars_Sampler*')):
    os.remove(old)
n = len(plates)
tower_x = col_x[1] + Wmax / 2 + 12
for pi, p in enumerate(plates, 1):
    objects, meshes = [], []
    for k in (0, 1):
        y = MARGIN
        for it in p[k]:
            pos = (col_x[k], y + it['H'] / 2); y += it['H'] + GAP
            objects.append(dict(name=f"{it['name']} keychain", pos=pos,
                                parts=[dict(name=f"{it['name']} - base (black)", mesh=it['black'], extruder=1),
                                       dict(name=f"{it['name']} - cap (white)", mesh=it['white'], extruder=2)]))
            allv = np.vstack([it['black'].vertices, it['white'].vertices]); mn, mx = allv.min(0), allv.max(0)
            t = [pos[0] - (mn[0] + mx[0]) / 2, pos[1] - (mn[1] + mx[1]) / 2, -mn[2]]
            for m, rgb in ((it['white'], (0.91, 0.90, 0.86)), (it['black'], (0.10, 0.10, 0.11))):
                mm = m.copy(); mm.apply_translation(t); meshes.append((mm, rgb))
    cnt = len(objects)
    stem = os.path.join(dest, f'All_Cars_Sampler_plate{pi}of{n}_{cnt}x')
    cfg = k2config.build({'wipe_tower_x': [f'{tower_x:.1f}'], 'wipe_tower_y': ['150.0']})
    render.render3d(meshes, stem + '_preview.png', size=(1400, 1400), elev=72, azim=0, zoom=0.95)
    write_3mf_multi(stem + '.3mf', objects, cfg, title=f'All cars sampler {pi}/{n}', thumbnail_png=stem + '_preview.png')
    print('wrote', stem + '.3mf', cnt, 'cars:', ', '.join(o['name'].replace(' keychain', '') for o in objects))
