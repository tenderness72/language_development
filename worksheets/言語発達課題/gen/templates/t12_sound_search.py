"""Ⅻ おとさがし（音韻意識：音の抽出・同定 / 上下2問）。

見出しに「『か』ではじまることば」などの条件。下に6語の楕円（当たり3・はずれ3、順不同）。当たりを○でかこむ。
当たりは split_mora で判定する（はじめ＝最初の音、おしまい＝最後の音、どこか＝どこかに含む）。
"""
from .. import layout
from .base import start_page
from .t7_mora import split_mora

KEY = "XII"
TITLE = "音韻意識（音の抽出・同定）"     # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "音を探そう"           # 子ども向け表示タイトル
INSTRUCTION = "言葉を声に出して言ってみて、当てはまる言葉を○で囲みましょう。"
HAS_ANSWER = True

HEAD = {"はじめ": "「{t}」で始《はじ》まる言葉《ことば》", "おしまい": "「{t}」で終《お》わる言葉《ことば》",
        "どこか": "「{t}」が入《はい》っている言葉《ことば》"}
COLS_CX = [45.0, 105.0, 165.0]
OVAL_W, OVAL_H = 44.0, 15.0
PROBLEM_H = 100.0


def hit(word, target, position):
    u = split_mora(word)
    return {"はじめ": u[0] == target, "おしまい": u[-1] == target, "どこか": target in u}[position]


def _draw_problem(c, ctx, top, item, lrng, answers):
    head = HEAD[item["position"]].format(t=item["target"])
    layout.box(c, 105 - 50, top, 100, 11, r=3.0, line=0.9, fill=0.9)
    layout.text_fit(c, 105, top + 5.5, head, 94, max_size=14, font=layout.BOLD, ctx=ctx, where="XII.head")
    words = list(item["words"])
    lrng.shuffle(words)
    for k, w in enumerate(words):
        cx = COLS_CX[k % 3]
        cy = top + 30 + (k // 3) * 28
        layout.text_fit(c, cx, cy, w, OVAL_W - 8, max_size=15, ctx=ctx, where="XII.word")
        if answers and hit(w, item["target"], item["position"]):
            layout.oval(c, cx, cy, OVAL_W, OVAL_H, line=1.8)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + PROBLEM_H + 10]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, top - 6, n)
        _draw_problem(c, ctx, top, item, lrng, answers)
        mani["problems"].append({"n": n, "id": item["id"], "target": item["target"], "position": item["position"],
                                 "hits": [w for w in item["words"] if hit(w, item["target"], item["position"])]})
    return mani
