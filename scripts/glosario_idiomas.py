# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Glosario FIJO de Jacksmith para los idiomas nuevos (escrito a mano, coherente con las
decisiones del español). traducir_idiomas.py manda con cada lote los términos que aparecen en él y el modelo debe
usarlos. Orden: it, pt, fr, de, ru, ja, zh_hans, zh_hant.
"""
C = ['it', 'pt', 'fr', 'de', 'ru', 'ja', 'zh_hans', 'zh_hant']
G = {
 # armas
 'Sword': ['spada', 'espada', 'épée', 'Schwert', 'меч', '剣', '剑', '劍'],
 'Longsword': ['spada lunga', 'espada longa', 'épée longue', 'Langschwert', 'длинный меч', 'ロングソード', '长剑', '長劍'],
 'Bow': ['arco', 'arco', 'arc', 'Bogen', 'лук', '弓', '弓', '弓'],
 'Axe': ['ascia', 'machado', 'hache', 'Axt', 'топор', '斧', '斧', '斧'],
 'Shield': ['scudo', 'escudo', 'bouclier', 'Schild', 'щит', '盾', '盾', '盾'],
 'Pike': ['lancia', 'lança', 'pique', 'Spieß', 'копьё', '槍', '长枪', '長槍'],
 'Mace': ['mazza', 'maça', 'masse', 'Keule', 'булава', 'メイス', '锤', '錘'],
 'Arrow': ['freccia', 'flecha', 'flèche', 'Pfeil', 'стрела', '矢', '箭', '箭'],
 'Cannonball': ['palla di cannone', 'bala de canhão', 'boulet de canon', 'Kanonenkugel', 'ядро', '砲弾', '炮弹', '砲彈'],
 'Cannon': ['cannone', 'canhão', 'canon', 'Kanone', 'пушка', '大砲', '大炮', '大砲'],
 'Weapon': ['arma', 'arma', 'arme', 'Waffe', 'оружие', '武器', '武器', '武器'],
 'Epic Weapon': ['arma epica', 'arma épica', 'arme épique', 'epische Waffe', 'эпическое оружие', '伝説の武器', '史诗武器', '史詩武器'],
 'Weapon Design': ['progetto d\'arma', 'projeto de arma', 'modèle d\'arme', 'Waffenentwurf', 'чертёж оружия', '武器デザイン', '武器设计图', '武器設計圖'],
 'Design': ['progetto', 'projeto', 'modèle', 'Entwurf', 'чертёж', 'デザイン', '设计图', '設計圖'],
 # piezas
 'Guard': ['guardia', 'guarda', 'garde', 'Parierstange', 'гарда', '鍔', '护手', '護手'],
 'Grip': ['impugnatura', 'empunhadura', 'poignée', 'Griff', 'рукоять', 'グリップ', '握把', '握把'],
 'Cap': ['pomello', 'pomo', 'pommeau', 'Knauf', 'навершие', '柄頭', '柄头', '柄頭'],
 'Pole': ['asta', 'haste', 'hampe', 'Stiel', 'древко', '柄', '长柄', '長柄'],
 'Fletching': ['impennaggio', 'penas', 'empennage', 'Befiederung', 'оперение', '矢羽根', '箭羽', '箭羽'],
 'Arrowhead': ['punta di freccia', 'ponta de flecha', 'pointe de flèche', 'Pfeilspitze', 'наконечник', '矢じり', '箭头', '箭頭'],
 'Crest': ['stemma', 'brasão', 'blason', 'Wappen', 'герб', '紋章', '纹章', '紋章'],
 'Paint': ['vernice', 'tinta', 'peinture', 'Farbe', 'краска', '塗料', '涂料', '塗料'],
 'Peg': ['chiodo', 'pino', 'clou', 'Dorn', 'шип', 'スパイク', '尖刺', '尖刺'],
 'Mold': ['stampo', 'molde', 'moule', 'Gussform', 'форма', '鋳型', '模具', '模具'],
 'Ore': ['minerale', 'minério', 'minerai', 'Erz', 'руда', '鉱石', '矿石', '礦石'],
 'Metal': ['metallo', 'metal', 'métal', 'Metall', 'металл', '金属', '金属', '金屬'],
 'Copper': ['rame', 'cobre', 'cuivre', 'Kupfer', 'медь', '銅', '铜', '銅'],
 'Bronze': ['bronzo', 'bronze', 'bronze', 'Bronze', 'бронза', 'ブロンズ', '青铜', '青銅'],
 'Iron': ['ferro', 'ferro', 'fer', 'Eisen', 'железо', '鉄', '铁', '鐵'],
 'Steel': ['acciaio', 'aço', 'acier', 'Stahl', 'сталь', '鋼', '钢', '鋼'],
 'Gold': ['oro', 'ouro', 'or', 'Gold', 'золото', '金', '金', '金'],
 'Silver': ['argento', 'prata', 'argent', 'Silber', 'серебро', '銀', '银', '銀'],
 'Crystal': ['cristallo', 'cristal', 'cristal', 'Kristall', 'кристалл', 'クリスタル', '水晶', '水晶'],
 # fases y estadísticas
 'Forging': ['forgiatura', 'forja', 'forge', 'Schmieden', 'ковка', '鍛造', '锻造', '鍛造'],
 'Hammering': ['martellatura', 'martelagem', 'martelage', 'Hämmern', 'чеканка', '打ち込み', '锤炼', '錘鍊'],
 'Handle': ['impugnatura', 'cabo', 'manche', 'Griffstück', 'рукоять', '柄', '柄', '柄'],
 'Construction': ['costruzione', 'construção', 'construction', 'Bau', 'сборка', '組み立て', '组装', '組裝'],
 'Stretching': ['tensione', 'tensão', 'tension', 'Spannen', 'натяжение', '弦張り', '拉弦', '拉弦'],
 'Painting': ['pittura', 'pintura', 'peinture', 'Bemalen', 'покраска', '塗装', '涂装', '塗裝'],
 'Power': ['potenza', 'poder', 'puissance', 'Kraft', 'сила', 'パワー', '威力', '威力'],
 'Durability': ['resistenza', 'durabilidade', 'durabilité', 'Haltbarkeit', 'прочность', '耐久力', '耐久度', '耐久度'],
 'Luck': ['fortuna', 'sorte', 'chance', 'Glück', 'удача', '運', '幸运', '幸運'],
 'Element Boost': ['potenziamento elementale', 'bônus elemental', 'bonus élémentaire', 'Elementbonus', 'стихийное усиление', '属性ブースト', '元素强化', '元素強化'],
 'Boost': ['potenziamento', 'bônus', 'bonus', 'Bonus', 'усиление', 'ブースト', '强化', '強化'],
 'Loot': ['bottino', 'espólio', 'butin', 'Beute', 'добыча', '戦利品', '战利品', '戰利品'],
 'Treasure': ['tesoro', 'tesouro', 'trésor', 'Schatz', 'сокровище', '宝物', '宝藏', '寶藏'],
 'Gem': ['gemma', 'gema', 'gemme', 'Edelstein', 'самоцвет', 'ジェム', '宝石', '寶石'],
 'Badge': ['distintivo', 'insígnia', 'badge', 'Abzeichen', 'значок', 'バッジ', '徽章', '徽章'],
 'Bestiary': ['bestiario', 'bestiário', 'bestiaire', 'Bestiarium', 'бестиарий', 'モンスター図鑑', '怪物图鉴', '怪物圖鑑'],
 'Scrap': ['smonta', 'descartar', 'démonter', 'verschrotten', 'разобрать', '解体', '拆解', '拆解'],
 'Bookmark': ['segna', 'marcar', 'marquer', 'markieren', 'отметить', 'ブックマーク', '标记', '標記'],
 'Crafting Station': ['postazione', 'estação de forja', 'poste de forge', 'Werkbank', 'станок', '作業台', '工作台', '工作台'],
 'Star Meter': ['contatore stelle', 'medidor de estrelas', 'jauge d\'étoiles', 'Sternanzeige', 'шкала звёзд', 'スターメーター', '星星计量条', '星星計量條'],
 'Bonus Meter': ['contatore bonus', 'medidor de bônus', 'jauge de bonus', 'Bonusanzeige', 'шкала бонуса', 'ボーナスメーター', '奖励计量条', '獎勵計量條'],
 'Repair Bomb': ['bomba di riparazione', 'bomba de reparo', 'bombe de réparation', 'Reparaturbombe', 'ремонтная бомба', '修理ボム', '修理炸弹', '修理炸彈'],
 'Booster Bomb': ['bomba potenziante', 'bomba de reforço', 'bombe de renfort', 'Verstärkerbombe', 'бомба-усилитель', 'ブースターボム', '增益炸弹', '增益炸彈'],
 'Fire Bomb': ['bomba di fuoco', 'bomba de fogo', 'bombe de feu', 'Feuerbombe', 'огненная бомба', 'ファイアボム', '火焰炸弹', '火焰炸彈'],
 'Ice Bomb': ['bomba di ghiaccio', 'bomba de gelo', 'bombe de glace', 'Eisbombe', 'ледяная бомба', 'アイスボム', '冰冻炸弹', '冰凍炸彈'],
 'Lightning Bomb': ['bomba fulmine', 'bomba elétrica', 'bombe électrique', 'Blitzbombe', 'молниевая бомба', 'サンダーボム', '闪电炸弹', '閃電炸彈'],
 'Soldier': ['soldato', 'soldado', 'soldat', 'Soldat', 'солдат', '兵士', '士兵', '士兵'],
 'Trail': ['sentiero', 'trilha', 'chemin', 'Pfad', 'тропа', '道', '道路', '道路'],
 'Workshop': ['officina', 'oficina', 'atelier', 'Werkstatt', 'мастерская', '工房', '工坊', '工坊'],
 'Shop': ['negozio', 'loja', 'boutique', 'Laden', 'магазин', 'ショップ', '商店', '商店'],
 'Order': ['ordine', 'pedido', 'commande', 'Auftrag', 'заказ', '注文', '订单', '訂單'],
 'Level': ['livello', 'nível', 'niveau', 'Stufe', 'уровень', 'レベル', '等级', '等級'],
 'Day': ['giorno', 'dia', 'jour', 'Tag', 'день', '日', '天', '天'],
 # elementos
 'Fire': ['fuoco', 'fogo', 'feu', 'Feuer', 'огонь', '炎', '火', '火'],
 'Water': ['acqua', 'água', 'eau', 'Wasser', 'вода', '水', '水', '水'],
 'Ice': ['ghiaccio', 'gelo', 'glace', 'Eis', 'лёд', '氷', '冰', '冰'],
 'Stone': ['pietra', 'pedra', 'pierre', 'Stein', 'камень', '岩', '岩石', '岩石'],
 'Wind': ['vento', 'vento', 'vent', 'Wind', 'ветер', '風', '风', '風'],
 'Lightning': ['fulmine', 'raio', 'foudre', 'Blitz', 'молния', '雷', '雷电', '雷電'],
 'Plant': ['pianta', 'planta', 'plante', 'Pflanze', 'растение', '草', '植物', '植物'],
 'Shadow': ['ombra', 'sombra', 'ombre', 'Schatten', 'тень', '闇', '暗影', '暗影'],
 # lugares (como el español: se traducen)
 'Lowlands': ['Bassopiano', 'Terras Baixas', 'Basses-Terres', 'Tiefland', 'Низины', '低地', '低地', '低地'],
 'Alpine Ridge': ['Cresta Alpina', 'Cordilheira Alpina', 'Crête Alpine', 'Alpenkamm', 'Альпийский хребет', 'アルプスの尾根', '高山山脊', '高山山脊'],
 'Boneyard Dunes': ['Dune delle Ossa', 'Dunas dos Ossos', 'Dunes d\'Ossements', 'Knochendünen', 'Костяные дюны', '骨の砂丘', '白骨沙丘', '白骨沙丘'],
 'Cinder Springs': ['Sorgenti di Cenere', 'Fontes de Cinzas', 'Sources de Cendre', 'Aschequellen', 'Пепельные источники', '灰の泉', '灰烬温泉', '灰燼溫泉'],
 'Evershade Forest': ['Foresta Ombrosa', 'Floresta Sombria', 'Forêt Ombreuse', 'Schattenwald', 'Сумрачный лес', '常影の森', '幽影森林', '幽影森林'],
 'Wormwood Hollow': ['Valle Amara', 'Vale Amargo', 'Val Amer', 'Wermutsenke', 'Полынная лощина', 'ニガヨモギの谷', '苦艾谷', '苦艾谷'],
 'Castle Ruins': ['Rovine del Castello', 'Ruínas do Castelo', 'Ruines du Château', 'Burgruine', 'Руины замка', '城跡', '城堡废墟', '城堡廢墟'],
 'Plumpfeather Castle': ['Castello Piumagrassa', 'Castelo Penagorda', 'Château Plumegrasse', 'Burg Dickfeder', 'замок Пухоперье', 'ふっくら羽根城', '丰羽城堡', '豐羽城堡'],
}

def para(lang, textos):
    """Términos del glosario que aparecen en `textos` -> líneas «inglés = traducción» para el idioma."""
    import re
    i = C.index(lang); todo = ' '.join(textos).lower(); out = []
    for en, tr in G.items():
        if re.search(r'\b' + re.escape(en.lower()) + r'(s|es)?\b', todo): out.append(f'{en} = {tr[i]}')
    return out
