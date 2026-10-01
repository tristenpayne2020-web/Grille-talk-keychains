"""2D colour maps -> 3D parts for the two constructions, plus STL / STEP export.

CLASSIC  (identical construction to the user's G80): white body with full-depth black inlays (every layer carries
         both colours -> one filament swap per layer). Grille/relief: black floor 1.0 mm, ribs to the face with a
         0.4 mm stepped chamfer. Grooves: 0.6 mm deep in the face.
PRODUCTION ("1-swap"): black base 0 -> HB for the whole outline, white cap HB -> T only where the face is white.
         Black details are recessed (HB below the face) and the grooves cut through the white to the black, so the
         front shows the same two-colour pattern with added depth. Relief: pocket in the black down to HF with ribs
         back up to HB. Exactly ONE black->white swap per plate, whatever the number of keychains.
All z levels sit on the 0.2 mm layer grid.
"""
import numpy as np, trimesh
import manifold3d as m3d
from shapely.geometry import Polygon
from shapely.ops import unary_union
from geom import polys, clean, T

HB = 1.6          # production: top of the black base
HF = 0.6          # production: floor of relief pockets
CL_FLOOR = 1.0    # classic: relief floor (G80 grille backing = 1.0 mm)
CL_GROOVE = 0.6   # classic: groove depth
CL_CHAMFER = 0.4  # classic: rib top chamfer (stepped, 2 x 0.2 mm)


def cross_section(g):
    if g is None or g.is_empty:
        return None
    contours = []
    for p in polys(g):
        p = p.buffer(0)
        if p.is_empty or p.area < 1e-6:
            continue
        for pp in polys(p):
            ext = np.asarray(pp.exterior.coords)[:-1]
            if Polygon(ext).exterior.is_ccw is False:
                ext = ext[::-1]
            contours.append(ext)
            for h in pp.interiors:
                hh = np.asarray(h.coords)[:-1]
                if Polygon(hh).exterior.is_ccw:
                    hh = hh[::-1]
                contours.append(hh)
    if not contours:
        return None
    return m3d.CrossSection(contours, m3d.FillRule.Positive)


def slab(g, z0, z1):
    cs = cross_section(g)
    if cs is None or z1 - z0 < 1e-6:
        return None
    return m3d.Manifold.extrude(cs, z1 - z0).translate((0, 0, z0))


def union(ms):
    ms = [m for m in ms if m is not None and not m.is_empty()]
    if not ms:
        return None
    out = ms[0]
    for m in ms[1:]:
        out = out + m
    return out


def to_trimesh(m):
    if m is None:
        return None
    mesh = m.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=True)
    return tm


def build_production(M, hb=HB, hf=HF, t=T):
    O, W, R, P = M['outline'], M['white'], M['relief_region'], M['relief_ribs']
    O = O.difference(M['hole'])
    base = union([slab(O.difference(R), 0, hb), slab(R, 0, hf), slab(P, hf, hb)])
    cap_region = W.difference(M['grooves_white'])
    cap = slab(cap_region, hb, t)
    slabs = {'black': [(O.difference(R), 0, hb), (R, 0, hf), (P, hf, hb)], 'white': [(cap_region, hb, t)]}
    return {'black': base, 'white': cap}, slabs


def build_classic(M, t=T, floor=CL_FLOOR, gd=CL_GROOVE, ch=CL_CHAMFER):
    O, W, B, R, P = M['outline'], M['white'], M['black'], M['relief_region'], M['relief_ribs']
    Gw, Gb = M['grooves_white'], M['grooves_black']
    hole = M['hole']
    W, B = W.difference(hole), B.difference(hole)
    white_sl = [(W.difference(Gw), 0, t), (Gw, 0, t - gd)]
    Bflat = B.difference(R)
    black_sl = [(Bflat.difference(Gb), 0, t), (Gb, 0, t - gd), (R, 0, floor)]
    if not P.is_empty:
        s1, s2 = P.buffer(-ch / 2, join_style=2), P.buffer(-ch, join_style=2)
        if s2.area > 0.3 * P.area:          # ribs wide enough (>= ~1.2 mm) for the G80-style chamfered tops
            black_sl += [(P, floor, t - ch), (s1, t - ch, t - ch / 2), (s2, t - ch / 2, t)]
        else:
            black_sl += [(P, floor, t)]
    white = union([slab(g, a, b) for g, a, b in white_sl])
    black = union([slab(g, a, b) for g, a, b in black_sl])
    return {'black': black, 'white': white}, {'black': black_sl, 'white': white_sl}


def check_parts(parts):
    """Watertight, no overlap between colours."""
    rep = {}
    b, w = parts['black'], parts['white']
    rep['black_volume'] = round(b.volume(), 2) if b else 0
    rep['white_volume'] = round(w.volume(), 2) if w else 0
    if b and w:
        rep['overlap_volume'] = round((b ^ w).volume(), 4)
    return rep


# ----------------------------------------------------------------------------------------------- STEP (OCC)
def export_step(slabs, path, name='keychain'):
    """Coloured STEP (white + black bodies) built from exact polygon prisms, so it opens as clean B-rep bodies in
    Fusion 360 like the original."""
    from OCP.gp import gp_Pnt, gp_Vec
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.TopTools import TopTools_ListOfShape
    from OCP.TopoDS import TopoDS_Compound
    from OCP.BRep import BRep_Builder
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.STEPCAFControl import STEPCAFControl_Writer
    from OCP.STEPControl import STEPControl_AsIs
    from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen
    from OCP.TDocStd import TDocStd_Document
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
    from OCP.TDataStd import TDataStd_Name
    from OCP.Interface import Interface_Static

    def wire(coords, z):
        mp = BRepBuilderAPI_MakePolygon()
        for x, y in coords[:-1]:
            mp.Add(gp_Pnt(float(x), float(y), float(z)))
        mp.Close()
        return mp.Wire()

    def prism(poly, z0, z1):
        from shapely.geometry.polygon import orient
        poly = orient(poly, 1.0)                        # exterior CCW, holes CW
        f = BRepBuilderAPI_MakeFace(wire(list(poly.exterior.coords), z0), True)
        for h in poly.interiors:
            f.Add(wire(list(h.coords), z0))
        return BRepPrimAPI_MakePrism(f.Face(), gp_Vec(0, 0, z1 - z0)).Shape()

    def body(sl):
        shapes = []
        for g, z0, z1 in sl:
            if g is None or g.is_empty or z1 - z0 < 1e-6:
                continue
            for p in polys(g.simplify(0.002)):
                if p.area > 1e-4:
                    shapes.append(prism(p, z0, z1))
        if not shapes:
            return None
        if len(shapes) == 1:                 # a fuse with no tools returns a null shape
            return shapes[0]
        args = TopTools_ListOfShape(); tools = TopTools_ListOfShape()
        args.Append(shapes[0])
        for s in shapes[1:]:
            tools.Append(s)
        fu = BRepAlgoAPI_Fuse(); fu.SetArguments(args); fu.SetTools(tools); fu.SetRunParallel(True); fu.Build()
        sh = fu.Shape()
        u = ShapeUpgrade_UnifySameDomain(sh, True, True, True); u.Build()
        return u.Shape()

    doc = TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    cols = {'white': (0.972, 0.969, 0.957), 'black': (0.098, 0.098, 0.098)}
    for cname in ('white', 'black'):
        sh = body(slabs[cname])
        if sh is None:
            continue
        lab = st.AddShape(sh, False)
        TDataStd_Name.Set_s(lab, TCollection_ExtendedString(f'{name} {cname}'))
        r, g, b = cols[cname]
        c = Quantity_Color(r, g, b, Quantity_TOC_RGB)
        ct.SetColor(lab, c, XCAFDoc_ColorGen); ct.SetColor(lab, c, XCAFDoc_ColorSurf)
    Interface_Static.SetCVal_s('write.step.schema', 'AP214')
    import os, sys
    sys.stdout.flush()
    fd = os.dup(1); nul = os.open(os.devnull, os.O_WRONLY); os.dup2(nul, 1)   # silence OCC's transfer banner
    try:
        w = STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True)
        w.Transfer(doc, STEPControl_AsIs)
        w.Write(path)
    finally:
        os.dup2(fd, 1); os.close(fd); os.close(nul)
    return path


# ---------------------------------------------------------------------------------------------- 3 colours
CL_LIGHT = 1.2    # classic custom-colour: white lights only in the top 1.2 mm, black inlay underneath


def build_production3(M, hb=HB, hf=HF, t=T):
    """Custom body colour, 1-swap style: black base, body-colour cap, white light islands (full cap height, so
    they stay opaque white). Every cap layer carries body + white -> about 8 changes per plate."""
    base, sl = build_production(M, hb, hf, t)
    body = M['white_body'].difference(M['grooves_white'])
    light = M['white_light'].difference(M['grooves_white'])
    parts = {'black': base['black'], 'body': slab(body, hb, t), 'light': slab(light, hb, t)}
    slabs = {'black': sl['black'], 'body': [(body, hb, t)], 'light': [(light, hb, t)]}
    return parts, slabs


def build_classic3(M, t=T, floor=CL_FLOOR, gd=CL_GROOVE, ch=CL_CHAMFER, lh=CL_LIGHT):
    """Custom body colour, classic style: body-colour body with full-depth black inlays; the white lights are the top
    1.2 mm of their inlay (black below)."""
    parts2, sl2 = build_classic(M, t, floor, gd, ch)
    hole = M['hole']
    Wb, Wl = M['white_body'].difference(hole), M['white_light'].difference(hole)
    Gw = M['grooves_white']
    body_sl = [(Wb.difference(Gw), 0, t), (Wb.intersection(Gw), 0, t - gd)]
    light_sl = [(Wl.difference(Gw), t - lh, t), (Wl.intersection(Gw), t - lh, t - gd)]
    black_sl = list(sl2['black']) + [(Wl, 0, t - lh)]
    parts = {'black': union([slab(g, a, b) for g, a, b in black_sl]),
             'body': union([slab(g, a, b) for g, a, b in body_sl]),
             'light': union([slab(g, a, b) for g, a, b in light_sl])}
    return parts, {'black': black_sl, 'body': body_sl, 'light': light_sl}
