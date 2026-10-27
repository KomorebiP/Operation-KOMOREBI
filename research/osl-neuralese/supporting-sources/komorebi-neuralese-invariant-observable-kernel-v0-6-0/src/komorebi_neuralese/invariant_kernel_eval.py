"""Fail-closed evaluation for the v0.6 invariant observable kernel.

The behavioral geometry is deliberately ``7 + 1 + 4`` rather than an
undifferentiated eight-dimensional "semantic" subspace:

``S``
    Seven contrast directions that can change an eight-way decision.
``L``
    One common-logit gauge line.  It may add the same scalar to every logit,
    but it is annihilated by the centered decoder.
``K``
    Four ambient fiber directions.  They are decoder-null and may carry
    vertical holonomy, but must never leak into ``S`` or ``L``.

All rank-sensitive calculations in this module first promote the *executed*
tensors to float64.  Promotion cannot recover information lost in float32,
but it prevents the audit itself from introducing an avoidable rank error.
Malformed, missing, non-finite, or numerically ambiguous inputs never receive
a passing receipt.

The intervention routines use explicitly non-zero synthetic vectors in ``L``
and ``K``.  This establishes structural invariance of those fibers.  It does
not turn a compiled hard control into evidence of learned memory.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Mapping, Sequence

import torch


DEFAULT_SUFFIX_LENGTHS = (0, 1, 2, 4, 8, 16, 32)


class AssayIntegrityError(RuntimeError):
    """Raised when an invariant-kernel assay cannot be interpreted safely."""


@dataclass(frozen=True)
class KernelStructureAudit:
    hidden_dimension: int
    behavioral_rank: int
    common_rank: int
    ambient_rank: int
    centered_null_rank: int
    expected_behavioral_rank: int
    expected_common_rank: int
    expected_ambient_rank: int
    centered_decoder_rank: int
    expected_centered_decoder_rank: int
    rank_ambiguous: bool
    behavioral_symmetry_residual: float
    common_symmetry_residual: float
    ambient_symmetry_residual: float
    behavioral_idempotence_residual: float
    common_idempotence_residual: float
    ambient_idempotence_residual: float
    partition_residual: float
    pairwise_projector_residual: float
    centered_decoder_null_residual: float
    ambient_raw_decoder_residual: float
    behavioral_decoder_completeness_residual: float
    operator_orthogonality_residual: float
    behavioral_to_null_leakage: float
    null_to_behavioral_leakage: float
    behavioral_to_common_leakage: float
    common_to_behavioral_leakage: float
    behavioral_to_ambient_leakage: float
    ambient_to_behavioral_leakage: float
    common_to_ambient_leakage: float
    ambient_to_common_leakage: float
    common_line_action_residual: float
    tolerance: float
    all_finite: bool
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SuffixLeakageLevel:
    length: int
    products: int
    behavioral_to_null: float
    null_to_behavioral: float
    behavioral_to_common: float
    common_to_behavioral: float
    behavioral_to_ambient: float
    ambient_to_behavioral: float
    common_to_ambient: float
    ambient_to_common: float
    common_line_action_residual: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SuffixLeakageAudit:
    required_lengths: tuple[int, ...]
    levels: tuple[SuffixLeakageLevel, ...]
    observer_singular_values: tuple[float, ...]
    observer_rank: int
    sigma_behavioral_relative: float
    sigma_first_null_relative: float
    sigma_behavioral_floor: float
    sigma_first_null_ceiling: float
    maximum_behavioral_to_null: float
    maximum_null_to_behavioral: float
    maximum_common_ambient_mixing: float
    maximum_common_line_action_residual: float
    tolerance: float
    all_finite: bool
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["levels"] = [level.to_dict() for level in self.levels]
        return row


@dataclass(frozen=True)
class PathDefectAudit:
    cases: int
    quotient_defects: tuple[float, ...]
    common_defects: tuple[float, ...]
    vertical_defects: tuple[float, ...]
    behavioral_to_null_defects: tuple[float, ...]
    null_to_behavioral_defects: tuple[float, ...]
    full_defects: tuple[float, ...]
    maximum_quotient_defect: float
    maximum_common_defect: float
    maximum_vertical_defect: float
    maximum_behavioral_to_null_defect: float
    maximum_null_to_behavioral_defect: float
    maximum_full_defect: float
    quotient_flat: bool
    common_flat: bool
    vertical_flat: bool
    full_flat: bool
    vertical_curvature_only: bool
    tolerance: float
    curvature_detection_floor: float
    all_finite: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FiberInterventionLevel:
    length: int
    products: int
    ambient_injection_effect: float
    ambient_transplant_effect_per_unit: float
    common_injection_effect: float
    common_transplant_effect_per_unit: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FiberInterventionAudit:
    required_lengths: tuple[int, ...]
    levels: tuple[FiberInterventionLevel, ...]
    ambient_probe_dimension: int
    common_probe_dimension: int
    minimum_ambient_probe_norm: float
    minimum_common_probe_norm: float
    minimum_ambient_transplant_distance: float
    minimum_common_transplant_distance: float
    maximum_ambient_injection_effect: float
    maximum_ambient_transplant_effect_per_unit: float
    maximum_common_injection_effect: float
    maximum_common_transplant_effect_per_unit: float
    tolerance: float
    all_finite: bool
    passed: bool
    memory_claim_eligible: bool = False
    evidence_scope: str = "synthetic_nonzero_fiber_invariance_not_learned_memory"

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["levels"] = [level.to_dict() for level in self.levels]
        return row


@dataclass(frozen=True)
class SemanticTransplantAudit:
    total_pairs: int
    eligible_pairs: int
    successful_pairs: int
    eligibility_fraction: float
    success_rate: float
    recipient_native_robust: int
    donor_native_robust: int
    distinct_exact_targets: int
    nontrivial_semantic_displacements: int
    minimum_eligible_semantic_displacement: float
    minimum_success_margin: float | None
    margin_tau: float
    exact_eligibility_enforced: bool
    all_finite: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GaugeCovarianceAudit:
    gauge_orthogonality_residual: float
    structure_scalar_delta: float
    suffix_scalar_delta: float
    quotient_path_delta: float
    common_path_delta: float
    vertical_path_delta: float
    centered_continuation_operator_delta: float
    rank_preserved: bool
    tolerance: float
    all_finite: bool
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExtractedKernelGeometry:
    """Model tensors plus a receipt for how the behavioral projector was set.

    ``common_projector`` and ``ambient_projector`` are ``None`` unless the
    architecture itself registers that split.  In particular, neither a
    learned rank-seven observer nor a post-training SVD is allowed to invent a
    scientifically ungrounded 1+4 decomposition of its five-dimensional null.
    """

    behavioral_projector: torch.Tensor
    centered_null_projector: torch.Tensor
    common_projector: torch.Tensor | None
    ambient_projector: torch.Tensor | None
    decoder_weight: torch.Tensor
    operator_codes: torch.Tensor
    source: str
    three_way_registered: bool
    observer_singular_values: tuple[float, ...]
    observer_rank: int
    sigma_behavioral_relative: float
    sigma_first_null_relative: float
    extraction_valid: bool
    failure_reason: str | None

    def receipt(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "three_way_registered": self.three_way_registered,
            "observer_singular_values": list(self.observer_singular_values),
            "observer_rank": self.observer_rank,
            "sigma_behavioral_relative": self.sigma_behavioral_relative,
            "sigma_first_null_relative": self.sigma_first_null_relative,
            "extraction_valid": self.extraction_valid,
            "failure_reason": self.failure_reason,
            "behavioral_projector_shape": list(self.behavioral_projector.shape),
            "centered_null_projector_shape": list(self.centered_null_projector.shape),
        }


@dataclass(frozen=True)
class TwoWayStructureAudit:
    hidden_dimension: int
    behavioral_rank: int
    centered_null_rank: int
    centered_decoder_rank: int
    rank_ambiguous: bool
    behavioral_idempotence_residual: float
    centered_null_idempotence_residual: float
    partition_residual: float
    projector_orthogonality_residual: float
    centered_decoder_null_residual: float
    behavioral_decoder_completeness_residual: float
    operator_orthogonality_residual: float
    behavioral_to_null_leakage: float
    null_to_behavioral_leakage: float
    tolerance: float
    all_finite: bool
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TwoWaySuffixAudit:
    required_lengths: tuple[int, ...]
    observer_singular_values: tuple[float, ...]
    observer_rank: int
    sigma_behavioral_relative: float
    sigma_first_null_relative: float
    maximum_behavioral_to_null: float
    maximum_null_to_behavioral: float
    by_length: tuple[tuple[int, float, float], ...]
    tolerance: float
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["by_length"] = [
            {
                "length": length,
                "behavioral_to_null": forward,
                "null_to_behavioral": reverse,
            }
            for length, forward, reverse in self.by_length
        ]
        return row


@dataclass(frozen=True)
class TwoWayPathAudit:
    cases: int
    maximum_quotient_defect: float
    maximum_null_defect: float
    maximum_behavioral_to_null_defect: float
    maximum_null_to_behavioral_defect: float
    maximum_full_defect: float
    quotient_flat: bool
    null_flat: bool
    full_flat: bool
    tolerance: float
    all_finite: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NullInterventionAudit:
    null_dimension: int
    required_lengths: tuple[int, ...]
    minimum_probe_norm: float
    minimum_transplant_distance: float
    maximum_injection_effect: float
    maximum_transplant_effect_per_unit: float
    by_length: tuple[tuple[int, float, float], ...]
    tolerance: float
    passed: bool
    memory_claim_eligible: bool = False
    evidence_scope: str = "untyped_null_invariance_not_learned_memory"

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["by_length"] = [
            {
                "length": length,
                "injection_effect": injection,
                "transplant_effect_per_unit": transplant,
            }
            for length, injection, transplant in self.by_length
        ]
        return row


def centered_decoder(decoder_weight: torch.Tensor) -> torch.Tensor:
    """Return the float64 decoder after removing the common-logit direction."""

    decoder = _floating_tensor("decoder_weight", decoder_weight, minimum_ndim=2)
    if decoder.ndim != 2 or decoder.shape[0] < 2 or decoder.shape[1] < 1:
        raise AssayIntegrityError("decoder_weight must have shape (classes>=2, hidden>=1)")
    decoder = decoder.to(torch.float64)
    classes = int(decoder.shape[0])
    identity = torch.eye(classes, dtype=torch.float64, device=decoder.device)
    centering = identity - torch.ones_like(identity) / float(classes)
    result = centering @ decoder
    _require_finite("centered decoder", result)
    return result


def build_suffix_word_bank(
    *,
    operator_count: int,
    samples_per_length: int,
    seed: int,
    lengths: Sequence[int] = DEFAULT_SUFFIX_LENGTHS,
) -> dict[int, torch.Tensor]:
    """Build a deterministic, local-RNG continuation bank.

    Every positive-length stratum starts with constant words for each operator,
    followed by seeded random words.  The construction therefore cannot omit a
    generator merely by chance.
    """

    for name, value in (
        ("operator_count", operator_count),
        ("samples_per_length", samples_per_length),
        ("seed", seed),
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
    if operator_count < 1 or samples_per_length < operator_count:
        raise ValueError("samples_per_length must be at least operator_count >= 1")
    normalized = _validate_required_lengths(lengths)
    generator = torch.Generator(device="cpu").manual_seed(seed)
    result: dict[int, torch.Tensor] = {}
    for length in normalized:
        if length == 0:
            result[length] = torch.empty((samples_per_length, 0), dtype=torch.long)
            continue
        words = torch.randint(
            0,
            operator_count,
            (samples_per_length, length),
            generator=generator,
            dtype=torch.long,
        )
        for operator in range(operator_count):
            words[operator].fill_(operator)
        result[length] = words
    return result


def path_products(operator_codes: torch.Tensor, words: torch.Tensor) -> torch.Tensor:
    """Execute words with the recurrent column-vector ordering.

    ``operator_codes`` may have shape ``(operators,d,d)`` or
    ``(contexts,operators,d,d)``.  Words may be shared across contexts with
    shape ``(cases,length)`` or supplied per context as
    ``(contexts,cases,length)``.  The result always has shape
    ``(contexts,cases,d,d)``.
    """

    codes = _floating_tensor("operator_codes", operator_codes, minimum_ndim=3).to(torch.float64)
    if codes.ndim == 3:
        codes = codes.unsqueeze(0)
    if codes.ndim != 4 or codes.shape[-1] != codes.shape[-2]:
        raise AssayIntegrityError(
            "operator_codes must have shape (operators,d,d) or (contexts,operators,d,d)"
        )
    if codes.shape[0] < 1 or codes.shape[1] < 1:
        raise AssayIntegrityError("operator_codes cannot have an empty context/operator axis")
    indexed = _integer_tensor("words", words)
    if indexed.ndim == 2:
        indexed = indexed.unsqueeze(0).expand(codes.shape[0], -1, -1)
    if indexed.ndim != 3 or indexed.shape[0] != codes.shape[0] or indexed.shape[1] < 1:
        raise AssayIntegrityError(
            "words must have shape (cases,length) or (contexts,cases,length)"
        )
    if indexed.numel() and (int(indexed.min()) < 0 or int(indexed.max()) >= codes.shape[1]):
        raise AssayIntegrityError("word contains an out-of-range operator index")
    indexed = indexed.to(device=codes.device, dtype=torch.long)
    contexts, cases = indexed.shape[:2]
    dimension = int(codes.shape[-1])
    result = torch.eye(dimension, dtype=torch.float64, device=codes.device)
    result = result.expand(contexts, cases, -1, -1).clone()
    rows = torch.arange(contexts, device=codes.device)[:, None].expand(contexts, cases)
    for step in range(indexed.shape[2]):
        selected = codes[rows, indexed[:, :, step]]
        result = selected @ result
    _require_finite("path products", result)
    return result


def audit_kernel_structure(
    behavioral_projector: torch.Tensor,
    common_projector: torch.Tensor,
    ambient_projector: torch.Tensor,
    decoder_weight: torch.Tensor,
    operator_codes: torch.Tensor,
    *,
    expected_behavioral_rank: int = 7,
    expected_common_rank: int = 1,
    expected_ambient_rank: int = 4,
    tolerance: float = 5e-6,
    rank_tolerance: float = 5e-6,
) -> KernelStructureAudit:
    """Audit the complete 7+1+4 split and one-step invariance contract."""

    tolerance = _positive_finite("tolerance", tolerance)
    rank_tolerance = _positive_finite("rank_tolerance", rank_tolerance)
    ranks_expected = (expected_behavioral_rank, expected_common_rank, expected_ambient_rank)
    if any(isinstance(rank, bool) or not isinstance(rank, int) or rank < 1 for rank in ranks_expected):
        raise AssayIntegrityError("expected projector ranks must be positive integers")

    s, line, fiber = _prepare_three_way_split(
        behavioral_projector, common_projector, ambient_projector
    )
    dimension = int(s.shape[0])
    if sum(ranks_expected) != dimension:
        raise AssayIntegrityError("expected projector ranks must sum to hidden dimension")
    decoder = _floating_tensor("decoder_weight", decoder_weight, minimum_ndim=2).to(
        device=s.device, dtype=torch.float64
    )
    if decoder.ndim != 2 or decoder.shape[1] != dimension or decoder.shape[0] < 2:
        raise AssayIntegrityError("decoder_weight has incompatible dimensions")
    centered = centered_decoder(decoder).to(device=s.device)
    codes = _square_matrix_batch("operator_codes", operator_codes, dimension, s.device)
    identity = torch.eye(dimension, dtype=torch.float64, device=s.device)
    null = line + fiber

    rank_s, ambiguity_s = _projector_rank(s, rank_tolerance)
    rank_l, ambiguity_l = _projector_rank(line, rank_tolerance)
    rank_k, ambiguity_k = _projector_rank(fiber, rank_tolerance)
    rank_n, ambiguity_n = _projector_rank(null, rank_tolerance)
    decoder_rank, decoder_ambiguous = _matrix_rank(centered, rank_tolerance)
    expected_decoder_rank = min(int(decoder.shape[0]) - 1, expected_behavioral_rank)
    rank_ambiguous = ambiguity_s or ambiguity_l or ambiguity_k or ambiguity_n or decoder_ambiguous

    symmetry_s = _spectral(s - s.T)
    symmetry_l = _spectral(line - line.T)
    symmetry_k = _spectral(fiber - fiber.T)
    idem_s = _spectral(s @ s - s)
    idem_l = _spectral(line @ line - line)
    idem_k = _spectral(fiber @ fiber - fiber)
    partition = _spectral(s + line + fiber - identity)
    pairwise = max(
        _spectral(s @ line),
        _spectral(line @ s),
        _spectral(s @ fiber),
        _spectral(fiber @ s),
        _spectral(line @ fiber),
        _spectral(fiber @ line),
    )
    decoder_null = _spectral(centered @ null)
    ambient_raw_decoder = _spectral(decoder @ fiber)
    decoder_complete = _spectral(centered - centered @ s)
    operator_orthogonality = _max_spectral(codes.transpose(-1, -2) @ codes - identity)

    s_to_n = _max_spectral(null @ codes @ s)
    n_to_s = _max_spectral(s @ codes @ null)
    s_to_l = _max_spectral(line @ codes @ s)
    l_to_s = _max_spectral(s @ codes @ line)
    s_to_k = _max_spectral(fiber @ codes @ s)
    k_to_s = _max_spectral(s @ codes @ fiber)
    l_to_k = _max_spectral(fiber @ codes @ line)
    k_to_l = _max_spectral(line @ codes @ fiber)
    common_action = _max_spectral(line @ (codes - identity) @ line)

    scalars = (
        symmetry_s,
        symmetry_l,
        symmetry_k,
        idem_s,
        idem_l,
        idem_k,
        partition,
        pairwise,
        decoder_null,
        ambient_raw_decoder,
        decoder_complete,
        operator_orthogonality,
        s_to_n,
        n_to_s,
        s_to_l,
        l_to_s,
        s_to_k,
        k_to_s,
        l_to_k,
        k_to_l,
        common_action,
    )
    all_finite = all(math.isfinite(value) for value in scalars)
    rank_valid = (
        rank_s == expected_behavioral_rank
        and rank_l == expected_common_rank
        and rank_k == expected_ambient_rank
        and rank_n == expected_common_rank + expected_ambient_rank
        and decoder_rank == expected_decoder_rank
        and not rank_ambiguous
    )
    passed = all_finite and rank_valid and all(value <= tolerance for value in scalars)
    return KernelStructureAudit(
        hidden_dimension=dimension,
        behavioral_rank=rank_s,
        common_rank=rank_l,
        ambient_rank=rank_k,
        centered_null_rank=rank_n,
        expected_behavioral_rank=expected_behavioral_rank,
        expected_common_rank=expected_common_rank,
        expected_ambient_rank=expected_ambient_rank,
        centered_decoder_rank=decoder_rank,
        expected_centered_decoder_rank=expected_decoder_rank,
        rank_ambiguous=rank_ambiguous,
        behavioral_symmetry_residual=symmetry_s,
        common_symmetry_residual=symmetry_l,
        ambient_symmetry_residual=symmetry_k,
        behavioral_idempotence_residual=idem_s,
        common_idempotence_residual=idem_l,
        ambient_idempotence_residual=idem_k,
        partition_residual=partition,
        pairwise_projector_residual=pairwise,
        centered_decoder_null_residual=decoder_null,
        ambient_raw_decoder_residual=ambient_raw_decoder,
        behavioral_decoder_completeness_residual=decoder_complete,
        operator_orthogonality_residual=operator_orthogonality,
        behavioral_to_null_leakage=s_to_n,
        null_to_behavioral_leakage=n_to_s,
        behavioral_to_common_leakage=s_to_l,
        common_to_behavioral_leakage=l_to_s,
        behavioral_to_ambient_leakage=s_to_k,
        ambient_to_behavioral_leakage=k_to_s,
        common_to_ambient_leakage=l_to_k,
        ambient_to_common_leakage=k_to_l,
        common_line_action_residual=common_action,
        tolerance=tolerance,
        all_finite=all_finite,
        passed=passed,
    )


def suffix_leakage_audit(
    behavioral_projector: torch.Tensor,
    common_projector: torch.Tensor,
    ambient_projector: torch.Tensor,
    decoder_weight: torch.Tensor,
    operator_codes: torch.Tensor,
    suffix_words: Mapping[int, torch.Tensor],
    *,
    required_lengths: Sequence[int] = DEFAULT_SUFFIX_LENGTHS,
    expected_behavioral_rank: int = 7,
    tolerance: float = 5e-6,
    rank_tolerance: float = 5e-6,
    sigma_behavioral_floor: float = 1e-4,
    sigma_first_null_ceiling: float = 5e-6,
) -> SuffixLeakageAudit:
    """Audit leakage and future observability over the frozen suffix grid."""

    tolerance = _positive_finite("tolerance", tolerance)
    rank_tolerance = _positive_finite("rank_tolerance", rank_tolerance)
    sigma_behavioral_floor = _positive_finite(
        "sigma_behavioral_floor", sigma_behavioral_floor
    )
    sigma_first_null_ceiling = _positive_finite(
        "sigma_first_null_ceiling", sigma_first_null_ceiling
    )
    lengths = _validate_suffix_mapping(suffix_words, required_lengths)
    s, line, fiber = _prepare_three_way_split(
        behavioral_projector, common_projector, ambient_projector
    )
    dimension = int(s.shape[0])
    codes = _square_matrix_batch("operator_codes", operator_codes, dimension, s.device)
    decoder = _floating_tensor("decoder_weight", decoder_weight, minimum_ndim=2).to(
        device=s.device, dtype=torch.float64
    )
    if decoder.ndim != 2 or decoder.shape[1] != dimension:
        raise AssayIntegrityError("decoder_weight has incompatible dimensions")
    observer = centered_decoder(decoder).to(device=s.device)
    null = line + fiber
    identity = torch.eye(dimension, dtype=torch.float64, device=s.device)
    levels: list[SuffixLeakageLevel] = []
    observer_rows: list[torch.Tensor] = []
    for length in lengths:
        words = suffix_words[length]
        products = path_products(codes, words).to(device=s.device)
        observer_rows.append((observer @ products).reshape(-1, dimension))
        levels.append(
            SuffixLeakageLevel(
                length=length,
                products=int(products.shape[0] * products.shape[1]),
                behavioral_to_null=_max_spectral(null @ products @ s),
                null_to_behavioral=_max_spectral(s @ products @ null),
                behavioral_to_common=_max_spectral(line @ products @ s),
                common_to_behavioral=_max_spectral(s @ products @ line),
                behavioral_to_ambient=_max_spectral(fiber @ products @ s),
                ambient_to_behavioral=_max_spectral(s @ products @ fiber),
                common_to_ambient=_max_spectral(fiber @ products @ line),
                ambient_to_common=_max_spectral(line @ products @ fiber),
                common_line_action_residual=_max_spectral(
                    line @ (products - identity) @ line
                ),
            )
        )
    stacked = torch.cat(observer_rows, dim=0)
    singular = torch.linalg.svdvals(stacked)
    _require_finite("suffix observer singular values", singular)
    leading = float(singular[0]) if singular.numel() else 0.0
    if leading <= 0.0:
        raise AssayIntegrityError("suffix observer is identically zero")
    relative = singular / leading
    rank, rank_ambiguous = _matrix_rank(stacked, rank_tolerance)
    if expected_behavioral_rank < 1 or expected_behavioral_rank >= dimension:
        raise AssayIntegrityError("expected_behavioral_rank must lie in [1, hidden-1]")
    sigma_behavioral = float(relative[expected_behavioral_rank - 1])
    sigma_first_null = float(relative[expected_behavioral_rank])
    maximum_s_to_n = max(level.behavioral_to_null for level in levels)
    maximum_n_to_s = max(level.null_to_behavioral for level in levels)
    maximum_lk = max(
        max(level.common_to_ambient, level.ambient_to_common) for level in levels
    )
    maximum_line = max(level.common_line_action_residual for level in levels)
    scalar_values = [
        sigma_behavioral,
        sigma_first_null,
        maximum_s_to_n,
        maximum_n_to_s,
        maximum_lk,
        maximum_line,
    ]
    all_finite = all(math.isfinite(value) for value in scalar_values)
    passed = (
        all_finite
        and not rank_ambiguous
        and rank == expected_behavioral_rank
        and sigma_behavioral >= sigma_behavioral_floor
        and sigma_first_null <= sigma_first_null_ceiling
        and maximum_s_to_n <= tolerance
        and maximum_n_to_s <= tolerance
        and maximum_lk <= tolerance
        and maximum_line <= tolerance
    )
    return SuffixLeakageAudit(
        required_lengths=lengths,
        levels=tuple(levels),
        observer_singular_values=tuple(float(value) for value in singular),
        observer_rank=rank,
        sigma_behavioral_relative=sigma_behavioral,
        sigma_first_null_relative=sigma_first_null,
        sigma_behavioral_floor=sigma_behavioral_floor,
        sigma_first_null_ceiling=sigma_first_null_ceiling,
        maximum_behavioral_to_null=maximum_s_to_n,
        maximum_null_to_behavioral=maximum_n_to_s,
        maximum_common_ambient_mixing=maximum_lk,
        maximum_common_line_action_residual=maximum_line,
        tolerance=tolerance,
        all_finite=all_finite,
        passed=passed,
    )


def path_defect_from_products(
    behavioral_projector: torch.Tensor,
    common_projector: torch.Tensor,
    ambient_projector: torch.Tensor,
    left_products: torch.Tensor,
    right_products: torch.Tensor,
    *,
    tolerance: float = 5e-6,
    curvature_detection_floor: float = 1e-3,
) -> PathDefectAudit:
    """Separate behavioral, common-line, and ambient relation defects."""

    tolerance = _positive_finite("tolerance", tolerance)
    curvature_detection_floor = _positive_finite(
        "curvature_detection_floor", curvature_detection_floor
    )
    s, line, fiber = _prepare_three_way_split(
        behavioral_projector, common_projector, ambient_projector
    )
    dimension = int(s.shape[0])
    left = _square_matrix_batch("left_products", left_products, dimension, s.device)
    right = _square_matrix_batch("right_products", right_products, dimension, s.device)
    if left.shape != right.shape:
        raise AssayIntegrityError("left_products and right_products must have identical shapes")
    delta = left - right
    null = line + fiber
    quotient = _spectral_values(s @ delta @ s)
    common = _spectral_values(line @ delta @ line)
    vertical = _spectral_values(fiber @ delta @ fiber)
    s_to_n = _spectral_values(null @ delta @ s)
    n_to_s = _spectral_values(s @ delta @ null)
    full = _spectral_values(delta)
    arrays = (quotient, common, vertical, s_to_n, n_to_s, full)
    if any(value.numel() < 1 for value in arrays):
        raise AssayIntegrityError("path defect bank cannot be empty")
    maxima = tuple(float(value.max()) for value in arrays)
    all_finite = all(math.isfinite(value) for value in maxima)
    quotient_flat = all_finite and maxima[0] <= tolerance and maxima[3] <= tolerance and maxima[4] <= tolerance
    common_flat = all_finite and maxima[1] <= tolerance
    vertical_flat = all_finite and maxima[2] <= tolerance
    full_flat = all_finite and maxima[5] <= tolerance
    vertical_curvature_only = (
        quotient_flat
        and common_flat
        and maxima[2] >= curvature_detection_floor
        and not full_flat
    )
    return PathDefectAudit(
        cases=int(quotient.numel()),
        quotient_defects=tuple(float(value) for value in quotient),
        common_defects=tuple(float(value) for value in common),
        vertical_defects=tuple(float(value) for value in vertical),
        behavioral_to_null_defects=tuple(float(value) for value in s_to_n),
        null_to_behavioral_defects=tuple(float(value) for value in n_to_s),
        full_defects=tuple(float(value) for value in full),
        maximum_quotient_defect=maxima[0],
        maximum_common_defect=maxima[1],
        maximum_vertical_defect=maxima[2],
        maximum_behavioral_to_null_defect=maxima[3],
        maximum_null_to_behavioral_defect=maxima[4],
        maximum_full_defect=maxima[5],
        quotient_flat=quotient_flat,
        common_flat=common_flat,
        vertical_flat=vertical_flat,
        full_flat=full_flat,
        vertical_curvature_only=vertical_curvature_only,
        tolerance=tolerance,
        curvature_detection_floor=curvature_detection_floor,
        all_finite=all_finite,
    )


def path_defect_audit(
    behavioral_projector: torch.Tensor,
    common_projector: torch.Tensor,
    ambient_projector: torch.Tensor,
    operator_codes: torch.Tensor,
    left_words: torch.Tensor,
    right_words: torch.Tensor,
    *,
    tolerance: float = 5e-6,
    curvature_detection_floor: float = 1e-3,
) -> PathDefectAudit:
    """Execute matched paths and call :func:`path_defect_from_products`."""

    codes = _floating_tensor("operator_codes", operator_codes, minimum_ndim=3)
    left = path_products(codes, left_words)
    right = path_products(codes, right_words)
    return path_defect_from_products(
        behavioral_projector,
        common_projector,
        ambient_projector,
        left,
        right,
        tolerance=tolerance,
        curvature_detection_floor=curvature_detection_floor,
    )


def fiber_intervention_audit(
    behavioral_projector: torch.Tensor,
    common_projector: torch.Tensor,
    ambient_projector: torch.Tensor,
    decoder_weight: torch.Tensor,
    operator_codes: torch.Tensor,
    suffix_words: Mapping[int, torch.Tensor],
    *,
    required_lengths: Sequence[int] = DEFAULT_SUFFIX_LENGTHS,
    tolerance: float = 5e-6,
    rank_tolerance: float = 5e-6,
) -> FiberInterventionAudit:
    """Inject and transplant explicit non-zero vectors in ``L`` and ``K``.

    For each suffix product ``W`` the exact normalized effects are measured as
    ``||C D W K||_2`` and ``||C D W L||_2``.  We additionally instantiate
    orthonormal probes ``q`` and the transplant pair ``q -> -q``; the latter
    has distance two and is normalized back to a per-unit effect.
    """

    tolerance = _positive_finite("tolerance", tolerance)
    rank_tolerance = _positive_finite("rank_tolerance", rank_tolerance)
    lengths = _validate_suffix_mapping(suffix_words, required_lengths)
    s, line, fiber = _prepare_three_way_split(
        behavioral_projector, common_projector, ambient_projector
    )
    dimension = int(s.shape[0])
    del s  # The intervention is entirely inside the centered decoder kernel.
    decoder = _floating_tensor("decoder_weight", decoder_weight, minimum_ndim=2).to(
        device=line.device, dtype=torch.float64
    )
    if decoder.ndim != 2 or decoder.shape[1] != dimension:
        raise AssayIntegrityError("decoder_weight has incompatible dimensions")
    observer = centered_decoder(decoder).to(device=line.device)
    codes = _square_matrix_batch("operator_codes", operator_codes, dimension, line.device)
    line_frame = _projector_frame(line, 1, rank_tolerance, "common projector")
    fiber_frame = _projector_frame(fiber, 4, rank_tolerance, "ambient projector")
    line_norms = torch.linalg.vector_norm(line_frame, dim=0)
    fiber_norms = torch.linalg.vector_norm(fiber_frame, dim=0)
    levels: list[FiberInterventionLevel] = []
    for length in lengths:
        products = path_products(codes, suffix_words[length]).to(device=line.device)
        ambient_response = observer @ products @ fiber_frame
        common_response = observer @ products @ line_frame
        # q -> -q changes a fiber by -2q.  Dividing the measured response by
        # the exact distance two yields the same per-unit operator effect, but
        # demonstrates that the assay did not rely on a zero-vector patch.
        ambient_transplant = (-2.0 * ambient_response).abs() / 2.0
        common_transplant = (-2.0 * common_response).abs() / 2.0
        levels.append(
            FiberInterventionLevel(
                length=length,
                products=int(products.shape[0] * products.shape[1]),
                ambient_injection_effect=_max_spectral(ambient_response),
                ambient_transplant_effect_per_unit=float(ambient_transplant.max()),
                common_injection_effect=_max_spectral(common_response),
                common_transplant_effect_per_unit=float(common_transplant.max()),
            )
        )
    maxima = (
        max(level.ambient_injection_effect for level in levels),
        max(level.ambient_transplant_effect_per_unit for level in levels),
        max(level.common_injection_effect for level in levels),
        max(level.common_transplant_effect_per_unit for level in levels),
    )
    minimum_fiber_norm = float(fiber_norms.min())
    minimum_line_norm = float(line_norms.min())
    values = (*maxima, minimum_fiber_norm, minimum_line_norm)
    all_finite = all(math.isfinite(value) for value in values)
    passed = (
        all_finite
        and minimum_fiber_norm > 0.0
        and minimum_line_norm > 0.0
        and all(value <= tolerance for value in maxima)
    )
    return FiberInterventionAudit(
        required_lengths=lengths,
        levels=tuple(levels),
        ambient_probe_dimension=int(fiber_frame.shape[1]),
        common_probe_dimension=int(line_frame.shape[1]),
        minimum_ambient_probe_norm=minimum_fiber_norm,
        minimum_common_probe_norm=minimum_line_norm,
        minimum_ambient_transplant_distance=2.0 * minimum_fiber_norm,
        minimum_common_transplant_distance=2.0 * minimum_line_norm,
        maximum_ambient_injection_effect=maxima[0],
        maximum_ambient_transplant_effect_per_unit=maxima[1],
        maximum_common_injection_effect=maxima[2],
        maximum_common_transplant_effect_per_unit=maxima[3],
        tolerance=tolerance,
        all_finite=all_finite,
        passed=passed,
    )


def semantic_transplant_audit(
    behavioral_projector: torch.Tensor,
    common_projector: torch.Tensor,
    ambient_projector: torch.Tensor,
    decoder_weight: torch.Tensor,
    continuation_products: torch.Tensor,
    recipient_states: torch.Tensor,
    donor_states: torch.Tensor,
    recipient_exact_targets: torch.Tensor,
    donor_exact_targets: torch.Tensor,
    *,
    targets_are_exact: bool,
    margin_tau: float = 2.0**-18,
    semantic_displacement_floor: float = 1e-8,
) -> SemanticTransplantAudit:
    """Patch donor ``S`` state into a recipient with exact eligibility.

    A pair is eligible iff both native continuations robustly match their exact
    targets, the exact targets differ, and the donor/recipient behavioral
    components are genuinely distinct.  There is no post-hoc hand mask.
    """

    if targets_are_exact is not True:
        raise AssayIntegrityError("semantic transplant requires exact ground-truth targets")
    margin_tau = _nonnegative_finite("margin_tau", margin_tau)
    semantic_displacement_floor = _positive_finite(
        "semantic_displacement_floor", semantic_displacement_floor
    )
    s, line, fiber = _prepare_three_way_split(
        behavioral_projector, common_projector, ambient_projector
    )
    dimension = int(s.shape[0])
    null = line + fiber
    decoder = _floating_tensor("decoder_weight", decoder_weight, minimum_ndim=2).to(
        device=s.device, dtype=torch.float64
    )
    if decoder.ndim != 2 or decoder.shape[1] != dimension:
        raise AssayIntegrityError("decoder_weight has incompatible dimensions")
    products = _square_matrix_batch(
        "continuation_products", continuation_products, dimension, s.device
    )
    products = products.reshape(-1, dimension, dimension)
    recipients = _state_rows("recipient_states", recipient_states, dimension, s.device)
    donors = _state_rows("donor_states", donor_states, dimension, s.device)
    if recipients.shape != donors.shape or recipients.shape[0] != products.shape[0]:
        raise AssayIntegrityError("state rows and continuation products must align exactly")
    classes = int(decoder.shape[0])
    recipient_targets = _target_vector(
        "recipient_exact_targets", recipient_exact_targets, recipients.shape[0], classes, s.device
    )
    donor_targets = _target_vector(
        "donor_exact_targets", donor_exact_targets, recipients.shape[0], classes, s.device
    )

    def continue_logits(states: torch.Tensor) -> torch.Tensor:
        final = torch.bmm(products, states.unsqueeze(-1)).squeeze(-1)
        logits = final @ decoder.T
        _require_finite("semantic transplant logits", logits)
        return logits

    recipient_logits = continue_logits(recipients)
    donor_logits = continue_logits(donors)
    patched_states = (donors @ s.T) + (recipients @ null.T)
    patched_logits = continue_logits(patched_states)
    recipient_ok, _ = _robust_target(recipient_logits, recipient_targets, margin_tau)
    donor_ok, _ = _robust_target(donor_logits, donor_targets, margin_tau)
    patched_ok, patched_margins = _robust_target(patched_logits, donor_targets, margin_tau)
    distinct = recipient_targets != donor_targets
    displacement = torch.linalg.vector_norm((donors - recipients) @ s.T, dim=1)
    nontrivial = displacement > semantic_displacement_floor
    eligible = recipient_ok & donor_ok & distinct & nontrivial
    eligible_count = int(eligible.sum())
    if eligible_count < 1:
        raise AssayIntegrityError("semantic transplant bank has no exactly eligible pair")
    successful = eligible & patched_ok
    success_count = int(successful.sum())
    success_margins = patched_margins[successful]
    minimum_success_margin = (
        float(success_margins.min()) if success_margins.numel() else None
    )
    return SemanticTransplantAudit(
        total_pairs=int(recipients.shape[0]),
        eligible_pairs=eligible_count,
        successful_pairs=success_count,
        eligibility_fraction=eligible_count / int(recipients.shape[0]),
        success_rate=success_count / eligible_count,
        recipient_native_robust=int(recipient_ok.sum()),
        donor_native_robust=int(donor_ok.sum()),
        distinct_exact_targets=int(distinct.sum()),
        nontrivial_semantic_displacements=int(nontrivial.sum()),
        minimum_eligible_semantic_displacement=float(displacement[eligible].min()),
        minimum_success_margin=minimum_success_margin,
        margin_tau=margin_tau,
        exact_eligibility_enforced=True,
        all_finite=True,
    )


def gauge_covariance_audit(
    behavioral_projector: torch.Tensor,
    common_projector: torch.Tensor,
    ambient_projector: torch.Tensor,
    decoder_weight: torch.Tensor,
    operator_codes: torch.Tensor,
    suffix_words: Mapping[int, torch.Tensor],
    left_words: torch.Tensor,
    right_words: torch.Tensor,
    gauge: torch.Tensor,
    *,
    required_lengths: Sequence[int] = DEFAULT_SUFFIX_LENGTHS,
    tolerance: float = 2e-10,
) -> GaugeCovarianceAudit:
    """Verify covariance under a simultaneous orthogonal coordinate change."""

    tolerance = _positive_finite("tolerance", tolerance)
    s, line, fiber = _prepare_three_way_split(
        behavioral_projector, common_projector, ambient_projector
    )
    dimension = int(s.shape[0])
    codes = _square_matrix_batch("operator_codes", operator_codes, dimension, s.device)
    decoder = _floating_tensor("decoder_weight", decoder_weight, minimum_ndim=2).to(
        device=s.device, dtype=torch.float64
    )
    if decoder.ndim != 2 or decoder.shape[1] != dimension:
        raise AssayIntegrityError("decoder_weight has incompatible dimensions")
    transform = _floating_tensor("gauge", gauge, minimum_ndim=2).to(
        device=s.device, dtype=torch.float64
    )
    if transform.shape != (dimension, dimension):
        raise AssayIntegrityError("gauge must have shape (hidden,hidden)")
    identity = torch.eye(dimension, dtype=torch.float64, device=s.device)
    gauge_residual = _spectral(transform.T @ transform - identity)
    if gauge_residual > 1e-6:
        raise AssayIntegrityError("gauge is not an orthogonal coordinate transformation")

    transformed_s = transform @ s @ transform.T
    transformed_l = transform @ line @ transform.T
    transformed_k = transform @ fiber @ transform.T
    transformed_decoder = decoder @ transform.T
    transformed_codes = transform @ codes @ transform.T

    original_structure = audit_kernel_structure(s, line, fiber, decoder, codes)
    transformed_structure = audit_kernel_structure(
        transformed_s,
        transformed_l,
        transformed_k,
        transformed_decoder,
        transformed_codes,
    )
    structure_names = (
        "centered_decoder_null_residual",
        "ambient_raw_decoder_residual",
        "behavioral_decoder_completeness_residual",
        "operator_orthogonality_residual",
        "behavioral_to_null_leakage",
        "null_to_behavioral_leakage",
        "common_to_ambient_leakage",
        "ambient_to_common_leakage",
        "common_line_action_residual",
    )
    structure_delta = max(
        abs(getattr(original_structure, name) - getattr(transformed_structure, name))
        for name in structure_names
    )
    original_suffix = suffix_leakage_audit(
        s, line, fiber, decoder, codes, suffix_words, required_lengths=required_lengths
    )
    transformed_suffix = suffix_leakage_audit(
        transformed_s,
        transformed_l,
        transformed_k,
        transformed_decoder,
        transformed_codes,
        suffix_words,
        required_lengths=required_lengths,
    )
    suffix_names = (
        "sigma_behavioral_relative",
        "sigma_first_null_relative",
        "maximum_behavioral_to_null",
        "maximum_null_to_behavioral",
        "maximum_common_ambient_mixing",
        "maximum_common_line_action_residual",
    )
    suffix_delta = max(
        abs(getattr(original_suffix, name) - getattr(transformed_suffix, name))
        for name in suffix_names
    )
    original_path = path_defect_audit(s, line, fiber, codes, left_words, right_words)
    transformed_path = path_defect_audit(
        transformed_s,
        transformed_l,
        transformed_k,
        transformed_codes,
        left_words,
        right_words,
    )

    observer = centered_decoder(decoder).to(device=s.device)
    transformed_observer = centered_decoder(transformed_decoder).to(device=s.device)
    continuation_delta = 0.0
    lengths = _validate_suffix_mapping(suffix_words, required_lengths)
    for length in lengths:
        products = path_products(codes, suffix_words[length]).to(device=s.device)
        products_g = path_products(transformed_codes, suffix_words[length]).to(device=s.device)
        # A transformed hidden vector is G h; therefore the transformed
        # continuation map is compared after composing its input with G.
        delta = transformed_observer @ products_g @ transform - observer @ products
        continuation_delta = max(continuation_delta, _max_spectral(delta))

    values = (
        gauge_residual,
        structure_delta,
        suffix_delta,
        abs(original_path.maximum_quotient_defect - transformed_path.maximum_quotient_defect),
        abs(original_path.maximum_common_defect - transformed_path.maximum_common_defect),
        abs(original_path.maximum_vertical_defect - transformed_path.maximum_vertical_defect),
        continuation_delta,
    )
    all_finite = all(math.isfinite(value) for value in values)
    rank_preserved = (
        original_structure.behavioral_rank == transformed_structure.behavioral_rank
        and original_structure.common_rank == transformed_structure.common_rank
        and original_structure.ambient_rank == transformed_structure.ambient_rank
        and original_suffix.observer_rank == transformed_suffix.observer_rank
    )
    passed = all_finite and rank_preserved and all(value <= tolerance for value in values)
    return GaugeCovarianceAudit(
        gauge_orthogonality_residual=gauge_residual,
        structure_scalar_delta=structure_delta,
        suffix_scalar_delta=suffix_delta,
        quotient_path_delta=values[3],
        common_path_delta=values[4],
        vertical_path_delta=values[5],
        centered_continuation_operator_delta=continuation_delta,
        rank_preserved=rank_preserved,
        tolerance=tolerance,
        all_finite=all_finite,
        passed=passed,
    )


def extract_model_geometry(
    model: Any,
    tables: torch.Tensor,
    suffix_words: Mapping[int, torch.Tensor],
    *,
    required_lengths: Sequence[int] = DEFAULT_SUFFIX_LENGTHS,
    expected_behavioral_rank: int = 7,
    rank_tolerance: float = 5e-6,
    sigma_behavioral_floor: float = 1e-4,
    sigma_first_null_ceiling: float = 5e-6,
) -> ExtractedKernelGeometry:
    """Extract registered or observational geometry without inventing fibers.

    Resolution order is scientific, not cosmetic:

    1. A hard model with explicit ``behavioral/common/ambient`` projectors uses
       that registered three-way geometry.
    2. A learned-intertwiner model uses its registered rank-seven observer but
       exposes only the resulting two-way split.
    3. A plain linear-polar model uses the prospectively fixed suffix-observer
       SVD.  Its top-seven projector is returned for diagnostics even when the
       required sigma gap fails; ``extraction_valid`` then remains false.

    The latter behavior lets a runner record a failed baseline without either
    crashing the whole study or silently certifying an arbitrary truncation.
    """

    rank_tolerance = _positive_finite("rank_tolerance", rank_tolerance)
    sigma_behavioral_floor = _positive_finite(
        "sigma_behavioral_floor", sigma_behavioral_floor
    )
    sigma_first_null_ceiling = _positive_finite(
        "sigma_first_null_ceiling", sigma_first_null_ceiling
    )
    lengths = _validate_suffix_mapping(suffix_words, required_lengths)
    table_tensor = _floating_tensor("tables", tables, minimum_ndim=4)
    if table_tensor.ndim != 4 or table_tensor.shape[0] < 1 or table_tensor.shape[1] < 1:
        raise AssayIntegrityError("tables must have shape (contexts,operators,states,states)")
    if not hasattr(model, "encode_operators") or not callable(model.encode_operators):
        raise AssayIntegrityError("model does not expose encode_operators")
    with torch.inference_mode():
        codes_native = model.encode_operators(table_tensor)
    codes = _floating_tensor("model operator codes", codes_native, minimum_ndim=4).to(
        torch.float64
    )
    if codes.ndim != 4 or codes.shape[0] != table_tensor.shape[0]:
        raise AssayIntegrityError("model operator codes have an invalid context axis")
    dimension = int(codes.shape[-1])
    if codes.shape[-2] != dimension:
        raise AssayIntegrityError("model operator codes must be square matrices")
    if hasattr(model, "effective_decoder_weight") and callable(
        model.effective_decoder_weight
    ):
        decoder_native = model.effective_decoder_weight()
    elif hasattr(model, "decoder") and hasattr(model.decoder, "weight"):
        decoder_native = model.decoder.weight
    else:
        raise AssayIntegrityError("model does not expose a linear decoder weight")
    decoder = _floating_tensor("model decoder weight", decoder_native, minimum_ndim=2).to(
        device=codes.device, dtype=torch.float64
    )
    if decoder.ndim != 2 or decoder.shape[1] != dimension:
        raise AssayIntegrityError("model decoder is incompatible with operator codes")

    observer_rows: list[torch.Tensor] = []
    for length in lengths:
        products = path_products(codes, suffix_words[length]).to(device=codes.device)
        observer_rows.append(
            (centered_decoder(decoder).to(device=codes.device) @ products).reshape(
                -1, dimension
            )
        )
    observer_stack = torch.cat(observer_rows, dim=0)
    _, singular, right_vectors = torch.linalg.svd(observer_stack, full_matrices=False)
    _require_finite("model suffix observer SVD", singular)
    if singular.numel() < dimension or float(singular[0]) <= 0.0:
        raise AssayIntegrityError("model suffix observer does not determine hidden geometry")
    relative = singular / singular[0]
    if expected_behavioral_rank < 1 or expected_behavioral_rank >= dimension:
        raise AssayIntegrityError("expected_behavioral_rank is incompatible with hidden dimension")
    sigma_behavioral = float(relative[expected_behavioral_rank - 1])
    sigma_first_null = float(relative[expected_behavioral_rank])
    observer_rank, observer_ambiguous = _matrix_rank(observer_stack, rank_tolerance)

    hard_methods = (
        "behavioral_projector",
        "common_logit_projector",
        "ambient_projector",
        "centered_null_projector",
    )
    if all(hasattr(model, name) and callable(getattr(model, name)) for name in hard_methods):
        behavioral = _floating_tensor(
            "registered behavioral projector", model.behavioral_projector(), minimum_ndim=2
        ).to(device=codes.device, dtype=torch.float64)
        common = _floating_tensor(
            "registered common projector", model.common_logit_projector(), minimum_ndim=2
        ).to(device=codes.device, dtype=torch.float64)
        ambient = _floating_tensor(
            "registered ambient projector", model.ambient_projector(), minimum_ndim=2
        ).to(device=codes.device, dtype=torch.float64)
        centered_null = _floating_tensor(
            "registered centered-null projector",
            model.centered_null_projector(),
            minimum_ndim=2,
        ).to(device=codes.device, dtype=torch.float64)
        source = "registered_three_way_7_plus_1_plus_4"
        three_way = True
    elif hasattr(model, "observer_projector") and callable(model.observer_projector):
        behavioral = _floating_tensor(
            "learned observer projector", model.observer_projector(), minimum_ndim=2
        ).to(device=codes.device, dtype=torch.float64)
        identity = torch.eye(dimension, dtype=torch.float64, device=codes.device)
        centered_null = identity - behavioral
        common = None
        ambient = None
        source = "registered_learned_rank7_observer"
        three_way = False
    else:
        frame = right_vectors[:expected_behavioral_rank].T
        behavioral = frame @ frame.T
        identity = torch.eye(dimension, dtype=torch.float64, device=codes.device)
        centered_null = identity - behavioral
        common = None
        ambient = None
        source = "preregistered_suffix_observer_top7_svd"
        three_way = False

    if behavioral.shape != (dimension, dimension) or centered_null.shape != (
        dimension,
        dimension,
    ):
        raise AssayIntegrityError("extracted projectors have incompatible dimensions")
    projector_rank, projector_ambiguous = _projector_rank(behavioral, rank_tolerance)
    null_rank, null_ambiguous = _projector_rank(centered_null, rank_tolerance)
    expected_null_rank = dimension - expected_behavioral_rank
    extraction_valid = (
        projector_rank == expected_behavioral_rank
        and null_rank == expected_null_rank
        and not projector_ambiguous
        and not null_ambiguous
        and not observer_ambiguous
        and observer_rank == expected_behavioral_rank
        and sigma_behavioral >= sigma_behavioral_floor
        and sigma_first_null <= sigma_first_null_ceiling
    )
    failure_parts: list[str] = []
    if projector_rank != expected_behavioral_rank or null_rank != expected_null_rank:
        failure_parts.append("projector_rank")
    if projector_ambiguous or null_ambiguous or observer_ambiguous:
        failure_parts.append("rank_ambiguous")
    if observer_rank != expected_behavioral_rank:
        failure_parts.append("observer_rank")
    if sigma_behavioral < sigma_behavioral_floor:
        failure_parts.append("sigma7_too_weak")
    if sigma_first_null > sigma_first_null_ceiling:
        failure_parts.append("sigma8_not_negligible")
    return ExtractedKernelGeometry(
        behavioral_projector=behavioral,
        centered_null_projector=centered_null,
        common_projector=common,
        ambient_projector=ambient,
        decoder_weight=decoder,
        operator_codes=codes,
        source=source,
        three_way_registered=three_way,
        observer_singular_values=tuple(float(value) for value in singular),
        observer_rank=observer_rank,
        sigma_behavioral_relative=sigma_behavioral,
        sigma_first_null_relative=sigma_first_null,
        extraction_valid=extraction_valid,
        failure_reason=None if extraction_valid else "+".join(failure_parts),
    )


def audit_centered_quotient_structure(
    behavioral_projector: torch.Tensor,
    centered_null_projector: torch.Tensor,
    decoder_weight: torch.Tensor,
    operator_codes: torch.Tensor,
    *,
    expected_behavioral_rank: int = 7,
    expected_null_rank: int = 5,
    tolerance: float = 5e-6,
    rank_tolerance: float = 5e-6,
) -> TwoWayStructureAudit:
    """Audit only the scientifically identified behavioral/null split."""

    tolerance = _positive_finite("tolerance", tolerance)
    rank_tolerance = _positive_finite("rank_tolerance", rank_tolerance)
    s, null = _prepare_two_way_split(behavioral_projector, centered_null_projector)
    dimension = int(s.shape[0])
    if expected_behavioral_rank + expected_null_rank != dimension:
        raise AssayIntegrityError("expected two-way ranks must sum to hidden dimension")
    decoder = _floating_tensor("decoder_weight", decoder_weight, minimum_ndim=2).to(
        device=s.device, dtype=torch.float64
    )
    if decoder.ndim != 2 or decoder.shape[1] != dimension:
        raise AssayIntegrityError("decoder_weight has incompatible dimensions")
    observer = centered_decoder(decoder).to(device=s.device)
    codes = _square_matrix_batch("operator_codes", operator_codes, dimension, s.device)
    identity = torch.eye(dimension, dtype=torch.float64, device=s.device)
    rank_s, ambiguity_s = _projector_rank(s, rank_tolerance)
    rank_n, ambiguity_n = _projector_rank(null, rank_tolerance)
    rank_d, ambiguity_d = _matrix_rank(observer, rank_tolerance)
    values = (
        _spectral(s @ s - s),
        _spectral(null @ null - null),
        _spectral(s + null - identity),
        max(_spectral(s @ null), _spectral(null @ s)),
        _spectral(observer @ null),
        _spectral(observer - observer @ s),
        _max_spectral(codes.transpose(-1, -2) @ codes - identity),
        _max_spectral(null @ codes @ s),
        _max_spectral(s @ codes @ null),
    )
    all_finite = all(math.isfinite(value) for value in values)
    rank_ambiguous = ambiguity_s or ambiguity_n or ambiguity_d
    passed = (
        all_finite
        and not rank_ambiguous
        and rank_s == expected_behavioral_rank
        and rank_n == expected_null_rank
        and rank_d == expected_behavioral_rank
        and all(value <= tolerance for value in values)
    )
    return TwoWayStructureAudit(
        hidden_dimension=dimension,
        behavioral_rank=rank_s,
        centered_null_rank=rank_n,
        centered_decoder_rank=rank_d,
        rank_ambiguous=rank_ambiguous,
        behavioral_idempotence_residual=values[0],
        centered_null_idempotence_residual=values[1],
        partition_residual=values[2],
        projector_orthogonality_residual=values[3],
        centered_decoder_null_residual=values[4],
        behavioral_decoder_completeness_residual=values[5],
        operator_orthogonality_residual=values[6],
        behavioral_to_null_leakage=values[7],
        null_to_behavioral_leakage=values[8],
        tolerance=tolerance,
        all_finite=all_finite,
        passed=passed,
    )


def audit_centered_quotient_suffixes(
    behavioral_projector: torch.Tensor,
    centered_null_projector: torch.Tensor,
    decoder_weight: torch.Tensor,
    operator_codes: torch.Tensor,
    suffix_words: Mapping[int, torch.Tensor],
    *,
    required_lengths: Sequence[int] = DEFAULT_SUFFIX_LENGTHS,
    expected_behavioral_rank: int = 7,
    tolerance: float = 5e-6,
    rank_tolerance: float = 5e-6,
    sigma_behavioral_floor: float = 1e-4,
    sigma_first_null_ceiling: float = 5e-6,
) -> TwoWaySuffixAudit:
    """Two-way suffix leakage and sigma7/sigma8 observability gate."""

    tolerance = _positive_finite("tolerance", tolerance)
    lengths = _validate_suffix_mapping(suffix_words, required_lengths)
    s, null = _prepare_two_way_split(behavioral_projector, centered_null_projector)
    dimension = int(s.shape[0])
    decoder = _floating_tensor("decoder_weight", decoder_weight, minimum_ndim=2).to(
        device=s.device, dtype=torch.float64
    )
    if decoder.ndim != 2 or decoder.shape[1] != dimension:
        raise AssayIntegrityError("decoder_weight has incompatible dimensions")
    observer = centered_decoder(decoder).to(device=s.device)
    codes = _square_matrix_batch("operator_codes", operator_codes, dimension, s.device)
    rows: list[torch.Tensor] = []
    by_length: list[tuple[int, float, float]] = []
    for length in lengths:
        products = path_products(codes, suffix_words[length]).to(device=s.device)
        rows.append((observer @ products).reshape(-1, dimension))
        by_length.append(
            (
                length,
                _max_spectral(null @ products @ s),
                _max_spectral(s @ products @ null),
            )
        )
    stacked = torch.cat(rows, dim=0)
    singular = torch.linalg.svdvals(stacked)
    _require_finite("two-way suffix observer singular values", singular)
    if float(singular[0]) <= 0.0:
        raise AssayIntegrityError("two-way suffix observer is identically zero")
    relative = singular / singular[0]
    rank, ambiguous = _matrix_rank(stacked, rank_tolerance)
    sigma_s = float(relative[expected_behavioral_rank - 1])
    sigma_n = float(relative[expected_behavioral_rank])
    maximum_forward = max(row[1] for row in by_length)
    maximum_reverse = max(row[2] for row in by_length)
    passed = (
        not ambiguous
        and rank == expected_behavioral_rank
        and sigma_s >= sigma_behavioral_floor
        and sigma_n <= sigma_first_null_ceiling
        and maximum_forward <= tolerance
        and maximum_reverse <= tolerance
    )
    return TwoWaySuffixAudit(
        required_lengths=lengths,
        observer_singular_values=tuple(float(value) for value in singular),
        observer_rank=rank,
        sigma_behavioral_relative=sigma_s,
        sigma_first_null_relative=sigma_n,
        maximum_behavioral_to_null=maximum_forward,
        maximum_null_to_behavioral=maximum_reverse,
        by_length=tuple(by_length),
        tolerance=tolerance,
        passed=passed,
    )


def audit_centered_quotient_paths(
    behavioral_projector: torch.Tensor,
    centered_null_projector: torch.Tensor,
    operator_codes: torch.Tensor,
    left_words: torch.Tensor,
    right_words: torch.Tensor,
    *,
    tolerance: float = 5e-6,
) -> TwoWayPathAudit:
    """Compare relation paths without assigning a type to the null block."""

    tolerance = _positive_finite("tolerance", tolerance)
    s, null = _prepare_two_way_split(behavioral_projector, centered_null_projector)
    codes = _square_matrix_batch("operator_codes", operator_codes, s.shape[0], s.device)
    left = path_products(codes, left_words).to(device=s.device)
    right = path_products(codes, right_words).to(device=s.device)
    if left.shape != right.shape:
        raise AssayIntegrityError("left and right word banks do not align")
    delta = left - right
    values = (
        _max_spectral(s @ delta @ s),
        _max_spectral(null @ delta @ null),
        _max_spectral(null @ delta @ s),
        _max_spectral(s @ delta @ null),
        _max_spectral(delta),
    )
    all_finite = all(math.isfinite(value) for value in values)
    quotient_flat = all_finite and values[0] <= tolerance and values[2] <= tolerance and values[3] <= tolerance
    return TwoWayPathAudit(
        cases=int(delta.numel() // (s.shape[0] * s.shape[0])),
        maximum_quotient_defect=values[0],
        maximum_null_defect=values[1],
        maximum_behavioral_to_null_defect=values[2],
        maximum_null_to_behavioral_defect=values[3],
        maximum_full_defect=values[4],
        quotient_flat=quotient_flat,
        null_flat=all_finite and values[1] <= tolerance,
        full_flat=all_finite and values[4] <= tolerance,
        tolerance=tolerance,
        all_finite=all_finite,
    )


def centered_null_intervention_audit(
    behavioral_projector: torch.Tensor,
    centered_null_projector: torch.Tensor,
    decoder_weight: torch.Tensor,
    operator_codes: torch.Tensor,
    suffix_words: Mapping[int, torch.Tensor],
    *,
    required_lengths: Sequence[int] = DEFAULT_SUFFIX_LENGTHS,
    expected_null_rank: int = 5,
    tolerance: float = 5e-6,
    rank_tolerance: float = 5e-6,
) -> NullInterventionAudit:
    """Non-zero injection/transplant assay for an untyped centered null."""

    tolerance = _positive_finite("tolerance", tolerance)
    lengths = _validate_suffix_mapping(suffix_words, required_lengths)
    s, null = _prepare_two_way_split(behavioral_projector, centered_null_projector)
    dimension = int(s.shape[0])
    del s
    decoder = _floating_tensor("decoder_weight", decoder_weight, minimum_ndim=2).to(
        device=null.device, dtype=torch.float64
    )
    if decoder.ndim != 2 or decoder.shape[1] != dimension:
        raise AssayIntegrityError("decoder_weight has incompatible dimensions")
    observer = centered_decoder(decoder).to(device=null.device)
    codes = _square_matrix_batch("operator_codes", operator_codes, dimension, null.device)
    frame = _projector_frame(
        null, expected_null_rank, rank_tolerance, "centered-null projector"
    )
    norms = torch.linalg.vector_norm(frame, dim=0)
    by_length: list[tuple[int, float, float]] = []
    for length in lengths:
        products = path_products(codes, suffix_words[length]).to(device=null.device)
        response = observer @ products @ frame
        by_length.append(
            (
                length,
                _max_spectral(response),
                float(((-2.0 * response).abs() / 2.0).max()),
            )
        )
    max_injection = max(row[1] for row in by_length)
    max_transplant = max(row[2] for row in by_length)
    minimum_norm = float(norms.min())
    return NullInterventionAudit(
        null_dimension=int(frame.shape[1]),
        required_lengths=lengths,
        minimum_probe_norm=minimum_norm,
        minimum_transplant_distance=2.0 * minimum_norm,
        maximum_injection_effect=max_injection,
        maximum_transplant_effect_per_unit=max_transplant,
        by_length=tuple(by_length),
        tolerance=tolerance,
        passed=(
            math.isfinite(max_injection)
            and math.isfinite(max_transplant)
            and minimum_norm > 0.0
            and max_injection <= tolerance
            and max_transplant <= tolerance
        ),
    )


def _helmert_contrasts() -> torch.Tensor:
    """Deterministic eight-state Helmert chart used only by assay controls."""

    basis = torch.zeros(8, 7, dtype=torch.float64)
    for column in range(7):
        count = column + 1
        scale = math.sqrt(float(count * (count + 1)))
        basis[:count, column] = 1.0 / scale
        basis[count, column] = -float(count) / scale
    return basis


def _orthogonal_control_matrix(dimension: int, seed: int) -> torch.Tensor:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    raw = torch.randn(dimension, dimension, generator=generator, dtype=torch.float64)
    orthogonal, triangular = torch.linalg.qr(raw)
    signs = torch.sign(torch.diagonal(triangular))
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    return orthogonal @ torch.diag(signs)


def _assemble_control_codes(
    behavioral_blocks: torch.Tensor,
    ambient_blocks: torch.Tensor,
) -> torch.Tensor:
    if behavioral_blocks.shape != (2, 7, 7) or ambient_blocks.shape != (2, 4, 4):
        raise AssayIntegrityError("control blocks must have shapes (2,7,7) and (2,4,4)")
    codes = torch.zeros(2, 12, 12, dtype=torch.float64)
    codes[:, :7, :7] = behavioral_blocks
    codes[:, 7, 7] = 1.0
    codes[:, 8:, 8:] = ambient_blocks
    return codes


def _semantic_control_fixture() -> dict[str, torch.Tensor]:
    """Exact anonymous dihedral action in the registered 7+1+4 chart."""

    basis = _helmert_contrasts()
    maps = torch.stack(
        (
            (torch.arange(8, dtype=torch.long) + 1) % 8,
            (-torch.arange(8, dtype=torch.long)) % 8,
        )
    )
    permutations = torch.zeros(2, 8, 8, dtype=torch.float64)
    sources = torch.arange(8)
    for operator in range(2):
        permutations[operator, maps[operator], sources] = 1.0
    behavioral = basis.T @ permutations @ basis
    ambient = torch.eye(4, dtype=torch.float64).expand(2, -1, -1).clone()
    codes = _assemble_control_codes(behavioral, ambient)
    decoder = torch.zeros(8, 12, dtype=torch.float64)
    decoder[:, :7] = basis
    decoder[:, 7] = 1.0
    anchors = torch.zeros(8, 12, dtype=torch.float64)
    anchors[:, :7] = basis
    anchors[:, 7] = 1.0 / math.sqrt(8.0)
    identity = torch.eye(12, dtype=torch.float64)
    s = torch.diag(torch.tensor([1.0] * 7 + [0.0] * 5, dtype=torch.float64))
    line = torch.diag(
        torch.tensor([0.0] * 7 + [1.0] + [0.0] * 4, dtype=torch.float64)
    )
    return {
        "basis": basis,
        "maps": maps,
        "codes": codes,
        "decoder": decoder,
        "anchors": anchors,
        "identity": identity,
        "behavioral_projector": s,
        "common_projector": line,
        "ambient_projector": identity - s - line,
    }


def _control_words() -> tuple[tuple[int, ...], ...]:
    words: list[tuple[int, ...]] = []
    for length in range(1, 5):
        for address in range(2**length):
            words.append(
                tuple((address >> (length - 1 - index)) & 1 for index in range(length))
            )
    return tuple(words)


def _control_rollout(
    codes: torch.Tensor,
    decoder: torch.Tensor,
    anchors: torch.Tensor,
    maps: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    logits: list[torch.Tensor] = []
    targets: list[int] = []
    starts: list[int] = []
    for word in _control_words():
        product = torch.eye(12, dtype=torch.float64)
        for operator in word:
            product = codes[operator] @ product
        for start in range(8):
            hidden = product @ anchors[start]
            logits.append(decoder @ hidden)
            target = start
            for operator in word:
                target = int(maps[operator, target])
            targets.append(target)
            starts.append(start)
    result = torch.stack(logits)
    _require_finite("control rollout logits", result)
    return (
        result,
        torch.tensor(targets, dtype=torch.long),
        torch.tensor(starts, dtype=torch.long),
    )


def _semantic_sensitivity_oracle(
    codes: torch.Tensor,
    decoder: torch.Tensor,
    anchors: torch.Tensor,
    maps: torch.Tensor,
) -> dict[str, Any]:
    """Require exact action execution and nonidentity counterfactual changes."""

    logits, targets, starts = _control_rollout(codes, decoder, anchors, maps)
    predictions = logits.argmax(dim=1)
    robust, margins = _robust_target(logits, targets, 2.0**-18)
    nonidentity = targets != starts
    if int(nonidentity.sum()) < 1:
        raise AssayIntegrityError("semantic control bank lacks a nonidentity transition")
    ordinary_accuracy = float((predictions == targets).to(torch.float64).mean())
    robust_accuracy = float(robust.to(torch.float64).mean())
    change_rate = float((predictions[nonidentity] != starts[nonidentity]).to(torch.float64).mean())
    nonidentity_accuracy = float(
        (predictions[nonidentity] == targets[nonidentity]).to(torch.float64).mean()
    )
    return {
        "examples": int(targets.numel()),
        "nonidentity_examples": int(nonidentity.sum()),
        "ordinary_accuracy": ordinary_accuracy,
        "robust_accuracy": robust_accuracy,
        "nonidentity_accuracy": nonidentity_accuracy,
        "prediction_change_rate_on_nonidentity": change_rate,
        "minimum_margin": float(margins.min()),
        "passed": (
            ordinary_accuracy == 1.0
            and robust_accuracy == 1.0
            and nonidentity_accuracy == 1.0
            and change_rate == 1.0
        ),
    }


def _classified_control(
    *,
    expected: str,
    condition: bool,
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "expected_classification": expected,
        "observed_classification": expected if condition else "MISCLASSIFIED",
        "correctly_classified": bool(condition),
        **dict(evidence),
    }


def adversarial_assay_controls() -> dict[str, Any]:
    """Run every preregistered calibration under its exact sealed name.

    Identity and random block-diagonal operators genuinely satisfy the kernel
    geometry.  They are rejected only by the explicit semantic execution and
    counterfactual-sensitivity oracle below, never by relabeling good geometry
    as leakage after inspecting the outcome.
    """

    registered_names = (
        "exact_7_plus_1_plus_4",
        "quotient_curved_ambient",
        "common_logit_shift",
        "cross_block_leaky",
        "identity_collapse",
        "random_block_orthogonal",
        "global_coordinate_conjugate",
        "rank6_collapse",
        "rank8_intrusion",
        "full_rank_leaky",
    )
    fixture = _semantic_control_fixture()
    s = fixture["behavioral_projector"]
    line = fixture["common_projector"]
    fiber = fixture["ambient_projector"]
    decoder = fixture["decoder"]
    anchors = fixture["anchors"]
    maps = fixture["maps"]
    exact_codes = fixture["codes"]
    identity = fixture["identity"]
    words = build_suffix_word_bank(
        operator_count=2,
        samples_per_length=4,
        seed=601,
        lengths=DEFAULT_SUFFIX_LENGTHS,
    )

    exact_structure = audit_kernel_structure(s, line, fiber, decoder, exact_codes)
    exact_suffix = suffix_leakage_audit(s, line, fiber, decoder, exact_codes, words)
    exact_fiber = fiber_intervention_audit(s, line, fiber, decoder, exact_codes, words)
    exact_semantic = _semantic_sensitivity_oracle(exact_codes, decoder, anchors, maps)
    exact_condition = (
        exact_structure.passed
        and exact_suffix.passed
        and exact_fiber.passed
        and exact_semantic["passed"]
    )

    # Same exact semantic representation, deliberately nonrepresentational K.
    curved_ambient = torch.eye(4, dtype=torch.float64).expand(2, -1, -1).clone()
    for operator, angle_value in enumerate((0.17, 0.19)):
        angle = torch.tensor(angle_value, dtype=torch.float64)
        curved_ambient[operator, 0, 0] = torch.cos(angle)
        curved_ambient[operator, 0, 1] = -torch.sin(angle)
        curved_ambient[operator, 1, 0] = torch.sin(angle)
        curved_ambient[operator, 1, 1] = torch.cos(angle)
    curved_codes = _assemble_control_codes(exact_codes[:, :7, :7], curved_ambient)
    flat_relation = (exact_codes[1] @ exact_codes[1]).unsqueeze(0)
    curved_relation = (curved_codes[1] @ curved_codes[1]).unsqueeze(0)
    curved_path = path_defect_from_products(
        s, line, fiber, identity.unsqueeze(0), curved_relation
    )
    curved_logits, curved_targets, _ = _control_rollout(
        curved_codes, decoder, anchors, maps
    )
    exact_logits, exact_targets, _ = _control_rollout(exact_codes, decoder, anchors, maps)
    if not torch.equal(curved_targets, exact_targets):
        raise AssayIntegrityError("curved and exact control target banks diverged")
    curved_behavior_delta = float((curved_logits - exact_logits).abs().max())
    curved_accuracy = float(
        (curved_logits.argmax(dim=1) == curved_targets).to(torch.float64).mean()
    )
    curved_condition = (
        curved_path.vertical_curvature_only
        and curved_behavior_delta <= 1e-10
        and curved_accuracy == 1.0
        and _semantic_sensitivity_oracle(curved_codes, decoder, anchors, maps)["passed"]
    )

    # The raw output moves, but only along the exact all-ones logit gauge.
    common_direction = torch.zeros(12, dtype=torch.float64)
    common_direction[7] = 1.0
    shift_delta = decoder @ (3.0 * common_direction)
    centered_shift = shift_delta - shift_delta.mean()
    shifted_logits = exact_logits + shift_delta
    common_condition = (
        float(torch.linalg.vector_norm(shift_delta)) > 1.0
        and float(centered_shift.abs().max()) <= 1e-12
        and torch.equal(shifted_logits.argmax(dim=1), exact_logits.argmax(dim=1))
    )

    mix = identity.clone()
    mix_angle = torch.tensor(0.31, dtype=torch.float64)
    mix[0, 0] = torch.cos(mix_angle)
    mix[0, 8] = -torch.sin(mix_angle)
    mix[8, 0] = torch.sin(mix_angle)
    mix[8, 8] = torch.cos(mix_angle)
    cross_codes = exact_codes.clone()
    cross_codes[0] = mix @ exact_codes[0] @ mix.T
    cross_structure = audit_kernel_structure(s, line, fiber, decoder, cross_codes)
    cross_suffix = suffix_leakage_audit(s, line, fiber, decoder, cross_codes, words)
    cross_fiber = fiber_intervention_audit(s, line, fiber, decoder, cross_codes, words)
    cross_condition = (
        not cross_structure.passed
        and not cross_suffix.passed
        and not cross_fiber.passed
        and max(
            cross_structure.behavioral_to_ambient_leakage,
            cross_structure.ambient_to_behavioral_leakage,
        )
        > 0.1
    )

    identity_codes = identity.expand(2, -1, -1).clone()
    identity_structure = audit_kernel_structure(s, line, fiber, decoder, identity_codes)
    identity_suffix = suffix_leakage_audit(s, line, fiber, decoder, identity_codes, words)
    identity_semantic = _semantic_sensitivity_oracle(identity_codes, decoder, anchors, maps)
    identity_condition = (
        identity_structure.passed
        and identity_suffix.passed
        and not identity_semantic["passed"]
        and identity_semantic["prediction_change_rate_on_nonidentity"] == 0.0
    )

    random_behavioral = torch.stack(
        (_orthogonal_control_matrix(7, 613), _orthogonal_control_matrix(7, 617))
    )
    random_ambient = torch.stack(
        (_orthogonal_control_matrix(4, 619), _orthogonal_control_matrix(4, 631))
    )
    random_codes = _assemble_control_codes(random_behavioral, random_ambient)
    random_structure = audit_kernel_structure(s, line, fiber, decoder, random_codes)
    random_suffix = suffix_leakage_audit(s, line, fiber, decoder, random_codes, words)
    random_semantic = _semantic_sensitivity_oracle(random_codes, decoder, anchors, maps)
    random_condition = (
        random_structure.passed
        and random_suffix.passed
        and not random_semantic["passed"]
        and random_semantic["robust_accuracy"] < 0.5
    )

    gauge = _orthogonal_control_matrix(12, 607)
    same_words = torch.zeros((2, 3), dtype=torch.long)
    gauge_audit = gauge_covariance_audit(
        s,
        line,
        fiber,
        decoder,
        exact_codes,
        words,
        same_words,
        same_words,
        gauge,
    )
    transformed_codes = gauge @ exact_codes @ gauge.T
    transformed_decoder = decoder @ gauge.T
    transformed_anchors = anchors @ gauge.T
    transformed_logits, transformed_targets, _ = _control_rollout(
        transformed_codes, transformed_decoder, transformed_anchors, maps
    )
    gauge_behavior_delta = float((transformed_logits - exact_logits).abs().max())
    gauge_condition = (
        gauge_audit.passed
        and torch.equal(transformed_targets, exact_targets)
        and gauge_behavior_delta <= 1e-10
        and torch.equal(transformed_logits.argmax(dim=1), exact_logits.argmax(dim=1))
    )

    s6 = torch.diag(torch.tensor([1.0] * 6 + [0.0] * 6, dtype=torch.float64))
    line6 = torch.diag(
        torch.tensor([0.0] * 6 + [1.0] + [0.0] * 5, dtype=torch.float64)
    )
    fiber6 = identity - s6 - line6
    decoder6 = torch.zeros_like(decoder)
    decoder6[:, :6] = fixture["basis"][:, :6]
    decoder6[:, 6] = 1.0
    rank6 = audit_kernel_structure(s6, line6, fiber6, decoder6, identity_codes)
    rank6_condition = (
        not rank6.passed
        and not rank6.rank_ambiguous
        and rank6.behavioral_rank == 6
        and rank6.centered_null_rank == 6
    )

    s8 = torch.diag(torch.tensor([1.0] * 8 + [0.0] * 4, dtype=torch.float64))
    line8 = torch.diag(
        torch.tensor([0.0] * 8 + [1.0] + [0.0] * 3, dtype=torch.float64)
    )
    fiber8 = identity - s8 - line8
    decoder8 = torch.zeros_like(decoder)
    decoder8[:, :7] = fixture["basis"]
    decoder8[:, 8] = 1.0
    rank8 = audit_kernel_structure(s8, line8, fiber8, decoder8, identity_codes)
    rank8_condition = (
        not rank8.passed
        and not rank8.rank_ambiguous
        and rank8.behavioral_rank == 8
        and rank8.centered_null_rank == 4
    )

    # Orthogonal full-rank recurrence with complete future leakage.  Matrix
    # rank and norm stability alone therefore cannot pass the assay.
    shift = torch.roll(identity, shifts=1, dims=0)
    leaky_codes = torch.stack((shift, shift.T), dim=0)
    leaky_structure = audit_kernel_structure(s, line, fiber, decoder, leaky_codes)
    leaky_suffix = suffix_leakage_audit(s, line, fiber, decoder, leaky_codes, words)
    leaky_fiber = fiber_intervention_audit(s, line, fiber, decoder, leaky_codes, words)
    full_leaky_condition = (
        not leaky_structure.passed
        and not leaky_suffix.passed
        and not leaky_fiber.passed
        and leaky_suffix.observer_rank == 12
        and leaky_structure.behavioral_to_null_leakage > 0.1
    )

    horizontal_angle = torch.tensor(0.37, dtype=torch.float64)
    horizontal = identity.clone()
    horizontal[0, 0] = torch.cos(horizontal_angle)
    horizontal[0, 1] = -torch.sin(horizontal_angle)
    horizontal[1, 0] = torch.sin(horizontal_angle)
    horizontal[1, 1] = torch.cos(horizontal_angle)
    horizontal_path = path_defect_from_products(
        s, line, fiber, identity.unsqueeze(0), horizontal.unsqueeze(0)
    )

    registered: dict[str, dict[str, Any]] = {
        "exact_7_plus_1_plus_4": _classified_control(
            expected="PASS_EXACT_INVARIANT_KERNEL",
            condition=exact_condition,
            evidence={
                "structure": exact_structure.to_dict(),
                "suffix": exact_suffix.to_dict(),
                "fiber_intervention": exact_fiber.to_dict(),
                "semantic_oracle": exact_semantic,
            },
        ),
        "quotient_curved_ambient": _classified_control(
            expected="PASS_QUOTIENT_CURVED_AMBIENT",
            condition=curved_condition,
            evidence={
                "path": curved_path.to_dict(),
                "behavior_max_abs_logit_delta_vs_exact": curved_behavior_delta,
                "behavior_accuracy": curved_accuracy,
                "flat_relation_full_defect": float(
                    torch.linalg.matrix_norm(flat_relation - identity, ord=2)
                ),
            },
        ),
        "common_logit_shift": _classified_control(
            expected="PASS_CENTERED_COMMON_LOGIT_INVARIANCE",
            condition=common_condition,
            evidence={
                "raw_shift_l2": float(torch.linalg.vector_norm(shift_delta)),
                "common_uniformity_residual": float(centered_shift.abs().max()),
                "prediction_retention": float(
                    (shifted_logits.argmax(dim=1) == exact_logits.argmax(dim=1))
                    .to(torch.float64)
                    .mean()
                ),
            },
        ),
        "cross_block_leaky": _classified_control(
            expected="REJECT_CROSS_BLOCK_LEAKAGE",
            condition=cross_condition,
            evidence={
                "structure": cross_structure.to_dict(),
                "suffix_passed": cross_suffix.passed,
                "fiber_intervention_passed": cross_fiber.passed,
            },
        ),
        "identity_collapse": _classified_control(
            expected="REJECT_SEMANTIC_IDENTITY_COLLAPSE",
            condition=identity_condition,
            evidence={
                "geometry_passed": identity_structure.passed and identity_suffix.passed,
                "semantic_oracle": identity_semantic,
                "rejection_basis": "semantic_sensitivity_oracle_not_geometry",
            },
        ),
        "random_block_orthogonal": _classified_control(
            expected="REJECT_RANDOM_SEMANTIC_ACTION",
            condition=random_condition,
            evidence={
                "geometry_passed": random_structure.passed and random_suffix.passed,
                "semantic_oracle": random_semantic,
                "rejection_basis": "semantic_execution_oracle_not_geometry",
            },
        ),
        "global_coordinate_conjugate": _classified_control(
            expected="PASS_GLOBAL_COORDINATE_CONJUGATE",
            condition=gauge_condition,
            evidence={
                "gauge": gauge_audit.to_dict(),
                "behavior_max_abs_logit_delta": gauge_behavior_delta,
                "prediction_retention": float(
                    (transformed_logits.argmax(dim=1) == exact_logits.argmax(dim=1))
                    .to(torch.float64)
                    .mean()
                ),
            },
        ),
        "rank6_collapse": _classified_control(
            expected="REJECT_RANK6_COLLAPSE",
            condition=rank6_condition,
            evidence={
                "structure": rank6.to_dict(),
            },
        ),
        "rank8_intrusion": _classified_control(
            expected="REJECT_RANK8_INTRUSION",
            condition=rank8_condition,
            evidence={
                "structure": rank8.to_dict(),
            },
        ),
        "full_rank_leaky": _classified_control(
            expected="REJECT_FULL_RANK_LEAKAGE",
            condition=full_leaky_condition,
            evidence={
                "structure_passed": leaky_structure.passed,
                "suffix_passed": leaky_suffix.passed,
                "fiber_passed": leaky_fiber.passed,
                "observer_rank": leaky_suffix.observer_rank,
                "behavioral_to_null": leaky_structure.behavioral_to_null_leakage,
                "detected": full_leaky_condition,
            },
        ),
    }

    # Retain earlier developmental aliases without substituting them for the
    # exact preregistered receipt keys.
    s9 = torch.diag(torch.tensor([1.0] * 9 + [0.0] * 3, dtype=torch.float64))
    line9 = torch.diag(
        torch.tensor([0.0] * 9 + [1.0] + [0.0] * 2, dtype=torch.float64)
    )
    fiber9 = identity - s9 - line9
    decoder9 = torch.zeros_like(decoder)
    decoder9[:, :7] = fixture["basis"]
    decoder9[:, 9] = 1.0
    rank9 = audit_kernel_structure(s9, line9, fiber9, decoder9, identity_codes)
    ambiguous_s = s.clone()
    ambiguous_s[6, 6] = 0.5
    ambiguous_fiber = identity - ambiguous_s - line
    ambiguous = audit_kernel_structure(
        ambiguous_s, line, ambiguous_fiber, decoder, identity_codes
    )

    assay_valid = all(
        control["correctly_classified"] for control in registered.values()
    ) and not ambiguous.passed and ambiguous.rank_ambiguous
    result: dict[str, Any] = {
        "schema": "komorebi.neuralese.invariant_kernel_controls.v2",
        "registered_control_names": list(registered_names),
        "registered_controls": registered,
        "kernel": {
            name: registered[name]
            for name in (
                "exact_7_plus_1_plus_4",
                "quotient_curved_ambient",
                "cross_block_leaky",
                "global_coordinate_conjugate",
                "rank6_collapse",
                "rank8_intrusion",
                "full_rank_leaky",
            )
        },
        "behavioral": {
            name: registered[name]
            for name in (
                "exact_7_plus_1_plus_4",
                "common_logit_shift",
                "identity_collapse",
                "random_block_orthogonal",
                "global_coordinate_conjugate",
            )
        },
        "rank7": {
            "passed": exact_structure.passed,
            "behavioral_rank": exact_structure.behavioral_rank,
            "centered_null_rank": exact_structure.centered_null_rank,
        },
        "rank9": {
            "passed": rank9.passed,
            "behavioral_rank": rank9.behavioral_rank,
            "expected_behavioral_rank": rank9.expected_behavioral_rank,
            "detected": not rank9.passed,
        },
        "ambiguous_projector": {
            "passed": ambiguous.passed,
            "rank_ambiguous": ambiguous.rank_ambiguous,
            "detected": not ambiguous.passed and ambiguous.rank_ambiguous,
        },
        "horizontal_curved": {
            "quotient_flat": horizontal_path.quotient_flat,
            "maximum_quotient_defect": horizontal_path.maximum_quotient_defect,
            "detected": not horizontal_path.quotient_flat,
        },
        "vertical_curved": {
            "quotient_flat": curved_path.quotient_flat,
            "common_flat": curved_path.common_flat,
            "vertical_flat": curved_path.vertical_flat,
            "vertical_curvature_only": curved_path.vertical_curvature_only,
            "maximum_vertical_defect": curved_path.maximum_vertical_defect,
            "detected_without_false_quotient_failure": curved_path.vertical_curvature_only,
        },
        "gauge_covariance": gauge_audit.to_dict(),
        "compiled_hard_control": {
            "memory_claim_eligible": False,
            "reason": "architectural fiber isolation is not evidence of learned memory",
        },
        "assay_valid": assay_valid,
    }
    result.update(registered)
    return result


def _floating_tensor(name: str, value: torch.Tensor, *, minimum_ndim: int) -> torch.Tensor:
    if not isinstance(value, torch.Tensor):
        raise AssayIntegrityError(f"{name} must be a torch.Tensor")
    if not value.is_floating_point() or value.ndim < minimum_ndim:
        raise AssayIntegrityError(f"{name} must be a floating tensor with ndim >= {minimum_ndim}")
    _require_finite(name, value)
    return value.detach()


def _integer_tensor(name: str, value: torch.Tensor) -> torch.Tensor:
    if not isinstance(value, torch.Tensor) or value.dtype == torch.bool:
        raise AssayIntegrityError(f"{name} must be an integer torch.Tensor")
    if value.dtype not in (
        torch.uint8,
        torch.int8,
        torch.int16,
        torch.int32,
        torch.int64,
    ):
        raise AssayIntegrityError(f"{name} must use an integer dtype")
    return value.detach()


def _require_finite(name: str, value: torch.Tensor) -> None:
    if not bool(torch.isfinite(value).all()):
        raise AssayIntegrityError(f"{name} contains a non-finite value")


def _positive_finite(name: str, value: float) -> float:
    if isinstance(value, bool):
        raise AssayIntegrityError(f"{name} must be a finite positive number")
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise AssayIntegrityError(f"{name} must be a finite positive number")
    return result


def _nonnegative_finite(name: str, value: float) -> float:
    if isinstance(value, bool):
        raise AssayIntegrityError(f"{name} must be a finite nonnegative number")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise AssayIntegrityError(f"{name} must be a finite nonnegative number")
    return result


def _prepare_three_way_split(
    behavioral_projector: torch.Tensor,
    common_projector: torch.Tensor,
    ambient_projector: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    supplied = (
        ("behavioral_projector", behavioral_projector),
        ("common_projector", common_projector),
        ("ambient_projector", ambient_projector),
    )
    converted: list[torch.Tensor] = []
    dimension: int | None = None
    device: torch.device | None = None
    for name, value in supplied:
        tensor = _floating_tensor(name, value, minimum_ndim=2)
        if tensor.ndim != 2 or tensor.shape[0] != tensor.shape[1]:
            raise AssayIntegrityError(f"{name} must be a square matrix")
        if dimension is None:
            dimension = int(tensor.shape[0])
            device = tensor.device
        if tensor.shape != (dimension, dimension):
            raise AssayIntegrityError("all projectors must have the same square shape")
        converted.append(tensor.to(device=device, dtype=torch.float64))
    assert dimension is not None
    if dimension < 3:
        raise AssayIntegrityError("three-way split requires hidden dimension >= 3")
    return converted[0], converted[1], converted[2]


def _prepare_two_way_split(
    behavioral_projector: torch.Tensor,
    centered_null_projector: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    behavioral = _floating_tensor(
        "behavioral_projector", behavioral_projector, minimum_ndim=2
    )
    null = _floating_tensor(
        "centered_null_projector", centered_null_projector, minimum_ndim=2
    )
    if (
        behavioral.ndim != 2
        or behavioral.shape[0] != behavioral.shape[1]
        or null.shape != behavioral.shape
    ):
        raise AssayIntegrityError("two-way projectors must share one square shape")
    device = behavioral.device
    return (
        behavioral.to(device=device, dtype=torch.float64),
        null.to(device=device, dtype=torch.float64),
    )


def _square_matrix_batch(
    name: str,
    value: torch.Tensor,
    dimension: int,
    device: torch.device,
) -> torch.Tensor:
    result = _floating_tensor(name, value, minimum_ndim=2).to(
        device=device, dtype=torch.float64
    )
    if result.shape[-2:] != (dimension, dimension):
        raise AssayIntegrityError(f"{name} must end in ({dimension},{dimension})")
    if result.ndim == 2:
        result = result.unsqueeze(0)
    if result.numel() == 0:
        raise AssayIntegrityError(f"{name} cannot be empty")
    return result


def _state_rows(
    name: str,
    value: torch.Tensor,
    dimension: int,
    device: torch.device,
) -> torch.Tensor:
    result = _floating_tensor(name, value, minimum_ndim=2).to(
        device=device, dtype=torch.float64
    )
    if result.ndim != 2 or result.shape[1] != dimension or result.shape[0] < 1:
        raise AssayIntegrityError(f"{name} must have shape (examples,{dimension})")
    return result


def _target_vector(
    name: str,
    value: torch.Tensor,
    examples: int,
    classes: int,
    device: torch.device,
) -> torch.Tensor:
    result = _integer_tensor(name, value).to(device=device, dtype=torch.long)
    if result.shape != (examples,):
        raise AssayIntegrityError(f"{name} must have shape ({examples},)")
    if int(result.min()) < 0 or int(result.max()) >= classes:
        raise AssayIntegrityError(f"{name} contains an out-of-range class")
    return result


def _spectral(value: torch.Tensor) -> float:
    _require_finite("spectral-norm input", value)
    return float(torch.linalg.matrix_norm(value, ord=2))


def _spectral_values(value: torch.Tensor) -> torch.Tensor:
    _require_finite("spectral-norm input", value)
    result = torch.linalg.matrix_norm(value, ord=2, dim=(-2, -1)).reshape(-1)
    _require_finite("spectral norms", result)
    return result


def _max_spectral(value: torch.Tensor) -> float:
    result = _spectral_values(value)
    if result.numel() < 1:
        raise AssayIntegrityError("cannot summarize an empty matrix batch")
    return float(result.max())


def _projector_rank(projector: torch.Tensor, tolerance: float) -> tuple[int, bool]:
    singular = torch.linalg.svdvals(projector)
    _require_finite("projector singular values", singular)
    near_zero = singular <= tolerance
    near_one = (singular - 1.0).abs() <= tolerance
    ambiguous = bool((~(near_zero | near_one)).any())
    return int(near_one.sum()), ambiguous


def _matrix_rank(matrix: torch.Tensor, relative_tolerance: float) -> tuple[int, bool]:
    singular = torch.linalg.svdvals(matrix)
    _require_finite("matrix singular values", singular)
    if singular.numel() < 1 or float(singular[0]) <= 0.0:
        return 0, False
    relative = singular / singular[0]
    rank = int((relative > relative_tolerance).sum())
    # A value very near the classification threshold is not silently assigned
    # to either side.  The broad factor-of-two band is intentional.
    ambiguous = bool(
        ((relative >= relative_tolerance / 2.0) & (relative <= relative_tolerance * 2.0)).any()
    )
    return rank, ambiguous


def _projector_frame(
    projector: torch.Tensor,
    expected_rank: int,
    tolerance: float,
    name: str,
) -> torch.Tensor:
    symmetric = (projector + projector.T) / 2.0
    eigenvalues, eigenvectors = torch.linalg.eigh(symmetric)
    _require_finite(f"{name} eigensystem", eigenvalues)
    near_one = (eigenvalues - 1.0).abs() <= tolerance
    near_zero = eigenvalues.abs() <= tolerance
    if bool((~(near_one | near_zero)).any()) or int(near_one.sum()) != expected_rank:
        raise AssayIntegrityError(f"{name} has ambiguous or unexpected rank")
    frame = eigenvectors[:, near_one]
    _require_finite(f"{name} frame", frame)
    return frame


def _validate_required_lengths(lengths: Sequence[int]) -> tuple[int, ...]:
    if isinstance(lengths, (str, bytes)):
        raise AssayIntegrityError("suffix lengths must be an integer sequence")
    normalized = tuple(int(value) for value in lengths)
    if not normalized or any(
        isinstance(value, bool) or not isinstance(value, int) or value < 0
        for value in lengths
    ):
        raise AssayIntegrityError("suffix lengths must be nonnegative integers")
    if len(set(normalized)) != len(normalized):
        raise AssayIntegrityError("suffix lengths must be unique")
    return tuple(sorted(normalized))


def _validate_suffix_mapping(
    suffix_words: Mapping[int, torch.Tensor],
    required_lengths: Sequence[int],
) -> tuple[int, ...]:
    if not isinstance(suffix_words, Mapping):
        raise AssayIntegrityError("suffix_words must be a mapping")
    lengths = _validate_required_lengths(required_lengths)
    if set(suffix_words) != set(lengths):
        raise AssayIntegrityError(
            f"suffix_words must contain exactly the required lengths {list(lengths)}"
        )
    for length in lengths:
        words = _integer_tensor(f"suffix_words[{length}]", suffix_words[length])
        if words.ndim not in (2, 3) or words.shape[-1] != length or words.shape[-2] < 1:
            raise AssayIntegrityError(
                f"suffix_words[{length}] has an invalid shape for length {length}"
            )
    return lengths


def _robust_target(
    logits: torch.Tensor,
    targets: torch.Tensor,
    tau: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    if logits.ndim != 2 or targets.shape != (logits.shape[0],):
        raise AssayIntegrityError("logits and targets have incompatible shapes")
    rows = torch.arange(logits.shape[0], device=logits.device)
    target_score = logits[rows, targets]
    alternatives = logits.clone()
    alternatives[rows, targets] = -torch.inf
    margins = target_score - alternatives.max(dim=1).values
    _require_finite("classification margins", margins)
    predictions = logits.argmax(dim=1)
    robust = (predictions == targets) & (margins > tau)
    return robust, margins


__all__ = [
    "AssayIntegrityError",
    "DEFAULT_SUFFIX_LENGTHS",
    "FiberInterventionAudit",
    "GaugeCovarianceAudit",
    "ExtractedKernelGeometry",
    "KernelStructureAudit",
    "NullInterventionAudit",
    "PathDefectAudit",
    "SemanticTransplantAudit",
    "SuffixLeakageAudit",
    "TwoWayPathAudit",
    "TwoWayStructureAudit",
    "TwoWaySuffixAudit",
    "adversarial_assay_controls",
    "audit_centered_quotient_paths",
    "audit_centered_quotient_structure",
    "audit_centered_quotient_suffixes",
    "audit_kernel_structure",
    "build_suffix_word_bank",
    "centered_null_intervention_audit",
    "centered_decoder",
    "extract_model_geometry",
    "fiber_intervention_audit",
    "gauge_covariance_audit",
    "path_defect_audit",
    "path_defect_from_products",
    "path_products",
    "semantic_transplant_audit",
    "suffix_leakage_audit",
]
