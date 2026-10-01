"""Helpers for tracing a car front from a reference photo (all coordinates are ORIGINAL photo pixels).

  python lib/trace_tools.py info   <img>
  python lib/trace_tools.py grid   <img> <out.png> [--step 50] [--crop x0 y0 x1 y1] [--scale 2]
  python lib/trace_tools.py edges  <img> <out.png> [--crop x0 y0 x1 y1] [--scale 2] [--lo 40] [--hi 120]
  python lib/trace_tools.py points <img> <out.png> x,y x,y ... [--crop x0 y0 x1 y1] [--scale 2]
  python lib/trace_tools.py rotate <img> <out.jpg> <deg>          (level a slightly tilted photo; + = counter-clockwise)
  python lib/trace_tools.py mirror <img> <out.png> <center_x>      (left half + its mirror side by side: symmetry check)
Grid labels always show ORIGINAL pixel coordinates, also on crops/zooms, so you can read positions straight off.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageOps


def _args(a, key, n=1, default=None, cast=float):
    if key in a:
        i = a.index(key)
        vals = [cast(v) for v in a[i + 1:i + 1 + n]]
        del a[i:i + 1 + n]
        return vals if n > 1 else vals[0]
    return default


def _crop_scale(im, crop, scale):
    x0, y0 = 0, 0
    if crop:
        x0, y0, x1, y1 = [int(v) for v in crop]
        im = im.crop((x0, y0, x1, y1))
    if scale and scale != 1:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    return im, x0, y0


def grid(img, out, step=50, crop=None, scale=1.0):
    im = Image.open(img).convert('RGB')
    im, x0, y0 = _crop_scale(im, crop, scale)
    s = scale or 1.0
    d = ImageDraw.Draw(im)
    W, H = im.size
    X0, Y0 = x0, y0
    gx = (int(X0 // step) + 1) * step
    while (gx - X0) * s < W:
        X = (gx - X0) * s
        major = gx % (step * 2) == 0
        d.line([(X, 0), (X, H)], fill=(255, 0, 0) if major else (255, 140, 140), width=1)
        d.text((X + 2, 2), str(gx), fill=(255, 255, 0))
        d.text((X + 2, H - 12), str(gx), fill=(255, 255, 0))
        gx += step
    gy = (int(Y0 // step) + 1) * step
    while (gy - Y0) * s < H:
        Y = (gy - Y0) * s
        major = gy % (step * 2) == 0
        d.line([(0, Y), (W, Y)], fill=(0, 200, 255) if major else (140, 220, 255), width=1)
        d.text((2, Y + 1), str(gy), fill=(0, 255, 0))
        d.text((W - 34, Y + 1), str(gy), fill=(0, 255, 0))
        gy += step
    im.save(out)


def edges(img, out, crop=None, scale=1.0, lo=40, hi=120, step=50):
    import cv2, os
    im = Image.open(img).convert('RGB')
    a = np.array(im)
    g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
    g = cv2.GaussianBlur(g, (3, 3), 0)
    e = cv2.Canny(g, lo, hi)
    over = (a * 0.45).astype(np.uint8)
    over[e > 0] = (255, 255, 0)
    tmp = out + '.tmp.png'
    Image.fromarray(over).save(tmp)
    grid(tmp, out, step=step, crop=crop, scale=scale)       # grid labels = ORIGINAL pixels
    os.remove(tmp)


def points(img, out, pts, crop=None, scale=1.0):
    im = Image.open(img).convert('RGB')
    im, x0, y0 = _crop_scale(im, crop, scale)
    s = scale or 1.0
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate(pts):
        X, Y = (x - x0) * s, (y - y0) * s
        d.ellipse([X - 4, Y - 4, X + 4, Y + 4], outline=(255, 0, 0), width=2)
        d.text((X + 6, Y - 6), f'{i}:{int(x)},{int(y)}', fill=(255, 255, 0))
    if len(pts) > 1:
        d.line([((x - x0) * s, (y - y0) * s) for x, y in pts], fill=(0, 255, 0), width=1)
    im.save(out)


def rotate(img, out, deg):
    im = Image.open(img).convert('RGB')
    im.rotate(deg, resample=Image.BICUBIC, expand=False, fillcolor=(0, 0, 0)).save(out, quality=95)


def mirror(img, out, cx):
    im = Image.open(img).convert('RGB')
    cx = int(cx)
    left = im.crop((0, 0, cx, im.height))
    right = im.crop((cx, 0, im.width, im.height))
    lm = ImageOps.mirror(left)
    canvas = Image.new('RGB', (im.width, im.height))
    # left half + mirrored left half (what a perfectly symmetric car would look like)
    canvas.paste(left, (0, 0)); canvas.paste(lm, (cx, 0))
    canvas.save(out)


if __name__ == '__main__':
    a = sys.argv[1:]
    cmd = a.pop(0)
    crop = _args(a, '--crop', 4)
    scale = _args(a, '--scale', 1, 1.0)
    if cmd == 'info':
        im = Image.open(a[0]); print(im.size, im.mode)
    elif cmd == 'grid':
        step = _args(a, '--step', 1, 50, int)
        grid(a[0], a[1], step, crop, scale)
    elif cmd == 'edges':
        lo = _args(a, '--lo', 1, 40, int); hi = _args(a, '--hi', 1, 120, int); step = _args(a, '--step', 1, 50, int)
        edges(a[0], a[1], crop, scale, lo, hi, step)
    elif cmd == 'points':
        pts = [tuple(float(v) for v in p.split(',')) for p in a[2:]]
        points(a[0], a[1], pts, crop, scale)
    elif cmd == 'rotate':
        rotate(a[0], a[1], float(a[2]))
    elif cmd == 'mirror':
        mirror(a[0], a[1], float(a[2]))
    else:
        print(__doc__)
