# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Traducción de Jacksmith a más idiomas con TRES agentes gratuitos y locales (Ollama) y
revisión final de Claude (pedido del usuario: «tengamos 3 agentes gratuitos para mayor precisión y tú las revisas»).

  python scripts/traducir_idiomas.py traducir it pt ...           1) TranslateGemma 12B traduce   -> <c>_gemma.json
  python scripts/traducir_idiomas.py revisar qwen it pt ...       2) Qwen 27B revisa línea a línea -> <c>_rev_qwen.json
  python scripts/traducir_idiomas.py revisar gemma4 it pt ...     3) Gemma 4 12B revisa             -> <c>_rev_gemma4.json
  python scripts/traducir_idiomas.py combinar it pt ...           -> <c>_textos.json (lo que usa la pieza 31)
                                                                     + <c>_dudas.json (para la revisión de Claude)
Códigos: it pt fr de ru ja zh_hans zh_hant. Todo en piezas/31_idiomas/fuente/. Se puede cortar y retomar.
Cada texto va con su traducción española YA REVISADA como referencia de sentido y con los términos del glosario fijo
(scripts/glosario_idiomas.py) que aparecen en el lote. Los textos de varios renglones van como una frase (el reparto en
renglones lo hace la pieza 31).
Combinar: si ningún revisor objeta, se queda la traducción; si los dos proponen LO MISMO, se aplica; si discrepan, se
deja la de TranslateGemma y la línea va a <c>_dudas.json (Claude decide y lo apunta en <c>_extra.json, que gana).
"""
import json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glosario_idiomas

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTE = os.path.join(RAIZ, 'piezas', '30_espanol', 'fuente')
SALIDA = os.path.join(RAIZ, 'piezas', '31_idiomas', 'fuente')
LOTE = 12
NOMBRES = {'it': 'Italian', 'pt': 'Brazilian Portuguese', 'de': 'German', 'fr': 'French', 'ru': 'Russian',
           'ja': 'Japanese', 'zh_hans': 'Simplified Chinese', 'zh_hant': 'Traditional Chinese'}
MODELOS = {'gemma': 'translategemma:12b', 'qwen': 'qwen3.8:27b', 'gemma4': 'gemma4:12b'}
CONTEXTO = ('These are user-interface texts from the video game "Jacksmith: Weapons and Warriors": a donkey blacksmith '
            'forges weapons (swords, axes, maces, bows, shields, arrows, cannon balls) for soldiers who fight monsters. '
            'Keep it short like game UI text, friendly and informal (address the player informally). Keep numbers and % '
            'exactly. Proper names of the game (Jacksmith, Flipline, Dudley, Liliana) stay unchanged.')
ES = {}

def pedir(modelo, prompt):
    cuerpo = {'model': MODELOS[modelo], 'prompt': prompt, 'stream': False, 'options': {'temperature': 0, 'num_ctx': 8192}}
    if modelo in ('qwen', 'gemma4'): cuerpo['think'] = False     # (sin esto Gemma 4 solo «piensa» y responde vacío)
    req = urllib.request.Request('http://localhost:11434/api/generate', data=json.dumps(cuerpo).encode(),
                                 headers={'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=1800))['response']
    return re.sub(r'<think>.*?</think>', '', r, flags=re.S).strip()

def ruta(code, nombre): return os.path.join(SALIDA, f'{code}_{nombre}.json')
def cargar(code, nombre):
    r = ruta(code, nombre); return json.load(open(r, encoding='utf-8')) if os.path.exists(r) else {}
def guardar(code, nombre, d):
    os.makedirs(SALIDA, exist_ok=True)
    json.dump(d, open(ruta(code, nombre), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def textos_fuente():
    es = json.load(open(os.path.join(FUENTE, 'es_textos.json'), encoding='utf-8'))
    extra = json.load(open(os.path.join(FUENTE, 'es_extra.json'), encoding='utf-8'))
    ES.update(es); ES.update(extra)
    t = [k for k, v in es.items() if v != k and v.strip()]
    for k in extra:
        if k not in t: t.append(k)
    return t

def una(s): return s.replace('\n', ' ')
def glosario(code, grupo):
    g = glosario_idiomas.para(code, grupo)
    return ('\nALWAYS use these game terms (adapting plural/case):\n' + '\n'.join(g)) if g else ''

def numeradas(r, n):
    out = {}
    for l in r.split('\n'):
        m = re.match(r'\s*(\d+)\s*[.．、:)]\s*(.*)$', l)
        if m and 1 <= int(m.group(1)) <= n: out[int(m.group(1)) - 1] = m.group(2).strip()
    return [out.get(i) for i in range(n)]

def limpiar(en, tr):
    tr = re.sub(r'\s*\|\|.*$', '', tr)            # (por si copia la referencia)
    tr = re.sub(r'\s*¶\s*', ' ', tr).strip().strip('"').strip()
    if '<B>' not in en: tr = tr.replace('<B>', '').replace('</B>', '')       # (se las inventaba)
    if not en.rstrip().endswith(('.', '!', '?')) and tr.endswith(('.', '。')) and not tr.endswith('...'): tr = tr[:-1]
    return tr

# ---------------------------------------------------------------- 1) traducir (TranslateGemma)
def p_traducir(code, grupo):
    b = NOMBRES[code]
    txt = '\n'.join(una(f'{i + 1}. {g}   ||   (es: {ES.get(g, "")})') for i, g in enumerate(grupo))
    return (f'You are a professional English to {b} video game localizer. {CONTEXTO} Each numbered line has the English '
            f'text, then "||" and an approved Spanish translation in parentheses as a reference for the meaning. Translate '
            f'ONLY the English text into {b}, using the Spanish only to understand the meaning. Keep leading and trailing '
            f'symbols such as - # : ! ? % exactly. Answer one line per number, same numbers, no Spanish, no explanations.'
            f'{glosario(code, grupo)}\n\n{txt}')

def traducir(code):
    hecho = cargar(code, 'gemma')
    pend = [t for t in textos_fuente() if t not in hecho]
    print(f'{code} traducir: {len(hecho)} hechos, {len(pend)} pendientes', flush=True); t0 = time.time()
    for i in range(0, len(pend), LOTE):
        grupo = pend[i:i + LOTE]
        res = numeradas(pedir('gemma', p_traducir(code, grupo)), len(grupo))
        for en, tr in zip(grupo, res):
            if tr is None: tr = numeradas(pedir('gemma', p_traducir(code, [en])), 1)[0] or en
            hecho[en] = limpiar(en, tr)
        guardar(code, 'gemma', hecho)
        print(f'  {code} {min(i + LOTE, len(pend))}/{len(pend)}  {time.time() - t0:.0f} s', flush=True)
    print(f'{code} traducir: FIN', flush=True)

# ---------------------------------------------------------------- 2) y 3) revisar (Qwen, Gemma 4)
def p_revisar(code, grupo, tr):
    b = NOMBRES[code]
    txt = '\n'.join(una(f'{i + 1}. EN: {g} || ES: {ES.get(g, "")} || {code.upper()}: {tr[g]}') for i, g in enumerate(grupo))
    return (f'You are a native {b} video game localization reviewer. {CONTEXTO} Each numbered line has the English original '
            f'(EN), an approved Spanish translation (ES) for reference, and a {b} translation to review. For EACH number answer '
            f'exactly one line: "N. OK" if the {b} translation is correct, natural and fits a game UI, or "N. " followed ONLY '
            f'by the corrected {b} translation (wrong meaning, grammar, unnatural wording, wrong game term, untranslated words, '
            f'English or Spanish words left in it). Keep numbers, % and leading/trailing symbols. No explanations.'
            f'{glosario(code, grupo)}\n\n{txt}')

def revisar(modelo, code):
    tr = cargar(code, 'gemma'); rev = cargar(code, 'rev_' + modelo)
    pend = [k for k in tr if k not in rev]
    textos_fuente()
    print(f'{code} revisar {modelo}: {len(rev)} hechos, {len(pend)} pendientes', flush=True); t0 = time.time()
    for i in range(0, len(pend), LOTE):
        grupo = pend[i:i + LOTE]
        res = numeradas(pedir(modelo, p_revisar(code, grupo, tr)), len(grupo))
        for en, r in zip(grupo, res):
            if r is None: r = '?'
            r = re.sub(r'^\s*N\s*[.:]\s*', '', r)        # (Gemma 4 copia la «N.» del enunciado)
            rev[en] = 'OK' if re.fullmatch(r'\s*(OK|ok|Ok)[.!]?\s*', r) else limpiar(en, r)
        guardar(code, 'rev_' + modelo, rev)
        print(f'  {code} {modelo} {min(i + LOTE, len(pend))}/{len(pend)}  {time.time() - t0:.0f} s', flush=True)
    print(f'{code} revisar {modelo}: FIN', flush=True)

# ---------------------------------------------------------------- combinar
def norm(s): return re.sub(r'\s+', ' ', s).strip().rstrip('.。!！').lower()

def combinar(code):
    textos_fuente()
    tr = cargar(code, 'gemma'); a = cargar(code, 'rev_qwen'); b = cargar(code, 'rev_gemma4')
    # (19-10, usuario: «de Gemma 4 salta a ti directamente») sin Qwen cuenta solo Gemma 4: lo que no objeta se queda; lo
    # que objeta va a las dudas con su propuesta, para Claude
    if not a: a = b
    final = {}; dudas = {}; n = {'ok': 0, 'iguales': 0, 'duda': 0}
    for en, t in tr.items():
        ra, rb = a.get(en, '?'), b.get(en, '?')
        oka = ra == 'OK' or norm(ra) == norm(t); okb = rb == 'OK' or norm(rb) == norm(t)
        if oka and okb: final[en] = t; n['ok'] += 1
        elif not oka and not okb and norm(ra) == norm(rb) and ra != '?' and a is not b: final[en] = ra; n['iguales'] += 1
        else:
            final[en] = t; n['duda'] += 1
            dudas[en] = {'es': ES.get(en, ''), 'gemma': t, 'qwen': ra, 'gemma4': rb}
    guardar(code, 'textos', final); guardar(code, 'dudas', dudas)
    print(f'{code} combinar: {n}', flush=True)

if __name__ == '__main__':
    orden = sys.argv[1]
    if orden == 'traducir':
        for c in sys.argv[2:]: traducir(c)
    elif orden == 'revisar':
        for c in sys.argv[3:]: revisar(sys.argv[2], c)
    elif orden == 'combinar':
        for c in sys.argv[2:]: combinar(c)

# ---------------------------------------------------------------- tutear (19-10)
# Francés y ruso mezclaban «tu / vous» y «ты / вы». Las frases con la forma de usted se retraducen con orden explícita
# de tutear (el español del mod tutea) y van a <c>_gemma.json; luego `combinar` y la revisión de Claude.
USTED = {'fr': r"\b(vous|votre|vos|Vous|Votre|Vos)\b|^[A-ZÉ][a-zéè]+ez\b",
         'ru': r"\b(вы|вас|вам|ваш\w*|Вы|Вас|Вам|Ваш\w*)\b|\b\w+(ите|йте)\b"}
TUTEO = {'fr': 'Address the player ONLY with the informal "tu" (tu, ton, ta, tes, toi; imperatives like "Clique", '
               '"Appuie", "Choisis"), NEVER "vous".',
         'ru': 'Address the player ONLY with the informal "ты" (твой, тебе; imperatives like "Нажми", "Выбери"), NEVER "вы".'}

def tutear(code):
    tr = cargar(code, 'gemma'); textos_fuente()
    malas = [k for k, v in tr.items() if re.search(USTED[code], v)]
    print(f'{code} tutear: {len(malas)} frases', flush=True)
    for i in range(0, len(malas), LOTE):
        grupo = malas[i:i + LOTE]
        p = p_traducir(code, grupo).replace('Answer one line per number', TUTEO[code] + ' Answer one line per number')
        res = numeradas(pedir('gemma', p), len(grupo))
        for en, t in zip(grupo, res):
            if t and not re.search(USTED[code], t): tr[en] = limpiar(en, t)
        guardar(code, 'gemma', tr)
    quedan = [k for k, v in tr.items() if re.search(USTED[code], v)]
    print(f'{code} tutear: FIN, quedan {len(quedan)} con usted', flush=True)

if __name__ == '__main__' and sys.argv[1] == 'tutear':
    for c in sys.argv[2:]: tutear(c)
