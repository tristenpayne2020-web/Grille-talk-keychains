"""Render every product in Blender (Cycles, GPU) with the photoreal studio look: replaces make_images.mjs.
Writes the same files to site/build/renders_png/ (front and angled per body color, back, headlight masks, and the
G80's hero / detail-tour views), so make_media.py and everything after it is unchanged.
usage: python site/tools/make_images_blender.py [id,id,...] [--samples=160] [--exposure=0.26] [--white-only]
"""
import json, os, subprocess, sys, tempfile, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BLENDER = os.environ.get('BLENDER', r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
OUT = os.path.join(ROOT, 'site', 'build', 'renders_png')
SCRIPT = os.path.join(ROOT, 'site', 'tools', 'blender_render.py')


def slug(s):
    return ''.join(ch if ch.isalnum() else '-' for ch in s.lower()).strip('-')


def on_white(src, dst):
    from PIL import Image, ImageFilter
    im = Image.open(src).convert('RGBA')
    a = im.getchannel('A')
    sh = Image.new('L', im.size, 0)
    sh.paste(a.point(lambda v: v * 0.22), (0, int(im.height * 0.012)))
    sh = sh.filter(ImageFilter.GaussianBlur(im.width * 0.012))
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    bg.paste(Image.new('RGBA', im.size, (0, 0, 0, 255)), (0, 0), sh)
    bg.alpha_composite(im)
    bg.convert('RGB').save(dst)


def main():
    args = sys.argv[1:]
    only = next((a.split(',') for a in args if not a.startswith('--')), None)
    samples = int(next((a.split('=')[1] for a in args if a.startswith('--samples=')), 160))
    size = int(next((a.split('=')[1] for a in args if a.startswith('--size=')), 2000))
    exposure = float(next((a.split('=')[1] for a in args if a.startswith('--exposure=')), 0.26))
    L = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    items = L['cars'] + [dict(w, wall=True) for w in L.get('wall', {}).get('items', [])]
    colors = [dict(c, slug=slug(c['name'])) for c in L['colors']]
    if '--white-only' in args:
        colors = colors[:1]
    os.makedirs(OUT, exist_ok=True)
    for it in items:
        cid = it['id']
        if only and cid not in only:
            continue
        o = lambda name: os.path.join(OUT, f'{cid}__{name}.png')
        views = [
            dict(angle=0.0, chain=False, colors=colors, out=o('{slug}__front')),
            dict(angle=-0.45, chain=True, colors=colors, out=o('{slug}__angle')),
        ]
        if it.get('headlights', True):     # headlight masks only where the lights are a separate colour
            views += [dict(angle=0.0, chain=False, mask=True, out=o('lights__front')),
                      dict(angle=-0.45, chain=True, mask=True, out=o('lights__angle'))]
        if not it.get('wall'):
            views.append(dict(angle=3.14159265 - 0.32, chain=True, colors=colors[:1], out=o('white__back')))
        if cid == 'g80_m3':
            views += [dict(angle=0.0, chain=True, colors=colors[:1], out=o('white__front-chain')),
                      dict(angle=3.14159265, chain=True, colors=colors[:1], out=o('white__back-straight'))]
        job = dict(id=cid, glb=os.path.join(ROOT, 'site', 'build', 'glb_raw', f'{cid}.glb'), views=views, samples=samples, size=size, exposure=exposure)
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump(job, f)
        t0 = time.time()
        r = subprocess.run([BLENDER, '--background', '--factory-startup', '--python', SCRIPT, '--', f.name],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        os.remove(f.name)
        ok = 'BLENDER_DONE' in r.stdout
        print(('rendered ' if ok else 'FAILED   ') + cid, f'{time.time() - t0:.0f}s', flush=True)
        if not ok:
            print(r.stdout[-3000:], r.stderr[-3000:])
            sys.exit(1)
        for col in colors:          # the same front on white (marketplaces, Shopify's own listings) with a soft contact shadow
            on_white(o(f"{col['slug']}__front"), o(f"{col['slug']}__front-white"))


if __name__ == '__main__':
    main()
