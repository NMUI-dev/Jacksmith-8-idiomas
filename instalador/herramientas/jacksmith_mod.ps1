param(
    [ValidateSet('instalar','desinstalar','estado')] [string]$Accion = 'instalar',
    [string]$Juego = '',
    [switch]$SinPausa
)
# Instalador del mod «Jacksmith - traducción múltiples idiomas + volumen por grupos».
# No contiene archivos del juego: aplica un parche al Main.assets de TU copia y guarda el original.
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$Aqui   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Raiz   = Split-Path -Parent $Aqui
$Parche = Join-Path $Raiz 'parche'
$Meta   = Get-Content (Join-Path $Parche 'parche.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$ModVersion = (Get-Content (Join-Path $Parche 'version.txt') -Raw -Encoding UTF8).Trim()
$CarpetasMod = @('00_nucleo','20_volumen','30_espanol','31_idiomas')
$NombreRespaldo = '_respaldo_mod_jacksmith'

Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.IO.Compression;
using System.Security.Cryptography;
public static class JmSwf {
    public static byte[] Inflate(byte[] zlib, int start) {
        using (var ms = new MemoryStream(zlib, start + 2, zlib.Length - start - 2))
        using (var ds = new DeflateStream(ms, CompressionMode.Decompress))
        using (var o = new MemoryStream()) { ds.CopyTo(o); return o.ToArray(); }
    }
    public static byte[] Deflate(byte[] raw) {
        using (var o = new MemoryStream()) {
            o.WriteByte(0x78); o.WriteByte(0x9C);
            using (var ds = new DeflateStream(o, CompressionLevel.Optimal, true)) { ds.Write(raw, 0, raw.Length); }
            uint a = 1, b = 0;
            for (int i = 0; i < raw.Length; i++) { a = (a + raw[i]) % 65521; b = (b + a) % 65521; }
            uint ad = (b << 16) | a;
            o.WriteByte((byte)(ad >> 24)); o.WriteByte((byte)(ad >> 16)); o.WriteByte((byte)(ad >> 8)); o.WriteByte((byte)ad);
            return o.ToArray();
        }
    }
    public static string Sha(byte[] d) {
        using (var s = SHA256.Create()) { return BitConverter.ToString(s.ComputeHash(d)).Replace("-", "").ToLowerInvariant(); }
    }
    // Cuerpo descomprimido de un SWF comprimido (CWS)
    public static byte[] Body(byte[] swf) {
        if (swf.Length < 8 || swf[0] != (byte)'C' || swf[1] != (byte)'W' || swf[2] != (byte)'S') throw new Exception("no es un SWF comprimido (CWS)");
        return Inflate(swf, 8);
    }
    public static byte[] Pack(byte[] body, byte version) {
        byte[] z = Deflate(body);
        byte[] o = new byte[8 + z.Length];
        o[0] = (byte)'C'; o[1] = (byte)'W'; o[2] = (byte)'S'; o[3] = version;
        uint len = (uint)(body.Length + 8);
        o[4] = (byte)len; o[5] = (byte)(len >> 8); o[6] = (byte)(len >> 16); o[7] = (byte)(len >> 24);
        Buffer.BlockCopy(z, 0, o, 8, z.Length);
        return o;
    }
    public static byte[] Apply(byte[] orig, byte[] patchZ) {
        byte[] p = Inflate(patchZ, 0);
        if (System.Text.Encoding.ASCII.GetString(p, 0, 8) != "JMPATCH1") throw new Exception("parche no reconocido");
        using (var o = new MemoryStream()) {
            int q = 8;
            while (q < p.Length) {
                byte t = p[q++];
                if (t == 1) { int off = BitConverter.ToInt32(p, q); int len = BitConverter.ToInt32(p, q + 4); q += 8; o.Write(orig, off, len); }
                else if (t == 2) { int len = BitConverter.ToInt32(p, q); q += 4; o.Write(p, q, len); q += len; }
                else throw new Exception("operación de parche desconocida");
            }
            return o.ToArray();
        }
    }
}
'@

function Fin([int]$codigo) {
    if (-not $SinPausa) { Write-Host ''; Read-Host 'Pulsa Intro para cerrar' | Out-Null }
    exit $codigo
}
function Mal([string]$m) { Write-Host ''; Write-Host "ERROR: $m" -ForegroundColor Red; Fin 1 }

function Buscar-Juego {
    $cands = @()
    foreach ($k in 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam','HKLM:\SOFTWARE\Valve\Steam','HKCU:\SOFTWARE\Valve\Steam') {
        try {
            $p = (Get-ItemProperty -Path $k -ErrorAction Stop)
            foreach ($n in 'InstallPath','SteamPath') { if ($p.$n) { $cands += ($p.$n -replace '/', '\') } }
        } catch {}
    }
    $libs = @()
    foreach ($s in ($cands | Select-Object -Unique)) {
        $libs += $s
        $vdf = Join-Path $s 'steamapps\libraryfolders.vdf'
        if (Test-Path $vdf) {
            foreach ($l in (Get-Content $vdf)) { if ($l -match '"path"\s+"(.+)"') { $libs += ($Matches[1] -replace '\\\\', '\') } }
        }
    }
    foreach ($l in ($libs | Select-Object -Unique)) {
        $g = Join-Path $l 'steamapps\common\Jacksmith Weapons and Warriors'
        if (Test-Path (Join-Path $g 'Data\assets\Main.assets')) { return $g }
    }
    return $null
}

Write-Host '=============================================================='
Write-Host " Jacksmith: Weapons and Warriors - traducción múltiples idiomas  (v$ModVersion)"
Write-Host '=============================================================='
if (-not $Juego) { $Juego = Buscar-Juego }
if (-not $Juego) {
    Write-Host 'No encuentro el juego en tus bibliotecas de Steam.'
    $Juego = (Read-Host 'Escribe (o arrastra aquí) la carpeta del juego').Trim('"').Trim()
}
$Main = Join-Path $Juego 'Data\assets\Main.assets'
if (-not (Test-Path $Main)) { Mal "En «$Juego» no está Data\assets\Main.assets. ¿Es la carpeta del juego?" }
Write-Host "Juego: $Juego"
$Resp = Join-Path $Juego $NombreRespaldo
$RespMain = Join-Path $Resp 'Data\assets\Main.assets'
$Manifiesto = Join-Path $Resp 'instalado.json'
if (Get-Process -Name 'Jacksmith' -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($Juego, [StringComparison]::OrdinalIgnoreCase) }) {
    Mal 'El juego está abierto. Ciérralo y vuelve a ejecutar.'
}

$bytes = [System.IO.File]::ReadAllBytes($Main)
$shaArchivo = [JmSwf]::Sha($bytes)
$cuerpo = [JmSwf]::Body($bytes)
$shaCuerpo = [JmSwf]::Sha($cuerpo)
$esOriginal = ($shaCuerpo -eq $Meta.original_cuerpo_sha256)
$esMod = ($shaCuerpo -eq $Meta.nuevo_cuerpo_sha256)

if ($Accion -eq 'estado') {
    if ($esOriginal) { Write-Host 'Estado: juego ORIGINAL (mod no instalado).' }
    elseif ($esMod) { Write-Host "Estado: mod v$ModVersion INSTALADO." }
    else { Write-Host 'Estado: Main.assets no es ni el original conocido ni este mod (otra versión del juego u otro mod).' }
    Fin 0
}

if ($Accion -eq 'instalar') {
    $origen = $null
    if ($esOriginal) { $origen = $cuerpo }
    elseif (Test-Path $RespMain) {
        # ya hay un mod puesto (este u otro anterior nuestro): se parte SIEMPRE del original guardado
        $rb = [JmSwf]::Body([System.IO.File]::ReadAllBytes($RespMain))
        if ([JmSwf]::Sha($rb) -ne $Meta.original_cuerpo_sha256) { Mal 'La copia de seguridad guardada no coincide con el original esperado. Usa en Steam «Verificar integridad de los archivos» y vuelve a instalar.' }
        $origen = $rb
        Write-Host 'Ya había un mod instalado: se reinstala partiendo del original guardado.'
    }
    else {
        Mal ("Tu Main.assets no es el de la versión $($Meta.version_juego) (compilación de Steam $($Meta.compilacion_steam)) para la que se hizo el mod.`n" +
             "No se ha cambiado nada. Si el juego se actualizó, hace falta una versión nueva del mod.")
    }
    Write-Host 'Aplicando el parche...'
    $nuevo = [JmSwf]::Apply($origen, [System.IO.File]::ReadAllBytes((Join-Path $Parche 'Main.jmpatch')))
    if ([JmSwf]::Sha($nuevo) -ne $Meta.nuevo_cuerpo_sha256) { Mal 'El resultado del parche no es el esperado. No se ha cambiado nada.' }
    # copia de seguridad del original (solo la primera vez)
    if (-not (Test-Path $RespMain)) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $RespMain) | Out-Null
        Copy-Item -LiteralPath $Main -Destination $RespMain
        Write-Host "Original guardado en: $RespMain"
    }
    $tmp = "$Main.jmtmp"
    [System.IO.File]::WriteAllBytes($tmp, [JmSwf]::Pack($nuevo, [byte]$Meta.swf_version))
    if ([JmSwf]::Sha([JmSwf]::Body([System.IO.File]::ReadAllBytes($tmp))) -ne $Meta.nuevo_cuerpo_sha256) { Remove-Item $tmp -Force; Mal 'No se pudo escribir bien el archivo nuevo. No se ha cambiado nada.' }
    Move-Item -LiteralPath $tmp -Destination $Main -Force
    # datos del mod
    $dst = Join-Path $Juego 'Data\mods'
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    foreach ($c in $CarpetasMod) {
        $d = Join-Path $dst $c
        if (Test-Path $d) { Remove-Item -LiteralPath $d -Recurse -Force }
        Copy-Item -LiteralPath (Join-Path $Parche "mods\$c") -Destination $d -Recurse
    }
    $info = [ordered]@{ mod = 'jacksmith-es'; version = $ModVersion; fecha = (Get-Date -Format 's'); juego = $Meta.version_juego
                        original_sha256 = $Meta.original_sha256; carpetas = $CarpetasMod }
    ($info | ConvertTo-Json) | Out-File -FilePath $Manifiesto -Encoding utf8
    Write-Host ''
    Write-Host 'LISTO: mod instalado. Abre el juego desde Steam como siempre.' -ForegroundColor Green
    Write-Host 'La primera vez te preguntará el idioma. Idioma y volúmenes: botón del engranaje (Ajustes).'
    Fin 0
}

if ($Accion -eq 'desinstalar') {
    if ($esOriginal) {
        Write-Host 'El juego ya tiene su Main.assets original.'
    }
    elseif (Test-Path $RespMain) {
        $rb = [System.IO.File]::ReadAllBytes($RespMain)
        if ([JmSwf]::Sha([JmSwf]::Body($rb)) -ne $Meta.original_cuerpo_sha256) { Mal 'La copia de seguridad no coincide con el original esperado; no la uso. Usa en Steam «Verificar integridad de los archivos».' }
        Copy-Item -LiteralPath $RespMain -Destination $Main -Force
        Write-Host 'Main.assets original restaurado.'
    }
    else { Mal 'No hay copia de seguridad del original. Usa en Steam: clic derecho en el juego > Propiedades > Archivos instalados > «Verificar integridad de los archivos».' }
    $dst = Join-Path $Juego 'Data\mods'
    foreach ($c in $CarpetasMod) { $d = Join-Path $dst $c; if (Test-Path $d) { Remove-Item -LiteralPath $d -Recurse -Force } }
    if ((Test-Path $dst) -and -not (Get-ChildItem -LiteralPath $dst -Force)) { Remove-Item -LiteralPath $dst -Force }
    if (Test-Path $Resp) { Remove-Item -LiteralPath $Resp -Recurse -Force }
    Write-Host ''
    Write-Host 'LISTO: mod quitado; el juego queda como el original.' -ForegroundColor Green
    Write-Host '(Tus partidas no se tocan. El ajuste de idioma/volumen del mod queda guardado por si lo reinstalas.)'
    Fin 0
}
