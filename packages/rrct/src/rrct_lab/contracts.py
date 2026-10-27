from __future__ import annotations

import ast
import importlib.util
import pathlib
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from .config import DEFAULT_CONFIG
from .exceptions import ConfigError
from .registry import get_experiment
from .utils import get_dotted


@dataclass(frozen=True)
class ContractFinding:
    key: str
    status: str
    reason: str
    value: Any
    default: Any


# These keys are consumed by the common runner, result writer, safety layer,
# checkpoint manager, or sweep scheduler rather than by an experiment module.
COMMON_IMPLEMENTED_KEYS = {
    "experiment.family",
    "run.name",
    "run.seed",
    "run.repetitions",
    "run.output_root",
    "run.overwrite",
    "run.fail_on_warning",
    "run.strict_feature_contract",
    "run.fail_on_unused_setting",
    "run.resume",
    "run.atomic_results",
    "run.checkpoint_keep",
    "run.checkpoint_on_completion",
    "run.tags",
    "runtime.threads",
    "sweep.enabled",
    "sweep.execute",
    "sweep.max_runs",
    "sweep.parallel_workers",
    "sweep.resume",
    "sweep.retry_failures",
    "sweep.fail_fast",
    "sweep.state_file",
    "sweep.gpu_workers",
}

# The settings below are intentionally retained for interface compatibility,
# but not every family has a generic implementation for them yet.
COMMON_PARTIAL_KEYS = {
    "training.checkpoint_interval": "Generic model/optimizer checkpointing is not yet implemented for every trainable family; continuous runs use continuous.checkpoint_interval.",
    "training.checkpoint_keep": "Generic model checkpoint retention is not yet implemented for every trainable family; run.checkpoint_keep controls run-state checkpoints.",
    "runtime.memory_limit_mb": "Memory enforcement is cooperative and Python-allocation based; it is exact only at continuous-family checkpoint boundaries.",
    "runtime.timeout_seconds": "Timeout enforcement is cooperative for continuous runs and post-hoc for legacy in-process families.",
    "runtime.poll_interval_seconds": "Polling cadence is reserved for isolated workers and is not used by in-process runs.",
    "runtime.process_isolation": "Process isolation is used by the sweep scheduler but not every single-run family.",
    "run.save_rows": "Row persistence is implemented only for families that emit row-level records.",
    "run.save_models": "Only experiment families that emit model artifacts implement model saving.",
    "run.make_plots": "Plot generation is family-specific; disabling is safe, enabling is not universal.",
    "runtime.backend": "Backend selection is advisory unless a family explicitly reads it.",
    "runtime.dtype": "Dtype selection is family-specific.",
    "runtime.cuda_deterministic": "Torch families set deterministic algorithms globally, not every backend primitive.",
    "runtime.compile_model": "Compilation is not implemented by every trainable family.",
    "runtime.amp": "Automatic mixed precision is not implemented by every trainable family.",
    "evaluation.confidence_intervals": "Common confidence-interval generation is not yet universal.",
    "evaluation.bootstrap_samples": "Used only when a family implements bootstrap output.",
    "evaluation.save_predictions": "Prediction persistence is family-specific.",
}

SAFETY_KEYS = {
    f"safety.{key}" for key in DEFAULT_CONFIG["safety"]
}


def _flatten(mapping: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for key, value in mapping.items():
        dotted = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            if dotted == "sweep.grid":
                rows[dotted] = value
            else:
                rows.update(_flatten(value, dotted))
        else:
            rows[dotted] = value
    return rows


DEFAULT_LEAVES = _flatten(DEFAULT_CONFIG)


def _literal_subscript_path(node: ast.AST) -> str | None:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Subscript):
        index = current.slice
        if isinstance(index, ast.Constant) and isinstance(index.value, str):
            parts.append(index.value)
        else:
            return None
        current = current.value
    if isinstance(current, ast.Name) and current.id == "config":
        return ".".join(reversed(parts))
    return None


@lru_cache(maxsize=None)
def module_config_keys(module_name: str) -> frozenset[str]:
    spec = importlib.util.find_spec(module_name)
    if spec is None or spec.origin is None:
        return frozenset()
    path = pathlib.Path(spec.origin)
    if not path.is_file():
        return frozenset()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name: str | None = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name == "cfg" and len(node.args) >= 2:
                value = node.args[1]
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    keys.add(value.value)
            if name == "enabled" and len(node.args) >= 2:
                feature = node.args[1]
                if isinstance(feature, ast.Constant) and isinstance(feature.value, str):
                    keys.add(f"features.{feature.value}")
                if len(node.args) >= 3:
                    cut = node.args[2]
                    if isinstance(cut, ast.Constant) and isinstance(cut.value, str):
                        keys.add(f"interventions.{cut.value}")
        if isinstance(node, ast.Subscript):
            path_key = _literal_subscript_path(node)
            if path_key:
                keys.add(path_key)
    return frozenset(keys)


def family_used_keys(family: str) -> set[str]:
    spec = get_experiment(family)
    keys = set(COMMON_IMPLEMENTED_KEYS) | SAFETY_KEYS
    keys.update(module_config_keys(spec.module))
    keys.update(spec.runtime_owned_keys)
    if spec.checkpoint_interval_key:
        keys.add(spec.checkpoint_interval_key)
    if family == "smoke_matrix":
        keys.update(DEFAULT_LEAVES)
    return keys


def unknown_config_keys(config: dict[str, Any]) -> list[str]:
    actual = _flatten(config)
    unknown: list[str] = []
    for key in actual:
        if key in DEFAULT_LEAVES:
            continue
        if key.startswith("sweep.grid.") or key == "sweep.grid":
            continue
        unknown.append(key)
    return sorted(unknown)


def audit_config(config: dict[str, Any], family: str | None = None) -> dict[str, Any]:
    family = family or str(get_dotted(config, "experiment.family", ""))
    used = family_used_keys(family)
    actual = _flatten(config)
    findings: list[ContractFinding] = []
    sentinel = object()
    for key, value in actual.items():
        if key == "sweep.grid" or key.startswith("sweep.grid."):
            continue
        default = DEFAULT_LEAVES.get(key, sentinel)
        if default is sentinel:
            continue
        if value == default:
            continue
        if key in used:
            findings.append(
                ContractFinding(key, "implemented", "Read by the selected family or common runtime.", value, default)
            )
        elif key in COMMON_PARTIAL_KEYS:
            findings.append(
                ContractFinding(key, "partial", COMMON_PARTIAL_KEYS[key], value, default)
            )
        else:
            findings.append(
                ContractFinding(
                    key,
                    "unsupported",
                    f"No execution path for {family!r} reads this nondefault setting.",
                    value,
                    default,
                )
            )
    return {
        "schema": "rrct.lab.feature_contract.v1",
        "family": family,
        "unknown_keys": unknown_config_keys(config),
        "findings": [finding.__dict__ for finding in findings],
        "implemented_nondefault": sorted(f.key for f in findings if f.status == "implemented"),
        "partial_nondefault": sorted(f.key for f in findings if f.status == "partial"),
        "unsupported_nondefault": sorted(f.key for f in findings if f.status == "unsupported"),
    }


def enforce_contract(config: dict[str, Any], family: str | None = None) -> dict[str, Any]:
    report = audit_config(config, family)
    if report["unknown_keys"]:
        raise ConfigError(
            "unknown configuration keys: " + ", ".join(report["unknown_keys"])
        )
    strict = bool(get_dotted(config, "run.strict_feature_contract", True))
    fail_unused = bool(get_dotted(config, "run.fail_on_unused_setting", True))
    if strict and fail_unused and report["unsupported_nondefault"]:
        raise ConfigError(
            "nondefault settings are unsupported by the selected experiment: "
            + ", ".join(report["unsupported_nondefault"])
        )
    return report


def key_status_for_family(key: str, family: str) -> tuple[str, str]:
    if key in family_used_keys(family):
        return "implemented", "Read by experiment or common runtime."
    if key in COMMON_PARTIAL_KEYS:
        return "partial", COMMON_PARTIAL_KEYS[key]
    return "unsupported", "No detected execution path in this family."
