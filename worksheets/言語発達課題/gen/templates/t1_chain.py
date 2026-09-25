"""Ⅰ 連想チェーン（線つなぎ・正解あり / 上下2問）。

スタート語(角箱) → 中間3列(各列4語の楕円) → ゴール語(角箱)。
各列に正解1語＋ダミー3語。スタート→列2→列3→列4→ゴールが1本につながる。
"""
from .. import layout
from .base import start_page

KEY = "I"
TITLE = "連想チェーン"            # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "ことばつなぎ"    # 子ども向け表示タイトル（PDF上部・帯に使用）
INSTRUCTION = ("左のことばから始めて、関係が深いと思うことばを順番に線で結び、"
               "右のゴールまでつなげましょう。")
HAS_ANSWER = True

OVAL_W, OVAL_H = 30.0, 12.0
BOX_W, BOX_H = 24.0, 15.0
COL_SPAN = 78.0
COL_CX = [67.0, 105.0, 143.0]
START_CX, GOAL_CX = 27.0, 183.0
COL_LABELS = ["2列", "3列", "4列"]


def _place(correct, dummies, lrng):
    """4行に正解＋ダミー3を配置。(rows[4], correct_row) を返す。"""
    rows = [0, 1, 2, 3]
    lrng.shuffle(rows)
    cr = rows[0]
    arr = [None] * 4
    arr[cr] = correct
    for r, d in zip(rows[1:], dummies):
        arr[r] = d
    return arr, cr


def _draw_problem(c, ctx, top, item, lrng, answers):
    chain = item["chain"]            # [start, c2, c3, c4, goal]
    dis = item.get("distractors", {})
    vcenter = top + COL_SPAN / 2.0

    # 外枠（薄め）
    layout.box(c, layout.CONTENT_X, top - 3, layout.CONTENT_W, COL_SPAN + 14,
               r=2.0, line=0.5, fill=None)

    # スタート / ゴール角箱
    layout.box(c, START_CX - BOX_W / 2, vcenter - BOX_H / 2, BOX_W, BOX_H, r=2.0, line=1.0)
    layout.text_fit(c, START_CX, vcenter, chain[0], BOX_W - 4, max_size=14,
                    font=layout.BOLD, ctx=ctx, where="I.start")
    layout.box(c, GOAL_CX - BOX_W / 2, vcenter - BOX_H / 2, BOX_W, BOX_H, r=2.0, line=1.0)
    layout.text_fit(c, GOAL_CX, vcenter, chain[4], BOX_W - 4, max_size=14,
                    font=layout.BOLD, ctx=ctx, where="I.goal")

    cols = ["col2", "col3", "col4"]
    correct_centers = []
    for ci, cx in enumerate(COL_CX):
        correct = chain[ci + 1]
        dummies = list(dis.get(cols[ci], []))[:3]
        arr, cr = _place(correct, dummies, lrng)
        for k in range(4):
            cy = top + (k + 0.5) * COL_SPAN / 4.0
            layout.oval(c, cx, cy, OVAL_W, OVAL_H, line=0.8)
            layout.text_fit(c, cx, cy, arr[k], OVAL_W - 5, max_size=11,
                            ctx=ctx, where=f"I.col{ci+2}")
            if k == cr:
                correct_centers.append((cx, cy))
        # 列ラベル
        layout.text(c, cx, top + COL_SPAN + 5, COL_LABELS[ci], size=8.5,
                    font=layout.REG, align="c")

    if answers:
        pts = [(START_CX, vcenter)] + correct_centers + [(GOAL_CX, vcenter)]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            layout.line(c, x1, y1, x2, y2, width=1.3)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + COL_SPAN + 28]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, top - 8, n)
        _draw_problem(c, ctx, top, item, lrng, answers)
        mani["problems"].append({
            "n": n, "id": item["id"], "chain": item["chain"],
        })
    return mani
