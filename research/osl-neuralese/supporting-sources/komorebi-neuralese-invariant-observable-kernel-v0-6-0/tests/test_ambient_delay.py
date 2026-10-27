from __future__ import annotations

import copy
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.ambient_delay import (
    AMBIENT_DIMENSION,
    DELAY,
    SEMANTIC_DIMENSION,
    STATE_DIMENSION,
    canonical_anc4_oracle,
    certify_anc4_minimality,
    controllability_matrix,
    delay_hankel,
    deterministic_change_of_basis,
    deterministic_self_check,
    evaluate_q_deletion,
    evaluate_q_transplant,
    observability_matrix,
)


def _histories() -> torch.Tensor:
    return torch.tensor(
        (
            (0.25, -0.50, 0.75, -1.00),
            (1.25, 0.50, -0.25, 0.875),
            (-0.375, 1.50, 0.625, -0.125),
            (0.90, -1.10, 1.30, -1.50),
        ),
        dtype=torch.float64,
    )


def test_exact_eight_plus_four_oracle_and_online_delay_four() -> None:
    oracle = canonical_anc4_oracle()
    assert oracle.semantic_injection.shape == (STATE_DIMENSION, SEMANTIC_DIMENSION)
    assert oracle.memory_injection.shape == (STATE_DIMENSION, AMBIENT_DIMENSION)
    assert STATE_DIMENSION == 12
    assert DELAY == AMBIENT_DIMENSION == 4

    identity = torch.eye(STATE_DIMENSION, dtype=torch.float64)
    zero = torch.zeros_like(identity)
    assert torch.equal(oracle.p_projector + oracle.q_projector, identity)
    assert torch.equal(oracle.p_projector @ oracle.q_projector, zero)
    assert torch.equal(oracle.q_projector @ oracle.p_projector, zero)

    state = oracle.encode(2, torch.zeros(AMBIENT_DIMENSION, dtype=torch.float64))
    inputs = torch.tensor((0.2, -0.4, 0.6, -0.8, 1.0, -1.2), dtype=torch.float64)
    observed: list[float] = []
    for value in inputs:
        observed.append(float(oracle.delay_output(state)))
        state = oracle.advance(state, 2, value)
        assert torch.equal(
            oracle.semantic_coordinates(state),
            torch.nn.functional.one_hot(torch.tensor(2), SEMANTIC_DIMENSION).to(torch.float64),
        )
    assert observed == pytest.approx((0.0, 0.0, 0.0, 0.0, 0.2, -0.4))
    assert torch.equal(
        oracle.future_delay_outputs(state, steps=8),
        torch.tensor(
            (0.6, -0.8, 1.0, -1.2, 0.0, 0.0, 0.0, 0.0),
            dtype=torch.float64,
        ),
    )


def test_hankel_observability_and_minimality_certificates_are_rank_four() -> None:
    oracle = canonical_anc4_oracle()
    controllability = controllability_matrix(
        oracle.memory_transition,
        oracle.memory_input,
        DELAY,
    )
    observability = observability_matrix(
        oracle.memory_transition,
        oracle.memory_output,
        DELAY,
    )
    hankel = delay_hankel(
        oracle.memory_transition,
        oracle.memory_input,
        oracle.memory_output,
    )
    reversal = torch.flip(torch.eye(DELAY, dtype=torch.float64), dims=(1,))
    assert torch.equal(hankel, reversal)
    assert int(torch.linalg.matrix_rank(controllability)) == 4
    assert int(torch.linalg.matrix_rank(observability)) == 4
    assert int(torch.linalg.matrix_rank(hankel)) == 4

    certificate = certify_anc4_minimality(oracle)
    assert certificate.semantic_projection.rank == 8
    assert certificate.vertical_fiber_dimension == 4
    assert certificate.controllability.rank == 4
    assert certificate.observability.rank == 4
    assert certificate.hankel.rank == 4
    assert certificate.hankel_reversal_max_error == 0.0
    assert certificate.transition_nilpotency_max_error == 0.0
    assert certificate.strict_delay_markov_max_error == 0.0
    assert certificate.memory_realization_minimal
    assert certificate.conditional_state_lower_bound == 12
    assumptions = " ".join(certificate.assumptions).lower()
    assert "sole temporal information channel" in assumptions
    assert "fixed surjective linear map" in assumptions
    assert "inputs before the four-lag window are fixed" in assumptions


def test_coordinate_conjugation_transports_the_oblique_split_and_behavior() -> None:
    canonical = canonical_anc4_oracle()
    transform = deterministic_change_of_basis(1701)
    assert bool(transform[:SEMANTIC_DIMENSION, SEMANTIC_DIMENSION:].abs().max() > 0.0)
    assert bool(transform[SEMANTIC_DIMENSION:, :SEMANTIC_DIMENSION].abs().max() > 0.0)
    transported = canonical.conjugate(transform)
    inverse = torch.linalg.inv(transform)
    tolerance = 2e-14

    assert torch.allclose(
        transported.p_projector,
        transform @ canonical.p_projector @ inverse,
        atol=tolerance,
        rtol=tolerance,
    )
    assert torch.allclose(
        transported.q_projector,
        transform @ canonical.q_projector @ inverse,
        atol=tolerance,
        rtol=tolerance,
    )
    assert torch.allclose(
        transported.p_projector @ transported.p_projector,
        transported.p_projector,
        atol=tolerance,
        rtol=tolerance,
    )
    # The deterministic map mixes Q into P, so this splitting is not a claim
    # about the last four displayed coordinates.
    assert not torch.allclose(
        transported.p_projector,
        transported.p_projector.transpose(0, 1),
    )
    assert bool(
        transported.semantic_injection[SEMANTIC_DIMENSION:].abs().max() > 0.0
    )
    assert bool(
        transported.memory_injection[:SEMANTIC_DIMENSION].abs().max() > 0.0
    )

    histories = _histories()
    labels = torch.tensor((0, 3, 5, 7))
    canonical_states = canonical.encode(labels, histories)
    transported_states = transported.encode(labels, histories)
    assert torch.allclose(
        transported_states,
        canonical_states @ transform.transpose(0, 1),
        atol=tolerance,
        rtol=tolerance,
    )
    assert torch.allclose(
        canonical.future_delay_outputs(canonical_states),
        transported.future_delay_outputs(transported_states),
        atol=tolerance,
        rtol=tolerance,
    )
    transported_certificate = certify_anc4_minimality(transported)
    assert transported_certificate.memory_realization_minimal
    assert transported_certificate.conditional_state_lower_bound == 12


def test_semantic_rank_certificate_uses_registered_right_inverse_under_bad_scaling() -> None:
    canonical = canonical_anc4_oracle()
    transform = torch.eye(STATE_DIMENSION, dtype=torch.float64)
    transform[0, 0] = float(2**40)
    transported = canonical.conjugate(transform)
    certificate = certify_anc4_minimality(transported)
    assert certificate.semantic_projection.rank == SEMANTIC_DIMENSION
    assert certificate.semantic_projection.method == "validated_right_inverse"
    assert certificate.semantic_projection.witness_residual == 0.0
    assert certificate.semantic_projection.singular_values[-1] < 1e-10
    assert certificate.conditional_state_lower_bound == STATE_DIMENSION


@pytest.mark.parametrize("conjugated", (False, True))
def test_q_deletion_removes_delay_packet_but_preserves_semantics(conjugated: bool) -> None:
    oracle = canonical_anc4_oracle()
    if conjugated:
        oracle = oracle.conjugate(deterministic_change_of_basis(29))
    histories = _histories()
    labels = torch.tensor((0, 3, 5, 7))
    result = evaluate_q_deletion(oracle, histories, labels)
    assert torch.allclose(result.native_outputs, histories, atol=1e-13, rtol=1e-13)
    assert torch.allclose(result.deleted_outputs, torch.zeros_like(histories), atol=1e-13)
    assert result.examples == 4
    assert result.nonzero_examples == 4
    assert result.native_match_fraction == 1.0
    assert result.deleted_zero_fraction == 1.0
    assert result.changed_fraction == 1.0
    assert result.changed_fraction_on_nonzero == 1.0
    assert result.semantic_preserved_fraction == 1.0
    assert result.maximum_native_error <= 1e-13
    assert result.maximum_deleted_magnitude <= 1e-13


def test_q_deletion_change_rate_is_conditioned_on_nonzero_histories() -> None:
    oracle = canonical_anc4_oracle()
    histories = _histories()
    histories[0] = 0.0
    labels = torch.tensor((0, 3, 5, 7))
    result = evaluate_q_deletion(oracle, histories, labels)
    assert result.examples == 4
    assert result.nonzero_examples == 3
    assert result.changed_fraction == 1.0
    assert result.unconditional_changed_fraction == pytest.approx(0.75)
    assert result.changed_fraction_on_nonzero == 1.0


@pytest.mark.parametrize("conjugated", (False, True))
def test_q_transplant_transplants_four_future_outputs_only(conjugated: bool) -> None:
    oracle = canonical_anc4_oracle()
    if conjugated:
        oracle = oracle.conjugate(deterministic_change_of_basis(31))
    recipients = _histories()
    donors = recipients.roll(shifts=1, dims=0)
    labels = torch.tensor((1, 1, 1, 1))
    result = evaluate_q_transplant(oracle, recipients, donors, labels)
    assert torch.allclose(result.recipient_outputs, recipients, atol=1e-13, rtol=1e-13)
    assert torch.allclose(result.donor_outputs, donors, atol=1e-13, rtol=1e-13)
    assert torch.allclose(result.transplanted_outputs, donors, atol=1e-13, rtol=1e-13)
    assert result.examples == result.distinct_examples == 4
    assert result.donor_match_fraction == 1.0
    assert result.recipient_changed_fraction_on_distinct == 1.0
    assert result.semantic_recipient_preserved_fraction == 1.0
    assert result.maximum_donor_error <= 1e-13


def test_counterfactual_evaluators_fail_closed_on_malformed_inputs() -> None:
    oracle = canonical_anc4_oracle()
    histories = _histories()
    labels = torch.tensor((0, 3, 5, 7))
    with pytest.raises(ValueError, match="shape"):
        evaluate_q_deletion(oracle, histories[:, :3], labels)
    with pytest.raises(TypeError, match="floating"):
        evaluate_q_deletion(oracle, histories.to(torch.long), labels)
    with pytest.raises(ValueError, match="one label"):
        evaluate_q_deletion(oracle, histories, labels[:3])
    with pytest.raises(ValueError, match="same shape"):
        oracle.transplant_q(
            oracle.encode(labels, histories),
            oracle.encode(labels[:3], histories[:3]),
        )
    with pytest.raises(ValueError, match="positive"):
        evaluate_q_transplant(oracle, histories, histories, labels, tolerance=0.0)
    singular = torch.eye(STATE_DIMENSION, dtype=torch.float64)
    singular[-1] = 0.0
    with pytest.raises((ValueError, torch.linalg.LinAlgError)):
        oracle.conjugate(singular)


def test_oracle_rejects_internally_inconsistent_split_and_dynamics() -> None:
    oracle = canonical_anc4_oracle()
    wrong_p = oracle.p_projector.clone()
    wrong_p[0, 0] = 0.5
    with pytest.raises(
        ValueError,
        match="projector resolution|P idempotence|P split definition",
    ):
        replace(oracle, p_projector=wrong_p)

    wrong_transition = oracle.state_transition.clone()
    wrong_transition[0, 0] = 0.25
    with pytest.raises(ValueError, match="full-state transition definition"):
        replace(oracle, state_transition=wrong_transition)

    sub_tolerance_transition = oracle.state_transition.clone()
    sub_tolerance_transition[-1, SEMANTIC_DIMENSION] = 1e-12
    with pytest.raises(ValueError, match="exact full-state transition definition"):
        replace(oracle, state_transition=sub_tolerance_transition)

    wrong_shift = oracle.memory_transition.clone()
    wrong_shift[0, 0] = 0.25
    tied_full_transition = (
        oracle.memory_injection @ wrong_shift @ oracle.memory_projection
    )
    with pytest.raises(ValueError, match="delay-four shift"):
        replace(
            oracle,
            memory_transition=wrong_shift,
            state_transition=tied_full_transition,
        )



def test_cyclic_echo_that_matches_hankel_block_is_rejected() -> None:
    oracle = canonical_anc4_oracle()
    cyclic_shift = oracle.memory_transition.clone()
    cyclic_shift[-1, 0] = 0.25
    reversal = torch.flip(torch.eye(DELAY, dtype=torch.float64), dims=(1,))
    assert torch.equal(
        delay_hankel(cyclic_shift, oracle.memory_input, oracle.memory_output),
        reversal,
    )
    assert float(torch.linalg.matrix_power(cyclic_shift, DELAY).abs().max()) == 0.25
    tied_transition = (
        oracle.memory_injection @ cyclic_shift @ oracle.memory_projection
    )
    with pytest.raises(ValueError, match="exact delay-four shift"):
        replace(
            oracle,
            memory_transition=cyclic_shift,
            state_transition=tied_transition,
        )


@pytest.mark.parametrize("dtype", (torch.float16, torch.bfloat16))
def test_low_precision_is_bounded_audited_and_not_vacuous(dtype: torch.dtype) -> None:
    canonical = canonical_anc4_oracle(dtype=dtype)
    transported = canonical.conjugate(
        deterministic_change_of_basis(1701, dtype=dtype)
    )
    certificate = certify_anc4_minimality(transported)
    assert certificate.memory_realization_minimal
    assert certificate.semantic_projection.rank == SEMANTIC_DIMENSION

    histories = _histories()
    labels = torch.tensor((0, 3, 5, 7))
    deletion = evaluate_q_deletion(transported, histories, labels)
    assert deletion.native_match_fraction == 1.0
    assert deletion.changed_fraction == 1.0
    assert deletion.semantic_preserved_fraction == 1.0

    zero = torch.zeros_like(canonical.coordinate_map)
    with pytest.raises(ValueError, match="numerically resolvable"):
        replace(
            canonical,
            coordinate_map=zero,
            inverse_coordinate_map=zero,
        )


@pytest.mark.parametrize("dtype", (torch.float16, torch.bfloat16, torch.float32))
@pytest.mark.parametrize("scale", (2.0**-10, 1.0, 2.0**10))
def test_default_evaluator_tolerance_scales_with_packet_magnitude(
    dtype: torch.dtype,
    scale: float,
) -> None:
    oracle = canonical_anc4_oracle(dtype=dtype).conjugate(
        deterministic_change_of_basis(59, dtype=dtype)
    )
    histories = _histories() * scale
    labels = torch.tensor((0, 3, 5, 7))
    deletion = evaluate_q_deletion(oracle, histories, labels)
    assert deletion.native_match_fraction == 1.0
    assert deletion.deleted_zero_fraction == 1.0
    assert deletion.semantic_preserved_fraction == 1.0

    donors = histories.roll(shifts=1, dims=0)
    transplant = evaluate_q_transplant(oracle, histories, donors, labels)
    assert transplant.donor_match_fraction == 1.0
    assert transplant.semantic_recipient_preserved_fraction == 1.0


def test_in_place_tensor_mutation_is_revalidated_before_use() -> None:
    oracle = canonical_anc4_oracle()
    state = oracle.encode(0, torch.zeros(AMBIENT_DIMENSION, dtype=torch.float64))
    oracle.state_transition[-1, SEMANTIC_DIMENSION] = 1e-12
    with pytest.raises(ValueError, match="exact full-state transition definition"):
        oracle.future_delay_outputs(state)

    oracle = canonical_anc4_oracle()
    oracle.memory_transition[-1, 0] = 0.25
    with pytest.raises(ValueError, match="exact delay-four shift"):
        certify_anc4_minimality(oracle)


def test_self_check_is_deterministic_json_safe_and_complete() -> None:
    first = deterministic_self_check(1701)
    second = deterministic_self_check(1701)
    assert first == second
    json.dumps(first, allow_nan=False)
    assert first["dimensions"] == {
        "semantic": 8,
        "vertical_fiber": 4,
        "state": 12,
        "delay": 4,
    }
    assert first["minimality"]["memory_realization_minimal"] is True
    assert first["status"] == "PASS"
    assert first["minimality"]["conditional_state_lower_bound"] == 12
    assert first["canonical_q_deletion"]["changed_fraction"] == 1.0
    assert first["transported_q_deletion"]["changed_fraction"] == 1.0
    assert first["canonical_q_transplant"]["donor_match_fraction"] == 1.0
    assert first["transported_q_transplant"]["donor_match_fraction"] == 1.0
    assert max(first["coordinate_conjugacy_max_residuals"].values()) < 1e-13
    assert first["native_output_coordinate_max_error"] < 1e-13
    assert first["transplant_output_coordinate_max_error"] < 1e-13
    receipt = first["receipt_sha256"]
    unsigned = copy.deepcopy(first)
    del unsigned["receipt_sha256"]
    encoded = json.dumps(
        unsigned,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert receipt == hashlib.sha256(encoded).hexdigest()

    different_seed = deterministic_self_check(1702)
    assert different_seed["receipt_sha256"] != first["receipt_sha256"]
