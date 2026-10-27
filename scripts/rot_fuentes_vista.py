# -*- coding: utf-8 -*-
"""Vista ampliada (x8) de UN rótulo traducido con varias fuentes, para elegir la más parecida al original.
Uso: python scripts/rot_fuentes_vista.py '<entrada json sin "fuente">' salida.png [fuente1,fuente2,...]"""
import sys, os, json, subprocess, glob, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'piezas', '40_rotulos'))
import pieza
from PIL import Image
JAVA = os.path.join(ROOT, 'tools', 'jre', 'jdk-21.0.12.1+1-jre', 'bin', 'java.exe'); FF = os.path.join(ROOT, 'tools', 'ffdec', 'ffdec.jar')
BASE = os.path.join(ROOT, 'work', 'base40', 'Data', 'assets', 'Main.assets'); Z = 8
def render(entry):
    t = os.path.join(ROOT, 'work', 'rot', 't.swf'); exp = os.path.join(ROOT, 'work', 'rot', 't_exp')
    ids = pieza.rotular(BASE, t, [entry], ROOT, verbose=False); d = list(ids.values())[0]; shutil.rmtree(exp, ignore_errors=True)
    sel = ','.join(str(v[0]) for L in d.values() for v in L)
    subprocess.run([JAVA, '-Xmx3g', '-jar', FF, '-selectid', sel, '-zoom', str(Z), '-format', 'shape:png', '-export', 'shape', exp, t], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    def comp(L):
        ims = [(Image.open(glob.glob(exp + '/**/%d.png' % i, recursive=True)[0]).convert('RGBA'), x, y) for i, x, y in L]
        x0 = min(x for _, x, y in ims); y0 = min(y for _, x, y in ims)
        W = max(int((x - x0) * Z / 20) + im.size[0] for im, x, y in ims); H = max(int((y - y0) * Z / 20) + im.size[1] for im, x, y in ims)
        o = Image.new('RGBA', (W, H), (95, 95, 115, 255))
        for im, x, y in ims: o.alpha_composite(im, (int((x - x0) * Z / 20), int((y - y0) * Z / 20)))
        return o
    return comp(d['en']), comp(d['es'])
if __name__ == '__main__':
    e = json.loads(sys.argv[1]); fs = sys.argv[3].split(',') if len(sys.argv) > 3 else [e['fuente']]
    outs = []
    for f in fs:
        en, es = render(dict(e, fuente=f)); outs.append(es)
    outs.insert(0, en)
    W = max(o.size[0] for o in outs); H = sum(o.size[1] + 6 for o in outs); sh = Image.new('RGB', (W, H), (95, 95, 115)); y = 0
    for o in outs: sh.paste(o, (0, y)); y += o.size[1] + 6
    if W > 1200: sh = sh.resize((1200, int(H * 1200 / W)))
    sh.save(sys.argv[2]); print(sys.argv[2], sh.size)
