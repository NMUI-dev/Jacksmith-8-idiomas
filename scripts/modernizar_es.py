# -*- coding: utf-8 -*-
"""Regla de vocabulario (13-oct): palabras modernas y conocidas. Aplica los cambios a las tablas fuente
(piezas/30_espanol/fuente/es_textos.json y es_extra.json) y deja la lista en work/cambios_vocabulario.txt."""
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'piezas', '30_espanol', 'fuente')

# (patrón, sustituto, nota). Se respetan mayúsculas iniciales.
REGLAS = [
    (r'fanfarrias', 'melodías', 'fanfarria -> melodía'),
    (r'fanfarria', 'melodía', ''),
    (r'alfanjes', 'sables', 'alfanje -> sable'),
    (r'(el|un|del|al) alfanje', r'\1 sable', ''),
    (r'alfanje', 'sable', ''),
    (r'un emplumado', 'unas plumas', 'emplumado -> plumas'),
    (r'emplumados', 'plumas', ''),
    (r'emplumado', 'plumas', ''),
    (r'del astil', 'de la flecha', 'astil -> vara de la flecha'),
    (r'al astil', 'a la vara de la flecha', ''),
    (r'el astil', 'la vara de la flecha', ''),
    (r'astil', 'vara', ''),
    (r'clavijas', 'clavos', 'clavija -> clavo'),
    (r'clavija', 'clavo', ''),
    (r'picas', 'lanzas', 'pica -> lanza'),
    (r'pica', 'lanza', ''),
    (r'piquero', 'lancero', 'piquero -> lancero'),
    (r'experto en astas', 'experto en lanzas', ''),
    (r'pupilo', 'ayudante', 'pupilo -> ayudante'),
    (r'hallados', 'encontrados', 'hallar -> encontrar'),
    (r'hallarás', 'encontrarás', ''),
    (r'hallar', 'encontrar', ''),
    (r'halla', 'encuentra', ''),
    (r'báculo', 'bastón', 'báculo -> bastón'),
    (r'cantero', 'picapedrero', 'cantero -> picapedrero'),
]

def aplicar(v, log, k):
    o = v
    for pat, rep, nota in REGLAS:
        def f(m, rep=rep):
            r = m.expand(rep) if '\\' in rep else rep
            s = m.group(0)
            if s.isupper(): return r.upper()
            if s[0].isupper(): return r[0].upper() + r[1:]
            return r
        v = re.sub(r'(?<![A-Za-zÁÉÍÓÚÑÜáéíóúñü])' + pat + r'(?![A-Za-zÁÉÍÓÚÑÜáéíóúñü])', f, v, flags=re.I)
    if v != o: log.append('%s\n    antes:  %s\n    ahora:  %s' % (k.replace('\n', ' / ')[:70], o, v))
    return v

if __name__ == '__main__':
    log = []
    for name in ('es_textos.json', 'es_extra.json'):
        p = os.path.join(SRC, name)
        d = json.load(open(p, encoding='utf-8'))
        d2 = {k: (aplicar(v, log, k) if v != k else v) for k, v in d.items()}
        json.dump(d2, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(ROOT, 'work', 'cambios_vocabulario.txt'), 'w', encoding='utf-8').write('\n'.join(log))
    print(len(log), 'frases cambiadas')
