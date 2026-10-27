from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

from .protocol import PilotTask

_ENTITY = re.compile(r"\b(?:Fae|Max|Polly|Rex|Sally|Sam|Stella)\b")
_PRED = re.compile(r"\b[a-z]+puses?\b", re.IGNORECASE)


def load_prontoqa(path: str | Path) -> list[PilotTask]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    tasks: list[PilotTask] = []
    for i, row in enumerate(raw):
        steps = tuple(str(s) for s in row.get("steps", []))
        signature = proof_signature(steps)
        tasks.append(
            PilotTask(
                task_id=f"prontoqa-{i:05d}",
                question=str(row["question"]),
                answer=str(row["answer"]),
                proof_steps=steps,
                proof_family=signature,
                metadata={"proof_depth": len(steps)},
            )
        )
    return tasks


def proof_signature(steps: Iterable[str]) -> str:
    """Surface-invariant shape digest; gold steps are audit-only metadata."""
    normalized: list[str] = []
    pred_map: dict[str, str] = {}
    for step in steps:
        s = _ENTITY.sub("ENTITY", step.lower())
        for token in _PRED.findall(s):
            key = token.lower()
            pred_map.setdefault(key, f"P{len(pred_map)}")
            s = re.sub(rf"\b{re.escape(token)}\b", pred_map[key], s, flags=re.IGNORECASE)
        normalized.append(s)
    return hashlib.sha256("\n".join(normalized).encode()).hexdigest()[:16]


def semantic_twin(task: PilotTask, seed: int) -> PilotTask:
    """Consistent entity and nonce-predicate renaming; proof semantics are unchanged."""
    names = ["Ari", "Bea", "Cato", "Dara", "Eli", "Fara", "Galen"]
    replacement_name = names[seed % len(names)]
    predicates = sorted(set(t.lower() for t in _PRED.findall(task.question)))
    mapping = {p: f"twin{seed % 997}_{i}pus" for i, p in enumerate(predicates)}

    def transform(text: str) -> str:
        out = _ENTITY.sub(replacement_name, text)
        for old, new in mapping.items():
            out = re.sub(rf"\b{re.escape(old)}\b", new, out, flags=re.IGNORECASE)
        return out

    return PilotTask(
        task_id=f"{task.task_id}-twin-{seed}",
        question=transform(task.question),
        answer=task.answer,
        proof_steps=tuple(transform(s) for s in task.proof_steps),
        proof_family=task.proof_family,
        metadata={**task.metadata, "semantic_twin_of": task.task_id},
    )


def donor_pairs(tasks: list[PilotTask]) -> dict[str, str]:
    """Choose same-answer, same-depth donors with different proof families."""
    by_key: dict[tuple[str, int], list[PilotTask]] = {}
    for t in tasks:
        by_key.setdefault((t.answer, int(t.metadata.get("proof_depth", len(t.proof_steps)))), []).append(t)
    out: dict[str, str] = {}
    for group in by_key.values():
        ordered = sorted(group, key=lambda x: x.task_id)
        for i, t in enumerate(ordered):
            candidates = [u for u in ordered if u.task_id != t.task_id and u.proof_family != t.proof_family]
            if candidates:
                # Deterministic far donor by lexical proof-set distance.
                a = set(" ".join(t.proof_steps).lower().split())
                candidates.sort(key=lambda u: (len(a & set(" ".join(u.proof_steps).lower().split())), u.task_id))
                out[t.task_id] = candidates[0].task_id
    return out
