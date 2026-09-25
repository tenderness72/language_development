"""データ読込・サンプリング（seed固定・セット内重複なし・レベル絞り込み）。"""
import os
import unicodedata
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


def load_furigana(base_dir="."):
    """data/furigana.yaml（無ければ空）。キー: 描く文字列 → 値: 漢字《よみ》 形式。"""
    path = os.path.join(base_dir, "data", "furigana.yaml")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


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


# 重複判定に使う項目（問題の「中身」）。id が違っても中身が同じなら重複とみなす。
KEY_FIELDS = {
    "I": ("chain",),
    "II": ("center",),
    "III": ("relation",),
    "IV": ("center",),
    "V": ("start",),
    "VI": ("category",),
    "VII": ("initial",),
    "VIII": ("left_attr", "right_attr"),
}


def _normalize(s):
    """表記ゆれの吸収: NFKC＋カタカナ→ひらがな＋空白除去。"""
    s = unicodedata.normalize("NFKC", str(s))
    s = "".join(chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch for ch in s)
    return "".join(s.split())


def dedup_key(type_key, item):
    """問題の重複判定キー。

    item に `key:` があればそれを使う（漢字/かなの書き分けなど、自動では
    同一と判定できない語をまとめたいとき用。例: 文房具 と ぶんぼうぐ）。
    """
    if item.get("key"):
        return _normalize(item["key"])
    parts = []
    for f in KEY_FIELDS.get(type_key, ()):
        v = item.get(f, "")
        parts.append("/".join(map(_normalize, v)) if isinstance(v, list) else _normalize(v))
    return "|".join(parts) or str(item["id"])


def count_unique(type_key, items):
    return len({dedup_key(type_key, it) for it in items})


def build_pool(items, level, needed, type_key=None):
    """生成に使う item プールを決める。(pool, broadened) を返す。

    - level 未指定: 全件。
    - 指定レベルの item が needed 件以上ある: そのレベルのみ（難易度を厳守）。
    - 足りない: 全件に広げる（broadened=True）。データ自体が不足なら take 時にエラー。
    """
    if level is None:
        return list(items), False
    matched = [it for it in items if int(it.get("level", 1)) == int(level)]
    n = count_unique(type_key, matched) if type_key else len(matched)
    if n >= needed:
        return matched, False
    return list(items), True


class Sampler:
    """セット（または商品パック）内で重複しないよう抽出する。"""

    def __init__(self, items, rng, type_key=None):
        self._pool = list(items)
        self._rng = rng
        self._type_key = type_key
        self._used = set()

    def _key(self, it):
        return dedup_key(self._type_key, it) if self._type_key else it["id"]

    def take(self, k):
        avail = [it for it in self._pool if self._key(it) not in self._used]
        self._rng.shuffle(avail)
        chosen, keys = [], set()
        for it in avail:
            kk = self._key(it)
            if kk in keys:
                continue
            chosen.append(it)
            keys.add(kk)
            if len(chosen) == k:
                break
        if len(chosen) < k:
            raise ValueError(
                f"データ不足: 必要 {k} 件に対し未使用 {len(chosen)} 件。"
                f"data/templates の item を増やすか --count を下げてください。"
            )
        self._used |= keys
        return chosen
