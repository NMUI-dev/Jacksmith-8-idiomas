# -*- coding: utf-8 -*-
"""Genera el parche de entrega: diferencia entre el Main.assets ORIGINAL y el construido (out/entrega).

El parche NO contiene el juego: solo instrucciones «copia este tramo del original» + los bytes nuevos.
Trabaja sobre el SWF descomprimido. Formato de Main.jmpatch:
   "JMPATCH1"  y luego operaciones:  0x01 u32 desplazamiento u32 longitud  (copiar del original)
                                     0x02 u32 longitud + bytes             (insertar)
Uso: python scripts/make_patch.py [carpeta_build=out/entrega] [carpeta_salida=out/parche]
"""
import sys, os, json, zlib, struct, hashlib, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import swftool
B = 32

def body(path):
    d = open(path, 'rb').read()
    assert d[:3] == b'CWS', path
    return d[3], zlib.decompress(d[8:]), hashlib.sha256(d).hexdigest()

def main():
    build = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'entrega')
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'out', 'parche')
    orig_path = os.path.join(ROOT, 'original', 'Data', 'assets', 'Main.assets')
    new_path = os.path.join(build, 'Data', 'assets', 'Main.assets')
    ver, ob, osha = body(orig_path)
    nver, nb, _ = body(new_path)
    # índice de bloques del original
    idx = {}
    for o in range(0, len(ob) - B + 1, B):
        idx.setdefault(ob[o:o + B], o)
    ops = []; lit = bytearray(); copied = 0; inserted = 0
    def flush():
        nonlocal lit, inserted
        if lit:
            ops.append(b'\x02' + struct.pack('<I', len(lit)) + bytes(lit)); inserted += len(lit); lit = bytearray()
    p = 0; n = len(nb); exp = 0      # exp: desplazamiento esperado en el original si todo sigue igual
    while p < n:
        # atajo: sigue coincidiendo donde tocaba
        o = None
        if exp is not None and exp + B <= len(ob) and nb[p:p + B] == ob[exp:exp + B]: o = exp
        else:
            o = idx.get(nb[p:p + B]) if p + B <= n else None
        if o is None:
            lit.append(nb[p]); p += 1; continue
        # extender hacia atrás (dentro del literal pendiente) y hacia delante
        back = 0
        while back < len(lit) and o - back - 1 >= 0 and ob[o - back - 1] == lit[len(lit) - back - 1]: back += 1
        if back: del lit[len(lit) - back:]; o -= back; p -= back
        L = B + back
        step = 1 << 16
        while True:
            a = nb[p + L:p + L + step]; b = ob[o + L:o + L + step]
            if a and a == b: L += len(a); continue
            k = 0; m = min(len(a), len(b))
            while k < m and a[k] == b[k]: k += 1
            L += k; break
        flush()
        ops.append(b'\x01' + struct.pack('<II', o, L)); copied += L
        p += L; exp = o + L
    flush()
    patch = b'JMPATCH1' + b''.join(ops)
    # comprobación: aplicar
    res = bytearray(); q = 8
    while q < len(patch):
        t = patch[q]; q += 1
        if t == 1:
            o, L = struct.unpack_from('<II', patch, q); q += 8; res += ob[o:o + L]
        else:
            L = struct.unpack_from('<I', patch, q)[0]; q += 4; res += patch[q:q + L]; q += L
    assert bytes(res) == nb, 'el parche no reproduce el archivo'
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(out)
    open(os.path.join(out, 'Main.jmpatch'), 'wb').write(zlib.compress(patch, 9))
    meta = {
        'juego': 'Jacksmith: Weapons and Warriors', 'steam_appid': 3580580, 'version_juego': '1.0.1', 'compilacion_steam': '18571048',
        'archivo': 'Data/assets/Main.assets',
        'original_sha256': osha, 'original_cuerpo_sha256': hashlib.sha256(ob).hexdigest(), 'original_cuerpo_bytes': len(ob),
        'nuevo_cuerpo_sha256': hashlib.sha256(nb).hexdigest(), 'nuevo_cuerpo_bytes': len(nb), 'swf_version': nver,
        'copiado_bytes': copied, 'insertado_bytes': inserted,
    }
    json.dump(meta, open(os.path.join(out, 'parche.json'), 'w', encoding='utf-8'), indent=1)
    print('parche:', os.path.getsize(os.path.join(out, 'Main.jmpatch')), 'bytes comprimido;', len(ops), 'operaciones; copiado', copied, 'insertado', inserted)

if __name__ == '__main__': main()
