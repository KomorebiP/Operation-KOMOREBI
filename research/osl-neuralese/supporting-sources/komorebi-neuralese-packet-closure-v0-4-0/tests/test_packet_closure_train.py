from __future__ import annotations

import copy
import itertools
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

from komorebi_neuralese.algebra import canonical_maps
from komorebi_neuralese.data import EpisodeGenerator
import komorebi_neuralese.packet_closure_train as packet_closure_train
from komorebi_neuralese.packet_closure_train import (
    PACKET_CLOSURE_ARMS,
    PACKET_CLOSURE_FOLLOWUP_ARMS,
    PRIMARY_PACKET_CLOSURE_ARMS,
    PacketClosureTrainConfig,
    build_packet_closure_model,
    compute_packet_closure_losses,
    construction_checkpoint_metadata,
    construction_minibank,
    d4_terminal_action_signatures,
    d4_terminal_reserved_mask,
    get_packet_closure_arm,
    make_v04_construction_bank,
    make_v04_stability_word_schedule,
    make_v04_suffix_plan,
    packet_closure_optimizer_parameter_groups,
    sample_v04_terminal_batch,
    state_dict_digest,
    terminal_firewall_policy_digest,
    train_packet_closure_arm,
    train_paired_packet_closure_panel,
)
from komorebi_neuralese.packet_models import (
    PolarIsometricTableOperatorRNN,
    ProjectiveLinearTableOperatorRNN,
)
from komorebi_neuralese.packet_training import relation_groups


def _config(**overrides: object) -> PacketClosureTrainConfig:
    values: dict[str, object] = {
        "seed": 53,
        "steps": 2,
        "batch_size": 4,
        "auxiliary_contexts": 1,
        "warmup_steps": 0,
        "checkpoints": 2,
    }
    values.update(overrides)
    return PacketClosureTrainConfig(**values)  # type: ignore[arg-type]


def test_arm_registry_is_complete_factorial_plus_controls_and_diagnostic() -> None:
    assert tuple(PACKET_CLOSURE_ARMS) == (
        "euclidean_supervised",
        "learned_metric_supervised",
        "euclidean_p111",
        "p000",
        "p001",
        "p010",
        "p011",
        "p100",
        "p101",
        "p110",
        "p111",
    )
    for bits in range(8):
        name = f"p{bits:03b}"
        spec = PACKET_CLOSURE_ARMS[name]
        assert spec.learn_metric
        assert spec.conformal and spec.switched_gain
        assert spec.composition == bool(bits & 4)
        assert spec.margin == bool(bits & 2)
        assert spec.delayed_return == bool(bits & 1)
    assert get_packet_closure_arm("full") == PACKET_CLOSURE_ARMS["p111"]
    assert get_packet_closure_arm("minus_return") == PACKET_CLOSURE_ARMS["p110"]
    diagnostic = PACKET_CLOSURE_ARMS["euclidean_p111"]
    assert not diagnostic.learn_metric
    assert all(
        (
            diagnostic.composition,
            diagnostic.margin,
            diagnostic.conformal,
            diagnostic.switched_gain,
            diagnostic.delayed_return,
        )
    )


def test_primary_cr_panel_is_separate_from_the_unchanged_legacy_registry() -> None:
    assert tuple(PACKET_CLOSURE_FOLLOWUP_ARMS) == (
        "euclidean_cr",
        "polar_supervised",
        "polar_cr",
    )
    assert PRIMARY_PACKET_CLOSURE_ARMS == (
        "euclidean_supervised",
        "euclidean_cr",
        "polar_supervised",
        "polar_cr",
    )
    assert not (set(PACKET_CLOSURE_FOLLOWUP_ARMS) & set(PACKET_CLOSURE_ARMS))
    for name in ("euclidean_cr", "polar_cr"):
        spec = get_packet_closure_arm(name)
        assert spec.composition and spec.delayed_return
        assert not spec.margin and not spec.conformal and not spec.switched_gain
    assert get_packet_closure_arm("polar_supervised").model_family == "polar"
    assert get_packet_closure_arm("polar_cr").model_family == "polar"


def test_training_bank_has_no_heldout_payload_and_posthoc_plan_is_group_disjoint() -> None:
    bank = make_v04_construction_bank()
    assert len(bank.construction) == 20
    assert not hasattr(bank, "heldout")
    assert () not in bank.construction
    metadata = construction_checkpoint_metadata(bank)
    serialized = json.dumps(metadata, sort_keys=True).lower()
    assert set(metadata) == {"plan_version", "construction_digest", "construction_words"}
    assert "heldout" not in serialized and "eval" not in serialized

    # Evaluation contents are instantiated separately, after a checkpoint can
    # be sealed. Whole induced-action groups remain on only one side.
    plan = make_v04_suffix_plan()
    assert plan.construction == bank.construction
    # The empty identity continuation is part of the audit so packet
    # membership also tests the captured prefix itself.
    assert len(plan.heldout) == 11
    assert () in plan.heldout
    construction_groups = set(relation_groups(plan, plan.construction))
    heldout_groups = set(relation_groups(plan, plan.heldout))
    assert construction_groups.isdisjoint(heldout_groups)
    transitions = torch.from_numpy(canonical_maps("d4")).long()
    identity = tuple(range(8))
    current = torch.arange(8)
    for action in (0, 0):
        current = transitions[action, current]
    assert heldout_groups == {identity, tuple(int(value) for value in current)}


def test_terminal_firewall_deterministically_rejects_reserved_composite_groups() -> None:
    first = sample_v04_terminal_batch(EpisodeGenerator(71), 64, 2)
    second = sample_v04_terminal_batch(EpisodeGenerator(71), 64, 2)
    assert first.accepted_count == second.accepted_count == 64
    assert first.rejected_count == second.rejected_count
    assert first.rejected_count > 0
    assert first.policy_digest == second.policy_digest == terminal_firewall_policy_digest()
    for name in (
        "tables",
        "maps",
        "op_slots",
        "canonical_ops",
        "start",
        "target",
        "intermediates",
        "canonical_to_slot",
        "phi",
    ):
        assert torch.equal(getattr(first.batch, name), getattr(second.batch, name))

    signatures = d4_terminal_action_signatures(first.batch.canonical_ops)
    transitions = torch.from_numpy(canonical_maps("d4")).long()
    identity = torch.arange(8)
    r2 = transitions[0, transitions[0]]
    assert not bool(((signatures == identity).all(dim=-1)).any())
    assert not bool(((signatures == r2).all(dim=-1)).any())
    assert not bool(d4_terminal_reserved_mask(first.batch.canonical_ops).any())


def test_terminal_firewall_exactly_matches_construction_groups_through_depth_four() -> None:
    rejection_counts: dict[int, int] = {}
    accepted: set[tuple[int, ...]] = set()
    for depth in range(1, 5):
        words = tuple(itertools.product((0, 1), repeat=depth))
        canonical_ops = torch.tensor(words, dtype=torch.long)
        reserved = d4_terminal_reserved_mask(canonical_ops)
        rejection_counts[depth] = int(reserved.sum())
        accepted.update(word for word, reject in zip(words, reserved.tolist()) if not reject)
    assert rejection_counts == {1: 0, 2: 2, 3: 0, 4: 8}
    assert accepted == set(make_v04_construction_bank().construction)

    # The firewall is an endpoint-group test, not a prefix ban: r,r is the
    # reserved r^2 action, while r,r,r is a valid final composite action.
    with_reserved_prefix = torch.tensor(((0, 0, 0),), dtype=torch.long)
    assert bool(d4_terminal_reserved_mask(with_reserved_prefix[:, :2]).item())
    assert not bool(d4_terminal_reserved_mask(with_reserved_prefix).item())


def test_seed71_terminal_firewall_protocol_lock() -> None:
    generator = EpisodeGenerator(40_071)
    length = int(generator.rng.integers(1, 5))
    sample = sample_v04_terminal_batch(generator, 8, length)
    assert length == 4
    assert sample.proposal_count == 16
    assert sample.accepted_count == 8
    assert sample.rejected_count == 8
    assert sample.identity_rejection_count == 5
    assert sample.r2_rejection_count == 3
    assert sample.proposal_digest == (
        "1caa33dc1acf9f1ec5aff92c6b55e1cedbcaad47c9e336942bc7cd74ddce23ea"
    )
    assert ["".join(map(str, word)) for word in sample.batch.canonical_ops.tolist()] == [
        "0010",
        "1110",
        "0100",
        "0010",
        "0010",
        "0100",
        "1101",
        "1110",
    ]

    # Verify slicing retained whole internally consistent rows.
    rows = torch.arange(8)
    current = sample.batch.start.clone()
    intermediates: list[torch.Tensor] = []
    for step in range(length):
        slots = sample.batch.op_slots[:, step]
        transition = sample.batch.maps[rows, slots]
        current = transition[rows, current]
        intermediates.append(current.clone())
    assert torch.equal(torch.stack(intermediates, dim=1), sample.batch.intermediates)
    assert torch.equal(current, sample.batch.target)


def test_every_terminal_batch_reaching_a_loss_is_firewalled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[torch.Tensor] = []
    original = packet_closure_train.compute_packet_closure_losses

    def checked_loss(*args: object, **kwargs: object):
        batch = args[1]
        assert isinstance(batch, packet_closure_train.EpisodeBatch)
        assert not bool(d4_terminal_reserved_mask(batch.canonical_ops).any())
        observed.append(batch.canonical_ops.detach().clone())
        return original(*args, **kwargs)

    monkeypatch.setattr(packet_closure_train, "compute_packet_closure_losses", checked_loss)
    config = _config(seed=71, steps=4, batch_size=8, checkpoints=1)
    trained = train_packet_closure_arm("euclidean_supervised", config)
    assert len(observed) == config.steps
    assert trained.terminal_candidates_accepted == config.steps * config.batch_size
    assert trained.terminal_candidates_rejected > 0
    assert trained.terminal_firewall_policy_digest == terminal_firewall_policy_digest()


def test_direct_loss_call_fails_closed_on_reserved_terminal_groups() -> None:
    config = _config(steps=1)
    model = build_packet_closure_model(config, "euclidean_supervised")
    bank = make_v04_construction_bank()
    words = tuple(itertools.product((0, 1), repeat=4))
    canonical_ops = torch.tensor(words, dtype=torch.long)
    signatures = d4_terminal_action_signatures(canonical_ops)
    transitions = torch.from_numpy(canonical_maps("d4")).long()
    identity = torch.arange(8)
    r2 = transitions[0, transitions[0]]
    identity_word = words[int(((signatures == identity).all(dim=-1)).nonzero()[0])]
    r2_word = words[int(((signatures == r2).all(dim=-1)).nonzero()[0])]
    for word in (identity_word, r2_word):
        batch = EpisodeGenerator(97).sample(4, 4, family="d4", canonical_word=word)
        with pytest.raises(ValueError, match="terminal endpoint firewall"):
            compute_packet_closure_losses(
                model,
                batch,
                bank,
                "euclidean_supervised",
                config,
                step=0,
            )

    accepted_batch = sample_v04_terminal_batch(EpisodeGenerator(1101), 4, 3).batch
    poisoned_bank = replace(
        bank,
        construction=bank.construction + ((0, 0),),
    )
    with pytest.raises(ValueError, match="construction endpoint firewall"):
        compute_packet_closure_losses(
            model,
            accepted_batch,
            poisoned_bank,
            "euclidean_supervised",
            config,
            step=0,
        )


def test_construction_minibanks_cycle_without_unequal_exposure() -> None:
    bank = make_v04_construction_bank()
    selections = [
        construction_minibank(bank, step=step, words_per_step=4)[1]
        for step in range(5)
    ]
    assert selections == [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (8, 9, 10, 11),
        (12, 13, 14, 15),
        (16, 17, 18, 19),
    ]
    assert sorted(index for selection in selections for index in selection) == list(range(20))
    for step, indices in enumerate(selections):
        mini, repeated = construction_minibank(bank, step=step, words_per_step=4)
        assert repeated == indices
        assert mini.construction == tuple(bank.construction[index] for index in indices)
        assert not hasattr(mini, "heldout")


def test_switched_schedule_has_fixed_depths_and_only_construction_actions() -> None:
    bank = make_v04_construction_bank()
    schedule = make_v04_stability_word_schedule(bank)
    assert set(map(len, schedule)) == {2, 4, 8}
    transitions = torch.tensor(bank.canonical_transitions, dtype=torch.long)
    allowed = set(bank.construction_group_signatures)
    signatures = set()
    for word in schedule:
        state = torch.arange(8)
        for action in word:
            state = transitions[action, state]
            assert tuple(int(value) for value in state) in allowed
        signatures.add(tuple(int(value) for value in state))
    assert signatures.issubset(allowed)


def test_all_arms_share_direct_model_initialization_and_only_control_freezes_metric() -> None:
    config = _config()
    euclidean = build_packet_closure_model(config, "euclidean_supervised")
    learned = build_packet_closure_model(config, "learned_metric_supervised")
    full = build_packet_closure_model(config, "p111")
    assert isinstance(euclidean, ProjectiveLinearTableOperatorRNN)
    assert state_dict_digest(euclidean) == state_dict_digest(learned) == state_dict_digest(full)
    assert not euclidean.metric_log_diagonal.requires_grad
    assert not euclidean.metric_strict_lower.requires_grad
    assert learned.metric_log_diagonal.requires_grad
    assert learned.metric_strict_lower.requires_grad
    assert torch.equal(euclidean.invariant_metric(), torch.eye(12))


def test_primary_raw_and_polar_models_share_the_exact_initial_state_dict() -> None:
    config = _config()
    raw_supervised = build_packet_closure_model(config, "euclidean_supervised")
    raw_cr = build_packet_closure_model(config, "euclidean_cr")
    polar_supervised = build_packet_closure_model(config, "polar_supervised")
    polar_cr = build_packet_closure_model(config, "polar_cr")
    assert type(raw_supervised) is ProjectiveLinearTableOperatorRNN
    assert type(raw_cr) is ProjectiveLinearTableOperatorRNN
    assert type(polar_supervised) is PolarIsometricTableOperatorRNN
    assert type(polar_cr) is PolarIsometricTableOperatorRNN
    assert len(
        {
            state_dict_digest(raw_supervised),
            state_dict_digest(raw_cr),
            state_dict_digest(polar_supervised),
            state_dict_digest(polar_cr),
        }
    ) == 1
    assert not polar_supervised.metric_log_diagonal.requires_grad
    assert not polar_supervised.metric_strict_lower.requires_grad

    batch = sample_v04_terminal_batch(EpisodeGenerator(71), 8, 3).batch
    trace = polar_supervised.run(batch.tables, batch.op_slots, batch.start)
    assert trace.operator_codes is not None
    operators = trace.operator_codes
    identity = torch.eye(12, dtype=operators.dtype)
    defects = operators.transpose(-1, -2) @ operators - identity
    assert float(
        torch.linalg.matrix_norm(defects, ord="fro", dim=(-2, -1)).max().detach()
    ) < 1e-5


@pytest.mark.parametrize("name", ["euclidean_cr", "polar_cr"])
def test_cr_arms_add_only_composition_and_exact_return(name: str) -> None:
    config = _config(steps=1)
    model = build_packet_closure_model(config, name)
    batch = sample_v04_terminal_batch(EpisodeGenerator(83), 4, 3).batch
    result = compute_packet_closure_losses(
        model,
        batch,
        make_v04_construction_bank(),
        name,
        config,
        step=0,
    )
    assert set(result.active_components) == {
        "terminal",
        "construction_ce",
        "anchor",
        "composition",
        "delayed_return",
    }
    assert float(result.margin.detach()) == 0.0
    assert float(result.conformal.detach()) == 0.0
    assert float(result.switched_gain.detach()) == 0.0
    assert result.nuisance_rank == 4
    result.total.backward()
    gradients = [parameter.grad for parameter in model.parameters() if parameter.requires_grad]
    assert gradients and all(gradient is not None for gradient in gradients)
    assert all(bool(torch.isfinite(gradient).all()) for gradient in gradients if gradient is not None)


def test_metric_uses_a_separate_tenfold_slower_optimizer_group() -> None:
    config = _config(learning_rate=3e-3, metric_learning_rate_scale=0.1)
    learned = build_packet_closure_model(config, "p111")
    learned_groups = packet_closure_optimizer_parameter_groups(learned, config)
    assert [group["group_name"] for group in learned_groups] == ["task", "metric"]
    assert [group["lr"] for group in learned_groups] == pytest.approx([3e-3, 3e-4])
    metric_ids = {
        id(learned.metric_log_diagonal),
        id(learned.metric_strict_lower),
    }
    assert {id(parameter) for parameter in learned_groups[1]["params"]} == metric_ids
    assert not ({id(parameter) for parameter in learned_groups[0]["params"]} & metric_ids)

    euclidean = build_packet_closure_model(config, "euclidean_p111")
    euclidean_groups = packet_closure_optimizer_parameter_groups(euclidean, config)
    assert len(euclidean_groups) == 1
    assert euclidean_groups[0]["group_name"] == "task"
    assert euclidean_groups[0]["lr"] == pytest.approx(3e-3)


def test_full_loss_uses_rank_four_complement_and_has_finite_gradients() -> None:
    config = _config(steps=1)
    model = build_packet_closure_model(config, "p111")
    batch = EpisodeGenerator(71).sample(4, 3, family="d4")
    bank = make_v04_construction_bank()
    result = compute_packet_closure_losses(model, batch, bank, "p111", config, step=0)
    assert result.nuisance_rank == 4
    assert result.construction_word_indices == (0, 1, 2, 3)
    assert set(result.active_components) == {
        "terminal",
        "construction_ce",
        "anchor",
        "composition",
        "margin",
        "conformal",
        "switched_gain",
        "delayed_return",
    }
    for value in (
        result.total,
        result.anchor,
        result.composition,
        result.margin,
        result.conformal,
        result.switched_gain,
        result.delayed_return,
        result.p_to_q_norm,
        result.q_to_p_norm,
        result.q_to_q_norm,
        result.return_fraction,
    ):
        assert bool(torch.isfinite(value.detach()))
    result.total.backward()
    gradients = [parameter.grad for parameter in model.parameters() if parameter.requires_grad]
    assert gradients and all(gradient is not None for gradient in gradients)
    assert all(bool(torch.isfinite(gradient).all()) for gradient in gradients if gradient is not None)


@pytest.mark.parametrize(
    ("name", "missing"),
    [
        ("p011", "composition"),
        ("p101", "margin"),
        ("p110", "delayed_return"),
    ],
)
def test_named_leave_one_out_arms_remove_only_the_intended_factor(
    name: str,
    missing: str,
) -> None:
    config = _config(steps=1)
    base = build_packet_closure_model(config, "p111")
    model = copy.deepcopy(base)
    batch = EpisodeGenerator(83).sample(4, 3, family="d4")
    bank = make_v04_construction_bank()
    result = compute_packet_closure_losses(model, batch, bank, name, config, step=1)
    assert missing not in result.active_components
    expected = {
        "terminal",
        "construction_ce",
        "anchor",
        "composition",
        "margin",
        "conformal",
        "switched_gain",
        "delayed_return",
    } - {missing}
    assert set(result.active_components) == expected


def test_paired_short_training_reuses_initialization_and_episode_stream() -> None:
    config = _config()
    results = train_paired_packet_closure_panel(
        config,
        arm_names=(
            "euclidean_supervised",
            "learned_metric_supervised",
            "p000",
            "p111",
        ),
    )
    assert len({result.initial_state_digest for result in results.values()}) == 1
    assert len({result.episode_stream_digest for result in results.values()}) == 1
    assert len({result.terminal_firewall_policy_digest for result in results.values()}) == 1
    assert len({result.terminal_proposal_stream_digest for result in results.values()}) == 1
    assert len({result.terminal_proposal_count for result in results.values()}) == 1
    assert len({result.terminal_candidates_accepted for result in results.values()}) == 1
    assert len({result.terminal_candidates_rejected for result in results.values()}) == 1
    assert len({result.terminal_identity_rejections for result in results.values()}) == 1
    assert len({result.terminal_r2_rejections for result in results.values()}) == 1
    assert len({result.construction_digest for result in results.values()}) == 1
    assert next(iter(results.values())).terminal_candidates_accepted == (
        config.steps * config.batch_size
    )
    representative = next(iter(results.values()))
    assert representative.terminal_proposal_count == (
        representative.terminal_candidates_accepted
        + representative.terminal_candidates_rejected
    )
    assert representative.terminal_candidates_rejected == (
        representative.terminal_identity_rejections
        + representative.terminal_r2_rejections
    )
    assert representative.trajectory[-1]["terminal_firewall_policy_digest"] == (
        representative.terminal_firewall_policy_digest
    )
    assert representative.trajectory[-1]["terminal_candidates_accepted_cumulative"] == (
        representative.terminal_candidates_accepted
    )
    assert results["euclidean_supervised"].trainable_parameter_count == 9_408
    assert results["learned_metric_supervised"].trainable_parameter_count == 9_486

    first = train_packet_closure_arm("p111", config)
    second = train_packet_closure_arm("p111", config)
    assert first.initial_state_digest == second.initial_state_digest
    assert first.episode_stream_digest == second.episode_stream_digest
    assert first.final_state_digest == second.final_state_digest
    assert first.trajectory == second.trajectory


def test_primary_raw_polar_panel_pairs_initialization_and_firewalled_stream() -> None:
    config = _config(seed=71, steps=1, batch_size=4, checkpoints=1)
    results = train_paired_packet_closure_panel(
        config,
        arm_names=PRIMARY_PACKET_CLOSURE_ARMS,
    )
    assert tuple(results) == PRIMARY_PACKET_CLOSURE_ARMS
    assert len({result.initial_state_digest for result in results.values()}) == 1
    assert len({result.episode_stream_digest for result in results.values()}) == 1
    assert len({result.terminal_proposal_stream_digest for result in results.values()}) == 1
    assert len({result.terminal_candidates_accepted for result in results.values()}) == 1
    assert len({result.terminal_candidates_rejected for result in results.values()}) == 1
    assert len({result.terminal_firewall_policy_digest for result in results.values()}) == 1
    assert len({result.shared_initialization_digest for result in results.values()}) == 1
    assert {result.terminal_candidates_accepted for result in results.values()} == {4}


def test_invalid_hidden_width_and_construction_depth_fail_closed() -> None:
    with pytest.raises(ValueError, match="hidden_dim == 12"):
        _config(hidden_dim=8).validate()
    with pytest.raises(ValueError, match="auxiliary_max_depth == 4"):
        _config(auxiliary_max_depth=3).validate()
    with pytest.raises(ValueError, match="metric_learning_rate_scale"):
        _config(metric_learning_rate_scale=0.0).validate()


def test_training_api_rejects_a_plan_that_contains_evaluation_words() -> None:
    config = _config(steps=1)
    model = build_packet_closure_model(config, "p000")
    batch = EpisodeGenerator(97).sample(4, 2, family="d4")
    with pytest.raises(TypeError, match="never an evaluation plan"):
        compute_packet_closure_losses(
            model,
            batch,
            make_v04_suffix_plan(),  # type: ignore[arg-type]
            "p000",
            config,
            step=0,
        )
