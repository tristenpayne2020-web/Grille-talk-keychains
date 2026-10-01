# Mercedes-AMG GT 63 S 4MATIC+ 4-Door Coupe (X290, 2019-2023, pre-facelift) - front keychain, G80 design language.
# Reference: ref/front.jpg = Mercedes-Benz press photo (Brilliant Blue Magno, black studio), via caricos.com
# (2560 x 1440). Straight-on, level, centred: left half + mirrored left half overlay seamlessly at x = 1270, so no
# rotation. Cross-checked against the daylight US-spec press photo ref/cand_us_blue_2560x1440.jpg for the lower
# fascia (which surfaces are body colour, where the chrome A-wing runs). Traced half = viewer's LEFT.
# See ref/SOURCE.txt for URLs / licence. 1 mm = 19.08 px (body 502..2038 px = 80.5 mm); height 39.1 mm (sedan nose,
# 6.2 mm taller than the 2-door C190 amg_gt in the line, 32.9 mm).
#
# Design (G80 language):
#  * white = body paint: hood, fenders, the bumper incl. the body-colour frame round each outer intake (the AMG
#    A-wing 'fins') and the band under the grille.
#  * black = slim Multibeam headlamps (whole lens), the Panamericana grille, the outer intakes, the black A-wing
#    mouth (trim band under the grille wrapping down between the intake frame and the chrome diagonal + centre
#    intake + carbon splitter), parking sensors, hood emblem.
#  * white on black = light signature + chrome: the X290 DRL (eyebrow along the lamp's top edge, rounded inner
#    corner, short return along the bottom) 0.75 mm; the chrome A-wing line (crossbar + diagonals beside the intake
#    frames) 0.85 mm; the lower chrome blade over the splitter 0.7 mm; the grille star (chrome ring + star). All of
#    these are separate white islands (>= 0.8 mm of black from the body), so export3's custom body-colour builds keep
#    them white while the body - incl. the intake frames - takes the body colour.
#  * relief (recessed with ribs): grille = vertical slats at the real 3.2 mm pitch (no slat under the star, as on the
#    car); outer intakes = 3 horizontal flics falling 2.6 deg to the centre; centre intake = 3 vertical dividers.
#    All ribs 1.4 mm so the classic build's 0.4 mm stepped rib tops keep a 0.6 mm top face.
#  * grooves 0.58 mm: clamshell hood shut line (hooks up into the fender edge at both ends) and the two power-dome
#    flanks running down from the cowl.
#  * badge (SHOW_BADGE, or KC_BADGE=0 for a badge-free export): grille star d 9.2 mm (photo 9.3) as a white chrome
#    ring + blunt-armed white star on a flat black disc (collar + bridge keep it out of the slat pocket), plus the
#    small hood emblem ring. Badge off -> continuous slats incl. the centre one, no emblem.
#  * dropped: plate, radar/camera, grille cross-bars, projector modules, washer nozzles, mirrors.
import os, sys, math
from shapely.geometry import LineString, Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib')))
import geom

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):
    SHOW_BADGE = False

CX = 1270                       # centreline (px)
GROOVE_W = 0.58

# ------------------------------------------------------------------------------------------------ outline
OUTLINE = [(1270, 431), (1100, 431), (960, 433), (860, 436), (800, 439), (772, 443), (752, 452), (736, 464),
           (718, 482), (699, 501), (678, 520), (655, 539), (622, 558), (586, 578), (557, 596), (538, 614),
           (528, 633), (522, 655), (516, 695), (510, 740), (506, 790), (503, 860), (502, 960), (503, 1050),
           (505, 1085), (510, 1105), (519, 1122), (532, 1140), (550, 1155), (585, 1166), (700, 1172),
           (900, 1176), (1270, 1177)]
XL = min(x for x, y in OUTLINE)
XR = 2 * CX - XL
YB = max(y for x, y in OUTLINE)
S = 80.5 / (XR - XL)            # mm per px
PX = 1.0 / S                    # px per mm


def mm(p):
    """photo px -> keychain mm (same mapping as the pipeline: x right from the centreline, y up from the bottom)"""
    return ((p[0] - CX) * S, (YB - p[1]) * S)


def _ngon(c, r_mm, n=8):
    """Regular n-gon (px), circumradius r_mm: prints like a circle, sliced as straight moves."""
    a0 = math.pi / n
    return [(c[0] + r_mm * PX * math.cos(a0 + 2 * math.pi * k / n),
             c[1] + r_mm * PX * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


# ------------------------------------------------------------------------------------------------ headlight
HEAD = [(544, 641), (550, 632), (562, 630), (600, 636), (700, 661), (800, 692), (834, 706), (833, 710), (820, 721),
        (802, 740), (788, 760), (776, 779), (763, 790), (750, 793), (700, 790), (630, 783), (577, 773),
        (553, 764), (543, 750), (539, 705), (540, 662)]
# Multibeam DRL: eyebrow along the top edge, rounded inner corner, short return along the bottom
DRL = [(598, 658), (650, 669), (700, 685), (750, 702), (776, 711), (785, 719), (781, 733), (771, 746),
       (759, 758), (747, 766), (720, 769), (664, 769)]

# ------------------------------------------------------------------------------------------------ grille
GRILLE = [(1300, 702), (1270, 702), (1100, 702), (960, 704), (890, 707), (858, 712), (840, 723), (825, 737),
          (811, 755), (798, 776), (789, 797), (788, 815), (792, 833), (802, 850), (818, 866), (842, 881),
          (875, 895), (920, 907), (1000, 916), (1100, 921), (1270, 924), (1300, 924)]

# ------------------------------------------------------------------------------------------------ lower fascia
# outer intake opening (inside its body-colour frame)
INTAKE = [(590, 921), (700, 919), (760, 924), (786, 932), (806, 943), (824, 955), (836, 969), (842, 985),
          (836, 1001), (824, 1019), (808, 1039), (792, 1059), (777, 1078), (763, 1092), (748, 1099), (620, 1100),
          (590, 1096), (570, 1086), (561, 1064), (560, 960), (565, 938), (575, 926)]
# the black A-wing mouth: band under the grille band, wrapping down between the intake frame and the chrome
# diagonal into the splitter, the centre intake and the splitter (one black area; the chrome A-line is painted white
# over it and stays a separate island, >= 0.8 mm clear of the body-colour intake frame, so custom body-colour prints
# keep the chrome white)
MOUTH = [(1300, 942), (1270, 942), (1100, 941), (980, 939), (905, 936), (868, 933), (848, 930), (838, 933),
         (842, 942), (856, 956), (862, 972), (861, 990), (853, 1006), (840, 1026), (824, 1047), (808, 1068),
         (793, 1088), (779, 1106), (766, 1121), (754, 1131), (738, 1137), (700, 1140), (620, 1134), (570, 1127), (540, 1122), (524, 1124), (490, 1130), (490, 1220), (1300, 1220)]
# chrome A-wing line: crossbar across the centre, diagonals down beside the intake frames to the splitter
ALINE = [(1300, 1001), (1000, 1002), (950, 1004), (925, 1009), (905, 1018), (887, 1030), (868, 1046),
         (850, 1065), (832, 1085), (815, 1103), (800, 1119), (789, 1131)]
# lower chrome blade on top of the carbon splitter
BLADE = [(838, 1137), (900, 1140), (1000, 1142), (1300, 1146)]

# outer intake flics: 3 horizontal fins (y at x = 700 px; real fins at ~31 / 57 / 80 % of the opening height, spaced a
# little more evenly here because the ribs are wider than the real fins),
# falling 2.6 deg towards the centre like the photo; built as exact ribs so no half fins appear at the walls
FLIC_Y = (968, 1016, 1062)
FLIC_W = 1.4                    # >= 1.4 mm so the classic build's 0.4 mm stepped rib top keeps a 0.6 mm top face
FLIC_TILT = math.tan(math.radians(2.6))


def _flics_left():
    bars = []
    for y in FLIC_Y:
        a, b = (520, y + (520 - 700) * FLIC_TILT), (900, y + (900 - 700) * FLIC_TILT)
        bars.append(LineString([mm(a), mm(b)]).buffer(FLIC_W / 2, cap_style=2))
    return unary_union(bars)


_intake_l = Polygon([mm(p) for p in INTAKE]).buffer(0)
FLICS_L = geom.regularize(_intake_l, _flics_left().intersection(_intake_l), 0.64)
FLICS_R = affinity.scale(FLICS_L, xfact=-1, yfact=1, origin=(0, 0))

# centre intake (under the chrome crossbar, above the lower blade): recessed, with its 3 vertical dividers
CENTRE = [(1300, 1001), (1000, 1002), (950, 1004), (925, 1009), (905, 1018), (887, 1030), (868, 1046),
          (850, 1065), (832, 1085), (815, 1103), (806, 1112), (838, 1137), (900, 1140), (1000, 1142), (1300, 1146)]
DIV_X = (0.0, 10.6)             # mm from the centreline (real: centre + 170 px / 1295 px of body width)
DIV_W = 1.4
CENTRE_RIBS = unary_union([box(sx * x - DIV_W / 2, 0, sx * x + DIV_W / 2, 20) for x in DIV_X for sx in (-1, 1)])

# ------------------------------------------------------------------------------------------------ grooves
SHUT = [(1300, 613), (1100, 614), (950, 616), (865, 618), (815, 617), (770, 610), (730, 600), (695, 590),
        (670, 580), (658, 568), (652, 556), (649, 545), (646, 533)]
DOME = [(1034, 420), (1040, 470), (1047, 530), (1053, 588)]

# ------------------------------------------------------------------------------------------------ badge
STAR_C = (1270, 818)
STAR_D = 9.2                    # outer diameter of the chrome ring (mm); photo ring = 178 px = 9.3 mm
STAR_RING = 0.65                # white ring width (mm)
STAR_COLLAR = 0.5               # flat black collar round the ring: its edge (5.1 mm) stays 0.6 mm clear of the
                                # slats at +-6.4 mm
STAR_ARM_ROOT = 0.62            # half-width of the white arms where they leave the centre (mm)
STAR_ARM_END = 0.32             # half-width of the blunt arm end hidden in the ring (mm)


def _star_arms():
    """White three-pointed star (px): arms taper from the centre to blunt ends running 0.3 mm into the ring, so no
    white tip is ever narrower than ~0.64 mm."""
    R = STAR_D / 2
    s_end = R - STAR_RING + 0.3
    pts = []
    for k in range(3):
        a = math.radians(90 + 120 * k)
        ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
        pts.append((s_end * ux - STAR_ARM_END * nx, s_end * uy - STAR_ARM_END * ny))
        pts.append((s_end * ux + STAR_ARM_END * nx, s_end * uy + STAR_ARM_END * ny))
        b = a + math.radians(60)
        pts.append((STAR_ARM_ROOT * math.cos(b), STAR_ARM_ROOT * math.sin(b)))
    return [(STAR_C[0] + x * PX, STAR_C[1] - y * PX) for x, y in pts]


# flat (not recessed) zone of the badge: collar disc + a 9 mm wide bridge down to the grille's bottom wall, so no
# recessed sliver is left between the collar and the wall (the ring sits only 0.95 mm above it) and no short slat stub
# is left under the star (too small to print with the classic build's chamfered rib tops)
_g = Polygon([mm(p) for p in GRILLE]).buffer(0)
GRILLE_MM = unary_union([_g, affinity.scale(_g, xfact=-1, yfact=1, origin=(0, 0))])
STAR_FLAT = unary_union([Point(mm(STAR_C)).buffer(STAR_D / 2 + STAR_COLLAR, 128),
                         box(-4.5, 0, 4.5, mm(STAR_C)[1])]).intersection(GRILLE_MM)

# Mercedes emblem on the nose (small ring, 0.7 mm clear below the hood shut line)
HOOD_EMBLEM = [
    dict(kind='circle', color='black', c=(CX, 650), r_mm=0.95, mirror=False),
    dict(kind='poly', color='white', pts=_ngon((CX, 650), 0.43), mirror=False),
]

STAR = [
    # white first: takes the badge zone out of the recessed slat field -> flat black badge disc
    dict(kind='geom', color='white', geom=STAR_FLAT, mirror=False),
    dict(kind='geom', color='black', geom=STAR_FLAT, mirror=False),
    dict(kind='ring', color='white', c=STAR_C, r_mm=STAR_D / 2, width=STAR_RING, mirror=False),
    dict(kind='poly', color='white', pts=_star_arms(), mirror=False),
]

# grille slats: vertical ribs at +-3.2 mm steps like the real slats (3.16 mm pitch, first pair at +-3.5 mm); the
# centreline slat exists only when the star is switched off (on the car the star covers it)
SLAT_PITCH, SLAT_W = 3.2, 1.4


def _grille_ribs():
    region = GRILLE_MM
    ks = range(1, 10) if SHOW_BADGE else range(0, 10)
    xs = sorted({sx * k * SLAT_PITCH for k in ks for sx in (-1, 1)})
    bars = unary_union([box(x - SLAT_W / 2, 0, x + SLAT_W / 2, 40) for x in xs])
    if SHOW_BADGE:
        region = region.difference(STAR_FLAT)
    return geom.regularize(region, bars.intersection(region), 0.64)


GRILLE_RIBS = _grille_ribs()

prims = [
    # headlights + DRL signature
    dict(kind='poly', color='black', pts=HEAD),
    dict(kind='stroke', color='white', width=0.75, pts=DRL),
    # Panamericana grille: recessed, vertical slats (real slats: 3.16 mm pitch, one on the centreline hidden by the star)
    dict(kind='poly', color='black', pts=GRILLE, relief=dict(type='custom', ribs=GRILLE_RIBS)),
    # lower fascia
    dict(kind='poly', color='black', pts=INTAKE),
    dict(kind='poly', color='black', pts=MOUTH),
    dict(kind='stroke', color='white', width=0.85, pts=ALINE),
    dict(kind='stroke', color='white', width=0.7, pts=BLADE),
    # outer intake flics (3 horizontal fins, falling slightly towards the centre)
    dict(kind='poly', color='relief', mirror=False, pts=INTAKE, relief=dict(type='custom', ribs=FLICS_L)),
    dict(kind='poly', color='relief', mirror=False, pts=[(2 * CX - x, y) for x, y in INTAKE],
         relief=dict(type='custom', ribs=FLICS_R)),
    # centre intake: recessed, 3 vertical dividers
    dict(kind='poly', color='relief', pts=CENTRE, relief=dict(type='custom', ribs=CENTRE_RIBS)),
    # engraved lines: hood shut line (hooks up into the fender edge), power-dome flanks
    dict(kind='stroke', color='groove', width=GROOVE_W, pts=SHUT),
    dict(kind='stroke', color='groove', width=GROOVE_W, pts=DOME),
    # details: parking sensor ring
    dict(kind='circle', color='black', c=(574, 870), r_mm=1.0),
    dict(kind='poly', color='white', pts=_ngon((574, 870), 0.45)),
] + (STAR + HOOD_EMBLEM if SHOW_BADGE else [])

SPEC = dict(
    id='amg_gt63_4door', name='Mercedes-AMG GT 63 S 4-Door (X290)',
    ref='kc/cars/amg_gt63_4door/ref/front.jpg',
    units='px', px_left=XL, px_right=XR, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    badge=None,
    badge_on=SHOW_BADGE,
    badge_note='custom Mercedes star prims (chrome ring + star in white on a flat black disc); SHOW_BADGE / KC_BADGE=0',
    tab=dict(y_frac=0.48),
)
