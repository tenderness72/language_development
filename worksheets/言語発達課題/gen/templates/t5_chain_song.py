"""Ⅴ つづき歌（語連鎖・自由記述 / 左右2問）。

最上段に開始語の角箱、↓ と空の角箱を縦に並べる。
"""
from .. import layout
from .base import start_page

KEY = "V"
TITLE = "つづき歌"                      # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "つづき歌をつくろう"    # 子ども向け表示タイトル
INSTRUCTION = ("一番上のことばから始めて、前のことばと関係があることばを"
               "1つずつ続けて書きましょう。")
HAS_ANSWER = False

HALF_CX = [60.0, 150.0]
BOX_W, BOX_H = 58.0, 15.0
ARROW = 11.0
STEP = BOX_H + ARROW


def _draw_problem(c, ctx, cx, top0, item):
    start = item["start"]
    slots = int(item.get("slots", 5))
    n_boxes = slots + 1
    for k in range(n_boxes):
        top = top0 + k * STEP
        layout.box(c, cx - BOX_W / 2, top, BOX_W, BOX_H, r=2.0, line=1.0,
                   fill=(0.93 if k == 0 else None))
        if k == 0:
            layout.text_fit(c, cx, top + BOX_H / 2, start, BOX_W - 6, max_size=14,
                            font=layout.BOLD, ctx=ctx, where="V.start")
        if k < n_boxes - 1:
            layout.arrow_down(c, cx, top + BOX_H + 1.0, ARROW - 2.0)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    for n, (item, cx) in enumerate(zip(items, HALF_CX), start=1):
        layout.problem_label(c, cx - BOX_W / 2, body_y + 4, n)
        _draw_problem(c, ctx, cx, body_y + 12, item)
        mani["problems"].append({
            "n": n, "id": item["id"], "start": item["start"],
            "slots": int(item.get("slots", 5)),
        })
    return mani
