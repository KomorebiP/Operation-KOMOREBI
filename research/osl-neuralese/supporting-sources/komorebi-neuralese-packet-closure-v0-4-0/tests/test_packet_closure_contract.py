from __future__ import annotations

import copy
from functools import lru_cache
import math
import sys
from pathlib import Path

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import run_packet_closure as runner
from komorebi_neuralese.packet_closure_eval import _word_digest


@lru_cache(maxsize=1)
def _registered_heldout_bank() -> object:
    return runner.freeze_heldout_bank(
        runner.make_v04_suffix_plan(max_depth=8),
        torch.from_numpy(runner.canonical_maps("d4")).to(dtype=torch.long),
        max_suffixes=None,
    )


def _registered_contract(source_digest: str = "a" * 64) -> dict[str, object]:
    return copy.deepcopy(runner.contract_requirements(source_digest))


def test_registered_contract_matches_every_frozen_requirement() -> None:
    source_digest = "a" * 64
    validation = runner.validate_contract(
        _registered_contract(source_digest),
        "pilot",
        runner.PROFILES["pilot"],
        source_digest,
    )
    assert validation["valid"]
    assert all(value is True for value in validation.values())


@pytest.mark.parametrize(
    "missing",
    [
        "schema",
        "version",
        "author",
        "status",
        "study_status",
        "implementation_source_digest",
        "profiles",
        "registered_design",
    ],
)
def test_registered_contract_fails_closed_on_missing_core_fields(missing: str) -> None:
    source_digest = "a" * 64
    contract = _registered_contract(source_digest)
    contract.pop(missing)
    assert not runner.validate_contract(
        contract,
        "pilot",
        runner.PROFILES["pilot"],
        source_digest,
    )["valid"]


def test_registered_contract_rejects_unregistered_top_level_field() -> None:
    source_digest = "a" * 64
    contract = _registered_contract(source_digest)
    contract["unregistered_field"] = True
    validation = runner.validate_contract(
        contract,
        "pilot",
        runner.PROFILES["pilot"],
        source_digest,
    )
    assert not validation["top_level_schema_valid"]
    assert not validation["valid"]


def test_contract_rejects_selected_profile_mutation() -> None:
    source_digest = "a" * 64
    contract = _registered_contract(source_digest)
    contract["profiles"]["pilot"]["training"]["steps"] += 1  # type: ignore[index,operator]
    validation = runner.validate_contract(
        contract,
        "pilot",
        runner.PROFILES["pilot"],
        source_digest,
    )
    assert not validation["valid"]
    assert not validation["profiles_valid"]
    assert not validation["profile_valid"]


def test_contract_rejects_unselected_profile_mutation() -> None:
    source_digest = "a" * 64
    contract = _registered_contract(source_digest)
    contract["profiles"]["screen"]["seeds"] = [72]  # type: ignore[index]
    validation = runner.validate_contract(
        contract,
        "pilot",
        runner.PROFILES["pilot"],
        source_digest,
    )
    assert not validation["valid"]
    assert not validation["profiles_valid"]
    assert validation["profile_valid"]


def test_contract_rejects_source_digest_mismatch() -> None:
    contract = _registered_contract("a" * 64)
    validation = runner.validate_contract(
        contract,
        "pilot",
        runner.PROFILES["pilot"],
        "b" * 64,
    )
    assert not validation["valid"]
    assert not validation["source_digest_valid"]


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("arm_names", ["euclidean_supervised", "polar_cr"]),
        ("primary_arm", "polar_supervised"),
    ],
)
def test_contract_rejects_arm_registry_or_primary_arm_mutation(
    field: str,
    replacement: object,
) -> None:
    source_digest = "a" * 64
    contract = _registered_contract(source_digest)
    contract["registered_design"][field] = replacement  # type: ignore[index]
    validation = runner.validate_contract(
        contract,
        "pilot",
        runner.PROFILES["pilot"],
        source_digest,
    )
    assert not validation["valid"]
    assert not validation["registered_design_valid"]


@pytest.mark.parametrize("criterion", sorted(runner.FROZEN_GATE_THRESHOLDS))
def test_contract_rejects_every_registered_criterion_mutation(criterion: str) -> None:
    source_digest = "a" * 64
    contract = _registered_contract(source_digest)
    thresholds = contract["registered_design"]["gate_thresholds"]  # type: ignore[index]
    value = thresholds[criterion]
    if isinstance(value, list):
        replacement: object = [*value, 999.0]
    elif isinstance(value, dict):
        replacement = {**value, "unexpected": 999.0}
    elif isinstance(value, int):
        replacement = value + 1
    else:
        replacement = float(value) + 0.123
    thresholds[criterion] = replacement
    validation = runner.validate_contract(
        contract,
        "pilot",
        runner.PROFILES["pilot"],
        source_digest,
    )
    assert not validation["valid"]
    assert not validation["registered_design_valid"]


def test_contract_source_digest_excludes_only_the_contract_itself(tmp_path: Path) -> None:
    (tmp_path / "study.py").write_text("VALUE = 1\n", encoding="utf-8")
    contract_path = tmp_path / runner.CONTRACT_FILENAME
    contract_path.write_text('{"revision": 1}\n', encoding="utf-8")
    first = runner.contract_source_digest(tmp_path)
    contract_path.write_text('{"revision": 2}\n', encoding="utf-8")
    assert runner.contract_source_digest(tmp_path) == first
    (tmp_path / "study.py").write_text("VALUE = 2\n", encoding="utf-8")
    assert runner.contract_source_digest(tmp_path) != first


def _switch_bank(profile: str) -> dict[str, object]:
    config = runner.PROFILES[profile]
    word_length = int(config["switched_word_length"])
    word_count = int(config["switched_word_count"])
    words = runner.sample_switch_words(
        num_actions=2,
        word_length=word_length,
        count=word_count,
        seed=runner.derive_seed(int(config["eval_seed_base"]), "switch_words"),
        include_constant_words=True,
    )
    return {
        "word_length": word_length,
        "word_count": word_count,
        "contexts": int(config["switched_contexts"]),
        "exhaustive": word_count == 2**word_length,
        "words": [list(word) for word in words],
    }


@pytest.mark.parametrize("profile", ["smoke", "screen", "pilot"])
def test_registered_switch_bank_is_accepted(profile: str) -> None:
    assert runner.validate_switch_bank(
        profile,
        runner.PROFILES[profile],
        _switch_bank(profile),
    )


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("word_length", 7),
        ("word_count", 255),
        ("contexts", 15),
        ("exhaustive", False),
    ],
)
def test_pilot_switch_bank_rejects_every_mutated_declaration(
    field: str,
    replacement: object,
) -> None:
    declaration = _switch_bank("pilot")
    declaration[field] = replacement
    assert not runner.validate_switch_bank(
        "pilot",
        runner.PROFILES["pilot"],
        declaration,
    )


@pytest.mark.parametrize(
    "missing",
    ["word_length", "word_count", "contexts", "exhaustive", "words"],
)
def test_switch_bank_fails_closed_on_missing_fields(missing: str) -> None:
    declaration = _switch_bank("smoke")
    declaration.pop(missing)
    assert not runner.validate_switch_bank(
        "smoke",
        runner.PROFILES["smoke"],
        declaration,
    )


def test_switch_bank_rejects_nonboolean_exhaustive_marker() -> None:
    declaration = _switch_bank("pilot")
    declaration["exhaustive"] = "true"
    assert not runner.validate_switch_bank(
        "pilot",
        runner.PROFILES["pilot"],
        declaration,
    )


def test_switch_bank_rejects_duplicate_word_even_when_count_is_unchanged() -> None:
    declaration = _switch_bank("pilot")
    words = declaration["words"]
    assert isinstance(words, list)
    words[-1] = copy.deepcopy(words[0])
    assert not runner.validate_switch_bank(
        "pilot",
        runner.PROFILES["pilot"],
        declaration,
    )


@pytest.mark.parametrize(
    ("profile", "mutation"),
    [
        ("pilot", "alphabet"),
        ("pilot", "length"),
        ("screen", "content"),
    ],
)
def test_switch_bank_rejects_mutated_word_content(
    profile: str,
    mutation: str,
) -> None:
    declaration = _switch_bank(profile)
    words = declaration["words"]
    assert isinstance(words, list)
    if mutation == "alphabet":
        words[0][0] = 2
    elif mutation == "length":
        words[0] = words[0][:-1]
    else:
        replacement = list(words[0])
        replacement[-1] = 1 - replacement[-1]
        words[0] = replacement
    assert not runner.validate_switch_bank(
        profile,
        runner.PROFILES[profile],
        declaration,
    )


def _ambient_row() -> dict[str, object]:
    return {
        "seed": 53,
        "arm": "polar_cr",
        "family": "d4",
        "anchor_rank": 8,
        "complement_rank": 4,
        "projector_idempotence_error": 0.0,
        "projector_metric_self_adjoint_error": 0.0,
        "applied_anchor_rank": 8,
        "applied_complement_rank": 4,
        "applied_rank_tolerance": runner.FROZEN_GATE_THRESHOLDS[
            "ambient_applied_rank_tolerance"
        ],
        "applied_anchor_projector_idempotence_error": 0.0,
        "applied_anchor_projector_metric_self_adjoint_error": 0.0,
        "applied_complement_projector_idempotence_error": 0.0,
        "applied_complement_projector_metric_self_adjoint_error": 0.0,
        "random_projector_rank": 4,
        "applied_random_projector_minimum_rank": 4,
        "applied_random_projector_maximum_rank": 4,
        "random_projector_idempotence_error": 0.0,
        "random_projector_metric_self_adjoint_error": 0.0,
        "energy_match_maximum_absolute_error": 0.0,
        "ideal_random_projector_idempotence_error": 0.0,
        "ideal_random_projector_metric_self_adjoint_error": 0.0,
        "ideal_energy_match_maximum_absolute_error": 0.0,
        "reported_energy_match_tolerance": runner.FROZEN_GATE_THRESHOLDS[
            "ambient_applied_geometry_tolerance"
        ],
        "status": "NO_MEANINGFUL_Q_PERFORMANCE_DROP",
    }


def _ambient_rows() -> list[dict[str, object]]:
    rows = []
    for family in ("d4", "c8", "mixed_cycle"):
        row = _ambient_row()
        row["family"] = family
        rows.append(row)
    return rows


def test_registered_ambient_control_geometry_is_accepted() -> None:
    assert runner.validate_ambient_control_rows(_ambient_rows(), expected_runs=1)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("anchor_rank", 7),
        ("complement_rank", 5),
        ("applied_anchor_rank", 7),
        ("applied_complement_rank", 5),
        ("random_projector_rank", 3),
        ("applied_random_projector_minimum_rank", 3),
        ("applied_random_projector_maximum_rank", 5),
        ("projector_idempotence_error", 1.1e-8),
        ("projector_metric_self_adjoint_error", 1.1e-8),
        ("ideal_random_projector_idempotence_error", 1.1e-8),
        ("ideal_random_projector_metric_self_adjoint_error", 1.1e-8),
        ("ideal_energy_match_maximum_absolute_error", 1.1e-8),
        ("applied_anchor_projector_idempotence_error", 1.1e-6),
        ("applied_anchor_projector_metric_self_adjoint_error", 1.1e-6),
        ("applied_complement_projector_idempotence_error", 1.1e-6),
        ("applied_complement_projector_metric_self_adjoint_error", 1.1e-6),
        ("random_projector_idempotence_error", 1.1e-6),
        ("random_projector_metric_self_adjoint_error", 1.1e-6),
        ("energy_match_maximum_absolute_error", 1.1e-6),
        ("projector_idempotence_error", -1e-9),
        ("projector_idempotence_error", math.inf),
        ("projector_metric_self_adjoint_error", math.nan),
        ("status", "RANDOM_CONTROL_ENERGY_MATCH_FAILED"),
    ],
)
def test_ambient_control_geometry_rejects_each_negative_mutation(
    field: str,
    replacement: object,
) -> None:
    rows = _ambient_rows()
    rows[0][field] = replacement
    assert not runner.validate_ambient_control_rows(rows, expected_runs=1)


@pytest.mark.parametrize(
    "missing",
    [
        "anchor_rank",
        "complement_rank",
        "random_projector_rank",
        "projector_idempotence_error",
        "projector_metric_self_adjoint_error",
        "random_projector_idempotence_error",
        "random_projector_metric_self_adjoint_error",
        "energy_match_maximum_absolute_error",
        "status",
    ],
)
def test_ambient_control_geometry_fails_closed_on_missing_fields(missing: str) -> None:
    rows = _ambient_rows()
    rows[0].pop(missing)
    assert not runner.validate_ambient_control_rows(rows, expected_runs=1)


def test_ambient_control_geometry_rejects_wrong_row_count() -> None:
    rows = _ambient_rows()
    assert not runner.validate_ambient_control_rows(rows[:-1], expected_runs=1)
    assert not runner.validate_ambient_control_rows(rows + [copy.deepcopy(rows[0])], expected_runs=1)


def _ambient_panel_rows(seeds: tuple[int, ...]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for seed in seeds:
        for arm in runner.ARM_NAMES:
            for family in ("d4", "c8", "mixed_cycle"):
                row = _ambient_row()
                row.update({"seed": seed, "arm": arm, "family": family})
                rows.append(row)
    return rows


def test_ambient_control_geometry_rejects_duplicate_or_unknown_family() -> None:
    duplicate = _ambient_panel_rows((53,))
    duplicate[2]["family"] = "d4"
    assert not runner.validate_ambient_control_rows(
        duplicate,
        expected_runs=len(runner.ARM_NAMES),
        expected_seeds=[53],
    )

    unknown = _ambient_panel_rows((53,))
    unknown[2]["family"] = "random"
    assert not runner.validate_ambient_control_rows(
        unknown,
        expected_runs=len(runner.ARM_NAMES),
        expected_seeds=[53],
    )


def test_ambient_control_geometry_requires_three_families_per_run() -> None:
    split_run = _ambient_panel_rows((53,))
    split_run[2]["seed"] = 71
    assert not runner.validate_ambient_control_rows(
        split_run,
        expected_runs=len(runner.ARM_NAMES),
        expected_seeds=[53],
    )

    two_seed_panel = _ambient_panel_rows((53, 71))
    assert runner.validate_ambient_control_rows(
        two_seed_panel,
        expected_runs=2 * len(runner.ARM_NAMES),
        expected_seeds=[53, 71],
    )


def _episode_contract(
    *, family: str, contexts: int, length: int
) -> dict[str, object]:
    return {
        "family": family,
        "intermediates_exact": True,
        "target_exact": True,
        "canonical_visible_slots_exact": True,
        "tables_exact_one_hot_maps": True,
        "tables_finite": True,
        "maps_are_permutations": True,
        "phi_is_permutation": True,
        "visible_slots_are_permutations": True,
        "canonical_family_realization_exact": True,
        "shapes_exact": True,
        "values_in_range": True,
        "contexts": contexts,
        "length": length,
    }


def _evaluation(config: dict[str, object], arm: str) -> dict[str, object]:
    heldout = _registered_heldout_bank()

    def constant_summary(count: int, value: float) -> dict[str, object]:
        return {
            "count": count,
            "finite_count": count,
            "minimum": value,
            "p10": value,
            "median": value,
            "mean": value,
            "p90": value,
            "maximum": value,
        }

    def unit_summary(count: int) -> dict[str, object]:
        return constant_summary(count, 1.0)

    def packet_row(examples: int) -> dict[str, object]:
        return {
            "bank": heldout.to_dict(),
            "examples": examples,
            "boundary_tolerance": 0.0,
            "strict_membership_fraction": 1.0,
            "word_weighted_membership_fraction": 1.0,
            "macro_relation_group_membership_fraction": 1.0,
            "suffix_accuracy": 1.0,
            "finite_margin_fraction": 1.0,
            "minimum_margin": unit_summary(examples),
            "suffix_minimum_margin": unit_summary(examples * len(heldout.words)),
            "relation_groups": [
                {
                    "membership_fraction": 1.0,
                    "word_weighted_membership_fraction": 1.0,
                    "minimum_margin": unit_summary(examples),
                    "signature": list(range(8)),
                    "suffix_count": 86,
                },
                {
                    "membership_fraction": 1.0,
                    "word_weighted_membership_fraction": 1.0,
                    "minimum_margin": unit_summary(examples),
                    "signature": [2, 3, 0, 1, 6, 7, 4, 5],
                    "suffix_count": 85,
                },
            ],
        }

    packet = {
        str(prefix): packet_row(int(config["packet_examples"]))
        for prefix in config["packet_prefixes"]  # type: ignore[union-attr]
    }
    deep = {
        str(depth): {
            "pooled_accuracy": 1.0,
            "macro_family_accuracy": 1.0,
            "minimum_family_accuracy": 1.0,
            "total_examples": 3 * int(config["eval_examples"]),
            "per_family": {
                family: {
                    "accuracy": 1.0,
                    "finite_fraction": 1.0,
                    "examples": int(config["eval_examples"]),
                    "depth": int(depth),
                }
                for family in ("d4", "c8", "mixed_cycle")
            },
        }
        for depth in config["deep_depths"]  # type: ignore[union-attr]
    }
    null_loop = {
        "bank": heldout.to_dict(),
        "baseline": packet_row(int(config["null_examples"])),
        "repeats": list(config["null_repeats"]),  # type: ignore[arg-type]
        "relations": {
            name: {
                "word": list(word),
                "by_repeat": {
                    str(repeat): {
                        "strict_membership_fraction": 1.0,
                        "conditional_retention_fraction": 1.0,
                        "conditional_word_retention_fraction": 1.0,
                        "current_label_accuracy": 1.0,
                        "finite_logit_fraction": 1.0,
                        "minimum_margin": unit_summary(
                            int(config["null_examples"])
                        ),
                        "positive_baseline_margin_ratio": unit_summary(
                            int(config["null_examples"])
                        ),
                        "macro_relation_group_membership_fraction": 1.0,
                    }
                    for repeat in config["null_repeats"]  # type: ignore[union-attr]
                },
                "first_sampled_crossing": {
                    "never_fraction_among_baseline_members": 1.0,
                    "observed": [],
                },
            }
            for name, word in runner.D4_RELATIONS.items()
        }
    }
    ambient = {
        family: {
            "geometry": {
                "steps": int(config["ambient_length"]),
                "midpoint": int(config["ambient_length"]) // 2,
                "anchor_rank": 8,
                "complement_rank": 4,
                "ambient_dimension": 12,
                "projector_idempotence_error": 0.0,
                "projector_metric_self_adjoint_error": 0.0,
                "applied_anchor_rank": 8,
                "applied_complement_rank": 4,
                "applied_rank_tolerance": runner.FROZEN_GATE_THRESHOLDS[
                    "ambient_applied_rank_tolerance"
                ],
                "applied_anchor_projector_idempotence_error": 0.0,
                "applied_anchor_projector_metric_self_adjoint_error": 0.0,
                "applied_complement_projector_idempotence_error": 0.0,
                "applied_complement_projector_metric_self_adjoint_error": 0.0,
            },
            "matched_random_control": {
                "rank": 4,
                "applied_minimum_effective_rank": 4,
                "applied_maximum_effective_rank": 4,
                "maximum_idempotence_error": 0.0,
                "maximum_metric_self_adjoint_error": 0.0,
                "q_energy_match_maximum_absolute_error": 0.0,
                "ideal_construction": {
                    "maximum_idempotence_error": 0.0,
                    "maximum_metric_self_adjoint_error": 0.0,
                    "q_energy_match_maximum_absolute_error": 0.0,
                },
            },
            "conditions": {
                "native": {
                    "accuracy": 1.0,
                    "finite_fraction": 1.0,
                    "defined_fraction": 1.0,
                    "state_valid_fraction": 1.0,
                    "agreement_with_native": 1.0,
                },
                "p_confined": {
                    "accuracy": 0.75,
                    "finite_fraction": 1.0,
                    "defined_fraction": 1.0,
                    "state_valid_fraction": 1.0,
                    "agreement_with_native": 0.75,
                },
                "midpoint_q_ablated": {
                    "accuracy": 0.75,
                    "finite_fraction": 1.0,
                    "defined_fraction": 1.0,
                    "state_valid_fraction": 1.0,
                    "agreement_with_native": 0.75,
                },
                "matched_random_rank_control": {
                    "accuracy": 0.9375,
                    "finite_fraction": 1.0,
                    "defined_fraction": 1.0,
                    "state_valid_fraction": 1.0,
                    "agreement_with_native": 0.9375,
                },
            },
            "performance_drops": {
                "p_confined": 0.25,
                "midpoint_q_ablation": 0.25,
                "matched_random_rank_control": 0.0625,
                "q_specific_excess_over_random": 0.1875,
            },
            "native_conditioned_transitions": {
                "native_correct_count": int(config["ambient_examples"]),
                "native_error_count": 0,
                "p_confined_break_fraction": 0.25,
                "p_confined_correction_fraction": None,
                "q_ablation_break_fraction": 0.25,
                "q_ablation_correction_fraction": None,
                "matched_random_break_fraction": 0.0625,
                "matched_random_correction_fraction": None,
            },
            "q_energy_fraction": {
                "initial": unit_summary(int(config["ambient_examples"])),
                "midpoint": unit_summary(int(config["ambient_examples"])),
                "final": unit_summary(int(config["ambient_examples"])),
                "all_native_states": unit_summary(
                    int(config["ambient_examples"])
                    * (int(config["ambient_length"]) + 1)
                ),
            },
            "attribution": {
                "status": "SUPPORTED_SPECIFIC_Q_PERFORMANCE_DROP",
                "supports_specific_ambient_attribution": True,
                "minimum_accuracy_drop": runner.FROZEN_GATE_THRESHOLDS[
                    "ambient_accuracy_drop_minimum"
                ],
                "specificity_margin": runner.FROZEN_GATE_THRESHOLDS[
                    "ambient_specificity_margin_minimum"
                ],
                "native_accuracy_floor": runner.FROZEN_GATE_THRESHOLDS[
                    "ambient_native_accuracy_minimum"
                ],
                "native_accuracy_eligible": True,
                "random_energy_match_tolerance": runner.FROZEN_GATE_THRESHOLDS[
                    "ambient_applied_geometry_tolerance"
                ],
            },
        }
        for family in ("d4", "c8", "mixed_cycle")
    }
    for family, row in ambient.items():
        row["matched_random_control"].update(
            {
                "seed": runner.derive_seed(
                    int(config["eval_seed_base"]),
                    "ambient_random_control",
                    family,
                ),
                "state_conditioned": True,
                "removed_energy_fraction": unit_summary(
                    int(config["ambient_examples"])
                ),
                "q_removed_energy_fraction": unit_summary(
                    int(config["ambient_examples"])
                ),
                "q_energy_match_mean_absolute_error": 0.0,
            }
        )
        row["matched_random_control"]["ideal_construction"].update(
            {
                "removed_energy_fraction": unit_summary(
                    int(config["ambient_examples"])
                ),
                "q_energy_match_mean_absolute_error": 0.0,
            }
        )
    causal = {
        "available": True,
        "examples": int(config["intervention_examples"]),
        "length": int(config["intervention_length"]),
        "state_split": int(config["intervention_state_split"]),
        "operator_step": int(config["intervention_operator_step_zero_indexed"]),
        "episode_bank_supplied": True,
        "operator_control_bank_supplied": True,
        "control_seed": runner.derive_seed(
            int(config["eval_seed_base"]),
            "intervention_controls",
        ),
        "state_patch_accuracy": 1.0,
        "random_state_patch_accuracy": 0.0,
        "angle_matched_state_control_accuracy": 0.0,
        "reachable_state_control_accuracy": 0.0,
        "random_absolute_state_accuracy": 0.0,
        "zero_state_lesion_original_accuracy": 0.0,
        "operator_patch_accuracy": 1.0,
        "random_operator_patch_accuracy": 0.0,
        "relative_conjugacy_operator_control_accuracy": 0.0,
        "cross_context_operator_control_accuracy": 0.0,
        "native_original_accuracy": 1.0,
        "state_counterfactual_target_distinct_fraction": 1.0,
        "operator_counterfactual_target_distinct_fraction": 1.0,
        "state_transition_eligible_examples": int(config["intervention_examples"]),
        "operator_transition_eligible_examples": int(config["intervention_examples"]),
        "state_patch_transition_accuracy": 1.0,
        "random_state_patch_transition_accuracy": 0.0,
        "angle_matched_state_control_transition_accuracy": 0.0,
        "reachable_state_control_transition_accuracy": 0.0,
        "operator_patch_transition_accuracy": 1.0,
        "random_operator_patch_transition_accuracy": 0.0,
        "relative_conjugacy_operator_control_transition_accuracy": 0.0,
        "cross_context_operator_control_transition_accuracy": 0.0,
        "native_original_defined_fraction": 1.0,
        "state_patch_defined_fraction": 1.0,
        "random_state_patch_defined_fraction": 1.0,
        "angle_matched_state_control_defined_fraction": 1.0,
        "reachable_state_control_defined_fraction": 1.0,
        "random_absolute_state_defined_fraction": 1.0,
        "zero_state_lesion_original_defined_fraction": 1.0,
        "operator_patch_defined_fraction": 1.0,
        "random_operator_patch_defined_fraction": 1.0,
        "relative_conjugacy_operator_control_defined_fraction": 1.0,
        "cross_context_operator_control_defined_fraction": 1.0,
        "state_control_geometry": {
            "control": "unit_sphere_recipient_angle_matched_random_tangent",
            "defined_fraction": 1.0,
            "maximum_norm_error": 0.0,
            "maximum_cosine_error": 0.0,
            "minimum_target_sine": 1.0,
        },
        "operator_control_geometry": {
            "control": "relative_conjugacy_matched_orthogonal",
            "cross_context_control": (
                "independent_context_balanced_slot_with_exact_original_and_alternate_"
                "table_collision_exclusion"
            ),
            "available": True,
            "defined_fraction": 1.0,
            "maximum_chord_distance_error": 0.0,
            "maximum_orthogonality_defect": 0.0,
            "determinant_component_match_fraction": 1.0,
            "minimum_separation_from_alternate": 1.0,
            "cross_context_defined_fraction": 1.0,
            "minimum_cross_context_separation_from_original": 1.0,
            "minimum_cross_context_separation_from_alternate": 1.0,
            "cross_context_base_original_table_collision_count": 2,
            "cross_context_base_alternate_table_collision_count": 1,
            "cross_context_selected_original_table_collision_count": 0,
            "cross_context_selected_alternate_table_collision_count": 0,
        },
    }
    if arm not in runner.POLAR_ARMS:
        causal["relative_conjugacy_operator_control_accuracy"] = None
        causal["relative_conjugacy_operator_control_transition_accuracy"] = None
        causal["relative_conjugacy_operator_control_defined_fraction"] = None
        causal["operator_control_geometry"].update(
            {
                "available": False,
                "defined_fraction": None,
                "maximum_chord_distance_error": None,
                "maximum_orthogonality_defect": None,
                "determinant_component_match_fraction": None,
                "minimum_separation_from_alternate": None,
                "cross_context_defined_fraction": None,
                "minimum_cross_context_separation_from_original": None,
                "minimum_cross_context_separation_from_alternate": None,
                "cross_context_base_original_table_collision_count": 0,
                "cross_context_base_alternate_table_collision_count": 0,
            }
        )
    switch_words = runner.sample_switch_words(
        num_actions=2,
        word_length=int(config["switched_word_length"]),
        count=int(config["switched_word_count"]),
        seed=runner.derive_seed(
            int(config["eval_seed_base"]),
            "switch_words",
        ),
        include_constant_words=True,
    )
    switched_contexts = int(config["switched_contexts"])
    switched_values = switched_contexts * len(switch_words)
    mixed_words = sum(len(set(word)) > 1 for word in switch_words)

    def switched_row(family: str) -> dict[str, object]:
        return {
            "bank": {
                "word_count": len(switch_words),
                "word_length": int(config["switched_word_length"]),
                "fingerprint": _word_digest(
                    torch.from_numpy(runner.canonical_maps(family)).to(
                        dtype=torch.long
                    ),
                    switch_words,
                ),
                "constant_word_count": len(switch_words) - mixed_words,
                "mixed_word_count": mixed_words,
            },
            "episodes": switched_contexts,
            "defined_fraction": 1.0,
            "word_accuracy": 1.0,
            "log_projective_gain": constant_summary(switched_values, 0.0),
            "projective_gain": unit_summary(switched_values),
            "mixed_minus_constant_log_gain": constant_summary(
                switched_contexts,
                0.0,
            ),
            "mixed_enhancement_fraction": 0.0,
        }

    if arm in runner.POLAR_ARMS:
        examples = int(config["ambient_examples"])
        per_batch_matrix_count = 2 * examples
        total_matrix_count = 3 * per_batch_matrix_count

        def geometry_batch() -> dict[str, object]:
            return {
                "examples": examples,
                "operators_per_example": 2,
                "ambient_dimension": 12,
                "frobenius_orthogonality_defect": constant_summary(
                    per_batch_matrix_count, 0.0
                ),
                "spectral_orthogonality_defect": constant_summary(
                    per_batch_matrix_count, 0.0
                ),
                "absolute_determinant": unit_summary(per_batch_matrix_count),
                "absolute_determinant_magnitude_defect": constant_summary(
                    per_batch_matrix_count, 0.0
                ),
                "determinant_components": {
                    "positive": per_batch_matrix_count,
                    "negative": 0,
                    "zero": 0,
                },
                "raw_relative_minimum_singular_value": unit_summary(
                    per_batch_matrix_count
                ),
                "raw_below_relative_singular_floor_fraction": 0.0,
                "postpolar_relative_minimum_singular_value": unit_summary(
                    per_batch_matrix_count
                ),
            }

        polar_geometry: dict[str, object] = {
            "available": True,
            "per_batch": {
                family: geometry_batch()
                for family in ("d4", "c8", "mixed_cycle")
            },
            "aggregate": {
                "batch_count": 3,
                "operator_matrix_count": total_matrix_count,
                "all_finite": True,
                "maximum_frobenius_orthogonality_defect": 0.0,
                "maximum_spectral_orthogonality_defect": 0.0,
                "absolute_determinant": unit_summary(total_matrix_count),
                "maximum_absolute_determinant_magnitude_defect": 0.0,
                "determinant_components": {
                    "positive": total_matrix_count,
                    "negative": 0,
                    "zero": 0,
                },
                "raw_relative_minimum_singular_value": unit_summary(
                    total_matrix_count
                ),
                "raw_below_relative_singular_floor_fraction": 0.0,
                "postpolar_relative_minimum_singular_value": unit_summary(
                    total_matrix_count
                ),
                "switched_defined_fraction": 1.0,
                "maximum_absolute_switched_log_gain": 0.0,
            },
            "switched_sanity": {
                family: switched_row(family)
                for family in ("d4", "c8", "mixed_cycle")
            },
            "thresholds": {
                "orthogonality_tolerance": runner.FROZEN_GATE_THRESHOLDS[
                    "hard_polar_orthogonality_tolerance"
                ],
                "determinant_magnitude_tolerance": runner.FROZEN_GATE_THRESHOLDS[
                    "hard_polar_determinant_tolerance"
                ],
                "projective_log_gain_tolerance": runner.FROZEN_GATE_THRESHOLDS[
                    "hard_polar_projective_log_gain_tolerance"
                ],
                "raw_relative_singular_floor": runner.FROZEN_GATE_THRESHOLDS[
                    "raw_prepolar_relative_singular_warning_floor"
                ],
            },
            "hard_isometry_pass": True,
            "projective_switched_gain_sanity_pass": True,
            "raw_prepolar_well_conditioned_pass": True,
        }
    else:
        polar_geometry = {
            "available": False,
            "reason": (
                "raw operator arm; hard-polar geometry assay is not applicable"
            ),
        }
    switched = switched_row("d4")
    return {
        "heldout_packet_by_prefix": packet,
        "structured_deep_by_depth": deep,
        "null_loop_retention": null_loop,
        "switched_gain": switched,
        "exact_feshbach": {
            "exact_anchor_plane": {
                "ambient_dimension": 12,
                "anchor_count": 8,
                "retained_rank": 8,
                "nuisance_rank": 4,
                "effective_trace": 8.0,
                "complement_effective_trace": 4.0,
                "idempotence_error": 0.0,
                "metric_self_adjoint_error": 0.0,
            },
            "metric": {
                "positive_definite": True,
                "condition_number": 1.0,
                "determinant": 1.0,
                "eigenvalues": [1.0] * 12,
            },
            "generator_blocks": {
                "projective_scale": unit_summary(
                    2 * int(config["feshbach_contexts"])
                ),
                "p_to_p_fraction": constant_summary(
                    2 * int(config["feshbach_contexts"]), 2.0 / 3.0
                ),
                "p_to_q_fraction": constant_summary(
                    2 * int(config["feshbach_contexts"]), 0.0
                ),
                "q_to_p_fraction": constant_summary(
                    2 * int(config["feshbach_contexts"]), 0.0
                ),
                "q_to_q_fraction": constant_summary(
                    2 * int(config["feshbach_contexts"]), 1.0 / 3.0
                ),
                "total_energy": constant_summary(
                    2 * int(config["feshbach_contexts"]), 12.0
                ),
            },
            "delayed_return": {
                "middle_word_maximum_length": 3,
                "middle_word_count": 15,
                "generator_pair_count": 4,
                "full_product_fraction": constant_summary(
                    60 * int(config["feshbach_contexts"]), 0.1
                ),
                "submultiplicative_fraction": constant_summary(
                    60 * int(config["feshbach_contexts"]), 0.1
                ),
                "return_energy": constant_summary(
                    60 * int(config["feshbach_contexts"]), 0.1
                ),
            },
        },
        "hard_polar_geometry": polar_geometry,
        "ambient_complement_causality": ambient,
        "causal_interventions": causal,
    }


def _pilot_adjudication_inputs() -> dict[str, object]:
    config = copy.deepcopy(runner.PROFILES["pilot"])
    records: dict[str, dict[str, dict[str, object]]] = {}
    accepted = int(config["training"]["steps"]) * int(  # type: ignore[index]
        config["training"]["batch_size"]  # type: ignore[index]
    )
    construction = runner.construction_checkpoint_metadata(
        runner.make_v04_construction_bank(
            int(config["training"]["auxiliary_max_depth"])  # type: ignore[index]
        )
    )
    construction_digest = str(construction["construction_digest"])
    for seed in config["seeds"]:  # type: ignore[union-attr]
        by_arm: dict[str, dict[str, object]] = {}
        for arm in runner.ARM_NAMES:
            by_arm[arm] = {
                "training": {
                    "initial_state_digest": f"initial-{seed}",
                    "shared_initialization_digest": f"shared-{seed}",
                    "episode_stream_digest": f"episode-{seed}",
                    "terminal_proposal_stream_digest": "a" * 64,
                    "terminal_firewall_policy_digest": (
                        runner.terminal_firewall_policy_digest()
                    ),
                    "terminal_proposal_count": accepted + 1,
                    "terminal_candidates_accepted": accepted,
                    "terminal_candidates_rejected": 1,
                    "terminal_identity_rejections": 1,
                    "terminal_r2_rejections": 0,
                    "construction_digest": construction_digest,
                    "construction_word_count": 20,
                },
                "checkpoint": {"present": True},
                "checkpoint_reload_verified": True,
                "evaluation": _evaluation(config, arm),
            }
        records[str(seed)] = by_arm

    episode_contracts = {
        "packet": {
            str(prefix): _episode_contract(
                family="d4",
                contexts=int(config["packet_examples"]),
                length=int(prefix),
            )
            for prefix in config["packet_prefixes"]  # type: ignore[union-attr]
        },
        "deep": {
            str(depth): {
                family: _episode_contract(
                    family=family,
                    contexts=int(config["eval_examples"]),
                    length=int(depth),
                )
                for family in ("d4", "c8", "mixed_cycle")
            }
            for depth in config["deep_depths"]  # type: ignore[union-attr]
        },
        "ambient": {
            family: _episode_contract(
                family=family,
                contexts=int(config["ambient_examples"]),
                length=int(config["ambient_length"]),
            )
            for family in ("d4", "c8", "mixed_cycle")
        },
        "null": _episode_contract(
            family="d4", contexts=int(config["null_examples"]), length=0
        ),
        "switched": _episode_contract(
            family="d4", contexts=int(config["switched_contexts"]), length=0
        ),
        "feshbach": _episode_contract(
            family="d4", contexts=int(config["feshbach_contexts"]), length=0
        ),
        "intervention": _episode_contract(
            family="d4",
            contexts=int(config["intervention_examples"]),
            length=int(config["intervention_length"]),
        ),
        "intervention_operator_control": _episode_contract(
            family="d4",
            contexts=int(config["intervention_examples"]),
            length=int(config["intervention_length"]),
        ),
    }
    frozen_heldout = _registered_heldout_bank()
    eval_bank = {
        "heldout_bank": frozen_heldout.to_dict(),
        "heldout_words": [list(word) for word in frozen_heldout.words],
        "heldout_relation_signatures": [
            list(value) for value in frozen_heldout.relation_signatures
        ],
        "switch_bank": _switch_bank("pilot"),
        "cross_context_operator_control": {
            "selection_policy": (
                "balanced_slot_by_bank_row_then_flip_only_on_exact_original_or_"
                "alternate_visible_table_collision"
            ),
            "examples": config["intervention_examples"],
            "operator_step_zero_indexed": config[
                "intervention_operator_step_zero_indexed"
            ],
            "base_original_table_collision_count": 2,
            "base_alternate_table_collision_count": 1,
            "selected_original_table_collision_count": 0,
            "selected_alternate_table_collision_count": 0,
            "selected_slot_counts": [257, 255],
        },
        "episode_receipts": {"contracts": episode_contracts},
    }
    seal = {
        "strict_checkpoint_firewall": True,
        "construction_word_count": 20,
        "construction": construction,
        "checkpoints": [{} for _ in range(len(config["seeds"]) * len(runner.ARM_NAMES))],  # type: ignore[arg-type]
    }
    return {
        "profile": "pilot",
        "config": config,
        "contract_status": {"valid": True},
        "records": records,
        "aggregate": runner.aggregate_records(records, config),
        "paired_analysis": runner.paired_2x2_analysis(records, config),
        "checkpoint_seal": seal,
        "eval_bank": eval_bank,
        "phase_times": {
            "checkpoint_sealed": "2026-09-02T00:00:00+00:00",
            "evaluation_bank_materialized": "2026-09-02T00:00:01+00:00",
        },
        "source_integrity": {"valid": True},
    }


def _adjudicate(inputs: dict[str, object]) -> dict[str, object]:
    return runner.adjudicate(
        inputs["profile"],  # type: ignore[arg-type]
        inputs["config"],  # type: ignore[arg-type]
        inputs["contract_status"],  # type: ignore[arg-type]
        inputs["records"],  # type: ignore[arg-type]
        inputs["aggregate"],  # type: ignore[arg-type]
        inputs["paired_analysis"],  # type: ignore[arg-type]
        inputs["checkpoint_seal"],  # type: ignore[arg-type]
        inputs["eval_bank"],  # type: ignore[arg-type]
        inputs["phase_times"],  # type: ignore[arg-type]
        source_integrity=inputs["source_integrity"],  # type: ignore[arg-type]
    )


def test_synthetic_pilot_fixture_passes_primary_registered_gates() -> None:
    gates = _adjudicate(_pilot_adjudication_inputs())
    assert gates["execution_status"] == "PASS"
    assert gates["assay_status"] == "PASS"
    assert gates["mechanism_status"] == "PASS"
    assert gates["capability_status"] == "PASS"
    assert gates["attribution_status"] == "PASS"
    assert gates["full_developmental_claim"] == "PASS"


@pytest.mark.parametrize(
    ("target", "gate_name"),
    [
        ("packet_membership", "M01_heldout_packet_membership"),
        ("packet_margin", "M02_heldout_margin_p10"),
        ("null_retention", "M03_null_loop_packet_retention"),
        ("deep_accuracy", "C01_primary_d4_depth_curve"),
    ],
)
def test_adjudicate_fails_closed_on_nonfinite_primary_metrics(
    target: str,
    gate_name: str,
) -> None:
    inputs = _pilot_adjudication_inputs()
    records = inputs["records"]
    assert isinstance(records, dict)
    evaluation = records["211"][runner.PRIMARY_ARM]["evaluation"]
    assert isinstance(evaluation, dict)
    if target == "packet_membership":
        evaluation["heldout_packet_by_prefix"]["64"][  # type: ignore[index]
            "strict_membership_fraction"
        ] = math.nan
        group = "mechanism_gates"
        result_contract_gate = "A15_packet_result_contract"
    elif target == "packet_margin":
        evaluation["heldout_packet_by_prefix"]["64"][  # type: ignore[index]
            "suffix_minimum_margin"
        ]["p10"] = math.nan
        group = "mechanism_gates"
        result_contract_gate = "A15_packet_result_contract"
    elif target == "null_retention":
        evaluation["null_loop_retention"]["relations"]["f2"]["by_repeat"]["2"][  # type: ignore[index]
            "strict_membership_fraction"
        ] = math.nan
        group = "mechanism_gates"
        result_contract_gate = "A20_null_result_contract"
    else:
        evaluation["structured_deep_by_depth"]["256"]["per_family"]["d4"][  # type: ignore[index]
            "accuracy"
        ] = math.nan
        group = "capability_gates"
        result_contract_gate = "A16_deep_result_contract"
    inputs["aggregate"] = runner.aggregate_records(records, inputs["config"])  # type: ignore[arg-type]
    inputs["paired_analysis"] = runner.paired_2x2_analysis(  # type: ignore[arg-type]
        records,
        inputs["config"],  # type: ignore[arg-type]
    )
    gates = _adjudicate(inputs)
    assert gates[group][gate_name]["status"] != "PASS"  # type: ignore[index]
    if result_contract_gate is None:
        assert gates["full_developmental_claim"] == "FAIL"
    else:
        assert gates["assay_gates"][result_contract_gate]["status"] == "FAIL"
        assert gates["full_developmental_claim"] == "NOT_EVALUATED"


def test_e01_criterion_describes_the_full_contract_seal() -> None:
    gates = _adjudicate(_pilot_adjudication_inputs())
    criterion = gates["execution_gates"]["E01_preregistration_profile_match"][  # type: ignore[index]
        "criterion"
    ].lower()
    assert "source" in criterion
    assert "all profiles" in criterion
    assert "registered design" in criterion
