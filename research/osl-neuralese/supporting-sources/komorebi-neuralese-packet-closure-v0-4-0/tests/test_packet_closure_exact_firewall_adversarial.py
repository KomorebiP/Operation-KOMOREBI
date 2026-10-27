from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import run_packet_closure as runner


def _set_path(root: dict[str, Any], path: tuple[str, ...], value: object) -> None:
    cursor: dict[str, Any] = root
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = value


@pytest.fixture(scope="module")
def exact_assay_inputs() -> dict[str, Any]:
    """Small, real evaluation receipts plus the minimum adjudication envelope."""

    config = copy.deepcopy(runner.PROFILES["smoke"])
    banks, episode_receipts = runner.make_eval_banks(config)

    construction = runner.construction_checkpoint_metadata(
        runner.make_v04_construction_bank(
            int(config["training"]["auxiliary_max_depth"])
        )
    )
    records = {
        str(seed): {
            arm: {
                "training": {
                    "construction_digest": construction["construction_digest"],
                    "construction_word_count": 20,
                }
            }
            for arm in runner.ARM_NAMES
        }
        for seed in config["seeds"]
    }

    transitions = torch.from_numpy(runner.canonical_maps("d4")).to(dtype=torch.long)
    heldout = runner.freeze_heldout_bank(
        runner.make_v04_suffix_plan(max_depth=8),
        transitions,
        max_suffixes=None,
    )
    switch_words = runner.sample_switch_words(
        num_actions=2,
        word_length=int(config["switched_word_length"]),
        count=int(config["switched_word_count"]),
        seed=runner.derive_seed(int(config["eval_seed_base"]), "switch_words"),
        include_constant_words=True,
    )
    eval_bank = {
        "heldout_bank": heldout.to_dict(),
        "heldout_words": [list(word) for word in heldout.words],
        "heldout_relation_signatures": [
            list(signature) for signature in heldout.relation_signatures
        ],
        "switch_bank": {
            "word_length": int(config["switched_word_length"]),
            "word_count": len(switch_words),
            "contexts": int(config["switched_contexts"]),
            "exhaustive": len(switch_words)
            == 2 ** int(config["switched_word_length"]),
            "words": [list(word) for word in switch_words],
        },
        "cross_context_operator_control": (
            runner.independent_cross_context_bank_contract(
                banks["intervention"],
                banks["intervention_operator_control"],
                operator_step=int(
                    config["intervention_operator_step_zero_indexed"]
                ),
            )
        ),
        "episode_receipts": episode_receipts,
    }
    checkpoint_seal = {
        "strict_checkpoint_firewall": True,
        "construction_word_count": 20,
        "construction": construction,
        # Other execution gates are deliberately outside this fixture's scope.
        "checkpoints": [],
    }
    return {
        "config": config,
        "records": records,
        "checkpoint_seal": checkpoint_seal,
        "eval_bank": eval_bank,
    }


def _assay_gates(
    inputs: dict[str, Any],
    *,
    checkpoint_seal: dict[str, Any] | None = None,
    eval_bank: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return runner.adjudicate(
        "smoke",
        inputs["config"],
        {},
        inputs["records"],
        {},
        {},
        checkpoint_seal or inputs["checkpoint_seal"],
        eval_bank or inputs["eval_bank"],
        {
            "checkpoint_sealed": "2026-01-01T00:00:00+00:00",
            "evaluation_bank_materialized": "2026-01-01T00:00:01+00:00",
        },
        source_integrity={},
    )["assay_gates"]


def test_exact_eval_contract_accepts_the_registered_real_bank(
    exact_assay_inputs: dict[str, Any],
) -> None:
    assert runner.validate_eval_episode_contracts(
        exact_assay_inputs["eval_bank"], exact_assay_inputs["config"]
    )
    assert (
        _assay_gates(exact_assay_inputs)["A06_exact_episode_contracts"]["status"]
        == "PASS"
    )


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("packet", "0", "contexts"), 17),
        (("packet", "64", "length"), 65),
        (("packet", "0", "family"), "c8"),
        (("packet", "64", "canonical_visible_slots_exact"), False),
        (("packet", "64", "canonical_family_realization_exact"), False),
        (("packet", "64", "canonical_visible_slots_exact"), 1),
    ],
    ids=(
        "context-count",
        "depth",
        "family",
        "canonical-slot-action",
        "canonical-family-action",
        "canonical-truth-type",
    ),
)
def test_exact_eval_contract_rejects_field_mutations(
    exact_assay_inputs: dict[str, Any],
    path: tuple[str, ...],
    replacement: object,
) -> None:
    eval_bank = copy.deepcopy(exact_assay_inputs["eval_bank"])
    contracts = eval_bank["episode_receipts"]["contracts"]
    _set_path(contracts, path, replacement)
    assert not runner.validate_eval_episode_contracts(
        eval_bank, exact_assay_inputs["config"]
    )


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("packet", "0", "contexts"), 16.0),
        (("packet", "64", "length"), 64.0),
        (("null", "length"), False),
    ],
    ids=("float-context-count", "float-depth", "boolean-zero-depth"),
)
def test_exact_eval_contract_rejects_json_numeric_type_impostors(
    exact_assay_inputs: dict[str, Any],
    path: tuple[str, ...],
    replacement: object,
) -> None:
    eval_bank = copy.deepcopy(exact_assay_inputs["eval_bank"])
    contracts = eval_bank["episode_receipts"]["contracts"]
    _set_path(contracts, path, replacement)
    assert not runner.validate_eval_episode_contracts(
        eval_bank, exact_assay_inputs["config"]
    )


def test_exact_construction_and_heldout_firewalls_accept_registered_payloads(
    exact_assay_inputs: dict[str, Any],
) -> None:
    assay = _assay_gates(exact_assay_inputs)
    assert assay["A02_construction_bank_shared"]["status"] == "PASS"
    assert assay["A04_reserved_terminal_action_holdout"]["status"] == "PASS"


@pytest.mark.parametrize(
    "mutation",
    ("word-count", "word", "digest"),
)
def test_exact_construction_firewall_rejects_value_mutations(
    exact_assay_inputs: dict[str, Any], mutation: str
) -> None:
    seal = copy.deepcopy(exact_assay_inputs["checkpoint_seal"])
    if mutation == "word-count":
        seal["construction_word_count"] = 19
    elif mutation == "word":
        seal["construction"]["construction_words"][0][0] = 1 - seal[
            "construction"
        ]["construction_words"][0][0]
    else:
        seal["construction"]["construction_digest"] = "0" * 64
    assert (
        _assay_gates(exact_assay_inputs, checkpoint_seal=seal)[
            "A02_construction_bank_shared"
        ]["status"]
        == "FAIL"
    )


@pytest.mark.parametrize(
    "mutation",
    ("word-count", "fingerprint", "word", "relation-signature"),
)
def test_exact_heldout_firewall_rejects_value_mutations(
    exact_assay_inputs: dict[str, Any], mutation: str
) -> None:
    eval_bank = copy.deepcopy(exact_assay_inputs["eval_bank"])
    if mutation == "word-count":
        eval_bank["heldout_bank"]["word_count"] = 170
    elif mutation == "fingerprint":
        eval_bank["heldout_bank"]["fingerprint"] = "0" * 64
    elif mutation == "word":
        eval_bank["heldout_words"][1][0] = 1 - eval_bank["heldout_words"][1][0]
    else:
        eval_bank["heldout_relation_signatures"][0][0] = 7
    assert (
        _assay_gates(exact_assay_inputs, eval_bank=eval_bank)[
            "A04_reserved_terminal_action_holdout"
        ]["status"]
        == "FAIL"
    )


@pytest.mark.parametrize(
    "mutation",
    ("word-count-float", "word-action-float"),
)
def test_exact_construction_firewall_rejects_json_numeric_type_impostors(
    exact_assay_inputs: dict[str, Any], mutation: str
) -> None:
    seal = copy.deepcopy(exact_assay_inputs["checkpoint_seal"])
    if mutation == "word-count-float":
        seal["construction_word_count"] = 20.0
    else:
        action = seal["construction"]["construction_words"][0][0]
        seal["construction"]["construction_words"][0][0] = float(action)
    assert (
        _assay_gates(exact_assay_inputs, checkpoint_seal=seal)[
            "A02_construction_bank_shared"
        ]["status"]
        == "FAIL"
    )


@pytest.mark.parametrize(
    "mutation",
    ("word-count-float", "split-verified-int", "word-action-float", "signature-float"),
)
def test_exact_heldout_firewall_rejects_json_numeric_type_impostors(
    exact_assay_inputs: dict[str, Any], mutation: str
) -> None:
    eval_bank = copy.deepcopy(exact_assay_inputs["eval_bank"])
    if mutation == "word-count-float":
        eval_bank["heldout_bank"]["word_count"] = 171.0
    elif mutation == "split-verified-int":
        eval_bank["heldout_bank"]["split_verified"] = 1
    elif mutation == "word-action-float":
        action = eval_bank["heldout_words"][1][0]
        eval_bank["heldout_words"][1][0] = float(action)
    else:
        value = eval_bank["heldout_relation_signatures"][0][0]
        eval_bank["heldout_relation_signatures"][0][0] = float(value)
    assert (
        _assay_gates(exact_assay_inputs, eval_bank=eval_bank)[
            "A04_reserved_terminal_action_holdout"
        ]["status"]
        == "FAIL"
    )
