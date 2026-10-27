from __future__ import annotations

import json
import shutil
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from . import __version__
from .config import validate_config
from .core import (
    Problem,
    generate_problem,
    seeded_rng,
    split_for_family,
    stable_hash,
    verify_trace,
    weighted_choice,
)
from .render import choose_response_mode, make_task, render_response


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sampling_configuration(config: dict[str, Any]) -> dict[str, Any]:
    presentation_only = {
        "dataset_name",
        "include_system_message",
        "output",
        "regimes",
        "system_prompt",
    }
    return {key: value for key, value in config.items() if key not in presentation_only}


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class ShardWriter:
    def __init__(self, root: Path, split: str, shard_size: int) -> None:
        self.root = root
        self.split = split
        self.shard_size = shard_size
        self.count = 0
        self.shard_index = -1
        self.handle = None
        self.paths: list[Path] = []

    def _open_next(self) -> None:
        if self.handle is not None:
            self.handle.close()
        self.root.mkdir(parents=True, exist_ok=True)
        self.shard_index += 1
        path = self.root / f"{self.split}-{self.shard_index:05d}.jsonl"
        self.paths.append(path)
        self.handle = path.open("w", encoding="utf-8", newline="\n")

    def write(self, record: dict[str, Any]) -> None:
        if self.handle is None or self.count % self.shard_size == 0:
            self._open_next()
        assert self.handle is not None
        self.handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        self.count += 1

    def close(self) -> None:
        if self.handle is not None:
            self.handle.close()
            self.handle = None


def _problem_record(
    problem: Problem,
    task: Any,
    sample_id: str,
    split: str,
    generator_index: int,
    seed: int,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "sample_id": sample_id,
        "family_id": problem.family_id,
        "family_key": problem.family_key,
        "relation_ids": problem.relation_ids,
        "split": split,
        "generator_index": generator_index,
        "operation_family": problem.operation_family,
        "task_type": task.task_type,
        "ast": problem.ast,
        "expression": problem.expression,
        "answer": problem.answer,
        "answer_type": problem.answer_type,
        "remainder": problem.remainder,
        "trace": problem.trace,
        "difficulty": problem.difficulty,
        "task": {
            "prompt": task.prompt,
            "prompt_style": task.prompt_style,
            "template_id": task.template_id,
            "target": task.target,
            "proposed_answer": task.proposed_answer,
            "hidden_operand": task.hidden_operand,
        },
        "generator": {"name": "arithmetic-space-lab", "version": __version__, "seed": seed},
    }


def _sft_record(
    canonical: dict[str, Any],
    regime_name: str,
    response_mode: str,
    completion: str,
    include_system_message: bool,
    system_prompt: str,
) -> dict[str, Any]:
    task = canonical["task"]
    record_id = stable_hash(f"{canonical['sample_id']}|{regime_name}|{response_mode}")
    messages = []
    if include_system_message:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(
        [
            {"role": "user", "content": task["prompt"]},
            {"role": "assistant", "content": completion},
        ]
    )
    return {
        "id": record_id,
        "pair_id": canonical["sample_id"],
        "messages": messages,
        "prompt": task["prompt"],
        "completion": completion,
        "answer": task["target"],
        "metadata": {
            "schema_version": canonical["schema_version"],
            "sample_id": canonical["sample_id"],
            "family_id": canonical["family_id"],
            "split": canonical["split"],
            "operation_family": canonical["operation_family"],
            "task_type": canonical["task_type"],
            "difficulty": canonical["difficulty"],
            "template_id": task["template_id"],
            "prompt_style": task["prompt_style"],
            "response_mode": response_mode,
            "regime": regime_name,
        },
    }


OUTPUT_SENTINEL = ".arithmetic_space_lab_output"
OUTPUT_SENTINEL_CONTENT = "arithmetic-space-lab-owned-output-v1\n"


def _safe_prepare_output(output: Path, overwrite: bool) -> None:
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        if not overwrite:
            raise FileExistsError(f"output directory is not empty: {output}")
        package_root = Path(__file__).resolve().parent.parent
        protected = {Path.home().resolve(), Path.cwd().resolve(), package_root}
        if output == Path(output.anchor) or any(path == output or path.is_relative_to(output) for path in protected):
            raise ValueError(f"refusing to clear protected or ancestral output path: {output}")
        sentinel = output / OUTPUT_SENTINEL
        manifest = output / "manifest.json"
        if not sentinel.is_file() or sentinel.read_text(encoding="utf-8") != OUTPUT_SENTINEL_CONTENT:
            raise ValueError(f"refusing to overwrite a directory not owned by arithmetic-space-lab: {output}")
        if manifest.is_file():
            try:
                with manifest.open("r", encoding="utf-8") as handle:
                    prior_manifest = json.load(handle)
                if prior_manifest.get("generator", {}).get("name") != "arithmetic-space-lab":
                    raise ValueError("unexpected generator identity")
            except (OSError, ValueError, json.JSONDecodeError) as error:
                raise ValueError(f"refusing to overwrite unverified output: {output}") from error
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    sentinel = output / OUTPUT_SENTINEL
    sentinel.write_text(OUTPUT_SENTINEL_CONTENT, encoding="utf-8", newline="\n")


def generate(config: dict[str, Any], output: str | Path, overwrite: bool = False) -> dict[str, Any]:
    validate_config(config)
    output_path = Path(output)
    _safe_prepare_output(output_path, overwrite)
    started = time.perf_counter()
    seed = int(config["seed"])
    fingerprint = stable_hash(canonical_json(config))
    sampling_fingerprint = stable_hash(canonical_json(sampling_configuration(config)))
    shard_size = int(config["output"]["shard_size"])

    base_counts = {name: int(count) for name, count in config["counts"].items()}
    all_targets = dict(base_counts)
    holdout_by_name: dict[str, dict[str, Any]] = {}
    for holdout in config.get("holdouts", []):
        name = holdout["name"]
        if name in all_targets:
            raise ValueError(f"holdout duplicates split name: {name}")
        all_targets[name] = int(holdout["count"])
        holdout_by_name[name] = holdout

    canonical_writers = {
        split: ShardWriter(output_path / "canonical", split, shard_size)
        for split, count in all_targets.items()
        if count > 0
    }
    regime_writers: dict[tuple[str, str], ShardWriter] = {}
    for regime in config["regimes"]:
        for split, count in all_targets.items():
            if count > 0:
                regime_writers[(regime["name"], split)] = ShardWriter(
                    output_path / f"sft_{regime['name']}", split, shard_size
                )

    achieved = Counter()
    family_split: dict[str, str] = {}
    relation_split: dict[str, str] = {}
    family_variant_count = Counter()
    sample_ids: set[str] = set()
    stats: dict[str, Counter] = {
        "operation": Counter(),
        "difficulty": Counter(),
        "task_type": Counter(),
        "prompt_style": Counter(),
        "split": Counter(),
    }
    max_variants = int(config.get("max_variants_per_family", 18))
    candidate_index = 0
    rejected = Counter()

    def emit(split: str, local: dict[str, Any] | None = None) -> bool:
        nonlocal candidate_index
        settings = local or config
        rng = seeded_rng(seed, sampling_fingerprint, split if local else "iid", candidate_index)
        candidate_index += 1
        operation = weighted_choice(rng, settings.get("operations", config["operations"]))
        level_text = weighted_choice(rng, settings.get("difficulty_weights", config["difficulty_weights"]))
        level = int(level_text)
        try:
            problem = generate_problem(operation, level, rng, config["number_policy"])
            verify_trace(problem)
        except (ArithmeticError, RuntimeError, ValueError):
            rejected["invalid_problem"] += 1
            return False

        family_id = problem.family_id
        relation_ids = problem.relation_ids
        existing_splits = {relation_split[relation_id] for relation_id in relation_ids if relation_id in relation_split}
        if family_id in family_split:
            existing_splits.add(family_split[family_id])
        if len(existing_splits) > 1:
            rejected["relation_component_conflict"] += 1
            return False
        if local is None:
            assigned = next(iter(existing_splits)) if existing_splits else split_for_family(family_id, seed, base_counts)
            accepted_assignment = family_split.get(family_id)
            if accepted_assignment is not None and accepted_assignment != assigned:
                raise RuntimeError("non-deterministic family split assignment")
            split = assigned
        else:
            if existing_splits and existing_splits != {split}:
                rejected["relation_overlap"] += 1
                return False

        if achieved[split] >= all_targets[split]:
            rejected["split_full"] += 1
            return False
        if family_variant_count[family_id] >= max_variants:
            rejected["family_variant_limit"] += 1
            return False

        task = make_task(
            problem,
            rng,
            settings.get("task_types", config["task_types"]),
            settings.get("prompt_styles", config["prompt_styles"]),
        )
        sample_key = canonical_json(
            {
                "family_id": family_id,
                "task_type": task.task_type,
                "prompt": task.prompt,
                "target": task.target,
                "proposed": task.proposed_answer,
            }
        )
        sample_id = stable_hash(sample_key)
        if sample_id in sample_ids:
            rejected["duplicate_sample"] += 1
            return False

        canonical = _problem_record(problem, task, sample_id, split, candidate_index - 1, seed)
        canonical_writers[split].write(canonical)
        for regime in config["regimes"]:
            response_rng = seeded_rng(seed, sample_id, regime["name"])
            response_mode = choose_response_mode(regime, response_rng)
            completion = render_response(problem, task, response_mode)
            regime_writers[(regime["name"], split)].write(
                _sft_record(
                    canonical,
                    regime["name"],
                    response_mode,
                    completion,
                    bool(config["include_system_message"]),
                    str(config["system_prompt"]),
                )
            )

        sample_ids.add(sample_id)
        family_split[family_id] = split
        for relation_id in relation_ids:
            relation_split[relation_id] = split
        family_variant_count[family_id] += 1
        achieved[split] += 1
        stats["operation"][problem.operation_family] += 1
        stats["difficulty"][str(problem.difficulty["level"])] += 1
        stats["task_type"][task.task_type] += 1
        stats["prompt_style"][task.prompt_style] += 1
        stats["split"][split] += 1
        return True

    try:
        base_total = sum(base_counts.values())
        max_attempts = max(100000, base_total * 500)
        attempts = 0
        while any(achieved[name] < count for name, count in base_counts.items()):
            if attempts >= max_attempts:
                missing = {name: count - achieved[name] for name, count in base_counts.items() if achieved[name] < count}
                raise RuntimeError(f"could not fill IID quotas after {attempts} attempts: {missing}")
            emit("train")
            attempts += 1

        for name, holdout in holdout_by_name.items():
            attempts = 0
            max_attempts = max(50000, int(holdout["count"]) * 500)
            while achieved[name] < int(holdout["count"]):
                if attempts >= max_attempts:
                    raise RuntimeError(
                        f"could not fill holdout {name} after {attempts} attempts; "
                        f"missing {int(holdout['count']) - achieved[name]}"
                    )
                emit(name, holdout)
                attempts += 1
    finally:
        for writer in canonical_writers.values():
            writer.close()
        for writer in regime_writers.values():
            writer.close()

    resolved_path = output_path / "resolved_config.json"
    with resolved_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    data_files = sorted(
        path for path in output_path.rglob("*") if path.is_file() and path.name != "manifest.json"
    )
    file_entries = [
        {
            "path": path.relative_to(output_path).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in data_files
    ]
    manifest = {
        "schema_version": "1.0",
        "generator": {"name": "arithmetic-space-lab", "version": __version__},
        "dataset_name": config["dataset_name"],
        "seed": seed,
        "configuration_sha256": fingerprint,
        "sampling_configuration_sha256": sampling_fingerprint,
        "requested_counts": all_targets,
        "actual_counts": dict(sorted(achieved.items())),
        "unique_samples": len(sample_ids),
        "unique_families": len(family_split),
        "unique_atomic_relations": len(relation_split),
        "statistics": {name: dict(sorted(counter.items())) for name, counter in stats.items()},
        "rejections": dict(sorted(rejected.items())),
        "candidate_count": candidate_index,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "records_per_second": round(len(sample_ids) / max(time.perf_counter() - started, 1e-9), 2),
        "files": file_entries,
    }
    manifest_path = output_path / "manifest.json"
    with manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(
            manifest,
            handle,
            ensure_ascii=False,
            indent=int(config["output"].get("indent_manifest", 2)),
            sort_keys=True,
        )
        handle.write("\n")
    return manifest
