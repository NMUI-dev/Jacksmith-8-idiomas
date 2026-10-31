# Comment compiler le mod de Jacksmith à partir du code source

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

Ce guide est pour ceux qui veulent **reconstruire ou vérifier** le mod. **Pour jouer, ce n'est pas nécessaire :** téléchargez le zip dans [Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest), décompressez-le et lancez `Instalar.bat`.

## Ce qu'il faut

- Windows 10/11 et *Jacksmith: Weapons and Warriors* sur Steam (build 18571048, v1.0.1).
- [Git pour Windows](https://git-scm.com/download/win) (avec **Git Bash**, où l'on tape les commandes).
- Tout le reste est téléchargé par **`PREPARAR TODO.bat`** (étape 2).

## 1. Télécharger le code

Placez-le dans `C:\Mods\jacksmith` (certains scripts contiennent ce dossier en dur). Dans Git Bash :

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

Sans Git : bouton vert **Code → Download ZIP**, puis décompressez-le en `C:\Mods\jacksmith`.

## 2. Tout télécharger d'un coup

Double-cliquez sur **`PREPARAR TODO.bat`**. Il télécharge tout seul et vérifie le SHA-256 de chaque fichier ; ce qui est déjà correct n'est pas retéléchargé :

| Quoi | D'où → où |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. Copier les fichiers du jeu

Le dossier Steam n'est jamais modifié : on travaille sur une copie. Remplacez `G` par le dossier de votre jeu :

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. Désassembler le code du jeu

Extrayez le bytecode propre du jeu dans `work/abc` avec RABCDAsm :

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. Compiler et assembler le mod

Compile la bibliothèque du mod (`src/core`), applique les pièces (`piezas/NN_*/pieza.py`) et crée le patch :

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. Résultat

Le dossier dans `out/dist/` est le mod, identique au zip de Releases : `parche/Main.jmpatch` (seulement les différences, aucun fichier du jeu), les traductions dans `parche/mods/*/lang/*.json` et l'installateur. `Instalar.bat` vérifie le SHA-256 du jeu, en fait une copie et applique le patch ; `Desinstalar.bat` remet tout comme avant.
