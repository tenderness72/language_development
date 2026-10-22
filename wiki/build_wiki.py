"""定型発達の言語発達 Wiki（ツェッテルカステン式）を組み立てる。

入力: wiki/_data/notes.json（ノートの一覧。各ノートに id・本文・出典・関連ノートを持つ）
出力:
  wiki/notes/<ID>.md       1ノート1ファイル（Obsidian で開ける [[ID|タイトル]] 形式のリンク）
  wiki/00_索引.md          領域ごとの構造ノート（入口）
  wiki/01_年齢別の見取り図.md  年齢帯ごとの構造ノート
  wiki/02_文献一覧.md      全ノートの出典をまとめた一覧
  wiki/viewer/wiki.html    閲覧用ページ（検索・タグ・被リンク）
  python wiki/build_wiki.py
"""
import html
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "_data", "notes.json")

DOMAIN_ORDER = ["発達の道筋", "前言語期", "言語環境", "語彙", "語意学習", "構音・音韻", "音韻意識", "読み書き",
                "文法", "語用・会話", "談話・ナラティブ", "心の理論と言語", "学齢期の語彙・意味"]
# 年齢帯（構造ノート用）。各ノートの age_band（複数可）で振り分ける。
BANDS = ["0〜1歳", "1〜2歳", "2〜3歳", "3〜4歳", "4〜6歳", "学齢期"]


def load():
    with open(DATA, encoding="utf-8") as f:
        notes = json.load(f)
    by_id = {n["id"]: n for n in notes}
    # 被リンク（backlinks）を計算
    back = defaultdict(list)
    for n in notes:
        for r in n.get("links", []):
            if r in by_id and n["id"] not in back[r]:
                back[r].append(n["id"])
    for n in notes:
        n["backlinks"] = back.get(n["id"], [])
        n.setdefault("kind", "知見")
    return notes, by_id


def link(by_id, nid):
    return f"[[{nid}|{by_id[nid]['title']}]]" if nid in by_id else nid


def write_note(n, by_id):
    fm = ["---", f"id: {n['id']}", f"title: \"{n['title']}\"", f"domain: {n['domain']}",
          f"age: \"{n.get('age', '')}\"", f"age_band: [{', '.join(n.get('age_band', []))}]",
          f"data: {n.get('lang_data', '')}", f"tags: [{', '.join(n.get('tags', []))}]", "---", ""]
    body = [f"# {n['id']} {n['title']}", "", f"**年齢**：{n.get('age', '—')}　**データ**：{n.get('lang_data', '—')}", "",
            n["body"], ""]
    if n.get("debate"):
        body += ["## 論点・議論のあるところ", "", n["debate"], ""]
    body += ["## 出典", ""]
    for s in n.get("sources", []):
        url = s.get("url", "")
        body.append(f"- {s['cite']}" + (f"　<{url}>" if url.startswith("http") else (f"　{url}" if url else ""))
                    + f"（確認：{s.get('level', '—')}）")
    body.append("")
    for key, head in (("builds_on", "基礎となるスキル（下位）"), ("leads_to", "つながる上位スキル")):
        if n.get(key):
            body += [f"## {head}", ""]
            for e in n[key]:
                tgt = link(by_id, e["id"]) if e.get("id") in by_id else e.get("skill", "")
                via = f"　根拠ノート：{link(by_id, e['via'])}" if e.get("via") in by_id else ""
                body.append(f"- {tgt}〔{e.get('evidence', '—')}〕" + (f"：{e['basis']}" if e.get("basis") else "") + via)
            body.append("")
    if n.get("nd_note"):
        body += ["## 神経発達症の子どもでの注意", "", n["nd_note"], ""]
    if n.get("links"):
        body += ["## 関連ノート", ""] + [f"- {link(by_id, r)}" for r in n["links"] if r in by_id] + [""]
    if n.get("backlinks"):
        body += ["## このノートを参照しているノート", ""] + [f"- {link(by_id, r)}" for r in n["backlinks"]] + [""]
    body += [f"[[00_索引|索引へ]]　[[01_年齢別の見取り図|年齢別の見取り図へ]]　[[03_発達の道筋|発達の道筋へ]]", ""]
    with open(os.path.join(ROOT, "notes", f"{n['id']}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(fm + body))


def write_index(notes, by_id):
    by_dom = defaultdict(list)
    for n in notes:
        by_dom[n["domain"]].append(n)
    out = ["# 00 索引（領域別）", "",
           "定型発達児の言語発達について、1枚に1つの知見をまとめたノート（ツェッテルカステン）の入口です。",
           "各ノートには出典（確認の程度つき）と、関連ノートへのリンクがあります。", "",
           f"ノート数：{len(notes)}　／　[[03_発達の道筋|発達の道筋（基礎→上位）]]　／　[[01_年齢別の見取り図|年齢別の見取り図]]　／　[[02_文献一覧|文献一覧]]", ""]
    doms = [d for d in DOMAIN_ORDER if d in by_dom] + [d for d in by_dom if d not in DOMAIN_ORDER]
    for d in doms:
        out += [f"## {d}", ""] + [f"- {link(by_id, n['id'])}（{n.get('age', '')}）" for n in by_dom[d]] + [""]
    with open(os.path.join(ROOT, "00_索引.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def write_timeline(notes, by_id):
    out = ["# 01 年齢別の見取り図", "", "各ノートを年齢帯で並べた構造ノートです（1つのノートが複数の年齢帯にまたがることがあります）。", ""]
    for b in BANDS:
        hits = [n for n in notes if b in n.get("age_band", [])]
        out += [f"## {b}", ""]
        by_dom = defaultdict(list)
        for n in hits:
            by_dom[n["domain"]].append(n)
        for d in [x for x in DOMAIN_ORDER if x in by_dom]:
            out.append(f"- **{d}**：" + "／".join(link(by_id, n["id"]) for n in by_dom[d]))
        out.append("")
    with open(os.path.join(ROOT, "01_年齢別の見取り図.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def write_biblio(notes, by_id):
    refs = defaultdict(lambda: {"url": "", "level": set(), "notes": []})
    for n in notes:
        for s in n.get("sources", []):
            r = refs[s["cite"]]
            r["url"] = r["url"] or s.get("url", "")
            r["level"].add(s.get("level", ""))
            r["notes"].append(n["id"])
    out = ["# 02 文献一覧", "", "全ノートの出典です。（確認）は、本文を読んだか・抄録のみか・他の文献経由かを示します。", ""]
    for cite in sorted(refs):
        r = refs[cite]
        url = r["url"]
        out.append(f"- {cite}" + (f"　<{url}>" if url.startswith("http") else (f"　{url}" if url else ""))
                   + f"（確認：{'・'.join(sorted(x for x in r['level'] if x))}）— "
                   + "、".join(link(by_id, i) for i in dict.fromkeys(r["notes"])))
    out.append("")
    with open(os.path.join(ROOT, "02_文献一覧.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


EVID_STYLE = {"縦断で予測": "==>", "介入で確認": "==>", "相関のみ": "-->", "理論上の仮説": "-.->"}


def pathway_edges(notes):
    """道筋ノート（kind=道筋）から、スキル名を節点とする（下位→上位）の辺を集める。"""
    nodes, edges = {}, []
    order = {b: i for i, b in enumerate(BANDS)}
    for n in notes:
        if n["kind"] != "道筋":
            continue
        for label, band in ((n["from_short"], n["age_band"]), (n["to_short"], n.get("to_band") or n["age_band"])):
            b0 = (band or ["学齢期"])[0]
            if label not in nodes or order[b0] < order[nodes[label]]:
                nodes[label] = b0
        edges.append((n["from_short"], n["to_short"], n["evidence"], n.get("bidirectional", False), n["id"]))
    return nodes, edges


def mermaid(notes, by_id):
    nodes, edges = pathway_edges(notes)
    key = {lab: f"K{i}" for i, lab in enumerate(nodes)}
    lines = ["flowchart LR"]
    for b in BANDS:
        labs = [lab for lab, st in nodes.items() if st == b]
        if not labs:
            continue
        lines.append(f'  subgraph S{BANDS.index(b)}["{b}"]')
        lines += [f'    {key[lab]}["{lab}"]' for lab in labs]
        lines.append("  end")
    for a, b, ev, bi, nid in edges:
        arrow = EVID_STYLE.get(ev, "-->")
        if bi:
            arrow = {"==>": "<==>", "-->": "<-->", "-.->": "<-.->"}[arrow]
        lines.append(f"  {key[a]} {arrow}|{nid}| {key[b]}")
    return "\n".join(lines)


def write_pathway(notes, by_id):
    out = ["# 03 発達の道筋（基礎 → 上位）", "",
           "どの下位スキルが、どの上位スキルの基礎になっているかを、根拠の強さつきでまとめた構造ノートです。",
           "神経発達症の子どもでは、この順序がゆっくり進んだり、下位スキルが不十分なまま上位スキルを部分的に身につけたりしますが、",
           "下位スキルが基礎であることに変わりはありません（各ノートの「神経発達症の子どもでの注意」を参照）。", "",
           "根拠の強さ：**縦断で予測**（先に測った力が後の力を予測）／**介入で確認**（下位を育てると上位が伸びた）／**相関のみ**／**理論上の仮説**", "",
           "```mermaid", mermaid(notes, by_id), "```", "", "## つながりの一覧", ""]
    for n in [x for x in notes if x["kind"] == "道筋"]:
        bi = "（双方向）" if n.get("bidirectional") else ""
        out.append(f"- {link(by_id, n['id'])}〔{n.get('evidence', '')}〕{bi}（{n.get('age', '')}）")
    out.append("")
    with open(os.path.join(ROOT, "03_発達の道筋.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def write_viewer(notes):
    tpl = os.path.join(ROOT, "viewer", "template.html")
    if not os.path.exists(tpl):
        return
    with open(tpl, encoding="utf-8") as f:
        page = f.read()
    by_id = {n["id"]: n for n in notes}
    payload = json.dumps({"notes": notes, "domains": DOMAIN_ORDER, "bands": BANDS}, ensure_ascii=False)
    page = page.replace("<!--__MERMAID__-->", html.escape(mermaid(notes, by_id)))
    page = page.replace("/*__WIKI__*/null", payload.replace("</", "<\\/"))
    with open(os.path.join(ROOT, "viewer", "wiki.html"), "w", encoding="utf-8") as f:
        f.write(page)


def check(notes, by_id):
    errs = []
    for n in notes:
        if not n.get("sources"):
            errs.append(f"{n['id']}: 出典がない")
        for r in n.get("links", []):
            if r not in by_id:
                errs.append(f"{n['id']}: 関連ノート {r} が存在しない")
    return errs


def main():
    notes, by_id = load()
    errs = check(notes, by_id)
    if errs:
        raise SystemExit("\n".join(errs))
    os.makedirs(os.path.join(ROOT, "notes"), exist_ok=True)
    for f in os.listdir(os.path.join(ROOT, "notes")):
        if f.endswith(".md"):
            os.remove(os.path.join(ROOT, "notes", f))
    for n in notes:
        write_note(n, by_id)
    write_index(notes, by_id)
    write_timeline(notes, by_id)
    write_biblio(notes, by_id)
    write_pathway(notes, by_id)
    write_viewer(notes)
    print(len(notes), "notes")


if __name__ == "__main__":
    main()
