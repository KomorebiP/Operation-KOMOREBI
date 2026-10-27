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

try:  # data.py re-exports the frozen helper in v0.2.0.
    from .data import map_split
except ImportError:  # Keep the canonical module usable during staged upgrades.
    from .splits import map_split

from .models import LinearHyperOperatorRNN, RecurrentOperatorModel, parameter_count


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
    metric_isometry_weight: float = 0.0
    composition_weight: float = 0.0
    composition_shuffle_targets: bool = False
    composition_min_length: int = 2
    composition_max_length: int = 4
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


def compose_operator_codes(operator_codes: torch.Tensor, visible_slots: torch.Tensor) -> torch.Tensor:
    """Compose matrix codes for a word written in anonymous visible slots.

    A word ``[a, b, c]`` is executed on a hidden column vector as
    ``M_c @ M_b @ M_a @ h``.  Building the product by left multiplication is
    therefore essential; text order and matrix-multiplication order reverse.
    """
    if operator_codes.ndim != 4 or operator_codes.shape[-1] != operator_codes.shape[-2]:
        raise ValueError("operator_codes must have shape (batch, slots, dim, dim)")
    if visible_slots.ndim != 2 or visible_slots.shape[0] != operator_codes.shape[0]:
        raise ValueError("visible_slots must have shape (batch, length)")
    batch, slots, dimension, _ = operator_codes.shape
    if visible_slots.numel() and ((visible_slots < 0).any() or (visible_slots >= slots).any()):
        raise ValueError("visible slot index out of range")
    product = torch.eye(dimension, dtype=operator_codes.dtype, device=operator_codes.device)
    product = product.unsqueeze(0).expand(batch, -1, -1)
    rows = torch.arange(batch, device=operator_codes.device)
    for index in range(visible_slots.shape[1]):
        selected = operator_codes[rows, visible_slots[:, index]]
        product = torch.bmm(selected, product)
    return product


def compose_visible_maps(maps: torch.Tensor, visible_slots: torch.Tensor) -> torch.Tensor:
    """Return the exact finite-state map represented by each visible word."""
    if maps.ndim != 3:
        raise ValueError("maps must have shape (batch, slots, states)")
    if visible_slots.ndim != 2 or visible_slots.shape[0] != maps.shape[0]:
        raise ValueError("visible_slots must have shape (batch, length)")
    batch, slots, states = maps.shape
    if visible_slots.numel() and ((visible_slots < 0).any() or (visible_slots >= slots).any()):
        raise ValueError("visible slot index out of range")
    current = torch.arange(states, dtype=torch.long, device=maps.device).unsqueeze(0).expand(batch, -1)
    rows = torch.arange(batch, device=maps.device)
    for index in range(visible_slots.shape[1]):
        selected = maps[rows, visible_slots[:, index]]
        current = torch.gather(selected, 1, current)
    return current


def intrinsic_isometry_loss(
    model: LinearHyperOperatorRNN,
    operator_codes: torch.Tensor,
    metric_factors: tuple[torch.Tensor, torch.Tensor] | None = None,
) -> torch.Tensor:
    """Penalize operator distortion in the model's intrinsic latent metric.

    Ordinary ``linear_hyper`` uses fixed ``G=I``.  ``linear_hyper_metric``
    learns ``G`` and supplies the corresponding whitening transformation.
    """
    if operator_codes.ndim != 4 or operator_codes.shape[-1] != operator_codes.shape[-2]:
        raise ValueError("operator_codes must have shape (batch, slots, dim, dim)")
    if metric_factors is None:
        whitened = model.whiten_operators(operator_codes)
    else:
        whitener, inverse_whitener = metric_factors
        whitened = whitener @ operator_codes @ inverse_whitener
    dimension = whitened.shape[-1]
    identity = torch.eye(dimension, dtype=whitened.dtype, device=whitened.device)
    gram = torch.matmul(whitened.transpose(-1, -2), whitened)
    return (gram - identity).square().mean()


def composition_target_train_mask(composed_maps: torch.Tensor) -> torch.Tensor:
    """Select only independently encoded targets in the frozen train split."""
    if composed_maps.ndim != 2:
        raise ValueError("composed_maps must have shape (batch, states)")
    mappings = composed_maps.detach().cpu().numpy()
    keep = np.fromiter(
        (map_split(mapping) == "train" for mapping in mappings),
        dtype=np.bool_,
        count=mappings.shape[0],
    )
    return torch.from_numpy(keep).to(device=composed_maps.device)


def anonymous_composition_loss(
    model: LinearHyperOperatorRNN,
    tables: torch.Tensor,
    maps: torch.Tensor,
    operator_codes: torch.Tensor,
    rng: np.random.Generator,
    min_length: int = 2,
    max_length: int = 4,
    shuffled_targets: bool = False,
    shuffle_rng: np.random.Generator | None = None,
    words_by_length: dict[int, torch.Tensor] | None = None,
    metric_factors: tuple[torch.Tensor, torch.Tensor] | None = None,
) -> torch.Tensor:
    """Match anonymous word products to independently encoded compositions.

    Exact target maps are constructed solely from visible slots and passed
    through the same encoder independently.  No canonical operator identity is
    supplied.  Targets outside the frozen coordinate train split are removed
    before encoder invocation, preventing auxiliary-loss leakage.
    """
    if min_length < 2 or max_length < min_length:
        raise ValueError("composition lengths must satisfy 2 <= min_length <= max_length")
    if tables.ndim != 4 or maps.ndim != 3 or tables.shape[:2] != maps.shape[:2]:
        raise ValueError(
            "tables and maps must have shapes (batch, slots, states, states) and (batch, slots, states)"
        )
    batch, slots, states = maps.shape
    if tables.shape[-2:] != (states, states):
        raise ValueError("table state dimensions do not match maps")
    if operator_codes.shape[:2] != (batch, slots):
        raise ValueError("operator_codes do not match tables")
    if shuffle_rng is None:
        shuffle_rng = rng

    losses: list[torch.Tensor] = []
    for length in range(min_length, max_length + 1):
        if words_by_length is None:
            words_np = rng.integers(0, slots, size=(batch, length), dtype=np.int64)
            visible_words = torch.from_numpy(words_np).to(device=maps.device)
        else:
            if length not in words_by_length:
                raise ValueError(f"missing visible words for length {length}")
            visible_words = words_by_length[length].to(device=maps.device, dtype=torch.long)
            if visible_words.shape != (batch, length):
                raise ValueError(f"visible words for length {length} must have shape {(batch, length)}")

        composed_maps = compose_visible_maps(maps, visible_words)
        keep = composition_target_train_mask(composed_maps)
        kept_count = int(keep.sum())
        if kept_count == 0 or (shuffled_targets and kept_count < 2):
            continue

        # Filtering deliberately precedes one-hot conversion and encoding.
        target_tables = F.one_hot(composed_maps[keep], num_classes=states).to(dtype=tables.dtype)
        if shuffled_targets:
            permutation = shuffle_rng.permutation(kept_count)
            if np.array_equal(permutation, np.arange(kept_count)):
                permutation = np.roll(permutation, 1)
            order = torch.from_numpy(permutation.copy()).to(device=target_tables.device)
            target_tables = target_tables[order]
        target_codes = model.encode_operators(target_tables.unsqueeze(1))[:, 0]
        predicted_codes = compose_operator_codes(operator_codes, visible_words)[keep]
        # Compare in the intrinsic coordinate system. This makes the auxiliary
        # objective invariant to the learned change of metric coordinates.
        if metric_factors is None:
            combined = torch.stack((target_codes, predicted_codes), dim=1)
            whitened = model.whiten_operators(combined)
            target_codes, predicted_codes = whitened[:, 0], whitened[:, 1]
        else:
            whitener, inverse_whitener = metric_factors
            target_codes = whitener @ target_codes @ inverse_whitener
            predicted_codes = whitener @ predicted_codes @ inverse_whitener
        # The independent encoder branch is a moving target, not a second path
        # through which the encoder can reduce loss by contracting every code.
        # This is the standard stop-gradient anti-collapse boundary for the
        # self-consistency objective; terminal behavior remains fully trained.
        target_codes = target_codes.detach()
        residual = (predicted_codes - target_codes).square().flatten(1).sum(dim=1)
        target_scale = target_codes.detach().square().flatten(1).sum(dim=1).clamp_min(1e-4)
        # log1p bounds the influence of badly mismatched early products so the
        # auxiliary cannot swamp the terminal objective during initialization.
        losses.append(torch.log1p(residual / target_scale).mean())

    if not losses:
        # Preserve device, dtype, and a valid zero-gradient connection.
        return operator_codes.sum() * 0.0
    return torch.stack(losses).mean()


def train_arm(model: nn.Module, config: TrainConfig) -> TrainedArm:
    if config.regime not in {"terminal", "relation", "intermediate", "metric"}:
        raise ValueError(f"Unknown regime: {config.regime}")
    if config.regime != "terminal" and not isinstance(model, RecurrentOperatorModel):
        raise ValueError(f"Regime {config.regime} requires a recurrent model")
    if config.metric_isometry_weight < 0.0 or config.composition_weight < 0.0:
        raise ValueError("auxiliary-loss weights must be nonnegative")
    if config.composition_min_length < 2 or config.composition_max_length < config.composition_min_length:
        raise ValueError("composition lengths must satisfy 2 <= min_length <= max_length")
    auxiliary_requested = config.metric_isometry_weight > 0.0 or config.composition_weight > 0.0
    if auxiliary_requested and not isinstance(model, LinearHyperOperatorRNN):
        raise ValueError("metric and composition losses require a matrix-valued linear_hyper model")

    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    device = torch.device(config.device)
    model = model.to(device)
    model.train()
    generator = EpisodeGenerator(10_000 + config.seed)
    # Separate streams keep episodes and anonymous words matched across true and
    # shuffled-target arms.
    composition_rng = np.random.default_rng(20_000 + config.seed)
    composition_shuffle_rng = np.random.default_rng(30_000 + config.seed)
    metric_parameters: list[nn.Parameter] = []
    ordinary_parameters: list[nn.Parameter] = []
    for name, parameter in model.named_parameters():
        if name.startswith("learned_metric."):
            metric_parameters.append(parameter)
        else:
            ordinary_parameters.append(parameter)
    parameter_groups: list[dict[str, Any]] = [
        {"params": ordinary_parameters, "weight_decay": config.weight_decay}
    ]
    if metric_parameters:
        # Weight decay on log(G) would quietly privilege G=I and confound the
        # learned-metric comparison.
        parameter_groups.append({"params": metric_parameters, "weight_decay": 0.0})
    optimizer = torch.optim.AdamW(parameter_groups, lr=config.learning_rate)
    trajectory: list[dict[str, Any]] = []
    checkpoints = set(np.linspace(0, config.steps - 1, num=min(11, config.steps), dtype=int).tolist())
    started = time.perf_counter()
    final_loss = math.nan

    for step in range(config.steps):
        length = int(generator.rng.integers(1, config.train_max_length + 1))
        batch = generator.sample(
            config.batch_size,
            length,
            family="d4",
            coordinate_split="train",
        ).to(device)
        optimizer.zero_grad(set_to_none=True)

        if isinstance(model, RecurrentOperatorModel):
            trace = model.run(batch.tables, batch.op_slots, batch.start)
            terminal_loss = F.cross_entropy(trace.logits, batch.target)
            loss = terminal_loss
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

            isometry_loss = torch.zeros((), dtype=loss.dtype, device=loss.device)
            composition_loss = torch.zeros((), dtype=loss.dtype, device=loss.device)
            metric_factors = (
                model.metric_factors()
                if isinstance(model, LinearHyperOperatorRNN)
                and (config.metric_isometry_weight > 0.0 or config.composition_weight > 0.0)
                else None
            )
            if config.metric_isometry_weight > 0.0:
                assert isinstance(model, LinearHyperOperatorRNN)
                assert trace.operator_codes is not None
                isometry_loss = intrinsic_isometry_loss(model, trace.operator_codes, metric_factors)
                loss = loss + config.metric_isometry_weight * isometry_loss
            if config.composition_weight > 0.0:
                assert isinstance(model, LinearHyperOperatorRNN)
                assert trace.operator_codes is not None
                composition_loss = anonymous_composition_loss(
                    model,
                    batch.tables,
                    batch.maps,
                    trace.operator_codes,
                    composition_rng,
                    min_length=config.composition_min_length,
                    max_length=config.composition_max_length,
                    shuffled_targets=config.composition_shuffle_targets,
                    shuffle_rng=composition_shuffle_rng,
                    metric_factors=metric_factors,
                )
                loss = loss + config.composition_weight * composition_loss
        else:
            logits = model(batch.tables, batch.op_slots, batch.start)
            terminal_loss = F.cross_entropy(logits, batch.target)
            loss = terminal_loss
            final_accuracy = (logits.argmax(dim=1) == batch.target).float().mean()
            isometry_loss = torch.zeros((), dtype=loss.dtype, device=loss.device)
            composition_loss = torch.zeros((), dtype=loss.dtype, device=loss.device)

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
                    "terminal_loss": float(terminal_loss.detach()),
                    "metric_isometry_loss": float(isometry_loss.detach()),
                    "composition_loss": float(composition_loss.detach()),
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
