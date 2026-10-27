from __future__ import annotations

import math

import pytest
import torch

from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.invariant_kernel_eval import (
    AssayIntegrityError,
    DEFAULT_SUFFIX_LENGTHS,
    adversarial_assay_controls,
    audit_centered_quotient_paths,
    audit_centered_quotient_structure,
    audit_centered_quotient_suffixes,
    audit_kernel_structure,
    build_suffix_word_bank,
    centered_decoder,
    centered_null_intervention_audit,
    extract_model_geometry,
    fiber_intervention_audit,
    gauge_covariance_audit,
    path_defect_audit,
    path_defect_from_products,
    path_products,
    semantic_transplant_audit,
    suffix_leakage_audit,
)
from komorebi_neuralese.invariant_kernel_models import (
    ExactInvariantKernelOperatorRNN,
    QuotientCurvedInvariantKernelOperatorRNN,
)


# The sealed numerical contract uses one CPU thread.  Tiny batched SVDs are
# also dramatically slower under large default BLAS thread pools.
torch.set_num_threads(1)


def _words(seed: int = 101, samples: int = 2) -> dict[int, torch.Tensor]:
    return build_suffix_word_bank(
        operator_count=2,
        samples_per_length=samples,
        seed=seed,
        lengths=DEFAULT_SUFFIX_LENGTHS,
    )


def _exact_fixture(contexts: int = 6):
    model = ExactInvariantKernelOperatorRNN(gauge_seed=103)
    batch = EpisodeGenerator(107).sample(contexts, 0, family="d4")
    codes = model.encode_operators(batch.tables)
    return model, batch, codes


def test_centered_decoder_promotes_before_rank_sensitive_work() -> None:
    decoder = torch.zeros(8, 12, dtype=torch.float32)
    decoder[:, :7] = torch.eye(8, dtype=torch.float32)[:, :7]
    decoder[:, 7] = 19.0
    centered = centered_decoder(decoder)
    assert centered.dtype == torch.float64
    assert torch.linalg.matrix_rank(centered) == 7
    assert float(centered[:, 7].abs().max()) < 1e-12


def test_hard_control_structure_is_exactly_rank_7_plus_1_plus_4() -> None:
    model, _, codes = _exact_fixture()
    result = audit_kernel_structure(
        model.P_S,
        model.P_L,
        model.P_K,
        model.effective_decoder_weight(),
        codes,
    )
    assert result.passed, result.to_dict()
    assert result.behavioral_rank == 7
    assert result.common_rank == 1
    assert result.ambient_rank == 4
    assert result.centered_null_rank == 5
    assert result.centered_decoder_rank == 7
    assert result.behavioral_to_null_leakage < 5e-6
    assert result.null_to_behavioral_leakage < 5e-6


def test_suffix_grid_gates_sigma7_sigma8_and_both_leakage_directions() -> None:
    model, _, codes = _exact_fixture()
    result = suffix_leakage_audit(
        model.P_S,
        model.P_L,
        model.P_K,
        model.effective_decoder_weight(),
        codes,
        _words(),
    )
    assert result.passed, result.to_dict()
    assert tuple(level.length for level in result.levels) == DEFAULT_SUFFIX_LENGTHS
    assert result.observer_rank == 7
    assert result.sigma_behavioral_relative > 0.5
    assert result.sigma_first_null_relative < 5e-6
    assert result.maximum_behavioral_to_null < 5e-6
    assert result.maximum_null_to_behavioral < 5e-6


def test_path_products_use_recurrent_left_action_order_and_float64() -> None:
    first = torch.tensor([[1.0, 1.0], [0.0, 1.0]])
    second = torch.tensor([[1.0, 0.0], [1.0, 1.0]])
    codes = torch.stack((first, second))
    words = torch.tensor([[0, 1]], dtype=torch.long)
    result = path_products(codes, words)
    assert result.dtype == torch.float64
    assert torch.equal(result[0, 0], second.double() @ first.double())


def test_vertical_curved_hard_control_passes_quotient_and_fails_full_flatness() -> None:
    model = QuotientCurvedInvariantKernelOperatorRNN(gauge_seed=109)
    batch = EpisodeGenerator(113).sample(
        12, 2, family="d4", canonical_word=(1, 1)
    )
    codes = model.encode_operators(batch.tables)
    empty_paths = torch.empty((12, 1, 0), dtype=torch.long)
    relation_paths = batch.op_slots[:, None, :]
    result = path_defect_audit(
        model.P_S,
        model.P_L,
        model.P_K,
        codes,
        empty_paths,
        relation_paths,
    )
    assert result.quotient_flat
    assert result.common_flat
    assert not result.vertical_flat
    assert not result.full_flat
    assert result.vertical_curvature_only
    assert result.maximum_vertical_defect > 0.1


def test_horizontal_and_vertical_curvature_are_not_conflated() -> None:
    identity = torch.eye(12, dtype=torch.float64)
    s = torch.diag(torch.tensor([1.0] * 7 + [0.0] * 5))
    line = torch.diag(torch.tensor([0.0] * 7 + [1.0] + [0.0] * 4))
    fiber = identity - s - line
    angle = torch.tensor(0.4)
    horizontal = identity.clone()
    horizontal[:2, :2] = torch.tensor(
        [[torch.cos(angle), -torch.sin(angle)], [torch.sin(angle), torch.cos(angle)]]
    )
    vertical = identity.clone()
    vertical[8:10, 8:10] = horizontal[:2, :2]
    horizontal_result = path_defect_from_products(
        s, line, fiber, identity, horizontal
    )
    vertical_result = path_defect_from_products(s, line, fiber, identity, vertical)
    assert not horizontal_result.quotient_flat
    assert horizontal_result.maximum_quotient_defect > 0.1
    assert vertical_result.quotient_flat
    assert vertical_result.vertical_curvature_only


def test_nonzero_ambient_and_common_interventions_remain_invisible() -> None:
    model = QuotientCurvedInvariantKernelOperatorRNN(gauge_seed=127)
    batch = EpisodeGenerator(131).sample(7, 0, family="d4")
    codes = model.encode_operators(batch.tables)
    result = fiber_intervention_audit(
        model.P_S,
        model.P_L,
        model.P_K,
        model.effective_decoder_weight(),
        codes,
        _words(137),
    )
    assert result.passed, result.to_dict()
    assert result.ambient_probe_dimension == 4
    assert result.common_probe_dimension == 1
    assert result.minimum_ambient_probe_norm > 0.99
    assert result.minimum_ambient_transplant_distance > 1.99
    assert result.maximum_ambient_injection_effect < 5e-6
    assert result.maximum_common_injection_effect < 5e-6
    assert not result.memory_claim_eligible
    assert "not_learned_memory" in result.evidence_scope


def test_semantic_transplant_uses_only_exact_nontrivial_eligible_pairs() -> None:
    model = ExactInvariantKernelOperatorRNN(gauge_seed=139)
    state_ids = torch.arange(8, dtype=torch.long)
    donor_ids = state_ids.roll(1)
    recipients = model.initial_hidden(state_ids)
    donors = model.initial_hidden(donor_ids)
    identity = torch.eye(12).expand(8, -1, -1)
    result = semantic_transplant_audit(
        model.P_S,
        model.P_L,
        model.P_K,
        model.effective_decoder_weight(),
        identity,
        recipients,
        donors,
        state_ids,
        donor_ids,
        targets_are_exact=True,
    )
    assert result.eligible_pairs == 8
    assert result.successful_pairs == 8
    assert result.success_rate == 1.0
    assert result.minimum_eligible_semantic_displacement > 1.0
    assert result.minimum_success_margin is not None
    assert result.minimum_success_margin > 0.9


def test_semantic_transplant_fails_without_exact_targets_or_eligible_pairs() -> None:
    model = ExactInvariantKernelOperatorRNN(gauge_seed=149)
    ids = torch.arange(8, dtype=torch.long)
    states = model.initial_hidden(ids)
    identity = torch.eye(12).expand(8, -1, -1)
    args = (
        model.P_S,
        model.P_L,
        model.P_K,
        model.effective_decoder_weight(),
        identity,
        states,
        states,
        ids,
        ids,
    )
    with pytest.raises(AssayIntegrityError, match="exact ground-truth"):
        semantic_transplant_audit(*args, targets_are_exact=False)
    with pytest.raises(AssayIntegrityError, match="no exactly eligible"):
        semantic_transplant_audit(*args, targets_are_exact=True)


def test_orthogonal_gauge_conjugation_preserves_every_metric() -> None:
    model, _, codes = _exact_fixture(contexts=4)
    generator = torch.Generator().manual_seed(151)
    gauge, _ = torch.linalg.qr(torch.randn(12, 12, generator=generator, dtype=torch.float64))
    same = torch.zeros((3, 2), dtype=torch.long)
    result = gauge_covariance_audit(
        model.P_S,
        model.P_L,
        model.P_K,
        model.effective_decoder_weight(),
        codes,
        _words(157),
        same,
        same,
        gauge,
    )
    assert result.passed, result.to_dict()
    assert result.rank_preserved
    assert result.centered_continuation_operator_delta < 2e-10


def test_geometry_extractor_registers_hard_split_and_two_way_audits_agree() -> None:
    model, batch, _ = _exact_fixture(contexts=5)
    words = _words(163)
    geometry = extract_model_geometry(model, batch.tables, words)
    assert geometry.source == "registered_three_way_7_plus_1_plus_4"
    assert geometry.three_way_registered
    assert geometry.common_projector is not None
    assert geometry.ambient_projector is not None
    assert geometry.extraction_valid, geometry.receipt()
    structure = audit_centered_quotient_structure(
        geometry.behavioral_projector,
        geometry.centered_null_projector,
        geometry.decoder_weight,
        geometry.operator_codes,
    )
    suffix = audit_centered_quotient_suffixes(
        geometry.behavioral_projector,
        geometry.centered_null_projector,
        geometry.decoder_weight,
        geometry.operator_codes,
        words,
    )
    null = centered_null_intervention_audit(
        geometry.behavioral_projector,
        geometry.centered_null_projector,
        geometry.decoder_weight,
        geometry.operator_codes,
        words,
    )
    assert structure.passed
    assert suffix.passed
    assert null.passed
    assert not null.memory_claim_eligible


def test_plain_full_rank_observer_is_recorded_as_invalid_not_cut_into_fibers() -> None:
    class FullRankLeakyModel:
        def __init__(self) -> None:
            self.decoder = type("Decoder", (), {})()
            decoder = torch.zeros(8, 12)
            decoder[:, :7] = (
                torch.eye(8) - torch.ones(8, 8) / 8.0
            )[:, :7]
            self.decoder.weight = decoder

        def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
            identity = torch.eye(12, device=tables.device, dtype=tables.dtype)
            shift = torch.roll(identity, shifts=1, dims=0)
            codes = torch.stack((shift, shift.T))
            return codes.unsqueeze(0).expand(tables.shape[0], -1, -1, -1)

    tables = torch.zeros(3, 2, 8, 8)
    geometry = extract_model_geometry(FullRankLeakyModel(), tables, _words(167))
    assert geometry.source == "preregistered_suffix_observer_top7_svd"
    assert not geometry.three_way_registered
    assert geometry.common_projector is None
    assert geometry.ambient_projector is None
    assert geometry.observer_rank == 12
    assert not geometry.extraction_valid
    assert "observer_rank" in str(geometry.failure_reason)
    assert "sigma8_not_negligible" in str(geometry.failure_reason)


def test_two_way_path_audit_does_not_label_untyped_null_as_ambient() -> None:
    model, _, codes = _exact_fixture(contexts=3)
    left = torch.zeros((3, 2, 4), dtype=torch.long)
    right = left.clone()
    result = audit_centered_quotient_paths(
        model.P_S, model.P_centered_null, codes, left, right
    )
    assert result.quotient_flat
    assert result.null_flat
    assert result.full_flat
    assert not hasattr(result, "vertical_curvature_only")


def test_missing_nonfinite_ambiguous_and_malformed_inputs_fail_closed() -> None:
    model, _, codes = _exact_fixture(contexts=2)
    words = _words(173)
    missing = dict(words)
    missing.pop(32)
    with pytest.raises(AssayIntegrityError, match="exactly the required lengths"):
        suffix_leakage_audit(
            model.P_S,
            model.P_L,
            model.P_K,
            model.effective_decoder_weight(),
            codes,
            missing,
        )
    nonfinite = codes.clone()
    nonfinite[0, 0, 0, 0] = float("nan")
    with pytest.raises(AssayIntegrityError, match="non-finite"):
        audit_kernel_structure(
            model.P_S,
            model.P_L,
            model.P_K,
            model.effective_decoder_weight(),
            nonfinite,
        )
    ambiguous = model.P_S.double().clone()
    direction = torch.linalg.eigh(ambiguous).eigenvectors[:, 6]
    ambiguous = ambiguous - 0.5 * torch.outer(direction, direction)
    result = audit_kernel_structure(
        ambiguous,
        model.P_L,
        model.P_K,
        model.effective_decoder_weight(),
        codes,
    )
    assert result.rank_ambiguous
    assert not result.passed
    malformed = dict(words)
    malformed[8] = torch.zeros((2, 7), dtype=torch.long)
    with pytest.raises(AssayIntegrityError, match="invalid shape"):
        suffix_leakage_audit(
            model.P_S,
            model.P_L,
            model.P_K,
            model.effective_decoder_weight(),
            codes,
            malformed,
        )


def test_adversarial_controls_discriminate_rank_leakage_and_curvature() -> None:
    controls = adversarial_assay_controls()
    assert controls["assay_valid"], controls
    registered_names = {
        "exact_7_plus_1_plus_4",
        "quotient_curved_ambient",
        "common_logit_shift",
        "cross_block_leaky",
        "identity_collapse",
        "random_block_orthogonal",
        "global_coordinate_conjugate",
        "rank6_collapse",
        "rank8_intrusion",
        "full_rank_leaky",
    }
    assert set(controls["registered_control_names"]) == registered_names
    assert set(controls["registered_controls"]) == registered_names
    for name in registered_names:
        assert controls[name] == controls["registered_controls"][name]
        assert controls[name]["correctly_classified"], (name, controls[name])
        assert controls[name]["observed_classification"] == controls[name][
            "expected_classification"
        ]

    exact = controls["exact_7_plus_1_plus_4"]
    assert exact["structure"]["passed"]
    assert exact["suffix"]["passed"]
    assert exact["fiber_intervention"]["passed"]
    assert exact["semantic_oracle"]["passed"]

    curved = controls["quotient_curved_ambient"]
    assert curved["path"]["quotient_flat"]
    assert curved["path"]["common_flat"]
    assert curved["path"]["vertical_curvature_only"]
    assert curved["behavior_max_abs_logit_delta_vs_exact"] < 1e-10
    assert curved["behavior_accuracy"] == 1.0

    common = controls["common_logit_shift"]
    assert common["raw_shift_l2"] > 1.0
    assert common["common_uniformity_residual"] < 1e-12
    assert common["prediction_retention"] == 1.0

    cross = controls["cross_block_leaky"]
    assert not cross["structure"]["passed"]
    assert not cross["suffix_passed"]
    assert not cross["fiber_intervention_passed"]

    identity = controls["identity_collapse"]
    random = controls["random_block_orthogonal"]
    # These are genuine invariant block systems.  Their rejection must come
    # from failure to execute the registered action, not from a false geometry
    # claim introduced after seeing their behavior.
    assert identity["geometry_passed"]
    assert random["geometry_passed"]
    assert not identity["semantic_oracle"]["passed"]
    assert identity["semantic_oracle"]["prediction_change_rate_on_nonidentity"] == 0.0
    assert identity["rejection_basis"] == "semantic_sensitivity_oracle_not_geometry"
    assert not random["semantic_oracle"]["passed"]
    assert random["semantic_oracle"]["robust_accuracy"] < 0.5
    assert random["rejection_basis"] == "semantic_execution_oracle_not_geometry"

    coordinate = controls["global_coordinate_conjugate"]
    assert coordinate["gauge"]["passed"]
    assert coordinate["behavior_max_abs_logit_delta"] < 1e-10
    assert coordinate["prediction_retention"] == 1.0

    assert controls["rank6_collapse"]["structure"]["behavioral_rank"] == 6
    assert controls["rank8_intrusion"]["structure"]["behavioral_rank"] == 8
    assert controls["rank7"]["passed"]
    assert controls["rank7"]["centered_null_rank"] == 5
    assert controls["rank9"]["detected"]
    assert controls["ambiguous_projector"]["detected"]
    assert controls["full_rank_leaky"]["observer_rank"] == 12
    assert controls["full_rank_leaky"]["detected"]
    assert controls["horizontal_curved"]["detected"]
    assert controls["vertical_curved"]["detected_without_false_quotient_failure"]
    assert controls["gauge_covariance"]["passed"]
    assert not controls["compiled_hard_control"]["memory_claim_eligible"]


def test_configuration_numbers_must_be_finite_and_unambiguous() -> None:
    model, _, codes = _exact_fixture(contexts=2)
    for bad in (math.nan, math.inf, 0.0, -1.0, True):
        with pytest.raises(AssayIntegrityError):
            audit_kernel_structure(
                model.P_S,
                model.P_L,
                model.P_K,
                model.effective_decoder_weight(),
                codes,
                tolerance=bad,
            )
