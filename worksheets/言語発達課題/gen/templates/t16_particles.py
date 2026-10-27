"""ⅩⅥ じょしをいれよう（格助詞「が」「を」、Lv4 は「に」も / 1ページ8文）。

文の中の（　）に「が」か「を」を書く。Lv3 は文の上に状況の説明（だれがしているか）を出す。
解答面では（　）に助詞を書く。
"""
from reportlab.lib.units import mm

from .. import layout
from .base import start_page

KEY = "XVI"
TITLE = "構文（格助詞が・を）"         # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "助詞を入れよう"      # 子ども向け表示タイトル
INSTRUCTION = "（　）に「が」か「を」を書きましょう。"
# Lv4（に を加える）のページ。（　）に の「に」と答えの「に」が並ばないよう、選ぶ語を先に出す。
INSTRUCTION_NI = "「が」「を」「に」から1つ選んで、（　）に書きましょう。"
HAS_ANSWER = True

BLANK = 10.0
ROW_STEP = 26.0


def parse(part):
    """'(が)' → ('が', True)、'とり' → ('とり', False)。"""
    if part.startswith("(") and part.endswith(")"):
        return part[1:-1], True
    return part, False


def _sentence(c, ctx, y, sent, answers):
    if isinstance(sent, dict):
        layout.text(c, layout.CONTENT_X + 8, y - 2, sent["context"], size=10.5, gray=0.2)
        y += 7
        parts = sent["parts"]
    else:
        parts = sent
    x = layout.CONTENT_X + 8
    for p in parts:
        tok, is_blank = parse(p)
        if is_blank:
            layout.box(c, x + 1, y, BLANK, BLANK, line=1.0)
            if answers:
                layout.text(c, x + 1 + BLANK / 2, y + BLANK / 2, tok, size=14, align="c", vcenter=True)
            x += BLANK + 3
        else:
            layout.text(c, x, y + BLANK / 2, tok, size=15, vcenter=True)
            shown = layout.plain(layout.annotate(tok))   # 漢字表記にしたあとの幅で次の位置を決める
            x += layout.pdfmetrics.stringWidth(shown, layout.REG, 15) / mm + 2
    layout.text(c, x, y + BLANK / 2, "。", size=15, vcenter=True)


def draw_page(c, ctx, items, lrng, answers=False):
    ni = any(parse(p) == ("に", True) for it in items for st in it["sentences"]
             for p in (st["parts"] if isinstance(st, dict) else st))
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION_NI if ni else INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    y = body_y + 8
    for n, item in enumerate(items, start=1):
        layout.problem_label(c, layout.CONTENT_X, y, n)
        y += 12
        ans = []
        for sent in item["sentences"]:
            _sentence(c, ctx, y, sent, answers)
            parts = sent["parts"] if isinstance(sent, dict) else sent
            ans.append("".join(parse(p)[0] for p in parts))
            y += ROW_STEP
        y += 2
        mani["problems"].append({"n": n, "id": item["id"], "answers": ans})
    return mani
