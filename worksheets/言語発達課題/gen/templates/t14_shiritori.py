"""ⅩⅣ しりとり（音韻意識：語尾音の抽出と語の検索 / 左右2問）。

いちばん上に start のことば。その下に「おしまいの おと」の小さいマスと、ことばを書く箱をくり返す。
答えは1つに決まらないので解答面は作らない。
"""
from .. import layout
from .base import start_page

KEY = "XIV"
TITLE = "音韻意識（語尾音の抽出・しりとり）"   # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "しりとりをしよう"               # 子ども向け表示タイトル
INSTRUCTION = "おしまいの音を□に書いてから、その音で始まる言葉を書きましょう。「ん」で終わる言葉は、使いません。"
HAS_ANSWER = False

HALF_CX = [60.0, 150.0]
BOX_W, BOX_H = 56.0, 13.0
SQ = 10.0
STEP = 34.0


def _draw_problem(c, ctx, cx, top, item):
    layout.box(c, cx - BOX_W / 2, top, BOX_W, BOX_H, r=2.0, line=1.0, fill=0.93)
    layout.text_fit(c, cx, top + BOX_H / 2, item["start"], BOX_W - 6, max_size=15, font=layout.BOLD,
                    ctx=ctx, where="XIV.start")
    y = top + BOX_H
    for _ in range(int(item["steps"])):
        layout.arrow_down(c, cx, y + 1.0, 5.0)
        layout.text(c, cx - BOX_W / 2, y + 9.5, "おしまいの音《おと》", size=8, gray=0.35, vcenter=True)
        layout.grid_cell(c, cx - SQ / 2, y + 7.0, SQ)
        layout.arrow_down(c, cx, y + 7.0 + SQ + 0.5, 3.5)
        layout.box(c, cx - BOX_W / 2, y + 21.0, BOX_W, BOX_H, r=2.0, line=1.0)
        y += STEP


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    for n, (item, cx) in enumerate(zip(items, HALF_CX), start=1):
        layout.problem_label(c, cx - BOX_W / 2, body_y + 4, n)
        _draw_problem(c, ctx, cx, body_y + 12, item)
        mani["problems"].append({"n": n, "id": item["id"], "start": item["start"], "steps": int(item["steps"])})
    return mani
