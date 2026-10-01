"""Slice a car's single keychain and full plate with the Creality Print CLI and report time / filament / swaps / purge.

classic    : real 2-colour slice (STL route, filament 1 = black, 2 = white) -> exact changes, purge (prime tower +
             flush into infill), time.
production : the 1-swap build is colour-by-height; the CLI's STL route drops a floating cap onto the bed, so it is
             sliced in one colour (exact geometry, time, grams) and exactly one black->white change is added using the
             per-change cost measured from the car's own classic 2-colour slices (tower + purge + change time).
usage: python kc/lib/verify_plate.py <car_out_dir> <spec.py|.pkl>
"""
import os, sys, json, re, zipfile, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import trimesh, numpy as np
import export, geom, plate, cli_multi, slicecheck, k2config, write3mf

PLA = 1.24


def single_colour_3mf_slice(meshes, placements, bounds, d, tag, thumb):
    """3MF route with every part on filament 1 (works in the CLI). Returns gcode stats."""
    parts = [dict(name=c, mesh=m, extruder=1) for c, m in meshes.items()]
    cfg = k2config.build()
    src = os.path.abspath(os.path.join(d, f'{tag}_1col.3mf')); out = os.path.abspath(os.path.join(d, f'{tag}_1col_sliced.3mf'))
    write3mf.write_3mf(src, parts, cfg, object_name=tag, positions=placements, thumbnail_png=thumb)
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run([cli_multi.EXE, '--slice', '1', '--export-3mf', out, src], capture_output=True, text=True, timeout=3600)
    if not os.path.exists(out):
        return None
    z = zipfile.ZipFile(out); g = [n for n in z.namelist() if n.endswith('.gcode')][0]
    t = z.read(g).decode('utf-8', 'ignore')
    return cli_multi.gcode_stats(t)


def run(outdir, spec_path):
    spec = export.load_spec(spec_path)
    cid = spec['id']
    M = geom.build_maps(spec); geom.repair_min_width(M)
    b = M['outline'].bounds
    placed, tower_xy, how = plate.best_layout(M['outline'])
    d = os.path.join(outdir, '_verify'); os.makedirs(d, exist_ok=True)
    rep = {'id': cid, 'plate_count': len(placed), 'layout': how}
    for st in ('classic', 'production'):
        sd = os.path.join(outdir, st)
        ms = {c: trimesh.load(os.path.join(sd, f'{cid}_{st}_{c}.stl')) for c in ('black', 'white')}
        thumb = os.path.join(sd, f'{cid}_{st}_render.png')
        r = {}
        for scope, pl in (('single', [(130.0, 130.0, 0)]), ('plate', placed)):
            one = single_colour_3mf_slice(ms, pl, b, d, f'{cid}_{st}_{scope}', thumb)
            r[scope] = {'one_colour': one}
            if st == 'classic':
                pm = cli_multi.place_meshes(ms, pl, b)
                paths = []
                for c, fid in (('black', 1), ('white', 2)):
                    p = os.path.join(d, f'{cid}_{st}_{scope}_{c}.stl'); pm[c].export(p); paths.append((p, fid))
                over = {'wipe_tower_x': [f'{tower_xy[0]:.1f}'], 'wipe_tower_y': [f'{tower_xy[1]:.1f}']} if scope == 'plate' else \
                       {'wipe_tower_x': ['200'], 'wipe_tower_y': ['200']}
                g, status = cli_multi.slice_stls(paths, d, f'{cid}_{st}_{scope}_2col', overrides=over)
                r[scope]['two_colour'] = cli_multi.gcode_stats(g) if g else {'error': status}
        rep[st] = r
    # per-change cost from the classic 2-colour slices (single keychain): time and filament above the 1-colour slice
    for scope in ('single', 'plate'):
        c1 = rep['classic'][scope]['one_colour']; c2 = rep['classic'][scope].get('two_colour', {})
        if c1 and c2 and c2.get('time_s') and c2.get('filament_changes'):
            n = c2['filament_changes']
            dt = (c2['time_s'] - c1['time_s']) / n
            dg = (sum(c2['grams_per_filament']) - sum(c1['grams_per_filament'] or [0])) / n
            rep['classic'][scope]['per_change'] = {'seconds': round(dt, 1), 'grams': round(dg, 2), 'changes': n}
    # production estimate: one black->white change. Cost of a B->W change = 871 mm3 purge (670 x 1.3) + tower share.
    pc = rep['classic']['plate'].get('per_change') or rep['classic']['single'].get('per_change')
    for scope in ('single', 'plate'):
        p1 = rep['production'][scope]['one_colour']
        if p1 and pc:
            purge_g = 0.871 * PLA
            rep['production'][scope]['estimate'] = {
                'filament_changes': 1,
                'time_s': round(p1['time_s'] + pc['seconds']),
                'grams_total': round(sum(p1['grams_per_filament']) + max(purge_g, pc['grams']), 2),
                'purge_grams': round(max(purge_g, pc['grams']), 2),
                'basis': 'one-colour CLI slice + 1 change at the per-change cost measured on the classic 2-colour slice'}
    json.dump(rep, open(os.path.join(outdir, 'verify_report.json'), 'w'), indent=1)
    return rep


if __name__ == '__main__':
    r = run(sys.argv[1], sys.argv[2])
    print(json.dumps(r, indent=1)[:6000])
