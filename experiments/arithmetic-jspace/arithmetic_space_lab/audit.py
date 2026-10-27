from __future__ import annotations

import json
import re
import time
from collections import Counter, defaultdict
from itertools import zip_longest
from pathlib import Path
from typing import Any

from .core import (
    Problem,
    expected_answer_type,
    expected_problem_difficulty,
    expected_problem_family_key,
    seeded_rng,
    stable_hash,
    verify_trace,
    weighted_choice,
)
from .generate import canonical_json, sampling_configuration, sha256_file
from .render import (
    choose_response_mode,
    expected_task_prompt,
    expected_task_target,
    render_response,
    task_from_dict,
)


class AuditFailure(RuntimeError):
    pass


def _read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                yield line_number, json.loads(line)
            except json.JSONDecodeError as error:
                raise AuditFailure(f"invalid JSON at {path}:{line_number}: {error}") from error


def _records_for_split(directory: Path, split: str):
    for path in sorted(directory.glob(f"{split}-*.jsonl")):
        for _, record in _read_jsonl(path):
            yield record


def _shard_split(path: Path) -> str | None:
    match = re.fullmatch(r"(.+)-(\d{5})\.jsonl", path.name)
    return match.group(1) if match else None


def _problem_from_record(record: dict[str, Any]) -> Problem:
    return Problem(
        operation_family=record["operation_family"],
        ast=record["ast"],
        answer=record["answer"],
        answer_type=record["answer_type"],
        expression=record["expression"],
        family_key=record["family_key"],
        difficulty=record["difficulty"],
        trace=record["trace"],
        remainder=record.get("remainder"),
    )


def audit_dataset(root: str | Path, write_report: bool = True) -> dict[str, Any]:
    root_path = Path(root).resolve()
    manifest_path = root_path / "manifest.json"
    if not manifest_path.is_file():
        raise AuditFailure(f"manifest not found: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    config_path = root_path / "resolved_config.json"
    if not config_path.is_file():
        raise AuditFailure(f"resolved configuration not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        resolved_config = json.load(handle)
    regime_configs = {regime["name"]: regime for regime in resolved_config.get("regimes", [])}
    holdout_configs = {
        holdout["name"]: holdout for holdout in resolved_config.get("holdouts", [])
    }
    started = time.perf_counter()
    errors: list[str] = []
    warnings: list[str] = []
    expected_sampling_fingerprint = stable_hash(
        canonical_json(sampling_configuration(resolved_config))
    )
    if stable_hash(canonical_json(resolved_config)) != manifest.get("configuration_sha256"):
        errors.append("resolved configuration hash does not match manifest")
    if expected_sampling_fingerprint != manifest.get("sampling_configuration_sha256"):
        errors.append("sampling configuration hash does not match manifest")
    if manifest.get("seed") != resolved_config.get("seed"):
        errors.append("manifest seed does not match resolved configuration")
    requested = {
        **{name: int(count) for name, count in resolved_config.get("counts", {}).items()},
        **{
            holdout["name"]: int(holdout["count"])
            for holdout in resolved_config.get("holdouts", [])
        },
    }
    if manifest.get("requested_counts") != requested:
        errors.append("requested counts do not match resolved configuration")

    for entry in manifest.get("files", []):
        path = root_path / entry["path"]
        if not path.is_file():
            errors.append(f"missing file: {entry['path']}")
            continue
        if path.stat().st_size != entry["bytes"]:
            errors.append(f"size mismatch: {entry['path']}")
        if sha256_file(path) != entry["sha256"]:
            errors.append(f"SHA-256 mismatch: {entry['path']}")

    canonical_files = sorted((root_path / "canonical").glob("*.jsonl"))
    if not canonical_files:
        errors.append("no canonical JSONL files found")
    sample_ids: set[str] = set()
    family_splits: dict[str, str] = {}
    relation_splits: dict[str, str] = {}
    prompt_splits: dict[str, str] = {}
    pair_targets: dict[str, str] = {}
    pair_metadata: dict[str, dict[str, Any]] = {}
    counts = Counter()
    operations = Counter()
    tasks = Counter()
    styles = Counter()
    difficulties = Counter()

    for path in canonical_files:
        physical_split = _shard_split(path)
        for line_number, record in _read_jsonl(path):
            where = f"{path.name}:{line_number}"
            try:
                sample_id = record["sample_id"]
                family_id = record["family_id"]
                split = record["split"]
                if split not in requested:
                    errors.append(f"unknown canonical split at {where}: {split}")
                if physical_split != split:
                    errors.append(
                        f"canonical split does not match shard filename at {where}: "
                        f"record={split}, file={physical_split}"
                    )
                if sample_id in sample_ids:
                    errors.append(f"duplicate sample_id at {where}: {sample_id}")
                sample_ids.add(sample_id)
                expected_family = stable_hash(record["family_key"])
                if family_id != expected_family:
                    errors.append(f"family hash mismatch at {where}")
                problem = _problem_from_record(record)
                if record["answer_type"] != expected_answer_type(problem):
                    errors.append(f"answer type does not follow arithmetic semantics at {where}")
                difficulty = record["difficulty"]
                level = difficulty.get("level") if isinstance(difficulty, dict) else None
                effective_config = holdout_configs.get(split, resolved_config)
                enabled_levels = {
                    int(name)
                    for name, weight in effective_config.get(
                        "difficulty_weights", resolved_config["difficulty_weights"]
                    ).items()
                    if float(weight) > 0
                }
                if level not in enabled_levels:
                    errors.append(f"difficulty level is not enabled for split at {where}")
                generator_index = record.get("generator_index")
                if (
                    not isinstance(generator_index, int)
                    or isinstance(generator_index, bool)
                    or generator_index < 0
                ):
                    errors.append(f"invalid generator index at {where}")
                else:
                    replay_rng = seeded_rng(
                        resolved_config["seed"],
                        expected_sampling_fingerprint,
                        split if split in holdout_configs else "iid",
                        generator_index,
                    )
                    expected_operation = weighted_choice(
                        replay_rng,
                        effective_config.get("operations", resolved_config["operations"]),
                    )
                    expected_level = int(
                        weighted_choice(
                            replay_rng,
                            effective_config.get(
                                "difficulty_weights", resolved_config["difficulty_weights"]
                            ),
                        )
                    )
                    if record["operation_family"] != expected_operation:
                        errors.append(f"operation does not match deterministic sample index at {where}")
                    if level != expected_level:
                        errors.append(f"difficulty level does not match deterministic sample index at {where}")
                if difficulty != expected_problem_difficulty(problem, level):
                    errors.append(f"difficulty metadata does not follow arithmetic semantics at {where}")
                semantic_family_key = expected_problem_family_key(problem)
                if record["family_key"] != semantic_family_key:
                    errors.append(f"family key does not follow arithmetic semantics at {where}")
                expected_relations = problem.relation_ids
                if record.get("relation_ids") != expected_relations:
                    errors.append(f"atomic relation list mismatch at {where}")
                task = record["task"]
                expected_sample = stable_hash(
                    canonical_json(
                        {
                            "family_id": family_id,
                            "task_type": record["task_type"],
                            "prompt": task["prompt"],
                            "target": task["target"],
                            "proposed": task.get("proposed_answer"),
                        }
                    )
                )
                if sample_id != expected_sample:
                    errors.append(f"sample hash mismatch at {where}")
                task_object = task_from_dict(task, record["task_type"])
                if not task_object.prompt.strip():
                    errors.append(f"blank task prompt at {where}")
                if task_object.prompt != expected_task_prompt(problem, task_object):
                    errors.append(f"task prompt does not match its template and arithmetic fields at {where}")
                if task_object.target != expected_task_target(problem, task_object):
                    errors.append(f"task target does not follow arithmetic semantics at {where}")
                prior = family_splits.setdefault(family_id, split)
                if prior != split:
                    errors.append(f"family leakage for {family_id}: {prior} and {split}")
                for relation_id in expected_relations:
                    prior_relation_split = relation_splits.setdefault(relation_id, split)
                    if prior_relation_split != split:
                        errors.append(
                            f"atomic relation leakage for {relation_id}: "
                            f"{prior_relation_split} and {split}"
                        )
                prompt_key = stable_hash(" ".join(record["task"]["prompt"].split()).casefold())
                prior_prompt_split = prompt_splits.setdefault(prompt_key, split)
                if prior_prompt_split != split:
                    errors.append(f"normalized prompt leakage at {where}")
                verify_trace(problem)
                pair_targets[sample_id] = record["task"]["target"]
                pair_metadata[sample_id] = {
                    "schema_version": record["schema_version"],
                    "sample_id": sample_id,
                    "family_id": family_id,
                    "split": split,
                    "operation_family": record["operation_family"],
                    "task_type": record["task_type"],
                    "difficulty": difficulty,
                    "template_id": record["task"]["template_id"],
                    "prompt_style": record["task"]["prompt_style"],
                }
                counts[split] += 1
                operations[record["operation_family"]] += 1
                tasks[record["task_type"]] += 1
                styles[record["task"]["prompt_style"]] += 1
                difficulties[str(level)] += 1
            except Exception as error:
                errors.append(f"invalid canonical record at {where}: {error}")

    for split, expected in requested.items():
        if counts[split] != expected:
            errors.append(f"count mismatch for {split}: expected {expected}, found {counts[split]}")
    positive_operations = {
        name for name, weight in resolved_config.get("operations", {}).items() if float(weight) > 0
    }
    if sum(counts.values()) >= 10 * max(1, len(positive_operations)):
        missing_operations = sorted(positive_operations - set(operations))
        if missing_operations:
            errors.append(f"configured operations produced no records: {missing_operations}")
    computed_statistics = {
        "operation": dict(sorted(operations.items())),
        "difficulty": dict(sorted(difficulties.items())),
        "task_type": dict(sorted(tasks.items())),
        "prompt_style": dict(sorted(styles.items())),
        "split": dict(sorted(counts.items())),
    }
    if manifest.get("statistics") != computed_statistics:
        errors.append("dataset statistics do not match manifest")
    if manifest.get("actual_counts") != dict(sorted(counts.items())):
        errors.append("actual counts do not match observed canonical records")
    if manifest.get("unique_samples") != len(sample_ids):
        errors.append("unique sample count does not match manifest")
    if manifest.get("unique_families") != len(family_splits):
        errors.append("unique family count does not match manifest")
    if manifest.get("unique_atomic_relations") != len(relation_splits):
        errors.append("unique atomic-relation count does not match manifest")

    regime_counts: dict[str, dict[str, int]] = {}
    regime_dirs = sorted(path for path in root_path.glob("sft_*") if path.is_dir())
    if not regime_dirs:
        errors.append("no SFT regime directories found")
    for regime_dir in regime_dirs:
        regime = regime_dir.name.removeprefix("sft_")
        regime_config = regime_configs.get(regime)
        if regime_config is None:
            errors.append(f"SFT directory has no resolved regime configuration: {regime}")
        seen_pairs: set[str] = set()
        seen_record_ids: set[str] = set()
        local_counts = Counter()
        for path in sorted(regime_dir.glob("*.jsonl")):
            physical_split = _shard_split(path)
            for line_number, record in _read_jsonl(path):
                where = f"{path.relative_to(root_path)}:{line_number}"
                try:
                    pair_id = record["pair_id"]
                    record_id = record["id"]
                    metadata_split = record.get("metadata", {}).get("split")
                    if metadata_split not in requested:
                        errors.append(f"unknown SFT split at {where}: {metadata_split}")
                    if physical_split != metadata_split:
                        errors.append(
                            f"SFT split does not match shard filename at {where}: "
                            f"record={metadata_split}, file={physical_split}"
                        )
                    if pair_id in seen_pairs:
                        errors.append(f"duplicate pair_id in {regime} at {where}")
                    seen_pairs.add(pair_id)
                    if record_id in seen_record_ids:
                        errors.append(f"duplicate SFT id in {regime} at {where}")
                    seen_record_ids.add(record_id)
                    if pair_id not in pair_targets:
                        errors.append(f"orphan SFT pair at {where}: {pair_id}")
                    if record["answer"] != pair_targets.get(pair_id):
                        errors.append(f"SFT answer mismatch at {where}")
                    expected_meta = pair_metadata.get(pair_id)
                    actual_meta = {
                        key: record["metadata"].get(key)
                        for key in expected_meta or {}
                    }
                    if expected_meta is not None and actual_meta != expected_meta:
                        errors.append(f"SFT metadata mismatch at {where}")
                    if record["metadata"].get("regime") != regime:
                        errors.append(f"SFT regime metadata mismatch at {where}")
                    response_mode = record["metadata"]["response_mode"]
                    expected_id = stable_hash(f"{pair_id}|{regime}|{response_mode}")
                    if record_id != expected_id:
                        errors.append(f"SFT id hash mismatch at {where}")
                    messages = record["messages"]
                    expected_roles = (
                        ["system", "user", "assistant"]
                        if resolved_config.get("include_system_message", True)
                        else ["user", "assistant"]
                    )
                    if [message.get("role") for message in messages] != expected_roles:
                        errors.append(f"invalid message roles at {where}")
                    if (
                        resolved_config.get("include_system_message", True)
                        and messages
                        and messages[0].get("content") != resolved_config.get("system_prompt")
                    ):
                        errors.append(f"system-message mismatch at {where}")
                    if messages[-2]["content"] != record["prompt"]:
                        errors.append(f"prompt/message mismatch at {where}")
                    if messages[-1]["content"] != record["completion"]:
                        errors.append(f"completion/message mismatch at {where}")
                    if response_mode == "answer_only" and record["completion"] != record["answer"]:
                        errors.append(f"answer-only completion mismatch at {where}")
                    if response_mode == "worked_trace" and not record["completion"].endswith(
                        f"Answer: {record['answer']}"
                    ):
                        errors.append(f"worked completion has invalid final answer at {where}")
                    local_counts[record["metadata"]["split"]] += 1
                except Exception as error:
                    errors.append(f"invalid SFT record at {where}: {error}")
        missing_pairs = sample_ids - seen_pairs
        extra_pairs = seen_pairs - sample_ids
        if missing_pairs:
            errors.append(f"{regime} is missing {len(missing_pairs)} canonical pairs")
        if extra_pairs:
            errors.append(f"{regime} has {len(extra_pairs)} extra pairs")
        regime_counts[regime] = dict(sorted(local_counts.items()))

        if regime_config is not None:
            missing_marker = object()
            for split, expected_count in requested.items():
                if expected_count <= 0:
                    continue
                canonical_iterator = _records_for_split(root_path / "canonical", split)
                sft_iterator = _records_for_split(regime_dir, split)
                for pair_index, (canonical_record, sft_record) in enumerate(
                    zip_longest(canonical_iterator, sft_iterator, fillvalue=missing_marker),
                    1,
                ):
                    where = f"{regime}/{split} pair {pair_index}"
                    if canonical_record is missing_marker or sft_record is missing_marker:
                        errors.append(f"canonical/SFT length mismatch at {where}")
                        break
                    if canonical_record["sample_id"] != sft_record.get("pair_id"):
                        errors.append(f"canonical/SFT order mismatch at {where}")
                        continue
                    problem = _problem_from_record(canonical_record)
                    task_object = task_from_dict(canonical_record["task"], canonical_record["task_type"])
                    expected_mode = choose_response_mode(
                        regime_config,
                        seeded_rng(manifest["seed"], canonical_record["sample_id"], regime),
                    )
                    actual_mode = sft_record.get("metadata", {}).get("response_mode")
                    if actual_mode != expected_mode:
                        errors.append(f"response-mode mismatch at {where}")
                        continue
                    expected_completion = render_response(problem, task_object, expected_mode)
                    if sft_record.get("completion") != expected_completion:
                        errors.append(f"completion is stale or incorrect at {where}")

    if len(family_splits) < max(1, len(sample_ids) // 100):
        warnings.append("very high number of variants per semantic family")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "root": str(root_path),
        "canonical_records": len(sample_ids),
        "unique_families": len(family_splits),
        "unique_atomic_relations": len(relation_splits),
        "counts": dict(sorted(counts.items())),
        "regime_counts": regime_counts,
        "operations": dict(sorted(operations.items())),
        "task_types": dict(sorted(tasks.items())),
        "prompt_styles": dict(sorted(styles.items())),
        "family_split_leakage": False if not any("family leakage" in error for error in errors) else True,
        "atomic_relation_split_leakage": False
        if not any("atomic relation leakage" in error for error in errors)
        else True,
        "errors": errors,
        "warnings": warnings,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }
    if write_report:
        report_path = root_path / "audit_report.json"
        with report_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
    if errors:
        preview = "; ".join(errors[:5])
        raise AuditFailure(f"dataset audit failed with {len(errors)} error(s): {preview}")
    return report
