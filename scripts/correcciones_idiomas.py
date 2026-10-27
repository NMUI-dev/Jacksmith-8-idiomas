# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Correcciones A MANO de Claude para los idiomas nuevos (ganan a la traducción de los agentes).
Escribe piezas/31_idiomas/fuente/<código>_extra.json.   uso: python scripts/correcciones_idiomas.py
Incluye: textos que el español deja igual que el inglés y por eso no entraron en la traducción automática («No», «Info»,
«Ultra»); huecos de iconos con los MISMOS espacios fijos que el español (13 dentro de «( )», 2 a cada lado de la «D»);
formas cortas donde la letra se encogía demasiado; términos que los agentes eligieron mal.
"""
import json, os
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = '\xa0'; G = '(' + N * 13 + ')'
K_GEMAS = 'Use the Gems you collect ( ) to buy\nweapon parts from Gander’s shop.'
K_SUERTE = 'Use weapon parts with a Luck Boost ( ), and\nenemies will have a chance to drop more loot and\nbetter metal ores!'
K_D = 'Press   D   to view Weapon Designs'
K_ICONO = "Any parts that are used in an Epic Weapon Design\nyou have collected, even if it isn't currently\nbookmarked, will also show this icon:"

C = {
 'it': {'No': 'No', 'Info': 'Info', 'Ultra': 'Ultra', 'Master:': 'Generale:', 'Quit App': 'Esci',
        K_GEMAS: f'Usa le Gemme che raccogli {G} per comprare componenti nel negozio di Gander.',
        K_SUERTE: f'Usa componenti con Fortuna {G} e i nemici potranno lasciare più bottino e minerali migliori.',
        K_D: f'Premi {N}{N}D {N}{N}per vedere i progetti', '20 Stretches': '20 tensioni', 'Grips': 'Manopole', 'Settings': 'Opzioni'},
 'pt': {'No': 'Não', 'Info': 'Info', 'Ultra': 'Ultra', 'Master:': 'Geral:', 'Quit App': 'Sair',
        K_GEMAS: f'Use as Gemas que você coleta {G} para comprar peças na loja do Gander.',
        K_SUERTE: f'Use peças com Sorte {G} e os inimigos poderão deixar mais espólio e minérios melhores.',
        K_D: f'Aperte {N}{N}D {N}{N}para ver os projetos', 'Grips': 'Punhos', 'Settings': 'Opções'},
 'fr': {'No': 'Non', 'Info': 'Infos', 'Ultra': 'Ultra', 'Master:': 'Général :', 'Quit App': 'Quitter',
        K_GEMAS: f'Utilise les Gemmes récoltées {G} pour acheter des pièces chez Gander.',
        K_SUERTE: f'Utilise des pièces avec Chance {G} et les ennemis pourront lâcher plus de butin et de meilleurs minerais.',
        K_D: f'Appuie sur {N}{N}D {N}{N}pour voir les modèles', '20 Stretches': '20 tensions'},
 'de': {'No': 'Nein', 'Info': 'Info', 'Ultra': 'Ultra', 'Master:': 'Gesamt:', 'Quit App': 'Beenden',
        'Interface:': 'Menüs:', 'Guards': 'Schutz', 'Settings': 'Optionen',
        K_GEMAS: f'Mit gesammelten Edelsteinen {G} kaufst du Teile in Ganders Laden.',
        K_SUERTE: f'Nutze Teile mit Glück {G}, dann lassen Feinde mehr Beute und bessere Erze fallen.',
        K_D: f'Drücke {N}{N}D {N}{N}für die Waffenentwürfe',
        K_ICONO: 'Teile aus einem gesammelten epischen\nWaffenentwurf zeigen auch ohne Markierung\ndieses Symbol:'},
 'ru': {'No': 'Нет', 'Info': 'Инфо', 'Ultra': 'Ультра', 'Master:': 'Общая:', 'Quit App': 'Выйти',
        K_GEMAS: f'Покупай детали в лавке Гандера за самоцветы {G}.',
        K_SUERTE: f'С деталями удачи {G} враги чаще роняют добычу и руду получше.',
        K_D: f'Нажми {N}{N}D {N}{N}, чтобы открыть чертежи'},
 'ja': {'No': 'いいえ', 'Info': '情報', 'Ultra': 'ウルトラ', 'Master:': '全体：', 'Quit App': '終了',
        K_GEMAS: f'集めたジェム{G}でガンダーのショップから部品を買おう。',
        K_SUERTE: f'運ブースト{G}付きの部品を使うと、敵が戦利品や良い鉱石を落としやすくなる！',
        K_D: f'{N}{N}D {N}{N}キーで武器デザインを見る'},
 'zh_hans': {'No': '否', 'Info': '信息', 'Ultra': '超高', 'Master:': '总音量：', 'Quit App': '退出',
        K_GEMAS: f'用收集到的宝石{G}在甘德的商店购买武器部件。',
        K_SUERTE: f'使用带幸运强化{G}的部件，敌人更容易掉落战利品和更好的矿石！',
        K_D: f'按 {N}{N}D {N}{N}查看武器设计图'},
 'zh_hant': {'No': '否', 'Info': '資訊', 'Ultra': '超高', 'Master:': '總音量：', 'Quit App': '退出',
        K_GEMAS: f'用收集到的寶石{G}在甘德的商店購買武器部件。',
        K_SUERTE: f'使用帶幸運強化{G}的部件，敵人更容易掉落戰利品和更好的礦石！',
        K_D: f'按 {N}{N}D {N}{N}查看武器設計圖'},
}
# SUSTITUCIONES dentro de las frases (fallos que se repiten: palabras del español que se colaron por la referencia,
# términos mal elegidos). Se aplican a la traducción de los agentes (<código>_textos.json) y el resultado va al _extra.
S = {
 'zh_hans': [('Jacksmith 的世界', '杰克史密斯的世界'), ('Jacksmith 喜欢', '杰克史密斯喜欢'), ('Jacksmith', '杰克史密斯'), ('Scout', '斯考特'),
        ('杜德利', '达德利'), ('Dudley', '达德利'), ('皇家 Plumpfeather 家族', '丰羽王室'), ('Plumpfeather', '丰羽'),
        ('Gander', '甘德'), ('大炮弹', '炮弹'), ('Flash 播放器', 'Flash Player'), ('杰克史密斯 (c)', 'Jacksmith (c)')],
 'zh_hant': [('型別', '類型'), ('連線', '連接'), ('Jacksmith 的世界', '傑克史密斯的世界'), ('Jacksmith 喜歡', '傑克史密斯喜歡'), ('Jacksmith', '傑克史密斯'), ('Scout', '斯考特'),
        ('杜德利', '達德利'), ('杜德里', '達德利'), ('Dudley', '達德利'), ('Plumpfeather', '豐羽'), ('Gander', '甘德'), ('大炮彈', '砲彈'),
        ('Flash 播放器', 'Flash Player'), ('傑克史密斯 (c)', 'Jacksmith (c)')],
 'ja': [('ダ Dudley', 'ダドリー'), ('Dudley', 'ダドリー'), ('リリリアナ', 'リリアナ'), ('Royal Plumpfeather家', 'ふっくら羽根王家'),
        ('キング・プラムフェザー', 'ふっくら羽根王'), ('Plumpfeather', 'ふっくら羽根'), ('Jacksmithと', 'ジャックスミスと'),
        ('Jacksmithは', 'ジャックスミスは'), ('Scout', 'スカウト'), ('ガース・ゴブリン', 'ガチョウ・ゴブリン')],
 'ru': [('́', ''), ('Jacksmith,', 'Джексмит,'), ('Jacksmith!', 'Джексмит!'), ('с Jacksmith', 'с Джексмитом'),
        ('Jacksmith любил', 'Джексмит любил'), ('Scout', 'Скаут'), ('Plumpfeather', 'Пухоперье'), ('Хильда', 'Хильдрид'),
        ('Дудли', 'Дадли'), ('ЭТУ ФАЙЛ', 'ЭТОТ ФАЙЛ'), ('Создать 10', 'Создай 10'), ('Чертёжи', 'Чертежи'),
        ('Уничтожьте', 'Уничтожь'), ('Покиньте', 'Покинь'), ('Соберите', 'Собери')],
 'de': [('Schloss Plumpfeather', 'Burg Dickfeder'), ('Familie Plumpfeather', 'Familie Dickfeder'), ('König Plumpfeather', 'König Dickfeder'),
        ('ist Ihnen sehr dankbar für Ihren Beitrag', 'ist dir sehr dankbar für deine Hilfe'), ('DIESE DATE ', 'DIESE DATEI '),
        ('Spieße-Typen', 'Spieß-Typen'), ('Schilde-Typen', 'Schild-Typen'), ('Finde einen Schriftrolle', 'Finde eine Schriftrolle'),
        ('Du musst ihm eine Waffe herstellen', 'Du musst ihm ein Schwert schmieden')],
 'fr': [('boules de canon', 'boulets de canon'), ('Plumpfeather', 'Plumegrasse'), ("N'oublie pas de moi", "Ne m'oublie pas"),
        ('meilleurs minerai ', 'meilleurs minerais '), ('martelagez', 'martelez'), ('"favorir"', '"marquer"'),
        ('favorisées', 'marquées'), ('modèles favoris', 'modèles marqués')],
 'pt': [('Cofres do Tesouro', 'Baús do Tesouro'), ('Cofre do Tesouro', 'Baú do Tesouro'), ('Plumpfeather', 'Penagorda'),
        ('Cajado do Fênix', 'Cajado da Fênix'), ('Crie 10 Machado', 'Crie 10 Machados')],
 'it': [('Fénix', 'Fenice'), ('Cofri del Tesoro', 'Forzieri del Tesoro'), ('Cofre del Tesoro', 'Forziere del Tesoro'),
        ('maza da battaglia', 'mazza da battaglia'), ('La falce', 'Il falcione'), ('Ascie', 'Asce'), ('ascie', 'asce'),
        ('lama e spiga', 'lama e punta'), ('Tira lentamente la leva', 'Tira lentamente la catena'),
        ('famiglia reale Plumpfeather', 'famiglia reale Piumagrassa'), ('Il re Plumpfeather', 'Il re Piumagrassa'),
        ('munizioni per cannone', 'palle di cannone')],
}
# frases enteras (además de C) por idioma
F = {
 'zh_hans': {'Build': '构建', '20 Stretches': '拉弦20次', 'Swings\nLeft': '剩余\n次数', 'Boss': '首领', 'Time': '次', 'Times': '次', 'Day:': '天数：', 'End of Day': '一天结束', 'XP to Next Level': '升级所需经验值', 'Journeyman': '熟练工', 'Yes': '是', 'Assembler': '组装工', 'Arms of Steel': '钢铁之臂', '+ 999 For all soldiers!': '所有士兵 +999！', 'Killed': '击败', 'Choose a Slot': '选择存档位', 'Defeated Dudley': '击败了达德利', '-Arrowhead #': '-箭头 #', '-Cap #': '-柄头 #', '-Crest #': '-纹章 #', '-Fletching #': '-箭羽 #', '-Grip #': '-握把 #', '-Guard #': '-护手 #', '-Paint #': '-涂料 #', '-Pole #': '-长柄 #'},
 'zh_hant': {'Build': '組建', '20 Stretches': '拉弦20次', 'Swings\nLeft': '剩餘\n次數', 'Boss': '首領', 'Time': '次', 'Times': '次', 'Day:': '天數：', 'End of Day': '一天結束', 'XP to Next Level': '升級所需經驗值', 'Journeyman': '熟練工', 'Yes': '是', 'Assembler': '組裝工', 'Arms of Steel': '鋼鐵之臂', '+ 999 For all soldiers!': '所有士兵 +999！', 'Killed': '擊敗', 'Choose a Slot': '選擇存檔位', 'Defeated Dudley': '擊敗了達德利', '-Arrowhead #': '-箭頭 #', '-Cap #': '-柄頭 #', '-Crest #': '-紋章 #', '-Fletching #': '-箭羽 #', '-Grip #': '-握把 #', '-Guard #': '-護手 #', '-Paint #': '-塗料 #', '-Pole #': '-長柄 #'},
 'ja': {'Build': 'ビルド', '20 Stretches': '弦張り20回', 'Unstoppable': '止められない！', 'Burning Longlegs': '燃える長脚',
        'Swings\nLeft': '残り\n打数', 'Time': '回', 'Times': '回', 'End of Day': '1日の終わり', 'Killed 99 times': '99回撃破',
        'Killed': '撃破', 'Journeyman': '職人', "You'll need to craft him a sword.": '彼のために剣を作ろう。', 'Smith': '鍛冶屋',
        'Stonemason': '石工', 'Swordsmith': '刀鍛冶', 'Lightsmith': '光の鍛冶屋', 'Sheepshearer': '羊毛刈り', 'Assembler': '組立職人',
        'Pine Recluse': 'マツグモ', 'Glacier Goat': '氷河ヤギ', 'Phoenix Hen': 'フェニックスめんどり', 'Nature vs. Nature': '自然対自然',
        '-Arrowhead #': '-矢じり #', '-Cap #': '-柄頭 #', '-Crest #': '-紋章 #', '-Fletching #': '-矢羽根 #', '-Grip #': '-グリップ #',
        '-Guard #': '-鍔 #', '-Paint #': '-塗料 #', '-Pole #': '-柄 #'},
 'ru': {'to change pages of weapon parts': 'чтобы листать страницы деталей оружия', 'Build': 'Build', '20 Stretches': '20 натяжений', 'Swings\nLeft': 'Осталось\nударов', 'ONE MOMENT...': 'СЕКУНДУ...', 'Full Screen:': 'Весь экран:', 'Sound FX': 'Звуки',
        'Time': 'раз', 'Times': 'раз', 'Killed 99 times': 'Побеждён 99 раз', 'Killed': 'Побеждён', 'Burning Longlegs': 'Огненный длинноног',
        'Axe Grinder': 'Точильщик топоров', 'Defeated Dudley': 'Дадли побеждён', 'Choose a Slot': 'Выбери слот',
        'Enter Your Name': 'Введи своё имя', 'Spike Design': 'Чертёж с шипами', 'Small Widescreen': 'Широкий (малый)',
        'Jumbo Classic': 'Огромный (классика)', 'Jumbo Widescreen': 'Огромный (широкий)', 'Large Classic': 'Большой (классика)',
        'Small Classic': 'Маленький (классика)', 'Attack 20 Lightning Enemies with Lightning-boosted weapons': 'Атакуй 20 врагов-молний оружием с усилением молнии',
        'Attack 20 Wind Enemies with Wind-boosted weapons': 'Атакуй 20 врагов-ветров оружием с усилением ветра',
        'Attack 30 Plant Enemies with Plant-boosted weapons': 'Атакуй 30 врагов-растений оружием с усилением растений',
        'Attack 30 Shadow Enemies with Shadow-boosted weapons': 'Атакуй 30 врагов-теней оружием с усилением тени',
        '-Arrowhead #': '-Наконечник #', '-Cap #': '-Навершие #', '-Crest #': '-Герб #', '-Fletching #': '-Оперение #',
        '-Grip #': '-Рукоять #', '-Guard #': '-Гарда #', '-Paint #': '-Краска #', '-Pole #': '-Древко #'},
 'de': {'to change pages of weapon parts': 'um zwischen den Seiten der Waffenteile zu wechseln', 'Build': 'Build', '20 Stretches': '20-mal gespannt', 'Swings\nLeft': 'Verbleibende\nSchläge', 'Time': 'Mal', 'Times': 'Mal',
        'Killed 99 times': '99 Mal besiegt', 'Killed': 'Besiegt', 'EASY-TO-DRAG': 'LEICHT ZU ZIEHEN', 'Spike Sharpener': 'Stachelschärfer',
        'Falchion': 'Falchion', 'Pine Recluse': 'Kiefernspinne', 'Expert Forger': 'Meisterschmied', 'Expert Handling': 'Meisterhafte Handhabung',
        'Check back later!': 'Schau später wieder vorbei!', 'Purchased!': 'Gekauft!', 'Spike Design': 'Stachel-Entwurf',
        '-Arrowhead #': '-Pfeilspitze #', '-Cap #': '-Knauf #', '-Crest #': '-Wappen #', '-Fletching #': '-Befiederung #',
        '-Grip #': '-Griff #', '-Guard #': '-Parierstange #', '-Paint #': '-Farbe #', '-Pole #': '-Stiel #'},
 'fr': {'Build': 'Build', 'Scrap': 'Démonter', 'Swordsmith': "Forgeron d'épées", 'Expert Forger': 'Forgeron expert',
        'Time': 'fois', 'Times': 'fois', 'Killed 99 times': 'Vaincu 99 fois', 'Killed': 'Vaincu',
        'New Enemy Approaching': 'Un nouvel ennemi approche', 'Burning Longlegs': 'Longues-Pattes ardent',
        'Full Screen:': 'Plein écran :', 'Getting Started': 'Premiers pas', 'ONE MOMENT...': 'UN INSTANT...',
        'Bombardier': 'Bombardier', 'Expert Handling': 'Maniement expert'},
 'pt': {'to change pages of weapon parts': 'para mudar as páginas das peças', 'Build': 'Build', '20 Stretches': '20 tensões', 'Burning Longlegs': 'Pernas-Longas em Chamas',
        'Choose a Slot': 'Escolha um espaço', 'Lightsmith': 'Ferreiro da Luz', 'Falchion': 'Falcião',
        'Swings\nLeft': 'Golpes\nrestantes', 'Journeyman': 'Oficial', 'Small Widescreen': 'Tela larga pequena',
        'Arrow Fletcher': 'Flecheiro', 'Killed': 'Derrotado'},
 'it': {'Build': 'Build', 'Getting Started': 'Primi passi', 'XP to Next Level': 'XP al prossimo livello',
        'Burning Longlegs': 'Gambelunghe infuocato', 'Time': 'volta', 'Times': 'volte', 'Choose a Slot': 'Scegli uno slot',
        'Stonemason': 'Scalpellino', 'Swordsmith': 'Spadaio', 'Small Widescreen': 'Panoramica piccola',
        '200 XP to Next Level': '200 XP al prossimo livello'},
}

if __name__ == '__main__':
    import re
    for code, d in C.items():
        out = dict(d); out.update(F.get(code, {}))
        ruta = os.path.join(RAIZ, 'piezas', '31_idiomas', 'fuente', f'{code}_textos.json')
        tr = json.load(open(ruta, encoding='utf-8')) if os.path.exists(ruta) else {}
        for en, v in tr.items():
            v2 = out.get(en, v)
            for a, b in S.get(code, []): v2 = v2.replace(a, b)
            if v2 != v and en not in out: out[en] = v2
            elif en in out:
                for a, b in S.get(code, []): out[en] = out[en].replace(a, b)
        json.dump(out, open(os.path.join(RAIZ, 'piezas', '31_idiomas', 'fuente', f'{code}_extra.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    print('ok', {c: len(json.load(open(os.path.join(RAIZ, 'piezas', '31_idiomas', 'fuente', f'{c}_extra.json'), encoding='utf-8'))) for c in C})
