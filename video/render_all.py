"""Render every Blender shot of the timeline (src/timeline.json) into public/shots/<film>/<shot>/0000.jpg ...
Resumable: Blender skips frames already on disk. usage: python render_all.py [only=<film>] [engine=EEVEE] [samples=64]
Log: renders/render_all.log"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = os.environ.get('BLENDER', r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
A = dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a)
T = json.load(open(os.path.join(HERE, 'src', 'timeline.json')))
MAP = {
    'launch': {'hook': 'hook', 'detail': 'detail', 'headlights': 'headlights', 'colours': 'colours', 'flip': 'flip',
               'garage': 'garage', 'wall': 'wall', 'spinner': 'spinner'},
    'spinner_ad': {'macro': 'sp_macro', 'spin': 'sp_spin', 'specs': 'sp_specs', 'price': 'sp_price'},
    'wall_ad': {'keys': 'w_keys', 'colours': 'w_colours', 'mount': 'w_mount', 'lineup': 'w_lineup'},
}
JOBS = []
for film, sizes in (('launch', [(1080, 1920, '9x16'), (1920, 1080, '16x9')]), ('spinner_ad', [(1080, 1920, '9x16')]),
                    ('wall_ad', [(1080, 1920, '9x16')])):
    for w, h, tag in sizes:
        for s in T[film]['shots']:
            if s['name'] in MAP[film]:
                JOBS.append((film, tag, s['name'], MAP[film][s['name']], s['dur'], w, h))
os.makedirs(os.path.join(HERE, 'renders'), exist_ok=True)
log = open(os.path.join(HERE, 'renders', 'render_all.log'), 'a', encoding='utf-8')
for film, tag, name, shot, dur, w, h in JOBS:
    if A.get('only') and A['only'] not in (film, f'{film}_{tag}', shot):
        continue
    out = os.path.join(HERE, 'public', 'shots', f'{film}_{tag}', name)
    os.makedirs(out, exist_ok=True)
    have = len([f for f in os.listdir(out) if f.endswith('.jpg') and os.path.getsize(os.path.join(out, f)) > 0])
    if have >= dur:
        continue
    t0 = time.time()
    r = subprocess.run([BLENDER, '-b', '--factory-startup', '-P', os.path.join(HERE, 'blender', 'shots.py'), '--',
                        f'shot={shot}', f'w={w}', f'h={h}', f'frames={dur}', f'out={out}',
                        f"engine={A.get('engine', 'EEVEE')}", f"samples={A.get('samples', 64)}"], capture_output=True, text=True, errors='replace')
    n = len([f for f in os.listdir(out) if f.endswith('.jpg')])
    msg = f"{time.strftime('%H:%M:%S')} {film}_{tag}/{name} ({shot}) {n}/{dur} frames, {time.time() - t0:.0f}s, exit {r.returncode}"
    if r.returncode or n < dur:
        msg += '\n' + (r.stdout[-1500:] + r.stderr[-1500:])
    print(msg, flush=True); log.write(msg + '\n'); log.flush()
print('ALL_DONE', flush=True); log.write(time.strftime('%H:%M:%S') + ' ALL_DONE\n'); log.flush()
