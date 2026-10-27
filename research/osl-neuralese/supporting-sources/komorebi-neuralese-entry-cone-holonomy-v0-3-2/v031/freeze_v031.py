#!/usr/bin/env python3
"""Fail-closed execution freeze for Neuralese v0.3.1.

Author: Komorebi P.

This module intentionally performs only byte hashing, JSON/schema validation,
symbolic D4 checks, and synthetic structural tests.  It never deserializes or
evaluates a learned checkpoint.  Copy it into ``v031/`` before creating the
one-time execution freeze.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


SCHEMA = "komorebi.neuralese.entry_cone_holonomy.execution_freeze.v1"
VERSION = "0.3.1"
AUTHOR = "Komorebi P."
TARGET_NAME = "V031_EXECUTION_FREEZE.json"
EXPECTED_PYTHON_IMPLEMENTATION = "CPython"
EXPECTED_PYTHON_VERSION = "3.12.13"
EXPECTED_NUMPY_VERSION = "2.3.5"
EXPECTED_ATTESTATION = (
    "No v0.3.1 learned endpoint on the exact 940000/941000 episode "
    "realizations was inspected before this file was written."
)

# These are root-relative and intentionally explicit.  There is no glob or
# directory discovery in the scientific freeze: adding, deleting, or silently
# substituting a registered scientific source must require a new revision.
REQUIRED_ROOT_RELATIVE_FILES: tuple[str, ...] = (
    "DESIGN_DISCLOSURE.json",
    "EXECUTION_FREEZE.json",
    "checkpoint_io.py",
    "checkpoints/projective_terminal_seed0.pt",
    "checkpoints/projective_terminal_seed1.pt",
    "core.py",
    "results/LINEAGE_REGRESSION.json",
    "v031/__init__.py",
    "v031/V031_FROZEN_INPUTS.json",
    "v031/V031_MATCHED_WORD_BANK.json",
    "v031/V031_PREFREEZE_VALIDATION.json",
    "v031/V031_PREREGISTRATION.json",
    "v031/V031_RESEARCH_SPEC.md",
    "v031/requirements.txt",
    "v031/entry_recurrence_probe.py",
    "v031/freeze_v031.py",
    "v031/generate_v031_inputs.py",
    "v031/generate_word_bank.py",
    "v031/holonomy_spectroscopy.py",
    "v031/matched_controls.py",
    "v031/run_v031.py",
    "v031/test_entry_recurrence_probe.py",
    "v031/test_holonomy_spectroscopy.py",
    "v031/test_matched_controls.py",
    "v031/test_v031_contract.py",
    "v031/test_v031_engine.py",
    "v031/v031_engine.py",
)

EXPECTED_CHECKPOINT_DIGESTS = {
    "checkpoints/projective_terminal_seed0.pt": (
        "b2d16d640dddc4f2f2ed69a4211f0d9948c71c3655901484238fa8ae11c1f702"
    ),
    "checkpoints/projective_terminal_seed1.pt": (
        "a52dd3def596553c2880dfd00516bd1bb7492d1cbfab1634b570f27c1737d2d7"
    ),
}

EXPECTED_TEST_FILES = (
    "test_entry_recurrence_probe.py",
    "test_holonomy_spectroscopy.py",
    "test_matched_controls.py",
    "test_v031_contract.py",
    "test_v031_engine.py",
)

EXPECTED_REGISTERED_PROFILE = {
    "checkpoint_seeds": [0, 1],
    "episode_seeds": {"0": 940000, "1": 941000},
    "episodes_per_checkpoint": 8,
    "entry_maximum_suffix_horizon": 8,
    "cone_maximum_history_depth": 8,
    "cone_maximum_suffix_horizon": 8,
    "relation_maximum_inserted_token_budget": 64,
    "relation_repeat_grids": {
        "f2": list(range(33)),
        "r4": list(range(17)),
        "frfr": list(range(17)),
        "rfrf": list(range(17)),
    },
    "path_base_cases_per_episode": 64,
    "path_maximum_suffix_horizon": 8,
    "matched_control_budgets": [16, 32, 64],
    "matched_reference_count": 12,
    "matched_exact_length_control_count": 48,
    "matched_total_path_count": 60,
    "parity_sandwich_materialized": False,
    "registered_run_started": "results/V031_RUN_STARTED.json",
    "registered_result": "results/V031_ENTRY_CONE_HOLONOMY_RESULTS.json",
    "runtime_contract": {
        "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
        "python_version": EXPECTED_PYTHON_VERSION,
        "numpy_version": EXPECTED_NUMPY_VERSION,
    },
    "alternate_profiles": "forbidden",
    "overwrite": "forbidden",
}

EXPECTED_RELATIONS: dict[str, tuple[int, ...]] = {
    "f2": (1, 1),
    "r4": (0, 0, 0, 0),
    "frfr": (1, 0, 1, 0),
    "rfrf": (0, 1, 0, 1),
}
EXPECTED_BUDGETS = (16, 32, 64)
EXPECTED_ENDPOINT_NAMES = ("e", "R", "R2", "R3", "F", "FR", "FR2", "FR3")
EXPECTED_TRANSVERSAL_WORDS: dict[str, tuple[int, ...]] = {
    "e": (1, 1),
    "R": (0,),
    "R2": (0, 0),
    "R3": (0, 0, 0),
    "F": (1,),
    "FR": (1, 0),
    "FR2": (1, 0, 0),
    "FR3": (1, 0, 0, 0),
}


class FreezeValidationError(ValueError):
    """Raised when an immutable execution input violates the contract."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_runtime_contract() -> dict[str, str]:
    """Require the exact numerical runtime registered for the one-shot run."""

    observed = {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
    }
    expected = {
        "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
        "python_version": EXPECTED_PYTHON_VERSION,
        "numpy_version": EXPECTED_NUMPY_VERSION,
    }
    _require(observed == expected, f"numerical runtime mismatch: {observed} != {expected}")
    return observed


def validate_no_executable_bytecode(package_root: Path) -> dict[str, Any]:
    """Reject Python bytecode that could bypass the registered source hashes."""

    root = Path(package_root).resolve()
    pyc_files = sorted(
        str(path.relative_to(root)) for path in root.rglob("*.pyc") if path.is_file()
    )
    cache_directories = sorted(
        str(path.relative_to(root))
        for path in root.rglob("__pycache__")
        if path.is_dir()
    )
    _require(
        not pyc_files and not cache_directories,
        "executable bytecode/cache is present; remove it before freeze: "
        f"pyc={pyc_files}, cache_dirs={cache_directories}",
    )
    return {
        "passed": True,
        "pyc_file_count": 0,
        "pycache_directory_count": 0,
    }


def content_sha256_without_field(value: Mapping[str, Any], field: str) -> str:
    stripped = {key: item for key, item in value.items() if key != field}
    return hashlib.sha256(canonical_json_bytes(stripped)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FreezeValidationError(message)


def _require_exact_keys(observed: Iterable[Any], expected: Iterable[Any], label: str) -> None:
    observed_set = set(observed)
    expected_set = set(expected)
    if observed_set != expected_set:
        missing = sorted(expected_set - observed_set, key=str)
        extra = sorted(observed_set - expected_set, key=str)
        raise FreezeValidationError(f"{label} key mismatch; missing={missing}, extra={extra}")


def _binary_word(value: Any, label: str, *, nonempty: bool = False) -> tuple[int, ...]:
    _require(isinstance(value, list), f"{label} must be a JSON list")
    _require(not nonempty or bool(value), f"{label} must be nonempty")
    _require(
        all(type(token) is int and token in (0, 1) for token in value),
        f"{label} must contain only integer 0/1 tokens",
    )
    return tuple(value)


def _is_permutation(values: Sequence[Any], size: int) -> bool:
    return (
        len(values) == size
        and all(type(value) is int for value in values)
        and set(values) == set(range(size))
    )


# Independent D4 oracle.  States 0..3 are the top orbit and states 4..7 the
# bottom orbit.  R advances within an orbit; F swaps orbits and negates phase.
_R = tuple(4 * (index // 4) + ((index % 4 + 1) % 4) for index in range(8))
_F = tuple(4 * (1 - index // 4) + ((-(index % 4)) % 4) for index in range(8))
_D4_MAPS = (_R, _F)


def d4_word_action(word: Iterable[int]) -> tuple[int, ...]:
    action = tuple(range(8))
    for raw_token in word:
        if type(raw_token) is not int or raw_token not in (0, 1):
            raise FreezeValidationError("D4 word contains a non-binary integer token")
        mapping = _D4_MAPS[raw_token]
        action = tuple(mapping[state] for state in action)
    return action


_CANONICAL_ENDPOINT_ACTIONS = tuple(
    d4_word_action(word)
    for word in ((), (0,), (0, 0), (0, 0, 0), (1,), (1, 0), (1, 0, 0), (1, 0, 0, 0))
)
_ACTION_TO_ENDPOINT = {
    action: index for index, action in enumerate(_CANONICAL_ENDPOINT_ACTIONS)
}


def d4_endpoint_index(word: Iterable[int]) -> int:
    action = d4_word_action(word)
    try:
        return _ACTION_TO_ENDPOINT[action]
    except KeyError as error:  # defensive: generators should close on D4
        raise FreezeValidationError("word action fell outside the declared D4 group") from error


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise FreezeValidationError(f"cannot read valid JSON at {path}: {error}") from error
    _require(isinstance(value, dict), f"{path} must contain one JSON object")
    return value


def validate_frozen_inputs(path: Path) -> dict[str, Any]:
    """Validate the learned-output-free episode serialization and transversal."""

    value = _load_json(path)
    _require(
        value.get("schema")
        == "komorebi.neuralese.entry_cone_holonomy.frozen_inputs.v1",
        "unexpected frozen-input schema",
    )
    _require(value.get("version") == VERSION, "unexpected frozen-input version")
    _require(value.get("author") == AUTHOR, "unexpected frozen-input author")
    _require(
        value.get("scientific_status") == "generated_without_learned_checkpoint_access",
        "frozen-input scientific status changed",
    )
    digest_field = "content_sha256_without_this_field"
    _require(
        value.get(digest_field) == content_sha256_without_field(value, digest_field),
        "frozen-input content self-hash mismatch",
    )
    _require(value.get("generator_encoding") == {"0": "R", "1": "F"}, "generator encoding changed")

    episode_rule = value.get("episode_rule")
    _require(isinstance(episode_rule, dict), "missing episode_rule")
    _require(
        episode_rule
        == {
            "episode_seeds": {"0": 940000, "1": 941000},
            "episodes_per_checkpoint": 8,
            "family": "d4",
            "sample_length": 0,
            "visible_starts": list(range(8)),
        },
        "episode rule does not match the registered fresh domain",
    )

    transversal = value.get("base_transversal")
    _require(isinstance(transversal, dict), "missing base_transversal")
    words = transversal.get("words")
    actions = transversal.get("canonical_actions")
    _require(isinstance(words, dict) and isinstance(actions, dict), "invalid base transversal maps")
    _require_exact_keys(words, EXPECTED_TRANSVERSAL_WORDS, "base-transversal words")
    _require_exact_keys(actions, EXPECTED_TRANSVERSAL_WORDS, "base-transversal actions")
    observed_actions: set[tuple[int, ...]] = set()
    for name, expected_word in EXPECTED_TRANSVERSAL_WORDS.items():
        word = _binary_word(words[name], f"base_transversal.words.{name}", nonempty=True)
        _require(word == expected_word, f"base transversal word changed for {name}")
        action = d4_word_action(word)
        _require(action == _CANONICAL_ENDPOINT_ACTIONS[EXPECTED_ENDPOINT_NAMES.index(name)], f"wrong D4 endpoint for {name}")
        _require(actions[name] == list(action), f"serialized canonical action disagrees for {name}")
        observed_actions.add(action)
    _require(len(observed_actions) == 8, "base transversal does not cover all eight D4 elements")
    _require(transversal.get("base_case_count_per_episode") == 64, "base case count must be 8 paths x 8 starts")

    checkpoints = value.get("checkpoints")
    _require(isinstance(checkpoints, dict), "missing checkpoints episode records")
    _require_exact_keys(checkpoints, ("0", "1"), "frozen-input checkpoints")
    serialized_episode_count = 0
    serialized_table_count = 0
    for checkpoint_name, expected_seed in (("0", 940000), ("1", 941000)):
        record = checkpoints[checkpoint_name]
        _require(isinstance(record, dict), f"checkpoint {checkpoint_name} record must be an object")
        _require(record.get("checkpoint_seed") == int(checkpoint_name), "checkpoint seed mismatch")
        _require(record.get("episode_seed") == expected_seed, "episode seed mismatch")
        episodes = record.get("episodes")
        _require(isinstance(episodes, list) and len(episodes) == 8, "each checkpoint must have exactly eight episodes")
        _require(
            [episode.get("episode_index") for episode in episodes] == list(range(8)),
            "episode indices must be exactly 0..7 in order",
        )
        for episode_index, episode in enumerate(episodes):
            _require(isinstance(episode, dict), "episode record must be an object")
            phi = episode.get("phi")
            mapping = episode.get("canonical_to_slot")
            slot_maps = episode.get("slot_maps")
            tables = episode.get("tables")
            _require(isinstance(phi, list) and _is_permutation(phi, 8), f"episode {episode_index} phi is not a permutation")
            _require(isinstance(mapping, list) and _is_permutation(mapping, 2), f"episode {episode_index} canonical_to_slot is not a permutation")
            _require(isinstance(slot_maps, list) and len(slot_maps) == 2, f"episode {episode_index} needs two slot maps")
            _require(isinstance(tables, list) and len(tables) == 2, f"episode {episode_index} needs two tables")
            for slot in range(2):
                slot_map = slot_maps[slot]
                table = tables[slot]
                _require(isinstance(slot_map, list) and _is_permutation(slot_map, 8), f"episode {episode_index} slot {slot} map is not a permutation")
                _require(isinstance(table, list) and len(table) == 8, f"episode {episode_index} slot {slot} table has wrong shape")
                for row_index, row in enumerate(table):
                    _require(
                        isinstance(row, list)
                        and len(row) == 8
                        and all(type(cell) is int and cell in (0, 1) for cell in row),
                        f"episode {episode_index} slot {slot} table is not binary 8x8",
                    )
                    expected_row = [0] * 8
                    expected_row[slot_map[row_index]] = 1
                    _require(row == expected_row, f"episode {episode_index} slot {slot} table disagrees with map")
                serialized_table_count += 1
            serialized_episode_count += 1

    return {
        "passed": True,
        "content_sha256": value[digest_field],
        "checkpoint_count": 2,
        "episode_count": serialized_episode_count,
        "operator_table_count": serialized_table_count,
        "base_transversal_endpoint_count": len(observed_actions),
        "base_cases_per_episode": 64,
    }


def _word_features(word: tuple[int, ...]) -> dict[str, Any]:
    if not word:
        return {
            "length": 0,
            "generator_counts": [0, 0],
            "directed_bigram_counts": [0, 0, 0, 0],
            "run_lengths": [],
            "run_second_moment": 0,
            "maximum_run_length": 0,
        }
    counts = [word.count(0), word.count(1)]
    bigrams = [0, 0, 0, 0]
    for left, right in zip(word, word[1:]):
        bigrams[2 * left + right] += 1
    runs: list[list[int]] = []
    current = word[0]
    length = 1
    for token in word[1:]:
        if token == current:
            length += 1
        else:
            runs.append([current, length])
            current = token
            length = 1
    runs.append([current, length])
    return {
        "length": len(word),
        "generator_counts": counts,
        "directed_bigram_counts": bigrams,
        "run_lengths": runs,
        "run_second_moment": sum(length * length for _, length in runs),
        "maximum_run_length": max(length for _, length in runs),
    }


def _exposure_score(reference: tuple[int, ...], control: tuple[int, ...]) -> list[int]:
    ref_features = _word_features(reference)
    control_features = _word_features(control)
    generator_l1 = sum(abs(a - b) for a, b in zip(ref_features["generator_counts"], control_features["generator_counts"]))
    bigram_l1 = sum(abs(a - b) for a, b in zip(ref_features["directed_bigram_counts"], control_features["directed_bigram_counts"]))
    run_error = abs(ref_features["run_second_moment"] - control_features["run_second_moment"])
    hamming = sum(a != b for a, b in zip(reference, control))
    lexical = 0
    for token in control:
        lexical = (lexical << 1) | token
    return [generator_l1, bigram_l1, run_error, hamming, lexical]


def validate_matched_word_bank(path: Path) -> dict[str, Any]:
    """Independently validate word endpoints, features, counts, and self-hash."""

    value = _load_json(path)
    _require(
        value.get("schema") == "komorebi.neuralese.matched_control_word_bank.v2",
        "unexpected matched-control schema",
    )
    _require(
        value.get("version") == VERSION and value.get("author") == AUTHOR,
        "matched-control version or author changed",
    )
    digest_field = "content_sha256_without_this_field"
    _require(
        value.get(digest_field) == content_sha256_without_field(value, digest_field),
        "matched-control bank content self-hash mismatch",
    )
    _require(value.get("scientific_status") == "combinatorial_word_bank_only_no_learned_execution", "matched-control status changed")
    _require(value.get("parity_sandwich_materialized") is False, "v0.3.1 freezes the lean primary bank only")
    _require(value.get("parity_sandwich_control_word_count") == 0, "unmaterialized parity word count must be zero")
    _require(value.get("control_word_count") == 48, "materialized control count must be 48")
    _require(value.get("canonical_generators") == {"0": "R", "1": "F"}, "matched-control generator encoding changed")
    _require(value.get("endpoint_names_in_token_order") == list(EXPECTED_ENDPOINT_NAMES), "endpoint name order changed")
    _require(tuple(value.get("budgets", ())) == EXPECTED_BUDGETS, "matched-control budgets changed")
    relations = value.get("relations")
    _require(isinstance(relations, dict), "matched-control relations missing")
    _require_exact_keys(relations, EXPECTED_RELATIONS, "matched-control relations")
    for name, expected in EXPECTED_RELATIONS.items():
        _require(_binary_word(relations[name], f"relations.{name}") == expected, f"relation {name} changed")

    representatives = value.get("endpoint_representative_words")
    _require(isinstance(representatives, list) and len(representatives) == 8, "need eight endpoint representatives")
    _require({d4_endpoint_index(_binary_word(word, "endpoint representative")) for word in representatives} == set(range(8)), "endpoint representatives do not cover D4")

    records = value.get("records")
    _require(isinstance(records, list), "matched-control records missing")
    _require(len(records) == 12 and value.get("record_count") == 12, "matched-control bank must have 12 records")
    observed_pairs: set[tuple[str, int]] = set()
    actual_exact_control_count = 0
    actual_parity_word_count = 0
    condition_words: list[tuple[int, ...]] = []
    directed_identity_pair_count = 0
    unordered_identity_pairs: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    for index, record in enumerate(records):
        _require(isinstance(record, dict), f"record {index} must be an object")
        relation = record.get("relation")
        budget = record.get("budget")
        _require(relation in EXPECTED_RELATIONS and budget in EXPECTED_BUDGETS, f"record {index} has unregistered relation/budget")
        pair = (relation, budget)
        _require(pair not in observed_pairs, f"duplicate matched-control record {pair}")
        observed_pairs.add(pair)
        relation_word = EXPECTED_RELATIONS[relation]
        expected_reference = relation_word * (budget // len(relation_word))
        reference = _binary_word(record.get("reference_word"), f"record {index} reference", nonempty=True)
        _require(reference == expected_reference, f"record {index} reference is not the exact repeated relation")
        _require(record.get("reference_word_binary") == "".join(map(str, reference)), f"record {index} reference binary mismatch")
        _require(d4_endpoint_index(reference) == 0 and record.get("reference_endpoint") == "e", f"record {index} reference is not identity")
        _require(record.get("reference_features") == _word_features(reference), f"record {index} reference features mismatch")
        condition_words.append(reference)

        reachable = record.get("exact_length_reachable_endpoint_indices")
        _require(reachable == [0, 2, 5, 7], f"record {index} even-parity endpoint set changed")
        _require(record.get("exact_length_reachable_endpoint_names") == ["e", "R2", "FR", "FR3"], f"record {index} reachable names changed")
        _require(record.get("parity_complement_endpoint_indices") == [1, 3, 4, 6], f"record {index} parity complement changed")
        controls = record.get("exact_length_controls")
        _require(isinstance(controls, list) and len(controls) == 4, f"record {index} needs four exact-length controls")
        _require([control.get("target_endpoint_index") for control in controls] == reachable, f"record {index} control endpoint order changed")
        for control_index, control in enumerate(controls):
            _require(isinstance(control, dict), "control must be an object")
            word = _binary_word(control.get("word"), f"record {index} control {control_index}", nonempty=True)
            endpoint = control.get("target_endpoint_index")
            _require(len(word) == budget, "exact-length control has wrong length")
            _require(d4_endpoint_index(word) == endpoint, "control has wrong D4 endpoint")
            _require(word != reference, "control is not distinct from its reference")
            _require(control.get("endpoint_verified") is True and control.get("distinct_from_reference") is True, "control certificate flags are false")
            _require(control.get("target_endpoint_name") == EXPECTED_ENDPOINT_NAMES[endpoint], "control endpoint name mismatch")
            _require(control.get("word_binary") == "".join(map(str, word)), "control binary serialization mismatch")
            _require(control.get("features") == _word_features(word), "control features mismatch")
            matching = control.get("matching")
            _require(isinstance(matching, dict), "control matching record missing")
            _require(matching.get("score") == _exposure_score(reference, word), "control exposure score mismatch")
            actual_exact_control_count += 1
            condition_words.append(word)
            if endpoint == 0:
                directed_identity_pair_count += 1
                unordered_identity_pairs.add(tuple(sorted((reference, word))))

        sandwiches = record.get("parity_sandwich_controls")
        _require(isinstance(sandwiches, list), "parity sandwich field must be a list")
        if value.get("parity_sandwich_materialized") is True:
            _require(len(sandwiches) == 4, "materialized parity panel needs four endpoint pairs")
            for sandwich in sandwiches:
                _require(isinstance(sandwich, dict), "parity sandwich must be an object")
                endpoint = sandwich.get("target_endpoint_index")
                _require(endpoint in (1, 3, 4, 6), "parity sandwich endpoint must be odd-parity")
                _require(sandwich.get("lower_length") == budget - 1, "lower sandwich length mismatch")
                _require(sandwich.get("upper_length") == budget + 1, "upper sandwich length mismatch")
                for side, expected_length in (("lower_control", budget - 1), ("upper_control", budget + 1)):
                    nested = sandwich.get(side)
                    _require(isinstance(nested, dict), "parity sandwich control missing")
                    word = _binary_word(nested.get("word"), f"{side} word", nonempty=True)
                    _require(len(word) == expected_length and d4_endpoint_index(word) == endpoint, "parity sandwich word has wrong length or endpoint")
                    actual_parity_word_count += 1
        else:
            _require(not sandwiches, "unmaterialized parity panel must have empty record lists")

    _require(observed_pairs == {(relation, budget) for relation in EXPECTED_RELATIONS for budget in EXPECTED_BUDGETS}, "relation-budget grid is incomplete")
    _require(actual_exact_control_count == 48, "exact-length control count is not 48")
    _require(value.get("exact_length_control_word_count") == actual_exact_control_count, "declared exact control count mismatch")
    _require(value.get("control_word_count") == actual_exact_control_count + actual_parity_word_count, "declared materialized control count mismatch")
    distinct_word_count = len(set(condition_words))
    reused_alias_count = len(condition_words) - distinct_word_count
    _require(value.get("condition_count") == len(condition_words) == 60, "condition alias count is not 60")
    _require(value.get("condition_word_entry_count") == len(condition_words), "condition word-entry count mismatch")
    _require(value.get("distinct_word_count") == distinct_word_count == 54, "distinct word count is not 54")
    _require(value.get("reused_condition_alias_count") == reused_alias_count == 6, "reused condition-alias count is not 6")
    _require(value.get("directed_reference_identity_comparison_count") == directed_identity_pair_count == 12, "directed identity-comparison count is not 12")
    _require(value.get("unique_unordered_reference_identity_pair_count") == len(unordered_identity_pairs) == 9, "unique unordered identity-pair count is not 9")
    if value.get("parity_sandwich_materialized") is True:
        _require(value.get("parity_sandwich_control_word_count") == actual_parity_word_count == 96, "declared parity count mismatch")
    else:
        _require(actual_parity_word_count == 0, "unmaterialized bank contains parity controls")

    return {
        "passed": True,
        "content_sha256": value[digest_field],
        "record_count": len(records),
        "reference_word_count": len(records),
        "exact_length_control_word_count": actual_exact_control_count,
        "parity_sandwich_control_word_count_materialized": actual_parity_word_count,
        "total_materialized_word_count": len(records) + actual_exact_control_count + actual_parity_word_count,
        "condition_alias_count": len(condition_words),
        "distinct_word_count": distinct_word_count,
        "reused_condition_alias_count": reused_alias_count,
        "directed_reference_identity_comparison_count": directed_identity_pair_count,
        "unique_unordered_reference_identity_pair_count": len(unordered_identity_pairs),
    }


def validate_preregistration(path: Path) -> dict[str, Any]:
    value = _load_json(path)
    _require(
        value.get("schema")
        == "komorebi.neuralese.entry_cone_holonomy.preregistration.v1",
        "unexpected preregistration schema",
    )
    _require(value.get("version") == VERSION and value.get("author") == AUTHOR, "preregistration identity mismatch")
    _require(value.get("status") == "TO_BE_FROZEN_BEFORE_FRESH_LEARNED_ENDPOINT_EXECUTION", "preregistration is not in pre-endpoint state")
    disclosure = value.get("design_disclosure")
    _require(
        isinstance(disclosure, dict)
        and "spectroscopy and continuation outcomes" in str(
            disclosure.get("old_episode_analysis_status", "")
        )
        and disclosure.get("confirmatory") is False,
        "preregistration design disclosure is incomplete",
    )
    immutable = value.get("immutable_learned_inputs")
    _require(isinstance(immutable, dict), "immutable learned input declaration missing")
    for relative, expected in EXPECTED_CHECKPOINT_DIGESTS.items():
        _require(immutable.get(Path(relative).name) == expected, f"preregistered checkpoint digest changed for {relative}")
    fresh = value.get("fresh_episode_domain")
    _require(isinstance(fresh, dict), "fresh episode domain missing")
    _require(fresh.get("episode_seeds") == {"0": 940000, "1": 941000}, "fresh episode seeds changed")
    _require(fresh.get("episodes_per_checkpoint") == 8, "fresh episode count changed")
    numeric = value.get("numeric_contract")
    _require(
        isinstance(numeric, dict)
        and numeric.get("minimum_valid_pre_normalization_norm") == 1e-12
        and numeric.get("MINIMUM_FACET_NORM") == 1e-14,
        "numeric abort thresholds changed",
    )
    policy = value.get("execution_policy")
    _require(isinstance(policy, dict) and policy.get("freeze_before_endpoint") is True, "freeze-before-endpoint policy missing")
    _require(policy.get("alternate_profiles") == "forbidden in the registered runner", "alternate-profile policy changed")
    _require(policy.get("overwrite") == "forbidden", "overwrite policy changed")
    _require(
        policy.get("registered_run_started") == "results/V031_RUN_STARTED.json",
        "registered run-start ledger changed",
    )
    _require(
        policy.get("runtime_contract")
        == {
            "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
            "python_version": EXPECTED_PYTHON_VERSION,
            "numpy_version": EXPECTED_NUMPY_VERSION,
        },
        "preregistered runtime contract changed",
    )
    _require(
        policy.get("registered_output")
        == "results/V031_ENTRY_CONE_HOLONOMY_RESULTS.json",
        "registered output path changed",
    )
    matched = value.get("matched_control_module")
    _require(isinstance(matched, dict), "matched-control preregistration missing")
    _require(
        matched.get("reference_count") == 12
        and matched.get("exact_length_control_count") == 48
        and matched.get("condition_count") == 60
        and matched.get("total_evaluated_path_count") == 60
        and matched.get("distinct_word_count") == 54
        and matched.get("directed_reference_identity_comparison_count") == 12
        and matched.get("reused_condition_alias_count") == 6
        and matched.get("unique_unordered_reference_identity_pair_count") == 9,
        "matched-control preregistered counts changed",
    )
    path_module = value.get("path_module")
    _require(
        isinstance(path_module, dict)
        and path_module.get("base_cases_per_episode") == 64
        and path_module.get("suffix_horizons") == list(range(9)),
        "path-module registered domain changed",
    )
    composites = value.get("composite_interpretation")
    _require(
        isinstance(composites, dict)
        and composites.get("entry_localized_finite")
        == "E0 and E1 and E2 and E3 and E4"
        and composites.get("finite_observed_cone_safe") == "K0 and K1"
        and composites.get("finite_observed_cone_robust") == "K0 and K1 and K2"
        and composites.get("registered_long_path_exit") == "B0 and P0 and H1"
        and composites.get("registered_broadly_replicated_long_path_exit")
        == "B0 and P0 and H1 and H2"
        and composites.get("registered_delayed_reveal")
        == "B0 and P0 and H1 and H3"
        and composites.get("matched_panel_interpretable") == "M0 and M1",
        "preregistered composite interpretation changed",
    )
    return {"passed": True, "schema": value["schema"], "version": value["version"]}


def validate_prefreeze_validation(path: Path) -> dict[str, Any]:
    value = _load_json(path)
    _require(
        value.get("schema")
        == "komorebi.neuralese.entry_cone_holonomy.prefreeze_validation.v1",
        "unexpected prefreeze-validation schema",
    )
    _require(
        value.get("version") == VERSION and value.get("author") == AUTHOR,
        "prefreeze-validation version or author changed",
    )
    _require(
        value.get("status")
        == "SYNTHETIC_AND_SYMBOLIC_ONLY_NO_FRESH_LEARNED_ENDPOINTS",
        "prefreeze-validation scope changed",
    )
    suite = value.get("unit_suite")
    _require(
        isinstance(suite, dict)
        and suite.get("status") == "PASS"
        and int(suite.get("test_count", -1)) == 75,
        "prefreeze unit-suite record is incomplete",
    )
    synthetic = value.get("full_profile_synthetic_exact_d4")
    _require(isinstance(synthetic, dict), "full synthetic-profile record missing")
    _require(
        synthetic.get("primary_logical_decision_count") == 109_035_136
        and synthetic.get("checkpoint_loader_guard")
        == "installed to raise; no learned checkpoint file was deserialized",
        "full synthetic-profile scope or count changed",
    )
    source_hashes = synthetic.get("validated_source_sha256")
    v031_directory = Path(path).parent
    package_root = v031_directory.parent
    expected_sources = {
        "core.py": package_root / "core.py",
        "checkpoint_io.py": package_root / "checkpoint_io.py",
        "v031/V031_FROZEN_INPUTS.json": v031_directory / "V031_FROZEN_INPUTS.json",
        "v031/V031_MATCHED_WORD_BANK.json": v031_directory
        / "V031_MATCHED_WORD_BANK.json",
        "v031/entry_recurrence_probe.py": v031_directory
        / "entry_recurrence_probe.py",
        "v031/holonomy_spectroscopy.py": v031_directory
        / "holonomy_spectroscopy.py",
        "v031/matched_controls.py": v031_directory / "matched_controls.py",
        "v031/run_v031.py": v031_directory / "run_v031.py",
        "v031/v031_engine.py": v031_directory / "v031_engine.py",
    }
    _require(isinstance(source_hashes, dict), "synthetic-profile source hashes missing")
    _require_exact_keys(source_hashes, expected_sources, "synthetic-profile source hashes")
    for name, source_path in expected_sources.items():
        _require(
            source_hashes[name] == file_sha256(source_path),
            f"synthetic-profile attestation predates the current source: {name}",
        )
    for module in ("entry", "ordinary_cones", "dense_relations", "matched_controls"):
        _require(
            isinstance(synthetic.get(module), dict)
            and synthetic[module].get("status") == "PASS",
            f"prefreeze full synthetic module did not pass: {module}",
        )
    entry_record = synthetic["entry"]
    cone_record = synthetic["ordinary_cones"]
    relation_record = synthetic["dense_relations"]
    matched_record = synthetic["matched_controls"]
    _require(
        entry_record.get("total_decision_count") == 327_040,
        "synthetic entry decision count changed",
    )
    _require(
        cone_record.get("history_state_count") == 65_280
        and cone_record.get("logical_decision_count") == 33_358_080
        and cone_record.get("K0") is True
        and cone_record.get("K1") is True
        and cone_record.get("K2") is True,
        "synthetic cone profile changed",
    )
    _require(
        relation_record.get("configuration_count") == 1_344
        and relation_record.get("logical_decision_count") == 43_954_176
        and relation_record.get("P0_grouped_product_equivalence") is True
        and relation_record.get("H0_no_cone_exit_in_exact_representation") is True,
        "synthetic relation profile changed",
    )
    _require(
        matched_record.get("condition_count") == 60
        and matched_record.get("distinct_word_count") == 54
        and matched_record.get("logical_path_decision_count") == 31_395_840
        and matched_record.get(
            "direct_identity_pair_reused_decision_comparison_count"
        )
        == 6_279_168
        and matched_record.get("M0_same_endpoint_baselines_eligible") is True
        and matched_record.get("M1_exact_bank_executed") is True,
        "synthetic matched-control profile changed",
    )
    scope = value.get("scope")
    _require(
        isinstance(scope, dict)
        and scope.get("learned_checkpoint_deserialization") == "not_performed"
        and scope.get("fresh_940000_941000_learned_endpoint_execution")
        == "not_performed"
        and scope.get("old_930000_931000_spectroscopy")
        == "already disclosed separately in DESIGN_DISCLOSURE.json",
        "prefreeze no-endpoint scope attestation changed",
    )
    return {"passed": True, "unit_test_count": int(suite["test_count"])}


def validate_digest_map(package_root: Path, digest_map: Mapping[str, str]) -> dict[str, str]:
    """Validate an exact root-relative digest map and reject unsafe paths."""

    root = Path(package_root).resolve()
    observed: dict[str, str] = {}
    for relative, expected in sorted(digest_map.items()):
        _require(isinstance(relative, str) and relative, "freeze contains an invalid path key")
        relative_path = Path(relative)
        _require(not relative_path.is_absolute() and ".." not in relative_path.parts, f"unsafe frozen path: {relative}")
        path = (root / relative_path).resolve()
        try:
            path.relative_to(root)
        except ValueError as error:
            raise FreezeValidationError(f"frozen path escapes package root: {relative}") from error
        _require(path.is_file(), f"missing frozen file: {relative}")
        actual = file_sha256(path)
        _require(actual == expected, f"digest mismatch for {relative}: {actual} != {expected}")
        observed[relative] = actual
    return observed


def _structural_test_command(v031_directory: Path) -> list[str]:
    # Explicit modules avoid accidentally enrolling an unreviewed exploratory
    # file merely because its filename happens to match a broad glob.
    return [
        sys.executable,
        "-B",
        "-Werror",
        "-m",
        "unittest",
        "-v",
        *(Path(name).stem for name in EXPECTED_TEST_FILES),
    ]


def run_structural_tests(v031_directory: Path) -> dict[str, Any]:
    source_v031 = Path(v031_directory).resolve()
    source_root = source_v031.parent
    # Run from a learned-input-free copy.  The tests retain the exact frozen
    # source/data bytes, while checkpoint deserialization is mechanically
    # impossible because neither checkpoint is present in the sandbox.
    with tempfile.TemporaryDirectory(prefix="komorebi-v031-structural-") as temporary:
        sandbox_root = Path(temporary) / "package"
        for relative in REQUIRED_ROOT_RELATIVE_FILES:
            if relative in EXPECTED_CHECKPOINT_DIGESTS:
                continue
            source = source_root / relative
            target = sandbox_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        _require(
            not any((sandbox_root / relative).exists() for relative in EXPECTED_CHECKPOINT_DIGESTS),
            "structural-test sandbox unexpectedly contains a learned checkpoint",
        )
        command = _structural_test_command(sandbox_root / "v031")
        environment = dict(os.environ)
        environment["KOMOREBI_V031_PREENDPOINT_STRUCTURAL_ONLY"] = "1"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            command,
            cwd=sandbox_root / "v031",
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    print(completed.stdout, end="")
    if completed.returncode != 0:
        raise FreezeValidationError("synthetic structural tests failed; no freeze written")
    match = re.search(r"Ran (\d+) tests?", completed.stdout)
    _require(match is not None, "could not parse structural test count")
    count = int(match.group(1))
    _require(count >= 20, f"too few structural tests ({count}); expected at least 20")
    return {
        "status": "PASS",
        "command": " ".join(command),
        "test_count": count,
        "preendpoint_guard_environment": "KOMOREBI_V031_PREENDPOINT_STRUCTURAL_ONLY=1",
        "isolated_test_sandbox": True,
        "learned_checkpoint_files_present_in_test_sandbox": False,
        "learned_checkpoint_deserialization": "not_performed",
        "learned_endpoint_execution": "not_performed",
    }


def build_execution_freeze(package_root: Path, structural_validation: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(package_root).resolve()
    runtime_validation = validate_runtime_contract()
    bytecode_validation = validate_no_executable_bytecode(root)
    _require(
        (root / "v031/requirements.txt").read_text(encoding="utf-8")
        == "numpy==2.3.5\n",
        "v0.3.1 numerical requirements are not exactly pinned",
    )
    _require_exact_keys(
        REQUIRED_ROOT_RELATIVE_FILES,
        REQUIRED_ROOT_RELATIVE_FILES,
        "internal required-file declaration",
    )
    files: dict[str, str] = {}
    for relative in REQUIRED_ROOT_RELATIVE_FILES:
        path = root / relative
        _require(path.is_file(), f"missing required freeze input: {relative}")
        files[relative] = file_sha256(path)
    for relative, expected in EXPECTED_CHECKPOINT_DIGESTS.items():
        _require(files[relative] == expected, f"checkpoint digest differs from preregistration: {relative}")

    preregistration_validation = validate_preregistration(root / "v031/V031_PREREGISTRATION.json")
    frozen_input_validation = validate_frozen_inputs(root / "v031/V031_FROZEN_INPUTS.json")
    word_bank_validation = validate_matched_word_bank(root / "v031/V031_MATCHED_WORD_BANK.json")
    prefreeze_validation = validate_prefreeze_validation(
        root / "v031/V031_PREFREEZE_VALIDATION.json"
    )
    _require(structural_validation.get("status") == "PASS", "structural validation did not pass")

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "date": "2026-09-03",
        "status": "FROZEN_BEFORE_FRESH_LEARNED_ENDPOINT_EXECUTION",
        "attestation": EXPECTED_ATTESTATION,
        "design_disclosure": {
            "path": "DESIGN_DISCLOSURE.json",
            "old_930000_931000_spectroscopy_and_continuations": (
                "exploratory_design_context_only"
            ),
            "fresh_940000_941000_endpoints": "prospective_relative_to_exact_frozen_realizations",
            "confirmatory": False,
        },
        "runtime_contract": runtime_validation,
        "files": files,
        "registered_profile": EXPECTED_REGISTERED_PROFILE,
        "preexecution_validation": {
            "preregistration": preregistration_validation,
            "frozen_inputs": frozen_input_validation,
            "matched_word_bank": word_bank_validation,
            "prefreeze_validation": prefreeze_validation,
            "structural_tests": dict(structural_validation),
            "bytecode_absence": bytecode_validation,
        },
    }


def validate_execution_freeze(freeze_path: Path, package_root: Path | None = None) -> dict[str, Any]:
    path = Path(freeze_path).resolve()
    root = Path(package_root).resolve() if package_root is not None else path.parent.parent
    value = _load_json(path)
    _require(value.get("schema") == SCHEMA, "unexpected execution-freeze schema")
    _require(value.get("version") == VERSION and value.get("author") == AUTHOR, "execution-freeze identity mismatch")
    _require(value.get("status") == "FROZEN_BEFORE_FRESH_LEARNED_ENDPOINT_EXECUTION", "execution freeze has wrong status")
    _require(value.get("attestation") == EXPECTED_ATTESTATION, "execution-freeze attestation changed")
    _require(
        value.get("runtime_contract")
        == {
            "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
            "python_version": EXPECTED_PYTHON_VERSION,
            "numpy_version": EXPECTED_NUMPY_VERSION,
        },
        "execution-freeze runtime contract changed",
    )
    disclosure = value.get("design_disclosure")
    _require(
        isinstance(disclosure, dict)
        and disclosure.get("path") == "DESIGN_DISCLOSURE.json"
        and disclosure.get("old_930000_931000_spectroscopy_and_continuations")
        == "exploratory_design_context_only"
        and disclosure.get("fresh_940000_941000_endpoints")
        == "prospective_relative_to_exact_frozen_realizations"
        and disclosure.get("confirmatory") is False,
        "execution-freeze design disclosure changed",
    )
    files = value.get("files")
    _require(isinstance(files, dict), "execution freeze has no file map")
    _require_exact_keys(files, REQUIRED_ROOT_RELATIVE_FILES, "execution-freeze files")
    _require(
        value.get("registered_profile") == EXPECTED_REGISTERED_PROFILE,
        "execution-freeze registered profile changed",
    )
    preexecution = value.get("preexecution_validation")
    _require(isinstance(preexecution, dict), "execution freeze lacks preexecution validation")
    _require_exact_keys(
        preexecution,
        (
            "preregistration",
            "frozen_inputs",
            "matched_word_bank",
            "prefreeze_validation",
            "structural_tests",
            "bytecode_absence",
        ),
        "preexecution validation",
    )
    for label in (
        "preregistration",
        "frozen_inputs",
        "matched_word_bank",
        "prefreeze_validation",
        "bytecode_absence",
    ):
        _require(
            isinstance(preexecution[label], dict)
            and preexecution[label].get("passed") is True,
            f"preexecution validation did not pass: {label}",
        )
    structural = preexecution["structural_tests"]
    _require(
        isinstance(structural, dict)
        and structural.get("status") == "PASS"
        and int(structural.get("test_count", -1)) == 75
        and structural.get("isolated_test_sandbox") is True
        and structural.get("learned_checkpoint_files_present_in_test_sandbox") is False
        and structural.get("learned_checkpoint_deserialization") == "not_performed"
        and structural.get("learned_endpoint_execution") == "not_performed",
        "structural preexecution validation is incomplete",
    )
    validated = validate_digest_map(root, files)
    for relative, expected in EXPECTED_CHECKPOINT_DIGESTS.items():
        _require(validated[relative] == expected, f"checkpoint digest mismatch in execution freeze: {relative}")
    return {
        "passed": True,
        "freeze_sha256": file_sha256(path),
        "validated_file_count": len(validated),
        "status": value["status"],
    }


def _atomic_create_json(path: Path, value: Mapping[str, Any]) -> None:
    target = Path(path)
    if target.exists():
        raise FileExistsError(f"refusing to overwrite existing execution freeze: {target}")
    temporary = target.with_name(f".{target.name}.tmp-{os.getpid()}")
    if temporary.exists():
        raise FileExistsError(f"refusing to reuse temporary path: {temporary}")
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        # A hard link is an atomic create-if-absent operation: unlike
        # check-then-replace, it cannot overwrite a freeze won by another
        # process in the intervening race window.
        os.link(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="v0.3.1 package root; defaults to the parent of v031/",
    )
    args = parser.parse_args(argv)
    root = args.package_root.resolve()
    v031 = root / "v031"
    target = v031 / TARGET_NAME
    if target.exists():
        raise SystemExit(f"refusing to overwrite existing execution freeze: {target}")
    try:
        validate_runtime_contract()
        validate_no_executable_bytecode(root)
        structural = run_structural_tests(v031)
        payload = build_execution_freeze(root, structural)
        _atomic_create_json(target, payload)
        validation = validate_execution_freeze(target, root)
    except (FreezeValidationError, FileExistsError, OSError) as error:
        raise SystemExit(f"FREEZE_ABORTED={error}") from error
    print(f"V031_EXECUTION_FREEZE={target}")
    print(f"EXECUTION_FREEZE_SHA256={validation['freeze_sha256']}")
    print(f"VALIDATED_FILE_COUNT={validation['validated_file_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
