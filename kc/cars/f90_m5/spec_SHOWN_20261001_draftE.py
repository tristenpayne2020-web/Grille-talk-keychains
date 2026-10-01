# BMW M5 Competition (F90 LCI, 2021+) front keychain - traced from a real photo.
# Reference: BMW Group PressClub photo P90390715 "The new BMW M5 Competition (06/2020)", studio, straight front:
#   https://www.press.bmwgroup.com/global/photo/detail/P90390715/
#   (BMW AG press image, (c) BMW AG, free for editorial use; used only as a tracing reference).
# ref/front.jpg = crop (650,430)-(2020,1130) of the 2249x1500 press file, brightened (gamma 0.6). The photo is level
# and symmetric about x=686 (checked with trace_tools mirror). Viewer's-left half traced, mirrored.
# Hood creases cross-checked on P90391321 (same car, daylight, straight front).
# NO LOGOS (user rule): the roundel on the hood nose is not drawn (plain body), badge=None.
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity

PX_L, PX_R, PX_B, CX = 60, 1312, 616, 686
S = 80.5 / (PX_R - PX_L)                          # mm per photo pixel


def mm_x(x):
    return (x - CX) * S


def mm_pt(p):
    return ((p[0] - CX) * S, (PX_B - p[1]) * S)


def full_poly(half_px):
    g = Polygon([mm_pt(p) for p in half_px]).buffer(0)
    return unary_union([g, Polygon([(-x, y) for x, y in g.exterior.coords])]).buffer(0)


# ------------------------------------------------------------------------------------------------ shapes (px)
# lens inner edge pulled to x=345 so a ~1.2 mm white web stays between lamp and kidney
HEADLIGHT = [(127, 190), (165, 186), (202, 190), (265, 199), (320, 208), (338, 212), (345, 220), (345, 285),
             (322, 288), (215, 287), (165, 286), (128, 280), (110, 272), (102, 256), (102, 226), (110, 203)]

# left kidney incl. its gloss-black frame; inner edge 8 px (0.5 mm) off the centreline -> ~1.0 mm white centre bar
KIDNEY = [(678, 228), (671, 214), (657, 207), (620, 203), (540, 202), (450, 203), (405, 207), (384, 214),
          (370, 228), (364, 250), (364, 272), (368, 292), (380, 315), (397, 336), (417, 347), (450, 351),
          (550, 352), (640, 351), (664, 346), (675, 338), (678, 325)]

SIDE_INTAKE = [(126, 376), (160, 373), (250, 384), (300, 397), (322, 410), (340, 428), (352, 450), (340, 458),
               (322, 471), (310, 492), (300, 515), (290, 530), (272, 537), (200, 535), (160, 531), (132, 526),
               (124, 515), (124, 400)]
# the gloss-black lower fin inside each side intake (horizontal blade + its diagonal leg), drawn as one relief rib
SIDE_FIN = [(296, 489), (196, 484), (166, 518)]

CENTRE_INTAKE = [(690, 455), (400, 455), (382, 459), (373, 478), (370, 530), (377, 551), (394, 565), (430, 572),
                 (690, 576)]
# radar housing runs down through the intake bottom so no half-cells are left under it
RADAR = [(690, 450), (632, 450), (622, 470), (620, 490), (620, 540), (623, 566), (630, 584), (690, 584)]

LIP = [(690, 592), (400, 589), (250, 586), (150, 582), (110, 579), (92, 586), (90, 640), (690, 640)]


def _mirror(g):
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))]).buffer(0)


def kidney_slats(centres_px, rib=0.82, kink_px=262, dx_px=19, inset=0.55):
    """F90 LCI Competition kidney: 6 vertical slats per side whose tops kink up and outboard into the frame
    (the 'shark-tooth' row of angled slat tops seen in the photo). Single ribs (the real slats are thin pairs that
    merge at keychain scale). Keychain mm, both kidneys (mirrored)."""
    inner = Polygon([mm_pt(p) for p in KIDNEY]).buffer(-inset)
    ribs = []
    for c in centres_px:
        x = mm_x(c)
        yk = (PX_B - kink_px) * S
        rise = (PX_B - 190) * S - yk
        ln = LineString([(x, -2.0), (x, yk), (x - dx_px * S * rise / ((262 - 212) * S), yk + rise)])
        ribs.append(ln.buffer(rib / 2, cap_style=2, join_style=2, mitre_limit=3))
    return _mirror(unary_union(ribs).intersection(inner))


def honeycomb(a=2.1, b=1.15, h=0.95, rib=0.75, y0=0.0):
    """M-style horizontally stretched honeycomb (pointy left/right cells), symmetric about x=0, keychain mm."""
    cells = []
    step_x = a + b
    for i in range(-30, 31):
        x = i * step_x
        for j in range(-5, 40):
            y = y0 + j * 2 * h + (h if i % 2 else 0)
            hexa = Polygon([(x + a, y), (x + b, y + h), (x - b, y + h), (x - a, y), (x - b, y - h), (x + b, y - h)])
            cells.append(hexa.buffer(-rib / 2, join_style=2))
    return box(-60, -5, 60, 60).difference(unary_union(cells))


def opened(g, r=0.3):
    return g.buffer(-r, join_style=2).buffer(r, join_style=2)


SLATS = kidney_slats([408, 453, 500, 545, 590, 635])     # 6 slats per kidney, as on the car
RADAR_G = full_poly(RADAR).buffer(-0.8, join_style=1).buffer(0.8, join_style=1)
CENTRE_MESH = full_poly(CENTRE_INTAKE).buffer(-0.6, join_style=1).difference(RADAR_G.buffer(0.8))
_ribs = opened(honeycomb(y0=(PX_B - 515) * S).intersection(CENTRE_MESH))
_ribs = _ribs.intersection(affinity.scale(_ribs, -1, 1, origin=(0, 0)))          # exactly symmetric
_gaps = CENTRE_MESH.difference(_ribs).buffer(-0.3).buffer(0.3)
_gaps = unary_union([q for q in getattr(_gaps, 'geoms', [_gaps]) if q.area > 0.5])
HONEY = CENTRE_MESH.buffer(0.5).difference(_gaps)                                  # no rib or cell opening under 0.6 mm
FIN = _mirror(LineString([mm_pt(p) for p in SIDE_FIN]).buffer(0.36, cap_style=2, join_style=2))
SIDE_G = full_poly(SIDE_INTAKE)

SPEC = dict(
    id='f90_m5', name='BMW M5 Competition (F90 LCI)',
    ref='kc/cars/f90_m5/ref/front.jpg',
    units='px', px_left=PX_L, px_right=PX_R, px_bottom=PX_B, center_x=CX,
    outline_half=[(686, 54), (520, 54), (380, 56), (260, 60), (222, 64), (205, 72), (185, 90), (165, 110),
                  (150, 128), (130, 150), (105, 170), (85, 188), (70, 205), (63, 225), (61, 260), (60, 330),
                  (60, 420), (62, 470), (66, 520), (73, 555), (84, 585), (97, 603), (130, 612), (400, 615),
                  (686, 616)],
    prims=[
        # LCI laser headlight (whole lens black), the two L-shaped DRL light guides and the upper 'laser' light bar
        # over each module (white strokes)
        dict(kind='poly', color='black', pts=HEADLIGHT),
        dict(kind='stroke', color='white', width=0.7, pts=[(120, 214), (123, 240), (131, 256), (148, 264), (205, 270)]),
        dict(kind='stroke', color='white', width=0.7, pts=[(209, 222), (214, 245), (224, 260), (240, 267), (326, 272)]),
        dict(kind='stroke', color='white', width=0.65, pts=[(142, 209), (190, 216)]),
        dict(kind='stroke', color='white', width=0.65, pts=[(232, 216), (328, 232)]),
        # twin kidneys: black frame + 6 kinked vertical slats each (relief)
        dict(kind='poly', color='black', pts=KIDNEY, relief=dict(type='custom', ribs=SLATS)),
        # side intakes: black with the lower fin as a relief rib
        dict(kind='poly', color='black', pts=SIDE_INTAKE),
        dict(kind='geom', color='relief', geom=SIDE_G, relief=dict(type='custom', ribs=FIN), mirror=False),
        # centre intake: honeycomb mesh around the flush-black radar housing
        dict(kind='poly', color='black', pts=CENTRE_INTAKE),
        dict(kind='geom', color='relief', geom=CENTRE_MESH, relief=dict(type='custom', ribs=HONEY), mirror=False),
        # black lower lip
        dict(kind='poly', color='black', pts=LIP),
        # grooves: fender/hood shut line (to the headlight), hood power-dome creases converging on the hood nose
        dict(kind='stroke', color='groove', width=0.65, pts=[(213, 90), (197, 104), (183, 122), (172, 145), (168, 165),
                                                             (168, 184)], smooth=1),
        dict(kind='stroke', color='groove', width=0.65, pts=[(520, 70), (552, 100), (578, 128), (594, 154)], smooth=2),
        # parking sensor (one per side) + ONE tow-hook cover (viewer's left only - user's BMW rule)
        dict(kind='ring', color='black', c=(463, 430), r_mm=0.9, width=0.5),
        dict(kind='ring', color='black', c=(388, 396), r_mm=1.25, width=0.5, mirror=False),
    ],
    badge=None,
    tab=dict(y_frac=0.50),
)
