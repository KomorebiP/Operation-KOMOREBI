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


def distractor_twin(record: TaskRecord, twin_index: int = 0) -> TaskRecord:
    """Add a new-entity fact that cannot affect the queried entity's proof.

    This is a second semantic-preserving orbit action. The inserted entity and
    predicate are intentionally outside the ordinary PrOntoQA vocabulary used by
    the record, and the protected proof object is unchanged.
    """
    match = _QUERY_MARKER_RE.search(record.question)
    if not match:
        raise ValueError("Cannot locate PrOntoQA query marker")
    context = record.question[: match.start()].strip()
    query = record.question[match.start():].strip()
    tag = hashlib.sha256(f"{record.task_id}:distractor:{twin_index}".encode("utf-8")).hexdigest()[:8]
    distractor = f"Quorin{tag} is ultramarine{tag}."
    metadata = dict(record.metadata)
    metadata.update({"semantic_twin_of": record.task_id, "twin_index": twin_index, "twin_type": "distractor"})
    return replace(
        record,
        task_id=f"{record.task_id}::distractor{twin_index}",
        question=" ".join([context, distractor, query]),
        metadata=metadata,
    )


def query_polarity_counterfactual(record: TaskRecord, intervention_index: int = 0) -> TaskRecord:
    """Flip only the polarity of the final PrOntoQA query and its protected answer.

    The proof chain remains valid evidence: when the original query is true, the
    negated query is false, and conversely. The operation is held out from semantic
    naming and is exposed to the constructor only through an anonymous intervention
    identifier.
    """
    match = _QUERY_MARKER_RE.search(record.question)
    if not match:
        raise ValueError("Cannot locate PrOntoQA query marker")
    context = record.question[: match.end()]
    query = record.question[match.end():].strip()
    terminal = ""
    if query.endswith("?") or query.endswith("."):
        terminal, query = query[-1], query[:-1].rstrip()
    # Typical form: "Stella is floral" or "Stella is not floral".
    not_pattern = re.compile(r"\bis\s+not\s+", re.IGNORECASE)
    is_pattern = re.compile(r"\bis\s+", re.IGNORECASE)
    if not_pattern.search(query):
        flipped = not_pattern.sub("is ", query, count=1)
    elif is_pattern.search(query):
        flipped = is_pattern.sub("is not ", query, count=1)
    else:
        raise ValueError(f"Unsupported PrOntoQA query form: {query!r}")
    answer_norm = record.answer.strip().lower()
    if answer_norm == "true":
        answer = "False"
    elif answer_norm == "false":
        answer = "True"
    else:
        raise ValueError("Polarity counterfactual requires a True/False answer")
    metadata = dict(record.metadata)
    metadata.update(
        {
            "counterfactual_of": record.task_id,
            "anonymous_intervention_id": f"u{intervention_index}",
            "intervention_type_audit_only": "query_polarity_flip",
        }
    )
    return replace(
        record,
        task_id=f"{record.task_id}::u{intervention_index}",
        question=f"{context}{flipped}{terminal}",
        answer=answer,
        orbit_id=f"{record.orbit_id}::counterfactual",
        metadata=metadata,
    )


def validate_polarity_counterfactual(original: TaskRecord, counterfactual: TaskRecord) -> None:
    if original.answer.strip().lower() == counterfactual.answer.strip().lower():
        raise ValueError("Polarity counterfactual did not flip the answer")
    if original.steps != counterfactual.steps or original.proof_signature != counterfactual.proof_signature:
        raise ValueError("Polarity counterfactual changed the proof evidence")
    if original.question == counterfactual.question:
        raise ValueError("Polarity counterfactual did not change the query")


def deterministic_group_split(
    records: Sequence[TaskRecord],
    *,
    seed: int,
    discovery_fraction: float,
    calibration_fraction: float,
) -> dict[str, list[TaskRecord]]:
    """Split by group_id so semantic twins and related rows cannot cross splits."""
    if not 0.0 < discovery_fraction < 1.0:
        raise ValueError("discovery_fraction must lie in (0, 1)")
    if not 0.0 < calibration_fraction < 1.0:
        raise ValueError("calibration_fraction must lie in (0, 1)")
    if discovery_fraction + calibration_fraction >= 1.0:
        raise ValueError("fractions must leave a final split")
    groups: dict[str, list[TaskRecord]] = {}
    for record in records:
        groups.setdefault(record.group_id, []).append(record)
    ranked = sorted(
        groups,
        key=lambda group: hashlib.sha256(f"{seed}:semantic-split:{group}".encode("utf-8")).hexdigest(),
    )
    n_groups = len(ranked)
    if n_groups < 3:
        raise ValueError("At least three groups are required for semantic splitting")
    n_discovery = max(1, int(round(n_groups * discovery_fraction)))
    n_calibration = max(1, int(round(n_groups * calibration_fraction)))
    if n_discovery + n_calibration >= n_groups:
        n_calibration = max(1, n_groups - n_discovery - 1)
    partitions = {
        "discovery": set(ranked[:n_discovery]),
        "calibration": set(ranked[n_discovery : n_discovery + n_calibration]),
        "final": set(ranked[n_discovery + n_calibration :]),
    }
    return {
        name: [record for record in records if record.group_id in group_ids]
        for name, group_ids in partitions.items()
    }


def deterministic_calibration_audit_split(
    records: Sequence[TaskRecord],
    *,
    seed: int,
    calibration_fraction: float,
) -> dict[str, list[TaskRecord]]:
    """Make a deterministic group-disjoint calibration/audit split.

    The calibration side is used only for nuisance-distribution quantities such
    as covariance-matched noise. Donor selection and causal effect estimation use
    only the audit side.
    """
    if not 0.0 < calibration_fraction < 0.5:
        raise ValueError("calibration_fraction must lie in (0, 0.5)")
    groups: dict[str, list[TaskRecord]] = {}
    for record in records:
        groups.setdefault(record.group_id, []).append(record)
    if len(groups) < 2:
        raise ValueError("At least two groups are required for calibration/audit splitting")
    ranked = sorted(
        groups,
        key=lambda group: hashlib.sha256(f"{seed}:causal-calibration:{group}".encode("utf-8")).hexdigest(),
    )
    n_calibration = max(1, int(round(len(ranked) * calibration_fraction)))
    n_calibration = min(n_calibration, len(ranked) - 1)
    calibration_groups = set(ranked[:n_calibration])
    return {
        "calibration": [record for record in records if record.group_id in calibration_groups],
        "audit": [record for record in records if record.group_id not in calibration_groups],
    }
