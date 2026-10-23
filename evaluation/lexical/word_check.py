"""ワークシートの語を、語彙表（獲得時期・学年配当）と照らし合わせる。

  python evaluation/lexical/word_check.py <語彙表のフォルダ>

語彙表（リポジトリには入れない。各配布元から取得する）:
  ninjal_kyoiku/kyoikukihongoi_2009B_utf8.csv  国立国語研究所「教育基本語彙データベース」（CC BY 4.0）
      語彙配当 1=小学校低学年 2=小学校高学年 3=中学校、田中＝指導学年①〜⑥
  mochizuki_ota_2025_aoa/data_AoA.csv           Mochizuki & Ota (2025) 獲得年齢評定（成人の評定、OSF）
      1=0–1歳 2=2–3歳 3=4–5歳 4=6–7歳 5=8–9歳 6=10–11歳 7=12歳以上
出力:
  evaluation/lexical/word_bands.tsv   語ごとの「時期の目安」（教育基本語彙の配当を主に、AoA で補う）
  evaluation/lexical/summary.md       課題・レベルごとの集計と、遅い語の一覧
"""
import csv
import glob
import os
import sys
import unicodedata
from collections import defaultdict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WS = os.path.join(ROOT, "worksheets", "言語発達課題", "data", "templates")
OUT = os.path.dirname(os.path.abspath(__file__))
TANAKA = {c: i for i, c in enumerate("①②③④⑤⑥", start=1)}
NAME = {"I": "Ⅰ", "II": "Ⅱ", "III": "Ⅲ", "IV": "Ⅳ", "V": "Ⅴ", "VI": "Ⅵ", "VII": "Ⅶ", "VIII": "Ⅷ", "IX": "Ⅸ", "X": "Ⅹ"}
# 時期の目安（発達年齢）。教育基本語彙の配当・田中の学年、AoA 評定をこの帯にそろえる。
BAND_LABEL = {1: "〜5歳", 2: "6〜7歳（小学校低学年）", 3: "8〜9歳", 4: "10〜12歳（小学校高学年）", 5: "中学生以上"}


def kana(s):
    s = unicodedata.normalize("NFKC", str(s)).strip()
    return "".join(chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch for ch in s)


def worksheet_words():
    """語 → {"I1", "III2", …}（課題とレベル）。関係名・カテゴリー名など問題の見出しも含める。"""
    words = defaultdict(set)
    skip = {"id", "level", "lines", "slots", "moras", "fixed", "key", "answers", "initial"}
    for f in sorted(glob.glob(os.path.join(WS, "*.yaml"))):
        d = yaml.safe_load(open(f, encoding="utf-8"))
        t = d["type"]
        for it in d["items"]:
            tag = f"{t}{it.get('level', 1)}"

            def add(v):
                if isinstance(v, str):
                    words[v.strip()].add(tag)
                elif isinstance(v, list):
                    for x in v:
                        add(x)
                elif isinstance(v, dict):
                    for x in v.values():
                        add(x)
            for k, v in it.items():
                if k not in skip and not (t == "V" and k == "relation"):
                    add(v)
            if t == "VII":   # Ⅶ は解答例の語（子どもが思い浮かべる語の目安）
                add(it.get("answers", {}))
    return words


def load_norms(src):
    kyo = defaultdict(list)
    with open(os.path.join(src, "ninjal_kyoiku", "kyoikukihongoi_2009B_utf8.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not (r.get("語彙配当") or "").strip().isdigit():
                continue   # 末尾の制御文字など
            g = TANAKA.get((r.get("田中") or "").strip())
            rec = (int(r["語彙配当"]), g)
            for key in {kana(r["見出し"]), kana(r["表記"] or "")} - {""}:
                kyo[key].append(rec)
    aoa = {}
    with open(os.path.join(src, "mochizuki_ota_2025_aoa", "data_AoA.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            aoa.setdefault(kana(r["Word"]), float(r["meanAoA"]))
    return kyo, aoa


def _aoa_band(a):
    return 1 if a < 3.5 else 2 if a < 4.5 else 3 if a < 5.5 else 4 if a < 6.5 else 5


def _is_loan(word):
    w = unicodedata.normalize("NFKC", word)
    return any("ァ" <= ch <= "ヶ" for ch in w)


def band(word, kyo, aoa):
    """(帯, 根拠) を返す。帯は BAND_LABEL のキー。照合できなければ (None, "")。"""
    k = kana(word)
    a = aoa.get(k)
    if k in kyo:
        recs = kyo[k]
        haito = min(r[0] for r in recs)
        grade = min((r[1] for r in recs if r[1]), default=None)
        if haito == 1:
            # 低学年配当のうち、AoA で幼児期（4–5歳以下）とされる語は「〜5歳」
            b = 1 if (a is not None and a < 3.5) else 2
        elif haito == 2:
            b = 3 if (grade and grade <= 4) else 4
        else:
            b = 5
        src = f"教育基本語彙 配当{haito}" + (f"・田中{grade}年" if grade else "") + (f"・AoA {a:.1f}" if a else "")
        # 古い語彙表は外来語や日常の具体物の配当が高い（例：サッカー・カレー）。AoA がより早い時期を示すときは AoA を採る
        if a is not None and _aoa_band(a) < b:
            b = _aoa_band(a)
            src += "（AoA を採用）"
        elif a is None and b >= 4 and _is_loan(word):
            src += "（外来語：古い語彙表による配当の可能性）"
        return b, src
    if a is not None:
        return _aoa_band(a), f"AoA {a:.1f}"
    return None, ""


def main(src):
    words = worksheet_words()
    kyo, aoa = load_norms(src)
    rows = []
    for w, tags in sorted(words.items()):
        b, why = band(w, kyo, aoa)
        rows.append((w, b, why, sorted(tags)))
    with open(os.path.join(OUT, "word_bands.tsv"), "w", encoding="utf-8") as f:
        f.write("語\t時期の目安\t根拠\t使っている課題とレベル\n")
        for w, b, why, tags in rows:
            f.write(f"{w}\t{BAND_LABEL.get(b, '照合できず')}\t{why}\t{' '.join(tags)}\n")
    # 課題・レベルごとの集計
    by = defaultdict(lambda: defaultdict(int))
    late = defaultdict(list)
    for w, b, why, tags in rows:
        for t in tags:
            by[t][b] += 1
            if b and b >= 4:
                late[t].append(f"{w}（{BAND_LABEL[b]}{'・外来語' if '外来語' in why else ''}）")
    out = ["# ワークシートの語と、語の時期の目安", "",
           "`python evaluation/lexical/word_check.py <語彙表のフォルダ>` で作る。語ごとの結果は `word_bands.tsv`。", "",
           "- 時期の目安は、国立国語研究所「教育基本語彙データベース」の語彙配当（1=小学校低学年／2=小学校高学年／3=中学校）と田中の指導学年を主に、",
           "  Mochizuki & Ota (2025) の獲得年齢評定（成人の評定）で補った。低学年配当で AoA 4–5歳以下の語を「〜5歳」とした。",
           "- 語彙表は語を「知っている子が多い時期」の目安で、個々の子どもが知っているかは分からない。古い語彙表に由来するずれがある（例：外来語の配当が高い）。",
           "- 古い語彙表は外来語や日常の具体物の配当が高いので、AoA がより早い時期を示すときは AoA を採った。",
           "  AoA のない外来語で配当が高いものには「外来語」と付けた（実際にはもっと早く知っている可能性が高い）。",
           "- 同音異義語は区別できないので、いちばん早い配当を採った。問題の見出し（関係名・カテゴリー名）も含む。", "",
           "## 課題・レベルごとの内訳（語の数）", "",
           "| 課題・レベル | " + " | ".join(BAND_LABEL.values()) + " | 照合できず | 10歳以降の語の割合 |",
           "|---|" + "---:|" * (len(BAND_LABEL) + 2)]
    order = [f"{t}{l}" for t in NAME for l in (1, 2, 3)]
    for t in order:
        if t not in by:
            continue
        c = by[t]
        n = sum(c.values())
        matched = n - c[None]
        lateshare = (c[4] + c[5]) / matched if matched else 0
        out.append(f"| {NAME[t[:-1]]} Lv{t[-1]} | " + " | ".join(str(c[b]) for b in BAND_LABEL) + f" | {c[None]} | {lateshare:.0%} |")
    out += ["", "## 10歳以降（小学校高学年・中学生以上）とされる語", ""]
    for t in order:
        if late.get(t):
            out.append(f"- **{NAME[t[:-1]]} Lv{t[-1]}**：" + "、".join(late[t]))
    total = len(rows)
    nomatch = sum(1 for r in rows if r[1] is None)
    out += ["", f"語の数：{total}（照合できず {nomatch}）", ""]
    with open(os.path.join(OUT, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(total, "words;", nomatch, "unmatched")


if __name__ == "__main__":
    main(sys.argv[1])
