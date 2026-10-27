import torch

from komorebi_neuralese.flatness_eval import (
    NATIVE_MARGIN_TAU,
    ExactCompiledPolarRNN,
    FlatnessAuditConfig,
    _path_geometry,
    build_flatness_audit_bank,
    evaluate_control_suite,
    native_decision,
    suffix_visible_holonomy_fixture,
)


def small_bank():
    return build_flatness_audit_bank(
        FlatnessAuditConfig(
            seed=123,
            diamonds_per_length=4,
            loops_per_stratum=2,
            diamond_lengths=(8,),
            diamond_suffix_lengths=(4,),
            loop_repeats=(1, 2),
            loop_suffix_lengths=(0, 4),
        )
    )


def test_audit_bank_is_long_derived_and_matched():
    bank = small_bank()
    assert all(len(case.left) >= 8 and len(case.right) >= 8 for case in bank.diamonds)
    assert all(case.left_rewrite_count >= 3 for case in bank.diamonds)
    assert all(case.right_rewrite_count >= 3 for case in bank.diamonds)
    assert all(case.left_signature == case.right_signature for case in bank.diamonds)
    assert all(case.left_signature != case.right_signature for case in bank.inequivalent)
    assert all(
        len(case.left) == len(case.right)
        and sum(case.left) == sum(case.right)
        for case in bank.inequivalent
    )


def test_native_membership_is_subset_of_native_correctness_and_boundary_fails():
    logits = torch.zeros(3, 8, dtype=torch.float32)
    logits[0, 0] = 1.0
    logits[1, 0] = 1.0
    logits[1, 1] = 1.0
    logits[2, 1] = 1.0
    target = torch.tensor([0, 0, 0], dtype=torch.long)
    result = native_decision(logits, target)
    assert result.robust_correct <= result.ordinary_correct
    assert result.ordinary_correct == 2
    assert result.robust_correct == 1
    assert result.boundary >= 1


def test_tau_equality_is_not_promoted_to_membership():
    # Derive the threshold from the exact stored-logit margin so the test hits
    # equality rather than relying on a rounded decimal fixture.
    logits = torch.zeros(1, 8, dtype=torch.float32)
    logits[0, 0] = torch.tensor(NATIVE_MARGIN_TAU, dtype=torch.float32)
    target = torch.tensor([0], dtype=torch.long)
    measured = native_decision(logits, target).margins[0]
    result = native_decision(logits, target, tau=measured)
    assert result.ordinary_correct == 1
    assert result.robust_correct == 0
    assert result.boundary == 1


def test_calibration_controls_all_pass():
    torch.set_num_threads(1)
    result = evaluate_control_suite(small_bank(), deep_examples=16)
    assert result["assay_valid"]
    assert all(result["gates"].values())
    curved = result["results"]["quotient_curved"]["diamonds"]
    assert curved["joint_correct_rate"] == 1.0
    assert curved["packet_quotient_defect"]["maximum"] <= 1e-6
    assert curved["full_holonomy_defect"]["median"] >= 0.02


def test_future_probe_detects_endpoint_invisible_residue():
    fixture = suffix_visible_holonomy_fixture()
    assert fixture["immediate_agreement"]
    assert fixture["immediate_joint_correct"] == 1.0
    assert fixture["future_disagreement"]
    assert fixture["future_joint_correct"] == 0.0
    assert fixture["signatures_defined"]
    assert fixture["future_probe_defect"] > 0.01
    assert fixture["pipeline"]["future"]["total"] == 1
    assert fixture["pipeline"]["future"]["packet_quotient_defect"][
        "finite_count"
    ] == 1
    assert fixture["pass"]


def test_path_geometry_is_computed_entirely_in_float64():
    model = ExactCompiledPolarRNN()
    tables = torch.stack(
        (torch.eye(8), torch.eye(8)), dim=0
    ).unsqueeze(0).to(torch.float32)
    codes = model.encode_operator_bundle(tables).matrices
    slots = torch.tensor([[0]], dtype=torch.long)
    empty = torch.empty((1, 0), dtype=torch.long)
    geometry = _path_geometry(model, codes, slots, empty, slots)
    assert all(value.dtype == torch.float64 for value in geometry)
    assert all(torch.isfinite(value).all() for value in geometry)
