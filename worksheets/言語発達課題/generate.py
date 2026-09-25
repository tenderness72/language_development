#!/usr/bin/env python3
"""関連語の想起課題ジェネレータ ― CLI。

例:
  python generate.py --type II --level 2 --count 20 --seed 42 --out ./out --with-answers
  python generate.py --pack products.yaml --seed 42 --out ./out --with-answers
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
        name=args.name,
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


def main(argv=None):
    ap = argparse.ArgumentParser(description="関連語の想起課題プリント生成")
    ap.add_argument("--type", help="I〜VIII から1つ")
    ap.add_argument("--level", type=int, choices=[1, 2, 3], default=None,
                    help="難易度 1〜3（省略時は全item対象）")
    ap.add_argument("--count", type=int, default=10, help="生成する枚数(=商品数)")
    ap.add_argument("--seed", type=int, default=0, help="乱数シード（再現性）")
    ap.add_argument("--out", default="./out", help="出力ディレクトリ")
    ap.add_argument("--with-answers", action="store_true",
                    help="I/II/III/VII の解答PDFも出力")
    ap.add_argument("--name", default=None, help="出力ファイル名の幹")
    ap.add_argument("--pack", default=None, help="products.yaml を渡して一括生成")
    ap.add_argument("--base-dir", default=os.path.dirname(os.path.abspath(__file__)),
                    help="data/ と fonts/ の基準ディレクトリ")
    args = ap.parse_args(argv)

    if args.pack:
        run_pack(args)
    elif args.type:
        run_single(args)
    else:
        ap.error("--type か --pack のいずれかを指定してください。")


if __name__ == "__main__":
    main()
