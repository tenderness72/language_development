"""Ⅹ ベン図えらび（Ⅷ の書かない版・正解あり / 上下2問）。

中央に重なる2円（Lv2 は外側に「どちらでもない」の四角）。左右の列に語の箱を並べ、
語から合う場所へ線を引かせる。場所の名前（ひだりだけ・りょうほう・みぎだけ）を円の中に薄く書く。
解答面では、語から正しい場所へ線を引く。
"""
from .. import layout
from .base import start_page

KEY = "X"
TITLE = "属性交差（書かない版）"           # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "合うところへ線でむすぼう"   # 子ども向け表示タイトル
INSTRUCTION = "ことばを、合うところへ線でむすびましょう。"
INSTRUCTION_NONE = "ことばを、合うところへ線でむすびましょう。どちらにも合わないことばは、まるの外の四角へ。"
READ_NOTE = "字を読むのがたいへんなときは、大人が読んであげてもいいよ。"
HAS_ANSWER = True

CIRCLE_D = 58.0
LEFT_CX, RIGHT_CX = 85.0, 125.0
ATTR_W, TAG_H = 44.0, 8.5
WORD_W, WORD_H = 30.0, 10.0
WORD_CX = [30.0, 180.0]
RECT_X0, RECT_X1 = 52.0, 158.0
PROBLEM_H = 100.0


def _targets(cy):
    """各場所の、解答の線を引く先の点。none は語の列の側で変える。"""
    return {"left": (LEFT_CX - 15, cy - 9), "both": (105.0, cy - 12), "right": (RIGHT_CX + 15, cy - 9),
            "none": {0: (RECT_X0 + 5, cy - 26), 1: (RECT_X1 - 5, cy - 26)}}


def _draw_problem(c, ctx, top, item, lrng, answers):
    cy = top + 50
    has_none = bool(item.get("none"))
    # 属性タグ（円の上）
    for cx, attr in ((LEFT_CX - 10, item["left_attr"]), (RIGHT_CX + 10, item["right_attr"])):
        layout.box(c, cx - ATTR_W / 2, top, ATTR_W, TAG_H, r=3.0, line=0.9, fill=0.9)
        layout.text_fit(c, cx, top + TAG_H / 2, attr, ATTR_W - 5, max_size=11,
                        font=layout.BOLD, ctx=ctx, where="X.attr")
    if has_none:
        layout.box(c, RECT_X0, cy - 34, RECT_X1 - RECT_X0, 68, r=2.0, line=0.9)
        layout.text(c, RECT_X0 + 2.5, cy + 31, "どちらでもない", size=7.5, gray=0.45)
    layout.circle(c, LEFT_CX, cy, CIRCLE_D, line=1.1)
    layout.circle(c, RIGHT_CX, cy, CIRCLE_D, line=1.1)
    for x, lab in ((LEFT_CX - 15, "ひだりだけ"), (105.0, "りょうほう"), (RIGHT_CX + 15, "みぎだけ")):
        layout.text(c, x, cy + 1, lab, size=7.5, align="c", gray=0.45)

    regions = ["left", "both", "right"] + (["none"] if has_none else [])
    tagged = [(w, r) for r in regions for w in item[r]]
    lrng.shuffle(tagged)
    half = len(tagged) // 2
    tg = _targets(cy)
    for side, group in enumerate((tagged[:half], tagged[half:])):
        span = 18.0
        y0 = cy - span * (len(group) - 1) / 2
        for k, (w, r) in enumerate(group):
            wy = y0 + k * span
            wx = WORD_CX[side]
            layout.box(c, wx - WORD_W / 2, wy - WORD_H / 2, WORD_W, WORD_H, r=2.0, line=0.9)
            layout.text_fit(c, wx, wy, w, WORD_W - 4, max_size=11, ctx=ctx, where="X.word")
            if answers:
                ex = wx + (WORD_W / 2 if side == 0 else -WORD_W / 2)
                tx, ty = tg[r][side] if r == "none" else tg[r]
                layout.line(c, ex, wy, tx, ty, width=1.1)
                layout.circle(c, tx, ty, 1.6, line=0.5, fill=0.0)


def draw_page(c, ctx, items, lrng, answers=False):
    instr = INSTRUCTION_NONE if any(it.get("none") for it in items) else INSTRUCTION
    body_y = start_page(c, KEY, DISPLAY_TITLE, instr, note=READ_NOTE)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + PROBLEM_H + 10]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, top - 6, n)
        _draw_problem(c, ctx, top, item, lrng, answers)
        mani["problems"].append({"n": n, "id": item["id"], "left_attr": item["left_attr"],
                                 "right_attr": item["right_attr"],
                                 "answer": {r: item.get(r, []) for r in ("left", "both", "right", "none")}})
    return mani
