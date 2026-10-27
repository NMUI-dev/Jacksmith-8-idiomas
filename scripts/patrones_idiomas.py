# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Frases con números o nombres (patrones) para los idiomas nuevos, escritas a mano.
Mismo formato que piezas/30_espanol/fuente/es_patrones.json: [regex del inglés, plantilla]; $N = grupo tal cual,
{N} = grupo traducido con la tabla, {Nl} = traducido y en minúsculas.
Escribe piezas/31_idiomas/fuente/<codigo>_patrones.json.   uso: python scripts/patrones_idiomas.py
"""
import json, os
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ES = json.load(open(os.path.join(RAIZ, 'piezas', '30_espanol', 'fuente', 'es_patrones.json'), encoding='utf-8'))
REGEX = [r for r, _ in ES]
T = {   # una plantilla por patrón, en el mismo orden que es_patrones.json
 'it': ['Giorno: $1', 'Giorno $1 completato!', 'Fine del giorno $1', 'Pagina $1/$2', '$1% completato', 'Creata 1 volta',
        'Creata $1 volte', 'Sconfitto 1 volta', 'Sconfitto $1 volte', 'Debole ai potenziamenti di {1l}', '-{1} #$2',
        '-{2} di {1l}', '+$1 per TUTTI i soldati', '+$1 per questa arma', 'Hai forgiato: {1}!', 'Hai forgiato: {1}!',
        '$1 XP al prossimo livello', 'Versione $1', 'Build $1', 'Disegno $1', '{1} x $2', '{1}: $2', 'Potenziamento {1l} +$2',
        'Ne hai $1', '{1} $2'],
 'pt': ['Dia: $1', 'Dia $1 concluído!', 'Fim do dia $1', 'Página $1/$2', '$1% concluído', 'Criada 1 vez', 'Criada $1 vezes',
        'Derrotado 1 vez', 'Derrotado $1 vezes', 'Fraco contra bônus de {1l}', '-{1} #$2', '-{2} de {1l}',
        '+$1 para TODOS os soldados', '+$1 para esta arma', 'Você forjou: {1}!', 'Você forjou: {1}!',
        '$1 XP para o próximo nível', 'Versão $1', 'Build $1', 'Projeto $1', '{1} x $2', '{1}: $2', 'Bônus de {1l} +$2',
        'Você tem $1', '{1} $2'],
 'fr': ['Jour : $1', 'Jour $1 terminé !', 'Fin du jour $1', 'Page $1/$2', '$1 % terminé', 'Créée 1 fois', 'Créée $1 fois',
        'Vaincu 1 fois', 'Vaincu $1 fois', 'Faible contre les bonus de {1l}', '-{1} #$2', '-{2} en {1l}',
        '+$1 pour TOUS les soldats', '+$1 pour cette arme', 'Tu as forgé : {1} !', 'Tu as forgé : {1} !',
        '$1 XP avant le niveau suivant', 'Version $1', 'Build $1', 'Modèle $1', '{1} x $2', '{1} : $2', 'Bonus {1l} +$2',
        'Tu en as $1', '{1} $2'],
 'de': ['Tag: $1', 'Tag $1 geschafft!', 'Ende von Tag $1', 'Seite $1/$2', '$1 % geschafft', '1-mal geschmiedet',
        '$1-mal geschmiedet', '1-mal besiegt', '$1-mal besiegt', 'Schwach gegen {1}-Boni', '-{1} #$2', '-{2} ({1})',
        '+$1 für ALLE Soldaten', '+$1 für diese Waffe', 'Du hast geschmiedet: {1}!', 'Du hast geschmiedet: {1}!',
        '$1 EP bis zur nächsten Stufe', 'Version $1', 'Build $1', 'Entwurf $1', '{1} x $2', '{1}: $2', '{1}-Bonus +$2',
        'Du hast $1', '{1} $2'],
 'ru': ['День: $1', 'День $1 пройден!', 'Конец дня $1', 'Страница $1/$2', 'Готово: $1%', 'Создано: 1 раз',
        'Создано раз: $1', 'Побеждён: 1 раз', 'Побеждён раз: $1', 'Уязвим к усилениям: {1l}', '-{1} #$2', '-{2} ({1l})',
        '+$1 для ВСЕХ солдат', '+$1 для этого оружия', 'Выковано: {1}!', 'Выковано: {1}!', '$1 опыта до след. уровня',
        'Версия $1', 'Сборка $1', 'Чертёж $1', '{1} x $2', '{1}: $2', 'Усиление «{1}» +$2', 'У тебя: $1', '{1} $2'],
 'ja': ['日数：$1', '$1日目 完了！', '$1日目 終了', 'ページ $1/$2', '$1% 完了', '作成回数：1', '作成回数：$1', '撃破回数：1',
        '撃破回数：$1', '{1}ブーストに弱い', '-{1} #$2', '-{1}の{2}', '兵士全員に+$1', 'この武器に+$1', '{1}を作った！',
        '{1}を作った！', '次のレベルまで $1 XP', 'バージョン $1', 'ビルド $1', 'デザイン $1', '{1} x $2', '{1}：$2',
        '{1}ブースト +$2', '所持数：$1', '{1} $2'],
 'zh_hans': ['天数：$1', '第$1天完成！', '第$1天结束', '第$1/$2页', '已完成$1%', '已制作1次', '已制作$1次', '已击败1次',
        '已击败$1次', '弱点：{1}强化', '-{1} #$2', '-{1}{2}', '全体士兵+$1', '此武器+$1', '你锻造了：{1}！', '你锻造了：{1}！',
        '距下一级还需$1经验', '版本 $1', '构建 $1', '设计 $1', '{1} x $2', '{1}：$2', '{1}强化 +$2', '拥有$1个', '{1} $2'],
 'zh_hant': ['天數：$1', '第$1天完成！', '第$1天結束', '第$1/$2頁', '已完成$1%', '已製作1次', '已製作$1次', '已擊敗1次',
        '已擊敗$1次', '弱點：{1}強化', '-{1} #$2', '-{1}{2}', '全體士兵+$1', '此武器+$1', '你鍛造了：{1}！', '你鍛造了：{1}！',
        '距下一級還需$1經驗', '版本 $1', '組建 $1', '設計 $1', '{1} x $2', '{1}：$2', '{1}強化 +$2', '擁有$1個', '{1} $2'],
}
if __name__ == '__main__':
    out = os.path.join(RAIZ, 'piezas', '31_idiomas', 'fuente'); os.makedirs(out, exist_ok=True)
    for code, pl in T.items():
        assert len(pl) == len(REGEX), (code, len(pl))
        json.dump([[r, p] for r, p in zip(REGEX, pl)], open(os.path.join(out, f'{code}_patrones.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    print('ok', len(T), 'idiomas x', len(REGEX), 'patrones')
