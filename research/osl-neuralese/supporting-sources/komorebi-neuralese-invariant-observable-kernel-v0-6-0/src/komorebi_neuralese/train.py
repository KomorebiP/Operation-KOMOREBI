from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from .algebra import D4_RELATIONS
from .data import EpisodeGenerator
from .models import RecurrentOperatorModel, parameter_count


@dataclass(frozen=True)
class TrainConfig:
    model_name: str
    regime: str
    seed: int
    steps: int
    batch_size: int
    train_max_length: int
    max_eval_length: int
    learning_rate: float
    weight_decay: float = 1e-6
    grad_clip: float = 5.0
    relation_weight: float = 0.15
    relation_hidden_weight: float = 0.05
    intermediate_weight: float = 0.50
    device: str = "cpu"


@dataclass
class TrainedArm:
    config: TrainConfig
    model: nn.Module
    trajectory: list[dict[str, Any]]
    elapsed_seconds: float
    final_loss: float
    parameter_count: int


def _relation_loss(
    model: RecurrentOperatorModel,
    tables: torch.Tensor,
    start: torch.Tensor,
    canonical_to_slot: torch.Tensor,
    hidden_weight: float,
) -> torch.Tensor:
    total = torch.zeros((), device=start.device)
    for word in D4_RELATIONS.values():
        slots = EpisodeGenerator.slots_for_word(canonical_to_slot, word)
        trace = model.run(tables, slots, start)
        endpoint = F.cross_entropy(trace.logits, start)
        h0 = trace.hidden[0]
        h1 = trace.hidden[-1]
        scale = h0.square().mean().detach().clamp_min(1e-6)
        hidden = (h1 - h0).square().mean() / scale
        total = total + endpoint + hidden_weight * hidden
    return total / len(D4_RELATIONS)


def train_arm(model: nn.Module, config: TrainConfig) -> TrainedArm:
    if config.regime not in {"terminal", "relation", "intermediate"}:
        raise ValueError(f"Unknown regime: {config.regime}")
    if config.regime != "terminal" and not isinstance(model, RecurrentOperatorModel):
        raise ValueError(f"Regime {config.regime} requires a recurrent model")

    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    device = torch.device(config.device)
    model = model.to(device)
    model.train()
    generator = EpisodeGenerator(10_000 + config.seed)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    trajectory: list[dict[str, Any]] = []
    checkpoints = set(np.linspace(0, config.steps - 1, num=min(11, config.steps), dtype=int).tolist())
    started = time.perf_counter()
    final_loss = math.nan

    for step in range(config.steps):
        length = int(generator.rng.integers(1, config.train_max_length + 1))
        batch = generator.sample(config.batch_size, length, family="d4").to(device)
        optimizer.zero_grad(set_to_none=True)

        if isinstance(model, RecurrentOperatorModel):
            trace = model.run(batch.tables, batch.op_slots, batch.start)
            loss = F.cross_entropy(trace.logits, batch.target)
            final_accuracy = (trace.logits.argmax(dim=1) == batch.target).float().mean()
            if config.regime == "intermediate":
                intermediate_losses = [
                    F.cross_entropy(model.decode_hidden(hidden), batch.intermediates[:, index])
                    for index, hidden in enumerate(trace.hidden[1:])
                ]
                loss = loss + config.intermediate_weight * torch.stack(intermediate_losses).mean()
            elif config.regime == "relation":
                loss = loss + config.relation_weight * _relation_loss(
                    model,
                    batch.tables,
                    batch.start,
                    batch.canonical_to_slot,
                    config.relation_hidden_weight,
                )
        else:
            logits = model(batch.tables, batch.op_slots, batch.start)
            loss = F.cross_entropy(logits, batch.target)
            final_accuracy = (logits.argmax(dim=1) == batch.target).float().mean()

        if not torch.isfinite(loss):
            raise FloatingPointError(f"Non-finite loss at step {step}: {float(loss.detach())}")
        loss.backward()
        grad_norm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), config.grad_clip))
        optimizer.step()
        final_loss = float(loss.detach())

        if step in checkpoints:
            trajectory.append(
                {
                    "step": step + 1,
                    "length": length,
                    "loss": final_loss,
                    "batch_accuracy": float(final_accuracy.detach()),
                    "gradient_norm_before_clip": grad_norm,
                }
            )

    elapsed = time.perf_counter() - started
    return TrainedArm(
        config=config,
        model=model,
        trajectory=trajectory,
        elapsed_seconds=elapsed,
        final_loss=final_loss,
        parameter_count=parameter_count(model),
    )


def config_dict(config: TrainConfig) -> dict[str, Any]:
    return asdict(config)
