"""Brand assets for the theme, from brand/ (the supplied files are used as is, never redrawn).

theme/assets/logo-metal-{800,1600}.webp   the supplied metal-texture logo, cropped to its glow (large uses only)
theme/assets/logo-flat.svg                flat trace of the full logo (header, footer, small sizes)
theme/assets/logo-mark.svg                flat trace of the speech-bubble grille mark
theme/assets/favicon.svg, favicon-32.png, apple-touch-icon.png
theme/assets/og-image.jpg                 1200x630 share image: metal logo + a logo-free G80 render
The flat traces threshold the logo's alpha, which isolates the letter and mark shapes from the glow, then follow
the contours with OpenCV. They are traces of the supplied artwork, not a new identity.
usage: python site/tools/make_brand.py   (after make_images.mjs, for the OG image)
"""
import os
import cv2
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'brand', 'logo', 'grille_talk_logo.webp')
ASSETS = os.path.join(ROOT, 'theme', 'assets')
RENDERS = os.path.join(ROOT, 'site', 'build', 'renders_png')
MARK_X = (110, 400)           # x range of the mark in the 2000 px source (the gap to the wordmark is 367..447)


def trace(mask, eps=0.55):
    """Binary mask -> SVG path data (even-odd), pixel units."""
    cs, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    d = []
    for c in cs:
        if cv2.contourArea(c) < 6:
            continue
        a = cv2.approxPolyDP(c, eps, True).reshape(-1, 2)
        d.append('M' + ' '.join(f'{x},{y}' for x, y in a) + 'Z')
    return ''.join(d)


def svg(d, box, title):
    x0, y0, x1, y1 = box
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" role="img">'
            f'<title>{title}</title><path fill="currentColor" fill-rule="evenodd" d="{d}"/></svg>\n')


def bbox(mask, pad):
    ys, xs = np.where(mask > 0)
    return xs.min() - pad, ys.min() - pad, xs.max() + 1 + pad, ys.max() + 1 + pad


def main():
    os.makedirs(ASSETS, exist_ok=True)
    im = Image.open(SRC).convert('RGBA')
    a = np.array(im)
    alpha = a[..., 3]

    # metal logo, cropped to the visible glow
    gx0, gy0, gx1, gy1 = bbox((alpha > 6).astype(np.uint8), 4)
    metal = im.crop((gx0, gy0, gx1, gy1))
    for w in (800, 1600):
        m = metal.resize((w, round(metal.height * w / metal.width)), Image.LANCZOS)
        m.save(os.path.join(ASSETS, f'logo-metal-{w}.webp'), quality=88, method=6)

    # flat traces
    solid = (alpha > 200).astype(np.uint8) * 255
    solid = cv2.morphologyEx(solid, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    full_box = bbox(solid, 2)
    open(os.path.join(ASSETS, 'logo-flat.svg'), 'w').write(svg(trace(solid), full_box, 'Grille Talk'))
    mark = np.zeros_like(solid)
    mark[:, MARK_X[0]:MARK_X[1]] = solid[:, MARK_X[0]:MARK_X[1]]
    mb = bbox(mark, 2)
    # square viewBox around the mark
    cx, cy, side = (mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2, max(mb[2] - mb[0], mb[3] - mb[1])
    sq = (round(cx - side / 2), round(cy - side / 2), round(cx + side / 2), round(cy + side / 2))
    md = trace(mark)
    open(os.path.join(ASSETS, 'logo-mark.svg'), 'w').write(svg(md, sq, 'Grille Talk'))

    # favicon: white mark on black, rounded square
    pad = side * 0.16
    fv = (sq[0] - pad, sq[1] - pad, sq[2] + pad, sq[3] + pad)
    fw = fv[2] - fv[0]
    open(os.path.join(ASSETS, 'favicon.svg'), 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{fv[0]:.0f} {fv[1]:.0f} {fw:.0f} {fw:.0f}">'
        f'<rect x="{fv[0]:.0f}" y="{fv[1]:.0f}" width="{fw:.0f}" height="{fw:.0f}" rx="{fw * 0.2:.0f}" fill="#000"/>'
        f'<path fill="#fff" fill-rule="evenodd" d="{md}"/></svg>\n')
    crop = mark[int(fv[1]):int(fv[3]), int(fv[0]):int(fv[2])]
    for size, name in ((32, 'favicon-32.png'), (180, 'apple-touch-icon.png')):
        m = Image.fromarray(crop).resize((size, size), Image.LANCZOS)
        out = Image.new('RGB', (size, size), (0, 0, 0))
        out.paste(Image.new('RGB', (size, size), (255, 255, 255)), (0, 0), m)
        out.save(os.path.join(ASSETS, name))

    # OG image
    og = Image.new('RGB', (1200, 630), (0, 0, 0))
    car_path = os.path.join(RENDERS, 'g80_m3__white__angle.png')
    if os.path.exists(car_path):
        car = Image.open(car_path).convert('RGBA')
        car = car.crop(car.getbbox())
        car.thumbnail((760, 400), Image.LANCZOS)
        og.paste(car, ((1200 - car.width) // 2, 200 + (400 - car.height) // 2), car)
    lg = metal.copy()
    lg.thumbnail((620, 140), Image.LANCZOS)
    og.paste(lg, ((1200 - lg.width) // 2, 50), lg)
    og.save(os.path.join(ASSETS, 'og-image.jpg'), quality=86)
    print('brand assets written to', ASSETS)


if __name__ == '__main__':
    main()
