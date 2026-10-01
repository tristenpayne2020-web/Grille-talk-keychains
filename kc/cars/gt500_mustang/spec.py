# Ford Mustang Shelby GT500 (S550, 2020-2022) front keychain - revision round 7 (round 6 backed up in work/r7).
# Reference: ref/front.jpg = Car and Driver 2022 Shelby GT500 gallery photo (Code Orange car, straight-on, camera about
# bumper/headlight height), levelled by -0.45 deg (trace_tools rotate) from ref/front_raw.jpg. See ref/SOURCE.txt.
# Traced half = viewer's LEFT (car's right). Coordinates are photo pixels of ref/front.jpg (1 mm = 15.78 px).
#
# Design (G80 language): white = Code Orange paint. Black = headlamp units, the one big central opening (upper
# grille + gloss bar + lower grille), the corner fog-lamp housings + brake-duct intakes + the trim wrapping under the
# body-colour "fangs", the full-width splitter with its corner dive planes, the hood heat extractor (top centre, from
# the hood's rear edge at the windshield down, like the photo), and the two hood ovals.
# White on black = light signature: the slanted tri-bar DRL (three equal 0.62 mm light guides cut parallel to the lens
# top/bottom like the real ones; nothing else is lit in the lamp), and the corner fog/turn lamps as slim tapered
# blades split into the real lamp's three reflector cells.
# Relief = the line's honeycomb (2.4 mm pitch, 0.8 walls, 1.6 holes, pointy-top) filling the upper grille, the lower
# grille (with its two thin vertical support struts) and the corner ducts out to a 0.8 mm rim rib, edge cells cut at
# the rim like a real mesh behind its frame. One recessed seam line (relief without ribs) marks the gloss bar's lower
# edge.
# Grooves (0.62 mm) = hood front shut line above the grille brow, the hood/fender shut lines and the power-dome creases.
# Body-colour lower bands and fangs stay white. Cobra emblem = one white silhouette drawn for 1:1 (SHOW_BADGE).
#
# Badge switch: SHOW_BADGE below (or environment KC_BADGE=0 for a badge-free export without editing this file).
# The pipeline's badge_on flag only drives spec['badge']; there is no cobra badge type, so the cobra lives here.
import os, sys, math, copy
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom                                                     # read-only use: chaikin / build_maps / regularize

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):   # badge-free export, no edit
    SHOW_BADGE = False

CX, YB, XL = 1116, 1342, 481      # centreline, splitter bottom, fender (body) left edge
XR = 2 * CX - XL
S = 80.5 / (XR - XL)              # mm per px (same mapping as the pipeline)


def mm(pts):
    """photo px -> keychain mm (pipeline frame: x from the centreline, y up from the splitter bottom)"""
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


def full(half):
    """left-half px trace that starts and ends on the centreline -> symmetric polygon in mm"""
    h = mm(half)
    return Polygon(h + [(-x, y) for x, y in reversed(h)]).buffer(0)


tidy = lambda g: shapely.set_precision(g.simplify(0.004), 0.001)   # robust boolean ops later
# geometries handed to the pipeline: plain floating precision model, exactly what export.load_spec's deepcopy (WKB
# round trip) produces, so the probe below sees the same GEOS input as the real build
plain = lambda g: shapely.from_wkb(shapely.to_wkb(g))

# ------------------------------------------------------------------------------------------------ outline
# top edge follows the cowl line incl. the raised hood shoulders beside the extractor (one smooth ramp 965 -> 930 px);
# the upper corner (670,815)..(484,930) follows the photo's fender edge (crisp S550 chamfer) with 1 Chaikin pass
_TOP = [(1116, 784), (1000, 784), (965, 785), (930, 794), (900, 796), (800, 803), (720, 810)]
_CORNER = [(670, 816), (630, 826), (590, 836), (560, 845), (546, 855), (524, 874), (501, 899), (484, 930)]
_SIDE = [(481, 980), (481, 1100), (482, 1200), (483, 1300), (485, 1330), (492, 1340), (600, 1342), (1116, 1342)]
OUTLINE = _TOP + [tuple(p) for p in geom.chaikin(_CORNER, 1, closed=False)] + _SIDE

# ------------------------------------------------------------------------------------------------ grille pockets
UPPER_GRILLE = [(1116, 948), (1016, 949), (916, 954), (866, 959), (816, 968), (790, 982), (776, 1000), (760, 1018),
                (745, 1040), (741, 1060), (1116, 1060)]
LOWER_GRILLE = [(1116, 1176), (779, 1176), (788, 1200), (800, 1235), (805, 1250), (807, 1276), (1116, 1276)]
DUCT = [(540, 1157), (682, 1166), (716, 1258), (545, 1252)]
# honeycomb (mm) - the product line's cell size (GT3 RS 2.4/0.8, C8 2.4/0.8): pointy-top cells, pitch 2.4 / wall 0.8
# -> 1.6 mm holes. Like the R8 / C8 grilles the mesh fills its whole opening and runs out to the frame: the relief
# region is the entire pocket (grille/duct polygon kept REGION_FRAME off white), a RIM-wide rim rib lines the pocket
# wall, and the lattice is cut at the rim - every cut edge cell is kept when the cut piece is still a real hole
# (>= CLIP_MIN_W wide everywhere after a mitred opening and >= CLIP_MIN_AREA of a whole cell), otherwise it is
# folded into the rim. Rim + frame = 0.9 mm of black between any hole and white (cobra included).
# Built here (relief type 'custom') so the centre lattices are exactly mirror-symmetric (x0 in {0, pitch/2}), the duct
# lattice is phased on the left duct and mirrored, and the ribs are a fixed point of the pipeline's 0.64 mm
# regularize. Phases (work/r6/phase6.py + visual check at 20/60 px/mm): upper = two whole rows under the brow + a
# flat-cut bottom row on the gloss bar; lower = three rows, top and bottom cut evenly by the frame (~55-60 %);
# ducts = two rows of 4 whole cells + cut ends (the 3-row duct phases leave triangles in three corners).
HEX_PITCH, HEX_RIB = 2.4, 0.8
REGION_FRAME, RIM = 0.1, 0.8                     # mm: pocket inset from white, rim rib along the pocket wall
HEX_CLIP, CLIP_MIN_W, CLIP_MIN_AREA = True, 0.8, 0.4
HEX_PHASE = dict(upper=(0.0, 2.32), lower=(1.2, 1.32), duct=(1.7, 3.08))
# the lower grille's two thin vertical support struts (photo x 895 px, mirrored): a 0.8 mm hole-free column (one rib),
# snapped (<= 0.3 mm) onto a quarter-pitch line of the lattice so it cuts every row at the same place -> clean
# ~1.0 mm cut cells on both sides instead of alternating half cells
STRUT_W = 0.8
STRUT_X_PHOTO = (895 - CX) * S


def strut_x(x0):
    """quarter-pitch line of the lower lattice nearest the photo strut (cuts cells of both row types at +-p/4)"""
    q = HEX_PITCH / 2
    return x0 + q / 2 + round((STRUT_X_PHOTO - x0 - q / 2) / q) * q

# ------------------------------------------------------------------------------------------------ Shelby cobra
# One white silhouette of the Shelby snake, drawn for 1:1 print in mm (local frame: x right, y up, base at y 0) after
# the 2022 emblem (ref/front.jpg + cand/cd52.jpg close-ups, work/r7/des.py variant 'I'), ~5.9 x 8.7 mm. A solid trace of
# the emblem outline reads as a seahorse/bird on a pad at this size (round head dome, filled coil), so the cues that
# make it a cobra are drawn bigger than life:
#  - head hooked over to the right and angled ~35 deg down (striking), fang tip lowest, the gape a >= 0.68 mm slot
#    running up-left into the head, lower jaw below it running into the throat;
#  - flared hood: the back edge bulges left (~2x the neck), the throat under the jaw is deeply recessed;
#  - slim S neck (~1.1-1.3 mm) sweeping down-right into the coil that sticks out right;
#  - coil: the body curls round at the bottom right into a thin base band (~0.9 mm) that runs left and rises into the
#    tail wedge (blunt end, crest at 2.05 mm) - no flat pad. A 0.7 mm slot between the descending body and the base
#    band is the over/under line of the coil, open at the V between tail and body.
# Every stroke/notch >= 0.6 mm after the clean-up (COBRA_CLEAN opening + closing). Centred on the car like on the
# 2020-22 GT500 (photo emblem centre x 1116.4 vs centreline 1116); the crown sits COBRA_GAP under the grille brow.
COBRA_MM = [(-1.35, 8.35), (-0.5, 8.6), (0.5, 8.65), (1.5, 8.4), (2.25, 7.95), (2.75, 7.35),     # hood top -> head top
            (2.95, 6.8), (2.85, 6.4), (2.5, 6.45),                                               # snout -> fang tip
            (1.95, 6.85), (1.55, 7.1), (1.2, 6.85), (1.35, 6.45),                                # gape (runs up-left)
            (1.8, 6.1), (2.15, 5.75), (2.05, 5.45), (1.65, 5.35), (1.1, 5.3), (0.75, 5.1),       # lower jaw -> throat
            (0.55, 4.7), (0.45, 4.1), (0.5, 3.5), (0.7, 2.95), (1.05, 2.5), (1.55, 2.15),         # belly (S)
            (2.15, 1.9), (2.65, 1.65), (3.0, 1.25), (3.05, 0.8), (2.85, 0.4),                     # coil sticking out right
            (2.45, 0.05), (1.2, -0.05), (-0.3, 0.0), (-1.4, 0.2), (-2.3, 0.55),                   # base band underside
            (-2.95, 1.0), (-2.75, 1.55), (-2.3, 2.05),                                            # tail end -> crest
            (-1.8, 1.8), (-1.2, 1.35), (-0.6, 1.05), (-0.2, 0.95),                                # tail top -> V
            (0.9, 0.92), (1.55, 0.98), (1.72, 1.25), (1.5, 1.62), (0.8, 1.68), (0.2, 1.9),        # coil slot (over/under)
            (-0.2, 2.35), (-0.4, 3.0), (-0.75, 3.7), (-1.25, 4.45), (-1.75, 5.25),               # body back -> hood
            (-2.1, 6.1), (-2.25, 6.95), (-2.1, 7.7)]                                              # flared hood back
COBRA_CLEAN, COBRA_GAP = 0.3, 1.2      # mm: min feature/gap (2 x clean), gap under the brow (>= 0.8 rule)


def cobra():
    """-> white cobra silhouette in keychain mm"""
    sil = Polygon(geom.chaikin(COBRA_MM, 1, closed=True)).buffer(0)
    r = COBRA_CLEAN
    sil = sil.buffer(r).buffer(-r).buffer(-r).buffer(r)                    # no notch / tip narrower than 2r
    b = sil.bounds
    dx = -(b[0] + b[2]) / 2                                                 # bbox centred on the car centreline
    dy = (YB - UPPER_GRILLE[0][1]) * S - COBRA_GAP - b[3]                   # crown COBRA_GAP under the brow
    return plain(tidy(affinity.translate(sil, dx, dy)))


# ------------------------------------------------------------------------------------------------ tri-bar DRL
# three equal light guides: 0.62 mm wide (across the bar), slanted ~51 deg; the top end is cut parallel to the lens
# top at DRL_TOP_GAP below it, the bottom end horizontal at DRL_BOT (like the real guides, not pill-rounded)
DRL_DIR = (-36.3, 45.0)                          # bar axis (px, downwards)
DRL_BOTTOM_X = (627.0, 652.0, 677.0)             # bar centre x on the bottom cut line
DRL_BOT, DRL_W, DRL_TOP_GAP = 999.0, 0.62, 0.68   # px, mm, mm
LENS_TOP = [(600, 924), (690, 933), (731, 940.5)]  # headlamp top edge (px)


def drl_bar(xb):
    ux, uy = DRL_DIR[0] / math.hypot(*DRL_DIR), DRL_DIR[1] / math.hypot(*DRL_DIR)
    hw = DRL_W / 2 / S / abs(uy)                 # horizontal half width (px) of a DRL_W bar
    d = DRL_TOP_GAP / S                          # lens top shifted perpendicularly into the lens (image y down)
    segs = []
    for (ax, ay), (bx, by) in zip(LENS_TOP[:-1], LENS_TOP[1:]):
        L = math.hypot(bx - ax, by - ay); nx, ny = -(by - ay) / L, (bx - ax) / L          # ny > 0: below
        segs.append(LineString([(ax + nx * d - (bx - ax) / L * 30, ay + ny * d - (by - ay) / L * 30),
                                (bx + nx * d + (bx - ax) / L * 30, by + ny * d + (by - ay) / L * 30)]))
    top = unary_union(segs)
    pts = []
    for xe in (xb - hw, xb + hw):
        ray = LineString([(xe, DRL_BOT), (xe - ux * 120, DRL_BOT - uy * 120)])
        hit = ray.intersection(top)                  # first crossing coming up the bar = the lowest offset segment
        hp = [(q.x, q.y) for q in getattr(hit, 'geoms', [hit])]
        pts.append(max(hp, key=lambda q: q[1]))
    return [(xb - hw, DRL_BOT), pts[0], pts[1], (xb + hw, DRL_BOT)]


GROOVE_W = 0.62
FOG_BLADE = [(560, 1110), (676, 1128), (682, 1134), (678, 1141), (563, 1139)]
# the photo's lit lamp shows three reflector segments: two 0.6 mm black dividers (leaning like the segment joints) cut
# the blade into three cells (~2.2 mm each; the inner one tapers to the blade tip)
FOG_DIVIDERS = [[(595, 1100), (603, 1150)], [(638.5, 1100), (646.5, 1150)]]

prims = [
    # ---- engraved lines (drawn first; black parts painted later cover their ends)
    # hood front edge (shut line above the grille brow), from the headlight tip to the centre. It starts with a flat
    # cap laid on the lamp's short top-inner edge (740,942)-(748,948) and leaves it at right angles: no groove sliver
    # at the lamp tip (the far end sits on the centreline and joins its mirror)
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2, cap='flat',
         pts=[(734.5, 943.8), (744.2, 933.3), (775, 918), (860, 899), (950, 890), (1116, 886), (1130, 886)]),
    # hood / fender shut line from the cowl down into the headlight top
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=1, pts=[(585, 828), (596, 880), (607, 932)]),
    # (r7: the fender/fascia groove at the keyring-tab root is gone - the lamp's and fog housing's outer black edges
    # already mark that boundary, and it made the tab look hung on a separate 2 mm strip)
    # power-dome crease: lower edge of the raised hood shoulder, leaving the extractor at its lower outer corner and
    # running out to the fender shut line (starts inside the black vent)
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=2,
         pts=[(950, 815), (940, 820), (918, 829), (885, 839), (800, 854), (720, 863), (650, 875), (599, 887)]),

    # ---- hood heat extractor (black, top centre): like the photo it runs from the hood's rear edge at the windshield
    # (the outline top, black on the edge like the splitter) down to y 819 and out to x 938 (~22.5 x 2.2 mm), between
    # the two raised body-colour shoulders. Top points sit above the outline so the clip is clean (no paint sliver).
    dict(kind='poly', color='black', pts=[(1116, 778), (950, 778), (938, 792), (941, 808), (952, 819), (1116, 819)]),
    # hood ovals: a 2.6 x 0.9 mm stadium (round-capped stroke), so the printed shape is the designed one (an ellipse's
    # tips fall under 0.5 mm)
    dict(kind='stroke', color='black', width=0.9, cap='round', pts=[(787.5, 886.5), (808.5, 883.5)]),

    # ---- headlight unit (inner edge parallel to the DRL bars, blunt inner tip where the lens ends)
    dict(kind='poly', color='black', pts=[(513, 918), (600, 924), (690, 933), (731, 940.5), (738, 947), (732.5, 954.5),
                                         (727, 961.5), (686, 1012), (600, 1013), (540, 1010), (524, 1004), (513, 1004)]),

    # ---- central opening: upper grille + gloss bar + lower grille (one black pocket, mirrored)
    dict(kind='poly', color='black', pts=UPPER_GRILLE[:-1] + [(745, 1080), (755, 1120), (773, 1160), (788, 1200),
                                                              (800, 1235), (805, 1250), (810, 1320), (1116, 1320)]),
    # ---- corner: fog-lamp housing + brake-duct intake + trim under the fang. Below the housing the intake's outer
    # side wall is body colour on the photo, so the black starts at x 530 there; the fang's foot lines up with the
    # housing's bottom edge, and the fang's inner flank is body colour (only ~0.8 mm of dark trim along the duct)
    dict(kind='poly', color='black', pts=[(513, 1071), (530, 1070), (722, 1111), (740, 1162), (735, 1165), (688, 1162),
                                         (724, 1237), (770, 1244), (805, 1250), (810, 1320), (530, 1320),
                                         (530, 1160), (513, 1150)]),
    # ---- splitter (full width) with the corner dive plane
    dict(kind='poly', color='black', pts=[(1116, 1311), (830, 1311), (770, 1301), (600, 1300), (560, 1296),
                                         (520, 1274), (492, 1252), (478, 1250), (478, 1350), (1116, 1350)]),
    # ---- white body bands on the lower fascia
    dict(kind='poly', color='white', pts=[(505, 1236), (522, 1250), (545, 1257), (650, 1266), (740, 1278),
                                         (764, 1283), (768, 1292), (760, 1299), (600, 1299), (560, 1295), (520, 1273),
                                         (505, 1262)]),
    dict(kind='poly', color='white', pts=[(835, 1276), (1116, 1276), (1116, 1311), (822, 1311)]),

    # ---- fog / turn lamp: a slim tapered light blade low in the black housing (~1.8 mm tall at the outer end, 0.8 mm
    # at the inner tip) instead of the full 8.7 x 3.1 mm lens, so its white (~8 mm2 after the FOG_DIVIDERS cuts) is of
    # the tri-bar DRL's order (8.1 mm2): a fine light signature, not a body panel; >= 1.6 mm of black housing above it
    dict(kind='poly', color='white', pts=FOG_BLADE),

    # ---- light signature: the slanted tri-bar DRL only. The lens top is a plain bezel on the real lamp (both reference
    # photos, incl. the lit cd52 lamps) - the outer part of the lamp stays plain black like the AMG / C8 lamps.
] + [dict(kind='poly', color='white', pts=drl_bar(xb)) for xb in DRL_BOTTOM_X] + \
    [dict(kind='stroke', color='black', width=0.6, cap='flat', pts=d) for d in FOG_DIVIDERS]   # fog lamp cell joints

# ---- blunt the two white fang tips (foot under the housing, lower tip at the dive plane): a local 0.3 mm opening of
# the white turns each hair-thin point into a round >= 0.6 mm end (black fills what the opening removes)
FANG_TIPS = [(688, 1162), (805, 1250)]
_W0 = geom.build_maps(dict(units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX, outline_half=OUTLINE,
                           prims=prims))['white']
_Wopen = _W0.buffer(-0.3).buffer(0.3)
for _t in FANG_TIPS:
    _cut = geom.clean(_W0.intersection(Point(mm([_t])[0]).buffer(1.0)).difference(_Wopen))
    if not _cut.is_empty:
        prims.append(dict(kind='geom', color='black', geom=plain(tidy(_cut.buffer(0.01)))))

if SHOW_BADGE:
    COBRA_SIL = cobra()
    prims += [dict(kind='geom', color='white', geom=COBRA_SIL, mirror=False, badge=True)]
else:
    COBRA_SIL = Polygon()

SPEC = dict(
    id='gt500_mustang', name='Ford Mustang Shelby GT500 (S550)',
    ref='kc/cars/gt500_mustang/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.55),
    badge_on=SHOW_BADGE,
)


# ------------------------------------------------------------------------------------------------ honeycomb relief
def hex_holes(region, x0, y0, pitch=None, rib=None, clip=None):
    """Pointy-top honeycomb holes (mm) in region; centres (x0 + i*p [+ p/2 on odd rows], y0 + j*p*sqrt(3)/2).
    Holes are (pitch - rib) across flats. clip=False: whole cells only. clip=True: the mesh runs on to the region edge
    like a real mesh behind its frame - cells crossing the edge are cut there and kept only if the cut piece is still a
    real hole (>= CLIP_MIN_W wide everywhere after a mitred opening, and >= CLIP_MIN_AREA of a whole cell)."""
    pitch, rib = pitch or HEX_PITCH, rib or HEX_RIB
    clip = HEX_CLIP if clip is None else clip
    if region.is_empty:
        return Polygon()
    minx, miny, maxx, maxy = region.bounds
    R = (pitch - rib) / math.sqrt(3)                       # circumradius of a hole
    dy = pitch * math.sqrt(3) / 2
    cells = []
    for j in range(int(math.floor((miny - y0) / dy)) - 1, int(math.ceil((maxy - y0) / dy)) + 2):
        y = y0 + j * dy
        sh = pitch / 2 if j % 2 else 0.0
        for i in range(int(math.floor((minx - x0 - sh) / pitch)) - 1, int(math.ceil((maxx - x0 - sh) / pitch)) + 2):
            x = x0 + sh + i * pitch
            cells.append(Polygon([(x + R * math.cos(math.radians(90 + 60 * k)), y + R * math.sin(math.radians(90 + 60 * k)))
                                  for k in range(6)]))
    arr = np.array(cells, dtype=object)
    shapely.prepare(region)
    inside = shapely.within(arr, region)
    keep = list(arr[inside])
    if clip:
        full_a = 3 * math.sqrt(3) / 2 * R * R
        r = CLIP_MIN_W / 2
        for c in arr[~inside & shapely.intersects(arr, region)]:
            try:
                piece = c.intersection(region)
                piece = piece.buffer(-r, join_style=2).buffer(r, join_style=2).intersection(piece)
            except shapely.errors.GEOSException:            # rare overlay failure on a near-degenerate cut:
                continue                                    # drop that piece (it simply becomes rim rib)
            for q in geom.polys(piece):
                if q.area >= CLIP_MIN_AREA * full_a:
                    keep.append(q)
    return unary_union(keep) if keep else Polygon()


def pockets():
    return (('upper', full(UPPER_GRILLE)), ('lower', full(LOWER_GRILLE)),
            ('duct', unary_union([Polygon(mm(DUCT)), Polygon([(-x, y) for x, y in mm(DUCT)])])))


def relief_regions(black):
    """recess regions (mm): each pocket kept REGION_FRAME away from white, strips under 0.9 mm removed (round
    opening: a mitred one grows mitre spikes that bridge the 0.4 mm strip over the cobra crown)"""
    inner = black.buffer(-REGION_FRAME, join_style=2)
    out = {}
    for key, poly in pockets():
        r = geom.clean(poly.intersection(inner))
        out[key] = geom.clean(r.buffer(-0.45).buffer(0.45).intersection(r))
    return out


def hole_zone(key, r, x0=0.0, rim=None):
    """where holes (whole or cut) may lie inside a recess region: the region minus its rim rib (and the struts)"""
    z = r.buffer(-(RIM if rim is None else rim), join_style=2)
    if key == 'lower':                                     # two hole-free support struts
        _, y0, _, y1 = r.bounds
        sx = strut_x(x0)
        for c in (sx, -sx):
            z = z.difference(box(c - STRUT_W / 2, y0 - 1, c + STRUT_W / 2, y1 + 1))
    return z


mirror_x = lambda g: affinity.scale(g, -1, 1, origin=(0, 0))


def pocket_holes(key, r, x0, y0):
    """honeycomb holes of one pocket (mm). Ducts: lattice phased on the left duct, mirrored onto the right one."""
    if key == 'duct':
        left = unary_union([q for q in geom.polys(r) if q.centroid.x < 0])
        h = hex_holes(hole_zone(key, left, x0), x0, y0)
        return unary_union([h, mirror_x(h)])
    return hex_holes(hole_zone(key, r, x0), x0, y0)


def relief_prims(regions, phases=None):
    phases = phases or HEX_PHASE
    out = []
    for key, r in regions.items():
        x0, y0 = phases[key]
        holes = pocket_holes(key, r, x0, y0)
        if holes.is_empty:
            continue
        # recess = the whole pocket (the mesh runs out to the frame); ribs = pocket minus holes, made a fixed point of
        # the pipeline's mitred 0.64 mm regularize here (twice), so its own pass changes (almost) nothing
        reg = geom.clean(r.intersection(BLACK0))           # pre-clipped exactly like the pipeline does
        ribs = geom.clean(reg.difference(holes))
        for _ in range(2):
            ribs = geom.regularize(reg, ribs, 0.64)
        out.append(dict(kind='geom', color='relief', geom=plain(reg), mirror=False, relief=dict(type='custom', ribs=plain(ribs))))
    return out


# ---- gloss bar: one recessed seam line (relief without ribs) along its bottom edge, where it meets the lower grille
# frame, >= SEAM_CLEAR of flat black from the honeycomb recesses. (The bands near the top of the gloss bar on the photo
# are sky/ground reflections in the piano black, not panel lines, so there is no top seam; the cobra's coil rests on
# plain gloss black.)
SEAM_W, SEAM_CLEAR = 0.68, 0.7
SEAM_X0 = 790        # left end (px); mirrored. Height: as low as the lower-grille recess allows (SEAM_CLEAR above
                     # it), i.e. on the lower grille's frame


def seam_prims(recess):
    """one straight rectangular seam band across the gloss bar, SEAM_CLEAR above the lower-grille recess"""
    near = recess.buffer(SEAM_CLEAR)                        # true (round) clearance
    low = [q for q in geom.polys(recess)                    # lower grille recess (the ducts sit further out)
           if abs(q.centroid.x) < 24 and q.centroid.y < (YB - 1176) * S]
    top = max(q.bounds[3] for q in low) if low else (YB - 1176) * S
    ax = (SEAM_X0 - CX) * S
    ay = top + SEAM_CLEAR + 0.01 + SEAM_W                    # band top edge (mm)
    band = box(ax, ay - SEAM_W, -ax, ay)
    if not COBRA_SIL.is_empty:
        band = band.difference(COBRA_SIL.buffer(SEAM_CLEAR))
    if band.intersects(near):                               # never notch a seam: report instead
        print('WARNING seam at y %.2f mm is closer than %.2f mm to a honeycomb recess' % (ay, SEAM_CLEAR))
        band = band.difference(near)
    band = geom.clean(band)
    if band.is_empty:
        return []
    return [dict(kind='geom', color='relief', geom=plain(tidy(band)), mirror=False, relief=dict(type='none'))]


def _lib_probe(all_prims):
    """Run the pipeline's own map build + min-width repair on the finished prims. Returns None if GEOS' mitred buffer
    trips over (near-)collinear clipped edges in geom.regularize ('side location conflict'), else the total area (mm2)
    of the micro gap slivers the repair's re-regularize leaves in the merged relief (gap pieces that are not holes)."""
    try:
        M = geom.build_maps(copy.deepcopy(dict(SPEC, prims=all_prims)))
        geom.repair_min_width(M)
    except shapely.errors.GEOSException:
        return None
    gaps = geom.polys(M['relief_region'].difference(M['relief_ribs']))
    return sum(q.area for q in gaps if q.area < 0.05)


BLACK0 = geom.build_maps(SPEC)['black']                          # flat 2D paint of everything above
REGIONS = relief_regions(BLACK0)
for _k in (0, 1, -1, 2, -2, 3, -3, 4, -4):   # nudge the rows by 0.013 mm steps (invisible) only if GEOS needs it
    _ph = {key: (x0, y0 + 0.013 * _k) for key, (x0, y0) in HEX_PHASE.items()}
    try:
        _rp = relief_prims(REGIONS, _ph)
        _rp += seam_prims(unary_union([p['geom'] for p in _rp]))
    except shapely.errors.GEOSException:
        continue
    MICRO_GAP_MM2 = _lib_probe(prims + _rp)       # numerical slivers left by the pipeline (a few 1e-4 mm2: unprintable)
    if MICRO_GAP_MM2 is not None:
        break
HEX_PHASE_USED = _ph
SPEC['prims'] = prims + _rp
