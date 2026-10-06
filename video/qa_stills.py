"""QA: bundle once, render stills of a composition at the given frames, and make a contact sheet.
usage: python qa_stills.py <Composition> <frame> [<frame> ...] [--no-bundle] [--scale=0.5]"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
args = [a for a in sys.argv[1:] if not a.startswith('--')]
scale = next((float(a.split('=')[1]) for a in sys.argv if a.startswith('--scale=')), 0.5)
comp, frames = args[0], [int(x) for x in args[1:]]
NPX = 'npx.cmd' if os.name == 'nt' else 'npx'
if '--no-bundle' not in sys.argv:
    subprocess.run([NPX, 'remotion', 'bundle', '--out-dir=build'], check=True, capture_output=True)
os.makedirs('out/stills', exist_ok=True)


def one(fr):
    out = f'out/stills/{comp}_{fr}.png'
    r = subprocess.run([NPX, 'remotion', 'still', 'build', comp, out, f'--frame={fr}', f'--scale={scale}'], capture_output=True, text=True)
    if r.returncode:
        print('FAIL', fr, r.stderr[-800:] or r.stdout[-800:])
    return out


with ThreadPoolExecutor(3) as ex:
    outs = list(ex.map(one, frames))
ims = [Image.open(o).convert('RGB') for o in outs if os.path.exists(o)]
if ims:
    tw = 300 if ims[0].height > ims[0].width else 420
    th = int(tw * ims[0].height / ims[0].width)
    cols = min(len(ims), 6 if tw == 300 else 4)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (tw + 6), rows * (th + 22)), (40, 40, 40))
    for i, (im, fr) in enumerate(zip(ims, frames)):
        x, y = (i % cols) * (tw + 6), (i // cols) * (th + 22)
        sheet.paste(im.resize((tw, th)), (x, y))
        ImageDraw.Draw(sheet).text((x + 4, y + th + 4), f'{comp} f{fr}', fill=(255, 255, 0))
    sheet.save(f'out/stills/_sheet_{comp}.png')
    print('sheet', f'out/stills/_sheet_{comp}.png')
