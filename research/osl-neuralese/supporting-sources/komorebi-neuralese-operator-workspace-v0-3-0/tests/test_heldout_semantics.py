from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import run_experiment

from komorebi_neuralese.algebra import N_STATES
from komorebi_neuralese.hard_operator import ExactTableOracle
from komorebi_neuralese.heldout_semantics import (
    compose_full_word_maps,
    split_conditioned_final_action_metrics,
)
from komorebi_neuralese.models import RecurrentOperatorModel
from komorebi_neuralese.splits import map_splits
from komorebi_neuralese.version import VERSION


class RecordingExactPermutationModel(RecurrentOperatorModel):
    model_name = "recording_exact_permutation_oracle"

    def __init__(self) -> None:
        super().__init__()
        self.evaluated: list[tuple[torch.Tensor, torch.Tensor]] = []

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return tables.transpose(-1, -2)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return F.one_hot(start, num_classes=N_STATES).float()

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return hidden

    def run(
        self,
        tables: torch.Tensor,
        op_slots: torch.Tensor,
        start: torch.Tensor,
    ):
        self.evaluated.append((tables.detach().cpu(), op_slots.detach().cpu()))
        return super().run(tables, op_slots, start)


def test_full_word_map_matches_sequential_action_on_every_state() -> None:
    first = torch.tensor([1, 2, 0, 4, 3, 6, 7, 5])
    second = torch.tensor([2, 0, 1, 3, 4, 7, 5, 6])
    maps = torch.stack(
        (
            torch.stack((first, second)),
            torch.stack((second, first)),
        )
    )
    slots = torch.tensor([[0, 1, 0], [1, 0, 1]])
    observed = compose_full_word_maps(maps, slots)

    expected = torch.arange(N_STATES).expand(2, -1).clone()
    rows = torch.arange(2)
    for step in range(slots.shape[1]):
        selected = maps[rows, slots[:, step]]
        expected = torch.gather(selected, 1, expected)
    assert torch.equal(observed, expected)


@pytest.mark.parametrize("coordinate_split", ["dev", "test"])
def test_metric_evaluates_only_words_whose_full_map_is_held_out(
    coordinate_split: str,
) -> None:
    model = RecordingExactPermutationModel()
    result = split_conditioned_final_action_metrics(
        model,
        family="random",
        depths=(2, 5),
        examples_per_depth=23,
        batch_size=7,
        seed=731,
        device="cpu",
        coordinate_split=coordinate_split,
    )

    assert result["available"] is True
    assert result["endpoint_accuracy"] == 1.0
    assert result["primitive_map_split"] == coordinate_split
    assert result["composite_target_map_split"] == coordinate_split
    assert result["full_composite_split_enforced"] is True
    assert result["acceptance_receipt"]["accepted_examples"] == 46
    assert result["acceptance_receipt"]["all_primitive_maps_in_requested_split"] is True
    assert result["acceptance_receipt"][
        "all_accepted_full_composites_in_requested_split"
    ] is True

    evaluated = 0
    for tables, slots in model.evaluated:
        primitive_maps = tables.argmax(dim=-1)
        primitive_labels = np.asarray(map_splits(primitive_maps.numpy()))
        assert np.all(primitive_labels == coordinate_split)
        composites = compose_full_word_maps(primitive_maps, slots)
        composite_labels = np.asarray(map_splits(composites.numpy()))
        assert np.all(composite_labels == coordinate_split)
        evaluated += tables.shape[0]
    assert evaluated == 46

    for record in result["by_depth"].values():
        receipt = record["acceptance_receipt"]
        assert receipt["candidate_accounting_exact"] is True
        assert receipt["rejection_accounting_exact"] is True
        assert receipt["accepted_examples"] == 23
        assert receipt["candidate_composite_split_counts"][coordinate_split] == 23
        assert sum(receipt["rejected_composite_split_counts"].values()) == receipt[
            "rejected_examples"
        ]
        assert receipt["primitive_split_violations"] == 0
        assert receipt["target_consistency_violations"] == 0
        assert len(receipt["candidate_stream_sha256"]) == 64
        assert len(receipt["accepted_examples_sha256"]) == 64


def test_rejection_receipts_are_deterministic_and_depth_order_independent() -> None:
    arguments = dict(
        family="random",
        examples_per_depth=19,
        batch_size=6,
        seed=991,
        device="cpu",
        coordinate_split="test",
    )
    forward = split_conditioned_final_action_metrics(
        RecordingExactPermutationModel(), depths=(2, 7), **arguments
    )
    repeated = split_conditioned_final_action_metrics(
        RecordingExactPermutationModel(), depths=(2, 7), **arguments
    )
    reversed_order = split_conditioned_final_action_metrics(
        RecordingExactPermutationModel(), depths=(7, 2), **arguments
    )

    assert forward == repeated
    assert forward["by_depth"] == reversed_order["by_depth"]
    assert (
        forward["acceptance_receipt"]["depth_receipts_sha256"]
        == reversed_order["acceptance_receipt"]["depth_receipts_sha256"]
    )


def test_heldout_metric_rejects_train_and_nonpositive_depths() -> None:
    model = RecordingExactPermutationModel()
    common = dict(
        model=model,
        family="random",
        examples_per_depth=2,
        batch_size=2,
        seed=1,
        device="cpu",
    )
    with pytest.raises(ValueError, match="held-out 'dev' or 'test'"):
        split_conditioned_final_action_metrics(
            depths=(2,), coordinate_split="train", **common
        )
    with pytest.raises(ValueError, match="depths must be positive"):
        split_conditioned_final_action_metrics(
            depths=(0,), coordinate_split="test", **common
        )


@pytest.fixture(scope="module")
def runner_semantic_payload() -> tuple[dict, dict, dict]:
    protocol = {
        "protocol_id": "runner_semantic_holdout_test",
        "analysis_status": "development",
        "arms": {"oracle": {"model_name": "exact_table_oracle"}},
        "evaluation": {
            "coordinate_split": "test",
            "depths": [2],
            "neighbor_offsets": [0],
            "examples_per_depth": 4,
            "batch_size": 4,
            "geometry_examples": 4,
            "composition_examples": 4,
            "patch_examples": 4,
            "c8_examples_per_depth": 4,
            "random_depths": [2],
            "random_examples_per_depth": 4,
            "semantic_holdout_depths": [2, 3],
            "semantic_holdout_examples": 5,
            "semantic_holdout_batch_size": 3,
            "semantic_holdout_family": "random",
        },
    }
    metrics = run_experiment._evaluate_model(
        ExactTableOracle(), protocol, seed=17, device=torch.device("cpu")
    )
    aggregate = run_experiment._aggregate_all(
        {"oracle": [{"metrics": metrics}]}, []
    )
    return protocol, metrics, aggregate


def test_runner_config_adds_split_conditioned_final_action_and_oracle_checks(
    runner_semantic_payload: tuple[dict, dict, dict],
) -> None:
    _, metrics, _ = runner_semantic_payload
    section = metrics["split_conditioned_final_action"]
    assert section["metric"] == "split_conditioned_full_composite_final_action_accuracy"
    assert section["evaluated_depths"] == [2, 3]
    assert section["endpoint_accuracy"] == 1.0
    assert section["acceptance_receipt"]["accepted_examples"] == 10
    integrity = run_experiment._exact_oracle_integrity(metrics)
    assert integrity["passed"] is True
    assert integrity["checks"]["split_conditioned_final_action.accepted_only"] is True


def test_runner_report_states_final_action_claim_boundary(
    runner_semantic_payload: tuple[dict, dict, dict],
) -> None:
    protocol, _, aggregate = runner_semantic_payload
    report = run_experiment._report(
        protocol,
        aggregate,
        gates={},
        grid={"complete": True, "observed_cells": 1, "expected_cells": 1},
        oracle_record={"integrity": {"passed": True}},
    )
    assert "Split-conditioned final-action assay" in report
    assert "globally novel" in report
    assert "| oracle | 2 | 1.0000 |" in report


def test_runner_csv_contains_semantic_accuracy_and_acceptance_receipt(
    tmp_path: Path,
    runner_semantic_payload: tuple[dict, dict, dict],
) -> None:
    _, metrics, _ = runner_semantic_payload
    path = tmp_path / "summary.csv"
    records = {
        "oracle": [
            {
                "seed": 17,
                "training": {"parameter_count": 0, "elapsed_seconds": 0.0},
                "metrics": metrics,
            }
        ]
    }
    run_experiment._write_csv(path, records)
    with path.open(encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["split_conditioned_final_action.by_depth.2.endpoint_accuracy"] == "1.0"
    assert (
        float(
            row[
                "split_conditioned_final_action.by_depth.2."
                "acceptance_receipt.acceptance_rate"
            ]
        )
        > 0.0
    )


def test_runner_requires_explicit_strict_training_split_protocol(tmp_path: Path) -> None:
    protocol = {
        "schema_version": "1",
        "protocol_id": "strict_split_parser_test",
        "analysis_status": "development",
        "package_version": VERSION,
        "seeds": [1],
        "arms": {"hard": {"model_name": "linear_hyper_hard"}},
        "training": {
            "word_product_scope": "contiguous",
            "conditioned_sampler_backend": "cached_exact_v1",
        },
        "evaluation": {"coordinate_split": "test"},
    }
    path = tmp_path / "protocol.json"
    path.write_text(json.dumps(protocol), encoding="utf-8")
    assert run_experiment._read_protocol(path)["training"]["word_product_scope"] == "contiguous"

    del protocol["training"]["word_product_scope"]
    path.write_text(json.dumps(protocol), encoding="utf-8")
    with pytest.raises(ValueError, match="explicitly freeze"):
        run_experiment._read_protocol(path)

    protocol["training"]["word_product_scope"] = "contiguous"
    del protocol["training"]["conditioned_sampler_backend"]
    path.write_text(json.dumps(protocol), encoding="utf-8")
    with pytest.raises(ValueError, match="conditioned_sampler_backend"):
        run_experiment._read_protocol(path)

    protocol["training"]["conditioned_sampler_backend"] = "cached_exact_v1"
    protocol["arms"]["hard"]["word_product_scope"] = "terminal"
    path.write_text(json.dumps(protocol), encoding="utf-8")
    with pytest.raises(ValueError, match="overrides the required contiguous"):
        run_experiment._read_protocol(path)
