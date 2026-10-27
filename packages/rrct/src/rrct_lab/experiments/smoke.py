from __future__ import annotations

import copy
from typing import Any

from rrct_lab.results import ExperimentResult


def run(config: dict[str, Any]) -> ExperimentResult:
    from rrct_lab.experiments import (
        continuous,
        distributed,
        formation,
        fuzzy,
        fuzzy_j,
        identity,
        nested,
        single_agent,
        synergy,
    )

    families = [
        ("single_agent_closure", single_agent.run),
        ("transformational_identity", identity.run),
        ("distributed_workspace", distributed.run),
        ("synergistic_channel", synergy.run),
        ("nested_workspace", nested.run),
        ("formation_routing", formation.run),
        ("fuzzy_coalitions", fuzzy.run),
        ("continuous_open_set_runtime", continuous.run),
        ("persistent_fuzzy_j_workspace", fuzzy_j.run),
    ]
    results: dict[str, Any] = {}
    warnings: list[str] = []
    passed = 0
    for index, (name, runner) in enumerate(families):
        local = copy.deepcopy(config)
        local["experiment"]["family"] = name
        local["experiment"]["episodes"] = 64
        local["experiment"]["calibration_episodes"] = 64
        local["experiment"]["holdout_episodes"] = 64
        local["run"]["save_rows"] = False
        local["run"]["make_plots"] = False
        local["run"]["seed"] = int(config["run"]["seed"]) + index
        local["training"]["enabled"] = name in {"nested_workspace", "fuzzy_coalitions"}
        local["run"]["strict_feature_contract"] = False
        local["run"]["fail_on_unused_setting"] = False
        local["training"]["steps"] = 2
        local["training"]["batch_size"] = 16
        local["features"]["distributed_workspace"] = name == "distributed_workspace"
        local["features"]["pair_memory"] = name == "distributed_workspace"
        local["features"]["hierarchical_workspace"] = name == "nested_workspace"
        if name == "nested_workspace":
            local["workspace"]["hierarchy_depth"] = 2
        local["features"]["cost_regularization"] = name in {
            "formation_routing",
            "persistent_fuzzy_j_workspace",
        }
        local["features"]["fuzzy_packets"] = name in {
            "fuzzy_coalitions",
            "continuous_open_set_runtime",
            "persistent_fuzzy_j_workspace",
        }
        local["features"]["continuous_event_fabric"] = name == "continuous_open_set_runtime"
        local["features"]["open_set_change_detection"] = name == "continuous_open_set_runtime"
        local["features"]["dynamic_packet_birth"] = name == "continuous_open_set_runtime"
        local["features"]["dynamic_packet_death"] = name == "continuous_open_set_runtime"
        local["features"]["self_model_repair"] = name == "continuous_open_set_runtime"
        local["features"]["dynamic_formation"] = name in {
            "formation_routing",
            "continuous_open_set_runtime",
            "persistent_fuzzy_j_workspace",
        }
        local["features"]["jacobian_workspace"] = name == "persistent_fuzzy_j_workspace"
        local["features"]["moving_j_lens"] = name == "persistent_fuzzy_j_workspace"
        local["features"]["sparse_cone"] = name == "persistent_fuzzy_j_workspace"
        local["workspace"]["allow_new_packets"] = name == "continuous_open_set_runtime"
        local["experiment"]["event_horizon"] = 64
        if name == "continuous_open_set_runtime":
            local["continuous"]["steps"] = 24
            local["continuous"]["calibration_steps"] = 3
            local["continuous"]["event_interval"] = 4
            local["training"]["checkpoint_interval"] = 6
        if name == "persistent_fuzzy_j_workspace":
            local["jspace"]["residual_dimension"] = 8
            local["jspace"]["frame_rank"] = 4
            local["jspace"]["active_directions"] = 2
            local["jspace"]["steps"] = 12
            local["jspace"]["calibration_steps"] = 3
            local["jspace"]["event_interval"] = 4
            local["jspace"]["random_baselines"] = 2
            local["jspace"]["checkpoint_interval"] = 4
        try:
            result = runner(local)
            finite = all(
                not isinstance(value, float) or value == value
                for value in result.metrics.values()
            )
            results[name] = {
                "status": result.status,
                "finite_metrics": finite,
                "metric_count": len(result.metrics),
            }
            if finite and result.status == "completed":
                passed += 1
        except Exception as exc:  # smoke matrix should report every family
            results[name] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            warnings.append(f"{name}: {type(exc).__name__}: {exc}")
    metrics = {
        "families_total": len(families),
        "families_passed": passed,
        "smoke_pass_rate": passed / len(families),
        "task_accuracy": passed / len(families),
    }
    return ExperimentResult(
        family="smoke_matrix",
        status="completed" if passed == len(families) else "partial",
        metrics=metrics,
        warnings=warnings,
        metadata={"family_results": results},
    )
