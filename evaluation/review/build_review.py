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


def page_png(pdf, page_no, dpi=62):
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

FIGURES = [
    ("Ⅳ Lv3（信頼・丸いもの）", page_png("out/IV/放射状連想 Lv3.pdf", 9)),
    ("Ⅲ ペアパック（体→はたらき・生き物→こども）", page_png("out/III/ペアパック.pdf", 4)),
    ("Ⅰ 連想チェーン（くも・風）", page_png("out/type_I.pdf", 1)),
    ("Ⅶ 解答（マスの書き方と注記）", page_png("out/type_VII_answers.pdf", 1)),
    ("Ⅶ Lv1 解答（直音・2〜4音）", page_png("out/VII/音韻パック_answers.pdf", 1)),
]

data_json = json.dumps(SECTIONS, ensure_ascii=False).replace("</", "<\\/")
figs = "\n".join(
    f'<figure class="fig"><img src="{src}" alt="{html.escape(cap)}の生成PDF" loading="lazy"><figcaption>{html.escape(cap)}</figcaption></figure>'
    for cap, src in FIGURES)

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html"), encoding="utf-8") as f:
    page = f.read()
page = page.replace("/*__DATA__*/[]", data_json).replace("<!--__FIGURES__-->", figs)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(page)
print(OUT, sum(len(s["items"]) for s in SECTIONS), "items", os.path.getsize(OUT), "bytes")
