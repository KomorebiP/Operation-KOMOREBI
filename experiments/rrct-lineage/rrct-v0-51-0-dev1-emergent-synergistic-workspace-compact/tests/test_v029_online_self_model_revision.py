import copy
import inspect
import json
from dataclasses import asdict, replace

import numpy as np
import pytest

from rrct.online_self_model_revision_experiment import (
    V029_ARMS,
    V029_OFFICIAL_SEEDS,
    V029_PILOT_SEEDS,
    V029_FROZEN_CONFIG,
    V029_ROUTE_RANK,
    V029_SCHEMA,
    V029_SOURCE_TAG,
    V029RunConfig,
    _agent,
    _anonymous_bank,
    _commitment_blind_bank_receipt,
    _hidden_route,
    _initial_world,
    _observation,
    _world_transition,
    aggregate_online_self_model_revision_results,
    run_online_self_model_revision_seed,
    run_v029_exploratory,
    run_v029_motor_yoked_pilot,
)


def _fast_config():
    # q=.80 is an explicit unit-test setting.  The production q=.99 path
    # retains 128 full and half null draws.
    return V029RunConfig(
        block_size=8,
        evidence_capacity=144,
        minimum_samples=144,
        fit_interval=8,
        null_permutations=5,
        half_null_permutations=5,
        null_quantile=0.80,
        revision_confirmations=1,
        revocation_confirmations=1,
        calibration_blocks=19,
        warmup_blocks=1,
        blackout_blocks=1,
        changed_blocks=(19, 19),
        disconnect_blocks=(19, 19),
        restore_blocks=(19, 19),
        change_episodes=1,
        stable_shock_episodes=1,
        bootstrap_replicates=20,
    )


def test_production_constants_are_block_complete_and_identifiable():
    config = V029_FROZEN_CONFIG
    assert config.block_size == 20
    assert config.minimum_samples == config.evidence_capacity == 240
    assert config.fit_interval == 20
    assert config.minimum_samples // 2 > 1 + 12 + 6 * 8 + 4
    assert config.minimum_samples // config.block_size == 12
    assert (config.minimum_samples // 2) % config.block_size == 0
    assert config.calibration_blocks == 14
    assert config.revocation_confirmations == 3
    assert config.scoring_grace_steps == 280
    assert min(config.changed_blocks) * config.block_size > config.scoring_grace_steps
    assert min(config.disconnect_blocks) * config.block_size > config.scoring_grace_steps
    assert min(config.restore_blocks) * config.block_size > config.scoring_grace_steps
    assert config.null_quantile == 0.99
    assert config.null_permutations == config.half_null_permutations == 128


def test_hidden_routes_are_permuted_rank_two_and_seed_counterbalanced():
    routes = [_hidden_route(seed, 0) for seed in V029_PILOT_SEEDS]
    assert {route.pair_a[0] for route in routes} == {0, 1, 2, 3}
    assert {route.pair_b[0] for route in routes} == {0, 1, 2, 3}
    assert len({route.pair_a[1] for route in routes}) == 4
    assert len({route.pair_b[1] for route in routes}) == 4
    assert all(route.pair_a != route.pair_b for route in routes)
    assert len({route.digest for route in routes}) == len(routes)
    for route in routes:
        assert sorted(route.source_order) == sorted(
            (
                "private_a",
                "one_step_echo",
                "policy_correlated",
                "private_b",
                "strong_exogenous",
                "other_agent",
            )
        )
        assert sorted(route.handle_order) == sorted(
            ("private_a", "one_step_echo", "policy_correlated", "private_b")
        )
        assert route.sensory_basis.shape == (12, 2)
        assert all(value.shape == (8, 2) for value in route.source_bases.values())


def test_official_pilot_and_exploratory_guards_fire_before_execution(monkeypatch):
    import rrct.online_self_model_revision_experiment as experiment

    def forbidden(*args, **kwargs):
        raise AssertionError("guard allowed experimental execution")

    monkeypatch.setattr(experiment, "_run_arm_episode", forbidden)
    with pytest.raises(PermissionError, match="official seeds are reserved"):
        run_online_self_model_revision_seed(V029_OFFICIAL_SEEDS[0])
    with pytest.raises(ValueError, match="pilot seeds require"):
        run_online_self_model_revision_seed(
            V029_PILOT_SEEDS[0], cohort="exploratory", exploratory=True
        )
    with pytest.raises(ValueError, match="unregistered seeds require"):
        run_online_self_model_revision_seed(5490)
    with pytest.raises(PermissionError, match="refuses pilot and official"):
        run_v029_exploratory(V029_PILOT_SEEDS[0], config=_fast_config())
    with pytest.raises(PermissionError, match="only declared.*pilot"):
        run_v029_motor_yoked_pilot(V029_OFFICIAL_SEEDS[0])


def test_atomic_receipt_uses_exact_same_observation_and_anonymous_source_tag():
    config = _fast_config()
    agent = _agent(9101, config, "adaptive")
    first_observation = np.linspace(-0.5, 0.6, 12)
    first = agent.step(first_observation, source="v029_online")
    bank = np.arange(48, dtype=np.float64).reshape(6, 8) / 48.0
    bound = agent.bind_causal_sources(bank, first.causal_commitment)
    outcome = np.linspace(0.7, -0.4, 12)
    second = agent.step(outcome, source="v029_online")

    assert np.array_equal(second.observation, outcome)
    assert second.source == "v029_online"
    assert second.causal_boundary_update_receipt is not None
    assert second.causal_boundary_update_receipt.transition_digest == bound.transition_digest
    assert second.causal_transition_digest == bound.transition_digest
    assert first.causal_commitment_digest == first.causal_commitment.digest


def test_anonymous_bank_draw_is_commitment_blind_and_replay_auditable():
    assert "commitment" not in inspect.signature(_anonymous_bank).parameters
    assert "handles" not in inspect.signature(_anonymous_bank).parameters
    route = _hidden_route(9109, 0)
    rng = np.random.default_rng(9110)
    world = _initial_world(rng)
    state = copy.deepcopy(rng.bit_generator.state)
    bank, _ = _anonymous_bank(rng, route, world, np.asarray([0.2, -0.3]), 1.0)
    assert _commitment_blind_bank_receipt(
        state, bank, route, world, np.asarray([0.2, -0.3]), 1.0
    )


def test_q99_production_world_acquires_rank_two_with_240_sample_window():
    """Exercise strict inference on the actual normalized-source world.

    Fourteen calibration blocks keep the second confirming fit inside the
    intact calibration loop, before any post-calibration control can apply.
    """

    seed = 5490  # Nonreserved exploratory seed; never pilot or official.
    assert seed not in V029_PILOT_SEEDS + V029_OFFICIAL_SEEDS
    config = replace(
        V029_FROZEN_CONFIG,
        evidence_capacity=240,
        minimum_samples=240,
        calibration_blocks=14,
    )
    assert config.null_quantile == 0.99
    assert config.null_permutations == config.half_null_permutations == 128

    route = _hidden_route(seed, 0)
    world_rng = np.random.default_rng(
        np.random.SeedSequence([seed, 0, 0x2902])
    )
    agent = _agent(seed, config, "adaptive")
    world = _initial_world(world_rng)
    observation = _observation(world, route)
    fit_states = []

    for _ in range(config.calibration_blocks * config.block_size):
        result = agent.step(observation, source=V029_SOURCE_TAG)
        receipt = result.causal_boundary_update_receipt
        if receipt is not None and receipt.fit_performed:
            fit_states.append(result.causal_boundary_state)
        bank, source_values = _anonymous_bank(
            world_rng,
            route,
            world,
            result.action,
            config.source_energy,
        )
        agent.bind_causal_sources(bank, result.causal_commitment)
        world, tracking = _world_transition(
            world,
            route,
            source_values,
            result.causal_commitment.handles,
            phase="route_a",
            public_pair=None,
            config=config,
            rng=world_rng,
        )
        observation = _observation(world, route)
        agent.register_executed_action(
            np.asarray(
                [tracking["executed_action_0"], tracking["executed_action_1"]]
            )
        )

    assert len(fit_states) == 2
    assert not fit_states[0].active
    acquired = fit_states[1]
    assert acquired.active
    assert (acquired.selected_handle_index, acquired.selected_source_index) == (
        route.pair_a
    )
    assert acquired.rank == V029_ROUTE_RANK

    internal_truth = (
        route.source_bases["private_a"] @ route.source_bases["private_a"].T
    )
    sensory_truth = route.sensory_basis @ route.sensory_basis.T
    assert np.trace(acquired.internal_projector @ internal_truth) / 2.0 > 0.98
    assert np.trace(acquired.sensory_projector @ sensory_truth) / 2.0 > 0.98


def test_no_broadcast_preserves_private_updater_evidence_but_has_no_public_port():
    config = _fast_config()
    adaptive = _agent(9127, config, "adaptive")
    no_broadcast = _agent(9127, config, "no_broadcast")
    observation = np.linspace(-0.2, 0.3, 12)
    outcome = np.linspace(0.4, -0.1, 12)
    bank = np.arange(48, dtype=np.float64).reshape(6, 8) / 23.0

    adaptive_first = adaptive.step(observation, source="v029_online")
    no_broadcast_first = no_broadcast.step(observation, source="v029_online")
    adaptive.bind_causal_sources(bank, adaptive_first.causal_commitment)
    no_broadcast.bind_causal_sources(bank, no_broadcast_first.causal_commitment)
    no_broadcast.set_ablations("causal_boundary_broadcast", reset=False)
    adaptive_second = adaptive.step(outcome, source="v029_online")
    no_broadcast_second = no_broadcast.step(outcome, source="v029_online")

    assert adaptive_second.causal_boundary_state.evidence_count == 1
    assert no_broadcast_second.causal_boundary_state.evidence_count == 1
    assert no_broadcast_second.causal_boundary_update_receipt is not None
    assert not no_broadcast_second.causal_boundary_workspace_drive.any()
    assert not no_broadcast_second.causal_boundary_proposal_selected
    assert no_broadcast.choose_causal_port() is None
    assert no_broadcast_second.causal_public_pair is None


def _part(seed):
    summary = {
        "seed": seed,
        "row_count": 1,
        "adaptive_private_accuracy": 0.8,
        "adaptive_public_port_accuracy": 0.7,
        "adaptive_tracking_utility": 0.6,
        "adaptive_internal_overlap": 0.75,
        "adaptive_sensory_overlap": 0.77,
        "no_broadcast_private_accuracy": 0.8,
        "no_broadcast_public_port_accuracy": 0.1,
        "no_broadcast_tracking_utility": 0.0,
        "counterfactual_broadcast_port_effect": 0.6,
        "counterfactual_broadcast_utility_effect": 0.6,
        "adaptive_route_b_private_accuracy": 0.8,
        "adaptive_route_b_public_port_accuracy": 0.7,
        "adaptive_route_b_tracking_utility": 0.6,
        "adaptive_disconnect_private_accuracy": 0.8,
        "adaptive_disconnect_public_port_accuracy": 0.7,
        "adaptive_disconnect_tracking_utility": 0.6,
        "adaptive_restore_a_private_accuracy": 0.8,
        "adaptive_restore_a_public_port_accuracy": 0.7,
        "adaptive_restore_a_tracking_utility": 0.6,
        "phase_metrics": {"adaptive": {"route_b": {"private_accuracy": 0.8}}},
        "integrity_pass": True,
        "adaptive_route_b_latency": 20.0,
        "adaptive_disconnect_latency": 20.0,
        "adaptive_restore_a_latency": 20.0,
    }
    row = {"seed": seed, "schema": V029_SCHEMA, "arm": "adaptive"}
    receipt = {
        "same_observation_all": True,
        "transition_chain_all": True,
        "source_energy_all": True,
        "commitment_blind_bank_all": True,
        "anonymous_source_tag_all": True,
        "terminal_reveal_ok": True,
    }
    return {
        "schema": V029_SCHEMA,
        "seed": seed,
        "rows": [row],
        "seed_summary": summary,
        "integrity_receipts": [receipt],
    }


def test_aggregator_requires_exact_seed_set_and_writes_hashes(tmp_path):
    parts = [_part(seed) for seed in V029_PILOT_SEEDS]
    with pytest.raises(ValueError, match="requires exact seeds"):
        aggregate_online_self_model_revision_results(
            parts[:-1],
            tmp_path / "missing",
            expected_seeds=V029_PILOT_SEEDS,
            status="pilot",
            recompute_seed_summaries=False,
            strict=False,
        )
    with pytest.raises(ValueError, match="requires exact seeds"):
        aggregate_online_self_model_revision_results(
            parts,
            tmp_path / "default_official",
            status="pilot",
            recompute_seed_summaries=False,
            strict=False,
        )
    result = aggregate_online_self_model_revision_results(
        parts,
        tmp_path / "exact",
        expected_seeds=V029_PILOT_SEEDS,
        bootstrap_replicates=30,
        bootstrap_seed=29,
        status="pilot",
        recompute_seed_summaries=False,
        strict=False,
    )
    assert result["summary"]["seeds"] == list(V029_PILOT_SEEDS)
    assert result["summary"]["integrity_pass"]
    for path in result["paths"].values():
        assert (tmp_path / "exact" / path.split("/")[-1]).is_file()
    hashes = json.loads(
        (tmp_path / "exact" / "v029_online_revision_sha256.json").read_text()
    )
    assert set(hashes) == {
        "v029_online_revision_rows.csv",
        "v029_online_revision_seed_summaries.csv",
        "v029_online_revision_integrity.json",
        "v029_online_revision_summary.json",
    }


def test_strict_aggregator_rejects_duplicate_or_missing_row_steps(tmp_path):
    parts = []
    for seed in V029_PILOT_SEEDS:
        rows = []
        receipts = []
        for episode, scenario in ((0, "route_change"), (1, "stable_shock")):
            for arm in V029_ARMS:
                rows.append(
                    {
                        "schema": V029_SCHEMA,
                        "seed": seed,
                        "episode": episode,
                        "arm": arm,
                        "scenario": scenario,
                        "step": 0,
                        "phase": "calibration",
                        "phase_step": 0,
                        "motor_execution_yoked_off": False,
                        "commitment_binary": True,
                        "oracle_truth_injected": False,
                        "oracle_counterfactual_only": True,
                    }
                )
                receipts.append(
                    {
                        "episode": episode,
                        "arm": arm,
                        "scenario": scenario,
                        "same_observation_all": True,
                        "transition_chain_all": True,
                        "source_energy_all": True,
                        "commitment_blind_bank_all": True,
                        "anonymous_source_tag_all": True,
                        "terminal_reveal_ok": True,
                        "terminal_commitment_unbound": True,
                        "terminal_fit_performed": arm != "frozen",
                        "terminal_revised": False,
                        "terminal_revoked": False,
                        "terminal_private_state_correct": True,
                        "terminal_private_model_digest": "0" * 64,
                        "frozen_control_applied": arm == "frozen",
                        "no_hidden_metadata_agent_api": True,
                        "motor_execution_yoked_off": False,
                    }
                )
        rows.append(dict(rows[0]))
        parts.append(
            {
                "schema": V029_SCHEMA,
                "seed": seed,
                "cohort": "pilot",
                "config": asdict(V029_FROZEN_CONFIG),
                "rows": rows,
                "seed_summary": {"seed": seed},
                "integrity_receipts": receipts,
            }
        )
    with pytest.raises(ValueError, match="duplicated, missing, or reordered"):
        aggregate_online_self_model_revision_results(
            parts,
            tmp_path / "strict_bad_steps",
            expected_seeds=V029_PILOT_SEEDS,
            status="pilot_strict_test",
            strict=True,
            recompute_seed_summaries=True,
        )
