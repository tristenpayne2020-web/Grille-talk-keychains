# ROUGH px-format EXAMPLE (quick 10-minute trace of the user's G80 reference photo) - shows the spec format only.
# The real G80 keychain is in kc/style/g80_face_flat.png; match THAT level of care and accuracy, not this sketch.
SPEC = dict(
    id='example_g80_px', name='G80 px example (rough)',
    ref='front.png',
    units='px', px_left=48, px_right=951, px_bottom=541, center_x=495,
    outline_half=[(495,124),(620,127),(760,134),(862,166),(905,198),(935,244),(950,300),(952,400),(946,468),(934,500),
                  (900,520),(700,535),(495,541)],
    prims=[
        # headlight unit (black) and DRL signature (white strokes)
        dict(kind='poly', color='black', pts=[(722,262),(760,240),(830,224),(900,216),(922,230),(926,262),(906,290),(840,297),(760,292),(728,281)]),
        dict(kind='stroke', color='white', width=0.7, pts=[(790,286),(803,266),(848,258),(857,272),(846,289)]),
        dict(kind='stroke', color='white', width=0.7, pts=[(858,258),(900,236),(912,256),(898,284),(868,289)]),
        # kidney grille (black, recessed, horizontal slats); the white centre bridge comes from the gap between halves
        dict(kind='poly', color='black', smooth=1, pts=[(505,248),(600,242),(662,250),(688,298),(700,380),(684,440),(655,494),(608,502),(512,502),(505,480)],
             relief=dict(type='hbars', pitch=2.5, rib=1.2)),
        # lower side intake
        dict(kind='poly', color='black', pts=[(705,425),(812,378),(846,470),(826,492),(720,496)]),
        # splitter lip (full width -> mirror of the right half)
        dict(kind='poly', color='black', pts=[(495,512),(700,508),(900,494),(944,474),(951,496),(930,528),(700,540),(495,544)]),
        # hood shut line + fender line (engraved)
        dict(kind='stroke', color='groove', width=0.55, pts=[(495,200),(600,205),(720,222),(820,228)]),
        dict(kind='stroke', color='groove', width=0.55, pts=[(862,168),(890,215)]),
        # parking sensor
        dict(kind='ring', color='black', c=(885,383), r_mm=1.0, width=0.5),
    ],
    badge=dict(type='roundel', c=(495,236), d=3.6),
    tab=dict(y_frac=0.55),
)
