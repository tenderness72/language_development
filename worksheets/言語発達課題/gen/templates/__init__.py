"""8テンプレートの登録。"""
from . import (
    t1_chain, t2_network, t3_pairs, t4_radial,
    t5_chain_song, t6_fluency, t7_mora, t8_venn,
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
}


def get(type_key):
    return REGISTRY[type_key]
