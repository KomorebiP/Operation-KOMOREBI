from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import torch
    import torch.nn.functional as F
except ImportError as error:  # pragma: no cover - handled by preflight
    raise ImportError("PyTorch is required for training. Use the Python environment containing torch.") from error

from .byte_tokenizer import ByteTokenizer
from .core import seeded_rng, stable_hash
from .generate import canonical_json
from .tiny_model import ModelConfig, TinyDecoderLM
from .train_data import TrainingExample


CHECKPOINT_SCHEMA_VERSION = "3.0"
TRAINER_FINGERPRINT_VERSION = "3.0"


@dataclass(frozen=True)
class CurriculumStage:
    name: str
    end_step: int
    difficulties: tuple[int, ...]
    operations: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CurriculumStage":
        if not isinstance(value, dict):
            raise ValueError("each curriculum stage must be an object")
        unknown = set(value) - {"name", "end_step", "difficulties", "operations"}
        if unknown:
            raise ValueError(f"unknown curriculum stage keys: {sorted(unknown)}")
        name = value.get("name")
        end_step = value.get("end_step")
        difficulties = value.get("difficulties")
        operations = value.get("operations", [])
        if not isinstance(name, str) or not name.strip() or not name.replace("_", "").isalnum():
            raise ValueError("curriculum stage names must contain letters, numbers, or underscores")
        if type(end_step) is not int or end_step <= 0:
            raise ValueError("curriculum stage end_step must be a positive integer")
        if (
            not isinstance(difficulties, (list, tuple))
            or not difficulties
            or any(type(level) is not int or not 1 <= level <= 9 for level in difficulties)
        ):
            raise ValueError("curriculum difficulties must be integers from 1 through 9")
        if (
            not isinstance(operations, (list, tuple))
            or any(not isinstance(operation, str) or not operation for operation in operations)
        ):
            raise ValueError("curriculum operations must be strings")
        normalized_difficulties = tuple(sorted(set(difficulties)))
        normalized_operations = tuple(sorted(set(operations)))
        if tuple(difficulties) != normalized_difficulties:
            raise ValueError("curriculum difficulties must be unique and increasing")
        if tuple(operations) != normalized_operations:
            raise ValueError("curriculum operations must be unique and sorted")
        return cls(
            name=name,
            end_step=end_step,
            difficulties=normalized_difficulties,
            operations=normalized_operations,
        )

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["difficulties"] = list(self.difficulties)
        value["operations"] = list(self.operations)
        return value


@dataclass(frozen=True)
class TrainConfig:
    max_steps: int
    micro_batch_size: int
    gradient_accumulation: int
    learning_rate: float
    minimum_learning_rate: float
    warmup_steps: int
    weight_decay: float
    gradient_clip: float
    checkpoint_steps: tuple[int, ...]
    eval_samples: int
    eval_batch_size: int
    max_new_tokens: int
    amp: bool = True
    deterministic: bool = True
    progress_every_steps: int = 100
    validation_every_steps: int = 0
    generation_every_steps: int = 0
    resume_every_steps: int = 500
    heldout_loss_samples: int = 0
    heldout_generation_samples: int = 1000
    curriculum_stages: tuple[CurriculumStage, ...] = ()

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "TrainConfig":
        payload = dict(value)
        raw_curriculum = payload.pop("curriculum_stages", [])
        if not isinstance(raw_curriculum, (list, tuple)):
            raise ValueError("curriculum_stages must be a sequence")
        curriculum = tuple(CurriculumStage.from_dict(stage) for stage in raw_curriculum)
        raw_checkpoint_steps = payload["checkpoint_steps"]
        if not isinstance(raw_checkpoint_steps, (list, tuple)) or any(
            type(step) is not int for step in raw_checkpoint_steps
        ):
            raise ValueError("checkpoint_steps must be a sequence of integers")
        payload["checkpoint_steps"] = tuple(raw_checkpoint_steps)
        payload["curriculum_stages"] = curriculum
        config = cls(**payload)
        integer_fields = (
            "max_steps",
            "micro_batch_size",
            "gradient_accumulation",
            "warmup_steps",
            "eval_samples",
            "eval_batch_size",
            "max_new_tokens",
            "progress_every_steps",
            "validation_every_steps",
            "generation_every_steps",
            "resume_every_steps",
            "heldout_loss_samples",
            "heldout_generation_samples",
        )
        if any(type(getattr(config, name)) is not int for name in integer_fields):
            raise ValueError("training counts must be integers")
        if config.max_steps <= 0 or config.micro_batch_size <= 0:
            raise ValueError("training steps and micro batch size must be positive")
        if config.gradient_accumulation <= 0:
            raise ValueError("gradient_accumulation must be positive")
        numeric_fields = (
            "learning_rate",
            "minimum_learning_rate",
            "weight_decay",
            "gradient_clip",
        )
        if any(
            isinstance(getattr(config, name), bool)
            or not isinstance(getattr(config, name), (int, float))
            or not math.isfinite(float(getattr(config, name)))
            for name in numeric_fields
        ):
            raise ValueError("training rates and norms must be finite numbers")
        if not 0 < config.learning_rate or not 0 <= config.minimum_learning_rate <= config.learning_rate:
            raise ValueError("invalid learning-rate range")
        if not 0 <= config.warmup_steps <= config.max_steps:
            raise ValueError("warmup_steps must be between zero and max_steps")
        if config.weight_decay < 0:
            raise ValueError("weight_decay must be nonnegative")
        if config.gradient_clip <= 0:
            raise ValueError("gradient_clip must be positive")
        if config.eval_samples <= 0 or config.eval_batch_size <= 0:
            raise ValueError("evaluation sample and batch counts must be positive")
        if config.max_new_tokens <= 0:
            raise ValueError("max_new_tokens must be positive")
        if config.progress_every_steps <= 0 or config.resume_every_steps <= 0:
            raise ValueError("progress and resume intervals must be positive")
        if config.validation_every_steps < 0 or config.generation_every_steps < 0:
            raise ValueError("validation and generation intervals must be nonnegative")
        if (
            config.validation_every_steps
            and config.generation_every_steps
            and config.generation_every_steps % config.validation_every_steps
        ):
            raise ValueError("generation interval must be a multiple of validation interval")
        if config.heldout_loss_samples < 0 or config.heldout_generation_samples <= 0:
            raise ValueError("held-out sample counts must be nonnegative, with generation positive")
        if type(config.amp) is not bool or type(config.deterministic) is not bool:
            raise ValueError("amp and deterministic must be boolean")
        required = {0, config.max_steps}
        if not required.issubset(config.checkpoint_steps):
            raise ValueError("checkpoint_steps must include step zero and max_steps")
        if any(step < 0 or step > config.max_steps for step in config.checkpoint_steps):
            raise ValueError("checkpoint step outside training range")
        if tuple(sorted(set(config.checkpoint_steps))) != config.checkpoint_steps:
            raise ValueError("checkpoint_steps must be unique and increasing")
        if config.curriculum_stages:
            ends = tuple(stage.end_step for stage in config.curriculum_stages)
            if tuple(sorted(set(ends))) != ends:
                raise ValueError("curriculum stage end_step values must be unique and increasing")
            if ends[-1] != config.max_steps:
                raise ValueError("the final curriculum stage must end at max_steps")
            names = [stage.name for stage in config.curriculum_stages]
            if len(set(names)) != len(names):
                raise ValueError("curriculum stage names must be unique")
        return config

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["checkpoint_steps"] = list(self.checkpoint_steps)
        value["curriculum_stages"] = [stage.to_dict() for stage in self.curriculum_stages]
        return value


def configure_runtime(seed: int, deterministic: bool) -> None:
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = deterministic
    torch.backends.cuda.matmul.allow_tf32 = False
    if hasattr(torch.backends.cuda, "enable_flash_sdp"):
        torch.backends.cuda.enable_flash_sdp(not deterministic)
        torch.backends.cuda.enable_mem_efficient_sdp(not deterministic)
        torch.backends.cuda.enable_math_sdp(True)
    if hasattr(torch.backends.cuda, "enable_cudnn_sdp"):
        torch.backends.cuda.enable_cudnn_sdp(not deterministic)
    torch.use_deterministic_algorithms(deterministic)


def resolve_device(name: str) -> "torch.device":
    normalized = name.lower()
    if normalized == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but PyTorch reports CUDA unavailable")
        return torch.device("cuda")
    if normalized == "cpu":
        return torch.device("cpu")
    if normalized == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    raise ValueError(f"unknown device: {name}")


def runtime_information(device: "torch.device") -> dict[str, Any]:
    information: dict[str, Any] = {
        "python": platform.python_version(),
        "python_executable": os.path.realpath(os.sys.executable),
        "python_prefix": os.sys.prefix,
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "torch_cuda": torch.version.cuda,
        "device": str(device),
    }
    if device.type == "cuda":
        properties = torch.cuda.get_device_properties(device)
        information.update(
            {
                "gpu": properties.name,
                "gpu_vram_gb": round(properties.total_memory / 1073741824, 3),
            }
        )
    return information


def _runtime_fingerprint_factors(
    device: "torch.device", amp_enabled: bool, deterministic: bool
) -> dict[str, Any]:
    factors: dict[str, Any] = {
        "trainer_fingerprint_version": TRAINER_FINGERPRINT_VERSION,
        "python": platform.python_version(),
        "torch": str(torch.__version__),
        "torch_cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "device_type": device.type,
        "device_index": device.index,
        "amp_enabled": bool(amp_enabled),
        "deterministic": bool(deterministic),
    }
    if device.type == "cuda":
        properties = torch.cuda.get_device_properties(device)
        factors.update(
            {
                "gpu": properties.name,
                "gpu_capability": [int(properties.major), int(properties.minor)],
            }
        )
    return factors


def model_state_hash(model: TinyDecoderLM) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        value = tensor.detach().cpu().contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(tuple(value.shape)).encode("ascii"))
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(value.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def _atomic_torch_save(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(value, temporary)
    os.replace(temporary, path)


def _atomic_json(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def _append_jsonl(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if path.is_file():
        with path.open("r", encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
    if isinstance(value, dict) and "step" in value and "arm" in value:
        rows = [
            row
            for row in rows
            if not (
                isinstance(row, dict)
                and row.get("step") == value["step"]
                and row.get("arm") == value["arm"]
            )
        ]
    rows.append(value)
    rows.sort(key=lambda row: (str(row.get("arm", "")), int(row.get("step", 0))))
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


def required_input_length(item: TrainingExample, tokenizer: ByteTokenizer) -> int:
    return len(tokenizer.prefix(item.prompt)) + len(tokenizer.encode(item.completion))


def _generation_budget(
    item: TrainingExample,
    tokenizer: ByteTokenizer,
    model: TinyDecoderLM,
    configured_max_new_tokens: int,
) -> int:
    prefix_length = len(tokenizer.prefix(item.prompt))
    required = len(tokenizer.encode(item.completion)) + 1
    available = model.config.max_seq_len - prefix_length + 1
    if required > available:
        raise ValueError(
            f"generation target for {item.pair_id} requires {required} new tokens, "
            f"but only {available} fit in the model context"
        )
    return min(max(configured_max_new_tokens, required), available)


def validate_lengths(
    examples: list[TrainingExample], tokenizer: ByteTokenizer, maximum: int, label: str
) -> None:
    longest = max((required_input_length(item, tokenizer), item.pair_id) for item in examples)
    if longest[0] > maximum:
        raise ValueError(
            f"{label} requires sequence length {longest[0]} for {longest[1]}, "
            f"but model max_seq_len is {maximum}"
        )


def _collate(
    examples: list[TrainingExample],
    indices: list[int],
    tokenizer: ByteTokenizer,
    device: "torch.device",
) -> tuple["torch.Tensor", "torch.Tensor", "torch.Tensor", int]:
    encoded = [tokenizer.sequence(examples[index].prompt, examples[index].completion) for index in indices]
    length = max(len(item[0]) for item in encoded)
    input_ids = torch.full(
        (len(encoded), length), tokenizer.pad_id, dtype=torch.long
    )
    labels = torch.full((len(encoded), length), -100, dtype=torch.long)
    prompt_positions = torch.empty(len(encoded), dtype=torch.long)
    target_tokens = 0
    for row, (tokens, targets, prompt_position) in enumerate(encoded):
        input_ids[row, : len(tokens)] = torch.tensor(tokens, dtype=torch.long)
        labels[row, : len(targets)] = torch.tensor(targets, dtype=torch.long)
        prompt_positions[row] = prompt_position
        target_tokens += sum(value != -100 for value in targets)
    if device.type != "cpu":
        input_ids = input_ids.to(device)
        labels = labels.to(device)
        prompt_positions = prompt_positions.to(device)
    return input_ids, labels, prompt_positions, target_tokens


def _batch_indices(
    count: int,
    batch_size: int,
    seed: int,
    stream_key: str,
    step: int,
    micro: int,
) -> list[int]:
    rng = seeded_rng(seed, "training-stream-v1", stream_key, step, micro)
    return [rng.randrange(count) for _ in range(batch_size)]


def _batch_indices_from_pool(
    pool: list[int],
    batch_size: int,
    seed: int,
    stream_key: str,
    step: int,
    micro: int,
) -> list[int]:
    if not pool:
        raise ValueError("training index pool must not be empty")
    rng = seeded_rng(seed, "training-stream-v1", stream_key, step, micro)
    return [pool[rng.randrange(len(pool))] for _ in range(batch_size)]


def _curriculum_pools(
    examples: list[TrainingExample], config: TrainConfig
) -> list[tuple[CurriculumStage, list[int], str]]:
    stages = config.curriculum_stages or (
        CurriculumStage(
            name="all_data",
            end_step=config.max_steps,
            difficulties=tuple(),
            operations=tuple(),
        ),
    )
    pools: list[tuple[CurriculumStage, list[int], str]] = []
    for stage in stages:
        allowed_difficulties = set(stage.difficulties)
        allowed_operations = set(stage.operations)
        indices = [
            index
            for index, item in enumerate(examples)
            if (not allowed_difficulties or item.difficulty in allowed_difficulties)
            and (not allowed_operations or item.operation in allowed_operations)
        ]
        if not indices:
            raise ValueError(f"curriculum stage {stage.name} has no eligible examples")
        pair_fingerprint = stable_hash(
            canonical_json([examples[index].pair_id for index in indices])
        )
        pools.append((stage, indices, pair_fingerprint))
    return pools


def _curriculum_at_step(
    pools: list[tuple[CurriculumStage, list[int], str]], step: int
) -> tuple[int, CurriculumStage, list[int], str]:
    for index, (stage, pool, fingerprint) in enumerate(pools):
        if step <= stage.end_step:
            return index, stage, pool, fingerprint
    raise ValueError(f"no curriculum stage covers optimizer step {step}")


def _learning_rate(config: TrainConfig, step: int) -> float:
    if config.warmup_steps > 0 and step <= config.warmup_steps:
        return config.learning_rate * step / config.warmup_steps
    denominator = max(1, config.max_steps - config.warmup_steps)
    progress = min(1.0, max(0.0, (step - config.warmup_steps) / denominator))
    cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
    return config.minimum_learning_rate + (config.learning_rate - config.minimum_learning_rate) * cosine


def _optimizer(model: TinyDecoderLM, config: TrainConfig) -> "torch.optim.Optimizer":
    decay = []
    no_decay = []
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        if parameter.ndim >= 2 and "token_embedding" not in name:
            decay.append(parameter)
        else:
            no_decay.append(parameter)
    return torch.optim.AdamW(
        [
            {"params": decay, "weight_decay": config.weight_decay},
            {"params": no_decay, "weight_decay": 0.0},
        ],
        lr=config.learning_rate,
        betas=(0.9, 0.95),
        eps=1e-8,
    )


def _fixed_subset(examples: list[TrainingExample], count: int, key: str) -> list[TrainingExample]:
    return sorted(examples, key=lambda item: stable_hash(f"{key}|{item.pair_id}"))[:count]


@torch.no_grad()
def evaluate_loss(
    model: TinyDecoderLM,
    examples: list[TrainingExample],
    tokenizer: ByteTokenizer,
    device: "torch.device",
    batch_size: int,
) -> dict[str, float]:
    model.eval()
    loss_sum = 0.0
    token_count = 0
    correct_tokens = 0
    for start in range(0, len(examples), batch_size):
        indices = list(range(start, min(len(examples), start + batch_size)))
        input_ids, labels, _, targets = _collate(examples, indices, tokenizer, device)
        logits = model(input_ids)
        loss_sum += float(
            F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]),
                labels.reshape(-1),
                ignore_index=-100,
                reduction="sum",
            ).item()
        )
        mask = labels != -100
        correct_tokens += int(((logits.argmax(dim=-1) == labels) & mask).sum().item())
        token_count += targets
    return {
        "loss": loss_sum / max(1, token_count),
        "token_accuracy": correct_tokens / max(1, token_count),
        "target_tokens": token_count,
    }


@torch.no_grad()
def evaluate_generation(
    model: TinyDecoderLM,
    examples: list[TrainingExample],
    tokenizer: ByteTokenizer,
    device: "torch.device",
    max_new_tokens: int,
    batch_size: int = 1,
    retain_items: bool = False,
) -> dict[str, Any]:
    if batch_size <= 0:
        raise ValueError("generation batch_size must be positive")
    model.eval()
    exact = 0
    answer_exact = 0
    terminated = 0
    effective_budgets: list[int] = []
    previews: list[dict[str, str]] = []
    operation_counts: dict[str, dict[str, int]] = {}
    difficulty_counts: dict[str, dict[str, int]] = {}
    item_results: list[dict[str, Any]] = []

    def record_group(
        groups: dict[str, dict[str, int]],
        key: str,
        raw_match: bool,
        answer_match: bool,
        has_eos: bool,
    ) -> None:
        counts = groups.setdefault(
            key, {"examples": 0, "raw_exact": 0, "answer_exact": 0, "eos": 0}
        )
        counts["examples"] += 1
        counts["raw_exact"] += int(raw_match)
        counts["answer_exact"] += int(answer_match)
        counts["eos"] += int(has_eos)

    def finalize_groups(
        groups: dict[str, dict[str, int]],
    ) -> dict[str, dict[str, float | int]]:
        return {
            key: {
                "examples": counts["examples"],
                "raw_exact_match": counts["raw_exact"] / counts["examples"],
                "answer_exact_match": counts["answer_exact"] / counts["examples"],
                "eos_rate": counts["eos"] / counts["examples"],
            }
            for key, counts in sorted(groups.items())
        }

    prefixes = [tokenizer.prefix(item.prompt) for item in examples]
    budgets = [
        _generation_budget(item, tokenizer, model, max_new_tokens) for item in examples
    ]
    generated_by_index: dict[int, list[int]] = {}
    by_prefix_length: dict[int, list[int]] = {}
    for index, prefix in enumerate(prefixes):
        by_prefix_length.setdefault(len(prefix), []).append(index)
    for prefix_length in sorted(by_prefix_length):
        group = by_prefix_length[prefix_length]
        for start in range(0, len(group), batch_size):
            indices = group[start : start + batch_size]
            outputs = model.generate_batch(
                [prefixes[index] for index in indices],
                tokenizer.eos_id,
                [budgets[index] for index in indices],
                device,
            )
            generated_by_index.update(zip(indices, outputs))

    for index, item in enumerate(examples):
        generation_budget = budgets[index]
        effective_budgets.append(generation_budget)
        generated = generated_by_index[index]
        has_eos = bool(generated and generated[-1] == tokenizer.eos_id)
        illegal_special = any(
            token > 255 and token != tokenizer.eos_id
            for token in generated
        )
        well_formed = has_eos and not illegal_special
        terminated += int(has_eos)
        completion = tokenizer.completion(generated) if not illegal_special else ""
        expected_tokens = [*tokenizer.encode(item.completion), tokenizer.eos_id]
        raw_match = generated == expected_tokens
        exact += int(raw_match)
        if "Answer:" in completion:
            extracted = completion.rsplit("Answer:", 1)[-1].strip()
        else:
            extracted = completion.strip()
        answer_match = well_formed and extracted == item.answer.strip()
        answer_exact += int(answer_match)
        record_group(
            operation_counts, item.operation, raw_match, answer_match, has_eos
        )
        record_group(
            difficulty_counts,
            str(item.difficulty),
            raw_match,
            answer_match,
            has_eos,
        )
        if len(previews) < 8:
            previews.append(
                {
                    "prompt": item.prompt,
                    "expected_completion": item.completion,
                    "generated_completion": completion,
                    "expected_answer": item.answer,
                    "well_formed": str(well_formed),
                    "generation_budget": str(generation_budget),
                }
            )
        if retain_items:
            item_results.append(
                {
                    "pair_id": item.pair_id,
                    "operation": item.operation,
                    "difficulty": item.difficulty,
                    "task_type": item.task_type,
                    "expected_answer": item.answer,
                    "generated_answer": extracted,
                    "generated_completion": completion,
                    "raw_exact_match": raw_match,
                    "answer_exact_match": answer_match,
                    "well_formed": well_formed,
                    "has_eos": has_eos,
                    "generation_budget": generation_budget,
                }
            )
    total = max(1, len(examples))
    return {
        "raw_exact_match": exact / total,
        "answer_exact_match": answer_exact / total,
        "raw_exact_count": exact,
        "answer_exact_count": answer_exact,
        "eos_rate": terminated / total,
        "examples": len(examples),
        "configured_max_new_tokens": max_new_tokens,
        "effective_max_new_tokens": max(effective_budgets, default=0),
        "expanded_budget_examples": sum(
            budget > max_new_tokens for budget in effective_budgets
        ),
        "by_operation": finalize_groups(operation_counts),
        "by_difficulty": finalize_groups(difficulty_counts),
        "previews": previews,
        "items": item_results if retain_items else [],
    }


def _checkpoint_payload(
    model: TinyDecoderLM,
    optimizer: "torch.optim.Optimizer",
    scaler: "torch.amp.GradScaler",
    step: int,
    examples_seen: int,
    target_tokens_seen: int,
    fingerprint: str,
    initial_hash: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "step": step,
        "examples_seen": examples_seen,
        "target_tokens_seen": target_tokens_seen,
        "fingerprint": fingerprint,
        "initial_model_hash": initial_hash,
        "model_config": model.config.to_dict(),
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "scaler": scaler.state_dict(),
        "python_rng": random.getstate(),
        "torch_rng": torch.get_rng_state(),
    }
    if torch.cuda.is_available():
        payload["cuda_rng"] = torch.cuda.get_rng_state_all()
    return payload


def _validate_checkpoint_model_config(
    payload: dict[str, Any], model_config: ModelConfig, path: Path
) -> None:
    if payload.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported checkpoint schema at {path}: {payload.get('schema_version')!r}"
        )
    saved_config = payload.get("model_config")
    if not isinstance(saved_config, dict):
        raise ValueError(f"checkpoint is missing its full model configuration: {path}")
    if canonical_json(saved_config) != canonical_json(model_config.to_dict()):
        raise ValueError(f"checkpoint model configuration does not match: {path}")


def _restore_checkpoint(
    path: Path,
    model: TinyDecoderLM,
    optimizer: "torch.optim.Optimizer",
    scaler: "torch.amp.GradScaler",
    fingerprint: str,
) -> tuple[int, int, int, str]:
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise ValueError(f"checkpoint payload is not an object: {path}")
    _validate_checkpoint_model_config(payload, model.config, path)
    if payload.get("fingerprint") != fingerprint:
        raise ValueError("resume checkpoint does not match the requested experiment")
    model.load_state_dict(payload["model"])
    optimizer.load_state_dict(payload["optimizer"])
    scaler.load_state_dict(payload["scaler"])
    random.setstate(payload["python_rng"])
    torch.set_rng_state(payload["torch_rng"])
    if torch.cuda.is_available() and "cuda_rng" in payload:
        torch.cuda.set_rng_state_all(payload["cuda_rng"])
    return (
        int(payload["step"]),
        int(payload["examples_seen"]),
        int(payload["target_tokens_seen"]),
        str(payload["initial_model_hash"]),
    )


def train_arm(
    *,
    arm_name: str,
    stream_key: str,
    train_examples: list[TrainingExample],
    validation_examples: list[TrainingExample],
    model_config: ModelConfig,
    train_config: TrainConfig,
    output: Path,
    device: "torch.device",
    seed: int,
    data_fingerprint: str,
    resume: bool,
) -> dict[str, Any]:
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    tokenizer = ByteTokenizer()
    if model_config.vocab_size != tokenizer.vocab_size:
        raise ValueError(
            f"model vocab_size {model_config.vocab_size} does not match "
            f"{tokenizer.version} vocabulary size {tokenizer.vocab_size}"
        )
    validate_lengths(train_examples, tokenizer, model_config.max_seq_len, f"{arm_name} train")
    validate_lengths(
        validation_examples, tokenizer, model_config.max_seq_len, f"{arm_name} validation"
    )
    curriculum_pools = _curriculum_pools(train_examples, train_config)
    amp_enabled = bool(train_config.amp and device.type == "cuda")
    configure_runtime(seed, train_config.deterministic)
    runtime_factors = _runtime_fingerprint_factors(
        device, amp_enabled, train_config.deterministic
    )
    fingerprint = stable_hash(
        canonical_json(
            {
                "trainer_fingerprint_version": TRAINER_FINGERPRINT_VERSION,
                "arm": arm_name,
                "stream_key": stream_key,
                "model": model_config.to_dict(),
                "training": train_config.to_dict(),
                "seed": seed,
                "data": data_fingerprint,
                "tokenizer": tokenizer.version,
                "runtime": runtime_factors,
            }
        )
    )
    model = TinyDecoderLM(model_config).to(device)
    trainable_parameters = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    optimizer = _optimizer(model, train_config)
    scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled)
    resume_path = output / "resume.pt"
    start_step = 0
    examples_seen = 0
    target_tokens_seen = 0
    initial_hash = model_state_hash(model)
    if resume and resume_path.is_file():
        start_step, examples_seen, target_tokens_seen, initial_hash = _restore_checkpoint(
            resume_path, model, optimizer, scaler, fingerprint
        )
        model.to(device)
        print(
            f"TRAIN_RESUME ARM={arm_name} STEP={start_step}/{train_config.max_steps}",
            flush=True,
        )
    elif resume_path.exists():
        raise ValueError(f"resume checkpoint exists but resume was disabled: {resume_path}")

    validation_subset = _fixed_subset(
        validation_examples, min(train_config.eval_samples, len(validation_examples)), "validation"
    )
    metrics_path = output / "metrics.jsonl"
    if start_step == 0 and not (output / "checkpoint_step_000000.pt").is_file():
        initial_metrics = evaluate_loss(
            model, validation_subset, tokenizer, device, train_config.eval_batch_size
        )
        generation = evaluate_generation(
            model,
            validation_subset,
            tokenizer,
            device,
            train_config.max_new_tokens,
            batch_size=train_config.eval_batch_size,
        )
        row = {
            "step": 0,
            "arm": arm_name,
            "validation": initial_metrics,
            "generation": generation,
            "model_hash": initial_hash,
        }
        _append_jsonl(row, metrics_path)
        payload = _checkpoint_payload(
            model,
            optimizer,
            scaler,
            0,
            0,
            0,
            fingerprint,
            initial_hash,
        )
        _atomic_torch_save(payload, output / "checkpoint_step_000000.pt")
        _atomic_torch_save(payload, resume_path)

    print(
        f"TRAIN_START ARM={arm_name} START_STEP={start_step} "
        f"MAX_STEPS={train_config.max_steps} PARAMETERS={trainable_parameters} "
        f"PROGRESS_EVERY={train_config.progress_every_steps}",
        flush=True,
    )

    started = time.perf_counter()
    last_train_loss = None
    last_gradient_norm = None
    amp_overflow_retries = 0
    progress_path = output / "progress.jsonl"
    window_loss_sum = 0.0
    window_target_tokens = 0
    window_examples = 0
    window_steps = 0
    window_training_seconds = 0.0
    training_seconds = 0.0
    active_stage_index: int | None = None
    if start_step >= train_config.max_steps and metrics_path.is_file():
        with metrics_path.open("r", encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
        final_rows = [row for row in rows if int(row.get("step", -1)) == start_step]
        if not final_rows:
            raise RuntimeError("final resume checkpoint has no matching metrics row")
        last_train_loss = final_rows[-1].get("training_loss")
        last_gradient_norm = final_rows[-1].get("gradient_norm")
        summary_path = output / "training_summary.json"
        if summary_path.is_file():
            with summary_path.open("r", encoding="utf-8") as handle:
                existing_summary = json.load(handle)
            if (
                not isinstance(existing_summary, dict)
                or existing_summary.get("status") != "PASS"
                or int(existing_summary.get("optimizer_steps", -1))
                != train_config.max_steps
                or existing_summary.get("fingerprint") != fingerprint
                or existing_summary.get("final_model_hash") != model_state_hash(model)
            ):
                raise RuntimeError(f"stale or invalid training summary: {summary_path}")
            print(
                f"TRAIN_ARM={arm_name} STEP={train_config.max_steps} STATUS=REUSED",
                flush=True,
            )
            return existing_summary
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    for step in range(start_step + 1, train_config.max_steps + 1):
        stage_index, stage, stage_pool, stage_pool_fingerprint = _curriculum_at_step(
            curriculum_pools, step
        )
        if active_stage_index != stage_index:
            active_stage_index = stage_index
            difficulty_text = ",".join(map(str, stage.difficulties)) or "all"
            operation_text = ",".join(stage.operations) or "all"
            print(
                f"CURRICULUM_ARM={arm_name} STAGE={stage_index + 1}/{len(curriculum_pools)} "
                f"NAME={stage.name} END_STEP={stage.end_step} POOL={len(stage_pool)} "
                f"DIFFICULTIES={difficulty_text} OPERATIONS={operation_text}",
                flush=True,
            )
        training_step_started = time.perf_counter()
        model.train()
        learning_rate = _learning_rate(train_config, step)
        for group in optimizer.param_groups:
            group["lr"] = learning_rate
        batches = [
            _batch_indices_from_pool(
                stage_pool,
                train_config.micro_batch_size,
                seed,
                stream_key,
                step,
                micro,
            )
            for micro in range(train_config.gradient_accumulation)
        ]
        token_totals = []
        for indices in batches:
            token_totals.append(
                sum(
                    len(tokenizer.encode(train_examples[index].completion)) + 1
                    for index in indices
                )
            )
        accumulation_tokens = sum(token_totals)
        for overflow_attempt in range(16):
            optimizer.zero_grad(set_to_none=True)
            step_loss_sum = 0.0
            for indices in batches:
                input_ids, labels, _, _ = _collate(
                    train_examples, indices, tokenizer, device
                )
                with torch.amp.autocast(
                    device_type=device.type,
                    dtype=torch.float16,
                    enabled=amp_enabled,
                ):
                    logits = model(input_ids)
                    loss_sum = F.cross_entropy(
                        logits.reshape(-1, logits.shape[-1]),
                        labels.reshape(-1),
                        ignore_index=-100,
                        reduction="sum",
                    )
                    normalized_loss = loss_sum / accumulation_tokens
                if not torch.isfinite(loss_sum):
                    raise RuntimeError(
                        f"nonfinite training loss in {arm_name} at step {step}"
                    )
                scaler.scale(normalized_loss).backward()
                step_loss_sum += float(loss_sum.detach().item())
            scaler.unscale_(optimizer)
            gradient_norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(), train_config.gradient_clip
            )
            if torch.isfinite(gradient_norm):
                last_gradient_norm = float(gradient_norm.item())
                scaler.step(optimizer)
                scaler.update()
                break
            if not amp_enabled:
                raise RuntimeError(
                    f"nonfinite gradient norm in {arm_name} at step {step}"
                )
            gradient_has_nonfinite_value = any(
                parameter.grad is not None
                and not bool(torch.isfinite(parameter.grad).all().item())
                for parameter in model.parameters()
            )
            if not gradient_has_nonfinite_value:
                raise RuntimeError(
                    f"gradient norm overflowed despite finite gradient values in "
                    f"{arm_name} at step {step}"
                )
            # GradScaler records the overflow during unscale_. Let it skip the
            # update and reduce the scale, then retry this same logical step.
            previous_scale = float(scaler.get_scale())
            scaler.step(optimizer)
            scaler.update()
            amp_overflow_retries += 1
            print(
                f"TRAIN_ARM={arm_name} STEP={step} AMP_OVERFLOW_RETRY="
                f"{overflow_attempt + 1} SCALE={previous_scale:.1f}->"
                f"{float(scaler.get_scale()):.1f}",
                flush=True,
            )
        else:
            raise RuntimeError(
                f"AMP gradients remained nonfinite after 16 retries in {arm_name} "
                f"at step {step}"
            )
        examples_seen += train_config.micro_batch_size * train_config.gradient_accumulation
        target_tokens_seen += accumulation_tokens
        last_train_loss = step_loss_sum / max(1, accumulation_tokens)
        training_step_seconds = time.perf_counter() - training_step_started
        training_seconds += training_step_seconds
        window_training_seconds += training_step_seconds
        window_loss_sum += step_loss_sum
        window_target_tokens += accumulation_tokens
        window_examples += train_config.micro_batch_size * train_config.gradient_accumulation
        window_steps += 1

        progress_due = (
            step % train_config.progress_every_steps == 0 or step == train_config.max_steps
        )
        if progress_due:
            elapsed = time.perf_counter() - started
            completed_this_invocation = max(1, step - start_step)
            eta_seconds = (
                training_seconds
                * (train_config.max_steps - step)
                / completed_this_invocation
            )
            rolling_loss = window_loss_sum / max(1, window_target_tokens)
            progress_row = {
                "arm": arm_name,
                "step": step,
                "max_steps": train_config.max_steps,
                "stage": stage.name,
                "stage_index": stage_index + 1,
                "stage_count": len(curriculum_pools),
                "stage_pool_examples": len(stage_pool),
                "stage_pool_pair_fingerprint": stage_pool_fingerprint,
                "window_steps": window_steps,
                "rolling_training_loss": rolling_loss,
                "current_training_loss": last_train_loss,
                "gradient_norm": last_gradient_norm,
                "learning_rate": learning_rate,
                "examples_seen": examples_seen,
                "target_tokens_seen": target_tokens_seen,
                "examples_per_second": window_examples
                / max(1e-9, window_training_seconds),
                "target_tokens_per_second": window_target_tokens
                / max(1e-9, window_training_seconds),
                "window_training_seconds": round(window_training_seconds, 6),
                "training_seconds_this_invocation": round(training_seconds, 6),
                "elapsed_seconds": round(elapsed, 6),
                "eta_training_seconds": round(eta_seconds, 3),
                "peak_vram_gb": (
                    round(torch.cuda.max_memory_allocated(device) / 1073741824, 4)
                    if device.type == "cuda"
                    else 0.0
                ),
            }
            _append_jsonl(progress_row, progress_path)
            print(
                f"TRAIN_PROGRESS ARM={arm_name} STEP={step}/{train_config.max_steps} "
                f"STAGE={stage_index + 1}/{len(curriculum_pools)}:{stage.name} "
                f"LOSS_ROLLING_{window_steps}={rolling_loss:.6f} "
                f"LOSS_CURRENT={last_train_loss:.6f} LR={learning_rate:.8f} "
                f"GRAD_NORM={last_gradient_norm:.6f} EXAMPLES_SEEN={examples_seen} "
                f"EXAMPLES_PER_SECOND={progress_row['examples_per_second']:.2f} "
                f"TARGET_TOKENS_PER_SECOND={progress_row['target_tokens_per_second']:.2f} "
                f"ETA_SECONDS={eta_seconds:.0f} "
                f"PEAK_VRAM_GB={progress_row['peak_vram_gb']:.4f}",
                flush=True,
            )
            window_loss_sum = 0.0
            window_target_tokens = 0
            window_examples = 0
            window_steps = 0
            window_training_seconds = 0.0

        named_checkpoint_due = step in train_config.checkpoint_steps
        validation_due = (
            named_checkpoint_due
            or step == train_config.max_steps
            or (
                train_config.generation_every_steps > 0
                and step % train_config.generation_every_steps == 0
            )
            or (
                train_config.validation_every_steps > 0
                and step % train_config.validation_every_steps == 0
            )
        )
        generation_due = (
            named_checkpoint_due
            or step == train_config.max_steps
            or (
                train_config.generation_every_steps > 0
                and step % train_config.generation_every_steps == 0
            )
        )
        if validation_due:
            validation = evaluate_loss(
                model, validation_subset, tokenizer, device, train_config.eval_batch_size
            )
            generation = (
                evaluate_generation(
                    model,
                    validation_subset,
                    tokenizer,
                    device,
                    train_config.max_new_tokens,
                    batch_size=train_config.eval_batch_size,
                )
                if generation_due
                else None
            )
            current_hash = model_state_hash(model) if named_checkpoint_due else None
            row = {
                "step": step,
                "arm": arm_name,
                "training_loss": last_train_loss,
                "gradient_norm": last_gradient_norm,
                "learning_rate": learning_rate,
                "examples_seen": examples_seen,
                "target_tokens_seen": target_tokens_seen,
                "amp_overflow_retries_this_invocation": amp_overflow_retries,
                "validation": validation,
                "generation": generation,
                "model_hash": current_hash,
                "elapsed_seconds": round(time.perf_counter() - started, 6),
                "curriculum_stage": stage.to_dict(),
                "curriculum_pool_examples": len(stage_pool),
                "curriculum_pool_pair_fingerprint": stage_pool_fingerprint,
            }
            _append_jsonl(row, metrics_path)
            print(
                f"VALIDATION_ARM={arm_name} STEP={step}/{train_config.max_steps} "
                f"LOSS={validation['loss']:.6f} "
                f"TOKEN_ACCURACY={validation['token_accuracy']:.6f}",
                flush=True,
            )
            if generation is not None:
                print(
                    f"GENERATION_ARM={arm_name} STEP={step}/{train_config.max_steps} "
                    f"ANSWER_EXACT={generation['answer_exact_count']}/{generation['examples']} "
                    f"RATE={generation['answer_exact_match']:.6f}",
                    flush=True,
                )

        resume_due = (
            named_checkpoint_due
            or step == train_config.max_steps
            or step % train_config.resume_every_steps == 0
        )
        if resume_due:
            payload = _checkpoint_payload(
                model,
                optimizer,
                scaler,
                step,
                examples_seen,
                target_tokens_seen,
                fingerprint,
                initial_hash,
            )
            if named_checkpoint_due:
                _atomic_torch_save(payload, output / f"checkpoint_step_{step:06d}.pt")
            _atomic_torch_save(payload, resume_path)

    final_hash = model_state_hash(model)
    if final_hash == initial_hash:
        raise RuntimeError(f"model weights did not change for trained arm {arm_name}")
    initial_payload = torch.load(
        output / "checkpoint_step_000000.pt", map_location="cpu", weights_only=False
    )
    if not isinstance(initial_payload, dict):
        raise ValueError("initial checkpoint payload is not an object")
    _validate_checkpoint_model_config(
        initial_payload, model_config, output / "checkpoint_step_000000.pt"
    )
    squared_delta = 0.0
    for name, tensor in model.state_dict().items():
        difference = tensor.detach().cpu().float() - initial_payload["model"][name].float()
        squared_delta += float(difference.square().sum().item())
    summary = {
        "status": "PASS",
        "arm": arm_name,
        "step": train_config.max_steps,
        "optimizer_steps": train_config.max_steps,
        "examples_seen": examples_seen,
        "target_tokens_seen": target_tokens_seen,
        "trainable_parameters": trainable_parameters,
        "initial_model_hash": initial_hash,
        "final_model_hash": final_hash,
        "parameter_delta_norm": math.sqrt(squared_delta),
        "last_training_loss": last_train_loss,
        "last_gradient_norm": last_gradient_norm,
        "amp_overflow_retries_this_invocation": amp_overflow_retries,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "peak_vram_gb": (
            round(torch.cuda.max_memory_allocated(device) / 1073741824, 4)
            if device.type == "cuda"
            else 0.0
        ),
        "progress_every_steps": train_config.progress_every_steps,
        "curriculum": [
            {
                **stage.to_dict(),
                "eligible_examples": len(pool),
                "eligible_pair_fingerprint": pair_fingerprint,
            }
            for stage, pool, pair_fingerprint in curriculum_pools
        ],
        "fingerprint": fingerprint,
    }
    _atomic_json(summary, output / "training_summary.json")
    return summary


def load_model_checkpoint(
    checkpoint: Path,
    model_config: ModelConfig,
    device: "torch.device",
) -> tuple[TinyDecoderLM, dict[str, Any]]:
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise ValueError(f"checkpoint payload is not an object: {checkpoint}")
    _validate_checkpoint_model_config(payload, model_config, checkpoint)
    model = TinyDecoderLM(model_config)
    model.load_state_dict(payload["model"])
    model.to(device).eval()
    return model, payload
