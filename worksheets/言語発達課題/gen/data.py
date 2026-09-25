"""データ読込・サンプリング（seed固定・セット内重複なし・レベル絞り込み）。"""
import os
import yaml

ROMAN = {
    "I": "Ⅰ", "II": "Ⅱ", "III": "Ⅲ", "IV": "Ⅳ",
    "V": "Ⅴ", "VI": "Ⅵ", "VII": "Ⅶ", "VIII": "Ⅷ",
}

TEMPLATE_FILE = {
    "I": "I_chain",
    "II": "II_network",
    "III": "III_pairs",
    "IV": "IV_radial",
    "V": "V_chain_song",
    "VI": "VI_fluency",
    "VII": "VII_mora",
    "VIII": "VIII_venn",
}

TYPES = list(TEMPLATE_FILE.keys())


def load_config(base_dir="."):
    path = os.path.join(base_dir, "data", "config.yaml")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def load_items(type_key, base_dir="."):
    fname = TEMPLATE_FILE[type_key]
    path = os.path.join(base_dir, "data", "templates", f"{fname}.yaml")
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    items = doc.get("items", [])
    # id 必須（重複管理用）。無ければ連番付与。
    for i, it in enumerate(items):
        it.setdefault("id", f"{type_key}_{i}")
        it.setdefault("level", 1)
    return items


def build_pool(items, level, needed):
    """生成に使う item プールを決める。(pool, broadened) を返す。

    - level 未指定: 全件。
    - 指定レベルの item が needed 件以上ある: そのレベルのみ（難易度を厳守）。
    - 足りない: 全件に広げる（broadened=True）。データ自体が不足なら take 時にエラー。
    """
    if level is None:
        return list(items), False
    matched = [it for it in items if int(it.get("level", 1)) == int(level)]
    if len(matched) >= needed:
        return matched, False
    return list(items), True


class Sampler:
    """セット（または商品パック）内で重複しないよう抽出する。"""

    def __init__(self, items, rng):
        self._pool = list(items)
        self._rng = rng
        self._used = set()

    def take(self, k):
        avail = [it for it in self._pool if it["id"] not in self._used]
        if len(avail) < k:
            raise ValueError(
                f"データ不足: 必要 {k} 件に対し未使用 {len(avail)} 件。"
                f"data/templates の item を増やすか --count を下げてください。"
            )
        self._rng.shuffle(avail)
        chosen = avail[:k]
        for it in chosen:
            self._used.add(it["id"])
        return chosen
