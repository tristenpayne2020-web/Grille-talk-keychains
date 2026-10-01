# Porsche Macan GTS (95B.2 facelift, 2022-2024) front keychain - traced on a straight-on studio press photo
# (viewer's right half traced, mirrored). NO LOGOS: badge=None, the crest spot on the hood stays plain body.
# Reference: caricos.com gallery "2022 Porsche Macan GTS" image #32 (Porsche AG press photo, Python Green, studio).
CX = 1293

SPEC = dict(
    id='macan', name='Porsche Macan GTS (95B.2)',
    ref='kc/cars/macan/ref/front.jpg',
    units='px', px_left=692, px_right=1895, px_bottom=1078, center_x=CX,
    outline_half=[(CX, 506), (1400, 508), (1500, 514), (1600, 522), (1680, 531), (1730, 542), (1765, 552),
                  (1795, 561), (1826, 576), (1849, 607), (1865, 648), (1876, 684), (1887, 716), (1893, 760),
                  (1895, 820), (1893, 900), (1888, 950), (1882, 990), (1876, 1030), (1868, 1058), (1846, 1072),
                  (1760, 1077), (1600, 1078), (CX, 1078)],
    outline_smooth=1,
    prims=[
        # headlight unit: Porsche teardrop with the pointed inner-lower corner
        dict(kind='poly', color='black', smooth=2, pts=[(1662, 698), (1664, 668), (1674, 638), (1692, 610), (1714, 592),
             (1745, 580), (1780, 576), (1806, 580), (1824, 593), (1837, 619), (1842, 648), (1837, 674), (1822, 692),
             (1795, 702), (1750, 705), (1700, 704)]),
        # four-point LED DRL: four short white bars in a 2x2 cluster around the projector (upper pair rises slightly outward)
        dict(kind='stroke', color='white', width=0.9, cap='round', pts=[(1710, 619), (1742, 618)]),
        dict(kind='stroke', color='white', width=0.9, cap='round', pts=[(1772, 617), (1804, 614)]),
        dict(kind='stroke', color='white', width=0.9, cap='round', pts=[(1708, 658), (1742, 658)]),
        dict(kind='stroke', color='white', width=0.9, cap='round', pts=[(1774, 658), (1808, 657)]),

        # centre grille opening: slats in the upper part, silver mesh bar, plain black plate panel below
        dict(kind='poly', color='black', pts=[(CX, 747), (1592, 747), (1592, 952), (1562, 976), (CX, 976)]),
        dict(kind='poly', color='relief', pts=[(CX, 752), (1600, 752), (1600, 864), (CX, 864)],
             relief=dict(type='hbars', pitch=3.0, rib=1.2, offset=0.0)),
        # silver mesh bar across the grille (body-coloured strip, chamfered ends)
        dict(kind='poly', color='white', pts=[(CX, 873), (1548, 873), (1562, 885), (1548, 897), (CX, 897)]),
        # side intake: one rounded black opening, slats below the LED light bar
        dict(kind='poly', color='black', smooth=2, pts=[(1608, 747), (1850, 745), (1864, 754), (1870, 790),
             (1868, 880), (1860, 932), (1846, 958), (1820, 970), (1760, 978), (1680, 982), (1608, 984)]),
        # slats in the side intake below the light bar, clipped clear of the rounded bottom
        dict(kind='poly', color='relief', pts=[(1600, 800), (1900, 800), (1900, 958), (1600, 958)],
             relief=dict(type='hbars', pitch=3.0, rib=1.2, offset=0.0)),
        # LED light blade at the top of the side intake, with a small upturn at its outer end
        dict(kind='stroke', color='white', width=0.8, cap='round', pts=[(1692, 781), (1828, 773), (1838, 766)]),
        # lower valance / lip: flat straight-topped band, ends tucked inside the body corners
        dict(kind='poly', color='black', pts=[(CX, 1015), (1826, 1015), (1836, 1021), (1822, 1090), (CX, 1090)]),
        # fender crown crease: from the cowl, down and outward onto the inner top of the headlight
        dict(kind='stroke', color='groove', width=0.65, smooth=2, pts=[(1507, 524), (1507, 566), (1526, 598),
             (1575, 616), (1630, 622), (1660, 617)]),
        # hood / bumper shut line under the headlights
        dict(kind='stroke', color='groove', width=0.65, smooth=2, pts=[(1650, 712), (1560, 722), (1450, 726), (CX, 727)]),
    ],
    badge=None,
    tab=dict(y_frac=0.62),
)
