"""Integrated Recursive Resolution Closure research agent.

The implementation is a falsifiable architectural prototype, not a detector
or proof of phenomenal consciousness.  It exposes every proposed causal link,
supports named ablations, and accepts explicit workspace interventions so the
full loop can be compared with matched controls.
"""

from __future__ import annotations

import copy
import hashlib
import pickle
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field, fields, replace
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .components import (
    BayesianCausalTransferModel,
    CounterfactualController,
    EpisodicMemory,
    GlobalWorkspace,
    MemoryRead,
    NonValencedSelfModel,
    NonValencedObservationForecaster,
    SpecialistModule,
    SpecialistOutput,
    balanced_matrix,
)
from .causal_boundary import (
    BoundCausalTransition,
    CausalAccessPrediction,
    CausalBoundaryConfig,
    CausalBoundaryState,
    CausalBoundaryUpdateReceipt,
    CausalHandleCommitment,
    DirectCausalAccessReadout,
    OnlineCausalAccessMemoryReadout,
    OnlineCausalAccessReadout,
    OnlineCausalSelfBoundary,
)
from .feedback import (
    AdaptiveFeedbackRegulator,
    FeedbackControlRecord,
    FeedbackTelemetry,
    compute_feedback_telemetry,
)
from .projectors import NestedOrthogonalProjectors


FloatArray = NDArray[np.float64]


def _causal_projection_digest(value: ArrayLike) -> str:
    """Bind a causal-path snapshot to one exact native projection."""

    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    digest = hashlib.sha256()
    digest.update(b"rrct.causal_boundary_projection.v1\0")
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(str(tuple(int(item) for item in array.shape)).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


@dataclass(frozen=True)
class AblationFlags:
    """Named causal ablations, where ``True`` means the link is disabled."""

    recurrence: bool = False
    self_model: bool = False
    broadcast: bool = False
    memory: bool = False
    resolution: bool = False
    feedback_adaptation: bool = False
    causal_boundary_broadcast: bool = False

    @classmethod
    def parse(
        cls,
        value: "AblationFlags | str | Iterable[str] | Mapping[str, bool] | None",
    ) -> "AblationFlags":
        """Parse flags from an instance, names, or a boolean mapping.

        Strings may contain comma-separated names.  In a mapping, a true value
        means that component is ablated.  Unknown names raise ``ValueError`` so
        experimental controls cannot silently misspell an ablation.
        """

        if value is None:
            return cls()
        if isinstance(value, cls):
            return value
        known = {field.name for field in fields(cls)}
        if isinstance(value, Mapping):
            unknown = set(value) - known
            if unknown:
                raise ValueError(f"unknown ablation(s): {sorted(unknown)}")
            options = {name: bool(value.get(name, False)) for name in known}
            return cls(**options)
        if isinstance(value, str):
            names = {name.strip() for name in value.split(",") if name.strip()}
        else:
            names = {str(name) for name in value}
        unknown = names - known
        if unknown:
            raise ValueError(f"unknown ablation(s): {sorted(unknown)}")
        return cls(**{name: name in names for name in known})

    @property
    def disabled(self) -> tuple[str, ...]:
        """Return disabled link names in stable declaration order."""

        return tuple(field.name for field in fields(self) if getattr(self, field.name))

    def enabled(self, name: str) -> bool:
        """Return whether a named link is active."""

        if name not in {field.name for field in fields(self)}:
            raise ValueError(f"unknown ablation: {name}")
        return not bool(getattr(self, name))


@dataclass(frozen=True)
class StepResult:
    """Immutable-by-convention record of one integrated causal step."""

    time: int
    source: str
    observation: FloatArray
    resolved: FloatArray
    resolution_level: int
    next_resolution_level: int
    resolution_rank: int
    next_resolution_rank: int
    detail_norms: FloatArray
    specialist_states: FloatArray
    specialist_salience: FloatArray
    workspace_proposal_states: FloatArray
    workspace_weights: FloatArray
    workspace: FloatArray
    selected_specialists: tuple[str, ...]
    self_state: FloatArray
    memory_read: FloatArray
    memory_indices: tuple[int, ...]
    memory_written: bool
    predicted_workspace: FloatArray
    prediction_error: FloatArray
    error_norm: float
    action: FloatArray
    action_scores: FloatArray
    resolution_scores: FloatArray
    ablations: tuple[str, ...]
    applied_recurrent_gain: float
    applied_closure_gain: float
    next_recurrent_gain: float
    next_closure_gain: float
    feedback_telemetry: FeedbackTelemetry | None
    causal_boundary_state: CausalBoundaryState | None
    causal_boundary_descriptor: FloatArray
    causal_boundary_proposal_state: FloatArray
    causal_boundary_workspace_drive: FloatArray
    causal_boundary_candidate_signal: FloatArray
    causal_commitment_digest: str | None
    causal_transition_digest: str | None
    causal_boundary_update_receipt: CausalBoundaryUpdateReceipt | None
    causal_public_pair: tuple[int, int] | None
    causal_commitment: CausalHandleCommitment | None
    causal_boundary_proposal_selected: bool
    causal_access_confidence: float
    causal_access_updated: bool
    causal_access_update_count: int
    causal_interrupted_transitions: int

    def feature_vector(self) -> FloatArray:
        """Return a compact representation suitable for an external readout."""

        return np.concatenate(
            (
                self.workspace,
                self.self_state,
                self.memory_read,
                self.action,
                np.asarray(
                    [
                        self.error_norm,
                        float(self.resolution_level),
                        float(self.next_resolution_level),
                    ],
                    dtype=np.float64,
                ),
            )
        )

    def causal_feature_vector(self) -> FloatArray:
        """Return the ordinary features plus the live boundary broadcast.

        The historical :meth:`feature_vector` remains byte-compatible with
        earlier releases.  This explicit extension is available only when a
        caller intentionally includes the v0.29 causal-boundary pathway.
        """

        return np.concatenate(
            (
                self.feature_vector(),
                self.causal_boundary_descriptor,
                self.causal_boundary_workspace_drive,
            )
        )

    def causal_nodes(self) -> FloatArray:
        """Return padded specialist/workspace/self/memory node states.

        Rows are nodes and columns are features.  This is convenient for
        intervention-based causal-adjacency metrics without imposing a common
        latent dimension on the components themselves.
        """

        node_vectors = [row for row in self.specialist_states]
        node_vectors.extend((self.workspace, self.self_state, self.memory_read))
        width = max(vector.size for vector in node_vectors)
        matrix = np.zeros((len(node_vectors), width), dtype=np.float64)
        for index, vector in enumerate(node_vectors):
            matrix[index, : vector.size] = vector
        return matrix


@dataclass(frozen=True)
class SelfCounterfactualQuery:
    """Paired prospective trajectories for a queried change to self-state."""

    self_delta: FloatArray
    baseline_workspace: FloatArray
    intervened_workspace: FloatArray
    workspace_delta: FloatArray
    baseline_actions: FloatArray
    intervened_actions: FloatArray
    action_delta: FloatArray
    baseline_resolutions: tuple[int, ...]
    intervened_resolutions: tuple[int, ...]
    baseline_self_states: FloatArray
    intervened_self_states: FloatArray
    baseline_prediction_errors: FloatArray
    intervened_prediction_errors: FloatArray

    @property
    def response_norm(self) -> float:
        return float(np.linalg.norm(self.workspace_delta))

    @property
    def action_response_norm(self) -> float:
        return float(np.linalg.norm(self.action_delta))

    @property
    def joint_response_norm(self) -> float:
        return float(np.sqrt(self.response_norm**2 + self.action_response_norm**2))


@dataclass(frozen=True)
class SelfDirectedPlan:
    """A selected self-counterfactual and its realized live trajectory."""

    selected_index: int
    predicted_scores: tuple[float, ...]
    predicted_score: float
    realized_score: float
    prediction_error: float
    query: SelfCounterfactualQuery
    realized_steps: tuple[StepResult, ...]


@dataclass(frozen=True)
class EndogenousSelfIntention:
    """Internally generated, bounded, nonvalenced self-regulation decision."""

    candidate_count: int
    queried_count: int
    queried_indices: tuple[int, ...]
    selected_index: int
    selected_delta: FloatArray
    predicted_candidate_errors: tuple[float, ...]
    predicted_baseline_error: float
    predicted_selected_error: float
    realized_baseline_error: float
    realized_selected_error: float
    realized_improvement: float
    prediction_error: float
    forecast_observations: FloatArray
    realized_steps: tuple[StepResult, ...]


@dataclass(frozen=True)
class EndogenousSelfPlan:
    """Pure precommit plan generated without access to a realized future."""

    state_digest: str
    candidate_deltas: FloatArray
    proxy_scores: FloatArray
    queried_indices: tuple[int, ...]
    selected_index: int
    raw_selected_index: int
    selected_delta: FloatArray
    predicted_candidate_errors: tuple[float, ...]
    predicted_baseline_error: float
    predicted_selected_error: float
    forecast_observations: FloatArray
    forecast_mode: str
    horizon: int
    calibration_mode: str
    calibration_key: str
    calibration_digest: str
    calibration_count: int
    calibration_ready: bool
    calibration_alpha: float
    calibration_min_samples: int
    minimum_effect: float
    uncertainty_threshold: float | None
    conservative_lower_bound: float | None
    raw_predicted_improvement: float
    predicted_improvement: float
    abstained: bool
    abstention_reason: str | None
    selection_mode: str
    simulator_selected_index: int
    bayesian_confidence: float
    bayesian_transfer_key: str
    bayesian_model_digest: str
    bayesian_observation_count: int
    bayesian_effective_sample_count: float
    bayesian_features: FloatArray
    bayesian_means: tuple[float, ...]
    bayesian_standard_deviations: tuple[float, ...]
    bayesian_probabilities_positive: tuple[float, ...]
    bayesian_lower_bounds: tuple[float, ...]
    plan_content_digest: str
    queries: tuple[SelfCounterfactualQuery, ...]


@dataclass(frozen=True)
class EndogenousCommitReceipt:
    """Atomic commitment receipt used to guard held-out evaluation."""

    plan: EndogenousSelfPlan
    precommit_state_digest: str
    postcommit_state_digest: str
    committed_time: int
    _baseline_agent: Any = field(repr=False, compare=False)


@dataclass(frozen=True)
class IntentionCalibrationRecord:
    """Auditable forecast-to-outcome record for one intention episode."""

    sequence_id: int
    calibration_key: str
    plan_state_digest: str
    planned_time: int
    recorded_time: int
    predicted_improvement: float
    realized_improvement: float
    optimism: float
    selected_index: int
    selected_delta_norm: float
    horizon: int
    forecast_mode: str
    outcome_source: str


@dataclass(frozen=True)
class BayesianTransferUpdate:
    """Audit receipt for one post-reveal generalized-Bayes update."""

    sequence_id: int
    transfer_key: str
    evidence_digest: str
    planned_time: int | None
    recorded_time: int | None
    feature_episode_index: int | None
    target_episode_index: int | None
    target_candidate_indices: tuple[int, ...]
    permutation_digest: str | None
    candidate_indices: tuple[int, ...]
    normalized_targets: tuple[float, ...]
    per_candidate_weight: float
    observation_count_before: int
    observation_count_after: int
    effective_sample_count_before: float
    effective_sample_count_after: float
    posterior_digest_before: str
    posterior_digest_after: str
    outcome_source: str


class RRCTAgent:
    """A deterministic Recursive Resolution Closure architecture.

    Parameters
    ----------
    observation_dim:
        Fixed dimension of every observation vector.
    action_dim:
        Dimension of the controller's continuous action vector.
    n_levels, projector_ranks:
        Resolution filtration.  Explicit ranks override automatic levels and
        must end at ``observation_dim``.
    n_specialists, specialist_dim:
        Number and latent width of local detail-band processors.
    workspace_dim, workspace_capacity:
        Width and proposal capacity of global broadcast.
    self_dim:
        Width of the nonvalenced causal self-model.
    memory_capacity:
        Maximum number of episodic workspace states.
    seed:
        Master seed.  Every component receives an independently spawned child
        seed, so identical configurations and seeds produce identical traces.
    recurrent_gain:
        Continuous gain on temporal recurrent drives and residual carry.  Zero
        is exactly memoryless and one recovers the original recurrence scale.
    closure_gain:
        Shared master gain on prior self-state and action feedback into the
        workspace.
    self_feedback_gain, action_feedback_gain:
        Nonnegative path-specific multipliers on the self-to-workspace and
        action-to-workspace feedback paths.  Both default to one, exactly
        recovering the original shared-gain configuration.
    self_model_mode:
        ``"train"`` enables normalized-LMS self-prediction updates;
        ``"frozen"`` retains parameters without updating them.
    feedback_mode:
        ``"fixed"`` preserves the configured gains exactly, ``"adaptive"``
        applies bounded next-step feedback regulation, and ``"manual"``
        accepts an explicit bounded gain schedule for matched controls.
    causal_boundary_config:
        Optional label-free online causal-boundary learner. ``None`` preserves
        the historical execution path exactly.
    causal_boundary_broadcast_gain:
        Nonnegative gain on the learner-owned descriptor entering the native
        workspace path.
    ablations:
        A set of names, comma-separated string, boolean mapping, or
        :class:`AblationFlags`.  True/named means disabled.
    """

    BAYESIAN_TRANSFER_FEATURE_NAMES = (
        "current_prediction_error_load",
        "current_workspace_load",
        "current_self_state_load",
        "forecaster_residual_load",
        "candidate_activity",
        "self_state_alignment",
        "normalized_proxy_score",
        "forecast_baseline_error",
        "mean_predicted_benefit",
        "minimum_predicted_benefit",
        "final_predicted_benefit",
        "predicted_benefit_trend",
        "predicted_benefit_dispersion",
        "workspace_response",
        "action_response",
        "self_state_response",
        "resolution_divergence",
        "forecast_amplitude",
        "forecast_roughness",
        "forecast_departure",
    )
    BAYESIAN_TRANSFER_PRIOR_PRECISION = 1.0
    BAYESIAN_TRANSFER_PRIOR_SHAPE = 2.0
    BAYESIAN_TRANSFER_PRIOR_SCALE = 1e-4
    FEEDBACK_SNAPSHOT_SCHEMA = "rrct.agent_feedback.v1"
    CAUSAL_BOUNDARY_SNAPSHOT_SCHEMA = "rrct.agent_causal_boundary.v4"

    def __init__(
        self,
        observation_dim: int,
        *,
        action_dim: int = 2,
        n_levels: int = 4,
        projector_ranks: Sequence[int] | None = None,
        n_specialists: int = 6,
        specialist_dim: int = 16,
        workspace_dim: int = 16,
        workspace_capacity: int = 3,
        self_dim: int = 12,
        memory_capacity: int = 64,
        memory_top_k: int = 3,
        seed: int = 0,
        recurrent_gain: float = 1.0,
        closure_gain: float = 1.0,
        self_feedback_gain: float = 1.0,
        action_feedback_gain: float = 1.0,
        self_model_mode: str = "frozen",
        self_model_learning_rate: float = 0.08,
        observation_forecaster_learning_rate: float = 0.08,
        feedback_mode: str = "fixed",
        feedback_minimum_gain: float = 0.15,
        feedback_maximum_gain: float = 1.20,
        feedback_adaptation_rate: float = 0.35,
        feedback_maximum_step: float = 0.12,
        feedback_deadband: float = 0.02,
        causal_boundary_config: CausalBoundaryConfig | None = None,
        causal_boundary_broadcast_gain: float = 0.28,
        causal_access_readout_mode: str = "centroid",
        causal_access_memory_capacity: int = 64,
        causal_access_neighbors: int = 1,
        causal_access_prototype_learning_rate: float = 0.25,
        ablations: AblationFlags
        | str
        | Iterable[str]
        | Mapping[str, bool]
        | None = None,
    ) -> None:
        integer_parameters = {
            "observation_dim": observation_dim,
            "action_dim": action_dim,
            "n_levels": n_levels,
            "n_specialists": n_specialists,
            "specialist_dim": specialist_dim,
            "workspace_dim": workspace_dim,
            "workspace_capacity": workspace_capacity,
            "self_dim": self_dim,
            "memory_capacity": memory_capacity,
            "memory_top_k": memory_top_k,
            "causal_access_memory_capacity": causal_access_memory_capacity,
            "causal_access_neighbors": causal_access_neighbors,
        }
        for name, value in integer_parameters.items():
            if int(value) != value or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

        self.observation_dim = int(observation_dim)
        self.action_dim = int(action_dim)
        self.n_levels = int(n_levels)
        self.projector_ranks = (
            tuple(int(rank) for rank in projector_ranks)
            if projector_ranks is not None
            else None
        )
        self.n_specialists = int(n_specialists)
        self.specialist_dim = int(specialist_dim)
        self.workspace_dim = int(workspace_dim)
        self.workspace_capacity = int(workspace_capacity)
        self.self_dim = int(self_dim)
        self.memory_capacity = int(memory_capacity)
        self.memory_top_k = int(memory_top_k)
        self.seed = int(seed)
        for name, value in (
            ("recurrent_gain", recurrent_gain),
            ("closure_gain", closure_gain),
            ("self_feedback_gain", self_feedback_gain),
            ("action_feedback_gain", action_feedback_gain),
        ):
            if not np.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
        if self_model_mode not in {"train", "frozen"}:
            raise ValueError("self_model_mode must be 'train' or 'frozen'")
        if feedback_mode not in {"fixed", "adaptive", "manual"}:
            raise ValueError("feedback_mode must be 'fixed', 'adaptive', or 'manual'")
        if causal_boundary_config is not None:
            if not isinstance(causal_boundary_config, CausalBoundaryConfig):
                raise TypeError(
                    "causal_boundary_config must be a CausalBoundaryConfig or None"
                )
            if causal_boundary_config.observation_dim != self.observation_dim:
                raise ValueError(
                    "causal boundary observation_dim must match the agent"
                )
        if causal_access_readout_mode not in {
            "centroid",
            "fifo_memory",
            "prototype_memory",
            "direct_candidate",
        }:
            raise ValueError(
                "causal_access_readout_mode must be 'centroid', "
                "'fifo_memory', 'prototype_memory', or "
                "'direct_candidate'"
            )
        if int(causal_access_neighbors) > int(causal_access_memory_capacity):
            raise ValueError(
                "causal_access_neighbors cannot exceed memory capacity"
            )
        if (
            isinstance(
                causal_access_prototype_learning_rate, (bool, np.bool_)
            )
            or not np.isscalar(causal_access_prototype_learning_rate)
            or not np.isfinite(causal_access_prototype_learning_rate)
            or not 0.0 < float(causal_access_prototype_learning_rate) <= 1.0
        ):
            raise ValueError(
                "causal_access_prototype_learning_rate must lie in (0, 1]"
            )
        if (
            isinstance(causal_boundary_broadcast_gain, (bool, np.bool_))
            or not np.isscalar(causal_boundary_broadcast_gain)
            or not np.isfinite(causal_boundary_broadcast_gain)
            or float(causal_boundary_broadcast_gain) < 0.0
        ):
            raise ValueError(
                "causal_boundary_broadcast_gain must be finite and nonnegative"
            )
        feedback_values: dict[str, float] = {}
        for name, value in (
            ("feedback_minimum_gain", feedback_minimum_gain),
            ("feedback_maximum_gain", feedback_maximum_gain),
            ("feedback_adaptation_rate", feedback_adaptation_rate),
            ("feedback_maximum_step", feedback_maximum_step),
            ("feedback_deadband", feedback_deadband),
        ):
            if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
                raise ValueError(f"{name} must be a finite real scalar")
            parsed_value = float(value)
            if not np.isfinite(parsed_value):
                raise ValueError(f"{name} must be a finite real scalar")
            feedback_values[name] = parsed_value
        if (
            feedback_values["feedback_minimum_gain"] < 0.0
            or feedback_values["feedback_maximum_gain"]
            <= feedback_values["feedback_minimum_gain"]
        ):
            raise ValueError("feedback gain bounds must satisfy 0 <= minimum < maximum")
        if not 0.0 < feedback_values["feedback_adaptation_rate"] <= 1.0:
            raise ValueError("feedback_adaptation_rate must lie in (0, 1]")
        if feedback_values["feedback_maximum_step"] <= 0.0:
            raise ValueError("feedback_maximum_step must be positive")
        if not 0.0 <= feedback_values["feedback_deadband"] < 1.0:
            raise ValueError("feedback_deadband must lie in [0, 1)")
        self.recurrent_gain = float(recurrent_gain)
        self.closure_gain = float(closure_gain)
        self.self_feedback_gain = float(self_feedback_gain)
        self.action_feedback_gain = float(action_feedback_gain)
        self.self_model_learning_rate = float(self_model_learning_rate)
        self.observation_forecaster_learning_rate = float(
            observation_forecaster_learning_rate
        )
        self._self_model_mode = str(self_model_mode)
        self.feedback_mode = str(feedback_mode)
        self.feedback_minimum_gain = feedback_values["feedback_minimum_gain"]
        self.feedback_maximum_gain = feedback_values["feedback_maximum_gain"]
        self.feedback_adaptation_rate = feedback_values["feedback_adaptation_rate"]
        self.feedback_maximum_step = feedback_values["feedback_maximum_step"]
        self.feedback_deadband = feedback_values["feedback_deadband"]
        self.causal_boundary_config = causal_boundary_config
        self.causal_boundary_broadcast_gain = float(
            causal_boundary_broadcast_gain
        )
        self.causal_access_readout_mode = str(causal_access_readout_mode)
        self.causal_access_memory_capacity = int(
            causal_access_memory_capacity
        )
        self.causal_access_neighbors = int(causal_access_neighbors)
        self.causal_access_prototype_learning_rate = float(
            causal_access_prototype_learning_rate
        )
        self.ablations = AblationFlags.parse(ablations)

        self.projectors: NestedOrthogonalProjectors
        self.specialists: tuple[SpecialistModule, ...]
        self.workspace: GlobalWorkspace
        self.self_model: NonValencedSelfModel
        self.observation_forecaster: NonValencedObservationForecaster
        self.bayesian_transfer: BayesianCausalTransferModel
        self.memory: EpisodicMemory
        self.controller: CounterfactualController
        self.causal_boundary: OnlineCausalSelfBoundary | None
        self._causal_access_readout: (
            OnlineCausalAccessReadout
            | OnlineCausalAccessMemoryReadout
            | DirectCausalAccessReadout
            | None
        )
        self._causal_boundary_projection: FloatArray | None
        self._build_components(self.seed)
        self._time = 0
        self._resolution_level = len(self.projectors) - 1
        self._last_action = np.zeros(self.action_dim, dtype=np.float64)
        self._last_result: StepResult | None = None
        self._intention_calibration_records: list[IntentionCalibrationRecord] = []
        self._intention_calibration_key: str | None = None
        self._intention_calibration_capacity = 128
        self._intention_calibration_epoch = 0
        self._intention_calibration_last_reset_reason: str | None = None
        self._bayesian_transfer_key: str | None = None
        self._bayesian_transfer_updates: list[BayesianTransferUpdate] = []
        self._bayesian_transfer_epoch = 0
        self._bayesian_transfer_last_reset_reason: str | None = None
        self._last_public_causal_pair: tuple[int, int] | None = None

    def _build_components(self, seed: int) -> None:
        child_count = self.n_specialists + 6
        children = np.random.SeedSequence(seed).spawn(child_count)
        self.projectors = NestedOrthogonalProjectors(
            self.observation_dim,
            ranks=self.projector_ranks,
            n_levels=self.n_levels,
            # The generic projector bank supports random or user-supplied
            # bases.  The integrated agent uses coordinate order as its stable
            # semantic filtration so experiments are comparable across seeds.
            basis=np.eye(self.observation_dim, dtype=np.float64),
            seed=children[0],
        )
        specialist_children = children[1 : 1 + self.n_specialists]
        self.specialists = tuple(
            SpecialistModule(
                self.observation_dim,
                self.specialist_dim,
                level=index % len(self.projectors),
                broadcast_dim=self.workspace_dim,
                name=f"specialist_{index:02d}_level_{index % len(self.projectors)}",
                seed=specialist_children[index],
            )
            for index in range(self.n_specialists)
        )
        offset = 1 + self.n_specialists
        self.workspace = GlobalWorkspace(
            self.specialist_dim,
            self.workspace_dim,
            capacity=self.workspace_capacity,
            seed=children[offset],
        )
        self.self_model = NonValencedSelfModel(
            self.workspace_dim,
            self.self_dim,
            learning_rate=self.self_model_learning_rate,
            training=self._self_model_mode == "train",
            seed=children[offset + 1],
        )
        self.controller = CounterfactualController(
            self.observation_dim,
            self.workspace_dim,
            self.self_dim,
            self.action_dim,
            seed=children[offset + 2],
        )
        self.memory = EpisodicMemory(
            self.workspace_dim,
            capacity=self.memory_capacity,
            top_k=self.memory_top_k,
        )
        self.observation_forecaster = NonValencedObservationForecaster(
            self.observation_dim,
            learning_rate=self.observation_forecaster_learning_rate,
            training=self._self_model_mode == "train",
        )
        self.bayesian_transfer = BayesianCausalTransferModel(
            len(self.BAYESIAN_TRANSFER_FEATURE_NAMES),
            include_intercept=False,
            feature_bound=1.0,
            target_bound=1.0,
            prior_precision=self.BAYESIAN_TRANSFER_PRIOR_PRECISION,
            prior_shape=self.BAYESIAN_TRANSFER_PRIOR_SHAPE,
            prior_scale=self.BAYESIAN_TRANSFER_PRIOR_SCALE,
            coordinate_names=self.BAYESIAN_TRANSFER_FEATURE_NAMES,
            training=False,
        )
        self.feedback_regulator: AdaptiveFeedbackRegulator | None = None
        if self.feedback_mode in {"adaptive", "manual"}:
            self.feedback_regulator = AdaptiveFeedbackRegulator(
                self.recurrent_gain,
                self.closure_gain,
                minimum_gain=self.feedback_minimum_gain,
                maximum_gain=self.feedback_maximum_gain,
                adaptation_rate=self.feedback_adaptation_rate,
                maximum_step=self.feedback_maximum_step,
                deadband=self.feedback_deadband,
            )
        feedback_rng = np.random.default_rng(children[offset + 3])
        self._self_feedback = balanced_matrix(
            feedback_rng,
            self.workspace_dim,
            self.self_dim,
            gain=0.16,
        )
        self._action_feedback = balanced_matrix(
            feedback_rng,
            self.workspace_dim,
            self.action_dim,
            gain=0.10,
        )
        if self.causal_boundary_config is None:
            self.causal_boundary = None
            self._causal_access_readout = None
            self._causal_boundary_projection = None
        else:
            self.causal_boundary = OnlineCausalSelfBoundary(
                self.causal_boundary_config
            )
            self._causal_access_readout = self._new_causal_access_readout()
            boundary_rng = np.random.default_rng(
                np.random.SeedSequence([int(seed), 29_029])
            )
            self._causal_boundary_projection = balanced_matrix(
                boundary_rng,
                self.specialist_dim,
                self.causal_boundary.descriptor_dim,
                gain=1.0,
            )

    def _new_causal_access_readout(
        self,
    ) -> (
        OnlineCausalAccessReadout
        | OnlineCausalAccessMemoryReadout
        | DirectCausalAccessReadout
    ):
        if self.causal_boundary_config is None:
            raise RuntimeError("causal boundary configuration is absent")
        arguments = (
            self.workspace_dim + self.self_dim,
            self.causal_boundary_config.handle_count,
            self.causal_boundary_config.source_count,
        )
        if self.causal_access_readout_mode == "centroid":
            return OnlineCausalAccessReadout(*arguments)
        if self.causal_access_readout_mode == "direct_candidate":
            return DirectCausalAccessReadout(*arguments)
        strategy = (
            "fifo"
            if self.causal_access_readout_mode == "fifo_memory"
            else "prototype"
        )
        return OnlineCausalAccessMemoryReadout(
            *arguments,
            memory_capacity=self.causal_access_memory_capacity,
            neighbors=self.causal_access_neighbors,
            strategy=strategy,
            prototype_learning_rate=(
                self.causal_access_prototype_learning_rate
            ),
        )

    @property
    def time(self) -> int:
        """Number of completed steps since reset."""

        return self._time

    @property
    def resolution_level(self) -> int:
        """Resolution that will process the next observation."""

        return self._resolution_level

    @property
    def last_result(self) -> StepResult | None:
        """Most recent step result, if any."""

        return self._last_result

    @property
    def effective_recurrent_gain(self) -> float:
        """Recurrent gain after the categorical recurrence ablation gate."""

        return 0.0 if self.ablations.recurrence else self.current_recurrent_gain

    @property
    def effective_closure_gain(self) -> float:
        """Shared closure master gain after the recurrence category gate."""

        return 0.0 if self.ablations.recurrence else self.current_closure_gain

    @property
    def effective_self_feedback_gain(self) -> float:
        """Actual self-to-workspace gain after the recurrence category gate."""

        if self.ablations.recurrence:
            return 0.0
        return self.current_closure_gain * self.self_feedback_gain

    @property
    def effective_action_feedback_gain(self) -> float:
        """Actual action-to-workspace gain after the recurrence category gate."""

        if self.ablations.recurrence:
            return 0.0
        return self.current_closure_gain * self.action_feedback_gain

    @property
    def current_recurrent_gain(self) -> float:
        """Gain committed before the next causal step begins."""

        if self.feedback_regulator is None or self.ablations.feedback_adaptation:
            return self.recurrent_gain
        return self.feedback_regulator.current_recurrent_gain

    @property
    def current_closure_gain(self) -> float:
        """Closure gain committed before the next causal step begins."""

        if self.feedback_regulator is None or self.ablations.feedback_adaptation:
            return self.closure_gain
        return self.feedback_regulator.current_closure_gain

    @property
    def last_feedback_control(self) -> FeedbackControlRecord | None:
        """Most recent adaptive next-step decision, if one has occurred."""

        return self.feedback_regulator.last_record if self.feedback_regulator is not None else None

    def feedback_snapshot(self) -> dict[str, Any]:
        """Return immutable configuration and bounded dynamic feedback state."""

        payload = {
            "schema": self.FEEDBACK_SNAPSHOT_SCHEMA,
            "mode": self.feedback_mode,
            "adaptation_ablated": bool(self.ablations.feedback_adaptation),
            "nominal_recurrent_gain": self.recurrent_gain,
            "nominal_closure_gain": self.closure_gain,
            "current_recurrent_gain": self.current_recurrent_gain,
            "current_closure_gain": self.current_closure_gain,
            "regulator": (
                self.feedback_regulator.snapshot()
                if self.feedback_regulator is not None
                else None
            ),
        }
        payload["digest"] = AdaptiveFeedbackRegulator._digest_payload(payload)
        return payload

    def load_feedback_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        """Transactionally restore a configuration-matched feedback state."""

        if not isinstance(snapshot, Mapping):
            raise TypeError("feedback snapshot must be a mapping")
        expected = {
            "schema",
            "mode",
            "adaptation_ablated",
            "nominal_recurrent_gain",
            "nominal_closure_gain",
            "current_recurrent_gain",
            "current_closure_gain",
            "regulator",
            "digest",
        }
        if set(snapshot) != expected:
            raise ValueError("agent feedback snapshot fields do not match")
        payload = {key: snapshot[key] for key in expected if key != "digest"}
        if snapshot["schema"] != self.FEEDBACK_SNAPSHOT_SCHEMA:
            raise ValueError("agent feedback snapshot schema does not match")
        if (
            not isinstance(snapshot["digest"], str)
            or snapshot["digest"]
            != AdaptiveFeedbackRegulator._digest_payload(payload)
        ):
            raise ValueError("agent feedback snapshot digest is invalid")
        if snapshot["mode"] != self.feedback_mode:
            raise ValueError("feedback snapshot mode does not match")
        if not isinstance(snapshot["adaptation_ablated"], (bool, np.bool_)):
            raise ValueError("feedback snapshot ablation state must be boolean")
        if snapshot["adaptation_ablated"] != bool(self.ablations.feedback_adaptation):
            raise ValueError("feedback snapshot ablation state does not match")
        for field_name, expected_value in (
            ("nominal_recurrent_gain", self.recurrent_gain),
            ("nominal_closure_gain", self.closure_gain),
        ):
            value = snapshot[field_name]
            if (
                isinstance(value, (bool, np.bool_))
                or not np.isscalar(value)
                or not np.isfinite(value)
                or float(value) != float(expected_value)
            ):
                raise ValueError(f"{field_name} does not match")
        current_values: dict[str, float] = {}
        for field_name in ("current_recurrent_gain", "current_closure_gain"):
            value = snapshot[field_name]
            if (
                isinstance(value, (bool, np.bool_))
                or not np.isscalar(value)
                or np.asarray(value).dtype.kind not in "iuf"
                or not np.isfinite(value)
            ):
                raise ValueError(f"{field_name} must be a finite real scalar")
            current_values[field_name] = float(value)
        if self.feedback_regulator is None:
            if snapshot["regulator"] is not None:
                raise ValueError("fixed feedback cannot load regulator state")
            if (
                current_values["current_recurrent_gain"] != self.recurrent_gain
                or current_values["current_closure_gain"] != self.closure_gain
            ):
                raise ValueError("fixed feedback state must equal nominal gains")
            return
        candidate = copy.deepcopy(self.feedback_regulator)
        candidate.load_snapshot(snapshot["regulator"])
        if (
            current_values["current_recurrent_gain"]
            != candidate.current_recurrent_gain
            or current_values["current_closure_gain"]
            != candidate.current_closure_gain
        ):
            raise ValueError("agent and regulator feedback states disagree")
        self.feedback_regulator = candidate

    def set_active_feedback(self, recurrent_gain: float, closure_gain: float) -> None:
        """Commit one explicit next-step gain pair in ``manual`` mode."""

        if self.feedback_mode != "manual" or self.feedback_regulator is None:
            raise RuntimeError("active feedback can be set only in manual mode")
        old_recurrent = self.feedback_regulator.current_recurrent_gain
        old_closure = self.feedback_regulator.current_closure_gain
        self.feedback_regulator.set_current(recurrent_gain, closure_gain)
        changed = (
            self.feedback_regulator.current_recurrent_gain != old_recurrent
            or self.feedback_regulator.current_closure_gain != old_closure
        )
        if changed and self._intention_calibration_records:
            self.reset_intention_calibration(reason="manual_feedback_changed")
        if changed and self.bayesian_transfer.observation_count:
            self.reset_bayesian_transfer(reason="manual_feedback_changed")

    @property
    def self_model_mode(self) -> str:
        """Current predictor mode: ``"train"`` or ``"frozen"``."""

        return self._self_model_mode

    @property
    def self_learning_updates(self) -> int:
        """Number of enabled normalized-LMS predictor updates."""

        return self.self_model.learning_steps

    def train_self_model(self) -> None:
        """Explicitly enable online predictor learning."""

        if self._intention_calibration_records:
            self.reset_intention_calibration(reason="predictors_entered_training_mode")
        if self.bayesian_transfer.observation_count:
            self.reset_bayesian_transfer(reason="predictors_entered_training_mode")
        self._self_model_mode = "train"
        self.self_model.train()
        self.observation_forecaster.train()

    def freeze_self_model(self) -> None:
        """Freeze learned predictor parameters for evaluation."""

        self._self_model_mode = "frozen"
        self.self_model.freeze()
        self.observation_forecaster.freeze()

    def observation_forecaster_snapshot(self) -> dict[str, Any]:
        """Return learned observation-forecast parameters."""

        return self.observation_forecaster.snapshot()

    def load_observation_forecaster_snapshot(
        self, snapshot: Mapping[str, Any], *, freeze: bool = True
    ) -> None:
        """Load exact observation-forecast parameters."""

        self.observation_forecaster.load_snapshot(snapshot, freeze=freeze)
        if self._intention_calibration_records:
            self.reset_intention_calibration(reason="observation_forecaster_replaced")
        if self.bayesian_transfer.observation_count:
            self.reset_bayesian_transfer(reason="observation_forecaster_replaced")

    @property
    def bayesian_transfer_improvement_scale(self) -> float:
        """Architectural bound for one baseline-to-intervention reduction."""

        return 2.0 * np.sqrt(float(self.workspace_dim))

    @property
    def bayesian_transfer_target_scale(self) -> float:
        """Bound for a realized-minus-rollout transfer correction."""

        return 4.0 * np.sqrt(float(self.workspace_dim))

    def train_bayesian_transfer(self) -> None:
        """Enable explicit post-reveal Bayesian transfer conditioning."""

        if self.feedback_mode != "fixed":
            raise RuntimeError(
                "Bayesian transfer v0.9 supports fixed feedback only"
            )
        if any(
            update.outcome_source == "permuted_control"
            for update in self._bayesian_transfer_updates
        ):
            raise RuntimeError("a permuted-control posterior cannot resume training")
        if (
            self._self_model_mode != "frozen"
            or self.self_model.training
            or self.observation_forecaster.training
        ):
            raise RuntimeError("Bayesian transfer training requires frozen predictors")
        if self._intention_calibration_records:
            self.reset_intention_calibration(reason="bayesian_posterior_entered_training_mode")
        self.bayesian_transfer.train()

    def freeze_bayesian_transfer(self) -> None:
        """Freeze the causal-transfer posterior for calibration or evaluation."""

        self.bayesian_transfer.freeze()

    def _bayesian_transfer_digest(self) -> str:
        payload = (
            1,
            self._bayesian_transfer_epoch,
            self._bayesian_transfer_key,
            tuple(self._bayesian_transfer_updates),
            self._bayesian_transfer_last_reset_reason,
            self.bayesian_transfer.posterior_digest(),
        )
        return hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()

    @staticmethod
    def bayesian_transfer_permutation_digest(
        transfer_key: str, permutation: Sequence[int]
    ) -> str:
        """Hash the complete episode permutation used by a negative control."""

        payload = (
            "rrct.v09.bayesian_transfer_permutation.v1",
            transfer_key,
            tuple(int(value) for value in permutation),
        )
        return hashlib.sha256(pickle.dumps(payload, protocol=5)).hexdigest()

    @staticmethod
    def bayesian_transfer_control_evidence_digest(
        *,
        permutation_digest: str,
        feature_episode_index: int,
        target_episode_index: int,
        candidate_indices: Sequence[int],
        target_candidate_indices: Sequence[int],
        normalized_targets: Sequence[float],
    ) -> str:
        """Hash one explicit feature/outcome pairing in a permuted control."""

        payload = (
            "rrct.v09.bayesian_transfer_control_evidence.v1",
            permutation_digest,
            int(feature_episode_index),
            int(target_episode_index),
            tuple(int(value) for value in candidate_indices),
            tuple(int(value) for value in target_candidate_indices),
            tuple(float(value) for value in normalized_targets),
        )
        return hashlib.sha256(pickle.dumps(payload, protocol=5)).hexdigest()

    def bayesian_transfer_snapshot(self) -> dict[str, Any]:
        """Return the posterior, configuration provenance, and update receipts."""

        return {
            "schema_version": 1,
            "transfer_key": self._bayesian_transfer_key,
            "epoch": self._bayesian_transfer_epoch,
            "updates": tuple(asdict(update) for update in self._bayesian_transfer_updates),
            "update_count": len(self._bayesian_transfer_updates),
            "last_reset_reason": self._bayesian_transfer_last_reset_reason,
            "model": self.bayesian_transfer.snapshot(),
            "digest": self._bayesian_transfer_digest(),
        }

    def load_bayesian_transfer_snapshot(
        self,
        snapshot: Mapping[str, Any],
        *,
        freeze: bool = True,
    ) -> None:
        """Transactionally load an auditable transfer posterior."""

        if not isinstance(snapshot, Mapping):
            raise TypeError("Bayesian transfer agent snapshot must be a mapping")
        if self.feedback_mode != "fixed" and snapshot.get("updates"):
            raise ValueError(
                "Bayesian transfer v0.9 evidence cannot load under adaptive feedback"
            )

        required_agent_fields = {
            "schema_version",
            "transfer_key",
            "epoch",
            "updates",
            "update_count",
            "last_reset_reason",
            "model",
            "digest",
        }
        missing_agent_fields = sorted(required_agent_fields.difference(snapshot))
        if missing_agent_fields:
            raise ValueError(
                "Bayesian transfer agent snapshot is missing required fields: "
                + ", ".join(missing_agent_fields)
            )
        unknown_agent_fields = sorted(set(snapshot).difference(required_agent_fields))
        if unknown_agent_fields:
            raise ValueError(
                "Bayesian transfer agent snapshot has unknown fields: "
                + ", ".join(unknown_agent_fields)
            )

        def exact_nonnegative_integer(value: Any, name: str) -> int:
            if isinstance(value, (bool, np.bool_)) or not isinstance(
                value, (int, np.integer)
            ):
                raise ValueError(f"{name} must be a nonnegative integer")
            result = int(value)
            if result < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
            return result

        def finite_real(value: Any, name: str) -> float:
            if isinstance(value, (bool, np.bool_)) or not isinstance(
                value, (int, float, np.integer, np.floating)
            ):
                raise ValueError(f"{name} must be finite")
            result = float(value)
            if not np.isfinite(result):
                raise ValueError(f"{name} must be finite")
            return result

        def valid_sha256(value: Any) -> bool:
            return (
                isinstance(value, str)
                and len(value) == 64
                and all(character in "0123456789abcdef" for character in value)
            )

        schema_version = exact_nonnegative_integer(
            snapshot.get("schema_version"), "Bayesian transfer schema_version"
        )
        if schema_version != 1:
            raise ValueError("unsupported Bayesian transfer agent snapshot")
        if not isinstance(freeze, (bool, np.bool_)):
            raise ValueError("freeze must be boolean")
        transfer_key = snapshot.get("transfer_key")
        if transfer_key is not None and (
            not isinstance(transfer_key, str) or not transfer_key
        ):
            raise ValueError("transfer_key must be null or a nonempty string")
        raw_updates_value = snapshot.get("updates")
        if not isinstance(raw_updates_value, (tuple, list)):
            raise ValueError("Bayesian transfer updates must be a sequence")
        raw_updates = tuple(raw_updates_value)
        updates: list[BayesianTransferUpdate] = []
        for item in raw_updates:
            if not isinstance(item, Mapping):
                raise ValueError("Bayesian transfer update must be a mapping")
            values = dict(item)
            values["candidate_indices"] = tuple(values.get("candidate_indices", ()))
            values["target_candidate_indices"] = tuple(
                values.get("target_candidate_indices", ())
            )
            values["normalized_targets"] = tuple(values.get("normalized_targets", ()))
            try:
                updates.append(BayesianTransferUpdate(**values))
            except TypeError as exc:
                raise ValueError("invalid Bayesian transfer update schema") from exc
        update_count = exact_nonnegative_integer(
            snapshot.get("update_count"), "Bayesian transfer update_count"
        )
        if update_count != len(updates):
            raise ValueError("Bayesian transfer update count mismatch")
        epoch = exact_nonnegative_integer(
            snapshot.get("epoch"), "Bayesian transfer epoch"
        )
        reset_reason = snapshot.get("last_reset_reason")
        if reset_reason is not None and (
            not isinstance(reset_reason, str) or not reset_reason
        ):
            raise ValueError("Bayesian transfer reset reason must be null or nonempty")
        candidate = BayesianCausalTransferModel(
            len(self.BAYESIAN_TRANSFER_FEATURE_NAMES),
            include_intercept=False,
            feature_bound=1.0,
            target_bound=1.0,
            prior_precision=self.BAYESIAN_TRANSFER_PRIOR_PRECISION,
            prior_shape=self.BAYESIAN_TRANSFER_PRIOR_SHAPE,
            prior_scale=self.BAYESIAN_TRANSFER_PRIOR_SCALE,
            coordinate_names=self.BAYESIAN_TRANSFER_FEATURE_NAMES,
        )
        prior_digest = candidate.posterior_digest()
        raw_model = snapshot.get("model")
        if not isinstance(raw_model, Mapping):
            raise ValueError("Bayesian transfer model snapshot must be a mapping")
        model_snapshot = dict(raw_model)
        if "coordinate_names" in model_snapshot:
            model_snapshot["coordinate_names"] = tuple(
                model_snapshot["coordinate_names"]
            )
        candidate.load_snapshot(model_snapshot, freeze=freeze)
        if candidate.observation_count > 0 and not updates:
            raise ValueError("posterior observations require update receipts")
        if updates and transfer_key is None:
            raise ValueError("Bayesian update receipts require a transfer key")
        outcome_sources = {update.outcome_source for update in updates}
        if len(outcome_sources) > 1:
            raise ValueError("Bayesian transfer receipts must have one provenance class")
        if outcome_sources == {"permuted_control"} and not bool(freeze):
            raise ValueError("a permuted-control posterior must remain frozen")
        expected_count = 0
        expected_effective = 0.0
        expected_digest = prior_digest
        for index, update in enumerate(updates):
            if exact_nonnegative_integer(
                update.sequence_id, "Bayesian transfer sequence_id"
            ) != index:
                raise ValueError("Bayesian transfer updates must be contiguous")
            if update.transfer_key != transfer_key or update.outcome_source not in {
                "shadow",
                "permuted_control",
            }:
                raise ValueError("Bayesian transfer update provenance mismatch")
            candidate_count = len(update.candidate_indices)
            try:
                normalized_targets = np.asarray(
                    update.normalized_targets, dtype=np.float64
                )
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("invalid Bayesian transfer targets") from exc
            if (
                not update.candidate_indices
                or candidate_count != len(update.normalized_targets)
                or candidate_count != len(update.target_candidate_indices)
                or any(
                    isinstance(value, (bool, np.bool_))
                    or not isinstance(value, (int, np.integer))
                    or not 1 <= int(value) <= 2 * self.self_dim
                    for value in (
                        tuple(update.candidate_indices)
                        + tuple(update.target_candidate_indices)
                    )
                )
                or len(set(update.candidate_indices)) != candidate_count
                or len(set(update.target_candidate_indices)) != candidate_count
                or normalized_targets.shape != (candidate_count,)
                or not np.all(np.isfinite(normalized_targets))
                or np.any(np.abs(normalized_targets) > 1.0)
                or not np.isclose(
                    finite_real(
                        update.per_candidate_weight,
                        "Bayesian transfer per_candidate_weight",
                    ),
                    1.0 / candidate_count,
                    atol=1e-15,
                    rtol=1e-15,
                )
                or not valid_sha256(update.evidence_digest)
                or exact_nonnegative_integer(
                    update.observation_count_before,
                    "Bayesian transfer observation_count_before",
                )
                != expected_count
                or exact_nonnegative_integer(
                    update.observation_count_after,
                    "Bayesian transfer observation_count_after",
                )
                != expected_count + candidate_count
                or update.observation_count_before != expected_count
                or update.observation_count_after != expected_count + candidate_count
                or not np.isclose(
                    finite_real(
                        update.effective_sample_count_before,
                        "Bayesian transfer effective_sample_count_before",
                    ),
                    expected_effective,
                    atol=1e-12,
                    rtol=1e-12,
                )
                or not np.isclose(
                    finite_real(
                        update.effective_sample_count_after,
                        "Bayesian transfer effective_sample_count_after",
                    ),
                    expected_effective + 1.0,
                    atol=1e-12,
                    rtol=1e-12,
                )
                or update.posterior_digest_before != expected_digest
                or not valid_sha256(update.posterior_digest_before)
                or not valid_sha256(update.posterior_digest_after)
                or update.posterior_digest_after == update.posterior_digest_before
            ):
                raise ValueError("invalid Bayesian transfer update receipt")
            if update.outcome_source == "shadow":
                if (
                    exact_nonnegative_integer(
                        update.planned_time, "Bayesian transfer planned_time"
                    )
                    < 0
                    or exact_nonnegative_integer(
                        update.recorded_time, "Bayesian transfer recorded_time"
                    )
                    < 0
                    or update.feature_episode_index is not None
                    or update.target_episode_index is not None
                    or update.permutation_digest is not None
                    or update.target_candidate_indices != update.candidate_indices
                ):
                    raise ValueError("invalid shadow Bayesian transfer provenance")
            else:
                feature_episode_index = exact_nonnegative_integer(
                    update.feature_episode_index,
                    "Bayesian transfer feature_episode_index",
                )
                target_episode_index = exact_nonnegative_integer(
                    update.target_episode_index,
                    "Bayesian transfer target_episode_index",
                )
                if (
                    update.planned_time is not None
                    or update.recorded_time is not None
                    or feature_episode_index != index
                    or target_episode_index >= len(updates)
                    or not valid_sha256(update.permutation_digest)
                    or update.evidence_digest
                    != self.bayesian_transfer_control_evidence_digest(
                        permutation_digest=update.permutation_digest,
                        feature_episode_index=feature_episode_index,
                        target_episode_index=target_episode_index,
                        candidate_indices=update.candidate_indices,
                        target_candidate_indices=update.target_candidate_indices,
                        normalized_targets=update.normalized_targets,
                    )
                ):
                    raise ValueError("invalid permuted Bayesian control provenance")
            expected_count = update.observation_count_after
            expected_effective = update.effective_sample_count_after
            expected_digest = update.posterior_digest_after
        if outcome_sources == {"permuted_control"}:
            permutation = tuple(
                int(update.target_episode_index) for update in updates
            )
            permutation_digests = {
                str(update.permutation_digest) for update in updates
            }
            if (
                tuple(int(update.feature_episode_index) for update in updates)
                != tuple(range(len(updates)))
                or tuple(sorted(permutation)) != tuple(range(len(updates)))
                or len(permutation_digests) != 1
                or next(iter(permutation_digests))
                != self.bayesian_transfer_permutation_digest(
                    str(transfer_key), permutation
                )
            ):
                raise ValueError("invalid Bayesian control permutation")
        if (
            expected_count != candidate.observation_count
            or not np.isclose(
                expected_effective,
                candidate.effective_sample_count,
                atol=1e-12,
                rtol=1e-12,
            )
            or expected_digest != candidate.posterior_digest()
        ):
            raise ValueError("Bayesian transfer receipt chain does not match posterior")
        payload = (
            1,
            int(epoch),
            transfer_key,
            tuple(updates),
            reset_reason,
            candidate.posterior_digest(),
        )
        digest = hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()
        if snapshot.get("digest") != digest:
            raise ValueError("Bayesian transfer agent snapshot digest mismatch")
        self.bayesian_transfer = candidate
        self._bayesian_transfer_key = transfer_key
        self._bayesian_transfer_updates = updates
        self._bayesian_transfer_epoch = int(epoch)
        self._bayesian_transfer_last_reset_reason = reset_reason
        if self._intention_calibration_records:
            self.reset_intention_calibration(reason="bayesian_posterior_replaced")

    def reset_bayesian_transfer(self, *, reason: str) -> dict[str, Any]:
        """Explicitly erase learned transfer evidence with an audit receipt."""

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Bayesian transfer reset requires a nonempty reason")
        old_digest = self._bayesian_transfer_digest()
        old_count = self.bayesian_transfer.observation_count
        old_epoch = self._bayesian_transfer_epoch
        self.bayesian_transfer.reset()
        self.bayesian_transfer.freeze()
        self._bayesian_transfer_key = None
        self._bayesian_transfer_updates = []
        self._bayesian_transfer_epoch += 1
        self._bayesian_transfer_last_reset_reason = reason.strip()
        if self._intention_calibration_records:
            self.reset_intention_calibration(reason="bayesian_posterior_reset")
        return {
            "reason": self._bayesian_transfer_last_reset_reason,
            "time": self._time,
            "old_count": old_count,
            "new_count": 0,
            "old_epoch": old_epoch,
            "new_epoch": self._bayesian_transfer_epoch,
            "old_digest": old_digest,
            "new_digest": self._bayesian_transfer_digest(),
        }

    @staticmethod
    def _conformal_optimism_threshold(
        values: Sequence[float],
        *,
        alpha: float,
        minimum_records: int,
    ) -> tuple[bool, float | None]:
        """Return a finite-sample one-sided split-conformal upper rank."""

        if not np.isfinite(alpha) or not 0.0 < alpha < 1.0:
            raise ValueError("calibration_alpha must lie in (0, 1)")
        if (
            isinstance(minimum_records, (bool, np.bool_))
            or
            not np.isscalar(minimum_records)
            or not np.isfinite(minimum_records)
            or int(minimum_records) != minimum_records
            or not 1 <= minimum_records <= 128
        ):
            raise ValueError("calibration_min_samples must be an integer from 1 through 128")
        observed = np.asarray(tuple(values), dtype=np.float64)
        if observed.ndim != 1 or not np.all(np.isfinite(observed)):
            raise ValueError("calibration optimism values must be a finite vector")
        count = int(observed.size)
        rank = int(np.ceil((count + 1) * (1.0 - float(alpha))))
        if count < int(minimum_records) or rank > count:
            return False, None
        threshold = max(0.0, float(np.sort(observed, kind="stable")[rank - 1]))
        return True, threshold

    def _intention_calibration_digest(self) -> str:
        payload = (
            1,
            self._intention_calibration_epoch,
            self._intention_calibration_key,
            tuple(self._intention_calibration_records),
            self._intention_calibration_capacity,
            self._intention_calibration_last_reset_reason,
        )
        return hashlib.sha256(pickle.dumps(payload, protocol=5)).hexdigest()

    def _intention_base_configuration_key(
        self,
        *,
        horizon: int,
        query_budget: int,
        candidate_magnitude: float,
        forecast_decay: float,
        forecast_mode: str,
        max_delta_norm: float,
    ) -> str:
        predictor = self.self_model.predictor_snapshot()
        forecaster = self.observation_forecaster.snapshot()
        feedback_configuration = (
            self.feedback_regulator.configuration
            if self.feedback_regulator is not None
            else None
        )
        manual_feedback_state = (
            (self.current_recurrent_gain, self.current_closure_gain)
            if self.feedback_mode == "manual"
            else None
        )
        payload = (
            "rrct-intention-base-configuration-v3",
            self.seed,
            self.observation_dim,
            self.workspace_dim,
            self.self_dim,
            self.projector_ranks,
            self.n_specialists,
            self.specialist_dim,
            self.recurrent_gain,
            self.closure_gain,
            self.self_feedback_gain,
            self.action_feedback_gain,
            self.feedback_mode,
            feedback_configuration,
            manual_feedback_state,
            self.ablations.disabled,
            int(horizon),
            int(query_budget),
            float(candidate_magnitude),
            float(forecast_decay),
            str(forecast_mode),
            float(max_delta_norm),
            np.asarray(predictor["prediction_weights"], dtype=np.float64),
            np.asarray(predictor["workspace_skip"], dtype=np.float64),
            np.asarray(forecaster["weights"], dtype=np.float64),
            np.asarray(forecaster["bias"], dtype=np.float64),
        )
        return hashlib.sha256(pickle.dumps(payload, protocol=5)).hexdigest()

    def _intention_configuration_key(
        self,
        *,
        horizon: int,
        query_budget: int,
        candidate_magnitude: float,
        forecast_decay: float,
        forecast_mode: str,
        max_delta_norm: float,
        selection_mode: str = "rollout",
    ) -> str:
        base_key = self._intention_base_configuration_key(
            horizon=horizon,
            query_budget=query_budget,
            candidate_magnitude=candidate_magnitude,
            forecast_decay=forecast_decay,
            forecast_mode=forecast_mode,
            max_delta_norm=max_delta_norm,
        )
        posterior_digest = (
            self.bayesian_transfer.posterior_digest()
            if selection_mode.startswith("bayesian_")
            else None
        )
        payload = (
            "rrct-intention-calibration-v2",
            base_key,
            str(selection_mode),
            posterior_digest,
        )
        return hashlib.sha256(pickle.dumps(payload, protocol=5)).hexdigest()

    def _validate_calibration_record(
        self, record: IntentionCalibrationRecord
    ) -> None:
        if not isinstance(record, IntentionCalibrationRecord):
            raise TypeError("calibration record has the wrong type")
        if record.sequence_id < 0 or record.horizon <= 0:
            raise ValueError("calibration sequence and horizon must be valid")
        if record.outcome_source not in {"live", "shadow"}:
            raise ValueError("calibration outcome_source must be 'live' or 'shadow'")
        if not record.calibration_key or not record.plan_state_digest:
            raise ValueError("calibration record digests must be nonempty")
        values = (
            record.predicted_improvement,
            record.realized_improvement,
            record.optimism,
            record.selected_delta_norm,
        )
        if not np.all(np.isfinite(values)) or record.selected_delta_norm < 0.0:
            raise ValueError("calibration record values must be finite and bounded")
        improvement_bound = 2.0 * np.sqrt(float(self.workspace_dim)) + 1e-9
        optimism_bound = 4.0 * np.sqrt(float(self.workspace_dim)) + 1e-9
        if (
            abs(record.predicted_improvement) > improvement_bound
            or abs(record.realized_improvement) > improvement_bound
            or abs(record.optimism) > optimism_bound
            or record.selected_delta_norm > 0.5 + 1e-9
        ):
            raise ValueError("calibration record exceeds architectural bounds")
        if not np.isclose(
            record.optimism,
            record.predicted_improvement - record.realized_improvement,
            atol=1e-12,
            rtol=1e-12,
        ):
            raise ValueError("calibration optimism does not match its components")

    def _append_intention_calibration_record(
        self, record: IntentionCalibrationRecord
    ) -> None:
        self._validate_calibration_record(record)
        if self._intention_calibration_key is None:
            self._intention_calibration_key = record.calibration_key
        elif self._intention_calibration_key != record.calibration_key:
            raise ValueError("calibration record does not match the retained configuration")
        expected_sequence = (
            self._intention_calibration_records[-1].sequence_id + 1
            if self._intention_calibration_records
            else 0
        )
        if record.sequence_id != expected_sequence:
            raise ValueError("calibration record sequence is not contiguous")
        self._intention_calibration_records.append(record)
        self._intention_calibration_records = self._intention_calibration_records[
            -self._intention_calibration_capacity:
        ]

    def intention_calibration_snapshot(self) -> dict[str, Any]:
        """Return bounded, auditable intention-transfer calibration state."""

        return {
            "schema_version": 1,
            "calibration_key": self._intention_calibration_key,
            "epoch": self._intention_calibration_epoch,
            "records": tuple(asdict(record) for record in self._intention_calibration_records),
            "capacity": self._intention_calibration_capacity,
            "count": len(self._intention_calibration_records),
            "last_reset_reason": self._intention_calibration_last_reset_reason,
            "digest": self._intention_calibration_digest(),
        }

    def load_intention_calibration_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        """Load a validated, provenance-preserving calibration snapshot."""

        if int(snapshot.get("schema_version", -1)) != 1:
            raise ValueError("unsupported intention-calibration schema")
        if int(snapshot.get("capacity", -1)) != self._intention_calibration_capacity:
            raise ValueError("calibration capacity does not match this agent")
        raw_records = tuple(snapshot.get("records", ()))
        if self.feedback_mode != "fixed" and raw_records:
            raise ValueError(
                "intention calibration evidence cannot load under adaptive feedback"
            )
        if len(raw_records) > self._intention_calibration_capacity:
            raise ValueError("calibration snapshot exceeds capacity")
        records = [IntentionCalibrationRecord(**dict(item)) for item in raw_records]
        calibration_key = snapshot.get("calibration_key")
        if calibration_key is not None and (
            not isinstance(calibration_key, str) or not calibration_key
        ):
            raise ValueError("calibration_key must be null or a nonempty string")
        if records and calibration_key is None:
            raise ValueError("nonempty calibration records require a calibration_key")
        for index, record in enumerate(records):
            self._validate_calibration_record(record)
            if record.calibration_key != calibration_key:
                raise ValueError("calibration records are misordered or mismatched")
            if index and record.sequence_id != records[index - 1].sequence_id + 1:
                raise ValueError("calibration records are misordered or mismatched")
        if int(snapshot.get("count", -1)) != len(records):
            raise ValueError("calibration snapshot count mismatch")
        epoch = snapshot.get("epoch", 0)
        if not np.isscalar(epoch) or int(epoch) != epoch or epoch < 0:
            raise ValueError("calibration epoch must be a nonnegative integer")
        reset_reason = snapshot.get("last_reset_reason")
        if reset_reason is not None and (
            not isinstance(reset_reason, str) or not reset_reason
        ):
            raise ValueError("last_reset_reason must be null or nonempty")
        candidate_payload = (
            1,
            int(epoch),
            calibration_key,
            tuple(records),
            self._intention_calibration_capacity,
            reset_reason,
        )
        expected_digest = hashlib.sha256(
            pickle.dumps(candidate_payload, protocol=5)
        ).hexdigest()
        if snapshot.get("digest") != expected_digest:
            raise ValueError("calibration snapshot digest mismatch")
        self._intention_calibration_records = records
        self._intention_calibration_key = calibration_key
        self._intention_calibration_epoch = int(epoch)
        self._intention_calibration_last_reset_reason = reset_reason

    def reset_intention_calibration(self, *, reason: str) -> dict[str, Any]:
        """Explicitly invalidate calibration and return an audit receipt."""

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("calibration reset requires a nonempty reason")
        old_digest = self._intention_calibration_digest()
        old_count = len(self._intention_calibration_records)
        old_epoch = self._intention_calibration_epoch
        self._intention_calibration_records = []
        self._intention_calibration_key = None
        self._intention_calibration_epoch += 1
        self._intention_calibration_last_reset_reason = reason.strip()
        return {
            "reason": self._intention_calibration_last_reset_reason,
            "time": self._time,
            "old_count": old_count,
            "new_count": 0,
            "old_epoch": old_epoch,
            "new_epoch": self._intention_calibration_epoch,
            "old_digest": old_digest,
            "new_digest": self._intention_calibration_digest(),
        }

    def predictor_snapshot(self) -> dict[str, Any]:
        """Return a copy of learned predictor weights for matched traces."""

        return self.self_model.predictor_snapshot()

    def load_predictor_snapshot(
        self,
        snapshot: Mapping[str, Any],
        *,
        freeze: bool = True,
    ) -> None:
        """Load exact predictor weights, normally freezing them immediately."""

        self.self_model.load_predictor_snapshot(snapshot, freeze=freeze)
        if self._intention_calibration_records:
            self.reset_intention_calibration(reason="self_predictor_replaced")
        if self.bayesian_transfer.observation_count:
            self.reset_bayesian_transfer(reason="self_predictor_replaced")
        if freeze:
            self._self_model_mode = "frozen"
        else:
            self._self_model_mode = (
                "train" if self.self_model.training else "frozen"
            )

    @property
    def causal_boundary_state(self) -> CausalBoundaryState | None:
        """Return an immutable copy of the private online boundary state."""

        if self.causal_boundary is None:
            return None
        return self.causal_boundary.state

    def bind_causal_sources(
        self,
        process_bank: ArrayLike,
        commitment: CausalHandleCommitment,
    ) -> BoundCausalTransition:
        """Bind sources after a step and before the world advances.

        The observation and time come from the completed RRCT step, while the
        supplied commitment must exactly match the agent-owned immutable
        commitment emitted by that step.  The next :meth:`step` atomically
        reveals the resulting transition with its own observation.
        """

        if self.causal_boundary is None:
            raise RuntimeError("this agent has no causal-boundary learner")
        if self._last_result is None:
            raise RuntimeError("step must emit a commitment before source binding")
        if not isinstance(commitment, CausalHandleCommitment):
            raise TypeError("commitment must be a CausalHandleCommitment")
        validated = self.causal_boundary.validate_pending_commitment(commitment)
        if (
            self._last_result.causal_commitment is None
            or validated.digest
            != self._last_result.causal_commitment.digest
            or validated.time != self._last_result.time
        ):
            raise ValueError("commitment does not belong to the latest RRCT step")
        return self.causal_boundary.bind_sources(
            self._last_result.observation,
            process_bank,
            commitment_digest=validated.digest,
            time=validated.time,
        )

    def causal_boundary_snapshot(self) -> dict[str, Any]:
        """Return the complete digest-protected online-boundary continuation."""

        if self.causal_boundary is None:
            raise RuntimeError("this agent has no causal-boundary learner")
        assert self._causal_access_readout is not None
        assert self._causal_boundary_projection is not None
        payload: dict[str, Any] = {
            "schema": self.CAUSAL_BOUNDARY_SNAPSHOT_SCHEMA,
            "agent_time": self._time,
            "causal_boundary_broadcast_gain": self.causal_boundary_broadcast_gain,
            "boundary_projection_digest": _causal_projection_digest(
                self._causal_boundary_projection
            ),
            "boundary": self.causal_boundary.snapshot(),
            "access_readout": self._causal_access_readout.snapshot(),
            "last_public_pair": self._last_public_causal_pair,
        }
        payload["digest"] = hashlib.sha256(
            pickle.dumps(payload, protocol=5)
        ).hexdigest()
        return copy.deepcopy(payload)

    def load_causal_boundary_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        """Load a validated configuration-matched boundary continuation."""

        if self.causal_boundary is None or self._causal_access_readout is None:
            raise RuntimeError("this agent has no causal-boundary learner")
        if not isinstance(snapshot, Mapping):
            raise TypeError("agent causal-boundary snapshot must be a mapping")
        payload = copy.deepcopy(dict(snapshot))
        observed_digest = payload.pop("digest", None)
        expected_digest = hashlib.sha256(
            pickle.dumps(payload, protocol=5)
        ).hexdigest()
        if not isinstance(observed_digest, str) or observed_digest != expected_digest:
            raise ValueError("agent causal-boundary snapshot digest mismatch")
        if payload.get("schema") != self.CAUSAL_BOUNDARY_SNAPSHOT_SCHEMA:
            raise ValueError("unsupported agent causal-boundary snapshot schema")
        raw_gain = payload.get("causal_boundary_broadcast_gain")
        if (
            isinstance(raw_gain, (bool, np.bool_))
            or not np.isscalar(raw_gain)
            or not np.isfinite(raw_gain)
            or float(raw_gain) != self.causal_boundary_broadcast_gain
        ):
            raise ValueError(
                "causal-boundary snapshot broadcast gain does not match"
            )
        assert self._causal_boundary_projection is not None
        expected_projection_digest = _causal_projection_digest(
            self._causal_boundary_projection
        )
        if payload.get("boundary_projection_digest") != expected_projection_digest:
            raise ValueError(
                "causal-boundary snapshot projection does not match"
            )
        agent_time = payload.get("agent_time")
        if (
            isinstance(agent_time, (bool, np.bool_))
            or not isinstance(agent_time, (int, np.integer))
            or int(agent_time) != self._time
        ):
            raise ValueError("causal-boundary snapshot agent_time does not match")
        boundary_candidate = OnlineCausalSelfBoundary(
            self.causal_boundary_config
        )
        boundary_candidate.load_snapshot(payload["boundary"])
        access_candidate = self._new_causal_access_readout()
        access_candidate.load_snapshot(payload["access_readout"])
        raw_pair = payload.get("last_public_pair")
        public_pair: tuple[int, int] | None = None
        if raw_pair is not None:
            if not isinstance(raw_pair, (tuple, list)) or len(raw_pair) != 2:
                raise ValueError("snapshot last_public_pair must have length two")
            if any(
                isinstance(item, (bool, np.bool_))
                or not isinstance(item, (int, np.integer))
                for item in raw_pair
            ):
                raise ValueError("snapshot last_public_pair must contain integers")
            public_pair = (int(raw_pair[0]), int(raw_pair[1]))
            if (
                not 0 <= public_pair[0] < self.causal_boundary_config.handle_count
                or not 0 <= public_pair[1] < self.causal_boundary_config.source_count
            ):
                raise ValueError("snapshot last_public_pair is out of bounds")
        prior_interruptions = self.causal_boundary.interrupted_transitions
        required_interruptions = max(
            boundary_candidate.interrupted_transitions,
            prior_interruptions,
        ) + int(self.causal_boundary.has_pending)
        missing_interruptions = (
            required_interruptions
            - boundary_candidate.interrupted_transitions
        )
        if missing_interruptions:
            boundary_candidate.record_interruption(missing_interruptions)
        self.causal_boundary = boundary_candidate
        self._causal_access_readout = access_candidate
        self._last_public_causal_pair = public_pair

    def freeze_causal_boundary(self) -> None:
        """Freeze online evidence updates while retaining earned state."""

        if self.causal_boundary is None:
            raise RuntimeError("this agent has no causal-boundary learner")
        self.causal_boundary.freeze()

    def unfreeze_causal_boundary(self) -> None:
        """Resume online evidence updates."""

        if self.causal_boundary is None:
            raise RuntimeError("this agent has no causal-boundary learner")
        self.causal_boundary.unfreeze()

    def reset_causal_boundary(self, *, retain_evidence: bool = False) -> None:
        """Explicitly erase the learned boundary and pending causal records."""

        if self.causal_boundary is None:
            raise RuntimeError("this agent has no causal-boundary learner")
        self.causal_boundary.clear_model(retain_evidence=retain_evidence)
        assert self._causal_access_readout is not None
        self._causal_access_readout.reset()
        self._last_public_causal_pair = None

    def choose_causal_port(self) -> tuple[int, int] | None:
        """Return the pair exposed to action systems by the latest broadcast.

        This deliberately returns no private updater state when the dedicated
        causal-boundary broadcast path or the whole workspace is ablated.
        """

        return self._last_public_causal_pair

    def reset(self, seed: int | None = None) -> None:
        """Clear dynamic state, optionally rebuilding parameters from ``seed``."""

        if seed is not None:
            old_bayesian_epoch = self._bayesian_transfer_epoch
            old_causal_interruptions = (
                self.causal_boundary.interrupted_transitions
                + int(self.causal_boundary.has_pending)
                if self.causal_boundary is not None
                else 0
            )
            self.seed = int(seed)
            self._build_components(self.seed)
            if self.causal_boundary is not None and old_causal_interruptions:
                self.causal_boundary.record_interruption(
                    old_causal_interruptions
                )
            self._bayesian_transfer_key = None
            self._bayesian_transfer_updates = []
            self._bayesian_transfer_epoch = old_bayesian_epoch + 1
            self._bayesian_transfer_last_reset_reason = "seeded_component_rebuild"
            self.reset_intention_calibration(reason="seeded_component_rebuild")
        else:
            if self.causal_boundary is not None:
                self.causal_boundary.reset_pending()
            for specialist in self.specialists:
                specialist.reset()
            self.workspace.reset()
            self.self_model.reset()
            self.observation_forecaster.reset()
            self.memory.reset()
            if self.feedback_regulator is not None:
                self.feedback_regulator.reset(
                    initial_recurrent_gain=self.recurrent_gain,
                    initial_closure_gain=self.closure_gain,
                )
        self._time = 0
        self._resolution_level = len(self.projectors) - 1
        self._last_action = np.zeros(self.action_dim, dtype=np.float64)
        self._last_result = None
        self._last_public_causal_pair = None

    def set_ablations(
        self,
        ablations: AblationFlags
        | str
        | Iterable[str]
        | Mapping[str, bool]
        | None,
        *,
        reset: bool = True,
    ) -> None:
        """Replace the experimental ablation set.

        Resetting by default prevents hidden state accumulated under one causal
        graph from contaminating a matched ablation run.
        """

        parsed = AblationFlags.parse(ablations)
        changed = parsed != self.ablations
        feedback_gate_changed = (
            parsed.feedback_adaptation != self.ablations.feedback_adaptation
        )
        recurrence_gate_changed = parsed.recurrence != self.ablations.recurrence
        self.ablations = parsed
        if changed and self._intention_calibration_records:
            self.reset_intention_calibration(reason="ablation_configuration_changed")
        if changed and self.bayesian_transfer.observation_count:
            self.reset_bayesian_transfer(reason="ablation_configuration_changed")
        if (
            (feedback_gate_changed or recurrence_gate_changed)
            and self.feedback_regulator is not None
        ):
            self.feedback_regulator.reset(
                initial_recurrent_gain=self.recurrent_gain,
                initial_closure_gain=self.closure_gain,
            )
        if reset:
            self.reset()

    def set_gains(
        self,
        recurrent_gain: float,
        closure_gain: float,
        *,
        reset: bool = True,
    ) -> None:
        """Set continuous recurrence and closure gains atomically.

        Both values must be finite and nonnegative, matching constructor
        validation.  ``reset=True`` clears core dynamic state while retaining
        learned predictor weights.  ``reset=False`` preserves core dynamic
        state, but a changed nominal pair reanchors the adaptive regulator and
        clears its control history.
        """

        parsed: dict[str, float] = {}
        for name, value in (
            ("recurrent_gain", recurrent_gain),
            ("closure_gain", closure_gain),
        ):
            if not np.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
            parsed[name] = float(value)
        changed = (
            parsed["recurrent_gain"] != self.recurrent_gain
            or parsed["closure_gain"] != self.closure_gain
        )
        if self.feedback_regulator is not None:
            for name, value in parsed.items():
                if not self.feedback_regulator.minimum_gain <= value <= self.feedback_regulator.maximum_gain:
                    raise ValueError(
                        f"{name} must lie within the adaptive feedback gain bounds"
                    )
        self.recurrent_gain = parsed["recurrent_gain"]
        self.closure_gain = parsed["closure_gain"]
        if changed and self.feedback_regulator is not None:
            self.feedback_regulator.reset(
                initial_recurrent_gain=self.recurrent_gain,
                initial_closure_gain=self.closure_gain,
            )
        if changed and self._intention_calibration_records:
            self.reset_intention_calibration(reason="recurrence_or_closure_gain_changed")
        if changed and self.bayesian_transfer.observation_count:
            self.reset_bayesian_transfer(reason="recurrence_or_closure_gain_changed")
        if reset:
            self.reset()

    def set_path_gains(
        self,
        self_feedback_gain: float,
        action_feedback_gain: float,
        *,
        reset: bool = True,
    ) -> None:
        """Atomically set the two explicit closure-path multipliers.

        The shared :attr:`closure_gain` remains unchanged.  Reset semantics
        match :meth:`set_gains`: a reset clears dynamic state but retains any
        learned predictor parameters, while ``reset=False`` supports matched
        continuation from the current state.
        """

        parsed: dict[str, float] = {}
        for name, value in (
            ("self_feedback_gain", self_feedback_gain),
            ("action_feedback_gain", action_feedback_gain),
        ):
            if not np.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
            parsed[name] = float(value)
        changed = (
            parsed["self_feedback_gain"] != self.self_feedback_gain
            or parsed["action_feedback_gain"] != self.action_feedback_gain
        )
        self.self_feedback_gain = parsed["self_feedback_gain"]
        self.action_feedback_gain = parsed["action_feedback_gain"]
        if changed and self._intention_calibration_records:
            self.reset_intention_calibration(reason="closure_path_gain_changed")
        if changed and self.bayesian_transfer.observation_count:
            self.reset_bayesian_transfer(reason="closure_path_gain_changed")
        if reset:
            self.reset()

    def _observation(self, values: ArrayLike) -> FloatArray:
        observation = np.asarray(values, dtype=np.float64)
        if observation.shape != (self.observation_dim,):
            raise ValueError(
                "observation must have shape "
                f"({self.observation_dim},), got {observation.shape}"
            )
        if not np.all(np.isfinite(observation)):
            raise ValueError("observation must contain only finite values")
        return observation

    def step(
        self,
        observation: ArrayLike,
        *,
        source: str = "external",
        perturb_workspace: ArrayLike | None = None,
        emit_causal_commitment: bool = True,
    ) -> StepResult:
        """Advance the complete recursive causal loop by one observation.

        The selected resolution is applied now.  The self-model and
        counterfactual controller then choose ``next_resolution_level`` for the
        following step. ``perturb_workspace`` is additive and affects every
        causally downstream component in the current step.  When configured,
        the same observation first reveals the previously bound causal
        transition, then traverses the ordinary RRCT loop.  A fresh
        agent-owned commitment is emitted only after that loop completes.
        ``emit_causal_commitment=False`` is the terminal form of the same
        recursive step: it reveals any prior bound transition and runs the
        complete loop, but deliberately leaves no successor causal work.
        """

        if not isinstance(source, str) or not source:
            raise ValueError("source must be a nonempty string")
        if not isinstance(emit_causal_commitment, (bool, np.bool_)):
            raise ValueError("emit_causal_commitment must be boolean")
        x = self._observation(observation)
        external_feedback: FloatArray | None = None
        if perturb_workspace is not None:
            external_feedback = np.asarray(perturb_workspace, dtype=np.float64)
            if external_feedback.shape != (self.workspace_dim,):
                raise ValueError(
                    f"perturb_workspace must have shape ({self.workspace_dim},)"
                )
            if not np.all(np.isfinite(external_feedback)):
                raise ValueError("perturb_workspace must contain only finite values")
        causal_update_receipt: CausalBoundaryUpdateReceipt | None = None
        bound_causal_bank: FloatArray | None = None
        bound_causal_handles: FloatArray | None = None
        if self.causal_boundary is not None:
            if self.causal_boundary.has_pending_commitment:
                raise RuntimeError(
                    "bind_causal_sources must bind the emitted commitment "
                    "before the next step"
                )
            if self.causal_boundary.has_bound_transition:
                bound_causal_bank = self.causal_boundary.bound_process_bank
                bound_causal_handles = self.causal_boundary.bound_handles
                assert bound_causal_bank is not None
                assert bound_causal_handles is not None
                transition_digest = self.causal_boundary.pending_transition_digest
                assert transition_digest is not None
                causal_update_receipt = self.causal_boundary.reveal_outcome(
                    x,
                    transition_digest=transition_digest,
                    time=self._time,
                )

        previous_workspace_state = self.workspace.state.copy()
        step_recurrent_gain = self.effective_recurrent_gain
        step_closure_gain = self.effective_closure_gain
        step_self_feedback_gain = (
            0.0
            if self.ablations.recurrence
            else step_closure_gain * self.self_feedback_gain
        )
        step_action_feedback_gain = (
            0.0
            if self.ablations.recurrence
            else step_closure_gain * self.action_feedback_gain
        )
        self.observation_forecaster.observe(x)
        if self.ablations.resolution:
            current_level = len(self.projectors) - 1
        else:
            current_level = self._resolution_level
        resolved = self.projectors.project(x, current_level)
        details = self.projectors.decompose(x)
        detail_norms = np.asarray(
            [np.linalg.norm(component) for component in details], dtype=np.float64
        )

        recurrence = not self.ablations.recurrence
        broadcast_enabled = not self.ablations.broadcast
        previous_broadcast = (
            step_recurrent_gain * self.workspace.state
            if broadcast_enabled
            else np.zeros(self.workspace_dim, dtype=np.float64)
        )
        proposals = []
        for specialist in self.specialists:
            signal = (
                details[specialist.level]
                if specialist.level <= current_level
                else np.zeros(self.observation_dim, dtype=np.float64)
            )
            proposals.append(
                specialist.process(
                    signal,
                    broadcast=previous_broadcast,
                    recurrence=recurrence,
                    recurrent_gain=step_recurrent_gain,
                )
            )

        internal_feedback = np.zeros(self.workspace_dim, dtype=np.float64)
        causal_boundary_state: CausalBoundaryState | None = None
        causal_boundary_descriptor = np.zeros(0, dtype=np.float64)
        causal_boundary_proposal_state = np.zeros(
            self.specialist_dim, dtype=np.float64
        )
        causal_boundary_workspace_drive = np.zeros(
            self.workspace_dim, dtype=np.float64
        )
        causal_boundary_candidate_signal = np.zeros(0, dtype=np.float64)
        causal_public_pair: tuple[int, int] | None = None
        causal_boundary_proposal_selected = False
        causal_access_confidence = 0.0
        causal_access_updated = False
        if broadcast_enabled:
            if (
                not self.ablations.self_model
                and step_self_feedback_gain
            ):
                internal_feedback += step_self_feedback_gain * (
                    self._self_feedback @ self.self_model.state
                )
            if step_action_feedback_gain:
                internal_feedback += step_action_feedback_gain * (
                    self._action_feedback @ self._last_action
                )
        if self.causal_boundary is not None:
            causal_boundary_state = self.causal_boundary.state
            causal_boundary_descriptor = self.causal_boundary.descriptor(
                x,
                bound_causal_bank,
                bound_causal_handles,
            )
            if bound_causal_bank is None:
                causal_boundary_candidate_signal = np.zeros(
                    self.causal_boundary.config.process_dim,
                    dtype=np.float64,
                )
            else:
                assert bound_causal_handles is not None
                causal_boundary_candidate_signal = (
                    self.causal_boundary.candidate_signal(
                        bound_causal_bank,
                        bound_causal_handles,
                    )
                )
            boundary_path_enabled = bool(
                broadcast_enabled
                and not self.ablations.causal_boundary_broadcast
                and self._causal_boundary_projection is not None
            )
            if boundary_path_enabled:
                causal_boundary_proposal_state = np.tanh(
                    self.causal_boundary_broadcast_gain
                    * self._causal_boundary_projection
                    @ causal_boundary_descriptor
                )
                proposal_norm = float(
                    np.linalg.norm(causal_boundary_proposal_state)
                )
                proposal_confidence = float(
                    causal_boundary_state.confidence
                    if causal_boundary_state.active
                    else 0.20 * causal_boundary_state.uncertainty
                )
                proposals.append(
                    SpecialistOutput(
                        name="causal_boundary",
                        level=current_level,
                        state=causal_boundary_proposal_state.copy(),
                        salience=(0.75 + proposal_confidence) * proposal_norm,
                        confidence=proposal_confidence,
                        reconstruction_error=1.0 - proposal_confidence,
                    )
                )
        if external_feedback is not None:
            internal_feedback += external_feedback

        workspace_result = self.workspace.step(
            proposals,
            recurrence=recurrence,
            recurrent_gain=step_recurrent_gain,
            enabled=broadcast_enabled,
            perturbation=internal_feedback if broadcast_enabled else None,
        )
        workspace_state = workspace_result.state
        causal_boundary_proposal_selected = bool(
            "causal_boundary" in workspace_result.selected
        )
        if causal_boundary_proposal_selected:
            selected_index = workspace_result.selected.index("causal_boundary")
            causal_boundary_workspace_drive = np.asarray(
                workspace_result.weights[selected_index]
                * (
                    self.workspace._proposal_weights
                    @ causal_boundary_proposal_state
                ),
                dtype=np.float64,
            )

        self_enabled = not self.ablations.self_model
        if self_enabled:
            predicted_workspace = self.self_model.predict_workspace()
        else:
            predicted_workspace = np.zeros(self.workspace_dim, dtype=np.float64)
        prediction_error = workspace_state - predicted_workspace
        # Learning is opt-in and gated by both mode and self-model presence.
        # It occurs after the one-step error has been recorded and before the
        # self-state consumes the new workspace.
        self.self_model.learn_workspace(
            workspace_state,
            enabled=self_enabled,
        )

        memory_enabled = not self.ablations.memory
        if memory_enabled:
            memory_result = self.memory.retrieve(workspace_state)
        else:
            memory_result = MemoryRead(
                vector=np.zeros(self.workspace_dim, dtype=np.float64),
                indices=(),
                similarities=np.zeros(0, dtype=np.float64),
                weights=np.zeros(0, dtype=np.float64),
            )
        self_state = self.self_model.update(
            workspace_state,
            memory_result.vector,
            prediction_error,
            recurrence=recurrence,
            recurrent_gain=step_recurrent_gain,
            enabled=self_enabled,
        )

        if (
            self.causal_boundary is not None
            and self._causal_access_readout is not None
            and causal_boundary_proposal_selected
            and np.linalg.norm(causal_boundary_proposal_state) > 1e-10
        ):
            access_features = np.concatenate((workspace_state, self_state))
            attempted_pair = None
            if causal_boundary_state is not None and causal_boundary_state.active:
                attempted_pair = (
                    int(causal_boundary_state.selected_handle_index),
                    int(causal_boundary_state.selected_source_index),
                )
            if self.causal_access_readout_mode == "direct_candidate":
                # This is an internal transport operation, not a learned
                # classifier.  Authorization remains downstream and must be
                # grounded in experienced consequences.
                causal_public_pair = attempted_pair
                causal_access_confidence = (
                    0.0
                    if causal_boundary_state is None
                    else float(causal_boundary_state.confidence)
                )
                causal_access_updated = False
            else:
                access_prediction: CausalAccessPrediction = (
                    self._causal_access_readout.predict(access_features)
                )
                causal_public_pair = access_prediction.pair
                causal_access_confidence = access_prediction.confidence
                self._causal_access_readout.update(
                    access_features,
                    attempted_pair,
                )
                causal_access_updated = True

        memory_written = False
        if memory_enabled and broadcast_enabled:
            memory_written = self.memory.write(
                workspace_state,
                time=self._time,
                source=source,
            )

        decision = self.controller.choose(
            x,
            self.projectors,
            current_level=current_level,
            workspace=workspace_state,
            self_state=self_state,
            memory=memory_result.vector,
            prediction_error=prediction_error,
            resolution_enabled=not self.ablations.resolution,
        )
        next_level = (
            len(self.projectors) - 1
            if self.ablations.resolution
            else decision.resolution_level
        )
        specialist_states = np.stack(
            [proposal.state for proposal in proposals], axis=0
        )
        specialist_salience = np.asarray(
            [proposal.salience for proposal in proposals], dtype=np.float64
        )
        feedback_telemetry: FeedbackTelemetry | None = None
        if (
            self.feedback_mode == "adaptive"
            and self.feedback_regulator is not None
            and not self.ablations.feedback_adaptation
            and not self.ablations.recurrence
        ):
            feedback_telemetry = compute_feedback_telemetry(
                specialist_states=specialist_states,
                specialist_salience=specialist_salience,
                workspace=workspace_state,
                prediction_error=prediction_error,
                previous_workspace=previous_workspace_state,
                workspace_proposal_states=workspace_result.proposal_states,
                workspace_weights=workspace_result.weights,
            )
            self.feedback_regulator.update(feedback_telemetry)
        next_recurrent_gain = self.effective_recurrent_gain
        next_closure_gain = self.effective_closure_gain
        causal_commitment: CausalHandleCommitment | None = None
        causal_access_update_count = 0
        causal_interrupted_transitions = 0
        if self.causal_boundary is not None and bool(emit_causal_commitment):
            causal_commitment = self.causal_boundary.commit_handles(
                time=self._time
            )
        if self.causal_boundary is not None:
            causal_interrupted_transitions = (
                self.causal_boundary.interrupted_transitions
            )
            assert self._causal_access_readout is not None
            causal_access_update_count = self._causal_access_readout.update_count
        result = StepResult(
            time=self._time,
            source=source,
            observation=x.copy(),
            resolved=resolved.copy(),
            resolution_level=current_level,
            next_resolution_level=next_level,
            resolution_rank=self.projectors.ranks[current_level],
            next_resolution_rank=self.projectors.ranks[next_level],
            detail_norms=detail_norms,
            specialist_states=np.asarray(specialist_states, dtype=np.float64),
            specialist_salience=specialist_salience,
            workspace_proposal_states=workspace_result.proposal_states.copy(),
            workspace_weights=workspace_result.weights.copy(),
            workspace=workspace_state.copy(),
            selected_specialists=workspace_result.selected,
            self_state=self_state.copy(),
            memory_read=memory_result.vector.copy(),
            memory_indices=memory_result.indices,
            memory_written=memory_written,
            predicted_workspace=predicted_workspace.copy(),
            prediction_error=prediction_error.copy(),
            error_norm=float(np.linalg.norm(prediction_error)),
            action=decision.action.copy(),
            action_scores=decision.action_scores.copy(),
            resolution_scores=decision.resolution_scores.copy(),
            ablations=self.ablations.disabled,
            applied_recurrent_gain=step_recurrent_gain,
            applied_closure_gain=step_closure_gain,
            next_recurrent_gain=next_recurrent_gain,
            next_closure_gain=next_closure_gain,
            feedback_telemetry=feedback_telemetry,
            causal_boundary_state=causal_boundary_state,
            causal_boundary_descriptor=causal_boundary_descriptor.copy(),
            causal_boundary_proposal_state=causal_boundary_proposal_state.copy(),
            causal_boundary_workspace_drive=causal_boundary_workspace_drive.copy(),
            causal_boundary_candidate_signal=causal_boundary_candidate_signal.copy(),
            causal_commitment_digest=(
                causal_commitment.digest
                if causal_commitment is not None
                else None
            ),
            causal_transition_digest=(
                causal_update_receipt.transition_digest
                if causal_update_receipt is not None
                else None
            ),
            causal_boundary_update_receipt=copy.deepcopy(
                causal_update_receipt
            ),
            causal_public_pair=causal_public_pair,
            causal_commitment=causal_commitment,
            causal_boundary_proposal_selected=causal_boundary_proposal_selected,
            causal_access_confidence=causal_access_confidence,
            causal_access_updated=causal_access_updated,
            causal_access_update_count=causal_access_update_count,
            causal_interrupted_transitions=causal_interrupted_transitions,
        )
        # A terminal reveal still computes the controller's internal proposal
        # as part of the ordinary recursive step, but no motor command is
        # emitted.  Preserve the last actually executed action so snapshots do
        # not record an unexecuted terminal proposal as action feedback.
        if bool(emit_causal_commitment):
            self._last_action = decision.action.copy()
        self._last_public_causal_pair = causal_public_pair
        self._resolution_level = next_level
        self._last_result = result
        self._time += 1
        return result

    def register_executed_action(self, action: ArrayLike) -> FloatArray:
        """Register the motor command actually sent to the environment.

        This supports hierarchical or metacognitive action modulation while
        keeping the next recurrent action-feedback cycle aligned with the
        executed command.  It does not advance time or alter any other state.
        """

        value = np.asarray(action, dtype=np.float64)
        if value.shape != (self.action_dim,):
            raise ValueError(f"action must have shape ({self.action_dim},)")
        if not np.all(np.isfinite(value)):
            raise ValueError("action must contain only finite values")
        self._last_action = np.clip(value, -1.0, 1.0).copy()
        return self._last_action.copy()

    def choose_action(self) -> FloatArray:
        """Return the most recently selected/executed action, or zeros before stepping."""

        return self._last_action.copy()

    def counterfactual_self_query(
        self,
        self_delta: ArrayLike,
        observations: Sequence[ArrayLike],
        *,
        max_delta_norm: float = 0.5,
    ) -> SelfCounterfactualQuery:
        """Simulate a self-state intervention without mutating the live agent.

        The query clones the complete current dynamical state, applies the
        proposed change only to one clone, and advances both through the same
        supplied future observations. It therefore exposes prospective causal
        self-access rather than a generated verbal self-description.
        """

        delta = np.asarray(self_delta, dtype=np.float64)
        if delta.shape != (self.self_dim,) or not np.all(np.isfinite(delta)):
            raise ValueError(f"self_delta must be finite with shape ({self.self_dim},)")
        if not np.isfinite(max_delta_norm) or max_delta_norm <= 0.0:
            raise ValueError("max_delta_norm must be finite and positive")
        if float(np.linalg.norm(delta)) > max_delta_norm + 1e-15:
            raise ValueError("self_delta exceeds max_delta_norm")
        future = tuple(self._observation(values).copy() for values in observations)
        if not future:
            raise ValueError("at least one future observation is required")
        baseline = copy.deepcopy(self)
        intervened = copy.deepcopy(self)
        intervened.self_model.state += delta
        baseline_steps = [baseline.step(x, source="self_counterfactual_query") for x in future]
        intervened_steps = [intervened.step(x, source="self_counterfactual_query") for x in future]
        baseline_workspace = np.stack([step.workspace for step in baseline_steps])
        intervened_workspace = np.stack([step.workspace for step in intervened_steps])
        baseline_actions = np.stack([step.action for step in baseline_steps])
        intervened_actions = np.stack([step.action for step in intervened_steps])
        return SelfCounterfactualQuery(
            self_delta=delta.copy(),
            baseline_workspace=baseline_workspace,
            intervened_workspace=intervened_workspace,
            workspace_delta=intervened_workspace - baseline_workspace,
            baseline_actions=baseline_actions,
            intervened_actions=intervened_actions,
            action_delta=intervened_actions - baseline_actions,
            baseline_resolutions=tuple(step.next_resolution_level for step in baseline_steps),
            intervened_resolutions=tuple(step.next_resolution_level for step in intervened_steps),
            baseline_self_states=np.stack([step.self_state for step in baseline_steps]),
            intervened_self_states=np.stack([step.self_state for step in intervened_steps]),
            baseline_prediction_errors=np.stack([step.prediction_error for step in baseline_steps]),
            intervened_prediction_errors=np.stack([step.prediction_error for step in intervened_steps]),
        )

    def select_self_counterfactual(
        self,
        candidates: Sequence[ArrayLike],
        observations: Sequence[ArrayLike],
        objective: ArrayLike,
        *,
        max_delta_norm: float = 0.5,
    ) -> tuple[int, tuple[float, ...], tuple[SelfCounterfactualQuery, ...]]:
        """Select the candidate whose prospective workspace best meets an objective."""

        target = np.asarray(objective, dtype=np.float64)
        if target.shape != (self.workspace_dim,) or not np.all(np.isfinite(target)):
            raise ValueError(f"objective must be finite with shape ({self.workspace_dim},)")
        candidate_values = tuple(candidates)
        if not candidate_values:
            raise ValueError("at least one candidate is required")
        future = tuple(self._observation(values).copy() for values in observations)
        if not future:
            raise ValueError("at least one future observation is required")
        queries = tuple(
            self.counterfactual_self_query(
                delta, future, max_delta_norm=max_delta_norm
            )
            for delta in candidate_values
        )
        scores = tuple(float(query.intervened_workspace[-1] @ target) for query in queries)
        return int(np.argmax(np.asarray(scores))), scores, queries

    def execute_self_counterfactual(
        self,
        candidates: Sequence[ArrayLike],
        observations: Sequence[ArrayLike],
        objective: ArrayLike,
        *,
        max_delta_norm: float = 0.5,
        realized_observations: Sequence[ArrayLike] | None = None,
    ) -> SelfDirectedPlan:
        """Select, commit, and audit a bounded prospective self intervention.

        Unlike :meth:`counterfactual_self_query`, this operation intentionally
        advances the live agent. The prospective winner is applied to the live
        self state, the supplied future is executed, and prediction error is
        retained explicitly.
        """

        if not np.isfinite(max_delta_norm) or max_delta_norm <= 0.0:
            raise ValueError("max_delta_norm must be finite and positive")
        future = tuple(self._observation(values).copy() for values in observations)
        candidate_values = tuple(np.asarray(value, dtype=np.float64) for value in candidates)
        for delta in candidate_values:
            if delta.shape != (self.self_dim,) or not np.all(np.isfinite(delta)):
                raise ValueError(f"each candidate must be finite with shape ({self.self_dim},)")
            if float(np.linalg.norm(delta)) > max_delta_norm + 1e-15:
                raise ValueError("candidate exceeds max_delta_norm")
        selected, scores, queries = self.select_self_counterfactual(
            candidate_values, future, objective, max_delta_norm=max_delta_norm
        )
        realized_future = (
            future
            if realized_observations is None
            else tuple(self._observation(values).copy() for values in realized_observations)
        )
        if not realized_future:
            raise ValueError("at least one realized observation is required")
        self.self_model.state += candidate_values[selected]
        realized_steps = tuple(
            self.step(observation, source="executed_self_counterfactual")
            for observation in realized_future
        )
        target = np.asarray(objective, dtype=np.float64)
        realized_score = float(realized_steps[-1].workspace @ target)
        predicted_score = float(scores[selected])
        return SelfDirectedPlan(
            selected_index=selected,
            predicted_scores=scores,
            predicted_score=predicted_score,
            realized_score=realized_score,
            prediction_error=abs(realized_score - predicted_score),
            query=queries[selected],
            realized_steps=realized_steps,
        )

    def _endogenous_state_digest(self) -> str:
        return hashlib.sha256(pickle.dumps(self, protocol=5)).hexdigest()

    @staticmethod
    def _endogenous_plan_content_digest(plan: EndogenousSelfPlan) -> str:
        if not isinstance(plan, EndogenousSelfPlan):
            raise TypeError("plan must be an EndogenousSelfPlan")
        canonical = replace(plan, plan_content_digest="")
        return hashlib.sha256(pickle.dumps(canonical, protocol=5)).hexdigest()

    @classmethod
    def _verify_endogenous_plan_content(cls, plan: EndogenousSelfPlan) -> None:
        if not isinstance(plan.plan_content_digest, str) or not plan.plan_content_digest:
            raise ValueError("endogenous plan content digest is missing")
        if plan.plan_content_digest != cls._endogenous_plan_content_digest(plan):
            raise RuntimeError("endogenous plan content changed after planning")

    @staticmethod
    def _bounded_rms(values: ArrayLike) -> float:
        bounded = np.tanh(np.asarray(values, dtype=np.float64))
        if bounded.size == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(bounded))))

    def _bayesian_transfer_features(
        self,
        *,
        query: SelfCounterfactualQuery,
        proxy_score: float,
        proxy_scale: float,
        forecast: FloatArray,
        max_delta_norm: float,
    ) -> FloatArray:
        """Construct the fixed bounded precommit-only 20-coordinate map."""

        if self._last_result is None:
            raise RuntimeError("transfer features require a prior agent step")
        delta = np.asarray(query.self_delta, dtype=np.float64)
        delta_norm = float(np.linalg.norm(delta))
        activity = delta_norm / float(max_delta_norm)
        if activity == 0.0:
            return np.zeros(len(self.BAYESIAN_TRANSFER_FEATURE_NAMES), dtype=np.float64)
        state = np.asarray(self._last_result.self_state, dtype=np.float64)
        state_norm = float(np.linalg.norm(state))
        alignment = (
            float(state @ delta) / (state_norm * delta_norm)
            if state_norm > 0.0
            else 0.0
        )
        normalized_proxy = (
            float(proxy_score) / float(proxy_scale) if proxy_scale > 0.0 else 0.0
        )
        error_scale = self.bayesian_transfer_improvement_scale
        baseline_norms = np.linalg.norm(
            query.baseline_prediction_errors, axis=1
        )
        intervened_norms = np.linalg.norm(
            query.intervened_prediction_errors, axis=1
        )
        predicted_benefits = (
            baseline_norms - intervened_norms
        ) / error_scale
        baseline_error = float(np.mean(baseline_norms) / error_scale)
        if predicted_benefits.size > 1:
            benefit_trend = float(
                (predicted_benefits[-1] - predicted_benefits[0]) / 2.0
            )
        else:
            benefit_trend = 0.0
        forecast_bounded = np.tanh(np.asarray(forecast, dtype=np.float64))
        forecast_roughness = (
            float(
                np.sqrt(np.mean(np.square(np.diff(forecast_bounded, axis=0))))
            )
            / 2.0
            if forecast_bounded.shape[0] > 1
            else 0.0
        )
        departure_difference = (
            forecast_bounded[0] - np.tanh(self._last_result.observation)
        )
        departure = float(
            np.sqrt(np.mean(np.square(departure_difference))) / 2.0
        )
        resolution_divergence = float(
            np.mean(
                np.asarray(query.baseline_resolutions)
                != np.asarray(query.intervened_resolutions)
            )
        )
        raw = np.asarray(
            [
                self._bounded_rms(self._last_result.prediction_error),
                self._bounded_rms(self._last_result.workspace),
                self._bounded_rms(self._last_result.self_state),
                self._bounded_rms(self.observation_forecaster.last_error),
                1.0,
                alignment,
                normalized_proxy,
                baseline_error,
                float(np.mean(predicted_benefits)),
                float(np.min(predicted_benefits)),
                float(predicted_benefits[-1]),
                benefit_trend,
                float(np.std(predicted_benefits)),
                self._bounded_rms(query.workspace_delta),
                self._bounded_rms(query.action_delta),
                self._bounded_rms(
                    query.intervened_self_states - query.baseline_self_states
                ),
                resolution_divergence,
                float(np.sqrt(np.mean(np.square(forecast_bounded)))),
                forecast_roughness,
                departure,
            ],
            dtype=np.float64,
        )
        features = activity * raw
        if not np.all(np.isfinite(features)):
            raise FloatingPointError("Bayesian transfer features became nonfinite")
        if np.any(np.abs(features) > 1.0 + 1e-12):
            raise FloatingPointError("Bayesian transfer features exceeded their proof bound")
        return np.clip(features, -1.0, 1.0)

    def plan_endogenous_self_intention(
        self,
        *,
        horizon: int = 4,
        query_budget: int = 8,
        candidate_magnitude: float = 0.35,
        forecast_decay: float = 0.85,
        forecast_mode: str = "learned",
        selection_mode: str = "rollout",
        bayesian_confidence: float = 0.95,
        calibration_mode: str = "off",
        calibration_alpha: float = 0.05,
        calibration_min_samples: int = 19,
        minimum_effect: float = 0.0,
        max_delta_norm: float = 0.5,
    ) -> EndogenousSelfPlan:
        """Purely plan a bounded epistemic self-regulation intervention."""

        if self._last_result is None:
            raise RuntimeError("an endogenous intention requires at least one prior step")
        if isinstance(horizon, (bool, np.bool_)) or not np.isscalar(horizon) or not np.isfinite(horizon) or int(horizon) != horizon or horizon <= 0:
            raise ValueError("horizon must be a positive integer")
        if isinstance(query_budget, (bool, np.bool_)) or not np.isscalar(query_budget) or not np.isfinite(query_budget) or int(query_budget) != query_budget or not 2 <= query_budget <= 25:
            raise ValueError("query_budget must be an integer from 2 through 25")
        if (
            not np.isfinite(max_delta_norm)
            or max_delta_norm <= 0.0
            or max_delta_norm > 0.5
        ):
            raise ValueError("max_delta_norm must lie in (0, 0.5]")
        if not np.isfinite(candidate_magnitude) or candidate_magnitude <= 0.0 or candidate_magnitude > max_delta_norm:
            raise ValueError("candidate_magnitude must be finite, positive, and no larger than max_delta_norm")
        if not np.isfinite(forecast_decay) or not 0.0 <= forecast_decay <= 1.0:
            raise ValueError("forecast_decay must lie in [0, 1]")
        if forecast_mode not in {"learned", "decay"}:
            raise ValueError("forecast_mode must be 'learned' or 'decay'")
        if selection_mode not in {"always_zero", "rollout", "bayesian_mean", "bayesian_credible"}:
            raise ValueError(
                "selection_mode must be 'always_zero', 'rollout', "
                "'bayesian_mean', or 'bayesian_credible'"
            )
        if (
            isinstance(bayesian_confidence, (bool, np.bool_))
            or not np.isscalar(bayesian_confidence)
            or not np.isfinite(bayesian_confidence)
            or not 0.5 < float(bayesian_confidence) < 1.0
        ):
            raise ValueError("bayesian_confidence must lie strictly between 0.5 and 1")
        if calibration_mode not in {"off", "explore", "conservative"}:
            raise ValueError("calibration_mode must be 'off', 'explore', or 'conservative'")
        if self.feedback_mode != "fixed" and (
            selection_mode.startswith("bayesian_") or calibration_mode != "off"
        ):
            raise ValueError(
                "adaptive feedback currently supports only uncalibrated rollout planning"
            )
        if not np.isfinite(minimum_effect) or minimum_effect < 0.0:
            raise ValueError("minimum_effect must be finite and nonnegative")
        self._conformal_optimism_threshold(
            (),
            alpha=calibration_alpha,
            minimum_records=calibration_min_samples,
        )
        state_digest = self._endogenous_state_digest()
        coordinates = np.arange(self.self_dim, dtype=np.float64)
        directions = np.asarray([
            np.cos(np.pi * (coordinates + 0.5) * frequency / self.self_dim)
            for frequency in range(self.self_dim)
        ], dtype=np.float64)
        directions /= np.linalg.norm(directions, axis=1, keepdims=True)
        candidates = np.asarray(
            [np.zeros(self.self_dim)] + [
                sign * candidate_magnitude * direction
                for direction in directions for sign in (1.0, -1.0)
            ], dtype=np.float64
        )
        current_error = self._last_result.prediction_error
        proxy_scores = np.asarray([
            float(current_error @ (self._self_feedback @ delta))
            for delta in candidates
        ], dtype=np.float64)
        nonzero_order = np.argsort(proxy_scores[1:], kind="stable") + 1
        queried_indices = (0,) + tuple(int(index) for index in nonzero_order[: int(query_budget) - 1])
        last_observation = self._last_result.observation
        forecast = (
            self.observation_forecaster.forecast(int(horizon))
            if forecast_mode == "learned"
            else np.stack([
                forecast_decay ** (lag + 1) * last_observation
                for lag in range(int(horizon))
            ])
        )
        queries = tuple(
            self.counterfactual_self_query(candidates[index], forecast, max_delta_norm=max_delta_norm)
            for index in queried_indices
        )
        predicted_errors = tuple(
            float(np.mean(np.linalg.norm(query.intervened_prediction_errors, axis=1)))
            for query in queries
        )
        zero_query = queries[0]
        predicted_baseline_error = float(np.mean(np.linalg.norm(zero_query.baseline_prediction_errors, axis=1)))
        rollout_benefits = np.asarray(
            [predicted_baseline_error - error for error in predicted_errors],
            dtype=np.float64,
        )
        simulator_position = int(np.argmax(rollout_benefits))
        simulator_selected_index = queried_indices[simulator_position]
        proxy_scale = float(np.max(np.abs(proxy_scores[1:])))
        bayesian_features = np.stack(
            [
                self._bayesian_transfer_features(
                    query=query,
                    proxy_score=float(proxy_scores[candidate_index]),
                    proxy_scale=proxy_scale,
                    forecast=forecast,
                    max_delta_norm=float(max_delta_norm),
                )
                for query, candidate_index in zip(queries, queried_indices)
            ]
        )
        bayesian_means: list[float] = []
        bayesian_standard_deviations: list[float] = []
        bayesian_probabilities_positive: list[float] = []
        bayesian_lower_bounds: list[float] = []
        for position, features in enumerate(bayesian_features):
            if queried_indices[position] == 0:
                bayesian_means.append(0.0)
                bayesian_standard_deviations.append(0.0)
                bayesian_probabilities_positive.append(0.5)
                bayesian_lower_bounds.append(0.0)
                continue
            prediction = self.bayesian_transfer.predict(features)
            bayesian_means.append(
                float(rollout_benefits[position])
                + prediction.mean * self.bayesian_transfer_target_scale
            )
            bayesian_standard_deviations.append(
                np.sqrt(prediction.variance)
                * self.bayesian_transfer_target_scale
            )
            bayesian_probabilities_positive.append(
                prediction.probability_above(
                    -float(rollout_benefits[position])
                    / self.bayesian_transfer_target_scale
                )
            )
            bayesian_lower_bounds.append(
                float(rollout_benefits[position])
                + prediction.lower_bound(float(bayesian_confidence))
                * self.bayesian_transfer_target_scale
            )
        transfer_key = self._intention_base_configuration_key(
            horizon=int(horizon),
            # The posterior may be fit on the complete candidate pool and then
            # applied to any deterministic shortlist from that same pool.
            query_budget=0,
            candidate_magnitude=float(candidate_magnitude),
            forecast_decay=float(forecast_decay),
            forecast_mode=forecast_mode,
            max_delta_norm=float(max_delta_norm),
        )
        if (
            selection_mode.startswith("bayesian_")
            and self.bayesian_transfer.observation_count > 0
            and self._bayesian_transfer_key != transfer_key
        ):
            raise RuntimeError(
                "retained Bayesian transfer posterior does not match this "
                "intention configuration"
            )
        if selection_mode == "always_zero":
            selection_scores = np.zeros_like(rollout_benefits)
            predicted_means = selection_scores
        elif selection_mode == "rollout":
            selection_scores = rollout_benefits
            predicted_means = rollout_benefits
        elif selection_mode == "bayesian_mean":
            selection_scores = np.asarray(bayesian_means, dtype=np.float64)
            predicted_means = selection_scores
        else:
            selection_scores = np.asarray(bayesian_lower_bounds, dtype=np.float64)
            predicted_means = np.asarray(bayesian_means, dtype=np.float64)
        raw_position = int(np.argmax(selection_scores))
        raw_selected_index = queried_indices[raw_position]
        raw_predicted_improvement = float(predicted_means[raw_position])
        calibration_key = self._intention_configuration_key(
            horizon=int(horizon),
            query_budget=int(query_budget),
            candidate_magnitude=float(candidate_magnitude),
            forecast_decay=float(forecast_decay),
            forecast_mode=forecast_mode,
            max_delta_norm=float(max_delta_norm),
            selection_mode=selection_mode,
        )
        if (
            calibration_mode != "off"
            and self._intention_calibration_records
            and self._intention_calibration_key != calibration_key
        ):
            raise RuntimeError(
                "retained calibration does not match this intention configuration"
            )
        optimism_values = tuple(
            record.optimism for record in self._intention_calibration_records
        )
        calibration_ready, threshold = self._conformal_optimism_threshold(
            optimism_values,
            alpha=float(calibration_alpha),
            minimum_records=int(calibration_min_samples),
        )
        conservative_lower_bound: float | None = (
            raw_predicted_improvement - float(threshold)
            if threshold is not None
            else None
        )
        abstained = False
        abstention_reason: str | None = None
        if selection_mode == "always_zero":
            abstained = True
            abstention_reason = "control_policy"
        elif selection_mode.startswith("bayesian_"):
            best_nonzero_score = float(np.max(selection_scores[1:]))
            if self.bayesian_transfer.observation_count == 0:
                abstained = True
                abstention_reason = "bayesian_posterior_not_ready"
            elif raw_selected_index == 0 and best_nonzero_score <= float(minimum_effect):
                abstained = True
                abstention_reason = (
                    "bayesian_lower_bound_not_above_minimum_effect"
                    if selection_mode == "bayesian_credible"
                    else "bayesian_mean_not_above_minimum_effect"
                )
            elif raw_selected_index != 0 and not float(
                selection_scores[raw_position]
            ) > float(minimum_effect):
                abstained = True
                abstention_reason = (
                    "bayesian_lower_bound_not_above_minimum_effect"
                    if selection_mode == "bayesian_credible"
                    else "bayesian_mean_not_above_minimum_effect"
                )
        if calibration_mode == "conservative" and raw_selected_index != 0:
            if not calibration_ready:
                abstained = True
                abstention_reason = "calibration_not_ready"
            elif not float(conservative_lower_bound) > float(minimum_effect):
                abstained = True
                abstention_reason = "lower_bound_not_above_minimum_effect"
        selected_index = 0 if abstained else raw_selected_index
        selected_position = queried_indices.index(selected_index)
        plan = EndogenousSelfPlan(
            state_digest=state_digest,
            candidate_deltas=candidates.copy(),
            proxy_scores=proxy_scores.copy(),
            queried_indices=queried_indices,
            selected_index=selected_index,
            raw_selected_index=raw_selected_index,
            selected_delta=candidates[selected_index].copy(),
            predicted_candidate_errors=predicted_errors,
            predicted_baseline_error=predicted_baseline_error,
            predicted_selected_error=predicted_errors[selected_position],
            forecast_observations=forecast.copy(),
            forecast_mode=forecast_mode,
            horizon=int(horizon),
            calibration_mode=calibration_mode,
            calibration_key=calibration_key,
            calibration_digest=self._intention_calibration_digest(),
            calibration_count=len(self._intention_calibration_records),
            calibration_ready=calibration_ready,
            calibration_alpha=float(calibration_alpha),
            calibration_min_samples=int(calibration_min_samples),
            minimum_effect=float(minimum_effect),
            uncertainty_threshold=(float(threshold) if threshold is not None else None),
            conservative_lower_bound=conservative_lower_bound,
            raw_predicted_improvement=raw_predicted_improvement,
            predicted_improvement=(
                0.0
                if selected_index == 0
                else float(predicted_means[selected_position])
            ),
            abstained=abstained,
            abstention_reason=abstention_reason,
            selection_mode=selection_mode,
            simulator_selected_index=simulator_selected_index,
            bayesian_confidence=float(bayesian_confidence),
            bayesian_transfer_key=transfer_key,
            bayesian_model_digest=self.bayesian_transfer.posterior_digest(),
            bayesian_observation_count=self.bayesian_transfer.observation_count,
            bayesian_effective_sample_count=self.bayesian_transfer.effective_sample_count,
            bayesian_features=bayesian_features.copy(),
            bayesian_means=tuple(float(value) for value in bayesian_means),
            bayesian_standard_deviations=tuple(
                float(value) for value in bayesian_standard_deviations
            ),
            bayesian_probabilities_positive=tuple(
                float(value) for value in bayesian_probabilities_positive
            ),
            bayesian_lower_bounds=tuple(
                float(value) for value in bayesian_lower_bounds
            ),
            plan_content_digest="",
            queries=queries,
        )
        return replace(
            plan,
            plan_content_digest=self._endogenous_plan_content_digest(plan),
        )

    def record_shadow_bayesian_transfer(
        self,
        plan: EndogenousSelfPlan,
        observations: Sequence[ArrayLike],
    ) -> BayesianTransferUpdate:
        """Condition only after a literal future is revealed on private branches.

        Every queried nonzero candidate is retained.  Candidates that share the
        same suffix receive equal fractional weights summing to one, preventing
        a single revealed future from masquerading as independent episodes.
        """

        if not isinstance(plan, EndogenousSelfPlan):
            raise TypeError("plan must be an EndogenousSelfPlan")
        self._verify_endogenous_plan_content(plan)
        if self._endogenous_state_digest() != plan.state_digest:
            raise RuntimeError("stale endogenous plan cannot train transfer")
        if (
            self._self_model_mode != "frozen"
            or self.self_model.training
            or self.observation_forecaster.training
        ):
            raise RuntimeError("Bayesian transfer requires frozen predictors")
        if not self.bayesian_transfer.training:
            raise RuntimeError("Bayesian transfer model is frozen")
        if self._intention_calibration_records:
            raise RuntimeError("Bayesian transfer cannot train after calibration")
        if plan.bayesian_model_digest != self.bayesian_transfer.posterior_digest():
            raise RuntimeError("Bayesian posterior changed after planning")
        if (
            self._bayesian_transfer_key is not None
            and self._bayesian_transfer_key != plan.bayesian_transfer_key
        ):
            raise RuntimeError("plan does not match the retained transfer configuration")
        future = tuple(self._observation(values).copy() for values in observations)
        if len(future) != plan.horizon:
            raise ValueError("transfer observations must equal the planned horizon")

        baseline_trial = copy.deepcopy(self)
        baseline_steps = tuple(
            baseline_trial.step(x, source="shadow_bayesian_transfer_baseline")
            for x in future
        )
        realized_baseline = float(np.mean([step.error_norm for step in baseline_steps]))
        candidate_indices: list[int] = []
        features: list[FloatArray] = []
        targets: list[float] = []
        for position, candidate_index in enumerate(plan.queried_indices):
            if candidate_index == 0:
                continue
            trial = copy.deepcopy(self)
            delta = np.asarray(plan.candidate_deltas[candidate_index], dtype=np.float64)
            trial.self_model.state += delta
            steps = tuple(
                trial.step(x, source="shadow_bayesian_transfer_candidate")
                for x in future
            )
            realized_error = float(np.mean([step.error_norm for step in steps]))
            realized_improvement = realized_baseline - realized_error
            rollout_prediction = (
                plan.predicted_baseline_error
                - plan.predicted_candidate_errors[position]
            )
            normalized_target = (
                realized_improvement - rollout_prediction
            ) / self.bayesian_transfer_target_scale
            if abs(normalized_target) > 1.0 + 1e-12:
                raise FloatingPointError("transfer target exceeded its proof bound")
            candidate_indices.append(int(candidate_index))
            features.append(np.asarray(plan.bayesian_features[position]).copy())
            targets.append(float(np.clip(normalized_target, -1.0, 1.0)))
        if not candidate_indices:
            raise RuntimeError("Bayesian transfer requires a queried nonzero candidate")
        per_candidate_weight = 1.0 / len(candidate_indices)
        count_before = self.bayesian_transfer.observation_count
        effective_before = self.bayesian_transfer.effective_sample_count
        digest_before = self.bayesian_transfer.posterior_digest()
        self.bayesian_transfer.observe_batch(
            np.stack(features),
            np.asarray(targets, dtype=np.float64),
            weights=np.full(len(targets), per_candidate_weight, dtype=np.float64),
        )
        self._bayesian_transfer_key = plan.bayesian_transfer_key
        update = BayesianTransferUpdate(
            sequence_id=len(self._bayesian_transfer_updates),
            transfer_key=plan.bayesian_transfer_key,
            evidence_digest=plan.plan_content_digest,
            planned_time=self._time,
            recorded_time=self._time,
            feature_episode_index=None,
            target_episode_index=None,
            target_candidate_indices=tuple(candidate_indices),
            permutation_digest=None,
            candidate_indices=tuple(candidate_indices),
            normalized_targets=tuple(targets),
            per_candidate_weight=per_candidate_weight,
            observation_count_before=count_before,
            observation_count_after=self.bayesian_transfer.observation_count,
            effective_sample_count_before=effective_before,
            effective_sample_count_after=self.bayesian_transfer.effective_sample_count,
            posterior_digest_before=digest_before,
            posterior_digest_after=self.bayesian_transfer.posterior_digest(),
            outcome_source="shadow",
        )
        self._bayesian_transfer_updates.append(update)
        return update

    def record_shadow_intention_calibration(
        self,
        plan: EndogenousSelfPlan,
        observations: Sequence[ArrayLike],
    ) -> IntentionCalibrationRecord:
        """Calibrate from a revealed future on private, non-live branches.

        The retained value is the largest optimism across the queried nonzero
        candidates.  This is deliberately conservative for the within-plan
        candidate selection step and is labeled ``shadow`` in the audit log.
        The live dynamical state is unchanged; only calibration state mutates.
        """

        if not isinstance(plan, EndogenousSelfPlan):
            raise TypeError("plan must be an EndogenousSelfPlan")
        self._verify_endogenous_plan_content(plan)
        if plan.calibration_mode != "explore":
            raise ValueError("shadow calibration requires calibration_mode='explore'")
        if self._endogenous_state_digest() != plan.state_digest:
            raise RuntimeError("stale endogenous plan cannot calibrate")
        if (
            self._self_model_mode != "frozen"
            or self.self_model.training
            or self.observation_forecaster.training
            or (
                plan.selection_mode.startswith("bayesian_")
                and self.bayesian_transfer.training
            )
        ):
            raise RuntimeError("calibration requires frozen predictors")
        future = tuple(self._observation(values).copy() for values in observations)
        if len(future) != plan.horizon:
            raise ValueError("calibration observations must equal the planned horizon")

        baseline_trial = copy.deepcopy(self)
        baseline_steps = tuple(
            baseline_trial.step(x, source="shadow_intention_baseline") for x in future
        )
        realized_baseline = float(
            np.mean([step.error_norm for step in baseline_steps])
        )
        candidate_records: list[tuple[float, float, float, int, float]] = []
        for position, candidate_index in enumerate(plan.queried_indices):
            if candidate_index == 0:
                continue
            trial = copy.deepcopy(self)
            delta = np.asarray(
                plan.candidate_deltas[candidate_index], dtype=np.float64
            )
            trial.self_model.state += delta
            steps = tuple(
                trial.step(x, source="shadow_intention_candidate") for x in future
            )
            realized_error = float(np.mean([step.error_norm for step in steps]))
            predicted_improvement = (
                plan.predicted_baseline_error
                - plan.predicted_candidate_errors[position]
                if plan.selection_mode == "rollout"
                else plan.bayesian_means[position]
            )
            realized_improvement = realized_baseline - realized_error
            optimism = predicted_improvement - realized_improvement
            candidate_records.append(
                (
                    optimism,
                    predicted_improvement,
                    realized_improvement,
                    int(candidate_index),
                    float(np.linalg.norm(delta)),
                )
            )
        if not candidate_records:
            raise RuntimeError("shadow calibration requires a queried nonzero candidate")
        (
            optimism,
            predicted_improvement,
            realized_improvement,
            selected_index,
            selected_delta_norm,
        ) = max(candidate_records, key=lambda item: item[0])
        record = IntentionCalibrationRecord(
            sequence_id=(
                self._intention_calibration_records[-1].sequence_id + 1
                if self._intention_calibration_records
                else 0
            ),
            calibration_key=plan.calibration_key,
            plan_state_digest=plan.state_digest,
            planned_time=self._time,
            recorded_time=self._time,
            predicted_improvement=float(predicted_improvement),
            realized_improvement=float(realized_improvement),
            optimism=float(optimism),
            selected_index=selected_index,
            selected_delta_norm=selected_delta_norm,
            horizon=plan.horizon,
            forecast_mode=plan.forecast_mode,
            outcome_source="shadow",
        )
        self._append_intention_calibration_record(record)
        return record

    def commit_endogenous_self_intention(self, plan: EndogenousSelfPlan) -> EndogenousCommitReceipt:
        """Atomically commit a still-current endogenous plan without stepping."""

        if not isinstance(plan, EndogenousSelfPlan):
            raise TypeError("plan must be an EndogenousSelfPlan")
        self._verify_endogenous_plan_content(plan)
        current_digest = self._endogenous_state_digest()
        if current_digest != plan.state_digest:
            raise RuntimeError("stale endogenous plan: live state changed after planning")
        baseline = copy.deepcopy(self)
        self.self_model.state += np.asarray(plan.selected_delta, dtype=np.float64)
        return EndogenousCommitReceipt(
            plan=plan,
            precommit_state_digest=current_digest,
            postcommit_state_digest=self._endogenous_state_digest(),
            committed_time=self._time,
            _baseline_agent=baseline,
        )

    def evaluate_committed_intention(
        self,
        receipt: EndogenousCommitReceipt,
        observations: Sequence[ArrayLike],
        *,
        update_calibration: bool = True,
    ) -> EndogenousSelfIntention:
        """Evaluate a committed plan transactionally on a revealed future."""

        if not isinstance(receipt, EndogenousCommitReceipt):
            raise TypeError("receipt must be an EndogenousCommitReceipt")
        if not isinstance(update_calibration, (bool, np.bool_)):
            raise ValueError("update_calibration must be boolean")
        if self._endogenous_state_digest() != receipt.postcommit_state_digest:
            raise RuntimeError("committed intention is stale")
        future = tuple(self._observation(values).copy() for values in observations)
        if not future:
            raise ValueError("at least one realized observation is required")
        plan = receipt.plan
        self._verify_endogenous_plan_content(plan)
        calibration_update_eligible = (
            bool(update_calibration)
            and
            plan.calibration_mode in {"explore", "conservative"}
            and plan.selected_index != 0
        )
        if plan.calibration_mode in {"explore", "conservative"}:
            if len(future) != plan.horizon:
                raise ValueError(
                    "calibrated evaluation observations must equal the planned horizon"
                )
            if (
                self._self_model_mode != "frozen"
                or self.self_model.training
                or self.observation_forecaster.training
                or (
                    plan.selection_mode.startswith("bayesian_")
                    and self.bayesian_transfer.training
                )
            ):
                raise RuntimeError("calibrated evaluation requires frozen predictors")
        baseline_trial = copy.deepcopy(receipt._baseline_agent)
        selected_trial = copy.deepcopy(self)
        baseline_steps = tuple(baseline_trial.step(x, source="endogenous_self_baseline") for x in future)
        realized_steps = tuple(selected_trial.step(x, source="endogenous_self_intention") for x in future)
        realized_baseline_error = float(np.mean([step.error_norm for step in baseline_steps]))
        realized_selected_error = float(np.mean([step.error_norm for step in realized_steps]))
        realized_improvement = realized_baseline_error - realized_selected_error
        if calibration_update_eligible:
            record = IntentionCalibrationRecord(
                sequence_id=(
                    selected_trial._intention_calibration_records[-1].sequence_id + 1
                    if selected_trial._intention_calibration_records
                    else 0
                ),
                calibration_key=plan.calibration_key,
                plan_state_digest=plan.state_digest,
                planned_time=receipt.committed_time,
                recorded_time=selected_trial._time,
                predicted_improvement=plan.predicted_improvement,
                realized_improvement=realized_improvement,
                optimism=plan.predicted_improvement - realized_improvement,
                selected_index=plan.selected_index,
                selected_delta_norm=float(np.linalg.norm(plan.selected_delta)),
                horizon=plan.horizon,
                forecast_mode=plan.forecast_mode,
                outcome_source="live",
            )
            selected_trial._append_intention_calibration_record(record)
        self.__dict__.clear()
        self.__dict__.update(selected_trial.__dict__)
        return EndogenousSelfIntention(
            candidate_count=int(plan.candidate_deltas.shape[0]),
            queried_count=len(plan.queries),
            queried_indices=plan.queried_indices,
            selected_index=plan.selected_index,
            selected_delta=plan.selected_delta.copy(),
            predicted_candidate_errors=plan.predicted_candidate_errors,
            predicted_baseline_error=plan.predicted_baseline_error,
            predicted_selected_error=plan.predicted_selected_error,
            realized_baseline_error=realized_baseline_error,
            realized_selected_error=realized_selected_error,
            realized_improvement=realized_improvement,
            prediction_error=abs(realized_selected_error - plan.predicted_selected_error),
            forecast_observations=plan.forecast_observations.copy(),
            realized_steps=realized_steps,
        )

    def execute_endogenous_self_intention(
        self,
        *,
        horizon: int = 4,
        query_budget: int = 8,
        candidate_magnitude: float = 0.35,
        forecast_decay: float = 0.85,
        forecast_mode: str = "learned",
        selection_mode: str = "rollout",
        bayesian_confidence: float = 0.95,
        calibration_mode: str = "off",
        calibration_alpha: float = 0.05,
        calibration_min_samples: int = 19,
        minimum_effect: float = 0.0,
        max_delta_norm: float = 0.5,
        realized_observations: Sequence[ArrayLike] | None = None,
    ) -> EndogenousSelfIntention:
        """Convenience wrapper for pure plan, atomic commit, then evaluation."""

        plan = self.plan_endogenous_self_intention(
            horizon=horizon,
            query_budget=query_budget,
            candidate_magnitude=candidate_magnitude,
            forecast_decay=forecast_decay,
            forecast_mode=forecast_mode,
            selection_mode=selection_mode,
            bayesian_confidence=bayesian_confidence,
            calibration_mode=calibration_mode,
            calibration_alpha=calibration_alpha,
            calibration_min_samples=calibration_min_samples,
            minimum_effect=minimum_effect,
            max_delta_norm=max_delta_norm,
        )
        if calibration_mode != "off" and realized_observations is None:
            raise ValueError(
                "calibration requires explicitly revealed realized_observations"
            )
        receipt = self.commit_endogenous_self_intention(plan)
        future = plan.forecast_observations if realized_observations is None else realized_observations
        return self.evaluate_committed_intention(receipt, future)

    def snapshot(self) -> dict[str, Any]:
        """Return a deep-copy diagnostic snapshot of current dynamic state."""

        return {
            "time": self._time,
            "seed": self.seed,
            "ablations": self.ablations.disabled,
            "recurrent_gain": self.recurrent_gain,
            "current_recurrent_gain": self.current_recurrent_gain,
            "effective_recurrent_gain": self.effective_recurrent_gain,
            "closure_gain": self.closure_gain,
            "current_closure_gain": self.current_closure_gain,
            "effective_closure_gain": self.effective_closure_gain,
            "self_feedback_gain": self.self_feedback_gain,
            "effective_self_feedback_gain": self.effective_self_feedback_gain,
            "action_feedback_gain": self.action_feedback_gain,
            "effective_action_feedback_gain": self.effective_action_feedback_gain,
            "self_model_mode": self.self_model_mode,
            "self_learning_updates": self.self_learning_updates,
            "observation_forecaster_learning_steps": self.observation_forecaster.learning_steps,
            "observation_forecaster_observed_count": self.observation_forecaster.observed_count,
            "observation_forecaster_last_observation": self.observation_forecaster.last_observation.copy(),
            "intention_calibration_count": len(self._intention_calibration_records),
            "intention_calibration_key": self._intention_calibration_key,
            "intention_calibration_epoch": self._intention_calibration_epoch,
            "intention_calibration_digest": self._intention_calibration_digest(),
            "bayesian_transfer_training": self.bayesian_transfer.training,
            "bayesian_transfer_observation_count": self.bayesian_transfer.observation_count,
            "bayesian_transfer_effective_sample_count": self.bayesian_transfer.effective_sample_count,
            "bayesian_transfer_key": self._bayesian_transfer_key,
            "bayesian_transfer_epoch": self._bayesian_transfer_epoch,
            "bayesian_transfer_posterior_digest": self.bayesian_transfer.posterior_digest(),
            "bayesian_transfer_digest": self._bayesian_transfer_digest(),
            "feedback": self.feedback_snapshot(),
            "causal_boundary": (
                self.causal_boundary.snapshot()
                if self.causal_boundary is not None
                else None
            ),
            "causal_access_readout": (
                self._causal_access_readout.snapshot()
                if self._causal_access_readout is not None
                else None
            ),
            "causal_boundary_broadcast_gain": self.causal_boundary_broadcast_gain,
            "causal_access_readout_mode": self.causal_access_readout_mode,
            "causal_access_memory_capacity": self.causal_access_memory_capacity,
            "causal_access_neighbors": self.causal_access_neighbors,
            "causal_access_prototype_learning_rate": (
                self.causal_access_prototype_learning_rate
            ),
            "causal_public_pair": self._last_public_causal_pair,
            "causal_interrupted_transitions": (
                self.causal_boundary.interrupted_transitions
                if self.causal_boundary is not None
                else 0
            ),
            "resolution_level": self._resolution_level,
            "resolution_rank": self.projectors.ranks[self._resolution_level],
            "projector_ranks": self.projectors.ranks,
            "specialist_states": np.stack(
                [specialist.state.copy() for specialist in self.specialists], axis=0
            ),
            "workspace": self.workspace.state.copy(),
            "self_state": self.self_model.state.copy(),
            "memory": self.memory.snapshot(),
            "last_action": self._last_action.copy(),
            "last_result": self._last_result,
        }


__all__ = ["AblationFlags", "BayesianTransferUpdate", "CausalBoundaryConfig", "CausalBoundaryState", "CausalBoundaryUpdateReceipt", "CausalHandleCommitment", "EndogenousCommitReceipt", "EndogenousSelfIntention", "EndogenousSelfPlan", "FloatArray", "IntentionCalibrationRecord", "RRCTAgent", "SelfCounterfactualQuery", "SelfDirectedPlan", "StepResult"]
