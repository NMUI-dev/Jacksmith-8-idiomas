# -*- coding: utf-8 -*-
"""Pieza 10 — NÚCLEO DE MODS (jm.JM): la capa común a todos los mods de Jacksmith.

 - Inyecta el código compilado de src/core (work/core/JMCore-0.abc) antes del código del juego.
 - GameModule.initGame() llama a JM.init(this).
 - Toda asignación «x.text = v» y «x.htmlText = v» del juego pasa por JM.setText / JM.setHtml
   (ahí se traduce según el idioma activo y se ajusta el tamaño para que no desborde).
 - AppSettingsScreen.setupScreen() llama a jm.Options.build(this) (controles añadidos a los ajustes).
 - Copia la carpeta de datos del núcleo: Data/mods/00_nucleo/.
"""
import os, re, subprocess

JM = 'QName(PackageNamespace("jm"), "JM")'
VOID = 'QName(PackageNamespace(""), "%s")'

def call_array(indent, fn):
    """La pila trae [obj, valor]; se empaqueta en un Array y se llama a JM.<fn>(array)."""
    return (f'{indent}newarray            2\n'
            f'{indent}getlex              {JM}\n'
            f'{indent}swap\n'
            f'{indent}callpropvoid        {VOID % fn}, 1\n')

RX = {
    'setText': re.compile(r'^([ \t]+)setproperty\s+(?:Multiname|QName)\((?:PackageNamespace\(""\), )?"text"(?:, \[.*\])?\)[ \t]*\r?\n', re.M),
    'setHtml': re.compile(r'^([ \t]+)setproperty\s+(?:Multiname|QName)\((?:PackageNamespace\(""\), )?"htmlText"(?:, \[.*\])?\)[ \t]*\r?\n', re.M),
}

def aplicar(ctx):
    root = ctx.root
    # 1) compilar el núcleo
    core = os.path.join(root, 'work', 'core'); os.makedirs(core, exist_ok=True)
    for f in os.listdir(core): os.remove(os.path.join(core, f))
    java = os.path.join(root, 'tools', 'jre', 'jdk-21.0.12.1+1-jre', 'bin', 'java.exe')
    flex = os.path.join(root, 'tools', 'flex')
    # ENTREGA: las órdenes de laboratorio (Dev, jm_cmd.txt, dev.txt) NO se compilan: ni forzar pantallas ni tocar datos.
    src = os.path.join(root, 'src', 'core')
    if not ctx.lab:
        import shutil
        src = os.path.join(root, 'work', 'core_src_entrega'); shutil.rmtree(src, ignore_errors=True)
        shutil.copytree(os.path.join(root, 'src', 'core'), src)
        with open(os.path.join(src, 'jm', 'Dev.as'), 'w', encoding='utf-8') as f:
            f.write(chr(10).join(['package jm', '{', '   /** Entrega: sin ordenes de laboratorio. */', '   public class Dev', '   {',
                                  '      public static function run(p:Array):void {}', '   }', '}', '']))
        jm = open(os.path.join(src, 'jm', 'JM.as'), encoding='utf-8').read()
        old = 'dev = root.resolvePath("dev.txt").exists;'
        if jm.count(old) != 1: raise SystemExit('10_nucleo: no encuentro la línea de dev.txt en JM.as')
        open(os.path.join(src, 'jm', 'JM.as'), 'w', encoding='utf-8').write(jm.replace(old, 'dev = false;'))
        xml = open(os.path.join(src, 'jm-config.xml'), encoding='utf-8').read().replace('../../tools/flex', os.path.join(root, 'tools', 'flex').replace(os.sep, '/'))
        open(os.path.join(src, 'jm-config.xml'), 'w', encoding='utf-8').write(xml)
    r = subprocess.run([java, '-Dsun.io.useCanonCaches=false', '-Xmx1g', '-jar', os.path.join(flex, 'lib', 'mxmlc.jar'),
                        '+flexlib=' + os.path.join(flex, 'frameworks'), '-load-config=' + os.path.join(src, 'jm-config.xml'),
                        '-output', os.path.join(core, 'JMCore.swf'), os.path.join(src, 'JMCore.as')],
                       capture_output=True, text=True, errors='replace')
    abc = os.path.join(core, 'JMCore-0.abc')
    if os.path.isfile(os.path.join(core, 'JMCore.swf')):
        subprocess.run([os.path.join(root, 'tools', 'rabcdasm', 'abcexport.exe'), os.path.join(core, 'JMCore.swf')])
    if r.returncode != 0 or not os.path.isfile(abc):
        print(r.stdout, r.stderr); raise SystemExit('no compila el núcleo')
    if 'Warning' in r.stderr or 'Advertencia' in r.stderr: print(r.stderr)
    ctx.extra_abc.append(('jm/JMCore', abc))

    # 2) ganchos de texto en todas las clases del juego
    n = {'setText': 0, 'setHtml': 0}; files = 0
    for dp, dn, fn in os.walk(ctx.asm):
        for f in fn:
            if not f.endswith('.class.asasm'): continue
            p = os.path.join(dp, f)
            with open(p, encoding='utf-8', newline='') as fh: t = fh.read()
            t0 = t
            for name, rx in RX.items():
                t, k = rx.subn(lambda m, name=name: call_array(m.group(1), name), t); n[name] += k
            if t != t0:
                files += 1
                with open(p, 'w', encoding='utf-8', newline='') as fh: fh.write(t)
    print(f'   ganchos de texto: {n["setText"]} .text, {n["setHtml"]} .htmlText en {files} clases')
    ctx.log.append(('ganchos_texto', n))

    # 3) JM.init(this) al empezar GameModule.initGame
    def ini(body):
        head = '      getlocal0\n      pushscope\n'
        assert body.replace('\r', '').startswith(head), body[:80]
        nl = '\r\n' if '\r\n' in body[:40] else '\n'
        add = (f'      getlex              {JM}\n      getlocal0\n      callpropvoid        {VOID % "init"}, 1\n').replace('\n', nl)
        i = body.index('pushscope') + len('pushscope') + len(nl)
        return body[:i] + add + body[i:]
    ctx.edit_method('swordGame/core/GameModule.class.asasm', 'initGame', ini, add_stack=1)

    # 4) Options.build(this) al final de AppSettingsScreen.setupScreen
    def opt(body):
        i = body.rindex('returnvoid')
        i = body.rindex('\n', 0, i) + 1
        add = (f'      getlex              QName(PackageNamespace("jm"), "Options")\n      getlocal0\n'
               f'      callpropvoid        {VOID % "build"}, 1\n')
        return body[:i] + add + body[i:]
    ctx.edit_method('swordGame/screens/AppSettingsScreen.class.asasm', 'setupScreen', opt, add_stack=2)

    # 5) textos estáticos -> campos de texto (para poder traducirlos al vuelo)
    def estaticos(c):
        import sys; sys.path.insert(0, os.path.join(c.root, 'scripts')); import swfmod
        n, raros = swfmod.static_to_dynamic(c.swf, os.path.join(c.root, 'original', 'Data', 'assets', 'Main.assets'))
        print('   textos estáticos convertidos:', n, '| sin convertir:', len(raros))
    ctx.post_swf.insert(0, estaticos)

    # 6) datos del núcleo
    ctx.extra_files['Data/mods/00_nucleo'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos')
