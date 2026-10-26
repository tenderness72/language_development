"""Ⅸ 仲間えらび（Ⅵ の書かない版・正解あり / 上下2問）。

上にカテゴリー名の角ラベル、下に12語の楕円（仲間6＋仲間でない6）を4列×3行に並べる。
仲間に入る語を○でかこませる。解答面では仲間の語を太い楕円でかこむ。
"""
from .. import layout
from .base import start_page

KEY = "IX"
TITLE = "カテゴリー判断（流暢性の書かない版）"   # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "仲間に○を付けよう"            # 子ども向け表示タイトル
INSTRUCTION = "上の四角の仲間に入る言葉を見つけて、○で囲みましょう。"
HAS_ANSWER = True

LABEL_W, LABEL_H = 80.0, 10.0
COLS_CX = [37.5, 82.5, 127.5, 172.5]
OVAL_W, OVAL_H = 36.0, 13.0
ROW_STEP = 22.0
PROBLEM_H = 100.0


def _draw_problem(c, ctx, top, item, lrng, answers):
    layout.box(c, 105 - LABEL_W / 2, top, LABEL_W, LABEL_H, r=3.0, line=0.9, fill=0.9)
    layout.text_fit(c, 105, top + LABEL_H / 2, item["category"], LABEL_W - 8, max_size=14,
                    font=layout.BOLD, ctx=ctx, where="IX.label")
    tagged = [(w, True) for w in item["members"]] + [(w, False) for w in item["others"]]
    lrng.shuffle(tagged)
    for k, (w, is_mem) in enumerate(tagged):
        cx = COLS_CX[k % 4]
        cy = top + LABEL_H + 16 + (k // 4) * ROW_STEP
        layout.text_fit(c, cx, cy, w, OVAL_W - 6, max_size=13, ctx=ctx, where="IX.word")
        if answers and is_mem:
            layout.oval(c, cx, cy, OVAL_W, OVAL_H, line=1.8)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + PROBLEM_H + 10]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, top - 6, n)
        _draw_problem(c, ctx, top, item, lrng, answers)
        mani["problems"].append({"n": n, "id": item["id"], "category": item["category"],
                                 "members": item["members"]})
    return mani
