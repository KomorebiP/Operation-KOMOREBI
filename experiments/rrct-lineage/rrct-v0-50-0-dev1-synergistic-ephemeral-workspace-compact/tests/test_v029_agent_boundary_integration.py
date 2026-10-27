import copy
import hashlib
import json
import pickle
from dataclasses import fields, is_dataclass, replace
from pathlib import Path

import numpy as np
import pytest

from rrct.agent import RRCTAgent
from rrct.causal_boundary import (
    CausalBoundaryConfig,
    OnlineCausalAccessReadout,
    OnlineCausalSelfBoundary,
)


def _boundary_config(**changes):
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
        "revocation_confirmations": 4,
        "seed": 2929,
    }
    values.update(changes)
    return CausalBoundaryConfig(**values)


def _agent(*, config=None, ablations=None, seed=83, gain=2.0):
    return RRCTAgent(
        6,
        projector_ranks=(2, 4, 6),
        action_dim=2,
        n_specialists=3,
        specialist_dim=6,
        workspace_dim=6,
        workspace_capacity=2,
        self_dim=5,
        memory_capacity=20,
        memory_top_k=2,
        seed=seed,
        causal_boundary_config=config,
        causal_boundary_broadcast_gain=gain,
        ablations=ablations,
    )


def _effects(seed=811):
    rng = np.random.default_rng(seed)
    internal, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    sensory, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    routed = (
        internal[:, :2]
        @ np.asarray([[4.00, 0.05], [-0.04, 3.50]])
        @ sensory[:, :2].T
    )
    exogenous = 2.60 * internal[:, 2:4] @ sensory[:, 2:4].T
    return routed, exogenous


def _assert_equal(first, second):
    if isinstance(first, np.ndarray) or isinstance(second, np.ndarray):
        assert isinstance(first, np.ndarray) and isinstance(second, np.ndarray)
        assert np.array_equal(first, second)
        return
    if is_dataclass(first) or is_dataclass(second):
        assert type(first) is type(second)
        for field in fields(first):
            _assert_equal(getattr(first, field.name), getattr(second, field.name))
        return
    if isinstance(first, dict) or isinstance(second, dict):
        assert isinstance(first, dict) and isinstance(second, dict)
        assert first.keys() == second.keys()
        for key in first:
            _assert_equal(first[key], second[key])
        return
    if isinstance(first, (tuple, list)) or isinstance(second, (tuple, list)):
        assert type(first) is type(second)
        assert len(first) == len(second)
        for left, right in zip(first, second, strict=True):
            _assert_equal(left, right)
        return
    assert first == second


def _trace_update(digest, value):
    if isinstance(value, np.ndarray):
        array = np.ascontiguousarray(value)
        digest.update(b"array\0")
        digest.update(array.dtype.str.encode("ascii"))
        digest.update(json.dumps(array.shape).encode("ascii"))
        digest.update(array.tobytes(order="C"))
        return
    if is_dataclass(value):
        digest.update(b"dataclass\0")
        digest.update(type(value).__name__.encode("utf-8"))
        for field in fields(value):
            _trace_update(digest, field.name)
            _trace_update(digest, getattr(value, field.name))
        return
    if isinstance(value, dict):
        digest.update(b"mapping\0")
        for key in sorted(value, key=str):
            _trace_update(digest, str(key))
            _trace_update(digest, value[key])
        return
    if isinstance(value, (tuple, list)):
        digest.update(b"sequence\0")
        for item in value:
            _trace_update(digest, item)
        return
    if isinstance(value, np.generic):
        value = value.item()
    digest.update(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    )


def _historical_trace_digest(results, historical_fields):
    digest = hashlib.sha256()
    digest.update(b"sequence\0")
    for result in results:
        digest.update(b"dataclass\0")
        digest.update(b"StepResult")
        for name in historical_fields:
            _trace_update(digest, name)
            _trace_update(digest, getattr(result, name))
    return digest.hexdigest()


def _value_digest(value):
    digest = hashlib.sha256()
    _trace_update(digest, value)
    return digest.hexdigest()


def _advance(agent, current, rng, routed, exogenous):
    result = agent.step(current)
    commitment = result.causal_commitment
    assert commitment is not None
    assert commitment.time == result.time
    assert commitment.digest == result.causal_commitment_digest
    bank = rng.normal(size=(3, 4))
    bound = agent.bind_causal_sources(bank, commitment)
    next_observation = (
        0.30 * current
        + bank[0] @ exogenous
        + commitment.handles[1] * bank[2] @ routed
        + rng.normal(0.0, 0.015, size=6)
    )
    return next_observation, result, commitment, bank, bound


@pytest.fixture(scope="module")
def acquired_agent():
    agent = _agent(config=_boundary_config())
    routed, exogenous = _effects()
    rng = np.random.default_rng(821)
    current = rng.normal(size=6)
    for _ in range(181):
        current, _, _, _, _ = _advance(
            agent, current, rng, routed, exogenous
        )
    assert agent.causal_boundary_state.active
    assert (
        agent.causal_boundary_state.selected_handle_index,
        agent.causal_boundary_state.selected_source_index,
    ) == (1, 2)
    return agent, current, routed, exogenous


def test_default_off_preserves_historical_trace_and_rng_exactly():
    historical_style = _agent(seed=89)
    explicit_off = _agent(config=None, seed=89)
    observations = np.random.default_rng(827).normal(size=(8, 6))
    for observation in observations:
        first = historical_style.step(observation)
        second = explicit_off.step(observation)
        _assert_equal(first, second)
        assert np.array_equal(first.feature_vector(), second.feature_vector())
        assert first.causal_boundary_state is None
        assert first.causal_commitment is None
        assert first.causal_boundary_descriptor.size == 0
        assert not first.causal_boundary_workspace_drive.any()
        assert first.causal_public_pair is None
    _assert_equal(historical_style.snapshot(), explicit_off.snapshot())


def test_default_off_matches_immutable_v028_numerical_trace_fixture():
    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "v028_default_off_trace.json"
    )
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert fixture["provenance"]["parent_archive_sha256"] == (
        "4477fcba7f0e2c63829f1eef942c0e492f4872d436fa1ad03a230b54f52d3a2f"
    )
    observations = np.random.default_rng(827).normal(size=(8, 6))
    assert _value_digest(observations) == fixture["observation_generator"][
        "sha256"
    ]
    agent = _agent(seed=89)
    results = [agent.step(observation) for observation in observations]
    assert _historical_trace_digest(
        results,
        fixture["historical_step_fields"],
    ) == fixture["historical_trace_sha256"]
    assert np.array_equal(
        results[-1].feature_vector(),
        np.asarray(fixture["last_feature_vector"], dtype=np.float64),
    )


def test_step_reveals_then_processes_same_observation_then_commits(monkeypatch):
    agent = _agent(config=_boundary_config(), seed=97)
    initial = agent.step(np.zeros(6))
    bank = np.arange(12, dtype=np.float64).reshape(3, 4) / 12.0
    bound = agent.bind_causal_sources(bank, initial.causal_commitment)
    events = []

    original_reveal = agent.causal_boundary.reveal_outcome
    original_observe = agent.observation_forecaster.observe
    original_commit = agent.causal_boundary.commit_handles

    def reveal(value, **kwargs):
        events.append(("reveal", np.asarray(value).copy()))
        return original_reveal(value, **kwargs)

    def observe(value):
        events.append(("ordinary", np.asarray(value).copy()))
        return original_observe(value)

    def commit(*, time):
        events.append(("commit", time))
        return original_commit(time=time)

    monkeypatch.setattr(agent.causal_boundary, "reveal_outcome", reveal)
    monkeypatch.setattr(agent.observation_forecaster, "observe", observe)
    monkeypatch.setattr(agent.causal_boundary, "commit_handles", commit)
    outcome = np.linspace(-0.4, 0.5, 6)
    result = agent.step(outcome)

    assert [event[0] for event in events] == ["reveal", "ordinary", "commit"]
    assert np.array_equal(events[0][1], outcome)
    assert np.array_equal(events[1][1], outcome)
    assert result.causal_boundary_update_receipt.transition_digest == bound.transition_digest
    assert result.causal_boundary_update_receipt.reveal_time == result.time == 1
    assert len(result.causal_boundary_update_receipt.outcome_digest) == 64
    assert result.causal_commitment.time == result.time
    assert not hasattr(agent, "register_causal_outcome")
    assert not hasattr(agent, "commit_causal_handles")


def test_binding_is_post_step_single_use_and_tamper_guarded():
    agent = _agent(config=_boundary_config(), seed=103)
    observation = np.linspace(-0.5, 0.5, 6)
    result = agent.step(observation)
    commitment = result.causal_commitment
    bank = np.arange(12, dtype=np.float64).reshape(3, 4) / 10.0

    with pytest.raises(RuntimeError, match="bind_causal_sources"):
        agent.step(observation[::-1])
    assert agent.time == 1
    altered = replace(commitment, handles=1.0 - commitment.handles)
    with pytest.raises(ValueError, match="commitment"):
        agent.bind_causal_sources(bank, altered)
    assert agent.causal_boundary.has_pending_commitment
    bound = agent.bind_causal_sources(bank, commitment)
    assert bound.commitment_digest == commitment.digest
    with pytest.raises(RuntimeError, match="unbound"):
        agent.bind_causal_sources(bank, commitment)


def test_boundary_is_a_native_competitor_and_access_is_workspace_derived(
    acquired_agent,
):
    template, current, _, _ = acquired_agent
    intact = copy.deepcopy(template)
    ablated = copy.deepcopy(template)
    ablated.set_ablations("causal_boundary_broadcast", reset=False)
    fresh_readout = copy.deepcopy(template)
    fresh_readout._causal_access_readout.reset()

    pre_access = OnlineCausalAccessReadout(11, 2, 3)
    pre_access.load_snapshot(
        intact.causal_boundary_snapshot()["access_readout"]
    )
    intact_result = intact.step(current)
    ablated_result = ablated.step(current)
    fresh_result = fresh_readout.step(current)

    _assert_equal(
        intact_result.causal_boundary_state,
        ablated_result.causal_boundary_state,
    )
    assert "causal_boundary" in intact_result.selected_specialists
    assert "causal_boundary" not in ablated_result.selected_specialists
    assert intact_result.causal_boundary_proposal_selected
    assert not ablated_result.causal_boundary_proposal_selected
    assert np.linalg.norm(intact_result.causal_boundary_candidate_signal) > 0.0
    assert np.linalg.norm(intact_result.causal_boundary_proposal_state) > 0.0
    assert np.linalg.norm(intact_result.causal_boundary_workspace_drive) > 0.0
    assert not ablated_result.causal_boundary_proposal_state.any()
    assert not ablated_result.causal_boundary_workspace_drive.any()
    assert not np.array_equal(intact_result.workspace, ablated_result.workspace)

    inferred = pre_access.predict(
        np.concatenate((intact_result.workspace, intact_result.self_state))
    )
    assert intact_result.causal_public_pair == inferred.pair == (1, 2)
    assert intact.choose_causal_port() == inferred.pair
    assert intact_result.causal_access_updated
    assert not ablated_result.causal_access_updated
    assert ablated.choose_causal_port() is None
    # Active private state is insufficient: a fresh prequential readout must
    # abstain on its first selected attempted-pair broadcast.
    assert fresh_result.causal_boundary_state.active
    assert fresh_result.causal_public_pair is None
    assert fresh_result.causal_access_updated


def test_zero_gain_and_whole_broadcast_ablation_cannot_leak_private_pair(
    acquired_agent,
):
    template, current, _, _ = acquired_agent
    zero_gain = copy.deepcopy(template)
    zero_gain.causal_boundary_broadcast_gain = 0.0
    no_broadcast = copy.deepcopy(template)
    no_broadcast.set_ablations("broadcast", reset=False)
    zero_count = zero_gain._causal_access_readout.update_count
    broadcast_count = no_broadcast._causal_access_readout.update_count

    zero_result = zero_gain.step(current)
    broadcast_result = no_broadcast.step(current)
    assert zero_result.causal_boundary_state.active
    assert broadcast_result.causal_boundary_state.active
    assert not zero_result.causal_boundary_proposal_state.any()
    assert zero_result.causal_public_pair is None
    assert no_broadcast.choose_causal_port() is None
    assert not zero_result.causal_access_updated
    assert not broadcast_result.causal_access_updated
    assert zero_gain._causal_access_readout.update_count == zero_count
    assert no_broadcast._causal_access_readout.update_count == broadcast_count


def test_explicit_resets_record_interrupted_causal_chains():
    agent = _agent(config=_boundary_config(), seed=107)
    first = agent.step(np.zeros(6))
    assert first.causal_interrupted_transitions == 0
    assert agent.causal_boundary.has_pending_commitment
    agent.reset()
    assert agent.snapshot()["causal_interrupted_transitions"] == 1
    assert not agent.causal_boundary.has_pending
    restarted = agent.step(np.ones(6))
    assert restarted.causal_interrupted_transitions == 1
    agent.bind_causal_sources(np.zeros((3, 4)), restarted.causal_commitment)
    agent.reset()
    assert agent.snapshot()["causal_interrupted_transitions"] == 2


def test_snapshot_load_and_deepcopy_preserve_pending_continuation(
    acquired_agent,
):
    template, current, routed, exogenous = acquired_agent
    first = copy.deepcopy(template)
    cloned = copy.deepcopy(template)
    _assert_equal(first.snapshot(), cloned.snapshot())
    snapshot = first.causal_boundary_snapshot()

    restored = copy.deepcopy(first)
    restored.causal_boundary = OnlineCausalSelfBoundary(
        restored.causal_boundary_config
    )
    restored._causal_access_readout = OnlineCausalAccessReadout(11, 2, 3)
    restored.load_causal_boundary_snapshot(snapshot)
    assert restored.causal_boundary_snapshot()["digest"] == snapshot["digest"]

    results = [agent.step(current) for agent in (first, cloned, restored)]
    _assert_equal(results[0], results[1])
    _assert_equal(results[0], results[2])
    rng = np.random.default_rng(839)
    bank = rng.normal(size=(3, 4))
    bounds = [
        agent.bind_causal_sources(bank, result.causal_commitment)
        for agent, result in zip((first, cloned, restored), results, strict=True)
    ]
    assert bounds[0] == bounds[1] == bounds[2]
    next_observation = (
        0.30 * current
        + bank[0] @ exogenous
        + results[0].causal_commitment.handles[1] * bank[2] @ routed
    )
    next_results = [agent.step(next_observation) for agent in (first, cloned, restored)]
    _assert_equal(next_results[0], next_results[1])
    _assert_equal(next_results[0], next_results[2])

    replacing = copy.deepcopy(first)
    replacement_snapshot = first.causal_boundary_snapshot()
    interruptions = replacement_snapshot["boundary"]["interrupted_transitions"]
    replacing.load_causal_boundary_snapshot(replacement_snapshot)
    assert replacing.causal_boundary.interrupted_transitions == interruptions + 1


def test_snapshot_integer_canonicalization_survives_rehashed_tampering():
    agent = _agent(config=_boundary_config(), seed=109)
    snapshot = agent.causal_boundary_snapshot()
    payload = copy.deepcopy(snapshot)
    payload.pop("digest")
    payload["agent_time"] = 0.0
    payload["digest"] = hashlib.sha256(
        pickle.dumps(payload, protocol=5)
    ).hexdigest()
    with pytest.raises(ValueError, match="agent_time"):
        agent.load_causal_boundary_snapshot(payload)


def test_composite_snapshot_binds_broadcast_gain_and_native_projection():
    config = _boundary_config()
    source = _agent(config=config, seed=113, gain=0.5)

    wrong_gain = _agent(config=config, seed=113, gain=2.0)
    before_gain = wrong_gain.causal_boundary_snapshot()["digest"]
    with pytest.raises(ValueError, match="broadcast gain"):
        wrong_gain.load_causal_boundary_snapshot(
            source.causal_boundary_snapshot()
        )
    assert wrong_gain.causal_boundary_snapshot()["digest"] == before_gain

    wrong_projection = _agent(config=config, seed=127, gain=0.5)
    before_projection = wrong_projection.causal_boundary_snapshot()["digest"]
    with pytest.raises(ValueError, match="projection"):
        wrong_projection.load_causal_boundary_snapshot(
            source.causal_boundary_snapshot()
        )
    assert (
        wrong_projection.causal_boundary_snapshot()["digest"]
        == before_projection
    )


def test_constructor_validation():
    config = _boundary_config()
    with pytest.raises(TypeError, match="CausalBoundaryConfig"):
        _agent(config={})
    with pytest.raises(ValueError, match="observation_dim"):
        _agent(config=_boundary_config(observation_dim=7))
    for gain in (True, -0.1, np.nan, np.inf):
        with pytest.raises(ValueError, match="broadcast_gain"):
            RRCTAgent(
                6,
                causal_boundary_config=config,
                causal_boundary_broadcast_gain=gain,
            )
