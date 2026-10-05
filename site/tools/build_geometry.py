"""Rebuild logo-free geometry for every launch car into site/build/geom/<id>/ (KC_BADGE forced to 0).

The owner's print outputs in kc/cars/<id>/out/ are never touched. Specs are read, never written.
usage: python site/tools/build_geometry.py [id,id,...]
"""
import json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
KC = os.path.join(ROOT, 'kc')
OUT = os.path.join(ROOT, 'site', 'build', 'geom')


def main():
    launch = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    pkg = {c['id']: c for c in json.load(open(os.path.join(KC, 'cars_pkg.json')))}
    ids = sys.argv[1].split(',') if len(sys.argv) > 1 else [c['id'] for c in launch['cars']]
    env = dict(os.environ, KC_BADGE='0')
    failed = []
    for i in ids:
        # relative to kc/, e.g. cars/g80_m3/spec_from_step.pkl; cars not yet in cars_pkg.json carry their own spec path
        spec = pkg[i]['spec'] if i in pkg else next(c['spec'] for c in launch['cars'] if c['id'] == i)
        out = os.path.join(OUT, i)
        cmd = [sys.executable, os.path.join('lib', 'export.py'), spec, out, '--no-slice', '--no-step', '--no-plate']
        r = subprocess.run(cmd, cwd=KC, env=env, capture_output=True, text=True)
        ok = r.returncode == 0 and os.path.exists(os.path.join(out, 'production', f'{i}_production_white.stl'))
        print(('ok    ' if ok else 'FAIL  ') + i)
        if not ok:
            failed.append(i)
            print(r.stderr[-2000:])
    if failed:
        sys.exit('failed: ' + ','.join(failed))


if __name__ == '__main__':
    main()
