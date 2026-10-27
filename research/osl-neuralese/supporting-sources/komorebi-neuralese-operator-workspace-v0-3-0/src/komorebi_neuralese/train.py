from __future__ import annotations

import hashlib
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
from .splits import validate_word_product_scope, word_products_all_in_split


TRAIN_LENGTH_SCHEDULE_NAMESPACE = (
    "komorebi-neuralese/independent-training-length-schedule/v1"
)
_TRAIN_LENGTH_SEED_OFFSET = 40_000


def _training_length_schedule(
    seed: int, minimum: int, maximum: int, steps: int
) -> tuple[np.ndarray, dict[str, Any]]:
    """Freeze training lengths independently of episode-sampler draw counts."""

    schedule_seed = _TRAIN_LENGTH_SEED_OFFSET + int(seed)
    rng = np.random.default_rng(schedule_seed)
    values = rng.integers(minimum, maximum + 1, size=steps, dtype=np.int64)
    payload = (
        TRAIN_LENGTH_SCHEDULE_NAMESPACE.encode("utf-8")
        + b"\x00"
        + np.asarray(
            (schedule_seed, minimum, maximum, steps), dtype="<i8"
        ).tobytes()
        + values.astype("<i8", copy=False).tobytes()
    )
    counts = {
        str(length): int(np.sum(values == length))
        for length in range(minimum, maximum + 1)
    }
    receipt = {
        "namespace": TRAIN_LENGTH_SCHEDULE_NAMESPACE,
        "seed": schedule_seed,
        "minimum": minimum,
        "maximum": maximum,
        "steps": steps,
        "counts": counts,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "independent_of_episode_sampler": True,
    }
    values.setflags(write=False)
    return values, receipt


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
    train_min_length: int = 1
    operator_init_std: float | None = None
    orthogonal_parameterization: str = "qr"
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
    word_product_scope: str = "contiguous"
    conditioned_sampler_backend: str = "cached_exact_v1"
    device: str = "cpu"


@dataclass
class TrainedArm:
    config: TrainConfig
    model: nn.Module
    trajectory: list[dict[str, Any]]
    elapsed_seconds: float
    final_loss: float
    parameter_count: int
    sampling_audit: dict[str, Any]


def _relation_loss(
    model: RecurrentOperatorModel,
    tables: torch.Tensor,
    maps: torch.Tensor,
    start: torch.Tensor,
    canonical_to_slot: torch.Tensor,
    hidden_weight: float,
    word_product_scope: str,
) -> torch.Tensor:
    total = torch.zeros((), device=start.device)
    included = 0
    for word in D4_RELATIONS.values():
        slots = EpisodeGenerator.slots_for_word(canonical_to_slot, word)
        if word_product_scope == "none":
            keep = torch.ones(start.shape[0], dtype=torch.bool, device=start.device)
        else:
            keep_numpy = word_products_all_in_split(
                maps.detach().cpu().numpy(),
                slots.detach().cpu().numpy(),
                "train",
                scope=word_product_scope,
            )
            keep = torch.from_numpy(keep_numpy).to(device=start.device)
        if not bool(keep.any()):
            continue
        trace = model.run(tables[keep], slots[keep], start[keep])
        endpoint = F.cross_entropy(trace.logits, start[keep])
        h0 = trace.hidden[0]
        h1 = trace.hidden[-1]
        scale = h0.square().mean().detach().clamp_min(1e-6)
        hidden = (h1 - h0).square().mean() / scale
        total = total + endpoint + hidden_weight * hidden
        included += 1
    if included == 0:
        return tables.sum() * 0.0
    return total / included


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
    word_product_scope: str = "contiguous",
) -> torch.Tensor:
    """Match anonymous word products to independently encoded compositions.

    Exact target maps are constructed solely from visible slots and passed
    through the same encoder independently.  No canonical operator identity is
    supplied.  Words with a held-out product covered by
    ``word_product_scope`` are removed before encoder invocation, preventing
    auxiliary-loss leakage.
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
    normalized_product_scope = validate_word_product_scope(word_product_scope)

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
        if normalized_product_scope == "none":
            keep = composition_target_train_mask(composed_maps)
        else:
            keep_numpy = word_products_all_in_split(
                maps.detach().cpu().numpy(),
                visible_words.detach().cpu().numpy(),
                "train",
                scope=normalized_product_scope,
            )
            keep = torch.from_numpy(keep_numpy).to(device=composed_maps.device)
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
    if config.steps < 1 or config.batch_size < 1:
        raise ValueError("steps and batch_size must be positive")
    if config.regime not in {"terminal", "relation", "intermediate", "metric"}:
        raise ValueError(f"Unknown regime: {config.regime}")
    if config.regime != "terminal" and not isinstance(model, RecurrentOperatorModel):
        raise ValueError(f"Regime {config.regime} requires a recurrent model")
    if config.metric_isometry_weight < 0.0 or config.composition_weight < 0.0:
        raise ValueError("auxiliary-loss weights must be nonnegative")
    if config.composition_min_length < 2 or config.composition_max_length < config.composition_min_length:
        raise ValueError("composition lengths must satisfy 2 <= min_length <= max_length")
    if config.train_min_length < 1 or config.train_max_length < config.train_min_length:
        raise ValueError("training lengths must satisfy 1 <= train_min_length <= train_max_length")
    if config.operator_init_std is not None and config.operator_init_std <= 0.0:
        raise ValueError("operator_init_std must be positive when supplied")
    word_product_scope = validate_word_product_scope(config.word_product_scope)
    auxiliary_requested = config.metric_isometry_weight > 0.0 or config.composition_weight > 0.0
    if auxiliary_requested and not isinstance(model, LinearHyperOperatorRNN):
        raise ValueError("metric and composition losses require a matrix-valued linear_hyper model")

    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    device = torch.device(config.device)
    model = model.to(device)
    model.train()
    generator = EpisodeGenerator(10_000 + config.seed)
    length_schedule, length_schedule_receipt = _training_length_schedule(
        config.seed,
        config.train_min_length,
        config.train_max_length,
        config.steps,
    )
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
    sampling_candidates = 0
    sampling_rejections = 0
    accepted_examples = 0
    accepted_word_products_checked = 0
    split_violations = 0
    sampling_methods: set[str] = set()
    conditioning_supports: dict[str, dict[str, Any]] = {}
    sampling_by_length: dict[str, dict[str, Any]] = {
        str(length): {
            "batches": 0,
            "accepted_examples": 0,
            "candidate_examples": 0,
            "rejected_examples": 0,
            "accepted_word_products_checked": 0,
            "sampling_methods": set(),
            "conditioning_support_digests": set(),
        }
        for length in range(config.train_min_length, config.train_max_length + 1)
    }

    for step in range(config.steps):
        length = int(length_schedule[step])
        batch = generator.sample(
            config.batch_size,
            length,
            family="d4",
            coordinate_split="train",
            word_product_scope=word_product_scope,
            word_product_split="train" if word_product_scope != "none" else None,
            conditioned_sampler_backend=config.conditioned_sampler_backend,
        ).to(device)
        sampling_candidates += batch.sampling_candidates
        sampling_rejections += batch.sampling_rejections
        accepted_examples += config.batch_size
        sampling_methods.add(batch.sampling_method)
        if (
            word_product_scope != "none"
            and batch.conditioned_sampler_backend != config.conditioned_sampler_backend
        ):
            raise RuntimeError("conditioned sampler backend receipt does not match TrainConfig")
        length_audit = sampling_by_length[str(length)]
        length_audit["batches"] += 1
        length_audit["accepted_examples"] += config.batch_size
        length_audit["candidate_examples"] += batch.sampling_candidates
        length_audit["rejected_examples"] += batch.sampling_rejections
        length_audit["sampling_methods"].add(batch.sampling_method)
        if batch.conditioning_support_digest is not None:
            if (
                batch.rejection_equivalent_candidate_pairs is None
                or batch.rejection_equivalent_accepted_pairs is None
                or batch.rejection_equivalent_acceptance_probability is None
            ):
                raise RuntimeError("direct-conditioned batch omitted its exact support receipt")
            length_audit["conditioning_support_digests"].add(
                batch.conditioning_support_digest
            )
            support_record = {
                "digest": batch.conditioning_support_digest,
                "length": length,
                "candidate_pairs": batch.rejection_equivalent_candidate_pairs,
                "accepted_pairs": batch.rejection_equivalent_accepted_pairs,
                "exact_acceptance_numerator": (
                    batch.rejection_equivalent_accepted_pairs
                ),
                "exact_acceptance_denominator": (
                    batch.rejection_equivalent_candidate_pairs
                ),
                "acceptance_probability": (
                    batch.rejection_equivalent_acceptance_probability
                ),
            }
            previous = conditioning_supports.setdefault(
                batch.conditioning_support_digest, support_record
            )
            if previous != support_record:
                raise RuntimeError("conditioning support digest metadata changed within a run")
        if word_product_scope != "none":
            confined = word_products_all_in_split(
                batch.maps.detach().cpu().numpy(),
                batch.op_slots.detach().cpu().numpy(),
                "train",
                scope=word_product_scope,
            )
            violations = int((~confined).sum())
            split_violations += violations
            if violations:
                raise RuntimeError(
                    f"word-product split confinement failed for {violations} training examples"
                )
            if word_product_scope == "terminal":
                products_per_example = int(length > 0)
            elif word_product_scope == "prefixes":
                products_per_example = length
            else:
                products_per_example = length * (length + 1) // 2
            accepted_word_products_checked += config.batch_size * products_per_example
            length_audit["accepted_word_products_checked"] += (
                config.batch_size * products_per_example
            )
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
                    batch.maps,
                    batch.start,
                    batch.canonical_to_slot,
                    config.relation_hidden_weight,
                    word_product_scope,
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
                    word_product_scope=word_product_scope,
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
                    "sampling_candidates_cumulative": sampling_candidates,
                    "sampling_rejections_cumulative": sampling_rejections,
                    "sampling_acceptance_fraction_cumulative": (
                        accepted_examples / sampling_candidates
                    ),
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
        sampling_audit={
            "coordinate_split": "train",
            "word_product_split": "train" if word_product_scope != "none" else None,
            "word_product_scope": word_product_scope,
            "counter_scope": "main sampled training words only",
            "guarantee": (
                "every nonempty contiguous product traversed by each sampled training word is in train"
                if word_product_scope == "contiguous"
                else "limited to the configured word-product scope"
            ),
            "generated_group_closure_constrained": False,
            "sampling_distribution": (
                "joint primitive-context/word distribution conditioned on all checked products being train"
                if word_product_scope != "none"
                else "unconditioned"
            ),
            "sampling_methods": sorted(sampling_methods),
            "conditioned_sampler_backend": config.conditioned_sampler_backend,
            "length_schedule": length_schedule_receipt,
            "actual_counter_semantics": (
                "candidate_examples and rejected_examples count sampler draws actually executed; "
                "direct-conditioned draws have no fictional rejections"
            ),
            "conditioning_supports": sorted(
                conditioning_supports.values(), key=lambda item: (item["length"], item["digest"])
            ),
            "auxiliary_paths_independently_filtered": word_product_scope != "none",
            "training_batches": config.steps,
            "accepted_examples": accepted_examples,
            "candidate_examples": sampling_candidates,
            "rejected_examples": sampling_rejections,
            "acceptance_fraction": accepted_examples / sampling_candidates,
            "accepted_word_products_checked": accepted_word_products_checked,
            "by_length": {
                key: {
                    **value,
                    "sampling_methods": sorted(value["sampling_methods"]),
                    "conditioning_support_digests": sorted(
                        value["conditioning_support_digests"]
                    ),
                    "acceptance_fraction": (
                        value["accepted_examples"] / value["candidate_examples"]
                        if value["candidate_examples"]
                        else None
                    ),
                }
                for key, value in sampling_by_length.items()
            },
            "split_violations": split_violations if word_product_scope != "none" else None,
            "fail_closed": word_product_scope == "contiguous",
        },
    )


def config_dict(config: TrainConfig) -> dict[str, Any]:
    return asdict(config)
