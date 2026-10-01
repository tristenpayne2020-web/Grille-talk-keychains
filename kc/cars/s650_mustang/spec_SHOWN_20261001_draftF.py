# Ford Mustang GT (S650, 2024+) front keychain - revision 7 (clean rewrite, NO LOGOS).
# Traced on ref/front.jpg = straight-on, level, headlight-height photo of a Race Red 2024 Mustang GT (Car and Driver,
# https://hips.hearstapps.com/hmg-prod/images/2024-ford-mustang-gt-155-64b982586091f.jpg - editorial photo, used only
# as a private tracing reference). Coordinates are ORIGINAL photo pixels; the viewer's LEFT half is traced and the
# pipeline mirrors it about the centreline x = CX.  1 mm on the keychain = 14.34 px.
#
# r7 vs r6 (critic fixes):
#   * no running pony / no badge at all (user rule: no logos) - the centre of the grille is plain honeycomb
#   * honeycomb = the product line's library 'hex' relief (pitch 2.4, rib 0.8) instead of the custom elongated mesh
#   * gloss-black fang blades = flat (unrecessed) black planks between the honeycomb centre and the outer nostrils,
#     with a J foot turning outward under the nostril; the nostrils get horizontal louvres so the blade separates two
#     visibly different textures
#   * tri-bar DRL = three vertical white bars per headlamp, one in each lamp module
# r8 vs r7 (critic fixes):
#   * fang blades = solid face-level planks (3.0 -> 2.4 mm) inside their own recessed strip with a 0.8 mm recessed gap
#     on both sides, so the blade reads as a separate bar; nostrils are honeycomb like the centre (phase-aligned:
#     same pocket top/bottom -> same lattice origin)
#   * gloss band under the honeycomb ~3.4 mm with crisper lower corners; DRL bars 1.15 mm, nudged to the module's
#     outer edge; lamp tip moved in (>= 1.8 mm white wall at the tab); shut-line groove starts inside the body;
#     grooves 0.65 mm; corner intake = flat black upper-outer wedge + honeycomb lower-inner; plain plate mount in
#     the lower grille centre
CX = 1108
PX_BOTTOM = 1072
PXMM = (1685 - 531) / 80.5          # px per mm


def mm(v):
    return v * PXMM


def _blade(top, foot, w_top, w_foot):
    """tapered straight plank (px polygon) from top to foot, widths in mm"""
    (x0, y0), (x1, y1) = top, foot
    a, b = mm(w_top) / 2, mm(w_foot) / 2
    return [(x0 - a, y0), (x0 + a, y0), (x1 + b, y1), (x1 - b, y1)]


# ---- upper grille opening (black)
GRILLE = [(CX, 737), (790, 737), (782, 741), (760, 777), (741, 815), (729, 848), (729, 862), (737, 873), (768, 894),
          (805, 910), (845, 916), (CX, 916)]
MESH_TOP = 746                      # top of the honeycomb pocket (0.65 mm gloss frame under the grille top edge)
MESH_BOT = 868                      # honeycomb bottom = top of the smooth gloss band (~3.4 mm band)
# fang blade (left), photo: top (879,737) -> foot (855,868), slanting outward-down
FANG_TOP, FANG_FOOT = (879, MESH_TOP), (855, MESH_BOT)
FANG_W = (3.0, 2.4)                 # mm, top -> foot
GAP = 0.8                           # mm recessed gap on each side of the blade
_fx = lambda y: FANG_TOP[0] + (FANG_FOOT[0] - FANG_TOP[0]) * (y - FANG_TOP[1]) / (FANG_FOOT[1] - FANG_TOP[1])
_hw = lambda y: mm(FANG_W[0] + (FANG_W[1] - FANG_W[0]) * (y - FANG_TOP[1]) / (FANG_FOOT[1] - FANG_TOP[1])) / 2
_e = lambda y, s, g: _fx(y) + s * (_hw(y) + mm(g))     # fang edge (s=+1 inner/centre side, -1 outer), plus gap g

# centre honeycomb pocket (right of the left fang strip; mirrored -> one symmetric pocket across the centre)
CENTRE = [(_e(MESH_TOP, 1, GAP), MESH_TOP), (CX, MESH_TOP), (CX, MESH_BOT), (_e(MESH_BOT, 1, GAP), MESH_BOT)]
# outer nostril pocket: inside the slanted grille side (~0.75 mm frame), left of the fang strip. Same top/bottom as
# CENTRE so the library hex lattice (origin = pocket bounds centre) lines up across the blade.
NOSTRIL = [(_e(MESH_TOP, -1, GAP), MESH_TOP), (_e(MESH_BOT, -1, GAP), MESH_BOT), (741, MESH_BOT), (741, 848),
           (751, 815), (770, 777), (786, MESH_TOP)]
# fang strip = gap + blade + gap (recessed); the blade itself is a face-level 'rib' (custom relief)
FANG_STRIP = [(_e(MESH_TOP, -1, GAP), MESH_TOP), (_e(MESH_TOP, 1, GAP), MESH_TOP), (_e(MESH_BOT, 1, GAP), MESH_BOT),
              (_e(MESH_BOT, -1, GAP), MESH_BOT)]
FANG = [(_e(MESH_TOP, -1, 0), MESH_TOP), (_e(MESH_TOP, 1, 0), MESH_TOP), (_e(MESH_BOT, 1, 0), MESH_BOT),
        (_e(MESH_BOT, -1, 0), MESH_BOT)]


S = 80.5 / (1685 - 531)              # mm per px (pipeline frame: x = (px - CX) * S, y = (PX_BOTTOM - py) * S)


def _mm_poly(pts, flip=False):
    from shapely.geometry import Polygon
    k = -1 if flip else 1
    return Polygon([(k * (x - CX) * S, (PX_BOTTOM - y) * S) for x, y in pts])


def _upper_ribs():
    """Custom relief ribs (mm) for the whole upper-grille pocket: ONE honeycomb lattice (pitch 2.4, rib 0.8 = the
    line's library 'hex' cell) centred on the car centreline, clipped to the centre pocket and both nostrils, plus the
    two solid fang blades. Built per polygon and mirrored here (the library regulariser drops one half of a mirrored
    MultiPolygon nostril pair on this geometry)."""
    import math
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    from geom import regularize
    pitch, rib = 2.4, 0.8
    a = pitch / math.sqrt(3)
    cy = (PX_BOTTOM - (MESH_TOP + MESH_BOT) / 2) * S
    cells = []
    for i in range(-24, 25):
        for j in range(-8, 9):
            x, y = i * 1.5 * a, cy + j * pitch + (pitch / 2 if i % 2 else 0)
            cells.append(Polygon([(x + a * math.cos(math.radians(60 * k)), y + a * math.sin(math.radians(60 * k)))
                                  for k in range(6)]).buffer(-rib / 2, join_style=2))
    lattice = box(-50, cy - 20, 50, cy + 20).difference(unary_union(cells))
    out = []
    centre = _mm_poly(CENTRE).union(_mm_poly(CENTRE, True))
    out.append(regularize(centre, lattice.intersection(centre), 0.64))
    for flip in (False, True):
        n = _mm_poly(NOSTRIL, flip)
        out.append(regularize(n, lattice.intersection(n), 0.64))
        out.append(_mm_poly(FANG, flip))
    return unary_union(out)


# ---- headlamp + tri-bar DRL
LAMP = [(562, 717), (600, 717), (690, 720), (745, 734), (752, 740), (738, 768), (724, 791), (650, 784),
        (580, 777), (566, 770), (565, 750)]
DRL_W = 1.15                        # mm bar width
DRL_X = [586, 645, 703]             # bars sit on the outer side of each lamp module (photo)
DRL_CLEAR = 0.7                     # mm of black kept between a bar end and the lamp edge


def _vbar(x, w=DRL_W):
    """vertical bar through the whole module height, clipped DRL_CLEAR inside the lamp outline"""
    from shapely.geometry import Polygon, box
    h = mm(w) / 2
    g = box(x - h, 600, x + h, 900).intersection(Polygon(LAMP).buffer(-mm(DRL_CLEAR), join_style=2))
    return [(round(a, 2), round(b, 2)) for a, b in list(g.exterior.coords)[:-1]]


# ---- corner intake: flat black opening, honeycomb only in its lower-inner part (upper-outer wedge stays plain)
INTAKE = [(570, 868), (582, 858), (622, 860), (700, 928), (750, 950), (700, 996), (688, 1004), (592, 1004),
          (578, 997), (570, 980)]
INTAKE_HEX = [(598, 924), (690, 924), (712, 936), (750, 950), (700, 996), (688, 1004), (598, 1004)]
# ---- lower grille: honeycomb either side of a plain plate-mount panel in the centre
LOWER = [(CX, 948), (832, 948), (826, 953), (788.5, 1022), (792, 1026), (CX, 1026)]
PLATE_X = 1052                      # plate panel = x 1052..1164 (7.8 mm wide), full lower-grille height
LOWER_HEX = [(PLATE_X - 8, 948), (832, 948), (826, 953), (788.5, 1022), (792, 1026), (PLATE_X - 8, 1026)]

HEX = dict(type='hex', pitch=2.4, rib=0.8)

SPEC = dict(
    id='s650_mustang', name='Ford Mustang GT (S650)',
    ref='ref/front.jpg',
    units='px', px_left=531, px_right=1685, px_bottom=PX_BOTTOM, center_x=CX,
    # body outline: cowl/hood rear edge -> raised power dome stepping down to the fender tops -> fender shoulder ->
    # flat fender side -> splitter end -> splitter bottom
    outline_half=[(CX, 564), (1000, 565), (885, 566), (866, 569), (850, 580.5), (836, 579), (790, 577.5), (730, 577),
                  (690, 578), (650, 582), (615, 590), (598, 598),
                  (578, 612), (560, 633), (546, 660), (537, 695), (532, 740), (531, 800), (531, 1000),
                  (533, 1034), (538, 1052), (560, 1060), (700, 1065), (860, 1070), (CX, 1072)],
    prims=[
        # ---- headlamp (black) + tri-bar DRL: three vertical white bars, one per lamp module
        dict(kind='poly', color='black', pts=LAMP),
        *[dict(kind='poly', color='white', pts=_vbar(x)) for x in DRL_X],
        # ---- upper grille: black; honeycomb centre + nostrils, split by the gloss fang blades; smooth band below
        dict(kind='poly', color='black', pts=GRILLE),
        *[dict(kind='poly', color='relief', pts=p, relief=dict(type='custom', ribs=_upper_ribs()))
          for p in (CENTRE, NOSTRIL, FANG_STRIP)],
        # ---- hood vent (power-dome opening)
        dict(kind='poly', color='black', pts=[(912, 602), (918, 599), (960, 598), (1040, 596), (CX, 595), (CX, 629.5),
                                               (945, 630), (934, 628)]),
        # ---- corner intake (plain wedge + honeycomb) and lower grille (honeycomb + plain plate panel)
        dict(kind='poly', color='black', pts=INTAKE),
        dict(kind='poly', color='relief', pts=INTAKE_HEX, relief=HEX),
        dict(kind='poly', color='black', pts=LOWER),
        dict(kind='poly', color='relief', pts=LOWER_HEX, relief=HEX),
        # ---- splitter lip
        dict(kind='poly', color='black', pts=[(CX, 1041), (800, 1041), (650, 1041), (560, 1041), (545, 1038),
                                               (520, 1036), (520, 1090), (CX, 1090)]),
        # ---- engraved body lines (0.65 mm): hood leading edge, hood/fender shut line, intake crease
        dict(kind='stroke', color='groove', width=0.65, pts=[(CX, 697), (900, 697), (780, 700), (742, 706)]),
        dict(kind='stroke', color='groove', width=0.65, pts=[(603, 613), (604, 640), (607, 680), (605, 716)]),
        dict(kind='stroke', color='groove', width=0.65, pts=[(665, 836), (620, 832), (588, 836), (582, 846)]),
    ],
    badge=None,
    tab=dict(y_mm=18.8),
)
