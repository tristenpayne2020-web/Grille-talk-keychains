"""Creality Print 7.3+: slice the EXACT delivered project 3MFs (multi-colour works in the 7.3 CLI) and report time,
filament per colour, filament changes. Same report keys as verify_plate.py so pricing/packaging keep working.
usage: python kc/lib/verify_plate2.py <car_out_dir>"""
import os, sys, json, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import slicecheck, cli_multi


def stats_of(path, workdir):
    t = slicecheck.slice_3mf(path, workdir)
    if t is None:
        return {'error': 'slice failed', 'file': os.path.basename(path)}
    st = cli_multi.gcode_stats(t)
    st['objects'] = len(re.findall(r'^EXCLUDE_OBJECT_DEFINE', t, re.M))
    st['file'] = os.path.basename(path)
    st['cfg_top_shell_layers'] = (re.search(r'^; top_shell_layers = (\S+)', t, re.M) or [None, None])[1]
    st['cfg_wall_transition_angle'] = (re.search(r'^; wall_transition_angle = (\S+)', t, re.M) or [None, None])[1]
    st['cfg_ironing_flow'] = (re.search(r'^; ironing_flow = (\S+)', t, re.M) or [None, None])[1]
    st['cfg_ironing_spacing'] = (re.search(r'^; ironing_spacing = (\S+)', t, re.M) or [None, None])[1]
    return st


def run(outdir):
    cid = os.path.basename(os.path.dirname(os.path.abspath(outdir))) if os.path.basename(outdir) == 'out' else os.path.basename(outdir)
    br = json.load(open(os.path.join(outdir, 'build_report.json')))
    cid = br['id']
    wd = os.path.join(outdir, '_verify73')
    rep = {'id': cid, 'method': 'Creality Print 7.3 CLI, real multi-colour slices of the delivered 3MF files'}
    for st, sub in (('production', 'production'), ('classic', 'classic'), ('custom', 'production3'), ('custom_classic', 'classic3')):
        d = os.path.join(outdir, sub)
        if not os.path.isdir(d):
            continue
        single = glob.glob(os.path.join(d, f'{cid}_{sub}_single.3mf'))
        plate = glob.glob(os.path.join(d, f'{cid}_{sub}_PLATE_*x.3mf'))
        plate = sorted(plate, key=os.path.getmtime)[-1:] if plate else []
        rep[st] = {}
        if single:
            rep[st]['single'] = stats_of(single[0], os.path.join(wd, st + '_single'))
        if plate:
            rep[st]['plate'] = stats_of(plate[0], os.path.join(wd, st + '_plate'))
            rep[st]['plate']['count'] = int(re.search(r'PLATE_(\d+)x', plate[0]).group(1))
    rep['plate_count'] = rep.get('production', {}).get('plate', {}).get('count')
    # compatibility keys used by pricing_inputs.py / package.py
    pp, cp = rep['production'].get('plate', {}), rep['classic'].get('plate', {})
    rep['production']['plate']['estimate'] = {'filament_changes': pp.get('filament_changes'), 'time_s': pp.get('time_s'),
                                              'grams_total': round(sum(pp.get('grams_per_filament') or [0]), 2),
                                              'basis': 'real 2-colour slice of the plate 3MF (Creality Print 7.3 CLI)'}
    rep['classic']['plate']['two_colour'] = {k: v for k, v in cp.items() if k != 'two_colour'}
    cu = rep.get('custom', {}).get('plate', {})
    if cu.get('time_s') and pp.get('time_s') and (cu.get('filament_changes') or 0) > (pp.get('filament_changes') or 0):
        n = cu['filament_changes'] - pp['filament_changes']
        rep['classic']['plate']['per_change'] = {'seconds': round((cu['time_s'] - pp['time_s']) / n, 1),
                                                 'grams': round((sum(cu['grams_per_filament']) - sum(pp['grams_per_filament'])) / n, 2),
                                                 'changes': n, 'basis': 'custom-colour plate minus 1-swap plate'}
    json.dump(rep, open(os.path.join(outdir, 'verify_report.json'), 'w'), indent=1)
    return rep


if __name__ == '__main__':
    r = run(sys.argv[1])
    for k in ('production', 'classic', 'custom', 'custom_classic'):
        p = r.get(k, {}).get('plate', {})
        print(k, p.get('count'), p.get('time'), p.get('grams_per_filament'), 'changes', p.get('filament_changes'), 'objects', p.get('objects'),
              'top', p.get('cfg_top_shell_layers'), 'wta', p.get('cfg_wall_transition_angle'), 'iron', p.get('cfg_ironing_flow'), p.get('cfg_ironing_spacing'), p.get('error', ''))
