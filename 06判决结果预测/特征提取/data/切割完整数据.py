# -*- coding:utf-8 -*-

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_utils import print_step, print_success, reset_dir


def split_cases(input_path: Path, output_dir: Path) -> int:
    reset_dir(output_dir)
    case_lines: list[str] = []
    case_index = 1

    def flush_case() -> None:
        nonlocal case_index, case_lines
        if not case_lines:
            return
        (output_dir / f"{case_index}.txt").write_text("".join(case_lines), encoding="utf-8")
        case_index += 1
        case_lines = []

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                case_lines.append(line)
            else:
                flush_case()
        flush_case()
    return case_index - 1


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="将 CRF 输出切分为单个案件文件。")
    parser.add_argument(
        "--input",
        default=str(script_dir / "result.txt"),
        help="CRF 输出文件。",
    )
    parser.add_argument(
        "--output-dir",
        default=str(script_dir / "单个案件"),
        help="切分后的单案目录。",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()

    print_step(f"切分 CRF 输出: {input_path}")
    count = split_cases(input_path, output_dir)
    print_success(f"切分完成，共生成 {count} 个案件文件。")


if __name__ == "__main__":
    main()
