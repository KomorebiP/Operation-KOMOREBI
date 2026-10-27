"""Piecewise-local engineering diagnostics for RRCT state transitions.

The state slice used here concatenates specialist states, workspace state,
self-model state, and the previous action.  Episodic-memory contents and ring
metadata, predictor caches, time, current resolution, component parameters,
and categorical branch choices are deliberately excluded.  Continuous
perturbation pairs begin with all excluded state held fixed, while differences
in their resulting specialist selection, next resolution, memory retrieval,
memory-write decision, and action-candidate selection are recorded explicitly.
The resulting Jacobian therefore describes one continuous slice of the
one-step transition, not the complete hybrid system.

These diagnostics are not Lyapunov exponents and provide no evidence for or
against consciousness.  They are ordinary numerical tools for testing local
gain, contraction, and sensitivity in a piecewise-defined architecture.  A
stopped or nonfinite computation raises
:class:`LocalTransitionComputationError` with its raw partial artifact intact.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .agent import RRCTAgent, StepResult


FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class HybridBranchSignature:
    """Immutable record of every audited discrete one-step choice.

    Tuple order is semantically meaningful for selected specialists and memory
    retrieval because both record deterministic ranked selections.  The action
    index is the controller candidate selected by its first-maximum ``argmax``
    rule, not an inference from the resulting continuous action vector.
    """

    selected_specialists: tuple[str, ...]
    action_candidate_index: int
    next_resolution_level: int
    memory_indices: tuple[int, ...]
    memory_written: bool

    def __post_init__(self) -> None:
        if isinstance(self.selected_specialists, (str, bytes)):
            raise TypeError("selected_specialists must be a sequence of names")
        selected = tuple(self.selected_specialists)
        if any(not isinstance(name, str) or not name for name in selected):
            raise TypeError("selected specialist names must be nonempty strings")
        if len(selected) != len(set(selected)):
            raise ValueError("selected specialist names must be unique")
        object.__setattr__(self, "selected_specialists", selected)

        for name in ("action_candidate_index", "next_resolution_level"):
            value = getattr(self, name)
            if (
                isinstance(value, (bool, np.bool_))
                or not isinstance(value, (int, np.integer))
                or int(value) < 0
            ):
                raise TypeError(f"{name} must be a nonnegative integer")
            object.__setattr__(self, name, int(value))

        if isinstance(self.memory_indices, (str, bytes)):
            raise TypeError("memory_indices must be a sequence of indices")
        memory_indices = tuple(self.memory_indices)
        if any(
            isinstance(index, (bool, np.bool_))
            or not isinstance(index, (int, np.integer))
            or int(index) < 0
            for index in memory_indices
        ):
            raise TypeError("memory indices must be nonnegative integers")
        memory_indices = tuple(int(index) for index in memory_indices)
        if len(memory_indices) != len(set(memory_indices)):
            raise ValueError("memory indices must be unique")
        object.__setattr__(self, "memory_indices", memory_indices)

        if not isinstance(self.memory_written, (bool, np.bool_)):
            raise TypeError("memory_written must be boolean")
        object.__setattr__(self, "memory_written", bool(self.memory_written))


class LocalTransitionComputationError(ValueError):
    """Failure with the raw finite-difference artifact retained for audit.

    ``jacobian`` always has the complete intended square shape.  It is
    initialized with NaN, so columns that were never completed remain explicit
    rather than being confused with computed zeros.  Paired branch signatures
    are retained for exactly the first ``completed_columns`` coordinates.
    Arrays and signature collections exposed by this exception are immutable.
    """

    def __init__(
        self,
        *,
        jacobian: ArrayLike,
        completed_columns: int,
        epsilon: float,
        state_dimension: int,
        positive_branch_signatures: tuple[HybridBranchSignature, ...],
        negative_branch_signatures: tuple[HybridBranchSignature, ...],
        stage: str,
        reason: str,
    ) -> None:
        dimension = int(state_dimension)
        if dimension <= 0 or dimension != state_dimension:
            raise ValueError("state_dimension must be a positive integer")
        matrix = np.asarray(jacobian, dtype=np.float64)
        if matrix.shape != (dimension, dimension):
            raise ValueError(
                "jacobian must have shape " f"({dimension}, {dimension})"
            )

        completed = int(completed_columns)
        if (
            completed != completed_columns
            or completed < 0
            or completed > dimension
        ):
            raise ValueError("completed_columns must lie in [0, state_dimension]")
        if completed < dimension and not np.all(np.isnan(matrix[:, completed:])):
            raise ValueError(
                "uncompleted Jacobian columns must remain explicitly NaN"
            )

        positive = tuple(positive_branch_signatures)
        negative = tuple(negative_branch_signatures)
        if len(positive) != completed or len(negative) != completed:
            raise ValueError(
                "retained branch signature counts must equal completed_columns"
            )
        if any(
            not isinstance(signature, HybridBranchSignature)
            for signature in positive + negative
        ):
            raise TypeError(
                "branch signature entries must be HybridBranchSignature instances"
            )

        parsed_epsilon = float(epsilon)
        if not np.isfinite(parsed_epsilon) or parsed_epsilon <= 0.0:
            raise ValueError("epsilon must be finite and positive")
        if not isinstance(stage, str) or not stage:
            raise TypeError("stage must be a nonempty string")
        if not isinstance(reason, str) or not reason:
            raise TypeError("reason must be a nonempty string")

        immutable_matrix = np.frombuffer(
            np.ascontiguousarray(matrix).tobytes(), dtype=np.float64
        ).reshape(matrix.shape)
        self._jacobian = immutable_matrix
        self._completed_columns = completed
        self._epsilon = parsed_epsilon
        self._state_dimension = dimension
        self._positive_branch_signatures = positive
        self._negative_branch_signatures = negative
        self._stage = stage
        self._reason = reason
        super().__init__(f"local transition computation failed at {stage}: {reason}")

    @property
    def jacobian(self) -> FloatArray:
        """Raw immutable matrix, with NaN in every uncompleted column."""

        return self._jacobian

    @property
    def completed_columns(self) -> int:
        """Number of fully computed finite-difference columns."""

        return self._completed_columns

    @property
    def epsilon(self) -> float:
        """Absolute centered finite-difference displacement."""

        return self._epsilon

    @property
    def state_dimension(self) -> int:
        """Intended square state dimension of ``jacobian``."""

        return self._state_dimension

    @property
    def positive_branch_signatures(self) -> tuple[HybridBranchSignature, ...]:
        """Positive-perturbation signatures for completed coordinates."""

        return self._positive_branch_signatures

    @property
    def negative_branch_signatures(self) -> tuple[HybridBranchSignature, ...]:
        """Negative-perturbation signatures for completed coordinates."""

        return self._negative_branch_signatures

    @property
    def stage(self) -> str:
        """Named computation stage at which execution stopped."""

        return self._stage

    @property
    def reason(self) -> str:
        """Human-readable exception type and message or validation failure."""

        return self._reason


@dataclass(frozen=True)
class LocalTransitionDiagnostics:
    """Centered finite-difference summary of a frozen one-step transition.

    ``branch_switch_fraction`` is the fraction of state coordinates for which
    the positive and negative perturbations differ in selected specialists,
    next resolution, retrieved memory indices, whether memory was written, or
    the selected action-candidate index.  The last is reconstructed by the
    controller's deterministic ``argmax`` rule over ``action_scores``.
    ``positive_branch_signatures`` and ``negative_branch_signatures`` preserve
    the actual paired outcomes for every finite-difference coordinate.
    ``branch_switch_coordinates`` is exactly the set of positions where those
    signatures differ.  A nonzero fraction warns that portions of the reported
    matrix cross discrete branches and should not be read as a derivative of
    one smooth map.
    """

    jacobian: FloatArray
    spectral_radius: float
    largest_singular_value: float
    branch_switch_fraction: float
    branch_switch_count: int
    branch_switch_coordinates: tuple[int, ...]
    positive_branch_signatures: tuple[HybridBranchSignature, ...]
    negative_branch_signatures: tuple[HybridBranchSignature, ...]
    epsilon: float
    state_dimension: int

    def __post_init__(self) -> None:
        matrix = np.asarray(self.jacobian, dtype=np.float64)
        dimension = int(self.state_dimension)
        if dimension <= 0 or dimension != self.state_dimension:
            raise ValueError("state_dimension must be a positive integer")
        if matrix.shape != (dimension, dimension):
            raise ValueError(
                "jacobian must have shape " f"({dimension}, {dimension})"
            )
        if not np.all(np.isfinite(matrix)):
            raise ValueError("jacobian must contain only finite values")
        immutable = np.frombuffer(
            np.ascontiguousarray(matrix).tobytes(), dtype=np.float64
        ).reshape(matrix.shape)
        object.__setattr__(self, "jacobian", immutable)
        object.__setattr__(self, "state_dimension", dimension)

        for name in ("spectral_radius", "largest_singular_value"):
            value = float(getattr(self, name))
            if not np.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
            object.__setattr__(self, name, value)

        branch_fraction = float(self.branch_switch_fraction)
        if (
            not np.isfinite(branch_fraction)
            or branch_fraction < 0.0
            or branch_fraction > 1.0
        ):
            raise ValueError("branch_switch_fraction must lie in [0, 1]")
        object.__setattr__(self, "branch_switch_fraction", branch_fraction)

        positive_signatures = tuple(self.positive_branch_signatures)
        negative_signatures = tuple(self.negative_branch_signatures)
        if (
            len(positive_signatures) != dimension
            or len(negative_signatures) != dimension
        ):
            raise ValueError(
                "positive and negative branch signatures must each have "
                "state_dimension entries"
            )
        if any(
            not isinstance(signature, HybridBranchSignature)
            for signature in positive_signatures + negative_signatures
        ):
            raise TypeError(
                "branch signature entries must be HybridBranchSignature instances"
            )
        object.__setattr__(
            self, "positive_branch_signatures", positive_signatures
        )
        object.__setattr__(
            self, "negative_branch_signatures", negative_signatures
        )

        branch_coordinates = tuple(
            int(coordinate) for coordinate in self.branch_switch_coordinates
        )
        if (
            branch_coordinates != tuple(sorted(set(branch_coordinates)))
            or any(
                coordinate < 0 or coordinate >= dimension
                for coordinate in branch_coordinates
            )
        ):
            raise ValueError(
                "branch_switch_coordinates must be sorted, unique, and valid"
            )
        expected_branch_coordinates = tuple(
            coordinate
            for coordinate, (positive, negative) in enumerate(
                zip(positive_signatures, negative_signatures, strict=True)
            )
            if positive != negative
        )
        if branch_coordinates != expected_branch_coordinates:
            raise ValueError(
                "branch_switch_coordinates must exactly identify unequal "
                "positive and negative branch signatures"
            )
        branch_count = int(self.branch_switch_count)
        if (
            branch_count != self.branch_switch_count
            or branch_count != len(branch_coordinates)
        ):
            raise ValueError(
                "branch_switch_count must equal branch_switch_coordinates length"
            )
        expected_fraction = branch_count / dimension
        if branch_fraction != expected_fraction:
            raise ValueError(
                "branch_switch_fraction must equal branch_switch_count / "
                "state_dimension"
            )
        object.__setattr__(self, "branch_switch_count", branch_count)
        object.__setattr__(
            self, "branch_switch_coordinates", branch_coordinates
        )

        epsilon = float(self.epsilon)
        if not np.isfinite(epsilon) or epsilon <= 0.0:
            raise ValueError("epsilon must be finite and positive")
        object.__setattr__(self, "epsilon", epsilon)


def _require_agent(agent: RRCTAgent) -> None:
    if not isinstance(agent, RRCTAgent):
        raise TypeError("agent must be an RRCTAgent")


def _hybrid_branch_signature(
    result: StepResult,
) -> HybridBranchSignature:
    """Return every discrete one-step choice audited by the Jacobian.

    ``CounterfactualController.choose`` selects the action candidate with
    NumPy's deterministic first-maximum ``argmax`` rule but ``StepResult``
    stores the score vector rather than the index.  Reconstructing that index
    here ensures an action branch flip cannot be hidden merely because two
    candidates happen to emit numerically similar continuous actions.
    """

    action_scores = np.asarray(result.action_scores, dtype=np.float64)
    if (
        action_scores.ndim != 1
        or action_scores.size == 0
        or not np.all(np.isfinite(action_scores))
    ):
        raise ValueError("action_scores must be a nonempty finite vector")
    return HybridBranchSignature(
        selected_specialists=result.selected_specialists,
        action_candidate_index=int(np.argmax(action_scores)),
        next_resolution_level=result.next_resolution_level,
        memory_indices=result.memory_indices,
        memory_written=result.memory_written,
    )


def continuous_state_vector(agent: RRCTAgent) -> FloatArray:
    """Flatten the continuous state slice used by the local diagnostic.

    The returned vector is an independent copy ordered as all specialist
    states in declaration order, workspace state, self-model state, and last
    action.  See the module documentation for intentionally excluded state.
    """

    _require_agent(agent)
    vector = np.concatenate(
        (
            *(specialist.state for specialist in agent.specialists),
            agent.workspace.state,
            agent.self_model.state,
            agent._last_action,
        )
    ).astype(np.float64, copy=False)
    if not np.all(np.isfinite(vector)):
        raise ValueError("agent continuous state must contain only finite values")
    return vector.copy()


def set_continuous_state_vector(
    agent: RRCTAgent,
    state: ArrayLike,
) -> None:
    """Set exactly the continuous state slice used by the local diagnostic.

    This deliberately leaves memory, predictor caches, time, resolution, and
    parameters unchanged.  The most recent :class:`~rrct.agent.StepResult` is
    cleared because it no longer describes the mutated state.
    """

    _require_agent(agent)
    vector = np.asarray(state, dtype=np.float64)
    expected = (
        agent.n_specialists * agent.specialist_dim
        + agent.workspace_dim
        + agent.self_dim
        + agent.action_dim
    )
    if vector.shape != (expected,):
        raise ValueError(f"state must have shape ({expected},), got {vector.shape}")
    if not np.all(np.isfinite(vector)):
        raise ValueError("state must contain only finite values")

    offset = 0
    for specialist in agent.specialists:
        end = offset + agent.specialist_dim
        specialist.state = vector[offset:end].copy()
        offset = end
    end = offset + agent.workspace_dim
    agent.workspace.state = vector[offset:end].copy()
    offset = end
    end = offset + agent.self_dim
    agent.self_model.state = vector[offset:end].copy()
    offset = end
    agent._last_action = vector[offset:].copy()
    agent._last_result = None


def local_transition_jacobian(
    agent: RRCTAgent,
    observation: ArrayLike,
    *,
    epsilon: float = 1e-5,
) -> LocalTransitionDiagnostics:
    """Estimate a centered one-step Jacobian around a frozen RRCT agent.

    Every Jacobian column advances two independent deep copies of ``agent``
    from ``x + epsilon*e_i`` and ``x - epsilon*e_i`` under the same fixed
    observation.  Online predictor training is refused because paired calls
    would otherwise estimate a parameter-updating map rather than a frozen
    state transition.

    The returned spectral radius and largest singular value are descriptive
    summaries of this finite-difference matrix.  Specialist selection, next
    resolution, memory indices, memory writing, and the deterministic argmax
    action-candidate index form the audited hybrid branch signature.  Any
    paired difference is separately exposed by ``branch_switch_fraction`` and
    the corresponding count and state coordinates.  If a coordinate, matrix
    validation, eigendecomposition, or SVD stage fails, the raised
    :class:`LocalTransitionComputationError` retains the NaN-initialized raw
    matrix and every completed branch-signature pair.
    """

    _require_agent(agent)
    if agent.self_model_mode != "frozen":
        raise ValueError("local transition diagnostics require a frozen self-model")
    if agent.feedback_mode == "adaptive" and not agent.ablations.feedback_adaptation:
        raise ValueError(
            "local transition diagnostics do not yet include adaptive feedback state"
        )
    epsilon = float(epsilon)
    if not np.isfinite(epsilon) or epsilon <= 0.0:
        raise ValueError("epsilon must be finite and positive")
    fixed_observation = np.asarray(observation, dtype=np.float64)
    if fixed_observation.shape != (agent.observation_dim,):
        raise ValueError(
            "observation must have shape "
            f"({agent.observation_dim},), got {fixed_observation.shape}"
        )
    if not np.all(np.isfinite(fixed_observation)):
        raise ValueError("observation must contain only finite values")

    base_state = continuous_state_vector(agent)
    dimension = int(base_state.size)
    # NaN is the explicit marker for a column that was never completed.  If
    # any later stage stops, this same raw matrix is retained on the public
    # computation error instead of being discarded.
    jacobian = np.full((dimension, dimension), np.nan, dtype=np.float64)
    branch_switch_coordinates: list[int] = []
    positive_branch_signatures: list[HybridBranchSignature] = []
    negative_branch_signatures: list[HybridBranchSignature] = []

    for coordinate in range(dimension):
        try:
            positive_state = base_state.copy()
            negative_state = base_state.copy()
            positive_state[coordinate] += epsilon
            negative_state[coordinate] -= epsilon

            positive_agent = copy.deepcopy(agent)
            negative_agent = copy.deepcopy(agent)
            set_continuous_state_vector(positive_agent, positive_state)
            set_continuous_state_vector(negative_agent, negative_state)
            positive_result = positive_agent.step(fixed_observation)
            negative_result = negative_agent.step(fixed_observation)
            positive_next = continuous_state_vector(positive_agent)
            negative_next = continuous_state_vector(negative_agent)
            column = (positive_next - negative_next) / (2.0 * epsilon)
            positive_signature = _hybrid_branch_signature(positive_result)
            negative_signature = _hybrid_branch_signature(negative_result)
        except Exception as error:
            reason = f"column {coordinate}: {type(error).__name__}: {error}"
            raise LocalTransitionComputationError(
                jacobian=jacobian,
                completed_columns=coordinate,
                epsilon=epsilon,
                state_dimension=dimension,
                positive_branch_signatures=tuple(positive_branch_signatures),
                negative_branch_signatures=tuple(negative_branch_signatures),
                stage="finite_difference",
                reason=reason,
            ) from error

        # Commit a column and its paired branch records atomically only after
        # every operation for that coordinate succeeds.
        jacobian[:, coordinate] = column
        positive_branch_signatures.append(positive_signature)
        negative_branch_signatures.append(negative_signature)
        if positive_signature != negative_signature:
            branch_switch_coordinates.append(coordinate)

    if not np.all(np.isfinite(jacobian)):
        raise LocalTransitionComputationError(
            jacobian=jacobian,
            completed_columns=dimension,
            epsilon=epsilon,
            state_dimension=dimension,
            positive_branch_signatures=tuple(positive_branch_signatures),
            negative_branch_signatures=tuple(negative_branch_signatures),
            stage="nonfinite_jacobian",
            reason="finite differences produced a nonfinite Jacobian",
        )
    try:
        eigenvalues = np.linalg.eigvals(jacobian)
        if not np.all(np.isfinite(eigenvalues)):
            raise ValueError("eigendecomposition returned nonfinite eigenvalues")
        spectral_radius = float(np.max(np.abs(eigenvalues)))
    except Exception as error:
        reason = f"{type(error).__name__}: {error}"
        raise LocalTransitionComputationError(
            jacobian=jacobian,
            completed_columns=dimension,
            epsilon=epsilon,
            state_dimension=dimension,
            positive_branch_signatures=tuple(positive_branch_signatures),
            negative_branch_signatures=tuple(negative_branch_signatures),
            stage="eigvals",
            reason=reason,
        ) from error
    try:
        singular_values = np.linalg.svd(jacobian, compute_uv=False)
        if singular_values.size == 0 or not np.all(np.isfinite(singular_values)):
            raise ValueError("SVD returned empty or nonfinite singular values")
        largest_singular_value = float(singular_values[0])
    except Exception as error:
        reason = f"{type(error).__name__}: {error}"
        raise LocalTransitionComputationError(
            jacobian=jacobian,
            completed_columns=dimension,
            epsilon=epsilon,
            state_dimension=dimension,
            positive_branch_signatures=tuple(positive_branch_signatures),
            negative_branch_signatures=tuple(negative_branch_signatures),
            stage="svd",
            reason=reason,
        ) from error
    return LocalTransitionDiagnostics(
        jacobian=jacobian,
        spectral_radius=spectral_radius,
        largest_singular_value=largest_singular_value,
        branch_switch_fraction=len(branch_switch_coordinates) / dimension,
        branch_switch_count=len(branch_switch_coordinates),
        branch_switch_coordinates=tuple(branch_switch_coordinates),
        positive_branch_signatures=tuple(positive_branch_signatures),
        negative_branch_signatures=tuple(negative_branch_signatures),
        epsilon=epsilon,
        state_dimension=dimension,
    )


__all__ = [
    "FloatArray",
    "HybridBranchSignature",
    "LocalTransitionComputationError",
    "LocalTransitionDiagnostics",
    "continuous_state_vector",
    "local_transition_jacobian",
    "set_continuous_state_vector",
]
