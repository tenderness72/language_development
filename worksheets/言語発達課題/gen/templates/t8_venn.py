"""Ⅷ 属性交差（ベン図・自由記述 / 上下2問）。

重なる2円。上に交差条件ラベル、左円・右円にそれぞれ属性ラベル。
"""
from .. import layout
from .base import start_page

KEY = "VIII"
TITLE = "属性交差"                       # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "どんなものがあるかな"   # 子ども向け表示タイトル
INSTRUCTION = "左だけに合うもの、右だけに合うもの、両方に合うものを考えて書きましょう。"
HAS_ANSWER = False

CIRCLE_D = 58.0
LEFT_CX, RIGHT_CX = 85.0, 125.0
INTER_W, ATTR_W, TAG_H = 60.0, 42.0, 8.5


def _intersection(item):
    if item.get("intersection"):
        return item["intersection"]
    return f"{item['left_attr']}・{item['right_attr']}"


def _draw_problem(c, ctx, rtop, item):
    left_attr = item["left_attr"]
    right_attr = item["right_attr"]
    inter = _intersection(item)

    # 交差条件タグ（上中央）
    layout.box(c, 105 - INTER_W / 2, rtop + 2, INTER_W, TAG_H, r=3.0, line=0.9, fill=0.9)
    layout.text_fit(c, 105, rtop + 2 + TAG_H / 2, inter, INTER_W - 6, max_size=11,
                    font=layout.BOLD, ctx=ctx, where="VIII.inter")
    # 属性タグ
    layout.box(c, LEFT_CX - 5 - ATTR_W / 2, rtop + 15, ATTR_W, TAG_H, r=3.0, line=0.9)
    layout.text_fit(c, LEFT_CX - 5, rtop + 15 + TAG_H / 2, left_attr, ATTR_W - 6,
                    max_size=11, ctx=ctx, where="VIII.left")
    layout.box(c, RIGHT_CX + 5 - ATTR_W / 2, rtop + 15, ATTR_W, TAG_H, r=3.0, line=0.9)
    layout.text_fit(c, RIGHT_CX + 5, rtop + 15 + TAG_H / 2, right_attr, ATTR_W - 6,
                    max_size=11, ctx=ctx, where="VIII.right")
    # 2円
    cy = rtop + 56
    layout.circle(c, LEFT_CX, cy, CIRCLE_D, line=1.1)
    layout.circle(c, RIGHT_CX, cy, CIRCLE_D, line=1.1)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    tops = [body_y, body_y + 100]
    for n, (item, rtop) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, rtop, n)
        _draw_problem(c, ctx, rtop + 6, item)
        mani["problems"].append({
            "n": n, "id": item["id"], "left_attr": item["left_attr"],
            "right_attr": item["right_attr"], "intersection": _intersection(item),
        })
    return mani
