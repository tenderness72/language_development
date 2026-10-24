"""Ⅺ ことばをおぼえよう（語を覚える段・上に新しいことば2つ、下に前のページのことばの思い出し）。

新しいことば：ことば・いみ・れいぶん・絵をかく枠・自分のことで文をつくる行。
思い出し：前のページの2語について、いみを読み、3つのことば（前のページの2語＋このページの1語）から○で選ぶ。
最初のページには思い出しの欄の代わりに「つぎのページで思い出します」とだけ書く。解答面では正しい語を○でかこむ。
"""
from .. import layout
from .base import start_page

KEY = "XI"
TITLE = "語彙学習（定義・文脈・想起練習）"   # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "ことばをおぼえよう"          # 子ども向け表示タイトル
INSTRUCTION = "あたらしいことばの、いみとつかいかたをおぼえよう。下では、前のページのことばを思い出そう。"
HAS_ANSWER = True

WORD_W, WORD_H = 50.0, 15.0
LEARN_H = 82.0
DRAW_X, DRAW_W, DRAW_H = 150.0, 45.0, 40.0


def _text_left(c, ctx, x, y, s, max_w, max_size, where):
    """左寄せで、幅に収まるよう文字を小さくして描く（収まらなければ警告）。"""
    size, ok = layout.fit_size(s, layout.REG, max_size, max_w)
    if not ok:
        ctx.warnings.append(f"{where}: {s}")
    layout.text(c, x, y, s, size=size, align="l")


def _learn(c, ctx, top, item):
    layout.box(c, layout.CONTENT_X, top, WORD_W, WORD_H, r=2.5, line=1.1, fill=0.93)
    layout.text_fit(c, layout.CONTENT_X + WORD_W / 2, top + WORD_H / 2, item["word"], WORD_W - 6, max_size=17,
                    font=layout.BOLD, ctx=ctx, where="XI.word")
    x0 = layout.CONTENT_X
    y = top + WORD_H + 6
    for lab, txt in (("いみ", item["meaning"]), ("れい", item["example"])):
        layout.text(c, x0, y, lab, size=9, font=layout.BOLD, gray=0.3)
        _text_left(c, ctx, x0 + 11, y - 1.0, txt, 120, 11, "XI.text")
        y += 11
    layout.text(c, x0, y + 2, "じぶんのことで、このことばをつかって文をつくろう", size=9, gray=0.3)
    for k in range(2):
        layout.line(c, x0, y + 15 + k * 11, x0 + 130, y + 15 + k * 11, width=0.6, gray=0.35)
    layout.box(c, DRAW_X, top, DRAW_W, DRAW_H, r=2.0, line=0.8, dash=[2, 2])
    layout.text(c, DRAW_X + 2.5, top + 2.0, "えでかいてみよう", size=8.5, gray=0.45)


def _review(c, ctx, top, prev, cur, lrng, answers):
    layout.box(c, layout.CONTENT_X, top, layout.CONTENT_W, 0.1, line=0.6)
    layout.text(c, layout.CONTENT_X, top + 3, "前のページのことばを思い出そう（いみに合うことばに○）", size=10, font=layout.BOLD)
    if not prev:
        layout.text(c, layout.CONTENT_X, top + 12, "このページのことばは、つぎのページで思い出します。", size=9.5, gray=0.35)
        return
    options = [it["word"] for it in prev] + [cur[0]["word"]]
    lrng.shuffle(options)
    y = top + 13
    for it in prev:
        _text_left(c, ctx, layout.CONTENT_X, y - 1.0, "いみ：" + it["meaning"], 112, 10.5, "XI.review")
        for k, w in enumerate(options):
            cx = 133 + k * 22
            layout.text(c, cx, y + 2.5, w, size=11, align="c", vcenter=True)
            if answers and w == it["word"]:
                layout.oval(c, cx, y + 2.5, 21, 8.5, line=1.6)
        y += 14


def draw_page(c, ctx, items, lrng, answers=False):
    # 前のページの語は、この版（問題・解答）ごとに覚えておく。解答面は問題面と同じページ順で描かれる。
    hist = ctx.__dict__.setdefault("xi_hist", {})
    seq = hist.setdefault(answers, [])
    prev = seq[-1] if seq else None
    seq.append(items)
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    for n, item in enumerate(items):
        top = body_y + 8 + n * (LEARN_H + 6)
        layout.problem_label(c, layout.CONTENT_X, top - 6, n + 1)
        _learn(c, ctx, top, item)
        mani["problems"].append({"n": n + 1, "id": item["id"], "word": item["word"]})
    _review(c, ctx, body_y + 8 + 2 * (LEARN_H + 6), prev, items, lrng, answers)
    mani["review"] = [it["word"] for it in prev] if prev else []
    return mani
