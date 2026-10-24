"""Ⅺ 経験とむすぼう（記号接地の段・自由記述 / 上下2問）。

左にことばの角箱、その下にチェック欄（見たことがある 等）と「どんなかんじ？」の欄。右に絵をかく枠。
kind（もの・うごき・ようす・きもち）でチェック欄と質問を変える。oto（オノマトペ）は薄い字で例として入れる。
"""
from .. import layout
from .base import start_page

KEY = "XI"
TITLE = "記号接地（経験・感覚・動作との結びつけ）"   # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "けいけんとむすぼう"                 # 子ども向け表示タイトル
INSTRUCTION = "ことばについて、じぶんが見たりさわったりしたことを思い出して、書ける分だけ書いてみましょう。"
HAS_ANSWER = False

# kind ごとのチェック欄と質問（左の列）。質問の行は oto があれば「おとでいうと」に薄い字で例を入れる。
CHECKS = {
    "もの": ["みたことがある", "さわったことがある", "つかったり たべたりしたことがある"],
    "うごき": ["みたことがある", "じぶんでしたことがある", "からだでやってみた"],
    "ようす": ["かんじたことがある", "そういうものをみたことがある"],
    "きもち": ["そういうきもちになったことがある"],
}
ROWS = {
    "もの": ["いろ・かたち", "おと", "におい", "さわったかんじ"],
    "うごき": ["どこでする？", "なにをつかう？", "おとでいうと", "そのときのきもち"],
    "ようす": ["そういうもの", "からだのどこでかんじる？", "おとでいうと", "そのときのきもち"],
    "きもち": ["どんなときになる？", "からだはどんなかんじ？", "かおはどうなる？", "にているきもちのことば"],
}
LEFT_X, LEFT_W = 15.0, 112.0
DRAW_X, DRAW_W = 132.0, 63.0
WORD_W, WORD_H = 56.0, 15.0
ROW_H = 11.0
PROBLEM_H = 104.0


def _draw_problem(c, ctx, top, item):
    kind = item["kind"]
    layout.box(c, LEFT_X, top, WORD_W, WORD_H, r=2.5, line=1.1, fill=0.93)
    layout.text_fit(c, LEFT_X + WORD_W / 2, top + WORD_H / 2, item["word"], WORD_W - 6, max_size=16,
                    font=layout.BOLD, ctx=ctx, where="XI.word")
    # チェック欄
    y = top + WORD_H + 5
    x = LEFT_X
    for lab in CHECKS[kind]:
        layout.box(c, x, y, 4.5, 4.5, line=0.8)
        layout.text(c, x + 6.0, y + 2.25, lab, size=9, vcenter=True)
        x += 8.0 + len(lab) * 3.3
    # 質問の行
    y += 10
    for lab in ROWS[kind]:
        layout.text(c, LEFT_X, y + ROW_H - 4.5, lab, size=8.5, gray=0.25)
        layout.line(c, LEFT_X + 40, y + ROW_H - 1.5, LEFT_X + LEFT_W, y + ROW_H - 1.5, width=0.6, gray=0.35)
        if lab == "おとでいうと" and item.get("oto"):
            layout.text(c, LEFT_X + 44, y + ROW_H - 7.0, f"（れい）{item['oto']}", size=10, gray=0.5)
        y += ROW_H
    # 絵をかく枠
    layout.box(c, DRAW_X, top, DRAW_W, PROBLEM_H - 22, r=2.0, line=0.8, dash=[2, 2])
    layout.text(c, DRAW_X + 2.5, top + 2.0, "えでかいてみよう", size=8.5, gray=0.45)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + PROBLEM_H + 6]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, top - 6, n)
        _draw_problem(c, ctx, top, item)
        mani["problems"].append({"n": n, "id": item["id"], "word": item["word"], "kind": item["kind"]})
    return mani
