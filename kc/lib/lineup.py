"""All cars at the same mm scale in one image:  python kc/lib/lineup.py out.png kc/cars/<id>/spec.py [...]
(a .pkl spec also works). Face renders use the same ppm so sizes and line weights compare 1:1."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from PIL import Image, ImageDraw
import export, geom, render

def main(out, specs, ppm=9):
    ims = []
    for p in specs:
        spec = export.load_spec(p)
        M = geom.build_maps(spec); geom.repair_min_width(M)
        tmp = out + f'.{len(ims)}.png'
        render.face_png(M, tmp, ppm=ppm, title=f"{spec.get('name', spec.get('id'))}  {M['outline'].bounds[2]-M['outline'].bounds[0]:.1f} x {M['outline'].bounds[3]-M['outline'].bounds[1]:.1f} mm")
        ims.append(Image.open(tmp).convert('RGB')); os.remove(tmp)
    cols = 2
    rows = (len(ims) + cols - 1) // cols
    cw = max(i.width for i in ims); ch = max(i.height for i in ims)
    canvas = Image.new('RGB', (cols * cw, rows * ch), (30, 34, 42))
    for k, im in enumerate(ims):
        canvas.paste(im, ((k % cols) * cw, (k // cols) * ch))
    canvas.save(out)
    print('wrote', out, canvas.size)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
