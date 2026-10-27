from __future__ import annotations

import hashlib
import numpy as np

from .schemas import TaskRecord


def _stable_angle(text: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}:{text}".encode("utf-8")).digest()
    integer = int.from_bytes(digest[:8], "big")
    return 2.0 * np.pi * integer / float(2**64 - 1)


def protected_proof_witness(
    task: TaskRecord,
    step: int,
    num_latents: int,
    *,
    seed: int = 2301,
) -> np.ndarray:
    """Audit-only compact formal-proof witness.

    This vector is not exposed to quotient construction. It deliberately avoids a
    natural-language semantic name for each coordinate while preserving answer,
    proof-family, and recurrent-progress distinctions. For a real PrOntoQA run,
    richer proof-graph witnesses may be added as post-seal analyses without changing
    the primary construction gates.
    """
    answer = 1.0 if task.answer.strip().lower() in {"true", "yes", "1"} else -1.0
    signature = "|".join(task.proof_signature)
    angle = _stable_angle(f"procedure:{signature}", seed)
    progress = (step + 1.0) / max(1.0, float(num_latents))
    return np.asarray([answer, np.cos(angle), np.sin(angle), progress], dtype=np.float64)


def proof_witness_matrix(
    records: list[TaskRecord],
    *,
    num_latents: int,
    include_last: bool = False,
    seed: int = 2301,
) -> np.ndarray:
    rows: list[np.ndarray] = []
    steps = num_latents if include_last else max(1, num_latents - 1)
    for record in records:
        for step in range(steps):
            rows.append(protected_proof_witness(record, step, num_latents, seed=seed))
    return np.stack(rows) if rows else np.empty((0, 4), dtype=np.float64)
