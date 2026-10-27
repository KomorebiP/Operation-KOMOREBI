from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .byte_tokenizer import ByteTokenizer
from .core import stable_hash
from .generate import canonical_json


@dataclass(frozen=True)
class TrainingExample:
    pair_id: str
    prompt: str
    completion: str
    answer: str
    operation: str
    difficulty: int
    task_type: str

    @property
    def answer_schema(self) -> str:
        if self.answer.lower() in {"true", "false"}:
            return "boolean"
        if "remainder" in self.answer:
            return "quotient_remainder"
        if "/" in self.answer:
            return "fraction"
        return "integer"

    @property
    def sign_class(self) -> str:
        return "negative" if self.answer.startswith("-") else "nonnegative"


def _jsonl_records(paths: Iterable[Path]) -> Iterable[dict[str, Any]]:
    for path in sorted(paths):
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError(f"record is not an object at {path}:{line_number}")
                yield record


def load_sft_examples(data_root: str | Path, regime: str, split: str) -> list[TrainingExample]:
    root = Path(data_root).resolve()
    directory = root / f"sft_{regime}"
    paths = sorted(directory.glob(f"{split}-*.jsonl"))
    if not paths:
        raise FileNotFoundError(f"no {split} shards found for regime {regime}: {directory}")
    examples: list[TrainingExample] = []
    seen: set[str] = set()
    for record in _jsonl_records(paths):
        metadata = record.get("metadata", {})
        pair_id = str(record["pair_id"])
        if pair_id in seen:
            raise ValueError(f"duplicate pair_id in {regime}/{split}: {pair_id}")
        seen.add(pair_id)
        if metadata.get("split") != split:
            raise ValueError(f"record split mismatch for {pair_id}")
        messages = record.get("messages", [])
        if not messages or messages[-1].get("content") != record.get("completion"):
            raise ValueError(f"assistant completion mismatch for {pair_id}")
        prompt = str(record["prompt"])
        completion = str(record["completion"])
        if not prompt or not completion:
            raise ValueError(f"blank prompt or completion for {pair_id}")
        examples.append(
            TrainingExample(
                pair_id=pair_id,
                prompt=prompt,
                completion=completion,
                answer=str(record["answer"]),
                operation=str(metadata["operation_family"]),
                difficulty=int(metadata["difficulty"]["level"]),
                task_type=str(metadata["task_type"]),
            )
        )
    return sorted(examples, key=lambda item: item.pair_id)


def examples_fingerprint(examples: list[TrainingExample], regime: str, split: str) -> str:
    payload = {
        "regime": regime,
        "split": split,
        "rows": [
            [item.pair_id, stable_hash(item.prompt), stable_hash(item.completion)]
            for item in examples
        ],
    }
    return stable_hash(canonical_json(payload))


def _bucket_key(item: TrainingExample, tokenizer: ByteTokenizer) -> tuple[Any, ...]:
    return (
        item.operation,
        item.difficulty,
        item.task_type,
        item.answer_schema,
        item.sign_class,
        len(tokenizer.encode(item.completion)),
    )


def deranged_control_plan(
    examples: list[TrainingExample], tokenizer: ByteTokenizer
) -> dict[str, Any]:
    """Create an exact-length, within-stratum target derangement.

    Strata that cannot be deranged without a fixed answer are omitted from both
    the positive and shuffled primary arms and reported explicitly.
    """
    buckets: dict[tuple[Any, ...], list[int]] = defaultdict(list)
    for index, item in enumerate(examples):
        buckets[_bucket_key(item, tokenizer)].append(index)
    assignment: dict[int, str] = {}
    dropped: list[int] = []
    bucket_summaries: list[dict[str, Any]] = []
    for key in sorted(buckets, key=lambda value: tuple(map(str, value))):
        # v0.3 sorted targets lexicographically before rotating them.  Although
        # that was a valid derangement, it preserved numerical neighbourhoods
        # and could leave prefix/magnitude structure in the control.  Group
        # order and row order are now keyed by cryptographic hashes.  The
        # maximum-frequency rotation still gives a constructive multiset
        # derangement, but there is no value-ordering signal in the mapping.
        grouped: dict[str, list[int]] = defaultdict(list)
        for index in buckets[key]:
            grouped[examples[index].completion].append(index)
        group_order = sorted(
            grouped,
            key=lambda completion: stable_hash(
                "random-derangement-v2|group|"
                + canonical_json([list(key), completion])
            ),
        )
        indices = []
        for completion in group_order:
            indices.extend(
                sorted(
                    grouped[completion],
                    key=lambda index: stable_hash(
                        "random-derangement-v2|row|" + examples[index].pair_id
                    ),
                )
            )
        values = [examples[index].completion for index in indices]
        frequencies = Counter(values)
        maximum = max(frequencies.values())
        if len(indices) < 2 or maximum * 2 > len(indices):
            dropped.extend(indices)
            bucket_summaries.append(
                {"key": list(key), "rows": len(indices), "status": "dropped_not_derangeable"}
            )
            continue
        rotated = values[maximum:] + values[:maximum]
        if any(examples[index].completion == target for index, target in zip(indices, rotated)):
            raise AssertionError("multiset derangement construction produced a fixed answer")
        for index, target in zip(indices, rotated):
            if len(tokenizer.encode(target)) != len(tokenizer.encode(examples[index].completion)):
                raise AssertionError("control target length changed")
            assignment[index] = target
        bucket_summaries.append(
            {
                "key": list(key),
                "rows": len(indices),
                "status": "deranged",
                "algorithm": "hash_randomized_group_rotation_v2",
            }
        )
    active = sorted(assignment)
    if not active:
        raise ValueError("no training examples remain after matched-control construction")
    source_multiset = Counter(examples[index].completion for index in active)
    target_multiset = Counter(assignment[index] for index in active)
    if source_multiset != target_multiset:
        raise AssertionError("control target multiset changed")
    return {
        "schema_version": "2.0",
        "active_indices": active,
        "dropped_indices": sorted(dropped),
        "assignment": {examples[index].pair_id: assignment[index] for index in active},
        "bucket_summaries": bucket_summaries,
        "active_rows": len(active),
        "dropped_rows": len(dropped),
    }


def apply_control_plan(
    examples: list[TrainingExample], plan: dict[str, Any], shuffled: bool
) -> list[TrainingExample]:
    active = [int(index) for index in plan["active_indices"]]
    assignment = plan["assignment"]
    selected: list[TrainingExample] = []
    for index in active:
        item = examples[index]
        completion = str(assignment[item.pair_id]) if shuffled else item.completion
        selected.append(replace(item, completion=completion))
    return selected
