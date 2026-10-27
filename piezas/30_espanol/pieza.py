# -*- coding: utf-8 -*-
"""Pieza 30 — ESPAÑOL.

 - Genera Data/mods/30_espanol/lang/es.json a partir de fuente/es_textos.json (traducción base, clave = inglés),
   fuente/es_extra.json (añadidos y correcciones a mano; ganan a los de base) y fuente/es_patrones.json
   (frases que el juego compone con números o nombres).
 - Añade a las fuentes incrustadas los glifos á é í ó ú ñ ü ¿ ¡ (y mayúsculas) que les faltan.
El inglés original no se toca: con el idioma «English» el núcleo no traduce nada.
"""
import os, sys, json, shutil

# (19-10-2026) nombres de TODOS los idiomas del mod en español (los nuevos los trae la pieza 31)
IDIOMAS_ES = {'es': 'Español', 'en': 'Inglés', 'it': 'Italiano', 'pt': 'Portugués', 'fr': 'Francés', 'de': 'Alemán',
              'ru': 'Ruso', 'ja': 'Japonés', 'zh_hans': 'Chino simplificado', 'zh_hant': 'Chino tradicional'}

def repartir(es, lens):
    """Parte `es` en len(lens) renglones con largos proporcionales a `lens` (solo corta en espacios)."""
    palabras = es.replace('\n', ' ').split()
    n = len(lens)
    if n < 2 or not palabras: return es
    if es.count('\n') + 1 == n and lens[0] > 1: return es       # ya viene repartida a mano
    out = [[] for _ in range(n)]
    i0 = 0
    if lens[0] <= 1 and len(palabras[0]) <= 1:            # primer renglón de un solo signo (p. ej. «.»)
        out[0].append(palabras[0]); palabras = palabras[1:]; i0 = 1
    vivos = [i for i in range(i0, n)]
    total = sum(len(w) + 1 for w in palabras); suma = float(sum(max(1, lens[i]) for i in vivos)) or 1.0
    pos = 0; j = 0; acum = 0.0
    for idx, i in enumerate(vivos):
        acum += max(1, lens[i]) / suma
        tope = total * acum
        quedan = len(vivos) - idx - 1
        while j < len(palabras) - quedan and (idx == len(vivos) - 1 or pos + (len(palabras[j]) + 1) / 2.0 <= tope or not out[i]):
            out[i].append(palabras[j]); pos += len(palabras[j]) + 1; j += 1
    return '\n'.join(' '.join(l) for l in out)

def aplicar(ctx):
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, 'fuente')
    base = json.load(open(os.path.join(src, 'es_textos.json'), encoding='utf-8'))
    origen = json.load(open(os.path.join(src, 'en_origen.json'), encoding='utf-8'))
    extra = json.load(open(os.path.join(src, 'es_extra.json'), encoding='utf-8'))
    pats = json.load(open(os.path.join(src, 'es_patrones.json'), encoding='utf-8'))
    frag = set()
    for e in origen:
        x = e.get('en_exacto')
        if x and (x != x.strip() or x.startswith('<')): frag.add(e['en'])
    textos = {}
    for en, es in base.items():
        if en in frag or es == en or not es.strip(): continue
        textos[en] = es
    import re
    def norm(k): return re.sub(r'[\s ]+', '', k).replace('‘', "'").replace('’', "'")
    nx = {norm(k) for k in extra}
    textos = {k: v for k, v in textos.items() if norm(k) not in nx}     # lo de es_extra.json gana
    textos.update(extra)
    # Textos que en el juego eran estáticos de varios renglones (historia, avisos): el juego los destapa renglón a
    # renglón, así que la traducción conserva el MISMO número de renglones, repartida en proporción al original.
    sys.path.insert(0, os.path.join(ctx.root, 'scripts')); import swfmod
    orig_swf = os.path.join(ctx.root, 'original', 'Data', 'assets', 'Main.assets')
    tmp = os.path.join(ctx.root, 'work', '_estaticos.swf'); shutil.copy(orig_swf, tmp)
    rep = []; swfmod.static_to_dynamic(tmp, orig_swf, rep); os.remove(tmp)
    porclave = {norm(k): k for k in textos}
    nrep = 0
    for cid, text in rep:
        lineas = text.split('\r')
        if len(lineas) < 2: continue
        k = porclave.get(norm(text))
        if not k: continue
        textos[k] = repartir(textos[k], [len(l.strip()) for l in lineas]); nrep += 1
    print(f'   textos de varios renglones repartidos: {nrep}')
    out = os.path.join(ctx.root, 'work', 'datos_30_espanol')
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'lang'))
    json.dump({'nombre': 'Español', 'nombre_en': 'Spanish', 'codigo': 'es', 'idiomas': IDIOMAS_ES, 'textos': textos, 'patrones': pats},
              open(os.path.join(out, 'lang', 'es.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    shutil.copy(os.path.join(here, 'datos', 'mod.json'), os.path.join(out, 'mod.json'))
    ctx.extra_files['Data/mods/30_espanol'] = out
    print(f'   es.json: {len(textos)} textos, {len(pats)} patrones')
    ctx.log.append(('es_textos', len(textos)))

    def glifos(c):
        sys.path.insert(0, os.path.join(c.root, 'scripts')); import swfmod
        rep = []; swfmod.add_glyphs(c.swf, rep)
        print('   glifos añadidos a', sum(1 for r in rep if r[1]), 'fuentes')
    ctx.post_swf.append(glifos)
