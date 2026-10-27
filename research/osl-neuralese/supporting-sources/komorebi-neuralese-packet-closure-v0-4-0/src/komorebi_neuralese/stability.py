from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product
from typing import Iterable

import torch

from .models import LinearHyperOperatorRNN


@dataclass(frozen=True)
class ObservabilityResult:
    rank: int
    null_dimension: int
    singular_values: tuple[float, ...]
    relative_tolerance: float
    max_depth: int
    episodes: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class FeshbachResult:
    retained_dimension: int
    nuisance_dimension: int
    nuisance_algebra_dimension: int
    mixed_return_max_frobenius: float
    mixed_return_mean_frobenius: float
    mixed_return_rank: int
    mixed_return_singular_values: tuple[float, ...]
    closed_at_tolerance: bool
    relative_tolerance: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def centered_decoder(decoder_weight: torch.Tensor) -> torch.Tensor:
    """Remove the behaviorally irrelevant common-logit direction."""

    # The audit is rank-sensitive.  Centering float32 rows and only then
    # promoting the result leaves a round-off singular value that can be
    # mistaken for a genuine eighth observable direction.
    decoder_weight = decoder_weight.to(torch.float64)
    classes = decoder_weight.shape[0]
    centering = torch.eye(classes, dtype=decoder_weight.dtype, device=decoder_weight.device)
    centering = centering - torch.ones_like(centering) / classes
    return centering @ decoder_weight


def projective_anchor_defect(
    codes: torch.Tensor,
    tables: torch.Tensor,
    basis: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Anchor intertwining error after quotienting each code by positive scale.

    Projective recurrence identifies ``M`` and ``alpha M`` for positive
    ``alpha``.  The ordinary anchor defect therefore confounds angular error
    with the learned matrix scale.  This function fits the least-squares
    scalar in ``alpha * M B ~= B P`` and reports a scale-free residual.
    """

    observed = codes @ basis
    target = basis @ tables.transpose(-1, -2)
    numerator = (observed * target).sum(dim=(-2, -1))
    denominator = observed.square().sum(dim=(-2, -1)).clamp_min(1e-30)
    scalar = numerator / denominator
    residual = scalar[..., None, None] * observed - target
    defect = torch.linalg.matrix_norm(residual, ord="fro", dim=(-2, -1))
    defect = defect / torch.linalg.matrix_norm(target, ord="fro", dim=(-2, -1)).clamp_min(1e-30)
    return defect, scalar


def conformal_metric_defect(
    codes: torch.Tensor,
    metric: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Metric-isometry error modulo the best nonnegative conformal scale."""

    pulled_back = codes.transpose(-1, -2) @ metric @ codes
    metric_norm_squared = metric.square().sum().clamp_min(1e-30)
    scale = (pulled_back * metric).sum(dim=(-2, -1)) / metric_norm_squared
    scale = scale.clamp_min(0.0)
    residual = pulled_back - scale[..., None, None] * metric
    defect = torch.linalg.matrix_norm(residual, ord="fro", dim=(-2, -1))
    defect = defect / torch.linalg.matrix_norm(pulled_back, ord="fro", dim=(-2, -1)).clamp_min(1e-30)
    return defect, scale


def anchor_basis(model: LinearHyperOperatorRNN) -> torch.Tensor:
    """Return the state anchors as columns of an ambient latent basis."""

    basis = model.state_embedding.weight.transpose(0, 1)
    if basis.shape[0] != basis.shape[1]:
        raise ValueError("anchor closure currently requires hidden_dim == number of states")
    return basis


def anchor_metric(model: LinearHyperOperatorRNN, normalize_trace: bool = True) -> torch.Tensor:
    """Metric for which exact anchor transports are isometries."""

    basis = anchor_basis(model)
    inverse = torch.linalg.inv(basis)
    metric = inverse.transpose(0, 1) @ inverse
    metric = (metric + metric.transpose(0, 1)) / 2
    if normalize_trace:
        metric = metric * (metric.shape[0] / torch.trace(metric))
    return metric


def anchor_closed_codes(model: LinearHyperOperatorRNN, tables: torch.Tensor) -> torch.Tensor:
    """Compile visible permutation tables into an exact latent representation.

    The table convention stores source states in rows. Its transpose acts on
    one-hot column states. If B contains the learned state embeddings as
    columns, B P B^{-1} is therefore the exact latent transport.
    """

    basis = anchor_basis(model)
    inverse = torch.linalg.inv(basis)
    permutation = tables.transpose(-1, -2)
    return basis @ permutation @ inverse


def normalized_anchor_defect(
    codes: torch.Tensor,
    tables: torch.Tensor,
    basis: torch.Tensor,
) -> torch.Tensor:
    target = basis @ tables.transpose(-1, -2)
    residual = codes @ basis - target
    numerator = torch.linalg.matrix_norm(residual, ord="fro", dim=(-2, -1))
    denominator = torch.linalg.matrix_norm(target, ord="fro", dim=(-2, -1)).clamp_min(1e-12)
    return numerator / denominator


def normalized_metric_defect(codes: torch.Tensor, metric: torch.Tensor) -> torch.Tensor:
    left = codes.transpose(-1, -2) @ metric @ codes
    residual = left - metric
    numerator = torch.linalg.matrix_norm(residual, ord="fro", dim=(-2, -1))
    denominator = torch.linalg.matrix_norm(metric, ord="fro").clamp_min(1e-12)
    return numerator / denominator


def metric_polar_codes(codes: torch.Tensor, metric: torch.Tensor) -> torch.Tensor:
    """Project matrices to the nearest isometries after metric whitening."""

    eigenvalues, eigenvectors = torch.linalg.eigh(metric)
    if float(eigenvalues.min()) <= 0:
        raise ValueError("metric must be positive definite")
    sqrt = (eigenvectors * eigenvalues.sqrt().unsqueeze(0)) @ eigenvectors.transpose(0, 1)
    inverse_sqrt = (eigenvectors * eigenvalues.rsqrt().unsqueeze(0)) @ eigenvectors.transpose(0, 1)
    whitened = sqrt @ codes @ inverse_sqrt
    left, _, right_h = torch.linalg.svd(whitened)
    orthogonal = left @ right_h
    return inverse_sqrt @ orthogonal @ sqrt


def future_observability(
    decoder_weight: torch.Tensor,
    code_batches: torch.Tensor,
    max_depth: int = 4,
    relative_tolerance: float = 1e-6,
    episode_limit: int | None = 32,
) -> ObservabilityResult:
    """Finite-horizon future observability of linear latent perturbations.

    This is a cross-episode diagnostic, not an infinite-horizon certificate.
    Products use the exact recurrent column-vector ordering.
    """

    if code_batches.ndim != 4:
        raise ValueError("code_batches must have shape (episodes, operators, dim, dim)")
    if max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    codes = code_batches[:episode_limit] if episode_limit is not None else code_batches
    codes = codes.to(torch.float64)
    observation = centered_decoder(decoder_weight)
    dimension = code_batches.shape[-1]
    rows: list[torch.Tensor] = []
    identity = torch.eye(dimension, dtype=codes.dtype, device=codes.device)
    for episode_codes in codes:
        frontier = [identity]
        rows.append(observation)
        for _ in range(max_depth):
            frontier = [operator @ prefix for prefix in frontier for operator in episode_codes]
            rows.extend(observation @ prefix for prefix in frontier)
    stacked = torch.cat(rows, dim=0)
    singular = torch.linalg.svdvals(stacked)
    threshold = float(singular[0]) * relative_tolerance if singular.numel() else 0.0
    rank = int((singular > threshold).sum())
    return ObservabilityResult(
        rank=rank,
        null_dimension=dimension - rank,
        singular_values=tuple(float(value) for value in singular),
        relative_tolerance=relative_tolerance,
        max_depth=max_depth,
        episodes=int(codes.shape[0]),
    )


def relation_product(codes: torch.Tensor, slots: torch.Tensor) -> torch.Tensor:
    batch = codes.shape[0]
    dimension = codes.shape[-1]
    rows = torch.arange(batch, device=codes.device)
    result = torch.eye(dimension, dtype=codes.dtype, device=codes.device).expand(batch, -1, -1).clone()
    for index in range(slots.shape[1]):
        result = codes[rows, slots[:, index]] @ result
    return result


def normalized_holonomy(product_matrix: torch.Tensor, metric: torch.Tensor | None = None) -> torch.Tensor:
    dimension = product_matrix.shape[-1]
    identity = torch.eye(dimension, dtype=product_matrix.dtype, device=product_matrix.device)
    residual = product_matrix - identity
    if metric is not None:
        eigenvalues, eigenvectors = torch.linalg.eigh(metric)
        sqrt = (eigenvectors * eigenvalues.clamp_min(1e-12).sqrt().unsqueeze(0)) @ eigenvectors.transpose(0, 1)
        residual = sqrt @ residual @ torch.linalg.inv(sqrt)
    numerator = torch.linalg.matrix_norm(residual, ord="fro", dim=(-2, -1))
    return numerator / (dimension**0.5)


def projective_holonomy(
    product_matrix: torch.Tensor,
    metric: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Residual from the best scalar identity, plus the fitted scalar."""

    dimension = product_matrix.shape[-1]
    transformed = product_matrix
    if metric is not None:
        eigenvalues, eigenvectors = torch.linalg.eigh(metric)
        sqrt = (eigenvectors * eigenvalues.clamp_min(1e-12).sqrt().unsqueeze(0)) @ eigenvectors.transpose(0, 1)
        inverse_sqrt = torch.linalg.inv(sqrt)
        transformed = sqrt @ product_matrix @ inverse_sqrt
    scalar = torch.diagonal(transformed, dim1=-2, dim2=-1).sum(-1) / dimension
    identity = torch.eye(dimension, dtype=transformed.dtype, device=transformed.device)
    residual = transformed - scalar[..., None, None] * identity
    numerator = torch.linalg.matrix_norm(residual, ord="fro", dim=(-2, -1))
    denominator = scalar.abs().clamp_min(1e-12) * (dimension**0.5)
    return numerator / denominator, scalar


def _append_independent_matrix(
    orthonormal_vectors: list[torch.Tensor],
    matrix: torch.Tensor,
    relative_tolerance: float,
) -> bool:
    vector = matrix.reshape(-1).to(torch.float64)
    original_norm = torch.linalg.vector_norm(vector)
    if float(original_norm) == 0:
        return False
    residual = vector.clone()
    for basis_vector in orthonormal_vectors:
        residual = residual - torch.dot(basis_vector, residual) * basis_vector
    residual_norm = torch.linalg.vector_norm(residual)
    if float(residual_norm) <= relative_tolerance * max(1.0, float(original_norm)):
        return False
    orthonormal_vectors.append(residual / residual_norm)
    return True


def nuisance_algebra_basis(
    nuisance_operators: torch.Tensor,
    relative_tolerance: float = 1e-9,
) -> torch.Tensor:
    """Basis of span{I, D_word} for a switched nuisance family."""

    if nuisance_operators.ndim != 3:
        raise ValueError("nuisance_operators must have shape (operators, q, q)")
    q = nuisance_operators.shape[-1]
    if q == 0:
        return nuisance_operators.new_zeros((0, 0, 0))
    dtype = nuisance_operators.dtype
    device = nuisance_operators.device
    matrices: list[torch.Tensor] = [torch.eye(q, dtype=dtype, device=device)]
    vectors: list[torch.Tensor] = []
    _append_independent_matrix(vectors, matrices[0], relative_tolerance)
    cursor = 0
    while cursor < len(matrices) and len(matrices) < q * q:
        current = matrices[cursor]
        cursor += 1
        for operator in nuisance_operators:
            for candidate in (operator @ current, current @ operator):
                if _append_independent_matrix(vectors, candidate, relative_tolerance):
                    matrices.append(candidate)
                    if len(matrices) == q * q:
                        break
            if len(matrices) == q * q:
                break
    return torch.stack(matrices)


def feshbach_blocks(
    operators: torch.Tensor,
    retained_basis: torch.Tensor,
    nuisance_basis: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return A, B, C, D blocks in orthonormal P/Q coordinates."""

    p = retained_basis
    q = nuisance_basis
    a = p.transpose(0, 1) @ operators @ p
    b = p.transpose(0, 1) @ operators @ q
    c = q.transpose(0, 1) @ operators @ p
    d = q.transpose(0, 1) @ operators @ q
    return a, b, c, d


def switched_feshbach_analysis(
    operators: torch.Tensor,
    retained_basis: torch.Tensor,
    nuisance_basis: torch.Tensor,
    relative_tolerance: float = 1e-8,
) -> FeshbachResult:
    """Finite exact switched-return test using the generated nuisance algebra."""

    p_dim = retained_basis.shape[1]
    q_dim = nuisance_basis.shape[1]
    if q_dim == 0:
        return FeshbachResult(
            retained_dimension=p_dim,
            nuisance_dimension=0,
            nuisance_algebra_dimension=0,
            mixed_return_max_frobenius=0.0,
            mixed_return_mean_frobenius=0.0,
            mixed_return_rank=0,
            mixed_return_singular_values=(),
            closed_at_tolerance=True,
            relative_tolerance=relative_tolerance,
        )
    _, b, c, d = feshbach_blocks(operators, retained_basis, nuisance_basis)
    algebra = nuisance_algebra_basis(d, relative_tolerance=max(relative_tolerance * 0.1, 1e-12))
    moments = []
    observable_rows = []
    reachable_columns = []
    for left_index, left in enumerate(b):
        for algebra_matrix in algebra:
            observable_rows.append(left @ algebra_matrix)
            for right in c:
                moments.append(left @ algebra_matrix @ right)
    for algebra_matrix in algebra:
        for right in c:
            reachable_columns.append(algebra_matrix @ right)
    norms = torch.stack([torch.linalg.matrix_norm(moment, ord="fro") for moment in moments])
    observable = torch.cat(observable_rows, dim=0).to(torch.float64)
    reachable = torch.cat(reachable_columns, dim=1).to(torch.float64)
    hankel = observable @ reachable
    singular = torch.linalg.svdvals(hankel)
    threshold = float(singular[0]) * relative_tolerance if singular.numel() else 0.0
    rank = int((singular > threshold).sum())
    scale = max(
        1.0,
        max(float(torch.linalg.matrix_norm(matrix, ord="fro")) for matrix in operators),
    )
    max_norm = float(norms.max()) if norms.numel() else 0.0
    return FeshbachResult(
        retained_dimension=p_dim,
        nuisance_dimension=q_dim,
        nuisance_algebra_dimension=int(algebra.shape[0]),
        mixed_return_max_frobenius=max_norm,
        mixed_return_mean_frobenius=float(norms.mean()) if norms.numel() else 0.0,
        mixed_return_rank=rank,
        mixed_return_singular_values=tuple(float(value) for value in singular),
        closed_at_tolerance=bool(max_norm <= relative_tolerance * scale),
        relative_tolerance=relative_tolerance,
    )


def enumerate_word_products(operators: torch.Tensor, depth: int) -> Iterable[torch.Tensor]:
    dimension = operators.shape[-1]
    identity = torch.eye(dimension, dtype=operators.dtype, device=operators.device)
    for word in product(range(operators.shape[0]), repeat=depth):
        result = identity
        for operator in word:
            result = operators[operator] @ result
        yield result
