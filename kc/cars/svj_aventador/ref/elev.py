"""Front-elevation correction for the SVJ press photo (ref/front.jpg).

The Lamborghini press photo is shot from high above the hood. Compared with a normal front view (checked against
the lower-camera street photo alt_red_monaco_1146.jpg and the G80 reference viewpoint) it shows
  * a perspective 'sag': everything near the centreline (nose, splitter, cowl) sits lower than at the corners,
    so the outline reads as a crescent;
  * the upward-facing surfaces (hood, lamp faces, nose) far too tall and the forward-facing lower bumper / intake
    too short.
W(x, y) maps a press-photo pixel to a 'front elevation' pixel:
  1. sag removal: y -= S * (1 - u^2), u = |x - CX| / WSAG   (centre raised by S px, corners unchanged)
  2. smooth vertical re-proportioning with per-band scale factors (hood above the lamps, lamps, nose,
     intake + splitter), integrated from a smoothed scale profile so there are no kinks.
Running this file writes ref/front_elev.png (the photo warped with the same map), which the spec uses as its
overlay reference, so overlay.png lines up with the design.
"""
import os
import numpy as np

CX = 639.5
S, WSAG = 12.0, 262.0
Y_ANCHOR = 476.0                                   # lamp top: stays where it is
# band edges (sag-corrected press px) and scale factors
BANDS = [(-1e9, 476.0, 0.60),                      # hood above the lamps
         (476.0, 563.0, 0.72),                     # lamps
         (563.0, 638.0, 0.62),                     # nose / vents / badge
         (638.0, 1e9, 1.15)]                       # intake + blades + splitter (forward-facing, foreshortened)
BLEND = 8.0                                        # px, smooth transition between bands

_ys = np.arange(0.0, 1200.0, 0.25)


def _scale(y):
    s = np.full_like(y, BANDS[0][2])
    for (a0, a1, k0), (b0, b1, k1) in zip(BANDS[:-1], BANDS[1:]):
        t = np.clip((y - (a1 - BLEND)) / (2 * BLEND), 0, 1)
        t = t * t * (3 - 2 * t)
        s = s + (k1 - k0) * t
    return s


_f = np.concatenate([[0.0], np.cumsum(_scale(_ys[:-1] + 0.125) * 0.25)])
_f += Y_ANCHOR - np.interp(Y_ANCHOR, _ys, _f)


def sag(x):
    u = np.minimum(np.abs(np.asarray(x, float) - CX) / WSAG, 1.0)
    return S * (1 - u * u)


def W(x, y):
    ys = y - sag(x)
    return float(x), float(np.interp(ys, _ys, _f))


def Wpts(pts, nd=1):
    return [(round(W(x, y)[0], nd), round(W(x, y)[1], nd)) for x, y in pts]


def inv_y(x, yp):
    ys = np.interp(yp, _f, _ys)
    return ys + sag(x)


if __name__ == '__main__':
    import cv2
    here = os.path.dirname(os.path.abspath(__file__))
    im = cv2.imread(os.path.join(here, 'front.jpg'))
    H, Wd = im.shape[:2]
    X, Y = np.meshgrid(np.arange(Wd, dtype=np.float32), np.arange(H, dtype=np.float32))
    mapy = inv_y(X, Y).astype(np.float32)
    out = cv2.remap(im, X, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(os.path.join(here, 'front_elev.png'), out)
    for p in [(CX, 428), (378, 391), (CX, 724), (430, 708), (371, 476), (427, 567), (CX, 651), (CX, 601)]:
        print(p, '->', W(*p))
