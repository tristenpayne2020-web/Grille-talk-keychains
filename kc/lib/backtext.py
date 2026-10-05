"""'GRILLE TALK' in white on the back of every keychain (user decision 2026-10-04).

The back is the side on the bed. A black label plate (text box + margin) sits in the bottom 0.4 mm (2 layers) and the
letters are white inside it, flush with the back. The plate keeps the look the same on every build: on the 1-swap
builds the back is black anyway, and on the classic builds (whose back shows the face pattern) the label stays
readable over white areas. The text is mirrored in X so it reads correctly when the keychain is turned over.
Cost: 3 extra filament changes per plate (layer 1 and 2 carry both colours).
Switch: KC_BACKTEXT=0 turns it off.
"""
import os
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity

TEXT = 'GRILLE TALK'
DEPTH = 0.4            # 2 layers at 0.2 mm
CAP_MM = (4.5, 4.2, 4.0, 3.8, 3.5)   # letter height to try, largest first
TRACK = 0.10           # extra letter spacing (fraction of the font size)
PAD = 1.4              # label margin around the text
EDGE = 1.2             # label keeps this far inside the outline
_cache = {}


def enabled():
    return os.environ.get('KC_BACKTEXT', '1').strip().lower() not in ('0', 'false', 'no', 'off')


def _text_shape(cap_mm):
    """Shapely geometry of TEXT with cap height cap_mm, centred on (0, 0), not mirrored."""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(family='DejaVu Sans', weight='bold')
    size = 10.0
    cap = TextPath((0, 0), 'H', size=size, prop=fp).get_extents().height
    glyphs, x = [], 0.0
    for ch in TEXT:
        if ch == ' ':
            x += size * 0.32
            continue
        tp = TextPath((0, 0), ch, size=size, prop=fp)
        g = None
        for p in sorted((Polygon(p).buffer(0) for p in tp.to_polygons() if len(p) >= 3), key=lambda p: -p.area):
            g = p if g is None else g.symmetric_difference(p)      # even-odd: counters become holes
        if g is None:
            continue
        b = g.bounds
        glyphs.append(affinity.translate(g, x - b[0], 0))
        x += (b[2] - b[0]) + size * TRACK                          # constant ink gap between letters
    g = unary_union(glyphs)
    g = affinity.scale(g, cap_mm / cap, cap_mm / cap, origin=(0, 0))
    b = g.bounds
    return affinity.translate(g, -(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2)


def label(M):
    """(plate, text) shapely geometries in model coordinates, or (None, None) if disabled / it does not fit."""
    key = id(M)
    if key in _cache:
        return _cache[key]
    out = (None, None)
    if enabled():
        O = M['outline']
        room = O.difference(M['hole'].buffer(3.0)).buffer(-EDGE)
        c = room.centroid if not room.is_empty else O.centroid
        ob = O.bounds
        for cap in CAP_MM:
            t = affinity.scale(_text_shape(cap), -1, 1, origin=(0, 0))       # mirrored: reads right from the back
            tb = t.bounds
            plate = box(tb[0] - PAD, tb[1] - PAD, tb[2] + PAD, tb[3] + PAD).buffer(0.8, join_style=1).buffer(-0.8, join_style=1)
            cands = [(dx * dx + dy * dy, c.x + dx, c.y + dy)
                     for dx in np.arange(-12, 12.01, 0.5) for dy in np.arange(-(ob[3] - ob[1]) / 2, (ob[3] - ob[1]) / 2, 0.5)]
            best = next(((x, y) for _, x, y in sorted(cands) if room.contains(affinity.translate(plate, x, y))), None)
            if best:
                out = (affinity.translate(plate, *best), affinity.translate(t, *best))
                break
    _cache[key] = out
    return out


def apply(slabs, M, black_key='black', white_key='white'):
    """Cut the label out of the bottom DEPTH of every slab and add plate (black) + letters (white)."""
    plate, text = label(M)
    if plate is None:
        return slabs
    out = {}
    for k, sl in slabs.items():
        new = []
        for g, z0, z1 in sl:
            if g is None or g.is_empty:
                continue
            if z0 < DEPTH - 1e-6:
                new.append((g.difference(plate), z0, z1))
                inside = g.intersection(plate)
                if z1 > DEPTH + 1e-6 and not inside.is_empty:
                    new.append((inside, DEPTH, z1))
            else:
                new.append((g, z0, z1))
        out[k] = new
    out[black_key] = out.get(black_key, []) + [(plate.difference(text), 0.0, DEPTH)]
    out[white_key] = out.get(white_key, []) + [(text, 0.0, DEPTH)]
    return out
