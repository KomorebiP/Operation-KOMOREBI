from dataclasses import asdict

import pytest

import rrct.conditional_rank_inference_experiment as experiment


def test_v031_candidate_schedule_and_information_boundary():
    config = experiment.V031_FROZEN_CANDIDATE_CONFIG
    assert config.evidence_capacity == 480
    assert config.minimum_samples == 480
    assert config.scenario_steps == 480
    assert config.block_size == 20
    assert config.learner_seed == 331031
    assert config.boundary_config(
        method="cross_fitted_reduced_rank_randomization_bootstrap"
    ).seed == 331031
    assert config.boundary_config(
        method="global_sharp_null"
    ).higher_mode_null == "global_sharp_null"
    assert all(config.learner_seed != seed for seed in (
        *experiment.V031_PILOT_SEEDS,
        *experiment.V031_OFFICIAL_SEEDS,
    ))


def test_reserved_official_seed_fails_before_hidden_world_construction(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("hidden official metadata was instantiated")

    monkeypatch.setattr(experiment, "_hidden_structure", forbidden)
    with pytest.raises(PermissionError, match="frozen harness"):
        experiment.run_conditional_rank_seed(
            experiment.V031_OFFICIAL_SEEDS[0], cohort="official"
        )


def _passing_part(seed):
    episodes = {}
    for name, _, target_rank in experiment.V031_SCENARIOS:
        integration = name == "rank_two_integration"
        episodes[name] = {
            "scenario": name,
            "scenario_steps": (
                experiment.V031_FROZEN_CANDIDATE_CONFIG.scenario_steps
                * experiment.V031_SCENARIO_WINDOWS[name]
            ),
            "target_rank": target_rank,
            "conditional_pair_exact": True,
            "conditional_rank": target_rank,
            "conditional_exact": True,
            "conditional_overrank": False,
            "conditional_confidence": 0.0 if target_rank == 0 else 0.5,
            "conditional_fit_steps": [479, 959] if integration else [479],
            "conditional_all_fits_exact": True,
            "conditional_acquisition_count": 1 if integration else 0,
            "conditional_state_transition_exact": True,
            "state_admission_expected": integration,
            "conditional_selected_pair_exact": True,
            "conditional_selected_rank": target_rank if integration else 0,
            "conditional_state_exact": True,
            "conditional_acquired": integration,
            "conditional_state_confidence": 0.5 if integration else 0.0,
            "global_pair_exact": True,
            "global_rank": target_rank,
            "global_exact": True,
            "global_overrank": False,
            "global_confidence": 0.0 if target_rank == 0 else 0.4,
            "global_fit_steps": [479, 959] if integration else [479],
            "global_all_fits_exact": True,
            "global_acquisition_count": 1 if integration else 0,
            "global_state_transition_exact": True,
            "global_selected_pair_exact": True,
            "global_selected_rank": target_rank if integration else 0,
            "global_state_exact": True,
            "global_acquired": integration,
            "global_state_confidence": 0.4 if integration else 0.0,
            "integrity": True,
        }
    return {
        "schema": experiment.V031_SCHEMA,
        "seed": seed,
        "cohort": "pilot",
        "config": asdict(experiment.V031_FROZEN_CANDIDATE_CONFIG),
        "seed_summary": {
            "seed": seed,
            "episodes": episodes,
            "conditional_false_overranks": 0,
            "conditional_positive_support": True,
            "integrity": True,
        },
        "rows": [
            {
                "schema": experiment.V031_SCHEMA,
                "seed": seed,
                "scenario": "synthetic_aggregate_test",
            }
        ],
        "receipt": {
            "rank_test_exact": False,
            "rank_test_method": (
                "cross_fitted_reduced_rank_randomization_bootstrap"
            ),
        },
    }


def test_v031_aggregate_requires_exact_cohort_and_preserves_claim_boundary(tmp_path):
    parts = [_passing_part(seed) for seed in experiment.V031_PILOT_SEEDS]
    result = experiment.aggregate_conditional_rank_results(
        parts, tmp_path / "aggregate"
    )
    assert result["all_primary_gates_pass"]
    assert len(result["primary_gates"]) == 10
    assert "not awareness or consciousness" in result["interpretation"]
    assert (
        tmp_path
        / "aggregate"
        / "v031_conditional_rank_integrity.json"
    ).is_file()
    with pytest.raises(ValueError, match="exact reserved cohort"):
        experiment.aggregate_conditional_rank_results(
            parts[:-1], tmp_path / "incomplete"
        )
    invalid = [dict(part) for part in parts]
    invalid[0]["cohort"] = "unknown"
    with pytest.raises(ValueError, match="pilot or official"):
        experiment.aggregate_conditional_rank_results(
            invalid, tmp_path / "invalid-cohort"
        )
