"""Target-free discovery of a locally balanced residual-stream subspace.

The discovery API deliberately accepts tokenized *prefixes only*.  It cannot see
completion strings, answer tokens, labels, or behavioral correctness.  This is
important: the returned object is a candidate causal coordinate system, not a
supervised answer probe.

The estimator is local and empirical.  Random residual perturbations are made at
an upstream layer and their effects at ``source_layer`` estimate controllability.
Gradients of fixed, answer-independent output diagnostics estimate observability.
The dominant modes of ``C**1/2 O C**1/2`` are mapped back to residual coordinates.
Rank is selected by predicting held-out diagnostic changes caused by fresh
upstream perturbations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Sequence

try:
    import torch
except ImportError as error:  # pragma: no cover - handled by package preflight
    raise ImportError("PyTorch is required for balanced-space discovery.") from error

from .tiny_model import TinyDecoderLM


@dataclass(frozen=True)
class BalancedSpaceConfig:
    """Configuration for a target-free, prefix-only discovery run."""

    upstream_layer: int
    source_layer: int
    perturbations_per_prompt: int = 4
    perturbation_scale: float = 0.05
    ridge: float = 1e-4
    candidate_ranks: tuple[int, ...] = (2, 4, 8, 16)
    prediction_fraction_threshold: float = 0.80
    random_output_consumers: int = 4
    seed: int = 314159
    token_position: int = -1

    def validate(self, model: TinyDecoderLM) -> None:
        if not 0 <= self.upstream_layer < self.source_layer < model.config.n_layers:
            raise ValueError(
                "layers must satisfy 0 <= upstream_layer < source_layer < n_layers"
            )
        if self.perturbations_per_prompt <= 0:
            raise ValueError("perturbations_per_prompt must be positive")
        if not 0.0 < self.perturbation_scale < 10.0:
            raise ValueError("perturbation_scale must be positive and finite")
        if self.ridge <= 0.0:
            raise ValueError("ridge must be positive")
        if not self.candidate_ranks:
            raise ValueError("candidate_ranks must not be empty")
        if any(rank <= 0 or rank > model.config.d_model for rank in self.candidate_ranks):
            raise ValueError("candidate ranks must lie in [1, d_model]")
        if not 0.0 <= self.prediction_fraction_threshold <= 1.0:
            raise ValueError("prediction_fraction_threshold must lie in [0, 1]")
        if self.random_output_consumers < 0:
            raise ValueError("random_output_consumers must be nonnegative")
        if self.token_position != -1:
            raise ValueError(
                "v0.4 discovery supports only token_position=-1 (the final prefix token)"
            )


@dataclass
class BalancedSpace:
    """Serializable candidate space and its pre-registered control bases."""

    basis: "torch.Tensor"
    mean: "torch.Tensor"
    eigenvalues: "torch.Tensor"
    source_layer: int
    upstream_layer: int
    token_position: int
    rank: int
    control_bases: dict[str, "torch.Tensor"] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.basis = self.basis.detach().double().cpu().contiguous()
        self.mean = self.mean.detach().double().cpu().contiguous()
        self.eigenvalues = self.eigenvalues.detach().double().cpu().contiguous()
        self.control_bases = {
            str(name): value.detach().double().cpu().contiguous()
            for name, value in self.control_bases.items()
        }
        if self.basis.ndim != 2 or self.basis.shape[1] != self.rank:
            raise ValueError("basis shape does not match rank")
        if self.mean.shape != (self.basis.shape[0],):
            raise ValueError("mean shape does not match basis width")
        identity = self.basis.T @ self.basis
        torch.testing.assert_close(
            identity,
            torch.eye(self.rank, dtype=identity.dtype),
            rtol=1e-5,
            atol=1e-6,
        )
        for name, value in self.control_bases.items():
            if value.shape != self.basis.shape:
                raise ValueError(f"control basis {name!r} is not rank matched")

    @property
    def projector(self) -> "torch.Tensor":
        return self.basis @ self.basis.T

    def summary(self) -> dict[str, Any]:
        return {
            "schema_version": "balanced-space-v1",
            "source_layer": self.source_layer,
            "upstream_layer": self.upstream_layer,
            "token_position": self.token_position,
            "rank": self.rank,
            "width": int(self.basis.shape[0]),
            "projector_shape": list(self.projector.shape),
            "eigenvalues": [float(value) for value in self.eigenvalues.tolist()],
            "selected_eigenvalues": [
                float(value) for value in self.eigenvalues[: self.rank].tolist()
            ],
            "controls": sorted(self.control_bases),
            "metadata": self.metadata,
        }

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "schema_version": "balanced-space-v1",
                "basis": self.basis,
                "projector": self.projector,
                "mean": self.mean,
                "eigenvalues": self.eigenvalues,
                "source_layer": self.source_layer,
                "upstream_layer": self.upstream_layer,
                "token_position": self.token_position,
                "rank": self.rank,
                "control_bases": self.control_bases,
                "metadata": self.metadata,
            },
            destination,
        )

    @classmethod
    def load(cls, path: str | Path) -> "BalancedSpace":
        try:
            payload = torch.load(Path(path), map_location="cpu", weights_only=True)
        except TypeError:  # pragma: no cover - compatibility with older PyTorch
            payload = torch.load(Path(path), map_location="cpu")
        if payload.get("schema_version") != "balanced-space-v1":
            raise ValueError("unsupported balanced-space artifact")
        result = cls(
            basis=payload["basis"],
            mean=payload["mean"],
            eigenvalues=payload["eigenvalues"],
            source_layer=int(payload["source_layer"]),
            upstream_layer=int(payload["upstream_layer"]),
            token_position=int(payload["token_position"]),
            rank=int(payload["rank"]),
            control_bases=dict(payload["control_bases"]),
            metadata=dict(payload["metadata"]),
        )
        if "projector" in payload:
            torch.testing.assert_close(
                result.projector,
                payload["projector"].double().cpu(),
                rtol=1e-5,
                atol=1e-6,
            )
        return result


def _validate_prefixes(
    prefixes: Sequence[Sequence[int]], model: TinyDecoderLM, label: str
) -> list[list[int]]:
    if not prefixes:
        raise ValueError(f"{label} prefixes must not be empty")
    normalized: list[list[int]] = []
    for row, prefix in enumerate(prefixes):
        values = [int(token) for token in prefix]
        if not values:
            raise ValueError(f"{label} prefix {row} is empty")
        if len(values) > model.config.max_seq_len:
            raise ValueError(f"{label} prefix {row} exceeds model context")
        if min(values) < 0 or max(values) >= model.config.vocab_size:
            raise ValueError(f"{label} prefix {row} contains an invalid token")
        # The arithmetic lab's fixed ByteTokenizer uses 258 as its prompt/answer
        # separator and 259 as EOS.  Requiring SEP at the final position makes it
        # impossible to accidentally pass a teacher-forced answer continuation to
        # the discovery routine.
        if values[-1] != 258 or 259 in values:
            raise ValueError(
                f"{label} prefix {row} must end at the ByteTokenizer SEP boundary"
            )
        normalized.append(values)
    return normalized


def _continue_to_layer(
    model: TinyDecoderLM,
    hidden: "torch.Tensor",
    completed_layers: int,
    target_completed_layers: int,
) -> "torch.Tensor":
    if not 0 <= completed_layers <= target_completed_layers <= model.config.n_layers:
        raise ValueError("invalid layer continuation interval")
    length = hidden.shape[1]
    rope_cos = model._rope_cos[:length].to(dtype=hidden.dtype)[None, None, :, :]
    rope_sin = model._rope_sin[:length].to(dtype=hidden.dtype)[None, None, :, :]
    for block in model.blocks[completed_layers:target_completed_layers]:
        hidden = block(hidden, rope_cos, rope_sin)
    return hidden


def _random_consumer_vectors(
    vocab_size: int, count: int, seed: int
) -> "torch.Tensor":
    generator = torch.Generator(device="cpu").manual_seed(seed)
    if count == 0:
        return torch.empty((0, vocab_size), dtype=torch.float64)
    signs = torch.randint(
        0, 2, (count, vocab_size), generator=generator, dtype=torch.int64
    ).mul(2).sub(1)
    return signs.double() / max(1.0, vocab_size**0.5)


def _consumer_features(
    logits: "torch.Tensor", random_vectors: "torch.Tensor"
) -> tuple["torch.Tensor", list[str]]:
    """Fixed output diagnostics that never reference the correct answer token."""

    if logits.ndim != 1:
        raise ValueError("consumer logits must be a vector")
    log_probabilities = torch.log_softmax(logits.float(), dim=-1)
    probabilities = log_probabilities.exp()
    vocab_size = logits.shape[0]
    digit_ids = torch.arange(
        ord("0"), min(ord("9") + 1, vocab_size), device=logits.device
    )
    if len(digit_ids):
        digit_mass = torch.logsumexp(log_probabilities[digit_ids], dim=0)
    else:  # pragma: no cover - the lab vocabulary always includes ASCII digits
        digit_mass = log_probabilities.mean()
    eos_id = min(259, vocab_size - 1)
    minus_id = min(ord("-"), vocab_size - 1)
    entropy = -(probabilities * log_probabilities).sum()
    maximum_log_probability = log_probabilities.max()
    features = [
        digit_mass,
        log_probabilities[eos_id],
        log_probabilities[minus_id],
        entropy,
        maximum_log_probability,
    ]
    names = [
        "digit_log_mass",
        "eos_log_probability",
        "minus_log_probability",
        "output_entropy",
        "top_log_probability",
    ]
    if random_vectors.numel():
        vectors = random_vectors.to(device=logits.device, dtype=log_probabilities.dtype)
        projected = vectors @ log_probabilities
        features.extend(projected.unbind())
        names.extend(f"sealed_vocab_projection_{index}" for index in range(len(projected)))
    return torch.stack(features), names


def _prefix_samples(
    model: TinyDecoderLM,
    prefixes: Sequence[Sequence[int]],
    config: BalancedSpaceConfig,
    device: "torch.device",
    random_vectors: "torch.Tensor",
    seed_offset: int,
    progress_phase: str,
    collect_gradients: bool = True,
) -> tuple["torch.Tensor", "torch.Tensor", "torch.Tensor", "torch.Tensor", list[str]]:
    """Return source states, causal effects/responses, and consumer gradients."""

    source_rows: list[torch.Tensor] = []
    effects: list[torch.Tensor] = []
    responses: list[torch.Tensor] = []
    gradients: list[torch.Tensor] = []
    consumer_names: list[str] | None = None
    width = model.config.d_model
    print(
        f"SPACE_PROGRESS PHASE={progress_phase} LAYER={config.source_layer} "
        f"ITEMS=0/{len(prefixes)} PERTURBATIONS_PER_ITEM={config.perturbations_per_prompt}",
        flush=True,
    )
    for prompt_index, prefix in enumerate(prefixes):
        ids = torch.tensor([list(prefix)], dtype=torch.long, device=device)
        with torch.no_grad():
            _, states = model(ids, return_hidden_states=True)
            upstream = states[config.upstream_layer].detach()
            source = states[config.source_layer].detach()
            source_vector = source[0, config.token_position]
        source_rows.append(source_vector.float().cpu())

        if collect_gradients:
            with torch.enable_grad():
                differentiable_source = source.detach().requires_grad_(True)
                clean_logits = model.continue_from_hidden(
                    differentiable_source, completed_layers=config.source_layer
                )[0, config.token_position]
                clean_features, names = _consumer_features(clean_logits, random_vectors)
                if consumer_names is None:
                    consumer_names = names
                elif consumer_names != names:  # pragma: no cover - defensive invariant
                    raise AssertionError("consumer feature ordering changed")
                for feature_index, feature in enumerate(clean_features):
                    gradient = torch.autograd.grad(
                        feature,
                        differentiable_source,
                        retain_graph=feature_index + 1 < len(clean_features),
                    )[0][0, config.token_position]
                    gradients.append(gradient.detach().float().cpu())
                clean_features_cpu = clean_features.detach().float().cpu()
        else:
            with torch.no_grad():
                clean_logits = model.continue_from_hidden(
                    source, completed_layers=config.source_layer
                )[0, config.token_position]
                clean_features, names = _consumer_features(clean_logits, random_vectors)
                if consumer_names is None:
                    consumer_names = names
                elif consumer_names != names:  # pragma: no cover - defensive invariant
                    raise AssertionError("consumer feature ordering changed")
                clean_features_cpu = clean_features.float().cpu()

        for perturbation_index in range(config.perturbations_per_prompt):
            local_seed = (
                int(config.seed)
                + int(seed_offset)
                + prompt_index * 1_000_003
                + perturbation_index * 97
            )
            generator = torch.Generator(device="cpu").manual_seed(local_seed)
            direction = torch.randn(width, generator=generator, dtype=torch.float32)
            direction /= direction.norm().clamp_min(1e-12)
            state_scale = float(
                upstream[0, config.token_position].float().norm().item()
                / max(1.0, width**0.5)
            )
            magnitude = config.perturbation_scale * max(state_scale, 1e-3) * width**0.5
            perturbation = (direction * magnitude).to(
                device=device, dtype=upstream.dtype
            )
            perturbed_upstream = upstream.clone()
            perturbed_upstream[0, config.token_position] += perturbation
            with torch.no_grad():
                perturbed_source = _continue_to_layer(
                    model,
                    perturbed_upstream,
                    config.upstream_layer,
                    config.source_layer,
                )
                effect = (
                    perturbed_source[0, config.token_position] - source_vector
                )
                perturbed_logits = model.continue_from_hidden(
                    perturbed_source, completed_layers=config.source_layer
                )[0, config.token_position]
                perturbed_features, _ = _consumer_features(
                    perturbed_logits, random_vectors
                )
            effects.append(effect.float().cpu())
            responses.append(
                perturbed_features.float().cpu() - clean_features_cpu
            )
        completed = prompt_index + 1
        if completed % 100 == 0 or completed == len(prefixes):
            print(
                f"SPACE_PROGRESS PHASE={progress_phase} LAYER={config.source_layer} "
                f"ITEMS={completed}/{len(prefixes)} "
                f"CAUSAL_SAMPLES={completed * config.perturbations_per_prompt}",
                flush=True,
            )
    if consumer_names is None:  # pragma: no cover - prefixes are validated nonempty
        raise AssertionError("consumer names were not initialized")
    return (
        torch.stack(source_rows).double(),
        torch.stack(effects).double(),
        torch.stack(responses).double(),
        (
            torch.stack(gradients).double()
            if gradients
            else torch.empty((0, width), dtype=torch.float64)
        ),
        consumer_names,
    )


def _symmetric_eigh(matrix: "torch.Tensor") -> tuple["torch.Tensor", "torch.Tensor"]:
    values, vectors = torch.linalg.eigh(0.5 * (matrix + matrix.T))
    order = torch.argsort(values, descending=True)
    return values[order], vectors[:, order]


def _orthonormalize(matrix: "torch.Tensor", columns: int) -> "torch.Tensor":
    basis, _ = torch.linalg.qr(matrix, mode="reduced")
    return basis[:, :columns]


def _causal_prediction_fraction(
    fit_effects: "torch.Tensor",
    fit_responses: "torch.Tensor",
    selection_effects: "torch.Tensor",
    selection_responses: "torch.Tensor",
    basis: "torch.Tensor",
    ridge: float,
) -> float:
    train = fit_effects @ basis
    heldout = selection_effects @ basis
    gram = train.T @ train
    weights = torch.linalg.solve(
        gram + ridge * torch.eye(gram.shape[0], dtype=gram.dtype),
        train.T @ fit_responses,
    )
    prediction = heldout @ weights
    denominator = float(selection_responses.square().sum().item())
    if denominator <= 1e-24:
        return 0.0
    fraction = 1.0 - float((selection_responses - prediction).square().sum().item()) / denominator
    return float(max(-1.0, min(1.0, fraction)))


def _rank_matched_controls(
    sources: "torch.Tensor",
    full_balanced_basis: "torch.Tensor",
    selected_rank: int,
    seed: int,
) -> dict[str, "torch.Tensor"]:
    width = sources.shape[1]
    centered = sources - sources.mean(dim=0)
    _, _, right = torch.linalg.svd(centered, full_matrices=True)
    pca = right.T[:, :selected_rank]

    generator = torch.Generator(device="cpu").manual_seed(seed)
    random_raw = torch.randn(width, selected_rank, generator=generator, dtype=torch.float64)
    random = _orthonormalize(random_raw, selected_rank)

    if full_balanced_basis.shape[1] >= 2 * selected_rank:
        complement = full_balanced_basis[:, selected_rank : 2 * selected_rank]
    else:
        candidate = full_balanced_basis[:, :selected_rank]
        raw = torch.randn(width, selected_rank, generator=generator, dtype=torch.float64)
        raw = raw - candidate @ (candidate.T @ raw)
        complement = _orthonormalize(raw, selected_rank)
    return {
        "pca": _orthonormalize(pca, selected_rank),
        "random": random,
        "complement": _orthonormalize(complement, selected_rank),
    }


def discover_balanced_space(
    model: TinyDecoderLM,
    discovery_prefixes: Sequence[Sequence[int]],
    selection_prefixes: Sequence[Sequence[int]],
    *,
    config: BalancedSpaceConfig,
    device: "torch.device",
) -> BalancedSpace:
    """Discover a candidate space without accepting any answer-side information.

    ``selection_prefixes`` are a held-out set used only for rank selection.  A
    genuinely sealed causal/behavioral evaluation must use a third set of items.
    """

    config.validate(model)
    discovery = _validate_prefixes(discovery_prefixes, model, "discovery")
    selection = _validate_prefixes(selection_prefixes, model, "selection")
    model = model.to(device).eval()
    original_flags = [parameter.requires_grad for parameter in model.parameters()]
    random_vectors = _random_consumer_vectors(
        model.config.vocab_size, config.random_output_consumers, config.seed + 41
    )
    try:
        for parameter in model.parameters():
            parameter.requires_grad_(False)
        fit_sources, fit_effects, fit_responses, fit_gradients, consumer_names = (
            _prefix_samples(
                model,
                discovery,
                config,
                device,
                random_vectors,
                seed_offset=0,
                progress_phase="DISCOVERY",
                collect_gradients=True,
            )
        )
        _, selection_effects, selection_responses, _, selection_consumer_names = (
            _prefix_samples(
                model,
                selection,
                config,
                device,
                random_vectors,
                seed_offset=100_000_019,
                progress_phase="RANK_SELECTION",
                collect_gradients=False,
            )
        )
    finally:
        for parameter, flag in zip(model.parameters(), original_flags):
            parameter.requires_grad_(flag)
    if consumer_names != selection_consumer_names:
        raise AssertionError("fit and selection consumers differ")

    width = model.config.d_model
    identity = torch.eye(width, dtype=torch.float64)
    controllability = fit_effects.T @ fit_effects / max(1, len(fit_effects))
    observability = fit_gradients.T @ fit_gradients / max(1, len(fit_gradients))
    controllability = 0.5 * (controllability + controllability.T) + config.ridge * identity
    observability = 0.5 * (observability + observability.T) + config.ridge * identity

    control_values, control_vectors = _symmetric_eigh(controllability)
    safe_control_values = control_values.clamp_min(config.ridge)
    control_sqrt = (
        control_vectors
        @ torch.diag(safe_control_values.sqrt())
        @ control_vectors.T
    )
    balanced_operator = control_sqrt @ observability @ control_sqrt
    balanced_values, balanced_vectors = _symmetric_eigh(balanced_operator)
    full_balanced_basis = _orthonormalize(
        control_sqrt @ balanced_vectors, width
    )

    ranks = sorted(set(int(rank) for rank in config.candidate_ranks))
    rank_table: list[dict[str, Any]] = []
    for rank in ranks:
        fraction = _causal_prediction_fraction(
            fit_effects,
            fit_responses,
            selection_effects,
            selection_responses,
            full_balanced_basis[:, :rank],
            config.ridge,
        )
        rank_table.append(
            {"rank": rank, "heldout_causal_prediction_fraction": fraction}
        )
    eligible = [
        row
        for row in rank_table
        if row["heldout_causal_prediction_fraction"]
        >= config.prediction_fraction_threshold
    ]
    if eligible:
        selected = eligible[0]
        selection_rule = "smallest_rank_meeting_threshold"
    else:
        selected = max(
            rank_table,
            key=lambda row: (row["heldout_causal_prediction_fraction"], -row["rank"]),
        )
        selection_rule = "best_heldout_fraction_threshold_not_met"
    selected_rank = int(selected["rank"])
    basis = full_balanced_basis[:, :selected_rank]
    controls = _rank_matched_controls(
        fit_sources, full_balanced_basis, selected_rank, config.seed + 101
    )

    positive_control_values = control_values.clamp_min(config.ridge)
    condition = float(
        (positive_control_values.max() / positive_control_values.min()).item()
    )
    metadata: dict[str, Any] = {
        "schema_version": "balanced-space-discovery-v1",
        "method": "empirical_residual_controllability_x_target_free_observability",
        "target_information_used": False,
        "prefix_only_api": True,
        "answer_boundary_enforced": "final token is ByteTokenizer SEP; EOS forbidden",
        "config": asdict(config),
        "discovery_prefixes": len(discovery),
        "selection_prefixes": len(selection),
        "fit_causal_samples": len(fit_effects),
        "selection_causal_samples": len(selection_effects),
        "consumer_names": consumer_names,
        "rank_selection": rank_table,
        "selected_rank": selected_rank,
        "rank_selection_rule": selection_rule,
        "prediction_fraction_threshold": config.prediction_fraction_threshold,
        "controllability_trace": float(controllability.trace().item()),
        "observability_trace": float(observability.trace().item()),
        "controllability_ridge_condition": condition,
        "ridge": config.ridge,
        "whitening": "eigendecomposition; C^(1/2) O C^(1/2); ridge on C and O",
        "limitations": [
            "local first-order observability around each prefix",
            "empirical residual perturbations are not exhaustive head/MLP interventions",
            "selection prefixes choose rank and are not a sealed confirmation set",
            "space existence requires independent behavioral and causal controls",
        ],
    }
    return BalancedSpace(
        basis=basis,
        mean=fit_sources.mean(dim=0),
        eigenvalues=balanced_values.clamp_min(0),
        source_layer=config.source_layer,
        upstream_layer=config.upstream_layer,
        token_position=config.token_position,
        rank=selected_rank,
        control_bases=controls,
        metadata=metadata,
    )


__all__ = [
    "BalancedSpace",
    "BalancedSpaceConfig",
    "discover_balanced_space",
]
