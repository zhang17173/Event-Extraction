# coding=utf-8

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from utils import extract_seg
from utils import find_element
from utils import remove_duplicate_elements
from utils import sentence_result

HEADERS = [
    "01死亡人数",
    "02重伤人数",
    "04责任认定",
    "05是否酒后驾驶",
    "06是否吸毒后驾驶",
    "07是否无证驾驶",
    "08是否无牌驾驶",
    "09是否不安全驾驶",
    "10是否超载",
    "11是否逃逸",
    "12是否抢救伤者",
    "13是否报警",
    "14是否现场等待",
    "15是否赔偿",
    "16是否认罪",
    "18是否初犯偶犯",
    "判决结果",
]


def merge_tagged_words(rows: list[list[str]]) -> tuple[list[str], list[str]]:
    words: list[str] = []
    element_types: list[str] = []

    index = 0
    while index < len(rows):
        row = rows[index]
        tag = row[-1]
        if "S" in tag:
            words.append(row[0])
            element_types.append(tag[-1])
        elif "B" in tag:
            current_word = row[0]
            current_type = tag[-1]
            index += 1
            while index < len(rows) and ("I" in rows[index][-1] or "E" in rows[index][-1]):
                current_word += rows[index][0]
                if "E" in rows[index][-1]:
                    break
                index += 1
            words.append(current_word)
            element_types.append(current_type)
        index += 1
    return words, element_types


def get_event_elements(case_file: Path) -> dict[str, list[str]]:
    rows: list[list[str]] = []
    with case_file.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip("\n").split("\t")
            if len(parts) >= 2:
                rows.append(parts)

    words, element_types = merge_tagged_words(rows)
    categorized = {
        "事故类型": [],
        "罪名": [],
        "主次责任": [],
        "减刑因素": [],
        "加刑因素": [],
        "判决结果": [],
    }

    for word, element_type in zip(words, element_types):
        if element_type == "T":
            categorized["事故类型"].append(word)
        elif element_type == "K":
            categorized["罪名"].append(word)
        elif element_type == "D":
            categorized["主次责任"].append(word)
        elif element_type == "P":
            categorized["减刑因素"].append(word)
        elif element_type == "N":
            categorized["加刑因素"].append(word)
        elif element_type == "R":
            categorized["判决结果"].append(word)

    case_text = "".join(row[0] for row in rows)
    if "无证" in case_text or "驾驶资格" in case_text:
        categorized["加刑因素"].append("无证驾驶")
    if "无号牌" in case_text or "牌照" in case_text or "无牌" in case_text:
        categorized["加刑因素"].append("无牌驾驶")
    if "酒" in case_text:
        categorized["加刑因素"].append("酒后驾驶")
    if "吸毒" in case_text or "毒品" in case_text or "毒驾" in case_text:
        categorized["加刑因素"].append("吸毒后驾驶")
    if "超载" in case_text:
        categorized["加刑因素"].append("超载")
    if "逃逸" in case_text or "逃离" in case_text:
        categorized["加刑因素"].append("逃逸")
    if ("有前科" in case_text or "有犯罪前科" in case_text) and (
        "无前科" not in case_text and "无犯罪前科" not in case_text
    ):
        categorized["加刑因素"].append("有犯罪前科")

    return {key: remove_duplicate_elements(value) for key, value in categorized.items()}


def get_patterns_from_dict(event_elements: dict[str, list[str]]) -> dict[str, str | int]:
    patterns: dict[str, str | int] = {}
    patterns["01死亡人数"], patterns["02重伤人数"], patterns["03轻伤人数"] = extract_seg(
        "".join(event_elements["加刑因素"])
    )
    patterns["04责任认定"] = find_element(event_elements["主次责任"], "全部责任")
    patterns["05是否酒后驾驶"] = find_element(event_elements["加刑因素"], "酒")
    patterns["06是否吸毒后驾驶"] = find_element(event_elements["加刑因素"], "毒")
    patterns["07是否无证驾驶"] = find_element(event_elements["加刑因素"], "驾驶证", "证")
    patterns["08是否无牌驾驶"] = find_element(event_elements["加刑因素"], "牌照", "牌")
    patterns["09是否不安全驾驶"] = find_element(event_elements["加刑因素"], "安全")
    patterns["10是否超载"] = find_element(event_elements["加刑因素"], "超载")
    patterns["11是否逃逸"] = find_element(event_elements["加刑因素"], "逃逸", "逃离")
    patterns["12是否抢救伤者"] = find_element(event_elements["减刑因素"], "抢救", "施救")
    patterns["13是否报警"] = find_element(event_elements["减刑因素"], "报警", "自首", "投案")
    patterns["14是否现场等待"] = find_element(event_elements["减刑因素"], "现场", "等候")
    patterns["15是否赔偿"] = find_element(event_elements["减刑因素"], "赔偿")
    patterns["16是否认罪"] = find_element(event_elements["减刑因素"], "认罪")
    patterns["17是否如实供述"] = find_element(event_elements["减刑因素"], "如实")
    patterns["18是否初犯偶犯"] = "0" if find_element(event_elements["加刑因素"], "前科") == "1" else "1"
    return patterns


def classify_label(months: int) -> int:
    if 0 <= months <= 5:
        return 0
    if 6 <= months <= 18:
        return 1
    if 19 <= months <= 24:
        return 2
    if 25 <= months <= 36:
        return 3
    return 4


def label_cases(cases: list[str], classify: bool) -> list[int | None]:
    labels = [sentence_result(case) for case in cases]
    if classify:
        return [classify_label(label) if label is not None else None for label in labels]
    return labels


def write_csv(rows: list[dict[str, str | int]], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, HEADERS)
        writer.writerows(rows)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="从 CRF 结果中提取结构化特征。")
    parser.add_argument(
        "--cases",
        default=str(script_dir / "data" / "单个案件"),
        help="CRF 切分后的单案目录。",
    )
    parser.add_argument(
        "--preprocessed",
        default=str(script_dir.parents[1] / "01数据预处理" / "preprocessed_data.txt"),
        help="预处理后的案件文本。",
    )
    parser.add_argument(
        "--classification-output",
        default=str(script_dir / "data.csv"),
        help="分类任务输出。",
    )
    parser.add_argument(
        "--regression-output",
        default=str(script_dir / "data_for_regression.csv"),
        help="回归任务输出。",
    )
    args = parser.parse_args()

    cases_dir = Path(args.cases).resolve()
    preprocessed_path = Path(args.preprocessed).resolve()
    classification_output = Path(args.classification_output).resolve()
    regression_output = Path(args.regression_output).resolve()

    text_cases = preprocessed_path.read_text(encoding="utf-8").splitlines()
    regression_labels = label_cases(text_cases, classify=False)
    classification_labels = label_cases(text_cases, classify=True)

    case_files = sorted(cases_dir.glob("*.txt"), key=lambda path: int(path.stem))
    if len(case_files) != len(text_cases):
        raise RuntimeError(
            f"案件数量不一致：CRF 切分得到 {len(case_files)} 个案件，但预处理文本有 {len(text_cases)} 行。"
        )

    regression_rows: list[dict[str, str | int]] = []
    classification_rows: list[dict[str, str | int]] = []
    skipped_cases = 0

    for index, case_file in enumerate(case_files):
        regression_label = regression_labels[index]
        classification_label = classification_labels[index]
        if regression_label is None or classification_label is None:
            skipped_cases += 1
            continue

        event_elements = get_event_elements(case_file)
        patterns = get_patterns_from_dict(event_elements)

        patterns["01死亡人数"], patterns["02重伤人数"], patterns["03轻伤人数"] = extract_seg(text_cases[index])
        del patterns["03轻伤人数"]
        del patterns["17是否如实供述"]

        regression_row = dict(patterns)
        regression_row["判决结果"] = regression_label
        regression_rows.append(regression_row)

        classification_row = dict(patterns)
        classification_row["判决结果"] = classification_label
        classification_rows.append(classification_row)

    write_csv(regression_rows, regression_output)
    write_csv(classification_rows, classification_output)
    print(f"特征提取完成，共处理 {len(case_files)} 个案件。")
    if skipped_cases:
        print(f"跳过了 {skipped_cases} 个无法解析判决结果的案件。")
    print(f"分类数据: {classification_output}")
    print(f"回归数据: {regression_output}")


if __name__ == "__main__":
    main()
