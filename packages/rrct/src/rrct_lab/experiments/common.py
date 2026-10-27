from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from rrct_lab.utils import get_dotted


def enabled(config: Mapping[str, Any], feature: str, cut: str | None = None) -> bool:
    value = bool(get_dotted(config, f"features.{feature}", False))
    if cut and bool(get_dotted(config, f"interventions.{cut}", False)):
        return False
    return value


def cfg(config: Mapping[str, Any], key: str, default: Any = None) -> Any:
    return get_dotted(config, key, default)
