"""Real multi-colour slicing with the Creality Print 7.x CLI.

The CLI crashes on multi-colour 3MF projects (prime-tower pre-check) and when rendering thumbnails for STL inputs,
but the STL route slices correctly and writes the full G-code (K2 CFS change sequence, prime tower, flush) BEFORE it
crashes on the thumbnail. So: one STL per colour (all copies of the plate merged), filament ids 1/2, no arrange; the
G-code is harvested from the path the CLI logs.  Settings = the same K2 config as the project 3MFs (k2config.build()).
"""
import os, re, json, subprocess, shutil, time, copy
import k2config

EXE = os.environ.get('CREALITY_EXE', r"C:\Program Files\Creality\Creality Print 7.1\CrealityPrint.exe")

MACHINE_EXTRA = {'flush_volumes_matrix', 'flush_volumes_vector', 'flush_multiplier', 'wipe_tower_x', 'wipe_tower_y',
                 'curr_bed_type', 'enable_prime_tower', 'prime_tower_width'}


def write_settings(d, overrides=None):
    os.makedirs(d, exist_ok=True)
    cfg = k2config.build(overrides or {})
    m = k2config.resolve('machine', k2config.MACHINE)
    p = k2config.resolve('process', k2config.PROCESS)
    f = k2config.resolve('filament', k2config.FILAMENT)
    mj, pj = {}, {}
    for k in m:
        if k in cfg:
            mj[k] = cfg[k]
    for k in p:
        if k in cfg:
            pj[k] = cfg[k]
    for k in MACHINE_EXTRA:                      # project-level keys: put them in both, the CLI merges everything
        if k in cfg:
            pj[k] = cfg[k]; mj[k] = cfg[k]
    for k in k2config.KEYCHAIN:
        if k in cfg:
            pj[k] = cfg[k]
    for j, name, typ in ((mj, k2config.MACHINE, 'machine'), (pj, k2config.PROCESS, 'process')):
        j.update({'name': name, 'from': 'system', 'type': typ, 'instantiation': 'true'})
    pj['compatible_printers'] = [k2config.MACHINE]
    paths = {}
    for nm, j in (('machine', mj), ('process', pj)):
        paths[nm] = os.path.abspath(os.path.join(d, nm + '.json'))
        json.dump(j, open(paths[nm], 'w', encoding='utf-8'), indent=1)
    for col, hexc in (('black', '#000000'), ('white', '#FFFFFF')):
        fj = {k: (v[0] if isinstance(v, list) and len(v) == 2 else v) for k, v in f.items()}
        fj.update({'name': k2config.FILAMENT, 'from': 'system', 'type': 'filament', 'instantiation': 'true',
                   'filament_colour': [hexc], 'compatible_printers': [k2config.MACHINE]})
        paths[col] = os.path.abspath(os.path.join(d, f'filament_{col}.json'))
        json.dump(fj, open(paths[col], 'w', encoding='utf-8'), indent=1)
    return paths


def slice_stls(objs, d, tag, overrides=None, custom_gcodes=None, timeout=3600):
    """objs: list of (stl_path, filament_id). Returns (gcode_text or None, log_tail)."""
    P = write_settings(os.path.join(d, 'settings'), overrides)
    args = [EXE, '--debug', '3', '--load-settings', f"{P['machine']};{P['process']}",
            '--load-filaments', f"{P['black']};{P['white']}",
            '--load-filament-ids', ','.join(str(fid) for _, fid in objs), '--arrange', '0']
    if custom_gcodes:
        cg = os.path.abspath(os.path.join(d, f'{tag}_customgcode.json'))
        json.dump(custom_gcodes, open(cg, 'w'))
        args += ['--load-custom-gcodes', cg]
    out3mf = os.path.abspath(os.path.join(d, f'{tag}_cli.3mf'))
    args += ['--slice', '0', '--export-3mf', out3mf] + [os.path.abspath(p) for p, _ in objs]
    logp = os.path.join(d, f'{tag}_cli.log')
    with open(logp, 'w', encoding='utf-8', errors='ignore') as lf:
        subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, timeout=timeout)
    log = open(logp, encoding='utf-8', errors='ignore').read()
    m = re.search(r'Will export G-code to (\S+)', log)
    if not m:
        errs = [l for l in log.split('\n') if 'error' in l.lower() and 'memory' not in l.lower()][-6:]
        return None, '\n'.join(errs)
    src = m.group(1)
    for _ in range(20):
        if os.path.exists(src) and os.path.getsize(src) > 0:
            break
        time.sleep(0.5)
    dst = os.path.join(d, f'{tag}.gcode')
    shutil.copy(src, dst)
    return open(dst, encoding='utf-8', errors='ignore').read(), 'ok'


def _secs(s):
    tot = 0
    for v, u in re.findall(r'(\d+)([dhms])', s):
        tot += int(v) * {'d': 86400, 'h': 3600, 'm': 60, 's': 1}[u]
    return tot


def gcode_stats(t):
    st = {}
    m = re.search(r'estimated printing time \(normal mode\) = ([^\n]+)', t)
    st['time'] = m.group(1).strip() if m else None
    st['time_s'] = _secs(st['time']) if st['time'] else None
    m = re.search(r'; filament used \[g\] = ([^\n]+)', t)
    st['grams_per_filament'] = [float(x) for x in m.group(1).split(',')] if m else None
    m = re.search(r'; total filament change = (\d+)', t)
    st['filament_changes'] = int(m.group(1)) if m else len(re.findall(r'^; toolchange #', t, re.M))
    st['prime_tower_blocks'] = len(re.findall(r'^;TYPE:Prime tower', t, re.M))
    # flush extruded into the K2 purge chute: E moves between FLUSH_START and FLUSH_END
    flush_mm = 0.0
    for blk in re.findall(r'; FLUSH_START(.*?); FLUSH_END', t, re.S):
        flush_mm += sum(float(x) for x in re.findall(r'^G1 E([\d.]+)', blk, re.M))
    st['flush_filament_mm'] = round(flush_mm, 1)
    st['flush_grams'] = round(flush_mm * 2.405 * 1.24 / 1000, 2)       # 1.75 mm filament, PLA 1.24 g/cm3
    for k in ('flush_volumes_matrix', 'flush_multiplier', 'enable_prime_tower', 'flush_into_infill', 'layer_height',
              'wall_generator', 'ironing_type', 'sparse_infill_density', 'top_shell_layers'):
        m = re.search(rf'^; {k} = ([^\n]+)', t, re.M)
        st['cfg_' + k] = m.group(1) if m else None
    return st


def place_meshes(meshes, placements, ref_bounds):
    """meshes: {'black': trimesh, 'white': trimesh} in design coords. placements: [(x, y, rot)] = where the centre of
    ref_bounds (outline bbox) goes on the bed, like write3mf positions. Returns merged per-colour trimeshes."""
    import numpy as np, trimesh
    cx, cy = (ref_bounds[0] + ref_bounds[2]) / 2, (ref_bounds[1] + ref_bounds[3]) / 2
    out = {}
    for col, m in meshes.items():
        parts = []
        for x, y, rot in placements:
            mm = m.copy()
            T = trimesh.transformations.translation_matrix([-cx, -cy, 0])
            R = trimesh.transformations.rotation_matrix(np.radians(rot), [0, 0, 1])
            T2 = trimesh.transformations.translation_matrix([x, y, 0])
            mm.apply_transform(T2 @ R @ T)
            parts.append(mm)
        out[col] = trimesh.util.concatenate(parts)
    return out
