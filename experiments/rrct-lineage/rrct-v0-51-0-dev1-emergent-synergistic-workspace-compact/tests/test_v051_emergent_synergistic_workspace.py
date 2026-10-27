"""Focused tests for RRCT v0.51 learned recurrent-message workspace."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from rrct.emergent_synergistic_workspace import (
    EmergentSynergisticDyad,
    EmergentWorkspaceConfig,
    load_emergent_model,
    operation_sequence_split,
    prefix_targets,
    save_emergent_model,
    state_dict_sha256,
    train_emergent_dyad,
)
from rrct.synergistic_ephemeral_workspace import (
    all_sequence_rows,
    synergy_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT_ROOT = (
    ROOT / "validation/v0.51.0_emergent_synergistic_workspace/results"
)
SUMMARY_PATH = RESULT_ROOT / "V0_51_FROZEN_SUMMARY.json"
ANALYSIS_PATH = RESULT_ROOT / "emergent_synergistic_workspace_analysis.json"


def test_task_retains_exact_four_bit_synergy() -> None:
    receipt = synergy_receipt(all_sequence_rows())
    assert receipt.target_entropy_bits == 4.0
    assert receipt.information_from_a_history_bits == 0.0
    assert receipt.information_from_b_history_bits == 0.0
    assert receipt.information_from_joint_history_bits == 4.0
    assert receipt.bayes_accuracy_a_history == 1.0 / 16.0
    assert receipt.bayes_accuracy_b_history == 1.0 / 16.0


def test_split_holds_out_complete_operation_compositions() -> None:
    rows = all_sequence_rows()
    train, heldout = operation_sequence_split(rows)
    assert int(train.sum()) == 52432
    assert int(heldout.sum()) == 13104
    train_keys = {tuple(row) for row in rows[train, 1:]}
    heldout_keys = {tuple(row) for row in rows[heldout, 1:]}
    assert train_keys.isdisjoint(heldout_keys)
    assert len(train_keys) + len(heldout_keys) == 4096
    assert all(np.sum(np.all(rows[:, 1:] == key, axis=1)) == 16 for key in list(heldout_keys)[:8])


def test_architecture_has_no_one_hot_workspace_input() -> None:
    config = EmergentWorkspaceConfig()
    model = EmergentSynergisticDyad(config)
    assert config.message_dim == 8
    assert config.message_dim < config.state_count
    assert model.initial_encoder.embedding_dim == 8
    assert model.agent_a.update_network[0].in_features == (
        config.message_dim + config.operation_embedding_dim
    )
    assert model.agent_b.update_network[0].in_features == (
        config.message_dim + config.operation_embedding_dim
    )


def test_prefix_targets_are_correct_and_order_sensitive() -> None:
    rows = all_sequence_rows()
    targets = prefix_targets(rows[:256])
    assert targets.shape == (256, 3)
    # Swapping A and B operation histories changes at least one accumulated state.
    altered = rows[:256].copy()
    altered[:, 1:4], altered[:, 4:7] = rows[:256, 4:7], rows[:256, 1:4]
    altered_targets = prefix_targets(altered)
    assert np.any(targets != altered_targets)


def test_small_training_is_seed_deterministic() -> None:
    config = EmergentWorkspaceConfig(
        hidden_dim=24,
        batch_size=256,
        training_steps=20,
        cpu_threads=2,
    )
    first, first_receipt = train_emergent_dyad(
        510511,
        "round_curriculum",
        config,
    )
    second, second_receipt = train_emergent_dyad(
        510511,
        "round_curriculum",
        config,
    )
    assert state_dict_sha256(first) == state_dict_sha256(second)
    assert first_receipt.digest == second_receipt.digest
    assert first_receipt.agent_parameter_digests_distinct


def test_saved_model_roundtrip_preserves_digest(tmp_path: Path) -> None:
    config = EmergentWorkspaceConfig(
        hidden_dim=24,
        batch_size=256,
        training_steps=10,
        cpu_threads=2,
    )
    model, receipt = train_emergent_dyad(
        510512,
        "round_curriculum",
        config,
    )
    path = tmp_path / "dyad.pt"
    save_emergent_model(path, model, receipt, 510512)
    loaded, loaded_receipt, holdout_seed = load_emergent_model(path)
    assert holdout_seed == 510512
    assert loaded_receipt == receipt
    assert state_dict_sha256(loaded) == receipt.state_dict_sha256


@pytest.mark.skipif(not SUMMARY_PATH.is_file(), reason="frozen evidence not yet generated")
def test_frozen_summary_preserves_bounded_claim() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert summary["all_endpoints_met"]
    assert len(summary["endpoints"]) == 21
    assert all(summary["endpoints"].values())
    assert summary["bounded_curriculum_supported_emergence_established"] is True
    assert summary["strict_emergence_established"] is False


@pytest.mark.skipif(not ANALYSIS_PATH.is_file(), reason="frozen evidence not yet generated")
def test_frozen_controls_and_transplants_have_expected_dissociation() -> None:
    analysis = json.loads(ANALYSIS_PATH.read_text(encoding="utf-8"))
    for result in analysis["seed_results"]:
        assert min(
            result["curriculum_training"]["heldout_accuracy_a"],
            result["curriculum_training"]["heldout_accuracy_b"],
        ) >= 0.995
        assert max(
            result["terminal_only_training"]["heldout_accuracy_a"],
            result["terminal_only_training"]["heldout_accuracy_b"],
        ) <= 0.35
        assert max(
            result["modes"]["reset_each_update"]["task_accuracy_a"],
            result["modes"]["reset_each_update"]["task_accuracy_b"],
        ) <= 0.20
        assert result["causal_transplant"]["patch_target_accuracy_a"] >= 0.95
        assert result["causal_transplant"]["patch_target_accuracy_b"] >= 0.95
        assert result["causal_transplant"]["patch_changes_plan_rate"] >= 0.90


@pytest.mark.skipif(not ANALYSIS_PATH.is_file(), reason="frozen evidence not yet generated")
def test_frozen_workspace_is_ephemeral_and_nonvalenced() -> None:
    analysis = json.loads(ANALYSIS_PATH.read_text(encoding="utf-8"))
    for result in analysis["seed_results"]:
        assert result["post_erasure"]["message_retained"] is False
        assert result["post_erasure"]["pair_memory_retained"] is False
        assert result["post_erasure"]["agent_a_accuracy"] <= 0.08
        assert result["post_erasure"]["agent_b_accuracy"] <= 0.08
        assert result["survival_reward"] == 0.0
        assert result["identity_reward"] == 0.0
        assert result["continuity_reward"] == 0.0
        assert result["valence_model_present"] is False
