# Come compilare la mod di Jacksmith dal codice sorgente

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

Questa guida è per chi vuole **ricostruire o verificare** la mod. **Per giocare non serve:** scarica lo zip da [Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest), estrailo e avvia `Instalar.bat`.

## Cosa ti serve

- Windows 10/11 e *Jacksmith: Weapons and Warriors* di Steam (build 18571048, v1.0.1).
- [Git per Windows](https://git-scm.com/download/win) (include **Git Bash**, dove si scrivono i comandi).
- Tutto il resto lo scarica **`PREPARAR TODO.bat`** (passo 2).

## 1. Scaricare il codice

Mettilo in `C:\Mods\jacksmith` (alcuni script hanno questa cartella scritta dentro). In Git Bash:

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

Senza Git: pulsante verde **Code → Download ZIP** ed estrailo come `C:\Mods\jacksmith`.

## 2. Scaricare tutto in una volta

Fai doppio clic su **`PREPARAR TODO.bat`**. Scarica tutto da solo e controlla lo SHA-256 di ogni file; ciò che è già a posto non viene riscaricato:

| Cosa | Da dove → dove |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. Copiare i file del gioco

La cartella di Steam non viene mai toccata: si lavora su una copia. Sostituisci `G` con la cartella del tuo gioco:

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. Disassemblare il codice del gioco

Estrai il bytecode pulito del gioco in `work/abc` con RABCDAsm:

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. Compilare e assemblare la mod

Compila la libreria della mod (`src/core`), applica i pezzi (`piezas/NN_*/pieza.py`) e crea la patch:

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. Risultato

La cartella in `out/dist/` è la mod, uguale allo zip di Releases: `parche/Main.jmpatch` (solo le differenze, nessun file del gioco), le traduzioni in `parche/mods/*/lang/*.json` e l'installer. `Instalar.bat` controlla lo SHA-256 del gioco, ne fa una copia e applica la patch; `Desinstalar.bat` lo riporta com'era.
