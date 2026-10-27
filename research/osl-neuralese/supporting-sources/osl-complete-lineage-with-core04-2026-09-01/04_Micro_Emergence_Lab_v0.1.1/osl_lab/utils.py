from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable, Iterator


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def save_json(path: str | Path, value: Any) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    return target


def iter_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Expected an object on line {line_number} of {path}")
            yield value


def write_jsonl(path: str | Path, records: Iterable[dict[str, Any]]) -> tuple[Path, int]:
    target = Path(path)
    ensure_dir(target.parent)
    count = 0
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False))
            handle.write("\n")
            count += 1
    return target, count


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def resolve_device(requested: str) -> str:
    normalized = requested.lower()
    if normalized not in {"auto", "cpu", "cuda"}:
        raise ValueError("device must be auto, cpu, or cuda")
    if normalized == "cpu":
        return "cpu"
    try:
        import torch
    except ImportError:
        if normalized == "cuda":
            raise RuntimeError("CUDA was requested but PyTorch is not installed")
        return "cpu"
    available = bool(torch.cuda.is_available())
    if normalized == "cuda" and not available:
        raise RuntimeError("CUDA was requested but torch.cuda.is_available() is false")
    return "cuda" if available else "cpu"


def environment_report() -> dict[str, Any]:
    matplotlib_cache = Path(tempfile.gettempdir()) / "osl-matplotlib-cache"
    matplotlib_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_cache))
    modules: dict[str, Any] = {}
    for name in ("numpy", "sklearn", "torch", "matplotlib"):
        try:
            module = __import__(name)
            modules[name] = {
                "installed": True,
                "version": str(getattr(module, "__version__", "unknown")),
            }
        except Exception as exc:
            modules[name] = {
                "installed": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
    cuda: dict[str, Any] = {"available": False}
    try:
        import torch

        cuda["available"] = bool(torch.cuda.is_available())
        cuda["torch_cuda_version"] = str(getattr(torch.version, "cuda", None))
        if cuda["available"]:
            cuda["device_count"] = int(torch.cuda.device_count())
            cuda["device_name"] = str(torch.cuda.get_device_name(0))
            properties = torch.cuda.get_device_properties(0)
            cuda["total_memory_bytes"] = int(properties.total_memory)
            cuda["compute_capability"] = [int(properties.major), int(properties.minor)]
    except ImportError:
        pass
    return {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "modules": modules,
        "cuda": cuda,
    }
