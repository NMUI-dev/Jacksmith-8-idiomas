# Descarga de una vez todo lo necesario para COMPILAR el mod (no para jugarlo: para jugar basta el zip de Releases).
# Downloads at once everything needed to BUILD the mod (not to play it: for that the Releases zip is enough).
# Lo arranca «PREPARAR TODO.bat». Solo baja de las páginas oficiales, comprueba la SHA-256 de cada archivo y no toca el juego.
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$repo = Split-Path -Parent $PSScriptRoot
$t = Join-Path $repo "tools"; $dl = Join-Path $t "dl"
New-Item -ItemType Directory -Force $dl | Out-Null

function Paso($s) { Write-Host ""; Write-Host "== $s" -ForegroundColor Cyan }
function Bajar($url, $destino, $sha) {
    # -LiteralPath: nombres con corchetes (NotoSans[wdth,wght].ttf) no son comodines / brackets are not wildcards
    $nombre = Split-Path -Leaf $destino
    if ((Test-Path -LiteralPath $destino) -and ((Get-FileHash -LiteralPath $destino -Algorithm SHA256).Hash -eq $sha)) { Write-Host "   ok: $nombre"; return $false }
    New-Item -ItemType Directory -Force (Split-Path $destino) | Out-Null
    Write-Host "   -> $nombre"
    $tmp = Join-Path (Split-Path $destino) "_descarga.tmp"
    Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing
    $got = (Get-FileHash -LiteralPath $tmp -Algorithm SHA256).Hash
    if ($got -ne $sha) { Remove-Item -LiteralPath $tmp -Force; throw "SHA-256 ${nombre}: $got (esperada / expected $sha)" }
    Move-Item -LiteralPath $tmp -Destination $destino -Force
    return $true
}
function Abrir($archivo, $carpeta) {          # zip, 7z o tar.gz con el tar.exe de Windows 10/11
    New-Item -ItemType Directory -Force $carpeta | Out-Null
    & "$env:SystemRoot\System32\tar.exe" -xf $archivo -C $carpeta
    if ($LASTEXITCODE -ne 0) { throw "No se pudo abrir / could not extract $archivo" }
}

Write-Host "PREPARAR TODO - Jacksmith (compilar / build)" -ForegroundColor Green
Write-Host "Repo: $repo"
if ($repo -ne "C:\Mods\jacksmith") { Write-Host "AVISO / NOTE: some scripts expect C:\Mods\jacksmith (see the build guide)." -ForegroundColor Yellow }

Paso "1/6 Python 3.12"
$py = $null
foreach ($c in @(@("py", "-3.12"), @("python"))) {
    try { $v = & $c[0] $c[1..9] -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null; if ($v -eq "3.12") { $py = $c; break } } catch {}
}
if (-not $py) {
    if ((Read-Host "   Python 3.12 no está / not found. ¿Instalar con winget? Install with winget? S/Y/N") -match "^[sSyY]") {
        winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements; $py = @("py", "-3.12")
    } else { throw "Python 3.12: https://www.python.org/downloads/" }
}

Paso "2/6 Python: fonttools, skia-pathops, opencc, numpy, pillow -> tools\pydeps"
& $py[0] $py[1..9] -m pip install --upgrade --target (Join-Path $t "pydeps") fonttools==4.66.1 skia-pathops==0.9.2 opencc-python-reimplemented==0.1.7 numpy==2.5.4 pillow==12.3.0
if ($LASTEXITCODE -ne 0) { throw "pip" }

Paso "3/6 RABCDAsm 1.18 (CyberShadow, GPL-3.0) -> tools\rabcdasm"
$f = Join-Path $dl "RABCDAsm_v1.18.7z"
if ((Bajar "https://github.com/CyberShadow/RABCDAsm/releases/download/1.18/RABCDAsm_v1.18.7z" $f "68F2A39B45BAFAB874BACAE7EC7B809E27EB6A14A2EC45C52C4305165D2308BF") -or -not (Test-Path "$t\rabcdasm\rabcasm.exe")) { Abrir $f "$t\rabcdasm" }

Paso "4/6 Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 -> tools\flex"
$f = Join-Path $dl "apache-flex-sdk-4.16.1-bin.zip"
if ((Bajar "https://archive.apache.org/dist/flex/4.16.1/binaries/apache-flex-sdk-4.16.1-bin.zip" $f "757AA19299C8A9C8AF0901C1AE35F97FA94B7AF0B0A9ABC2BAB04FE61D756E8B") -or -not (Test-Path "$t\flex\lib\mxmlc.jar")) { Abrir $f "$t\flex" }
$pg = Join-Path $dl "playerglobal32_0.swc"
[void](Bajar "https://fpdownload.macromedia.com/get/flashplayer/updaters/32/playerglobal32_0.swc" $pg "7D4D6168D27603CFB3B750302448E354E0BBC1BDD58F5D101C3DCF6891E9BB65")
New-Item -ItemType Directory -Force "$t\flex\frameworks\libs\player\32.0" | Out-Null
Copy-Item $pg "$t\flex\frameworks\libs\player\32.0\playerglobal.swc" -Force

Paso "5/6 Java 21 (Eclipse Temurin JRE 21.0.12.1+1) -> tools\jre"
$f = Join-Path $dl "jre21.zip"
if ((Bajar "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jre_x64_windows_hotspot_21.0.12.1_1.zip" $f "D35F31E712F0FCF6AC5A093EDC90204FBFF22F720BA3950BD09D331D5E621636") -or -not (Test-Path "$t\jre\jdk-21.0.12.1+1-jre\bin\java.exe")) { Abrir $f "$t\jre" }

Paso "6/6 Fuentes / fonts (Google Fonts, Liberation Sans 2.1.5) -> tools\dl\fuentes"
$fu = Join-Path $dl "fuentes"
$gf = "https://raw.githubusercontent.com/google/fonts/6c1dbe27dcf7d817d4b62cec033ba77fa8e2a5ec/ofl"
$sha = @{}
Get-Content (Join-Path $PSScriptRoot "fuentes.sha256") -Encoding UTF8 | ForEach-Object { $a = $_ -split "\s+\*?", 2; $sha[$a[1]] = $a[0].ToUpper() }
foreach ($n in $sha.Keys) {
    if ($n -eq "liberation.tar.gz") { continue }
    $dir = switch -regex ($n) { "^AlegreyaSansSC|OFL_AlegreyaSansSC" { "alegreyasanssc"; break } "^AlegreyaSans|OFL_AlegreyaSans" { "alegreyasans"; break }
        "^ArchivoBlack" { "archivoblack"; break } "^LilitaOne" { "lilitaone"; break } "^ProtestStrike" { "proteststrike"; break } "^NotoSansJP" { "notosansjp"; break }
        "^NotoSansSC" { "notosanssc"; break } "^NotoSansTC" { "notosanstc"; break } "^NotoSans" { "notosans"; break } }
    $remoto = if ($n -like "OFL_*") { "OFL.txt" } else { [Uri]::EscapeDataString($n) }
    [void](Bajar "$gf/$dir/$remoto" (Join-Path $fu $n) $sha[$n])
}
$f = Join-Path $fu "liberation.tar.gz"
if ((Bajar "https://github.com/liberationfonts/liberation-fonts/files/7261482/liberation-fonts-ttf-2.1.5.tar.gz" $f $sha["liberation.tar.gz"]) -or -not (Test-Path "$fu\liberation-fonts-ttf-2.1.5")) { Abrir $f $fu }

Write-Host ""
Write-Host "TODO LISTO / ALL DONE. Sigue la guía desde el paso 3 / continue the build guide at step 3 (docs/)." -ForegroundColor Green
