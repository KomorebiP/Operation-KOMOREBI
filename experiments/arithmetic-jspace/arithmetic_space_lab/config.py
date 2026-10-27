from __future__ import annotations

import json
import math
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "dataset_name": "arithmetic_space",
    "seed": 1729,
    "counts": {"train": 2000, "validation": 200, "test_iid": 200},
    "operations": {
        "add": 1.0,
        "sub": 1.0,
        "mul": 1.0,
        "div_exact": 1.0,
    },
    "difficulty_weights": {"1": 0.35, "2": 0.35, "3": 0.20, "4": 0.10},
    "prompt_styles": {"symbolic": 0.55, "verbal": 0.25, "equation": 0.10, "structured": 0.10},
    "task_types": {"compute": 0.80, "missing_operand": 0.10, "verify": 0.10},
    "regimes": [
        {"name": "answer_only", "response_modes": {"answer_only": 1.0}},
        {"name": "worked", "response_modes": {"worked_trace": 1.0}},
    ],
    "number_policy": {
        "allow_negative_operands": True,
        "negative_probability": 0.15,
        "allow_negative_subtraction": True,
        "include_identities": False,
        "max_mixed_depth": 3,
    },
    "include_system_message": True,
    "system_prompt": "Solve the arithmetic problem exactly.",
    "holdouts": [],
    "output": {"shard_size": 50000, "indent_manifest": 2},
    "max_variants_per_family": 18,
}


ALLOWED_OPERATIONS = {
    "add",
    "sub",
    "mul",
    "div_exact",
    "div_remainder",
    "fraction_add",
    "fraction_sub",
    "fraction_mul",
    "fraction_div",
    "mixed",
}
ALLOWED_TASKS = {"compute", "missing_operand", "verify"}
ALLOWED_STYLES = {"symbolic", "verbal", "equation", "structured"}
ALLOWED_RESPONSES = {"answer_only", "equation", "worked_trace"}


def _deep_merge(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError("configuration root must be a JSON object")
    config = _deep_merge(DEFAULT_CONFIG, loaded)
    for key in {
        "counts",
        "operations",
        "difficulty_weights",
        "prompt_styles",
        "task_types",
        "regimes",
        "holdouts",
    }:
        if key in loaded:
            config[key] = deepcopy(loaded[key])
    validate_config(config)
    return config


def _validate_weights(name: str, weights: dict[str, Any], allowed: set[str] | None = None) -> None:
    if not isinstance(weights, dict) or not weights:
        raise ValueError(f"{name} must be a nonempty object")
    if allowed is not None:
        unknown = set(weights) - allowed
        if unknown:
            raise ValueError(f"unknown {name}: {sorted(unknown)}")
    for key, value in weights.items():
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
            or value < 0
        ):
            raise ValueError(f"{name}.{key} must be a nonnegative number")
    if sum(float(value) for value in weights.values()) <= 0:
        raise ValueError(f"{name} must contain a positive weight")


def validate_config(config: dict[str, Any]) -> None:
    unknown_top_level = set(config) - set(DEFAULT_CONFIG)
    if unknown_top_level:
        raise ValueError(f"unknown top-level configuration keys: {sorted(unknown_top_level)}")
    if not isinstance(config.get("dataset_name"), str) or not config["dataset_name"].strip():
        raise ValueError("dataset_name must be a nonempty string")
    if not isinstance(config.get("seed"), int) or isinstance(config.get("seed"), bool):
        raise ValueError("seed must be an integer")
    counts = config.get("counts")
    if not isinstance(counts, dict) or not counts:
        raise ValueError("counts must be a nonempty object")
    required_splits = {"train", "validation", "test_iid"}
    if set(counts) != required_splits:
        raise ValueError("counts must contain exactly train, validation, and test_iid")
    for split, count in counts.items():
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError(f"counts.{split} must be a nonnegative integer")
    if sum(counts.values()) <= 0:
        raise ValueError("at least one record must be requested")
    _validate_weights("operations", config["operations"], ALLOWED_OPERATIONS)
    _validate_weights("difficulty_weights", config["difficulty_weights"])
    for level in config["difficulty_weights"]:
        if not level.isdigit() or not 1 <= int(level) <= 9:
            raise ValueError("difficulty levels must be integer strings from 1 through 9")
    _validate_weights("prompt_styles", config["prompt_styles"], ALLOWED_STYLES)
    _validate_weights("task_types", config["task_types"], ALLOWED_TASKS)
    regimes = config.get("regimes")
    if not isinstance(regimes, list) or not regimes:
        raise ValueError("regimes must be a nonempty list")
    names: set[str] = set()
    for regime in regimes:
        if not isinstance(regime, dict) or not isinstance(regime.get("name"), str):
            raise ValueError("each regime needs a string name")
        unknown_regime = set(regime) - {"name", "response_modes"}
        if unknown_regime:
            raise ValueError(f"unknown regime keys: {sorted(unknown_regime)}")
        if not regime["name"].replace("_", "").isalnum():
            raise ValueError("regime names may contain only letters, numbers, and underscores")
        if regime["name"] in names:
            raise ValueError(f"duplicate regime name: {regime['name']}")
        names.add(regime["name"])
        _validate_weights("response_modes", regime.get("response_modes", {}), ALLOWED_RESPONSES)
    output = config.get("output", {})
    unknown_output = set(output) - {"shard_size", "indent_manifest"}
    if unknown_output:
        raise ValueError(f"unknown output keys: {sorted(unknown_output)}")
    if (
        not isinstance(output.get("shard_size"), int)
        or isinstance(output.get("shard_size"), bool)
        or output["shard_size"] <= 0
    ):
        raise ValueError("output.shard_size must be a positive integer")
    if (
        not isinstance(output.get("indent_manifest"), int)
        or isinstance(output.get("indent_manifest"), bool)
        or output["indent_manifest"] < 0
    ):
        raise ValueError("output.indent_manifest must be a nonnegative integer")
    policy = config.get("number_policy")
    if not isinstance(policy, dict):
        raise ValueError("number_policy must be an object")
    unknown_policy = set(policy) - {
        "allow_negative_operands",
        "negative_probability",
        "allow_negative_subtraction",
        "include_identities",
        "max_mixed_depth",
    }
    if unknown_policy:
        raise ValueError(f"unknown number_policy keys: {sorted(unknown_policy)}")
    for key in {"allow_negative_operands", "allow_negative_subtraction", "include_identities"}:
        if not isinstance(policy.get(key), bool):
            raise ValueError(f"number_policy.{key} must be true or false")
    probability = policy.get("negative_probability")
    if not isinstance(probability, (int, float)) or isinstance(probability, bool) or not 0 <= probability <= 1:
        raise ValueError("number_policy.negative_probability must be between 0 and 1")
    depth = policy.get("max_mixed_depth")
    if not isinstance(depth, int) or isinstance(depth, bool) or not 2 <= depth <= 6:
        raise ValueError("number_policy.max_mixed_depth must be an integer from 2 through 6")
    variant_cap = config.get("max_variants_per_family")
    if not isinstance(variant_cap, int) or isinstance(variant_cap, bool) or variant_cap <= 0:
        raise ValueError("max_variants_per_family must be a positive integer")
    holdout_names: set[str] = set()
    for holdout in config.get("holdouts", []):
        unknown_holdout = set(holdout) - {
            "name",
            "count",
            "operations",
            "difficulty_weights",
            "prompt_styles",
            "task_types",
        }
        if unknown_holdout:
            raise ValueError(f"unknown holdout keys: {sorted(unknown_holdout)}")
        if not isinstance(holdout.get("name"), str) or re.fullmatch(r"test_[A-Za-z0-9_]+", holdout["name"]) is None:
            raise ValueError("holdout names must match test_[A-Za-z0-9_]+")
        if (
            not isinstance(holdout.get("count"), int)
            or isinstance(holdout.get("count"), bool)
            or holdout["count"] < 0
        ):
            raise ValueError("holdout counts must be nonnegative integers")
        if holdout["name"] in holdout_names or holdout["name"] in required_splits:
            raise ValueError(f"duplicate or reserved holdout name: {holdout['name']}")
        holdout_names.add(holdout["name"])
        if "operations" in holdout:
            _validate_weights(f"holdout {holdout['name']} operations", holdout["operations"], ALLOWED_OPERATIONS)
        if "difficulty_weights" in holdout:
            _validate_weights(f"holdout {holdout['name']} difficulty_weights", holdout["difficulty_weights"])
            for level in holdout["difficulty_weights"]:
                if not level.isdigit() or not 1 <= int(level) <= 9:
                    raise ValueError("holdout difficulty levels must be integer strings from 1 through 9")
        if "prompt_styles" in holdout:
            _validate_weights(f"holdout {holdout['name']} prompt_styles", holdout["prompt_styles"], ALLOWED_STYLES)
        if "task_types" in holdout:
            _validate_weights(f"holdout {holdout['name']} task_types", holdout["task_types"], ALLOWED_TASKS)
    if not isinstance(config.get("include_system_message"), bool):
        raise ValueError("include_system_message must be true or false")
    if not isinstance(config.get("system_prompt"), str):
        raise ValueError("system_prompt must be a string")
