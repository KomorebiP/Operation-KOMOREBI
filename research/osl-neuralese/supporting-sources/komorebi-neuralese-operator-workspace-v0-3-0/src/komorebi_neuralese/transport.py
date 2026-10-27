from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

import numpy as np
import torch
from torch.nn import functional as F

from .data import EpisodeBatch, EpisodeGenerator
from .evaluate import _chunks
from .models import RecurrentOperatorModel
from .splits import validate_coordinate_split


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


def _normalize_coordinate_split(coordinate_split: str | int | None) -> str | None:
    if coordinate_split is None:
        return None
    if isinstance(coordinate_split, bool):
        raise ValueError("coordinate_split must be 'train', 'dev', 'test', or None")
    if isinstance(coordinate_split, int):
        if coordinate_split == 0:
            return "train"
        if coordinate_split == 1:
            return "test"
        if coordinate_split == 2:
            return "dev"
        raise ValueError("integer coordinate_split must be 0, 1, or 2")
    key = str(coordinate_split).strip().lower().replace("-", "_")
    aliases = {
        "all": None,
        "any": None,
        "none": None,
        "train": "train",
        "anchor": "train",
        "anchors": "train",
        "fit": "train",
        "dev": "dev",
        "validation": "dev",
        "validate": "dev",
        "test": "test",
        "eval": "test",
        "evaluation": "test",
        "heldout": "test",
        "held_out": "test",
    }
    if key not in aliases:
        raise ValueError("coordinate_split must be 'train', 'dev', 'test', or None")
    normalized = aliases[key]
    return validate_coordinate_split(normalized)


def _iter_coordinate_batches(
    generator: EpisodeGenerator,
    examples: int,
    batch_size: int,
    length: int,
    family: str,
    device: torch.device,
    word_product_scope: str = "none",
    word_product_split: str | None = None,
) -> Iterator[EpisodeBatch]:
    if examples < 1 or batch_size < 1:
        raise ValueError("examples and batch_size must be positive")
    for current in _chunks(examples, batch_size):
        yield generator.sample(
            current,
            length,
            family=family,
            word_product_scope=word_product_scope,
            word_product_split=word_product_split,
        ).to(device)


def _balanced_length_counts(examples: int, max_length: int) -> dict[int, int]:
    if examples < 1:
        raise ValueError("examples must be positive")
    if max_length < 1:
        raise ValueError("max_length must be positive")
    quotient, remainder = divmod(int(examples), int(max_length))
    return {
        length: quotient + int(length <= remainder)
        for length in range(1, max_length + 1)
    }


def collect_paired_hidden(
    source: RecurrentOperatorModel,
    target: RecurrentOperatorModel,
    seed: int,
    examples: int,
    batch_size: int,
    max_length: int,
    device: torch.device,
    coordinate_split: str | int | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Collect balanced paired endpoint anchors at depths 1 through max_length.

    ``examples`` is the number of returned anchor pairs.  Only the endpoint h_L
    from each length-L trajectory is retained.  In particular, h_0 is never an
    anchor and shallower states are not repeatedly overrepresented as prefixes of
    longer trajectories.
    """

    normalized_split = _normalize_coordinate_split(coordinate_split)
    generator = EpisodeGenerator(seed, coordinate_split=normalized_split)
    source_values: list[torch.Tensor] = []
    target_values: list[torch.Tensor] = []
    source.eval()
    target.eval()
    counts = _balanced_length_counts(examples, max_length)
    product_scope = "contiguous" if normalized_split == "train" else (
        "terminal" if normalized_split is not None else "none"
    )
    with torch.no_grad():
        for length, length_examples in counts.items():
            if length_examples == 0:
                continue
            for batch in _iter_coordinate_batches(
                generator,
                examples=length_examples,
                batch_size=batch_size,
                length=length,
                family="d4",
                device=device,
                word_product_scope=product_scope,
                word_product_split=normalized_split,
            ):
                source_trace = source.run(batch.tables, batch.op_slots, batch.start)
                target_trace = target.run(batch.tables, batch.op_slots, batch.start)
                source_values.append(source_trace.hidden[-1].detach())
                target_values.append(target_trace.hidden[-1].detach())
    return torch.cat(source_values, dim=0), torch.cat(target_values, dim=0)


def fit_affine_transport(
    source_hidden: torch.Tensor,
    target_hidden: torch.Tensor,
    ridge: float = 1e-5,
) -> AffineTransport:
    if source_hidden.ndim != 2 or target_hidden.ndim != 2:
        raise ValueError("hidden arrays must be matrices")
    if source_hidden.shape[0] != target_hidden.shape[0]:
        raise ValueError("source and target anchor counts differ")
    if source_hidden.shape[0] < 1:
        raise ValueError("at least one anchor pair is required")
    if ridge < 0:
        raise ValueError("ridge must be nonnegative")
    source_mean = source_hidden.mean(dim=0)
    target_mean = target_hidden.mean(dim=0)
    x = source_hidden - source_mean
    y = target_hidden - target_mean
    identity = torch.eye(x.shape[1], device=x.device, dtype=x.dtype)
    weight = torch.linalg.solve(x.T @ x + ridge * identity, x.T @ y)
    bias = target_mean - source_mean @ weight
    return AffineTransport(weight, bias, source_mean, target_mean)


def _deranged_indices(count: int, generator: torch.Generator, device: torch.device) -> torch.Tensor:
    if count < 2:
        return torch.arange(count, device=device)
    identity = torch.arange(count, device=device)
    for _ in range(64):
        permutation = torch.randperm(count, generator=generator, device=device)
        if not torch.any(permutation == identity):
            return permutation
    shift = int(torch.randint(1, count, (1,), generator=generator, device=device).item())
    return torch.roll(identity, shifts=shift)


def fit_shuffled_pair_transport(
    source_hidden: torch.Tensor,
    target_hidden: torch.Tensor,
    seed: int,
    ridge: float = 1e-5,
    groups: torch.Tensor | None = None,
) -> AffineTransport:
    """Fit the affine control after destroying source/target pair identity.

    When ``groups`` is supplied, targets are shuffled within group.  Cross-seed
    transport uses trajectory length as the group, preserving the length and norm
    distribution while removing episode-level correspondence.
    """

    if source_hidden.ndim != 2 or target_hidden.ndim != 2:
        raise ValueError("hidden arrays must be matrices")
    if source_hidden.shape[0] != target_hidden.shape[0]:
        raise ValueError("source and target anchor counts differ")
    count = source_hidden.shape[0]
    if count < 2:
        raise ValueError("at least two anchor pairs are required for a shuffled control")
    device = target_hidden.device
    generator = torch.Generator(device=device).manual_seed(int(seed))
    identity = torch.arange(count, device=device)

    if groups is None:
        order = _deranged_indices(count, generator, device)
    else:
        groups = torch.as_tensor(groups, device=device)
        if groups.ndim != 1 or groups.shape[0] != count:
            raise ValueError("groups must be a vector with one entry per anchor")
        order = identity.clone()
        for group in torch.unique(groups, sorted=True):
            members = torch.nonzero(groups == group, as_tuple=False).flatten()
            local = _deranged_indices(int(members.numel()), generator, device)
            order[members] = members[local]
        # Degenerate singleton-only groupings should still be a genuine control.
        if torch.equal(order, identity):
            order = _deranged_indices(count, generator, device)

    return fit_affine_transport(source_hidden, target_hidden[order], ridge=ridge)


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


def _materialize_tensor(candidate: Any) -> torch.Tensor | None:
    if torch.is_tensor(candidate):
        return candidate
    if callable(candidate):
        try:
            value = candidate()
        except (AttributeError, NotImplementedError, TypeError):
            return None
        if torch.is_tensor(value):
            return value
    return None


def _extract_metric(
    model: RecurrentOperatorModel,
    hidden_dim: int,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor | None:
    """Duck-type learned metric APIs without imposing one on old models."""

    holder = getattr(model, "metric", None)
    candidates: list[Any] = []
    if torch.is_tensor(holder) or (callable(holder) and not isinstance(holder, torch.nn.Module)):
        candidates.append(holder)
    if holder is not None:
        candidates.extend(getattr(holder, name, None) for name in ("metric", "matrix"))
    candidates.extend(
        getattr(model, name, None)
        for name in ("latent_metric", "metric_matrix", "get_metric")
    )
    for candidate in candidates:
        metric = _materialize_tensor(candidate)
        if metric is None:
            continue
        if metric.ndim == 2 and metric.shape == (hidden_dim, hidden_dim):
            metric = metric.detach().to(device=device, dtype=dtype)
            if torch.isfinite(metric).all():
                return 0.5 * (metric + metric.T)

    # Optional compatibility fallback for metric implementations exposing only a
    # whitening factor W, with G = W^T W.
    if holder is not None:
        whitener = _materialize_tensor(getattr(holder, "whitener", None))
        if whitener is not None and whitener.ndim == 2 and whitener.shape == (hidden_dim, hidden_dim):
            whitener = whitener.detach().to(device=device, dtype=dtype)
            return whitener.T @ whitener
    return None


def metric_compatibility_metrics(
    source: RecurrentOperatorModel,
    target: RecurrentOperatorModel,
    transport: AffineTransport,
) -> dict[str, Any]:
    """Measure the pullback defect ||T^T G_B T - G_A|| when G_A and G_B exist."""

    source_dim, target_dim = transport.weight.shape
    device = transport.weight.device
    calculation_dtype = torch.float64
    source_metric = _extract_metric(source, source_dim, device, calculation_dtype)
    target_metric = _extract_metric(target, target_dim, device, calculation_dtype)
    unavailable = {
        "metric_compatibility_available": False,
        "metric_compatibility_frobenius_defect": None,
        "metric_compatibility_normalized_defect": None,
        "metric_compatibility_scale_adjusted_defect": None,
        "metric_compatibility_cosine": None,
    }
    if source_metric is None or target_metric is None:
        return unavailable

    # AffineTransport stores row-vector weight W in h_B = h_A W + b.  The
    # corresponding column-vector map is T = W^T, so the requested pullback is
    # exactly T^T G_B T.
    transform = transport.weight.detach().to(dtype=calculation_dtype).T
    pullback = transform.T @ target_metric @ transform
    difference = pullback - source_metric
    absolute = torch.linalg.matrix_norm(difference)
    normalized = absolute / torch.linalg.matrix_norm(source_metric).clamp_min(1e-12)
    scale = (pullback * source_metric).sum() / pullback.square().sum().clamp_min(1e-12)
    scale_adjusted = torch.linalg.matrix_norm(scale * pullback - source_metric)
    scale_adjusted = scale_adjusted / torch.linalg.matrix_norm(source_metric).clamp_min(1e-12)
    cosine = F.cosine_similarity(pullback.reshape(1, -1), source_metric.reshape(1, -1), dim=1)[0]
    return {
        "metric_compatibility_available": True,
        "metric_compatibility_frobenius_defect": float(absolute.cpu()),
        "metric_compatibility_normalized_defect": float(normalized.cpu()),
        "metric_compatibility_scale_adjusted_defect": float(scale_adjusted.cpu()),
        "metric_compatibility_cosine": float(cosine.cpu()),
        "source_metric_condition_number": float(torch.linalg.cond(source_metric).cpu()),
        "target_metric_condition_number": float(torch.linalg.cond(target_metric).cpu()),
    }


def _hidden_r2(predictions: list[torch.Tensor], targets: list[torch.Tensor]) -> float:
    prediction = torch.cat(predictions, dim=0)
    truth = torch.cat(targets, dim=0)
    residual = (prediction - truth).square().sum()
    total = (truth - truth.mean(dim=0)).square().sum().clamp_min(1e-8)
    return float((1.0 - residual / total).cpu())


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
    shuffled_transport: AffineTransport | None = None,
    coordinate_split: str | int | None = None,
) -> dict[str, Any]:
    if examples < 1 or batch_size < 1:
        raise ValueError("examples and batch_size must be positive")
    if length < 1 or not 0 <= split < length:
        raise ValueError("transport evaluation requires 0 <= split < length")

    normalized_split = _normalize_coordinate_split(coordinate_split)
    generator = EpisodeGenerator(seed, coordinate_split=normalized_split)
    product_scope = "terminal" if normalized_split is not None else "none"
    transformed_exact = 0
    transformed_native_agreement = 0
    random_exact = 0
    shuffled_exact = 0
    decode_reembed_exact = 0
    decode_reembed_native_agreement = 0
    decoded_prefix_exact = 0
    source_native_exact = 0
    target_native_exact = 0
    count = 0
    sampling_candidates = 0
    sampling_rejections = 0
    hidden_predictions: list[torch.Tensor] = []
    random_hidden_predictions: list[torch.Tensor] = []
    shuffled_hidden_predictions: list[torch.Tensor] = []
    reembedded_hidden_predictions: list[torch.Tensor] = []
    hidden_targets: list[torch.Tensor] = []
    empirical_cosine: list[float] = []
    empirical_l2: list[float] = []
    empirical_behavior_agreement = 0
    empirical_left_exact = 0
    empirical_right_exact = 0
    operator_cosine: list[float] = []
    operator_l2: list[float] = []
    operator_bias_l2: list[float] = []
    source.eval()
    target.eval()

    with torch.no_grad():
        for batch in _iter_coordinate_batches(
            generator,
            examples=examples,
            batch_size=batch_size,
            length=length,
            family=family,
            device=device,
            word_product_scope=product_scope,
            word_product_split=normalized_split,
        ):
            current_batch = batch.start.shape[0]
            sampling_candidates += batch.sampling_candidates
            sampling_rejections += batch.sampling_rejections
            prefix = batch.op_slots[:, :split]
            suffix = batch.op_slots[:, split:]
            source_prefix = source.run(batch.tables, prefix, batch.start)
            target_prefix = target.run(batch.tables, prefix, batch.start)
            if source_prefix.operator_codes is None or target_prefix.operator_codes is None:
                raise TypeError("transport evaluation requires recurrent operator codes")

            source_hidden = source_prefix.hidden[-1]
            target_hidden = target_prefix.hidden[-1]
            aligned = transport.apply(source_hidden)
            random_aligned = random_transport.apply(source_hidden)
            shuffled_aligned = shuffled_transport.apply(source_hidden) if shuffled_transport is not None else None

            decoded_state = source.decode_hidden(source_hidden).argmax(dim=1)
            reembedded = target.initial_hidden(decoded_state)
            prefix_truth = batch.start if split == 0 else batch.intermediates[:, split - 1]
            decoded_prefix_exact += int((decoded_state == prefix_truth).sum().item())

            aligned_result = target.continue_from_hidden(aligned, target_prefix.operator_codes, suffix)
            random_result = target.continue_from_hidden(random_aligned, target_prefix.operator_codes, suffix)
            shuffled_result = (
                target.continue_from_hidden(shuffled_aligned, target_prefix.operator_codes, suffix)
                if shuffled_aligned is not None
                else None
            )
            reembedded_result = target.continue_from_hidden(reembedded, target_prefix.operator_codes, suffix)
            target_native_result = target.continue_from_hidden(
                target_hidden, target_prefix.operator_codes, suffix
            )
            source_native_result = source.continue_from_hidden(
                source_hidden, source_prefix.operator_codes, suffix
            )

            aligned_prediction = aligned_result.logits.argmax(dim=1)
            native_prediction = target_native_result.logits.argmax(dim=1)
            reembedded_prediction = reembedded_result.logits.argmax(dim=1)
            transformed_exact += int((aligned_prediction == batch.target).sum().item())
            transformed_native_agreement += int((aligned_prediction == native_prediction).sum().item())
            random_exact += int((random_result.logits.argmax(dim=1) == batch.target).sum().item())
            if shuffled_result is not None:
                shuffled_exact += int((shuffled_result.logits.argmax(dim=1) == batch.target).sum().item())
            decode_reembed_exact += int((reembedded_prediction == batch.target).sum().item())
            decode_reembed_native_agreement += int((reembedded_prediction == native_prediction).sum().item())
            source_native_exact += int((source_native_result.logits.argmax(dim=1) == batch.target).sum().item())
            target_native_exact += int((native_prediction == batch.target).sum().item())

            hidden_predictions.append(aligned)
            random_hidden_predictions.append(random_aligned)
            if shuffled_aligned is not None:
                shuffled_hidden_predictions.append(shuffled_aligned)
            reembedded_hidden_predictions.append(reembedded)
            hidden_targets.append(target_hidden)

            rows = torch.arange(current_batch, device=device)
            next_slots = batch.op_slots[:, split]
            source_code = source_prefix.operator_codes[rows, next_slots]
            target_code = target_prefix.operator_codes[rows, next_slots]
            source_next = source.step_hidden(source_hidden, source_code)
            left = transport.apply(source_next)
            right = target.step_hidden(aligned, target_code)
            empirical_cosine.extend(F.cosine_similarity(left, right, dim=1).cpu().tolist())
            scale = right.norm(dim=1).clamp_min(1e-8)
            empirical_l2.extend(((left - right).norm(dim=1) / scale).cpu().tolist())

            left_prediction = target.decode_hidden(left).argmax(dim=1)
            right_prediction = target.decode_hidden(right).argmax(dim=1)
            next_truth = batch.intermediates[:, split]
            empirical_behavior_agreement += int((left_prediction == right_prediction).sum().item())
            empirical_left_exact += int((left_prediction == next_truth).sum().item())
            empirical_right_exact += int((right_prediction == next_truth).sum().item())

            if (
                source_code.ndim == 3
                and target_code.ndim == 3
                and source_code.shape[1] == source_code.shape[2] == transport.weight.shape[0]
                and target_code.shape[1] == target_code.shape[2] == transport.weight.shape[1]
            ):
                transform = transport.weight.T
                operator_left = torch.matmul(transform.unsqueeze(0), source_code)
                operator_right = torch.matmul(target_code, transform.unsqueeze(0))
                flat_left = operator_left.flatten(1)
                flat_right = operator_right.flatten(1)
                operator_cosine.extend(F.cosine_similarity(flat_left, flat_right, dim=1).cpu().tolist())
                operator_scale = flat_right.norm(dim=1).clamp_min(1e-8)
                operator_l2.extend(((flat_left - flat_right).norm(dim=1) / operator_scale).cpu().tolist())

                bias_column = transport.bias.reshape(1, -1, 1).expand(current_batch, -1, -1)
                transformed_bias = torch.matmul(target_code, bias_column)
                bias_scale = transformed_bias.flatten(1).norm(dim=1).clamp_min(1e-8)
                operator_bias_l2.extend(
                    ((bias_column - transformed_bias).flatten(1).norm(dim=1) / bias_scale).cpu().tolist()
                )
            count += current_batch

    heldout_r2 = _hidden_r2(hidden_predictions, hidden_targets)
    random_r2 = _hidden_r2(random_hidden_predictions, hidden_targets)
    shuffled_r2 = (
        _hidden_r2(shuffled_hidden_predictions, hidden_targets)
        if shuffled_hidden_predictions
        else None
    )
    reembedded_r2 = _hidden_r2(reembedded_hidden_predictions, hidden_targets)
    operator_available = bool(operator_cosine)
    shuffled_accuracy = shuffled_exact / count if shuffled_transport is not None else None
    metrics: dict[str, Any] = {
        "available": True,
        "family": family,
        "examples": count,
        "length": length,
        "split": split,
        "coordinate_split": normalized_split,
        "word_product_scope": product_scope,
        "word_product_split": normalized_split,
        "sampling_candidates": sampling_candidates,
        "sampling_rejections": sampling_rejections,
        "sampling_acceptance_fraction": count / sampling_candidates,
        "heldout_hidden_r2": heldout_r2,
        "random_map_hidden_r2": random_r2,
        "shuffled_pair_hidden_r2": shuffled_r2,
        "decode_reembed_hidden_r2": reembedded_r2,
        "aligned_state_patch_accuracy": transformed_exact / count,
        "aligned_target_native_agreement": transformed_native_agreement / count,
        "random_map_state_patch_accuracy": random_exact / count,
        "shuffled_pair_state_patch_accuracy": shuffled_accuracy,
        "shuffled_pair_affine_state_patch_accuracy": shuffled_accuracy,
        "decode_reembed_state_patch_accuracy": decode_reembed_exact / count,
        "decode_target_reembed_accuracy": decode_reembed_exact / count,
        "decode_reembed_target_native_agreement": decode_reembed_native_agreement / count,
        "decode_reembed_prefix_accuracy": decoded_prefix_exact / count,
        "source_native_accuracy": source_native_exact / count,
        "target_native_accuracy": target_native_exact / count,
        # These retain the v0.1 state-conditioned intertwining schema.
        "empirical_intertwining_cosine_mean": float(np.mean(empirical_cosine)),
        "empirical_intertwining_normalized_l2_mean": float(np.mean(empirical_l2)),
        "empirical_intertwining_behavior_agreement": empirical_behavior_agreement / count,
        "empirical_intertwining_left_next_state_accuracy": empirical_left_exact / count,
        "empirical_intertwining_right_next_state_accuracy": empirical_right_exact / count,
        # These directly test T rho_A(g) ~= rho_B(g) T when codes are matrices.
        "operator_intertwining_available": operator_available,
        "operator_intertwining_cosine_mean": float(np.mean(operator_cosine)) if operator_available else None,
        "operator_intertwining_normalized_frobenius_mean": (
            float(np.mean(operator_l2)) if operator_available else None
        ),
        "operator_intertwining_affine_bias_normalized_l2_mean": (
            float(np.mean(operator_bias_l2)) if operator_available else None
        ),
        "operator_intertwining_behavior_agreement": empirical_behavior_agreement / count,
        "operator_intertwining_left_next_state_accuracy": empirical_left_exact / count,
        "operator_intertwining_right_next_state_accuracy": empirical_right_exact / count,
    }
    metrics.update(metric_compatibility_metrics(source, target, transport))
    return metrics


def cross_seed_transport(
    source: RecurrentOperatorModel,
    target: RecurrentOperatorModel,
    seed: int,
    anchor_examples: int,
    test_examples: int,
    batch_size: int,
    device: torch.device,
    anchor_coordinate_split: str | int | None = "train",
    test_coordinate_split: str | int | None = "test",
) -> tuple[dict[str, Any], AffineTransport]:
    anchor_max_length = 4
    source_hidden, target_hidden = collect_paired_hidden(
        source,
        target,
        seed=seed,
        examples=anchor_examples,
        batch_size=batch_size,
        max_length=anchor_max_length,
        device=device,
        coordinate_split=anchor_coordinate_split,
    )
    transport = fit_affine_transport(source_hidden, target_hidden)
    length_counts = _balanced_length_counts(anchor_examples, anchor_max_length)
    anchor_groups = torch.cat(
        [
            torch.full((count,), length, device=target_hidden.device, dtype=torch.long)
            for length, count in length_counts.items()
            if count
        ]
    )
    shuffled_transport = fit_shuffled_pair_transport(
        source_hidden,
        target_hidden,
        seed=seed + 1,
        groups=anchor_groups,
    )
    random_transport = random_matched_transport(transport, seed + 2)
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
            shuffled_transport=shuffled_transport,
            coordinate_split=test_coordinate_split,
        )
    # Keep the D4 fields at top level for stable v0.1 gate and receipt schemas.
    metrics: dict[str, Any] = dict(by_family["d4"])
    metrics["by_family"] = by_family
    metrics["anchor_family"] = "d4"
    metrics["anchor_max_length"] = anchor_max_length
    metrics["anchor_length_counts"] = {str(key): value for key, value in length_counts.items()}
    metrics["anchor_hidden_includes_h0"] = False
    metrics["anchor_coordinate_split"] = _normalize_coordinate_split(anchor_coordinate_split)
    metrics["test_coordinate_split"] = _normalize_coordinate_split(test_coordinate_split)
    metrics["anchor_word_product_scope"] = (
        "contiguous"
        if _normalize_coordinate_split(anchor_coordinate_split) == "train"
        else "terminal"
        if _normalize_coordinate_split(anchor_coordinate_split) is not None
        else "none"
    )
    metrics["test_word_product_scope"] = (
        "terminal" if _normalize_coordinate_split(test_coordinate_split) is not None else "none"
    )
    metrics["anchor_vectors"] = int(source_hidden.shape[0])
    metrics["source_dim"] = int(source_hidden.shape[1])
    metrics["target_dim"] = int(target_hidden.shape[1])
    return metrics, transport
