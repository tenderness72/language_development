"""ⅩⅣ 音から言葉を集めよう（音を手がかりにした語の想起・自由回答 / 左右2問）。

見出しに「『か』から始まる言葉」「『こ』で終わる言葉」。その下に例を1つ、続く罫線に思いつく言葉を書く。
答えは1つに決まらないので解答面は作らない。
"""
from .. import layout
from .base import start_page

KEY = "XIV"
TITLE = "音韻（語頭音・語尾音を手がかりにした語の想起）"   # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "音から言葉を集めよう"                     # 子ども向け表示タイトル
INSTRUCTION = "決められた音から始まる（終わる）言葉を、書ける分だけ書いてみましょう。初めの1つは例です。"
HAS_ANSWER = False

HEAD = {"はじめ": "「{t}」から始まる言葉", "おしまい": "「{t}」で終わる言葉"}
COLS = [(19.0, 57.0), (111.0, 149.0)]
COL_W = 76.0
LABEL_W, LABEL_H = 72.0, 10.0
N_LINES = 8
LINE_END_Y = 270.0


def _draw_problem(c, ctx, col_left, cx, top, item):
    head = HEAD[item["position"]].format(t=item["target"])
    layout.box(c, cx - LABEL_W / 2, top, LABEL_W, LABEL_H, r=3.0, line=0.9, fill=0.9)
    layout.text_fit(c, cx, top + LABEL_H / 2, head, LABEL_W - 6, max_size=13, font=layout.BOLD,
                    ctx=ctx, where="XIV.head")
    layout.text(c, col_left + 2, top + LABEL_H + 6, "例《れい》", size=8.5, gray=0.45)
    layout.text_fit(c, cx, top + LABEL_H + 10, item["example"], COL_W - 20, max_size=13, ctx=ctx,
                    where="XIV.example")
    start_y = top + LABEL_H + 20
    step = (LINE_END_Y - start_y) / N_LINES
    for i in range(1, N_LINES + 1):
        y = start_y + i * step
        layout.line(c, col_left, y, col_left + COL_W, y, width=0.6, gray=0.35)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    for n, (item, (col_left, cx)) in enumerate(zip(items, COLS), start=1):
        layout.problem_label(c, col_left, body_y + 2, n)
        _draw_problem(c, ctx, col_left, cx, body_y + 12, item)
        mani["problems"].append({"n": n, "id": item["id"], "target": item["target"], "position": item["position"]})
    return mani
