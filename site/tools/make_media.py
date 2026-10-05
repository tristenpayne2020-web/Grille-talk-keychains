"""Renders and flat faces -> compressed WebP at 600/1200/2000 px, plus alt text.

in : site/build/renders_png/<id>__<color>__<view>.png (make_images.mjs), site/build/geom/<id>/face.png
out: site/build/media/<id>/<id>-<color>-<view>-<w>.webp and site/build/media/manifest.json
     (manifest: per car, ordered media with file names and alt text; upload_media.py and the preview read it)
The 2000 px file is what gets uploaded to Shopify; Shopify serves the other sizes itself through image_url.
Reference photos in kc/cars/*/ref/ are never read.
usage: python site/tools/make_media.py
"""
import json, os, sys
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BUILD = os.path.join(ROOT, 'site', 'build')
THEME_ASSETS = os.path.join(ROOT, 'theme', 'assets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SIZES = (600, 1200, 2000)


def slug(s):
    return ''.join(ch if ch.isalnum() else '-' for ch in s.lower()).strip('-')


def car_name(c):
    return f"{c['make']} {c['model']} ({c['generation']})" + (f", {c['variant']}" if c.get('variant') else '')


def webp(src, dst_stem, trim=True, box_from=None, sizes=SIZES):
    im = Image.open(src).convert('RGBA')
    if trim:
        bb = (Image.open(box_from).convert('RGBA') if box_from else im).getbbox()   # crop like the reference render
        if bb:   # square crop around the object with 6% margin, keeps every view framed alike
            x0, y0, x1, y1 = bb
            side = int(max(x1 - x0, y1 - y0) * 1.12)
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
            canvas.paste(im.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)), (0, 0))
            im = canvas
    out = []
    for w in sizes:
        r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        p = f'{dst_stem}-{w}.webp'
        r.save(p, quality=84, method=4)
        out.append(os.path.basename(p))
    return out


def one(args):
    c, colors = args
    return c['id'], car_media(c, colors)


def main():
    from multiprocessing import Pool
    launch = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    with Pool(max(2, os.cpu_count() - 2)) as pool:
        manifest = dict(pool.map(one, [(c, launch['colors']) for c in launch['cars']]))
    json.dump(manifest, open(os.path.join(BUILD, 'media', 'manifest.json'), 'w'), indent=1)
    print(len(manifest), 'cars')


def car_media(c, colors):
    cid, name = c['id'], car_name(c)
    od = os.path.join(BUILD, 'media', cid)
    os.makedirs(od, exist_ok=True)
    items = []
    for col in colors:
        cs = slug(col['name'])
        src = os.path.join(BUILD, 'renders_png', f'{cid}__{cs}__front.png')
        files = webp(src, os.path.join(od, f'{cid}-{cs}-front'))
        items.append(dict(kind='variant', color=col['name'], files=files,
                          alt=f"Grille Talk keychain inspired by the {name}, {col['name'].lower()} body, front view"))
        src = os.path.join(BUILD, 'renders_png', f'{cid}__{cs}__angle.png')
        items.append(dict(kind='angle', color=col['name'], files=webp(src, os.path.join(od, f'{cid}-{cs}-angle')),
                          alt=f"Grille Talk keychain inspired by the {name}, {col['name'].lower()} body, angled view with jump ring, chain and split ring"))
        src = os.path.join(BUILD, 'renders_png', f'{cid}__{cs}__front-white.png')
        files = webp(src, os.path.join(od, f'{cid}-{cs}-front-on-white'), trim=False)
        items.append(dict(kind='variant_on_white', color=col['name'], files=files,
                          alt=f"Grille Talk keychain inspired by the {name}, {col['name'].lower()} body, front view on white"))
    # headlight masks for the theme: same square crop as the white front / angle renders, alpha only
    from make_csv import handle
    for view in ('front', 'angle'):
        ref = os.path.join(BUILD, 'renders_png', f'{cid}__white__{view}.png')
        mask = os.path.join(BUILD, 'renders_png', f'{cid}__lights__{view}.png')
        if os.path.exists(mask):
            stem = os.path.join(THEME_ASSETS, f'lights-{handle(c)}-{view}')
            webp(mask, stem, box_from=ref, sizes=(900,))
            os.replace(stem + '-900.webp', stem + '.webp')
    src = os.path.join(BUILD, 'renders_png', f'{cid}__white__back.png')
    items.append(dict(kind='back', color=None, files=webp(src, os.path.join(od, f'{cid}-back')),
                      alt=f'Back of the Grille Talk keychain inspired by the {name}: carbon-fibre finish with GRILLE TALK lettering'))
    face = os.path.join(BUILD, 'geom', cid, 'face.png')
    if os.path.exists(face):
        items.append(dict(kind='face', color=None, files=webp(face, os.path.join(od, f'{cid}-design')),
                          alt=f'Flat two-colour design drawing of the keychain inspired by the {name}'))
    return dict(name=name, glb=f'glb/{cid}.glb', media=items)


if __name__ == '__main__':
    main()
