# -*- coding: utf-8 -*-
"""Retoques del SWF que necesita la traducción:
  1) add_glyphs(): añade a las fuentes incrustadas (DefineFont3) los glifos del español que les faltan
     (á é í ó ú ñ ü, sus mayúsculas, ¿ ¡), compuestos a partir de glifos de la propia fuente.
  2) static_to_dynamic(): convierte los textos estáticos (DefineText) en campos de texto (DefineEditText)
     para que el núcleo pueda traducirlos al vuelo y para que no dependan de índices de glifo.
"""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swftool

EM = 20480.0

# ------------------------------------------------------------------ bits
class BR:
    def __init__(s, d, p=0): s.d = d; s.p = p * 8
    def u(s, n):
        v = 0
        for _ in range(n):
            v = (v << 1) | ((s.d[s.p >> 3] >> (7 - (s.p & 7))) & 1); s.p += 1
        return v
    def s_(s, n):
        if n == 0: return 0
        v = s.u(n)
        return v - (1 << n) if v >> (n - 1) else v
    def align(s): s.p = (s.p + 7) & ~7
    @property
    def byte(s): return (s.p + 7) >> 3

class BW:
    def __init__(s): s.bits = []
    def u(s, v, n):
        for i in range(n - 1, -1, -1): s.bits.append((v >> i) & 1)
    def s_(s, v, n): s.u(v & ((1 << n) - 1), n)
    def align(s):
        while len(s.bits) % 8: s.bits.append(0)
    def bytes(s):
        s.align(); out = bytearray()
        for i in range(0, len(s.bits), 8):
            b = 0
            for k in s.bits[i:i + 8]: b = (b << 1) | k
            out.append(b)
        return bytes(out)

def sbits(*vals):
    n = 1
    for v in vals:
        v = int(v)
        n = max(n, (v.bit_length() if v >= 0 else (~v).bit_length()) + 1)
    return n

def read_rect(d, p):
    r = BR(d, p); n = r.u(5); v = [r.s_(n) for _ in range(4)]   # xmin xmax ymin ymax
    return v, r.byte
def write_rect(xmin, xmax, ymin, ymax):
    w = BW(); n = sbits(xmin, xmax, ymin, ymax); w.u(n, 5)
    for v in (xmin, xmax, ymin, ymax): w.s_(int(v), n)
    return w.bytes()

def read_matrix(d, p):
    r = BR(d, p); sx = sy = 1.0; r0 = r1 = 0.0
    if r.u(1):
        n = r.u(5); sx = r.s_(n) / 65536.0; sy = r.s_(n) / 65536.0
    if r.u(1):
        n = r.u(5); r0 = r.s_(n) / 65536.0; r1 = r.s_(n) / 65536.0
    n = r.u(5); tx = r.s_(n); ty = r.s_(n)
    return (sx, sy, r0, r1, tx, ty), r.byte

# ------------------------------------------------------------------ formas de glifo
def decode_shape(d):
    """-> lista de contornos {'f0','f1','pts':[(x,y)], 'segs':[('L',x,y)|('Q',cx,cy,x,y)]} en coordenadas absolutas."""
    r = BR(d); fb = r.u(4); lb = r.u(4)
    x = y = 0; f0 = f1 = 0; cons = []; cur = None
    while True:
        if r.u(1) == 0:
            fl = r.u(5)
            if fl == 0: break
            if fl & 1:
                n = r.u(5); x = r.s_(n); y = r.s_(n)
            if fl & 2: f0 = r.u(fb)
            if fl & 4: f1 = r.u(fb)
            if fl & 8: r.u(lb)
            if fl & 16: raise ValueError('estilos nuevos en un glifo')
            cur = {'f0': f0, 'f1': f1, 'start': (x, y), 'segs': []}; cons.append(cur)
        else:
            if cur is None:
                cur = {'f0': f0, 'f1': f1, 'start': (x, y), 'segs': []}; cons.append(cur)
            if r.u(1):
                n = r.u(4) + 2
                if r.u(1): dx = r.s_(n); dy = r.s_(n)
                elif r.u(1): dx = 0; dy = r.s_(n)
                else: dx = r.s_(n); dy = 0
                x += dx; y += dy; cur['segs'].append(('L', x, y))
            else:
                n = r.u(4) + 2
                cx = x + r.s_(n); cy = y + r.s_(n); x = cx + r.s_(n); y = cy + r.s_(n)
                cur['segs'].append(('Q', cx, cy, x, y))
    return [c for c in cons if c['segs']]

def encode_shape(cons):
    w = BW(); w.u(1, 4); w.u(0, 4)
    for c in cons:
        x, y = (int(round(v)) for v in c['start'])
        fl = 1 | (2 if c['f0'] else 0) | (4 if c['f1'] else 0)
        if not (fl & 6): fl |= 4; c = dict(c, f1=1)
        w.u(0, 1); w.u(fl, 5)
        n = sbits(x, y); w.u(n, 5); w.s_(x, n); w.s_(y, n)
        if fl & 2: w.u(1, 1)
        if fl & 4: w.u(1, 1)
        for s in c['segs']:
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
                a, b, c2, e = cx - x, cy - y, nx - cx, ny - cy
                n = max(2, sbits(a, b, c2, e)); w.u(1, 1); w.u(0, 1); w.u(n - 2, 4)
                w.s_(a, n); w.s_(b, n); w.s_(c2, n); w.s_(e, n)
                x, y = nx, ny
    w.u(0, 6)
    return w.bytes()

def pts(c):
    out = [c['start']]
    for s in c['segs']:
        if s[0] == 'L': out.append((s[1], s[2]))
        else: out.append((s[1], s[2])); out.append((s[3], s[4]))
    return out
def bbox(cons):
    P = [p for c in cons for p in pts(c)]
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    return min(xs), min(ys), max(xs), max(ys)
def xform(cons, f):
    out = []
    for c in cons:
        segs = [('L',) + f(s[1], s[2]) if s[0] == 'L' else ('Q',) + f(s[1], s[2]) + f(s[3], s[4]) for s in c['segs']]
        out.append({'f0': c['f0'], 'f1': c['f1'], 'start': f(*c['start']), 'segs': segs})
    return out
def reverse(c):
    P = [c['start']] + [(s[-2], s[-1]) for s in c['segs']]
    segs = []
    for i in range(len(c['segs']) - 1, -1, -1):
        s = c['segs'][i]; to = P[i]
        segs.append(('L', to[0], to[1]) if s[0] == 'L' else ('Q', s[1], s[2], to[0], to[1]))
    return {'f0': c['f0'], 'f1': c['f1'], 'start': P[-1], 'segs': segs}

# ------------------------------------------------------------------ fuentes
class Font:
    def __init__(s, d):
        s.fid, s.flags, s.lang, nl = struct.unpack_from('<HBBB', d, 0)
        s.name = d[5:5 + nl]; o = 5 + nl
        n = struct.unpack_from('<H', d, o)[0]; o += 2; base = o
        wide = s.flags & 8
        if n == 0: raise ValueError('fuente vacía')
        fmt, sz = ('<I', 4) if wide else ('<H', 2)
        offs = [struct.unpack_from(fmt, d, base + sz * i)[0] for i in range(n + 1)]
        s.shapes = [d[base + offs[i]:base + offs[i + 1]] for i in range(n)]
        o = base + offs[n]
        s.codes = list(struct.unpack_from('<%dH' % n, d, o)); o += 2 * n
        s.layout = bool(s.flags & 0x80)
        if s.layout:
            s.ascent, s.descent, s.leading = struct.unpack_from('<HHh', d, o); o += 6
            s.adv = list(struct.unpack_from('<%dh' % n, d, o)); o += 2 * n
            s.bounds = []
            for _ in range(n):
                r, o2 = read_rect(d, o); s.bounds.append(d[o:o2]); o = o2
            s.kern = d[o:]
        else:
            s.rest = d[o:]
    def idx(s, ch):
        try: return s.codes.index(ord(ch))
        except ValueError: return None
    def glyph(s, ch): return decode_shape(s.shapes[s.idx(ch)])
    def pack(s):
        n = len(s.codes)
        body = b''.join(s.shapes)
        wide = (n + 1) * 2 + len(body) > 65000
        s.flags = (s.flags | 8) if wide else (s.flags & ~8)
        fmt, sz = ('<I', 4) if wide else ('<H', 2)
        off = (n + 1) * sz; tab = b''
        for sh in s.shapes: tab += struct.pack(fmt, off); off += len(sh)
        tab += struct.pack(fmt, off)
        out = struct.pack('<HBBB', s.fid, s.flags, s.lang, len(s.name)) + s.name + struct.pack('<H', n) + tab + body
        out += struct.pack('<%dH' % n, *s.codes)
        if s.layout:
            out += struct.pack('<HHh', s.ascent, s.descent, s.leading) + struct.pack('<%dh' % n, *s.adv) + b''.join(s.bounds) + s.kern
        else: out += s.rest
        return out

ACCENTS = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
TILDES = {'ñ': 'n', 'Ñ': 'N'}
DIER = {'ü': 'u', 'Ü': 'U'}
FLIP = {'¿': '?', '¡': '!'}

def compose(font):
    """-> {car: (contornos, avance, base)} para los caracteres que le faltan a la fuente."""
    have = set(map(chr, font.codes)); new = {}
    def top(ch):
        return -bbox(font.glyph(ch))[1]
    xh = top('x'); cap = top('H')
    gap_def = 0.055 * EM
    def place(mark, base_cons, raise_extra=0):
        bx0, by0, bx1, by1 = bbox(base_cons); mx0, my0, mx1, my1 = bbox(mark)
        gap = (-my1) - xh                       # separación de la marca respecto a la altura de la x
        if gap < 0.03 * EM or gap > 0.2 * EM: gap = gap_def
        dy = (-(-by0) - gap) - my1              # parte baja de la marca = techo de la base + separación
        dx = (bx0 + bx1) / 2.0 - (mx0 + mx1) / 2.0
        return xform(mark, lambda x, y: (x + dx, y + dy))
    def base_of(b, strip_dot):
        cons = font.glyph(b)
        if strip_dot and len(cons) >= 2:
            cons = sorted(cons, key=lambda c: bbox([c])[1])[1:]      # quita el punto de la i
        return cons
    if '`' in have:
        g = font.glyph('`'); x0, y0, x1, y1 = bbox(g); cx = (x0 + x1) / 2.0
        acute = [reverse(c) for c in xform(g, lambda x, y: (2 * cx - x, y))]
        for ch, b in ACCENTS.items():
            if ch in have or b not in have: continue
            bc = base_of(b, b == 'i')
            new[ch] = (bc + place(acute, bc), b)
    til = '˜' if '˜' in have else ('~' if '~' in have else None)
    if til:
        g = font.glyph(til)
        if til == '~':                               # la virgulilla ASCII va a media altura: se sube
            x0, y0, x1, y1 = bbox(g); g = xform(g, lambda x, y: (x, y - ((-y1) - xh) + (-(-y1) - xh)))
        for ch, b in TILDES.items():
            if ch in have or b not in have: continue
            bc = font.glyph(b); new[ch] = (bc + place(g, bc), b)
    if '.' in have:
        g = font.glyph('.'); x0, y0, x1, y1 = bbox(g); k = 0.8; w = (x1 - x0) * k
        one = xform(g, lambda x, y: ((x - x0) * k, (y - y1) * k))
        two = one + xform(one, lambda x, y: (x + w * 1.9, y))
        two = xform(two, lambda x, y: (x, y - xh - gap_def))    # como si estuviera sobre la x (place la recoloca)
        for ch, b in DIER.items():
            if ch in have or b not in have: continue
            bc = font.glyph(b); new[ch] = (bc + place(two, bc), b)
    for ch, b in FLIP.items():
        if ch in have or b not in have: continue
        g = font.glyph(b); x0, y0, x1, y1 = bbox(g); cx = (x0 + x1) / 2.0; cy = -xh / 2.0 + (-(-y0) + cap) * 0
        # giro de 180º: lo que estaba en la línea base queda a la altura de la x, y cuelga por debajo
        new[ch] = (xform(g, lambda x, y: (2 * cx - x, -xh - y)), b)
    return new

def add_glyphs(swf, report=None):
    ver, head, tags = swftool.load(swf)
    out = bytearray(); added = {}; fonts = {}
    for t, p, q, e in swftool.iter_tags(tags):
        d = tags[q:e]
        if t == 75:
            try:
                f = Font(d); new = compose(f)
            except Exception as ex:
                print('   fuente', d[5:5 + d[4]], 'sin tocar:', ex); out += tags[p:e]; continue
            ins = []
            for ch in sorted(new, key=ord):
                cons, b = new[ch]; bi = f.idx(b)
                pos = 0
                while pos < len(f.codes) and f.codes[pos] < ord(ch): pos += 1
                f.codes.insert(pos, ord(ch)); f.shapes.insert(pos, encode_shape(cons))
                bi = f.idx(b)
                if f.layout:
                    x0, y0, x1, y1 = bbox(cons)
                    f.adv.insert(pos, f.adv[bi if bi < pos else bi - 0] if False else 0)
                    f.adv[pos] = f.adv[f.idx(b)]
                    f.bounds.insert(pos, write_rect(x0, x1, y0, y1))
                ins.append((pos, b, ch))
            added[f.fid] = ins; fonts[f.fid] = f
            out += swftool.mk_tag(75, f.pack())
            if report is not None: report.append((f.name.rstrip(b'\0').decode(), ''.join(c for _, _, c in ins)))
        elif t == 73 and struct.unpack_from('<H', d, 0)[0] in added:
            fid = struct.unpack_from('<H', d, 0)[0]; f = fonts[fid]
            recs = []; o = 3
            while o < len(d):
                nz = d[o]; ln = 1 + nz * 4 + 1; recs.append(d[o:o + ln]); o += ln
            for pos, b, ch in added[fid]:
                recs.insert(pos, recs[f.idx(b)] if f.idx(b) < len(recs) else recs[0])
            # los índices de la base pueden haberse movido al insertar: se recalcula con la tabla final
            fixed = list(recs)
            for pos, b, ch in added[fid]: fixed[pos] = recs[f.idx(b)]
            out += swftool.mk_tag(73, d[:3] + b''.join(fixed))
        else:
            out += tags[p:e]
    swftool.save(swf, ver, head, bytes(out))
    return added

# ------------------------------------------------------------------ textos estáticos -> campos
MARK_MAXLEN = 7777      # el núcleo reconoce por maxChars los campos que eran texto estático

def static_to_dynamic(swf, orig_swf, report=None):
    """Convierte cada DefineText de `swf`; los índices de glifo se leen con las fuentes ORIGINALES."""
    _, _, otags = swftool.load(orig_swf)
    fonts = {}
    for t, p, q, e in swftool.iter_tags(otags):
        if t == 75:
            try: f = Font(otags[q:e]); fonts[f.fid] = f
            except Exception: pass
    ver, head, tags = swftool.load(swf)
    out = bytearray(); n = 0; raros = []
    for t, p, q, e in swftool.iter_tags(tags):
        if t not in (11, 33): out += tags[p:e]; continue
        d = tags[q:e]; cid = struct.unpack_from('<H', d, 0)[0]
        (bx0, bx1, by0, by1), o = read_rect(d, 2)
        (sx, sy, r0, r1, tx, ty), o = read_matrix(d, o)
        gb, ab = d[o], d[o + 1]; o += 2
        fid = None; color = (0, 0, 0, 255); height = 240; x = y = 0; recs = []
        while d[o] != 0:
            fl = d[o]; o += 1
            if fl & 8: fid = struct.unpack_from('<H', d, o)[0]; o += 2
            if fl & 4:
                if t == 33: color = tuple(d[o:o + 4]); o += 4
                else: color = tuple(d[o:o + 3]) + (255,); o += 3
            if fl & 1: x = struct.unpack_from('<h', d, o)[0]; o += 2
            if fl & 2: y = struct.unpack_from('<h', d, o)[0]; o += 2
            if fl & 8: height = struct.unpack_from('<H', d, o)[0]; o += 2
            cnt = d[o]; o += 1
            r = BR(d, o); s = ''; w = 0
            f = fonts.get(fid)
            for _ in range(cnt):
                gi = r.u(gb); a = r.s_(ab); w += a
                s += chr(f.codes[gi]) if f and gi < len(f.codes) else '?'
            o = r.byte
            recs.append({'x': x, 'y': y, 'w': w, 's': s, 'fid': fid, 'h': height, 'col': color})
            x += w
        if not recs or fid not in fonts: out += tags[p:e]; raros.append((cid, 'sin registros/fuente')); continue
        if abs(r0) > 1e-6 or abs(r1) > 1e-6: raros.append((cid, 'matriz con giro'))
        # líneas (registros con la misma Y)
        lines = []
        for rc in recs:
            if lines and abs(lines[-1]['y'] - rc['y']) < 20:
                L = lines[-1]; gapw = rc['x'] - (L['x'] + L['w'])
                L['s'] += rc['s']; L['w'] = rc['x'] + rc['w'] - L['x']
            else: lines.append(dict(rc))
        r0_ = recs[0]; f = fonts[r0_['fid']]; H = r0_['h']
        if len({(rc['fid'], rc['h']) for rc in recs}) > 1: raros.append((cid, 'varias fuentes/tamaños'))
        asc = f.ascent * H / EM if f.layout else H * 0.9
        desc = f.descent * H / EM if f.layout else H * 0.25
        lead_font = f.leading * H / EM if f.layout else 0
        starts = [L['x'] for L in lines]; ends = [L['x'] + L['w'] for L in lines]; mids = [(a + b) / 2.0 for a, b in zip(starts, ends)]
        W = max(L['w'] for L in lines)
        def same(v): return max(v) - min(v) < 60
        if len(lines) == 1: align = 2
        elif same(mids): align = 2
        elif same(starts): align = 0
        elif same(ends): align = 1
        else: align = 2
        pad = max(30, W * 0.03)
        mar = int(max(60, W * 0.04))      # margen interior: las letras que sobresalen no se cortan
        pad += mar
        if align == 0: X0 = min(starts) - 40; X1 = X0 + W + 80 + 2 * pad
        elif align == 1: X1 = max(ends) + 40; X0 = X1 - W - 80 - 2 * pad
        else:
            m = sum(mids) / len(mids); X0 = m - W / 2.0 - 40 - pad; X1 = m + W / 2.0 + 40 + pad
        pitch = (lines[-1]['y'] - lines[0]['y']) / (len(lines) - 1) if len(lines) > 1 else asc + desc
        leading = int(round(pitch - (asc + desc))) if len(lines) > 1 else 0
        Y0 = lines[0]['y'] - asc - 40
        Y1 = lines[-1]['y'] + desc + 40 + (max(0, leading) if len(lines) > 1 else 0) + 20
        # matriz del texto: traslación y escala uniforme
        Hh = int(round(H * sy))
        X0, X1 = X0 * sx + tx, X1 * sx + tx; Y0, Y1 = Y0 * sy + ty, Y1 * sy + ty; leading = int(round(leading * sy))
        text = '\r'.join(L['s'].rstrip() for L in lines)
        multi = len(lines) > 1
        fl1 = 0x80 | (0x20 if multi else 0) | 0x08 | 0x04 | 0x02 | 0x01      # HasText, Multiline, ReadOnly, HasTextColor, HasMaxLength, HasFont
        fl2 = 0x20 | 0x10 | 0x04 | 0x01                                      # HasLayout, NoSelect, WasStatic, UseOutlines
        ed = struct.pack('<H', cid) + write_rect(int(X0), int(X1), int(Y0), int(Y1)) + bytes([fl1, fl2])
        ed += struct.pack('<HH', r0_['fid'], Hh) + bytes(r0_['col']) + struct.pack('<H', MARK_MAXLEN)
        ed += struct.pack('<BHHHh', align, int(mar * sx), int(mar * sx), 0, max(-32000, min(32000, leading)))
        ed += b'\0' + text.encode('utf-8') + b'\0'
        out += swftool.mk_tag(37, ed); n += 1
        _convertidos.add(cid)
        if report is not None: report.append((cid, text))
    conv = {r[0] for r in (report or [])} if report is not None else set()
    if not conv:
        conv = set()
        for t2, p2, q2, e2 in swftool.iter_tags(bytes(out)):
            if t2 == 37 and bytes(out)[e2 - 1:e2] == b'\0':
                pass
    stats = [0, 0]
    fixed = fix_replaces(bytes(out), _convertidos, stats)
    swftool.save(swf, ver, head, fixed)
    print('   sustituciones de texto en el mismo nivel rehechas:', stats[0], '| PlaceObject3 sin tocar:', stats[1])
    return n, raros

_convertidos = set()

def fix_replaces(stream, conv, stats):
    """El reproductor NO sustituye un campo de texto por otro en el mismo nivel (PlaceObject «mover + carácter»);
    con textos estáticos sí lo hacía. Donde el nuevo o el viejo es un texto convertido: quitar y colocar."""
    out = bytearray(); state = {}
    for t, p, q, e in swftool.iter_tags(stream):
        d = stream[q:e]
        if t == 39:
            out += swftool.mk_tag(39, d[:4] + fix_replaces(d[4:], conv, stats)); continue
        if t == 26:
            fl = d[0]; depth = struct.unpack_from('<H', d, 1)[0]; o = 3; cid = None; mb = None
            if fl & 2: cid = struct.unpack_from('<H', d, o)[0]; o += 2
            if fl & 4:
                _, o2 = read_matrix(d, o); mb = d[o:o2]
            prev = state.get(depth)
            if (fl & 1) and (fl & 2) and (cid in conv or (prev and prev[0] in conv)):
                nd = bytearray(d); nd[0] = fl & ~1
                if not (fl & 4) and prev and prev[1] is not None:
                    nd[0] |= 4; nd = nd[:5] + prev[1] + nd[5:]; mb = prev[1]
                out += swftool.mk_tag(28, struct.pack('<H', depth)) + swftool.mk_tag(26, bytes(nd))
                state[depth] = (cid, mb); stats[0] += 1; continue
            if fl & 2: state[depth] = (cid, mb if mb is not None else (prev[1] if (prev and (fl & 1)) else None))
            elif (fl & 4) and prev: state[depth] = (prev[0], mb)
        elif t == 70:
            fl = d[0]; depth = struct.unpack_from('<H', d, 2)[0]
            prev = state.get(depth)
            if (fl & 1) and (fl & 2) and prev and prev[0] in conv: stats[1] += 1
            if fl & 2 and not (d[1] & 0x18): state[depth] = (struct.unpack_from('<H', d, 4)[0], None)
        elif t == 28:
            state.pop(struct.unpack_from('<H', d, 0)[0], None)
        elif t == 5:
            state.pop(struct.unpack_from('<H', d, 2)[0], None)
        out += stream[p:e]
    return bytes(out)

# ------------------------------------------------------------------ vista previa de glifos (comprobación visual)
def preview(swf, png, sample='áéíóúñü ÁÉÍÓÚÑÜ ¿¡ aeiounAEIOUN?!'):
    from PIL import Image, ImageDraw
    _, _, tags = swftool.load(swf)
    fs = []
    for t, p, q, e in swftool.iter_tags(tags):
        if t == 75:
            try: fs.append(Font(tags[q:e]))
            except Exception: pass
    S = 0.0022; rowh = 62; SS = 3
    img = Image.new('L', (1500 * SS, rowh * len(fs) * SS), 255); dr = ImageDraw.Draw(img)
    for i, f in enumerate(fs):
        x = 10.0; base = (i * rowh + 46)
        for ch in sample:
            gi = f.idx(ch)
            if gi is None: x += 14; continue
            cons = decode_shape(f.shapes[gi]) if len(f.shapes[gi]) > 1 else []
            layer = Image.new('L', img.size, 0); ld = ImageDraw.Draw(layer)
            mask = Image.new('1', img.size, 0)
            from PIL import ImageChops
            acc = Image.new('1', img.size, 0)
            for c in cons:
                P = [c['start']]
                for s in c['segs']:
                    if s[0] == 'L': P.append((s[1], s[2]))
                    else:
                        x0, y0 = P[-1]
                        for k in range(1, 9):
                            tt = k / 8.0
                            P.append(((1 - tt) ** 2 * x0 + 2 * (1 - tt) * tt * s[1] + tt * tt * s[3], (1 - tt) ** 2 * y0 + 2 * (1 - tt) * tt * s[2] + tt * tt * s[4]))
                one = Image.new('1', img.size, 0)
                ImageDraw.Draw(one).polygon([((x + px * S) * SS, (base + py * S) * SS) for px, py in P], fill=1)
                acc = ImageChops.logical_xor(acc, one)
            img.paste(0, mask=acc)
            x += (f.adv[gi] if f.layout else 600 * 20) * S + 1
        dr.text((1150 * SS, (i * rowh + 20) * SS), f.name.rstrip(b'\0').decode(), fill=0, font_size=11 * SS)
    img = img.resize((1500, rowh * len(fs)), Image.LANCZOS); img.save(png)

if __name__ == '__main__':
    import shutil
    src, dst = sys.argv[1], sys.argv[2]
    shutil.copy(src, dst); rep = []
    add_glyphs(dst, rep)
    for r in rep: print(r)
    n, raros = static_to_dynamic(dst, src)
    print(n, 'textos estáticos convertidos; raros:', raros)
    preview(dst, dst + '.glifos.png')
