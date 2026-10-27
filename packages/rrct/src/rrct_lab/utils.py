from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import pathlib
import random
import time
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from typing import Any

import numpy as np


def scalarize(value: Any) -> Any:
    if is_dataclass(value):
        return scalarize(asdict(value))
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, pathlib.Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): scalarize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [scalarize(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        scalarize(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def digest_object(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def deep_merge(base: dict[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    merged = {key: scalarize(value) for key, value in base.items()}
    for key, value in overlay.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, Mapping)
        ):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = scalarize(value)
    return merged


def get_dotted(mapping: Mapping[str, Any], dotted: str, default: Any = None) -> Any:
    node: Any = mapping
    for part in dotted.split("."):
        if not isinstance(node, Mapping) or part not in node:
            return default
        node = node[part]
    return node


def set_dotted(mapping: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    node = mapping
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


def parse_cli_value(text: str) -> Any:
    stripped = text.strip()
    lowered = stripped.lower()
    if lowered in {"true", "yes", "on"}:
        return True
    if lowered in {"false", "no", "off"}:
        return False
    if lowered in {"none", "null"}:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return stripped


def seed_everything(seed: int, deterministic: bool = True) -> np.random.Generator:
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic:
            torch.use_deterministic_algorithms(True, warn_only=True)
    except ImportError:
        pass
    return np.random.default_rng(seed)


def orthogonal_matrix(rng: np.random.Generator, dimension: int) -> np.ndarray:
    matrix = rng.normal(size=(dimension, dimension))
    q, r = np.linalg.qr(matrix)
    signs = np.sign(np.diag(r))
    signs[signs == 0] = 1
    return q * signs


def accuracy(predicted: Sequence[Any], target: Sequence[Any]) -> float:
    p = np.asarray(predicted)
    t = np.asarray(target)
    if p.shape != t.shape:
        raise ValueError(f"shape mismatch: {p.shape} != {t.shape}")
    return float(np.mean(p == t))


def mse(predicted: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean(np.square(np.asarray(predicted) - np.asarray(target))))


def r2_score(predicted: np.ndarray, target: np.ndarray) -> float:
    p = np.asarray(predicted, dtype=float)
    t = np.asarray(target, dtype=float)
    denominator = float(np.sum(np.square(t - t.mean(axis=0, keepdims=True))))
    if denominator <= 1e-15:
        return 1.0 if np.allclose(p, t) else 0.0
    numerator = float(np.sum(np.square(t - p)))
    return 1.0 - numerator / denominator


def entropy(probabilities: np.ndarray, axis: int = -1) -> np.ndarray:
    p = np.asarray(probabilities, dtype=float)
    p = np.clip(p, 1e-12, 1.0)
    return -np.sum(p * np.log(p), axis=axis)


def nearest_centroid_fit(features: np.ndarray, labels: np.ndarray) -> dict[int, np.ndarray]:
    return {
        int(label): features[labels == label].mean(axis=0)
        for label in np.unique(labels)
    }


def nearest_centroid_predict(
    features: np.ndarray, centroids: Mapping[int, np.ndarray]
) -> np.ndarray:
    labels = np.asarray(sorted(centroids), dtype=int)
    matrix = np.stack([centroids[int(label)] for label in labels])
    distances = np.sum(np.square(features[:, None, :] - matrix[None, :, :]), axis=-1)
    return labels[np.argmin(distances, axis=1)]



def atomic_write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_write_json(path: pathlib.Path, value: Any) -> None:
    atomic_write_text(
        path,
        json.dumps(scalarize(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
    )

def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(scalarize(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: pathlib.Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({str(key) for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: scalarize(row.get(key)) for key in fields})


class Timer:
    def __enter__(self) -> "Timer":
        self.started = time.perf_counter()
        self.elapsed = 0.0
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.elapsed = time.perf_counter() - self.started
