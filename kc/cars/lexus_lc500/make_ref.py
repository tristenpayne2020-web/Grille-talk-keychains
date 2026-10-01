"""Build ref/front.jpg for tracing/overlay from ref/sao9314.jpg (Wikimedia 1920 px thumbnail):
CLAHE contrast boost (the car is dark blue) + the same hood compression as spec.py (rows above Y0 squeezed by K),
so overlay.png lines up with the design. Run: python kc/cars/lexus_lc500/make_ref.py"""
import os, cv2, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
Y0, K = 520.0, 0.32
im = cv2.imread(os.path.join(D, 'ref', 'sao9314.jpg'))
lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
lab[:, :, 0] = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(lab[:, :, 0])
im = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
cv2.imwrite(os.path.join(D, 'ref', 'front_enh.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 95])
H, W = im.shape[:2]
yo = np.arange(H, dtype=np.float32)
ys = np.where(yo >= Y0, yo, Y0 - (Y0 - yo) / K)          # inverse of T: output row -> source row
mapy = np.repeat(ys[:, None], W, 1).astype(np.float32)
mapx = np.repeat(np.arange(W, dtype=np.float32)[None, :], H, 0)
out = cv2.remap(im, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(40, 40, 40))
cv2.imwrite(os.path.join(D, 'ref', 'front.jpg'), out, [cv2.IMWRITE_JPEG_QUALITY, 95])
