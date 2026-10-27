#!/bin/bash
# Arma la entrega: build limpio (sin pieza de laboratorio) + parche + instalador -> out/dist/  y  el zip.
# Uso: scripts/make_dist.sh <versión>     p. ej. scripts/make_dist.sh 1.0.0
set -e
D=/c/Mods/jacksmith; V=${1:-1.0.0}
cd $D && python scripts/build.py 2>&1 | grep -v Warning | tail -3 && python scripts/make_patch.py
rm -rf out/dist && mkdir -p "out/dist/Jacksmith - traducción múltiples idiomas/parche/mods" "out/dist/Jacksmith - traducción múltiples idiomas/herramientas"
X="out/dist/Jacksmith - traducción múltiples idiomas"
cp instalador/Instalar.bat instalador/Desinstalar.bat "$X/"
cp instalador/herramientas/jacksmith_mod.ps1 "$X/herramientas/"
cp out/parche/Main.jmpatch out/parche/parche.json "$X/parche/"
printf '%s' "$V" > "$X/parche/version.txt"
cp -r out/entrega/Data/mods/. "$X/parche/mods/"
cp instalador/LEEME.txt "$X/LEEME.txt"
cp /c/Mods/AVISO.txt "$X/AVISO.txt"
cp -r instalador/licencias "$X/licencias"
# comprobación: en el paquete no puede ir ningún archivo del juego
if find "$X" -iname "*.assets" -o -iname "*.swf" -o -iname "*.exe" -o -iname "*.dll" | grep -q .; then echo "ERROR: hay archivos del juego en la entrega"; exit 1; fi
find "$X" -type f | sed "s|$X/||" | sort
