from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import pytest
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.algebra import D4_RELATIONS, N_STATES, canonical_maps
from komorebi_neuralese.ambient_packets import (
    SuffixSplit,
    enumerate_suffixes,
    split_suffixes_for_validation,
    suffix_transition_signature,
)
from komorebi_neuralese.data import EpisodeBatch, EpisodeGenerator
from komorebi_neuralese.models import RecurrentOperatorModel
from komorebi_neuralese.packet_models import PolarIsometricTableOperatorRNN
from komorebi_neuralese.packet_closure_eval import (
    AmbientComplementCausalAssay,
    FrozenHeldoutBank,
    HardPolarGeometryAudit,
    HeldoutPacketEvaluation,
    evaluate_ambient_complement_causality,
    evaluate_hard_polar_geometry,
    evaluate_heldout_packet,
    evaluate_null_loop_retention,
    evaluate_packet_closure_arm,
    evaluate_sampled_switched_gain,
    evaluate_structured_deep_accuracy,
    factorial_effect_summaries,
    factorial_effect_summary,
    freeze_heldout_bank,
    sample_switch_words,
)


class ExactTableProjectiveModel(RecurrentOperatorModel):
    """Exact finite table executor expressed in the visible one-hot chart."""

    model_name = "test_exact_table_projective"

    def __init__(self) -> None:
        super().__init__()
        self.state_embedding = nn.Embedding(N_STATES, N_STATES)
        self.decoder = nn.Linear(N_STATES, N_STATES, bias=False)
        with torch.no_grad():
            self.state_embedding.weight.copy_(torch.eye(N_STATES))
            self.decoder.weight.copy_(torch.eye(N_STATES))

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return tables.transpose(-1, -2)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return self.state_embedding(start)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        updated = torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)
        return torch.nn.functional.normalize(updated, dim=-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.decoder(hidden)


def _transitions(family: str = "d4") -> torch.Tensor:
    return torch.from_numpy(canonical_maps(family)).long()


def _relation_split(transitions: torch.Tensor, max_depth: int = 4) -> SuffixSplit:
    words = enumerate_suffixes(int(transitions.shape[0]), max_depth)
    return split_suffixes_for_validation(
        words,
        heldout_fraction=0.25,
        seed=371,
        equivalence_key=lambda word: suffix_transition_signature(transitions, word),
        stratify_by_depth=False,
        keep_empty_in_construction=True,
    )


def _batch(family: str, *, seed: int, examples: int = 12, length: int = 12) -> EpisodeBatch:
    return EpisodeGenerator(seed).sample(examples, length, family=family)


def test_exact_table_model_passes_relation_grouped_packet_and_deep_accuracy() -> None:
    model = ExactTableProjectiveModel()
    transitions = _transitions("d4")
    split = _relation_split(transitions)
    packet = evaluate_heldout_packet(
        model,
        _batch("d4", seed=11, length=17),
        split,
        transitions,
    )
    assert packet.membership_fraction == 1.0
    assert packet.word_weighted_membership_fraction == 1.0
    assert packet.macro_relation_group_membership_fraction == 1.0
    assert packet.bank.split_verified
    assert packet.to_dict()["minimum_margin"]["minimum"] > 0

    deep = evaluate_structured_deep_accuracy(
        model,
        {
            "d4": _batch("d4", seed=13, length=64),
            "c8": _batch("c8", seed=17, length=64),
            "mixed_cycle": _batch("mixed_cycle", seed=19, length=64),
        },
    )
    assert deep.pooled_accuracy == 1.0
    assert deep.macro_family_accuracy == 1.0
    assert deep.minimum_family_accuracy == 1.0


def test_nonfinite_deep_logits_are_counted_as_incorrect() -> None:
    model = ExactTableProjectiveModel()
    with torch.no_grad():
        model.decoder.weight.fill_(torch.nan)
    deep = evaluate_structured_deep_accuracy(
        model,
        {"d4": _batch("d4", seed=21, examples=7, length=5)},
    )
    assert deep.pooled_accuracy == 0.0
    assert deep.per_family["d4"]["finite_fraction"] == 0.0


def test_relation_group_macro_is_not_weighted_by_number_of_words() -> None:
    signatures = ((0, 1), (0, 1), (0, 1), (1, 0))
    bank = FrozenHeldoutBank(
        words=((0,), (0, 0), (0, 0, 0), (1,)),
        relation_signatures=signatures,
        fingerprint="synthetic",
        split_verified=True,
    )
    inside = torch.tensor([[True, True, True, False]])
    result = HeldoutPacketEvaluation(
        bank=bank,
        minimum_margin_by_suffix=torch.tensor([[0.4, 0.3, 0.2, -0.1]]),
        inside_by_suffix=inside,
        target_by_suffix=torch.zeros((1, 4), dtype=torch.long),
        prediction_by_suffix=torch.tensor([[0, 0, 0, 1]]),
        boundary_tolerance=0.0,
    )
    assert result.word_weighted_membership_fraction == 0.75
    assert result.macro_relation_group_membership_fraction == 0.5
    assert result.membership_fraction == 0.0


def test_split_and_episode_semantics_fail_closed() -> None:
    d4 = _transitions("d4")
    split = _relation_split(d4)
    bad = SuffixSplit(
        construction=split.construction + (split.heldout[0],),
        heldout=split.heldout,
        construction_group_keys=split.construction_group_keys,
        heldout_group_keys=split.heldout_group_keys,
        seed=split.seed,
    )
    with pytest.raises(ValueError, match="leakage"):
        freeze_heldout_bank(bad, d4)

    with pytest.raises(ValueError, match="realize canonical_transitions"):
        c8 = _transitions("c8")
        evaluate_heldout_packet(
            ExactTableProjectiveModel(),
            _batch("d4", seed=23),
            _relation_split(c8),
            c8,
        )


def test_exact_null_loop_preserves_heldout_packet_and_nonnull_is_rejected() -> None:
    transitions = _transitions("d4")
    split = _relation_split(transitions)
    result = evaluate_null_loop_retention(
        ExactTableProjectiveModel(),
        _batch("d4", seed=29, length=23),
        split,
        transitions,
        {"r4": D4_RELATIONS["r4"], "frfr": D4_RELATIONS["frfr"]},
        repeats=(1, 2, 5),
    )
    assert result.baseline.membership_fraction == 1.0
    for relation in result.relations.values():
        for record in relation["by_repeat"].values():
            assert record["conditional_retention_fraction"] == 1.0
            assert record["current_label_accuracy"] == 1.0
        assert relation["first_sampled_crossing"]["never_fraction_among_baseline_members"] == 1.0

    with pytest.raises(ValueError, match="not a null loop"):
        evaluate_null_loop_retention(
            ExactTableProjectiveModel(),
            _batch("d4", seed=31),
            split,
            transitions,
            {"not_null": (0,)},
            repeats=(1,),
        )


def test_switch_word_sampling_is_deterministic_and_rng_local() -> None:
    state_before = random.getstate()
    first = sample_switch_words(num_actions=2, word_length=8, count=31, seed=1101)
    state_after = random.getstate()
    second = sample_switch_words(num_actions=2, word_length=8, count=31, seed=1101)
    third = sample_switch_words(num_actions=2, word_length=8, count=31, seed=103)
    assert state_before == state_after
    assert first == second
    assert first != third
    assert (0,) * 8 in first
    assert (1,) * 8 in first
    assert len(first) == len(set(first)) == 31


def test_exact_switched_gain_is_one_and_arm_wrapper_is_complete() -> None:
    model = ExactTableProjectiveModel()
    transitions = _transitions("d4")
    split = _relation_split(transitions, max_depth=3)
    words = sample_switch_words(num_actions=2, word_length=6, count=20, seed=107)
    packet_batch = _batch("d4", seed=37, examples=5, length=9)
    switched = evaluate_sampled_switched_gain(
        model,
        packet_batch,
        words,
        transitions,
    )
    summary = switched.to_dict()
    assert summary["defined_fraction"] == 1.0
    assert summary["word_accuracy"] == 1.0
    assert summary["log_projective_gain"]["maximum"] == pytest.approx(0.0, abs=1e-6)

    complete = evaluate_packet_closure_arm(
        model,
        packet_batch,
        {"d4": _batch("d4", seed=41, examples=5, length=32)},
        split,
        transitions,
        {"f2": D4_RELATIONS["f2"]},
        words,
        null_repeats=(1, 2),
    ).to_dict()
    assert set(complete) == {
        "heldout_packet",
        "structured_deep",
        "null_loop_retention",
        "switched_gain",
    }


class FixedNonnormalModel(RecurrentOperatorModel):
    model_name = "test_nonnormal"

    def __init__(self) -> None:
        super().__init__()
        from komorebi_neuralese.switched_stability import nonnormal_switched_counterexample

        control = nonnormal_switched_counterexample(dtype=torch.float32)
        matrices = 0.5 * torch.eye(N_STATES).repeat(2, 1, 1)
        matrices[:, :2, :2] = control.operators
        self.register_buffer("codes", matrices)
        self.state_embedding = nn.Embedding(N_STATES, N_STATES)
        self.decoder = nn.Linear(N_STATES, N_STATES, bias=False)
        with torch.no_grad():
            self.state_embedding.weight.copy_(torch.eye(N_STATES))
            self.state_embedding.weight[0, :2].copy_(control.projective_probe_state)
            self.decoder.weight.copy_(torch.eye(N_STATES))

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return self.codes.unsqueeze(0).expand(tables.shape[0], -1, -1, -1)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return self.state_embedding(start)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        value = torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)
        return torch.nn.functional.normalize(value, dim=-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.decoder(hidden)


def _identity_episode() -> EpisodeBatch:
    maps = torch.arange(N_STATES).repeat(1, 2, 1)
    tables = torch.nn.functional.one_hot(maps, num_classes=N_STATES).float()
    empty = torch.empty((1, 0), dtype=torch.long)
    return EpisodeBatch(
        tables=tables,
        maps=maps,
        op_slots=empty,
        canonical_ops=empty.clone(),
        start=torch.tensor([0]),
        target=torch.tensor([0]),
        intermediates=empty.clone(),
        canonical_to_slot=torch.tensor([[0, 1]]),
        phi=torch.arange(N_STATES).unsqueeze(0),
        family="identity",
    )


def test_sampled_switch_audit_detects_nonnormal_amplification() -> None:
    identity_transitions = torch.arange(N_STATES).repeat(2, 1)
    result = evaluate_sampled_switched_gain(
        FixedNonnormalModel(),
        _identity_episode(),
        ((0, 1), (0, 0), (1, 1)),
        identity_transitions,
    )
    assert result.to_dict()["log_projective_gain"]["maximum"] > math.log(30.0)


def test_factorial_summary_recovers_all_seven_paired_effects() -> None:
    beta = {
        (0,): 1.0,
        (1,): 2.0,
        (2,): -0.5,
        (0, 1): 3.0,
        (0, 2): -2.0,
        (1, 2): 0.75,
        (0, 1, 2): 1.25,
    }
    cells: dict[tuple[bool, bool, bool], tuple[float, ...]] = {}
    for first in (False, True):
        for second in (False, True):
            for third in (False, True):
                cell = (first, second, third)
                coded = tuple(1.0 if level else -1.0 for level in cell)
                value = 10.0 + sum(
                    coefficient * math.prod(coded[index] for index in term)
                    for term, coefficient in beta.items()
                )
                # Common paired offsets alter the grand mean, not contrasts.
                cells[cell] = (value - 0.2, value, value + 0.2)
    result = factorial_effect_summary(cells, factor_names=("A", "B", "C"))
    assert result.grand_mean == pytest.approx(10.0)
    expected = {
        "A": 2.0,
        "B": 4.0,
        "C": -1.0,
        "A:B": 6.0,
        "A:C": -4.0,
        "B:C": 1.5,
        "A:B:C": 2.5,
    }
    assert set(result.effects) == set(expected)
    for name, value in expected.items():
        assert result.effects[name].estimate == pytest.approx(value)
        assert result.effects[name].sample_standard_deviation == pytest.approx(0.0, abs=1e-12)

    multiple = factorial_effect_summaries(
        {cell: {"accuracy": values, "margin": tuple(2 * x for x in values)} for cell, values in cells.items()},
        factor_names=("A", "B", "C"),
    )
    assert multiple["margin"].effects["A:B:C"].estimate == pytest.approx(5.0)


def test_factorial_summary_rejects_missing_and_unbalanced_cells() -> None:
    cells = {
        (a, b, c): (float(a + b + c),)
        for a in (False, True)
        for b in (False, True)
        for c in (False, True)
    }
    incomplete = dict(cells)
    incomplete.pop((True, True, True))
    with pytest.raises(ValueError, match="all eight"):
        factorial_effect_summary(incomplete)
    unbalanced = dict(cells)
    unbalanced[(True, True, True)] = (1.0, 2.0)
    with pytest.raises(ValueError, match="balanced"):
        factorial_effect_summary(unbalanced)


def test_hard_polar_geometry_audits_actual_and_raw_matrices() -> None:
    torch.manual_seed(1211)
    model = PolarIsometricTableOperatorRNN()
    model.train()
    transitions = _transitions("d4")
    batch = _batch("d4", seed=223, examples=4, length=7)
    words = sample_switch_words(num_actions=2, word_length=5, count=12, seed=227)
    result = evaluate_hard_polar_geometry(
        model,
        {"d4": batch},
        {"d4": words},
        {"d4": transitions},
        switched_episode_limit=3,
    )
    assert isinstance(result, HardPolarGeometryAudit)
    assert model.training
    assert result.hard_isometry_pass
    assert result.projective_switched_gain_sanity_pass
    assert result.aggregate["maximum_frobenius_orthogonality_defect"] < 5e-5
    assert result.aggregate["maximum_spectral_orthogonality_defect"] < 5e-5
    assert result.aggregate["maximum_absolute_determinant_magnitude_defect"] < 5e-5
    components = result.aggregate["determinant_components"]
    assert components["positive"] + components["negative"] == 8
    assert components["zero"] == 0
    assert result.to_dict()["switched_sanity"]["d4"]["defined_fraction"] == 1.0

    # Orthogonal output does not conceal a singular pre-polar parameterization.
    with torch.no_grad():
        model.operator_encoder.weight.zero_()
    singular = evaluate_hard_polar_geometry(
        model,
        {"d4": batch},
        {"d4": words},
        {"d4": transitions},
        switched_episode_limit=2,
    )
    assert singular.hard_isometry_pass
    assert singular.aggregate["raw_relative_minimum_singular_value"]["finite_count"] == 0
    assert singular.aggregate["raw_below_relative_singular_floor_fraction"] == 1.0
    assert not singular.to_dict()["raw_prepolar_well_conditioned_pass"]


class AmbientBlockModel(RecurrentOperatorModel):
    """Exact 8+4 block model with an optionally causal complement route."""

    model_name = "test_ambient_block"

    def __init__(self, *, q_dependent: bool = False) -> None:
        super().__init__()
        self.q_dependent = bool(q_dependent)
        self.state_embedding = nn.Embedding(N_STATES, 12)
        self.decoder = nn.Linear(12, N_STATES, bias=False)
        with torch.no_grad():
            self.state_embedding.weight.zero_()
            self.state_embedding.weight[:, :N_STATES].copy_(torch.eye(N_STATES))
            self.decoder.weight.zero_()
            self.decoder.weight[:, :N_STATES].copy_(torch.eye(N_STATES))
        if self.q_dependent:
            codes = torch.zeros(2, 12, 12)
            direct = math.sqrt(0.75)
            for state in range(4):
                codes[0, state, state] = direct
                codes[0, 8 + state, state] = 0.5
                codes[1, (state + 1) % 4, state] = 1.0
                codes[1, state, 8 + state] = 4.0
            for state in range(4, N_STATES):
                codes[:, state, state] = 1.0
            self.register_buffer("fixed_codes", codes)

    def invariant_metric(self) -> torch.Tensor:
        return torch.eye(12, device=self.state_embedding.weight.device)

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        if self.q_dependent:
            return self.fixed_codes.unsqueeze(0).expand(tables.shape[0], -1, -1, -1)
        output = torch.eye(12, dtype=tables.dtype, device=tables.device).repeat(
            tables.shape[0], tables.shape[1], 1, 1
        )
        output[:, :, :N_STATES, :N_STATES] = tables.transpose(-1, -2)
        return output

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return self.state_embedding(start)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        updated = torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)
        return torch.nn.functional.normalize(updated, dim=-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.decoder(hidden)


def _q_dependent_identity_episode(examples: int = 40) -> EpisodeBatch:
    maps = torch.arange(N_STATES).repeat(examples, 2, 1)
    tables = torch.nn.functional.one_hot(maps, num_classes=N_STATES).float()
    op_slots = torch.tensor((0, 1), dtype=torch.long).repeat(examples, 1)
    starts = torch.arange(examples, dtype=torch.long) % 4
    return EpisodeBatch(
        tables=tables,
        maps=maps,
        op_slots=op_slots,
        canonical_ops=op_slots.clone(),
        start=starts,
        target=starts.clone(),
        intermediates=torch.empty((examples, 0), dtype=torch.long),
        canonical_to_slot=torch.tensor((0, 1), dtype=torch.long).repeat(examples, 1),
        phi=torch.arange(N_STATES).repeat(examples, 1),
        family="identity_q_route",
    )


def test_ambient_assay_does_not_infer_use_from_a_vacuous_complement() -> None:
    model = AmbientBlockModel()
    result = evaluate_ambient_complement_causality(
        model,
        _batch("d4", seed=229, examples=16, length=8),
        random_seed=233,
    )
    assert isinstance(result, AmbientComplementCausalAssay)
    assert result.anchor_rank == 8
    assert result.complement_rank == 4
    assert result.native.accuracy == 1.0
    assert result.p_confined.accuracy == 1.0
    assert result.midpoint_q_ablated.accuracy == 1.0
    assert result.midpoint_q_energy_fraction.max() == 0.0
    assert result.evidence_status == "NO_MEANINGFUL_Q_PERFORMANCE_DROP"
    assert not result.supports_specific_ambient_attribution


def test_ambient_assay_detects_a_specific_complement_mediated_return() -> None:
    model = AmbientBlockModel(q_dependent=True)
    batch = _q_dependent_identity_episode()
    first = evaluate_ambient_complement_causality(model, batch, random_seed=239)
    second = evaluate_ambient_complement_causality(model, batch, random_seed=239)
    assert first.native.accuracy == 1.0
    assert first.p_confined.accuracy == 0.0
    assert first.midpoint_q_ablated.accuracy == 0.0
    assert first.matched_random_rank_control.accuracy > 0.5
    assert first.midpoint_q_energy_fraction.mean() == pytest.approx(0.25)
    assert first.random_energy_match_maximum_absolute_error <= 1e-6
    assert first.ideal_random_energy_match_maximum_absolute_error < 1e-12
    assert first.evidence_status == "SUPPORTED_SPECIFIC_Q_PERFORMANCE_DROP"
    assert first.supports_specific_ambient_attribution
    assert torch.equal(
        first.matched_random_rank_control.prediction,
        second.matched_random_rank_control.prediction,
    )
    assert torch.equal(
        first.matched_random_removed_energy_fraction,
        second.matched_random_removed_energy_fraction,
    )


def test_ambient_assay_rejects_a_zero_rank_complement() -> None:
    with pytest.raises(ValueError, match="nonvacuous anchor complement"):
        evaluate_ambient_complement_causality(
            ExactTableProjectiveModel(),
            _batch("d4", seed=241, examples=4, length=4),
        )
