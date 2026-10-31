# 如何从源代码编译 Jacksmith 模组

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

本指南适用于想要**重新编译或检查**模组的人。**只想玩的话不需要：**从 [Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest) 下载 zip，解压后运行 `Instalar.bat`。

## 所需条件

- Windows 10/11 和 Steam 版《Jacksmith: Weapons and Warriors》（版本 18571048，v1.0.1）。
- [Git for Windows](https://git-scm.com/download/win)（附带用于输入命令的 **Git Bash**）。
- 其余全部由 **`PREPARAR TODO.bat`** 下载（第 2 步）。

## 1. 下载代码

放在 `C:\Mods\jacksmith`（部分脚本中写死了这个文件夹）。在 Git Bash 中：

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

没有 Git：点击绿色的 **Code → Download ZIP** 按钮，解压为 `C:\Mods\jacksmith`。

## 2. 一次性下载所有需要的东西

双击 **`PREPARAR TODO.bat`**。它会自动下载以下全部内容并校验每个文件的 SHA-256；已经正确的文件不会重复下载：

| 内容 | 来源 → 位置 |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. 复制游戏文件

绝不修改 Steam 文件夹：在副本上工作。把 `G` 改成你的游戏文件夹：

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. 反汇编游戏代码

用 RABCDAsm 把游戏的干净字节码提取到 `work/abc`：

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. 编译并组装模组

编译模组库（`src/core`），应用各个部件（`piezas/NN_*/pieza.py`）并生成补丁：

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. 结果

`out/dist/` 中的文件夹就是模组，与 Releases 中的 zip 相同：`parche/Main.jmpatch`（只有差异，不含游戏文件）、`parche/mods/*/lang/*.json` 中的翻译以及安装程序。`Instalar.bat` 会校验游戏的 SHA-256，先备份再应用补丁；`Desinstalar.bat` 可恢复原样。
