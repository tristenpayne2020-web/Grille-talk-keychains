# Lexus IS 350 F Sport (XE30 facelift, 2021+) front keychain.
# Reference: ref/front.jpg = Lexus pressroom photo "2021-Lexus-IS-F-SPORT-013" (2560 x 1707, studio, straight-on,
# camera at headlight height, level). See ref/SOURCE.txt. Traced half = viewer's LEFT. Photo pixels (1 mm = 26.7 px).
# Centreline 1276 px = centre of the grille corners / badge (the body sides read ~7 px wider on the left because of a
# tiny yaw; the side outline and lamp corner were traced ~6 px inboard to split the difference).
#
# Design (G80 language), revision 1:
#  black  = slim headlamp units with their sharp inner tips, the spindle grille (hourglass, runs down into the gloss
#           lower lip), the corner intakes + gloss blades, the full-width lower lip, parking-sensor rings, badge field.
#  white  = body paint incl. the body-colour "fangs" (knife tips reaching down to the lip) and the outer bumper strips;
#           light signature = one tapering DRL blade under the lens top (0.64 -> ~1.05 mm) ending in the inner
#           arrowhead: the upper barb is split off by a 0.6 mm parallel-sided slot, so the check shape survives printing.
#  relief = F Sport mesh: two rib families at +-24 deg (pitch 2.0, rib 0.7) -> long flat diamonds (4.9 x 2.2 mm cells,
#           like the real 4.9 x 1.8), inside a 0.8 mm flat gloss-black frame (the real spindle surround); a node of the
#           lattice sits on the centreline under the badge. Below the mesh: one flat horizontal slat (the frame) and a
#           plain recessed slot, then the gloss lip - the 2021 lower-grille band. Corner intakes: fins at 32 deg
#           (pitch 1.8, rib 0.7) inside a 0.6 mm gloss frame.
#  grooves (0.62) = hood front shut line over the grille brow, hood/fender shut lines, and the hood-side creases that
#           run from the A-pillar base to the headlamp inner corners, meeting the hood line in one point there.
#           They are painted first, so the lamp black trims their round caps at the lamp edge.
#  badge  = simplified Lexus emblem (white 0.62 mm oval ring, black field, white slanted-stem L, 0.7 mm flat black
#           collar) behind SHOW_BADGE (or KC_BADGE=0 for a badge-free export).
import os, sys, math
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

SHOW_BADGE = True
if os.environ.get('KC_BADGE', '').strip().lower() in ('0', 'false', 'no', 'off'):
    SHOW_BADGE = False

CX, YB, XL = 1276, 1352, 201           # centreline, splitter bottom, body edge (left)
S = 80.5 / (2 * (CX - XL))              # mm per px


def mm(p):
    return ((p[0] - CX) * S, (YB - p[1]) * S)


def mir(pts):
    """left-half px points -> the right-half px points (mirror about CX)"""
    return [(2 * CX - x, y) for x, y in pts]


OUTLINE = [(1276, 455), (900, 455), (700, 457), (610, 461), (545, 470), (485, 486), (432, 506),
           (380, 524), (335, 544), (297, 566), (270, 590), (251, 614), (238, 640), (228, 670), (221, 700),
           (214, 745), (208, 800), (204, 860), (201, 920), (201, 1000), (203, 1080), (207, 1160), (210, 1240),
           (213, 1300), (216, 1328), (224, 1344), (245, 1352), (1276, 1352)]

HEADLIGHT = [(268, 651), (682, 717), (722, 752), (762, 788), (792, 819), (760, 815), (700, 809), (560, 808),
             (400, 808), (340, 806)]
# DRL (one white poly): tapering blade under the lens top (top edge 12.7 deg, bottom edge 14.6 deg) that ends in the
# inner arrowhead. The barb (upper part of the head) runs 0.6 mm under the lens edges; a 0.6 mm wide parallel-sided
# slot at 44 deg separates it from the blade (mouth between the barb tip and the blade top, flat inner end).
# Points computed in w3/drl_explore.py: drl(phi=44, xa=638, L=36, K=(682,787)).
DRL = [(322, 677),                       # outer end, top
       (637.7, 748.2),                   # blade top meets the slot's lower side
       (652.8, 762.7), (663.9, 751.2),   # slot inner end (flat, 0.6 mm)
       (638.0, 726.2),                   # barb tip (slot upper side meets the barb top)
       (674.9, 732.1),                   # barb top corner (0.6 mm under the lens top / inner edges)
       (734, 791),                       # arrowhead tip
       (682, 787),                       # blade bottom edge
       (322, 694)]                       # outer end, bottom (square end, 0.64 mm)

GRILLE = [(1276, 713), (774, 713), (790, 735), (815, 770), (840, 805), (856, 830), (845, 848), (820, 880),
          (790, 915), (755, 950), (720, 990), (688, 1030), (660, 1070), (638, 1110), (620, 1155), (605, 1205),
          (592, 1245), (583, 1270), (642, 1336), (650, 1400), (1276, 1400)]
# relief zones run 30 px past the centreline so the -0.8 mm frame offset (applied before mirroring) leaves no seam.
# Their flat top/bottom edges (716 / 1236 px) were picked with w3/phase_search.py so the lattice meets the frame
# without rib slivers (the top frame is 0.9 mm, the slat between mesh and slot 0.8 mm).
MESH_ZONE = [(1306, 716), (776.2, 716)] + GRILLE[2:16] + [(595, 1236), (1306, 1236)]   # mesh above the lower band
SLOT_ZONE = [(1306, 1215), (602, 1215), (592, 1245), (583, 1270), (615, 1306), (1306, 1306)]   # lower-grille slot

INTAKE = [(332, 947), (362, 972), (400, 1030), (430, 1085), (440, 1118), (438, 1200), (434, 1288), (532, 1322),
          (642, 1336), (650, 1400), (190, 1400), (190, 1328), (240, 1328), (247, 1290), (252, 1260), (265, 1170),
          (285, 1070), (310, 985)]
FIN_ZONE = [(332, 947), (362, 972), (400, 1030), (430, 1085), (440, 1118), (438, 1200), (434, 1288), (247, 1288),
            (252, 1260), (265, 1170), (285, 1070), (310, 985)]

HOOD_LINE = [(681, 719), (700, 697), (720, 680), (745, 669), (780, 662), (840, 659), (960, 654), (1100, 651), (1276, 649)]
FENDER_LINE = [(383, 670), (391, 611), (402, 561), (413, 533), (440, 505)]
CREASE = [(505, 476), (530, 515), (560, 565), (594, 620), (630, 670), (679, 719)]

# F Sport mesh: +-24 deg, pitch 2.0, rib 0.7. Phase: put a rib crossing on the centreline just under the badge
# (0.3 mm inside the collar's lower edge), so the lattice centres on the emblem. Nodes on x=0 sit at cy + (offset + i*pitch)/cos(angle),
# cy = centre of the relief region's bounding box.
MESH_A, MESH_P, MESH_R, MESH_FRAME = 24.0, 2.0, 0.7, 0.8
BADGE_C = mm((1276, 837))
BADGE_RX, BADGE_RY, BADGE_RING, BADGE_COLLAR = 3.8, 2.6, 0.62, 0.7
_zb = Polygon([mm(p) for p in MESH_ZONE]).buffer(-MESH_FRAME).bounds
_cy = (_zb[1] + _zb[3]) / 2
_node_y = BADGE_C[1] - BADGE_RY - BADGE_COLLAR + 0.3
MESH_OFF = ((_node_y - _cy) * math.cos(math.radians(MESH_A))) % MESH_P
MESH = dict(type='bars', pitch=MESH_P, rib=MESH_R, offset=MESH_OFF)

prims = [
    # grooves first: the lamp black painted afterwards trims their round caps exactly at the lamp edge
    dict(kind='stroke', color='groove', width=0.62, pts=HOOD_LINE),
    dict(kind='stroke', color='groove', width=0.62, pts=FENDER_LINE),
    dict(kind='stroke', color='groove', width=0.62, pts=CREASE, smooth=1),
    dict(kind='poly', color='black', pts=HEADLIGHT),
    dict(kind='poly', color='white', pts=DRL),
    dict(kind='poly', color='black', pts=GRILLE),
    dict(kind='poly', color='black', pts=INTAKE),
    # F Sport mesh (two families) inside a flat black frame
    dict(kind='poly', color='relief', pts=MESH_ZONE, offset=-MESH_FRAME, relief=dict(MESH, angle=MESH_A)),
    dict(kind='poly', color='relief', pts=MESH_ZONE, offset=-MESH_FRAME, relief=dict(MESH, angle=-MESH_A)),
    # lower-grille band: the frame above it is the flat slat, below it a plain recessed slot
    dict(kind='poly', color='relief', pts=SLOT_ZONE, offset=-MESH_FRAME, relief=dict(type='none')),
    # corner intake fins (slope down towards the car centre, mirrored by hand) inside a 0.6 mm gloss frame
    dict(kind='poly', color='relief', pts=FIN_ZONE, mirror=False, offset=-0.6,
         relief=dict(type='bars', angle=-32, pitch=1.8, rib=0.7, offset=0.15)),
    dict(kind='poly', color='relief', pts=mir(FIN_ZONE), mirror=False, offset=-0.6,
         relief=dict(type='bars', angle=32, pitch=1.8, rib=0.7, offset=0.15)),
    dict(kind='ring', color='black', c=(318, 877), r_mm=1.1, width=0.6),
]


# ------------------------------------------------------------------ Lexus badge: white L in a white oval, black field
def lexus_badge():
    cx, cy = BADGE_C
    E = lambda rx, ry: affinity.scale(Point(cx, cy).buffer(1.0, 128), rx, ry)
    outer = E(BADGE_RX, BADGE_RY)
    inner = outer.buffer(-BADGE_RING, 128)                  # constant-width chrome ring
    collar = outer.buffer(BADGE_COLLAR, 128)
    # L (traced on the photo, mm from the badge centre): slanted stem, wide at the top where it runs into the ring,
    # and a flat foot whose left end meets the stem's lower-left corner and whose right end runs into the ring
    # (stem edges keep the photo's slopes, dx/dy 0.65 left and 1.08 right; the L's corner sits where the photo has it,
    # the foot is ~0.35 mm higher than on the car so the black crescent under it stays >= 0.55 mm and the field
    # wraps round the L's corner as on the real emblem)
    stem = Polygon([(cx + 0.93, cy + 2.7), (cx + 3.14, cy + 2.7), (cx - 0.30, cy - 0.48), (cx - 1.55, cy - 1.10)])
    foot = Polygon([(cx - 1.55, cy - 1.10), (cx + 3.6, cy - 1.10), (cx + 3.6, cy - 0.48), (cx - 1.145, cy - 0.48)])
    L = unary_union([stem, foot]).intersection(outer)
    # where the L meets the ring at a shallow angle the black field pinches to a wedge: fill every part of the field
    # narrower than 0.52 mm (the foot then joins the ring a little earlier, as on the real emblem)
    field = inner.difference(L)
    kept = field.buffer(-0.26, 64).buffer(0.26, 64)
    L = unary_union([L, inner.difference(kept)]).intersection(outer)
    return [dict(kind='geom', color='white', geom=collar, mirror=False),   # removes the mesh under the collar ...
            dict(kind='geom', color='black', geom=collar, mirror=False),   # ... and repaints it flat black
            dict(kind='geom', color='white', geom=outer, mirror=False),
            dict(kind='geom', color='black', geom=inner, mirror=False),
            dict(kind='geom', color='white', geom=L, mirror=False)]


if SHOW_BADGE:
    prims += lexus_badge()

SPEC = dict(
    id='lexus_is350', name='Lexus IS 350 F Sport (XE30 FL)',
    ref='kc/cars/lexus_is350/ref/front.jpg',
    units='px', px_left=XL, px_right=2 * CX - XL, px_bottom=YB, center_x=CX,
    outline_half=OUTLINE,
    prims=prims,
    tab=dict(y_frac=0.56),
)
