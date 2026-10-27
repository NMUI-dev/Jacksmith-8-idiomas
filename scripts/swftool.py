# -*- coding: utf-8 -*-
"""Utilidades mínimas de SWF: leer etiquetas, listar fuentes, insertar etiquetas DoABC."""
import zlib, struct, sys

def load(path):
    d = open(path, 'rb').read()
    sig, ver = d[:3], d[3]
    body = zlib.decompress(d[8:]) if sig == b'CWS' else d[8:]
    nb = body[0] >> 3; hl = (5 + 4 * nb + 7) // 8 + 4
    return ver, body[:hl], body[hl:]

def save(path, ver, head, tags):
    body = head + tags
    open(path, 'wb').write(b'CWS' + bytes([ver]) + struct.pack('<I', len(body) + 8) + zlib.compress(body, 9))

def iter_tags(tags):
    p = 0
    while p < len(tags):
        h = struct.unpack_from('<H', tags, p)[0]; t = h >> 6; l = h & 63; q = p + 2
        if l == 63: l = struct.unpack_from('<I', tags, q)[0]; q += 4
        yield t, p, q, q + l
        p = q + l

def mk_tag(t, data):
    return struct.pack('<HI', (t << 6) | 63, len(data)) + data

def insert_abcs(swf, abcs):
    """Inserta cada (nombre, ruta.abc) como DoABC (carga diferida) justo ANTES del primer DoABC del juego."""
    ver, head, tags = load(swf)
    for t, p, q, e in iter_tags(tags):
        if t == 82: pos = p; break
    new = b''
    for name, path in abcs:
        new += mk_tag(82, struct.pack('<I', 1) + name.encode() + b'\0' + open(path, 'rb').read())
    save(swf, ver, head, tags[:pos] + new + tags[pos:])

def fonts(swf):
    ver, head, tags = load(swf); out = []
    for t, p, q, e in iter_tags(tags):
        if t != 75: continue
        d = tags[q:e]; fid = struct.unpack_from('<H', d, 0)[0]; fl = d[2]; nl = d[4]
        name = d[5:5 + nl].rstrip(b'\0').decode('utf-8', 'replace'); o = 5 + nl
        n = struct.unpack_from('<H', d, o)[0]; o += 2
        wide_off = fl & 8; wide_codes = fl & 4; has_layout = fl & 0x80
        if n == 0: out.append((fid, name, '', bool(has_layout))); continue
        base = o
        if wide_off: code_off = struct.unpack_from('<I', d, base + 4 * n)[0]
        else: code_off = struct.unpack_from('<H', d, base + 2 * n)[0]
        c = base + code_off
        codes = [struct.unpack_from('<H', d, c + 2 * i)[0] for i in range(n)] if wide_codes else list(d[c:c + n])
        out.append((fid, name, ''.join(map(chr, codes)), bool(has_layout)))
    return out

if __name__ == '__main__':
    need = 'áéíóúñüÁÉÍÓÚÑÜ¿¡'
    for fid, name, chars, lay in fonts(sys.argv[1]):
        miss = ''.join(c for c in need if c not in chars)
        print(fid, name, len(chars), 'layout' if lay else '-', 'FALTAN: ' + miss if miss else 'completa')
        if '-v' in sys.argv: print('   ', chars)
