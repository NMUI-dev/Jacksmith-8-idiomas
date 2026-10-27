# -*- coding: utf-8 -*-
"""Saca las cadenas (pushstring) del desensamblado limpio -> work/code_strings.json {cadena: [archivos]}."""
import os, re, json, collections, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root = os.path.join(ROOT, 'work', 'abc', 'Main-0')

def unesc(s):
    out = []; i = 0
    while i < len(s):
        c = s[i]
        if c == '\\':
            n = s[i + 1]
            if n == 'n': out.append('\n'); i += 2
            elif n == 'r': out.append('\r'); i += 2
            elif n == 't': out.append('\t'); i += 2
            elif n == 'x': out.append(('x', int(s[i + 2:i + 4], 16))); i += 4
            else: out.append(n); i += 2
        else: out.append(c); i += 1
    # las secuencias \xNN son bytes UTF-8
    b = bytearray()
    for o in out:
        if isinstance(o, tuple): b.append(o[1])
        else: b += o.encode('utf-8')
    return b.decode('utf-8', 'replace')

def all_strings():
    res = collections.defaultdict(set)
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if not f.endswith('.class.asasm'): continue
            rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/')
            t = open(os.path.join(dp, f), encoding='utf-8').read()
            for m in re.finditer(r'^\s+pushstring\s+"((?:[^"\\]|\\.)*)"', t, re.M):
                res[unesc(m.group(1))].add(rel)
    return res

def texty(s):
    if len(s) < 2: return False
    if re.fullmatch(r'[a-z0-9_.\-/:#]+', s): return False
    if re.search(r'\.(wav|mp3|png|swf)$', s): return False
    return bool(re.search(r'[A-Za-z]{2}', s))

if __name__ == '__main__':
    res = all_strings()
    cand = {s: sorted(v) for s, v in res.items() if texty(s)}
    json.dump(cand, open(os.path.join(ROOT, 'work', 'code_strings.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    byfile = collections.Counter()
    for s, v in cand.items():
        for f in v: byfile[f] += 1
    print(len(res), 'cadenas;', len(cand), 'candidatas')
    for f, n in byfile.most_common(50): print(n, f)
