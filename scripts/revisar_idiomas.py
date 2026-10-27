# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Control de calidad automático de piezas/31_idiomas/fuente/<código>_textos.json.
  python scripts/revisar_idiomas.py <código> [--todo]
Avisa de: vacío, igual al inglés, restos de la referencia española «(es:» / «||», números o % distintos, etiquetas
<B> perdidas, símbolo inicial/final perdido (- # : ! ? …), saltos de línea de más y longitud excesiva (> 1,7 veces el
inglés en textos de menos de 30 letras: los botones no estiran). Con --todo lista también los textos sin aviso.
"""
import json, os, re, sys, unicodedata
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJK = {'ja', 'zh_hans', 'zh_hant'}

def ancho(s, cjk):
    # (en chino/japonés un carácter ocupa ~1,8 letras latinas)
    return sum(1.8 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)

def revisar(code, todo=False):
    d = json.load(open(os.path.join(RAIZ, 'piezas', '31_idiomas', 'fuente', f'{code}_textos.json'), encoding='utf-8'))
    avisos = 0
    for en, tr in d.items():
        a = []
        if not tr.strip(): a.append('VACÍO')
        elif tr.strip() == en.strip() and re.search(r'[a-z]{3}', en): a.append('IGUAL AL INGLÉS')
        if '(es:' in tr or '||' in tr: a.append('RESTO DE LA REFERENCIA')
        if sorted(re.findall(r'\d+', en)) != sorted(re.findall(r'\d+', tr)): a.append('NÚMEROS')
        if en.count('%') != tr.count('%'): a.append('%')
        if en.count('<B>') != tr.count('<B>') or en.count('</B>') != tr.count('</B>'): a.append('<B>')
        for c in '-#':
            if en.startswith(c) and not tr.startswith(c): a.append('INICIO ' + c)
        if en.rstrip().endswith(':') and not tr.rstrip().endswith((':', '：')): a.append('FIN :')
        if tr.count('\n') > max(en.count('\n'), 0) + 1: a.append('RENGLONES')
        if len(en) < 30 and ancho(tr, code in CJK) > max(1.7 * len(en), len(en) + 6): a.append('LARGO')
        if a or todo:
            avisos += bool(a)
            print(f'[{",".join(a) or "ok"}] {en!r} => {tr!r}')
    print(f'--- {code}: {len(d)} textos, {avisos} con aviso')

if __name__ == '__main__':
    revisar(sys.argv[1], '--todo' in sys.argv)
