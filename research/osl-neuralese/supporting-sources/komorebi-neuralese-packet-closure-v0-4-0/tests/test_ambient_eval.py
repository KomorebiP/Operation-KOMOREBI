from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import torch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.ambient_eval import (
    canonicalize_actions,
    capture_trajectory,
    derive_seed,
    episode_bank_receipts,
    episode_contract,
    exact_chart_packet_control,
    gauge_synthetic_controls,
    json_ready,
    load_projective_pilot_models,
    make_episode_bank,
    switched_synthetic_controls,
    tensor_receipt,
)
from komorebi_neuralese.stable_models import ProjectiveLinearHyperOperatorRNN


def test_tuple_addressed_seed_is_stable_and_distinct() -> None:
    first = derive_seed(31001, "context", "d4", 7)
    assert first == derive_seed(31001, "context", "d4", 7)
    assert first != derive_seed(31001, "context", "d4", 8)
    assert 0 <= first < 2**64


def test_same_context_bank_is_byte_deterministic_and_exact() -> None:
    first = make_episode_bank(contexts=8, length=12, family="d4", seed=31001)
    second = make_episode_bank(contexts=8, length=12, family="d4", seed=31001)
    for field in (
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
        assert torch.equal(getattr(first, field), getattr(second, field))
    assert episode_contract(first) == {
        "family": "d4",
        "intermediates_exact": True,
        "target_exact": True,
        "canonical_visible_slots_exact": True,
        "tables_exact_one_hot_maps": True,
        "tables_finite": True,
        "maps_are_permutations": True,
        "phi_is_permutation": True,
        "visible_slots_are_permutations": True,
        "canonical_family_realization_exact": True,
        "shapes_exact": True,
        "values_in_range": True,
        "contexts": 8,
        "length": 12,
    }
    assert episode_bank_receipts(first) == episode_bank_receipts(second)


def test_canonical_action_reordering_keeps_codes_and_maps_paired() -> None:
    bank = make_episode_bank(contexts=16, length=1, family="c8", seed=13)
    visible_codes = torch.arange(16 * 2 * 3 * 3, dtype=torch.float64).reshape(16, 2, 3, 3)
    codes, transitions = canonicalize_actions(
        visible_codes, bank.maps, bank.canonical_to_slot
    )
    for episode in range(16):
        for canonical_action in range(2):
            visible_slot = int(bank.canonical_to_slot[episode, canonical_action])
            assert torch.equal(codes[episode, canonical_action], visible_codes[episode, visible_slot])
            assert torch.equal(transitions[episode, canonical_action], bank.maps[episode, visible_slot])


def test_frozen_checkpoint_loader_uses_projective_model_and_validates_receipt() -> None:
    loaded = load_projective_pilot_models(ROOT, [0], device="cpu")[0]
    assert isinstance(loaded.model, ProjectiveLinearHyperOperatorRNN)
    assert loaded.receipt["sha256"] == (
        "b2d16d640dddc4f2f2ed69a4211f0d9948c71c3655901484238fa8ae11c1f702"
    )
    bank = make_episode_bank(contexts=4, length=3, family="d4", seed=17)
    trace = loaded.model.run(bank.tables, bank.op_slots, bank.start)
    assert torch.allclose(trace.hidden[-1].norm(dim=1), torch.ones(4), atol=1e-6, rtol=1e-6)


def test_gauge_controls_discriminate_global_statewise_negative_and_leakage() -> None:
    controls = gauge_synthetic_controls()
    assert controls["exact_global"]["global_residual_max"] < 1e-12
    assert controls["exact_statewise"]["statewise_residual_max"] < 1e-12
    assert controls["exact_statewise"]["global_residual_min"] > 0.1
    assert controls["negative_scale"]["invalid_coefficients"] == 1
    assert controls["leakage"]["statewise_residual_max"] > 1e-3
    assert controls["leakage"]["reconstruction_error_max"] < 1e-12


def test_exact_chart_packet_and_switched_controls_pass() -> None:
    loaded = load_projective_pilot_models(ROOT, [0], device="cpu")[0]
    bank = make_episode_bank(contexts=3, length=2, family="d4", seed=19)
    capture = capture_trajectory(loaded.model, bank, [0, 2])
    packet = exact_chart_packet_control(capture, prefixes=[0, 2], horizon=2)
    assert packet["0"]["membership_fraction"] == 1.0
    assert packet["2"]["membership_fraction"] == 1.0
    switched = switched_synthetic_controls(capture.canonical_transitions[0])
    assert switched["exact_chart"]["accuracy"] == 1.0
    assert abs(switched["exact_chart"]["gain"]["minimum"] - 1.0) < 1e-12
    assert abs(switched["exact_chart"]["gain"]["maximum"] - 1.0) < 1e-12
    assert switched["nonnormal"]["flagged"]
    assert switched["nonnormal"]["projective_worst_amplification"] > 30.0


def test_json_ready_removes_nonfinite_values_and_strict_json_accepts_result() -> None:
    value = json_ready({"nan": math.nan, "inf": math.inf, "tensor": torch.tensor([1.0])})
    assert value == {"nan": None, "inf": None, "tensor": [1.0]}
    json.dumps(value, allow_nan=False)


def test_tensor_receipt_is_content_deterministic() -> None:
    first = tensor_receipt(torch.arange(12, dtype=torch.float32).reshape(3, 4))
    second = tensor_receipt(torch.arange(12, dtype=torch.float32).reshape(3, 4))
    changed = tensor_receipt(torch.arange(12, dtype=torch.float32).reshape(3, 4) + 1)
    assert first == second
    assert first["shape"] == [3, 4]
    assert first["dtype"] == "float32"
    assert first["sha256"] != changed["sha256"]
