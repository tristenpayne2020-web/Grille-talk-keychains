# BMW M550i xDrive (G30 LCI, 2021-2023) front keychain - traced from a real photo.
# Reference: Wikimedia Commons "BMW G30 LCI M550i xDrive Mineral White Metallic (1).jpg" by Damian B Oh, CC BY-SA 4.0
#   https://commons.wikimedia.org/wiki/File:BMW_G30_LCI_M550i_xDrive_Mineral_White_Metallic_(1).jpg
# ref/front.jpg = crop (400,950)-(3480,2700) of the 3840x2880 Commons rendition, scaled 0.5 (1540x875).
# The photo is level and symmetric about x=765 (checked with trace_tools mirror). Viewer's-left half traced, mirrored.
# NO LOGOS (user rule): the roundel on the hood nose is not drawn (plain body), badge=None.
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity

PX_L, PX_R, PX_B, CX = 65, 1465, 822, 765
YS = 0.96                                        # y_scale: mild correction of the elevated camera
# The camera sits above the hood, so the hood above the headlights (y < HOOD_Y0) is foreshortened the wrong way
# (too much hood). Everything traced above HOOD_Y0 is compressed by HOOD_K towards HOOD_Y0 (outline top 78 -> 173 px),
# so the face gets the G80's ~2.3:1 body ratio with the headlights near the top edge.
HOOD_Y0, HOOD_K = 315, 0.6


def cy(p):
    x, y = p
    return (x, y if y >= HOOD_Y0 else HOOD_Y0 - (HOOD_Y0 - y) * HOOD_K)


def C(pts):
    return [cy(p) for p in pts]
S = 80.5 / (PX_R - PX_L)                          # mm per photo pixel


def mm_x(x):
    return (x - CX) * S


def mm_pt(p):
    return ((p[0] - CX) * S, (PX_B - p[1]) * S * YS)


def _mirror(g):
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))]).buffer(0)


def full_poly(half_px):
    return _mirror(Polygon([mm_pt(p) for p in half_px]).buffer(0))


def opened(g, r=0.3):
    return g.buffer(-r, join_style=2).buffer(r, join_style=2)


def honeycomb(a=2.3, b=1.4, h=1.15, rib=0.8, y0=0.0, x0=0.0):
    """M-Sport horizontally stretched honeycomb (pointy left/right cells), symmetric about x=0, keychain mm."""
    cells = []
    step_x = a + b
    for i in range(-30, 31):
        x = x0 + i * step_x
        for j in range(-5, 40):
            y = y0 + j * 2 * h + (h if i % 2 else 0)
            hexa = Polygon([(x + a, y), (x + b, y + h), (x - b, y + h), (x - a, y), (x - b, y - h), (x + b, y - h)])
            cells.append(hexa.buffer(-rib / 2, join_style=2))
    return box(-60, -5, 60, 60).difference(unary_union(cells))


def clean_mesh(region, ribs, min_gap=0.36, rim=0.7):
    """Honeycomb ribs for a recessed region: the openings stay >= rim mm inside the region wall (so no rib ever
    meets the wall in a needle wedge), symmetric, no rib (>= 0.64 mm) or opening (>= 0.72 mm) narrower than that."""
    def big(g):
        return unary_union([q for q in getattr(g, 'geoms', [g]) if q.area > 1.0])

    inner = region.buffer(-rim)
    g = inner.difference(opened(ribs.intersection(region)))
    for _ in range(3):                                          # alternate open(gaps) / open(ribs) until clean
        g = big(g.buffer(-min_gap).buffer(min_gap))
        g = inner.difference(region.difference(g).buffer(-0.33).buffer(0.33))
    g = big(g.buffer(-min_gap).buffer(min_gap)).intersection(box(-60, -5, 0, 60))
    g = unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])
    return region.buffer(0.5).difference(g)


def soft(g, r=0.4):
    return g.buffer(-r).buffer(r)


# ------------------------------------------------------------------------------------------------ shapes (px)
OUTLINE = C([(765, 78), (600, 81), (420, 87), (300, 92), (250, 95), (226, 102), (207, 114), (192, 128), (170, 160),
             (145, 205), (122, 250), (102, 290), (86, 330), (75, 370), (68, 420), (65, 480), (66, 560), (69, 640),
             (75, 700), (84, 750), (96, 785), (112, 806), (135, 815), (250, 819), (500, 821), (765, 822)])

# laser headlight: whole lens black, inner end pulled back to leave a white web next to the kidney frame
HEADLIGHT = [(122, 312), (160, 322), (200, 336), (260, 357), (320, 378), (366, 395), (368, 420), (364, 450),
             (364, 486), (300, 479), (245, 471), (200, 465), (140, 456), (112, 448), (97, 433), (90, 410),
             (89, 380), (92, 352), (100, 332), (110, 319)]

# LCI single-frame kidneys: outer edge of the frame, joined at the centreline (hood nose dips to y 420 at the top,
# body-colour V below the joint at y 563)
KIDNEY = [(765, 420), (748, 420), (738, 411), (720, 399), (690, 392), (600, 387), (500, 386), (440, 389), (405, 398),
          (388, 420), (381, 448), (379, 480), (383, 515), (393, 545), (410, 568), (435, 583), (470, 592),
          (550, 596), (650, 597), (720, 593), (742, 583), (755, 572), (765, 563)]
# dark opening inside the frame (the frame, incl. the 2.6 mm centre divider, becomes a raised black rim)
KID_OPEN = [(741, 448), (735, 432), (720, 420), (700, 413), (600, 408), (500, 408), (450, 411), (422, 418),
            (403, 434), (396, 455), (394, 485), (399, 518), (410, 542), (428, 560), (460, 572), (550, 577),
            (650, 577), (705, 574), (728, 566), (739, 553), (741, 530)]
BAR_X = [430, 470, 512, 552, 592, 633, 675, 715]           # vertical bar centres

OUTER_INTAKE = [(92, 557), (105, 555), (160, 574), (220, 596), (250, 614), (275, 645), (300, 685), (325, 722),
                (345, 755), (352, 768), (340, 776), (290, 777), (240, 769), (190, 753), (150, 738), (120, 722),
                (103, 705), (95, 670), (91, 620)]

CENTRE_INTAKE = [(765, 685), (470, 685), (448, 680), (432, 672), (420, 666), (370, 661), (340, 657), (336, 663),
                 (352, 692), (374, 727), (397, 759), (415, 777), (440, 781), (765, 782)]
RADAR = [(765, 690), (712, 690), (700, 705), (696, 725), (698, 760), (706, 790), (765, 790)]


def kidney_bars(centres_px, rib=0.9, lean_px=0):
    ribs = []
    for c in centres_px:
        top, bot = (mm_x(c - lean_px * 0.8), (PX_B - 390) * S * YS), (mm_x(c + lean_px * 0.8), (PX_B - 600) * S * YS)
        ribs.append(LineString([top, bot]).buffer(rib / 2, cap_style=2))
    return unary_union(ribs)


KID_G = full_poly(KIDNEY)
KID_OPEN_G = full_poly(KID_OPEN)
KID_RIBS = KID_G.difference(KID_OPEN_G).union(_mirror(kidney_bars(BAR_X)).intersection(KID_OPEN_G))

RADAR_G = full_poly(RADAR).buffer(-1.4, join_style=1).buffer(1.4, join_style=1)
CENTRE_MESH = soft(full_poly(CENTRE_INTAKE).buffer(-0.1).difference(RADAR_G.buffer(0.3)))
CENTRE_HONEY = clean_mesh(CENTRE_MESH, honeycomb(y0=(PX_B - 735) * S * YS))

OUTER_MESH = soft(full_poly(OUTER_INTAKE).buffer(-0.1).intersection(box(-60, -5, 60, (PX_B - 618) * S * YS)))
OUTER_HONEY = clean_mesh(OUTER_MESH, honeycomb(y0=(PX_B - 700) * S * YS, x0=0.0))

SPEC = dict(
    id='g30_m550i', name='BMW M550i xDrive (G30 LCI)',
    ref='kc/cars/g30_m550i/ref/front.jpg',
    units='px', y_scale=YS, px_left=PX_L, px_right=PX_R, px_bottom=PX_B, center_x=CX,
    outline_half=OUTLINE,
    prims=[
        # grooves: fender/hood shut line down to the headlight, power-dome crease towards the kidney corner,
        # hood front shut line above the kidneys, lower bumper lip crease
        dict(kind='stroke', color='groove', width=0.68, smooth=2,
             pts=C([(200, 160), (186, 182), (171, 215), (163, 260), (161, 298), (164, 330)])),
        dict(kind='stroke', color='groove', width=0.68, smooth=2,
             pts=C([(465, 343), (430, 300), (385, 240), (338, 172)])),
        dict(kind='stroke', color='groove', width=0.68, smooth=2,
             pts=[(380, 384), (420, 373), (500, 367), (600, 366), (700, 370), (765, 377)]),
        dict(kind='stroke', color='groove', width=0.68, smooth=2,
             pts=[(405, 799), (560, 801), (765, 802)]),
        # LCI laser headlight + DRL: two upper light bars and two L-shaped light guides (white strokes)
        dict(kind='poly', color='black', pts=HEADLIGHT),
        dict(kind='stroke', color='white', width=0.7, pts=[(132, 354), (186, 367)]),
        dict(kind='stroke', color='white', width=0.7, pts=[(200, 364), (218, 367), (228, 378), (346, 410)]),
        dict(kind='stroke', color='white', width=0.7, pts=[(122, 375), (127, 401), (136, 414), (150, 420), (200, 429)]),
        dict(kind='stroke', color='white', width=0.7, pts=[(207, 392), (214, 420), (222, 436), (240, 446), (347, 463)]),
        # kidneys: black, single-frame rim + 8 vertical bars each as relief
        dict(kind='poly', color='black', pts=KIDNEY, relief=dict(type='custom', ribs=KID_RIBS)),
        # tall trapezoid outer intakes with honeycomb below the gloss upper band
        dict(kind='poly', color='black', pts=OUTER_INTAKE),
        dict(kind='geom', color='relief', geom=OUTER_MESH, relief=dict(type='custom', ribs=OUTER_HONEY), mirror=False),
        # wide lower centre opening: honeycomb around the flush-black ACC radar cover
        dict(kind='poly', color='black', pts=CENTRE_INTAKE),
        dict(kind='geom', color='relief', geom=CENTRE_MESH, relief=dict(type='custom', ribs=CENTRE_HONEY), mirror=False),
        # parking sensors (one per side) + ONE tow-hook cover (viewer's left only - user's BMW rule)
        dict(kind='ring', color='black', c=(500, 660), r_mm=0.9, width=0.5),
        dict(kind='stroke', color='black', width=0.65, mirror=False,
             pts=[(378, 602), (438, 605), (454, 630), (447, 642), (394, 639), (374, 616), (378, 602)]),
    ],
    badge=None,
    tab=dict(y_frac=0.53),
)
