# Cómo compilar el mod de Jacksmith desde el código

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

Esto es para quien quiera **rehacer o revisar** el mod. **Para jugar no hace falta:** descarga el zip de [Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest), descomprímelo y abre `Instalar.bat`.

## Lo que necesitas

- Windows 10/11 y *Jacksmith: Weapons and Warriors* de Steam (build 18571048, v1.0.1).
- [Git para Windows](https://git-scm.com/download/win) (trae **Git Bash**, donde se escriben los comandos).
- Todo lo demás lo baja **`PREPARAR TODO.bat`** (paso 2).

## 1. Descargar el código

Ponlo en `C:\Mods\jacksmith` (algunos scripts tienen esa carpeta escrita dentro). En Git Bash:

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

Sin Git: botón verde **Code → Download ZIP** y descomprímelo como `C:\Mods\jacksmith`.

## 2. Descargar todo lo necesario de una vez

Doble clic en **`PREPARAR TODO.bat`**. Baja esto solo y comprueba la SHA-256 de cada archivo; lo que ya está bien no se vuelve a bajar:

| Qué | De dónde → dónde |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. Copiar los archivos del juego

Nunca se toca la carpeta de Steam: se trabaja con una copia. Cambia `G` por la carpeta de tu juego:

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. Desensamblar el código del juego

Saca el bytecode limpio del juego a `work/abc` con RABCDAsm:

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. Compilar y armar el mod

Compila la biblioteca del mod (`src/core`), aplica las piezas (`piezas/NN_*/pieza.py`) y crea el parche:

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. Resultado

La carpeta de `out/dist/` es el mod, igual que el zip de Releases: `parche/Main.jmpatch` (solo las diferencias, sin archivos del juego), las traducciones en `parche/mods/*/lang/*.json` y el instalador. `Instalar.bat` comprueba la SHA-256 del juego, guarda una copia y aplica el parche; `Desinstalar.bat` lo deja como estaba.
