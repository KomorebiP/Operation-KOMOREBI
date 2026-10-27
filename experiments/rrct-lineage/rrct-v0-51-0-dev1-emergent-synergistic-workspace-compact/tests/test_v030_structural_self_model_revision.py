from dataclasses import asdict

import pytest

import rrct.structural_self_model_revision_experiment as experiment


def test_frozen_schedule_separates_fit_and_structural_confirmation_clocks():
    config = experiment.V030_FROZEN_CONFIG
    assert config.evidence_capacity == 240
    assert config.minimum_samples == 240
    assert config.fit_interval == 20
    assert config.structural_confirmation_interval == 120
    assert config.structural_grace_steps == 480
    assert config.maximum_revocation_latency_steps == 480
    assert config.contraction_steps == 580
    assert config.restoration_steps == 580
    assert config.transient_steps == 80
    assert config.boundary_config().structural_confirmation_interval == 120


def test_learner_rng_is_not_derived_from_the_world_seed():
    config = experiment.V030_FROZEN_CONFIG
    assert config.learner_seed == 330030
    assert config.boundary_config().seed == config.learner_seed
    assert all(
        config.boundary_config().seed != seed + 300_000
        for seed in experiment.V030_PILOT_SEEDS + experiment.V030_OFFICIAL_SEEDS
    )


def test_reserved_official_seed_fails_before_hidden_world_construction(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("hidden official metadata was instantiated")

    monkeypatch.setattr(experiment, "_hidden_structure", forbidden)
    with pytest.raises(PermissionError, match="frozen harness"):
        experiment.run_structural_self_model_revision_seed(
            experiment.V030_OFFICIAL_SEEDS[0],
            cohort="official",
        )


def test_official_authority_cannot_be_used_for_pilot_runs():
    with pytest.raises(ValueError, match="invalid for a pilot"):
        experiment.run_structural_self_model_revision_seed(
            experiment.V030_PILOT_SEEDS[0],
            cohort="pilot",
            allow_reserved_official=True,
        )


def test_matching_fit_streak_ignores_nonfit_rows_but_resets_on_other_fits():
    rows = [
        {"fit_performed": True, "fit_handle": 1, "fit_source": 2, "fit_rank": 1},
        {"fit_performed": False, "fit_handle": None, "fit_source": None, "fit_rank": 0},
        {"fit_performed": True, "fit_handle": 1, "fit_source": 2, "fit_rank": 1},
        {"fit_performed": True, "fit_handle": 1, "fit_source": 2, "fit_rank": 2},
        {"fit_performed": True, "fit_handle": 1, "fit_source": 2, "fit_rank": 1},
    ]
    assert experiment._maximum_matching_fit_streak(
        rows, handle=1, source=2, rank=1
    ) == 2


def _passing_part(seed):
    summary = {
        "seed": seed,
        "acquisition_terminal_exact": True,
        "acquisition_rank": 2,
        "stable_exact_accuracy": 1.0,
        "stable_rank_revisions": 0,
        "stable_terminal_exact": True,
        "transient_exact_accuracy": 1.0,
        "transient_rank_revisions": 0,
        "transient_terminal_exact": True,
        "transient_rank_one_proposals": 2,
        "transient_rank_one_candidate_starts_or_renewals": 1,
        "transient_rank_one_max_fit_streak": 3,
        "transient_legacy_false_rank_rate": 0.20,
        "transient_overlap_false_rank_rate": 0.20,
        "transient_overlap_rank_revisions": 2,
        "contraction_terminal_tail_accuracy": 1.0,
        "restoration_terminal_tail_accuracy": 1.0,
        "contraction_revision_latency": 300,
        "restoration_revision_latency": 420,
        "contraction_rank_revisions": 1,
        "restoration_rank_revisions": 1,
        "contraction_pair_retained": True,
        "restoration_pair_retained": True,
        "candidate_support_decays": True,
        "active_support_positive": True,
        "active_fit_support_positive": True,
        "prequential_chain_all": True,
        "equal_energy_all": True,
        "hidden_truth_isolated": True,
        "sustained_terminal_exact": True,
        "integrity": True,
    }
    receipt = {
        "seed": seed,
        "cohort": "pilot",
        "confidence_is_calibrated_probability": False,
        "hidden_pair_never_passed_to_model": True,
        "hidden_rank_never_passed_to_model": True,
        "hidden_projectors_never_passed_to_model": True,
        "phase_labels_never_passed_to_model": True,
        "world_seed_never_passed_to_model": True,
        "learner_rng_independent_of_world_seed": True,
    }
    return {
        "schema": experiment.V030_SCHEMA,
        "seed": seed,
        "cohort": "pilot",
        "config": asdict(experiment.V030_FROZEN_CONFIG),
        "seed_summary": summary,
        "rows": [{"seed": seed, "phase": "synthetic_aggregator_test"}],
        "receipt": receipt,
    }


def test_aggregate_requires_and_scores_the_exact_pilot_cohort(tmp_path):
    parts = [_passing_part(seed) for seed in experiment.V030_PILOT_SEEDS]
    output = tmp_path / "aggregate"
    result = experiment.aggregate_structural_self_model_revision_results(
        parts, output
    )

    assert result["all_primary_gates_pass"]
    assert result["transient_challenge"]["potent_seeds"] == 4
    assert result["transient_challenge"]["overlap_failure_seeds"] == 4
    assert (output / "v030_structural_revision_summary.json").is_file()
    assert (output / "v030_structural_revision_sha256.json").is_file()

    with pytest.raises(ValueError, match="exact reserved cohort"):
        experiment.aggregate_structural_self_model_revision_results(
            parts[:-1], tmp_path / "incomplete"
        )
