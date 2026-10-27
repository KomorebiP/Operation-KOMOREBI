from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    import torch
    import torch.nn.functional as F
except ImportError as error:  # pragma: no cover - handled by preflight
    raise ImportError("PyTorch is required for geometry probes.") from error

from .byte_tokenizer import ByteTokenizer
from .core import stable_hash
from .tiny_model import ModelConfig, TinyDecoderLM
from .train_data import TrainingExample
from .generate import canonical_json, sha256_file
from .trainer import _collate, load_model_checkpoint, model_state_hash


def _atomic_json(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def _subset(examples: list[TrainingExample], count: int, key: str) -> list[TrainingExample]:
    return sorted(examples, key=lambda item: stable_hash(f"{key}|{item.pair_id}"))[:count]


def _prompt_batch(
    examples: list[TrainingExample],
    tokenizer: ByteTokenizer,
    device: "torch.device",
) -> tuple["torch.Tensor", "torch.Tensor", "torch.Tensor"]:
    prefixes = [tokenizer.prefix(item.prompt) for item in examples]
    length = max(map(len, prefixes))
    input_ids = torch.full(
        (len(examples), length), tokenizer.pad_id, dtype=torch.long, device=device
    )
    positions = torch.empty(len(examples), dtype=torch.long, device=device)
    targets = torch.empty(len(examples), dtype=torch.long, device=device)
    for row, (item, prefix) in enumerate(zip(examples, prefixes)):
        input_ids[row, : len(prefix)] = torch.tensor(prefix, dtype=torch.long, device=device)
        positions[row] = len(prefix) - 1
        targets[row] = tokenizer.encode(item.completion)[0]
    return input_ids, positions, targets


def _top_space(matrix: "torch.Tensor", rank: int) -> tuple["torch.Tensor", "torch.Tensor"]:
    symmetric = 0.5 * (matrix + matrix.T)
    eigenvalues, eigenvectors = torch.linalg.eigh(symmetric.double().cpu())
    order = torch.argsort(eigenvalues, descending=True)
    eigenvalues = eigenvalues[order].clamp_min(0)
    basis = eigenvectors[:, order[:rank]]
    return basis, eigenvalues


def _projection_overlap(left: "torch.Tensor", right: "torch.Tensor") -> float:
    rank = min(left.shape[1], right.shape[1])
    return float((left[:, :rank].T @ right[:, :rank]).square().sum().item() / rank)


def _spectral_summary(eigenvalues: "torch.Tensor", rank: int) -> dict[str, float]:
    total = float(eigenvalues.sum().item())
    squared = float(eigenvalues.square().sum().item())
    top = float(eigenvalues[:rank].sum().item())
    participation = total * total / squared if squared > 0 else 0.0
    eigengap = (
        float(eigenvalues[rank - 1].item() - eigenvalues[rank].item())
        if len(eigenvalues) > rank
        else float(eigenvalues[rank - 1].item())
    )
    return {
        "top_rank_trace_fraction": top / total if total > 0 else 0.0,
        "participation_rank": participation,
        "eigengap": eigengap,
        "trace": total,
    }


@torch.no_grad()
def _activation_bank(
    model: TinyDecoderLM,
    examples: list[TrainingExample],
    tokenizer: ByteTokenizer,
    device: "torch.device",
    layer: int,
    batch_size: int,
) -> tuple["torch.Tensor", "torch.Tensor", "torch.Tensor"]:
    sources = []
    updates = []
    target_tokens = []
    for start in range(0, len(examples), batch_size):
        batch = examples[start : start + batch_size]
        input_ids, positions, batch_targets = _prompt_batch(batch, tokenizer, device)
        _, states = model(input_ids, return_hidden_states=True)
        rows = torch.arange(len(batch), device=device)
        source = states[layer][rows, positions]
        final = states[-1][rows, positions]
        sources.append(source.float().cpu())
        updates.append((final - source).float().cpu())
        target_tokens.extend(batch_targets.cpu().tolist())
    return torch.cat(sources), torch.cat(updates), torch.tensor(target_tokens, dtype=torch.long)


def _gradient_banks(
    model: TinyDecoderLM,
    examples: list[TrainingExample],
    tokenizer: ByteTokenizer,
    device: "torch.device",
    layer: int,
    batch_size: int,
    jacobian_projections: int,
    seed: int,
) -> tuple["torch.Tensor", "torch.Tensor"]:
    completion_score_gradient_rows = []
    jacobian_rows = []
    original_flags = [parameter.requires_grad for parameter in model.parameters()]
    try:
        for parameter in model.parameters():
            parameter.requires_grad_(False)
        model.eval()
        for start in range(0, len(examples), batch_size):
            batch = examples[start : start + batch_size]
            indices = list(range(len(batch)))
            input_ids, labels, positions, _ = _collate(
                batch, indices, tokenizer, device
            )
            embeddings = model.token_embedding(input_ids).detach().requires_grad_(True)
            logits, states = model.forward_embeddings(embeddings, return_hidden_states=True)
            source = states[layer]
            rows = torch.arange(len(batch), device=device)
            valid = labels != -100
            safe_labels = labels.masked_fill(~valid, 0)
            token_log_probabilities = F.log_softmax(logits.float(), dim=-1).gather(
                dim=-1, index=safe_labels.unsqueeze(-1)
            ).squeeze(-1)
            completion_log_probability = token_log_probabilities.masked_fill(
                ~valid, 0.0
            ).sum()
            completion_score_gradient = torch.autograd.grad(
                completion_log_probability, source, retain_graph=True
            )[0][rows, positions]
            completion_score_gradient_rows.append(
                completion_score_gradient.detach().float().cpu()
            )
            update = states[-1][rows, positions] - source[rows, positions]
            for projection in range(jacobian_projections):
                generator_seed = int(
                    stable_hash(f"{seed}|vjp|{start}|{projection}")[:16], 16
                )
                generator = torch.Generator(device="cpu").manual_seed(generator_seed)
                signs = (
                    torch.randint(
                        0,
                        2,
                        update.shape,
                        generator=generator,
                        dtype=torch.int64,
                        device="cpu",
                    )
                    .mul(2)
                    .sub(1)
                    .to(device=device, dtype=update.dtype)
                )
                scalar = (update * signs).sum()
                keep = projection + 1 < jacobian_projections
                gradient = torch.autograd.grad(scalar, source, retain_graph=keep)[0][
                    rows, positions
                ]
                jacobian_rows.append(gradient.detach().float().cpu())
    finally:
        for parameter, flag in zip(model.parameters(), original_flags):
            parameter.requires_grad_(flag)
    return torch.cat(completion_score_gradient_rows), torch.cat(jacobian_rows)


def _geometry_matrices(
    sources: "torch.Tensor",
    updates: "torch.Tensor",
    targets: "torch.Tensor",
    completion_score_gradients: "torch.Tensor",
    jacobian: "torch.Tensor",
    ridge: float,
) -> tuple[dict[str, "torch.Tensor"], dict[str, "torch.Tensor"]]:
    source_mean = sources.mean(dim=0, keepdim=True)
    update_mean = updates.mean(dim=0, keepdim=True)
    z = sources - source_mean
    u = updates - update_mean
    cross = z.T @ u / max(1, len(z))
    predictive = cross @ cross.T
    completion_score_gradient_matrix = (
        completion_score_gradients.T @ completion_score_gradients
        / max(1, len(completion_score_gradients))
    )
    jacobian_matrix = jacobian.T @ jacobian / max(1, len(jacobian))
    target_matrix = F.one_hot(targets, num_classes=260).double()
    gram = z.double().T @ z.double()
    weights = torch.linalg.solve(
        gram + ridge * torch.eye(gram.shape[0], dtype=torch.float64),
        z.double().T @ target_matrix,
    )
    decoder_first_token = weights @ weights.T
    return (
        {
            "future_update_crosscov": predictive,
            "completion_score_gradient": completion_score_gradient_matrix,
            "jacobian_update": jacobian_matrix,
            "decoder_first_token": decoder_first_token,
        },
        {
            "source_mean": source_mean.squeeze(0),
            "decoder_first_token_weights": weights,
        },
    )


def _decoder_first_token_accuracy(
    sources: "torch.Tensor",
    targets: "torch.Tensor",
    source_mean: "torch.Tensor",
    weights: "torch.Tensor",
) -> float:
    predictions = ((sources - source_mean).double() @ weights).argmax(dim=-1)
    return float((predictions == targets).double().mean().item())


@torch.no_grad()
def _ablation_effect(
    model: TinyDecoderLM,
    examples: list[TrainingExample],
    tokenizer: ByteTokenizer,
    device: "torch.device",
    layer: int,
    source_mean: "torch.Tensor",
    basis: "torch.Tensor",
    batch_size: int,
    match_energy_to: "torch.Tensor | None" = None,
) -> dict[str, float]:
    completion_nll_changes = []
    completion_token_counts = []
    removal_norms = []
    mean = source_mean.to(device=device, dtype=torch.float32)
    space = basis.to(device=device, dtype=torch.float32)
    reference = (
        match_energy_to.to(device=device, dtype=torch.float32)
        if match_energy_to is not None
        else None
    )
    for start in range(0, len(examples), batch_size):
        batch = examples[start : start + batch_size]
        indices = list(range(len(batch)))
        input_ids, labels, positions, _ = _collate(batch, indices, tokenizer, device)
        logits, states = model(input_ids, return_hidden_states=True)
        rows = torch.arange(len(batch), device=device)
        valid = labels != -100
        safe_labels = labels.masked_fill(~valid, 0)
        baseline_token_nll = -F.log_softmax(logits.float(), dim=-1).gather(
            dim=-1, index=safe_labels.unsqueeze(-1)
        ).squeeze(-1)
        hidden = states[layer].clone()
        prompt_state = hidden[rows, positions]
        centered = prompt_state - mean
        removal = (centered @ space) @ space.T
        if reference is not None:
            reference_removal = (centered @ reference) @ reference.T
            desired = reference_removal.norm(dim=-1, keepdim=True)
            removal = removal * (desired / removal.norm(dim=-1, keepdim=True).clamp_min(1e-12))
        removal_norms.append(removal.norm(dim=-1).cpu())
        hidden[rows, positions] = prompt_state - removal
        patched_logits = model.continue_from_hidden(hidden, completed_layers=layer)
        patched_token_nll = -F.log_softmax(patched_logits.float(), dim=-1).gather(
            dim=-1, index=safe_labels.unsqueeze(-1)
        ).squeeze(-1)
        token_changes = (patched_token_nll - baseline_token_nll).masked_fill(
            ~valid, 0.0
        )
        example_changes = token_changes.sum(dim=-1)
        example_token_counts = valid.sum(dim=-1).clamp_min(1)
        completion_nll_changes.append(example_changes.cpu())
        completion_token_counts.append(example_token_counts.cpu())
    all_completion_nll_changes = torch.cat(completion_nll_changes)
    all_completion_token_counts = torch.cat(completion_token_counts)
    change_per_example = float(all_completion_nll_changes.mean().item())
    change_per_token = float(
        (all_completion_nll_changes.sum() / all_completion_token_counts.sum()).item()
    )
    removed = float(torch.cat(removal_norms).mean().item())
    return {
        "completion_teacher_forced_nll_increase_per_example": change_per_example,
        "completion_teacher_forced_nll_increase_per_token": change_per_token,
        "removed_state_norm": removed,
        "completion_teacher_forced_nll_increase_per_token_per_removed_norm": (
            change_per_token / max(removed, 1e-12)
        ),
    }


def synthetic_calibration(seed: int = 314159, dimension: int = 32, rank: int = 4) -> dict[str, float]:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    basis, _ = torch.linalg.qr(torch.randn(dimension, rank, generator=generator, dtype=torch.float64))
    inputs = torch.randn(512, dimension, generator=generator, dtype=torch.float64)
    outputs = inputs @ basis @ basis.T + 0.02 * torch.randn(
        512, dimension, generator=generator, dtype=torch.float64
    )
    cross = (inputs - inputs.mean(0)).T @ (outputs - outputs.mean(0)) / len(inputs)
    recovered, _ = _top_space(cross @ cross.T, rank)
    shuffled = outputs[torch.randperm(len(outputs), generator=generator)]
    null_cross = (inputs - inputs.mean(0)).T @ (shuffled - shuffled.mean(0)) / len(inputs)
    null_space, _ = _top_space(null_cross @ null_cross.T, rank)
    return {
        "planted_overlap": _projection_overlap(basis, recovered),
        "shuffled_overlap": _projection_overlap(basis, null_space),
        "random_expectation": rank / dimension,
    }


def probe_checkpoint(
    *,
    checkpoint: Path,
    model_config: ModelConfig,
    discovery_examples: list[TrainingExample],
    sealed_examples: list[TrainingExample],
    device: "torch.device",
    output: Path,
    rank: int,
    layer: int,
    activation_samples: int,
    gradient_samples: int,
    jacobian_projections: int,
    random_controls: int,
    batch_size: int,
    ridge: float,
    seed: int,
) -> dict[str, Any]:
    if not 0 <= layer <= model_config.n_layers:
        raise ValueError("probe layer is outside the model")
    if not 1 <= rank <= model_config.d_model:
        raise ValueError("probe rank must be between 1 and d_model")
    if min(
        activation_samples,
        gradient_samples,
        jacobian_projections,
        random_controls,
        batch_size,
    ) <= 0:
        raise ValueError("all probe sample, projection, control, and batch counts must be positive")
    if ridge <= 0:
        raise ValueError("ridge must be positive")
    if layer == model_config.n_layers:
        raise ValueError("probe layer must precede the final residual state")
    model, payload = load_model_checkpoint(checkpoint, model_config, device)
    checkpoint_step = int(payload["step"])
    del payload
    before_hash = model_state_hash(model)
    tokenizer = ByteTokenizer()
    discovery = _subset(discovery_examples, activation_samples, "geometry-discovery")
    sealed = _subset(sealed_examples, activation_samples, "geometry-sealed")
    gradient_examples = discovery[:gradient_samples]
    if len(discovery) < rank or len(sealed) < rank:
        raise ValueError("probe discovery and sealed samples must each be at least the rank")
    if len(gradient_examples) < rank:
        raise ValueError("gradient_samples must provide at least rank examples")
    sources, updates, targets = _activation_bank(
        model, discovery, tokenizer, device, layer, batch_size
    )
    sealed_sources, _, sealed_targets = _activation_bank(
        model, sealed, tokenizer, device, layer, batch_size
    )
    completion_score_gradients, jacobian = _gradient_banks(
        model,
        gradient_examples,
        tokenizer,
        device,
        layer,
        batch_size,
        jacobian_projections,
        seed,
    )
    matrices, auxiliaries = _geometry_matrices(
        sources,
        updates,
        targets,
        completion_score_gradients,
        jacobian,
        ridge,
    )
    if not all(torch.isfinite(matrix).all() for matrix in matrices.values()):
        raise RuntimeError("nonfinite geometry matrix")
    spaces = {}
    spectra = {}
    for name, matrix in matrices.items():
        basis, eigenvalues = _top_space(matrix, rank)
        spaces[name] = basis
        spectra[name] = _spectral_summary(eigenvalues, rank)
    pair_overlaps = {
        "jacobian_update__future_update_crosscov": _projection_overlap(
            spaces["jacobian_update"], spaces["future_update_crosscov"]
        ),
        "jacobian_update__completion_score_gradient": _projection_overlap(
            spaces["jacobian_update"], spaces["completion_score_gradient"]
        ),
        "future_update_crosscov__decoder_first_token": _projection_overlap(
            spaces["future_update_crosscov"], spaces["decoder_first_token"]
        ),
        "completion_score_gradient__decoder_first_token": _projection_overlap(
            spaces["completion_score_gradient"], spaces["decoder_first_token"]
        ),
    }
    projectors = [
        spaces["jacobian_update"] @ spaces["jacobian_update"].T,
        spaces["future_update_crosscov"] @ spaces["future_update_crosscov"].T,
    ]
    consensus, _ = _top_space(sum(projectors), rank)
    generator = torch.Generator(device="cpu").manual_seed(seed + checkpoint_step)
    random_overlaps = []
    random_effects = []
    for _ in range(random_controls):
        random_basis, _ = torch.linalg.qr(
            torch.randn(model_config.d_model, rank, generator=generator, dtype=torch.float64)
        )
        random_overlaps.append(_projection_overlap(spaces["jacobian_update"], random_basis))
        random_effects.append(
            _ablation_effect(
                model,
                sealed,
                tokenizer,
                device,
                layer,
                auxiliaries["source_mean"],
                random_basis,
                batch_size,
                match_energy_to=consensus,
            )
        )
    candidate_effect = _ablation_effect(
        model,
        sealed,
        tokenizer,
        device,
        layer,
        auxiliaries["source_mean"],
        consensus,
        batch_size,
    )
    after_hash = model_state_hash(model)
    if before_hash != after_hash:
        raise RuntimeError("geometry probe modified checkpoint weights")
    report = {
        "status": "PASS",
        "claim_status": "CANDIDATE_GEOMETRY_DIAGNOSTIC_ONLY",
        "checkpoint": str(checkpoint.resolve()),
        "checkpoint_step": checkpoint_step,
        "checkpoint_file_sha256": sha256_file(checkpoint),
        "checkpoint_model_hash": before_hash,
        "layer": layer,
        "rank": rank,
        "dimension": model_config.d_model,
        "random_overlap_expectation": rank / model_config.d_model,
        "estimator_families": {
            "update_map": ["jacobian_update", "future_update_crosscov"],
            "target_conditioned": [
                "completion_score_gradient",
                "decoder_first_token",
            ],
        },
        "completion_score_gradient_scope": (
            "teacher_forced_sum_log_probability_of_completion_bytes_plus_eos"
        ),
        "candidate_consensus_source": "update_map_family_only",
        "overlaps": pair_overlaps,
        "random_overlap_mean": sum(random_overlaps) / max(1, len(random_overlaps)),
        "spectra": spectra,
        "decoder_first_token_accuracy_discovery": _decoder_first_token_accuracy(
            sources,
            targets,
            auxiliaries["source_mean"],
            auxiliaries["decoder_first_token_weights"],
        ),
        "decoder_first_token_accuracy_sealed": _decoder_first_token_accuracy(
            sealed_sources,
            sealed_targets,
            auxiliaries["source_mean"],
            auxiliaries["decoder_first_token_weights"],
        ),
        "candidate_ablation": candidate_effect,
        "candidate_ablation_scope": (
            "teacher_forced_full_completion_bytes_plus_eos_at_prompt_boundary"
        ),
        "energy_matched_random_ablation_mean": {
            key: sum(effect[key] for effect in random_effects) / max(1, len(random_effects))
            for key in candidate_effect
        },
        "discovery_examples": len(discovery),
        "sealed_examples": len(sealed),
        "gradient_examples": len(gradient_examples),
        "jacobian_random_projections": jacobian_projections,
        "synthetic_crosscov_calibration": synthetic_calibration(seed),
    }
    report["probe_configuration_sha256"] = stable_hash(
        canonical_json(
            {
                "rank": rank,
                "layer": layer,
                "activation_samples": activation_samples,
                "gradient_samples": gradient_samples,
                "jacobian_projections": jacobian_projections,
                "random_controls": random_controls,
                "batch_size": batch_size,
                "ridge": ridge,
                "seed": seed,
            }
        )
    )
    _atomic_json(report, output)
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return report
