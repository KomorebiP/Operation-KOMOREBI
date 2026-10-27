"""Execution dispatch for serialized Block 6 program records."""
from __future__ import annotations

import json
from typing import Any, Mapping

import numpy as np

from .common import freeze
from .structural import execute_family as execute_structural_family
from .targeted import TARGETED_FAMILY_EXECUTORS, execute_targeted_family


def execute_compiled(family: str, grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    if family in TARGETED_FAMILY_EXECUTORS:
        return execute_targeted_family(family, grid, dict(parameters))
    return execute_structural_family(family, grid, parameters)


def execute_spec(grid: Any, specification: str) -> tuple[tuple[int, ...], ...]:
    record = json.loads(specification)
    if not isinstance(record, dict) or set(record) != {"family", "parameters"}:
        raise ValueError("compiled specification must contain exactly family and parameters")
    return freeze(execute_compiled(str(record["family"]), grid, record["parameters"]))
