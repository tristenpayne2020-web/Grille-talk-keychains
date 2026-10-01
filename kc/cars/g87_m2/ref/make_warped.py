"""Perspective correction of the reference photo: the photo was taken from eye level (~1.4 m), so the nearly
horizontal hood / fender tops look much taller than in the G80 reference (camera near bonnet height). Rows above
the headlight tips (y < Y0) are compressed toward Y0 by factor F; the front (vertical) surfaces are untouched.
The spec applies the same mapping to its traced points, so overlay.png on the warped photo stays exact."""
import sys
import numpy as np
from PIL import Image
Y0, F = 515.0, 0.62
src = Image.open(sys.argv[1]).convert('RGB')
a = np.asarray(src)
H, W = a.shape[:2]
out = np.zeros_like(a)
for yp in range(H):
    y = yp if yp >= Y0 else Y0 - (Y0 - yp) / F
    yi = int(round(y))
    if 0 <= yi < H:
        out[yp] = a[yi]
Image.fromarray(out).save(sys.argv[2])
