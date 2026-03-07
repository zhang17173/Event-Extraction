from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_utils import python_executable, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="一键执行判决结果预测主流程。")
    parser.add_argument("--skip-train", action="store_true", help="只生成数据，不训练模型。")
    args = parser.parse_args()

    command = [python_executable(), str(ROOT / "run_project.py")]
    if args.skip_train:
        command.append("--skip-train")
    run_command(command, cwd=ROOT)


if __name__ == "__main__":
    main()
