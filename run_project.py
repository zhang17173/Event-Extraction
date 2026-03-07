from __future__ import annotations

import argparse
from pathlib import Path

from project_utils import (
    ROOT,
    find_crf_test,
    find_ltp_data_dir,
    print_step,
    print_success,
    print_warning,
    python_module_available,
    python_executable,
    run_command,
)


PREPROCESS_SCRIPT = ROOT / "01数据预处理" / "data_preprocess.py"
LTP_SCRIPT = ROOT / "02分词" / "分词算法" / "05LTP分词" / "LTP分词_词性标注_命名实体识别.py"
SEGMENT_OUTPUT = ROOT / "02分词" / "分词算法" / "05LTP分词" / "分词_词性标注_命名实体识别_结果.txt"
CRF_MODEL = ROOT / "03基于CRF的事件要素抽取" / "实验" / "05" / "model"
CRF_OUTPUT = ROOT / "06判决结果预测" / "特征提取" / "data" / "result.txt"
SPLIT_SCRIPT = ROOT / "06判决结果预测" / "特征提取" / "data" / "切割完整数据.py"
FEATURE_SCRIPT = ROOT / "06判决结果预测" / "特征提取" / "特征提取.py"
CLASSIFY_PREP_SCRIPT = ROOT / "06判决结果预测" / "pytorch多分类" / "数据预处理.py"
CLASSIFY_TRAIN_SCRIPT = ROOT / "06判决结果预测" / "pytorch多分类" / "net.py"
CLASSIFICATION_DATA = ROOT / "06判决结果预测" / "特征提取" / "data.csv"
REGRESSION_DATA = ROOT / "06判决结果预测" / "特征提取" / "data_for_regression.csv"
def run_preprocess() -> None:
    print_step("步骤 1/5: 数据预处理")
    run_command([python_executable(), str(PREPROCESS_SCRIPT)], cwd=ROOT)


def run_segment() -> None:
    print_step("步骤 2/5: LTP 分词、词性标注、命名实体识别")
    run_command([python_executable(), str(LTP_SCRIPT)], cwd=ROOT)


def run_crf(use_cache: bool) -> bool:
    print_step("步骤 3/5: CRF 事件要素抽取")
    crf_test = find_crf_test()
    if crf_test is None:
        if use_cache and CRF_OUTPUT.exists():
            print_warning("未找到 crf_test，继续使用已有的 CRF 输出缓存。")
            return True
        print_warning("未找到 crf_test。请安装 CRF++，或设置环境变量 CRF_TEST_BIN。")
        return False

    if not SEGMENT_OUTPUT.exists():
        raise FileNotFoundError(f"LTP 输出不存在: {SEGMENT_OUTPUT}")

    try:
        result = run_command(
            [str(crf_test), "-m", str(CRF_MODEL), str(SEGMENT_OUTPUT)],
            cwd=ROOT,
            capture_output=True,
            description="CRF 事件抽取",
        )
    except Exception as exc:
        if use_cache:
            print_warning(f"CRF 可执行文件当前不可用: {exc}")
            if CRF_OUTPUT.exists():
                print_warning("继续使用已有的 CRF 输出缓存。")
                return True
            return False
        raise
    CRF_OUTPUT.write_text(result.stdout, encoding="utf-8")
    print_success(f"CRF 输出已写入: {CRF_OUTPUT}")
    return True


def run_features(use_cache: bool) -> None:
    print_step("步骤 4/5: 特征提取")
    if not run_crf(use_cache=use_cache):
        if use_cache and CLASSIFICATION_DATA.exists() and REGRESSION_DATA.exists():
            print_warning("CRF 未运行，直接使用已有特征文件。")
            return
        raise RuntimeError("无法执行 CRF 抽取，且没有可用的缓存特征文件。")

    run_command([python_executable(), str(SPLIT_SCRIPT), "--input", str(CRF_OUTPUT)], cwd=ROOT)
    run_command([python_executable(), str(FEATURE_SCRIPT)], cwd=ROOT)


def run_classifier_data() -> None:
    print_step("步骤 5/5: 生成分类模型数据")
    run_command([python_executable(), str(CLASSIFY_PREP_SCRIPT)], cwd=ROOT)


def run_classifier_train() -> None:
    print_step("训练多分类模型")
    run_command([python_executable(), str(CLASSIFY_TRAIN_SCRIPT)], cwd=ROOT)


def run_check() -> None:
    print_step("检查项目运行环境")
    print(f"Python: {python_executable()}")
    print(f"pyltp: {'已安装' if python_module_available('pyltp') else '未安装'}")
    try:
        ltp_dir = find_ltp_data_dir()
        print(f"LTP model: {ltp_dir}")
    except Exception:
        print("LTP model: 未找到")
    print(f"CRF model: {'存在' if CRF_MODEL.exists() else '缺失'}")
    print(f"CRF test: {find_crf_test() or '未找到'}")
    print(f"LTP 缓存输出: {'存在' if SEGMENT_OUTPUT.exists() else '缺失'}")
    print(f"分类特征缓存: {'存在' if CLASSIFICATION_DATA.exists() else '缺失'}")
    print(f"回归特征缓存: {'存在' if REGRESSION_DATA.exists() else '缺失'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="项目统一入口，适合初学者按步骤运行。")
    parser.add_argument(
        "--step",
        choices=["check", "preprocess", "segment", "features", "classifier-data", "train-classifier", "all"],
        default="all",
        help="指定要执行的步骤。",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="不使用已有缓存结果。默认会尽量复用仓库中已有结果，降低首次运行门槛。",
    )
    parser.add_argument(
        "--skip-train",
        action="store_true",
        help="在 all 模式下跳过模型训练，只生成中间数据。",
    )
    args = parser.parse_args()

    use_cache = not args.no_cache

    if args.step == "check":
        run_check()
    elif args.step == "preprocess":
        run_preprocess()
    elif args.step == "segment":
        run_segment()
    elif args.step == "features":
        run_features(use_cache=use_cache)
    elif args.step == "classifier-data":
        run_classifier_data()
    elif args.step == "train-classifier":
        run_classifier_train()
    else:
        run_preprocess()
        try:
            run_segment()
        except Exception as exc:
            if not use_cache:
                raise
            print_warning(f"LTP 步骤失败，将尝试复用缓存结果: {exc}")
        run_features(use_cache=use_cache)
        run_classifier_data()
        if not args.skip_train:
            run_classifier_train()


if __name__ == "__main__":
    main()
