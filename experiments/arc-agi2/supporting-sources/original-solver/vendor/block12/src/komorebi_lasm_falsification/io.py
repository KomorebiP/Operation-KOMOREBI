"""Canonical JSON helpers for PR-LASM Block 12.

Author: Komorebi P.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from komorebi_lasm_composition.model import canonical_value


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".partial")
    temporary.unlink(missing_ok=True)
    try:
        temporary.write_text(
            json.dumps(
                canonical_value(value), indent=2, sort_keys=True, allow_nan=False,
            ) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def sha256_file(path: str | Path) -> str:
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


__all__ = ["load_json", "sha256_file", "write_json"]
