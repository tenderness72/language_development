"""Ⅺ おとのかず（音韻意識：モーラの分解 / 1ページ8語）。

左にことば、右に○を7つ。ことばを声に出して言いながら、音の数だけ○をぬる（シールでもよい）。
解答面では、音の数だけ○を黒くぬる。音の数は t7_mora.split_mora で数える。
"""
from .. import layout
from .base import start_page
from .t7_mora import split_mora

KEY = "XI"
TITLE = "音韻意識（モーラの分解）"          # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "おとのかずだけ ぬろう"      # 子ども向け表示タイトル
INSTRUCTION = "ことばを声に出して言いながら、おとの数だけ○をぬりましょう。"
HAS_ANSWER = True

N_CIRCLES = 7
CIRCLE_D = 11.0
WORD_W = 52.0
ROW_STEP = 23.0


def _row(c, ctx, y, word, answers):
    layout.box(c, layout.CONTENT_X, y - 7, WORD_W, 14, r=2.5, line=1.0)
    layout.text_fit(c, layout.CONTENT_X + WORD_W / 2, y, word, WORD_W - 6, max_size=16,
                    font=layout.BOLD, ctx=ctx, where="XI.word")
    n = len(split_mora(word))
    for k in range(N_CIRCLES):
        cx = layout.CONTENT_X + WORD_W + 12 + k * (CIRCLE_D + 6)
        layout.circle(c, cx, y, CIRCLE_D, line=0.9, fill=(0.15 if answers and k < n else None))
    return n


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    y = body_y + 8
    for n, item in enumerate(items, start=1):
        layout.problem_label(c, layout.CONTENT_X, y, n)
        y += 14
        counts = []
        for w in item["words"]:
            counts.append(_row(c, ctx, y, w, answers))
            y += ROW_STEP
        y += 4
        mani["problems"].append({"n": n, "id": item["id"], "words": item["words"], "counts": counts})
    return mani
