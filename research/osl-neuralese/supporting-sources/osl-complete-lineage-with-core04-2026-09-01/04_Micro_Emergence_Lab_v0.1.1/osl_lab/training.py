"""Reproducible training, checkpointing, resume, and evaluation for Micro OSL."""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import asdict, dataclass, field
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import random
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .metrics import (
    compute_algebra_residuals,
    counterfactual_metrics,
    evaluate_by_split,
    length_generalization_metrics,
)
from .model import (
    TORCH_AVAILABLE,
    DeterministicVocabulary,
    ModelConfig,
    OSLTransformer,
    StableLabelEncoder,
    build_operator_vocabulary,
    canonical_json,
    extract_operator_name,
    require_torch,
    text_from_record,
)
from .worlds import answer_vocabulary, get_world


if TORCH_AVAILABLE:  # pragma: no branch
    import torch
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, Dataset


@dataclass
class TrainingConfig:
    arm: str = "answer_only"
    epochs: int = 12
    batch_size: int = 64
    learning_rate: float = 3e-4
    weight_decay: float = 1e-2
    gradient_clip: float = 1.0
    seed: int = 17
    max_length: int = 256
    min_frequency: int = 1
    max_vocab_size: int | None = 50_000
    hash_buckets: int = 2048
    num_workers: int = 0
    early_stopping_patience: int = 4
    selection_metric: str = "query_macro_accuracy"
    amp: bool = True
    loss_weights: dict[str, float] = field(
        default_factory=lambda: {
            "answer": 1.0,
            "state": 0.5,
            "equivalence": 0.2,
            "operator_alignment": 0.1,
            "operator_laws": 0.1,
        }
    )
    model: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any] | None) -> "TrainingConfig":
        raw = dict(payload or {})
        if "lr" in raw and "learning_rate" not in raw:
            raw["learning_rate"] = raw.pop("lr")
        model = dict(raw.pop("model", {}))
        weights = dict(raw.pop("loss_weights", {}))
        known = cls.__dataclass_fields__
        config = cls(**{key: value for key, value in raw.items() if key in known})
        config.model.update(model)
        config.loss_weights.update({key: float(value) for key, value in weights.items()})
        return config


def _semantic_equivalence_id(record: Mapping[str, Any]) -> str:
    if record.get("equivalence_id") is not None:
        return f"explicit::{record['equivalence_id']}"
    transform = record.get(
        "canonical_transform_id",
        record.get("transform_id", record.get("semantic_id", record.get("id", ""))),
    )
    # A transform alone is not an output-equivalence class.  Context, state,
    # and query must also agree or the contrastive loss can erase distinctions.
    return canonical_json(
        {
            "world": record.get("world", ""),
            "transform": transform,
            "initial_state": record.get("initial_state", {}),
            "question_id": record.get("question_id", record.get("question", "")),
        }
    )


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Expected an object at {path}:{line_number}")
            records.append(value)
    return records


def _choose_device(requested: str = "auto") -> str:
    require_torch()
    requested = str(requested).lower()
    if requested == "auto":
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    if requested.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested, but this PyTorch installation cannot access CUDA")
    if requested == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS was requested but is unavailable")
    if requested != "cpu" and not requested.startswith("cuda") and requested != "mps":
        raise ValueError("device must be auto, cpu, cuda, cuda:N, or mps")
    return requested


def set_deterministic_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    if TORCH_AVAILABLE:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            cuda_backends = getattr(torch.backends, "cuda", None)
            if cuda_backends is not None:
                if hasattr(cuda_backends, "enable_flash_sdp"):
                    cuda_backends.enable_flash_sdp(False)
                if hasattr(cuda_backends, "enable_mem_efficient_sdp"):
                    cuda_backends.enable_mem_efficient_sdp(False)
                if hasattr(cuda_backends, "enable_math_sdp"):
                    cuda_backends.enable_math_sdp(True)
        torch.use_deterministic_algorithms(True)
        if getattr(torch.backends, "cudnn", None) is not None:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False


def _validation_selection_score(behavior: Mapping[str, Any], metric: str) -> float:
    """Resolve the preregistered checkpoint-selection metric."""

    if metric == "accuracy":
        return float(behavior["overall"]["accuracy"])
    if metric == "macro_f1":
        return float(behavior["overall"]["macro_f1"])
    balanced = behavior.get("balanced", {})
    if metric in balanced and isinstance(balanced[metric], (int, float)):
        return float(balanced[metric])
    overall = balanced.get("overall", {}) if isinstance(balanced, Mapping) else {}
    if metric in overall and isinstance(overall[metric], (int, float)):
        return float(overall[metric])
    available = sorted(
        key for key, value in overall.items() if isinstance(value, (int, float))
    )
    raise ValueError(
        f"unknown validation selection metric {metric!r}; available balanced metrics: {available}"
    )


def _normalize_model_keys(payload: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    aliases = {
        "hidden_dim": "d_model",
        "embedding_dim": "d_model",
        "num_heads": "n_heads",
        "num_layers": "n_layers",
        "feedforward_dim": "d_ff",
    }
    for old, new in aliases.items():
        if old in result and new not in result:
            result[new] = result.pop(old)
    result.pop("kind", None)
    return result


if TORCH_AVAILABLE:

    class OSLDataset(Dataset):
        def __init__(
            self,
            records: Sequence[Mapping[str, Any]],
            tokenizer: DeterministicVocabulary,
            answer_encoder: StableLabelEncoder,
            state_encoder: StableLabelEncoder,
            operator_vocabulary: Mapping[str, int],
            *,
            max_length: int,
            include_positive: bool,
        ) -> None:
            self.records = [dict(record) for record in records]
            self.tokenizer = tokenizer
            self.answer_encoder = answer_encoder
            self.state_encoder = state_encoder
            self.operator_vocabulary = dict(operator_vocabulary)
            self.max_length = int(max_length)
            self.include_positive = bool(include_positive)
            groups: dict[str, list[int]] = {}
            for index, record in enumerate(self.records):
                groups.setdefault(_semantic_equivalence_id(record), []).append(index)
            self.positive_index: dict[int, int] = {}
            for indices in groups.values():
                ordered = sorted(indices)
                if len(ordered) >= 2:
                    for position, index in enumerate(ordered):
                        self.positive_index[index] = ordered[(position + 1) % len(ordered)]

        def __len__(self) -> int:
            return len(self.records)

        def _encoded_text(self, record: Mapping[str, Any]) -> dict[str, list[int]]:
            return self.tokenizer.encode_pair(
                str(record.get("story", "")),
                str(record.get("question", "")),
                max_length=self.max_length,
            )

        def __getitem__(self, index: int) -> dict[str, Any]:
            record = self.records[index]
            item: dict[str, Any] = self._encoded_text(record)
            answer = str(record.get("answer", ""))
            item["answer_target"] = self.answer_encoder.label_to_id.get(answer, -100)
            state = canonical_json(record.get("final_state", {}))
            item["state_target"] = self.state_encoder.label_to_id.get(state, -100)
            program_ids: list[int] = []
            program_mask: list[int] = []
            for event in record.get("program", []) or []:
                name = extract_operator_name(event)
                if name in self.operator_vocabulary:
                    program_ids.append(self.operator_vocabulary[name])
                    program_mask.append(1)
                else:
                    program_ids.append(0)
                    program_mask.append(0)
            item["program_ids"] = program_ids
            item["program_mask"] = program_mask
            item["record_index"] = index
            item["equivalence_id"] = _semantic_equivalence_id(record)
            item["record"] = record
            positive = self.positive_index.get(index)
            item["positive_mask"] = int(self.include_positive and positive is not None)
            positive_record = self.records[positive] if positive is not None else record
            encoded_positive = self._encoded_text(positive_record)
            for key, value in encoded_positive.items():
                item[f"positive_{key}"] = value
            return item


    def _collate(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        tensor_keys = ("input_ids", "attention_mask", "token_type_ids")
        result: dict[str, Any] = {
            key: torch.tensor([item[key] for item in items], dtype=torch.long) for key in tensor_keys
        }
        for key in tensor_keys:
            result[f"positive_{key}"] = torch.tensor(
                [item[f"positive_{key}"] for item in items], dtype=torch.long
            )
        result["answer_target"] = torch.tensor(
            [item["answer_target"] for item in items], dtype=torch.long
        )
        result["state_target"] = torch.tensor(
            [item["state_target"] for item in items], dtype=torch.long
        )
        result["positive_mask"] = torch.tensor(
            [item["positive_mask"] for item in items], dtype=torch.bool
        )
        maximum_program = max(1, max(len(item["program_ids"]) for item in items))
        program_ids = torch.zeros((len(items), maximum_program), dtype=torch.long)
        program_mask = torch.zeros((len(items), maximum_program), dtype=torch.bool)
        for row, item in enumerate(items):
            length = len(item["program_ids"])
            if length:
                program_ids[row, :length] = torch.tensor(item["program_ids"], dtype=torch.long)
                program_mask[row, :length] = torch.tensor(item["program_mask"], dtype=torch.bool)
        result["program_ids"] = program_ids
        result["program_mask"] = program_mask
        result["equivalence_ids"] = [str(item["equivalence_id"]) for item in items]
        result["record_indices"] = [int(item["record_index"]) for item in items]
        result["records"] = [item["record"] for item in items]
        return result


def _build_encoders(
    train_records: Sequence[Mapping[str, Any]],
    config: TrainingConfig,
    tokenizer_records: Sequence[Mapping[str, Any]] | None = None,
) -> tuple[DeterministicVocabulary, StableLabelEncoder, StableLabelEncoder, dict[str, int]]:
    tokenizer_corpus = tokenizer_records if tokenizer_records is not None else train_records
    vocabulary = DeterministicVocabulary(
        lowercase=True,
        min_frequency=config.min_frequency,
        max_size=config.max_vocab_size,
        hash_buckets=config.hash_buckets,
    ).fit(text_from_record(record) for record in tokenizer_corpus)
    declared_answers = answer_vocabulary()
    observed_answers = {str(record.get("answer", "")) for record in train_records}
    unknown_answers = sorted(observed_answers - set(declared_answers))
    if unknown_answers:
        raise ValueError(
            "training records contain answers outside the declared finite-world ontology: "
            f"{unknown_answers}"
        )
    answers = StableLabelEncoder().fit(declared_answers)
    states = StableLabelEncoder().fit(
        canonical_json(record.get("final_state", {})) for record in train_records
    )
    operators = build_operator_vocabulary(train_records)
    return vocabulary, answers, states, operators


def _build_model_config(
    config: TrainingConfig,
    vocabulary: DeterministicVocabulary,
    answers: StableLabelEncoder,
    states: StableLabelEncoder,
    operators: Mapping[str, int],
) -> ModelConfig:
    model_values = _normalize_model_keys(config.model)
    defaults = {
        "vocab_size": len(vocabulary),
        "num_answers": len(answers),
        "num_states": len(states) if config.arm in {"state_supervised", "combined"} else 0,
        "num_operators": len(operators)
        if config.arm in {"operator_regularized", "combined"}
        else 0,
        "max_length": config.max_length,
        "arm": config.arm,
    }
    defaults.update(model_values)
    # Corpus-derived dimensions may not be overridden accidentally.
    defaults["vocab_size"] = len(vocabulary)
    defaults["num_answers"] = len(answers)
    defaults["num_states"] = len(states) if config.arm in {"state_supervised", "combined"} else 0
    defaults["num_operators"] = (
        len(operators) if config.arm in {"operator_regularized", "combined"} else 0
    )
    defaults["max_length"] = config.max_length
    defaults["arm"] = config.arm
    return ModelConfig.from_dict(defaults)


def _move_batch(batch: Mapping[str, Any], device: str) -> dict[str, Any]:
    if not TORCH_AVAILABLE:
        return dict(batch)
    return {
        key: value.to(device) if isinstance(value, torch.Tensor) else value
        for key, value in batch.items()
    }


def _equivalence_loss(representation: Any, positive: Any, mask: Any) -> Any:
    if not bool(mask.any()):
        return representation.sum() * 0.0
    anchor = F.normalize(representation[mask], dim=-1)
    match = F.normalize(positive[mask], dim=-1)
    attraction = 1.0 - (anchor * match).sum(dim=-1)
    if len(anchor) <= 1:
        return attraction.mean()
    negative = torch.roll(match, shifts=1, dims=0)
    repulsion = F.relu((anchor * negative).sum(dim=-1) - 0.2)
    return attraction.mean() + 0.25 * repulsion.mean()


def _extract_law_specs(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    laws: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        metadata = record.get("metadata", {})
        if not isinstance(metadata, Mapping):
            continue
        raw: Any = metadata.get("laws", metadata.get("law"))
        if raw is None:
            continue
        entries = raw if isinstance(raw, list) else [raw]
        for entry in entries:
            if isinstance(entry, str):
                specification = {"kind": entry}
                names = [extract_operator_name(event) for event in record.get("program", []) or []]
                if names:
                    specification["op"] = names[0]
                if len(names) > 1:
                    specification["left"], specification["right"] = names[:2]
            elif isinstance(entry, Mapping):
                specification = dict(entry)
            else:
                continue
            key = canonical_json(specification)
            if key not in seen:
                seen.add(key)
                laws.append(specification)
    # Training records deliberately omit the held-out law sequences.  The
    # operator arm regularizes the declared primitive matrices, while the text
    # examples exercising those relations remain sealed behavioral tests.
    for world_name in sorted({str(record.get("world", "")) for record in records}):
        if not world_name:
            continue
        try:
            declared_laws = get_world(world_name).laws
        except (KeyError, ValueError):
            continue
        for law in declared_laws:
            specification: dict[str, Any] = {
                "law_id": law.law_id,
                "kind": law.kind,
                "left_program": list(law.left),
                "right_program": list(law.right),
                "description": law.description,
            }
            if law.kind in {"idempotence", "idempotent"} and law.left:
                specification["op"] = law.left[0]
            elif law.kind in {"inverse", "inverses"} and len(law.left) >= 2:
                specification["left"] = law.left[0]
                specification["right"] = law.left[1]
            elif law.kind in {"commutation", "commute", "commutative"} and len(law.left) >= 2:
                specification["left"] = law.left[0]
                specification["right"] = law.left[1]
            key = canonical_json(specification)
            if key not in seen:
                seen.add(key)
                laws.append(specification)
    return laws


def _resolve_operator(spec: Mapping[str, Any], keys: Sequence[str], vocabulary: Mapping[str, int]) -> int:
    for key in keys:
        if spec.get(key) is not None:
            value = spec[key]
            if isinstance(value, int):
                return value
            if str(value) in vocabulary:
                return vocabulary[str(value)]
    raise KeyError(f"No known operator found in fields {list(keys)} for law {dict(spec)}")


def _operator_law_loss(model: Any, laws: Sequence[Mapping[str, Any]], vocabulary: Mapping[str, int]) -> Any:
    matrices = model.operator_matrices
    if matrices is None or not laws:
        return next(model.parameters()).sum() * 0.0
    identity = torch.eye(matrices.shape[-1], device=matrices.device, dtype=matrices.dtype)
    losses = []
    for law in laws:
        kind = str(law.get("kind", law.get("law", ""))).lower()
        try:
            if kind in {"idempotent", "idempotence"}:
                index = _resolve_operator(law, ("op", "operator"), vocabulary)
                matrix = matrices[index]
                losses.append(F.mse_loss(matrix @ matrix, matrix))
            elif kind in {"inverse", "inverses"}:
                left = matrices[_resolve_operator(law, ("left", "op_a"), vocabulary)]
                right = matrices[_resolve_operator(law, ("right", "op_b"), vocabulary)]
                losses.extend([F.mse_loss(left @ right, identity), F.mse_loss(right @ left, identity)])
            elif kind in {"commute", "commutation", "commutative"}:
                left = matrices[_resolve_operator(law, ("left", "op_a"), vocabulary)]
                right = matrices[_resolve_operator(law, ("right", "op_b"), vocabulary)]
                losses.append(F.mse_loss(left @ right, right @ left))
            elif kind in {"identity"}:
                index = _resolve_operator(law, ("op", "operator"), vocabulary)
                losses.append(F.mse_loss(matrices[index], identity))
        except (KeyError, IndexError):
            continue
    return torch.stack(losses).mean() if losses else matrices.sum() * 0.0


def _program_alignment_loss(outputs: Mapping[str, Any], program_mask: Any) -> Any:
    program = outputs.get("program_representation")
    pooled = outputs["pooled"]
    valid = program_mask.any(dim=1)
    if program is None or not bool(valid.any()):
        return pooled.sum() * 0.0
    return (1.0 - F.cosine_similarity(pooled[valid], program[valid], dim=-1)).mean()


def _loss_components(
    model: Any,
    batch: Mapping[str, Any],
    outputs: Mapping[str, Any],
    config: TrainingConfig,
    laws: Sequence[Mapping[str, Any]],
    operators: Mapping[str, int],
) -> dict[str, Any]:
    components: dict[str, Any] = {}
    components["answer"] = F.cross_entropy(outputs["answer_logits"], batch["answer_target"])
    if config.arm in {"state_supervised", "combined"} and outputs.get("state_logits") is not None:
        components["state"] = F.cross_entropy(
            outputs["state_logits"], batch["state_target"], ignore_index=-100
        )
    if config.arm in {"equivalence_regularized", "combined"}:
        positive_outputs = model(
            batch["positive_input_ids"],
            batch["positive_attention_mask"],
            batch["positive_token_type_ids"],
        )
        components["equivalence"] = _equivalence_loss(
            outputs["representation"], positive_outputs["representation"], batch["positive_mask"]
        )
    if config.arm in {"operator_regularized", "combined"}:
        components["operator_alignment"] = _program_alignment_loss(outputs, batch["program_mask"])
        components["operator_laws"] = _operator_law_loss(model, laws, operators)
    return components


def _weighted_loss(components: Mapping[str, Any], weights: Mapping[str, float]) -> Any:
    return sum(float(weights.get(name, 1.0)) * value for name, value in components.items())


def _autocast_context(device: str, enabled: bool) -> Any:
    if not TORCH_AVAILABLE or not enabled or not device.startswith("cuda"):
        return nullcontext()
    if hasattr(torch, "amp") and hasattr(torch.amp, "autocast"):
        return torch.amp.autocast("cuda", dtype=torch.float16)
    return torch.cuda.amp.autocast(dtype=torch.float16)


def _grad_scaler(device: str, enabled: bool) -> Any:
    active = bool(enabled and device.startswith("cuda"))
    if hasattr(torch, "amp") and hasattr(torch.amp, "GradScaler"):
        return torch.amp.GradScaler("cuda", enabled=active)
    return torch.cuda.amp.GradScaler(enabled=active)


def _atomic_torch_save(payload: Mapping[str, Any], path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(dict(payload), temporary)
    os.replace(temporary, path)


def _model_state_digest(model: Any) -> str:
    """Hash initialized parameters so matched arms can prove identical starts."""

    digest = sha256()
    for name, tensor in sorted(model.state_dict().items()):
        value = tensor.detach().cpu().contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(canonical_json(list(value.shape)).encode("ascii"))
        digest.update(value.numpy().tobytes(order="C"))
    return digest.hexdigest()


def _model_parameter_schema_digest(model: Any) -> str:
    """Hash parameter and buffer names, dtypes, and shapes without their values."""

    schema = [
        {
            "name": name,
            "dtype": str(tensor.dtype),
            "shape": list(tensor.shape),
        }
        for name, tensor in sorted(model.state_dict().items())
    ]
    return sha256(canonical_json(schema).encode("utf-8")).hexdigest()


def _initialization_contract(
    model: Any,
    tokenizer: DeterministicVocabulary,
    answers: StableLabelEncoder,
    initial_model_sha256: str | None,
) -> dict[str, Any]:
    """Fingerprint every identity-bearing component shared by matched arms."""

    return {
        "schema": "osl.micro-emergence.initialization-contract.v1",
        "answer_ontology_policy": "exhaustive_declared_finite_worlds",
        "tokenizer_sha256": sha256(
            canonical_json(tokenizer.to_dict()).encode("utf-8")
        ).hexdigest(),
        "answer_classes_sha256": sha256(
            canonical_json(answers.labels).encode("utf-8")
        ).hexdigest(),
        "model_parameter_schema_sha256": _model_parameter_schema_digest(model),
        "initial_model_sha256": initial_model_sha256,
    }


def _effective_corpus_summary(
    records: Sequence[Mapping[str, Any]], tokenizer: DeterministicVocabulary
) -> dict[str, Any]:
    """Describe the exact optimization corpus without exposing local paths."""

    worlds: Counter[str] = Counter()
    queries: Counter[str] = Counter()
    answers: Counter[str] = Counter()
    token_lengths: list[int] = []
    for record in records:
        world = str(record.get("world", "unspecified"))
        query = str(record.get("question_id", record.get("question", "unspecified")))
        worlds[world] += 1
        queries[f"{world}::{query}"] += 1
        answers[str(record.get("answer", ""))] += 1
        token_lengths.append(len(tokenizer.tokenize(text_from_record(record))))
    return {
        "records": len(records),
        "ordered_content_sha256": _ordered_corpus_digest(records),
        "world_counts": dict(sorted(worlds.items())),
        "query_counts": dict(sorted(queries.items())),
        "answer_counts": dict(sorted(answers.items())),
        "input_token_lengths": {
            "minimum": min(token_lengths) if token_lengths else 0,
            "mean": float(np.mean(token_lengths)) if token_lengths else 0.0,
            "maximum": max(token_lengths) if token_lengths else 0,
        },
    }


def _ordered_corpus_digest(records: Sequence[Mapping[str, Any]]) -> str:
    """Hash the exact ordered optimization records for safe resume checks."""

    digest = sha256()
    for record in records:
        digest.update(canonical_json(record).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _capture_rng_state() -> dict[str, Any]:
    state: dict[str, Any] = {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state(),
    }
    if torch.cuda.is_available():
        state["cuda"] = torch.cuda.get_rng_state_all()
    return state


def _restore_rng_state(state: Mapping[str, Any]) -> None:
    if not state:
        return
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])
    if "cuda" in state and torch.cuda.is_available():
        torch.cuda.set_rng_state_all(state["cuda"])


def _load_torch_checkpoint(path: str | Path, *, map_location: str = "cpu") -> dict[str, Any]:
    require_torch()
    try:
        return torch.load(path, map_location=map_location, weights_only=False)
    except TypeError:  # PyTorch before the weights_only argument
        return torch.load(path, map_location=map_location)


def _checkpoint_payload(
    *,
    model: Any,
    optimizer: Any,
    epoch: int,
    global_step: int,
    best_validation_accuracy: float,
    best_validation_score: float,
    epochs_without_improvement: int,
    training_config: TrainingConfig,
    tokenizer: DeterministicVocabulary,
    answer_encoder: StableLabelEncoder,
    state_encoder: StableLabelEncoder,
    operator_vocabulary: Mapping[str, int],
    laws: Sequence[Mapping[str, Any]],
    history: Sequence[Mapping[str, Any]],
    initial_model_sha256: str | None,
    initialization_contract: Mapping[str, Any],
    effective_corpus_ordered_sha256: str,
) -> dict[str, Any]:
    return {
        "format_version": 5,
        "epoch": int(epoch),
        "global_step": int(global_step),
        "best_validation_accuracy": float(best_validation_accuracy),
        "best_validation_score": float(best_validation_score),
        "selection_metric": training_config.selection_metric,
        "epochs_without_improvement": int(epochs_without_improvement),
        "training_config": asdict(training_config),
        "model_config": model.config.to_dict(),
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "tokenizer": tokenizer.to_dict(),
        "answer_encoder": answer_encoder.to_dict(),
        "state_encoder": state_encoder.to_dict(),
        "operator_vocabulary": dict(operator_vocabulary),
        "laws": [dict(law) for law in laws],
        "history": list(history),
        "initial_model_sha256": initial_model_sha256,
        "initialization_contract": dict(initialization_contract),
        "effective_corpus_ordered_sha256": effective_corpus_ordered_sha256,
        "rng_state": _capture_rng_state(),
    }


def _predict_loader(model: Any, loader: Any, device: str) -> tuple[list[str], list[int], list[int], list[int]]:
    model.eval()
    predicted_ids: list[int] = []
    state_ids: list[int] = []
    record_indices: list[int] = []
    gold_ids: list[int] = []
    with torch.no_grad():
        for raw_batch in loader:
            batch = _move_batch(raw_batch, device)
            outputs = model(
                batch["input_ids"],
                batch["attention_mask"],
                batch["token_type_ids"],
                batch["program_ids"] if model.operator_matrices is not None else None,
                batch["program_mask"] if model.operator_matrices is not None else None,
            )
            predicted_ids.extend(outputs["answer_logits"].argmax(dim=-1).cpu().tolist())
            gold_ids.extend(batch["answer_target"].cpu().tolist())
            record_indices.extend(raw_batch["record_indices"])
            if outputs.get("state_logits") is not None:
                state_ids.extend(outputs["state_logits"].argmax(dim=-1).cpu().tolist())
    return [str(value) for value in predicted_ids], state_ids, record_indices, gold_ids


def evaluate_model(
    model: Any,
    records: Sequence[Mapping[str, Any]],
    tokenizer: DeterministicVocabulary,
    answer_encoder: StableLabelEncoder,
    state_encoder: StableLabelEncoder,
    operator_vocabulary: Mapping[str, int],
    *,
    batch_size: int = 128,
    device: str = "auto",
    max_length: int | None = None,
    laws: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    require_torch()
    selected_device = _choose_device(device)
    model.to(selected_device)
    dataset = OSLDataset(
        records,
        tokenizer,
        answer_encoder,
        state_encoder,
        operator_vocabulary,
        max_length=max_length or model.config.max_length,
        include_positive=False,
    )
    loader = DataLoader(dataset, batch_size=int(batch_size), shuffle=False, collate_fn=_collate)
    raw_ids, state_ids, order, _ = _predict_loader(model, loader, selected_device)
    integer_predictions = [int(value) for value in raw_ids]
    predictions = answer_encoder.inverse_transform(integer_predictions)
    ordered_records = [records[index] for index in order]
    result: dict[str, Any] = {
        "device": selected_device,
        "n": len(records),
        "record_ids": [str(record.get("id", "")) for record in ordered_records],
        "predictions": predictions,
        "behavior": evaluate_by_split(ordered_records, predictions),
        "length_generalization": length_generalization_metrics(ordered_records, predictions),
        "counterfactual": counterfactual_metrics(ordered_records, predictions),
    }
    if state_ids and model.state_head is not None:
        predicted_states = state_encoder.inverse_transform(state_ids)
        gold_states = [canonical_json(record.get("final_state", {})) for record in ordered_records]
        result["state_exact_accuracy"] = float(
            np.mean([left == right for left, right in zip(gold_states, predicted_states)])
        )
        result["state_predictions"] = [json.loads(value) for value in predicted_states]
    if model.operator_matrices is not None:
        named = {
            name: model.operator_matrices[index].detach().cpu().numpy()
            for name, index in operator_vocabulary.items()
        }
        result["algebra"] = compute_algebra_residuals(named, list(laws or []))
    return result


def train_model(
    train_records: Sequence[Mapping[str, Any]],
    validation_records: Sequence[Mapping[str, Any]],
    output_dir: str | Path,
    config: Mapping[str, Any] | TrainingConfig | None = None,
    *,
    resume: str | Path | None = None,
    device: str = "auto",
    tokenizer_records: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Train a requested arm and write best/last resumable checkpoints."""

    require_torch()
    if not train_records or not validation_records:
        raise ValueError("Nonempty training and validation records are required")
    training_config = config if isinstance(config, TrainingConfig) else TrainingConfig.from_mapping(config)
    requested_arm = training_config.arm
    effective_corpus_ordered_sha256 = _ordered_corpus_digest(train_records)
    selected_device = _choose_device(device)
    set_deterministic_seed(training_config.seed)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resume_payload: dict[str, Any] | None = None
    resume_best_payload: dict[str, Any] | None = None

    if resume is None:
        tokenizer, answers, states, operators = _build_encoders(
            train_records, training_config, tokenizer_records
        )
        model_config = _build_model_config(training_config, tokenizer, answers, states, operators)
        model = OSLTransformer(model_config).to(selected_device)
        initial_model_sha256 = _model_state_digest(model)
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=training_config.learning_rate,
            weight_decay=training_config.weight_decay,
        )
        start_epoch = 0
        global_step = 0
        best_score = -1.0
        best_accuracy = -1.0
        no_improvement = 0
        history: list[dict[str, Any]] = []
        laws = _extract_law_specs(train_records)
    else:
        checkpoint = _load_torch_checkpoint(resume, map_location=selected_device)
        resume_payload = checkpoint
        sibling_best = Path(resume).with_name("checkpoint.pt")
        if sibling_best.is_file() and sibling_best.resolve() != Path(resume).resolve():
            resume_best_payload = _load_torch_checkpoint(
                sibling_best, map_location=selected_device
            )
        else:
            resume_best_payload = checkpoint
        saved_config = TrainingConfig.from_mapping(checkpoint["training_config"])
        if saved_config.arm != requested_arm:
            raise ValueError(
                f"resume checkpoint arm {saved_config.arm!r} does not match requested arm "
                f"{requested_arm!r}"
            )
        saved_corpus_digest = checkpoint.get("effective_corpus_ordered_sha256")
        if (
            saved_corpus_digest is not None
            and str(saved_corpus_digest) != effective_corpus_ordered_sha256
        ):
            raise ValueError(
                "resume dataset does not match the checkpoint's ordered effective corpus"
            )
        if "selection_metric" not in checkpoint.get("training_config", {}):
            saved_config.selection_metric = "accuracy"
        # Epoch count and output destination may change; the experiment definition may not.
        saved_config.epochs = training_config.epochs
        training_config = saved_config
        tokenizer = DeterministicVocabulary.from_dict(checkpoint["tokenizer"])
        answers = StableLabelEncoder.from_dict(checkpoint["answer_encoder"])
        states = StableLabelEncoder.from_dict(checkpoint["state_encoder"])
        operators = {str(key): int(value) for key, value in checkpoint["operator_vocabulary"].items()}
        model = OSLTransformer(ModelConfig.from_dict(checkpoint["model_config"])).to(selected_device)
        model.load_state_dict(checkpoint["model_state"])
        initial_model_sha256 = checkpoint.get("initial_model_sha256")
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=training_config.learning_rate,
            weight_decay=training_config.weight_decay,
        )
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        start_epoch = int(checkpoint["epoch"]) + 1
        global_step = int(checkpoint["global_step"])
        best_score = float(
            checkpoint.get(
                "best_validation_score",
                checkpoint.get("best_validation_accuracy", -1.0),
            )
        )
        best_accuracy = float(checkpoint.get("best_validation_accuracy", -1.0))
        no_improvement = int(checkpoint.get("epochs_without_improvement", 0))
        history = list(checkpoint.get("history", []))
        laws = list(checkpoint.get("laws", []))
        _restore_rng_state(checkpoint.get("rng_state", {}))

    initialization_contract = _initialization_contract(
        model, tokenizer, answers, initial_model_sha256
    )

    include_positive = training_config.arm in {"equivalence_regularized", "combined"}
    train_dataset = OSLDataset(
        train_records,
        tokenizer,
        answers,
        states,
        operators,
        max_length=training_config.max_length,
        include_positive=include_positive,
    )
    validation_dataset = OSLDataset(
        validation_records,
        tokenizer,
        answers,
        states,
        operators,
        max_length=training_config.max_length,
        include_positive=False,
    )
    validation_loader = DataLoader(
        validation_dataset,
        batch_size=training_config.batch_size,
        shuffle=False,
        collate_fn=_collate,
        num_workers=training_config.num_workers,
    )
    scaler = _grad_scaler(selected_device, training_config.amp)
    best_checkpoint = output / "checkpoint.pt"
    last_checkpoint = output / "last_checkpoint.pt"
    final_epoch = start_epoch - 1
    if resume_payload is not None:
        # Seed the new destination before continuing. A no-op resume remains
        # valid, and the previous best survives if no later epoch improves it.
        _atomic_torch_save(resume_payload, last_checkpoint)
        _atomic_torch_save(resume_best_payload or resume_payload, best_checkpoint)

    for epoch in range(start_epoch, training_config.epochs):
        final_epoch = epoch
        generator = torch.Generator()
        generator.manual_seed(training_config.seed + epoch)
        train_loader = DataLoader(
            train_dataset,
            batch_size=training_config.batch_size,
            shuffle=True,
            generator=generator,
            collate_fn=_collate,
            num_workers=training_config.num_workers,
        )
        model.train()
        epoch_totals: dict[str, float] = {}
        examples_seen = 0
        for raw_batch in train_loader:
            batch = _move_batch(raw_batch, selected_device)
            optimizer.zero_grad(set_to_none=True)
            with _autocast_context(selected_device, training_config.amp):
                outputs = model(
                    batch["input_ids"],
                    batch["attention_mask"],
                    batch["token_type_ids"],
                    batch["program_ids"] if model.operator_matrices is not None else None,
                    batch["program_mask"] if model.operator_matrices is not None else None,
                )
                components = _loss_components(
                    model, batch, outputs, training_config, laws, operators
                )
                loss = _weighted_loss(components, training_config.loss_weights)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), training_config.gradient_clip)
            scaler.step(optimizer)
            scaler.update()
            batch_size = int(batch["input_ids"].shape[0])
            examples_seen += batch_size
            epoch_totals["total"] = epoch_totals.get("total", 0.0) + float(loss.detach()) * batch_size
            for name, value in components.items():
                epoch_totals[name] = epoch_totals.get(name, 0.0) + float(value.detach()) * batch_size
            global_step += 1

        raw_ids, _, order, _ = _predict_loader(model, validation_loader, selected_device)
        validation_predictions = answers.inverse_transform(int(value) for value in raw_ids)
        ordered_validation = [validation_records[index] for index in order]
        validation_behavior = evaluate_by_split(ordered_validation, validation_predictions)
        validation_accuracy = float(validation_behavior["overall"]["accuracy"])
        validation_macro_f1 = float(validation_behavior["overall"]["macro_f1"])
        validation_score = _validation_selection_score(
            validation_behavior, training_config.selection_metric
        )
        epoch_record = {
            "epoch": epoch,
            "global_step": global_step,
            "train_losses": {
                key: value / max(examples_seen, 1) for key, value in sorted(epoch_totals.items())
            },
            "validation_accuracy": validation_accuracy,
            "validation_macro_f1": validation_macro_f1,
            "validation_selection_metric": training_config.selection_metric,
            "validation_selection_score": validation_score,
        }
        history.append(epoch_record)
        print(
            json.dumps(
                {
                    "event": "training_epoch",
                    "arm": training_config.arm,
                    "epoch": epoch + 1,
                    "epochs_requested": training_config.epochs,
                    "global_step": global_step,
                    "train_total_loss": epoch_record["train_losses"].get("total"),
                    "validation_accuracy": validation_accuracy,
                    "validation_macro_f1": validation_macro_f1,
                    "validation_selection_metric": training_config.selection_metric,
                    "validation_selection_score": validation_score,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        improved = validation_score > best_score + 1e-12
        if improved:
            best_score = validation_score
            best_accuracy = validation_accuracy
            no_improvement = 0
        else:
            no_improvement += 1
        payload = _checkpoint_payload(
            model=model,
            optimizer=optimizer,
            epoch=epoch,
            global_step=global_step,
            best_validation_accuracy=best_accuracy,
            best_validation_score=best_score,
            epochs_without_improvement=no_improvement,
            training_config=training_config,
            tokenizer=tokenizer,
            answer_encoder=answers,
            state_encoder=states,
            operator_vocabulary=operators,
            laws=laws,
            history=history,
            initial_model_sha256=initial_model_sha256,
            initialization_contract=initialization_contract,
            effective_corpus_ordered_sha256=effective_corpus_ordered_sha256,
        )
        _atomic_torch_save(payload, last_checkpoint)
        if improved:
            _atomic_torch_save(payload, best_checkpoint)
        if no_improvement >= training_config.early_stopping_patience:
            break

    if not last_checkpoint.exists():
        # A resume target may already have completed the requested epoch range.
        payload = _checkpoint_payload(
            model=model,
            optimizer=optimizer,
            epoch=final_epoch,
            global_step=global_step,
            best_validation_accuracy=best_accuracy,
            best_validation_score=best_score,
            epochs_without_improvement=no_improvement,
            training_config=training_config,
            tokenizer=tokenizer,
            answer_encoder=answers,
            state_encoder=states,
            operator_vocabulary=operators,
            laws=laws,
            history=history,
            initial_model_sha256=initial_model_sha256,
            initialization_contract=initialization_contract,
            effective_corpus_ordered_sha256=effective_corpus_ordered_sha256,
        )
        _atomic_torch_save(payload, last_checkpoint)
    if not best_checkpoint.exists():
        _atomic_torch_save(_load_torch_checkpoint(last_checkpoint), best_checkpoint)
    best = _load_torch_checkpoint(best_checkpoint, map_location=selected_device)
    model.load_state_dict(best["model_state"])
    validation_result = evaluate_model(
        model,
        validation_records,
        tokenizer,
        answers,
        states,
        operators,
        batch_size=training_config.batch_size,
        device=selected_device,
        max_length=training_config.max_length,
        laws=laws,
    )
    # Predictions make a summary unnecessarily large; checkpoint evaluation can recreate them.
    validation_result.pop("record_ids", None)
    validation_result.pop("predictions", None)
    validation_result.pop("state_predictions", None)
    summary = {
        "arm": training_config.arm,
        "model_seed": int(training_config.seed),
        "device": selected_device,
        "epochs_completed": len(history),
        "global_step": global_step,
        "best_validation_accuracy": best_accuracy,
        "best_validation_score": best_score,
        "selection_metric": training_config.selection_metric,
        "initial_model_sha256": initial_model_sha256,
        "initialization_contract": initialization_contract,
        "effective_corpus": _effective_corpus_summary(train_records, tokenizer),
        "checkpoint": str(best_checkpoint.resolve()),
        "last_checkpoint": str(last_checkpoint.resolve()),
        "vocabulary_size": len(tokenizer),
        "hash_buckets": tokenizer.hash_buckets,
        "answer_classes": answers.labels,
        "state_classes": len(states),
        "operator_vocabulary": operators,
        "laws": laws,
        "loss_components": [
            "answer",
            *(["state"] if training_config.arm in {"state_supervised", "combined"} else []),
            *(
                ["equivalence"]
                if training_config.arm in {"equivalence_regularized", "combined"}
                else []
            ),
            *(
                ["operator_alignment", "operator_laws"]
                if training_config.arm in {"operator_regularized", "combined"}
                else []
            ),
        ],
        "checkpoint_metadata": {
            "format_version": int(best.get("format_version", 1)),
            "epoch": int(best["epoch"]),
            "global_step": int(best["global_step"]),
            "selection_metric": str(
                best.get("selection_metric", training_config.selection_metric)
            ),
            "best_validation_score": float(
                best.get("best_validation_score", best.get("best_validation_accuracy", -1.0))
            ),
            "model_config": dict(best["model_config"]),
        },
        "history": history,
        "validation": validation_result,
    }
    (output / "training_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    return summary


def train_from_jsonl(
    train_path: str | Path,
    validation_path: str | Path,
    output_dir: str | Path,
    config: Mapping[str, Any] | TrainingConfig | None = None,
    *,
    resume: str | Path | None = None,
    device: str = "auto",
) -> dict[str, Any]:
    return train_from_jsonl_files(
        [train_path],
        validation_path,
        output_dir,
        config,
        resume=resume,
        device=device,
    )


def train_from_jsonl_files(
    train_paths: Sequence[str | Path],
    validation_path: str | Path,
    output_dir: str | Path,
    config: Mapping[str, Any] | TrainingConfig | None = None,
    *,
    resume: str | Path | None = None,
    device: str = "auto",
    tokenizer_paths: Sequence[str | Path] | None = None,
) -> dict[str, Any]:
    """Train from one or more deterministic JSONL shards.

    Multiple shards are used by the answer-supervised role-binding arm.  The
    order supplied by the caller is preserved so the effective corpus remains
    reproducible and independently hashable.
    """

    if not train_paths:
        raise ValueError("at least one training shard is required")
    train_records: list[dict[str, Any]] = []
    for path in train_paths:
        train_records.extend(_read_jsonl(path))
    tokenizer_records: list[dict[str, Any]] | None = None
    if tokenizer_paths is not None:
        tokenizer_records = []
        for path in tokenizer_paths:
            tokenizer_records.extend(_read_jsonl(path))
    return train_model(
        train_records,
        _read_jsonl(validation_path),
        output_dir,
        config,
        resume=resume,
        device=device,
        tokenizer_records=tokenizer_records,
    )


def train_from_jsonl_replacement(
    base_path: str | Path,
    augmentation_path: str | Path,
    validation_path: str | Path,
    output_dir: str | Path,
    config: Mapping[str, Any] | TrainingConfig | None = None,
    *,
    resume: str | Path | None = None,
    device: str = "auto",
    tokenizer_paths: Sequence[str | Path] | None = None,
) -> dict[str, Any]:
    """Replace a deterministic subset of base examples with augmentation.

    The resulting corpus has exactly the same record count as the base corpus,
    preventing a training-volume confound when comparing role-binding
    augmentation with the untouched answer-only arm.
    """

    base_records = _read_jsonl(base_path)
    augmentation_records = _read_jsonl(augmentation_path)
    if not augmentation_records:
        raise ValueError("the replacement augmentation shard is empty")
    if len(augmentation_records) >= len(base_records):
        raise ValueError("replacement augmentation must be smaller than the base corpus")
    retained = len(base_records) - len(augmentation_records)
    deterministic_base = sorted(base_records, key=lambda record: str(record.get("id", "")))
    effective_records = deterministic_base[:retained] + augmentation_records
    tokenizer_records: list[dict[str, Any]] | None = None
    if tokenizer_paths is not None:
        tokenizer_records = []
        for path in tokenizer_paths:
            tokenizer_records.extend(_read_jsonl(path))
    result = train_model(
        effective_records,
        _read_jsonl(validation_path),
        output_dir,
        config,
        resume=resume,
        device=device,
        tokenizer_records=tokenizer_records,
    )
    result["mixture"] = {
        "policy": "deterministic_replacement",
        "base_records_available": len(base_records),
        "base_records_retained": retained,
        "augmentation_records": len(augmentation_records),
        "effective_training_records": len(effective_records),
    }
    return result


def evaluate_checkpoint(
    checkpoint_path: str | Path,
    data_path: str | Path,
    *,
    output_path: str | Path | None = None,
    batch_size: int = 128,
    device: str = "auto",
) -> dict[str, Any]:
    """Load a portable checkpoint and evaluate every declared data split."""

    require_torch()
    selected_device = _choose_device(device)
    checkpoint = _load_torch_checkpoint(checkpoint_path, map_location=selected_device)
    tokenizer = DeterministicVocabulary.from_dict(checkpoint["tokenizer"])
    answers = StableLabelEncoder.from_dict(checkpoint["answer_encoder"])
    states = StableLabelEncoder.from_dict(checkpoint["state_encoder"])
    operators = {str(key): int(value) for key, value in checkpoint["operator_vocabulary"].items()}
    model = OSLTransformer(ModelConfig.from_dict(checkpoint["model_config"])
    ).to(selected_device)
    model.load_state_dict(checkpoint["model_state"])
    records = _read_jsonl(data_path)
    result = evaluate_model(
        model,
        records,
        tokenizer,
        answers,
        states,
        operators,
        batch_size=batch_size,
        device=selected_device,
        laws=checkpoint.get("laws", []),
    )
    result["checkpoint"] = str(Path(checkpoint_path).resolve())
    if output_path is not None:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
