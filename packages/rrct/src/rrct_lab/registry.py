from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExperimentSpec:
    key: str
    title: str
    description: str
    module: str
    function: str = "run"
    optional_dependencies: tuple[str, ...] = ()
    supported_feature_keys: tuple[str, ...] = ()
    runtime_owned_keys: tuple[str, ...] = ()
    checkpoint_interval_key: str | None = None


COMMON = (
    "workspace",
    "planner_binding",
    "recurrence",
    "metacognition",
    "uncertainty",
    "causal_patching",
    "receipt_chain",
)


EXPERIMENTS: dict[str, ExperimentSpec] = {
    "single_agent_closure": ExperimentSpec(
        key="single_agent_closure",
        title="Single-agent functional closure",
        description="Self/world attribution, workspace access, provenance, planning, and feedback recurrence.",
        module="rrct_lab.experiments.single_agent",
        supported_feature_keys=COMMON
        + (
            "self_model",
            "causal_boundary",
            "temporal_identity",
            "transformational_continuity",
            "autobiographical_memory",
            "provenance",
            "adaptive_probing",
            "abstention",
        ),
    ),
    "transformational_identity": ExperimentSpec(
        key="transformational_identity",
        title="Transformational identity and continuity",
        description="Continuation, copy, fork, replacement, unresolved relation, and memory transfer.",
        module="rrct_lab.experiments.identity",
        supported_feature_keys=(
            "self_model",
            "temporal_identity",
            "transformational_continuity",
            "autobiographical_memory",
            "provenance",
            "planner_binding",
            "metacognition",
            "abstention",
        ),
    ),
    "distributed_workspace": ExperimentSpec(
        key="distributed_workspace",
        title="Distributed workspace dyad",
        description="Complementary agents, latent alignment, joint planning, private-state leakage, and pair recurrence.",
        module="rrct_lab.experiments.distributed",
        supported_feature_keys=COMMON
        + (
            "communication",
            "distributed_workspace",
            "pair_memory",
            "coordinate_alignment",
            "sparse_workspace",
            "fuzzy_packets",
        ),
    ),
    "synergistic_channel": ExperimentSpec(
        key="synergistic_channel",
        title="Synergistic recurrent communication channel",
        description="Alternating complementary operators with a persistent or learned message state.",
        module="rrct_lab.experiments.synergy",
        optional_dependencies=("torch",),
        supported_feature_keys=(
            "communication",
            "distributed_workspace",
            "planner_binding",
            "recurrence",
            "causal_patching",
            "emergence_training",
            "curriculum",
            "terminal_only",
        ),
    ),
    "nested_workspace": ExperimentSpec(
        key="nested_workspace",
        title="Learned two-level nested workspace",
        description="Four leaves, two local bottlenecks, one global bottleneck, top-down binding, and causal transplantation.",
        module="rrct_lab.experiments.nested",
        optional_dependencies=("torch",),
        supported_feature_keys=(
            "workspace",
            "hierarchical_workspace",
            "top_down_broadcast",
            "planner_binding",
            "causal_patching",
            "emergence_training",
            "terminal_only",
        ),
    ),
    "formation_routing": ExperimentSpec(
        key="formation_routing",
        title="Cost-regularized workspace formation",
        description="Task-conditioned choice among no workspace, flat, hierarchical, and overlapping routes.",
        module="rrct_lab.experiments.formation",
        supported_feature_keys=(
            "workspace",
            "dynamic_formation",
            "cost_regularization",
            "hierarchical_workspace",
            "distributed_workspace",
        ),
    ),
    "fuzzy_coalitions": ExperimentSpec(
        key="fuzzy_coalitions",
        title="Fuzzy Komorebi coalition formation",
        description="Fuzzy membership matrices, packet operators, idempotence defect, hardening, and causal membership calibration.",
        module="rrct_lab.experiments.fuzzy",
        optional_dependencies=("torch",),
        supported_feature_keys=(
            "workspace",
            "fuzzy_packets",
            "hard_packets",
            "dynamic_formation",
            "cost_regularization",
            "causal_patching",
        ),
    ),
    "continuous_open_set_runtime": ExperimentSpec(
        key="continuous_open_set_runtime",
        title="Continuous open-set self-model runtime",
        description=(
            "One persistent controller across unannounced self, world, sensor, memory, "
            "and task-structure changes with moving fuzzy packets, probing, repair, planning, "
            "provenance, and checkpointed recurrence."
        ),
        module="rrct_lab.experiments.continuous",
        runtime_owned_keys=(
            "runtime.memory_limit_mb",
            "runtime.timeout_seconds",
            "run.save_rows",
        ),
        checkpoint_interval_key="continuous.checkpoint_interval",
        supported_feature_keys=(
            "workspace",
            "self_model",
            "causal_boundary",
            "temporal_identity",
            "transformational_continuity",
            "autobiographical_memory",
            "provenance",
            "planner_binding",
            "recurrence",
            "metacognition",
            "uncertainty",
            "adaptive_probing",
            "abstention",
            "fuzzy_packets",
            "dynamic_formation",
            "cost_regularization",
            "receipt_chain",
            "continuous_event_fabric",
            "open_set_change_detection",
            "dynamic_packet_birth",
            "dynamic_packet_death",
            "self_model_repair",
            "memory_quarantine",
        ),
    ),
    "persistent_fuzzy_j_workspace": ExperimentSpec(
        key="persistent_fuzzy_j_workspace",
        title="Persistent fuzzy-to-J workspace bridge",
        description=(
            "Evaluator-blind fuzzy coalition formation feeding a moving Jacobian-discovered "
            "sparse workspace, measured causal broadcast, provenance-conditioned planning, "
            "and consequence-driven recurrence with matched PCA and random controls."
        ),
        module="rrct_lab.experiments.fuzzy_j",
        runtime_owned_keys=(
            "runtime.memory_limit_mb",
            "runtime.timeout_seconds",
            "run.save_rows",
        ),
        checkpoint_interval_key="jspace.checkpoint_interval",
        supported_feature_keys=(
            "workspace",
            "fuzzy_packets",
            "dynamic_formation",
            "cost_regularization",
            "jacobian_workspace",
            "moving_j_lens",
            "sparse_cone",
            "provenance",
            "planner_binding",
            "recurrence",
        ),
    ),
    "smoke_matrix": ExperimentSpec(
        key="smoke_matrix",
        title="All-family smoke matrix",
        description="Runs tiny configurations of every experiment family without performing scientific-scale training.",
        module="rrct_lab.experiments.smoke",
        supported_feature_keys=(),
    ),
}


def get_experiment(key: str) -> ExperimentSpec:
    try:
        return EXPERIMENTS[key]
    except KeyError as exc:
        raise KeyError(f"unknown experiment {key!r}") from exc


def list_experiments() -> list[dict[str, Any]]:
    return [
        {
            "key": spec.key,
            "title": spec.title,
            "description": spec.description,
            "optional_dependencies": list(spec.optional_dependencies),
            "supported_feature_keys": list(spec.supported_feature_keys),
            "runtime_owned_keys": list(spec.runtime_owned_keys),
            "checkpoint_interval_key": spec.checkpoint_interval_key,
        }
        for spec in EXPERIMENTS.values()
    ]
