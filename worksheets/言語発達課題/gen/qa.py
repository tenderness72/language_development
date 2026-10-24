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
        ex = item.get("extra")
        if not ex:
            return f"[III:{item['id']}] extra（右に足す、どれとも結ばない語）が必要"
        if ex in rights or ex in lefts:
            return f"[III:{item['id']}] extra '{ex}' が左右の語と重複"
    elif type_key == "VII":
        if not item.get("initial"):
            return f"[VII:{item['id']}] initial（語頭音）が必要"
        from .templates.t7_mora import MORA_ROWS, split_mora
        rows = item.get("moras") or MORA_ROWS
        for k, words in (item.get("answers") or {}).items():
            if int(k) not in rows:
                return f"[VII:{item['id']}] answers の {k}音 が moras {rows} にない"
            fx = {int(i): ch for i, ch in ((item.get("fixed") or {}).get(int(k)) or {}).items()}
            for w in words:
                units = split_mora(w)
                if not w.startswith(item["initial"]) or len(units) != int(k):
                    return f"[VII:{item['id']}] 解答例 '{w}' が語頭音または{k}音と合わない"
                if units[0] != item["initial"]:
                    return f"[VII:{item['id']}] 解答例 '{w}' の1マス目が語頭音「{item['initial']}」と合わない"
                for i, ch in fx.items():
                    if not (0 < i < int(k)) or units[i] != ch:
                        return f"[VII:{item['id']}] 解答例 '{w}' の{i + 1}マス目が書いておく字「{ch}」と合わない"
                # 拗長音（拗音＋のばす音）には、のばす音の字を書いておく
                for j, u in enumerate(units[:-1]):
                    if len(u) == 2 and u[1] in "ゃゅょ" and units[j + 1] in "うー" and fx.get(j + 1) != units[j + 1]:
                        return (f"[VII:{item['id']}] 解答例 '{w}' の拗長音に支えがない："
                                f"{k}音の行の{j + 2}マス目に「{units[j + 1]}」を書いておく（fixed）")
                lv = int(item.get("level", 1))
                if lv == 1 and any(ch in w for ch in "ゃゅょぁぃぅぇぉっんー"):
                    return f"[VII:{item['id']}] Lv1 の解答例 '{w}' に特殊音節がある"
                if lv == 2 and any(ch in w for ch in "ゃゅょぁぃぅぇぉっ"):
                    return f"[VII:{item['id']}] Lv2 の解答例 '{w}' に拗音・促音がある"
        for k, row in (item.get("fixed") or {}).items():
            if len(row) + 1 >= int(k):
                return f"[VII:{item['id']}] {k}音の行は、書いておく字で全部うまってしまう（書くマスが残らない）"
        lv = int(item.get("level", 1))
        fixed_chars = {ch for row in (item.get("fixed") or {}).values() for ch in row.values()}
        if lv == 2 and not fixed_chars:
            return f"[VII:{item['id']}] Lv2 は「ん」または長音の字を書いておく行（fixed）が必要"
        if lv == 3 and len(split_mora(item["initial"])[0]) < 2 and "っ" not in fixed_chars:
            return f"[VII:{item['id']}] Lv3 は語頭音が拗音か、「っ」を書いておく行が必要"
    elif type_key == "V":
        rel = item.get("relation")
        expect = {"かんけい": 1, "なかま": 2, "こうたい": 3}
        if rel not in expect:
            return f"[V:{item['id']}] relation は かんけい／なかま／こうたい のいずれか"
        if int(item.get("level", 1)) != expect[rel]:
            return f"[V:{item['id']}] relation「{rel}」は Lv{expect[rel]}"
    elif type_key == "IX":
        mem, oth = item.get("members", []), item.get("others", [])
        if len(mem) != 6 or len(oth) != 6:
            return f"[IX:{item['id']}] members/others は各6語"
        if len(set(mem + oth)) != 12:
            return f"[IX:{item['id']}] 語に重複あり（仲間とそうでない語の衝突を含む）"
    elif type_key == "X":
        regions = ["left", "both", "right"] + (["none"] if int(item.get("level", 1)) >= 2 else [])
        words = []
        for r in regions:
            ws = item.get(r, [])
            if len(ws) != 2:
                return f"[X:{item['id']}] {r} は2語（Lv2 は none も2語）"
            words += ws
        if int(item.get("level", 1)) == 1 and item.get("none"):
            return f"[X:{item['id']}] Lv1 に none は置かない（3つの場所だけ）"
        if len(set(words)) != len(words):
            return f"[X:{item['id']}] 語が2つの場所に重複している"
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
