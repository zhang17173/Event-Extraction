#!/usr/bin/env python
# _*_coding:utf-8 _*_

from __future__ import annotations

import argparse
from pathlib import Path


def split_cases(input_path: Path, output_dir: Path) -> int:
    output_dir.mkdir(exist_ok=True)
    case_lines = []
    count = 0
    for old_file in output_dir.glob("*.txt"):
        old_file.unlink()

    def flush() -> None:
        nonlocal count, case_lines
        if not case_lines:
            return
        count += 1
        (output_dir / f"{count}.txt").write_text("".join(case_lines), encoding="utf-8")
        case_lines = []

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                case_lines.append(line)
            else:
                flush()
        flush()
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="将完整 CRF 数据切分成单个案件。")
    parser.add_argument("--input", default="完整数据.data", help="输入文件。")
    parser.add_argument("--output-dir", default="元数据", help="输出目录。")
    args = parser.parse_args()

    count = split_cases(Path(args.input), Path(args.output_dir))
    print(f"切分完成，共生成 {count} 个案件文件。")


if __name__ == "__main__":
    main()
