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
    from pyltp import NamedEntityRecognizer
    from pyltp import Postagger
    from pyltp import Segmentor
except ImportError as exc:
    raise SystemExit("未安装 pyltp。请先安装依赖，或直接使用仓库中已有的分词结果文件。") from exc


def normalize_segmentation(seg_list: list[str]) -> list[str]:
    normalized: list[str] = []
    for token in seg_list:
        if "\n" in token and token != "\n":
            parts = token.split("\n")
            for idx, part in enumerate(parts):
                if part:
                    normalized.append(part)
                if idx != len(parts) - 1:
                    normalized.append("\n")
        else:
            normalized.append(token)

    merged: list[str] = []
    index = 0
    while index < len(normalized):
        token = normalized[index]
        if token.isdigit():
            current = token
            while index + 1 < len(normalized) and normalized[index + 1].isdigit():
                index += 1
                current += normalized[index]
            merged.append(current)
        else:
            merged.append(token)
        index += 1
    return merged


def main() -> None:
    repo = repo_root(__file__)
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(description="使用 LTP 完成分词、词性标注和命名实体识别。")
    parser.add_argument(
        "--input",
        default=str(repo / "01数据预处理" / "preprocessed_data.txt"),
        help="预处理后的文本文件。",
    )
    parser.add_argument(
        "--output",
        default=str(script_dir / "分词_词性标注_命名实体识别_结果.txt"),
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
    if not input_path.exists():
        raise FileNotFoundError(f"预处理文本不存在: {input_path}")
    if not lexicon_path.exists():
        raise FileNotFoundError(f"LTP 自定义词典不存在: {lexicon_path}")

    print_step(f"读取预处理数据: {input_path}")
    content = input_path.read_text(encoding="utf-8")
    if not content.strip():
        raise RuntimeError("预处理文本为空，无法继续执行 LTP。")

    cws_model_path = ltp_data_dir / "cws.model"
    pos_model_path = ltp_data_dir / "pos.model"
    ner_model_path = ltp_data_dir / "ner.model"

    segmentor = Segmentor()
    postagger = Postagger()
    recognizer = NamedEntityRecognizer()

    try:
        segmentor.load_with_lexicon(str(cws_model_path), str(lexicon_path))
        raw_seg_list = list(segmentor.segment(content))
        seg_list = normalize_segmentation(raw_seg_list)

        postagger.load(str(pos_model_path))
        postags = list(postagger.postag(seg_list))

        recognizer.load(str(ner_model_path))
        netags = list(recognizer.recognize(seg_list, postags))
    finally:
        try:
            segmentor.release()
        except Exception:
            pass
        try:
            postagger.release()
        except Exception:
            pass
        try:
            recognizer.release()
        except Exception:
            pass

    with output_path.open("w", encoding="utf-8") as f:
        for word, postag, netag in zip(seg_list, postags, netags):
            if word == "\n":
                f.write("\n")
            else:
                f.write(f"{word} {postag} {netag}\n")

    print_success("LTP 处理完成。")
    print_step(f"输出文件: {output_path.relative_to(repo) if output_path.is_relative_to(repo) else output_path}")


if __name__ == "__main__":
    main()
