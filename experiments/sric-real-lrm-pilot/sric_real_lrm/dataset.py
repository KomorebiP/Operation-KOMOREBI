from __future__ import annotations

import hashlib
import json
import random
import re
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Sequence

from .hashing import sha256_file, sha256_object
from .schemas import TaskRecord


_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "being", "been", "all", "every",
    "some", "if", "then", "and", "or", "not", "true", "false", "does", "do", "of", "to",
    "in", "on", "for", "that", "this", "it", "so", "because", "therefore", "from", "with",
}
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
_QUERY_MARKER_RE = re.compile(r"\bTrue or false:\s*", re.IGNORECASE)


def normalized_step_tokens(text: str) -> tuple[str, ...]:
    words = [w.lower() for w in _WORD_RE.findall(text)]
    return tuple(w for w in words if w not in _STOPWORDS and len(w) > 1)


def proof_signature_from_steps(steps: Sequence[str]) -> tuple[str, ...]:
    signature: list[str] = []
    for index, step in enumerate(steps):
        tokens = normalized_step_tokens(step)
        token_counts = Counter(tokens)
        compressed = ",".join(f"{token}:{token_counts[token]}" for token in sorted(token_counts))
        signature.append(f"s{index}:{compressed}")
    return tuple(signature)


def signature_token_set(record: TaskRecord) -> set[str]:
    out: set[str] = set()
    for item in record.proof_signature:
        out.update(normalized_step_tokens(item))
    return out


def jaccard_distance(a: set[str], b: set[str]) -> float:
    union = a | b
    if not union:
        return 0.0
    return 1.0 - len(a & b) / len(union)


def load_prontoqa_json(path: str | Path, max_tasks: int | None = None) -> list[TaskRecord]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if max_tasks is not None:
        rows = rows[:max_tasks]
    records: list[TaskRecord] = []
    for index, row in enumerate(rows):
        steps = tuple(str(x) for x in row.get("steps", []))
        metadata = dict(row.get("metadata", {}))
        metadata.setdefault("source_index", index)
        record = TaskRecord(
            task_id=str(row.get("task_id", row.get("idx", index))),
            question=str(row["question"]),
            answer=str(row["answer"]),
            steps=steps,
            proof_depth=int(row.get("proof_depth", len(steps))),
            proof_signature=tuple(row.get("proof_signature", proof_signature_from_steps(steps))),
            orbit_id=str(row.get("orbit_id", f"prontoqa:{index}")),
            group_id=str(row.get("group_id", row.get("orbit_id", f"prontoqa:{index}"))),
            metadata=metadata,
        )
        records.append(record)
    return records


def dataset_fingerprint(path: str | Path, records: Sequence[TaskRecord]) -> dict[str, object]:
    return {
        "path_basename": Path(path).name,
        "sha256": sha256_file(path),
        "task_count": len(records),
        "task_ids_digest": sha256_object([r.task_id for r in records]),
        "group_ids_digest": sha256_object([r.group_id for r in records]),
    }


def deterministic_permutation(items: Sequence[str], key: str) -> list[str]:
    output = list(items)
    seed = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:16], 16)
    random.Random(seed).shuffle(output)
    if len(output) > 1 and output == list(items):
        output = output[1:] + output[:1]
    return output


def semantic_twin(record: TaskRecord, twin_index: int = 0) -> TaskRecord:
    """Create a conservative surface twin by reordering context sentences.

    The transformation does not alter the proof steps, answer, proof signature, or orbit identity.
    It is appropriate only when premise order is semantically irrelevant, as in PrOntoQA.
    """
    match = _QUERY_MARKER_RE.search(record.question)
    if match:
        context = record.question[: match.start()].strip()
        query = record.question[match.start():].strip()
    else:
        context = record.question.strip()
        query = ""
    sentences = [s.strip() for s in _SENTENCE_RE.split(context) if s.strip()]
    shuffled = deterministic_permutation(sentences, f"{record.task_id}:twin:{twin_index}")
    twin_question = " ".join(shuffled + ([query] if query else []))
    metadata = dict(record.metadata)
    metadata.update({"semantic_twin_of": record.task_id, "twin_index": twin_index})
    return replace(
        record,
        task_id=f"{record.task_id}::twin{twin_index}",
        question=twin_question,
        metadata=metadata,
    )


def validate_semantic_twin(original: TaskRecord, twin: TaskRecord) -> None:
    fields = ("answer", "steps", "proof_depth", "proof_signature", "orbit_id", "group_id")
    for field in fields:
        if getattr(original, field) != getattr(twin, field):
            raise ValueError(f"Semantic twin changed protected field: {field}")
    if original.question == twin.question and len(_SENTENCE_RE.split(original.question)) > 1:
        raise ValueError("Semantic twin did not alter the surface form")


def save_records(path: str | Path, records: Iterable[TaskRecord]) -> None:
    Path(path).write_text(
        json.dumps([r.to_mapping() for r in records], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def deterministic_subset(records: Sequence[TaskRecord], max_tasks: int | None, seed: int) -> list[TaskRecord]:
    if max_tasks is None or max_tasks >= len(records):
        return list(records)
    ranked = sorted(
        records,
        key=lambda record: hashlib.sha256(f"{seed}:{record.task_id}".encode("utf-8")).hexdigest(),
    )
    return ranked[:max_tasks]
