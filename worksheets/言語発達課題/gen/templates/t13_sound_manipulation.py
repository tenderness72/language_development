"""ⅩⅢ おとけし・ぎゃくよみ（音韻意識：音の削除・逆唱 / 1ページ8つ）。

「『さかな』を ぎゃくから いうと？」「『つくえ』から『つ』を とると？」の下に、こたえの音の数だけマス。
こたえは split_mora で作る（ぎゃく＝音を逆順、けす＝t を1つ除く）。解答面ではマスにこたえを書く。
"""
from .. import layout
from .base import start_page
from .t7_mora import split_mora

KEY = "XIII"
TITLE = "音韻意識（音の削除・逆唱）"     # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "音を消したり逆から言ったりしよう"   # 子ども向け表示タイトル
INSTRUCTION = "言葉を声に出して言ってから、答えを□に1つずつ書きましょう。"
HAS_ANSWER = True

SQ = 12.0
ROW_STEP = 25.0


def answer(entry):
    u = split_mora(entry["w"])
    if entry["op"] == "ぎゃく":
        return list(reversed(u))
    u = list(u)
    u.remove(entry["t"])
    return u


def question(entry):
    w = entry.get("disp") or layout.kanji(entry["w"])
    if entry["op"] == "ぎゃく":
        return f"「{w}」を逆《ぎゃく》から言《い》うと？"
    return f"「{w}」から「{entry['t']}」を取《と》ると？"


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    y = body_y + 8
    for n, item in enumerate(items, start=1):
        layout.problem_label(c, layout.CONTENT_X, y, n)
        y += 12
        res = []
        for e in item["entries"]:
            layout.text(c, layout.CONTENT_X + 2, y + SQ / 2, question(e), size=12, vcenter=True)
            ans = answer(e)
            x0 = 118.0
            for k, ch in enumerate(ans):
                layout.grid_cell(c, x0 + k * SQ, y, SQ)
                if answers:
                    layout.text(c, x0 + k * SQ + SQ / 2, y + SQ / 2, ch, size=13, align="c", vcenter=True, conv=False)
            res.append("".join(ans))
            y += ROW_STEP
        y += 2
        mani["problems"].append({"n": n, "id": item["id"], "answers": res})
    return mani
