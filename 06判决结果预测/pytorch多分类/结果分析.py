from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="分析多分类结果。")
    parser.add_argument("--result", default=str(script_dir / "result.csv"), help="模型输出的 result.csv。")
    args = parser.parse_args()

    result_path = Path(args.result).resolve()
    if not result_path.exists():
        raise FileNotFoundError(f"结果文件不存在: {result_path}")
    rows = list(csv.reader(result_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError("结果文件为空，无法分析。")

    total = defaultdict(int)
    correct = defaultdict(int)
    errors = defaultdict(list)

    for row in rows:
        if len(row) < 3:
            continue
        true_label = row[-2]
        pred_label = row[-1]
        total[true_label] += 1
        if true_label == pred_label:
            correct[true_label] += 1
        else:
            errors[true_label].append(pred_label)

    total_count = sum(total.values())
    true_count = sum(correct.values())
    print(f"total: {total_count}")
    print(f"true: {true_count}")
    print("class\ttotal\ttrue\tfalse")
    for label in sorted(total.keys(), key=int):
        false_count = total[label] - correct[label]
        print(f"{label}\t{total[label]}\t{correct[label]}\t{false_count}")
        if errors[label]:
            print(f"class {label} 常见误判: {Counter(errors[label])}")


if __name__ == "__main__":
    main()
