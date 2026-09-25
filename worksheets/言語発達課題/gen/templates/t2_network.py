"""Ⅱ 意味ネットワーク照合（線結び・正解あり / 上下2問）。

中央に大きな円の中心語。左右に5語ずつ計10語の楕円（関連5＋ダミー5）。
関連語に線を引かせる。
"""
from .. import layout
from .base import start_page

KEY = "II"
TITLE = "意味ネットワーク照合"                  # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "関係のあることばを結ぼう"      # 子ども向け表示タイトル
INSTRUCTION = "まん中のことばと関係が深いものを、まわりのことばから選んで線で結びましょう。"
HAS_ANSWER = True

REGION_SPAN = 82.0
OVAL_W, OVAL_H = 30.0, 13.0
CIRCLE_D = 40.0
CENTER_CX = 105.0
LEFT_CX, RIGHT_CX = 42.0, 168.0


def _draw_problem(c, ctx, top, item, lrng, answers):
    center = item["center"]
    related = list(item["related"])
    dist = list(item["distractors"])
    vcenter = top + REGION_SPAN / 2.0

    # 周囲語（related/distractor をシャッフルし左右に5語ずつ）
    tagged = [(w, True) for w in related] + [(w, False) for w in dist]
    lrng.shuffle(tagged)
    left = tagged[:5]
    right = tagged[5:]

    related_pts = []
    for col_cx, group in ((LEFT_CX, left), (RIGHT_CX, right)):
        for k, (w, is_rel) in enumerate(group):
            cy = top + (k + 0.5) * REGION_SPAN / 5.0
            layout.oval(c, col_cx, cy, OVAL_W, OVAL_H, line=0.8)
            layout.text_fit(c, col_cx, cy, w, OVAL_W - 5, max_size=11,
                            ctx=ctx, where="II.word")
            if is_rel:
                edge = col_cx + (OVAL_W / 2 if col_cx < CENTER_CX else -OVAL_W / 2)
                related_pts.append((edge, cy))

    # 中心円
    layout.circle(c, CENTER_CX, vcenter, CIRCLE_D, line=1.2)
    layout.text_fit(c, CENTER_CX, vcenter, center, CIRCLE_D - 8, max_size=17,
                    font=layout.BOLD, ctx=ctx, where="II.center")

    if answers:
        for (x, y) in related_pts:
            ex = CENTER_CX + (-CIRCLE_D / 2 if x < CENTER_CX else CIRCLE_D / 2)
            layout.line(c, ex, vcenter, x, y, width=1.2)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + REGION_SPAN + 24]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, top - 8, n)
        _draw_problem(c, ctx, top, item, lrng, answers)
        mani["problems"].append({
            "n": n, "id": item["id"], "center": item["center"],
            "related": item["related"],
        })
    return mani
