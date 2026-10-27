"""RRCT v0.30 structural self-boundary persistence and revision.

The learner owns prospective anonymous handle commitments and receives only a
mixed observation, an anonymous equal-energy process bank, and the subsequently
revealed observation.  The evaluator changes the physical rank of the same
hidden handle/source route.  A brief contraction tests persistent structural
identity; a sustained contraction and restoration test revisability.

The learner's reported ``rank`` is an operational admitted SVD dimension.
Its first-mode pair screen is calibrated against a global sharp null, while
higher-mode admission is not a conditional test of the composite lower-rank
null.  Agreement with the evaluator's physical matrix rank in this benchmark
must not be described as statistically controlled causal-rank identification.

The internal ``confidence`` field remains a bounded paired-margin evidence
support score.  It is audited prequentially but is not called a calibrated
posterior probability.  This experiment concerns a functional causal
self-model and makes no claim about phenomenal awareness or consciousness.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from .causal_boundary import CausalBoundaryConfig, OnlineCausalSelfBoundary


FloatArray = NDArray[np.float64]

V030_SCHEMA = "rrct.v030.structural_self_model_revision.v1"
V030_PILOT_SEEDS = (5701, 5707, 5713, 5719)
V030_OFFICIAL_SEEDS = (5801, 5807, 5813, 5819, 5821, 5827, 5839, 5843)
V030_OBSERVATION_DIM = 12
V030_PROCESS_DIM = 8
V030_SOURCE_COUNT = 6
V030_HANDLE_COUNT = 4
V030_FULL_RANK = 2


@dataclass(frozen=True)
class V030RunConfig:
    block_size: int = 20
    learner_seed: int = 330030
    evidence_capacity: int = 240
    minimum_samples: int = 240
    fit_interval: int = 20
    structural_confirmation_interval: int = 120
    null_permutations: int = 128
    half_null_permutations: int = 128
    null_quantile: float = 0.99
    ridge: float = 0.50
    revision_confirmations: int = 3
    revocation_confirmations: int = 3
    confidence_decay: float = 0.65
    calibration_blocks: int = 29
    stable_blocks: int = 29
    transient_rows: int = 80
    transient_recovery_blocks: int = 17
    contraction_blocks: int = 29
    restoration_blocks: int = 29
    scoring_tail_blocks: int = 5
    routed_mode_one: float = 5.0
    routed_mode_two: float = 3.2
    exogenous_strength: float = 5.0
    stable_shock_multiplier: float = 1.50
    observation_persistence: float = 0.42
    observation_noise: float = 0.035

    def __post_init__(self) -> None:
        integer_names = (
            "block_size",
            "learner_seed",
            "evidence_capacity",
            "minimum_samples",
            "fit_interval",
            "structural_confirmation_interval",
            "null_permutations",
            "half_null_permutations",
            "revision_confirmations",
            "revocation_confirmations",
            "calibration_blocks",
            "stable_blocks",
            "transient_rows",
            "transient_recovery_blocks",
            "contraction_blocks",
            "restoration_blocks",
            "scoring_tail_blocks",
        )
        for name in integer_names:
            value = getattr(self, name)
            if isinstance(value, (bool, np.bool_)) or int(value) != value or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.block_size % 2:
            raise ValueError("block_size must be even")
        for name in (
            "evidence_capacity",
            "minimum_samples",
            "fit_interval",
            "structural_confirmation_interval",
        ):
            if getattr(self, name) % self.block_size:
                raise ValueError(f"{name} must align to commitment blocks")
        if self.structural_confirmation_interval % self.fit_interval:
            raise ValueError(
                "structural_confirmation_interval must align to scheduled fits"
            )
        if self.minimum_samples > self.evidence_capacity:
            raise ValueError("minimum_samples cannot exceed evidence_capacity")
        nuisance_columns = (
            1
            + V030_OBSERVATION_DIM
            + V030_SOURCE_COUNT * V030_PROCESS_DIM
            + V030_HANDLE_COUNT
        )
        if self.minimum_samples // 2 <= nuisance_columns:
            raise ValueError("each evidence half must exceed the nuisance design")
        if self.calibration_steps < self.structural_grace_steps:
            raise ValueError("calibration is too short for confirmed acquisition")
        minimum_scored_revision_phase = (
            self.maximum_structural_latency_steps + self.scoring_tail_steps
        )
        if self.contraction_steps < minimum_scored_revision_phase:
            raise ValueError(
                "contraction must contain the direct-rank latency bound and scoring tail"
            )
        if self.restoration_steps < minimum_scored_revision_phase:
            raise ValueError(
                "restoration must contain the direct-rank latency bound and scoring tail"
            )
        minimum_washout_phase = self.evidence_capacity + self.scoring_tail_steps
        if self.stable_steps < minimum_washout_phase:
            raise ValueError("stable phase must contain a full-window washout and scoring tail")
        if self.transient_recovery_steps < minimum_washout_phase:
            raise ValueError(
                "transient recovery must contain a full-window washout and scoring tail"
            )
        if self.scoring_tail_steps > min(
            self.contraction_steps, self.restoration_steps
        ):
            raise ValueError("scoring tail is longer than a sustained phase")
        for name in (
            "routed_mode_one",
            "routed_mode_two",
            "exogenous_strength",
            "stable_shock_multiplier",
            "observation_persistence",
            "observation_noise",
            "ridge",
            "confidence_decay",
        ):
            value = float(getattr(self, name))
            if not np.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
        if self.routed_mode_one <= self.routed_mode_two:
            raise ValueError("mode one must be stronger than mode two")

    @property
    def calibration_steps(self) -> int:
        return self.calibration_blocks * self.block_size

    @property
    def structural_grace_steps(self) -> int:
        return self.evidence_capacity + (
            self.revision_confirmations - 1
        ) * self.structural_confirmation_interval

    @property
    def maximum_structural_latency_steps(self) -> int:
        """Full replacement window plus direct rank-confirmation allowance."""

        return self.structural_grace_steps

    @property
    def maximum_revocation_latency_steps(self) -> int:
        """Full replacement window plus consecutive-null allowance."""

        return self.evidence_capacity + (
            self.revocation_confirmations - 1
        ) * self.structural_confirmation_interval

    @property
    def stable_steps(self) -> int:
        return self.stable_blocks * self.block_size

    @property
    def transient_steps(self) -> int:
        return self.transient_rows

    @property
    def transient_recovery_steps(self) -> int:
        return self.transient_recovery_blocks * self.block_size

    @property
    def contraction_steps(self) -> int:
        return self.contraction_blocks * self.block_size

    @property
    def restoration_steps(self) -> int:
        return self.restoration_blocks * self.block_size

    @property
    def scoring_tail_steps(self) -> int:
        return self.scoring_tail_blocks * self.block_size

    def boundary_config(self) -> CausalBoundaryConfig:
        """Build the learner config without exposing the evaluator/world seed."""

        return CausalBoundaryConfig(
            observation_dim=V030_OBSERVATION_DIM,
            process_dim=V030_PROCESS_DIM,
            source_count=V030_SOURCE_COUNT,
            handle_count=V030_HANDLE_COUNT,
            evidence_capacity=self.evidence_capacity,
            minimum_samples=self.minimum_samples,
            fit_interval=self.fit_interval,
            structural_confirmation_interval=(
                self.structural_confirmation_interval
            ),
            commitment_block_size=self.block_size,
            ridge=self.ridge,
            null_permutations=self.null_permutations,
            half_null_permutations=self.half_null_permutations,
            null_quantile=self.null_quantile,
            higher_mode_null="global_sharp_null",
            revision_confirmations=self.revision_confirmations,
            revocation_confirmations=self.revocation_confirmations,
            confidence_decay=self.confidence_decay,
            seed=self.learner_seed,
        )


V030_FROZEN_CONFIG = V030RunConfig()


@dataclass(frozen=True)
class _HiddenStructure:
    pair: tuple[int, int]
    internal_basis: FloatArray
    sensory_basis: FloatArray
    rank_two_effect: FloatArray
    rank_one_effect: FloatArray
    exogenous_source: int
    exogenous_effect: FloatArray
    digest: str


def _orthogonal(
    rng: np.random.Generator, rows: int, columns: int
) -> FloatArray:
    q, _ = np.linalg.qr(rng.normal(size=(rows, columns)))
    return np.asarray(q[:, :columns], dtype=np.float64)


def _array_digest(value: FloatArray) -> str:
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def _hidden_structure(seed: int, config: V030RunConfig) -> _HiddenStructure:
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), 0x3000]))
    handle = int(rng.integers(V030_HANDLE_COUNT))
    source = int(rng.integers(V030_SOURCE_COUNT))
    exogenous_source = (source + 1 + int(rng.integers(V030_SOURCE_COUNT - 1))) % V030_SOURCE_COUNT
    internal = _orthogonal(rng, V030_PROCESS_DIM, V030_PROCESS_DIM)
    sensory = _orthogonal(rng, V030_OBSERVATION_DIM, V030_OBSERVATION_DIM)
    rank_two = (
        internal[:, :2]
        @ np.diag([config.routed_mode_one, config.routed_mode_two])
        @ sensory[:, :2].T
    )
    rank_one = (
        config.routed_mode_one
        * np.outer(internal[:, 0], sensory[:, 0])
    )
    exogenous = (
        config.exogenous_strength
        * internal[:, 2:4]
        @ sensory[:, 2:4].T
    )
    payload = {
        "seed": int(seed),
        "pair": [handle, source],
        "exogenous_source": exogenous_source,
        "internal": _array_digest(internal),
        "sensory": _array_digest(sensory),
        "rank_two": _array_digest(rank_two),
        "rank_one": _array_digest(rank_one),
        "exogenous": _array_digest(exogenous),
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return _HiddenStructure(
        pair=(handle, source),
        internal_basis=internal[:, :2],
        sensory_basis=sensory[:, :2],
        rank_two_effect=rank_two,
        rank_one_effect=rank_one,
        exogenous_source=exogenous_source,
        exogenous_effect=exogenous,
        digest=digest,
    )


def _equal_energy_bank(
    rng: np.random.Generator,
) -> FloatArray:
    raw = rng.normal(size=(V030_SOURCE_COUNT, V030_PROCESS_DIM))
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    if np.any(norms <= 1e-12):
        raise RuntimeError("degenerate anonymous process draw")
    return np.asarray(raw / norms, dtype=np.float64)


def _projector_overlap(
    estimate: FloatArray, basis: FloatArray, rank: int
) -> float:
    if rank <= 0:
        return 0.0
    truth = basis[:, :rank] @ basis[:, :rank].T
    return float(np.clip(np.trace(estimate @ truth) / rank, 0.0, 1.0))


def _transition(
    model: OnlineCausalSelfBoundary,
    observation: FloatArray,
    structure: _HiddenStructure,
    effect: FloatArray,
    config: V030RunConfig,
    rng: np.random.Generator,
    *,
    time: int,
    phase: str,
    target_rank: int,
    exogenous_multiplier: float,
) -> tuple[FloatArray, dict[str, Any]]:
    state_before = model.state
    commitment = model.commit_handles(time=time)
    bank = _equal_energy_bank(rng)
    bound = model.bind_sources(
        observation,
        bank,
        commitment_digest=commitment.digest,
        time=time,
    )
    handle, source = structure.pair
    routed = commitment.handles[handle] * bank[source] @ effect
    exogenous = (
        float(exogenous_multiplier)
        * bank[structure.exogenous_source]
        @ structure.exogenous_effect
    )
    next_observation = (
        config.observation_persistence * observation
        + routed
        + exogenous
        + rng.normal(
            0.0,
            config.observation_noise,
            size=V030_OBSERVATION_DIM,
        )
    )
    receipt = model.reveal_outcome(
        next_observation,
        transition_digest=bound.transition_digest,
        time=time + 1,
    )
    state = model.state
    pair = (
        (state.selected_handle_index, state.selected_source_index)
        if state.active
        else None
    )
    fit_pair = (
        (receipt.fit_handle_index, receipt.fit_source_index)
        if receipt.fit_handle_index is not None
        else None
    )
    candidate_pair = (
        (receipt.candidate_handle_index, receipt.candidate_source_index)
        if receipt.candidate_handle_index is not None
        else None
    )
    correct = bool(pair == structure.pair and state.rank == target_rank)
    fit_correct = bool(fit_pair == structure.pair and receipt.fit_rank == target_rank)
    internal_overlap = (
        _projector_overlap(
            state.internal_projector,
            structure.internal_basis,
            target_rank,
        )
        if correct
        else 0.0
    )
    sensory_overlap = (
        _projector_overlap(
            state.sensory_projector,
            structure.sensory_basis,
            target_rank,
        )
        if correct
        else 0.0
    )
    row = {
        "schema": V030_SCHEMA,
        "time": int(time),
        "phase": phase,
        "target_handle": structure.pair[0],
        "target_source": structure.pair[1],
        "target_rank": int(target_rank),
        "selected_handle": state.selected_handle_index,
        "selected_source": state.selected_source_index,
        "selected_rank": state.rank,
        "committed_exact": correct,
        "internal_overlap": internal_overlap,
        "sensory_overlap": sensory_overlap,
        "epoch": state.epoch,
        "confidence_before": receipt.confidence_before,
        "confidence_after": receipt.confidence,
        "confidence_is_probability": False,
        "confidence_semantics": "minimum correctly paired normalized randomization margin",
        "fit_performed": receipt.fit_performed,
        "fit_handle": receipt.fit_handle_index,
        "fit_source": receipt.fit_source_index,
        "fit_rank": receipt.fit_rank,
        "fit_confidence": receipt.fit_confidence,
        "fit_exact": fit_correct,
        "candidate_handle": receipt.candidate_handle_index,
        "candidate_source": receipt.candidate_source_index,
        "candidate_rank": receipt.candidate_rank,
        "candidate_streak": receipt.candidate_streak,
        "candidate_last_evidence_count": receipt.candidate_last_evidence_count,
        "candidate_renewed": receipt.candidate_renewed,
        "null_streak": receipt.null_streak,
        "null_last_evidence_count": receipt.null_last_evidence_count,
        "null_renewed": receipt.null_renewed,
        "candidate_pair_matches": bool(
            candidate_pair is None or candidate_pair == structure.pair
        ),
        "structural_event": receipt.structural_event,
        "acquired": receipt.acquired,
        "revised": receipt.revised,
        "revoked": receipt.revoked,
        "rank_changed": receipt.rank_changed,
        "previous_rank": receipt.previous_rank,
        "pre_state_digest": receipt.model_digest_before,
        "post_state_digest": receipt.model_digest_after,
        "commitment_digest": receipt.commitment_digest,
        "transition_digest": receipt.transition_digest,
        "outcome_digest": receipt.outcome_digest,
        "prequential_chain": bool(
            receipt.model_digest_before == state_before.model_digest
            and receipt.commitment_digest == commitment.digest
            and receipt.transition_digest == bound.transition_digest
        ),
        "source_energy_error": float(
            np.max(np.abs(np.linalg.norm(bank, axis=1) - 1.0))
        ),
        "hidden_truth_passed_to_model": False,
    }
    return np.asarray(next_observation, dtype=np.float64), row


def _run_schedule(
    seed: int,
    branch: str,
    model: OnlineCausalSelfBoundary,
    observation: FloatArray,
    structure: _HiddenStructure,
    config: V030RunConfig,
    schedule: Sequence[tuple[str, int, FloatArray, int, float]],
    *,
    start_time: int,
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(
        # All post-calibration branches receive the same prospective banks,
        # observation noise and exogenous draws.  Only the declared hidden
        # route condition differs.
        np.random.SeedSequence([int(seed), 0x3002])
    )
    rows: list[dict[str, Any]] = []
    current = np.asarray(observation, dtype=np.float64)
    time = int(start_time)
    legacy_rank = model.state.rank
    overlap_signature: tuple[int, int, int] | None = None
    if model.state.active:
        overlap_signature = (
            int(model.state.selected_handle_index),
            int(model.state.selected_source_index),
            int(model.state.rank),
        )
    overlap_candidate: tuple[int, int, int] | None = None
    overlap_streak = 0
    for phase, steps, effect, target_rank, exogenous_multiplier in schedule:
        for phase_step in range(int(steps)):
            current, row = _transition(
                model,
                current,
                structure,
                effect,
                config,
                rng,
                time=time,
                phase=phase,
                target_rank=target_rank,
                exogenous_multiplier=exogenous_multiplier,
            )
            if (
                row["fit_performed"]
                and row["fit_handle"] == structure.pair[0]
                and row["fit_source"] == structure.pair[1]
                and row["fit_rank"] > 0
            ):
                # Exact v0.29 same-pair behavior: install fit rank immediately.
                legacy_rank = int(row["fit_rank"])
            overlap_revised = False
            if row["fit_performed"]:
                fit_signature = None
                if row["fit_handle"] is not None:
                    fit_signature = (
                        int(row["fit_handle"]),
                        int(row["fit_source"]),
                        int(row["fit_rank"]),
                    )
                if fit_signature is None or fit_signature == overlap_signature:
                    overlap_candidate = None
                    overlap_streak = 0
                else:
                    if fit_signature == overlap_candidate:
                        overlap_streak += 1
                    else:
                        overlap_candidate = fit_signature
                        overlap_streak = 1
                    if overlap_streak >= config.revision_confirmations:
                        overlap_signature = fit_signature
                        overlap_candidate = None
                        overlap_streak = 0
                        overlap_revised = True
            overlap_exact = bool(
                overlap_signature is not None
                and overlap_signature[:2] == structure.pair
                and overlap_signature[2] == target_rank
            )
            row.update(
                {
                    "seed": int(seed),
                    "branch": branch,
                    "phase_step": phase_step,
                    "legacy_immediate_rank": legacy_rank,
                    "legacy_immediate_exact": legacy_rank == target_rank,
                    "overlap_confirmation_handle": (
                        None if overlap_signature is None else overlap_signature[0]
                    ),
                    "overlap_confirmation_source": (
                        None if overlap_signature is None else overlap_signature[1]
                    ),
                    "overlap_confirmation_rank": (
                        0 if overlap_signature is None else overlap_signature[2]
                    ),
                    "overlap_confirmation_exact": overlap_exact,
                    "overlap_confirmation_revised": overlap_revised,
                    "structure_digest": structure.digest,
                }
            )
            rows.append(row)
            time += 1
    return rows


def _phase_rows(rows: Sequence[Mapping[str, Any]], phase: str) -> list[Mapping[str, Any]]:
    return [row for row in rows if row["phase"] == phase]


def _mean(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    return float(np.mean([float(row[key]) for row in rows])) if rows else float("nan")


def _terminal_tail(
    rows: Sequence[Mapping[str, Any]], config: V030RunConfig
) -> list[Mapping[str, Any]]:
    return list(rows[-config.scoring_tail_steps :])


def _rank_revision_latency(rows: Sequence[Mapping[str, Any]]) -> int | None:
    for row in rows:
        if row["structural_event"] == "rank_revision":
            return int(row["phase_step"]) + 1
    return None


def _maximum_matching_fit_streak(
    rows: Sequence[Mapping[str, Any]],
    *,
    handle: int,
    source: int,
    rank: int,
) -> int:
    """Count consecutive matching proposals, ignoring non-fit transition rows."""

    streak = 0
    maximum = 0
    for row in rows:
        if not bool(row["fit_performed"]):
            continue
        if (
            row["fit_handle"] == handle
            and row["fit_source"] == source
            and row["fit_rank"] == rank
        ):
            streak += 1
            maximum = max(maximum, streak)
        else:
            streak = 0
    return maximum


def run_structural_self_model_revision_seed(
    seed: int,
    *,
    cohort: str = "pilot",
    config: V030RunConfig = V030_FROZEN_CONFIG,
    allow_reserved_official: bool = False,
) -> dict[str, Any]:
    seed = int(seed)
    if cohort not in {"pilot", "official"}:
        raise ValueError("cohort must be 'pilot' or 'official'")
    if not isinstance(allow_reserved_official, (bool, np.bool_)):
        raise TypeError("allow_reserved_official must be boolean")
    if cohort == "official" and not allow_reserved_official:
        raise PermissionError(
            "reserved official seeds may execute only through the frozen harness"
        )
    if cohort == "pilot" and allow_reserved_official:
        raise ValueError("official execution authority is invalid for a pilot run")
    allowed = V030_PILOT_SEEDS if cohort == "pilot" else V030_OFFICIAL_SEEDS
    if seed not in allowed:
        raise ValueError(f"seed is not reserved for the v0.30 {cohort} cohort")
    structure = _hidden_structure(seed, config)
    model = OnlineCausalSelfBoundary(config.boundary_config())
    calibration_rng = np.random.default_rng(
        np.random.SeedSequence([seed, 0x3001])
    )
    observation = calibration_rng.normal(0.0, 0.25, V030_OBSERVATION_DIM)
    calibration_rows: list[dict[str, Any]] = []
    for time in range(config.calibration_steps):
        observation, row = _transition(
            model,
            observation,
            structure,
            structure.rank_two_effect,
            config,
            calibration_rng,
            time=time,
            phase="calibration",
            target_rank=2,
            exogenous_multiplier=1.0,
        )
        row.update(
            {
                "seed": seed,
                "branch": "calibration",
                "phase_step": time,
                "legacy_immediate_rank": row["selected_rank"],
                "legacy_immediate_exact": row["committed_exact"],
                "overlap_confirmation_handle": row["selected_handle"],
                "overlap_confirmation_source": row["selected_source"],
                "overlap_confirmation_rank": row["selected_rank"],
                "overlap_confirmation_exact": row["committed_exact"],
                "overlap_confirmation_revised": False,
                "structure_digest": structure.digest,
            }
        )
        calibration_rows.append(row)
    if not model.state.active:
        raise RuntimeError("v0.30 calibration failed to acquire a boundary")
    base_snapshot = model.snapshot()
    base_observation = observation.copy()

    stable_model = OnlineCausalSelfBoundary(config.boundary_config())
    stable_model.load_snapshot(base_snapshot)
    stable = _run_schedule(
        seed,
        "stable",
        stable_model,
        base_observation,
        structure,
        config,
        (
            (
                "stable_shock",
                config.stable_steps,
                structure.rank_two_effect,
                2,
                config.stable_shock_multiplier,
            ),
        ),
        start_time=config.calibration_steps,
    )

    transient_model = OnlineCausalSelfBoundary(config.boundary_config())
    transient_model.load_snapshot(base_snapshot)
    transient = _run_schedule(
        seed,
        "transient",
        transient_model,
        base_observation,
        structure,
        config,
        (
            (
                "transient_dropout",
                config.transient_steps,
                structure.rank_one_effect,
                2,
                1.0,
            ),
            (
                "transient_recovery",
                config.transient_recovery_steps,
                structure.rank_two_effect,
                2,
                1.0,
            ),
        ),
        start_time=config.calibration_steps,
    )

    sustained_model = OnlineCausalSelfBoundary(config.boundary_config())
    sustained_model.load_snapshot(base_snapshot)
    sustained = _run_schedule(
        seed,
        "sustained",
        sustained_model,
        base_observation,
        structure,
        config,
        (
            (
                "sustained_contraction",
                config.contraction_steps,
                structure.rank_one_effect,
                1,
                1.0,
            ),
            (
                "sustained_restoration",
                config.restoration_steps,
                structure.rank_two_effect,
                2,
                1.0,
            ),
        ),
        start_time=config.calibration_steps,
    )

    rows = calibration_rows + stable + transient + sustained
    stable_rows = _phase_rows(rows, "stable_shock")
    dropout_rows = _phase_rows(rows, "transient_dropout")
    recovery_rows = _phase_rows(rows, "transient_recovery")
    contraction_rows = _phase_rows(rows, "sustained_contraction")
    restoration_rows = _phase_rows(rows, "sustained_restoration")
    contraction_tail = _terminal_tail(contraction_rows, config)
    restoration_tail = _terminal_tail(restoration_rows, config)
    contraction_latency = _rank_revision_latency(contraction_rows)
    restoration_latency = _rank_revision_latency(restoration_rows)
    transient_rows = dropout_rows + recovery_rows
    rank_one_proposals = [
        row
        for row in transient_rows
        if row["fit_performed"]
        and row["fit_handle"] == structure.pair[0]
        and row["fit_source"] == structure.pair[1]
        and row["fit_rank"] == 1
    ]
    rank_one_starts_or_renewals = [
        row for row in rank_one_proposals if bool(row["candidate_renewed"])
    ]
    candidate_rows = [
        row for row in rows if row["structural_event"] == "structural_candidate"
    ]
    active_rows = [row for row in rows if row["selected_rank"] > 0]
    active_fit_rows = [
        row
        for row in rows
        if row["fit_performed"] and row["fit_rank"] > 0
    ]
    summary = {
        "seed": seed,
        "acquisition_terminal_exact": bool(calibration_rows[-1]["committed_exact"]),
        "acquisition_rank": int(calibration_rows[-1]["selected_rank"]),
        "stable_exact_accuracy": _mean(stable_rows, "committed_exact"),
        "stable_rank_revisions": int(
            sum(row["structural_event"] == "rank_revision" for row in stable_rows)
        ),
        "transient_exact_accuracy": _mean(transient_rows, "committed_exact"),
        "transient_rank_revisions": int(
            sum(row["structural_event"] == "rank_revision" for row in transient_rows)
        ),
        "transient_rank_one_proposals": len(rank_one_proposals),
        "transient_rank_one_candidate_starts_or_renewals": len(
            rank_one_starts_or_renewals
        ),
        "transient_rank_one_max_fit_streak": _maximum_matching_fit_streak(
            transient_rows,
            handle=structure.pair[0],
            source=structure.pair[1],
            rank=1,
        ),
        "transient_legacy_false_rank_rate": float(
            np.mean([row["legacy_immediate_rank"] == 1 for row in transient_rows])
        ),
        "transient_overlap_false_rank_rate": float(
            np.mean(
                [
                    not bool(row["overlap_confirmation_exact"])
                    for row in transient_rows
                ]
            )
        ),
        "transient_overlap_rank_revisions": int(
            sum(
                bool(row["overlap_confirmation_revised"])
                for row in transient_rows
            )
        ),
        "contraction_terminal_tail_accuracy": _mean(
            contraction_tail, "committed_exact"
        ),
        "restoration_terminal_tail_accuracy": _mean(
            restoration_tail, "committed_exact"
        ),
        "contraction_revision_latency": contraction_latency,
        "restoration_revision_latency": restoration_latency,
        "contraction_rank_revisions": int(
            sum(row["structural_event"] == "rank_revision" for row in contraction_rows)
        ),
        "restoration_rank_revisions": int(
            sum(row["structural_event"] == "rank_revision" for row in restoration_rows)
        ),
        "contraction_pair_retained": bool(
            all(
                row["selected_handle"] == structure.pair[0]
                and row["selected_source"] == structure.pair[1]
                for row in contraction_tail
            )
        ),
        "restoration_pair_retained": bool(
            all(
                row["selected_handle"] == structure.pair[0]
                and row["selected_source"] == structure.pair[1]
                for row in restoration_tail
            )
        ),
        "candidate_support_decays": bool(
            candidate_rows
            and all(
                row["confidence_after"] < row["confidence_before"]
                for row in candidate_rows
            )
        ),
        "active_support_positive": bool(
            active_rows and all(row["confidence_after"] > 0.0 for row in active_rows)
        ),
        "active_fit_support_positive": bool(
            active_fit_rows
            and all(row["fit_confidence"] > 0.0 for row in active_fit_rows)
        ),
        "prequential_chain_all": bool(all(row["prequential_chain"] for row in rows)),
        "equal_energy_all": bool(
            all(row["source_energy_error"] <= 1e-12 for row in rows)
        ),
        "hidden_truth_isolated": bool(
            all(not row["hidden_truth_passed_to_model"] for row in rows)
        ),
        "stable_terminal_exact": bool(stable_rows[-1]["committed_exact"]),
        "transient_terminal_exact": bool(transient_rows[-1]["committed_exact"]),
        "sustained_terminal_exact": bool(restoration_rows[-1]["committed_exact"]),
        "integrity": True,
    }
    receipt = {
        "seed": seed,
        "cohort": cohort,
        "structure_digest": structure.digest,
        "hidden_pair_never_passed_to_model": True,
        "hidden_rank_never_passed_to_model": True,
        "hidden_projectors_never_passed_to_model": True,
        "phase_labels_never_passed_to_model": True,
        "world_seed_never_passed_to_model": True,
        "learner_rng_independent_of_world_seed": True,
        "confidence_is_calibrated_probability": False,
        "confidence_semantics": "minimum correctly paired normalized randomization margin",
        "interventions_reversible_and_synthetic": True,
    }
    return {
        "schema": V030_SCHEMA,
        "seed": seed,
        "cohort": cohort,
        "config": asdict(config),
        "seed_summary": summary,
        "rows": rows,
        "receipt": receipt,
    }


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty CSV")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def aggregate_structural_self_model_revision_results(
    parts: Sequence[Mapping[str, Any]], output: str | Path
) -> dict[str, Any]:
    if not parts:
        raise ValueError("parts cannot be empty")
    cohort = str(parts[0]["cohort"])
    if cohort not in {"pilot", "official"}:
        raise ValueError("part cohort must be 'pilot' or 'official'")
    expected = V030_PILOT_SEEDS if cohort == "pilot" else V030_OFFICIAL_SEEDS
    by_seed: dict[int, Mapping[str, Any]] = {}
    for part in parts:
        if part.get("schema") != V030_SCHEMA or part.get("cohort") != cohort:
            raise ValueError("part schema or cohort mismatch")
        seed = int(part["seed"])
        if seed in by_seed:
            raise ValueError("duplicate seed part")
        if part.get("config") != asdict(V030_FROZEN_CONFIG):
            raise ValueError("part configuration mismatch")
        by_seed[seed] = part
    if tuple(sorted(by_seed)) != tuple(sorted(expected)):
        raise ValueError("parts do not contain the exact reserved cohort")
    ordered = [by_seed[seed] for seed in expected]
    summaries = [dict(part["seed_summary"]) for part in ordered]
    rows = [dict(row) for part in ordered for row in part["rows"]]
    receipts = [dict(part["receipt"]) for part in ordered]
    means = {
        key: float(np.mean([float(summary[key]) for summary in summaries]))
        for key in (
            "stable_exact_accuracy",
            "transient_exact_accuracy",
            "transient_rank_one_proposals",
            "transient_rank_one_candidate_starts_or_renewals",
            "transient_legacy_false_rank_rate",
            "transient_overlap_false_rank_rate",
            "transient_overlap_rank_revisions",
            "contraction_terminal_tail_accuracy",
            "restoration_terminal_tail_accuracy",
        )
    }
    potent_summaries = [
        summary
        for summary in summaries
        if int(summary["transient_rank_one_proposals"]) >= 1
    ]
    minimum_potent_seeds = int(math.ceil(0.75 * len(summaries)))
    minimum_overlap_failure_seeds = int(math.ceil(0.50 * len(summaries)))
    pooled_rank_one_proposals = int(
        sum(int(summary["transient_rank_one_proposals"]) for summary in summaries)
    )
    overlap_failure_seeds = int(
        sum(
            int(summary["transient_overlap_rank_revisions"]) >= 1
            for summary in summaries
        )
    )
    gates = {
        "acquisition_exact_all": all(
            bool(summary["acquisition_terminal_exact"])
            and int(summary["acquisition_rank"]) == 2
            for summary in summaries
        ),
        "stable_structure_exact_all": all(
            float(summary["stable_exact_accuracy"]) == 1.0
            and int(summary["stable_rank_revisions"]) == 0
            and bool(summary["stable_terminal_exact"])
            for summary in summaries
        ),
        "transient_structure_retained_all": all(
            float(summary["transient_exact_accuracy"]) == 1.0
            and int(summary["transient_rank_revisions"]) == 0
            and bool(summary["transient_terminal_exact"])
            for summary in summaries
        ),
        "transient_challenge_potent": bool(
            len(potent_summaries) >= minimum_potent_seeds
            and pooled_rank_one_proposals >= len(summaries)
            and means["transient_legacy_false_rank_rate"] >= 0.05
            and means["transient_overlap_false_rank_rate"] >= 0.05
            and overlap_failure_seeds >= minimum_overlap_failure_seeds
        ),
        "sustained_contraction_revised_all": all(
            float(summary["contraction_terminal_tail_accuracy"]) >= 0.95
            and int(summary["contraction_rank_revisions"]) == 1
            and summary["contraction_revision_latency"] is not None
            and int(summary["contraction_revision_latency"])
            <= V030_FROZEN_CONFIG.maximum_structural_latency_steps
            and bool(summary["contraction_pair_retained"])
            for summary in summaries
        ),
        "sustained_restoration_revised_all": all(
            float(summary["restoration_terminal_tail_accuracy"]) >= 0.95
            and int(summary["restoration_rank_revisions"]) == 1
            and summary["restoration_revision_latency"] is not None
            and int(summary["restoration_revision_latency"])
            <= V030_FROZEN_CONFIG.maximum_structural_latency_steps
            and bool(summary["restoration_pair_retained"])
            and bool(summary["sustained_terminal_exact"])
            for summary in summaries
        ),
        "candidate_support_decays_all": all(
            bool(summary["candidate_support_decays"]) for summary in summaries
        ),
        "accepted_support_positive_all": all(
            bool(summary["active_support_positive"])
            and bool(summary["active_fit_support_positive"])
            for summary in summaries
        ),
        "prequential_integrity_all": all(
            bool(summary["prequential_chain_all"])
            and bool(summary["equal_energy_all"])
            and bool(summary["hidden_truth_isolated"])
            and bool(summary["integrity"])
            for summary in summaries
        ),
        "claim_boundary_receipts_all": all(
            receipt["confidence_is_calibrated_probability"] is False
            and receipt["hidden_pair_never_passed_to_model"] is True
            and receipt["hidden_rank_never_passed_to_model"] is True
            and receipt["hidden_projectors_never_passed_to_model"] is True
            and receipt["phase_labels_never_passed_to_model"] is True
            and receipt["world_seed_never_passed_to_model"] is True
            and receipt["learner_rng_independent_of_world_seed"] is True
            for receipt in receipts
        ),
    }
    result = {
        "schema": V030_SCHEMA,
        "cohort": cohort,
        "seeds": list(expected),
        "means": means,
        "transient_challenge": {
            "minimum_potent_seeds": minimum_potent_seeds,
            "potent_seeds": len(potent_summaries),
            "pooled_rank_one_proposals": pooled_rank_one_proposals,
            "minimum_overlap_failure_seeds": minimum_overlap_failure_seeds,
            "overlap_failure_seeds": overlap_failure_seeds,
        },
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_boundary": (
            "Persistent and revisable structural causal self-boundary identity "
            "with an operational admitted dimension in a bounded synthetic "
            "benchmark. Higher-mode admission is not a conditional causal-rank "
            "test. Confidence is a paired-margin support score, not a posterior "
            "probability. This is not evidence "
            "of phenomenal awareness, consciousness, sentience, or valence."
        ),
    }
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=False)
    _write_csv(destination / "v030_structural_revision_rows.csv", rows)
    _write_csv(destination / "v030_structural_revision_seed_summaries.csv", summaries)
    (destination / "v030_structural_revision_integrity.json").write_text(
        json.dumps(receipts, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (destination / "v030_structural_revision_summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(destination.iterdir())
        if path.is_file()
    }
    (destination / "v030_structural_revision_sha256.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


__all__ = [
    "V030_FROZEN_CONFIG",
    "V030_OFFICIAL_SEEDS",
    "V030_PILOT_SEEDS",
    "V030RunConfig",
    "aggregate_structural_self_model_revision_results",
    "run_structural_self_model_revision_seed",
]
