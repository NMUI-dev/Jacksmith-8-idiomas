# -*- coding: utf-8 -*-
"""Estructura de una forma: grupos, rellenos (tipo/color), líneas y, por relleno, nº de contornos y caja (px).
Uso: python scripts/forma_info.py [--swf ruta] <id> [<id> ...]"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'pydeps'))
import formas, swfshape
def info(S, sid):
    t, p, q, e = S.pos[sid]; sh = swfshape.parse_shape(t, S.tags[q:e])
    b = sh['bounds']; print('== %d  v%d  caja %s  grupos %d' % (sid, sh['ver'], [round(v / 20.0, 1) for v in b], len(sh['groups'])))
    for gi, g in enumerate(sh['groups']):
        cs = swfshape.contours(g); nl = sum(1 for ed in g['edges'] if ed[8])
        print('  g%d aristas %d (con línea %d) líneas %s' % (gi, len(g['edges']), nl, [(l['width'], l.get('color')) for l in g['lines']]))
        for fi, f in enumerate(g['fills'], 1):
            mine = [c for c in cs if c['fill'] == fi]
            if not mine: print('    f%d %s (sin contornos)' % (fi, f.get('color', hex(f['type'])))); continue
            bb = [swfshape.cbbox(c['path']) for c in mine]
            box = (min(x[0] for x in bb), min(x[1] for x in bb), max(x[2] for x in bb), max(x[3] for x in bb))
            desc = f.get('color') if f['type'] == 0 else ('grad%x %s' % (f['type'], [r[1] for r in f['grad']['recs']]) if 'grad' in f else 'bmp %s' % f.get('bitmap'))
            print('    f%d %s  contornos %d  caja %s' % (fi, desc, len(mine), [round(v / 20.0, 1) for v in box]))
if __name__ == '__main__':
    a = sys.argv[1:]; swf = os.path.join(ROOT, 'original', 'Data', 'assets', 'Main.assets')
    if '--swf' in a: i = a.index('--swf'); swf = a[i + 1]; del a[i:i + 2]
    S = formas.Swf(swf)
    for x in a: info(S, int(x))
