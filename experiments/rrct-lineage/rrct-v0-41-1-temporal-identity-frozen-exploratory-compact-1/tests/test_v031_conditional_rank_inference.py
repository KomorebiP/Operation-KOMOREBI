import copy

import numpy as np
import pytest

import rrct.causal_boundary as boundary
from rrct.causal_boundary import CausalBoundaryConfig, OnlineCausalSelfBoundary


def _conditional_config(**changes):
    values = {
        "observation_dim": 6,
        "process_dim": 4,
        "source_count": 3,
        "handle_count": 2,
        "evidence_capacity": 240,
        "minimum_samples": 240,
        "fit_interval": 240,
        "commitment_block_size": 20,
        "ridge": 0.35,
        "null_permutations": 24,
        "half_null_permutations": 24,
        "null_quantile": 0.95,
        "higher_mode_null": (
            "cross_fitted_reduced_rank_randomization_bootstrap"
        ),
        "revision_confirmations": 2,
        "revocation_confirmations": 2,
        "confidence_decay": 0.60,
        "seed": 310031,
    }
    values.update(changes)
    return CausalBoundaryConfig(**values)


def _objective(x, y, coefficient, ridge):
    residual = y - x @ coefficient
    return float(
        np.sum(residual * residual) + ridge * np.sum(coefficient * coefficient)
    )


def test_reduced_rank_ridge_truncation_matches_penalized_improvement():
    rng = np.random.default_rng(3101)
    x = rng.normal(size=(90, 4))
    y = rng.normal(size=(90, 6))
    ridge = 0.45
    rank_one, singular, unrestricted = boundary._reduced_rank_ridge_fit(
        x, y, ridge, 1
    )
    rank_two, replay_singular, replay_unrestricted = (
        boundary._reduced_rank_ridge_fit(x, y, ridge, 2)
    )

    assert np.linalg.matrix_rank(rank_one) == 1
    assert np.linalg.matrix_rank(rank_two) == 2
    assert np.allclose(singular, replay_singular)
    assert np.allclose(unrestricted, replay_unrestricted)
    improvement = _objective(x, y, rank_one, ridge) - _objective(
        x, y, rank_two, ridge
    )
    assert improvement == pytest.approx(singular[1] ** 2, rel=1e-10, abs=1e-10)
    assert boundary._rank_increment_statistic(x, y, ridge, 1) == pytest.approx(
        singular[1] ** 2
    )


def test_finite_monte_carlo_boundary_uses_strict_order_statistic():
    null = np.arange(9, dtype=np.float64)
    threshold = boundary._monte_carlo_threshold(null, 0.90)
    assert threshold == 8.0
    assert not 8.0 > threshold
    assert np.nextafter(8.0, np.inf) > threshold
    # The equivalent add-one p-value lies on a floating-point representation
    # boundary for this otherwise valid configuration, so admission must use
    # the exact order-statistic comparison above rather than p <= 1 - q.
    boundary_p = 1.0 / 10.0
    assert boundary_p > 1.0 - 0.90


def test_conditional_folds_are_complete_disjoint_and_nonce_determined():
    config = _conditional_config()
    evidence = []
    for nonce in range(config.minimum_samples):
        evidence.append(
            boundary._Evidence(
                observation=np.zeros(config.observation_dim),
                process_bank=np.zeros(
                    (config.source_count, config.process_dim)
                ),
                handles=np.zeros(config.handle_count),
                next_observation=np.zeros(config.observation_dim),
                commitment_time=nonce,
                commitment_nonce=nonce,
                commitment_digest=f"c{nonce}",
                transition_digest=f"t{nonce}",
                reveal_time=nonce + 1,
                outcome_digest=f"o{nonce}",
            )
        )

    proposal, confirmation_a, confirmation_b = (
        boundary._partition_inference_evidence(evidence, config)
    )
    assert [len(proposal), len(confirmation_a), len(confirmation_b)] == [
        120,
        60,
        60,
    ]
    nonce_sets = [
        {item.commitment_nonce for item in fold}
        for fold in (proposal, confirmation_a, confirmation_b)
    ]
    assert not nonce_sets[0] & nonce_sets[1]
    assert not nonce_sets[0] & nonce_sets[2]
    assert not nonce_sets[1] & nonce_sets[2]
    assert set.union(*nonce_sets) == set(range(240))


def test_conditional_partition_uses_newest_four_block_multiple():
    config = _conditional_config(
        evidence_capacity=480,
        minimum_samples=240,
    )
    evidence = []
    for nonce in range(280):
        evidence.append(
            boundary._Evidence(
                observation=np.zeros(config.observation_dim),
                process_bank=np.zeros(
                    (config.source_count, config.process_dim)
                ),
                handles=np.zeros(config.handle_count),
                next_observation=np.zeros(config.observation_dim),
                commitment_time=nonce,
                commitment_nonce=nonce,
                commitment_digest=f"c{nonce}",
                transition_digest=f"t{nonce}",
                reveal_time=nonce + 1,
                outcome_digest=f"o{nonce}",
            )
        )
    proposal, confirmation_a, confirmation_b = (
        boundary._partition_inference_evidence(evidence, config)
    )
    retained = proposal + confirmation_a + confirmation_b
    assert [len(proposal), len(confirmation_a), len(confirmation_b)] == [
        120,
        60,
        60,
    ]
    assert retained[0].commitment_nonce == 40
    assert retained[-1].commitment_nonce == 279


def test_conditional_configuration_rejects_underpowered_folds():
    with pytest.raises(ValueError, match="multiple of four"):
        _conditional_config(evidence_capacity=200, minimum_samples=200)
    with pytest.raises(ValueError, match="more rows"):
        CausalBoundaryConfig(
            observation_dim=12,
            process_dim=8,
            source_count=6,
            handle_count=4,
            evidence_capacity=240,
            minimum_samples=240,
            fit_interval=20,
            commitment_block_size=20,
            null_permutations=24,
            half_null_permutations=24,
            null_quantile=0.95,
        )


def test_null_imputation_moves_a_rank_one_surface_with_reassignment():
    config = _conditional_config()
    rng = np.random.default_rng(3103)
    count = 60
    observation = rng.normal(size=(count, config.observation_dim))
    bank = rng.normal(
        size=(count, config.source_count, config.process_dim)
    )
    handles = rng.integers(0, 2, size=(count, config.handle_count)).astype(float)
    reassigned = handles.copy()
    reassigned[:, 1] = reassigned[::-1, 1]
    effect = np.outer(
        np.asarray([1.0, -0.3, 0.2, 0.1]),
        np.asarray([0.8, -0.4, 0.2, 0.1, 0.0, -0.2]),
    )
    nuisance_columns = (
        1
        + config.observation_dim
        + config.source_count * config.process_dim
        + config.handle_count
    )
    nuisance_coefficient = np.zeros(
        (nuisance_columns, config.observation_dim)
    )
    first = boundary._null_preserving_outcome(
        observation,
        bank,
        handles,
        np.zeros((count, config.observation_dim)),
        effect,
        nuisance_coefficient,
        config,
        selected_pair=(1, 2),
    )
    second = boundary._null_preserving_outcome(
        observation,
        bank,
        reassigned,
        np.zeros((count, config.observation_dim)),
        effect,
        nuisance_coefficient,
        config,
        selected_pair=(1, 2),
    )
    expected_first = handles[:, 1, None] * (bank[:, 2] @ effect)
    expected_second = reassigned[:, 1, None] * (bank[:, 2] @ effect)
    assert np.allclose(first, expected_first)
    assert np.allclose(second, expected_second)
    assert not np.allclose(first, second)
    assert np.linalg.matrix_rank(effect) == 1


def test_null_imputation_replays_observed_assignment_to_roundoff():
    config = _conditional_config()
    rng = np.random.default_rng(3105)
    count = 60
    observation = rng.normal(size=(count, config.observation_dim))
    bank = rng.normal(size=(count, config.source_count, config.process_dim))
    handles = rng.integers(
        0, 2, size=(count, config.handle_count)
    ).astype(np.float64)
    next_observation = rng.normal(size=(count, config.observation_dim))
    effect = np.outer(rng.normal(size=config.process_dim), rng.normal(
        size=config.observation_dim
    ))
    nuisance, raw_interactions = boundary._raw_designs(
        observation, bank, handles, config
    )
    nuisance_coefficient = rng.normal(
        size=(nuisance.shape[1], config.observation_dim)
    )
    pair = (1, 2)
    residual = (
        next_observation
        - nuisance @ nuisance_coefficient
        - raw_interactions[:, pair[0], pair[1]] @ effect
    )
    replay = boundary._null_preserving_outcome(
        observation,
        bank,
        handles,
        residual,
        effect,
        nuisance_coefficient,
        config,
        selected_pair=pair,
    )
    assert np.allclose(replay, next_observation, rtol=1e-14, atol=1e-14)
    replay_outcome, replay_interactions = boundary._residual_problem(
        observation, bank, handles, replay, config
    )
    observed_outcome, observed_interactions = boundary._residual_problem(
        observation, bank, handles, next_observation, config
    )
    assert boundary._rank_increment_statistic(
        replay_interactions[:, pair[0], pair[1]],
        replay_outcome,
        config.ridge,
        1,
    ) == pytest.approx(
        boundary._rank_increment_statistic(
            observed_interactions[:, pair[0], pair[1]],
            observed_outcome,
            config.ridge,
            1,
        ),
        rel=1e-13,
        abs=1e-13,
    )


def _run_rank_world(
    rank,
    *,
    seed,
    config=None,
    steps=None,
    return_model=False,
):
    config = _conditional_config() if config is None else config
    model = OnlineCausalSelfBoundary(config)
    rng = np.random.default_rng(seed)
    internal, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    sensory, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    strengths = np.asarray([4.0, 2.5])[:rank]
    effect = (
        internal[:, :rank] @ np.diag(strengths) @ sensory[:, :rank].T
        if rank
        else np.zeros((4, 6))
    )
    exogenous = 3.0 * internal[:, 2:4] @ sensory[:, 2:4].T
    observation = np.zeros(6)
    receipt = None
    run_steps = config.minimum_samples if steps is None else int(steps)
    for time in range(run_steps):
        commitment = model.commit_handles(time=time)
        bank = rng.normal(size=(3, 4))
        bank /= np.linalg.norm(bank, axis=1, keepdims=True)
        bound = model.bind_sources(
            observation,
            bank,
            commitment_digest=commitment.digest,
            time=time,
        )
        next_observation = (
            0.42 * observation
            + commitment.handles[1] * bank[2] @ effect
            + bank[0] @ exogenous
            + rng.normal(0.0, 0.035, size=6)
        )
        receipt = model.reveal_outcome(
            next_observation,
            transition_digest=bound.transition_digest,
            time=time + 1,
        )
        observation = next_observation
    if return_model:
        return model, receipt
    return receipt


def test_cross_fitted_inference_rejects_extra_mode_and_detects_real_one():
    rank_one = _run_rank_world(1, seed=7001)
    rank_two = _run_rank_world(2, seed=7001)
    no_route = _run_rank_world(0, seed=7001)

    assert (
        rank_one.fit_handle_index,
        rank_one.fit_source_index,
        rank_one.fit_rank,
    ) == (1, 2, 1)
    assert (
        rank_two.fit_handle_index,
        rank_two.fit_source_index,
        rank_two.fit_rank,
    ) == (1, 2, 2)
    assert no_route.fit_handle_index is None
    assert no_route.fit_source_index is None
    assert no_route.fit_rank == 0
    assert rank_one.fit_confidence > 0.0
    assert rank_two.fit_confidence > 0.0


def test_global_higher_mode_screen_remains_available_only_as_comparator():
    conditional = _conditional_config()
    comparator = _conditional_config(higher_mode_null="global_sharp_null")
    assert conditional.higher_mode_null.startswith("cross_fitted")
    assert comparator.higher_mode_null == "global_sharp_null"


def test_conditional_intermediate_fit_trims_to_newest_four_block_multiple():
    config = _conditional_config(
        evidence_capacity=480,
        minimum_samples=240,
        fit_interval=40,
        structural_confirmation_interval=40,
    )
    model, receipt = _run_rank_world(
        1,
        seed=7011,
        config=config,
        steps=280,
        return_model=True,
    )
    assert receipt.fit_performed
    assert (receipt.fit_handle_index, receipt.fit_source_index, receipt.fit_rank) == (
        1,
        2,
        1,
    )
    assert receipt.acquired
    assert (model.state.selected_handle_index, model.state.selected_source_index) == (
        1,
        2,
    )


def test_conditional_snapshot_and_deepcopy_continue_exactly():
    config = _conditional_config()
    model, _ = _run_rank_world(
        1,
        seed=7013,
        config=config,
        return_model=True,
    )
    rng = np.random.default_rng(7015)
    observation = rng.normal(size=config.observation_dim)
    bank = rng.normal(size=(config.source_count, config.process_dim))
    commitment = model.commit_handles(time=config.minimum_samples)
    bound = model.bind_sources(
        observation,
        bank,
        commitment_digest=commitment.digest,
        time=config.minimum_samples,
    )
    snapshot = model.snapshot()
    restored = OnlineCausalSelfBoundary(config)
    restored.load_snapshot(snapshot)
    cloned = copy.deepcopy(model)
    next_observation = rng.normal(size=config.observation_dim)
    receipts = [
        item.reveal_outcome(
            next_observation,
            transition_digest=bound.transition_digest,
            time=config.minimum_samples + 1,
        )
        for item in (model, restored, cloned)
    ]
    assert receipts[0] == receipts[1] == receipts[2]
    assert model.snapshot()["digest"] == restored.snapshot()["digest"]
    assert model.snapshot()["digest"] == cloned.snapshot()["digest"]


def test_rehashed_snapshot_cannot_change_conditional_method():
    config = _conditional_config()
    model = OnlineCausalSelfBoundary(config)
    snapshot = model.snapshot()
    snapshot["config"]["higher_mode_null"] = "global_sharp_null"
    payload = copy.deepcopy(snapshot)
    payload.pop("digest")
    snapshot["digest"] = boundary._digest(payload)
    with pytest.raises(ValueError, match="config does not match"):
        model.load_snapshot(snapshot)
