"""Ⅲ ペア対応づけ（1対1マッチング・正解あり / 上下2問）。

左5語・右6語（正解5語＋どれとも結ばない1語 `extra`）の角箱を1対1で結ぶ。
右に1語多いので、最後の1組が消去法で決まらない。右の並びはシャッフルする。
"""
from .. import layout
from .base import start_page

KEY = "III"
TITLE = "ペア対応づけ"                       # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "ことばのペアをつくろう"     # 子ども向け表示タイトル
INSTRUCTION = "左のことばと関係が深いことばを右から選んで、線で結びましょう。右には、あまることばが1つあります。"
HAS_ANSWER = True

BOX_W, BOX_H = 42.0, 12.0
LEFT_CX, RIGHT_CX = 48.0, 162.0
ROW_SPAN = 80.0
DOT_R = 1.0


def _row_y(top, k, n=5):
    return top + (k + 0.5) * ROW_SPAN / n


def _draw_problem(c, ctx, top, item, lrng, answers):
    pairs = list(item["pairs"])           # [[左,右], ...] ×5
    lefts = [p[0] for p in pairs]
    rights = [p[1] for p in pairs]
    shown = rights + ([item["extra"]] if item.get("extra") else [])
    nr = len(shown)

    order = list(range(nr))
    lrng.shuffle(order)
    right_shuffled = [shown[i] for i in order]      # 表示順
    pos_of = {w: idx for idx, w in enumerate(right_shuffled)}  # 右語→表示行

    for k in range(5):
        y = _row_y(top, k)
        # 左箱
        layout.box(c, LEFT_CX - BOX_W / 2, y - BOX_H / 2, BOX_W, BOX_H, r=1.5, line=0.9)
        layout.text_fit(c, LEFT_CX, y, lefts[k], BOX_W - 5, max_size=12,
                        ctx=ctx, where="III.left")
        layout.circle(c, LEFT_CX + BOX_W / 2, y, DOT_R * 2, line=0.5, fill=0.0)
    for k in range(nr):
        y = _row_y(top, k, nr)
        # 右箱
        layout.box(c, RIGHT_CX - BOX_W / 2, y - BOX_H / 2, BOX_W, BOX_H, r=1.5, line=0.9)
        layout.text_fit(c, RIGHT_CX, y, right_shuffled[k], BOX_W - 5, max_size=12,
                        ctx=ctx, where="III.right")
        layout.circle(c, RIGHT_CX - BOX_W / 2, y, DOT_R * 2, line=0.5, fill=0.0)

    if answers:
        for k in range(5):
            ly = _row_y(top, k)
            ry = _row_y(top, pos_of[rights[k]], nr)
            layout.line(c, LEFT_CX + BOX_W / 2, ly, RIGHT_CX - BOX_W / 2, ry, width=1.2)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + ROW_SPAN + 26]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        rel = item.get("relation", "")
        layout.problem_label(c, layout.CONTENT_X, top - 8, n)
        if rel:
            layout.text(c, layout.CONTENT_X + 26, top - 8, f"（{rel}）", size=9.5,
                        font=layout.REG, align="l")
        _draw_problem(c, ctx, top, item, lrng, answers)
        mani["problems"].append({
            "n": n, "id": item["id"], "relation": rel, "pairs": item["pairs"],
            "extra": item.get("extra"),
        })
    return mani
