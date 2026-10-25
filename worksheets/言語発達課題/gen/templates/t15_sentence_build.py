"""ⅩⅤ ぶんをつくろう（二語文・三語文：語をならべる / 上下2問・1問3文）。

上に「ことばばこ」（その問題の語をまぜて並べる）。下に3文ぶんの枠。枠の形で役割を示す（Shape Coding のモノクロ版）：
だれが・なにが＝楕円、なにを＝四角、どうする＝六角形、どこで・なにで＝破線の角丸。枠の上に疑問語のラベル。
Lv3 は枠のあとに助詞（が・で・を）を印刷しておく。解答面では枠に語を書く（こたえの例）。
"""
from reportlab.lib.units import mm

from .. import layout
from .base import start_page

KEY = "XV"
TITLE = "構文（二語文・三語文の生成）"   # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "ぶんをつくろう"          # 子ども向け表示タイトル
INSTRUCTION = "ことばばこの ことばを、合う わくに 書いて、ぶんを つくりましょう。"
HAS_ANSWER = True

ROLES = ("だれが", "なにが", "なにを", "どうする", "どこで", "なにで")
PARTICLE = {"だれが": "が", "なにが": "が", "なにを": "を", "どこで": "で", "なにで": "で"}
SHAPE_W, SHAPE_H = 33.0, 13.0
GAP = 9.0
ROW_STEP = 25.0
PROBLEM_H = 112.0


def _hexagon(c, x, y, w, h):
    """左上(x,y)・幅w・高h の横長六角形。"""
    k = h / 2
    pts = [(x + k, y), (x + w - k, y), (x + w, y + h / 2), (x + w - k, y + h), (x + k, y + h), (x, y + h / 2)]
    layout._set_line(c, 1.0)
    p = c.beginPath()
    p.moveTo(layout._x(pts[0][0]), layout._y(pts[0][1]))
    for px, py in pts[1:]:
        p.lineTo(layout._x(px), layout._y(py))
    p.close()
    c.drawPath(p, stroke=1, fill=0)


def _shape(c, role, x, y):
    if role in ("だれが", "なにが"):
        layout.box(c, x, y, SHAPE_W, SHAPE_H, r=SHAPE_H / 2, line=1.0)
    elif role == "なにを":
        layout.box(c, x, y, SHAPE_W, SHAPE_H, line=1.0)
    elif role == "どうする":
        _hexagon(c, x, y, SHAPE_W, SHAPE_H)
    else:
        layout.box(c, x, y, SHAPE_W, SHAPE_H, r=2.5, line=1.0, dash=[2, 2])


def _draw_problem(c, ctx, top, item, lrng, answers):
    words = [w for sent in item["sentences"] for _, w in sent]
    lrng.shuffle(words)
    layout.box(c, layout.CONTENT_X, top, layout.CONTENT_W, 12, r=2.5, line=0.8, fill=0.94)
    layout.text(c, layout.CONTENT_X + 3, top + 6, "ことばばこ", size=8.5, gray=0.35, vcenter=True)
    layout.text_fit(c, 117, top + 6, "　".join(words), layout.CONTENT_W - 30, max_size=12,
                    ctx=ctx, where="XV.bank")
    lv = int(item.get("level", 1))
    y = top + 20
    for k, sent in enumerate(item["sentences"]):
        x = layout.CONTENT_X + 8
        layout.text(c, layout.CONTENT_X, y + 4 + SHAPE_H / 2, f"{k + 1}.", size=10, vcenter=True)
        for role, w in sent:
            layout.text(c, x + SHAPE_W / 2, y, role, size=8, align="c", gray=0.35)
            _shape(c, role, x, y + 4)
            if answers:
                layout.text_fit(c, x + SHAPE_W / 2, y + 4 + SHAPE_H / 2, w, SHAPE_W - 5, max_size=12,
                                ctx=ctx, where="XV.ans")
            x += SHAPE_W
            if lv >= 3 and role in PARTICLE:
                layout.text(c, x + GAP / 2, y + 4 + SHAPE_H / 2, PARTICLE[role], size=13, align="c", vcenter=True)
            x += GAP
        y += ROW_STEP
    if answers:
        layout.text(c, 195, top + PROBLEM_H - 8, "こたえの例（ほかの組み合わせでも、自然な文なら正答）", size=7.5,
                    align="r", gray=0.4)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + PROBLEM_H + 4]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, top - 6, n)
        _draw_problem(c, ctx, top, item, lrng, answers)
        mani["problems"].append({"n": n, "id": item["id"],
                                 "sentences": [" ".join(w for _, w in s) for s in item["sentences"]]})
    return mani
