"""Pack as many keychains as possible on the K2 bed (260 x 260 mm), leaving room for the prime tower."""
import numpy as np
from shapely.geometry import box, Polygon
from shapely import affinity
from scipy.signal import fftconvolve
from geom import polys

BED = 260.0
RES = 0.5            # mm per cell


def _mask(g, res, pad):
    b = g.bounds
    W = int(np.ceil((b[2] - b[0] + 2 * pad) / res)) + 1
    H = int(np.ceil((b[3] - b[1] + 2 * pad) / res)) + 1
    from PIL import Image, ImageDraw
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    fn = lambda x, y: ((x - b[0] + pad) / res, (y - b[1] + pad) / res)
    gg = g.buffer(pad, join_style=1)
    for p in polys(gg):
        d.polygon([fn(x, y) for x, y in p.exterior.coords], fill=1)
        for h in p.interiors:
            d.polygon([fn(x, y) for x, y in h.coords], fill=0)
    return np.array(img, dtype=np.float32), (b[0] - pad, b[1] - pad)


def pack(outline, spacing=3.0, margin=4.0, tower=(45.0, 32.0), orientations=(0, 180, 90, 270), max_n=60):
    """Bottom-left-fill on a raster. outline: shapely polygon of one keychain (mm, any origin).
    tower: (w, d) mm region reserved in the back-right corner for the prime tower.
    Returns list of (x, y, rot) = translation of the ORIGINAL outline's bbox centre on the bed + rotation (deg),
    and the tower's front-left corner."""
    n = int(BED / RES)
    occ = np.zeros((n, n), dtype=np.float32)
    m = int(margin / RES)
    occ[:m, :] = 1; occ[-m:, :] = 1; occ[:, :m] = 1; occ[:, -m:] = 1
    tw, td = tower
    tx0, ty0 = BED - margin - tw, BED - margin - td
    occ[int(ty0 / RES):, int(tx0 / RES):] = 1
    c0 = ((outline.bounds[0] + outline.bounds[2]) / 2, (outline.bounds[1] + outline.bounds[3]) / 2)
    shapes = {}
    for rot in orientations:
        g = affinity.rotate(outline, rot, origin=c0)
        mk, org = _mask(g, RES, spacing / 2)
        shapes[rot] = (g, mk, org)
    placed = []
    for k in range(max_n):
        best = None
        for rot, (g, mk, org) in shapes.items():
            # collision[i,j] > 0 if the footprint placed with its mask origin at cell (i,j) hits occupied cells
            col = fftconvolve(occ, mk[::-1, ::-1], mode='valid')
            ok = np.argwhere(col < 0.5)
            if len(ok) == 0:
                continue
            # bottom-left: min row (y), then min col (x)
            i, j = ok[np.lexsort((ok[:, 1], ok[:, 0]))[0]]
            score = (i, j)
            if best is None or score < best[0]:
                best = (score, rot, i, j)
        if best is None:
            break
        _, rot, i, j = best
        g, mk, org = shapes[rot]
        h, w = mk.shape
        occ[i:i + h, j:j + w] = np.maximum(occ[i:i + h, j:j + w], mk)
        # translation that moves the rotated outline so its mask origin lands at (j, i)*RES
        dx = j * RES - org[0]
        dy = i * RES - org[1]
        placed.append((c0[0] + dx, c0[1] + dy, rot))
    return placed, (tx0 + 5.0, ty0 + 5.0)


def rows_layout(outline, spacing=3.0, margin=4.0, tower=(45.0, 32.0)):
    """Neat rows: same orientation, tower in the back-right corner. Returns placements like pack()."""
    b = outline.bounds
    w, h = b[2] - b[0], b[3] - b[1]
    c0 = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    ncol = int((BED - 2 * margin + spacing) // (w + spacing))
    nrow = int((BED - 2 * margin + spacing) // (h + spacing))
    tw, td = tower
    placed = []
    x_start = margin + w / 2
    for r in range(nrow):
        for cidx in range(ncol):
            x = x_start + cidx * (w + spacing)
            y = margin + h / 2 + r * (h + spacing)
            # skip cells overlapping the tower corner
            if x + w / 2 > BED - margin - tw and y + h / 2 > BED - margin - td:
                continue
            placed.append((x, y, 0))
    return placed, (BED - margin - tw + 5.0, BED - margin - td + 5.0)


def best_layout(outline, **kw):
    cands = []
    for orient in ((0, 180), (0, 180, 90, 270), (90, 270)):
        a, ta = pack(outline, orientations=orient, **kw)
        cands.append((len(a), 'blf' + str(orient), a, ta))
    b, tb = rows_layout(outline, **{k: v for k, v in kw.items() if k in ('spacing', 'margin', 'tower')})
    cands.append((len(b) + 0.5, 'rows', b, tb))          # prefer neat rows on a tie
    n, how, pl, t = max(cands, key=lambda c: c[0])
    return pl, t, how


def layout_png(outline, placed, tower_xy, tower_wd, path):
    from PIL import Image, ImageDraw
    s = 3
    img = Image.new('RGB', (int(BED * s), int(BED * s)), (40, 44, 52))
    d = ImageDraw.Draw(img)
    c0 = ((outline.bounds[0] + outline.bounds[2]) / 2, (outline.bounds[1] + outline.bounds[3]) / 2)
    for x, y, rot in placed:
        g = affinity.translate(affinity.rotate(outline, rot, origin=c0), x - c0[0], y - c0[1])
        for p in polys(g):
            d.polygon([(px * s, (BED - py) * s) for px, py in p.exterior.coords], fill=(225, 222, 212), outline=(0, 0, 0))
    tx, ty = tower_xy
    d.rectangle([tx * s, (BED - ty - tower_wd[1]) * s, (tx + tower_wd[0]) * s, (BED - ty) * s], outline=(255, 120, 0), width=3)
    d.text((tx * s + 4, (BED - ty - tower_wd[1]) * s + 4), 'prime tower', fill=(255, 150, 50))
    img.save(path)


def grid_layouts(outline, spacing=3.0, margin=4.0, tower=(45.0, 32.0)):
    """Structured layouts: a block of 90-degree-rotated columns + a block of normal rows (split left/right or
    bottom/top). Every cell is an axis-aligned bbox, so parts never touch. Returns the best (placements, tower_xy, name)."""
    b = outline.bounds
    W, H = b[2] - b[0], b[3] - b[1]
    usable = BED - 2 * margin
    tw, td = tower
    tower_rect = (BED - margin - tw, BED - margin - td, BED - margin, BED - margin)

    def ok(cx, cy, w, h):
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        if x0 < margin - 1e-6 or y0 < margin - 1e-6 or x1 > BED - margin + 1e-6 or y1 > BED - margin + 1e-6:
            return False
        tx0, ty0, tx1, ty1 = tower_rect
        return x1 <= tx0 - spacing or y1 <= ty0 - spacing
    best = ([], None, 'none')
    for split in ('lr', 'bt'):
        for kA in range(0, 12):
            pl = []
            if split == 'lr':
                wa = kA * (H + spacing)                       # rotated columns block width
                if wa - spacing > usable:
                    break
                for c in range(kA):
                    for r in range(int((usable + spacing) // (W + spacing))):
                        cx = margin + H / 2 + c * (H + spacing); cy = margin + W / 2 + r * (W + spacing)
                        if ok(cx, cy, H, W):
                            pl.append((cx, cy, 90))
                x0 = margin + wa
                for c in range(int((BED - margin - x0 + spacing) // (W + spacing))):
                    for r in range(int((usable + spacing) // (H + spacing))):
                        cx = x0 + W / 2 + c * (W + spacing); cy = margin + H / 2 + r * (H + spacing)
                        if ok(cx, cy, W, H):
                            pl.append((cx, cy, 0))
            else:
                ha = kA * (H + spacing)                       # normal rows block height (bottom)
                if ha - spacing > usable:
                    break
                for r in range(kA):
                    for c in range(int((usable + spacing) // (W + spacing))):
                        cx = margin + W / 2 + c * (W + spacing); cy = margin + H / 2 + r * (H + spacing)
                        if ok(cx, cy, W, H):
                            pl.append((cx, cy, 0))
                y0 = margin + ha
                for r in range(int((BED - margin - y0 + spacing) // (W + spacing))):
                    for c in range(int((usable + spacing) // (H + spacing))):
                        cx = margin + H / 2 + c * (H + spacing); cy = y0 + W / 2 + r * (W + spacing)
                        if ok(cx, cy, H, W):
                            pl.append((cx, cy, 90))
            if len(pl) > len(best[0]):
                best = (pl, (tower_rect[0] + 5.0, tower_rect[1] + 5.0), f'grid-{split}-{kA}')
    return best


def best_layout(outline, **kw):
    g, tg, how = grid_layouts(outline, **{k: v for k, v in kw.items() if k in ('spacing', 'margin', 'tower')})
    a, ta = pack(outline, **kw)
    if len(a) >= len(g) + 2:                               # only accept the messy BLF layout for a real gain
        return a, ta, 'blf'
    return g, tg, how
