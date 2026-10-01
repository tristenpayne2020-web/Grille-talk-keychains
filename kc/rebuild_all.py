"""Rebuild every finished car with the current k2config (top shells 6, wall transition 50, ironing 25 % / 0.12 mm),
verify with real Creality Print 7.3 slices, add the newly approved cars, repackage Downloads/CarKeychains.
usage: python rebuild_all.py [--skip-done]   (log: rebuild_log.txt, progress: rebuild_status.json)"""
import json, os, sys, subprocess, time
SP = os.path.dirname(os.path.abspath(__file__)); os.chdir(SP)
NEW = ['c7_z06', 'g42_m240i_lci', 'lexus_is350', 'civic_11th', 'camry_xv80']
WANT = {'cfg_top_shell_layers': '6', 'cfg_wall_transition_angle': '50', 'cfg_ironing_flow': '25%', 'cfg_ironing_spacing': '0.12'}
LOG = open('rebuild_log.txt', 'a', encoding='utf-8')
STATUS = 'rebuild_status.json'
status = json.load(open(STATUS)) if os.path.exists(STATUS) and '--skip-done' in sys.argv else {}


def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + '\n'); LOG.flush()


def step(args, cid, name):
    t0 = time.time()
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    log(cid, name, 'exit', r.returncode, f'{time.time() - t0:.0f}s')
    if r.returncode:
        log(r.stdout[-1500:], r.stderr[-2500:])
    return r.returncode == 0


def settings_ok(cid):
    v = json.load(open(f'cars/{cid}/out/verify_report.json'))
    bad = []
    for st in ('production', 'classic', 'custom', 'custom_classic'):
        p = v.get(st, {}).get('plate', {})
        if p.get('error'):
            bad.append(f'{st}: {p["error"]}')
        for k, want in WANT.items():
            if str(p.get(k)) != want:
                bad.append(f'{st} {k}={p.get(k)} (want {want})')
    return bad


cars = [c['id'] for c in json.load(open('cars_pkg.json'))] + NEW
for cid in cars:
    if status.get(cid) == 'ok':
        continue
    spec = 'cars/g80_m3/spec_from_step.pkl' if cid == 'g80_m3' else f'cars/{cid}/spec.py'
    out = f'cars/{cid}/out'
    ok = step(['lib/export.py', spec, out], cid, 'export') and step(['lib/export3.py', spec, out], cid, 'export3') \
        and step(['lib/verify_plate2.py', out], cid, 'verify73')
    bad = settings_ok(cid) if ok else ['build failed']
    status[cid] = 'ok' if not bad else bad
    json.dump(status, open(STATUS, 'w'), indent=1)
    log(cid, 'OK' if not bad else f'PROBLEM {bad}')
    if bad and cid == cars[0]:
        log('first car failed the settings check - stopping'); sys.exit(1)

step(['add_cars_pkg.py'] + NEW, 'all', 'add_cars_pkg')
step(['finalize.py'], 'all', 'finalize')
log('DONE', sum(v == 'ok' for v in status.values()), 'of', len(status), 'ok;', {k: v for k, v in status.items() if v != 'ok'})
