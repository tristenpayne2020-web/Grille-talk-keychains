# Cadillac CT5-V Blackwing (2022-2024, pre-facelift) front keychain - revision round 1 (round 0 kept in work/r1).
# Reference: ref/front.jpg = CarBuzz road-test photo of a 2022 CT5-V Blackwing (straight-on, camera at headlight
# height, level - no rotation needed), 3000 x 2250 px. Cross-checked against a straight-on Cadillac configurator view
# (ref/cand/cb_1141504.jpg) for body lines and a close-up (ref/cand/cc_8.jpg) for mesh and crest. See ref/SOURCE.txt.
# Traced half = viewer's LEFT; coordinates are photo pixels of ref/front.jpg (centreline x 1458, 1 mm = 24.9 px).
#
# Design (G80 language):
#  * white = body paint (hood, fenders, bumper incl. the diagonal body-colour 'fangs' and the lower band).
#  * black = slim headlamps, the big upper grille, the tall corner housings (DRL blade + brake-duct vent, plain black
#    like the G80's side vents), the one wide lower opening (side intakes + centre grille, split by two bold diagonal
#    dark divider bars) and the carbon splitter.
#  * light signature (white in black) = Cadillac's vertical lighting, read as one broken vertical line: the curved
#    '(' LED blade hugging the outer edge of each headlamp and, right below it, the tall tapered DRL blade in each
#    corner housing.
#  * relief: Blackwing 'scale' mesh (wide flat hexagon cells in staggered rows, 3.4 x 2.1 mm = the photo's 1.6:1,
#    0.7 mm walls) in the upper grille and the lower centre grille, sitting in a solid border (0.6 / 0.5 mm flat frame +
#    >= 0.85 mm rib) like a mesh behind its surround; three horizontal louvres in each side intake. The corner
#    brake-duct vents stay plain black (like the G80's side vents) so the white DRL blade reads on its own.
#  * grooves: hood front shut line above the grille (dipping steeply into the lamps), the hood/fender shut lines
#    (lamp -> cowl corner, like the G80's fender lines) and the two edges of the hood power dome.
#  * small detail: one parking-sensor ring per side. Dropped: tow-hook cover, front camera, plate, fog-lamp eye.
#  * crest (SHOW_BADGE): 2021+ Cadillac crest (10.0 x 4.3 mm, 8 % over the photo) as a white shield, quartered: a
#    black horizontal quartering line with the dark red/blue quarters (upper right, lower left) as black windows, the
#    gold-bar quarters white.
# Badge switch: SHOW_BADGE below (or environment KC_BADGE=0 for a badge-free export without editing this file).
import os, sys, math
import shapely
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):
    SHOW_BADGE = False

CX = 1458                       # centreline (px)
GROOVE_W = 0.58                 # shut lines (mm)
CREASE_W = 0.55                 # hood-dome creases (mm)

# ------------------------------------------------------------------------------------------------ outline
OUTLINE = [(1458, 812), (1200, 815), (1000, 821), (880, 827), (800, 831), (775, 838), (750, 851), (728, 866),
        (710, 883), (688, 901), (662, 915), (636, 929), (614, 942), (596, 955), (578, 969), (560, 986),
        (544, 1001), (528, 1013), (514, 1027), (500, 1041), (489, 1058), (481, 1078), (474, 1104), (468, 1140),
        (462, 1200), (457, 1280), (455, 1360), (456, 1440), (460, 1500), (466, 1555), (472, 1600), (478, 1632),
        (484, 1650), (492, 1663), (520, 1676), (560, 1690), (650, 1708), (750, 1719), (850, 1723), (1000, 1725),
        (1200, 1726), (1458, 1727)]
XL = min(x for x, y in OUTLINE)
XR = 2 * CX - XL
YB = max(y for x, y in OUTLINE)
S = 80.5 / (XR - XL)            # mm per px (pipeline mapping)


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


def mirror_x(g):
    return affinity.scale(g, -1, 1, origin=(0, 0))


def sym(g):
    return unary_union([g, mirror_x(g)])


def full(half):
    """left-half px polygon touching the centreline -> symmetric mm polygon"""
    return sym(Polygon(mm(half)).buffer(0))


plain = lambda g: shapely.from_wkb(shapely.to_wkb(g))
OUTLINE_MM = full(OUTLINE[:] + [(CX, YB), (CX, OUTLINE[0][1])])

# ------------------------------------------------------------------------------------------------ traced shapes
# headlamp: the outer end rises to a point under the fender crown (where the hood/fender shut line starts); the inner
# tail ends >= 0.8 mm short of the grille corner
LAMP = [(598, 962), (608, 955), (624, 962), (629, 982), (629, 1010), (636, 1036), (655, 1054), (700, 1066),
        (780, 1081), (832, 1091), (843, 1097), (840, 1104), (826, 1118), (808, 1133), (788, 1145), (760, 1152),
        (720, 1152), (680, 1146), (630, 1138), (585, 1128), (552, 1119), (541, 1100), (540, 1060), (546, 1025),
        (562, 992), (580, 973)]
LAMP_MARGIN = 0.75              # mm of white body kept between the lamp and the outline
# vertical LED bar: a curved '(' blade hugging the lens outer edge, leaning in at the top (clipped by the lens rims)
LAMP_DRL = [(545, 1112), (540, 1060), (545, 1030), (560, 1005), (580, 985), (600, 974), (616, 986), (611, 1004),
            (603, 1018), (593, 1032), (587, 1046), (585, 1072), (586, 1112)]
LIGHT_GAP = 0.6                 # mm of black kept around every light element
LIGHT_GAP_OUT = 0.63            # mm of black between the LED bar and the lens outer rim (body side)
GRILLE = [(866, 1086), (1000, 1082), (1200, 1086), (1458, 1090), (1458, 1393), (1400, 1391), (1300, 1384),
          (1200, 1375), (1120, 1367), (1040, 1355), (1000, 1346), (975, 1336), (955, 1322), (938, 1300),
          (916, 1260), (896, 1230), (883, 1200), (870, 1175), (862, 1150), (858, 1120), (860, 1096)]
HOUSING = [(519, 1177), (548, 1186), (592, 1201), (599, 1220), (616, 1240), (638, 1260), (658, 1280), (677, 1300),
           (695, 1320), (707, 1340), (720, 1360), (724, 1380), (722, 1395), (705, 1440), (687, 1480), (671, 1520),
           (656, 1560), (651, 1580), (653, 1592), (661, 1602), (677, 1620), (681, 1634), (612, 1634), (580, 1624),
           (563, 1608), (554, 1585), (548, 1540), (541, 1480), (533, 1400), (526, 1320), (522, 1250)]
BLADE = [(557, 1214), (584, 1212), (604, 1452), (590, 1460), (574, 1456)]
# one wide lower opening; its bottom sits ~1.1 mm above the splitter (white lower band)
LOWER = [(805, 1437), (1000, 1448), (1458, 1448), (1458, 1646), (1300, 1646),
         (1100, 1652), (1000, 1653), (950, 1651), (850, 1645), (760, 1634), (719, 1622), (705, 1612), (700, 1600),
         (702, 1580), (715, 1560), (730, 1540), (745, 1520), (760, 1500), (773, 1480), (788, 1460), (798, 1447)]
DIV = [(987, 1440), (1072, 1670)]            # lower divider bar centreline (side intake | centre grille)
DIV_W = 1.15
SPLIT = [(470, 1640), (500, 1652), (560, 1658), (650, 1661), (720, 1661), (800, 1669), (900, 1677), (1000, 1685),
         (1150, 1687), (1300, 1689), (1458, 1689), (1458, 1760), (440, 1760)]
SENSOR = (1078, 1404)                        # centred in the white band between grille and lower opening

# ------------------------------------------------------------------------------------------------ mesh
# Blackwing scale mesh: wide flat cells (3.4 x 2.1 mm, 1.6:1 like the photo's cells) in tightly stacked staggered rows
MESH_P, MESH_V, MESH_RIB = 3.4, 1.6, 0.7     # horizontal pitch, row spacing, wall (mm)
FRAME = 0.6                                  # flat black frame between white and the mesh recess (mm)
MIN_CELL = 1.3                               # mm2: smaller cut cells are folded into the ribs
WALL_MIN = 0.85                              # mm: a rib between a hole and the recess wall is never thinner than this
                                             # (thinner ones break in the pipeline's 0.31 mm re-regularisation)


def sopen(g, r):
    """mitred opening that never adds material"""
    return geom.clean(g.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(g))


def regularize(region, ribs, w=0.64):
    """drop rib slivers, close gap slivers narrower than w"""
    r = w / 2 - 0.01
    ribs = sopen(ribs, r).intersection(region)
    gaps = sopen(geom.clean(region.difference(ribs)), r)
    ribs = sopen(geom.clean(region.difference(gaps)), r)
    return geom.clean(ribs)


def tidy(region, ribs, w=0.6):
    """regularise ribs + gaps, then fold every strip-like rib or gap sliver still under w (the wedges where a cut cell
    or a slat meets the recess wall): a thin gap becomes rib; a thin rib is thickened into its hole (so cut cells shrink
    or vanish into the frame instead of merging into ragged bands)."""
    for _ in range(2):
        ribs = regularize(region, ribs, 0.64)
    for _ in range(6):
        changed = False
        gaps = geom.clean(region.difference(ribs))
        tg = geom.thin_strips(gaps, w)
        if tg:
            ribs = geom.clean(unary_union([ribs] + [p.buffer(0.03, join_style=2) for p in tg]).intersection(region))
            changed = True
        tr = geom.thin_strips(ribs, w)
        if tr:
            ribs = geom.clean(unary_union([ribs] + [p.buffer(w / 2 + 0.02, join_style=1) for p in tr]).intersection(region))
            changed = True
        gaps = sopen(geom.clean(region.difference(ribs)), w / 2 - 0.01)       # holes left under w wide close
        gaps = unary_union([q for q in geom.polys(gaps) if q.area >= 0.5]) if not gaps.is_empty else gaps
        ribs = geom.clean(region.difference(gaps))
        if not changed:
            break
    return geom.clean(ribs)


GR = 0.31           # mm: the pipeline re-regularises all relief with a mitred opening of this radius. Plain hexagon holes
                    # whose shortest edge survives that inset (vertical ends 0.55 mm here) and that are pre-opened the
                    # same way below are an exact fixed point of it (for convex shapes opening is idempotent).


def mopen(g, r=GR):
    """mitred opening exactly like the pipeline's (no clipping to the original)"""
    return geom.clean(g.buffer(-r, join_style=2).buffer(r, join_style=2))


def hex_cells(region, x0, y0, P=MESH_P, V=MESH_V, rib=MESH_RIB, min_cell=MIN_CELL):
    """holes of a squashed pointy-top honeycomb (x0 = 0 or P/2 keeps it mirror-symmetric), clipped to the region and
    pre-opened like the pipeline does; pieces under min_cell are folded into the ribs."""
    R = P / math.sqrt(3)
    s = V / (P * math.sqrt(3) / 2)
    minx, miny, maxx, maxy = region.bounds
    cells = []
    j0, j1 = int(math.floor((miny - y0) / V)) - 2, int(math.ceil((maxy - y0) / V)) + 2
    n = int(max(abs(minx), abs(maxx)) / P) + 3
    for j in range(j0, j1 + 1):
        sh = P / 2 if j % 2 else 0.0
        for i in range(-n, n + 1):
            x, y = x0 + sh + i * P, y0 + j * V
            c = Polygon([(x + R * math.cos(math.radians(90 + 60 * k)), y + s * R * math.sin(math.radians(90 + 60 * k)))
                         for k in range(6)])
            cells.append(c.buffer(-rib / 2, join_style=2))
    holes = unary_union(cells).intersection(region)
    keep = [mopen(q) for q in geom.polys(holes)]
    keep = [max(geom.polys(q), key=lambda t: t.area) for q in keep if not q.is_empty]
    return [q for q in keep if q.area >= min_cell]


def hex_mesh(region, x0=0.0, y0=0.0, w=0.6):
    """mesh ribs = region minus the kept holes. Every hole keeps >= WALL_MIN of rib to the recess wall (cells running
    into the wall are cut parallel to it, too-small leftovers are folded into the ribs), so the mesh sits in a solid
    border like the real one behind its surround, and no hole touches the recess wall (holes touching it are what
    the pipeline's re-regularisation fills or cracks). Clean-up so nothing under w is left: a hole's thin tip is
    trimmed off; a hole next to a thin rib sliver is cut back once more."""
    inner = region.buffer(-WALL_MIN, join_style=2)
    holes = []
    for h in hex_cells(region, x0, y0):
        h = mopen(geom.clean(h.intersection(inner)))
        h = max(geom.polys(h), key=lambda q: q.area) if not h.is_empty else Polygon()
        if h.area >= MIN_CELL:
            holes.append(h)
    for _ in range(8):
        changed = False
        new = []
        for h in holes:
            t = geom.thin_strips(h, w)
            if t:
                h = mopen(geom.clean(h.difference(unary_union(t).buffer(0.03, join_style=2))))
                h = max(geom.polys(h), key=lambda q: q.area) if not h.is_empty else Polygon()
                changed = True
            if h.area >= MIN_CELL:
                new.append(h)
            else:
                changed = True
        holes = new
        ribs = geom.clean(region.difference(unary_union(holes)))
        tr = geom.thin_strips(ribs, w)
        if tr:
            T = unary_union(tr).buffer(0.05)
            keep = []
            for h in holes:
                if h.intersects(T):
                    h = mopen(geom.clean(h.intersection(inner)))
                    h = max(geom.polys(h), key=lambda q: q.area) if not h.is_empty else Polygon()
                    changed = True
                if h.area >= MIN_CELL:
                    keep.append(h)
            holes = keep
        if not changed:
            break
    # exact mirror symmetry: left holes + their mirrors, centred holes intersected with their own mirror
    sy = [h for h in holes if h.centroid.x < -0.05]
    sy += [mirror_x(h) for h in sy]
    sy += [geom.clean(h.intersection(mirror_x(h))) for h in holes if abs(h.centroid.x) <= 0.05]
    return geom.clean(region.difference(unary_union(sy)))


def finalize(region, ribs, mirror=True, w=0.6):
    """make the ribs a fixed point of the pipeline's own post-pass (geom.regularize at 0.64, applied to all relief
    after build_maps), with no rib or gap strip under w left, and exactly mirror-symmetric"""
    for _ in range(5):
        r2 = geom.regularize(region, ribs, 0.64)
        gaps = geom.clean(region.difference(r2))
        add = [p.buffer(0.03, join_style=2) for p in geom.thin_strips(gaps, w)]
        add += [p.buffer(0.03, join_style=2) for p in geom.polys(gaps) if p.area < 0.3]
        add += [p.buffer(w / 2 + 0.02, join_style=1) for p in geom.thin_strips(r2, w)]
        if add:
            r2 = geom.clean(unary_union([r2] + add).intersection(region))
        if mirror:
            r2 = geom.clean(sym(geom.clean(r2.intersection(box(-200, -200, 0, 200)))).intersection(region))
        done = r2.symmetric_difference(ribs).area < 0.005
        ribs = r2
        if done:
            break
    return ribs


def hole_top():
    """height of a full hole's top above its cell centre (mm)"""
    return 2 * MESH_V / 3 - (MESH_RIB / 2) / math.cos(math.atan((MESH_V / 3) / (MESH_P / 2)))


def _span(region, x_probe):
    b = region.intersection(LineString([(x_probe, -50), (x_probe, 80)])).bounds
    return b[1], b[3]


def top_phase(region, x_probe, gap=WALL_MIN):
    """row origin y0 so that the top row of holes is complete and sits `gap` mm under the recess top at x_probe (the
    solid rib above it merges with the flat frame: no half cells or wedge slivers along the top)"""
    return _span(region, x_probe)[1] - gap - hole_top()


def centre_phase(region, x_probe):
    """row origin y0 so that as many full rows as fit at x_probe sit centred between the recess top and bottom"""
    lo, hi = _span(region, x_probe)
    ht = hole_top()
    n = int((hi - lo - 2 * WALL_MIN - 2 * ht) // MESH_V) + 1
    margin = (hi - lo - 2 * ht - (n - 1) * MESH_V) / 2
    return hi - margin - ht


def bars(region, pitch, rib, angle, offset=0.0):
    """straight slats (mm) through region at angle (deg)"""
    minx, miny, maxx, maxy = region.bounds
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    D = math.hypot(maxx - minx, maxy - miny) + 4
    g = unary_union([box(cx - D, cy + offset + i * pitch - rib / 2, cx + D, cy + offset + i * pitch + rib / 2)
                     for i in range(-int(D / pitch) - 2, int(D / pitch) + 3)])
    g = affinity.rotate(g, angle, origin=(cx, cy))
    return tidy(region, geom.clean(g.intersection(region)))


def opened(g, r=0.3):
    return geom.clean(g.buffer(-r, join_style=1).buffer(r, join_style=1))


# ------------------------------------------------------------------------------------------------ Cadillac crest
# 2021+ crest traced on the photo (9.3 x 4.0 mm there), drawn 8 % larger (10.0 x 4.3 mm) so the quarter windows stay
# readable: upswept top corners with a blunt ~0.4 mm end, flat top, curved flanks, V bottom. Quartering line at 0.53 of
# the height (photo 0.525).
CREST_HALF = [(0.0, 4.0), (4.62, 4.02), (4.55, 3.72), (4.2, 3.48), (3.85, 3.0), (3.62, 2.25), (3.40, 1.55),
              (3.08, 1.06), (2.55, 0.76), (0.0, 0.0)]
CREST_K = 1.08                       # scale about the crest top
CREST_TOP_Y = (YB - 1149) * S        # mm, crest top (photo)
CREST_FRAME = 0.62                   # white chrome frame
CREST_MID = 2.3                      # mm above the crest tip: the quartering line
CREST_CROSS = 0.55                   # mm, white vertical quartering line (between the dark and the gold quarters)
CREST_BAND = 0.55                    # mm, black horizontal quartering line, run out through both flanks


def crest():
    """white crest silhouette quartered: a black horizontal quartering line runs across the whole crest (out through
    both flanks into the black collar); the dark (red/blue) quarters upper right and lower left are black windows hung
    on it, the gold-bar quarters (upper left, lower right) stay white and merge with the chrome frame. This keeps the
    point symmetry of the real crest and leaves no black island inside white (face.png's mask renderer drops islands
    nested in holes; the 3D builds would not care): the black is one piece with the collar, the white is two pieces."""
    h = CREST_HALF
    sil = Polygon(h + [(-x, y) for x, y in reversed(h[1:-1])]).buffer(0)
    sil = affinity.scale(sil, CREST_K, CREST_K, origin=(0, 4.0))
    sil = sil.buffer(-0.12, join_style=1).buffer(0.12, join_style=1)
    b = sil.bounds
    sil = affinity.translate(sil, 0, CREST_TOP_Y - b[3])
    field = sil.buffer(-CREST_FRAME, join_style=1)
    y0 = sil.bounds[1]
    ymid = y0 + CREST_MID
    c = CREST_CROSS / 2
    hb = CREST_BAND / 2
    ur = field.intersection(box(c, ymid, 9, 30))
    ll = field.intersection(box(-9, 0, -c, ymid))
    band = box(-9, ymid - hb, 9, ymid + hb)
    win = opened(geom.clean(unary_union([ur, ll])), 0.15)
    win = geom.clean(unary_union([win, band]).intersection(sil.buffer(0.3)))
    return plain(geom.clean(sil)), plain(win)


# ------------------------------------------------------------------------------------------------ lights
LAMP_BLACK = geom.clean(Polygon(mm(LAMP)).buffer(0).intersection(OUTLINE_MM.buffer(-LAMP_MARGIN, join_style=1)))
LAMP_BLACK = geom.clean(LAMP_BLACK.buffer(0.35, join_style=1).buffer(-0.7, join_style=1).buffer(0.35, join_style=1)
                        .intersection(LAMP_BLACK.buffer(0.01)))
# LED bar: 0.6 mm of black to the lens top / inner side / bottom, 0.63 mm to the outer rim along the body edge
_edge_band = OUTLINE_MM.difference(OUTLINE_MM.buffer(-(LAMP_MARGIN + LIGHT_GAP_OUT + 0.3), join_style=1))
_lamp_in = LAMP_BLACK.buffer(-LIGHT_GAP_OUT, join_style=1).intersection(
    LAMP_BLACK.buffer(-LIGHT_GAP, join_style=1).union(_edge_band))
LAMP_LIGHT = opened(Polygon(mm(LAMP_DRL)).buffer(0).intersection(_lamp_in))
HOUSING_MM = geom.clean(Polygon(mm(HOUSING)).buffer(0))
BLADE_LIGHT = opened(Polygon(mm(BLADE)).buffer(0).intersection(HOUSING_MM.buffer(-LIGHT_GAP, join_style=1)))

# ------------------------------------------------------------------------------------------------ prims
prims = [
    # engraved lines first (black parts painted later cover their ends)
    # hood front shut line: across the brow, dropping steeply into the lamp's top edge (no knife-edge wedge)
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2,
         pts=[(788, 1106), (796, 1074), (818, 1058), (850, 1047), (920, 1036), (1100, 1030), (1300, 1027),
              (1470, 1026)]),
    # hood / fender shut line: from the lamp's outer top, ~1.2 mm inside the fender crown (as the studio view shows
    # it), then up into the cowl corner like the G80's fender lines
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2,
         pts=[(610, 992), (632, 972), (668, 953), (706, 934), (738, 912), (768, 889), (790, 864), (806, 822)]),
    # hood power-dome edges (the reflection breaks in the photo): from the cowl, converging towards the hood front,
    # ending ~1 mm above the hood front shut line
    dict(kind='stroke', color='groove', width=CREASE_W, smooth=2,
         pts=[(1146, 800), (1158, 850), (1178, 895), (1206, 935), (1230, 968), (1240, 990)]),

    dict(kind='geom', color='black', geom=plain(LAMP_BLACK)),
    dict(kind='geom', color='white', geom=plain(LAMP_LIGHT)),
    dict(kind='poly', color='black', pts=GRILLE),
    dict(kind='poly', color='black', pts=HOUSING),
    dict(kind='geom', color='white', geom=plain(BLADE_LIGHT)),
    dict(kind='poly', color='black', pts=LOWER),
    dict(kind='poly', color='black', pts=SPLIT),
    dict(kind='ring', color='black', c=SENSOR, r_mm=0.95, width=0.5),
]

if SHOW_BADGE:
    CREST, CREST_WIN = crest()
    prims += [dict(kind='geom', color='white', geom=CREST, mirror=False, badge=True),
              dict(kind='geom', color='black', geom=CREST_WIN, mirror=False, badge=True)]
else:
    CREST = Polygon()

# ---- relief regions (built here so the mesh is symmetric and the frames are exact)
_grille = full(GRILLE).buffer(-FRAME, join_style=2)
if SHOW_BADGE:
    # 0.9 mm flat collar round the crest, and a flat bridge from the crest top to the grille frame (no cut row there)
    _grille = _grille.difference(CREST.buffer(0.9)).difference(box(-5.3, CREST_TOP_Y, 5.3, 40))
_grille = geom.clean(_grille)
_lower = full(LOWER)
_div = sym(LineString(mm(DIV)).buffer(DIV_W / 2, cap_style=2))
_lower_in = _lower.buffer(-0.5, join_style=2)
_pieces = geom.polys(geom.clean(_lower_in.difference(_div.buffer(0.5, join_style=2))))
_side_l = unary_union([q for q in _pieces if q.centroid.x < -12])
_centre = unary_union([q for q in _pieces if abs(q.centroid.x) <= 12])

_gx, _gy = 0.0, top_phase(_grille, -7.0)
_lx, _ly = MESH_P / 2, centre_phase(_centre, 0.0)
GRILLE_RIBS = hex_mesh(_grille, x0=_gx, y0=_gy)
LOWER_RIBS = hex_mesh(_centre, x0=_lx, y0=_ly)
SIDE_L_RIBS = finalize(_side_l, bars(_side_l, 2.3, 0.95, 0, offset=0.5), mirror=False)   # 3 even louvres, no stubs

prims += [
    dict(kind='geom', color='relief', geom=plain(_grille), mirror=False, relief=dict(type='custom', ribs=plain(GRILLE_RIBS))),
    dict(kind='geom', color='relief', geom=plain(_centre), mirror=False, relief=dict(type='custom', ribs=plain(LOWER_RIBS))),
    dict(kind='geom', color='relief', geom=plain(sym(_side_l)), mirror=False,
         relief=dict(type='custom', ribs=plain(sym(SIDE_L_RIBS)))),
]

SPEC = dict(
    id='ct5v_blackwing', name='Cadillac CT5-V Blackwing',
    ref='kc/cars/ct5v_blackwing/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.55),
    badge_on=SHOW_BADGE,
)
