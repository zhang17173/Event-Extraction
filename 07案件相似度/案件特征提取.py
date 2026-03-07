# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_utils import find_crf_test, find_ltp_data_dir, print_step, print_success, print_warning, run_command

try:
    from pyltp import NamedEntityRecognizer
    from pyltp import Postagger
    from pyltp import Segmentor
except ImportError:
    Segmentor = Postagger = NamedEntityRecognizer = None

from utils import extract_seg
from utils import find_element
from utils import remove_duplicate_elements
from utils import sentence_result

PUNCTUATION = '''，。、:；（）ＸX×xa"“”,<《》'''
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


def preprocess_text(text: str) -> str:
    line1 = re.sub(u"（.*?）", "", text)
    return re.sub("[%s]+" % PUNCTUATION, "", line1)


def case_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache_meta(meta_path: Path) -> dict[str, str]:
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache_meta(meta_path: Path, case_text: str) -> None:
    meta_path.write_text(json.dumps({"case_hash": case_hash(case_text)}, ensure_ascii=False, indent=2), encoding="utf-8")


def cache_matches(meta_path: Path, case_text: str) -> bool:
    return load_cache_meta(meta_path).get("case_hash") == case_hash(case_text)


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
    return normalized


def run_ltp(text: str, lexicon_path: Path) -> tuple[list[str], list[str], list[str]]:
    if Segmentor is None:
        raise RuntimeError("未安装 pyltp。")
    ltp_dir = find_ltp_data_dir()
    segmentor = Segmentor()
    postagger = Postagger()
    recognizer = NamedEntityRecognizer()
    try:
        segmentor.load_with_lexicon(str(ltp_dir / "cws.model"), str(lexicon_path))
        seg_list = normalize_segmentation(list(segmentor.segment(text)))
        postagger.load(str(ltp_dir / "pos.model"))
        postags = list(postagger.postag(seg_list))
        recognizer.load(str(ltp_dir / "ner.model"))
        netags = list(recognizer.recognize(seg_list, postags))
        return seg_list, postags, netags
    finally:
        for model in (segmentor, postagger, recognizer):
            try:
                model.release()
            except Exception:
                pass


def merge_tagged_words(rows: list[list[str]]) -> tuple[list[str], list[str]]:
    words = []
    element_types = []
    index = 0
    while index < len(rows):
        row = rows[index]
        tag = row[-1]
        if "S" in tag:
            words.append(row[0])
            element_types.append(tag[-1])
        elif "B" in tag:
            current = row[0]
            current_type = tag[-1]
            index += 1
            while index < len(rows) and ("I" in rows[index][-1] or "E" in rows[index][-1]):
                current += rows[index][0]
                if "E" in rows[index][-1]:
                    break
                index += 1
            words.append(current)
            element_types.append(current_type)
        index += 1
    return words, element_types


def get_event_elements(case_file: Path) -> dict[str, list[str]]:
    rows = [line.strip("\n").split("\t") for line in case_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    words, element_types = merge_tagged_words(rows)
    result = {"事故类型": [], "罪名": [], "主次责任": [], "减刑因素": [], "加刑因素": [], "判决结果": []}
    for word, element_type in zip(words, element_types):
        mapping = {"T": "事故类型", "K": "罪名", "D": "主次责任", "P": "减刑因素", "N": "加刑因素", "R": "判决结果"}
        if element_type in mapping:
            result[mapping[element_type]].append(word)

    case_text = "".join(row[0] for row in rows)
    if "无证" in case_text or "驾驶资格" in case_text:
        result["加刑因素"].append("无证驾驶")
    if "无号牌" in case_text or "牌照" in case_text or "无牌" in case_text:
        result["加刑因素"].append("无牌驾驶")
    if "酒" in case_text:
        result["加刑因素"].append("酒后驾驶")
    if "吸毒" in case_text or "毒品" in case_text or "毒驾" in case_text:
        result["加刑因素"].append("吸毒后驾驶")
    if "超载" in case_text:
        result["加刑因素"].append("超载")
    if "逃逸" in case_text or "逃离" in case_text:
        result["加刑因素"].append("逃逸")
    if ("有前科" in case_text or "有犯罪前科" in case_text) and ("无前科" not in case_text and "无犯罪前科" not in case_text):
        result["加刑因素"].append("有犯罪前科")
    return {key: remove_duplicate_elements(value) for key, value in result.items()}


def get_patterns_from_dict(event_elements: dict[str, list[str]], case_text: str, label: int) -> dict[str, str | int]:
    patterns = {
        "04责任认定": find_element(event_elements["主次责任"], "全部责任"),
        "05是否酒后驾驶": find_element(event_elements["加刑因素"], "酒"),
        "06是否吸毒后驾驶": find_element(event_elements["加刑因素"], "毒"),
        "07是否无证驾驶": find_element(event_elements["加刑因素"], "驾驶证", "证"),
        "08是否无牌驾驶": find_element(event_elements["加刑因素"], "牌照", "牌"),
        "09是否不安全驾驶": find_element(event_elements["加刑因素"], "安全"),
        "10是否超载": find_element(event_elements["加刑因素"], "超载"),
        "11是否逃逸": find_element(event_elements["加刑因素"], "逃逸", "逃离"),
        "12是否抢救伤者": find_element(event_elements["减刑因素"], "抢救", "施救"),
        "13是否报警": find_element(event_elements["减刑因素"], "报警", "自首", "投案"),
        "14是否现场等待": find_element(event_elements["减刑因素"], "现场", "等候"),
        "15是否赔偿": find_element(event_elements["减刑因素"], "赔偿"),
        "16是否认罪": find_element(event_elements["减刑因素"], "认罪"),
        "18是否初犯偶犯": "0" if find_element(event_elements["加刑因素"], "前科") == "1" else "1",
        "判决结果": label,
    }
    patterns["01死亡人数"], patterns["02重伤人数"], _ = extract_seg(case_text)
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


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="提取单个案件特征，并查找结构相同的历史案件。")
    parser.add_argument("--case", default=str(script_dir / "case.txt"), help="输入案件文本。")
    parser.add_argument("--feature-db", default=str(ROOT / "06判决结果预测" / "特征提取" / "data.csv"), help="历史案件特征库。")
    parser.add_argument("--corpus", default=str(ROOT / "01数据预处理" / "preprocessed_data.txt"), help="历史案件文本库。")
    args = parser.parse_args()

    case_path = Path(args.case).resolve()
    feature_db_path = Path(args.feature_db).resolve()
    corpus_path = Path(args.corpus).resolve()
    if not case_path.exists():
        raise FileNotFoundError(f"案件文本不存在: {case_path}")
    if not feature_db_path.exists():
        raise FileNotFoundError(f"历史特征库不存在: {feature_db_path}")
    if not corpus_path.exists():
        raise FileNotFoundError(f"历史案件文本库不存在: {corpus_path}")

    lexicon_path = ROOT / "02分词" / "分词算法" / "05LTP分词" / "dict"
    segment_output_path = script_dir / "分词_词性标注_命名实体识别_结果.txt"
    crf_output_path = script_dir / "CRF结果.txt"
    pattern_output_path = script_dir / "pattern.csv"
    similar_output_path = script_dir / "类似案件.txt"
    segment_meta_path = script_dir / ".segment_cache_meta.json"
    crf_meta_path = script_dir / ".crf_cache_meta.json"

    case_text = preprocess_text(case_path.read_text(encoding="utf-8").strip())
    (script_dir / "preprocessed_data.txt").write_text(case_text + "\n", encoding="utf-8")

    if Segmentor is not None:
        try:
            print_step("运行 LTP 处理单个案件")
            seg_list, postags, netags = run_ltp(case_text, lexicon_path)
            with segment_output_path.open("w", encoding="utf-8") as f:
                for word, postag, netag in zip(seg_list, postags, netags):
                    if word == "\n":
                        f.write("\n")
                    else:
                        f.write(f"{word} {postag} {netag}\n")
            save_cache_meta(segment_meta_path, case_text)
        except Exception as exc:
            if segment_output_path.exists() and cache_matches(segment_meta_path, case_text):
                print_warning(f"LTP 当前不可用，继续使用当前案件对应的分词缓存: {exc}")
            else:
                raise RuntimeError(f"LTP 当前不可用，且当前案件没有可用的分词缓存: {exc}") from exc
    elif not (segment_output_path.exists() and cache_matches(segment_meta_path, case_text)):
        raise RuntimeError("未安装 pyltp，且当前案件没有可用的分词缓存。请安装 pyltp 后重新运行。")
    else:
        print_warning("未安装 pyltp，继续使用当前案件对应的分词缓存。")

    crf_test = find_crf_test()
    if crf_test is not None and segment_output_path.exists():
        try:
            result = run_command(
                [str(crf_test), "-m", str(ROOT / "03基于CRF的事件要素抽取" / "实验" / "05" / "model"), str(segment_output_path)],
                cwd=ROOT,
                capture_output=True,
                description="单案 CRF 事件抽取",
            )
            crf_output_path.write_text(result.stdout, encoding="utf-8")
            save_cache_meta(crf_meta_path, case_text)
        except Exception as exc:
            if crf_output_path.exists() and cache_matches(crf_meta_path, case_text):
                print_warning(f"CRF 当前不可执行，继续使用当前案件对应的 CRF 缓存: {exc}")
            else:
                raise RuntimeError(f"CRF 当前不可执行，且当前案件没有可用的 CRF 缓存: {exc}") from exc
    elif not (crf_output_path.exists() and cache_matches(crf_meta_path, case_text)):
        raise RuntimeError("缺少当前案件对应的 CRF 输出文件，且当前环境没有可用的 crf_test。")
    else:
        print_warning("未找到可用的 crf_test，继续使用当前案件对应的 CRF 缓存。")

    event_elements = get_event_elements(crf_output_path)
    sentence_months = sentence_result(case_text)
    if sentence_months is None:
        raise RuntimeError("无法从当前案件文本中解析判决结果，不能继续做相似案件匹配。")
    label = classify_label(sentence_months)
    patterns = get_patterns_from_dict(event_elements, case_text, label)

    with pattern_output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, HEADERS)
        writer.writerow(patterns)

    with pattern_output_path.open("r", encoding="utf-8") as f:
        target_row = next(csv.reader(f))
    with feature_db_path.open("r", encoding="utf-8") as f:
        feature_rows = list(csv.reader(f))
    matched_indexes = [idx for idx, row in enumerate(feature_rows) if row == target_row]
    corpus_rows = corpus_path.read_text(encoding="utf-8").splitlines()

    with similar_output_path.open("w", encoding="utf-8") as f:
        for matched_index in matched_indexes:
            if matched_index < len(corpus_rows):
                f.write(corpus_rows[matched_index] + "\n")

    print_success(f"特征已写入: {pattern_output_path}")
    print_success(f"相似案件已写入: {similar_output_path}")
    print_success(f"匹配到 {len(matched_indexes)} 个结构相同的历史案件。")


if __name__ == "__main__":
    main()
