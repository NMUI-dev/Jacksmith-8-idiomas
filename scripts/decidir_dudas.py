# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Revisión de Claude de las DUDAS (frases que Gemma 4 objetó) de cada idioma.
Por defecto se acepta la propuesta de Gemma 4; en DECISIONES[código] van las excepciones por número de duda (orden de
<código>_dudas.json): 'K' = se queda la traducción de TranslateGemma; cualquier otro texto = mi versión.
Escribe el resultado en <código>_textos.json (las correcciones de correcciones_idiomas.py se aplican después y ganan).
  python scripts/decidir_dudas.py <código> [<código>...]
"""
import json, os, re, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(RAIZ, 'piezas', '31_idiomas', 'fuente')
DECISIONES = {
 'zh_hant': {45: 'K', 48: 'K', 50: 'K', 91: 'K', 95: 'K'},
 'zh_hans': {10: 'K', 70: 'K', 115: 'K', 120: '锻造金属时，拉动链条经过优化，便于鼠标操作，尤其是在全屏模式下。'},
 'ja': {6: 'K', 8: 'K', 27: 'K', 71: 'K', 72: 'K', 73: 'K', 74: 'K', 77: '-金のトライデント',
        104: '3つのパーツをすべて中央に取り付けて、斧の頭を作ろう。', 113: 'K', 129: 'K'},
 'ru': {0: 'K', 11: 'K', 12: 'K', 13: 'K', 14: 'K', 15: 'K', 16: 'K', 17: 'K', 18: 'K', 19: 'K', 20: 'K', 26: 'K', 27: 'K',
        28: 'K', 29: 'K', 30: 'K', 41: 'K', 59: 'Оружие воды', 60: 'Воины ветра', 81: 'K', 87: 'K', 89: 'K', 90: 'K', 94: 'K',
        104: 'K', 110: 'K', 117: 'K', 121: 'K', 122: 'K'},
 'de': {0: 'K', 42: 'K', 48: 'K', 49: 'K', 52: 'K', 60: 'Spieße herstellen', 67: 'K'},
 'fr': {0: 'K', 3: 'K', 6: 'K', 14: 'K', 60: 'K', 62: 'K', 63: 'K', 64: 'K', 65: 'K', 66: 'K', 97: 'K', 109: 'K',
        123: 'Marque-pages', 124: 'K', 126: 'K', 133: 'Sauvegarde', 150: 'pour changer de page de pièces'},
 'pt': {0: 'K', 16: 'K', 17: 'K', 19: 'K', 26: 'K', 30: 'K', 42: 'K', 51: 'K', 59: 'K', 61: 'K'},
 'it': {0: 'K', 1: 'K', 41: 'K', 42: 'K', 48: 'K', 52: 'Nome qui', 54: 'K', 55: 'K', 56: 'K', 57: 'K', 59: 'K', 60: 'K',
        62: 'K', 63: 'K', 65: 'K', 67: 'K', 79: 'K', 80: 'K', 81: 'Non preoccuparti se non raggiungi il Forziere del Tesoro ogni giorno!',
        85: 'K', 90: 'Forgiatura di archi', 97: 'Forgiatura di mazze', 104: 'K', 105: 'K', 106: 'K', 107: 'K', 108: 'K',
        109: 'K', 110: 'K', 111: 'Salvataggio'},
}

def aplicar(code):
    dudas = json.load(open(os.path.join(F, f'{code}_dudas.json'), encoding='utf-8'))
    ruta = os.path.join(F, f'{code}_textos.json'); tr = json.load(open(ruta, encoding='utf-8'))
    dec = DECISIONES.get(code, {}); n = {'gemma4': 0, 'K': 0, 'mia': 0}
    for i, (en, d) in enumerate(dudas.items()):
        x = dec.get(i)
        g4 = d['gemma4']
        # reglas automáticas: notas del propio modelo dentro del texto, o propuesta que recorta mucho una frase larga
        if x is None and (re.search(r'Wait|->|\(note|prompt', g4) or (len(d['gemma']) > 40 and len(g4) < 0.6 * len(d['gemma']))):
            x = 'K'
        if x == 'K': tr[en] = d['gemma']; n['K'] += 1
        elif x: tr[en] = x; n['mia'] += 1
        elif d['gemma4'] not in ('?', 'OK', ''): tr[en] = d['gemma4']; n['gemma4'] += 1
    json.dump(tr, open(ruta, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(code, n)

if __name__ == '__main__':
    for c in sys.argv[1:]: aplicar(c)
