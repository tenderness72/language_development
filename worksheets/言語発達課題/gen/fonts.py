"""フォント登録（Noto Sans JP / 商用利用可 SIL OFL 1.1）。

ネットワーク不使用。fonts/ 配下に同梱した静的TTFを埋め込む。
"""
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

REG = "NotoJP"        # 本文・楕円内など
BOLD = "NotoJP-B"     # タイトル・見出し

_DEFAULT = {
    "regular": "fonts/NotoSansJP-Regular.ttf",
    "bold": "fonts/NotoSansJP-Bold.ttf",
}
_registered = False


def register(font_cfg=None, base_dir="."):
    """Regular/Bold を登録。多重登録は無視。"""
    global _registered
    if _registered:
        return
    cfg = dict(_DEFAULT)
    if font_cfg:
        cfg.update({k: v for k, v in font_cfg.items() if v})
    reg_path = os.path.join(base_dir, cfg["regular"])
    bold_path = os.path.join(base_dir, cfg["bold"])
    for label, path in (("regular", reg_path), ("bold", bold_path)):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"日本語フォントが見つかりません ({label}): {path}\n"
                f"fonts/ に Noto Sans JP の静的TTFを配置してください。"
            )
    pdfmetrics.registerFont(TTFont(REG, reg_path))
    pdfmetrics.registerFont(TTFont(BOLD, bold_path))
    _registered = True
