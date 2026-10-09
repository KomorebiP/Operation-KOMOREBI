from __future__ import annotations

from dataclasses import fields
from pathlib import Path
from typing import Any

from .api import AMSpdConfig, AMSpdResult
from .api import resume_model as _resume_model
from .model import AMSpdModel


def config_from_mapping(mapping: dict[str, Any]) -> AMSpdConfig:
    """Compatibility wrapper for configuration metadata."""

    allowed = {field.name for field in fields(AMSpdConfig)}
    values = {key: value for key, value in mapping.items() if key in allowed}
    if "reopen_fractions" in values:
        values["reopen_fractions"] = tuple(float(value) for value in values["reopen_fractions"])
    return AMSpdConfig(**values)


def config_from_model(model: AMSpdModel) -> AMSpdConfig:
    return config_from_mapping(model.config)


def resume_model(
    model: AMSpdModel | str | Path,
    *,
    additional_packets: int = 8,
    target_packet_budget: int | None = None,
    method: str | None = None,
    config: AMSpdConfig | None = None,
) -> AMSpdResult:
    """Compatibility wrapper for :func:`am_spd.api.resume_model`."""

    return _resume_model(
        model,
        config,
        additional_packets=additional_packets,
        target_packet_budget=target_packet_budget,
        method=method,  # type: ignore[arg-type]
    )
