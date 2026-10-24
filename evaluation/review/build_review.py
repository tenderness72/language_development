"""修正確認ページ（review.html）を生成する。

データ（YAML）と生成済みPDFから確認項目と見本画像を作り、1枚のHTMLに埋め込む。
判定（承認/要修正/保留）とコメントは、公開ページの共有DB（collection: reviews）に保存される。
  python evaluation/review/build_review.py
"""
import base64
import html
import json
import os

import pymupdf
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WS = os.path.join(ROOT, "worksheets", "言語発達課題")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review.html")


def load(name):
    with open(os.path.join(WS, "data", "templates", name), encoding="utf-8") as f:
        return {it["id"]: it for it in yaml.safe_load(f)["items"]}


_DIRS = {"I": "01_連想チェーン", "II": "02_意味ネットワーク照合", "III": "03_ペア対応づけ", "IV": "04_放射状連想",
         "V": "05_つづき歌", "VI": "06_カテゴリー流暢性", "VII": "07_語頭音とモーラ数", "VIII": "08_属性交差ベン図",
         "IX": "09_仲間えらび", "X": "10_ベン図えらび"}


def sheet(k, level, answers=False):
    """プリント/ の中の、課題 k・レベル level の PDF（相対パス）。"""
    d = _DIRS[k]
    return f"プリント/{d}/Lv{level}/{d}_Lv{level}_{'解答' if answers else '問題'}.pdf"


def page_png(pdf, page_no, dpi=62):  # noqa: E302
    doc = pymupdf.open(os.path.join(WS, pdf))
    png = doc[page_no - 1].get_pixmap(dpi=dpi).tobytes("png")
    return "data:image/png;base64," + base64.b64encode(png).decode()


II = load("II_network.yaml")
V = load("V_chain_song.yaml")
I, III, IV, VI, VII, VIII = (load(n) for n in (
    "I_chain.yaml", "III_pairs.yaml", "IV_radial.yaml", "VI_fluency.yaml",
    "VII_mora.yaml", "VIII_venn.yaml"))


# レビューで削除した問題（過去の確認項目の表示用に、削除前の内容を残す）
III.setdefault("vehicle_place", {"id": "vehicle_place", "relation": "のりもの→走るところ（2026-10-21 削除）", "level": 1,
                                 "pairs": [["でんしゃ", "せんろ"], ["ふね", "うみ"], ["ひこうき", "そら"], ["くるま", "どうろ"], ["そり", "ゆきのうえ"]],
                                 "extra": "うちゅう"})
VIII.setdefault("long_animal", {"id": "long_animal", "left_attr": "長いもの", "right_attr": "どうぶつ",
                                "intersection": "長いどうぶつ（2026-10-21 削除）", "level": 2})
VIII.setdefault("white_animal", {"id": "white_animal", "left_attr": "白いもの", "right_attr": "どうぶつ",
                                 "intersection": "白いどうぶつ（2026-10-21 白い花 に変更）", "level": 2})


I.setdefault("rain_use", {"id": "rain_use", "_stub": True, "chain": ["雨", "ふる", "かさ", "さす", "使う"], "level": 1,
                          "distractors": {"col2": ["はしる", "わらう", "ねむる"], "col3": ["バナナ", "とけい", "ボール"], "col4": ["たべる", "およぐ", "うたう"]}})


def pairs(it):
    return "、".join(f"{a}→{b}" for a, b in it["pairs"])


def chain(it):
    d = it["distractors"]
    return ("正解：" + " → ".join(it["chain"])
            + f"\nダミー 2列：{'・'.join(d['col2'])}／3列：{'・'.join(d['col3'])}／4列：{'・'.join(d['col4'])}")


# 各項目: id（DBのdoc id）, 見出し, 修正前, 修正後, 確認してほしい点
SECTIONS = [
    {
        "key": "safety", "title": "Ⅳ Lv3 ヒント文（安全上の差し替え）",
        "lead": "感情・社会的な語のヒントを、子どもの安全教育と矛盾せず、家庭環境を前提にしないものに差し替えました。",
        "items": [
            {"id": "iv-hint-trust", "label": "信頼", "before": "秘密を守る", "after": IV["iv_lv3_012"]["hint"],
             "ask": "「いやな秘密は話してよい」という安全教育と矛盾しないか"},
            {"id": "iv-hint-relief", "label": "安心", "before": "家族", "after": IV["iv_lv3_004"]["hint"],
             "ask": "家庭で安心できない子どもにも書ける手がかりになっているか"},
            {"id": "iv-hint-regret", "label": "後悔", "before": "あのときこうすれば", "after": IV["iv_lv3_019"]["hint"],
             "ask": "自責の反すうより、次に向かう方向づけになっているか"},
            {"id": "iv-hint-patience", "label": "我慢", "before": "気持ちを抑える", "after": IV["iv_lv3_014"]["hint"],
             "ask": "感情の抑圧を良いこととして示す含意が消えているか"},
        ],
    },
    {
        "key": "pairs", "title": "Ⅲ ペア対応づけ",
        "lead": "事実誤り・語として不自然なもの・音の規則だけで解ける組・正解が1対1にならない組を直しました。",
        "items": [
            {"id": "iii-animal-home", "label": "動物→すみか",
             "before": "とり→す、はち→すばこ、くも→くもの巣、かい→から、きつね→あな",
             "after": pairs(III["animal_home"]), "ask": "すみかとして事実に合っているか、1対1で決まるか"},
            {"id": "iii-part-use", "label": "体→はたらき",
             "before": "目→みる、耳→きく、鼻→におう、口→たべる、手→つかむ",
             "after": pairs(III["part_use"]), "ask": "「かぐ」への修正でよいか"},
            {"id": "iii-animal-baby", "label": "生き物→こども（旧: 動物→こども）",
             "before": "いぬ→こいぬ、ねこ→こねこ、うし→こうし、うま→こうま、ライオン→こライオン",
             "after": pairs(III["animal_baby"]), "ask": "対象年齢に対して語が難しすぎないか（やご、もんしろちょう）"},
            {"id": "iii-tool-action", "label": "道具→すること（旧: 楽器→鳴らし方）",
             "before": "たいこ→たたく、ふえ→ふく、ギター→はじく、ピアノ→おす、すず→ふる",
             "after": pairs(III["tool_action"]),
             "ask": "楽器の題材を外してよいか（5つの楽器に別々の鳴らし方を1対1で当てられないため差し替え）"},
            {"id": "iii-vehicle-place", "label": "のりもの→走るところ（旧: 天気→持ち物）",
             "before": "雨→かさ、雪→手袋、晴れ→ぼうし、風→ウインドブレーカー、くもり→うわぎ",
             "after": pairs(III["vehicle_place"]), "ask": "天気の題材を外してよいか、Lv1として妥当か"},
            {"id": "iii-season", "label": "季節・時期→もの（関係名のみ変更）",
             "before": "季節→もの（春・夏・秋・冬・梅雨）", "after": "季節・時期→もの（" + pairs(III["season_thing"]) + "）",
             "ask": "梅雨を含めるための関係名の変更でよいか"},
        ],
    },
    {
        "key": "chain", "title": "Ⅰ 連想チェーン",
        "lead": "事実誤りと、ダミー語を通っても筋が通ってしまう経路（正解が一つに決まらない問題）を直しました。",
        "items": [
            {"id": "i-rain", "label": "雨（旧 rain_use）", "before": "正解：雨 → ふる → かさ → さす → 使う（ゴールが汎用動詞）",
             "after": chain(I["rain_boots"]), "ask": "つながりが自然か"},
            {"id": "i-tree", "label": "木（旧 tree_paper）", "before": "正解：木 → きる → 板 → けずる → 紙（紙の作り方として誤り）",
             "after": chain(I["tree_blocks"]), "ask": "ダミー（いし・てつ・ガラス 等）を通る別経路がないか"},
            {"id": "i-grape", "label": "ぶどう（旧 grape_wine）", "before": "正解：ぶどう → つむ → しぼる → おく → ジュース（「おく→ジュース」が不成立）",
             "after": chain(I["grape_sherbet"]), "ask": "ダミー（たね・かわ・にる 等）を通る別経路がないか"},
            {"id": "i-cloud", "label": "くも（ダミー差し替え）", "before": "ダミー 2列：ちぢむ・かたまる・きえる／4列：かわく・もえる・こおる\n（くも→きえる→はれ→かわく→タオル が成立してしまう）",
             "after": chain(I["cloud_umbrella"]), "ask": "別経路が残っていないか（にじ・はれ を含めて）"},
            {"id": "i-rice", "label": "米（ダミー差し替え）", "before": "ダミー 2列：あらう・なげる・ほる／4列：きる・やく・ゆでる\n（米→あらう、ごはん→やく→おにぎり が成立しうる）",
             "after": chain(I["rice_onigiri"]), "ask": "別経路が残っていないか"},
        ],
    },
    {
        "key": "mora", "title": "Ⅶ 語頭音＋モーラ数",
        "lead": "教示を正しくし、マスの書き方と「解答は例」であることをページ下部に明記しました。",
        "items": [
            {"id": "vii-instruction", "label": "教示文とマスの書き方",
             "before": "決められた音から始まり、マスの数に合うことばを考えて書きましょう。小さい「ゃ・ゅ・ょ」は1マスに入れても構いません。",
             "after": ("決められた音から始まり、マスの数に合うことばを考えて書きましょう。\n"
                       "【マスの書き方】1マスに1つの音を書きます。\n"
                       "・小さい「ゃ・ゅ・ょ」は、前の字といっしょに1マスに書きます（例：「きゃ」で1マス）。\n"
                       "・小さい「っ」、のばす音、「ん」は、それぞれ1マスです（例：「らっぱ」「ケーキ」「みかん」はどれも3マス）。"),
             "ask": "子どもと保護者に伝わる言い方か、例は適切か"},
            {"id": "vii-answer-note", "label": "解答PDFの注記",
             "before": "（注記なし。各マス数に語例を1つだけ表示）",
             "after": "※解答は答えの例です。始まりの音とマスの数が合っていれば、ほかのことばも正解です。",
             "ask": "言い回しは適切か"},
            {"id": "vii-examples", "label": "不自然な解答例の差し替え",
             "before": "き・5音：きりんさん／と・4音：とらのこ",
             "after": "き・5音：きりぎりす／と・4音：とびばこ", "ask": "語として適切か"},
        ],
    },
    {
        "key": "venn", "title": "Ⅷ 属性交差（ベン図）",
        "lead": "片方の属性がもう片方をほぼ含み、「右だけ」の領域が空になる組を差し替えました。",
        "items": [
            {"id": "viii-soft-eat", "label": "Lv2 の差し替え",
             "before": "小さいもの ／ むし（両方：小さいむし）",
             "after": "{0} ／ {1}（両方：{2}）".format(VIII["soft_eat"]["left_attr"], VIII["soft_eat"]["right_attr"], VIII["soft_eat"]["intersection"]),
             "ask": "3つの領域すべてに答えがあり、Lv2として妥当か"},
        ],
    },
    {
        "key": "removed", "title": "削除した重複",
        "lead": "同じ中心語・カテゴリー（表記ゆれを含む）がレベル内・レベル間で重複していたものを削除しました。残した側のレベルが妥当かを見てください。",
        "items": [
            {"id": "dup-iv", "label": "Ⅳ 放射状連想（9件削除）",
             "before": "Lv2 から削除：公園/すべり台、病院/先生、海/波、誕生日/ケーキ、駅/電車、冬/雪、朝/目覚まし、雨の日/かさ、お正月/おもち",
             "after": "Lv1 に残す：海・冬・誕生日・公園　／　Lv2 に残す：病院/薬・駅/電車・朝/朝ごはん・雨/かさ・お正月/おもち",
             "ask": "残した側のレベルとヒントでよいか"},
            {"id": "dup-vi", "label": "Ⅵ カテゴリー流暢性（16件削除）",
             "before": ("Lv2 から削除：文房具、スポーツ（サッカー）、天気、色、野菜、魚、虫、花（さくら）、食べ物、飲み物、乗り物、"
                        "体の部分、国、鳥、果物、職業"),
             "after": ("Lv1 に残す：やさい・色・たべもの・のみもの・のりもの・くだもの　／　Lv2 に残す：ぶんぼうぐ・スポーツ（やきゅう）・"
                       "さかな・むし・花（チューリップ）・からだのぶぶん・とり　／　Lv3 に残す：お天気・国・しごと"),
             "ask": "とくに「お天気」「国」「しごと」を Lv3 に残す判断でよいか"},
        ],
    },
]

new_iv = [it for k, it in IV.items() if k.startswith("iv_lv2_0") and int(k[-3:]) >= 21]
new_vi = [it for k, it in VI.items() if k.startswith("vi_lv2_0") and len(k) == 10 and int(k[-3:]) >= 21]
SECTIONS.append({
    "key": "new-iv", "title": "新規追加：Ⅳ 放射状連想 Lv2（10問）",
    "lead": "重複を削除して不足した Lv2 の補充です。身近な場所・行事から選びました。中心語とヒントを見てください。",
    "items": [{"id": "new-" + it["id"].replace("_", "-"), "label": it["center"], "before": "",
               "after": f"中心語：{it['center']}　ヒント：{it['hint']}", "ask": ""} for it in new_iv],
})
SECTIONS.append({
    "key": "new-vi", "title": "新規追加：Ⅵ カテゴリー流暢性 Lv2（16問）",
    "lead": "同じく Lv2 の補充です。身近で具体的なカテゴリーから選びました。カテゴリー名と例の語を見てください。",
    "items": [{"id": "new-" + it["id"].replace("_", "-"), "label": it["category"], "before": "",
               "after": f"カテゴリー：{it['category']}　例：{it['example']}", "ask": ""} for it in new_vi],
})

# ---- 第2回：不足レベルの補充（先頭に表示） ----
def added(d, prefix_or_ids):
    return [it for k, it in d.items() if (k in prefix_or_ids if isinstance(prefix_or_ids, set) else k.startswith(prefix_or_ids))]


ROUND2 = [
    {
        "key": "r2-iv", "title": "追加：Ⅳ 放射状連想 Lv1（10問）",
        "lead": "Lv1 パック（9枚＝18問）に足りなかった分です。身近な具体物・季節から選びました。",
        "items": [{"id": "r2-" + it["id"].replace("_", "-"), "label": it["center"], "before": "",
                   "after": f"中心語：{it['center']}　ヒント：{it['hint']}", "ask": ""} for it in added(IV, "iv_lv1_")],
    },
    {
        "key": "r2-vi", "title": "追加：Ⅵ カテゴリー流暢性 Lv1（8問）",
        "lead": "Lv1 パック（7枚＝14問）に足りなかった分です。生活の場面で使う、具体的なカテゴリーにしました。",
        "items": [{"id": "r2-" + it["id"].replace("_", "-"), "label": it["category"], "before": "",
                   "after": f"カテゴリー：{it['category']}　例：{it['example']}", "ask": ""} for it in added(VI, "vi_lv1_")],
    },
    {
        "key": "r2-vii", "title": "追加：Ⅶ 語頭音＋モーラ数 Lv1（11問）",
        "lead": "音韻パック（Lv1）には該当する問題がありませんでした。Lv1 は直音の語だけで作れる語頭音にし、マスを2〜4音にしています（Lv2・3 は従来どおり2〜5音）。語例は解答PDFに出る「答えの例」です。",
        "items": [{"id": "r2-" + it["id"].replace("_", "-"), "label": "「" + it["initial"] + "」から始まることば", "before": "",
                   "after": "　".join(f"{k}音：{'・'.join(v)}" for k, v in it["answers"].items()),
                   "ask": "直音だけの語として適切か、年少の子どもになじみのある語か"} for it in added(VII, "_lv1") or
                  [x for k, x in VII.items() if k.endswith("_lv1")]],
    },
    {
        "key": "r2-iii", "title": "追加：Ⅲ ペア対応づけ Lv1（4問）",
        "lead": "ペアパック（Lv1、5枚＝10問）に足りなかった分です。意味の上でも1対1に決まる組にしました。",
        "items": [{"id": "r2-iii-" + it["id"].replace("_", "-"), "label": it["relation"], "before": "",
                   "after": pairs(it), "ask": "1対1で決まるか、Lv1として妥当か"}
                  for it in added(III, {"body_wear", "opposite_adj", "worker_place", "animal_move"})],
    },
    {
        "key": "r2-viii", "title": "追加：Ⅷ 属性交差 Lv2（6問）",
        "lead": "ベン図パック（Lv2、6枚＝12問）に足りなかった分です。左だけ・右だけ・両方の3領域すべてに答えがある組にしました。",
        "items": [{"id": "r2-viii-" + it["id"].replace("_", "-"), "label": it["intersection"], "before": "",
                   "after": f"{it['left_attr']} ／ {it['right_attr']}（両方：{it['intersection']}）",
                   "ask": "3つの領域すべてに答えがあるか"}
                  for it in added(VIII, {"hard_eat", "square_school", "long_animal", "white_animal", "hot_drink", "sound_toy"})],
    },
]
for sec in SECTIONS:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND2

# ---- 第3回：Ⅵ の課題の型とレベルの整理（先頭に表示） ----
def vi(i):
    return VI[i]


ROUND3 = [
    {
        "key": "r3-vi-remove", "title": "Ⅵ から外したもの（課題の型が違う・語を探す課題にならない）",
        "lead": "対の語を作る課題はⅢへ移し、成員が少数に決まっている閉じた集合は削除しました。",
        "items": [
            {"id": "r3-vi-pair-tasks", "label": "反対の意味のことば／似た意味のことば（Lv3）",
             "before": "Ⅵ Lv3 のカテゴリーとして出題（1行に1語）",
             "after": "Ⅵ から削除し、Ⅲ ペア対応づけに「反対のことば（うごき）」Lv2・「似た意味のことば」Lv3 を新設",
             "ask": "仲間集めではなく対の語の課題として扱う判断でよいか"},
            {"id": "r3-vi-closed-sets", "label": "季節（例：夏）／月（例：1月）（Lv2）",
             "before": "Ⅵ Lv2 のカテゴリーとして出題", "after": "削除（成員が4つ・12個に決まっていて、語を探す課題にならない）",
             "ask": "削除でよいか"},
        ],
    },
    {
        "key": "r3-vi-relevel", "title": "Ⅵ のレベル変更",
        "lead": "国立国語研究所（1981）の連想語彙の集計と、課題の性質に合わせて付け直しました。",
        "items": [
            {"id": "r3-vi-sounds", "label": "動物の鳴き声", "before": "Lv2", "after": "Lv1（擬音語で易しい）", "ask": ""},
            {"id": "r3-vi-furniture", "label": "家具", "before": "Lv2",
             "after": "Lv3（上位語として難しい。連想語彙表の集計で小1でも約半数が無反応）", "ask": ""},
            {"id": "r3-vi-action-words", "label": "動作を表すことば", "before": "Lv2",
             "after": "Lv3（ことばの種類そのものを考えるメタ言語的な課題）", "ask": ""},
            {"id": "r3-vi-size-words", "label": "大きさを表すことば", "before": "Lv2", "after": "Lv3（同上）", "ask": ""},
        ],
    },
    {
        "key": "r3-vi-adult", "title": "Ⅵ Lv3 の大人向けの語の差し替え",
        "lead": "子どもの生活から離れたカテゴリー・例を、子どもが考えられるものに替えました。",
        "items": [
            {"id": "r3-vi-energy", "label": "カテゴリーの差し替え①", "before": "エネルギーに関係することば（例：太陽）",
             "after": f"{vi('vi_lv3_009b')['category']}（例：{vi('vi_lv3_009b')['example']}）", "ask": "Lv3 として妥当か"},
            {"id": "r3-vi-social-rule", "label": "カテゴリーの差し替え②", "before": "社会のルールに関係することば（例：法律）",
             "after": f"{vi('vi_lv3_017a')['category']}（例：{vi('vi_lv3_017a')['example']}）",
             "ask": "「ルールがあるもの」「約束が必要なもの」「マナー」と重なっていたため差し替え。Lv3 として妥当か"},
            {"id": "r3-vi-salary", "label": "例の差し替え", "before": "働くことに関係することば（例：給料）／お金に関係することば（例：給料）",
             "after": f"働くことに関係することば（例：{vi('vi_lv3_011a')['example']}）／お金に関係することば（例：{vi('vi_lv3_016a')['example']}）",
             "ask": "例として適切か"},
        ],
    },
    {
        "key": "r3-vi-new", "title": "追加：Ⅵ Lv2（6問）",
        "lead": "Lv2 から外した分の補充です。身近な場所・料理などの具体的なカテゴリーにしました。",
        "items": [{"id": "r3-" + it["id"].replace("_", "-"), "label": it["category"], "before": "",
                   "after": f"カテゴリー：{it['category']}　例：{it['example']}", "ask": ""}
                  for k, it in VI.items() if k in {f"vi_lv2_{n:03d}" for n in range(37, 43)}],
    },
    {
        "key": "r3-iii-new", "title": "追加：Ⅲ ペア対応づけ（Ⅵ から移した対の語の課題）",
        "lead": "意味の上でも1対1に決まる組にしました。",
        "items": [{"id": "r3-iii-" + k.replace("_", "-"), "label": III[k]["relation"] + f"（Lv{III[k]['level']}）", "before": "",
                   "after": pairs(III[k]), "ask": "1対1で決まるか、レベルは妥当か"} for k in ("opposite_verb", "synonym")],
    },
]
for sec in ROUND2:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND3

# ---- 第4回：Ⅳ Lv3 の整理（先頭に表示） ----
_hint_changes = [("友だち", "一緒に遊ぶ"), ("挑戦", "新しいこと"), ("平和", "争わない"), ("信頼", "約束を守る"),
                 ("我慢", "順番を待つ"), ("思いやり", "気にかける"), ("成長", "練習"), ("責任", "約束")]
_iv_by_center = {it["center"]: it for it in IV.values()}
ROUND4 = [
    {
        "key": "r4-iv-move", "title": "Ⅳ 属性で集める語を Lv3 → Lv2 へ",
        "lead": "Lv3 に混ざっていた「赤いもの」などの属性で集める語を、Ⅵ（赤いもの・冷たいもの は Lv2）と同じ扱いにして Lv2 へ移しました。Lv3 は抽象語・感情語だけになります。",
        "items": [{"id": "r4-iv-move", "label": "Lv2 へ移した6問", "before": "Lv3",
                   "after": "Lv2：赤いもの・丸いもの・あたたかいもの・音がするもの・はやいもの・やわらかいもの",
                   "ask": "属性で集める語を Lv2 とする判断でよいか"}],
    },
    {
        "key": "r4-iv-hint", "title": "Ⅳ Lv3 ヒントを1語に（重複も解消）",
        "lead": "文になっていたヒントを1語にしました。「練習」「約束」が2つの中心語で重なっていたので、片方を替えています。",
        "items": [{"id": "r4-iv-hint-" + str(n), "label": c, "before": old, "after": _iv_by_center[c]["hint"], "ask": ""}
                  for n, (c, old) in enumerate(_hint_changes)]
                 + [{"id": "r4-iv-hint-regret", "label": "後悔（変更せず）", "before": "次はこうしたい",
                     "after": "次はこうしたい（1語の候補「はんせい」は自責につながりうるため、前回承認の言い方を残しました）",
                     "ask": "このまま残すか、1語（例：はんせい）にするか"}],
    },
    {
        "key": "r4-iv-new", "title": "追加：Ⅳ Lv3（6問）",
        "lead": "Lv3 パック（13枚＝26問）を Lv3 の語だけで作るための補充です。前向きな抽象語を選びました。",
        "items": [{"id": "r4-" + k.replace("_", "-"), "label": it["center"], "before": "",
                   "after": f"中心語：{it['center']}　ヒント：{it['hint']}", "ask": ""}
                  for k, it in IV.items() if k in {f"iv_lv3_{n:03d}" for n in range(21, 27)}],
    },
]
for sec in ROUND3:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND4

# ---- 第5回：Ⅶ Lv2・Lv3 を特殊音節で段階化（先頭に表示） ----
def _vii_after(it):
    return "　".join(f"{k}音：{'・'.join(v)}" for k, v in it["answers"].items())


_r5_lv2 = [it for it in VII.values() if it["level"] == 2]
_r5_lv3 = [it for it in VII.values() if it["level"] == 3]
ROUND5 = [
    {
        "key": "r5-vii-design", "title": "Ⅶ レベルの作り方（特殊音節で段階化）",
        "lead": "解答例を替えるだけでは子どもが取り組む課題が変わらないため、マスの中に特殊音節を1つ書いておき、その音を含むことばを考える形にしました。",
        "items": [
            {"id": "r5-vii-levels", "label": "レベルの定義",
             "before": "Lv2・Lv3 とも2〜5音のマスで、解答例に拗音・長音・撥音が段階なく混在（例：はくちょう、やきゅう、まんが）",
             "after": ("Lv1：直音の語だけ（2〜4音）\nLv2：撥音・長音。1行に「ん」または長音の字（う・い）を書いておく。拗音・促音の語は使わない\n"
                       "Lv3：拗音・促音。語頭音が拗音（しゃ・ちょ・きゅ など。1マスに2文字）、または1行に「っ」を書いておく"),
             "ask": "段階の順（直音 → 撥音・長音 → 拗音・促音）と、マスに字を書いておく形でよいか"},
            {"id": "r5-vii-notes", "label": "【マスの書き方】をレベル別に",
             "before": "全レベル同じ説明（小さい字・っ・のばす音・ん をすべて説明）",
             "after": ("Lv1：1マスに1つの音を書きます。\nLv2：＋「ん」と、のばす音は、それぞれ1マス。はじめから書いてある字は、そのまま使う。\n"
                       "Lv3：＋小さい「ゃゅょ」は前の字と1マス。小さい「っ」「ん」のばす音は、それぞれ1マス。はじめから書いてある字は、そのまま使う。"),
             "ask": "子どもに伝わる言い方か"},
        ],
    },
    {
        "key": "r5-vii-lv2", "title": "Ⅶ Lv2（撥音・長音）14問",
        "lead": "既存の14の語頭音を作り直しました。マスに書いておく字に合う語が実際にあるか、なじみのある語かを見てください。",
        "items": [{"id": "r5-vii-" + it["id"].replace("_", "-"), "label": f"「{it['initial']}」から始まることば",
                   "before": "", "after": _vii_after(it), "ask": ""} for it in _r5_lv2],
    },
    {
        "key": "r5-vii-lv3", "title": "Ⅶ Lv3（拗音・促音）12問",
        "lead": "新しく作りました。拗音の語頭音7つ（しゃ・ちょ・きゅ・じゃ・ちゃ・しょ・きょ）と、「っ」を書いておく5つ（ら・こ・し・せ・そ）です。語が少ない語頭音はマスの行数を減らしています。",
        "items": [{"id": "r5-vii-" + it["id"].replace("_", "-"), "label": f"「{it['initial']}」から始まることば",
                   "before": "", "after": _vii_after(it), "ask": ""} for it in _r5_lv3],
    },
]
for sec in ROUND4:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND5



FIGURES = [
    ("Ⅳ Lv3（抽象語・感情語）", page_png(sheet("IV", 3), 1)),
    ("Ⅲ Lv1（右6語・解答）", page_png(sheet("III", 1, True), 1)),
    ("Ⅰ 連想チェーン Lv3（解答）", page_png(sheet("I", 3, True), 1)),
    ("Ⅱ Lv3（同じ種類・別の場面のダミー）", page_png(sheet("II", 3), 1)),
    ("Ⅴ つづき歌（手本つき）", page_png(sheet("V", 1), 1)),
    ("Ⅶ Lv1 解答（直音・2〜4音）", page_png(sheet("VII", 1, True), 1)),
    ("Ⅶ Lv2 問題（ん・長音を書いておく行）", page_png(sheet("VII", 2), 1)),
    ("Ⅶ Lv3 問題（拗音の語頭音・っ を書いておく行）", page_png(sheet("VII", 3), 1)),
]

# ---- 課題の説明（どの課題の、どんな問題の中の表現か） ----
import importlib
import sys
sys.path.insert(0, WS)
_MOD = {"I": "t1_chain", "II": "t2_network", "III": "t3_pairs", "IV": "t4_radial",
        "V": "t5_chain_song", "VI": "t6_fluency", "VII": "t7_mora", "VIII": "t8_venn",
        "IX": "t9_category_choice", "X": "t10_venn_choice"}
_NAME = {"I": "Ⅰ 連想チェーン", "II": "Ⅱ 意味ネットワーク照合", "III": "Ⅲ ペア対応づけ", "IV": "Ⅳ 放射状連想",
         "V": "Ⅴ つづき歌", "VI": "Ⅵ カテゴリー流暢性", "VII": "Ⅶ 語頭音＋モーラ数", "VIII": "Ⅷ 属性交差（ベン図）",
         "IX": "Ⅸ 仲間えらび（Ⅵ の書かない版）", "X": "Ⅹ ベン図えらび（Ⅷ の書かない版）"}
_FORMAT = {
    "I": "左のスタート語から右のゴール語まで、2〜4列目の楕円（各列に正解1つ＋ダミー3つ）から1つずつ選び、線でつなぐ。1枚に2問。",
    "III": "見出しに関係名（例：動物→鳴き声）。左に5語、右に順番を入れかえた5語。左右の語を線で結ぶ。1枚に2問。",
    "IV": "中央の円に中心語。まわりの8つの丸のうち1つにヒントの語が書いてあり、残り7つに子どもが思いつくことばを書く。1枚に2問。",
    "VI": "見出しにカテゴリー名、その下に例の語。続く約10本の線に、子どもが仲間のことばを書く（時間制限なし）。1枚に2問。",
    "VII": "「〇」から始まることば。2〜5音（Lv1 は2〜4音）のマス目の先頭に語頭音が印字され、残りのマスに書く。1枚に2問。",
    "VIII": "上に重なりの見出し（例：赤くて食べるもの）、左右の円に属性。左だけ・右だけ・重なりの3か所に書く。1枚に2問。",
}
TASKS = {}
_FORMAT["II"] = "中央の円に中心語。まわりに10の楕円（関係する5語＋ダミー5語）。関係する語を選んで線で結ぶ。1枚に2問。"
_FORMAT["V"] = "いちばん上の箱に開始語。下へ矢印でつながる箱に、矢印の横に書いたつなぎ方（Lv1 関係のあることば／Lv2 おなじなかま／Lv3 なかまといっしょを交互）でことばを1つずつ書く。2番目の箱は手本。1枚に2問。"
_FORMAT["IX"] = "上の四角にカテゴリー名。下に12語（仲間6語＋仲間でない6語、順不同）。仲間の語を○でかこむ。書かずに答える。1枚に2問。"
_FORMAT["X"] = "左右の円に条件。左右の列の語の箱から、合う場所（ひだりだけ・りょうほう・みぎだけ、Lv2 は外の四角＝どちらでもない）へ線を引く。書かずに答える。1枚に2問。"
for k in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"):
    m = importlib.import_module("gen.templates." + _MOD[k])
    TASKS[k] = {"name": _NAME[k], "title": m.DISPLAY_TITLE, "instruction": m.INSTRUCTION,
                "format": _FORMAT[k], "img": page_png(sheet(k, 1), 1, dpi=48)}


def sc_iv(it):
    return f"中央の円に「{it['center']}」。まわりの丸の1つにヒント「{it['hint']}」（Lv{it['level']}）。"


def sc_vi(it):
    return f"見出し「{it['category']}」、例「{it['example']}」。線に仲間のことばを書く（Lv{it['level']}）。"


def sc_iii(it):
    l = "・".join(a for a, _ in it["pairs"]); r = "・".join(b for _, b in it["pairs"])
    return f"見出し（{it['relation']}）。左：{l}／右（順不同）：{r}。左右を線で結ぶ（Lv{it['level']}）。"


def sc_i(it):
    c = it["chain"]
    return f"スタート「{c[0]}」→ゴール「{c[4]}」。2〜4列目の楕円から1つずつ選んでつなぐ（Lv{it['level']}）。"


def sc_vii(it):
    rows = it.get("moras") or [2, 3, 4, 5]
    fx = "".join(f"{k}音の行は{i + 1}マス目に「{ch}」を書いておく。" for k, r in (it.get("fixed") or {}).items() for i, ch in r.items())
    return (f"「{it['initial']}」から始まることば。{'・'.join(map(str, rows))}音のマス目の先頭に「{it['initial']}」。"
            + fx + f"（Lv{it['level']}）")


def sc_viii(it):
    return f"左の円「{it['left_attr']}」、右の円「{it['right_attr']}」、重なりの見出し「{it['intersection']}」（Lv{it['level']}）。"


_IVc = {it["center"]: it for it in IV.values()}
_VIc = {it["category"]: it for it in VI.values()}
_SC = {"II": (II, lambda it: sc_ii(it)), "V": (V, lambda it: sc_v(it)), "I": (I, sc_i), "III": (III, sc_iii), "IV": (IV, sc_iv), "VI": (VI, sc_vi), "VII": (VII, sc_vii), "VIII": (VIII, sc_viii)}
SEC_TASK = {"safety": ["IV"], "pairs": ["III"], "chain": ["I"], "mora": ["VII"], "venn": ["VIII"], "removed": ["IV", "VI"],
            "new-iv": ["IV"], "new-vi": ["VI"], "r2-iv": ["IV"], "r2-vi": ["VI"], "r2-vii": ["VII"], "r2-iii": ["III"],
            "r2-viii": ["VIII"], "r3-vi-remove": ["VI", "III"], "r3-vi-relevel": ["VI"], "r3-vi-adult": ["VI"],
            "r3-vi-new": ["VI"], "r3-iii-new": ["III"], "r4-iv-move": ["IV"], "r4-iv-hint": ["IV"], "r4-iv-new": ["IV"],
            "r5-vii-design": ["VII"], "r5-vii-lv2": ["VII"], "r5-vii-lv3": ["VII"],
            "r6-iii-instruction": ["III"], "r6-iii-extra": ["III"],
            "r7-i-lv1": ["I"], "r7-i-lv2": ["I"], "r7-i-lv3": ["I"],
            "r8-ii-lv3": ["II"], "r8-v-example": ["V"], "r8-viii-audit": ["VIII"]}
MANUAL = {
    "iv-hint-trust": sc_iv(_IVc["信頼"]), "iv-hint-relief": sc_iv(_IVc["安心"]),
    "iv-hint-regret": sc_iv(_IVc["後悔"]), "iv-hint-patience": sc_iv(_IVc["我慢"]),
    "iii-animal-home": sc_iii(III["animal_home"]), "iii-part-use": sc_iii(III["part_use"]),
    "iii-animal-baby": sc_iii(III["animal_baby"]), "iii-tool-action": sc_iii(III["tool_action"]),
    "iii-vehicle-place": sc_iii(III["vehicle_place"]), "iii-season": sc_iii(III["season_thing"]),
    "i-rain": sc_i(I["rain_boots"]), "i-tree": sc_i(I["tree_blocks"]), "i-grape": sc_i(I["grape_sherbet"]),
    "i-cloud": sc_i(I["cloud_umbrella"]), "i-rice": sc_i(I["rice_onigiri"]),
    "vii-instruction": "Ⅶ のすべてのページで、題の帯の下（教示文）と、ページ下部の【マスの書き方】に表示される。",
    "vii-answer-note": "Ⅶ の解答PDFのページ下部にだけ表示される（子どもが使う問題PDFには出ない）。",
    "vii-examples": "解答PDFで、「き」の問題の5音のマスと、「と」の問題の4音のマスに入る答えの例。",
    "viii-soft-eat": sc_viii(VIII["soft_eat"]),
    "dup-iv": "Ⅳ のパックで、同じ中心語（とヒント）の問題が2回出ないようにするための削除。",
    "dup-vi": "Ⅵ のパックで、同じカテゴリー（ひらがな／漢字の書き分けを含む）が2回出ないようにするための削除。",
    "r3-vi-pair-tasks": "修正前は Ⅵ Lv3 で、見出し「反対の意味のことば（例：大きい↔小さい）」、例「長い」の下の線に1語ずつ書く形だった。修正後は Ⅲ で、左右の語を線で結ぶ形になる。",
    "r3-vi-closed-sets": "修正前は Ⅵ Lv2 で、見出し「季節」（例：夏）／「月」（例：1月）の下の約10本の線に書く形だった。",
    "r3-vi-sounds": sc_vi(_VIc["動物の鳴き声"]), "r3-vi-furniture": sc_vi(_VIc["家具"]),
    "r3-vi-action-words": sc_vi(_VIc["動作を表すことば"]), "r3-vi-size-words": sc_vi(_VIc["大きさを表すことば"]),
    "r3-vi-energy": sc_vi(VI["vi_lv3_009b"]), "r3-vi-social-rule": sc_vi(VI["vi_lv3_017a"]),
    "r3-vi-salary": sc_vi(VI["vi_lv3_011a"]) + "\n" + sc_vi(VI["vi_lv3_016a"]),
    "r4-iv-move": "Lv2 のパックで、中央の円に「赤いもの」などが出る（例：" + sc_iv(_IVc["赤いもの"]) + "）",
    "r4-iv-hint-regret": sc_iv(_IVc["後悔"]),
    "r5-vii-levels": "Ⅶ の各問題のマス目。例：Lv2「か」の3音の行は「か□ん」（→かばん）、Lv3「ら」の3音の行は「ら っ□」（→らっぱ）。",
    "r6-iii-instruction": "Ⅲ のすべてのページで、題の帯の下に表示される教示文。",
    "r5-vii-notes": "Ⅶ の各ページ下部の【マスの書き方】。ページ内でいちばん高いレベルの説明を表示する。",
}


def _lookup(item_id, task):
    if task not in _SC:
        return None
    d, fn = _SC[task]
    for pre in ("new-", "r2-iii-", "r3-iii-", "r2-viii-", "r5-vii-", "r7-i-", "r8-viii-", "r2-", "r3-", "r4-"):
        if item_id.startswith(pre):
            key = item_id[len(pre):].replace("-", "_")
            if key in d:
                return fn(d[key])
    return None


# ---- 第6回：Ⅲ 右側に「どれとも結ばない語」を1つ足す（先頭に表示） ----
ROUND6 = [
    {
        "key": "r6-iii-instruction", "title": "Ⅲ 消去法で解けないようにする（右側を6語に）",
        "lead": "これまでは左5語・右5語で、4組を結ぶと最後の1組が自動的に決まっていました。右に「どれとも結ばない語」を1つ足し、教示文でもそれを伝えます。",
        "items": [{"id": "r6-iii-instruction", "label": "教示文",
                   "before": "左のことばと関係が深いことばを、右の中から1つ選んで線で結びましょう。",
                   "after": "左のことばと関係が深いことばを右から選んで、線で結びましょう。右には、あまることばが1つあります。",
                   "ask": "子どもに伝わる言い方か"}],
    },
    {
        "key": "r6-iii-extra", "title": "Ⅲ 各問題に足した「あまることば」（18問）",
        "lead": "右側の語と同じ種類で、左のどの語とも意味の上で結びつかない語を選びました。左のどれかと結べてしまわないかを見てください。",
        "items": [{"id": "r6-iii-" + k.replace("_", "-"), "label": f"{it['relation']}（Lv{it['level']}）",
                   "before": "", "after": f"あまることば：{it['extra']}", "ask": "",
                   "scene": sc_iii(it) + f" 右に「{it['extra']}」が加わり6語になる。"}
                  for k, it in III.items() if k not in ("synonym_verb", "synonym_state", "synonym_noun")],
    },
]
for sec in ROUND5:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND6

# ---- 第7回：Ⅰ 連想チェーンの点検と追加（先頭に表示） ----
_I_STATUS = {
    "school_note": "作り直し（旧：学校→勉強→教科書→読む→本。2列目が名詞で、教科書→本 は言いかえ）",
    "bread_jam": "新規", "morning_towel": "新規", "flower_honey": "新規",
    "fire_imo": "ゴールを変更（旧：…→あたる→あたたかい。ゴールが形容詞）",
    "milk_cheese": "4列目を変更（旧：つくる。何にでもつながる動詞）",
    "egg_chick": "ダミーを変更（旧：わる。ひなが殻をわる、で筋が通ってしまう）",
    "sports_baton": "新規", "scissors_crane": "新規", "paint_picture": "新規",
}
_I_SIDE = {
    "sports_baton": "わき道：おどる→ダンス、なげる→たまいれ→いれる、つなひき→ひく（どれもバトンに届かない）",
    "scissors_crane": "わき道：きる→ぬの→ぬう、きる→かみのけ→とかす、はる→テープ（どれもつるに届かない）",
    "paint_picture": "わき道：しぼる→タオル→ふく、ながす→みず→こぼす（どれも絵に届かない）",
}
ROUND7 = []
for _lv, _lead in ((1, "ダミーは始まりとも終わりとも関係のない、遠い語です。"),
                   (2, "ダミーは同じ場面にはあるが、つながらない語です。"),
                   (3, "ダミーは途中まで筋が通る「わき道」になるが、ゴールには届かない語です。ダミーを通ってゴールまで筋が通る経路がないかを、とくに見てください。")):
    ROUND7.append({
        "key": f"r7-i-lv{_lv}", "title": f"Ⅰ 連想チェーン Lv{_lv}（6問）",
        "lead": "形を「名詞→動き→名詞→動き→名詞」にそろえ、各レベル6問にしました。" + _lead,
        "items": [{"id": "r7-i-" + k.replace("_", "-"), "label": " → ".join(it["chain"]),
                   "before": "", "after": chain(it) + ("\n" + _I_SIDE[k] if k in _I_SIDE else ""),
                   "ask": _I_STATUS.get(k, "前回までに確認済みの問題（変更なし）")}
                  for k, it in I.items() if it["level"] == _lv and not it.get("_stub")],
    })
for sec in ROUND6:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND7

# ---- 第8回：Ⅱ Lv3・Ⅴ 手本・Ⅷ 点検（先頭に表示） ----
_VIII_CHECK = {
    "赤いもの/食べるもの": ("ポスト", "パン", "トマト"), "丸いもの/学校にあるもの": ("つき", "こくばん", "とけい"),
    "白いもの/食べるもの": ("ゆき", "トマト", "とうふ"), "四角いもの/家にあるもの": ("はがき", "まくら", "テレビ"),
    "あまいもの/飲みもの": ("ケーキ", "みず", "ジュース"), "黄色いもの/くだもの": ("ひまわり", "りんご", "バナナ"),
    "長いもの/道具": ("へび", "はさみ", "ものさし"), "つめたいもの/食べるもの": ("ゆき", "パン", "アイス"),
    "大きいもの/どうぶつ": ("ビル", "ねずみ", "ぞう"), "やわらかいもの/食べるもの": ("ふとん", "せんべい", "プリン"),
    "みどりのもの/やさい": ("はっぱ", "にんじん", "ピーマン"), "かたいもの/台所にあるもの": ("いし", "スポンジ", "なべ"),
    "ふわふわのもの/どうぶつ": ("わたあめ", "へび", "うさぎ"), "光るもの/空にあるもの": ("でんき", "くも", "たいよう"),
    "丸いもの/食べるもの": ("ボール", "バナナ", "おだんご"), "はやいもの/のりもの": ("チーター", "そり", "しんかんせん"),
    "かたいもの/食べるもの": ("いし", "プリン", "せんべい"), "四角いもの/学校にあるもの": ("とうふ", "ボール", "こくばん"),
    "白いもの/花": ("ゆき", "ひまわり", "ゆり"), "あついもの/飲みもの": ("ストーブ", "ジュース", "おちゃ"),
    "音が出るもの/おもちゃ": ("でんわ", "つみき", "ガラガラ"),
    "音が出るもの/丸いもの": ("ピアノ", "ボタン", "カスタネット"),
    "火を使うもの/料理に使うもの": ("はなび", "ほうちょう", "コンロ"),
    "時間がわかるもの/持ち歩けるもの": ("とけいだい", "かばん", "うでどけい"),
    "人が作ったもの/空をとぶもの": ("いす", "とり", "ひこうき"),
}


R10_VIII = ("fire_cook", "time_carry", "made_fly")   # 第10回で追加（第8回の点検には入れない）
R10_III = ("synonym_verb", "synonym_state", "synonym_noun")


def sc_ii(it):
    return f"中央の円に「{it['center']}」。まわりの10の楕円（関係する5語＋ダミー5語、順不同）から関係する語を選んで線で結ぶ（Lv{it['level']}）。"


def sc_v(it):
    return f"いちばん上の箱に「{it['start']}」、2番目の破線の箱に手本「{it.get('example')}」（薄い字・「れい」の印）。残り4つの箱に子どもが書く（Lv{it['level']}）。"


ROUND8 = [
    {
        "key": "r8-ii-lv3", "title": "Ⅱ 意味ネットワーク照合 Lv3（新規6問）",
        "lead": "Lv3 のダミー語を「同じ種類だが別の場面のもの」にしました（例：消防署 に対して パトカー・おまわりさん）。Lv1 は関係のないダミー、Lv2 は反対の場面のダミーです。これまで Lv3 だった「花火」「朝」は、ダミーが反対の場面（冬・夜）のものなので Lv2 に移しました。ダミーのどれかが中心語にも当てはまってしまわないかを見てください。",
        "items": [{"id": "r8-ii-" + k.replace("_", "-"), "label": it["center"], "before": "",
                   "after": "関係する語：" + "・".join(it["related"]) + "\nダミー語：" + "・".join(it["distractors"]),
                   "ask": "消防署：救急隊も使う「ちょうしんき」「ほうたい」は、消防署と結べてしまうので避けました" if k == "fire_station" else "",
                   "scene": sc_ii(it)} for k, it in II.items() if it["level"] == 3],
    },
    {
        "key": "r8-v-example", "title": "Ⅴ つづき歌の手本（24問）",
        "lead": "何を書けばよいか（前のことばと関係のあることば）が分かるよう、2番目の箱に手本の語を薄い字で入れました。教示文は「…1つずつ書きましょう。2ばんめは、れいです。」に変えています。手本が開始語とはっきり関係しているかを見てください。",
        "items": [{"id": "r8-v-" + k.replace("_", "-"), "label": it["start"], "before": "",
                   "after": f"{it['start']} → {it.get('example')}（れい）→ □ → □ → □ → □", "ask": "", "scene": sc_v(it)}
                  for k, it in V.items() if it.get("relation") == "かんけい"],
    },
    {
        "key": "r8-viii-audit", "title": "Ⅷ 属性交差 全21問の点検結果",
        "lead": "左だけ・右だけ・両方の3つの領域すべてに答えがあるかを点検しました。全問に答えがありました。答えの例が成り立つかを見てください。",
        "items": [{"id": "r8-viii-" + k.replace("_", "-"), "label": f"{it['left_attr']} ／ {it['right_attr']}", "before": "",
                   "after": "左だけ：{0}　右だけ：{1}　両方：{2}".format(*_VIII_CHECK.get(f"{it['left_attr']}/{it['right_attr']}", ("？", "？", "？"))),
                   "ask": ""} for k, it in VIII.items() if k not in R10_VIII
                   and "削除" not in str(it.get("intersection", "")) and "変更" not in str(it.get("intersection", ""))],
    },
]
for sec in ROUND7:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND8

# ---- 第9回：書かない版（Ⅸ・Ⅹ）、Ⅴ のつなぎ方によるレベル、Ⅶ Lv3 の拗長音、教示の補足（先頭に表示） ----
IX = load("IX_category_choice.yaml")
X = load("X_venn_choice.yaml")
_VII_BEFORE = {"cho_lv3": "2・3・5音の行。3音の行は2マス目に「っ」。", "kyu_lv3": "2・3・4・5音の行。書いておく字なし。",
               "sho_lv3": "3・4・5音の行。3音の行は2マス目に「っ」。", "kyo_lv3": "2・3・4音の行。書いておく字なし。"}
_V_LINK = {"なかま": "おなじなかま", "こうたい": "おなじなかま → いっしょにあるもの → おなじなかま …（交互）"}


def _rows(it):
    rows = it.get("moras") or [2, 3, 4, 5]
    fx = "".join(f"{k}音の行は{i + 1}マス目に「{ch}」。" for k, r in (it.get("fixed") or {}).items() for i, ch in r.items())
    return f"{'・'.join(map(str, rows))}音の行。" + (fx or "書いておく字なし。")


ROUND9 = [
    {
        "key": "r9-ix", "title": "Ⅸ 仲間えらび（Ⅵ の書かない版・新規8問）",
        "lead": "Ⅵ カテゴリー流暢性を、書かずに○で答える形にしました。12語のうち仲間の6語を○でかこみます。Lv1 は仲間でない語が別の領域の物、Lv2 はとなりのカテゴリーの物です。境界があいまいな語（いちご・すいか、くつ・ぼうし、くも・だんごむし など）は避けました。仲間でない語が仲間にも入ってしまわないか、仲間の語に迷うものがないかを見てください。",
        "items": [{"id": "r9-ix-" + k.replace("_", "-"), "label": f"{it['category']}（Lv{it['level']}）", "before": "",
                   "after": "仲間：" + "・".join(it["members"]) + "\n仲間でない：" + "・".join(it["others"]), "ask": "",
                   "scene": f"上の四角に「{it['category']}」。下の12語（順不同）から仲間の語を○でかこむ（Lv{it['level']}）。"}
                  for k, it in IX.items()],
    },
    {
        "key": "r9-x", "title": "Ⅹ ベン図えらび（Ⅷ の書かない版・新規8問）",
        "lead": "Ⅷ 属性交差を、書かずに線で答える形にしました。語の箱から、合う場所（ひだりだけ・りょうほう・みぎだけ）へ線を引きます。Lv2 は円の外の四角（どちらでもない）を加えます。どの語も入る場所が1つに決まるかを見てください。「食べるもの／木になるもの」の どんぐり・まつぼっくり は「食べるもの」に入れない前提です。",
        "items": [{"id": "r9-x-" + k.replace("_", "-"), "label": f"{it['left_attr']} ／ {it['right_attr']}（Lv{it['level']}）", "before": "",
                   "after": "ひだりだけ：" + "・".join(it["left"]) + "　りょうほう：" + "・".join(it["both"]) + "　みぎだけ：" + "・".join(it["right"])
                            + ("　どちらでもない：" + "・".join(it["none"]) if it.get("none") else ""), "ask": "",
                   "scene": f"左の円「{it['left_attr']}」、右の円「{it['right_attr']}」。左右の列の語から、合う場所へ線を引く（Lv{it['level']}）。"}
                  for k, it in X.items()],
    },
    {
        "key": "r9-v-levels", "title": "Ⅴ つづき歌：つなぎ方でレベル分け（新規18問）",
        "lead": "レベルを開始語の抽象度ではなく、つなぎ方の種類で決めるようにしました。矢印の横につなぎ方を書きます。Lv1 は第8回で確認していただいた24問（関係のあることば・つなぎ方は自由）。Lv2 は「おなじなかま」、Lv3 は「おなじなかま」と「いっしょにあるもの」を交互に。根拠：幼児が主題的関係と分類学的関係のどちらを選ぶかは教示で変わり（湯川, 2002）、上位概念の知識は3〜4歳、関係を切り替える実行制御は4〜5歳で伸びる（Blaye & Jacques, 2009）。手本の語が最初のつなぎ方（おなじなかま）に合っているかを見てください。",
        "items": [{"id": "r9-v-" + k.replace("_", "-"), "label": f"{it['start']}（Lv{it['level']}）", "before": "",
                   "after": f"{it['start']} →〔おなじなかま〕→ {it['example']}（れい）→ □ → □ → □ → □\nつなぎ方：{_V_LINK[it['relation']]}",
                   "ask": "", "scene": f"いちばん上の箱に「{it['start']}」、2番目の破線の箱に手本「{it['example']}」。矢印の横のつなぎ方で、残り4つの箱に書く（Lv{it['level']}）。"}
                  for k, it in V.items() if it.get("relation") in ("なかま", "こうたい")],
    },
    {
        "key": "r9-vii-yochoon", "title": "Ⅶ Lv3：拗長音の行に「う」を書いておく（4問）",
        "lead": "拗長音（きゅう・しょう など）は特殊音節の中で最も表記が難しい（年長の読み正答率43％：太田ら, 2018）ため、答えが拗長音になる行には、のばす音の「う」を書いておくようにしました。2音の行は「う」を書くとマスが全部うまってしまうので、その行は外しました。",
        "items": [{"id": "r9-vii-" + k.replace("_", "-"), "label": f"「{VII[k]['initial']}」から始まることば", "before": _VII_BEFORE[k],
                   "after": _rows(VII[k]) + "\n答えの例：" + "・".join(w for ws in VII[k]["answers"].values() for w in ws), "ask": "",
                   "scene": sc_vii(VII[k])} for k in _VII_BEFORE],
    },
    {
        "key": "r9-notes", "title": "教示の補足（書かずに・読まずに答えてよいこと）",
        "lead": "どの課題もねらいは語の意味の力で、かなの読み書きではないため、教示の下に1行の補足を入れました（評価レポート §13）。",
        "items": [
            {"id": "r9-note-oral", "label": "書く課題（Ⅳ・Ⅴ・Ⅵ・Ⅷ）", "before": "（なし）",
             "after": "書くのがたいへんなときは、口で言って、大人に書いてもらってもいいよ。", "ask": "子どもに伝わる言い方か",
             "scene": "Ⅳ・Ⅴ・Ⅵ・Ⅷ のすべてのページで、教示文の下に薄い字で表示される。"},
            {"id": "r9-note-read", "label": "読む課題（Ⅸ・Ⅹ）", "before": "（なし）",
             "after": "字を読むのがたいへんなときは、大人が読んであげてもいいよ。", "ask": "",
             "scene": "Ⅸ・Ⅹ のすべてのページで、教示文の下に薄い字で表示される。"},
            {"id": "r9-note-vi", "label": "Ⅵ の教示文", "before": "それぞれの仲間に入ることばを、できるだけたくさん書きましょう。はじめの1つは例です。",
             "after": "それぞれの仲間に入ることばを、思いつくだけ書きましょう。はじめの1つは例です。全部うめなくてもだいじょうぶ。",
             "ask": "5行版（_問題_5行.pdf）も作りました", "scene": "Ⅵ のすべてのページで、題の帯の下に表示される教示文。"},
            {"id": "r9-note-viii-labels", "label": "Ⅷ ベン図の場所の名前", "before": "（なし）",
             "after": "左の円の外寄りに「ひだりだけ」、重なりに「りょうほう」、右の円の外寄りに「みぎだけ」を薄い字で書く。",
             "ask": "根拠：幼児の「だけ」の理解は付く位置と助詞で大きく変わる（Matsuoka, 2007）ので、文で読ませず図のラベルで示す。書く場所をふさがないか",
             "scene": "Ⅷ のすべてのページで、2つの円の中に薄い字で表示される。"},
            {"id": "r9-note-v", "label": "Ⅴ の教示文", "before": "一番上のことばから始めて、前のことばと関係があることばを1つずつ書きましょう。2ばんめは、れいです。",
             "after": "一番上のことばから始めて、やじるしの横に書いてあるつなぎ方で、ことばを1つずつ書きましょう。2ばんめは、れいです。",
             "ask": "", "scene": "Ⅴ のすべてのページで、題の帯の下に表示される教示文。"},
        ],
    },
]
for sec in ROUND8:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND9
SEC_TASK.update({"r9-ix": ["IX"], "r9-x": ["X"], "r9-v-levels": ["V"], "r9-vii-yochoon": ["VII"],
                 "r9-notes": ["IV", "V", "VI", "VIII", "IX", "X"]})
# ---- 第10回：Ⅲ・Ⅷ の Lv3 を追加（先頭に表示） ----
ROUND10 = [
    {
        "key": "r10-iii-lv3", "title": "Ⅲ ペア対応づけ Lv3（新規3問）",
        "lead": "Lv3 が1問（似た意味のことば）しかなくプリントにできなかったので、同じ「似た意味」の型で3問足しました（うごき・ようす・もの／こと）。Lv3 は似た意味を結ぶ範列的・メタ言語的な判断で、語の定義の質は5〜11歳で伸びるとされます（Wiki SV-16）。左右が1対1に決まるか、あまることばがどれとも結ばないかを見てください。",
        "items": [{"id": "r10-iii-" + k.replace("_", "-"), "label": III[k]["relation"], "before": "",
                   "after": "　".join(f"{a}－{b}" for a, b in III[k]["pairs"]) + f"\nあまることば：{III[k]['extra']}", "ask": "",
                   "scene": sc_iii(III[k])} for k in R10_III],
    },
    {
        "key": "r10-viii-lv3", "title": "Ⅷ 属性交差 Lv3（新規3問）",
        "lead": "Lv3 が1問（光るもの／空にあるもの）しかなかったので、見た目では決まらない、はたらき・なりたちの条件で3問足しました。2つの条件で分ける力は、自分で例を考える形では6〜8歳ごろまで難しいとされます（Wiki SV-18）。3つの場所すべてに答えがあるか、答えの例が成り立つかを見てください。",
        "items": [{"id": "r10-viii-" + k.replace("_", "-"), "label": f"{VIII[k]['left_attr']} ／ {VIII[k]['right_attr']}", "before": "",
                   "after": "左だけ：{0}　右だけ：{1}　両方：{2}".format(*_VIII_CHECK[f"{VIII[k]['left_attr']}/{VIII[k]['right_attr']}"]),
                   "ask": "", "scene": sc_viii(VIII[k])} for k in R10_VIII],
    },
]
for sec in ROUND9:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND10
SEC_TASK.update({"r10-iii-lv3": ["III"], "r10-viii-lv3": ["VIII"]})
# ---- 第11回：発達の順序に沿ったレベルの見直しと、年長の生徒向けの題材（先頭に表示） ----
_R11_VII = {"ka": "Lv2 → Lv1", "a": "Lv2 → Lv1", "ha": "Lv2 → Lv1", "ni_lv2": "Lv1 → Lv2", "ne_lv2": "Lv1 → Lv2", "wa_lv2": "Lv1 → Lv2"}
_R11_III = {"tool_action": "Lv2 → Lv1", "part_use": "Lv2 → Lv1", "job_tool": "Lv1 → Lv2", "food_ingredient": "Lv1 → Lv2"}
ROUND11 = [
    {
        "key": "r11-vii-initial", "title": "Ⅶ 語頭音の語の多さでレベルを入れ替え（6問）",
        "lead": "頭音を手がかりに思い出せる語の数は、その音で始まる語の多さに強く左右されます（国立国語研究所 1981、rs=.81〜.89）。教育基本語彙（低学年配当）でその音から始まる語を数えると、Lv1 に語の少ない ね(71)・わ(83)・に(92)、Lv2 に語の多い か(406)・あ(288)・は(276) がありました。そこで入れ替え、か・あ・は は直音だけの Lv1 に、ね・わ・に は「ん」を書いておく行のある Lv2 にしました。答えの例が成り立つかを見てください。あわせて Lv1 の答えの例のうち時期の遅い語（なまず・すきやき・みずたま）を差し替えました。",
        "items": [{"id": "r11-vii-" + k.replace("_", "-"), "label": f"「{VII[k]['initial']}」（{v}）", "before": "",
                   "after": _rows(VII[k]) + "\n答えの例：" + "・".join(w for ws in VII[k]["answers"].values() for w in ws), "ask": "",
                   "scene": sc_vii(VII[k])} for k, v in _R11_VII.items()],
    },
    {
        "key": "r11-iii-level", "title": "Ⅲ 関係の種類の順にレベルをそろえる（4問の移動）",
        "lead": "機能・部分と全体の関係は早くから使われ、上位カテゴリーの関係はそれより遅れます（Wiki SV-32）。反対語は類義語より易しいとされます（SV-29）。そこで、Lv1 を機能・場面の関係と反対のことば（ようす）、Lv2 を知識の要る関係（すみか・こども・材料・職業の道具）と反対のことば（うごき）、Lv3 を似た意味のことばにそろえました。「職業→道具」は「聴診器」「写真家」など時期の遅い語を含むので Lv2 にしました。",
        "items": [{"id": "r11-iii-" + k.replace("_", "-"), "label": f"{III[k]['relation']}（{v}）", "before": v.split(" → ")[0],
                   "after": v.split(" → ")[1], "ask": "", "scene": sc_iii(III[k])} for k, v in _R11_III.items()],
    },
    {
        "key": "r11-iv-level", "title": "Ⅳ 放射状連想：Lv1 は場面、Lv2 は属性に（新規6問）",
        "lead": "これまで Lv2 に、場面の題（病院・駅など）と属性の題（赤いものなど）が混ざっていました。場面の連想（そこにあるもの・すること）は最も早く使える主題的な関係です。属性の連想は、別々の場面から同じ性質のものを集める範列的な連想です。そこで場面の題をすべて Lv1 に、属性の題を Lv2 にしました（属性を上に置くのは、主題的関係が最も早いことからの推論です）。Lv2 が6問になるので、属性の題を6問足しました。ヒントの語が合っているかを見てください。",
        "items": [{"id": "r11-iv-" + k, "label": IV[k]["center"], "before": "", "after": f"中心：{IV[k]['center']}　ヒント：{IV[k]['hint']}",
                   "ask": "", "scene": sc_iv(IV[k])} for k in ("white", "cold", "long", "sweet", "big", "shiny")],
    },
    {
        "key": "r11-teen", "title": "年長の生徒の生活に合う題材（新規9問）",
        "lead": "対象は小学4年〜高校3年なので、語は易しいまま、題材を生活年齢に合わせたものを足しました（受容語彙には生活年齢・経験も寄与する：Wiki ND-04）。題材とヒント・例の語が合っているか、生徒にとって身近かを見てください。",
        "items": [{"id": "r11-teen-" + k.replace("_", "-"), "label": IV[k]["center"], "before": "", "after": f"中心：{IV[k]['center']}　ヒント：{IV[k]['hint']}",
                   "ask": "", "scene": sc_iv(IV[k])} for k in ("club", "convenience", "smartphone", "school_trip", "school_festival", "junior_high")]
                 + [{"id": "r11-teen-" + k.replace("_", "-"), "label": VI[k]["category"], "before": "", "after": f"カテゴリー：{VI[k]['category']}　例：{VI[k]['example']}",
                     "ask": "", "scene": sc_vi(VI[k])} for k in ("club_types", "phone_can", "conv_sell")],
    },
]
for sec in ROUND10:
    sec["title"] = "［前回］" + sec["title"]
SECTIONS[:0] = ROUND11
SEC_TASK.update({"r11-vii-initial": ["VII"], "r11-iii-level": ["III"], "r11-iv-level": ["IV"], "r11-teen": ["IV", "VI"]})
FIGURES[:0] = [
]
FIGURES[:0] = [
    ("Ⅲ ペア対応づけ Lv3（解答）", page_png(sheet("III", 3, True), 1)),
    ("Ⅷ 属性交差 Lv3", page_png(sheet("VIII", 3), 1)),
]
FIGURES[:0] = [
    ("Ⅸ 仲間えらび Lv2（解答）", page_png(sheet("IX", 2, True), 1)),
    ("Ⅹ ベン図えらび Lv2（解答）", page_png(sheet("X", 2, True), 1)),
    ("Ⅴ つづき歌 Lv3（なかま・いっしょを交互）", page_png(sheet("V", 3), 1)),
    ("Ⅵ カテゴリー流暢性 Lv1（5行版）", page_png(sheet("VI", 1).replace("_問題.pdf", "_問題_5行.pdf"), 1)),
]
for sec in SECTIONS:
    key = sec["key"]
    sec["tasks"] = SEC_TASK.get(key, [])
    for it in sec["items"]:
        if it["id"] in MANUAL:
            it["scene"] = MANUAL[it["id"]]
        elif it["id"].startswith("r4-iv-hint-"):
            it["scene"] = sc_iv(_IVc[it["label"]])
        else:
            for t in sec["tasks"]:
                sc = _lookup(it["id"], t)
                if sc:
                    it["scene"] = sc
                    break

missing = [it["id"] for sec in SECTIONS for it in sec["items"] if not it.get("scene")]
if missing:
    raise SystemExit("scene 未設定: " + ", ".join(missing))

data_json = json.dumps(SECTIONS, ensure_ascii=False).replace("</", "<\\/")
tasks_json = json.dumps(TASKS, ensure_ascii=False).replace("</", "<\\/")
figs = "\n".join(
    f'<figure class="fig"><img src="{src}" alt="{html.escape(cap)}の生成PDF" loading="lazy"><figcaption>{html.escape(cap)}</figcaption></figure>'
    for cap, src in FIGURES)

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html"), encoding="utf-8") as f:
    page = f.read()
page = page.replace("/*__DATA__*/[]", data_json).replace("/*__TASKS__*/{}", tasks_json).replace("<!--__FIGURES__-->", figs)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(page)
print(OUT, sum(len(s["items"]) for s in SECTIONS), "items", os.path.getsize(OUT), "bytes")
