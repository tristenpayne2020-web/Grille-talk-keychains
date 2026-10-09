"""Render the three Blender acts of the one-take ad into public/shots/oner_9x16/<act>/ (resumable).
usage: python render_oner.py   log: renders/render_oner.log"""
import os, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = os.environ.get('BLENDER', r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
log = open(os.path.join(HERE, 'renders', 'render_oner.log'), 'a', encoding='utf-8')
for act in ('kc', 'wall', 'spin'):
    out = os.path.join(HERE, 'public', 'shots', 'oner_9x16', act)
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    r = subprocess.run([BLENDER, '-b', '--factory-startup', '-P', os.path.join(HERE, 'blender', 'oner.py'), '--',
                        f'act={act}', 'w=1080', 'h=1920', f'out={out}', 'samples=64'], capture_output=True, text=True, errors='replace')
    n = len([f for f in os.listdir(out) if f.endswith('.jpg')])
    msg = f"{time.strftime('%H:%M:%S')} {act}: {n} frames, {time.time() - t0:.0f}s, exit {r.returncode}"
    if r.returncode:
        msg += '\n' + r.stdout[-1500:] + r.stderr[-1500:]
    print(msg, flush=True); log.write(msg + '\n'); log.flush()
log.write(time.strftime('%H:%M:%S') + ' ONER_DONE\n'); log.flush()
