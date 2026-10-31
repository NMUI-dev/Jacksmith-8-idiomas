# ソースコードから Jacksmith の MOD をビルドする方法

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

このガイドは MOD を**作り直したり確認したり**したい人向けです。**遊ぶだけなら不要です：**[Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest) から zip をダウンロードして解凍し、`Instalar.bat` を実行してください。

## 必要なもの

- Windows 10/11 と Steam 版『Jacksmith: Weapons and Warriors』（ビルド 18571048、v1.0.1）。
- [Git for Windows](https://git-scm.com/download/win)（コマンドを入力する **Git Bash** が付属）。
- それ以外はすべて **`PREPARAR TODO.bat`** がダウンロードします（手順 2）。

## 1. コードをダウンロード

`C:\Mods\jacksmith` に置いてください（一部のスクリプトにこのフォルダーが書き込まれています）。Git Bash で：

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

Git がない場合：緑の **Code → Download ZIP** ボタンを押し、`C:\Mods\jacksmith` として解凍します。

## 2. 必要なものを一括ダウンロード

**`PREPARAR TODO.bat`** をダブルクリックします。すべて自動でダウンロードし、各ファイルの SHA-256 を確認します。すでに正しいものは再ダウンロードしません：

| 内容 | 入手元 → 保存先 |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. ゲームファイルをコピー

Steam のフォルダーには一切手を加えず、コピーで作業します。`G` をあなたのゲームフォルダーに変えてください：

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. ゲームのコードを逆アセンブル

RABCDAsm でゲームのクリーンなバイトコードを `work/abc` に取り出します：

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. MOD をコンパイルして組み立てる

MOD のライブラリ（`src/core`）をコンパイルし、各パーツ（`piezas/NN_*/pieza.py`）を適用してパッチを作ります：

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. 結果

`out/dist/` のフォルダーが MOD で、Releases の zip と同じです：`parche/Main.jmpatch`（差分のみ、ゲームファイルは含みません）、`parche/mods/*/lang/*.json` の翻訳、インストーラー。`Instalar.bat` はゲームの SHA-256 を確認し、バックアップを取ってからパッチを適用します。`Desinstalar.bat` で元に戻せます。
