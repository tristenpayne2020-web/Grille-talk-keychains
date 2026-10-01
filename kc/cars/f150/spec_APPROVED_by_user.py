# Ford F-150 (14th gen, P702, 2021-2023) front keychain
# Reference: ref/front.jpg = ref/caricos_11.jpg (official Ford press photo "2021 Ford F-150 Limited", via caricos.com,
# see ref/SOURCE.txt) levelled by -6.6 deg with trace_tools rotate. Traced half = viewer's LEFT, centreline x = 1316 px.
# NO LOGOS (user rule): the Ford oval and the LIMITED hood lettering are NOT drawn; the oval spot is plain grille bar.
import math

CX = 1316


def _arc(cx, cy, r, a0, a1, n=8):
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
            for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)]]


def rrect(xl, yt, yb, rt, rb):
    """Full-width rounded rectangle, symmetric about CX: left edge xl, top yt, bottom yb, corner radii (px).
    Image y points down, so the top-left arc runs 180->270 deg and the bottom-left arc 90->180 deg."""
    xr = 2 * CX - xl
    pts = _arc(xl + rt, yt + rt, rt, 180, 270)                      # top-left
    pts += _arc(xr - rt, yt + rt, rt, 270, 360)                     # top-right
    pts += _arc(xr - rb, yb - rb, rb, 0, 90)                        # bottom-right
    pts += _arc(xl + rb, yb - rb, rb, 90, 180)                      # bottom-left
    return pts


def rbox(x0, y0, x1, y1, r):
    """Small rounded box (px), for local details."""
    return (_arc(x0 + r, y0 + r, r, 180, 270, 4) + _arc(x1 - r, y0 + r, r, 270, 360, 4)
            + _arc(x1 - r, y1 - r, r, 0, 90, 4) + _arc(x0 + r, y1 - r, r, 90, 180, 4))


SLATS = dict(type='hbars', pitch=1.4, rib=0.7)

SPEC = dict(
    id='f150', name='Ford F-150 (2021+)',
    ref='kc/cars/f150/ref/front.jpg',
    units='px', px_left=642, px_right=2 * CX - 642, px_bottom=1052, center_x=CX,
    # flat, square-cornered hood top raised ~40 px over the photo cowl (the low camera foreshortens the tall hood)
    outline_half=[(CX, 310), (760, 310), (712, 312), (684, 322), (666, 340), (658, 365), (655, 420), (652, 520),
                  (650, 700), (656, 758), (648, 771), (642, 790), (642, 915), (650, 935), (668, 948),
                  (678, 985), (686, 1035), (700, 1050), (760, 1052), (CX, 1052)],
    prims=[
        # ---- black band: headlight units (flush with the fender edge) + dark grille surround up to the chrome frame
        dict(kind='poly', color='black', pts=[(CX, 470), (905, 470), (905, 444), (600, 444), (600, 716), (830, 718),
                                              (905, 724), (905, 690), (CX, 690)]),
        # inner edge of the tall, narrow lamp housing (between projectors and grille surround)
        dict(kind='stroke', color='groove', width=0.6, cap='flat', pts=[(830, 480), (830, 718)]),
        # ---- grille: chrome frame (white, squarer top) with two slatted openings and the big centre bar
        dict(kind='poly', color='white', mirror=False, pts=rrect(888, 440, 718, 35, 45)),
        dict(kind='poly', color='black', mirror=False, pts=rrect(913, 466, 550, 30, 12), relief=SLATS),
        dict(kind='poly', color='black', mirror=False, pts=rrect(913, 604, 696, 12, 30), relief=SLATS),
        # centre bar runs out of the frame into the headlight and on as the amber turn bar between the projectors
        dict(kind='poly', color='white', pts=[(836, 566), (895, 566), (895, 592), (836, 592)]),
        dict(kind='stroke', color='white', width=0.8, pts=[(714, 579), (840, 579)]),
        # ---- headlight: C-clamp DRL (thick top bar to the grille frame, outer light pipe, inward bottom return)
        dict(kind='stroke', color='white', width=1.3, pts=[(892, 466), (692, 466), (679, 479), (679, 684),
                                                            (690, 695), (742, 695)]),
        dict(kind='poly', color='white', pts=rbox(736, 510, 800, 562, 10)),
        dict(kind='poly', color='white', pts=rbox(736, 597, 800, 652, 10)),
        # ---- bumper: fog-lamp pocket with the hockey-stick light bar
        dict(kind='poly', color='black', pts=[(698, 784), (895, 784), (870, 860), (700, 860)]),
        dict(kind='stroke', color='white', width=0.8, pts=[(718, 804), (720, 830), (732, 841), (858, 841)]),
        # lower centre intake: slatted side panels + three slots split by chrome dividers
        dict(kind='poly', color='black', pts=[(1118, 836), (952, 836), (940, 846), (884, 922), (1118, 922)], relief=SLATS),
        dict(kind='poly', color='black', mirror=False, pts=[(1120, 836), (2 * CX - 1120, 836), (2 * CX - 1120, 922),
                                                            (1120, 922)]),
        dict(kind='stroke', color='white', width=1.0, cap='flat', pts=[(1118, 826), (1118, 932)]),
        dict(kind='stroke', color='white', width=1.0, cap='flat', pts=[(1250, 826), (1250, 932)]),
        # lower black valance / air dam
        dict(kind='poly', color='black', pts=[(CX, 1000), (905, 1000), (884, 972), (700, 957), (668, 948), (600, 948),
                                              (600, 1100), (CX, 1100)]),
        # ---- engraved lines: hood shut line merged into the power-dome front edge, dome sides, bumper shut line
        dict(kind='stroke', color='groove', width=0.6, pts=[(735, 430), (760, 427), (890, 425), (915, 413), (CX, 412)]),
        dict(kind='stroke', color='groove', width=0.6, smooth=2, pts=[(944, 332), (941, 380), (930, 402), (915, 413)]),
        dict(kind='stroke', color='groove', width=0.6, pts=[(670, 765), (CX, 765)]),
        # parking sensors
        dict(kind='ring', color='black', c=(788, 905), r_mm=1.0, width=0.55),
        dict(kind='ring', color='black', c=(1102, 802), r_mm=1.0, width=0.55),
    ],
    badge=None,
    tab=dict(y_mm=13.0),
)
