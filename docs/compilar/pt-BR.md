# Como compilar o mod de Jacksmith a partir do código

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

Isto é para quem quer **refazer ou conferir** o mod. **Para jogar não precisa:** baixe o zip em [Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest), descompacte e abra `Instalar.bat`.

## O que você precisa

- Windows 10/11 e *Jacksmith: Weapons and Warriors* da Steam (build 18571048, v1.0.1).
- [Git para Windows](https://git-scm.com/download/win) (vem com o **Git Bash**, onde se digitam os comandos).
- Todo o resto é baixado pelo **`PREPARAR TODO.bat`** (passo 2).

## 1. Baixar o código

Coloque em `C:\Mods\jacksmith` (alguns scripts têm essa pasta escrita dentro). No Git Bash:

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

Sem Git: botão verde **Code → Download ZIP** e descompacte como `C:\Mods\jacksmith`.

## 2. Baixar tudo de uma vez

Clique duas vezes em **`PREPARAR TODO.bat`**. Ele baixa tudo sozinho e confere o SHA-256 de cada arquivo; o que já está certo não é baixado de novo:

| O quê | De onde → para onde |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. Copiar os arquivos do jogo

A pasta da Steam nunca é alterada: trabalha-se com uma cópia. Troque `G` pela pasta do seu jogo:

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. Desmontar o código do jogo

Extraia o bytecode limpo do jogo para `work/abc` com o RABCDAsm:

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. Compilar e montar o mod

Compila a biblioteca do mod (`src/core`), aplica as peças (`piezas/NN_*/pieza.py`) e cria o patch:

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. Resultado

A pasta em `out/dist/` é o mod, igual ao zip de Releases: `parche/Main.jmpatch` (só as diferenças, sem arquivos do jogo), as traduções em `parche/mods/*/lang/*.json` e o instalador. `Instalar.bat` confere o SHA-256 do jogo, faz uma cópia e aplica o patch; `Desinstalar.bat` deixa como estava.
