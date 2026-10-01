# Mercedes-AMG GT (C190, 2019+ facelift) - front keychain, same design language as the user's G80 M3.
# Reference: Mercedes-Benz press photo of the 2020 AMG GT R (Green Hell Magno), straight-on front view
# (via caricos.com, 2560x1440). Photo is centred and level (left half + mirrored right half overlay cleanly
# at x=1311), so no rotation was needed. Traced on the viewer's LEFT half, everything mirrored.
# Revision 1: cleaner fender shoulder, heavier splitter, G80-weight slats/fins (classic gets the stepped rib tops),
# full-pocket intake relief, smaller hood-emblem ring clear of the shut line, anchored power-dome lines,
# fender seam, GT R hood outlets, 0.8 mm DRL, squarer LED cubes, G80-size sensor rings.
# Revision 2 (line consistency): the library 'star' badge is not used any more (its black arms taper to points and
# needed 3 auto-repairs). The grille star is built here as centred prims painted LAST, like the library badge:
# white disc (d 8.85 mm, the real ring measures 8.9), black 0.55 mm ring, black three-pointed star whose arms stay
# >= 0.62 mm wide and run 0.3 mm into the ring instead of tapering to a point. Switch it off with BADGE_ON = False
# (same convention as c8_corvette, s650_mustang and svj_aventador; SPEC['badge'] is None so the library never draws
# a second one).
import math

BADGE_ON = True

_PX_PER_MM = (2168 - 454) / 80.5            # photo px per keychain mm (same calibration as below)


def _rrect(c, w_mm, h_mm, rot_deg, r_mm=0.2):
    """Rectangle (px) that becomes a w x h mm rounded rectangle after offset=+r_mm; rot in image degrees
    (+ = right end lower)."""
    a = math.radians(rot_deg)
    hw, hh = (w_mm / 2 - r_mm) * _PX_PER_MM, (h_mm / 2 - r_mm) * _PX_PER_MM
    pts = []
    for u, v in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)):
        pts.append((c[0] + u * math.cos(a) - v * math.sin(a), c[1] + u * math.sin(a) + v * math.cos(a)))
    return pts


def _ngon(c, r_mm, n=8):
    """Regular n-gon (px) with circumradius r_mm, flat top. Used for the tiny white pins inside the sensor /
    emblem rings: prints the same as a circle, but the slicer writes it as straight G1 moves (its G2/G3 arc fits of
    a 0.9 mm circle are read as chords by the pipeline's slicecheck parser and flagged as 'lost')."""
    a0 = math.pi / n
    return [(c[0] + r_mm * _PX_PER_MM * math.cos(a0 + 2 * math.pi * k / n),
             c[1] + r_mm * _PX_PER_MM * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


# ---------------------------------------------------------------- Mercedes star (custom badge, see top)
STAR_C = (1311, 897)                 # star centre (px), same place as the old library badge
STAR_D = 8.85                        # outer diameter incl. the black ring (mm)
STAR_RING = 0.55                     # black ring width (mm)
STAR_R_IN = 0.7                      # radius of the star's concave (inner) vertices (mm)
STAR_TIP_IN = 0.3                    # how far the blunt arm ends run into the ring (mm)
STAR_TIP_HW = 0.31                   # arm half-width at its (hidden) end (mm) -> >= 0.62 mm where it meets the ring


def _star_arms():
    """Black three-pointed star (px): one arm up, two down at +-120 deg; each arm tapers from the centre to a
    blunt end hidden 0.3 mm inside the ring, so no black point is ever narrower than ~0.62 mm."""
    R = STAR_D / 2
    s_end = R - STAR_RING + STAR_TIP_IN
    pts_mm = []
    for k in range(3):
        a = math.radians(90 + 120 * k)
        ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
        for sg in (-1, 1):                                     # the two corners of the blunt arm end
            pts_mm.append((s_end * ux + sg * STAR_TIP_HW * nx, s_end * uy + sg * STAR_TIP_HW * ny))
        b = a + math.radians(60)                               # concave vertex between this arm and the next
        pts_mm.append((STAR_R_IN * math.cos(b), STAR_R_IN * math.sin(b)))
    return [(STAR_C[0] + x * _PX_PER_MM, STAR_C[1] - y * _PX_PER_MM) for x, y in pts_mm]   # mm (y up) -> px


STAR = [
    dict(kind='circle', color='white', c=STAR_C, r_mm=STAR_D / 2, mirror=False),
    dict(kind='ring', color='black', c=STAR_C, r_mm=STAR_D / 2, width=STAR_RING, mirror=False),
    dict(kind='poly', color='black', pts=_star_arms(), mirror=False),
]

SPEC = dict(
    id='amg_gt', name='Mercedes-AMG GT (C190)',
    ref='kc/cars/amg_gt/ref/front.jpg',
    units='px', px_left=454, px_right=2168, px_bottom=1203, center_x=1311,
    # windshield base (flat) -> rounded A-pillar corner -> fender shoulder (one smooth run, fitted to the
    # averaged left/right silhouette) -> body side -> bumper corner -> bottom
    outline_half=[(1311, 506), (1000, 505), (700, 502), (652, 503), (634, 506), (620, 510), (607, 517), (595, 528),
                  (583, 541), (573, 554), (564, 566), (552, 579), (541, 589), (527, 601), (511, 614), (496, 627),
                  (484, 637), (472, 649), (465, 659), (460, 672), (458, 687), (456, 707), (455, 736), (454, 800),
                  (454, 1000), (456, 1110), (461, 1150), (476, 1180), (515, 1198), (600, 1203), (1311, 1203)],
    prims=[
        # ---- headlight: whole lens black, cat's-eye shape (outer top corner high, pointed inner tip)
        dict(kind='poly', color='black', smooth=1, pts=[
            (561, 647), (602, 651), (680, 683), (750, 720), (785, 752), (799, 780), (797, 805), (778, 840),
            (757, 872), (724, 877), (673, 867), (630, 856), (587, 839), (559, 819), (544, 796), (539, 759),
            (539, 716), (541, 681), (550, 659)]),
        # DRL signature: long diagonal "eyebrow" line from the outer top corner down to the inner tip, hooking
        # back along the bottom (hairpin)
        dict(kind='stroke', color='white', width=0.8, pts=[
            (582, 679), (762, 783), (772, 792), (772, 806), (760, 813), (646, 798)]),
        # three LED low-beam cubes (squarish, stepping down towards the grille like the real modules)
        dict(kind='poly', color='white', offset=0.2, pts=_rrect((619, 824), 1.4, 1.0, 9)),
        dict(kind='poly', color='white', offset=0.2, pts=_rrect((666, 834), 1.4, 1.0, 9)),
        dict(kind='poly', color='white', offset=0.2, pts=_rrect((712, 843), 1.4, 1.0, 9)),
        # ---- Panamericana grille: black, recessed, vertical slats (G80 slat weight so the classic build gets
        # the same stepped rib tops)
        dict(kind='poly', color='black', smooth=1, pts=[
            (1345, 780), (1311, 780), (1100, 783), (1000, 785), (950, 787), (910, 792), (880, 800), (858, 812), (843, 828),
            (834, 848), (828, 872), (828, 898), (833, 922), (843, 944), (883, 965), (925, 977), (1050, 998),
            (1175, 1007), (1311, 1011), (1345, 1011)],
             relief=dict(type='vbars', pitch=3.0, rib=1.4)),
        # ---- lower fascia: outer intakes + central intake (one black opening under the green bumper band)
        dict(kind='poly', color='black', smooth=1, pts=[
            (1345, 1043), (1311, 1043), (1080, 1040), (990, 1035), (930, 1030), (875, 1022), (840, 1008), (815, 992),
            (790, 976), (765, 964), (720, 955), (640, 951), (612, 956), (596, 968), (589, 990), (588, 1106),
            (592, 1128), (606, 1141), (640, 1146), (750, 1146), (822, 1142), (905, 1135), (1080, 1133),
            (1311, 1133), (1345, 1133)]),
        # outer intake fins (two horizontal flics per side) as relief ribs over the WHOLE outer pocket (no flat
        # black slivers left along its walls); one prim per side so the tilt mirrors
        dict(kind='poly', color='relief', mirror=False, pts=[(570, 940), (795, 940), (795, 1160), (570, 1160)],
             relief=dict(type='hbars', pitch=2.9, rib=1.4, angle=-2.5, offset=-1.75, margin=0.8)),
        dict(kind='poly', color='relief', mirror=False, pts=[(2052, 940), (1827, 940), (1827, 1160), (2052, 1160)],
             relief=dict(type='hbars', pitch=2.9, rib=1.4, angle=2.5, offset=-1.75, margin=0.8)),
        # vertical air-curtain slot at the bumper corner
        dict(kind='poly', color='black', smooth=1, pts=[
            (548, 945), (556, 952), (553, 985), (546, 1040), (541, 1100), (532, 1119), (520, 1121),
            (511, 1110), (508, 1080), (512, 1020), (524, 978), (538, 952)]),
        # ---- splitter (black, full width, G80-weight lip; wraps up the corner with a blunt end)
        dict(kind='poly', color='black', pts=[
            (1345, 1163), (1311, 1163), (905, 1164), (865, 1171), (820, 1175), (600, 1176), (522, 1172), (496, 1162),
            (484, 1146), (482, 1118), (430, 1118), (430, 1230), (1345, 1230)]),
        # ---- GT R hood outlets (slim louvred vents just ahead of the windshield)
        dict(kind='poly', color='black', offset=0.2, pts=[(796, 525), (1002, 525), (999, 531), (799, 531)]),
        # ---- engraved lines: clamshell hood shut line, power-dome edges (top edge -> shut line), fender seam
        dict(kind='stroke', color='groove', width=0.62, smooth=2, pts=[
            (684, 498), (693, 540), (705, 580), (720, 612), (740, 645), (765, 675), (792, 699), (822, 711),
            (880, 712), (1000, 708), (1150, 704), (1311, 702)]),
        dict(kind='stroke', color='groove', width=0.62, smooth=1, pts=[(1064, 498), (1072, 560), (1082, 630), (1090, 705)]),
        dict(kind='stroke', color='groove', width=0.62, pts=[(478, 729), (536, 717)]),
        # ---- details
        # parking sensor: black ring (outer r 1.1 mm) with a 0.9 mm white pin, like the G80's sensor rings
        dict(kind='circle', color='black', c=(504, 938), r_mm=1.1),
        dict(kind='poly', color='white', pts=_ngon((504, 938), 0.5)),
        # hood emblem: small ring on the nose, clear of the shut line (0.6 mm) and the grille (0.64 mm)
        dict(kind='circle', color='black', c=(1311, 744), r_mm=1.05, mirror=False),
        dict(kind='poly', color='white', pts=_ngon((1311, 744), 0.46), mirror=False),
    ] + (STAR if BADGE_ON else []),   # grille star, painted last like the library badge (BADGE_ON above)
    badge=None,          # library 'star' not used; the star is the last three prims (BADGE_ON above)
    badge_note='custom Mercedes star prims (white disc / black ring / black 3-point star), on/off with BADGE_ON in spec.py',
    badge_on=False,
    tab=dict(y_frac=0.52),
)
