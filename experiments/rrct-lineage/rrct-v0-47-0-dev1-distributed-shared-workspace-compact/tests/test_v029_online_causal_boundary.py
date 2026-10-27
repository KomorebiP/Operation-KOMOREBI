import copy
import inspect

import numpy as np
import pytest

import rrct.causal_boundary as causal_boundary
from rrct.causal_boundary import (
    CausalBoundaryConfig,
    OnlineCausalSelfBoundary,
    _monte_carlo_order,
    _monte_carlo_threshold,
    _replicated_directional_mode,
    _rerandomized_handles,
)


def _config(**changes):
    values = {
        "observation_dim": 6,
        "process_dim": 4,
        "source_count": 3,
        "handle_count": 2,
        "evidence_capacity": 120,
        "minimum_samples": 120,
        "fit_interval": 20,
        "commitment_block_size": 20,
        "ridge": 0.35,
        "null_permutations": 9,
        "half_null_permutations": 9,
        "null_quantile": 0.90,
        "higher_mode_null": "global_sharp_null",
        "revision_confirmations": 2,
        "revocation_confirmations": 2,
        "confidence_decay": 0.60,
        "seed": 2901,
    }
    values.update(changes)
    return CausalBoundaryConfig(**values)


def _effects(seed=701):
    rng = np.random.default_rng(seed)
    internal, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    sensory, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    routed = (
        internal[:, :2]
        @ np.asarray([[1.85, 0.08], [-0.05, 1.45]])
        @ sensory[:, :2].T
    )
    exogenous = 2.50 * internal[:, 2:4] @ sensory[:, 2:4].T
    return routed, exogenous, internal[:, :2] @ internal[:, :2].T


def _advance(model, rng, time, *, pair=None, routed=None, exogenous=None):
    commitment = model.commit_handles(time=time)
    observation = rng.normal(size=model.config.observation_dim)
    bank = rng.normal(
        size=(model.config.source_count, model.config.process_dim)
    )
    next_observation = 0.42 * observation
    if exogenous is not None:
        next_observation = next_observation + bank[0] @ exogenous
    if pair is not None:
        handle_index, source_index = pair
        next_observation = next_observation + (
            commitment.handles[handle_index]
            * bank[source_index]
            @ routed
        )
    next_observation = next_observation + rng.normal(
        0.0, 0.035, size=model.config.observation_dim
    )
    bound = model.bind_sources(
        observation,
        bank,
        commitment_digest=commitment.digest,
        time=time,
    )
    receipt = model.reveal_outcome(
        next_observation,
        transition_digest=bound.transition_digest,
        time=time + 1,
    )
    return commitment, observation, bank, next_observation, bound, receipt


def _run(model, rng, start, count, *, pair=None, routed=None, exogenous=None):
    receipts = []
    for time in range(start, start + count):
        receipts.append(
            _advance(
                model,
                rng,
                time,
                pair=pair,
                routed=routed,
                exogenous=exogenous,
            )[-1]
        )
    return receipts


def _assert_same_state(first, second):
    assert first.selected_handle_index == second.selected_handle_index
    assert first.selected_source_index == second.selected_source_index
    assert first.rank == second.rank
    assert first.confidence == second.confidence
    assert first.uncertainty == second.uncertainty
    assert first.change_alarm == second.change_alarm
    assert first.evidence_count == second.evidence_count
    assert first.fit_count == second.fit_count
    assert first.age == second.age
    assert first.epoch == second.epoch
    assert first.model_digest == second.model_digest
    assert np.array_equal(first.internal_projector, second.internal_projector)
    assert np.array_equal(first.sensory_projector, second.sensory_projector)
    assert np.array_equal(first.effect_operator, second.effect_operator)


def _keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _keys(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _keys(item)


def _rehash_boundary_snapshot(snapshot):
    payload = copy.deepcopy(snapshot)
    payload.pop("digest", None)
    payload["digest"] = causal_boundary._digest(payload)
    return payload


def _rehash_boundary_state(model, snapshot):
    raw = snapshot["state"]
    candidate = causal_boundary.CausalBoundaryState(**raw)
    raw["model_digest"] = model._state_digest(candidate)
    return _rehash_boundary_snapshot(snapshot)


def test_commit_bind_reveal_is_balanced_hashed_and_single_use():
    config = _config(minimum_samples=120, evidence_capacity=120)
    first = OnlineCausalSelfBoundary(config)
    replay = OnlineCausalSelfBoundary(config)
    rng_a = np.random.default_rng(11)
    rng_b = np.random.default_rng(11)
    handles_a = []
    handles_b = []

    for time in range(config.commitment_block_size):
        result_a = _advance(first, rng_a, time)
        result_b = _advance(replay, rng_b, time)
        handles_a.append(result_a[0].handles)
        handles_b.append(result_b[0].handles)
        assert result_a[0].digest == result_b[0].digest
        assert result_a[4].transition_digest == result_b[4].transition_digest

    handles_a = np.stack(handles_a)
    assert np.array_equal(handles_a, np.stack(handles_b))
    assert np.all((handles_a == 0.0) | (handles_a == 1.0))
    assert np.array_equal(
        handles_a.sum(axis=0),
        np.full(config.handle_count, config.commitment_block_size // 2),
    )

    commitment = first.commit_handles(time=30)
    assert not commitment.handles.flags.writeable
    with pytest.raises(RuntimeError, match="already pending"):
        first.commit_handles(time=30)
    observation = np.zeros(config.observation_dim)
    bank = np.zeros((config.source_count, config.process_dim))
    with pytest.raises(ValueError, match="digest"):
        first.bind_sources(
            observation,
            bank,
            commitment_digest="0" * 64,
            time=30,
        )
    with pytest.raises(ValueError, match="time"):
        first.bind_sources(
            observation,
            bank,
            commitment_digest=commitment.digest,
            time=31,
        )
    bound = first.bind_sources(
        observation,
        bank,
        commitment_digest=commitment.digest,
        time=30,
    )
    with pytest.raises(ValueError, match="digest"):
        first.reveal_outcome(
            observation,
            transition_digest="f" * 64,
            time=31,
        )
    with pytest.raises(ValueError, match="follow"):
        first.reveal_outcome(
            observation,
            transition_digest=bound.transition_digest,
            time=30,
        )
    first.reveal_outcome(
        observation,
        transition_digest=bound.transition_digest,
        time=31,
    )
    with pytest.raises(RuntimeError, match="no bound"):
        first.reveal_outcome(
            observation,
            transition_digest=bound.transition_digest,
            time=31,
        )


def test_reveal_rolls_back_the_complete_transition_when_a_fit_raises(monkeypatch):
    model = OnlineCausalSelfBoundary(_config())
    rng = np.random.default_rng(13)
    _run(model, rng, 0, model.config.minimum_samples - 1)
    time = model.config.minimum_samples - 1
    commitment = model.commit_handles(time=time)
    observation = rng.normal(size=model.config.observation_dim)
    bank = rng.normal(
        size=(model.config.source_count, model.config.process_dim)
    )
    next_observation = rng.normal(size=model.config.observation_dim)
    bound = model.bind_sources(
        observation,
        bank,
        commitment_digest=commitment.digest,
        time=time,
    )
    before = model.snapshot()
    original_fit = causal_boundary._fit_window

    def fail_fit(*args, **kwargs):
        raise RuntimeError("deliberate fit failure")

    monkeypatch.setattr(causal_boundary, "_fit_window", fail_fit)
    with pytest.raises(RuntimeError, match="deliberate fit failure"):
        model.reveal_outcome(
            next_observation,
            transition_digest=bound.transition_digest,
            time=time + 1,
        )
    assert model.snapshot()["digest"] == before["digest"]
    assert model.has_bound_transition

    monkeypatch.setattr(causal_boundary, "_fit_window", original_fit)
    receipt = model.reveal_outcome(
        next_observation,
        transition_digest=bound.transition_digest,
        time=time + 1,
    )
    assert receipt.fit_performed
    assert receipt.evidence_count == model.config.minimum_samples


def test_finite_monte_carlo_order_requires_resolvable_tail_without_interpolation():
    with pytest.raises(ValueError, match="cannot resolve alpha"):
        _config(
            null_quantile=0.99,
            null_permutations=98,
            half_null_permutations=99,
        )
    resolved = _config(
        null_quantile=0.99,
        null_permutations=99,
        half_null_permutations=99,
    )
    assert resolved.null_permutations == 99
    assert _monte_carlo_order(99, 0.99) == 99
    maxima = np.arange(99, dtype=np.float64)
    assert _monte_carlo_threshold(maxima, 0.99) == 98.0
    with pytest.raises(ValueError, match="nuisance-design columns"):
        _config(minimum_samples=40)


def test_handle_null_rerandomizes_columns_within_balanced_commitment_blocks():
    size = 20
    first = np.column_stack(
        (
            np.tile([0.0, 1.0], size // 2),
            np.repeat([0.0, 1.0], size // 2),
        )
    )
    handles = np.vstack((first, first[::-1]))
    nonces = np.arange(2 * size, dtype=np.int64)
    randomized = _rerandomized_handles(
        handles, nonces, size, np.random.default_rng(117)
    )
    replay = _rerandomized_handles(
        handles, nonces, size, np.random.default_rng(117)
    )
    assert np.array_equal(randomized, replay)
    assert not np.array_equal(randomized, handles)
    for start in (0, size):
        stop = start + size
        assert np.array_equal(
            randomized[start:stop].sum(axis=0),
            handles[start:stop].sum(axis=0),
        )


def test_each_max_null_draw_recomputes_the_residual_problem(monkeypatch):
    config = _config(null_quantile=0.80, null_permutations=4)
    rng = np.random.default_rng(121)
    observation = rng.normal(size=(20, config.observation_dim))
    bank = rng.normal(size=(20, config.source_count, config.process_dim))
    handles = np.column_stack(
        [
            np.tile([0.0, 1.0], 10),
            np.repeat([0.0, 1.0], 10),
        ]
    )
    next_observation = rng.normal(size=(20, config.observation_dim))
    nonces = np.arange(20, dtype=np.int64)
    original = causal_boundary._residual_problem
    calls = []

    def counted(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(causal_boundary, "_residual_problem", counted)
    causal_boundary._familywise_threshold(
        observation,
        bank,
        handles,
        next_observation,
        nonces,
        config,
        permutations=4,
        salt=131,
    )
    assert len(calls) == 4


def test_replication_rejects_opposite_sign_or_negative_half_effects():
    assert _replicated_directional_mode(2.0, 1.5, 1.2, 1.0, 1.0, 1.0)
    assert not _replicated_directional_mode(2.0, 1.5, -1.2, 1.0, 1.0, 1.0)
    assert not _replicated_directional_mode(2.0, -1.5, -1.2, 1.0, 1.0, 1.0)


def test_sequential_mode_admission_does_not_promote_rank_one_to_rank_two():
    config = _config(revision_confirmations=1)
    model = OnlineCausalSelfBoundary(config)
    basis_rng = np.random.default_rng(777)
    internal, _ = np.linalg.qr(basis_rng.normal(size=(4, 4)))
    sensory, _ = np.linalg.qr(basis_rng.normal(size=(6, 6)))
    routed = 2.5 * np.outer(internal[:, 0], sensory[:, 0])
    exogenous = 2.5 * internal[:, 2:4] @ sensory[:, 2:4].T
    _run(
        model,
        np.random.default_rng(41),
        0,
        120,
        pair=(1, 2),
        routed=routed,
        exogenous=exogenous,
    )
    assert model.state.active
    assert (model.state.selected_handle_index, model.state.selected_source_index) == (
        1,
        2,
    )
    assert model.state.rank == 1


def test_online_boundary_acquires_rank_two_revises_and_revokes():
    # A longer revocation horizon lets a changed unique pair replicate through
    # a mixed rolling window; repeated true-null fits still revoke below.
    model = OnlineCausalSelfBoundary(_config(revocation_confirmations=8))
    rng = np.random.default_rng(19)
    routed, exogenous, internal_truth = _effects()

    early = _run(
        model,
        rng,
        0,
        model.config.minimum_samples,
        pair=(1, 2),
        routed=routed,
        exogenous=exogenous,
    )
    assert early[-1].fit_performed
    assert not model.state.active
    _run(
        model,
        rng,
        model.config.minimum_samples,
        model.config.fit_interval,
        pair=(1, 2),
        routed=routed,
        exogenous=exogenous,
    )
    acquired = model.state
    assert acquired.active
    assert (acquired.selected_handle_index, acquired.selected_source_index) == (1, 2)
    assert acquired.rank == 2
    assert acquired.epoch == 1
    assert np.trace(acquired.internal_projector @ internal_truth) / 2.0 > 0.98
    assert np.allclose(
        acquired.internal_projector @ acquired.effect_operator,
        acquired.effect_operator,
        atol=1e-10,
    )
    assert np.allclose(
        acquired.effect_operator @ acquired.sensory_projector,
        acquired.effect_operator,
        atol=1e-10,
    )
    assert np.linalg.matrix_rank(
        acquired.effect_operator,
        tol=1e-9,
    ) == acquired.rank
    assert np.linalg.matrix_rank(
        acquired.internal_projector,
        tol=1e-9,
    ) == acquired.rank
    assert np.linalg.matrix_rank(
        acquired.sensory_projector,
        tol=1e-9,
    ) == acquired.rank
    assert 0.0 < acquired.confidence <= 1.0

    acquisition_epoch = acquired.epoch
    revision_receipts = _run(
        model,
        rng,
        140,
        180,
        pair=(0, 1),
        routed=routed,
        exogenous=exogenous,
    )
    revised = model.state
    assert (revised.selected_handle_index, revised.selected_source_index) == (0, 1)
    assert revised.rank == 2
    assert revised.epoch == acquisition_epoch + 1
    assert any(receipt.revised for receipt in revision_receipts)

    revocation_receipts = _run(
        model,
        rng,
        320,
        300,
        pair=None,
        routed=routed,
        exogenous=exogenous,
    )
    revoked = model.state
    assert not revoked.active
    assert revoked.rank == 0
    assert revoked.selected_handle_index is None
    assert revoked.selected_source_index is None
    assert revoked.epoch == revised.epoch + 1
    assert revoked.change_alarm > 0.0
    assert any(receipt.revoked for receipt in revocation_receipts)
    assert revoked.evidence_count == 620
    # The rolling window has truncated, but the persistent counter and snapshot agree.
    restored = OnlineCausalSelfBoundary(model.config)
    restored.load_snapshot(model.snapshot())
    _assert_same_state(restored.state, revoked)


def test_descriptor_is_bounded_persistent_and_pair_identifying():
    config = _config()
    null_model = OnlineCausalSelfBoundary(config)
    observation = np.linspace(-4.0, 4.0, config.observation_dim)
    null_descriptor = null_model.descriptor(observation)
    assert null_descriptor.shape == (null_model.descriptor_dim,)
    assert np.max(np.abs(null_descriptor)) <= 1.0
    assert null_descriptor.any()  # uncertainty telemetry broadcasts the null state

    model = OnlineCausalSelfBoundary(config)
    rng = np.random.default_rng(23)
    routed, exogenous, _ = _effects(703)
    _run(
        model,
        rng,
        0,
        140,
        pair=(1, 2),
        routed=routed,
        exogenous=exogenous,
    )
    assert model.state.active
    commitment = model.commit_handles(time=140)
    bank = rng.normal(size=(config.source_count, config.process_dim))
    descriptor = model.descriptor(observation, bank, commitment.handles)
    assert descriptor.shape == (model.descriptor_dim,)
    assert np.max(np.abs(descriptor)) <= 1.0
    identity_start = config.observation_dim + config.process_dim
    handle_code = descriptor[
        identity_start : identity_start + config.handle_count
    ]
    source_code = descriptor[
        identity_start + config.handle_count :
        identity_start + config.handle_count + config.source_count
    ]
    assert np.array_equal(handle_code, np.asarray([0.0, 1.0]))
    assert np.array_equal(source_code, np.asarray([0.0, 0.0, 1.0]))
    candidate = model.candidate_signal(bank, commitment.handles)
    raw = commitment.handles[1] * bank[2]
    assert np.linalg.norm(candidate) <= np.linalg.norm(raw) + 1e-10

    digest = model.state.model_digest
    model.reset_pending()
    assert model.state.model_digest == digest
    assert model.descriptor(observation).any()


def test_freeze_snapshot_load_and_deepcopy_continue_exactly():
    config = _config()
    model = OnlineCausalSelfBoundary(config)
    rng = np.random.default_rng(29)
    routed, exogenous, _ = _effects(709)
    _run(
        model,
        rng,
        0,
        140,
        pair=(1, 2),
        routed=routed,
        exogenous=exogenous,
    )
    assert model.state.active
    frozen_model = model.state
    model.freeze()
    frozen_receipts = _run(
        model,
        rng,
        140,
        140,
        pair=(0, 1),
        routed=routed,
        exogenous=exogenous,
    )
    assert all(receipt.updates_frozen for receipt in frozen_receipts)
    frozen_after_evidence = model.state
    assert (
        frozen_after_evidence.selected_handle_index,
        frozen_after_evidence.selected_source_index,
        frozen_after_evidence.rank,
        frozen_after_evidence.epoch,
    ) == (
        frozen_model.selected_handle_index,
        frozen_model.selected_source_index,
        frozen_model.rank,
        frozen_model.epoch,
    )
    assert np.array_equal(
        frozen_after_evidence.internal_projector,
        frozen_model.internal_projector,
    )
    assert frozen_after_evidence.evidence_count == 280

    commitment = model.commit_handles(time=280)
    pending_observation = rng.normal(size=config.observation_dim)
    pending_bank = rng.normal(size=(config.source_count, config.process_dim))
    bound = model.bind_sources(
        pending_observation,
        pending_bank,
        commitment_digest=commitment.digest,
        time=280,
    )
    snapshot = model.snapshot()
    restored = OnlineCausalSelfBoundary(config)
    restored.load_snapshot(snapshot)
    cloned = copy.deepcopy(model)
    assert restored.snapshot()["digest"] == snapshot["digest"]
    assert cloned.snapshot()["digest"] == snapshot["digest"]

    pending_next = (
        0.42 * pending_observation
        + pending_bank[0] @ exogenous
        + commitment.handles[0] * pending_bank[1] @ routed
    )
    receipts = [
        item.reveal_outcome(
            pending_next,
            transition_digest=bound.transition_digest,
            time=281,
        )
        for item in (model, restored, cloned)
    ]
    assert receipts[0] == receipts[1] == receipts[2]
    assert model.snapshot()["digest"] == restored.snapshot()["digest"]
    assert model.snapshot()["digest"] == cloned.snapshot()["digest"]

    for item in (model, restored, cloned):
        item.unfreeze()
    continuation_rng = np.random.default_rng(31)
    for time in range(281, 321):
        observation = continuation_rng.normal(size=config.observation_dim)
        bank = continuation_rng.normal(
            size=(config.source_count, config.process_dim)
        )
        noise = continuation_rng.normal(0.0, 0.035, size=config.observation_dim)
        commitments = [item.commit_handles(time=time) for item in (model, restored, cloned)]
        assert commitments[0].digest == commitments[1].digest == commitments[2].digest
        next_observation = (
            0.42 * observation
            + bank[0] @ exogenous
            + commitments[0].handles[0] * bank[1] @ routed
            + noise
        )
        bound_receipts = [
            item.bind_sources(
                observation,
                bank,
                commitment_digest=committed.digest,
                time=time,
            )
            for item, committed in zip(
                (model, restored, cloned), commitments, strict=True
            )
        ]
        update_receipts = [
            item.reveal_outcome(
                next_observation,
                transition_digest=bound_receipt.transition_digest,
                time=time + 1,
            )
            for item, bound_receipt in zip(
                (model, restored, cloned), bound_receipts, strict=True
            )
        ]
        assert update_receipts[0] == update_receipts[1] == update_receipts[2]
    assert model.snapshot()["digest"] == restored.snapshot()["digest"]
    assert model.snapshot()["digest"] == cloned.snapshot()["digest"]

    corrupted = model.snapshot()
    corrupted["state"]["confidence"] = 0.123
    with pytest.raises(ValueError, match="snapshot digest"):
        restored.load_snapshot(corrupted)


def test_rehashed_snapshot_rejects_evidence_receipt_nonce_and_state_forgery():
    config = _config()
    model = OnlineCausalSelfBoundary(config)
    _advance(model, np.random.default_rng(33), 0)

    bad_counter = model.snapshot()
    bad_counter["commit_count"] = 0
    with pytest.raises(ValueError, match="completed_count exceeds commit_count"):
        OnlineCausalSelfBoundary(config).load_snapshot(
            _rehash_boundary_snapshot(bad_counter)
        )

    bad_evidence = model.snapshot()
    bad_evidence["evidence"][0]["handles"] = (
        1.0 - bad_evidence["evidence"][0]["handles"]
    )
    with pytest.raises(ValueError, match="owned schedule|commitment digest"):
        OnlineCausalSelfBoundary(config).load_snapshot(
            _rehash_boundary_snapshot(bad_evidence)
        )

    bad_receipt = model.snapshot()
    bad_receipt["last_receipt"]["outcome_digest"] = "0" * 64
    with pytest.raises(ValueError, match="last_receipt does not match"):
        OnlineCausalSelfBoundary(config).load_snapshot(
            _rehash_boundary_snapshot(bad_receipt)
        )

    impossible = OnlineCausalSelfBoundary(config)
    bad_state = impossible.snapshot()
    bad_state["state"].update(
        {
            "selected_handle_index": 0,
            "selected_source_index": 0,
            "rank": 99,
            "confidence": 0.9,
            "uncertainty": 0.1,
        }
    )
    with pytest.raises(ValueError, match="active state rank"):
        OnlineCausalSelfBoundary(config).load_snapshot(
            _rehash_boundary_state(impossible, bad_state)
        )

    bad_confidence = impossible.snapshot()
    bad_confidence["state"]["confidence"] = 0.2
    bad_confidence["state"]["uncertainty"] = 0.9
    with pytest.raises(ValueError, match="must sum to one"):
        OnlineCausalSelfBoundary(config).load_snapshot(
            _rehash_boundary_state(impossible, bad_confidence)
        )


def test_rehashed_snapshot_rejects_invalid_projector_and_effect_geometry():
    config = _config()
    model = OnlineCausalSelfBoundary(config)
    routed, exogenous, _ = _effects(713)
    _run(
        model,
        np.random.default_rng(35),
        0,
        140,
        pair=(1, 2),
        routed=routed,
        exogenous=exogenous,
    )
    assert model.state.active

    bad_projector = model.snapshot()
    bad_projector["state"]["internal_projector"][0, 1] += 0.1
    with pytest.raises(ValueError, match="internal_projector"):
        OnlineCausalSelfBoundary(config).load_snapshot(
            _rehash_boundary_state(model, bad_projector)
        )

    bad_effect = model.snapshot()
    bad_effect["state"]["effect_operator"].fill(0.0)
    with pytest.raises(ValueError, match="effect_operator rank"):
        OnlineCausalSelfBoundary(config).load_snapshot(
            _rehash_boundary_state(model, bad_effect)
        )


def test_api_has_no_evaluator_labels_and_null_data_fail_closed():
    config = _config()
    model = OnlineCausalSelfBoundary(config)
    routed, exogenous, _ = _effects(719)
    rng = np.random.default_rng(37)
    _run(
        model,
        rng,
        0,
        140,
        pair=None,
        routed=routed,
        exogenous=exogenous,
    )
    assert not model.state.active
    assert model.state.rank == 0
    bank = rng.normal(size=(config.source_count, config.process_dim))
    assert not model.candidate_signal(bank, np.ones(config.handle_count)).any()

    public_parameters = {
        *inspect.signature(model.commit_handles).parameters,
        *inspect.signature(model.bind_sources).parameters,
        *inspect.signature(model.reveal_outcome).parameters,
    }
    forbidden = ("truth", "label", "oracle", "route", "condition")
    assert not any(
        token in parameter.lower()
        for parameter in public_parameters
        for token in forbidden
    )
    assert not any(
        token in key.lower()
        for key in _keys(model.snapshot())
        for token in forbidden
    )
