"""ⅩⅧ 絵を見て文を作ろう（絵だけを手がかりに、二語文・三語文・四語文を自分で作る / 上下2問・1問1文）。

上に絵の枠、下に1文ぶんの枠（ⅩⅤ と同じ形とラベル）。語は1つも印刷せず、助詞（が・を・で・に）だけを印刷する。
絵は先生が用意した画像を data/images/ に置き、データの image: にファイル名を書く。ないときは枠だけを印刷する
（絵カードを貼るか、その場で描く）。解答面は、絵の枠に絵の内容（scene:）、文の枠に こたえの例 を書く。
"""
import os

from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm

from .. import layout
from .base import start_page
from .t15_sentence_build import SHAPE_H, draw_row, shape_width

KEY = "XVIII"
TITLE = "構文（絵からの文の生成）"     # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "絵を見て文を作ろう"  # 子ども向け表示タイトル
INSTRUCTION = "絵を見て、枠に合う言葉を考えて書き、文を作りましょう。"
HAS_ANSWER = True

IMAGE_DIR = os.path.join("data", "images")
PIC_W, PIC_H = 96.0, 64.0
PROBLEM_H = 112.0


def image_path(ctx, name):
    return os.path.join(getattr(ctx, "base_dir", "."), IMAGE_DIR, name)


def _picture(c, ctx, top, item, answers):
    x = layout.CONTENT_X + (layout.CONTENT_W - PIC_W) / 2
    layout.box(c, x, top, PIC_W, PIC_H, line=1.0)
    path = image_path(ctx, item.get("image", ""))
    if item.get("image") and os.path.isfile(path):
        pad = 2.0
        c.drawImage(ImageReader(path), layout._x(x + pad), layout._y(top + PIC_H - pad),
                    (PIC_W - 2 * pad) * mm, (PIC_H - 2 * pad) * mm,
                    preserveAspectRatio=True, anchor="c", mask="auto")
    else:
        missing = ctx.__dict__.setdefault("missing_images", [])
        if item.get("image") not in missing:
            missing.append(item.get("image"))
        if answers:   # 絵がないときは、解答面にだけ絵の内容を書く（問題面に書くと答えになる）
            layout.text(c, x + PIC_W / 2, top + PIC_H / 2, f"（絵：{item['scene']}）", size=9, align="c",
                        vcenter=True, gray=0.45, conv=False)


def _draw_problem(c, ctx, top, item, answers):
    _picture(c, ctx, top, item, answers)
    sent = item["sentence"]
    sw = shape_width([sent])
    total = len(sent) * sw + (len(sent) - 1) * 9.0
    x = layout.CONTENT_X + (layout.CONTENT_W - total) / 2
    # 助詞は全レベルで印刷する（ねらいは語を思い出して文にすること。助詞の選択は ⅩⅥ で扱う）
    draw_row(c, ctx, x, top + PIC_H + 8, sent, answers, lv=3, w=sw, where="XVIII.ans")
    if answers:
        layout.text(c, 195, top + PIC_H + 8 + 4 + SHAPE_H + 8, "こたえの例（絵に合う自然な文なら正答）", size=7.5,
                    align="r", gray=0.4)


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    tops = [body_y + 8, body_y + 8 + PROBLEM_H + 4]
    for n, (item, top) in enumerate(zip(items, tops), start=1):
        layout.problem_label(c, layout.CONTENT_X, top - 6, n)
        _draw_problem(c, ctx, top, item, answers)
        mani["problems"].append({"n": n, "id": item["id"], "image": item.get("image"),
                                 "sentence": " ".join(w for _, w in item["sentence"])})
    return mani
