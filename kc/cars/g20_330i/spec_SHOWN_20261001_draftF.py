# BMW 330i M Sport (G20, pre-LCI 2019-2022) front keychain.
# Reference: BMW Group PressClub photo P90332472 "The all-new BMW 330i, Model M Sport, Portimao blue metallic,
# Rim 19" Styling 791 M (12/2018)", https://www.press.bmwgroup.com/global/photo/detail/P90332472  (c) BMW AG,
# press/editorial image, used only as a private tracing reference.
# ref/front.jpg = crop (1150,1050)-(3800,2700) of the 4961x3307 HighRes original, scaled 0.55 (1457x907).
# The photo is level and centred (mirror blend at x=725 matches). Traced half = viewer's left (car's right).
# NO LOGOS (user rule): badge=None, the roundel spot on the hood stays plain body.

CX = 725
OFF = 2.0

OUTLINE = [(725, 265), (560, 265), (420, 266), (300, 267), (240, 268), (222, 271), (206, 279), (195, 288), (184, 300),
           (171, 316), (156, 334), (137, 353), (114, 373), (96, 389), (84, 406), (78, 428), (75, 470), (74, 540),
           (75, 620), (77, 700), (77, 755), (81, 774), (92, 787), (115, 795), (200, 797), (330, 798), (342, 803),
           (352, 817), (380, 821), (500, 823), (725, 824)]

# headlight lens (black), with the characteristic notch in the lower edge between the two DRL elements
HEADLIGHT = [(110, 452), (108, 430), (117, 411), (134, 401), (165, 401), (250, 410), (330, 420), (386, 430),
             (397, 440), (400, 470), (397, 508), (330, 508), (262, 506), (260, 480), (238, 480), (235, 499),
             (175, 499), (134, 491), (116, 474)]

# pre-LCI DRL: two "L" elements, each with the angled notch at its top end
DRL_OUTER = [(152, 416), (133, 435), (134, 452), (140, 466), (152, 476), (172, 481), (226, 481)]
DRL_INNER = [(288, 430), (269, 448), (270, 463), (277, 477), (290, 487), (312, 491), (386, 491)]

# kidney opening (inside the chrome surround, which stays white)
KIDNEY = [(706, 432), (699, 419), (682, 412), (600, 408), (500, 408), (440, 413), (420, 422), (412, 437),
          (414, 456), (425, 478), (443, 502), (468, 524), (500, 537), (560, 541), (640, 541), (684, 537),
          (700, 527), (706, 508)]
# outer edge of the chrome kidney surround (engraved)
# kept >= 0.8 mm of white chrome between the groove and the kidney black; halves meet flat at the centre
KIDNEY_FRAME = [(725, 389), (712, 388), (650, 386), (540, 386), (460, 390), (418, 401), (399, 414)]
KIDNEY_FRAME_LOW = [(400, 474), (418, 500), (446, 528), (480, 551), (530, 560), (620, 561), (690, 558), (712, 554), (725, 551)]

# outer intake (smoked fog-light housing + lower mesh)
OUTER_INTAKE = [(112, 600), (116, 588), (126, 582), (160, 580), (225, 582), (255, 590), (280, 615), (302, 652),
                (318, 690), (324, 715), (318, 732), (300, 740), (240, 748), (170, 755), (130, 753), (114, 744),
                (110, 720)]
FOG = [(178, 662), (268, 662)]

# trapezoid centre intake (hex mesh), two slanted blades, radar panel in the middle
CENTRE_INTAKE = [(745, 646), (345, 646), (352, 668), (366, 698), (382, 726), (400, 748), (428, 764), (480, 771),
                 (745, 772)]
BLADE = [(434, 638), (502, 778)]
# hex mesh area = slightly oversized centre intake (clipped by the black); radar panel dropped (low contrast on the car)
MESH = [(725, 640)] + [(339, 640), (346, 668), (360, 700), (377, 729), (396, 753), (426, 769), (480, 778)] + \
       [(725, 778)]

LIP = [(342, 792), (400, 788), (725, 788), (725, 840), (342, 840)]

SPEC = dict(
    id='g20_330i', name='BMW 330i M Sport (G20)',
    ref='kc/cars/g20_330i/ref/front.jpg',
    units='px', px_left=74, px_right=1375, px_bottom=824, center_x=CX,
    outline_half=OUTLINE,
    prims=[
        # grooves first (black parts painted later cover their ends)
        dict(kind='stroke', color='groove', width=0.65, smooth=2,
             pts=[(236, 292), (214, 304), (199, 322), (189, 345), (186, 372), (186, 398)]),    # hood shut line
        dict(kind='stroke', color='groove', width=0.65, smooth=1,
             pts=[(436, 292), (452, 330), (464, 368), (468, 388)]),                         # hood crease to kidney
        dict(kind='stroke', color='groove', width=0.65, smooth=2, pts=KIDNEY_FRAME),
        dict(kind='stroke', color='groove', width=0.65, smooth=2, pts=KIDNEY_FRAME_LOW),
        # headlight + DRL
        dict(kind='poly', color='black', pts=HEADLIGHT, smooth=1),
        dict(kind='stroke', color='white', width=0.68, cap='flat', pts=DRL_OUTER),
        dict(kind='stroke', color='white', width=0.68, cap='flat', pts=DRL_INNER),
        # kidneys with vertical bars
        dict(kind='poly', color='black', pts=KIDNEY, smooth=1, relief=dict(type='vbars', pitch=2.3, rib=1.1, offset=1.15)),
        # outer intakes
        dict(kind='poly', color='black', pts=OUTER_INTAKE, smooth=1),
        dict(kind='stroke', color='white', width=0.9, cap='flat', pts=FOG),
        # centre intake
        dict(kind='poly', color='black', pts=CENTRE_INTAKE),
        dict(kind='poly', color='relief', pts=MESH, relief=dict(type='hex', pitch=3.0, rib=0.85, offset=OFF)),
        dict(kind='stroke', color='white', width=0.7, cap='flat', pts=BLADE),
        # lower lip
        dict(kind='poly', color='black', pts=LIP),
        # single front tow-hook cover (viewer's left only)
        dict(kind='ring', color='black', c=(410, 592), r_mm=1.5, width=0.6, mirror=False),
    ],
    badge=None,
    tab=dict(y_frac=0.5),
)
