# Как собрать мод Jacksmith из исходного кода

[Español](es.md) · [English](en.md) · [Italiano](it.md) · [Português (Brasil)](pt-BR.md) · [Français](fr.md) · [Deutsch](de.md) · [Русский](ru.md) · [日本語](ja.md) · [简体中文](zh-Hans.md) · [繁體中文](zh-Hant.md)

Это руководство для тех, кто хочет **пересобрать или проверить** мод. **Для игры оно не нужно:** скачайте zip в [Releases](https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest), распакуйте его и запустите `Instalar.bat`.

## Что понадобится

- Windows 10/11 и *Jacksmith: Weapons and Warriors* из Steam (сборка 18571048, v1.0.1).
- [Git для Windows](https://git-scm.com/download/win) (в комплекте **Git Bash**, где вводятся команды).
- Всё остальное скачает **`PREPARAR TODO.bat`** (шаг 2).

## 1. Скачать код

Поместите его в `C:\Mods\jacksmith` (в некоторых скриптах эта папка прописана жёстко). В Git Bash:

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```

Без Git: зелёная кнопка **Code → Download ZIP**, затем распакуйте как `C:\Mods\jacksmith`.

## 2. Скачать всё сразу

Дважды щёлкните **`PREPARAR TODO.bat`**. Он сам всё скачает и проверит SHA-256 каждого файла; то, что уже в порядке, повторно не скачивается:

| Что | Откуда → куда |
|---|---|
| Python 3.12 | python.org / winget |
| fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow | PyPI → `tools/pydeps` |
| RABCDAsm 1.18 (CyberShadow, GPL-3.0) | GitHub → `tools/rabcdasm` |
| Apache Flex SDK 4.16.1 + playerglobal.swc 32.0 | apache.org / Adobe → `tools/flex` |
| Java 21 (Eclipse Temurin JRE 21.0.12.1+1) | adoptium → `tools/jre` |
| Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5 | Google Fonts / GitHub → `tools/dl/fuentes` |

## 3. Скопировать файлы игры

Папка Steam никогда не изменяется: работа идёт с копией. Замените `G` на папку вашей игры:

```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```

## 4. Дизассемблировать код игры

Извлеките чистый байт-код игры в `work/abc` с помощью RABCDAsm:

```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```

## 5. Скомпилировать и собрать мод

Компилирует библиотеку мода (`src/core`), применяет части (`piezas/NN_*/pieza.py`) и создаёт патч:

```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```

## 6. Результат

Папка в `out/dist/` — это мод, такой же, как zip в Releases: `parche/Main.jmpatch` (только различия, без файлов игры), переводы в `parche/mods/*/lang/*.json` и установщик. `Instalar.bat` проверяет SHA-256 игры, делает резервную копию и применяет патч; `Desinstalar.bat` возвращает всё как было.
