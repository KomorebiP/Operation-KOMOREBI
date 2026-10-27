from __future__ import annotations

import json
import re
from collections import Counter
from hashlib import sha256
from pathlib import Path

from osl_lab.generator import (
    EVALUATION_NONCE_POOL,
    EVALUATION_SPLITS,
    HELDOUT_PAIRS,
    HELDOUT_TRIPLES,
    LEXICAL_SURFACE_MARKER_POOLS,
    SPLITS,
    TRAINING_SPLITS,
    TRAIN_NONCE_POOL,
    TRAIN_SURFACE_MARKER_POOLS,
    VALIDATION_SPLITS,
    DatasetConfig,
    dataset_digest,
    generate_dataset,
    load_dataset,
    write_dataset,
    _make_record,
)
from osl_lab.validation import validate_dataset


TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\w\s]")


def smoke_config(**overrides) -> DatasetConfig:
    values = {
        "seed": 90210,
        "split_sizes": {split: 12 for split in SPLITS},
        "train_min_length": 1,
        "train_max_length": 3,
        "length_test_min": 4,
        "length_test_max": 5,
    }
    values.update(overrides)
    return DatasetConfig(**values)


def test_preset_bundle_cardinalities_are_exact() -> None:
    root = Path(__file__).resolve().parents[1]
    for name in ("smoke", "standard", "confirmatory", "full"):
        dataset = json.loads((root / "configs" / f"{name}.json").read_text())["dataset"]
        sizes = dataset["split_sizes"]
        assert sizes["renaming"] % 3 == 0
        assert sizes["renaming_train"] == sizes["renaming_scrambled_train"]


def test_nontriplet_renaming_size_is_rejected() -> None:
    sizes = {split: 0 for split in SPLITS}
    sizes["renaming"] = 13
    try:
        smoke_config(split_sizes=sizes)
    except ValueError as exc:
        assert "divisible by three" in str(exc)
    else:
        raise AssertionError("nontriplet renaming size was accepted")


def test_generation_is_deterministic_and_has_every_split() -> None:
    config = smoke_config()
    first = generate_dataset(config)
    second = generate_dataset(config)
    assert tuple(first) == SPLITS
    assert all(len(first[split]) == 12 for split in SPLITS if split != "counterfactual")
    assert len(first["counterfactual"]) >= 12
    assert {split: dataset_digest(records) for split, records in first.items()} == {
        split: dataset_digest(records) for split, records in second.items()
    }


def test_semantic_digest_excludes_surface_realization() -> None:
    records = generate_dataset(smoke_config())["iid_test"]
    changed = json.loads(json.dumps(records))
    changed[0]["id"] = "different-rendered-id"
    changed[0]["renderer"] = "different-renderer"
    changed[0]["story"] = "Different surface story."
    changed[0]["question"] = "Different surface question?"
    changed[0]["answer_text"] = "different surface answer"
    changed[0]["metadata"]["lexicon"] = "different-surface-lexicon"
    assert dataset_digest(records) == dataset_digest(changed)
    changed[0]["answer"] = "different-semantic-answer"
    assert dataset_digest(records) != dataset_digest(changed)


def test_generated_dataset_passes_exact_validation() -> None:
    dataset = generate_dataset(smoke_config())
    report = validate_dataset(dataset)
    assert report.ok, json.dumps(report.to_dict(), indent=2)
    assert report.statistics["formal_records_checked"] == sum(
        len(records) for records in dataset.values()
    )
    assert report.statistics["heldout_transform_overlap"] == 0
    assert not any(report.statistics["rendered_input_overlap_with_train"].values())
    assert not report.statistics["cross_clean_rendered_overlap"]


def test_structural_splits_and_canonical_labels() -> None:
    dataset = generate_dataset(smoke_config())
    train_max = max(record["metadata"]["program_length"] for record in dataset["train"])
    assert min(record["metadata"]["program_length"] for record in dataset["length"]) > train_max
    for record in dataset["heldout_pair"]:
        program = tuple(action["op"] for action in record["program"])
        assert program in HELDOUT_PAIRS[record["world"]]
    for record in dataset["heldout_triple"]:
        program = tuple(action["op"] for action in record["program"])
        assert program in HELDOUT_TRIPLES[record["world"]]
    for record in dataset["lexical"]:
        assert record["metadata"]["lexicon"] == "lexical"
        if record["world"] == "algebra" and record["question_id"] in {
            "left_status",
            "right_status",
        }:
            assert record["answer"] in {"lit", "dark"}
            assert record["answer_text"] in {"active", "inactive"}


def test_counterfactual_records_are_complete_pairs() -> None:
    dataset = generate_dataset(smoke_config(split_sizes={split: 3 for split in SPLITS}))
    records = dataset["counterfactual"]
    assert len(records) >= 3
    pairs = {}
    for record in records:
        pairs.setdefault(record["metadata"]["pair_id"], []).append(record)
    assert all(len(pair) == 2 * len({record["question_id"] for record in pair}) for pair in pairs.values())
    for pair in pairs.values():
        assert len(
            {
                json.dumps(record["metadata"]["surface_marker"], sort_keys=True)
                for record in pair
            }
        ) == 1
        query_groups = {}
        for record in pair:
            query_groups.setdefault(record["question_id"], []).append(record)
        assert set(query_groups) == set(pair[0]["metadata"]["bundle_query_ids"])
        for query_pair in query_groups.values():
            variants = {record["metadata"]["variant"]: record for record in query_pair}
            expected = variants["base"]["metadata"]["query_expected_to_change"]
            observed = variants["base"]["answer"] != variants["counterfactual"]["answer"]
            assert expected == observed


def test_nonce_meanings_are_permuted_by_episode() -> None:
    sizes = {split: 0 for split in SPLITS}
    sizes["renaming_train"] = 30
    sizes["renaming_scrambled_train"] = 30
    sizes["renaming"] = 30
    dataset = generate_dataset(smoke_config(split_sizes=sizes))
    training_records = dataset["renaming_train"]
    scrambled_training_records = dataset["renaming_scrambled_train"]
    records = [
        record
        for record in dataset["renaming"]
        if record["metadata"]["variant"] == "renamed"
    ]
    mappings = {
        tuple(sorted(record["metadata"]["operator_mapping"].items()))
        for record in training_records
    }
    assert len(mappings) > 1
    training_pairs = {
        record["metadata"]["pair_id"]: record for record in training_records
    }
    scrambled_pairs = {
        record["metadata"]["pair_id"]: record for record in scrambled_training_records
    }
    assert set(training_pairs) == set(scrambled_pairs)
    for pair_id, correct in training_pairs.items():
        scrambled = scrambled_pairs[pair_id]
        assert correct["metadata"]["target_commands"] == scrambled["metadata"]["target_commands"]
        assert correct["metadata"]["operator_mapping"] == scrambled["metadata"]["operator_mapping"]
        assert correct["metadata"]["render_seed"] == scrambled["metadata"]["render_seed"]
        assert len(set(correct["metadata"]["target_commands"])) >= 2
        assert correct["answer"] == scrambled["answer"]
        assert correct["story"] != scrambled["story"]
        assert Counter(TOKEN_PATTERN.findall(correct["story"].lower())) == Counter(
            TOKEN_PATTERN.findall(scrambled["story"].lower())
        )
        target_marker = "At the start of the target episode,"
        assert correct["story"].split(target_marker, 1)[1] == scrambled["story"].split(target_marker, 1)[1]
    for record in training_records:
        mapping = record["metadata"]["operator_mapping"]
        assert all(command in mapping for command in record["metadata"]["target_commands"])
        assert set(mapping) <= set(TRAIN_NONCE_POOL)
        assert record["metadata"]["split_role"] == "training"
        assert "Calibration:" in record["story"]
    for record in records:
        assert set(record["metadata"]["operator_mapping"]) <= set(EVALUATION_NONCE_POOL)
    assert set(TRAIN_NONCE_POOL).isdisjoint(EVALUATION_NONCE_POOL)
    def bucket(token: str) -> int:
        return int.from_bytes(
            sha256(token.encode("utf-8")).digest()[:8], "big"
        ) % 2048
    training_buckets = {bucket(token) for token in TRAIN_NONCE_POOL}
    evaluation_buckets = {bucket(token) for token in EVALUATION_NONCE_POOL}
    assert len(training_buckets) == len(TRAIN_NONCE_POOL)
    assert len(evaluation_buckets) == len(EVALUATION_NONCE_POOL)
    assert training_buckets.isdisjoint(evaluation_buckets)


def test_renaming_evaluation_is_paired_and_semantically_matched() -> None:
    sizes = {split: (15 if split == "renaming" else 0) for split in SPLITS}
    records = generate_dataset(smoke_config(split_sizes=sizes))["renaming"]
    assert len(records) == 15
    pairs = {}
    for record in records:
        pairs.setdefault(record["metadata"]["pair_id"], []).append(record)
    assert len(pairs) == 5
    for pair in pairs.values():
        variants = {record["metadata"]["variant"]: record for record in pair}
        assert set(variants) == {"canonical", "renamed", "scrambled"}
        canonical = variants["canonical"]
        renamed = variants["renamed"]
        scrambled = variants["scrambled"]
        for field in (
            "world",
            "semantic_id",
            "question_id",
            "question",
            "answer",
            "initial_state",
            "program",
            "canonical_transform_id",
            "final_state",
        ):
            assert canonical[field] == renamed[field] == scrambled[field]
        assert "Calibration:" not in canonical["story"]
        assert "Calibration:" in renamed["story"]
        assert "Calibration:" in scrambled["story"]
        assert (
            canonical["metadata"]["surface_marker"]
            == renamed["metadata"]["surface_marker"]
            == scrambled["metadata"]["surface_marker"]
        )
        assert renamed["metadata"]["target_commands"] == scrambled["metadata"]["target_commands"]
        assert Counter(TOKEN_PATTERN.findall(renamed["story"].lower())) == Counter(
            TOKEN_PATTERN.findall(scrambled["story"].lower())
        )


def test_surface_markers_are_label_independent_disjoint_and_scale() -> None:
    dark = _make_record(
        split="iid_test",
        world="algebra",
        initial_state={"left": False, "right": False},
        program=("clear_left",),
        query_id="left_status",
        renderer="direct",
        lexicon="train",
        render_seed=123456,
        include_formal_fields=True,
    )
    lit = _make_record(
        split="iid_test",
        world="algebra",
        initial_state={"left": False, "right": False},
        program=("set_left",),
        query_id="left_status",
        renderer="direct",
        lexicon="train",
        render_seed=123456,
        include_formal_fields=True,
    )
    assert dark["answer"] != lit["answer"]
    assert dark["metadata"]["surface_marker"] == lit["metadata"]["surface_marker"]

    train_markers = set(TRAIN_SURFACE_MARKER_POOLS[0] + TRAIN_SURFACE_MARKER_POOLS[1])
    lexical_markers = set(
        LEXICAL_SURFACE_MARKER_POOLS[0] + LEXICAL_SURFACE_MARKER_POOLS[1]
    )
    assert train_markers.isdisjoint(lexical_markers)
    all_special_tokens = train_markers | lexical_markers | set(TRAIN_NONCE_POOL) | set(EVALUATION_NONCE_POOL)
    buckets = {
        int.from_bytes(sha256(token.encode("utf-8")).digest()[:8], "big") % 2048
        for token in all_special_tokens
    }
    assert len(buckets) == len(all_special_tokens)

    sizes = {split: 0 for split in SPLITS}
    sizes["heldout_pair"] = 2000
    sizes["heldout_triple"] = 2000
    dataset = generate_dataset(smoke_config(split_sizes=sizes))
    assert len(dataset["heldout_pair"]) == 2000
    assert len(dataset["heldout_triple"]) == 2000
    report = validate_dataset(dataset)
    assert report.ok, json.dumps(report.to_dict(), indent=2)


def test_split_roles_balance_and_iid_independence() -> None:
    dataset = generate_dataset(smoke_config(split_sizes={split: 42 for split in SPLITS}))
    for split in TRAINING_SPLITS:
        assert {record["metadata"]["split_role"] for record in dataset[split]} == {"training"}
    for split in VALIDATION_SPLITS:
        assert {record["metadata"]["split_role"] for record in dataset[split]} == {"validation"}
    for split in EVALUATION_SPLITS:
        assert {record["metadata"]["split_role"] for record in dataset[split]} == {"evaluation"}
    for split in ("iid_validation", "iid_test", "heldout_pair", "heldout_triple"):
        world_counts = {
            world: sum(record["world"] == world for record in dataset[split])
            for world in ("algebra", "provenance", "resources")
        }
        assert max(world_counts.values()) - min(world_counts.values()) <= 1
    validation_inputs = {
        (record["story"], record["question"]) for record in dataset["iid_validation"]
    }
    test_inputs = {(record["story"], record["question"]) for record in dataset["iid_test"]}
    assert validation_inputs.isdisjoint(test_inputs)


def test_validation_rejects_role_pair_pool_and_overlap_violations() -> None:
    sizes = {split: 6 for split in SPLITS}

    wrong_role = generate_dataset(smoke_config(split_sizes=sizes))
    wrong_role["iid_test"][0]["metadata"]["split_role"] = "training"
    codes = {issue["code"] for issue in validate_dataset(wrong_role).errors}
    assert "dataset.wrong_split_role" in codes

    broken_pair = generate_dataset(smoke_config(split_sizes=sizes))
    broken_pair["renaming"][0]["metadata"]["pair_id"] = "orphan"
    codes = {issue["code"] for issue in validate_dataset(broken_pair).errors}
    assert "renaming.bad_pair_variants" in codes

    wrong_pool = generate_dataset(smoke_config(split_sizes=sizes))
    renamed = next(
        record
        for record in wrong_pool["renaming"]
        if record["metadata"]["variant"] == "renamed"
    )
    mapping = renamed["metadata"]["operator_mapping"]
    old_nonce = next(iter(mapping))
    operator = mapping.pop(old_nonce)
    mapping[TRAIN_NONCE_POOL[0]] = operator
    renamed["metadata"]["target_commands"] = [
        TRAIN_NONCE_POOL[0] if command == old_nonce else command
        for command in renamed["metadata"]["target_commands"]
    ]
    codes = {issue["code"] for issue in validate_dataset(wrong_pool).errors}
    assert "renaming.wrong_nonce_pool" in codes

    rendered_overlap = generate_dataset(smoke_config(split_sizes=sizes))
    rendered_overlap["iid_test"][0]["story"] = rendered_overlap["train"][0]["story"]
    rendered_overlap["iid_test"][0]["question"] = rendered_overlap["train"][0]["question"]
    codes = {issue["code"] for issue in validate_dataset(rendered_overlap).errors}
    assert "dataset.rendered_train_overlap" in codes

    wrong_marker = generate_dataset(smoke_config(split_sizes=sizes))
    wrong_marker["iid_test"][0]["metadata"]["surface_marker"]["first"] = (
        LEXICAL_SURFACE_MARKER_POOLS[0][0]
    )
    codes = {issue["code"] for issue in validate_dataset(wrong_marker).errors}
    assert "surface_marker.wrong_pool" in codes

    changed_scramble = generate_dataset(smoke_config(split_sizes=sizes))
    scrambled = next(
        record
        for record in changed_scramble["renaming"]
        if record["metadata"]["variant"] == "scrambled"
    )
    scrambled["story"] += " Extra nuisance token."
    codes = {issue["code"] for issue in validate_dataset(changed_scramble).errors}
    assert "renaming.scrambled_token_multiset_mismatch" in codes


def test_write_load_and_manifest_hashes(tmp_path) -> None:
    config = smoke_config(split_sizes={split: 6 for split in SPLITS})
    manifest = write_dataset(tmp_path, config)
    loaded = load_dataset(tmp_path)
    assert manifest["format"] == "micro-osl-jsonl-v1.1"
    assert manifest["schema_version"] == "0.1.1"
    assert all((tmp_path / f"{split}.jsonl").exists() for split in SPLITS)
    assert {split: len(records) for split, records in loaded.items()} == {
        split: manifest["files"][split]["records"] for split in SPLITS
    }
    assert all(
        descriptor["sha256"] != descriptor["semantic_sha256"]
        for descriptor in manifest["files"].values()
        if descriptor["records"]
    )
    assert all(
        len(loaded[split]) == 6
        for split in SPLITS
        if split not in {"counterfactual", "renaming"}
    )
    assert len(loaded["counterfactual"]) >= 6
    assert len(loaded["renaming"]) == 6
    report = validate_dataset(tmp_path)
    assert report.ok, json.dumps(report.to_dict(), indent=2)
