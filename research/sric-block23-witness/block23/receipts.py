from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


CANONICAL_FLOAT_DECIMALS = 12


def _canonical_float(value: float) -> float | None:
    if not math.isfinite(value):
        return None
    rounded = round(float(value), CANONICAL_FLOAT_DECIMALS)
    return 0.0 if rounded == 0.0 else rounded


def json_ready(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return json_ready(obj.tolist())
    if isinstance(obj, np.generic):
        return json_ready(obj.item())
    if isinstance(obj, float):
        return _canonical_float(obj)
    if isinstance(obj, dict):
        return {str(k): json_ready(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_ready(v) for v in obj]
    return obj


def stable_bytes(obj: Any) -> bytes:
    return json.dumps(json_ready(obj), sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(obj: Any) -> str:
    return hashlib.sha256(stable_bytes(obj)).hexdigest()


def array_digest(x: np.ndarray) -> str:
    a = np.asarray(x)
    if np.issubdtype(a.dtype, np.floating):
        a = np.round(a.astype(np.float64, copy=False), CANONICAL_FLOAT_DECIMALS)
        a[a == 0.0] = 0.0
    a = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(str(a.dtype).encode())
    h.update(str(tuple(a.shape)).encode())
    h.update(a.tobytes())
    return h.hexdigest()


def compiled_record(compiled: Any) -> dict[str, Any]:
    projections = {}
    if compiled.projection is not None:
        projections = {k: array_digest(v) for k, v in sorted(compiled.projection.matrices.items())}
    return json_ready({
        "pre_certificate": compiled.pre_certificate,
        "selected_method": compiled.selected_method,
        "selected_rank": compiled.selected_rank,
        "metrics_by_system": compiled.metrics_by_system,
        "candidate_table": compiled.candidate_table,
        "unresolved_blocks": compiled.unresolved_blocks,
        "diagnostics": compiled.diagnostics,
        "projection_digests": projections,
    })


def write_json(path: str | Path, obj: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(json_ready(obj), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
