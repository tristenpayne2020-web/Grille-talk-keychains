# Ferrari SF90 Stradale (2019+) front keychain.
# NO reference photo: every image host (Wikimedia Commons, Pexels, CarDekho, ...) is blocked by this cloud run's
# egress proxy, so the design is drawn directly in mm (units='mm', x = -40.25..40.25, y up, 0 = splitter bottom)
# from the car's known front-view proportions (1972 mm wide, very low nose). Traced half = viewer's LEFT (x < 0).
#
# Design (G80 language):
#  outline  - flat cowl at the centre rising gently into the two fender crowns over the headlights, fender sides
#             straight down, bumper corners tucking into the splitter. Tyres/mirrors/windscreen dropped.
#  black    - slim wedge headlights at the upper outer corners (inner tip lower), the full-width lower mouth,
#             the two outer side intakes under the headlights (split from the mouth by a diagonal white fin),
#             the full-width splitter.
#  white on black - the C-shaped LED signature: upper arm along the lamp top, bending down round the outer end and
#             back inboard as a shorter lower arm (0.7 mm). The central splitter blade: a body-colour bar across the
#             middle of the mouth.
#  relief   - mouth: honeycomb mesh; side intakes: horizontal radiator slats.
#  grooves  - front-hood shut line (cowl -> past the headlight tips -> across the nose = one big U when mirrored),
#             plus the two ridges of the central hood channel converging toward the nose.
#  badge    - none (user rule: no logos); the nose spot stays plain body.
#  tab      - viewer's left, y_frac 0.60 (white fender between headlight and side intake).

SPEC = dict(
    id='ferrari_sf90', name='Ferrari SF90 Stradale',
    ref=None,
    units='mm',
    # rev 1: deeper centre dip (cowl 28.0 vs crowns 31.0) and tighter upper corners / tucked bumper corners
    outline_half=[(0, 28.0), (-10, 28.2), (-18, 29.0), (-24, 30.3), (-29, 31.0), (-33, 30.8),
                  (-37.0, 29.4), (-39.3, 27.0), (-40.0, 24.5), (-40.25, 21.0), (-40.15, 14.0),
                  (-39.4, 8.5), (-38.7, 5.3), (-38.2, 3.2), (-37.7, 1.8), (-36.9, 0.8), (-35.0, 0.3),
                  (-20.0, 0.05), (0, 0)],
    outline_smooth=2,
    prims=[
        # splitter (full width)
        dict(kind='poly', color='black', pts=[(0.5, -1), (-39, -1), (-38.9, 2.9), (-36, 2.15),
                                              (-25, 1.95), (0.5, 1.9)]),
        # lower mouth (crosses the centreline -> unioned with its mirror); calm horizontal slats like the G80
        dict(kind='poly', color='black', smooth=2,
             pts=[(8, 11.0), (0, 11.0), (-8, 11.0), (-15, 11.2), (-20, 11.8), (-24, 12.6), (-26.0, 13.1), (-27.3, 12.5),
                  (-26.2, 7.5), (-24.8, 2.85), (0, 2.85), (8, 2.85)],
             relief=dict(type='hbars', pitch=1.4, rib=0.7, margin=0.6, offset=0.6)),
        # outer side intakes: narrower, more vertical, tucked under the lamp; fine vertical fins
        dict(kind='poly', color='black', smooth=2,
             pts=[(-30.5, 16.0), (-33, 17.9), (-36, 18.7), (-37.9, 17.7), (-38.2, 12.0),
                  (-37.7, 6.5), (-36.6, 3.9), (-29.5, 3.75)],
             relief=dict(type='vbars', pitch=1.8, rib=0.7, margin=0.8)),
        # central splitter blade (body colour): thick wing anchored to the mouth bottom by an end plate
        dict(kind='stroke', color='white', width=1.8, cap='round', smooth=2,
             pts=[(0, 6.25), (-8, 6.25), (-15, 6.3), (-20.0, 6.35), (-21.6, 5.6), (-22.6, 3.4)]),
        # headlight: slim even blade sweeping up and outward, blunted inner tip
        dict(kind='poly', color='black', smooth=1,
             pts=[(-18.3, 20.5), (-24, 22.6), (-30, 24.6), (-35, 25.85), (-37.8, 25.75), (-39.1, 24.6),
                  (-39.1, 22.5), (-37.4, 21.5), (-32, 20.7), (-26, 20.1), (-21.5, 19.8), (-18.8, 19.8)]),
        # C-shaped LED signature: long upper arm, round turn at the outer end, shorter lower arm
        dict(kind='stroke', color='white', width=0.9, smooth=2,
             pts=[(-25.0, 21.45), (-30, 23.2), (-35, 24.45), (-37.2, 24.6), (-38.0, 24.0), (-37.9, 23.1),
                  (-37.0, 22.75), (-32, 21.95), (-30.0, 21.65)]),
        # front-hood shut line: shallower, wider U ending at the nose
        dict(kind='stroke', color='groove', width=0.65, smooth=2,
             pts=[(-13, 28.9), (-15.0, 25.0), (-16.4, 21.0), (-16.0, 18.0), (-12.5, 16.0), (-6, 15.5), (0, 15.5)]),
        # central hood channel: two parallel ridges, stopping short of the cowl and the U bottom
        dict(kind='stroke', color='groove', width=0.65, cap='round',
             pts=[(-3.2, 26.5), (-3.2, 17.0)]),
    ],
    badge=None,
    tab=dict(y_frac=0.65),
)
