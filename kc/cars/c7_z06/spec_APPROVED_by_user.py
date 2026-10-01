# Chevrolet Corvette C7 Z06 (2015-2019) - front keychain artwork.
# Reference: ref/front_raw.jpg = Wikimedia Commons "2015 Chevy Corvette Stingray Z06 Debut at Detroit Auto Show 10.jpg"
# (4128x2322, CC BY-SA 3.0, see ref/SOURCE.txt).
#
# Photo preprocessing (the car stood on a turntable, ~5 deg yawed, camera above the hood):
#   1. ref/front_level.jpg = front_raw rotated -2.2 deg (best mirror symmetry, trace_tools rotate). All traced numbers
#      below are pixels of THIS image.
#   2. Yaw: every feature was traced on BOTH halves; the design uses the average of the left point and the mirrored
#      right point (avg(), axis C). For a yawed car this cancels the first-order error (the left headlight is 355 px
#      wide in the photo, the right one 283 px; a second, straight-on photo agrees with the average).
#   3. High camera: below the badge the proportions match a level straight-on view (checked against that second
#      photo), above it the hood and the headlight tops are stretched. Y() compresses the rows above the headlight tips
#      smoothly (factor 1 -> K over D0..D1 px above the splitter, K above). ref/front.jpg is the levelled photo warped
#      with exactly this Y() (work/warp.py imports it), so out/overlay.png lines up.
#      Cross-check with a level straight-on photo (ref/cand_blue_show.jpg): height/width 0.49 (design 40.25/80.5 = 0.50),
#      headlight 0.61-0.91 of the height (design 0.61-0.89), hood shut line 0.73 (0.73), grille top 0.41 (0.37-0.43).
#
# Design (G80 language), revision 1 (after the likeness + style/printability reviews):
#   black : whole headlight lenses, grille opening (flush frame + 1.05 mm divider bars), gloss-black hood centre
#           (flush, vent lip -> windshield base) above the recessed hood extractor vent, carbon splitter + Z07 end
#           plates (flat top) at the lower corners, winged-V crossed-flags badge (8.8 x 4.0 mm)
#   white : DRL light pipe as a 0.82 mm 'L' with flat ends (outer vertical leg, rounded bend, long leg along the lens
#           bottom to the inner tip) inside each lens, >= 0.62 mm black rim kept around it
#   relief: centre mesh = long flat C7 hexagons with short chevron tips, rows following the grille's V, centre column
#           on the axis (4 openings there); upper outboard pockets = 1 horizontal 0.9 mm fin; brake ducts below the
#           hockey-stick dividers = open recess; vent = 2 louvres + the centre spine. All with wedge clean-up.
#   groove: clamshell hood shut line (cowl corners -> hood front corners -> wavy front edge) + the nose crease on the
#           axis from the grille's V apex to just below the badge
#   tab   : viewer's left, 64 % height, on the white fender below the headlight
#
# Build note (2026-09-29): Creality Print auto-updated to 7.3.0.6149 and its CLI rejects the call in kc/lib/slicecheck.py
# ('CLI exit 1'). Until the library is updated, run the full build with work/build_cp73.py (export.full with an in-memory
# slicer-call shim: --cli --slice 1 --outputdir DIR --need-gcode-file) and work/build3_cp73.py for the colour set.
import os
import math
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

SHOW_BADGE = True          # crossed-flags winged V (custom prim, see BADGE)
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):   # badge-free export, no edit
    SHOW_BADGE = False
BLACK_HOOD = True          # gloss-black hood centre (traced debut car, cand_5); False = body colour (cand_blue_show)
GROOVE_W = 0.58

# ---------------------------------------------------------------------------------------------- frame
C = 2134.0                 # design axis (levelled px)
HALF_W = 1148.5            # averaged half body width: left edge 946 (1188 from C), right edge 3243 (1109)
PXL, PXR = C - HALF_W, C + HALF_W
YB = 2135.0                # bottom of the splitter at the centreline
S = 80.5 / (PXR - PXL)     # mm per px
_D0, _D1, _K = 700.0, 1100.0, 0.62


def _dp(d):
    if d <= _D0:
        return d
    if d <= _D1:
        t = d - _D0
        return _D0 + t - (1 - _K) * t * t / (2 * (_D1 - _D0))
    return _D1 - (1 - _K) * (_D1 - _D0) / 2 + _K * (d - _D1)


def Y(y):
    """levelled-photo row -> corrected row (== ref/front.jpg)."""
    return YB - _dp(YB - y)


def W(p):
    return (round(p[0], 2), round(Y(p[1]), 2))


def avg(L, R):
    """left-half point + right-half point (mirrored about C) -> averaged, corrected point."""
    return W(((L[0] + 2 * C - R[0]) / 2.0, (L[1] + R[1]) / 2.0))


def avgs(Ls, Rs):
    assert len(Ls) == len(Rs)
    return [avg(a, b) for a, b in zip(Ls, Rs)]


def mm(p):                  # corrected px -> keychain mm (valid: the outline spans exactly PXL..PXR and ends at YB)
    return ((p[0] - C) * S, (YB - p[1]) * S)


def px(q):                  # keychain mm -> corrected px
    return (q[0] / S + C, YB - q[1] / S)


def chaikin_open(pts, n=1):
    """Chaikin smoothing of an open polyline; the end points stay fixed."""
    for _ in range(n):
        out = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            out += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        out.append(pts[-1])
        pts = out
    return pts


def rounded(pts, keep, n=2):
    """closed polygon, Chaikin-smoothed except at the vertices listed in keep (they stay sharp)."""
    keep = sorted(set(keep))
    out = []
    for i, k in enumerate(keep):
        k2 = keep[(i + 1) % len(keep)]
        seg = pts[k:k2 + 1] if k2 > k else pts[k:] + pts[:k2 + 1]
        out += chaikin_open(seg, n)[:-1]
    return [(round(x, 2), round(y, 2)) for x, y in out]


def ring_pts(g):
    return [(round(x, 2), round(y, 2)) for x, y in list(g.exterior.coords)[:-1]]


# ---------------------------------------------------------------------------------------------- outline
# top: hood centre bulge meets the windshield, dips over the outer hood, rises to the cowl corner (A-pillar base),
# fender top falls to the side, side, lower corner, splitter tip, splitter bottom.
_OUT_L = [(1735, 833), (1640, 872), (1345, 845), (1200, 905), (1050, 1005), (995, 1045), (962, 1141), (948, 1300),
          (946, 1459), (955, 1680), (979, 1812)]
_OUT_R = [(2380, 843), (2470, 880), (2730, 850), (2925, 932), (3125, 1055), (3180, 1135), (3210, 1230), (3235, 1365),
          (3243, 1500), (3238, 1680), (3212, 1812)]
_BODY_LOW = avgs(_OUT_L, _OUT_R)[9:]          # white body's lower corner (tucks in) -> inner edge of the end plate
OUTLINE = ([W((C, 834))] + avgs(_OUT_L, _OUT_R)[:9] +
           [W((PXL, 1893)), W((1000, 1935)), W((1100, 1992)), W((1250, 2052)), W((1450, 2106)),
            W((1650, 2131)), W((C, YB))])
OUTLINE[9] = (PXL, OUTLINE[9][1])            # widest point exactly at PXL (no rescale by the pipeline)
# Z07 carbon splitter end plates: pointed vertical fins at the lower corners (top between the headlight tip and the
# grille top in both photos). In the photo they stand just outside the body side; here they fill the outer strip of
# the lower side (the silhouette width is fixed), their inner edge follows the body's lower-corner tuck.
# rev 1: flat top ~0.75 mm wide inside the outline (no knife-edge tip); the inner-bottom vertex sits on the splitter's
# top edge (W((1080,1905)) is a SPLITTER vertex) so plate + splitter form one black corner without a white needle.
END_PLATE = [W((PXL + 24, 1572)), W((PXL + 30, 1630)), W((PXL + 36, 1700)), W((PXL + 44, 1780)), W((PXL + 58, 1840)),
             W((1080, 1905)), W((PXL - 30, 1905)), W((PXL - 30, 1572))]

# ---------------------------------------------------------------------------------------------- headlight
# 12 points: inner-bottom tip, inner edge up, top-inner corner, top peak, top-outer corner, outer edge, outer-bottom
# corner, bottom edge back to the tip.
_HL_L = [(1400, 1430), (1380, 1350), (1330, 1240), (1280, 1140), (1240, 1078), (1150, 1028), (1078, 1042),
         (1054, 1110), (1050, 1210), (1072, 1305), (1170, 1358), (1300, 1403)]
_HL_R = [(2884, 1432), (2897, 1350), (2918, 1240), (2941, 1140), (2964, 1089), (3044, 1054), (3085, 1064),
         (3130, 1118), (3155, 1215), (3150, 1312), (3040, 1372), (2945, 1416)]
LENS = avgs(_HL_L, _HL_R)
# DRL light pipe: an 'L' - bar down the outer side, rounded bend, long bar along the lower edge to the inner tip
_DRL_L = [(1133, 1192), (1131, 1262), (1142, 1328), (1250, 1378), (1365, 1418)]
_DRL_R = [(3073, 1207), (3075, 1270), (3068, 1328), (2990, 1370), (2895, 1420)]
_drl = avgs(_DRL_L, _DRL_R)
DRL_W = 0.82                                  # rev 1: 0.72 -> 0.82 (G80 stroke weight), flat caps
DRL_RIM = 0.62                                # black lens rim kept below / beside the light pipe (mm)
_lens_mm = Polygon([mm(p) for p in LENS])
_inner = _lens_mm.buffer(-(DRL_RIM + DRL_W / 2), join_style=2, mitre_limit=10)


def _inner_near(i):
    q = mm(LENS[i])
    c = list(_inner.exterior.coords)[:-1]
    return px(min(c, key=lambda v: (v[0] - q[0]) ** 2 + (v[1] - q[1]) ** 2))


# vertical bar as traced, then along the offset bottom edge (vertices at the outer-bottom corner, mid and tip)
# rev 1: bend vertex pulled ~0.2 mm into the lens so the smoothed bend keeps the full rim at the outer-bottom corner
DRL = _drl[:2] + [(_drl[2][0] + 7, _drl[2][1] - 12)] + [_inner_near(10), _inner_near(11), _inner_near(0)]

# ---------------------------------------------------------------------------------------------- grille
_GR_L = [(1850, 1682), (1564, 1650), (1321, 1643), (1293, 1686), (1279, 1750), (1307, 1814), (1350, 1850),
         (1564, 1886), (1850, 1929)]
_GR_R = [(2452, 1680), (2721, 1651), (2950, 1636), (2971, 1671), (2979, 1729), (2943, 1821), (2907, 1846),
         (2710, 1876), (2446, 1915)]
_GR = [W((C, 1716))] + avgs(_GR_L, _GR_R) + [W((C, 1955))]
GRILLE = rounded(_GR, keep=[0, 10], n=2)          # V points on the centreline stay sharp
GRILLE_G = Polygon(GRILLE)
# outboard brake-duct divider (hockey stick: steep from the grille floor, curving to near-horizontal outward)
_DV_L = [(1645, 1893), (1600, 1790), (1575, 1760), (1450, 1752), (1300, 1747)]
_DV_R = [(2652, 1890), (2695, 1795), (2735, 1765), (2850, 1747), (2945, 1737)]
_DV = avgs(_DV_L, _DV_R)
DIV_W = 1.05                                         # mm, flush black divider bar (rev 1: 0.8 -> 1.05, reads vs the duct)
_dv = chaikin_open(_DV[:4], 2) + [_DV[4]]
_knee = _DV[2]
_bot_ext = (_DV[0][0] + (_DV[0][0] - _DV[1][0]) * 0.8, _DV[0][1] + (_DV[0][1] - _DV[1][1]) * 0.8)
_div_line = LineString([_bot_ext] + _dv + [(PXL - 50, _DV[4][1])])
_knee_line = LineString([_knee, (_knee[0], 1500)])
_bar_px = unary_union([_div_line, _knee_line]).buffer(DIV_W / 2 / S, cap_style=2, join_style=2)
_outboard = Polygon([_bot_ext] + _dv + [(PXL - 50, _DV[4][1]), (PXL - 50, 2300), (_bot_ext[0], 2300)])
_upper_out = box(PXL - 50, 1400, _knee[0], 1800).difference(_outboard)
DUCT_G = GRILLE_G.intersection(_outboard).difference(_bar_px)
SLATS_G = GRILLE_G.intersection(_upper_out).difference(_bar_px)
MESH_G = GRILLE_G.difference(_outboard).difference(_upper_out).difference(_bar_px)


def _chevron(g, k):
    """shear the right half up by k*x and the left half up by -k*x (rows follow the grille's V)."""
    R = g.intersection(box(0, -100, 100, 100))
    L = g.intersection(box(-100, -100, 0, 100))
    return unary_union([affinity.affine_transform(R, [1, 0, k, 1, 0, 0]),
                        affinity.affine_transform(L, [1, 0, -k, 1, 0, 0])]).buffer(0)


def honeycomb(region_mm, h=2.27, dx=5.8, tip=1.1, rib=0.72, y0=0.0, k=0.0, min_cell=1.5):
    """C7 grille mesh: long flat hexagons with short pointed ends (points left/right), staggered columns dx apart
    with the centre column on the axis, symmetric about x=0. rev 1 (measured on the level cand_blue_show photo):
    the real cells are long slats with short ~45 deg chevron tips, column pitch ~5.8 mm, row pitch ~2.2 mm, and the
    rows follow the grille's V (both grille edges rise ~0.11 mm/mm outboard) - so the cell is built from h (row
    pitch), dx (column pitch) and tip (length of the pointed end, tip-to-tip width = dx + tip), and the whole
    pattern is sheared by k per half (_chevron). Part-cells smaller than min_cell (mm2) after clipping are folded
    into the ribs so no ragged fragments stay along the walls."""
    w2 = (dx + tip) / 2.0
    minx, miny, maxx, maxy = region_mm.bounds
    nx = int(max(abs(minx), abs(maxx)) / dx) + 2
    lo, hi = miny - k * max(abs(minx), abs(maxx)) - 2 * h, maxy + 2 * h
    cells = []
    for i in range(-nx, nx + 1):
        for j in range(int((lo - y0) / h) - 2, int((hi - y0) / h) + 3):
            x, y = i * dx, y0 + j * h + (h / 2 if i % 2 else 0)
            hx = Polygon([(x + w2, y), (x + w2 - tip, y + h / 2), (x - w2 + tip, y + h / 2), (x - w2, y),
                          (x - w2 + tip, y - h / 2), (x + w2 - tip, y - h / 2)])
            hx = _chevron(hx, k) if k else hx
            cells.append(hx.buffer(-rib / 2, join_style=2))
    holes = unary_union(cells).intersection(region_mm)
    parts = list(holes.geoms) if hasattr(holes, 'geoms') else [holes]
    keep = [p for p in parts if p.area >= min_cell]
    r = 0.3
    keep = unary_union(keep).buffer(-r, join_style=2).buffer(r, join_style=2) if keep else Polygon()
    return region_mm.difference(keep)


_mesh_mm = unary_union([Polygon([mm(p) for p in ring_pts(g)]) for g in (MESH_G.geoms if hasattr(MESH_G, 'geoms') else [MESH_G])])
_mesh_mm = unary_union([_mesh_mm, affinity.scale(_mesh_mm, -1, 1, origin=(0, 0))])


def _polys(g):
    if g.is_empty:
        return []
    return [g] if g.geom_type == 'Polygon' else [q for x in getattr(g, 'geoms', []) for q in _polys(x)]


def _strips(g, w):
    """strip-like pieces of g narrower than w (same test as the library's printability check)."""
    r = w / 2.0
    thin = g.difference(g.buffer(-r, join_style=1).buffer(r, join_style=1).buffer(0.01))
    out = []
    for p in _polys(thin):
        if p.area < 0.004:
            continue
        c = list(p.minimum_rotated_rectangle.exterior.coords)
        L = max(math.dist(c[0], c[1]), math.dist(c[1], c[2]))
        if L >= 1.0 and p.area / max(L, 1e-6) < w:
            out.append(p)
    return out


def regularize(region, ribs, w=0.64, fix_wedges=True):
    """The library's own pattern clean-up (no rib or gap narrower than w mm; mitre joins keep the hexagons sharp).
    fix_wedges: afterwards drop the thin rib wedges and fill the thin gap wedges that survive it where cells/fins
    meet a sloping wall (one pass, pieces found with the printability check's own test)."""
    r = w / 2 - 0.01
    ribs = ribs.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(region)
    gaps = region.difference(ribs).buffer(-r, join_style=2).buffer(r, join_style=2).intersection(region)
    ribs = region.difference(gaps)
    ribs = ribs.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(region)
    if fix_wedges:
        bad_r = _strips(ribs, 0.6)
        if bad_r:
            ribs = ribs.difference(unary_union(bad_r))
        bad_g = _strips(region.difference(ribs), 0.6)
        if bad_g:
            ribs = unary_union([ribs, unary_union(bad_g)]).intersection(region)
    return ribs


def mirrored(g):
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])


def poly_mm(g):
    return Polygon([mm(p) for p in ring_pts(g)])


# rows: the centre column holds exactly 4 openings between the grille's V points (6.31 .. 14.68 mm), the grille
# frame itself acting as the top and bottom rib: 4 * h - rib = 8.37 mm -> h = 2.27 (real car ~2.2)
MESH_RIB = 0.72
_GR_BOT, _GR_TOP = mm(_GR[-1])[1], mm(_GR[0])[1]
MESH_H = (_GR_TOP - _GR_BOT + MESH_RIB) / 4.0
MESH_K = 0.113                                       # V slope of the grille edges (top 0.110-0.117, bottom 0.110)
MESH_RIBS = regularize(_mesh_mm, honeycomb(_mesh_mm, h=MESH_H, dx=5.8, tip=1.1, rib=MESH_RIB, k=MESH_K,
                                           y0=_GR_BOT + (MESH_H - MESH_RIB) / 2), fix_wedges=True)

# upper outboard pocket (above the duct divider): rev 1 one 0.9 mm horizontal fin centred between the divider and the
# grille top at every x (the pocket is only 2.9-3.3 mm tall with the 1.05 mm divider, too little for two fins with
# >= 0.75 mm gaps); it runs into the flush knee bar on the inboard side and into the rounded outer end of the pocket.
RIB = 0.64


def _fins(region, x_in, x_out, n=2, w=RIB, step=0.1):
    bands = [[] for _ in range(n)]
    xs = [x_in - i * step for i in range(int((x_in - x_out) / step) + 1)] + [x_out]
    probe = (region.bounds[0] + 0.05, region.bounds[2] - 0.05)
    for x in xs:
        xp = min(max(x, probe[0]), probe[1])
        seg = LineString([(xp, -5), (xp, 60)]).intersection(region)
        b, t = seg.bounds[1], seg.bounds[3]
        g = ((t - b) - n * w) / (n + 1)
        for k in range(n):
            y0 = b + (k + 1) * g + k * w
            bands[k].append((x, y0, y0 + w))
    out = []
    for bd in bands:
        out.append(Polygon([(x, y0) for x, y0, _ in bd] + [(x, y1) for x, _, y1 in reversed(bd)]))
    return unary_union(out)


_slats_mm = poly_mm(SLATS_G)
SLAT_RIBS = mirrored(regularize(_slats_mm, _fins(_slats_mm, _slats_mm.bounds[2] + 0.3, _slats_mm.bounds[0] - 0.3, n=1, w=0.9), fix_wedges=True))

# ---------------------------------------------------------------------------------------------- hood
# rev 1: the vent is defined in mm (averaged from both halves of front.jpg + the level cand_blue_show / cand_5 photos):
# a wide, nearly rectangular slot, steep (~60-65 deg) sides and small rounded bottom corners, bottom flat ~77 % of the
# top width. 3.4 mm tall (top edge 36.75 = the lip of the black hood panel, flat bottom 33.35): room for two louvres.
_VENT_MM = [(0.0, 36.75), (-12.0, 36.75), (-11.3, 35.3), (-10.6, 34.0), (-10.0, 33.45), (-9.2, 33.35), (0.0, 33.35)]
VENT = [px(q) for q in _VENT_MM]
_vent_mm = mirrored(Polygon(_VENT_MM))
# two horizontal louvres (evenly spaced) + the Z06 vent's centre spine
_vb, _vt = _vent_mm.bounds[1], _vent_mm.bounds[3]
_vg = ((_vt - _vb) - 2 * RIB) / 3
_louvres = unary_union([box(-20, _vb + _vg, 20, _vb + _vg + RIB), box(-20, _vb + 2 * _vg + RIB, 20, _vb + 2 * (_vg + RIB))])
VENT_RIBS = regularize(_vent_mm, unary_union([_louvres, box(-0.4, _vb - 1, 0.4, _vt + 1)]), fix_wedges=True)
# rev 1: black hood centre. On the traced car (and the Toronto car, cand_5) the raised hood centre from the vent's lip
# back to the windshield base is gloss black (carbon-flash insert, hard edges): with the vent it is one big black block
# in the top centre of the Z06 front. Flush black (no relief); its sides run from the vent's top corners through the
# outline step at +/-11.3 mm (so the outline gives its top edge), 0.1 mm overlap into the vent (painted first).
HOOD_PANEL = [px(q) for q in [(0.0, 36.65), (-11.95, 36.65), (-12.0, 36.75), (-11.3, 40.17), (-11.2, 41.0), (0.0, 41.0)]]
# hood shut lines: side line from the cowl corner down to the hood front corner, wavy front edge to the centre
_HOOD_L = [(1343, 850), (1487, 1257), (1625, 1284), (1825, 1267)]
_HOOD_R = [(2735, 875), (2770, 1273), (2650, 1297), (2442, 1276)]
HOOD = avgs(_HOOD_L, _HOOD_R) + [W((C, 1287))]
# rev 1: the power-dome grooves are gone (the black HOOD_PANEL now shows the dome). New: the sharp nose crease on the
# centreline, rising from the grille's top V apex (14.68 mm) to 0.8 mm below the badge's lower point (~20.8 mm) - the
# C7's pointed nose. It starts inside the grille (joins the V apex like the real crease); a free-floating bar that
# stops short of the grille read as a stem under the badge at keychain scale.
NOSE = [px((0.0, 14.55)), px((0.0, 20.0))]

# ---------------------------------------------------------------------------------------------- splitter
SPLITTER = [W((C, 1990)), W((1990, 1987)), W((1860, 2005)), W((1760, 2032)), W((1690, 2043)), W((1590, 2038)),
            W((1480, 2018)), W((1380, 1995)), W((1280, 1972)), W((1180, 1942)), W((1080, 1905)), W((1010, 1862)),
            W((PXL - 20, 1880)), W((PXL - 20, 2200)), W((C, 2200))]

# ---------------------------------------------------------------------------------------------- badge
# crossed-flags winged V (left half incl. centre, traced on the emblem whose own axis is x=2166; scaled 0.92 for
# the nose sitting closer to the camera than the headlights)
_BADGE_RAW = [(2044, 1423), (2088, 1440), (2098, 1452), (2143, 1472), (2166, 1500), (2166, 1547), (2146, 1522),
              (2100, 1494), (2090, 1482), (2060, 1466)]
_BC = (2166, 1485)
BADGE_WX = 1.12            # rev 1: x stretch about the axis (7.9 -> 8.8 mm wide, 4.0 mm tall: ~2.2:1 like the car)
BADGE = [W((C + (x - _BC[0]) * 0.92 * BADGE_WX, _BC[1] + (y - _BC[1]) * 0.92)) for x, y in _BADGE_RAW]

SPEC = dict(
    id='c7_z06', name='Chevrolet Corvette C7 Z06',
    ref='kc/cars/c7_z06/ref/front.jpg',
    units='px', px_left=PXL, px_right=PXR, px_bottom=YB, center_x=C,
    outline_half=OUTLINE,
    prims=[
        # headlight (whole lens black) + DRL light pipe (white)
        dict(kind='poly', color='black', pts=LENS),
        dict(kind='stroke', color='white', width=DRL_W, smooth=2, pts=DRL, cap='flat'),
        # grille: flush black frame + divider bars, three recessed pockets
        dict(kind='poly', color='black', pts=GRILLE),
        dict(kind='poly', color='relief', pts=ring_pts(MESH_G), relief=dict(type='custom', ribs=MESH_RIBS)),
        dict(kind='poly', color='relief', pts=ring_pts(SLATS_G), relief=dict(type='custom', ribs=SLAT_RIBS)),
        dict(kind='poly', color='relief', pts=ring_pts(DUCT_G), relief=dict(type='none')),
        # black hood centre (flush) + hood extractor vent with louvres (recessed)
    ] + ([dict(kind='poly', color='black', pts=HOOD_PANEL)] if BLACK_HOOD else []) + [
        dict(kind='poly', color='black', pts=VENT, relief=dict(type='custom', ribs=VENT_RIBS)),
        # hood shut lines + nose ridge
        dict(kind='stroke', color='groove', width=GROOVE_W, pts=HOOD),
        dict(kind='stroke', color='groove', width=GROOVE_W, pts=NOSE, cap='flat'),
        # carbon splitter
        dict(kind='poly', color='black', pts=SPLITTER),
        dict(kind='poly', color='black', pts=END_PLATE),
    ] + ([dict(kind='poly', color='black', pts=BADGE)] if SHOW_BADGE else []),
    badge=None,
    badge_on=False,
    badge_note='custom black crossed-flags winged-V prim, on/off with SHOW_BADGE in spec.py',
    tab=dict(y_frac=0.64),
)
