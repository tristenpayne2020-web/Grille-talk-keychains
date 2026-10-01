"""One call builds everything for a car: maps -> checks -> both constructions -> STL / STEP / 3MF (single + full
plate) / renders / report.  Usage:  python -m export <spec.py> <outdir> [--no-step] [--no-slice] [--no-plate]"""
import os, sys, json, time, importlib.util, pickle, copy
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom, build3d, render, plate, k2config, write3mf

WHITE_RGB = (0.91, 0.90, 0.86)
BLACK_RGB = (0.10, 0.10, 0.11)
STYLES = {
    'production': dict(fn=build3d.build_production, label='1-swap production', parts=[('Base (black)', 'black', 1), ('Cap (white)', 'white', 2)]),
    'classic': dict(fn=build3d.build_classic, label='classic full inlay', parts=[('Body (white)', 'white', 2), ('Inlays (black)', 'black', 1)]),
}


def load_spec(path):
    if path.endswith('.pkl'):
        return pickle.load(open(path, 'rb'))
    sp = importlib.util.spec_from_file_location('carspec', path)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    spec = copy.deepcopy(mod.SPEC)
    spec['_dir'] = os.path.dirname(os.path.abspath(path))
    return spec


def design(spec, outdir, repair=True, verbose=True):
    """2D stage only (fast): maps, repair, checks, face + overlay previews. Used while tracing."""
    os.makedirs(outdir, exist_ok=True)
    M = geom.build_maps(spec)
    rep0 = geom.check_maps(M)
    fixes = geom.repair_min_width(M) if repair else []
    rep = geom.check_maps(M)
    rep['errors_before_repair'] = len(rep0['errors'])
    rep['auto_repairs'] = fixes
    render.face_png(M, os.path.join(outdir, 'face.png'), title=spec.get('name', ''))
    ref = spec.get('ref')
    if ref and not os.path.isabs(ref) and not os.path.exists(ref) and spec.get('_dir'):
        for cand in (os.path.join(spec['_dir'], ref), os.path.join(spec['_dir'], os.path.basename(ref)), os.path.join(spec['_dir'], 'ref', os.path.basename(ref))):
            if os.path.exists(cand):
                ref = cand; break
    if ref and spec.get('units', 'px') == 'px' and os.path.exists(ref):
        render.overlay_png(spec, M, ref, os.path.join(outdir, 'overlay.png'))
    json.dump(rep, open(os.path.join(outdir, 'design_report.json'), 'w'), indent=1)
    if verbose:
        print(f"size {rep['size_mm']} mm | errors before repair {rep['errors_before_repair']} | auto-repairs {len(fixes)} | remaining errors {len(rep['errors'])}")
        for e in rep['errors'][:30]:
            print('  ERROR', e)
    return M, rep


def full(spec, outdir, do_step=True, do_slice=True, do_plate=True, styles=('production', 'classic'), verbose=True):
    t0 = time.time()
    cid = spec['id']
    M, rep = design(spec, outdir, verbose=verbose)
    summary = {'id': cid, 'name': spec.get('name'), 'size_mm': rep['size_mm'], 'design_errors': rep['errors'],
               'auto_repairs': rep['auto_repairs'], 'styles': {}}
    for st in styles:
        S = STYLES[st]
        parts, slabs = S['fn'](M)
        chk = build3d.check_parts(parts)
        tb, tw = build3d.to_trimesh(parts['black']), build3d.to_trimesh(parts['white'])
        d = os.path.join(outdir, st); os.makedirs(d, exist_ok=True)
        stem = f'{cid}_{st}'
        tb.export(os.path.join(d, f'{stem}_black.stl')); tw.export(os.path.join(d, f'{stem}_white.stl'))
        r3d = os.path.join(d, f'{stem}_render.png')
        render.render3d([(tw, WHITE_RGB), (tb, BLACK_RGB)], r3d, elev=55, azim=-10)
        if do_step:
            build3d.export_step(slabs, os.path.join(d, f'{stem}.step'), name=f"{spec.get('name', cid)}")
        meshes = {'black': tb, 'white': tw}
        prt = [dict(name=n, mesh=meshes[c], extruder=e) for n, c, e in S['parts']]
        oname = f"{spec.get('name', cid)} keychain ({S['label']})"
        cfg = k2config.build()
        write3mf.write_3mf(os.path.join(d, f'{stem}_single.3mf'), prt, cfg, object_name=oname, app_version=k2config.VERSION,
                           thumbnail_png=r3d, positions=[(130.0, 130.0)])
        info = {'check': chk, 'volume_black_mm3': chk['black_volume'], 'volume_white_mm3': chk['white_volume']}
        if do_plate:
            placed, tower_xy, how = plate.best_layout(M['outline'])
            # write3mf positions are bbox centres of the whole object; the object bbox == outline bbox (all parts inside)
            cfgp = k2config.build({'wipe_tower_x': [f'{tower_xy[0]:.1f}'], 'wipe_tower_y': [f'{tower_xy[1]:.1f}']})
            n = len(placed)
            write3mf.write_3mf(os.path.join(d, f'{stem}_PLATE_{n}x.3mf'), prt, cfgp, object_name=oname, app_version=k2config.VERSION,
                               thumbnail_png=r3d, positions=placed)
            plate.layout_png(M['outline'], placed, tower_xy, (40, 25), os.path.join(d, f'{stem}_plate_layout.png'))
            info['plate'] = {'count': n, 'layout': how, 'tower_xy': tower_xy}
        if do_slice:
            import slicecheck
            sc = slicecheck.check_parts(meshes, slabs, os.path.join(outdir, '_slicecheck', st), r3d, stem)
            info['slicecheck'] = sc
        summary['styles'][st] = info
    summary['build_seconds'] = round(time.time() - t0, 1)
    json.dump(summary, open(os.path.join(outdir, 'build_report.json'), 'w'), indent=1, default=str)
    if verbose:
        print(json.dumps(summary, indent=1, default=str)[:4000])
    return summary


if __name__ == '__main__':
    a = sys.argv[1:]
    spec = load_spec(a[0])
    out = a[1]
    if '--design-only' in a:
        design(spec, out)
    else:
        full(spec, out, do_step='--no-step' not in a, do_slice='--no-slice' not in a, do_plate='--no-plate' not in a)
