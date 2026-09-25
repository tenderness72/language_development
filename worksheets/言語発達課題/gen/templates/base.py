"""テンプレート共通の小ヘルパ。"""
from .. import layout
from ..data import ROMAN


def start_page(c, type_key, display_title, instruction):
    """ヘッダー（名前・日付・区切り線）＋大問帯を描き、本文開始 y(mm) を返す。

    ページのタイトルは大問帯の「ローマ数字＋display_title」のみ
    （例「Ⅲ　ことばのペアをつくろう」）。「関連語の想起課題」や臨床名は出さない。
    """
    layout.page_header(c)
    y = layout.section_band(c, 36.0, ROMAN[type_key], display_title, instruction)
    return y
