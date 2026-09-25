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
INSTRUCTION = ("決められた音から始まり、マスの数に合うことばを考えて書きましょう。"
               "小さい「ゃ・ゅ・ょ」は1マスに入れても構いません。")
HAS_ANSWER = True

# 問題1=左, 問題2=右
HALVES = [
    {"heading_cx": 59.0, "label_x": 19.0, "sq_x0": 31.0},
    {"heading_cx": 150.0, "label_x": 109.0, "sq_x0": 121.0},
]
MORA_ROWS = [2, 3, 4, 5]
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
    for i, mora in enumerate(MORA_ROWS):
        ry = rows_top + i * ROW_STEP
        layout.text(c, half["label_x"], ry + SQ / 2, f"{mora}音", size=10,
                    font=layout.REG, align="c", vcenter=True)
        for j in range(mora):
            cx = half["sq_x0"] + j * SQ
            layout.box(c, cx, ry, SQ, SQ, line=0.9)
        # 先頭マスに語頭音
        layout.text_fit(c, half["sq_x0"] + SQ / 2, ry + SQ / 2, initial, SQ - 4,
                        max_size=13, font=layout.BOLD, ctx=ctx, where="VII.initial")
        if answers:
            examples = ans.get(mora) or ans.get(str(mora)) or []
            if examples:
                units = split_mora(examples[0])[:mora]
                for j, u in enumerate(units):
                    cx = half["sq_x0"] + j * SQ
                    layout.text_fit(c, cx + SQ / 2, ry + SQ / 2, u, SQ - 3,
                                    max_size=12, font=layout.REG,
                                    ctx=ctx, where="VII.ans")


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    for n, (item, half) in enumerate(zip(items, HALVES), start=1):
        layout.problem_label(c, half["label_x"] - 2, body_y + 2, n)
        _draw_problem(c, ctx, half, body_y + 14, item, answers)
        mani["problems"].append({
            "n": n, "id": item["id"], "initial": item["initial"],
            "answers": item.get("answers", {}),
        })
    return mani
