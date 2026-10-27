# -*- coding: utf-8 -*-
"""¿Con qué fuente incrustada está dibujado un rótulo?  Compara la proporción ancho/alto de la cara del rótulo con la
del texto compuesto con cada fuente (tal cual y en versalitas 0.8).   0 % = coincide.
Uso: python scripts/rot_fuente.py <id> "<texto>" <grupo> <relleno> [<grupo> <relleno> ...]"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'piezas', '40_rotulos'))
import swftool, swfshape, swfmod, formas, pieza
def main(sid, text, pairs, swf=os.path.join(ROOT, 'work', 'base40', 'Data', 'assets', 'Main.assets')):
    S = formas.Swf(swf); t, p, q, e = S.pos[sid]; sh = swfshape.parse_shape(t, S.tags[q:e]); bs = []
    for g, f in pairs:
        for c in swfshape.contours(sh['groups'][g]):
            if c['fill'] == f: bs.append(swfshape.cbbox(c['path']))
    R = (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)); ar = (R[2] - R[0]) / float(R[3] - R[1])
    res = []
    for t, p, q, e in swftool.iter_tags(S.tags):
        if t != 75: continue
        try: f = swfmod.Font(S.tags[q:e])
        except Exception: continue
        for vers in (None, 0.8):
            x = 0.0; cons = []
            try:
                for ch in text:
                    k = 1.0
                    if vers and ch != ch.upper(): ch = ch.upper(); k = vers
                    i = f.idx(ch); g = swfmod.decode_shape(f.shapes[i]) if len(f.shapes[i]) > 1 else []
                    cons += pieza._aff(g, k, 0, 0, k, x, 0); x += f.adv[i] * k
            except Exception: continue
            b = pieza._bbox(cons); a2 = (b[2] - b[0]) / float(b[3] - b[1])
            res.append((abs(a2 / ar - 1), '%+5.1f %%  %s%s' % ((a2 / ar - 1) * 100, f.name.decode().rstrip('\0'), ' (versalitas)' if vers else '')))
    return [r[1] for r in sorted(res)[:3]]
if __name__ == '__main__':
    a = sys.argv[1:]; pairs = [(int(a[i]), int(a[i + 1])) for i in range(2, len(a), 2)]
    print(a[0], a[1], ' | '.join(main(int(a[0]), a[1], pairs)))
