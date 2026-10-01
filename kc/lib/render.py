"""Previews: flat face render (Fusion-style colours), overlay of the traced spec on the reference photo, 3D render."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon
from shapely import affinity
from geom import polys, Frame

WHITE = (232, 229, 218)
BLACK = (32, 32, 34)
BG = (46, 52, 64)
GRID = (62, 69, 84)


def _fill(draw, g, fn, colour, outline=None):
    for p in polys(g):
        draw.polygon([fn(x, y) for x, y in p.exterior.coords], fill=colour, outline=outline)
        for h in p.interiors:
            draw.polygon([fn(x, y) for x, y in h.coords], fill=None)


def _paint(img, g, fn, colour):
    """Fill polygons with holes correctly via a mask."""
    if g is None or g.is_empty:
        return
    mask = Image.new('L', img.size, 0)
    d = ImageDraw.Draw(mask)
    for p in polys(g):
        d.polygon([fn(x, y) for x, y in p.exterior.coords], fill=255)
        for h in p.interiors:
            d.polygon([fn(x, y) for x, y in h.coords], fill=0)
    img.paste(Image.new('RGB', img.size, colour), (0, 0), mask)


def face_png(M, path, ppm=14, style='production', title=None, grid=True):
    """Top view of the face. style='production' shades recessed black slightly lighter where ribs stand up."""
    b = M['outline'].bounds
    pad = 6
    W = int((b[2] - b[0] + 2 * pad) * ppm)
    H = int((b[3] - b[1] + 2 * pad) * ppm) + (40 if title else 0)
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    if grid:
        for gx in range(int(b[0] - pad), int(b[2] + pad) + 1, 5):
            X = (gx - b[0] + pad) * ppm
            d.line([(X, 0), (X, H)], fill=GRID, width=1)
        for gy in range(int(b[1] - pad), int(b[3] + pad) + 1, 5):
            Y = H - (gy - b[1] + pad) * ppm
            d.line([(0, Y), (W, Y)], fill=GRID, width=1)
    fn = lambda x, y: ((x - b[0] + pad) * ppm, H - (y - b[1] + pad) * ppm)
    _paint(img, M['outline'], fn, WHITE)
    _paint(img, M['black'], fn, BLACK)
    if not M['relief_region'].is_empty:
        _paint(img, M['relief_region'], fn, (14, 14, 16))
        _paint(img, M['relief_ribs'], fn, (58, 58, 62))
    gcol = (40, 40, 42) if style == 'production' else (150, 148, 140)
    _paint(img, M['grooves_white'], fn, gcol)
    _paint(img, M['grooves_black'], fn, (70, 70, 72))
    _paint(img, M['hole'], fn, BG)
    if title:
        d.text((10, 8), title, fill=(230, 230, 230))
    img.save(path)
    return img


def overlay_png(spec, M, ref_path, path, alpha=0.45):
    """Draw the painted design back onto the reference photo (in photo pixels) to check the tracing."""
    F = Frame(spec)
    dy, k = M['place']
    im = Image.open(ref_path).convert('RGB')
    base = im.copy()
    def to_px(x, y):
        x = x / k; y = y / k - dy
        return (x / F.s + F.cx, F.ybot - y / (F.s * F.yscale))
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    mask_img = Image.new('RGB', im.size, (0, 0, 0))
    over = im.copy()
    _paint(over, M['white'], to_px, (255, 255, 255))
    _paint(over, M['black'], to_px, (0, 0, 0))
    _paint(over, M['relief_ribs'], to_px, (90, 90, 90))
    _paint(over, unary(M), to_px, (255, 0, 0))
    out = Image.blend(base, over, alpha)
    d = ImageDraw.Draw(out)
    for g, col in ((M['outline'], (255, 60, 60)), (M['black'], (0, 200, 255)), (M['white'], (255, 220, 0))):
        for p in polys(g):
            d.line([to_px(x, y) for x, y in p.exterior.coords], fill=col, width=2)
            for h in p.interiors:
                d.line([to_px(x, y) for x, y in h.coords], fill=col, width=1)
    out.save(path)
    return out


def unary(M):
    from shapely.ops import unary_union
    return unary_union([M['grooves_white'], M['grooves_black']])


def side_by_side(paths, out, labels=None, height=520):
    ims = [Image.open(p).convert('RGB') for p in paths]
    ims = [im.resize((int(im.width * height / im.height), height)) for im in ims]
    W = sum(im.width for im in ims) + 10 * (len(ims) + 1)
    canvas = Image.new('RGB', (W, height + 40), (20, 20, 20))
    x = 10
    d = ImageDraw.Draw(canvas)
    for i, im in enumerate(ims):
        canvas.paste(im, (x, 30))
        if labels:
            d.text((x, 8), labels[i], fill=(240, 240, 240))
        x += im.width + 10
    canvas.save(out)


# ----------------------------------------------------------------------------------------------- 3D (VTK, offscreen)
def render3d(parts, path, size=(1400, 900), elev=38, azim=-18, bg=(0.18, 0.20, 0.25), zoom=1.35):
    """parts: list of (trimesh, rgb 0..1). Perspective view like the user's Fusion screenshot."""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
    ren = vtk.vtkRenderer(); ren.SetBackground(*bg)
    allv = []
    for tm, rgb in parts:
        if tm is None:
            continue
        v = np.asarray(tm.vertices, dtype=np.float64); f = np.asarray(tm.faces, dtype=np.int64)
        allv.append(v)
        pts = vtk.vtkPoints(); pts.SetData(numpy_to_vtk(v, deep=True))
        cells = np.hstack([np.full((len(f), 1), 3, dtype=np.int64), f]).ravel()
        ca = vtk.vtkCellArray(); ca.SetCells(len(f), numpy_to_vtkIdTypeArray(cells, deep=True))
        pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(ca)
        nm = vtk.vtkPolyDataNormals(); nm.SetInputData(pd); nm.SetFeatureAngle(30); nm.SplittingOn(); nm.Update()
        mp = vtk.vtkPolyDataMapper(); mp.SetInputConnection(nm.GetOutputPort())
        ac = vtk.vtkActor(); ac.SetMapper(mp)
        pr = ac.GetProperty(); pr.SetColor(*rgb); pr.SetDiffuse(0.85); pr.SetAmbient(0.22); pr.SetSpecular(0.12); pr.SetSpecularPower(20)
        ren.AddActor(ac)
        fe = vtk.vtkFeatureEdges(); fe.SetInputData(pd); fe.BoundaryEdgesOff(); fe.FeatureEdgesOn(); fe.SetFeatureAngle(60)
        fe.ManifoldEdgesOff(); fe.NonManifoldEdgesOff(); fe.Update()
        em = vtk.vtkPolyDataMapper(); em.SetInputConnection(fe.GetOutputPort()); em.ScalarVisibilityOff()
        ea = vtk.vtkActor(); ea.SetMapper(em); ea.GetProperty().SetColor(0.05, 0.05, 0.05); ea.GetProperty().SetLineWidth(1.0); ea.GetProperty().SetOpacity(0.35)
        ren.AddActor(ea)
    allv = np.vstack(allv)
    c = (allv.min(0) + allv.max(0)) / 2
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(*c)
    r = np.linalg.norm(allv.max(0) - allv.min(0))
    e, a = np.radians(elev), np.radians(azim)
    cam.SetPosition(c[0] + r * 1.6 * np.sin(a) * np.cos(e), c[1] - r * 1.6 * np.cos(a) * np.cos(e), c[2] + r * 1.6 * np.sin(e) + 0)
    cam.SetViewUp(0, 0, 1)
    cam.SetViewAngle(30)
    ren.ResetCameraClippingRange()
    cam.Zoom(zoom)
    l1 = vtk.vtkLight(); l1.SetPosition(c[0] - 80, c[1] - 120, c[2] + 200); l1.SetFocalPoint(*c); l1.SetIntensity(0.8)
    l2 = vtk.vtkLight(); l2.SetPosition(c[0] + 120, c[1] + 60, c[2] + 120); l2.SetFocalPoint(*c); l2.SetIntensity(0.35)
    ren.AddLight(l1); ren.AddLight(l2)
    rw = vtk.vtkRenderWindow(); rw.SetOffScreenRendering(1); rw.AddRenderer(ren); rw.SetSize(*size); rw.SetMultiSamples(8)
    rw.Render()
    w2i = vtk.vtkWindowToImageFilter(); w2i.SetInput(rw); w2i.Update()
    wr = vtk.vtkPNGWriter(); wr.SetFileName(path); wr.SetInputConnection(w2i.GetOutputPort()); wr.Write()
    rw.Finalize()
    return path


def render3d_pair(parts, path_front, **kw):
    return render3d(parts, path_front, **kw)
