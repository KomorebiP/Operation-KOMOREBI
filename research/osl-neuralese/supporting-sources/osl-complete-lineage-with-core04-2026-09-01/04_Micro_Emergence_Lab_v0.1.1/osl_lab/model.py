"""Deterministic text encoding and a compact transformer for Micro OSL.

The module is intentionally importable without PyTorch.  Corpus generation,
baselines, and NumPy analyses remain usable in a lightweight environment.  A
clear error is raised only when a neural component is instantiated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
import re
from collections import Counter
from typing import Any, Iterable, Mapping, Sequence


try:  # pragma: no cover - availability depends on the offline environment
    import torch
    from torch import Tensor, nn

    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover - exercised in lightweight CI
    torch = None  # type: ignore[assignment]
    Tensor = Any  # type: ignore[misc,assignment]
    nn = None  # type: ignore[assignment]
    TORCH_AVAILABLE = False


TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\w\s]", re.UNICODE)


def require_torch() -> None:
    """Raise an actionable error if neural training dependencies are absent."""

    if not TORCH_AVAILABLE:
        raise RuntimeError(
            "PyTorch is required for neural training. Install the CPU or CUDA "
            "build listed in the offline lab README, then rerun this command."
        )


def canonical_json(value: Any) -> str:
    """Return a stable, compact representation suitable for categorical labels."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class DeterministicVocabulary:
    """A serializable vocabulary whose construction is independent of hash order."""

    SPECIAL_TOKENS = ("[PAD]", "[UNK]", "[CLS]", "[SEP]")

    def __init__(
        self,
        tokens: Sequence[str] | None = None,
        *,
        lowercase: bool = True,
        min_frequency: int = 1,
        max_size: int | None = None,
        hash_buckets: int = 0,
    ) -> None:
        self.lowercase = bool(lowercase)
        self.min_frequency = int(min_frequency)
        self.max_size = None if max_size is None else int(max_size)
        self.hash_buckets = int(hash_buckets)
        if self.hash_buckets < 0:
            raise ValueError("hash_buckets must be nonnegative")
        ordered = list(self.SPECIAL_TOKENS)
        if tokens:
            for token in tokens:
                if token not in ordered:
                    ordered.append(str(token))
        self.id_to_token = ordered
        self.token_to_id = {token: index for index, token in enumerate(ordered)}

    @property
    def pad_id(self) -> int:
        return self.token_to_id["[PAD]"]

    @property
    def unk_id(self) -> int:
        return self.token_to_id["[UNK]"]

    @property
    def cls_id(self) -> int:
        return self.token_to_id["[CLS]"]

    @property
    def sep_id(self) -> int:
        return self.token_to_id["[SEP]"]

    def __len__(self) -> int:
        return len(self.id_to_token)

    def tokenize(self, text: str) -> list[str]:
        text = str(text)
        if self.lowercase:
            text = text.lower()
        return TOKEN_PATTERN.findall(text)

    def fit(self, texts: Iterable[str]) -> "DeterministicVocabulary":
        counts: Counter[str] = Counter()
        for text in texts:
            counts.update(self.tokenize(text))
        candidates = [
            (token, count)
            for token, count in counts.items()
            if count >= self.min_frequency and token not in self.SPECIAL_TOKENS
        ]
        candidates.sort(key=lambda item: (-item[1], item[0]))
        if self.max_size is not None:
            room = max(0, self.max_size - len(self.SPECIAL_TOKENS))
            candidates = candidates[:room]
        self.id_to_token = list(self.SPECIAL_TOKENS) + [token for token, _ in candidates]
        self.id_to_token.extend(
            f"[HASH_{index:04d}]" for index in range(self.hash_buckets)
        )
        self.token_to_id = {token: index for index, token in enumerate(self.id_to_token)}
        return self

    def encode_tokens(self, tokens: Sequence[str]) -> list[int]:
        encoded: list[int] = []
        for token in tokens:
            if self.hash_buckets and re.fullmatch(r"[A-Za-z]+(?:'[A-Za-z]+)?", token):
                digest = int.from_bytes(sha256(token.encode("utf-8")).digest()[:8], "big")
                bucket = digest % self.hash_buckets
                encoded.append(self.token_to_id[f"[HASH_{bucket:04d}]"])
            else:
                encoded.append(self.token_to_id.get(token, self.unk_id))
        return encoded

    def encode_pair(
        self,
        story: str,
        question: str,
        *,
        max_length: int = 256,
    ) -> dict[str, list[int]]:
        """Encode ``[CLS] story [SEP] question [SEP]`` with stable truncation.

        Truncation removes tokens from the longer segment first, preserving both
        the story and the query even for unusually long generated examples.
        """

        if max_length < 5:
            raise ValueError("max_length must be at least 5")
        story_tokens = self.tokenize(story)
        question_tokens = self.tokenize(question)
        budget = max_length - 3
        while len(story_tokens) + len(question_tokens) > budget:
            if len(story_tokens) > len(question_tokens):
                story_tokens.pop()
            else:
                question_tokens.pop()
        tokens = ["[CLS]", *story_tokens, "[SEP]", *question_tokens, "[SEP]"]
        token_types = [0] * (len(story_tokens) + 2) + [1] * (len(question_tokens) + 1)
        input_ids = self.encode_tokens(tokens)
        attention_mask = [1] * len(input_ids)
        padding = max_length - len(input_ids)
        if padding:
            input_ids.extend([self.pad_id] * padding)
            attention_mask.extend([0] * padding)
            token_types.extend([0] * padding)
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_types,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "tokens": self.id_to_token[len(self.SPECIAL_TOKENS) :],
            "lowercase": self.lowercase,
            "min_frequency": self.min_frequency,
            "max_size": self.max_size,
            "hash_buckets": self.hash_buckets,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "DeterministicVocabulary":
        return cls(
            list(payload.get("tokens", [])),
            lowercase=bool(payload.get("lowercase", True)),
            min_frequency=int(payload.get("min_frequency", 1)),
            max_size=payload.get("max_size"),
            hash_buckets=int(payload.get("hash_buckets", 0)),
        )


class StableLabelEncoder:
    """A minimal deterministic categorical encoder with JSON serialization."""

    def __init__(self, labels: Sequence[str] | None = None) -> None:
        self.labels = sorted({str(label) for label in labels or []})
        self.label_to_id = {label: index for index, label in enumerate(self.labels)}

    def fit(self, labels: Iterable[str]) -> "StableLabelEncoder":
        self.labels = sorted({str(label) for label in labels})
        self.label_to_id = {label: index for index, label in enumerate(self.labels)}
        return self

    def __len__(self) -> int:
        return len(self.labels)

    def transform(self, labels: Iterable[str]) -> list[int]:
        result = []
        for label in labels:
            key = str(label)
            if key not in self.label_to_id:
                raise KeyError(f"Unknown label: {key!r}")
            result.append(self.label_to_id[key])
        return result

    def inverse_transform(self, indices: Iterable[int]) -> list[str]:
        return [self.labels[int(index)] for index in indices]

    def to_dict(self) -> dict[str, Any]:
        return {"labels": list(self.labels)}

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "StableLabelEncoder":
        return cls(list(payload.get("labels", [])))


def extract_operator_name(event: Any) -> str:
    """Extract the primitive name from the supported program encodings."""

    if isinstance(event, str):
        return event
    if isinstance(event, Mapping):
        for key in ("op", "operator", "name", "type"):
            if key in event:
                return str(event[key])
    raise ValueError(f"Cannot extract an operator name from {event!r}")


def build_operator_vocabulary(records: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    names: set[str] = set()
    for record in records:
        for event in record.get("program", []) or []:
            names.add(extract_operator_name(event))
    return {name: index for index, name in enumerate(sorted(names))}


@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int
    num_answers: int
    num_states: int = 0
    num_operators: int = 0
    max_length: int = 256
    d_model: int = 192
    n_heads: int = 6
    n_layers: int = 4
    d_ff: int = 512
    dropout: float = 0.1
    representation_dim: int = 96
    operator_dim: int = 16
    arm: str = "answer_only"

    def __post_init__(self) -> None:
        allowed = {
            "answer_only",
            "role_bind_augmented",
            "role_bind_scrambled",
            "state_supervised",
            "equivalence_regularized",
            "operator_regularized",
            "combined",
        }
        if self.arm not in allowed:
            raise ValueError(f"Unknown training arm {self.arm!r}; choose one of {sorted(allowed)}")
        if self.d_model % self.n_heads:
            raise ValueError("d_model must be divisible by n_heads")
        if self.max_length < 5 or self.num_answers < 1 or self.vocab_size < 4:
            raise ValueError("Invalid vocabulary, answer, or sequence dimensions")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ModelConfig":
        fields = cls.__dataclass_fields__
        return cls(**{key: value for key, value in payload.items() if key in fields})


if TORCH_AVAILABLE:

    class OSLTransformer(nn.Module):
        """Small encoder with optional state, quotient, and operator objectives."""

        def __init__(self, config: ModelConfig) -> None:
            super().__init__()
            self.config = config
            self.token_embedding = nn.Embedding(config.vocab_size, config.d_model, padding_idx=0)
            self.position_embedding = nn.Embedding(config.max_length, config.d_model)
            self.type_embedding = nn.Embedding(2, config.d_model)
            self.input_norm = nn.LayerNorm(config.d_model)
            self.dropout = nn.Dropout(config.dropout)
            layer = nn.TransformerEncoderLayer(
                d_model=config.d_model,
                nhead=config.n_heads,
                dim_feedforward=config.d_ff,
                dropout=config.dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.encoder = nn.TransformerEncoder(layer, num_layers=config.n_layers)
            self.output_norm = nn.LayerNorm(config.d_model)
            self.answer_head = nn.Linear(config.d_model, config.num_answers)
            self.state_head = (
                nn.Linear(config.d_model, config.num_states) if config.num_states > 0 else None
            )
            self.representation_head = nn.Sequential(
                nn.Linear(config.d_model, config.representation_dim),
                nn.GELU(),
                nn.LayerNorm(config.representation_dim),
            )
            if config.num_operators > 0:
                identity = torch.eye(config.operator_dim).repeat(config.num_operators, 1, 1)
                identity += 0.01 * torch.randn_like(identity)
                self.operator_matrices = nn.Parameter(identity)
                self.program_projection = nn.Sequential(
                    nn.Linear(config.operator_dim * config.operator_dim, config.d_model),
                    nn.GELU(),
                    nn.LayerNorm(config.d_model),
                )
            else:
                self.register_parameter("operator_matrices", None)
                self.program_projection = None
            self.reset_parameters()

        def reset_parameters(self) -> None:
            nn.init.normal_(self.token_embedding.weight, mean=0.0, std=0.02)
            nn.init.normal_(self.position_embedding.weight, mean=0.0, std=0.02)
            nn.init.normal_(self.type_embedding.weight, mean=0.0, std=0.02)
            with torch.no_grad():
                self.token_embedding.weight[0].zero_()
            for head in (self.answer_head, self.state_head):
                if head is not None:
                    nn.init.xavier_uniform_(head.weight)
                    nn.init.zeros_(head.bias)

        def encode(
            self,
            input_ids: Tensor,
            attention_mask: Tensor,
            token_type_ids: Tensor | None = None,
        ) -> Tensor:
            batch_size, length = input_ids.shape
            if length > self.config.max_length:
                raise ValueError(
                    f"Sequence length {length} exceeds configured maximum {self.config.max_length}"
                )
            positions = torch.arange(length, device=input_ids.device).unsqueeze(0)
            if token_type_ids is None:
                token_type_ids = torch.zeros_like(input_ids)
            hidden = (
                self.token_embedding(input_ids)
                + self.position_embedding(positions)
                + self.type_embedding(token_type_ids)
            )
            hidden = self.dropout(self.input_norm(hidden))
            hidden = self.encoder(hidden, src_key_padding_mask=~attention_mask.bool())
            return self.output_norm(hidden[:, 0])

        def compose_programs(self, program_ids: Tensor, program_mask: Tensor) -> tuple[Tensor, Tensor]:
            if self.operator_matrices is None or self.program_projection is None:
                raise RuntimeError("Operator matrices were not enabled in this model")
            batch, length = program_ids.shape
            dim = self.config.operator_dim
            composed = torch.eye(dim, device=program_ids.device, dtype=self.operator_matrices.dtype)
            composed = composed.unsqueeze(0).repeat(batch, 1, 1)
            for position in range(length):
                indices = program_ids[:, position].clamp_min(0)
                matrices = self.operator_matrices[indices]
                candidate = torch.bmm(matrices, composed)
                active = program_mask[:, position].view(batch, 1, 1).bool()
                composed = torch.where(active, candidate, composed)
            projected = self.program_projection(composed.flatten(start_dim=1))
            return composed, projected

        def forward(
            self,
            input_ids: Tensor,
            attention_mask: Tensor,
            token_type_ids: Tensor | None = None,
            program_ids: Tensor | None = None,
            program_mask: Tensor | None = None,
        ) -> dict[str, Tensor | None]:
            pooled = self.encode(input_ids, attention_mask, token_type_ids)
            result: dict[str, Tensor | None] = {
                "answer_logits": self.answer_head(pooled),
                "state_logits": self.state_head(pooled) if self.state_head is not None else None,
                "representation": self.representation_head(pooled),
                "pooled": pooled,
                "program_matrix": None,
                "program_representation": None,
            }
            if program_ids is not None and program_mask is not None and self.operator_matrices is not None:
                matrix, program_representation = self.compose_programs(program_ids, program_mask)
                result["program_matrix"] = matrix
                result["program_representation"] = program_representation
            return result

        @torch.no_grad()
        def operator_matrices_numpy(self) -> Any:
            if self.operator_matrices is None:
                return None
            return self.operator_matrices.detach().cpu().numpy().copy()

else:

    class OSLTransformer:  # type: ignore[no-redef]
        """Placeholder that keeps non-neural commands importable without PyTorch."""

        def __init__(self, config: ModelConfig) -> None:
            require_torch()


def text_from_record(record: Mapping[str, Any]) -> str:
    """Canonical text used to fit the vocabulary and classical baselines."""

    return f"{record.get('story', '')} [QUESTION] {record.get('question', '')}"
