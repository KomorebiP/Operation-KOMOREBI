from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json

from .hashing import sha256_object


def verify_result_receipt(result: Mapping[str, Any]) -> None:
    expected = result.get("result_sha256")
    payload = {key: value for key, value in result.items() if key != "result_sha256"}
    actual = sha256_object(payload)
    if actual != expected:
        raise ValueError(f"Result receipt mismatch: expected {expected}, got {actual}")


def write_json(path: str | Path, obj: Mapping[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(dict(obj), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_and_verify_result(path: str | Path) -> dict[str, Any]:
    result = json.loads(Path(path).read_text(encoding="utf-8"))
    verify_result_receipt(result)
    return result
