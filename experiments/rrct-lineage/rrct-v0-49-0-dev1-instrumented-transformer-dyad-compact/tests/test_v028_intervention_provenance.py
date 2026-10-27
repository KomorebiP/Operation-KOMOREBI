from dataclasses import replace

import numpy as np
import pytest

import rrct.intervention_provenance_experiment as provenance

from rrct.intervention_provenance_experiment import (
    discover_intervention_provenance,
)


def _balanced_binary(rng, samples, columns):
    values = np.empty((samples, columns), dtype=np.float64)
    for column in range(columns):
        sequence = np.tile((0.0, 1.0), samples // 2 + 1)[:samples]
        values[:, column] = sequence[rng.permutation(samples)]
    return values


def _synthetic(seed=3, *, gated_route=True):
    rng = np.random.default_rng(seed)
    samples, source_count, handle_count = 1400, 5, 3
    true_handle, true_source = 1, 3
    internal_q, _ = np.linalg.qr(rng.normal(size=(8, 8)))
    sensory_q, _ = np.linalg.qr(rng.normal(size=(12, 12)))
    internal_basis = internal_q[:, :2]
    sensory_basis = sensory_q[:, :2]
    internal_truth = internal_basis @ internal_basis.T
    sensory_truth = sensory_basis @ sensory_basis.T

    sensor = rng.normal(size=(samples, 12))
    bank = rng.normal(size=(samples, source_count, 8))
    # A same-distribution delayed copy is a tempting but noninterventional source.
    bank[1:, 1] = bank[:-1, true_source]
    bank[0, 1] = rng.normal(size=8)
    handles = _balanced_binary(rng, samples, handle_count)

    focal_effect = internal_basis @ np.asarray([[0.68, 0.04], [-0.03, 0.61]]) @ sensory_basis.T
    exogenous_qi, _ = np.linalg.qr(rng.normal(size=(8, 8)))
    exogenous_qo, _ = np.linalg.qr(rng.normal(size=(12, 12)))
    exogenous_effect = 1.05 * exogenous_qi[:, :2] @ exogenous_qo[:, 2:4].T
    delayed_effect = 0.78 * exogenous_qi[:, 2:4] @ exogenous_qo[:, 4:6].T

    next_sensor = (
        0.58 * sensor
        + bank[:, 0] @ exogenous_effect
        + bank[:, 1] @ delayed_effect
        + rng.normal(0.0, 0.065, size=(samples, 12))
    )
    if gated_route:
        next_sensor += (
            handles[:, true_handle, None] * bank[:, true_source]
        ) @ focal_effect
    return {
        "sensor": sensor,
        "bank": bank,
        "handles": handles,
        "next_sensor": next_sensor,
        "true_handle": true_handle,
        "true_source": true_source,
        "internal_truth": internal_truth,
        "sensory_truth": sensory_truth,
    }


def _overlap(projector, truth):
    return float(np.trace(projector @ truth) / 2.0)


def _discover(data, seed=91):
    return discover_intervention_provenance(
        data["sensor"],
        data["bank"],
        data["handles"],
        data["next_sensor"],
        seed=seed,
        permutations=64,
        half_permutations=48,
    )


def test_discovers_hidden_provenance_pair_and_rank_two_interface():
    data = _synthetic()
    found = _discover(data)
    assert found.selected_handle_index == data["true_handle"]
    assert found.selected_source_index == data["true_source"]
    assert found.rank == 2
    assert not found.ambiguous
    assert _overlap(found.internal_projector, data["internal_truth"]) > 0.98
    assert _overlap(found.sensory_projector, data["sensory_truth"]) > 0.98
    expected = (
        data["handles"][:, data["true_handle"], None]
        * data["bank"][:, data["true_source"]]
    ) @ found.internal_projector
    assert np.allclose(found.candidate_signal(data["bank"], data["handles"]), expected)


def test_source_and_handle_permutation_equivariance():
    data = _synthetic(7)
    original = _discover(data, seed=97)
    source_order = np.asarray([2, 4, 0, 1, 3])
    handle_order = np.asarray([1, 2, 0])
    permuted = dict(data)
    permuted["bank"] = data["bank"][:, source_order]
    permuted["handles"] = data["handles"][:, handle_order]
    moved = _discover(permuted, seed=97)
    assert moved.selected_source_index == int(np.flatnonzero(source_order == data["true_source"])[0])
    assert moved.selected_handle_index == int(np.flatnonzero(handle_order == data["true_handle"])[0])
    assert moved.rank == original.rank == 2
    assert np.allclose(moved.internal_projector, original.internal_projector, atol=1e-10)
    assert np.allclose(moved.sensory_projector, original.sensory_projector, atol=1e-10)
    assert np.allclose(
        moved.candidate_signal(permuted["bank"], permuted["handles"]),
        original.candidate_signal(data["bank"], data["handles"]),
        atol=1e-10,
    )


def test_rejects_stronger_ungated_exogenous_and_delayed_associations():
    data = _synthetic(11)
    found = _discover(data, seed=101)
    assert found.selected_source_index == data["true_source"]
    assert found.selected_handle_index == data["true_handle"]
    assert found.pair_ranks[:, 0].sum() == 0
    assert found.pair_ranks[:, 1].sum() == 0
    raw_exogenous_scale = np.linalg.norm(data["bank"][:, 0].T @ data["next_sensor"])
    raw_focal_scale = np.linalg.norm(
        data["bank"][:, data["true_source"]].T @ data["next_sensor"]
    )
    assert raw_exogenous_scale > raw_focal_scale


def test_shuffled_handle_and_no_route_fail_closed():
    routed = _synthetic(17)
    rng = np.random.default_rng(211)
    shuffled = dict(routed)
    shuffled["handles"] = routed["handles"][rng.permutation(len(routed["handles"]))]
    shuffled_found = _discover(shuffled, seed=107)
    assert shuffled_found.rank == 0
    assert shuffled_found.selected_handle_index is None
    assert shuffled_found.selected_source_index is None
    assert not shuffled_found.candidate_signal(
        shuffled["bank"], shuffled["handles"]
    ).any()

    no_route = _synthetic(17, gated_route=False)
    null_found = _discover(no_route, seed=109)
    assert null_found.rank == 0
    assert null_found.selected_handle_index is None
    assert null_found.selected_source_index is None


def test_official_and_pilot_seed_guards_do_not_cross_sets(monkeypatch):
    calls = []

    def fake_run(seed):
        calls.append(int(seed))
        return {"seed": int(seed)}

    monkeypatch.setattr(provenance, "_run_intervention_provenance_seed", fake_run)
    for seed in provenance.V028_DEVELOPMENT_SEEDS:
        assert provenance.run_intervention_provenance_seed(seed) == {"seed": seed}
    for seed in provenance.V028_PILOT_SEEDS:
        assert provenance.run_intervention_provenance_pilot_seed(seed) == {
            "seed": seed
        }
    assert calls == list(provenance.V028_DEVELOPMENT_SEEDS) + list(
        provenance.V028_PILOT_SEEDS
    )

    with pytest.raises(ValueError, match="official set"):
        provenance.run_intervention_provenance_seed(
            provenance.V028_PILOT_SEEDS[0]
        )
    with pytest.raises(ValueError, match="pilot set"):
        provenance.run_intervention_provenance_pilot_seed(
            provenance.V028_DEVELOPMENT_SEEDS[0]
        )
    with pytest.raises(ValueError, match="official set"):
        provenance.run_intervention_provenance_seed(-1)
    with pytest.raises(ValueError, match="pilot set"):
        provenance.run_intervention_provenance_pilot_seed(-1)


def test_official_hidden_truth_uses_distinct_slots_and_valid_permutations():
    routes = [
        provenance._hidden_provenance_route(seed)
        for seed in provenance.V028_DEVELOPMENT_SEEDS
    ]
    assert len({route.true_source_index for route in routes}) == 4
    assert len({route.true_handle_index for route in routes}) == 4
    assert len(
        {(route.true_handle_index, route.true_source_index) for route in routes}
    ) == 4
    for route in routes:
        assert len(route.source_order) == provenance.V028_SOURCE_COUNT
        assert len(set(route.source_order)) == provenance.V028_SOURCE_COUNT
        assert set(route.source_order) == set(provenance.V028_SOURCE_KINDS)
        assert len(route.handle_order) == provenance.V028_HANDLE_COUNT
        assert len(set(route.handle_order)) == provenance.V028_HANDLE_COUNT
        assert set(route.handle_order) == set(
            provenance.V028_GATEABLE_SOURCE_KINDS
        )
        assert route.source_order[route.true_source_index] == "true_private"
        assert route.handle_order[route.true_handle_index] == "true_private"
        assert route.source_index("true_private") == route.true_source_index
        assert route.handle_index("true_private") == route.true_handle_index


def test_commitment_handles_are_binary_balanced_and_fail_on_invalid_shapes():
    first = provenance._balanced_handles(
        np.random.default_rng(311), 60, active_handle=None
    )
    replay = provenance._balanced_handles(
        np.random.default_rng(311), 60, active_handle=None
    )
    assert np.array_equal(first, replay)
    assert first.shape == (60, provenance.V028_HANDLE_COUNT)
    assert np.all((first == 0.0) | (first == 1.0))
    assert np.array_equal(
        np.sum(first, axis=0),
        np.full(provenance.V028_HANDLE_COUNT, 30.0),
    )

    active_index = 2
    active = provenance._balanced_handles(
        np.random.default_rng(313), 30, active_handle=active_index
    )
    assert np.all((active == 0.0) | (active == 1.0))
    assert np.sum(active[:, active_index]) == 15.0
    assert not np.delete(active, active_index, axis=1).any()
    with pytest.raises(ValueError, match="even step count"):
        provenance._balanced_handles(
            np.random.default_rng(317), 31, active_handle=None
        )
    with pytest.raises(ValueError, match="outside"):
        provenance._balanced_handles(
            np.random.default_rng(319),
            30,
            active_handle=provenance.V028_HANDLE_COUNT,
        )


def test_candidate_signal_is_projector_bounded_and_index_fail_closed():
    data = _synthetic(23)
    found = _discover(data, seed=113)
    signal = found.candidate_signal(data["bank"], data["handles"])
    source = data["bank"][:, found.selected_source_index]
    gate = data["handles"][:, found.selected_handle_index]
    assert np.all(
        np.linalg.norm(signal, axis=1)
        <= np.abs(gate) * np.linalg.norm(source, axis=1) + 1e-10
    )

    disabled_handles = data["handles"].copy()
    disabled_handles[:, found.selected_handle_index] = 0.0
    assert not found.candidate_signal(data["bank"], disabled_handles).any()
    unselected = replace(
        found, selected_handle_index=None, selected_source_index=None
    )
    assert not unselected.candidate_signal(
        data["bank"], data["handles"]
    ).any()

    bad_source = replace(found, selected_source_index=data["bank"].shape[1])
    with pytest.raises(ValueError, match="source index"):
        bad_source.candidate_signal(data["bank"], data["handles"])
    bad_handle = replace(found, selected_handle_index=data["handles"].shape[1])
    with pytest.raises(ValueError, match="handle index"):
        bad_handle.candidate_signal(data["bank"], data["handles"])
