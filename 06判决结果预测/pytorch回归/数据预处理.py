from __future__ import annotations

import argparse
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def split_rows(rows: list[list[str]], train_size: int, seed: int) -> tuple[list[list[str]], list[list[str]]]:
    rows = list(rows)
    random.Random(seed).shuffle(rows)
    if len(rows) <= train_size:
        split_at = max(1, int(len(rows) * 0.8))
    else:
        split_at = train_size
    return rows[:split_at], rows[split_at:]


def remove_error(rows: list[list[str]], output_path: Path | None = None) -> list[list[str]]:
    grouped: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[:-1])].append(row[-1])

    cleaned = []
    for row in rows:
        features = tuple(row[:-1])
        label = Counter(grouped[features]).most_common(1)[0][0]
        cleaned.append(list(features) + [label])

    if output_path is not None:
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(cleaned)
    return cleaned


def patterns_weight(input_path: Path, output_path: Path) -> None:
    data = np.loadtxt(input_path, delimiter=",", dtype=int)
    if data.ndim == 1:
        data = data.reshape(1, -1)

    rows = []
    for item in data:
        rows.append(
            {
                "01伤亡情况": int(item[0]) * 80 + int(item[1]) * 30,
                "02责任认定": 30 if int(item[2]) == 1 else 10,
                "03违章情况": int(item[3]) * 15
                + int(item[4]) * 20
                + int(item[5]) * 10
                + int(item[6]) * 10
                + int(item[7]) * 5
                + int(item[8]) * 10
                + int(item[9]) * 30,
                "04案后表现": int(item[10]) * (-15)
                + int(item[11]) * (-30)
                + int(item[12]) * (-15)
                + int(item[13]) * (-25)
                + int(item[14]) * (-15),
                "05初犯偶犯": 30 if int(item[15]) == 0 else -15,
                "06是否逃逸": int(item[9]) * 100,
                "07判决结果": int(item[-1]),
            }
        )

    headers = ["01伤亡情况", "02责任认定", "03违章情况", "04案后表现", "05初犯偶犯", "06是否逃逸", "07判决结果"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, headers)
        writer.writerows(rows)


def write_rows(rows: list[list[str]], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    data_dir.mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(description="生成回归模型训练数据。")
    parser.add_argument(
        "--input",
        default=str(script_dir.parent / "特征提取" / "data_for_regression.csv"),
        help="特征提取阶段生成的回归数据。",
    )
    parser.add_argument("--seed", type=int, default=42, help="随机种子。")
    parser.add_argument("--train-size", type=int, default=20000, help="训练集最大样本数。")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    cleaned_path = data_dir / "data_without_error.csv"
    train16_path = data_dir / "train16.csv"
    test16_path = data_dir / "test16.csv"
    train6_path = data_dir / "train6.csv"
    test6_path = data_dir / "test6.csv"

    raw_rows = list(csv.reader(input_path.open("r", encoding="utf-8")))
    train_rows, test_rows = split_rows(raw_rows, args.train_size, args.seed)
    cleaned_train_rows = remove_error(train_rows, cleaned_path)
    write_rows(cleaned_train_rows, train16_path)
    write_rows(test_rows, test16_path)
    patterns_weight(train16_path, train6_path)
    patterns_weight(test16_path, test6_path)

    print("回归数据预处理完成。")
    print(f"训练集: {train6_path}")
    print(f"测试集: {test6_path}")


if __name__ == "__main__":
    main()
