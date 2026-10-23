"""調査結果（wiki_A〜E.json）を notes.json にまとめる。ID付与・関連ノートのID化・年齢帯の判定。
  python wiki/_data/assemble.py wiki/_data/research
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
PREFIX = {"前言語期": "PL", "語彙": "VO", "語意学習": "WL", "言語環境": "EN", "構音・音韻": "PH",
          "音韻意識": "PA", "読み書き": "RW", "文法": "GR", "語用・会話": "PR", "談話・ナラティブ": "NA",
          "心の理論と言語": "TM", "学齢期の語彙・意味": "SV", "神経発達症と語彙・意味": "ND", "発達の道筋": "PW"}
BANDS = [(0, 12, "0〜1歳"), (12, 24, "1〜2歳"), (24, 36, "2〜3歳"), (36, 48, "3〜4歳"), (48, 72, "4〜6歳"),
         (72, 999, "学齢期")]
SCHOOL = re.compile(r"学齢|小学|小\d|中学|高校|学年|児童|青年|成人")
# 数値のない年齢表記（月齢が抄録にない場合など）の振り分け
WORDS = [("乳児", ["0〜1歳"]), ("一語期", ["1〜2歳"]), ("二語", ["1〜2歳"]), ("年中", ["4〜6歳"]), ("年長", ["4〜6歳"]),
         ("幼児期後期", ["4〜6歳"]), ("幼児期", ["2〜3歳", "3〜4歳", "4〜6歳"]), ("幼児", ["2〜3歳", "3〜4歳", "4〜6歳"])]


def months(age):
    """年齢表記から月齢の数値を拾う（1;6 / 1歳6か月 / 18か月 / 4歳）。"""
    a = unicodedata.normalize("NFKC", age)
    vals = []
    for m in re.finditer(r"(\d+);(\d+)", a):
        vals.append(int(m[1]) * 12 + int(m[2]))
    a2 = re.sub(r"\d+;\d+", " ", a)
    for m in re.finditer(r"(\d+(?:\.\d+)?)歳(?:(\d+)か月)?", a2):
        vals.append(float(m[1]) * 12 + int(m[2] or 0))
    a3 = re.sub(r"\d+(?:\.\d+)?歳(?:\d+か月)?", " ", a2)
    # 「4〜6歳」の 4 のように、単位が後ろにだけ付く範囲
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*[〜~\-–]\s*(\d+(?:\.\d+)?)\s*(か月|ヶ月|カ月|歳)", a):
        f = 1 if m[3] != "歳" else 12
        vals += [float(m[1]) * f, float(m[2]) * f]
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(か月|ヶ月|カ月)", a3):
        vals.append(float(m[1]))
    return vals


def bands(age):
    a_n = unicodedata.normalize("NFKC", age)
    v = months(age)
    out = []
    if v:
        lo, hi = min(v), max(v)
        if "未満" in a_n and lo == hi:
            lo = 36  # 「7歳未満」は誤信念課題の対象年齢（幼児期）を指す
        for a, b, name in BANDS:
            # 範囲の上端ちょうど（「〜12か月」「〜6歳」）は次の帯に含めない
            if (lo < b and hi > a) or (lo == hi and a <= lo < b):
                out.append(name)
    else:
        for w, bs in WORDS:
            if w in a_n:
                out += [b for b in bs if b not in out]
                break
    if SCHOOL.search(a_n) and "学齢期" not in out:
        # 「3歳〜小学3年」のように学齢期まで続く範囲は、その間の帯も埋める
        start = min((i for i, (_, _, b) in enumerate(BANDS) if b in out), default=len(BANDS) - 1)
        out += [b for _, _, b in BANDS[start:] if b not in out]
    order = [b for _, _, b in BANDS]
    return sorted(out, key=order.index) or ["学齢期"]


# 別々の調査で重複した同一知見：前者（重複側）を後者に統合する（タイトルの書き出しで指定）
MERGE = {"日本語乳児は母音の長短の弁別感受性": "日本語の母音の長短（/mana/–/ma:na/）の弁別は"}


LEVEL = {"本文確認": "本文", "抄録のみ": "抄録", "二次文献経由": "二次"}


def _deps(lst):
    """builds_on/leads_to の要素が文字列だけのとき（根拠の強さの記載なし）は {"skill": …} にそろえる。"""
    return [{"skill": e} if isinstance(e, str) else e for e in lst]


def norm(t):
    return re.sub(r"[\s、。，．・「」（）()]", "", unicodedata.normalize("NFKC", t))


def main(src):
    raw = []
    for k in "ABCDFGH":
        p = os.path.join(src, f"wiki_{k}.json")
        if os.path.exists(p):
            raw += json.load(open(p, encoding="utf-8"))
    keep = {}
    for r in raw:
        for dup, main_ in MERGE.items():
            if r["title"].startswith(main_):
                keep[dup] = r
    alias = {}
    rest = []
    for r in raw:
        dup = next((d for d in MERGE if r["title"].startswith(d)), None)
        if dup and dup in keep:
            m = keep[dup]
            alias[norm(r["title"])] = norm(m["title"])
            m["related"] = m.get("related", []) + [t for t in r.get("related", []) if t not in m.get("related", [])]
            m["tags"] = list(dict.fromkeys(m.get("tags", []) + r.get("tags", [])))
            m["sources"] += [s for s in r.get("sources", []) if s["cite"] not in [x["cite"] for x in m["sources"]]]
        else:
            rest.append(r)
    raw = rest
    count = {}
    notes, title_id = [], {}
    for r in raw:
        d = r["domain"]
        count[d] = count.get(d, 0) + 1
        nid = f"{PREFIX[d]}-{count[d]:02d}"
        title_id[norm(r["title"])] = nid
        notes.append({"id": nid, "title": r["title"], "domain": d, "age": r.get("age", ""),
                      "age_band": bands(r.get("age", "")), "lang_data": r.get("lang_data", ""),
                      "tags": r.get("tags", []), "body": r["body"], "debate": r.get("debate", ""),
                      "sources": r.get("sources", []), "builds_on": _deps(r.get("builds_on", [])),
                      "leads_to": _deps(r.get("leads_to", [])), "nd_note": r.get("nd_note", ""),
                      "_related": r.get("related", [])})
    miss = []
    for n in notes:
        n["links"] = []
        for t in n.pop("_related"):
            i = title_id.get(alias.get(norm(t), norm(t)))
            if i and i != n["id"] and i not in n["links"]:
                n["links"].append(i)
            elif not i:
                miss.append((n["id"], t))
    # 道筋（E）：下位→上位のつながりノート
    pe = os.path.join(src, "wiki_E.json")
    pmap_p = os.path.join(HERE, "pathway_map.json")
    if os.path.exists(pe):
        pmap = json.load(open(pmap_p, encoding="utf-8"))
        by_id = {n["id"]: n for n in notes}
        for i, e in enumerate(json.load(open(pe, encoding="utf-8")), 1):
            nid = f"PW-{i:02d}"
            m = pmap["pathways"][i - 1]
            fr, to = m["from_notes"], m["to_notes"]
            notes.append({"id": nid, "kind": "道筋", "domain": "発達の道筋",
                          "title": f"{e['from']} → {e['to']}", "from_skill": e["from"], "to_skill": e["to"],
                          "edges": m["edges"],
                          "age": f"{e.get('from_age', '')} → {e.get('to_age', '')}",
                          "age_band": bands(e.get("from_age", "")), "to_band": bands(e.get("to_age", "")),
                          "evidence": e["evidence"], "bidirectional": e.get("bidirectional", False),
                          "lang_data": e.get("lang_data", ""), "tags": [e["evidence"]],
                          "body": e["summary"], "debate": e.get("debate", ""),
                          "sources": [dict(s, level=LEVEL.get(s.get("level"), s.get("level"))) for s in e.get("sources", [])],
                          "nd_note": e.get("nd_note", ""), "links": [x for x in fr + to if x in by_id],
                          "builds_on": [{"id": x, "evidence": e["evidence"]} for x in fr if x in by_id],
                          "leads_to": [{"id": x, "evidence": e["evidence"]} for x in to if x in by_id]})
            # 上位側のノートに「基礎となるスキル」として、下位側に「つながる上位スキル」として書き戻す
            for t in to:
                for f in fr:
                    if t in by_id and f in by_id and t != f:
                        by_id[t]["builds_on"].append({"id": f, "evidence": e["evidence"], "via": nid})
                        by_id[f]["leads_to"].append({"id": t, "evidence": e["evidence"], "via": nid})
    with open(os.path.join(HERE, "notes.json"), "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=1)
    print(len(notes), "notes;", "unresolved related:", len(miss))
    for m in miss:
        print("  ", *m)


if __name__ == "__main__":
    main(sys.argv[1])
