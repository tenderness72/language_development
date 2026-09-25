"""共通レイアウト基盤。

座標はすべて「左上原点・mm」で扱い、内部で ReportLab（左下原点・pt）へ変換する。
モノクロ前提：色は使わず、線の太さ・破線・濃淡(グレー)のみで情報設計する。
"""
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics

from .fonts import REG, BOLD

PAGE_W, PAGE_H = A4  # pt (595.27 x 841.89)

# 余白（mm）
M_L, M_R, M_T, M_B = 15.0, 15.0, 14.0, 15.0
CONTENT_W = 210.0 - M_L - M_R   # 180 mm
CONTENT_X = M_L                 # 左端 15 mm

# CJK 文字の視覚的な縦中央補正係数（baseline = center より下へ size*係数）
_VC = 0.36


# ---- 座標変換 -------------------------------------------------------------
def _y(top_mm):
    """左上原点の縦位置(mm)を ReportLab の縦座標(pt)へ。"""
    return PAGE_H - top_mm * mm


def _x(left_mm):
    return left_mm * mm


# ---- テキスト -------------------------------------------------------------
def fit_size(s, font, max_size, max_w_mm, min_size=6.0, step=0.5):
    """幅 max_w_mm に収まる最大のフォントサイズを返す。(size, ok)。"""
    limit = max_w_mm * mm
    size = max_size
    while size > min_size and pdfmetrics.stringWidth(s, font, size) > limit:
        size -= step
    ok = pdfmetrics.stringWidth(s, font, size) <= limit
    return size, ok


# ---- ふりがな -------------------------------------------------------------
# data/furigana.yaml（キー: 描く文字列 → 値: 漢字《よみ》 形式）を set_furigana で登録すると、
# text() が描く文字列に自動でルビを付ける。未登録の漢字は MISSING_FURIGANA に記録する。
_FURI = {}
_FURI_BY_HEAD = {}
MISSING_FURIGANA = set()
RUBY_RATIO = 0.5          # ルビの大きさ（親文字比）
_RUBY_RE = re.compile(r"([^《》]+?)《([^》]*)》")


def set_furigana(mapping):
    _FURI.clear()
    _FURI_BY_HEAD.clear()
    _FURI.update(mapping or {})
    for k in sorted(_FURI, key=len, reverse=True):
        _FURI_BY_HEAD.setdefault(k[0], []).append(k)


def _is_kanji(ch):
    return "\u4e00" <= ch <= "\u9fff" or ch in "々〆"


def annotate(s):
    """文字列中の登録語を、いちばん長く一致するものから 漢字《よみ》 形式に置き換える。"""
    if not _FURI or "《" in s:
        return s
    out, i = [], 0
    while i < len(s):
        for k in _FURI_BY_HEAD.get(s[i], ()):
            if s.startswith(k, i):
                out.append(_FURI[k])
                i += len(k)
                break
        else:
            if _is_kanji(s[i]):
                MISSING_FURIGANA.add(s)
            out.append(s[i])
            i += 1
    return "".join(out)


def _segments(s):
    """'雨《あめ》の日《ひ》' -> [('雨','あめ'), ('の',None), ('日','ひ')]。親文字は直前の漢字列。"""
    segs, pos = [], 0
    for m in re.finditer(r"([\u4e00-\u9fff々〆]+)《([^》]*)》", s):
        if m.start() > pos:
            segs.append((s[pos:m.start()], None))
        segs.append((m.group(1), m.group(2)))
        pos = m.end()
    if pos < len(s):
        segs.append((s[pos:], None))
    return segs


def plain(s):
    """ルビ注記を除いた文字列。"""
    return re.sub(r"《[^》]*》", "", s)


def text(c, x_mm, y_mm, s, size=11, font=REG, align="l", vcenter=False, gray=0.0):
    """文字を描画。align: l/c/r。vcenter=True なら y_mm を縦中央とみなす。

    ふりがな辞書に登録された語には、自動でルビ（親文字の上）を付ける。
    """
    c.setFillGray(gray)
    c.setFont(font, size)
    yb = _y(y_mm)
    if vcenter:
        yb -= size * _VC
    else:
        yb -= size  # y_mm を上端とみなしてベースラインを下げる
    segs = _segments(annotate(s))
    if any(r for _, r in segs):
        _draw_ruby_line(c, _x(x_mm), yb, segs, size, font, align, vcenter)
        c.setFillGray(0.0)
        return
    if align == "c":
        c.drawCentredString(_x(x_mm), yb, s)
    elif align == "r":
        c.drawRightString(_x(x_mm), yb, s)
    else:
        c.drawString(_x(x_mm), yb, s)
    c.setFillGray(0.0)


def _draw_ruby_line(c, x, yb, segs, size, font, align, vcenter):
    """ルビ付きの1行を描く。親文字の幅を基準に配置し、ルビはその上に中央揃え。"""
    if vcenter:
        yb -= size * 0.14        # ルビ分だけ親文字を下げ、全体として縦中央に見せる
    widths = [pdfmetrics.stringWidth(b, font, size) for b, _ in segs]
    total = sum(widths)
    x0 = x - total / 2 if align == "c" else (x - total if align == "r" else x)
    rfont = REG
    for (base, ruby), w in zip(segs, widths):
        c.setFont(font, size)
        c.drawString(x0, yb, base)
        if ruby:
            rs = size * RUBY_RATIO
            # ルビが親文字より大きくはみ出すときは縮める（最小で親文字の 0.38 倍）
            limit = w + size * 0.4
            while rs > size * 0.38 and pdfmetrics.stringWidth(ruby, rfont, rs) > limit:
                rs -= 0.25
            rw = pdfmetrics.stringWidth(ruby, rfont, rs)
            c.setFont(rfont, rs)
            c.drawString(x0 + (w - rw) / 2, yb + size * 0.9, ruby)
        x0 += w
    c.setFont(font, size)


def text_fit(c, cx_mm, cy_mm, s, max_w_mm, max_size=12, min_size=6.0,
             font=REG, ctx=None, where=""):
    """枠(幅 max_w_mm)の中央(cx,cy)に収まるよう自動縮小して描画。

    最小サイズでも収まらなければ ctx.warnings に記録（QAで検出）。
    """
    size, ok = fit_size(s, font, max_size, max_w_mm, min_size)
    if not ok and ctx is not None:
        ctx.warnings.append(f"overflow: {s!r} ({where}) max_w={max_w_mm}mm")
    text(c, cx_mm, cy_mm, s, size=size, font=font, align="c", vcenter=True)
    return size, ok


# ---- 図形 -----------------------------------------------------------------
def _set_line(c, width=0.8, dash=None, gray=0.0):
    c.setLineWidth(width)
    c.setStrokeGray(gray)
    c.setDash(dash if dash else [])


def box(c, x_mm, y_mm, w_mm, h_mm, r=0.0, line=0.8, fill=None, dash=None):
    """左上(x,y)・幅w・高hの矩形（r>0で角丸）。"""
    _set_line(c, line, dash)
    xb = _x(x_mm)
    yb = _y(y_mm + h_mm)  # 下端
    if fill is not None:
        c.setFillGray(fill)
    stroke = 1 if line else 0
    do_fill = 1 if fill is not None else 0
    if r > 0:
        c.roundRect(xb, yb, w_mm * mm, h_mm * mm, r * mm, stroke=stroke, fill=do_fill)
    else:
        c.rect(xb, yb, w_mm * mm, h_mm * mm, stroke=stroke, fill=do_fill)
    c.setFillGray(0.0)
    c.setDash([])


def oval(c, cx_mm, cy_mm, w_mm, h_mm, line=0.8, fill=None, dash=None):
    """中心(cx,cy)・幅w・高hの楕円。"""
    _set_line(c, line, dash)
    x1 = _x(cx_mm - w_mm / 2)
    x2 = _x(cx_mm + w_mm / 2)
    y1 = _y(cy_mm - h_mm / 2)
    y2 = _y(cy_mm + h_mm / 2)
    if fill is not None:
        c.setFillGray(fill)
    c.ellipse(x1, y1, x2, y2,
              stroke=1 if line else 0, fill=1 if fill is not None else 0)
    c.setFillGray(0.0)
    c.setDash([])


def circle(c, cx_mm, cy_mm, d_mm, line=0.8, fill=None, dash=None):
    oval(c, cx_mm, cy_mm, d_mm, d_mm, line=line, fill=fill, dash=dash)


def line(c, x1, y1, x2, y2, width=0.8, dash=None, gray=0.0):
    _set_line(c, width, dash, gray)
    c.line(_x(x1), _y(y1), _x(x2), _y(y2))
    c.setDash([])
    c.setStrokeGray(0.0)


def hrule(c, y_mm, width=1.4, x0=None, x1=None):
    x0 = CONTENT_X if x0 is None else x0
    x1 = (210.0 - M_R) if x1 is None else x1
    line(c, x0, y_mm, x1, y_mm, width=width)


def arrow_down(c, x_mm, y_top, length, width=0.9, head=2.2):
    """下向き矢印。x_mm を中心、y_top から length mm。"""
    line(c, x_mm, y_top, x_mm, y_top + length, width=width)
    _set_line(c, width)
    yb = _y(y_top + length)
    c.line(_x(x_mm), yb, _x(x_mm - head), _y(y_top + length - head))
    c.line(_x(x_mm), yb, _x(x_mm + head), _y(y_top + length - head))


def grid_cell(c, x_mm, y_mm, side, line=0.9):
    """マス目1個（左上 x,y・正方形 side）。"""
    box(c, x_mm, y_mm, side, side, line=line)


# ---- ヘッダー・大問帯 -----------------------------------------------------
def page_header(c):
    """名前(左)・日付(右)・太い区切り線。タイトルは大問帯側に出す。

    返り値は使用していないが、帯は section_band(c, 36.0, ...) で描く前提。
    """
    # 名前 / 日付
    text(c, M_L, 18.0, "名前：＿＿＿＿＿＿＿＿＿＿", size=11, font=REG, align="l")
    text(c, 210.0 - M_R, 18.0, "日付：＿＿＿＿年＿＿月＿＿日", size=11, font=REG, align="r")
    # 太線
    hrule(c, 27.0, width=1.4)
    return 36.0


def section_band(c, y_mm, roman, title, instruction):
    """角丸帯（ローマ数字＋タイトル）＋直下の指示文。返り値: 本文開始 y(mm)。"""
    band_h = 8.5
    box(c, CONTENT_X, y_mm, CONTENT_W, band_h, r=2.5, line=0.9, fill=0.92)
    text(c, CONTENT_X + 4.0, y_mm + band_h / 2, f"{roman}　{title}",
         size=13, font=BOLD, align="l", vcenter=True)
    instr_y = y_mm + band_h + 4.5
    text(c, CONTENT_X, instr_y, instruction, size=9.5, font=REG, align="l")
    # 本文（「問題1」見出しとそのふりがな）が教示文に重ならないよう間をあける
    return instr_y + 7.0


def problem_label(c, x_mm, y_mm, n):
    """「問題1 / 問題2」見出し。"""
    text(c, x_mm, y_mm, f"問題{n}", size=11, font=BOLD, align="l")


class Ctx:
    """描画中の警告（はみ出し等）を集約する文脈。"""

    def __init__(self, titles=None):
        self.titles = titles or {}
        self.warnings = []
