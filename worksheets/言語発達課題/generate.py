#!/usr/bin/env python3
"""関連語の想起課題ジェネレータ ― CLI。

例:
  python generate.py --catalog                 # products.yaml の全課題・全レベルを プリント/ に作り直す
  python generate.py --type II --level 2 --count 5 --seed 1 --out ./プリント/_試し --with-answers
"""
import argparse
import os
import sys

import yaml

from gen import data
from gen.render import generate_set


def _sanitize(name):
    bad = '<>:"/\\|?*'
    return "".join("_" if ch in bad else ch for ch in name).strip() or "pack"


def run_single(args):
    if args.type not in data.TYPES:
        sys.exit(f"--type は {data.TYPES} のいずれか。指定: {args.type}")
    generate_set(
        type_key=args.type, count=args.count, level=args.level, seed=args.seed,
        out_dir=args.out, with_answers=args.with_answers, base_dir=args.base_dir,
        name=args.name, overrides={"lines": args.lines} if args.lines else None,
    )


def run_pack(args):
    with open(args.pack, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    products = doc.get("products", [])
    if not products:
        sys.exit(f"{args.pack} に products がありません。")
    for i, p in enumerate(products):
        tkey = str(p["type"])
        if tkey not in data.TYPES:
            sys.exit(f"products[{i}] の type が不正: {tkey}")
        pack_name = _sanitize(str(p.get("name", f"type_{tkey}")))
        out_dir = os.path.join(args.out, tkey)
        generate_set(
            type_key=tkey, count=int(p.get("count", 10)),
            level=p.get("level"), seed=args.seed + i, out_dir=out_dir,
            with_answers=args.with_answers, base_dir=args.base_dir, name=pack_name,
        )


def run_catalog(args):
    """products.yaml の catalog に従い、全課題・全レベルを次の構成で作り直す。

    プリント/NN_名前/LvL/NN_名前_LvL_問題.pdf（＋ _解答.pdf）
    プリント/_生成記録/NN_名前_LvL.json
    各レベルの PDF には、そのレベルの問題を1回ずつ（2問×枚数）収める。
    """
    import shutil
    with open(args.catalog, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    out_root = args.out or os.path.join(args.base_dir, "プリント")
    if os.path.isdir(out_root):
        shutil.rmtree(out_root)          # 古い出力が残らないよう毎回作り直す
    log_dir = os.path.join(out_root, "_生成記録")
    for n, entry in enumerate(doc.get("catalog", []), start=1):
        tkey = str(entry["type"])
        folder = f"{n:02d}_{entry['name']}"
        items = data.load_items(tkey, args.base_dir)
        for level in sorted({int(it.get("level", 1)) for it in items}):
            uniq = data.count_unique(tkey, [it for it in items if int(it.get("level", 1)) == level])
            count = uniq // 2
            if count == 0:
                print(f"[{tkey}] Lv{level}: 問題が{uniq}問のため1枚に満たず、作りません")
                continue
            stem = f"{folder}_Lv{level}"
            # variants: 同じ問題を、行数などを変えた版でも作る（例：Ⅵ の5行版 → 〜_問題_5行.pdf）
            for v in [None] + list(entry.get("variants") or []):
                suffix = f"_{v['suffix']}" if v else ""
                generate_set(
                    type_key=tkey, count=count, level=level,
                    seed=args.seed + n * 10 + level,
                    out_dir=os.path.join(out_root, folder, f"Lv{level}"),
                    with_answers=True, base_dir=args.base_dir,
                    name=f"{stem}_問題{suffix}", answers_name=f"{stem}_解答{suffix}",
                    manifest_path=os.path.join(log_dir, f"{stem}{suffix}.json"),
                    overrides=(v or {}).get("set"),
                )


def main(argv=None):
    ap = argparse.ArgumentParser(description="関連語の想起課題プリント生成")
    ap.add_argument("--type", help="I〜VIII から1つ")
    ap.add_argument("--level", type=int, choices=[1, 2, 3, 4], default=None,
                    help="難易度 1〜3（省略時は全item対象）")
    ap.add_argument("--count", type=int, default=10, help="生成する枚数(=商品数)")
    ap.add_argument("--seed", type=int, default=0, help="乱数シード（再現性）")
    ap.add_argument("--out", default=None,
                    help="出力ディレクトリ（省略時：--catalog は プリント/、それ以外は プリント/_試し/）")
    ap.add_argument("--with-answers", action="store_true",
                    help="I/II/III/VII の解答PDFも出力")
    ap.add_argument("--name", default=None, help="出力ファイル名の幹")
    ap.add_argument("--lines", type=int, default=None, help="Ⅵ の記入行の数を全問で上書き（例：5）")
    ap.add_argument("--pack", default=None, help="products.yaml の products（販売パック）を一括生成")
    ap.add_argument("--catalog", nargs="?", const="products.yaml", default=None,
                    help="products.yaml の catalog に従い、全課題・全レベルを プリント/ に作り直す")
    ap.add_argument("--base-dir", default=os.path.dirname(os.path.abspath(__file__)),
                    help="data/ と fonts/ の基準ディレクトリ")
    args = ap.parse_args(argv)

    if not args.catalog and not args.out:
        args.out = os.path.join(args.base_dir, "プリント", "_試し")
    if args.catalog:
        if not os.path.isabs(args.catalog) and not os.path.exists(args.catalog):
            args.catalog = os.path.join(args.base_dir, args.catalog)
        run_catalog(args)
    elif args.pack:
        run_pack(args)
    elif args.type:
        run_single(args)
    else:
        ap.error("--catalog・--type・--pack のいずれかを指定してください。")


if __name__ == "__main__":
    main()
