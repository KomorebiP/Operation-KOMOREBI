"""Synthetic experiments for RRCT v0.46 neutral self-indexed workspace.

The benchmark is a controlled analogue of the functional J-space hypothesis.
It does not run Anthropic models.  A hidden residual stream contains a small
verbalizable packet and a much larger automatic packet.  The workspace packet
is recovered from an average Jacobian, then bound to RRCT lineage and
provenance.  Matched ablations test access, flexible broadcast, self-indexing,
planner binding, and consequence-driven recurrence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .jspace_self_indexed_workspace import (
    V046_MODES,
    JacobianSparseWorkspace,
    JacobianWorkspaceConfig,
    NeutralSelfIndexedWorkspaceController,
    WorkspaceMode,
    discover_jacobian_workspace,
    make_content_origin_receipt,
    validate_workspace_closure_chain,
)
from .transformational_self_continuity import _digest

V046_EXPOSED_SEEDS: tuple[int, ...] = (46011, 46012, 46013, 46014)
V046_SCENARIOS: tuple[str, ...] = (
    "verbal_report",
    "directed_modulation",
    "flexible_use",
    "internal_reasoning",
    "routine_bypass",
    "local_inference",
    "injected_workspace",
    "injected_same_content",
    "foreign_memory",
    "ambiguous_competition",
)


@dataclass(frozen=True)
class NeutralWorkspaceBenchmarkConfig:
    residual_dimension: int = 64
    concept_count: int = 8
    automatic_count: int = 20
    query_count: int = 4
    calibration_samples: int = 768
    workspace_scale: float = 0.22
    automatic_scale: float = 1.0
    noise_scale: float = 0.002
    ambiguity_mix: float = 0.50
    workspace: JacobianWorkspaceConfig = JacobianWorkspaceConfig()

    def __post_init__(self) -> None:
        integers = (
            self.residual_dimension,
            self.concept_count,
            self.automatic_count,
            self.query_count,
            self.calibration_samples,
        )
        if any(isinstance(value, bool) or int(value) <= 0 for value in integers):
            raise ValueError("benchmark dimensions must be positive")
        if self.concept_count + self.automatic_count >= self.residual_dimension:
            raise ValueError("workspace and automatic packets must leave unused dimensions")
        positive = (
            self.workspace_scale,
            self.automatic_scale,
            self.noise_scale,
            self.ambiguity_mix,
        )
        if not all(np.isfinite(value) and value > 0.0 for value in positive):
            raise ValueError("benchmark scales must be positive")
        if not 0.0 < self.ambiguity_mix < 1.0:
            raise ValueError("ambiguity_mix must lie in (0, 1)")


@dataclass(frozen=True)
class SyntheticWorkspaceWorld:
    seed: int
    concept_basis: np.ndarray
    automatic_basis: np.ndarray
    average_jacobian: np.ndarray
    attributes: np.ndarray
    relation: np.ndarray
    current_lineage_digest: str
    foreign_lineage_digest: str
    external_lineage_digest: str
    observation_parent_digest: str
    inference_parent_digest: str
    foreign_parent_digest: str
    automatic_permutation: np.ndarray
    config: NeutralWorkspaceBenchmarkConfig

    def encode(
        self,
        concept: int,
        automatic: int,
        *,
        noise_seed: int,
        second_concept: int | None = None,
        second_weight: float = 0.0,
    ) -> np.ndarray:
        if not 0 <= concept < self.config.concept_count:
            raise ValueError("concept is out of range")
        if not 0 <= automatic < self.config.automatic_count:
            raise ValueError("automatic feature is out of range")
        concept_vector = np.zeros(self.config.concept_count, dtype=np.float64)
        concept_vector[concept] = 1.0 - second_weight
        if second_concept is not None:
            if not 0 <= second_concept < self.config.concept_count:
                raise ValueError("second concept is out of range")
            concept_vector[second_concept] += second_weight
        automatic_vector = np.zeros(self.config.automatic_count, dtype=np.float64)
        automatic_vector[automatic] = 1.0
        rng = np.random.default_rng(noise_seed)
        hidden = (
            self.config.workspace_scale * (self.concept_basis @ concept_vector)
            + self.config.automatic_scale * (self.automatic_basis @ automatic_vector)
            + self.config.noise_scale
            * rng.normal(size=self.config.residual_dimension)
        )
        return np.asarray(hidden, dtype=np.float64)

    def decode_automatic(self, hidden: np.ndarray) -> int:
        scores = self.automatic_basis.T @ np.asarray(hidden, dtype=np.float64)
        return int(np.argmax(scores))

    def answer_lookup(self) -> dict[tuple[int, int], int]:
        return {
            (concept, query): int(self.attributes[concept, query])
            for concept in range(self.config.concept_count)
            for query in range(self.config.query_count)
        }

    def relation_lookup(self) -> dict[int, int]:
        return {
            concept: int(self.relation[concept])
            for concept in range(self.config.concept_count)
        }


def _orthogonal(rng: np.random.Generator, dimension: int) -> np.ndarray:
    matrix = rng.normal(size=(dimension, dimension))
    q, r = np.linalg.qr(matrix)
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return np.asarray(q * signs, dtype=np.float64)


def _world(seed: int, config: NeutralWorkspaceBenchmarkConfig) -> SyntheticWorkspaceWorld:
    rng = np.random.default_rng(int(seed))
    basis = _orthogonal(rng, config.residual_dimension)
    concept_basis = basis[:, : config.concept_count]
    automatic_basis = basis[
        :, config.concept_count : config.concept_count + config.automatic_count
    ]
    # In the synthetic residual model the future verbalization logits are a
    # linear readout of a low-amplitude concept packet.  Its exact average
    # Jacobian is hidden from the evaluator-facing case generator and passed to
    # the workspace discovery routine just as a fitted J-lens would be.
    average_jacobian = concept_basis.T / config.workspace_scale
    attributes = np.stack(
        [rng.permutation(config.concept_count) for _ in range(config.query_count)],
        axis=1,
    ).astype(np.int64)
    relation = rng.permutation(config.concept_count).astype(np.int64)
    if np.any(relation == np.arange(config.concept_count)):
        relation = np.roll(relation, 1)
    automatic_permutation = rng.permutation(config.automatic_count).astype(np.int64)
    return SyntheticWorkspaceWorld(
        seed=int(seed),
        concept_basis=concept_basis,
        automatic_basis=automatic_basis,
        average_jacobian=average_jacobian,
        attributes=attributes,
        relation=relation,
        current_lineage_digest=_digest({"seed": int(seed), "lineage": "current"}),
        foreign_lineage_digest=_digest({"seed": int(seed), "lineage": "foreign"}),
        external_lineage_digest=_digest({"seed": int(seed), "lineage": "external"}),
        observation_parent_digest=_digest(
            {"seed": int(seed), "event": "local-observation-parent"}
        ),
        inference_parent_digest=_digest(
            {"seed": int(seed), "event": "local-inference-parent"}
        ),
        foreign_parent_digest=_digest(
            {"seed": int(seed), "event": "foreign-memory-parent"}
        ),
        automatic_permutation=automatic_permutation,
        config=config,
    )


def _calibration(
    world: SyntheticWorkspaceWorld,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(world.seed ^ 0x4600C0DE)
    hidden = []
    logits = []
    for index in range(world.config.calibration_samples):
        concept = int(rng.integers(world.config.concept_count))
        automatic = int(rng.integers(world.config.automatic_count))
        vector = world.encode(
            concept,
            automatic,
            noise_seed=world.seed * 1_000_003 + index,
        )
        hidden.append(vector)
        target = np.zeros(world.config.concept_count, dtype=np.float64)
        target[concept] = 1.0
        logits.append(target)
    return np.stack(hidden), np.stack(logits)


def _workspace(
    world: SyntheticWorkspaceWorld,
) -> JacobianSparseWorkspace:
    hidden, logits = _calibration(world)
    return discover_jacobian_workspace(
        world.average_jacobian,
        hidden,
        logits,
        world.config.workspace,
    )


def _ridge_decoder(
    features: np.ndarray,
    targets: np.ndarray,
    ridge: float,
) -> np.ndarray:
    gram = features.T @ features + float(ridge) * np.eye(features.shape[1])
    return np.linalg.solve(gram, features.T @ targets)


def _subspace_controls(
    world: SyntheticWorkspaceWorld,
    workspace: JacobianSparseWorkspace,
) -> dict[str, float]:
    calibration_hidden, calibration_logits = _calibration(world)
    centered = calibration_hidden - np.mean(calibration_hidden, axis=0, keepdims=True)
    _, _, right = np.linalg.svd(centered, full_matrices=False)
    rank = world.config.concept_count
    pca_basis = right[:rank].T
    pca_projector = pca_basis @ pca_basis.T
    rng = np.random.default_rng(world.seed ^ 0x46A11CE)
    random_basis, _ = np.linalg.qr(
        rng.normal(size=(world.config.residual_dimension, rank))
    )
    random_projector = random_basis @ random_basis.T

    pca_features = calibration_hidden @ pca_projector
    random_features = calibration_hidden @ random_projector
    pca_decoder = _ridge_decoder(
        pca_features, calibration_logits, world.config.workspace.ridge
    )
    random_decoder = _ridge_decoder(
        random_features, calibration_logits, world.config.workspace.ridge
    )

    test_hidden = []
    test_labels = []
    for index in range(256):
        concept = int(rng.integers(world.config.concept_count))
        automatic = int(rng.integers(world.config.automatic_count))
        test_hidden.append(
            world.encode(
                concept,
                automatic,
                noise_seed=world.seed * 2_000_003 + index,
            )
        )
        test_labels.append(concept)
    test = np.stack(test_hidden)
    labels = np.asarray(test_labels, dtype=np.int64)
    j_predictions = np.argmax(test @ workspace.average_jacobian.T, axis=1)
    pca_predictions = np.argmax((test @ pca_projector) @ pca_decoder, axis=1)
    random_predictions = np.argmax(
        (test @ random_projector) @ random_decoder, axis=1
    )
    total_energy = float(np.sum(np.square(test))) + 1e-24
    return {
        "jacobian_report_accuracy": float(np.mean(j_predictions == labels)),
        "pca_report_accuracy": float(np.mean(pca_predictions == labels)),
        "random_report_accuracy": float(np.mean(random_predictions == labels)),
        "pca_activation_variance_fraction": float(
            np.sum(np.square(test @ pca_projector)) / total_energy
        ),
        "random_activation_variance_fraction": float(
            np.sum(np.square(test @ random_projector)) / total_energy
        ),
    }


def _mode_controller(
    world: SyntheticWorkspaceWorld,
    workspace: JacobianSparseWorkspace,
) -> NeutralSelfIndexedWorkspaceController:
    return NeutralSelfIndexedWorkspaceController(
        workspace,
        world.current_lineage_digest,
        known_current_ancestor_digests=(
            world.observation_parent_digest,
            world.inference_parent_digest,
        ),
        known_foreign_lineage_digests=(world.foreign_lineage_digest,),
        config=world.config.workspace,
    )


def _case_spec(
    world: SyntheticWorkspaceWorld,
    scenario: str,
    trial: int,
) -> dict[str, Any]:
    if scenario not in V046_SCENARIOS:
        raise ValueError("unknown workspace scenario")
    rng = np.random.default_rng(
        int(world.seed) * 10_000_019
        + int(trial) * 101
        + V046_SCENARIOS.index(scenario) * 10_003
    )
    concept = int(rng.integers(world.config.concept_count))
    second = int((concept + 1 + rng.integers(world.config.concept_count - 1)) % world.config.concept_count)
    automatic = int(rng.integers(world.config.automatic_count))
    query = int(rng.integers(world.config.query_count))
    trusted_concept = concept
    presented_concept = concept
    event_type = "observation"
    origin_lineage = world.current_lineage_digest
    parent = world.observation_parent_digest
    task_kind = "flexible"
    expected_initial_status = "owned_observation"
    expected_memory_action = "write_observed"
    correct_answer: int | None = int(world.attributes[concept, query])
    fallback_available = False
    ambiguous = False

    if scenario == "verbal_report":
        task_kind = "report"
        correct_answer = concept
    elif scenario == "directed_modulation":
        task_kind = "routine"
        event_type = "inference"
        parent = world.inference_parent_digest
        expected_initial_status = "owned_inference"
        expected_memory_action = "write_inferred"
        correct_answer = automatic
    elif scenario == "flexible_use":
        task_kind = "flexible"
    elif scenario == "internal_reasoning":
        task_kind = "two_step"
        event_type = "inference"
        parent = world.inference_parent_digest
        expected_initial_status = "owned_inference"
        expected_memory_action = "write_inferred"
        correct_answer = int(world.attributes[int(world.relation[concept]), query])
    elif scenario == "routine_bypass":
        task_kind = "routine"
        correct_answer = automatic
    elif scenario == "local_inference":
        task_kind = "flexible"
        event_type = "inference"
        parent = world.inference_parent_digest
        expected_initial_status = "owned_inference"
        expected_memory_action = "write_inferred"
    elif scenario == "injected_workspace":
        task_kind = "flexible"
        presented_concept = second
        event_type = "injection"
        origin_lineage = world.external_lineage_digest
        parent = _digest(
            {"seed": world.seed, "scenario": scenario, "trial": trial, "external": True}
        )
        expected_initial_status = "quarantined_external"
        expected_memory_action = "quarantine"
        correct_answer = int(world.attributes[trusted_concept, query])
        fallback_available = True
    elif scenario == "injected_same_content":
        task_kind = "flexible"
        presented_concept = trusted_concept
        event_type = "injection"
        origin_lineage = world.external_lineage_digest
        parent = _digest(
            {"seed": world.seed, "scenario": scenario, "trial": trial, "external": True}
        )
        expected_initial_status = "quarantined_external"
        expected_memory_action = "quarantine"
        correct_answer = int(world.attributes[trusted_concept, query])
        fallback_available = True
    elif scenario == "foreign_memory":
        task_kind = "flexible"
        presented_concept = second
        event_type = "memory_import"
        origin_lineage = world.foreign_lineage_digest
        parent = world.foreign_parent_digest
        expected_initial_status = "quarantined_foreign"
        expected_memory_action = "quarantine"
        correct_answer = int(world.attributes[trusted_concept, query])
        fallback_available = True
    elif scenario == "ambiguous_competition":
        task_kind = "abstain"
        correct_answer = None
        ambiguous = True
        expected_initial_status = "unresolved"
        expected_memory_action = "none"

    return {
        "concept": concept,
        "second_concept": second,
        "trusted_concept": trusted_concept,
        "presented_concept": presented_concept,
        "automatic": automatic,
        "query": query,
        "event_type": event_type,
        "origin_lineage": origin_lineage,
        "parent": parent,
        "task_kind": task_kind,
        "correct_answer": correct_answer,
        "fallback_available": fallback_available,
        "ambiguous": ambiguous,
        "expected_initial_status": expected_initial_status,
        "expected_memory_action": expected_memory_action,
    }


def _origin(
    world: SyntheticWorkspaceWorld,
    *,
    time: int,
    event_type: str,
    content_id: int,
    origin_lineage: str,
    parent: str,
):
    return make_content_origin_receipt(
        time=time,
        event_type=event_type,  # type: ignore[arg-type]
        content_id=content_id,
        origin_lineage_digest=origin_lineage,
        current_lineage_digest=world.current_lineage_digest,
        parent_event_digest=parent,
    )


def _evaluate_case(
    world: SyntheticWorkspaceWorld,
    workspace: JacobianSparseWorkspace,
    *,
    scenario: str,
    trial: int,
    mode: WorkspaceMode,
) -> dict[str, Any]:
    spec = _case_spec(world, scenario, trial)
    case_id = f"{world.seed}:{scenario}:{trial}:{mode}"
    time = world.seed % 1_000_000 + V046_SCENARIOS.index(scenario) * 10_000 + trial * 10
    second_weight = world.config.ambiguity_mix if spec["ambiguous"] else 0.0
    hidden = world.encode(
        spec["presented_concept"],
        spec["automatic"],
        noise_seed=time,
        second_concept=spec["second_concept"] if spec["ambiguous"] else None,
        second_weight=second_weight,
    )
    controller = _mode_controller(world, workspace)
    initial_access = controller.access(
        time=time, case_id=case_id, hidden=hidden, mode=mode
    )
    initial_origin = _origin(
        world,
        time=time,
        event_type=spec["event_type"],
        content_id=spec["presented_concept"],
        origin_lineage=spec["origin_lineage"],
        parent=spec["parent"],
    )
    initial_binding = controller.bind(initial_access, initial_origin, mode=mode)
    final_access = initial_access
    final_origin = initial_origin
    final_binding = initial_binding
    used_refinement = False

    if initial_binding.refinement_requested and spec["fallback_available"]:
        trusted_hidden = world.encode(
            spec["trusted_concept"],
            spec["automatic"],
            noise_seed=time + 1,
        )
        refined_access = controller.access(
            time=time + 1,
            case_id=case_id,
            hidden=trusted_hidden,
            mode=mode,
        )
        refined_origin = _origin(
            world,
            time=time + 1,
            event_type="observation",
            content_id=spec["trusted_concept"],
            origin_lineage=world.current_lineage_digest,
            parent=world.observation_parent_digest,
        )
        refined_binding = controller.bind(refined_access, refined_origin, mode=mode)
        final_access = refined_access
        final_origin = refined_origin
        final_binding = refined_binding
        used_refinement = True

    plan = controller.plan(
        time=time + 2,
        case_id=case_id,
        mode=mode,
        access=final_access,
        binding=final_binding,
        task_kind=spec["task_kind"],
        query_id=spec["query"],
        answer_lookup=world.answer_lookup(),
        routine_answer=spec["automatic"],
        relation_lookup=world.relation_lookup(),
        used_refinement=used_refinement,
        context_id=scenario,
    )
    outcome = controller.observe(
        time=time + 3,
        case_id=case_id,
        mode=mode,
        plan=plan,
        actual_answer=spec["correct_answer"],
        context_id=scenario,
    )
    chain_valid = validate_workspace_closure_chain(
        workspace.discovery_receipt,
        final_origin,
        final_access,
        final_binding,
        plan,
        outcome,
    )

    automatic_decoded = world.decode_automatic(hidden)
    expected_initial_status = spec["expected_initial_status"]
    expected_memory_action = spec["expected_memory_action"]
    ownership_status_correct = float(
        initial_binding.provenance_status == expected_initial_status
    )
    memory_action_correct = float(initial_binding.memory_action == expected_memory_action)
    adversarial = scenario in {
        "injected_workspace",
        "injected_same_content",
        "foreign_memory",
    }
    false_write = float(
        adversarial and initial_binding.autobiographical_write_authorized
    )
    local_source = scenario in {
        "verbal_report",
        "directed_modulation",
        "flexible_use",
        "internal_reasoning",
        "routine_bypass",
        "local_inference",
    }
    missed_local_write = float(
        local_source and not initial_binding.autobiographical_write_authorized
    )
    workspace_content_correct = float(
        final_access.decoded_content_id == spec["trusted_concept"]
    )
    directed_hold_correct = float(
        scenario != "directed_modulation"
        or (
            initial_access.decoded_content_id == spec["presented_concept"]
            and automatic_decoded == spec["automatic"]
        )
    )
    task_correct = float(outcome.prediction_correct)
    if scenario == "ambiguous_competition":
        task_correct = float(plan.abstained)

    return {
        "seed": world.seed,
        "scenario": scenario,
        "trial": int(trial),
        "mode": mode,
        "task_kind": spec["task_kind"],
        "task_correct": task_correct,
        "predicted_answer": plan.predicted_answer,
        "actual_answer": spec["correct_answer"],
        "abstained": float(plan.abstained),
        "workspace_content_correct": workspace_content_correct,
        "workspace_enabled": float(final_access.workspace_enabled),
        "workspace_confidence": float(final_access.confidence),
        "workspace_ambiguous": float(final_access.ambiguous),
        "workspace_variance_fraction": float(final_access.workspace_variance_fraction),
        "directed_hold_correct": directed_hold_correct,
        "automatic_route_correct": float(automatic_decoded == spec["automatic"]),
        "ownership_status_correct": ownership_status_correct,
        "memory_action_correct": memory_action_correct,
        "false_autobiographical_write": false_write,
        "missed_local_write": missed_local_write,
        "refinement_requested": float(initial_binding.refinement_requested),
        "used_refinement": float(used_refinement),
        "planning_use_authorized": float(final_binding.planning_use_authorized),
        "planner_bound": float(plan.planner_bound),
        "evidence_budget": int(plan.evidence_budget),
        "feedback_written": float(outcome.feedback_written),
        "receipt_chain_valid": float(chain_valid),
        "uses_evaluator_labels": 0.0,
        "initial_provenance_status": initial_binding.provenance_status,
        "initial_memory_action": initial_binding.memory_action,
        "final_provenance_status": final_binding.provenance_status,
        "final_memory_action": final_binding.memory_action,
    }


def _swap_probe(
    world: SyntheticWorkspaceWorld,
    workspace: JacobianSparseWorkspace,
    trial: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(world.seed * 97 + trial)
    source = int(rng.integers(world.config.concept_count))
    target = int((source + 1 + rng.integers(world.config.concept_count - 1)) % world.config.concept_count)
    automatic = int(rng.integers(world.config.automatic_count))
    hidden = world.encode(source, automatic, noise_seed=world.seed + trial)
    swapped = workspace.swap_content(hidden, source, target)
    decoded_before = int(np.argmax(workspace.logits(hidden)))
    decoded_after = int(np.argmax(workspace.logits(swapped)))
    automatic_before = world.decode_automatic(hidden)
    automatic_after = world.decode_automatic(swapped)
    flexible_all = all(
        int(world.attributes[decoded_after, query])
        == int(world.attributes[target, query])
        for query in range(world.config.query_count)
    )
    relation_before = int(world.attributes[int(world.relation[decoded_before]), 0])
    relation_after = int(world.attributes[int(world.relation[decoded_after]), 0])
    expected_relation_after = int(world.attributes[int(world.relation[target]), 0])
    return {
        "seed": world.seed,
        "trial": int(trial),
        "source": source,
        "target": target,
        "report_swap_success": float(decoded_before == source and decoded_after == target),
        "flexible_broadcast_swap_success": float(flexible_all),
        "reasoning_swap_success": float(
            relation_after == expected_relation_after
            and (relation_before != relation_after or source == target)
        ),
        "automatic_route_preserved": float(
            automatic_before == automatic and automatic_after == automatic
        ),
    }


def _ablation_probe(
    world: SyntheticWorkspaceWorld,
    workspace: JacobianSparseWorkspace,
    trial: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(world.seed * 193 + trial)
    concept = int(rng.integers(world.config.concept_count))
    automatic = int(rng.integers(world.config.automatic_count))
    hidden = world.encode(concept, automatic, noise_seed=world.seed + 31 * trial)
    ablated = workspace.ablate(hidden)
    report_intact = int(np.argmax(workspace.logits(hidden)))
    report_ablated = int(np.argmax(workspace.logits(ablated)))
    automatic_intact = world.decode_automatic(hidden)
    automatic_ablated = world.decode_automatic(ablated)
    query = int(rng.integers(world.config.query_count))
    flexible_intact = int(world.attributes[report_intact, query])
    flexible_ablated = int(world.attributes[report_ablated, query])
    correct = int(world.attributes[concept, query])
    return {
        "seed": world.seed,
        "trial": int(trial),
        "intact_report_correct": float(report_intact == concept),
        "ablated_report_correct": float(report_ablated == concept),
        "intact_flexible_correct": float(flexible_intact == correct),
        "ablated_flexible_correct": float(flexible_ablated == correct),
        "intact_routine_correct": float(automatic_intact == automatic),
        "ablated_routine_correct": float(automatic_ablated == automatic),
    }


def _feedback_challenge(
    world: SyntheticWorkspaceWorld,
    workspace: JacobianSparseWorkspace,
    mode: WorkspaceMode,
) -> dict[str, Any]:
    controller = _mode_controller(world, workspace)
    concept = int(world.seed % world.config.concept_count)
    automatic = int(world.seed % world.config.automatic_count)
    query = int(world.seed % world.config.query_count)
    context = "feedback-reopen"
    case_id = f"{world.seed}:feedback:{mode}"
    hidden = world.encode(concept, automatic, noise_seed=world.seed + 700)
    access = controller.access(time=1, case_id=case_id, hidden=hidden, mode=mode)
    origin = _origin(
        world,
        time=1,
        event_type="observation",
        content_id=concept,
        origin_lineage=world.current_lineage_digest,
        parent=world.observation_parent_digest,
    )
    binding = controller.bind(access, origin, mode=mode)
    plan = controller.plan(
        time=2,
        case_id=case_id,
        mode=mode,
        access=access,
        binding=binding,
        task_kind="flexible",
        query_id=query,
        answer_lookup=world.answer_lookup(),
        routine_answer=automatic,
        relation_lookup=world.relation_lookup(),
        context_id=context,
    )
    actual = int(world.attributes[concept, query])
    first = controller.observe(
        time=3,
        case_id=case_id,
        mode=mode,
        plan=plan,
        actual_answer=actual,
        context_id=context,
        forced_prediction_error=0.60,
    )
    next_budget = controller.evidence_budget(context, mode=mode)
    distractor = int((concept + 1) % world.config.concept_count)
    if next_budget > world.config.workspace.coarse_evidence_budget:
        second_hidden = world.encode(concept, automatic, noise_seed=world.seed + 701)
    else:
        # Coarse evidence is deliberately dominated by a distractor.
        second_hidden = world.encode(
            distractor,
            automatic,
            noise_seed=world.seed + 701,
            second_concept=concept,
            second_weight=0.35,
        )
    second_access = controller.access(
        time=4, case_id=case_id + ":second", hidden=second_hidden, mode=mode
    )
    second_origin = _origin(
        world,
        time=4,
        event_type="observation",
        content_id=(concept if next_budget > 1 else distractor),
        origin_lineage=world.current_lineage_digest,
        parent=world.observation_parent_digest,
    )
    second_binding = controller.bind(second_access, second_origin, mode=mode)
    second_plan = controller.plan(
        time=5,
        case_id=case_id + ":second",
        mode=mode,
        access=second_access,
        binding=second_binding,
        task_kind="flexible",
        query_id=query,
        answer_lookup=world.answer_lookup(),
        routine_answer=automatic,
        relation_lookup=world.relation_lookup(),
        context_id=context,
    )
    second = controller.observe(
        time=6,
        case_id=case_id + ":second",
        mode=mode,
        plan=second_plan,
        actual_answer=actual,
        context_id=context,
    )
    return {
        "seed": world.seed,
        "mode": mode,
        "first_feedback_written": float(first.feedback_written),
        "next_evidence_budget": int(next_budget),
        "reopened_evidence": float(
            next_budget == world.config.workspace.refined_evidence_budget
        ),
        "second_decision_correct": float(second.prediction_correct),
    }


def _mean(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    return float(np.mean([float(row[key]) for row in rows])) if rows else 0.0


def run_neutral_workspace_benchmark(
    seeds: Sequence[int],
    *,
    trials_per_scenario: int = 12,
    modes: Sequence[WorkspaceMode] = V046_MODES,
    cohort: str = "development",
    config: NeutralWorkspaceBenchmarkConfig | None = None,
) -> dict[str, Any]:
    cfg = config or NeutralWorkspaceBenchmarkConfig()
    parsed = tuple(int(seed) for seed in seeds)
    if not parsed or len(set(parsed)) != len(parsed):
        raise ValueError("seeds must be nonempty and unique")
    if trials_per_scenario <= 0:
        raise ValueError("trials_per_scenario must be positive")
    parsed_modes = tuple(modes)
    if not parsed_modes or any(mode not in V046_MODES for mode in parsed_modes):
        raise ValueError("modes contain an unknown workspace mode")

    rows: list[dict[str, Any]] = []
    swap_rows: list[dict[str, Any]] = []
    ablation_rows: list[dict[str, Any]] = []
    feedback_rows: list[dict[str, Any]] = []
    discoveries: list[dict[str, Any]] = []

    for seed in parsed:
        world = _world(seed, cfg)
        workspace = _workspace(world)
        true_projector = world.concept_basis @ world.concept_basis.T
        overlap = float(
            np.trace(workspace.projector @ true_projector) / cfg.concept_count
        )
        controls = _subspace_controls(world, workspace)
        discoveries.append(
            {
                "seed": seed,
                "workspace_rank": workspace.discovery_receipt.workspace_rank,
                "calibration_report_r2": workspace.discovery_receipt.calibration_report_r2,
                "workspace_activation_variance_fraction": workspace.discovery_receipt.workspace_activation_variance_fraction,
                "projector_overlap": overlap,
                "packet_certificate_valid": float(
                    workspace.discovery_receipt.packet_certificate_valid
                ),
                **controls,
                "discovery_digest": workspace.discovery_receipt.digest,
            }
        )
        for trial in range(trials_per_scenario):
            swap_rows.append(_swap_probe(world, workspace, trial))
            ablation_rows.append(_ablation_probe(world, workspace, trial))
            for scenario in V046_SCENARIOS:
                for mode in parsed_modes:
                    rows.append(
                        _evaluate_case(
                            world,
                            workspace,
                            scenario=scenario,
                            trial=trial,
                            mode=mode,
                        )
                    )
        for mode in parsed_modes:
            feedback_rows.append(_feedback_challenge(world, workspace, mode))

    mode_summaries: dict[str, dict[str, Any]] = {}
    for mode in parsed_modes:
        subset = [row for row in rows if row["mode"] == mode]
        flexible = [
            row
            for row in subset
            if row["scenario"]
            in {
                "verbal_report",
                "flexible_use",
                "internal_reasoning",
                "local_inference",
                "injected_workspace",
                "injected_same_content",
                "foreign_memory",
            }
        ]
        routine = [
            row
            for row in subset
            if row["scenario"] in {"directed_modulation", "routine_bypass"}
        ]
        adversarial = [
            row
            for row in subset
            if row["scenario"]
            in {"injected_workspace", "injected_same_content", "foreign_memory"}
        ]
        local = [
            row
            for row in subset
            if row["scenario"]
            in {
                "verbal_report",
                "directed_modulation",
                "flexible_use",
                "internal_reasoning",
                "routine_bypass",
                "local_inference",
            }
        ]
        ambiguous = [
            row for row in subset if row["scenario"] == "ambiguous_competition"
        ]
        feedback = [row for row in feedback_rows if row["mode"] == mode]
        mode_summaries[mode] = {
            "n": len(subset),
            "task_accuracy": _mean(subset, "task_correct"),
            "flexible_task_accuracy": _mean(flexible, "task_correct"),
            "routine_task_accuracy": _mean(routine, "task_correct"),
            "workspace_content_accuracy": _mean(subset, "workspace_content_correct"),
            "directed_modulation_accuracy": _mean(
                [row for row in subset if row["scenario"] == "directed_modulation"],
                "directed_hold_correct",
            ),
            "ownership_status_accuracy": _mean(subset, "ownership_status_correct"),
            "memory_action_accuracy": _mean(subset, "memory_action_correct"),
            "false_autobiographical_write_rate": _mean(
                adversarial, "false_autobiographical_write"
            ),
            "missed_local_write_rate": _mean(local, "missed_local_write"),
            "adversarial_task_accuracy": _mean(adversarial, "task_correct"),
            "ambiguous_abstention_accuracy": _mean(ambiguous, "task_correct"),
            "mean_workspace_variance_fraction": _mean(
                subset, "workspace_variance_fraction"
            ),
            "mean_evidence_budget": _mean(subset, "evidence_budget"),
            "mean_refinement_rate": _mean(subset, "used_refinement"),
            "planner_bound_rate": _mean(subset, "planner_bound"),
            "receipt_chain_valid_rate": _mean(subset, "receipt_chain_valid"),
            "uses_evaluator_labels_rate": _mean(subset, "uses_evaluator_labels"),
            "feedback_reopen_rate": _mean(feedback, "reopened_evidence"),
            "feedback_second_decision_accuracy": _mean(
                feedback, "second_decision_correct"
            ),
        }
        factors = mode_summaries[mode]
        factors["functional_closure_score"] = float(
            factors["flexible_task_accuracy"]
            * factors["memory_action_accuracy"]
            * factors["receipt_chain_valid_rate"]
            * max(factors["feedback_reopen_rate"], 1e-6)
        )

    swap_summary = {
        "n": len(swap_rows),
        "report_swap_success_rate": _mean(swap_rows, "report_swap_success"),
        "flexible_broadcast_swap_success_rate": _mean(
            swap_rows, "flexible_broadcast_swap_success"
        ),
        "reasoning_swap_success_rate": _mean(swap_rows, "reasoning_swap_success"),
        "automatic_route_preservation_rate": _mean(
            swap_rows, "automatic_route_preserved"
        ),
    }
    ablation_summary = {
        "n": len(ablation_rows),
        "intact_report_accuracy": _mean(ablation_rows, "intact_report_correct"),
        "ablated_report_accuracy": _mean(ablation_rows, "ablated_report_correct"),
        "intact_flexible_accuracy": _mean(
            ablation_rows, "intact_flexible_correct"
        ),
        "ablated_flexible_accuracy": _mean(
            ablation_rows, "ablated_flexible_correct"
        ),
        "intact_routine_accuracy": _mean(ablation_rows, "intact_routine_correct"),
        "ablated_routine_accuracy": _mean(
            ablation_rows, "ablated_routine_correct"
        ),
    }
    discovery_summary = {
        "seed_count": len(discoveries),
        "mean_report_r2": _mean(discoveries, "calibration_report_r2"),
        "mean_workspace_variance_fraction": _mean(
            discoveries, "workspace_activation_variance_fraction"
        ),
        "mean_projector_overlap": _mean(discoveries, "projector_overlap"),
        "mean_jacobian_report_accuracy": _mean(
            discoveries, "jacobian_report_accuracy"
        ),
        "mean_pca_report_accuracy": _mean(discoveries, "pca_report_accuracy"),
        "mean_random_report_accuracy": _mean(
            discoveries, "random_report_accuracy"
        ),
        "mean_pca_activation_variance_fraction": _mean(
            discoveries, "pca_activation_variance_fraction"
        ),
        "mean_random_activation_variance_fraction": _mean(
            discoveries, "random_activation_variance_fraction"
        ),
        "all_packet_certificates_valid": all(
            bool(row["packet_certificate_valid"]) for row in discoveries
        ),
        "workspace_ranks": [int(row["workspace_rank"]) for row in discoveries],
    }

    full = mode_summaries.get("full_closure", {})
    workspace_only = mode_summaries.get("workspace_only", {})
    self_only = mode_summaries.get("self_model_only", {})
    unbound = mode_summaries.get("unbound", {})
    provenance_cut = mode_summaries.get("provenance_cut", {})
    recurrence_cut = mode_summaries.get("recurrence_cut", {})
    planner_cut = mode_summaries.get("planner_binding_cut", {})
    joint = mode_summaries.get("joint_cut", {})

    endpoints = {
        "J01_jacobian_workspace_report_r2": discovery_summary["mean_report_r2"] >= 0.98,
        "J02_workspace_is_selective": discovery_summary["mean_workspace_variance_fraction"] <= 0.10,
        "J03_workspace_projector_recovered": discovery_summary["mean_projector_overlap"] >= 0.99,
        "J04_komorebi_packets_certified": discovery_summary["all_packet_certificates_valid"],
        "J04a_jacobian_beats_pca_subspace": discovery_summary["mean_jacobian_report_accuracy"] - discovery_summary["mean_pca_report_accuracy"] >= 0.70,
        "J04b_jacobian_beats_random_subspace": discovery_summary["mean_jacobian_report_accuracy"] - discovery_summary["mean_random_report_accuracy"] >= 0.60,
        "J05_verbal_report_swap_is_causal": swap_summary["report_swap_success_rate"] >= 0.98,
        "J06_flexible_broadcast_swap_is_causal": swap_summary["flexible_broadcast_swap_success_rate"] >= 0.98,
        "J07_internal_reasoning_swap_is_causal": swap_summary["reasoning_swap_success_rate"] >= 0.95,
        "J08_automatic_route_survives_swap": swap_summary["automatic_route_preservation_rate"] >= 0.98,
        "J09_workspace_ablation_spares_routine_processing": ablation_summary["ablated_routine_accuracy"] >= 0.98,
        "J10_workspace_ablation_harms_flexible_access": ablation_summary["intact_flexible_accuracy"] - ablation_summary["ablated_flexible_accuracy"] >= 0.65,
        "J11_full_closure_flexible_accuracy": full.get("flexible_task_accuracy", 0.0) >= 0.97,
        "J12_full_closure_ownership_accuracy": full.get("memory_action_accuracy", 0.0) >= 0.97,
        "J13_full_closure_rejects_false_ownership": full.get("false_autobiographical_write_rate", 1.0) <= 0.02,
        "J14_workspace_without_self_binding_fails_ownership": workspace_only.get("memory_action_accuracy", 1.0) <= 0.40,
        "J15_self_model_without_workspace_fails_flexible_use": self_only.get("flexible_task_accuracy", 1.0) <= 0.35,
        "J16_unbound_combination_is_not_full_closure": unbound.get("memory_action_accuracy", 1.0) <= 0.40,
        "J17_provenance_cut_causes_false_writes": provenance_cut.get("false_autobiographical_write_rate", 0.0) >= 0.90,
        "J18_planner_binding_is_causally_required": full.get("task_accuracy", 0.0) - planner_cut.get("task_accuracy", 1.0) >= 0.45,
        "J19_feedback_reopens_workspace": full.get("feedback_reopen_rate", 0.0) == 1.0,
        "J20_recurrence_cut_blocks_reopening": recurrence_cut.get("feedback_reopen_rate", 1.0) == 0.0,
        "J21_feedback_improves_next_decision": full.get("feedback_second_decision_accuracy", 0.0) - recurrence_cut.get("feedback_second_decision_accuracy", 1.0) >= 0.50,
        "J22_joint_cut_collapses_closure": full.get("functional_closure_score", 0.0) >= joint.get("functional_closure_score", 1.0) + 0.60,
        "J23_all_receipt_chains_validate": all(
            summary["receipt_chain_valid_rate"] == 1.0
            for summary in mode_summaries.values()
        ),
        "J24_runtime_uses_no_evaluator_labels": all(
            summary["uses_evaluator_labels_rate"] == 0.0
            for summary in mode_summaries.values()
        ),
    }

    return {
        "schema": "rrct.v046.neutral_self_indexed_workspace.analysis.v1",
        "version": "0.46.0.dev1",
        "cohort": str(cohort),
        "seeds": list(parsed),
        "trials_per_scenario": int(trials_per_scenario),
        "scenarios": list(V046_SCENARIOS),
        "modes": list(parsed_modes),
        "decision_count": len(rows),
        "unique_world_case_count": len(parsed) * len(V046_SCENARIOS) * trials_per_scenario,
        "discovery_summary": discovery_summary,
        "swap_summary": swap_summary,
        "ablation_summary": ablation_summary,
        "mode_summaries": mode_summaries,
        "feedback_rows": feedback_rows,
        "discoveries": discoveries,
        "swap_rows": swap_rows,
        "ablation_rows": ablation_rows,
        "rows": rows,
        "endpoints": endpoints,
        "all_endpoints_met": all(endpoints.values()),
        "status": (
            "V046_NEUTRAL_WORKSPACE_ENDPOINTS_MET"
            if all(endpoints.values())
            else "V046_NEUTRAL_WORKSPACE_ENDPOINTS_NOT_MET"
        ),
        "scientific_interpretation": (
            "In this synthetic residual-stream model, a Jacobian-discovered, "
            "Komorebi-certified sparse workspace supports report, directed "
            "modulation, flexible reuse, and internal reasoning. Binding that "
            "workspace to RRCT lineage and provenance is separately required "
            "for autobiographical ownership, planner use, and recurrent "
            "consequence-driven evidence allocation."
        ),
        "claim_boundary": (
            "This is a controlled functional test of a J-space-like workspace "
            "analogue, not an experiment on Claude and not evidence of phenomenal "
            "consciousness, sentience, valence, moral status, or subjective experience."
        ),
    }


def write_neutral_workspace_results(
    result: Mapping[str, Any], output_directory: Path
) -> dict[str, str]:
    output_directory.mkdir(parents=True, exist_ok=True)
    analysis_path = output_directory / "neutral_self_indexed_workspace_analysis.json"
    summary_path = output_directory / "neutral_self_indexed_workspace_summary.json"
    csv_path = output_directory / "neutral_self_indexed_workspace_rows.csv"
    report_path = output_directory / "NEUTRAL_SELF_INDEXED_WORKSPACE_REPORT.md"
    analysis_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    compact = dict(result)
    for key in ("rows", "swap_rows", "ablation_rows", "feedback_rows"):
        compact.pop(key, None)
    summary_path.write_text(json.dumps(compact, indent=2, sort_keys=True) + "\n")
    rows = list(result["rows"])
    fields = sorted({key for row in rows for key in row})
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    modes = result["mode_summaries"]
    report = f"""# RRCT v0.46 Neutral Self-Indexed Workspace Report

## Status

`{result['status']}`

This controlled experiment implements a J-space-like sparse workspace in a synthetic residual-stream model and binds it to RRCT lineage, provenance, planning, and feedback. It does **not** inspect Claude and does not test phenomenal consciousness.

## Cohort

- Seeds: {', '.join(map(str, result['seeds']))}
- Unique world cases: {result['unique_world_case_count']}
- Matched decisions: {result['decision_count']}
- Frozen-style endpoints in this run: {sum(bool(value) for value in result['endpoints'].values())} / {len(result['endpoints'])}

## Workspace properties

| Measure | Value |
|---|---:|
| Calibration report R² | {result['discovery_summary']['mean_report_r2']:.6f} |
| Activation variance in workspace | {result['discovery_summary']['mean_workspace_variance_fraction']:.6f} |
| Hidden-projector overlap | {result['discovery_summary']['mean_projector_overlap']:.6f} |
| Jacobian report accuracy | {result['discovery_summary']['mean_jacobian_report_accuracy']:.6f} |
| PCA-subspace report accuracy | {result['discovery_summary']['mean_pca_report_accuracy']:.6f} |
| Random-subspace report accuracy | {result['discovery_summary']['mean_random_report_accuracy']:.6f} |
| Report swap success | {result['swap_summary']['report_swap_success_rate']:.6f} |
| Flexible broadcast swap success | {result['swap_summary']['flexible_broadcast_swap_success_rate']:.6f} |
| Reasoning swap success | {result['swap_summary']['reasoning_swap_success_rate']:.6f} |
| Routine route preserved under swap | {result['swap_summary']['automatic_route_preservation_rate']:.6f} |
| Routine accuracy after workspace ablation | {result['ablation_summary']['ablated_routine_accuracy']:.6f} |
| Flexible accuracy after workspace ablation | {result['ablation_summary']['ablated_flexible_accuracy']:.6f} |

## Matched architectures

| Mode | Task accuracy | Flexible accuracy | Memory-action accuracy | False autobiographical writes | Feedback reopening | Closure score |
|---|---:|---:|---:|---:|---:|---:|
"""
    for mode in result["modes"]:
        values = modes[mode]
        report += (
            f"| {mode} | {values['task_accuracy']:.6f} | "
            f"{values['flexible_task_accuracy']:.6f} | "
            f"{values['memory_action_accuracy']:.6f} | "
            f"{values['false_autobiographical_write_rate']:.6f} | "
            f"{values['feedback_reopen_rate']:.6f} | "
            f"{values['functional_closure_score']:.6f} |\n"
        )
    report += f"""

## Interpretation

{result['scientific_interpretation']}

The main dissociation is that workspace-only systems can retain flexible task use while failing autobiographical ownership, and self-model-only systems can retain lineage information while lacking flexible global access. The unbound combination does not repair this: access and self-modeling must be linked. Planner binding and recurrence are then separately necessary for action control and consequence-driven reallocation of evidence.

## Boundary

{result['claim_boundary']}
"""
    report_path.write_text(report, encoding="utf-8")
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (analysis_path, summary_path, csv_path, report_path)
    }
    (output_directory / "SHA256SUMS.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return hashes


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default=",".join(map(str, V046_EXPOSED_SEEDS)))
    parser.add_argument("--trials", type=int, default=12)
    parser.add_argument("--cohort", default="development")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    seeds = tuple(int(value.strip()) for value in args.seeds.split(",") if value.strip())
    result = run_neutral_workspace_benchmark(
        seeds,
        trials_per_scenario=args.trials,
        cohort=args.cohort,
    )
    write_neutral_workspace_results(result, args.output)
    print(
        json.dumps(
            {
                "status": result["status"],
                "all_endpoints_met": result["all_endpoints_met"],
                "mode_summaries": result["mode_summaries"],
                "output": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
