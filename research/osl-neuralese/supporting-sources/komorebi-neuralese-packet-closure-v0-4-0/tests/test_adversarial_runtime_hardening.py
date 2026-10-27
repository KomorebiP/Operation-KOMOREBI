from __future__ import annotations

from dataclasses import replace
import math
import sys
from pathlib import Path
from typing import Any

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"
for path in (ROOT, SRC, TESTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


import run_packet_closure as runner
import test_packet_closure_contract as contract_fixtures
import test_packet_closure_eval as eval_fixtures
from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.evaluate import intervention_metrics
from komorebi_neuralese import packet_closure_eval


def _refresh_and_adjudicate(inputs: dict[str, Any]) -> dict[str, Any]:
    records = inputs["records"]
    config = inputs["config"]
    inputs["aggregate"] = runner.aggregate_records(records, config)
    inputs["paired_analysis"] = runner.paired_2x2_analysis(records, config)
    return contract_fixtures._adjudicate(inputs)


def _assay_contract_status(inputs: dict[str, Any], gate_name: str) -> str:
    validators = {
        "A15_packet_result_contract": runner.validate_packet_result_contract,
        "A16_deep_result_contract": runner.validate_deep_result_contract,
        "A17_ambient_result_contract": runner.validate_ambient_result_contract,
        "A19_switched_result_contract": runner.validate_switched_result_contract,
        "A20_null_result_contract": runner.validate_null_result_contract,
        "A21_feshbach_result_contract": runner.validate_feshbach_result_contract,
    }
    config = inputs["config"]
    cross_context = inputs["eval_bank"]["cross_context_operator_control"]
    for seed in config["seeds"]:
        for arm in runner.ARM_NAMES:
            evaluation = inputs["records"][str(seed)][arm]["evaluation"]
            if gate_name == "A18_causal_result_contract":
                valid = runner.validate_causal_result_contract(
                    evaluation,
                    config,
                    arm,
                    cross_context,
                )
            elif gate_name == "A22_hard_polar_result_contract":
                valid = runner.validate_hard_polar_result_contract(
                    evaluation,
                    config,
                    arm,
                )
            else:
                valid = validators[gate_name](evaluation, config)
            if not valid:
                return "FAIL"
    return "PASS"


@pytest.mark.parametrize("corruption", ["endpoint", "gain"])
def test_switched_nonfinite_endpoint_or_gain_is_undefined(
    monkeypatch: pytest.MonkeyPatch,
    corruption: str,
) -> None:
    original = packet_closure_eval.projective_sequence_jacobian

    def corrupted(*args: Any, **kwargs: Any) -> Any:
        result = original(*args, **kwargs)
        if corruption == "endpoint":
            return replace(result, endpoint=torch.full_like(result.endpoint, torch.nan))
        return replace(
            result,
            worst_singular_amplification=math.nan,
            log_worst_singular_amplification=math.nan,
        )

    monkeypatch.setattr(
        packet_closure_eval,
        "projective_sequence_jacobian",
        corrupted,
    )
    examples = 3
    words = ((0, 0), (0, 1), (1, 0))
    result = packet_closure_eval.evaluate_sampled_switched_gain(
        eval_fixtures.ExactTableProjectiveModel(),
        eval_fixtures._batch("d4", seed=1601, examples=examples, length=4),
        words,
        eval_fixtures._transitions("d4"),
    )

    assert not bool(result.defined.any())
    assert bool(torch.isnan(result.log_gain).all())
    summary = result.to_dict()
    assert summary["defined_fraction"] == 0.0
    assert summary["word_accuracy"] is None
    assert result.log_gain.shape == (examples, len(words))
    assert summary["log_projective_gain"]["count"] == 0
    assert summary["log_projective_gain"]["finite_count"] == 0


def test_nan_logits_are_excluded_from_conditional_causal_transitions() -> None:
    examples = 12
    length = 6
    model = eval_fixtures.ExactTableProjectiveModel()
    with torch.no_grad():
        model.decoder.weight.fill_(torch.nan)
    result = intervention_metrics(
        model,
        examples,
        batch_size=5,
        seed=991,
        device=torch.device("cpu"),
        length=length,
        split=3,
        operator_step=2,
        episode_batch=EpisodeGenerator(503).sample(
            examples,
            length,
            family="d4",
        ),
        operator_control_batch=EpisodeGenerator(509).sample(
            examples,
            length,
            family="d4",
        ),
        control_seed=997,
    )

    assert result["native_original_accuracy"] == 0.0
    assert result["native_original_defined_fraction"] == 0.0
    assert result["state_transition_eligible_examples"] == 0
    assert result["operator_transition_eligible_examples"] == 0
    for condition in (
        "state_patch",
        "angle_matched_state_control",
        "reachable_state_control",
        "random_state_patch",
        "operator_patch",
        "random_operator_patch",
        "cross_context_operator_control",
    ):
        assert result[f"{condition}_defined_fraction"] == 0.0
        assert result[f"{condition}_transition_accuracy"] is None


def test_nan_ambient_logits_make_the_assay_undefined() -> None:
    model = eval_fixtures.AmbientBlockModel()
    with torch.no_grad():
        model.decoder.weight.fill_(torch.nan)
    result = packet_closure_eval.evaluate_ambient_complement_causality(
        model,
        eval_fixtures._batch("d4", seed=1613, examples=8, length=6),
        random_seed=1619,
    )

    for condition in (
        result.native,
        result.p_confined,
        result.midpoint_q_ablated,
        result.matched_random_rank_control,
    ):
        assert condition.finite_fraction == 0.0
        assert condition.defined_fraction == 0.0
    assert result.evidence_status == "CAUSAL_ROLLOUT_UNDEFINED"
    assert not result.supports_specific_ambient_attribution


@pytest.mark.parametrize(
    "condition",
    (
        "native",
        "p_confined",
        "midpoint_q_ablated",
        "matched_random_rank_control",
    ),
)
@pytest.mark.parametrize(
    ("field", "replacement"),
    (("finite_fraction", math.nan), ("defined_fraction", 0.0)),
)
def test_d01_rejects_undefined_or_nonfinite_serialized_conditions(
    condition: str,
    field: str,
    replacement: float,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "ambient_complement_causality"
    ]["d4"]
    row["conditions"][condition][field] = replacement

    gate = _refresh_and_adjudicate(inputs)["ambient_attribution_gates"][
        "D01_specific_ambient_complement_use"
    ]
    assert gate["status"] == "FAIL"


@pytest.mark.parametrize(
    ("field_path", "replacement"),
    (
        (("conditions", "native", "accuracy"), math.inf),
        (("performance_drops", "midpoint_q_ablation"), math.nan),
        (("performance_drops", "q_specific_excess_over_random"), math.nan),
        (("attribution", "supports_specific_ambient_attribution"), False),
    ),
)
def test_d01_rechecks_numeric_support_instead_of_trusting_status(
    field_path: tuple[str, ...],
    replacement: object,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row: dict[str, Any] = inputs["records"]["211"][runner.PRIMARY_ARM][
        "evaluation"
    ]["ambient_complement_causality"]["d4"]
    target: dict[str, Any] = row
    for key in field_path[:-1]:
        target = target[key]
    target[field_path[-1]] = replacement

    gate = _refresh_and_adjudicate(inputs)["ambient_attribution_gates"][
        "D01_specific_ambient_complement_use"
    ]
    assert gate["status"] == "FAIL"


@pytest.mark.parametrize(
    ("metric", "gate_name", "mutate"),
    (
        (
            "switched_max_gain",
            "M04_switched_projective_gain",
            lambda evaluation: evaluation["switched_gain"]["projective_gain"].__setitem__(
                "maximum", math.nan
            ),
        ),
        (
            "switched_defined_fraction",
            "M05_switched_domain_defined",
            lambda evaluation: evaluation["switched_gain"].__setitem__(
                "defined_fraction", math.nan
            ),
        ),
        (
            "switched_word_accuracy",
            "M06_switched_word_accuracy",
            lambda evaluation: evaluation["switched_gain"].__setitem__(
                "word_accuracy", math.nan
            ),
        ),
    ),
)
def test_nan_scalar_cannot_be_masked_by_aggregate_filtering(
    metric: str,
    gate_name: str,
    mutate: Any,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    evaluation = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"]
    mutate(evaluation)
    gates = _refresh_and_adjudicate(inputs)

    assert inputs["aggregate"][runner.PRIMARY_ARM]["metrics"][metric]["n"] == 2
    assert gates["assay_gates"]["A19_switched_result_contract"]["status"] == "FAIL"
    assert gates["mechanism_gates"][gate_name]["status"] != "PASS"
    assert gates["full_developmental_claim"] == "NOT_EVALUATED"


@pytest.mark.parametrize("summary_kind", ("packet", "relation_group"))
def test_packet_margin_requires_every_reported_value_to_be_finite(
    summary_kind: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    evaluation = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"]
    packet_row = evaluation["heldout_packet_by_prefix"]["64"]
    summary = (
        packet_row["suffix_minimum_margin"]
        if summary_kind == "packet"
        else packet_row["relation_groups"][0]["minimum_margin"]
    )
    summary["finite_count"] -= 1

    coverage = runner.validate_primary_closure_grid(evaluation, inputs["config"])
    gates = _refresh_and_adjudicate(inputs)
    assert not coverage["packet_margin_finiteness_exact"]
    assert gates["mechanism_gates"]["M02_heldout_margin_p10"]["status"] == "FAIL"


@pytest.mark.parametrize(
    ("corruption", "expected_statuses"),
    (
        (
            "margin",
            ("NOT_EVALUABLE", "PASS", "PASS"),
        ),
        (
            "membership",
            ("FAIL", "NOT_EVALUABLE", "PASS"),
        ),
        (
            "null",
            ("FAIL", "PASS", "NOT_EVALUABLE"),
        ),
    ),
)
def test_objective_metrics_are_independently_evaluable(
    corruption: str,
    expected_statuses: tuple[str, str, str],
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    evaluation = inputs["records"]["211"]["polar_supervised"]["evaluation"]
    if corruption == "margin":
        evaluation["heldout_packet_by_prefix"]["64"]["suffix_minimum_margin"][
            "finite_count"
        ] -= 1
    elif corruption == "membership":
        evaluation["heldout_packet_by_prefix"]["64"][
            "strict_membership_fraction"
        ] = math.nan
    else:
        evaluation["null_loop_retention"]["relations"]["f2"]["by_repeat"][
            "2"
        ]["strict_membership_fraction"] = math.nan

    objective = _refresh_and_adjudicate(inputs)["objective_effect_gates"]
    observed = tuple(
        objective[name]["status"]
        for name in (
            "O01_cr_grid_margin_benefit",
            "O02_cr_grid_membership_nonnegative_direction",
            "O03_cr_null_closure_nonnegative_direction",
        )
    )
    assert observed == expected_statuses


def test_zero_baseline_null_closure_remains_defined_as_zero() -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    evaluation = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"]
    null = evaluation["null_loop_retention"]
    null["baseline"]["strict_membership_fraction"] = 0.0
    for relation in null["relations"].values():
        for repeat in relation["by_repeat"].values():
            repeat["conditional_retention_fraction"] = None

    scalars = runner.scalar_metrics(evaluation, inputs["config"])
    assert scalars["null_baseline_membership"] == 0.0
    assert scalars["null_conditional_retention"] is None
    assert scalars["null_closure"] == 0.0


@pytest.mark.parametrize(
    ("field", "replacement", "state_status", "operator_status"),
    (
        ("native_original_accuracy", 0.0, "FAIL", "FAIL"),
        ("native_original_defined_fraction", 0.0, "FAIL", "FAIL"),
        ("state_counterfactual_target_distinct_fraction", 0.5, "FAIL", "PASS"),
        ("operator_counterfactual_target_distinct_fraction", 0.5, "PASS", "FAIL"),
        ("state_patch_defined_fraction", 0.5, "FAIL", "PASS"),
        ("operator_patch_defined_fraction", 0.5, "PASS", "FAIL"),
        ("state_transition_eligible_examples", 0, "FAIL", "PASS"),
        ("operator_transition_eligible_examples", 0, "PASS", "FAIL"),
        ("state_patch_transition_accuracy", math.nan, "FAIL", "PASS"),
        ("operator_patch_transition_accuracy", math.nan, "PASS", "FAIL"),
    ),
)
def test_conditional_causal_gates_require_native_distinct_defined_population(
    field: str,
    replacement: object,
    state_status: str,
    operator_status: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    causal = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "causal_interventions"
    ]
    causal[field] = replacement

    adjudication = _refresh_and_adjudicate(inputs)
    gates = adjudication["attribution_gates"]
    assert gates["T02_causal_state_patch_specificity"]["status"] == state_status
    assert gates["T03_causal_operator_patch_specificity"]["status"] == operator_status
    if isinstance(replacement, float) and math.isnan(replacement):
        assert adjudication["assay_gates"]["A18_causal_result_contract"]["status"] == "FAIL"
        assert adjudication["full_developmental_claim"] == "NOT_EVALUATED"


@pytest.mark.parametrize(
    ("family", "gate_group", "gate_name"),
    (
        ("d4", "capability_gates", "C01_primary_d4_depth_curve"),
        (
            "c8",
            "secondary_transfer_gates",
            "S01_zero_shot_cross_family_depth_curve",
        ),
        (
            "mixed_cycle",
            "secondary_transfer_gates",
            "S01_zero_shot_cross_family_depth_curve",
        ),
    ),
)
@pytest.mark.parametrize("replacement", (0.0, math.nan))
def test_deep_accuracy_requires_fully_finite_outputs(
    family: str,
    gate_group: str,
    gate_name: str,
    replacement: float,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "structured_deep_by_depth"
    ]["512"]["per_family"][family]["finite_fraction"] = replacement

    gates = _refresh_and_adjudicate(inputs)
    assert gates["assay_gates"]["A16_deep_result_contract"]["status"] == "FAIL"
    assert gates[gate_group][gate_name]["status"] == "NOT_EVALUABLE"
    assert gates["full_developmental_claim"] == "NOT_EVALUATED"


@pytest.mark.parametrize(
    "corruption",
    (
        "missing_depth",
        "extra_depth",
        "missing_family",
        "extra_family",
        "wrong_examples",
        "wrong_reported_depth",
    ),
)
def test_deep_grid_requires_exact_depth_family_and_example_sizes(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    evaluation = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"]
    deep = evaluation["structured_deep_by_depth"]
    if corruption == "missing_depth":
        deep.pop("512")
    elif corruption == "extra_depth":
        deep["1024"] = deep["512"]
    elif corruption == "missing_family":
        deep["512"]["per_family"].pop("c8")
    elif corruption == "extra_family":
        deep["512"]["per_family"]["random"] = deep["512"]["per_family"]["d4"]
    elif corruption == "wrong_examples":
        deep["512"]["per_family"]["d4"]["examples"] += 1
    else:
        deep["512"]["per_family"]["d4"]["depth"] += 1

    result = runner.validate_primary_closure_grid(evaluation, inputs["config"])
    assert not result["structured_deep_grid_exact"]
    assert not result["valid"]


def test_all_per_record_result_contracts_accept_the_complete_fixture() -> None:
    gates = _refresh_and_adjudicate(
        contract_fixtures._pilot_adjudication_inputs()
    )["assay_gates"]
    for name in (
        "A15_packet_result_contract",
        "A16_deep_result_contract",
        "A17_ambient_result_contract",
        "A18_causal_result_contract",
        "A19_switched_result_contract",
        "A20_null_result_contract",
        "A21_feshbach_result_contract",
        "A22_hard_polar_result_contract",
    ):
        assert gates[name]["status"] == "PASS"


@pytest.mark.parametrize(
    "corruption",
    (
        "relation_counts_1_170",
        "missing_bank",
        "missing_examples",
        "missing_boundary_tolerance",
        "wrong_examples",
        "float_examples",
        "nonfinite_boundary_tolerance",
        "membership_above_one",
        "negative_suffix_accuracy",
        "finite_margin_fraction_above_one",
    ),
)
def test_packet_result_contract_rejects_incomplete_or_impossible_rows(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "heldout_packet_by_prefix"
    ]["64"]
    if corruption == "relation_counts_1_170":
        row["relation_groups"][0]["suffix_count"] = 1
        row["relation_groups"][1]["suffix_count"] = 170
    elif corruption == "missing_bank":
        row.pop("bank")
    elif corruption == "missing_examples":
        row.pop("examples")
    elif corruption == "missing_boundary_tolerance":
        row.pop("boundary_tolerance")
    elif corruption == "wrong_examples":
        row["examples"] += 1
    elif corruption == "float_examples":
        row["examples"] = float(row["examples"])
    elif corruption == "nonfinite_boundary_tolerance":
        row["boundary_tolerance"] = math.nan
    elif corruption == "membership_above_one":
        row["strict_membership_fraction"] = 1.01
    elif corruption == "negative_suffix_accuracy":
        row["suffix_accuracy"] = -0.01
    else:
        row["finite_margin_fraction"] = 1.01

    assert (
        _assay_contract_status(inputs, "A15_packet_result_contract") == "FAIL"
    )


@pytest.mark.parametrize(
    "corruption",
    (
        "negative_accuracy",
        "accuracy_above_one",
        "nonfinite_accuracy",
        "boolean_finite_fraction",
        "finite_fraction_above_one",
        "float_examples",
        "float_depth",
        "wrong_total_examples",
        "aggregate_accuracy_above_one",
    ),
)
def test_deep_result_contract_rejects_impossible_accuracy_or_grid_receipts(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    depth_row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "structured_deep_by_depth"
    ]["512"]
    family_row = depth_row["per_family"]["d4"]
    if corruption == "negative_accuracy":
        family_row["accuracy"] = -0.01
    elif corruption == "accuracy_above_one":
        family_row["accuracy"] = 1.01
    elif corruption == "nonfinite_accuracy":
        family_row["accuracy"] = math.nan
    elif corruption == "boolean_finite_fraction":
        family_row["finite_fraction"] = True
    elif corruption == "finite_fraction_above_one":
        family_row["finite_fraction"] = 1.01
    elif corruption == "float_examples":
        family_row["examples"] = float(family_row["examples"])
    elif corruption == "float_depth":
        family_row["depth"] = float(family_row["depth"])
    elif corruption == "wrong_total_examples":
        depth_row["total_examples"] += 1
    else:
        depth_row["pooled_accuracy"] = 1.01

    assert _assay_contract_status(inputs, "A16_deep_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "corruption",
    (
        "native_accuracy_above_one",
        "negative_condition_accuracy",
        "nonfinite_condition_accuracy",
        "drop_above_one",
        "drop_inconsistent_with_accuracy",
        "unsupported_values_with_supported_status",
        "unknown_status",
        "missing_condition",
        "boolean_finite_fraction",
    ),
)
def test_ambient_result_contract_rejects_impossible_outcomes_and_status(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "ambient_complement_causality"
    ]["d4"]
    if corruption == "native_accuracy_above_one":
        row["conditions"]["native"]["accuracy"] = 1.01
    elif corruption == "negative_condition_accuracy":
        row["conditions"]["p_confined"]["accuracy"] = -0.01
    elif corruption == "nonfinite_condition_accuracy":
        row["conditions"]["midpoint_q_ablated"]["accuracy"] = math.nan
    elif corruption == "drop_above_one":
        row["performance_drops"]["midpoint_q_ablation"] = 1.01
    elif corruption == "drop_inconsistent_with_accuracy":
        row["performance_drops"]["matched_random_rank_control"] = 0.25
    elif corruption == "unsupported_values_with_supported_status":
        row["conditions"]["midpoint_q_ablated"]["accuracy"] = 1.0
        row["performance_drops"]["midpoint_q_ablation"] = 0.0
        row["performance_drops"]["q_specific_excess_over_random"] = -0.05
    elif corruption == "unknown_status":
        row["attribution"]["status"] = "SUPPORTED"
    elif corruption == "missing_condition":
        row["conditions"].pop("matched_random_rank_control")
    else:
        row["conditions"]["native"]["finite_fraction"] = True

    assert _assay_contract_status(inputs, "A17_ambient_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "corruption",
    (
        "native_q_energy_incomplete",
        "native_q_energy_above_one",
        "applied_random_energy_incomplete",
        "applied_q_energy_above_one",
        "applied_mean_difference_exceeds_error",
        "applied_mean_error_exceeds_maximum",
        "ideal_random_energy_incomplete",
        "ideal_random_energy_above_one",
        "ideal_mean_difference_exceeds_error",
        "ideal_mean_error_exceeds_maximum",
    ),
)
def test_ambient_result_contract_links_bounded_energy_summaries_to_errors(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "ambient_complement_causality"
    ]["d4"]
    matched = row["matched_random_control"]
    ideal = matched["ideal_construction"]

    def set_summary_value(summary: dict[str, object], value: float) -> None:
        for key in ("minimum", "p10", "median", "mean", "p90", "maximum"):
            summary[key] = value

    if corruption == "native_q_energy_incomplete":
        row["q_energy_fraction"]["initial"]["finite_count"] -= 1
    elif corruption == "native_q_energy_above_one":
        row["q_energy_fraction"]["all_native_states"]["maximum"] = 1.01
    elif corruption == "applied_random_energy_incomplete":
        matched["removed_energy_fraction"]["finite_count"] -= 1
    elif corruption == "applied_q_energy_above_one":
        matched["q_removed_energy_fraction"]["maximum"] = 1.01
    elif corruption == "applied_mean_difference_exceeds_error":
        set_summary_value(matched["removed_energy_fraction"], 0.5)
    elif corruption == "applied_mean_error_exceeds_maximum":
        matched["q_energy_match_mean_absolute_error"] = 0.1
    elif corruption == "ideal_random_energy_incomplete":
        ideal["removed_energy_fraction"]["finite_count"] -= 1
    elif corruption == "ideal_random_energy_above_one":
        ideal["removed_energy_fraction"]["maximum"] = 1.01
    elif corruption == "ideal_mean_difference_exceeds_error":
        set_summary_value(ideal["removed_energy_fraction"], 0.5)
    else:
        ideal["q_energy_match_mean_absolute_error"] = 0.1

    assert _assay_contract_status(inputs, "A17_ambient_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "corruption",
    (
        "examples_too_large",
        "float_examples",
        "wrong_length",
        "float_length",
        "wrong_split",
        "wrong_operator_step",
        "episode_bank_false",
        "episode_bank_integer_true",
        "operator_bank_false",
        "wrong_control_seed",
        "float_control_seed",
    ),
)
def test_causal_result_contract_rejects_wrong_registered_metadata(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    config = inputs["config"]
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "causal_interventions"
    ]
    if corruption == "examples_too_large":
        row["examples"] = int(config["intervention_examples"]) + 1
    elif corruption == "float_examples":
        row["examples"] = float(row["examples"])
    elif corruption == "wrong_length":
        row["length"] += 1
    elif corruption == "float_length":
        row["length"] = float(row["length"])
    elif corruption == "wrong_split":
        row["state_split"] += 1
    elif corruption == "wrong_operator_step":
        row["operator_step"] += 1
    elif corruption == "episode_bank_false":
        row["episode_bank_supplied"] = False
    elif corruption == "episode_bank_integer_true":
        row["episode_bank_supplied"] = 1
    elif corruption == "operator_bank_false":
        row["operator_control_bank_supplied"] = False
    elif corruption == "wrong_control_seed":
        row["control_seed"] += 1
    else:
        row["control_seed"] = float(row["control_seed"])

    assert _assay_contract_status(inputs, "A18_causal_result_contract") == "FAIL"


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("state_transition_eligible_examples", 513),
        ("operator_transition_eligible_examples", 513),
        ("state_transition_eligible_examples", 512.0),
        ("state_patch_accuracy", -0.01),
        ("state_patch_accuracy", 1.01),
        ("native_original_defined_fraction", 1.01),
        ("state_counterfactual_target_distinct_fraction", -0.01),
        ("operator_patch_transition_accuracy", 1.01),
        ("state_patch_accuracy", 0.1),
        ("state_patch_defined_fraction", 0.1),
        ("state_counterfactual_target_distinct_fraction", 0.1),
        ("state_patch_transition_accuracy", 0.1),
    ),
)
def test_causal_result_contract_rejects_ranges_counts_and_noninteger_closure(
    field: str,
    replacement: object,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "causal_interventions"
    ]
    row[field] = replacement
    assert _assay_contract_status(inputs, "A18_causal_result_contract") == "FAIL"


@pytest.mark.parametrize("population", ("state", "operator"))
def test_causal_transition_none_is_required_exactly_for_zero_denominator(
    population: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "causal_interventions"
    ]
    names = (
        (
            "state_patch",
            "random_state_patch",
            "angle_matched_state_control",
            "reachable_state_control",
        )
        if population == "state"
        else (
            "operator_patch",
            "random_operator_patch",
            "relative_conjugacy_operator_control",
            "cross_context_operator_control",
        )
    )
    row[f"{population}_transition_eligible_examples"] = 0
    row[f"{population}_counterfactual_target_distinct_fraction"] = 0.0
    for name in names:
        row[f"{name}_transition_accuracy"] = None

    assert _assay_contract_status(inputs, "A18_causal_result_contract") == "PASS"


@pytest.mark.parametrize("population", ("state", "operator"))
def test_causal_transition_none_is_rejected_for_positive_denominator(
    population: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "causal_interventions"
    ]
    row[f"{population}_patch_transition_accuracy"] = None
    assert _assay_contract_status(inputs, "A18_causal_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "field",
    (
        "relative_conjugacy_operator_control_accuracy",
        "relative_conjugacy_operator_control_defined_fraction",
        "relative_conjugacy_operator_control_transition_accuracy",
    ),
)
def test_raw_causal_rows_cannot_claim_relative_conjugacy_results(field: str) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"]["euclidean_supervised"]["evaluation"][
        "causal_interventions"
    ]
    row[field] = 0.0
    assert _assay_contract_status(inputs, "A18_causal_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "field",
    (
        "relative_conjugacy_operator_control_accuracy",
        "relative_conjugacy_operator_control_defined_fraction",
        "relative_conjugacy_operator_control_transition_accuracy",
    ),
)
def test_polar_causal_rows_require_relative_conjugacy_results(field: str) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "causal_interventions"
    ]
    row[field] = None
    assert _assay_contract_status(inputs, "A18_causal_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "corruption",
    (
        "missing_bank",
        "extra_field",
        "wrong_word_count",
        "float_word_count",
        "wrong_word_length",
        "wrong_fingerprint",
        "wrong_constant_count",
        "wrong_mixed_count",
        "wrong_episodes",
        "float_episodes",
        "boolean_defined_fraction",
        "inconsistent_defined_fraction",
        "word_accuracy_above_one",
        "word_accuracy_none_when_defined",
        "incomplete_log_gain",
        "incomplete_projective_gain",
        "incomplete_mixed_difference",
        "nonfinite_gain_statistic",
        "mixed_fraction_above_one",
    ),
)
def test_switched_result_contract_rejects_schema_and_count_mutations(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "switched_gain"
    ]
    if corruption == "missing_bank":
        row.pop("bank")
    elif corruption == "extra_field":
        row["unexpected"] = True
    elif corruption == "wrong_word_count":
        row["bank"]["word_count"] -= 1
    elif corruption == "float_word_count":
        row["bank"]["word_count"] = float(row["bank"]["word_count"])
    elif corruption == "wrong_word_length":
        row["bank"]["word_length"] += 1
    elif corruption == "wrong_fingerprint":
        row["bank"]["fingerprint"] = "0" * 64
    elif corruption == "wrong_constant_count":
        row["bank"]["constant_word_count"] += 1
    elif corruption == "wrong_mixed_count":
        row["bank"]["mixed_word_count"] -= 1
    elif corruption == "wrong_episodes":
        row["episodes"] += 1
    elif corruption == "float_episodes":
        row["episodes"] = float(row["episodes"])
    elif corruption == "boolean_defined_fraction":
        row["defined_fraction"] = True
    elif corruption == "inconsistent_defined_fraction":
        row["defined_fraction"] = 0.5
    elif corruption == "word_accuracy_above_one":
        row["word_accuracy"] = 1.01
    elif corruption == "word_accuracy_none_when_defined":
        row["word_accuracy"] = None
    elif corruption == "incomplete_log_gain":
        row["log_projective_gain"]["finite_count"] -= 1
    elif corruption == "incomplete_projective_gain":
        row["projective_gain"]["finite_count"] -= 1
    elif corruption == "incomplete_mixed_difference":
        row["mixed_minus_constant_log_gain"]["finite_count"] -= 1
    elif corruption == "nonfinite_gain_statistic":
        row["projective_gain"]["maximum"] = math.nan
    else:
        row["mixed_enhancement_fraction"] = 1.01

    assert _assay_contract_status(inputs, "A19_switched_result_contract") == "FAIL"


def test_switched_result_contract_accepts_a_coherent_fully_undefined_audit() -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "switched_gain"
    ]
    empty_summary = {
        "count": 0,
        "finite_count": 0,
        "minimum": None,
        "p10": None,
        "median": None,
        "mean": None,
        "p90": None,
        "maximum": None,
    }
    row["defined_fraction"] = 0.0
    row["word_accuracy"] = None
    row["log_projective_gain"] = dict(empty_summary)
    row["projective_gain"] = dict(empty_summary)
    row["mixed_minus_constant_log_gain"] = dict(empty_summary)
    row["mixed_enhancement_fraction"] = None

    assert _assay_contract_status(inputs, "A19_switched_result_contract") == "PASS"


def test_switched_result_contract_rejects_more_enhancements_than_defined_pairs() -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    row = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "switched_gain"
    ]
    total_cells = row["episodes"] * row["bank"]["word_count"]
    row["defined_fraction"] = 1.0 / total_cells
    row["word_accuracy"] = 1.0
    zero_summary = {
        "count": 1,
        "finite_count": 1,
        "minimum": 0.0,
        "p10": 0.0,
        "median": 0.0,
        "mean": 0.0,
        "p90": 0.0,
        "maximum": 0.0,
    }
    row["log_projective_gain"] = dict(zero_summary)
    row["projective_gain"] = {
        key: (1.0 if key not in {"count", "finite_count"} else value)
        for key, value in zero_summary.items()
    }
    row["mixed_minus_constant_log_gain"] = dict(zero_summary)
    row["mixed_enhancement_fraction"] = 0.0

    assert _assay_contract_status(inputs, "A19_switched_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "corruption",
    (
        "missing_bank",
        "missing_repeat",
        "conditional_none_with_baseline",
        "impossible_conditional_intersection",
        "word_conditional_above_one",
        "accuracy_above_finite_fraction",
        "strict_above_macro",
        "incomplete_margin",
        "wrong_ratio_count",
        "crossing_at_unregistered_repeat",
        "inconsistent_never_fraction",
    ),
)
def test_null_result_contract_rejects_count_and_conditional_mutations(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    null = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "null_loop_retention"
    ]
    relation = null["relations"]["f2"]
    repeat = relation["by_repeat"]["2"]
    if corruption == "missing_bank":
        null.pop("bank")
    elif corruption == "missing_repeat":
        relation["by_repeat"].pop("2")
    elif corruption == "conditional_none_with_baseline":
        repeat["conditional_retention_fraction"] = None
    elif corruption == "impossible_conditional_intersection":
        repeat["conditional_retention_fraction"] = 0.0
    elif corruption == "word_conditional_above_one":
        repeat["conditional_word_retention_fraction"] = 1.01
    elif corruption == "accuracy_above_finite_fraction":
        repeat["finite_logit_fraction"] = 0.5
    elif corruption == "strict_above_macro":
        repeat["macro_relation_group_membership_fraction"] = 0.5
    elif corruption == "incomplete_margin":
        repeat["minimum_margin"]["finite_count"] -= 1
    elif corruption == "wrong_ratio_count":
        repeat["positive_baseline_margin_ratio"]["count"] -= 1
        repeat["positive_baseline_margin_ratio"]["finite_count"] -= 1
    elif corruption == "crossing_at_unregistered_repeat":
        relation["first_sampled_crossing"]["observed"] = [3]
        relation["first_sampled_crossing"][
            "never_fraction_among_baseline_members"
        ] = (int(inputs["config"]["null_examples"]) - 1) / int(
            inputs["config"]["null_examples"]
        )
    else:
        relation["first_sampled_crossing"][
            "never_fraction_among_baseline_members"
        ] = 0.5

    assert _assay_contract_status(inputs, "A20_null_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "corruption",
    (
        "missing_plane",
        "extra_top_level_field",
        "wrong_ambient_dimension",
        "float_retained_rank",
        "trace_rank_mismatch",
        "nonfinite_projector_error",
        "truthy_positive_definite",
        "condition_below_one",
        "determinant_eigenvalue_mismatch",
        "integer_eigenvalue",
        "unsorted_eigenvalues",
        "missing_generator_summary",
        "wrong_generator_count",
        "incomplete_generator_summary",
        "negative_generator_statistic",
        "fractions_do_not_partition_energy",
        "wrong_middle_word_count",
        "wrong_delayed_summary_count",
        "negative_delayed_statistic",
        "submultiplicative_fraction_above_one",
    ),
)
def test_feshbach_result_contract_rejects_schema_spectral_and_count_mutations(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    feshbach = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "exact_feshbach"
    ]
    plane = feshbach["exact_anchor_plane"]
    metric = feshbach["metric"]
    blocks = feshbach["generator_blocks"]
    delayed = feshbach["delayed_return"]
    if corruption == "missing_plane":
        feshbach.pop("exact_anchor_plane")
    elif corruption == "extra_top_level_field":
        feshbach["claim"] = True
    elif corruption == "wrong_ambient_dimension":
        plane["ambient_dimension"] = 13
    elif corruption == "float_retained_rank":
        plane["retained_rank"] = 8.0
    elif corruption == "trace_rank_mismatch":
        plane["effective_trace"] = 7.5
    elif corruption == "nonfinite_projector_error":
        plane["idempotence_error"] = math.nan
    elif corruption == "truthy_positive_definite":
        metric["positive_definite"] = "yes"
    elif corruption == "condition_below_one":
        metric["condition_number"] = 0.5
    elif corruption == "determinant_eigenvalue_mismatch":
        metric["determinant"] = 2.0
    elif corruption == "integer_eigenvalue":
        metric["eigenvalues"][0] = 1
    elif corruption == "unsorted_eigenvalues":
        metric["eigenvalues"][:2] = [2.0, 1.0]
    elif corruption == "missing_generator_summary":
        blocks.pop("q_to_p_fraction")
    elif corruption == "wrong_generator_count":
        blocks["total_energy"]["count"] -= 1
    elif corruption == "incomplete_generator_summary":
        blocks["projective_scale"]["finite_count"] -= 1
    elif corruption == "negative_generator_statistic":
        blocks["q_to_p_fraction"]["minimum"] = -1.0
    elif corruption == "fractions_do_not_partition_energy":
        for key in ("minimum", "p10", "median", "mean", "p90", "maximum"):
            blocks["p_to_p_fraction"][key] = 0.5
    elif corruption == "wrong_middle_word_count":
        delayed["middle_word_count"] = 14
    elif corruption == "wrong_delayed_summary_count":
        delayed["return_energy"]["count"] -= 1
    elif corruption == "negative_delayed_statistic":
        delayed["return_energy"]["minimum"] = -1.0
    else:
        for key in ("minimum", "p10", "median", "mean", "p90", "maximum"):
            delayed["submultiplicative_fraction"][key] = 1.1

    assert _assay_contract_status(inputs, "A21_feshbach_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "corruption",
    (
        "available_true",
        "available_truthy_string",
        "missing_reason",
        "extra_field",
    ),
)
def test_hard_polar_result_contract_requires_exact_raw_arm_payload(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    geometry = inputs["records"]["211"]["euclidean_supervised"]["evaluation"][
        "hard_polar_geometry"
    ]
    if corruption == "available_true":
        geometry["available"] = True
    elif corruption == "available_truthy_string":
        geometry["available"] = "no"
    elif corruption == "missing_reason":
        geometry.pop("reason")
    else:
        geometry["aggregate"] = {}

    assert _assay_contract_status(inputs, "A22_hard_polar_result_contract") == "FAIL"


@pytest.mark.parametrize(
    "corruption",
    (
        "available_truthy_string",
        "missing_per_batch",
        "extra_top_level_field",
        "missing_family",
        "wrong_examples",
        "float_operator_count",
        "missing_family_summary",
        "wrong_family_summary_count",
        "incomplete_family_summary",
        "negative_family_statistic",
        "relative_singular_value_above_one",
        "determinant_component_mismatch",
        "nonintegral_raw_below_fraction",
        "uncovered_nonfinite_raw_value",
        "wrong_threshold",
        "wrong_family_switched_fingerprint",
        "wrong_aggregate_matrix_count",
        "truthy_aggregate_all_finite",
        "aggregate_maximum_mismatch",
        "aggregate_pooled_summary_mismatch",
        "aggregate_component_mismatch",
        "aggregate_raw_below_mismatch",
        "aggregate_switched_fraction_mismatch",
        "aggregate_switched_log_maximum_mismatch",
        "hard_isometry_flag_lies",
        "switched_sanity_flag_lies",
        "raw_condition_flag_lies",
    ),
)
def test_hard_polar_result_contract_rejects_geometry_and_reconciliation_mutations(
    corruption: str,
) -> None:
    inputs = contract_fixtures._pilot_adjudication_inputs()
    geometry = inputs["records"]["211"][runner.PRIMARY_ARM]["evaluation"][
        "hard_polar_geometry"
    ]
    per_batch = geometry["per_batch"]
    d4 = per_batch["d4"]
    aggregate = geometry["aggregate"]
    if corruption == "available_truthy_string":
        geometry["available"] = "yes"
    elif corruption == "missing_per_batch":
        geometry.pop("per_batch")
    elif corruption == "extra_top_level_field":
        geometry["claim"] = True
    elif corruption == "missing_family":
        per_batch.pop("mixed_cycle")
    elif corruption == "wrong_examples":
        d4["examples"] += 1
    elif corruption == "float_operator_count":
        d4["operators_per_example"] = 2.0
    elif corruption == "missing_family_summary":
        d4.pop("spectral_orthogonality_defect")
    elif corruption == "wrong_family_summary_count":
        d4["absolute_determinant"]["count"] -= 1
    elif corruption == "incomplete_family_summary":
        d4["frobenius_orthogonality_defect"]["finite_count"] -= 1
    elif corruption == "negative_family_statistic":
        d4["absolute_determinant_magnitude_defect"]["minimum"] = -1.0
    elif corruption == "relative_singular_value_above_one":
        d4["postpolar_relative_minimum_singular_value"]["maximum"] = 1.01
    elif corruption == "determinant_component_mismatch":
        d4["determinant_components"]["positive"] -= 1
    elif corruption == "nonintegral_raw_below_fraction":
        d4["raw_below_relative_singular_floor_fraction"] = 0.1
    elif corruption == "uncovered_nonfinite_raw_value":
        d4["raw_relative_minimum_singular_value"]["finite_count"] -= 1
    elif corruption == "wrong_threshold":
        geometry["thresholds"]["orthogonality_tolerance"] = 1e-4
    elif corruption == "wrong_family_switched_fingerprint":
        geometry["switched_sanity"]["c8"]["bank"]["fingerprint"] = geometry[
            "switched_sanity"
        ]["d4"]["bank"]["fingerprint"]
    elif corruption == "wrong_aggregate_matrix_count":
        aggregate["operator_matrix_count"] -= 1
    elif corruption == "truthy_aggregate_all_finite":
        aggregate["all_finite"] = "yes"
    elif corruption == "aggregate_maximum_mismatch":
        aggregate["maximum_frobenius_orthogonality_defect"] = 1e-8
    elif corruption == "aggregate_pooled_summary_mismatch":
        for key in ("minimum", "p10", "median", "mean", "p90", "maximum"):
            d4["absolute_determinant"][key] = 0.5
    elif corruption == "aggregate_component_mismatch":
        aggregate["determinant_components"]["positive"] -= 1
        aggregate["determinant_components"]["negative"] += 1
    elif corruption == "aggregate_raw_below_mismatch":
        aggregate["raw_below_relative_singular_floor_fraction"] = (
            1.0 / aggregate["operator_matrix_count"]
        )
    elif corruption == "aggregate_switched_fraction_mismatch":
        aggregate["switched_defined_fraction"] = 0.5
    elif corruption == "aggregate_switched_log_maximum_mismatch":
        aggregate["maximum_absolute_switched_log_gain"] = 1e-4
    elif corruption == "hard_isometry_flag_lies":
        geometry["hard_isometry_pass"] = False
    elif corruption == "switched_sanity_flag_lies":
        geometry["projective_switched_gain_sanity_pass"] = False
    else:
        geometry["raw_prepolar_well_conditioned_pass"] = False

    assert _assay_contract_status(inputs, "A22_hard_polar_result_contract") == "FAIL"
