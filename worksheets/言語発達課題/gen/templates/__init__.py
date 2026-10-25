"""テンプレートの登録（Ⅰ〜Ⅷ ＋ 書かない版 Ⅸ・Ⅹ ）。"""
from . import (
    t1_chain, t2_network, t3_pairs, t4_radial,
    t5_chain_song, t6_fluency, t7_mora, t8_venn,
    t9_category_choice, t10_venn_choice,
    t11_mora_count, t12_sound_search, t13_sound_manipulation, t14_shiritori,
)

REGISTRY = {
    "I": t1_chain,
    "II": t2_network,
    "III": t3_pairs,
    "IV": t4_radial,
    "V": t5_chain_song,
    "VI": t6_fluency,
    "VII": t7_mora,
    "VIII": t8_venn,
    "IX": t9_category_choice,
    "X": t10_venn_choice,
    "XI": t11_mora_count,
    "XII": t12_sound_search,
    "XIII": t13_sound_manipulation,
    "XIV": t14_shiritori,
}


def get(type_key):
    return REGISTRY[type_key]
