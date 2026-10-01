# Bugatti Chiron (2016-2022) front keychain.
# Reference: ref/front.jpg = Wikimedia Commons "File:2018 Bugatti Chiron 3.jpg" (Calreyn88, CC BY-SA 4.0), 1920 px
# rendition, levelled by -0.65 deg (trace_tools rotate) from ref/front_raw.jpg. See ref/SOURCE.txt.
# Traced half = viewer's LEFT. Coordinates are photo pixels of ref/front.jpg (1 mm = 21.7 px). Camera ~ headlamp
# height, straight on; generation checked: 2016-2022 Chiron (quad-LED lamps, chrome horseshoe with the sill knob,
# silver blades under hex-mesh side intakes, carbon splitter). Body 80.5 x 31.8 mm (y_scale 1.0).
#
# Design (G80 language):
#  white  = body paint + the silver blades under the side intakes + the horseshoe's chrome frame and sill (with the
#           centre knob) + the EB oval.
#  black  = headlamp lenses (rounded outer end, pointed inner tail), the horseshoe (a 0.55 mm shadow line outside the
#           white chrome frame, then the recessed mesh), the side intakes, the full-width carbon splitter, parking
#           sensor rings (2 per side), the EB monogram.
#  light signature (white on black) = the Chiron's quad LED: four rounded-square rings per lamp (0.64 mm walls,
#           0.55 mm apart) turned with the lens mid-line.
#  relief = the Chiron's elongated-hex mesh (flat-top hexagons stretched 1.45x in x, 0.7 mm ribs): grille pitch 1.8 mm,
#           side intakes 1.7 mm with the rows turned -5.5 deg to follow the intake slope.
#  grooves (0.55 mm) = the two hood shut lines (A-pillar base -> horseshoe) and the central spine up the hood.
# Badge: Bugatti oval with a printable 'EB' monogram (SHOW_BADGE below, or env KC_BADGE=0 for a badge-free export).
import os, sys, math
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom as _geom                       # read-only use: chaikin / regularize

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):
    SHOW_BADGE = False

CX, XL, YB = 945, 70, 983                  # centreline, body left edge, splitter bottom (px)
S = 80.5 / (2 * (CX - XL))                 # mm per px


def mm(p):
    return ((p[0] - CX) * S, (YB - p[1]) * S)


def mpoly(pts, smooth=0):
    q = [mm(p) for p in pts]
    if smooth:
        q = _geom.chaikin(q, smooth, closed=True)
    return Polygon(q).buffer(0)


def half_sym(pts, smooth=0):
    """left-half px trace starting and ending on the centreline -> symmetric polygon (mm)"""
    h = [mm(p) for p in pts]
    if smooth:
        h = _geom.chaikin(h, smooth, closed=False)
    h = [(min(x, 0.0), y) for x, y in h]
    h[0] = (0.0, h[0][1]); h[-1] = (0.0, h[-1][1])
    return Polygon(h + [(-x, y) for x, y in reversed(h)]).buffer(0)


def both(g):
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])


plain = lambda g: shapely.from_wkb(shapely.to_wkb(shapely.set_precision(g.buffer(0), 0.001)))

# ---------------------------------------------------------------------------------------------- outline
OUTLINE = [(945, 287), (700, 288), (480, 291), (330, 294), (250, 297), (205, 307), (165, 327), (135, 352),
           (112, 382), (96, 415), (85, 450), (78, 490), (73, 540), (70, 590), (70, 640), (72, 690), (76, 730),
           (80, 765), (84, 785), (87, 820), (90, 860), (96, 888), (108, 906), (130, 917), (200, 931), (300, 942),
           (400, 951), (500, 958), (600, 965), (700, 971), (800, 976), (945, 983)]

# ---------------------------------------------------------------------------------------------- headlamp
# black lens: rounded outer end, straight brow, the lower edge sweeping up into a pointed inner tail (the dark inlet
# beside the lamp; the tail tip follows the brow crease like the lit Geneva / high Basel photos)
LAMP = [(141, 463), (146, 445), (160, 434), (185, 429), (250, 431), (300, 436), (350, 442), (400, 447),
        (450, 452), (500, 456), (545, 461), (585, 466), (606, 470), (585, 484), (560, 505), (535, 523), (500, 532),
        (450, 531), (400, 528), (350, 524), (300, 519), (250, 514), (200, 509), (170, 502), (150, 490)]
# four LED units: equal rounded-square rings on a 3.25 mm pitch, each centred on the lens mid-line and turned with it
U_X1, U_N = -34.0, 4                        # mm: centre x of the outermost unit, number of units
U_W, U_H, U_R, U_T, U_GAP = 2.7, 2.4, 0.7, 0.64, 0.55  # mm: ring width / height / corner r / wall / gap (photo: units
                                                       # x 160-448 px, ours 177-447 px; >= 0.54 mm black all round)


def lamp_rings():
    lamp = mpoly(LAMP, smooth=1)

    def mid(x):
        b = LineString([(x, -10), (x, 60)]).intersection(lamp).bounds
        return (b[1] + b[3]) / 2
    out = []
    for i in range(U_N):
        x = U_X1 + i * (U_W + U_GAP)
        y = mid(x)
        ang = math.degrees(math.atan2(mid(x + 0.5) - mid(x - 0.5), 1.0))
        r = box(x - U_W / 2 + U_R, y - U_H / 2 + U_R, x + U_W / 2 - U_R, y + U_H / 2 - U_R).buffer(U_R, 32)
        r = affinity.rotate(r, ang, origin=(x, y))
        out.append(r)
    rings = unary_union([r.difference(r.buffer(-U_T, 32)) for r in out])
    windows = unary_union([r.buffer(-U_T, 32) for r in out])
    return rings, windows

# ---------------------------------------------------------------------------------------------- horseshoe grille
HS_OUT = [(945, 497), (901, 500), (845, 514), (817, 529), (798, 544), (784, 559), (773, 574), (764, 589),
          (757, 604), (751, 619), (747, 634), (744, 649), (742, 664), (741, 680), (741, 710), (742, 725),
          (743, 740), (745, 755), (747, 770), (750, 785), (754, 800), (757, 815), (762, 830), (766, 845),
          (771, 860), (777, 875), (784, 891), (793, 907), (806, 922), (826, 931), (860, 935), (945, 936)]
LINE_W, FRAME_W = 0.55, 0.72              # mm: black shadow line outside the chrome frame, frame width
SILL_TOP = 900                            # px: top of the frame's bottom sill (mesh bottom)
KNOB = [(945, 881), (935, 884), (929, 892), (924, 901), (945, 901)]   # centre bump on the sill (half)


def horseshoe():
    outer = half_sym(HS_OUT)
    frame_out = outer.buffer(-LINE_W, join_style=1)
    mesh = frame_out.buffer(-FRAME_W, join_style=1)
    sill_y = (YB - SILL_TOP) * S
    mesh = mesh.difference(box(-30, -5, 30, sill_y))
    knob = half_sym(KNOB, smooth=2)
    mesh = mesh.difference(knob)
    return outer, frame_out, mesh


# ---------------------------------------------------------------------------------------------- mesh lattice
HEX_H, HEX_K, HEX_RIB = 1.8, 1.45, 0.7   # mm: cell pitch (across flats, centre-to-centre), x-stretch, rib
INTAKE_HEX_H = 1.7                        # mm: finer pitch in the 4.4 mm tall side intakes (3 clean rows)
GRILLE_PHASE_Y = 0.6                      # mm: row phase of the grille mesh (whole cells along the sill and the sides)


def lattice(region, H=HEX_H, ang=0.0, origin=(0.0, 0.0), phase=(0.0, 0.0), rim=0.0):
    """elongated flat-top hex mesh (holes) -> ribs = region - holes (+ optional rim rib along the region wall).
    Lattice columns sit at origin.x + phase.x + i*dx; with origin/phase x = 0 and ang = 0 the mesh is
    mirror-symmetric about the centreline. ang turns the lattice (deg) about origin to follow a sloped opening."""
    a = H / math.sqrt(3)
    ox, oy = origin
    r0 = affinity.rotate(region, -ang, origin=origin) if ang else region
    minx, miny, maxx, maxy = r0.bounds
    dx, dy = 1.5 * a * HEX_K, H
    cells = []
    for i in range(int((minx - ox) / dx) - 3, int((maxx - ox) / dx) + 4):
        for j in range(int((miny - oy) / dy) - 3, int((maxy - oy) / dy) + 4):
            x = ox + phase[0] + i * dx
            y = oy + phase[1] + j * dy + (dy / 2 if i % 2 else 0)
            hexa = Polygon([(x + a * HEX_K * math.cos(math.radians(60 * k)), y + a * math.sin(math.radians(60 * k)))
                            for k in range(6)])
            cells.append(hexa.buffer(-HEX_RIB / 2, join_style=2))
    holes = unary_union(cells)
    if ang:
        holes = affinity.rotate(holes, ang, origin=origin)
    ribs = region.difference(holes)
    if rim:
        ribs = unary_union([ribs, region.difference(region.buffer(-rim, join_style=1))])
    return _geom.regularize(region, ribs.intersection(region), 0.64)


# ---------------------------------------------------------------------------------------------- side intake + splitter
INTAKE = [(118, 776), (108, 748), (112, 714), (128, 693), (160, 682), (210, 678), (300, 689), (400, 699),
          (500, 710), (560, 716), (600, 724), (624, 736), (636, 755), (637, 785), (630, 806), (612, 818),
          (580, 820), (500, 813), (400, 802), (300, 790), (200, 777), (145, 777)]
SPLITTER = [(60, 790), (88, 796), (120, 806), (200, 821), (300, 837), (400, 849), (500, 860), (600, 871),
            (700, 879), (762, 886), (800, 890), (945, 890), (945, 1020),
            (60, 1020)]

# ---------------------------------------------------------------------------------------------- badge (EB macaron)
# real macaron: 4.9 x 2.3 mm at (945, 613) px; the smallest printable EB (5 strokes of 0.52 mm = 2.6 mm tall letters,
# >= 0.55 mm white all round) needs a 6.7 x 4.1 mm oval, centred on the real one
BADGE_C = (945, 613)
BADGE_A, BADGE_B = 3.35, 2.05             # mm: oval semi-axes (6.7 x 4.1: the smallest oval that holds a printable EB)
EB_W, EB_H = 0.52, 2.6                    # mm: stroke (= gap) and letter height of the monogram


def eb_glyph(w=EB_W, h=EB_H, earm=0.9, bw=1.2):
    """Bugatti 'EB' monogram in mm, centred at (0, 0): a reversed E and a B sharing one stem.
    Three E arms + two gaps = 5 strokes of w over the letter height; the B has two counters >= w."""
    hs, H = w / 2, h / 2
    stem = box(-hs, -H, hs, H)
    arms = [box(-hs - earm, H - w, 0, H), box(-hs - earm * 0.85, -w / 2, 0, w / 2), box(-hs - earm, -H, 0, -H + w)]

    def bowl(y0, y1, xr):
        r = (y1 - y0) / 2
        return unary_union([box(0, y0, xr - r, y1), Point(xr - r, (y0 + y1) / 2).buffer(r, 64)])
    b = unary_union([bowl(-w / 2, H, hs + bw * 0.95), bowl(-H, w / 2, hs + bw * 1.05)])
    b = b.difference(bowl(w / 2, H - w, hs + bw * 0.95 - w).difference(box(-5, -5, hs, 5)))
    b = b.difference(bowl(-H + w, -w / 2, hs + bw * 1.05 - w).difference(box(-5, -5, hs, 5)))
    g = unary_union([stem] + arms + [b])
    bb = g.bounds
    return affinity.translate(g, -(bb[0] + bb[2]) / 2, 0)


def badge():
    """-> (white oval, black EB) in keychain mm"""
    x, y = mm(BADGE_C)
    ov = affinity.scale(Point(0, 0).buffer(1.0, 128), BADGE_A, BADGE_B)
    return affinity.translate(ov, x, y), affinity.translate(eb_glyph(), x, y)


outer, frame_out, mesh = horseshoe()
intake = mpoly(INTAKE)
oval, glyph = badge()
mesh_ribs = lattice(mesh.difference(oval.buffer(0.6)) if SHOW_BADGE else mesh, phase=(0.0, GRILLE_PHASE_Y))
_ic = intake.centroid
# rows follow the intake slope; phase chosen so no rib or gap sliver < 0.6 mm is left at the rounded ends
intake_ribs = lattice(intake, H=INTAKE_HEX_H, ang=-5.5, origin=(_ic.x, _ic.y), phase=(0.6, 0.0))
rings, windows = lamp_rings()
# engraved lines (mm): stop GROOVE_TOP below the cowl edge (no notch in the silhouette), run into the horseshoe line
GROOVE_W, GROOVE_TOP = 0.55, 0.45
_top = half_sym(OUTLINE, smooth=1).buffer(-GROOVE_TOP)
hood_line = LineString([mm((392, 284)), mm((800, 528))]).buffer(GROOVE_W / 2, cap_style=2).intersection(_top)
hood_line = hood_line.difference(outer)
spine = LineString([mm((945, 280)), mm((945, 500))]).buffer(GROOVE_W / 2, cap_style=2).intersection(_top)
spine = spine.difference(outer)
# NOTE on 'groove' over black (lamp windows, EB letters): these black islands sit inside holes of other black areas;
# a groove prim on them keeps them black in both builds (production: unchanged; classic: 0.6 mm below the face,
# like a lens / an engraved monogram) and makes the preview renderer draw them (it paints grooves last).

prims = [
    dict(kind='poly', color='black', pts=LAMP, smooth=1),
    dict(kind='geom', color='white', geom=plain(rings)),
    dict(kind='geom', color='groove', geom=plain(windows)),
    dict(kind='poly', color='black', pts=SPLITTER),
    dict(kind='geom', color='black', geom=plain(intake), relief=dict(type='custom', ribs=plain(both(intake_ribs)))),
    dict(kind='geom', color='black', geom=plain(outer), mirror=False),
    dict(kind='geom', color='white', geom=plain(frame_out), mirror=False),
    dict(kind='geom', color='black', geom=plain(mesh), mirror=False,
         relief=dict(type='custom', ribs=plain(mesh_ribs))),
    # engraved lines: hood shut lines (hood / fender) + the central spine
    dict(kind='geom', color='groove', geom=plain(hood_line)),
    dict(kind='geom', color='groove', geom=plain(spine), mirror=False),
    # parking sensors
    dict(kind='ring', color='black', c=(170, 597), r_mm=0.9, width=0.5),
    dict(kind='ring', color='black', c=(690, 680), r_mm=0.9, width=0.5),
]
if SHOW_BADGE:
    prims += [dict(kind='geom', color='white', geom=plain(oval), mirror=False),
              dict(kind='geom', color='black', geom=plain(glyph), mirror=False),
              dict(kind='geom', color='groove', geom=plain(glyph), mirror=False)]

SPEC = dict(
    id='bugatti_chiron', name='Bugatti Chiron',
    ref='ref/front.jpg',
    units='px', px_left=XL, px_right=2 * CX - XL, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    outline_smooth=1,
    prims=prims,
    badge=None,
    tab=dict(y_frac=0.56),
)
