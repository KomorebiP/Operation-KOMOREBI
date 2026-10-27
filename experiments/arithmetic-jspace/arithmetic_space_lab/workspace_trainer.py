from __future__ import annotations

"""Deterministic online trainer for the v0.4 arithmetic-workspace study.

This module deliberately keeps the training objective ordinary: a causal
language-model loss over the answer bytes only.  Workspace measurements are
performed after training by separate modules.  The trainer's responsibilities
are reproducible paired streams, durable resumption, honest free-generation
evaluation, and enough telemetry to audit a long Windows/PowerShell run.
"""

import dataclasses
import hashlib
import json
import math
import os
import platform
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    import torch
    import torch.nn.functional as F
except ImportError as error:  # pragma: no cover - Windows preflight covers this
    raise ImportError(
        "PyTorch is required for workspace training. Use the selected training environment."
    ) from error

from .byte_tokenizer import ByteTokenizer
from .tiny_model import ModelConfig, TinyDecoderLM


WORKSPACE_TRAINER_SCHEMA = "arithmetic-workspace-trainer-v4"
RESUME_SCHEMA = "arithmetic-workspace-resume-v4"
RESEARCH_CHECKPOINT_SCHEMA = "arithmetic-workspace-model-v4"
SUPPORTED_ARMS = frozenset({"correct", "no_carry", "pseudo_fst", "deranged"})
_INTEGER_ANSWER = re.compile(r"^-?[0-9]+$")


@dataclass(frozen=True)
class WorkspaceTrainSettings:
    max_steps: int
    micro_batch_size: int
    gradient_accumulation: int
    learning_rate: float
    minimum_learning_rate: float
    warmup_steps: int
    stable_steps: int
    decay_steps: int
    weight_decay: float
    beta1: float
    beta2: float
    adam_eps: float
    gradient_clip: float
    precision: str
    deterministic: bool
    progress_every_steps: int
    light_eval_every_steps: int
    full_eval_every_steps: int
    resume_every_steps: int
    light_eval_items: int
    full_eval_items: int
    eval_batch_size: int
    generation_max_new_tokens: int
    evaluation_splits: tuple[str, ...]
    evaluation_panels: tuple[dict[str, Any], ...]
    research_checkpoints: tuple[int, ...]
    curriculum: tuple[dict[str, Any], ...]

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "WorkspaceTrainSettings":
        training = _mapping(config.get("training", config), "training")
        evaluation = _mapping(config.get("evaluation", {}), "evaluation")

        max_steps = _positive_int(training, "max_steps")
        micro_batch_size = _positive_int_alias(
            training, ("microbatch_size", "micro_batch_size"), "microbatch_size"
        )
        gradient_accumulation = _positive_int_alias(
            training,
            ("gradient_accumulation_steps", "gradient_accumulation"),
            "gradient_accumulation_steps",
        )
        learning_rate = _positive_float(training, "learning_rate")
        minimum_learning_rate = _nonnegative_float_alias(
            training, ("min_learning_rate", "minimum_learning_rate"), default=0.0
        )
        if minimum_learning_rate > learning_rate:
            raise ValueError("min_learning_rate must not exceed learning_rate")
        warmup_steps = _nonnegative_int(training, "warmup_steps", default=0)
        if warmup_steps > max_steps:
            raise ValueError("warmup_steps exceeds max_steps")

        decay_value = training.get("decay_steps")
        stable_value = training.get("stable_steps")
        if decay_value is None and stable_value is None:
            decay_steps = max(1, int(round(max_steps * 0.10)))
            stable_steps = max_steps - warmup_steps - decay_steps
        elif decay_value is None:
            stable_steps = _as_nonnegative_int(stable_value, "stable_steps")
            decay_steps = max_steps - warmup_steps - stable_steps
        elif stable_value is None:
            decay_steps = _as_nonnegative_int(decay_value, "decay_steps")
            stable_steps = max_steps - warmup_steps - decay_steps
        else:
            stable_steps = _as_nonnegative_int(stable_value, "stable_steps")
            decay_steps = _as_nonnegative_int(decay_value, "decay_steps")
            if warmup_steps + stable_steps + decay_steps != max_steps:
                raise ValueError(
                    "warmup_steps + stable_steps + decay_steps must equal max_steps"
                )
        if stable_steps < 0 or decay_steps < 0:
            raise ValueError("warmup/stable/decay schedule exceeds max_steps")

        optimizer_name = str(training.get("optimizer", "adamw")).lower()
        if optimizer_name != "adamw":
            raise ValueError("workspace training currently requires optimizer='adamw'")
        precision = str(training.get("precision", "auto")).lower().replace("-", "_")
        if precision not in {
            "auto",
            "bf16",
            "fp16",
            "fp32",
            "float32",
            "bf16_if_supported",
        }:
            raise ValueError(f"unsupported training precision: {precision}")

        checkpoints_raw = training.get("research_checkpoints", [0, max_steps])
        if not isinstance(checkpoints_raw, (list, tuple)) or any(
            type(value) is not int for value in checkpoints_raw
        ):
            raise ValueError("research_checkpoints must be a list of integer steps")
        checkpoints = tuple(sorted(set([0, max_steps, *checkpoints_raw])))
        if checkpoints[0] < 0 or checkpoints[-1] > max_steps:
            raise ValueError("research checkpoint step outside training range")

        curriculum_raw = training.get("curriculum", [])
        if not isinstance(curriculum_raw, (list, tuple)):
            raise ValueError("training.curriculum must be a list")
        curriculum = _normalize_curriculum(curriculum_raw, max_steps)

        splits_raw = evaluation.get("splits", ["validation", "test_iid"])
        if not isinstance(splits_raw, (list, tuple)) or not splits_raw or any(
            not isinstance(value, str) or not value for value in splits_raw
        ):
            raise ValueError("evaluation.splits must be a nonempty list of names")
        evaluation_splits = tuple(dict.fromkeys(splits_raw))
        panels_raw = evaluation.get("panels", [])
        if not isinstance(panels_raw, (list, tuple)):
            raise ValueError("evaluation.panels must be a list")
        panels: list[dict[str, Any]] = []
        for index, raw_panel in enumerate(panels_raw):
            panel = dict(_mapping(raw_panel, f"evaluation.panels[{index}]"))
            name = panel.get("name")
            split = panel.get("split", name)
            count = panel.get("count")
            if not isinstance(name, str) or not name:
                raise ValueError("each evaluation panel requires a nonempty name")
            if not isinstance(split, str) or not split:
                raise ValueError("each evaluation panel requires a nonempty split")
            if type(count) is not int or count <= 0:
                raise ValueError("each evaluation panel requires a positive count")
            panel["name"] = name
            panel["split"] = split
            panel["count"] = count
            panels.append(panel)

        if panels:
            panel_splits = tuple(
                dict.fromkeys(str(panel["split"]) for panel in panels)
            )
            panel_total = sum(int(panel["count"]) for panel in panels)
            if "splits" in evaluation and evaluation_splits != panel_splits:
                raise ValueError(
                    "evaluation.splits must equal the ordered unique panel split names"
                )
            declared_full_items = _positive_int(
                evaluation, "full_items", default=panel_total
            )
            if declared_full_items != panel_total:
                raise ValueError(
                    "evaluation.full_items must equal the sum of panel counts"
                )
            evaluation_splits = panel_splits
            full_eval_items = panel_total
        else:
            full_eval_items = _positive_int(
                evaluation, "full_items", default=2048
            )

        result = cls(
            max_steps=max_steps,
            micro_batch_size=micro_batch_size,
            gradient_accumulation=gradient_accumulation,
            learning_rate=learning_rate,
            minimum_learning_rate=minimum_learning_rate,
            warmup_steps=warmup_steps,
            stable_steps=stable_steps,
            decay_steps=decay_steps,
            weight_decay=_nonnegative_float(training, "weight_decay", default=0.1),
            beta1=_probability(training, "beta1", default=0.9, upper_open=True),
            beta2=_probability(training, "beta2", default=0.95, upper_open=True),
            adam_eps=_positive_float(training, "adam_eps", default=1e-8),
            gradient_clip=_positive_float(training, "gradient_clip", default=1.0),
            precision=precision,
            deterministic=_boolean(training, "deterministic", default=True),
            progress_every_steps=_positive_int(
                training, "progress_every_steps", default=100
            ),
            light_eval_every_steps=_positive_int_alias(
                training,
                ("light_eval_every_steps", "generation_every_steps"),
                "light_eval_every_steps",
                default=500,
            ),
            full_eval_every_steps=_positive_int(
                training, "full_eval_every_steps", default=2000
            ),
            resume_every_steps=_positive_int(
                training, "resume_every_steps", default=500
            ),
            light_eval_items=_positive_int(
                evaluation, "light_items", default=256
            ),
            full_eval_items=full_eval_items,
            eval_batch_size=_positive_int_alias(
                evaluation,
                ("batch_size", "full_batch_size"),
                "evaluation batch size",
                default=min(128, micro_batch_size),
            ),
            generation_max_new_tokens=_positive_int(
                evaluation, "generation_max_new_tokens", default=32
            ),
            evaluation_splits=evaluation_splits,
            evaluation_panels=tuple(panels),
            research_checkpoints=checkpoints,
            curriculum=curriculum,
        )
        if result.full_eval_every_steps % result.light_eval_every_steps:
            raise ValueError("full_eval_every_steps must be a multiple of light_eval_every_steps")
        return result

    def to_dict(self) -> dict[str, Any]:
        value = dataclasses.asdict(self)
        value["evaluation_splits"] = list(self.evaluation_splits)
        value["evaluation_panels"] = [dict(panel) for panel in self.evaluation_panels]
        value["research_checkpoints"] = list(self.research_checkpoints)
        value["curriculum"] = [dict(stage) for stage in self.curriculum]
        return value


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _as_nonnegative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")
    return value


def _positive_int(mapping: Mapping[str, Any], key: str, default: Any = None) -> int:
    value = mapping.get(key, default)
    if type(value) is not int or value <= 0:
        raise ValueError(f"{key} must be a positive integer")
    return value


def _nonnegative_int(
    mapping: Mapping[str, Any], key: str, default: Any = None
) -> int:
    return _as_nonnegative_int(mapping.get(key, default), key)


def _positive_int_alias(
    mapping: Mapping[str, Any],
    aliases: Sequence[str],
    label: str,
    default: Any = None,
) -> int:
    found = [name for name in aliases if name in mapping]
    if len(found) > 1 and len({mapping[name] for name in found}) > 1:
        raise ValueError(f"conflicting aliases for {label}: {found}")
    value = mapping[found[0]] if found else default
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _finite_float(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _positive_float(
    mapping: Mapping[str, Any], key: str, default: Any = None
) -> float:
    value = _finite_float(mapping.get(key, default), key)
    if value <= 0:
        raise ValueError(f"{key} must be positive")
    return value


def _nonnegative_float(
    mapping: Mapping[str, Any], key: str, default: Any = None
) -> float:
    value = _finite_float(mapping.get(key, default), key)
    if value < 0:
        raise ValueError(f"{key} must be nonnegative")
    return value


def _nonnegative_float_alias(
    mapping: Mapping[str, Any], aliases: Sequence[str], default: Any
) -> float:
    found = [name for name in aliases if name in mapping]
    if len(found) > 1 and len({mapping[name] for name in found}) > 1:
        raise ValueError(f"conflicting aliases: {found}")
    value = mapping[found[0]] if found else default
    result = _finite_float(value, aliases[0])
    if result < 0:
        raise ValueError(f"{aliases[0]} must be nonnegative")
    return result


def _probability(
    mapping: Mapping[str, Any], key: str, default: float, upper_open: bool
) -> float:
    value = _finite_float(mapping.get(key, default), key)
    if value < 0 or (value >= 1 if upper_open else value > 1):
        bracket = "[0, 1)" if upper_open else "[0, 1]"
        raise ValueError(f"{key} must be in {bracket}")
    return value


def _boolean(mapping: Mapping[str, Any], key: str, default: bool) -> bool:
    value = mapping.get(key, default)
    if type(value) is not bool:
        raise ValueError(f"{key} must be boolean")
    return value


def _normalize_curriculum(
    raw_stages: Sequence[Any], max_steps: int
) -> tuple[dict[str, Any], ...]:
    if not raw_stages:
        return ({"name": "all", "min_step": 1, "max_step": max_steps},)
    normalized: list[dict[str, Any]] = []
    previous_end = 0
    for index, raw in enumerate(raw_stages):
        stage = dict(_mapping(raw, f"curriculum[{index}]"))
        name = stage.get("name", f"stage_{index + 1}")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("curriculum stage name must be nonempty")
        raw_start = stage.get("start_step")
        if raw_start is not None:
            if type(raw_start) is not int or raw_start != previous_end:
                raise ValueError(
                    "curriculum start_step values must form contiguous half-open boundaries"
                )
            start = raw_start + 1
        else:
            start = stage.get("min_step", previous_end + 1)
        end = stage.get("max_step", stage.get("end_step"))
        if type(start) is not int or type(end) is not int:
            raise ValueError("curriculum stages require integer min_step/max_step")
        if start != previous_end + 1 or end < start:
            raise ValueError("curriculum stages must be contiguous and increasing")
        stage["name"] = name
        stage["min_step"] = start
        stage["max_step"] = end
        stage.pop("end_step", None)
        normalized.append(stage)
        previous_end = end
    if previous_end != max_steps:
        raise ValueError("final curriculum stage must end at max_steps")
    return tuple(normalized)


def _model_config(config: Mapping[str, Any]) -> ModelConfig:
    raw = dict(_mapping(config.get("model", {}), "model"))
    gradient_checkpointing = raw.pop("gradient_checkpointing", False)
    if gradient_checkpointing:
        raise ValueError("TinyDecoderLM does not implement gradient checkpointing")
    d_model = raw.get("d_model", 512)
    d_ff = raw.pop("d_ff", None)
    ff_multiplier = raw.pop("ff_multiplier", None)
    if d_ff is not None:
        if type(d_ff) is not int or type(d_model) is not int or d_ff % d_model:
            raise ValueError("model.d_ff must be an integer multiple of d_model")
        derived = d_ff // d_model
        if ff_multiplier is not None and ff_multiplier != derived:
            raise ValueError("model.d_ff conflicts with ff_multiplier")
        ff_multiplier = derived
    raw["ff_multiplier"] = 4 if ff_multiplier is None else ff_multiplier
    raw.setdefault("vocab_size", ByteTokenizer().vocab_size)
    if raw["vocab_size"] != ByteTokenizer().vocab_size:
        raise ValueError(
            f"model.vocab_size must be {ByteTokenizer().vocab_size} for the fixed byte tokenizer"
        )
    raw.setdefault("d_model", 512)
    raw.setdefault("n_layers", 12)
    raw.setdefault("n_heads", 8)
    raw.setdefault("max_seq_len", 128)
    raw.setdefault("dropout", 0.0)
    raw.setdefault("rope_base", 10000.0)
    raw.setdefault("tie_embeddings", True)
    allowed = {
        "vocab_size",
        "d_model",
        "n_layers",
        "n_heads",
        "ff_multiplier",
        "max_seq_len",
        "dropout",
        "rope_base",
        "tie_embeddings",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unsupported model configuration keys: {sorted(unknown)}")
    return ModelConfig.from_dict(raw)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _state_dict_hash(state: Mapping[str, "torch.Tensor"]) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        if not isinstance(name, str) or not isinstance(tensor, torch.Tensor):
            raise ValueError("model state dictionary contains an invalid entry")
        value = tensor.detach().cpu().contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(tuple(value.shape)).encode("ascii"))
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(value.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def _model_state_hash(model: TinyDecoderLM) -> str:
    return _state_dict_hash(model.state_dict())


def _atomic_json(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _atomic_torch_save(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(value, temporary)
    # Windows may reject FlushFileBuffers/fsync on a descriptor opened
    # read-only.  Reopen the completed temporary checkpoint with write access,
    # flush it, and only then atomically replace the destination.
    with temporary.open("r+b") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _append_jsonl(value: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(_canonical_json(dict(value)) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _truncate_jsonl_after(path: Path, step: int) -> None:
    if not path.is_file():
        return
    kept: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if int(row.get("step", -1)) <= step:
                kept.append(row)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in kept:
            handle.write(_canonical_json(row) + "\n")
    os.replace(temporary, path)


def _field(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, Mapping):
        return item.get(name, default)
    return getattr(item, name, default)


def _metadata_mapping(item: Any) -> dict[str, Any]:
    metadata = _field(item, "metadata", {})
    if metadata is None:
        return {}
    if isinstance(metadata, Mapping):
        return dict(metadata)
    if hasattr(metadata, "to_dict"):
        return dict(metadata.to_dict())
    if dataclasses.is_dataclass(metadata):
        return dataclasses.asdict(metadata)
    return {
        name: getattr(metadata, name)
        for name in dir(metadata)
        if not name.startswith("_")
        and isinstance(getattr(metadata, name), (str, int, float, bool))
    }


def _item_identity(item: Any) -> dict[str, Any]:
    return {
        "pair_id": str(_field(item, "pair_id", "")),
        "prompt": str(_field(item, "prompt", "")),
        "completion": str(_field(item, "completion", "")),
        "answer": str(_field(item, "answer", "")),
        "operation": str(_field(item, "operation", "")),
        "metadata": _metadata_mapping(item),
    }


def _provider_config_snapshot(provider: Any) -> Any:
    value = getattr(provider, "config", None)
    if value is None:
        return None
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    return repr(value)


def _collate_examples(
    examples: Sequence[Any],
    tokenizer: ByteTokenizer,
    device: "torch.device",
    maximum_length: int,
) -> tuple["torch.Tensor", "torch.Tensor", int, int]:
    if not examples:
        raise ValueError("training batch is empty")
    encoded: list[tuple[list[int], list[int], int]] = []
    for item in examples:
        prompt = _field(item, "prompt")
        completion = _field(item, "completion")
        if not isinstance(prompt, str) or not isinstance(completion, str) or not completion:
            raise ValueError("each online example requires nonempty prompt/completion strings")
        row = tokenizer.sequence(prompt, completion)
        if len(row[0]) > maximum_length:
            raise ValueError(
                f"example {_field(item, 'pair_id', '?')} needs {len(row[0])} tokens, "
                f"exceeding model max_seq_len={maximum_length}"
            )
        encoded.append(row)
    width = max(len(row[0]) for row in encoded)
    inputs = torch.full((len(encoded), width), tokenizer.pad_id, dtype=torch.long)
    labels = torch.full((len(encoded), width), -100, dtype=torch.long)
    input_tokens = 0
    target_tokens = 0
    for index, (tokens, targets, _) in enumerate(encoded):
        inputs[index, : len(tokens)] = torch.tensor(tokens, dtype=torch.long)
        labels[index, : len(targets)] = torch.tensor(targets, dtype=torch.long)
        input_tokens += len(tokens)
        target_tokens += sum(token != -100 for token in targets)
    if device.type != "cpu":
        inputs = inputs.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
    return inputs, labels, input_tokens, target_tokens


def _structure_labels(item: Any) -> list[str]:
    metadata = _metadata_mapping(item)
    operation = str(_field(item, "operation", "unknown"))
    left_digits = int(metadata.get("left_digits", 0) or 0)
    right_digits = int(metadata.get("right_digits", 0) or 0)
    carry_count = int(metadata.get("carry_count", 0) or 0)
    borrow_count = int(metadata.get("borrow_count", 0) or 0)
    event_count = int(metadata.get("event_count", carry_count + borrow_count) or 0)
    longest_chain = int(metadata.get("longest_chain", 0) or 0)
    labels = [f"operation:{operation}"]
    if left_digits or right_digits:
        labels.append(f"digits:{max(left_digits, right_digits)}")
    if event_count == 0:
        labels.append("no_event")
    else:
        labels.append("event")
        labels.append("single_event" if event_count == 1 else "multi_event")
    if carry_count:
        labels.append("carry")
        labels.append("single_carry" if carry_count == 1 else "multi_carry")
    if borrow_count:
        labels.append("borrow")
        labels.append("single_borrow" if borrow_count == 1 else "multi_borrow")
    if longest_chain:
        labels.append("chain_1" if longest_chain == 1 else "chain_2plus")
        if longest_chain >= 4:
            labels.append("chain_4plus")
    if int(metadata.get("result_width_change", 0) or 0):
        labels.append("width_change")
    if bool(metadata.get("has_zero", False)):
        labels.append("has_zero")
    if bool(metadata.get("has_nine", False)):
        labels.append("has_nine")
    requested = metadata.get("requested_structure")
    observed = metadata.get("observed_structure")
    if requested:
        labels.append(f"requested:{requested}")
    if observed:
        labels.append(f"observed:{observed}")
    return list(dict.fromkeys(labels))


def _new_group() -> dict[str, int]:
    return {"examples": 0, "answer_exact": 0, "raw_exact": 0, "well_formed": 0}


def _record_group(
    groups: dict[str, dict[str, int]],
    key: str,
    *,
    answer_exact: bool,
    raw_exact: bool,
    well_formed: bool,
) -> None:
    group = groups.setdefault(key, _new_group())
    group["examples"] += 1
    group["answer_exact"] += int(answer_exact)
    group["raw_exact"] += int(raw_exact)
    group["well_formed"] += int(well_formed)


def _finish_groups(
    groups: Mapping[str, Mapping[str, int]]
) -> dict[str, dict[str, float | int]]:
    result: dict[str, dict[str, float | int]] = {}
    for key, counts in sorted(groups.items()):
        total = max(1, int(counts["examples"]))
        result[key] = {
            "examples": int(counts["examples"]),
            "answer_exact_count": int(counts["answer_exact"]),
            "answer_exact_match": counts["answer_exact"] / total,
            "raw_exact_match": counts["raw_exact"] / total,
            "well_formed_rate": counts["well_formed"] / total,
            "malformed_rate": 1.0 - counts["well_formed"] / total,
        }
    return result


@torch.no_grad()
def evaluate_free_generation(
    *,
    model: TinyDecoderLM,
    examples: Sequence[Any],
    tokenizer: ByteTokenizer | None = None,
    device: "torch.device | str" = "cpu",
    max_new_tokens: int = 32,
    batch_size: int = 64,
    retain_items: bool = False,
) -> dict[str, Any]:
    """Greedily evaluate answers; empty/EOS-only output is always malformed."""

    if batch_size <= 0 or max_new_tokens <= 0:
        raise ValueError("evaluation batch size and generation budget must be positive")
    tokenizer = tokenizer or ByteTokenizer()
    resolved_device = resolve_device(device)
    rows = list(examples)
    if not rows:
        raise ValueError("free-generation evaluation requires at least one example")
    model.eval()
    prefixes: list[list[int]] = []
    budgets: list[int] = []
    for item in rows:
        prompt = str(_field(item, "prompt", ""))
        completion = str(_field(item, "completion", ""))
        prefix = tokenizer.prefix(prompt)
        required = len(tokenizer.encode(completion)) + 1
        available = model.config.max_seq_len - len(prefix) + 1
        if required > available:
            raise ValueError(
                f"evaluation target {_field(item, 'pair_id', '?')} exceeds model context"
            )
        prefixes.append(prefix)
        budgets.append(min(max(max_new_tokens, required), available))

    generated: dict[int, list[int]] = {}
    by_prefix_length: dict[int, list[int]] = {}
    for index, prefix in enumerate(prefixes):
        by_prefix_length.setdefault(len(prefix), []).append(index)
    for length in sorted(by_prefix_length):
        indices_at_length = by_prefix_length[length]
        for start in range(0, len(indices_at_length), batch_size):
            indices = indices_at_length[start : start + batch_size]
            outputs = model.generate_batch(
                [prefixes[index] for index in indices],
                tokenizer.eos_id,
                [budgets[index] for index in indices],
                resolved_device,
            )
            generated.update(zip(indices, outputs))

    exact_count = 0
    arithmetic_oracle_exact_count = 0
    raw_count = 0
    well_formed_count = 0
    eos_count = 0
    operation_groups: dict[str, dict[str, int]] = {}
    digit_groups: dict[str, dict[str, int]] = {}
    structure_groups: dict[str, dict[str, int]] = {}
    items: list[dict[str, Any]] = []
    previews: list[dict[str, Any]] = []
    for index, item in enumerate(rows):
        output_ids = generated[index]
        has_eos = bool(output_ids and output_ids[-1] == tokenizer.eos_id)
        illegal_special = any(
            token > 255 and token != tokenizer.eos_id for token in output_ids
        )
        decoded = "" if illegal_special else tokenizer.completion(output_ids)
        stripped = decoded.strip()
        # Answer-only arithmetic output must contain a signed decimal integer.
        well_formed = bool(
            has_eos and not illegal_special and stripped and _INTEGER_ANSWER.fullmatch(stripped)
        )
        expected_completion = str(_field(item, "completion", ""))
        # The trained target is completion.  For pseudo-FST and deranged arms,
        # item.answer intentionally remains the ordinary-arithmetic oracle and
        # must not be used to judge whether that control learned its own task.
        expected_answer = expected_completion.strip()
        arithmetic_oracle_answer = str(
            _field(item, "answer", expected_completion)
        ).strip()
        raw_expected = [*tokenizer.encode(expected_completion), tokenizer.eos_id]
        raw_exact = output_ids == raw_expected
        answer_exact = bool(well_formed and stripped == expected_answer)
        arithmetic_oracle_exact = bool(
            well_formed and stripped == arithmetic_oracle_answer
        )
        eos_count += int(has_eos)
        well_formed_count += int(well_formed)
        exact_count += int(answer_exact)
        arithmetic_oracle_exact_count += int(arithmetic_oracle_exact)
        raw_count += int(raw_exact)
        operation = str(_field(item, "operation", "unknown"))
        metadata = _metadata_mapping(item)
        digit_key = str(
            max(
                int(metadata.get("left_digits", 0) or 0),
                int(metadata.get("right_digits", 0) or 0),
            )
            or _field(item, "difficulty", "unknown")
        )
        _record_group(
            operation_groups,
            operation,
            answer_exact=answer_exact,
            raw_exact=raw_exact,
            well_formed=well_formed,
        )
        _record_group(
            digit_groups,
            digit_key,
            answer_exact=answer_exact,
            raw_exact=raw_exact,
            well_formed=well_formed,
        )
        for label in _structure_labels(item):
            _record_group(
                structure_groups,
                label,
                answer_exact=answer_exact,
                raw_exact=raw_exact,
                well_formed=well_formed,
            )
        item_row = {
            "pair_id": str(_field(item, "pair_id", index)),
            "family_id": str(_field(item, "family_id", _field(item, "pair_id", index))),
            "family_partition": _field(item, "family_partition"),
            "control_arm": str(_field(item, "control_arm", "")),
            "operation": operation,
            "expected_answer": expected_answer,
            "arithmetic_oracle_answer": arithmetic_oracle_answer,
            "generated_answer": stripped,
            "generated_completion": decoded,
            "answer_exact_match": answer_exact,
            "arithmetic_oracle_exact_match": arithmetic_oracle_exact,
            "raw_exact_match": raw_exact,
            "well_formed": well_formed,
            "has_eos": has_eos,
            "illegal_special": illegal_special,
            "metadata": metadata,
        }
        if retain_items:
            items.append(item_row)
        if len(previews) < 8:
            previews.append(item_row)

    total = len(rows)
    return {
        "examples": total,
        "answer_exact_count": exact_count,
        "answer_exact_match": exact_count / total,
        "arithmetic_oracle_exact_count": arithmetic_oracle_exact_count,
        "arithmetic_oracle_exact_match": arithmetic_oracle_exact_count / total,
        "raw_exact_count": raw_count,
        "raw_exact_match": raw_count / total,
        "well_formed_count": well_formed_count,
        "well_formed_rate": well_formed_count / total,
        "malformed_rate": 1.0 - well_formed_count / total,
        "eos_rate": eos_count / total,
        "by_operation": _finish_groups(operation_groups),
        "by_digits": _finish_groups(digit_groups),
        "by_structure": _finish_groups(structure_groups),
        "previews": previews,
        "items": items,
    }


@torch.no_grad()
def _evaluate_teacher_forced_loss(
    model: TinyDecoderLM,
    examples: Sequence[Any],
    tokenizer: ByteTokenizer,
    device: "torch.device",
    batch_size: int,
) -> dict[str, float | int]:
    model.eval()
    total_loss = 0.0
    total_targets = 0
    correct_targets = 0
    rows = list(examples)
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        inputs, labels, _, targets = _collate_examples(
            batch, tokenizer, device, model.config.max_seq_len
        )
        logits = model(inputs)
        total_loss += float(
            F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]),
                labels.reshape(-1),
                ignore_index=-100,
                reduction="sum",
            ).item()
        )
        mask = labels != -100
        correct_targets += int(((logits.argmax(-1) == labels) & mask).sum().item())
        total_targets += targets
    return {
        "loss": total_loss / max(1, total_targets),
        "token_accuracy": correct_targets / max(1, total_targets),
        "target_tokens": total_targets,
    }


def _extract_split_metrics(evaluations: Mapping[str, Any]) -> Mapping[str, Any]:
    if "splits" in evaluations and isinstance(evaluations["splits"], Mapping):
        return evaluations["splits"]
    if "generation" in evaluations and isinstance(evaluations["generation"], Mapping):
        generation = evaluations["generation"]
        if "splits" in generation and isinstance(generation["splits"], Mapping):
            return generation["splits"]
    metric_keys = {"answer_exact_match", "malformed_rate", "by_structure"}
    return {
        key: value
        for key, value in evaluations.items()
        if isinstance(value, Mapping) and metric_keys.intersection(value)
    }


def competence_report(
    evaluations: Mapping[str, Any],
    gates: Mapping[str, Any],
    gate_name: str = "probe_requires",
) -> dict[str, Any]:
    """Evaluate a competence gate without converting missing evidence into failure."""

    if not isinstance(evaluations, Mapping) or not isinstance(gates, Mapping):
        raise ValueError("evaluations and gates must be mappings")
    thresholds_raw = gates.get(gate_name)
    if thresholds_raw is None and any(isinstance(value, Mapping) for value in gates.values()):
        thresholds_raw = gates.get("probe_requires", gates.get("primary", gates))
    if thresholds_raw is None:
        thresholds_raw = gates
    thresholds = dict(_mapping(thresholds_raw, gate_name))
    split_metrics = _extract_split_metrics(evaluations)
    iid_name = next(
        (name for name in ("test_iid", "iid", "validation") if name in split_metrics),
        next(
            (name for name in split_metrics if "iid" in str(name).lower()),
            next(iter(split_metrics), None),
        ),
    )
    iid = split_metrics.get(iid_name, {}) if iid_name is not None else {}
    ood_values = [
        float(metrics["answer_exact_match"])
        for name, metrics in split_metrics.items()
        if "ood" in str(name).lower()
        and isinstance(metrics, Mapping)
        and isinstance(metrics.get("answer_exact_match"), (int, float))
    ]
    structure = iid.get("by_structure", {}) if isinstance(iid, Mapping) else {}

    def structural_rate(name: str) -> float | None:
        group = structure.get(name, {}) if isinstance(structure, Mapping) else {}
        value = group.get("answer_exact_match") if isinstance(group, Mapping) else None
        if isinstance(value, (int, float)):
            return float(value)
        # Dedicated balanced carry/borrow panels are preferable when the IID
        # panel happens not to contain that stratum.
        for split_name, metrics in split_metrics.items():
            if name not in str(split_name).lower() or not isinstance(metrics, Mapping):
                continue
            direct = metrics.get("answer_exact_match")
            if isinstance(direct, (int, float)):
                return float(direct)
        return None

    malformed_values = [
        float(metrics["malformed_rate"])
        for metrics in split_metrics.values()
        if isinstance(metrics, Mapping)
        and isinstance(metrics.get("malformed_rate"), (int, float))
    ]
    observed: dict[str, float | None] = {
        "iid_exact": (
            float(iid["answer_exact_match"])
            if isinstance(iid, Mapping)
            and isinstance(iid.get("answer_exact_match"), (int, float))
            else None
        ),
        "ood_exact": min(ood_values) if ood_values else None,
        "carry_exact": structural_rate("carry"),
        "borrow_exact": structural_rate("borrow"),
        "malformed_max": max(malformed_values) if malformed_values else None,
        "control_margin": (
            float(evaluations["control_margin"])
            if isinstance(evaluations.get("control_margin"), (int, float))
            else None
        ),
    }
    checks: dict[str, bool | None] = {}
    missing: list[str] = []
    for key, raw_threshold in thresholds.items():
        if key not in observed:
            continue
        threshold = _finite_float(raw_threshold, f"gate {key}")
        value = observed[key]
        if value is None:
            checks[key] = None
            missing.append(key)
        elif key.endswith("_max") or key.startswith("malformed"):
            checks[key] = value <= threshold
        else:
            checks[key] = value >= threshold
    ready = bool(checks) and all(value is True for value in checks.values())
    status = "INCOMPLETE" if missing or not checks else ("PASS" if ready else "FAIL")
    return {
        "status": status,
        "gate_name": gate_name,
        "ready": ready,
        "observed": observed,
        "thresholds": thresholds,
        "checks": checks,
        "missing": missing,
        "iid_split": iid_name,
        "evaluated_splits": list(split_metrics),
    }


def learning_rate_at_step(
    config: Mapping[str, Any] | WorkspaceTrainSettings, step: int
) -> float:
    settings = (
        config
        if isinstance(config, WorkspaceTrainSettings)
        else WorkspaceTrainSettings.from_config(config)
    )
    if type(step) is not int or not 0 <= step <= settings.max_steps:
        raise ValueError("learning-rate step outside [0, max_steps]")
    if step == 0:
        return 0.0 if settings.warmup_steps else settings.learning_rate
    if settings.warmup_steps and step <= settings.warmup_steps:
        return settings.learning_rate * step / settings.warmup_steps
    decay_start = settings.warmup_steps + settings.stable_steps
    if step <= decay_start or settings.decay_steps == 0:
        return settings.learning_rate
    progress = min(1.0, (step - decay_start) / max(1, settings.decay_steps))
    cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
    return settings.minimum_learning_rate + (
        settings.learning_rate - settings.minimum_learning_rate
    ) * cosine


def resolve_device(device: "torch.device | str") -> "torch.device":
    if isinstance(device, torch.device):
        return device
    normalized = str(device).lower()
    if normalized == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if normalized == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but PyTorch reports it unavailable")
    if normalized not in {"cpu", "cuda"}:
        raise ValueError(f"unknown device: {device}")
    return torch.device(normalized)


def _configure_runtime(seed: int, deterministic: bool) -> None:
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = deterministic
    if hasattr(torch.backends, "cuda"):
        torch.backends.cuda.matmul.allow_tf32 = not deterministic
        if hasattr(torch.backends.cuda, "enable_flash_sdp"):
            torch.backends.cuda.enable_flash_sdp(not deterministic)
            torch.backends.cuda.enable_mem_efficient_sdp(not deterministic)
            torch.backends.cuda.enable_math_sdp(True)
        if hasattr(torch.backends.cuda, "enable_cudnn_sdp"):
            torch.backends.cuda.enable_cudnn_sdp(not deterministic)
    torch.use_deterministic_algorithms(deterministic)


def _precision(
    requested: str, device: "torch.device"
) -> tuple[str, bool, "torch.dtype", bool]:
    if device.type != "cuda" or requested in {"fp32", "float32"}:
        return "fp32", False, torch.float32, False
    bf16_supported = bool(
        hasattr(torch.cuda, "is_bf16_supported") and torch.cuda.is_bf16_supported()
    )
    if requested in {"auto", "bf16_if_supported", "bf16"} and bf16_supported:
        return "bf16", True, torch.bfloat16, False
    if requested == "bf16" and not bf16_supported:
        print("PRECISION_FALLBACK REQUESTED=bf16 ACTUAL=fp16", flush=True)
    return "fp16", True, torch.float16, True


def _optimizer(
    model: TinyDecoderLM, settings: WorkspaceTrainSettings
) -> "torch.optim.Optimizer":
    decay: list[torch.nn.Parameter] = []
    no_decay: list[torch.nn.Parameter] = []
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        # Biases, normalization scales, and token embeddings are not decayed.
        if parameter.ndim >= 2 and "token_embedding" not in name:
            decay.append(parameter)
        else:
            no_decay.append(parameter)
    return torch.optim.AdamW(
        [
            {"params": decay, "weight_decay": settings.weight_decay},
            {"params": no_decay, "weight_decay": 0.0},
        ],
        lr=settings.learning_rate,
        betas=(settings.beta1, settings.beta2),
        eps=settings.adam_eps,
    )


def _optimizer_to_device(
    optimizer: "torch.optim.Optimizer", device: "torch.device"
) -> None:
    for state in optimizer.state.values():
        for key, value in list(state.items()):
            if isinstance(value, torch.Tensor):
                state[key] = value.to(device)


def _stage_for_step(
    settings: WorkspaceTrainSettings, step: int
) -> tuple[int, dict[str, Any]]:
    for index, stage in enumerate(settings.curriculum):
        if int(stage["min_step"]) <= step <= int(stage["max_step"]):
            return index, dict(stage)
    raise RuntimeError(f"no curriculum stage covers step {step}")


def _make_provider(config: Mapping[str, Any], seed: int) -> Any:
    from .workspace_data import WorkspaceDataProvider

    return WorkspaceDataProvider(_mapping(config.get("data", {}), "data"), seed=seed)


def _data_stage(stage: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Translate study curriculum notation into the provider's stream notation."""

    if stage is None:
        return None
    result = dict(stage)
    digits = result.get("digits")
    if isinstance(digits, (list, tuple)) and len(digits) == 2:
        result.setdefault("min_digits", int(digits[0]))
        result.setdefault("max_digits", int(digits[1]))
    if "structure_cycle" not in result:
        carry = result.get("carry_chain", [0, 0])
        borrow = result.get("borrow_chain", [0, 0])
        ranges = [value for value in (carry, borrow) if isinstance(value, (list, tuple)) and len(value) == 2]
        lower = min((int(value[0]) for value in ranges), default=0)
        upper = max((int(value[1]) for value in ranges), default=0)
        if upper == 0:
            structures = ["no_event"]
        elif lower >= 1 and upper == 1:
            structures = ["event"]
        elif lower >= 1:
            structures = ["event", "chain"]
        elif upper == 1:
            structures = ["no_event", "event"]
        else:
            structures = ["no_event", "event", "chain", "balanced"]
        result["structure_cycle"] = structures
    return result


def _provider_batch(
    provider: Any,
    arm: str,
    split: str,
    start: int,
    size: int,
    stage: Mapping[str, Any] | None,
) -> list[Any]:
    rows = provider.batch(arm, split, start, size, _data_stage(stage))
    result = list(rows)
    if len(result) != size:
        raise RuntimeError(
            f"data provider returned {len(result)} examples for requested batch of {size}"
        )
    return result


def _provider_fixed_eval(
    provider: Any,
    arm: str,
    split: str,
    count: int,
    stage: Mapping[str, Any] | None,
) -> list[Any]:
    rows = list(provider.fixed_eval(arm, split, count, _data_stage(stage)))
    if len(rows) != count:
        raise RuntimeError(
            f"data provider returned {len(rows)} fixed-eval examples, expected {count}"
        )
    return rows


def _runtime_information(
    device: "torch.device", precision: str, deterministic: bool
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "python": platform.python_version(),
        "python_executable": os.path.realpath(os.sys.executable),
        "torch": str(torch.__version__),
        "torch_cuda": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "device": str(device),
        "precision": precision,
        "deterministic_algorithms": deterministic,
    }
    if device.type == "cuda":
        properties = torch.cuda.get_device_properties(device)
        result.update(
            {
                "gpu": properties.name,
                "gpu_vram_gb": round(properties.total_memory / 1073741824, 3),
                "compute_capability": [properties.major, properties.minor],
            }
        )
    return result


def _runtime_compatibility_fingerprint(
    device: "torch.device", precision: str, deterministic: bool
) -> dict[str, Any]:
    """Factors that must match for an exact optimizer/RNG continuation."""

    device_index = (
        int(device.index)
        if device.index is not None
        else (int(torch.cuda.current_device()) if device.type == "cuda" else None)
    )
    result: dict[str, Any] = {
        "schema_version": "workspace-runtime-compatibility-v1",
        "python": platform.python_version(),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "torch": str(torch.__version__),
        "torch_cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "device_type": device.type,
        "device_index": device_index,
        "precision": precision,
        "deterministic_algorithms": deterministic,
    }
    if device.type == "cuda":
        properties = torch.cuda.get_device_properties(device_index)
        result.update(
            {
                "gpu": properties.name,
                "gpu_compute_capability": [
                    int(properties.major),
                    int(properties.minor),
                ],
            }
        )
    return result


def _capture_rng() -> dict[str, Any]:
    result: dict[str, Any] = {
        "python": random.getstate(),
        "torch": torch.get_rng_state(),
    }
    if torch.cuda.is_available():
        result["cuda"] = torch.cuda.get_rng_state_all()
    try:
        import numpy as np

        result["numpy"] = np.random.get_state()
    except ImportError:
        pass
    return result


def _restore_rng(value: Mapping[str, Any]) -> None:
    random.setstate(value["python"])
    torch.set_rng_state(value["torch"])
    if torch.cuda.is_available() and "cuda" in value:
        torch.cuda.set_rng_state_all(value["cuda"])
    if "numpy" in value:
        try:
            import numpy as np

            np.random.set_state(value["numpy"])
        except ImportError:
            pass


def _make_resume_payload(
    *,
    model: TinyDecoderLM,
    optimizer: "torch.optim.Optimizer",
    scaler: Any,
    step: int,
    data_counter: int,
    examples_seen: int,
    input_tokens_seen: int,
    target_tokens_seen: int,
    overflow_count: int,
    last_training_loss: float | None,
    last_gradient_norm: float | None,
    elapsed_seconds_total: float,
    latest_eval: Mapping[str, Any] | None,
    latest_eval_step: int | None,
    fingerprint: str,
    data_fingerprint: str,
    initial_model_hash: str,
    resume_generation: int,
    runtime_compatibility: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": RESUME_SCHEMA,
        "fingerprint": fingerprint,
        "data_fingerprint": data_fingerprint,
        "runtime_compatibility": dict(runtime_compatibility),
        "model_config": model.config.to_dict(),
        "step": step,
        "successful_optimizer_steps": step,
        "data_counter": data_counter,
        "examples_seen": examples_seen,
        "input_tokens_seen": input_tokens_seen,
        "target_tokens_seen": target_tokens_seen,
        "overflow_count": overflow_count,
        "last_training_loss": last_training_loss,
        "last_gradient_norm": last_gradient_norm,
        "elapsed_seconds_total": elapsed_seconds_total,
        "latest_eval": dict(latest_eval) if latest_eval is not None else None,
        "latest_eval_step": latest_eval_step,
        "initial_model_hash": initial_model_hash,
        "model_hash": _model_state_hash(model),
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "scaler": scaler.state_dict(),
        "rng": _capture_rng(),
        "resume_generation": resume_generation,
    }


def _save_rotating_resume(payload: Mapping[str, Any], output: Path) -> None:
    generation = int(payload["resume_generation"])
    slot_name = "resume_a.pt" if generation % 2 == 0 else "resume_b.pt"
    slot = output / slot_name
    _atomic_torch_save(dict(payload), slot)
    pointer = {
        "schema_version": RESUME_SCHEMA,
        "slot": slot_name,
        "sha256": _sha256_file(slot),
        "step": int(payload["step"]),
        "resume_generation": generation,
        "fingerprint": payload["fingerprint"],
    }
    _atomic_json(pointer, output / "resume_pointer.json")


def _load_resume_candidate(
    path: Path,
    fingerprint: str,
    model_config: ModelConfig,
    runtime_compatibility: Mapping[str, Any],
) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = torch.load(path, map_location="cpu", weights_only=False)
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("schema_version") != RESUME_SCHEMA:
        return None
    if payload.get("fingerprint") != fingerprint:
        return None
    if _canonical_json(payload.get("model_config")) != _canonical_json(
        model_config.to_dict()
    ):
        return None
    if _canonical_json(payload.get("runtime_compatibility")) != _canonical_json(
        dict(runtime_compatibility)
    ):
        return None
    if int(payload.get("successful_optimizer_steps", -1)) != int(
        payload.get("step", -2)
    ):
        return None
    state = payload.get("model")
    expected_model_hash = payload.get("model_hash")
    if not isinstance(state, Mapping) or not isinstance(expected_model_hash, str):
        return None
    try:
        actual_model_hash = _state_dict_hash(state)
    except (TypeError, ValueError, RuntimeError):
        return None
    if actual_model_hash != expected_model_hash:
        return None
    return payload


def _load_latest_resume(
    output: Path,
    fingerprint: str,
    model_config: ModelConfig,
    runtime_compatibility: Mapping[str, Any],
) -> tuple[dict[str, Any], Path] | None:
    pointer_path = output / "resume_pointer.json"
    pointer: dict[str, Any] | None = None
    if pointer_path.is_file():
        try:
            pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pointer = None
    ordered = [output / "resume_a.pt", output / "resume_b.pt"]
    if pointer and pointer.get("slot") in {"resume_a.pt", "resume_b.pt"}:
        preferred = output / str(pointer["slot"])
        preferred_hash_matches = bool(
            preferred.is_file()
            and isinstance(pointer.get("sha256"), str)
            and pointer.get("sha256") == _sha256_file(preferred)
        )
        if preferred_hash_matches:
            ordered = [preferred, *(path for path in ordered if path != preferred)]
        else:
            # A named preferred slot with a mismatched external digest is not
            # a fallback candidate.  The other rotating slot may still recover
            # the run after its internal model hash and runtime checks pass.
            ordered = [path for path in ordered if path != preferred]
    candidates: list[tuple[dict[str, Any], Path]] = []
    for path in ordered:
        payload = _load_resume_candidate(
            path, fingerprint, model_config, runtime_compatibility
        )
        if payload is not None:
            candidates.append((payload, path))
    if not candidates:
        return None
    return max(candidates, key=lambda value: int(value[0]["step"]))


def _save_research_checkpoint(
    *,
    model: TinyDecoderLM,
    output: Path,
    step: int,
    arm: str,
    seed: int,
    fingerprint: str,
    data_fingerprint: str,
    data_counter: int,
    latest_eval: Mapping[str, Any] | None,
) -> Path:
    model_hash = _model_state_hash(model)
    payload = {
        "schema_version": RESEARCH_CHECKPOINT_SCHEMA,
        "kind": "model_only",
        "arm": arm,
        "seed": seed,
        "step": step,
        "successful_optimizer_steps": step,
        "fingerprint": fingerprint,
        "data_fingerprint": data_fingerprint,
        "data_counter": data_counter,
        "model_config": model.config.to_dict(),
        "model_hash": model_hash,
        "latest_eval": dict(latest_eval) if latest_eval is not None else None,
        "model": model.state_dict(),
    }
    path = output / "checkpoints" / f"model_step_{step:06d}.pt"
    _atomic_torch_save(payload, path)
    return path


def load_research_checkpoint(
    checkpoint: Path | str, device: "torch.device | str" = "cpu"
) -> tuple[TinyDecoderLM, dict[str, Any]]:
    path = Path(checkpoint).resolve()
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict) or payload.get("schema_version") != RESEARCH_CHECKPOINT_SCHEMA:
        raise ValueError(f"not a v0.4 research checkpoint: {path}")
    config = ModelConfig.from_dict(dict(payload["model_config"]))
    model = TinyDecoderLM(config)
    model.load_state_dict(payload["model"])
    if _model_state_hash(model) != payload.get("model_hash"):
        raise ValueError(f"model hash mismatch in research checkpoint: {path}")
    resolved_device = resolve_device(device)
    model.to(resolved_device).eval()
    return model, payload


def _run_evaluation(
    *,
    model: TinyDecoderLM,
    provider: Any,
    arm: str,
    tokenizer: ByteTokenizer,
    device: "torch.device",
    settings: WorkspaceTrainSettings,
    stage: Mapping[str, Any],
    full: bool,
) -> dict[str, Any]:
    split_results: dict[str, Any] = {}
    # no_carry is a training-distribution restriction, not an alternative
    # target rule.  Evaluate that trained model on ordinary arithmetic panels,
    # including transfer cases, or its central generalization control is lost.
    evaluation_arm = "correct" if arm == "no_carry" else arm
    if full and settings.evaluation_panels:
        requests = [
            (
                str(panel["name"]),
                str(panel["split"]),
                int(panel["count"]),
                dict(panel.get("stage", stage)),
            )
            for panel in settings.evaluation_panels
        ]
    elif full:
        # If no explicit panels exist, full_items is a total budget shared as
        # evenly as possible over the named split namespaces.
        base = settings.full_eval_items // len(settings.evaluation_splits)
        remainder = settings.full_eval_items % len(settings.evaluation_splits)
        requests = [
            (name, name, base + int(index < remainder), dict(stage))
            for index, name in enumerate(settings.evaluation_splits)
        ]
    else:
        requests = [("validation", "validation", settings.light_eval_items, dict(stage))]
    for panel_name, split, count, panel_stage in requests:
        examples = _provider_fixed_eval(
            provider, evaluation_arm, split, count, panel_stage
        )
        generation = evaluate_free_generation(
            model=model,
            examples=examples,
            tokenizer=tokenizer,
            device=device,
            max_new_tokens=settings.generation_max_new_tokens,
            batch_size=settings.eval_batch_size,
            retain_items=False,
        )
        teacher_forced = _evaluate_teacher_forced_loss(
            model,
            examples,
            tokenizer,
            device,
            settings.eval_batch_size,
        )
        generation["teacher_forced"] = teacher_forced
        generation["panel_split"] = split
        generation["panel_stage"] = _data_stage(panel_stage)
        split_results[panel_name] = generation
    return {
        "kind": "full" if full else "light",
        "evaluation_target_arm": evaluation_arm,
        "examples_total": sum(request[2] for request in requests),
        "splits": split_results,
    }


def _latest_validation(latest_eval: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not latest_eval:
        return {}
    splits = latest_eval.get("splits", {})
    if not isinstance(splits, Mapping):
        return {}
    for name in ("validation", "test_iid", "iid"):
        if name in splits and isinstance(splits[name], Mapping):
            return splits[name]
    first = next(iter(splits.values()), {})
    return first if isinstance(first, Mapping) else {}


def _format_rate(value: Any) -> str:
    return "NA" if not isinstance(value, (int, float)) else f"{float(value):.6f}"


def _control_audit(provider: Any, arm: str, stage: Mapping[str, Any]) -> Any:
    if not hasattr(provider, "audit_control"):
        return {"status": "NOT_AVAILABLE"}
    audit = provider.audit_control(arm, "train", 512, _data_stage(stage))
    if isinstance(audit, Mapping):
        if (
            audit.get("passed") is False
            or audit.get("valid") is False
            or str(audit.get("status", "")).upper() == "FAIL"
        ):
            raise RuntimeError(f"control audit failed for arm {arm}: {dict(audit)}")
        return dict(audit)
    return audit


def train_arm(
    *,
    config: Mapping[str, Any],
    arm: str,
    seed: int,
    output_dir: Path | str,
    device: "torch.device | str" = "auto",
    resume: bool = True,
    data_provider: Any | None = None,
) -> dict[str, Any]:
    """Train one arm with an online, counter-addressed, answer-only stream."""

    if arm not in SUPPORTED_ARMS:
        raise ValueError(f"unknown arm {arm!r}; expected one of {sorted(SUPPORTED_ARMS)}")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    settings = WorkspaceTrainSettings.from_config(config)
    model_config = _model_config(config)
    tokenizer = ByteTokenizer()
    resolved_device = resolve_device(device)
    _configure_runtime(seed, settings.deterministic)
    actual_precision, amp_enabled, autocast_dtype, use_scaler = _precision(
        settings.precision, resolved_device
    )
    runtime_compatibility = _runtime_compatibility_fingerprint(
        resolved_device, actual_precision, settings.deterministic
    )
    provider = data_provider or _make_provider(config, seed)
    data_config = dict(_mapping(config.get("data", {}), "data"))
    data_fingerprint = _hash_json(
        {
            "requested_data": data_config,
            "resolved_provider_config": _provider_config_snapshot(provider),
            "provider": f"{provider.__class__.__module__}.{provider.__class__.__qualname__}",
            "seed": seed,
        }
    )
    arm_definition = next(
        (
            dict(value)
            for value in config.get("arms", [])
            if isinstance(value, Mapping) and value.get("name") == arm
        ),
        {"name": arm},
    )
    fingerprint = _hash_json(
        {
            "schema": WORKSPACE_TRAINER_SCHEMA,
            "arm": arm,
            "seed": seed,
            "model": model_config.to_dict(),
            "training": settings.to_dict(),
            "arm_definition": arm_definition,
            "competence_gates": config.get("competence_gates", {}),
            "data_fingerprint": data_fingerprint,
            "tokenizer": tokenizer.version,
            "runtime_compatibility": runtime_compatibility,
        }
    )

    first_stage = dict(settings.curriculum[0])
    print(
        f"TRAIN_PREP ARM={arm} SEED={seed} STATUS=AUDITING_DATA_STREAM",
        flush=True,
    )
    probe_examples = _provider_batch(provider, arm, "train", 0, 64, first_stage)
    input_stream_probe_hash = _hash_json(
        [
            {
                "pair_id": str(_field(item, "pair_id", "")),
                "prompt": str(_field(item, "prompt", "")),
            }
            for item in probe_examples
        ]
    )
    label_stream_probe_hash = _hash_json(
        [str(_field(item, "completion", "")) for item in probe_examples]
    )
    control_audit = _control_audit(provider, arm, first_stage)
    _atomic_json(control_audit, output / "control_audit.json")

    # Data auditing must never perturb the paired model initialization, even
    # for a third-party provider that happens to use a global RNG internally.
    _configure_runtime(seed, settings.deterministic)
    model = TinyDecoderLM(model_config).to(resolved_device)
    trainable_parameters = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    initial_model_hash = _model_state_hash(model)
    optimizer = _optimizer(model, settings)
    scaler = torch.amp.GradScaler("cuda", enabled=use_scaler)
    runtime = _runtime_information(
        resolved_device, actual_precision, settings.deterministic
    )
    resolved = {
        "schema_version": WORKSPACE_TRAINER_SCHEMA,
        "arm": arm,
        "seed": seed,
        "fingerprint": fingerprint,
        "data_fingerprint": data_fingerprint,
        "input_stream_probe_hash": input_stream_probe_hash,
        "label_stream_probe_hash": label_stream_probe_hash,
        "model": model_config.to_dict(),
        "training": settings.to_dict(),
        "runtime": runtime,
        "runtime_compatibility": runtime_compatibility,
        "trainable_parameters": trainable_parameters,
    }
    _atomic_json(resolved, output / "resolved_training.json")
    _atomic_json(runtime, output / "runtime.json")

    step = 0
    data_counter = 0
    examples_seen = 0
    input_tokens_seen = 0
    target_tokens_seen = 0
    overflow_count = 0
    restored_last_loss: float | None = None
    restored_gradient_norm: float | None = None
    elapsed_before = 0.0
    latest_eval: dict[str, Any] | None = None
    latest_eval_step: int | None = None
    resume_generation = 0
    resume_result = _load_latest_resume(
        output, fingerprint, model_config, runtime_compatibility
    )
    if resume_result is not None:
        if not resume:
            raise ValueError(f"resume state exists but resume=False: {output}")
        payload, resume_path = resume_result
        model.load_state_dict(payload["model"])
        model.to(resolved_device)
        optimizer.load_state_dict(payload["optimizer"])
        _optimizer_to_device(optimizer, resolved_device)
        scaler.load_state_dict(payload["scaler"])
        _restore_rng(payload["rng"])
        step = int(payload["step"])
        data_counter = int(payload["data_counter"])
        examples_seen = int(payload["examples_seen"])
        input_tokens_seen = int(payload["input_tokens_seen"])
        target_tokens_seen = int(payload["target_tokens_seen"])
        overflow_count = int(payload["overflow_count"])
        restored_last_loss = payload.get("last_training_loss")
        restored_gradient_norm = payload.get("last_gradient_norm")
        elapsed_before = float(payload.get("elapsed_seconds_total", 0.0))
        latest_eval = payload.get("latest_eval")
        latest_eval_step = payload.get("latest_eval_step")
        initial_model_hash = str(payload["initial_model_hash"])
        resume_generation = int(payload.get("resume_generation", 0)) + 1
        print(
            f"TRAIN_RESUME ARM={arm} SEED={seed} STEP={step}/{settings.max_steps} "
            f"DATA_COUNTER={data_counter} SLOT={resume_path.name}",
            flush=True,
        )
    elif any((output / name).exists() for name in ("resume_a.pt", "resume_b.pt")):
        raise ValueError("resume files exist but none match this experiment fingerprint")

    progress_path = output / "progress.jsonl"
    metrics_path = output / "metrics.jsonl"
    if step:
        _truncate_jsonl_after(progress_path, step)
        _truncate_jsonl_after(metrics_path, step)

    if step == 0:
        initial_checkpoint = output / "checkpoints" / "model_step_000000.pt"
        if initial_checkpoint.is_file():
            existing_initial = torch.load(
                initial_checkpoint, map_location="cpu", weights_only=False
            )
            if (
                not isinstance(existing_initial, Mapping)
                or existing_initial.get("schema_version")
                != RESEARCH_CHECKPOINT_SCHEMA
                or existing_initial.get("fingerprint") != fingerprint
                or existing_initial.get("model_hash") != initial_model_hash
            ):
                raise RuntimeError(
                    f"stale initial research checkpoint conflicts with this run: "
                    f"{initial_checkpoint}"
                )
        else:
            _save_research_checkpoint(
                model=model,
                output=output,
                step=0,
                arm=arm,
                seed=seed,
                fingerprint=fingerprint,
                data_fingerprint=data_fingerprint,
                data_counter=0,
                latest_eval=None,
            )
        # No valid resume state means any JSONL tail came from an incomplete
        # pre-step preparation attempt.  The checkpoint validation above makes
        # sure we never clear logs belonging to a different experiment.
        _truncate_jsonl_after(progress_path, -1)
        _truncate_jsonl_after(metrics_path, -1)
        print(
            f"TRAIN_EVAL_START ARM={arm} SEED={seed} STEP=0 KIND=light "
            f"ITEMS={settings.light_eval_items}",
            flush=True,
        )
        latest_eval = _run_evaluation(
            model=model,
            provider=provider,
            arm=arm,
            tokenizer=tokenizer,
            device=resolved_device,
            settings=settings,
            stage=first_stage,
            full=False,
        )
        latest_eval_step = 0
        _append_jsonl(
            {"arm": arm, "seed": seed, "step": 0, "evaluation": latest_eval},
            metrics_path,
        )
        initial_resume = _make_resume_payload(
            model=model,
            optimizer=optimizer,
            scaler=scaler,
            step=0,
            data_counter=0,
            examples_seen=0,
            input_tokens_seen=0,
            target_tokens_seen=0,
            overflow_count=0,
            last_training_loss=None,
            last_gradient_norm=None,
            elapsed_seconds_total=0.0,
            latest_eval=latest_eval,
            latest_eval_step=0,
            fingerprint=fingerprint,
            data_fingerprint=data_fingerprint,
            initial_model_hash=initial_model_hash,
            resume_generation=resume_generation,
            runtime_compatibility=runtime_compatibility,
        )
        _save_rotating_resume(initial_resume, output)
        resume_generation += 1

    print(
        f"TRAIN_START ARM={arm} SEED={seed} STEP={step}/{settings.max_steps} "
        f"PARAMETERS={trainable_parameters} DEVICE={resolved_device} "
        f"PRECISION={actual_precision} PROGRESS_EVERY={settings.progress_every_steps}",
        flush=True,
    )

    summary_path = output / "training_summary.json"
    if step >= settings.max_steps and summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if summary.get("fingerprint") != fingerprint:
            raise RuntimeError("existing final summary has the wrong experiment fingerprint")
        print(
            f"TRAIN_ARM={arm} SEED={seed} STEP={step} STATUS=REUSED",
            flush=True,
        )
        return summary

    if resolved_device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(resolved_device)
    invocation_started = time.perf_counter()
    window_started = invocation_started
    window_loss_sum = 0.0
    window_targets = 0
    window_examples = 0
    window_input_tokens = 0
    window_steps = 0
    last_loss: float | None = restored_last_loss
    last_gradient_norm: float | None = restored_gradient_norm
    active_stage_index: int | None = None

    while step < settings.max_steps:
        logical_step = step + 1
        stage_index, stage = _stage_for_step(settings, logical_step)
        if active_stage_index != stage_index:
            active_stage_index = stage_index
            print(
                f"TRAIN_STAGE ARM={arm} SEED={seed} INDEX={stage_index + 1}/"
                f"{len(settings.curriculum)} NAME={stage['name']} "
                f"STEPS={stage['min_step']}-{stage['max_step']}",
                flush=True,
            )
        learning_rate = learning_rate_at_step(settings, logical_step)
        for group in optimizer.param_groups:
            group["lr"] = learning_rate

        examples_per_step = settings.micro_batch_size * settings.gradient_accumulation
        online_rows = _provider_batch(
            provider,
            arm,
            "train",
            data_counter,
            examples_per_step,
            stage,
        )
        microbatches = [
            online_rows[
                micro * settings.micro_batch_size : (micro + 1)
                * settings.micro_batch_size
            ]
            for micro in range(settings.gradient_accumulation)
        ]
        target_counts = [
            sum(
                len(tokenizer.encode(str(_field(item, "completion", "")))) + 1
                for item in microbatch
            )
            for microbatch in microbatches
        ]
        total_targets = sum(target_counts)
        if total_targets <= 0:
            raise RuntimeError("online batch contains no supervised answer tokens")
        step_input_tokens = 0
        step_loss_sum = 0.0
        step_succeeded = False
        for overflow_attempt in range(16):
            optimizer.zero_grad(set_to_none=True)
            step_loss_sum = 0.0
            step_input_tokens = 0
            for microbatch in microbatches:
                inputs, labels, input_count, _ = _collate_examples(
                    microbatch,
                    tokenizer,
                    resolved_device,
                    model.config.max_seq_len,
                )
                step_input_tokens += input_count
                with torch.amp.autocast(
                    device_type=resolved_device.type,
                    dtype=autocast_dtype,
                    enabled=amp_enabled,
                ):
                    logits = model(inputs)
                    loss_sum = F.cross_entropy(
                        logits.reshape(-1, logits.shape[-1]),
                        labels.reshape(-1),
                        ignore_index=-100,
                        reduction="sum",
                    )
                    normalized = loss_sum / total_targets
                if not bool(torch.isfinite(loss_sum).item()):
                    raise RuntimeError(
                        f"nonfinite training loss in arm {arm} at logical step {logical_step}"
                    )
                scaler.scale(normalized).backward()
                step_loss_sum += float(loss_sum.detach().item())
            scaler.unscale_(optimizer)
            gradient_norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(), settings.gradient_clip
            )
            finite_gradient = bool(torch.isfinite(gradient_norm).item())
            if finite_gradient:
                last_gradient_norm = float(gradient_norm.item())
                scaler.step(optimizer)
                scaler.update()
                step_succeeded = True
                break
            if not use_scaler:
                raise RuntimeError(
                    f"nonfinite gradient in arm {arm} at logical step {logical_step}"
                )
            prior_scale = float(scaler.get_scale())
            scaler.step(optimizer)
            scaler.update()
            overflow_count += 1
            print(
                f"TRAIN_OVERFLOW ARM={arm} SEED={seed} LOGICAL_STEP={logical_step} "
                f"RETRY={overflow_attempt + 1} SCALE={prior_scale:.1f}->"
                f"{float(scaler.get_scale()):.1f}",
                flush=True,
            )
        if not step_succeeded:
            raise RuntimeError(f"16 consecutive AMP overflows at logical step {logical_step}")

        # The counter and public step advance only after a real optimizer update.
        step = logical_step
        data_counter += examples_per_step
        examples_seen += examples_per_step
        input_tokens_seen += step_input_tokens
        target_tokens_seen += total_targets
        last_loss = step_loss_sum / total_targets
        window_loss_sum += step_loss_sum
        window_targets += total_targets
        window_examples += examples_per_step
        window_input_tokens += step_input_tokens
        window_steps += 1

        full_due = step % settings.full_eval_every_steps == 0 or step == settings.max_steps
        light_due = step % settings.light_eval_every_steps == 0
        if full_due or light_due:
            latest_eval = _run_evaluation(
                model=model,
                provider=provider,
                arm=arm,
                tokenizer=tokenizer,
                device=resolved_device,
                settings=settings,
                stage=stage,
                full=full_due,
            )
            latest_eval_step = step
            _append_jsonl(
                {
                    "arm": arm,
                    "seed": seed,
                    "step": step,
                    "evaluation": latest_eval,
                    "training_loss": last_loss,
                    "learning_rate": learning_rate,
                },
                metrics_path,
            )
            validation = _latest_validation(latest_eval)
            print(
                f"TRAIN_EVAL ARM={arm} SEED={seed} STEP={step}/{settings.max_steps} "
                f"KIND={latest_eval['kind']} EXACT="
                f"{_format_rate(validation.get('answer_exact_match'))} "
                f"MALFORMED={_format_rate(validation.get('malformed_rate'))}",
                flush=True,
            )

        progress_due = (
            step % settings.progress_every_steps == 0 or step == settings.max_steps
        )
        if progress_due:
            now = time.perf_counter()
            window_seconds = max(1e-9, now - window_started)
            elapsed_invocation = now - invocation_started
            elapsed_total = elapsed_before + elapsed_invocation
            # On resume, using global step would understate ETA; window rate is honest and stable.
            seconds_per_step = window_seconds / max(1, window_steps)
            eta_seconds = seconds_per_step * (settings.max_steps - step)
            rolling_loss = window_loss_sum / max(1, window_targets)
            validation = _latest_validation(latest_eval)
            operations = validation.get("by_operation", {}) if validation else {}
            add_rate = (
                operations.get("add", {}).get("answer_exact_match")
                if isinstance(operations, Mapping)
                else None
            )
            sub_rate = (
                operations.get("sub", {}).get("answer_exact_match")
                if isinstance(operations, Mapping)
                else None
            )
            eval_age = None if latest_eval_step is None else step - latest_eval_step
            peak_vram = (
                torch.cuda.max_memory_allocated(resolved_device) / 1073741824
                if resolved_device.type == "cuda"
                else 0.0
            )
            progress_row = {
                "schema_version": WORKSPACE_TRAINER_SCHEMA,
                "arm": arm,
                "seed": seed,
                "step": step,
                "max_steps": settings.max_steps,
                "stage": stage["name"],
                "current_loss": last_loss,
                "rolling_loss": rolling_loss,
                "learning_rate": learning_rate,
                "gradient_norm": last_gradient_norm,
                "overflow_count": overflow_count,
                "examples_per_second": window_examples / window_seconds,
                "tokens_per_second": window_input_tokens / window_seconds,
                "examples_seen": examples_seen,
                "input_tokens_seen": input_tokens_seen,
                "target_tokens_seen": target_tokens_seen,
                "data_counter": data_counter,
                "precision": actual_precision,
                "peak_vram_gb": peak_vram,
                "elapsed_seconds": elapsed_total,
                "eta_seconds": eta_seconds,
                "latest_eval_step": latest_eval_step,
                "latest_eval_age_steps": eval_age,
                "latest_exact": validation.get("answer_exact_match") if validation else None,
                "latest_add_exact": add_rate,
                "latest_sub_exact": sub_rate,
                "window_steps": window_steps,
            }
            _append_jsonl(progress_row, progress_path)
            print(
                f"TRAIN_PROGRESS ARM={arm} SEED={seed} STEP={step}/{settings.max_steps} "
                f"STAGE={stage['name']} LOSS={last_loss:.6f} "
                f"ROLLING_LOSS={rolling_loss:.6f} LR={learning_rate:.8g} "
                f"GRAD_NORM={last_gradient_norm:.6f} OVERFLOWS={overflow_count} "
                f"EXAMPLES_PER_SECOND={progress_row['examples_per_second']:.2f} "
                f"TOKENS_PER_SECOND={progress_row['tokens_per_second']:.2f} "
                f"TOKENS_TOTAL={input_tokens_seen} PRECISION={actual_precision} "
                f"VRAM_GB={peak_vram:.3f} "
                f"ELAPSED_SECONDS={elapsed_total:.0f} ETA_SECONDS={eta_seconds:.0f} "
                f"EVAL_EXACT={_format_rate(validation.get('answer_exact_match') if validation else None)} "
                f"EVAL_ADD={_format_rate(add_rate)} EVAL_SUB={_format_rate(sub_rate)} "
                f"EVAL_AGE_STEPS={eval_age if eval_age is not None else 'NA'}",
                flush=True,
            )
            window_started = time.perf_counter()
            window_loss_sum = 0.0
            window_targets = 0
            window_examples = 0
            window_input_tokens = 0
            window_steps = 0

        checkpoint_due = step in settings.research_checkpoints
        if checkpoint_due:
            _save_research_checkpoint(
                model=model,
                output=output,
                step=step,
                arm=arm,
                seed=seed,
                fingerprint=fingerprint,
                data_fingerprint=data_fingerprint,
                data_counter=data_counter,
                latest_eval=latest_eval,
            )
        resume_due = (
            checkpoint_due
            or step % settings.resume_every_steps == 0
            or step == settings.max_steps
        )
        if resume_due:
            elapsed_total = elapsed_before + (time.perf_counter() - invocation_started)
            resume_payload = _make_resume_payload(
                model=model,
                optimizer=optimizer,
                scaler=scaler,
                step=step,
                data_counter=data_counter,
                examples_seen=examples_seen,
                input_tokens_seen=input_tokens_seen,
                target_tokens_seen=target_tokens_seen,
                overflow_count=overflow_count,
                last_training_loss=last_loss,
                last_gradient_norm=last_gradient_norm,
                elapsed_seconds_total=elapsed_total,
                latest_eval=latest_eval,
                latest_eval_step=latest_eval_step,
                fingerprint=fingerprint,
                data_fingerprint=data_fingerprint,
                initial_model_hash=initial_model_hash,
                resume_generation=resume_generation,
                runtime_compatibility=runtime_compatibility,
            )
            _save_rotating_resume(resume_payload, output)
            resume_generation += 1

    elapsed_total = elapsed_before + (time.perf_counter() - invocation_started)
    final_hash = _model_state_hash(model)
    if final_hash == initial_model_hash:
        raise RuntimeError(f"model weights did not change in trained arm {arm}")
    final_checkpoint = output / "checkpoints" / f"model_step_{settings.max_steps:06d}.pt"
    if not final_checkpoint.is_file():
        final_checkpoint = _save_research_checkpoint(
            model=model,
            output=output,
            step=settings.max_steps,
            arm=arm,
            seed=seed,
            fingerprint=fingerprint,
            data_fingerprint=data_fingerprint,
            data_counter=data_counter,
            latest_eval=latest_eval,
        )
    latest_gate = competence_report(
        latest_eval or {},
        _mapping(config.get("competence_gates", {}), "competence_gates"),
        "probe_requires",
    )
    summary = {
        "status": "PASS",
        "schema_version": WORKSPACE_TRAINER_SCHEMA,
        "arm": arm,
        "seed": seed,
        "optimizer_steps": step,
        "successful_optimizer_steps": step,
        "data_counter": data_counter,
        "examples_seen": examples_seen,
        "input_tokens_seen": input_tokens_seen,
        "target_tokens_seen": target_tokens_seen,
        "overflow_count": overflow_count,
        "trainable_parameters": trainable_parameters,
        "precision": actual_precision,
        "runtime_compatibility": runtime_compatibility,
        "initial_model_hash": initial_model_hash,
        "final_model_hash": final_hash,
        "last_training_loss": last_loss,
        "last_gradient_norm": last_gradient_norm,
        "latest_evaluation_step": latest_eval_step,
        "latest_evaluation": latest_eval,
        "competence": latest_gate,
        "elapsed_seconds": elapsed_total,
        "peak_vram_gb": (
            torch.cuda.max_memory_allocated(resolved_device) / 1073741824
            if resolved_device.type == "cuda"
            else 0.0
        ),
        "fingerprint": fingerprint,
        "data_fingerprint": data_fingerprint,
        "input_stream_probe_hash": input_stream_probe_hash,
        "label_stream_probe_hash": label_stream_probe_hash,
        "final_checkpoint": str(final_checkpoint),
        "progress_every_steps": settings.progress_every_steps,
    }
    _atomic_json(summary, summary_path)
    print(
        f"TRAIN_ARM={arm} SEED={seed} STEP={step}/{settings.max_steps} "
        f"STATUS=PASS FINAL_CHECKPOINT={final_checkpoint}",
        flush=True,
    )
    return summary


__all__ = [
    "SUPPORTED_ARMS",
    "WorkspaceTrainSettings",
    "competence_report",
    "evaluate_free_generation",
    "learning_rate_at_step",
    "load_research_checkpoint",
    "resolve_device",
    "train_arm",
]
