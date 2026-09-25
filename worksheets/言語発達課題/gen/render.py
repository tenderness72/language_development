"""1テンプレートのセット生成（問題PDF＋任意で解答PDF＋manifest）。"""
import json
import os
import random
import zlib

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from . import data, fonts, templates
from .layout import Ctx
from .qa import validate_items


def _page_rng(seed, type_key, page_idx):
    """ページ単位の配置乱数（問題面と解答面で同一・実行をまたいで再現可能）。

    str の hash() はプロセス毎に乱数化されるため、crc32 で安定化する。
    """
    key = f"{seed}|{type_key}|{page_idx}".encode("utf-8")
    return random.Random(zlib.crc32(key))


def generate_set(type_key, count, level, seed, out_dir, with_answers=False,
                 base_dir=".", name=None, sampler=None, verbose=True):
    """1テンプレートを count 枚生成。manifest(dict) を返す。"""
    fonts.register(data.load_config(base_dir).get("font"), base_dir=base_dir)
    mod = templates.get(type_key)

    items = data.load_items(type_key, base_dir)
    errs = validate_items(type_key, items)
    if errs:
        raise ValueError("データ不備:\n  " + "\n  ".join(errs))

    pool, broadened = data.build_pool(items, level, needed=count * 2)
    rng = random.Random(seed)
    if sampler is None:
        sampler = data.Sampler(pool, rng)

    os.makedirs(out_dir, exist_ok=True)
    stem = name or f"type_{type_key}"
    q_path = os.path.join(out_dir, f"{stem}.pdf")
    a_path = os.path.join(out_dir, f"{stem}_answers.pdf")

    # PDFメタデータのタイトルも「ローマ数字＋表示名」のみ。
    # 「関連語の想起課題」や臨床名はPDFに一切入れない。
    disp = f"{data.ROMAN[type_key]}　{mod.DISPLAY_TITLE}"
    # invariant=1: 生成日時/IDを固定し、同一seedでバイト単位再現可能にする
    qc = canvas.Canvas(q_path, pagesize=A4, invariant=1)
    qc.setTitle(f"{disp}（{stem}）")
    ac = None
    do_answers = with_answers and mod.HAS_ANSWER
    if do_answers:
        ac = canvas.Canvas(a_path, pagesize=A4, invariant=1)
        ac.setTitle(f"{disp}（{stem}）解答")

    ctx = Ctx(titles=data.load_config(base_dir).get("titles"))
    # manifest は手元管理用ファイル。臨床名(clinical_title)はここにのみ残す。
    manifest = {"type": type_key, "display_title": mod.DISPLAY_TITLE,
                "clinical_title": mod.TITLE, "name": stem,
                "level": level, "seed": seed, "count": count, "pages": []}

    for page_idx in range(count):
        page_items = sampler.take(2)
        lr = _page_rng(seed, type_key, page_idx)
        page_mani = mod.draw_page(qc, ctx, page_items, lr, answers=False)
        qc.showPage()
        if do_answers:
            lr2 = _page_rng(seed, type_key, page_idx)
            mod.draw_page(ac, ctx, page_items, lr2, answers=True)
            ac.showPage()
        page_mani["page"] = page_idx + 1
        manifest["pages"].append(page_mani)

    qc.save()
    if do_answers:
        ac.save()

    manifest["warnings"] = ctx.warnings
    manifest["has_answers"] = do_answers
    with open(os.path.join(out_dir, f"{stem}_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    manifest["broadened_level"] = broadened
    if verbose:
        msg = f"[{type_key}] {count}枚 -> {q_path}"
        if do_answers:
            msg += f"  (+解答 {a_path})"
        if broadened and level is not None:
            msg += f"  ※level={level}のitemが不足のため全levelから出題"
        if ctx.warnings:
            msg += f"  ⚠ はみ出し {len(ctx.warnings)}件"
        print(msg)
    return manifest
