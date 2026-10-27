from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .config import DEFAULT_CONFIG
from .contracts import key_status_for_family
from .registry import EXPERIMENTS


def flatten(mapping: Mapping[str, Any], prefix: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, value in mapping.items():
        dotted = f"{prefix}.{key}" if prefix else key
        if isinstance(value, Mapping):
            if dotted == "sweep.grid":
                rows.append({"key": dotted, "default": value, "type": "dict"})
            else:
                rows.extend(flatten(value, dotted))
        else:
            rows.append(
                {
                    "key": dotted,
                    "default": value,
                    "type": type(value).__name__,
                }
            )
    return rows


def feature_rows() -> list[dict[str, Any]]:
    rows = flatten(DEFAULT_CONFIG)
    families = list(EXPERIMENTS)
    for row in rows:
        statuses: dict[str, str] = {}
        reasons: dict[str, str] = {}
        for family in families:
            status, reason = key_status_for_family(row["key"], family)
            statuses[family] = status
            reasons[family] = reason
        row["implemented_experiments"] = ",".join(
            family for family in families if statuses[family] == "implemented"
        )
        row["partial_experiments"] = ",".join(
            family for family in families if statuses[family] == "partial"
        )
        row["unsupported_experiments"] = ",".join(
            family for family in families if statuses[family] == "unsupported"
        )
        row["family_status"] = statuses
        row["family_reason"] = reasons
    return rows
