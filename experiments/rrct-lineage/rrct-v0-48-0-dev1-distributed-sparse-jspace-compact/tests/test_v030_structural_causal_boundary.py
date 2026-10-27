import copy

import numpy as np
import pytest

import rrct.causal_boundary as boundary_module
from rrct.causal_boundary import CausalBoundaryConfig, OnlineCausalSelfBoundary


def _config(**changes):
    values = {
        "observation_dim": 6,
        "process_dim": 4,
        "source_count": 3,
        "handle_count": 2,
        "evidence_capacity": 160,
        "minimum_samples": 80,
        "fit_interval": 20,
        "commitment_block_size": 20,
        "ridge": 0.35,
        "null_permutations": 24,
        "half_null_permutations": 24,
        "null_quantile": 0.95,
        "higher_mode_null": "global_sharp_null",
        "revision_confirmations": 2,
        "revocation_confirmations": 3,
        "confidence_decay": 0.60,
        "seed": 3030,
    }
    values.update(changes)
    return CausalBoundaryConfig(**values)


def _fit(config, handle, source, rank, confidence=0.40):
    internal = np.zeros((config.process_dim, config.process_dim))
    sensory = np.zeros((config.observation_dim, config.observation_dim))
    effect = np.zeros((config.process_dim, config.observation_dim))
    internal[:rank, :rank] = np.eye(rank)
    sensory[:rank, :rank] = np.eye(rank)
    effect[:rank, :rank] = np.eye(rank)
    return boundary_module._FitResult(
        selected_handle_index=int(handle),
        selected_source_index=int(source),
        rank=int(rank),
        internal_projector=boundary_module._readonly(internal),
        sensory_projector=boundary_module._readonly(sensory),
        effect_operator=boundary_module._readonly(effect),
        confidence=float(confidence),
        ambiguous=False,
    )


def _acquire(model, fit):
    first = model._apply_fit(fit)
    model._candidate_last_evidence_count -= (
        model.config.structural_confirmation_interval
    )
    second = model._apply_fit(fit)
    assert first == (
        False,
        False,
        False,
        False,
        "acquisition_candidate",
        True,
        False,
    )
    assert second == (
        False,
        False,
        True,
        False,
        "acquisition",
        True,
        False,
    )
    assert model.state.active


def test_paired_mode_confidence_never_crosses_split_thresholds():
    value = boundary_module._paired_mode_confidence(
        1.10,
        0.25,
        0.25,
        1.00,
        0.20,
        0.20,
    )
    assert value == pytest.approx((1.10 - 1.00) / 1.10)
    assert value > 0.0
    assert boundary_module._paired_mode_confidence(
        1.00,
        0.25,
        0.25,
        1.00,
        0.20,
        0.20,
    ) == 0.0
    stronger = boundary_module._paired_mode_confidence(
        1.20,
        0.30,
        0.30,
        1.00,
        0.20,
        0.20,
    )
    assert stronger > value


def test_one_same_pair_rank_dropout_does_not_overwrite_structure():
    config = _config()
    model = OnlineCausalSelfBoundary(config)
    rank_two = _fit(config, 1, 2, 2, confidence=0.50)
    rank_one = _fit(config, 1, 2, 1, confidence=0.35)
    _acquire(model, rank_two)
    accepted = model.state

    result = model._apply_fit(rank_one)

    assert result == (
        False,
        False,
        False,
        False,
        "structural_candidate",
        True,
        False,
    )
    retained = model.state
    assert retained.structural_signature == accepted.structural_signature
    assert retained.epoch == accepted.epoch
    assert np.array_equal(retained.internal_projector, accepted.internal_projector)
    assert np.array_equal(retained.sensory_projector, accepted.sensory_projector)
    assert np.array_equal(retained.effect_operator, accepted.effect_operator)
    assert retained.confidence == pytest.approx(
        accepted.confidence * config.confidence_decay
    )
    snapshot = model.snapshot()
    assert snapshot["candidate_signature"] == (1, 2, 1)
    assert snapshot["candidate_streak"] == 1

    refresh = model._apply_fit(rank_two)
    assert refresh == (
        False,
        False,
        False,
        False,
        "parameter_refresh",
        False,
        False,
    )
    assert model.state.rank == 2
    assert model.state.epoch == accepted.epoch
    assert model.snapshot()["candidate_signature"] is None


def test_sustained_same_pair_rank_change_is_a_revision():
    config = _config()
    model = OnlineCausalSelfBoundary(config)
    rank_two = _fit(config, 0, 1, 2, confidence=0.55)
    rank_one = _fit(config, 0, 1, 1, confidence=0.45)
    _acquire(model, rank_two)
    prior_epoch = model.state.epoch

    first = model._apply_fit(rank_one)
    overlap = model._apply_fit(rank_one)
    assert overlap == (
        False,
        False,
        False,
        False,
        "structural_candidate",
        False,
        False,
    )
    assert model.snapshot()["candidate_streak"] == 1
    model._candidate_last_evidence_count -= (
        model.config.structural_confirmation_interval
    )
    second = model._apply_fit(rank_one)

    assert first[4] == "structural_candidate"
    assert second == (
        True,
        False,
        False,
        True,
        "rank_revision",
        True,
        False,
    )
    assert model.state.structural_signature == (True, 0, 1, 1)
    assert model.state.epoch == prior_epoch + 1
    assert model.state.age == 0
    assert model.snapshot()["candidate_signature"] is None


def test_rank_is_part_of_candidate_confirmation_and_snapshot_continuation():
    config = _config()
    model = OnlineCausalSelfBoundary(config)
    current = _fit(config, 0, 0, 2)
    pair_rank_one = _fit(config, 1, 2, 1)
    pair_rank_two = _fit(config, 1, 2, 2)
    _acquire(model, current)

    model._apply_fit(pair_rank_one)
    assert model.snapshot()["candidate_signature"] == (1, 2, 1)
    model._apply_fit(pair_rank_two)
    pending = model.snapshot()
    assert pending["candidate_signature"] == (1, 2, 2)
    assert pending["candidate_streak"] == 1
    assert model.state.structural_signature == (True, 0, 0, 2)

    restored = OnlineCausalSelfBoundary(config)
    restored.load_snapshot(copy.deepcopy(pending))
    assert restored.snapshot()["digest"] == pending["digest"]
    restored._candidate_last_evidence_count -= (
        restored.config.structural_confirmation_interval
    )
    result = restored._apply_fit(pair_rank_two)
    assert result == (
        True,
        False,
        False,
        False,
        "pair_revision",
        True,
        False,
    )
    assert restored.state.structural_signature == (True, 1, 2, 2)


def test_null_fit_clears_structural_candidate_before_revocation():
    config = _config(revocation_confirmations=2)
    model = OnlineCausalSelfBoundary(config)
    current = _fit(config, 0, 1, 2)
    candidate = _fit(config, 0, 1, 1)
    _acquire(model, current)
    model._apply_fit(candidate)

    first = model._apply_fit(boundary_module._null_fit(config))
    assert first == (
        False,
        False,
        False,
        False,
        "null_candidate",
        False,
        True,
    )
    assert model.snapshot()["candidate_signature"] is None
    assert model.state.active

    overlap = model._apply_fit(boundary_module._null_fit(config))
    assert overlap[-2:] == (False, False)
    assert model.state.active
    model._miss_last_evidence_count -= config.structural_confirmation_interval
    second = model._apply_fit(boundary_module._null_fit(config))
    assert second == (
        False,
        True,
        False,
        False,
        "revocation",
        False,
        True,
    )
    assert not model.state.active


def test_reveal_receipt_binds_pre_and_post_structural_state(monkeypatch):
    config = _config()
    model = OnlineCausalSelfBoundary(config)
    rank_two = _fit(config, 1, 2, 2, confidence=0.50)
    rank_one = _fit(config, 1, 2, 1, confidence=0.40)
    proposals = iter((rank_two, rank_two, rank_one, rank_one))
    monkeypatch.setattr(
        boundary_module,
        "_fit_window",
        lambda evidence, observed_config: next(proposals),
    )

    receipts = []
    for time in range(140):
        commitment = model.commit_handles(time=time)
        bound = model.bind_sources(
            np.zeros(config.observation_dim),
            np.zeros((config.source_count, config.process_dim)),
            commitment_digest=commitment.digest,
            time=time,
        )
        receipts.append(
            model.reveal_outcome(
                np.zeros(config.observation_dim),
                transition_digest=bound.transition_digest,
                time=time + 1,
            )
        )

    acquisition = receipts[99]
    candidate = receipts[119]
    revision = receipts[139]
    assert acquisition.structural_event == "acquisition"
    assert acquisition.acquired and not acquisition.revised
    assert candidate.structural_event == "structural_candidate"
    assert candidate.previous_rank == 2 and candidate.rank == 2
    assert candidate.candidate_rank == 1 and candidate.candidate_streak == 1
    assert candidate.confidence < candidate.confidence_before
    assert revision.structural_event == "rank_revision"
    assert revision.revised and revision.rank_changed
    assert revision.previous_rank == 2 and revision.rank == 1
    assert revision.epoch == acquisition.epoch + 1
    assert revision.candidate_rank == 0 and revision.candidate_streak == 0

    restored = OnlineCausalSelfBoundary(config)
    restored.load_snapshot(model.snapshot())
    assert restored.snapshot()["digest"] == model.snapshot()["digest"]


def test_reveal_clock_requires_fresh_rows_before_confirmation_renewal(monkeypatch):
    config = _config(
        structural_confirmation_interval=60,
        revision_confirmations=2,
    )
    model = OnlineCausalSelfBoundary(config)
    rank_two = _fit(config, 1, 2, 2, confidence=0.50)
    rank_one = _fit(config, 1, 2, 1, confidence=0.40)
    fit_calls = 0

    def proposal(evidence, observed_config):
        nonlocal fit_calls
        fit_calls += 1
        return rank_two if fit_calls <= 4 else rank_one

    monkeypatch.setattr(boundary_module, "_fit_window", proposal)

    fit_receipts = []
    for time in range(220):
        commitment = model.commit_handles(time=time)
        bound = model.bind_sources(
            np.zeros(config.observation_dim),
            np.zeros((config.source_count, config.process_dim)),
            commitment_digest=commitment.digest,
            time=time,
        )
        receipt = model.reveal_outcome(
            np.zeros(config.observation_dim),
            transition_digest=bound.transition_digest,
            time=time + 1,
        )
        if receipt.fit_performed:
            fit_receipts.append(receipt)

    assert [receipt.evidence_count for receipt in fit_receipts] == [
        80,
        100,
        120,
        140,
        160,
        180,
        200,
        220,
    ]
    assert [receipt.candidate_renewed for receipt in fit_receipts] == [
        True,
        False,
        False,
        True,
        True,
        False,
        False,
        True,
    ]
    assert fit_receipts[3].structural_event == "acquisition"
    assert fit_receipts[7].structural_event == "rank_revision"
    assert model.state.structural_signature == (True, 1, 2, 1)
