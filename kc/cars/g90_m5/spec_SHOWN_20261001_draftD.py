# BMW M5 (G90, 2025+) front keychain.
# PROVISIONAL DESIGN WITHOUT A REFERENCE PHOTO: the cloud container's egress proxy blocked every image host
# (Wikimedia, BMW PressClub, motor1, caricos, ...), so this was drawn in keychain millimetres (units='mm',
# x = 0 at the centreline, y up, 0 at the bottom of the lip) from the published G90/G60 design description:
#   * large, wide, near-rectangular kidney grille with tight horizontal slats and the Iconic Glow contour
#     (black frame / white lit contour / black slatted interior)
#   * slim, long headlights whose inner tips reach toward the kidneys; DRL = "two nearly vertical LED elements
#     positioned towards the outside" of each lamp
#   * M bumper: wide centre intake under the kidneys, huge outer intakes, vertical air curtains at the corners,
#     black lower lip; hood with two creases framing the centre power dome
# NO LOGOS (user rule): no roundel / lettering, the spot above the kidneys stays plain body (badge=None).
# The user should re-trace / check this on a real straight-on photo before printing a sale batch.

OUTLINE = [(0, 38.4), (12, 38.3), (21, 37.9), (27, 37.2), (31.5, 36.1), (34.6, 34.8), (36.8, 33.0),
           (38.4, 30.6), (39.2, 28.3), (39.5, 26.0), (39.7, 22), (40.1, 18), (40.25, 14), (40.25, 10),
           (39.9, 6.6), (39.5, 4.6), (39.2, 2.6), (37.8, 1.2), (34, 0.6), (22, 0.2), (0, 0)]

# viewer's right kidney (mirrored): near-rectangular trapezoid widening to a square lower outer corner
KIDNEY = [(1.0, 15.8), (1.0, 28.4), (1.7, 29.4), (12.2, 29.4), (13.0, 28.6), (14.9, 15.4), (14.6, 15.0), (1.6, 15.0)]

SPEC = dict(
    id='g90_m5', name='BMW M5 (G90)',
    ref=None,
    units='mm',
    outline_half=OUTLINE,
    outline_smooth=1,
    prims=[
        # hood: front shut line above the kidneys (stops short of the lamp), fender/brow lines, two floating dome creases
        dict(kind='stroke', color='groove', width=0.65, pts=[(0, 30.7), (11.0, 30.9), (14.3, 31.4)]),
        dict(kind='stroke', color='groove', width=0.65, pts=[(34.4, 33.4), (32.0, 36.9)]),
        dict(kind='stroke', color='groove', width=0.65, smooth=2, pts=[(8.6, 37.4), (8.2, 35.3), (7.0, 32.4)]),
        # headlight unit (black): slim sharp wedge, thin inner tip toward the kidney, lower edge rising outward
        dict(kind='poly', color='black', smooth=1,
             pts=[(15.4, 30.4), (16.6, 31.4), (21, 31.9), (27, 32.4), (33, 32.8), (35.9, 32.6), (36.8, 31.4),
                  (36.7, 30.3), (35.8, 29.2), (33, 28.5), (28, 28.0), (21, 28.0), (16.2, 28.4)]),
        # DRL: two near-vertical LED elements in the outer part of the lamp (boldest white marks on the face)
        dict(kind='stroke', color='white', width=0.9, cap='round', pts=[(28.4, 29.2), (28.7, 31.3)]),
        dict(kind='stroke', color='white', width=0.9, cap='round', pts=[(32.8, 29.6), (33.1, 31.6)]),
        # kidney grille with Iconic Glow: black frame -> white lit contour -> black interior with tight slats
        dict(kind='poly', color='black', smooth=0, pts=KIDNEY),
        dict(kind='poly', color='white', smooth=0, pts=KIDNEY, offset=-0.9),
        dict(kind='poly', color='black', smooth=0, pts=KIDNEY, offset=-1.55,
             relief=dict(type='hbars', pitch=1.8, rib=0.8, offset=1.5)),
        # centre lower intake (wide trapezoid) with coarse honeycomb
        dict(kind='poly', color='black', smooth=1,
             pts=[(-12, 12.9), (15.6, 12.9), (17.4, 12.2), (20.2, 5.0), (19.4, 4.3), (-12, 4.3)],
             relief=dict(type='hex', pitch=3.2, rib=0.9, offset=0.8)),
        # outer intakes (huge, pointing up and in toward the kidneys) with horizontal fins
        dict(kind='poly', color='black', smooth=1,
             pts=[(22.2, 15.2), (24.0, 17.0), (36.4, 18.6), (36.4, 6.8), (35.0, 5.0), (24.8, 4.7)],
             relief=dict(type='hbars', pitch=3.0, rib=1.0, offset=1.0)),
        # air curtains (vertical slits at the corners)
        dict(kind='poly', color='black', pts=[(37.9, 10.0), (38.8, 10.3), (39.0, 19.6), (38.1, 19.3)]),
        # lower lip / splitter: thinner in the middle, deeper and wrapping at the corners
        dict(kind='poly', color='black',
             pts=[(-1, -1), (-1, 2.5), (14, 2.6), (26, 2.9), (34, 3.4), (36.4, 3.8), (38.4, 5.4), (39.0, 6.3),
                  (41, 6.3), (41, -1)]),
    ],
    badge=None,
    tab=dict(y_mm=21.5),
)
