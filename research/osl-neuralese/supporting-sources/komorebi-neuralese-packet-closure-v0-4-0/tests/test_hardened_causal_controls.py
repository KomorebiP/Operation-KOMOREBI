from __future__ import annotations

from dataclasses import replace
import sys
from pathlib import Path

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.evaluate import (
    _angle_matched_random_state,
    _relative_conjugacy_matched_orthogonal_control,
    _select_cross_context_operator_control_slots,
    intervention_metrics,
)
from komorebi_neuralese.packet_models import PolarIsometricTableOperatorRNN


def _orthogonal_batch(
    *, batch: int, dimension: int, seed: int, dtype: torch.dtype = torch.float64
) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    matrix = torch.randn(batch, dimension, dimension, generator=generator, dtype=dtype)
    orthogonal, triangular = torch.linalg.qr(matrix)
    signs = torch.where(
        torch.diagonal(triangular, dim1=-2, dim2=-1) >= 0,
        torch.ones(batch, dimension, dtype=dtype),
        -torch.ones(batch, dimension, dtype=dtype),
    )
    return orthogonal * signs.unsqueeze(-2)


def test_angle_matched_state_control_preserves_donor_norm_and_recipient_cosine() -> None:
    source = torch.Generator().manual_seed(1101)
    recipient = torch.randn(32, 12, generator=source, dtype=torch.float64)
    donor = torch.randn(32, 12, generator=source, dtype=torch.float64)

    first, first_receipt = _angle_matched_random_state(
        recipient,
        donor,
        torch.Generator().manual_seed(1211),
    )
    replay, replay_receipt = _angle_matched_random_state(
        recipient,
        donor,
        torch.Generator().manual_seed(1211),
    )

    recipient_unit = torch.nn.functional.normalize(recipient, dim=1)
    donor_unit = torch.nn.functional.normalize(donor, dim=1)
    control_unit = torch.nn.functional.normalize(first, dim=1)
    target_cosine = (recipient_unit * donor_unit).sum(dim=1)
    observed_cosine = (recipient_unit * control_unit).sum(dim=1)

    assert torch.equal(first, replay)
    assert first_receipt == replay_receipt
    assert first_receipt["defined_fraction"] == 1.0
    assert torch.allclose(first.norm(dim=1), donor.norm(dim=1), atol=1e-12, rtol=1e-12)
    assert torch.allclose(observed_cosine, target_cosine, atol=1e-12, rtol=1e-12)
    assert first_receipt["maximum_norm_error"] <= 1e-12
    assert first_receipt["maximum_cosine_error"] <= 1e-12


def test_angle_matched_state_control_reports_coincident_and_antipodal_degeneracy() -> None:
    recipient = torch.tensor(
        [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        dtype=torch.float64,
    )
    donor = torch.tensor(
        [[2.0, 0.0, 0.0], [-3.0, 0.0, 0.0], [0.0, 4.0, 0.0]],
        dtype=torch.float64,
    )

    control, receipt = _angle_matched_random_state(
        recipient,
        donor,
        torch.Generator().manual_seed(1307),
    )

    assert receipt["defined_fraction"] == pytest.approx(1.0 / 3.0)
    assert receipt["minimum_target_sine"] == 0.0
    assert torch.equal(control[0], donor[0])
    assert torch.equal(control[1], donor[1])
    assert torch.allclose(control.norm(dim=1), donor.norm(dim=1), atol=1e-12, rtol=0.0)


def test_relative_conjugacy_control_matches_orthogonal_geometry_and_replays() -> None:
    original = _orthogonal_batch(batch=24, dimension=12, seed=401)
    alternate = _orthogonal_batch(batch=24, dimension=12, seed=409)

    control, receipt = _relative_conjugacy_matched_orthogonal_control(
        original,
        alternate,
        torch.Generator().manual_seed(419),
    )
    replay, replay_receipt = _relative_conjugacy_matched_orthogonal_control(
        original,
        alternate,
        torch.Generator().manual_seed(419),
    )

    identity = torch.eye(12, dtype=torch.float64).expand_as(control)
    semantic_chord = torch.linalg.matrix_norm(alternate - original, ord="fro")
    control_chord = torch.linalg.matrix_norm(control - original, ord="fro")

    assert torch.equal(control, replay)
    assert receipt == replay_receipt
    assert receipt["defined_fraction"] == 1.0
    assert torch.allclose(control.transpose(-1, -2) @ control, identity, atol=2e-12, rtol=2e-12)
    assert torch.allclose(control_chord, semantic_chord, atol=2e-12, rtol=2e-12)
    assert torch.equal(torch.sign(torch.linalg.det(control)), torch.sign(torch.linalg.det(alternate)))
    assert float(torch.linalg.matrix_norm(control - alternate, ord="fro").min()) > 1e-5
    assert receipt["maximum_chord_distance_error"] <= 2e-12
    assert receipt["maximum_orthogonality_defect"] <= 2e-12
    assert receipt["determinant_component_match_fraction"] == 1.0
    assert receipt["minimum_separation_from_alternate"] > 1e-5


def test_relative_conjugacy_control_reports_central_relative_transform_as_undefined() -> None:
    original = _orthogonal_batch(batch=5, dimension=6, seed=431)
    alternate = -original

    control, receipt = _relative_conjugacy_matched_orthogonal_control(
        original,
        alternate,
        torch.Generator().manual_seed(433),
    )

    assert receipt["defined_fraction"] == 0.0
    assert receipt["minimum_separation_from_alternate"] == 0.0
    assert torch.equal(control, alternate)


def test_cross_context_slot_selection_excludes_original_and_alternate_tables() -> None:
    original = torch.tensor(
        [[1, 0, 3, 2], [1, 0, 3, 2], [1, 0, 3, 2]],
        dtype=torch.long,
    )
    alternate = torch.tensor(
        [[2, 3, 0, 1], [2, 3, 0, 1], [2, 3, 0, 1]],
        dtype=torch.long,
    )
    identity = torch.arange(4, dtype=torch.long)
    reverse = torch.arange(3, -1, -1, dtype=torch.long)
    candidates = torch.stack(
        (
            torch.stack((original[0], identity)),
            torch.stack((alternate[1], identity)),
            torch.stack((identity, reverse)),
        )
    )

    selected, receipt = _select_cross_context_operator_control_slots(
        original,
        alternate,
        candidates,
        torch.zeros(3, dtype=torch.long),
    )

    assert selected.tolist() == [1, 1, 0]
    assert int(receipt["base_original_table_collision"].sum()) == 1
    assert int(receipt["base_alternate_table_collision"].sum()) == 1
    assert int(receipt["selected_original_table_collision"].sum()) == 0
    assert int(receipt["selected_alternate_table_collision"].sum()) == 0


def test_cross_context_slot_selection_rejects_when_both_slots_are_primary() -> None:
    original = torch.tensor([[1, 0, 3, 2]], dtype=torch.long)
    alternate = torch.tensor([[2, 3, 0, 1]], dtype=torch.long)
    candidates = torch.stack((original, alternate), dim=1)

    with pytest.raises(RuntimeError, match="outside both primary operator tables"):
        _select_cross_context_operator_control_slots(
            original,
            alternate,
            candidates,
            torch.zeros(1, dtype=torch.long),
        )


def test_intervention_metrics_uses_supplied_banks_without_regeneration(monkeypatch: pytest.MonkeyPatch) -> None:
    examples = 12
    length = 6
    episode_batch = EpisodeGenerator(503).sample(examples, length, family="d4")
    operator_control_batch = EpisodeGenerator(509).sample(examples, length, family="d4")
    torch.manual_seed(521)
    model = PolarIsometricTableOperatorRNN()

    def forbidden_sample(*args: object, **kwargs: object) -> object:
        raise AssertionError("supplied intervention banks must prevent episode regeneration")

    monkeypatch.setattr(EpisodeGenerator, "sample", forbidden_sample)
    corrupted_target = replace(
        episode_batch,
        target=(episode_batch.target + 1) % 8,
    )
    with pytest.raises(ValueError, match="inexact terminal targets"):
        intervention_metrics(
            model,
            examples,
            batch_size=5,
            seed=991,
            device=torch.device("cpu"),
            length=length,
            split=3,
            operator_step=2,
            episode_batch=corrupted_target,
            operator_control_batch=operator_control_batch,
            control_seed=997,
        )

    first = intervention_metrics(
        model,
        examples,
        batch_size=5,
        seed=991,
        device=torch.device("cpu"),
        length=length,
        split=3,
        operator_step=2,
        episode_batch=episode_batch,
        operator_control_batch=operator_control_batch,
        control_seed=997,
    )
    replay = intervention_metrics(
        model,
        examples,
        batch_size=5,
        seed=123_456,
        device=torch.device("cpu"),
        length=length,
        split=3,
        operator_step=2,
        episode_batch=episode_batch,
        operator_control_batch=operator_control_batch,
        control_seed=997,
    )

    assert first == replay
    assert first["available"] is True
    assert first["examples"] == examples
    assert first["episode_bank_supplied"] is True
    assert first["operator_control_bank_supplied"] is True
    assert first["control_seed"] == 997
    assert first["state_control_geometry"]["maximum_norm_error"] <= 1e-5
    assert first["state_control_geometry"]["maximum_cosine_error"] <= 1e-5
    assert first["operator_control_geometry"]["available"] is True
    assert first["operator_control_geometry"]["maximum_chord_distance_error"] <= 1e-4
    assert first["operator_control_geometry"]["maximum_orthogonality_defect"] <= 1e-4
    assert (
        first["operator_control_geometry"][
            "minimum_cross_context_separation_from_original"
        ]
        > 1e-5
    )
    assert (
        first["operator_control_geometry"][
            "minimum_cross_context_separation_from_alternate"
        ]
        > 1e-5
    )
    assert (
        first["operator_control_geometry"][
            "cross_context_selected_original_table_collision_count"
        ]
        == 0
    )
    assert (
        first["operator_control_geometry"][
            "cross_context_selected_alternate_table_collision_count"
        ]
        == 0
    )
