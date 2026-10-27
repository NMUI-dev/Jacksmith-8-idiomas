# -*- coding: utf-8 -*-
"""Pieza 31 — MÁS IDIOMAS (Claude Code, 19-10-2026): italiano, portugués (Brasil), francés, alemán, ruso, japonés,
chino simplificado y chino tradicional.

 - Genera Data/mods/31_idiomas/lang/<código>.json desde fuente/<código>_textos.json (traducción de TranslateGemma con la
   española revisada como referencia; scripts/traducir_idiomas.py), fuente/<código>_extra.json (a mano, gana) y
   fuente/<código>_patrones.json (scripts/patrones_idiomas.py).
 - Textos que eran estáticos de varios renglones: mismo nº de renglones que el inglés (como la pieza 30); en chino y
   japonés se reparte por CARACTERES (no hay espacios entre palabras).
 - Nombres de TODOS los idiomas escritos en cada idioma (regla del usuario) y aviso de traducción automática bajo el
   selector (segunda línea de «More languages coming soon»).
 - Añade a las fuentes del juego las letras que falten (scripts/glifos_ttf.py: misma familia si la tenemos, si no Noto).
   Va antes que la pieza 40 (rótulos), que dibuja con esas mismas fuentes.
"""
import os, sys, json, re, shutil

CODIGOS = ['it', 'pt', 'fr', 'de', 'ru', 'ja', 'zh_hans', 'zh_hant']
CJK = {'ja', 'zh_hans', 'zh_hant'}
# nombre de cada idioma en cada idioma: NOMBRES[idioma activo][código]
NOMBRES = {
 'es': {'es': 'Español', 'en': 'Inglés', 'it': 'Italiano', 'pt': 'Portugués', 'fr': 'Francés', 'de': 'Alemán', 'ru': 'Ruso',
        'ja': 'Japonés', 'zh_hans': 'Chino simplificado', 'zh_hant': 'Chino tradicional'},
 'en': {'es': 'Spanish', 'en': 'English', 'it': 'Italian', 'pt': 'Portuguese', 'fr': 'French', 'de': 'German', 'ru': 'Russian',
        'ja': 'Japanese', 'zh_hans': 'Simplified Chinese', 'zh_hant': 'Traditional Chinese'},
 'it': {'es': 'Spagnolo', 'en': 'Inglese', 'it': 'Italiano', 'pt': 'Portoghese', 'fr': 'Francese', 'de': 'Tedesco', 'ru': 'Russo',
        'ja': 'Giapponese', 'zh_hans': 'Cinese semplificato', 'zh_hant': 'Cinese tradizionale'},
 'pt': {'es': 'Espanhol', 'en': 'Inglês', 'it': 'Italiano', 'pt': 'Português', 'fr': 'Francês', 'de': 'Alemão', 'ru': 'Russo',
        'ja': 'Japonês', 'zh_hans': 'Chinês simplificado', 'zh_hant': 'Chinês tradicional'},
 'fr': {'es': 'Espagnol', 'en': 'Anglais', 'it': 'Italien', 'pt': 'Portugais', 'fr': 'Français', 'de': 'Allemand', 'ru': 'Russe',
        'ja': 'Japonais', 'zh_hans': 'Chinois simplifié', 'zh_hant': 'Chinois traditionnel'},
 'de': {'es': 'Spanisch', 'en': 'Englisch', 'it': 'Italienisch', 'pt': 'Portugiesisch', 'fr': 'Französisch', 'de': 'Deutsch',
        'ru': 'Russisch', 'ja': 'Japanisch', 'zh_hans': 'Chinesisch (vereinfacht)', 'zh_hant': 'Chinesisch (traditionell)'},
 'ru': {'es': 'Испанский', 'en': 'Английский', 'it': 'Итальянский', 'pt': 'Португальский', 'fr': 'Французский', 'de': 'Немецкий',
        'ru': 'Русский', 'ja': 'Японский', 'zh_hans': 'Китайский (упрощ.)', 'zh_hant': 'Китайский (трад.)'},
 'ja': {'es': 'スペイン語', 'en': '英語', 'it': 'イタリア語', 'pt': 'ポルトガル語', 'fr': 'フランス語', 'de': 'ドイツ語', 'ru': 'ロシア語',
        'ja': '日本語', 'zh_hans': '中国語（簡体字）', 'zh_hant': '中国語（繁体字）'},
 'zh_hans': {'es': '西班牙语', 'en': '英语', 'it': '意大利语', 'pt': '葡萄牙语', 'fr': '法语', 'de': '德语', 'ru': '俄语', 'ja': '日语',
        'zh_hans': '简体中文', 'zh_hant': '繁体中文'},
 'zh_hant': {'es': '西班牙文', 'en': '英文', 'it': '義大利文', 'pt': '葡萄牙文', 'fr': '法文', 'de': '德文', 'ru': '俄文', 'ja': '日文',
        'zh_hans': '簡體中文', 'zh_hant': '繁體中文'},
}
# nota bajo el selector: «Próximamente más idiomas» + aviso de traducción automática (pedido del usuario: «si la
# traducción tiene errores, perdón; el objetivo es que la mayor cantidad de personas lo jueguen»)
NOTA = {
 'it': 'Presto altre lingue\nTradotto con l\'IA: scusa per eventuali errori',
 'pt': 'Mais idiomas em breve\nTraduzido com IA: desculpe por eventuais erros',
 'fr': 'D\'autres langues arrivent bientôt\nTraduit avec l\'IA : désolé pour les erreurs',
 'de': 'Weitere Sprachen folgen bald\nMit KI übersetzt: Entschuldigung für Fehler',
 'ru': 'Скоро появятся другие языки\nПереведено с помощью ИИ: простите за ошибки',
 'ja': '他の言語も近日追加予定\nAIで翻訳しました。誤りがあればご容赦ください',
 'zh_hans': '更多语言即将推出\n本翻译借助AI完成，如有错误敬请谅解',
 'zh_hant': '更多語言即將推出\n本翻譯藉助AI完成，如有錯誤敬請見諒',
}

def repartir_cjk(t, lens):
    """Como la pieza 30, pero cortando entre caracteres (chino y japonés no separan palabras con espacios)."""
    s = t.replace('\n', '')
    n = len(lens)
    if n < 2 or not s: return t
    tot = float(sum(max(1, l) for l in lens)); out = []; i = 0; acum = 0.0
    for k, l in enumerate(lens):
        acum += max(1, l) / tot
        j = len(s) if k == n - 1 else max(i + 1 if i < len(s) else i, int(round(len(s) * acum)))
        while j < len(s) and s[j] in '，。、！？：；）」』,.!?:;)': j += 1        # no empezar renglón con puntuación
        out.append(s[i:j]); i = j
    return '\n'.join(out)

def aplicar(ctx):
    here = os.path.dirname(os.path.abspath(__file__)); src = os.path.join(here, 'fuente')
    sys.path.insert(0, os.path.join(ctx.root, 'scripts')); sys.path.insert(0, os.path.join(ctx.root, 'piezas', '30_espanol'))
    import swfmod
    from pieza import repartir                      # (la de la pieza 30)
    origen = json.load(open(os.path.join(ctx.root, 'piezas', '30_espanol', 'fuente', 'en_origen.json'), encoding='utf-8'))
    frag = {e['en'] for e in origen if e.get('en_exacto') and (e['en_exacto'] != e['en_exacto'].strip() or e['en_exacto'].startswith('<'))}
    def norm(k): return re.sub(r'[\s ]+', '', k).replace('‘', "'").replace('’', "'")
    orig_swf = os.path.join(ctx.root, 'original', 'Data', 'assets', 'Main.assets')
    tmp = os.path.join(ctx.root, 'work', '_estaticos31.swf'); shutil.copy(orig_swf, tmp)
    rep = []; swfmod.static_to_dynamic(tmp, orig_swf, rep); os.remove(tmp)
    out = os.path.join(ctx.root, 'work', 'datos_31_idiomas')
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'lang'))
    chars = set(); origen_cjk = {}
    for code in CODIGOS:
        ruta = os.path.join(src, f'{code}_textos.json')
        if not os.path.exists(ruta): print(f'   {code}: sin traducción, no se incluye'); continue
        base = json.load(open(ruta, encoding='utf-8'))
        extra_r = os.path.join(src, f'{code}_extra.json')
        extra = json.load(open(extra_r, encoding='utf-8')) if os.path.exists(extra_r) else {}
        pats = json.load(open(os.path.join(src, f'{code}_patrones.json'), encoding='utf-8'))
        textos = {k: v for k, v in base.items() if k not in frag and v.strip() and v != k}
        nx = {norm(k) for k in extra}
        textos = {k: v for k, v in textos.items() if norm(k) not in nx}
        textos.update(extra)
        textos['More languages coming soon'] = NOTA[code]
        if code == 'zh_hant':
            # (19-10) el traductor colaba caracteres SIMPLIFICADOS en el tradicional (116 frases): OpenCC s2tw (solo caracteres: s2twp cambiaba «你的士兵» por «你計程車兵», de «的士» = taxi) lo deja
            # todo en tradicional de Taiwán, también lo corregido a mano
            sys.path.insert(0, os.path.join(ctx.root, 'tools', 'pydeps'))
            from opencc import OpenCC
            cc = OpenCC('s2tw'); textos = {k: cc.convert(v) for k, v in textos.items()}
        porclave = {norm(k): k for k in textos}; nrep = 0
        for cid, text in rep:
            lineas = text.split('\r')
            if len(lineas) < 2: continue
            k = porclave.get(norm(text))
            if not k: continue
            lens = [len(l.strip()) for l in lineas]
            textos[k] = repartir_cjk(textos[k], lens) if code in CJK else repartir(textos[k], lens); nrep += 1
        nombres = NOMBRES[code]
        json.dump({'nombre': nombres[code], 'nombre_en': NOMBRES['en'][code], 'codigo': code, 'idiomas': nombres,
                   'textos': textos, 'patrones': pats},
                  open(os.path.join(out, 'lang', f'{code}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        todo = ''.join(textos.values()) + ''.join(p for _, p in pats) + ''.join(nombres.values())
        chars |= set(todo)
        if code in CJK:
            for c in todo: origen_cjk.setdefault(c, code)        # (orden de CODIGOS: ja, zh_hans, zh_hant)
        print(f'   {code}.json: {len(textos)} textos, {len(pats)} patrones, {nrep} de varios renglones')
    # los nombres de los idiomas también salen en español e inglés (selector) y en los rótulos de la pieza 40
    rot_chars = set(''.join(''.join(d.values()) for d in NOMBRES.values()))
    for d in NOMBRES.values(): chars |= set(''.join(d.values()))
    try:
        for e in json.load(open(os.path.join(ctx.root, 'piezas', '40_rotulos', 'rotulos.json'), encoding='utf-8')):
            for code in CODIGOS:
                if isinstance(e.get(code), str): chars |= set(e[code]); rot_chars.update(e[code])
    except Exception as ex: print('   rótulos:', ex)
    shutil.copy(os.path.join(here, 'datos', 'mod.json'), os.path.join(out, 'mod.json'))
    ctx.extra_files['Data/mods/31_idiomas'] = out
    ctx.log.append(('idiomas', len(CODIGOS)))

    def glifos(c):
        import glifos_ttf
        glifos_ttf.PRIORIDAD = rot_chars
        rep2 = []; glifos_ttf.add_glyphs_ttf(c.swf, ''.join(sorted(chars)), origen_cjk, rep2)
        for nombre, n, sin in rep2: print(f'   glifos {nombre}: +{n}' + (f' (sin fuente: {sin})' if sin else ''))
    ctx.post_swf.append(glifos)
