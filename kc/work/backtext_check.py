"""Preview of the back label: bottom layer of every build for a few cars + geometry checks."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
import geom, build3d, backtext, export
from PIL import Image, ImageDraw
from shapely.geometry import Point

COL = {'black': (25, 25, 28), 'white': (235, 233, 225), 'light': (235, 233, 225), 'body': (200, 16, 46)}
cars = sys.argv[1:] or ['g80_m3', 'tesla_model3', 'ram_trx', 'mclaren_720s']
S = 9  # px per mm
rows = []
for cid in cars:
    sp = os.path.join(HERE, '..', 'cars', cid, 'spec_from_step.pkl' if cid == 'g80_m3' else 'spec.py')
    M = geom.build_maps(export.load_spec(sp)); geom.repair_min_width(M); geom.split_white(M)
    plate, text = backtext.label(M)
    if plate is None:
        print(cid, 'NO FIT'); continue
    thin = text.area - text.buffer(-0.4).buffer(0.4).area
    gaps = plate.difference(text)
    gap_thin = gaps.area - gaps.buffer(-0.25).buffer(0.25).area
    print(f"{cid}: text {text.bounds[2]-text.bounds[0]:.1f} x {text.bounds[3]-text.bounds[1]:.1f} mm, "
          f"strokes <0.8mm area {thin:.3f} mm2, gaps <0.5mm area {gap_thin:.3f} mm2")
    ims = []
    for st, fn in (('production', build3d.build_production), ('classic', build3d.build_classic),
                   ('production3', build3d.build_production3), ('classic3', build3d.build_classic3)):
        parts, sl = fn(M)
        # overlap check between colours
        ks = [k for k in parts if parts[k] is not None]
        ov = sum((parts[a] ^ parts[b]).volume() for i, a in enumerate(ks) for b in ks[i + 1:])
        b = M['outline'].bounds
        W, H = int((b[2] - b[0]) * S) + 20, int((b[3] - b[1]) * S) + 20
        im = Image.new('RGB', (W, H), (60, 64, 80)); d = ImageDraw.Draw(im)
        for k, lst in sl.items():
            for g, z0, z1 in lst:
                if z0 <= 0.1 < z1 and g is not None and not g.is_empty:
                    for p in geom.polys(g):
                        tr = lambda cs: [(W - 10 - (x - b[0]) * S, 10 + (b[3] - y) * S) for x, y in cs]   # seen from the back
                        m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
                        md.polygon(tr(p.exterior.coords), fill=255)
                        for h in p.interiors:
                            md.polygon(tr(h.coords), fill=0)
                        im.paste(COL[k], (0, 0), m)
        d.text((4, 2), f'{cid} {st} overlap {ov:.3f}', fill=(255, 255, 0))
        ims.append(im)
    w = sum(i.width for i in ims) + 10 * len(ims); h = max(i.height for i in ims)
    r = Image.new('RGB', (w, h), (20, 20, 20)); x = 0
    for i in ims:
        r.paste(i, (x, 0)); x += i.width + 10
    rows.append(r)
sheet = Image.new('RGB', (max(r.width for r in rows), sum(r.height + 10 for r in rows)), (20, 20, 20)); y = 0
for r in rows:
    sheet.paste(r, (0, y)); y += r.height + 10
sheet.save(os.path.join(HERE, 'backtext_check.png')); print('saved')
