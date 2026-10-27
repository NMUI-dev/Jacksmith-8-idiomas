# -*- coding: utf-8 -*-
"""Construye el Main.assets modificado de Jacksmith a partir del original y de las piezas de `piezas/`.

Uso:  python scripts/build.py [--lab] [--solo 10_nucleo,20_volumen] [--out ruta]
  --lab   añade la pieza 00_laboratorio (permite el id de AIR «.lab» para no tocar las partidas reales)
Cada pieza es una carpeta `piezas/NN_nombre/` con un `pieza.py` que define `aplicar(ctx)`.
Se aplican en orden alfabético sobre una copia limpia del desensamblado (work/abc/Main-0).
"""
import sys, os, re, shutil, subprocess, importlib.util, argparse, time
try: sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")   # (19-10: rótulos en japonés/chino en la consola)
except Exception: pass
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
RABC = os.path.join(TOOLS, 'rabcdasm')
ORIG = os.path.join(ROOT, 'original', 'Data', 'assets', 'Main.assets')
PRISTINE = os.path.join(ROOT, 'work', 'abc')          # Main.swf + Main-0.abc + Main-0/ (desensamblado limpio)
BUILD = os.path.join(ROOT, 'work', 'build')

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stdout); print(r.stderr); raise SystemExit('FALLO: ' + ' '.join(map(str, cmd)))
    return r.stdout

class Ctx:
    """Lo que recibe cada pieza."""
    def __init__(self, lab):
        self.root = ROOT; self.lab = lab
        self.asm = os.path.join(BUILD, 'Main-0')
        self.swf = os.path.join(BUILD, 'Main.swf')
        self.extra_abc = []      # [(nombre, ruta .abc)] que se insertan ANTES del código del juego
        self.extra_files = {}    # ruta relativa al juego -> ruta de origen (archivos nuevos del mod)
        self.post_swf = []       # funciones(ctx) que retocan el SWF ya ensamblado (textos, fuentes...)
        self.log = []
    def path(self, rel): return os.path.join(self.asm, rel.replace('/', os.sep))
    def read(self, rel):
        with open(self.path(rel), encoding='utf-8', newline='') as f: return f.read()
    def write(self, rel, txt):
        with open(self.path(rel), 'w', encoding='utf-8', newline='') as f: f.write(txt)
    def sub(self, rel, old, new, count=1):
        """Sustitución exacta; falla si no aparece `count` veces (count=None: al menos una)."""
        t = self.read(rel); n = t.count(old)
        if n == 0 or (count is not None and n != count):
            raise SystemExit(f'[{rel}] esperaba {count} apariciones y hay {n}: {old[:80]!r}')
        self.write(rel, t.replace(old, new)); return n
    def method(self, rel, name):
        """Devuelve (texto, inicio, fin) del cuerpo `code ... end ; code` del método con refid que acaba en name."""
        t = self.read(rel)
        m = re.search(r'refid "[^"]*/' + re.escape(name) + r'"', t)
        if not m: raise SystemExit(f'[{rel}] no encuentro el método {name}')
        a = t.index('\n     code', m.end()) if '\n     code' in t[m.end():] else None
        a = re.search(r'\n\s+code\r?\n', t[m.end():]).end() + m.end()
        b = re.search(r'\n\s+end ; code', t[a:]).start() + a
        return t, a, b
    def edit_method(self, rel, name, fn, add_stack=0, add_locals=0):
        t, a, b = self.method(rel, name)
        body = fn(t[a:b])
        head_start = t.rfind('body', 0, a)
        head = t[head_start:a]
        if add_stack:
            head = re.sub(r'maxstack (\d+)', lambda m: 'maxstack %d' % (int(m.group(1)) + add_stack), head, 1)
        if add_locals:
            head = re.sub(r'localcount (\d+)', lambda m: 'localcount %d' % (int(m.group(1)) + add_locals), head, 1)
        self.write(rel, t[:head_start] + head + body + t[b:])

def load_piezas(lab, solo):
    d = os.path.join(ROOT, 'piezas'); out = []
    for n in sorted(os.listdir(d)):
        p = os.path.join(d, n, 'pieza.py')
        if not os.path.isfile(p): continue
        if n.startswith('00_') and not lab: continue
        if solo and n not in solo and not n.startswith('00_'): continue
        spec = importlib.util.spec_from_file_location('pieza_' + n, p); m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m); out.append((n, m))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--lab', action='store_true'); ap.add_argument('--solo', default='')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    t0 = time.time()
    if os.path.isdir(BUILD): shutil.rmtree(BUILD)
    os.makedirs(BUILD)
    shutil.copytree(os.path.join(PRISTINE, 'Main-0'), os.path.join(BUILD, 'Main-0'))
    shutil.copy(ORIG, os.path.join(BUILD, 'Main.swf'))
    ctx = Ctx(a.lab)
    piezas = load_piezas(a.lab, [s for s in a.solo.split(',') if s])
    for n, m in piezas:
        print('== pieza', n); m.aplicar(ctx)
    run([os.path.join(RABC, 'rabcasm.exe'), os.path.join(BUILD, 'Main-0', 'Main-0.main.asasm')])
    run([os.path.join(RABC, 'abcreplace.exe'), ctx.swf, '0', os.path.join(BUILD, 'Main-0', 'Main-0.main.abc')])
    if ctx.extra_abc:
        sys.path.insert(0, os.path.join(ROOT, 'scripts')); import swftool
        swftool.insert_abcs(ctx.swf, ctx.extra_abc)
    for fn in ctx.post_swf: fn(ctx)
    out = a.out or os.path.join(ROOT, 'out', 'lab' if a.lab else 'entrega')
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'Data', 'assets'))
    shutil.copy(ctx.swf, os.path.join(out, 'Data', 'assets', 'Main.assets'))
    for rel, src in ctx.extra_files.items():
        dst = os.path.join(out, rel.replace('/', os.sep)); os.makedirs(os.path.dirname(dst), exist_ok=True)
        (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, dst)
    print('piezas:', ', '.join(n for n, _ in piezas)); print('salida:', out, '(%.1f s)' % (time.time() - t0))

if __name__ == '__main__': main()
