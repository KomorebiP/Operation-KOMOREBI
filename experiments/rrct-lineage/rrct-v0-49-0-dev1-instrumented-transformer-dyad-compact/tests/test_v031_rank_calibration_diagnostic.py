from copy import deepcopy
from dataclasses import asdict

import pytest

import rrct.conditional_rank_calibration_diagnostic as diagnostic
from rrct.conditional_rank_inference_experiment import (
    V031_FROZEN_CANDIDATE_CONFIG,
    V031_OFFICIAL_SEEDS,
)


def test_calibration_cohort_and_configuration_are_isolated_from_candidate():
    assert diagnostic.V031_CALIBRATION_SCHEMA.endswith(".v2")
    assert diagnostic.V031_CALIBRATION_SEEDS == tuple(range(891000, 891200))
    assert not set(diagnostic.V031_CALIBRATION_SEEDS) & set(V031_OFFICIAL_SEEDS)
    assert diagnostic.V031_CALIBRATION_CONFIG.null_permutations == 24
    assert diagnostic.V031_CALIBRATION_CONFIG.half_null_permutations == 24
    assert diagnostic.V031_CALIBRATION_CONFIG.null_quantile == 0.95
    assert V031_FROZEN_CANDIDATE_CONFIG.null_permutations == 128
    assert V031_FROZEN_CANDIDATE_CONFIG.half_null_permutations == 128
    assert V031_FROZEN_CANDIDATE_CONFIG.null_quantile == 0.99
    assert diagnostic.V031_CALIBRATION_CONFIG is not V031_FROZEN_CANDIDATE_CONFIG


def test_unreserved_calibration_seed_fails_before_world_generation(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("an unreserved diagnostic world was generated")

    monkeypatch.setattr(diagnostic, "_generate_rank_one_world", forbidden)
    with pytest.raises(ValueError, match="not in the v0.31 calibration cohort"):
        diagnostic.run_rank_calibration_world(889999)
    with pytest.raises(ValueError, match="integer"):
        diagnostic.run_rank_calibration_world(True)


def test_deterministic_receipt_preserves_rank_one_only_in_conditional_world():
    receipt = diagnostic.null_preservation_receipt()
    assert receipt["all_gates_pass"]
    assert receipt["physical_effect_rank"] == 1
    assert receipt["conditional_relative_reconstruction_error"] <= 1e-12
    assert receipt["legacy_relative_counterfactual_error"] == pytest.approx(
        2.0**0.5
    )


def _synthetic_record(seed, *, conditional_a, conditional_b, global_a, global_b):
    def fold(reject, *, global_null=False):
        value = {
            "observed": 2.0 if reject else 0.5,
            "threshold": 1.0,
            "p_value": 0.04 if reject else 0.52,
            "reject": bool(reject),
            "lower_modes_preserved_in_null": not global_null,
        }
        return value

    return {
        "schema": diagnostic.V031_CALIBRATION_SCHEMA,
        "seed": seed,
        "mode_two_config": asdict(diagnostic.V031_CALIBRATION_CONFIG),
        "online_learner_config": asdict(V031_FROZEN_CANDIDATE_CONFIG),
        "target_handle": 1,
        "target_source": 2,
        "target_rank": 1,
        "structure_digest": "1" * 64,
        "trajectory_digest": "2" * 64,
        "source_energy_error": 0.0,
        "prequential_chain": True,
        "conditioned_handle": 1,
        "conditioned_source": 2,
        "pair_conditioning": {
            "source": "evaluator_ground_truth_for_mode_two_diagnostic_only",
            "conditioned_pair_equals_target": True,
            "pair_passed_to_online_causal_self_boundary": False,
            "pair_discovery_claimed_by_diagnostic": False,
            "pair_discovery_assigned_to_candidate_assays": True,
        },
        "conditional_fold_a": fold(conditional_a),
        "conditional_fold_b": fold(conditional_b),
        "global_fold_a": fold(global_a, global_null=True),
        "global_fold_b": fold(global_b, global_null=True),
        "integrity": {
            "retained_rows": 480,
            "nonce_exact": True,
            "prequential_chain": True,
            "source_energy_error": 0.0,
            "equal_source_energy": True,
            "structure_digest": "1" * 64,
            "trajectory_digest": "2" * 64,
            "target_handle": 1,
            "target_source": 2,
            "target_rank": 1,
            "learner_seed": 331031,
            "learner_rng_independent_of_world_seed": True,
            "world_seed_passed_to_model": False,
            "hidden_pair_passed_to_model": False,
            "hidden_rank_passed_to_model": False,
            "conditioned_pair_passed_to_online_model": False,
            "observed_history_held_fixed": True,
        },
    }


def _passing_synthetic_records():
    records = []
    for index, seed in enumerate(diagnostic.V031_CALIBRATION_SEEDS):
        records.append(
            _synthetic_record(
                seed,
                conditional_a=index < 10,
                conditional_b=10 <= index < 20,
                global_a=index == 0,
                global_b=index == 1,
            )
        )
    return records


def test_calibration_gates_are_recomputed_from_all_200_world_records():
    records = _passing_synthetic_records()
    result = diagnostic.evaluate_rank_calibration_records(
        records,
        runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT,
    )
    assert result["all_primary_gates_pass"]
    assert result["retained_worlds"] == 200
    assert result["counts"] == {
        "conditional_fold_a_rejections": 10,
        "conditional_fold_b_rejections": 10,
        "conditional_pooled_rejections": 20,
        "global_fold_a_rejections": 1,
        "global_fold_b_rejections": 1,
        "global_pooled_rejections": 2,
    }

    assert result["primary_gates"][
        "pair_conditioning_is_evaluator_only_and_never_passed_online"
    ]


def test_calibration_aggregate_rejects_missing_reordered_or_wrong_runtime():
    records = _passing_synthetic_records()
    with pytest.raises(ValueError, match="exactly 200"):
        diagnostic.evaluate_rank_calibration_records(
            records[:-1], runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )
    reordered = records.copy()
    reordered[0], reordered[1] = reordered[1], reordered[0]
    with pytest.raises(ValueError, match="seed mismatch"):
        diagnostic.evaluate_rank_calibration_records(
            reordered, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )
    wrong_runtime = deepcopy(diagnostic.EXPECTED_RUNTIME_RECEIPT)
    wrong_runtime["numpy"] = "0.0.0"
    with pytest.raises(ValueError, match="runtime receipt mismatch"):
        diagnostic.evaluate_rank_calibration_records(
            records, runtime_receipt=wrong_runtime
        )


def test_calibration_validator_rejects_p_value_and_threshold_tampering():
    records = _passing_synthetic_records()
    off_lattice = deepcopy(records)
    off_lattice[7]["conditional_fold_a"]["p_value"] = 0.05
    with pytest.raises(ValueError, match="add-one lattice"):
        diagnostic.evaluate_rank_calibration_records(
            off_lattice, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )

    incoherent = deepcopy(records)
    incoherent[7]["conditional_fold_a"]["observed"] = 0.5
    incoherent[7]["conditional_fold_a"]["threshold"] = 1.0
    incoherent[7]["conditional_fold_a"]["p_value"] = 0.04
    incoherent[7]["conditional_fold_a"]["reject"] = True
    with pytest.raises(ValueError, match="rejection coherence"):
        diagnostic.evaluate_rank_calibration_records(
            incoherent, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )


def test_calibration_validator_rejects_digest_and_integrity_tampering():
    records = _passing_synthetic_records()
    bad_digest = deepcopy(records)
    bad_digest[11]["trajectory_digest"] = "A" * 64
    with pytest.raises(ValueError, match="SHA-256"):
        diagnostic.evaluate_rank_calibration_records(
            bad_digest, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )

    mismatched_integrity = deepcopy(records)
    mismatched_integrity[11]["integrity"]["prequential_chain"] = False
    with pytest.raises(ValueError, match="top-level/integrity"):
        diagnostic.evaluate_rank_calibration_records(
            mismatched_integrity,
            runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT,
        )

    leaked_pair = deepcopy(records)
    leaked_pair[11]["pair_conditioning"][
        "pair_passed_to_online_causal_self_boundary"
    ] = True
    with pytest.raises(ValueError, match="pair-conditioning receipt"):
        diagnostic.evaluate_rank_calibration_records(
            leaked_pair, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )

    truthy_string = deepcopy(records)
    truthy_string[11]["integrity"]["nonce_exact"] = "true"
    with pytest.raises(ValueError, match="exact boolean"):
        diagnostic.evaluate_rank_calibration_records(
            truthy_string, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )

    boolean_integer = deepcopy(records)
    boolean_integer[11]["integrity"]["retained_rows"] = True
    with pytest.raises(ValueError, match="exact integer"):
        diagnostic.evaluate_rank_calibration_records(
            boolean_integer, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )

    boolean_numeric = deepcopy(records)
    boolean_numeric[11]["conditional_fold_a"]["observed"] = True
    with pytest.raises(ValueError, match="exact number"):
        diagnostic.evaluate_rank_calibration_records(
            boolean_numeric, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )

    string_numeric = deepcopy(records)
    string_numeric[11]["source_energy_error"] = "0.0"
    with pytest.raises(ValueError, match="exact number"):
        diagnostic.evaluate_rank_calibration_records(
            string_numeric, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )

    extra_fold_key = deepcopy(records)
    extra_fold_key[11]["conditional_fold_a"]["unfrozen"] = True
    with pytest.raises(ValueError, match="key schema"):
        diagnostic.evaluate_rank_calibration_records(
            extra_fold_key, runtime_receipt=diagnostic.EXPECTED_RUNTIME_RECEIPT
        )
