from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError as error:  # pragma: no cover - exercised by Windows preflight
    raise ImportError("PyTorch is required for model training. Install torch in the selected Python.") from error


@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int = 260
    d_model: int = 128
    n_layers: int = 4
    n_heads: int = 4
    ff_multiplier: int = 4
    max_seq_len: int = 192
    dropout: float = 0.0
    rope_base: float = 10000.0
    tie_embeddings: bool = True

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ModelConfig":
        config = cls(**value)
        integer_fields = (
            "vocab_size",
            "d_model",
            "n_layers",
            "n_heads",
            "ff_multiplier",
            "max_seq_len",
        )
        if any(type(getattr(config, name)) is not int for name in integer_fields):
            raise ValueError("model sizes must be integers")
        if config.vocab_size <= 0:
            raise ValueError("vocab_size must be positive")
        if (
            config.d_model <= 0
            or config.n_layers <= 0
            or config.n_heads <= 0
            or config.ff_multiplier <= 0
        ):
            raise ValueError("model dimensions and ff_multiplier must be positive")
        if config.d_model % config.n_heads:
            raise ValueError("d_model must be divisible by n_heads")
        if (config.d_model // config.n_heads) % 2:
            raise ValueError("attention head dimension must be even for RoPE")
        if config.max_seq_len < 8:
            raise ValueError("max_seq_len is too small")
        if (
            isinstance(config.dropout, bool)
            or not isinstance(config.dropout, (int, float))
            or not math.isfinite(float(config.dropout))
            or not 0 <= config.dropout < 1
        ):
            raise ValueError("dropout must be in [0, 1)")
        if (
            isinstance(config.rope_base, bool)
            or not isinstance(config.rope_base, (int, float))
            or not math.isfinite(float(config.rope_base))
            or config.rope_base <= 0
        ):
            raise ValueError("rope_base must be finite and positive")
        if type(config.tie_embeddings) is not bool:
            raise ValueError("tie_embeddings must be boolean")
        return config

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _apply_rope(
    tensor: "torch.Tensor", cos: "torch.Tensor", sin: "torch.Tensor"
) -> "torch.Tensor":
    even = tensor[..., 0::2]
    odd = tensor[..., 1::2]
    rotated_even = even * cos - odd * sin
    rotated_odd = even * sin + odd * cos
    return torch.stack((rotated_even, rotated_odd), dim=-1).flatten(-2)


class CausalSelfAttention(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.n_heads = config.n_heads
        self.head_dim = config.d_model // config.n_heads
        self.dropout = config.dropout
        self.qkv = nn.Linear(config.d_model, 3 * config.d_model, bias=False)
        self.proj = nn.Linear(config.d_model, config.d_model, bias=False)

    def forward(
        self,
        x: "torch.Tensor",
        rope_cos: "torch.Tensor",
        rope_sin: "torch.Tensor",
    ) -> "torch.Tensor":
        batch, length, width = x.shape
        qkv = self.qkv(x).view(batch, length, 3, self.n_heads, self.head_dim)
        query, key, value = qkv.unbind(dim=2)
        query = query.transpose(1, 2)
        key = key.transpose(1, 2)
        value = value.transpose(1, 2)
        rope_cos = rope_cos.to(dtype=query.dtype)
        rope_sin = rope_sin.to(dtype=query.dtype)
        query = _apply_rope(query, rope_cos, rope_sin)
        key = _apply_rope(key, rope_cos, rope_sin)
        attention = F.scaled_dot_product_attention(
            query,
            key,
            value,
            dropout_p=self.dropout if self.training else 0.0,
            is_causal=True,
        )
        merged = attention.transpose(1, 2).contiguous().view(batch, length, width)
        return self.proj(merged)


class DecoderBlock(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.attention_norm = nn.LayerNorm(config.d_model)
        self.attention = CausalSelfAttention(config)
        self.mlp_norm = nn.LayerNorm(config.d_model)
        hidden = config.d_model * config.ff_multiplier
        self.mlp = nn.Sequential(
            nn.Linear(config.d_model, hidden, bias=False),
            nn.GELU(),
            nn.Linear(hidden, config.d_model, bias=False),
        )
        self.dropout = nn.Dropout(config.dropout)

    def forward(
        self,
        x: "torch.Tensor",
        rope_cos: "torch.Tensor",
        rope_sin: "torch.Tensor",
    ) -> "torch.Tensor":
        x = x + self.dropout(
            self.attention(self.attention_norm(x), rope_cos, rope_sin)
        )
        return x + self.dropout(self.mlp(self.mlp_norm(x)))


class TinyDecoderLM(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.blocks = nn.ModuleList([DecoderBlock(config) for _ in range(config.n_layers)])
        self.final_norm = nn.LayerNorm(config.d_model)
        self.output = (
            None
            if config.tie_embeddings
            else nn.Linear(config.d_model, config.vocab_size, bias=False)
        )
        head_dim = config.d_model // config.n_heads
        frequencies = 1.0 / (
            config.rope_base
            ** (
                torch.arange(0, head_dim, 2, dtype=torch.float32)
                / head_dim
            )
        )
        angles = torch.outer(
            torch.arange(config.max_seq_len, dtype=torch.float32), frequencies
        )
        self.register_buffer("_rope_cos", angles.cos(), persistent=False)
        self.register_buffer("_rope_sin", angles.sin(), persistent=False)
        self.apply(self._initialize)
        for block in self.blocks:
            nn.init.normal_(
                block.attention.proj.weight,
                mean=0.0,
                std=0.02 / math.sqrt(2 * config.n_layers),
            )
            nn.init.normal_(
                block.mlp[-1].weight,
                mean=0.0,
                std=0.02 / math.sqrt(2 * config.n_layers),
            )

    @staticmethod
    def _initialize(module: nn.Module) -> None:
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)

    def _logits(self, hidden: "torch.Tensor") -> "torch.Tensor":
        normalized = self.final_norm(hidden)
        if self.output is None:
            return F.linear(normalized, self.token_embedding.weight)
        return self.output(normalized)

    def forward(
        self,
        input_ids: "torch.Tensor",
        return_hidden_states: bool = False,
    ) -> "torch.Tensor | tuple[torch.Tensor, list[torch.Tensor]]":
        if input_ids.ndim != 2:
            raise ValueError("input_ids must have shape [batch, sequence]")
        if input_ids.shape[1] > self.config.max_seq_len:
            raise ValueError(
                f"sequence length {input_ids.shape[1]} exceeds model limit {self.config.max_seq_len}"
            )
        hidden = self.token_embedding(input_ids)
        return self.forward_embeddings(hidden, return_hidden_states=return_hidden_states)

    def forward_embeddings(
        self,
        embeddings: "torch.Tensor",
        return_hidden_states: bool = False,
    ) -> "torch.Tensor | tuple[torch.Tensor, list[torch.Tensor]]":
        if embeddings.ndim != 3 or embeddings.shape[-1] != self.config.d_model:
            raise ValueError("embeddings must have shape [batch, sequence, d_model]")
        if embeddings.shape[1] > self.config.max_seq_len:
            raise ValueError(
                f"sequence length {embeddings.shape[1]} exceeds model limit "
                f"{self.config.max_seq_len}"
            )
        hidden = embeddings
        length = embeddings.shape[1]
        rope_cos = self._rope_cos[:length].to(dtype=hidden.dtype)[None, None, :, :]
        rope_sin = self._rope_sin[:length].to(dtype=hidden.dtype)[None, None, :, :]
        states = [hidden] if return_hidden_states else []
        for block in self.blocks:
            hidden = block(hidden, rope_cos, rope_sin)
            if return_hidden_states:
                states.append(hidden)
        logits = self._logits(hidden)
        return (logits, states) if return_hidden_states else logits

    def continue_from_hidden(
        self,
        hidden: "torch.Tensor",
        completed_layers: int,
    ) -> "torch.Tensor":
        if not 0 <= completed_layers <= len(self.blocks):
            raise ValueError("completed_layers outside model")
        length = hidden.shape[1]
        rope_cos = self._rope_cos[:length].to(dtype=hidden.dtype)[None, None, :, :]
        rope_sin = self._rope_sin[:length].to(dtype=hidden.dtype)[None, None, :, :]
        for block in self.blocks[completed_layers:]:
            hidden = block(hidden, rope_cos, rope_sin)
        return self._logits(hidden)

    @torch.no_grad()
    def generate(
        self,
        prefix_ids: list[int],
        eos_id: int,
        max_new_tokens: int,
        device: "torch.device",
    ) -> list[int]:
        sequence = list(map(int, prefix_ids))
        generated: list[int] = []
        for _ in range(max_new_tokens):
            # A context exactly at max_seq_len can still predict one final token.
            # Stop only after that prediction has extended the stored sequence.
            if len(sequence) > self.config.max_seq_len:
                break
            inputs = torch.tensor([sequence], dtype=torch.long, device=device)
            logits = self(inputs)
            token = int(logits[0, -1].argmax().item())
            generated.append(token)
            sequence.append(token)
            if token == eos_id:
                break
        return generated

    @torch.no_grad()
    def generate_batch(
        self,
        prefix_ids: list[list[int]],
        eos_id: int,
        max_new_tokens: list[int],
        device: "torch.device",
    ) -> list[list[int]]:
        """Greedily generate equal-prefix-length rows without padding leakage."""
        if not prefix_ids or len(prefix_ids) != len(max_new_tokens):
            raise ValueError("prefix_ids and max_new_tokens must be nonempty and aligned")
        lengths = {len(prefix) for prefix in prefix_ids}
        if len(lengths) != 1:
            raise ValueError("batched generation requires equal prefix lengths")
        if any(budget <= 0 for budget in max_new_tokens):
            raise ValueError("generation budgets must be positive")
        prefix_length = next(iter(lengths))
        if any(prefix_length + budget - 1 > self.config.max_seq_len for budget in max_new_tokens):
            raise ValueError("a batched generation budget exceeds model context")

        sequences = [list(map(int, prefix)) for prefix in prefix_ids]
        generated: list[list[int]] = [[] for _ in sequences]
        finished = [False for _ in sequences]
        for _ in range(max(max_new_tokens)):
            inputs = torch.tensor(sequences, dtype=torch.long, device=device)
            logits = self(inputs)
            next_tokens = logits[:, -1].argmax(dim=-1).tolist()
            for row, token_value in enumerate(next_tokens):
                if finished[row] or len(generated[row]) >= max_new_tokens[row]:
                    token = eos_id
                    finished[row] = True
                else:
                    token = int(token_value)
                    generated[row].append(token)
                    if token == eos_id:
                        finished[row] = True
                sequences[row].append(token)
            if all(finished):
                break
        return generated
