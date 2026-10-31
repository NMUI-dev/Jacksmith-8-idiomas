# So kompilierst du die Jacksmith-Mod aus dem Quellcode

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

Diese Anleitung ist für alle, die die Mod **neu bauen oder prüfen** wollen. **Zum Spielen brauchst du sie nicht:** Lade das Zip unter [Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest) herunter, entpacke es und starte `Instalar.bat`.

## Was du brauchst

- Windows 10/11 und *Jacksmith: Weapons and Warriors* von Steam (Build 18571048, v1.0.1).
- [Git für Windows](https://git-scm.com/download/win) (enthält **Git Bash**, in das die Befehle eingegeben werden).
- Alles andere lädt **`PREPARAR TODO.bat`** herunter (Schritt 2).

## 1. Code herunterladen

Lege ihn unter `C:\Mods\jacksmith` ab (einige Skripte haben diesen Ordner fest eingetragen). In Git Bash:

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

Ohne Git: grüner Button **Code → Download ZIP**, dann als `C:\Mods\jacksmith` entpacken.

## 2. Alles auf einmal herunterladen

Doppelklicke auf **`PREPARAR TODO.bat`**. Es lädt alles selbst herunter und prüft die SHA-256 jeder Datei; was schon stimmt, wird nicht erneut geladen:

| Was | Woher → wohin |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. Spieldateien kopieren

Der Steam-Ordner wird nie verändert: Gearbeitet wird mit einer Kopie. Ersetze `G` durch deinen Spielordner:

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. Spielcode disassemblieren

Extrahiere den sauberen Bytecode des Spiels mit RABCDAsm nach `work/abc`:

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. Mod kompilieren und bauen

Kompiliert die Mod-Bibliothek (`src/core`), wendet die Teile an (`piezas/NN_*/pieza.py`) und erstellt den Patch:

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. Ergebnis

Der Ordner in `out/dist/` ist die Mod, genau wie das Zip unter Releases: `parche/Main.jmpatch` (nur die Unterschiede, keine Spieldateien), die Übersetzungen in `parche/mods/*/lang/*.json` und der Installer. `Instalar.bat` prüft die SHA-256 des Spiels, legt eine Sicherung an und wendet den Patch an; `Desinstalar.bat` stellt den Originalzustand wieder her.
