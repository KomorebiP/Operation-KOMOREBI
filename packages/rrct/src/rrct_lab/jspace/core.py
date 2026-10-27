"""Small NumPy primitives for Jacobian-discovered sparse workspaces.

The module deliberately contains no model- or experiment-specific policy.  It
extracts a low-rank residual-stream subspace from an average output Jacobian,
provides sparse nonnegative content operations, and tracks that subspace under
an exponential moving average.  All public arrays owned by a frame are backed
by immutable buffers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np


_FLOAT_EPSILON = np.finfo(np.float64).eps
_ORTHONORMAL_ATOL = 1e-10
_STATE_SCHEMA = "rrct_lab.moving_jacobian_frame.v1"


def _finite_array(value: Any, *, name: str, ndim: int) -> np.ndarray:
    try:
        array = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a numeric {ndim}-D array") from error
    if array.ndim != ndim:
        raise ValueError(f"{name} must be a {ndim}-D array")
    if any(size <= 0 for size in array.shape):
        raise ValueError(f"{name} must not have an empty dimension")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return np.array(array, dtype=np.float64, copy=True, order="C")


def _immutable_array(value: Any, *, name: str, ndim: int) -> np.ndarray:
    """Copy an array into a bytes-backed buffer that cannot be made writable."""

    array = _finite_array(value, name=name, ndim=ndim)
    return np.frombuffer(array.tobytes(order="C"), dtype=np.float64).reshape(
        array.shape
    )


def _positive_integer(value: Any, *, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} must be a positive integer")
    result = int(value)
    if result <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return result


def _nonnegative_integer(value: Any, *, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} must be a nonnegative integer")
    result = int(value)
    if result < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return result


def _bounded_float(
    value: Any,
    *,
    name: str,
    lower: float,
    upper: float,
    include_upper: bool,
) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not np.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    upper_ok = result <= upper if include_upper else result < upper
    if result < lower or not upper_ok:
        bracket = "]" if include_upper else ")"
        raise ValueError(f"{name} must lie in [{lower}, {upper}{bracket}")
    return result


def _validate_selection(
    rank: int | None,
    spectral_threshold: float | None,
    *,
    maximum_rank: int,
) -> tuple[int | None, float | None]:
    if (rank is None) == (spectral_threshold is None):
        raise ValueError("provide exactly one of rank or spectral_threshold")
    if rank is not None:
        selected_rank = _positive_integer(rank, name="rank")
        if selected_rank > maximum_rank:
            raise ValueError(f"rank must not exceed {maximum_rank}")
        return selected_rank, None
    threshold = _bounded_float(
        spectral_threshold,
        name="spectral_threshold",
        lower=0.0,
        upper=1.0,
        include_upper=False,
    )
    return None, threshold


def _validate_projector(value: Any, *, dimension: int | None = None) -> np.ndarray:
    projector = _finite_array(value, name="projector", ndim=2)
    if projector.shape[0] != projector.shape[1]:
        raise ValueError("projector must be square")
    if dimension is not None and projector.shape != (dimension, dimension):
        raise ValueError("projector has the wrong dimension")
    return projector


def _canonicalize_signs(basis: np.ndarray) -> np.ndarray:
    result = np.array(basis, dtype=np.float64, copy=True)
    for column_index in range(result.shape[1]):
        column = result[:, column_index]
        pivot = int(np.argmax(np.abs(column)))
        if column[pivot] < 0.0:
            result[:, column_index] *= -1.0
    return result


def _align_basis(candidate: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Transport a new subspace basis toward the preceding orientation.

    Projecting the old axes into the new subspace avoids arbitrary SVD sign
    flips and also stabilizes rotations inside nearly degenerate singular
    subspaces.  Candidate axes fill dimensions that did not previously exist.
    """

    if candidate.ndim != 2 or reference.ndim != 2:
        raise ValueError("candidate and reference bases must be matrices")
    if candidate.shape[0] != reference.shape[0]:
        raise ValueError("candidate and reference residual dimensions differ")
    projector = candidate @ candidate.T
    columns: list[np.ndarray] = []

    def append_if_independent(vector: np.ndarray, reference_axis: np.ndarray | None) -> None:
        candidate_vector = np.array(vector, dtype=np.float64, copy=True)
        for existing in columns:
            candidate_vector -= existing * float(np.dot(existing, candidate_vector))
        norm = float(np.linalg.norm(candidate_vector))
        if norm <= 64.0 * _FLOAT_EPSILON:
            return
        candidate_vector /= norm
        if reference_axis is not None:
            if float(np.dot(candidate_vector, reference_axis)) < 0.0:
                candidate_vector *= -1.0
        else:
            pivot = int(np.argmax(np.abs(candidate_vector)))
            if candidate_vector[pivot] < 0.0:
                candidate_vector *= -1.0
        columns.append(candidate_vector)

    for column_index in range(reference.shape[1]):
        if len(columns) == candidate.shape[1]:
            break
        reference_axis = reference[:, column_index]
        append_if_independent(projector @ reference_axis, reference_axis)

    for column_index in range(candidate.shape[1]):
        if len(columns) == candidate.shape[1]:
            break
        append_if_independent(candidate[:, column_index], None)

    # Coordinate axes are a deterministic final fallback for very degenerate
    # overlap patterns.  Their projections still remain in the new subspace.
    for axis_index in range(candidate.shape[0]):
        if len(columns) == candidate.shape[1]:
            break
        axis = np.zeros(candidate.shape[0], dtype=np.float64)
        axis[axis_index] = 1.0
        append_if_independent(projector @ axis, None)

    if len(columns) != candidate.shape[1]:
        raise RuntimeError("could not construct a stable basis orientation")
    return np.column_stack(columns)


@dataclass(frozen=True)
class JacobianFrameMetrics:
    """Measured geometric and calibration properties of a Jacobian frame."""

    projector_idempotence_defect: float
    jacobian_energy_capture: float
    activation_variance_fraction: float
    report_r2: float

    def __post_init__(self) -> None:
        values = (
            self.projector_idempotence_defect,
            self.jacobian_energy_capture,
            self.activation_variance_fraction,
            self.report_r2,
        )
        if not all(np.isfinite(value) for value in values):
            raise ValueError("frame metrics must be finite")
        if self.projector_idempotence_defect < 0.0:
            raise ValueError("projector idempotence defect must be nonnegative")
        for name, value in (
            ("jacobian_energy_capture", self.jacobian_energy_capture),
            ("activation_variance_fraction", self.activation_variance_fraction),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1]")
        if self.report_r2 > 1.0 + 1e-12:
            raise ValueError("report_r2 must not exceed one")


@dataclass(frozen=True, eq=False)
class JacobianFrame:
    """Immutable low-rank frame discovered from an average Jacobian.

    ``basis`` has shape ``(residual_dimension, rank)``.  In contrast,
    ``frame_vectors`` has one normalized residual-space direction per output
    content and therefore has shape
    ``(residual_dimension, content_dimension)``.
    """

    average_jacobian: np.ndarray
    basis: np.ndarray
    singular_values: np.ndarray
    top_k: int = 2
    _projector: np.ndarray = field(init=False, repr=False)
    _frame_vectors: np.ndarray = field(init=False, repr=False)
    _frame_pseudoinverse: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        jacobian = _immutable_array(
            self.average_jacobian, name="average_jacobian", ndim=2
        )
        basis = _immutable_array(self.basis, name="basis", ndim=2)
        singular_values = _immutable_array(
            self.singular_values, name="singular_values", ndim=1
        )
        maximum_rank = min(jacobian.shape)
        if basis.shape[0] != jacobian.shape[1]:
            raise ValueError("basis residual dimension does not match the Jacobian")
        if not 1 <= basis.shape[1] <= maximum_rank:
            raise ValueError("basis rank is outside the valid Jacobian range")
        if singular_values.shape != (maximum_rank,):
            raise ValueError("singular_values has the wrong length")
        if np.any(singular_values < 0.0):
            raise ValueError("singular_values must be nonnegative")
        if np.any(np.diff(singular_values) > 1e-12):
            raise ValueError("singular_values must be in descending order")
        if float(singular_values[0]) <= 0.0:
            raise ValueError("average_jacobian must have nonzero spectral energy")
        top_k = _positive_integer(self.top_k, name="top_k")
        if top_k > jacobian.shape[0]:
            raise ValueError("top_k must not exceed the content dimension")
        gram = basis.T @ basis
        if not np.allclose(
            gram,
            np.eye(basis.shape[1], dtype=np.float64),
            rtol=0.0,
            atol=_ORTHONORMAL_ATOL,
        ):
            raise ValueError("basis columns must be orthonormal")

        projector = basis @ basis.T
        # Content directions must live inside the selected subspace.  Using the
        # raw Jacobian rows here would let reconstruction or a swap reintroduce
        # singular directions that an explicit rank truncation discarded.
        frame_vectors = np.array(projector @ jacobian.T, dtype=np.float64, copy=True)
        norms = np.linalg.norm(frame_vectors, axis=0)
        nonzero = norms > 64.0 * _FLOAT_EPSILON
        frame_vectors[:, nonzero] /= norms[nonzero]
        frame_vectors[:, ~nonzero] = 0.0
        frame_pseudoinverse = np.linalg.pinv(frame_vectors)

        object.__setattr__(self, "average_jacobian", jacobian)
        object.__setattr__(self, "basis", basis)
        object.__setattr__(self, "singular_values", singular_values)
        object.__setattr__(self, "top_k", top_k)
        object.__setattr__(
            self,
            "_projector",
            _immutable_array(projector, name="projector", ndim=2),
        )
        object.__setattr__(
            self,
            "_frame_vectors",
            _immutable_array(frame_vectors, name="frame_vectors", ndim=2),
        )
        object.__setattr__(
            self,
            "_frame_pseudoinverse",
            _immutable_array(
                frame_pseudoinverse, name="frame_pseudoinverse", ndim=2
            ),
        )

    @property
    def residual_dimension(self) -> int:
        return int(self.average_jacobian.shape[1])

    @property
    def content_dimension(self) -> int:
        return int(self.average_jacobian.shape[0])

    @property
    def rank(self) -> int:
        return int(self.basis.shape[1])

    @property
    def projector(self) -> np.ndarray:
        return self._projector

    @property
    def frame_vectors(self) -> np.ndarray:
        return self._frame_vectors

    def _hidden(self, hidden: Any, *, allow_batch: bool) -> np.ndarray:
        try:
            vector = np.asarray(hidden, dtype=np.float64)
        except (TypeError, ValueError) as error:
            raise ValueError("hidden must be a finite numeric array") from error
        valid_dimensions = (1, 2) if allow_batch else (1,)
        if vector.ndim not in valid_dimensions:
            shape_name = "a vector or matrix" if allow_batch else "a vector"
            raise ValueError(f"hidden must be {shape_name}")
        if vector.shape[-1] != self.residual_dimension:
            raise ValueError("hidden has the wrong residual dimension")
        if not np.all(np.isfinite(vector)):
            raise ValueError("hidden must contain only finite values")
        return np.array(vector, dtype=np.float64, copy=True)

    def logits(self, hidden: Any) -> np.ndarray:
        """Apply the average Jacobian to one vector or a row-major batch."""

        vector = self._hidden(hidden, allow_batch=True)
        return np.asarray(vector @ self.average_jacobian.T, dtype=np.float64)

    def project(self, hidden: Any) -> np.ndarray:
        """Project one vector or a row-major batch into the selected subspace."""

        vector = self._hidden(hidden, allow_batch=True)
        return np.asarray(vector @ self.projector, dtype=np.float64)

    def ablate(self, hidden: Any) -> np.ndarray:
        """Remove the selected Jacobian subspace from activations."""

        vector = self._hidden(hidden, allow_batch=True)
        return np.asarray(vector - vector @ self.projector, dtype=np.float64)

    def sparse_code(self, hidden: Any, *, top_k: int | None = None) -> np.ndarray:
        """Return an at-most-top-k, nonnegative output-content code."""

        vector = self._hidden(hidden, allow_batch=False)
        selected_capacity = self.top_k if top_k is None else _positive_integer(
            top_k, name="top_k"
        )
        if selected_capacity > self.content_dimension:
            raise ValueError("top_k must not exceed the content dimension")
        # Codes describe the selected workspace, not report sensitivity in the
        # discarded complement of an explicitly truncated Jacobian.
        positive_scores = np.maximum(self.logits(self.project(vector)), 0.0)
        order = np.argsort(-positive_scores, kind="stable")
        code = np.zeros(self.content_dimension, dtype=np.float64)
        for index in order[:selected_capacity]:
            if positive_scores[index] <= 0.0:
                break
            code[int(index)] = float(positive_scores[index])
        return code

    def sparse_content(
        self, hidden: Any, *, top_k: int | None = None
    ) -> tuple[tuple[int, ...], tuple[float, ...]]:
        """Return ranked support and coefficients for :meth:`sparse_code`."""

        code = self.sparse_code(hidden, top_k=top_k)
        order = np.argsort(-code, kind="stable")
        support = tuple(int(index) for index in order if code[index] > 0.0)
        coefficients = tuple(float(code[index]) for index in support)
        return support, coefficients

    def reconstruct(self, code: Any) -> np.ndarray:
        """Map a full nonnegative output-content code to residual space."""

        try:
            coefficients = np.asarray(code, dtype=np.float64)
        except (TypeError, ValueError) as error:
            raise ValueError("code must be a finite numeric vector") from error
        if coefficients.shape != (self.content_dimension,):
            raise ValueError("code has the wrong content dimension")
        if not np.all(np.isfinite(coefficients)):
            raise ValueError("code must contain only finite values")
        if np.any(coefficients < 0.0):
            raise ValueError("code must be nonnegative")
        return np.asarray(self.frame_vectors @ coefficients, dtype=np.float64)

    def swap(
        self,
        hidden: Any,
        source: int,
        target: int,
        *,
        magnitude: float | None = None,
    ) -> np.ndarray:
        """Transfer a nonnegative frame coefficient while preserving the cut.

        The component outside the selected subspace is retained exactly.  If
        the requested source has no positive coefficient and no explicit
        magnitude is supplied, the operation is a no-op.
        """

        vector = self._hidden(hidden, allow_batch=False)
        source_index = _nonnegative_integer(source, name="source")
        target_index = _nonnegative_integer(target, name="target")
        if source_index >= self.content_dimension:
            raise ValueError("source is outside the content dimension")
        if target_index >= self.content_dimension:
            raise ValueError("target is outside the content dimension")
        if magnitude is not None:
            transfer = _bounded_float(
                magnitude,
                name="magnitude",
                lower=0.0,
                upper=float(np.finfo(np.float64).max),
                include_upper=True,
            )
        else:
            transfer = -1.0
        if source_index == target_index:
            return vector.copy()

        workspace_component = self.project(vector)
        coefficients = np.maximum(
            self._frame_pseudoinverse @ workspace_component, 0.0
        )
        if magnitude is None:
            transfer = float(coefficients[source_index])
            if transfer <= 64.0 * _FLOAT_EPSILON:
                transfer = float(
                    max(self.logits(workspace_component)[source_index], 0.0)
                )
        if transfer <= 64.0 * _FLOAT_EPSILON:
            return vector.copy()
        coefficients[source_index] = max(
            float(coefficients[source_index]) - transfer, 0.0
        )
        coefficients[target_index] += transfer
        replacement = self.frame_vectors @ coefficients
        return np.asarray(vector - workspace_component + replacement, dtype=np.float64)

    def metrics(
        self, activations: Any, report_targets: Any
    ) -> JacobianFrameMetrics:
        """Measure the frame on a calibration batch."""

        return measure_jacobian_frame(self, activations, report_targets)


def discover_jacobian_frame(
    average_jacobian: Any,
    *,
    rank: int | None = None,
    spectral_threshold: float | None = None,
    top_k: int = 2,
) -> JacobianFrame:
    """Discover a residual-space frame from an average Jacobian SVD.

    Exactly one selection rule is required. ``spectral_threshold`` is a ratio
    to the largest singular value and must lie in ``[0, 1)``.
    """

    jacobian = _finite_array(
        average_jacobian, name="average_jacobian", ndim=2
    )
    selected_rank, threshold = _validate_selection(
        rank,
        spectral_threshold,
        maximum_rank=min(jacobian.shape),
    )
    selected_top_k = _positive_integer(top_k, name="top_k")
    if selected_top_k > jacobian.shape[0]:
        raise ValueError("top_k must not exceed the content dimension")
    _, singular_values, right_vectors = np.linalg.svd(jacobian, full_matrices=False)
    leading = float(singular_values[0])
    if not np.isfinite(leading) or leading <= 0.0:
        raise ValueError("average_jacobian has no nonzero spectral energy")
    numerical_cutoff = (
        _FLOAT_EPSILON * float(max(jacobian.shape)) * leading
    )
    if threshold is not None:
        cutoff = max(threshold * leading, numerical_cutoff)
        selected_rank = int(np.count_nonzero(singular_values > cutoff))
        if selected_rank <= 0:
            raise ValueError("spectral_threshold selects no Jacobian directions")
    if selected_rank is None:  # Kept as a local type guard.
        raise RuntimeError("Jacobian rank selection failed")
    if float(singular_values[selected_rank - 1]) <= numerical_cutoff:
        raise ValueError("rank selects a numerically null Jacobian direction")
    basis = _canonicalize_signs(right_vectors[:selected_rank].T)
    return JacobianFrame(
        average_jacobian=jacobian,
        basis=basis,
        singular_values=singular_values,
        top_k=selected_top_k,
    )


def projector_idempotence_defect(projector: Any) -> float:
    """Return ``||P^2-P||_F / ||P||_F`` for a finite square matrix."""

    matrix = _validate_projector(projector)
    denominator = float(np.linalg.norm(matrix, ord="fro"))
    if denominator <= _FLOAT_EPSILON:
        return 0.0
    return float(np.linalg.norm(matrix @ matrix - matrix, ord="fro") / denominator)


def jacobian_energy_capture(average_jacobian: Any, projector: Any) -> float:
    """Fraction of average-Jacobian Frobenius energy retained by a projector."""

    jacobian = _finite_array(
        average_jacobian, name="average_jacobian", ndim=2
    )
    matrix = _validate_projector(projector, dimension=jacobian.shape[1])
    denominator = float(np.sum(np.square(jacobian)))
    if denominator <= _FLOAT_EPSILON:
        raise ValueError("average_jacobian has no measurable energy")
    value = float(np.sum(np.square(jacobian @ matrix)) / denominator)
    if value < -1e-12 or value > 1.0 + 1e-10:
        raise ValueError("projector expands Jacobian energy outside [0, 1]")
    return float(np.clip(value, 0.0, 1.0))


def activation_variance_fraction(activations: Any, projector: Any) -> float:
    """Fraction of uncentered activation energy retained by a projector.

    This preserves the v0.46 metric convention.  Callers that require centered
    sample variance can center their activation matrix before passing it here.
    """

    hidden = _finite_array(activations, name="activations", ndim=2)
    matrix = _validate_projector(projector, dimension=hidden.shape[1])
    denominator = float(np.sum(np.square(hidden)))
    if denominator <= _FLOAT_EPSILON:
        raise ValueError("activations have no measurable energy")
    value = float(np.sum(np.square(hidden @ matrix)) / denominator)
    if value < -1e-12 or value > 1.0 + 1e-10:
        raise ValueError("projector expands activation energy outside [0, 1]")
    return float(np.clip(value, 0.0, 1.0))


def report_r2(
    average_jacobian: Any,
    activations: Any,
    report_targets: Any,
) -> float:
    """Coefficient of determination for Jacobian-predicted report vectors."""

    jacobian = _finite_array(
        average_jacobian, name="average_jacobian", ndim=2
    )
    hidden = _finite_array(activations, name="activations", ndim=2)
    targets = _finite_array(report_targets, name="report_targets", ndim=2)
    if hidden.shape[1] != jacobian.shape[1]:
        raise ValueError("activations have the wrong residual dimension")
    expected_shape = (hidden.shape[0], jacobian.shape[0])
    if targets.shape != expected_shape:
        raise ValueError(f"report_targets must have shape {expected_shape}")
    predictions = hidden @ jacobian.T
    residual_energy = float(np.sum(np.square(targets - predictions)))
    centered = targets - np.mean(targets, axis=0, keepdims=True)
    total_energy = float(np.sum(np.square(centered)))
    if total_energy <= _FLOAT_EPSILON:
        raise ValueError("report_targets have no measurable variance")
    value = float(1.0 - residual_energy / total_energy)
    return min(value, 1.0)


def measure_jacobian_frame(
    frame: JacobianFrame,
    activations: Any,
    report_targets: Any,
) -> JacobianFrameMetrics:
    """Return all core geometric and calibration metrics for a frame."""

    if not isinstance(frame, JacobianFrame):
        raise ValueError("frame must be a JacobianFrame")
    return JacobianFrameMetrics(
        projector_idempotence_defect=projector_idempotence_defect(frame.projector),
        jacobian_energy_capture=jacobian_energy_capture(
            frame.average_jacobian, frame.projector
        ),
        activation_variance_fraction=activation_variance_fraction(
            activations, frame.projector
        ),
        report_r2=report_r2(
            frame.average_jacobian, activations, report_targets
        ),
    )


class MovingJacobianFrame:
    """EMA-tracked Jacobian frame with stable basis orientation and JSON state."""

    def __init__(
        self,
        initial_jacobian: Any,
        *,
        decay: float,
        rank: int | None = None,
        spectral_threshold: float | None = None,
        top_k: int = 2,
    ) -> None:
        jacobian = _finite_array(
            initial_jacobian, name="initial_jacobian", ndim=2
        )
        self._decay = _bounded_float(
            decay,
            name="decay",
            lower=0.0,
            upper=1.0,
            include_upper=False,
        )
        self._rank, self._spectral_threshold = _validate_selection(
            rank,
            spectral_threshold,
            maximum_rank=min(jacobian.shape),
        )
        self._top_k = _positive_integer(top_k, name="top_k")
        self._frame = discover_jacobian_frame(
            jacobian,
            rank=self._rank,
            spectral_threshold=self._spectral_threshold,
            top_k=self._top_k,
        )
        self._updates = 0

    @property
    def frame(self) -> JacobianFrame:
        return self._frame

    @property
    def decay(self) -> float:
        return self._decay

    @property
    def updates(self) -> int:
        return self._updates

    def update(self, observed_jacobian: Any) -> JacobianFrame:
        """Apply one EMA update and return the newly oriented immutable frame."""

        observation = _finite_array(
            observed_jacobian, name="observed_jacobian", ndim=2
        )
        if observation.shape != self.frame.average_jacobian.shape:
            raise ValueError("observed_jacobian shape changed across EMA updates")
        average = (
            self.decay * self.frame.average_jacobian
            + (1.0 - self.decay) * observation
        )
        discovered = discover_jacobian_frame(
            average,
            rank=self._rank,
            spectral_threshold=self._spectral_threshold,
            top_k=self._top_k,
        )
        aligned_basis = _align_basis(discovered.basis, self.frame.basis)
        updated_frame = JacobianFrame(
            average_jacobian=discovered.average_jacobian,
            basis=aligned_basis,
            singular_values=discovered.singular_values,
            top_k=discovered.top_k,
        )
        self._frame = updated_frame
        self._updates += 1
        return updated_frame

    def state_dict(self) -> dict[str, Any]:
        """Return a JSON-scalarizable state sufficient for exact continuation."""

        return {
            "schema": _STATE_SCHEMA,
            "decay": float(self.decay),
            "rank": None if self._rank is None else int(self._rank),
            "spectral_threshold": (
                None
                if self._spectral_threshold is None
                else float(self._spectral_threshold)
            ),
            "top_k": int(self._top_k),
            "updates": int(self.updates),
            "average_jacobian": self.frame.average_jacobian.tolist(),
            "basis": self.frame.basis.tolist(),
            "singular_values": self.frame.singular_values.tolist(),
        }

    @staticmethod
    def _validated_state(
        state: Mapping[str, Any],
    ) -> tuple[float, int | None, float | None, int, int, JacobianFrame]:
        if not isinstance(state, Mapping):
            raise ValueError("state must be a mapping")
        expected_keys = {
            "schema",
            "decay",
            "rank",
            "spectral_threshold",
            "top_k",
            "updates",
            "average_jacobian",
            "basis",
            "singular_values",
        }
        if set(state) != expected_keys:
            raise ValueError("state keys do not match the moving-frame schema")
        if state["schema"] != _STATE_SCHEMA:
            raise ValueError("unsupported moving-frame state schema")
        average = _finite_array(
            state["average_jacobian"], name="average_jacobian", ndim=2
        )
        decay = _bounded_float(
            state["decay"],
            name="decay",
            lower=0.0,
            upper=1.0,
            include_upper=False,
        )
        rank, threshold = _validate_selection(
            state["rank"],
            state["spectral_threshold"],
            maximum_rank=min(average.shape),
        )
        top_k = _positive_integer(state["top_k"], name="top_k")
        updates = _nonnegative_integer(state["updates"], name="updates")
        reference = discover_jacobian_frame(
            average,
            rank=rank,
            spectral_threshold=threshold,
            top_k=top_k,
        )
        frame = JacobianFrame(
            average_jacobian=average,
            basis=state["basis"],
            singular_values=state["singular_values"],
            top_k=top_k,
        )
        if frame.rank != reference.rank:
            raise ValueError("state basis rank disagrees with its selection rule")
        if not np.allclose(
            frame.singular_values,
            reference.singular_values,
            rtol=1e-12,
            atol=1e-15,
        ):
            raise ValueError("state singular values disagree with its Jacobian")
        if not np.allclose(
            frame.projector,
            reference.projector,
            rtol=0.0,
            atol=1e-9,
        ):
            raise ValueError("state basis does not span the discovered subspace")
        return decay, rank, threshold, top_k, updates, frame

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        """Atomically restore a state produced by :meth:`state_dict`."""

        decay, rank, threshold, top_k, updates, frame = self._validated_state(state)
        self._decay = decay
        self._rank = rank
        self._spectral_threshold = threshold
        self._top_k = top_k
        self._updates = updates
        self._frame = frame

    @classmethod
    def from_state_dict(cls, state: Mapping[str, Any]) -> MovingJacobianFrame:
        """Construct and validate a moving frame from serialized JSON state."""

        decay, rank, threshold, top_k, _, frame = cls._validated_state(state)
        result = cls(
            frame.average_jacobian,
            decay=decay,
            rank=rank,
            spectral_threshold=threshold,
            top_k=top_k,
        )
        result.load_state_dict(state)
        return result
