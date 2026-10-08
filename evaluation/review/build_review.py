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


def page_png(pdf, page_no, dpi=62):  # noqa: E302
    doc = pymupdf.open(os.path.join(WS, pdf))
    png = doc[page_no - 1].get_pixmap(dpi=dpi).tobytes("png")
    return "data:image/png;base64," + base64.b64encode(png).decode()


I, III, IV, VI, VII, VIII = (load(n) for n in (
    "I_chain.yaml", "III_pairs.yaml", "IV_radial.yaml", "VI_fluency.yaml",
    "VII_mora.yaml", "VIII_venn.yaml"))


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
    ("Ⅳ Lv3（抽象語・感情語）", page_png("out/IV/放射状連想 Lv3.pdf", 1)),
    ("Ⅲ ペアパック（体→はたらき・生き物→こども）", page_png("out/III/ペアパック.pdf", 4)),
    ("Ⅰ 連想チェーン（くも・風）", page_png("out/type_I.pdf", 1)),
    ("Ⅶ 解答（マスの書き方と注記）", page_png("out/type_VII_answers.pdf", 1)),
    ("Ⅶ Lv1 解答（直音・2〜4音）", page_png("out/VII/音韻パック_answers.pdf", 1)),
    ("Ⅶ Lv2 問題（ん・長音を書いておく行）", page_png("out/VII/音韻 Lv2 見本（撥音・長音）.pdf", 1)),
    ("Ⅶ Lv3 問題（拗音の語頭音・っ を書いておく行）", page_png("out/VII/音韻 Lv3 見本（拗音・促音）.pdf", 1)),
]

# ---- 課題の説明（どの課題の、どんな問題の中の表現か） ----
import importlib
import sys
sys.path.insert(0, WS)
_MOD = {"I": "t1_chain", "II": "t2_network", "III": "t3_pairs", "IV": "t4_radial",
        "V": "t5_chain_song", "VI": "t6_fluency", "VII": "t7_mora", "VIII": "t8_venn"}
_NAME = {"I": "Ⅰ 連想チェーン", "II": "Ⅱ 意味ネットワーク照合", "III": "Ⅲ ペア対応づけ", "IV": "Ⅳ 放射状連想",
         "V": "Ⅴ つづき歌", "VI": "Ⅵ カテゴリー流暢性", "VII": "Ⅶ 語頭音＋モーラ数", "VIII": "Ⅷ 属性交差（ベン図）"}
_FORMAT = {
    "I": "左のスタート語から右のゴール語まで、2〜4列目の楕円（各列に正解1つ＋ダミー3つ）から1つずつ選び、線でつなぐ。1枚に2問。",
    "III": "見出しに関係名（例：動物→鳴き声）。左に5語、右に順番を入れかえた5語。左右の語を線で結ぶ。1枚に2問。",
    "IV": "中央の円に中心語。まわりの8つの丸のうち1つにヒントの語が書いてあり、残り7つに子どもが思いつくことばを書く。1枚に2問。",
    "VI": "見出しにカテゴリー名、その下に例の語。続く約10本の線に、子どもが仲間のことばを書く（時間制限なし）。1枚に2問。",
    "VII": "「〇」から始まることば。2〜5音（Lv1 は2〜4音）のマス目の先頭に語頭音が印字され、残りのマスに書く。1枚に2問。",
    "VIII": "上に重なりの見出し（例：赤くて食べるもの）、左右の円に属性。左だけ・右だけ・重なりの3か所に書く。1枚に2問。",
}
TASKS = {}
for k in ("I", "III", "IV", "VI", "VII", "VIII"):
    m = importlib.import_module("gen.templates." + _MOD[k])
    TASKS[k] = {"name": _NAME[k], "title": m.DISPLAY_TITLE, "instruction": m.INSTRUCTION,
                "format": _FORMAT[k], "img": page_png(f"out/type_{k}.pdf", 1, dpi=48)}


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
_SC = {"I": (I, sc_i), "III": (III, sc_iii), "IV": (IV, sc_iv), "VI": (VI, sc_vi), "VII": (VII, sc_vii), "VIII": (VIII, sc_viii)}
SEC_TASK = {"safety": ["IV"], "pairs": ["III"], "chain": ["I"], "mora": ["VII"], "venn": ["VIII"], "removed": ["IV", "VI"],
            "new-iv": ["IV"], "new-vi": ["VI"], "r2-iv": ["IV"], "r2-vi": ["VI"], "r2-vii": ["VII"], "r2-iii": ["III"],
            "r2-viii": ["VIII"], "r3-vi-remove": ["VI", "III"], "r3-vi-relevel": ["VI"], "r3-vi-adult": ["VI"],
            "r3-vi-new": ["VI"], "r3-iii-new": ["III"], "r4-iv-move": ["IV"], "r4-iv-hint": ["IV"], "r4-iv-new": ["IV"],
            "r5-vii-design": ["VII"], "r5-vii-lv2": ["VII"], "r5-vii-lv3": ["VII"]}
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
    "r5-vii-notes": "Ⅶ の各ページ下部の【マスの書き方】。ページ内でいちばん高いレベルの説明を表示する。",
}


def _lookup(item_id, task):
    d, fn = _SC[task]
    for pre in ("new-", "r2-iii-", "r3-iii-", "r2-viii-", "r5-vii-", "r2-", "r3-", "r4-"):
        if item_id.startswith(pre):
            key = item_id[len(pre):].replace("-", "_")
            if key in d:
                return fn(d[key])
    return None


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
