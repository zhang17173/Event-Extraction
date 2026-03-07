# -*- coding:utf-8 -*-

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="检查标注数据中可能导致 CRF++ 训练失败的位置。")
    parser.add_argument("--input", default="new_train.data", help="待检查的数据文件。")
    parser.add_argument("--template", default="template01", help="CRF++ 模板文件。")
    parser.add_argument("--crf-learn", default="crf_learn", help="crf_learn 可执行文件。")
    args = parser.parse_args()

    input_path = Path(args.input)
    contents = input_path.read_text(encoding="utf-8").splitlines()
    lines_with_error = []
    blanks_count = 0
    chunk_index = 0
    file_name = Path(f"train{chunk_index}.data")

    for line_number, content in enumerate(contents):
        with file_name.open("a", encoding="utf-8") as f:
            f.write(content + "\n")
        if content in ("", "   "):
            blanks_count += 1
            if blanks_count % 2 == 0:
                chunk_index += 1
                result = subprocess.run(
                    [args.crf_learn, args.template, str(file_name), "model"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and Path("model").exists():
                    print(f"{file_name} 检查通过")
                    Path("model").unlink()
                else:
                    lines_with_error.append(line_number)
                file_name = Path(f"train{chunk_index}.data")

    print(lines_with_error)
    for idx in range(chunk_index + 1):
        temp_file = Path(f"train{idx}.data")
        if temp_file.exists():
            temp_file.unlink()


if __name__ == "__main__":
    main()
