from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from .data import EpisodeGenerator
from .evaluate import _chunks
from .models import RecurrentOperatorModel


@dataclass
class AffineTransport:
    weight: torch.Tensor
    bias: torch.Tensor
    source_mean: torch.Tensor
    target_mean: torch.Tensor

    def apply(self, hidden: torch.Tensor) -> torch.Tensor:
        return hidden @ self.weight + self.bias

    def to_serializable(self) -> dict[str, Any]:
        return {
            "weight": self.weight.detach().cpu().tolist(),
            "bias": self.bias.detach().cpu().tolist(),
            "source_mean": self.source_mean.detach().cpu().tolist(),
            "target_mean": self.target_mean.detach().cpu().tolist(),
        }


def collect_paired_hidden(
    source: RecurrentOperatorModel,
    target: RecurrentOperatorModel,
    seed: int,
    examples: int,
    batch_size: int,
    max_length: int,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor]:
    generator = EpisodeGenerator(seed)
    source_values: list[torch.Tensor] = []
    target_values: list[torch.Tensor] = []
    source.eval()
    target.eval()
    with torch.no_grad():
        for current_batch in _chunks(examples, batch_size):
            length = int(generator.rng.integers(1, max_length + 1))
            batch = generator.sample(current_batch, length, family="d4").to(device)
            source_trace = source.run(batch.tables, batch.op_slots, batch.start)
            target_trace = target.run(batch.tables, batch.op_slots, batch.start)
            source_values.extend(hidden.detach() for hidden in source_trace.hidden)
            target_values.extend(hidden.detach() for hidden in target_trace.hidden)
    return torch.cat(source_values, dim=0), torch.cat(target_values, dim=0)


def fit_affine_transport(source_hidden: torch.Tensor, target_hidden: torch.Tensor, ridge: float = 1e-5) -> AffineTransport:
    if source_hidden.ndim != 2 or target_hidden.ndim != 2:
        raise ValueError("hidden arrays must be matrices")
    if source_hidden.shape[0] != target_hidden.shape[0]:
        raise ValueError("source and target anchor counts differ")
    source_mean = source_hidden.mean(dim=0)
    target_mean = target_hidden.mean(dim=0)
    x = source_hidden - source_mean
    y = target_hidden - target_mean
    identity = torch.eye(x.shape[1], device=x.device, dtype=x.dtype)
    weight = torch.linalg.solve(x.T @ x + ridge * identity, x.T @ y)
    bias = target_mean - source_mean @ weight
    return AffineTransport(weight, bias, source_mean, target_mean)


def random_matched_transport(reference: AffineTransport, seed: int) -> AffineTransport:
    device = reference.weight.device
    dtype = reference.weight.dtype
    generator = torch.Generator(device=device).manual_seed(seed)
    random = torch.randn(reference.weight.shape, generator=generator, device=device, dtype=dtype)
    if random.shape[0] == random.shape[1]:
        q, _ = torch.linalg.qr(random)
        scale = reference.weight.norm() / q.norm().clamp_min(1e-8)
        weight = q * scale
    else:
        weight = random * (reference.weight.norm() / random.norm().clamp_min(1e-8))
    bias = reference.target_mean - reference.source_mean @ weight
    return AffineTransport(weight, bias, reference.source_mean, reference.target_mean)


def evaluate_transport(
    source: RecurrentOperatorModel,
    target: RecurrentOperatorModel,
    transport: AffineTransport,
    random_transport: AffineTransport,
    seed: int,
    examples: int,
    batch_size: int,
    device: torch.device,
    length: int = 8,
    split: int = 4,
    family: str = "d4",
) -> dict[str, Any]:
    generator = EpisodeGenerator(seed)
    transformed_exact = 0
    random_exact = 0
    target_native_exact = 0
    count = 0
    hidden_predictions: list[torch.Tensor] = []
    hidden_targets: list[torch.Tensor] = []
    intertwining_cosine: list[float] = []
    intertwining_l2: list[float] = []
    source.eval()
    target.eval()

    with torch.no_grad():
        for current_batch in _chunks(examples, batch_size):
            batch = generator.sample(current_batch, length, family=family).to(device)
            prefix = batch.op_slots[:, :split]
            suffix = batch.op_slots[:, split:]
            source_prefix = source.run(batch.tables, prefix, batch.start)
            target_prefix = target.run(batch.tables, prefix, batch.start)
            aligned = transport.apply(source_prefix.hidden[-1])
            random_aligned = random_transport.apply(source_prefix.hidden[-1])
            aligned_result = target.continue_from_hidden(aligned, target_prefix.operator_codes, suffix)
            random_result = target.continue_from_hidden(random_aligned, target_prefix.operator_codes, suffix)
            native_result = target.continue_from_hidden(
                target_prefix.hidden[-1], target_prefix.operator_codes, suffix
            )
            transformed_exact += int((aligned_result.logits.argmax(dim=1) == batch.target).sum())
            random_exact += int((random_result.logits.argmax(dim=1) == batch.target).sum())
            target_native_exact += int((native_result.logits.argmax(dim=1) == batch.target).sum())

            hidden_predictions.append(aligned)
            hidden_targets.append(target_prefix.hidden[-1])

            rows = torch.arange(current_batch, device=device)
            next_slots = batch.op_slots[:, split]
            source_code = source_prefix.operator_codes[rows, next_slots]
            target_code = target_prefix.operator_codes[rows, next_slots]
            source_next = source.step_hidden(source_prefix.hidden[-1], source_code)
            left = transport.apply(source_next)
            right = target.step_hidden(aligned, target_code)
            intertwining_cosine.extend(F.cosine_similarity(left, right, dim=1).cpu().tolist())
            scale = right.norm(dim=1).clamp_min(1e-8)
            intertwining_l2.extend(((left - right).norm(dim=1) / scale).cpu().tolist())
            count += current_batch

    prediction = torch.cat(hidden_predictions, dim=0)
    truth = torch.cat(hidden_targets, dim=0)
    residual = (prediction - truth).square().sum()
    total = (truth - truth.mean(dim=0)).square().sum().clamp_min(1e-8)
    r2 = 1.0 - residual / total
    return {
        "available": True,
        "family": family,
        "examples": count,
        "length": length,
        "split": split,
        "heldout_hidden_r2": float(r2.cpu()),
        "aligned_state_patch_accuracy": transformed_exact / count,
        "random_map_state_patch_accuracy": random_exact / count,
        "target_native_accuracy": target_native_exact / count,
        "empirical_intertwining_cosine_mean": float(np.mean(intertwining_cosine)),
        "empirical_intertwining_normalized_l2_mean": float(np.mean(intertwining_l2)),
    }


def cross_seed_transport(
    source: RecurrentOperatorModel,
    target: RecurrentOperatorModel,
    seed: int,
    anchor_examples: int,
    test_examples: int,
    batch_size: int,
    device: torch.device,
) -> tuple[dict[str, Any], AffineTransport]:
    source_hidden, target_hidden = collect_paired_hidden(
        source,
        target,
        seed=seed,
        examples=anchor_examples,
        batch_size=batch_size,
        max_length=4,
        device=device,
    )
    transport = fit_affine_transport(source_hidden, target_hidden)
    random_transport = random_matched_transport(transport, seed + 1)
    by_family: dict[str, dict[str, Any]] = {}
    for offset, family in enumerate(("d4", "c8", "mixed_cycle", "random")):
        by_family[family] = evaluate_transport(
            source,
            target,
            transport,
            random_transport,
            seed=seed + 1000 + 1000 * offset,
            examples=test_examples,
            batch_size=batch_size,
            device=device,
            family=family,
        )
    # Keep the D4 fields at top level for stable gate and receipt schemas.
    metrics: dict[str, Any] = dict(by_family["d4"])
    metrics["by_family"] = by_family
    metrics["anchor_family"] = "d4"
    metrics["anchor_max_length"] = 4
    metrics["anchor_vectors"] = int(source_hidden.shape[0])
    metrics["source_dim"] = int(source_hidden.shape[1])
    metrics["target_dim"] = int(target_hidden.shape[1])
    return metrics, transport
