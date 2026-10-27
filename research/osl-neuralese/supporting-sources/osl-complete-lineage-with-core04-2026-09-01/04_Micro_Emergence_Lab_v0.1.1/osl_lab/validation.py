"""Integrity and semantic validation for generated Micro OSL datasets."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from .generator import (
    DATASET_SCHEMA_VERSION,
    EVALUATION_NONCE_POOL,
    EVALUATION_SPLITS,
    GENERATOR_VERSION,
    HELDOUT_PAIRS,
    HELDOUT_TRIPLES,
    LEXICAL_SURFACE_MARKER_POOLS,
    SPLITS,
    TRAINING_SPLITS,
    TRAIN_NONCE_POOL,
    TRAIN_SURFACE_MARKER_POOLS,
    VALIDATION_SPLITS,
    dataset_digest,
    load_dataset,
)
from .renderers import render_answer
from .worlds import (
    canonical_transformation_id,
    execute,
    get_world,
    normalize_program,
    query_answers,
    validate_state,
)


@dataclass(frozen=True)
class ValidationReport:
    """Machine-readable dataset adjudication."""

    errors: tuple[dict[str, Any], ...]
    warnings: tuple[dict[str, Any], ...]
    statistics: Mapping[str, Any]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": [dict(issue) for issue in self.errors],
            "warnings": [dict(issue) for issue in self.warnings],
            "statistics": dict(self.statistics),
        }


def _issue(code: str, message: str, record_id: str | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"code": code, "message": message}
    if record_id is not None:
        value["record_id"] = record_id
    return value


def validate_record(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Re-execute and validate one record, returning error dictionaries."""

    errors: list[dict[str, Any]] = []
    record_id = str(record.get("id", "<missing>"))
    required = (
        "id",
        "split",
        "world",
        "semantic_id",
        "renderer",
        "story",
        "question_id",
        "question",
        "answer",
        "metadata",
    )
    missing = [key for key in required if key not in record]
    if missing:
        errors.append(_issue("record.missing_fields", f"missing fields: {missing}", record_id))
        return errors
    if record["split"] not in SPLITS:
        errors.append(_issue("record.bad_split", f"unknown split {record['split']!r}", record_id))
    try:
        spec = get_world(str(record["world"]))
    except Exception as exc:
        errors.append(_issue("record.bad_world", str(exc), record_id))
        return errors
    if record["question_id"] not in spec.query_ids:
        errors.append(
            _issue(
                "record.bad_query",
                f"query {record['question_id']!r} is not defined in {spec.name}",
                record_id,
            )
        )
        return errors
    metadata = record["metadata"]
    if not isinstance(metadata, Mapping):
        errors.append(_issue("record.bad_metadata", "metadata must be an object", record_id))
        metadata = {}
    formal_keys = {"initial_state", "program", "final_state", "canonical_transform_id"}
    present_formal = formal_keys.intersection(record)
    if present_formal and present_formal != formal_keys:
        errors.append(
            _issue(
                "record.partial_formal_fields",
                f"formal fields must be all present or all absent; found {sorted(present_formal)}",
                record_id,
            )
        )
        return errors
    if not present_formal:
        return errors
    try:
        initial = dict(record["initial_state"])
        validate_state(spec, initial)
        program = normalize_program(record["program"])
        execution = execute(spec, initial, program)
    except Exception as exc:
        errors.append(_issue("record.execution_failed", str(exc), record_id))
        return errors
    if dict(record["final_state"]) != execution.final_state:
        errors.append(_issue("record.wrong_final_state", "stored final state disagrees with replay", record_id))
    if "state_trace" in record:
        stored_trace = [dict(state) for state in record["state_trace"]]
        if stored_trace != list(execution.states):
            errors.append(_issue("record.wrong_state_trace", "stored trace disagrees with replay", record_id))
    expected_transform = canonical_transformation_id(spec, program)
    if record["canonical_transform_id"] != expected_transform:
        errors.append(
            _issue(
                "record.wrong_transform_id",
                "canonical transformation identifier disagrees with exact enumeration",
                record_id,
            )
        )
    abstract_answer = query_answers(spec, execution.final_state)[str(record["question_id"])]
    lexicon = str(metadata.get("lexicon", "train"))
    expected_answer = abstract_answer
    if record["answer"] != expected_answer:
        errors.append(
            _issue(
                "record.wrong_answer",
                f"stored answer {record['answer']!r} != exact answer {expected_answer!r}",
                record_id,
            )
        )
    expected_answer_text = render_answer(
        spec.name, str(record["question_id"]), abstract_answer, lexicon
    )
    if "answer_text" in record and record["answer_text"] != expected_answer_text:
        errors.append(
            _issue(
                "record.wrong_answer_text",
                f"stored answer text {record['answer_text']!r} != rendered answer {expected_answer_text!r}",
                record_id,
            )
        )
    if metadata.get("program_length") != len(program):
        errors.append(_issue("record.wrong_length", "metadata program_length is incorrect", record_id))
    return errors


def _load_source(
    source: Mapping[str, Sequence[Mapping[str, Any]]] | str | Path,
) -> tuple[dict[str, list[dict[str, Any]]], Path | None, dict[str, Any] | None]:
    if isinstance(source, Mapping):
        return (
            {split: [dict(record) for record in records] for split, records in source.items()},
            None,
            None,
        )
    path = Path(source)
    if path.is_file() and path.suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            records = [json.loads(line) for line in handle if line.strip()]
        split = str(records[0].get("split", path.stem)) if records else path.stem
        return {split: records}, path.parent, None
    dataset = load_dataset(path)
    manifest_path = path / "manifest.json"
    manifest = None
    if manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
    return dataset, path, manifest


def _validate_counterfactual_groups(
    records: Sequence[Mapping[str, Any]],
    errors: list[dict[str, Any]],
) -> None:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        metadata = record.get("metadata", {})
        pair_id = metadata.get("pair_id") if isinstance(metadata, Mapping) else None
        if not pair_id:
            errors.append(_issue("counterfactual.missing_pair", "counterfactual record lacks pair_id", str(record.get("id"))))
            continue
        groups[str(pair_id)].append(record)
    for pair_id, pair in groups.items():
        worlds = {str(record.get("world")) for record in pair}
        if len(worlds) != 1:
            errors.append(_issue("counterfactual.mixed_worlds", f"pair {pair_id} spans worlds {sorted(worlds)}"))
            continue
        world = next(iter(worlds))
        expected_queries = set(get_world(world).query_ids)
        by_query: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for record in pair:
            by_query[str(record.get("question_id"))].append(record)
        if set(by_query) != expected_queries:
            errors.append(
                _issue(
                    "counterfactual.incomplete_queries",
                    f"pair {pair_id} covers {sorted(by_query)}, expected {sorted(expected_queries)}",
                )
            )
        expected_size = 2 * len(expected_queries)
        if len(pair) != expected_size:
            errors.append(
                _issue(
                    "counterfactual.bad_bundle_size",
                    f"pair {pair_id} has {len(pair)} records, expected {expected_size}",
                )
            )
        reference_initial = pair[0].get("initial_state")
        marker_signatures = {
            json.dumps(record.get("metadata", {}).get("surface_marker"), sort_keys=True)
            for record in pair
        }
        if len(marker_signatures) != 1:
            errors.append(
                _issue(
                    "counterfactual.surface_marker_mismatch",
                    f"pair {pair_id} does not share one nuisance marker",
                )
            )
        changed_sets = {
            tuple(sorted(record.get("metadata", {}).get("changed_query_ids", [])))
            for record in pair
        }
        if len(changed_sets) != 1:
            errors.append(_issue("counterfactual.inconsistent_change_set", f"pair {pair_id} has inconsistent changed_query_ids"))
        for query_id, query_pair in by_query.items():
            by_variant = {
                str(record.get("metadata", {}).get("variant")): record
                for record in query_pair
            }
            if len(query_pair) != 2 or set(by_variant) != {"base", "counterfactual"}:
                errors.append(
                    _issue(
                        "counterfactual.bad_variants",
                        f"pair {pair_id}, query {query_id} lacks exactly one base and one counterfactual",
                    )
                )
                continue
            base, changed = by_variant["base"], by_variant["counterfactual"]
            if base.get("initial_state") != changed.get("initial_state") or base.get("initial_state") != reference_initial:
                errors.append(_issue("counterfactual.unmatched_initial", f"pair {pair_id} has different initial states"))
            expected_change = bool(base["metadata"].get("query_expected_to_change"))
            observed_change = base.get("answer") != changed.get("answer")
            if expected_change != observed_change:
                errors.append(
                    _issue(
                        "counterfactual.wrong_change_flag",
                        f"pair {pair_id}, query {query_id}: expected_change={expected_change} but observed={observed_change}",
                    )
                )


def _expected_split_role(split: str) -> str:
    if split in TRAINING_SPLITS:
        return "training"
    if split in VALIDATION_SPLITS:
        return "validation"
    if split in EVALUATION_SPLITS:
        return "evaluation"
    return "unknown"


def _contains_subsequence(program: Sequence[str], pattern: Sequence[str]) -> bool:
    width = len(pattern)
    return any(
        tuple(program[index : index + width]) == tuple(pattern)
        for index in range(len(program) - width + 1)
    )


def _validate_surface_marker(
    record: Mapping[str, Any],
    errors: list[dict[str, Any]],
) -> tuple[str, str, str] | None:
    record_id = str(record.get("id", "<missing>"))
    metadata = record.get("metadata", {})
    if not isinstance(metadata, Mapping):
        return None
    marker = metadata.get("surface_marker")
    if not isinstance(marker, Mapping):
        errors.append(_issue("surface_marker.missing", "record lacks audited surface marker metadata", record_id))
        return None
    lexicon = str(metadata.get("lexicon", "train"))
    if lexicon == "train":
        expected_family = "train"
        first_pool, second_pool = TRAIN_SURFACE_MARKER_POOLS
    elif lexicon == "lexical":
        expected_family = "lexical"
        first_pool, second_pool = LEXICAL_SURFACE_MARKER_POOLS
    else:
        errors.append(_issue("surface_marker.bad_lexicon", f"unknown marker lexicon {lexicon!r}", record_id))
        return None
    family = str(marker.get("family", ""))
    first = str(marker.get("first", ""))
    second = str(marker.get("second", ""))
    if family != expected_family or first not in first_pool or second not in second_pool:
        errors.append(
            _issue(
                "surface_marker.wrong_pool",
                "surface marker does not belong to the record's lexicon-specific pool",
                record_id,
            )
        )
    expected_prefix = f"Case markers {first} and {second} were assigned before review. "
    if not str(record.get("story", "")).startswith(expected_prefix):
        errors.append(
            _issue(
                "surface_marker.story_mismatch",
                "story prefix disagrees with audited surface marker metadata",
                record_id,
            )
        )
    return family, first, second


def _validate_nonce_record(
    record: Mapping[str, Any],
    expected_pool: set[str],
    expected_pool_name: str,
    errors: list[dict[str, Any]],
) -> set[str]:
    record_id = str(record.get("id", "<missing>"))
    metadata = record.get("metadata", {})
    if not isinstance(metadata, Mapping):
        return set()
    mapping = metadata.get("operator_mapping", {})
    commands = metadata.get("target_commands", [])
    if not isinstance(mapping, Mapping) or not mapping:
        errors.append(_issue("renaming.bad_mapping", "renamed record lacks an operator mapping", record_id))
        return set()
    nonce_tokens = {str(token) for token in mapping}
    if not nonce_tokens <= expected_pool:
        errors.append(
            _issue(
                "renaming.wrong_nonce_pool",
                f"record uses nonces outside the {expected_pool_name} pool",
                record_id,
            )
        )
    if metadata.get("nonce_pool") != expected_pool_name:
        errors.append(
            _issue(
                "renaming.bad_pool_marker",
                f"nonce_pool must be {expected_pool_name!r}",
                record_id,
            )
        )
    world = str(record.get("world"))
    try:
        expected_operators = set(get_world(world).operators)
    except Exception:
        expected_operators = set()
    mapped_operators = {str(operator) for operator in mapping.values()}
    if mapped_operators != expected_operators or len(mapping) != len(expected_operators):
        errors.append(
            _issue(
                "renaming.incomplete_bijection",
                "operator mapping must be a bijection over every operator in the world",
                record_id,
            )
        )
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes)):
        errors.append(_issue("renaming.bad_commands", "target_commands must be a sequence", record_id))
        return nonce_tokens
    if any(command not in mapping for command in commands):
        errors.append(_issue("renaming.unmapped_command", "mapping does not cover target commands", record_id))
    if "program" in record:
        expected_program = list(normalize_program(record["program"]))
        observed_program = [str(mapping[command]) for command in commands if command in mapping]
        if observed_program != expected_program:
            errors.append(
                _issue(
                    "renaming.command_program_mismatch",
                    "nonce commands do not decode to the stored formal program",
                    record_id,
                )
            )
    if "Calibration:" not in str(record.get("story", "")):
        errors.append(_issue("renaming.missing_calibration", "renamed story lacks calibration demonstrations", record_id))
    return nonce_tokens


_MODEL_TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\w\s]", re.UNICODE)


def _validate_scrambled_match(
    correct: Mapping[str, Any],
    scrambled: Mapping[str, Any],
    pair_id: str,
    errors: list[dict[str, Any]],
) -> None:
    invariant_fields = (
        "world",
        "semantic_id",
        "renderer",
        "question_id",
        "question",
        "answer",
        "answer_text",
        "initial_state",
        "program",
        "canonical_transform_id",
        "state_trace",
        "final_state",
    )
    different = [key for key in invariant_fields if correct.get(key) != scrambled.get(key)]
    if different:
        errors.append(
            _issue(
                "renaming.scrambled_semantic_mismatch",
                f"pair {pair_id} differs on invariant fields {different}",
            )
        )
    correct_metadata = correct.get("metadata", {})
    scrambled_metadata = scrambled.get("metadata", {})
    paired_metadata = (
        "episode_id",
        "pair_id",
        "nonce_pool",
        "operator_mapping",
        "target_commands",
        "render_seed",
        "surface_marker",
    )
    metadata_differences = [
        key
        for key in paired_metadata
        if correct_metadata.get(key) != scrambled_metadata.get(key)
    ]
    if metadata_differences:
        errors.append(
            _issue(
                "renaming.scrambled_metadata_mismatch",
                f"pair {pair_id} differs on matched metadata {metadata_differences}",
            )
        )
    commands = tuple(str(value) for value in correct_metadata.get("target_commands", ()))
    used = tuple(dict.fromkeys(commands))
    if len(used) < 2:
        errors.append(
            _issue(
                "renaming.scramble_not_identifiable",
                f"pair {pair_id} uses fewer than two distinct target operators",
            )
        )
        return
    correct_permutation = correct_metadata.get("calibration_label_permutation", {})
    expected_identity = {token: token for token in used}
    if correct_permutation != expected_identity:
        errors.append(
            _issue(
                "renaming.correct_calibration_not_identity",
                f"pair {pair_id} correct calibration is not the identity alignment",
            )
        )
    permutation = scrambled_metadata.get("calibration_label_permutation", {})
    if not isinstance(permutation, Mapping):
        errors.append(_issue("renaming.bad_scramble_permutation", f"pair {pair_id} lacks a scramble permutation"))
        return
    normalized_permutation = {str(key): str(value) for key, value in permutation.items()}
    if set(normalized_permutation) != set(used) or set(normalized_permutation.values()) != set(used):
        errors.append(
            _issue(
                "renaming.bad_scramble_permutation",
                f"pair {pair_id} permutation is not a bijection over used commands",
            )
        )
        return
    if all(normalized_permutation[token] == token for token in used):
        errors.append(_issue("renaming.identity_scramble", f"pair {pair_id} uses an identity scramble"))

    correct_story = str(correct.get("story", ""))
    scrambled_story = str(scrambled.get("story", ""))
    correct_tokens = _MODEL_TOKEN_PATTERN.findall(correct_story.lower())
    scrambled_tokens = _MODEL_TOKEN_PATTERN.findall(scrambled_story.lower())
    if Counter(correct_tokens) != Counter(scrambled_tokens):
        errors.append(
            _issue(
                "renaming.scrambled_token_multiset_mismatch",
                f"pair {pair_id} does not preserve the exact model-token multiset",
            )
        )
    target_marker = "At the start of the target episode,"
    if target_marker not in correct_story or target_marker not in scrambled_story:
        errors.append(_issue("renaming.missing_target_marker", f"pair {pair_id} lacks a target marker"))
        return
    correct_calibration, correct_target = correct_story.split(target_marker, 1)
    _, scrambled_target = scrambled_story.split(target_marker, 1)
    if correct_target != scrambled_target:
        errors.append(
            _issue(
                "renaming.scrambled_target_changed",
                f"pair {pair_id} changed target commands or target formatting",
            )
        )
    pattern = re.compile(r"\b(?:" + "|".join(map(re.escape, used)) + r")\b")
    expected_calibration = pattern.sub(
        lambda match: normalized_permutation[match.group(0)],
        correct_calibration,
    )
    expected_story = expected_calibration + target_marker + correct_target
    if scrambled_story != expected_story:
        errors.append(
            _issue(
                "renaming.scrambled_format_mismatch",
                f"pair {pair_id} changes more than calibration nonce labels",
            )
        )


def _validate_renaming_protocol(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
    errors: list[dict[str, Any]],
) -> tuple[set[str], set[str]]:
    training_nonces: set[str] = set()
    evaluation_nonces: set[str] = set()
    training_groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for split in ("renaming_train", "renaming_scrambled_train"):
        for record in dataset.get(split, []):
            training_nonces.update(
                _validate_nonce_record(
                    record,
                    set(TRAIN_NONCE_POOL),
                    "training",
                    errors,
                )
            )
            metadata = record.get("metadata", {})
            pair_id = metadata.get("pair_id") if isinstance(metadata, Mapping) else None
            if not pair_id:
                errors.append(
                    _issue(
                        "renaming.training_missing_pair",
                        f"{split} record lacks pair_id",
                        str(record.get("id")),
                    )
                )
                continue
            training_groups[str(pair_id)].append(record)

    for pair_id, pair in training_groups.items():
        by_variant = {
            str(record.get("metadata", {}).get("variant")): record for record in pair
        }
        if len(pair) != 2 or set(by_variant) != {"correct", "scrambled"}:
            errors.append(
                _issue(
                    "renaming.bad_training_pair_variants",
                    f"training pair {pair_id} must contain one correct and one scrambled record",
                )
            )
            continue
        correct = by_variant["correct"]
        scrambled = by_variant["scrambled"]
        if correct.get("split") != "renaming_train" or scrambled.get("split") != "renaming_scrambled_train":
            errors.append(
                _issue(
                    "renaming.training_pair_wrong_split",
                    f"training pair {pair_id} variants are in the wrong shards",
                )
            )
        _validate_scrambled_match(correct, scrambled, pair_id, errors)

    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in dataset.get("renaming", []):
        metadata = record.get("metadata", {})
        pair_id = metadata.get("pair_id") if isinstance(metadata, Mapping) else None
        if not pair_id:
            errors.append(_issue("renaming.missing_pair", "evaluation renaming record lacks pair_id", str(record.get("id"))))
            continue
        groups[str(pair_id)].append(record)

    for pair_id, pair in groups.items():
        by_variant = {
            str(record.get("metadata", {}).get("variant")): record for record in pair
        }
        if len(pair) != 3 or set(by_variant) != {"canonical", "renamed", "scrambled"}:
            errors.append(
                _issue(
                    "renaming.bad_pair_variants",
                    f"pair {pair_id} must contain canonical, renamed, and scrambled records",
                )
            )
            continue
        canonical = by_variant["canonical"]
        renamed = by_variant["renamed"]
        scrambled = by_variant["scrambled"]
        invariant_fields = (
            "world",
            "semantic_id",
            "renderer",
            "question_id",
            "question",
            "answer",
            "answer_text",
            "initial_state",
            "program",
            "canonical_transform_id",
            "state_trace",
            "final_state",
        )
        different = [
            key
            for key in invariant_fields
            if canonical.get(key) != renamed.get(key)
            or canonical.get(key) != scrambled.get(key)
        ]
        if different:
            errors.append(
                _issue(
                    "renaming.pair_semantic_mismatch",
                    f"pair {pair_id} differs on invariant fields {different}",
                )
            )
        canonical_metadata = canonical.get("metadata", {})
        renamed_metadata = renamed.get("metadata", {})
        scrambled_metadata = scrambled.get("metadata", {})
        if not (
            canonical_metadata.get("episode_id")
            == renamed_metadata.get("episode_id")
            == scrambled_metadata.get("episode_id")
        ):
            errors.append(_issue("renaming.pair_episode_mismatch", f"pair {pair_id} has mismatched episode IDs"))
        if not (
            canonical_metadata.get("surface_marker")
            == renamed_metadata.get("surface_marker")
            == scrambled_metadata.get("surface_marker")
        ):
            errors.append(_issue("renaming.pair_marker_mismatch", f"pair {pair_id} has mismatched nuisance markers"))
        if "operator_mapping" in canonical_metadata or "target_commands" in canonical_metadata:
            errors.append(
                _issue(
                    "renaming.canonical_has_nonce_fields",
                    f"canonical member of pair {pair_id} contains nonce-only metadata",
                )
            )
        if "Calibration:" in str(canonical.get("story", "")):
            errors.append(_issue("renaming.canonical_is_calibrated", f"canonical member of pair {pair_id} contains calibration text"))
        evaluation_nonces.update(
            _validate_nonce_record(
                renamed,
                set(EVALUATION_NONCE_POOL),
                "evaluation",
                errors,
            )
        )
        evaluation_nonces.update(
            _validate_nonce_record(
                scrambled,
                set(EVALUATION_NONCE_POOL),
                "evaluation",
                errors,
            )
        )
        _validate_scrambled_match(renamed, scrambled, pair_id, errors)

    if training_nonces & evaluation_nonces:
        errors.append(
            _issue(
                "renaming.nonce_pool_overlap",
                "observed training and evaluation nonce vocabularies overlap",
            )
        )
    return training_nonces, evaluation_nonces


def _validate_balancing(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
    errors: list[dict[str, Any]],
) -> None:
    active_worlds = sorted(
        {
            str(record.get("world"))
            for records in dataset.values()
            for record in records
            if str(record.get("world")) in {"algebra", "provenance", "resources"}
        }
    )
    if not active_worlds:
        return
    ordinary = tuple(
        split
        for split in VALIDATION_SPLITS + EVALUATION_SPLITS
        if split not in {"counterfactual", "renaming"}
    )
    for split in ordinary:
        records = dataset.get(split, [])
        if not records:
            continue
        world_counts = Counter(str(record.get("world")) for record in records)
        values = [world_counts[world] for world in active_worlds]
        if max(values) - min(values) > 1:
            errors.append(_issue("dataset.unbalanced_worlds", f"{split} world counts are {dict(world_counts)}"))
        for world in active_worlds:
            query_counts = Counter(
                str(record.get("question_id"))
                for record in records
                if record.get("world") == world
            )
            query_values = [query_counts[query] for query in get_world(world).query_ids]
            if query_values and max(query_values) - min(query_values) > 1:
                errors.append(
                    _issue(
                        "dataset.unbalanced_queries",
                        f"{split}/{world} query counts are {dict(query_counts)}",
                    )
                )

    renaming = dataset.get("renaming", [])
    if renaming:
        world_counts = Counter(str(record.get("world")) for record in renaming)
        values = [world_counts[world] for world in active_worlds]
        if max(values) - min(values) > 3:
            errors.append(_issue("dataset.unbalanced_worlds", f"renaming world counts are {dict(world_counts)}"))
        for world in active_worlds:
            query_counts = Counter(
                str(record.get("question_id"))
                for record in renaming
                if record.get("world") == world
            )
            query_values = [query_counts[query] for query in get_world(world).query_ids]
            if query_values and max(query_values) - min(query_values) > 3:
                errors.append(
                    _issue(
                        "dataset.unbalanced_queries",
                        f"renaming/{world} query counts are {dict(query_counts)}",
                    )
                )

    counterfactual = dataset.get("counterfactual", [])
    if counterfactual:
        world_counts = Counter(str(record.get("world")) for record in counterfactual)
        values = [world_counts[world] for world in active_worlds]
        tolerance = max(2 * len(get_world(world).query_ids) for world in active_worlds)
        if max(values) - min(values) > tolerance:
            errors.append(_issue("dataset.unbalanced_worlds", f"counterfactual world counts are {dict(world_counts)}"))


def _validate_manifest(
    root: Path,
    manifest: Mapping[str, Any],
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
    errors: list[dict[str, Any]],
) -> None:
    if manifest.get("format") != "micro-osl-jsonl-v1.1":
        errors.append(_issue("manifest.bad_format", "manifest format must be micro-osl-jsonl-v1.1"))
    if manifest.get("schema_version") != DATASET_SCHEMA_VERSION:
        errors.append(_issue("manifest.bad_schema_version", f"schema version must be {DATASET_SCHEMA_VERSION}"))
    if manifest.get("generator_version") != GENERATOR_VERSION:
        errors.append(_issue("manifest.bad_generator_version", f"generator version must be {GENERATOR_VERSION}"))
    files = manifest.get("files", {})
    if not isinstance(files, Mapping):
        errors.append(_issue("manifest.bad_files", "manifest files field must be an object"))
        return
    for split, descriptor in files.items():
        if not isinstance(descriptor, Mapping):
            errors.append(_issue("manifest.bad_descriptor", f"bad descriptor for {split}"))
            continue
        path = root / str(descriptor.get("path", f"{split}.jsonl"))
        if not path.exists():
            errors.append(_issue("manifest.missing_file", f"missing file {path.name}"))
            continue
        observed_hash = sha256(path.read_bytes()).hexdigest()
        if descriptor.get("sha256") != observed_hash:
            errors.append(_issue("manifest.hash_mismatch", f"byte hash mismatch for {path.name}"))
        records = dataset.get(str(split), [])
        if descriptor.get("records") != len(records):
            errors.append(_issue("manifest.count_mismatch", f"record count mismatch for {split}"))
        if descriptor.get("semantic_sha256") != dataset_digest(records):
            errors.append(_issue("manifest.semantic_hash_mismatch", f"semantic hash mismatch for {split}"))


def validate_dataset(
    source: Mapping[str, Sequence[Mapping[str, Any]]] | str | Path,
    *,
    max_errors: int = 200,
) -> ValidationReport:
    """Validate records, exact labels, split invariants, pairs, and manifests."""

    dataset, root, manifest = _load_source(source)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    answer_counts: Counter[str] = Counter()
    world_counts: Counter[str] = Counter()
    surface_marker_counts: Counter[str] = Counter()
    formal_checked = 0
    for split, records in dataset.items():
        if split not in SPLITS:
            errors.append(_issue("dataset.unknown_split", f"unknown split key {split!r}"))
        for record in records:
            record_id = str(record.get("id", "<missing>"))
            if record_id in seen_ids:
                errors.append(_issue("dataset.duplicate_id", "record identifier is duplicated", record_id))
            seen_ids.add(record_id)
            if record.get("split") != split:
                errors.append(_issue("dataset.split_mismatch", f"container split {split} disagrees with record", record_id))
            metadata = record.get("metadata", {})
            observed_role = metadata.get("split_role") if isinstance(metadata, Mapping) else None
            expected_role = _expected_split_role(split)
            if observed_role != expected_role:
                errors.append(
                    _issue(
                        "dataset.wrong_split_role",
                        f"{split} must have split_role={expected_role!r}, found {observed_role!r}",
                        record_id,
                    )
                )
            record_errors = validate_record(record)
            errors.extend(record_errors)
            marker = _validate_surface_marker(record, errors)
            if marker is not None:
                surface_marker_counts["|".join(marker)] += 1
            if "initial_state" in record:
                formal_checked += 1
            answer_counts[str(record.get("answer"))] += 1
            world_counts[str(record.get("world"))] += 1
            if len(errors) >= max_errors:
                break
        if len(errors) >= max_errors:
            break

    train_transforms = {
        str(record.get("canonical_transform_id"))
        for split in TRAINING_SPLITS
        for record in dataset.get(split, [])
        if record.get("canonical_transform_id")
    }
    heldout_transforms = {
        str(record.get("canonical_transform_id"))
        for split in ("heldout_pair", "heldout_triple")
        for record in dataset.get(split, [])
        if record.get("canonical_transform_id")
    }
    leakage = sorted(train_transforms & heldout_transforms)
    if leakage:
        errors.append(
            _issue(
                "dataset.heldout_transform_leakage",
                f"{len(leakage)} held-out transformations occur in training",
            )
        )

    for split in TRAINING_SPLITS:
        for record in dataset.get(split, []):
            if "program" not in record:
                continue
            world = str(record.get("world"))
            try:
                program = normalize_program(record["program"])
                law_patterns = tuple(
                    law.left for law in get_world(world).laws if len(law.left) >= 2
                )
                sealed_patterns = HELDOUT_PAIRS[world] + HELDOUT_TRIPLES[world] + law_patterns
            except Exception:
                continue
            if any(_contains_subsequence(program, pattern) for pattern in sealed_patterns):
                errors.append(
                    _issue(
                        "dataset.sealed_training_pattern",
                        f"{split} contains a sealed held-out or law composition",
                        str(record.get("id")),
                    )
                )

    train_semantic_queries = {
        (str(record.get("semantic_id")), str(record.get("question_id")))
        for split in TRAINING_SPLITS
        for record in dataset.get(split, [])
    }
    train_rendered_inputs = {
        (str(record.get("story")), str(record.get("question")))
        for split in TRAINING_SPLITS
        for record in dataset.get(split, [])
    }
    semantic_query_overlap = {
        split: sum(
            (str(record.get("semantic_id")), str(record.get("question_id")))
            in train_semantic_queries
            for record in dataset.get(split, [])
        )
        for split in SPLITS
        if split not in TRAINING_SPLITS
    }
    rendered_input_overlap = {
        split: sum(
            (str(record.get("story")), str(record.get("question")))
            in train_rendered_inputs
            for record in dataset.get(split, [])
        )
        for split in SPLITS
        if split not in TRAINING_SPLITS
    }
    semantic_query_overlap_rates = {
        split: semantic_query_overlap[split] / len(dataset.get(split, []))
        if dataset.get(split, [])
        else 0.0
        for split in semantic_query_overlap
    }
    rendered_input_overlap_rates = {
        split: rendered_input_overlap[split] / len(dataset.get(split, []))
        if dataset.get(split, [])
        else 0.0
        for split in rendered_input_overlap
    }
    for split in VALIDATION_SPLITS + EVALUATION_SPLITS:
        if rendered_input_overlap.get(split, 0):
            errors.append(
                _issue(
                    "dataset.rendered_train_overlap",
                    f"{split} has {rendered_input_overlap[split]} exact rendered inputs in training shards",
                )
            )

    clean_input_owner: dict[tuple[str, str], str] = {}
    cross_clean_overlap: Counter[str] = Counter()
    for split in VALIDATION_SPLITS + EVALUATION_SPLITS:
        for record in dataset.get(split, []):
            key = (str(record.get("story")), str(record.get("question")))
            previous = clean_input_owner.get(key)
            if previous is not None:
                cross_clean_overlap[f"{previous}|{split}"] += 1
            else:
                clean_input_owner[key] = split
    if cross_clean_overlap:
        errors.append(
            _issue(
                "dataset.cross_clean_rendered_overlap",
                f"exact rendered inputs repeat across clean shards: {dict(cross_clean_overlap)}",
            )
        )

    train_lengths = [
        int(record.get("metadata", {}).get("program_length", 0))
        for record in dataset.get("train", [])
    ]
    length_lengths = [
        int(record.get("metadata", {}).get("program_length", 0))
        for record in dataset.get("length", [])
    ]
    if train_lengths and length_lengths and min(length_lengths) <= max(train_lengths):
        errors.append(_issue("dataset.length_overlap", "length split is not strictly longer than training"))

    for record in dataset.get("lexical", []):
        if record.get("metadata", {}).get("lexicon") != "lexical":
            errors.append(_issue("dataset.lexical_marker", "lexical record lacks lexical marker", str(record.get("id"))))
    _validate_counterfactual_groups(dataset.get("counterfactual", []), errors)
    training_nonces, evaluation_nonces = _validate_renaming_protocol(dataset, errors)
    _validate_balancing(dataset, errors)
    if root is not None and manifest is not None:
        _validate_manifest(root, manifest, dataset, errors)
    if formal_checked == 0 and sum(len(records) for records in dataset.values()):
        warnings.append(
            _issue(
                "dataset.no_formal_fields",
                "formal fields were omitted, so exact replay validation was unavailable",
            )
        )
    statistics = {
        "records": sum(len(records) for records in dataset.values()),
        "split_counts": {split: len(dataset.get(split, [])) for split in SPLITS},
        "world_counts": dict(sorted(world_counts.items())),
        "answer_counts": dict(sorted(answer_counts.items())),
        "surface_marker_counts": dict(sorted(surface_marker_counts.items())),
        "formal_records_checked": formal_checked,
        "heldout_transform_overlap": len(leakage),
        "semantic_query_overlap_with_train": semantic_query_overlap,
        "rendered_input_overlap_with_train": rendered_input_overlap,
        "semantic_query_overlap_rate_with_train": semantic_query_overlap_rates,
        "rendered_input_overlap_rate_with_train": rendered_input_overlap_rates,
        "semantic_query_overlap_with_train_like": semantic_query_overlap,
        "rendered_input_overlap_with_train_like": rendered_input_overlap,
        "semantic_query_overlap_rate_with_train_like": semantic_query_overlap_rates,
        "rendered_input_overlap_rate_with_train_like": rendered_input_overlap_rates,
        "cross_clean_rendered_overlap": dict(sorted(cross_clean_overlap.items())),
        "training_nonce_vocabulary": sorted(training_nonces),
        "evaluation_nonce_vocabulary": sorted(evaluation_nonces),
        "nonce_vocabulary_overlap": sorted(training_nonces & evaluation_nonces),
    }
    return ValidationReport(
        errors=tuple(errors[:max_errors]),
        warnings=tuple(warnings),
        statistics=statistics,
    )


__all__ = ["ValidationReport", "validate_dataset", "validate_record"]
