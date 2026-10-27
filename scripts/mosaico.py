# -*- coding: utf-8 -*-
"""Mosaico de capturas para revisarlas juntas.  Uso: python scripts/mosaico.py salida.png [--col N] [--w ancho] nombre1 nombre2 ...
(nombres de shots/ sin .png)"""
import sys, os
from PIL import Image, ImageDraw
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shots')
a = sys.argv[1:]; out = a.pop(0); col = 2; w = 640
while a and a[0].startswith('--'):
    k = a.pop(0); v = int(a.pop(0))
    if k == '--col': col = v
    else: w = v
ims = []
for n in a:
    f = os.path.join(D, n + '.png')
    if not os.path.exists(f): continue
    im = Image.open(f).convert('RGB'); im = im.resize((w, int(im.size[1] * w / im.size[0])), Image.LANCZOS)
    ImageDraw.Draw(im).text((3, 2), n, fill=(255, 255, 0)); ims.append(im)
if ims:
    rows = (len(ims) + col - 1) // col; h = max(i.size[1] for i in ims)
    o = Image.new('RGB', (col * w, rows * h), (30, 30, 30))
    for k, im in enumerate(ims): o.paste(im, ((k % col) * w, (k // col) * h))
    o.save(os.path.join(D, out) if not os.path.isabs(out) else out); print(out, len(ims))
