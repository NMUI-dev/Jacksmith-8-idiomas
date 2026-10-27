# -*- coding: utf-8 -*-
"""Rótulos dibujados (texto convertido a contornos dentro de formas vectoriales).

  python scripts/arte.py inventario      -> work/arte/inventario.json + listado legible work/arte/inventario.txt
Reconoce las letras comparando cada contorno con los glifos de:
  - las fuentes incrustadas en el SWF, y
  - las TTF libres de tools/dl/fuentes (Alegreya Sans / Alegreya Sans SC, licencia OFL).
"""
import sys, os, json, struct, math, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'pydeps'))
import swftool, swfshape
from swfshape import parse_shape, contours, cbbox, signature, glyph_paths
from swfmod import Font

TRIV = set('.:oO0lIi-_|\'`,ˉ·•°')
CHARS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?&\'.,:-+%#')

def ttf_paths(path):
    """-> (nombre, {car: [contornos]}, {car: avance}, unidades_por_em). Contornos con y hacia abajo."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    f = TTFont(path); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm
    name = os.path.splitext(os.path.basename(path))[0]
    glyphs = {}; adv = {}
    for code, gname in cmap.items():
        ch = chr(code)
        pen = DecomposingRecordingPen(gs); gs[gname].draw(pen)
        paths = []; cur = []; pos = None; start = None
        for op, args in pen.value:
            if op == 'moveTo': pos = start = args[0]; cur = []
            elif op == 'lineTo':
                p = args[0]
                if p != pos: cur.append((pos[0], -pos[1], p[0], -p[1], None, None))
                pos = p
            elif op == 'qCurveTo':
                pts = list(args)
                if pts[-1] is None:      # contorno sin puntos en curva
                    pts = pts[:-1]; first = ((pts[-1][0] + pts[0][0]) / 2.0, (pts[-1][1] + pts[0][1]) / 2.0)
                    pos = start = first; pts = pts + [first]
                offs = pts[:-1]; end = pts[-1]
                for i, c in enumerate(offs):
                    nxt = end if i == len(offs) - 1 else ((c[0] + offs[i + 1][0]) / 2.0, (c[1] + offs[i + 1][1]) / 2.0)
                    cur.append((pos[0], -pos[1], nxt[0], -nxt[1], c[0], -c[1])); pos = nxt
            elif op == 'curveTo':
                p = args[-1]; cur.append((pos[0], -pos[1], p[0], -p[1], None, None)); pos = p
            elif op in ('closePath', 'endPath'):
                if pos != start and start is not None: cur.append((pos[0], -pos[1], start[0], -start[1], None, None))
                if cur: paths.append(cur)
                cur = []
        if paths: glyphs[ch] = paths
        adv[ch] = f['hmtx'][gname][0]
    return name, glyphs, adv, upm

class Fonts:
    """Todas las fuentes disponibles para reconocer y para dibujar."""
    def __init__(self, swf):
        self.g = {}; self.adv = {}; self.upm = {}
        _, _, tags = swftool.load(swf)
        for t, p, q, e in swftool.iter_tags(tags):
            if t != 75: continue
            try: f = Font(tags[q:e])
            except Exception: continue
            name = f.name.rstrip(b'\0').decode()
            self.g[name] = glyph_paths(f); self.upm[name] = 20480
            self.adv[name] = {chr(c): a for c, a in zip(f.codes, f.adv)} if f.layout else {}
        for path in sorted(glob.glob(os.path.join(ROOT, 'tools', 'dl', 'fuentes', '*.ttf'))):
            name, glyphs, adv, upm = ttf_paths(path)
            self.g[name] = glyphs; self.adv[name] = adv; self.upm[name] = upm
        self.index = {}
        for name, glyphs in self.g.items():
            for ch, paths in glyphs.items():
                if ch not in CHARS: continue
                big = max(paths, key=lambda p: (cbbox(p)[2] - cbbox(p)[0]) * (cbbox(p)[3] - cbbox(p)[1]))
                sg = signature(big)
                if sg is None: continue
                self.index.setdefault(sg[0], []).append((sg, name, ch, cbbox(big)))
    def match(self, path, tol=0.05):
        sg = signature(path)
        if sg is None or sg[0] < 4: return None
        best = None
        for g, name, ch, bb in self.index.get(sg[0], []):
            d = abs(g[1] - sg[1]) / max(g[1], 1e-6) + abs(g[2] - sg[2]) * 2 + abs(g[3] - sg[3]) * 2 + abs(g[4] - sg[4]) * 2 + abs(g[5] - sg[5]) / g[5]
            if best is None or d < best[0]: best = (d, name, ch, bb)
        return best if best and best[0] < tol else None

def scan(swf, fonts):
    _, _, tags = swftool.load(swf); res = []
    for t, p, q, e in swftool.iter_tags(tags):
        if t not in (2, 22, 32, 83): continue
        sh = parse_shape(t, tags[q:e]); letters = []
        for gi, g in enumerate(sh['groups']):
            for ci, c in enumerate(contours(g)):
                m = fonts.match(c['path'])
                if not m: continue
                x0, y0, x1, y1 = cbbox(c['path']); gb = m[3]
                sc = (y1 - y0) / float(gb[3] - gb[1])
                letters.append({'g': gi, 'fill': c['fill'], 'ch': m[2], 'font': m[1], 'd': round(m[0], 4), 'x': x0, 'y': y0,
                                'w': x1 - x0, 'h': y1 - y0, 'sc': sc, 'base': y0 - gb[1] * sc, 'gx': x0 - gb[0] * sc, 'edges': c['edges']})
        real = [L for L in letters if L['ch'] not in TRIV]
        if len(real) >= 2: res.append({'id': sh['id'], 'tag': t, 'letters': letters})
    return res

def lines(letters, fonts):
    """Agrupa en renglones (misma fuente, relleno, escala y línea base) -> [{text, font, fill, sc, base, x0, x1, letters}]"""
    out = []
    for L in sorted(letters, key=lambda a: a['x']):
        for ln in out:
            if ln['font'] == L['font'] and ln['fill'] == (L['g'], L['fill']) and abs(ln['base'] - L['base']) < 0.08 * L['sc'] * fonts.upm[L['font']] and abs(ln['sc'] - L['sc']) < 0.06 * L['sc']:
                ln['letters'].append(L); break
        else:
            out.append({'font': L['font'], 'fill': (L['g'], L['fill']), 'base': L['base'], 'sc': L['sc'], 'letters': [L]})
    res = []
    for ln in out:
        ls = ln['letters']; s = ''; prev = None
        upm = fonts.upm[ln['font']]; adv = fonts.adv.get(ln['font'], {})
        for a in ls:
            if prev is not None:
                expect = prev['gx'] + adv.get(prev['ch'], 0) * prev['sc']          # donde empezaría la siguiente letra
                if a['gx'] - expect > 0.12 * upm * a['sc']: s += ' '
            s += a['ch']; prev = a
        ln['text'] = s; ln['x0'] = ls[0]['x']; ln['x1'] = ls[-1]['x'] + ls[-1]['w']
        if len([c for c in s if c not in TRIV and c != ' ']) >= 2: res.append(ln)
    res.sort(key=lambda a: (round(a['base'] / 200.0), a['x0']))
    return res

if __name__ == '__main__':
    src = os.path.join(ROOT, 'original', 'Data', 'assets', 'Main.assets')
    fonts = Fonts(src)
    inv = scan(src, fonts)
    os.makedirs(os.path.join(ROOT, 'work', 'arte'), exist_ok=True)
    out = []
    with open(os.path.join(ROOT, 'work', 'arte', 'inventario.txt'), 'w', encoding='utf-8') as fh:
        for it in inv:
            ls = lines(it['letters'], fonts)
            if not ls: continue
            txt = ' / '.join('%s [%s %.0fpx f%d.%d]' % (l['text'], l['font'], l['sc'] * fonts.upm[l['font']] / 20, l['fill'][0], l['fill'][1]) for l in ls)
            fh.write('%d | %s\n' % (it['id'], txt)); out.append({'id': it['id'], 'lines': [{k: v for k, v in l.items() if k != 'letters'} for l in ls]})
    json.dump(out, open(os.path.join(ROOT, 'work', 'arte', 'inventario.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(out), 'formas con rótulos')
