from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

_original_dumps = json.dumps


def _default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, pathlib.Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _patched_dumps(obj, *args, **kwargs):
    kwargs.setdefault("default", _default)
    return _original_dumps(obj, *args, **kwargs)

json.dumps = _patched_dumps

import analyze_edge

if __name__ == "__main__":
    raise SystemExit(analyze_edge.main())
