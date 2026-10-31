# How to build the Jacksmith mod from source

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

This is for people who want to **rebuild or check** the mod. **You do not need it to play:** download the zip from [Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest), unzip it and run `Instalar.bat`.

## What you need

- Windows 10/11 and *Jacksmith: Weapons and Warriors* from Steam (build 18571048, v1.0.1).
- [Git for Windows](https://git-scm.com/download/win) (it includes **Git Bash**, where you type the commands).
- Everything else is downloaded by **`PREPARAR TODO.bat`** (step 2).

## 1. Get the code

Put it in `C:\Mods\jacksmith` (a few scripts have that folder written inside). In Git Bash:

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

Without Git: green **Code → Download ZIP** button, and unzip it as `C:\Mods\jacksmith`.

## 2. Download everything at once

Double-click **`PREPARAR TODO.bat`**. It downloads all this by itself and checks the SHA-256 of every file; whatever is already right is not downloaded again:

| What | From → to |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. Copy the game files

The Steam folder is never touched: you work on a copy. Change `G` to your game folder:

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. Disassemble the game code

Extract the game's clean bytecode to `work/abc` with RABCDAsm:

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. Compile and build the mod

Compiles the mod library (`src/core`), applies the pieces (`piezas/NN_*/pieza.py`) and makes the patch:

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. Result

The folder in `out/dist/` is the mod, the same as the Releases zip: `parche/Main.jmpatch` (only the differences, no game files), the translations in `parche/mods/*/lang/*.json` and the installer. `Instalar.bat` checks the game's SHA-256, backs it up and applies the patch; `Desinstalar.bat` puts it back.
