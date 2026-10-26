"""Ⅴ つづき歌（語連鎖・自由記述 / 左右2問）。

最上段に開始語の角箱、↓ と空の角箱を縦に並べる。
item に example があれば、2番目の箱に手本の語を薄い字で入れ（破線の箱・「れい」の印）、
何を書けばよいか（前のことばと関係のあることば）を示す。
"""
from .. import layout
from .base import start_page

KEY = "V"
TITLE = "つづき歌"                      # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "つづき歌をつくろう"    # 子ども向け表示タイトル
INSTRUCTION = "一番上の言葉から始めて、矢印の横に書いてあるつなぎ方で、言葉を1つずつ書きましょう。2番目は、例です。"
# 矢印の横に出すつなぎ方（relation ごと）。こうたい は なかま から始めて交互にする。
LINK_LABEL = {"かんけい": "関係《かんけい》のある言葉《ことば》", "いっしょ": "一緒《いっしょ》にあるもの",
              "なかま": "同《おな》じ仲間《なかま》"}
HAS_ANSWER = False

HALF_CX = [60.0, 150.0]
BOX_W, BOX_H = 58.0, 15.0
ARROW = 11.0
STEP = BOX_H + ARROW


def _link(relation, k):
    """k 番目（0始まり）の矢印のつなぎ方。"""
    if relation == "こうたい":
        return LINK_LABEL["なかま" if k % 2 == 0 else "いっしょ"]
    return LINK_LABEL[relation]


def _draw_problem(c, ctx, cx, top0, item):
    start = item["start"]
    slots = int(item.get("slots", 5))
    n_boxes = slots + 1
    example = item.get("example")
    for k in range(n_boxes):
        top = top0 + k * STEP
        is_ex = example and k == 1
        layout.box(c, cx - BOX_W / 2, top, BOX_W, BOX_H, r=2.0, line=1.0,
                   fill=(0.93 if k == 0 else None), dash=([2, 2] if is_ex else None))
        if k == 0:
            layout.text_fit(c, cx, top + BOX_H / 2, start, BOX_W - 6, max_size=14,
                            font=layout.BOLD, ctx=ctx, where="V.start")
        if is_ex:
            layout.text_fit(c, cx, top + BOX_H / 2, example, BOX_W - 16, max_size=13,
                            ctx=ctx, where="V.example", gray=0.45)
            layout.text(c, cx - BOX_W / 2 + 2.5, top + 2.0, "れい", size=8, gray=0.45)
        if k < n_boxes - 1:
            layout.arrow_down(c, cx, top + BOX_H + 1.0, ARROW - 2.0)
            label = _link(item.get("relation", "かんけい"), k)
            layout.text(c, cx + 3.0, top + BOX_H + ARROW / 2 + 0.5, label, size=8, align="l",
                        vcenter=True, gray=0.3)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    for n, (item, cx) in enumerate(zip(items, HALF_CX), start=1):
        layout.problem_label(c, cx - BOX_W / 2, body_y + 4, n)
        _draw_problem(c, ctx, cx, body_y + 12, item)
        mani["problems"].append({
            "n": n, "id": item["id"], "start": item["start"],
            "slots": int(item.get("slots", 5)), "example": item.get("example"),
            "relation": item.get("relation", "かんけい"),
        })
    return mani
