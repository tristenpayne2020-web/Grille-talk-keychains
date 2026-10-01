# BMW X4 M Competition (F98 LCI, 2022+) - traced on BMW Group press photo P90466622 (Sao Paulo Yellow, straight front).
# Left (viewer's) half traced, mirrored about x=1176. NO LOGOS (user rule): no roundel, no badges.
# Revision 1: twin square-ish kidneys with white centre bridge + paired M slats, pointed lamp with long L DRLs,
# centre intake with horizontal cooler slats either side of a flush radar plate.
# relief opening (walls placed in the slat phase so no slivers appear); the frame is this grown by 0.8 mm
KIDNEY = [(1158, 896), (1158, 792), (1155, 789), (962, 789), (955, 796), (955, 903), (964, 912), (1100, 912),
          (1140, 907)]
SLAT = dict(type='vbars', pitch=3.4, rib=0.7)
SPEC = dict(
    id='x4m', name='BMW X4 M Competition (F98 LCI)',
    ref='kc/cars/x4m/ref/press_P90466622.jpg',
    units='px', px_left=734, px_right=1618, center_x=1176, px_bottom=1110,
    outline_half=[(1176, 679), (1000, 679), (880, 680), (855, 683), (836, 692), (824, 702), (808, 716), (790, 736), (772, 756),
                  (756, 776), (745, 800), (737, 830), (734, 870), (734, 950), (736, 1010), (741, 1045), (750, 1072),
                  (766, 1092), (792, 1104), (840, 1108), (1000, 1110), (1176, 1110)],
    prims=[
        # ---- headlight unit (black): slim LCI lens, upper edge rising outward, pointed inner end; white rim at fender
        dict(kind='poly', color='black', smooth=1, pts=[(762, 786), (770, 772), (790, 765), (850, 776), (900, 788), (928, 798),
             (941, 813), (924, 834), (898, 846), (850, 851), (790, 850), (766, 845), (756, 830), (753, 806)]),
        # ---- DRL: two L-shaped light guides (vertical + long bottom bar, short top return)
        dict(kind='stroke', color='white', width=0.9, pts=[(792, 800), (776, 803), (776, 834), (826, 834)]),
        dict(kind='stroke', color='white', width=0.9, pts=[(856, 800), (841, 803), (841, 834), (896, 834)]),
        # ---- twin kidneys: slim flush black frame, recessed openings with paired vertical M slats
        dict(kind='poly', color='black', offset=0.8, pts=KIDNEY),
        dict(kind='poly', color='relief', pts=KIDNEY, relief=dict(SLAT, offset=0.7)),
        dict(kind='poly', color='relief', pts=KIDNEY, relief=dict(SLAT, offset=-0.7)),
        # ---- big central lower intake (black), V-shaped top under the plate
        dict(kind='poly', color='black', pts=[(1176, 1000), (1010, 1000), (920, 950), (902, 968), (878, 1040), (890, 1055),
             (940, 1080), (1176, 1080)]),
        # cooler with horizontal slats either side of the flush radar plate (centre left plain black)
        dict(kind='poly', color='relief', pts=[(1138, 1011), (1004, 1011), (1004, 1069), (1138, 1069)],
             relief=dict(type='hbars', pitch=1.6, rib=0.7)),
        # ---- outer vertical intakes, running down into the splitter
        dict(kind='poly', color='black', pts=[(757, 900), (786, 898), (800, 912), (800, 1005), (812, 1028), (865, 1056),
             (930, 1090), (938, 1100), (835, 1100), (760, 1042)]),
        # ---- splitter (black)
        dict(kind='poly', color='black', pts=[(1176, 1094), (840, 1095), (795, 1095), (775, 1086), (762, 1072), (756, 1050), (758, 1040), (720, 1040), (720, 1120), (1176, 1120)]),
        # ---- parking sensors (real PDC sensors flank the plate in the photo at x~1013/1339, y~977)
        dict(kind='ring', color='black', c=(1012, 975), r_mm=0.9, width=0.5),
        # ---- hood shut lines (grooves), running into the headlight
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(848, 702), (832, 712), (812, 730), (802, 752), (799, 780)]),
        # hood power-dome lines (no top bar: they converge slightly towards the cowl and fade out)
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[(1012, 704), (1003, 730), (1000, 750), (1001, 767)]),
    ],
    badge=None,
    tab=dict(y_frac=0.53),
)
