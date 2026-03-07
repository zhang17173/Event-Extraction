from __future__ import annotations

import os
import shutil
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path
from typing import Iterable, Sequence


def repo_root(start: str | Path | None = None) -> Path:
    path = Path(start or __file__).resolve()
    if path.is_file():
        path = path.parent
    for current in [path, *path.parents]:
        if (current / ".git").exists():
            return current
    return Path(__file__).resolve().parent


ROOT = repo_root(__file__)


def root_path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


def env_path(name: str, default: str | Path | None = None) -> Path | None:
    value = os.environ.get(name)
    if value:
        return Path(value).expanduser().resolve()
    if default is None:
        return None
    return Path(default).expanduser().resolve()


def require_path(path: Path, description: str) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"{description}不存在: {path}")
    return path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def reset_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def remove_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def find_ltp_data_dir() -> Path:
    candidates = [
        env_path("LTP_DATA_DIR"),
        root_path("ltp_data_v3.4.0"),
        root_path("models", "ltp_data_v3.4.0"),
        root_path("..", "ltp_data_v3.4.0"),
    ]
    for candidate in candidates:
        if candidate and (candidate / "cws.model").exists():
            return candidate
    raise FileNotFoundError(
        "未找到 LTP 模型目录。请设置环境变量 LTP_DATA_DIR，并确保目录下包含 cws.model / pos.model / ner.model。"
    )


def find_executable(env_name: str, names: Sequence[str], extra_candidates: Iterable[Path] = ()) -> Path | None:
    configured = env_path(env_name)
    if configured and configured.exists():
        return configured

    for name in names:
        located = shutil.which(name)
        if located:
            return Path(located)

    for candidate in extra_candidates:
        if candidate.exists():
            return candidate
    return None


def find_crf_test() -> Path | None:
    extra_candidates: list[Path] = []
    if os.name == "nt":
        extra_candidates.append(root_path("03基于CRF的事件要素抽取", "实验", "05", "crf_test.exe"))
    return find_executable("CRF_TEST_BIN", ["crf_test"], extra_candidates)


def run_command(
    cmd: Sequence[str],
    cwd: Path | None = None,
    description: str | None = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            list(cmd),
            cwd=str(cwd) if cwd else None,
            check=True,
            text=True,
            capture_output=capture_output,
        )
    except FileNotFoundError as exc:
        detail = description or cmd[0]
        raise RuntimeError(f"未找到可执行命令: {detail}") from exc
    except subprocess.CalledProcessError as exc:
        detail = description or " ".join(cmd)
        stderr = exc.stderr.strip() if exc.stderr else ""
        message = f"命令执行失败: {detail}"
        if stderr:
            message += f"\n{stderr}"
        raise RuntimeError(message) from exc


def print_step(message: str) -> None:
    print(f"[INFO] {message}")


def print_warning(message: str) -> None:
    print(f"[WARN] {message}")


def print_success(message: str) -> None:
    print(f"[OK] {message}")


def python_executable() -> str:
    return sys.executable


def python_module_available(module_name: str) -> bool:
    return find_spec(module_name) is not None
