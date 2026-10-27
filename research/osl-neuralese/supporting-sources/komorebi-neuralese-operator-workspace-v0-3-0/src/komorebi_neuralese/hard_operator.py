"""Hard-stable latent operators for the Komorebi v0.3 experiment.

The public recurrent-model API remains identical to the v0.2 linear-hyper
models.  The only architectural change is that the table encoder no longer
emits an unconstrained transition matrix directly.  It emits parameters for an
orthogonal matrix.  The primary model uses fixed Euclidean coordinates; the
secondary learned-metric model conjugates the matrix back from whitened
coordinates with one bounded determinant-one SPD metric.

For any supported projection,

    Q(T) = orthogonalize(R(T))
    M(T) = W^-1 Q(T) W,       G = W.T W.

The primary projection is sign-canonicalized reduced QR because it covers both
components of ``O(d)`` and has the strongest development-only trainability
result.  Skew exponential, Cayley, and SVD polar factors remain explicit
ablations.  In all cases ``M.T @ G @ M == G`` up to floating-point roundoff for
every table.  Operator-code collapse and per-step contraction are therefore
outside the parameter space rather than merely discouraged by a loss.
"""

from __future__ import annotations

from typing import Final, Literal

import torch
from torch import nn
from torch.nn import functional as F

from komorebi_neuralese.algebra import N_STATES
from komorebi_neuralese.models import LinearHyperOperatorRNN, RecurrentOperatorModel


OrthogonalParameterization = Literal["qr", "matrix_exp", "cayley", "polar"]

HARD_MODEL_NAME: Final[str] = "linear_hyper_hard"
HARD_METRIC_MODEL_NAME: Final[str] = "linear_hyper_hard_metric"
SUPPORTED_PARAMETERIZATIONS: Final[tuple[str, ...]] = (
    "qr",
    "matrix_exp",
    "cayley",
    "polar",
)


def skew_part(raw: torch.Tensor) -> torch.Tensor:
    """Return the skew-symmetric part of a square matrix batch."""
    if raw.ndim < 2 or raw.shape[-1] != raw.shape[-2]:
        raise ValueError("raw operator parameters must have square trailing dimensions")
    return 0.5 * (raw - raw.transpose(-1, -2))


def matrix_exp_orthogonal(raw: torch.Tensor) -> torch.Tensor:
    """Map arbitrary square matrices smoothly into ``SO(d)``.

    ``torch.matrix_exp`` of a real skew-symmetric matrix is orthogonal with
    determinant +1 in exact arithmetic.  Unlike a Cayley map, the exponential
    can represent orthogonal matrices having eigenvalue -1.
    """
    return torch.matrix_exp(skew_part(raw))


def canonical_qr_orthogonal(raw: torch.Tensor) -> torch.Tensor:
    """Return the sign-canonicalized reduced-QR orthogonal factor.

    Making the diagonal of ``R`` nonnegative removes the arbitrary QR column
    signs and makes ``Q`` invariant to positive rescaling of a full-rank input.
    Unlike skew-exponential and Cayley maps, QR reaches both connected
    components of ``O(d)``.  The unavoidable component boundary occurs at a
    rank-deficient raw matrix, where QR gradients can be ill-conditioned.
    """
    if raw.ndim < 2 or raw.shape[-1] != raw.shape[-2]:
        raise ValueError("raw operator parameters must have square trailing dimensions")
    orthogonal, triangular = torch.linalg.qr(raw, mode="reduced")
    diagonal = torch.diagonal(triangular, dim1=-2, dim2=-1)
    signs = torch.where(diagonal < 0.0, -torch.ones_like(diagonal), torch.ones_like(diagonal)).detach()
    return orthogonal * signs.unsqueeze(-2)


def cayley_orthogonal(raw: torch.Tensor) -> torch.Tensor:
    """Map arbitrary square matrices into the no-minus-one-eigenvalue part of ``SO(d)``.

    This is retained as an ablation/benchmark backend.  ``I - A`` is
    nonsingular for real skew-symmetric ``A``, but the map cannot attain
    matrices with eigenvalue -1 and is therefore not the v0.3 primary model.
    """
    skew = skew_part(raw)
    dimension = skew.shape[-1]
    identity = torch.eye(dimension, dtype=skew.dtype, device=skew.device)
    return torch.linalg.solve(identity - skew, identity + skew)


def polar_orthogonal(raw: torch.Tensor) -> torch.Tensor:
    """Return the SVD polar factor of a square matrix batch.

    The polar factor covers both connected components of ``O(d)``.  Gradients
    are poorly conditioned at singular inputs and can be undefined at repeated
    singular values, so this backend is an ablation rather than the primary
    training parameterization.
    """
    if raw.ndim < 2 or raw.shape[-1] != raw.shape[-2]:
        raise ValueError("raw operator parameters must have square trailing dimensions")
    left, _, right_transpose = torch.linalg.svd(raw, full_matrices=False)
    return left @ right_transpose


def orthogonalize(
    raw: torch.Tensor,
    parameterization: OrthogonalParameterization = "matrix_exp",
) -> torch.Tensor:
    """Apply one of the exact/numerically tight orthogonal maps."""
    if parameterization == "qr":
        return canonical_qr_orthogonal(raw)
    if parameterization == "matrix_exp":
        return matrix_exp_orthogonal(raw)
    if parameterization == "cayley":
        return cayley_orthogonal(raw)
    if parameterization == "polar":
        return polar_orthogonal(raw)
    raise ValueError(
        f"unknown orthogonal parameterization {parameterization!r}; "
        f"expected one of {SUPPORTED_PARAMETERIZATIONS}"
    )


class HardOperatorRNN(LinearHyperOperatorRNN):
    """Linear hypernetwork with hard Euclidean-isometric recurrent operators.

    It deliberately subclasses the v0.2 linear-hyper model, preserving all
    ``run``/``continue_from_hidden`` behavior, matrix-code shape checks,
    composition training, metric diagnostics, and optimizer parameter-group
    handling.  Public operator codes remain ambient-coordinate matrices with
    shape ``(batch, slots, hidden_dim, hidden_dim)``.
    """

    model_name = HARD_MODEL_NAME

    def __init__(
        self,
        hidden_dim: int = 8,
        parameterization: OrthogonalParameterization = "qr",
        operator_init_std: float = 0.08,
    ) -> None:
        super().__init__(hidden_dim=hidden_dim, operator_init_std=operator_init_std)
        if parameterization not in SUPPORTED_PARAMETERIZATIONS:
            raise ValueError(
                f"unknown orthogonal parameterization {parameterization!r}; "
                f"expected one of {SUPPORTED_PARAMETERIZATIONS}"
            )
        self.parameterization: OrthogonalParameterization = parameterization
        if operator_init_std <= 0.0:
            raise ValueError("operator_init_std must be positive")
        self.operator_init_std = float(operator_init_std)

    def raw_operator_parameters(self, tables: torch.Tensor) -> torch.Tensor:
        """Return the unconstrained table-encoder output before hard projection."""
        if tables.ndim != 4:
            raise ValueError("tables must have shape (batch, slots, states, states)")
        batch, operators = tables.shape[:2]
        flat_tables = tables.reshape(batch * operators, -1)
        if flat_tables.shape[-1] != self.operator_encoder.in_features:
            raise ValueError(
                "table state dimensions do not match the operator encoder: "
                f"got {flat_tables.shape[-1]} features, expected "
                f"{self.operator_encoder.in_features}"
            )
        raw = self.operator_encoder(flat_tables)
        return raw.reshape(batch, operators, self.hidden_dim, self.hidden_dim)

    def intrinsic_operator_codes(self, tables: torch.Tensor) -> torch.Tensor:
        """Return the exactly orthogonal codes in whitened coordinates."""
        return orthogonalize(self.raw_operator_parameters(tables), self.parameterization)

    # Alias phrased for geometry/diagnostic callers.
    orthogonal_operator_codes = intrinsic_operator_codes

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        """Return hard-isometric operator matrices in ambient coordinates."""
        intrinsic = self.intrinsic_operator_codes(tables)
        return self.unwhiten_operators(intrinsic)

    def model_spec(self) -> dict[str, object]:
        """Return the semantic constructor receipt for reports/checkpoints."""
        return {
            "model_name": self.model_name,
            "class_name": type(self).__name__,
            "hidden_dim": self.hidden_dim,
            "orthogonal_parameterization": self.parameterization,
            "operator_init_std": self.operator_init_std,
            "metric_parameterization": "fixed_identity",
        }

    def get_extra_state(self) -> dict[str, object]:
        return self.model_spec()

    def set_extra_state(self, state: object) -> None:
        if not isinstance(state, dict):
            raise TypeError("hard-operator extra state must be a dictionary")
        parameterization = state.get("orthogonal_parameterization")
        if parameterization not in SUPPORTED_PARAMETERIZATIONS:
            raise ValueError(f"invalid checkpoint orthogonal parameterization: {parameterization!r}")
        hidden_dim = int(state.get("hidden_dim", -1))
        if hidden_dim != self.hidden_dim:
            raise ValueError(
                f"checkpoint hidden_dim {hidden_dim} does not match constructed hidden_dim {self.hidden_dim}"
            )
        self.parameterization = parameterization
        self.operator_init_std = float(state.get("operator_init_std", self.operator_init_std))


class LearnedDiagonalMetric(nn.Module):
    """Cheap bounded determinant-one metric in a learned latent basis.

    A full SPD metric's eigenvectors are a global orthogonal gauge that can be
    absorbed by the freely learned state embeddings, decoder, and raw operator
    encoder.  Learning only its eigenvalues therefore retains the meaningful
    anisotropic scaling while replacing repeated matrix exponentials with
    elementwise exponentials and diagonal conjugation.
    """

    def __init__(self, dimension: int, log_frobenius_bound: float = 2.0) -> None:
        super().__init__()
        if dimension < 1:
            raise ValueError("dimension must be positive")
        if log_frobenius_bound <= 0.0:
            raise ValueError("log_frobenius_bound must be positive")
        self.dimension = int(dimension)
        self.log_frobenius_bound = float(log_frobenius_bound)
        self.raw_log_metric = nn.Parameter(torch.zeros(self.dimension))

    def log_diagonal(self) -> torch.Tensor:
        trace_free = self.raw_log_metric - self.raw_log_metric.mean()
        norm = torch.linalg.vector_norm(trace_free)
        ratio = norm / self.log_frobenius_bound
        denominator = ratio.clamp_min(torch.finfo(trace_free.dtype).eps)
        regular_scale = torch.tanh(ratio) / denominator
        taylor_scale = 1.0 - ratio.square() / 3.0
        scale = torch.where(ratio > 1e-6, regular_scale, taylor_scale)
        return trace_free * scale

    def log_matrix(self) -> torch.Tensor:
        return torch.diag(self.log_diagonal())

    bounded_log_metric = log_matrix

    def matrix(self) -> torch.Tensor:
        return torch.diag(torch.exp(self.log_diagonal()))

    metric_matrix = matrix
    forward = matrix

    def factors(self) -> tuple[torch.Tensor, torch.Tensor]:
        half = 0.5 * self.log_diagonal()
        return torch.diag(torch.exp(half)), torch.diag(torch.exp(-half))

    def whitener(self) -> torch.Tensor:
        return self.factors()[0]

    def inverse_whitener(self) -> torch.Tensor:
        return self.factors()[1]

    def condition_number(self) -> torch.Tensor:
        log_diagonal = self.log_diagonal()
        return torch.exp(log_diagonal.max() - log_diagonal.min())

    def get_extra_state(self) -> dict[str, object]:
        return {
            "dimension": self.dimension,
            "log_frobenius_bound": self.log_frobenius_bound,
            "parameterization": "bounded_trace_free_log_diagonal",
        }

    def set_extra_state(self, state: object) -> None:
        if not isinstance(state, dict):
            raise TypeError("metric extra state must be a dictionary")
        dimension = int(state.get("dimension", -1))
        if dimension != self.dimension:
            raise ValueError(
                f"checkpoint metric dimension {dimension} does not match constructed dimension {self.dimension}"
            )
        self.log_frobenius_bound = float(state["log_frobenius_bound"])


class HardMetricOperatorRNN(HardOperatorRNN):
    """Hard operator model conjugated by a learned diagonal SPD whitener."""

    model_name = HARD_METRIC_MODEL_NAME

    def __init__(
        self,
        hidden_dim: int = 8,
        log_metric_bound: float = 2.0,
        parameterization: OrthogonalParameterization = "qr",
        operator_init_std: float = 0.08,
    ) -> None:
        super().__init__(
            hidden_dim=hidden_dim,
            parameterization=parameterization,
            operator_init_std=operator_init_std,
        )
        self.learned_metric = LearnedDiagonalMetric(
            hidden_dim,
            log_frobenius_bound=log_metric_bound,
        )

    def metric_matrix(self) -> torch.Tensor:
        return self.learned_metric.matrix()

    def metric_factors(self) -> tuple[torch.Tensor, torch.Tensor]:
        return self.learned_metric.factors()

    def model_spec(self) -> dict[str, object]:
        spec = super().model_spec()
        spec.update(
            {
                "metric_parameterization": "bounded_trace_free_log_diagonal",
                "log_metric_frobenius_bound": self.learned_metric.log_frobenius_bound,
            }
        )
        return spec


class ExactTableOracle(RecurrentOperatorModel):
    """Parameter-free execution and closure ceiling.

    Episode tables use row actions, whereas the recurrent state is a column
    vector, so the exact latent operator is the table transpose.  This class is
    an assay/orientation check only.  It hard-codes the observable executor and
    is never evidence that a representation was learned.
    """

    model_name = "exact_table_oracle"
    hidden_dim = N_STATES

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return tables.transpose(-1, -2)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return F.one_hot(start, num_classes=N_STATES).to(dtype=torch.float32)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return hidden

    def metric_matrix(self) -> torch.Tensor:
        return torch.eye(N_STATES)

    def model_spec(self) -> dict[str, object]:
        return {
            "model_name": self.model_name,
            "class_name": type(self).__name__,
            "hidden_dim": self.hidden_dim,
            "operator_source": "observable_table_transpose",
            "claim_role": "exact_structured_ceiling_only",
        }


def _finite_summary(values: torch.Tensor) -> dict[str, float | int]:
    flattened = values.detach().double().reshape(-1)
    finite = flattened[torch.isfinite(flattened)]
    if finite.numel() == 0:
        return {
            "count": int(flattened.numel()),
            "finite_fraction": 0.0,
            "minimum": float("nan"),
            "median": float("nan"),
            "p95": float("nan"),
            "maximum": float("nan"),
        }
    return {
        "count": int(flattened.numel()),
        "finite_fraction": float(finite.numel() / max(flattened.numel(), 1)),
        "minimum": float(finite.min().cpu()),
        "median": float(finite.median().cpu()),
        "p95": float(torch.quantile(finite, 0.95).cpu()),
        "maximum": float(finite.max().cpu()),
    }


@torch.no_grad()
def hard_operator_health_metrics(
    model: HardOperatorRNN,
    tables: torch.Tensor,
) -> dict[str, object]:
    """Audit hard constraints and the raw projection's trainability margin.

    The smallest raw singular value is not a dynamical-stability requirement:
    projected codes stay orthogonal even for rank-deficient raw matrices.  It
    is nevertheless a crucial QR/polar optimization diagnostic because their
    derivatives become ill-conditioned near rank loss.
    """
    if not isinstance(model, HardOperatorRNN):
        raise TypeError("hard_operator_health_metrics requires a HardOperatorRNN")
    raw = model.raw_operator_parameters(tables)
    intrinsic = orthogonalize(raw, model.parameterization)
    ambient = model.unwhiten_operators(intrinsic)
    dimension = raw.shape[-1]
    flat_raw = raw.reshape(-1, dimension, dimension).double()
    flat_intrinsic = intrinsic.reshape(-1, dimension, dimension).double()
    flat_ambient = ambient.reshape(-1, dimension, dimension).double()

    raw_singular = torch.linalg.svdvals(flat_raw)
    raw_minimum = raw_singular[:, -1]
    raw_condition = raw_singular[:, 0] / raw_minimum.clamp_min(torch.finfo(torch.float64).tiny)
    intrinsic_singular = torch.linalg.svdvals(flat_intrinsic)
    determinant = torch.linalg.det(flat_intrinsic)
    identity = torch.eye(dimension, dtype=torch.float64, device=flat_intrinsic.device)
    orthogonality_defect = torch.linalg.matrix_norm(
        flat_intrinsic.transpose(-1, -2) @ flat_intrinsic - identity,
        ord="fro",
        dim=(-2, -1),
    ) / dimension**0.5

    metric = model.metric_matrix().detach().double()
    metric_defect = torch.linalg.matrix_norm(
        flat_ambient.transpose(-1, -2) @ metric @ flat_ambient - metric,
        ord="fro",
        dim=(-2, -1),
    ) / torch.linalg.matrix_norm(metric, ord="fro").clamp_min(torch.finfo(torch.float64).tiny)
    determinant_tolerance = 1e-6
    return {
        "available": True,
        "parameterization": model.parameterization,
        "operator_instances": int(flat_raw.shape[0]),
        "raw_minimum_singular_value": _finite_summary(raw_minimum),
        "raw_condition_number": _finite_summary(raw_condition),
        "intrinsic_minimum_singular_value": _finite_summary(intrinsic_singular[:, -1]),
        "intrinsic_maximum_singular_value": _finite_summary(intrinsic_singular[:, 0]),
        "intrinsic_orthogonality_defect": _finite_summary(orthogonality_defect),
        "metric_isometry_defect": _finite_summary(metric_defect),
        "determinant": _finite_summary(determinant),
        "determinant_positive_fraction": float((determinant > determinant_tolerance).double().mean().cpu()),
        "determinant_negative_fraction": float((determinant < -determinant_tolerance).double().mean().cpu()),
        "determinant_near_zero_fraction": float(
            (determinant.abs() <= determinant_tolerance).double().mean().cpu()
        ),
    }


def hard_operator_compute_shadow(
    operator_codes: torch.Tensor,
    parameterization: OrthogonalParameterization = "qr",
) -> torch.Tensor:
    """Optional projected shadow for profiling a soft matrix arm.

    Callers that intend to match training cost must keep the returned tensor in
    the autograd graph (for example by adding ``0.0 * shadow.sum()`` to the
    objective).  Detaching it matches only forward cost, not backward cost.
    """
    return orthogonalize(operator_codes, parameterization)


__all__ = [
    "HARD_MODEL_NAME",
    "HARD_METRIC_MODEL_NAME",
    "SUPPORTED_PARAMETERIZATIONS",
    "ExactTableOracle",
    "HardMetricOperatorRNN",
    "HardOperatorRNN",
    "LearnedDiagonalMetric",
    "OrthogonalParameterization",
    "cayley_orthogonal",
    "canonical_qr_orthogonal",
    "hard_operator_compute_shadow",
    "hard_operator_health_metrics",
    "matrix_exp_orthogonal",
    "orthogonalize",
    "polar_orthogonal",
    "skew_part",
]
