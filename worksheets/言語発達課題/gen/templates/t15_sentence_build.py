"""ⅩⅤ ぶんをつくろう（二語文・三語文：語をならべる / 上下2問・1問3文）。

上に「言葉箱」（ふたの見える箱に、その問題の語のカードをまぜて並べる）。下に3文ぶんの枠。枠の形で役割を示す（Shape Coding のモノクロ版）：
だれが・なにが＝楕円、なにを＝四角、どうする＝六角形、どこで・なにで＝破線の角丸。枠の上に疑問語のラベル。
Lv3 は枠のあとに助詞（が・で・を）を印刷しておく。解答面では枠に語を書く（こたえの例）。
"""
from reportlab.lib.units import mm

from .. import layout
from .base import start_page

KEY = "XV"
TITLE = "構文（二語文・三語文の生成）"   # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "文を作ろう"          # 子ども向け表示タイトル
INSTRUCTION = "言葉箱の言葉を、合う枠に書いて、文を作りましょう。"
# 助詞を自分で書く版（products.yaml の variants で particle_blank: true）。枠のあとの□に が・を・で を書く。
INSTRUCTION_PARTICLE = "言葉箱の言葉を、合う枠に書いて、□に「が」「を」「で」を入れて、文を作りましょう。"
PBOX = 8.0
HAS_ANSWER = True

ROLES = ("だれが", "なにが", "なにを", "どうする", "どこで", "なにで")
PARTICLE = {"だれが": "が", "なにが": "が", "なにを": "を", "どこで": "で", "なにで": "で"}
SHAPE_W, SHAPE_H = 33.0, 13.0
GAP = 9.0
ROW_STEP = 25.0
PROBLEM_H = 112.0


def _poly(c, pts, fill=None, line=1.0):
    """左上原点(mm)の点列で閉じた多角形を描く。"""
    layout._set_line(c, line)
    if fill is not None:
        c.setFillGray(fill)
    p = c.beginPath()
    p.moveTo(layout._x(pts[0][0]), layout._y(pts[0][1]))
    for px, py in pts[1:]:
        p.lineTo(layout._x(px), layout._y(py))
    p.close()
    c.drawPath(p, stroke=1, fill=1 if fill is not None else 0)
    c.setFillGray(0.0)


def _hexagon(c, x, y, w, h):
    """左上(x,y)・幅w・高h の横長六角形。"""
    k = h / 2
    _poly(c, [(x + k, y), (x + w - k, y), (x + w, y + h / 2), (x + w - k, y + h), (x + k, y + h), (x, y + h / 2)])


BOX_DEPTH, BOX_H, CARD_H = 5.0, 17.0, 10.0


def _word_box(c, ctx, top, words):
    """言葉箱：ふたの見える箱（正面・上面・右側面）の正面に、語のカードを並べる。"""
    x, w = layout.CONTENT_X, layout.CONTENT_W - BOX_DEPTH
    d, h = BOX_DEPTH, BOX_H
    _poly(c, [(x, top + d), (x + d, top), (x + w + d, top), (x + w, top + d)], fill=0.85)      # 上面（ふた）
    _poly(c, [(x + w, top + d), (x + w + d, top), (x + w + d, top + h), (x + w, top + d + h)], fill=0.7)  # 右側面
    layout.box(c, x, top + d, w, h, line=1.0, fill=0.96)                                        # 正面
    layout.box(c, x + 2.5, top + d + 3.5, 22, 10, r=1.5, line=0.8, fill=0.25)                    # 名札
    c.setFillGray(1.0)
    layout.text(c, x + 13.5, top + d + 8.5, "言葉箱《ことばばこ》", size=9.5, align="c", vcenter=True, gray=1.0)
    c.setFillGray(0.0)
    # 語のカード
    widths = [max(13.0, len(layout.plain(layout.annotate(wd))) * 4.6 + 5) for wd in words]
    gap = 2.0
    avail = w - 30
    scale = min(1.0, avail / (sum(widths) + gap * (len(words) - 1)))
    cx = x + 28
    cy = top + d + (h - CARD_H) / 2
    for wd, cw in zip(words, widths):
        cw *= scale
        layout.box(c, cx, cy, cw, CARD_H, r=1.5, line=0.8, fill=1.0)
        layout.text_fit(c, cx + cw / 2, cy + CARD_H / 2 + 0.6, wd, cw - 2, max_size=12, ctx=ctx, where="XV.card")
        cx += cw + gap * scale


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
    _word_box(c, ctx, top, words)
    lv = int(item.get("level", 1))
    y = top + BOX_DEPTH + BOX_H + 7
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
            if role in PARTICLE and item.get("particle_blank"):
                bx, by = x + (GAP - PBOX) / 2, y + 4 + (SHAPE_H - PBOX) / 2
                layout.box(c, bx, by, PBOX, PBOX, line=0.9)
                if answers:
                    layout.text(c, bx + PBOX / 2, by + PBOX / 2, PARTICLE[role], size=12, align="c", vcenter=True)
            elif lv >= 3 and role in PARTICLE:
                layout.text(c, x + GAP / 2, y + 4 + SHAPE_H / 2, PARTICLE[role], size=13, align="c", vcenter=True)
            x += GAP
        y += ROW_STEP
    if answers:
        layout.text(c, 195, top + PROBLEM_H - 8, "こたえの例（ほかの組み合わせでも、自然な文なら正答）", size=7.5,
                    align="r", gray=0.4)


def draw_page(c, ctx, items, lrng, answers=False):
    instr = INSTRUCTION_PARTICLE if any(it.get("particle_blank") for it in items) else INSTRUCTION
    body_y = start_page(c, KEY, DISPLAY_TITLE, instr)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + PROBLEM_H + 4]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, top - 6, n)
        _draw_problem(c, ctx, top, item, lrng, answers)
        mani["problems"].append({"n": n, "id": item["id"],
                                 "sentences": [" ".join(w for _, w in s) for s in item["sentences"]]})
    return mani
