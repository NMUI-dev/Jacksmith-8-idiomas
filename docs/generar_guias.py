"""Genera docs/compilar/<idioma>.md: la guía para compilar el mod en los idiomas del mod (español, inglés y los 8
idiomas nuevos de la 1.1.0). Los comandos son los mismos en todas; solo cambia el texto.   python docs/generar_guias.py"""
import os

REL = "https://github.com/NMUI-dev/Jacksmith-8-idiomas/releases/latest"
GIT = "https://git-scm.com/download/win"
CMD_CLONE = """```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Jacksmith-8-idiomas.git jacksmith
cd jacksmith
```"""
CMD_GAME = """```bash
G="/c/Program Files (x86)/Steam/steamapps/common/Jacksmith Weapons and Warriors"
mkdir -p original && cp -r "$G/Data" "$G/META-INF" original/
```"""
CMD_ABC = """```bash
mkdir -p work/abc && cp original/Data/assets/Main.assets work/abc/Main.swf
tools/rabcdasm/abcexport.exe work/abc/Main.swf
tools/rabcdasm/rabcdasm.exe work/abc/Main-0.abc
```"""
CMD_BUILD = """```bash
bash scripts/compile_core.sh
bash scripts/make_dist.sh 1.1.0
```"""
TABLA = [("Python 3.12", "python.org / winget"),
         ("fonttools 4.66.1, skia-pathops 0.9.2, opencc 0.1.7, numpy, pillow", "PyPI → `tools/pydeps`"),
         ("RABCDAsm 1.18 (CyberShadow, GPL-3.0)", "GitHub → `tools/rabcdasm`"),
         ("Apache Flex SDK 4.16.1 + playerglobal.swc 32.0", "apache.org / Adobe → `tools/flex`"),
         ("Java 21 (Eclipse Temurin JRE 21.0.12.1+1)", "adoptium → `tools/jre`"),
         ("Alegreya Sans, Alegreya Sans SC, Archivo Black, Lilita One, Protest Strike, Noto Sans JP/SC/TC, Liberation Sans 2.1.5",
          "Google Fonts / GitHub → `tools/dl/fuentes`")]

T = {
"es": dict(nombre="Español", titulo="Cómo compilar el mod de Jacksmith desde el código",
    jugar=f"Esto es para quien quiera **rehacer o revisar** el mod. **Para jugar no hace falta:** descarga el zip de [Releases]({REL}), descomprímelo y abre `Instalar.bat`.",
    nec="Lo que necesitas", nec_l=["Windows 10/11 y *Jacksmith: Weapons and Warriors* de Steam (build 18571048, v1.0.1).",
        f"[Git para Windows]({GIT}) (trae **Git Bash**, donde se escriben los comandos).", "Todo lo demás lo baja **`PREPARAR TODO.bat`** (paso 2)."],
    p1="1. Descargar el código", p1t="Ponlo en `C:\\Mods\\jacksmith` (algunos scripts tienen esa carpeta escrita dentro). En Git Bash:",
    p1b="Sin Git: botón verde **Code → Download ZIP** y descomprímelo como `C:\\Mods\\jacksmith`.",
    p2="2. Descargar todo lo necesario de una vez", p2t="Doble clic en **`PREPARAR TODO.bat`**. Baja esto solo y comprueba la SHA-256 de cada archivo; lo que ya está bien no se vuelve a bajar:",
    col=("Qué", "De dónde → dónde"),
    p3="3. Copiar los archivos del juego", p3t="Nunca se toca la carpeta de Steam: se trabaja con una copia. Cambia `G` por la carpeta de tu juego:",
    p4="4. Desensamblar el código del juego", p4t="Saca el bytecode limpio del juego a `work/abc` con RABCDAsm:",
    p5="5. Compilar y armar el mod", p5t="Compila la biblioteca del mod (`src/core`), aplica las piezas (`piezas/NN_*/pieza.py`) y crea el parche:",
    p6="6. Resultado", p6t="La carpeta de `out/dist/` es el mod, igual que el zip de Releases: `parche/Main.jmpatch` (solo las diferencias, sin archivos del juego), las traducciones en `parche/mods/*/lang/*.json` y el instalador. `Instalar.bat` comprueba la SHA-256 del juego, guarda una copia y aplica el parche; `Desinstalar.bat` lo deja como estaba."),
"en": dict(nombre="English", titulo="How to build the Jacksmith mod from source",
    jugar=f"This is for people who want to **rebuild or check** the mod. **You do not need it to play:** download the zip from [Releases]({REL}), unzip it and run `Instalar.bat`.",
    nec="What you need", nec_l=["Windows 10/11 and *Jacksmith: Weapons and Warriors* from Steam (build 18571048, v1.0.1).",
        f"[Git for Windows]({GIT}) (it includes **Git Bash**, where you type the commands).", "Everything else is downloaded by **`PREPARAR TODO.bat`** (step 2)."],
    p1="1. Get the code", p1t="Put it in `C:\\Mods\\jacksmith` (a few scripts have that folder written inside). In Git Bash:",
    p1b="Without Git: green **Code → Download ZIP** button, and unzip it as `C:\\Mods\\jacksmith`.",
    p2="2. Download everything at once", p2t="Double-click **`PREPARAR TODO.bat`**. It downloads all this by itself and checks the SHA-256 of every file; whatever is already right is not downloaded again:",
    col=("What", "From → to"),
    p3="3. Copy the game files", p3t="The Steam folder is never touched: you work on a copy. Change `G` to your game folder:",
    p4="4. Disassemble the game code", p4t="Extract the game's clean bytecode to `work/abc` with RABCDAsm:",
    p5="5. Compile and build the mod", p5t="Compiles the mod library (`src/core`), applies the pieces (`piezas/NN_*/pieza.py`) and makes the patch:",
    p6="6. Result", p6t="The folder in `out/dist/` is the mod, the same as the Releases zip: `parche/Main.jmpatch` (only the differences, no game files), the translations in `parche/mods/*/lang/*.json` and the installer. `Instalar.bat` checks the game's SHA-256, backs it up and applies the patch; `Desinstalar.bat` puts it back."),
"it": dict(nombre="Italiano", titulo="Come compilare la mod di Jacksmith dal codice sorgente",
    jugar=f"Questa guida è per chi vuole **ricostruire o verificare** la mod. **Per giocare non serve:** scarica lo zip da [Releases]({REL}), estrailo e avvia `Instalar.bat`.",
    nec="Cosa ti serve", nec_l=["Windows 10/11 e *Jacksmith: Weapons and Warriors* di Steam (build 18571048, v1.0.1).",
        f"[Git per Windows]({GIT}) (include **Git Bash**, dove si scrivono i comandi).", "Tutto il resto lo scarica **`PREPARAR TODO.bat`** (passo 2)."],
    p1="1. Scaricare il codice", p1t="Mettilo in `C:\\Mods\\jacksmith` (alcuni script hanno questa cartella scritta dentro). In Git Bash:",
    p1b="Senza Git: pulsante verde **Code → Download ZIP** ed estrailo come `C:\\Mods\\jacksmith`.",
    p2="2. Scaricare tutto in una volta", p2t="Fai doppio clic su **`PREPARAR TODO.bat`**. Scarica tutto da solo e controlla lo SHA-256 di ogni file; ciò che è già a posto non viene riscaricato:",
    col=("Cosa", "Da dove → dove"),
    p3="3. Copiare i file del gioco", p3t="La cartella di Steam non viene mai toccata: si lavora su una copia. Sostituisci `G` con la cartella del tuo gioco:",
    p4="4. Disassemblare il codice del gioco", p4t="Estrai il bytecode pulito del gioco in `work/abc` con RABCDAsm:",
    p5="5. Compilare e assemblare la mod", p5t="Compila la libreria della mod (`src/core`), applica i pezzi (`piezas/NN_*/pieza.py`) e crea la patch:",
    p6="6. Risultato", p6t="La cartella in `out/dist/` è la mod, uguale allo zip di Releases: `parche/Main.jmpatch` (solo le differenze, nessun file del gioco), le traduzioni in `parche/mods/*/lang/*.json` e l'installer. `Instalar.bat` controlla lo SHA-256 del gioco, ne fa una copia e applica la patch; `Desinstalar.bat` lo riporta com'era."),
"pt-BR": dict(nombre="Português (Brasil)", titulo="Como compilar o mod de Jacksmith a partir do código",
    jugar=f"Isto é para quem quer **refazer ou conferir** o mod. **Para jogar não precisa:** baixe o zip em [Releases]({REL}), descompacte e abra `Instalar.bat`.",
    nec="O que você precisa", nec_l=["Windows 10/11 e *Jacksmith: Weapons and Warriors* da Steam (build 18571048, v1.0.1).",
        f"[Git para Windows]({GIT}) (vem com o **Git Bash**, onde se digitam os comandos).", "Todo o resto é baixado pelo **`PREPARAR TODO.bat`** (passo 2)."],
    p1="1. Baixar o código", p1t="Coloque em `C:\\Mods\\jacksmith` (alguns scripts têm essa pasta escrita dentro). No Git Bash:",
    p1b="Sem Git: botão verde **Code → Download ZIP** e descompacte como `C:\\Mods\\jacksmith`.",
    p2="2. Baixar tudo de uma vez", p2t="Clique duas vezes em **`PREPARAR TODO.bat`**. Ele baixa tudo sozinho e confere o SHA-256 de cada arquivo; o que já está certo não é baixado de novo:",
    col=("O quê", "De onde → para onde"),
    p3="3. Copiar os arquivos do jogo", p3t="A pasta da Steam nunca é alterada: trabalha-se com uma cópia. Troque `G` pela pasta do seu jogo:",
    p4="4. Desmontar o código do jogo", p4t="Extraia o bytecode limpo do jogo para `work/abc` com o RABCDAsm:",
    p5="5. Compilar e montar o mod", p5t="Compila a biblioteca do mod (`src/core`), aplica as peças (`piezas/NN_*/pieza.py`) e cria o patch:",
    p6="6. Resultado", p6t="A pasta em `out/dist/` é o mod, igual ao zip de Releases: `parche/Main.jmpatch` (só as diferenças, sem arquivos do jogo), as traduções em `parche/mods/*/lang/*.json` e o instalador. `Instalar.bat` confere o SHA-256 do jogo, faz uma cópia e aplica o patch; `Desinstalar.bat` deixa como estava."),
"fr": dict(nombre="Français", titulo="Comment compiler le mod de Jacksmith à partir du code source",
    jugar=f"Ce guide est pour ceux qui veulent **reconstruire ou vérifier** le mod. **Pour jouer, ce n'est pas nécessaire :** téléchargez le zip dans [Releases]({REL}), décompressez-le et lancez `Instalar.bat`.",
    nec="Ce qu'il faut", nec_l=["Windows 10/11 et *Jacksmith: Weapons and Warriors* sur Steam (build 18571048, v1.0.1).",
        f"[Git pour Windows]({GIT}) (avec **Git Bash**, où l'on tape les commandes).", "Tout le reste est téléchargé par **`PREPARAR TODO.bat`** (étape 2)."],
    p1="1. Télécharger le code", p1t="Placez-le dans `C:\\Mods\\jacksmith` (certains scripts contiennent ce dossier en dur). Dans Git Bash :",
    p1b="Sans Git : bouton vert **Code → Download ZIP**, puis décompressez-le en `C:\\Mods\\jacksmith`.",
    p2="2. Tout télécharger d'un coup", p2t="Double-cliquez sur **`PREPARAR TODO.bat`**. Il télécharge tout seul et vérifie le SHA-256 de chaque fichier ; ce qui est déjà correct n'est pas retéléchargé :",
    col=("Quoi", "D'où → où"),
    p3="3. Copier les fichiers du jeu", p3t="Le dossier Steam n'est jamais modifié : on travaille sur une copie. Remplacez `G` par le dossier de votre jeu :",
    p4="4. Désassembler le code du jeu", p4t="Extrayez le bytecode propre du jeu dans `work/abc` avec RABCDAsm :",
    p5="5. Compiler et assembler le mod", p5t="Compile la bibliothèque du mod (`src/core`), applique les pièces (`piezas/NN_*/pieza.py`) et crée le patch :",
    p6="6. Résultat", p6t="Le dossier dans `out/dist/` est le mod, identique au zip de Releases : `parche/Main.jmpatch` (seulement les différences, aucun fichier du jeu), les traductions dans `parche/mods/*/lang/*.json` et l'installateur. `Instalar.bat` vérifie le SHA-256 du jeu, en fait une copie et applique le patch ; `Desinstalar.bat` remet tout comme avant."),
"de": dict(nombre="Deutsch", titulo="So kompilierst du die Jacksmith-Mod aus dem Quellcode",
    jugar=f"Diese Anleitung ist für alle, die die Mod **neu bauen oder prüfen** wollen. **Zum Spielen brauchst du sie nicht:** Lade das Zip unter [Releases]({REL}) herunter, entpacke es und starte `Instalar.bat`.",
    nec="Was du brauchst", nec_l=["Windows 10/11 und *Jacksmith: Weapons and Warriors* von Steam (Build 18571048, v1.0.1).",
        f"[Git für Windows]({GIT}) (enthält **Git Bash**, in das die Befehle eingegeben werden).", "Alles andere lädt **`PREPARAR TODO.bat`** herunter (Schritt 2)."],
    p1="1. Code herunterladen", p1t="Lege ihn unter `C:\\Mods\\jacksmith` ab (einige Skripte haben diesen Ordner fest eingetragen). In Git Bash:",
    p1b="Ohne Git: grüner Button **Code → Download ZIP**, dann als `C:\\Mods\\jacksmith` entpacken.",
    p2="2. Alles auf einmal herunterladen", p2t="Doppelklicke auf **`PREPARAR TODO.bat`**. Es lädt alles selbst herunter und prüft die SHA-256 jeder Datei; was schon stimmt, wird nicht erneut geladen:",
    col=("Was", "Woher → wohin"),
    p3="3. Spieldateien kopieren", p3t="Der Steam-Ordner wird nie verändert: Gearbeitet wird mit einer Kopie. Ersetze `G` durch deinen Spielordner:",
    p4="4. Spielcode disassemblieren", p4t="Extrahiere den sauberen Bytecode des Spiels mit RABCDAsm nach `work/abc`:",
    p5="5. Mod kompilieren und bauen", p5t="Kompiliert die Mod-Bibliothek (`src/core`), wendet die Teile an (`piezas/NN_*/pieza.py`) und erstellt den Patch:",
    p6="6. Ergebnis", p6t="Der Ordner in `out/dist/` ist die Mod, genau wie das Zip unter Releases: `parche/Main.jmpatch` (nur die Unterschiede, keine Spieldateien), die Übersetzungen in `parche/mods/*/lang/*.json` und der Installer. `Instalar.bat` prüft die SHA-256 des Spiels, legt eine Sicherung an und wendet den Patch an; `Desinstalar.bat` stellt den Originalzustand wieder her."),
"ru": dict(nombre="Русский", titulo="Как собрать мод Jacksmith из исходного кода",
    jugar=f"Это руководство для тех, кто хочет **пересобрать или проверить** мод. **Для игры оно не нужно:** скачайте zip в [Releases]({REL}), распакуйте его и запустите `Instalar.bat`.",
    nec="Что понадобится", nec_l=["Windows 10/11 и *Jacksmith: Weapons and Warriors* из Steam (сборка 18571048, v1.0.1).",
        f"[Git для Windows]({GIT}) (в комплекте **Git Bash**, где вводятся команды).", "Всё остальное скачает **`PREPARAR TODO.bat`** (шаг 2)."],
    p1="1. Скачать код", p1t="Поместите его в `C:\\Mods\\jacksmith` (в некоторых скриптах эта папка прописана жёстко). В Git Bash:",
    p1b="Без Git: зелёная кнопка **Code → Download ZIP**, затем распакуйте как `C:\\Mods\\jacksmith`.",
    p2="2. Скачать всё сразу", p2t="Дважды щёлкните **`PREPARAR TODO.bat`**. Он сам всё скачает и проверит SHA-256 каждого файла; то, что уже в порядке, повторно не скачивается:",
    col=("Что", "Откуда → куда"),
    p3="3. Скопировать файлы игры", p3t="Папка Steam никогда не изменяется: работа идёт с копией. Замените `G` на папку вашей игры:",
    p4="4. Дизассемблировать код игры", p4t="Извлеките чистый байт-код игры в `work/abc` с помощью RABCDAsm:",
    p5="5. Скомпилировать и собрать мод", p5t="Компилирует библиотеку мода (`src/core`), применяет части (`piezas/NN_*/pieza.py`) и создаёт патч:",
    p6="6. Результат", p6t="Папка в `out/dist/` — это мод, такой же, как zip в Releases: `parche/Main.jmpatch` (только различия, без файлов игры), переводы в `parche/mods/*/lang/*.json` и установщик. `Instalar.bat` проверяет SHA-256 игры, делает резервную копию и применяет патч; `Desinstalar.bat` возвращает всё как было."),
"ja": dict(nombre="日本語", titulo="ソースコードから Jacksmith の MOD をビルドする方法",
    jugar=f"このガイドは MOD を**作り直したり確認したり**したい人向けです。**遊ぶだけなら不要です：**[Releases]({REL}) から zip をダウンロードして解凍し、`Instalar.bat` を実行してください。",
    nec="必要なもの", nec_l=["Windows 10/11 と Steam 版『Jacksmith: Weapons and Warriors』（ビルド 18571048、v1.0.1）。",
        f"[Git for Windows]({GIT})（コマンドを入力する **Git Bash** が付属）。", "それ以外はすべて **`PREPARAR TODO.bat`** がダウンロードします（手順 2）。"],
    p1="1. コードをダウンロード", p1t="`C:\\Mods\\jacksmith` に置いてください（一部のスクリプトにこのフォルダーが書き込まれています）。Git Bash で：",
    p1b="Git がない場合：緑の **Code → Download ZIP** ボタンを押し、`C:\\Mods\\jacksmith` として解凍します。",
    p2="2. 必要なものを一括ダウンロード", p2t="**`PREPARAR TODO.bat`** をダブルクリックします。すべて自動でダウンロードし、各ファイルの SHA-256 を確認します。すでに正しいものは再ダウンロードしません：",
    col=("内容", "入手元 → 保存先"),
    p3="3. ゲームファイルをコピー", p3t="Steam のフォルダーには一切手を加えず、コピーで作業します。`G` をあなたのゲームフォルダーに変えてください：",
    p4="4. ゲームのコードを逆アセンブル", p4t="RABCDAsm でゲームのクリーンなバイトコードを `work/abc` に取り出します：",
    p5="5. MOD をコンパイルして組み立てる", p5t="MOD のライブラリ（`src/core`）をコンパイルし、各パーツ（`piezas/NN_*/pieza.py`）を適用してパッチを作ります：",
    p6="6. 結果", p6t="`out/dist/` のフォルダーが MOD で、Releases の zip と同じです：`parche/Main.jmpatch`（差分のみ、ゲームファイルは含みません）、`parche/mods/*/lang/*.json` の翻訳、インストーラー。`Instalar.bat` はゲームの SHA-256 を確認し、バックアップを取ってからパッチを適用します。`Desinstalar.bat` で元に戻せます。"),
"zh-Hans": dict(nombre="简体中文", titulo="如何从源代码编译 Jacksmith 模组",
    jugar=f"本指南适用于想要**重新编译或检查**模组的人。**只想玩的话不需要：**从 [Releases]({REL}) 下载 zip，解压后运行 `Instalar.bat`。",
    nec="所需条件", nec_l=["Windows 10/11 和 Steam 版《Jacksmith: Weapons and Warriors》（版本 18571048，v1.0.1）。",
        f"[Git for Windows]({GIT})（附带用于输入命令的 **Git Bash**）。", "其余全部由 **`PREPARAR TODO.bat`** 下载（第 2 步）。"],
    p1="1. 下载代码", p1t="放在 `C:\\Mods\\jacksmith`（部分脚本中写死了这个文件夹）。在 Git Bash 中：",
    p1b="没有 Git：点击绿色的 **Code → Download ZIP** 按钮，解压为 `C:\\Mods\\jacksmith`。",
    p2="2. 一次性下载所有需要的东西", p2t="双击 **`PREPARAR TODO.bat`**。它会自动下载以下全部内容并校验每个文件的 SHA-256；已经正确的文件不会重复下载：",
    col=("内容", "来源 → 位置"),
    p3="3. 复制游戏文件", p3t="绝不修改 Steam 文件夹：在副本上工作。把 `G` 改成你的游戏文件夹：",
    p4="4. 反汇编游戏代码", p4t="用 RABCDAsm 把游戏的干净字节码提取到 `work/abc`：",
    p5="5. 编译并组装模组", p5t="编译模组库（`src/core`），应用各个部件（`piezas/NN_*/pieza.py`）并生成补丁：",
    p6="6. 结果", p6t="`out/dist/` 中的文件夹就是模组，与 Releases 中的 zip 相同：`parche/Main.jmpatch`（只有差异，不含游戏文件）、`parche/mods/*/lang/*.json` 中的翻译以及安装程序。`Instalar.bat` 会校验游戏的 SHA-256，先备份再应用补丁；`Desinstalar.bat` 可恢复原样。"),
"zh-Hant": dict(nombre="繁體中文", titulo="如何從原始碼編譯 Jacksmith 模組",
    jugar=f"本指南適用於想要**重新編譯或檢查**模組的人。**只想玩的話不需要：**從 [Releases]({REL}) 下載 zip，解壓縮後執行 `Instalar.bat`。",
    nec="所需條件", nec_l=["Windows 10/11 與 Steam 版《Jacksmith: Weapons and Warriors》（版本 18571048，v1.0.1）。",
        f"[Git for Windows]({GIT})（附帶用來輸入指令的 **Git Bash**）。", "其餘全部由 **`PREPARAR TODO.bat`** 下載（第 2 步）。"],
    p1="1. 下載程式碼", p1t="放在 `C:\\Mods\\jacksmith`（部分指令碼中寫死了這個資料夾）。在 Git Bash 中：",
    p1b="沒有 Git：按下綠色的 **Code → Download ZIP** 按鈕，解壓縮為 `C:\\Mods\\jacksmith`。",
    p2="2. 一次下載所有需要的東西", p2t="按兩下 **`PREPARAR TODO.bat`**。它會自動下載以下全部內容並驗證每個檔案的 SHA-256；已經正確的檔案不會重複下載：",
    col=("內容", "來源 → 位置"),
    p3="3. 複製遊戲檔案", p3t="絕不修改 Steam 資料夾：在副本上作業。把 `G` 改成你的遊戲資料夾：",
    p4="4. 反組譯遊戲程式碼", p4t="用 RABCDAsm 把遊戲的乾淨位元組碼取出到 `work/abc`：",
    p5="5. 編譯並組裝模組", p5t="編譯模組函式庫（`src/core`），套用各個部件（`piezas/NN_*/pieza.py`）並產生修補檔：",
    p6="6. 結果", p6t="`out/dist/` 中的資料夾就是模組，與 Releases 中的 zip 相同：`parche/Main.jmpatch`（只有差異，不含遊戲檔案）、`parche/mods/*/lang/*.json` 中的翻譯以及安裝程式。`Instalar.bat` 會驗證遊戲的 SHA-256，先備份再套用修補檔；`Desinstalar.bat` 可恢復原狀。"),
}
ORDEN = ["es", "en", "it", "pt-BR", "fr", "de", "ru", "ja", "zh-Hans", "zh-Hant"]

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "compilar")
os.makedirs(OUT, exist_ok=True)
otros = " · ".join(f"[{T[c]['nombre']}]({c}.md)" for c in ORDEN)
for c in ORDEN:
    d = T[c]
    tabla = f"| {d['col'][0]} | {d['col'][1]} |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a, b in TABLA)
    md = "\n\n".join([
        f"# {d['titulo']}", otros, d["jugar"],
        f"## {d['nec']}", "\n".join(f"- {x}" for x in d["nec_l"]),
        f"## {d['p1']}", d["p1t"], CMD_CLONE, d["p1b"],
        f"## {d['p2']}", d["p2t"], tabla,
        f"## {d['p3']}", d["p3t"], CMD_GAME,
        f"## {d['p4']}", d["p4t"], CMD_ABC,
        f"## {d['p5']}", d["p5t"], CMD_BUILD,
        f"## {d['p6']}", d["p6t"]]) + "\n"
    open(os.path.join(OUT, f"{c}.md"), "w", encoding="utf-8", newline="\n").write(md)
    print("escrito", c)
