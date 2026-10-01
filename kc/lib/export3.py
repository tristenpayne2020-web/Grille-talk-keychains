"""Custom body colour versions (3 filaments): 1 = black details, 2 = BODY colour (change freely in the slicer),
3 = white light signatures / badge details.   usage: python kc/lib/export3.py <spec> <car_out_dir>"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import geom, build3d, render, plate, k2config, write3mf, export
from geom import polys

COLOURS = ['#000000', '#C8102E', '#FFFFFF']          # body sample colour: red (change it to your spool)
FLUSH3 = [0, 670, 670,  200, 0, 670,  200, 300, 0]   # from black / body / white -> to black, body, white (mm3)
PARTS = {'production3': [('Base + details (black)', 'black', 1), ('Body (custom colour)', 'body', 2), ('Lights + badge (white)', 'light', 3)],
         'classic3': [('Body (custom colour)', 'body', 2), ('Inlays (black)', 'black', 1), ('Lights + badge (white)', 'light', 3)]}
SAMPLES = {'red': (0.78, 0.06, 0.18), 'blue': (0.05, 0.25, 0.65), 'yellow': (0.95, 0.75, 0.05), 'grey': (0.55, 0.57, 0.60)}


def export_step3(slabs, path, name, cols):
    """Coloured STEP with an arbitrary set of bodies (copy of build3d.export_step, generalised)."""
    from OCP.gp import gp_Pnt, gp_Vec
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.TopTools import TopTools_ListOfShape
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.STEPCAFControl import STEPCAFControl_Writer
    from OCP.STEPControl import STEPControl_AsIs
    from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen
    from OCP.TDocStd import TDocStd_Document
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
    from OCP.TDataStd import TDataStd_Name
    from OCP.Interface import Interface_Static
    from shapely.geometry.polygon import orient

    def wire(coords, z):
        mp = BRepBuilderAPI_MakePolygon()
        for x, y in coords[:-1]:
            mp.Add(gp_Pnt(float(x), float(y), float(z)))
        mp.Close()
        return mp.Wire()

    def prism(poly, z0, z1):
        poly = orient(poly, 1.0)
        f = BRepBuilderAPI_MakeFace(wire(list(poly.exterior.coords), z0), True)
        for h in poly.interiors:
            f.Add(wire(list(h.coords), z0))
        return BRepPrimAPI_MakePrism(f.Face(), gp_Vec(0, 0, z1 - z0)).Shape()

    def body(sl):
        shapes = [prism(p, z0, z1) for g, z0, z1 in sl if g is not None and not g.is_empty and z1 - z0 > 1e-6
                  for p in polys(g.simplify(0.002)) if p.area > 1e-4]
        if not shapes:
            return None
        if len(shapes) == 1:                 # a fuse with no tools returns a null shape
            return shapes[0]
        args = TopTools_ListOfShape(); tools = TopTools_ListOfShape()
        args.Append(shapes[0])
        for s in shapes[1:]:
            tools.Append(s)
        fu = BRepAlgoAPI_Fuse(); fu.SetArguments(args); fu.SetTools(tools); fu.SetRunParallel(True); fu.Build()
        u = ShapeUpgrade_UnifySameDomain(fu.Shape(), True, True, True); u.Build()
        return u.Shape()

    doc = TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    for cname, rgb in cols.items():
        sh = body(slabs[cname])
        if sh is None:
            continue
        lab = st.AddShape(sh, False)
        TDataStd_Name.Set_s(lab, TCollection_ExtendedString(f'{name} {cname}'))
        c = Quantity_Color(*rgb, Quantity_TOC_RGB)
        ct.SetColor(lab, c, XCAFDoc_ColorGen); ct.SetColor(lab, c, XCAFDoc_ColorSurf)
    Interface_Static.SetCVal_s('write.step.schema', 'AP214')
    sys.stdout.flush()
    fd = os.dup(1); nul = os.open(os.devnull, os.O_WRONLY); os.dup2(nul, 1)
    try:
        w = STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True)
        w.Transfer(doc, STEPControl_AsIs); w.Write(path)
    finally:
        os.dup2(fd, 1); os.close(fd); os.close(nul)


def count_changes(slabs, extruders, lh=0.2, top=3.0):
    """Simulate by-layer printing with the slicer's ordering rule (start each layer with the current filament)."""
    n = int(round(top / lh))
    cur, changes = None, 0
    for i in range(n):
        zm = (i + 0.5) * lh
        used = sorted({extruders[k] for k, sl in slabs.items() for g, a, b in sl
                       if g is not None and not g.is_empty and a < zm < b})
        if not used:
            continue
        if cur in used:
            order = [cur] + [e for e in used if e != cur]
        else:
            order = used
        for e in order:
            if cur is not None and e != cur:
                changes += 1
            cur = e
    return changes


def run(spec_path, outdir, do_step=True, do_slice=True):
    spec = export.load_spec(spec_path)
    cid = spec['id']
    M = geom.build_maps(spec); geom.repair_min_width(M); geom.split_white(M)
    placed, tower_xy, how = plate.best_layout(M['outline'])
    rep = {'id': cid, 'light_islands': len(polys(M['white_light'])), 'plate_count': len(placed)}
    # face previews in sample colours
    for nm, rgb in SAMPLES.items():
        render_face3(M, os.path.join(outdir, f'face_body_{nm}.png'), tuple(int(255 * c) for c in rgb), title=f"{spec.get('name')} - {nm} body")
    for st, fn in (('production3', build3d.build_production3), ('classic3', build3d.build_classic3)):
        parts, slabs = fn(M)
        d = os.path.join(outdir, st); os.makedirs(d, exist_ok=True)
        stem = f'{cid}_{st}'
        tms = {k: build3d.to_trimesh(v) for k, v in parts.items() if v is not None}
        for k, tm in tms.items():
            tm.export(os.path.join(d, f'{stem}_{k}.stl'))
        r3d = os.path.join(d, f'{stem}_render_red.png')
        render.render3d([(tms['body'], SAMPLES['red']), (tms['black'], (0.10, 0.10, 0.11))] + ([(tms['light'], (0.95, 0.95, 0.93))] if 'light' in tms else []),
                        r3d, elev=55, azim=-10)
        if do_step:
            export_step3(slabs, os.path.join(d, f'{stem}.step'), spec.get('name', cid),
                         {'black': (0.098, 0.098, 0.098), 'body': SAMPLES['red'], 'light': (0.972, 0.969, 0.957)})
        prt = [dict(name=n, mesh=tms[c], extruder=e) for n, c, e in PARTS[st] if c in tms]
        oname = f"{spec.get('name', cid)} keychain (custom body colour, {'1-swap style' if st == 'production3' else 'classic inlay'})"
        cfg = k2config.build_n(3, COLOURS, FLUSH3)
        write3mf.write_3mf(os.path.join(d, f'{stem}_single.3mf'), prt, cfg, object_name=oname, app_version=k2config.VERSION,
                           thumbnail_png=r3d, positions=[(130.0, 130.0)])
        cfgp = k2config.build_n(3, COLOURS, FLUSH3, {'wipe_tower_x': [f'{tower_xy[0]:.1f}'], 'wipe_tower_y': [f'{tower_xy[1]:.1f}']})
        write3mf.write_3mf(os.path.join(d, f'{stem}_PLATE_{len(placed)}x.3mf'), prt, cfgp, object_name=oname, app_version=k2config.VERSION,
                           thumbnail_png=r3d, positions=placed)
        ext = {c: e for _, c, e in PARTS[st]}
        info = {'changes_per_plate': count_changes(slabs, ext),
                'volumes_mm3': {k: round(v.volume(), 1) for k, v in parts.items() if v is not None}}
        if do_slice:
            import slicecheck
            sc = slicecheck.check_parts(tms, slabs, os.path.join(outdir, '_slicecheck3', st), r3d, stem)
            info['slicecheck'] = {k: {kk: v.get(kk) for kk in ('status', 'n_lost', 'top_layer_coverage', 'grams', 'time_single_colour')} for k, v in sc.items()}
        rep[st] = info
    json.dump(rep, open(os.path.join(outdir, 'custom_colour_report.json'), 'w'), indent=1)
    return rep


def render_face3(M, path, body_rgb, title=None, ppm=12):
    from PIL import Image, ImageDraw
    b = M['outline'].bounds; pad = 4
    W = int((b[2] - b[0] + 2 * pad) * ppm); H = int((b[3] - b[1] + 2 * pad) * ppm) + (30 if title else 0)
    img = Image.new('RGB', (W, H), (46, 52, 64))
    fn = lambda x, y: ((x - b[0] + pad) * ppm, H - (y - b[1] + pad) * ppm)
    render._paint(img, M['outline'], fn, body_rgb)
    render._paint(img, M['black'], fn, (32, 32, 34))
    if not M['relief_region'].is_empty:
        render._paint(img, M['relief_region'], fn, (14, 14, 16)); render._paint(img, M['relief_ribs'], fn, (58, 58, 62))
    render._paint(img, M['grooves_white'], fn, tuple(int(c * 0.55) for c in body_rgb))
    render._paint(img, M['white_light'], fn, (240, 240, 236))
    render._paint(img, M['hole'], fn, (46, 52, 64))
    if title:
        ImageDraw.Draw(img).text((8, 6), title, fill=(230, 230, 230))
    img.save(path)


if __name__ == '__main__':
    r = run(sys.argv[1], sys.argv[2], do_step='--no-step' not in sys.argv, do_slice='--no-slice' not in sys.argv)
    print(json.dumps(r, indent=1))
