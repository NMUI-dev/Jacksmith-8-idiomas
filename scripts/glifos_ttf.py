# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Añade a las fuentes incrustadas del juego (DefineFont3) los glifos que les faltan para otros
idiomas (italiano, portugués, francés, alemán, ruso, japonés, chino), sacados de archivos TTF:

  1) la MISMA familia cuando la tenemos (las «Luna Sans» del juego son Alegreya Sans renombrada: mismos contornos,
     comprobado; Protest Strike, Archivo Black, Lilita One y Liberation Sans de Google Fonts / liberationfonts);
  2) si la familia no trae el carácter (cirílico en Protest Strike, Archivo Black, Lilita One; todo en CelticHoof):
     Noto Sans con el grosor más parecido;
  3) chino y japonés: Noto Sans SC / TC / JP con el grosor más parecido (cada carácter de la variante del idioma que
     lo usa: primero japonés, luego chino tradicional, luego simplificado).
Escala: la altura de la «H» del TTF = la de la fuente del juego. Convenio de los glifos del juego (medido): todos los
contornos con relleno f0 = 1 y el contorno exterior con área positiva (eje y hacia abajo).
Las fuentes variables se recortan a los caracteres pedidos y se fijan al grosor (caché en work/ttf_cache).

  add_glyphs_ttf(swf, chars, origen_cjk={car: 'ja'|'zh_hant'|'zh_hans'}, report=[])
"""
import os, sys, struct, hashlib
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI); sys.path.insert(0, os.path.join(RAIZ, 'tools', 'pydeps'))
import swftool, swfmod
from swfmod import EM, encode_shape, bbox, write_rect, reverse
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

DIR = os.path.join(RAIZ, 'tools', 'dl', 'fuentes')
CACHE = os.path.join(RAIZ, 'work', 'ttf_cache')
FAMILIA = {   # fuente del juego -> (TTF de su familia o None, grosor para Noto)
    'Alegreya Sans SC ExtraBold': ('AlegreyaSansSC-ExtraBold.ttf', 800),
    'Alegreya Sans SC Bold': ('AlegreyaSansSC-Bold.ttf', 700),
    'Alegreya Sans ExtraBold': ('AlegreyaSans-ExtraBold.ttf', 800),
    'Alegreya Sans ExtraBold_v': ('AlegreyaSans-ExtraBold.ttf', 800),
    'Alegreya Sans Bold': ('AlegreyaSans-Bold.ttf', 700),
    'Alegreya Sans Black': ('AlegreyaSans-Black.ttf', 900),
    'Luna Sans ExtraBold': ('AlegreyaSans-ExtraBold.ttf', 800),
    'Luna Sans Bold': ('AlegreyaSans-Bold.ttf', 700),
    'Luna Sans Black': ('AlegreyaSans-Black.ttf', 900),
    'Luna Sans Regular': ('AlegreyaSans-Regular.ttf', 400),
    'Protest Strike Regular': ('ProtestStrike-Regular.ttf', 800),
    'Archivo Black Regular': ('ArchivoBlack-Regular.ttf', 900),
    'Liberation Sans Bold': ('liberation-fonts-ttf-2.1.5/LiberationSans-Bold.ttf', 700),
    'Lilita One': ('LilitaOne-Regular.ttf', 700),
    'CelticHoof Regular': (None, 700),
}
NOTO = 'NotoSans[wdth,wght].ttf'
NOTO_CJK = {'ja': 'NotoSansJP[wght].ttf', 'zh_hant': 'NotoSansTC[wght].ttf', 'zh_hans': 'NotoSansSC[wght].ttf'}

def es_cjk(c):
    o = ord(c)
    return 0x2E80 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFFEF or 0x3000 <= o <= 0x30FF

_ttf = {}
PRIORIDAD = set()     # (pruebas con JM_CJK_MAX: letras que no pueden faltar, las de los rótulos)
def ttf(nombre, chars, peso=None):
    """TTFont recortado a `chars` (y fijado a `peso` si es variable), con caché en disco."""
    chars = ''.join(sorted(set(chars)))
    clave = hashlib.md5((nombre + str(peso) + chars).encode('utf-8')).hexdigest()[:16]
    if clave in _ttf: return _ttf[clave]
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, clave + '.ttf')
    if not os.path.exists(ruta):
        from fontTools import subset
        f = TTFont(os.path.join(DIR, nombre))
        cm = f.getBestCmap()
        uni = [ord(c) for c in chars if ord(c) in cm] + [ord('H')]
        op = subset.Options(); op.layout_features = []; op.notdef_outline = False; op.name_IDs = ['*']
        s = subset.Subsetter(op); s.populate(unicodes=uni); s.subset(f)
        if 'fvar' in f:
            from fontTools.varLib import instancer
            ax = {a.axisTag: a.defaultValue for a in f['fvar'].axes}
            ax['wght'] = max(min(peso or 400, max(a.maxValue for a in f['fvar'].axes if a.axisTag == 'wght')), 100)
            f = instancer.instantiateVariableFont(f, ax)
        # (las fuentes variables traen contornos SOLAPADOS; Flash rellena los glifos alternando y los solapes salían
        # como cuadros vacíos: visto en Ж, 鍛, 铁) se fusionan con skia-pathops
        from fontTools.ttLib.removeOverlaps import removeOverlaps
        removeOverlaps(f)
        f.save(ruta)
    t = TTFont(ruta); _ttf[clave] = t
    return t

class _Pen(BasePen):
    """Contornos TTF -> contornos de swfmod (eje y hacia abajo, escala k, desplazamiento dx)."""
    def __init__(s, gs, k):
        BasePen.__init__(s, gs); s.k = k; s.cons = []; s.cur = None
    def _p(s, p): return (p[0] * s.k, -p[1] * s.k)
    def _moveTo(s, p): s.cur = {'f0': 1, 'f1': 0, 'start': s._p(p), 'segs': []}; s.cons.append(s.cur)
    def _lineTo(s, p): s.cur['segs'].append(('L',) + s._p(p))
    def _qCurveToOne(s, c, p): s.cur['segs'].append(('Q',) + s._p(c) + s._p(p))
    def _curveToOne(s, c1, c2, p):       # (no pasa con glyf) cúbica -> una cuadrática aproximada
        a = s._getCurrentPoint()
        s._qCurveToOne(((3 * c1[0] - a[0] + 3 * c2[0] - p[0]) / 4.0, (3 * c1[1] - a[1] + 3 * c2[1] - p[1]) / 4.0), p)
    def _closePath(s):
        if s.cur and s.cur['segs']:
            last = s.cur['segs'][-1]; st = s.cur['start']
            if (last[-2], last[-1]) != st: s.cur['segs'].append(('L',) + st)
        s.cur = None
    _endPath = _closePath

def _area(c):
    P = swfmod.pts(c); n = len(P)
    return sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n)) / 2.0

def glifo(t, ch, k):
    """-> (contornos, avance) del carácter `ch` del TTFont `t` a escala k (o None si no lo tiene)."""
    cm = t.getBestCmap(); g = cm.get(ord(ch))
    if g is None: return None
    gs = t.getGlyphSet(); pen = _Pen(gs, k); gs[g].draw(pen)
    cons = [c for c in pen.cons if c['segs']]
    if cons:
        mayor = max(cons, key=lambda c: abs(_area(c)))
        if _area(mayor) < 0: cons = [reverse(c) for c in cons]      # exterior con área positiva, como el juego
        for c in cons: c['f0'], c['f1'] = 1, 0
    return cons, t['hmtx'][g][0] * k

def alto_H_ttf(t):
    gs = t.getGlyphSet(); g = t.getBestCmap()[ord('H')]
    from fontTools.pens.boundsPen import BoundsPen
    bp = BoundsPen(gs); gs[g].draw(bp); return bp.bounds[3]

def add_glyphs_ttf(swf, chars, origen_cjk=None, report=None):
    origen_cjk = origen_cjk or {}
    ver, head, tags = swftool.load(swf)
    out = bytearray(); added = {}; fonts = {}
    for t, p, q, e in swftool.iter_tags(tags):
        d = tags[q:e]
        if t == 75:
            f = swfmod.Font(d); nombre = f.name.rstrip(b'\0').decode('latin-1')
            fam, peso = FAMILIA.get(nombre, (None, 700))
            have = set(map(chr, f.codes))
            falta = [c for c in sorted(set(chars)) if c not in have and c.strip() and ord(c) >= 32]
            if os.environ.get('JM_CJK_MAX'):            # (solo pruebas: limitar los caracteres chinos/japoneses)
                cj = [c for c in falta if es_cjk(c) and c in PRIORIDAD] + [c for c in falta if es_cjk(c) and c not in PRIORIDAD]
                cj = cj[:int(os.environ['JM_CJK_MAX'])]
                falta = [c for c in falta if not es_cjk(c)] + cj
            if not falta or 'H' not in have: out += tags[p:e]; continue
            hH = -bbox(f.glyph('H'))[1]                 # altura de la H en la fuente del juego
            nuevos = {}
            def de(fuente_ttf, cs, peso_):
                if not cs: return
                tt = ttf(fuente_ttf, cs, peso_); k = hH / alto_H_ttf(tt)
                for c in cs:
                    if c in nuevos: continue
                    r = glifo(tt, c, k)
                    if r: nuevos[c] = r
            lat = [c for c in falta if not es_cjk(c)]
            if fam: de(fam, lat, peso)
            de(NOTO, [c for c in lat if c not in nuevos], peso)
            for lang in ('ja', 'zh_hant', 'zh_hans'):
                de(NOTO_CJK[lang], [c for c in falta if es_cjk(c) and c not in nuevos and origen_cjk.get(c, 'zh_hans') == lang], peso)
            ins = []
            ref = f.idx('H')
            for ch in sorted(nuevos, key=ord):
                cons, adv = nuevos[ch]
                pos = 0
                while pos < len(f.codes) and f.codes[pos] < ord(ch): pos += 1
                f.codes.insert(pos, ord(ch)); f.shapes.insert(pos, encode_shape(cons) if cons else encode_shape([]))
                if f.layout:
                    x0, y0, x1, y1 = bbox(cons) if cons else (0, 0, 0, 0)
                    f.adv.insert(pos, int(round(adv))); f.bounds.insert(pos, write_rect(int(x0), int(x1), int(y0), int(y1)))
                ins.append((pos, ch))
            added[f.fid] = ins; fonts[f.fid] = f
            out += swftool.mk_tag(75, f.pack())
            if report is not None: report.append((nombre, len(ins), ''.join(c for c in falta if c not in nuevos)))
        elif t == 73 and struct.unpack_from('<H', d, 0)[0] in added:
            # zonas de alineación: una por glifo, en el orden de los glifos; a los nuevos, la de la «H»
            fid = struct.unpack_from('<H', d, 0)[0]; f = fonts[fid]
            recs = []; o = 3
            while o < len(d):
                nz = d[o]; ln = 1 + nz * 4 + 1; recs.append(d[o:o + ln]); o += ln
            nuevos_pos = {pos for pos, _ in added[fid]}
            viejos = iter(recs); h = recs[0]
            final = []
            for i in range(len(f.codes)):
                final.append(None if i in nuevos_pos else next(viejos, recs[0]))
            hpos = f.idx('H'); h = final[hpos] or recs[0]
            out += swftool.mk_tag(73, d[:3] + b''.join(r if r is not None else h for r in final))
        else:
            out += tags[p:e]
    swftool.save(swf, ver, head, bytes(out))
    return added
