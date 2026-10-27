# -*- coding: utf-8 -*-
"""Prueba rápida de la pieza 40 (rótulos dibujados) sin abrir el juego.
  python scripts/rot_prueba.py base              construye work/base40 (todas las piezas menos la 40)
  python scripts/rot_prueba.py [id id ...]       aplica rotulos.json a la base, exporta con FFDec la forma inglesa y la
                                                 traducida de cada rótulo y las pega por parejas en work/rot/hoja_N.png
"""
import sys, os, json, subprocess, shutil, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'piezas', '40_rotulos')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
BASE = os.path.join(ROOT, 'work', 'base40', 'Data', 'assets', 'Main.assets'); W = os.path.join(ROOT, 'work', 'rot')
JAVA = os.path.join(ROOT, 'tools', 'jre', 'jdk-21.0.12.1+1-jre', 'bin', 'java.exe'); FF = os.path.join(ROOT, 'tools', 'ffdec', 'ffdec.jar')
a = sys.argv[1:]
if a and a[0] == 'base':
    subprocess.check_call([sys.executable, os.path.join(ROOT, 'scripts', 'build.py'), '--lab', '--solo', '10_nucleo,20_volumen,30_espanol',
                           '--out', os.path.join(ROOT, 'work', 'base40')], stdout=subprocess.DEVNULL); print('base lista'); sys.exit()
import pieza
Z = 4
from PIL import Image, ImageDraw
os.makedirs(W, exist_ok=True)
lista = json.load(open(os.path.join(ROOT, 'piezas', '40_rotulos', 'rotulos.json'), encoding='utf-8'))
if a: lista = [r for r in lista if str(r['id']) in a]
ids = pieza.rotular(BASE, os.path.join(W, 'rot.swf'), lista, ROOT)
exp = os.path.join(W, 'exp'); shutil.rmtree(exp, ignore_errors=True)
sel = ','.join(str(v[0]) for d in ids.values() for L in d.values() for v in L)
subprocess.run([JAVA, '-Xmx3g', '-jar', FF, '-selectid', sel, '-zoom', str(Z), '-format', 'shape:png', '-export', 'shape', exp, os.path.join(W, 'rot.swf')],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def one(i):
    for f in glob.glob(os.path.join(exp, '**', '%d.png' % i), recursive=True): return Image.open(f).convert('RGBA')
def img(L):
    """compone las formas de un idioma (cada una recortada a su caja) en una sola imagen"""
    ims = [(one(i), x, y) for i, x, y in L]
    if any(a[0] is None for a in ims): return None
    x0 = min(x for _, x, y in ims); y0 = min(y for _, x, y in ims)
    Wd = max(int(round((x - x0) * Z / 20.0)) + im.size[0] for im, x, y in ims); Hd = max(int(round((y - y0) * Z / 20.0)) + im.size[1] for im, x, y in ims)
    out = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0))
    for im, x, y in ims: out.alpha_composite(im, (int(round((x - x0) * Z / 20.0)), int(round((y - y0) * Z / 20.0))))
    return out
cells = []
for sid, d in ids.items():
    for lang in d:
        if lang == 'en': continue
        A = img(d['en']); B = img(d[lang])
        if A is None or B is None: print('sin imagen', sid); continue
        cells.append((sid, A, B))
CW = 400; sheets = 0; y = 0; row = []; pend = []
def flush(rows, n):
    H = sum(r[3] for r in rows) ; sh = Image.new('RGB', (CW * 2 + 60, H), (95, 95, 115)); d = ImageDraw.Draw(sh); y = 0
    for sid, A, B, h in rows:
        d.text((2, y + 2), str(sid), fill=(255, 255, 0))
        for k, im in enumerate((A, B)):
            im = im.copy(); im.thumbnail((CW - 10, 600))
            sh.paste(im, (60 + k * CW, y + 4), im)
        y += h
    out = os.path.join(W, 'hoja_%d.png' % n); sh.save(out); print(out)
rows = []; tot = 0
for sid, A, B in cells:
    sc = min(1.0, (CW - 10) / max(A.size[0], B.size[0])); h = int(max(A.size[1], B.size[1]) * sc) + 12
    if tot + h > 1500 and rows: flush(rows, sheets); sheets += 1; rows = []; tot = 0
    rows.append((sid, A, B, h)); tot += h
if rows: flush(rows, sheets)
