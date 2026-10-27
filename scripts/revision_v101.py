# -*- coding: utf-8 -*-
"""Revisión del usuario de la v1.0.0 (13-oct) aplicada a las tablas fuente del español:
 - Grip = «mango» (corto, no se corta); Handle (el conjunto) = «agarre». Nada de abreviaturas («Empuñ.»).
 - Nombres de zonas del mapa traducidos cuando se puede.
 - Huecos para iconos «(   )» con el mismo ancho que en inglés (espacios duros).
Deja la lista de cambios en work/cambios_v101.txt. Se puede ejecutar más de una vez."""
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'piezas', '30_espanol', 'fuente')
L = r'(?<![A-Za-zÁÉÍÓÚÑÜáéíóúñü])'; R = r'(?![A-Za-zÁÉÍÓÚÑÜáéíóúñü])'

HANDLE = [(r'el mango', 'el agarre'), (r'del mango', 'del agarre'), (r'al mango', 'al agarre'), (r'en Mango en', 'en Agarre en'), (r'mango', 'agarre')]
GRIP = [(r'una de tus empuñaduras', 'uno de tus mangos'), (r'una empuñadura', 'un mango'), (r'luego una EMPUÑADURA', 'luego un MANGO'),
        (r'las empuñaduras', 'los mangos'), (r'empuñaduras', 'mangos'), (r'empuñadura', 'mango'), (r'Empuñ\.', 'Mangos')]
ZONAS = [('Lowlands', 'Tierras Bajas'), ('Cinder Springs', 'Manantiales de Ceniza'), ('Alpine Ridge', 'Cresta Alpina'),
         ('Boneyard Dunes', 'Dunas de Huesos'), ('Evershade Forest', 'Bosque Sombrío'), ('Wormwood Hollow', 'Valle Amargo')]

def sub(v, pairs):
    for a, b in pairs:
        def f(m, b=b):
            s = m.group(0)
            if s.isupper() and len(s) > 2: return b.upper()
            return b[0].upper() + b[1:] if s[0].isupper() else b
        v = re.sub(L + a + R, f, v, flags=re.I)
    return v

def main():
    log = []
    for name in ('es_textos.json', 'es_extra.json'):
        p = os.path.join(SRC, name); d = json.load(open(p, encoding='utf-8')); out = {}
        for k, v in d.items():
            o = v
            if v != k:
                if re.search(r'handle|hilt', k, re.I): v = sub(v, HANDLE)
                v = sub(v, GRIP)
            for en, es in ZONAS:
                if en in v and not (k == v and k != en): v = v.replace(en, es)
                if k == en: v = es
            v = v.replace('a Bosque Sombrío', 'al Bosque Sombrío').replace('a Valle Amargo', 'al Valle Amargo').replace('de Bosque Sombrío', 'del Bosque Sombrío').replace('de Valle Amargo', 'del Valle Amargo')
            # hueco de icono: mismo ancho que el inglés, con espacios duros
            m = re.search(r'\( *\)', v)
            if m and '(' in k: v = v[:m.start()] + '(' + ' ' * 13 + ')' + v[m.end():]
            if v != o: log.append('%s\n    antes: %s\n    ahora: %s' % (k.replace('\n', ' / ')[:70], o, v))
            out[k] = v
        json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    x = os.path.join(SRC, 'es_extra.json'); d = json.load(open(x, encoding='utf-8'))
    d.update({'Grips': 'Mangos', 'Grip': 'Mango', 'Handle': 'Agarre'})
    for en, es in ZONAS: d[en] = es
    json.dump(d, open(x, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(ROOT, 'work', 'cambios_v101.txt'), 'w', encoding='utf-8').write('\n'.join(log))
    print(len(log), 'frases cambiadas')

if __name__ == '__main__': main()
