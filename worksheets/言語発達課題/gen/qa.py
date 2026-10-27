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
    elif type_key in ("XI", "XII", "XIII", "XIV"):
        from .templates.t7_mora import split_mora
        lv = int(item.get("level", 1))
        special = set("ゃゅょっんーぁぃぅぇぉ")
        dakuon = set("がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ")

        def lvl_ok(w):
            if lv == 1 and (set(w) & (special | dakuon)):
                return False
            if lv == 2 and type_key == "XI" and set(w) & special:
                return False
            return True
        if type_key == "XI":
            ws = item.get("words", [])
            if len(ws) != 4:
                return f"[XI:{item['id']}] words は4語"
            for w in ws:
                if not lvl_ok(w):
                    return f"[XI:{item['id']}] '{w}' がレベル{lv}の条件（Lv1 清音のみ・Lv2 特殊音節なし）に合わない"
                if len(split_mora(w)) > 7:
                    return f"[XI:{item['id']}] '{w}' の音の数が○の数（7）をこえる"
            if lv == 2 and not any(set(w) & dakuon for w in ws):
                return f"[XI:{item['id']}] Lv2 は濁音・半濁音の語を含める"
            if lv == 3 and not all(set(w) & special for w in ws):
                return f"[XI:{item['id']}] Lv3 はどの語にも特殊音節を含める"
        elif type_key == "XII":
            from .templates.t12_sound_search import hit
            ws = item.get("words", [])
            if len(ws) != 6 or len(set(ws)) != 6:
                return f"[XII:{item['id']}] words は重ならない6語"
            n = sum(hit(w, item["target"], item["position"]) for w in ws)
            if n != 3:
                return f"[XII:{item['id']}] 当たりが{n}語（3語にする）"
            if lv == 1 and not all(lvl_ok(w) for w in ws):
                return f"[XII:{item['id']}] Lv1 は清音だけの語にする"
        elif type_key == "XIII":
            es = item.get("entries", [])
            if len(es) != 4:
                return f"[XIII:{item['id']}] entries は4つ"
            for e in es:
                u = split_mora(e["w"])
                if set(e["w"]) & special and lv < 3:
                    return f"[XIII:{item['id']}] '{e['w']}' に特殊音節がある（Lv1・2 では使わない）"
                from .templates.t13_sound_manipulation import answer as _ans
                if "".join(_ans(e)) != e.get("answer"):
                    return f"[XIII:{item['id']}] '{e['w']}' のこたえ '{''.join(_ans(e))}' が answer '{e.get('answer')}' と合わない"
                if e["op"] == "けす" and u.count(e.get("t")) != 1:
                    return f"[XIII:{item['id']}] '{e['w']}' にけす音「{e.get('t')}」が1回だけ出てくるようにする"
                if e["op"] not in ("ぎゃく", "けす"):
                    return f"[XIII:{item['id']}] op は ぎゃく／けす"
                if lv == 1 and (len(u) != 2 or e["op"] != "ぎゃく"):
                    return f"[XIII:{item['id']}] Lv1 は2音のことばの逆唱"
        else:
            from .templates.t12_sound_search import hit
            import unicodedata
            ex = unicodedata.normalize("NFKC", item.get("example", ""))
            ex = "".join(chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch for ch in ex)
            if item.get("position") not in ("はじめ", "おしまい"):
                return f"[XIV:{item['id']}] position は はじめ／おしまい"
            if not ex or not hit(ex, item["target"], item["position"]):
                return f"[XIV:{item['id']}] 例 '{item.get('example')}' が条件（{item['target']}・{item['position']}）に合わない"
            if (lv == 3) != (item["position"] == "おしまい"):
                return f"[XIV:{item['id']}] Lv3 は「〇で終わる言葉」、Lv1・2 は「〇から始まる言葉」"
    elif type_key == "XV":
        from .templates.t15_sentence_build import ROLES
        lv = int(item.get("level", 1))
        sents = item.get("sentences", [])
        if len(sents) != (3 if lv <= 3 else 2):
            return f"[XV:{item['id']}] sentences は Lv1〜3 で3文、Lv4・5 で2文"
        for st in sents:
            roles = [r for r, _ in st]
            if any(r not in ROLES for r in roles) or roles[-1] != "どうする" or roles.count("どうする") != 1:
                return f"[XV:{item['id']}] 役割が不正（最後は どうする を1つ）: {roles}"
            if len(st) > 5:
                return f"[XV:{item['id']}] 1文は5語まで（1行に収める）"
            if ("どうして" in roles) != (lv == 5) or roles.count("どうして") > 1:
                return f"[XV:{item['id']}] 「〜て」の動詞（どうして）は Lv5 だけで、1文に1つ"
            if ({"いつ", "だれと"} & set(roles)) and lv < 4:
                return f"[XV:{item['id']}] いつ・だれと は Lv4 から"
            if lv == 4 and (len(st) < 4 or not ({"いつ", "だれと"} & set(roles))):
                return f"[XV:{item['id']}] Lv4 は いつ か だれと を含む4〜5語の文"
            if lv == 1 and len(st) != 2:
                return f"[XV:{item['id']}] Lv1 は2語の文"
            if lv == 2 and roles not in (["だれが", "なにを", "どうする"], ["どんな", "なにを", "どうする"]):
                return f"[XV:{item['id']}] Lv2 は だれが＋なにを＋どうする か どんな＋なにを＋どうする"
            if lv == 3 and not ({"どこで", "なにで", "どこに"} & set(roles)):
                return f"[XV:{item['id']}] Lv3 は どこで・なにで・どこに のどれかを含める"
        words = [w for st in sents for _, w in st]
        if len(set(words)) != len(words):
            return f"[XV:{item['id']}] ことばばこの語が重なっている"
    elif type_key == "XVIII":
        from .templates.t15_sentence_build import ROLES
        lv = int(item.get("level", 1))
        st = item.get("sentence", [])
        roles = [r for r, _ in st]
        if not item.get("image") or not item.get("scene"):
            return f"[XVIII:{item['id']}] image（絵のファイル名）と scene（絵の内容）を書く"
        if any(r not in ROLES for r in roles) or not roles or roles[-1] != "どうする" or roles.count("どうする") != 1:
            return f"[XVIII:{item['id']}] 役割が不正（最後は どうする を1つ）: {roles}"
        if {"いつ", "だれと", "どうして"} & set(roles):
            return f"[XVIII:{item['id']}] いつ・だれと・どうして は使わない（絵1枚で決まらない）"
        if lv == 1 and len(st) != 2:
            return f"[XVIII:{item['id']}] Lv1 は2語の文"
        if lv == 2 and roles != ["だれが", "なにを", "どうする"]:
            return f"[XVIII:{item['id']}] Lv2 は だれが＋なにを＋どうする"
        if lv == 3 and not ({"どこで", "なにで", "どこに"} & set(roles)):
            return f"[XVIII:{item['id']}] Lv3 は どこで・なにで・どこに のどれかを含める"
    elif type_key == "XVI":
        from .templates.t16_particles import parse
        lv = int(item.get("level", 1))
        sents = item.get("sentences", [])
        if len(sents) != 4:
            return f"[XVI:{item['id']}] sentences は4文"
        for st in sents:
            parts = st["parts"] if isinstance(st, dict) else st
            blanks = [parse(p)[0] for p in parts if parse(p)[1]]
            if any(b not in ("が", "を", "に") for b in blanks):
                return f"[XVI:{item['id']}] 空欄は が・を・に"
            if ("に" in blanks) != (lv == 4):
                return f"[XVI:{item['id']}] に を使うのは Lv4 だけ（Lv4 は どの文にも に を入れる）"
            if lv == 4 and (blanks.count("が") != 1 or len(set(blanks)) != len(blanks)):
                return f"[XVI:{item['id']}] Lv4 は が＋に（＋を）を1つずつ"
            if lv == 1 and len(blanks) != 1:
                return f"[XVI:{item['id']}] Lv1 は助詞1つ"
            if lv in (2, 3) and sorted(blanks) != ["が", "を"]:
                return f"[XVI:{item['id']}] Lv2・3 は が と を を1つずつ"
            if lv == 3 and not (isinstance(st, dict) and st.get("context")):
                return f"[XVI:{item['id']}] Lv3 は状況の説明（context）を付ける"
    elif type_key == "XVII":
        from .templates.t17_word_transform import apply_ops
        es = item.get("entries", [])
        if len(es) != 4:
            return f"[XVII:{item['id']}] entries は4つ"
        lv = int(item.get("level", 1))
        for e in es:
            got = "".join(apply_ops(e["w"], e["ops"]))
            if got != e.get("answer"):
                return f"[XVII:{item['id']}] '{e['w']}' の操作の結果 '{got}' が answer '{e.get('answer')}' と合わない"
            if len(e["ops"]) > 1 and lv < 3:
                return f"[XVII:{item['id']}] 2段階の指示は Lv3"
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
