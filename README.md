# Jacksmith: Weapons and Warriors — multi-language translation mod (source)

## Para jugar / To play

**No descargues el código (botón verde «Code»): no trae la traducción lista.** Descarga el zip de la última versión en **[Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest)** (`Jacksmith - traduccion multiples idiomas v1.1.0.zip`), descomprímelo en una carpeta, haz doble clic en **`Instalar.bat`** y sigue lo que diga la ventana. El instalador encuentra el juego de Steam solo y guarda una copia de los archivos originales para poder quitarla. Lee el `LEEME.txt` del zip.

*Do not download the source (green «Code» button): it does not contain the ready translation.* Get the zip from **[Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest)**, unzip it into a folder, double-click **`Instalar.bat`** and follow the window. The installer finds the Steam game by itself and backs up the original files so it can be removed.

The rest of this page is the source code, for people who want to rebuild or check the mod.

Source code for the fan-made translation mod of *Jacksmith: Weapons and Warriors* (Steam, PC, Adobe AIR):
Spanish, German, French, Italian, Portuguese, Russian, Japanese, Simplified and Traditional Chinese, plus a per-group
volume option. Release v1.1.0.

**This repository contains no game files** (no `Main.assets`, no disassembly of the game, no game art).
Everything here is our own code and translation data. To build the mod you need your own copy of the game.

## How the mod works

The whole game is one SWF (`Data/assets/Main.assets`). The mod adds a small ActionScript 3 library (`src/core`) and
changes a few calls in the game's own bytecode so every text goes through it (`JM.setText`), which then shows the
selected language from `Data/mods/*/lang/*.json`.

The release does **not** ship the modified `Main.assets` (that would redistribute the game). It ships:

- `parche/Main.jmpatch` — a binary diff made by `scripts/make_patch.py`: a list of "copy N bytes from the original at
  offset X" and "insert these new bytes" operations. The inserted bytes are the compiled code of `src/core` plus the
  bytecode edits made by `piezas/*/pieza.py`, all reproducible with the steps below. The patch works on the uncompressed SWF body;
  `parche/parche.json` holds the SHA-256 of the original body it applies to and of the expected result.
- `parche/mods/*/` — plain JSON: translations (`lang/*.json`), volume groups (`sonidos.json`), `mod.json`.
- `herramientas/jacksmith_mod.ps1` + `Instalar.bat` / `Desinstalar.bat` (in `instalador/` here) — the installer.
  It is PowerShell with a small inline C# class (`Add-Type`) only to inflate/deflate the SWF (zlib) and compute
  SHA-256 quickly. It finds the game through Steam's `libraryfolders.vdf`, checks the SHA-256 of your `Main.assets`,
  backs it up, applies the patch, checks the result's SHA-256, and copies `Data/mods`. Uninstall restores the backup.
  It downloads nothing and starts nothing. The `.bat` files run it with `-ExecutionPolicy Bypass` only so a
  double-click works on systems where unsigned scripts are blocked; you can read the whole script before running it.

## Repository layout

```
src/core/                 AS3 source of the mod library (JM.as, Options.as, LangPick.as, Dev.as, JMCore.as, jm-config.xml)
piezas/NN_name/pieza.py   build steps applied in order to the game's disassembled bytecode:
  10_nucleo               inserts the compiled library, redirects text assignments to JM.setText / JM.setHtml
  20_volumen              per-group volume (sound ids in datos/sonidos.json)
  30_espanol              Spanish table (fuente/es_textos.json + es_extra.json + es_patrones.json) and accented glyphs
  31_idiomas              the other 8 languages (fuente/<lang>_textos.json) and their glyphs
  40_rotulos              text drawn as vector shapes, redrawn per language (rotulos.json)
scripts/build.py          applies the pieces and reassembles -> out/entrega
scripts/make_patch.py     original vs. built Main.assets -> out/parche/Main.jmpatch + parche.json
scripts/make_dist.sh      build + patch + installer -> out/dist (refuses if any .assets/.swf/.exe/.dll would be shipped)
scripts/swftool.py, swfmod.py, swfshape.py   our SWF reader/writer (tags, fonts, shapes, static -> dynamic text)
scripts/*idiomas*.py, glosario_idiomas.py ... how the translations were produced and checked
instalador/               installer, readme and font licenses, as shipped
```

## Requirements

- Windows 10/11, *Jacksmith: Weapons and Warriors* from Steam (build 18571048, v1.0.1).
- Python 3.12 with `pip install fonttools skia-pathops opencc-python-reimplemented numpy pillow`
  (the scripts also look for them in `tools/pydeps`).
- Git Bash (for the `.sh` scripts).
- Third-party tools (not included, put them in `tools/`):
  - **RABCDAsm** 1.18 (CyberShadow, GPL-3.0) — `tools/rabcdasm/` (`abcexport`, `rabcdasm`, `rabcasm`, `abcreplace`)
    <https://github.com/CyberShadow/RABCDAsm>
  - **Apache Flex SDK** 4.16.1 (Apache-2.0) — `tools/flex/` <https://flex.apache.org/download-binaries.html>,
    with `playerglobal.swc` 32.0 in `tools/flex/frameworks/libs/player/32.0/`
  - **Java** 21 runtime (e.g. Eclipse Temurin JRE) — `tools/jre/jdk-21.0.12.1+1-jre/`
  - **JPEXS Free Flash Decompiler** 26.3.0 (GPL-3.0) — `tools/ffdec/` — only used by the research scripts that render
    shapes to PNG (`formas.py`, `rot_*.py`), not by the build.
  - Fonts (SIL OFL, licenses in `instalador/licencias/`) — `tools/dl/fuentes/`: Alegreya Sans, Alegreya Sans SC,
    Archivo Black, Lilita One, Protest Strike, Noto Sans / JP / SC / TC (<https://fonts.google.com>) and
    Liberation Sans 2.1.5 (<https://github.com/liberationfonts/liberation-fonts>).

## How to build

Clone to `C:\Mods\jacksmith` (a few scripts have that folder hard-coded) and run from there in Git Bash.

```bash
# 1. your original game files (never edit the Steam folder)
G="/d/SteamLibrary/steamapps/common/Jacksmith Weapons and Warriors"   # your install folder
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/

# 2. clean disassembly of the game's bytecode -> work/abc (RABCDAsm)
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf          # -> work/abc/Main-0.abc
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc         # -> work/abc/Main-0/

# 3. compile the mod library, build, make the patch and the release folder
bash scripts/compile_core.sh                            # src/core -> work/core/JMCore.swf (Flex mxmlc)
bash scripts/make_dist.sh 1.1.0                         # build.py + make_patch.py -> out/dist/
```

`build.py` copies `work/abc/Main-0`, runs each `piezas/NN_*/pieza.py` in order (each text substitution stops the build
if it does not find the exact code it expects), reassembles with `rabcasm` + `abcreplace`, and writes the modified
`Main.assets` and `Data/mods` to `out/entrega`. `make_patch.py` then diffs it against the original. Applying
`out/dist/.../parche/Main.jmpatch` to the original gives an uncompressed SWF body byte-identical to that of
`out/entrega/Data/assets/Main.assets` (both SHA-256 are in `parche.json`, and the installer checks them).

## Credits and licenses

- Our code and translation data: MIT (see `LICENSE`). The game and its assets belong to Flipline Studios; this is an
  unofficial fan mod and is not affiliated with them.
- RABCDAsm (GPL-3.0), Apache Flex SDK (Apache-2.0), JPEXS FFDec (GPL-3.0), fonts (SIL OFL) — their authors.
- Translations made with AI assistance (Claude by Anthropic, Google Gemini, free OpenRouter models, a local Gemma model)
  and reviewed.
