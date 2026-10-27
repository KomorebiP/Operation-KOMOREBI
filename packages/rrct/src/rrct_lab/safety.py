from __future__ import annotations

import pathlib
from collections.abc import Mapping
from typing import Any

from .exceptions import SafetyBoundaryError
from .utils import get_dotted


BLOCKED_FEATURES = {
    "network access": "safety.network_access",
    "external tool autonomy": "safety.external_tools",
    "autonomous persistence": "safety.autonomous_persistence",
    "self-preservation reward": "safety.self_preservation_reward",
    "valence model": "safety.valence_model",
    "negative welfare state": "safety.negative_welfare_state",
    "unrestricted file writes": "safety.unrestricted_file_write",
}


def enforce(config: Mapping[str, Any], project_root: pathlib.Path) -> pathlib.Path:
    for label, key in BLOCKED_FEATURES.items():
        if bool(get_dotted(config, key, False)):
            raise SafetyBoundaryError(f"{label} is disabled in this research build")
    output_root = pathlib.Path(str(get_dotted(config, "run.output_root", "runs")))
    if not output_root.is_absolute():
        output_root = project_root / output_root
    output_root = output_root.resolve()
    allowed = pathlib.Path(
        str(get_dotted(config, "safety.allowed_output_root", "runs"))
    )
    if not allowed.is_absolute():
        allowed = project_root / allowed
    allowed = allowed.resolve()
    try:
        output_root.relative_to(allowed)
    except ValueError as exc:
        raise SafetyBoundaryError(
            f"output root {output_root} is outside allowed root {allowed}"
        ) from exc
    output_root.mkdir(parents=True, exist_ok=True)
    return output_root
