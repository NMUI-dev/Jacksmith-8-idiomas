# -*- coding: utf-8 -*-
"""Formas vectoriales (DefineShape 1-4): lectura completa, reconstrucción de contornos y reconocimiento de
letras dibujadas (texto convertido a contornos) comparándolas con los glifos de las fuentes del propio SWF.

Uso: python scripts/swfshape.py inventario   -> work/arte/inventario.json  (formas que contienen letras)
"""
import struct, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swftool
from swfmod import BR, BW, sbits, read_rect, write_rect, Font, decode_shape, bbox as gbbox, pts as gpts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------ lectura de DefineShape
def _rgb(r, alpha):
    return (r.u(8), r.u(8), r.u(8), r.u(8) if alpha else 255)

def _matrix(r):
    r.align(); m = {}
    if r.u(1): n = r.u(5); m['s'] = (r.s_(n), r.s_(n))
    if r.u(1): n = r.u(5); m['r'] = (r.s_(n), r.s_(n))
    n = r.u(5); m['t'] = (r.s_(n), r.s_(n)); r.align()
    return m

def _gradient(r, ver, focal):
    r.align(); spread = r.u(2); interp = r.u(2); n = r.u(4); recs = []
    for _ in range(n): recs.append((r.u(8), _rgb(r, ver >= 3)))
    fp = None
    if focal: fp = r.s_(16)
    return {'spread': spread, 'interp': interp, 'recs': recs, 'focal': fp}

def _fillstyle(r, ver):
    t = r.u(8); f = {'type': t}
    if t == 0x00: f['color'] = _rgb(r, ver >= 3)
    elif t in (0x10, 0x12, 0x13): f['matrix'] = _matrix(r); f['grad'] = _gradient(r, ver, t == 0x13)
    elif t in (0x40, 0x41, 0x42, 0x43): f['bitmap'] = r.u(16); f['matrix'] = _matrix(r)
    else: raise ValueError('relleno %x' % t)
    return f

def _fillstyles(r, ver):
    r.align(); n = r.u(8)
    if n == 0xFF and ver >= 2: n = r.u(16)
    return [_fillstyle(r, ver) for _ in range(n)]

def _linestyles(r, ver):
    r.align(); n = r.u(8)
    if n == 0xFF: n = r.u(16)
    out = []
    for _ in range(n):
        if ver < 4: out.append({'width': r.u(16), 'color': _rgb(r, ver >= 3)})
        else:
            w = r.u(16); sc = r.u(2); js = r.u(2); hasfill = r.u(1); nh = r.u(1); nv = r.u(1); ph = r.u(1); r.u(5); nc = r.u(1); ec = r.u(2)
            l = {'width': w, 'startcap': sc, 'join': js, 'nohscale': nh, 'novscale': nv, 'pixelhint': ph, 'noclose': nc, 'endcap': ec}
            if js == 2: l['miter'] = r.u(16)
            if hasfill: l['fill'] = _fillstyle(r, ver)
            else: l['color'] = _rgb(r, True)
            out.append(l)
    return out

def parse_shape(tag, d):
    """-> dict(id, ver, bounds, groups=[{fills, lines, edges=[(x0,y0,x1,y1,cx,cy|None,f0,f1,ls)]}], cabecera bytes)"""
    ver = {2: 1, 22: 2, 32: 3, 83: 4}[tag]
    sid = struct.unpack_from('<H', d, 0)[0]
    b, o = read_rect(d, 2)
    eb = None; flags4 = None
    if ver == 4:
        eb, o = read_rect(d, o); flags4 = d[o]; o += 1
    r = BR(d, o)
    fills = _fillstyles(r, ver); lines = _linestyles(r, ver)
    r.align(); fb = r.u(4); lb = r.u(4)
    groups = [{'fills': fills, 'lines': lines, 'edges': []}]
    x = y = 0; f0 = f1 = ls = 0
    while True:
        if r.u(1) == 0:
            fl = r.u(5)
            if fl == 0: break
            if fl & 1: n = r.u(5); x = r.s_(n); y = r.s_(n)
            if fl & 2: f0 = r.u(fb)
            if fl & 4: f1 = r.u(fb)
            if fl & 8: ls = r.u(lb)
            if fl & 16:
                fills = _fillstyles(r, ver); lines = _linestyles(r, ver); r.align(); fb = r.u(4); lb = r.u(4)
                groups.append({'fills': fills, 'lines': lines, 'edges': []})
        else:
            if r.u(1):
                n = r.u(4) + 2
                if r.u(1): dx = r.s_(n); dy = r.s_(n)
                elif r.u(1): dx = 0; dy = r.s_(n)
                else: dx = r.s_(n); dy = 0
                groups[-1]['edges'].append((x, y, x + dx, y + dy, None, None, f0, f1, ls)); x += dx; y += dy
            else:
                n = r.u(4) + 2
                cx = x + r.s_(n); cy = y + r.s_(n); ax = cx + r.s_(n); ay = cy + r.s_(n)
                groups[-1]['edges'].append((x, y, ax, ay, cx, cy, f0, f1, ls)); x, y = ax, ay
    return {'id': sid, 'ver': ver, 'bounds': b, 'ebounds': eb, 'flags4': flags4, 'groups': groups}

# ------------------------------------------------------------------ contornos por relleno
def contours(group):
    """Encadena las aristas de cada relleno en contornos cerrados.
    -> [{'fill': idx, 'pts': [(x,y)...] (vértices de anclaje), 'segs': [...], 'edges': [índices de arista]}]"""
    byfill = {}
    for i, e in enumerate(group['edges']):
        x0, y0, x1, y1, cx, cy, f0, f1, ls = e
        if f1: byfill.setdefault(f1, []).append((x0, y0, x1, y1, cx, cy, i))
        if f0: byfill.setdefault(f0, []).append((x1, y1, x0, y0, cx, cy, i))       # invertida
    out = []
    for f, es in byfill.items():
        start = {}
        for e in es: start.setdefault((e[0], e[1]), []).append(e)
        used = set()
        for e in es:
            if id(e) in used: continue
            path = [e]; used.add(id(e)); p = (e[2], e[3]); p0 = (e[0], e[1]); ok = False
            for _ in range(100000):
                if p == p0: ok = True; break
                nxt = None
                for c in start.get(p, []):
                    if id(c) not in used: nxt = c; break
                if nxt is None: break
                path.append(nxt); used.add(id(nxt)); p = (nxt[2], nxt[3])
            if ok and len(path) >= 2:
                out.append({'fill': f, 'path': path, 'edges': [q[6] for q in path]})
    return out

def cbbox(path):
    xs = []; ys = []
    for e in path:
        xs += [e[0], e[2]]; ys += [e[1], e[3]]
        if e[4] is not None: xs.append(e[4]); ys.append(e[5])
    return min(xs), min(ys), max(xs), max(ys)

def area_centroid(path):
    """Área con signo y centroide de la poligonal de anclajes (suficiente para comparar)."""
    a = 0.0; cx = cy = 0.0
    for e in path:
        x0, y0, x1, y1 = e[0], e[1], e[2], e[3]
        cr = x0 * y1 - x1 * y0; a += cr; cx += (x0 + x1) * cr; cy += (y0 + y1) * cr
    if abs(a) < 1e-9: return 0.0, (0, 0)
    return a / 2.0, (cx / (3 * a), cy / (3 * a))

def signature(path):
    """Firma invariante a traslación, escala y punto de inicio: (nº de segmentos, relación de aspecto,
    área relativa, centroide relativo, perímetro relativo)."""
    x0, y0, x1, y1 = cbbox(path); w = x1 - x0; h = y1 - y0
    if w <= 0 or h <= 0: return None
    a, (cx, cy) = area_centroid(path)
    per = sum(math.hypot(e[2] - e[0], e[3] - e[1]) for e in path)
    return (len(path), w / h, abs(a) / (w * h), (cx - x0) / w, (cy - y0) / h, per / (w + h))

def glyph_paths(font):
    """{car: [contornos como listas de aristas (x0,y0,x1,y1,cx,cy)]} de una fuente."""
    out = {}
    for code, sh in zip(font.codes, font.shapes):
        if len(sh) < 2: continue
        try: cons = decode_shape(sh)
        except Exception: continue
        paths = []
        for c in cons:
            x, y = c['start']; p = []
            for s in c['segs']:
                if s[0] == 'L': p.append((x, y, s[1], s[2], None, None)); x, y = s[1], s[2]
                else: p.append((x, y, s[3], s[4], s[1], s[2])); x, y = s[3], s[4]
            if p: paths.append(p)
        if paths: out[chr(code)] = paths
    return out

class Matcher:
    def __init__(self, swf):
        _, _, tags = swftool.load(swf)
        self.fonts = {}; self.index = {}
        for t, p, q, e in swftool.iter_tags(tags):
            if t != 75: continue
            try: f = Font(tags[q:e])
            except Exception: continue
            name = f.name.rstrip(b'\0').decode()
            self.fonts[name] = f
            for ch, paths in glyph_paths(f).items():
                if not (ch.isalnum() or ch in '!?&\'.,:-+%#'): continue
                # contorno exterior = el de mayor caja
                big = max(paths, key=lambda p: (cbbox(p)[2] - cbbox(p)[0]) * (cbbox(p)[3] - cbbox(p)[1]))
                sg = signature(big)
                if sg is None: continue
                bb = cbbox(big)
                self.index.setdefault(sg[0], []).append((sg, name, ch, bb, len(paths)))
    def match(self, path):
        sg = signature(path)
        if sg is None or sg[0] < 4: return None
        best = None
        for g, name, ch, bb, nc in self.index.get(sg[0], []):
            d = abs(g[1] - sg[1]) / max(g[1], 1e-6) + abs(g[2] - sg[2]) * 2 + abs(g[3] - sg[3]) * 2 + abs(g[4] - sg[4]) * 2 + abs(g[5] - sg[5]) / g[5]
            if best is None or d < best[0]: best = (d, name, ch, bb)
        if best and best[0] < 0.06: return best
        return None

def inventory(swf):
    m = Matcher(swf)
    _, _, tags = swftool.load(swf)
    res = []
    for t, p, q, e in swftool.iter_tags(tags):
        if t not in (2, 22, 32, 83): continue
        try: sh = parse_shape(t, tags[q:e])
        except Exception as ex:
            res.append({'id': struct.unpack_from('<H', tags, q)[0], 'error': str(ex)}); continue
        letters = []
        for gi, g in enumerate(sh['groups']):
            for c in contours(g):
                mt = m.match(c['path'])
                if not mt: continue
                x0, y0, x1, y1 = cbbox(c['path']); gb = mt[3]
                scale = (y1 - y0) / float(gb[3] - gb[1])
                letters.append({'g': gi, 'fill': c['fill'], 'ch': mt[2], 'font': mt[1], 'd': round(mt[0], 4),
                                'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0, 'scale': round(scale, 5),
                                'base': round(y0 - gb[1] * scale, 1), 'n': len(c['path'])})
        if len(letters) >= 2:
            res.append({'id': sh['id'], 'ver': sh['ver'], 'bounds': sh['bounds'], 'letters': letters,
                        'nedges': sum(len(g['edges']) for g in sh['groups'])})
    return res

def read_lines(letters):
    """Agrupa letras por (fuente, relleno, línea base) y las ordena por x -> lista de cadenas."""
    groups = {}
    for L in letters:
        key = None
        for k in groups:
            if k[0] == L['font'] and k[1] == (L['g'], L['fill']) and abs(k[2] - L['base']) < max(40, L['h'] * 0.25): key = k; break
        if key is None: key = (L['font'], (L['g'], L['fill']), L['base']); groups[key] = []
        groups[key].append(L)
    out = []
    for k, ls in groups.items():
        ls.sort(key=lambda a: a['x'])
        # huecos grandes = espacio
        s = ''; prev = None
        for a in ls:
            if prev is not None and a['x'] - (prev['x'] + prev['w']) > 0.28 * max(a['h'], prev['h']) * 1.0 + 0.12 * EMH(a): s += ' '
            s += a['ch']; prev = a
        out.append({'font': k[0], 'fill': k[1], 'base': k[2], 'text': s, 'x': ls[0]['x'], 'n': len(ls), 'scale': ls[0]['scale']})
    out.sort(key=lambda a: (a['base'], a['x']))
    return out

def EMH(a): return a['scale'] * 20480 * 0.5

if __name__ == '__main__':
    src = os.path.join(ROOT, 'original', 'Data', 'assets', 'Main.assets')
    inv = inventory(src)
    os.makedirs(os.path.join(ROOT, 'work', 'arte'), exist_ok=True)
    json.dump(inv, open(os.path.join(ROOT, 'work', 'arte', 'inventario.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    err = [i for i in inv if 'error' in i]
    print(len(inv) - len(err), 'formas con letras;', len(err), 'formas con error de lectura')
    for i in inv:
        if 'error' in i: continue
        ls = read_lines(i['letters'])
        print(i['id'], '|', ' / '.join('%s [%s]' % (l['text'], l['font'].replace('Alegreya Sans', 'AS').replace('ExtraBold', 'XB')) for l in ls))
