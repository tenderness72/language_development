"""品質保証チェック。

- 閉課題（I・II・III）の正解が一意か（正解語とダミー語の衝突検査）
  ※文字列の衝突のみ検査する。意味の上で別の経路が成り立たないかは人が確認すること。
- データ内に同じ中身の問題がないか（data.dedup_key による表記ゆれ込みの判定）
- ページ内の文字はみ出し（ctx.warnings）
は generate 側で集約し、満たさなければ再サンプリング→上限超で停止する。
"""


class QAError(Exception):
    pass


def check_item(type_key, item):
    """データ自体の妥当性（正解とダミーの非衝突など）。問題があれば文字列を返す。"""
    if type_key == "I":
        chain = item.get("chain", [])
        if len(chain) != 5:
            return f"[I:{item['id']}] chain は5要素 [start,列2,列3,列4,goal] が必要"
        d = item.get("distractors", {})
        for ci, col in enumerate(("col2", "col3", "col4")):
            correct = chain[ci + 1]
            dummies = d.get(col, [])
            if len(dummies) < 3:
                return f"[I:{item['id']}] {col} のダミーが3語未満"
            if correct in dummies:
                return f"[I:{item['id']}] {col} の正解'{correct}'がダミーと衝突"
            if len(set(dummies)) != len(dummies):
                return f"[I:{item['id']}] {col} のダミーに重複"
    elif type_key == "II":
        rel = item.get("related", [])
        dis = item.get("distractors", [])
        if len(rel) != 5 or len(dis) != 5:
            return f"[II:{item['id']}] related/distractors は各5語"
        overlap = set(rel) & set(dis)
        if overlap:
            return f"[II:{item['id']}] 関連語とダミーが衝突: {overlap}"
        if len(set(rel + dis)) != 10:
            return f"[II:{item['id']}] 語に重複あり"
    elif type_key == "III":
        pairs = item.get("pairs", [])
        if len(pairs) != 5:
            return f"[III:{item['id']}] pairs は5組"
        lefts = [p[0] for p in pairs]
        rights = [p[1] for p in pairs]
        if len(set(lefts)) != 5 or len(set(rights)) != 5:
            return f"[III:{item['id']}] 左右に重複があり一意に解けない"
    elif type_key == "VII":
        if not item.get("initial"):
            return f"[VII:{item['id']}] initial（語頭音）が必要"
    return None


def validate_items(type_key, items):
    """データ全件を検査し、問題のあるメッセージ一覧を返す。"""
    from .data import dedup_key
    errs = []
    seen = {}
    for it in items:
        msg = check_item(type_key, it)
        if msg:
            errs.append(msg)
        # 同じ中身の問題がレベルをまたいで重複していないか
        k = dedup_key(type_key, it)
        if k in seen:
            errs.append(f"[{type_key}:{it['id']}] '{seen[k]}' と同じ問題（重複）")
        else:
            seen[k] = it["id"]
    return errs
