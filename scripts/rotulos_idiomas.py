# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Traducciones (a mano) de los 51 rótulos dibujados para los idiomas nuevos: las añade como
claves <código> a cada entrada de piezas/40_rotulos/rotulos.json (la pieza 40 genera jm_<código>_N y JM.fixArt las
enseña). «|» = renglón. Mismo uso de mayúsculas que el original/el español.   uso: python scripts/rotulos_idiomas.py
"""
import json, os
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(RAIZ, 'piezas', '40_rotulos', 'rotulos.json')
C = ['it', 'pt', 'fr', 'de', 'ru', 'ja', 'zh_hans', 'zh_hant']
T = {   # inglés -> [it, pt, fr, de, ru, ja, zh_hans, zh_hant]
 'Skip': ['Salta', 'Pular', 'Passer', 'Weiter', 'Пропуск', 'スキップ', '跳过', '跳過'],
 'Craft': ['Forgia', 'Forjar', 'Forger', 'Schmieden', 'Ковать', '鍛造', '锻造', '鍛造'],
 'Order': ['Ordine', 'Pedido', 'Commande', 'Auftrag', 'Заказ', '注文', '订单', '訂單'],
 'You Own': ['Hai', 'Você tem', 'Tu as', 'Du hast', 'У тебя', '所持', '拥有', '擁有'],
 'Shop': ['Negozio', 'Loja', 'Boutique', 'Laden', 'Магазин', 'ショップ', '商店', '商店'],
 'SWORD': ['SPADA', 'ESPADA', 'ÉPÉE', 'SCHWERT', 'МЕЧ', '剣', '剑', '劍'],
 'BOW': ['ARCO', 'ARCO', 'ARC', 'BOGEN', 'ЛУК', '弓', '弓', '弓'],
 'SHIELD': ['SCUDO', 'ESCUDO', 'BOUCLIER', 'SCHILD', 'ЩИТ', '盾', '盾', '盾'],
 'AXE': ['ASCIA', 'MACHADO', 'HACHE', 'AXT', 'ТОПОР', '斧', '斧', '斧'],
 'PIKE': ['PICCA', 'LANÇA', 'PIQUE', 'SPIESS', 'КОПЬЁ', '槍', '长枪', '長槍'],
 'MACE': ['MAZZA', 'MAÇA', 'MASSE', 'KEULE', 'БУЛАВА', 'メイス', '锤', '錘'],
 'New Cannonball': ['Nuova Palla di Cannone', 'Nova Bala de Canhão', 'Nouveau Boulet', 'Neue Kanonenkugel', 'Новое ядро',
                    '新しい砲弾', '新炮弹', '新砲彈'],
 'New Weapon': ['Nuova Arma', 'Nova Arma', 'Nouvelle Arme', 'Neue Waffe', 'Новое оружие', '新しい武器', '新武器', '新武器'],
 'Beware': ['Attenzione!', 'Cuidado!', 'Attention !', 'Vorsicht!', 'Осторожно!', '気をつけて！', '小心！', '小心！'],
 'New Shop Item': ['Nuovo nel Negozio', 'Novo na Loja', 'Nouveau en Boutique', 'Neu im Laden', 'Новинка в магазине',
                   'ショップに新商品', '商店新品', '商店新品'],
 'LeVeL': ['LiVeLLo', 'NíVeL', 'NiVeAu', 'StUfE', 'УрОвЕнЬ', 'レベル', '等级', '等級'],
 'AWESOME': ['FANTASTICO', 'INCRÍVEL', 'GÉNIAL', 'KLASSE', 'ПОТРЯСАЮЩЕ', '最高', '太棒了', '太棒了'],
 'GREAT': ['OTTIMO', 'ÓTIMO', 'SUPER', 'SUPER', 'ОТЛИЧНО', 'すごい', '很棒', '很棒'],
 'GOOD': ['BENE', 'BOM', 'BIEN', 'GUT', 'ХОРОШО', 'いいね', '不错', '不錯'],
 'PERFECT!': ['PERFETTO!', 'PERFEITO!', 'PARFAIT !', 'PERFEKT!', 'ИДЕАЛЬНО!', '完璧！', '完美！', '完美！'],
 'OKAY': ['DISCRETO', 'OK', 'PASSABLE', 'OKAY', 'НОРМАЛЬНО', 'まあまあ', '还行', '還行'],
 'HMM...': ['HMM...', 'HMM...', 'HMM...', 'HMM...', 'ХММ...', 'うーん…', '嗯……', '嗯……'],
 'TOO|BAD': ['CHE|PECCATO', 'QUE|PENA', 'PAS|TOP', 'SO|SCHADE', 'ОЧЕНЬ|ПЛОХО', 'ざん|ねん', '太|糟了', '太|糟了'],
 'Good!': ['Bene!', 'Bom!', 'Bien !', 'Gut!', 'Хорошо!', 'いいね！', '不错！', '不錯！'],
 'Great!': ['Ottimo!', 'Ótimo!', 'Super !', 'Super!', 'Отлично!', 'すごい！', '很棒！', '很棒！'],
 'MENU': ['MENU', 'MENU', 'MENU', 'MENÜ', 'МЕНЮ', 'メニュー', '菜单', '選單'],
 'SKIP': ['SALTA', 'PULAR', 'PASSER', 'WEITER', 'ПРОПУСК', 'スキップ', '跳过', '跳過'],
 'BACK': ['INDIETRO', 'VOLTAR', 'RETOUR', 'ZURÜCK', 'НАЗАД', '戻る', '返回', '返回'],
 'PULL': ['TIRA', 'PUXE', 'TIRE', 'ZIEH', 'ТЯНИ', '引く', '拉', '拉'],
 'HELP': ['AIUTO', 'AJUDA', 'AIDE', 'HILFE', 'ПОМОЩЬ', 'ヘルプ', '帮助', '說明'],
 'Designs': ['Progetti', 'Projetos', 'Modèles', 'Entwürfe', 'Чертежи', 'デザイン', '设计', '設計'],
 'Beasts': ['Bestie', 'Feras', 'Bêtes', 'Bestien', 'Звери', 'モンスター', '怪物', '怪物'],
 'Preparing for Battle!': ['Pronti alla Battaglia!', 'Preparando para a Batalha!', 'Préparation au Combat !',
                           'Bereit zur Schlacht!', 'Готовимся к битве!', '戦いの準備中！', '准备战斗！', '準備戰鬥！'],
 'PUT|AWAY': ['METTI|VIA', 'GUARDAR', 'RANGER', 'WEG|LEGEN', 'УБРАТЬ', 'しまう', '收起', '收起'],
 'NEW!': ['NUOVO!', 'NOVO!', 'NOUVEAU !', 'NEU!', 'НОВОЕ!', '新着！', '新品！', '新品！'],
 'Epic Weapon Designs': ['Progetti di Armi Epiche', 'Projetos de Armas Épicas', "Modèles d'Armes Épiques",
                         'Epische Waffenentwürfe', 'Чертежи эпического оружия', '伝説の武器デザイン', '史诗武器设计', '史詩武器設計'],
 'REWARD': ['RICOMPENSA', 'RECOMPENSA', 'RÉCOMPENSE', 'BELOHNUNG', 'НАГРАДА', '報酬', '奖励', '獎勵'],
 'OFF': ['NO', 'NÃO', 'NON', 'AUS', 'ВЫКЛ', 'オフ', '关', '關'],
 'ON': ['SÌ', 'SIM', 'OUI', 'AN', 'ВКЛ', 'オン', '开', '開'],
}
if __name__ == '__main__':
    d = json.load(open(R, encoding='utf-8')); n = 0
    for e in d:
        tr = T.get(e['en'])
        if not tr: print('SIN TRADUCIR', e['id'], e['en']); continue
        for code, v in zip(C, tr): e[code] = v
        n += 1
    json.dump(d, open(R, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('ok', n, 'rótulos x', len(C), 'idiomas')
