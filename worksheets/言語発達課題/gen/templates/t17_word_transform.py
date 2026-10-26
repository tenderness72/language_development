"""ⅩⅦ ことばへんしん（音韻操作：指示どおりに音を変えて別のことばにする / 1ページ8つ）。

左に元のことば、まん中に指示、右にこたえの音の数だけマス。こたえは ops から自動で作る（apply_ops）。
2段階の指示は2行に分けて書く。解答面ではマスにこたえを書く。
"""
import unicodedata

from .. import layout
from .base import start_page
from .t7_mora import split_mora

KEY = "XVII"
TITLE = "音韻操作（指示に従って音を変える）"   # 内部の臨床名（PDFには出さない）
DISPLAY_TITLE = "ことばへんしん"                 # 子ども向け表示タイトル
INSTRUCTION = "ことばを声に出して言いながら、おとをかえて、べつのことばにしましょう。こたえを□に1つずつ書きます。"
HAS_ANSWER = True

SQ = 11.0
ROW_STEP = 25.0
WORD_W = 28.0


def _daku(ch, add):
    if add:
        return unicodedata.normalize("NFC", ch + "゙")
    return "".join(c for c in unicodedata.normalize("NFD", ch) if c not in "゙゚")


def apply_ops(word, ops):
    u = split_mora(word)
    for op in ops:
        (k, v), = op.items()
        if k == "rep_head":
            u = [v] + u[1:]
        elif k == "rep_tail":
            u = u[:-1] + [v]
        elif k == "rev":
            u = list(reversed(u))
        elif k == "add_head":
            u = split_mora(v) + u
        elif k == "add_tail":
            u = u + split_mora(v)
        elif k == "insert_mid":
            u = u[:1] + split_mora(v) + u[1:]
        elif k in ("daku_add", "daku_del"):
            u = list(u)
            u[int(v)] = _daku(u[int(v)], k == "daku_add")
        else:
            raise ValueError(f"不明な操作: {k}")
    return u


def _phrase(word, op, te=False):
    """指示の句。te=True なら「〜て」の形（2段階の指示の1つめ）。"""
    (k, v), = op.items()
    u = split_mora(word)
    base, verb = {
        "rep_head": (f"さいしょの おとを「{v}」に ", ("かえる", "かえて")),
        "rep_tail": (f"さいごの おとを「{v}」に ", ("かえる", "かえて")),
        "rev": ("ぎゃくから ", ("いう", "いって")),
        "add_head": (f"さいしょに「{v}」を ", ("つける", "つけて")),
        "add_tail": (f"さいごに「{v}」を ", ("つける", "つけて")),
        "insert_mid": (f"まんなかに「{v}」を ", ("いれる", "いれて")),
        "daku_add": (f"「{u[int(v)]}」に「゛」を " if k == "daku_add" else "", ("つける", "つけて")),
        "daku_del": (f"「{u[int(v)]}」の「゛」を " if k == "daku_del" else "", ("とる", "とって")),
    }[k]
    return base + verb[1 if te else 0]


def instruction_lines(entry):
    """指示の文（1行、2段階なら2行）。"""
    ops, w = entry["ops"], entry["w"]
    if len(ops) == 1:
        return [_phrase(w, ops[0]) + "と？"]
    # 2つめの操作は、1つめの結果のことばに対して行う
    mid = "".join(apply_ops(w, ops[:1]))
    return [_phrase(w, ops[0], te=True) + "、", "それから " + _phrase(mid, ops[1]) + "と？"]


def draw_page(c, ctx, items, lrng, answers=False):
    body_y = start_page(c, KEY, DISPLAY_TITLE, INSTRUCTION)
    mani = {"type": KEY, "problems": []}
    y = body_y + 8
    for n, item in enumerate(items, start=1):
        layout.problem_label(c, layout.CONTENT_X, y, n)
        y += 12
        res = []
        for e in item["entries"]:
            layout.box(c, layout.CONTENT_X, y, WORD_W, SQ, r=2.0, line=1.0, fill=0.93)
            layout.text_fit(c, layout.CONTENT_X + WORD_W / 2, y + SQ / 2, e["w"], WORD_W - 4, max_size=14,
                            font=layout.BOLD, ctx=ctx, where="XVII.word")
            lines = instruction_lines(e)
            for i, ln in enumerate(lines):
                dy = SQ / 2 if len(lines) == 1 else (SQ / 2 - 3.2 + i * 6.4)
                layout.text(c, layout.CONTENT_X + WORD_W + 4, y + dy, ln, size=10.5 if len(lines) == 1 else 9.5,
                            vcenter=True)
            ans = apply_ops(e["w"], e["ops"])
            x0 = 195.0 - len(ans) * SQ
            for k, ch in enumerate(ans):
                layout.grid_cell(c, x0 + k * SQ, y, SQ)
                if answers:
                    layout.text(c, x0 + k * SQ + SQ / 2, y + SQ / 2, ch, size=13, align="c", vcenter=True)
            res.append("".join(ans))
            y += ROW_STEP
        y += 2
        mani["problems"].append({"n": n, "id": item["id"], "answers": res})
    return mani
