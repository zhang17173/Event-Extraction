# -*- coding:utf-8 -*-

from __future__ import annotations

import argparse
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_utils import print_step, print_success, repo_root

PUNCTUATION = '''，。、:；（）ＸX×xa"“”,<《》'''
REDUNDANT_PATTERN = re.compile(
    "本院认为|违反道路交通管理法规|驾驶机动车辆|因而|违反道路交通运输管理法规|违反交通运输管理法规|"
    "缓刑考.*?计算|刑期.*?止|依照|《.*?》|第.*?条|第.*?款|的|了|其|另|已|且"
)


def preprocess_line(content: str) -> str:
    line1 = re.sub(u"（.*?）", "", content)
    line2 = re.sub("[%s]+" % PUNCTUATION, "", line1)
    return REDUNDANT_PATTERN.sub("", line2)


def load_cases(input_path: Path) -> list[str]:
    processed_cases: list[str] = []
    with input_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            parts = raw_line.rstrip("\n").split("\t", maxsplit=1)
            if len(parts) != 2:
                continue
            location, content = parts
            cleaned = preprocess_line(content)
            if 100 < len(cleaned) < 400 and cleaned.startswith("被告人") and "保险" not in cleaned:
                processed_cases.append(f"{location}\t{cleaned}")
    return processed_cases


def write_cases(cases: list[str], output_paths: list[Path]) -> None:
    for output_path in output_paths:
        with output_path.open("w", encoding="utf-8") as f:
            for idx, case in enumerate(cases, start=1):
                f.write(f"{idx}\t{case}\n")


def main() -> None:
    repo = repo_root(__file__)
    base_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(description="预处理原始裁判文书数据。")
    parser.add_argument(
        "--input",
        default=str(base_dir / "original_data.txt"),
        help="原始数据文件，格式为“地区\\t案情文本”。",
    )
    parser.add_argument(
        "--output",
        default=str(base_dir / "preprocessed_data.txt"),
        help="主输出文件。",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机打乱样本时使用的种子，默认 42。",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    legacy_output = output_path.with_name("processed_data.txt")
    if not input_path.exists():
        raise FileNotFoundError(f"原始数据文件不存在: {input_path}")

    print_step(f"读取原始数据: {input_path}")
    cases = load_cases(input_path)
    if not cases:
        raise RuntimeError("没有生成任何预处理样本，请检查 original_data.txt 的格式是否为“地区\\t案情文本”。")
    random.Random(args.seed).shuffle(cases)

    write_cases(cases, [output_path, legacy_output])
    print_success(f"数据预处理完成，共保留 {len(cases)} 条样本。")
    print_step(f"主输出: {output_path.relative_to(repo) if output_path.is_relative_to(repo) else output_path}")
    if legacy_output != output_path:
        print_step(f"兼容输出: {legacy_output.relative_to(repo) if legacy_output.is_relative_to(repo) else legacy_output}")


if __name__ == "__main__":
    main()
