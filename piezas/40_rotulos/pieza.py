# -*- coding: utf-8 -*-
"""Pieza 40 — RÓTULOS DIBUJADOS por idioma (v2, 13-oct-2026).

Muchos letreros del juego no son texto sino formas vectoriales (letras convertidas a contornos, a veces dentro de
la misma forma que el fondo del letrero). Para cada entrada de `rotulos.json` se fabrica UNA forma nueva por idioma:
   grupos del original que no son letras (fondo, flechas...)  +  las letras traducidas, dibujadas con los glifos
   de una fuente incrustada del propio juego y con las MISMAS capas que el original (contorno, sombra desplazada,
   cara de dos tonos, degradado), deducidas de la forma original.
La forma original pasa a ser un sprite con hijos «jm_en» (la original) y «jm_<idioma>_0» (la nueva); el núcleo
(JM.fixArt) enseña uno u otro al cambiar de idioma en vivo.

rotulos.json — lista de entradas:
  id       id de la forma original                       en / es / ...   texto original y traducciones («|» = renglón)
  fuente   nombre de la fuente incrustada (scripts/formas.py no; ver swftool.fonts)
  quitar   grupos de la forma que son letras (por defecto: el último). "todo" = todos.
  cara     [grupo, relleno] (o lista de ellos) cuya caja es la cara de las letras (por defecto: el relleno con más
           contornos del último grupo quitado)
  hueco    [x0, x1] en px de la forma: ancho disponible para el texto (por defecto: el del original)
  huecoy   [y0, y1] igual en vertical (solo modo vertical)
  vertical true = letras apiladas (estandartes)          afin  [a, b, c, d] deformación (libros en perspectiva)
  capas    lista manual de capas (si no, se deducen)     union "inglete" | "redonda"
  estrecha mínimo de estrechamiento horizontal antes de reducir (por defecto 0.8)
  mayus    true = pasa la traducción a mayúsculas
Prueba suelta (sin construir todo):  python piezas/40_rotulos/pieza.py <swf base> <swf salida>
"""
import os, sys, json, struct

RES = ('caja', 'parche', 'techo', '_anc', 'quitar_x', 'alinea', 'versalitas', 'condensa', 'id', 'en', 'fuente', 'quitar', 'cara', 'hueco', 'huecoy', 'vertical', 'afin', 'capas', 'union', 'estrecha', 'mayus',
       'nota', 'interlinea', 'dy', 'dx', 'escala', 'tracking')

def aplicar(ctx):
    here = os.path.dirname(os.path.abspath(__file__))
    ctx.post_swf.append(lambda c: rotular(c.swf, c.swf, json.load(open(os.path.join(here, 'rotulos.json'), encoding='utf-8')), c.root))

# ---------------------------------------------------------------- escritura de DefineShape4
def _imports(root):
    sys.path.insert(0, os.path.join(root, 'scripts'))
    import swftool, swfshape, swfmod
    return swftool, swfshape, swfmod

def _w_rgba(w, c):
    for v in (c[0], c[1], c[2], c[3] if len(c) > 3 else 255): w.u(int(v), 8)

def _w_matrix(w, m, sbits):
    w.align()
    for k in ('s', 'r'):
        if k in m:
            n = sbits(*m[k]); w.u(1, 1); w.u(n, 5); w.s_(m[k][0], n); w.s_(m[k][1], n)
        else: w.u(0, 1)
    t = m.get('t', (0, 0)); n = sbits(*t) if (t[0] or t[1]) else 0
    w.u(n, 5)
    if n: w.s_(t[0], n); w.s_(t[1], n)
    w.align()

def _w_fill(w, f, sbits):
    w.align(); t = f['type']; w.u(t, 8)
    if t == 0: _w_rgba(w, f['color'])
    elif t in (0x10, 0x12, 0x13):
        _w_matrix(w, f['matrix'], sbits); g = f['grad']
        w.u(g.get('spread', 0), 2); w.u(g.get('interp', 0), 2); w.u(len(g['recs']), 4)
        for ratio, col in g['recs']: w.u(int(ratio), 8); _w_rgba(w, col)
        if t == 0x13: w.s_(g.get('focal') or 0, 16)
    else:
        w.u(f['bitmap'], 16); _w_matrix(w, f['matrix'], sbits)

def _w_styles(w, fills, lines, sbits):
    w.align()
    if len(fills) >= 255: w.u(255, 8); w.u(len(fills) & 255, 8); w.u(len(fills) >> 8, 8)
    else: w.u(len(fills), 8)
    for f in fills: _w_fill(w, f, sbits)
    w.align()
    if len(lines) >= 255: w.u(255, 8); w.u(len(lines) & 255, 8); w.u(len(lines) >> 8, 8)
    else: w.u(len(lines), 8)
    for l in lines:
        w.align()
        if 'w' in l: w.u(l['w'] & 255, 8); w.u(l['w'] >> 8, 8)          # nuestra: ancho en twips
        else: w.u(l['width'], 16)                                         # leída (mismo patrón de bits)
        js = l.get('join', 0); w.u(l.get('startcap', 0), 2); w.u(js, 2); hasfill = 1 if 'fill' in l else 0
        w.u(hasfill, 1); w.u(l.get('nohscale', 0), 1); w.u(l.get('novscale', 0), 1); w.u(l.get('pixelhint', 0), 1)
        w.u(0, 5); w.u(l.get('noclose', 0), 1); w.u(l.get('endcap', 0), 2)
        if js == 2:
            mi = l.get('miter', 0x0300)
            if 'w' in l: w.u(mi & 255, 8); w.u(mi >> 8, 8)
            else: w.u(mi, 16)
        if hasfill: _w_fill(w, l['fill'], sbits)
        else: _w_rgba(w, l.get('color', (0, 0, 0, 255)))
    w.align()
    fb = len(fills).bit_length(); lb = len(lines).bit_length()
    w.u(fb, 4); w.u(lb, 4)
    return fb, lb

def write_shape4(swfmod, swftool, sid, groups):
    """groups: [{'fills': [...], 'lines': [...], 'paths': [{'f0','f1','ls','start','segs'}]}] -> etiqueta DefineShape4"""
    BW, sbits, write_rect = swfmod.BW, swfmod.sbits, swfmod.write_rect
    xs = []; ys = []; mg = 20
    for g in groups:
        for l in g['lines']: mg = max(mg, l.get('w', 40) // 2 + 20)
        for p in g['paths']:
            xs.append(p['start'][0]); ys.append(p['start'][1])
            for s in p['segs']: xs += list(s[1::2]); ys += list(s[2::2])
    if not xs: xs = [0]; ys = [0]
    x0, x1, y0, y1 = int(min(xs)), int(max(xs)), int(min(ys)), int(max(ys))
    d = struct.pack('<H', sid) + write_rect(x0 - mg, x1 + mg, y0 - mg, y1 + mg) + write_rect(x0, x1, y0, y1) + bytes([1])
    w = BW(); fb = lb = 0
    for gi, g in enumerate(groups):
        if gi == 0: fb, lb = _w_styles(w, g['fills'], g['lines'], sbits)
        else:
            w.u(0, 1); w.u(16, 5); fb, lb = _w_styles(w, g['fills'], g['lines'], sbits)
        for p in g['paths']:
            x, y = int(round(p['start'][0])), int(round(p['start'][1]))
            w.u(0, 1); w.u(15, 5); n = sbits(x, y); w.u(n, 5); w.s_(x, n); w.s_(y, n)
            w.u(p.get('f0', 0), fb); w.u(p.get('f1', 0), fb); w.u(p.get('ls', 0), lb)
            for s in p['segs']:
                if s[0] == 'L':
                    nx, ny = int(round(s[1])), int(round(s[2])); dx, dy = nx - x, ny - y
                    if dx == 0 and dy == 0: continue
                    n = max(2, sbits(dx, dy)); w.u(1, 1); w.u(1, 1); w.u(n - 2, 4)
                    if dx and dy: w.u(1, 1); w.s_(dx, n); w.s_(dy, n)
                    elif dx == 0: w.u(0, 1); w.u(1, 1); w.s_(dy, n)
                    else: w.u(0, 1); w.u(0, 1); w.s_(dx, n)
                    x, y = nx, ny
                else:
                    cx, cy, nx, ny = (int(round(v)) for v in s[1:])
                    a, b, c2, e2 = cx - x, cy - y, nx - cx, ny - cy
                    n = max(2, sbits(a, b, c2, e2)); w.u(1, 1); w.u(0, 1); w.u(n - 2, 4)
                    w.s_(a, n); w.s_(b, n); w.s_(c2, n); w.s_(e2, n); x, y = nx, ny
    w.u(0, 6)
    return swftool.mk_tag(83, d + w.bytes()), (x0 - mg, y0 - mg)

def _vgrad(stops, cx):
    """degradado vertical: stops = [[y_px, [r,g,b]], ...] de arriba abajo -> relleno 0x10"""
    ya = stops[0][0] * 20.0; yb = stops[-1][0] * 20.0; b16 = int(round((yb - ya) / 32768.0 * 65536))
    recs = [(max(0, min(255, int(round((y * 20.0 - ya) / (yb - ya) * 255)))), tuple(c) + (255,) if len(c) == 3 else tuple(c)) for y, c in stops]
    return {'type': 0x10, 'matrix': {'s': (0, 0), 'r': (b16, -b16), 't': (int(cx), int((ya + yb) / 2))}, 'grad': {'spread': 0, 'interp': 0, 'recs': recs}}

def _keep_group(g, drop=None):
    """grupo leído por swfshape.parse_shape -> grupo para write_shape4 (mismas aristas y estilos)"""
    paths = []; cur = None; end = None
    for ei, (x0, y0, x1, y1, cx, cy, f0, f1, ls) in enumerate(g['edges']):
        if drop is not None and ei in drop: cur = None; continue
        if cur is None or end != (x0, y0) or (cur['f0'], cur['f1'], cur['ls']) != (f0, f1, ls):
            cur = {'f0': f0, 'f1': f1, 'ls': ls, 'start': (x0, y0), 'segs': []}; paths.append(cur)
        cur['segs'].append(('L', x1, y1) if cx is None else ('Q', cx, cy, x1, y1)); end = (x1, y1)
    fills = []
    for f in g['fills']:
        f = dict(f)
        if f['type'] == 0 and len(f['color']) == 3: f['color'] = tuple(f['color']) + (255,)
        fills.append(f)
    return {'fills': fills, 'lines': [dict(l) for l in g['lines']], 'paths': paths}

# ---------------------------------------------------------------- texto -> contornos
def _bbox(cons):
    xs = []; ys = []
    for k in cons:
        xs.append(k['start'][0]); ys.append(k['start'][1])
        for s in k['segs']: xs += list(s[1::2]); ys += list(s[2::2])
    return min(xs), min(ys), max(xs), max(ys)

def _aff(cons, a, b, c, d, tx, ty):
    """(x, y) -> (a·x + c·y + tx, b·x + d·y + ty)"""
    f = lambda x, y: (a * x + c * y + tx, b * x + d * y + ty)
    out = []
    for k in cons:
        segs = []
        for s in k['segs']:
            if s[0] == 'L': segs.append(('L',) + f(s[1], s[2]))
            else: segs.append(('Q',) + f(s[1], s[2]) + f(s[3], s[4]))
        out.append({'f0': k['f0'], 'f1': k['f1'], 'start': f(*k['start']), 'segs': segs})
    return out

def _fix_buttons(swftool, swfmod, tags, conv, stats):
    """Un sprite como ZONA ACTIVA (hit) de un botón cuelga el reproductor: en los botones que usan una forma convertida
    también como zona activa, ese estado vuelve a apuntar a la forma original (copia «jm_en»)."""
    BR = swfmod.BR; out = bytearray(); n = 0
    for t, p, q, e in swftool.iter_tags(tags):
        if t != 34: out += tags[p:e]; continue
        d = bytearray(tags[q:e]); o = 5; add = b''; changed = False
        try:
            while d[o] != 0:
                fl = d[o]; cid = struct.unpack_from('<H', d, o + 1)[0]
                r = BR(bytes(d), o + 5)
                r.align()
                if r.u(1): k = r.u(5); r.u(2 * k)
                if r.u(1): k = r.u(5); r.u(2 * k)
                k = r.u(5); r.u(2 * k); r.align()
                ha = r.u(1); hm = r.u(1); k = r.u(4)
                if hm: r.u(4 * k)
                if ha: r.u(4 * k)
                r.align(); end = r.byte
                if fl & 0x30: raise ValueError('filtros')
                if cid in conv and (fl & 0x08):
                    if fl & 0x07:
                        d[o] = fl & ~0x08; add += bytes([0x08]) + struct.pack('<H', conv[cid]) + bytes(d[o + 3:end])
                    else: struct.pack_into('<H', d, o + 1, conv[cid])
                    changed = True
                o = end
        except Exception: out += tags[p:e]; continue
        if changed:
            n += 1
            if add:
                d[o:o] = add; ao = struct.unpack_from('<H', d, 3)[0]
                if ao: struct.pack_into('<H', d, 3, ao + len(add))
            out += swftool.mk_tag(34, bytes(d))
        else: out += tags[p:e]
    stats.append(n)
    return bytes(out)

def rotular(swf_in, swf_out, lista, root, verbose=True):
    swftool, swfshape, swfmod = _imports(root)
    Font, decode_shape = swfmod.Font, swfmod.decode_shape
    ver, head, tags = swftool.load(swf_in)
    fonts = {}; shapes = {}; maxid = 0
    for t, p, q, e in swftool.iter_tags(tags):
        if t == 75:
            try: f = Font(tags[q:e]); fonts[f.name.rstrip(b'\0').decode()] = f
            except Exception: pass
        if t in (2, 22, 32, 83): shapes[struct.unpack_from('<H', tags, q)[0]] = (t, p, q, e)
        if t in (2, 22, 32, 83, 39, 37, 11, 33, 75, 46, 84, 34, 7, 20, 21, 35, 36, 6, 14, 87, 60, 91, 48, 10, 13, 90):
            maxid = max(maxid, struct.unpack_from('<H', tags, q)[0])
    nextid = [maxid + 1]
    def newid():
        nextid[0] += 1; return nextid[0] - 1

    def glyphs(font, ch):
        i = font.idx(ch)
        if i is None: raise SystemExit('la fuente %s no tiene %r' % (font.name, ch))
        return (decode_shape(font.shapes[i]) if len(font.shapes[i]) > 1 else []), font.adv[i]

    def line(font, text, track=0.0, vers=None):
        x = 0.0; cons = []
        for ch in text:
            k = 1.0
            if vers and ch != ch.upper() and font.idx(ch.upper()) is not None: ch = ch.upper(); k = vers
            g, adv = glyphs(font, ch)
            cons += _aff(g, k, 0, 0, k, x, 0); x += (adv + track) * k
        return cons

    def stack(font, text, step):
        """letras apiladas: cada una centrada en x=0, líneas base separadas `step`"""
        cons = []
        for i, ch in enumerate(text):
            g, adv = glyphs(font, ch)
            if not g: continue
            b = _bbox(g); cons += _aff(g, 1, 0, 0, 1, -(b[0] + b[2]) / 2.0, i * step)
        return cons

    def place(depth, cid, name):
        return swftool.mk_tag(26, bytes([0x22]) + struct.pack('<HH', depth, cid) + name.encode() + b'\0')

    rep = {}; hechos = 0; conv = set(); informe = []
    for r in lista:
        sid = r['id']
        if sid not in shapes: print('   rótulo', sid, 'no existe'); continue
        if r['fuente'] not in fonts: print('   rótulo', sid, 'sin fuente', r['fuente']); continue
        t, p, q, e = shapes[sid]
        sh = swfshape.parse_shape(t, tags[q:e]); G = sh['groups']; font = fonts[r['fuente']]
        quitar = r.get('quitar', [len(G) - 1])
        if quitar == 'todo': quitar = list(range(len(G)))
        # ---- cajas de cada relleno de los grupos de letras
        items = []
        for gi in quitar:
            cs = swfshape.contours(G[gi])
            for fi, f in enumerate(G[gi]['fills'], 1):
                mine = [c for c in cs if c['fill'] == fi]
                if not mine: continue
                bb = [swfshape.cbbox(c['path']) for c in mine]
                if 'quitar_x' in r: bb = [b for b in bb if r['quitar_x'][0] * 20.0 <= (b[0] + b[2]) / 2.0 <= r['quitar_x'][1] * 20.0]
                if not bb: continue
                items.append({'g': gi, 'f': fi, 'fill': f, 'n': len(mine),
                              'box': (min(b[0] for b in bb), min(b[1] for b in bb), max(b[2] for b in bb), max(b[3] for b in bb))})
        if 'caja' in r:                                       # letras dentro de un mapa de bits: la caja de la cara se da a mano
            R = tuple(v * 20.0 for v in r['caja']); cset = set()
        else:
            if not items: print('   rótulo', sid, 'sin contornos de letras'); continue
            cara = r.get('cara')
            if cara is None:
                last = [it for it in items if it['g'] == quitar[-1]]
                m_ = min(last, key=lambda it: it['n']); cara = [[m_['g'], m_['f']]]
            elif cara and not isinstance(cara[0], list): cara = [cara]
            cset = set((c[0], c[1]) for c in cara)
            cb = [it['box'] for it in items if (it['g'], it['f']) in cset]
            R = (min(b[0] for b in cb), min(b[1] for b in cb), max(b[2] for b in cb), max(b[3] for b in cb))
        RW = float(R[2] - R[0]); RH = float(R[3] - R[1])
        # ---- capas (deducidas del original o dadas a mano)
        capas = r.get('capas')
        if capas is None:
            capas = []
            for it in items:
                b = it['box']; exl = R[0] - b[0]; exr = b[2] - R[2]; ext = R[1] - b[1]; exb = b[3] - R[3]
                cut_b = exb < -0.2 * RH; cut_t = ext < -0.2 * RH
                if exr < -0.25 * RW or exl < -0.25 * RW: informe.append('%d: relleno g%d f%d parcial en x, omitido' % (sid, it['g'], it['f'])); continue
                if cut_t or cut_b:
                    sides = ([] if cut_t else [ext]) + ([] if cut_b else [exb]) or [0.0]; dx = dy = 0.0
                else:
                    sides = [exl, exr, ext, exb]; dx = (exr - exl) / 2.0; dy = (exb - ext) / 2.0
                ex = max(0.0, sum(sides) / len(sides))
                if ex < 12: ex = 0                                  # < 0,6 px: no es contorno, es un filo desplazado (bisel)
                else: dx = 0 if abs(dx) < 3 else dx; dy = 0 if abs(dy) < 3 else dy
                c = {'fill': it['fill'], 'e': ex, 'dx': dx, 'dy': dy, 'g': it['g'], 'esc': (it['g'], it['f']) in cset}
                if cut_t or cut_b: c['banda'] = (b[1] if cut_t else None, b[3] if cut_b else None)
                capas.append(c)
            capas.sort(key=lambda c: (quitar.index(c['g']), -c['e'], 1 if 'banda' in c else 0, 1 if c['esc'] else 0))
        else:
            capas = [dict(c, fill=(_vgrad(c['grad'], 0) if 'grad' in c else {'type': 0, 'color': tuple(c['color'])}), e=c.get('borde', 0) * 20.0, dx=c.get('dx', 0) * 20.0, dy=c.get('dy', 0) * 20.0) for c in capas]
        # ---- medida del texto inglés con la fuente: escala, línea base, interletra
        afin = r.get('afin'); cx0 = (R[0] + R[2]) / 2.0; cy0 = (R[1] + R[3]) / 2.0
        def build(text, s, sx, track, step):
            """-> contornos en coordenadas de fuente ya escaladas (sin colocar)"""
            if r.get('vertical'):
                cons = stack(font, text, step)
                return _aff(cons, sx, 0, 0, s, 0, 0)
            ls = text.split('|'); cons = []
            for i, l in enumerate(ls):
                k = line(font, l, track, r.get('versalitas')); b = _bbox(k)
                cons += _aff(k, sx, 0, 0, s, -(b[0] + b[2]) / 2.0 * sx, i * step * s)
            return cons
        en = r['en']; nl = en.count('|') + 1; cond = bool(r.get('condensa'))
        Hb = _bbox(line(font, 'H')); hcap = float(Hb[3] - Hb[1])
        if r.get('vertical'):
            wmax = max((_bbox(glyphs(font, ch)[0])[2] - _bbox(glyphs(font, ch)[0])[0]) for ch in en)
            s = RW / wmax; n = len(en)
            lastb = _bbox(glyphs(font, en[-1])[0]); firstb = _bbox(glyphs(font, en[0])[0])
            step = ((RH / s) - (lastb[3] - firstb[1])) / max(1, n - 1)
            track = 0.0
        else:
            one = [_bbox(line(font, l, 0.0, r.get('versalitas'))) for l in en.split('|')]
            if nl == 1:
                s = RH / float(one[0][3] - one[0][1]); step = 0.0
            else:
                s = RW / float(max(b[2] - b[0] for b in one))
                step = ((RH / s) - (one[-1][3] - one[0][1])) / (nl - 1)
            if 'interlinea' in r: step = r['interlinea'] * hcap
            wen = max(b[2] - b[0] for b in one) * s; nch = max(len(l) for l in en.split('|'))
            track = 0.0
            if nl == 1 and nch > 1:
                if abs(RW - wen) <= 0.25 * RW: cond = True                      # misma fuente, estrechada/ensanchada por el dibujante
                else:
                    informe.append('%d: «%s» con %s mide %.0f px y el original %.0f px (¿otra fuente?)' % (sid, en, r['fuente'], wen / 20, RW / 20)); track = 0.0
            if 'tracking' in r: track = r['tracking'] * hcap
        if 'escala' in r: s *= r['escala']
        kx = 1.0
        if cond: kx = RW / wen                              # la fuente del original va estrechada
        enc = build(en, s, s * kx, track, step)
        if afin: enc = _aff(enc, afin[0], afin[1], afin[2], afin[3], 0, 0)
        eb = _bbox(enc)
        ox = cx0 - (eb[0] + eb[2]) / 2.0; oy = R[3] - eb[3]            # coloca el inglés sobre el original (centro x, base)
        hueco = [v * 20.0 for v in r['hueco']] if 'hueco' in r else [R[0], R[2]]
        huecoy = [v * 20.0 for v in r['huecoy']] if 'huecoy' in r else [R[1], R[3]]
        extra = []; orig = newid()
        for lang, txt in r.items():
            if lang in RES: continue
            if r.get('mayus'): txt = txt.upper()
            s2 = s; sx = s * kx
            for _ in range(3):
                tc = build(txt, s2, sx, track, step)
                if afin: tc = _aff(tc, afin[0], afin[1], afin[2], afin[3], 0, 0)
                tb = _bbox(tc); w = tb[2] - tb[0]; h = tb[3] - tb[1]
                if r.get('vertical'):
                    lim = huecoy[1] - min(huecoy[0], R[1])
                    if h <= lim + 1: break
                    k = lim / h; s2 *= k; sx *= k
                else:
                    lim = hueco[1] - hueco[0]
                    if w <= lim + 1: break
                    k = lim / w; mn = r.get('estrecha', 0.8)
                    if sx / s2 * k >= mn: sx *= k
                    else:
                        k2 = k * (sx / s2) / mn; sx = s2 * k2 * mn; s2 *= k2
            anc = False
            if 'techo' in r and not r.get('vertical') and not afin:
                base_en = oy + (nl - 1) * step * s; top = base_en + tb[1]; lim_t = r['techo'] * 20.0
                if top < lim_t - 1 and tb[1] < 0:
                    kt = (base_en - lim_t) / float(base_en - top); s2 *= kt; sx *= kt
                    tc = build(txt, s2, sx, track, step); tb = _bbox(tc); anc = True
            # colocación: centrado en el hueco; misma línea base (la base del último renglón, reducida respecto del centro)
            if r.get('vertical'):
                dx = cx0 - (tb[0] + tb[2]) / 2.0; dy = R[1] - tb[1]                 # apiladas: empiezan donde el original
                if tb[3] + dy > huecoy[1]: dy = huecoy[1] - tb[3]
            else:
                dx = (hueco[0] + hueco[1]) / 2.0 - (tb[0] + tb[2]) / 2.0
                if r.get('alinea') == 'der': dx = hueco[1] - tb[2]
                elif r.get('alinea') == 'izq': dx = hueco[0] - tb[0]
                # la línea base de «H» (y=0 del último renglón) queda donde estaba; si se redujo, se centra en altura
                base_en = oy + (nl - 1) * step * s
                nl2 = txt.count('|') + 1
                if afin: dy = cy0 - (tb[1] + tb[3]) / 2.0
                elif (s2 == s or anc) and nl2 == nl: dy = base_en - (nl2 - 1) * step * s2
                else:
                    blk = _bbox(build('H' + '|H' * (nl2 - 1), s2, s2, 0, step)); dy = cy0 - (blk[1] + blk[3]) / 2.0
            dx += r.get('dx', 0) * 20.0; dy += r.get('dy', 0) * 20.0
            tc = _aff(tc, 1, 0, 0, 1, dx, dy); k = s2 / s
            parts = []
            keep = [_keep_group(g) for gi, g in enumerate(G) if gi not in quitar]
            if not quitar: keep = []; extra.append((lang, orig, b'', (sh['bounds'][0], sh['bounds'][2])))   # nada que quitar: debajo va la forma original tal cual (no se reescribe su mapa de bits)
            if 'quitar_x' in r:                                   # adornos (flechas) de la cara fuera del tramo: se calcan con las letras
                qa, qb = r['quitar_x'][0] * 20.0, r['quitar_x'][1] * 20.0
                for gi in quitar:
                    for c in swfshape.contours(G[gi]):
                        if (gi, c['fill']) not in cset: continue
                        b = swfshape.cbbox(c['path'])
                        if qa <= (b[0] + b[2]) / 2.0 <= qb: continue
                        e0 = c['path'][0]
                        tc.append({'f0': 0, 'f1': 1, 'start': (e0[0], e0[1]),
                                   'segs': [('L', e[2], e[3]) if e[4] is None else ('Q', e[4], e[5], e[2], e[3]) for e in c['path']]})
            if 'parche' in r:                                     # tapa las letras pintadas del mapa de bits con el color del fondo
                x0, y0, x1, y1 = (v * 20.0 for v in r['parche']['caja'])
                pf = _vgrad(r['parche']['grad'], (x0 + x1) / 2) if 'grad' in r['parche'] else {'type': 0, 'color': tuple(r['parche']['color']) + (255,)}
                keep.append({'fills': [pf], 'lines': [],
                             'paths': [{'f0': 0, 'f1': 1, 'ls': 0, 'start': (x0, y0), 'segs': [('L', x1, y0), ('L', x1, y1), ('L', x0, y1), ('L', x0, y0)]}]})
            if keep: parts.append(keep)
            for c in capas:
                fill = dict(c['fill'])
                if fill['type'] == 0 and len(fill['color']) == 3: fill['color'] = tuple(fill['color']) + (255,)
                if 'banda' in c:
                    col = fill.get('color') or fill['grad']['recs'][0][1]; tr = (col[0], col[1], col[2], 0)
                    ya = min(R[1], _bbox(tc)[1]) - c['e'] - 40; yb = max(R[3], _bbox(tc)[3]) + c['e'] + 40
                    def rat(y):
                        y = cy0 + (y - cy0) * k
                        return max(1, min(254, int(round((y - ya) / (yb - ya) * 255))))
                    recs = []
                    if c['banda'][0] is not None: recs += [(rat(c['banda'][0]) - 1, tr), (rat(c['banda'][0]), col)]
                    else: recs += [(0, col)]
                    if c['banda'][1] is not None: recs += [(rat(c['banda'][1]), col), (rat(c['banda'][1]) + 1, tr)]
                    else: recs += [(255, col)]
                    b16 = int(round((yb - ya) / 32768.0 * 65536))
                    fill = {'type': 0x10, 'matrix': {'s': (0, 0), 'r': (b16, -b16), 't': (int(cx0), int((ya + yb) / 2))},
                            'grad': {'spread': 0, 'interp': 0, 'recs': recs}}
                lines = []
                if c['e'] > 0:
                    l = {'w': int(round(2 * c['e'] * (k if k < 1 else 1))), 'join': 2 if r.get('union') == 'inglete' else 0, 'miter': 0x0300}
                    if fill['type'] == 0: l['color'] = fill['color']
                    else: l['fill'] = fill
                    lines = [l]
                paths = [{'f0': 1 if kk['f0'] else 0, 'f1': 1 if kk['f1'] else 0, 'ls': 1 if lines else 0,
                          'start': (kk['start'][0] + c['dx'], kk['start'][1] + c['dy']),
                          'segs': [(sg[0],) + tuple(v + (c['dx'] if n % 2 == 0 else c['dy']) for n, v in enumerate(sg[1:])) for sg in kk['segs']]} for kk in tc]
                for pth in paths:
                    if not (pth['f0'] or pth['f1']): pth['f1'] = 1
                if parts and not lines and not any(g['lines'] for g in parts[-1]) and parts[-1] is not keep: parts[-1].append({'fills': [fill], 'lines': lines, 'paths': paths})
                else: parts.append([{'fills': [fill], 'lines': lines, 'paths': paths}])
            for groups in parts:
                nid = newid(); tg, org = write_shape4(swfmod, swftool, nid, groups); extra.append((lang, nid, tg, org))
            fb = _bbox(tc)
            informe.append('%d %s «%s»: alto %.1f px (orig %.1f), ancho %.1f de %.1f px, capas %d, x %.1f..%.1f' % (
                sid, lang, txt, hcap * s2 / 20, hcap * s / 20, (fb[2] - fb[0]) / 20, (hueco[1] - hueco[0]) / 20, len(capas), fb[0] / 20, fb[2] / 20))
        new = swftool.mk_tag(t, struct.pack('<H', orig) + tags[q + 2:e])
        sprite = place(1, orig, 'jm_en'); depth = 2
        for i, (lang, cid, tagb, org) in enumerate(extra):
            new += tagb; sprite += place(depth, cid, 'jm_%s_%d' % (lang, i)); depth += 1
        sprite += struct.pack('<H', 1 << 6) + struct.pack('<H', 0)                      # ShowFrame + End
        new += swftool.mk_tag(39, struct.pack('<HH', sid, 1) + sprite)
        rep[p] = (e, new); hechos += 1; conv.add(sid)
        r['_ids'] = {'en': [[orig, sh['bounds'][0], sh['bounds'][2]]]}
        for lang, cid, tagb, org in extra: r['_ids'].setdefault(lang, []).append([cid, org[0], org[1]])
    out = bytearray(); pos = 0
    for p in sorted(rep):
        e, new = rep[p]; out += tags[pos:p] + new; pos = e
    out += tags[pos:]
    stats = [0, 0]
    out = _fix_buttons(swftool, swfmod, bytes(out), {r['id']: r['_ids']['en'][0][0] for r in lista if '_ids' in r}, stats)
    fixed = swfmod.fix_replaces(bytes(out), conv, stats)
    swftool.save(swf_out, ver, head, fixed)
    print('   rótulos dibujados traducidos: %d (sustituciones en el mismo nivel arregladas: %d, PlaceObject3 sin arreglar: %d, botones con zona activa repuesta: %d)' % (hechos, stats[0], stats[1], stats[2]))
    if verbose:
        for l in informe: print('     ', l)
    return {r['id']: r['_ids'] for r in lista if '_ids' in r}

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(os.path.dirname(here))
    ids = rotular(sys.argv[1], sys.argv[2], json.load(open(os.path.join(here, 'rotulos.json'), encoding='utf-8')), root)
    json.dump(ids, open(sys.argv[2] + '.ids.json', 'w'))
