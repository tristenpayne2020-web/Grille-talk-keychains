"""Hero assets from the real G80 keychain geometry (run after make_svgs.py and make_images.mjs).

theme/assets/hero-g80.webp      static end state (no JS / reduced motion): the front render with its chain, cropped so
                                the body lands exactly where the SVG layers and the 3D canvas put it
The hero box CSS (.hero__box > .hero__static: inset -4% -2% -62% -2%) and these crop fractions must match.
"""
import os, re
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SVG = os.path.join(ROOT, 'site', 'build', 'svg', 'g80_m3')
THEME = os.path.join(ROOT, 'theme')
EXT = dict(left=0.02, right=0.02, top=0.04, bottom=0.62)
# the hero shows the G80/G82 snake-eye front in Matte Gray with yellow headlights (owner's pick); same frame as the G80.
# Render it first: see make_hero_render() below (Blender).
HERO_SVG = os.path.join(ROOT, 'site', 'build', 'svg', 'g80_m3_snakeeye')
HERO_PNG = os.path.join(ROOT, 'site', 'build', 'renders_png', 'g80_m3_snakeeye__gray-yellow__front-chain.png')


def main():
    drl = open(os.path.join(HERO_SVG, 'drl.svg')).read()
    vb = re.search(r'viewBox="([^"]+)"', drl).group(1)   # the G80 frame the hero box is built on
    x0, y0, w_mm, h_mm = map(float, vb.split())        # viewBox already includes the 1 mm margin
    if not os.path.exists(HERO_PNG):
        make_hero_render()
    im = Image.open(HERO_PNG).convert('RGBA')
    a = np.array(im)[..., 3] > 16
    rows = np.where(a.any(1))[0]
    cols = np.where(a.any(0))[0]
    widths = a.sum(1)
    body_rows = np.where(widths > 0.4 * (cols.max() - cols.min()))[0]
    top, bottom = rows.min(), body_rows.max()
    left, right = cols.min(), cols.max()
    k = (right - left) / (w_mm - 2)                      # px per mm (body width = viewBox width - 2 mm)
    print('px/mm x', round(k, 2), 'y', round((bottom - top) / (h_mm - 2), 2))
    vx, vy = left - k, top - k
    vw, vh = w_mm * k, h_mm * k
    box = (vx - EXT['left'] * vw, vy - EXT['top'] * vh, vx + (1 + EXT['right']) * vw, vy + (1 + EXT['bottom']) * vh)
    box = tuple(int(round(v)) for v in box)
    canvas = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0))
    canvas.paste(im.crop((max(0, box[0]), max(0, box[1]), min(im.width, box[2]), min(im.height, box[3]))),
                 (max(0, -box[0]), max(0, -box[1])))
    w = 1600
    canvas = canvas.resize((w, round(canvas.height * w / canvas.width)), Image.LANCZOS)
    canvas.save(os.path.join(THEME, 'assets', 'hero-g80.webp'), quality=86, method=6)
    print('hero-g80.webp', canvas.size)


def make_hero_render():
    """Blender: the snake-eye front with its chain, Matte Gray body, Yellow headlights (colours from launch.json)."""
    import json, subprocess, tempfile
    L = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    gray = next(c for c in L['colors'] if c['name'] == 'Matte Gray')
    yellow = next(h for h in L['headlights']['values'] if h['name'] == 'Yellow')
    col = dict(gray, slug='gray-yellow', lights=yellow['hex'])
    job = dict(id='hero', glb=os.path.join(ROOT, 'site', 'build', 'glb_raw', 'g80_m3_snakeeye.glb'), samples=160, size=2000,
               exposure=0.26, views=[dict(angle=0.0, chain=True, colors=[col], out=HERO_PNG.replace('gray-yellow', '{slug}'))])
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(job, f)
    blender = os.environ.get('BLENDER', r'C:\Program Files\Blender Foundation\Blender 5.2lender.exe')
    subprocess.run([blender, '--background', '--factory-startup', '--python',
                    os.path.join(ROOT, 'site', 'tools', 'blender_render.py'), '--', f.name], check=True, capture_output=True)


def detail_assets():
    """Details chapter: a tight 2000 px G80 render with its chain, plus spotlight anchors (percent of that image)
    for the light signature, grille, intake and tab, measured from the real design map (KC_BADGE=0)."""
    import json, sys
    sys.path.insert(0, os.path.join(ROOT, 'kc', 'lib'))
    os.environ['KC_BADGE'] = '0'
    import geom, export
    from shapely.geometry import Polygon, MultiPolygon
    M = geom.build_maps(export.load_spec(os.path.join(ROOT, 'kc', 'cars', 'g80_m3', 'spec_from_step.pkl')))
    polys = lambda g: [g] if isinstance(g, Polygon) else list(getattr(g, 'geoms', []))
    x0, y0, x1, y1 = M['outline'].bounds
    whites = sorted(polys(M['white']), key=lambda q: -q.area)[1:]
    drl = max([q for q in whites if q.centroid.x < 0], key=lambda q: q.area)
    blacks = polys(M['black'])
    grille = [q for q in blacks if abs(q.centroid.x) < 14 and q.area > 20]
    gy = sum(q.centroid.y * q.area for q in grille) / sum(q.area for q in grille)
    intake = max([q for q in blacks if q.centroid.x < -14 and q.centroid.y < (y0 + y1) / 2], key=lambda q: q.area)
    tx, ty = M['tab_center']
    pts_mm = {'lights': (drl.centroid.x, drl.centroid.y), 'grille': (0.0, gy),
              'intakes': (intake.centroid.x, intake.centroid.y), 'tab': (tx, ty - 6.0)}
    im = Image.open(os.path.join(ROOT, 'site', 'build', 'renders_png', 'g80_m3__white__front-chain.png')).convert('RGBA')
    a = np.array(im)[..., 3] > 16
    widths = a.sum(1)
    cols = np.where(a.any(0))[0]
    rows = np.where(a.any(1))[0]
    body_rows = np.where(widths > 0.4 * (cols.max() - cols.min()))[0]
    left, right, top = cols.min(), cols.max(), rows.min()
    k = (right - left) / (x1 - x0)
    to_px = lambda x, y: (left + (x - x0) * k, top + (y1 - y) * k)
    pad = int(0.04 * (right - left))
    box = (max(0, left - pad), max(0, top - pad), min(im.width, right + pad), min(im.height, rows.max() + pad))
    crop = im.crop(box)
    crop.save(os.path.join(THEME, 'assets', 'detail-g80.webp'), quality=88, method=6)
    W, H = crop.size
    anchors = {}
    # the chain hangs straight down from the hole: its pixel column below the body gives the true hole x in the render
    below = a[body_rows.max() + 10:, :]
    chain_cols = np.where(below.any(0))[0]
    hole_px = chain_cols.mean() if len(chain_cols) else None
    for name, (x, y) in pts_mm.items():
        px, py = to_px(x, y)
        if name == 'tab' and hole_px is not None:
            px = hole_px
        anchors[name] = [round((px - box[0]) / W * 100, 2), round((py - box[1]) / H * 100, 2)]
    open(os.path.join(THEME, 'snippets', 'detail-anchors.liquid'), 'w').write(
        '{%- comment -%} Generated by site/tools/make_hero_assets.py: spotlight anchors (percent of detail-g80.webp). {%- endcomment -%}' + chr(10)
        + json.dumps({'w': W, 'h': H, 'anchors': anchors}) + chr(10))
    # the back, straight on, cropped to the same frame proportions so the tour can cross-fade between them
    bk = Image.open(os.path.join(ROOT, 'site', 'build', 'renders_png', 'g80_m3__white__back-straight.png')).convert('RGBA')
    bb = bk.getbbox()
    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    bw = (bb[2] - bb[0]) * 1.08
    bh = bw * H / W
    if bh < (bb[3] - bb[1]) * 1.08:
        bh = (bb[3] - bb[1]) * 1.08; bw = bh * W / H
    canvas = Image.new('RGBA', (int(bw), int(bh)), (0, 0, 0, 0))
    canvas.paste(bk.crop((int(cx - bw / 2), int(cy - bh / 2), int(cx + bw / 2), int(cy + bh / 2))), (0, 0))
    canvas.resize((W, H), Image.LANCZOS).save(os.path.join(THEME, 'assets', 'detail-g80-back.webp'), quality=88, method=6)
    # lettering sits at the body centre; seen from behind the keyring tab is on the right
    a = np.array(canvas.resize((W, H)))[..., 3] > 16
    widths = a.sum(1); body_rows = np.where(widths > 0.4 * widths.max())[0]
    cols = np.where(a[body_rows.min():body_rows.max()].any(0))[0]
    anchors['back'] = [round(float((cols.min() + (cols.max() - cols.min()) * 0.45) / W * 100), 2),
                       round(float((body_rows.min() + body_rows.max()) / 2 / H * 100), 2)]
    open(os.path.join(THEME, 'snippets', 'detail-anchors.liquid'), 'w').write(
        '{%- comment -%} Generated by site/tools/make_hero_assets.py: spotlight anchors (percent of detail-g80.webp). {%- endcomment -%}' + chr(10)
        + json.dumps({'w': W, 'h': H, 'anchors': anchors}) + chr(10))
    print('detail-g80.webp', crop.size, anchors)


def process_assets():
    """Process chapter visuals from the G80 design layers: the traced outline (stroke) and the flat two-colour design."""
    d = lambda name: re.search(r' d="([^"]*)"', open(os.path.join(SVG, f'{name}.svg')).read()).group(1)
    vb = re.search(r'viewBox="([^"]+)"', open(os.path.join(SVG, 'outline.svg')).read()).group(1)
    open(os.path.join(THEME, 'assets', 'process-trace.svg'), 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><path d="{d("outline")}" fill="none" stroke="#f2f1ee" stroke-width="0.35"/>'
        f'<path d="{d("black")}" fill="none" stroke="#f2f1ee" stroke-opacity="0.55" stroke-width="0.25"/></svg>' + chr(10))
    open(os.path.join(THEME, 'assets', 'process-flat.svg'), 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><path d="{d("white")}" fill="#f2f1ee" fill-rule="evenodd"/>'
        f'<path d="{d("black")}" fill="#141416" fill-rule="evenodd"/></svg>' + chr(10))
    im = Image.open(os.path.join(ROOT, 'site', 'build', 'renders_png', 'g80_m3__white__front.png')).convert('RGBA')
    im = im.crop(im.getbbox())
    im.thumbnail((1400, 1400), Image.LANCZOS)
    im.save(os.path.join(THEME, 'assets', 'process-render.webp'), quality=86, method=6)
    print('process-trace.svg, process-flat.svg, process-render.webp', im.size)


if __name__ == '__main__':
    main()
    detail_assets()
    process_assets()
