from __future__ import annotations

import json
import pathlib
import tomllib
from collections.abc import Mapping, Sequence
from typing import Any

from .exceptions import ConfigError, SafetyBoundaryError
from .utils import deep_merge, get_dotted, parse_cli_value, set_dotted


DEFAULT_CONFIG: dict[str, Any] = {
    "run": {
        "name": "rrct_run",
        "seed": 590001,
        "repetitions": 1,
        "deterministic": True,
        "output_root": "runs",
        "overwrite": False,
        "save_rows": True,
        "save_models": False,
        "make_plots": True,
        "fail_on_warning": False,
        "strict_feature_contract": True,
        "fail_on_unused_setting": True,
        "resume": False,
        "atomic_results": True,
        "checkpoint_keep": 3,
        "checkpoint_on_completion": True,
        "tags": [],
    },
    "runtime": {
        "backend": "auto",
        "device": "auto",
        "dtype": "float32",
        "threads": 0,
        "cuda_deterministic": True,
        "compile_model": False,
        "amp": False,
        "memory_limit_mb": 0,
        "timeout_seconds": 0,
        "process_isolation": False,
        "poll_interval_seconds": 0.25,
    },
    "experiment": {
        "family": "single_agent_closure",
        "task_family": "mixed",
        "episodes": 512,
        "calibration_episodes": 256,
        "holdout_episodes": 512,
        "sequence_length": 6,
        "agent_count": 4,
        "state_dim": 16,
        "observation_dim": 12,
        "action_dim": 4,
        "noise_std": 0.05,
        "transform_probability": 0.35,
        "surprise_probability": 0.20,
        "foreign_memory_probability": 0.20,
        "ambiguous_probability": 0.10,
        "task_difficulty": 1.0,
        "event_horizon": 256,
        "world_shift_probability": 0.12,
        "self_shift_probability": 0.12,
        "memory_corruption_probability": 0.10,
        "partner_change_probability": 0.08,
        "no_workspace_probability": 0.25,
    },
    "features": {
        "workspace": True,
        "self_model": True,
        "causal_boundary": True,
        "temporal_identity": True,
        "transformational_continuity": True,
        "autobiographical_memory": True,
        "provenance": True,
        "planner_binding": True,
        "recurrence": True,
        "metacognition": True,
        "uncertainty": True,
        "adaptive_probing": True,
        "abstention": True,
        "communication": True,
        "distributed_workspace": False,
        "pair_memory": False,
        "coordinate_alignment": True,
        "sparse_workspace": False,
        "fuzzy_packets": False,
        "hard_packets": False,
        "dynamic_formation": False,
        "cost_regularization": False,
        "hierarchical_workspace": False,
        "top_down_broadcast": True,
        "counterfactual_rollout": True,
        "receipt_chain": True,
        "causal_patching": True,
        "emergence_training": False,
        "curriculum": False,
        "terminal_only": True,
        "continuous_event_fabric": False,
        "open_set_change_detection": False,
        "dynamic_packet_birth": False,
        "dynamic_packet_death": False,
        "self_model_repair": False,
        "memory_quarantine": True,
        "jacobian_workspace": False,
        "moving_j_lens": False,
        "sparse_cone": False,
    },
    "workspace": {
        "mode": "global",
        "dimension": 8,
        "local_dimension": 4,
        "global_dimension": 4,
        "packet_count": 4,
        "shared_packet_count": 3,
        "capacity": 4,
        "top_k": 4,
        "hierarchy_depth": 1,
        "persistent_across_steps": True,
        "persistent_across_episodes": False,
        "bidirectional": True,
        "read_only": False,
        "message_dimension": 8,
        "message_rounds": 3,
        "alignment_rank": 4,
        "alignment_method": "cca",
        "transport_method": "procrustes",
        "membership_mode": "softmax",
        "temperature": 1.0,
        "entropy_penalty": 0.0,
        "idempotence_penalty": 0.0,
        "sparsity_penalty": 0.0,
        "edge_penalty": 0.0,
        "switching_cost": 0.0,
        "depth_cost": 0.0,
        "formation_cost": 0.12,
        "dissolve_after_episode": True,
        "allow_overlap": True,
        "allow_new_packets": False,
        "allow_packet_death": True,
        "max_packets": 8,
        "min_packet_lifetime": 4,
        "birth_threshold": 0.25,
        "death_threshold": 0.15,
        "split_threshold": 0.55,
        "merge_threshold": 0.90,
        "membership_hysteresis": 0.10,
        "learn_dimension": False,
    },
    "memory": {
        "working": True,
        "episodic": True,
        "semantic": False,
        "procedural": True,
        "capacity": 256,
        "retrieval_top_k": 8,
        "compression": "packetwise",
        "compression_rank": 8,
        "protected_self_rank": 2,
        "write_threshold": 0.70,
        "quarantine_threshold": 0.40,
        "feedback_decay": 0.90,
    },
    "metacognition": {
        "evidence_budget": 1,
        "max_evidence_budget": 4,
        "uncertainty_threshold": 0.35,
        "abstention_threshold": 0.55,
        "information_gain_weight": 1.0,
        "probe_cost": 0.05,
        "calibration_bins": 10,
    },
    "planner": {
        "horizon": 4,
        "candidate_actions": 4,
        "discount": 0.95,
        "risk_weight": 0.0,
        "uncertainty_weight": 0.20,
        "commit_before_outcome": True,
        "authorization_required": True,
    },
    "interaction": {
        "communication_bandwidth": 8,
        "asynchronous": False,
        "delay_steps": 0,
        "dropout_probability": 0.0,
        "message_noise_std": 0.0,
        "partner_swap_probability": 0.0,
        "coalition_count": 2,
        "overlap_probability": 0.25,
        "dynamic_membership": False,
        "private_state_dimension": 4,
    },
    "continuous": {
        "steps": 256,
        "calibration_steps": 16,
        "event_interval": 12,
        "event_duration": 1,
        "event_types": [
            "none",
            "world_shift",
            "self_shift",
            "memory_corruption",
            "partner_change",
        ],
        "change_threshold": 0.18,
        "anomaly_threshold": 0.35,
        "attribution_margin": 0.10,
        "recovery_threshold": 0.08,
        "repair_rate": 0.75,
        "repair_learning_rate": 0.40,
        "packet_update_rate": 0.35,
        "packet_sharpen_rate": 0.15,
        "packet_decay_rate": 0.10,
        "packet_birth_patience": 2,
        "packet_death_patience": 3,
        "probe_samples": 3,
        "probe_rounds": 2,
        "probe_noise_std": 0.015,
        "passive_noise_std": 0.02,
        "task_switch_interval": 7,
        "memory_injection_interval": 19,
        "memory_decay": 0.995,
        "max_memory_records": 512,
        "checkpoint_state_rows": 128,
        "checkpoint_interval": 32,
        "save_every_event": False,
        "invocation_step_limit": 0,
    },
    "jspace": {
        "residual_dimension": 32,
        "frame_rank": 4,
        "active_directions": 2,
        "steps": 96,
        "calibration_steps": 24,
        "event_interval": 12,
        "moving_rate": 0.20,
        "gate_learning_rate": 0.08,
        "readout_learning_rate": 0.05,
        "ridge": 0.001,
        "spectral_ratio": 0.0001,
        "ignition_threshold": 0.12,
        "access_hysteresis": 0.04,
        "random_baselines": 8,
        "checkpoint_interval": 16,
        "invocation_step_limit": 0,
    },
    "training": {
        "enabled": False,
        "steps": 1000,
        "batch_size": 256,
        "learning_rate": 0.003,
        "weight_decay": 1e-5,
        "optimizer": "adamw",
        "hidden_width": 32,
        "layers": 2,
        "heads": 4,
        "dropout": 0.0,
        "gradient_clip": 1.0,
        "checkpoint_interval": 100,
        "checkpoint_keep": 3,
        "early_stop_patience": 0,
        "curriculum_weight": 1.0,
        "terminal_loss_weight": 1.0,
        "intermediate_loss_weight": 0.0,
        "train_fraction": 0.80,
    },
    "interventions": {
        "workspace_cut": False,
        "self_model_cut": False,
        "causal_boundary_cut": False,
        "memory_cut": False,
        "provenance_cut": False,
        "planner_binding_cut": False,
        "recurrence_cut": False,
        "metacognition_cut": False,
        "feedback_cut": False,
        "one_way": False,
        "read_only_workspace": False,
        "reset_each_step": False,
        "reset_each_round": False,
        "message_shuffle": False,
        "wrong_source_substitution": False,
        "top_down_cut": False,
        "local_a_cut": False,
        "local_b_cut": False,
        "global_cut": False,
        "hardening": False,
        "random_membership": False,
        "patch_workspace": False,
        "patch_fraction": 0.25,
        "ablation_fraction": 1.0,
        "change_detector_cut": False,
        "packet_birth_cut": False,
        "packet_death_cut": False,
        "self_world_attribution_cut": False,
        "probe_cut": False,
        "repair_cut": False,
        "membership_shuffle": False,
        "jspace_cut": False,
        "broadcast_cut": False,
    },
    "evaluation": {
        "task_accuracy": True,
        "regret": True,
        "workspace_decodability": True,
        "alignment": True,
        "private_leakage": True,
        "causal_patch_effect": True,
        "ablation_drop": True,
        "provenance_accuracy": True,
        "false_memory_write_rate": True,
        "recurrence_reopen_rate": True,
        "continuity_accuracy": True,
        "membership_entropy": True,
        "idempotence_defect": True,
        "transport_defect": True,
        "synergy_information": True,
        "parameter_count": True,
        "wall_time": True,
        "peak_memory": True,
        "confidence_intervals": False,
        "bootstrap_samples": 500,
        "save_predictions": False,
        "change_detection_accuracy": True,
        "self_world_attribution_accuracy": True,
        "packet_birth_accuracy": True,
        "packet_death_accuracy": True,
        "repair_accuracy": True,
    },
    "sweep": {
        "enabled": False,
        "execute": True,
        "max_runs": 0,
        "parallel_workers": 1,
        "resume": True,
        "retry_failures": 0,
        "fail_fast": False,
        "state_file": "sweep_state.json",
        "gpu_workers": 1,
        "grid": {},
    },
    "safety": {
        "mode": "offline_research_sandbox",
        "network_access": False,
        "external_tools": False,
        "autonomous_persistence": False,
        "self_preservation_reward": False,
        "valence_model": False,
        "negative_welfare_state": False,
        "unrestricted_file_write": False,
        "allowed_output_root": "runs",
        "max_agents": 64,
        "max_hierarchy_depth": 8,
        "max_sequence_length": 10000,
        "max_training_steps": 10000000,
    },
}


HARD_BLOCKED_SAFETY_KEYS = (
    "safety.network_access",
    "safety.external_tools",
    "safety.autonomous_persistence",
    "safety.self_preservation_reward",
    "safety.valence_model",
    "safety.negative_welfare_state",
    "safety.unrestricted_file_write",
)


EXPERIMENT_FAMILIES = {
    "single_agent_closure",
    "transformational_identity",
    "distributed_workspace",
    "synergistic_channel",
    "nested_workspace",
    "formation_routing",
    "fuzzy_coalitions",
    "continuous_open_set_runtime",
    "persistent_fuzzy_j_workspace",
    "smoke_matrix",
}


def load_mapping(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigError(f"configuration file not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".toml":
        with path.open("rb") as handle:
            value = tomllib.load(handle)
    elif suffix == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise ConfigError("configuration must be TOML or JSON")
    if not isinstance(value, dict):
        raise ConfigError("top-level configuration must be a table/object")
    return value


def load_config(
    path: pathlib.Path | None,
    overrides: Sequence[str] = (),
) -> dict[str, Any]:
    config = deep_merge({}, DEFAULT_CONFIG)
    if path is not None:
        config = deep_merge(config, load_mapping(path))
    for override in overrides:
        if "=" not in override:
            raise ConfigError(f"override must use key=value syntax: {override}")
        key, raw = override.split("=", 1)
        set_dotted(config, key.strip(), parse_cli_value(raw))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    family = str(get_dotted(config, "experiment.family", ""))
    if family not in EXPERIMENT_FAMILIES:
        raise ConfigError(
            f"unknown experiment family {family!r}; choose from {sorted(EXPERIMENT_FAMILIES)}"
        )
    for key in HARD_BLOCKED_SAFETY_KEYS:
        if bool(get_dotted(config, key, False)):
            raise SafetyBoundaryError(
                f"{key}=true is blocked in this offline research build"
            )
    agents = int(get_dotted(config, "experiment.agent_count", 1))
    if not 1 <= agents <= int(get_dotted(config, "safety.max_agents", 64)):
        raise ConfigError("experiment.agent_count exceeds the configured safety bound")
    depth = int(get_dotted(config, "workspace.hierarchy_depth", 1))
    if not 0 <= depth <= int(get_dotted(config, "safety.max_hierarchy_depth", 8)):
        raise ConfigError("workspace.hierarchy_depth exceeds the configured safety bound")
    length = int(get_dotted(config, "experiment.sequence_length", 1))
    if not 1 <= length <= int(get_dotted(config, "safety.max_sequence_length", 10000)):
        raise ConfigError("experiment.sequence_length exceeds the configured safety bound")
    steps = int(get_dotted(config, "training.steps", 0))
    if not 0 <= steps <= int(get_dotted(config, "safety.max_training_steps", 10000000)):
        raise ConfigError("training.steps exceeds the configured safety bound")
    if int(get_dotted(config, "workspace.dimension", 1)) < 1:
        raise ConfigError("workspace.dimension must be positive")
    packets = int(get_dotted(config, "workspace.packet_count", 1))
    max_packets = int(get_dotted(config, "workspace.max_packets", packets))
    if packets < 1 or max_packets < packets:
        raise ConfigError("workspace packet counts are inconsistent")
    if int(get_dotted(config, "run.repetitions", 1)) < 1:
        raise ConfigError("run.repetitions must be at least one")
    if not bool(get_dotted(config, "run.atomic_results", True)):
        raise ConfigError("run.atomic_results=false is not allowed in the reliable build")
    if float(get_dotted(config, "workspace.temperature", 1.0)) <= 0:
        raise ConfigError("workspace.temperature must be positive")
    if not 0 <= float(get_dotted(config, "training.train_fraction", 0.8)) < 1:
        raise ConfigError("training.train_fraction must be in [0, 1)")
    if int(get_dotted(config, "sweep.parallel_workers", 1)) < 1:
        raise ConfigError("sweep.parallel_workers must be positive")
    if int(get_dotted(config, "continuous.steps", 1)) < 1:
        raise ConfigError("continuous.steps must be positive")
    if int(get_dotted(config, "continuous.calibration_steps", 0)) < 0:
        raise ConfigError("continuous.calibration_steps must be nonnegative")
    if int(get_dotted(config, "continuous.checkpoint_interval", 0)) < 0:
        raise ConfigError("continuous.checkpoint_interval must be nonnegative")
    if int(get_dotted(config, "continuous.invocation_step_limit", 0)) < 0:
        raise ConfigError("continuous.invocation_step_limit must be nonnegative")
    residual_dimension = int(get_dotted(config, "jspace.residual_dimension", 1))
    frame_rank = int(get_dotted(config, "jspace.frame_rank", 1))
    active_directions = int(get_dotted(config, "jspace.active_directions", 1))
    jspace_steps = int(get_dotted(config, "jspace.steps", 1))
    calibration_steps = int(get_dotted(config, "jspace.calibration_steps", 0))
    if residual_dimension < 4:
        raise ConfigError("jspace.residual_dimension must be at least four")
    # The synthetic bridge exposes four independent terminal readout heads.  A
    # higher requested Jacobian rank would be silently truncated by that
    # four-row Jacobian, so reject it rather than pretending the setting is
    # effective.  The optional transformer adapter is a separate probe path.
    maximum_synthetic_rank = min(residual_dimension, 4)
    if not 1 <= frame_rank <= maximum_synthetic_rank:
        raise ConfigError(
            "jspace.frame_rank must be between one and "
            f"{maximum_synthetic_rank} for the four-head synthetic bridge"
        )
    if not 1 <= active_directions <= frame_rank:
        raise ConfigError("jspace.active_directions must be between one and the frame rank")
    if jspace_steps < 1:
        raise ConfigError("jspace.steps must be positive")
    if not 0 <= calibration_steps < jspace_steps:
        raise ConfigError("jspace.calibration_steps must be nonnegative and less than jspace.steps")
    if int(get_dotted(config, "jspace.event_interval", 0)) < 1:
        raise ConfigError("jspace.event_interval must be positive")
    if float(get_dotted(config, "jspace.ridge", 0.0)) <= 0.0:
        raise ConfigError("jspace.ridge must be positive")
    if not 0.0 < float(get_dotted(config, "jspace.spectral_ratio", 0.0)) < 1.0:
        raise ConfigError("jspace.spectral_ratio must be in (0, 1)")
    if int(get_dotted(config, "jspace.random_baselines", 0)) < 1:
        raise ConfigError("jspace.random_baselines must be positive")
    if int(get_dotted(config, "jspace.checkpoint_interval", 0)) < 0:
        raise ConfigError("jspace.checkpoint_interval must be nonnegative")
    if int(get_dotted(config, "jspace.invocation_step_limit", 0)) < 0:
        raise ConfigError("jspace.invocation_step_limit must be nonnegative")
    if int(get_dotted(config, "run.checkpoint_keep", 0)) < 0:
        raise ConfigError("run.checkpoint_keep must be nonnegative")
    for key in (
        "workspace.birth_threshold",
        "workspace.death_threshold",
        "workspace.membership_hysteresis",
        "continuous.change_threshold",
        "continuous.attribution_margin",
        "continuous.recovery_threshold",
        "continuous.repair_rate",
        "jspace.moving_rate",
        "jspace.gate_learning_rate",
        "jspace.readout_learning_rate",
        "jspace.ignition_threshold",
        "jspace.access_hysteresis",
    ):
        value = float(get_dotted(config, key, 0.0))
        if not 0.0 <= value <= 1.0:
            raise ConfigError(f"{key} must be in [0, 1]")


def config_without_runtime_paths(config: Mapping[str, Any]) -> dict[str, Any]:
    clone = deep_merge({}, config)
    clone.get("run", {}).pop("output_root", None)
    clone.get("safety", {}).pop("allowed_output_root", None)
    return clone
