from __future__ import annotations

from dataclasses import dataclass
import hashlib
from itertools import product
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import torch

from .algebra import D4_RELATIONS, N_STATES
from .ambient_packets import (
    build_continuation_constraints,
    continuation_margins,
    oriented_projective_distance,
)
from .data import EpisodeBatch, EpisodeGenerator
from .gauge import column_permutation_matrix, decompose_operator_gauge
from .stability import anchor_basis, anchor_metric, future_observability
from .stable_models import ProjectiveLinearHyperOperatorRNN
from .switched_stability import (
    nonnormal_switched_counterexample,
    normalized_decoder_margin,
    normalized_projective_map,
    projective_sequence_jacobian,
)


FAMILY_TO_GENERATOR = {
    "d4": "d4",
    "c8": "c8",
    "mixed_cycle": "mixed_cycle",
    "random_permutation_pairs": "random",
}


class AssayIntegrityError(RuntimeError):
    """Raised when an input or harness contract is invalid."""


@dataclass(frozen=True)
class LoadedProjectiveCheckpoint:
    seed: int
    model: ProjectiveLinearHyperOperatorRNN
    receipt: dict[str, Any]


@dataclass(frozen=True)
class TrajectoryCapture:
    visible_codes: torch.Tensor
    canonical_codes: torch.Tensor
    canonical_transitions: torch.Tensor
    hidden_by_prefix: dict[int, torch.Tensor]
    exact_state_by_prefix: dict[int, torch.Tensor]
    minimum_preimage_norm: float
    finite_preimage_fraction: float


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_projective_checkpoint(
    checkpoint_path: Path,
    *,
    seed: int,
    expected_sha256: str,
    expected_config: Mapping[str, Any],
    device: torch.device | str = "cpu",
) -> LoadedProjectiveCheckpoint:
    checkpoint_path = checkpoint_path.resolve()
    if not checkpoint_path.is_file():
        raise AssayIntegrityError(f"missing checkpoint: {checkpoint_path}")
    observed_sha = file_sha256(checkpoint_path)
    if observed_sha != expected_sha256:
        raise AssayIntegrityError(
            f"checkpoint SHA-256 mismatch for seed {seed}: {observed_sha} != {expected_sha256}"
        )
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    expected_fields = {"schema", "source_digest", "config", "state_dict"}
    if set(payload) != expected_fields:
        raise AssayIntegrityError(
            f"unexpected checkpoint fields for seed {seed}: {sorted(payload)}"
        )
    if payload["schema"] != "komorebi.neuralese.projective_checkpoint.v1":
        raise AssayIntegrityError(f"checkpoint schema mismatch for seed {seed}")
    if payload["config"] != dict(expected_config):
        raise AssayIntegrityError(f"checkpoint/result config mismatch for seed {seed}")
    if payload["config"].get("model_name") != "projective_linear_hyper":
        raise AssayIntegrityError(f"seed {seed} is not a projective checkpoint")
    if int(payload["config"].get("seed", -1)) != int(seed):
        raise AssayIntegrityError(f"checkpoint seed mismatch for seed {seed}")

    state_dict = payload["state_dict"]
    required_tensors = {
        "state_embedding.weight": (N_STATES, N_STATES),
        "operator_encoder.weight": (N_STATES * N_STATES, N_STATES * N_STATES),
        "decoder.weight": (N_STATES, N_STATES),
    }
    if set(state_dict) != set(required_tensors):
        raise AssayIntegrityError(f"unexpected state_dict fields for seed {seed}")
    for name, shape in required_tensors.items():
        if tuple(state_dict[name].shape) != shape or not torch.isfinite(state_dict[name]).all():
            raise AssayIntegrityError(f"invalid checkpoint tensor {name} for seed {seed}")

    model = ProjectiveLinearHyperOperatorRNN(hidden_dim=N_STATES)
    model.load_state_dict(state_dict, strict=True)
    model.to(device).eval().requires_grad_(False)
    receipt = {
        "seed": int(seed),
        "path": checkpoint_path.as_posix(),
        "sha256": observed_sha,
        "schema": payload["schema"],
        "training_source_digest": payload["source_digest"],
        "config": payload["config"],
        "model_class": type(model).__name__,
    }
    return LoadedProjectiveCheckpoint(seed=int(seed), model=model, receipt=receipt)


def load_projective_pilot_models(
    root: Path,
    seeds: Iterable[int],
    device: torch.device | str = "cpu",
) -> dict[int, LoadedProjectiveCheckpoint]:
    result_path = root / "results" / "projective_pilot" / "RESULTS.json"
    if not result_path.is_file():
        raise AssayIntegrityError(f"missing projective result index: {result_path}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("schema") != "komorebi.neuralese.projective_training.result.v1":
        raise AssayIntegrityError("projective result index schema mismatch")
    loaded: dict[int, LoadedProjectiveCheckpoint] = {}
    for seed in seeds:
        record = result.get("records", {}).get(str(seed), {}).get("projective")
        if not isinstance(record, dict):
            raise AssayIntegrityError(f"missing projective result record for seed {seed}")
        checkpoint = record.get("checkpoint", {})
        training = record.get("training", {})
        config = training.get("config")
        if not isinstance(config, dict):
            raise AssayIntegrityError(f"missing training config for seed {seed}")
        if checkpoint.get("schema") != "komorebi.neuralese.projective_checkpoint.v1":
            raise AssayIntegrityError(f"checkpoint receipt schema mismatch for seed {seed}")
        relative = checkpoint.get("path")
        expected_sha = checkpoint.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected_sha, str):
            raise AssayIntegrityError(f"invalid checkpoint receipt for seed {seed}")
        path = (root / relative).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError as error:
            raise AssayIntegrityError("checkpoint path escapes package root") from error
        item = load_projective_checkpoint(
            path,
            seed=int(seed),
            expected_sha256=expected_sha,
            expected_config=config,
            device=device,
        )
        indexed_training_digest = checkpoint.get("training_source_digest")
        recorded_training_digest = training.get("training_source_digest")
        payload_training_digest = item.receipt["training_source_digest"]
        if not (
            isinstance(indexed_training_digest, str)
            and indexed_training_digest == recorded_training_digest
            and indexed_training_digest == payload_training_digest
        ):
            raise AssayIntegrityError(f"training source digest mismatch for seed {seed}")
        portable_receipt = dict(item.receipt)
        portable_receipt["path"] = relative
        loaded[int(seed)] = LoadedProjectiveCheckpoint(
            seed=item.seed,
            model=item.model,
            receipt=portable_receipt,
        )
    return loaded


def make_episode_bank(
    *,
    contexts: int,
    length: int,
    family: str,
    seed: int,
) -> EpisodeBatch:
    if family not in FAMILY_TO_GENERATOR:
        raise ValueError(f"unknown external family: {family}")
    if contexts < 1 or length < 0:
        raise ValueError("contexts must be positive and length nonnegative")

    # A context is generated exactly once from its tuple address. Words and starts
    # use separate tuple addresses, so changing iteration or execution batching
    # cannot silently change the operator system.
    context_rows: list[EpisodeBatch] = []
    for context_index in range(int(contexts)):
        context_seed = derive_seed(seed, "context", family, context_index)
        context = EpisodeGenerator(context_seed).sample(
            1, 0, family=FAMILY_TO_GENERATOR[family]
        )
        word_rng = np.random.default_rng(derive_seed(seed, "word", family, context_index, length))
        start_rng = np.random.default_rng(derive_seed(seed, "start", family, context_index))
        canonical_ops = word_rng.integers(0, 2, size=(1, length), dtype=np.int64)
        canonical_ops_tensor = torch.from_numpy(canonical_ops)
        op_slots = torch.gather(context.canonical_to_slot, 1, canonical_ops_tensor)
        start = torch.from_numpy(start_rng.integers(0, N_STATES, size=1, dtype=np.int64))
        current = start.clone()
        intermediates = torch.empty((1, length), dtype=torch.long)
        rows = torch.arange(1)
        for step in range(length):
            selected = context.maps[rows, op_slots[:, step]]
            current = selected[rows, current]
            intermediates[:, step] = current
        context_rows.append(
            EpisodeBatch(
                tables=context.tables,
                maps=context.maps,
                op_slots=op_slots,
                canonical_ops=canonical_ops_tensor,
                start=start,
                target=current,
                intermediates=intermediates,
                canonical_to_slot=context.canonical_to_slot,
                phi=context.phi,
                family=context.family,
            )
        )

    return EpisodeBatch(
        tables=torch.cat([row.tables for row in context_rows], dim=0),
        maps=torch.cat([row.maps for row in context_rows], dim=0),
        op_slots=torch.cat([row.op_slots for row in context_rows], dim=0),
        canonical_ops=torch.cat([row.canonical_ops for row in context_rows], dim=0),
        start=torch.cat([row.start for row in context_rows], dim=0),
        target=torch.cat([row.target for row in context_rows], dim=0),
        intermediates=torch.cat([row.intermediates for row in context_rows], dim=0),
        canonical_to_slot=torch.cat([row.canonical_to_slot for row in context_rows], dim=0),
        phi=torch.cat([row.phi for row in context_rows], dim=0),
        family=FAMILY_TO_GENERATOR[family],
    )


def derive_seed(base_seed: int, *parts: object) -> int:
    payload = json.dumps(
        [int(base_seed), *[str(part) for part in parts]],
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little", signed=False)


def episode_contract(batch: EpisodeBatch) -> dict[str, Any]:
    rows = torch.arange(batch.start.shape[0])
    current = batch.start.clone()
    intermediate_ok = True
    for step in range(batch.op_slots.shape[1]):
        selected = batch.maps[rows, batch.op_slots[:, step]]
        current = selected[rows, current]
        intermediate_ok = intermediate_ok and torch.equal(current, batch.intermediates[:, step])
    mapped_slots = torch.gather(batch.canonical_to_slot, 1, batch.canonical_ops)
    return {
        "intermediates_exact": bool(intermediate_ok),
        "target_exact": bool(torch.equal(current, batch.target)),
        "canonical_visible_slots_exact": bool(torch.equal(mapped_slots, batch.op_slots)),
        "contexts": int(batch.start.shape[0]),
        "length": int(batch.op_slots.shape[1]),
    }


def canonicalize_actions(
    visible_codes: torch.Tensor,
    maps: torch.Tensor,
    canonical_to_slot: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    if visible_codes.ndim != 4 or maps.ndim != 3 or canonical_to_slot.ndim != 2:
        raise ValueError("invalid action tensors")
    code_index = canonical_to_slot[..., None, None].expand(
        -1, -1, visible_codes.shape[-2], visible_codes.shape[-1]
    )
    map_index = canonical_to_slot[..., None].expand(-1, -1, maps.shape[-1])
    return (
        torch.gather(visible_codes, 1, code_index),
        torch.gather(maps, 1, map_index),
    )


def capture_trajectory(
    model: ProjectiveLinearHyperOperatorRNN,
    batch: EpisodeBatch,
    prefixes: Iterable[int],
) -> TrajectoryCapture:
    requested = tuple(sorted(set(int(value) for value in prefixes)))
    if not requested or requested[0] < 0 or requested[-1] > batch.op_slots.shape[1]:
        raise ValueError("prefixes must lie inside the episode length")
    device = next(model.parameters()).device
    working = batch.to(device)
    with torch.inference_mode():
        visible_codes = model.encode_operators(working.tables)
        canonical_codes, canonical_transitions = canonicalize_actions(
            visible_codes, working.maps, working.canonical_to_slot
        )
        hidden = model.initial_hidden(working.start)
        hidden_by_prefix: dict[int, torch.Tensor] = {}
        if 0 in requested:
            hidden_by_prefix[0] = hidden.detach().cpu()
        rows = torch.arange(working.start.shape[0], device=device)
        preimage_norms: list[torch.Tensor] = []
        for step in range(working.op_slots.shape[1]):
            selected = visible_codes[rows, working.op_slots[:, step]]
            preimage = torch.bmm(selected, hidden.unsqueeze(-1)).squeeze(-1)
            preimage_norms.append(torch.linalg.vector_norm(preimage, dim=1).detach().cpu())
            hidden = model.step_hidden(hidden, selected)
            depth = step + 1
            if depth in requested:
                hidden_by_prefix[depth] = hidden.detach().cpu()
    joined = torch.cat(preimage_norms) if preimage_norms else torch.empty(0)
    finite = torch.isfinite(joined)
    minimum = float(joined[finite].min()) if finite.any() else 0.0
    exact = {
        depth: (
            batch.start.detach().cpu()
            if depth == 0
            else batch.intermediates[:, depth - 1].detach().cpu()
        )
        for depth in requested
    }
    return TrajectoryCapture(
        visible_codes=visible_codes.detach().cpu(),
        canonical_codes=canonical_codes.detach().cpu(),
        canonical_transitions=canonical_transitions.detach().cpu(),
        hidden_by_prefix=hidden_by_prefix,
        exact_state_by_prefix=exact,
        minimum_preimage_norm=minimum,
        finite_preimage_fraction=float(finite.to(torch.float64).mean()) if joined.numel() else 1.0,
    )


def _finite_values(values: torch.Tensor | Iterable[float]) -> torch.Tensor:
    value = values.detach().to(torch.float64).flatten() if isinstance(values, torch.Tensor) else torch.tensor(list(values), dtype=torch.float64)
    return value[torch.isfinite(value)]


def numeric_summary(values: torch.Tensor | Iterable[float]) -> dict[str, Any]:
    finite = _finite_values(values)
    if not finite.numel():
        return {"count": 0, "minimum": None, "p10": None, "median": None, "maximum": None}
    return {
        "count": int(finite.numel()),
        "minimum": float(finite.min()),
        "p10": float(torch.quantile(finite, 0.10)),
        "median": float(torch.median(finite)),
        "maximum": float(finite.max()),
    }


def tensor_receipt(tensor: torch.Tensor) -> dict[str, Any]:
    value = tensor.detach().cpu().contiguous()
    payload = value.numpy().tobytes(order="C")
    return {
        "shape": list(value.shape),
        "dtype": str(value.dtype).removeprefix("torch."),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def episode_bank_receipts(batch: EpisodeBatch) -> dict[str, Any]:
    fields = (
        "tables",
        "maps",
        "op_slots",
        "canonical_ops",
        "start",
        "target",
        "intermediates",
        "canonical_to_slot",
        "phi",
    )
    return {
        "family": batch.family,
        "tensors": {name: tensor_receipt(getattr(batch, name)) for name in fields},
    }


def trajectory_tensor_receipts(
    model: ProjectiveLinearHyperOperatorRNN,
    capture: TrajectoryCapture,
) -> dict[str, Any]:
    return {
        "decoder_weight": tensor_receipt(model.decoder.weight),
        "state_embedding": tensor_receipt(model.state_embedding.weight),
        "canonical_codes": tensor_receipt(capture.canonical_codes),
        "canonical_transitions": tensor_receipt(capture.canonical_transitions),
        "hidden_by_prefix": {
            str(depth): tensor_receipt(hidden)
            for depth, hidden in sorted(capture.hidden_by_prefix.items())
        },
        "exact_state_by_prefix": {
            str(depth): tensor_receipt(state)
            for depth, state in sorted(capture.exact_state_by_prefix.items())
        },
    }


def family_rollout_metrics(
    model: ProjectiveLinearHyperOperatorRNN,
    batch: EpisodeBatch,
    prefixes: Iterable[int],
) -> tuple[dict[str, Any], TrajectoryCapture]:
    capture = capture_trajectory(model, batch, prefixes)
    decoder = model.decoder.weight.detach().cpu()
    output: dict[str, Any] = {}
    for depth in sorted(capture.hidden_by_prefix):
        hidden = capture.hidden_by_prefix[depth]
        finite = torch.isfinite(hidden).all(dim=1)
        prediction = (hidden @ decoder.transpose(0, 1)).argmax(dim=1)
        target = capture.exact_state_by_prefix[depth]
        output[str(depth)] = {
            "accuracy": float(((prediction == target) & finite).to(torch.float64).mean()),
            "finite_fraction": float(finite.to(torch.float64).mean()),
            "examples": int(hidden.shape[0]),
        }
    output["domain"] = {
        "minimum_pre_normalization_l2": capture.minimum_preimage_norm,
        "finite_preimage_fraction": capture.finite_preimage_fraction,
    }
    return output, capture


def learned_gauge_diagnostic(
    model: ProjectiveLinearHyperOperatorRNN,
    capture: TrajectoryCapture,
) -> dict[str, Any]:
    basis = anchor_basis(model).detach().cpu().to(torch.float64)
    codes = capture.canonical_codes.to(torch.float64)
    transitions = capture.canonical_transitions
    fit = decompose_operator_gauge(basis, codes, transitions)
    statewise = fit.statewise_relative_residual
    global_value = fit.global_relative_residual
    improvement = global_value - statewise
    return {
        "projectively_valid_fraction": float(fit.projectively_valid.to(torch.float64).mean()),
        "statewise_relative_residual": numeric_summary(statewise),
        "global_relative_residual": numeric_summary(global_value),
        "ambient_statewise_relative_residual": numeric_summary(
            fit.ambient_statewise_relative_residual
        ),
        "ambient_global_relative_residual": numeric_summary(
            fit.ambient_global_relative_residual
        ),
        "statewise_improvement": numeric_summary(improvement),
        "statewise_better_fraction": float((statewise < global_value).to(torch.float64).mean()),
        "positive_scale": numeric_summary(fit.raw_state_scales[fit.projectively_valid]),
    }


def gauge_synthetic_controls() -> dict[str, Any]:
    dtype = torch.float64
    basis = torch.eye(4, dtype=dtype)
    maps = torch.tensor([[1, 2, 3, 0], [0, 3, 2, 1]], dtype=torch.long)
    permutations = column_permutation_matrix(maps, dtype=dtype)
    exact = decompose_operator_gauge(basis, permutations, maps)

    state_scales = torch.tensor(
        [[0.5, 1.0, 2.0, 4.0], [1.25, 0.75, 3.0, 1.5]], dtype=dtype
    )
    statewise_operators = permutations @ torch.diag_embed(state_scales)
    statewise = decompose_operator_gauge(basis, statewise_operators, maps)

    negative_scales = state_scales.clone()
    negative_scales[0, 1] = -negative_scales[0, 1]
    negative = decompose_operator_gauge(
        basis, permutations @ torch.diag_embed(negative_scales), maps
    )

    leakage_operators = statewise_operators.clone()
    leakage_operators[0, 0, 0] += 0.20
    leakage = decompose_operator_gauge(basis, leakage_operators, maps)
    reconstruction = leakage.ambient_skeleton + leakage.ambient_leakage
    reconstruction_error = torch.linalg.matrix_norm(
        reconstruction - leakage_operators, ord="fro", dim=(-2, -1)
    ).max()

    return {
        "exact_global": {
            "statewise_residual_max": float(exact.statewise_relative_residual.max()),
            "global_residual_max": float(exact.global_relative_residual.max()),
            "all_positive": bool(exact.projectively_valid.all()),
        },
        "exact_statewise": {
            "statewise_residual_max": float(statewise.statewise_relative_residual.max()),
            "global_residual_min": float(statewise.global_relative_residual.min()),
            "statewise_beats_global": bool(
                torch.all(statewise.statewise_relative_residual < statewise.global_relative_residual)
            ),
            "all_positive": bool(statewise.projectively_valid.all()),
        },
        "negative_scale": {
            "invalid_coefficients": int((~negative.projectively_valid).sum()),
            "raw_minimum_scale": float(negative.raw_state_scales.min()),
        },
        "leakage": {
            "statewise_residual_max": float(leakage.statewise_relative_residual.max()),
            "reconstruction_error_max": float(reconstruction_error),
        },
    }


def packet_audit(
    model: ProjectiveLinearHyperOperatorRNN,
    capture: TrajectoryCapture,
    *,
    prefixes: Iterable[int],
    horizon: int,
) -> dict[str, Any]:
    decoder = model.decoder.weight.detach().cpu().to(torch.float64)
    metric = anchor_metric(model, normalize_trace=False).detach().cpu().to(torch.float64)
    codes = capture.canonical_codes.to(torch.float64)
    transitions = capture.canonical_transitions
    cache: dict[tuple[int, int], Any] = {}
    output: dict[str, Any] = {}
    expected_constraints = (2 ** (horizon + 1) - 1) * (N_STATES - 1)
    for depth in sorted(set(int(value) for value in prefixes)):
        margins: list[float] = []
        inside: list[bool] = []
        hidden = capture.hidden_by_prefix[depth].to(torch.float64)
        source = capture.exact_state_by_prefix[depth]
        prediction = (hidden @ decoder.transpose(0, 1)).argmax(dim=1)
        for episode in range(hidden.shape[0]):
            state_index = int(source[episode])
            key = (episode, state_index)
            if key not in cache:
                cache[key] = build_continuation_constraints(
                    decoder,
                    codes[episode],
                    transitions[episode],
                    state_index,
                    max_depth=horizon,
                )
            result = continuation_margins(hidden[episode : episode + 1], cache[key], metric)
            margins.append(float(result.minimum_margin[0]))
            inside.append(bool(result.inside[0]))
        output[str(depth)] = {
            "membership_fraction": sum(inside) / len(inside),
            "current_accuracy": float((prediction == source).to(torch.float64).mean()),
            "margin": numeric_summary(margins),
            "examples": len(inside),
            "constraints_per_packet": expected_constraints,
        }
    output["horizon"] = int(horizon)
    output["suffix_count"] = 2 ** (horizon + 1) - 1
    output["metric"] = "learned_anchor_metric_B^-T_B^-1"
    return output


def exact_chart_packet_control(
    capture: TrajectoryCapture,
    *,
    prefixes: Iterable[int],
    horizon: int,
) -> dict[str, Any]:
    decoder = torch.eye(N_STATES, dtype=torch.float64)
    metric = torch.eye(N_STATES, dtype=torch.float64)
    transitions = capture.canonical_transitions
    exact_operators = column_permutation_matrix(transitions, dtype=torch.float64)
    cache: dict[tuple[int, int], Any] = {}
    output: dict[str, Any] = {}
    for depth in sorted(set(int(value) for value in prefixes)):
        source = capture.exact_state_by_prefix[depth]
        inside: list[bool] = []
        margins: list[float] = []
        for episode in range(source.shape[0]):
            state_index = int(source[episode])
            key = (episode, state_index)
            if key not in cache:
                cache[key] = build_continuation_constraints(
                    decoder,
                    exact_operators[episode],
                    transitions[episode],
                    state_index,
                    max_depth=horizon,
                )
            state = torch.nn.functional.one_hot(
                source[episode : episode + 1], num_classes=N_STATES
            ).to(torch.float64)
            result = continuation_margins(state, cache[key], metric)
            inside.append(bool(result.inside[0]))
            margins.append(float(result.minimum_margin[0]))
        output[str(depth)] = {
            "membership_fraction": sum(inside) / len(inside),
            "margin": numeric_summary(margins),
            "examples": len(inside),
        }
    output["horizon"] = int(horizon)
    return output


def per_episode_observability(
    model: ProjectiveLinearHyperOperatorRNN,
    capture: TrajectoryCapture,
    *,
    max_depth: int,
    episode_limit: int,
) -> dict[str, Any]:
    decoder = model.decoder.weight.detach().cpu()
    ranks: list[int] = []
    null_dimensions: list[int] = []
    smallest_relative: list[float] = []
    for episode in range(min(episode_limit, capture.canonical_codes.shape[0])):
        result = future_observability(
            decoder,
            capture.canonical_codes[episode : episode + 1],
            max_depth=max_depth,
            episode_limit=None,
        )
        ranks.append(result.rank)
        null_dimensions.append(result.null_dimension)
        singular = result.singular_values
        smallest_relative.append(singular[-1] / singular[0] if singular and singular[0] else 0.0)
    histogram = {str(rank): ranks.count(rank) for rank in sorted(set(ranks))}
    return {
        "max_depth": int(max_depth),
        "episodes": len(ranks),
        "ranks": ranks,
        "rank_histogram": histogram,
        "minimum_rank": min(ranks),
        "maximum_null_dimension": max(null_dimensions),
        "smallest_relative_singular_value": numeric_summary(smallest_relative),
    }


def _apply_semantic_word(transitions: torch.Tensor, start: int, word: tuple[int, ...]) -> int:
    current = int(start)
    for action in word:
        current = int(transitions[action, current])
    return current


def _safe_exp(log_value: float) -> float | None:
    if not math.isfinite(log_value) or log_value > math.log(torch.finfo(torch.float64).max):
        return None
    return math.exp(log_value)


def switched_word_audit(
    model: ProjectiveLinearHyperOperatorRNN,
    capture: TrajectoryCapture,
    *,
    prefix: int,
    episode_limit: int,
    word_length: int = 8,
) -> dict[str, Any]:
    words = tuple(product(range(2), repeat=word_length))
    decoder = model.decoder.weight.detach().cpu().to(torch.float64)
    metric = anchor_metric(model, normalize_trace=False).detach().cpu().to(torch.float64)
    records: list[dict[str, Any]] = []
    undefined = 0
    for episode in range(min(episode_limit, capture.canonical_codes.shape[0])):
        operators = capture.canonical_codes[episode].to(torch.float64)
        transitions = capture.canonical_transitions[episode]
        state = capture.hidden_by_prefix[prefix][episode].to(torch.float64)
        source = int(capture.exact_state_by_prefix[prefix][episode])
        best: tuple[float, tuple[int, ...], Any, int] | None = None
        constant_logs: list[float] = []
        mixed_logs: list[float] = []
        all_correct = 0
        evaluated = 0
        for word in words:
            sequence = operators[torch.tensor(word, dtype=torch.long)]
            try:
                result = projective_sequence_jacobian(sequence, state, metric)
            except ValueError:
                undefined += 1
                continue
            log_gain = float(result.log_worst_singular_amplification)
            target = _apply_semantic_word(transitions, source, word)
            prediction = int((decoder @ result.endpoint).argmax())
            all_correct += int(prediction == target)
            evaluated += 1
            if len(set(word)) == 1:
                constant_logs.append(log_gain)
            else:
                mixed_logs.append(log_gain)
            if best is None or log_gain > best[0]:
                best = (log_gain, word, result, target)
        if best is None:
            records.append({
                "episode": episode,
                "defined": False,
                "evaluated_words": evaluated,
            })
            continue
        best_log, best_word, best_result, best_target = best
        margin = normalized_decoder_margin(decoder, best_result.endpoint, best_target, metric)
        constant_max = max(constant_logs)
        mixed_max = max(mixed_logs)
        records.append({
            "episode": episode,
            "defined": True,
            "worst_word": "".join(map(str, best_word)),
            "worst_log_gain": best_log,
            "worst_gain": _safe_exp(best_log),
            "worst_word_margin": margin,
            "worst_word_correct": bool(int((decoder @ best_result.endpoint).argmax()) == best_target),
            "all_word_accuracy": all_correct / evaluated,
            "constant_max_log_gain": constant_max,
            "mixed_max_log_gain": mixed_max,
            "mixed_minus_constant_log_gain": mixed_max - constant_max,
            "evaluated_words": evaluated,
        })
    valid = [record for record in records if record.get("defined")]
    return {
        "prefix": int(prefix),
        "word_length": int(word_length),
        "word_count": len(words),
        "episodes": len(records),
        "undefined_applications": undefined,
        "per_episode": records,
        "worst_log_gain": numeric_summary(record["worst_log_gain"] for record in valid),
        "mixed_minus_constant_log_gain": numeric_summary(
            record["mixed_minus_constant_log_gain"] for record in valid
        ),
        "mixed_enhancement_fraction": (
            sum(record["mixed_minus_constant_log_gain"] > 1e-12 for record in valid) / len(valid)
            if valid
            else 0.0
        ),
        "all_word_accuracy": numeric_summary(record["all_word_accuracy"] for record in valid),
        "worst_word_margin": numeric_summary(record["worst_word_margin"] for record in valid),
    }


def switched_synthetic_controls(
    transitions: torch.Tensor, *, word_length: int = 8
) -> dict[str, Any]:
    words = tuple(product(range(2), repeat=word_length))
    exact_operators = column_permutation_matrix(transitions.to(torch.long), dtype=torch.float64)
    state = torch.nn.functional.one_hot(torch.tensor(0), num_classes=N_STATES).to(torch.float64)
    gains: list[float] = []
    correct = 0
    for word in words:
        result = projective_sequence_jacobian(
            exact_operators[torch.tensor(word, dtype=torch.long)], state
        )
        gains.append(result.worst_singular_amplification)
        target = _apply_semantic_word(transitions, 0, word)
        correct += int(int(result.endpoint.argmax()) == target)
    nonnormal = nonnormal_switched_counterexample()
    return {
        "exact_chart": {
            "word_count": len(words),
            "accuracy": correct / len(words),
            "gain": numeric_summary(gains),
        },
        "nonnormal": {
            "individual_spectral_radii": list(nonnormal.individual_spectral_radii),
            "period_spectral_radius": nonnormal.period_spectral_radius,
            "projective_worst_amplification": nonnormal.projective_worst_amplification,
            "flagged": nonnormal.is_counterexample,
        },
    }


def null_loop_margin_audit(
    model: ProjectiveLinearHyperOperatorRNN,
    capture: TrajectoryCapture,
    *,
    prefix: int,
    horizon: int,
    repeats: Iterable[int],
    episode_limit: int,
) -> dict[str, Any]:
    decoder = model.decoder.weight.detach().cpu().to(torch.float64)
    metric = anchor_metric(model, normalize_trace=False).detach().cpu().to(torch.float64)
    repeat_values = tuple(sorted(set(int(value) for value in repeats)))
    output: dict[str, Any] = {}
    for relation_name, relation_word in D4_RELATIONS.items():
        rows_by_repeat: dict[int, list[dict[str, Any]]] = {value: [] for value in repeat_values}
        first_crossings: list[int] = []
        for episode in range(min(episode_limit, capture.canonical_codes.shape[0])):
            operators = capture.canonical_codes[episode].to(torch.float64)
            transitions = capture.canonical_transitions[episode]
            state = capture.hidden_by_prefix[prefix][episode].to(torch.float64)
            source = int(capture.exact_state_by_prefix[prefix][episode])
            if _apply_semantic_word(transitions, source, tuple(relation_word)) != source:
                raise AssayIntegrityError(f"{relation_name} is not null in episode {episode}")
            constraints = build_continuation_constraints(
                decoder, operators, transitions, source, max_depth=horizon
            )
            baseline_result = continuation_margins(state.unsqueeze(0), constraints, metric)
            baseline_margin = float(baseline_result.minimum_margin[0])
            baseline_inside = bool(baseline_result.inside[0])
            current = state
            completed = 0
            first_crossing = -1
            for requested_repeat in repeat_values:
                for _ in range(requested_repeat - completed):
                    for action in relation_word:
                        current = normalized_projective_map(operators[action], current)
                completed = requested_repeat
                result = continuation_margins(current.unsqueeze(0), constraints, metric)
                margin = float(result.minimum_margin[0])
                inside = bool(result.inside[0])
                if baseline_inside and not inside and first_crossing < 0:
                    first_crossing = requested_repeat
                ratio = margin / baseline_margin if baseline_margin > 0 else None
                prediction = int((decoder @ current).argmax())
                angle = float(oriented_projective_distance(state, current, metric))
                rows_by_repeat[requested_repeat].append({
                    "margin": margin,
                    "margin_ratio": ratio,
                    "inside": inside,
                    "correct": prediction == source,
                    "angle": angle,
                })
            first_crossings.append(first_crossing)
        relation_output: dict[str, Any] = {}
        for repeat, rows in rows_by_repeat.items():
            ratios = [row["margin_ratio"] for row in rows if row["margin_ratio"] is not None]
            relation_output[str(repeat)] = {
                "accuracy": sum(row["correct"] for row in rows) / len(rows),
                "membership_fraction": sum(row["inside"] for row in rows) / len(rows),
                "margin": numeric_summary(row["margin"] for row in rows),
                "positive_baseline_margin_ratio": numeric_summary(ratios),
                "projective_angle": numeric_summary(row["angle"] for row in rows),
                "examples": len(rows),
            }
        relation_output["first_crossing_repeat"] = {
            "never_fraction": sum(value < 0 for value in first_crossings) / len(first_crossings),
            "observed": [value for value in first_crossings if value >= 0],
        }
        output[relation_name] = relation_output
    return {
        "prefix": int(prefix),
        "horizon": int(horizon),
        "relations": output,
    }


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(child) for child in value]
    if isinstance(value, torch.Tensor):
        return json_ready(value.detach().cpu().tolist())
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f"cannot serialize value of type {type(value).__name__}")


__all__ = [
    "AssayIntegrityError",
    "FAMILY_TO_GENERATOR",
    "LoadedProjectiveCheckpoint",
    "TrajectoryCapture",
    "canonicalize_actions",
    "capture_trajectory",
    "derive_seed",
    "episode_bank_receipts",
    "episode_contract",
    "exact_chart_packet_control",
    "family_rollout_metrics",
    "file_sha256",
    "gauge_synthetic_controls",
    "json_ready",
    "learned_gauge_diagnostic",
    "load_projective_checkpoint",
    "load_projective_pilot_models",
    "make_episode_bank",
    "null_loop_margin_audit",
    "numeric_summary",
    "packet_audit",
    "per_episode_observability",
    "switched_synthetic_controls",
    "switched_word_audit",
    "tensor_receipt",
    "trajectory_tensor_receipts",
]
