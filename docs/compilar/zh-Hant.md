# 如何從原始碼編譯 Jacksmith 模組

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

本指南適用於想要**重新編譯或檢查**模組的人。**只想玩的話不需要：**從 [Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest) 下載 zip，解壓縮後執行 `Instalar.bat`。

## 所需條件

- Windows 10/11 與 Steam 版《Jacksmith: Weapons and Warriors》（版本 18571048，v1.0.1）。
- [Git for Windows](https://git-scm.com/download/win)（附帶用來輸入指令的 **Git Bash**）。
- 其餘全部由 **`PREPARAR TODO.bat`** 下載（第 2 步）。

## 1. 下載程式碼

放在 `C:\Mods\jacksmith`（部分指令碼中寫死了這個資料夾）。在 Git Bash 中：

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

沒有 Git：按下綠色的 **Code → Download ZIP** 按鈕，解壓縮為 `C:\Mods\jacksmith`。

## 2. 一次下載所有需要的東西

按兩下 **`PREPARAR TODO.bat`**。它會自動下載以下全部內容並驗證每個檔案的 SHA-256；已經正確的檔案不會重複下載：

| 內容 | 來源 → 位置 |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. 複製遊戲檔案

絕不修改 Steam 資料夾：在副本上作業。把 `G` 改成你的遊戲資料夾：

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. 反組譯遊戲程式碼

用 RABCDAsm 把遊戲的乾淨位元組碼取出到 `work/abc`：

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. 編譯並組裝模組

編譯模組函式庫（`src/core`），套用各個部件（`piezas/NN_*/pieza.py`）並產生修補檔：

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. 結果

`out/dist/` 中的資料夾就是模組，與 Releases 中的 zip 相同：`parche/Main.jmpatch`（只有差異，不含遊戲檔案）、`parche/mods/*/lang/*.json` 中的翻譯以及安裝程式。`Instalar.bat` 會驗證遊戲的 SHA-256，先備份再套用修補檔；`Desinstalar.bat` 可恢復原狀。
