# Dodge Challenger SRT Hellcat (2019-2023, dual-snorkel hood) front keychain - v2
# Reference: ref/front.jpg (levelled -0.4 deg from ref/front_raw.jpg, see ref/SOURCE.txt). Traced half = viewer's LEFT.
import os, sys, math
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom                                                     # read-only use: chaikin / clean / polys

CX, YB, XL = 640.5, 869, 150          # centreline, splitter bottom, fender (body) left edge  (photo px)
XR = 2 * CX - XL
S = 80.5 / (XR - XL)                   # mm per px (same mapping as the pipeline)


def mm(pts):
    return [((x - CX) * S, (YB - y) * S) for x, y in pts]


def mirror_union(g):
    return geom.clean(unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))]))


plain = lambda g: shapely.from_wkb(shapely.to_wkb(shapely.set_precision(g, 0.001)))

OUTLINE = [(640.5, 325), (500, 325), (400, 325), (330, 325), (312, 327), (295, 336), (275, 347), (255, 360),
           (235, 375), (218, 390), (202, 406), (188, 424), (176, 442), (167, 460), (160, 478), (155, 495),
           (151.5, 512), (150, 530), (150, 600), (150.5, 650), (151.5, 700), (153, 760), (155, 795), (157, 808),
           (162, 816), (172, 822), (200, 829), (250, 836), (320, 845), (400, 856), (500, 864), (580, 868),
           (640.5, 869)]

# headlight + grille band (one black opening), edges measured column by column on the photo. Over the lamps the top
# edge is raised 0.35-0.5 mm: the brow hides the top of the real lamps, the keychain shows the full halo rings
BAND = [(700, 526), (620, 526), (580, 525), (540, 524), (500, 523), (480, 522), (450, 521), (420, 521), (400, 520),
        (380, 519), (365, 517), (350, 513.5), (330, 510.5), (300, 509.5), (260, 508.5), (222, 508), (190, 508.5),
        (176, 510.5), (170, 514), (166, 520), (164.5, 540), (165, 565), (168, 578), (172, 587), (180, 595.5),
        (199, 600.5), (223, 603.5), (251, 606.5), (300, 609.5), (330, 609), (340, 607.5), (350, 604), (360, 601),
        (370, 600), (400, 601.5), (450, 605.5), (500, 608.5), (560, 611.5), (600, 612), (700, 612)]
LAMP_OUT, LAMP_IN = (222, 552), (317.5, 554)   # px: lamp centres (photo x; y set so the full rings fit the band)
GRILLE_X0 = 362                        # px: grille mesh starts right of the inner lamp
LOWER = [(314, 717), (340, 719.5), (360, 721.5), (380, 723.5), (400, 725.5), (450, 729.5), (500, 733.5), (540, 735.5),
         (580, 737.5), (700, 737.5), (700, 797), (580, 796.5), (540, 793.5), (500, 791.5), (450, 786.5), (400, 780.5),
         (380, 777.5), (371.5, 776), (359.5, 772), (351.5, 768), (345.5, 764), (341.5, 760), (334.5, 752),
         (329.5, 744), (324.5, 736), (320.5, 728), (316.5, 720)]   # lower grille, edges measured on the photo

# ------------------------------------------------------------------------------------------------ Hellcat badge
# The grille carries "SRT" + the Hellcat head on the viewer's right (photo x 810-897). The letters are far below the
# 0.5 mm limit at keychain scale, so only the head is kept, enlarged to HEAD_H: one white silhouette facing right like
# the real chrome badge (cand/c08.jpg close-up) - swept-back ear + the second point on the skull, round forehead,
# snout, open snarling mouth with the upper fang, lower jaw - with a black slanted eye and the black cheek line that
# separates the jaw/cheek swoosh. Badge units: x right, y DOWN (~9.4 units tall), scaled to HEAD_H mm.
SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):   # badge-free export, no edit
    SHOW_BADGE = False
HEAD_H = 5.5                                   # mm, badge height
HEAD_C = (19.75, 25.26)                        # mm, badge centre (keychain frame; photo head ~ x 872-897 px);
                                               # x also puts the mesh end on whole bricks + a full rib
HEAD_MARGIN = 0.6                              # mm of plain black between the head and the grille mesh
HEAD_SIL = [(0.5, 0.6), (2.8, 1.9), (3.9, 1.8), (4.7, 1.1), (5.3, 1.9), (6.6, 2.4), (7.9, 3.3), (8.9, 4.4), (9.5, 5.5),
            (9.7, 6.4), (9.3, 6.9), (8.9, 7.0), (8.95, 8.3), (8.3, 7.35), (6.4, 6.8), (7.75, 8.6), (7.3, 9.15),
            (6.6, 9.6), (5.0, 9.9), (3.2, 10.0), (1.6, 9.6), (1.0, 8.0), (1.3, 6.0), (1.8, 4.2), (1.7, 2.8)]
HEAD_EYE = [(4.5, 3.85), (8.1, 4.8), (7.75, 5.85), (4.8, 4.95)]
HEAD_CHEEK = [(6.5, 7.0), (5.3, 7.5), (4.1, 8.3), (3.3, 9.4), (3.0, 10.6)]     # black line, HEAD_CHEEK_W
HEAD_CHEEK_W = 0.6


def hellcat_head():
    """-> (white head, black eye) in keychain mm"""
    k = HEAD_H / 9.4
    to_mm = lambda g: affinity.scale(g, k, -k, origin=(0, 0))
    sil = to_mm(Polygon(HEAD_SIL).buffer(0))
    cheek = LineString([(x * k, -y * k) for x, y in HEAD_CHEEK]).buffer(HEAD_CHEEK_W / 2)
    eye = to_mm(Polygon(HEAD_EYE).buffer(0))
    b = sil.bounds
    dx, dy = HEAD_C[0] - (b[0] + b[2]) / 2, HEAD_C[1] - (b[1] + b[3]) / 2
    white = geom.clean(affinity.translate(sil.difference(cheek), dx, dy))
    return white, geom.clean(affinity.translate(eye, dx, dy))


HEAD, HEAD_EYE_MM = hellcat_head() if SHOW_BADGE else (Polygon(), Polygon())
HEAD_ZONE = HEAD.buffer(HEAD_MARGIN) if SHOW_BADGE else Polygon()


# ------------------------------------------------------------------------------------------------ brick mesh relief
# The Challenger grilles are a staggered "brick" mesh of horizontal bars and short vertical links. Simplified to
# rows of 1.2-1.3 mm openings between 0.7 mm ribs (upper grille 4 rows, lower grille 3 rows); the rows follow the
# opening's top and bottom edges (so the first/last row meet the body-colour surround cleanly, like the G80 slats),
# vertical links staggered half a brick per row. Even rows put a link on the centreline, odd rows an opening ->
# mirror-symmetric lattice.
BR_RIB, BR_OPEN_W = 0.8, 3.2           # mm: rib width, opening width (brick length)
BR_MIN = 0.75                          # mm: a brick cut by the recess end must stay this wide to be kept
BR_MIN_AREA = 0.3                      # ... and keep this fraction of a whole brick
BR_OVER = 0.3                          # mm: outer rows overshoot the recess edge (clipped by it)


def edges_at(poly, x):
    """(bottom, top) y of a polygon on the vertical line at x (mm); x is clamped into the polygon's x range"""
    minx, _, maxx, _ = poly.bounds
    x = min(max(x, minx + 0.05), maxx - 0.05)
    seg = poly.intersection(LineString([(x, -50), (x, 100)]))
    b = seg.bounds
    return b[1], b[3]


def brick_holes(region, ybot, ytop, n_rows, x_phase=0.0, exclude=None, skipped=None):
    """Staggered brick openings (mm) in region; rows interpolate between ybot(x) and ytop(x) (mm). Bricks touching
    `exclude` are left out whole (appended to `skipped` if given)."""
    pitch = BR_OPEN_W + BR_RIB
    minx, _, maxx, _ = region.bounds
    holes = []
    for k in range(n_rows):
        off = (BR_RIB / 2 if k % 2 == 0 else -BR_OPEN_W / 2) + x_phase
        i0 = int(math.floor((minx - off) / pitch)) - 1
        i1 = int(math.ceil((maxx - off) / pitch)) + 1
        for i in range(i0, i1 + 1):
            x0 = off + i * pitch
            x1 = x0 + BR_OPEN_W
            xs = [x0, x1]                          # straight-edged bricks (near-collinear vertices trip GEOS)
            def y(x, frac):
                b, t = ybot(x), ytop(x)
                h = t - b
                oh = (h - (n_rows - 1) * BR_RIB) / n_rows
                return b + frac[0] * (oh + BR_RIB) + frac[1] * oh
            cell = Polygon([(x, y(x, (k, 0))) for x in xs] + [(x, y(x, (k, 1))) for x in reversed(xs)])
            if exclude is not None and not exclude.is_empty and cell.intersects(exclude):
                if skipped is not None:
                    skipped.append(cell)
                continue                                   # no cut bricks around the badge: whole bricks only
            # the outer rows run 0.3 mm past the recess edge so the edge itself bounds them (no hairline rib)
            lo = -BR_OVER if k == 0 else 0.0
            hi = BR_OVER if k == n_rows - 1 else 0.0
            ext = Polygon([(x, y(x, (k, 0)) + lo) for x in xs] + [(x, y(x, (k, 1)) + hi) for x in reversed(xs)])
            piece = ext.intersection(region)
            if piece.is_empty:
                continue
            if cell.intersection(region).area < 0.95 * cell.area:
                # brick cut by the recess wall: round opening removes the thin wedges along the curved wall
                r = BR_MIN / 2
                piece = piece.buffer(-r, join_style=1).buffer(r, join_style=1).intersection(piece)
            for q in geom.polys(piece):
                if q.area >= BR_MIN_AREA * cell.area:
                    holes.append(q)
    return shapely.set_precision(unary_union(holes), 0.001) if holes else Polygon()


# upper grille: the band right of GRILLE_X0 (mirrored); 4 rows between the band's top and bottom edges
BAND_MM = mirror_union(Polygon(mm(BAND)))
UPPER_REGION = geom.clean(BAND_MM.intersection(box((GRILLE_X0 - CX) * S, -10, -(GRILLE_X0 - CX) * S, 60)))
# the badge sits on plain black: the grille mesh stops (whole bricks, staggered end) HEAD_MARGIN before the head and
# the rest of that grille end, up to the lamp, is plain black like the badge plinth
BADGE_BOX = box(HEAD.bounds[0] - HEAD_MARGIN, -10, 40, 60) if SHOW_BADGE else Polygon()
_skip = []
UPPER_HOLES = brick_holes(UPPER_REGION, lambda x: edges_at(BAND_MM, x)[0], lambda x: edges_at(BAND_MM, x)[1], 4,
                          exclude=BADGE_BOX, skipped=_skip)
if SHOW_BADGE:
    _patch = unary_union([BADGE_BOX] + _skip)
    UPPER_REGION = geom.clean(UPPER_REGION.difference(_patch))
    # the skipped (un-overshot) bricks leave a ~0.02 mm sliver of recess along the band edge above the plinth:
    # a small morphological opening drops it (square joins keep the recess corners sharp)
    UPPER_REGION = geom.clean(UPPER_REGION.buffer(-0.12, join_style=2).buffer(0.12, join_style=2)
                              .intersection(UPPER_REGION))
    UPPER_HOLES = geom.clean(UPPER_HOLES.intersection(UPPER_REGION))

# lower grille: 3 rows between its top edge and its bottom edge; where the bottom edge sweeps up into the rounded
# outer end (x < LOWER_FLAT_X) the rows keep the height they have at LOWER_FLAT_X and the end cuts them
LOWER_REGION = mirror_union(Polygon(mm(LOWER)))
LOWER_FLAT_X = (420 - CX) * S


def _lower_bot(x):
    xa = -abs(x)
    if xa >= LOWER_FLAT_X:
        return edges_at(LOWER_REGION, x)[0]
    b0, t0 = edges_at(LOWER_REGION, LOWER_FLAT_X)
    return edges_at(LOWER_REGION, x)[1] - (t0 - b0)


LOWER_HOLES = brick_holes(LOWER_REGION, _lower_bot, lambda x: edges_at(LOWER_REGION, x)[1], 3)


def relief_prim(region, holes):
    ribs = geom.clean(region.difference(holes))
    for _ in range(2):
        ribs = geom.regularize(region, ribs, 0.64)
    return dict(kind='geom', color='relief', geom=plain(region), mirror=False,
                relief=dict(type='custom', ribs=plain(ribs)))


GROOVE_W = 0.55
prims = [
    # hood outline (engraved, traced pixel by pixel): front edge above the brow + the side shut lines, which run up
    # into the fender edge at the cowl on the car - the groove stops where the fender strip beside it drops to ~1 mm
    dict(kind='stroke', color='groove', width=GROOVE_W, smooth=1,
         pts=[(304, 339), (293.5, 350), (283, 360), (273, 370), (263, 380), (253, 390), (245, 400), (238, 410),
              (232, 420), (226.5, 430), (222, 440), (218.5, 449), (216, 457), (215, 462), (217, 465), (222, 465.2),
              (260, 465), (300, 464), (375, 463), (450, 462), (700, 462)]),
    # hood snorkel scoops (black; average of both scoops measured row by row)
    dict(kind='poly', color='black', smooth=1,
         pts=[(419, 403.5), (516, 403.5), (530, 406), (540, 410), (545.5, 415), (549, 420), (551.5, 425), (549.5, 430),
              (544, 435), (538, 436.5), (395, 436.5), (388.5, 435), (382, 430), (383.5, 425), (385, 420),
              (388.5, 415), (395.5, 410), (406, 406)]),
    # headlight + grille band
    dict(kind='poly', color='black', pts=BAND),
    # halo rings + projector lens rings
    dict(kind='ring', color='white', c=LAMP_OUT, r_mm=3.0, width=0.7),
    dict(kind='ring', color='white', c=LAMP_IN, r_mm=3.0, width=0.7),
    dict(kind='ring', color='white', c=LAMP_OUT, r_mm=1.6, width=0.55),
    dict(kind='ring', color='white', c=LAMP_IN, r_mm=1.6, width=0.55),
    # fog / brake-duct pocket
    dict(kind='poly', color='black', smooth=1,
         pts=[(222, 711), (291, 713), (298, 740), (296, 760), (288, 766), (250, 765), (236, 756), (226, 735)]),
    # lower grille
    dict(kind='poly', color='black', pts=LOWER),
    # splitter + its dark end plates rising up the bumper corners (outside the white lower-lip loop, measured)
    dict(kind='poly', color='black',
         pts=[(140, 688), (152, 688), (170, 692), (173.5, 696), (175.5, 702), (178.5, 708), (180.5, 714), (183.5, 720),
              (186.5, 726), (190.5, 732), (193.5, 738), (197, 744), (200.5, 750), (204.5, 756), (209.5, 762),
              (214.5, 768), (218.5, 774), (223.5, 780), (231, 787), (240, 792.5), (250, 796.5), (260, 799.5),
              (280, 803.5), (300, 807.5), (320, 809.5), (350, 812.5), (380, 816.5), (400, 818.5), (450, 824.5),
              (500, 829.5), (550, 833.5), (600, 836.5), (640, 837.5), (700, 837.5), (700, 890), (140, 890)]),
]
prims += [relief_prim(UPPER_REGION, UPPER_HOLES), relief_prim(LOWER_REGION, LOWER_HOLES)]
if SHOW_BADGE:
    prims += [dict(kind='geom', color='white', geom=plain(HEAD), mirror=False),
              dict(kind='geom', color='groove', geom=plain(HEAD_EYE_MM), mirror=False)]

SPEC = dict(
    id='challenger_hellcat', name='Dodge Challenger SRT Hellcat',
    ref='kc/cars/challenger_hellcat/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.45),
)
