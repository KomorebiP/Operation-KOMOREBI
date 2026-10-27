"""Registered repeated-relator witness audit for Neuralese v0.3.0.

This module is intentionally separate from the exact completion rectangle.  It
evaluates the longer adversarial histories frozen in ``PREREGISTRATION.json``
without fitting parameters or claiming exhaustive coverage at those depths.

The public entry point, :func:`run_relator_witness`, consumes one checkpoint's
weights and its already-constructed eight-episode D4 batch.  Results are JSON
serializable.  Set ``retain_case_arrays=True`` only when the caller has a
compressed sidecar sink; the aggregate output always retains every discovered
hard counterexample and the complete first-reveal histogram.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from checkpoint_io import LinearOperatorWeights
from core import EpisodeBatch, N_OPERATORS, N_STATES, encode_tables, sample_batch


SCHEMA = "komorebi.neuralese.completion_surface.relator_witness.v1"
BASE_HISTORY_DEPTH = 6
EPISODES_PER_CHECKPOINT = 8
MAX_SUFFIX_HORIZON = 8
MINIMUM_PRE_NORMALIZATION_NORM = 1e-12

REGISTERED_RELATIONS: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("r4", (0, 0, 0, 0)),
    ("f2", (1, 1)),
    ("frfr", (1, 0, 1, 0)),
    ("rfrf", (0, 1, 0, 1)),
)
REGISTERED_REPEAT_CANDIDATES: tuple[int, ...] = (1, 2, 4, 8, 16, 32)
MAX_INSERTED_TOKENS = 64


class NumericalExecutionError(ArithmeticError):
    """Raised on a registered zero-norm or non-finite execution event."""


@dataclass(frozen=True)
class RelationConfiguration:
    relation: str
    relation_word: tuple[int, ...]
    repeat_count: int
    inserted_token_budget: int
    identity_word: tuple[int, ...]
    control_word: tuple[int, ...]


@dataclass(frozen=True)
class _BaselineShell:
    hidden: np.ndarray
    semantic: np.ndarray
    logits: np.ndarray
    probabilities: np.ndarray
    prediction: np.ndarray
    target_margin: np.ndarray


@dataclass(frozen=True)
class _ShellMeasurements:
    pair_equal: np.ndarray
    strict_correct: dict[str, np.ndarray]
    argmax_correct: dict[str, np.ndarray]
    margins: dict[str, np.ndarray]
    loop_minus_baseline_margin: np.ndarray
    control_baseline_disagree: np.ndarray
    unit_ray_l2: np.ndarray
    positive_ray_angle: np.ndarray
    probability_difference: np.ndarray
    centered_logit_difference: np.ndarray
    centered_logit_absmax: float


@dataclass
class _MetricAccumulator:
    """Exact finite accumulator for one suffix scope."""

    case_count: int
    suffix_count: int = 0
    pair_equal_count: int = 0
    pair_case_all: np.ndarray = field(init=False)
    strict_correct_count: dict[str, int] = field(init=False)
    argmax_correct_count: dict[str, int] = field(init=False)
    strict_case_all: dict[str, np.ndarray] = field(init=False)
    margin_chunks: dict[str, list[np.ndarray]] = field(init=False)
    margin_case_min: dict[str, np.ndarray] = field(init=False)
    margin_delta_chunks: list[np.ndarray] = field(default_factory=list)
    margin_delta_case_min: np.ndarray = field(init=False)
    control_disagree_count: int = 0
    control_case_all_disagree: np.ndarray = field(init=False)
    ray_l2_chunks: list[np.ndarray] = field(default_factory=list)
    ray_l2_case_sumsq: np.ndarray = field(init=False)
    ray_l2_case_max: np.ndarray = field(init=False)
    angle_chunks: list[np.ndarray] = field(default_factory=list)
    angle_case_max: np.ndarray = field(init=False)
    probability_case_sumsq: np.ndarray = field(init=False)
    probability_case_max: np.ndarray = field(init=False)
    centered_case_sumsq: np.ndarray = field(init=False)
    centered_case_max: np.ndarray = field(init=False)
    centered_logit_absmax: float = 1.0

    def __post_init__(self) -> None:
        interfaces = ("baseline", "identity_loop", "matched_control")
        self.pair_case_all = np.ones(self.case_count, dtype=bool)
        self.strict_correct_count = {name: 0 for name in interfaces}
        self.argmax_correct_count = {name: 0 for name in interfaces}
        self.strict_case_all = {
            name: np.ones(self.case_count, dtype=bool) for name in interfaces
        }
        self.margin_chunks = {name: [] for name in interfaces}
        self.margin_case_min = {
            name: np.full(self.case_count, np.inf, dtype=np.float64)
            for name in interfaces
        }
        self.margin_delta_case_min = np.full(
            self.case_count, np.inf, dtype=np.float64
        )
        self.control_case_all_disagree = np.ones(self.case_count, dtype=bool)
        self.ray_l2_case_sumsq = np.zeros(self.case_count, dtype=np.float64)
        self.ray_l2_case_max = np.zeros(self.case_count, dtype=np.float64)
        self.angle_case_max = np.zeros(self.case_count, dtype=np.float64)
        self.probability_case_sumsq = np.zeros(self.case_count, dtype=np.float64)
        self.probability_case_max = np.zeros(self.case_count, dtype=np.float64)
        self.centered_case_sumsq = np.zeros(self.case_count, dtype=np.float64)
        self.centered_case_max = np.zeros(self.case_count, dtype=np.float64)

    def update(self, shell: _ShellMeasurements) -> None:
        width = int(shell.pair_equal.shape[1])
        expected_2d = (self.case_count, width)
        if shell.pair_equal.shape != expected_2d:
            raise ValueError("paired-decision shell has an invalid shape")

        self.suffix_count += width
        self.pair_equal_count += int(np.sum(shell.pair_equal))
        self.pair_case_all &= np.all(shell.pair_equal, axis=1)

        for name in ("baseline", "identity_loop", "matched_control"):
            strict = shell.strict_correct[name]
            argmax = shell.argmax_correct[name]
            margins = shell.margins[name]
            if strict.shape != expected_2d or argmax.shape != expected_2d:
                raise ValueError(f"{name} correctness shell has an invalid shape")
            if margins.shape != expected_2d:
                raise ValueError(f"{name} margin shell has an invalid shape")
            _require_finite(f"{name} margins", margins)
            self.strict_correct_count[name] += int(np.sum(strict))
            self.argmax_correct_count[name] += int(np.sum(argmax))
            self.strict_case_all[name] &= np.all(strict, axis=1)
            self.margin_chunks[name].append(margins.reshape(-1).copy())
            self.margin_case_min[name] = np.minimum(
                self.margin_case_min[name], np.min(margins, axis=1)
            )

        margin_delta = shell.loop_minus_baseline_margin
        if margin_delta.shape != expected_2d:
            raise ValueError("loop-minus-baseline margin shell has an invalid shape")
        _require_finite("loop-minus-baseline margin", margin_delta)
        self.margin_delta_chunks.append(margin_delta.reshape(-1).copy())
        self.margin_delta_case_min = np.minimum(
            self.margin_delta_case_min, np.min(margin_delta, axis=1)
        )

        control_disagree = shell.control_baseline_disagree
        if control_disagree.shape != expected_2d:
            raise ValueError("control disagreement shell has an invalid shape")
        self.control_disagree_count += int(np.sum(control_disagree))
        self.control_case_all_disagree &= np.all(control_disagree, axis=1)

        ray_l2 = shell.unit_ray_l2
        angle = shell.positive_ray_angle
        if ray_l2.shape != expected_2d or angle.shape != expected_2d:
            raise ValueError("ray diagnostic shell has an invalid shape")
        _require_finite("unit-ray L2", ray_l2)
        _require_finite("positive-ray angle", angle)
        self.ray_l2_chunks.append(ray_l2.reshape(-1).copy())
        self.angle_chunks.append(angle.reshape(-1).copy())
        self.ray_l2_case_sumsq += np.sum(np.square(ray_l2), axis=1)
        self.ray_l2_case_max = np.maximum(self.ray_l2_case_max, np.max(ray_l2, axis=1))
        self.angle_case_max = np.maximum(self.angle_case_max, np.max(angle, axis=1))

        probability = shell.probability_difference
        centered = shell.centered_logit_difference
        expected_3d = (self.case_count, width, N_STATES)
        if probability.shape != expected_3d or centered.shape != expected_3d:
            raise ValueError("soft paired shell has an invalid shape")
        _require_finite("probability difference", probability)
        _require_finite("centered-logit difference", centered)
        probability_abs = np.abs(probability)
        centered_abs = np.abs(centered)
        self.probability_case_sumsq += np.sum(np.square(probability), axis=(1, 2))
        self.centered_case_sumsq += np.sum(np.square(centered), axis=(1, 2))
        self.probability_case_max = np.maximum(
            self.probability_case_max, np.max(probability_abs, axis=(1, 2))
        )
        self.centered_case_max = np.maximum(
            self.centered_case_max, np.max(centered_abs, axis=(1, 2))
        )
        self.centered_logit_absmax = max(
            self.centered_logit_absmax, float(shell.centered_logit_absmax)
        )

    def summary(self, horizon: int, scope: str) -> dict[str, Any]:
        if self.suffix_count <= 0:
            raise ArithmeticError("cannot summarize an empty suffix scope")
        decision_count = self.case_count * self.suffix_count

        interfaces: dict[str, Any] = {}
        for name in ("baseline", "identity_loop", "matched_control"):
            margins = np.concatenate(self.margin_chunks[name])
            interfaces[name] = {
                "semantic_accuracy": _finite_ratio(
                    self.strict_correct_count[name], decision_count
                ),
                "argmax_accuracy": _finite_ratio(
                    self.argmax_correct_count[name], decision_count
                ),
                "all_decisions_correct_case_fraction": _finite_ratio(
                    int(np.sum(self.strict_case_all[name])), self.case_count
                ),
                "all_target_margins_strictly_positive": bool(np.all(margins > 0.0)),
                "target_margin": _distribution_summary(margins),
            }

        probability_denominator = self.suffix_count * N_STATES
        probability_case_rms = np.sqrt(
            self.probability_case_sumsq / probability_denominator
        )
        centered_case_rms = np.sqrt(
            self.centered_case_sumsq / probability_denominator
        )
        ray_case_rms = np.sqrt(self.ray_l2_case_sumsq / self.suffix_count)
        _require_finite("probability case RMS", probability_case_rms)
        _require_finite("centered-logit case RMS", centered_case_rms)
        _require_finite("unit-ray case RMS", ray_case_rms)

        centered_tolerance = 1e-10 * max(1.0, self.centered_logit_absmax)
        summary = {
            "scope": scope,
            "horizon": int(horizon),
            "base_case_count": int(self.case_count),
            "suffixes_per_case": int(self.suffix_count),
            "decision_count": int(decision_count),
            "identity_loop_vs_baseline": {
                "hard_signature_survival_fraction": _finite_ratio(
                    int(np.sum(self.pair_case_all)), self.case_count
                ),
                "paired_decision_agreement_fraction": _finite_ratio(
                    self.pair_equal_count, decision_count
                ),
            },
            "interfaces": interfaces,
            "loop_minus_baseline_margin": _distribution_summary(
                np.concatenate(self.margin_delta_chunks)
            ),
            "matched_control_vs_baseline": {
                "prediction_disagreement_fraction": _finite_ratio(
                    self.control_disagree_count, decision_count
                ),
                "all_predictions_disagree_case_fraction": _finite_ratio(
                    int(np.sum(self.control_case_all_disagree)), self.case_count
                ),
            },
            "paired_path": {
                "unit_ray_l2": {
                    **_distribution_summary(np.concatenate(self.ray_l2_chunks)),
                    "scalar_rms": _finite_float(
                        np.sqrt(np.sum(self.ray_l2_case_sumsq) / decision_count)
                    ),
                    "maximum_case_rms": _finite_float(np.max(ray_case_rms)),
                    "maximum_case_coordinate": _finite_float(
                        np.max(self.ray_l2_case_max)
                    ),
                },
                "positive_ray_angle": {
                    **_distribution_summary(np.concatenate(self.angle_chunks)),
                    "maximum_case_angle": _finite_float(np.max(self.angle_case_max)),
                },
                "probability": {
                    "scalar_normalized_rms": _finite_float(
                        np.sqrt(
                            np.sum(self.probability_case_sumsq)
                            / (decision_count * N_STATES)
                        )
                    ),
                    "mean_case_rms": _finite_float(np.mean(probability_case_rms)),
                    "maximum_case_rms": _finite_float(np.max(probability_case_rms)),
                    "maximum_difference": _finite_float(
                        np.max(self.probability_case_max)
                    ),
                    "exact_tolerance": 1e-10,
                },
                "centered_logit": {
                    "scalar_normalized_rms": _finite_float(
                        np.sqrt(
                            np.sum(self.centered_case_sumsq)
                            / (decision_count * N_STATES)
                        )
                    ),
                    "mean_case_rms": _finite_float(np.mean(centered_case_rms)),
                    "maximum_case_rms": _finite_float(np.max(centered_case_rms)),
                    "maximum_difference": _finite_float(np.max(self.centered_case_max)),
                    "comparison_absmax": _finite_float(self.centered_logit_absmax),
                    "exact_tolerance": _finite_float(centered_tolerance),
                },
            },
            "invalid_numerical_events": 0,
        }
        return summary

    def compact_case_arrays(self) -> dict[str, Any]:
        """Return cumulative per-case gate inputs for a compressed sidecar."""

        probability_denominator = self.suffix_count * N_STATES
        return {
            "pair_survives": self.pair_case_all.astype(np.uint8).tolist(),
            "baseline_all_correct": self.strict_case_all["baseline"]
            .astype(np.uint8)
            .tolist(),
            "identity_loop_all_correct": self.strict_case_all["identity_loop"]
            .astype(np.uint8)
            .tolist(),
            "matched_control_all_correct": self.strict_case_all["matched_control"]
            .astype(np.uint8)
            .tolist(),
            "baseline_minimum_target_margin": self.margin_case_min[
                "baseline"
            ].tolist(),
            "identity_loop_minimum_target_margin": self.margin_case_min[
                "identity_loop"
            ].tolist(),
            "matched_control_minimum_target_margin": self.margin_case_min[
                "matched_control"
            ].tolist(),
            "minimum_loop_minus_baseline_margin": self.margin_delta_case_min.tolist(),
            "control_all_predictions_disagree": self.control_case_all_disagree.astype(
                np.uint8
            ).tolist(),
            "unit_ray_max": self.ray_l2_case_max.tolist(),
            "positive_ray_angle_max": self.angle_case_max.tolist(),
            "probability_rms": np.sqrt(
                self.probability_case_sumsq / probability_denominator
            ).tolist(),
            "probability_max": self.probability_case_max.tolist(),
            "centered_logit_rms": np.sqrt(
                self.centered_case_sumsq / probability_denominator
            ).tolist(),
            "centered_logit_max": self.centered_case_max.tolist(),
        }


def registered_relation_configurations() -> tuple[RelationConfiguration, ...]:
    """Enumerate the 21 frozen relation/budget configurations."""

    configurations: list[RelationConfiguration] = []
    for relation, relation_word in REGISTERED_RELATIONS:
        for repeat_count in REGISTERED_REPEAT_CANDIDATES:
            budget = repeat_count * len(relation_word)
            if budget > MAX_INSERTED_TOKENS:
                continue
            identity_word = relation_word * repeat_count
            control_word = identity_word[:-1] + (1 - identity_word[-1],)
            configurations.append(
                RelationConfiguration(
                    relation=relation,
                    relation_word=relation_word,
                    repeat_count=repeat_count,
                    inserted_token_budget=budget,
                    identity_word=identity_word,
                    control_word=control_word,
                )
            )
    if len(configurations) != 21:
        raise ArithmeticError("registered relator filter did not produce 21 configurations")
    return tuple(configurations)


def exact_binary_words(length: int) -> np.ndarray:
    """Return exact-length binary words in canonical breadth/lexicographic order."""

    if length < 0:
        raise ValueError("word length must be nonnegative")
    if length == 0:
        return np.empty((1, 0), dtype=np.int64)
    values = np.arange(1 << length, dtype=np.uint64)[:, None]
    shifts = np.arange(length - 1, -1, -1, dtype=np.uint64)[None, :]
    return ((values >> shifts) & 1).astype(np.int64)


def decode_exact_word(index: int, length: int) -> list[int]:
    """Decode an index in :func:`exact_binary_words` order."""

    if length < 0 or index < 0 or index >= (1 << length):
        raise ValueError("word index is outside the exact binary shell")
    return [int((index >> shift) & 1) for shift in range(length - 1, -1, -1)]


def run_relator_witness(
    weights: LinearOperatorWeights,
    batch: EpisodeBatch,
    checkpoint_seed: int,
    *,
    retain_case_arrays: bool = False,
) -> dict[str, Any]:
    """Run the frozen v0.3.0 repeated-relator witness family.

    ``batch`` must be the registered length-zero, eight-episode D4 batch for the
    checkpoint seed.  Every learned generator application is routed through the
    episode's ``canonical_to_slot`` map and normalized in float64.  A non-finite
    value or pre-normalization norm at or below ``1e-12`` raises
    :class:`NumericalExecutionError`; no metric is returned from an invalid run.
    """

    weights.validate()
    _validate_registered_batch(batch, int(checkpoint_seed))
    if int(checkpoint_seed) not in (0, 1):
        raise ValueError("registered checkpoint_seed must be 0 or 1")

    configurations = registered_relation_configurations()
    episode_records: list[dict[str, Any]] = []

    all_hard_pass = True
    all_soft_pass = True
    all_control_pass = True
    record_count = 0

    for episode_index in range(EPISODES_PER_CHECKPOINT):
        episode_record = _run_episode(
            weights=weights,
            batch=batch,
            episode_index=episode_index,
            configurations=configurations,
            retain_case_arrays=retain_case_arrays,
        )
        episode_records.append(episode_record)
        record_count += len(episode_record["relation_budget_records"])
        all_hard_pass &= bool(episode_record["gates"]["W0_relator_hard_closure"])
        all_soft_pass &= bool(episode_record["gates"]["W1_relator_soft_flatness"])
        all_control_pass &= bool(episode_record["gates"]["C0_nonidentity_control"])

    if record_count != EPISODES_PER_CHECKPOINT * len(configurations):
        raise ArithmeticError("relator witness record count is incomplete")

    return {
        "schema": SCHEMA,
        "checkpoint_seed": int(checkpoint_seed),
        "registered_episode_seed": int(930000 + 1000 * int(checkpoint_seed)),
        "configuration": {
            "base_history_depth": BASE_HISTORY_DEPTH,
            "base_histories": 1 << BASE_HISTORY_DEPTH,
            "starts": N_STATES,
            "base_cases_per_episode": (1 << BASE_HISTORY_DEPTH) * N_STATES,
            "suffix_horizons": list(range(MAX_SUFFIX_HORIZON + 1)),
            "relation_budget_configurations": len(configurations),
            "case_order": "base_history_index major, semantic start minor",
            "canonical_generators": {"0": "R", "1": "F"},
            "minimum_pre_normalization_norm": MINIMUM_PRE_NORMALIZATION_NORM,
            "negative_rays_distinct": True,
            "retain_case_arrays": bool(retain_case_arrays),
        },
        "episodes": episode_records,
        "gates": {
            "W0_relator_hard_closure": bool(all_hard_pass),
            "W1_relator_soft_flatness": bool(all_soft_pass),
            "C0_nonidentity_control": bool(all_control_pass),
        },
        "invalid_numerical_events": 0,
        "claim_boundary": (
            "A failure is a finite counterexample at the observed history depth and "
            "suffix horizon. A pass covers only the registered relation family and "
            "does not certify all ordinary histories at the same total depth."
        ),
    }


def _run_episode(
    *,
    weights: LinearOperatorWeights,
    batch: EpisodeBatch,
    episode_index: int,
    configurations: tuple[RelationConfiguration, ...],
    retain_case_arrays: bool,
) -> dict[str, Any]:
    slot_codes = encode_tables(
        weights, batch.tables[episode_index : episode_index + 1], dtype=np.float64
    )[0]
    _require_finite("encoded operators", slot_codes)
    canonical_to_slot = np.asarray(
        batch.canonical_to_slot[episode_index], dtype=np.int64
    )
    slot_maps = np.asarray(batch.maps[episode_index], dtype=np.int64)
    canonical_codes, canonical_maps = _canonicalized_episode_operators(
        slot_codes, slot_maps, canonical_to_slot
    )

    base_hidden, base_semantic, base_words, base_starts = _build_base_cases(
        weights, canonical_codes, canonical_maps
    )
    baseline_shells = _build_baseline_shells(
        weights, base_hidden, base_semantic, canonical_codes, canonical_maps
    )

    relation_records: list[dict[str, Any]] = []
    hard_pass = True
    soft_pass = True
    control_pass = True

    for configuration in configurations:
        record = _evaluate_configuration(
            weights=weights,
            canonical_codes=canonical_codes,
            canonical_maps=canonical_maps,
            baseline_shells=baseline_shells,
            base_hidden=base_hidden,
            base_semantic=base_semantic,
            base_words=base_words,
            base_starts=base_starts,
            configuration=configuration,
            retain_case_arrays=retain_case_arrays,
        )
        relation_records.append(record)
        hard_pass &= bool(record["gates"]["W0_relator_hard_closure"])
        soft_pass &= bool(record["gates"]["W1_relator_soft_flatness"])
        control_pass &= bool(record["gates"]["C0_nonidentity_control"])

    return {
        "episode_index": int(episode_index),
        "canonical_to_slot": canonical_to_slot.tolist(),
        "base_case_count": int(base_hidden.shape[0]),
        "relation_budget_records": relation_records,
        "gates": {
            "W0_relator_hard_closure": bool(hard_pass),
            "W1_relator_soft_flatness": bool(soft_pass),
            "C0_nonidentity_control": bool(control_pass),
        },
        "invalid_numerical_events": 0,
    }


def _evaluate_configuration(
    *,
    weights: LinearOperatorWeights,
    canonical_codes: np.ndarray,
    canonical_maps: np.ndarray,
    baseline_shells: list[_BaselineShell],
    base_hidden: np.ndarray,
    base_semantic: np.ndarray,
    base_words: np.ndarray,
    base_starts: np.ndarray,
    configuration: RelationConfiguration,
    retain_case_arrays: bool,
) -> dict[str, Any]:
    identity_action = _word_action(canonical_maps, configuration.identity_word)
    if not np.array_equal(identity_action, np.arange(N_STATES, dtype=np.int64)):
        raise ArithmeticError(
            f"registered relation {configuration.relation} repeat "
            f"{configuration.repeat_count} is not exact identity"
        )
    control_action = _word_action(canonical_maps, configuration.control_word)
    if np.array_equal(control_action, np.arange(N_STATES, dtype=np.int64)):
        raise ArithmeticError("matched control unexpectedly has identity D4 action")
    if np.any(control_action == np.arange(N_STATES, dtype=np.int64)):
        raise ArithmeticError(
            "matched control has a fixed point, so endpoint disagreement is not implied"
        )

    identity_hidden = _apply_shared_word(
        base_hidden, canonical_codes, configuration.identity_word
    )
    control_hidden = _apply_shared_word(
        base_hidden, canonical_codes, configuration.control_word
    )
    control_semantic = control_action[base_semantic]
    if not np.all(control_semantic != base_semantic):
        raise ArithmeticError("matched-control endpoint semantics did not all change")

    endpoint_l2, endpoint_angle = _paired_ray_geometry(base_hidden, identity_hidden)
    baseline_endpoint_prediction = baseline_shells[0].prediction[:, 0]
    identity_endpoint_logits = _decoder_logits(weights, identity_hidden[:, None, :])
    control_endpoint_logits = _decoder_logits(weights, control_hidden[:, None, :])
    identity_endpoint_prediction = np.argmax(identity_endpoint_logits[:, 0], axis=-1)
    control_endpoint_prediction = np.argmax(control_endpoint_logits[:, 0], axis=-1)

    case_count = base_hidden.shape[0]
    first_reveal = np.full(case_count, MAX_SUFFIX_HORIZON + 1, dtype=np.int64)
    first_reveal_suffix_index = np.full(case_count, -1, dtype=np.int64)
    first_identity_failure = np.full(
        case_count, MAX_SUFFIX_HORIZON + 1, dtype=np.int64
    )
    first_identity_failure_suffix_index = np.full(case_count, -1, dtype=np.int64)
    first_identity_failure_argmax_correct = np.ones(case_count, dtype=bool)
    first_identity_failure_margin = np.full(case_count, np.nan, dtype=np.float64)
    cumulative = _MetricAccumulator(case_count)
    cumulative_records: list[dict[str, Any]] = []
    exact_shell_records: list[dict[str, Any]] = []
    retained_case_arrays: list[dict[str, Any]] = []

    identity_frontier = identity_hidden[:, None, :]
    control_frontier = control_hidden[:, None, :]
    control_semantic_frontier = control_semantic[:, None]

    for horizon in range(MAX_SUFFIX_HORIZON + 1):
        baseline = baseline_shells[horizon]
        shell = _measure_shell(
            weights=weights,
            baseline=baseline,
            identity_hidden=identity_frontier,
            control_hidden=control_frontier,
            control_semantic=control_semantic_frontier,
        )

        shell_case_disagreement = np.any(~shell.pair_equal, axis=1)
        newly_revealed = (first_reveal == MAX_SUFFIX_HORIZON + 1) & shell_case_disagreement
        if np.any(newly_revealed):
            rows = np.flatnonzero(newly_revealed)
            first_reveal[rows] = horizon
            first_reveal_suffix_index[rows] = np.argmax(
                ~shell.pair_equal[rows], axis=1
            )

        identity_bad = ~shell.strict_correct["identity_loop"]
        newly_failed = (
            first_identity_failure == MAX_SUFFIX_HORIZON + 1
        ) & np.any(identity_bad, axis=1)
        if np.any(newly_failed):
            rows = np.flatnonzero(newly_failed)
            suffix_indices = np.argmax(identity_bad[rows], axis=1)
            first_identity_failure[rows] = horizon
            first_identity_failure_suffix_index[rows] = suffix_indices
            first_identity_failure_argmax_correct[rows] = shell.argmax_correct[
                "identity_loop"
            ][rows, suffix_indices]
            first_identity_failure_margin[rows] = shell.margins["identity_loop"][
                rows, suffix_indices
            ]

        shell_accumulator = _MetricAccumulator(case_count)
        shell_accumulator.update(shell)
        exact_shell_records.append(
            shell_accumulator.summary(horizon, "exact_suffix_shell")
        )
        cumulative.update(shell)
        cumulative_records.append(cumulative.summary(horizon, "cumulative_suffixes"))
        if retain_case_arrays:
            retained_case_arrays.append(
                {
                    "horizon": int(horizon),
                    "cumulative": cumulative.compact_case_arrays(),
                    "exact_shell": shell_accumulator.compact_case_arrays(),
                }
            )

        if horizon < MAX_SUFFIX_HORIZON:
            identity_frontier = _expand_hidden_frontier(
                identity_frontier, canonical_codes
            )
            control_frontier = _expand_hidden_frontier(
                control_frontier, canonical_codes
            )
            control_semantic_frontier = _expand_semantic_frontier(
                control_semantic_frontier, canonical_maps
            )

    reveal_histogram = {
        str(horizon): int(np.sum(first_reveal == horizon))
        for horizon in range(MAX_SUFFIX_HORIZON + 1)
    }
    reveal_histogram[f">{MAX_SUFFIX_HORIZON}"] = int(
        np.sum(first_reveal == MAX_SUFFIX_HORIZON + 1)
    )
    revealing_cases = np.flatnonzero(first_reveal <= MAX_SUFFIX_HORIZON)
    hard_witnesses = [
        {
            "case_index": int(case_index),
            "base_history_index": int(case_index // N_STATES),
            "base_history": base_words[case_index].tolist(),
            "start": int(base_starts[case_index]),
            "first_reveal_horizon": int(first_reveal[case_index]),
            "first_revealing_suffix_index": int(
                first_reveal_suffix_index[case_index]
            ),
            "first_revealing_suffix": decode_exact_word(
                int(first_reveal_suffix_index[case_index]),
                int(first_reveal[case_index]),
            ),
        }
        for case_index in revealing_cases
    ]
    identity_failure_cases = np.flatnonzero(
        first_identity_failure <= MAX_SUFFIX_HORIZON
    )
    identity_failure_witnesses = [
        {
            "case_index": int(case_index),
            "base_history_index": int(case_index // N_STATES),
            "base_history": base_words[case_index].tolist(),
            "start": int(base_starts[case_index]),
            "first_failure_horizon": int(first_identity_failure[case_index]),
            "first_failure_suffix_index": int(
                first_identity_failure_suffix_index[case_index]
            ),
            "first_failure_suffix": decode_exact_word(
                int(first_identity_failure_suffix_index[case_index]),
                int(first_identity_failure[case_index]),
            ),
            "argmax_correct": bool(
                first_identity_failure_argmax_correct[case_index]
            ),
            "target_margin": _finite_float(
                first_identity_failure_margin[case_index]
            ),
            "failure_kind": (
                "nonpositive_margin"
                if first_identity_failure_argmax_correct[case_index]
                else "wrong_argmax"
            ),
        }
        for case_index in identity_failure_cases
    ]

    endpoint_control_disagree = control_endpoint_prediction != baseline_endpoint_prediction
    endpoint = {
        "identity_loop_vs_baseline": {
            "unit_ray_l2": _distribution_summary(endpoint_l2),
            "positive_ray_angle": _distribution_summary(endpoint_angle),
            "prediction_agreement_fraction": _finite_ratio(
                int(np.sum(identity_endpoint_prediction == baseline_endpoint_prediction)),
                case_count,
            ),
        },
        "matched_control_vs_baseline": {
            "exact_semantic_disagreement_fraction": _finite_ratio(
                int(np.sum(control_semantic != base_semantic)), case_count
            ),
            "prediction_disagreement_fraction": _finite_ratio(
                int(np.sum(endpoint_control_disagree)), case_count
            ),
            "all_predictions_disagree": bool(np.all(endpoint_control_disagree)),
        },
    }

    final_cumulative = cumulative_records[-1]
    identity_final = final_cumulative["interfaces"]["identity_loop"]
    control_final = final_cumulative["interfaces"]["matched_control"]
    paired_final = final_cumulative["paired_path"]

    hard_gate = bool(
        final_cumulative["identity_loop_vs_baseline"][
            "hard_signature_survival_fraction"
        ]
        == 1.0
        and identity_final["semantic_accuracy"] == 1.0
        and identity_final["all_target_margins_strictly_positive"]
        and final_cumulative["invalid_numerical_events"] == 0
    )
    soft_gate = bool(
        paired_final["unit_ray_l2"]["maximum"] <= 1e-8
        and paired_final["probability"]["maximum_difference"] <= 1e-10
        and paired_final["centered_logit"]["maximum_difference"]
        <= paired_final["centered_logit"]["exact_tolerance"]
        and final_cumulative["invalid_numerical_events"] == 0
    )
    control_gate = bool(
        not np.array_equal(control_action, np.arange(N_STATES, dtype=np.int64))
        and control_final["semantic_accuracy"] == 1.0
        and control_final["all_target_margins_strictly_positive"]
        and endpoint["matched_control_vs_baseline"]["all_predictions_disagree"]
        and final_cumulative["invalid_numerical_events"] == 0
    )

    record: dict[str, Any] = {
        "relation": configuration.relation,
        "relation_word": list(configuration.relation_word),
        "repeat_count": int(configuration.repeat_count),
        "inserted_token_budget": int(configuration.inserted_token_budget),
        "observed_history_depth": int(
            BASE_HISTORY_DEPTH + configuration.inserted_token_budget
        ),
        "base_case_count": int(case_count),
        "identity_action_verified": True,
        "control_action": control_action.tolist(),
        "control_nonidentity_verified": True,
        "control_fixed_point_free_verified": True,
        "matched_control_construction": {
            "length": len(configuration.control_word),
            "shared_prefix_length": len(configuration.control_word) - 1,
            "identity_final_generator": int(configuration.identity_word[-1]),
            "control_final_generator": int(configuration.control_word[-1]),
        },
        "endpoint": endpoint,
        "first_revealing_suffix_horizon": (
            None
            if revealing_cases.size == 0
            else int(np.min(first_reveal[revealing_cases]))
        ),
        "first_reveal_histogram": reveal_histogram,
        "hard_counterexample_count": int(revealing_cases.size),
        "hard_counterexamples": hard_witnesses,
        "identity_semantic_or_margin_failure_count": int(
            identity_failure_cases.size
        ),
        "identity_semantic_or_margin_failures": identity_failure_witnesses,
        "cumulative_suffix_records": cumulative_records,
        "exact_suffix_shell_records": exact_shell_records,
        "gates": {
            "W0_relator_hard_closure": hard_gate,
            "W1_relator_soft_flatness": soft_gate,
            "C0_nonidentity_control": control_gate,
        },
        "invalid_numerical_events": 0,
    }
    if retain_case_arrays:
        record["case_arrays"] = {
            "case_order": "base_history_index major, semantic start minor",
            "first_reveal_depth": first_reveal.tolist(),
            "first_reveal_suffix_index": first_reveal_suffix_index.tolist(),
            "endpoint_unit_ray_l2": endpoint_l2.tolist(),
            "endpoint_positive_ray_angle": endpoint_angle.tolist(),
            "endpoint_control_prediction_disagrees": endpoint_control_disagree.astype(
                np.uint8
            ).tolist(),
            "horizon_records": retained_case_arrays,
        }
    return record


def _validate_registered_batch(batch: EpisodeBatch, checkpoint_seed: int) -> None:
    expected_tables = (
        EPISODES_PER_CHECKPOINT,
        N_OPERATORS,
        N_STATES,
        N_STATES,
    )
    if batch.family.lower() != "d4":
        raise ValueError("relator witness requires the registered D4 family")
    if batch.tables.shape != expected_tables:
        raise ValueError(f"registered episode tables must have shape {expected_tables}")
    if batch.maps.shape != (EPISODES_PER_CHECKPOINT, N_OPERATORS, N_STATES):
        raise ValueError("registered episode maps have an invalid shape")
    if batch.canonical_to_slot.shape != (EPISODES_PER_CHECKPOINT, N_OPERATORS):
        raise ValueError("canonical_to_slot has an invalid shape")
    if batch.canonical_ops.shape != (EPISODES_PER_CHECKPOINT, 0):
        raise ValueError("registered episode batch must have length zero")
    if batch.op_slots.shape != (EPISODES_PER_CHECKPOINT, 0):
        raise ValueError("registered episode batch must have no sampled operator slots")
    _require_finite("episode tables", batch.tables)
    for episode_mapping in batch.canonical_to_slot:
        if not np.array_equal(np.sort(episode_mapping), np.arange(N_OPERATORS)):
            raise ValueError("canonical_to_slot must be a permutation of operator slots")
    if np.any(batch.maps < 0) or np.any(batch.maps >= N_STATES):
        raise ValueError("episode semantic maps contain an invalid state")

    expected = sample_batch(
        np.random.default_rng(930000 + 1000 * checkpoint_seed),
        batch_size=EPISODES_PER_CHECKPOINT,
        length=0,
        family="d4",
    )
    for field_name in (
        "tables",
        "maps",
        "op_slots",
        "canonical_ops",
        "start",
        "target",
        "canonical_to_slot",
        "phi",
    ):
        if not np.array_equal(getattr(batch, field_name), getattr(expected, field_name)):
            raise ValueError(
                f"episode batch field {field_name} does not match registered seed "
                f"{930000 + 1000 * checkpoint_seed}"
            )


def _canonicalized_episode_operators(
    slot_codes: np.ndarray,
    slot_maps: np.ndarray,
    canonical_to_slot: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if not np.array_equal(np.sort(canonical_to_slot), np.arange(N_OPERATORS)):
        raise ValueError("canonical_to_slot is not a generator-slot permutation")
    canonical_codes = slot_codes[canonical_to_slot]
    canonical_maps = slot_maps[canonical_to_slot]
    _require_finite("canonicalized learned operators", canonical_codes)
    for mapping in canonical_maps:
        if not np.array_equal(np.sort(mapping), np.arange(N_STATES)):
            raise ValueError("D4 semantic operator is not a permutation")
    return canonical_codes, canonical_maps


def _build_base_cases(
    weights: LinearOperatorWeights,
    canonical_codes: np.ndarray,
    canonical_maps: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    history_words = exact_binary_words(BASE_HISTORY_DEPTH)
    words = np.repeat(history_words, N_STATES, axis=0)
    starts = np.tile(np.arange(N_STATES, dtype=np.int64), history_words.shape[0])
    hidden = weights.state_embedding.astype(np.float64, copy=False)[starts].copy()
    semantic = starts.copy()
    _require_finite("initial state embedding", hidden)
    rows = np.arange(hidden.shape[0])
    for step in range(BASE_HISTORY_DEPTH):
        operators = words[:, step]
        selected_codes = canonical_codes[operators]
        hidden = np.einsum("bij,bj->bi", selected_codes, hidden)
        hidden = _safe_normalize(hidden, f"base history step {step + 1}")
        semantic = canonical_maps[operators, semantic]
    expected_cases = (1 << BASE_HISTORY_DEPTH) * N_STATES
    if hidden.shape != (expected_cases, N_STATES):
        raise ArithmeticError("base history enumeration produced the wrong case count")
    return hidden, semantic, words, starts


def _build_baseline_shells(
    weights: LinearOperatorWeights,
    base_hidden: np.ndarray,
    base_semantic: np.ndarray,
    canonical_codes: np.ndarray,
    canonical_maps: np.ndarray,
) -> list[_BaselineShell]:
    shells: list[_BaselineShell] = []
    hidden = base_hidden[:, None, :]
    semantic = base_semantic[:, None]
    for horizon in range(MAX_SUFFIX_HORIZON + 1):
        logits = _decoder_logits(weights, hidden)
        probabilities = _softmax(logits)
        prediction = np.argmax(logits, axis=-1)
        margins = _target_margin(logits, semantic)
        shells.append(
            _BaselineShell(
                hidden=hidden,
                semantic=semantic,
                logits=logits,
                probabilities=probabilities,
                prediction=prediction,
                target_margin=margins,
            )
        )
        if horizon < MAX_SUFFIX_HORIZON:
            hidden = _expand_hidden_frontier(hidden, canonical_codes)
            semantic = _expand_semantic_frontier(semantic, canonical_maps)
    if [shell.hidden.shape[1] for shell in shells] != [
        1 << horizon for horizon in range(MAX_SUFFIX_HORIZON + 1)
    ]:
        raise ArithmeticError("baseline suffix shell counts are incorrect")
    return shells


def _measure_shell(
    *,
    weights: LinearOperatorWeights,
    baseline: _BaselineShell,
    identity_hidden: np.ndarray,
    control_hidden: np.ndarray,
    control_semantic: np.ndarray,
) -> _ShellMeasurements:
    if identity_hidden.shape != baseline.hidden.shape:
        raise ValueError("identity and baseline suffix shells differ in shape")
    if control_hidden.shape != baseline.hidden.shape:
        raise ValueError("control and baseline suffix shells differ in shape")
    if control_semantic.shape != baseline.semantic.shape:
        raise ValueError("control semantic suffix shell differs in shape")

    identity_logits = _decoder_logits(weights, identity_hidden)
    control_logits = _decoder_logits(weights, control_hidden)
    identity_probabilities = _softmax(identity_logits)
    identity_prediction = np.argmax(identity_logits, axis=-1)
    control_prediction = np.argmax(control_logits, axis=-1)
    identity_margin = _target_margin(identity_logits, baseline.semantic)
    control_margin = _target_margin(control_logits, control_semantic)

    baseline_argmax_correct = baseline.prediction == baseline.semantic
    identity_argmax_correct = identity_prediction == baseline.semantic
    control_argmax_correct = control_prediction == control_semantic
    argmax_correct = {
        "baseline": baseline_argmax_correct,
        "identity_loop": identity_argmax_correct,
        "matched_control": control_argmax_correct,
    }
    strict_correct = {
        "baseline": baseline_argmax_correct & (baseline.target_margin > 0.0),
        "identity_loop": identity_argmax_correct & (identity_margin > 0.0),
        "matched_control": control_argmax_correct & (control_margin > 0.0),
    }

    baseline_centered = baseline.logits - np.mean(
        baseline.logits, axis=-1, keepdims=True
    )
    identity_centered = identity_logits - np.mean(
        identity_logits, axis=-1, keepdims=True
    )
    centered_absmax = max(
        1.0,
        float(np.max(np.abs(baseline_centered))),
        float(np.max(np.abs(identity_centered))),
    )
    ray_l2, ray_angle = _paired_ray_geometry(baseline.hidden, identity_hidden)

    return _ShellMeasurements(
        pair_equal=identity_prediction == baseline.prediction,
        strict_correct=strict_correct,
        argmax_correct=argmax_correct,
        margins={
            "baseline": baseline.target_margin,
            "identity_loop": identity_margin,
            "matched_control": control_margin,
        },
        loop_minus_baseline_margin=identity_margin - baseline.target_margin,
        control_baseline_disagree=control_prediction != baseline.prediction,
        unit_ray_l2=ray_l2,
        positive_ray_angle=ray_angle,
        probability_difference=identity_probabilities - baseline.probabilities,
        centered_logit_difference=identity_centered - baseline_centered,
        centered_logit_absmax=centered_absmax,
    )


def _apply_shared_word(
    hidden: np.ndarray,
    canonical_codes: np.ndarray,
    word: tuple[int, ...],
) -> np.ndarray:
    state = np.asarray(hidden, dtype=np.float64).copy()
    _require_finite("shared-word initial state", state)
    for step, canonical_generator in enumerate(word):
        if canonical_generator not in (0, 1):
            raise ValueError("canonical word contains a non-binary generator")
        state = np.einsum("ij,bj->bi", canonical_codes[canonical_generator], state)
        state = _safe_normalize(state, f"inserted word step {step + 1}")
    return state


def _word_action(canonical_maps: np.ndarray, word: tuple[int, ...]) -> np.ndarray:
    current = np.arange(N_STATES, dtype=np.int64)
    for canonical_generator in word:
        if canonical_generator not in (0, 1):
            raise ValueError("canonical word contains a non-binary generator")
        current = canonical_maps[canonical_generator, current]
    return current


def _expand_hidden_frontier(
    hidden: np.ndarray, canonical_codes: np.ndarray
) -> np.ndarray:
    if hidden.ndim != 3 or hidden.shape[-1] != N_STATES:
        raise ValueError("hidden suffix frontier has an invalid shape")
    expanded = np.einsum("oij,cbj->cboi", canonical_codes, hidden)
    expanded = expanded.reshape(hidden.shape[0], hidden.shape[1] * N_OPERATORS, N_STATES)
    return _safe_normalize(expanded, "suffix expansion")


def _expand_semantic_frontier(
    semantic: np.ndarray, canonical_maps: np.ndarray
) -> np.ndarray:
    if semantic.ndim != 2:
        raise ValueError("semantic suffix frontier has an invalid shape")
    expanded = np.stack(
        [canonical_maps[operator, semantic] for operator in range(N_OPERATORS)],
        axis=2,
    )
    return expanded.reshape(semantic.shape[0], semantic.shape[1] * N_OPERATORS)


def _decoder_logits(weights: LinearOperatorWeights, hidden: np.ndarray) -> np.ndarray:
    _require_finite("decoder input", hidden)
    decoder = weights.decoder.astype(np.float64, copy=False)
    logits = np.einsum("...i,ki->...k", hidden, decoder)
    _require_finite("decoder logits", logits)
    return logits


def _softmax(logits: np.ndarray) -> np.ndarray:
    _require_finite("softmax logits", logits)
    shifted = logits - np.max(logits, axis=-1, keepdims=True)
    exponentials = np.exp(shifted)
    denominator = np.sum(exponentials, axis=-1, keepdims=True)
    if not np.isfinite(denominator).all() or np.any(denominator <= 0.0):
        raise NumericalExecutionError("softmax denominator is invalid")
    probabilities = exponentials / denominator
    _require_finite("softmax probabilities", probabilities)
    return probabilities


def _target_margin(logits: np.ndarray, target: np.ndarray) -> np.ndarray:
    if logits.shape[:-1] != target.shape:
        raise ValueError("target shape does not match logits")
    if np.any(target < 0) or np.any(target >= N_STATES):
        raise ValueError("target contains an invalid semantic state")
    selected = np.take_along_axis(logits, target[..., None], axis=-1)[..., 0]
    other = np.where(
        np.arange(N_STATES) == target[..., None], -np.inf, logits
    )
    margins = selected - np.max(other, axis=-1)
    _require_finite("target margins", margins)
    return margins


def _safe_normalize(states: np.ndarray, context: str) -> np.ndarray:
    state = np.asarray(states, dtype=np.float64)
    _require_finite(f"{context} pre-normalization states", state)
    norms = np.linalg.norm(state, axis=-1, keepdims=True)
    if not np.isfinite(norms).all():
        raise NumericalExecutionError(f"{context} produced a non-finite norm")
    minimum = float(np.min(norms))
    if minimum <= MINIMUM_PRE_NORMALIZATION_NORM:
        raise NumericalExecutionError(
            f"{context} reached norm {minimum:.17g} at or below "
            f"{MINIMUM_PRE_NORMALIZATION_NORM:.17g}"
        )
    normalized = state / norms
    _require_finite(f"{context} normalized states", normalized)
    return normalized


def _paired_ray_geometry(
    left: np.ndarray, right: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    if left.shape != right.shape or left.shape[-1] != N_STATES:
        raise ValueError("paired rays have incompatible shapes")
    left_unit = _safe_normalize(left, "left positive ray")
    right_unit = _safe_normalize(right, "right positive ray")
    difference = np.linalg.norm(left_unit - right_unit, axis=-1)
    cosine = np.sum(left_unit * right_unit, axis=-1)
    angle = np.arccos(np.clip(cosine, -1.0, 1.0))
    _require_finite("positive-ray L2", difference)
    _require_finite("positive-ray angle", angle)
    return difference, angle


def _distribution_summary(values: np.ndarray) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64).reshape(-1)
    if array.size == 0:
        raise ArithmeticError("cannot summarize an empty array")
    _require_finite("reported statistic input", array)
    return {
        "minimum": _finite_float(np.min(array)),
        "p01": _finite_float(np.percentile(array, 1.0)),
        "median": _finite_float(np.median(array)),
        "maximum": _finite_float(np.max(array)),
    }


def _finite_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        raise ArithmeticError("ratio denominator must be positive")
    return _finite_float(float(numerator) / float(denominator))


def _finite_float(value: float | np.floating[Any]) -> float:
    result = float(value)
    if not np.isfinite(result):
        raise NumericalExecutionError("derived statistic is non-finite")
    return result


def _require_finite(name: str, values: np.ndarray) -> None:
    if not np.isfinite(values).all():
        raise NumericalExecutionError(f"{name} contains a non-finite value")


__all__ = [
    "BASE_HISTORY_DEPTH",
    "EPISODES_PER_CHECKPOINT",
    "MAX_SUFFIX_HORIZON",
    "MINIMUM_PRE_NORMALIZATION_NORM",
    "NumericalExecutionError",
    "REGISTERED_RELATIONS",
    "REGISTERED_REPEAT_CANDIDATES",
    "RelationConfiguration",
    "decode_exact_word",
    "exact_binary_words",
    "registered_relation_configurations",
    "run_relator_witness",
]
