"""Ⅵ カテゴリー流暢性（自由記述 / 左右2問）。

各問1カテゴリー。見出し(角ラベル)＋例語＋「それから…」＋記入罫線8〜10本。
"""
from .. import layout
from .base import start_page

KEY = "VI"
TITLE = "カテゴリー流暢性"                 # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "仲間をたくさん探そう"     # 子ども向け表示タイトル
INSTRUCTION = ("それぞれの仲間に入ることばを、できるだけたくさん書きましょう。"
               "はじめの1つは例です。")
HAS_ANSWER = False

# (列左端, 中心) — 問題1/問題2
COLS = [(19.0, 57.0), (111.0, 149.0)]
COL_W = 76.0
# 角ラベルは列幅(COL_W=76)いっぱい近くまで使い、長いカテゴリー名も収まるようにする
LABEL_W, LABEL_H = 72.0, 9.0
LINE_END_Y = 278.0


def _draw_problem(c, ctx, col_left, cx, top, item):
    category = item["category"]
    example = item.get("example", "")
    n_lines = int(item.get("lines", 10))

    # 角ラベル見出し
    layout.box(c, cx - LABEL_W / 2, top, LABEL_W, LABEL_H, r=3.0, line=0.9, fill=0.9)
    layout.text_fit(c, cx, top + LABEL_H / 2, category, LABEL_W - 6, max_size=12,
                    font=layout.BOLD, ctx=ctx, where="VI.label")
    # 例語
    if example:
        layout.text(c, cx, top + LABEL_H + 10, example, size=13, font=layout.REG,
                    align="c", vcenter=True)
    # それから…
    flow_y = top + LABEL_H + 18
    layout.text(c, col_left + 2, flow_y, "それから…", size=9.5, font=layout.REG, align="l")
    # 記入罫線
    start_y = flow_y + 8
    span = LINE_END_Y - start_y
    step = span / n_lines
    for i in range(1, n_lines + 1):
        y = start_y + i * step
        layout.line(c, col_left, y, col_left + COL_W, y, width=0.6, gray=0.35)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    for n, (item, (col_left, cx)) in enumerate(zip(items, COLS), start=1):
        layout.problem_label(c, col_left, body_y + 2, n)
        _draw_problem(c, ctx, col_left, cx, body_y + 12, item)
        mani["problems"].append({
            "n": n, "id": item["id"], "category": item["category"],
            "example": item.get("example", ""),
        })
    return mani
