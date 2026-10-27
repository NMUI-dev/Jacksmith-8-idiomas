# -*- coding: utf-8 -*-
"""Prepara work/tr/en_all.json: todas las cadenas inglesas que puede mostrar el juego
(textos de la línea de tiempo exportados con FFDec + cadenas del código que parecen texto visible)."""
import os, re, json, html, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
W = os.path.join(ROOT, 'work')
out = {}

def clean(s):
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    s = re.sub(r'\n?--- RECORDSEPARATOR ---\n?', '\n', s)
    s = html.unescape(s).replace(' ', ' ').replace('�', "'")
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' ?\n ?', '\n', s).strip()
    return s

for f in sorted(os.listdir(os.path.join(W, 'txt_plain')), key=lambda x: int(x.split('.')[0])):
    s = clean(open(os.path.join(W, 'txt_plain', f), encoding='utf-8', errors='replace').read())
    if not re.search(r'[A-Za-z]{2}', s): continue
    out.setdefault(s, {'en': s, 'donde': []})['donde'].append('campo ' + f[:-4])

code = json.load(open(os.path.join(W, 'code_strings.json'), encoding='utf-8'))
LOGGY = re.compile(r'(^\(|\)$|^\[|Error|ERROR|ERR:|^\w+_\w+$|^[A-Z]{2}-\d+$|^[a-z]+[A-Z]\w*$|^QName|^http|\.sol$|^flash\.|^swordGame|^com\.|^mx\.)')
SKIPFILES = ('ExtensionSteamHelper', 'DesktopUtility', 'FliplineAPI', 'APIHelper', 'DataHelper', 'Tracer', 'SoundManager')
for s, files in code.items():
    fs = [f for f in files if not any(k in f for k in SKIPFILES)]
    if not fs or LOGGY.search(s): continue
    if not (f.startswith('swordGame') or f.startswith('flipline') or '_fla' in f for f in fs): continue
    c = clean(s)
    if not c: continue
    e = out.setdefault(c, {'en': c, 'donde': []})
    e['donde'] += [f.replace('.class.asasm', '').split('/')[-1] for f in fs][:3]
    if s != c: e['en_exacto'] = s      # con sus espacios al borde (para cadenas que se concatenan)

lst = sorted(out.values(), key=lambda e: (e['donde'][0], e['en']))
os.makedirs(os.path.join(W, 'tr'), exist_ok=True)
json.dump(lst, open(os.path.join(W, 'tr', 'en_all.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(lst), 'cadenas;', sum(len(e['en']) for e in lst), 'caracteres')
