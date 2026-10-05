# Tesla Model S Plaid (2021+ refresh) - straight-on front.
# Reference: kc/cars/tesla_models_plaid/ref/front.jpg (2025 Model S, same front as the 2021+ Plaid;
# carsdirect.com / autodata OEM studio image CDC_2025TSC021982861). Traced on the viewer's LEFT half, mirrored.
# NO LOGOS: the T badge spot in the nose V is plain black trim (badge=None).
from shapely.geometry import box
from shapely.ops import unary_union

# lower intake mesh (keychain mm): 2 horizontal slats + sparse vertical dividers, like the real Plaid mesh
_S = 80.5 / (1689 - 413)
def _ymm(py):
    return (1300 - py) * _S
INTAKE_RIBS = unary_union(
    [box(-40, y - 0.35, 40, y + 0.35) for y in (_ymm(1232) - 0.87, _ymm(1232) + 0.87)] +
    [box(x - 0.35, 0, x + 0.35, 10) for x in (-20, -15, -10, -5, 0, 5, 10, 15, 20)])

SPEC = dict(
    id='tesla_models_plaid', name='Tesla Model S Plaid (2021+)',
    ref='kc/cars/tesla_models_plaid/ref/front.jpg',
    units='px', px_left=413, px_right=1689, px_bottom=1300, center_x=1051,
    outline_half=[
        (1051, 728), (850, 728), (650, 729), (590, 731), (562, 737),        # cowl / hood rear edge
        (520, 778), (470, 825), (435, 858), (418, 882),                    # sloping fender shoulder
        (413, 920), (411, 1000), (412, 1100), (416, 1200), (424, 1250),    # fender / bumper side
        (440, 1276), (470, 1290), (560, 1297), (700, 1299), (1051, 1300),  # bumper bottom
    ],
    prims=[
        # headlight unit (whole lens, black)
        dict(kind='poly', color='black', pts=[
            (461, 869), (520, 876), (580, 893), (630, 915), (670, 945), (700, 975), (714, 984),
            (680, 988), (620, 988), (560, 987), (528, 990), (500, 979), (472, 962), (461, 940), (457, 900)]),
        # DRL light signature: outer 'J' hook running up the outer edge and along the top toward the inner tip
        dict(kind='stroke', color='white', width=0.7, smooth=2, pts=[
            (560, 974), (522, 970), (496, 957), (482, 933), (480, 902), (494, 892),
            (540, 901), (600, 920), (640, 942), (664, 962)]),
        # nose: black gloss trim band between hood and bumper with the central V (badge spot left plain)
        dict(kind='poly', color='black', smooth=1, pts=[
            (752, 1006), (790, 996), (900, 993), (1000, 991), (1070, 991), (1080, 991),
            (1080, 1035), (1051, 1064), (1032, 1046), (1000, 1027), (970, 1018), (900, 1016), (800, 1014), (762, 1013)]),
        # side lamp blade (tapered black slit) + small vertical air-curtain opening under its outer end
        dict(kind='poly', color='black', pts=[
            (446, 1092), (520, 1101), (580, 1128), (626, 1172), (560, 1163), (480, 1154), (452, 1152)]),
        dict(kind='stroke', color='white', width=0.65, pts=[(470, 1112), (520, 1121), (553, 1138)]),   # lamp in the blade
        dict(kind='poly', color='black', pts=[
            (452, 1146), (472, 1150), (477, 1200), (484, 1258), (466, 1262), (456, 1200)]),
        # wide lower intake band with mesh
        dict(kind='poly', color='black', smooth=2, pts=[
            (1090, 1196), (1070, 1196), (720, 1196), (672, 1201), (650, 1222), (650, 1250), (672, 1265), (720, 1268), (1070, 1268), (1090, 1268)],
             relief=dict(type='custom', ribs=INTAKE_RIBS)),
        # dark under-lip below the bumper edge (grounds the shape like the set's splitters)
        dict(kind='poly', color='black', pts=[
            (452, 1268), (480, 1276), (560, 1282), (640, 1284), (700, 1280), (1090, 1279),
            (1090, 1340), (452, 1340)]),
        # hood: fender shut line + soft hood crease (engraved)
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[
            (590, 731), (566, 762), (553, 800), (549, 845), (553, 866)]),
        dict(kind='stroke', color='groove', width=0.55, smooth=2, pts=[
            (614, 762), (640, 808), (672, 858), (706, 912), (736, 960), (750, 988)]),
    ],
    badge=None,
    tab=dict(y_frac=0.55),
)
