from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import torch
from torch.nn import functional as F

from .algebra import N_OPERATORS, N_STATES
from .data import EpisodeBatch, EpisodeGenerator
from .models import RecurrentOperatorModel


@dataclass(frozen=True)
class ClosureEvaluationConfig:
    """Configuration for the v0.2 dynamical-closure audit.

    Neighbor offsets are applied to every requested depth.  The default therefore
    evaluates 15/16/17, 31/32/33, and 63/64/65 rather than reporting only isolated
    depths that could benefit from a periodic endpoint coincidence.
    """

    depths: tuple[int, ...] = (16, 32, 64)
    neighbor_offsets: tuple[int, ...] = (-1, 0, 1)
    examples: int = 2048
    batch_size: int = 256
    geometry_examples: int = 2048
    composition_examples: int = 2048
    patch_examples: int = 2048
    composition_family: str = "random"
    patch_donor_family: str = "random"
    patch_recipient_family: str = "random"
    patch_prefix_length: int = 4
    patch_suffix_length: int = 8
    coordinate_split: str = "test"


def _chunks(total: int, size: int) -> Iterable[int]:
    if total < 1:
        raise ValueError("examples must be positive")
    if size < 1:
        raise ValueError("batch_size must be positive")
    remaining = total
    while remaining:
        current = min(size, remaining)
        yield current
        remaining -= current


def _generator(seed: int, coordinate_split: str) -> EpisodeGenerator:
    if coordinate_split not in {"train", "dev", "test"}:
        raise ValueError("coordinate_split must be 'train', 'dev', or 'test'")
    return EpisodeGenerator(seed, coordinate_split=coordinate_split)


def expand_neighbor_depths(
    depths: Iterable[int],
    neighbor_offsets: Iterable[int] = (-1, 0, 1),
) -> tuple[int, ...]:
    """Return the sorted nonnegative union of requested depths and neighbors."""

    requested = tuple(int(depth) for depth in depths)
    offsets = tuple(int(offset) for offset in neighbor_offsets)
    if not requested:
        raise ValueError("depths must not be empty")
    if not offsets:
        raise ValueError("neighbor_offsets must not be empty")
    if any(depth < 0 for depth in requested):
        raise ValueError("depths must be nonnegative")
    return tuple(sorted({depth + offset for depth in requested for offset in offsets if depth + offset >= 0}))


def compose_action_tables(first: torch.Tensor, second: torch.Tensor) -> torch.Tensor:
    """Compose row-action tables for applying ``first`` and then ``second``.

    Episode tables use ``T[x, y] = 1`` when the map sends ``x`` to ``y``.  A
    row state therefore acts on the right, so the directly observed composite is
    ``first @ second``.  This is intentionally the opposite written order from
    the corresponding latent column-state product.
    """

    if first.ndim < 2 or second.ndim < 2:
        raise ValueError("action tables must have at least two dimensions")
    if first.shape[-2:] != second.shape[-2:]:
        raise ValueError("action tables must have matching square trailing dimensions")
    if first.shape[-1] != first.shape[-2]:
        raise ValueError("action tables must be square")
    return torch.matmul(first, second)


def word_action_tables(tables: torch.Tensor, slots: torch.Tensor) -> torch.Tensor:
    """Compose an anonymous batched word using only visible slot indices."""

    if tables.ndim != 4 or tables.shape[-1] != tables.shape[-2]:
        raise ValueError("tables must have shape (batch, operators, states, states)")
    if slots.ndim != 2 or slots.shape[0] != tables.shape[0]:
        raise ValueError("slots must have shape (batch, length)")
    if slots.dtype != torch.long:
        slots = slots.long()
    batch, operators, states, _ = tables.shape
    if slots.numel() and (int(slots.min()) < 0 or int(slots.max()) >= operators):
        raise ValueError("slot index out of range")
    product = torch.eye(states, dtype=tables.dtype, device=tables.device).expand(batch, -1, -1).clone()
    rows = torch.arange(batch, device=tables.device)
    for step in range(slots.shape[1]):
        product = compose_action_tables(product, tables[rows, slots[:, step]])
    return product


def compose_latent_matrices(first: torch.Tensor, second: torch.Tensor) -> torch.Tensor:
    """Compose latent column-state maps for applying ``first`` then ``second``."""

    if first.ndim < 2 or second.ndim < 2:
        raise ValueError("latent operators must have at least two dimensions")
    if first.shape[-2:] != second.shape[-2:]:
        raise ValueError("latent operators must have matching square trailing dimensions")
    if first.shape[-1] != first.shape[-2]:
        raise ValueError("latent operators must be square")
    return torch.matmul(second, first)


def _slot_vector(slots: torch.Tensor | int, batch: int, device: torch.device) -> torch.Tensor:
    if isinstance(slots, int):
        result = torch.full((batch,), slots, dtype=torch.long, device=device)
    else:
        result = slots.to(device=device, dtype=torch.long)
        if result.ndim == 2 and result.shape[1] == 1:
            result = result[:, 0]
        if result.shape != (batch,):
            raise ValueError("slot selectors must be scalar or have shape (batch,)")
    return result


def _selected(values: torch.Tensor, slots: torch.Tensor) -> torch.Tensor:
    rows = torch.arange(values.shape[0], device=values.device)
    return values[rows, slots]


def _replace_slot(tables: torch.Tensor, slots: torch.Tensor, replacements: torch.Tensor) -> torch.Tensor:
    output = tables.clone()
    rows = torch.arange(tables.shape[0], device=tables.device)
    output[rows, slots] = replacements
    return output


def _metric_matrix(
    model: RecurrentOperatorModel,
    hidden_dim: int,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    accessor = getattr(model, "metric_matrix", None)
    if callable(accessor):
        matrix = accessor()
    else:
        metric = getattr(model, "metric", None)
        accessor = getattr(metric, "matrix", None) if metric is not None else None
        matrix = accessor() if callable(accessor) else torch.eye(hidden_dim, device=device, dtype=dtype)
    matrix = torch.as_tensor(matrix, device=device, dtype=dtype)
    if matrix.shape != (hidden_dim, hidden_dim):
        raise ValueError(
            f"latent metric must have shape {(hidden_dim, hidden_dim)}, got {tuple(matrix.shape)}"
        )
    if not torch.isfinite(matrix).all():
        raise ValueError("latent metric contains non-finite values")
    return 0.5 * (matrix + matrix.transpose(-1, -2))


def latent_g_norm(model: RecurrentOperatorModel, hidden: torch.Tensor) -> torch.Tensor:
    """Evaluate the learned latent norm, using Euclidean geometry when absent."""

    if hidden.ndim < 2:
        raise ValueError("hidden states must have a trailing feature dimension")
    matrix = _metric_matrix(model, hidden.shape[-1], hidden.device, hidden.dtype)
    quadratic = torch.einsum("...i,ij,...j->...", hidden, matrix, hidden)
    tolerance = 32 * torch.finfo(hidden.dtype).eps
    if bool((quadratic < -tolerance).any()):
        raise ValueError("latent metric is not positive semidefinite on evaluated states")
    return quadratic.clamp_min(0).sqrt()


def whiten_operators(model: RecurrentOperatorModel, matrices: torch.Tensor) -> torch.Tensor:
    """Transform latent matrices into Euclidean coordinates induced by ``G``."""

    direct = getattr(model, "whiten_operators", None)
    if callable(direct):
        result = direct(matrices)
    else:
        metric = getattr(model, "metric", None)
        metric_method = getattr(metric, "whiten_operators", None) if metric is not None else None
        if callable(metric_method):
            result = metric_method(matrices)
        else:
            hidden_dim = matrices.shape[-1]
            g = _metric_matrix(model, hidden_dim, matrices.device, matrices.dtype)
            # torch.linalg.cholesky gives G=L L^T, while W=L^T satisfies G=W^T W.
            whitener = torch.linalg.cholesky(g).transpose(-1, -2)
            inverse = torch.linalg.inv(whitener)
            result = torch.matmul(torch.matmul(whitener, matrices), inverse)
    if result.shape != matrices.shape:
        raise ValueError("whiten_operators must preserve the matrix tensor shape")
    return result


def metric_diagnostics(
    model: RecurrentOperatorModel,
    hidden_dim: int,
    device: torch.device | str,
    dtype: torch.dtype = torch.float32,
) -> dict[str, float]:
    """Audit scale and conditioning of the optional learned metric."""

    device = torch.device(device)
    with torch.no_grad():
        matrix = _metric_matrix(model, hidden_dim, device, dtype).double()
        eigenvalues = torch.linalg.eigvalsh(matrix)
    minimum = float(eigenvalues.min())
    maximum = float(eigenvalues.max())
    return {
        "trace": float(torch.trace(matrix)),
        "trace_over_dimension": float(torch.trace(matrix) / hidden_dim),
        "minimum_eigenvalue": minimum,
        "maximum_eigenvalue": maximum,
        "condition_number": maximum / max(minimum, np.finfo(np.float64).tiny),
    }


def _summary(values: list[float] | np.ndarray) -> dict[str, float | int | None]:
    array = np.asarray(values, dtype=np.float64).reshape(-1)
    finite = array[np.isfinite(array)]
    base: dict[str, float | int | None] = {
        "count": int(array.size),
        "finite_fraction": float(finite.size / array.size) if array.size else None,
    }
    if not finite.size:
        base.update({key: None for key in ("mean", "median", "p05", "p95", "minimum", "maximum")})
        return base
    base.update(
        {
            "mean": float(np.mean(finite)),
            "median": float(np.median(finite)),
            "p05": float(np.quantile(finite, 0.05)),
            "p95": float(np.quantile(finite, 0.95)),
            "minimum": float(np.min(finite)),
            "maximum": float(np.max(finite)),
        }
    )
    return base


def _apply_maps(maps: torch.Tensor, start: torch.Tensor, slots: torch.Tensor) -> torch.Tensor:
    current = start.clone()
    rows = torch.arange(start.shape[0], device=start.device)
    for step in range(slots.shape[1]):
        chosen = maps[rows, slots[:, step]]
        current = chosen[rows, current]
    return current


def deep_accuracy_stability(
    model: RecurrentOperatorModel,
    family: str,
    depths: Iterable[int],
    examples_per_depth: int,
    batch_size: int,
    seed: int,
    device: torch.device | str,
    coordinate_split: str,
    neighbor_offsets: Iterable[int] = (-1, 0, 1),
) -> dict[str, Any]:
    """Measure endpoint correctness and full-trajectory stability at deep horizons."""

    if not isinstance(model, RecurrentOperatorModel):
        return {"available": False, "reason": "model is nonrecurrent", "coordinate_split": coordinate_split}
    requested = tuple(int(depth) for depth in depths)
    offsets = tuple(int(offset) for offset in neighbor_offsets)
    evaluated = expand_neighbor_depths(requested, offsets)
    generator = _generator(seed, coordinate_split)
    device = torch.device(device)
    was_training = model.training
    model.eval()
    by_depth: dict[str, Any] = {}
    try:
        with torch.no_grad():
            for depth in evaluated:
                correct = 0
                trajectory_exact = 0
                total = 0
                finite_trajectory: list[float] = []
                peak_absolute: list[float] = []
                endpoint_euclidean_ratio: list[float] = []
                transient_euclidean_gain: list[float] = []
                endpoint_g_ratio: list[float] = []
                transient_g_gain: list[float] = []
                step_g_ratio: list[float] = []
                g_log_growth: list[float] = []
                step_correct = 0
                step_count = 0
                initial_g_values: list[float] = []
                endpoint_g_values: list[float] = []

                for current_batch in _chunks(examples_per_depth, batch_size):
                    batch = generator.sample(current_batch, depth, family=family).to(device)
                    trace = model.run(batch.tables, batch.op_slots, batch.start)
                    prediction = trace.logits.argmax(dim=1)
                    correct += int((prediction == batch.target).sum())
                    total += current_batch

                    trajectory = torch.stack(trace.hidden, dim=1)
                    finite = torch.isfinite(trajectory).all(dim=(1, 2))
                    finite_trajectory.extend(finite.float().cpu().tolist())
                    peak_absolute.extend(trajectory.abs().amax(dim=(1, 2)).cpu().tolist())

                    euclidean = trajectory.norm(dim=2)
                    denominator = euclidean[:, 0].clamp_min(torch.finfo(euclidean.dtype).eps)
                    euclidean_ratio = euclidean / denominator[:, None]
                    endpoint_euclidean_ratio.extend(euclidean_ratio[:, -1].cpu().tolist())
                    transient_euclidean_gain.extend(euclidean_ratio.amax(dim=1).cpu().tolist())

                    g_values = latent_g_norm(model, trajectory)
                    g_denominator = g_values[:, 0].clamp_min(torch.finfo(g_values.dtype).eps)
                    g_ratio = g_values / g_denominator[:, None]
                    endpoint_g_ratio.extend(g_ratio[:, -1].cpu().tolist())
                    transient_g_gain.extend(g_ratio.amax(dim=1).cpu().tolist())
                    initial_g_values.extend(g_values[:, 0].cpu().tolist())
                    endpoint_g_values.extend(g_values[:, -1].cpu().tolist())
                    if depth:
                        per_step = g_values[:, 1:] / g_values[:, :-1].clamp_min(
                            torch.finfo(g_values.dtype).eps
                        )
                        step_g_ratio.extend(per_step.reshape(-1).cpu().tolist())
                        log_growth = torch.log(g_ratio[:, -1].clamp_min(torch.finfo(g_values.dtype).tiny)) / depth
                        g_log_growth.extend(log_growth.cpu().tolist())

                        decoded = torch.stack(
                            [model.decode_hidden(hidden).argmax(dim=1) for hidden in trace.hidden[1:]], dim=1
                        )
                        matches = decoded == batch.intermediates
                        step_correct += int(matches.sum())
                        step_count += int(matches.numel())
                        trajectory_exact += int(matches.all(dim=1).sum())
                    else:
                        trajectory_exact += int((prediction == batch.start).sum())

                g_endpoint = _summary(endpoint_g_ratio)
                g_transient = _summary(transient_g_gain)
                record = {
                    "examples": total,
                    "endpoint_accuracy": correct / total,
                    "mean_step_accuracy": step_correct / step_count if step_count else None,
                    "all_steps_exact_fraction": trajectory_exact / total,
                    "finite_trajectory_fraction": float(np.mean(finite_trajectory)),
                    "peak_absolute_hidden": _summary(peak_absolute),
                    "initial_g_norm": _summary(initial_g_values),
                    "endpoint_g_norm": _summary(endpoint_g_values),
                    "euclidean_endpoint_ratio": _summary(endpoint_euclidean_ratio),
                    "euclidean_transient_gain": _summary(transient_euclidean_gain),
                    "g_endpoint_ratio": g_endpoint,
                    "g_transient_gain": g_transient,
                    "g_step_ratio": _summary(step_g_ratio),
                    "finite_horizon_g_log_growth_per_step": _summary(g_log_growth),
                    # Convenient scalar aliases for report/gate code.
                    "g_endpoint_ratio_median": g_endpoint["median"],
                    "g_endpoint_ratio_p95": g_endpoint["p95"],
                    "g_transient_gain_median": g_transient["median"],
                    "g_transient_gain_p95": g_transient["p95"],
                }
                by_depth[str(depth)] = record
    finally:
        model.train(was_training)

    return {
        "available": True,
        "family": family,
        "coordinate_split": coordinate_split,
        "requested_depths": list(requested),
        "neighbor_offsets": list(offsets),
        "evaluated_depths": list(evaluated),
        "by_depth": by_depth,
    }


def _geometry_record(
    spectral_radius: torch.Tensor,
    singular_values: torch.Tensor,
    isometry_defect: torch.Tensor,
) -> dict[str, Any]:
    spectral_summary = _summary(spectral_radius.cpu().tolist())
    defect_summary = _summary(isometry_defect.cpu().tolist())
    minimum_singular = _summary(singular_values.min(dim=1).values.cpu().tolist())
    maximum_singular = _summary(singular_values.max(dim=1).values.cpu().tolist())
    return {
        "spectral_radius": spectral_summary,
        "spectral_radius_mean": spectral_summary["mean"],
        "spectral_radius_p95": spectral_summary["p95"],
        "spectral_radius_maximum": spectral_summary["maximum"],
        "whitened_singular_values": _summary(singular_values.cpu().reshape(-1).tolist()),
        "whitened_singular_values_mean_by_rank": singular_values.mean(dim=0).cpu().tolist(),
        "whitened_minimum_singular_value": minimum_singular,
        "whitened_maximum_singular_value": maximum_singular,
        "normalized_g_isometry_defect": defect_summary,
        "normalized_g_isometry_defect_mean": defect_summary["mean"],
        "normalized_g_isometry_defect_p95": defect_summary["p95"],
    }


def operator_geometry_metrics(
    model: RecurrentOperatorModel,
    family: str,
    examples: int,
    batch_size: int,
    seed: int,
    device: torch.device | str,
    coordinate_split: str,
) -> dict[str, Any]:
    """Audit each visible operator without assigning it a canonical algebra label."""

    if not isinstance(model, RecurrentOperatorModel):
        return {"available": False, "reason": "model is nonrecurrent", "coordinate_split": coordinate_split}
    generator = _generator(seed, coordinate_split)
    device = torch.device(device)
    was_training = model.training
    model.eval()
    code_chunks: list[torch.Tensor] = []
    try:
        with torch.no_grad():
            for current_batch in _chunks(examples, batch_size):
                batch = generator.sample(current_batch, 0, family=family).to(device)
                codes = model.encode_operators(batch.tables)
                if codes.ndim != 4 or codes.shape[-1] != codes.shape[-2]:
                    return {
                        "available": False,
                        "reason": "operator codes are not square latent matrices",
                        "coordinate_split": coordinate_split,
                    }
                code_chunks.append(codes.detach())
            codes = torch.cat(code_chunks, dim=0)
            whitened = whiten_operators(model, codes)
            flat_codes = codes.reshape(-1, codes.shape[-1], codes.shape[-1]).double()
            flat_whitened = whitened.reshape(-1, whitened.shape[-1], whitened.shape[-1]).double()
            spectral = torch.linalg.eigvals(flat_codes).abs().amax(dim=1).real
            singular = torch.linalg.svdvals(flat_whitened)
            identity = torch.eye(flat_whitened.shape[-1], dtype=flat_whitened.dtype, device=device)
            gram_error = flat_whitened.transpose(-1, -2) @ flat_whitened - identity
            defect = torch.linalg.matrix_norm(gram_error, ord="fro", dim=(-2, -1)) / np.sqrt(
                flat_whitened.shape[-1]
            )

            per_visible_slot: dict[str, Any] = {}
            operators = codes.shape[1]
            spectral_by_example = spectral.reshape(codes.shape[0], operators)
            singular_by_example = singular.reshape(codes.shape[0], operators, -1)
            defect_by_example = defect.reshape(codes.shape[0], operators)
            for slot in range(operators):
                per_visible_slot[str(slot)] = _geometry_record(
                    spectral_by_example[:, slot],
                    singular_by_example[:, slot],
                    defect_by_example[:, slot],
                )
            aggregate = _geometry_record(spectral, singular, defect)
            metric = metric_diagnostics(model, codes.shape[-1], device, codes.dtype)
    finally:
        model.train(was_training)

    return {
        "available": True,
        "family": family,
        "coordinate_split": coordinate_split,
        "examples": int(codes.shape[0]),
        "operator_instances": int(codes.shape[0] * codes.shape[1]),
        "operator_dimension": int(codes.shape[-1]),
        "metric": metric,
        "aggregate": aggregate,
        "per_visible_slot": per_visible_slot,
    }


def anonymous_closure_loss(
    model: RecurrentOperatorModel,
    tables: torch.Tensor,
    first_slots: torch.Tensor | int,
    second_slots: torch.Tensor | int,
    eps: float = 1e-8,
    metric_aware: bool = True,
) -> torch.Tensor:
    """Differentiable anonymous composition residual.

    No canonical operator identities or relation words are used.  The directly
    encoded observable composite is compared with the correctly ordered product
    of the two latent matrices.  A terminal objective remains necessary to rule
    out a zero representation.
    """

    if not isinstance(model, RecurrentOperatorModel):
        raise TypeError("anonymous_closure_loss requires a recurrent operator model")
    if tables.ndim != 4 or tables.shape[-1] != tables.shape[-2]:
        raise ValueError("tables must have shape (batch, operators, states, states)")
    batch, operators = tables.shape[:2]
    first_slots = _slot_vector(first_slots, batch, tables.device)
    second_slots = _slot_vector(second_slots, batch, tables.device)
    if bool(((first_slots < 0) | (first_slots >= operators)).any()) or bool(
        ((second_slots < 0) | (second_slots >= operators)).any()
    ):
        raise ValueError("slot index out of range")
    first_table = _selected(tables, first_slots)
    second_table = _selected(tables, second_slots)
    composite_table = compose_action_tables(first_table, second_table)
    direct_tables = _replace_slot(tables, first_slots, composite_table)
    base_codes = model.encode_operators(tables)
    direct_codes = model.encode_operators(direct_tables)
    if (
        base_codes.ndim != 4
        or direct_codes.ndim != 4
        or base_codes.shape[-1] != base_codes.shape[-2]
        or direct_codes.shape != base_codes.shape
    ):
        raise TypeError("anonymous closure requires square matrix-valued operator codes")
    first_code = _selected(base_codes, first_slots)
    second_code = _selected(base_codes, second_slots)
    expected_code = compose_latent_matrices(first_code, second_code)
    direct_code = _selected(direct_codes, first_slots)
    difference = direct_code - expected_code
    if metric_aware:
        difference = whiten_operators(model, difference)
        expected_code = whiten_operators(model, expected_code)
    numerator = difference.square().flatten(1).sum(dim=1)
    scale = expected_code.square().flatten(1).sum(dim=1).detach().clamp_min(eps)
    return (numerator / scale).mean()


def _maps_to_tables(maps: torch.Tensor, dtype: torch.dtype) -> torch.Tensor:
    return F.one_hot(maps, num_classes=N_STATES).to(dtype=dtype)


def _compose_maps(first: torch.Tensor, second: torch.Tensor) -> torch.Tensor:
    """Return ``second(first(x))`` for batched observable integer maps."""

    return torch.gather(second, 1, first)


def _conditional_fraction(mask: torch.Tensor, successes: torch.Tensor) -> float | None:
    count = int(mask.sum())
    return float(successes[mask].float().mean()) if count else None


def _g_cosine(model: RecurrentOperatorModel, left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
    g = _metric_matrix(model, left.shape[-1], left.device, left.dtype)
    numerator = torch.einsum("bi,ij,bj->b", left, g, right)
    denominator = latent_g_norm(model, left) * latent_g_norm(model, right)
    return (numerator / denominator.clamp_min(torch.finfo(left.dtype).eps)).clamp(-1, 1)


def anonymous_composition_metrics(
    model: RecurrentOperatorModel,
    family: str,
    examples: int,
    batch_size: int,
    seed: int,
    device: torch.device | str,
    coordinate_split: str,
) -> dict[str, Any]:
    """Test direct composed-table substitution against reversed and wrong tables."""

    if not isinstance(model, RecurrentOperatorModel):
        return {"available": False, "reason": "model is nonrecurrent", "coordinate_split": coordinate_split}
    if N_OPERATORS < 2:
        return {"available": False, "reason": "at least two visible slots are required"}
    generator = _generator(seed, coordinate_split)
    device = torch.device(device)
    torch_rng = torch.Generator(device=device).manual_seed(seed + 91_177)
    counts = {
        "native_two_step": 0,
        "true_substitution": 0,
        "true_output_agreement": 0,
        "reversed_against_true": 0,
        "reversed_self": 0,
        "wrong_against_true": 0,
        "wrong_self": 0,
    }
    reverse_distinguishing = 0
    reverse_distinguishing_success = 0
    wrong_distinguishing = 0
    wrong_distinguishing_success = 0
    hidden_distance: list[float] = []
    hidden_cosine: list[float] = []
    ambient_residual: list[float] = []
    metric_residual: list[float] = []
    total = 0
    was_training = model.training
    model.eval()
    try:
        with torch.no_grad():
            for current_batch in _chunks(examples, batch_size):
                batch = generator.sample(current_batch, 0, family=family).to(device)
                rows = torch.arange(current_batch, device=device)
                first_slots = torch.randint(
                    0, N_OPERATORS, (current_batch,), generator=torch_rng, device=device
                )
                # With two slots this deterministically chooses the other anonymous table.
                second_slots = 1 - first_slots
                first_map = batch.maps[rows, first_slots]
                second_map = batch.maps[rows, second_slots]
                true_map = _compose_maps(first_map, second_map)
                reverse_map = _compose_maps(second_map, first_map)

                # A composite from another observed context is an on-manifold wrong table.
                # If it happens to coincide, a domain roll preserves permutation validity
                # and guarantees a different observable map without a canonical label.
                wrong_map = torch.roll(true_map, shifts=1, dims=0)
                collision = (wrong_map == true_map).all(dim=1)
                if bool(collision.any()):
                    wrong_map[collision] = torch.roll(true_map[collision], shifts=1, dims=1)
                # A different permutation can still agree at the sampled start.
                # Replace those rows with a domain roll so the wrong-table control
                # is behaviorally distinguishing for every evaluated example.
                true_at_start = true_map[rows, batch.start]
                wrong_at_start = wrong_map[rows, batch.start]
                endpoint_collision = wrong_at_start == true_at_start
                if bool(endpoint_collision.any()):
                    wrong_map[endpoint_collision] = torch.roll(
                        true_map[endpoint_collision], shifts=1, dims=1
                    )

                true_tables = _replace_slot(
                    batch.tables, first_slots, _maps_to_tables(true_map, batch.tables.dtype)
                )
                reverse_tables = _replace_slot(
                    batch.tables, first_slots, _maps_to_tables(reverse_map, batch.tables.dtype)
                )
                wrong_tables = _replace_slot(
                    batch.tables, first_slots, _maps_to_tables(wrong_map, batch.tables.dtype)
                )
                word = torch.stack((first_slots, second_slots), dim=1)
                one_step = first_slots[:, None]
                native = model.run(batch.tables, word, batch.start)
                true_direct = model.run(true_tables, one_step, batch.start)
                reversed_direct = model.run(reverse_tables, one_step, batch.start)
                wrong_direct = model.run(wrong_tables, one_step, batch.start)

                true_target = true_map[rows, batch.start]
                reverse_target = reverse_map[rows, batch.start]
                wrong_target = wrong_map[rows, batch.start]
                native_prediction = native.logits.argmax(dim=1)
                true_prediction = true_direct.logits.argmax(dim=1)
                reverse_prediction = reversed_direct.logits.argmax(dim=1)
                wrong_prediction = wrong_direct.logits.argmax(dim=1)
                counts["native_two_step"] += int((native_prediction == true_target).sum())
                counts["true_substitution"] += int((true_prediction == true_target).sum())
                counts["true_output_agreement"] += int((true_prediction == native_prediction).sum())
                counts["reversed_against_true"] += int((reverse_prediction == true_target).sum())
                counts["reversed_self"] += int((reverse_prediction == reverse_target).sum())
                counts["wrong_against_true"] += int((wrong_prediction == true_target).sum())
                counts["wrong_self"] += int((wrong_prediction == wrong_target).sum())

                reverse_mask = reverse_target != true_target
                wrong_mask = wrong_target != true_target
                reverse_distinguishing += int(reverse_mask.sum())
                wrong_distinguishing += int(wrong_mask.sum())
                reverse_distinguishing_success += int(
                    ((reverse_prediction == true_target) & reverse_mask).sum()
                )
                wrong_distinguishing_success += int(((wrong_prediction == true_target) & wrong_mask).sum())

                native_hidden = native.hidden[-1]
                direct_hidden = true_direct.hidden[-1]
                difference = native_hidden - direct_hidden
                scale = latent_g_norm(model, native_hidden).clamp_min(
                    torch.finfo(native_hidden.dtype).eps
                )
                hidden_distance.extend((latent_g_norm(model, difference) / scale).cpu().tolist())
                hidden_cosine.extend(_g_cosine(model, native_hidden, direct_hidden).cpu().tolist())

                base_codes = native.operator_codes
                direct_codes = true_direct.operator_codes
                if (
                    base_codes is not None
                    and direct_codes is not None
                    and base_codes.ndim == 4
                    and direct_codes.shape == base_codes.shape
                    and base_codes.shape[-1] == base_codes.shape[-2]
                ):
                    first_code = base_codes[rows, first_slots]
                    second_code = base_codes[rows, second_slots]
                    product = compose_latent_matrices(first_code, second_code)
                    encoded_composite = direct_codes[rows, first_slots]
                    delta = encoded_composite - product
                    denominator = product.flatten(1).norm(dim=1).clamp_min(1e-8)
                    ambient_residual.extend((delta.flatten(1).norm(dim=1) / denominator).cpu().tolist())
                    white_delta = whiten_operators(model, delta)
                    white_product = whiten_operators(model, product)
                    white_denominator = white_product.flatten(1).norm(dim=1).clamp_min(1e-8)
                    metric_residual.extend(
                        (white_delta.flatten(1).norm(dim=1) / white_denominator).cpu().tolist()
                    )
                total += current_batch
    finally:
        model.train(was_training)

    return {
        "available": True,
        "family": family,
        "coordinate_split": coordinate_split,
        "examples": total,
        "native_two_step_accuracy": counts["native_two_step"] / total,
        "true_substitution_accuracy": counts["true_substitution"] / total,
        "true_substitution_output_agreement": counts["true_output_agreement"] / total,
        "reversed_control_accuracy_against_true": counts["reversed_against_true"] / total,
        "reversed_control_self_accuracy": counts["reversed_self"] / total,
        "wrong_control_accuracy_against_true": counts["wrong_against_true"] / total,
        "wrong_control_self_accuracy": counts["wrong_self"] / total,
        "reversed_distinguishing_fraction": reverse_distinguishing / total,
        "reversed_accuracy_on_distinguishing_examples": (
            reverse_distinguishing_success / reverse_distinguishing if reverse_distinguishing else None
        ),
        "wrong_distinguishing_fraction": wrong_distinguishing / total,
        "wrong_accuracy_on_distinguishing_examples": (
            wrong_distinguishing_success / wrong_distinguishing if wrong_distinguishing else None
        ),
        "true_hidden_normalized_g_distance": _summary(hidden_distance),
        "true_hidden_g_cosine": _summary(hidden_cosine),
        "ambient_operator_closure_residual": _summary(ambient_residual) if ambient_residual else None,
        "metric_operator_closure_residual": _summary(metric_residual) if metric_residual else None,
    }


def _sample_distinct_contexts(
    donor_generator: EpisodeGenerator,
    recipient_generator: EpisodeGenerator,
    batch_size: int,
    prefix_length: int,
    suffix_length: int,
    donor_family: str,
    recipient_family: str,
    device: torch.device,
) -> tuple[EpisodeBatch, EpisodeBatch]:
    donor = donor_generator.sample(batch_size, prefix_length, family=donor_family).to(device)
    # Paired contexts, not merely independent random calls, must be observably distinct.
    for _ in range(128):
        recipient = recipient_generator.sample(batch_size, suffix_length, family=recipient_family).to(device)
        equal = (donor.maps == recipient.maps).all(dim=(1, 2))
        if not bool(equal.any()):
            return donor, recipient
    raise RuntimeError("could not sample pairwise-distinct operator contexts")


def cross_context_state_patch_metrics(
    model: RecurrentOperatorModel,
    examples: int,
    batch_size: int,
    seed: int,
    device: torch.device | str,
    coordinate_split: str,
    prefix_length: int = 4,
    suffix_length: int = 8,
    donor_family: str = "random",
    recipient_family: str = "random",
) -> dict[str, Any]:
    """Patch a state between distinct table contexts and continue in the recipient.

    The matched wrong control is another genuine trajectory state from the same
    donor context, produced from a different start.  It is therefore on manifold
    and differs only in its causal state content, rather than in vector norm or
    realism.
    """

    if not isinstance(model, RecurrentOperatorModel):
        return {"available": False, "reason": "model is nonrecurrent", "coordinate_split": coordinate_split}
    if prefix_length < 0 or suffix_length < 0:
        raise ValueError("prefix_length and suffix_length must be nonnegative")
    donor_generator = _generator(seed, coordinate_split)
    recipient_generator = _generator(seed + 1_000_003, coordinate_split)
    device = torch.device(device)
    torch_rng = torch.Generator(device=device).manual_seed(seed + 313_337)
    counts = {
        "donor_prefix": 0,
        "recipient_native": 0,
        "reencoded_state": 0,
        "cross_context_patch": 0,
        "wrong_on_manifold": 0,
    }
    table_distinct = 0
    state_distinct = 0
    hidden_distance: list[float] = []
    hidden_cosine: list[float] = []
    total = 0
    was_training = model.training
    model.eval()
    try:
        with torch.no_grad():
            for current_batch in _chunks(examples, batch_size):
                donor, recipient = _sample_distinct_contexts(
                    donor_generator,
                    recipient_generator,
                    current_batch,
                    prefix_length,
                    suffix_length,
                    donor_family,
                    recipient_family,
                    device,
                )
                distinct = ~(donor.maps == recipient.maps).all(dim=(1, 2))
                table_distinct += int(distinct.sum())

                donor_trace = model.run(donor.tables, donor.op_slots, donor.start)
                donor_midpoint = _apply_maps(donor.maps, donor.start, donor.op_slots)
                counts["donor_prefix"] += int((donor_trace.logits.argmax(dim=1) == donor_midpoint).sum())

                offsets = torch.randint(
                    1, N_STATES, (current_batch,), generator=torch_rng, device=device
                )
                wrong_start = (donor.start + offsets) % N_STATES
                wrong_trace = model.run(donor.tables, donor.op_slots, wrong_start)
                wrong_midpoint = _apply_maps(donor.maps, wrong_start, donor.op_slots)
                state_distinct += int((wrong_midpoint != donor_midpoint).sum())

                recipient_codes = model.encode_operators(recipient.tables)
                patched = model.continue_from_hidden(
                    donor_trace.hidden[-1], recipient_codes, recipient.op_slots
                )
                wrong_patched = model.continue_from_hidden(
                    wrong_trace.hidden[-1], recipient_codes, recipient.op_slots
                )
                expected = _apply_maps(recipient.maps, donor_midpoint, recipient.op_slots)
                counts["cross_context_patch"] += int((patched.logits.argmax(dim=1) == expected).sum())
                counts["wrong_on_manifold"] += int(
                    (wrong_patched.logits.argmax(dim=1) == expected).sum()
                )

                reencoded_hidden = model.initial_hidden(donor_midpoint)
                reencoded = model.continue_from_hidden(
                    reencoded_hidden, recipient_codes, recipient.op_slots
                )
                counts["reencoded_state"] += int((reencoded.logits.argmax(dim=1) == expected).sum())

                recipient_native = model.run(recipient.tables, recipient.op_slots, recipient.start)
                counts["recipient_native"] += int(
                    (recipient_native.logits.argmax(dim=1) == recipient.target).sum()
                )

                delta = donor_trace.hidden[-1] - reencoded_hidden
                denominator = latent_g_norm(model, reencoded_hidden).clamp_min(
                    torch.finfo(reencoded_hidden.dtype).eps
                )
                hidden_distance.extend((latent_g_norm(model, delta) / denominator).cpu().tolist())
                hidden_cosine.extend(
                    _g_cosine(model, donor_trace.hidden[-1], reencoded_hidden).cpu().tolist()
                )
                total += current_batch
    finally:
        model.train(was_training)

    patch_accuracy = counts["cross_context_patch"] / total
    wrong_accuracy = counts["wrong_on_manifold"] / total
    return {
        "available": True,
        "coordinate_split": coordinate_split,
        "examples": total,
        "prefix_length": prefix_length,
        "suffix_length": suffix_length,
        "donor_family": donor_family,
        "recipient_family": recipient_family,
        "distinct_operator_context_fraction": table_distinct / total,
        "distinct_wrong_state_fraction": state_distinct / total,
        "donor_prefix_accuracy": counts["donor_prefix"] / total,
        "recipient_native_accuracy": counts["recipient_native"] / total,
        "reencoded_state_continuation_accuracy": counts["reencoded_state"] / total,
        "cross_context_state_patch_accuracy": patch_accuracy,
        "on_manifold_wrong_state_control_accuracy": wrong_accuracy,
        "cross_context_patch_margin": patch_accuracy - wrong_accuracy,
        "donor_vs_reencoded_hidden_normalized_g_distance": _summary(hidden_distance),
        "donor_vs_reencoded_hidden_g_cosine": _summary(hidden_cosine),
    }


def full_closure_evaluation(
    model: RecurrentOperatorModel,
    config: ClosureEvaluationConfig,
    seed: int,
    device: torch.device | str,
) -> dict[str, Any]:
    """Run the complete v0.2 closure and stability evaluation battery."""

    split = config.coordinate_split
    return {
        "coordinate_split": split,
        "deep_stability": deep_accuracy_stability(
            model,
            family="d4",
            depths=config.depths,
            examples_per_depth=config.examples,
            batch_size=config.batch_size,
            seed=seed,
            device=device,
            coordinate_split=split,
            neighbor_offsets=config.neighbor_offsets,
        ),
        "operator_geometry": operator_geometry_metrics(
            model,
            family="d4",
            examples=config.geometry_examples,
            batch_size=config.batch_size,
            seed=seed + 10_000,
            device=device,
            coordinate_split=split,
        ),
        "anonymous_composition": anonymous_composition_metrics(
            model,
            family=config.composition_family,
            examples=config.composition_examples,
            batch_size=config.batch_size,
            seed=seed + 20_000,
            device=device,
            coordinate_split=split,
        ),
        "cross_context_patch": cross_context_state_patch_metrics(
            model,
            examples=config.patch_examples,
            batch_size=config.batch_size,
            seed=seed + 30_000,
            device=device,
            coordinate_split=split,
            prefix_length=config.patch_prefix_length,
            suffix_length=config.patch_suffix_length,
            donor_family=config.patch_donor_family,
            recipient_family=config.patch_recipient_family,
        ),
    }
