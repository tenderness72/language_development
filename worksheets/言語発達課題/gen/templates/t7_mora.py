"""Ⅶ 語頭音＋モーラ数（音韻想起・解答例あり / 左右2問）。

各問に語頭音1つ。行は2音・3音・4音・5音。各行はモーラ数ぶんのマス目で、
先頭マスに語頭音を印字。--with-answers で語例を充填した解答面を出力。
"""
from .. import layout
from .base import start_page

KEY = "VII"
TITLE = "語頭音＋モーラ数"                        # 内部の臨床名（PDFには出さない）
# 子ども向け表示タイトル。問題ごとに語頭音が変わるため特定の音は入れず固定文言。
DISPLAY_TITLE = "決めた音からはじまることば"
INSTRUCTION = "決められた音から始まり、マスの数に合うことばを考えて書きましょう。"
# マスの書き方（1マス＝1拍）。拗音は2文字で1拍なので前の字と同じマスに入れる。
# 促音・長音・撥音はそれぞれ1拍＝1マス（原, 2001 の拍の定義に準拠）。
# レベル別の【マスの書き方】（ページ内の最も高いレベルに合わせて表示）
_FIXED_NOTE = "・はじめから書いてある字は、そのまま使ってことばを作ります。"
RULE_NOTES = {
    1: ["【マスの書き方】1マスに1つの音を書きます。"],
    2: ["【マスの書き方】1マスに1つの音を書きます。",
        "・「ん」と、のばす音（「くうき」の「う」、「ケーキ」の「ー」）は、それぞれ1マスです。",
        _FIXED_NOTE],
    3: ["【マスの書き方】1マスに1つの音を書きます。",
        "・小さい「ゃ・ゅ・ょ」は、前の字といっしょに1マスに書きます（例：「しゃ」で1マス）。",
        "・小さい「っ」、「ん」、のばす音は、それぞれ1マスです（例：「らっぱ」は3マス）。",
        _FIXED_NOTE],
}
RULE_NOTE = RULE_NOTES[3]
ANSWER_NOTE = "※解答は答えの例です。始まりの音とマスの数が合っていれば、ほかのことばも正解です。"
NOTE_Y = 205.0
HAS_ANSWER = True

# 問題1=左, 問題2=右
HALVES = [
    {"heading_cx": 59.0, "label_x": 19.0, "sq_x0": 31.0},
    {"heading_cx": 150.0, "label_x": 109.0, "sq_x0": 121.0},
]
MORA_ROWS = [2, 3, 4, 5]   # 既定の行。item の `moras:` で上書きできる（例: Lv1 は [2, 3, 4]）
SQ = 14.0
ROW_STEP = 30.0
SMALL = set("ゃゅょャュョぁぃぅぇぉァィゥェォ")


def split_mora(word):
    """かな語を簡易モーラ単位に分割（小さいゃゅょは前と結合）。"""
    units = []
    for ch in word:
        if ch in SMALL and units:
            units[-1] += ch
        else:
            units.append(ch)
    return units


def _draw_problem(c, ctx, half, top, item, answers):
    initial = item["initial"]
    ans = item.get("answers", {}) or {}
    layout.text(c, half["heading_cx"], top, f"「{initial}」から始まることば",
                size=12, font=layout.BOLD, align="c")

    rows_top = top + 12
    for i, mora in enumerate(item.get("moras") or MORA_ROWS):
        ry = rows_top + i * ROW_STEP
        layout.text(c, half["label_x"], ry + SQ / 2, f"{mora}音", size=10,
                    font=layout.REG, align="c", vcenter=True)
        for j in range(mora):
            cx = half["sq_x0"] + j * SQ
            layout.box(c, cx, ry, SQ, SQ, line=0.9)
        # 先頭マスに語頭音、fixed の位置に特殊音節（あらかじめ書いておく字）
        printed = {0: initial}
        printed.update({int(k): v for k, v in (item.get("fixed") or {}).get(mora, {}).items()})
        for j, ch in printed.items():
            layout.text_fit(c, half["sq_x0"] + j * SQ + SQ / 2, ry + SQ / 2, ch, SQ - 4,
                            max_size=13, font=layout.BOLD, ctx=ctx, where="VII.printed")
        if answers:
            examples = ans.get(mora) or ans.get(str(mora)) or []
            if examples:
                units = split_mora(examples[0])[:mora]
                for j, u in enumerate(units):
                    if j in printed:
                        continue
                    cx = half["sq_x0"] + j * SQ
                    layout.text_fit(c, cx + SQ / 2, ry + SQ / 2, u, SQ - 3,
                                    max_size=12, font=layout.REG,
                                    ctx=ctx, where="VII.ans")


def _draw_notes(c, answers, level=3):
    y = NOTE_Y
    for i, line in enumerate(RULE_NOTES.get(level, RULE_NOTE)):
        layout.text(c, layout.CONTENT_X, y, line, size=10,
                    font=layout.BOLD if i == 0 else layout.REG, align="l")
        y += 6.0
    if answers:
        layout.text(c, layout.CONTENT_X, y + 3.0, ANSWER_NOTE, size=10,
                    font=layout.BOLD, align="l")


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    _draw_notes(c, answers, max(int(it.get("level", 1)) for it in items))
    mani = {"type": KEY, "problems": []}
    for n, (item, half) in enumerate(zip(items, HALVES), start=1):
        layout.problem_label(c, half["label_x"] - 2, body_y + 2, n)
        _draw_problem(c, ctx, half, body_y + 14, item, answers)
        mani["problems"].append({
            "n": n, "id": item["id"], "initial": item["initial"],
            "moras": item.get("moras") or MORA_ROWS,
            "fixed": item.get("fixed") or {},
            "answers": item.get("answers", {}),
        })
    return mani
