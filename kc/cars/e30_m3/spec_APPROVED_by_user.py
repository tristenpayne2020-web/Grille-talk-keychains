# BMW M3 (E30, 1986-1991) front keychain.
# Reference: Wikimedia Commons "BMW M3 E30 Evolution Front 2025-06-28.jpg" by Strubbl, CC BY-SA 4.0
#   https://commons.wikimedia.org/wiki/File:BMW_M3_E30_Evolution_Front_2025-06-28.jpg
# ref/front.jpg = the 3840 px Commons rendition, yaw-rectified (1D projective fit on the four headlight centres)
# and levelled by 0.6 deg, so the car is mirror-symmetric about x = 2087 (matrix in work/H_total.npy).
# Left half traced in photo pixels, mirrored. Body-colour logic (rub strip, slots, nose/bumper gap) cross-checked
# on a white standard M3 (Commons "BMW M3 (17755995436).jpg", CC BY 2.0).
#
# Design: black grille band with horizontal louvres (relief) carrying the four round lamps as solid white glass
# discs (the low-beam lamps get their engraved inner lens ring); upright twin kidneys = white chrome surround +
# black interior with 4 vertical slats (relief) and a flush black gap between them; black rub strip, rectangular
# turn signals, slatted outer lower openings, two rows of centre slots, black lower lip; grooves = hood outline
# (fender shut lines + hood front edge) running into the raised centre-section edges, and the nose/bumper gap.
# One tow-hook cover ring (viewer's left only).
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

CX, PX_B = 2087, 2175
S = 80.5 / (2 * (CX - 424))         # mm per photo px (body width 80.5 mm between the bumper corners)


def mm(p):
    return ((p[0] - CX) * S, (PX_B - p[1]) * S)


# ---- headlights: glass circles, centres + radii in px
LAMP_Y = 1176
LAMP_OUT = (798, LAMP_Y, 148)       # outer (low beam) lamp
LAMP_IN = (1163, LAMP_Y, 155)       # inner (high beam) lamp
LAMP_GROOVES_OUT = ((1.6, 0.55),)   # engraved inner lens ring of the low-beam lamp (outer r mm, width mm)
LAMP_GROOVES_IN = ()


def lamp(c, r_px, grooves=()):
    """Headlight glass = solid white disc in the black band (it removes the band louvres under it)."""
    x, y = c
    out = [dict(kind='circle', color='white', c=(x, y), r_mm=r_px * S)]
    for ro, w in grooves:
        out.append(dict(kind='ring', color='groove', c=(x, y), r_mm=ro, width=w))
    return out


# ---- kidney (left one): outer chrome edge and interior opening. The chrome sits fully inside black (band +
# a flush black surround 0.65 mm wide), so each surround is its own white island (stays white/chrome in the custom
# body-colour version); a 0.68 mm black gap separates the two surrounds.
KID_OUT = [(1752, 1050), (1756, 1026), (1768, 1013), (1790, 1008), (2040, 1008), (2062, 1012), (2073, 1030),
           (2073, 1355), (2067, 1376), (2049, 1384), (1800, 1384), (1778, 1377), (1768, 1357), (1752, 1150)]
KID_IN = [(1784, 1068), (1788, 1052), (1800, 1038), (2029, 1038), (2039, 1042), (2043, 1055),
          (2043, 1340), (2037, 1350), (2025, 1354), (1812, 1354), (1800, 1350), (1794, 1338), (1784, 1150)]


def kidney_slats(n=4, rib=0.7, x_out=1790, x_in=2043):
    """n evenly spaced full-height vertical slats per kidney (mm, both kidneys), clear of the side walls."""
    x0, x1 = mm((x_out, 0))[0], mm((x_in, 0))[0]
    g = (x1 - x0 - n * rib) / (n + 1)
    bars = []
    for i in range(n):
        a = x0 + g + i * (rib + g)
        bars += [box(a, 0, a + rib, 60), box(-a - rib, 0, -a, 60)]
    return unary_union(bars)


BAND = [(1726, 983), (600, 983), (578, 989), (566, 1008), (562, 1100), (562, 1330), (570, 1355), (592, 1368),
        (1726, 1368)]


def band_louvres(n=6, rib=0.7, lamp_gap=0.6, end_gap=0.5, min_len=1.0):
    """Horizontal louvres of the grille band (mm, both sides): n rows evenly spaced with equal gaps at the band
    top/bottom; every louvre ends square, lamp_gap mm short of the lamp glass (the lamp bezel), and end_gap mm
    short of the band's outer end, so no rib or gap ever runs out into a thin tangent sliver."""
    band = Polygon([mm(p) for p in BAND])
    x_end, y0, x_kid, y1 = band.bounds
    x_end += end_gap
    g = (y1 - y0 - n * rib) / (n + 1)
    lamps = [(mm(l[:2]), l[2] * S) for l in (LAMP_OUT, LAMP_IN)]
    bars = []
    for i in range(n):
        a, b = y0 + g + i * (rib + g), y0 + g + i * (rib + g) + rib
        cuts = []
        for (lx, ly), r in lamps:
            dy = min(abs(a - ly), abs(b - ly)) if not (a <= ly <= b) else 0.0
            if dy < r:
                h = (r * r - dy * dy) ** 0.5 + lamp_gap
                cuts.append((lx - h, lx + h))
        segs, x = [], x_end
        for c0, c1 in sorted(cuts):
            if c0 > x:
                segs.append((x, c0))
            x = max(x, c1)
        segs.append((x, x_kid))
        for u, v in segs:
            if v - u >= min_len:
                bars += [box(u, a, v, b), box(-v, a, -u, b)]
    return unary_union(bars)


prims = [
    # black grille band (headlight panel) with horizontal louvres; it ends under the kidney chrome
    dict(kind='poly', color='black', pts=BAND, relief=dict(type='custom', ribs=band_louvres(min_len=2.0))),
    # flush black kidney surround: frames the chrome, fills the gap between the kidneys, wraps under them
    dict(kind='poly', color='black', pts=[(1726, 983), (CX, 983), (CX, 1368), (1726, 1368)]),
    dict(kind='poly', color='black', pts=KID_OUT, offset=0.65),
]
prims += lamp(LAMP_OUT[:2], LAMP_OUT[2], LAMP_GROOVES_OUT)
prims += lamp(LAMP_IN[:2], LAMP_IN[2], LAMP_GROOVES_IN)
prims += [
    # kidneys: white chrome surround, black interior with vertical slats
    dict(kind='poly', color='white', pts=KID_OUT),
    dict(kind='poly', color='black', pts=KID_IN, relief=dict(type='custom', ribs=kidney_slats())),
    # bumper: black rub strip (continuous across the centre) + outboard piece rising round the corner
    dict(kind='poly', color='black', pts=[(CX, 1570), (1000, 1570), (1000, 1630), (CX, 1630)]),
    dict(kind='poly', color='black', pts=[(610, 1570), (610, 1630), (470, 1622), (400, 1615), (400, 1548), (470, 1558)]),
    # rectangular turn signal
    dict(kind='poly', color='black', pts=[(662, 1550), (952, 1550), (962, 1560), (962, 1695), (952, 1705),
                                          (662, 1705), (652, 1695), (652, 1560)]),
    # outboard lower opening (brake duct / fog-lamp grille position), slatted
    dict(kind='poly', color='black', pts=[(645, 1731), (975, 1731), (987, 1743), (987, 1892), (975, 1904),
                                          (645, 1904), (633, 1892), (633, 1743)],
         relief=dict(type='hbars', pitch=1.6, rib=0.75, offset=0.8)),      # 2 slats
    # centre slots: two rows of three
    dict(kind='poly', color='black', pts=[(CX, 1790), (1588, 1790), (1576, 1800), (1576, 1857), (1588, 1867), (CX, 1867)]),
    dict(kind='poly', color='black', pts=[(CX, 1943), (1592, 1943), (1580, 1955), (1580, 2034), (1592, 2046), (CX, 2046)]),
    dict(kind='poly', color='white', pts=[(1906, 1780), (1931, 1780), (1931, 2056), (1906, 2056)]),
    # lower lip spoiler
    dict(kind='poly', color='black', pts=[(CX, 2092), (1800, 2090), (1300, 2083), (800, 2074), (515, 2068),
                                          (400, 2068), (400, 2250), (CX, 2250)]),
    # grooves: hood outline (fender shut line + hood front edge) running into the raised centre-section edge
    dict(kind='stroke', color='groove', width=0.55, pts=[(1120, 700), (1000, 730), (880, 757), (760, 785),
                                                          (670, 825), (618, 880), (604, 922), (627, 946),
                                                          (1712, 946), (1710, 612)]),
    # nose / bumper gap
    dict(kind='stroke', color='groove', width=0.55, pts=[(520, 1404), (600, 1442), (900, 1449), (CX, 1450)]),
    # single tow-hook cover (viewer's left only)
    dict(kind='ring', color='black', c=(1120, 1698), r_mm=1.0, width=0.55, mirror=False),
]

SPEC = dict(
    id='e30_m3', name='BMW M3 (E30)',
    ref='kc/cars/e30_m3/ref/front.jpg',
    units='px', px_left=424, px_right=2 * CX - 424, px_bottom=PX_B, center_x=CX,
    outline_half=[(CX, 570), (1700, 578), (1400, 594), (1260, 606), (1180, 630), (1110, 668), (1030, 697),
                  (950, 712), (900, 721), (800, 742), (700, 766), (645, 795), (600, 848), (560, 915), (530, 980),
                  (507, 1040), (500, 1100), (500, 1325), (492, 1350), (470, 1375), (447, 1405), (430, 1440),
                  (424, 1480), (425, 1530), (432, 1585), (448, 1630), (470, 1672), (491, 1728), (498, 1800),
                  (502, 1900), (504, 2030), (514, 2064), (527, 2088), (537, 2114), (559, 2141), (595, 2156),
                  (673, 2168), (900, 2172), (CX, PX_B)],
    prims=prims,
    badge=dict(type='roundel', c=(CX, 868), d=4.3),
    tab=dict(y_frac=0.57),
)
