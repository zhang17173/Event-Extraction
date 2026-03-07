# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_utils import find_ltp_data_dir, print_step, print_success, repo_root

try:
    from pyltp import Segmentor
except ImportError as exc:
    raise SystemExit("未安装 pyltp。请先安装依赖，或直接使用仓库中已有的分词结果文件。") from exc


def main() -> None:
    repo = repo_root(__file__)
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(description="使用 LTP 仅进行分词。")
    parser.add_argument(
        "--input",
        default=str(repo / "01数据预处理" / "preprocessed_data.txt"),
        help="预处理后的文本文件。",
    )
    parser.add_argument(
        "--output",
        default=str(script_dir / "仅分词结果.txt"),
        help="输出文件。",
    )
    parser.add_argument(
        "--dict",
        default=str(script_dir / "dict"),
        help="LTP 自定义词典路径。",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    lexicon_path = Path(args.dict).resolve()
    ltp_data_dir = find_ltp_data_dir()
    cws_model_path = ltp_data_dir / "cws.model"

    segmentor = Segmentor()
    try:
        segmentor.load_with_lexicon(str(cws_model_path), str(lexicon_path))
        with input_path.open("r", encoding="utf-8") as f_in, output_path.open("w", encoding="utf-8") as f_out:
            for line in f_in:
                words = list(segmentor.segment(line.strip()))
                f_out.write(" ".join(words) + "\n")
    finally:
        try:
            segmentor.release()
        except Exception:
            pass

    print_success("分词完成。")
    print_step(f"输出文件: {output_path.relative_to(repo) if output_path.is_relative_to(repo) else output_path}")


if __name__ == "__main__":
    main()
