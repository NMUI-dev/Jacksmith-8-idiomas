# -*- coding: utf-8 -*-
"""Pieza 20 — VOLUMEN SEPARADO de música y efectos (usa jm.JM del núcleo).

 - SoundManager.playSound: la transformación pasa por JM.fx(st, esMusica) antes de sonar
   (efectos × JM.sfxGain; jingles de «playMusicClip» × JM.musicGain).
 - Pistas de música: el tope de volumen (maxVolume / 1) pasa a ser JM.musicGain en switchMusic, fadeMusic y
   unmuteMusic.
 - Sonidos en bucle con volumen propio (fuego, hervor, vertido, pintura, carreta): cada
   «canal.soundTransform = st» del juego (menos los de SoundManager) pasa por JM.setST.
"""
import os, re

JM = 'QName(PackageNamespace("jm"), "JM")'
def q(n): return 'QName(PackageNamespace(""), "%s")' % n
SM = 'swordGame/managers/SoundManager.class.asasm'
MAXV = '      getproperty         QName(PrivateNamespace(null, "swordGame.managers:SoundManager/instance"), "maxVolume")\n'
GAIN = f'      pop\n      getlex              {JM}\n      getproperty         {q("musicGain")}\n'
RX_ST = re.compile(r'^([ \t]+)setproperty\s+(?:Multiname|QName)\((?:PackageNamespace\(""\), )?"soundTransform"(?:, \[.*\])?\)[ \t]*\r?\n', re.M)

def aplicar(ctx):
    # playSound
    def ps(body):
        b = body.replace('\r\n', '\n')
        k = f'      callproperty        {q("play")}, 3\n'
        assert b.count(k) == 1
        add = (f'      getlex              {JM}\n      swap\n      getlocal            6\n      getlocal1\n'
               f'      callproperty        {q("fx")}, 3\n')
        post = (f'      getlex              {JM}\n      swap\n      getlocal1\n'
                f'      callproperty        {q("reg")}, 2\n')
        return b.replace(k, add + k + post)
    ctx.edit_method(SM, 'playSound', ps, add_stack=3)

    # tope de la música
    def cap(n):
        def f(body):
            b = body.replace('\r\n', '\n')
            assert b.count(MAXV) == n, (b.count(MAXV), n)
            return b.replace(MAXV, MAXV + GAIN)
        return f
    ctx.edit_method(SM, 'switchMusic', cap(1), add_stack=1)
    ctx.edit_method(SM, 'fadeMusic', cap(2), add_stack=1)

    def unmute(body):
        b = body.replace('\r\n', '\n')
        old = ('      pushbyte            1\n'
               '      constructprop       QName(PackageNamespace("flash.media"), "SoundTransform"), 1\n')
        assert b.count(old) == 1
        return b.replace(old, f'      getlex              {JM}\n      getproperty         {q("musicGain")}\n' + old.split('\n', 1)[1])
    ctx.edit_method(SM, 'unmuteMusic', unmute, add_stack=1)

    # sonidos en bucle
    n = 0
    for dp, dn, fn in os.walk(os.path.join(ctx.asm, 'swordGame')):
        for f in fn:
            if not f.endswith('.class.asasm') or f.startswith('SoundManager'): continue
            p = os.path.join(dp, f)
            with open(p, encoding='utf-8', newline='') as fh: t = fh.read()
            t2, k = RX_ST.subn(lambda m: (f'{m.group(1)}newarray            2\n{m.group(1)}getlex              {JM}\n'
                                          f'{m.group(1)}swap\n{m.group(1)}callpropvoid        {q("setST")}, 1\n'), t)
            if k:
                n += k
                with open(p, 'w', encoding='utf-8', newline='') as fh: fh.write(t2)
    print(f'   soundTransform enganchados: {n}')
    ctx.extra_files['Data/mods/20_volumen'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos')
