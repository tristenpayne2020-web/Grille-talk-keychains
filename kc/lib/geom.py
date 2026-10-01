"""Car-front keychain artwork: spec -> 2D colour maps (in mm).

DESIGN LANGUAGE (measured from the user's G80 M3 keychain STEP):
  * straight-on front elevation, cropped at the base of the windshield (hood + fenders + bumper + splitter),
    perfectly mirror-symmetric about the car centreline
  * car body 80.5 mm wide (x = -40.25 .. +40.25), height follows the car (G80: 38 mm), 3.0 mm thick
  * two colours: white body, black details (headlights, grille, intakes, splitter lip, side vents, badge)
  * white light signatures (DRLs) drawn inside the black headlights
  * grille recessed with slats/mesh standing up inside it
  * engraved shut lines (hood outline, fender lines)
  * keyring tab on the viewer's left side at about mid height, 4.5 mm hole

SPEC FORMAT (python dict `SPEC` in cars/<id>/spec.py) - see cars/README_SPEC.md
Coordinates are in reference-photo pixels (units='px') or millimetres (units='mm').
Primitives are painted in order (painter's algorithm): later primitives paint over earlier ones.
"""
import math, copy, os
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box, GeometryCollection
from shapely.ops import unary_union
from shapely import affinity

# Global logo switch. Badge-free is the default (user decision 2026-09-30, trademark reasons); KC_BADGE=1 turns
# badges back on. Specs with a custom SHOW_BADGE read the same variable, so it is set here before any spec loads.
os.environ.setdefault('KC_BADGE', '0')


def badges_on():
    return os.environ.get('KC_BADGE', '0').strip().lower() in ('1', 'true', 'yes', 'on')

BODY_W = 80.5          # mm, car body width (G80 reference)
T = 3.0                # keychain thickness
EPS = 1e-4


# ----------------------------------------------------------------------------------------------- helpers
def polys(g):
    """Flatten any geometry into a list of Polygons."""
    if g is None or g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    if g.geom_type in ('MultiPolygon', 'GeometryCollection'):
        out = []
        for x in g.geoms:
            out += polys(x)
        return out
    return []


def clean(g, grid=0.001):
    g = shapely.make_valid(g) if not g.is_valid else g
    g = unary_union(polys(g)) if g.geom_type == 'GeometryCollection' else g
    g = shapely.set_precision(g, grid)
    g = unary_union(polys(g))
    return g if not g.is_empty else Polygon()


def chaikin(pts, n=2, closed=True):
    pts = [tuple(p) for p in pts]
    for _ in range(n):
        new = []
        m = len(pts)
        rng = range(m) if closed else range(m - 1)
        if not closed:
            new.append(pts[0])
        for i in rng:
            p, q = np.array(pts[i]), np.array(pts[(i + 1) % m])
            new.append(tuple(0.75 * p + 0.25 * q))
            new.append(tuple(0.25 * p + 0.75 * q))
        if not closed:
            new.append(pts[-1])
        pts = new
    return pts


class Frame:
    """Maps spec coordinates (px or mm) to keychain mm (x right, y up, centreline x=0, y=0 at the bottom of the car)."""

    def __init__(self, spec):
        self.units = spec.get('units', 'px')
        if self.units == 'px':
            L, R = spec['px_left'], spec['px_right']          # x pixel of the car's widest body points
            self.cx = spec.get('center_x', (L + R) / 2.0)
            self.s = BODY_W / float(R - L)
            self.ybot = spec['px_bottom']                       # y pixel of the lowest point of the car outline
            self.yscale = spec.get('y_scale', 1.0)              # optional vertical stretch (perspective correction)
        else:
            self.cx, self.s, self.ybot, self.yscale = 0.0, 1.0, 0.0, 1.0

    def pt(self, p):
        x, y = p
        if self.units == 'px':
            return ((x - self.cx) * self.s, (self.ybot - y) * self.s * self.yscale)
        return (float(x), float(y))

    def pts(self, ps):
        return [self.pt(p) for p in ps]

    def len(self, v):
        """spec length -> mm (lengths in primitives are always mm unless *_px is used)."""
        return v


def mirror_x(g):
    return affinity.scale(g, xfact=-1, yfact=1, origin=(0, 0))


def sym(g, mirror):
    if not mirror:
        return g
    return unary_union([g, mirror_x(g)])


# ----------------------------------------------------------------------------------------------- primitives
def prim_geom(pr, F):
    """Return the shapely geometry (mm) of one primitive, before mirroring."""
    k = pr['kind']
    if k == 'poly':
        pts = F.pts(pr['pts'])
        if pr.get('smooth'):
            pts = chaikin(pts, pr['smooth'], closed=True)
        g = Polygon(pts).buffer(0)
    elif k == 'stroke':                                    # polyline with width (mm)
        pts = F.pts(pr['pts'])
        if pr.get('smooth'):
            pts = chaikin(pts, pr['smooth'], closed=False)
        cap = {'round': 1, 'flat': 2, 'square': 3}[pr.get('cap', 'round')]
        g = LineString(pts).buffer(pr['width'] / 2.0, cap_style=cap, join_style=pr.get('join', 1))
    elif k == 'circle':
        c = F.pt(pr['c'])
        r = pr['r_mm'] if 'r_mm' in pr else pr['r'] * F.s
        g = Point(c).buffer(r, 64)
    elif k == 'ring':                                      # annulus: outer radius + width (mm)
        c = F.pt(pr['c'])
        r = pr['r_mm'] if 'r_mm' in pr else pr['r'] * F.s
        g = Point(c).buffer(r, 64).difference(Point(c).buffer(r - pr['width'], 64))
    elif k == 'ellipse':
        c = F.pt(pr['c'])
        rx = pr['rx_mm'] if 'rx_mm' in pr else pr['rx'] * F.s
        ry = pr['ry_mm'] if 'ry_mm' in pr else pr['ry'] * F.s
        g = affinity.scale(Point(c).buffer(1.0, 64), rx, ry)
        if pr.get('rot'):
            g = affinity.rotate(g, pr['rot'], origin=c)
    elif k == 'mm_poly':                                   # polygon given directly in keychain mm
        g = Polygon(pr['pts']).buffer(0)
    elif k == 'geom':                                      # shapely geometry already in mm (used by badges/tests)
        g = pr['geom']
    else:
        raise ValueError('unknown primitive kind ' + k)
    if pr.get('offset'):                                   # grow (+) / shrink (-) in mm
        g = g.buffer(pr['offset'], join_style=2 if pr.get('sharp') else 1)
    return g


# ----------------------------------------------------------------------------------------------- relief patterns
def pattern_ribs(region, pat):
    """Ribs (standing bars/mesh) inside a recessed region. All sizes in mm.
    pat: {'type': 'hbars'|'vbars'|'bars'|'hex'|'grid'|'diamond'|'none', 'pitch', 'rib', 'angle', 'margin', 'offset'}"""
    t = pat.get('type', 'none')
    if t == 'none' or region.is_empty:
        return Polygon()
    if t == 'custom':                                      # explicit rib geometry (mm)
        return clean(pat['ribs'].intersection(region))
    minx, miny, maxx, maxy = region.bounds
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    D = math.hypot(maxx - minx, maxy - miny) + 10
    pitch, rib = pat.get('pitch', 2.4), pat.get('rib', 1.0)
    ang = pat.get('angle', 0.0)
    off = pat.get('offset', 0.0)
    geoms = []
    if t in ('hbars', 'vbars', 'bars'):
        if t == 'vbars':
            ang += 90
        n = int(D / pitch) + 2
        for i in range(-n, n + 1):
            y = cy + off + i * pitch
            geoms.append(box(cx - D, y - rib / 2, cx + D, y + rib / 2))
        g = unary_union(geoms)
        g = affinity.rotate(g, ang, origin=(cx, cy))
    elif t in ('grid', 'diamond'):
        n = int(D / pitch) + 2
        for i in range(-n, n + 1):
            y = cy + off + i * pitch
            geoms.append(box(cx - D, y - rib / 2, cx + D, y + rib / 2))
            geoms.append(box(cx + off + i * pitch - rib / 2, cy - D, cx + off + i * pitch + rib / 2, cy + D))
        g = unary_union(geoms)
        g = affinity.rotate(g, ang + (45 if t == 'diamond' else 0), origin=(cx, cy))
    elif t == 'hex':
        # honeycomb: cells of across-flats `pitch - rib`, walls `rib`
        a = pitch / math.sqrt(3)                         # circumradius of the cell pitch hexagon
        cells = []
        nx = int(D / (1.5 * a)) + 2
        ny = int(D / pitch) + 2
        for i in range(-nx, nx + 1):
            for j in range(-ny, ny + 1):
                x = cx + i * 1.5 * a
                y = cy + off + j * pitch + (pitch / 2 if i % 2 else 0)
                hexa = Polygon([(x + a * math.cos(math.radians(60 * k)), y + a * math.sin(math.radians(60 * k))) for k in range(6)])
                cells.append(hexa.buffer(-rib / 2, join_style=2))
        holes = unary_union(cells)
        holes = affinity.rotate(holes, ang, origin=(cx, cy))
        g = box(cx - D, cy - D, cx + D, cy + D).difference(holes)
    else:
        raise ValueError('pattern ' + t)
    margin = pat.get('margin', 0.0)                        # keep ribs off the recess wall (mm); 0 = ribs meet the wall
    inner = region.buffer(-margin) if margin else region
    ribs = clean(g.intersection(inner))
    return regularize(region, ribs, pat.get('min_w', 0.64))


def regularize(region, ribs, w=0.6):
    """Remove rib slivers and close gap slivers narrower than w (clipped bars at the recess edge)."""
    r = w / 2 - 0.01
    ribs = ribs.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(region)
    gaps = region.difference(ribs)
    gaps = gaps.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(region)
    ribs = region.difference(gaps)
    ribs = ribs.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(region)
    return clean(ribs)


# ----------------------------------------------------------------------------------------------- keyring tab
def keyring_tab(outline, tab):
    """Round tab with a hole on the viewer's left. Returns (outline_with_tab, hole)."""
    minx, miny, maxx, maxy = outline.bounds
    H = maxy - miny
    y = tab.get('y_mm', miny + tab.get('y_frac', 0.55) * H)
    # leftmost outline point at this height
    probe = outline.intersection(LineString([(minx - 50, y), (maxx + 50, y)]))
    xl = probe.bounds[0] if not probe.is_empty else minx
    R, r = tab.get('outer_r', 4.25), tab.get('hole_d', 4.5) / 2
    cxh = xl - tab.get('reach', 3.3)
    c = Point(cxh, y)
    ring = c.buffer(R, 96)
    # neck: blend circle into the body with a concave fillet, locally only
    fil = tab.get('fillet', 1.6)
    zone = box(cxh - R - 1, y - R - fil - 3, xl + 3.0, y + R + fil + 3)
    u = unary_union([outline, ring])
    blended = u.buffer(fil, join_style=1).buffer(-fil, join_style=1)
    out = unary_union([u, blended.intersection(zone)])
    hole = c.buffer(r, 96)
    return clean(out), hole, (cxh, y)


# ----------------------------------------------------------------------------------------------- badges
def badge_geoms(b):
    """Simplified badge shapes (mm), painted as a list of (colour, geometry). Centred at b['c_mm'], size = diameter.
    Kept deliberately simple: at keychain scale only a few 0.5 mm+ features survive printing."""
    cx, cy = b['c_mm']
    d = b.get('d', 4.4)
    R = d / 2
    t = b['type']
    out = []
    P = lambda r: Point(cx, cy).buffer(r, 96)
    if t == 'roundel':                                    # BMW: black ring, white disc, black quarters (TL + BR white)
        out.append(('black', P(R)))
        out.append(('white', P(R - 0.55)))
        q = R - 0.55
        out.append(('black', box(cx, cy, cx + q, cy + q).intersection(P(q))))
        out.append(('black', box(cx - q, cy - q, cx, cy).intersection(P(q))))
    elif t == 'star':                                     # Mercedes: ring + three-pointed star
        out.append(('black', P(R)))
        out.append(('white', P(R - 0.5)))
        pts = []
        for k in range(3):
            a = math.radians(90 + 120 * k)
            pts.append((cx + (R - 0.5) * math.cos(a), cy + (R - 0.5) * math.sin(a)))
            a2 = math.radians(90 + 120 * k + 60)
            pts.append((cx + 0.55 * math.cos(a2), cy + 0.55 * math.sin(a2)))
        out.append(('black', Polygon(pts)))
    elif t == 'rings':                                    # Audi: four interlocking rings, horizontal
        w = b.get('w', 0.5)
        rr = b.get('ring_r', d / 2)
        step = rr * 1.45
        for k in range(4):
            x = cx + (k - 1.5) * step
            out.append((b.get('colour', 'white'), Point(x, cy).buffer(rr, 64).difference(Point(x, cy).buffer(rr - w, 64))))
    elif t == 'shield':                                   # generic crest (Porsche / Lamborghini) - shield outline + field
        w = d * 0.78
        h = d
        sh = Polygon([(cx - w / 2, cy + h / 2), (cx + w / 2, cy + h / 2), (cx + w / 2, cy - h * 0.1),
                      (cx, cy - h / 2), (cx - w / 2, cy - h * 0.1)])
        out.append(('black', sh.buffer(0.25, join_style=1)))
        out.append(('white', sh.buffer(-0.35, join_style=1)))
        out.append(('black', sh.buffer(-0.95, join_style=1)))
    elif t == 'flags':                                    # Corvette crossed flags (simplified X of two pennants)
        L = d * 1.3
        for s in (-1, 1):
            ln = LineString([(cx - s * L / 2, cy - L * 0.32), (cx + s * L / 2, cy + L * 0.32)])
            out.append(('black', ln.buffer(0.3, cap_style=2)))
            fx = cx + s * L / 2
            fy = cy + L * 0.32
            flag = Polygon([(fx, fy), (fx - s * L * 0.34, fy + L * 0.02), (fx - s * L * 0.30, fy - L * 0.24), (fx, fy - L * 0.20)])
            out.append(('black', flag.buffer(0.1)))
    elif t == 'pony':                                     # Ford Mustang: running-horse silhouette (very simplified)
        pts = [(-1.0, -0.2), (-0.55, 0.05), (-0.15, 0.1), (0.35, 0.25), (0.62, 0.55), (0.95, 0.5), (0.8, 0.3), (0.55, 0.12),
               (0.6, -0.15), (0.95, -0.55), (0.75, -0.6), (0.35, -0.2), (-0.2, -0.15), (-0.55, -0.55), (-0.8, -0.5), (-0.55, -0.2)]
        g = Polygon([(cx + x * R * 1.2, cy + y * R * 1.2) for x, y in pts]).buffer(0.08)
        out.append(('black', g))
    elif t == 'bar':
        out.append(('black', box(cx - R, cy - 0.35, cx + R, cy + 0.35)))
    else:
        raise ValueError('badge ' + t)
    return out


# ----------------------------------------------------------------------------------------------- spec -> maps
def build_maps(spec, verbose=False):
    """Paint the spec into disjoint 2D regions (mm):
       white, black (flush black on the face), relief (recessed black regions) with ribs, grooves (with the colour
       under them), outline, hole. Returns dict."""
    F = Frame(spec)
    # ---- outline
    if 'outline_half' in spec:
        half = F.pts(spec['outline_half'])
        if spec.get('outline_smooth'):
            half = chaikin(half, spec['outline_smooth'], closed=False)
        # force the end points onto the centreline and mirror
        half = [(abs(x), y) for x, y in half]              # either half may be traced
        half[0] = (0.0, half[0][1]); half[-1] = (0.0, half[-1][1])
        full = half + [(-x, y) for x, y in reversed(half)]
        outline = Polygon(full).buffer(0)
    else:
        outline = prim_geom(spec['outline'], F)
    outline = clean(outline)
    # re-centre vertically: y=0 at the lowest point
    miny = outline.bounds[1]
    if abs(miny) > 1e-6:
        outline = affinity.translate(outline, 0, -miny)
    dy = -miny
    # scale check: force exact body width
    w = outline.bounds[2] - outline.bounds[0]
    if spec.get('force_width', True) and abs(w - BODY_W) > 0.02:
        k = BODY_W / w
        outline = affinity.scale(outline, k, k, origin=(0, 0))
    else:
        k = 1.0

    def place(g):
        g = affinity.translate(g, 0, dy)
        return affinity.scale(g, k, k, origin=(0, 0)) if k != 1.0 else g

    white = outline
    black = Polygon()
    groove_any = Polygon()
    relief = []      # list of (region, ribs_geometry, pattern)
    for pr in spec.get('prims', []):
        g = place(prim_geom(pr, F))
        g = sym(g, pr.get('mirror', True))
        g = clean(g.intersection(outline)) if pr.get('clip', True) else clean(g)
        col = pr['color']
        if col == 'black':
            black = unary_union([black, g]); white = white.difference(g)
            groove_any = groove_any.difference(g)
            if pr.get('relief'):
                relief.append([g, pr['relief']])
        elif col == 'white':
            white = unary_union([white, g]); black = black.difference(g)
            groove_any = groove_any.difference(g)
            relief = [[r.difference(g), p] for r, p in relief]
        elif col == 'groove':
            groove_any = unary_union([groove_any, g])
        elif col == 'relief':                              # recess an existing black area with a pattern (no repaint)
            relief.append([g.intersection(black), pr['relief']])
        else:
            raise ValueError(col)
    # badge
    if spec.get('badge') and spec.get('badge_on', True) and badges_on():
        b = dict(spec['badge'])
        if 'c' in b:
            b['c_mm'] = place(Point(F.pt(b['c']))).coords[0]
        for col, g in badge_geoms(b):
            g = clean(g)
            if col == 'black':
                black = unary_union([black, g]); white = white.difference(g); groove_any = groove_any.difference(g)
            else:
                white = unary_union([white, g]); black = black.difference(g); groove_any = groove_any.difference(g)
                relief = [[r.difference(g), p] for r, p in relief]
    # keyring tab
    tab = spec.get('tab', {})
    outline2, hole, tabc = keyring_tab(outline, tab)
    added = outline2.difference(outline)
    white = unary_union([white, added])
    outline = outline2
    white, black = clean(white.difference(hole)), clean(black.difference(hole))
    groove_any = clean(groove_any.difference(hole).intersection(outline))
    # relief regions & ribs
    rel_regions, rel_ribs = [], []
    for r, pat in relief:
        r = clean(r.intersection(black))
        if r.is_empty:
            continue
        ribs = pattern_ribs(r, pat)
        rel_regions.append(r); rel_ribs.append(ribs)
    relief_region = clean(unary_union(rel_regions)) if rel_regions else Polygon()
    relief_ribs = clean(unary_union(rel_ribs)) if rel_ribs else Polygon()
    grooves_on_white = clean(groove_any.intersection(white))
    grooves_on_black = clean(groove_any.intersection(black).difference(relief_region))
    return dict(outline=outline, white=white, black=black, relief_region=relief_region, relief_ribs=relief_ribs,
                grooves_white=grooves_on_white, grooves_black=grooves_on_black, hole=hole, tab_center=tabc,
                frame=F, place=(dy, k))


# ----------------------------------------------------------------------------------------------- printability
def thin_strips(g, w, min_len=1.0):
    """Parts of g narrower than w that are strip-like (longer than min_len); sharp corners are ignored."""
    if g.is_empty:
        return []
    r = w / 2.0
    opened = g.buffer(-r, join_style=1).buffer(r, join_style=1)
    thin = g.difference(opened.buffer(0.01))
    out = []
    for p in polys(thin):
        if p.area < 0.004:
            continue
        mrr = p.minimum_rotated_rectangle
        xy = np.asarray(mrr.exterior.coords) if mrr.geom_type == 'Polygon' else np.zeros((5, 2))
        L = max(np.linalg.norm(xy[1] - xy[0]), np.linalg.norm(xy[2] - xy[1]))   # long side of the thin piece
        if L >= min_len and p.area / max(L, 1e-6) < w:     # mean width below w over a real length (not a corner tip)
            out.append(p)
    return out


def check_maps(M, min_w=0.5, warn_w=0.6, relief_w=0.6):
    """Printability report for a 0.4 mm nozzle."""
    rep = {'errors': [], 'warnings': []}
    face_black = unary_union([M['black']])
    items = [('black feature', face_black, min_w), ('white feature', M['white'], min_w),
             ('groove', unary_union([M['grooves_white'], M['grooves_black']]), min_w),
             ('relief rib', M['relief_ribs'], relief_w),
             ('relief gap', M['relief_region'].difference(M['relief_ribs']), relief_w)]
    for name, g, w in items:
        # relief patterns are generated + regularised automatically; wedges where bars meet a curved recess wall
        # are harmless (the slicer fills or skips them), so they are only warnings
        bucket = rep['warnings'] if name.startswith('relief') else rep['errors']
        for p in thin_strips(g, w):
            c = p.representative_point()
            bucket.append(f'{name} thinner than {w} mm near ({c.x:.1f}, {c.y:.1f}) mm, piece ~{p.length / 2:.1f} mm long, mean width {p.area / (p.length / 2):.2f} mm')
        if w < warn_w:
            for p in thin_strips(g, warn_w):
                c = p.representative_point()
                rep['warnings'].append(f'{name} thinner than {warn_w} mm near ({c.x:.1f}, {c.y:.1f}) mm')
    # keyring wall
    tx, ty = M['tab_center']
    ring = Point(tx, ty).buffer(4.25).intersection(M['outline']).difference(M['hole'])
    # tiny isolated specks
    for name, g in (('black', M['black']), ('white', M['white'])):
        for p in polys(g):
            if p.area < 0.25:
                c = p.representative_point()
                rep['errors'].append(f'isolated {name} speck {p.area:.2f} mm2 at ({c.x:.1f}, {c.y:.1f})')
    b = M['outline'].bounds
    rep['size_mm'] = (round(b[2] - b[0], 2), round(b[3] - b[1], 2))
    rep['areas_mm2'] = {k: round(M[k].area, 1) for k in ('outline', 'white', 'black', 'relief_region', 'relief_ribs')}
    return rep


def repair_min_width(M, w=0.5, iters=2, verbose=False):
    """Safety net: widen strip-like features narrower than w (black, white, grooves) by growing them into the
    neighbouring colour. Sharp corners are left alone. Returns the list of repairs made."""
    log = []
    O = M['outline']
    for it in range(iters):
        changed = False
        for name in ('black', 'white', 'grooves'):
            g = M['black'] if name == 'black' else M['white'] if name == 'white' else unary_union([M['grooves_white'], M['grooves_black']])
            strips = thin_strips(g, w)
            if not strips:
                continue
            grow = []
            for p in strips:
                L = p.length / 2.0
                mw = p.area / max(L, 1e-6)
                grow.append(p.buffer(max(0.02, (w - mw) / 2 + 0.03), join_style=1))
                c = p.representative_point()
                log.append(f'{name}: widened strip at ({c.x:.1f},{c.y:.1f}) from ~{mw:.2f} mm')
            G = clean(unary_union(grow).intersection(O).difference(M['hole']))
            if name == 'black':
                M['black'] = clean(unary_union([M['black'], G])); M['white'] = clean(M['white'].difference(G))
                M['grooves_white'] = clean(M['grooves_white'].difference(G))
            elif name == 'white':
                M['white'] = clean(unary_union([M['white'], G])); M['black'] = clean(M['black'].difference(G))
                M['relief_region'] = clean(M['relief_region'].difference(G)); M['relief_ribs'] = clean(M['relief_ribs'].difference(G))
                M['grooves_black'] = clean(M['grooves_black'].difference(G))
            else:
                M['grooves_white'] = clean(unary_union([M['grooves_white'], G.intersection(M['white'])]))
                M['grooves_black'] = clean(unary_union([M['grooves_black'], G.intersection(M['black']).difference(M['relief_region'])]))
            changed = True
        # relief ribs/gaps: re-regularise after any repair nibbled the recess
        R, P = M['relief_region'], M['relief_ribs']
        if not P.is_empty:
            M['relief_ribs'] = regularize(R, P.intersection(R), 0.64)
        if not changed:
            break
    if verbose:
        print('\n'.join(log))
    return log


def split_white(M):
    """Body paint vs white details. The largest white region is the body; small round solid discs (parking-sensor
    centres, the insides of Audi-style badge rings) are body paint too. Every other white island (DRL light signatures, badge details) stays white."""
    comps = sorted(polys(M['white']), key=lambda q: -q.area)
    body, light = [], []
    for i, q in enumerate(comps):
        if i == 0:
            body.append(q); continue
        b = q.bounds
        w, h = b[2] - b[0], b[3] - b[1]
        circ = 4 * math.pi * q.area / (q.length ** 2) if q.length else 0
        solid_disc = (len(q.interiors) == 0 and circ > 0.90 and max(w, h) / max(min(w, h), 1e-6) < 1.2 and q.area < 4.0)
        (body if solid_disc else light).append(q)
    M['white_body'] = clean(unary_union(body)) if body else Polygon()
    M['white_light'] = clean(unary_union(light)) if light else Polygon()
    return M
