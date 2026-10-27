# -*- coding: utf-8 -*-
"""Inventario de formas por pantalla: quién coloca a quién dentro del SWF (sprites, botones, formas, textos).

  python scripts/formas.py clases [filtro]            lista «id clase» (SymbolClass)
  python scripts/formas.py arbol <clase|id> [prof]    árbol de hijos (id, tipo, nombre de instancia, fotograma)
  python scripts/formas.py uso <id>                   quién usa ese carácter (cadena de padres hasta una clase)
  python scripts/formas.py hoja <clase|id> <png>      hoja de contacto con todas las formas/bitmaps del árbol
  python scripts/formas.py ids <png> <id> <id> ...    hoja de contacto de esos ids (formas de work/shp, bitmaps de work/img)
  python scripts/formas.py rango <png> <a> <b>        hoja de contacto de las formas con id entre a y b
Opción --swf <ruta> (por defecto el original).  Las miniaturas salen de work/shp/<id>.png (exportadas con FFDec:
  java -jar tools/ffdec/ffdec.jar -format shape:png -export shape work/shp original/Data/assets/Main.assets).
"""
import sys, os, struct
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'pydeps'))
import swftool
from swfmod import BR

TIPOS = {2: 'forma', 22: 'forma', 32: 'forma', 83: 'forma', 39: 'sprite', 34: 'boton', 7: 'boton', 11: 'texto', 33: 'texto',
         37: 'campo', 6: 'bitmap', 21: 'bitmap', 35: 'bitmap', 20: 'bitmap', 36: 'bitmap', 90: 'bitmap', 75: 'fuente',
         48: 'fuente', 46: 'morph', 84: 'morph', 87: 'binario', 14: 'sonido', 60: 'video'}

def _skip_matrix(r):
    r.align()
    if r.u(1): n = r.u(5); r.u(n); r.u(n)
    if r.u(1): n = r.u(5); r.u(n); r.u(n)
    n = r.u(5); tx = r.s_(n); ty = r.s_(n); r.align()
    return tx, ty

def _skip_cx(r):
    r.align(); a = r.u(1); m = r.u(1); n = r.u(4)
    if m: r.u(4 * n)
    if a: r.u(4 * n)
    r.align()

def _u16(r, d):
    r.align(); p = r.byte; r.p = (p + 2) * 8
    return struct.unpack_from('<H', d, p)[0]

def _place(t, d):
    """-> (profundidad, id o None, nombre, (tx,ty))"""
    r = BR(d); f = r.u(8); f2 = r.u(8) if t == 70 else 0
    depth = _u16(r, d); cid = None; name = ''; pos = None
    if t == 70 and (f2 & 0x08 or (f2 & 0x10 and f & 0x02)):
        p = r.byte; z = d.index(b'\0', p); r.p = (z + 1) * 8
    if f & 0x02: cid = _u16(r, d)
    if f & 0x04: pos = _skip_matrix(r)
    if f & 0x08: _skip_cx(r)
    if f & 0x10: _u16(r, d)
    if f & 0x20:
        p = r.byte; z = d.index(b'\0', p); name = d[p:z].decode('latin1')
    return depth, cid, name, pos

class Swf:
    def __init__(self, path):
        self.ver, self.head, self.tags = swftool.load(path)
        self.tipo = {}; self.hijos = {}; self.clase = {}; self.pos = {}
        T = self.tags
        for t, p, q, e in swftool.iter_tags(T):
            if t in TIPOS:
                cid = struct.unpack_from('<H', T, q)[0]; self.tipo[cid] = TIPOS[t]; self.pos[cid] = (t, p, q, e)
            if t == 39:
                cid = struct.unpack_from('<H', T, q)[0]; ch = []; fr = 1
                for t2, p2, q2, e2 in swftool.iter_tags(T[q + 4:e]):
                    if t2 == 1: fr += 1
                    elif t2 in (26, 70):
                        try:
                            depth, c2, name, pos = _place(t2, T[q + 4 + q2:q + 4 + e2])
                            if c2 is not None: ch.append((c2, name, fr, depth, pos))
                        except Exception: pass
                    elif t2 == 0: break
                self.hijos[cid] = ch
            elif t == 34:
                cid = struct.unpack_from('<H', T, q)[0]; ch = []
                try:
                    r = BR(T[q + 5:e])
                    while True:
                        fl = r.u(8)
                        if fl == 0: break
                        c2 = r.u(8) | (r.u(8) << 8); r.u(16); _skip_matrix(r); _skip_cx(r)
                        if fl & 0x10: break
                        if fl & 0x20: r.u(8)
                        ch.append((c2, 'estado%X' % (fl & 15), 1, 0, None))
                except Exception: pass
                self.hijos[cid] = ch
            elif t == 76:
                n = struct.unpack_from('<H', T, q)[0]; p3 = q + 2
                for _ in range(n):
                    cid = struct.unpack_from('<H', T, p3)[0]; z = T.index(b'\0', p3 + 2)
                    self.clase[cid] = T[p3 + 2:z].decode(); p3 = z + 1
            elif t in (2, 22, 32, 83):
                pass
        self.padres = {}
        for par, ch in self.hijos.items():
            for c in ch: self.padres.setdefault(c[0], set()).add(par)
    def busca(self, s):
        if s.isdigit(): return int(s)
        for cid, n in self.clase.items():
            if n == s: return cid
        m = [cid for cid, n in self.clase.items() if s.lower() in n.lower()]
        if len(m) == 1: return m[0]
        raise SystemExit('clase %r: %s' % (s, ', '.join('%d %s' % (c, self.clase[c]) for c in m) or 'no existe'))
    def arbol(self, cid, prof=99, ind=0, name='', fr=1, seen=None, out=None):
        out = [] if out is None else out; seen = set() if seen is None else seen
        out.append('%s%d %s%s%s%s' % ('  ' * ind, cid, self.tipo.get(cid, '?'), ' «%s»' % name if name else '',
                                       ' f%d' % fr if fr > 1 else '', ' [%s]' % self.clase[cid] if cid in self.clase else ''))
        if ind >= prof: return out
        if cid in seen and self.hijos.get(cid): out[-1] += ' (ya listado)'; return out
        seen.add(cid)
        vistos = set()
        for c, n, f, dp, pos in self.hijos.get(cid, []):
            if (c, n) in vistos: continue
            vistos.add((c, n)); self.arbol(c, prof, ind + 1, n, f, seen, out)
        return out
    def hojas(self, cid, acc=None):
        acc = [] if acc is None else acc
        if self.tipo.get(cid) in ('forma', 'bitmap', 'morph'):
            if cid not in acc: acc.append(cid)
        for c in self.hijos.get(cid, []):
            if c[0] != cid: self.hojas(c[0], acc)
        return acc
    def uso(self, cid, ind=0, out=None, seen=None):
        out = [] if out is None else out; seen = set() if seen is None else seen
        for par in sorted(self.padres.get(cid, [])):
            nm = [c[1] for c in self.hijos[par] if c[0] == cid and c[1]]
            out.append('%s<- %d %s%s%s' % ('  ' * ind, par, self.tipo.get(par, '?'), ' [%s]' % self.clase[par] if par in self.clase else '',
                                            ' como «%s»' % nm[0] if nm else ''))
            if par not in seen and ind < 8: seen.add(par); self.uso(par, ind + 1, out, seen)
        return out
    def bitmaps_de(self, sid):
        """bitmaps usados como relleno por una forma"""
        import swfshape
        t, p, q, e = self.pos[sid]; res = []
        try:
            sh = swfshape.parse_shape(t, self.tags[q:e])
            for g in sh['groups']:
                for f in g['fills']:
                    if 'bitmap' in f and f['bitmap'] != 65535: res.append(f['bitmap'])
        except Exception: pass
        return res

def hoja(ids, png, T=170, C=7, dirs=None):
    from PIL import Image, ImageDraw
    dirs = dirs or [os.path.join(ROOT, 'work', 'shp'), os.path.join(ROOT, 'work', 'img')]
    cells = []
    for i in ids:
        for d in dirs:
            f = os.path.join(d, '%d.png' % i)
            if not os.path.exists(f): f = os.path.join(d, '%d.jpg' % i)
            if os.path.exists(f): cells.append((i, f)); break
    R = max(1, (len(cells) + C - 1) // C)
    sheet = Image.new('RGB', (C * T, R * (T + 14)), (95, 95, 115)); d = ImageDraw.Draw(sheet)
    for k, (i, f) in enumerate(cells):
        im = Image.open(f).convert('RGBA'); im.thumbnail((T - 6, T - 6))
        x = (k % C) * T + 3; y = (k // C) * (T + 14)
        sheet.paste(im, (x + (T - 6 - im.size[0]) // 2, y + 14 + (T - 6 - im.size[1]) // 2), im); d.text((x, y + 1), str(i), fill=(255, 255, 0))
    sheet.save(png); print(png, len(cells), 'de', len(ids))

if __name__ == '__main__':
    a = sys.argv[1:]; swf = os.path.join(ROOT, 'original', 'Data', 'assets', 'Main.assets')
    if '--swf' in a: i = a.index('--swf'); swf = a[i + 1]; del a[i:i + 2]
    S = Swf(swf)
    if a[0] == 'clases':
        for cid in sorted(S.clase):
            if len(a) < 2 or a[1].lower() in S.clase[cid].lower(): print(cid, S.clase[cid], S.tipo.get(cid, '?'))
    elif a[0] == 'arbol': print('\n'.join(S.arbol(S.busca(a[1]), int(a[2]) if len(a) > 2 else 99)))
    elif a[0] == 'uso': print('\n'.join(S.uso(int(a[1]))))
    elif a[0] == 'hoja':
        ids = S.hojas(S.busca(a[1])); print(' '.join(map(str, ids))); hoja(ids, a[2])
    elif a[0] == 'ids': hoja([int(x) for x in a[2:]], a[1])
    elif a[0] == 'rango':
        hoja([i for i in sorted(S.tipo) if int(a[2]) <= i <= int(a[3]) and S.tipo[i] in ('forma', 'bitmap', 'morph')], a[1])
