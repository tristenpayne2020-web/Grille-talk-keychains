"""Slice each colour part on its own with the Creality Print CLI (K2 0.4 profile) and compare the real tool paths,
layer by layer, with the designed cross-sections. Reports features the slicer drops or only partly fills.

(The CLI of Creality Print 7.x crashes on multi-colour plates - a bug in its prime-tower pre-check - so the colour
parts are verified one at a time here; the combined multi-colour plates are sliced in the Creality Print GUI.)
"""
import os, re, json, subprocess, zipfile, math
import numpy as np
from PIL import Image, ImageDraw
from shapely.ops import unary_union
from shapely.geometry import box
import k2config, write3mf
from geom import polys

EXE = os.environ.get('CREALITY_EXE', r"C:\Program Files\Creality\Creality Print 7.1\CrealityPrint.exe")  # no slicer in the cloud: export with --no-slice
BEDC = (130.0, 130.0)


def slice_single_part(mesh, name, workdir, thumb, cfg_over=None):
    os.makedirs(workdir, exist_ok=True)
    cfg = k2config.build(cfg_over or {})
    src = os.path.abspath(os.path.join(workdir, name + '_1part.3mf'))
    out = os.path.abspath(os.path.join(workdir, name + '_1part_sliced.3mf'))
    write3mf.write_3mf(src, [dict(name=name, mesh=mesh, extruder=1)], cfg, object_name=name, positions=[BEDC], thumbnail_png=thumb)
    text = slice_3mf(src, os.path.join(workdir, name + '_gcode'))
    if text is None:
        return None, 'CLI failed'
    return text, 'ok'


def slice_3mf(src, outdir, timeout=3600):
    """Slice plate 1 of a project 3MF with the Creality Print CLI. 7.3+ syntax first (it also handles multi-colour
    projects), then the 7.1/7.2 syntax as a fallback. Returns the G-code text or None."""
    import shutil
    src = os.path.abspath(src); outdir = os.path.abspath(outdir)
    shutil.rmtree(outdir, ignore_errors=True); os.makedirs(outdir, exist_ok=True)
    r = subprocess.run([EXE, '--cli', '--slice', '1', '--outputdir', outdir, '--need-gcode-file', src], capture_output=True, text=True, timeout=timeout)
    g = os.path.join(outdir, 'plate_1.gcode')
    if r.returncode == 0 and os.path.exists(g):
        return open(g, encoding='utf-8', errors='ignore').read()
    out = os.path.join(outdir, 'sliced.3mf')
    r = subprocess.run([EXE, '--slice', '1', '--export-3mf', out, src], capture_output=True, text=True, timeout=timeout)
    if r.returncode == 0 and os.path.exists(out):
        z = zipfile.ZipFile(out)
        gn = [n for n in z.namelist() if n.endswith('.gcode')][0]
        return z.read(gn).decode('utf-8', 'ignore')
    return None


def parse_gcode(text):
    """-> {z: [(x0,y0,x1,y1,width), ...]} for extruding moves, plus header info."""
    layers = {}
    z = None; width = 0.42; x = y = None; rel = True; e_abs = 0.0; typ = ''
    for line in text.split('\n'):
        if line.startswith(';'):
            if line.startswith(';Z:') or line.startswith(';:'):
                try:
                    z = round(float(line.split(':', 1)[1]), 3)
                except ValueError:
                    pass
            elif line.startswith(';WIDTH:'):
                width = float(line[7:])
            elif line.startswith(';TYPE:'):
                typ = line[6:].strip()
            continue
        if line.startswith('M83'):
            rel = True
        elif line.startswith('M82'):
            rel = False
        elif line.startswith('G92') and ' E' in line:
            e_abs = float(re.search(r'E(-?[\d.]+)', line).group(1))
        elif line.startswith(('G1 ', 'G0 ', 'G2 ', 'G3 ')):
            mx = re.search(r' X(-?[\d.]+)', line); my = re.search(r' Y(-?[\d.]+)', line); me = re.search(r' E(-?[\d.]+)', line)
            nx = float(mx.group(1)) if mx else x
            ny = float(my.group(1)) if my else y
            ext = False
            if me:
                ev = float(me.group(1))
                if rel:
                    ext = ev > 0
                else:
                    ext = ev > e_abs; e_abs = ev
            if ext and z is not None and x is not None and (nx != x or ny != y) and typ not in ('Ironing', 'Skirt', 'Prime tower', 'Wipe tower'):
                if line.startswith(('G2 ', 'G3 ')) and (' I' in line or ' J' in line):
                    # arc move: interpolate (the slicer uses arc fitting; a chord would under-report round features)
                    mi = re.search(r' I(-?[\d.]+)', line); mj = re.search(r' J(-?[\d.]+)', line)
                    cx = x + (float(mi.group(1)) if mi else 0.0); cy = y + (float(mj.group(1)) if mj else 0.0)
                    a0 = math.atan2(y - cy, x - cx); a1 = math.atan2(ny - cy, nx - cx)
                    r = math.hypot(x - cx, y - cy)
                    if line.startswith('G2 '):          # clockwise
                        while a1 >= a0: a1 -= 2 * math.pi
                    else:
                        while a1 <= a0: a1 += 2 * math.pi
                    nseg = max(2, int(abs(a1 - a0) * r / 0.2) + 1)
                    px, py = x, y
                    for k in range(1, nseg + 1):
                        a = a0 + (a1 - a0) * k / nseg
                        qx, qy = cx + r * math.cos(a), cy + r * math.sin(a)
                        layers.setdefault(z, []).append((px, py, qx, qy, width)); px, py = qx, qy
                else:
                    layers.setdefault(z, []).append((x, y, nx, ny, width))
            x, y = nx, ny
    info = {}
    m = re.search(r'estimated printing time \(normal mode\) = ([^\n]+)', text)
    if m:
        info['time'] = m.group(1).strip()
    m = re.search(r'total filament used \[g\] = ([\d.]+)', text) or re.search(r'filament used \[g\] = ([\d.]+)', text)
    if m:
        info['grams'] = float(m.group(1))
    return layers, info


def region_at(slabs, zmid):
    return unary_union([g for g, z0, z1 in slabs if g is not None and not g.is_empty and z0 < zmid < z1])


def _rast(g, W, H, fd):
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    for p in polys(g):
        d.polygon([fd(X, Y) for X, Y in p.exterior.coords], fill=255)
        for h in p.interiors:
            d.polygon([fd(X, Y) for X, Y in h.coords], fill=0)
    return np.array(im) > 0


def compare(slabs, layers, offset, ppm=20, lh=0.2, zoff=0.0, band=0.8, name=''):
    """offset: (dx, dy) added to design coords to get bed coords; zoff: design z of the part's lowest point (the CLI
    drops a lone part onto the bed). A feature counts as printed when the band along its outline (where the walls go)
    is covered - interior sparse infill is ignored. The top layer is also checked for full solid coverage."""
    dx, dy = offset
    allg = unary_union([g for g, _, _ in slabs if g is not None and not g.is_empty])
    b = allg.bounds
    W = int((b[2] - b[0] + 4) * ppm); H = int((b[3] - b[1] + 4) * ppm)
    fn = lambda X, Y: ((X - dx - b[0] + 2) * ppm, H - (Y - dy - b[1] + 2) * ppm)
    fd = lambda X, Y: ((X - b[0] + 2) * ppm, H - (Y - b[1] + 2) * ppm)
    report = {'layers': [], 'lost_features': [], 'top_layer_coverage': None}
    zs = sorted(layers)
    for zt in zs:
        zmid = zt - lh / 2 + zoff
        exp = region_at(slabs, zmid)
        if exp.is_empty:
            continue
        pm = Image.new('L', (W, H), 0); d = ImageDraw.Draw(pm)
        for x0, y0, x1, y1, w in layers[zt]:
            d.line([fn(x0, y0), fn(x1, y1)], fill=255, width=max(1, int(round(w * ppm))))
            r = w * ppm / 2
            for X, Y in (fn(x0, y0), fn(x1, y1)):
                d.ellipse([X - r, Y - r, X + r, Y + r], fill=255)
        pa = np.array(pm) > 0
        ea = _rast(exp, W, H, fd)
        cov = (pa & ea).sum() / max(1, ea.sum())
        report['layers'].append((round(zt + zoff, 3), round(float(cov), 3)))
        if zt == zs[-1]:
            report['top_layer_coverage'] = round(float(cov), 3)
        for p in polys(exp):
            if p.area < 0.08:
                continue
            bnd = p.difference(p.buffer(-band))
            fa = _rast(bnd if not bnd.is_empty else p, W, H, fd)
            c = (pa & fa).sum() / max(1, fa.sum())
            if c < 0.6:
                rp = p.representative_point()
                report['lost_features'].append(dict(z=round(zt + zoff, 3), at=(round(rp.x, 1), round(rp.y, 1)), area=round(p.area, 2), coverage=round(float(c), 2)))
    return report


def check_parts(meshes, slabs, workdir, thumb, tag):
    """meshes: {'black': trimesh, 'white': trimesh}; slabs from build3d. Returns dict per colour."""
    out = {}
    for col, mesh in meshes.items():
        if mesh is None:
            continue
        sl = slabs[col]
        # back label letters (bottom 0.4 mm) under a cap that starts higher: the part alone would float, which the
        # single-part slicer refuses. Check the floating part on its own (the letters are checked with the full plate).
        comps = mesh.split(only_watertight=False)
        lo = [c for c in comps if c.bounds[1][2] <= 0.4 + 1e-3]
        if lo and len(lo) < len(comps) and min(c.bounds[0][2] for c in comps if c not in lo) > 0.4 - 1e-3:
            import trimesh
            mesh = trimesh.util.concatenate([c for c in comps if c.bounds[1][2] > 0.4 + 1e-3])
            sl = [(g, a, b) for g, a, b in sl if a >= 0.4 - 1e-3]
        text, st = slice_single_part(mesh, f'{tag}_{col}', workdir, thumb)
        if text is None:
            out[col] = {'status': st}
            continue
        layers, info = parse_gcode(text)
        bb = mesh.bounds
        cx, cy = (bb[0][0] + bb[1][0]) / 2, (bb[0][1] + bb[1][1]) / 2
        rep = compare(sl, layers, (BEDC[0] - cx, BEDC[1] - cy), zoff=float(bb[0][2]), name=col)
        covs = [c for _, c in rep['layers']]
        out[col] = {'status': 'ok', 'time_single_colour': info.get('time'), 'grams': info.get('grams'),
                    'n_layers': len(covs), 'min_layer_coverage': min(covs) if covs else None,
                    'mean_layer_coverage': round(float(np.mean(covs)), 3) if covs else None,
                    'top_layer_coverage': rep['top_layer_coverage'],
                    'lost_features': rep['lost_features'][:40], 'n_lost': len(rep['lost_features'])}
    return out
