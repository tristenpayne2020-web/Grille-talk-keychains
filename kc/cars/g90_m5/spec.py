# BMW M5 (G90, 2025+) front keychain.
# PROVISIONAL DESIGN WITHOUT A REFERENCE PHOTO: the cloud container's egress proxy blocked every image host
# (Wikimedia, BMW PressClub, motor1, caricos, ...), so this was drawn in keychain millimetres (units='mm',
# x = 0 at the centreline, y up, 0 at the bottom of the lip) from the published G90/G60 design description:
#   * large, wide, near-rectangular kidney grille with horizontal slats (optional Iconic Glow contour not drawn)
#   * slim, long headlights whose inner tips reach toward the kidneys; DRL = "two nearly vertical LED elements
#     positioned towards the outside" of each lamp
#   * M bumper: wide centre intake under the kidneys, huge outer intakes, vertical air curtains at the corners,
#     black lower lip; hood with two creases framing the centre power dome
# NO LOGOS (user rule): no roundel / lettering, the spot above the kidneys stays plain body (badge=None).
# The user should re-trace / check this on a real straight-on photo before printing a sale batch.

OUTLINE = [(0, 38.4), (12, 38.3), (21, 37.9), (27, 37.2), (31.5, 36.1), (35.2, 34.6), (37.8, 32.6),
           (39.4, 29.8), (40.2, 26.0), (40.25, 21), (40.0, 14), (39.5, 9), (38.9, 6.2), (39.3, 4.6), (39.2, 2.6),
           (37.8, 1.2), (34, 0.6), (22, 0.2), (0, 0)]

SPEC = dict(
    id='g90_m5', name='BMW M5 (G90)',
    ref=None,
    units='mm',
    outline_half=OUTLINE,
    outline_smooth=1,
    prims=[
        # hood: front shut line above the kidneys + headlights, fender shut lines up to the cowl, two dome creases
        dict(kind='stroke', color='groove', width=0.55, pts=[(0, 30.7), (11.5, 30.9), (15.6, 31.9)]),
        dict(kind='stroke', color='groove', width=0.55, pts=[(35.2, 33.5), (32.8, 35.2), (30.4, 37.6)]),
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(9.0, 38.6), (8.4, 35.5), (6.8, 31.6)]),
        # headlight unit (black): slim wedge, inner tip angled down toward the kidney, outer end wraps the corner
        dict(kind='poly', color='black', smooth=1,
             pts=[(15.0, 27.0), (15.5, 30.6), (16.6, 31.6), (25, 32.2), (33, 33.0), (36.6, 33.6), (38.3, 32.8),
                  (38.9, 31.0), (38.2, 29.0), (35.8, 28.0), (28, 27.3), (20, 26.7), (16.0, 26.5)]),
        # DRL: two nearly vertical LED elements in the outer part of the lamp
        dict(kind='stroke', color='white', width=0.7, cap='round',
             pts=[(28.6, 28.1), (29.3, 31.9)]),
        dict(kind='stroke', color='white', width=0.7, cap='round',
             pts=[(33.0, 28.5), (33.8, 32.6)]),
        # kidney grille (viewer's right kidney, mirrored): big, wide, near-rectangular, slight flare at the bottom
        dict(kind='poly', color='black', smooth=2,
             pts=[(0.75, 15.8), (0.75, 28.0), (1.4, 29.0), (11.8, 29.0), (13.0, 28.0), (14.4, 17.2), (13.8, 15.4),
                  (12.4, 15.0), (1.4, 15.0)],
             relief=dict(type='hbars', pitch=2.5, rib=1.1, offset=0.0)),
        # centre lower intake (wide, trapezoid) with mesh
        dict(kind='poly', color='black', smooth=1,
             pts=[(-12, 12.9), (15.6, 12.9), (17.4, 12.2), (20.2, 5.3), (19.4, 4.7), (-12, 4.7)],
             relief=dict(type='hex', pitch=2.4, rib=0.7)),
        # outer intakes (huge, under the headlights)
        dict(kind='poly', color='black', smooth=1,
             pts=[(21.6, 14.6), (24.0, 17.0), (36.9, 18.6), (37.0, 6.8), (35.4, 5.0), (24.8, 4.9)]),
        # air curtains (vertical slits at the corners)
        dict(kind='poly', color='black', pts=[(37.9, 10.0), (38.7, 10.3), (38.9, 19.6), (38.1, 19.3)]),
        # lower lip / splitter (full width)
        dict(kind='poly', color='black',
             pts=[(-1, -1), (-1, 3.2), (14, 3.3), (28, 3.45), (36.0, 3.7), (38.4, 5.6), (38.9, 6.3), (41, 6.3), (41, -1)]),
    ],
    badge=None,
    tab=dict(y_mm=22.5),
)
