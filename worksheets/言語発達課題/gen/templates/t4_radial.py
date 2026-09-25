"""Ⅳ 放射状連想（マインドマップ・自由記述 / 左右2問）。

中央円の中心語、放射状に空の楕円8個。うち1個にヒント語を記入済み。
"""
import math

from .. import layout
from .base import start_page

KEY = "IV"
TITLE = "放射状連想"                          # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "思いつくことばを集めよう"    # 子ども向け表示タイトル
INSTRUCTION = ("まん中のことばから思いつくことばを、まわりの丸に書きましょう。"
               "1つはヒントとして書いてあります。")
HAS_ANSWER = False

HALF_CX = [60.0, 150.0]
MCY = 160.0
RX, RY = 31.0, 60.0
CENTER_D = 34.0
OVAL_W, OVAL_H = 26.0, 12.0


def _draw_problem(c, ctx, cx, item, lrng):
    center = item["center"]
    hint = item.get("hint")
    hint_pos = lrng.randrange(8)

    for i in range(8):
        rad = math.radians(90 - i * 45)
        ox = cx + RX * math.cos(rad)
        oy = MCY - RY * math.sin(rad)
        # 中心から各楕円へ細い放射線
        layout.line(c, cx, MCY, ox, oy, width=0.5, gray=0.45)
        layout.oval(c, ox, oy, OVAL_W, OVAL_H, line=0.8, fill=1.0)
        if hint and i == hint_pos:
            layout.text_fit(c, ox, oy, hint, OVAL_W - 5, max_size=11,
                            ctx=ctx, where="IV.hint")

    layout.circle(c, cx, MCY, CENTER_D, line=1.2, fill=1.0)
    layout.text_fit(c, cx, MCY, center, CENTER_D - 8, max_size=16,
                    font=layout.BOLD, ctx=ctx, where="IV.center")


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    for n, (item, cx) in enumerate(zip(items, HALF_CX), start=1):
        layout.problem_label(c, cx - 38, body_y + 6, n)
        _draw_problem(c, ctx, cx, item, lrng)
        mani["problems"].append({
            "n": n, "id": item["id"], "center": item["center"],
            "hint": item.get("hint"),
        })
    return mani
