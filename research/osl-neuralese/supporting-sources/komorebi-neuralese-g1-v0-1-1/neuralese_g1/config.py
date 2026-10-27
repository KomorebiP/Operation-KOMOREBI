from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "komorebi.neuralese.g1.config.v1"
PROFILES = ("wiring", "smoke", "pilot")
TOP_LEVEL_KEYS = {
    "schema",
    "profile",
    "seed",
    "replication_seeds",
    "model",
    "workspace",
    "task",
    "training",
    "gates",
    "config_digest",
}
GROUP_KEYS = {
    "model": {
        "source_layer",
        "device",
        "dtype",
        "max_sequence_length",
        "local_files_only",
        "trust_remote_code",
        "strict_backbone_hash",
        "expected_model_type",
        "expected_architecture",
        "expected_hidden_size",
        "expected_layers",
        "attention_implementation",
    },
    "workspace": {"width", "steps", "injection_scale", "state_clip", "dropout"},
    "task": {
        "states",
        "train_base_problems",
        "validation_base_problems",
        "test_base_problems",
        "ood_base_problems",
        "train_chain_min",
        "train_chain_max",
        "ood_chain_min",
        "ood_chain_max",
    },
    "training": {
        "steps",
        "batch_size",
        "learning_rate",
        "weight_decay",
        "gradient_clip",
        "loss_scale_initial",
        "max_overflow_retries",
        "log_every",
        "eval_batch_size",
    },
    "gates": {
        "scientific_enabled",
        "recurrent_iid_min",
        "per_query_min",
        "zero_gap_min",
        "shuffle_gap_min",
        "feedback_gap_min",
        "ood_min",
    },
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def config_digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _finite_float(value: Any, label: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    result = float(value)
    if result != result or result in (float("inf"), -float("inf")):
        raise ValueError(f"{label} must be finite")
    if minimum is not None and result < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return result


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    unknown_top_level = set(config) - TOP_LEVEL_KEYS
    if unknown_top_level:
        raise ValueError(f"unknown top-level config keys: {sorted(unknown_top_level)}")
    if config.get("schema") != SCHEMA:
        raise ValueError(f"config schema must be {SCHEMA}")
    if config.get("profile") not in PROFILES:
        raise ValueError(f"profile must be one of {PROFILES}")
    _positive_int(config.get("seed"), "seed")
    for group in ("model", "workspace", "task", "training", "gates"):
        if not isinstance(config.get(group), dict):
            raise ValueError(f"missing mapping: {group}")
        unknown_group_keys = set(config[group]) - GROUP_KEYS[group]
        if unknown_group_keys:
            raise ValueError(
                f"unknown {group} config keys: {sorted(unknown_group_keys)}"
            )

    replication_seeds = config.get("replication_seeds")
    if replication_seeds is not None:
        if not isinstance(replication_seeds, list) or len(replication_seeds) < 3:
            raise ValueError("replication_seeds must contain at least three seeds")
        for index, value in enumerate(replication_seeds):
            _positive_int(value, f"replication_seeds[{index}]")
        if len(set(replication_seeds)) != len(replication_seeds):
            raise ValueError("replication_seeds must be distinct")
    if config["profile"] == "pilot":
        if replication_seeds is None or config["seed"] not in replication_seeds:
            raise ValueError("pilot seed must be one of the registered replication_seeds")
    elif replication_seeds is not None:
        raise ValueError("replication_seeds are registered only for the pilot profile")

    model = config["model"]
    if (
        isinstance(model.get("source_layer"), bool)
        or not isinstance(model.get("source_layer"), int)
        or model["source_layer"] < 0
    ):
        raise ValueError("model.source_layer must be a nonnegative integer")
    if model.get("device") not in ("cuda", "cpu"):
        raise ValueError("model.device must be cuda or cpu")
    if model.get("dtype") not in ("float16", "bfloat16", "float32"):
        raise ValueError("unsupported model.dtype")
    _positive_int(model.get("max_sequence_length"), "model.max_sequence_length")
    if model.get("local_files_only") is not True:
        raise ValueError("G1 requires model.local_files_only=true")
    if model.get("trust_remote_code") is not False:
        raise ValueError("G1 requires model.trust_remote_code=false")
    if not isinstance(model.get("strict_backbone_hash"), bool):
        raise ValueError("model.strict_backbone_hash must be boolean")
    for key in ("expected_model_type", "expected_architecture"):
        if not isinstance(model.get(key), str) or not model[key]:
            raise ValueError(f"model.{key} must be a nonempty string")
    _positive_int(model.get("expected_hidden_size"), "model.expected_hidden_size")
    _positive_int(model.get("expected_layers"), "model.expected_layers")
    if model.get("attention_implementation") != "eager":
        raise ValueError("G1 requires model.attention_implementation=eager")

    workspace = config["workspace"]
    _positive_int(workspace.get("width"), "workspace.width")
    _positive_int(workspace.get("steps"), "workspace.steps")
    if _finite_float(
        workspace.get("injection_scale"), "workspace.injection_scale", minimum=0.0
    ) <= 0.0:
        raise ValueError("workspace.injection_scale must be positive")
    _finite_float(workspace.get("state_clip"), "workspace.state_clip", minimum=0.0)
    dropout = _finite_float(workspace.get("dropout"), "workspace.dropout", minimum=0.0)
    if dropout >= 1.0:
        raise ValueError("workspace.dropout must be below 1")

    task = config["task"]
    states = _positive_int(task.get("states"), "task.states")
    if not 2 <= states <= 10:
        raise ValueError("task.states must be from 2 through 10")
    for key in (
        "train_base_problems",
        "validation_base_problems",
        "test_base_problems",
        "ood_base_problems",
        "train_chain_min",
        "train_chain_max",
        "ood_chain_min",
        "ood_chain_max",
    ):
        _positive_int(task.get(key), f"task.{key}")
    if task["train_chain_min"] > task["train_chain_max"]:
        raise ValueError("invalid training chain range")
    if task["ood_chain_min"] > task["ood_chain_max"]:
        raise ValueError("invalid OOD chain range")
    if task["ood_chain_min"] <= task["train_chain_max"]:
        raise ValueError("OOD chain range must begin above the training range")

    training = config["training"]
    for key in (
        "steps",
        "batch_size",
        "max_overflow_retries",
        "log_every",
        "eval_batch_size",
    ):
        _positive_int(training.get(key), f"training.{key}")
    if _finite_float(
        training.get("learning_rate"), "training.learning_rate", minimum=0.0
    ) <= 0.0:
        raise ValueError("training.learning_rate must be positive")
    _finite_float(training.get("weight_decay"), "training.weight_decay", minimum=0.0)
    if _finite_float(
        training.get("gradient_clip"), "training.gradient_clip", minimum=0.0
    ) <= 0.0:
        raise ValueError("training.gradient_clip must be positive")
    if _finite_float(
        training.get("loss_scale_initial"),
        "training.loss_scale_initial",
        minimum=0.0,
    ) <= 0.0:
        raise ValueError("training.loss_scale_initial must be positive")

    gates = config["gates"]
    if not isinstance(gates.get("scientific_enabled"), bool):
        raise ValueError("gates.scientific_enabled must be boolean")
    if gates["scientific_enabled"] != (config["profile"] == "pilot"):
        raise ValueError("scientific gates must be enabled exactly for the pilot profile")
    if gates["scientific_enabled"] and not model["strict_backbone_hash"]:
        raise ValueError("scientific evaluation requires strict_backbone_hash=true")
    for key in (
        "recurrent_iid_min",
        "per_query_min",
        "zero_gap_min",
        "shuffle_gap_min",
        "feedback_gap_min",
        "ood_min",
    ):
        threshold = _finite_float(gates.get(key), f"gates.{key}")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"gates.{key} must be in [0, 1]")
    return config


def load_config(path: str | Path, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    source = Path(path)
    config = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("configuration root must be a mapping")
    if "config_digest" in config:
        raise ValueError("source configuration must not contain config_digest")
    config = copy.deepcopy(config)
    for dotted_key, value in (overrides or {}).items():
        if dotted_key == "seed":
            config["seed"] = value
            continue
        group, separator, key = dotted_key.partition(".")
        if not separator or group not in config or not isinstance(config[group], dict):
            raise ValueError(f"invalid override key: {dotted_key}")
        config[group][key] = value
    validate_config(config)
    config["config_digest"] = config_digest(config)
    return config
