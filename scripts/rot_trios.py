# -*- coding: utf-8 -*-
"""Junta las hojas work/rot/hoja_N.png de tres en tres (work/rot/trio_N.png) para revisarlas de un vistazo."""
import glob, os
from PIL import Image
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'work', 'rot')
for f in glob.glob(os.path.join(D, 'trio_*.png')): os.remove(f)
fs = sorted(glob.glob(os.path.join(D, 'hoja_*.png')), key=lambda f: int(f.split('_')[-1][:-4]))
for k in range(0, len(fs), 3):
    ims = [Image.open(f) for f in fs[k:k + 3]]; W = sum(i.size[0] for i in ims); H = max(i.size[1] for i in ims)
    o = Image.new('RGB', (W, H), (95, 95, 115)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.size[0]
    o.resize((int(W * 0.62), int(H * 0.62)), Image.LANCZOS).save(os.path.join(D, 'trio_%d.png' % (k // 3))); print('trio_%d' % (k // 3))
