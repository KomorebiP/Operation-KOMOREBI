from __future__ import annotations

import hashlib
import copy
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch

from .algebra import D4_RELATIONS
from .data import EpisodeGenerator
from .evaluate import _chunks, apply_slots_torch, intervention_metrics
from .models import LinearHyperOperatorRNN, RecurrentOperatorModel, build_model
from .stability import (
    anchor_basis,
    anchor_metric,
    conformal_metric_defect,
    future_observability,
    normalized_anchor_defect,
    normalized_holonomy,
    normalized_metric_defect,
    projective_holonomy,
    projective_anchor_defect,
    relation_product,
)
from .stable_models import (
    AnchorClosedOperatorRNN,
    MetricPolarOperatorRNN,
    NormalizedRawOperatorRNN,
    SemanticChartClosedOperatorRNN,
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_legacy_linear_checkpoint(path: Path, device: torch.device) -> tuple[LinearHyperOperatorRNN, dict[str, Any]]:
    payload = torch.load(path, map_location="cpu", weights_only=True)
    required = {"arm", "source_digest", "config", "state_dict"}
    if set(payload) != required:
        raise ValueError(f"unexpected legacy checkpoint fields: {sorted(payload)}")
    if payload["config"].get("model_name") != "linear_hyper":
        raise ValueError("stability audit requires a linear_hyper checkpoint")
    model = build_model("linear_hyper")
    if not isinstance(model, LinearHyperOperatorRNN):
        raise TypeError("linear_hyper builder returned the wrong type")
    model.load_state_dict(payload["state_dict"], strict=True)
    model.to(device).eval()
    return model, payload


def build_stability_arms(base: LinearHyperOperatorRNN) -> dict[str, RecurrentOperatorModel]:
    return {
        "raw": base,
        "normalized_raw": NormalizedRawOperatorRNN(base),
        "metric_polar": MetricPolarOperatorRNN(base),
        "anchor_closed": AnchorClosedOperatorRNN(base),
        "semantic_chart_closed": SemanticChartClosedOperatorRNN(base),
    }


def _base_model(model: RecurrentOperatorModel) -> LinearHyperOperatorRNN:
    if isinstance(model, LinearHyperOperatorRNN):
        return model
    base = getattr(model, "base", None)
    if not isinstance(base, LinearHyperOperatorRNN):
        raise TypeError("model does not expose a linear base")
    return base


def _analysis_basis_and_metric(model: RecurrentOperatorModel) -> tuple[torch.Tensor, torch.Tensor]:
    if isinstance(model, SemanticChartClosedOperatorRNN):
        identity = torch.eye(
            model.hidden_dim,
            dtype=model.base.state_embedding.weight.dtype,
            device=model.base.state_embedding.weight.device,
        )
        return identity, identity
    base = _base_model(model)
    return anchor_basis(base), anchor_metric(base)


def _finite_summary(values: list[torch.Tensor]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    joined = torch.cat(values).to(torch.float64)
    joined = joined[torch.isfinite(joined)]
    if not joined.numel():
        return None, None
    return float(torch.median(joined)), float(torch.max(joined))


def deep_rollout_metrics(
    model: RecurrentOperatorModel,
    family: str,
    lengths: Iterable[int],
    examples: int,
    batch_size: int,
    seed: int,
    device: torch.device,
) -> dict[str, dict[str, Any]]:
    generator = EpisodeGenerator(seed)
    base = _base_model(model)
    _, metric = _analysis_basis_and_metric(model)
    metric = metric.to(device)
    output: dict[str, dict[str, Any]] = {}
    model.eval()
    with torch.no_grad():
        for length in lengths:
            correct = 0
            total = 0
            finite_examples = 0
            log_norms: list[torch.Tensor] = []
            log_metric_norms: list[torch.Tensor] = []
            projective_errors: list[torch.Tensor] = []
            for current_batch in _chunks(examples, batch_size):
                batch = generator.sample(current_batch, int(length), family=family).to(device)
                codes = model.encode_operators(batch.tables)
                hidden = model.initial_hidden(batch.start)
                rows = torch.arange(current_batch, device=device)
                for step in range(batch.op_slots.shape[1]):
                    hidden = model.step_hidden(hidden, codes[rows, batch.op_slots[:, step]])
                finite = torch.isfinite(hidden).all(dim=1)
                logits = model.decode_hidden(hidden)
                prediction = logits.argmax(dim=1)
                correct += int(((prediction == batch.target) & finite).sum())
                total += current_batch
                finite_examples += int(finite.sum())
                if finite.any():
                    observed = hidden[finite]
                    expected = (
                        model.initial_hidden(batch.target[finite])
                        if isinstance(model, SemanticChartClosedOperatorRNN)
                        else base.initial_hidden(batch.target[finite])
                    )
                    euclidean_norm = torch.linalg.vector_norm(observed, dim=1)
                    metric_squared = torch.einsum("bi,ij,bj->b", observed, metric, observed).clamp_min(1e-30)
                    log_norms.append(torch.log10(euclidean_norm.clamp_min(1e-30)))
                    log_metric_norms.append(0.5 * torch.log10(metric_squared))
                    alpha = (observed * expected).sum(dim=1) / expected.square().sum(dim=1).clamp_min(1e-30)
                    residual = observed - alpha.unsqueeze(1) * expected
                    projective_errors.append(
                        torch.linalg.vector_norm(residual, dim=1)
                        / torch.linalg.vector_norm(observed, dim=1).clamp_min(1e-30)
                    )
            median_log_norm, max_log_norm = _finite_summary(log_norms)
            median_log_metric, max_log_metric = _finite_summary(log_metric_norms)
            median_projective, max_projective = _finite_summary(projective_errors)
            output[str(length)] = {
                "accuracy": correct / total,
                "finite_fraction": finite_examples / total,
                "median_log10_l2": median_log_norm,
                "max_log10_l2": max_log_norm,
                "median_log10_metric_norm": median_log_metric,
                "max_log10_metric_norm": max_log_metric,
                "median_projective_anchor_error": median_projective,
                "max_projective_anchor_error": max_projective,
                "examples": total,
            }
    return output


def code_audit(
    model: RecurrentOperatorModel,
    examples: int,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    generator = EpisodeGenerator(seed)
    batch = generator.sample(examples, 0, family="d4").to(device)
    base = _base_model(model)
    basis, metric = _analysis_basis_and_metric(model)
    basis = basis.to(device)
    metric = metric.to(device)
    with torch.no_grad():
        codes = model.encode_operators(batch.tables)
        anchor_defect = normalized_anchor_defect(codes, batch.tables, basis)
        ray_anchor_defect, ray_anchor_scale = projective_anchor_defect(codes, batch.tables, basis)
        metric_defect = normalized_metric_defect(codes, metric)
        conformal_defect, conformal_scale = conformal_metric_defect(codes, metric)
        eigenvalues = torch.linalg.eigvals(codes.to(torch.float64))
        radii = eigenvalues.abs().max(dim=-1).values
        relation_output: dict[str, Any] = {}
        for name, word in D4_RELATIONS.items():
            slots = EpisodeGenerator.slots_for_word(batch.canonical_to_slot, word)
            product_matrix = relation_product(codes, slots)
            raw = normalized_holonomy(product_matrix, metric)
            projective, scalar = projective_holonomy(product_matrix, metric)
            relation_output[name] = {
                "metric_holonomy_mean": float(raw.mean()),
                "metric_holonomy_max": float(raw.max()),
                "projective_holonomy_mean": float(projective.mean()),
                "projective_holonomy_max": float(projective.max()),
                "projective_scalar_median": float(torch.median(scalar)),
                "positive_scalar_fraction": float((scalar > 0).to(torch.float32).mean()),
            }
    metric_eigenvalues = torch.linalg.eigvalsh(metric.to(torch.float64))
    return {
        "anchor_defect_mean": float(anchor_defect.mean()),
        "anchor_defect_max": float(anchor_defect.max()),
        "projective_anchor_defect_mean": float(ray_anchor_defect.mean()),
        "projective_anchor_defect_max": float(ray_anchor_defect.max()),
        "projective_anchor_positive_scale_fraction": float(
            (ray_anchor_scale > 0).to(torch.float32).mean()
        ),
        "metric_isometry_defect_mean": float(metric_defect.mean()),
        "metric_isometry_defect_max": float(metric_defect.max()),
        "conformal_metric_defect_mean": float(conformal_defect.mean()),
        "conformal_metric_defect_max": float(conformal_defect.max()),
        "conformal_scale_median": float(torch.median(conformal_scale)),
        "spectral_radius_median": float(torch.median(radii)),
        "spectral_radius_max": float(torch.max(radii)),
        "metric_condition_number": float((metric_eigenvalues.max() / metric_eigenvalues.min()).detach()),
        "relations": relation_output,
    }


def observability_audit(
    model: LinearHyperOperatorRNN,
    examples: int,
    max_depth: int,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    generator = EpisodeGenerator(seed)
    batch = generator.sample(examples, 0, family="d4").to(device)
    with torch.no_grad():
        codes = model.encode_operators(batch.tables)
        result = future_observability(
            model.decoder.weight,
            codes,
            max_depth=max_depth,
            relative_tolerance=1e-6,
            episode_limit=examples,
        )
        decoder_rank = int(torch.linalg.matrix_rank(model.decoder.weight.to(torch.float64)))
        centered = (
            model.decoder.weight.to(torch.float64)
            - model.decoder.weight.to(torch.float64).mean(dim=0, keepdim=True)
        )
        centered_singular = torch.linalg.svdvals(centered)
        centered_threshold = float(centered_singular[0]) * 1e-6
        centered_rank = int((centered_singular > centered_threshold).sum())
        basis_condition = float(torch.linalg.cond(anchor_basis(model).to(torch.float64)))
    return {
        "finite_horizon": result.to_dict(),
        "decoder_rank": decoder_rank,
        "centered_decoder_rank": centered_rank,
        "anchor_basis_condition_number": basis_condition,
        "interpretation": (
            "No nonzero additive future-null packet was found at the frozen tolerance."
            if result.null_dimension == 0
            else "A candidate additive future-null packet remains and requires causal validation."
        ),
    }


def projective_gauge_audit(
    raw: LinearHyperOperatorRNN,
    normalized: NormalizedRawOperatorRNN,
    lengths: Iterable[int],
    examples: int,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    raw64 = copy.deepcopy(raw).to(device=device, dtype=torch.float64).eval()
    normalized64 = NormalizedRawOperatorRNN(raw64).to(device=device, dtype=torch.float64).eval()
    with torch.no_grad():
        for offset, length in enumerate(lengths):
            batch = EpisodeGenerator(seed + offset).sample(examples, int(length), family="d4").to(device)
            tables = batch.tables.to(torch.float64)
            raw_codes = raw64.encode_operators(tables)
            normalized_codes = normalized64.encode_operators(tables)
            raw_hidden = raw64.initial_hidden(batch.start)
            normalized_hidden = normalized64.initial_hidden(batch.start)
            rows = torch.arange(examples, device=device)
            for step in range(batch.op_slots.shape[1]):
                slots = batch.op_slots[:, step]
                raw_hidden = raw64.step_hidden(raw_hidden, raw_codes[rows, slots])
                normalized_hidden = normalized64.step_hidden(normalized_hidden, normalized_codes[rows, slots])
            raw_finite = torch.isfinite(raw_hidden).all(dim=1)
            normalized_finite = torch.isfinite(normalized_hidden).all(dim=1)
            comparable = raw_finite & normalized_finite
            if comparable.any():
                raw_prediction = raw64.decode_hidden(raw_hidden[comparable]).argmax(dim=1)
                normalized_prediction = normalized64.decode_hidden(normalized_hidden[comparable]).argmax(dim=1)
                agreement = float((raw_prediction == normalized_prediction).to(torch.float32).mean())
                cosine = float(
                    torch.nn.functional.cosine_similarity(
                        raw_hidden[comparable], normalized_hidden[comparable], dim=1
                    ).mean()
                )
            else:
                agreement = None
                cosine = None
            output[str(length)] = {
                "raw_finite_fraction": float(raw_finite.to(torch.float32).mean()),
                "normalized_finite_fraction": float(normalized_finite.to(torch.float32).mean()),
                "prediction_agreement_when_comparable": agreement,
                "direction_cosine_when_comparable": cosine,
                "audit_dtype": "float64",
            }
    return output


def null_cycle_metrics(
    model: RecurrentOperatorModel,
    relation_repeats: Iterable[int],
    examples: int,
    batch_size: int,
    base_length: int,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    model.eval()
    with torch.no_grad():
        for relation_index, (relation_name, relation_word) in enumerate(D4_RELATIONS.items()):
            relation_output: dict[str, Any] = {}
            for repeats in relation_repeats:
                generator = EpisodeGenerator(seed + 1000 * relation_index)
                correct = 0
                total = 0
                finite_count = 0
                agreement_count = 0
                logs: list[torch.Tensor] = []
                angles: list[torch.Tensor] = []
                for current_batch in _chunks(examples, batch_size):
                    batch = generator.sample(current_batch, base_length, family="d4").to(device)
                    midpoint = base_length // 2
                    insertion = torch.tensor(
                        relation_word * int(repeats), dtype=torch.long, device=device
                    ).unsqueeze(0).expand(current_batch, -1)
                    canonical = torch.cat(
                        (batch.canonical_ops[:, :midpoint], insertion, batch.canonical_ops[:, midpoint:]), dim=1
                    )
                    slots = torch.gather(batch.canonical_to_slot, 1, canonical)
                    expected = apply_slots_torch(batch.maps, batch.start, slots)
                    if not torch.equal(expected, batch.target):
                        raise AssertionError(f"{relation_name} insertion changed the exact endpoint")
                    trace = model.run(batch.tables, slots, batch.start)
                    hidden = trace.hidden[-1]
                    baseline = model.run(batch.tables, batch.op_slots, batch.start)
                    finite = torch.isfinite(hidden).all(dim=1)
                    comparable = finite & torch.isfinite(baseline.hidden[-1]).all(dim=1)
                    prediction = trace.logits.argmax(dim=1)
                    baseline_prediction = baseline.logits.argmax(dim=1)
                    correct += int(((prediction == expected) & finite).sum())
                    agreement_count += int(((prediction == baseline_prediction) & comparable).sum())
                    total += current_batch
                    finite_count += int(finite.sum())
                    if finite.any():
                        logs.append(torch.log10(torch.linalg.vector_norm(hidden[finite], dim=1).clamp_min(1e-30)))
                    if comparable.any():
                        cosine = torch.nn.functional.cosine_similarity(
                            hidden[comparable].to(torch.float64),
                            baseline.hidden[-1][comparable].to(torch.float64),
                            dim=1,
                        ).clamp(-1.0, 1.0)
                        angles.append(torch.acos(cosine))
                median_log, max_log = _finite_summary(logs)
                median_angle, max_angle = _finite_summary(angles)
                relation_output[str(repeats)] = {
                    "accuracy": correct / total,
                    "finite_fraction": finite_count / total,
                    "prediction_agreement_with_no_cycle": agreement_count / total,
                    "median_projective_angle_to_no_cycle": median_angle,
                    "max_projective_angle_to_no_cycle": max_angle,
                    "median_log10_l2": median_log,
                    "max_log10_l2": max_log,
                    "inserted_relation_length": len(relation_word) * int(repeats),
                }
            output[relation_name] = relation_output
    return output


def deep_intervention_audit(
    model: RecurrentOperatorModel,
    examples: int,
    batch_size: int,
    length: int,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    return intervention_metrics(
        model,
        examples=examples,
        batch_size=batch_size,
        seed=seed,
        device=device,
        length=length,
        split=length // 2,
        operator_step=max(0, length // 2 - 1),
    )


def cross_seed_semantic_transport(
    source_base: LinearHyperOperatorRNN,
    target_base: LinearHyperOperatorRNN,
    examples: int,
    length: int,
    split: int,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    source = AnchorClosedOperatorRNN(source_base).to(device).eval()
    target = AnchorClosedOperatorRNN(target_base).to(device).eval()
    source_basis = anchor_basis(source_base).to(device)
    target_basis = anchor_basis(target_base).to(device)
    transport = target_basis @ torch.linalg.inv(source_basis)
    generator = EpisodeGenerator(seed)
    correct = 0
    total = 0
    residuals: list[torch.Tensor] = []
    with torch.no_grad():
        for current_batch in _chunks(examples, min(examples, 512)):
            batch = generator.sample(current_batch, length, family="d4").to(device)
            source_codes = source.encode_operators(batch.tables)
            target_codes = target.encode_operators(batch.tables)
            residual = transport @ source_codes - target_codes @ transport
            residuals.append(
                torch.linalg.matrix_norm(residual, ord="fro", dim=(-2, -1))
                / torch.linalg.matrix_norm(target_codes @ transport, ord="fro", dim=(-2, -1)).clamp_min(1e-12)
            )
            prefix = batch.op_slots[:, :split]
            suffix = batch.op_slots[:, split:]
            source_trace = source.run(batch.tables, prefix, batch.start)
            mapped = (transport @ source_trace.hidden[-1].unsqueeze(-1)).squeeze(-1)
            target_result = target.continue_from_hidden(mapped, target_codes, suffix)
            correct += int((target_result.logits.argmax(dim=1) == batch.target).sum())
            total += current_batch
    joined = torch.cat(residuals)
    metric_source = anchor_metric(source_base, normalize_trace=False).to(device)
    metric_target = anchor_metric(target_base, normalize_trace=False).to(device)
    metric_residual = transport.transpose(0, 1) @ metric_target @ transport - metric_source
    return {
        "accuracy": correct / total,
        "examples": total,
        "length": length,
        "split": split,
        "intertwining_residual_mean": float(joined.mean()),
        "intertwining_residual_max": float(joined.max()),
        "metric_transport_residual": float((
            torch.linalg.matrix_norm(metric_residual, ord="fro")
            / torch.linalg.matrix_norm(metric_source, ord="fro").clamp_min(1e-12)
        ).detach()),
        "transport_condition_number": float(torch.linalg.cond(transport.to(torch.float64)).detach()),
    }
